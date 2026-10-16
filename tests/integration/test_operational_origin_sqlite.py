"""Migration-v7 and append-only operational-origin persistence contracts."""

import sqlite3
from datetime import UTC, datetime

import pytest

from conftest import ensure_test_operational_epoch
from relay_engine.domain.ids import ProjectId
from relay_engine.domain.models import AcceptanceCriterion, Project, ScopeSpec, Slice
from relay_engine.domain.references import ActorKind, ActorRef, RepositoryRef
from relay_engine.persistence import (
    DEFAULT_MIGRATIONS,
    apply_migrations,
    load_operational_history_epoch_resolution,
    open_database,
    verify_schema,
)
from relay_engine.project_slice import MutationMetadata, create_project
from relay_engine.project_slice.origin import OriginResolutionState

NOW = datetime(2026, 10, 15, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789021"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789022", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789023",
    host="github.com",
    path="owner/relay",
)


def _project() -> Project:
    return Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY)


def _slice() -> Slice:
    return Slice(
        id="slc_018f47c1-7b2c-7abc-8def-123456789024",
        project_id=PROJECT_ID,
        title="Legacy row",
        scope=ScopeSpec(in_scope=("preserve bytes",), out_of_scope=("infer origin",)),
        acceptance_criteria=(
            AcceptanceCriterion(key="A01", statement="Migration is structural.", required=True),
        ),
    )


def test_migration_v7_creates_two_empty_tables_and_required_integrity_objects(tmp_path) -> None:
    database = open_database(
        tmp_path / "pg1-v7.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    try:
        versions = tuple(
            row[0]
            for row in database.connection.execute(
                "SELECT version FROM relay_schema_migrations ORDER BY version"
            )
        )
        assert versions == (1, 2, 3, 4, 5, 6, 7)
        assert DEFAULT_MIGRATIONS[-1].version == 7
        assert (
            database.connection.execute(
                "SELECT count(*) FROM operational_history_epochs"
            ).fetchone()[0]
            == 0
        )
        assert (
            database.connection.execute(
                "SELECT count(*) FROM operational_origin_records"
            ).fetchone()[0]
            == 0
        )
        verify_schema(database.connection)
        for name in (
            "operational_history_epochs_no_update",
            "operational_history_epochs_no_delete",
            "operational_origin_records_no_update",
            "operational_origin_records_no_delete",
            "operational_origin_records_subject_matches_insert",
        ):
            assert database.connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='trigger' AND name=?", (name,)
            ).fetchone()
    finally:
        database.close()


def test_v7_upgrade_preserves_legacy_payload_bytes_and_performs_no_backfill(tmp_path) -> None:
    path = tmp_path / "v6-populated.sqlite"
    connection = sqlite3.connect(path, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    apply_migrations(connection, DEFAULT_MIGRATIONS[:6], applied_at=NOW)
    project = _project()
    slice_value = _slice()
    connection.execute(
        "INSERT INTO projects(id, payload_json) VALUES (?, ?)",
        (project.id, project.model_dump_json()),
    )
    connection.execute(
        "INSERT INTO slices(id, project_id, payload_json) VALUES (?, ?, ?)",
        (slice_value.id, slice_value.project_id, slice_value.model_dump_json()),
    )
    prior_bytes = tuple(
        tuple(row)
        for row in connection.execute(
            "SELECT id, payload_json FROM projects UNION ALL "
            "SELECT id, payload_json FROM slices ORDER BY id"
        )
    )
    apply_migrations(connection, DEFAULT_MIGRATIONS, applied_at=NOW)
    after_bytes = tuple(
        tuple(row)
        for row in connection.execute(
            "SELECT id, payload_json FROM projects UNION ALL "
            "SELECT id, payload_json FROM slices ORDER BY id"
        )
    )
    assert after_bytes == prior_bytes
    assert connection.execute("SELECT count(*) FROM operational_history_epochs").fetchone()[0] == 0
    assert connection.execute("SELECT count(*) FROM operational_origin_records").fetchone()[0] == 0
    connection.close()


def test_epoch_and_origin_assertions_are_append_only_and_singleton(tmp_path) -> None:
    database = open_database(
        tmp_path / "append-only.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    ensure_test_operational_epoch(database)
    try:
        epoch = database.connection.execute("SELECT * FROM operational_history_epochs").fetchone()
        assert epoch is not None
        with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
            database.connection.execute(
                "INSERT INTO operational_history_epochs SELECT * FROM operational_history_epochs"
            )
        create_project(
            database,
            _project(),
            MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Create origin fixture."),
        )
        origin = database.connection.execute(
            "SELECT * FROM operational_origin_records WHERE subject_id = ?", (PROJECT_ID,)
        ).fetchone()
        assert origin is not None
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            database.connection.execute(
                "UPDATE operational_history_epochs SET epoch_digest = 'tampered' "
                "WHERE epoch_slot = 1"
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            database.connection.execute(
                "DELETE FROM operational_history_epochs WHERE epoch_slot = 1"
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            database.connection.execute(
                "UPDATE operational_origin_records SET origin = 'PRE_GENESIS' WHERE record_id = ?",
                (origin["record_id"],),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            database.connection.execute(
                "DELETE FROM operational_origin_records WHERE record_id = ?", (origin["record_id"],)
            )
    finally:
        database.close()


def test_existing_entity_without_origin_remains_a_read_only_diagnostic(tmp_path) -> None:
    database = open_database(
        tmp_path / "unclassified.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    ensure_test_operational_epoch(database)
    try:
        value = _project()
        database.connection.execute(
            "INSERT INTO projects(id, payload_json, definition_revision) VALUES (?, ?, 1)",
            (value.id, value.model_dump_json()),
        )
        database.connection.execute(
            "INSERT INTO project_definition_revisions(project_id, definition_revision, operation, "
            "payload_json) VALUES (?, 1, 'SEED', ?)",
            (value.id, value.model_dump_json()),
        )
        from relay_engine.project_slice import resolve_project_origin

        resolution = resolve_project_origin(database, value.id)
        assert resolution.state is OriginResolutionState.NOT_ESTABLISHED
        assert resolution.origin is None
    finally:
        database.close()


def test_corrupt_epoch_payload_fails_closed_without_repair(tmp_path) -> None:
    database = open_database(
        tmp_path / "corrupt-epoch.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    ensure_test_operational_epoch(database)
    try:
        database.connection.execute("DROP TRIGGER operational_history_epochs_no_update")
        database.connection.execute(
            "UPDATE operational_history_epochs SET epoch_digest = ?",
            ("sha256:" + "f" * 64,),
        )

        resolution = load_operational_history_epoch_resolution(database)

        assert resolution.state is OriginResolutionState.NOT_ESTABLISHED
        assert resolution.epoch is None
        assert resolution.record_ids
        with pytest.raises(AssertionError, match="invalid epoch state"):
            ensure_test_operational_epoch(database)
    finally:
        database.close()


def test_epoch_loader_rejects_multiple_roots_even_if_constraints_are_bypassed(tmp_path) -> None:
    database = open_database(
        tmp_path / "multiple-epochs.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    ensure_test_operational_epoch(database)
    try:
        row = database.connection.execute("SELECT * FROM operational_history_epochs").fetchone()
        database.connection.execute("PRAGMA ignore_check_constraints = ON")
        database.connection.execute(
            "INSERT INTO operational_history_epochs SELECT 2, epoch_id || '-duplicate', "
            "genesis_cut_at, source_commit_sha, genesis_package_artifact_id, "
            "genesis_package_path, genesis_package_digest, package_acceptance_artifact_id, "
            "package_acceptance_digest, epoch_digest, payload_json FROM operational_history_epochs"
        )
        assert row is not None

        resolution = load_operational_history_epoch_resolution(database)

        assert resolution.state is OriginResolutionState.NOT_ESTABLISHED
        assert len(resolution.record_ids) == 2
    finally:
        database.close()
