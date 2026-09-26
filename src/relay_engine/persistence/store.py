"""Concrete insert/load operations and causal SQLite state transitions."""

import json
import sqlite3
from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import cast

from pydantic import BaseModel, TypeAdapter, ValidationError

from relay_engine.domain.ids import (
    ArtifactId,
    AuthorizationId,
    BaselineId,
    DecisionId,
    EventId,
    EvidenceId,
    ExecutionId,
    GateEvaluationRecordId,
    HandoverGateId,
    HumanDecisionId,
    ProjectId,
    SliceId,
)
from relay_engine.domain.models import Artifact, Baseline, Decision, Evidence, Project, Slice
from relay_engine.domain.references import ActorRef
from relay_engine.governance import (
    AuthorizationGrant,
    GateEvaluation,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HumanGateDecision,
    evaluate_handover_gates,
    execute_handover,
)
from relay_engine.lifecycle import (
    BlockageChanged,
    LifecycleEvent,
    LifecycleInitialized,
    PhaseChanged,
    SliceLifecycle,
    ValidityChanged,
    replay_lifecycle,
)
from relay_engine.lifecycle.errors import LifecycleReplayError
from relay_engine.persistence.database import RelayDatabase, write_transaction
from relay_engine.persistence.errors import (
    ConcurrencyConflict,
    DatabaseUnavailable,
    PersistenceError,
    PersistenceIntegrityError,
)
from relay_engine.persistence.records import ExecutionRecord, GateEvaluationRecord

_EVENT_ADAPTER: TypeAdapter[LifecycleEvent] = TypeAdapter(LifecycleEvent)
_DECISION_ADAPTER: TypeAdapter[HumanGateDecision] = TypeAdapter(HumanGateDecision)
_EVENT_TYPES: dict[str, type[BaseModel]] = {
    "LifecycleInitialized": LifecycleInitialized,
    "PhaseChanged": PhaseChanged,
    "BlockageChanged": BlockageChanged,
    "ValidityChanged": ValidityChanged,
}


def _canonical_json(model: BaseModel) -> str:
    return json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _parse_payload[ModelT: BaseModel](
    row: sqlite3.Row,
    model_type: type[ModelT],
    indexed_fields: Mapping[str, str],
) -> ModelT:
    try:
        model = model_type.model_validate_json(cast(str, row["payload_json"]))
    except (ValidationError, ValueError, TypeError) as error:
        raise PersistenceIntegrityError("stored typed payload is invalid") from error
    for column, field_name in indexed_fields.items():
        field_value: object = model
        for component in field_name.split("."):
            field_value = getattr(field_value, component)
        if isinstance(field_value, datetime):
            field_value = _datetime_text(field_value)
        if row[column] != field_value:
            raise PersistenceIntegrityError(
                f"stored indexed column {column!r} disagrees with its typed payload"
            )
    return model


def _insert_payload(
    connection: sqlite3.Connection,
    table: str,
    identity_column: str,
    identity: str,
    model: BaseModel,
    indexed_values: Mapping[str, object] | None = None,
) -> None:
    values = dict(indexed_values or {})
    values[identity_column] = identity
    names = tuple(values)
    columns = ", ".join((*names, "payload_json"))
    placeholders = ", ".join("?" for _ in range(len(names) + 1))
    connection.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
        (*values.values(), _canonical_json(model)),
    )


def _read_one[ModelT: BaseModel](
    connection: sqlite3.Connection,
    table: str,
    identity_column: str,
    identity: str,
    model_type: type[ModelT],
    indexed_fields: Mapping[str, str] | None = None,
) -> ModelT | None:
    row = connection.execute(
        f"SELECT * FROM {table} WHERE {identity_column} = ?", (identity,)
    ).fetchone()
    return None if row is None else _parse_payload(row, model_type, indexed_fields or {})


@contextmanager
def _write(database: RelayDatabase) -> Generator[sqlite3.Connection]:
    """Keep SQLite constraints within the public persistence error contract."""

    try:
        with write_transaction(database) as connection:
            yield connection
    except sqlite3.IntegrityError as error:
        raise PersistenceIntegrityError(
            "durable uniqueness or reference constraint failed"
        ) from error


def _read[ResultT](
    database: RelayDatabase,
    action: Callable[[sqlite3.Connection], ResultT],
) -> ResultT:
    try:
        return action(database.connection)
    except PersistenceError:
        raise
    except sqlite3.OperationalError as error:
        if _is_busy(error):
            raise DatabaseUnavailable("SQLite database is busy or locked") from error
        raise DatabaseUnavailable("SQLite read failed") from error
    except sqlite3.Error as error:
        raise DatabaseUnavailable("SQLite read failed") from error


def _is_busy(error: sqlite3.OperationalError) -> bool:
    message = str(error).lower()
    return "locked" in message or "busy" in message


def insert_project(database: RelayDatabase, value: Project) -> None:
    with _write(database) as connection:
        _insert_payload(connection, "projects", "id", value.id, value)


def load_project(database: RelayDatabase, project_id: ProjectId) -> Project | None:
    return _read(
        database,
        lambda connection: _read_one(
            connection, "projects", "id", project_id, Project, {"id": "id"}
        ),
    )


def insert_baseline(database: RelayDatabase, value: Baseline) -> None:
    with _write(database) as connection:
        _insert_payload(
            connection,
            "baselines",
            "id",
            value.id,
            value,
            {"project_id": value.project_id},
        )


def load_baseline(database: RelayDatabase, baseline_id: BaselineId) -> Baseline | None:
    return _read(
        database,
        lambda connection: _read_one(
            connection,
            "baselines",
            "id",
            baseline_id,
            Baseline,
            {"id": "id", "project_id": "project_id"},
        ),
    )


def insert_slice(database: RelayDatabase, value: Slice) -> None:
    with _write(database) as connection:
        _insert_payload(
            connection, "slices", "id", value.id, value, {"project_id": value.project_id}
        )


def load_slice(database: RelayDatabase, slice_id: SliceId) -> Slice | None:
    return _read(
        database,
        lambda connection: _read_one(
            connection,
            "slices",
            "id",
            slice_id,
            Slice,
            {"id": "id", "project_id": "project_id"},
        ),
    )


def insert_artifact(database: RelayDatabase, value: Artifact) -> None:
    with _write(database) as connection:
        _insert_payload(connection, "artifacts", "id", value.id, value)


def load_artifact(database: RelayDatabase, artifact_id: ArtifactId) -> Artifact | None:
    return _read(
        database,
        lambda connection: _read_one(
            connection, "artifacts", "id", artifact_id, Artifact, {"id": "id"}
        ),
    )


def insert_decision(database: RelayDatabase, value: Decision) -> None:
    with _write(database) as connection:
        _insert_payload(connection, "decisions", "id", value.id, value)


def load_decision(database: RelayDatabase, decision_id: DecisionId) -> Decision | None:
    return _read(
        database,
        lambda connection: _read_one(
            connection, "decisions", "id", decision_id, Decision, {"id": "id"}
        ),
    )


def insert_evidence(database: RelayDatabase, value: Evidence) -> None:
    with _write(database) as connection:
        _insert_payload(connection, "evidence", "id", value.id, value)


def load_evidence(database: RelayDatabase, evidence_id: EvidenceId) -> Evidence | None:
    return _read(
        database,
        lambda connection: _read_one(
            connection, "evidence", "id", evidence_id, Evidence, {"id": "id"}
        ),
    )


def _datetime_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _insert_event(connection: sqlite3.Connection, event: LifecycleEvent) -> None:
    connection.execute(
        "INSERT INTO lifecycle_events(event_id, slice_id, event_type, resulting_revision, "
        "occurred_at, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
        (
            event.event_id,
            event.slice_id,
            type(event).__name__,
            event.resulting_revision,
            _datetime_text(event.occurred_at),
            _canonical_json(event),
        ),
    )


def _load_events(connection: sqlite3.Connection, slice_id: SliceId) -> tuple[LifecycleEvent, ...]:
    rows = connection.execute(
        "SELECT * FROM lifecycle_events WHERE slice_id = ? ORDER BY resulting_revision ASC",
        (slice_id,),
    ).fetchall()
    events: list[LifecycleEvent] = []
    for row in rows:
        event_type = cast(str, row["event_type"])
        model_type = _EVENT_TYPES.get(event_type)
        if model_type is None:
            raise PersistenceIntegrityError(
                f"unknown persisted lifecycle event type {event_type!r}"
            )
        event = _parse_payload(
            row,
            cast(type[LifecycleEvent], model_type),
            {
                "event_id": "event_id",
                "slice_id": "slice_id",
                "resulting_revision": "resulting_revision",
                "occurred_at": "occurred_at",
            },
        )
        if (
            type(event).__name__ != row["event_type"]
            or _datetime_text(event.occurred_at) != row["occurred_at"]
        ):
            raise PersistenceIntegrityError("lifecycle event index columns disagree with payload")
        events.append(event)
    try:
        return tuple(_EVENT_ADAPTER.validate_python(item) for item in events)
    except ValidationError as error:
        raise PersistenceIntegrityError("stored lifecycle event is malformed") from error


def _load_current_row(connection: sqlite3.Connection, slice_id: SliceId) -> SliceLifecycle | None:
    row = connection.execute(
        "SELECT * FROM lifecycle_current WHERE slice_id = ?", (slice_id,)
    ).fetchone()
    if row is None:
        return None
    return _parse_payload(
        row,
        SliceLifecycle,
        {"slice_id": "slice_id", "revision": "revision"},
    )


def _load_current_and_history(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[SliceLifecycle | None, tuple[LifecycleEvent, ...]]:
    current = _load_current_row(connection, slice_id)
    events = _load_events(connection, slice_id)
    if current is None:
        if events:
            raise PersistenceIntegrityError("lifecycle history exists without a current snapshot")
        return None, ()
    if not events:
        raise PersistenceIntegrityError("current lifecycle snapshot exists without event history")
    try:
        replayed = replay_lifecycle(events)
    except LifecycleReplayError as error:
        raise PersistenceIntegrityError("durable lifecycle history cannot be replayed") from error
    if replayed != current:
        raise PersistenceIntegrityError("durable lifecycle history does not match current snapshot")
    return current, events


def persist_lifecycle_initialization(
    database: RelayDatabase,
    initial_lifecycle: SliceLifecycle,
    initialized_event: LifecycleInitialized,
) -> None:
    """Atomically establish the absent lifecycle projection and revision-zero event."""

    with _write(database) as connection:
        current, events = _load_current_and_history(connection, initial_lifecycle.slice_id)
        if current is not None or events:
            if current is not None and events:
                raise ConcurrencyConflict("lifecycle is already initialized")
            raise PersistenceIntegrityError("lifecycle initialization is only partially durable")
        if initial_lifecycle.revision != 0:
            raise PersistenceIntegrityError("lifecycle initialization must start at revision zero")
        if (
            initialized_event.slice_id != initial_lifecycle.slice_id
            or initialized_event.resulting_revision != 0
        ):
            raise PersistenceIntegrityError("initialization event does not identify revision zero")
        try:
            replayed = replay_lifecycle((initialized_event,))
        except LifecycleReplayError as error:
            raise PersistenceIntegrityError("initialization event is not replayable") from error
        if replayed != initial_lifecycle:
            raise PersistenceIntegrityError(
                "initialization event does not produce supplied snapshot"
            )
        _insert_event(connection, initialized_event)
        connection.execute(
            "INSERT INTO lifecycle_current(slice_id, revision, payload_json) VALUES (?, ?, ?)",
            (
                initial_lifecycle.slice_id,
                initial_lifecycle.revision,
                _canonical_json(initial_lifecycle),
            ),
        )


def persist_lifecycle_change(
    database: RelayDatabase,
    expected_lifecycle_revision: int,
    updated_lifecycle: SliceLifecycle,
    event: LifecycleEvent,
) -> None:
    """Prove accepted replay causality and atomically append one lifecycle change."""

    if expected_lifecycle_revision < 0:
        raise ValueError("expected lifecycle revision must be non-negative")
    with _write(database) as connection:
        current, history = _load_current_and_history(connection, updated_lifecycle.slice_id)
        if current is None:
            raise ConcurrencyConflict("lifecycle is not initialized")
        if current.revision != expected_lifecycle_revision:
            raise ConcurrencyConflict("expected lifecycle revision is stale")
        if isinstance(event, LifecycleInitialized):
            raise PersistenceIntegrityError("initialization is not a lifecycle mutation event")
        if (
            event.slice_id != current.slice_id
            or updated_lifecycle.slice_id != current.slice_id
            or event.resulting_revision != expected_lifecycle_revision + 1
            or updated_lifecycle.revision != expected_lifecycle_revision + 1
        ):
            raise PersistenceIntegrityError(
                "lifecycle event and snapshot identity or revision disagree"
            )
        try:
            replayed = replay_lifecycle((*history, event))
        except LifecycleReplayError as error:
            raise PersistenceIntegrityError(
                "candidate lifecycle event cannot replay from durable history"
            ) from error
        if replayed != updated_lifecycle:
            raise PersistenceIntegrityError(
                "candidate event does not produce supplied lifecycle snapshot"
            )

        _insert_event(connection, event)
        cursor = connection.execute(
            "UPDATE lifecycle_current SET revision = ?, payload_json = ? "
            "WHERE slice_id = ? AND revision = ?",
            (
                updated_lifecycle.revision,
                _canonical_json(updated_lifecycle),
                updated_lifecycle.slice_id,
                expected_lifecycle_revision,
            ),
        )
        if cursor.rowcount != 1:
            raise ConcurrencyConflict("lifecycle changed while committing the update")


def load_lifecycle_events(database: RelayDatabase, slice_id: SliceId) -> tuple[LifecycleEvent, ...]:
    def read(connection: sqlite3.Connection) -> tuple[LifecycleEvent, ...]:
        current, events = _load_current_and_history(connection, slice_id)
        return () if current is None else events

    return _read(database, read)


def load_current_lifecycle(database: RelayDatabase, slice_id: SliceId) -> SliceLifecycle | None:
    return _read(
        database,
        lambda connection: _load_current_and_history(connection, slice_id)[0],
    )


def verify_slice_history(database: RelayDatabase, slice_id: SliceId) -> None:
    """Read-only proof that exact stored lifecycle events produce current state."""

    def verify(connection: sqlite3.Connection) -> None:
        current, events = _load_current_and_history(connection, slice_id)
        if current is None or not events:
            raise PersistenceIntegrityError("slice has no complete durable lifecycle history")

    _read(database, verify)


def insert_handover_gate(database: RelayDatabase, value: HandoverGate) -> None:
    """Insert one immutable exact gate revision."""

    with _write(database) as connection:
        _insert_payload(
            connection,
            "handover_gate_revisions",
            "gate_id",
            value.gate_id,
            value,
            {
                "gate_revision": value.revision,
                "baseline_id": value.baseline_id,
                "slice_id": value.slice_id,
            },
        )


def load_handover_gate(
    database: RelayDatabase, gate_id: HandoverGateId, gate_revision: int
) -> HandoverGate | None:
    def read(connection: sqlite3.Connection) -> HandoverGate | None:
        row = connection.execute(
            "SELECT * FROM handover_gate_revisions WHERE gate_id = ? AND gate_revision = ?",
            (gate_id, gate_revision),
        ).fetchone()
        if row is None:
            return None
        gate = _parse_payload(
            row,
            HandoverGate,
            {"gate_id": "gate_id", "baseline_id": "baseline_id", "slice_id": "slice_id"},
        )
        if gate.revision != row["gate_revision"]:
            raise PersistenceIntegrityError("gate revision column disagrees with typed payload")
        return gate

    return _read(database, read)


def load_handover_gates(
    database: RelayDatabase, gate_id: HandoverGateId
) -> tuple[HandoverGate, ...]:
    def read(connection: sqlite3.Connection) -> tuple[HandoverGate, ...]:
        rows = connection.execute(
            "SELECT * FROM handover_gate_revisions WHERE gate_id = ? ORDER BY gate_revision ASC",
            (gate_id,),
        ).fetchall()
        values = tuple(
            _parse_payload(
                row,
                HandoverGate,
                {"gate_id": "gate_id", "baseline_id": "baseline_id", "slice_id": "slice_id"},
            )
            for row in rows
        )
        for row, gate in zip(rows, values, strict=True):
            if gate.revision != row["gate_revision"]:
                raise PersistenceIntegrityError("gate revision column disagrees with typed payload")
        return values

    return _read(database, read)


def load_latest_handover_gate(
    database: RelayDatabase, gate_id: HandoverGateId
) -> HandoverGate | None:
    gates = load_handover_gates(database, gate_id)
    return None if not gates else gates[-1]


def insert_authorization_grant(database: RelayDatabase, value: AuthorizationGrant) -> None:
    with _write(database) as connection:
        _insert_payload(
            connection,
            "authorization_grants",
            "authorization_id",
            value.authorization_id,
            value,
            {"baseline_id": value.baseline_id},
        )


def load_authorization_grant(
    database: RelayDatabase, authorization_id: AuthorizationId
) -> AuthorizationGrant | None:
    return _read(
        database,
        lambda connection: _read_one(
            connection,
            "authorization_grants",
            "authorization_id",
            authorization_id,
            AuthorizationGrant,
            {"authorization_id": "authorization_id", "baseline_id": "baseline_id"},
        ),
    )


def insert_human_decision(database: RelayDatabase, value: HumanGateDecision) -> None:
    decision_type = type(value).__name__
    with _write(database) as connection:
        connection.execute(
            "INSERT INTO human_decisions(decision_id, decision_type, baseline_id, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (value.decision_id, decision_type, value.baseline_id, _canonical_json(value)),
        )


def load_human_decision(
    database: RelayDatabase, decision_id: HumanDecisionId
) -> HumanGateDecision | None:
    def read(connection: sqlite3.Connection) -> HumanGateDecision | None:
        row = connection.execute(
            "SELECT * FROM human_decisions WHERE decision_id = ?", (decision_id,)
        ).fetchone()
        if row is None:
            return None
        try:
            value = _DECISION_ADAPTER.validate_json(cast(str, row["payload_json"]))
        except (ValidationError, ValueError, TypeError) as error:
            raise PersistenceIntegrityError("stored human decision payload is invalid") from error
        if (
            value.decision_id != row["decision_id"]
            or value.baseline_id != row["baseline_id"]
            or type(value).__name__ != row["decision_type"]
        ):
            raise PersistenceIntegrityError("human-decision index columns disagree with payload")
        return value

    return _read(database, read)


def insert_gate_evaluation_record(database: RelayDatabase, value: GateEvaluationRecord) -> None:
    """Append validated evaluation evidence; this record alone never authorizes execution."""

    with _write(database) as connection:
        _insert_payload(
            connection,
            "gate_evaluation_records",
            "record_id",
            value.id,
            value,
            {
                "baseline_id": value.context.baseline_id,
                "slice_id": value.context.lifecycle.slice_id,
            },
        )


def load_gate_evaluation_record(
    database: RelayDatabase, record_id: GateEvaluationRecordId
) -> GateEvaluationRecord | None:
    return _read(
        database,
        lambda connection: _read_one(
            connection,
            "gate_evaluation_records",
            "record_id",
            record_id,
            GateEvaluationRecord,
            {
                "record_id": "id",
                "baseline_id": "context.baseline_id",
                "slice_id": "context.lifecycle.slice_id",
            },
        ),
    )


def load_gate_evaluation_records(
    database: RelayDatabase,
) -> tuple[GateEvaluationRecord, ...]:
    def read(connection: sqlite3.Connection) -> tuple[GateEvaluationRecord, ...]:
        rows = connection.execute(
            "SELECT * FROM gate_evaluation_records ORDER BY sequence ASC, record_id ASC"
        ).fetchall()
        records: list[GateEvaluationRecord] = []
        for row in rows:
            record = _parse_payload(
                row,
                GateEvaluationRecord,
                {
                    "record_id": "id",
                    "baseline_id": "context.baseline_id",
                    "slice_id": "context.lifecycle.slice_id",
                },
            )
            records.append(record)
        return tuple(records)

    return _read(database, read)


def _insert_execution_record(connection: sqlite3.Connection, value: ExecutionRecord) -> None:
    connection.execute(
        "INSERT INTO executions(execution_id, evaluation_record_id, event_id, slice_id, "
        "resulting_lifecycle_revision, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
        (
            value.execution_id,
            value.gate_evaluation_record_id,
            value.event_id,
            value.slice_id,
            value.resulting_lifecycle_revision,
            _canonical_json(value),
        ),
    )


def _load_execution(
    connection: sqlite3.Connection, execution_id: ExecutionId
) -> ExecutionRecord | None:
    row = connection.execute(
        "SELECT * FROM executions WHERE execution_id = ?", (execution_id,)
    ).fetchone()
    if row is None:
        return None
    record = _parse_payload(
        row,
        ExecutionRecord,
        {
            "execution_id": "execution_id",
            "evaluation_record_id": "gate_evaluation_record_id",
            "event_id": "event_id",
            "slice_id": "slice_id",
            "resulting_lifecycle_revision": "resulting_lifecycle_revision",
        },
    )
    evaluation = _read_one(
        connection,
        "gate_evaluation_records",
        "record_id",
        record.gate_evaluation_record_id,
        GateEvaluationRecord,
        {
            "record_id": "id",
            "baseline_id": "context.baseline_id",
            "slice_id": "context.lifecycle.slice_id",
        },
    )
    if evaluation is None:
        raise PersistenceIntegrityError("execution references a missing evaluation record")
    matching = tuple(
        item
        for item in evaluation.evaluations
        if item.gate_id == record.selected_gate_id
        and item.gate_revision == record.selected_gate_revision
    )
    if (
        len(matching) != 1
        or matching[0].light.value != "GREEN"
        or evaluation.context.lifecycle.slice_id != record.slice_id
        or evaluation.context.baseline_id != record.baseline_id
        or evaluation.context.lifecycle.revision != record.source_lifecycle_revision
    ):
        raise PersistenceIntegrityError("execution does not match its evaluation evidence")
    event_rows = connection.execute(
        "SELECT * FROM lifecycle_events WHERE event_id = ?", (record.event_id,)
    ).fetchall()
    events = tuple(event for row in event_rows if (event := _load_event_row(row)) is not None)
    if (
        len(events) != 1
        or not isinstance(events[0], PhaseChanged)
        or events[0].slice_id != record.slice_id
    ):
        raise PersistenceIntegrityError("execution does not reference its lifecycle event")
    if events[0].resulting_revision != record.resulting_lifecycle_revision:
        raise PersistenceIntegrityError("execution revision does not match its lifecycle event")
    if (
        events[0].actor != record.actor
        or events[0].occurred_at != record.occurred_at
        or events[0].reason != record.reason
    ):
        raise PersistenceIntegrityError("execution provenance does not match its lifecycle event")
    return record


def _load_event_row(row: sqlite3.Row) -> LifecycleEvent | None:
    event_type = cast(str, row["event_type"])
    model_type = _EVENT_TYPES.get(event_type)
    if model_type is None:
        raise PersistenceIntegrityError(f"unknown persisted lifecycle event type {event_type!r}")
    event = _parse_payload(
        row,
        cast(type[LifecycleEvent], model_type),
        {
            "event_id": "event_id",
            "slice_id": "slice_id",
            "resulting_revision": "resulting_revision",
        },
    )
    if (
        type(event).__name__ != event_type
        or _datetime_text(event.occurred_at) != row["occurred_at"]
    ):
        raise PersistenceIntegrityError("lifecycle event index columns disagree with payload")
    return _EVENT_ADAPTER.validate_python(event)


def load_execution_record(
    database: RelayDatabase, execution_id: ExecutionId
) -> ExecutionRecord | None:
    return _read(database, lambda connection: _load_execution(connection, execution_id))


def load_execution_records(database: RelayDatabase) -> tuple[ExecutionRecord, ...]:
    def read(connection: sqlite3.Connection) -> tuple[ExecutionRecord, ...]:
        rows = connection.execute(
            "SELECT execution_id FROM executions "
            "ORDER BY resulting_lifecycle_revision ASC, execution_id ASC"
        ).fetchall()
        records: list[ExecutionRecord] = []
        for row in rows:
            record = _load_execution(connection, cast(str, row["execution_id"]))
            if record is None:
                raise PersistenceIntegrityError("execution disappeared during ordered read")
            records.append(record)
        return tuple(records)

    return _read(database, read)


def _require_gate(connection: sqlite3.Connection, gate: HandoverGate) -> None:
    row = connection.execute(
        "SELECT * FROM handover_gate_revisions WHERE gate_id = ? AND gate_revision = ?",
        (gate.gate_id, gate.revision),
    ).fetchone()
    if row is None:
        raise PersistenceIntegrityError("supplied gate revision is not durable")
    durable = _parse_payload(
        row,
        HandoverGate,
        {"gate_id": "gate_id", "baseline_id": "baseline_id", "slice_id": "slice_id"},
    )
    if durable.revision != row["gate_revision"] or durable != gate:
        raise PersistenceIntegrityError("supplied gate differs from its durable revision")


def _require_grant(connection: sqlite3.Connection, grant: AuthorizationGrant) -> None:
    durable = _read_one(
        connection,
        "authorization_grants",
        "authorization_id",
        grant.authorization_id,
        AuthorizationGrant,
        {"authorization_id": "authorization_id", "baseline_id": "baseline_id"},
    )
    if durable is None or durable != grant:
        raise PersistenceIntegrityError("supplied authorization is not an exact durable record")


def _require_decision(connection: sqlite3.Connection, decision: HumanGateDecision) -> None:
    row = connection.execute(
        "SELECT * FROM human_decisions WHERE decision_id = ?", (decision.decision_id,)
    ).fetchone()
    if row is None:
        raise PersistenceIntegrityError("supplied human decision is not durable")
    try:
        durable = _DECISION_ADAPTER.validate_json(cast(str, row["payload_json"]))
    except (ValidationError, ValueError, TypeError) as error:
        raise PersistenceIntegrityError("stored human decision payload is invalid") from error
    if (
        durable.decision_id != row["decision_id"]
        or durable.baseline_id != row["baseline_id"]
        or type(durable).__name__ != row["decision_type"]
        or durable != decision
    ):
        raise PersistenceIntegrityError("supplied human decision differs from durable record")


def _require_baseline(connection: sqlite3.Connection, baseline_id: BaselineId) -> None:
    if (
        _read_one(
            connection,
            "baselines",
            "id",
            baseline_id,
            Baseline,
            {"id": "id", "project_id": "project_id"},
        )
        is None
    ):
        raise PersistenceIntegrityError("context baseline is not durable")


def _require_dependency(connection: sqlite3.Connection, supplied: SliceLifecycle) -> None:
    durable, _ = _load_current_and_history(connection, supplied.slice_id)
    if durable is None:
        raise PersistenceIntegrityError("supplied dependency lifecycle is not durable")
    if durable.revision != supplied.revision:
        raise ConcurrencyConflict("dependency lifecycle projection is stale")
    if durable != supplied:
        raise PersistenceIntegrityError("dependency lifecycle differs at the same revision")


def execute_and_persist_handover(
    database: RelayDatabase,
    gates: tuple[HandoverGate, ...],
    selected_gate_id: HandoverGateId,
    context: HandoverContext,
    expected_lifecycle_revision: int,
    evaluation_record_id: GateEvaluationRecordId,
    evaluation_recorded_at: datetime,
    execution_id: ExecutionId,
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[SliceLifecycle, PhaseChanged, GateEvaluation, GateEvaluationRecord, ExecutionRecord]:
    """Recheck durable governance facts, execute, and commit all causality atomically."""

    with _write(database) as connection:
        current, history = _load_current_and_history(connection, context.lifecycle.slice_id)
        if current is None:
            raise ConcurrencyConflict("target lifecycle is not initialized")
        if current.revision != expected_lifecycle_revision:
            raise ConcurrencyConflict("expected target lifecycle revision is stale")
        if context.lifecycle.revision != current.revision:
            raise ConcurrencyConflict("supplied target lifecycle projection is stale")
        if context.lifecycle != current:
            raise PersistenceIntegrityError(
                "target lifecycle differs from durable state at same revision"
            )

        _require_baseline(connection, context.baseline_id)
        for gate in gates:
            _require_gate(connection, gate)
        for dependency in context.dependency_lifecycles:
            _require_dependency(connection, dependency)
        for grant in context.authorization_grants:
            _require_grant(connection, grant)
        for decision in context.human_decisions:
            _require_decision(connection, decision)
        for artifact_id in context.available_artifact_ids:
            if (
                _read_one(connection, "artifacts", "id", artifact_id, Artifact, {"id": "id"})
                is None
            ):
                raise PersistenceIntegrityError("available artifact ID is not durable")
        for evidence_id in context.available_evidence_ids:
            if _read_one(connection, "evidence", "id", evidence_id, Evidence, {"id": "id"}) is None:
                raise PersistenceIntegrityError("available evidence ID is not durable")

        evaluations = evaluate_handover_gates(gates, context)
        updated, event, selected_evaluation = execute_handover(
            gates,
            selected_gate_id,
            context,
            event_id,
            actor,
            occurred_at,
            reason,
        )
        expected_selected = next(
            (item for item in evaluations if item.gate_id == selected_gate_id), None
        )
        if expected_selected is None or expected_selected != selected_evaluation:
            raise PersistenceIntegrityError(
                "execution evaluation differs from complete evidence tuple"
            )

        evaluation_record = GateEvaluationRecord(
            id=evaluation_record_id,
            recorded_at=evaluation_recorded_at,
            gate_refs=tuple(
                GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision)
                for gate in sorted(gates, key=lambda item: item.gate_id)
            ),
            context=context,
            evaluations=evaluations,
        )
        try:
            replayed = replay_lifecycle((*history, event))
        except LifecycleReplayError as error:
            raise PersistenceIntegrityError("executed lifecycle event cannot replay") from error
        if replayed != updated:
            raise PersistenceIntegrityError("executed event does not produce returned lifecycle")

        execution_record = ExecutionRecord(
            execution_id=execution_id,
            gate_evaluation_record_id=evaluation_record_id,
            slice_id=context.lifecycle.slice_id,
            baseline_id=context.baseline_id,
            selected_gate_id=selected_gate_id,
            selected_gate_revision=selected_evaluation.gate_revision,
            source_lifecycle_revision=current.revision,
            resulting_lifecycle_revision=updated.revision,
            event_id=event.event_id,
            actor=actor,
            occurred_at=event.occurred_at,
            reason=event.reason,
        )

        _insert_payload(
            connection,
            "gate_evaluation_records",
            "record_id",
            evaluation_record.id,
            evaluation_record,
            {
                "baseline_id": evaluation_record.context.baseline_id,
                "slice_id": evaluation_record.context.lifecycle.slice_id,
            },
        )
        _insert_event(connection, event)
        cursor = connection.execute(
            "UPDATE lifecycle_current SET revision = ?, payload_json = ? "
            "WHERE slice_id = ? AND revision = ?",
            (
                updated.revision,
                _canonical_json(updated),
                updated.slice_id,
                expected_lifecycle_revision,
            ),
        )
        if cursor.rowcount != 1:
            raise ConcurrencyConflict("target lifecycle changed during governed execution")
        _insert_execution_record(connection, execution_record)
        return updated, event, selected_evaluation, evaluation_record, execution_record
