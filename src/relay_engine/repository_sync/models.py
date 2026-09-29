"""Immutable values for exact-subject repository synchronization."""

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator, model_validator

from relay_engine.domain import (
    ActorKind,
    ActorRef,
    CommitRef,
    ContentDigest,
    ProjectId,
    RepositoryMutationAuthorizationId,
    RepositoryRef,
)
from relay_engine.domain._base import (
    DomainModel,
    require_nonblank,
    require_repository_relative_path,
)
from relay_engine.integrations.github.models import GitHubRepositoryAccessSelection
from relay_engine.repository_contract.models import RepositoryRegistry


class RepositoryContractState(StrEnum):
    """Classification of one exact default-branch repository snapshot."""

    UNINITIALIZED = "UNINITIALIZED"
    CURRENT = "CURRENT"
    SYNCHRONIZABLE = "SYNCHRONIZABLE"
    CONFLICT = "CONFLICT"
    INVALID = "INVALID"


class RepositoryArtifactWrite(DomainModel):
    """Caller-supplied bytes for one registered target artifact path."""

    path: str
    raw_bytes: bytes

    @field_validator("path")
    @classmethod
    def path_is_safe_and_not_registry_metadata(cls, value: str) -> str:
        checked = require_repository_relative_path(value)
        if checked == ".relay" or checked.startswith(".relay/"):
            raise ValueError("caller artifact writes cannot target .relay paths")
        return checked


class ArtifactWriteDigest(DomainModel):
    """Canonical path and raw-byte digest included in Human Authority scope."""

    path: str
    content_digest: ContentDigest

    @field_validator("path")
    @classmethod
    def path_is_safe(cls, value: str) -> str:
        return require_repository_relative_path(value)


class RepositorySyncSubjectV1(DomainModel):
    """Deterministic, exact mutation subject approved by Human Authority."""

    schema_version: Literal[1] = 1
    project_id: ProjectId
    repository: RepositoryRef
    installation_id: int = Field(gt=0)
    github_repository_id: int = Field(gt=0)
    github_node_id: str
    expected_state_revision: int = Field(ge=1)
    expected_default_branch: str
    expected_base_commit: CommitRef
    target_registry_digest: ContentDigest
    artifact_write_digests: tuple[ArtifactWriteDigest, ...]

    @field_validator("github_node_id", "expected_default_branch")
    @classmethod
    def required_text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("expected_default_branch")
    @classmethod
    def branch_name_is_safe_for_ref_path(cls, value: str) -> str:
        if (
            value.startswith("/")
            or value.endswith("/")
            or "//" in value
            or ".." in value
            or "@{" in value
            or any(character.isspace() or ord(character) < 32 for character in value)
            or any(character in value for character in "~^:?*[\\")
            or any(part.startswith(".") or part.endswith(".lock") for part in value.split("/"))
        ):
            raise ValueError("default branch is not a safe Git ref name")
        return value

    @field_validator("artifact_write_digests")
    @classmethod
    def writes_are_unique_and_canonical(
        cls, value: tuple[ArtifactWriteDigest, ...]
    ) -> tuple[ArtifactWriteDigest, ...]:
        paths = tuple(item.path for item in value)
        if paths != tuple(sorted(set(paths))):
            raise ValueError("artifact write digests must be unique and ordered by path")
        return value

    @model_validator(mode="after")
    def commit_uses_subject_repository(self) -> RepositorySyncSubjectV1:
        if self.expected_base_commit.repository != self.repository:
            raise ValueError("expected base commit must use the subject RepositoryRef")
        return self


class RepositorySyncRequest(DomainModel):
    """Exact target contract and expected existing default-branch base."""

    selection: GitHubRepositoryAccessSelection
    expected_default_branch: str
    expected_base_commit: CommitRef
    target_registry: RepositoryRegistry
    artifact_writes: tuple[RepositoryArtifactWrite, ...]
    authorization_id: RepositoryMutationAuthorizationId | None = None

    @field_validator("expected_default_branch")
    @classmethod
    def expected_branch_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("artifact_writes")
    @classmethod
    def write_paths_are_unique(cls, value: tuple[RepositoryArtifactWrite, ...]):
        paths = tuple(item.path for item in value)
        if len(paths) != len(set(paths)):
            raise ValueError("artifact write paths must be unique")
        return value

    @model_validator(mode="after")
    def request_identities_are_exact(self) -> RepositorySyncRequest:
        if self.expected_base_commit.repository != self.selection.repository:
            raise ValueError("expected base commit repository must equal selection repository")
        if (
            self.target_registry.project_id != self.selection.project_id
            or self.target_registry.repository != self.selection.repository
        ):
            raise ValueError("target registry identity must equal the captured selection")
        return self


class RepositorySyncPreparation(DomainModel):
    """Read-only evidence describing a no-op or exact Human Authority subject."""

    state: RepositoryContractState
    prior_commit: CommitRef
    subject: RepositorySyncSubjectV1 | None = None
    subject_digest: ContentDigest | None = None
    changed_paths: tuple[str, ...] = ()

    @field_validator("changed_paths")
    @classmethod
    def changed_paths_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("changed_paths must be unique and ordered by path")
        return value

    @model_validator(mode="after")
    def subject_matches_state(self) -> RepositorySyncPreparation:
        has_subject = self.subject is not None and self.subject_digest is not None
        if self.state is RepositoryContractState.CURRENT:
            if has_subject or self.changed_paths:
                raise ValueError("CURRENT preparation cannot carry mutation authority")
        elif self.state is RepositoryContractState.SYNCHRONIZABLE:
            if not has_subject or self.subject is None or self.subject_digest is None:
                raise ValueError("SYNCHRONIZABLE preparation requires an exact subject")
            if repository_sync_subject_digest(self.subject) != self.subject_digest:
                raise ValueError("preparation digest does not match its exact subject")
        else:
            if has_subject:
                raise ValueError("non-executable classification cannot carry a mutation subject")
        return self


class RepositoryMutationAuthorization(DomainModel):
    """Immutable Human Authority approval for one exact repository-sync subject."""

    authorization_id: RepositoryMutationAuthorizationId
    project_id: ProjectId
    subject_schema_version: Literal[1] = 1
    subject: RepositorySyncSubjectV1
    subject_digest: ContentDigest
    actor: ActorRef
    granted_at: datetime
    reason: str

    @field_validator("granted_at")
    @classmethod
    def grant_time_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("granted_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def authorization_is_exact_human_approval(self) -> RepositoryMutationAuthorization:
        if self.actor.kind is not ActorKind.HUMAN:
            raise ValueError("repository mutation authorization requires a HUMAN actor")
        if self.subject.project_id != self.project_id:
            raise ValueError("authorization project does not match its subject")
        if self.subject_schema_version != self.subject.schema_version:
            raise ValueError("authorization subject schema version does not match its subject")
        if self.subject_digest != repository_sync_subject_digest(self.subject):
            raise ValueError("authorization digest does not match its exact subject")
        return self


class RepositorySyncResult(DomainModel):
    """Verified synchronization evidence; success never persists a Baseline."""

    state: Literal[RepositoryContractState.CURRENT] = RepositoryContractState.CURRENT
    prior_commit: CommitRef
    resulting_commit: CommitRef
    wrote_remote: bool

    @model_validator(mode="after")
    def commit_identity_matches_visibility(self) -> RepositorySyncResult:
        if self.prior_commit.repository != self.resulting_commit.repository:
            raise ValueError("prior and resulting commit repositories must match")
        if self.wrote_remote == (self.prior_commit.sha == self.resulting_commit.sha):
            raise ValueError("wrote_remote must distinguish no-op from mutation")
        return self


def repository_registry_digest(registry: RepositoryRegistry) -> ContentDigest:
    """SHA-256 of the exact deterministic schema-v1 registry bytes."""

    from relay_engine.repository_contract.registry import serialize_repository_registry

    return _sha256_digest(serialize_repository_registry(registry))


def repository_sync_subject_digest(subject: RepositorySyncSubjectV1) -> ContentDigest:
    """SHA-256 of canonical JSON bytes for the complete typed subject."""

    raw = json.dumps(
        subject.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256_digest(raw)


def artifact_write_digest(raw_bytes: bytes) -> ContentDigest:
    return _sha256_digest(raw_bytes)


def _sha256_digest(raw: bytes) -> ContentDigest:
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


__all__ = [
    "ArtifactWriteDigest",
    "RepositoryArtifactWrite",
    "RepositoryContractState",
    "RepositoryMutationAuthorization",
    "RepositorySyncPreparation",
    "RepositorySyncRequest",
    "RepositorySyncResult",
    "RepositorySyncSubjectV1",
    "artifact_write_digest",
    "repository_registry_digest",
    "repository_sync_subject_digest",
]
