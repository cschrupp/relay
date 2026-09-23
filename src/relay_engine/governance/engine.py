"""Pure deterministic handover evaluation and governed lifecycle execution."""

from datetime import UTC, datetime

from relay_engine.domain.ids import EventId, HandoverGateId
from relay_engine.domain.references import ActorRef
from relay_engine.governance.errors import HandoverNotExecutable, InvalidGateSet
from relay_engine.governance.models import (
    AuthorizationGrant,
    ChangeSurfaceStatus,
    GateEvaluation,
    GateReason,
    GateReasonCode,
    GateReasonKind,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    HumanApprovalDecision,
    HumanApprovalValue,
    HumanChoiceDecision,
    QualityCheckStatus,
    ReviewPolicy,
    RiskStatus,
    ToolchainChangeStatus,
    TrafficLight,
)
from relay_engine.lifecycle.engine import transition_phase, validate_phase_transition
from relay_engine.lifecycle.errors import LifecycleError
from relay_engine.lifecycle.events import PhaseChanged
from relay_engine.lifecycle.models import LifecyclePhase, LifecycleValidity, SliceLifecycle

_CODE_ORDER = {code: index for index, code in enumerate(GateReasonCode)}


def _reason(code: GateReasonCode, subject: str | None = None) -> GateReason:
    return GateReason.for_code(code, subject)


def _canonical_reasons(reasons: set[GateReason]) -> tuple[GateReason, ...]:
    return tuple(
        sorted(reasons, key=lambda reason: (_CODE_ORDER[reason.code], reason.subject or ""))
    )


def _validate_gate_set(gates: tuple[HandoverGate, ...], context: HandoverContext) -> None:
    if not gates:
        raise InvalidGateSet("gate set must not be empty")
    gate_ids = tuple(gate.gate_id for gate in gates)
    slices = tuple(gate.slice_id for gate in gates)
    baselines = tuple(gate.baseline_id for gate in gates)
    if len(gate_ids) != len(set(gate_ids)):
        raise InvalidGateSet("gate IDs must be unique")
    if len(set(slices)) != 1:
        raise InvalidGateSet("all gates must describe the same slice")
    if len(set(baselines)) != 1:
        raise InvalidGateSet("mixed gate baselines are not valid")
    if slices[0] != context.lifecycle.slice_id:
        raise InvalidGateSet("gate slice must match the current lifecycle slice")


def _current_approval(gate: HandoverGate, context: HandoverContext) -> HumanApprovalDecision | None:
    for decision in context.human_decisions:
        if not isinstance(decision, HumanApprovalDecision) or decision.gate_id != gate.gate_id:
            continue
        if (
            decision.slice_id == gate.slice_id
            and decision.baseline_id == context.baseline_id
            and decision.gate_revision == gate.revision
            and decision.lifecycle_revision == context.lifecycle.revision
            and decision.governance_revision == context.governance_revision
        ):
            return decision
    return None


def _stale_approval(
    gate: HandoverGate, context: HandoverContext
) -> tuple[HumanApprovalDecision, ...]:
    return tuple(
        decision
        for decision in context.human_decisions
        if isinstance(decision, HumanApprovalDecision)
        and decision.gate_id == gate.gate_id
        and decision != _current_approval(gate, context)
    )


def _matching_grant(gate: HandoverGate, context: HandoverContext) -> AuthorizationGrant | None:
    return next(
        (grant for grant in context.authorization_grants if grant.gate_id == gate.gate_id), None
    )


def _choice_refs(gates: tuple[HandoverGate, ...]) -> tuple[GateRevisionRef, ...]:
    return tuple(
        GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision)
        for gate in sorted(
            (item for item in gates if item.policy is HandoverPolicy.HUMAN_CHOICE),
            key=lambda item: item.gate_id,
        )
    )


def _current_choice(
    gates: tuple[HandoverGate, ...], context: HandoverContext
) -> HumanChoiceDecision | None:
    decision = next(
        (item for item in context.human_decisions if isinstance(item, HumanChoiceDecision)), None
    )
    if decision is None:
        return None
    if (
        decision.slice_id == context.lifecycle.slice_id
        and decision.baseline_id == context.baseline_id
        and decision.lifecycle_revision == context.lifecycle.revision
        and decision.governance_revision == context.governance_revision
        and decision.choice_gate_refs == _choice_refs(gates)
    ):
        return decision
    return None


def _evaluate_one(
    gate: HandoverGate,
    context: HandoverContext,
    choice: HumanChoiceDecision | None,
) -> GateEvaluation:
    reasons: set[GateReason] = set()
    lifecycle = context.lifecycle

    if gate.source_phase is not lifecycle.phase:
        reasons.add(_reason(GateReasonCode.SOURCE_PHASE_MISMATCH))
    else:
        try:
            validate_phase_transition(lifecycle, gate.target_phase, gate.superseded_by_slice_id)
        except LifecycleError:
            reasons.add(_reason(GateReasonCode.INVALID_LIFECYCLE_TRANSITION))

    artifacts = set(context.available_artifact_ids)
    for artifact_id in gate.required_artifact_ids:
        if artifact_id not in artifacts:
            reasons.add(_reason(GateReasonCode.MISSING_REQUIRED_ARTIFACT, artifact_id))
    evidence = set(context.available_evidence_ids)
    for evidence_id in gate.required_evidence_ids:
        if evidence_id not in evidence:
            reasons.add(_reason(GateReasonCode.MISSING_REQUIRED_EVIDENCE, evidence_id))

    dependencies = {item.slice_id: item for item in context.dependency_lifecycles}
    for slice_id in gate.required_dependency_slice_ids:
        dependency = dependencies.get(slice_id)
        if dependency is None:
            reasons.add(_reason(GateReasonCode.DEPENDENCY_MISSING, slice_id))
        elif dependency.phase is not LifecyclePhase.ACCEPTED:
            reasons.add(_reason(GateReasonCode.DEPENDENCY_NOT_ACCEPTED, slice_id))
        elif dependency.validity is LifecycleValidity.STALE:
            reasons.add(_reason(GateReasonCode.DEPENDENCY_STALE, slice_id))

    if gate.required_evaluation_outcomes:
        if context.evaluation_outcome is None:
            reasons.add(_reason(GateReasonCode.EVALUATION_REQUIRED))
        elif context.evaluation_outcome not in gate.required_evaluation_outcomes:
            reasons.add(_reason(GateReasonCode.EVALUATION_OUTCOME_NOT_ALLOWED))

    checks = {item.key: item.status for item in context.quality_checks}
    for key in gate.required_quality_checks:
        status = checks.get(key)
        if status is None:
            reasons.add(_reason(GateReasonCode.QUALITY_CHECK_MISSING, key))
        elif status is QualityCheckStatus.FAIL:
            reasons.add(_reason(GateReasonCode.QUALITY_CHECK_FAILED, key))

    approval = _current_approval(gate, context)
    positive_decision = approval is not None and approval.decision is HumanApprovalValue.APPROVE
    if approval is not None and approval.decision is HumanApprovalValue.REJECT:
        reasons.add(_reason(GateReasonCode.HUMAN_REJECTED, approval.decision_id))

    if context.change_surface_status is ChangeSurfaceStatus.MATERIAL_DEVIATION:
        if gate.change_surface_policy is ReviewPolicy.BLOCK:
            reasons.add(_reason(GateReasonCode.CHANGE_SURFACE_BLOCKED))
        elif gate.change_surface_policy is ReviewPolicy.HUMAN_REVIEW and not positive_decision:
            reasons.add(_reason(GateReasonCode.CHANGE_SURFACE_REVIEW_REQUIRED))

    if context.risk_status is RiskStatus.FLAGGED:
        if gate.risk_policy is ReviewPolicy.BLOCK:
            reasons.add(_reason(GateReasonCode.RISK_BLOCKED))
        elif gate.risk_policy is ReviewPolicy.HUMAN_REVIEW and not positive_decision:
            reasons.add(_reason(GateReasonCode.RISK_REVIEW_REQUIRED))

    if context.toolchain_change_status is ToolchainChangeStatus.UNAUTHORIZED:
        reasons.add(_reason(GateReasonCode.UNAUTHORIZED_TOOLCHAIN_CHANGE))

    if gate.authorization_required:
        grant = _matching_grant(gate, context)
        if grant is None:
            reasons.add(_reason(GateReasonCode.AUTHORIZATION_REQUIRED))
        elif (
            grant.slice_id != gate.slice_id
            or grant.baseline_id != context.baseline_id
            or grant.gate_revision != gate.revision
        ):
            reasons.add(_reason(GateReasonCode.AUTHORIZATION_STALE, grant.authorization_id))

    positive_choice = (
        choice is not None
        and choice.selected_gate_id == gate.gate_id
        and choice.selected_gate_revision == gate.revision
    )
    approval_required = gate.policy is HandoverPolicy.HUMAN_APPROVAL and not positive_decision
    hard_stop_unresolved = gate.hard_stop and not (positive_decision or positive_choice)
    if gate.policy is HandoverPolicy.HUMAN_APPROVAL and not positive_decision:
        reasons.add(_reason(GateReasonCode.HUMAN_APPROVAL_REQUIRED))
    if hard_stop_unresolved:
        reasons.add(_reason(GateReasonCode.HARD_STOP_REQUIRES_HUMAN))

    surface_review_unresolved = (
        context.change_surface_status is ChangeSurfaceStatus.MATERIAL_DEVIATION
        and gate.change_surface_policy is ReviewPolicy.HUMAN_REVIEW
        and not positive_decision
    )
    risk_review_unresolved = (
        context.risk_status is RiskStatus.FLAGGED
        and gate.risk_policy is ReviewPolicy.HUMAN_REVIEW
        and not positive_decision
    )
    if (
        approval_required
        or hard_stop_unresolved
        or surface_review_unresolved
        or risk_review_unresolved
    ):
        stale_approvals = _stale_approval(gate, context)
        reasons.update(
            _reason(GateReasonCode.HUMAN_DECISION_STALE, item.decision_id)
            for item in stale_approvals
        )

    if gate.policy is HandoverPolicy.HUMAN_CHOICE:
        if choice is None:
            reasons.add(_reason(GateReasonCode.HUMAN_CHOICE_REQUIRED))
            stale_choices = tuple(
                item for item in context.human_decisions if isinstance(item, HumanChoiceDecision)
            )
            reasons.update(
                _reason(GateReasonCode.HUMAN_DECISION_STALE, item.decision_id)
                for item in stale_choices
            )
        elif (
            choice.selected_gate_id != gate.gate_id
            or choice.selected_gate_revision != gate.revision
        ):
            if not any(reason.kind is GateReasonKind.BLOCKING for reason in reasons):
                reasons.add(_reason(GateReasonCode.NOT_SELECTED_BY_HUMAN, choice.selected_gate_id))

    canonical = _canonical_reasons(reasons)
    light = (
        TrafficLight.RED
        if any(reason.kind is GateReasonKind.BLOCKING for reason in canonical)
        else TrafficLight.YELLOW
        if canonical
        else TrafficLight.GREEN
    )
    return GateEvaluation(
        gate_id=gate.gate_id,
        gate_revision=gate.revision,
        slice_id=gate.slice_id,
        baseline_id=context.baseline_id,
        lifecycle_revision=lifecycle.revision,
        governance_revision=context.governance_revision,
        target_phase=gate.target_phase,
        light=light,
        reasons=canonical,
    )


def evaluate_handover_gates(
    gates: tuple[HandoverGate, ...], context: HandoverContext
) -> tuple[GateEvaluation, ...]:
    """Evaluate the complete outgoing gate set without I/O or generated state."""

    _validate_gate_set(gates, context)
    ordered_gates = tuple(sorted(gates, key=lambda item: item.gate_id))
    if ordered_gates[0].baseline_id != context.baseline_id:
        return tuple(
            GateEvaluation(
                gate_id=gate.gate_id,
                gate_revision=gate.revision,
                slice_id=gate.slice_id,
                baseline_id=context.baseline_id,
                lifecycle_revision=context.lifecycle.revision,
                governance_revision=context.governance_revision,
                target_phase=gate.target_phase,
                light=TrafficLight.RED,
                reasons=(_reason(GateReasonCode.BASELINE_MISMATCH),),
            )
            for gate in ordered_gates
        )

    choice = _current_choice(gates, context)
    results = [_evaluate_one(gate, context, choice) for gate in ordered_gates]
    green_indices = [
        index for index, result in enumerate(results) if result.light is TrafficLight.GREEN
    ]
    if len(green_indices) > 1:
        for index in green_indices:
            conflicting = {
                _reason(GateReasonCode.MULTIPLE_EXECUTABLE_PATHS, results[other].gate_id)
                for other in green_indices
                if other != index
            }
            reasons = _canonical_reasons(set(results[index].reasons) | conflicting)
            results[index] = results[index].model_copy(
                update={"light": TrafficLight.RED, "reasons": reasons}
            )
    return tuple(results)


def execute_handover(
    gates: tuple[HandoverGate, ...],
    selected_gate_id: HandoverGateId,
    context: HandoverContext,
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[SliceLifecycle, PhaseChanged, GateEvaluation]:
    """Re-evaluate governance and execute exactly one currently GREEN handover."""

    evaluations = evaluate_handover_gates(gates, context)
    gate = next((item for item in gates if item.gate_id == selected_gate_id), None)
    evaluation = next((item for item in evaluations if item.gate_id == selected_gate_id), None)
    if gate is None or evaluation is None or evaluation.light is not TrafficLight.GREEN:
        raise HandoverNotExecutable("selected handover must exist and be GREEN")
    execution_time = _aware_utc(occurred_at)
    if gate.authorization_required:
        grant = _matching_grant(gate, context)
        if grant is None or execution_time < grant.granted_at:
            raise HandoverNotExecutable("execution cannot predate required authorization")
    approval = _current_approval(gate, context)
    if (
        approval is not None
        and (
            gate.policy is HandoverPolicy.HUMAN_APPROVAL
            or gate.hard_stop
            or (
                context.change_surface_status is ChangeSurfaceStatus.MATERIAL_DEVIATION
                and gate.change_surface_policy is ReviewPolicy.HUMAN_REVIEW
            )
            or (
                context.risk_status is RiskStatus.FLAGGED
                and gate.risk_policy is ReviewPolicy.HUMAN_REVIEW
            )
        )
        and execution_time < approval.occurred_at
    ):
        raise HandoverNotExecutable("execution cannot predate required human approval")
    if gate.policy is HandoverPolicy.HUMAN_CHOICE:
        choice = _current_choice(gates, context)
        if choice is None or execution_time < choice.occurred_at:
            raise HandoverNotExecutable("execution cannot predate required human choice")
    lifecycle, event = transition_phase(
        context.lifecycle,
        gate.target_phase,
        event_id,
        actor,
        execution_time,
        reason,
        gate.superseded_by_slice_id,
    )
    return lifecycle, event, evaluation


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise HandoverNotExecutable("execution time must be timezone-aware")
    return value.astimezone(UTC)
