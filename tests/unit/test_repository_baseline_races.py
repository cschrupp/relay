from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr

from relay_engine.domain import ActorKind, ActorRef, Project, RepositoryRef
from relay_engine.integrations.github import (
    GitHubAccessReadiness,
    GitHubAccountType,
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
    GitHubIntegrationStore,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRepositoryAccessSelection,
    GitHubRepositorySelectionMode,
    GitHubRepositorySnapshot,
    GitHubRepositoryUnavailable,
    GitHubTree,
    GitHubTreeEntry,
)
from relay_engine.persistence import load_artifact, load_baseline, open_database
from relay_engine.project_slice import MutationMetadata, create_project
from relay_engine.repository_baseline import (
    RepositoryAccessChanged,
    RepositoryAccessUnavailable,
    RepositoryBaselineService,
    RepositoryProviderIdentityChanged,
    RepositoryRevisionKind,
    RepositoryRevisionSelector,
)
from relay_engine.repository_contract import (
    RepositoryArtifactClass,
    RepositoryArtifactRevision,
    RepositoryArtifactState,
    RepositoryRegistry,
    serialize_repository_registry,
)

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


ARTIFACT_ID = "art_018f47c1-7b2c-7abc-8def-123456789301"
BASELINE_ID = "base_018f47c1-7b2c-7abc-8def-123456789401"
COMMIT_SHA = "1" * 40
TREE_ROOT = "2" * 40
TREE_RELAY = "3" * 40
TREE_DOCS = "4" * 40
REGISTRY_BLOB_SHA = "5" * 40
ARTIFACT_BLOB_SHA = "6" * 40


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
                scope="race regression artifact",
            ),
        ),
        canonical=(),
    )


def _repository(**changes: object) -> GitHubRepositorySnapshot:
    repository = GitHubRepositorySnapshot(
        github_repository_id=501,
        node_id="R_501",
        full_name=REPOSITORY.path,
        owner_login="cschrupp",
        private=False,
        archived=False,
        default_branch="main",
        observed_at=NOW,
    )
    return repository.model_copy(update=changes)


def _state(revision: int = 1) -> GitHubInstallationState:
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
        state_revision=revision,
    )


def _seed_database():
    database = open_database(":memory:", apply_migrations=True, migration_applied_at=NOW)
    _create_project(database, Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY))
    store = GitHubIntegrationStore(database)
    store.apply_mutation(
        expected_revision=None,
        state=_state(),
        repositories=(_repository(),),
        event=GitHubInstallationEvent(
            event_id="seed-race-regressions",
            project_id=PROJECT_ID,
            installation_id=1001,
            event_type=GitHubInstallationEventType.INSTALLATION_SYNCED,
            observed_at=NOW,
            prior_state_revision=0,
            resulting_state_revision=1,
        ),
    )
    return database, store


def _selection() -> GitHubRepositoryAccessSelection:
    return GitHubRepositoryAccessSelection(
        project_id=PROJECT_ID,
        installation_id=1001,
        github_repository_id=501,
        github_node_id="R_501",
        repository=REPOSITORY,
        expected_state_revision=1,
    )


def _selector() -> RepositoryRevisionSelector:
    return RepositoryRevisionSelector(kind=RepositoryRevisionKind.BRANCH, value="main")


class FakeIntegration:
    def __init__(self) -> None:
        self.calls = 0
        self.selections: list[GitHubRepositoryAccessSelection] = []

    def create_repository_token(self, **kwargs):
        self.calls += 1
        self.selections.append(kwargs["selection"])
        return GitHubInstallationToken(
            token=SecretStr("token"), expires_at=NOW + timedelta(hours=1)
        )


class SequencedSnapshotClient:
    def __init__(
        self,
        *,
        pre_repository: GitHubRepositorySnapshot | None = None,
        post_repository: GitHubRepositorySnapshot | None = None,
        post_error: Exception | None = None,
        after_post_check: Callable[[], None] | None = None,
        remote_guard: Callable[[], None] | None = None,
    ) -> None:
        self.pre_repository = _repository() if pre_repository is None else pre_repository
        self.post_repository = _repository() if post_repository is None else post_repository
        self.post_error = post_error
        self.after_post_check = after_post_check
        self.remote_guard = remote_guard
        self.repository_calls = 0
        self.resolve_calls = 0
        self.events: list[str] = []
        self.registry_raw = serialize_repository_registry(_registry())

    def _record(self, event: str) -> None:
        if self.remote_guard is not None:
            self.remote_guard()
        self.events.append(event)

    def get_repository(self, **kwargs):
        self._record("repository")
        self.repository_calls += 1
        if self.repository_calls == 1:
            return self.pre_repository
        if self.post_error is not None:
            raise self.post_error
        result = self.post_repository
        if self.after_post_check is not None:
            self.after_post_check()
        return result

    def resolve_commit_sha(self, **kwargs):
        self._record("resolve")
        self.resolve_calls += 1
        return GitHubCommitResolution(sha=COMMIT_SHA)

    def get_git_commit(self, **kwargs):
        self._record("commit")
        return GitHubCommitObject(sha=COMMIT_SHA, tree_sha=TREE_ROOT)

    def get_git_tree(self, **kwargs):
        self._record(f"tree:{kwargs['tree_sha']}")
        sha = kwargs["tree_sha"]
        if sha == TREE_ROOT:
            return GitHubTree(
                sha=sha,
                truncated=False,
                entries=(
                    GitHubTreeEntry(
                        path=".relay",
                        mode="040000",
                        object_type=GitHubGitObjectType.TREE,
                        sha=TREE_RELAY,
                    ),
                    GitHubTreeEntry(
                        path="docs",
                        mode="040000",
                        object_type=GitHubGitObjectType.TREE,
                        sha=TREE_DOCS,
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
        self._record(f"blob:{kwargs['blob_sha']}")
        sha = kwargs["blob_sha"]
        raw = self.registry_raw if sha == REGISTRY_BLOB_SHA else _artifact_raw()
        return GitHubBlob(sha=sha, raw_bytes=raw)


def _service(database, client: SequencedSnapshotClient, integration: FakeIntegration | None = None):
    return RepositoryBaselineService(
        database=database,
        github_integration=FakeIntegration() if integration is None else integration,
        github_client=client,
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"github_repository_id": 502},
        {"node_id": "R_502"},
        {"full_name": "cschrupp/renamed"},
    ],
)
def test_pre_snapshot_provider_identity_mismatch_blocks_before_ref_resolution(
    changes: dict[str, object],
) -> None:
    database, _ = _seed_database()
    with database:
        client = SequencedSnapshotClient(pre_repository=_repository(**changes))
        integration = FakeIntegration()
        service = _service(database, client, integration)
        with pytest.raises(RepositoryProviderIdentityChanged):
            service.resolve_and_persist_github_baseline(
                selection=_selection(),
                selector=_selector(),
                baseline_id=BASELINE_ID,
                decision_ids=(),
                observed_at=NOW,
            )
        assert integration.calls == 1
        assert integration.selections == [_selection()]
        assert client.repository_calls == 1
        assert client.resolve_calls == 0
        assert load_artifact(database, ARTIFACT_ID) is None
        assert load_baseline(database, BASELINE_ID) is None


@pytest.mark.parametrize(
    "changes",
    [
        {"github_repository_id": 502},
        {"node_id": "R_502"},
        {"full_name": "cschrupp/renamed"},
    ],
)
def test_post_snapshot_provider_identity_mismatch_blocks_after_remote_proof(
    changes: dict[str, object],
) -> None:
    database, _ = _seed_database()
    with database:
        client = SequencedSnapshotClient(post_repository=_repository(**changes))
        service = _service(database, client)
        with pytest.raises(RepositoryProviderIdentityChanged):
            service.resolve_and_persist_github_baseline(
                selection=_selection(),
                selector=_selector(),
                baseline_id=BASELINE_ID,
                decision_ids=(),
                observed_at=NOW,
            )
        assert client.repository_calls == 2
        assert client.resolve_calls == 1
        assert client.events[-1] == "repository"
        assert any(event.startswith("blob:") for event in client.events[:-1])
        assert load_artifact(database, ARTIFACT_ID) is None
        assert load_baseline(database, BASELINE_ID) is None


def test_post_snapshot_identity_unavailable_fails_closed() -> None:
    database, _ = _seed_database()
    with database:
        client = SequencedSnapshotClient(
            post_error=GitHubRepositoryUnavailable("repository unavailable after snapshot")
        )
        service = _service(database, client)
        with pytest.raises(RepositoryAccessUnavailable):
            service.resolve_and_persist_github_baseline(
                selection=_selection(),
                selector=_selector(),
                baseline_id=BASELINE_ID,
                decision_ids=(),
                observed_at=NOW,
            )
        assert client.repository_calls == 2
        assert client.events[-1] == "repository"
        assert load_artifact(database, ARTIFACT_ID) is None
        assert load_baseline(database, BASELINE_ID) is None


def test_local_revision_change_after_post_provider_check_blocks_persistence() -> None:
    database, store = _seed_database()

    def advance_local_authority() -> None:
        prior = store.load_state(PROJECT_ID, 1001)
        assert prior is not None
        store.apply_mutation(
            expected_revision=1,
            state=prior.model_copy(update={"state_revision": 2}),
            repositories=None,
            event=GitHubInstallationEvent(
                event_id="authority-changed-after-post-check",
                project_id=PROJECT_ID,
                installation_id=1001,
                event_type=GitHubInstallationEventType.REPOSITORIES_CHANGED,
                observed_at=NOW,
                prior_state_revision=1,
                resulting_state_revision=2,
            ),
        )

    with database:
        client = SequencedSnapshotClient(after_post_check=advance_local_authority)
        service = _service(database, client)
        with pytest.raises(RepositoryAccessChanged):
            service.resolve_and_persist_github_baseline(
                selection=_selection(),
                selector=_selector(),
                baseline_id=BASELINE_ID,
                decision_ids=(),
                observed_at=NOW,
            )
        assert client.repository_calls == 2
        assert client.events[-1] == "repository"
        assert load_artifact(database, ARTIFACT_ID) is None
        assert load_baseline(database, BASELINE_ID) is None


def test_all_provider_network_reads_finish_before_final_write_transaction() -> None:
    database, _ = _seed_database()

    def require_no_sqlite_write_transaction() -> None:
        assert database.connection.in_transaction is False

    with database:
        client = SequencedSnapshotClient(remote_guard=require_no_sqlite_write_transaction)
        service = _service(database, client)
        result = service.resolve_and_persist_github_baseline(
            selection=_selection(),
            selector=_selector(),
            baseline_id=BASELINE_ID,
            decision_ids=(),
            observed_at=NOW,
        )
        assert client.repository_calls == 2
        assert client.events[0] == "repository"
        assert client.events[-1] == "repository"
        assert result.commit.sha == COMMIT_SHA
        assert load_artifact(database, ARTIFACT_ID) is not None
        assert load_baseline(database, BASELINE_ID) is not None
