"""Transactional, audited Project and Slice definition CRUD."""

import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC
from typing import cast

from pydantic import BaseModel, ValidationError

from relay_engine.domain.ids import ProjectId, SliceId, new_id
from relay_engine.domain.models import Project, Slice
from relay_engine.persistence.database import RelayDatabase, read_transaction, write_transaction
from relay_engine.persistence.errors import PersistenceError, PersistenceIntegrityError
from relay_engine.project_slice.errors import (
    CrossProjectSliceReference,
    DefinitionRevisionConflict,
    OperationalOriginNotEstablished,
    ProjectAlreadyExists,
    ProjectDeleteForbidden,
    ProjectIdentifierRetired,
    ProjectNotFound,
    ProjectRepositoryImmutable,
    SliceAlreadyExists,
    SliceDefinitionFrozen,
    SliceDeleteForbidden,
    SliceDependencyCycle,
    SliceHasDownstreamDependents,
    SliceIdentifierRetired,
    SliceNotFound,
    SliceParentCycle,
)
from relay_engine.project_slice.models import (
    DefinitionOperation,
    MutationMetadata,
    ProjectDefinitionRevision,
    ProjectDefinitionSnapshot,
    ProjectDeleteResult,
    ProjectMutationResult,
    SliceDefinitionRevision,
    SliceDefinitionSnapshot,
    SliceDeleteResult,
    SliceMutationResult,
)
from relay_engine.project_slice.origin import (
    NativeRelayOriginProofV1,
    OperationalHistoryEpochResolution,
    OperationalOrigin,
    OperationalOriginRecordV1,
    OperationalOriginResolution,
    OriginDiagnosticCode,
    OriginRecordKind,
    OriginResolutionState,
    OriginSubjectType,
    build_operational_origin_record,
    definition_payload_digest,
    origin_resolution_not_established,
    resolve_origin_chain,
    unresolved_origin_dependency_scope,
)


def _json(value: BaseModel) -> str:
    return json.dumps(
        value.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def _mutation(value: MutationMetadata) -> MutationMetadata:
    try:
        return MutationMetadata.model_validate(value)
    except (ValidationError, TypeError) as error:
        raise ValueError(
            "mutation metadata must identify a human, aware time, and reason"
        ) from error


def _time_text(value: MutationMetadata) -> str:
    return value.occurred_at.astimezone(UTC).isoformat().replace("+00:00", "Z")


@contextmanager
def _transaction(database: RelayDatabase) -> Generator[sqlite3.Connection]:
    try:
        with write_transaction(database) as connection:
            yield connection
    except sqlite3.IntegrityError as error:
        raise PersistenceIntegrityError("durable definition constraint failed") from error


def _parse_project(row: sqlite3.Row) -> Project:
    try:
        value = Project.model_validate_json(cast(str, row["payload_json"]))
    except (ValidationError, ValueError, TypeError) as error:
        raise PersistenceIntegrityError("stored Project payload is invalid") from error
    if value.id != row["id"]:
        raise PersistenceIntegrityError("Project row identity disagrees with payload")
    return value


def _parse_slice(row: sqlite3.Row) -> Slice:
    try:
        value = Slice.model_validate_json(cast(str, row["payload_json"]))
    except (ValidationError, ValueError, TypeError) as error:
        raise PersistenceIntegrityError("stored Slice payload is invalid") from error
    if value.id != row["id"] or value.project_id != row["project_id"]:
        raise PersistenceIntegrityError("Slice indexed identity disagrees with payload")
    return value


def _load_project(
    connection: sqlite3.Connection, project_id: ProjectId
) -> ProjectDefinitionSnapshot | None:
    row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if row is None:
        history = _project_history(connection, project_id)
        if history and history[-1].operation is not DefinitionOperation.DELETE:
            raise PersistenceIntegrityError(
                "Project history exists without a current row or DELETE"
            )
        return None
    value = _parse_project(row)
    revision = int(row["definition_revision"])
    _verify_project_history(connection, project_id, revision, value)
    return ProjectDefinitionSnapshot(value=value, definition_revision=revision)


def _load_slice(
    connection: sqlite3.Connection, slice_id: SliceId
) -> SliceDefinitionSnapshot | None:
    row = connection.execute("SELECT * FROM slices WHERE id = ?", (slice_id,)).fetchone()
    if row is None:
        history = _slice_history(connection, slice_id)
        if history and history[-1].operation is not DefinitionOperation.DELETE:
            raise PersistenceIntegrityError("Slice history exists without a current row or DELETE")
        return None
    value = _parse_slice(row)
    revision = int(row["definition_revision"])
    _verify_slice_history(connection, slice_id, revision, value)
    return SliceDefinitionSnapshot(value=value, definition_revision=revision)


def _decode_mutation(row: sqlite3.Row) -> MutationMetadata | None:
    if row["actor_json"] is None:
        if row["occurred_at"] is not None or row["reason"] is not None:
            raise PersistenceIntegrityError("definition revision has partial mutation metadata")
        return None
    try:
        actor = json.loads(cast(str, row["actor_json"]))
        raw = json.dumps(
            {"actor": actor, "occurred_at": row["occurred_at"], "reason": row["reason"]}
        )
        return MutationMetadata.model_validate_json(raw)
    except (ValidationError, ValueError, TypeError, json.JSONDecodeError) as error:
        raise PersistenceIntegrityError(
            "definition revision mutation metadata is invalid"
        ) from error


def _project_history(
    connection: sqlite3.Connection, project_id: ProjectId
) -> tuple[ProjectDefinitionRevision, ...]:
    rows = connection.execute(
        "SELECT * FROM project_definition_revisions WHERE project_id = ? "
        "ORDER BY definition_revision",
        (project_id,),
    ).fetchall()
    revisions: list[ProjectDefinitionRevision] = []
    try:
        for expected, row in enumerate(rows, 1):
            if int(row["definition_revision"]) != expected:
                raise PersistenceIntegrityError("Project definition history is not contiguous")
            payload = (
                None
                if row["payload_json"] is None
                else Project.model_validate_json(row["payload_json"])
            )
            revisions.append(
                ProjectDefinitionRevision(
                    project_id=project_id,
                    definition_revision=expected,
                    operation=DefinitionOperation(row["operation"]),
                    payload=payload,
                    mutation=_decode_mutation(row),
                )
            )
    except PersistenceIntegrityError:
        raise
    except (ValidationError, ValueError, TypeError) as error:
        raise PersistenceIntegrityError("Project definition history is invalid") from error
    if not revisions:
        return ()
    if (
        any(item.operation is DefinitionOperation.SEED for item in revisions[1:])
        or (revisions[0].operation not in {DefinitionOperation.SEED, DefinitionOperation.CREATE})
        or any(item.operation is DefinitionOperation.CREATE for item in revisions[1:])
    ):
        raise PersistenceIntegrityError(
            "Project definition history has an invalid operation sequence"
        )
    if any(item.operation is DefinitionOperation.DELETE for item in revisions[:-1]):
        raise PersistenceIntegrityError("Project definition history continues after DELETE")
    return tuple(revisions)


def _verify_project_history(
    connection: sqlite3.Connection, project_id: ProjectId, current_revision: int, current: Project
) -> None:
    revisions = _project_history(connection, project_id)
    if not revisions or len(revisions) != current_revision:
        raise PersistenceIntegrityError(
            "Project current revision disagrees with definition history"
        )
    latest = revisions[-1]
    if latest.operation is DefinitionOperation.DELETE or latest.payload != current:
        raise PersistenceIntegrityError(
            "Project current value disagrees with latest definition revision"
        )


def _slice_history(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[SliceDefinitionRevision, ...]:
    rows = connection.execute(
        "SELECT * FROM slice_definition_revisions WHERE slice_id = ? ORDER BY definition_revision",
        (slice_id,),
    ).fetchall()
    revisions: list[SliceDefinitionRevision] = []
    try:
        for expected, row in enumerate(rows, 1):
            if int(row["definition_revision"]) != expected:
                raise PersistenceIntegrityError("Slice definition history is not contiguous")
            payload = (
                None
                if row["payload_json"] is None
                else Slice.model_validate_json(row["payload_json"])
            )
            revision = SliceDefinitionRevision(
                slice_id=slice_id,
                project_id=row["project_id"],
                definition_revision=expected,
                operation=DefinitionOperation(row["operation"]),
                payload=payload,
                mutation=_decode_mutation(row),
            )
            revisions.append(revision)
    except PersistenceIntegrityError:
        raise
    except (ValidationError, ValueError, TypeError) as error:
        raise PersistenceIntegrityError("Slice definition history is invalid") from error
    if not revisions:
        return ()
    if (
        any(item.operation is DefinitionOperation.SEED for item in revisions[1:])
        or (revisions[0].operation not in {DefinitionOperation.SEED, DefinitionOperation.CREATE})
        or any(item.operation is DefinitionOperation.CREATE for item in revisions[1:])
    ):
        raise PersistenceIntegrityError(
            "Slice definition history has an invalid operation sequence"
        )
    if any(item.operation is DefinitionOperation.DELETE for item in revisions[:-1]):
        raise PersistenceIntegrityError("Slice definition history continues after DELETE")
    return tuple(revisions)


def _verify_slice_history(
    connection: sqlite3.Connection, slice_id: SliceId, current_revision: int, current: Slice
) -> None:
    revisions = _slice_history(connection, slice_id)
    if not revisions or len(revisions) != current_revision:
        raise PersistenceIntegrityError("Slice current revision disagrees with definition history")
    latest = revisions[-1]
    if latest.operation is DefinitionOperation.DELETE or latest.payload != current:
        raise PersistenceIntegrityError(
            "Slice current value disagrees with latest definition revision"
        )


def _append_project_revision(
    connection: sqlite3.Connection,
    project_id: ProjectId,
    revision: int,
    operation: DefinitionOperation,
    value: Project | None,
    mutation: MutationMetadata,
) -> None:
    connection.execute(
        "INSERT INTO project_definition_revisions(project_id, definition_revision, operation, "
        "payload_json, actor_json, occurred_at, reason) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            project_id,
            revision,
            operation.value,
            None if value is None else _json(value),
            _json(mutation.actor),
            _time_text(mutation),
            mutation.reason,
        ),
    )


def _append_slice_revision(
    connection: sqlite3.Connection,
    value: Slice,
    revision: int,
    operation: DefinitionOperation,
    mutation: MutationMetadata,
) -> None:
    connection.execute(
        "INSERT INTO slice_definition_revisions(slice_id, project_id, definition_revision, "
        "operation, payload_json, actor_json, occurred_at, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            value.id,
            value.project_id,
            revision,
            operation.value,
            None if operation is DefinitionOperation.DELETE else _json(value),
            _json(mutation.actor),
            _time_text(mutation),
            mutation.reason,
        ),
    )


def _history_exists(connection: sqlite3.Connection, table: str, key: str, identity: str) -> bool:
    return (
        connection.execute(f"SELECT 1 FROM {table} WHERE {key} = ? LIMIT 1", (identity,)).fetchone()
        is not None
    )


def _origin_error(
    subject_type: OriginSubjectType,
    subject_id: ProjectId | SliceId,
    epoch: OperationalHistoryEpochResolution,
    code: OriginDiagnosticCode,
    message: str,
) -> OperationalOriginResolution:
    return origin_resolution_not_established(
        subject_type,
        subject_id,
        epoch.epoch,
        code,
        message,
    )


def resolve_project_origin_from_connection(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    project_id: ProjectId,
) -> OperationalOriginResolution:
    """Resolve one Project origin against the unique epoch and exact CREATE record."""

    from relay_engine.adoption.persistence import resolve_project_adoption_origin_from_connection

    adoption_resolution = resolve_project_adoption_origin_from_connection(connection, project_id)
    if adoption_resolution is not None:
        return adoption_resolution

    from relay_engine.persistence.store import (
        load_operational_history_epoch_resolution_from_connection,
        load_operational_origin_records_from_connection,
    )

    epoch = load_operational_history_epoch_resolution_from_connection(connection)
    if epoch.state is not OriginResolutionState.ESTABLISHED or epoch.epoch is None:
        return _origin_error(
            OriginSubjectType.PROJECT,
            project_id,
            epoch,
            OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            "The database-wide operational-history epoch is not established.",
        )
    try:
        records = load_operational_origin_records_from_connection(
            connection,
            subject_type=OriginSubjectType.PROJECT,
            subject_id=project_id,
        )
        creation_revision = (
            get_project_revision(database, project_id, 1)
            if any(record.origin is OperationalOrigin.NATIVE_RELAY for record in records)
            else None
        )
    except (PersistenceIntegrityError, ProjectNotFound) as error:
        return _origin_error(
            OriginSubjectType.PROJECT,
            project_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_RECORD,
            str(error),
        )
    return resolve_origin_chain(
        records,
        subject_type=OriginSubjectType.PROJECT,
        subject_id=project_id,
        project_id=project_id,
        epoch_resolution=epoch,
        creation_revision=creation_revision,
    )


def resolve_project_origin(
    database: RelayDatabase,
    project_id: ProjectId,
) -> OperationalOriginResolution:
    """Resolve one Project origin as a read-only diagnostic operation."""

    with read_transaction(database) as connection:
        return resolve_project_origin_from_connection(database, connection, project_id)


def resolve_slice_origin_from_connection(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    slice_id: SliceId,
    project_id: ProjectId,
) -> OperationalOriginResolution:
    """Resolve one Slice origin and enforce the one-way Project/Slice rule."""

    from relay_engine.adoption.persistence import (
        project_adoption_mode_present_from_connection,
        resolve_slice_adoption_origin_from_connection,
    )

    if project_adoption_mode_present_from_connection(connection, project_id):
        project_origin = resolve_project_origin_from_connection(database, connection, project_id)
        return resolve_slice_adoption_origin_from_connection(
            connection,
            slice_id,
            project_id,
            project_origin,
        )

    from relay_engine.persistence.store import (
        load_operational_history_epoch_resolution_from_connection,
        load_operational_origin_records_from_connection,
    )

    epoch = load_operational_history_epoch_resolution_from_connection(connection)
    if epoch.state is not OriginResolutionState.ESTABLISHED or epoch.epoch is None:
        return _origin_error(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            "The database-wide operational-history epoch is not established.",
        )
    project_origin = resolve_project_origin_from_connection(database, connection, project_id)
    if project_origin.state is not OriginResolutionState.ESTABLISHED:
        return _origin_error(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.PROJECT_ORIGIN_NOT_ESTABLISHED,
            "Owning Project origin is not established; Slice hierarchy cannot be validated.",
        )
    try:
        records = load_operational_origin_records_from_connection(
            connection,
            subject_type=OriginSubjectType.SLICE,
            subject_id=slice_id,
        )
        creation_revision = (
            get_slice_revision(database, slice_id, 1)
            if any(record.origin is OperationalOrigin.NATIVE_RELAY for record in records)
            else None
        )
    except (PersistenceIntegrityError, SliceNotFound) as error:
        return _origin_error(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_RECORD,
            str(error),
        )
    resolution = resolve_origin_chain(
        records,
        subject_type=OriginSubjectType.SLICE,
        subject_id=slice_id,
        project_id=project_id,
        epoch_resolution=epoch,
        creation_revision=creation_revision,
    )
    if (
        resolution.state is OriginResolutionState.ESTABLISHED
        and resolution.origin is OperationalOrigin.PRE_GENESIS
        and project_origin.origin is not OperationalOrigin.PRE_GENESIS
    ):
        return _origin_error(
            OriginSubjectType.SLICE,
            slice_id,
            epoch,
            OriginDiagnosticCode.HIERARCHY_CONFLICT,
            "A PRE_GENESIS Slice requires an independently proven PRE_GENESIS Project.",
        )
    return resolution


def resolve_slice_origin(
    database: RelayDatabase,
    slice_id: SliceId,
    project_id: ProjectId,
) -> OperationalOriginResolution:
    """Resolve one Slice origin and its owning Project hierarchy read-only."""

    with read_transaction(database) as connection:
        return resolve_slice_origin_from_connection(database, connection, slice_id, project_id)


def require_slice_origin_governance_scope_from_connection(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    slice_id: SliceId,
) -> None:
    """Require valid origin for one Slice and its transitive dependency scope."""

    first = _load_slice(connection, slice_id)
    if first is None:
        raise SliceNotFound(slice_id)
    project_origin = resolve_project_origin_from_connection(
        database, connection, first.value.project_id
    )
    if project_origin.state is not OriginResolutionState.ESTABLISHED:
        raise OperationalOriginNotEstablished(
            f"Project {first.value.project_id} origin is not established"
        )

    def scope_facts(current_id: SliceId) -> tuple[tuple[SliceId, ...], bool]:
        current = _load_slice(connection, current_id)
        if current is None or current.value.project_id != first.value.project_id:
            raise PersistenceIntegrityError(
                "Slice governance dependency is missing or crosses Project boundaries"
            )
        resolution = resolve_slice_origin_from_connection(
            database, connection, current_id, first.value.project_id
        )
        return (
            current.value.dependency_ids,
            resolution.state is OriginResolutionState.ESTABLISHED,
        )

    unresolved = unresolved_origin_dependency_scope(slice_id, scope_facts)
    if unresolved:
        raise OperationalOriginNotEstablished(f"Slice {unresolved[0]} origin is not established")


def _native_origin_record(
    *,
    subject_type: OriginSubjectType,
    subject_id: ProjectId | SliceId,
    project_id: ProjectId,
    payload: Project | Slice,
    mutation: MutationMetadata,
    epoch: OperationalHistoryEpochResolution,
) -> OperationalOriginRecordV1:
    if epoch.state is not OriginResolutionState.ESTABLISHED or epoch.epoch is None:
        raise OperationalOriginNotEstablished(
            "database operational-history epoch is not established"
        )
    if mutation.occurred_at <= epoch.epoch.genesis_cut_at:
        raise OperationalOriginNotEstablished("CREATE timestamp does not occur after epoch T1")
    proof = NativeRelayOriginProofV1(
        proof_type="NATIVE_RELAY",
        subject_type=subject_type,
        subject_id=subject_id,
        definition_revision=1,
        operation="CREATE",
        creation_payload_digest=definition_payload_digest(payload),
        actor=mutation.actor,
        created_at=mutation.occurred_at,
        reason=mutation.reason,
    )
    subject_name = "project" if subject_type is OriginSubjectType.PROJECT else "slice"
    return build_operational_origin_record(
        record_id=new_id("oor_"),
        subject_type=subject_type,
        subject_id=subject_id,
        project_id=project_id,
        record_kind=OriginRecordKind.INITIAL,
        origin=OperationalOrigin.NATIVE_RELAY,
        epoch_id=epoch.epoch.epoch_id,
        epoch_digest=epoch.epoch.epoch_digest,
        proof=proof,
        recorded_at=mutation.occurred_at,
        recorded_by=mutation.actor,
        establishing_authority_id=f"{subject_name}_definition_revisions/{subject_id}/1",
    )


def create_project(
    database: RelayDatabase, value: Project, mutation: MutationMetadata
) -> ProjectMutationResult:
    """Create a Project through the sole post-v4 audited mutation path."""
    from relay_engine.persistence.store import (
        append_native_origin_for_creation_from_connection,
        load_operational_history_epoch_resolution_from_connection,
    )

    metadata = _mutation(mutation)
    with _transaction(database) as connection:
        current = _load_project(connection, value.id)
        if current is not None:
            if current.definition_revision == 1 and current.value == value:
                origin = resolve_project_origin_from_connection(database, connection, value.id)
                if origin.state is not OriginResolutionState.ESTABLISHED:
                    raise OperationalOriginNotEstablished(
                        f"Project {value.id} origin is not established"
                    )
                return ProjectMutationResult(snapshot=current, changed=False)
            raise ProjectAlreadyExists(value.id)
        if _history_exists(connection, "project_definition_revisions", "project_id", value.id):
            raise ProjectIdentifierRetired(value.id)
        epoch = load_operational_history_epoch_resolution_from_connection(connection)
        origin = _native_origin_record(
            subject_type=OriginSubjectType.PROJECT,
            subject_id=value.id,
            project_id=value.id,
            payload=value,
            mutation=metadata,
            epoch=epoch,
        )
        connection.execute(
            "INSERT INTO projects(id, payload_json, definition_revision) VALUES (?, ?, 1)",
            (value.id, _json(value)),
        )
        _append_project_revision(
            connection, value.id, 1, DefinitionOperation.CREATE, value, metadata
        )
        append_native_origin_for_creation_from_connection(connection, origin)
    return ProjectMutationResult(
        snapshot=ProjectDefinitionSnapshot(value=value, definition_revision=1), changed=True
    )


def get_project(database: RelayDatabase, project_id: ProjectId) -> ProjectDefinitionSnapshot:
    snapshot = _load_project(database.connection, project_id)
    if snapshot is None:
        raise ProjectNotFound(project_id)
    return snapshot


def list_projects(database: RelayDatabase) -> tuple[ProjectDefinitionSnapshot, ...]:
    retired = database.connection.execute(
        "SELECT DISTINCT project_id FROM project_definition_revisions "
        "WHERE NOT EXISTS (SELECT 1 FROM projects "
        "WHERE projects.id = project_definition_revisions.project_id) "
        "ORDER BY project_id"
    ).fetchall()
    for row in retired:
        history = _project_history(database.connection, row["project_id"])
        if not history or history[-1].operation is not DefinitionOperation.DELETE:
            raise PersistenceIntegrityError("retired Project history has no terminal DELETE")
    rows = database.connection.execute("SELECT * FROM projects ORDER BY id").fetchall()
    result: list[ProjectDefinitionSnapshot] = []
    for row in rows:
        value = _parse_project(row)
        revision = int(row["definition_revision"])
        _verify_project_history(database.connection, value.id, revision, value)
        result.append(ProjectDefinitionSnapshot(value=value, definition_revision=revision))
    return tuple(result)


def get_project_revision(
    database: RelayDatabase, project_id: ProjectId, definition_revision: int
) -> ProjectDefinitionRevision:
    revisions = _project_history(database.connection, project_id)
    if definition_revision < 1 or definition_revision > len(revisions):
        raise ProjectNotFound(f"{project_id} revision {definition_revision}")
    return revisions[definition_revision - 1]


def update_project(
    database: RelayDatabase,
    expected_definition_revision: int,
    target: Project,
    mutation: MutationMetadata,
) -> ProjectMutationResult:
    metadata = _mutation(mutation)
    with _transaction(database) as connection:
        current = _load_project(connection, target.id)
        if current is None:
            raise ProjectNotFound(target.id)
        if target.primary_repository != current.value.primary_repository:
            raise ProjectRepositoryImmutable(target.id)
        if expected_definition_revision != current.definition_revision:
            raise DefinitionRevisionConflict(
                f"Project {target.id}: expected {expected_definition_revision}, "
                f"current {current.definition_revision}"
            )
        if target == current.value:
            return ProjectMutationResult(snapshot=current, changed=False)
        next_revision = current.definition_revision + 1
        _append_project_revision(
            connection, target.id, next_revision, DefinitionOperation.UPDATE, target, metadata
        )
        cursor = connection.execute(
            "UPDATE projects SET payload_json = ?, definition_revision = ? "
            "WHERE id = ? AND definition_revision = ?",
            (_json(target), next_revision, target.id, current.definition_revision),
        )
        if cursor.rowcount != 1:
            raise DefinitionRevisionConflict(f"Project {target.id} changed during update")
    return ProjectMutationResult(
        snapshot=ProjectDefinitionSnapshot(value=target, definition_revision=next_revision),
        changed=True,
    )


def _slice_values(connection: sqlite3.Connection, project_id: ProjectId) -> dict[SliceId, Slice]:
    rows = connection.execute(
        "SELECT * FROM slices WHERE project_id = ? ORDER BY id", (project_id,)
    ).fetchall()
    values: dict[SliceId, Slice] = {}
    for row in rows:
        value = _parse_slice(row)
        _verify_slice_history(connection, value.id, int(row["definition_revision"]), value)
        values[value.id] = value
    return values


def _assert_acyclic(edges: dict[SliceId, tuple[SliceId, ...]], error_type: type[Exception]) -> None:
    visiting: set[SliceId] = set()
    visited: set[SliceId] = set()

    def visit(node: SliceId) -> None:
        if node in visiting:
            raise error_type(node)
        if node in visited:
            return
        visiting.add(node)
        for target in edges.get(node, ()):
            if target in edges:
                visit(target)
        visiting.remove(node)
        visited.add(node)

    for node in edges:
        visit(node)


def _validate_graph(connection: sqlite3.Connection, target: Slice, *, replacing: bool) -> None:
    if (
        connection.execute("SELECT 1 FROM projects WHERE id = ?", (target.project_id,)).fetchone()
        is None
    ):
        raise CrossProjectSliceReference(f"owning Project {target.project_id} does not exist")
    existing = _slice_values(connection, target.project_id)
    if replacing:
        existing.pop(target.id, None)
    existing[target.id] = target
    for value in existing.values():
        references = (
            (value.parent_slice_id,) if value.parent_slice_id else ()
        ) + value.dependency_ids
        for reference in references:
            if reference not in existing:
                raise CrossProjectSliceReference(
                    f"Slice reference {reference} is missing or cross-Project"
                )
    parent_edges = {
        item_id: (() if value.parent_slice_id is None else (value.parent_slice_id,))
        for item_id, value in existing.items()
    }
    dependency_edges = {item_id: value.dependency_ids for item_id, value in existing.items()}
    _assert_acyclic(parent_edges, SliceParentCycle)
    _assert_acyclic(dependency_edges, SliceDependencyCycle)


def create_slice(
    database: RelayDatabase, value: Slice, mutation: MutationMetadata
) -> SliceMutationResult:
    metadata = _mutation(mutation)
    from relay_engine.adoption.persistence import (
        append_project_native_origin_from_connection,
        load_project_operational_epoch_resolution_from_connection,
    )
    from relay_engine.persistence.store import (
        append_native_origin_for_creation_from_connection,
        load_operational_history_epoch_resolution_from_connection,
    )
    from relay_engine.project_slice.origin import (
        ProjectOperationalOriginRecordV1,
        build_project_operational_origin_record,
    )

    with _transaction(database) as connection:
        current = _load_slice(connection, value.id)
        if current is not None:
            if current.definition_revision == 1 and current.value == value:
                origin = resolve_slice_origin_from_connection(
                    database, connection, value.id, value.project_id
                )
                if origin.state is not OriginResolutionState.ESTABLISHED:
                    raise OperationalOriginNotEstablished(
                        f"Slice {value.id} origin is not established"
                    )
                return SliceMutationResult(snapshot=current, changed=False)
            raise SliceAlreadyExists(value.id)
        if _history_exists(connection, "slice_definition_revisions", "slice_id", value.id):
            raise SliceIdentifierRetired(value.id)
        _validate_graph(connection, value, replacing=False)
        project_origin = resolve_project_origin_from_connection(
            database, connection, value.project_id
        )
        if project_origin.state is not OriginResolutionState.ESTABLISHED:
            raise OperationalOriginNotEstablished(
                "owning Project operational origin is not established"
            )
        project_epoch = load_project_operational_epoch_resolution_from_connection(
            connection, value.project_id
        )
        if project_epoch.record_ids:
            epoch_value = project_epoch.epoch
            if project_epoch.state is not OriginResolutionState.ESTABLISHED or epoch_value is None:
                raise OperationalOriginNotEstablished(
                    "Project adoption epoch is invalid or ambiguous"
                )
            if metadata.occurred_at <= epoch_value.genesis_cut_at:
                raise OperationalOriginNotEstablished(
                    "Slice CREATE timestamp does not occur after Project T1"
                )
            proof = NativeRelayOriginProofV1(
                proof_type="NATIVE_RELAY",
                subject_type=OriginSubjectType.SLICE,
                subject_id=value.id,
                definition_revision=1,
                operation="CREATE",
                creation_payload_digest=definition_payload_digest(value),
                actor=metadata.actor,
                created_at=metadata.occurred_at,
                reason=metadata.reason,
            )
            origin = build_project_operational_origin_record(
                record_id=new_id("oor_"),
                subject_type=OriginSubjectType.SLICE,
                subject_id=value.id,
                project_id=value.project_id,
                record_kind=OriginRecordKind.INITIAL,
                origin=OperationalOrigin.NATIVE_RELAY,
                epoch_id=epoch_value.epoch_id,
                epoch_digest=epoch_value.epoch_digest,
                proof=proof,
                recorded_at=metadata.occurred_at,
                recorded_by=metadata.actor,
                establishing_authority_id=f"slice_definition_revisions/{value.id}/1",
            )
        else:
            epoch = load_operational_history_epoch_resolution_from_connection(connection)
            origin = _native_origin_record(
                subject_type=OriginSubjectType.SLICE,
                subject_id=value.id,
                project_id=value.project_id,
                payload=value,
                mutation=metadata,
                epoch=epoch,
            )
        connection.execute(
            "INSERT INTO slices(id, project_id, payload_json, definition_revision) "
            "VALUES (?, ?, ?, 1)",
            (value.id, value.project_id, _json(value)),
        )
        _append_slice_revision(connection, value, 1, DefinitionOperation.CREATE, metadata)
        if isinstance(origin, ProjectOperationalOriginRecordV1):
            append_project_native_origin_from_connection(connection, origin)
        else:
            append_native_origin_for_creation_from_connection(connection, origin)
    return SliceMutationResult(
        snapshot=SliceDefinitionSnapshot(value=value, definition_revision=1), changed=True
    )


def get_slice(database: RelayDatabase, slice_id: SliceId) -> SliceDefinitionSnapshot:
    snapshot = _load_slice(database.connection, slice_id)
    if snapshot is None:
        raise SliceNotFound(slice_id)
    return snapshot


def list_slices(
    database: RelayDatabase, project_id: ProjectId
) -> tuple[SliceDefinitionSnapshot, ...]:
    if (
        database.connection.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone()
        is None
    ):
        raise ProjectNotFound(project_id)
    retired = database.connection.execute(
        "SELECT DISTINCT slice_id FROM slice_definition_revisions "
        "WHERE project_id = ? AND NOT EXISTS "
        "(SELECT 1 FROM slices WHERE slices.id = slice_definition_revisions.slice_id) "
        "ORDER BY slice_id",
        (project_id,),
    ).fetchall()
    for row in retired:
        history = _slice_history(database.connection, row["slice_id"])
        if not history or history[-1].operation is not DefinitionOperation.DELETE:
            raise PersistenceIntegrityError("retired Slice history has no terminal DELETE")
    snapshots: list[SliceDefinitionSnapshot] = []
    rows = database.connection.execute(
        "SELECT * FROM slices WHERE project_id = ? ORDER BY id", (project_id,)
    ).fetchall()
    for row in rows:
        value = _parse_slice(row)
        revision = int(row["definition_revision"])
        _verify_slice_history(database.connection, value.id, revision, value)
        snapshots.append(SliceDefinitionSnapshot(value=value, definition_revision=revision))
    return tuple(snapshots)


def get_slice_revision(
    database: RelayDatabase, slice_id: SliceId, definition_revision: int
) -> SliceDefinitionRevision:
    revisions = _slice_history(database.connection, slice_id)
    if definition_revision < 1 or definition_revision > len(revisions):
        raise SliceNotFound(f"{slice_id} revision {definition_revision}")
    return revisions[definition_revision - 1]


def update_slice(
    database: RelayDatabase,
    expected_definition_revision: int,
    target: Slice,
    mutation: MutationMetadata,
) -> SliceMutationResult:
    metadata = _mutation(mutation)
    with _transaction(database) as connection:
        return update_slice_from_connection(
            connection,
            expected_definition_revision,
            target,
            metadata,
        )


def update_slice_from_connection(
    connection: sqlite3.Connection,
    expected_definition_revision: int,
    target: Slice,
    mutation: MutationMetadata,
) -> SliceMutationResult:
    """Update one Slice inside a caller-owned SQLite transaction."""

    if not connection.in_transaction:
        raise PersistenceError("Slice update requires an active caller-owned transaction")
    metadata = _mutation(mutation)
    try:
        current = _load_slice(connection, target.id)
        if current is None:
            raise SliceNotFound(target.id)
        if target.project_id != current.value.project_id:
            raise CrossProjectSliceReference("Slice project ownership is immutable")
        if expected_definition_revision != current.definition_revision:
            raise DefinitionRevisionConflict(
                f"Slice {target.id}: expected {expected_definition_revision}, "
                f"current {current.definition_revision}"
            )
        if target == current.value:
            return SliceMutationResult(snapshot=current, changed=False)
        if (
            connection.execute(
                "SELECT 1 FROM lifecycle_current WHERE slice_id = ?", (target.id,)
            ).fetchone()
            or connection.execute(
                "SELECT 1 FROM lifecycle_events WHERE slice_id = ? LIMIT 1", (target.id,)
            ).fetchone()
        ):
            raise SliceDefinitionFrozen(target.id)
        if connection.execute(
            "SELECT 1 FROM handover_gate_revisions WHERE slice_id = ? LIMIT 1", (target.id,)
        ).fetchone():
            raise SliceDefinitionFrozen(target.id)
        _validate_graph(connection, target, replacing=True)
        downstream = connection.execute(
            "SELECT * FROM slices WHERE id <> ? ORDER BY id",
            (target.id,),
        ).fetchall()
        for row in downstream:
            dependent = _parse_slice(row)
            if target.id in dependent.dependency_ids:
                raise SliceHasDownstreamDependents(target.id)
        next_revision = current.definition_revision + 1
        _append_slice_revision(
            connection, target, next_revision, DefinitionOperation.UPDATE, metadata
        )
        cursor = connection.execute(
            "UPDATE slices SET payload_json = ?, definition_revision = ? "
            "WHERE id = ? AND definition_revision = ?",
            (_json(target), next_revision, target.id, current.definition_revision),
        )
        if cursor.rowcount != 1:
            raise DefinitionRevisionConflict(f"Slice {target.id} changed during update")
    except sqlite3.IntegrityError as error:
        raise PersistenceIntegrityError("durable definition constraint failed") from error
    return SliceMutationResult(
        snapshot=SliceDefinitionSnapshot(value=target, definition_revision=next_revision),
        changed=True,
    )


def _project_delete_blockers(
    connection: sqlite3.Connection, project_id: ProjectId
) -> tuple[str, ...]:
    checks = (
        ("slices", "SELECT 1 FROM slices WHERE project_id = ? LIMIT 1", "slices"),
        ("baselines", "SELECT 1 FROM baselines WHERE project_id = ? LIMIT 1", "baselines"),
        (
            "github_installations",
            "SELECT 1 FROM github_installations WHERE project_id = ? LIMIT 1",
            "github_installations",
        ),
        (
            "repository_mutation_authorizations",
            "SELECT 1 FROM repository_mutation_authorizations WHERE project_id = ? LIMIT 1",
            "repository_mutation_authorizations",
        ),
    )
    return tuple(
        name for _, query, name in checks if connection.execute(query, (project_id,)).fetchone()
    )


def delete_project(
    database: RelayDatabase,
    project_id: ProjectId,
    expected_definition_revision: int,
    mutation: MutationMetadata,
) -> ProjectDeleteResult:
    metadata = _mutation(mutation)
    with _transaction(database) as connection:
        current = _load_project(connection, project_id)
        if current is None:
            latest = connection.execute(
                "SELECT definition_revision, operation FROM project_definition_revisions "
                "WHERE project_id = ? ORDER BY definition_revision DESC LIMIT 1",
                (project_id,),
            ).fetchone()
            if latest is not None and latest["operation"] == DefinitionOperation.DELETE.value:
                return ProjectDeleteResult(
                    project_id=project_id,
                    definition_revision=int(latest["definition_revision"]),
                    deleted=False,
                    already_deleted=True,
                )
            raise ProjectNotFound(project_id)
        if expected_definition_revision != current.definition_revision:
            raise DefinitionRevisionConflict(project_id)
        blockers = _project_delete_blockers(connection, project_id)
        if blockers:
            raise ProjectDeleteForbidden(blockers)
        deleted_revision = current.definition_revision + 1
        _append_project_revision(
            connection, project_id, deleted_revision, DefinitionOperation.DELETE, None, metadata
        )
        cursor = connection.execute(
            "DELETE FROM projects WHERE id = ? AND definition_revision = ?",
            (project_id, current.definition_revision),
        )
        if cursor.rowcount != 1:
            raise DefinitionRevisionConflict(project_id)
    return ProjectDeleteResult(
        project_id=project_id,
        definition_revision=deleted_revision,
        deleted=True,
        already_deleted=False,
    )


def _slice_delete_blockers(connection: sqlite3.Connection, value: Slice) -> tuple[str, ...]:
    checks = (
        (
            "lifecycle_current",
            "SELECT 1 FROM lifecycle_current WHERE slice_id = ? LIMIT 1",
            (value.id,),
        ),
        (
            "lifecycle_events",
            "SELECT 1 FROM lifecycle_events WHERE slice_id = ? LIMIT 1",
            (value.id,),
        ),
        (
            "handover_gate_revisions",
            "SELECT 1 FROM handover_gate_revisions WHERE slice_id = ? LIMIT 1",
            (value.id,),
        ),
        (
            "gate_evaluation_records",
            "SELECT 1 FROM gate_evaluation_records WHERE slice_id = ? LIMIT 1",
            (value.id,),
        ),
        ("executions", "SELECT 1 FROM executions WHERE slice_id = ? LIMIT 1", (value.id,)),
    )
    found = [name for name, query, params in checks if connection.execute(query, params).fetchone()]
    for row in connection.execute(
        "SELECT * FROM slices WHERE id <> ? ORDER BY id", (value.id,)
    ).fetchall():
        dependent = _parse_slice(row)
        if dependent.parent_slice_id == value.id:
            found.append("child_slices")
            break
    for row in connection.execute(
        "SELECT * FROM slices WHERE id <> ? ORDER BY id", (value.id,)
    ).fetchall():
        dependent = _parse_slice(row)
        if value.id in dependent.dependency_ids:
            found.append("incoming_dependencies")
            break
    return tuple(found)


def delete_slice(
    database: RelayDatabase,
    slice_id: SliceId,
    expected_definition_revision: int,
    mutation: MutationMetadata,
) -> SliceDeleteResult:
    metadata = _mutation(mutation)
    with _transaction(database) as connection:
        current = _load_slice(connection, slice_id)
        if current is None:
            latest = connection.execute(
                "SELECT definition_revision, operation FROM slice_definition_revisions "
                "WHERE slice_id = ? ORDER BY definition_revision DESC LIMIT 1",
                (slice_id,),
            ).fetchone()
            if latest is not None and latest["operation"] == DefinitionOperation.DELETE.value:
                return SliceDeleteResult(
                    slice_id=slice_id,
                    definition_revision=int(latest["definition_revision"]),
                    deleted=False,
                    already_deleted=True,
                )
            raise SliceNotFound(slice_id)
        if expected_definition_revision != current.definition_revision:
            raise DefinitionRevisionConflict(slice_id)
        blockers = _slice_delete_blockers(connection, current.value)
        if blockers:
            raise SliceDeleteForbidden(blockers)
        deleted_revision = current.definition_revision + 1
        _append_slice_revision(
            connection, current.value, deleted_revision, DefinitionOperation.DELETE, metadata
        )
        cursor = connection.execute(
            "DELETE FROM slices WHERE id = ? AND definition_revision = ?",
            (slice_id, current.definition_revision),
        )
        if cursor.rowcount != 1:
            raise DefinitionRevisionConflict(slice_id)
    return SliceDeleteResult(
        slice_id=slice_id, definition_revision=deleted_revision, deleted=True, already_deleted=False
    )


__all__ = [
    "create_project",
    "create_slice",
    "delete_project",
    "delete_slice",
    "get_project",
    "get_project_revision",
    "get_slice",
    "get_slice_revision",
    "list_projects",
    "list_slices",
    "update_project",
    "update_slice",
]
