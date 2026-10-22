"""Read existing Relay board projections through a read-only SQLite connection."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from relay_engine.board.service import project_board, slice_detail
from relay_engine.domain.ids import ProjectId, SliceId
from relay_engine.persistence import PersistenceError, RelayDatabase, verify_schema
from relay_engine.project_slice.errors import ProjectSliceError


def open_read_only_database(path: str | Path) -> RelayDatabase:
    """Open an existing Relay database without permitting SQLite writes."""

    resolved_path = Path(path).expanduser().resolve()
    uri = f"{resolved_path.as_uri()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True, isolation_level=None)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA query_only = ON")

        query_only = connection.execute("PRAGMA query_only").fetchone()
        if query_only is None or int(query_only[0]) != 1:
            raise RuntimeError("SQLite query_only could not be enabled")
        foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()
        if foreign_keys is None or int(foreign_keys[0]) != 1:
            raise RuntimeError("SQLite foreign-key enforcement could not be enabled")

        verify_schema(connection)
        return RelayDatabase(path=str(resolved_path), connection=connection)
    except BaseException:
        connection.close()
        raise


def inspect_database(
    database_path: str | Path,
    project_id: ProjectId,
    slice_id: SliceId,
) -> dict[str, Any]:
    """Return the existing board and slice-detail projections as JSON values."""

    database = open_read_only_database(database_path)
    try:
        connection = database.connection
        query_only = int(connection.execute("PRAGMA query_only").fetchone()[0])
        schema_row = connection.execute(
            "SELECT MAX(version) AS schema_version FROM relay_schema_migrations"
        ).fetchone()
        if schema_row is None or schema_row["schema_version"] is None:
            raise RuntimeError("Relay schema version is unavailable")

        board = project_board(database, project_id)
        detail = slice_detail(database, project_id, slice_id)
        return {
            "schema_version": int(schema_row["schema_version"]),
            "database_path": database.path,
            "project_id": project_id,
            "slice_id": slice_id,
            "query_only": query_only,
            "project_board": board.model_dump(mode="json"),
            "slice_detail": detail.model_dump(mode="json"),
        }
    finally:
        database.close()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--slice-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Print deterministic JSON projections, or a concise error to stderr."""

    args = _parser().parse_args(argv)
    try:
        project_id = TypeAdapter(ProjectId).validate_python(args.project_id)
        slice_id = TypeAdapter(SliceId).validate_python(args.slice_id)
        result = inspect_database(args.database, project_id, slice_id)
    except (
        OSError,
        PersistenceError,
        ProjectSliceError,
        RuntimeError,
        sqlite3.Error,
        ValueError,
    ) as error:
        print(f"B4 read-only inspection failed: {error}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
