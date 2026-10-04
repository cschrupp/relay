"""Immutable presentation values for the read-only Relay board."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator

from relay_engine.domain._base import DomainModel
from relay_engine.domain.ids import (
    BaselineId,
    GateEvaluationRecordId,
    HandoverGateId,
    SliceId,
)
from relay_engine.domain.models import Baseline, Project
from relay_engine.governance.models import (
    GateReason,
    HandoverGate,
    HandoverPolicy,
    TrafficLight,
)
from relay_engine.human_control.models import HumanActionProjection
from relay_engine.lifecycle.models import LifecyclePhase, LifecycleValidity, SliceLifecycle
from relay_engine.persistence.records import ExecutionRecord, GateEvaluationRecord
from relay_engine.project_slice.models import SliceDefinitionSnapshot


class BoardLane(StrEnum):
    """One of the six fixed, presentation-only lifecycle groupings."""

    NOT_STARTED = "NOT_STARTED"
    SHAPING = "SHAPING"
    READY = "READY"
    DELIVERY = "DELIVERY"
    EVALUATION = "EVALUATION"
    TERMINAL = "TERMINAL"


class EvaluationBasisStatus(StrEnum):
    """Structural relationship between the latest observation and durable state."""

    MATCHING_DURABLE_BASIS = "MATCHING_DURABLE_BASIS"
    STALE_DURABLE_BASIS = "STALE_DURABLE_BASIS"
    NOT_EVALUATED = "NOT_EVALUATED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ProjectSummary(DomainModel):
    """A current Project definition and its verified current Slice count."""

    project: Project
    definition_revision: int = Field(ge=1)
    slice_count: int = Field(ge=0)


class DependencyProjection(DomainModel):
    """Read-only relationship facts for a parent or dependency Slice."""

    slice_id: SliceId
    title: str | None
    lifecycle_phase: LifecyclePhase | None
    lifecycle_validity: LifecycleValidity | None


class GateProjection(DomainModel):
    """One current outgoing gate definition with an optional durable observation."""

    gate_id: HandoverGateId
    gate_revision: int = Field(ge=1)
    target_phase: LifecyclePhase
    policy: HandoverPolicy
    hard_stop: bool
    authorization_required: bool
    baseline_id: BaselineId
    evaluation_light: TrafficLight | None
    evaluation_reasons: tuple[GateReason, ...]
    evaluation_basis_status: EvaluationBasisStatus


class SliceCard(DomainModel):
    """Compact read-only Slice projection for one board lane."""

    slice_id: SliceId
    title: str
    definition_revision: int = Field(ge=1)
    parent_slice_id: SliceId | None
    dependency_ids: tuple[SliceId, ...]
    lane: BoardLane
    lifecycle: SliceLifecycle | None
    dependencies: tuple[DependencyProjection, ...]
    outgoing_gates: tuple[GateProjection, ...]
    latest_evaluation_record_id: GateEvaluationRecordId | None
    latest_evaluation_recorded_at: datetime | None
    evaluation_basis_status: EvaluationBasisStatus

    @field_validator("latest_evaluation_recorded_at")
    @classmethod
    def timestamp_is_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("evaluation timestamp must be timezone-aware")
        return value


class ProjectBoard(DomainModel):
    """All current Slices for one Project, grouped by fixed display lanes."""

    project: Project
    project_definition_revision: int = Field(ge=1)
    lanes: tuple[BoardLane, ...]
    cards: tuple[SliceCard, ...]

    @field_validator("lanes")
    @classmethod
    def lanes_are_fixed_and_ordered(cls, value: tuple[BoardLane, ...]) -> tuple[BoardLane, ...]:
        if value != tuple(BoardLane):
            raise ValueError("ProjectBoard lanes must use the fixed board order")
        return value


class BoardProjection(DomainModel):
    """Verified Project summaries for the board index route."""

    projects: tuple[ProjectSummary, ...]


class SliceDetail(DomainModel):
    """Full read-only definition, governance provenance, and advisory Human controls."""

    project: Project
    project_definition_revision: int = Field(ge=1)
    slice_definition: SliceDefinitionSnapshot
    lifecycle: SliceLifecycle | None
    parent: DependencyProjection | None
    children: tuple[DependencyProjection, ...]
    dependencies: tuple[DependencyProjection, ...]
    outgoing_gate_definitions: tuple[HandoverGate, ...]
    outgoing_gates: tuple[GateProjection, ...]
    latest_evaluation_observation: GateEvaluationRecord | None
    evaluation_basis_status: EvaluationBasisStatus
    baseline: Baseline | None
    evaluation_baseline: Baseline | None
    relevant_execution_records: tuple[ExecutionRecord, ...]
    human_actions: HumanActionProjection = Field(default_factory=HumanActionProjection)


__all__ = [
    "BoardLane",
    "BoardProjection",
    "DependencyProjection",
    "EvaluationBasisStatus",
    "GateProjection",
    "ProjectBoard",
    "ProjectSummary",
    "SliceCard",
    "SliceDetail",
]
