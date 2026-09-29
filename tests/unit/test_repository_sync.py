from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pydantic import SecretStr, ValidationError

from relay_engine.domain import ActorKind, ActorRef, CommitRef, Project, RepositoryRef
from relay_engine.integrations.github import (
    GitHubAccessReadiness,
    GitHubAccountType,
    GitHubCommitObject,
    GitHubCreatedObject,
    GitHubGitObjectType,
    GitHubInstallationEvent,
    GitHubInstallationEventType,
    GitHubInstallationSnapshot,
    GitHubInstallationState,
    GitHubInstallationStatus,
    GitHubInstallationToken,
    GitHubIntegrationStore,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRefNotFound,
    GitHubRefTarget,
    GitHubRepositoryAccessSelection,
    GitHubRepositorySelectionMode,
    GitHubRepositorySnapshot,
    GitHubTree,
    GitHubTreeEntry,
)
from relay_engine.persistence import (
    PersistenceIntegrityError,
    insert_project,
    load_repository_mutation_authorization,
    open_database,
)
from relay_engine.repository_contract import (
    RepositoryArtifactClass,
    RepositoryArtifactRevision,
    RepositoryArtifactState,
    RepositoryRegistry,
    serialize_repository_registry,
)
from relay_engine.repository_sync import (
    RepositoryArtifactWrite,
    RepositoryContractState,
    RepositoryMutationAuthorization,
    RepositorySyncAccessChanged,
    RepositorySyncAuthorizationRequired,
    RepositorySyncAuthorizationStale,
    RepositorySyncConflict,
    RepositorySyncNoDefaultHead,
    RepositorySyncRequest,
    RepositorySyncService,
    RepositorySyncWorkflowMutationUnsupported,
    artifact_write_digest,
    repository_sync_subject_digest,
)

NOW = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)
PROJECT_ID = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY_ID = "repo_018f47c1-7b2c-7abc-8def-123456789002"
AUTHORIZATION_ID = "rma_018f47c1-7b2c-7abc-8def-123456789003"
ARTIFACT_ID = "art_018f47c1-7b2c-7abc-8def-123456789004"
BASE_SHA = "1" * 40
REPOSITORY = RepositoryRef(id=REPOSITORY_ID, host="github.com", path="cschrupp/relay")
ACTOR = ActorRef(kind=ActorKind.HUMAN, id="act_018f47c1-7b2c-7abc-8def-123456789005")
RAW = b"Relay test artifact\n"


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def _target_registry() -> RepositoryRegistry:
    return RepositoryRegistry(
        project_id=PROJECT_ID,
        repository=REPOSITORY,
        artifacts=(
            RepositoryArtifactRevision(
                artifact_id=ARTIFACT_ID,
                revision=1,
                title="Test artifact",
                artifact_type="DOCUMENT",
                artifact_class=RepositoryArtifactClass.WORKING,
                artifact_state=RepositoryArtifactState.DRAFT,
                path="docs/test.md",
                content_digest=artifact_write_digest(RAW),
                updated_at=NOW,
                scope="Slice 1.3 repository-sync regression fixture",
            ),
        ),
        canonical=(),
    )


def _request_with_target(
    request: RepositorySyncRequest, path: str, raw: bytes
) -> RepositorySyncRequest:
    original = request.target_registry.artifacts[0]
    artifact = original.model_copy(
        update={"path": path, "content_digest": artifact_write_digest(raw)}
    )
    registry = request.target_registry.model_copy(update={"artifacts": (artifact,)})
    return request.model_copy(
        update={
            "target_registry": registry,
            "artifact_writes": (RepositoryArtifactWrite(path=path, raw_bytes=raw),),
        }
    )


def _event(
    state: GitHubInstallationState,
    event_id: str = "seed-sync-state",
    prior_revision: int = 0,
) -> GitHubInstallationEvent:
    return GitHubInstallationEvent(
        event_id=event_id,
        project_id=state.project_id,
        installation_id=state.installation_id,
        event_type=GitHubInstallationEventType.INSTALLATION_SYNCED,
        observed_at=NOW,
        prior_state_revision=prior_revision,
        resulting_state_revision=state.state_revision,
    )


def _permissions(*, write: bool) -> tuple[GitHubPermissionGrant, ...]:
    return (
        GitHubPermissionGrant(
            name="contents",
            level=GitHubPermissionLevel.WRITE if write else GitHubPermissionLevel.READ,
        ),
        GitHubPermissionGrant(name="metadata", level=GitHubPermissionLevel.READ),
    )


def _make_state(*, write: bool, revision: int = 1) -> GitHubInstallationState:
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
            permissions=_permissions(write=write),
            observed_at=NOW,
        ),
        readiness=GitHubAccessReadiness.READY,
        state_revision=revision,
    )


class _FakeIntegration:
    def __init__(self) -> None:
        self.read_tokens = 0
        self.write_tokens = 0
        self.github_store: GitHubIntegrationStore | None = None
        self.after_write_token: Callable[[], None] | None = None

    @staticmethod
    def _token(value: str) -> GitHubInstallationToken:
        return GitHubInstallationToken(token=SecretStr(value), expires_at=NOW + timedelta(hours=1))

    def create_repository_token(self, *, selection: object, observed_at: datetime):
        self.read_tokens += 1
        return self._token("read-token")

    def create_repository_write_token(self, *, selection: object, observed_at: datetime):
        self.write_tokens += 1
        if self.after_write_token is not None:
            self.after_write_token()
        return self._token("write-token")


class _FakeGitHub:
    def __init__(self) -> None:
        self.head = BASE_SHA
        self.blobs: dict[str, bytes] = {_git_blob_sha(b"README\n"): b"README\n"}
        self.trees: dict[str, GitHubTree] = {}
        self.commits: dict[str, GitHubCommitObject] = {}
        self.git_object_writes = 0
        self.blob_creations = 0
        self.tree_creations = 0
        self.commit_creations = 0
        self.ref_updates = 0
        self.default_branch = "main"
        self.missing_head = False
        self.before_ref_check: Callable[[], None] | None = None
        self._base_tree = self._store_tree(
            {"README.md": ("100644", GitHubGitObjectType.BLOB, _git_blob_sha(b"README\n"))}
        )
        self.commits[BASE_SHA] = GitHubCommitObject(sha=BASE_SHA, tree_sha=self._base_tree)

    def _store_tree(self, files: dict[str, tuple[str, GitHubGitObjectType, str]]) -> str:
        root: dict[str, Any] = {}
        for path, (mode, object_type, sha) in files.items():
            node = root
            parts = path.split("/")
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = (mode, object_type, sha)

        def store(node: dict[str, Any]) -> str:
            entries: list[GitHubTreeEntry] = []
            for name, value in sorted(node.items()):
                if isinstance(value, dict):
                    child_sha = store(value)
                    entries.append(
                        GitHubTreeEntry(
                            path=name,
                            mode="040000",
                            object_type=GitHubGitObjectType.TREE,
                            sha=child_sha,
                        )
                    )
                else:
                    mode, object_type, sha = value
                    entries.append(
                        GitHubTreeEntry(path=name, mode=mode, object_type=object_type, sha=sha)
                    )
            material = json.dumps(
                [item.model_dump(mode="json") for item in entries], sort_keys=True
            ).encode()
            tree_sha = hashlib.sha1(material).hexdigest()
            self.trees[tree_sha] = GitHubTree(sha=tree_sha, entries=tuple(entries), truncated=False)
            return tree_sha

        return store(root)

    def _flatten(self, tree_sha: str, prefix: str = ""):
        result = {}
        for item in self.trees[tree_sha].entries:
            path = f"{prefix}{item.path}"
            if item.object_type is GitHubGitObjectType.TREE:
                result.update(self._flatten(item.sha, f"{path}/"))
            else:
                result[path] = (item.mode, item.object_type, item.sha)
        return result

    def get_repository(self, *, token, repository_path, observed_at):
        return GitHubRepositorySnapshot(
            github_repository_id=501,
            node_id="R_501",
            full_name=REPOSITORY.path,
            owner_login="cschrupp",
            private=False,
            archived=False,
            default_branch=self.default_branch,
            observed_at=observed_at,
        )

    def get_git_ref(self, *, token, repository_path, branch):
        if self.missing_head:
            raise GitHubRefNotFound("no existing branch")
        return GitHubRefTarget(
            ref=f"refs/heads/{branch}",
            sha=self.head,
            object_type=GitHubGitObjectType.COMMIT,
        )

    def get_git_commit(self, *, token, repository_path, sha):
        return self.commits[sha]

    def get_git_tree(self, *, token, repository_path, tree_sha):
        return self.trees[tree_sha]

    def get_git_blob(self, *, token, repository_path, blob_sha):
        from relay_engine.integrations.github import GitHubBlob

        return GitHubBlob(sha=blob_sha, raw_bytes=self.blobs[blob_sha])

    def create_git_blob(self, *, token, repository_path, raw_bytes):
        self.git_object_writes += 1
        self.blob_creations += 1
        sha = _git_blob_sha(raw_bytes)
        self.blobs[sha] = raw_bytes
        return GitHubCreatedObject(sha=sha)

    def create_git_tree(self, *, token, repository_path, base_tree_sha, entries):
        self.git_object_writes += 1
        self.tree_creations += 1
        files = self._flatten(base_tree_sha)
        for entry in entries:
            files[entry.path] = (entry.mode, entry.object_type, entry.sha)
        return GitHubCreatedObject(sha=self._store_tree(files))

    def create_git_commit(self, *, token, repository_path, message, tree_sha, parent_sha):
        self.git_object_writes += 1
        self.commit_creations += 1
        sha = hashlib.sha1(f"{tree_sha}:{parent_sha}:{message}".encode()).hexdigest()
        commit = GitHubCommitObject(sha=sha, tree_sha=tree_sha, parents=(parent_sha,))
        self.commits[sha] = commit
        if self.before_ref_check is not None:
            self.before_ref_check()
        return commit

    def update_git_ref(self, *, token, repository_path, branch, commit_sha, force=False):
        assert force is False
        assert branch == "main"
        self.ref_updates += 1
        self.head = commit_sha
        return GitHubRefTarget(
            ref="refs/heads/main", sha=commit_sha, object_type=GitHubGitObjectType.COMMIT
        )


@pytest.fixture
def fixture_env():
    database = open_database(":memory:", apply_migrations=True, migration_applied_at=NOW)
    insert_project(database, Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY))
    github_store = GitHubIntegrationStore(database)
    state = _make_state(write=True)
    github_store.apply_mutation(
        expected_revision=None,
        state=state,
        repositories=(
            GitHubRepositorySnapshot(
                github_repository_id=501,
                node_id="R_501",
                full_name=REPOSITORY.path,
                owner_login="cschrupp",
                private=False,
                archived=False,
                default_branch="main",
                observed_at=NOW,
            ),
        ),
        event=_event(state),
    )
    integration = _FakeIntegration()
    integration.github_store = github_store
    github = _FakeGitHub()
    service = RepositorySyncService(
        database=database,
        github_integration=integration,  # type: ignore[arg-type]
        github_client=github,  # type: ignore[arg-type]
        github_store=github_store,
    )
    selection = GitHubRepositoryAccessSelection(
        project_id=PROJECT_ID,
        installation_id=1001,
        github_repository_id=501,
        github_node_id="R_501",
        repository=REPOSITORY,
        expected_state_revision=1,
    )
    request = RepositorySyncRequest(
        selection=selection,
        expected_default_branch="main",
        expected_base_commit=CommitRef(repository=REPOSITORY, sha=BASE_SHA),
        target_registry=_target_registry(),
        artifact_writes=(RepositoryArtifactWrite(path="docs/test.md", raw_bytes=RAW),),
    )
    try:
        yield database, service, integration, github, request
    finally:
        database.close()


def test_subject_digest_is_deterministic_and_authorization_has_no_slice_fields(
    fixture_env,
) -> None:
    database, service, _, _, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    assert preparation.state is RepositoryContractState.SYNCHRONIZABLE
    assert preparation.subject is not None
    assert preparation.subject_digest == repository_sync_subject_digest(preparation.subject)
    authorization = service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Authorize exact repository initialization.",
    )
    persisted = load_repository_mutation_authorization(database, AUTHORIZATION_ID)
    assert persisted == authorization
    assert "slice_id" not in RepositoryMutationAuthorization.model_fields
    assert "baseline_id" not in RepositoryMutationAuthorization.model_fields
    assert "gate_id" not in RepositoryMutationAuthorization.model_fields


def test_preparation_uses_read_token_and_creates_no_remote_git_objects(fixture_env) -> None:
    _, service, integration, github, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    assert preparation.state is RepositoryContractState.SYNCHRONIZABLE
    assert integration.read_tokens == 1
    assert integration.write_tokens == 0
    assert github.git_object_writes == 0
    assert github.ref_updates == 0


def test_uninitialized_empty_repository_without_default_head_is_not_bootstrapped(
    fixture_env,
) -> None:
    _, service, integration, github, request = fixture_env
    github.missing_head = True
    with pytest.raises(RepositorySyncNoDefaultHead, match="does not create refs"):
        service.prepare_repository_sync(request, observed_at=NOW)
    assert integration.write_tokens == 0
    assert github.git_object_writes == 0


def test_execution_requires_exact_human_authorization_before_write_token(fixture_env) -> None:
    _, service, integration, github, request = fixture_env
    with pytest.raises(RepositorySyncAuthorizationRequired):
        service.execute_repository_sync(request, observed_at=NOW)
    assert integration.write_tokens == 0
    assert github.git_object_writes == 0
    assert github.ref_updates == 0


def test_authorization_cannot_be_retargeted_to_another_registry_subject(fixture_env) -> None:
    _, service, integration, github, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Approve only this exact target.",
    )
    changed_artifact = request.target_registry.artifacts[0].model_copy(
        update={"scope": "A different authorized registry subject."}
    )
    changed_registry = request.target_registry.model_copy(update={"artifacts": (changed_artifact,)})
    changed_request = request.model_copy(
        update={"target_registry": changed_registry, "authorization_id": AUTHORIZATION_ID}
    )
    with pytest.raises(RepositorySyncAuthorizationStale):
        service.execute_repository_sync(changed_request, observed_at=NOW)
    assert integration.write_tokens == 0
    assert github.git_object_writes == 0


@pytest.mark.parametrize(
    ("existing_path", "existing_bytes"),
    [("docs/test.md", b"unregistered different bytes\n"), ("docs/test.md/child.md", b"child\n")],
)
def test_unregistered_file_or_directory_cannot_be_overwritten(
    fixture_env, existing_path: str, existing_bytes: bytes
) -> None:
    _, service, _, github, request = fixture_env
    sha = _git_blob_sha(existing_bytes)
    github.blobs[sha] = existing_bytes
    files = github._flatten(github._base_tree)
    files[existing_path] = ("100644", GitHubGitObjectType.BLOB, sha)
    github._base_tree = github._store_tree(files)
    github.commits[BASE_SHA] = GitHubCommitObject(sha=BASE_SHA, tree_sha=github._base_tree)
    with pytest.raises(RepositorySyncConflict):
        service.prepare_repository_sync(request, observed_at=NOW)
    assert github.git_object_writes == 0


def test_exact_existing_unregistered_file_may_be_adopted_without_replacement_blob(
    fixture_env,
) -> None:
    _, service, _, github, request = fixture_env
    sha = _git_blob_sha(RAW)
    github.blobs[sha] = RAW
    files = github._flatten(github._base_tree)
    files["docs/test.md"] = ("100644", GitHubGitObjectType.BLOB, sha)
    github._base_tree = github._store_tree(files)
    github.commits[BASE_SHA] = GitHubCommitObject(sha=BASE_SHA, tree_sha=github._base_tree)
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    assert preparation.state is RepositoryContractState.SYNCHRONIZABLE
    assert preparation.changed_paths == (".relay/registry.json",)
    service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Adopt the exact existing bytes without rewriting them.",
    )
    service.execute_repository_sync(
        request.model_copy(update={"authorization_id": AUTHORIZATION_ID}), observed_at=NOW
    )
    assert github.blob_creations == 1


def test_workflow_file_creation_is_rejected_by_permission_ceiling(fixture_env) -> None:
    _, service, _, github, request = fixture_env
    workflow_request = _request_with_target(
        request, ".github/workflows/generated.yml", b"name: generated\n"
    )
    with pytest.raises(RepositorySyncWorkflowMutationUnsupported):
        service.prepare_repository_sync(workflow_request, observed_at=NOW)
    assert github.git_object_writes == 0


def test_authorized_initialization_uses_one_commit_and_exact_parent(fixture_env) -> None:
    database, service, _, github, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Approve the prepared exact write set.",
    )
    result = service.execute_repository_sync(
        request.model_copy(update={"authorization_id": AUTHORIZATION_ID}), observed_at=NOW
    )
    assert result.wrote_remote is True
    assert result.prior_commit.sha == BASE_SHA
    assert result.resulting_commit.sha == github.head
    assert github.commits[github.head].parents == (BASE_SHA,)
    assert github.ref_updates == 1
    assert database.connection.execute("SELECT COUNT(*) FROM baselines").fetchone()[0] == 0


def test_multifile_initialization_uses_one_tree_one_commit_and_one_ref_update(fixture_env) -> None:
    _, service, _, github, request = fixture_env
    second_raw = b"Second registered artifact\n"
    second = RepositoryArtifactRevision(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789007",
        revision=1,
        title="Second test artifact",
        artifact_type="DOCUMENT",
        artifact_class=RepositoryArtifactClass.WORKING,
        artifact_state=RepositoryArtifactState.DRAFT,
        path="docs/another.md",
        content_digest=artifact_write_digest(second_raw),
        updated_at=NOW,
        scope="Atomic multi-file initialization regression fixture",
    )
    registry = request.target_registry.model_copy(
        update={"artifacts": (second, request.target_registry.artifacts[0])}
    )
    multi_request = request.model_copy(
        update={
            "target_registry": registry,
            "artifact_writes": (
                RepositoryArtifactWrite(path="docs/another.md", raw_bytes=second_raw),
                request.artifact_writes[0],
            ),
        }
    )
    preparation = service.prepare_repository_sync(multi_request, observed_at=NOW)
    service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Approve the complete two-file registry snapshot.",
    )
    service.execute_repository_sync(
        multi_request.model_copy(update={"authorization_id": AUTHORIZATION_ID}),
        observed_at=NOW,
    )
    assert github.blob_creations == 3
    assert github.tree_creations == 1
    assert github.commit_creations == 1
    assert github.ref_updates == 1


def test_local_installation_change_after_object_creation_blocks_ref_visibility(fixture_env) -> None:
    _, service, integration, github, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Approve the exact write set.",
    )
    assert integration.github_store is not None

    def change_local_state() -> None:
        next_state = _make_state(write=True, revision=2)
        existing_repositories = integration.github_store.list_repositories(PROJECT_ID, 1001)
        integration.github_store.apply_mutation(
            expected_revision=1,
            state=next_state,
            repositories=existing_repositories,
            event=_event(next_state, "sync-race-state-change", prior_revision=1),
        )

    integration.after_write_token = change_local_state
    with pytest.raises(RepositorySyncAccessChanged):
        service.execute_repository_sync(
            request.model_copy(update={"authorization_id": AUTHORIZATION_ID}), observed_at=NOW
        )
    assert github.git_object_writes > 0
    assert github.ref_updates == 0


def test_advanced_default_branch_head_blocks_nonforce_ref_update(fixture_env) -> None:
    _, service, _, github, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Approve the exact write set.",
    )
    github.before_ref_check = lambda: setattr(github, "head", "f" * 40)
    with pytest.raises(RepositorySyncConflict, match="head advanced"):
        service.execute_repository_sync(
            request.model_copy(update={"authorization_id": AUTHORIZATION_ID}), observed_at=NOW
        )
    assert github.git_object_writes > 0
    assert github.ref_updates == 0


def test_exact_current_retry_is_a_noop_without_authorization(fixture_env) -> None:
    _, service, integration, github, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Approve the prepared exact write set.",
    )
    service.execute_repository_sync(
        request.model_copy(update={"authorization_id": AUTHORIZATION_ID}), observed_at=NOW
    )
    writes = github.git_object_writes
    no_op = service.execute_repository_sync(request, observed_at=NOW)
    assert no_op.wrote_remote is False
    assert no_op.prior_commit == no_op.resulting_commit
    assert github.git_object_writes == writes
    assert github.ref_updates == 1
    assert integration.write_tokens == 1


def test_authorization_rejects_non_human_and_digest_tampering(fixture_env) -> None:
    _, service, _, _, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    with pytest.raises(RepositorySyncAuthorizationRequired):
        service.authorize_repository_sync(
            authorization_id=AUTHORIZATION_ID,
            preparation=preparation,
            actor=ActorRef(kind=ActorKind.AGENT, id="act_018f47c1-7b2c-7abc-8def-123456789006"),
            granted_at=NOW,
            reason="Not human authority.",
        )
    assert preparation.subject is not None
    with pytest.raises(ValidationError):
        RepositoryMutationAuthorization(
            authorization_id=AUTHORIZATION_ID,
            project_id=PROJECT_ID,
            subject=preparation.subject,
            subject_digest="sha256:" + "0" * 64,
            actor=ACTOR,
            granted_at=NOW,
            reason="Bad digest.",
        )


def test_mutation_authorization_payload_index_mismatch_is_integrity_error(fixture_env) -> None:
    database, service, _, _, request = fixture_env
    preparation = service.prepare_repository_sync(request, observed_at=NOW)
    auth = service.authorize_repository_sync(
        authorization_id=AUTHORIZATION_ID,
        preparation=preparation,
        actor=ACTOR,
        granted_at=NOW,
        reason="Exact authority.",
    )
    altered = auth.model_copy(update={"project_id": "prj_018f47c1-7b2c-7abc-8def-123456789099"})
    database.connection.execute(
        "UPDATE repository_mutation_authorizations SET payload_json = ? WHERE authorization_id = ?",
        (altered.model_dump_json(), AUTHORIZATION_ID),
    )
    with pytest.raises(PersistenceIntegrityError):
        load_repository_mutation_authorization(database, AUTHORIZATION_ID)


def test_migration_v3_has_project_subject_index_and_no_slice_authority(fixture_env) -> None:
    database, *_ = fixture_env
    columns = {
        row[1]
        for row in database.connection.execute(
            "PRAGMA table_info(repository_mutation_authorizations)"
        )
    }
    assert columns == {"authorization_id", "project_id", "subject_digest", "payload_json"}
    assert "slice_id" not in columns
    indexes = {
        row[1]
        for row in database.connection.execute(
            "PRAGMA index_list(repository_mutation_authorizations)"
        )
    }
    assert "repository_mutation_authorizations_by_project_subject" in indexes


def test_target_registry_wire_bytes_are_deterministic() -> None:
    assert serialize_repository_registry(_target_registry()) == serialize_repository_registry(
        _target_registry()
    )
