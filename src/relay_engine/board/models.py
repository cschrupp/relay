"""Immutable presentation values for the read-only Relay board."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from relay_engine.adoption.models import ProjectAdoptionRecordV1
from relay_engine.decision_support.models import DecisionSupportProjection
from relay_engine.domain._base import DomainModel
from relay_engine.domain.ids import (
    BaselineId,
    GateEvaluationRecordId,
    HandoverGateId,
    SliceId,
)
from relay_engine.domain.models import Baseline, Project
from relay_engine.domain.references import RepositoryRef
from relay_engine.governance.models import (
    GateReason,
    HandoverGate,
    HandoverPolicy,
    TrafficLight,
)
from relay_engine.human_control.models import HumanActionProjection
from relay_engine.lifecycle.models import LifecyclePhase, LifecycleValidity, SliceLifecycle
from relay_engine.manual_evaluation.models import ManualEvaluationProjection
from relay_engine.persistence.records import ExecutionRecord, GateEvaluationRecord
from relay_engine.project_slice.models import SliceDefinitionSnapshot
from relay_engine.project_slice.origin import OperationalOriginResolution
from relay_engine.promotion.controls import SourceControlObservationV1
from relay_engine.promotion.models import (
    CanonicalPromotionPolicyBindingResolution,
    CanonicalPromotionPolicyBindingV1,
    CanonicalPromotionReconciliationV1,
    CanonicalRefHealth,
    PromotionAuthorizability,
    PromotionEligibilityState,
    PromotionPropertyOutcome,
    ReconciliationPreparationState,
    RepositoryPromotionIntentV1,
    RepositoryPromotionResultV1,
)


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
    origin_resolution: OperationalOriginResolution
    adoption_record: ProjectAdoptionRecordV1 | None = None


class ProjectSliceIdentity(DomainModel):
    """Exact current Slice definition identity for Project Situation lists."""

    slice_id: SliceId
    title: str
    definition_revision: int = Field(ge=1)


class ProjectSliceHierarchy(DomainModel):
    """Declared parent, child, and dependency relationships for one Slice."""

    slice_id: SliceId
    parent_slice_id: SliceId | None
    child_slice_ids: tuple[SliceId, ...]
    dependency_ids: tuple[SliceId, ...]
    superseded_by_slice_id: SliceId | None


class FrontierCardinality(StrEnum):
    """Presentation cardinality of the exact active leaf-frontier set."""

    NONE = "NONE"
    ONE = "ONE"
    MULTIPLE = "MULTIPLE"


class SituationNextWorkState(StrEnum):
    """Whether current frontier gates provide a deterministic next-step view."""

    CURRENT_FRONTIER_GATES = "CURRENT_FRONTIER_GATES"
    NOT_DETERMINABLE = "NOT_DETERMINABLE"
    INCOMPLETE_ORIGIN = "INCOMPLETE_ORIGIN"


class ProjectionCompleteness(StrEnum):
    """Completeness of a read-model aggregate that depends on origin evidence."""

    COMPLETE = "COMPLETE"
    INCOMPLETE_NOT_ESTABLISHED = "INCOMPLETE_NOT_ESTABLISHED"


class ProjectGateReference(DomainModel):
    """One current outgoing gate tied to its exact Slice identity."""

    slice: ProjectSliceIdentity
    gate: GateProjection


class SituationBlockerSource(StrEnum):
    LIFECYCLE = "LIFECYCLE"
    GATE_EVALUATION = "GATE_EVALUATION"


class SituationBlocker(DomainModel):
    """An explicit lifecycle or current-basis gate blocker."""

    slice: ProjectSliceIdentity
    source: SituationBlockerSource
    code: str
    summary: str


class StaleStateKind(StrEnum):
    LIFECYCLE = "LIFECYCLE"
    GATE_EVALUATION = "GATE_EVALUATION"


class StaleSituationState(DomainModel):
    """A current durable Slice or evaluation projection marked stale."""

    slice: ProjectSliceIdentity
    kind: StaleStateKind


class ProjectSituationProjection(DomainModel):
    """Deterministic orientation over current Slice lifecycle and hierarchy facts."""

    done_slices: tuple[ProjectSliceIdentity, ...]
    active_slices: tuple[ProjectSliceIdentity, ...]
    not_started_slices: tuple[ProjectSliceIdentity, ...]
    pre_genesis_no_lifecycle_slices: tuple[ProjectSliceIdentity, ...]
    origin_not_established_slices: tuple[ProjectSliceIdentity, ...]
    lifecycle_inventory_completeness: ProjectionCompleteness
    lifecycle_inventory_incomplete_slices: tuple[ProjectSliceIdentity, ...]
    superseded_slices: tuple[ProjectSliceIdentity, ...]
    cancelled_slices: tuple[ProjectSliceIdentity, ...]
    leaf_active_frontiers: tuple[ProjectSliceIdentity, ...]
    frontier_cardinality: FrontierCardinality
    frontier_completeness: ProjectionCompleteness
    frontier_incomplete_slices: tuple[ProjectSliceIdentity, ...]
    blockers: tuple[SituationBlocker, ...]
    stale_states: tuple[StaleSituationState, ...]
    current_outgoing_gates: tuple[ProjectGateReference, ...]
    hierarchy: tuple[ProjectSliceHierarchy, ...]
    next_governed_work: tuple[ProjectGateReference, ...]
    next_work_state: SituationNextWorkState
    next_work_incomplete_slices: tuple[ProjectSliceIdentity, ...]

    @model_validator(mode="after")
    def cardinality_matches_frontiers(self) -> ProjectSituationProjection:
        expected = (
            FrontierCardinality.NONE
            if len(self.leaf_active_frontiers) == 0
            else FrontierCardinality.ONE
            if len(self.leaf_active_frontiers) == 1
            else FrontierCardinality.MULTIPLE
        )
        if self.frontier_cardinality is not expected:
            raise ValueError("frontier cardinality must match the exact frontier set")
        return self


class PromotionIntentAuthorityStatus(StrEnum):
    VERIFIED = "VERIFIED"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class LiveObservationStatus(StrEnum):
    UNAVAILABLE = "UNAVAILABLE"
    SUPPLIED = "SUPPLIED"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    AMBIGUOUS = "AMBIGUOUS"


class PromotionAttemptInspection(DomainModel):
    """Read-only exact records for one canonical promotion attempt."""

    promotion_id: str
    intent: RepositoryPromotionIntentV1 | None
    original_authority_status: PromotionIntentAuthorityStatus
    result: RepositoryPromotionResultV1 | None
    reconciliations: tuple[CanonicalPromotionReconciliationV1, ...]


class CanonicalTargetInspection(DomainModel):
    """One durable canonical-ref target and its exact promotion history."""

    repository: RepositoryRef
    canonical_ref: str
    binding_resolution: CanonicalPromotionPolicyBindingResolution
    current_binding: CanonicalPromotionPolicyBindingV1 | None
    health: CanonicalRefHealth
    current_authorizability: PromotionAuthorizability
    current_eligibility: PromotionEligibilityState
    reconciliation_preparation_state: ReconciliationPreparationState | None
    live_observation_status: LiveObservationStatus
    live_source_control_observation: SourceControlObservationV1 | None
    live_source_control_conformance: PromotionPropertyOutcome
    promotion_attempts: tuple[PromotionAttemptInspection, ...]


class CanonicalGovernanceInspection(DomainModel):
    """One serializable, read-only projection of canonical promotion governance."""

    durable_target_established: bool
    targets: tuple[CanonicalTargetInspection, ...]


class DependencyProjection(DomainModel):
    """Read-only relationship facts for a parent or dependency Slice."""

    slice_id: SliceId
    title: str | None
    lifecycle_phase: LifecyclePhase | None
    lifecycle_validity: LifecycleValidity | None
    origin_resolution: OperationalOriginResolution


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
    lane: BoardLane | None
    lifecycle: SliceLifecycle | None
    origin_resolution: OperationalOriginResolution
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
    project_origin_resolution: OperationalOriginResolution
    adoption_record: ProjectAdoptionRecordV1 | None = None
    situation: ProjectSituationProjection
    canonical_governance: CanonicalGovernanceInspection
    lanes: tuple[BoardLane, ...]
    cards: tuple[SliceCard, ...]

    @field_validator("lanes")
    @classmethod
    def lanes_are_fixed_and_ordered(cls, value: tuple[BoardLane, ...]) -> tuple[BoardLane, ...]:
        if value != tuple(BoardLane):
            raise ValueError("ProjectBoard lanes must use the fixed board order")
        return value

    @model_validator(mode="after")
    def situation_hierarchy_matches_cards(self) -> ProjectBoard:
        card_ids = tuple(card.slice_id for card in self.cards)
        hierarchy_ids = tuple(item.slice_id for item in self.situation.hierarchy)
        if len(set(hierarchy_ids)) != len(hierarchy_ids) or set(hierarchy_ids) != set(card_ids):
            raise ValueError("Project Situation hierarchy must cover each current Slice once")
        return self


class BoardProjection(DomainModel):
    """Verified Project summaries for the board index route."""

    projects: tuple[ProjectSummary, ...]


class SliceDetail(DomainModel):
    """Full read-only definition, governance provenance, and advisory Human controls."""

    project: Project
    project_definition_revision: int = Field(ge=1)
    slice_definition: SliceDefinitionSnapshot
    lifecycle: SliceLifecycle | None
    origin_resolution: OperationalOriginResolution
    origin_governance_scope_available: bool
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
    manual_evaluation: ManualEvaluationProjection = Field(
        default_factory=ManualEvaluationProjection
    )
    decision_support: DecisionSupportProjection


__all__ = [
    "BoardLane",
    "BoardProjection",
    "CanonicalGovernanceInspection",
    "CanonicalTargetInspection",
    "DependencyProjection",
    "EvaluationBasisStatus",
    "FrontierCardinality",
    "GateProjection",
    "LiveObservationStatus",
    "ProjectGateReference",
    "ProjectBoard",
    "ProjectSituationProjection",
    "ProjectSliceHierarchy",
    "ProjectSliceIdentity",
    "ProjectSummary",
    "ProjectionCompleteness",
    "PromotionAttemptInspection",
    "PromotionIntentAuthorityStatus",
    "SliceCard",
    "SliceDetail",
    "SituationBlocker",
    "SituationBlockerSource",
    "SituationNextWorkState",
    "StaleSituationState",
    "StaleStateKind",
]
