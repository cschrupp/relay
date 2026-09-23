"""Stable Relay engineering-domain vocabulary for Slice 0.2."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import (
    DomainModel,
    require_nonblank,
    require_repository_relative_path,
)
from relay_engine.domain.ids import (
    ArtifactId,
    BaselineId,
    DecisionId,
    EvidenceId,
    ProjectId,
    SliceId,
)
from relay_engine.domain.references import ActorRef, CommitRef, RepositoryRef

type ContentDigest = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]


class Project(DomainModel):
    """Engineering project with one primary repository."""

    id: ProjectId
    name: str = Field(min_length=1)
    primary_repository: RepositoryRef

    @field_validator("name")
    @classmethod
    def name_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class Baseline(DomainModel):
    """Exact code commit plus authoritative artifact and decision references."""

    id: BaselineId
    project_id: ProjectId
    commit: CommitRef
    artifact_ids: tuple[ArtifactId, ...]
    decision_ids: tuple[DecisionId, ...]

    @field_validator("artifact_ids", "decision_ids")
    @classmethod
    def references_are_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("authority references must be unique")
        return value


class ScopeSpec(DomainModel):
    """Ordered in-scope and out-of-scope statements."""

    in_scope: tuple[str, ...]
    out_of_scope: tuple[str, ...]

    @field_validator("in_scope", "out_of_scope")
    @classmethod
    def statements_are_nonblank(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for statement in value:
            require_nonblank(statement)
        return value


class AcceptanceCriterion(DomainModel):
    """One named, required-or-optional acceptance item."""

    key: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    required: bool

    @field_validator("key", "statement")
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class Slice(DomainModel):
    """Bounded intended engineering change; intentionally has no workflow state."""

    id: SliceId
    project_id: ProjectId
    title: str = Field(min_length=1)
    scope: ScopeSpec
    acceptance_criteria: tuple[AcceptanceCriterion, ...]
    parent_slice_id: SliceId | None = None
    dependency_ids: tuple[SliceId, ...] = ()

    @field_validator("title")
    @classmethod
    def title_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("acceptance_criteria")
    @classmethod
    def acceptance_keys_are_unique(
        cls, value: tuple[AcceptanceCriterion, ...]
    ) -> tuple[AcceptanceCriterion, ...]:
        keys = tuple(criterion.key for criterion in value)
        if len(keys) != len(set(keys)):
            raise ValueError("acceptance criterion keys must be unique")
        return value

    @field_validator("dependency_ids")
    @classmethod
    def dependencies_are_unique(cls, value: tuple[SliceId, ...]) -> tuple[SliceId, ...]:
        if len(value) != len(set(value)):
            raise ValueError("slice dependencies must be unique")
        return value

    @model_validator(mode="after")
    def slice_does_not_reference_itself(self) -> Slice:
        if self.parent_slice_id == self.id:
            raise ValueError("slice cannot be its own parent")
        if self.id in self.dependency_ids:
            raise ValueError("slice cannot depend on itself")
        return self


class Artifact(DomainModel):
    """Durable engineering artifact with safe path and immutable provenance."""

    id: ArtifactId
    artifact_type: str = Field(min_length=1, max_length=128)
    path: str = Field(min_length=1)
    commit: CommitRef
    content_digest: ContentDigest

    @field_validator("artifact_type")
    @classmethod
    def artifact_type_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("path")
    @classmethod
    def path_is_repository_relative(cls, value: str) -> str:
        return require_repository_relative_path(value)


class DecisionStatus(StrEnum):
    PROPOSED = "PROPOSED"
    LOCKED = "LOCKED"
    SUPERSEDED = "SUPERSEDED"


class Decision(DomainModel):
    """Durable engineering judgment with explicit historical supersession links."""

    id: DecisionId
    title: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    status: DecisionStatus
    supersedes_id: DecisionId | None = None
    superseded_by_id: DecisionId | None = None

    @field_validator("title", "statement")
    @classmethod
    def decision_text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def supersession_links_are_consistent(self) -> Decision:
        if self.supersedes_id == self.id or self.superseded_by_id == self.id:
            raise ValueError("decision cannot supersede itself")
        if self.supersedes_id is not None and self.supersedes_id == self.superseded_by_id:
            raise ValueError("decision cannot supersede and be superseded by the same decision")
        if (self.status is DecisionStatus.SUPERSEDED) != (self.superseded_by_id is not None):
            raise ValueError(
                "SUPERSEDED decisions require superseded_by_id; other statuses forbid it"
            )
        return self


class Evidence(DomainModel):
    """Claim-support record with actor, time, and exact repository provenance."""

    id: EvidenceId
    claim: str = Field(min_length=1)
    recorded_by: ActorRef
    recorded_at: datetime
    source_commit: CommitRef

    @field_validator("claim")
    @classmethod
    def claim_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("recorded_at")
    @classmethod
    def timestamp_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("recorded_at must be timezone-aware")
        return value.astimezone(UTC)


__all__ = [
    "AcceptanceCriterion",
    "Artifact",
    "Baseline",
    "ContentDigest",
    "Decision",
    "DecisionStatus",
    "Evidence",
    "Project",
    "ScopeSpec",
    "Slice",
]
