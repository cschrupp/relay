"""Immutable governance policy, current facts, and derived evaluations."""

import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import (
    ArtifactId,
    AuthorizationId,
    BaselineId,
    EvidenceId,
    HandoverGateId,
    HumanDecisionId,
    SliceId,
)
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.lifecycle.models import LifecyclePhase, SliceLifecycle

type StableKey = Annotated[str, Field(pattern=r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")]


class TrafficLight(StrEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class HandoverPolicy(StrEnum):
    AUTO = "AUTO"
    AUTO_NOTIFY = "AUTO_NOTIFY"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    HUMAN_CHOICE = "HUMAN_CHOICE"


class ReviewPolicy(StrEnum):
    ALLOW = "ALLOW"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    BLOCK = "BLOCK"


class EvaluationOutcome(StrEnum):
    ACCEPT = "ACCEPT"
    REWORK = "REWORK"
    ESCALATE_CONTRACT = "ESCALATE_CONTRACT"
    ESCALATE_ARCHITECTURE = "ESCALATE_ARCHITECTURE"
    BLOCKED = "BLOCKED"
    EXPERIMENT_REQUIRED = "EXPERIMENT_REQUIRED"


class QualityCheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"


class ChangeSurfaceStatus(StrEnum):
    WITHIN_DECLARED = "WITHIN_DECLARED"
    MATERIAL_DEVIATION = "MATERIAL_DEVIATION"


class RiskStatus(StrEnum):
    CLEAR = "CLEAR"
    FLAGGED = "FLAGGED"


class ToolchainChangeStatus(StrEnum):
    NONE = "NONE"
    AUTHORIZED = "AUTHORIZED"
    UNAUTHORIZED = "UNAUTHORIZED"


class HumanApprovalValue(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class GateReasonKind(StrEnum):
    BLOCKING = "BLOCKING"
    HUMAN_ACTION = "HUMAN_ACTION"


class GateReasonCode(StrEnum):
    BASELINE_MISMATCH = "BASELINE_MISMATCH"
    SOURCE_PHASE_MISMATCH = "SOURCE_PHASE_MISMATCH"
    INVALID_LIFECYCLE_TRANSITION = "INVALID_LIFECYCLE_TRANSITION"
    MISSING_REQUIRED_ARTIFACT = "MISSING_REQUIRED_ARTIFACT"
    MISSING_REQUIRED_EVIDENCE = "MISSING_REQUIRED_EVIDENCE"
    DEPENDENCY_MISSING = "DEPENDENCY_MISSING"
    DEPENDENCY_NOT_ACCEPTED = "DEPENDENCY_NOT_ACCEPTED"
    DEPENDENCY_STALE = "DEPENDENCY_STALE"
    EVALUATION_REQUIRED = "EVALUATION_REQUIRED"
    EVALUATION_OUTCOME_NOT_ALLOWED = "EVALUATION_OUTCOME_NOT_ALLOWED"
    QUALITY_CHECK_MISSING = "QUALITY_CHECK_MISSING"
    QUALITY_CHECK_FAILED = "QUALITY_CHECK_FAILED"
    CHANGE_SURFACE_BLOCKED = "CHANGE_SURFACE_BLOCKED"
    CHANGE_SURFACE_REVIEW_REQUIRED = "CHANGE_SURFACE_REVIEW_REQUIRED"
    RISK_BLOCKED = "RISK_BLOCKED"
    RISK_REVIEW_REQUIRED = "RISK_REVIEW_REQUIRED"
    UNAUTHORIZED_TOOLCHAIN_CHANGE = "UNAUTHORIZED_TOOLCHAIN_CHANGE"
    AUTHORIZATION_REQUIRED = "AUTHORIZATION_REQUIRED"
    AUTHORIZATION_STALE = "AUTHORIZATION_STALE"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    HUMAN_CHOICE_REQUIRED = "HUMAN_CHOICE_REQUIRED"
    HUMAN_DECISION_STALE = "HUMAN_DECISION_STALE"
    HARD_STOP_REQUIRES_HUMAN = "HARD_STOP_REQUIRES_HUMAN"
    HUMAN_REJECTED = "HUMAN_REJECTED"
    NOT_SELECTED_BY_HUMAN = "NOT_SELECTED_BY_HUMAN"
    MULTIPLE_EXECUTABLE_PATHS = "MULTIPLE_EXECUTABLE_PATHS"


_REASON_KINDS: dict[GateReasonCode, GateReasonKind] = {
    code: GateReasonKind.BLOCKING
    for code in (
        GateReasonCode.BASELINE_MISMATCH,
        GateReasonCode.SOURCE_PHASE_MISMATCH,
        GateReasonCode.INVALID_LIFECYCLE_TRANSITION,
        GateReasonCode.MISSING_REQUIRED_ARTIFACT,
        GateReasonCode.MISSING_REQUIRED_EVIDENCE,
        GateReasonCode.DEPENDENCY_MISSING,
        GateReasonCode.DEPENDENCY_NOT_ACCEPTED,
        GateReasonCode.DEPENDENCY_STALE,
        GateReasonCode.EVALUATION_REQUIRED,
        GateReasonCode.EVALUATION_OUTCOME_NOT_ALLOWED,
        GateReasonCode.QUALITY_CHECK_MISSING,
        GateReasonCode.QUALITY_CHECK_FAILED,
        GateReasonCode.CHANGE_SURFACE_BLOCKED,
        GateReasonCode.RISK_BLOCKED,
        GateReasonCode.UNAUTHORIZED_TOOLCHAIN_CHANGE,
        GateReasonCode.HUMAN_REJECTED,
        GateReasonCode.NOT_SELECTED_BY_HUMAN,
        GateReasonCode.MULTIPLE_EXECUTABLE_PATHS,
    )
}
_REASON_KINDS.update(
    {
        code: GateReasonKind.HUMAN_ACTION
        for code in (
            GateReasonCode.CHANGE_SURFACE_REVIEW_REQUIRED,
            GateReasonCode.RISK_REVIEW_REQUIRED,
            GateReasonCode.AUTHORIZATION_REQUIRED,
            GateReasonCode.AUTHORIZATION_STALE,
            GateReasonCode.HUMAN_APPROVAL_REQUIRED,
            GateReasonCode.HUMAN_CHOICE_REQUIRED,
            GateReasonCode.HUMAN_DECISION_STALE,
            GateReasonCode.HARD_STOP_REQUIRES_HUMAN,
        )
    }
)
_SUBJECT_REQUIRED = {
    GateReasonCode.MISSING_REQUIRED_ARTIFACT,
    GateReasonCode.MISSING_REQUIRED_EVIDENCE,
    GateReasonCode.DEPENDENCY_MISSING,
    GateReasonCode.DEPENDENCY_NOT_ACCEPTED,
    GateReasonCode.DEPENDENCY_STALE,
    GateReasonCode.QUALITY_CHECK_MISSING,
    GateReasonCode.QUALITY_CHECK_FAILED,
    GateReasonCode.AUTHORIZATION_STALE,
    GateReasonCode.HUMAN_DECISION_STALE,
    GateReasonCode.HUMAN_REJECTED,
    GateReasonCode.NOT_SELECTED_BY_HUMAN,
    GateReasonCode.MULTIPLE_EXECUTABLE_PATHS,
}
_SUBJECT_PREFIX = {
    GateReasonCode.MISSING_REQUIRED_ARTIFACT: "art_",
    GateReasonCode.MISSING_REQUIRED_EVIDENCE: "evd_",
    GateReasonCode.DEPENDENCY_MISSING: "slc_",
    GateReasonCode.DEPENDENCY_NOT_ACCEPTED: "slc_",
    GateReasonCode.DEPENDENCY_STALE: "slc_",
    GateReasonCode.AUTHORIZATION_STALE: "auth_",
    GateReasonCode.HUMAN_DECISION_STALE: "hdec_",
    GateReasonCode.HUMAN_REJECTED: "hdec_",
    GateReasonCode.NOT_SELECTED_BY_HUMAN: "gate_",
    GateReasonCode.MULTIPLE_EXECUTABLE_PATHS: "gate_",
}


class GateRevisionRef(DomainModel):
    """Identity of one exact gate policy revision."""

    gate_id: HandoverGateId
    gate_revision: int = Field(ge=1)


class HandoverGate(DomainModel):
    """Immutable policy for one possible lifecycle handover."""

    gate_id: HandoverGateId
    revision: int = Field(ge=1)
    key: StableKey
    slice_id: SliceId
    baseline_id: BaselineId
    source_phase: LifecyclePhase
    target_phase: LifecyclePhase
    superseded_by_slice_id: SliceId | None = None
    policy: HandoverPolicy
    hard_stop: bool = False
    authorization_required: bool = False
    required_artifact_ids: tuple[ArtifactId, ...] = ()
    required_evidence_ids: tuple[EvidenceId, ...] = ()
    required_dependency_slice_ids: tuple[SliceId, ...] = ()
    required_evaluation_outcomes: tuple[EvaluationOutcome, ...] = ()
    required_quality_checks: tuple[StableKey, ...] = ()
    change_surface_policy: ReviewPolicy = ReviewPolicy.ALLOW
    risk_policy: ReviewPolicy = ReviewPolicy.ALLOW

    @field_validator(
        "required_artifact_ids",
        "required_evidence_ids",
        "required_dependency_slice_ids",
        "required_evaluation_outcomes",
        "required_quality_checks",
    )
    @classmethod
    def tuple_values_are_unique(cls, value: tuple[object, ...]) -> tuple[object, ...]:
        if len(value) != len(set(value)):
            raise ValueError("gate requirement tuples must not contain duplicates")
        return value

    @model_validator(mode="after")
    def gate_structure_is_valid(self) -> HandoverGate:
        if self.source_phase is self.target_phase:
            raise ValueError("gate source and target phases must differ")
        if self.slice_id in self.required_dependency_slice_ids:
            raise ValueError("gate cannot depend on its own slice")
        is_superseding = self.target_phase is LifecyclePhase.SUPERSEDED
        if is_superseding != (self.superseded_by_slice_id is not None):
            raise ValueError("supersession gates require a successor and other gates forbid one")
        if self.superseded_by_slice_id == self.slice_id:
            raise ValueError("a slice cannot supersede itself")
        return self


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(UTC)


class AuthorizationGrant(DomainModel):
    """Durable permission bound to a slice, baseline, gate, and policy revision."""

    authorization_id: AuthorizationId
    slice_id: SliceId
    baseline_id: BaselineId
    gate_id: HandoverGateId
    gate_revision: int = Field(ge=1)
    actor: ActorRef
    granted_at: datetime
    reason: str

    @field_validator("actor")
    @classmethod
    def authorization_requires_human(cls, value: ActorRef) -> ActorRef:
        if value.kind is not ActorKind.HUMAN:
            raise ValueError("Slice 0.4 authorization requires a HUMAN actor")
        return value

    @field_validator("granted_at")
    @classmethod
    def grant_time_is_aware_utc(cls, value: datetime) -> datetime:
        return _aware_utc(value)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class HumanApprovalDecision(DomainModel):
    """Current execution-time approval or rejection for one exact gate."""

    decision_id: HumanDecisionId
    slice_id: SliceId
    baseline_id: BaselineId
    gate_id: HandoverGateId
    gate_revision: int = Field(ge=1)
    lifecycle_revision: int = Field(ge=0)
    governance_revision: int = Field(ge=0)
    actor: ActorRef
    occurred_at: datetime
    decision: HumanApprovalValue
    reason: str

    @field_validator("actor")
    @classmethod
    def approval_requires_human(cls, value: ActorRef) -> ActorRef:
        if value.kind is not ActorKind.HUMAN:
            raise ValueError("human approval requires a HUMAN actor")
        return value

    @field_validator("occurred_at")
    @classmethod
    def approval_time_is_aware_utc(cls, value: datetime) -> datetime:
        return _aware_utc(value)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class HumanChoiceDecision(DomainModel):
    """Execution-time selection from one exact canonical gate-choice set."""

    decision_id: HumanDecisionId
    slice_id: SliceId
    baseline_id: BaselineId
    selected_gate_id: HandoverGateId
    selected_gate_revision: int = Field(ge=1)
    choice_gate_refs: tuple[GateRevisionRef, ...]
    lifecycle_revision: int = Field(ge=0)
    governance_revision: int = Field(ge=0)
    actor: ActorRef
    occurred_at: datetime
    reason: str

    @field_validator("actor")
    @classmethod
    def choice_requires_human(cls, value: ActorRef) -> ActorRef:
        if value.kind is not ActorKind.HUMAN:
            raise ValueError("human choice requires a HUMAN actor")
        return value

    @field_validator("occurred_at")
    @classmethod
    def choice_time_is_aware_utc(cls, value: datetime) -> datetime:
        return _aware_utc(value)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("choice_gate_refs")
    @classmethod
    def choice_set_is_canonical(
        cls, value: tuple[GateRevisionRef, ...]
    ) -> tuple[GateRevisionRef, ...]:
        ids = tuple(item.gate_id for item in value)
        if not ids or len(ids) != len(set(ids)) or ids != tuple(sorted(ids)):
            raise ValueError("choice_gate_refs must be non-empty, unique, and sorted by gate_id")
        return value

    @model_validator(mode="after")
    def selected_gate_is_in_choice_set(self) -> HumanChoiceDecision:
        if (
            GateRevisionRef(
                gate_id=self.selected_gate_id, gate_revision=self.selected_gate_revision
            )
            not in self.choice_gate_refs
        ):
            raise ValueError("selected gate and revision must appear in choice_gate_refs")
        return self


type HumanGateDecision = HumanApprovalDecision | HumanChoiceDecision


class QualityCheckResult(DomainModel):
    """Explicit supplied result for one named quality check."""

    key: StableKey
    status: QualityCheckStatus


class HandoverContext(DomainModel):
    """Current explicit facts used to evaluate one outgoing gate set."""

    baseline_id: BaselineId
    governance_revision: int = Field(ge=0)
    lifecycle: SliceLifecycle
    available_artifact_ids: tuple[ArtifactId, ...] = ()
    available_evidence_ids: tuple[EvidenceId, ...] = ()
    dependency_lifecycles: tuple[SliceLifecycle, ...] = ()
    evaluation_outcome: EvaluationOutcome | None = None
    authorization_grants: tuple[AuthorizationGrant, ...] = ()
    human_decisions: tuple[HumanGateDecision, ...] = ()
    quality_checks: tuple[QualityCheckResult, ...] = ()
    change_surface_status: ChangeSurfaceStatus
    risk_status: RiskStatus
    toolchain_change_status: ToolchainChangeStatus

    @model_validator(mode="after")
    def projections_are_unambiguous(self) -> HandoverContext:
        if len(self.available_artifact_ids) != len(set(self.available_artifact_ids)):
            raise ValueError("available artifact IDs must be unique")
        if len(self.available_evidence_ids) != len(set(self.available_evidence_ids)):
            raise ValueError("available evidence IDs must be unique")
        dependency_ids = tuple(item.slice_id for item in self.dependency_lifecycles)
        if len(dependency_ids) != len(set(dependency_ids)):
            raise ValueError("dependency lifecycle projections must be unique by slice_id")
        quality_keys = tuple(item.key for item in self.quality_checks)
        if len(quality_keys) != len(set(quality_keys)):
            raise ValueError("quality checks must be unique by key")
        grant_ids = tuple(item.authorization_id for item in self.authorization_grants)
        grant_gates = tuple(item.gate_id for item in self.authorization_grants)
        if len(grant_ids) != len(set(grant_ids)) or len(grant_gates) != len(set(grant_gates)):
            raise ValueError("authorization projection must be unique by ID and logical gate")
        decision_ids = tuple(item.decision_id for item in self.human_decisions)
        approval_gates = tuple(
            item.gate_id for item in self.human_decisions if isinstance(item, HumanApprovalDecision)
        )
        choices = tuple(
            item for item in self.human_decisions if isinstance(item, HumanChoiceDecision)
        )
        if len(decision_ids) != len(set(decision_ids)):
            raise ValueError("human decision IDs must be unique")
        if len(approval_gates) != len(set(approval_gates)):
            raise ValueError("at most one approval per logical gate may be current")
        if len(choices) > 1:
            raise ValueError("at most one choice decision may be current")
        return self


class GateReason(DomainModel):
    """Typed deterministic reason explaining a gate light."""

    kind: GateReasonKind
    code: GateReasonCode
    subject: str | None = None

    @classmethod
    def for_code(cls, code: GateReasonCode, subject: str | None = None) -> GateReason:
        """Build a reason using the fixed normative code-to-kind mapping."""

        return cls(kind=_REASON_KINDS[code], code=code, subject=subject)

    def __hash__(self) -> int:
        return hash((self.kind, self.code, self.subject))

    @model_validator(mode="after")
    def code_contract_is_respected(self) -> GateReason:
        if self.kind is not _REASON_KINDS[self.code]:
            raise ValueError("reason kind does not match its normative code mapping")
        if (self.subject is not None) != (self.code in _SUBJECT_REQUIRED):
            raise ValueError("reason subject cardinality does not match its code")
        if self.subject is not None:
            require_nonblank(self.subject)
            prefix = _SUBJECT_PREFIX.get(self.code)
            if prefix is not None and not re.fullmatch(
                rf"{prefix}[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}",
                self.subject,
            ):
                raise ValueError("reason subject must use the identifier type required by its code")
            if self.code in {
                GateReasonCode.QUALITY_CHECK_MISSING,
                GateReasonCode.QUALITY_CHECK_FAILED,
            } and not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", self.subject):
                raise ValueError("quality-check reason subject must be a stable slug")
        return self


class GateEvaluation(DomainModel):
    """Deterministic gate result bound to its exact current evaluation basis."""

    gate_id: HandoverGateId
    gate_revision: int = Field(ge=1)
    slice_id: SliceId
    baseline_id: BaselineId
    lifecycle_revision: int = Field(ge=0)
    governance_revision: int = Field(ge=0)
    target_phase: LifecyclePhase
    light: TrafficLight
    reasons: tuple[GateReason, ...]

    @model_validator(mode="after")
    def light_and_reasons_agree(self) -> GateEvaluation:
        if (self.light is TrafficLight.GREEN) != (not self.reasons):
            raise ValueError("GREEN requires no reasons; YELLOW and RED require reasons")
        reason_keys = tuple((reason.code, reason.subject) for reason in self.reasons)
        if len(reason_keys) != len(set(reason_keys)):
            raise ValueError("gate evaluations must not repeat a reason subject")
        if self.reasons != tuple(
            sorted(
                self.reasons, key=lambda r: (list(GateReasonCode).index(r.code), r.subject or "")
            )
        ):
            raise ValueError("gate reasons must use canonical code and subject order")
        return self


__all__ = [
    "AuthorizationGrant",
    "AuthorizationId",
    "ChangeSurfaceStatus",
    "EvaluationOutcome",
    "GateEvaluation",
    "GateReason",
    "GateReasonCode",
    "GateReasonKind",
    "GateRevisionRef",
    "HandoverContext",
    "HandoverGate",
    "HandoverGateId",
    "HandoverPolicy",
    "HumanApprovalDecision",
    "HumanApprovalValue",
    "HumanChoiceDecision",
    "HumanDecisionId",
    "HumanGateDecision",
    "QualityCheckResult",
    "QualityCheckStatus",
    "ReviewPolicy",
    "RiskStatus",
    "ToolchainChangeStatus",
    "TrafficLight",
]
