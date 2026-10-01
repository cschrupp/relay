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

GITHUB_INTEGRATION_MIGRATION = Migration(
    version=2,
    name="github app integration state",
    statements=(
        """CREATE TABLE github_installations (
            project_id TEXT NOT NULL REFERENCES projects(id),
            installation_id INTEGER NOT NULL CHECK (installation_id > 0),
            state_revision INTEGER NOT NULL CHECK (state_revision >= 1),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (project_id, installation_id)
        )""",
        """CREATE TABLE github_installation_repositories (
            project_id TEXT NOT NULL,
            installation_id INTEGER NOT NULL,
            github_repository_id INTEGER NOT NULL CHECK (github_repository_id > 0),
            payload_json TEXT NOT NULL,
            PRIMARY KEY (project_id, installation_id, github_repository_id),
            FOREIGN KEY (project_id, installation_id)
                REFERENCES github_installations(project_id, installation_id)
                ON DELETE CASCADE
        )""",
        """CREATE TABLE github_installation_events (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL UNIQUE,
            project_id TEXT NOT NULL,
            installation_id INTEGER NOT NULL,
            prior_state_revision INTEGER NOT NULL CHECK (prior_state_revision >= 0),
            resulting_state_revision INTEGER NOT NULL CHECK (resulting_state_revision >= 1),
            event_type TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            delivery_id TEXT,
            delivery_digest TEXT,
            payload_json TEXT NOT NULL,
            FOREIGN KEY (project_id, installation_id)
                REFERENCES github_installations(project_id, installation_id),
            CHECK ((delivery_id IS NULL AND delivery_digest IS NULL)
                OR (delivery_id IS NOT NULL AND delivery_digest IS NOT NULL)),
            UNIQUE (project_id, delivery_id)
        )""",
        """CREATE INDEX github_installations_by_external_id
        ON github_installations(installation_id, project_id)""",
        """CREATE INDEX github_events_by_binding_revision
        ON github_installation_events(
            project_id, installation_id, resulting_state_revision, sequence
        )""",
    ),
)

REPOSITORY_MUTATION_AUTHORITY_MIGRATION = Migration(
    version=3,
    name="repository mutation authorization",
    statements=(
        """CREATE TABLE repository_mutation_authorizations (
            authorization_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id),
            subject_digest TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )""",
        """CREATE INDEX repository_mutation_authorizations_by_project_subject
        ON repository_mutation_authorizations(project_id, subject_digest)""",
    ),
)

PROJECT_SLICE_DEFINITION_HISTORY_MIGRATION = Migration(
    version=4,
    name="project and slice definition history",
    statements=(
        "ALTER TABLE projects ADD COLUMN definition_revision INTEGER NOT NULL DEFAULT 1 "
        "CHECK (definition_revision >= 1)",
        "ALTER TABLE slices ADD COLUMN definition_revision INTEGER NOT NULL DEFAULT 1 "
        "CHECK (definition_revision >= 1)",
        """CREATE TABLE project_definition_revisions (
            project_id TEXT NOT NULL,
            definition_revision INTEGER NOT NULL CHECK (definition_revision >= 1),
            operation TEXT NOT NULL CHECK (operation IN ('SEED', 'CREATE', 'UPDATE', 'DELETE')),
            payload_json TEXT,
            actor_json TEXT,
            occurred_at TEXT,
            reason TEXT,
            PRIMARY KEY (project_id, definition_revision),
            CHECK ((operation = 'DELETE' AND payload_json IS NULL)
                OR (operation <> 'DELETE' AND payload_json IS NOT NULL)),
            CHECK ((operation = 'SEED' AND actor_json IS NULL AND occurred_at IS NULL
                    AND reason IS NULL)
                OR (operation <> 'SEED' AND actor_json IS NOT NULL
                    AND occurred_at IS NOT NULL AND reason IS NOT NULL))
        )""",
        """CREATE TABLE slice_definition_revisions (
            slice_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            definition_revision INTEGER NOT NULL CHECK (definition_revision >= 1),
            operation TEXT NOT NULL CHECK (operation IN ('SEED', 'CREATE', 'UPDATE', 'DELETE')),
            payload_json TEXT,
            actor_json TEXT,
            occurred_at TEXT,
            reason TEXT,
            PRIMARY KEY (slice_id, definition_revision),
            CHECK ((operation = 'DELETE' AND payload_json IS NULL)
                OR (operation <> 'DELETE' AND payload_json IS NOT NULL)),
            CHECK ((operation = 'SEED' AND actor_json IS NULL AND occurred_at IS NULL
                    AND reason IS NULL)
                OR (operation <> 'SEED' AND actor_json IS NOT NULL
                    AND occurred_at IS NOT NULL AND reason IS NOT NULL))
        )""",
        """INSERT INTO project_definition_revisions(
            project_id, definition_revision, operation, payload_json
        ) SELECT id, 1, 'SEED', payload_json FROM projects ORDER BY id""",
        """INSERT INTO slice_definition_revisions(
            slice_id, project_id, definition_revision, operation, payload_json
        ) SELECT id, project_id, 1, 'SEED', payload_json FROM slices ORDER BY id""",
        "CREATE INDEX project_definition_revisions_by_revision "
        "ON project_definition_revisions(project_id, definition_revision)",
        "CREATE INDEX slice_definition_revisions_by_project_revision "
        "ON slice_definition_revisions(project_id, slice_id, definition_revision)",
        """CREATE TRIGGER project_definition_revisions_no_update
        BEFORE UPDATE ON project_definition_revisions BEGIN
            SELECT RAISE(ABORT, 'Project definition history is append-only');
        END""",
        """CREATE TRIGGER project_definition_revisions_no_delete
        BEFORE DELETE ON project_definition_revisions BEGIN
            SELECT RAISE(ABORT, 'Project definition history is append-only');
        END""",
        """CREATE TRIGGER slice_definition_revisions_no_update
        BEFORE UPDATE ON slice_definition_revisions BEGIN
            SELECT RAISE(ABORT, 'Slice definition history is append-only');
        END""",
        """CREATE TRIGGER slice_definition_revisions_no_delete
        BEFORE DELETE ON slice_definition_revisions BEGIN
            SELECT RAISE(ABORT, 'Slice definition history is append-only');
        END""",
    ),
)

DEFAULT_MIGRATIONS: tuple[Migration, ...] = (
    INITIAL_MIGRATION,
    GITHUB_INTEGRATION_MIGRATION,
    REPOSITORY_MUTATION_AUTHORITY_MIGRATION,
    PROJECT_SLICE_DEFINITION_HISTORY_MIGRATION,
)

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
        "github_installations",
        "github_installation_repositories",
        "github_installation_events",
        "repository_mutation_authorizations",
        "project_definition_revisions",
        "slice_definition_revisions",
    }
)
REQUIRED_INDEXES = frozenset(
    {
        "lifecycle_events_by_slice_revision",
        "gates_by_id_revision",
        "executions_by_slice_revision",
        "github_installations_by_external_id",
        "github_events_by_binding_revision",
        "repository_mutation_authorizations_by_project_subject",
        "project_definition_revisions_by_revision",
        "slice_definition_revisions_by_project_revision",
    }
)
REQUIRED_TRIGGERS = frozenset(
    {
        "project_definition_revisions_no_update",
        "project_definition_revisions_no_delete",
        "slice_definition_revisions_no_update",
        "slice_definition_revisions_no_delete",
    }
)


def validate_migration_definitions(migrations: tuple[Migration, ...]) -> None:
    versions = tuple(item.version for item in migrations)
    if versions != tuple(sorted(set(versions))) or versions != tuple(range(1, len(versions) + 1)):
        raise MigrationError("migration versions must be unique, increasing, and begin at 1")


def _validate_applied_prefix(applied_versions: set[int], supported_count: int) -> None:
    expected = set(range(1, len(applied_versions) + 1))
    if applied_versions != expected:
        raise MigrationError("applied migration history is not a contiguous version prefix")
    if len(applied_versions) > supported_count:
        raise MigrationError("database has an unsupported future schema version")


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
        _validate_applied_prefix(set(applied), len(migrations))

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
    _validate_applied_prefix(set(applied), len(migrations))
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
        triggers = {
            cast(str, row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'trigger'"
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
    missing_triggers = REQUIRED_TRIGGERS - triggers
    if missing_triggers:
        raise MigrationError(
            f"database is missing required triggers: {', '.join(sorted(missing_triggers))}"
        )


def _is_busy(error: sqlite3.OperationalError) -> bool:
    message = str(error).lower()
    return "locked" in message or "busy" in message
