"""Typed immutable subjects and deterministic Slice 1.7 projections."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import (
    BaselineId,
    EvidenceId,
    ExecutionId,
    GateEvaluationRecordId,
    HumanDecisionId,
    ManualEvaluationId,
    SliceId,
    SliceResultId,
)
from relay_engine.domain.models import Baseline, Evidence
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.governance.models import (
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateRevisionRef,
    HumanApprovalDecision,
    QualityCheckResult,
    RiskStatus,
    ToolchainChangeStatus,
)


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(UTC)


class SliceResultRecord(DomainModel):
    """Append-only identity for one exact, verified Slice result commit."""

    schema_version: Literal[1] = 1
    result_id: SliceResultId
    slice_id: SliceId
    slice_definition_revision: int = Field(ge=1)
    source_baseline_id: BaselineId
    result_baseline_id: BaselineId
    lifecycle_revision: int = Field(ge=0)
    supersedes_result_id: SliceResultId | None = None
    recorded_by: ActorRef
    recorded_at: datetime
    reason: str

    @field_validator("recorded_by")
    @classmethod
    def result_requires_human(cls, value: ActorRef) -> ActorRef:
        if value.kind is not ActorKind.HUMAN:
            raise ValueError("Slice result attachment requires a HUMAN actor")
        return value

    @field_validator("recorded_at")
    @classmethod
    def timestamp_is_aware_utc(cls, value: datetime) -> datetime:
        return _aware_utc(value)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class EvaluationEvidenceSubmission(DomainModel):
    """Caller-owned Evidence identity, claim, and time; actor/commit are derived."""

    evidence_id: EvidenceId
    claim: str
    recorded_at: datetime

    @field_validator("claim")
    @classmethod
    def claim_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("recorded_at")
    @classmethod
    def timestamp_is_aware_utc(cls, value: datetime) -> datetime:
        return _aware_utc(value)


class ManualEvaluationRecord(DomainModel):
    """Append-only Human-authored assessment of one exact Slice result."""

    schema_version: Literal[1] = 1
    evaluation_id: ManualEvaluationId
    slice_id: SliceId
    result_id: SliceResultId
    result_baseline_id: BaselineId
    source_baseline_id: BaselineId
    slice_definition_revision: int = Field(ge=1)
    lifecycle_revision: int = Field(ge=0)
    gate_refs: tuple[GateRevisionRef, ...]
    prior_gate_evaluation_record_id: GateEvaluationRecordId | None
    supersedes_evaluation_id: ManualEvaluationId | None = None
    evaluator: ActorRef
    evaluated_at: datetime
    outcome: EvaluationOutcome
    evidence_ids: tuple[EvidenceId, ...]
    quality_checks: tuple[QualityCheckResult, ...] = ()
    change_surface_status: ChangeSurfaceStatus
    risk_status: RiskStatus
    toolchain_change_status: ToolchainChangeStatus
    findings: tuple[str, ...] = ()
    summary: str

    @field_validator("evaluator")
    @classmethod
    def evaluator_is_human(cls, value: ActorRef) -> ActorRef:
        if value.kind is not ActorKind.HUMAN:
            raise ValueError("manual evaluation requires a HUMAN evaluator")
        return value

    @field_validator("evaluated_at")
    @classmethod
    def evaluation_time_is_aware_utc(cls, value: datetime) -> datetime:
        return _aware_utc(value)

    @field_validator("summary")
    @classmethod
    def summary_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("findings")
    @classmethod
    def findings_are_nonblank(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            require_nonblank(item)
        return value

    @field_validator("evidence_ids")
    @classmethod
    def evidence_ids_are_canonical(cls, value: tuple[EvidenceId, ...]) -> tuple[EvidenceId, ...]:
        if not value or value != tuple(sorted(set(value))):
            raise ValueError("evidence_ids must be non-empty, unique, and sorted")
        return value

    @field_validator("gate_refs")
    @classmethod
    def gate_refs_are_canonical(
        cls, value: tuple[GateRevisionRef, ...]
    ) -> tuple[GateRevisionRef, ...]:
        ids = tuple(item.gate_id for item in value)
        if not ids or ids != tuple(sorted(ids)) or len(ids) != len(set(ids)):
            raise ValueError("gate_refs must be non-empty, unique, and sorted by gate_id")
        return value

    @field_validator("quality_checks")
    @classmethod
    def quality_checks_are_canonical(
        cls, value: tuple[QualityCheckResult, ...]
    ) -> tuple[QualityCheckResult, ...]:
        keys = tuple(item.key for item in value)
        if keys != tuple(sorted(set(keys))):
            raise ValueError("quality_checks must be unique and sorted by key")
        return value


class ManualEvaluationActionKind(StrEnum):
    """Fixed server-rendered controls for the bounded Slice 1.7 seam."""

    ATTACH_RESULT = "ATTACH_RESULT"
    EVALUATE = "EVALUATE"
    TECHNICAL_ACCEPT = "TECHNICAL_ACCEPT"
    TECHNICAL_REJECT = "TECHNICAL_REJECT"
    PROMOTE_ACCEPTED = "PROMOTE_ACCEPTED"


class ManualEvaluationActionBasis(DomainModel):
    """CAS values rendered for Slice 1.7 forms."""

    slice_id: SliceId
    lifecycle_revision: int = Field(ge=0)
    slice_definition_revision: int = Field(ge=1)
    current_result_id: SliceResultId | None = None
    current_manual_evaluation_id: ManualEvaluationId | None = None
    latest_gate_evaluation_record_id: GateEvaluationRecordId | None = None
    gate_refs: tuple[GateRevisionRef, ...] = ()


class AcceptedSliceResult(DomainModel):
    """Accepted result reconstructed from immutable records and execution causality."""

    slice_id: SliceId
    result_id: SliceResultId
    result_baseline_id: BaselineId
    commit: str
    manual_evaluation_id: ManualEvaluationId
    human_approval_decision_id: HumanDecisionId
    accepted_execution_id: ExecutionId
    accepted_at: datetime

    @field_validator("accepted_at")
    @classmethod
    def accepted_time_is_aware_utc(cls, value: datetime) -> datetime:
        return _aware_utc(value)


class DevelopmentMemoryProjection(DomainModel):
    """Deterministic derived engineering history; never persisted or materialized."""

    slice_id: SliceId
    source_baseline: Baseline
    result_history: tuple[SliceResultRecord, ...]
    evaluation_history: tuple[ManualEvaluationRecord, ...]
    evidence: tuple[Evidence, ...]
    accepted_results: tuple[AcceptedSliceResult, ...]


class ManualEvaluationProjection(DomainModel):
    """Current and historical Slice 1.7 state projected from durable Relay records."""

    action_basis: ManualEvaluationActionBasis | None = None
    actions: tuple[ManualEvaluationActionKind, ...] = ()
    technical_gate_refs: tuple[GateRevisionRef, ...] = ()
    promotable_gate_refs: tuple[GateRevisionRef, ...] = ()
    current_result: SliceResultRecord | None = None
    current_result_baseline: Baseline | None = None
    result_history: tuple[SliceResultRecord, ...] = ()
    current_evaluation: ManualEvaluationRecord | None = None
    evaluation_history: tuple[ManualEvaluationRecord, ...] = ()
    current_technical_decision: HumanApprovalDecision | None = None
    accepted_result: AcceptedSliceResult | None = None
    accepted_results: tuple[AcceptedSliceResult, ...] = ()
    development_memory: DevelopmentMemoryProjection | None = None


__all__ = [
    "AcceptedSliceResult",
    "DevelopmentMemoryProjection",
    "EvaluationEvidenceSubmission",
    "ManualEvaluationActionBasis",
    "ManualEvaluationActionKind",
    "ManualEvaluationProjection",
    "ManualEvaluationRecord",
    "SliceResultRecord",
]
