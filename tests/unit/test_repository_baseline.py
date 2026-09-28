from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr, ValidationError

from relay_engine.domain import (
    Artifact,
    Baseline,
    CommitRef,
    Project,
    RepositoryRef,
)
from relay_engine.integrations.github import (
    GitHubAccessReadiness,
    GitHubAccountType,
    GitHubAppConfig,
    GitHubBlob,
    GitHubCommitObject,
    GitHubCommitResolution,
    GitHubGitObjectType,
    GitHubInstallationEvent,
    GitHubInstallationEventType,
    GitHubInstallationSnapshot,
    GitHubInstallationState,
    GitHubInstallationStatus,
    GitHubInstallationToken,
    GitHubIntegrationService,
    GitHubIntegrationStore,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRepositoryAccessSelection,
    GitHubRepositorySelectionMode,
    GitHubRepositorySnapshot,
    GitHubTree,
    GitHubTreeEntry,
)
from relay_engine.persistence import (
    insert_project,
    load_artifact,
    load_baseline,
    open_database,
)
from relay_engine.repository_baseline import (
    RepositoryAccessChanged,
    RepositoryBaselinePersistenceError,
    RepositoryBaselineService,
    RepositoryProviderIdentityChanged,
    RepositoryRevisionKind,
    RepositoryRevisionSelector,
    RepositorySnapshotIntegrityError,
    persist_verified_baseline,
)
from relay_engine.repository_contract import (
    ArtifactIntegrityError,
    RepositoryArtifactClass,
    RepositoryArtifactRevision,
    RepositoryArtifactState,
    RepositoryContractInvalid,
    RepositoryRegistry,
    RepositorySnapshotEntry,
    serialize_repository_registry,
    validate_repository_snapshot,
)

NOW = datetime(2026, 9, 28, 1, 0, tzinfo=UTC)
PROJECT_ID = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY_ID = "repo_018f47c1-7b2c-7abc-8def-123456789002"
ARTIFACT_ID = "art_018f47c1-7b2c-7abc-8def-123456789301"
BASELINE_ID = "base_018f47c1-7b2c-7abc-8def-123456789401"
BASELINE_ID_2 = "base_018f47c1-7b2c-7abc-8def-123456789402"
SHA1 = "1" * 40
SHA2 = "2" * 40
TREE_ROOT = "3" * 40
TREE_RELAY = "4" * 40
TREE_DOCS = "5" * 40
REGISTRY_BLOB_SHA = "6" * 40
ARTIFACT_BLOB_SHA = "7" * 40
REPOSITORY = RepositoryRef(id=REPOSITORY_ID, host="github.com", path="cschrupp/relay")


def _artifact_raw() -> bytes:
    return b"verified artifact bytes\n"


def _registry() -> RepositoryRegistry:
    raw = _artifact_raw()
    return RepositoryRegistry(
        project_id=PROJECT_ID,
        repository=REPOSITORY,
        artifacts=(
            RepositoryArtifactRevision(
                artifact_id=ARTIFACT_ID,
                revision=1,
                title="Artifact",
                artifact_type="DOCUMENT",
                artifact_class=RepositoryArtifactClass.LIVING_PROJECTION,
                artifact_state=RepositoryArtifactState.CURRENT,
                path="docs/a.md",
                content_digest=f"sha256:{hashlib.sha256(raw).hexdigest()}",
                updated_at=NOW,
                scope="test artifact",
            ),
        ),
        canonical=(),
    )


def _snapshot_entries(*, artifact_mode: str = "100644", artifact_raw: bytes | None = None):
    registry_raw = serialize_repository_registry(_registry())
    content = _artifact_raw() if artifact_raw is None else artifact_raw
    return registry_raw, (
        RepositorySnapshotEntry(
            path=".relay/registry.json",
            mode="100644",
            object_type="blob",
            tree_object_sha=REGISTRY_BLOB_SHA,
            blob_object_sha=REGISTRY_BLOB_SHA,
            raw_bytes=registry_raw,
        ),
        RepositorySnapshotEntry(
            path="docs/a.md",
            mode=artifact_mode,
            object_type="blob",
            tree_object_sha=ARTIFACT_BLOB_SHA,
            blob_object_sha=ARTIFACT_BLOB_SHA,
            raw_bytes=content,
        ),
    )


def _repo(observed_at: datetime = NOW) -> GitHubRepositorySnapshot:
    return GitHubRepositorySnapshot(
        github_repository_id=501,
        node_id="R_501",
        full_name=REPOSITORY.path,
        owner_login="cschrupp",
        private=False,
        archived=False,
        default_branch="main",
        observed_at=observed_at,
    )


def _installation(state_revision: int = 1) -> GitHubInstallationState:
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
        readiness=GitHubAccessReadiness.READY,
        state_revision=state_revision,
    )


def _seed_database():
    database = open_database(":memory:", apply_migrations=True, migration_applied_at=NOW)
    insert_project(
        database,
        Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY),
    )
    store = GitHubIntegrationStore(database)
    state = _installation()
    store.apply_mutation(
        expected_revision=None,
        state=state,
        repositories=(_repo(),),
        event=GitHubInstallationEvent(
            event_id="seed-s12",
            project_id=PROJECT_ID,
            installation_id=1001,
            event_type=GitHubInstallationEventType.INSTALLATION_SYNCED,
            observed_at=NOW,
            prior_state_revision=0,
            resulting_state_revision=1,
        ),
    )
    return database, store


def _selection(revision: int = 1) -> GitHubRepositoryAccessSelection:
    return GitHubRepositoryAccessSelection(
        project_id=PROJECT_ID,
        installation_id=1001,
        github_repository_id=501,
        github_node_id="R_501",
        repository=REPOSITORY,
        expected_state_revision=revision,
    )


def test_selector_rejects_ambiguous_prefixes_and_abbreviated_sha() -> None:
    with pytest.raises(ValidationError):
        RepositoryRevisionSelector(kind=RepositoryRevisionKind.BRANCH, value="refs/heads/main")
    with pytest.raises(ValidationError):
        RepositoryRevisionSelector(kind=RepositoryRevisionKind.TAG, value="refs/tags/v1")
    with pytest.raises(ValidationError):
        RepositoryRevisionSelector(kind=RepositoryRevisionKind.COMMIT_SHA, value="abc123")
    selector = RepositoryRevisionSelector(kind=RepositoryRevisionKind.COMMIT_SHA, value=SHA1)
    assert selector.value == SHA1


def test_snapshot_validator_accepts_exact_registry_and_blob_bytes() -> None:
    registry_raw, entries = _snapshot_entries()
    result = validate_repository_snapshot(
        registry_raw=registry_raw,
        entries=entries,
        expected_project_id=PROJECT_ID,
        expected_repository=REPOSITORY,
    )
    assert result == _registry()


def test_snapshot_validator_rejects_unknown_direct_relay_entry() -> None:
    registry_raw, entries = _snapshot_entries()
    extra = RepositorySnapshotEntry(
        path=".relay/extra.json",
        mode="100644",
        object_type="blob",
        tree_object_sha="8" * 40,
        blob_object_sha="8" * 40,
        raw_bytes=b"{}",
    )
    with pytest.raises(RepositoryContractInvalid, match="only .relay/registry.json"):
        validate_repository_snapshot(
            registry_raw=registry_raw,
            entries=(*entries, extra),
            expected_project_id=PROJECT_ID,
            expected_repository=REPOSITORY,
        )


@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_snapshot_validator_rejects_registered_symlink_or_submodule(mode: str) -> None:
    registry_raw, entries = _snapshot_entries(artifact_mode=mode)
    with pytest.raises(ArtifactIntegrityError, match="not a regular file"):
        validate_repository_snapshot(
            registry_raw=registry_raw,
            entries=entries,
            expected_project_id=PROJECT_ID,
            expected_repository=REPOSITORY,
        )


def test_snapshot_validator_rejects_digest_mismatch() -> None:
    registry_raw, entries = _snapshot_entries(artifact_raw=b"wrong")
    with pytest.raises(ArtifactIntegrityError, match="digest mismatch"):
        validate_repository_snapshot(
            registry_raw=registry_raw,
            entries=entries,
            expected_project_id=PROJECT_ID,
            expected_repository=REPOSITORY,
        )


def test_first_binding_then_later_identical_snapshot_reuses_artifact_commit() -> None:
    with _seed_database()[0] as database:
        selection = _selection()
        first = persist_verified_baseline(
            database=database,
            selection=selection,
            registry=_registry(),
            commit=CommitRef(repository=REPOSITORY, sha=SHA1),
            baseline_id=BASELINE_ID,
            decision_ids=(),
        )
        second = persist_verified_baseline(
            database=database,
            selection=selection,
            registry=_registry(),
            commit=CommitRef(repository=REPOSITORY, sha=SHA2),
            baseline_id=BASELINE_ID_2,
            decision_ids=(),
        )
        artifact = load_artifact(database, ARTIFACT_ID)
        assert artifact is not None
        assert artifact.commit.sha == SHA1
        assert first.commit.sha == SHA1
        assert second.commit.sha == SHA2


def test_existing_artifact_conflict_rolls_back_baseline() -> None:
    with _seed_database()[0] as database:
        conflicting = Artifact(
            id=ARTIFACT_ID,
            artifact_type="DOCUMENT",
            path="docs/other.md",
            commit=CommitRef(repository=REPOSITORY, sha=SHA1),
            content_digest=_registry().artifacts[0].content_digest,
        )
        database.connection.execute(
            "INSERT INTO artifacts(id, payload_json) VALUES (?, ?)",
            (conflicting.id, conflicting.model_dump_json()),
        )
        with pytest.raises(RepositoryBaselinePersistenceError, match="conflicts"):
            persist_verified_baseline(
                database=database,
                selection=_selection(),
                registry=_registry(),
                commit=CommitRef(repository=REPOSITORY, sha=SHA1),
                baseline_id=BASELINE_ID,
                decision_ids=(),
            )
        assert load_baseline(database, BASELINE_ID) is None


def test_missing_decision_rolls_back_new_artifact_and_baseline() -> None:
    with _seed_database()[0] as database:
        with pytest.raises(RepositoryBaselinePersistenceError, match="Decision does not exist"):
            persist_verified_baseline(
                database=database,
                selection=_selection(),
                registry=_registry(),
                commit=CommitRef(repository=REPOSITORY, sha=SHA1),
                baseline_id=BASELINE_ID,
                decision_ids=("dec_018f47c1-7b2c-7abc-8def-123456789999",),
            )
        assert load_artifact(database, ARTIFACT_ID) is None
        assert load_baseline(database, BASELINE_ID) is None


def test_state_revision_change_blocks_artifact_and_baseline() -> None:
    database, store = _seed_database()
    with database:
        prior = store.load_state(PROJECT_ID, 1001)
        assert prior is not None
        changed = prior.model_copy(update={"state_revision": 2})
        store.apply_mutation(
            expected_revision=1,
            state=changed,
            repositories=None,
            event=GitHubInstallationEvent(
                event_id="state-changed",
                project_id=PROJECT_ID,
                installation_id=1001,
                event_type=GitHubInstallationEventType.REPOSITORIES_CHANGED,
                observed_at=NOW,
                prior_state_revision=1,
                resulting_state_revision=2,
            ),
        )
        with pytest.raises(RepositoryAccessChanged):
            persist_verified_baseline(
                database=database,
                selection=_selection(revision=1),
                registry=_registry(),
                commit=CommitRef(repository=REPOSITORY, sha=SHA1),
                baseline_id=BASELINE_ID,
                decision_ids=(),
            )
        assert load_artifact(database, ARTIFACT_ID) is None
        assert load_baseline(database, BASELINE_ID) is None


def test_duplicate_baseline_id_is_rejected() -> None:
    with _seed_database()[0] as database:
        persist_verified_baseline(
            database=database,
            selection=_selection(),
            registry=_registry(),
            commit=CommitRef(repository=REPOSITORY, sha=SHA1),
            baseline_id=BASELINE_ID,
            decision_ids=(),
        )
        with pytest.raises(RepositoryBaselinePersistenceError, match="already exists"):
            persist_verified_baseline(
                database=database,
                selection=_selection(),
                registry=_registry(),
                commit=CommitRef(repository=REPOSITORY, sha=SHA1),
                baseline_id=BASELINE_ID,
                decision_ids=(),
            )


class FakeIntegration:
    def __init__(self) -> None:
        self.token = GitHubInstallationToken(
            token=SecretStr("token"), expires_at=NOW + timedelta(hours=1)
        )

    def create_repository_token(self, **kwargs):
        return self.token


class FakeSnapshotClient:
    def __init__(self, *, post_repository: GitHubRepositorySnapshot | None = None) -> None:
        self.repository_calls = 0
        self.refs: list[str] = []
        self.post_repository = _repo() if post_repository is None else post_repository
        self.registry_raw = serialize_repository_registry(_registry())

    def get_repository(self, **kwargs):
        self.repository_calls += 1
        return _repo() if self.repository_calls == 1 else self.post_repository

    def resolve_commit_sha(self, **kwargs):
        self.refs.append(kwargs["ref"])
        return GitHubCommitResolution(sha=SHA1)

    def get_git_commit(self, **kwargs):
        return GitHubCommitObject(sha=SHA1, tree_sha=TREE_ROOT)

    def get_git_tree(self, **kwargs):
        sha = kwargs["tree_sha"]
        if sha == TREE_ROOT:
            return GitHubTree(
                sha=sha,
                truncated=False,
                entries=(
                    GitHubTreeEntry(
                        path=".relay", mode="040000", object_type=GitHubGitObjectType.TREE, sha=TREE_RELAY
                    ),
                    GitHubTreeEntry(
                        path="docs", mode="040000", object_type=GitHubGitObjectType.TREE, sha=TREE_DOCS
                    ),
                ),
            )
        if sha == TREE_RELAY:
            return GitHubTree(
                sha=sha,
                truncated=False,
                entries=(
                    GitHubTreeEntry(
                        path="registry.json",
                        mode="100644",
                        object_type=GitHubGitObjectType.BLOB,
                        sha=REGISTRY_BLOB_SHA,
                    ),
                ),
            )
        return GitHubTree(
            sha=sha,
            truncated=False,
            entries=(
                GitHubTreeEntry(
                    path="a.md",
                    mode="100644",
                    object_type=GitHubGitObjectType.BLOB,
                    sha=ARTIFACT_BLOB_SHA,
                ),
            ),
        )

    def get_git_blob(self, **kwargs):
        sha = kwargs["blob_sha"]
        raw = self.registry_raw if sha == REGISTRY_BLOB_SHA else _artifact_raw()
        return GitHubBlob(sha=sha, raw_bytes=raw)


def test_service_brackets_snapshot_identity_and_pins_branch_once() -> None:
    with _seed_database()[0] as database:
        client = FakeSnapshotClient()
        service = RepositoryBaselineService(
            database=database,
            github_integration=FakeIntegration(),
            github_client=client,
        )
        result = service.resolve_and_persist_github_baseline(
            selection=_selection(),
            selector=RepositoryRevisionSelector(kind=RepositoryRevisionKind.BRANCH, value="main"),
            baseline_id=BASELINE_ID,
            decision_ids=(),
            observed_at=NOW,
        )
        assert client.repository_calls == 2
        assert client.refs == ["heads/main"]
        assert result.commit.sha == SHA1
        assert load_baseline(database, BASELINE_ID) is not None


def test_post_snapshot_provider_identity_change_blocks_persistence() -> None:
    changed = _repo().model_copy(update={"full_name": "cschrupp/renamed"})
    with _seed_database()[0] as database:
        client = FakeSnapshotClient(post_repository=changed)
        service = RepositoryBaselineService(
            database=database,
            github_integration=FakeIntegration(),
            github_client=client,
        )
        with pytest.raises(RepositoryProviderIdentityChanged):
            service.resolve_and_persist_github_baseline(
                selection=_selection(),
                selector=RepositoryRevisionSelector(kind=RepositoryRevisionKind.BRANCH, value="main"),
                baseline_id=BASELINE_ID,
                decision_ids=(),
                observed_at=NOW,
            )
        assert load_artifact(database, ARTIFACT_ID) is None
        assert load_baseline(database, BASELINE_ID) is None


def test_truncated_tree_blocks_snapshot() -> None:
    class TruncatedClient(FakeSnapshotClient):
        def get_git_tree(self, **kwargs):
            result = super().get_git_tree(**kwargs)
            if kwargs["tree_sha"] == TREE_ROOT:
                return result.model_copy(update={"truncated": True})
            return result

    with _seed_database()[0] as database:
        service = RepositoryBaselineService(
            database=database,
            github_integration=FakeIntegration(),
            github_client=TruncatedClient(),
        )
        with pytest.raises(RepositorySnapshotIntegrityError, match="truncated"):
            service.resolve_and_persist_github_baseline(
                selection=_selection(),
                selector=RepositoryRevisionSelector(kind=RepositoryRevisionKind.BRANCH, value="main"),
                baseline_id=BASELINE_ID,
                decision_ids=(),
                observed_at=NOW,
            )
