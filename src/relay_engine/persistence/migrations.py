"""Deterministic, checksummed SQLite schema migrations."""

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast

from relay_engine.persistence.errors import DatabaseUnavailable, MigrationError


@dataclass(frozen=True, slots=True)
class Migration:
    """One ordered SQLite schema change with a deterministic checksum."""

    version: int
    name: str
    statements: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("migration versions must begin at 1")
        if not self.name.strip():
            raise ValueError("migration name must not be blank")
        if not self.statements or any(not statement.strip() for statement in self.statements):
            raise ValueError("migration statements must be non-empty")

    @property
    def checksum(self) -> str:
        value = {
            "name": self.name,
            "statements": list(self.statements),
            "version": self.version,
        }
        content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return f"sha256:{digest}"


INITIAL_MIGRATION = Migration(
    version=1,
    name="initial engineering state",
    statements=(
        """CREATE TABLE projects (
            id TEXT PRIMARY KEY,
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE baselines (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id),
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE slices (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id),
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE artifacts (
            id TEXT PRIMARY KEY,
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE decisions (
            id TEXT PRIMARY KEY,
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE evidence (
            id TEXT PRIMARY KEY,
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE lifecycle_current (
            slice_id TEXT PRIMARY KEY REFERENCES slices(id),
            revision INTEGER NOT NULL CHECK (revision >= 0),
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE lifecycle_events (
            event_id TEXT PRIMARY KEY,
            slice_id TEXT NOT NULL REFERENCES slices(id),
            event_type TEXT NOT NULL,
            resulting_revision INTEGER NOT NULL CHECK (resulting_revision >= 0),
            occurred_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            UNIQUE (slice_id, resulting_revision)
        )""",
        """CREATE TABLE handover_gate_revisions (
            gate_id TEXT NOT NULL,
            gate_revision INTEGER NOT NULL CHECK (gate_revision >= 1),
            baseline_id TEXT NOT NULL REFERENCES baselines(id),
            slice_id TEXT NOT NULL REFERENCES slices(id),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (gate_id, gate_revision)
        )""",
        """CREATE TABLE authorization_grants (
            authorization_id TEXT PRIMARY KEY,
            baseline_id TEXT NOT NULL REFERENCES baselines(id),
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE human_decisions (
            decision_id TEXT PRIMARY KEY,
            decision_type TEXT NOT NULL,
            baseline_id TEXT NOT NULL REFERENCES baselines(id),
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE gate_evaluation_records (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id TEXT NOT NULL UNIQUE,
            baseline_id TEXT NOT NULL REFERENCES baselines(id),
            slice_id TEXT NOT NULL REFERENCES slices(id),
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE executions (
            execution_id TEXT PRIMARY KEY,
            evaluation_record_id TEXT NOT NULL REFERENCES gate_evaluation_records(record_id),
            event_id TEXT NOT NULL UNIQUE REFERENCES lifecycle_events(event_id),
            slice_id TEXT NOT NULL REFERENCES slices(id),
            resulting_lifecycle_revision INTEGER NOT NULL CHECK (resulting_lifecycle_revision >= 1),
            payload_json TEXT NOT NULL
        )""",
        """CREATE INDEX lifecycle_events_by_slice_revision
        ON lifecycle_events(slice_id, resulting_revision)""",
        "CREATE INDEX gates_by_id_revision ON handover_gate_revisions(gate_id, gate_revision)",
        """CREATE INDEX executions_by_slice_revision
        ON executions(slice_id, resulting_lifecycle_revision, execution_id)""",
    ),
)

DEFAULT_MIGRATIONS: tuple[Migration, ...] = (INITIAL_MIGRATION,)

_MIGRATION_TABLE = """CREATE TABLE IF NOT EXISTS relay_schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    checksum TEXT NOT NULL
)"""

REQUIRED_TABLES = frozenset(
    {
        "relay_schema_migrations",
        "projects",
        "baselines",
        "slices",
        "artifacts",
        "decisions",
        "evidence",
        "lifecycle_current",
        "lifecycle_events",
        "handover_gate_revisions",
        "authorization_grants",
        "human_decisions",
        "gate_evaluation_records",
        "executions",
    }
)
REQUIRED_INDEXES = frozenset(
    {
        "lifecycle_events_by_slice_revision",
        "gates_by_id_revision",
        "executions_by_slice_revision",
    }
)


def validate_migration_definitions(migrations: tuple[Migration, ...]) -> None:
    versions = tuple(item.version for item in migrations)
    if versions != tuple(sorted(set(versions))) or versions != tuple(range(1, len(versions) + 1)):
        raise MigrationError("migration versions must be unique, increasing, and begin at 1")


def apply_migrations(
    connection: sqlite3.Connection,
    migrations: tuple[Migration, ...] = DEFAULT_MIGRATIONS,
    *,
    applied_at: datetime,
) -> None:
    """Verify prior checksums and apply one complete pending batch atomically."""

    validate_migration_definitions(migrations)
    if applied_at.tzinfo is None or applied_at.utcoffset() is None:
        raise MigrationError("migration applied_at must be timezone-aware")
    timestamp = applied_at.astimezone(UTC).isoformat().replace("+00:00", "Z")

    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(_MIGRATION_TABLE)
        rows = connection.execute(
            "SELECT version, name, checksum FROM relay_schema_migrations ORDER BY version"
        ).fetchall()
        applied = {int(row["version"]): (str(row["name"]), str(row["checksum"])) for row in rows}
        migration_by_version = {item.version: item for item in migrations}

        if applied and max(applied) > len(migrations):
            raise MigrationError("database has an unsupported future schema version")

        for version, (name, checksum) in applied.items():
            migration = migration_by_version.get(version)
            if migration is None or name != migration.name or checksum != migration.checksum:
                raise MigrationError(f"applied migration {version} does not match its definition")

        for migration in migrations:
            if migration.version in applied:
                continue
            for statement in migration.statements:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO relay_schema_migrations(version, name, applied_at, checksum) "
                "VALUES (?, ?, ?, ?)",
                (migration.version, migration.name, timestamp, migration.checksum),
            )
        connection.commit()
    except MigrationError:
        if connection.in_transaction:
            connection.rollback()
        raise
    except sqlite3.OperationalError as error:
        if connection.in_transaction:
            connection.rollback()
        if _is_busy(error):
            raise DatabaseUnavailable("SQLite migration database is busy") from error
        raise MigrationError("could not apply SQLite schema migrations") from error
    except sqlite3.Error as error:
        if connection.in_transaction:
            connection.rollback()
        raise MigrationError("could not apply SQLite schema migrations") from error


def verify_schema(
    connection: sqlite3.Connection,
    migrations: tuple[Migration, ...] = DEFAULT_MIGRATIONS,
) -> None:
    """Verify known migration checksums and required tables without writing."""

    validate_migration_definitions(migrations)
    try:
        rows = connection.execute(
            "SELECT version, name, checksum FROM relay_schema_migrations ORDER BY version"
        ).fetchall()
    except sqlite3.OperationalError as error:
        raise MigrationError("database schema metadata is missing") from error

    applied = {int(row["version"]): (str(row["name"]), str(row["checksum"])) for row in rows}
    if applied and max(applied) > len(migrations):
        raise MigrationError("database has an unsupported future schema version")
    for version, (name, checksum) in applied.items():
        migration = migrations[version - 1] if 0 < version <= len(migrations) else None
        if migration is None or name != migration.name or checksum != migration.checksum:
            raise MigrationError(f"applied migration {version} does not match its definition")
    if len(applied) != len(migrations):
        raise MigrationError("database schema is missing known migrations")

    try:
        names = {
            cast(str, row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        indexes = {
            cast(str, row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            ).fetchall()
        }
    except sqlite3.Error as error:
        raise MigrationError("could not verify SQLite schema") from error
    missing = REQUIRED_TABLES - names
    if missing:
        raise MigrationError(f"database is missing required tables: {', '.join(sorted(missing))}")
    missing_indexes = REQUIRED_INDEXES - indexes
    if missing_indexes:
        raise MigrationError(
            f"database is missing required indexes: {', '.join(sorted(missing_indexes))}"
        )


def _is_busy(error: sqlite3.OperationalError) -> bool:
    message = str(error).lower()
    return "locked" in message or "busy" in message
