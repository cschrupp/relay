"""Immutable governance evidence records stored by Slice 0.5."""

from datetime import UTC, datetime

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import (
    BaselineId,
    EventId,
    ExecutionId,
    GateEvaluationRecordId,
    HandoverGateId,
    SliceId,
)
from relay_engine.domain.references import ActorRef
from relay_engine.governance.models import (
    GateEvaluation,
    GateRevisionRef,
    HandoverContext,
)


class GateEvaluationRecord(DomainModel):
    """Exact immutable basis and complete output for one gate evaluation."""

    id: GateEvaluationRecordId
    recorded_at: datetime
    gate_refs: tuple[GateRevisionRef, ...]
    context: HandoverContext
    evaluations: tuple[GateEvaluation, ...]

    @field_validator("recorded_at")
    @classmethod
    def timestamp_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("recorded_at must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def evidence_is_complete_and_canonical(self) -> GateEvaluationRecord:
        gate_ids = tuple(item.gate_id for item in self.gate_refs)
        if (
            not gate_ids
            or gate_ids != tuple(sorted(gate_ids))
            or len(gate_ids) != len(set(gate_ids))
        ):
            raise ValueError("gate_refs must be non-empty, unique, and sorted by gate_id")

        evaluation_ids = tuple(item.gate_id for item in self.evaluations)
        if (
            not evaluation_ids
            or evaluation_ids != tuple(sorted(evaluation_ids))
            or evaluation_ids != gate_ids
        ):
            raise ValueError("evaluations must match the complete canonical gate_refs set")

        by_gate = {item.gate_id: item for item in self.evaluations}
        for reference in self.gate_refs:
            evaluation = by_gate[reference.gate_id]
            if (
                evaluation.gate_revision != reference.gate_revision
                or evaluation.baseline_id != self.context.baseline_id
                or evaluation.lifecycle_revision != self.context.lifecycle.revision
                or evaluation.governance_revision != self.context.governance_revision
                or evaluation.slice_id != self.context.lifecycle.slice_id
            ):
                raise ValueError("evaluation does not match its exact persisted context and gate")
        return self


class ExecutionRecord(DomainModel):
    """Minimal immutable commit record for one governed lifecycle movement."""

    execution_id: ExecutionId
    gate_evaluation_record_id: GateEvaluationRecordId
    slice_id: SliceId
    baseline_id: BaselineId
    selected_gate_id: HandoverGateId
    selected_gate_revision: int = Field(ge=1)
    source_lifecycle_revision: int = Field(ge=0)
    resulting_lifecycle_revision: int = Field(ge=1)
    event_id: EventId
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
    def revision_advances_once(self) -> ExecutionRecord:
        if self.resulting_lifecycle_revision != self.source_lifecycle_revision + 1:
            raise ValueError("execution must advance lifecycle revision exactly once")
        return self


__all__ = ["ExecutionRecord", "GateEvaluationRecord"]
