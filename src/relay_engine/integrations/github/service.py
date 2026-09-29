"""Application services for secure GitHub installation synchronization and webhooks."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import SecretStr

from relay_engine.domain.ids import ProjectId, RepositoryId
from relay_engine.domain.references import RepositoryRef
from relay_engine.integrations.github.auth import create_app_jwt
from relay_engine.integrations.github.client import GitHubClient
from relay_engine.integrations.github.errors import (
    GitHubInstallationUnavailable,
    GitHubIntegrationError,
    GitHubPermissionError,
    GitHubRepositoryAccessDenied,
)
from relay_engine.integrations.github.models import (
    GitHubAccessReadiness,
    GitHubAppConfig,
    GitHubInstallationEvent,
    GitHubInstallationEventType,
    GitHubInstallationSnapshot,
    GitHubInstallationState,
    GitHubInstallationStatus,
    GitHubInstallationToken,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRepositoryAccessSelection,
    GitHubRepositorySnapshot,
    GitHubWebhookEnvelope,
    repository_ref_from_github,
)
from relay_engine.integrations.github.store import GitHubIntegrationStore
from relay_engine.integrations.github.webhooks import (
    parse_supported_webhook,
    webhook_delivery_digest,
)

_READ_PERMISSIONS = {
    "contents": GitHubPermissionLevel.READ,
    "metadata": GitHubPermissionLevel.READ,
}
_WRITE_PERMISSIONS = {
    "contents": GitHubPermissionLevel.WRITE,
    "metadata": GitHubPermissionLevel.READ,
}


def permission_policy_allows(permissions: tuple[GitHubPermissionGrant, ...]) -> bool:
    """Allow exactly one of the accepted READ or WRITE installation profiles."""

    observed = {item.name: item.level for item in permissions}
    return observed in (_READ_PERMISSIONS, _WRITE_PERMISSIONS)


def permission_profile(
    permissions: tuple[GitHubPermissionGrant, ...],
) -> Literal["READ", "WRITE"] | None:
    observed = {item.name: item.level for item in permissions}
    if observed == _READ_PERMISSIONS:
        return "READ"
    if observed == _WRITE_PERMISSIONS:
        return "WRITE"
    return None


def _snapshot_with(
    snapshot: GitHubInstallationSnapshot,
    *,
    observed_at: datetime,
    status: GitHubInstallationStatus | None = None,
    permissions: tuple[GitHubPermissionGrant, ...] | None = None,
) -> GitHubInstallationSnapshot:
    return GitHubInstallationSnapshot(
        project_id=snapshot.project_id,
        installation_id=snapshot.installation_id,
        app_id=snapshot.app_id,
        account_id=snapshot.account_id,
        account_login=snapshot.account_login,
        account_type=snapshot.account_type,
        repository_selection=snapshot.repository_selection,
        status=snapshot.status if status is None else status,
        permissions=snapshot.permissions if permissions is None else permissions,
        observed_at=observed_at,
    )


def _event(
    *,
    event_id: str,
    state: GitHubInstallationState,
    prior_revision: int,
    event_type: GitHubInstallationEventType,
    observed_at: datetime,
    delivery_id: str | None = None,
    delivery_digest: str | None = None,
) -> GitHubInstallationEvent:
    return GitHubInstallationEvent(
        event_id=event_id,
        project_id=state.project_id,
        installation_id=state.installation_id,
        event_type=event_type,
        observed_at=observed_at,
        prior_state_revision=prior_revision,
        resulting_state_revision=state.state_revision,
        delivery_id=delivery_id,
        delivery_digest=delivery_digest,
    )


class GitHubIntegrationService:
    def __init__(
        self,
        *,
        config: GitHubAppConfig,
        private_key_pem: SecretStr,
        webhook_secret: SecretStr,
        client: GitHubClient,
        store: GitHubIntegrationStore,
    ) -> None:
        self._config = config
        self._private_key_pem = private_key_pem
        self._webhook_secret = webhook_secret
        self._client = client
        self._store = store

    def synchronize_installation(
        self,
        *,
        project_id: ProjectId,
        installation_id: int,
        observed_at: datetime,
        event_id: str,
    ) -> GitHubInstallationState:
        """Synchronize a complete installation snapshot with optimistic concurrency."""

        prior = self._store.load_state(project_id, installation_id)
        expected_revision = None if prior is None else prior.state_revision
        app_jwt = create_app_jwt(
            config=self._config,
            private_key_pem=self._private_key_pem,
            now=observed_at,
        )
        try:
            snapshot = self._client.get_installation(
                project_id=project_id,
                installation_id=installation_id,
                app_jwt=app_jwt,
                observed_at=observed_at,
            )
        except GitHubInstallationUnavailable:
            if prior is not None:
                deleted_snapshot = _snapshot_with(
                    prior.installation,
                    observed_at=observed_at,
                    status=GitHubInstallationStatus.DELETED,
                )
                state = GitHubInstallationState(
                    installation=deleted_snapshot,
                    readiness=GitHubAccessReadiness.RESYNC_REQUIRED,
                    state_revision=prior.state_revision + 1,
                )
                self._store.apply_mutation(
                    expected_revision=prior.state_revision,
                    state=state,
                    repositories=(),
                    event=_event(
                        event_id=event_id,
                        state=state,
                        prior_revision=prior.state_revision,
                        event_type=GitHubInstallationEventType.DELETED,
                        observed_at=observed_at,
                    ),
                )
            raise

        next_revision = 1 if expected_revision is None else expected_revision + 1
        prior_revision = 0 if expected_revision is None else expected_revision

        if not permission_policy_allows(snapshot.permissions):
            state = GitHubInstallationState(
                installation=snapshot,
                readiness=GitHubAccessReadiness.PERMISSION_POLICY_VIOLATION,
                state_revision=next_revision,
            )
            self._store.apply_mutation(
                expected_revision=expected_revision,
                state=state,
                repositories=None,
                event=_event(
                    event_id=event_id,
                    state=state,
                    prior_revision=prior_revision,
                    event_type=GitHubInstallationEventType.PERMISSIONS_CHANGED,
                    observed_at=observed_at,
                ),
            )
            raise GitHubPermissionError(
                "GitHub installation violates the Slice 1.1 permission policy"
            )

        if snapshot.status is GitHubInstallationStatus.SUSPENDED:
            state = GitHubInstallationState(
                installation=snapshot,
                readiness=GitHubAccessReadiness.RESYNC_REQUIRED,
                state_revision=next_revision,
            )
            self._store.apply_mutation(
                expected_revision=expected_revision,
                state=state,
                repositories=None,
                event=_event(
                    event_id=event_id,
                    state=state,
                    prior_revision=prior_revision,
                    event_type=GitHubInstallationEventType.SUSPENDED,
                    observed_at=observed_at,
                ),
            )
            return state

        token = self._client.create_installation_token(
            installation_id=installation_id,
            app_jwt=app_jwt,
        )
        if token.expires_at <= observed_at:
            raise GitHubPermissionError("GitHub returned an already-expired installation token")
        repositories = self._client.list_installation_repositories(
            token=token,
            observed_at=observed_at,
        )
        state = GitHubInstallationState(
            installation=snapshot,
            readiness=GitHubAccessReadiness.READY,
            state_revision=next_revision,
        )
        self._store.apply_mutation(
            expected_revision=expected_revision,
            state=state,
            repositories=repositories,
            event=_event(
                event_id=event_id,
                state=state,
                prior_revision=prior_revision,
                event_type=GitHubInstallationEventType.INSTALLATION_SYNCED,
                observed_at=observed_at,
            ),
        )
        return state

    def repository_ref_for_selected(
        self,
        *,
        project_id: ProjectId,
        installation_id: int,
        github_repository_id: int,
        relay_repository_id: RepositoryId,
    ) -> RepositoryRef:
        state = self._store.load_state(project_id, installation_id)
        if state is None:
            raise GitHubRepositoryAccessDenied("GitHub installation is not bound to this project")
        repositories = self._store.list_repositories(project_id, installation_id)
        repository = next(
            (item for item in repositories if item.github_repository_id == github_repository_id),
            None,
        )
        if repository is None:
            raise GitHubRepositoryAccessDenied(
                "GitHub repository is not in the confirmed access set"
            )
        try:
            return repository_ref_from_github(
                relay_repository_id=relay_repository_id,
                state=state,
                repository=repository,
                current_repositories=repositories,
            )
        except ValueError as error:
            raise GitHubRepositoryAccessDenied(
                "GitHub repository is not currently usable"
            ) from error

    def repository_access_selection(
        self,
        *,
        project_id: ProjectId,
        installation_id: int,
        github_repository_id: int,
        repository: RepositoryRef,
    ) -> GitHubRepositoryAccessSelection:
        """Capture one immutable ACTIVE/READY binding matching durable Project authority."""

        project_repository = self._store.load_project_repository(project_id)
        if project_repository is None:
            raise GitHubRepositoryAccessDenied("Relay project does not exist")
        if project_repository != repository:
            raise GitHubRepositoryAccessDenied(
                "GitHub repository does not match durable Project.primary_repository"
            )
        state = self._store.load_state(project_id, installation_id)
        if state is None or not state.usable:
            raise GitHubRepositoryAccessDenied("GitHub installation is not ACTIVE / READY")
        repositories = self._store.list_repositories(project_id, installation_id)
        selected = next(
            (item for item in repositories if item.github_repository_id == github_repository_id),
            None,
        )
        if selected is None:
            raise GitHubRepositoryAccessDenied(
                "GitHub repository is not in the confirmed access set"
            )
        try:
            resolved = repository_ref_from_github(
                relay_repository_id=repository.id,
                state=state,
                repository=selected,
                current_repositories=repositories,
            )
        except ValueError as error:
            raise GitHubRepositoryAccessDenied(
                "GitHub repository is not currently usable"
            ) from error
        if resolved != repository:
            raise GitHubRepositoryAccessDenied(
                "GitHub repository does not match Relay repository authority"
            )
        return GitHubRepositoryAccessSelection(
            project_id=project_id,
            installation_id=installation_id,
            github_repository_id=github_repository_id,
            github_node_id=selected.node_id,
            repository=repository,
            expected_state_revision=state.state_revision,
        )

    def create_repository_token(
        self,
        *,
        selection: GitHubRepositoryAccessSelection,
        observed_at: datetime,
    ) -> GitHubInstallationToken:
        """Mint one repository-scoped token with contents read, even for WRITE installs."""

        return self._create_repository_token(
            selection=selection,
            observed_at=observed_at,
            contents_permission="read",
        )

    def create_repository_write_token(
        self,
        *,
        selection: GitHubRepositoryAccessSelection,
        observed_at: datetime,
    ) -> GitHubInstallationToken:
        """Mint a separate repository-scoped contents-write token for explicit sync."""

        state = self._store.load_state(selection.project_id, selection.installation_id)
        if state is None or permission_profile(state.installation.permissions) != "WRITE":
            raise GitHubPermissionError("GitHub installation does not have the exact WRITE profile")
        return self._create_repository_token(
            selection=selection,
            observed_at=observed_at,
            contents_permission="write",
        )

    def _create_repository_token(
        self,
        *,
        selection: GitHubRepositoryAccessSelection,
        observed_at: datetime,
        contents_permission: Literal["read", "write"],
    ) -> GitHubInstallationToken:

        app_jwt = create_app_jwt(
            config=self._config,
            private_key_pem=self._private_key_pem,
            now=observed_at,
        )
        token = self._client.create_installation_token(
            installation_id=selection.installation_id,
            app_jwt=app_jwt,
            repository_id=selection.github_repository_id,
            contents_permission=contents_permission,
        )
        if token.expires_at <= observed_at:
            raise GitHubPermissionError("GitHub returned an already-expired installation token")
        return token

    def process_webhook(
        self,
        *,
        headers: Mapping[str, str],
        raw_body: bytes,
        observed_at: datetime,
        event_id_factory: Callable[[ProjectId, GitHubWebhookEnvelope], str],
    ) -> tuple[GitHubWebhookProjectOutcome, ...]:
        envelope = parse_supported_webhook(
            headers=headers,
            raw_body=raw_body,
            webhook_secret=self._webhook_secret,
        )
        digest = webhook_delivery_digest(envelope)
        projects = self._store.project_bindings_for_installation(envelope.installation_id)
        outcomes: list[GitHubWebhookProjectOutcome] = []
        for project_id in projects:
            try:
                applied = self._apply_webhook_to_project(
                    project_id=project_id,
                    envelope=envelope,
                    delivery_digest=digest,
                    observed_at=observed_at,
                    event_id=event_id_factory(project_id, envelope),
                )
                outcomes.append(GitHubWebhookProjectOutcome(project_id, applied, None))
            except GitHubIntegrationError as error:
                outcomes.append(
                    GitHubWebhookProjectOutcome(project_id, False, type(error).__name__)
                )
        return tuple(outcomes)

    def _apply_webhook_to_project(
        self,
        *,
        project_id: ProjectId,
        envelope: GitHubWebhookEnvelope,
        delivery_digest: str,
        observed_at: datetime,
        event_id: str,
    ) -> bool:
        prior = self._store.load_state(project_id, envelope.installation_id)
        if prior is None:
            return False
        repositories = self._store.list_repositories(project_id, envelope.installation_id)
        status = prior.installation.status
        readiness = prior.readiness
        next_repositories: tuple[GitHubRepositorySnapshot, ...] | None = None
        event_type = GitHubInstallationEventType.INSTALLATION_SYNCED
        permissions: tuple[GitHubPermissionGrant, ...] | None = None

        if prior.installation.status is GitHubInstallationStatus.DELETED:
            status = GitHubInstallationStatus.DELETED
            readiness = GitHubAccessReadiness.RESYNC_REQUIRED
            next_repositories = ()
            event_type = GitHubInstallationEventType.DELETED
        elif envelope.event_name == "installation":
            if envelope.action == "suspend":
                status = GitHubInstallationStatus.SUSPENDED
                readiness = GitHubAccessReadiness.RESYNC_REQUIRED
                event_type = GitHubInstallationEventType.SUSPENDED
            elif envelope.action == "unsuspend":
                status = GitHubInstallationStatus.ACTIVE
                readiness = GitHubAccessReadiness.RESYNC_REQUIRED
                event_type = GitHubInstallationEventType.UNSUSPENDED
            elif envelope.action == "deleted":
                status = GitHubInstallationStatus.DELETED
                readiness = GitHubAccessReadiness.RESYNC_REQUIRED
                next_repositories = ()
                event_type = GitHubInstallationEventType.DELETED
            elif envelope.action == "new_permissions_accepted":
                permissions = envelope.permissions
                readiness = (
                    GitHubAccessReadiness.RESYNC_REQUIRED
                    if permission_policy_allows(permissions)
                    else GitHubAccessReadiness.PERMISSION_POLICY_VIOLATION
                )
                event_type = GitHubInstallationEventType.PERMISSIONS_CHANGED
            elif envelope.action == "created":
                status = GitHubInstallationStatus.ACTIVE
                readiness = GitHubAccessReadiness.RESYNC_REQUIRED
                event_type = GitHubInstallationEventType.INSTALLATION_SYNCED
        else:
            event_type = GitHubInstallationEventType.REPOSITORIES_CHANGED
            readiness = GitHubAccessReadiness.RESYNC_REQUIRED
            if envelope.action == "removed":
                removed = set(envelope.repository_ids)
                next_repositories = tuple(
                    item for item in repositories if item.github_repository_id not in removed
                )
            elif envelope.action == "added":
                next_repositories = None

        snapshot = _snapshot_with(
            prior.installation,
            observed_at=observed_at,
            status=status,
            permissions=permissions,
        )
        state = GitHubInstallationState(
            installation=snapshot,
            readiness=readiness,
            state_revision=prior.state_revision + 1,
        )
        result = self._store.apply_mutation(
            expected_revision=prior.state_revision,
            state=state,
            repositories=next_repositories,
            event=_event(
                event_id=event_id,
                state=state,
                prior_revision=prior.state_revision,
                event_type=event_type,
                observed_at=observed_at,
                delivery_id=envelope.delivery_id,
                delivery_digest=delivery_digest,
            ),
        )
        return result.applied


@dataclass(frozen=True, slots=True)
class GitHubWebhookProjectOutcome:
    project_id: ProjectId
    applied: bool
    error_type: str | None
