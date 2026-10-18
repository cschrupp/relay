"""Narrow SQLite materialization and validation boundary for B2 adoption."""

from __future__ import annotations

import json
import os
import sqlite3
import stat
import tempfile
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, ValidationError

from relay_engine.adoption.models import (
    ProjectAdoptionRecordV1,
    adoption_record_digest,
)
from relay_engine.domain import Baseline, CommitRef, Project, Slice
from relay_engine.persistence import open_database
from relay_engine.persistence.database import RelayDatabase, write_transaction
from relay_engine.persistence.errors import PersistenceError, PersistenceIntegrityError
from relay_engine.project_slice.models import DefinitionOperation, MutationMetadata
from relay_engine.project_slice.origin import (
    AdoptionPreGenesisProjectProofV1,
    NativeRelayOriginProofV1,
    OperationalOrigin,
    OperationalOriginResolution,
    OriginDiagnosticCode,
    OriginRecordKind,
    OriginResolutionState,
    OriginSubjectType,
    ProjectOperationalEpochResolution,
    ProjectOperationalEpochV1,
    ProjectOperationalOriginRecordV1,
    definition_payload_digest,
    origin_resolution_not_established,
    project_operational_epoch_digest,
    project_operational_origin_record_digest,
)


class AdoptionPersistenceError(RuntimeError):
    """Typed failure from B2's narrow staging database boundary."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _json(value: object) -> str:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _time_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def load_project_adoption_from_connection(
    connection: sqlite3.Connection,
    project_id: str,
) -> ProjectAdoptionRecordV1 | None:
    """Load and cross-check the immutable adoption payload and indexed columns."""

    row = connection.execute(
        "SELECT * FROM project_adoptions WHERE project_id = ?", (project_id,)
    ).fetchone()
    if row is None:
        return None
    try:
        value = ProjectAdoptionRecordV1.model_validate_json(cast(str, row["payload_json"]))
    except (ValidationError, ValueError, TypeError) as error:
        raise PersistenceIntegrityError("stored Project adoption record is invalid") from error
    indexed = {
        "adoption_id": value.adoption_id,
        "project_id": value.project_id,
        "repository_id": value.repository_id,
        "t1": _time_text(value.t1),
        "manifest_sha256": value.manifest_sha256,
        "fresh_report_sha256": value.fresh_report_sha256,
        "fresh_report_state_sha256": value.fresh_report_state_sha256,
        "fresh_head_sha": value.fresh_repository_fingerprint.head_sha,
        "initial_slice_id": value.initial_slice_id,
        "baseline_id": value.baseline_id,
        "record_digest": value.record_digest,
    }
    if any(row[name] != expected for name, expected in indexed.items()):
        raise PersistenceIntegrityError(
            "Project adoption indexed columns disagree with its immutable payload"
        )
    if value.record_digest != adoption_record_digest(value):
        raise PersistenceIntegrityError("Project adoption record digest is invalid")
    return value


def load_project_adoption(
    database: RelayDatabase,
    project_id: str,
) -> ProjectAdoptionRecordV1 | None:
    """Load the one adoption record for a Project from a caller-owned database."""

    return load_project_adoption_from_connection(database.connection, project_id)


def load_project_operational_epoch_resolution_from_connection(
    connection: sqlite3.Connection,
    project_id: str,
) -> ProjectOperationalEpochResolution:
    """Resolve the optional project-scoped epoch without inferring a missing anchor."""

    rows = connection.execute(
        "SELECT * FROM project_operational_epochs WHERE project_id = ? ORDER BY epoch_id",
        (project_id,),
    ).fetchall()
    record_ids = tuple(str(row["epoch_id"]) for row in rows)
    if not rows:
        return ProjectOperationalEpochResolution(
            state=OriginResolutionState.NOT_ESTABLISHED,
            epoch=None,
            diagnostic=None,
            record_ids=(),
        )
    if len(rows) != 1:
        return ProjectOperationalEpochResolution(
            state=OriginResolutionState.NOT_ESTABLISHED,
            epoch=None,
            diagnostic=OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            record_ids=record_ids,
        )
    try:
        epoch = ProjectOperationalEpochV1.model_validate_json(cast(str, rows[0]["payload_json"]))
    except ValidationError, ValueError, TypeError:
        return ProjectOperationalEpochResolution(
            state=OriginResolutionState.NOT_ESTABLISHED,
            epoch=None,
            diagnostic=OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            record_ids=record_ids,
        )
    indexed = {
        "project_id": epoch.project_id,
        "epoch_id": epoch.epoch_id,
        "genesis_cut_at": _time_text(epoch.genesis_cut_at),
        "basis_kind": epoch.basis_kind,
        "adoption_id": epoch.adoption_id,
        "adoption_record_digest": epoch.adoption_record_digest,
        "recorded_at": _time_text(epoch.recorded_at),
        "epoch_digest": epoch.epoch_digest,
    }
    if any(rows[0][name] != expected for name, expected in indexed.items()) or (
        epoch.epoch_digest != project_operational_epoch_digest(epoch)
    ):
        return ProjectOperationalEpochResolution(
            state=OriginResolutionState.NOT_ESTABLISHED,
            epoch=None,
            diagnostic=OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            record_ids=record_ids,
        )
    adoption = load_project_adoption_from_connection(connection, project_id)
    if (
        adoption is None
        or epoch.adoption_id != adoption.adoption_id
        or epoch.adoption_record_digest != adoption.record_digest
        or epoch.genesis_cut_at != adoption.t1
    ):
        return ProjectOperationalEpochResolution(
            state=OriginResolutionState.NOT_ESTABLISHED,
            epoch=None,
            diagnostic=OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            record_ids=record_ids,
        )
    return ProjectOperationalEpochResolution(
        state=OriginResolutionState.ESTABLISHED,
        epoch=epoch,
        diagnostic=None,
        record_ids=record_ids,
    )


def project_adoption_mode_present_from_connection(
    connection: sqlite3.Connection,
    project_id: str,
) -> bool:
    """Detect any B2 provenance row so missing epochs cannot fall back to v7."""

    for table in (
        "project_adoptions",
        "project_operational_epochs",
        "project_operational_origin_records",
    ):
        row = connection.execute(
            f"SELECT 1 FROM {table} WHERE project_id = ? LIMIT 1", (project_id,)
        ).fetchone()
        if row is not None:
            return True
    return False


def load_project_operational_origin_records_from_connection(
    connection: sqlite3.Connection,
    *,
    subject_type: OriginSubjectType,
    subject_id: str,
) -> tuple[ProjectOperationalOriginRecordV1, ...]:
    """Load exact project-scoped origin records and check indexed payload agreement."""

    rows = connection.execute(
        "SELECT * FROM project_operational_origin_records "
        "WHERE subject_type = ? AND subject_id = ? ORDER BY record_id",
        (subject_type.value, subject_id),
    ).fetchall()
    values: list[ProjectOperationalOriginRecordV1] = []
    for row in rows:
        try:
            value = ProjectOperationalOriginRecordV1.model_validate_json(
                cast(str, row["payload_json"])
            )
        except (ValidationError, ValueError, TypeError) as error:
            raise PersistenceIntegrityError("stored project-scoped origin is invalid") from error
        indexed = {
            "record_id": value.record_id,
            "subject_type": value.subject_type.value,
            "subject_id": value.subject_id,
            "project_id": value.project_id,
            "record_kind": value.record_kind.value,
            "origin": value.origin.value,
            "epoch_id": value.epoch_id,
            "epoch_digest": value.epoch_digest,
            "supersedes_record_id": value.supersedes_record_id,
            "supersedes_record_digest": value.supersedes_record_digest,
            "recorded_at": _time_text(value.recorded_at),
            "recorded_by_json": _json(value.recorded_by),
            "establishing_authority_id": value.establishing_authority_id,
            "correction_authorization_id": value.correction_authorization_id,
            "correction_authorization_digest": value.correction_authorization_digest,
            "rationale": value.rationale,
            "record_digest": value.record_digest,
        }
        if any(row[name] != expected for name, expected in indexed.items()) or (
            value.record_digest != project_operational_origin_record_digest(value)
        ):
            raise PersistenceIntegrityError(
                "project-scoped origin columns disagree with immutable payload"
            )
        values.append(value)
    return tuple(values)


def resolve_project_adoption_origin_from_connection(
    connection: sqlite3.Connection,
    project_id: str,
) -> OperationalOriginResolution | None:
    """Resolve one B2 Project origin, or return None when the Project uses v7 mode."""

    epoch_result = load_project_operational_epoch_resolution_from_connection(connection, project_id)
    if not project_adoption_mode_present_from_connection(connection, project_id):
        return None
    epoch = epoch_result.epoch
    if epoch_result.state is not OriginResolutionState.ESTABLISHED or epoch is None:
        return origin_resolution_not_established(
            OriginSubjectType.PROJECT,
            project_id,
            None,
            OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            "The Project adoption epoch is invalid or ambiguous.",
            tuple(),
        )
    strict_rows = connection.execute(
        "SELECT record_id FROM operational_origin_records WHERE project_id = ? ORDER BY record_id",
        (project_id,),
    ).fetchall()
    if strict_rows:
        return origin_resolution_not_established(
            OriginSubjectType.PROJECT,
            project_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
            "Both strict-v7 and Project-adoption origin modes apply to this Project.",
        )
    try:
        records = load_project_operational_origin_records_from_connection(
            connection,
            subject_type=OriginSubjectType.PROJECT,
            subject_id=project_id,
        )
        adoption = load_project_adoption_from_connection(connection, project_id)
    except PersistenceIntegrityError as error:
        return origin_resolution_not_established(
            OriginSubjectType.PROJECT,
            project_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_RECORD,
            str(error),
        )
    if adoption is None or len(records) != 1:
        return origin_resolution_not_established(
            OriginSubjectType.PROJECT,
            project_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
            "Adoption mode requires one exact initial Project origin record.",
            tuple(record.record_id for record in records),
        )
    record = records[0]
    proof = record.proof
    expected_proof = AdoptionPreGenesisProjectProofV1(
        proof_type="ADOPTION_PRE_GENESIS_PROJECT",
        project_id=adoption.project_id,
        repository=adoption.repository,
        adoption_id=adoption.adoption_id,
        adoption_record_digest=adoption.record_digest,
        manifest_sha256=adoption.manifest_sha256,
        input_report_sha256=adoption.input_report_sha256,
        fresh_report_sha256=adoption.fresh_report_sha256,
        fresh_report_state_sha256=adoption.fresh_report_state_sha256,
        fresh_repository_fingerprint_sha256=adoption.fresh_repository_fingerprint_sha256,
        repository_root=adoption.fresh_repository_fingerprint.repository_root,
        relay_contract_status=cast(
            Literal["ABSENT", "VALID"],
            adoption.fresh_repository_fingerprint.relay_contract.status.value,
        ),
        fresh_head=CommitRef(
            repository=adoption.repository,
            sha=adoption.fresh_repository_fingerprint.head_sha,
        ),
        attestation_id=adoption.attestation_id,
        assertion="REPRESENTED_PROJECT_EXISTED_BEFORE_T1",
        actor=adoption.human_actor,
        decided_at=adoption.t1,
    )
    if (
        len(records) != 1
        or record.subject_type is not OriginSubjectType.PROJECT
        or record.subject_id != project_id
        or record.project_id != project_id
        or record.record_kind is not OriginRecordKind.INITIAL
        or record.origin is not OperationalOrigin.PRE_GENESIS
        or record.epoch_id != epoch.epoch_id
        or record.epoch_digest != epoch.epoch_digest
        or record.recorded_at != adoption.t1
        or record.recorded_by != adoption.human_actor
        or record.establishing_authority_id != adoption.adoption_id
        or proof != expected_proof
    ):
        return origin_resolution_not_established(
            OriginSubjectType.PROJECT,
            project_id,
            epoch,
            OriginDiagnosticCode.INVALID_PROOF,
            "Project PRE_GENESIS proof does not match the exact adoption record.",
            tuple(item.record_id for item in records),
        )
    return OperationalOriginResolution(
        subject_type=OriginSubjectType.PROJECT,
        subject_id=project_id,
        state=OriginResolutionState.ESTABLISHED,
        origin=OperationalOrigin.PRE_GENESIS,
        record=record,
        epoch=epoch,
        diagnostic=None,
    )


def resolve_slice_adoption_origin_from_connection(
    connection: sqlite3.Connection,
    slice_id: str,
    project_id: str,
    project_origin: OperationalOriginResolution,
) -> OperationalOriginResolution:
    """Resolve a new B2/future Slice CREATE against its adopted Project epoch."""

    epoch_result = load_project_operational_epoch_resolution_from_connection(connection, project_id)
    epoch = epoch_result.epoch
    if epoch_result.state is not OriginResolutionState.ESTABLISHED or epoch is None:
        return origin_resolution_not_established(
            OriginSubjectType.SLICE,
            slice_id,
            None,
            OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            "The Project adoption epoch is not established.",
        )
    if project_origin.state is not OriginResolutionState.ESTABLISHED:
        return origin_resolution_not_established(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.PROJECT_ORIGIN_NOT_ESTABLISHED,
            "Owning Project origin is not established.",
        )
    strict_rows = connection.execute(
        "SELECT record_id FROM operational_origin_records WHERE project_id = ? ORDER BY record_id",
        (project_id,),
    ).fetchall()
    if strict_rows:
        return origin_resolution_not_established(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
            "Both strict-v7 and Project-adoption origin modes apply to this Project.",
        )
    try:
        records = load_project_operational_origin_records_from_connection(
            connection,
            subject_type=OriginSubjectType.SLICE,
            subject_id=slice_id,
        )
    except PersistenceIntegrityError as error:
        return origin_resolution_not_established(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_RECORD,
            str(error),
        )
    if len(records) != 1 or records[0].record_kind is not OriginRecordKind.INITIAL:
        return origin_resolution_not_established(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
            "Project-adoption Slice origin requires one exact initial record.",
            tuple(record.record_id for record in records),
        )
    record = records[0]
    proof = record.proof
    row = connection.execute(
        "SELECT operation, payload_json, actor_json, occurred_at, reason "
        "FROM slice_definition_revisions WHERE slice_id = ? AND definition_revision = 1",
        (slice_id,),
    ).fetchone()
    if row is None or row["operation"] != "CREATE":
        return origin_resolution_not_established(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.INVALID_CREATION_REFERENCE,
            "NATIVE_RELAY Slice origin has no exact CREATE definition revision.",
            (record.record_id,),
        )
    try:
        created_slice = Slice.model_validate_json(cast(str, row["payload_json"]))
    except ValidationError, ValueError, TypeError:
        return origin_resolution_not_established(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.INVALID_CREATION_REFERENCE,
            "NATIVE_RELAY Slice CREATE payload is invalid.",
            (record.record_id,),
        )
    if (
        record.subject_type is not OriginSubjectType.SLICE
        or record.subject_id != slice_id
        or record.project_id != project_id
        or record.record_kind is not OriginRecordKind.INITIAL
        or record.origin is not OperationalOrigin.NATIVE_RELAY
        or record.epoch_id != epoch.epoch_id
        or record.epoch_digest != epoch.epoch_digest
        or not isinstance(proof, NativeRelayOriginProofV1)
        or proof.subject_type is not OriginSubjectType.SLICE
        or proof.subject_id != slice_id
        or proof.operation != "CREATE"
        or proof.creation_payload_digest != definition_payload_digest(created_slice)
        or row["actor_json"] != _json(proof.actor)
        or row["occurred_at"] != _time_text(proof.created_at)
        or row["reason"] != proof.reason
        or proof.created_at <= epoch.genesis_cut_at
        or record.recorded_at != proof.created_at
        or record.recorded_by != proof.actor
        or project_origin.origin is not OperationalOrigin.PRE_GENESIS
    ):
        return origin_resolution_not_established(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.INVALID_PROOF,
            "NATIVE_RELAY proof does not match the exact project-scoped epoch and CREATE.",
            (record.record_id,),
        )
    return OperationalOriginResolution(
        subject_type=OriginSubjectType.SLICE,
        subject_id=slice_id,
        state=OriginResolutionState.ESTABLISHED,
        origin=OperationalOrigin.NATIVE_RELAY,
        record=record,
        epoch=epoch,
        diagnostic=None,
    )


def append_project_native_origin_from_connection(
    connection: sqlite3.Connection,
    record: ProjectOperationalOriginRecordV1,
) -> None:
    """Append one NATIVE_RELAY Slice origin beside its exact CREATE revision."""

    if (
        record.record_kind is not OriginRecordKind.INITIAL
        or record.origin is not OperationalOrigin.NATIVE_RELAY
        or record.subject_type is not OriginSubjectType.SLICE
        or not isinstance(record.proof, NativeRelayOriginProofV1)
    ):
        raise PersistenceIntegrityError("adoption mode accepts initial NATIVE_RELAY Slice only")
    epoch_result = load_project_operational_epoch_resolution_from_connection(
        connection, record.project_id
    )
    epoch = epoch_result.epoch
    if (
        epoch_result.state is not OriginResolutionState.ESTABLISHED
        or epoch is None
        or record.epoch_id != epoch.epoch_id
        or record.epoch_digest != epoch.epoch_digest
    ):
        raise PersistenceIntegrityError("NATIVE_RELAY origin is not bound to its Project epoch")
    row = connection.execute(
        "SELECT operation, payload_json, actor_json, occurred_at, reason "
        "FROM slice_definition_revisions WHERE slice_id = ? AND definition_revision = 1",
        (record.subject_id,),
    ).fetchone()
    if row is None or row["operation"] != "CREATE":
        raise PersistenceIntegrityError("NATIVE_RELAY origin requires exact Slice CREATE")
    try:
        created_slice = Slice.model_validate_json(cast(str, row["payload_json"]))
    except (ValidationError, ValueError, TypeError) as error:
        raise PersistenceIntegrityError("Slice CREATE payload is invalid") from error
    proof = record.proof
    if (
        created_slice.id != record.subject_id
        or created_slice.project_id != record.project_id
        or proof.creation_payload_digest != definition_payload_digest(created_slice)
        or row["actor_json"] != _json(proof.actor)
        or row["occurred_at"] != _time_text(proof.created_at)
        or row["reason"] != proof.reason
        or proof.created_at <= epoch.genesis_cut_at
        or record.recorded_at != proof.created_at
        or record.recorded_by != proof.actor
        or record.establishing_authority_id != f"slice_definition_revisions/{record.subject_id}/1"
    ):
        raise PersistenceIntegrityError("NATIVE_RELAY proof disagrees with exact CREATE")
    _insert_project_origin_from_connection(connection, record)


def _insert_project_origin_from_connection(
    connection: sqlite3.Connection,
    value: ProjectOperationalOriginRecordV1,
) -> None:
    connection.execute(
        """INSERT INTO project_operational_origin_records(
            record_id, subject_type, subject_id, project_id, record_kind, origin,
            epoch_id, epoch_digest, supersedes_record_id, supersedes_record_digest,
            recorded_at, recorded_by_json, establishing_authority_id,
            correction_authorization_id, correction_authorization_digest, rationale,
            record_digest, payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            value.record_id,
            value.subject_type.value,
            value.subject_id,
            value.project_id,
            value.record_kind.value,
            value.origin.value,
            value.epoch_id,
            value.epoch_digest,
            value.supersedes_record_id,
            value.supersedes_record_digest,
            _time_text(value.recorded_at),
            _json(value.recorded_by),
            value.establishing_authority_id,
            value.correction_authorization_id,
            value.correction_authorization_digest,
            value.rationale,
            value.record_digest,
            _json(value),
        ),
    )


def _validate_database_target(database_path: Path, repository_root: Path) -> Path:
    try:
        requested = database_path.expanduser().absolute()
        parent = requested.parent.resolve(strict=True)
        target = parent / requested.name
        root = repository_root.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AdoptionPersistenceError(
            "ADOPTION_DATABASE_UNSAFE", "database path or parent cannot be resolved"
        ) from error
    try:
        target.relative_to(root)
    except ValueError:
        pass
    else:
        raise AdoptionPersistenceError(
            "ADOPTION_DATABASE_UNSAFE", "database must be outside the inspected repository"
        )
    if target.is_symlink():
        raise AdoptionPersistenceError("ADOPTION_DATABASE_UNSAFE", "database path is a symlink")
    if target.exists():
        raise AdoptionPersistenceError("ADOPTION_DATABASE_EXISTS", "database target already exists")
    for suffix in ("-wal", "-shm", "-journal"):
        if Path(str(target) + suffix).exists():
            raise AdoptionPersistenceError(
                "ADOPTION_DATABASE_UNSAFE", "database has a pre-existing SQLite sidecar"
            )
    return target


def publish_adoption_database(
    *,
    database_path: Path,
    repository_root: Path,
    project: Project,
    baseline: Baseline,
    initial_slice: Slice,
    adoption: ProjectAdoptionRecordV1,
    epoch: ProjectOperationalEpochV1,
    project_origin: ProjectOperationalOriginRecordV1,
    slice_origin: ProjectOperationalOriginRecordV1,
    project_mutation: MutationMetadata,
    slice_mutation: MutationMetadata,
    migration_applied_at: datetime,
    final_repository_check: Callable[[], bool],
) -> Path:
    """Materialize, verify, and atomically publish a fresh external database."""

    target = _validate_database_target(database_path, repository_root)
    stage_fd, stage_text = tempfile.mkstemp(
        prefix=f".{target.name}.adoption-", suffix=".sqlite", dir=target.parent
    )
    os.close(stage_fd)
    stage = Path(stage_text)
    database: RelayDatabase | None = None
    try:
        database = open_database(
            stage,
            apply_migrations=True,
            migration_applied_at=migration_applied_at,
        )
        with write_transaction(database) as connection:
            _insert_initial_project(connection, project, project_mutation)
            connection.execute(
                "INSERT INTO baselines(id, project_id, payload_json) VALUES (?, ?, ?)",
                (baseline.id, baseline.project_id, _json(baseline)),
            )
            _insert_initial_slice(connection, initial_slice, slice_mutation)
            _insert_adoption_from_connection(connection, adoption)
            _insert_project_epoch_from_connection(connection, epoch)
            _insert_project_origin_from_connection(connection, project_origin)
            append_project_native_origin_from_connection(connection, slice_origin)
        _verify_materialized_database(
            database,
            project,
            baseline,
            initial_slice,
            adoption,
            epoch,
            project_mutation,
            slice_mutation,
        )
        _consolidate_sqlite(database)
        database.close()
        database = None
        if _stage_has_sidecars(stage):
            raise AdoptionPersistenceError(
                "ADOPTION_VERIFICATION_FAILED", "SQLite staging sidecars remain before publish"
            )
        if not final_repository_check():
            raise AdoptionPersistenceError(
                "ADOPTION_STATE_CHANGED", "repository changed before database publication"
            )
        try:
            os.link(stage, target)
        except FileExistsError as error:
            raise AdoptionPersistenceError(
                "ADOPTION_DATABASE_EXISTS", "database target appeared before publication"
            ) from error
        except OSError as error:
            raise AdoptionPersistenceError(
                "ADOPTION_DATABASE_UNSAFE", "atomic no-replace database publication failed"
            ) from error
        with suppress(OSError):
            stage.unlink()
        return target
    except AdoptionPersistenceError:
        raise
    except (sqlite3.Error, OSError, PersistenceError, ValidationError) as error:
        raise AdoptionPersistenceError(
            "ADOPTION_MATERIALIZATION_FAILED", "staged adoption database failed validation"
        ) from error
    finally:
        if database is not None:
            with suppress(Exception):
                database.close()
        _remove_stage_files(stage)


def _insert_initial_project(
    connection: sqlite3.Connection,
    value: Project,
    mutation: MutationMetadata,
) -> None:
    connection.execute(
        "INSERT INTO projects(id, payload_json, definition_revision) VALUES (?, ?, 1)",
        (value.id, _json(value)),
    )
    connection.execute(
        """INSERT INTO project_definition_revisions(
            project_id, definition_revision, operation, payload_json,
            actor_json, occurred_at, reason
        ) VALUES (?, 1, 'CREATE', ?, ?, ?, ?)""",
        (
            value.id,
            _json(value),
            _json(mutation.actor),
            _time_text(mutation.occurred_at),
            mutation.reason,
        ),
    )


def _insert_initial_slice(
    connection: sqlite3.Connection,
    value: Slice,
    mutation: MutationMetadata,
) -> None:
    connection.execute(
        "INSERT INTO slices(id, project_id, payload_json, definition_revision) VALUES (?, ?, ?, 1)",
        (value.id, value.project_id, _json(value)),
    )
    connection.execute(
        """INSERT INTO slice_definition_revisions(
            slice_id, project_id, definition_revision, operation, payload_json,
            actor_json, occurred_at, reason
        ) VALUES (?, ?, 1, 'CREATE', ?, ?, ?, ?)""",
        (
            value.id,
            value.project_id,
            _json(value),
            _json(mutation.actor),
            _time_text(mutation.occurred_at),
            mutation.reason,
        ),
    )


def _insert_adoption_from_connection(
    connection: sqlite3.Connection,
    value: ProjectAdoptionRecordV1,
) -> None:
    connection.execute(
        """INSERT INTO project_adoptions(
            adoption_id, project_id, repository_id, t1, manifest_sha256,
            fresh_report_sha256, fresh_report_state_sha256, fresh_head_sha,
            initial_slice_id, baseline_id, record_digest, payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            value.adoption_id,
            value.project_id,
            value.repository_id,
            _time_text(value.t1),
            value.manifest_sha256,
            value.fresh_report_sha256,
            value.fresh_report_state_sha256,
            value.fresh_repository_fingerprint.head_sha,
            value.initial_slice_id,
            value.baseline_id,
            value.record_digest,
            _json(value),
        ),
    )


def _insert_project_epoch_from_connection(
    connection: sqlite3.Connection,
    value: ProjectOperationalEpochV1,
) -> None:
    connection.execute(
        """INSERT INTO project_operational_epochs(
            project_id, epoch_id, genesis_cut_at, basis_kind, adoption_id,
            adoption_record_digest, recorded_at, epoch_digest, payload_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            value.project_id,
            value.epoch_id,
            _time_text(value.genesis_cut_at),
            value.basis_kind,
            value.adoption_id,
            value.adoption_record_digest,
            _time_text(value.recorded_at),
            value.epoch_digest,
            _json(value),
        ),
    )


def _verify_materialized_database(
    database: RelayDatabase,
    project: Project,
    baseline: Baseline,
    initial_slice: Slice,
    adoption: ProjectAdoptionRecordV1,
    epoch: ProjectOperationalEpochV1,
    project_mutation: MutationMetadata,
    slice_mutation: MutationMetadata,
) -> None:
    connection = database.connection
    counts = {
        "projects": connection.execute("SELECT count(*) FROM projects").fetchone()[0],
        "baselines": connection.execute("SELECT count(*) FROM baselines").fetchone()[0],
        "slices": connection.execute("SELECT count(*) FROM slices").fetchone()[0],
        "project_definition_revisions": connection.execute(
            "SELECT count(*) FROM project_definition_revisions"
        ).fetchone()[0],
        "slice_definition_revisions": connection.execute(
            "SELECT count(*) FROM slice_definition_revisions"
        ).fetchone()[0],
        "project_adoptions": connection.execute(
            "SELECT count(*) FROM project_adoptions"
        ).fetchone()[0],
        "project_operational_epochs": connection.execute(
            "SELECT count(*) FROM project_operational_epochs"
        ).fetchone()[0],
        "project_operational_origin_records": connection.execute(
            "SELECT count(*) FROM project_operational_origin_records"
        ).fetchone()[0],
        "operational_history_epochs": connection.execute(
            "SELECT count(*) FROM operational_history_epochs"
        ).fetchone()[0],
        "operational_origin_records": connection.execute(
            "SELECT count(*) FROM operational_origin_records"
        ).fetchone()[0],
        "lifecycle_events": connection.execute("SELECT count(*) FROM lifecycle_events").fetchone()[
            0
        ],
        "lifecycle_current": connection.execute(
            "SELECT count(*) FROM lifecycle_current"
        ).fetchone()[0],
        "artifacts": connection.execute("SELECT count(*) FROM artifacts").fetchone()[0],
        "decisions": connection.execute("SELECT count(*) FROM decisions").fetchone()[0],
        "evidence": connection.execute("SELECT count(*) FROM evidence").fetchone()[0],
        "handover_gate_revisions": connection.execute(
            "SELECT count(*) FROM handover_gate_revisions"
        ).fetchone()[0],
        "authorization_grants": connection.execute(
            "SELECT count(*) FROM authorization_grants"
        ).fetchone()[0],
        "human_decisions": connection.execute("SELECT count(*) FROM human_decisions").fetchone()[0],
        "gate_evaluation_records": connection.execute(
            "SELECT count(*) FROM gate_evaluation_records"
        ).fetchone()[0],
        "executions": connection.execute("SELECT count(*) FROM executions").fetchone()[0],
        "repository_mutation_authorizations": connection.execute(
            "SELECT count(*) FROM repository_mutation_authorizations"
        ).fetchone()[0],
        "github_installations": connection.execute(
            "SELECT count(*) FROM github_installations"
        ).fetchone()[0],
        "github_installation_repositories": connection.execute(
            "SELECT count(*) FROM github_installation_repositories"
        ).fetchone()[0],
        "github_installation_events": connection.execute(
            "SELECT count(*) FROM github_installation_events"
        ).fetchone()[0],
        "slice_results": connection.execute("SELECT count(*) FROM slice_results").fetchone()[0],
        "manual_evaluations": connection.execute(
            "SELECT count(*) FROM manual_evaluations"
        ).fetchone()[0],
        "canonical_promotion_policy_bindings": connection.execute(
            "SELECT count(*) FROM canonical_promotion_policy_bindings"
        ).fetchone()[0],
        "repository_promotion_intents": connection.execute(
            "SELECT count(*) FROM repository_promotion_intents"
        ).fetchone()[0],
        "repository_promotion_results": connection.execute(
            "SELECT count(*) FROM repository_promotion_results"
        ).fetchone()[0],
        "repository_promotion_reconciliations": connection.execute(
            "SELECT count(*) FROM repository_promotion_reconciliations"
        ).fetchone()[0],
    }
    expected = {
        "projects": 1,
        "baselines": 1,
        "slices": 1,
        "project_definition_revisions": 1,
        "slice_definition_revisions": 1,
        "project_adoptions": 1,
        "project_operational_epochs": 1,
        "project_operational_origin_records": 2,
        "operational_history_epochs": 0,
        "operational_origin_records": 0,
        "lifecycle_events": 0,
        "lifecycle_current": 0,
        "artifacts": 0,
        "decisions": 0,
        "evidence": 0,
        "handover_gate_revisions": 0,
        "authorization_grants": 0,
        "human_decisions": 0,
        "gate_evaluation_records": 0,
        "executions": 0,
        "repository_mutation_authorizations": 0,
        "github_installations": 0,
        "github_installation_repositories": 0,
        "github_installation_events": 0,
        "slice_results": 0,
        "manual_evaluations": 0,
        "canonical_promotion_policy_bindings": 0,
        "repository_promotion_intents": 0,
        "repository_promotion_results": 0,
        "repository_promotion_reconciliations": 0,
    }
    if counts != expected:
        raise PersistenceIntegrityError("staged database contains an unexpected record count")
    if load_project_adoption_from_connection(connection, project.id) != adoption:
        raise PersistenceIntegrityError("staged adoption record failed exact reload")
    epoch_resolution = load_project_operational_epoch_resolution_from_connection(
        connection, project.id
    )
    if (
        epoch_resolution.state is not OriginResolutionState.ESTABLISHED
        or epoch_resolution.epoch != epoch
    ):
        raise PersistenceIntegrityError("staged project epoch failed exact reload")
    project_origin = resolve_project_adoption_origin_from_connection(connection, project.id)
    if (
        project_origin is None
        or project_origin.state is not OriginResolutionState.ESTABLISHED
        or project_origin.origin is not OperationalOrigin.PRE_GENESIS
    ):
        raise PersistenceIntegrityError("staged Project PRE_GENESIS proof failed resolution")
    slice_origin = resolve_slice_adoption_origin_from_connection(
        connection,
        initial_slice.id,
        project.id,
        project_origin,
    )
    if (
        slice_origin.state is not OriginResolutionState.ESTABLISHED
        or slice_origin.origin is not OperationalOrigin.NATIVE_RELAY
    ):
        raise PersistenceIntegrityError("staged Slice NATIVE_RELAY proof failed resolution")
    slice_records = load_project_operational_origin_records_from_connection(
        connection,
        subject_type=OriginSubjectType.SLICE,
        subject_id=initial_slice.id,
    )
    if len(slice_records) != 1 or slice_records[0].origin is not OperationalOrigin.NATIVE_RELAY:
        raise PersistenceIntegrityError("staged adoption Slice NATIVE_RELAY proof is missing")
    row = connection.execute(
        "SELECT id, project_id, payload_json FROM slices WHERE id = ?", (initial_slice.id,)
    ).fetchone()
    if row is None or row["project_id"] != project.id:
        raise PersistenceIntegrityError("staged adoption frontier Slice is missing")
    if Slice.model_validate_json(cast(str, row["payload_json"])) != initial_slice:
        raise PersistenceIntegrityError("staged adoption frontier Slice changed")
    base_row = connection.execute(
        "SELECT project_id, payload_json FROM baselines WHERE id = ?", (baseline.id,)
    ).fetchone()
    if (
        base_row is None
        or base_row["project_id"] != baseline.project_id
        or Baseline.model_validate_json(cast(str, base_row["payload_json"])) != baseline
    ):
        raise PersistenceIntegrityError("staged exact T1 Baseline changed")
    project_row = connection.execute(
        "SELECT payload_json, definition_revision FROM projects WHERE id = ?", (project.id,)
    ).fetchone()
    if (
        project_row is None
        or project_row["definition_revision"] != 1
        or Project.model_validate_json(cast(str, project_row["payload_json"])) != project
    ):
        raise PersistenceIntegrityError("staged adopted Project changed")
    project_revision_count = connection.execute(
        "SELECT count(*) FROM project_definition_revisions WHERE project_id = ?",
        (project.id,),
    ).fetchone()[0]
    if project_revision_count != 1:
        raise PersistenceIntegrityError("staged Project has unexpected definition history")
    project_revision = connection.execute(
        "SELECT operation, payload_json, actor_json, occurred_at, reason "
        "FROM project_definition_revisions WHERE project_id = ? AND definition_revision = 1",
        (project.id,),
    ).fetchone()
    if (
        project_revision is None
        or project_revision["operation"] != DefinitionOperation.CREATE.value
        or Project.model_validate_json(cast(str, project_revision["payload_json"])) != project
        or project_revision["actor_json"] != _json(project_mutation.actor)
        or project_revision["occurred_at"] != _time_text(project_mutation.occurred_at)
        or project_revision["reason"] != project_mutation.reason
    ):
        raise PersistenceIntegrityError("staged Project CREATE revision is not exact")
    slice_row = connection.execute(
        "SELECT definition_revision FROM slices WHERE id = ?", (initial_slice.id,)
    ).fetchone()
    slice_revision = connection.execute(
        "SELECT operation, payload_json, actor_json, occurred_at, reason "
        "FROM slice_definition_revisions WHERE slice_id = ? AND definition_revision = 1",
        (initial_slice.id,),
    ).fetchone()
    if (
        slice_row is None
        or slice_row["definition_revision"] != 1
        or slice_revision is None
        or slice_revision["operation"] != DefinitionOperation.CREATE.value
        or Slice.model_validate_json(cast(str, slice_revision["payload_json"])) != initial_slice
        or slice_revision["actor_json"] != _json(slice_mutation.actor)
        or slice_revision["occurred_at"] != _time_text(slice_mutation.occurred_at)
        or slice_revision["reason"] != slice_mutation.reason
    ):
        raise PersistenceIntegrityError("staged Slice CREATE revision is not exact")
    slice_revision_count = connection.execute(
        "SELECT count(*) FROM slice_definition_revisions WHERE slice_id = ?",
        (initial_slice.id,),
    ).fetchone()[0]
    if slice_revision_count != 1:
        raise PersistenceIntegrityError("staged Slice has unexpected definition history")
    from relay_engine.board.render import render_project_board
    from relay_engine.board.service import project_board

    board = project_board(database, project.id)
    if (
        board.project != project
        or board.adoption_record != adoption
        or len(board.cards) != 1
        or board.cards[0].slice_id != initial_slice.id
        or board.cards[0].lifecycle is not None
        or board.cards[0].origin_resolution.state is not OriginResolutionState.ESTABLISHED
        or board.cards[0].origin_resolution.origin is not OperationalOrigin.NATIVE_RELAY
    ):
        raise PersistenceIntegrityError("staged adoption board projection is inconsistent")
    rendered_board = render_project_board(board)
    for expected_text in ("CURRENT", "NEXT", "LATER", "BLOCKED", "none established at T1"):
        if expected_text not in rendered_board:
            raise PersistenceIntegrityError("staged adoption board is missing its T1 orientation")
    foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_errors:
        raise PersistenceIntegrityError("staged database has a foreign-key integrity error")
    if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise PersistenceIntegrityError("staged SQLite integrity check failed")


def _consolidate_sqlite(database: RelayDatabase) -> None:
    connection = database.connection
    checkpoint = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    if checkpoint is None or int(checkpoint[0]) != 0:
        raise PersistenceIntegrityError("staging SQLite WAL could not be consolidated")
    journal_mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()
    if journal_mode is None or str(journal_mode[0]).lower() != "delete":
        raise PersistenceIntegrityError("staging SQLite journal mode could not be consolidated")


def _stage_has_sidecars(stage: Path) -> bool:
    return any(Path(str(stage) + suffix).exists() for suffix in ("-wal", "-shm", "-journal"))


def _remove_stage_files(stage: Path) -> None:
    for candidate in (
        stage,
        Path(str(stage) + "-wal"),
        Path(str(stage) + "-shm"),
        Path(str(stage) + "-journal"),
    ):
        with suppress(FileNotFoundError, OSError):
            mode = candidate.lstat().st_mode
            if stat.S_ISREG(mode):
                candidate.unlink()


__all__ = [
    "AdoptionPersistenceError",
    "append_project_native_origin_from_connection",
    "load_project_adoption",
    "load_project_adoption_from_connection",
    "load_project_operational_epoch_resolution_from_connection",
    "load_project_operational_origin_records_from_connection",
    "project_adoption_mode_present_from_connection",
    "publish_adoption_database",
    "resolve_project_adoption_origin_from_connection",
    "resolve_slice_adoption_origin_from_connection",
]
