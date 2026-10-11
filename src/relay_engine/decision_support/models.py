"""Immutable, non-authoritative Decision Support presentation values."""

import json
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import (
    HumanDecisionId,
    ManualEvaluationId,
    SliceId,
    SliceResultId,
)
from relay_engine.domain.models import ContentDigest
from relay_engine.governance.models import GateRevisionRef
from relay_engine.human_control.models import HumanActionBasis, HumanActionKind
from relay_engine.lifecycle.models import LifecyclePhase
from relay_engine.manual_evaluation.models import ManualEvaluationActionKind


class DecisionKind(StrEnum):
    GATE_AUTHORIZATION = "GATE_AUTHORIZATION"
    GATE_APPROVAL = "GATE_APPROVAL"
    GATE_PATH_CHOICE = "GATE_PATH_CHOICE"
    TECHNICAL_ACCEPTANCE = "TECHNICAL_ACCEPTANCE"


class DecisionCardState(StrEnum):
    PENDING_REQUIRED = "PENDING_REQUIRED"
    RECORDED_REVISABLE = "RECORDED_REVISABLE"


class DecisionBasisApplicability(StrEnum):
    REQUIRED_PRESENT = "REQUIRED_PRESENT"
    OPTIONAL_PRESENT = "OPTIONAL_PRESENT"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"
    MISSING_REQUIRED = "MISSING_REQUIRED"


class DecisionBasisFreshness(StrEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class DecisionBasisCompleteness(StrEnum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"


class DecisionStatementBasis(StrEnum):
    CANONICAL_FACT = "CANONICAL_FACT"
    EVALUATOR_JUDGMENT = "EVALUATOR_JUDGMENT"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    UNKNOWN = "UNKNOWN"


class DecisionQuestionKind(StrEnum):
    WHY_REQUIRED = "WHY_REQUIRED"
    WHAT_IS_CURRENT = "WHAT_IS_CURRENT"
    WHAT_WOULD_CHANGE = "WHAT_WOULD_CHANGE"
    WHAT_EVIDENCE_EXISTS = "WHAT_EVIDENCE_EXISTS"
    WHAT_DID_THE_EVALUATOR_FIND = "WHAT_DID_THE_EVALUATOR_FIND"
    WHAT_BLOCKS_OR_IS_UNKNOWN = "WHAT_BLOCKS_OR_IS_UNKNOWN"
    WHAT_IF_APPROVED = "WHAT_IF_APPROVED"
    WHAT_IF_REJECTED = "WHAT_IF_REJECTED"
    WHAT_IF_DEFERRED = "WHAT_IF_DEFERRED"
    WHAT_GOVERNANCE_REQUIREMENTS_APPLY = "WHAT_GOVERNANCE_REQUIREMENTS_APPLY"


class DecisionBasisComponentKind(StrEnum):
    DECISION_SUBJECT = "DECISION_SUBJECT"
    CURRENT_STATE = "CURRENT_STATE"
    PROPOSED_STATE = "PROPOSED_STATE"
    AUTHORITY_BASIS = "AUTHORITY_BASIS"
    POLICY_OR_GATE_BASIS = "POLICY_OR_GATE_BASIS"
    DESIGN_OR_SCOPE_BASIS = "DESIGN_OR_SCOPE_BASIS"
    CHANGE_OR_RESULT_BASIS = "CHANGE_OR_RESULT_BASIS"
    EVIDENCE = "EVIDENCE"
    EVALUATION = "EVALUATION"
    RISKS_AND_BLOCKERS = "RISKS_AND_BLOCKERS"
    GOVERNANCE_REQUIREMENTS = "GOVERNANCE_REQUIREMENTS"
    CONSEQUENCES = "CONSEQUENCES"
    SOURCE_PROVENANCE = "SOURCE_PROVENANCE"


class DecisionSourceKind(StrEnum):
    SLICE_DEFINITION = "SLICE_DEFINITION"
    LIFECYCLE = "LIFECYCLE"
    HANDOVER_GATE = "HANDOVER_GATE"
    GATE_EVALUATION = "GATE_EVALUATION"
    BASELINE = "BASELINE"
    AUTHORIZATION = "AUTHORIZATION"
    HUMAN_DECISION = "HUMAN_DECISION"
    SLICE_RESULT = "SLICE_RESULT"
    MANUAL_EVALUATION = "MANUAL_EVALUATION"
    EVIDENCE = "EVIDENCE"
    EXECUTION = "EXECUTION"
    ACCEPTED_DESIGN_OR_ARTIFACT = "ACCEPTED_DESIGN_OR_ARTIFACT"
    POLICY_REFERENCE = "POLICY_REFERENCE"


class DecisionBasisIdentityV1(DomainModel):
    """Exact mutation-relevant identity used only for navigation freshness."""

    schema_version: Literal[1] = 1
    decision_kind: DecisionKind
    slice_id: SliceId
    gate_ref: GateRevisionRef | None
    target_phase: LifecyclePhase | None
    human_action_basis: HumanActionBasis
    decision_state: DecisionCardState
    expected_current_approval_decision_id: HumanDecisionId | None = None
    expected_current_choice_decision_id: HumanDecisionId | None = None
    expected_result_id: SliceResultId | None = None
    expected_manual_evaluation_id: ManualEvaluationId | None = None
    eligible_choice_gate_refs: tuple[GateRevisionRef, ...] = ()

    @field_validator("eligible_choice_gate_refs")
    @classmethod
    def choice_refs_are_ordered(
        cls, value: tuple[GateRevisionRef, ...]
    ) -> tuple[GateRevisionRef, ...]:
        keys = tuple((item.gate_id, item.gate_revision) for item in value)
        if keys != tuple(sorted(set(keys))):
            raise ValueError("eligible choice refs must be unique and sorted")
        return value

    @model_validator(mode="after")
    def identity_matches_kind(self) -> DecisionBasisIdentityV1:
        if self.human_action_basis.slice_id != self.slice_id:
            raise ValueError("HumanActionBasis must identify the same Slice")
        if self.decision_kind is DecisionKind.GATE_PATH_CHOICE:
            if self.gate_ref is not None or self.target_phase is not None:
                raise ValueError("path choice identity uses null gate_ref and target_phase")
            if not self.eligible_choice_gate_refs:
                raise ValueError("path choice identity requires eligible exact gate refs")
        elif self.gate_ref is None or self.target_phase is None:
            raise ValueError("single-gate decision identity requires exact gate and target")
        if self.decision_kind not in {
            DecisionKind.GATE_APPROVAL,
            DecisionKind.TECHNICAL_ACCEPTANCE,
        } and (self.expected_current_approval_decision_id is not None):
            raise ValueError("approval selector is only valid for approval decisions")
        if self.decision_kind is not DecisionKind.GATE_PATH_CHOICE and (
            self.expected_current_choice_decision_id is not None
        ):
            raise ValueError("choice selector is only valid for path-choice decisions")
        if self.decision_kind is DecisionKind.TECHNICAL_ACCEPTANCE:
            if self.expected_result_id is None or self.expected_manual_evaluation_id is None:
                raise ValueError("technical acceptance requires exact result and evaluation IDs")
        elif self.expected_result_id is not None or self.expected_manual_evaluation_id is not None:
            raise ValueError("result/evaluation selectors are only valid for technical decisions")
        return self

    def digest(self) -> ContentDigest:
        """Return the exact canonical SHA-256 identity digest."""

        canonical_bytes = json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"sha256:{sha256(canonical_bytes).hexdigest()}"


class PendingDecisionRef(DomainModel):
    """Deterministic, non-durable identity of one current Decision Card."""

    identity: DecisionBasisIdentityV1
    basis_digest: ContentDigest

    @model_validator(mode="after")
    def digest_matches_identity(self) -> PendingDecisionRef:
        if self.basis_digest != self.identity.digest():
            raise ValueError("basis digest must match exact DecisionBasisIdentityV1")
        return self


class DecisionSourceRef(DomainModel):
    """Typed provenance link to an exact current governed identity."""

    kind: DecisionSourceKind
    stable_ref: str = Field(min_length=1)
    label: str = Field(min_length=1)

    @field_validator("stable_ref", "label")
    @classmethod
    def values_are_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class DecisionStatement(DomainModel):
    """One concise statement whose evidentiary basis is explicit."""

    text: str = Field(min_length=1)
    basis: DecisionStatementBasis
    source_refs: tuple[DecisionSourceRef, ...] = ()

    @field_validator("text")
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("basis")
    @classmethod
    def no_model_inference(cls, value: DecisionStatementBasis) -> DecisionStatementBasis:
        if value in {
            DecisionStatementBasis.MODEL_INFERENCE,
            DecisionStatementBasis.EXTERNAL_REFERENCE,
        }:
            raise ValueError(
                "this implementation emits only canonical, evaluator, or unknown basis"
            )
        return value


class DecisionBasisComponent(DomainModel):
    """Applicability and freshness of one required or optional basis component."""

    kind: DecisionBasisComponentKind
    applicability: DecisionBasisApplicability
    freshness: DecisionBasisFreshness
    required: bool
    summary: str
    source_refs: tuple[DecisionSourceRef, ...] = ()

    @field_validator("summary")
    @classmethod
    def summary_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class DecisionProposedOutcome(DomainModel):
    """One exact possible governed outcome for a Human decision."""

    gate_ref: GateRevisionRef
    target_phase: LifecyclePhase
    label: str

    @field_validator("label")
    @classmethod
    def label_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class GateAuthorizationChoice(DomainModel):
    """Existing AUTHORIZE control bound to the exact gate and Human basis."""

    command: Literal[HumanActionKind.AUTHORIZE]
    gate_ref: GateRevisionRef
    human_action_basis: HumanActionBasis


class GateApprovalChoice(DomainModel):
    """Existing APPROVE/REJECT control with its current-decision CAS selector."""

    command: Literal[HumanActionKind.APPROVE, HumanActionKind.REJECT]
    gate_ref: GateRevisionRef
    human_action_basis: HumanActionBasis
    expected_current_approval_decision_id: HumanDecisionId | None = None


class GatePathChoice(DomainModel):
    """Existing CHOOSE_PATH control for one exact eligible gate."""

    command: Literal[HumanActionKind.CHOOSE_PATH]
    gate_ref: GateRevisionRef
    human_action_basis: HumanActionBasis
    expected_current_choice_decision_id: HumanDecisionId | None = None


class TechnicalAcceptanceChoice(DomainModel):
    """Existing technical decision control over exact result/evaluation CAS."""

    command: Literal[
        ManualEvaluationActionKind.TECHNICAL_ACCEPT,
        ManualEvaluationActionKind.TECHNICAL_REJECT,
    ]
    gate_ref: GateRevisionRef
    human_action_basis: HumanActionBasis
    expected_current_approval_decision_id: HumanDecisionId | None = None
    expected_result_id: SliceResultId
    expected_manual_evaluation_id: ManualEvaluationId


DecisionChoice = Annotated[
    GateAuthorizationChoice | GateApprovalChoice | GatePathChoice | TechnicalAcceptanceChoice,
    Field(discriminator="command"),
]


class DecisionCard(DomainModel):
    """One complete deterministic explanation for an existing Human action."""

    decision: PendingDecisionRef
    title: str
    state: DecisionCardState
    current_recorded_decision: str | None = None
    why_required: DecisionStatement
    current_state: DecisionStatement
    proposed_outcomes: tuple[DecisionProposedOutcome, ...]
    choices: tuple[DecisionChoice, ...]
    components: tuple[DecisionBasisComponent, ...]
    evidence: tuple[DecisionStatement, ...] = ()
    evaluation: tuple[DecisionStatement, ...] = ()
    risks: tuple[DecisionStatement, ...] = ()
    unknowns: tuple[DecisionStatement, ...] = ()
    blocking_findings: tuple[DecisionStatement, ...] = ()
    consequences: tuple[DecisionStatement, ...]
    governance_requirements: tuple[DecisionStatement, ...]
    source_refs: tuple[DecisionSourceRef, ...]
    completeness: DecisionBasisCompleteness
    question_kinds: tuple[DecisionQuestionKind, ...] = tuple(DecisionQuestionKind)

    @field_validator("title", "current_recorded_decision")
    @classmethod
    def optional_text_is_nonblank(cls, value: str | None) -> str | None:
        if value is not None:
            require_nonblank(value)
        return value

    @model_validator(mode="after")
    def outcomes_match_identity(self) -> DecisionCard:
        kind = self.decision.identity.decision_kind
        expected_refs = {
            (item.gate_ref.gate_id, item.gate_ref.gate_revision) for item in self.proposed_outcomes
        }
        eligible = {
            (item.gate_id, item.gate_revision)
            for item in self.decision.identity.eligible_choice_gate_refs
        }
        if not self.proposed_outcomes:
            raise ValueError("Decision Card requires proposed outcomes")
        if kind is DecisionKind.GATE_PATH_CHOICE:
            if expected_refs != eligible:
                raise ValueError("path-choice outcomes must equal eligible exact gate refs")
        elif len(self.proposed_outcomes) != 1:
            raise ValueError("single-gate decisions require exactly one proposed outcome")
        order = tuple(
            (item.gate_ref.gate_id, item.gate_ref.gate_revision, item.target_phase.value)
            for item in self.proposed_outcomes
        )
        if order != tuple(sorted(order)):
            raise ValueError("proposed outcomes must use deterministic order")
        return self


class DecisionAnswer(DomainModel):
    """Deterministic answer generated only from one current Decision Card."""

    decision: PendingDecisionRef
    question_kind: DecisionQuestionKind
    answer: str
    basis_labels: tuple[DecisionStatementBasis, ...]
    source_refs: tuple[DecisionSourceRef, ...]
    freshness: DecisionBasisFreshness

    @field_validator("answer")
    @classmethod
    def answer_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("basis_labels")
    @classmethod
    def answer_cannot_claim_inference(cls, value: tuple[DecisionStatementBasis, ...]):
        allowed = {
            DecisionStatementBasis.CANONICAL_FACT,
            DecisionStatementBasis.EVALUATOR_JUDGMENT,
            DecisionStatementBasis.UNKNOWN,
        }
        if any(item not in allowed for item in value):
            raise ValueError("answers may not emit external references or model inference")
        return tuple(sorted(set(value), key=lambda item: item.value))


class DecisionSupportProjection(DomainModel):
    """All current Decision Cards for one Slice detail snapshot."""

    cards: tuple[DecisionCard, ...] = ()
    stale_notice: str | None = None
    answer: DecisionAnswer | None = None

    @field_validator("stale_notice")
    @classmethod
    def notice_is_nonblank(cls, value: str | None) -> str | None:
        if value is not None:
            require_nonblank(value)
        return value


__all__ = [
    "DecisionAnswer",
    "DecisionBasisApplicability",
    "DecisionBasisCompleteness",
    "DecisionBasisComponent",
    "DecisionBasisComponentKind",
    "DecisionBasisFreshness",
    "DecisionBasisIdentityV1",
    "DecisionCard",
    "DecisionCardState",
    "DecisionChoice",
    "DecisionKind",
    "DecisionProposedOutcome",
    "DecisionQuestionKind",
    "DecisionSourceKind",
    "DecisionSourceRef",
    "DecisionStatement",
    "DecisionStatementBasis",
    "DecisionSupportProjection",
    "PendingDecisionRef",
]
