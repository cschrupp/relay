"""Pure projection cardinality, freshness, and deterministic Q&A tests."""

from datetime import UTC, datetime

from relay_engine.board.models import EvaluationBasisStatus
from relay_engine.decision_support.models import (
    DecisionBasisApplicability,
    DecisionBasisCompleteness,
    DecisionCardState,
    DecisionKind,
    DecisionQuestionKind,
)
from relay_engine.decision_support.service import answer_decision_question, project_decision_support
from relay_engine.domain.ids import (
    BaselineId,
    HandoverGateId,
    ProjectId,
    SliceId,
)
from relay_engine.domain.models import AcceptanceCriterion, ScopeSpec, Slice
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.governance.models import (
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateEvaluation,
    GateReason,
    GateReasonCode,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    HumanApprovalDecision,
    HumanApprovalValue,
    HumanChoiceDecision,
    RiskStatus,
    ToolchainChangeStatus,
    TrafficLight,
)
from relay_engine.human_control.models import (
    HumanAction,
    HumanActionBasis,
    HumanActionKind,
    HumanActionProjection,
    HumanApprovalIdentity,
)
from relay_engine.lifecycle.models import (
    Blockage,
    BlockageStatus,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
)
from relay_engine.manual_evaluation.models import (
    ManualEvaluationActionBasis,
    ManualEvaluationActionKind,
    ManualEvaluationProjection,
    ManualEvaluationRecord,
    SliceResultRecord,
)
from relay_engine.persistence.records import GateEvaluationRecord
from relay_engine.project_slice.models import SliceDefinitionSnapshot

NOW = datetime(2026, 10, 11, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
GATE_A: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"
GATE_B: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789021"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)


def _slice() -> SliceDefinitionSnapshot:
    return SliceDefinitionSnapshot(
        value=Slice(
            id=SLICE_ID,
            project_id=PROJECT_ID,
            title="Decision support",
            scope=ScopeSpec(in_scope=("project current state",), out_of_scope=("mutate state",)),
            acceptance_criteria=(
                AcceptanceCriterion(key="A01", statement="Explain decisions.", required=True),
            ),
        ),
        definition_revision=1,
    )


def _lifecycle(phase: LifecyclePhase = LifecyclePhase.READY) -> SliceLifecycle:
    return SliceLifecycle(
        slice_id=SLICE_ID,
        phase=phase,
        validity=LifecycleValidity.CURRENT,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=2,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )


def _gate(
    gate_id: HandoverGateId = GATE_A,
    *,
    target: LifecyclePhase = LifecyclePhase.IMPLEMENTING,
    policy: HandoverPolicy = HandoverPolicy.HUMAN_APPROVAL,
    evidence_ids: tuple[str, ...] = (),
) -> HandoverGate:
    return HandoverGate(
        gate_id=gate_id,
        revision=1,
        key="deliver",
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        source_phase=LifecyclePhase.READY
        if target is LifecyclePhase.IMPLEMENTING
        else LifecyclePhase.EVALUATING,
        target_phase=target,
        superseded_by_slice_id=None,
        policy=policy,
        hard_stop=False,
        authorization_required=False,
        required_evidence_ids=evidence_ids,
    )


def _basis(gates: tuple[HandoverGate, ...]) -> HumanActionBasis:
    return HumanActionBasis(
        evaluation_record_id="geval_018f47c1-7b2c-7abc-8def-123456789030",
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        lifecycle_revision=2,
        governance_revision=3,
        gate_refs=tuple(
            GateRevisionRef(gate_id=item.gate_id, gate_revision=item.revision) for item in gates
        ),
    )


def _latest(gates: tuple[HandoverGate, ...], lifecycle: SliceLifecycle) -> GateEvaluationRecord:
    refs = tuple(
        GateRevisionRef(gate_id=item.gate_id, gate_revision=item.revision) for item in gates
    )
    context = HandoverContext(
        baseline_id=BASELINE_ID,
        governance_revision=3,
        lifecycle=lifecycle,
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
    )
    reason_code = (
        GateReasonCode.HUMAN_CHOICE_REQUIRED
        if gates[0].policy is HandoverPolicy.HUMAN_CHOICE
        else GateReasonCode.HUMAN_APPROVAL_REQUIRED
    )
    evaluations = tuple(
        GateEvaluation(
            gate_id=item.gate_id,
            gate_revision=item.revision,
            slice_id=SLICE_ID,
            baseline_id=BASELINE_ID,
            lifecycle_revision=lifecycle.revision,
            governance_revision=3,
            target_phase=item.target_phase,
            light=TrafficLight.YELLOW,
            reasons=(GateReason.for_code(reason_code),),
        )
        for item in gates
    )
    return GateEvaluationRecord(
        id="geval_018f47c1-7b2c-7abc-8def-123456789030",
        recorded_at=NOW,
        gate_refs=refs,
        context=context,
        evaluations=evaluations,
    )


def _project(
    gates: tuple[HandoverGate, ...],
    actions: tuple[HumanAction, ...],
    *,
    lifecycle: SliceLifecycle | None = None,
    decisions: tuple[HumanApprovalDecision, ...] = (),
    choice: HumanChoiceDecision | None = None,
    basis: HumanActionBasis | None = None,
) -> object:
    current_lifecycle = lifecycle or _lifecycle()
    action_basis = basis or _basis(gates)
    return project_decision_support(
        slice_definition=_slice(),
        lifecycle=current_lifecycle,
        gates=gates,
        latest_evaluation=_latest(gates, current_lifecycle),
        evaluation_basis_status=EvaluationBasisStatus.MATCHING_DURABLE_BASIS,
        executions=(),
        human_actions=HumanActionProjection(
            basis=action_basis,
            actions=actions,
            current_approval_decisions=decisions,
            current_choice=choice,
        ),
        manual_evaluation=ManualEvaluationProjection(),
    )


def test_authorization_and_approval_actions_group_into_one_decision_each() -> None:
    gate = _gate()
    auth = _project(
        (gate,),
        (
            HumanAction(
                kind=HumanActionKind.AUTHORIZE,
                gate_id=GATE_A,
                gate_revision=1,
                target_phase=gate.target_phase,
            ),
        ),
    )
    assert len(auth.cards) == 1
    assert auth.cards[0].decision.identity.decision_kind is DecisionKind.GATE_AUTHORIZATION
    assert auth.cards[0].state is DecisionCardState.PENDING_REQUIRED
    approval = _project(
        (gate,),
        (
            HumanAction(
                kind=HumanActionKind.APPROVE,
                gate_id=GATE_A,
                gate_revision=1,
                target_phase=gate.target_phase,
            ),
            HumanAction(
                kind=HumanActionKind.REJECT,
                gate_id=GATE_A,
                gate_revision=1,
                target_phase=gate.target_phase,
            ),
        ),
    )
    assert len(approval.cards) == 1
    assert approval.cards[0].decision.identity.decision_kind is DecisionKind.GATE_APPROVAL
    assert len(approval.cards[0].choices) == 2
    assert len(approval.cards[0].proposed_outcomes) == 1


def test_current_rejection_is_recorded_revisable_not_missing() -> None:
    gate = _gate()
    decision = HumanApprovalDecision(
        decision_id="hdec_018f47c1-7b2c-7abc-8def-123456789032",
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        gate_id=GATE_A,
        gate_revision=1,
        lifecycle_revision=2,
        governance_revision=3,
        actor=ACTOR,
        occurred_at=NOW,
        decision=HumanApprovalValue.REJECT,
        reason="Risk remains unresolved.",
    )
    projection = _project(
        (gate,),
        (
            HumanAction(
                kind=HumanActionKind.APPROVE,
                gate_id=GATE_A,
                gate_revision=1,
                target_phase=gate.target_phase,
            ),
            HumanAction(
                kind=HumanActionKind.REJECT,
                gate_id=GATE_A,
                gate_revision=1,
                target_phase=gate.target_phase,
            ),
        ),
        decisions=(decision,),
        basis=_basis((gate,)).model_copy(
            update={
                "current_approval_decision_ids": (
                    HumanApprovalIdentity(gate_id=GATE_A, decision_id=decision.decision_id),
                )
            }
        ),
    )
    card = projection.cards[0]
    assert card.state is DecisionCardState.RECORDED_REVISABLE
    assert card.current_recorded_decision == "REJECT"
    assert card.decision.identity.expected_current_approval_decision_id == decision.decision_id


def test_path_choices_are_one_card_with_all_exact_outcomes_and_qa() -> None:
    gates = (
        _gate(GATE_A, policy=HandoverPolicy.HUMAN_CHOICE),
        _gate(GATE_B, policy=HandoverPolicy.HUMAN_CHOICE, target=LifecyclePhase.PLANNING),
    )
    projection = _project(
        gates,
        tuple(
            HumanAction(
                kind=HumanActionKind.CHOOSE_PATH,
                gate_id=item.gate_id,
                gate_revision=1,
                target_phase=item.target_phase,
            )
            for item in gates
        ),
    )
    assert len(projection.cards) == 1
    card = projection.cards[0]
    assert card.decision.identity.decision_kind is DecisionKind.GATE_PATH_CHOICE
    assert len(card.proposed_outcomes) == 2
    assert {
        (item.gate_ref.gate_id, item.gate_ref.gate_revision) for item in card.proposed_outcomes
    } == {(GATE_A, 1), (GATE_B, 1)}
    answer = answer_decision_question(card, DecisionQuestionKind.WHAT_WOULD_CHANGE)
    assert len(answer.answer.splitlines()) == 2
    assert (
        "choose one" in answer_decision_question(card, DecisionQuestionKind.WHAT_IF_APPROVED).answer
    )


def test_gate_evidence_applicability_and_operational_controls() -> None:
    gate = _gate(evidence_ids=("evd_018f47c1-7b2c-7abc-8def-123456789050",))
    projection = _project(
        (gate,),
        (
            HumanAction(
                kind=HumanActionKind.APPROVE,
                gate_id=GATE_A,
                gate_revision=1,
                target_phase=gate.target_phase,
            ),
        ),
    )
    card = projection.cards[0]
    evidence_component = next(item for item in card.components if item.kind.value == "EVIDENCE")
    assert evidence_component.applicability is DecisionBasisApplicability.MISSING_REQUIRED
    assert card.completeness is DecisionBasisCompleteness.INCOMPLETE
    no_evidence_requirement = _project(
        (_gate(),),
        (
            HumanAction(
                kind=HumanActionKind.APPROVE,
                gate_id=GATE_A,
                gate_revision=1,
                target_phase=LifecyclePhase.IMPLEMENTING,
            ),
        ),
    ).cards[0]
    assert (
        next(
            item for item in no_evidence_requirement.components if item.kind.value == "EVIDENCE"
        ).applicability
        is DecisionBasisApplicability.NOT_APPLICABLE
    )
    controls_only = _project(
        (_gate(),),
        (HumanAction(kind=HumanActionKind.DEFER), HumanAction(kind=HumanActionKind.BLOCK)),
    )
    assert controls_only.cards == ()


def test_technical_acceptance_is_one_card_with_exact_result_evaluation_and_evidence() -> None:
    lifecycle = _lifecycle(LifecyclePhase.EVALUATING)
    gate = _gate(target=LifecyclePhase.ACCEPTED)
    result = SliceResultRecord(
        result_id="res_018f47c1-7b2c-7abc-8def-123456789034",
        slice_id=SLICE_ID,
        slice_definition_revision=1,
        source_baseline_id=BASELINE_ID,
        result_baseline_id=BASELINE_ID,
        lifecycle_revision=2,
        supersedes_result_id=None,
        recorded_by=ACTOR,
        recorded_at=NOW,
        reason="Attach exact result.",
    )
    evaluation = ManualEvaluationRecord(
        evaluation_id="eval_018f47c1-7b2c-7abc-8def-123456789035",
        slice_id=SLICE_ID,
        result_id=result.result_id,
        result_baseline_id=BASELINE_ID,
        source_baseline_id=BASELINE_ID,
        slice_definition_revision=1,
        lifecycle_revision=2,
        gate_refs=(GateRevisionRef(gate_id=GATE_A, gate_revision=1),),
        prior_gate_evaluation_record_id="geval_018f47c1-7b2c-7abc-8def-123456789030",
        evaluator=ACTOR,
        evaluated_at=NOW,
        outcome=EvaluationOutcome.ACCEPT,
        evidence_ids=("evd_018f47c1-7b2c-7abc-8def-123456789050",),
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
        findings=("Checks passed.",),
        summary="The exact candidate meets the criteria.",
    )
    basis = _basis((gate,)).model_copy(
        update={
            "current_result_id": result.result_id,
            "current_result_baseline_id": BASELINE_ID,
            "current_manual_evaluation_id": evaluation.evaluation_id,
        }
    )
    support = project_decision_support(
        slice_definition=_slice(),
        lifecycle=lifecycle,
        gates=(gate,),
        latest_evaluation=_latest((gate,), lifecycle),
        evaluation_basis_status=EvaluationBasisStatus.MATCHING_DURABLE_BASIS,
        executions=(),
        human_actions=HumanActionProjection(basis=basis),
        manual_evaluation=ManualEvaluationProjection(
            action_basis=ManualEvaluationActionBasis(
                slice_id=SLICE_ID,
                lifecycle_revision=2,
                slice_definition_revision=1,
                current_result_id=result.result_id,
                current_manual_evaluation_id=evaluation.evaluation_id,
                latest_gate_evaluation_record_id="geval_018f47c1-7b2c-7abc-8def-123456789030",
                gate_refs=(GateRevisionRef(gate_id=GATE_A, gate_revision=1),),
            ),
            actions=(
                ManualEvaluationActionKind.TECHNICAL_ACCEPT,
                ManualEvaluationActionKind.TECHNICAL_REJECT,
            ),
            technical_gate_refs=(GateRevisionRef(gate_id=GATE_A, gate_revision=1),),
            current_result=result,
            current_evaluation=evaluation,
        ),
    )
    assert len(support.cards) == 1
    card = support.cards[0]
    assert card.decision.identity.decision_kind is DecisionKind.TECHNICAL_ACCEPTANCE
    assert card.state is DecisionCardState.PENDING_REQUIRED
    assert card.decision.identity.expected_result_id == result.result_id
    assert card.decision.identity.expected_manual_evaluation_id == evaluation.evaluation_id
    assert len(card.choices) == 2
    assert len(card.proposed_outcomes) == 1
    evidence = next(item for item in card.components if item.kind.value == "EVIDENCE")
    assert evidence.applicability is DecisionBasisApplicability.REQUIRED_PRESENT
    assert any(item.basis.value == "EVALUATOR_JUDGMENT" for item in card.evaluation)
