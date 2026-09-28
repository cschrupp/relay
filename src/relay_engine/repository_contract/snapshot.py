"""Pure validation of commit-pinned repository snapshot entries."""

import hashlib
import re
from dataclasses import dataclass

from relay_engine.domain import ProjectId, RepositoryRef
from relay_engine.domain._base import require_repository_relative_path
from relay_engine.repository_contract.errors import (
    ArtifactIntegrityError,
    RepositoryContractInvalid,
)
from relay_engine.repository_contract.models import RepositoryArtifactRevision, RepositoryRegistry
from relay_engine.repository_contract.registry import parse_repository_registry

_SHA_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_REGULAR_MODES = frozenset({"100644", "100755"})


@dataclass(frozen=True, slots=True)
class RepositorySnapshotEntry:
    """One tree-selected path plus optional exact blob evidence."""

    path: str
    mode: str
    object_type: str
    tree_object_sha: str
    blob_object_sha: str | None = None
    raw_bytes: bytes | None = None

    def __post_init__(self) -> None:
        require_repository_relative_path(self.path)
        if not self.mode or not self.object_type:
            raise ValueError("snapshot entry mode and object type must be nonblank")
        if _SHA_PATTERN.fullmatch(self.tree_object_sha) is None:
            raise ValueError("tree object SHA must be canonical full lowercase hex")
        if (
            self.blob_object_sha is not None
            and _SHA_PATTERN.fullmatch(self.blob_object_sha) is None
        ):
            raise ValueError("blob object SHA must be canonical full lowercase hex")
        if (self.blob_object_sha is None) != (self.raw_bytes is None):
            raise ValueError("blob object SHA and raw bytes must appear together")


def validate_repository_snapshot(
    *,
    registry_raw: bytes,
    entries: tuple[RepositorySnapshotEntry, ...],
    expected_project_id: ProjectId,
    expected_repository: RepositoryRef,
) -> RepositoryRegistry:
    """Validate exact tree/blob evidence with the accepted repository-contract semantics."""

    paths = tuple(item.path for item in entries)
    if len(paths) != len(set(paths)):
        raise RepositoryContractInvalid("snapshot paths must be unique")
    by_path = {item.path: item for item in entries}

    direct_relay_entries = tuple(
        sorted(path for path in paths if path.startswith(".relay/") and path.count("/") == 1)
    )
    if direct_relay_entries != (".relay/registry.json",):
        raise RepositoryContractInvalid("schema v1 permits only .relay/registry.json")

    registry_entry = by_path.get(".relay/registry.json")
    if registry_entry is None:
        raise RepositoryContractInvalid(".relay/registry.json is required")
    _require_regular_blob(registry_entry, ".relay/registry.json")
    if registry_entry.raw_bytes != registry_raw:
        raise RepositoryContractInvalid("registry bytes disagree with tree-selected blob evidence")

    registry = parse_repository_registry(registry_raw)
    if registry.project_id != expected_project_id:
        raise RepositoryContractInvalid("registry project identity does not match expected project")
    if registry.repository != expected_repository:
        raise RepositoryContractInvalid("registry RepositoryRef does not match expected repository")

    for artifact in registry.artifacts:
        entry = by_path.get(artifact.path)
        if entry is None:
            raise ArtifactIntegrityError(f"registered artifact is missing: {artifact.path}")
        _verify_artifact_entry(entry, artifact)
    return registry


def _require_regular_blob(entry: RepositorySnapshotEntry, path: str) -> None:
    if entry.object_type != "blob" or entry.mode not in _REGULAR_MODES:
        raise ArtifactIntegrityError(f"registered artifact is not a regular file: {path}")
    if entry.raw_bytes is None or entry.blob_object_sha is None:
        raise ArtifactIntegrityError(f"registered artifact bytes are unavailable: {path}")
    if entry.blob_object_sha != entry.tree_object_sha:
        raise ArtifactIntegrityError(f"registered artifact blob SHA mismatch: {path}")


def _verify_artifact_entry(
    entry: RepositorySnapshotEntry,
    artifact: RepositoryArtifactRevision,
) -> None:
    _require_regular_blob(entry, artifact.path)
    assert entry.raw_bytes is not None
    digest = f"sha256:{hashlib.sha256(entry.raw_bytes).hexdigest()}"
    if digest != artifact.content_digest:
        raise ArtifactIntegrityError(f"registered artifact digest mismatch: {artifact.path}")
