from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import SecretStr

from relay_engine.domain import ActorKind, ActorRef, Project, RepositoryRef
from relay_engine.integrations.github import (
    GitHubAccessReadiness,
    GitHubAccountType,
    GitHubAppConfig,
    GitHubInstallationEvent,
    GitHubInstallationEventType,
    GitHubInstallationSnapshot,
    GitHubInstallationState,
    GitHubInstallationStatus,
    GitHubIntegrationService,
    GitHubIntegrationStore,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRepositoryAccessDenied,
    GitHubRepositorySelectionMode,
    GitHubRepositorySnapshot,
)
from relay_engine.persistence import open_database
from relay_engine.project_slice import MutationMetadata, create_project

NOW = datetime(2026, 9, 28, 1, 0, tzinfo=UTC)
PROJECT_ID = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="cschrupp/relay",
)


def _create_project(database: object, value: Project) -> None:
    create_project(
        database,
        value,
        MutationMetadata(
            actor=ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN),
            occurred_at=NOW,
            reason="Test setup.",
        ),
    )


class DummyClient:
    pass


def _state(readiness: GitHubAccessReadiness) -> GitHubInstallationState:
    return GitHubInstallationState(
        installation=GitHubInstallationSnapshot(
            project_id=PROJECT_ID,
            installation_id=1001,
            app_id=77,
            account_id=9,
            account_login="relay-test",
            account_type=GitHubAccountType.ORGANIZATION,
            repository_selection=GitHubRepositorySelectionMode.SELECTED,
            status=GitHubInstallationStatus.ACTIVE,
            permissions=(
                GitHubPermissionGrant(name="contents", level=GitHubPermissionLevel.READ),
                GitHubPermissionGrant(name="metadata", level=GitHubPermissionLevel.READ),
            ),
            observed_at=NOW,
        ),
        readiness=readiness,
        state_revision=1,
    )


def _repository() -> GitHubRepositorySnapshot:
    return GitHubRepositorySnapshot(
        github_repository_id=501,
        node_id="R_501",
        full_name=REPOSITORY.path,
        owner_login="cschrupp",
        private=False,
        archived=False,
        default_branch="main",
        observed_at=NOW,
    )


def _seed(readiness: GitHubAccessReadiness):
    database = open_database(":memory:", apply_migrations=True, migration_applied_at=NOW)
    _create_project(
        database,
        Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY),
    )
    store = GitHubIntegrationStore(database)
    state = _state(readiness)
    store.apply_mutation(
        expected_revision=None,
        state=state,
        repositories=(_repository(),),
        event=GitHubInstallationEvent(
            event_id="seed-selection",
            project_id=PROJECT_ID,
            installation_id=1001,
            event_type=GitHubInstallationEventType.INSTALLATION_SYNCED,
            observed_at=NOW,
            prior_state_revision=0,
            resulting_state_revision=1,
        ),
    )
    service = GitHubIntegrationService(
        config=GitHubAppConfig(client_id="Iv1.test"),
        private_key_pem=SecretStr("unused"),
        webhook_secret=SecretStr("unused"),
        client=DummyClient(),
        store=store,
    )
    return database, service


def test_access_selection_captures_exact_provider_binding_and_state_revision() -> None:
    database, service = _seed(GitHubAccessReadiness.READY)
    with database:
        selection = service.repository_access_selection(
            project_id=PROJECT_ID,
            installation_id=1001,
            github_repository_id=501,
            repository=REPOSITORY,
        )
        assert selection.project_id == PROJECT_ID
        assert selection.installation_id == 1001
        assert selection.github_repository_id == 501
        assert selection.github_node_id == "R_501"
        assert selection.repository == REPOSITORY
        assert selection.expected_state_revision == 1


def test_access_selection_rejects_non_ready_binding() -> None:
    database, service = _seed(GitHubAccessReadiness.RESYNC_REQUIRED)
    with database, pytest.raises(GitHubRepositoryAccessDenied, match="ACTIVE / READY"):
        service.repository_access_selection(
            project_id=PROJECT_ID,
            installation_id=1001,
            github_repository_id=501,
            repository=REPOSITORY,
        )


def test_access_selection_requires_durable_project_repository_authority() -> None:
    database, service = _seed(GitHubAccessReadiness.READY)
    different_relay_identity = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789999",
        host="github.com",
        path=REPOSITORY.path,
    )
    with database, pytest.raises(GitHubRepositoryAccessDenied, match="Project.primary_repository"):
        service.repository_access_selection(
            project_id=PROJECT_ID,
            installation_id=1001,
            github_repository_id=501,
            repository=different_relay_identity,
        )
