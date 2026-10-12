"""Deterministic Project Situation and canonical inspection projection tests."""

from datetime import UTC, datetime

from relay_engine.board.inspection import project_project_situation
from relay_engine.board.models import (
    BoardLane,
    EvaluationBasisStatus,
    FrontierCardinality,
    GateProjection,
    SliceCard,
    StaleStateKind,
)
from relay_engine.domain.ids import BaselineId, HandoverGateId, SliceId
from relay_engine.governance.models import (
    GateReason,
    GateReasonCode,
    HandoverPolicy,
    TrafficLight,
)
from relay_engine.lifecycle.models import (
    Blockage,
    BlockageStatus,
    BlockReason,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
)

NOW = datetime(2026, 10, 12, tzinfo=UTC)
SLICE_A: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
SLICE_B: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789007"
SLICE_C: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789008"
SLICE_D: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789009"
SLICE_E: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789010"
BASELINE: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
GATE: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"


def _lifecycle(
    slice_id: SliceId,
    phase: LifecyclePhase,
    *,
    validity: LifecycleValidity = LifecycleValidity.CURRENT,
    blocked: bool = False,
    superseded_by: SliceId | None = None,
) -> SliceLifecycle:
    return SliceLifecycle(
        slice_id=slice_id,
        phase=phase,
        validity=validity,
        blockage=Blockage(
            status=BlockageStatus.BLOCKED if blocked else BlockageStatus.CLEAR,
            reasons=(BlockReason(code="WAITING", summary="Explicit blocker."),) if blocked else (),
        ),
        revision=1,
        updated_at=NOW,
        superseded_by_slice_id=superseded_by,
    )


def _card(
    slice_id: SliceId,
    *,
    phase: LifecyclePhase | None,
    parent: SliceId | None = None,
    validity: LifecycleValidity = LifecycleValidity.CURRENT,
    blocked: bool = False,
    superseded_by: SliceId | None = None,
    stale_evaluation: bool = False,
    matching_gate_blocker: bool = False,
) -> SliceCard:
    gate = GateProjection(
        gate_id=GATE,
        gate_revision=1,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.AUTO,
        hard_stop=False,
        authorization_required=True,
        baseline_id=BASELINE,
        evaluation_light=TrafficLight.RED if matching_gate_blocker else None,
        evaluation_reasons=(GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),)
        if matching_gate_blocker
        else (),
        evaluation_basis_status=(
            EvaluationBasisStatus.MATCHING_DURABLE_BASIS
            if matching_gate_blocker
            else EvaluationBasisStatus.NOT_EVALUATED
        ),
    )
    return SliceCard(
        slice_id=slice_id,
        title=f"Slice {slice_id[-1]}",
        definition_revision=1,
        parent_slice_id=parent,
        dependency_ids=(),
        lane=BoardLane.NOT_STARTED if phase is None else BoardLane.DELIVERY,
        lifecycle=None
        if phase is None
        else _lifecycle(
            slice_id,
            phase,
            validity=validity,
            blocked=blocked,
            superseded_by=superseded_by,
        ),
        dependencies=(),
        outgoing_gates=(gate,),
        latest_evaluation_record_id=None,
        latest_evaluation_recorded_at=None,
        evaluation_basis_status=(
            EvaluationBasisStatus.STALE_DURABLE_BASIS
            if stale_evaluation
            else EvaluationBasisStatus.NOT_EVALUATED
        ),
    )


def test_project_situation_classifies_frontier_history_and_hierarchy_exactly() -> None:
    cards = (
        _card(SLICE_A, phase=LifecyclePhase.IMPLEMENTING, blocked=True),
        _card(SLICE_B, phase=LifecyclePhase.REWORK, parent=SLICE_A),
        _card(SLICE_C, phase=LifecyclePhase.DESIGNING),
        _card(SLICE_D, phase=LifecyclePhase.ACCEPTED),
        _card(SLICE_E, phase=LifecyclePhase.SUPERSEDED, superseded_by=SLICE_C),
        _card(
            "slc_018f47c1-7b2c-7abc-8def-123456789011",
            phase=LifecyclePhase.CANCELLED,
        ),
        _card("slc_018f47c1-7b2c-7abc-8def-123456789012", phase=None),
    )

    projection = project_project_situation(cards)

    assert projection.frontier_cardinality is FrontierCardinality.MULTIPLE
    assert tuple(item.slice_id for item in projection.leaf_active_frontiers) == (
        SLICE_B,
        SLICE_C,
    )
    assert tuple(item.slice_id for item in projection.done_slices) == (SLICE_D,)
    assert tuple(item.slice_id for item in projection.superseded_slices) == (SLICE_E,)
    assert projection.hierarchy[4].superseded_by_slice_id == SLICE_C
    assert len(projection.cancelled_slices) == 1
    assert len(projection.not_started_slices) == 1
    assert tuple(item.slice_id for item in projection.active_slices) == (SLICE_A, SLICE_B, SLICE_C)
    assert tuple(item.slice.slice_id for item in projection.next_governed_work) == (
        SLICE_B,
        SLICE_C,
    )


def test_project_situation_single_leaf_and_no_frontier_are_explicit() -> None:
    parent = _card(SLICE_A, phase=LifecyclePhase.IMPLEMENTING)
    child = _card(SLICE_B, phase=LifecyclePhase.REWORK, parent=SLICE_A)

    single = project_project_situation((parent, child))
    none = project_project_situation((_card(SLICE_D, phase=LifecyclePhase.ACCEPTED),))

    assert single.frontier_cardinality is FrontierCardinality.ONE
    assert tuple(item.slice_id for item in single.leaf_active_frontiers) == (SLICE_B,)
    assert none.frontier_cardinality is FrontierCardinality.NONE
    assert none.leaf_active_frontiers == ()


def test_stale_states_are_separate_and_stale_blockage_is_not_current_blocker() -> None:
    stale_lifecycle = _card(
        SLICE_A,
        phase=LifecyclePhase.IMPLEMENTING,
        validity=LifecycleValidity.STALE,
        blocked=True,
        stale_evaluation=True,
    )
    current_blocked = _card(SLICE_B, phase=LifecyclePhase.REWORK, matching_gate_blocker=True)

    projection = project_project_situation((stale_lifecycle, current_blocked))

    assert {(item.slice.slice_id, item.kind) for item in projection.stale_states} == {
        (SLICE_A, StaleStateKind.LIFECYCLE),
        (SLICE_A, StaleStateKind.GATE_EVALUATION),
    }
    assert {item.slice.slice_id for item in projection.blockers} == {SLICE_B}
    assert project_project_situation(
        (stale_lifecycle, current_blocked)
    ) == project_project_situation((current_blocked, stale_lifecycle))
