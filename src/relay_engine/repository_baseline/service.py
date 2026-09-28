"""Orchestration for commit-pinned GitHub snapshot proof and Baseline persistence."""

from dataclasses import dataclass
from datetime import datetime

from relay_engine.domain.ids import BaselineId, DecisionId
from relay_engine.domain.references import CommitRef
from relay_engine.integrations.github import (
    GitHubAuthenticationError,
    GitHubClient,
    GitHubGitObjectType,
    GitHubIntegrationService,
    GitHubObjectUnavailable,
    GitHubPermissionError,
    GitHubRateLimited,
    GitHubRefNotFound,
    GitHubRemoteError,
    GitHubRepositoryAccessSelection,
    GitHubRepositorySnapshot,
    GitHubRepositoryUnavailable,
    GitHubTree,
    GitHubTreeEntry,
)
from relay_engine.persistence import RelayDatabase, load_project
from relay_engine.repository_baseline.errors import (
    RepositoryAccessUnavailable,
    RepositoryAuthenticationFailed,
    RepositoryProjectMismatch,
    RepositoryProviderIdentityChanged,
    RepositoryRateLimited,
    RepositoryRefNotFound,
    RepositorySnapshotIntegrityError,
    RepositorySnapshotUnavailable,
)
from relay_engine.repository_baseline.models import (
    RepositoryRevisionKind,
    RepositoryRevisionSelector,
    ResolvedBaselineResult,
)
from relay_engine.repository_baseline.persistence import persist_verified_baseline
from relay_engine.repository_contract import (
    ArtifactIntegrityError,
    RepositoryContractInvalid,
    RepositorySnapshotEntry,
    parse_repository_registry,
    validate_repository_snapshot,
)
from relay_engine.repository_contract.models import RepositoryRegistry


@dataclass(slots=True)
class _TreeWalker:
    client: GitHubClient
    token: object
    repository_path: str
    cache: dict[str, GitHubTree]

    def tree(self, tree_sha: str) -> GitHubTree:
        existing = self.cache.get(tree_sha)
        if existing is not None:
            return existing
        from relay_engine.integrations.github.models import GitHubInstallationToken

        if not isinstance(self.token, GitHubInstallationToken):
            raise RepositorySnapshotIntegrityError("invalid GitHub installation token value")
        tree = self.client.get_git_tree(
            token=self.token,
            repository_path=self.repository_path,
            tree_sha=tree_sha,
        )
        if tree.sha != tree_sha:
            raise RepositorySnapshotIntegrityError("GitHub tree response changed requested identity")
        if tree.truncated:
            raise RepositorySnapshotIntegrityError(
                "GitHub tree response is truncated and cannot prove a complete subtree"
            )
        self.cache[tree_sha] = tree
        return tree

    def resolve(self, root_tree_sha: str, path: str) -> GitHubTreeEntry:
        parts = path.split("/")
        current_sha = root_tree_sha
        for index, part in enumerate(parts):
            tree = self.tree(current_sha)
            entry = next((item for item in tree.entries if item.path == part), None)
            if entry is None:
                raise RepositorySnapshotIntegrityError(f"snapshot path is missing: {path}")
            if index == len(parts) - 1:
                return entry
            if entry.object_type is not GitHubGitObjectType.TREE or entry.mode != "040000":
                raise RepositorySnapshotIntegrityError(
                    f"snapshot path traverses a non-tree object: {path}"
                )
            current_sha = entry.sha
        raise RepositorySnapshotIntegrityError(f"snapshot path is invalid: {path}")


class RepositoryBaselineService:
    def __init__(
        self,
        *,
        database: RelayDatabase,
        github_integration: GitHubIntegrationService,
        github_client: GitHubClient,
    ) -> None:
        self._database = database
        self._github_integration = github_integration
        self._github_client = github_client

    def resolve_and_persist_github_baseline(
        self,
        *,
        selection: GitHubRepositoryAccessSelection,
        selector: RepositoryRevisionSelector,
        baseline_id: BaselineId,
        decision_ids: tuple[DecisionId, ...],
        observed_at: datetime,
    ) -> ResolvedBaselineResult:
        """Prove one GitHub snapshot, re-check local access, and persist immutable authority."""

        project = load_project(self._database, selection.project_id)
        if project is None:
            raise RepositoryProjectMismatch("Relay project does not exist")
        if project.primary_repository != selection.repository:
            raise RepositoryProjectMismatch(
                "captured GitHub selection differs from Project.primary_repository"
            )

        try:
            token = self._github_integration.create_repository_token(
                selection=selection, observed_at=observed_at
            )
            self._require_provider_identity(
                self._github_client.get_repository(
                    token=token,
                    repository_path=selection.repository.path,
                    observed_at=observed_at,
                ),
                selection,
            )
            provider_ref = self._provider_ref(selector)
            resolution = self._github_client.resolve_commit_sha(
                token=token,
                repository_path=selection.repository.path,
                ref=provider_ref,
            )
            if (
                selector.kind is RepositoryRevisionKind.COMMIT_SHA
                and resolution.sha != selector.value
            ):
                raise RepositorySnapshotIntegrityError(
                    "GitHub commit selector resolved to a different commit identity"
                )
            commit = CommitRef(repository=selection.repository, sha=resolution.sha)
            commit_object = self._github_client.get_git_commit(
                token=token,
                repository_path=selection.repository.path,
                sha=commit.sha,
            )
            if commit_object.sha != commit.sha:
                raise RepositorySnapshotIntegrityError(
                    "GitHub commit object changed the resolved commit identity"
                )
            registry = self._verify_snapshot(
                selection=selection,
                token=token,
                root_tree_sha=commit_object.tree_sha,
            )
            self._require_provider_identity(
                self._github_client.get_repository(
                    token=token,
                    repository_path=selection.repository.path,
                    observed_at=observed_at,
                ),
                selection,
            )
        except GitHubAuthenticationError as error:
            raise RepositoryAuthenticationFailed("GitHub authentication failed") from error
        except GitHubRateLimited as error:
            raise RepositoryRateLimited("GitHub rate limited snapshot verification") from error
        except GitHubRefNotFound as error:
            raise RepositoryRefNotFound("selected repository revision was not found") from error
        except GitHubRepositoryUnavailable as error:
            raise RepositoryAccessUnavailable("selected GitHub repository is unavailable") from error
        except GitHubPermissionError as error:
            raise RepositoryAccessUnavailable("selected GitHub repository is not readable") from error
        except GitHubObjectUnavailable as error:
            raise RepositorySnapshotUnavailable("required GitHub snapshot object is unavailable") from error
        except GitHubRemoteError as error:
            raise RepositorySnapshotUnavailable("GitHub snapshot verification failed") from error

        baseline = persist_verified_baseline(
            database=self._database,
            selection=selection,
            registry=registry,
            commit=commit,
            baseline_id=baseline_id,
            decision_ids=decision_ids,
        )
        return ResolvedBaselineResult(
            project_id=baseline.project_id,
            repository=selection.repository,
            selector=selector,
            commit=baseline.commit,
            baseline_id=baseline.id,
            artifact_ids=baseline.artifact_ids,
        )

    @staticmethod
    def _provider_ref(selector: RepositoryRevisionSelector) -> str:
        if selector.kind is RepositoryRevisionKind.BRANCH:
            return f"heads/{selector.value}"
        if selector.kind is RepositoryRevisionKind.TAG:
            return f"tags/{selector.value}"
        return selector.value

    @staticmethod
    def _require_provider_identity(
        repository: GitHubRepositorySnapshot,
        selection: GitHubRepositoryAccessSelection,
    ) -> None:
        if (
            repository.github_repository_id != selection.github_repository_id
            or repository.node_id != selection.github_node_id
            or repository.full_name != selection.repository.path
        ):
            raise RepositoryProviderIdentityChanged(
                "live GitHub repository identity differs from captured selection"
            )

    def _verify_snapshot(
        self,
        *,
        selection: GitHubRepositoryAccessSelection,
        token: object,
        root_tree_sha: str,
    ) -> RepositoryRegistry:
        from relay_engine.integrations.github.models import GitHubInstallationToken

        if not isinstance(token, GitHubInstallationToken):
            raise RepositorySnapshotIntegrityError("invalid GitHub installation token value")
        walker = _TreeWalker(
            client=self._github_client,
            token=token,
            repository_path=selection.repository.path,
            cache={},
        )
        try:
            relay_entry = walker.resolve(root_tree_sha, ".relay")
            if relay_entry.object_type is not GitHubGitObjectType.TREE or relay_entry.mode != "040000":
                raise RepositorySnapshotIntegrityError(".relay must be a real Git tree directory")
            relay_tree = walker.tree(relay_entry.sha)
            entries: list[RepositorySnapshotEntry] = []
            registry_raw: bytes | None = None
            for direct in relay_tree.entries:
                full_path = f".relay/{direct.path}"
                if direct.path == "registry.json" and direct.object_type is GitHubGitObjectType.BLOB:
                    blob = self._github_client.get_git_blob(
                        token=token,
                        repository_path=selection.repository.path,
                        blob_sha=direct.sha,
                    )
                    registry_raw = blob.raw_bytes
                    entries.append(
                        RepositorySnapshotEntry(
                            path=full_path,
                            mode=direct.mode,
                            object_type=direct.object_type.value,
                            tree_object_sha=direct.sha,
                            blob_object_sha=blob.sha,
                            raw_bytes=blob.raw_bytes,
                        )
                    )
                else:
                    entries.append(
                        RepositorySnapshotEntry(
                            path=full_path,
                            mode=direct.mode,
                            object_type=direct.object_type.value,
                            tree_object_sha=direct.sha,
                        )
                    )
            if registry_raw is None:
                raise RepositorySnapshotIntegrityError(".relay/registry.json is unavailable")
            preliminary = parse_repository_registry(registry_raw)
            if (
                preliminary.project_id != selection.project_id
                or preliminary.repository != selection.repository
            ):
                raise RepositoryProjectMismatch(
                    "repository registry identity differs from Relay project authority"
                )

            for revision in preliminary.artifacts:
                tree_entry = walker.resolve(root_tree_sha, revision.path)
                if tree_entry.object_type is GitHubGitObjectType.BLOB:
                    blob = self._github_client.get_git_blob(
                        token=token,
                        repository_path=selection.repository.path,
                        blob_sha=tree_entry.sha,
                    )
                    entries.append(
                        RepositorySnapshotEntry(
                            path=revision.path,
                            mode=tree_entry.mode,
                            object_type=tree_entry.object_type.value,
                            tree_object_sha=tree_entry.sha,
                            blob_object_sha=blob.sha,
                            raw_bytes=blob.raw_bytes,
                        )
                    )
                else:
                    entries.append(
                        RepositorySnapshotEntry(
                            path=revision.path,
                            mode=tree_entry.mode,
                            object_type=tree_entry.object_type.value,
                            tree_object_sha=tree_entry.sha,
                        )
                    )
            return validate_repository_snapshot(
                registry_raw=registry_raw,
                entries=tuple(entries),
                expected_project_id=selection.project_id,
                expected_repository=selection.repository,
            )
        except RepositoryProjectMismatch:
            raise
        except (RepositoryContractInvalid, ArtifactIntegrityError, ValueError) as error:
            raise RepositorySnapshotIntegrityError(
                "commit-pinned repository snapshot violates Relay repository authority"
            ) from error
