"""Deterministic derivation and full evaluation-observation identity tests."""

from datetime import UTC, datetime
from typing import cast

import pytest

from relay_engine.board.models import BoardLane, EvaluationBasisStatus
from relay_engine.board.service import (
    _check_duplicate_evaluation_outputs,
    _current_outgoing_gates,
    _evaluation_basis_status,
    _gate_projections,
    _lane_for,
    project_board,
    project_index,
    slice_detail,
)
from relay_engine.domain.ids import (
    BaselineId,
    EventId,
    GateEvaluationRecordId,
    HandoverGateId,
    ProjectId,
    SliceId,
)
from relay_engine.domain.models import (
    AcceptanceCriterion,
    Baseline,
    Project,
    ScopeSpec,
    Slice,
)
from relay_engine.domain.references import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.governance import evaluate_handover_gates
from relay_engine.governance.models import (
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateEvaluation,
    GateReason,
    GateReasonCode,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    QualityCheckResult,
    QualityCheckStatus,
    RiskStatus,
    ToolchainChangeStatus,
    TrafficLight,
)
from relay_engine.lifecycle import initialize_lifecycle
from relay_engine.lifecycle.models import (
    Blockage,
    BlockageStatus,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
)
from relay_engine.persistence import (
    GateEvaluationRecord,
    PersistenceIntegrityError,
    insert_baseline,
    insert_gate_evaluation_record,
    insert_handover_gate,
    open_database,
    persist_lifecycle_initialization,
)
from relay_engine.project_slice import (
    MutationMetadata,
    create_project,
    create_slice,
)

NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_A: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
SLICE_B: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789007"
SLICE_C: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789008"
BASELINE_A: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
BASELINE_B: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789009"
GATE_A: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"
GATE_B: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789021"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="owner/relay",
)


def _project(name: str = "Relay") -> Project:
    return Project(id=PROJECT_ID, name=name, primary_repository=REPOSITORY)


def _slice(
    slice_id: SliceId = SLICE_A,
    *,
    title: str = "Board projection",
    parent: SliceId | None = None,
    dependencies: tuple[SliceId, ...] = (),
) -> Slice:
    return Slice(
        id=slice_id,
        project_id=PROJECT_ID,
        title=title,
        scope=ScopeSpec(in_scope=("read durable state",), out_of_scope=("write state",)),
        acceptance_criteria=(
            AcceptanceCriterion(key="A01", statement="Projection is deterministic.", required=True),
        ),
        parent_slice_id=parent,
        dependency_ids=dependencies,
    )


def _baseline(baseline_id: BaselineId = BASELINE_A, sha: str = "a" * 40) -> Baseline:
    return Baseline(
        id=baseline_id,
        project_id=PROJECT_ID,
        commit=CommitRef(repository=REPOSITORY, sha=sha),
        artifact_ids=(),
        decision_ids=(),
    )


def _gate(
    gate_id: HandoverGateId = GATE_A,
    *,
    revision: int = 1,
    baseline_id: BaselineId = BASELINE_A,
    source_phase: LifecyclePhase = LifecyclePhase.PROPOSED,
    target_phase: LifecyclePhase = LifecyclePhase.DEFINING,
    authorization_required: bool = False,
) -> HandoverGate:
    return HandoverGate(
        gate_id=gate_id,
        revision=revision,
        key="define-work",
        slice_id=SLICE_A,
        baseline_id=baseline_id,
        source_phase=source_phase,
        target_phase=target_phase,
        policy=HandoverPolicy.AUTO,
        authorization_required=authorization_required,
    )


def _context(
    lifecycle: SliceLifecycle,
    baseline_id: BaselineId = BASELINE_A,
    *,
    quality_checks: tuple[QualityCheckResult, ...] = (),
    evaluation_outcome: EvaluationOutcome | None = None,
) -> HandoverContext:
    return HandoverContext(
        baseline_id=baseline_id,
        governance_revision=1,
        lifecycle=lifecycle,
        quality_checks=quality_checks,
        evaluation_outcome=evaluation_outcome,
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
    )


def _record(
    record_id: GateEvaluationRecordId,
    gate: HandoverGate,
    context: HandoverContext,
    *,
    recorded_at: datetime = NOW,
    evaluations: tuple[GateEvaluation, ...] | None = None,
) -> GateEvaluationRecord:
    outputs = evaluate_handover_gates((gate,), context) if evaluations is None else evaluations
    return GateEvaluationRecord(
        id=record_id,
        recorded_at=recorded_at,
        gate_refs=(GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision),),
        context=context,
        evaluations=outputs,
    )


def _metadata() -> MutationMetadata:
    return MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Create board test data.")


def _database(path) -> object:
    database = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    create_project(database, _project(), _metadata())
    insert_baseline(database, _baseline())
    create_slice(database, _slice(), _metadata())
    return database


def _persist_initial_lifecycle(database, slice_id: SliceId = SLICE_A) -> SliceLifecycle:
    state, event = initialize_lifecycle(
        slice_id,
        cast(EventId, f"evt_018f47c1-7b2c-7abc-8def-{int(slice_id[-1], 16):012x}"),
        ACTOR,
        NOW,
        "Initialize lifecycle.",
    )
    persist_lifecycle_initialization(database, state, event)
    return state


def test_lifecycle_phases_map_to_exact_fixed_lanes() -> None:
    expected = {
        LifecyclePhase.PROPOSED: BoardLane.SHAPING,
        LifecyclePhase.DEFINING: BoardLane.SHAPING,
        LifecyclePhase.RESEARCHING: BoardLane.SHAPING,
        LifecyclePhase.DESIGNING: BoardLane.SHAPING,
        LifecyclePhase.CONTRACTING: BoardLane.SHAPING,
        LifecyclePhase.PLANNING: BoardLane.SHAPING,
        LifecyclePhase.READY: BoardLane.READY,
        LifecyclePhase.IMPLEMENTING: BoardLane.DELIVERY,
        LifecyclePhase.EVALUATING: BoardLane.EVALUATION,
        LifecyclePhase.REWORK: BoardLane.EVALUATION,
        LifecyclePhase.ACCEPTED: BoardLane.TERMINAL,
        LifecyclePhase.SUPERSEDED: BoardLane.TERMINAL,
        LifecyclePhase.CANCELLED: BoardLane.TERMINAL,
    }
    assert _lane_for(None) is BoardLane.NOT_STARTED
    assert len(expected) == len(LifecyclePhase)
    for phase, lane in expected.items():
        state = SliceLifecycle(
            slice_id=SLICE_A,
            phase=phase,
            validity=LifecycleValidity.CURRENT,
            blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
            revision=0,
            updated_at=NOW,
            superseded_by_slice_id=(SLICE_B if phase is LifecyclePhase.SUPERSEDED else None),
        )
        assert _lane_for(state) is lane
        assert state.phase is phase


def test_board_projection_orders_slices_and_keeps_relationships_navigational(tmp_path) -> None:
    database = _database(tmp_path / "board.sqlite")
    try:
        create_slice(database, _slice(SLICE_B, title="beta"), _metadata())
        create_slice(
            database,
            _slice(SLICE_C, title="Alpha", parent=SLICE_A, dependencies=(SLICE_B,)),
            _metadata(),
        )
        index = project_index(database)
        assert tuple(item.project.id for item in index.projects) == (PROJECT_ID,)
        assert index.projects[0].slice_count == 3

        board = project_board(database, PROJECT_ID)
        assert board.lanes == tuple(BoardLane)
        assert tuple(card.title for card in board.cards) == (
            "Alpha",
            "beta",
            "Board projection",
        )
        child = next(card for card in board.cards if card.slice_id == SLICE_C)
        assert child.lane is BoardLane.NOT_STARTED
        assert child.lifecycle is None
        assert child.parent_slice_id == SLICE_A
        assert child.dependencies[0].slice_id == SLICE_B
        assert child.dependencies[0].title == "beta"
        assert child.evaluation_basis_status is EvaluationBasisStatus.NOT_APPLICABLE
        assert not hasattr(child, "traffic_light")

        detail = slice_detail(database, PROJECT_ID, SLICE_C)
        assert detail.parent is not None and detail.parent.slice_id == SLICE_A
        assert detail.children == ()
        assert detail.dependencies[0].title == "beta"
        assert detail.slice_definition.value.scope.out_of_scope == ("write state",)
    finally:
        database.close()


def test_latest_observation_uses_durable_sequence_and_full_context_identity(tmp_path) -> None:
    database = _database(tmp_path / "observations.sqlite")
    try:
        state = _persist_initial_lifecycle(database)
        gate = _gate()
        insert_handover_gate(database, gate)
        initial_context = _context(state)
        first = _record("geval_018f47c1-7b2c-7abc-8def-123456789030", gate, initial_context)
        duplicate = _record(
            "geval_018f47c1-7b2c-7abc-8def-123456789031",
            gate,
            initial_context,
            recorded_at=NOW.replace(year=2025),
        )
        distinct_context = _context(
            state,
            quality_checks=(QualityCheckResult(key="tests", status=QualityCheckStatus.PASS),),
        )
        distinct = _record("geval_018f47c1-7b2c-7abc-8def-123456789032", gate, distinct_context)
        insert_gate_evaluation_record(database, first)
        insert_gate_evaluation_record(database, duplicate)
        insert_gate_evaluation_record(database, distinct)

        card = project_board(database, PROJECT_ID).cards[0]
        assert card.evaluation_basis_status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS
        assert card.latest_evaluation_record_id == distinct.id
        assert card.latest_evaluation_recorded_at == distinct.recorded_at
        assert card.outgoing_gates[0].evaluation_light is TrafficLight.GREEN
        assert card.outgoing_gates[0].evaluation_basis_status is (
            EvaluationBasisStatus.MATCHING_DURABLE_BASIS
        )
    finally:
        database.close()


def test_evaluation_basis_not_applicable_and_not_evaluated() -> None:
    lifecycle = SliceLifecycle(
        slice_id=SLICE_A,
        phase=LifecyclePhase.PROPOSED,
        validity=LifecycleValidity.CURRENT,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=0,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    assert (
        _evaluation_basis_status(_slice(), None, (_gate(),), None)
        is EvaluationBasisStatus.NOT_APPLICABLE
    )
    assert (
        _evaluation_basis_status(_slice(), lifecycle, (), None)
        is EvaluationBasisStatus.NOT_APPLICABLE
    )
    assert (
        _evaluation_basis_status(_slice(), lifecycle, (_gate(),), None)
        is EvaluationBasisStatus.NOT_EVALUATED
    )


def test_evaluation_basis_mismatches_lifecycle_gates_and_baseline() -> None:
    current = SliceLifecycle(
        slice_id=SLICE_A,
        phase=LifecyclePhase.PROPOSED,
        validity=LifecycleValidity.CURRENT,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=0,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    gate = _gate()
    context = _context(current)
    record = _record("geval_018f47c1-7b2c-7abc-8def-123456789033", gate, context)
    assert (
        _evaluation_basis_status(_slice(), current, (gate,), record)
        is EvaluationBasisStatus.MATCHING_DURABLE_BASIS
    )

    changed_lifecycle = current.model_copy(update={"revision": 1})
    assert (
        _evaluation_basis_status(_slice(), changed_lifecycle, (gate,), record)
        is EvaluationBasisStatus.STALE_DURABLE_BASIS
    )
    changed_phase = current.model_copy(update={"phase": LifecyclePhase.DEFINING})
    assert (
        _evaluation_basis_status(_slice(), changed_phase, (gate,), record)
        is EvaluationBasisStatus.STALE_DURABLE_BASIS
    )
    changed_gate = gate.model_copy(update={"revision": 2})
    assert (
        _evaluation_basis_status(_slice(), current, (changed_gate,), record)
        is EvaluationBasisStatus.STALE_DURABLE_BASIS
    )
    alternate_context = _context(current, BASELINE_B)
    alternate_record = _record(
        "geval_018f47c1-7b2c-7abc-8def-123456789034", gate, alternate_context
    )
    assert (
        _evaluation_basis_status(_slice(), current, (gate,), alternate_record)
        is EvaluationBasisStatus.STALE_DURABLE_BASIS
    )


def test_current_gate_selection_and_gate_reason_order_are_deterministic() -> None:
    lifecycle = SliceLifecycle(
        slice_id=SLICE_A,
        phase=LifecyclePhase.PROPOSED,
        validity=LifecycleValidity.CURRENT,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=0,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    superseded_revision = _gate(GATE_A, revision=1)
    latest_wrong_source = _gate(GATE_A, revision=2, source_phase=LifecyclePhase.READY)
    other_gate = _gate(GATE_B)
    selected = _current_outgoing_gates(
        (other_gate, latest_wrong_source, superseded_revision), lifecycle
    )
    assert tuple(gate.gate_id for gate in selected) == (GATE_B,)

    current_gates = tuple(
        gate.model_copy(
            update={
                "authorization_required": True,
                "required_quality_checks": ("tests",),
            }
        )
        for gate in (other_gate, _gate(GATE_A))
    )
    context = _context(lifecycle)
    evaluations = evaluate_handover_gates(current_gates, context)
    ordered_gates = tuple(sorted(current_gates, key=lambda item: item.gate_id))
    record = GateEvaluationRecord(
        id="geval_018f47c1-7b2c-7abc-8def-123456789039",
        recorded_at=NOW,
        gate_refs=tuple(
            GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision)
            for gate in ordered_gates
        ),
        context=context,
        evaluations=evaluations,
    )
    projections = _gate_projections(
        ordered_gates, record, EvaluationBasisStatus.MATCHING_DURABLE_BASIS
    )
    assert tuple(gate.gate_id for gate in projections) == (GATE_A, GATE_B)
    assert all(gate.evaluation_light is TrafficLight.RED for gate in projections)
    assert all(
        tuple(reason.code for reason in gate.evaluation_reasons)
        == (GateReasonCode.QUALITY_CHECK_MISSING, GateReasonCode.AUTHORIZATION_REQUIRED)
        for gate in projections
    )


def test_full_basis_duplicate_conflict_and_stale_lights_fail_closed() -> None:
    lifecycle = SliceLifecycle(
        slice_id=SLICE_A,
        phase=LifecyclePhase.PROPOSED,
        validity=LifecycleValidity.STALE,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=0,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    gate = _gate(authorization_required=True)
    context = _context(lifecycle)
    first = _record("geval_018f47c1-7b2c-7abc-8def-123456789035", gate, context)
    identical = _record("geval_018f47c1-7b2c-7abc-8def-123456789036", gate, context)
    _check_duplicate_evaluation_outputs((first, identical))
    assert (
        _evaluation_basis_status(_slice(), lifecycle, (gate,), first)
        is EvaluationBasisStatus.MATCHING_DURABLE_BASIS
    )

    different_context = _context(
        lifecycle,
        quality_checks=(QualityCheckResult(key="build", status=QualityCheckStatus.FAIL),),
    )
    distinct = _record("geval_018f47c1-7b2c-7abc-8def-123456789037", gate, different_context)
    _check_duplicate_evaluation_outputs((first, distinct))

    contradictory_evaluation = first.evaluations[0].model_copy(
        update={
            "light": TrafficLight.RED,
            "reasons": (GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
        }
    )
    conflicting = _record(
        "geval_018f47c1-7b2c-7abc-8def-123456789038",
        gate,
        context,
        evaluations=(contradictory_evaluation,),
    )
    with pytest.raises(PersistenceIntegrityError, match="conflicting outputs"):
        _check_duplicate_evaluation_outputs((first, conflicting))

    stale_gates = _gate_projections((gate,), first, EvaluationBasisStatus.STALE_DURABLE_BASIS)
    assert stale_gates[0].evaluation_light is None
    assert stale_gates[0].evaluation_reasons == ()
    assert lifecycle.validity is LifecycleValidity.STALE
    assert EvaluationBasisStatus.STALE_DURABLE_BASIS is not lifecycle.validity
