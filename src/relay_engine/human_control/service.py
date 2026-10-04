"""Transactional Human Authority commands over durable governance evidence."""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime

from relay_engine.domain.ids import (
    AuthorizationId,
    EventId,
    ExecutionId,
    GateEvaluationRecordId,
    HandoverGateId,
    HumanDecisionId,
    SliceId,
)
from relay_engine.domain.models import Baseline
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.governance import (
    AuthorizationGrant,
    GateEvaluation,
    GateReasonCode,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    HumanApprovalDecision,
    HumanApprovalValue,
    HumanChoiceDecision,
    HumanGateDecision,
    TrafficLight,
    evaluate_handover_gates,
)
from relay_engine.human_control.errors import (
    HumanActionBasisStale,
    HumanActionConflict,
    HumanActionForbidden,
    HumanActionInvalidChoice,
    HumanActionNotAvailable,
    HumanActionRequiresEvaluation,
)
from relay_engine.human_control.models import (
    HumanAction,
    HumanActionBasis,
    HumanActionKind,
    HumanActionProjection,
    HumanApprovalIdentity,
)
from relay_engine.lifecycle import clear_blockage, is_blockable_phase, set_blocked
from relay_engine.lifecycle.errors import LifecycleError
from relay_engine.lifecycle.models import (
    BlockageStatus,
    BlockReason,
    LifecyclePhase,
    SliceLifecycle,
)
from relay_engine.manual_evaluation.models import ManualEvaluationRecord, SliceResultRecord
from relay_engine.persistence import (
    ConcurrencyConflict,
    GateEvaluationRecord,
    PersistenceIntegrityError,
    RelayDatabase,
    execute_and_persist_handover_from_connection,
    insert_authorization_grant_from_connection,
    insert_gate_evaluation_record_from_connection,
    insert_human_decision_from_connection,
    load_authorization_grants_for_slice_from_connection,
    load_baseline_from_connection,
    load_current_lifecycle_from_connection,
    load_gate_evaluation_records_for_slice_from_connection,
    load_handover_gates_for_slice_from_connection,
    load_human_decisions_for_slice_from_connection,
    load_slice_1_7_subject_from_connection,
    persist_lifecycle_change_from_connection,
)
from relay_engine.persistence.database import write_transaction
from relay_engine.persistence.records import ExecutionRecord

_HUMAN_HOLD_CODES = frozenset({"HUMAN_BLOCK", "HUMAN_PAUSE", "HUMAN_DEFER"})
_APPROVAL_REASONS = frozenset(
    {
        GateReasonCode.HUMAN_APPROVAL_REQUIRED,
        GateReasonCode.CHANGE_SURFACE_REVIEW_REQUIRED,
        GateReasonCode.RISK_REVIEW_REQUIRED,
        GateReasonCode.HARD_STOP_REQUIRES_HUMAN,
    }
)


@dataclass(frozen=True, slots=True)
class HumanControlSnapshot:
    """Relevant durable state loaded after a read or write transaction begins."""

    lifecycle: SliceLifecycle | None
    gates: tuple[HandoverGate, ...]
    latest: GateEvaluationRecord | None
    grants: tuple[AuthorizationGrant, ...]
    decisions: tuple[HumanGateDecision, ...]
    current_result: SliceResultRecord | None
    current_result_baseline: Baseline | None
    current_manual_evaluation: ManualEvaluationRecord | None


@contextmanager
def _human_write(database: RelayDatabase) -> Generator[sqlite3.Connection]:
    """Translate persistence concurrency and uniqueness failures at this boundary."""

    try:
        with write_transaction(database) as connection:
            yield connection
    except ConcurrencyConflict as error:
        raise HumanActionConflict("durable state changed during the Human action") from error
    except sqlite3.IntegrityError as error:
        raise PersistenceIntegrityError(
            "Human action violated a durable integrity constraint"
        ) from error


def _require_human(actor: ActorRef) -> None:
    if actor.kind is not ActorKind.HUMAN:
        raise HumanActionForbidden("Human Authority commands require a server-bound HUMAN actor")


def current_gates(
    gate_history: tuple[HandoverGate, ...], lifecycle: SliceLifecycle | None
) -> tuple[HandoverGate, ...]:
    if lifecycle is None:
        return ()
    latest_by_id: dict[HandoverGateId, HandoverGate] = {}
    for gate in gate_history:
        current = latest_by_id.get(gate.gate_id)
        if current is None or gate.revision > current.revision:
            latest_by_id[gate.gate_id] = gate
    return tuple(
        sorted(
            (gate for gate in latest_by_id.values() if gate.source_phase is lifecycle.phase),
            key=lambda item: item.gate_id,
        )
    )


def load_human_control_snapshot(
    connection: sqlite3.Connection, slice_id: SliceId
) -> HumanControlSnapshot:
    lifecycle = load_current_lifecycle_from_connection(connection, slice_id)
    gates = current_gates(
        load_handover_gates_for_slice_from_connection(connection, slice_id), lifecycle
    )
    evaluation_records = load_gate_evaluation_records_for_slice_from_connection(
        connection, slice_id
    )
    for index, record in enumerate(evaluation_records):
        for earlier in evaluation_records[:index]:
            if (
                earlier.gate_refs == record.gate_refs
                and earlier.context == record.context
                and earlier.evaluations != record.evaluations
            ):
                raise PersistenceIntegrityError(
                    "duplicate full-basis evaluation records have conflicting outputs"
                )
    latest = evaluation_records[-1] if evaluation_records else None
    current_result, current_manual_evaluation = load_slice_1_7_subject_from_connection(
        connection, slice_id
    )
    current_result_baseline = None
    if current_result is not None:
        current_result_baseline = load_baseline_from_connection(
            connection, current_result.result_baseline_id
        )
        if current_result_baseline is None:
            raise PersistenceIntegrityError("current result Baseline is missing")
    return HumanControlSnapshot(
        lifecycle=lifecycle,
        gates=gates,
        latest=latest,
        grants=load_authorization_grants_for_slice_from_connection(connection, slice_id),
        decisions=load_human_decisions_for_slice_from_connection(connection, slice_id),
        current_result=current_result,
        current_result_baseline=current_result_baseline,
        current_manual_evaluation=current_manual_evaluation,
    )


def _require_gates(
    snapshot: HumanControlSnapshot,
) -> tuple[SliceLifecycle, tuple[HandoverGate, ...]]:
    if snapshot.lifecycle is None:
        raise HumanActionNotAvailable("Slice lifecycle is not initialized")
    if not snapshot.gates:
        raise HumanActionNotAvailable("Slice has no current outgoing gates")
    return snapshot.lifecycle, snapshot.gates


def project_authorizations(
    grants: tuple[AuthorizationGrant, ...], gates: tuple[HandoverGate, ...]
) -> tuple[AuthorizationGrant, ...]:
    """Apply the accepted Revision 3 exact-first grant projection deterministically."""

    projected: list[AuthorizationGrant] = []
    for gate in gates:
        same_gate = tuple(
            item
            for item in grants
            if item.slice_id == gate.slice_id and item.gate_id == gate.gate_id
        )
        exact = tuple(
            item
            for item in same_gate
            if item.baseline_id == gate.baseline_id and item.gate_revision == gate.revision
        )
        if exact:
            selected = min(exact, key=lambda item: (item.granted_at, item.authorization_id))
        elif same_gate:
            selected = max(same_gate, key=lambda item: (item.granted_at, item.authorization_id))
        else:
            continue
        projected.append(selected)
    return tuple(projected)


def project_decisions(
    decisions: tuple[HumanGateDecision, ...], gates: tuple[HandoverGate, ...]
) -> tuple[HumanGateDecision, ...]:
    current_gate_ids = {gate.gate_id for gate in gates}
    approvals_by_gate: dict[HandoverGateId, HumanApprovalDecision] = {}
    choices: list[HumanChoiceDecision] = []
    for decision in decisions:
        if isinstance(decision, HumanApprovalDecision):
            if decision.gate_id not in current_gate_ids:
                continue
            current = approvals_by_gate.get(decision.gate_id)
            if current is None or (decision.occurred_at, decision.decision_id) > (
                current.occurred_at,
                current.decision_id,
            ):
                approvals_by_gate[decision.gate_id] = decision
        else:
            choices.append(decision)
    approvals = tuple(approvals_by_gate[key] for key in sorted(approvals_by_gate))
    choice = max(choices, key=lambda item: (item.occurred_at, item.decision_id), default=None)
    return approvals if choice is None else (*approvals, choice)


def gate_refs_for_gates(gates: tuple[HandoverGate, ...]) -> tuple[GateRevisionRef, ...]:
    return tuple(
        GateRevisionRef(gate_id=item.gate_id, gate_revision=item.revision) for item in gates
    )


def _basis_for_snapshot(snapshot: HumanControlSnapshot) -> HumanActionBasis:
    lifecycle, gates = _require_gates(snapshot)
    latest = snapshot.latest
    if latest is None:
        raise HumanActionRequiresEvaluation("a durable gate evaluation is required")
    expected_refs = gate_refs_for_gates(gates)
    expected_baselines = {gate.baseline_id for gate in gates}
    if len(expected_baselines) != 1:
        raise PersistenceIntegrityError("current outgoing gates identify mixed baselines")
    baseline_id = next(iter(expected_baselines))
    projected_grants = project_authorizations(snapshot.grants, gates)
    projected_decisions = project_decisions(snapshot.decisions, gates)
    if (
        latest.context.lifecycle != lifecycle
        or latest.context.baseline_id != baseline_id
        or latest.gate_refs != expected_refs
    ):
        raise HumanActionBasisStale("latest evaluation does not match current durable structure")
    if latest.context.authorization_grants != projected_grants:
        raise HumanActionRequiresEvaluation(
            "latest evaluation does not project the current authorization evidence"
        )
    if latest.context.human_decisions != projected_decisions:
        raise HumanActionRequiresEvaluation(
            "latest evaluation does not project the current Human decision evidence"
        )
    if snapshot.current_result is not None and snapshot.current_manual_evaluation is None:
        raise HumanActionRequiresEvaluation(
            "the current Slice result is awaiting an authored manual evaluation"
        )
    current_result_id = (
        None if snapshot.current_result is None else snapshot.current_result.result_id
    )
    current_result_baseline_id = (
        None if snapshot.current_result is None else snapshot.current_result.result_baseline_id
    )
    current_manual_evaluation_id = (
        None
        if snapshot.current_manual_evaluation is None
        else snapshot.current_manual_evaluation.evaluation_id
    )
    if (
        latest.context.result_id != current_result_id
        or latest.context.result_baseline_id != current_result_baseline_id
        or latest.context.manual_evaluation_id != current_manual_evaluation_id
    ):
        if current_result_id is not None:
            raise HumanActionRequiresEvaluation(
                "latest gate observation does not project the current Slice 1.7 subject"
            )
        raise HumanActionBasisStale("latest gate observation contains a stale Slice 1.7 subject")
    if snapshot.current_manual_evaluation is not None:
        result = snapshot.current_result
        result_baseline = snapshot.current_result_baseline
        evaluation = snapshot.current_manual_evaluation
        if result is None or result_baseline is None:
            raise PersistenceIntegrityError("current manual evaluation subject is incomplete")
        if (
            result.source_baseline_id != baseline_id
            or result_baseline.id != result.result_baseline_id
            or latest.context.evaluation_outcome is not evaluation.outcome
            or latest.context.available_artifact_ids != result_baseline.artifact_ids
            or latest.context.available_evidence_ids != evaluation.evidence_ids
            or latest.context.quality_checks != evaluation.quality_checks
            or latest.context.change_surface_status != evaluation.change_surface_status
            or latest.context.risk_status != evaluation.risk_status
            or latest.context.toolchain_change_status != evaluation.toolchain_change_status
        ):
            raise HumanActionRequiresEvaluation(
                "latest gate observation does not project the exact authored evaluation"
            )
    if evaluate_handover_gates(gates, latest.context) != latest.evaluations:
        raise PersistenceIntegrityError(
            "durable gate observation disagrees with deterministic evaluation"
        )
    approvals = tuple(
        HumanApprovalIdentity(gate_id=item.gate_id, decision_id=item.decision_id)
        for item in projected_decisions
        if isinstance(item, HumanApprovalDecision)
    )
    choice = next(
        (item for item in projected_decisions if isinstance(item, HumanChoiceDecision)), None
    )
    return HumanActionBasis(
        evaluation_record_id=latest.id,
        slice_id=lifecycle.slice_id,
        baseline_id=baseline_id,
        lifecycle_revision=lifecycle.revision,
        governance_revision=latest.context.governance_revision,
        gate_refs=expected_refs,
        current_approval_decision_ids=approvals,
        current_choice_decision_id=None if choice is None else choice.decision_id,
        current_result_id=current_result_id,
        current_result_baseline_id=current_result_baseline_id,
        current_manual_evaluation_id=current_manual_evaluation_id,
    )


def validate_human_action_basis(
    snapshot: HumanControlSnapshot, submitted: HumanActionBasis
) -> tuple[SliceLifecycle, tuple[HandoverGate, ...], GateEvaluationRecord]:
    if snapshot.lifecycle is None:
        raise HumanActionBasisStale("Slice lifecycle is no longer available")
    if (
        submitted.slice_id != snapshot.lifecycle.slice_id
        or submitted.lifecycle_revision != snapshot.lifecycle.revision
    ):
        raise HumanActionBasisStale("lifecycle changed since the form was rendered")
    if not snapshot.gates and submitted.gate_refs:
        raise HumanActionBasisStale("the form's outgoing gates are no longer current")
    basis = _basis_for_snapshot(snapshot)
    if basis != submitted:
        raise HumanActionBasisStale("submitted Human Action Basis is stale")
    assert snapshot.lifecycle is not None and snapshot.latest is not None
    return snapshot.lifecycle, snapshot.gates, snapshot.latest


def basis_if_current(snapshot: HumanControlSnapshot) -> HumanActionBasis | None:
    try:
        return _basis_for_snapshot(snapshot)
    except HumanActionBasisStale, HumanActionRequiresEvaluation, HumanActionNotAvailable:
        return None


def timestamp_at_or_after(value: datetime, *lower_bounds: datetime, label: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")
    normalized = value.astimezone(UTC)
    for lower_bound in lower_bounds:
        if lower_bound.tzinfo is None or lower_bound.utcoffset() is None:
            raise PersistenceIntegrityError("durable timestamps must be timezone-aware")
        if normalized < lower_bound.astimezone(UTC):
            raise ValueError(f"{label} must not precede current durable evidence")
    return normalized


def _latest_evidence_time(snapshot: HumanControlSnapshot) -> datetime | None:
    evidence_times = [
        *(grant.granted_at for grant in snapshot.grants),
        *(decision.occurred_at for decision in snapshot.decisions),
    ]
    return max(evidence_times, default=None)


def _durable_action_times(
    snapshot: HumanControlSnapshot,
    lifecycle: SliceLifecycle,
    latest: GateEvaluationRecord,
) -> tuple[datetime, ...]:
    values = [lifecycle.updated_at, latest.recorded_at]
    evidence_time = _latest_evidence_time(snapshot)
    if evidence_time is not None:
        values.append(evidence_time)
    return tuple(values)


def record_successor_observation(
    connection: sqlite3.Connection,
    gates: tuple[HandoverGate, ...],
    context: HandoverContext,
    evaluation_record_id: GateEvaluationRecordId,
    recorded_at: datetime,
) -> GateEvaluationRecord:
    evaluations = evaluate_handover_gates(gates, context)
    record = GateEvaluationRecord(
        id=evaluation_record_id,
        recorded_at=recorded_at,
        gate_refs=gate_refs_for_gates(gates),
        context=context,
        evaluations=evaluations,
    )
    insert_gate_evaluation_record_from_connection(connection, record)
    return record


# Kept as a narrow patch seam for existing transaction rollback tests.
_record_successor = record_successor_observation


def successor_context(
    latest: GateEvaluationRecord,
    lifecycle: SliceLifecycle,
    gates: tuple[HandoverGate, ...],
    grants: tuple[AuthorizationGrant, ...],
    decisions: tuple[HumanGateDecision, ...],
    *,
    governance_revision: int | None = None,
) -> HandoverContext:
    return latest.context.model_copy(
        update={
            "baseline_id": gates[0].baseline_id,
            "governance_revision": (
                latest.context.governance_revision
                if governance_revision is None
                else governance_revision
            ),
            "lifecycle": lifecycle,
            "authorization_grants": grants,
            "human_decisions": decisions,
        }
    )


def _find_gate(gates: tuple[HandoverGate, ...], gate_id: HandoverGateId) -> HandoverGate:
    gate = next((item for item in gates if item.gate_id == gate_id), None)
    if gate is None:
        raise HumanActionBasisStale("selected gate is not a current outgoing gate")
    return gate


def _latest_eval_for_gate(record: GateEvaluationRecord, gate_id: HandoverGateId) -> GateEvaluation:
    evaluation = next((item for item in record.evaluations if item.gate_id == gate_id), None)
    if evaluation is None:
        raise PersistenceIntegrityError("complete gate evaluation is missing a current gate")
    return evaluation


def _human_hold_reasons(lifecycle: SliceLifecycle) -> tuple[BlockReason, ...]:
    if lifecycle.blockage.status is not BlockageStatus.BLOCKED:
        return ()
    return tuple(
        reason for reason in lifecycle.blockage.reasons if reason.code in _HUMAN_HOLD_CODES
    )


def project_human_actions(
    connection: sqlite3.Connection,
    slice_id: SliceId,
    lifecycle: SliceLifecycle | None,
    gates: tuple[HandoverGate, ...],
    latest: GateEvaluationRecord | None,
) -> HumanActionProjection:
    """Build advisory controls from the same read snapshot as Slice detail."""

    grants = load_authorization_grants_for_slice_from_connection(connection, slice_id)
    decisions = load_human_decisions_for_slice_from_connection(connection, slice_id)
    current_result, current_manual_evaluation = load_slice_1_7_subject_from_connection(
        connection, slice_id
    )
    current_result_baseline = None
    if current_result is not None:
        current_result_baseline = load_baseline_from_connection(
            connection, current_result.result_baseline_id
        )
        if current_result_baseline is None:
            raise PersistenceIntegrityError("current result Baseline is missing")
    current_gates = gates if lifecycle is not None else ()
    projected_grants = project_authorizations(grants, current_gates)
    projected_decisions = project_decisions(decisions, current_gates)
    snapshot = HumanControlSnapshot(
        lifecycle=lifecycle,
        gates=current_gates,
        latest=latest,
        grants=grants,
        decisions=decisions,
        current_result=current_result,
        current_result_baseline=current_result_baseline,
        current_manual_evaluation=current_manual_evaluation,
    )
    basis = basis_if_current(snapshot)
    actions: list[HumanAction] = []
    if lifecycle is not None and is_blockable_phase(lifecycle.phase):
        actions.extend(
            HumanAction(kind=kind)
            for kind in (HumanActionKind.BLOCK, HumanActionKind.PAUSE, HumanActionKind.DEFER)
        )
        if _human_hold_reasons(lifecycle):
            actions.append(HumanAction(kind=HumanActionKind.CLEAR_HOLD))
    if basis is not None and latest is not None and lifecycle is not None:
        for gate in current_gates:
            evaluation = _latest_eval_for_gate(latest, gate.gate_id)
            reason_codes = {reason.code for reason in evaluation.reasons}
            if reason_codes & {
                GateReasonCode.AUTHORIZATION_REQUIRED,
                GateReasonCode.AUTHORIZATION_STALE,
            }:
                actions.append(
                    HumanAction(
                        kind=HumanActionKind.AUTHORIZE,
                        gate_id=gate.gate_id,
                        gate_revision=gate.revision,
                        target_phase=gate.target_phase,
                        reasons=evaluation.reasons,
                    )
                )
            if reason_codes & _APPROVAL_REASONS or any(
                isinstance(item, HumanApprovalDecision)
                and item.gate_id == gate.gate_id
                and item.baseline_id == gate.baseline_id
                and item.gate_revision == gate.revision
                and item.lifecycle_revision == lifecycle.revision
                and item.governance_revision == latest.context.governance_revision
                for item in projected_decisions
            ):
                for kind in (HumanActionKind.APPROVE, HumanActionKind.REJECT):
                    actions.append(
                        HumanAction(
                            kind=kind,
                            gate_id=gate.gate_id,
                            gate_revision=gate.revision,
                            target_phase=gate.target_phase,
                            reasons=evaluation.reasons,
                        )
                    )
            if reason_codes & {
                GateReasonCode.HUMAN_CHOICE_REQUIRED,
                GateReasonCode.NOT_SELECTED_BY_HUMAN,
            }:
                actions.append(
                    HumanAction(
                        kind=HumanActionKind.CHOOSE_PATH,
                        gate_id=gate.gate_id,
                        gate_revision=gate.revision,
                        target_phase=gate.target_phase,
                        reasons=evaluation.reasons,
                    )
                )
            if evaluation.light is TrafficLight.GREEN:
                if gate.target_phase is LifecyclePhase.CANCELLED:
                    actions.append(
                        HumanAction(
                            kind=HumanActionKind.CANCEL,
                            gate_id=gate.gate_id,
                            gate_revision=gate.revision,
                            target_phase=gate.target_phase,
                        )
                    )
                elif gate.target_phase is not LifecyclePhase.ACCEPTED:
                    actions.append(
                        HumanAction(
                            kind=HumanActionKind.ADVANCE,
                            gate_id=gate.gate_id,
                            gate_revision=gate.revision,
                            target_phase=gate.target_phase,
                        )
                    )
    order = {kind: index for index, kind in enumerate(HumanActionKind)}
    actions.sort(key=lambda item: (order[item.kind], item.gate_id or ""))
    approvals = tuple(
        item for item in projected_decisions if isinstance(item, HumanApprovalDecision)
    )
    choice = next(
        (item for item in projected_decisions if isinstance(item, HumanChoiceDecision)), None
    )
    return HumanActionProjection(
        basis=basis,
        actions=tuple(actions),
        current_authorizations=projected_grants,
        current_approval_decisions=approvals,
        current_choice=choice,
        human_hold=() if lifecycle is None else _human_hold_reasons(lifecycle),
    )


def grant_gate_authorization(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    actor: ActorRef,
    reason: str,
    *,
    authorization_id: AuthorizationId,
    granted_at: datetime,
    successor_evaluation_record_id: GateEvaluationRecordId,
    successor_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    """Grant exact current gate permission and atomically evaluate its successor."""

    _require_human(actor)
    with _human_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        lifecycle, gates, latest = validate_human_action_basis(snapshot, basis)
        gate = _find_gate(gates, gate_id)
        if gate_id not in {item.gate_id for item in gates} or not gate.authorization_required:
            raise HumanActionNotAvailable("current gate does not require Human authorization")
        evaluation = _latest_eval_for_gate(latest, gate_id)
        if not any(
            item.code in {GateReasonCode.AUTHORIZATION_REQUIRED, GateReasonCode.AUTHORIZATION_STALE}
            for item in evaluation.reasons
        ):
            exact = tuple(
                item
                for item in snapshot.grants
                if item.gate_id == gate_id
                and item.baseline_id == gate.baseline_id
                and item.gate_revision == gate.revision
            )
            if exact:
                return latest
            raise HumanActionNotAvailable("authorization is not currently requested by this gate")

        exact_grants = tuple(
            item
            for item in snapshot.grants
            if item.gate_id == gate_id
            and item.baseline_id == gate.baseline_id
            and item.gate_revision == gate.revision
        )
        if exact_grants:
            return latest

        lower_bounds = _durable_action_times(snapshot, lifecycle, latest)
        when = timestamp_at_or_after(
            granted_at,
            *lower_bounds,
            label="granted_at",
        )
        evaluation_time = timestamp_at_or_after(
            successor_evaluation_recorded_at,
            when,
            label="successor_evaluation_recorded_at",
        )
        grant = AuthorizationGrant(
            authorization_id=authorization_id,
            slice_id=slice_id,
            baseline_id=gate.baseline_id,
            gate_id=gate.gate_id,
            gate_revision=gate.revision,
            actor=actor,
            granted_at=when,
            reason=reason,
        )
        insert_authorization_grant_from_connection(connection, grant)
        grants = project_authorizations(
            load_authorization_grants_for_slice_from_connection(connection, slice_id), gates
        )
        decisions = project_decisions(snapshot.decisions, gates)
        context = successor_context(
            latest,
            lifecycle,
            gates,
            grants,
            decisions,
            governance_revision=latest.context.governance_revision + 1,
        )
        return _record_successor(
            connection,
            gates,
            context,
            successor_evaluation_record_id,
            evaluation_time,
        )


def _record_decision(
    connection: sqlite3.Connection,
    snapshot: HumanControlSnapshot,
    basis: HumanActionBasis,
    gate_id: HandoverGateId,
    actor: ActorRef,
    reason: str,
    target: HumanApprovalValue,
    expected_current_approval_decision_id: HumanDecisionId | None,
    decision_id: HumanDecisionId,
    occurred_at: datetime,
    successor_evaluation_record_id: GateEvaluationRecordId,
    successor_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    slice_id = basis.slice_id
    lifecycle, gates, latest = validate_human_action_basis(snapshot, basis)
    gate = _find_gate(gates, gate_id)
    evaluation = _latest_eval_for_gate(latest, gate_id)
    reasons = {item.code for item in evaluation.reasons}
    previous = next(
        (
            item
            for item in project_decisions(snapshot.decisions, gates)
            if isinstance(item, HumanApprovalDecision) and item.gate_id == gate_id
        ),
        None,
    )
    actual_id = None if previous is None else previous.decision_id
    if actual_id != expected_current_approval_decision_id:
        raise HumanActionConflict("current approval changed since the form was rendered")
    previous_is_current = (
        previous is not None
        and previous.baseline_id == gate.baseline_id
        and previous.gate_revision == gate.revision
        and previous.lifecycle_revision == lifecycle.revision
        and previous.governance_revision == latest.context.governance_revision
    )
    if (
        not reasons.intersection(_APPROVAL_REASONS | {GateReasonCode.HUMAN_REJECTED})
        and not previous_is_current
    ):
        raise HumanActionNotAvailable("current gate does not require an approval decision")
    if previous_is_current and previous is not None and previous.decision is target:
        return latest

    lower_bounds = _durable_action_times(snapshot, lifecycle, latest)
    when = timestamp_at_or_after(
        occurred_at,
        *lower_bounds,
        label="occurred_at",
    )
    evaluation_time = timestamp_at_or_after(
        successor_evaluation_recorded_at,
        when,
        label="successor_evaluation_recorded_at",
    )
    decision = HumanApprovalDecision(
        decision_id=decision_id,
        slice_id=slice_id,
        baseline_id=gate.baseline_id,
        gate_id=gate.gate_id,
        gate_revision=gate.revision,
        lifecycle_revision=lifecycle.revision,
        governance_revision=latest.context.governance_revision,
        actor=actor,
        occurred_at=when,
        decision=target,
        reason=reason,
    )
    insert_human_decision_from_connection(connection, decision)
    decisions = project_decisions(
        load_human_decisions_for_slice_from_connection(connection, slice_id), gates
    )
    grants = project_authorizations(snapshot.grants, gates)
    context = successor_context(latest, lifecycle, gates, grants, decisions)
    return _record_successor(
        connection,
        gates,
        context,
        successor_evaluation_record_id,
        evaluation_time,
    )


def record_gate_approval(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    expected_current_approval_decision_id: HumanDecisionId | None,
    actor: ActorRef,
    reason: str,
    *,
    decision: HumanApprovalValue = HumanApprovalValue.APPROVE,
    decision_id: HumanDecisionId,
    occurred_at: datetime,
    successor_evaluation_record_id: GateEvaluationRecordId,
    successor_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    """Record APPROVE or REJECT with per-gate optimistic concurrency."""

    _require_human(actor)
    if basis.slice_id != slice_id:
        raise HumanActionBasisStale("basis Slice does not match route Slice")
    with _human_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        return _record_decision(
            connection,
            snapshot,
            basis,
            gate_id,
            actor,
            reason,
            decision,
            expected_current_approval_decision_id,
            decision_id,
            occurred_at,
            successor_evaluation_record_id,
            successor_evaluation_recorded_at,
        )


def record_gate_rejection(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    expected_current_approval_decision_id: HumanDecisionId | None,
    actor: ActorRef,
    reason: str,
    *,
    decision_id: HumanDecisionId,
    occurred_at: datetime,
    successor_evaluation_record_id: GateEvaluationRecordId,
    successor_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    """Record REJECT with per-gate optimistic concurrency."""

    _require_human(actor)
    if basis.slice_id != slice_id:
        raise HumanActionBasisStale("basis Slice does not match route Slice")
    with _human_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        return _record_decision(
            connection,
            snapshot,
            basis,
            gate_id,
            actor,
            reason,
            HumanApprovalValue.REJECT,
            expected_current_approval_decision_id,
            decision_id,
            occurred_at,
            successor_evaluation_record_id,
            successor_evaluation_recorded_at,
        )


def record_gate_choice(
    database: RelayDatabase,
    slice_id: SliceId,
    selected_gate_id: HandoverGateId,
    basis: HumanActionBasis,
    expected_current_choice_decision_id: HumanDecisionId | None,
    actor: ActorRef,
    reason: str,
    *,
    decision_id: HumanDecisionId,
    occurred_at: datetime,
    successor_evaluation_record_id: GateEvaluationRecordId,
    successor_evaluation_recorded_at: datetime,
) -> GateEvaluationRecord:
    """Record a selection over the exact canonical current choice gate set."""

    _require_human(actor)
    if basis.slice_id != slice_id:
        raise HumanActionBasisStale("basis Slice does not match route Slice")
    with _human_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        lifecycle, gates, latest = validate_human_action_basis(snapshot, basis)
        choice_gates = tuple(gate for gate in gates if gate.policy is HandoverPolicy.HUMAN_CHOICE)
        choice_refs = gate_refs_for_gates(choice_gates)
        if not choice_gates or selected_gate_id not in {item.gate_id for item in choice_gates}:
            raise HumanActionInvalidChoice("selected gate is outside the current Human choice set")
        current_choice = next(
            (
                item
                for item in project_decisions(snapshot.decisions, gates)
                if isinstance(item, HumanChoiceDecision)
            ),
            None,
        )
        actual_id = None if current_choice is None else current_choice.decision_id
        if actual_id != expected_current_choice_decision_id:
            raise HumanActionConflict("current choice changed since the form was rendered")
        selected = _find_gate(choice_gates, selected_gate_id)
        if (
            current_choice is not None
            and current_choice.selected_gate_id == selected_gate_id
            and current_choice.selected_gate_revision == selected.revision
            and current_choice.choice_gate_refs == choice_refs
            and current_choice.baseline_id == selected.baseline_id
            and current_choice.lifecycle_revision == lifecycle.revision
            and current_choice.governance_revision == latest.context.governance_revision
        ):
            return latest
        lower_bounds = _durable_action_times(snapshot, lifecycle, latest)
        when = timestamp_at_or_after(
            occurred_at,
            *lower_bounds,
            label="occurred_at",
        )
        evaluation_time = timestamp_at_or_after(
            successor_evaluation_recorded_at,
            when,
            label="successor_evaluation_recorded_at",
        )
        choice = HumanChoiceDecision(
            decision_id=decision_id,
            slice_id=slice_id,
            baseline_id=selected.baseline_id,
            selected_gate_id=selected.gate_id,
            selected_gate_revision=selected.revision,
            choice_gate_refs=choice_refs,
            lifecycle_revision=lifecycle.revision,
            governance_revision=latest.context.governance_revision,
            actor=actor,
            occurred_at=when,
            reason=reason,
        )
        insert_human_decision_from_connection(connection, choice)
        decisions = project_decisions(
            load_human_decisions_for_slice_from_connection(connection, slice_id), gates
        )
        context = successor_context(
            latest,
            lifecycle,
            gates,
            project_authorizations(snapshot.grants, gates),
            decisions,
        )
        return _record_successor(
            connection,
            gates,
            context,
            successor_evaluation_record_id,
            evaluation_time,
        )


def _change_human_hold(
    database: RelayDatabase,
    slice_id: SliceId,
    action: HumanActionKind,
    expected_lifecycle_revision: int,
    actor: ActorRef,
    reason: str,
    event_id: EventId,
    occurred_at: datetime,
    successor_evaluation_record_id: GateEvaluationRecordId,
    successor_evaluation_recorded_at: datetime,
) -> SliceLifecycle:
    _require_human(actor)
    if action not in {HumanActionKind.BLOCK, HumanActionKind.PAUSE, HumanActionKind.DEFER}:
        raise HumanActionNotAvailable("unsupported Human hold action")
    with _human_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        lifecycle = snapshot.lifecycle
        if lifecycle is None:
            raise HumanActionNotAvailable("Slice lifecycle is not initialized")
        if lifecycle.revision != expected_lifecycle_revision:
            raise HumanActionBasisStale("lifecycle changed since the hold form was rendered")
        if not is_blockable_phase(lifecycle.phase):
            raise HumanActionNotAvailable("current lifecycle phase cannot be blocked")
        code = f"HUMAN_{action.value}"
        hold = BlockReason(code=code, summary=reason)
        remaining = tuple(
            item for item in lifecycle.blockage.reasons if item.code not in _HUMAN_HOLD_CODES
        )
        reasons = (*remaining, hold)
        if (
            lifecycle.blockage.status is BlockageStatus.BLOCKED
            and lifecycle.blockage.reasons == reasons
        ):
            return lifecycle
        lower_bounds = [lifecycle.updated_at]
        if snapshot.latest is not None:
            lower_bounds.append(snapshot.latest.recorded_at)
        evidence_time = _latest_evidence_time(snapshot)
        if evidence_time is not None:
            lower_bounds.append(evidence_time)
        when = timestamp_at_or_after(
            occurred_at,
            *lower_bounds,
            label="occurred_at",
        )
        try:
            updated, event = set_blocked(
                lifecycle,
                reasons,
                event_id,
                actor,
                when,
                reason,
            )
        except LifecycleError as error:
            raise HumanActionNotAvailable(str(error)) from error
        valid_basis = basis_if_current(snapshot)
        persist_lifecycle_change_from_connection(connection, lifecycle.revision, updated, event)
        if valid_basis is not None and snapshot.latest is not None:
            gates = snapshot.gates
            context = successor_context(
                snapshot.latest,
                updated,
                gates,
                project_authorizations(snapshot.grants, gates),
                project_decisions(snapshot.decisions, gates),
            )
            evaluation_time = timestamp_at_or_after(
                successor_evaluation_recorded_at,
                when,
                label="successor_evaluation_recorded_at",
            )
            _record_successor(
                connection,
                gates,
                context,
                successor_evaluation_record_id,
                evaluation_time,
            )
        return updated


def set_human_hold(
    database: RelayDatabase,
    slice_id: SliceId,
    action: HumanActionKind,
    expected_lifecycle_revision: int,
    actor: ActorRef,
    reason: str,
    *,
    event_id: EventId,
    occurred_at: datetime,
    successor_evaluation_record_id: GateEvaluationRecordId,
    successor_evaluation_recorded_at: datetime,
) -> SliceLifecycle:
    """Set one indefinite Human blocker while preserving unrelated blockers."""

    return _change_human_hold(
        database,
        slice_id,
        action,
        expected_lifecycle_revision,
        actor,
        reason,
        event_id,
        occurred_at,
        successor_evaluation_record_id,
        successor_evaluation_recorded_at,
    )


def clear_human_hold(
    database: RelayDatabase,
    slice_id: SliceId,
    expected_lifecycle_revision: int,
    actor: ActorRef,
    reason: str,
    *,
    event_id: EventId,
    occurred_at: datetime,
    successor_evaluation_record_id: GateEvaluationRecordId,
    successor_evaluation_recorded_at: datetime,
) -> SliceLifecycle:
    """Remove only Human blockers; unrelated blockage reasons remain durable."""

    _require_human(actor)
    with _human_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        lifecycle = snapshot.lifecycle
        if lifecycle is None:
            raise HumanActionNotAvailable("Slice lifecycle is not initialized")
        if lifecycle.revision != expected_lifecycle_revision:
            raise HumanActionBasisStale("lifecycle changed since the resume form was rendered")
        holds = _human_hold_reasons(lifecycle)
        if not holds:
            return lifecycle
        remaining = tuple(
            item for item in lifecycle.blockage.reasons if item.code not in _HUMAN_HOLD_CODES
        )
        lower_bounds = [lifecycle.updated_at]
        if snapshot.latest is not None:
            lower_bounds.append(snapshot.latest.recorded_at)
        evidence_time = _latest_evidence_time(snapshot)
        if evidence_time is not None:
            lower_bounds.append(evidence_time)
        when = timestamp_at_or_after(
            occurred_at,
            *lower_bounds,
            label="occurred_at",
        )
        try:
            if remaining:
                updated, event = set_blocked(lifecycle, remaining, event_id, actor, when, reason)
            else:
                updated, event = clear_blockage(lifecycle, event_id, actor, when, reason)
        except LifecycleError as error:
            raise HumanActionNotAvailable(str(error)) from error
        valid_basis = basis_if_current(snapshot)
        persist_lifecycle_change_from_connection(connection, lifecycle.revision, updated, event)
        if valid_basis is not None and snapshot.latest is not None:
            gates = snapshot.gates
            context = successor_context(
                snapshot.latest,
                updated,
                gates,
                project_authorizations(snapshot.grants, gates),
                project_decisions(snapshot.decisions, gates),
            )
            evaluation_time = timestamp_at_or_after(
                successor_evaluation_recorded_at,
                when,
                label="successor_evaluation_recorded_at",
            )
            _record_successor(
                connection,
                gates,
                context,
                successor_evaluation_record_id,
                evaluation_time,
            )
        return updated


def _validate_green_action(
    snapshot: HumanControlSnapshot,
    basis: HumanActionBasis,
    gate_id: HandoverGateId,
    *,
    cancellation: bool,
) -> tuple[SliceLifecycle, tuple[HandoverGate, ...], GateEvaluationRecord, HandoverGate]:
    lifecycle, gates, latest = validate_human_action_basis(snapshot, basis)
    gate = _find_gate(gates, gate_id)
    if cancellation:
        if gate.target_phase is not LifecyclePhase.CANCELLED:
            raise HumanActionNotAvailable("CANCEL requires a current cancellation gate")
    elif gate.target_phase in {LifecyclePhase.ACCEPTED, LifecyclePhase.CANCELLED}:
        raise HumanActionNotAvailable("ADVANCE cannot execute this target phase")
    evaluations = evaluate_handover_gates(gates, latest.context)
    selected = next((item for item in evaluations if item.gate_id == gate_id), None)
    if selected is None or selected.light is not TrafficLight.GREEN:
        raise HumanActionNotAvailable("current gate evaluation is not GREEN")
    if evaluations != latest.evaluations:
        raise PersistenceIntegrityError("latest evaluation changed during current-state validation")
    return lifecycle, gates, latest, gate


def _execution_times(
    snapshot: HumanControlSnapshot,
    lifecycle: SliceLifecycle,
    latest: GateEvaluationRecord,
    evaluation_recorded_at: datetime,
    occurred_at: datetime,
) -> tuple[datetime, datetime]:
    evaluation_time = timestamp_at_or_after(
        evaluation_recorded_at,
        *_durable_action_times(snapshot, lifecycle, latest),
        label="evaluation_recorded_at",
    )
    event_time = timestamp_at_or_after(
        occurred_at,
        evaluation_time,
        label="occurred_at",
    )
    return evaluation_time, event_time


def advance_green_handover(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId,
    basis: HumanActionBasis,
    actor: ActorRef,
    reason: str,
    *,
    evaluation_record_id: GateEvaluationRecordId,
    evaluation_recorded_at: datetime,
    execution_id: ExecutionId,
    event_id: EventId,
    occurred_at: datetime,
) -> ExecutionRecord:
    """Execute exactly one currently GREEN non-terminal handover."""

    _require_human(actor)
    if basis.slice_id != slice_id:
        raise HumanActionBasisStale("basis Slice does not match route Slice")
    with _human_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        lifecycle, gates, latest, _gate = _validate_green_action(
            snapshot, basis, gate_id, cancellation=False
        )
        evaluation_time, event_time = _execution_times(
            snapshot, lifecycle, latest, evaluation_recorded_at, occurred_at
        )
        result = execute_and_persist_handover_from_connection(
            connection,
            gates,
            gate_id,
            latest.context,
            lifecycle.revision,
            evaluation_record_id,
            evaluation_time,
            execution_id,
            event_id,
            actor,
            event_time,
            reason,
        )
        return result[-1]


def cancel_slice(
    database: RelayDatabase,
    slice_id: SliceId,
    gate_id: HandoverGateId | None,
    basis: HumanActionBasis | None,
    actor: ActorRef,
    reason: str,
    *,
    evaluation_record_id: GateEvaluationRecordId,
    evaluation_recorded_at: datetime,
    execution_id: ExecutionId,
    event_id: EventId,
    occurred_at: datetime,
) -> ExecutionRecord | None:
    """Cancel only through a current GREEN gate targeting CANCELLED."""

    _require_human(actor)
    with _human_write(database) as connection:
        snapshot = load_human_control_snapshot(connection, slice_id)
        lifecycle = snapshot.lifecycle
        if lifecycle is None:
            raise HumanActionNotAvailable("Slice lifecycle is not initialized")
        if lifecycle.phase is LifecyclePhase.CANCELLED:
            return None
        if gate_id is None or basis is None:
            raise HumanActionNotAvailable("CANCEL requires a current cancellation gate and basis")
        if basis.slice_id != slice_id:
            raise HumanActionBasisStale("basis Slice does not match route Slice")
        lifecycle, gates, latest, _gate = _validate_green_action(
            snapshot, basis, gate_id, cancellation=True
        )
        evaluation_time, event_time = _execution_times(
            snapshot, lifecycle, latest, evaluation_recorded_at, occurred_at
        )
        result = execute_and_persist_handover_from_connection(
            connection,
            gates,
            gate_id,
            latest.context,
            lifecycle.revision,
            evaluation_record_id,
            evaluation_time,
            execution_id,
            event_id,
            actor,
            event_time,
            reason,
        )
        return result[-1]


__all__ = [
    "advance_green_handover",
    "cancel_slice",
    "clear_human_hold",
    "grant_gate_authorization",
    "project_human_actions",
    "record_gate_approval",
    "record_gate_choice",
    "record_gate_rejection",
    "set_human_hold",
]
