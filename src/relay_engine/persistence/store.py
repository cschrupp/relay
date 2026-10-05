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
    RepositoryMutationAuthorizationId,
    SliceId,
    SliceResultId,
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
from relay_engine.lifecycle.models import LifecyclePhase
from relay_engine.manual_evaluation.models import ManualEvaluationRecord, SliceResultRecord
from relay_engine.persistence.database import RelayDatabase, write_transaction
from relay_engine.persistence.errors import (
    ConcurrencyConflict,
    DatabaseUnavailable,
    PersistenceError,
    PersistenceIntegrityError,
)
from relay_engine.persistence.records import ExecutionRecord, GateEvaluationRecord
from relay_engine.repository_sync.models import RepositoryMutationAuthorization

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


def load_baseline_from_connection(
    connection: sqlite3.Connection, baseline_id: BaselineId
) -> Baseline | None:
    """Load and validate one baseline inside a caller-owned read snapshot."""

    return _read_one(
        connection,
        "baselines",
        "id",
        baseline_id,
        Baseline,
        {"id": "id", "project_id": "project_id"},
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


def load_evidence_from_connection(
    connection: sqlite3.Connection, evidence_id: EvidenceId
) -> Evidence | None:
    """Load and validate Evidence in a caller-owned transaction."""

    return _read_one(connection, "evidence", "id", evidence_id, Evidence, {"id": "id"})


def insert_evidence_from_connection(connection: sqlite3.Connection, value: Evidence) -> None:
    """Insert one Evidence record without opening a nested transaction."""

    _insert_payload(connection, "evidence", "id", value.id, value)


def insert_slice_result_from_connection(
    connection: sqlite3.Connection, value: SliceResultRecord
) -> None:
    """Append one Slice result inside a caller-owned transaction."""

    _insert_payload(
        connection,
        "slice_results",
        "result_id",
        value.result_id,
        value,
        {
            "slice_id": value.slice_id,
            "source_baseline_id": value.source_baseline_id,
            "result_baseline_id": value.result_baseline_id,
            "lifecycle_revision": value.lifecycle_revision,
            "supersedes_result_id": value.supersedes_result_id,
        },
    )


def _linear_chain[RecordT: BaseModel](
    records: tuple[RecordT, ...],
    *,
    identity: Callable[[RecordT], str],
    parent: Callable[[RecordT], str | None],
    label: str,
) -> tuple[RecordT, ...]:
    """Order an append-only supersession history by its explicit links."""

    if not records:
        return ()
    by_id = {identity(item): item for item in records}
    if len(by_id) != len(records):
        raise PersistenceIntegrityError(f"{label} identities are not unique")
    children: dict[str, str] = {}
    roots: list[RecordT] = []
    for item in records:
        parent_id = parent(item)
        if parent_id is None:
            roots.append(item)
            continue
        if parent_id not in by_id:
            raise PersistenceIntegrityError(f"{label} supersession parent is missing")
        if parent_id in children:
            raise PersistenceIntegrityError(f"{label} supersession chain forks")
        children[parent_id] = identity(item)
    if len(roots) != 1:
        raise PersistenceIntegrityError(f"{label} history has no unique chain root")
    ordered: list[RecordT] = []
    visited: set[str] = set()
    current = roots[0]
    while True:
        current_id = identity(current)
        if current_id in visited:
            raise PersistenceIntegrityError(f"{label} supersession chain is cyclic")
        visited.add(current_id)
        ordered.append(current)
        successor_id = children.get(current_id)
        if successor_id is None:
            break
        current = by_id[successor_id]
    if len(visited) != len(records):
        raise PersistenceIntegrityError(f"{label} history is disconnected or cyclic")
    return tuple(ordered)


def load_slice_result_history_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[SliceResultRecord, ...]:
    """Load typed Slice result history and validate its explicit supersession chain."""

    rows = connection.execute(
        "SELECT * FROM slice_results WHERE slice_id = ? ORDER BY sequence, result_id",
        (slice_id,),
    ).fetchall()
    records = tuple(
        _parse_payload(
            row,
            SliceResultRecord,
            {
                "result_id": "result_id",
                "slice_id": "slice_id",
                "source_baseline_id": "source_baseline_id",
                "result_baseline_id": "result_baseline_id",
                "lifecycle_revision": "lifecycle_revision",
                "supersedes_result_id": "supersedes_result_id",
            },
        )
        for row in rows
    )
    slice_value = _read_one(
        connection,
        "slices",
        "id",
        slice_id,
        Slice,
        {"id": "id", "project_id": "project_id"},
    )
    if slice_value is None:
        raise PersistenceIntegrityError("Slice result history references a missing Slice")
    for record in records:
        source = load_baseline_from_connection(connection, record.source_baseline_id)
        result = load_baseline_from_connection(connection, record.result_baseline_id)
        if source is None or result is None:
            raise PersistenceIntegrityError("Slice result references a missing Baseline")
        if (
            record.slice_id != slice_id
            or source.project_id != slice_value.project_id
            or result.project_id != slice_value.project_id
            or source.commit.repository != result.commit.repository
            or source.decision_ids != result.decision_ids
        ):
            raise PersistenceIntegrityError(
                "Slice result Baseline violates Project, repository, or Decision authority"
            )
    ordered = _linear_chain(
        records,
        identity=lambda item: item.result_id,
        parent=lambda item: item.supersedes_result_id,
        label="Slice result",
    )
    for previous, current in zip(ordered, ordered[1:], strict=False):
        if current.lifecycle_revision < previous.lifecycle_revision:
            raise PersistenceIntegrityError("Slice result lifecycle revisions regress")
        if current.recorded_at < previous.recorded_at:
            raise PersistenceIntegrityError("Slice result chronology regresses")
        if current.lifecycle_revision == previous.lifecycle_revision:
            evaluated = connection.execute(
                "SELECT 1 FROM manual_evaluations WHERE result_id = ? LIMIT 1",
                (previous.result_id,),
            ).fetchone()
            if evaluated is not None:
                raise PersistenceIntegrityError(
                    "an evaluated result was superseded in the same lifecycle attempt"
                )
    return ordered


def insert_manual_evaluation_from_connection(
    connection: sqlite3.Connection, value: ManualEvaluationRecord
) -> None:
    """Append one authored evaluation inside a caller-owned transaction."""

    _insert_payload(
        connection,
        "manual_evaluations",
        "evaluation_id",
        value.evaluation_id,
        value,
        {
            "slice_id": value.slice_id,
            "result_id": value.result_id,
            "result_baseline_id": value.result_baseline_id,
            "lifecycle_revision": value.lifecycle_revision,
            "supersedes_evaluation_id": value.supersedes_evaluation_id,
        },
    )


def load_manual_evaluation_history_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[ManualEvaluationRecord, ...]:
    """Load evaluator history, validate result/Evidence provenance, and follow its chains."""

    results = load_slice_result_history_from_connection(connection, slice_id)
    result_by_id = {item.result_id: item for item in results}
    rows = connection.execute(
        "SELECT * FROM manual_evaluations WHERE slice_id = ? ORDER BY sequence, evaluation_id",
        (slice_id,),
    ).fetchall()
    gate_revisions = {
        (gate.gate_id, gate.revision): gate
        for gate in load_handover_gates_for_slice_from_connection(connection, slice_id)
    }
    records = tuple(
        _parse_payload(
            row,
            ManualEvaluationRecord,
            {
                "evaluation_id": "evaluation_id",
                "slice_id": "slice_id",
                "result_id": "result_id",
                "result_baseline_id": "result_baseline_id",
                "lifecycle_revision": "lifecycle_revision",
                "supersedes_evaluation_id": "supersedes_evaluation_id",
            },
        )
        for row in rows
    )
    by_id = {item.evaluation_id: item for item in records}
    if len(by_id) != len(records):
        raise PersistenceIntegrityError("manual evaluation identities are not unique")
    groups: dict[SliceResultId, list[ManualEvaluationRecord]] = {}
    for record in records:
        result = result_by_id.get(record.result_id)
        if result is None:
            raise PersistenceIntegrityError("manual evaluation references a missing result")
        if (
            record.slice_id != slice_id
            or record.result_baseline_id != result.result_baseline_id
            or record.source_baseline_id != result.source_baseline_id
            or record.slice_definition_revision != result.slice_definition_revision
            or record.lifecycle_revision != result.lifecycle_revision
        ):
            raise PersistenceIntegrityError("manual evaluation does not match its result subject")
        if any(
            (gate := gate_revisions.get((reference.gate_id, reference.gate_revision))) is None
            or gate.slice_id != slice_id
            or gate.baseline_id != record.source_baseline_id
            for reference in record.gate_refs
        ):
            raise PersistenceIntegrityError(
                "manual evaluation references a missing or mismatched gate revision"
            )
        result_baseline = load_baseline_from_connection(connection, result.result_baseline_id)
        source_baseline = load_baseline_from_connection(connection, result.source_baseline_id)
        if (
            result_baseline is None
            or source_baseline is None
            or source_baseline.decision_ids != result_baseline.decision_ids
        ):
            raise PersistenceIntegrityError("manual evaluation Decision authority is inconsistent")
        for evidence_id in record.evidence_ids:
            evidence = load_evidence_from_connection(connection, evidence_id)
            if (
                evidence is None
                or evidence.source_commit != result_baseline.commit
                or evidence.recorded_at > record.evaluated_at
            ):
                raise PersistenceIntegrityError(
                    "manual evaluation Evidence is missing, postdates evaluation, or belongs "
                    "to another result commit"
                )
        if record.evaluated_at < result.recorded_at:
            raise PersistenceIntegrityError("manual evaluation predates its exact result record")
        if record.prior_gate_evaluation_record_id is not None:
            prior = _read_one(
                connection,
                "gate_evaluation_records",
                "record_id",
                record.prior_gate_evaluation_record_id,
                GateEvaluationRecord,
                {
                    "record_id": "id",
                    "baseline_id": "context.baseline_id",
                    "slice_id": "context.lifecycle.slice_id",
                },
            )
            if prior is None or prior.context.lifecycle.slice_id != slice_id:
                raise PersistenceIntegrityError(
                    "manual evaluation references a missing or cross-Slice prior observation"
                )
        groups.setdefault(record.result_id, []).append(record)

    ordered: list[ManualEvaluationRecord] = []
    for result in results:
        group = tuple(groups.get(result.result_id, ()))
        chain = _linear_chain(
            group,
            identity=lambda item: item.evaluation_id,
            parent=lambda item: item.supersedes_evaluation_id,
            label="manual evaluation",
        )
        for previous, current in zip(chain, chain[1:], strict=False):
            if (
                current.lifecycle_revision != previous.lifecycle_revision
                or current.evaluated_at < previous.evaluated_at
            ):
                raise PersistenceIntegrityError(
                    "manual evaluation supersession crosses its lifecycle or regresses in time"
                )
        for record in chain:
            parent = (
                None
                if record.supersedes_evaluation_id is None
                else by_id.get(record.supersedes_evaluation_id)
            )
            if parent is not None and parent.result_id != record.result_id:
                raise PersistenceIntegrityError("manual evaluation supersession crosses results")
            ordered.append(record)
    if len(ordered) != len(records):
        raise PersistenceIntegrityError("manual evaluation history contains an unknown result")
    return tuple(ordered)


def load_slice_1_7_subject_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[SliceResultRecord | None, ManualEvaluationRecord | None]:
    """Return the explicit result/evaluation tails for the current EVALUATING attempt."""

    lifecycle = load_current_lifecycle_from_connection(connection, slice_id)
    if lifecycle is None or lifecycle.phase is not LifecyclePhase.EVALUATING:
        return None, None
    results = load_slice_result_history_from_connection(connection, slice_id)
    if not results:
        return None, None
    result = results[-1]
    if result.lifecycle_revision > lifecycle.revision:
        raise PersistenceIntegrityError("Slice result is bound to a future lifecycle revision")
    if result.lifecycle_revision != lifecycle.revision:
        return None, None
    evaluations = tuple(
        item
        for item in load_manual_evaluation_history_from_connection(connection, slice_id)
        if item.result_id == result.result_id
    )
    return result, None if not evaluations else evaluations[-1]


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
        persist_lifecycle_change_from_connection(
            connection, expected_lifecycle_revision, updated_lifecycle, event
        )


def persist_lifecycle_change_from_connection(
    connection: sqlite3.Connection,
    expected_lifecycle_revision: int,
    updated_lifecycle: SliceLifecycle,
    event: LifecycleEvent,
) -> None:
    """Persist one lifecycle change inside a caller-owned transaction."""

    if expected_lifecycle_revision < 0:
        raise ValueError("expected lifecycle revision must be non-negative")
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


def load_current_lifecycle_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> SliceLifecycle | None:
    """Load and replay lifecycle history inside a caller-owned read snapshot."""

    return _load_current_and_history(connection, slice_id)[0]


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


def load_handover_gates_for_slice_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[HandoverGate, ...]:
    """Load every persisted gate revision for one Slice in deterministic order."""

    rows = connection.execute(
        "SELECT * FROM handover_gate_revisions WHERE slice_id = ? "
        "ORDER BY gate_id ASC, gate_revision ASC",
        (slice_id,),
    ).fetchall()
    gates: list[HandoverGate] = []
    for row in rows:
        gate = _parse_payload(
            row,
            HandoverGate,
            {"gate_id": "gate_id", "baseline_id": "baseline_id", "slice_id": "slice_id"},
        )
        if gate.revision != row["gate_revision"]:
            raise PersistenceIntegrityError("gate revision column disagrees with typed payload")
        gates.append(gate)
    return tuple(gates)


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


def insert_authorization_grant_from_connection(
    connection: sqlite3.Connection, value: AuthorizationGrant
) -> None:
    """Insert one grant without opening or committing a nested transaction."""

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


def load_authorization_grants_for_slice_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[AuthorizationGrant, ...]:
    """Load and validate all grants for one Slice in deterministic order."""

    rows = connection.execute(
        "SELECT * FROM authorization_grants ORDER BY authorization_id ASC"
    ).fetchall()
    grants: list[AuthorizationGrant] = []
    for row in rows:
        grant = _parse_payload(
            row,
            AuthorizationGrant,
            {"authorization_id": "authorization_id", "baseline_id": "baseline_id"},
        )
        if grant.slice_id == slice_id:
            grants.append(grant)
    return tuple(sorted(grants, key=lambda item: (item.granted_at, item.authorization_id)))


def insert_repository_mutation_authorization(
    database: RelayDatabase, value: RepositoryMutationAuthorization
) -> None:
    """Persist one immutable HUMAN authorization for an exact repository-sync subject."""

    with _write(database) as connection:
        _insert_payload(
            connection,
            "repository_mutation_authorizations",
            "authorization_id",
            value.authorization_id,
            value,
            {"project_id": value.project_id, "subject_digest": value.subject_digest},
        )


def load_repository_mutation_authorization(
    database: RelayDatabase, authorization_id: RepositoryMutationAuthorizationId
) -> RepositoryMutationAuthorization | None:
    """Load and integrity-check indexed identity/digest against the immutable payload."""

    return _read(
        database,
        lambda connection: _read_one(
            connection,
            "repository_mutation_authorizations",
            "authorization_id",
            authorization_id,
            RepositoryMutationAuthorization,
            {
                "authorization_id": "authorization_id",
                "project_id": "project_id",
                "subject_digest": "subject_digest",
            },
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


def insert_human_decision_from_connection(
    connection: sqlite3.Connection, value: HumanGateDecision
) -> None:
    """Insert one Human decision inside the caller-owned transaction."""

    connection.execute(
        "INSERT INTO human_decisions(decision_id, decision_type, baseline_id, payload_json) "
        "VALUES (?, ?, ?, ?)",
        (value.decision_id, type(value).__name__, value.baseline_id, _canonical_json(value)),
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


def load_human_decisions_for_slice_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[HumanGateDecision, ...]:
    """Load, type-check, and order Human decisions for one Slice."""

    rows = connection.execute("SELECT * FROM human_decisions ORDER BY decision_id ASC").fetchall()
    decisions: list[HumanGateDecision] = []
    for row in rows:
        try:
            decision = _DECISION_ADAPTER.validate_json(cast(str, row["payload_json"]))
        except (ValidationError, ValueError, TypeError) as error:
            raise PersistenceIntegrityError("stored human decision payload is invalid") from error
        if (
            decision.decision_id != row["decision_id"]
            or decision.baseline_id != row["baseline_id"]
            or type(decision).__name__ != row["decision_type"]
        ):
            raise PersistenceIntegrityError("human-decision index columns disagree with payload")
        if decision.slice_id == slice_id:
            decisions.append(decision)
    return tuple(sorted(decisions, key=lambda item: (item.occurred_at, item.decision_id)))


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


def insert_gate_evaluation_record_from_connection(
    connection: sqlite3.Connection, value: GateEvaluationRecord
) -> None:
    """Append one observation in a caller-owned write transaction."""

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


def load_gate_evaluation_records_for_slice_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[GateEvaluationRecord, ...]:
    """Load one Slice's evaluation records in durable sequence order."""

    rows = connection.execute(
        "SELECT * FROM gate_evaluation_records WHERE slice_id = ? "
        "ORDER BY sequence ASC, record_id ASC",
        (slice_id,),
    ).fetchall()
    return tuple(
        _parse_payload(
            row,
            GateEvaluationRecord,
            {
                "record_id": "id",
                "baseline_id": "context.baseline_id",
                "slice_id": "context.lifecycle.slice_id",
            },
        )
        for row in rows
    )


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


def load_execution_records_for_slice_from_connection(
    connection: sqlite3.Connection, slice_id: SliceId
) -> tuple[ExecutionRecord, ...]:
    """Load and cross-check one Slice's execution records in deterministic order."""

    rows = connection.execute(
        "SELECT execution_id FROM executions WHERE slice_id = ? "
        "ORDER BY resulting_lifecycle_revision ASC, execution_id ASC",
        (slice_id,),
    ).fetchall()
    records: list[ExecutionRecord] = []
    for row in rows:
        record = _load_execution(connection, cast(str, row["execution_id"]))
        if record is None:
            raise PersistenceIntegrityError("execution disappeared during ordered read")
        if record.slice_id != slice_id:
            raise PersistenceIntegrityError("execution indexed Slice disagrees with its payload")
        records.append(record)
    return tuple(records)


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
        return execute_and_persist_handover_from_connection(
            connection,
            gates,
            selected_gate_id,
            context,
            expected_lifecycle_revision,
            evaluation_record_id,
            evaluation_recorded_at,
            execution_id,
            event_id,
            actor,
            occurred_at,
            reason,
        )


def execute_and_persist_handover_from_connection(
    connection: sqlite3.Connection,
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
    """Execute a governed handover without opening a nested transaction."""

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
        if _read_one(connection, "artifacts", "id", artifact_id, Artifact, {"id": "id"}) is None:
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
        raise PersistenceIntegrityError("execution evaluation differs from complete evidence tuple")

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

    insert_gate_evaluation_record_from_connection(connection, evaluation_record)
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
