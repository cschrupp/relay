"""Typed fail-closed outcomes for repository initialization and synchronization."""


class RepositorySyncError(RuntimeError):
    """Base class for bounded repository-sync failures."""


class RepositorySyncInvalidRemote(RepositorySyncError):
    """The existing .relay contract or repository snapshot is invalid."""


class RepositorySyncConflict(RepositorySyncError):
    """The requested target cannot safely follow the exact captured repository head."""


class RepositorySyncWritePermissionRequired(RepositorySyncError):
    """The installation does not have the exact accepted WRITE profile."""


class RepositorySyncAccessChanged(RepositorySyncError):
    """Local installation, repository membership, or state revision changed."""


class RepositorySyncProviderIdentityChanged(RepositorySyncError):
    """The observed provider repository no longer matches the captured repository."""


class RepositorySyncDefaultBranchChanged(RepositorySyncError):
    """The provider-reported default branch changed during the operation."""


class RepositorySyncNoDefaultHead(RepositorySyncError):
    """Slice 1.3 does not create the first branch/ref of an empty repository."""


class RepositorySyncAuthorizationRequired(RepositorySyncError):
    """No HUMAN authorization exists for the exact prepared subject."""


class RepositorySyncAuthorizationStale(RepositorySyncError):
    """The persisted HUMAN authorization does not match the recomputed subject."""


class RepositorySyncWorkflowMutationUnsupported(RepositorySyncError):
    """Contents-only repository tokens cannot create or change workflow files."""


class RepositorySyncProtectedBranch(RepositorySyncError):
    """GitHub rejected the non-force update under branch protection or rules."""


class RepositorySyncRefUpdateNotVisible(RepositorySyncError):
    """An indeterminate ref update was observed not to have moved the branch."""

    def __init__(self, message: str, created_commit_sha: str) -> None:
        super().__init__(message)
        self.created_commit_sha = created_commit_sha


class RepositorySyncSnapshotIntegrityError(RepositorySyncError):
    """The exact visible or proposed repository snapshot failed verification."""


class RepositorySyncPostWriteVerificationError(RepositorySyncError):
    """Post-write verification failed or the ref outcome remains ambiguous."""

    def __init__(self, message: str, created_commit_sha: str) -> None:
        super().__init__(message)
        self.created_commit_sha = created_commit_sha


__all__ = [
    "RepositorySyncAccessChanged",
    "RepositorySyncAuthorizationRequired",
    "RepositorySyncAuthorizationStale",
    "RepositorySyncConflict",
    "RepositorySyncDefaultBranchChanged",
    "RepositorySyncError",
    "RepositorySyncInvalidRemote",
    "RepositorySyncNoDefaultHead",
    "RepositorySyncPostWriteVerificationError",
    "RepositorySyncProtectedBranch",
    "RepositorySyncProviderIdentityChanged",
    "RepositorySyncRefUpdateNotVisible",
    "RepositorySyncSnapshotIntegrityError",
    "RepositorySyncWorkflowMutationUnsupported",
    "RepositorySyncWritePermissionRequired",
]
