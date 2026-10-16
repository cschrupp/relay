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

MANUAL_EVALUATION_MIGRATION = Migration(
    version=5,
    name="slice result and manual evaluation history",
    statements=(
        """CREATE TABLE slice_results (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id TEXT NOT NULL UNIQUE,
            slice_id TEXT NOT NULL REFERENCES slices(id),
            source_baseline_id TEXT NOT NULL REFERENCES baselines(id),
            result_baseline_id TEXT NOT NULL REFERENCES baselines(id),
            lifecycle_revision INTEGER NOT NULL CHECK (lifecycle_revision >= 0),
            supersedes_result_id TEXT UNIQUE REFERENCES slice_results(result_id),
            payload_json TEXT NOT NULL
        )""",
        """CREATE TABLE manual_evaluations (
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT NOT NULL UNIQUE,
            slice_id TEXT NOT NULL REFERENCES slices(id),
            result_id TEXT NOT NULL REFERENCES slice_results(result_id),
            result_baseline_id TEXT NOT NULL REFERENCES baselines(id),
            lifecycle_revision INTEGER NOT NULL CHECK (lifecycle_revision >= 0),
            supersedes_evaluation_id TEXT UNIQUE REFERENCES manual_evaluations(evaluation_id),
            payload_json TEXT NOT NULL
        )""",
        "CREATE INDEX slice_results_by_slice_sequence "
        "ON slice_results(slice_id, sequence, result_id)",
        "CREATE INDEX manual_evaluations_by_slice_result_sequence "
        "ON manual_evaluations(slice_id, result_id, sequence, evaluation_id)",
        """CREATE TRIGGER slice_results_no_update
        BEFORE UPDATE ON slice_results BEGIN
            SELECT RAISE(ABORT, 'Slice result history is append-only');
        END""",
        """CREATE TRIGGER slice_results_no_delete
        BEFORE DELETE ON slice_results BEGIN
            SELECT RAISE(ABORT, 'Slice result history is append-only');
        END""",
        """CREATE TRIGGER manual_evaluations_no_update
        BEFORE UPDATE ON manual_evaluations BEGIN
            SELECT RAISE(ABORT, 'Manual evaluation history is append-only');
        END""",
        """CREATE TRIGGER manual_evaluations_no_delete
        BEFORE DELETE ON manual_evaluations BEGIN
            SELECT RAISE(ABORT, 'Manual evaluation history is append-only');
        END""",
    ),
)

CANONICAL_PROMOTION_MIGRATION = Migration(
    version=6,
    name="repository canonical promotion evidence",
    statements=(
        """CREATE TABLE canonical_promotion_policy_bindings (
            binding_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id),
            repository_id TEXT NOT NULL,
            canonical_ref TEXT NOT NULL,
            revision INTEGER NOT NULL CHECK (revision >= 1),
            state TEXT NOT NULL CHECK (state IN ('UNMANAGED', 'MANAGED')),
            policy_digest TEXT,
            authorization_id TEXT NOT NULL,
            supersedes_binding_id TEXT,
            bound_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            UNIQUE(project_id, repository_id, canonical_ref, revision),
            UNIQUE(supersedes_binding_id),
            CHECK ((state = 'UNMANAGED' AND policy_digest IS NULL)
                OR (state = 'MANAGED' AND policy_digest IS NOT NULL))
        )""",
        """CREATE INDEX canonical_promotion_bindings_by_ref_revision
        ON canonical_promotion_policy_bindings(
            project_id, repository_id, canonical_ref, revision, binding_id
        )""",
        """CREATE TABLE repository_promotion_intents (
            promotion_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL REFERENCES projects(id),
            repository_id TEXT NOT NULL,
            canonical_ref TEXT NOT NULL,
            subject_digest TEXT NOT NULL,
            expected_parent_sha TEXT NOT NULL,
            target_sha TEXT NOT NULL,
            created_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )""",
        """CREATE INDEX repository_promotion_intents_by_project_ref_subject
        ON repository_promotion_intents(project_id, canonical_ref, subject_digest)""",
        """CREATE INDEX repository_promotion_intents_by_parent_target
        ON repository_promotion_intents(project_id, canonical_ref,
            expected_parent_sha, target_sha)""",
        """CREATE TABLE repository_promotion_results (
            promotion_id TEXT PRIMARY KEY REFERENCES repository_promotion_intents(promotion_id),
            project_id TEXT NOT NULL REFERENCES projects(id),
            repository_id TEXT NOT NULL,
            canonical_ref TEXT NOT NULL,
            target_sha TEXT NOT NULL,
            outcome TEXT NOT NULL CHECK (outcome IN
                ('SUCCEEDED', 'NOT_APPLIED', 'CONFLICT', 'VISIBLE_UNVERIFIED')),
            observed_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )""",
        """CREATE INDEX repository_promotion_results_by_project_ref_outcome
        ON repository_promotion_results(project_id, repository_id, canonical_ref,
            outcome, promotion_id)""",
        """CREATE UNIQUE INDEX repository_promotion_results_unique_successful_target
        ON repository_promotion_results(project_id, canonical_ref, target_sha)
        WHERE outcome = 'SUCCEEDED'""",
        """CREATE TABLE repository_promotion_reconciliations (
            reconciliation_id TEXT PRIMARY KEY,
            promotion_id TEXT NOT NULL UNIQUE
                REFERENCES repository_promotion_intents(promotion_id),
            project_id TEXT NOT NULL REFERENCES projects(id),
            repository_id TEXT NOT NULL,
            canonical_ref TEXT NOT NULL,
            target_sha TEXT NOT NULL,
            authorization_id TEXT NOT NULL,
            reconciled_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )""",
        """CREATE INDEX repository_promotion_reconciliations_by_project_ref
        ON repository_promotion_reconciliations(project_id, repository_id, canonical_ref,
            promotion_id)""",
        """CREATE TRIGGER canonical_promotion_policy_bindings_no_update
        BEFORE UPDATE ON canonical_promotion_policy_bindings BEGIN
            SELECT RAISE(ABORT, 'Canonical promotion policy bindings are append-only');
        END""",
        """CREATE TRIGGER canonical_promotion_policy_bindings_no_delete
        BEFORE DELETE ON canonical_promotion_policy_bindings BEGIN
            SELECT RAISE(ABORT, 'Canonical promotion policy bindings are append-only');
        END""",
        """CREATE TRIGGER repository_promotion_intents_no_update
        BEFORE UPDATE ON repository_promotion_intents BEGIN
            SELECT RAISE(ABORT, 'Repository promotion intents are append-only');
        END""",
        """CREATE TRIGGER repository_promotion_intents_no_delete
        BEFORE DELETE ON repository_promotion_intents BEGIN
            SELECT RAISE(ABORT, 'Repository promotion intents are append-only');
        END""",
        """CREATE TRIGGER repository_promotion_results_no_update
        BEFORE UPDATE ON repository_promotion_results BEGIN
            SELECT RAISE(ABORT, 'Repository promotion results are append-only');
        END""",
        """CREATE TRIGGER repository_promotion_results_no_delete
        BEFORE DELETE ON repository_promotion_results BEGIN
            SELECT RAISE(ABORT, 'Repository promotion results are append-only');
        END""",
        """CREATE TRIGGER repository_promotion_reconciliations_no_update
        BEFORE UPDATE ON repository_promotion_reconciliations BEGIN
            SELECT RAISE(ABORT, 'Repository promotion reconciliations are append-only');
        END""",
        """CREATE TRIGGER repository_promotion_reconciliations_no_delete
        BEFORE DELETE ON repository_promotion_reconciliations BEGIN
            SELECT RAISE(ABORT, 'Repository promotion reconciliations are append-only');
        END""",
    ),
)

OPERATIONAL_ORIGIN_MIGRATION = Migration(
    version=7,
    name="operational history epoch and origin provenance",
    statements=(
        """CREATE TABLE operational_history_epochs (
            epoch_slot INTEGER PRIMARY KEY CHECK (epoch_slot = 1),
            epoch_id TEXT NOT NULL UNIQUE,
            genesis_cut_at TEXT NOT NULL,
            source_commit_sha TEXT NOT NULL,
            genesis_package_artifact_id TEXT NOT NULL,
            genesis_package_path TEXT NOT NULL,
            genesis_package_digest TEXT NOT NULL,
            package_acceptance_artifact_id TEXT NOT NULL,
            package_acceptance_digest TEXT NOT NULL,
            epoch_digest TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )""",
        """CREATE INDEX operational_history_epochs_by_digest
        ON operational_history_epochs(epoch_id, epoch_digest)""",
        """CREATE TABLE operational_origin_records (
            record_id TEXT PRIMARY KEY,
            subject_type TEXT NOT NULL CHECK (subject_type IN ('PROJECT', 'SLICE')),
            subject_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            record_kind TEXT NOT NULL CHECK (record_kind IN ('INITIAL', 'CORRECTION')),
            origin TEXT NOT NULL CHECK (origin IN ('PRE_GENESIS', 'NATIVE_RELAY')),
            epoch_id TEXT NOT NULL REFERENCES operational_history_epochs(epoch_id),
            epoch_digest TEXT NOT NULL,
            supersedes_record_id TEXT,
            supersedes_record_digest TEXT,
            recorded_at TEXT NOT NULL,
            recorded_by_json TEXT NOT NULL,
            establishing_authority_id TEXT NOT NULL,
            correction_authorization_id TEXT,
            correction_authorization_digest TEXT,
            rationale TEXT,
            record_digest TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            UNIQUE(subject_type, subject_id, record_id),
            FOREIGN KEY(subject_type, subject_id, supersedes_record_id)
                REFERENCES operational_origin_records(subject_type, subject_id, record_id),
            CHECK ((record_kind = 'INITIAL' AND supersedes_record_id IS NULL
                    AND supersedes_record_digest IS NULL
                    AND correction_authorization_id IS NULL
                    AND correction_authorization_digest IS NULL
                    AND rationale IS NULL)
                OR (record_kind = 'CORRECTION' AND supersedes_record_id IS NOT NULL
                    AND supersedes_record_digest IS NOT NULL
                    AND correction_authorization_id IS NOT NULL
                    AND correction_authorization_digest IS NOT NULL
                    AND rationale IS NOT NULL))
        )""",
        """CREATE INDEX operational_origin_records_by_subject
        ON operational_origin_records(subject_type, subject_id, project_id)""",
        """CREATE INDEX operational_origin_records_by_epoch
        ON operational_origin_records(epoch_id, epoch_digest)""",
        """CREATE UNIQUE INDEX operational_origin_records_unique_initial
        ON operational_origin_records(subject_type, subject_id)
        WHERE record_kind = 'INITIAL'""",
        """CREATE UNIQUE INDEX operational_origin_records_unique_successor
        ON operational_origin_records(supersedes_record_id)
        WHERE supersedes_record_id IS NOT NULL""",
        """CREATE TRIGGER operational_origin_records_subject_matches_insert
        BEFORE INSERT ON operational_origin_records
        WHEN (NEW.subject_type = 'PROJECT' AND (
              NEW.subject_id != NEW.project_id
              OR NOT EXISTS (SELECT 1 FROM projects WHERE id = NEW.project_id)
          ))
          OR (NEW.subject_type = 'SLICE' AND NOT EXISTS (
              SELECT 1 FROM slices
              WHERE slices.id = NEW.subject_id AND slices.project_id = NEW.project_id
          ))
        BEGIN
            SELECT RAISE(ABORT, 'Operational origin subject/project mismatch');
        END""",
        """CREATE TRIGGER operational_history_epochs_no_update
        BEFORE UPDATE ON operational_history_epochs BEGIN
            SELECT RAISE(ABORT, 'Operational history epochs are append-only');
        END""",
        """CREATE TRIGGER operational_history_epochs_no_delete
        BEFORE DELETE ON operational_history_epochs BEGIN
            SELECT RAISE(ABORT, 'Operational history epochs are append-only');
        END""",
        """CREATE TRIGGER operational_origin_records_no_update
        BEFORE UPDATE ON operational_origin_records BEGIN
            SELECT RAISE(ABORT, 'Operational origin records are append-only');
        END""",
        """CREATE TRIGGER operational_origin_records_no_delete
        BEFORE DELETE ON operational_origin_records BEGIN
            SELECT RAISE(ABORT, 'Operational origin records are append-only');
        END""",
    ),
)

DEFAULT_MIGRATIONS: tuple[Migration, ...] = (
    INITIAL_MIGRATION,
    GITHUB_INTEGRATION_MIGRATION,
    REPOSITORY_MUTATION_AUTHORITY_MIGRATION,
    PROJECT_SLICE_DEFINITION_HISTORY_MIGRATION,
    MANUAL_EVALUATION_MIGRATION,
    CANONICAL_PROMOTION_MIGRATION,
    OPERATIONAL_ORIGIN_MIGRATION,
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
        "slice_results",
        "manual_evaluations",
        "canonical_promotion_policy_bindings",
        "repository_promotion_intents",
        "repository_promotion_results",
        "repository_promotion_reconciliations",
        "operational_history_epochs",
        "operational_origin_records",
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
        "slice_results_by_slice_sequence",
        "manual_evaluations_by_slice_result_sequence",
        "canonical_promotion_bindings_by_ref_revision",
        "repository_promotion_intents_by_project_ref_subject",
        "repository_promotion_intents_by_parent_target",
        "repository_promotion_results_by_project_ref_outcome",
        "repository_promotion_results_unique_successful_target",
        "repository_promotion_reconciliations_by_project_ref",
        "operational_history_epochs_by_digest",
        "operational_origin_records_by_subject",
        "operational_origin_records_by_epoch",
        "operational_origin_records_unique_initial",
        "operational_origin_records_unique_successor",
    }
)
REQUIRED_TRIGGERS = frozenset(
    {
        "project_definition_revisions_no_update",
        "project_definition_revisions_no_delete",
        "slice_definition_revisions_no_update",
        "slice_definition_revisions_no_delete",
        "slice_results_no_update",
        "slice_results_no_delete",
        "manual_evaluations_no_update",
        "manual_evaluations_no_delete",
        "canonical_promotion_policy_bindings_no_update",
        "canonical_promotion_policy_bindings_no_delete",
        "repository_promotion_intents_no_update",
        "repository_promotion_intents_no_delete",
        "repository_promotion_results_no_update",
        "repository_promotion_results_no_delete",
        "repository_promotion_reconciliations_no_update",
        "repository_promotion_reconciliations_no_delete",
        "operational_history_epochs_no_update",
        "operational_history_epochs_no_delete",
        "operational_origin_records_no_update",
        "operational_origin_records_no_delete",
        "operational_origin_records_subject_matches_insert",
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
