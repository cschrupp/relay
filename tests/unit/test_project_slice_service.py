"""Slice 1.4 definition administration contract coverage."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier

import pytest

import relay_engine.persistence as persistence
from relay_engine.domain import (
    AcceptanceCriterion,
    ActorKind,
    ActorRef,
    Project,
    RepositoryRef,
    ScopeSpec,
    Slice,
)
from relay_engine.domain.ids import ProjectId, SliceId
from relay_engine.lifecycle import LifecyclePhase, initialize_lifecycle, transition_phase
from relay_engine.persistence import (
    open_database,
    persist_lifecycle_change,
    persist_lifecycle_initialization,
)
from relay_engine.persistence.errors import PersistenceIntegrityError
from relay_engine.project_slice import (
    CrossProjectSliceReference,
    DefinitionRevisionConflict,
    MutationMetadata,
    ProjectAlreadyExists,
    ProjectDeleteForbidden,
    ProjectIdentifierRetired,
    ProjectNotFound,
    ProjectRepositoryImmutable,
    SliceDefinitionFrozen,
    SliceDeleteForbidden,
    SliceDependencyCycle,
    SliceHasDownstreamDependents,
    SliceIdentifierRetired,
    SliceNotFound,
    SliceParentCycle,
    create_project,
    create_slice,
    delete_project,
    delete_slice,
    get_project,
    get_project_revision,
    get_slice,
    get_slice_revision,
    list_projects,
    list_slices,
    update_project,
    update_slice,
)

NOW = datetime(2026, 9, 30, 12, tzinfo=UTC)
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
SYSTEM = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789009", kind=ActorKind.SYSTEM)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
PROJECT_ID_2: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789011"
SLICE_A: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789002"
SLICE_B: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789003"
SLICE_C: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789004"
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789005", host="github.com", path="owner/repo"
)


def _metadata(*, actor: ActorRef = ACTOR, occurred_at: datetime = NOW) -> MutationMetadata:
    return MutationMetadata(actor=actor, occurred_at=occurred_at, reason="Human definition change.")


def _project(project_id: ProjectId = PROJECT_ID, *, name: str = "Relay") -> Project:
    repository = REPOSITORY
    if project_id == PROJECT_ID_2:
        repository = repository.model_copy(
            update={"id": "repo_018f47c1-7b2c-7abc-8def-123456789015", "path": "owner/other"}
        )
    return Project(id=project_id, name=name, primary_repository=repository)


def _slice(
    slice_id: SliceId = SLICE_A,
    *,
    project_id: ProjectId = PROJECT_ID,
    parent: SliceId | None = None,
    dependencies: tuple[SliceId, ...] = (),
    title: str = "Foundation",
) -> Slice:
    return Slice(
        id=slice_id,
        project_id=project_id,
        title=title,
        scope=ScopeSpec(in_scope=("define the work",), out_of_scope=("execute agents",)),
        acceptance_criteria=(AcceptanceCriterion(key="A01", statement="Works.", required=True),),
        parent_slice_id=parent,
        dependency_ids=dependencies,
    )


@pytest.fixture
def db(tmp_path):
    database = open_database(
        tmp_path / "definitions.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    yield database
    database.close()


def _create_project(database, value: Project | None = None):
    return create_project(database, value or _project(), _metadata())


def _create_slice(database, value: Slice | None = None):
    return create_slice(database, value or _slice(), _metadata())


def test_project_create_exact_retry_snapshot_and_sorted_list(db) -> None:
    later = _project("prj_018f47c1-7b2c-7abc-8def-123456789010", name="Later")
    create_project(db, later, _metadata())
    created = _create_project(db)
    assert created.changed is True
    assert created.snapshot.definition_revision == 1
    assert get_project(db, PROJECT_ID) == created.snapshot
    assert create_project(db, _project(), _metadata()).changed is False
    assert tuple(item.value.id for item in list_projects(db)) == (PROJECT_ID, later.id)
    assert (
        db.connection.execute(
            "SELECT count(*) FROM project_definition_revisions WHERE project_id = ?", (PROJECT_ID,)
        ).fetchone()[0]
        == 1
    )


def test_project_create_different_value_and_nonhuman_metadata_fail(db) -> None:
    _create_project(db)
    with pytest.raises(ProjectAlreadyExists):
        create_project(db, _project(name="Changed"), _metadata())
    with pytest.raises(ValueError):
        create_project(db, _project(PROJECT_ID_2), _metadata(actor=SYSTEM))
    with pytest.raises(ValueError):
        MutationMetadata(actor=ACTOR, occurred_at=datetime(2026, 9, 30), reason="bad time")
    with pytest.raises(ValueError):
        MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="  ")


def test_project_update_changes_name_and_requires_strict_cas_even_for_exact_target(db) -> None:
    _create_project(db)
    updated = update_project(db, 1, _project(name="Renamed"), _metadata())
    assert updated.changed and updated.snapshot.definition_revision == 2
    with pytest.raises(DefinitionRevisionConflict):
        update_project(db, 1, _project(name="Renamed"), _metadata())
    assert update_project(db, 2, _project(name="Renamed"), _metadata()).changed is False
    with pytest.raises(ProjectRepositoryImmutable):
        update_project(
            db,
            2,
            _project().model_copy(
                update={"primary_repository": _project(PROJECT_ID_2).primary_repository}
            ),
            _metadata(),
        )
    assert get_project_revision(db, PROJECT_ID, 1).operation.value == "CREATE"


def test_slice_create_graph_validation_and_deterministic_reads(db) -> None:
    _create_project(db)
    b = _slice(SLICE_B, title="B")
    c = _slice(SLICE_C, title="C")
    create_slice(db, b, _metadata())
    create_slice(db, c, _metadata())
    a = _slice(parent=SLICE_B, dependencies=(SLICE_C,))
    create_slice(db, a, _metadata())
    assert get_slice(db, SLICE_A).value == a
    assert tuple(item.value.id for item in list_slices(db, PROJECT_ID)) == (
        SLICE_A,
        SLICE_B,
        SLICE_C,
    )
    assert create_slice(db, a, _metadata()).changed is False
    with pytest.raises(ProjectNotFound):
        list_slices(db, PROJECT_ID_2)


def test_slice_create_requires_project_and_rejects_cross_project_edges(db) -> None:
    _create_project(db)
    other = _project(PROJECT_ID_2)
    create_project(db, other, _metadata())
    foreign_id: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789012"
    create_slice(db, _slice(foreign_id, project_id=PROJECT_ID_2), _metadata())
    with pytest.raises(CrossProjectSliceReference):
        create_slice(db, _slice(parent=foreign_id), _metadata())
    with pytest.raises(CrossProjectSliceReference):
        create_slice(db, _slice(dependencies=(foreign_id,)), _metadata())
    with pytest.raises(CrossProjectSliceReference):
        create_slice(db, _slice(project_id="prj_018f47c1-7b2c-7abc-8def-123456789099"), _metadata())


def test_slice_parent_and_dependency_cycles_are_rejected(db) -> None:
    _create_project(db)
    create_slice(db, _slice(SLICE_A), _metadata())
    create_slice(db, _slice(SLICE_B), _metadata())
    update_slice(db, 1, _slice(SLICE_A, parent=SLICE_B), _metadata())
    with pytest.raises(SliceParentCycle):
        update_slice(db, 1, _slice(SLICE_B, parent=SLICE_A), _metadata())
    update_slice(db, 2, _slice(SLICE_A, dependencies=(SLICE_B,)), _metadata())
    with pytest.raises(SliceDependencyCycle):
        update_slice(db, 1, _slice(SLICE_B, dependencies=(SLICE_A,)), _metadata())


def test_slice_update_has_strict_cas_and_permanent_lifecycle_freeze(db) -> None:
    _create_project(db)
    _create_slice(db)
    changed = update_slice(db, 1, _slice(title="Edited"), _metadata())
    assert changed.snapshot.definition_revision == 2
    with pytest.raises(DefinitionRevisionConflict):
        update_slice(db, 1, _slice(title="Edited"), _metadata())
    assert update_slice(db, 2, _slice(title="Edited"), _metadata()).changed is False
    state, event = initialize_lifecycle(
        SLICE_A, "evt_018f47c1-7b2c-7abc-8def-123456789007", ACTOR, NOW, "Start."
    )
    persist_lifecycle_initialization(db, state, event)
    with pytest.raises(SliceDefinitionFrozen):
        update_slice(db, 2, _slice(title="Later"), _metadata())


def test_downstream_dependency_freezes_target_definition(db) -> None:
    _create_project(db)
    _create_slice(db)
    create_slice(db, _slice(SLICE_B, dependencies=(SLICE_A,)), _metadata())
    with pytest.raises(SliceHasDownstreamDependents):
        update_slice(db, 1, _slice(title="Changed"), _metadata())


def test_handover_gate_revision_freezes_slice_definition(db) -> None:
    _create_project(db)
    _create_slice(db)
    db.connection.execute(
        "INSERT INTO baselines(id, project_id, payload_json) VALUES (?, ?, '{}')",
        ("base_018f47c1-7b2c-7abc-8def-123456789013", PROJECT_ID),
    )
    db.connection.execute(
        "INSERT INTO handover_gate_revisions(gate_id, gate_revision, baseline_id, "
        "slice_id, payload_json) "
        "VALUES ('gate_test', 1, 'base_018f47c1-7b2c-7abc-8def-123456789013', ?, '{}')",
        (SLICE_A,),
    )
    with pytest.raises(SliceDefinitionFrozen):
        update_slice(db, 1, _slice(title="Changed"), _metadata())


def test_lifecycle_advanced_to_defining_remains_a_permanent_freeze(db) -> None:
    _create_project(db)
    _create_slice(db)
    state, initialization = initialize_lifecycle(
        SLICE_A, "evt_018f47c1-7b2c-7abc-8def-123456789007", ACTOR, NOW, "Start."
    )
    persist_lifecycle_initialization(db, state, initialization)
    defining, event = transition_phase(
        state,
        LifecyclePhase.DEFINING,
        "evt_018f47c1-7b2c-7abc-8def-123456789016",
        ACTOR,
        NOW,
        "Define.",
    )
    persist_lifecycle_change(db, 0, defining, event)
    with pytest.raises(SliceDefinitionFrozen):
        update_slice(db, 1, _slice(title="Changed"), _metadata())


def test_slice_delete_tombstone_retires_identity_and_preserves_history(db) -> None:
    _create_project(db)
    _create_slice(db)
    result = delete_slice(db, SLICE_A, 1, _metadata())
    assert result.deleted and result.definition_revision == 2
    assert get_slice_revision(db, SLICE_A, 2).operation.value == "DELETE"
    retry = delete_slice(db, SLICE_A, 1, _metadata())
    assert retry.already_deleted and retry.definition_revision == 2
    with pytest.raises(SliceIdentifierRetired):
        create_slice(db, _slice(), _metadata())
    with pytest.raises(SliceNotFound):
        get_slice(db, SLICE_A)


def test_slice_delete_rejects_stale_revision(db) -> None:
    _create_project(db)
    _create_slice(db)
    update_slice(db, 1, _slice(title="Renamed"), _metadata())
    with pytest.raises(DefinitionRevisionConflict):
        delete_slice(db, SLICE_A, 1, _metadata())


@pytest.mark.parametrize(
    ("table", "columns", "values", "project_blocker"),
    [
        (
            "baselines",
            "id, project_id, payload_json",
            ("base_018f47c1-7b2c-7abc-8def-123456789013", PROJECT_ID, "{}"),
            "baselines",
        ),
        (
            "github_installations",
            "project_id, installation_id, state_revision, payload_json",
            (PROJECT_ID, 3, 1, "{}"),
            "github_installations",
        ),
        (
            "repository_mutation_authorizations",
            "authorization_id, project_id, subject_digest, payload_json",
            ("rma_018f47c1-7b2c-7abc-8def-123456789014", PROJECT_ID, "digest", "{}"),
            "repository_mutation_authorizations",
        ),
    ],
)
def test_project_delete_explicit_authority_blockers(
    db, table, columns, values, project_blocker
) -> None:
    _create_project(db)
    db.connection.execute(
        f"INSERT INTO {table}({columns}) VALUES ({', '.join('?' for _ in values)})", values
    )
    with pytest.raises(ProjectDeleteForbidden) as error:
        delete_project(db, PROJECT_ID, 1, _metadata())
    assert project_blocker in error.value.blockers


def test_project_delete_is_blocked_by_slice_and_unused_project_can_be_retired(db) -> None:
    _create_project(db)
    _create_slice(db)
    with pytest.raises(ProjectDeleteForbidden):
        delete_project(db, PROJECT_ID, 1, _metadata())
    delete_slice(db, SLICE_A, 1, _metadata())
    deleted = delete_project(db, PROJECT_ID, 1, _metadata())
    assert deleted.deleted and deleted.definition_revision == 2
    assert get_project_revision(db, PROJECT_ID, 2).operation.value == "DELETE"
    with pytest.raises(ProjectIdentifierRetired):
        create_project(db, _project(), _metadata())
    assert delete_project(db, PROJECT_ID, 1, _metadata()).already_deleted
    with pytest.raises(ProjectNotFound):
        get_project(db, PROJECT_ID_2)


def test_project_delete_rejects_stale_revision(db) -> None:
    _create_project(db)
    update_project(db, 1, _project(name="Renamed"), _metadata())
    with pytest.raises(DefinitionRevisionConflict):
        delete_project(db, PROJECT_ID, 1, _metadata())


def test_residual_foreign_key_delete_failure_rolls_back_tombstone(db) -> None:
    _create_project(db)
    db.connection.execute(
        "CREATE TABLE external_project_reference (project_id TEXT REFERENCES projects(id))"
    )
    db.connection.execute(
        "INSERT INTO external_project_reference(project_id) VALUES (?)", (PROJECT_ID,)
    )
    with pytest.raises(PersistenceIntegrityError):
        delete_project(db, PROJECT_ID, 1, _metadata())
    assert get_project(db, PROJECT_ID).definition_revision == 1
    assert (
        db.connection.execute(
            "SELECT count(*) FROM project_definition_revisions WHERE project_id = ?", (PROJECT_ID,)
        ).fetchone()[0]
        == 1
    )


@pytest.mark.parametrize(
    ("blocker", "expected"),
    [
        ("lifecycle_current", "lifecycle_current"),
        ("lifecycle_events", "lifecycle_events"),
        ("handover_gate_revisions", "handover_gate_revisions"),
        ("gate_evaluation_records", "gate_evaluation_records"),
        ("executions", "executions"),
    ],
)
def test_slice_delete_governance_blockers_are_explicit(db, blocker, expected) -> None:
    _create_project(db)
    _create_slice(db)
    db.connection.execute(
        "INSERT INTO baselines(id, project_id, payload_json) VALUES (?, ?, '{}')",
        ("base_018f47c1-7b2c-7abc-8def-123456789013", PROJECT_ID),
    )
    if blocker == "lifecycle_current":
        db.connection.execute(
            "INSERT INTO lifecycle_current(slice_id, revision, payload_json) VALUES (?, 0, '{}')",
            (SLICE_A,),
        )
    elif blocker == "lifecycle_events":
        db.connection.execute(
            "INSERT INTO lifecycle_events(event_id, slice_id, event_type, resulting_revision, "
            "occurred_at, payload_json) VALUES ('e', ?, 'E', 0, '2026-09-30T12:00:00Z', '{}')",
            (SLICE_A,),
        )
    elif blocker == "handover_gate_revisions":
        db.connection.execute(
            "INSERT INTO handover_gate_revisions(gate_id, gate_revision, baseline_id, "
            "slice_id, payload_json) VALUES ('g', 1, "
            "'base_018f47c1-7b2c-7abc-8def-123456789013', ?, '{}')",
            (SLICE_A,),
        )
    elif blocker == "gate_evaluation_records":
        db.connection.execute(
            "INSERT INTO gate_evaluation_records(record_id, baseline_id, slice_id, payload_json) "
            "VALUES ('geval', 'base_018f47c1-7b2c-7abc-8def-123456789013', ?, '{}')",
            (SLICE_A,),
        )
    else:
        db.connection.execute(
            "INSERT INTO lifecycle_events(event_id, slice_id, event_type, resulting_revision, "
            "occurred_at, payload_json) VALUES ('e', ?, 'E', 0, '2026-09-30T12:00:00Z', '{}')",
            (SLICE_A,),
        )
        db.connection.execute(
            "INSERT INTO gate_evaluation_records(record_id, baseline_id, slice_id, payload_json) "
            "VALUES ('geval', 'base_018f47c1-7b2c-7abc-8def-123456789013', ?, '{}')",
            (SLICE_A,),
        )
        db.connection.execute(
            "INSERT INTO executions(execution_id, evaluation_record_id, event_id, slice_id, "
            "resulting_lifecycle_revision, payload_json) VALUES ('exec', 'geval', 'e', ?, 1, '{}')",
            (SLICE_A,),
        )
    with pytest.raises(SliceDeleteForbidden) as error:
        delete_slice(db, SLICE_A, 1, _metadata())
    assert expected in error.value.blockers


@pytest.mark.parametrize("relation", ["parent", "dependency"])
def test_slice_delete_rejects_child_or_incoming_dependency(db, relation) -> None:
    _create_project(db)
    _create_slice(db)
    child = (
        _slice(SLICE_B, parent=SLICE_A)
        if relation == "parent"
        else _slice(SLICE_B, dependencies=(SLICE_A,))
    )
    create_slice(db, child, _metadata())
    with pytest.raises(SliceDeleteForbidden):
        delete_slice(db, SLICE_A, 1, _metadata())


def test_project_and_slice_definition_history_is_database_append_only(db) -> None:
    _create_project(db)
    _create_slice(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.connection.execute(
            "DELETE FROM project_definition_revisions WHERE project_id = ?", (PROJECT_ID,)
        )
    with pytest.raises(sqlite3.IntegrityError):
        db.connection.execute(
            "UPDATE slice_definition_revisions SET reason = 'changed' WHERE slice_id = ?",
            (SLICE_A,),
        )


def test_current_payload_history_mismatch_fails_closed(db) -> None:
    _create_project(db)
    db.connection.execute(
        "UPDATE projects SET payload_json = ? WHERE id = ?",
        (
            '{"id":"prj_018f47c1-7b2c-7abc-8def-123456789001","name":"tampered","primary_repository":{"host":"github.com","id":"repo_018f47c1-7b2c-7abc-8def-123456789005","path":"owner/repo","schema_version":1},"schema_version":1}',
            PROJECT_ID,
        ),
    )
    with pytest.raises(PersistenceIntegrityError):
        get_project(db, PROJECT_ID)


def test_project_revision_payload_identity_corruption_fails_closed_without_repair(db) -> None:
    _create_project(db)
    tampered = _project(PROJECT_ID_2).model_dump_json()
    db.connection.execute("DROP TRIGGER project_definition_revisions_no_update")
    db.connection.execute(
        "UPDATE project_definition_revisions SET payload_json = ? WHERE project_id = ?",
        (tampered, PROJECT_ID),
    )

    with pytest.raises(PersistenceIntegrityError):
        get_project_revision(db, PROJECT_ID, 1)

    stored = db.connection.execute(
        "SELECT payload_json FROM project_definition_revisions WHERE project_id = ?",
        (PROJECT_ID,),
    ).fetchone()[0]
    assert Project.model_validate_json(stored).id == PROJECT_ID_2


def test_slice_revision_project_identity_corruption_fails_closed_without_repair(db) -> None:
    _create_project(db)
    _create_slice(db)
    tampered = _slice(SLICE_A, project_id=PROJECT_ID_2).model_dump_json()
    db.connection.execute("DROP TRIGGER slice_definition_revisions_no_update")
    db.connection.execute(
        "UPDATE slice_definition_revisions SET payload_json = ? WHERE slice_id = ?",
        (tampered, SLICE_A),
    )

    with pytest.raises(PersistenceIntegrityError):
        get_slice_revision(db, SLICE_A, 1)

    stored = db.connection.execute(
        "SELECT payload_json, project_id FROM slice_definition_revisions WHERE slice_id = ?",
        (SLICE_A,),
    ).fetchone()
    assert Slice.model_validate_json(stored["payload_json"]).project_id == PROJECT_ID_2
    assert stored["project_id"] == PROJECT_ID


def test_two_connections_cannot_both_update_from_same_revision(tmp_path) -> None:
    path = tmp_path / "concurrent.sqlite"
    setup = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    _create_project(setup)
    setup.close()

    def attempt(name: str) -> str:
        database = open_database(path, apply_migrations=False)
        try:
            update_project(database, 1, _project(name=name), _metadata())
            return "UPDATED"
        except DefinitionRevisionConflict:
            return "CONFLICT"
        finally:
            database.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(executor.map(attempt, ("First", "Second")))
    assert sorted(results) == ["CONFLICT", "UPDATED"]


def test_two_connections_serialize_update_vs_delete_from_same_revision(tmp_path) -> None:
    path = tmp_path / "update-delete-race.sqlite"
    setup = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    _create_project(setup)
    setup.close()
    start = Barrier(2)

    def attempt_update() -> str:
        database = open_database(path, apply_migrations=False)
        try:
            start.wait()
            update_project(database, 1, _project(name="Concurrent update"), _metadata())
            return "UPDATE_COMMITTED"
        except DefinitionRevisionConflict:
            return "UPDATE_CONFLICT"
        except ProjectNotFound:
            return "UPDATE_NOT_FOUND"
        finally:
            database.close()

    def attempt_delete() -> str:
        database = open_database(path, apply_migrations=False)
        try:
            start.wait()
            result = delete_project(database, PROJECT_ID, 1, _metadata())
            return "DELETE_COMMITTED" if result.deleted else "DELETE_ALREADY_DONE"
        except DefinitionRevisionConflict:
            return "DELETE_CONFLICT"
        finally:
            database.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        update_result, delete_result = tuple(
            future.result()
            for future in (executor.submit(attempt_update), executor.submit(attempt_delete))
        )

    assert (update_result, delete_result) in {
        ("UPDATE_COMMITTED", "DELETE_CONFLICT"),
        ("UPDATE_NOT_FOUND", "DELETE_COMMITTED"),
    }


def test_slice_1_4_exact_authority_and_design_lineage_are_recorded() -> None:
    root = Path(__file__).parents[2]
    plan = (root / "docs/BUILD_PLAN_V0_5.md").read_text(encoding="utf-8")
    authorization = (root / "docs/reviews/SLICE_1_4_IMPLEMENTATION_AUTHORIZATION.md").read_text(
        encoding="utf-8"
    )
    baseline = (root / "docs/CURRENT_BASELINE.md").read_text(encoding="utf-8")

    assert "Human-authorized subject baseline:\n670996ec43d77526adb0ea540c81a57d6e83453b" in plan
    assert "Authority-recording design parent:\n1eaece23e31d831bfd2b27e55a898df389cc45fc" in plan
    assert "Revision 1:\n430b1e1ff5eb06c26d4c63225b455feda14b6710" in plan
    assert "Accepted Revision 2 design head:\nf5a678da360b96701a1f9635d3703b49dc16e779" in plan
    assert "RLY-S14-AUTH-001" in authorization
    assert "RLY-S14-AUTH-001 — AUTHORIZED" in plan
    assert "Canonical rework baseline:\ndfe6c20c8f65b42fe69b7d315956a91d2a29487c" in baseline
    assert "Prior implementation candidate:\ne5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d" in baseline
    assert "RLY-S14-EVAL-001 — REWORK" in baseline


def test_raw_runtime_project_and_slice_creation_are_not_publicly_exported() -> None:
    assert not hasattr(persistence, "insert_project")
    assert not hasattr(persistence, "insert_slice")
