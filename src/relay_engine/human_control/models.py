"""Typed Human action commands and display-only action projections."""

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import DomainModel
from relay_engine.domain.ids import (
    BaselineId,
    GateEvaluationRecordId,
    HandoverGateId,
    HumanDecisionId,
    ManualEvaluationId,
    SliceId,
    SliceResultId,
)
from relay_engine.governance.models import (
    AuthorizationGrant,
    GateReason,
    GateRevisionRef,
    HumanApprovalDecision,
    HumanChoiceDecision,
)
from relay_engine.lifecycle.models import BlockReason, LifecyclePhase


class HumanActionKind(StrEnum):
    """The fixed set of Human controls authorized for Slice 1.6."""

    AUTHORIZE = "AUTHORIZE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    CHOOSE_PATH = "CHOOSE_PATH"
    BLOCK = "BLOCK"
    PAUSE = "PAUSE"
    DEFER = "DEFER"
    CLEAR_HOLD = "CLEAR_HOLD"
    ADVANCE = "ADVANCE"
    CANCEL = "CANCEL"


class HumanApprovalIdentity(DomainModel):
    """Identity of the deterministic latest approval projection for a gate."""

    gate_id: HandoverGateId
    decision_id: HumanDecisionId


class HumanActionBasis(DomainModel):
    """Exact durable observation and Human-evidence projection seen by a form."""

    evaluation_record_id: GateEvaluationRecordId
    slice_id: SliceId
    baseline_id: BaselineId
    lifecycle_revision: int = Field(ge=0)
    governance_revision: int = Field(ge=0)
    gate_refs: tuple[GateRevisionRef, ...]
    current_approval_decision_ids: tuple[HumanApprovalIdentity, ...] = ()
    current_choice_decision_id: HumanDecisionId | None = None
    current_result_id: SliceResultId | None = None
    current_result_baseline_id: BaselineId | None = None
    current_manual_evaluation_id: ManualEvaluationId | None = None

    @field_validator("gate_refs")
    @classmethod
    def gate_refs_are_canonical(
        cls, value: tuple[GateRevisionRef, ...]
    ) -> tuple[GateRevisionRef, ...]:
        ids = tuple(item.gate_id for item in value)
        if not ids or ids != tuple(sorted(ids)) or len(ids) != len(set(ids)):
            raise ValueError("gate_refs must be non-empty, unique, and sorted by gate_id")
        return value

    @field_validator("current_approval_decision_ids")
    @classmethod
    def approval_ids_are_canonical(
        cls, value: tuple[HumanApprovalIdentity, ...]
    ) -> tuple[HumanApprovalIdentity, ...]:
        ids = tuple(item.gate_id for item in value)
        if ids != tuple(sorted(ids)) or len(ids) != len(set(ids)):
            raise ValueError("approval identities must be unique and sorted by gate_id")
        return value

    @model_validator(mode="after")
    def result_subject_is_consistent(self) -> HumanActionBasis:
        if (self.current_result_id is None) != (self.current_result_baseline_id is None):
            raise ValueError("current result identity and Baseline must be present together")
        if self.current_manual_evaluation_id is not None and self.current_result_id is None:
            raise ValueError("current evaluation identity requires a current result")
        return self


class HumanAction(DomainModel):
    """One displayable action and its exact gate provenance, when applicable."""

    kind: HumanActionKind
    gate_id: HandoverGateId | None = None
    gate_revision: int | None = Field(default=None, ge=1)
    target_phase: LifecyclePhase | None = None
    reasons: tuple[GateReason, ...] = ()


class HumanActionProjection(DomainModel):
    """Advisory action controls and current Human evidence for Slice detail."""

    basis: HumanActionBasis | None = None
    actions: tuple[HumanAction, ...] = ()
    current_authorizations: tuple[AuthorizationGrant, ...] = ()
    current_approval_decisions: tuple[HumanApprovalDecision, ...] = ()
    current_choice: HumanChoiceDecision | None = None
    human_hold: tuple[BlockReason, ...] = ()


__all__ = [
    "HumanAction",
    "HumanActionBasis",
    "HumanActionKind",
    "HumanActionProjection",
    "HumanApprovalIdentity",
]
