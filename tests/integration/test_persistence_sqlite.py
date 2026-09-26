"""Contract tests for SQLite persistence and durable governance causality."""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest
from pydantic import TypeAdapter

from relay_engine.domain.ids import (
    ArtifactId,
    BaselineId,
    EventId,
    EvidenceId,
    ExecutionId,
    GateEvaluationRecordId,
    HandoverGateId,
    ProjectId,
    SliceId,
)
from relay_engine.domain.models import Artifact, Baseline, Decision, Evidence, Project, Slice
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.governance import (
    AuthorizationGrant,
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    HumanApprovalDecision,
    HumanApprovalValue,
    HumanChoiceDecision,
    RiskStatus,
    ToolchainChangeStatus,
)
from relay_engine.lifecycle import (
    LifecycleInitialized,
    LifecyclePhase,
    PhaseChanged,
    SliceLifecycle,
    initialize_lifecycle,
    transition_phase,
)
from relay_engine.persistence import (
    ConcurrencyConflict,
    Migration,
    MigrationError,
    PersistenceError,
    PersistenceIntegrityError,
    apply_migrations,
    execute_and_persist_handover,
    insert_artifact,
    insert_authorization_grant,
    insert_baseline,
    insert_decision,
    insert_evidence,
    insert_handover_gate,
    insert_human_decision,
    insert_project,
    insert_slice,
    load_artifact,
    load_authorization_grant,
    load_baseline,
    load_current_lifecycle,
    load_decision,
    load_evidence,
    load_execution_record,
    load_gate_evaluation_record,
    load_handover_gate,
    load_handover_gates,
    load_human_decision,
    load_lifecycle_events,
    load_project,
    load_slice,
    open_database,
    persist_lifecycle_change,
    persist_lifecycle_initialization,
    verify_slice_history,
)

NOW = datetime(2026, 9, 23, 12, tzinfo=UTC)
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
GATE_ID: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"


def _id(prefix: str, number: int) -> str:
    return f"{prefix}018f47c1-7b2c-7abc-8def-{number:012x}"


def _fixture(name: str, model: type[object]) -> object:
    path = Path("tests/fixtures/domain/v1") / f"{name}.json"
    return TypeAdapter(model).validate_json(path.read_text())


def _setup(database: object) -> None:
    insert_project(database, cast(Project, _fixture("project", Project)))
    insert_baseline(database, cast(Baseline, _fixture("baseline", Baseline)))
    insert_slice(database, cast(Slice, _fixture("slice", Slice)))


def _initialized(database: object) -> tuple[SliceLifecycle, LifecycleInitialized]:
    state, event = initialize_lifecycle(SLICE_ID, _id("evt_", 1), ACTOR, NOW, "Initialize.")
    persist_lifecycle_initialization(database, state, event)
    return state, event


def _ready(database: object) -> SliceLifecycle:
    state, _ = _initialized(database)
    updated, event = transition_phase(
        state, LifecyclePhase.READY, _id("evt_", 2), ACTOR, NOW + timedelta(seconds=1), "Ready."
    )
    persist_lifecycle_change(database, 0, updated, event)
    return updated


def _gate() -> HandoverGate:
    return HandoverGate(
        gate_id=GATE_ID,
        revision=1,
        key="implement",
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        source_phase=LifecyclePhase.READY,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.AUTO,
    )


def _context(state: SliceLifecycle, **changes: object) -> HandoverContext:
    values: dict[str, object] = {
        "baseline_id": BASELINE_ID,
        "governance_revision": 1,
        "lifecycle": state,
        "change_surface_status": ChangeSurfaceStatus.WITHIN_DECLARED,
        "risk_status": RiskStatus.CLEAR,
        "toolchain_change_status": ToolchainChangeStatus.NONE,
    }
    values.update(changes)
    return HandoverContext.model_validate(values)


@pytest.fixture
def db(tmp_path: Path):
    database = open_database(
        tmp_path / "relay.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    try:
        _setup(database)
        yield database
    finally:
        database.close()


def test_lifecycle_initialization_persists_revision_zero_atomically(db: object) -> None:
    state, event = initialize_lifecycle(SLICE_ID, _id("evt_", 1), ACTOR, NOW, "Initialize.")
    persist_lifecycle_initialization(db, state, event)
    assert load_current_lifecycle(db, SLICE_ID) == state
    assert load_lifecycle_events(db, SLICE_ID) == (event,)
    verify_slice_history(db, SLICE_ID)


def test_duplicate_lifecycle_initialization_conflicts(db: object) -> None:
    state, event = _initialized(db)
    with pytest.raises(ConcurrencyConflict):
        persist_lifecycle_initialization(db, state, event)


def test_partial_initialization_state_is_integrity_error(db: object) -> None:
    state, event = initialize_lifecycle(SLICE_ID, _id("evt_", 1), ACTOR, NOW, "Initialize.")
    db.connection.execute(
        "INSERT INTO lifecycle_current(slice_id, revision, payload_json) VALUES (?, ?, ?)",
        (SLICE_ID, 0, state.model_dump_json()),
    )
    with pytest.raises(PersistenceIntegrityError):
        persist_lifecycle_initialization(db, state, event)


def test_lifecycle_write_rejects_event_snapshot_mismatch(db: object) -> None:
    state, _ = _initialized(db)
    updated, event = transition_phase(
        state, LifecyclePhase.READY, _id("evt_", 2), ACTOR, NOW + timedelta(seconds=1), "Ready."
    )
    mismatch = updated.model_copy(update={"phase": LifecyclePhase.EVALUATING})
    with pytest.raises(PersistenceIntegrityError):
        persist_lifecycle_change(db, 0, mismatch, event)
    assert load_current_lifecycle(db, SLICE_ID) == state
    assert len(load_lifecycle_events(db, SLICE_ID)) == 1


def test_two_connections_cannot_commit_same_revision(tmp_path: Path) -> None:
    first = open_database(
        tmp_path / "shared.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    second = open_database(tmp_path / "shared.sqlite", apply_migrations=False)
    try:
        _setup(first)
        state, _ = _initialized(first)
        next_state, event = transition_phase(
            state, LifecyclePhase.READY, _id("evt_", 2), ACTOR, NOW + timedelta(seconds=1), "Ready."
        )
        persist_lifecycle_change(first, 0, next_state, event)
        with pytest.raises(ConcurrencyConflict):
            persist_lifecycle_change(second, 0, next_state, event)
    finally:
        first.close()
        second.close()


def test_restart_recovers_lifecycle_from_file_database(tmp_path: Path) -> None:
    path = tmp_path / "restart.sqlite"
    first = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    _setup(first)
    state = _ready(first)
    first.close()
    second = open_database(path, apply_migrations=False)
    try:
        assert load_current_lifecycle(second, SLICE_ID) == state
        verify_slice_history(second, SLICE_ID)
    finally:
        second.close()


def test_persisted_execution_records_complete_causal_evidence(db: object) -> None:
    state = _ready(db)
    gate = _gate()
    insert_handover_gate(db, gate)
    updated, event, selected, evidence, execution = execute_and_persist_handover(
        db,
        (gate,),
        GATE_ID,
        _context(state),
        1,
        cast(GateEvaluationRecordId, _id("geval_", 1)),
        NOW + timedelta(seconds=2),
        cast(ExecutionId, _id("exec_", 1)),
        cast(EventId, _id("evt_", 3)),
        ACTOR,
        NOW + timedelta(seconds=3),
        "Begin implementation.",
    )
    assert updated.phase is LifecyclePhase.IMPLEMENTING
    assert isinstance(event, PhaseChanged)
    assert selected.light.value == "GREEN"
    assert evidence.evaluations == (selected,)
    assert execution.gate_evaluation_record_id == evidence.id
    assert load_gate_evaluation_record(db, evidence.id) == evidence
    assert load_execution_record(db, execution.execution_id) == execution
    assert load_current_lifecycle(db, SLICE_ID) == updated
    verify_slice_history(db, SLICE_ID)


def test_persisted_execution_rejects_unknown_baseline(db: object) -> None:
    state = _ready(db)
    with pytest.raises(PersistenceIntegrityError):
        execute_and_persist_handover(
            db,
            (),
            GATE_ID,
            _context(state, baseline_id="base_018f47c1-7b2c-7abc-8def-123456789099"),
            1,
            cast(GateEvaluationRecordId, _id("geval_", 1)),
            NOW,
            cast(ExecutionId, _id("exec_", 1)),
            cast(EventId, _id("evt_", 3)),
            ACTOR,
            NOW + timedelta(seconds=2),
            "Attempt.",
        )


def test_index_column_payload_mismatch_is_integrity_error(db: object) -> None:
    gate = _gate()
    insert_handover_gate(db, gate)
    payload = json.loads(
        db.connection.execute(
            "SELECT payload_json FROM handover_gate_revisions WHERE gate_id = ?", (GATE_ID,)
        ).fetchone()[0]
    )
    payload["revision"] = 2
    db.connection.execute(
        "UPDATE handover_gate_revisions SET payload_json = ? WHERE gate_id = ?",
        (json.dumps(payload), GATE_ID),
    )

    with pytest.raises(PersistenceIntegrityError):
        load_handover_gate(db, GATE_ID, 1)


def test_duplicate_static_domain_identity_is_rejected(db: object) -> None:
    project = cast(Project, _fixture("project", Project))
    with pytest.raises(PersistenceError):
        insert_project(db, project)


def test_migration_pending_batch_rolls_back_as_one_unit(tmp_path: Path) -> None:
    connection = sqlite3.connect(tmp_path / "migration.sqlite", isolation_level=None)
    connection.row_factory = sqlite3.Row
    first = Migration(
        1,
        "create one",
        (
            "CREATE TABLE relay_schema_migrations (version INTEGER PRIMARY KEY, "
            "name TEXT, applied_at TEXT, checksum TEXT)",
        ),
    )
    second = Migration(2, "pending one", ("CREATE TABLE temporary_table (id INTEGER)",))
    third = Migration(3, "pending failure", ("CREATE TABLE broken (id INTEGER)", "INVALID SQL"))
    with pytest.raises(MigrationError):
        apply_migrations(connection, (first, second, third), applied_at=NOW)
    tables = {
        row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert "temporary_table" not in tables
    assert "relay_schema_migrations" not in tables
    connection.close()


def test_static_domain_records_round_trip_from_typed_fixtures(db: object) -> None:
    project = cast(Project, _fixture("project", Project))
    baseline = cast(Baseline, _fixture("baseline", Baseline))
    slice_value = cast(Slice, _fixture("slice", Slice))
    artifact = cast(Artifact, _fixture("artifact", Artifact))
    decision = cast(Decision, _fixture("decision", Decision))
    evidence = cast(Evidence, _fixture("evidence", Evidence))
    insert_artifact(db, artifact)
    insert_decision(db, decision)
    insert_evidence(db, evidence)
    assert load_project(db, project.id) == project
    assert load_baseline(db, baseline.id) == baseline
    assert load_slice(db, slice_value.id) == slice_value
    assert load_artifact(db, artifact.id) == artifact
    assert load_decision(db, decision.id) == decision
    assert load_evidence(db, evidence.id) == evidence


def test_stored_domain_payload_corruption_is_integrity_error(db: object) -> None:
    artifact = cast(Artifact, _fixture("artifact", Artifact))
    insert_artifact(db, artifact)
    db.connection.execute(
        "UPDATE artifacts SET payload_json = ? WHERE id = ?", ("{broken", artifact.id)
    )
    with pytest.raises(PersistenceIntegrityError):
        load_artifact(db, artifact.id)


def test_gate_revisions_are_insert_only_and_load_in_revision_order(db: object) -> None:
    original = _gate()
    later = original.model_copy(update={"revision": 2, "key": "implement-v2"})
    insert_handover_gate(db, later)
    insert_handover_gate(db, original)
    assert load_handover_gates(db, GATE_ID) == (original, later)
    with pytest.raises(PersistenceError):
        insert_handover_gate(db, original)
    with pytest.raises(PersistenceError):
        insert_handover_gate(db, later)


def test_authorization_and_human_approval_round_trip(db: object) -> None:
    gate = _gate().model_copy(update={"authorization_required": True})
    grant = _authorization(gate)
    decision_gate = gate.model_copy(update={"policy": HandoverPolicy.HUMAN_APPROVAL})
    decision = _approval(decision_gate)
    insert_authorization_grant(db, grant)
    insert_human_decision(db, decision)
    assert load_authorization_grant(db, grant.authorization_id) == grant
    assert load_human_decision(db, decision.decision_id) == decision


def test_human_choice_decision_round_trip(db: object) -> None:
    gate = _gate().model_copy(update={"policy": HandoverPolicy.HUMAN_CHOICE})
    decision = HumanChoiceDecision(
        decision_id=cast(str, _id("hdec_", 42)),
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        selected_gate_id=gate.gate_id,
        selected_gate_revision=gate.revision,
        choice_gate_refs=(GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision),),
        lifecycle_revision=1,
        governance_revision=1,
        actor=ACTOR,
        occurred_at=NOW,
        reason="Choose the exact outgoing path.",
    )
    insert_human_decision(db, decision)
    assert load_human_decision(db, decision.decision_id) == decision


def _attempt_persisted_execution(
    database: object,
    state: SliceLifecycle,
    gates: tuple[HandoverGate, ...],
    context: HandoverContext,
) -> None:
    execute_and_persist_handover(
        database,
        gates,
        GATE_ID,
        context,
        expected_lifecycle_revision=1,
        evaluation_record_id=cast(GateEvaluationRecordId, _id("geval_", 10)),
        evaluation_recorded_at=NOW + timedelta(seconds=2),
        execution_id=cast(ExecutionId, _id("exec_", 10)),
        event_id=cast(EventId, _id("evt_", 10)),
        actor=ACTOR,
        occurred_at=NOW + timedelta(seconds=3),
        reason="Execute persisted handover.",
    )


def _authorization(gate: HandoverGate) -> AuthorizationGrant:
    return AuthorizationGrant(
        authorization_id=cast(str, _id("auth_", 10)),
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        gate_id=gate.gate_id,
        gate_revision=gate.revision,
        actor=ACTOR,
        granted_at=NOW,
        reason="Authorize this exact gate.",
    )


def _approval(gate: HandoverGate) -> HumanApprovalDecision:
    return HumanApprovalDecision(
        decision_id=cast(str, _id("hdec_", 10)),
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        gate_id=gate.gate_id,
        gate_revision=gate.revision,
        lifecycle_revision=1,
        governance_revision=1,
        actor=ACTOR,
        occurred_at=NOW,
        decision=HumanApprovalValue.APPROVE,
        reason="Approve the exact handover.",
    )


def test_persisted_execution_rejects_unpersisted_gate_revision(db: object) -> None:
    state = _ready(db)
    with pytest.raises(PersistenceIntegrityError):
        _attempt_persisted_execution(db, state, (_gate(),), _context(state))


def test_persisted_execution_rejects_gate_payload_mismatch(db: object) -> None:
    state = _ready(db)
    gate = _gate()
    insert_handover_gate(db, gate)
    row = db.connection.execute(
        "SELECT payload_json FROM handover_gate_revisions WHERE gate_id = ?", (GATE_ID,)
    ).fetchone()
    payload = json.loads(row[0])
    payload["key"] = "different-key"
    db.connection.execute(
        "UPDATE handover_gate_revisions SET payload_json = ? WHERE gate_id = ?",
        (json.dumps(payload), GATE_ID),
    )
    with pytest.raises(PersistenceIntegrityError):
        _attempt_persisted_execution(db, state, (gate,), _context(state))


def test_persisted_execution_rejects_unpersisted_authorization(db: object) -> None:
    state = _ready(db)
    gate = _gate().model_copy(update={"authorization_required": True})
    insert_handover_gate(db, gate)
    context = _context(state, authorization_grants=(_authorization(gate),))
    with pytest.raises(PersistenceIntegrityError):
        _attempt_persisted_execution(db, state, (gate,), context)


def test_persisted_execution_rejects_authorization_payload_mismatch(db: object) -> None:
    state = _ready(db)
    gate = _gate().model_copy(update={"authorization_required": True})
    grant = _authorization(gate)
    insert_handover_gate(db, gate)
    insert_authorization_grant(db, grant)
    row = db.connection.execute(
        "SELECT payload_json FROM authorization_grants WHERE authorization_id = ?",
        (grant.authorization_id,),
    ).fetchone()
    payload = json.loads(row[0])
    payload["reason"] = "different reason"
    db.connection.execute(
        "UPDATE authorization_grants SET payload_json = ? WHERE authorization_id = ?",
        (json.dumps(payload), grant.authorization_id),
    )
    with pytest.raises(PersistenceIntegrityError):
        _attempt_persisted_execution(
            db, state, (gate,), _context(state, authorization_grants=(grant,))
        )


def test_persisted_execution_rejects_unpersisted_human_decision(db: object) -> None:
    state = _ready(db)
    gate = _gate().model_copy(update={"policy": HandoverPolicy.HUMAN_APPROVAL})
    insert_handover_gate(db, gate)
    context = _context(state, human_decisions=(_approval(gate),))
    with pytest.raises(PersistenceIntegrityError):
        _attempt_persisted_execution(db, state, (gate,), context)


def test_persisted_execution_rejects_human_decision_payload_mismatch(db: object) -> None:
    state = _ready(db)
    gate = _gate().model_copy(update={"policy": HandoverPolicy.HUMAN_APPROVAL})
    decision = _approval(gate)
    insert_handover_gate(db, gate)
    insert_human_decision(db, decision)
    row = db.connection.execute(
        "SELECT payload_json FROM human_decisions WHERE decision_id = ?",
        (decision.decision_id,),
    ).fetchone()
    payload = json.loads(row[0])
    payload["reason"] = "different reason"
    db.connection.execute(
        "UPDATE human_decisions SET payload_json = ? WHERE decision_id = ?",
        (json.dumps(payload), decision.decision_id),
    )
    with pytest.raises(PersistenceIntegrityError):
        _attempt_persisted_execution(
            db, state, (gate,), _context(state, human_decisions=(decision,))
        )


def test_persisted_execution_rejects_stale_dependency_projection(db: object) -> None:
    state = _ready(db)
    dependency_id: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789099"
    dependency = cast(Slice, _fixture("slice", Slice)).model_copy(
        update={"id": dependency_id, "title": "Dependency"}
    )
    insert_slice(db, dependency)
    durable, event = initialize_lifecycle(
        dependency_id, cast(EventId, _id("evt_", 20)), ACTOR, NOW, "Initialize dependency."
    )
    persist_lifecycle_initialization(db, durable, event)
    stale = durable.model_copy(update={"revision": 1})
    gate = _gate().model_copy(update={"required_dependency_slice_ids": (dependency_id,)})
    insert_handover_gate(db, gate)
    with pytest.raises(ConcurrencyConflict):
        _attempt_persisted_execution(
            db, state, (gate,), _context(state, dependency_lifecycles=(stale,))
        )


def test_persisted_execution_rejects_unknown_available_artifact(db: object) -> None:
    state = _ready(db)
    gate = _gate()
    insert_handover_gate(db, gate)
    artifact_id = cast(ArtifactId, _id("art_", 99))
    with pytest.raises(PersistenceIntegrityError):
        _attempt_persisted_execution(
            db, state, (gate,), _context(state, available_artifact_ids=(artifact_id,))
        )


def test_persisted_execution_rejects_unknown_available_evidence(db: object) -> None:
    state = _ready(db)
    gate = _gate()
    insert_handover_gate(db, gate)
    evidence_id = cast(EvidenceId, _id("evd_", 99))
    with pytest.raises(PersistenceIntegrityError):
        _attempt_persisted_execution(
            db, state, (gate,), _context(state, available_evidence_ids=(evidence_id,))
        )


def test_evaluation_record_preserves_exact_context(db: object) -> None:
    state = _ready(db)
    gate = _gate()
    insert_handover_gate(db, gate)
    context = _context(state, evaluation_outcome=EvaluationOutcome.ACCEPT)
    _, _, _, evidence, _ = execute_and_persist_handover(
        db,
        (gate,),
        GATE_ID,
        context,
        1,
        cast(GateEvaluationRecordId, _id("geval_", 31)),
        NOW + timedelta(seconds=2),
        cast(ExecutionId, _id("exec_", 31)),
        cast(EventId, _id("evt_", 31)),
        ACTOR,
        NOW + timedelta(seconds=3),
        "Execute.",
    )
    assert evidence.context == context
    assert evidence.context.evaluation_outcome is EvaluationOutcome.ACCEPT


def test_evaluation_record_preserves_exact_gate_set(db: object) -> None:
    state = _ready(db)
    first = _gate()
    second_id = cast(HandoverGateId, _id("gate_", 21))
    second = first.model_copy(
        update={
            "gate_id": second_id,
            "key": "other-path",
            "source_phase": LifecyclePhase.IMPLEMENTING,
            "target_phase": LifecyclePhase.EVALUATING,
        }
    )
    insert_handover_gate(db, first)
    insert_handover_gate(db, second)
    _, _, _, evidence, _ = execute_and_persist_handover(
        db,
        (second, first),
        GATE_ID,
        _context(state),
        1,
        cast(GateEvaluationRecordId, _id("geval_", 32)),
        NOW + timedelta(seconds=2),
        cast(ExecutionId, _id("exec_", 32)),
        cast(EventId, _id("evt_", 32)),
        ACTOR,
        NOW + timedelta(seconds=3),
        "Execute.",
    )
    assert tuple(ref.gate_id for ref in evidence.gate_refs) == tuple(sorted((GATE_ID, second_id)))


def test_evaluation_record_preserves_full_canonical_evaluation_tuple(db: object) -> None:
    state = _ready(db)
    first = _gate()
    second = first.model_copy(
        update={
            "gate_id": cast(HandoverGateId, _id("gate_", 22)),
            "key": "other-path",
            "source_phase": LifecyclePhase.IMPLEMENTING,
            "target_phase": LifecyclePhase.EVALUATING,
        }
    )
    insert_handover_gate(db, first)
    insert_handover_gate(db, second)
    _, _, _, evidence, _ = execute_and_persist_handover(
        db,
        (second, first),
        GATE_ID,
        _context(state),
        1,
        cast(GateEvaluationRecordId, _id("geval_", 33)),
        NOW + timedelta(seconds=2),
        cast(ExecutionId, _id("exec_", 33)),
        cast(EventId, _id("evt_", 33)),
        ACTOR,
        NOW + timedelta(seconds=3),
        "Execute.",
    )
    assert tuple(item.gate_id for item in evidence.evaluations) == tuple(
        sorted((GATE_ID, cast(HandoverGateId, _id("gate_", 22))))
    )
    lights = {item.gate_id: item.light.value for item in evidence.evaluations}
    assert lights[GATE_ID] == "GREEN"
    assert lights[cast(HandoverGateId, _id("gate_", 22))] == "RED"


def test_execution_references_exact_evaluation_record(db: object) -> None:
    state = _ready(db)
    gate = _gate()
    insert_handover_gate(db, gate)
    _, _, _, evidence, execution = execute_and_persist_handover(
        db,
        (gate,),
        GATE_ID,
        _context(state),
        1,
        cast(GateEvaluationRecordId, _id("geval_", 34)),
        NOW + timedelta(seconds=2),
        cast(ExecutionId, _id("exec_", 34)),
        cast(EventId, _id("evt_", 34)),
        ACTOR,
        NOW + timedelta(seconds=3),
        "Execute.",
    )
    assert execution.gate_evaluation_record_id == evidence.id
    assert load_execution_record(db, execution.execution_id) == execution
    assert load_gate_evaluation_record(db, evidence.id) == evidence


def test_execution_selected_evaluation_matches_evidence_record(db: object) -> None:
    state = _ready(db)
    gate = _gate()
    insert_handover_gate(db, gate)
    _, _, selected, evidence, _ = execute_and_persist_handover(
        db,
        (gate,),
        GATE_ID,
        _context(state),
        1,
        cast(GateEvaluationRecordId, _id("geval_", 35)),
        NOW + timedelta(seconds=2),
        cast(ExecutionId, _id("exec_", 35)),
        cast(EventId, _id("evt_", 35)),
        ACTOR,
        NOW + timedelta(seconds=3),
        "Execute.",
    )
    assert (
        next(item for item in evidence.evaluations if item.gate_id == selected.gate_id) == selected
    )
