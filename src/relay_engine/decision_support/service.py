"""Pure deterministic projection and Q&A over one already-loaded Slice snapshot."""

from collections.abc import Iterable
from enum import StrEnum

from relay_engine.board.models import EvaluationBasisStatus
from relay_engine.decision_support.models import (
    DecisionAnswer,
    DecisionBasisApplicability,
    DecisionBasisCompleteness,
    DecisionBasisComponent,
    DecisionBasisComponentKind,
    DecisionBasisFreshness,
    DecisionBasisIdentityV1,
    DecisionCard,
    DecisionCardState,
    DecisionChoice,
    DecisionKind,
    DecisionProposedOutcome,
    DecisionQuestionKind,
    DecisionSourceKind,
    DecisionSourceRef,
    DecisionStatement,
    DecisionStatementBasis,
    DecisionSupportProjection,
    GateApprovalChoice,
    GateAuthorizationChoice,
    GatePathChoice,
    PendingDecisionRef,
    TechnicalAcceptanceChoice,
)
from relay_engine.governance.models import (
    AuthorizationGrant,
    GateRevisionRef,
    HandoverGate,
    HumanApprovalDecision,
    HumanChoiceDecision,
)
from relay_engine.human_control.models import (
    HumanAction,
    HumanActionBasis,
    HumanActionKind,
    HumanActionProjection,
)
from relay_engine.lifecycle.models import LifecyclePhase, SliceLifecycle
from relay_engine.manual_evaluation.models import (
    ManualEvaluationActionKind,
    ManualEvaluationProjection,
    ManualEvaluationRecord,
    SliceResultRecord,
)
from relay_engine.persistence import PersistenceIntegrityError
from relay_engine.persistence.records import ExecutionRecord, GateEvaluationRecord
from relay_engine.project_slice.models import SliceDefinitionSnapshot

_CARD_ORDER = {
    DecisionKind.GATE_AUTHORIZATION: 0,
    DecisionKind.GATE_APPROVAL: 1,
    DecisionKind.GATE_PATH_CHOICE: 2,
    DecisionKind.TECHNICAL_ACCEPTANCE: 3,
}


def _source(kind: DecisionSourceKind, stable_ref: str, label: str) -> DecisionSourceRef:

    return DecisionSourceRef(kind=kind, stable_ref=stable_ref, label=label)


def _statement(
    text: str,
    source_refs: tuple[DecisionSourceRef, ...],
    basis: DecisionStatementBasis = DecisionStatementBasis.CANONICAL_FACT,
) -> DecisionStatement:

    return DecisionStatement(text=text, basis=basis, source_refs=source_refs)


def _decision_why(
    *,
    state: DecisionCardState,
    pending_reason: str,
    recorded_text: str | None,
    recorded_id: str | None,
    refs: tuple[DecisionSourceRef, ...],
) -> DecisionStatement:
    if state is DecisionCardState.PENDING_REQUIRED:
        return _statement(f"Human decision required: {pending_reason}", refs)
    decision_refs = tuple(
        item
        for item in refs
        if item.kind is DecisionSourceKind.HUMAN_DECISION and item.stable_ref == recorded_id
    )
    if not decision_refs:
        raise PersistenceIntegrityError(
            "recorded revisable decision is missing its exact Human decision source"
        )
    return _statement(
        f"Current Human decision {recorded_text} ({recorded_id}) is recorded. "
        "A replacement decision remains available before the governed transition or control "
        "ceases to be revisable.",
        decision_refs,
    )


def _gate_ref(gate: HandoverGate) -> GateRevisionRef:

    return GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision)


def _current_approval(
    projection: HumanActionProjection, gate: HandoverGate, basis: HumanActionBasis
) -> HumanApprovalDecision | None:

    expected_identity = next(
        (item for item in basis.current_approval_decision_ids if item.gate_id == gate.gate_id),
        None,
    )

    for decision in projection.current_approval_decisions:
        if (
            expected_identity is not None
            and decision.decision_id == expected_identity.decision_id
            and decision.gate_id == gate.gate_id
            and decision.baseline_id == gate.baseline_id
            and decision.gate_revision == gate.revision
            and decision.lifecycle_revision == basis.lifecycle_revision
            and decision.governance_revision == basis.governance_revision
        ):
            return decision

    return None


def _sources(
    definition: SliceDefinitionSnapshot,
    lifecycle: SliceLifecycle | None,
    gate: HandoverGate,
    latest: GateEvaluationRecord | None,
    result: SliceResultRecord | None,
    evaluation: ManualEvaluationRecord | None,
    executions: tuple[ExecutionRecord, ...],
    decisions: Iterable[object],
    authorizations: Iterable[AuthorizationGrant] = (),
    artifact_ids: Iterable[str] = (),
) -> tuple[DecisionSourceRef, ...]:

    refs = [
        _source(
            DecisionSourceKind.SLICE_DEFINITION,
            f"{definition.value.id}@r{definition.definition_revision}",
            f"Slice definition revision {definition.definition_revision}",
        ),
        _source(
            DecisionSourceKind.HANDOVER_GATE,
            f"{gate.gate_id}@r{gate.revision}",
            f"Gate {gate.key} revision {gate.revision}",
        ),
        _source(DecisionSourceKind.BASELINE, gate.baseline_id, "Gate Baseline"),
    ]

    if lifecycle is not None:
        refs.append(
            _source(
                DecisionSourceKind.LIFECYCLE,
                f"{lifecycle.slice_id}@r{lifecycle.revision}",
                f"Lifecycle {lifecycle.phase.value} revision {lifecycle.revision}",
            )
        )

    if latest is not None:
        refs.append(
            _source(
                DecisionSourceKind.GATE_EVALUATION,
                latest.id,
                "Current gate evaluation record",
            )
        )

    if result is not None:
        refs.append(_source(DecisionSourceKind.SLICE_RESULT, result.result_id, "Current result"))

    if evaluation is not None:
        refs.append(
            _source(
                DecisionSourceKind.MANUAL_EVALUATION,
                evaluation.evaluation_id,
                "Current manual evaluation",
            )
        )

    evidence_ids: set[str] = set() if latest is None else set(latest.context.available_evidence_ids)

    if evaluation is not None:
        evidence_ids.update(evaluation.evidence_ids)

    refs.extend(
        _source(DecisionSourceKind.EVIDENCE, item, f"Evidence {item}")
        for item in sorted(evidence_ids)
    )

    refs.extend(
        _source(DecisionSourceKind.ARTIFACT, item, f"Required artifact {item}")
        for item in sorted(set(artifact_ids))
    )

    refs.extend(
        _source(DecisionSourceKind.AUTHORIZATION, item.authorization_id, "Current authorization")
        for item in authorizations
        if item.gate_id == gate.gate_id and item.gate_revision == gate.revision
    )

    refs.extend(
        _source(DecisionSourceKind.HUMAN_DECISION, item.decision_id, "Current Human decision")
        for item in decisions
        if isinstance(item, (HumanApprovalDecision, HumanChoiceDecision))
    )

    refs.extend(
        _source(DecisionSourceKind.EXECUTION, item.execution_id, "Governed execution")
        for item in executions
    )

    unique_refs = {(item.kind.value, item.stable_ref, item.label): item for item in refs}

    return tuple(unique_refs[key] for key in sorted(unique_refs))


def _component(
    kind: DecisionBasisComponentKind,
    applicability: DecisionBasisApplicability,
    required: bool,
    summary: str,
    sources: tuple[DecisionSourceRef, ...],
    freshness: DecisionBasisFreshness = DecisionBasisFreshness.CURRENT,
) -> DecisionBasisComponent:

    return DecisionBasisComponent(
        kind=kind,
        applicability=applicability,
        freshness=freshness,
        required=required,
        summary=summary,
        source_refs=sources,
    )


def _completeness(components: tuple[DecisionBasisComponent, ...]) -> DecisionBasisCompleteness:

    required = tuple(item for item in components if item.required)

    if any(item.freshness is DecisionBasisFreshness.STALE for item in required):
        return DecisionBasisCompleteness.STALE

    if any(
        item.applicability is DecisionBasisApplicability.UNKNOWN
        or item.freshness is DecisionBasisFreshness.UNKNOWN
        for item in required
    ):
        return DecisionBasisCompleteness.UNKNOWN

    if any(item.applicability is DecisionBasisApplicability.MISSING_REQUIRED for item in required):
        return DecisionBasisCompleteness.INCOMPLETE

    return DecisionBasisCompleteness.COMPLETE


def _gate_components(
    kind: DecisionKind,
    gate: HandoverGate,
    refs: tuple[DecisionSourceRef, ...],
    latest: GateEvaluationRecord | None,
    evaluation: ManualEvaluationRecord | None,
    evaluation_status: EvaluationBasisStatus,
) -> tuple[DecisionBasisComponent, ...]:

    requirements = {
        DecisionKind.GATE_AUTHORIZATION: {
            DecisionBasisComponentKind.DECISION_SUBJECT,
            DecisionBasisComponentKind.CURRENT_STATE,
            DecisionBasisComponentKind.PROPOSED_STATE,
            DecisionBasisComponentKind.AUTHORITY_BASIS,
            DecisionBasisComponentKind.POLICY_OR_GATE_BASIS,
            DecisionBasisComponentKind.EVALUATION,
            DecisionBasisComponentKind.RISKS_AND_BLOCKERS,
            DecisionBasisComponentKind.GOVERNANCE_REQUIREMENTS,
            DecisionBasisComponentKind.CONSEQUENCES,
            DecisionBasisComponentKind.SOURCE_PROVENANCE,
        },
        DecisionKind.GATE_APPROVAL: {
            DecisionBasisComponentKind.DECISION_SUBJECT,
            DecisionBasisComponentKind.CURRENT_STATE,
            DecisionBasisComponentKind.PROPOSED_STATE,
            DecisionBasisComponentKind.POLICY_OR_GATE_BASIS,
            DecisionBasisComponentKind.EVALUATION,
            DecisionBasisComponentKind.RISKS_AND_BLOCKERS,
            DecisionBasisComponentKind.GOVERNANCE_REQUIREMENTS,
            DecisionBasisComponentKind.CONSEQUENCES,
            DecisionBasisComponentKind.SOURCE_PROVENANCE,
        },
        DecisionKind.GATE_PATH_CHOICE: {
            DecisionBasisComponentKind.DECISION_SUBJECT,
            DecisionBasisComponentKind.CURRENT_STATE,
            DecisionBasisComponentKind.PROPOSED_STATE,
            DecisionBasisComponentKind.POLICY_OR_GATE_BASIS,
            DecisionBasisComponentKind.EVALUATION,
            DecisionBasisComponentKind.RISKS_AND_BLOCKERS,
            DecisionBasisComponentKind.GOVERNANCE_REQUIREMENTS,
            DecisionBasisComponentKind.CONSEQUENCES,
            DecisionBasisComponentKind.SOURCE_PROVENANCE,
        },
    }[kind]

    if gate.required_artifact_ids:
        artifact_ids: set[str] = (
            set() if latest is None else set(latest.context.available_artifact_ids)
        )

        missing = tuple(item for item in gate.required_artifact_ids if item not in artifact_ids)

        artifact_applicability = (
            DecisionBasisApplicability.MISSING_REQUIRED
            if missing
            else DecisionBasisApplicability.REQUIRED_PRESENT
        )

        artifact_summary = (
            "Missing required artifacts: " + ", ".join(missing)
            if missing
            else "All gate-required artifacts are current in the exact evaluation basis."
        )

    else:
        artifact_applicability = DecisionBasisApplicability.NOT_APPLICABLE

        artifact_summary = "This gate has no required artifact basis."

    if gate.required_evidence_ids:
        evidence_ids: set[str] = (
            set() if latest is None else set(latest.context.available_evidence_ids)
        )

        missing_evidence = tuple(
            item for item in gate.required_evidence_ids if item not in evidence_ids
        )

        evidence_applicability = (
            DecisionBasisApplicability.MISSING_REQUIRED
            if missing_evidence
            else DecisionBasisApplicability.REQUIRED_PRESENT
        )

        evidence_summary = (
            "Missing required evidence: " + ", ".join(missing_evidence)
            if missing_evidence
            else "All gate-required Evidence IDs are current in the exact evaluation basis."
        )

    else:
        evidence_applicability = DecisionBasisApplicability.NOT_APPLICABLE

        evidence_summary = "No Evidence IDs are required by this gate."

    current = evaluation_status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS

    freshness = (
        DecisionBasisFreshness.CURRENT
        if current
        else DecisionBasisFreshness.STALE
        if evaluation_status is EvaluationBasisStatus.STALE_DURABLE_BASIS
        else DecisionBasisFreshness.UNKNOWN
    )

    components: list[DecisionBasisComponent] = []

    summaries = {
        DecisionBasisComponentKind.DECISION_SUBJECT: "Exact current Slice and gate decision subject.",  # noqa: E501
        DecisionBasisComponentKind.CURRENT_STATE: "Current lifecycle and current Human decision state.",  # noqa: E501
        DecisionBasisComponentKind.PROPOSED_STATE: "Exact governed gate target phase.",
        DecisionBasisComponentKind.AUTHORITY_BASIS: "Existing Human Authority command is available.",  # noqa: E501
        DecisionBasisComponentKind.POLICY_OR_GATE_BASIS: f"Gate policy is {gate.policy.value}; hard_stop={gate.hard_stop}; authorization_required={gate.authorization_required}.",  # noqa: E501
        DecisionBasisComponentKind.EVALUATION: "Current exact gate evaluation is present."
        if current
        else "Current exact gate evaluation is unavailable or stale.",
        DecisionBasisComponentKind.RISKS_AND_BLOCKERS: "Current gate reasons and evaluation facts are projected below.",  # noqa: E501
        DecisionBasisComponentKind.GOVERNANCE_REQUIREMENTS: "Exact requirements from the current HandoverGate are projected below.",  # noqa: E501
        DecisionBasisComponentKind.CONSEQUENCES: "Existing command semantics are described without executing them.",  # noqa: E501
        DecisionBasisComponentKind.SOURCE_PROVENANCE: "Exact source references are listed below.",
    }

    for component_kind in DecisionBasisComponentKind:
        if component_kind is DecisionBasisComponentKind.DESIGN_OR_SCOPE_BASIS:
            components.append(
                _component(
                    component_kind,
                    artifact_applicability,
                    bool(gate.required_artifact_ids),
                    artifact_summary,
                    tuple(item for item in refs if item.kind is DecisionSourceKind.ARTIFACT),
                    freshness
                    if gate.required_artifact_ids
                    else DecisionBasisFreshness.NOT_APPLICABLE,
                )
            )

        elif component_kind is DecisionBasisComponentKind.EVIDENCE:
            components.append(
                _component(
                    component_kind,
                    evidence_applicability,
                    bool(gate.required_evidence_ids),
                    evidence_summary,
                    tuple(item for item in refs if item.kind is DecisionSourceKind.EVIDENCE),
                    freshness
                    if gate.required_evidence_ids
                    else DecisionBasisFreshness.NOT_APPLICABLE,
                )
            )

        elif component_kind is DecisionBasisComponentKind.CHANGE_OR_RESULT_BASIS:
            components.append(
                _component(
                    component_kind,
                    DecisionBasisApplicability.NOT_APPLICABLE,
                    False,
                    "This gate decision is not a technical result decision.",
                    refs,
                    DecisionBasisFreshness.NOT_APPLICABLE,
                )
            )

        elif (
            component_kind is DecisionBasisComponentKind.AUTHORITY_BASIS
            and component_kind not in requirements
        ):
            components.append(
                _component(
                    component_kind,
                    DecisionBasisApplicability.OPTIONAL_PRESENT,
                    False,
                    "Existing Human action basis is available.",
                    refs,
                )
            )

        elif component_kind not in requirements:
            components.append(
                _component(
                    component_kind,
                    DecisionBasisApplicability.NOT_APPLICABLE,
                    False,
                    "Not required for this decision kind.",
                    refs,
                    DecisionBasisFreshness.NOT_APPLICABLE,
                )
            )

        else:
            components.append(
                _component(
                    component_kind,
                    DecisionBasisApplicability.REQUIRED_PRESENT,
                    True,
                    summaries[component_kind],
                    refs,
                    freshness
                    if component_kind is DecisionBasisComponentKind.EVALUATION
                    else DecisionBasisFreshness.CURRENT,
                )
            )

    return tuple(components)


def _technical_components(
    refs: tuple[DecisionSourceRef, ...],
    gate: HandoverGate,
    latest: GateEvaluationRecord | None,
    evaluation_status: EvaluationBasisStatus,
    result: SliceResultRecord | None,
    evaluation: ManualEvaluationRecord | None,
) -> tuple[DecisionBasisComponent, ...]:
    values: list[DecisionBasisComponent] = []

    for kind in DecisionBasisComponentKind:
        if kind is DecisionBasisComponentKind.EVIDENCE:
            present = evaluation is not None and bool(evaluation.evidence_ids)

            applicability = (
                DecisionBasisApplicability.REQUIRED_PRESENT
                if present
                else DecisionBasisApplicability.MISSING_REQUIRED
            )

            text = (
                "Current manual evaluation binds exact Evidence IDs."
                if present
                else "Required technical Evidence is missing."
            )

            required = True

        elif kind is DecisionBasisComponentKind.CHANGE_OR_RESULT_BASIS:
            present = (
                result is not None
                and evaluation is not None
                and evaluation.result_id == result.result_id
            )

            applicability = (
                DecisionBasisApplicability.REQUIRED_PRESENT
                if present
                else DecisionBasisApplicability.MISSING_REQUIRED
            )

            text = (
                "Exact current result and evaluation subject are bound."
                if present
                else "Exact current result/evaluation subject is missing."
            )

            required = True

        elif kind is DecisionBasisComponentKind.DESIGN_OR_SCOPE_BASIS:
            required_ids = gate.required_artifact_ids
            available_ids: set[str] = (
                set() if latest is None else set(latest.context.available_artifact_ids)
            )
            missing_ids = tuple(item for item in required_ids if item not in available_ids)
            applicability = (
                DecisionBasisApplicability.NOT_APPLICABLE
                if not required_ids
                else DecisionBasisApplicability.MISSING_REQUIRED
                if missing_ids
                else DecisionBasisApplicability.REQUIRED_PRESENT
            )
            text = (
                "No current gate policy requires design/scope artifacts."
                if not required_ids
                else "Missing required artifacts: " + ", ".join(missing_ids)
                if missing_ids
                else "All required design/scope artifacts are present in the exact current basis."
            )
            required = bool(required_ids)

        elif kind is DecisionBasisComponentKind.AUTHORITY_BASIS:
            applicability = DecisionBasisApplicability.REQUIRED_PRESENT

            text = "Existing Human Authority action basis is current."

            required = True

        elif kind is DecisionBasisComponentKind.EVALUATION:
            applicability = (
                DecisionBasisApplicability.REQUIRED_PRESENT
                if evaluation
                else DecisionBasisApplicability.MISSING_REQUIRED
            )

            text = (
                "Current evaluator outcome and findings are available."
                if evaluation
                else "Required manual evaluation is missing."
            )

            required = True

        elif kind is DecisionBasisComponentKind.GOVERNANCE_REQUIREMENTS:
            applicability = DecisionBasisApplicability.REQUIRED_PRESENT

            text = "Exact technical acceptance gate requirements are projected below."

            required = True

        else:
            applicability = DecisionBasisApplicability.REQUIRED_PRESENT

            text = "Exact technical decision basis is available."

            required = True

        component_refs = (
            tuple(item for item in refs if item.kind is DecisionSourceKind.ARTIFACT)
            if kind is DecisionBasisComponentKind.DESIGN_OR_SCOPE_BASIS
            else refs
        )
        freshness = (
            DecisionBasisFreshness.NOT_APPLICABLE
            if not required
            else DecisionBasisFreshness.CURRENT
            if evaluation_status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS
            else DecisionBasisFreshness.STALE
            if evaluation_status is EvaluationBasisStatus.STALE_DURABLE_BASIS
            else DecisionBasisFreshness.UNKNOWN
        )
        values.append(_component(kind, applicability, required, text, component_refs, freshness))

    return tuple(values)


def _governance_statements(
    gate: HandoverGate, refs: tuple[DecisionSourceRef, ...]
) -> tuple[DecisionStatement, ...]:

    values = [
        f"policy={gate.policy.value}",
        f"hard_stop={str(gate.hard_stop).lower()}",
        f"authorization_required={str(gate.authorization_required).lower()}",
        f"change_surface_policy={gate.change_surface_policy.value}",
        f"risk_policy={gate.risk_policy.value}",
    ]

    for label, items in (
        ("required_artifact_ids", gate.required_artifact_ids),
        ("required_evidence_ids", gate.required_evidence_ids),
        ("required_dependency_slice_ids", gate.required_dependency_slice_ids),
        ("required_evaluation_outcomes", gate.required_evaluation_outcomes),
        ("required_quality_checks", gate.required_quality_checks),
    ):
        rendered_items = tuple(
            item.value if isinstance(item, StrEnum) else str(item) for item in items
        )

        values.append(f"{label}={', '.join(rendered_items) or 'none'}")

    return tuple(_statement(value, refs) for value in values)


def _gate_reasons(gate: HandoverGate, latest: GateEvaluationRecord | None):

    if latest is None:
        return ()

    evaluation = next((item for item in latest.evaluations if item.gate_id == gate.gate_id), None)

    return () if evaluation is None else evaluation.reasons


def _gate_choice(
    command: HumanActionKind,
    ref: GateRevisionRef,
    basis: HumanActionBasis,
    approval: HumanApprovalDecision | None,
) -> DecisionChoice:

    if command is HumanActionKind.AUTHORIZE:
        return GateAuthorizationChoice(command=command, gate_ref=ref, human_action_basis=basis)

    if command is HumanActionKind.APPROVE:
        return GateApprovalChoice(
            command=HumanActionKind.APPROVE,
            gate_ref=ref,
            human_action_basis=basis,
            expected_current_approval_decision_id=(
                None if approval is None else approval.decision_id
            ),
        )

    if command is HumanActionKind.REJECT:
        return GateApprovalChoice(
            command=HumanActionKind.REJECT,
            gate_ref=ref,
            human_action_basis=basis,
            expected_current_approval_decision_id=(
                None if approval is None else approval.decision_id
            ),
        )

    raise PersistenceIntegrityError("unsupported action was included in a Decision Card")


def _build_gate_card(
    *,
    kind: DecisionKind,
    gate: HandoverGate,
    definition: SliceDefinitionSnapshot,
    lifecycle: SliceLifecycle | None,
    latest: GateEvaluationRecord | None,
    evaluation_status: EvaluationBasisStatus,
    basis: HumanActionBasis,
    human_actions: HumanActionProjection,
    executions: tuple[ExecutionRecord, ...],
    actions: tuple[HumanAction, ...],
) -> DecisionCard:

    ref = _gate_ref(gate)

    approval = (
        _current_approval(human_actions, gate, basis)
        if kind is DecisionKind.GATE_APPROVAL
        else None
    )

    current_choice = human_actions.current_choice if kind is DecisionKind.GATE_PATH_CHOICE else None

    eligible: tuple[GateRevisionRef, ...] = ()

    if kind is DecisionKind.GATE_PATH_CHOICE:
        eligible = tuple(
            sorted(
                (_gate_ref(item) for item in _action_gates(actions, (gate,))),
                key=lambda item: (item.gate_id, item.gate_revision),
            )
        )

        choice = human_actions.current_choice

        if choice is not None and (
            choice.choice_gate_refs != eligible
            or GateRevisionRef(
                gate_id=choice.selected_gate_id, gate_revision=choice.selected_gate_revision
            )
            not in eligible
        ):
            current_choice = None

    state = (
        DecisionCardState.RECORDED_REVISABLE
        if approval is not None or current_choice is not None
        else DecisionCardState.PENDING_REQUIRED
    )

    identity = DecisionBasisIdentityV1(
        decision_kind=kind,
        slice_id=definition.value.id,
        gate_ref=None if kind is DecisionKind.GATE_PATH_CHOICE else ref,
        target_phase=None if kind is DecisionKind.GATE_PATH_CHOICE else gate.target_phase,
        human_action_basis=basis,
        decision_state=state,
        expected_current_approval_decision_id=None if approval is None else approval.decision_id,
        expected_current_choice_decision_id=None
        if current_choice is None
        else current_choice.decision_id,
        eligible_choice_gate_refs=eligible,
    )

    pending = PendingDecisionRef(identity=identity, basis_digest=identity.digest())

    decisions = tuple(item for item in (approval, current_choice) if item is not None)

    refs = _sources(
        definition,
        lifecycle,
        gate,
        latest,
        None,
        None,
        executions,
        decisions,
        human_actions.current_authorizations,
        gate.required_artifact_ids,
    )

    components = _gate_components(kind, gate, refs, latest, None, evaluation_status)

    gate_reason_values = _gate_reasons(gate, latest)

    reasons = tuple(
        _statement(
            f"{item.kind.value}: {item.code.value}"
            f"{'' if item.subject is None else f' ({item.subject})'}",
            refs,
        )
        for item in gate_reason_values
    )

    lifecycle_blockers = tuple(
        _statement(f"Lifecycle blockage {item.code}: {item.summary}", refs)
        for item in (() if lifecycle is None else lifecycle.blockage.reasons)
    )

    human_holds = tuple(
        _statement(f"Human hold {item.code}: {item.summary}", refs)
        for item in human_actions.human_hold
    )

    governed_risk: tuple[DecisionStatement, ...] = ()

    if latest is not None and evaluation_status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS:
        governed_risk = (
            _statement(f"Recorded risk status: {latest.context.risk_status.value}", refs),
            _statement(
                f"Recorded change-surface status: {latest.context.change_surface_status.value}",
                refs,
            ),
            _statement(
                f"Recorded toolchain-change status: {latest.context.toolchain_change_status.value}",
                refs,
            ),
        )

    risks = reasons + lifecycle_blockers + human_holds + governed_risk

    blockers = (
        tuple(
            item
            for item, reason in zip(reasons, gate_reason_values, strict=True)
            if reason.kind.value == "BLOCKING"
        )
        + lifecycle_blockers
        + human_holds
    )

    governance = _governance_statements(gate, refs)

    available_evidence_ids: set[str] = (
        set() if latest is None else set(latest.context.available_evidence_ids)
    )

    evidence_statements = tuple(
        _statement(
            f"Current Evidence ID: {item}",
            tuple(
                ref
                for ref in refs
                if ref.kind is DecisionSourceKind.EVIDENCE and ref.stable_ref == item
            ),
        )
        for item in gate.required_evidence_ids
        if item in available_evidence_ids
    )

    outcomes = (
        DecisionProposedOutcome(
            gate_ref=ref,
            target_phase=gate.target_phase,
            label=f"{gate.key}: {gate.target_phase.value}",
        ),
    )

    current_text = (
        f"Lifecycle is {lifecycle.phase.value} at revision {lifecycle.revision}."
        if lifecycle
        else "No lifecycle record exists."
    )

    why = (
        "; ".join(
            f"{item.code.value}{'' if item.subject is None else f' ({item.subject})'}"
            for item in gate_reason_values
        )
        or f"Current {gate.policy.value} gate exposes this Human decision."
    )

    command_choices = tuple(
        _gate_choice(action.kind, ref, basis, approval)
        for action in actions
        if action.gate_id == gate.gate_id
        and action.kind
        in {HumanActionKind.APPROVE, HumanActionKind.REJECT, HumanActionKind.AUTHORIZE}
    )

    consequences = (
        _statement(
            "Records the exact Human approval or rejection and reevaluates governed state; "
            "it does not itself advance lifecycle or promote a result."
            if kind is DecisionKind.GATE_APPROVAL
            else "Records the exact selected gate choice and reevaluates; "
            "it does not execute the handover itself."
            if kind is DecisionKind.GATE_PATH_CHOICE
            else "Records the exact current authorization grant and reevaluates; "
            "authorization does not itself advance lifecycle.",
            refs,
        ),
    )

    return DecisionCard(
        decision=pending,
        title={
            DecisionKind.GATE_AUTHORIZATION: "Authorize handover",
            DecisionKind.GATE_APPROVAL: "Approve or reject handover",
            DecisionKind.GATE_PATH_CHOICE: "Choose a handover path",
        }[kind],
        state=state,
        current_recorded_decision=(
            approval.decision.value
            if approval is not None
            else (
                None
                if current_choice is None
                else f"Selected {current_choice.selected_gate_id}@r{current_choice.selected_gate_revision}"  # noqa: E501
            )
        ),
        why_required=_decision_why(
            state=state,
            pending_reason=why,
            recorded_text=(
                approval.decision.value
                if approval is not None
                else (
                    None
                    if current_choice is None
                    else f"selected {current_choice.selected_gate_id}@r"
                    f"{current_choice.selected_gate_revision}"
                )
            ),
            recorded_id=(
                approval.decision_id
                if approval is not None
                else None
                if current_choice is None
                else current_choice.decision_id
            ),
            refs=refs,
        ),
        current_state=_statement(current_text, refs),
        proposed_outcomes=outcomes,
        choices=command_choices,
        components=components,
        evidence=evidence_statements,
        risks=risks,
        blocking_findings=blockers,
        unknowns=tuple(
            _statement(item.summary, item.source_refs, DecisionStatementBasis.UNKNOWN)
            for item in components
            if item.applicability is DecisionBasisApplicability.UNKNOWN
        ),
        consequences=consequences,
        governance_requirements=governance,
        source_refs=refs,
        completeness=_completeness(components),
    )


def _action_gates(
    actions: tuple[HumanAction, ...], gates: tuple[HandoverGate, ...]
) -> tuple[HandoverGate, ...]:

    refs = {
        (item.gate_id, item.gate_revision)
        for item in actions
        if item.kind is HumanActionKind.CHOOSE_PATH
    }

    return tuple(
        item
        for item in gates
        if (item.gate_id, item.revision) in refs and item.policy.value == "HUMAN_CHOICE"
    )


def project_decision_support(
    *,
    slice_definition: SliceDefinitionSnapshot,
    lifecycle: SliceLifecycle | None,
    gates: tuple[HandoverGate, ...],
    latest_evaluation: GateEvaluationRecord | None,
    evaluation_basis_status: EvaluationBasisStatus,
    executions: tuple[ExecutionRecord, ...],
    human_actions: HumanActionProjection,
    manual_evaluation: ManualEvaluationProjection,
) -> DecisionSupportProjection:
    """Build cards from already-loaded same-snapshot governance projections."""

    basis = human_actions.basis

    if basis is None:
        return DecisionSupportProjection(cards=())

    gate_by_ref = {(item.gate_id, item.revision): item for item in gates}

    actions = human_actions.actions

    cards: list[DecisionCard] = []

    for kind in (DecisionKind.GATE_AUTHORIZATION, DecisionKind.GATE_APPROVAL):
        action_kinds = (
            {HumanActionKind.AUTHORIZE}
            if kind is DecisionKind.GATE_AUTHORIZATION
            else {HumanActionKind.APPROVE, HumanActionKind.REJECT}
        )

        keys = sorted(
            {
                (item.gate_id, item.gate_revision)
                for item in actions
                if item.kind in action_kinds
                and item.gate_id is not None
                and item.gate_revision is not None
            }
        )

        for key in keys:
            gate = gate_by_ref.get(key)

            if (
                gate is None
                or GateRevisionRef(gate_id=key[0], gate_revision=key[1]) not in basis.gate_refs
            ):
                raise PersistenceIntegrityError(
                    "current Human action references a missing exact gate revision"
                )

            matching = tuple(
                item
                for item in actions
                if item.gate_id == gate.gate_id
                and item.gate_revision == gate.revision
                and item.kind
                in (
                    {HumanActionKind.AUTHORIZE}
                    if kind is DecisionKind.GATE_AUTHORIZATION
                    else {HumanActionKind.APPROVE, HumanActionKind.REJECT}
                )
            )

            cards.append(
                _build_gate_card(
                    kind=kind,
                    gate=gate,
                    definition=slice_definition,
                    lifecycle=lifecycle,
                    latest=latest_evaluation,
                    evaluation_status=evaluation_basis_status,
                    basis=basis,
                    human_actions=human_actions,
                    executions=executions,
                    actions=matching,
                )
            )

    choice_actions = tuple(item for item in actions if item.kind is HumanActionKind.CHOOSE_PATH)

    if choice_actions:
        choice_gates = _action_gates(choice_actions, gates)

        choice_action_refs = {
            (item.gate_id, item.gate_revision)
            for item in choice_actions
            if item.gate_id is not None and item.gate_revision is not None
        }

        if not choice_gates or len(choice_gates) != len(choice_action_refs):
            raise PersistenceIntegrityError(
                "CHOOSE_PATH actions do not identify the complete current HUMAN_CHOICE gate set"
            )

        if any(_gate_ref(item) not in basis.gate_refs for item in choice_gates):
            raise PersistenceIntegrityError(
                "current HUMAN_CHOICE gate is absent from HumanActionBasis"
            )

        choice_gates = tuple(sorted(choice_gates, key=lambda item: (item.gate_id, item.revision)))
        gate_cards = tuple(
            _build_gate_card(
                kind=DecisionKind.GATE_PATH_CHOICE,
                gate=gate,
                definition=slice_definition,
                lifecycle=lifecycle,
                latest=latest_evaluation,
                evaluation_status=evaluation_basis_status,
                basis=basis,
                human_actions=human_actions,
                executions=executions,
                actions=tuple(
                    action
                    for action in choice_actions
                    if action.gate_id == gate.gate_id and action.gate_revision == gate.revision
                ),
            )
            for gate in choice_gates
        )
        path_card = gate_cards[0]

        outcomes = tuple(
            sorted(
                (
                    DecisionProposedOutcome(
                        gate_ref=_gate_ref(gate),
                        target_phase=gate.target_phase,
                        label=f"{gate.key}: {gate.target_phase.value}",
                    )
                    for gate in choice_gates
                ),
                key=lambda item: (
                    item.gate_ref.gate_id,
                    item.gate_ref.gate_revision,
                    item.target_phase.value,
                ),
            )
        )

        path_refs = tuple(_gate_ref(gate) for gate in choice_gates)

        choice = human_actions.current_choice

        is_current = (
            choice is not None
            and choice.choice_gate_refs == path_refs
            and basis.current_choice_decision_id == choice.decision_id
            and GateRevisionRef(
                gate_id=choice.selected_gate_id, gate_revision=choice.selected_gate_revision
            )
            in path_refs
        )

        state = (
            DecisionCardState.RECORDED_REVISABLE
            if is_current
            else DecisionCardState.PENDING_REQUIRED
        )

        current_choice_id = choice.decision_id if is_current and choice is not None else None

        current_choice_text = (
            f"Selected {choice.selected_gate_id}@r{choice.selected_gate_revision}"
            if is_current and choice is not None
            else None
        )

        source_refs_by_key = {
            (ref.kind.value, ref.stable_ref, ref.label): ref
            for card in gate_cards
            for ref in card.source_refs
        }
        if is_current and choice is not None:
            decision_ref = _source(
                DecisionSourceKind.HUMAN_DECISION,
                choice.decision_id,
                "Current Human path-choice decision",
            )
            source_refs_by_key[
                (decision_ref.kind.value, decision_ref.stable_ref, decision_ref.label)
            ] = decision_ref
        path_source_refs = tuple(source_refs_by_key[key] for key in sorted(source_refs_by_key))

        components_by_kind: dict[DecisionBasisComponentKind, list[DecisionBasisComponent]] = {}
        for card in gate_cards:
            for component in card.components:
                components_by_kind.setdefault(component.kind, []).append(component)
        merged_components: list[DecisionBasisComponent] = []
        for component_kind in DecisionBasisComponentKind:
            values = components_by_kind[component_kind]
            required = any(item.required for item in values)
            source_map = {
                (ref.kind.value, ref.stable_ref, ref.label): ref
                for item in values
                for ref in item.source_refs
            }
            component_refs = tuple(source_map[key] for key in sorted(source_map))
            if not required:
                if any(
                    item.applicability is DecisionBasisApplicability.OPTIONAL_PRESENT
                    for item in values
                ):
                    applicability = DecisionBasisApplicability.OPTIONAL_PRESENT
                    freshness = (
                        DecisionBasisFreshness.STALE
                        if any(item.freshness is DecisionBasisFreshness.STALE for item in values)
                        else DecisionBasisFreshness.UNKNOWN
                        if any(item.freshness is DecisionBasisFreshness.UNKNOWN for item in values)
                        else DecisionBasisFreshness.CURRENT
                    )
                elif any(
                    item.applicability is DecisionBasisApplicability.UNKNOWN for item in values
                ):
                    applicability = DecisionBasisApplicability.UNKNOWN
                    freshness = DecisionBasisFreshness.UNKNOWN
                else:
                    applicability = DecisionBasisApplicability.NOT_APPLICABLE
                    freshness = DecisionBasisFreshness.NOT_APPLICABLE
            else:
                applicability = (
                    DecisionBasisApplicability.MISSING_REQUIRED
                    if any(
                        item.applicability is DecisionBasisApplicability.MISSING_REQUIRED
                        for item in values
                        if item.required
                    )
                    else DecisionBasisApplicability.UNKNOWN
                    if any(
                        item.applicability is DecisionBasisApplicability.UNKNOWN
                        for item in values
                        if item.required
                    )
                    else DecisionBasisApplicability.REQUIRED_PRESENT
                )
                freshness = (
                    DecisionBasisFreshness.STALE
                    if any(
                        item.freshness is DecisionBasisFreshness.STALE
                        for item in values
                        if item.required
                    )
                    else DecisionBasisFreshness.UNKNOWN
                    if any(
                        item.freshness is DecisionBasisFreshness.UNKNOWN
                        for item in values
                        if item.required
                    )
                    else DecisionBasisFreshness.CURRENT
                )
            summaries = tuple(dict.fromkeys(item.summary for item in values))
            merged_components.append(
                DecisionBasisComponent(
                    kind=component_kind,
                    applicability=applicability,
                    freshness=freshness,
                    required=required,
                    summary="; ".join(summaries),
                    source_refs=component_refs,
                )
            )

        def merge_statements(name: str) -> tuple[DecisionStatement, ...]:
            unique: dict[tuple[str, str, tuple[tuple[str, str, str], ...]], DecisionStatement] = {}
            for card in gate_cards:
                for statement in getattr(card, name):
                    statement_key = (
                        statement.text,
                        statement.basis.value,
                        tuple(
                            (ref.kind.value, ref.stable_ref, ref.label)
                            for ref in statement.source_refs
                        ),
                    )
                    unique[statement_key] = statement
            return tuple(unique[key] for key in sorted(unique))

        path_why = "; ".join(card.why_required.text for card in gate_cards)
        path_why_statement = _decision_why(
            state=state,
            pending_reason=path_why,
            recorded_text=current_choice_text,
            recorded_id=current_choice_id,
            refs=path_source_refs,
        )

        identity = path_card.decision.identity.model_copy(
            update={
                "decision_state": state,
                "expected_current_choice_decision_id": current_choice_id,
                "eligible_choice_gate_refs": path_refs,
            }
        )

        pending = PendingDecisionRef(identity=identity, basis_digest=identity.digest())

        choices = tuple(
            GatePathChoice(
                command=HumanActionKind.CHOOSE_PATH,
                gate_ref=ref,
                human_action_basis=basis,
                expected_current_choice_decision_id=current_choice_id,
            )
            for ref in path_refs
        )

        path_card = path_card.model_copy(
            update={
                "decision": pending,
                "state": state,
                "current_recorded_decision": None if not is_current else current_choice_text,
                "proposed_outcomes": outcomes,
                "choices": choices,
                "title": "Choose one of the current handover paths",
                "why_required": path_why_statement,
                "components": tuple(merged_components),
                "evidence": merge_statements("evidence"),
                "evaluation": merge_statements("evaluation"),
                "risks": merge_statements("risks"),
                "unknowns": merge_statements("unknowns"),
                "blocking_findings": merge_statements("blocking_findings"),
                "governance_requirements": merge_statements("governance_requirements"),
                "source_refs": path_source_refs,
                "completeness": _completeness(tuple(merged_components)),
            }
        )

        cards.append(path_card)

    technical_actions = set(manual_evaluation.actions) & {
        ManualEvaluationActionKind.TECHNICAL_ACCEPT,
        ManualEvaluationActionKind.TECHNICAL_REJECT,
    }

    result = manual_evaluation.current_result

    evaluation = manual_evaluation.current_evaluation

    if technical_actions and result is not None and evaluation is not None:
        human_basis = basis

        technical_basis = manual_evaluation.action_basis

        if (
            technical_basis is None
            or human_basis.current_result_id != result.result_id
            or human_basis.current_result_baseline_id != result.result_baseline_id
            or human_basis.current_manual_evaluation_id != evaluation.evaluation_id
            or technical_basis.current_result_id != result.result_id
            or technical_basis.current_manual_evaluation_id != evaluation.evaluation_id
            or result.slice_id != slice_definition.value.id
            or evaluation.slice_id != slice_definition.value.id
            or evaluation.result_id != result.result_id
            or evaluation.result_baseline_id != result.result_baseline_id
        ):
            raise PersistenceIntegrityError(
                "technical decision projection does not bind the exact current result and evaluation"  # noqa: E501
            )

        for reference in manual_evaluation.technical_gate_refs:
            gate = gate_by_ref.get((reference.gate_id, reference.gate_revision))

            if (
                gate is None
                or gate.target_phase is not LifecyclePhase.ACCEPTED
                or reference not in human_basis.gate_refs
                or reference not in technical_basis.gate_refs
            ):
                raise PersistenceIntegrityError(
                    "technical action references a missing exact ACCEPTED gate"
                )

            approval = _current_approval(human_actions, gate, human_basis)

            current_decision = manual_evaluation.current_technical_decision

            if current_decision is not None and (
                current_decision.gate_id != gate.gate_id
                or approval is None
                or approval.decision_id != current_decision.decision_id
            ):
                current_decision = None

            state = (
                DecisionCardState.RECORDED_REVISABLE
                if current_decision is not None
                else DecisionCardState.PENDING_REQUIRED
            )

            current_decision_id = (
                current_decision.decision_id if current_decision is not None else None
            )

            identity = DecisionBasisIdentityV1(
                decision_kind=DecisionKind.TECHNICAL_ACCEPTANCE,
                slice_id=slice_definition.value.id,
                gate_ref=reference,
                target_phase=gate.target_phase,
                human_action_basis=human_basis,
                decision_state=state,
                expected_current_approval_decision_id=current_decision_id,
                expected_result_id=result.result_id,
                expected_manual_evaluation_id=evaluation.evaluation_id,
            )

            pending = PendingDecisionRef(identity=identity, basis_digest=identity.digest())

            refs = _sources(
                slice_definition,
                lifecycle,
                gate,
                latest_evaluation,
                result,
                evaluation,
                executions,
                () if current_decision is None else (current_decision,),
                human_actions.current_authorizations,
                gate.required_artifact_ids,
            )

            components = _technical_components(
                refs,
                gate,
                latest_evaluation,
                evaluation_basis_status,
                result,
                evaluation,
            )

            outcomes = (
                DecisionProposedOutcome(
                    gate_ref=reference,
                    target_phase=gate.target_phase,
                    label=f"{gate.key}: {gate.target_phase.value}",
                ),
            )

            commands = tuple(
                TechnicalAcceptanceChoice(
                    command=kind,
                    gate_ref=reference,
                    human_action_basis=human_basis,
                    expected_current_approval_decision_id=(
                        None if approval is None else approval.decision_id
                    ),
                    expected_result_id=result.result_id,
                    expected_manual_evaluation_id=evaluation.evaluation_id,
                )
                for kind in (
                    ManualEvaluationActionKind.TECHNICAL_ACCEPT,
                    ManualEvaluationActionKind.TECHNICAL_REJECT,
                )
                if kind in technical_actions
            )

            statements = tuple(
                _statement(text, refs, DecisionStatementBasis.EVALUATOR_JUDGMENT)
                for text in (
                    f"Outcome: {evaluation.outcome.value}",
                    f"Summary: {evaluation.summary}",
                    *(f"Finding: {item}" for item in evaluation.findings),
                )
            )

            risk = tuple(
                _statement(text, refs, DecisionStatementBasis.EVALUATOR_JUDGMENT)
                for text in (
                    f"Risk status: {evaluation.risk_status.value}",
                    f"Change surface: {evaluation.change_surface_status.value}",
                    f"Toolchain change: {evaluation.toolchain_change_status.value}",
                )
            )

            consequences = (
                _statement(
                    "Records the exact Human decision over this result/evaluation/gate basis; technical acceptance is not promotion.",  # noqa: E501
                    refs,
                ),
            )

            cards.append(
                DecisionCard(
                    decision=pending,
                    title="Accept or reject technical result",
                    state=state,
                    current_recorded_decision=None
                    if current_decision is None
                    else current_decision.decision.value,
                    why_required=_decision_why(
                        state=state,
                        pending_reason=(
                            "the current manual evaluation outcome is ACCEPT and the exact "
                            "accepted-target gate exposes technical Human decisions."
                        ),
                        recorded_text=(
                            None if current_decision is None else current_decision.decision.value
                        ),
                        recorded_id=(
                            None if current_decision is None else current_decision.decision_id
                        ),
                        refs=refs,
                    ),
                    current_state=_statement(
                        f"Result {result.result_id} with evaluation {evaluation.evaluation_id} ({evaluation.outcome.value}).",  # noqa: E501
                        refs,
                    ),
                    proposed_outcomes=outcomes,
                    choices=commands,
                    components=components,
                    evidence=tuple(
                        _statement(f"Evidence {item}", refs) for item in evaluation.evidence_ids
                    ),
                    evaluation=statements,
                    risks=risk,
                    consequences=consequences,
                    governance_requirements=_governance_statements(gate, refs),
                    source_refs=refs,
                    completeness=_completeness(components),
                )
            )

    cards.sort(
        key=lambda item: (
            _CARD_ORDER[item.decision.identity.decision_kind],
            item.decision.identity.gate_ref.gate_id if item.decision.identity.gate_ref else "",
            item.decision.identity.target_phase.value
            if item.decision.identity.target_phase
            else "",
            item.decision.basis_digest,
        )
    )

    return DecisionSupportProjection(cards=tuple(cards))


def answer_decision_question(card: DecisionCard, question: DecisionQuestionKind) -> DecisionAnswer:
    """Return a deterministic answer derived only from the supplied current card."""

    kind = card.decision.identity.decision_kind

    statements: tuple[DecisionStatement, ...]

    if question is DecisionQuestionKind.WHY_REQUIRED:
        statements = (card.why_required,)

    elif question is DecisionQuestionKind.WHAT_IS_CURRENT:
        statements = (card.current_state,)

    elif question is DecisionQuestionKind.WHAT_WOULD_CHANGE:
        statements = tuple(
            _statement(
                f"{item.gate_ref.gate_id}@r{item.gate_ref.gate_revision} -> {item.target_phase.value}: {item.label}",  # noqa: E501
                card.source_refs,
            )
            for item in card.proposed_outcomes
        )

    elif question is DecisionQuestionKind.WHAT_EVIDENCE_EXISTS:
        component_statements = tuple(
            _statement(
                f"Evidence applicability is {item.applicability.value}: {item.summary}",
                item.source_refs,
                DecisionStatementBasis.UNKNOWN
                if item.applicability is DecisionBasisApplicability.UNKNOWN
                else DecisionStatementBasis.CANONICAL_FACT,
            )
            for item in card.components
            if item.kind is DecisionBasisComponentKind.EVIDENCE
        )
        statements = card.evidence + component_statements

    elif question is DecisionQuestionKind.WHAT_DID_THE_EVALUATOR_FIND:
        statements = card.evaluation or (
            _statement("No current manual evaluation applies to this decision.", card.source_refs),
        )

    elif question is DecisionQuestionKind.WHAT_BLOCKS_OR_IS_UNKNOWN:
        statements = (
            card.blocking_findings
            + card.unknowns
            + tuple(
                _statement(f"{item.kind.value}: {item.summary}", item.source_refs)
                for item in card.components
                if item.applicability is DecisionBasisApplicability.MISSING_REQUIRED
            )
        )

        if not statements:
            statements = (
                _statement(
                    "No required component is recorded as missing, stale, or unknown in this exact basis.",  # noqa: E501
                    card.source_refs,
                ),
            )

    elif question in {DecisionQuestionKind.WHAT_IF_APPROVED, DecisionQuestionKind.WHAT_IF_REJECTED}:
        if kind is DecisionKind.GATE_PATH_CHOICE:
            statements = (
                _statement(
                    "A path choice is not collapsed into an approval or preselected route; choose one exact listed path.",  # noqa: E501
                    card.source_refs,
                ),
            )

        elif kind is DecisionKind.GATE_AUTHORIZATION:
            if question is DecisionQuestionKind.WHAT_IF_APPROVED:
                statements = card.consequences

            else:
                statements = (
                    _statement(
                        "No rejection command applies to this authorization decision; the answer does not execute a command.",  # noqa: E501
                        card.source_refs,
                        DecisionStatementBasis.UNKNOWN,
                    ),
                )

        elif kind is DecisionKind.TECHNICAL_ACCEPTANCE:
            outcome = (
                "acceptance" if question is DecisionQuestionKind.WHAT_IF_APPROVED else "rejection"
            )

            statements = (
                _statement(
                    f"Records the exact Human technical {outcome} over the current result and evaluation; "  # noqa: E501
                    "technical acceptance is distinct from promotion.",
                    card.source_refs,
                ),
            )

        else:
            decision = (
                "approval" if question is DecisionQuestionKind.WHAT_IF_APPROVED else "rejection"
            )

            statements = (
                _statement(
                    f"Records the exact Human {decision} for the current gate and reevaluates; "
                    "it does not itself execute handover.",
                    card.source_refs,
                ),
            )

    elif question is DecisionQuestionKind.WHAT_IF_DEFERRED:
        statements = (
            _statement(
                "DEFER remains an existing Human hold control where currently available; this answer does not execute it.",  # noqa: E501
                card.source_refs,
            ),
        )

    else:
        statements = card.governance_requirements

    answer = "\n".join(item.text for item in statements)

    return DecisionAnswer(
        decision=card.decision,
        question_kind=question,
        answer=answer,
        basis_labels=tuple(item.basis for item in statements),
        source_refs=tuple(
            sorted(
                {
                    (ref.kind.value, ref.stable_ref, ref.label): ref
                    for item in statements
                    for ref in item.source_refs
                }.values(),
                key=lambda item: (item.kind.value, item.stable_ref, item.label),
            )
        ),
        freshness=DecisionBasisFreshness.CURRENT,
    )


__all__ = ["answer_decision_question", "project_decision_support"]
