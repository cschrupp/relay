"""Strict provider-specific values for the GitHub App integration."""

import re
from datetime import datetime
from enum import StrEnum

from pydantic import Field, SecretStr, field_validator, model_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import ProjectId, RepositoryId
from relay_engine.domain.references import RepositoryRef


class GitHubPermissionLevel(StrEnum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class GitHubAccountType(StrEnum):
    USER = "User"
    ORGANIZATION = "Organization"
    ENTERPRISE = "Enterprise"


class GitHubRepositorySelectionMode(StrEnum):
    ALL = "all"
    SELECTED = "selected"


class GitHubInstallationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class GitHubAccessReadiness(StrEnum):
    READY = "READY"
    RESYNC_REQUIRED = "RESYNC_REQUIRED"
    PERMISSION_POLICY_VIOLATION = "PERMISSION_POLICY_VIOLATION"


class GitHubInstallationEventType(StrEnum):
    INSTALLATION_SYNCED = "INSTALLATION_SYNCED"
    PERMISSIONS_CHANGED = "PERMISSIONS_CHANGED"
    REPOSITORIES_CHANGED = "REPOSITORIES_CHANGED"
    SUSPENDED = "SUSPENDED"
    UNSUSPENDED = "UNSUSPENDED"
    DELETED = "DELETED"


class GitHubGitObjectType(StrEnum):
    BLOB = "blob"
    TREE = "tree"
    COMMIT = "commit"


def _canonical_git_sha(value: str) -> str:
    if re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value) is None:
        raise ValueError("Git object SHA must be canonical full lowercase hex")
    return value


class GitHubPermissionGrant(DomainModel):
    name: str = Field(min_length=1)
    level: GitHubPermissionLevel

    @field_validator("name")
    @classmethod
    def name_is_canonical(cls, value: str) -> str:
        require_nonblank(value)
        if value != value.lower() or not re.fullmatch(r"[a-z][a-z0-9_]*", value):
            raise ValueError("permission name must be canonical lowercase GitHub permission text")
        return value


class GitHubInstallationSnapshot(DomainModel):
    project_id: ProjectId
    installation_id: int = Field(gt=0)
    app_id: int = Field(gt=0)
    account_id: int = Field(gt=0)
    account_login: str = Field(min_length=1)
    account_type: GitHubAccountType
    repository_selection: GitHubRepositorySelectionMode
    status: GitHubInstallationStatus
    permissions: tuple[GitHubPermissionGrant, ...]
    observed_at: datetime

    @field_validator("account_login")
    @classmethod
    def login_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("permissions")
    @classmethod
    def permissions_are_unique_and_sorted(
        cls, value: tuple[GitHubPermissionGrant, ...]
    ) -> tuple[GitHubPermissionGrant, ...]:
        names = tuple(item.name for item in value)
        if len(names) != len(set(names)):
            raise ValueError("permission names must be unique")
        if names != tuple(sorted(names)):
            raise ValueError("permissions must be sorted by name")
        return value

    @field_validator("observed_at")
    @classmethod
    def observed_at_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value


class GitHubInstallationState(DomainModel):
    installation: GitHubInstallationSnapshot
    readiness: GitHubAccessReadiness
    state_revision: int = Field(ge=1)

    @model_validator(mode="after")
    def ready_requires_active(self) -> GitHubInstallationState:
        if (
            self.readiness is GitHubAccessReadiness.READY
            and self.installation.status is not GitHubInstallationStatus.ACTIVE
        ):
            raise ValueError("only an active installation may be READY")
        return self

    @property
    def project_id(self) -> ProjectId:
        return self.installation.project_id

    @property
    def installation_id(self) -> int:
        return self.installation.installation_id

    @property
    def usable(self) -> bool:
        return (
            self.installation.status is GitHubInstallationStatus.ACTIVE
            and self.readiness is GitHubAccessReadiness.READY
        )


class GitHubRepositorySnapshot(DomainModel):
    github_repository_id: int = Field(gt=0)
    node_id: str = Field(min_length=1)
    full_name: str = Field(min_length=3)
    owner_login: str = Field(min_length=1)
    private: bool
    archived: bool
    default_branch: str = Field(min_length=1)
    observed_at: datetime

    @field_validator("node_id", "owner_login", "default_branch")
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("full_name")
    @classmethod
    def full_name_is_repository_path(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
            raise ValueError("full_name must be canonical owner/repository text")
        return value

    @field_validator("observed_at")
    @classmethod
    def repository_observed_at_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value


class GitHubRepositoryAccessSelection(DomainModel):
    """Ephemeral provider evidence captured from one usable Slice-1.1 binding."""

    project_id: ProjectId
    installation_id: int = Field(gt=0)
    github_repository_id: int = Field(gt=0)
    github_node_id: str = Field(min_length=1)
    repository: RepositoryRef
    expected_state_revision: int = Field(ge=1)

    @field_validator("github_node_id")
    @classmethod
    def node_id_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def repository_is_public_github(self) -> GitHubRepositoryAccessSelection:
        if self.repository.host != "github.com":
            raise ValueError("Slice 1.2 GitHub selection requires github.com RepositoryRef")
        return self


class GitHubCommitResolution(DomainModel):
    sha: str

    @field_validator("sha")
    @classmethod
    def sha_is_canonical(cls, value: str) -> str:
        return _canonical_git_sha(value)


class GitHubCommitObject(DomainModel):
    sha: str
    tree_sha: str

    @field_validator("sha", "tree_sha")
    @classmethod
    def sha_is_canonical(cls, value: str) -> str:
        return _canonical_git_sha(value)


class GitHubTreeEntry(DomainModel):
    path: str = Field(min_length=1)
    mode: str = Field(min_length=1)
    object_type: GitHubGitObjectType
    sha: str

    @field_validator("path", "mode")
    @classmethod
    def tree_text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("sha")
    @classmethod
    def sha_is_canonical(cls, value: str) -> str:
        return _canonical_git_sha(value)


class GitHubTree(DomainModel):
    sha: str
    entries: tuple[GitHubTreeEntry, ...]
    truncated: bool

    @field_validator("sha")
    @classmethod
    def sha_is_canonical(cls, value: str) -> str:
        return _canonical_git_sha(value)

    @field_validator("entries")
    @classmethod
    def paths_are_unique(cls, value: tuple[GitHubTreeEntry, ...]) -> tuple[GitHubTreeEntry, ...]:
        paths = tuple(item.path for item in value)
        if len(paths) != len(set(paths)):
            raise ValueError("GitHub tree paths must be unique")
        return value


class GitHubBlob(DomainModel):
    sha: str
    raw_bytes: bytes

    @field_validator("sha")
    @classmethod
    def sha_is_canonical(cls, value: str) -> str:
        return _canonical_git_sha(value)


class GitHubInstallationEvent(DomainModel):
    event_id: str = Field(min_length=1)
    project_id: ProjectId
    installation_id: int = Field(gt=0)
    event_type: GitHubInstallationEventType
    observed_at: datetime
    prior_state_revision: int = Field(ge=0)
    resulting_state_revision: int = Field(ge=1)
    delivery_id: str | None = None
    delivery_digest: str | None = None

    @field_validator("event_id")
    @classmethod
    def event_id_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("observed_at")
    @classmethod
    def event_time_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value

    @field_validator("delivery_id")
    @classmethod
    def delivery_id_is_nonblank(cls, value: str | None) -> str | None:
        return None if value is None else require_nonblank(value)

    @field_validator("delivery_digest")
    @classmethod
    def delivery_digest_is_sha256(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
            raise ValueError("delivery_digest must be canonical sha256 text")
        return value

    @model_validator(mode="after")
    def delivery_fields_are_paired(self) -> GitHubInstallationEvent:
        if (self.delivery_id is None) != (self.delivery_digest is None):
            raise ValueError("delivery_id and delivery_digest must appear together")
        if self.resulting_state_revision != self.prior_state_revision + 1:
            raise ValueError("state-changing event must advance revision by exactly one")
        return self


class GitHubWebhookEnvelope(DomainModel):
    event_name: str = Field(min_length=1)
    delivery_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    installation_id: int = Field(gt=0)
    repository_ids: tuple[int, ...] = ()
    permissions: tuple[GitHubPermissionGrant, ...] = ()

    @field_validator("event_name", "delivery_id", "action")
    @classmethod
    def envelope_text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("repository_ids")
    @classmethod
    def repository_ids_are_unique_sorted(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if any(item <= 0 for item in value):
            raise ValueError("repository IDs must be positive")
        if value != tuple(sorted(set(value))):
            raise ValueError("repository IDs must be unique and sorted")
        return value

    @field_validator("permissions")
    @classmethod
    def envelope_permissions_are_sorted(
        cls, value: tuple[GitHubPermissionGrant, ...]
    ) -> tuple[GitHubPermissionGrant, ...]:
        names = tuple(item.name for item in value)
        if len(names) != len(set(names)) or names != tuple(sorted(names)):
            raise ValueError("webhook permissions must be unique and sorted")
        return value


class GitHubAppConfig(DomainModel):
    client_id: str = Field(min_length=1)
    api_base_url: str = "https://api.github.com"
    api_version: str = "2026-03-10"
    user_agent: str = "relay-engine"
    request_timeout_seconds: float = Field(default=10.0, gt=0, le=120)

    @field_validator("client_id", "api_version", "user_agent")
    @classmethod
    def config_text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("api_base_url")
    @classmethod
    def api_base_is_public_github(cls, value: str) -> str:
        if value != "https://api.github.com":
            raise ValueError("Slice 1.1 supports only the public GitHub API")
        return value


class GitHubSecretConfig(DomainModel):
    private_key_pem: SecretStr
    webhook_secret: SecretStr


class GitHubInstallationToken(DomainModel):
    token: SecretStr
    expires_at: datetime

    @field_validator("expires_at")
    @classmethod
    def expiration_is_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("expires_at must be timezone-aware")
        return value


def repository_ref_from_github(
    *,
    relay_repository_id: RepositoryId,
    state: GitHubInstallationState,
    repository: GitHubRepositorySnapshot,
    current_repositories: tuple[GitHubRepositorySnapshot, ...],
) -> RepositoryRef:
    """Convert one confirmed usable GitHub repository to provider-neutral identity."""

    if not state.usable:
        raise ValueError("GitHub installation is not ACTIVE / READY")
    if repository.github_repository_id not in {
        item.github_repository_id for item in current_repositories
    }:
        raise ValueError("repository is not in the confirmed current installation set")
    return RepositoryRef(id=relay_repository_id, host="github.com", path=repository.full_name)
