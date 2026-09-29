"""Exact-subject initialization and synchronization of Relay's repository contract."""

from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from relay_engine.repository_sync.service import RepositorySyncService


def __getattr__(name: str) -> object:
    if name == "RepositorySyncService":
        from relay_engine.repository_sync.service import RepositorySyncService

        return RepositorySyncService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ArtifactWriteDigest",
    "RepositoryArtifactWrite",
    "RepositoryContractState",
    "RepositoryMutationAuthorization",
    "RepositorySyncAccessChanged",
    "RepositorySyncAuthorizationRequired",
    "RepositorySyncAuthorizationStale",
    "RepositorySyncConflict",
    "RepositorySyncDefaultBranchChanged",
    "RepositorySyncError",
    "RepositorySyncInvalidRemote",
    "RepositorySyncNoDefaultHead",
    "RepositorySyncPostWriteVerificationError",
    "RepositorySyncPreparation",
    "RepositorySyncProtectedBranch",
    "RepositorySyncProviderIdentityChanged",
    "RepositorySyncRefUpdateNotVisible",
    "RepositorySyncRequest",
    "RepositorySyncResult",
    "RepositorySyncService",
    "RepositorySyncSnapshotIntegrityError",
    "RepositorySyncSubjectV1",
    "RepositorySyncWorkflowMutationUnsupported",
    "RepositorySyncWritePermissionRequired",
    "artifact_write_digest",
    "repository_registry_digest",
    "repository_sync_subject_digest",
]
