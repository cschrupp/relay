"""Immutable schema-v1 models for Relay's repository-side canonical registry."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from relay_engine.domain import ArtifactId, CommitRef, ContentDigest, ProjectId, RepositoryRef
from relay_engine.domain._base import (
    DomainModel,
    require_nonblank,
    require_repository_relative_path,
)

type CanonicalKey = Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]


class RepositoryArtifactClass(StrEnum):
    WORKING = "WORKING"
    LOCKABLE_RECORD = "LOCKABLE_RECORD"
    LIVING_PROJECTION = "LIVING_PROJECTION"
    IMMUTABLE_RECORD = "IMMUTABLE_RECORD"


class RepositoryArtifactState(StrEnum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    LOCKED = "LOCKED"
    SUPERSEDED = "SUPERSEDED"
    CURRENT = "CURRENT"
    IMMUTABLE = "IMMUTABLE"


class ArtifactRevisionRef(DomainModel):
    """Reference to one exact registry artifact identity and revision."""

    artifact_id: ArtifactId
    revision: int = Field(ge=1)


class RepositoryArtifactRevision(DomainModel):
    """One exact repository-contract revision, without a core Artifact commit binding."""

    artifact_id: ArtifactId
    revision: int = Field(ge=1)
    title: str
    artifact_type: str = Field(min_length=1, max_length=128)
    artifact_class: RepositoryArtifactClass
    artifact_state: RepositoryArtifactState
    path: str = Field(min_length=1)
    content_digest: ContentDigest
    human_version: str | None = None
    updated_at: datetime
    scope: str
    supersedes: ArtifactRevisionRef | None = None
    superseded_by: ArtifactRevisionRef | None = None

    @field_validator("title", "artifact_type", "scope")
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("human_version")
    @classmethod
    def optional_version_is_nonblank(cls, value: str | None) -> str | None:
        return None if value is None else require_nonblank(value)

    @field_validator("path")
    @classmethod
    def path_is_safe_relative_posix(cls, value: str) -> str:
        checked = require_repository_relative_path(value)
        if checked == ".relay/registry.json":
            raise ValueError("the registry cannot register itself")
        return checked

    @field_validator("updated_at")
    @classmethod
    def timestamp_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("updated_at must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def state_matches_class_and_lineage(self) -> RepositoryArtifactRevision:
        allowed = {
            RepositoryArtifactClass.WORKING: {
                RepositoryArtifactState.DRAFT,
                RepositoryArtifactState.REVIEW,
            },
            RepositoryArtifactClass.LOCKABLE_RECORD: {
                RepositoryArtifactState.DRAFT,
                RepositoryArtifactState.REVIEW,
                RepositoryArtifactState.LOCKED,
                RepositoryArtifactState.SUPERSEDED,
            },
            RepositoryArtifactClass.LIVING_PROJECTION: {RepositoryArtifactState.CURRENT},
            RepositoryArtifactClass.IMMUTABLE_RECORD: {
                RepositoryArtifactState.IMMUTABLE,
                RepositoryArtifactState.SUPERSEDED,
            },
        }
        if self.artifact_state not in allowed[self.artifact_class]:
            raise ValueError("artifact state is not valid for its class")
        historical = self.artifact_class in {
            RepositoryArtifactClass.LOCKABLE_RECORD,
            RepositoryArtifactClass.IMMUTABLE_RECORD,
        }
        if historical and (self.artifact_state is RepositoryArtifactState.SUPERSEDED) != (
            self.superseded_by is not None
        ):
            raise ValueError("historical SUPERSEDED state and successor reference must agree")
        if not historical and (self.supersedes is not None or self.superseded_by is not None):
            raise ValueError("only historical artifact classes can have supersession links")
        if self.supersedes is not None and self.artifact_state not in {
            RepositoryArtifactState.LOCKED,
            RepositoryArtifactState.SUPERSEDED,
            RepositoryArtifactState.IMMUTABLE,
        }:
            raise ValueError("only mature historical records can supersede another revision")
        if (
            self.supersedes is not None
            and self.artifact_class is RepositoryArtifactClass.LOCKABLE_RECORD
            and (
                self.artifact_state
                not in {RepositoryArtifactState.LOCKED, RepositoryArtifactState.SUPERSEDED}
            )
        ):
            raise ValueError("lockable supersession records must be LOCKED or SUPERSEDED")
        if (
            self.supersedes is not None
            and self.artifact_class is RepositoryArtifactClass.IMMUTABLE_RECORD
            and (
                self.artifact_state
                not in {RepositoryArtifactState.IMMUTABLE, RepositoryArtifactState.SUPERSEDED}
            )
        ):
            raise ValueError("immutable supersession records must be IMMUTABLE or SUPERSEDED")
        if self.supersedes is not None and self.supersedes.artifact_id == self.artifact_id:
            raise ValueError("an artifact revision cannot supersede itself")
        if self.superseded_by is not None and self.superseded_by.artifact_id == self.artifact_id:
            raise ValueError("an artifact revision cannot name itself as successor")
        if self.supersedes == self.superseded_by and self.supersedes is not None:
            raise ValueError("an artifact revision cannot point both ways to the same revision")
        return self


class CanonicalPointer(DomainModel):
    """Explicit semantic pointer from one stable key to one exact revision."""

    canonical_key: CanonicalKey
    target: ArtifactRevisionRef


class RepositoryRegistry(DomainModel):
    """The complete schema-v1 repository artifact and canonical-pointer contract."""

    schema_version: Literal[1] = 1
    project_id: ProjectId
    repository: RepositoryRef
    artifacts: tuple[RepositoryArtifactRevision, ...]
    canonical: tuple[CanonicalPointer, ...]

    @model_validator(mode="after")
    def registry_invariants(self) -> RepositoryRegistry:
        artifacts = self.artifacts
        canonical = self.canonical
        artifact_order = tuple(sorted(artifacts, key=lambda item: (item.path, item.artifact_id)))
        if artifacts != artifact_order:
            raise ValueError("artifacts must use normative (path, artifact_id) ordering")
        if canonical != tuple(sorted(canonical, key=lambda item: item.canonical_key)):
            raise ValueError("canonical pointers must use canonical_key ordering")

        ids = tuple(item.artifact_id for item in artifacts)
        paths = tuple(item.path for item in artifacts)
        keys = tuple(item.canonical_key for item in canonical)
        if len(ids) != len(set(ids)):
            raise ValueError("artifact IDs must be unique")
        if len(paths) != len(set(paths)):
            raise ValueError("artifact paths must be unique")
        if len(keys) != len(set(keys)):
            raise ValueError("canonical keys must be unique")

        by_id = {item.artifact_id: item for item in artifacts}
        for item in artifacts:
            predecessor = by_id.get(item.supersedes.artifact_id) if item.supersedes else None
            successor = by_id.get(item.superseded_by.artifact_id) if item.superseded_by else None
            if item.supersedes is not None:
                if predecessor is None or _revision_ref(predecessor) != item.supersedes:
                    raise ValueError("supersedes must reference an exact registered revision")
                if predecessor.superseded_by != _revision_ref(item):
                    raise ValueError("supersession links must be reciprocal")
                _require_lineage_compatibility(predecessor, item)
            if item.superseded_by is not None:
                if successor is None or _revision_ref(successor) != item.superseded_by:
                    raise ValueError("superseded_by must reference an exact registered revision")
                if successor.supersedes != _revision_ref(item):
                    raise ValueError("supersession links must be reciprocal")
                _require_lineage_compatibility(item, successor)

        _reject_supersession_cycles(artifacts, by_id)
        for pointer in canonical:
            target = by_id.get(pointer.target.artifact_id)
            if target is None or _revision_ref(target) != pointer.target:
                raise ValueError("canonical pointer must target an exact registered revision")
            if not _is_canonical_target(target):
                raise ValueError("canonical pointer target must be CURRENT, LOCKED, or IMMUTABLE")
        return self


class ResolvedRepositoryArtifact(DomainModel):
    """Exact registry revision plus the explicitly supplied observation commit."""

    canonical_key: CanonicalKey | None = None
    revision: RepositoryArtifactRevision
    observed_at_commit: CommitRef
    canonical_status: Literal["CURRENT"] | None = None


def _revision_ref(value: RepositoryArtifactRevision) -> ArtifactRevisionRef:
    return ArtifactRevisionRef(artifact_id=value.artifact_id, revision=value.revision)


def _require_lineage_compatibility(
    predecessor: RepositoryArtifactRevision, successor: RepositoryArtifactRevision
) -> None:
    if predecessor.artifact_class is not successor.artifact_class:
        raise ValueError("supersession cannot change artifact class")
    if predecessor.artifact_type != successor.artifact_type:
        raise ValueError("supersession cannot change artifact type")
    if successor.revision != predecessor.revision + 1:
        raise ValueError("successor revision must increment by exactly one")
    if predecessor.artifact_class is RepositoryArtifactClass.LOCKABLE_RECORD:
        allowed = {RepositoryArtifactState.LOCKED, RepositoryArtifactState.SUPERSEDED}
    else:
        allowed = {RepositoryArtifactState.IMMUTABLE, RepositoryArtifactState.SUPERSEDED}
    if successor.artifact_state not in allowed:
        raise ValueError("historical successor has insufficient maturity")


def _is_canonical_target(value: RepositoryArtifactRevision) -> bool:
    return (
        (
            value.artifact_class is RepositoryArtifactClass.LIVING_PROJECTION
            and value.artifact_state is RepositoryArtifactState.CURRENT
        )
        or (
            value.artifact_class is RepositoryArtifactClass.LOCKABLE_RECORD
            and value.artifact_state is RepositoryArtifactState.LOCKED
        )
        or (
            value.artifact_class is RepositoryArtifactClass.IMMUTABLE_RECORD
            and value.artifact_state is RepositoryArtifactState.IMMUTABLE
        )
    )


def _reject_supersession_cycles(
    artifacts: tuple[RepositoryArtifactRevision, ...],
    by_id: dict[str, RepositoryArtifactRevision],
) -> None:
    for artifact in artifacts:
        seen: set[str] = set()
        current = artifact
        while True:
            if current.artifact_id in seen:
                raise ValueError("supersession lineage cannot contain a cycle")
            seen.add(current.artifact_id)
            if current.superseded_by is None:
                break
            current = by_id[current.superseded_by.artifact_id]
