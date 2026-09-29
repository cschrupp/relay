"""Read-only preparation and one-commit, non-force GitHub repository synchronization."""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime

from relay_engine.domain import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.domain.ids import RepositoryMutationAuthorizationId
from relay_engine.integrations.github import (
    GitHubClient,
    GitHubGitObjectType,
    GitHubIntegrationService,
    GitHubRefNotFound,
    GitHubRefUpdateIndeterminate,
    GitHubRefUpdateRejected,
    GitHubRepositoryAccessSelection,
    GitHubRepositorySnapshot,
    GitHubTree,
    GitHubTreeEntry,
    permission_profile,
)
from relay_engine.integrations.github.models import GitHubInstallationToken
from relay_engine.integrations.github.store import GitHubIntegrationStore
from relay_engine.persistence import (
    PersistenceError,
    RelayDatabase,
    insert_repository_mutation_authorization,
    load_project,
    load_repository_mutation_authorization,
)
from relay_engine.repository_contract import (
    ArtifactIntegrityError,
    RepositoryContractInvalid,
    RepositorySnapshotEntry,
    parse_repository_registry,
    serialize_repository_registry,
    validate_registry_transition,
    validate_repository_snapshot,
)
from relay_engine.repository_contract.models import (
    RepositoryRegistry,
)
from relay_engine.repository_sync.errors import (
    RepositorySyncAccessChanged,
    RepositorySyncAuthorizationRequired,
    RepositorySyncAuthorizationStale,
    RepositorySyncConflict,
    RepositorySyncDefaultBranchChanged,
    RepositorySyncError,
    RepositorySyncInvalidRemote,
    RepositorySyncNoDefaultHead,
    RepositorySyncPostWriteVerificationError,
    RepositorySyncProtectedBranch,
    RepositorySyncProviderIdentityChanged,
    RepositorySyncRefUpdateNotVisible,
    RepositorySyncSnapshotIntegrityError,
    RepositorySyncWorkflowMutationUnsupported,
    RepositorySyncWritePermissionRequired,
)
from relay_engine.repository_sync.models import (
    ArtifactWriteDigest,
    RepositoryArtifactWrite,
    RepositoryContractState,
    RepositoryMutationAuthorization,
    RepositorySyncPreparation,
    RepositorySyncRequest,
    RepositorySyncResult,
    RepositorySyncSubjectV1,
    artifact_write_digest,
    repository_registry_digest,
    repository_sync_subject_digest,
)

_SHA_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_REGULAR_MODES = frozenset({"100644", "100755"})
_REGISTRY_PATH = ".relay/registry.json"
_WORKFLOW_PREFIX = ".github/workflows/"


@dataclass(frozen=True, slots=True)
class _ResolvedPath:
    entry: GitHubTreeEntry
    complete: bool


@dataclass(frozen=True, slots=True)
class _RepositoryFile:
    path: str
    mode: str
    object_type: GitHubGitObjectType
    sha: str
    raw_bytes: bytes


@dataclass(slots=True)
class _TreeWalker:
    client: GitHubClient
    token: GitHubInstallationToken
    repository_path: str
    cache: dict[str, GitHubTree] = field(default_factory=dict[str, GitHubTree])
    blobs: dict[str, bytes] = field(default_factory=dict[str, bytes])

    def tree(self, tree_sha: str) -> GitHubTree:
        existing = self.cache.get(tree_sha)
        if existing is not None:
            return existing
        tree = self.client.get_git_tree(
            token=self.token,
            repository_path=self.repository_path,
            tree_sha=tree_sha,
        )
        if tree.sha != tree_sha or tree.truncated:
            raise RepositorySyncSnapshotIntegrityError(
                "GitHub tree response cannot prove the exact requested tree"
            )
        self.cache[tree_sha] = tree
        return tree

    def resolve(self, root_tree_sha: str, path: str) -> _ResolvedPath | None:
        parts = path.split("/")
        current_sha = root_tree_sha
        for index, part in enumerate(parts):
            tree = self.tree(current_sha)
            entry = next((item for item in tree.entries if item.path == part), None)
            if entry is None:
                return None
            if index == len(parts) - 1:
                return _ResolvedPath(entry, True)
            if entry.object_type is not GitHubGitObjectType.TREE or entry.mode != "040000":
                return _ResolvedPath(entry, False)
            current_sha = entry.sha
        return None

    def file(self, root_tree_sha: str, path: str) -> _RepositoryFile | None:
        resolved = self.resolve(root_tree_sha, path)
        if resolved is None or not resolved.complete:
            return None
        entry = resolved.entry
        if entry.object_type is not GitHubGitObjectType.BLOB:
            return None
        raw = self.blobs.get(entry.sha)
        if raw is None:
            blob = self.client.get_git_blob(
                token=self.token,
                repository_path=self.repository_path,
                blob_sha=entry.sha,
            )
            if blob.sha != entry.sha:
                raise RepositorySyncSnapshotIntegrityError(
                    f"GitHub blob identity changed for {path}"
                )
            raw = blob.raw_bytes
            self.blobs[entry.sha] = raw
        return _RepositoryFile(path, entry.mode, entry.object_type, entry.sha, raw)


@dataclass(frozen=True, slots=True)
class _CurrentSnapshot:
    state: RepositoryContractState
    registry: RepositoryRegistry | None
    files: dict[str, _RepositoryFile]


@dataclass(frozen=True, slots=True)
class _PreparedOperation:
    request: RepositorySyncRequest
    public: RepositorySyncPreparation
    token: GitHubInstallationToken
    provider: GitHubRepositorySnapshot
    base_tree_sha: str
    target_registry_raw: bytes
    resulting_files: dict[str, _RepositoryFile]
    changed_files: dict[str, _RepositoryFile]


class RepositorySyncService:
    """Enforce exact Human Authority, access, provider, and branch-head boundaries."""

    def __init__(
        self,
        *,
        database: RelayDatabase,
        github_integration: GitHubIntegrationService,
        github_client: GitHubClient,
        github_store: GitHubIntegrationStore,
    ) -> None:
        self._database = database
        self._github_integration = github_integration
        self._github_client = github_client
        self._github_store = github_store

    def prepare_repository_sync(
        self,
        request: RepositorySyncRequest,
        *,
        observed_at: datetime,
    ) -> RepositorySyncPreparation:
        """Inspect the exact target using READ capability only; create no Git objects."""

        return self._prepare(request, observed_at=observed_at).public

    def authorize_repository_sync(
        self,
        *,
        authorization_id: RepositoryMutationAuthorizationId,
        preparation: RepositorySyncPreparation,
        actor: ActorRef,
        granted_at: datetime,
        reason: str,
    ) -> RepositoryMutationAuthorization:
        """Persist exactly the prepared subject approved by a HUMAN actor."""

        if (
            preparation.state is not RepositoryContractState.SYNCHRONIZABLE
            or preparation.subject is None
            or preparation.subject_digest is None
        ):
            raise RepositorySyncAuthorizationRequired(
                "only a SYNCHRONIZABLE exact subject can receive mutation authorization"
            )
        if actor.kind is not ActorKind.HUMAN:
            raise RepositorySyncAuthorizationRequired(
                "repository mutation authorization requires a HUMAN actor"
            )
        authorization = RepositoryMutationAuthorization(
            authorization_id=authorization_id,
            project_id=preparation.subject.project_id,
            subject_schema_version=1,
            subject=preparation.subject,
            subject_digest=preparation.subject_digest,
            actor=actor,
            granted_at=granted_at,
            reason=reason,
        )
        try:
            insert_repository_mutation_authorization(self._database, authorization)
        except PersistenceError:
            raise
        return authorization

    def execute_repository_sync(
        self,
        request: RepositorySyncRequest,
        *,
        observed_at: datetime,
    ) -> RepositorySyncResult:
        """Re-prepare, verify exact authority, write one commit, and verify its visibility."""

        operation = self._prepare(request, observed_at=observed_at)
        preparation = operation.public
        if preparation.state is RepositoryContractState.CURRENT:
            return RepositorySyncResult(
                prior_commit=preparation.prior_commit,
                resulting_commit=preparation.prior_commit,
                wrote_remote=False,
            )
        if preparation.state is not RepositoryContractState.SYNCHRONIZABLE:
            raise RepositorySyncConflict("repository target is not synchronizable")

        if preparation.subject is None:
            raise RepositorySyncAuthorizationRequired(
                "synchronizable preparation lost its exact subject"
            )
        authorization = self._require_authorization(request, preparation)
        profile = self._require_local_access(request.selection, require_write=True)
        if profile != "WRITE":
            raise RepositorySyncWritePermissionRequired(
                "repository mutation requires the exact WRITE permission profile"
            )
        write_token = self._github_integration.create_repository_write_token(
            selection=request.selection,
            observed_at=observed_at,
        )

        created_blobs: dict[str, str] = {}
        for path, file in sorted(operation.changed_files.items()):
            blob = self._github_client.create_git_blob(
                token=write_token,
                repository_path=request.selection.repository.path,
                raw_bytes=file.raw_bytes,
            )
            created_blobs[path] = blob.sha

        entries = tuple(
            sorted(
                (
                    GitHubTreeEntry(
                        path=path,
                        mode=file.mode,
                        object_type=GitHubGitObjectType.BLOB,
                        sha=created_blobs[path],
                    )
                    for path, file in operation.changed_files.items()
                ),
                key=lambda item: item.path,
            )
        )
        tree = self._github_client.create_git_tree(
            token=write_token,
            repository_path=request.selection.repository.path,
            base_tree_sha=operation.base_tree_sha,
            entries=entries,
        )
        commit = self._github_client.create_git_commit(
            token=write_token,
            repository_path=request.selection.repository.path,
            message=(
                "Synchronize Relay repository contract "
                f"({preparation.subject.target_registry_digest})"
            ),
            tree_sha=tree.sha,
            parent_sha=preparation.prior_commit.sha,
        )
        if commit.parents != (preparation.prior_commit.sha,):
            raise RepositorySyncSnapshotIntegrityError(
                "GitHub-created commit does not have the exact captured base as its sole parent"
            )

        self._require_authorization(request, preparation, expected=authorization)
        profile = self._require_local_access(request.selection, require_write=True)
        if profile != "WRITE":
            raise RepositorySyncWritePermissionRequired(
                "WRITE profile changed before default-branch visibility"
            )
        provider = self._read_provider(
            operation.token,
            request.selection,
            observed_at,
            expected_default_branch=request.expected_default_branch,
        )
        if provider.default_branch != operation.provider.default_branch:
            raise RepositorySyncDefaultBranchChanged(
                "provider default branch changed during synchronization"
            )
        current_head = self._resolve_default_head(
            operation.token,
            request.selection.repository,
            provider.default_branch,
        )
        if current_head.sha != preparation.prior_commit.sha:
            raise RepositorySyncConflict("default-branch head advanced after preparation")

        visible_commit = commit.sha
        try:
            updated = self._github_client.update_git_ref(
                token=write_token,
                repository_path=request.selection.repository.path,
                branch=provider.default_branch,
                commit_sha=commit.sha,
                force=False,
            )
            if (
                updated.ref != f"refs/heads/{provider.default_branch}"
                or updated.sha != commit.sha
                or updated.object_type is not GitHubGitObjectType.COMMIT
            ):
                raise GitHubRefUpdateIndeterminate(
                    "GitHub ref update response did not prove the requested branch and commit"
                )
        except GitHubRefUpdateRejected as error:
            raise RepositorySyncProtectedBranch(
                "GitHub rejected the non-force default-branch update"
            ) from error
        except GitHubRefUpdateIndeterminate as update_error:
            observed = self._observe_ref_after_ambiguous_update(
                operation=operation,
                created_commit_sha=commit.sha,
                observed_at=observed_at,
            )
            if observed == preparation.prior_commit.sha:
                raise RepositorySyncRefUpdateNotVisible(
                    "ambiguous GitHub ref update left the branch at its captured base",
                    commit.sha,
                ) from update_error
            if observed != commit.sha:
                raise RepositorySyncPostWriteVerificationError(
                    "ambiguous GitHub ref update resolved to another or unobservable head",
                    commit.sha,
                ) from update_error

        self._verify_visible_result(
            operation=operation,
            created_commit_sha=visible_commit,
            observed_at=observed_at,
            expected_parent=preparation.prior_commit.sha,
        )
        return RepositorySyncResult(
            prior_commit=preparation.prior_commit,
            resulting_commit=CommitRef(
                repository=request.selection.repository,
                sha=visible_commit,
            ),
            wrote_remote=True,
        )

    def _prepare(
        self,
        request: RepositorySyncRequest,
        *,
        observed_at: datetime,
    ) -> _PreparedOperation:
        self._require_local_access(request.selection, require_write=False)
        read_token = self._github_integration.create_repository_token(
            selection=request.selection,
            observed_at=observed_at,
        )
        provider = self._read_provider(
            read_token,
            request.selection,
            observed_at,
            expected_default_branch=request.expected_default_branch,
        )
        prior_commit = self._resolve_default_head(
            read_token,
            request.selection.repository,
            provider.default_branch,
        )
        base = self._github_client.get_git_commit(
            token=read_token,
            repository_path=request.selection.repository.path,
            sha=prior_commit.sha,
        )
        if base.sha != prior_commit.sha:
            raise RepositorySyncSnapshotIntegrityError(
                "provider returned a different base commit identity"
            )
        walker = _TreeWalker(
            client=self._github_client,
            token=read_token,
            repository_path=request.selection.repository.path,
        )
        current = self._read_current_snapshot(
            walker=walker,
            root_tree_sha=base.tree_sha,
            selection=request.selection,
        )

        writes = {item.path: item for item in request.artifact_writes}
        target_by_path = {item.path: item for item in request.target_registry.artifacts}
        for path, write in writes.items():
            target_artifact = target_by_path.get(path)
            if target_artifact is None:
                raise RepositorySyncConflict(
                    f"caller write is not represented by the target registry: {path}"
                )
            if artifact_write_digest(write.raw_bytes) != target_artifact.content_digest:
                raise RepositorySyncConflict(
                    f"caller bytes do not match target registry digest: {path}"
                )

        target_registry_raw = serialize_repository_registry(request.target_registry)
        current_registry_file = current.files.get(_REGISTRY_PATH)
        if (
            current.state is RepositoryContractState.CURRENT
            and current.registry == request.target_registry
            and current_registry_file is not None
            and current_registry_file.raw_bytes == target_registry_raw
        ):
            assert current.files
            self._validate_logical_snapshot(
                request.target_registry,
                target_registry_raw,
                {
                    path: item.raw_bytes
                    for path, item in current.files.items()
                    if path != _REGISTRY_PATH
                },
            )
            public = RepositorySyncPreparation(
                state=RepositoryContractState.CURRENT,
                prior_commit=prior_commit,
            )
            return _PreparedOperation(
                request,
                public,
                read_token,
                provider,
                base.tree_sha,
                target_registry_raw,
                current.files,
                {},
            )

        if prior_commit.sha != request.expected_base_commit.sha:
            raise RepositorySyncConflict(
                "default-branch head differs from the exact expected base commit"
            )
        if current.state is RepositoryContractState.INVALID:
            raise RepositorySyncInvalidRemote("existing .relay contract is invalid")
        if current.state is RepositoryContractState.CURRENT:
            assert current.registry is not None
            try:
                validate_registry_transition(current.registry, request.target_registry)
            except RepositoryContractInvalid as error:
                raise RepositorySyncConflict(
                    "target registry is not a valid transition from the current registry"
                ) from error

        plan = self._target_file_plan(
            walker=walker,
            root_tree_sha=base.tree_sha,
            current=current,
            request=request,
            writes=writes,
        )
        target_bytes = {
            path: item.raw_bytes for path, item in plan.items() if path != _REGISTRY_PATH
        }
        self._validate_logical_snapshot(request.target_registry, target_registry_raw, target_bytes)

        changed_files = {
            path: item
            for path, item in plan.items()
            if (
                (base_file := walker.file(base.tree_sha, path)) is None
                or item.raw_bytes != base_file.raw_bytes
                or item.mode != base_file.mode
            )
        }
        changed_paths = tuple(sorted(changed_files))
        if not changed_paths:
            raise RepositorySyncConflict("non-current target produced no repository-tree changes")

        subject = self._subject(request, target_registry_raw)
        subject_digest = repository_sync_subject_digest(subject)
        public = RepositorySyncPreparation(
            state=RepositoryContractState.SYNCHRONIZABLE,
            prior_commit=prior_commit,
            subject=subject,
            subject_digest=subject_digest,
            changed_paths=changed_paths,
        )
        return _PreparedOperation(
            request,
            public,
            read_token,
            provider,
            base.tree_sha,
            target_registry_raw,
            plan,
            changed_files,
        )

    def _target_file_plan(
        self,
        *,
        walker: _TreeWalker,
        root_tree_sha: str,
        current: _CurrentSnapshot,
        request: RepositorySyncRequest,
        writes: dict[str, RepositoryArtifactWrite],
    ) -> dict[str, _RepositoryFile]:
        plan: dict[str, _RepositoryFile] = {}
        current_registered: set[str] = (
            set()
            if current.registry is None
            else {item.path for item in current.registry.artifacts}
        )
        target_artifacts = {item.path: item for item in request.target_registry.artifacts}
        for path, artifact in sorted(target_artifacts.items()):
            existing = current.files.get(path)
            resolved = None if existing is not None else walker.resolve(root_tree_sha, path)
            if existing is None and resolved is not None:
                existing = walker.file(root_tree_sha, path)
                if existing is None:
                    raise RepositorySyncConflict(
                        f"pre-existing unregistered path is not a regular file: {path}"
                    )
            is_registered_now = path in current_registered
            write = writes.get(path)

            if existing is not None and not is_registered_now:
                if (
                    existing.object_type is not GitHubGitObjectType.BLOB
                    or existing.mode not in _REGULAR_MODES
                    or artifact_write_digest(existing.raw_bytes) != artifact.content_digest
                ):
                    raise RepositorySyncConflict(
                        f"pre-existing unregistered path cannot be overwritten or adopted: {path}"
                    )
                resulting = existing
            elif existing is not None and existing.mode not in _REGULAR_MODES:
                raise RepositorySyncInvalidRemote(
                    f"registered target path is not a regular file: {path}"
                )
            elif write is not None:
                mode = "100644" if existing is None else existing.mode
                resulting = _RepositoryFile(
                    path,
                    mode,
                    GitHubGitObjectType.BLOB,
                    _git_blob_sha(write.raw_bytes),
                    write.raw_bytes,
                )
            elif (
                existing is not None
                and artifact_write_digest(existing.raw_bytes) == artifact.content_digest
            ):
                resulting = existing
            else:
                raise RepositorySyncConflict(
                    f"target artifact bytes are missing or require an explicit write: {path}"
                )

            if path.startswith(_WORKFLOW_PREFIX) and (
                existing is None
                or existing.raw_bytes != resulting.raw_bytes
                or existing.mode != resulting.mode
            ):
                raise RepositorySyncWorkflowMutationUnsupported(
                    f"workflow paths cannot be created or modified by repository sync: {path}"
                )
            plan[path] = resulting

        registry_existing = current.files.get(_REGISTRY_PATH)
        if registry_existing is None:
            registry_entry = walker.resolve(root_tree_sha, ".relay")
            if current.state is RepositoryContractState.UNINITIALIZED:
                mode = "100644"
            elif registry_entry is not None and registry_entry.complete:
                mode = registry_entry.entry.mode
            else:
                raise RepositorySyncInvalidRemote("existing .relay registry path is malformed")
        else:
            mode = registry_existing.mode
        registry_file = _RepositoryFile(
            _REGISTRY_PATH,
            mode,
            GitHubGitObjectType.BLOB,
            _git_blob_sha(serialize_repository_registry(request.target_registry)),
            serialize_repository_registry(request.target_registry),
        )
        plan[_REGISTRY_PATH] = registry_file
        return plan

    def _read_current_snapshot(
        self,
        *,
        walker: _TreeWalker,
        root_tree_sha: str,
        selection: GitHubRepositoryAccessSelection,
    ) -> _CurrentSnapshot:
        relay = walker.resolve(root_tree_sha, ".relay")
        if relay is None:
            return _CurrentSnapshot(RepositoryContractState.UNINITIALIZED, None, {})
        if (
            not relay.complete
            or relay.entry.object_type is not GitHubGitObjectType.TREE
            or relay.entry.mode != "040000"
        ):
            return _CurrentSnapshot(RepositoryContractState.INVALID, None, {})
        try:
            relay_tree = walker.tree(relay.entry.sha)
            if tuple(item.path for item in relay_tree.entries) != ("registry.json",):
                return _CurrentSnapshot(RepositoryContractState.INVALID, None, {})
            registry_entry = relay_tree.entries[0]
            if (
                registry_entry.object_type is not GitHubGitObjectType.BLOB
                or registry_entry.mode not in _REGULAR_MODES
            ):
                return _CurrentSnapshot(RepositoryContractState.INVALID, None, {})
            registry_file = walker.file(root_tree_sha, _REGISTRY_PATH)
            if registry_file is None:
                return _CurrentSnapshot(RepositoryContractState.INVALID, None, {})
            registry = parse_repository_registry(registry_file.raw_bytes)
            entries = [self._snapshot_entry(registry_file)]
            files = {_REGISTRY_PATH: registry_file}
            for artifact in registry.artifacts:
                artifact_file = walker.file(root_tree_sha, artifact.path)
                if artifact_file is None:
                    raise ArtifactIntegrityError(
                        f"registered path is not a regular file: {artifact.path}"
                    )
                files[artifact.path] = artifact_file
                entries.append(self._snapshot_entry(artifact_file))
            validated = validate_repository_snapshot(
                registry_raw=registry_file.raw_bytes,
                entries=tuple(entries),
                expected_project_id=selection.project_id,
                expected_repository=selection.repository,
            )
            if validated != registry:
                raise RepositoryContractInvalid("parsed registry changed during validation")
            return _CurrentSnapshot(RepositoryContractState.CURRENT, registry, files)
        except RepositoryContractInvalid, ArtifactIntegrityError, ValueError:
            return _CurrentSnapshot(RepositoryContractState.INVALID, None, {})

    @staticmethod
    def _snapshot_entry(file: _RepositoryFile) -> RepositorySnapshotEntry:
        return RepositorySnapshotEntry(
            path=file.path,
            mode=file.mode,
            object_type="blob",
            tree_object_sha=file.sha,
            blob_object_sha=file.sha,
            raw_bytes=file.raw_bytes,
        )

    @staticmethod
    def _validate_logical_snapshot(
        registry: RepositoryRegistry,
        registry_raw: bytes,
        artifact_bytes: dict[str, bytes],
    ) -> None:
        entries: list[RepositorySnapshotEntry] = []
        for path, raw_bytes in sorted(artifact_bytes.items()):
            sha = _git_blob_sha(raw_bytes)
            entries.append(
                RepositorySnapshotEntry(
                    path=path,
                    mode="100644",
                    object_type="blob",
                    tree_object_sha=sha,
                    blob_object_sha=sha,
                    raw_bytes=raw_bytes,
                )
            )
        registry_sha = _git_blob_sha(registry_raw)
        entries.append(
            RepositorySnapshotEntry(
                path=_REGISTRY_PATH,
                mode="100644",
                object_type="blob",
                tree_object_sha=registry_sha,
                blob_object_sha=registry_sha,
                raw_bytes=registry_raw,
            )
        )
        try:
            validated = validate_repository_snapshot(
                registry_raw=registry_raw,
                entries=tuple(entries),
                expected_project_id=registry.project_id,
                expected_repository=registry.repository,
            )
        except (RepositoryContractInvalid, ArtifactIntegrityError) as error:
            raise RepositorySyncSnapshotIntegrityError(
                "proposed repository target does not satisfy the schema-v1 contract"
            ) from error
        if validated != registry:
            raise RepositorySyncSnapshotIntegrityError(
                "proposed repository target changed its validated registry"
            )

    def _subject(
        self,
        request: RepositorySyncRequest,
        target_registry_raw: bytes,
    ) -> RepositorySyncSubjectV1:
        selection = request.selection
        return RepositorySyncSubjectV1(
            project_id=selection.project_id,
            repository=selection.repository,
            installation_id=selection.installation_id,
            github_repository_id=selection.github_repository_id,
            github_node_id=selection.github_node_id,
            expected_state_revision=selection.expected_state_revision,
            expected_default_branch=request.expected_default_branch,
            expected_base_commit=request.expected_base_commit,
            target_registry_digest=repository_registry_digest(request.target_registry),
            artifact_write_digests=tuple(
                ArtifactWriteDigest(
                    path=path,
                    content_digest=artifact_write_digest(write.raw_bytes),
                )
                for path, write in sorted(
                    ((item.path, item) for item in request.artifact_writes),
                    key=lambda item: item[0],
                )
            ),
        )

    def _require_authorization(
        self,
        request: RepositorySyncRequest,
        preparation: RepositorySyncPreparation,
        *,
        expected: RepositoryMutationAuthorization | None = None,
    ) -> RepositoryMutationAuthorization:
        if request.authorization_id is None:
            raise RepositorySyncAuthorizationRequired(
                "a non-no-op repository mutation requires explicit HUMAN authorization"
            )
        authorization = load_repository_mutation_authorization(
            self._database,
            request.authorization_id,
        )
        if authorization is None:
            raise RepositorySyncAuthorizationRequired(
                "repository mutation authorization does not exist"
            )
        if (
            authorization.project_id != request.selection.project_id
            or authorization.subject != preparation.subject
            or authorization.subject_digest != preparation.subject_digest
            or authorization.actor.kind is not ActorKind.HUMAN
            or (expected is not None and authorization != expected)
        ):
            raise RepositorySyncAuthorizationStale(
                "persisted authorization does not match the recomputed exact sync subject"
            )
        return authorization

    def _require_local_access(
        self,
        selection: GitHubRepositoryAccessSelection,
        *,
        require_write: bool,
    ) -> str:
        project = load_project(self._database, selection.project_id)
        if project is None or project.primary_repository != selection.repository:
            raise RepositorySyncAccessChanged(
                "Project.primary_repository no longer matches captured repository authority"
            )
        state = self._github_store.load_state(selection.project_id, selection.installation_id)
        if (
            state is None
            or not state.usable
            or state.state_revision != selection.expected_state_revision
        ):
            raise RepositorySyncAccessChanged(
                "installation readiness or state_revision changed during synchronization"
            )
        repositories = self._github_store.list_repositories(
            selection.project_id,
            selection.installation_id,
        )
        provider_repository = next(
            (
                item
                for item in repositories
                if item.github_repository_id == selection.github_repository_id
            ),
            None,
        )
        if (
            provider_repository is None
            or provider_repository.node_id != selection.github_node_id
            or provider_repository.full_name != selection.repository.path
        ):
            raise RepositorySyncAccessChanged(
                "repository membership or provider identity changed during synchronization"
            )
        profile = permission_profile(state.installation.permissions)
        if profile is None:
            raise RepositorySyncAccessChanged("installation permission profile is not accepted")
        if require_write and profile != "WRITE":
            raise RepositorySyncWritePermissionRequired(
                "installation is read-only for this synchronization request"
            )
        return profile

    def _read_provider(
        self,
        token: GitHubInstallationToken,
        selection: GitHubRepositoryAccessSelection,
        observed_at: datetime,
        *,
        expected_default_branch: str,
    ) -> GitHubRepositorySnapshot:
        provider = self._github_client.get_repository(
            token=token,
            repository_path=selection.repository.path,
            observed_at=observed_at,
        )
        if (
            provider.github_repository_id != selection.github_repository_id
            or provider.node_id != selection.github_node_id
            or provider.full_name != selection.repository.path
        ):
            raise RepositorySyncProviderIdentityChanged(
                "GitHub repository ID, node ID, or full_name changed"
            )
        if provider.archived:
            raise RepositorySyncAccessChanged("archived repositories cannot be synchronized")
        if provider.default_branch != expected_default_branch:
            raise RepositorySyncDefaultBranchChanged(
                "provider default branch differs from the exact expected branch"
            )
        return provider

    def _resolve_default_head(
        self,
        token: GitHubInstallationToken,
        repository: RepositoryRef,
        default_branch: str,
    ) -> CommitRef:
        try:
            ref = self._github_client.get_git_ref(
                token=token,
                repository_path=repository.path,
                branch=default_branch,
            )
        except GitHubRefNotFound as error:
            raise RepositorySyncNoDefaultHead(
                "repository has no existing default-branch head; Slice 1.3 does not create refs"
            ) from error
        if ref.object_type is not GitHubGitObjectType.COMMIT:
            raise RepositorySyncNoDefaultHead(
                "default branch does not resolve directly to a commit"
            )
        return CommitRef(repository=repository, sha=ref.sha)

    def _observe_ref_after_ambiguous_update(
        self,
        *,
        operation: _PreparedOperation,
        created_commit_sha: str,
        observed_at: datetime,
    ) -> str | None:
        try:
            provider = self._read_provider(
                operation.token,
                operation.request.selection,
                observed_at,
                expected_default_branch=operation.request.expected_default_branch,
            )
            head = self._resolve_default_head(
                operation.token,
                operation.request.selection.repository,
                provider.default_branch,
            )
            return head.sha
        except Exception as error:
            if isinstance(error, RepositorySyncError):
                return None
            return None

    def _verify_visible_result(
        self,
        *,
        operation: _PreparedOperation,
        created_commit_sha: str,
        observed_at: datetime,
        expected_parent: str,
    ) -> None:
        request = operation.request
        try:
            provider = self._read_provider(
                operation.token,
                request.selection,
                observed_at,
                expected_default_branch=request.expected_default_branch,
            )
            head = self._resolve_default_head(
                operation.token,
                request.selection.repository,
                provider.default_branch,
            )
            if head.sha != created_commit_sha:
                raise RepositorySyncPostWriteVerificationError(
                    "default-branch head does not equal the created commit",
                    created_commit_sha,
                )
            self._require_local_access(request.selection, require_write=True)
            commit = self._github_client.get_git_commit(
                token=operation.token,
                repository_path=request.selection.repository.path,
                sha=created_commit_sha,
            )
            if commit.sha != created_commit_sha or commit.parents != (expected_parent,):
                raise RepositorySyncPostWriteVerificationError(
                    "visible commit identity or exact parent does not match the prepared write",
                    created_commit_sha,
                )
            walker = _TreeWalker(
                self._github_client,
                operation.token,
                request.selection.repository.path,
            )
            current = self._read_current_snapshot(
                walker=walker,
                root_tree_sha=commit.tree_sha,
                selection=request.selection,
            )
            visible_registry = current.files.get(_REGISTRY_PATH)
            if (
                current.state is not RepositoryContractState.CURRENT
                or current.registry != request.target_registry
                or visible_registry is None
                or visible_registry.raw_bytes != operation.target_registry_raw
            ):
                raise RepositorySyncPostWriteVerificationError(
                    "visible repository snapshot does not match the exact target registry bytes",
                    created_commit_sha,
                )
            self._validate_logical_snapshot(
                request.target_registry,
                visible_registry.raw_bytes,
                {
                    path: item.raw_bytes
                    for path, item in current.files.items()
                    if path != _REGISTRY_PATH
                },
            )
        except RepositorySyncPostWriteVerificationError:
            raise
        except Exception as error:
            raise RepositorySyncPostWriteVerificationError(
                "visible repository commit could not be verified; reconciliation is required",
                created_commit_sha,
            ) from error


def _git_blob_sha(raw_bytes: bytes) -> str:
    header = f"blob {len(raw_bytes)}\0".encode("ascii")
    return hashlib.sha1(header + raw_bytes).hexdigest()


__all__ = ["RepositorySyncService"]
