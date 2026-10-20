"""Disposable-database proof for the bounded B3 Stage A transaction."""

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from conftest import ensure_test_operational_epoch
from relay_engine.b3_materialization import (
    B3_INITIAL_FRONTIER,
    B3_PROJECT_ID,
    B3_SLICE_ID,
    B3_TARGET_SLICE,
    B3MaterializationError,
    B3MaterializationPlan,
    materialize_b3,
)
from relay_engine.board import project_board, project_board_from_connection
from relay_engine.domain.ids import EventId, ProjectId
from relay_engine.domain.models import Baseline, Project, Slice
from relay_engine.domain.references import ActorKind, ActorRef, RepositoryRef
from relay_engine.lifecycle import (
    LifecyclePhase,
    initialize_lifecycle,
)
from relay_engine.persistence import (
    RelayDatabase,
    load_current_lifecycle,
    load_lifecycle_events,
    open_database,
    persist_lifecycle_initialization,
    persist_lifecycle_initialization_from_connection,
    read_transaction,
)
from relay_engine.persistence.database import write_transaction
from relay_engine.persistence.errors import PersistenceError
from relay_engine.persistence.store import insert_baseline
from relay_engine.project_slice import (
    MutationMetadata,
    create_project,
    create_slice,
    get_slice,
    update_slice,
    update_slice_from_connection,
)

NOW = datetime(2026, 10, 20, 12, tzinfo=UTC)
ACTOR = ActorRef(
    id="act_018f47c1-7b2c-7abc-8def-123456789008",
    kind=ActorKind.HUMAN,
    display_name="Stage A test Human",
)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="owner/relay-stage-a-test",
)
MUTATION = MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Stage A disposable test.")


def _initial_frontier() -> Slice:
    return B3_INITIAL_FRONTIER


def _create_fixture(path: Path, *, include_other_records: bool = False) -> RelayDatabase:
    database = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    ensure_test_operational_epoch(database)
    create_project(
        database,
        Project(id=B3_PROJECT_ID, name="Relay", primary_repository=REPOSITORY),
        MUTATION,
    )
    create_slice(database, _initial_frontier(), MUTATION)
    if include_other_records:
        other_project_id: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789099"
        create_project(
            database,
            Project(id=other_project_id, name="Other", primary_repository=REPOSITORY),
            MUTATION,
        )
        insert_baseline(
            database,
            Baseline(
                id="base_018f47c1-7b2c-7abc-8def-123456789099",
                project_id=other_project_id,
                commit={"repository": REPOSITORY, "sha": "a" * 40},
                artifact_ids=(),
                decision_ids=(),
            ),
        )
    return database


def _plan(target: Slice = B3_TARGET_SLICE, revision: int = 1) -> B3MaterializationPlan:
    return B3MaterializationPlan(
        target=target,
        expected_definition_revision=revision,
        mutation=MUTATION,
        event_id=cast(EventId, "evt_018f47c1-7b2c-7abc-8def-123456789099"),
    )


def _table_snapshot(database: RelayDatabase) -> dict[str, tuple[tuple[object, ...], ...]]:
    names = database.connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()
    result: dict[str, tuple[tuple[object, ...], ...]] = {}
    for row in names:
        table_name = row["name"]
        rows = database.connection.execute(
            f'SELECT * FROM "{table_name}" ORDER BY rowid'
        ).fetchall()
        result[table_name] = tuple(tuple(value) for value in rows)
    return result


def test_frozen_b3_payload_is_exact_slice_model_value() -> None:
    design_path = (
        Path(__file__).parents[2]
        / "docs/slices/SLICE_1_10_DOGFOOD_B3_FORWARD_REBASELINE_FIRST_GOVERNED_WORK_DESIGN.md"
    )
    design_text = design_path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", design_text, flags=re.DOTALL)
    assert match is not None
    accepted_payload = json.loads(match.group(1))
    assert B3_TARGET_SLICE.model_dump(mode="json") == accepted_payload
    assert tuple(item.key for item in B3_TARGET_SLICE.acceptance_criteria) == tuple(
        f"A{index:02d}" for index in range(1, 12)
    )
    assert all(item.required for item in B3_TARGET_SLICE.acceptance_criteria)


def test_connection_owned_slice_update_matches_public_wrapper(tmp_path: Path) -> None:
    wrapper_db = _create_fixture(tmp_path / "wrapper.sqlite")
    connection_db = _create_fixture(tmp_path / "connection.sqlite")
    target = B3_TARGET_SLICE.model_copy(update={"title": "Equivalent focused update"})
    try:
        wrapper_result = update_slice(wrapper_db, 1, target, MUTATION)
        with write_transaction(connection_db) as connection:
            connection_result = update_slice_from_connection(connection, 1, target, MUTATION)
        assert connection_result == wrapper_result
        assert get_slice(connection_db, B3_SLICE_ID) == get_slice(wrapper_db, B3_SLICE_ID)
    finally:
        wrapper_db.close()
        connection_db.close()


def test_connection_owned_slice_update_requires_active_transaction(tmp_path: Path) -> None:
    database = _create_fixture(tmp_path / "no-transaction.sqlite")
    try:
        with pytest.raises(PersistenceError, match="active caller-owned transaction"):
            update_slice_from_connection(database.connection, 1, B3_TARGET_SLICE, MUTATION)
    finally:
        database.close()


def test_connection_owned_lifecycle_initialization_matches_public_wrapper(
    tmp_path: Path,
) -> None:
    wrapper_db = _create_fixture(tmp_path / "lifecycle-wrapper.sqlite")
    connection_db = _create_fixture(tmp_path / "lifecycle-connection.sqlite")
    try:
        initial, event = initialize_lifecycle(
            B3_SLICE_ID,
            cast(EventId, "evt_018f47c1-7b2c-7abc-8def-123456789098"),
            ACTOR,
            NOW,
            "Initialize disposable lifecycle.",
        )
        persist_lifecycle_initialization(wrapper_db, initial, event)
        with write_transaction(connection_db) as connection:
            persist_lifecycle_initialization_from_connection(connection, initial, event)
        wrapper_snapshot = _table_snapshot(wrapper_db)
        connection_snapshot = _table_snapshot(connection_db)
        assert connection_snapshot["lifecycle_events"] == wrapper_snapshot["lifecycle_events"]
        assert connection_snapshot["lifecycle_current"] == wrapper_snapshot["lifecycle_current"]
    finally:
        wrapper_db.close()
        connection_db.close()


def test_connection_owned_lifecycle_requires_active_transaction(tmp_path: Path) -> None:
    database = _create_fixture(tmp_path / "lifecycle-no-transaction.sqlite")
    initial, event = initialize_lifecycle(
        B3_SLICE_ID,
        cast(EventId, "evt_018f47c1-7b2c-7abc-8def-123456789098"),
        ACTOR,
        NOW,
        "Initialize disposable lifecycle.",
    )
    try:
        with pytest.raises(PersistenceError, match="active transaction"):
            persist_lifecycle_initialization_from_connection(database.connection, initial, event)
    finally:
        database.close()


def test_connection_owned_board_matches_public_projection(tmp_path: Path) -> None:
    database = _create_fixture(tmp_path / "board.sqlite")
    try:
        expected = project_board(database, B3_PROJECT_ID)
        with read_transaction(database) as connection:
            observed = project_board_from_connection(database, connection, B3_PROJECT_ID)
        assert observed == expected
    finally:
        database.close()


def test_coordinator_updates_definition_and_initializes_proposed_atomically(
    tmp_path: Path,
) -> None:
    database = _create_fixture(tmp_path / "success.sqlite", include_other_records=True)
    before = _table_snapshot(database)
    try:
        result = materialize_b3(database, _plan())
        after = _table_snapshot(database)
        current = get_slice(database, B3_SLICE_ID)
        assert current.value == B3_TARGET_SLICE
        assert current.definition_revision == 2
        assert result.slice_mutation.changed
        assert result.lifecycle.phase is LifecyclePhase.PROPOSED
        assert result.lifecycle.revision == 0
        assert result.initialization_event.resulting_revision == 0
        assert load_current_lifecycle(database, B3_SLICE_ID) == result.lifecycle
        assert load_lifecycle_events(database, B3_SLICE_ID) == (result.initialization_event,)
        assert len([card for card in result.board.cards if card.slice_id == B3_SLICE_ID]) == 1
        assert result.board.cards[0].lifecycle == result.lifecycle
        assert result.board.cards[0].definition_revision == 2
        assert result.slice_mutation.snapshot.value.id == B3_SLICE_ID
        assert result.slice_mutation.snapshot.value.project_id == B3_PROJECT_ID

        allowed_changes = {
            "slice_definition_revisions",
            "slices",
            "lifecycle_events",
            "lifecycle_current",
        }
        assert all(before[name] == after[name] for name in before if name not in allowed_changes)
        before_slices = tuple(row for row in before["slices"] if row[0] != B3_SLICE_ID)
        after_slices = tuple(row for row in after["slices"] if row[0] != B3_SLICE_ID)
        assert after_slices == before_slices
        before_revisions = tuple(
            row for row in before["slice_definition_revisions"] if row[0] != B3_SLICE_ID
        )
        after_revisions = tuple(
            row for row in after["slice_definition_revisions"] if row[0] != B3_SLICE_ID
        )
        assert after_revisions == before_revisions
        assert (
            len(after["slice_definition_revisions"])
            == len(before["slice_definition_revisions"]) + 1
        )
        assert len(after["lifecycle_events"]) == len(before["lifecycle_events"]) + 1
        assert len(after["lifecycle_current"]) == len(before["lifecycle_current"]) + 1
    finally:
        database.close()


@pytest.mark.parametrize("failure_point", ["after_slice_update", "after_lifecycle_initialization"])
def test_coordinator_rolls_back_each_injected_failure(
    tmp_path: Path,
    failure_point: str,
) -> None:
    database = _create_fixture(tmp_path / f"rollback-{failure_point}.sqlite")
    before = _table_snapshot(database)

    def fail_at(stage: str) -> None:
        if stage == failure_point:
            raise RuntimeError(f"injected failure at {stage}")

    try:
        with pytest.raises(RuntimeError, match="injected failure"):
            materialize_b3(database, _plan(), failure_hook=fail_at)
        assert _table_snapshot(database) == before
        assert get_slice(database, B3_SLICE_ID).value == B3_INITIAL_FRONTIER
        assert load_current_lifecycle(database, B3_SLICE_ID) is None
        assert load_lifecycle_events(database, B3_SLICE_ID) == ()
    finally:
        database.close()


def test_coordinator_rejects_stale_definition_revision(tmp_path: Path) -> None:
    database = _create_fixture(tmp_path / "stale.sqlite")
    before = _table_snapshot(database)
    try:
        with pytest.raises(B3MaterializationError, match="revision differs"):
            materialize_b3(database, _plan(revision=2))
        assert _table_snapshot(database) == before
    finally:
        database.close()


def test_coordinator_rejects_existing_lifecycle(tmp_path: Path) -> None:
    database = _create_fixture(tmp_path / "existing-lifecycle.sqlite")
    initial, event = initialize_lifecycle(
        B3_SLICE_ID,
        cast(EventId, "evt_018f47c1-7b2c-7abc-8def-123456789098"),
        ACTOR,
        NOW,
        "Initialize before B3 attempt.",
    )
    persist_lifecycle_initialization(database, initial, event)
    before = _table_snapshot(database)
    try:
        with pytest.raises(B3MaterializationError, match="already initialized"):
            materialize_b3(database, _plan())
        assert _table_snapshot(database) == before
    finally:
        database.close()


def test_coordinator_rejects_existing_handover_history(tmp_path: Path) -> None:
    database = _create_fixture(tmp_path / "handover-history.sqlite")
    insert_baseline(
        database,
        Baseline(
            id="base_018f47c1-7b2c-7abc-8def-123456789097",
            project_id=B3_PROJECT_ID,
            commit={"repository": REPOSITORY, "sha": "b" * 40},
            artifact_ids=(),
            decision_ids=(),
        ),
    )
    database.connection.execute(
        "INSERT INTO handover_gate_revisions "
        "(gate_id, gate_revision, baseline_id, slice_id, payload_json) VALUES (?, ?, ?, ?, ?)",
        (
            "gate_018f47c1-7b2c-7abc-8def-123456789097",
            1,
            "base_018f47c1-7b2c-7abc-8def-123456789097",
            B3_SLICE_ID,
            "{}",
        ),
    )
    before = _table_snapshot(database)
    try:
        with pytest.raises(B3MaterializationError, match="handover history"):
            materialize_b3(database, _plan())
        assert _table_snapshot(database) == before
    finally:
        database.close()


def test_coordinator_rejects_noncanonical_target_without_mutation(tmp_path: Path) -> None:
    database = _create_fixture(tmp_path / "wrong-target.sqlite")
    before = _table_snapshot(database)
    wrong_target = B3_TARGET_SLICE.model_copy(update={"title": "Changed target"})
    try:
        with pytest.raises(B3MaterializationError, match="frozen canonical"):
            materialize_b3(database, _plan(target=wrong_target))
        assert _table_snapshot(database) == before
    finally:
        database.close()
