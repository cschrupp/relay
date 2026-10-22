"""Read-only B4 inspection harness tests against disposable Relay databases."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

import relay_engine.persistence as persistence
from conftest import ensure_test_operational_epoch
from relay_engine.board.service import project_board, slice_detail
from relay_engine.domain.ids import ProjectId, SliceId
from relay_engine.domain.models import AcceptanceCriterion, Project, ScopeSpec, Slice
from relay_engine.domain.references import ActorKind, ActorRef, RepositoryRef
from relay_engine.persistence import open_database
from relay_engine.project_slice import MutationMetadata, create_project, create_slice
from relay_engine.project_slice.errors import ProjectNotFound, SliceNotFound

_HARNESS_PATH = Path(__file__).resolve().parents[2] / "scripts" / "b4_readonly_harness.py"
_HARNESS_SPEC = importlib.util.spec_from_file_location("b4_readonly_harness", _HARNESS_PATH)
assert _HARNESS_SPEC is not None and _HARNESS_SPEC.loader is not None
_HARNESS = importlib.util.module_from_spec(_HARNESS_SPEC)
_HARNESS_SPEC.loader.exec_module(_HARNESS)
inspect_database = _HARNESS.inspect_database
main = _HARNESS.main
open_read_only_database = _HARNESS.open_read_only_database

NOW = datetime(2026, 10, 20, 12, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="owner/relay",
)


def _fixture_database(path: Path):
    database = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    ensure_test_operational_epoch(database)
    metadata = MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Create test fixture.")
    create_project(
        database,
        Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY),
        metadata,
    )
    create_slice(
        database,
        Slice(
            id=SLICE_ID,
            project_id=PROJECT_ID,
            title="Read-only harness fixture",
            scope=ScopeSpec(in_scope=("inspect state",), out_of_scope=("change state",)),
            acceptance_criteria=(
                AcceptanceCriterion(
                    key="A01",
                    statement="The harness exposes current Relay projections.",
                    required=True,
                ),
            ),
        ),
        metadata,
    )
    return database


def _invoke(path: Path) -> tuple[int, str, str]:
    from contextlib import redirect_stderr, redirect_stdout
    from io import StringIO

    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        result = main(
            [
                "--database",
                str(path),
                "--project-id",
                PROJECT_ID,
                "--slice-id",
                SLICE_ID,
            ]
        )
    return result, stdout.getvalue(), stderr.getvalue()


def test_harness_projection_equals_existing_services(tmp_path: Path) -> None:
    path = tmp_path / "relay.sqlite3"
    expected_database = _fixture_database(path)
    try:
        expected_board = project_board(expected_database, PROJECT_ID).model_dump(mode="json")
        expected_detail = slice_detail(expected_database, PROJECT_ID, SLICE_ID).model_dump(
            mode="json"
        )
    finally:
        expected_database.close()

    output = inspect_database(path, PROJECT_ID, SLICE_ID)

    assert output["project_board"] == expected_board
    assert output["slice_detail"] == expected_detail
    assert output["query_only"] == 1
    assert output["schema_version"] == len(persistence.DEFAULT_MIGRATIONS)


def test_read_only_uri_and_query_only_block_writes(tmp_path: Path) -> None:
    path = tmp_path / "relay.sqlite3"
    setup_database = _fixture_database(path)
    setup_database.close()

    database = open_read_only_database(path)
    try:
        assert database.connection.execute("PRAGMA query_only").fetchone()[0] == 1
        assert database.connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1

        database.connection.execute("PRAGMA query_only = OFF")
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            database.connection.execute(
                "UPDATE projects SET payload_json = payload_json WHERE id = ?", (PROJECT_ID,)
            )
    finally:
        database.close()


def test_harness_never_uses_normal_writable_database_opener(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "relay.sqlite3"
    setup_database = _fixture_database(path)
    setup_database.close()

    def fail_if_open_database_is_used(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("open_database must not be used by the B4 harness")

    monkeypatch.setattr(persistence, "open_database", fail_if_open_database_is_used)
    result = inspect_database(path, PROJECT_ID, SLICE_ID)

    assert result["query_only"] == 1


def test_cli_serialization_is_deterministic(tmp_path: Path) -> None:
    path = tmp_path / "relay.sqlite3"
    setup_database = _fixture_database(path)
    setup_database.close()

    first = _invoke(path)
    second = _invoke(path)

    assert first[0] == second[0] == 0
    assert first[1] == second[1]
    assert first[1].endswith("\n")
    decoded = json.loads(first[1])
    assert tuple(decoded) == tuple(sorted(decoded))
    assert decoded["database_path"] == str(path.resolve())


def test_missing_database_fails_without_creating_file(tmp_path: Path) -> None:
    path = tmp_path / "missing.sqlite3"

    result, stdout, stderr = _invoke(path)

    assert result == 2
    assert stdout == ""
    assert stderr.startswith("B4 read-only inspection failed:")
    assert not path.exists()


def test_unknown_project_and_slice_keep_existing_service_errors(tmp_path: Path) -> None:
    path = tmp_path / "relay.sqlite3"
    database = _fixture_database(path)
    database.close()

    with pytest.raises(ProjectNotFound):
        inspect_database(path, "prj_018f47c1-7b2c-7abc-8def-123456789099", SLICE_ID)

    with pytest.raises(SliceNotFound):
        inspect_database(path, PROJECT_ID, "slc_018f47c1-7b2c-7abc-8def-123456789099")
