"""SQLite snapshot, ownership, and fail-closed board projection tests."""

from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest

import relay_engine.board.service as board_service
from relay_engine.board.service import project_board, project_index, slice_detail
from relay_engine.domain.ids import (
    BaselineId,
    EventId,
    ExecutionId,
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
    GateReason,
    GateReasonCode,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    RiskStatus,
    ToolchainChangeStatus,
    TrafficLight,
)
from relay_engine.lifecycle import LifecyclePhase, initialize_lifecycle, transition_phase
from relay_engine.lifecycle.models import SliceLifecycle
from relay_engine.persistence import (
    GateEvaluationRecord,
    PersistenceError,
    PersistenceIntegrityError,
    execute_and_persist_handover,
    insert_baseline,
    insert_gate_evaluation_record,
    insert_handover_gate,
    open_database,
    persist_lifecycle_change,
    persist_lifecycle_initialization,
    read_transaction,
)
from relay_engine.project_slice import (
    MutationMetadata,
    create_project,
    create_slice,
    update_slice,
)

NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
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


def _project() -> Project:
    return Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY)


def _slice(title: str = "Original title") -> Slice:
    return Slice(
        id=SLICE_ID,
        project_id=PROJECT_ID,
        title=title,
        scope=ScopeSpec(in_scope=("read state",), out_of_scope=("mutate state",)),
        acceptance_criteria=(
            AcceptanceCriterion(key="A01", statement="Snapshot is consistent.", required=True),
        ),
    )


def _baseline(baseline_id: BaselineId, sha: str) -> Baseline:
    return Baseline(
        id=baseline_id,
        project_id=PROJECT_ID,
        commit=CommitRef(repository=REPOSITORY, sha=sha),
        artifact_ids=(),
        decision_ids=(),
    )


def _gate(
    gate_id: HandoverGateId,
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
        key="advance",
        slice_id=SLICE_ID,
        baseline_id=baseline_id,
        source_phase=source_phase,
        target_phase=target_phase,
        policy=HandoverPolicy.AUTO,
        authorization_required=authorization_required,
    )


def _context(lifecycle: SliceLifecycle, baseline_id: BaselineId = BASELINE_A) -> HandoverContext:
    return HandoverContext(
        baseline_id=baseline_id,
        governance_revision=1,
        lifecycle=lifecycle,
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
    )


def _setup(path: Path):
    database = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    metadata = MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Create integration fixture.")
    create_project(database, _project(), metadata)
    insert_baseline(database, _baseline(BASELINE_A, "a" * 40))
    create_slice(database, _slice(), metadata)
    return database


def _initialize(database) -> SliceLifecycle:
    state, event = initialize_lifecycle(
        SLICE_ID,
        cast(EventId, "evt_018f47c1-7b2c-7abc-8def-123456789040"),
        ACTOR,
        NOW,
        "Initialize Slice.",
    )
    persist_lifecycle_initialization(database, state, event)
    return state


def _table_snapshot(database) -> dict[str, tuple[tuple[object, ...], ...]]:
    names = database.connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()
    snapshot: dict[str, tuple[tuple[object, ...], ...]] = {}
    for row in names:
        name = row["name"]
        values = database.connection.execute(f'SELECT * FROM "{name}" ORDER BY rowid').fetchall()
        snapshot[name] = tuple(tuple(value) for value in values)
    return snapshot


def test_projection_owns_one_read_transaction_and_does_not_mutate(tmp_path: Path) -> None:
    path = tmp_path / "read-only.sqlite"
    database = _setup(path)
    try:
        before = _table_snapshot(database)
        original = board_service.read_transaction
        entries: list[object] = []

        @contextmanager
        def tracked_read_transaction(db):
            with original(db) as connection:
                entries.append(connection)
                assert connection.in_transaction
                yield connection

        board_service.read_transaction = tracked_read_transaction
        try:
            assert project_index(database).projects[0].slice_count == 1
            assert len(project_board(database, PROJECT_ID).cards) == 1
            assert (
                slice_detail(database, PROJECT_ID, SLICE_ID).slice_definition.value.id == SLICE_ID
            )
        finally:
            board_service.read_transaction = original

        assert len(entries) == 3
        assert all(not database.connection.in_transaction for _ in entries)
        assert _table_snapshot(database) == before
    finally:
        database.close()


def test_read_transaction_rejects_nesting_without_ending_callers_transaction(
    tmp_path: Path,
) -> None:
    database = _setup(tmp_path / "nested-reads.sqlite")
    try:
        database.connection.execute("BEGIN")
        with (
            pytest.raises(PersistenceError, match="cannot be nested"),
            read_transaction(database),
        ):
            pytest.fail("a nested read transaction must not start")
        assert database.connection.in_transaction
    finally:
        database.connection.rollback()
        database.close()


def test_board_request_cannot_mix_pre_and_post_writer_slice_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "snapshot.sqlite"
    reader = _setup(path)
    original_list_slices = board_service.list_slices
    wrote = False

    def update_between_project_and_slice_reads(database, project_id):
        nonlocal wrote
        if not wrote:
            writer = open_database(path, apply_migrations=False)
            try:
                update_slice(
                    writer,
                    1,
                    _slice("Changed while projecting"),
                    MutationMetadata(
                        actor=ACTOR,
                        occurred_at=NOW + timedelta(seconds=1),
                        reason="Concurrent writer update.",
                    ),
                )
            finally:
                writer.close()
            wrote = True
        return original_list_slices(database, project_id)

    monkeypatch.setattr(board_service, "list_slices", update_between_project_and_slice_reads)
    try:
        board = project_board(reader, PROJECT_ID)
        assert wrote
        assert board.project.name == "Relay"
        assert board.cards[0].title == "Original title"
        assert original_list_slices(reader, PROJECT_ID)[0].value.title == "Changed while projecting"
        assert not reader.connection.in_transaction
    finally:
        reader.close()


def test_lifecycle_current_history_disagreement_fails_closed(tmp_path: Path) -> None:
    database = _setup(tmp_path / "lifecycle-corrupt.sqlite")
    try:
        state = _initialize(database)
        changed = state.model_copy(update={"phase": LifecyclePhase.READY})
        database.connection.execute(
            "UPDATE lifecycle_current SET payload_json = ? WHERE slice_id = ?",
            (changed.model_dump_json(), SLICE_ID),
        )
        with pytest.raises(PersistenceIntegrityError, match="history does not match"):
            project_board(database, PROJECT_ID)
        assert not database.connection.in_transaction
    finally:
        database.close()


def test_malformed_typed_payload_and_definition_history_fail_closed(tmp_path: Path) -> None:
    database = _setup(tmp_path / "definition-corrupt.sqlite")
    try:
        database.connection.execute(
            "UPDATE slices SET payload_json = '{' WHERE id = ?", (SLICE_ID,)
        )
        with pytest.raises(PersistenceIntegrityError, match="stored Slice payload is invalid"):
            project_board(database, PROJECT_ID)
        assert not database.connection.in_transaction
    finally:
        database.close()

    database = _setup(tmp_path / "history-corrupt.sqlite")
    try:
        changed_payload = _slice("Different historical title").model_dump_json()
        database.connection.execute("DROP TRIGGER slice_definition_revisions_no_update")
        database.connection.execute(
            "UPDATE slice_definition_revisions SET payload_json = ? "
            "WHERE slice_id = ? AND definition_revision = 1",
            (changed_payload, SLICE_ID),
        )
        with pytest.raises(PersistenceIntegrityError, match="latest definition revision"):
            project_board(database, PROJECT_ID)
    finally:
        database.close()


def test_mixed_current_gate_baselines_fail_closed(tmp_path: Path) -> None:
    database = _setup(tmp_path / "mixed-baselines.sqlite")
    try:
        insert_baseline(database, _baseline(BASELINE_B, "b" * 40))
        _initialize(database)
        insert_handover_gate(database, _gate(GATE_A, baseline_id=BASELINE_A))
        insert_handover_gate(database, _gate(GATE_B, baseline_id=BASELINE_B))
        with pytest.raises(PersistenceIntegrityError, match="different durable baselines"):
            project_board(database, PROJECT_ID)
        assert not database.connection.in_transaction
    finally:
        database.close()


def test_full_basis_conflicting_evaluations_fail_closed(tmp_path: Path) -> None:
    database = _setup(tmp_path / "evaluation-conflict.sqlite")
    try:
        state = _initialize(database)
        gate = _gate(GATE_A)
        insert_handover_gate(database, gate)
        context = _context(state)
        evaluations = evaluate_handover_gates((gate,), context)
        first = GateEvaluationRecord(
            id=cast(GateEvaluationRecordId, "geval_018f47c1-7b2c-7abc-8def-123456789041"),
            recorded_at=NOW,
            gate_refs=(GateRevisionRef(gate_id=GATE_A, gate_revision=1),),
            context=context,
            evaluations=evaluations,
        )
        conflicting_output = evaluations[0].model_copy(
            update={
                "light": TrafficLight.RED,
                "reasons": (GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
            }
        )
        second = GateEvaluationRecord(
            id=cast(GateEvaluationRecordId, "geval_018f47c1-7b2c-7abc-8def-123456789042"),
            recorded_at=NOW + timedelta(seconds=1),
            gate_refs=first.gate_refs,
            context=context,
            evaluations=(conflicting_output,),
        )
        insert_gate_evaluation_record(database, first)
        insert_gate_evaluation_record(database, second)
        with pytest.raises(PersistenceIntegrityError, match="conflicting outputs"):
            project_board(database, PROJECT_ID)
        assert not database.connection.in_transaction
    finally:
        database.close()


def _ready_lifecycle(database) -> SliceLifecycle:
    state = _initialize(database)
    phases = (
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.READY,
    )
    for offset, phase in enumerate(phases, start=1):
        updated, event = transition_phase(
            state,
            phase,
            cast(EventId, f"evt_018f47c1-7b2c-7abc-8def-{40 + offset:012x}"),
            ACTOR,
            NOW + timedelta(seconds=offset),
            f"Move to {phase.value}.",
        )
        persist_lifecycle_change(database, state.revision, updated, event)
        state = updated
    return state


def test_detail_uses_accepted_loader_to_detect_execution_evaluation_conflict(
    tmp_path: Path,
) -> None:
    database = _setup(tmp_path / "execution-corrupt.sqlite")
    try:
        state = _ready_lifecycle(database)
        gate = _gate(
            GATE_A,
            source_phase=LifecyclePhase.READY,
            target_phase=LifecyclePhase.IMPLEMENTING,
        )
        insert_handover_gate(database, gate)
        _, _, _, evidence, execution = execute_and_persist_handover(
            database,
            (gate,),
            GATE_A,
            _context(state),
            state.revision,
            cast(GateEvaluationRecordId, "geval_018f47c1-7b2c-7abc-8def-123456789043"),
            NOW + timedelta(seconds=10),
            cast(ExecutionId, "exec_018f47c1-7b2c-7abc-8def-123456789044"),
            cast(EventId, "evt_018f47c1-7b2c-7abc-8def-123456789047"),
            ACTOR,
            NOW + timedelta(seconds=11),
            "Begin implementation.",
        )
        contradictory = evidence.evaluations[0].model_copy(
            update={
                "light": TrafficLight.RED,
                "reasons": (GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
            }
        )
        modified = evidence.model_copy(update={"evaluations": (contradictory,)})
        database.connection.execute(
            "UPDATE gate_evaluation_records SET payload_json = ? WHERE record_id = ?",
            (modified.model_dump_json(), evidence.id),
        )

        with pytest.raises(PersistenceIntegrityError, match="execution does not match"):
            slice_detail(database, PROJECT_ID, SLICE_ID)
        assert not database.connection.in_transaction
        assert execution.execution_id == "exec_018f47c1-7b2c-7abc-8def-123456789044"
    finally:
        database.close()


def test_execution_evidence_is_ordered_by_result_revision_then_id(tmp_path: Path) -> None:
    database = _setup(tmp_path / "execution-order.sqlite")
    try:
        ready = _ready_lifecycle(database)
        first_gate = _gate(
            GATE_A,
            source_phase=LifecyclePhase.READY,
            target_phase=LifecyclePhase.IMPLEMENTING,
        )
        second_gate = _gate(
            GATE_B,
            source_phase=LifecyclePhase.IMPLEMENTING,
            target_phase=LifecyclePhase.EVALUATING,
        )
        insert_handover_gate(database, first_gate)
        insert_handover_gate(database, second_gate)
        first_state, _, _, _, first_execution = execute_and_persist_handover(
            database,
            (first_gate,),
            GATE_A,
            _context(ready),
            ready.revision,
            cast(GateEvaluationRecordId, "geval_018f47c1-7b2c-7abc-8def-123456789050"),
            NOW + timedelta(seconds=10),
            cast(ExecutionId, "exec_018f47c1-7b2c-7abc-8def-123456789051"),
            cast(EventId, "evt_018f47c1-7b2c-7abc-8def-123456789052"),
            ACTOR,
            NOW + timedelta(seconds=11),
            "Begin implementation.",
        )
        _, _, _, _, second_execution = execute_and_persist_handover(
            database,
            (second_gate,),
            GATE_B,
            _context(first_state),
            first_state.revision,
            cast(GateEvaluationRecordId, "geval_018f47c1-7b2c-7abc-8def-123456789053"),
            NOW + timedelta(seconds=12),
            cast(ExecutionId, "exec_018f47c1-7b2c-7abc-8def-123456789054"),
            cast(EventId, "evt_018f47c1-7b2c-7abc-8def-123456789055"),
            ACTOR,
            NOW + timedelta(seconds=13),
            "Begin evaluation.",
        )

        detail = slice_detail(database, PROJECT_ID, SLICE_ID)
        assert tuple(record.execution_id for record in detail.relevant_execution_records) == (
            first_execution.execution_id,
            second_execution.execution_id,
        )
        assert tuple(
            record.resulting_lifecycle_revision for record in detail.relevant_execution_records
        ) == (
            first_execution.resulting_lifecycle_revision,
            second_execution.resulting_lifecycle_revision,
        )
    finally:
        database.close()
