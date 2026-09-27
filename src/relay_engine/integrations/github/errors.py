"""Provider-specific GitHub integration errors with secret-safe context."""


class GitHubIntegrationError(RuntimeError):
    """Base error for the GitHub App integration boundary."""


class GitHubAuthenticationError(GitHubIntegrationError):
    """GitHub rejected app or installation authentication."""


class GitHubInstallationUnavailable(GitHubIntegrationError):
    """The requested installation is unavailable or no longer exists."""


class GitHubPermissionError(GitHubIntegrationError):
    """The observed GitHub grant violates or lacks required permissions."""


class GitHubRepositoryAccessDenied(GitHubIntegrationError):
    """A repository is not accessible through the selected installation."""


class GitHubRateLimited(GitHubIntegrationError):
    """GitHub rate limiting prevented the requested operation."""


class GitHubWebhookInvalid(GitHubIntegrationError):
    """A webhook failed signature, envelope, or supported-event validation."""


class GitHubRemoteError(GitHubIntegrationError):
    """GitHub returned an unexpected remote error."""


class GitHubIntegrationIntegrityError(GitHubIntegrationError):
    """Stored or delivered GitHub integration state violates invariants."""


class GitHubIntegrationConcurrencyConflict(GitHubIntegrationError):
    """Local GitHub integration state changed during an in-flight operation."""
