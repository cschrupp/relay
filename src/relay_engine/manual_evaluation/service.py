"""Deterministic Slice 1.7 commands over durable Relay state."""

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime

from pydantic import ValidationError

from relay_engine.domain.ids import (
    BaselineId,
    EventId,
    EvidenceId,
    ExecutionId,
    GateEvaluationRecordId,
    HandoverGateId,
    HumanDecisionId,
    ManualEvaluationId,
    SliceId,
    SliceResultId,
)
from relay_engine.domain.models import Baseline, Evidence, Slice
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.governance import evaluate_handover_gates
from relay_engine.governance.models import (
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HumanApprovalDecision,
    HumanApprovalValue,
    HumanChoiceDecision,
    QualityCheckResult,
    RiskStatus,
    ToolchainChangeStatus,
    TrafficLight,
)
from relay_engine.human_control.models import HumanActionBasis, HumanApprovalIdentity
from relay_engine.human_control.service import (
    HumanControlSnapshot,
    basis_if_current,
    current_gates,
    gate_refs_for_gates,
    load_human_control_snapshot,
    project_authorizations,
    project_decisions,
    record_successor_observation,
    successor_context,
    timestamp_at_or_after,
    validate_human_action_basis,
)
from relay_engine.integrations.github.models import GitHubRepositoryAccessSelection
from relay_engine.lifecycle import PhaseChanged
from relay_engine.lifecycle.models import LifecyclePhase, LifecycleValidity, SliceLifecycle
from relay_engine.manual_evaluation.errors import (
    ManualEvaluationConflict,
    ManualEvaluationForbidden,
    ManualEvaluationInvalid,
    ManualEvaluationNotAvailable,
    ManualEvaluationStale,
)
from relay_engine.manual_evaluation.models import (
    AcceptedSliceResult,
    DevelopmentMemoryProjection,
    EvaluationEvidenceSubmission,
    ManualEvaluationActionBasis,
    ManualEvaluationActionKind,
    ManualEvaluationProjection,
    ManualEvaluationRecord,
    SliceResultRecord,
)
from relay_engine.persistence import (
    ConcurrencyConflict,
    GateEvaluationRecord,
    PersistenceIntegrityError,
    RelayDatabase,
    execute_and_persist_handover_from_connection,
    insert_evidence_from_connection,
    insert_human_decision_from_connection,
    insert_manual_evaluation_from_connection,
    insert_slice_result_from_connection,
    load_authorization_grants_for_slice_from_connection,
    load_baseline_from_connection,
    load_current_lifecycle_from_connection,
    load_evidence_from_connection,
    load_execution_records_for_slice_from_connection,
    load_gate_evaluation_records_for_slice_from_connection,
    load_handover_gate,
    load_handover_gates_for_slice_from_connection,
    load_human_decisions_for_slice_from_connection,
    load_lifecycle_events,
    load_manual_evaluation_history_from_connection,
    load_slice_1_7_subject_from_connection,
    load_slice_result_history_from_connection,
    read_transaction,
)
from relay_engine.persistence.database import write_transaction
from relay_engine.persistence.records import ExecutionRecord
from relay_engine.project_slice import get_slice, list_slices
from relay_engine.repository_baseline.models import (
    RepositoryRevisionKind,
    RepositoryRevisionSelector,
    ResolvedBaselineResult,
)
from relay_engine.repository_baseline.service import RepositoryBaselineService


@contextmanager
def _manual_write(database: RelayDatabase):
    try:
        with write_transaction(database) as connection:
            yield connection
    except ConcurrencyConflict as error:
        raise ManualEvaluationConflict("durable Slice 1.7 state changed concurrently") from error
    except sqlite3.IntegrityError as error:
        raise PersistenceIntegrityError(
            "Slice 1.7 mutation violated durable uniqueness or reference integrity"
        ) from error


def _require_human(actor: ActorRef, role: str) -> None:
    if actor.kind is not ActorKind.HUMAN:
        raise ManualEvaluationForbidden(f"{role} requires a server-bound HUMAN actor")


def _common_baseline(gates: tuple[HandoverGate, ...]) -> BaselineId:
    if not gates:
        raise ManualEvaluationNotAvailable("Slice has no current outgoing gates")
    baseline_ids = {item.baseline_id for item in gates}
    if len(baseline_ids) != 1:
        raise PersistenceIntegrityError("current outgoing gates identify mixed Baselines")
    return next(iter(baseline_ids))


def _check_evaluating(
    lifecycle: SliceLifecycle | None,
    expected_revision: int,
) -> SliceLifecycle:
    if lifecycle is None:
        raise ManualEvaluationNotAvailable("Slice lifecycle is not initialized")
    if lifecycle.revision != expected_revision:
        raise ManualEvaluationStale("Slice lifecycle revision changed")
    if lifecycle.phase is not LifecyclePhase.EVALUATING:
        raise ManualEvaluationNotAvailable("Slice must be in EVALUATING")
    return lifecycle


def _current_attempt_result(
    connection: sqlite3.Connection,
    slice_id: SliceId,
    lifecycle: SliceLifecycle,
) -> tuple[tuple[SliceResultRecord, ...], SliceResultRecord | None, ManualEvaluationRecord | None]:
    history = load_slice_result_history_from_connection(connection, slice_id)
    current = None
    evaluation = None
    if history and history[-1].lifecycle_revision == lifecycle.revision:
        current = history[-1]
        evaluation_history = load_manual_evaluation_history_from_connection(connection, slice_id)
        current_evaluations = tuple(
            item for item in evaluation_history if item.result_id == current.result_id
        )
        evaluation = None if not current_evaluations else current_evaluations[-1]
    return history, current, evaluation


def _verified_baseline(
    connection: sqlite3.Connection,
    baseline_id: BaselineId,
    *,
    project_id: str,
    repository: object | None = None,
) -> Baseline:
    baseline = load_baseline_from_connection(connection, baseline_id)
    if baseline is None:
        raise PersistenceIntegrityError("Slice 1.7 references a missing Baseline")
    if baseline.project_id != project_id:
        raise PersistenceIntegrityError("Slice 1.7 Baseline belongs to another Project")
    if repository is not None and baseline.commit.repository != repository:
        raise PersistenceIntegrityError("Slice 1.7 Baseline belongs to another repository")
    return baseline


def _validate_result_authority(
    connection: sqlite3.Connection,
    record: SliceResultRecord,
    slice_value: Slice,
) -> tuple[Baseline, Baseline]:
    source = _verified_baseline(
        connection, record.source_baseline_id, project_id=slice_value.project_id
    )
    result = _verified_baseline(
        connection,
        record.result_baseline_id,
        project_id=slice_value.project_id,
        repository=source.commit.repository,
    )
    if source.decision_ids != result.decision_ids:
        raise PersistenceIntegrityError("result Baseline Decision IDs differ from source authority")
    if result.commit.repository != source.commit.repository:
        raise PersistenceIntegrityError("result commit belongs to another repository")
    return source, result


def _basis_matches_gate_observation(
    basis: HumanActionBasis, observation: GateEvaluationRecord
) -> bool:
    """Prove a submitted form basis identifies one exact durable observation."""

    context = observation.context
    approvals = tuple(
        HumanApprovalIdentity(gate_id=item.gate_id, decision_id=item.decision_id)
        for item in context.human_decisions
        if isinstance(item, HumanApprovalDecision)
    )
    choice = next(
        (item for item in context.human_decisions if isinstance(item, HumanChoiceDecision)), None
    )
    expected = HumanActionBasis(
        evaluation_record_id=observation.id,
        slice_id=context.lifecycle.slice_id,
        baseline_id=context.baseline_id,
        lifecycle_revision=context.lifecycle.revision,
        governance_revision=context.governance_revision,
        gate_refs=observation.gate_refs,
        current_approval_decision_ids=approvals,
        current_choice_decision_id=None if choice is None else choice.decision_id,
        current_result_id=context.result_id,
        current_result_baseline_id=context.result_baseline_id,
        current_manual_evaluation_id=context.manual_evaluation_id,
    )
    return basis == expected


def _observations_are_adjacent(
    observations: tuple[GateEvaluationRecord, ...],
    predecessor: GateEvaluationRecord,
    successor: GateEvaluationRecord,
) -> bool:
    predecessor_index = next(
        (index for index, item in enumerate(observations) if item.id == predecessor.id), None
    )
    successor_index = next(
        (index for index, item in enumerate(observations) if item.id == successor.id), None
    )
    return (
        predecessor_index is not None
        and successor_index is not None
        and successor_index == predecessor_index + 1
    )


def attach_result(
    database: RelayDatabase,
    slice_id: SliceId,
    *,
    repository_baseline_service: RepositoryBaselineService,
    selection: GitHubRepositoryAccessSelection,
    selector: RepositoryRevisionSelector,
    result_id: SliceResultId,
    result_baseline_id: BaselineId,
    expected_lifecycle_revision: int,
    expected_slice_definition_revision: int,
    expected_current_result_id: SliceResultId | None,
    recorded_by: ActorRef,
    recorded_at: datetime,
    reason: str,
) -> SliceResultRecord:
    """Verify an exact result Baseline, then atomically append its Slice subject."""

    _require_human(recorded_by, "result attachment")
    if not reason.strip():
        raise ManualEvaluationInvalid("result attachment reason must be nonblank")
    if recorded_at.tzinfo is None or recorded_at.utcoffset() is None:
        raise ManualEvaluationInvalid("recorded_at must be timezone-aware")
    recorded_at = recorded_at.astimezone(UTC)

    with read_transaction(database) as connection:
        snapshot = get_slice(database, slice_id)
        if snapshot.definition_revision != expected_slice_definition_revision:
            raise ManualEvaluationStale("Slice definition revision changed")
        lifecycle = _check_evaluating(
            load_current_lifecycle_from_connection(connection, slice_id),
            expected_lifecycle_revision,
        )
        gates = current_gates(
            load_handover_gates_for_slice_from_connection(connection, slice_id), lifecycle
        )
        source_id = _common_baseline(gates)
        source_baseline = _verified_baseline(
            connection,
            source_id,
            project_id=snapshot.value.project_id,
            repository=selection.repository,
        )
        history, current, current_evaluation = _current_attempt_result(
            connection, slice_id, lifecycle
        )
        existing = next((item for item in history if item.result_id == result_id), None)
        if existing is not None:
            if selection.project_id != snapshot.value.project_id:
                raise ManualEvaluationConflict("result retry selection changed Project")
            if selection.repository != source_baseline.commit.repository:
                raise ManualEvaluationConflict("result retry selection changed repository")
            if current is None or current.result_id != existing.result_id:
                raise ManualEvaluationConflict("result identity is no longer the current result")
            if existing != SliceResultRecord(
                result_id=result_id,
                slice_id=slice_id,
                slice_definition_revision=expected_slice_definition_revision,
                source_baseline_id=source_id,
                result_baseline_id=result_baseline_id,
                lifecycle_revision=expected_lifecycle_revision,
                supersedes_result_id=expected_current_result_id,
                recorded_by=recorded_by,
                recorded_at=recorded_at,
                reason=reason,
            ):
                raise ManualEvaluationConflict("result ID is bound to different command content")
            _, existing_baseline = _validate_result_authority(connection, existing, snapshot.value)
            if existing_baseline.id != result_baseline_id or (
                selector.kind is RepositoryRevisionKind.COMMIT_SHA
                and selector.value != existing_baseline.commit.sha
            ):
                raise ManualEvaluationConflict("result retry does not match its exact Baseline")
            return existing

        actual_current_id = None if current is None else current.result_id
        if actual_current_id != expected_current_result_id:
            raise ManualEvaluationStale("current result changed since attachment form was rendered")
        if current_evaluation is not None:
            raise ManualEvaluationNotAvailable(
                "an evaluated result can only be replaced after governed REWORK"
            )
        if selection.project_id != snapshot.value.project_id:
            raise ManualEvaluationInvalid("GitHub selection belongs to another Project")
        if selection.repository != source_baseline.commit.repository:
            raise ManualEvaluationInvalid("GitHub selection differs from the source Baseline")

    resolved: ResolvedBaselineResult = (
        repository_baseline_service.resolve_and_persist_github_baseline(
            selection=selection,
            selector=selector,
            baseline_id=result_baseline_id,
            decision_ids=source_baseline.decision_ids,
            observed_at=recorded_at,
        )
    )
    if resolved.project_id != selection.project_id or resolved.repository != selection.repository:
        raise PersistenceIntegrityError("verified result Baseline identity differs from selection")

    with _manual_write(database) as connection:
        snapshot = get_slice(database, slice_id)
        lifecycle = _check_evaluating(
            load_current_lifecycle_from_connection(connection, slice_id),
            expected_lifecycle_revision,
        )
        if snapshot.definition_revision != expected_slice_definition_revision:
            raise ManualEvaluationStale("Slice definition changed during repository verification")
        gates = current_gates(
            load_handover_gates_for_slice_from_connection(connection, slice_id), lifecycle
        )
        source_id = _common_baseline(gates)
        if source_id != source_baseline.id:
            raise ManualEvaluationStale("source authority Baseline changed during verification")
        source, result = _validate_result_authority(
            connection,
            SliceResultRecord(
                result_id=result_id,
                slice_id=slice_id,
                slice_definition_revision=snapshot.definition_revision,
                source_baseline_id=source_id,
                result_baseline_id=resolved.baseline_id,
                lifecycle_revision=lifecycle.revision,
                recorded_by=recorded_by,
                recorded_at=recorded_at,
                reason=reason,
            ),
            snapshot.value,
        )
        if source.decision_ids != result.decision_ids:
            raise PersistenceIntegrityError("result Baseline Decision authority drifted")
        history, current, current_evaluation = _current_attempt_result(
            connection, slice_id, lifecycle
        )
        actual_current_id = None if current is None else current.result_id
        if actual_current_id != expected_current_result_id:
            raise ManualEvaluationStale("current result changed during repository verification")
        if current_evaluation is not None:
            raise ManualEvaluationNotAvailable(
                "an evaluated result can only be replaced after governed REWORK"
            )
        if history and recorded_at < history[-1].recorded_at:
            raise ManualEvaluationInvalid("result chronology may not regress")
        record = SliceResultRecord(
            result_id=result_id,
            slice_id=slice_id,
            slice_definition_revision=snapshot.definition_revision,
            source_baseline_id=source_id,
            result_baseline_id=result.id,
            lifecycle_revision=lifecycle.revision,
            supersedes_result_id=None if not history else history[-1].result_id,
            recorded_by=recorded_by,
            recorded_at=recorded_at,
            reason=reason,
        )
        insert_slice_result_from_connection(connection, record)
        return record


def _fresh_dependencies(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    slice_value: Slice,
    gates: tuple[HandoverGate, ...],
) -> tuple[SliceLifecycle, ...]:
    required = set(slice_value.dependency_ids)
    for gate in gates:
        required.update(gate.required_dependency_slice_ids)
    known = {item.value.id for item in list_slices(database, slice_value.project_id)}
    projections: list[SliceLifecycle] = []
    for dependency_id in sorted(required):
        if dependency_id not in known:
            continue
        lifecycle = load_current_lifecycle_from_connection(connection, dependency_id)
        if lifecycle is not None:
            projections.append(lifecycle)
    return tuple(projections)


def _successor_evaluation_context(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    *,
    slice_value: Slice,
    lifecycle: SliceLifecycle,
    gates: tuple[HandoverGate, ...],
    source_baseline: Baseline,
    result_baseline: Baseline,
    evaluation: ManualEvaluationRecord,
    governance_revision: int,
) -> HandoverContext:
    grants = load_authorization_grants_for_slice_from_connection(connection, slice_value.id)
    decisions = load_human_decisions_for_slice_from_connection(connection, slice_value.id)
    return HandoverContext(
        baseline_id=source_baseline.id,
        governance_revision=governance_revision,
        lifecycle=lifecycle,
        available_artifact_ids=result_baseline.artifact_ids,
        available_evidence_ids=evaluation.evidence_ids,
        dependency_lifecycles=_fresh_dependencies(database, connection, slice_value, gates),
        evaluation_outcome=evaluation.outcome,
        result_id=evaluation.result_id,
        result_baseline_id=evaluation.result_baseline_id,
        manual_evaluation_id=evaluation.evaluation_id,
        authorization_grants=project_authorizations(grants, gates),
        human_decisions=project_decisions(decisions, gates),
        quality_checks=evaluation.quality_checks,
        change_surface_status=evaluation.change_surface_status,
        risk_status=evaluation.risk_status,
        toolchain_change_status=evaluation.toolchain_change_status,
    )


def record_manual_evaluation(
    database: RelayDatabase,
    slice_id: SliceId,
    *,
    evaluation_id: ManualEvaluationId,
    evaluator: ActorRef,
    evaluated_at: datetime,
    outcome: EvaluationOutcome,
    existing_evidence_ids: tuple[EvidenceId, ...],
    evidence_submissions: tuple[EvaluationEvidenceSubmission, ...],
    quality_checks: tuple[QualityCheckResult, ...],
    change_surface_status: ChangeSurfaceStatus,
    risk_status: RiskStatus,
    toolchain_change_status: ToolchainChangeStatus,
    findings: tuple[str, ...],
    summary: str,
    expected_lifecycle_revision: int,
    expected_slice_definition_revision: int,
    expected_result_id: SliceResultId,
    expected_current_evaluation_id: ManualEvaluationId | None,
    expected_latest_gate_evaluation_record_id: GateEvaluationRecordId | None,
    expected_gate_refs: tuple[GateRevisionRef, ...],
    successor_gate_evaluation_record_id: GateEvaluationRecordId,
    successor_gate_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    """Append Human Evidence, an authored evaluation, and its complete gate observation."""

    _require_human(evaluator, "manual evaluation")
    if not summary.strip():
        raise ManualEvaluationInvalid("manual evaluation summary must be nonblank")
    if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
        raise ManualEvaluationInvalid("evaluated_at must be timezone-aware")
    if (
        successor_gate_evaluation_recorded_at.tzinfo is None
        or successor_gate_evaluation_recorded_at.utcoffset() is None
    ):
        raise ManualEvaluationInvalid("successor observation time must be timezone-aware")
    evaluated_at = evaluated_at.astimezone(UTC)
    successor_gate_evaluation_recorded_at = successor_gate_evaluation_recorded_at.astimezone(UTC)

    with _manual_write(database) as connection:
        snapshot = get_slice(database, slice_id)
        lifecycle = _check_evaluating(
            load_current_lifecycle_from_connection(connection, slice_id),
            expected_lifecycle_revision,
        )
        if snapshot.definition_revision != expected_slice_definition_revision:
            raise ManualEvaluationStale("Slice definition revision changed")
        gates = current_gates(
            load_handover_gates_for_slice_from_connection(connection, slice_id), lifecycle
        )
        expected_refs = gate_refs_for_gates(gates)
        if expected_refs != expected_gate_refs:
            raise ManualEvaluationStale("outgoing gate revisions changed")
        source_id = _common_baseline(gates)
        source_baseline = _verified_baseline(
            connection, source_id, project_id=snapshot.value.project_id
        )
        _, current_result, current_evaluation = _current_attempt_result(
            connection, slice_id, lifecycle
        )
        if current_result is None or current_result.result_id != expected_result_id:
            raise ManualEvaluationStale("current result changed or is unavailable")
        if current_result.source_baseline_id != source_id:
            raise PersistenceIntegrityError(
                "current result source Baseline differs from current gates"
            )
        _, result_baseline = _validate_result_authority(connection, current_result, snapshot.value)
        if current_result.slice_definition_revision != snapshot.definition_revision:
            raise ManualEvaluationStale("current result was attached to another Slice definition")
        actual_eval_id = None if current_evaluation is None else current_evaluation.evaluation_id
        if actual_eval_id != expected_current_evaluation_id:
            raise ManualEvaluationStale("current manual evaluation changed")
        records = load_gate_evaluation_records_for_slice_from_connection(connection, slice_id)
        latest = None if not records else records[-1]
        actual_latest_id = None if latest is None else latest.id
        if actual_latest_id != expected_latest_gate_evaluation_record_id:
            raise ManualEvaluationStale("latest durable gate observation changed")
        if current_evaluation is not None and (
            latest is None
            or latest.context.result_id != current_result.result_id
            or latest.context.result_baseline_id != current_result.result_baseline_id
            or latest.context.manual_evaluation_id != current_evaluation.evaluation_id
        ):
            raise ManualEvaluationStale(
                "current evaluation has no matching latest gate observation"
            )
        if not existing_evidence_ids and not evidence_submissions:
            raise ManualEvaluationInvalid("manual evaluation requires at least one Evidence item")
        submitted_ids = (
            *existing_evidence_ids,
            *(item.evidence_id for item in evidence_submissions),
        )
        if len(submitted_ids) != len(set(submitted_ids)):
            raise ManualEvaluationInvalid("Evidence IDs must be unique")

        evidence_by_id: dict[EvidenceId, Evidence] = {}
        for evidence_id in existing_evidence_ids:
            evidence = load_evidence_from_connection(connection, evidence_id)
            if evidence is None:
                raise ManualEvaluationInvalid("referenced Evidence does not exist")
            if evidence.source_commit != result_baseline.commit:
                raise ManualEvaluationInvalid(
                    "referenced Evidence belongs to another result commit"
                )
            evidence_by_id[evidence_id] = evidence

        new_evidence: list[Evidence] = []
        for submission in evidence_submissions:
            evidence = Evidence(
                id=submission.evidence_id,
                claim=submission.claim,
                recorded_by=evaluator,
                recorded_at=submission.recorded_at,
                source_commit=result_baseline.commit,
            )
            if (
                evidence.recorded_at < current_result.recorded_at
                or evidence.recorded_at > evaluated_at
            ):
                raise ManualEvaluationInvalid(
                    "Evidence chronology must be result ≤ evidence ≤ evaluation"
                )
            existing = load_evidence_from_connection(connection, evidence.id)
            if existing is not None:
                if existing != evidence:
                    raise ManualEvaluationConflict(
                        "Evidence ID already has conflicting durable content"
                    )
            else:
                new_evidence.append(evidence)
            evidence_by_id[evidence.id] = evidence

        if any(item.recorded_at > evaluated_at for item in evidence_by_id.values()):
            raise ManualEvaluationInvalid("Evidence may not postdate its manual evaluation")
        if evaluated_at < current_result.recorded_at:
            raise ManualEvaluationInvalid("manual evaluation may not predate its result")
        if current_evaluation is not None and evaluated_at < current_evaluation.evaluated_at:
            raise ManualEvaluationInvalid("manual evaluation chronology may not regress")
        if latest is not None and evaluated_at < latest.recorded_at:
            raise ManualEvaluationInvalid(
                "manual evaluation may not predate the latest observation"
            )
        if successor_gate_evaluation_recorded_at < evaluated_at:
            raise ManualEvaluationInvalid("successor observation may not predate manual evaluation")

        prior_governance_revision = max(
            (item.context.governance_revision for item in records), default=0
        )
        record = ManualEvaluationRecord(
            evaluation_id=evaluation_id,
            slice_id=slice_id,
            result_id=current_result.result_id,
            result_baseline_id=current_result.result_baseline_id,
            source_baseline_id=current_result.source_baseline_id,
            slice_definition_revision=snapshot.definition_revision,
            lifecycle_revision=lifecycle.revision,
            gate_refs=expected_refs,
            prior_gate_evaluation_record_id=actual_latest_id,
            supersedes_evaluation_id=actual_eval_id,
            evaluator=evaluator,
            evaluated_at=evaluated_at,
            outcome=outcome,
            evidence_ids=tuple(sorted(evidence_by_id)),
            quality_checks=quality_checks,
            change_surface_status=change_surface_status,
            risk_status=risk_status,
            toolchain_change_status=toolchain_change_status,
            findings=findings,
            summary=summary,
        )
        prior_by_id = {
            item.evaluation_id: item
            for item in load_manual_evaluation_history_from_connection(connection, slice_id)
        }
        existing_identity = prior_by_id.get(evaluation_id)
        if existing_identity is not None:
            if existing_identity != record or current_evaluation != existing_identity:
                raise ManualEvaluationConflict(
                    "evaluation ID already has conflicting durable content"
                )
            if latest is None or latest.context.manual_evaluation_id != evaluation_id:
                raise ManualEvaluationStale(
                    "idempotent evaluation has no matching gate observation"
                )
            return latest

        for evidence in new_evidence:
            insert_evidence_from_connection(connection, evidence)
        insert_manual_evaluation_from_connection(connection, record)
        context = _successor_evaluation_context(
            database,
            connection,
            slice_value=snapshot.value,
            lifecycle=lifecycle,
            gates=gates,
            source_baseline=source_baseline,
            result_baseline=result_baseline,
            evaluation=record,
            governance_revision=prior_governance_revision + 1,
        )
        return record_successor_observation(
            connection,
            gates,
            context,
            successor_gate_evaluation_record_id,
            successor_gate_evaluation_recorded_at,
        )


def _exact_technical_decision_retry(
    connection: sqlite3.Connection,
    snapshot: HumanControlSnapshot,
    basis: HumanActionBasis,
    decision: HumanApprovalDecision,
    expected_result_id: SliceResultId,
    expected_manual_evaluation_id: ManualEvaluationId,
    expected_current_approval_decision_id: HumanDecisionId | None,
    successor_gate_evaluation_record_id: GateEvaluationRecordId,
    successor_gate_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    """Return a durable successor only for an exact, still-current command replay."""

    lifecycle = snapshot.lifecycle
    latest = snapshot.latest
    gates = snapshot.gates
    if lifecycle is None or lifecycle.phase is not LifecyclePhase.EVALUATING or latest is None:
        raise ManualEvaluationConflict("technical decision retry is no longer current")
    observations = load_gate_evaluation_records_for_slice_from_connection(
        connection, decision.slice_id
    )
    predecessor = next(
        (item for item in observations if item.id == basis.evaluation_record_id), None
    )
    successor = next(
        (item for item in observations if item.id == successor_gate_evaluation_record_id), None
    )
    if (
        predecessor is None
        or successor is None
        or latest.id != successor.id
        or not _observations_are_adjacent(observations, predecessor, successor)
        or not _basis_matches_gate_observation(basis, predecessor)
    ):
        raise ManualEvaluationConflict("technical decision retry does not match its exact basis")
    submitted_current = next(
        (
            item.decision_id
            for item in basis.current_approval_decision_ids
            if item.gate_id == decision.gate_id
        ),
        None,
    )
    if submitted_current != expected_current_approval_decision_id:
        raise ManualEvaluationConflict(
            "technical decision retry changed its compare-and-swap basis"
        )
    gate = next((item for item in gates if item.gate_id == decision.gate_id), None)
    if (
        gate is None
        or gate.target_phase is not LifecyclePhase.ACCEPTED
        or decision.baseline_id != gate.baseline_id
        or decision.gate_revision != gate.revision
        or decision.lifecycle_revision != lifecycle.revision
        or decision.governance_revision != predecessor.context.governance_revision
        or decision.slice_id != lifecycle.slice_id
    ):
        raise ManualEvaluationConflict("technical decision retry is bound to another gate basis")
    current_result = snapshot.current_result
    current_evaluation = snapshot.current_manual_evaluation
    if (
        current_result is None
        or current_evaluation is None
        or expected_result_id != basis.current_result_id
        or expected_manual_evaluation_id != basis.current_manual_evaluation_id
        or expected_result_id != current_result.result_id
        or expected_manual_evaluation_id != current_evaluation.evaluation_id
        or current_result.result_id != basis.current_result_id
        or current_result.result_baseline_id != basis.current_result_baseline_id
        or current_evaluation.evaluation_id != basis.current_manual_evaluation_id
        or expected_result_id != successor.context.result_id
        or expected_manual_evaluation_id != successor.context.manual_evaluation_id
        or current_result.result_id != successor.context.result_id
        or current_result.result_baseline_id != successor.context.result_baseline_id
        or current_evaluation.evaluation_id != successor.context.manual_evaluation_id
    ):
        raise ManualEvaluationConflict("technical decision retry subject is no longer current")
    projected = project_decisions(snapshot.decisions, gates)
    current = next(
        (
            item
            for item in projected
            if isinstance(item, HumanApprovalDecision) and item.gate_id == decision.gate_id
        ),
        None,
    )
    if current != decision:
        raise ManualEvaluationConflict("technical decision is no longer the current decision")
    expected_context = successor_context(
        predecessor,
        lifecycle,
        gates,
        project_authorizations(snapshot.grants, gates),
        projected,
    )
    if (
        successor.context != expected_context
        or successor.recorded_at != successor_gate_evaluation_recorded_at.astimezone(UTC)
        or successor.gate_refs != gate_refs_for_gates(gates)
        or evaluate_handover_gates(gates, successor.context) != successor.evaluations
    ):
        raise ManualEvaluationConflict(
            "technical decision retry successor differs from durable state"
        )
    return successor


def _record_technical_decision(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    *,
    expected_result_id: SliceResultId,
    expected_manual_evaluation_id: ManualEvaluationId,
    expected_current_approval_decision_id: HumanDecisionId | None,
    actor: ActorRef,
    reason: str,
    decision_id: HumanDecisionId,
    occurred_at: datetime,
    decision: HumanApprovalValue,
    successor_gate_evaluation_record_id: GateEvaluationRecordId,
    successor_gate_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    _require_human(actor, "technical acceptance or rejection")
    if not reason.strip():
        raise ManualEvaluationInvalid("technical decision reason must be nonblank")
    if basis.slice_id != slice_id:
        raise ManualEvaluationStale("Human Action Basis identifies another Slice")
    if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
        raise ManualEvaluationInvalid("decision time must be timezone-aware")
    if (
        successor_gate_evaluation_recorded_at.tzinfo is None
        or successor_gate_evaluation_recorded_at.utcoffset() is None
    ):
        raise ManualEvaluationInvalid("successor observation time must be timezone-aware")
    basis_gate = next((item for item in basis.gate_refs if item.gate_id == gate_id), None)
    if basis_gate is None:
        raise ManualEvaluationStale("technical decision gate is absent from its submitted basis")
    submitted_decision = HumanApprovalDecision(
        decision_id=decision_id,
        slice_id=slice_id,
        baseline_id=basis.baseline_id,
        gate_id=gate_id,
        gate_revision=basis_gate.gate_revision,
        lifecycle_revision=basis.lifecycle_revision,
        governance_revision=basis.governance_revision,
        actor=actor,
        occurred_at=occurred_at,
        decision=decision,
        reason=reason,
    )

    with _manual_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        existing_identity = next(
            (item for item in snapshot.decisions if item.decision_id == decision_id), None
        )
        if existing_identity is not None:
            if existing_identity != submitted_decision:
                raise ManualEvaluationConflict(
                    "technical decision ID is already bound to different payload"
                )
            return _exact_technical_decision_retry(
                connection,
                snapshot,
                basis,
                submitted_decision,
                expected_result_id,
                expected_manual_evaluation_id,
                expected_current_approval_decision_id,
                successor_gate_evaluation_record_id,
                successor_gate_evaluation_recorded_at,
            )
        lifecycle, gates, latest = validate_human_action_basis(snapshot, basis)
        current_result = snapshot.current_result
        current_evaluation = snapshot.current_manual_evaluation
        if current_result is None or current_evaluation is None:
            raise ManualEvaluationNotAvailable(
                "a current result and manual evaluation are required"
            )
        if (
            current_result.result_id != expected_result_id
            or current_evaluation.evaluation_id != expected_manual_evaluation_id
            or latest.context.result_id != expected_result_id
            or latest.context.manual_evaluation_id != expected_manual_evaluation_id
            or current_evaluation.outcome is not EvaluationOutcome.ACCEPT
        ):
            raise ManualEvaluationStale("technical decision subject is no longer current")
        gate = next((item for item in gates if item.gate_id == gate_id), None)
        if gate is None or gate.target_phase is not LifecyclePhase.ACCEPTED:
            raise ManualEvaluationNotAvailable(
                "technical acceptance applies only to a current ACCEPTED-target gate"
            )
        projected = project_decisions(snapshot.decisions, gates)
        current = next(
            (
                item
                for item in projected
                if isinstance(item, HumanApprovalDecision) and item.gate_id == gate_id
            ),
            None,
        )
        actual_id = None if current is None else current.decision_id
        if actual_id != expected_current_approval_decision_id:
            raise ManualEvaluationConflict("technical decision changed since the form was rendered")

        source_id = _common_baseline(gates)
        if source_id != current_result.source_baseline_id:
            raise PersistenceIntegrityError(
                "current result authority differs from its gate baseline"
            )
        slice_snapshot = get_slice(database, slice_id)
        if (
            current_result.slice_definition_revision != slice_snapshot.definition_revision
            or current_evaluation.slice_definition_revision != slice_snapshot.definition_revision
        ):
            raise ManualEvaluationStale("Slice definition changed since manual evaluation")
        slice_value = slice_snapshot.value
        _, result_baseline = _validate_result_authority(connection, current_result, slice_value)
        if result_baseline.id != current_result.result_baseline_id:
            raise PersistenceIntegrityError("technical decision result Baseline changed")
        occurred_at = timestamp_at_or_after(
            occurred_at,
            lifecycle.updated_at,
            current_result.recorded_at,
            current_evaluation.evaluated_at,
            latest.recorded_at,
            *(item.occurred_at for item in snapshot.decisions),
            label="occurred_at",
        )
        successor_at = timestamp_at_or_after(
            successor_gate_evaluation_recorded_at,
            occurred_at,
            label="successor_gate_evaluation_recorded_at",
        )
        decision_record = HumanApprovalDecision(
            decision_id=decision_id,
            slice_id=slice_id,
            baseline_id=gate.baseline_id,
            gate_id=gate.gate_id,
            gate_revision=gate.revision,
            lifecycle_revision=lifecycle.revision,
            governance_revision=latest.context.governance_revision,
            actor=actor,
            occurred_at=occurred_at,
            decision=decision,
            reason=reason,
        )
        insert_human_decision_from_connection(connection, decision_record)
        decisions = project_decisions(
            load_human_decisions_for_slice_from_connection(connection, slice_id), gates
        )
        context = successor_context(
            latest,
            lifecycle,
            gates,
            project_authorizations(
                load_authorization_grants_for_slice_from_connection(connection, slice_id), gates
            ),
            decisions,
        )
        if (
            context.result_id != current_result.result_id
            or context.result_baseline_id != result_baseline.id
            or context.manual_evaluation_id != current_evaluation.evaluation_id
            or context.evaluation_outcome is not EvaluationOutcome.ACCEPT
        ):
            raise PersistenceIntegrityError("technical decision successor lost its exact subject")
        return record_successor_observation(
            connection,
            gates,
            context,
            successor_gate_evaluation_record_id,
            successor_at,
        )


def record_technical_acceptance(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    *,
    expected_result_id: SliceResultId,
    expected_manual_evaluation_id: ManualEvaluationId,
    expected_current_approval_decision_id: HumanDecisionId | None,
    actor: ActorRef,
    reason: str,
    decision_id: HumanDecisionId,
    occurred_at: datetime,
    successor_gate_evaluation_record_id: GateEvaluationRecordId,
    successor_gate_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    """Record explicit Human technical APPROVE using the durable approval model."""

    return _record_technical_decision(
        database,
        slice_id,
        gate_id,
        basis,
        expected_result_id=expected_result_id,
        expected_manual_evaluation_id=expected_manual_evaluation_id,
        expected_current_approval_decision_id=expected_current_approval_decision_id,
        actor=actor,
        reason=reason,
        decision_id=decision_id,
        occurred_at=occurred_at,
        decision=HumanApprovalValue.APPROVE,
        successor_gate_evaluation_record_id=successor_gate_evaluation_record_id,
        successor_gate_evaluation_recorded_at=successor_gate_evaluation_recorded_at,
    )


def record_technical_rejection(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    *,
    expected_result_id: SliceResultId,
    expected_manual_evaluation_id: ManualEvaluationId,
    expected_current_approval_decision_id: HumanDecisionId | None,
    actor: ActorRef,
    reason: str,
    decision_id: HumanDecisionId,
    occurred_at: datetime,
    successor_gate_evaluation_record_id: GateEvaluationRecordId,
    successor_gate_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    """Record explicit Human technical REJECT without changing evaluator judgment."""

    return _record_technical_decision(
        database,
        slice_id,
        gate_id,
        basis,
        expected_result_id=expected_result_id,
        expected_manual_evaluation_id=expected_manual_evaluation_id,
        expected_current_approval_decision_id=expected_current_approval_decision_id,
        actor=actor,
        reason=reason,
        decision_id=decision_id,
        occurred_at=occurred_at,
        decision=HumanApprovalValue.REJECT,
        successor_gate_evaluation_record_id=successor_gate_evaluation_record_id,
        successor_gate_evaluation_recorded_at=successor_gate_evaluation_recorded_at,
    )


def _accepted_results_from_connection(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    slice_id: SliceId,
) -> tuple[AcceptedSliceResult, ...]:
    """Reconstruct every ACCEPTED result from its exact governed execution chain."""

    lifecycle = load_current_lifecycle_from_connection(connection, slice_id)
    events = load_lifecycle_events(database, slice_id)
    accepted_events = tuple(
        item
        for item in events
        if isinstance(item, PhaseChanged) and item.to_phase is LifecyclePhase.ACCEPTED
    )
    executions = load_execution_records_for_slice_from_connection(connection, slice_id)
    results = load_slice_result_history_from_connection(connection, slice_id)
    results_by_id = {item.result_id: item for item in results}
    evaluations = load_manual_evaluation_history_from_connection(connection, slice_id)
    evaluations_by_id = {item.evaluation_id: item for item in evaluations}
    observations = load_gate_evaluation_records_for_slice_from_connection(connection, slice_id)
    durable_decisions = load_human_decisions_for_slice_from_connection(connection, slice_id)
    execution_by_event: dict[EventId, list[ExecutionRecord]] = {}
    for execution in executions:
        event = next((item for item in events if item.event_id == execution.event_id), None)
        if isinstance(event, PhaseChanged) and event.to_phase is LifecyclePhase.ACCEPTED:
            execution_by_event.setdefault(execution.event_id, []).append(execution)
    if lifecycle is not None and lifecycle.phase is LifecyclePhase.ACCEPTED and not accepted_events:
        raise PersistenceIntegrityError("ACCEPTED lifecycle has no causal phase event")

    accepted: list[AcceptedSliceResult] = []
    for event in accepted_events:
        matching_executions = execution_by_event.get(event.event_id, [])
        if len(matching_executions) != 1:
            raise PersistenceIntegrityError(
                "ACCEPTED lifecycle event has no unique governed execution"
            )
        execution = matching_executions[0]
        if (
            execution.event_id != event.event_id
            or execution.resulting_lifecycle_revision != event.resulting_revision
            or execution.source_lifecycle_revision + 1 != event.resulting_revision
            or execution.occurred_at != event.occurred_at
            or execution.actor != event.actor
        ):
            raise PersistenceIntegrityError(
                "accepted execution does not causally match its lifecycle event"
            )
        observation = next(
            (item for item in observations if item.id == execution.gate_evaluation_record_id),
            None,
        )
        if observation is None:
            raise PersistenceIntegrityError("accepted execution observation is missing")
        context = observation.context
        gate = load_handover_gate(
            database, execution.selected_gate_id, execution.selected_gate_revision
        )
        if (
            gate is None
            or gate.target_phase is not LifecyclePhase.ACCEPTED
            or gate.baseline_id != execution.baseline_id
            or gate.gate_id != execution.selected_gate_id
            or gate.revision != execution.selected_gate_revision
        ):
            raise PersistenceIntegrityError(
                "accepted execution did not use an ACCEPTED-target gate"
            )
        outputs = tuple(
            item
            for item in observation.evaluations
            if item.gate_id == gate.gate_id and item.gate_revision == gate.revision
        )
        if len(outputs) != 1 or outputs[0].light is not TrafficLight.GREEN:
            raise PersistenceIntegrityError("accepted execution lacks exact GREEN gate evidence")
        if (
            context.lifecycle.slice_id != slice_id
            or context.lifecycle.revision != execution.source_lifecycle_revision
            or context.baseline_id != gate.baseline_id
            or context.result_id is None
            or context.result_baseline_id is None
            or context.manual_evaluation_id is None
            or context.evaluation_outcome is not EvaluationOutcome.ACCEPT
        ):
            raise PersistenceIntegrityError("accepted execution lacks exact Slice 1.7 subject")
        observed_gates = tuple(
            load_handover_gate(database, reference.gate_id, reference.gate_revision)
            for reference in observation.gate_refs
        )
        if any(gate is None for gate in observed_gates):
            raise PersistenceIntegrityError(
                "accepted observation references a missing gate revision"
            )
        complete_gates = tuple(gate for gate in observed_gates if gate is not None)
        if (
            not complete_gates
            or any(gate.slice_id != slice_id for gate in complete_gates)
            or gate_refs_for_gates(complete_gates) != observation.gate_refs
            or evaluate_handover_gates(complete_gates, context) != observation.evaluations
        ):
            raise PersistenceIntegrityError(
                "accepted execution gate observation is incomplete or non-deterministic"
            )
        result = results_by_id.get(context.result_id)
        evaluation = evaluations_by_id.get(context.manual_evaluation_id)
        if (
            result is None
            or evaluation is None
            or result.result_baseline_id != context.result_baseline_id
            or evaluation.result_id != result.result_id
            or evaluation.result_baseline_id != result.result_baseline_id
            or evaluation.source_baseline_id != result.source_baseline_id
            or evaluation.outcome is not EvaluationOutcome.ACCEPT
            or evaluation.lifecycle_revision != context.lifecycle.revision
            or evaluation.evaluation_id != context.manual_evaluation_id
        ):
            raise PersistenceIntegrityError("accepted execution does not match authored evaluation")
        slice_snapshot = get_slice(database, slice_id)
        if result.slice_definition_revision != slice_snapshot.definition_revision:
            raise PersistenceIntegrityError(
                "accepted result references another Slice definition revision"
            )
        slice_value = slice_snapshot.value
        source, result_baseline = _validate_result_authority(connection, result, slice_value)
        if (
            source.id != gate.baseline_id
            or result_baseline.id != context.result_baseline_id
            or source.decision_ids != result_baseline.decision_ids
        ):
            raise PersistenceIntegrityError("accepted result Decision authority is inconsistent")
        approvals = tuple(
            item
            for item in context.human_decisions
            if isinstance(item, HumanApprovalDecision)
            and item.gate_id == gate.gate_id
            and item.gate_revision == gate.revision
            and item.baseline_id == gate.baseline_id
            and item.lifecycle_revision == context.lifecycle.revision
            and item.governance_revision == context.governance_revision
            and item.decision is HumanApprovalValue.APPROVE
        )
        if len(approvals) != 1:
            raise PersistenceIntegrityError(
                "accepted execution lacks unique Human technical APPROVE"
            )
        approval = approvals[0]
        if approval not in durable_decisions:
            raise PersistenceIntegrityError(
                "accepted observation Human APPROVE is missing from durable decisions"
            )
        if (
            execution.occurred_at < approval.occurred_at
            or execution.occurred_at < evaluation.evaluated_at
            or observation.recorded_at < evaluation.evaluated_at
            or execution.occurred_at < observation.recorded_at
            or event.to_phase is not LifecyclePhase.ACCEPTED
        ):
            raise PersistenceIntegrityError(
                "accepted execution chronology or event target is invalid"
            )
        accepted.append(
            AcceptedSliceResult(
                slice_id=slice_id,
                result_id=result.result_id,
                result_baseline_id=result_baseline.id,
                commit=result_baseline.commit.sha,
                manual_evaluation_id=evaluation.evaluation_id,
                human_approval_decision_id=approval.decision_id,
                accepted_execution_id=execution.execution_id,
                accepted_at=execution.occurred_at,
            )
        )
    if lifecycle is not None and lifecycle.phase is LifecyclePhase.ACCEPTED:
        current_events = tuple(
            item for item in accepted_events if item.resulting_revision == lifecycle.revision
        )
        if len(current_events) != 1:
            raise PersistenceIntegrityError(
                "current ACCEPTED lifecycle has no unique causal phase event"
            )
        current_executions = execution_by_event.get(current_events[0].event_id, ())
        if (
            len(current_executions) != 1
            or sum(
                item.accepted_execution_id == current_executions[0].execution_id
                for item in accepted
            )
            != 1
        ):
            raise PersistenceIntegrityError(
                "current ACCEPTED lifecycle has no uniquely reconstructable result"
            )
    return tuple(accepted)


def _exact_accepted_promotion_retry(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    *,
    expected_result_id: SliceResultId,
    expected_manual_evaluation_id: ManualEvaluationId,
    expected_current_approval_decision_id: HumanDecisionId,
    actor: ActorRef,
    reason: str,
    gate_evaluation_record_id: GateEvaluationRecordId,
    gate_evaluation_recorded_at: datetime,
    execution_id: ExecutionId,
    event_id: EventId,
    occurred_at: datetime,
) -> AcceptedSliceResult:
    """Return an already-committed promotion only when every durable identity matches."""

    lifecycle = load_current_lifecycle_from_connection(connection, slice_id)
    if lifecycle is None or lifecycle.phase is not LifecyclePhase.ACCEPTED:
        raise ManualEvaluationConflict("accepted promotion retry has no ACCEPTED target state")
    accepted = _accepted_results_from_connection(database, connection, slice_id)
    matching = tuple(
        item
        for item in accepted
        if item.result_id == expected_result_id
        and item.manual_evaluation_id == expected_manual_evaluation_id
        and item.accepted_execution_id == execution_id
    )
    if len(matching) != 1:
        raise ManualEvaluationConflict("accepted target state has another promotion identity")
    projection = matching[0]
    executions = load_execution_records_for_slice_from_connection(connection, slice_id)
    execution = next((item for item in executions if item.execution_id == execution_id), None)
    observations = load_gate_evaluation_records_for_slice_from_connection(connection, slice_id)
    promotion_observation = next(
        (item for item in observations if item.id == gate_evaluation_record_id), None
    )
    predecessor = next(
        (item for item in observations if item.id == basis.evaluation_record_id), None
    )
    events = load_lifecycle_events(database, slice_id)
    event = next((item for item in events if item.event_id == event_id), None)
    current_accepted_events = tuple(
        item
        for item in events
        if isinstance(item, PhaseChanged)
        and item.to_phase is LifecyclePhase.ACCEPTED
        and item.resulting_revision == lifecycle.revision
    )
    approval_for_gate = next(
        (
            item.decision_id
            for item in basis.current_approval_decision_ids
            if item.gate_id == gate_id
        ),
        None,
    )
    exact = (
        execution is not None
        and promotion_observation is not None
        and predecessor is not None
        and isinstance(event, PhaseChanged)
        and len(current_accepted_events) == 1
        and current_accepted_events[0].event_id == event_id
        and _basis_matches_gate_observation(basis, predecessor)
        and _observations_are_adjacent(observations, predecessor, promotion_observation)
        and promotion_observation.context == predecessor.context
        and promotion_observation.gate_refs == predecessor.gate_refs
        and promotion_observation.recorded_at == gate_evaluation_recorded_at.astimezone(UTC)
        and projection.human_approval_decision_id == expected_current_approval_decision_id
        and approval_for_gate == expected_current_approval_decision_id
        and basis.current_result_id == expected_result_id
        and basis.current_manual_evaluation_id == expected_manual_evaluation_id
        and execution.gate_evaluation_record_id == gate_evaluation_record_id
        and execution.event_id == event_id
        and execution.selected_gate_id == gate_id
        and execution.slice_id == slice_id
        and execution.baseline_id == basis.baseline_id
        and execution.source_lifecycle_revision == basis.lifecycle_revision
        and execution.resulting_lifecycle_revision == lifecycle.revision
        and execution.actor == actor
        and execution.reason == reason
        and execution.occurred_at == occurred_at.astimezone(UTC)
        and event.to_phase is LifecyclePhase.ACCEPTED
        and event.from_phase is LifecyclePhase.EVALUATING
        and event.actor == actor
        and event.reason == reason
        and event.occurred_at == occurred_at.astimezone(UTC)
        and execution.selected_gate_revision
        == next(
            (
                reference.gate_revision
                for reference in basis.gate_refs
                if reference.gate_id == gate_id
            ),
            None,
        )
    )
    if not exact:
        raise ManualEvaluationConflict("accepted target state does not match the exact retry")
    return projection


def promote_accepted_result(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    *,
    expected_result_id: SliceResultId,
    expected_manual_evaluation_id: ManualEvaluationId,
    expected_current_approval_decision_id: HumanDecisionId,
    actor: ActorRef,
    reason: str,
    gate_evaluation_record_id: GateEvaluationRecordId,
    gate_evaluation_recorded_at: datetime,
    execution_id: ExecutionId,
    event_id: EventId,
    occurred_at: datetime,
) -> AcceptedSliceResult:
    """Promote only an exact current evaluator ACCEPT + Human APPROVE through a GREEN gate."""

    _require_human(actor, "accepted-result promotion")
    if basis.slice_id != slice_id:
        raise ManualEvaluationStale("Human Action Basis identifies another Slice")
    with _manual_write(database) as connection:
        lifecycle = load_current_lifecycle_from_connection(connection, slice_id)
        if lifecycle is not None and lifecycle.phase is LifecyclePhase.ACCEPTED:
            if (
                gate_evaluation_recorded_at.tzinfo is None
                or gate_evaluation_recorded_at.utcoffset() is None
                or occurred_at.tzinfo is None
                or occurred_at.utcoffset() is None
            ):
                raise ManualEvaluationInvalid("promotion timestamps must be timezone-aware")
            return _exact_accepted_promotion_retry(
                database,
                connection,
                slice_id,
                gate_id,
                basis,
                expected_result_id=expected_result_id,
                expected_manual_evaluation_id=expected_manual_evaluation_id,
                expected_current_approval_decision_id=expected_current_approval_decision_id,
                actor=actor,
                reason=reason,
                gate_evaluation_record_id=gate_evaluation_record_id,
                gate_evaluation_recorded_at=gate_evaluation_recorded_at,
                execution_id=execution_id,
                event_id=event_id,
                occurred_at=occurred_at,
            )
        snapshot = load_human_control_snapshot(connection, slice_id)
        lifecycle, gates, latest = validate_human_action_basis(snapshot, basis)
        if (
            lifecycle.phase is not LifecyclePhase.EVALUATING
            or lifecycle.validity is not LifecycleValidity.CURRENT
            or lifecycle.blockage.reasons
        ):
            raise ManualEvaluationNotAvailable("Slice is not in a promotable EVALUATING lifecycle")
        current_result = snapshot.current_result
        current_evaluation = snapshot.current_manual_evaluation
        if (
            current_result is None
            or current_evaluation is None
            or current_result.result_id != expected_result_id
            or current_evaluation.evaluation_id != expected_manual_evaluation_id
            or current_evaluation.outcome is not EvaluationOutcome.ACCEPT
            or latest.context.result_id != expected_result_id
            or latest.context.result_baseline_id != current_result.result_baseline_id
            or latest.context.manual_evaluation_id != expected_manual_evaluation_id
            or latest.context.evaluation_outcome is not EvaluationOutcome.ACCEPT
        ):
            raise ManualEvaluationStale("accepted-result subject is no longer current")
        gate = next((item for item in gates if item.gate_id == gate_id), None)
        if gate is None or gate.target_phase is not LifecyclePhase.ACCEPTED:
            raise ManualEvaluationNotAvailable("selected gate is not a current ACCEPTED target")
        source_id = _common_baseline(gates)
        if source_id != current_result.source_baseline_id:
            raise PersistenceIntegrityError("current result uses a different authority Baseline")
        slice_snapshot = get_slice(database, slice_id)
        if (
            current_result.slice_definition_revision != slice_snapshot.definition_revision
            or current_evaluation.slice_definition_revision != slice_snapshot.definition_revision
        ):
            raise ManualEvaluationStale("Slice definition changed since manual evaluation")
        slice_value = slice_snapshot.value
        source, result_baseline = _validate_result_authority(
            connection, current_result, slice_value
        )
        if source.decision_ids != result_baseline.decision_ids:
            raise PersistenceIntegrityError("result Baseline Decision authority drifted")
        approvals = tuple(
            item
            for item in project_decisions(snapshot.decisions, gates)
            if isinstance(item, HumanApprovalDecision) and item.gate_id == gate_id
        )
        approval = approvals[0] if approvals else None
        if (
            approval is None
            or approval.decision_id != expected_current_approval_decision_id
            or approval.decision is not HumanApprovalValue.APPROVE
            or approval.baseline_id != source.id
            or approval.gate_revision != gate.revision
            or approval.lifecycle_revision != lifecycle.revision
            or approval.governance_revision != latest.context.governance_revision
        ):
            raise ManualEvaluationStale("exact current Human technical APPROVE is required")
        evaluations = evaluate_handover_gates(gates, latest.context)
        selected = next((item for item in evaluations if item.gate_id == gate_id), None)
        if evaluations != latest.evaluations:
            raise PersistenceIntegrityError("latest gate observation is not deterministic")
        if selected is None or selected.light is not TrafficLight.GREEN:
            raise ManualEvaluationNotAvailable("current ACCEPTED-target gate is not GREEN")
        if (
            gate_evaluation_recorded_at.tzinfo is None
            or gate_evaluation_recorded_at.utcoffset() is None
        ):
            raise ManualEvaluationInvalid("promotion evaluation time must be timezone-aware")
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise ManualEvaluationInvalid("promotion time must be timezone-aware")
        gate_evaluation_recorded_at = timestamp_at_or_after(
            gate_evaluation_recorded_at,
            latest.recorded_at,
            current_evaluation.evaluated_at,
            approval.occurred_at,
            label="gate_evaluation_recorded_at",
        )
        occurred_at = timestamp_at_or_after(
            occurred_at,
            gate_evaluation_recorded_at,
            label="occurred_at",
        )
        execute_and_persist_handover_from_connection(
            connection,
            gates,
            gate_id,
            latest.context,
            lifecycle.revision,
            gate_evaluation_record_id,
            gate_evaluation_recorded_at,
            execution_id,
            event_id,
            actor,
            occurred_at,
            reason,
        )
        accepted = _accepted_results_from_connection(database, connection, slice_id)
        matching = tuple(
            item
            for item in accepted
            if item.accepted_execution_id == execution_id
            and item.result_id == expected_result_id
            and item.manual_evaluation_id == expected_manual_evaluation_id
        )
        if len(matching) != 1:
            raise PersistenceIntegrityError("promotion did not create one reconstructable result")
        return matching[0]


def project_manual_evaluation_from_connection(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    slice_id: SliceId,
    *,
    slice_definition_revision: int,
) -> ManualEvaluationProjection:
    snapshot = get_slice(database, slice_id)
    if snapshot.definition_revision != slice_definition_revision:
        raise PersistenceIntegrityError("Slice definition changed during board projection")
    lifecycle = load_current_lifecycle_from_connection(connection, slice_id)
    gates = current_gates(
        load_handover_gates_for_slice_from_connection(connection, slice_id), lifecycle
    )
    result_history = load_slice_result_history_from_connection(connection, slice_id)
    evaluation_history = load_manual_evaluation_history_from_connection(connection, slice_id)
    current_result, current_evaluation = load_slice_1_7_subject_from_connection(
        connection, slice_id
    )
    if (
        current_result is not None
        and current_result.slice_definition_revision != snapshot.definition_revision
    ):
        raise PersistenceIntegrityError("current result references another Slice definition")
    current_result_baseline = None
    if current_result is not None:
        _, current_result_baseline = _validate_result_authority(
            connection, current_result, snapshot.value
        )
    latest_records = load_gate_evaluation_records_for_slice_from_connection(connection, slice_id)
    latest = None if not latest_records else latest_records[-1]
    expected_refs = gate_refs_for_gates(gates)
    if current_evaluation is not None and (
        current_result is None
        or lifecycle is None
        or latest is None
        or (
            latest.context.result_id != current_result.result_id
            or latest.context.result_baseline_id != current_result.result_baseline_id
            or latest.context.manual_evaluation_id != current_evaluation.evaluation_id
            or latest.context.evaluation_outcome is not current_evaluation.outcome
            or latest.context.lifecycle.revision != lifecycle.revision
            or latest.gate_refs != expected_refs
        )
    ):
        raise PersistenceIntegrityError(
            "authored manual evaluation has no exact current successor gate observation"
        )
    accepted_results = _accepted_results_from_connection(database, connection, slice_id)
    accepted_result = None if not accepted_results else accepted_results[-1]
    current_technical_decision = None
    if accepted_result is not None:
        decisions = load_human_decisions_for_slice_from_connection(connection, slice_id)
        candidate = next(
            (
                item
                for item in decisions
                if isinstance(item, HumanApprovalDecision)
                and item.decision_id == accepted_result.human_approval_decision_id
            ),
            None,
        )
        if candidate is None:
            raise PersistenceIntegrityError("accepted projection Human decision is missing")
        current_technical_decision = candidate
    elif current_result is not None:
        current_decisions = project_decisions(
            load_human_decisions_for_slice_from_connection(connection, slice_id), gates
        )
        current_technical_decision = next(
            (
                decision
                for decision in current_decisions
                if isinstance(decision, HumanApprovalDecision)
                and any(
                    gate.gate_id == decision.gate_id
                    and gate.revision == decision.gate_revision
                    and gate.target_phase is LifecyclePhase.ACCEPTED
                    for gate in gates
                )
            ),
            None,
        )
        if current_technical_decision is not None and (
            latest is None
            or lifecycle is None
            or current_technical_decision.baseline_id != latest.context.baseline_id
            or current_technical_decision.lifecycle_revision != lifecycle.revision
            or current_technical_decision.governance_revision != latest.context.governance_revision
        ):
            current_technical_decision = None

    action_basis = None
    actions: list[ManualEvaluationActionKind] = []
    technical_gate_refs: tuple[GateRevisionRef, ...] = ()
    promotable_gate_refs: tuple[GateRevisionRef, ...] = ()
    if lifecycle is not None and lifecycle.phase is LifecyclePhase.EVALUATING and gates:
        human_snapshot = load_human_control_snapshot(connection, slice_id)
        human_basis = basis_if_current(human_snapshot)
        action_basis = ManualEvaluationActionBasis(
            slice_id=slice_id,
            lifecycle_revision=lifecycle.revision,
            slice_definition_revision=snapshot.definition_revision,
            current_result_id=None if current_result is None else current_result.result_id,
            current_manual_evaluation_id=(
                None if current_evaluation is None else current_evaluation.evaluation_id
            ),
            latest_gate_evaluation_record_id=None if latest is None else latest.id,
            gate_refs=expected_refs,
        )
        if current_evaluation is None:
            actions.append(ManualEvaluationActionKind.ATTACH_RESULT)
        if current_result is not None:
            actions.append(ManualEvaluationActionKind.EVALUATE)
        if (
            current_evaluation is not None
            and current_evaluation.outcome is EvaluationOutcome.ACCEPT
        ):
            accepted_gates = tuple(
                GateRevisionRef(gate_id=item.gate_id, gate_revision=item.revision)
                for item in gates
                if item.target_phase is LifecyclePhase.ACCEPTED
            )
            if human_basis is not None and accepted_gates:
                technical_gate_refs = accepted_gates
                actions.extend(
                    (
                        ManualEvaluationActionKind.TECHNICAL_ACCEPT,
                        ManualEvaluationActionKind.TECHNICAL_REJECT,
                    )
                )
                if latest is not None:
                    decisions = project_decisions(human_snapshot.decisions, gates)
                    approvals = {
                        item.gate_id: item
                        for item in decisions
                        if isinstance(item, HumanApprovalDecision)
                    }
                    gate_by_id = {item.gate_id: item for item in gates}
                    light_by_gate = {item.gate_id: item for item in latest.evaluations}
                    promotable_gate_refs = tuple(
                        reference
                        for reference in accepted_gates
                        if approvals.get(reference.gate_id) is not None
                        and approvals[reference.gate_id].decision is HumanApprovalValue.APPROVE
                        and approvals[reference.gate_id].baseline_id
                        == gate_by_id[reference.gate_id].baseline_id
                        and approvals[reference.gate_id].gate_revision == reference.gate_revision
                        and approvals[reference.gate_id].lifecycle_revision == lifecycle.revision
                        and approvals[reference.gate_id].governance_revision
                        == latest.context.governance_revision
                        and light_by_gate.get(reference.gate_id) is not None
                        and light_by_gate[reference.gate_id].gate_revision
                        == reference.gate_revision
                        and light_by_gate[reference.gate_id].light is TrafficLight.GREEN
                    )
                    if promotable_gate_refs:
                        actions.append(ManualEvaluationActionKind.PROMOTE_ACCEPTED)

    development_memory = None
    if result_history:
        source_baseline = load_baseline_from_connection(
            connection, result_history[0].source_baseline_id
        )
        if source_baseline is None:
            raise PersistenceIntegrityError("development-memory source Baseline is missing")
        evidence_ids = tuple(
            sorted(
                {evidence_id for item in evaluation_history for evidence_id in item.evidence_ids}
            )
        )
        evidence = tuple(
            item
            for evidence_id in evidence_ids
            if (item := load_evidence_from_connection(connection, evidence_id)) is not None
        )
        if len(evidence) != len(evidence_ids):
            raise PersistenceIntegrityError("development-memory Evidence reference is missing")
        development_memory = DevelopmentMemoryProjection(
            slice_id=slice_id,
            source_baseline=source_baseline,
            result_history=result_history,
            evaluation_history=evaluation_history,
            evidence=evidence,
            accepted_results=accepted_results,
        )
    return ManualEvaluationProjection(
        action_basis=action_basis,
        actions=tuple(dict.fromkeys(actions)),
        technical_gate_refs=technical_gate_refs,
        promotable_gate_refs=promotable_gate_refs,
        current_result=current_result,
        current_result_baseline=current_result_baseline,
        result_history=result_history,
        current_evaluation=current_evaluation,
        evaluation_history=evaluation_history,
        current_technical_decision=current_technical_decision,
        accepted_result=accepted_result,
        accepted_results=accepted_results,
        development_memory=development_memory,
    )


def project_manual_evaluation(
    database: RelayDatabase, slice_id: SliceId
) -> ManualEvaluationProjection:
    """Project exact current/historical evaluation state from one read snapshot."""

    try:
        with read_transaction(database) as connection:
            snapshot = get_slice(database, slice_id)
            return project_manual_evaluation_from_connection(
                database,
                connection,
                slice_id,
                slice_definition_revision=snapshot.definition_revision,
            )
    except ValidationError as error:
        raise PersistenceIntegrityError("manual-evaluation projection is invalid") from error


def project_development_memory(
    database: RelayDatabase, slice_id: SliceId
) -> DevelopmentMemoryProjection | None:
    """Return the deterministic development-memory projection when results exist."""

    return project_manual_evaluation(database, slice_id).development_memory


__all__ = [
    "attach_result",
    "project_development_memory",
    "project_manual_evaluation",
    "promote_accepted_result",
    "record_manual_evaluation",
    "record_technical_acceptance",
    "record_technical_rejection",
]
