"""Provider-neutral errors for verified repository baseline resolution."""


class RepositoryBaselineError(RuntimeError):
    """Base error for Slice 1.2 verified repository baseline resolution."""


class RepositorySelectionInvalid(RepositoryBaselineError):
    """The requested repository/ref selection is structurally invalid."""


class RepositoryProjectMismatch(RepositoryBaselineError):
    """The selected repository does not match Relay project authority."""


class RepositoryAuthenticationFailed(RepositoryBaselineError):
    """Provider authentication failed during snapshot verification."""


class RepositoryAccessUnavailable(RepositoryBaselineError):
    """Provider access is unavailable for the selected repository."""


class RepositoryAccessChanged(RepositoryBaselineError):
    """Relay access authority changed while a baseline operation was in flight."""


class RepositoryRateLimited(RepositoryBaselineError):
    """Provider rate limiting prevented repository snapshot verification."""


class RepositoryRefNotFound(RepositoryBaselineError):
    """The explicitly selected branch, tag, or commit does not exist."""


class RepositorySnapshotUnavailable(RepositoryBaselineError):
    """Required commit/tree/blob data could not be obtained completely."""


class RepositorySnapshotIntegrityError(RepositoryBaselineError):
    """Remote snapshot evidence violates repository integrity requirements."""


class RepositoryProviderIdentityChanged(RepositoryBaselineError):
    """The live provider repository identity differs from the captured selection."""


class RepositoryBaselinePersistenceError(RepositoryBaselineError):
    """Verified Artifact/Baseline authority could not be persisted consistently."""
