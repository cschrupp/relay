"""Verified provider-neutral repository baseline resolution for Relay Slice 1.2."""

from relay_engine.repository_baseline.errors import (
    RepositoryAccessChanged,
    RepositoryAccessUnavailable,
    RepositoryAuthenticationFailed,
    RepositoryBaselineError,
    RepositoryBaselinePersistenceError,
    RepositoryProjectMismatch,
    RepositoryProviderIdentityChanged,
    RepositoryRateLimited,
    RepositoryRefNotFound,
    RepositorySelectionInvalid,
    RepositorySnapshotIntegrityError,
    RepositorySnapshotUnavailable,
)
from relay_engine.repository_baseline.models import (
    RepositoryRevisionKind,
    RepositoryRevisionSelector,
    ResolvedBaselineResult,
)
from relay_engine.repository_baseline.persistence import persist_verified_baseline
from relay_engine.repository_baseline.service import RepositoryBaselineService

__all__ = [
    "RepositoryAccessChanged",
    "RepositoryAccessUnavailable",
    "RepositoryAuthenticationFailed",
    "RepositoryBaselineError",
    "RepositoryBaselinePersistenceError",
    "RepositoryBaselineService",
    "RepositoryProjectMismatch",
    "RepositoryProviderIdentityChanged",
    "RepositoryRateLimited",
    "RepositoryRefNotFound",
    "RepositoryRevisionKind",
    "RepositoryRevisionSelector",
    "RepositorySelectionInvalid",
    "RepositorySnapshotIntegrityError",
    "RepositorySnapshotUnavailable",
    "ResolvedBaselineResult",
    "persist_verified_baseline",
]
