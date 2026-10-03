"""Deterministic board projections over one caller-owned SQLite snapshot."""

from sqlite3 import Connection

from pydantic import ValidationError

from relay_engine.board.models import (
    BoardLane,
    BoardProjection,
    DependencyProjection,
    EvaluationBasisStatus,
    GateProjection,
    ProjectBoard,
    ProjectSummary,
    SliceCard,
    SliceDetail,
)
from relay_engine.domain.ids import ProjectId, SliceId
from relay_engine.domain.models import Baseline, Slice
from relay_engine.governance.models import GateRevisionRef, HandoverGate
from relay_engine.lifecycle.models import LifecyclePhase, SliceLifecycle
from relay_engine.persistence import (
    PersistenceIntegrityError,
    RelayDatabase,
    load_baseline_from_connection,
    load_current_lifecycle_from_connection,
    load_execution_records_for_slice_from_connection,
    load_gate_evaluation_records_for_slice_from_connection,
    load_handover_gates_for_slice_from_connection,
    read_transaction,
)
from relay_engine.persistence.records import GateEvaluationRecord
from relay_engine.project_slice import (
    ProjectDefinitionSnapshot,
    SliceDefinitionSnapshot,
    SliceNotFound,
    get_project,
    get_slice,
    list_projects,
    list_slices,
)


def _lane_for(lifecycle: SliceLifecycle | None) -> BoardLane:
    if lifecycle is None:
        return BoardLane.NOT_STARTED
    if lifecycle.phase in {
        LifecyclePhase.PROPOSED,
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
    }:
        return BoardLane.SHAPING
    if lifecycle.phase is LifecyclePhase.READY:
        return BoardLane.READY
    if lifecycle.phase is LifecyclePhase.IMPLEMENTING:
        return BoardLane.DELIVERY
    if lifecycle.phase in {LifecyclePhase.EVALUATING, LifecyclePhase.REWORK}:
        return BoardLane.EVALUATION
    return BoardLane.TERMINAL


def _current_outgoing_gates(
    gates: tuple[HandoverGate, ...], lifecycle: SliceLifecycle | None
) -> tuple[HandoverGate, ...]:
    if lifecycle is None:
        return ()

    latest_by_id: dict[str, HandoverGate] = {}
    for gate in gates:
        current = latest_by_id.get(gate.gate_id)
        if current is None or gate.revision > current.revision:
            latest_by_id[gate.gate_id] = gate
    return tuple(
        sorted(
            (gate for gate in latest_by_id.values() if gate.source_phase is lifecycle.phase),
            key=lambda gate: gate.gate_id,
        )
    )


def _check_duplicate_evaluation_outputs(
    records: tuple[GateEvaluationRecord, ...],
) -> None:
    for index, record in enumerate(records):
        for prior in records[:index]:
            same_full_basis = (
                prior.gate_refs == record.gate_refs and prior.context == record.context
            )
            if same_full_basis and prior.evaluations != record.evaluations:
                raise PersistenceIntegrityError(
                    "duplicate full-basis evaluation records have conflicting outputs"
                )


def _evaluation_basis_status(
    slice_value: Slice,
    lifecycle: SliceLifecycle | None,
    gates: tuple[HandoverGate, ...],
    latest: GateEvaluationRecord | None,
) -> EvaluationBasisStatus:
    if lifecycle is None or not gates:
        return EvaluationBasisStatus.NOT_APPLICABLE
    if latest is None:
        return EvaluationBasisStatus.NOT_EVALUATED

    expected_refs = tuple(
        GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision) for gate in gates
    )
    expected_baseline_ids = {gate.baseline_id for gate in gates}
    if len(expected_baseline_ids) != 1:
        raise PersistenceIntegrityError(
            "current outgoing gates identify different durable baselines"
        )

    context = latest.context
    if (
        context.lifecycle.slice_id != slice_value.id
        or context.lifecycle != lifecycle
        or latest.gate_refs != expected_refs
        or context.baseline_id != next(iter(expected_baseline_ids))
    ):
        return EvaluationBasisStatus.STALE_DURABLE_BASIS
    return EvaluationBasisStatus.MATCHING_DURABLE_BASIS


def _checked_baseline(connection: Connection, baseline_id: str, project_id: ProjectId) -> Baseline:
    baseline = load_baseline_from_connection(connection, baseline_id)
    if baseline is None:
        raise PersistenceIntegrityError("gate or evaluation references a missing baseline")
    if baseline.project_id != project_id:
        raise PersistenceIntegrityError("gate baseline belongs to a different Project")
    return baseline


def _load_slice_basis(
    connection: Connection, project_id: ProjectId, slice_value: Slice
) -> tuple[
    SliceLifecycle | None,
    tuple[HandoverGate, ...],
    tuple[GateEvaluationRecord, ...],
    GateEvaluationRecord | None,
    EvaluationBasisStatus,
    Baseline | None,
    Baseline | None,
]:
    lifecycle = load_current_lifecycle_from_connection(connection, slice_value.id)
    gate_history = load_handover_gates_for_slice_from_connection(connection, slice_value.id)
    gates = _current_outgoing_gates(gate_history, lifecycle)
    evaluation_records = load_gate_evaluation_records_for_slice_from_connection(
        connection, slice_value.id
    )
    _check_duplicate_evaluation_outputs(evaluation_records)
    latest = evaluation_records[-1] if evaluation_records else None
    status = _evaluation_basis_status(slice_value, lifecycle, gates, latest)

    current_baseline: Baseline | None = None
    if gates:
        baseline_ids = {gate.baseline_id for gate in gates}
        if len(baseline_ids) != 1:
            raise PersistenceIntegrityError(
                "current outgoing gates identify different durable baselines"
            )
        current_baseline = _checked_baseline(connection, next(iter(baseline_ids)), project_id)

    evaluation_baseline = (
        None
        if latest is None
        else _checked_baseline(connection, latest.context.baseline_id, project_id)
    )
    return (
        lifecycle,
        gates,
        evaluation_records,
        latest,
        status,
        current_baseline,
        evaluation_baseline,
    )


def _gate_projections(
    gates: tuple[HandoverGate, ...],
    latest: GateEvaluationRecord | None,
    status: EvaluationBasisStatus,
) -> tuple[GateProjection, ...]:
    evaluations = (
        {evaluation.gate_id: evaluation for evaluation in latest.evaluations}
        if latest is not None and status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS
        else {}
    )
    projections: list[GateProjection] = []
    for gate in gates:
        evaluation = evaluations.get(gate.gate_id)
        if status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS and evaluation is None:
            raise PersistenceIntegrityError(
                "matching evaluation is missing a current outgoing gate result"
            )
        if evaluation is not None and evaluation.gate_revision != gate.revision:
            raise PersistenceIntegrityError(
                "matching evaluation contains a different current gate revision"
            )
        projections.append(
            GateProjection(
                gate_id=gate.gate_id,
                gate_revision=gate.revision,
                target_phase=gate.target_phase,
                policy=gate.policy,
                hard_stop=gate.hard_stop,
                authorization_required=gate.authorization_required,
                baseline_id=gate.baseline_id,
                evaluation_light=None if evaluation is None else evaluation.light,
                evaluation_reasons=() if evaluation is None else evaluation.reasons,
                evaluation_basis_status=status,
            )
        )
    return tuple(projections)


def _verify_related_slice_project(
    database: RelayDatabase,
    project_id: ProjectId,
    related_id: SliceId,
    known: dict[SliceId, SliceDefinitionSnapshot],
) -> SliceDefinitionSnapshot | None:
    snapshot = known.get(related_id)
    if snapshot is None:
        try:
            snapshot = get_slice(database, related_id)
        except SliceNotFound:
            return None
    if snapshot.value.project_id != project_id:
        raise PersistenceIntegrityError("Slice relationship crosses Project boundaries")
    if related_id not in known:
        raise PersistenceIntegrityError("Slice relationship points outside current Project rows")
    return snapshot


def _dependency_projection(
    database: RelayDatabase,
    connection: Connection,
    project_id: ProjectId,
    related_id: SliceId,
    known: dict[SliceId, SliceDefinitionSnapshot],
    lifecycles: dict[SliceId, SliceLifecycle | None],
) -> DependencyProjection:
    snapshot = _verify_related_slice_project(database, project_id, related_id, known)
    lifecycle = lifecycles.get(related_id)
    if lifecycle is None and snapshot is not None:
        lifecycle = load_current_lifecycle_from_connection(connection, related_id)
        lifecycles[related_id] = lifecycle
    return DependencyProjection(
        slice_id=related_id,
        title=None if snapshot is None else snapshot.value.title,
        lifecycle_phase=None if lifecycle is None else lifecycle.phase,
        lifecycle_validity=None if lifecycle is None else lifecycle.validity,
    )


def _ordered_cards(cards: list[SliceCard]) -> tuple[SliceCard, ...]:
    lane_order = {lane: index for index, lane in enumerate(BoardLane)}
    return tuple(
        sorted(
            cards, key=lambda card: (lane_order[card.lane], card.title.casefold(), card.slice_id)
        )
    )


def project_index(database: RelayDatabase) -> BoardProjection:
    """Project every current Project in one verified SQLite read snapshot."""

    try:
        with read_transaction(database):
            snapshots = list_projects(database)
            projects = tuple(
                ProjectSummary(
                    project=snapshot.value,
                    definition_revision=snapshot.definition_revision,
                    slice_count=len(list_slices(database, snapshot.value.id)),
                )
                for snapshot in snapshots
            )
            return BoardProjection(projects=projects)
    except ValidationError as error:
        raise PersistenceIntegrityError("Project index projection is invalid") from error


def project_board(database: RelayDatabase, project_id: ProjectId) -> ProjectBoard:
    """Project all current Slices and required evidence from one read snapshot."""

    try:
        with read_transaction(database) as connection:
            project_snapshot = get_project(database, project_id)
            slice_snapshots = list_slices(database, project_id)
            known = {snapshot.value.id: snapshot for snapshot in slice_snapshots}
            lifecycles = {
                slice_id: load_current_lifecycle_from_connection(connection, slice_id)
                for slice_id in known
            }
            cards: list[SliceCard] = []
            for snapshot in slice_snapshots:
                value = snapshot.value
                (
                    lifecycle,
                    gates,
                    _records,
                    latest,
                    status,
                    _current_baseline,
                    _evaluation_baseline,
                ) = _load_slice_basis(connection, project_id, value)
                lifecycles[value.id] = lifecycle
                if value.parent_slice_id is not None:
                    _dependency_projection(
                        database,
                        connection,
                        project_id,
                        value.parent_slice_id,
                        known,
                        lifecycles,
                    )
                dependencies = tuple(
                    _dependency_projection(
                        database,
                        connection,
                        project_id,
                        dependency_id,
                        known,
                        lifecycles,
                    )
                    for dependency_id in value.dependency_ids
                )
                cards.append(
                    SliceCard(
                        slice_id=value.id,
                        title=value.title,
                        definition_revision=snapshot.definition_revision,
                        parent_slice_id=value.parent_slice_id,
                        dependency_ids=value.dependency_ids,
                        lane=_lane_for(lifecycle),
                        lifecycle=lifecycle,
                        dependencies=dependencies,
                        outgoing_gates=_gate_projections(gates, latest, status),
                        latest_evaluation_record_id=None if latest is None else latest.id,
                        latest_evaluation_recorded_at=None
                        if latest is None
                        else latest.recorded_at,
                        evaluation_basis_status=status,
                    )
                )
            return ProjectBoard(
                project=project_snapshot.value,
                project_definition_revision=project_snapshot.definition_revision,
                lanes=tuple(BoardLane),
                cards=_ordered_cards(cards),
            )
    except ValidationError as error:
        raise PersistenceIntegrityError("Project board projection is invalid") from error


def slice_detail(database: RelayDatabase, project_id: ProjectId, slice_id: SliceId) -> SliceDetail:
    """Project one Slice's full durable provenance in one read snapshot."""

    try:
        with read_transaction(database) as connection:
            project_snapshot: ProjectDefinitionSnapshot = get_project(database, project_id)
            slice_snapshot: SliceDefinitionSnapshot = get_slice(database, slice_id)
            if slice_snapshot.value.project_id != project_id:
                raise SliceNotFound(slice_id)

            all_slices = list_slices(database, project_id)
            known = {snapshot.value.id: snapshot for snapshot in all_slices}
            lifecycle = load_current_lifecycle_from_connection(connection, slice_id)
            lifecycles = {slice_id: lifecycle}
            (
                _lifecycle,
                gates,
                _records,
                latest,
                status,
                current_baseline,
                evaluation_baseline,
            ) = _load_slice_basis(connection, project_id, slice_snapshot.value)

            parent = (
                None
                if slice_snapshot.value.parent_slice_id is None
                else _dependency_projection(
                    database,
                    connection,
                    project_id,
                    slice_snapshot.value.parent_slice_id,
                    known,
                    lifecycles,
                )
            )
            dependencies = tuple(
                _dependency_projection(
                    database,
                    connection,
                    project_id,
                    dependency_id,
                    known,
                    lifecycles,
                )
                for dependency_id in slice_snapshot.value.dependency_ids
            )
            child_snapshots = sorted(
                (snapshot for snapshot in all_slices if snapshot.value.parent_slice_id == slice_id),
                key=lambda snapshot: (snapshot.value.title.casefold(), snapshot.value.id),
            )
            children = tuple(
                _dependency_projection(
                    database,
                    connection,
                    project_id,
                    snapshot.value.id,
                    known,
                    lifecycles,
                )
                for snapshot in child_snapshots
            )
            executions = load_execution_records_for_slice_from_connection(connection, slice_id)
            return SliceDetail(
                project=project_snapshot.value,
                project_definition_revision=project_snapshot.definition_revision,
                slice_definition=slice_snapshot,
                lifecycle=lifecycle,
                parent=parent,
                children=children,
                dependencies=dependencies,
                outgoing_gate_definitions=gates,
                outgoing_gates=_gate_projections(gates, latest, status),
                latest_evaluation_observation=latest,
                evaluation_basis_status=status,
                baseline=current_baseline,
                evaluation_baseline=evaluation_baseline,
                relevant_execution_records=executions,
            )
    except ValidationError as error:
        raise PersistenceIntegrityError("Slice detail projection is invalid") from error


__all__ = ["project_board", "project_index", "slice_detail"]
