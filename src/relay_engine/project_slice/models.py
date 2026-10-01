"""Immutable service and audit values for Project/Slice definition administration."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import ProjectId, SliceId
from relay_engine.domain.models import Project, Slice
from relay_engine.domain.references import ActorKind, ActorRef


class DefinitionOperation(StrEnum):
    SEED = "SEED"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class MutationMetadata(DomainModel):
    """Required human provenance for one durable definition mutation."""

    actor: ActorRef
    occurred_at: datetime
    reason: str

    @field_validator("occurred_at")
    @classmethod
    def timestamp_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def actor_is_human(self) -> MutationMetadata:
        if self.actor.kind is not ActorKind.HUMAN:
            raise ValueError("definition mutations require a HUMAN actor")
        return self


class ProjectDefinitionSnapshot(DomainModel):
    value: Project
    definition_revision: int = Field(ge=1)


class SliceDefinitionSnapshot(DomainModel):
    value: Slice
    definition_revision: int = Field(ge=1)


class ProjectDefinitionRevision(DomainModel):
    project_id: ProjectId
    definition_revision: int = Field(ge=1)
    operation: DefinitionOperation
    payload: Project | None
    mutation: MutationMetadata | None = None

    @model_validator(mode="after")
    def payload_matches_operation(self) -> ProjectDefinitionRevision:
        if (self.operation is DefinitionOperation.DELETE) != (self.payload is None):
            raise ValueError(
                "DELETE revisions require null payload; other revisions require Project"
            )
        if self.payload is not None and self.payload.id != self.project_id:
            raise ValueError("Project revision payload identity mismatch")
        if (self.operation is DefinitionOperation.SEED) != (self.mutation is None):
            raise ValueError("SEED revisions alone omit human mutation metadata")
        return self


class SliceDefinitionRevision(DomainModel):
    slice_id: SliceId
    project_id: ProjectId
    definition_revision: int = Field(ge=1)
    operation: DefinitionOperation
    payload: Slice | None
    mutation: MutationMetadata | None = None

    @model_validator(mode="after")
    def payload_matches_operation(self) -> SliceDefinitionRevision:
        if (self.operation is DefinitionOperation.DELETE) != (self.payload is None):
            raise ValueError("DELETE revisions require null payload; other revisions require Slice")
        if self.payload is not None and (
            self.payload.id != self.slice_id or self.payload.project_id != self.project_id
        ):
            raise ValueError("Slice revision payload identity mismatch")
        if (self.operation is DefinitionOperation.SEED) != (self.mutation is None):
            raise ValueError("SEED revisions alone omit human mutation metadata")
        return self


class ProjectMutationResult(DomainModel):
    snapshot: ProjectDefinitionSnapshot
    changed: bool


class SliceMutationResult(DomainModel):
    snapshot: SliceDefinitionSnapshot
    changed: bool


class ProjectDeleteResult(DomainModel):
    project_id: ProjectId
    definition_revision: int = Field(ge=1)
    deleted: bool
    already_deleted: bool

    @model_validator(mode="after")
    def result_is_unambiguous(self) -> ProjectDeleteResult:
        if self.deleted == self.already_deleted:
            raise ValueError("exactly one of deleted and already_deleted must be true")
        return self


class SliceDeleteResult(DomainModel):
    slice_id: SliceId
    definition_revision: int = Field(ge=1)
    deleted: bool
    already_deleted: bool

    @model_validator(mode="after")
    def result_is_unambiguous(self) -> SliceDeleteResult:
        if self.deleted == self.already_deleted:
            raise ValueError("exactly one of deleted and already_deleted must be true")
        return self


__all__ = [
    "DefinitionOperation",
    "MutationMetadata",
    "ProjectDefinitionRevision",
    "ProjectDefinitionSnapshot",
    "ProjectDeleteResult",
    "ProjectMutationResult",
    "SliceDefinitionRevision",
    "SliceDefinitionSnapshot",
    "SliceDeleteResult",
    "SliceMutationResult",
]
