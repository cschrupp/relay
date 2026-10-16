"""HTML escaping, observational wording, and accessibility presentation tests."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from conftest import make_test_origin_resolution
from relay_engine.board.inspection import project_project_situation
from relay_engine.board.models import (
    BoardLane,
    CanonicalGovernanceInspection,
    CanonicalTargetInspection,
    DependencyProjection,
    EvaluationBasisStatus,
    GateProjection,
    LiveObservationStatus,
    ProjectBoard,
    PromotionAttemptInspection,
    PromotionIntentAuthorityStatus,
    SliceCard,
    SliceDetail,
)
from relay_engine.board.render import (
    render_project_board,
    render_project_index,
    render_slice_detail,
)
from relay_engine.decision_support.models import (
    DecisionBasisCompleteness,
    DecisionBasisIdentityV1,
    DecisionCard,
    DecisionCardState,
    DecisionKind,
    DecisionProposedOutcome,
    DecisionSourceKind,
    DecisionSourceRef,
    DecisionStatement,
    DecisionStatementBasis,
    DecisionSupportProjection,
    PendingDecisionRef,
)
from relay_engine.domain.ids import (
    AuthorizationId,
    BaselineId,
    EvidenceId,
    ExecutionId,
    HandoverGateId,
    HumanDecisionId,
    ManualEvaluationId,
    ProjectId,
    SliceId,
    SliceResultId,
)
from relay_engine.domain.models import (
    AcceptanceCriterion,
    Baseline,
    Evidence,
    Project,
    ScopeSpec,
    Slice,
)
from relay_engine.domain.references import (
    ActorKind,
    ActorRef,
    CommitRef,
    RepositoryRef,
)
from relay_engine.governance.models import (
    AuthorizationGrant,
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
from relay_engine.human_control.models import HumanActionBasis, HumanActionProjection
from relay_engine.lifecycle.models import (
    Blockage,
    BlockageStatus,
    BlockReason,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
)
from relay_engine.manual_evaluation.models import (
    AcceptedSliceResult,
    DevelopmentMemoryProjection,
    ManualEvaluationProjection,
    ManualEvaluationRecord,
    SliceResultRecord,
)
from relay_engine.persistence.records import ExecutionRecord, GateEvaluationRecord
from relay_engine.project_slice.models import SliceDefinitionSnapshot
from relay_engine.project_slice.origin import OperationalOrigin, OriginSubjectType
from relay_engine.promotion.models import (
    CanonicalPromotionPolicyBindingResolution,
    CanonicalPromotionReconciliationV1,
    CanonicalRefHealth,
    PromotionAuthorizability,
    PromotionEligibilityState,
    PromotionPropertyOutcome,
    PromotionResultOutcome,
    ReconciliationPreparationState,
    RepositoryPromotionResultV1,
)

NOW = datetime(2026, 10, 2, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
RESULT_BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789004"
GATE_ID: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"
AUTHORIZATION_ID: AuthorizationId = "auth_018f47c1-7b2c-7abc-8def-123456789040"
HUMAN_DECISION_ID: HumanDecisionId = "hdec_018f47c1-7b2c-7abc-8def-123456789041"
CHOICE_DECISION_ID: HumanDecisionId = "hdec_018f47c1-7b2c-7abc-8def-123456789042"
RESULT_ID: SliceResultId = "res_018f47c1-7b2c-7abc-8def-123456789043"
EVALUATION_ID: ManualEvaluationId = "eval_018f47c1-7b2c-7abc-8def-123456789044"
EXECUTION_ID: ExecutionId = "exec_018f47c1-7b2c-7abc-8def-123456789045"
EVIDENCE_ID: EvidenceId = "evd_018f47c1-7b2c-7abc-8def-123456789046"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="owner/relay",
)


def _fixture() -> tuple[ProjectBoard, SliceDetail]:
    project = Project(
        id=PROJECT_ID,
        name="<script>project()</script>",
        primary_repository=REPOSITORY,
    )
    slice_value = Slice(
        id=SLICE_ID,
        project_id=PROJECT_ID,
        title="<img src=x onerror=alert(1)>",
        scope=ScopeSpec(
            in_scope=("<script>scope()</script>",),
            out_of_scope=("<b>not HTML</b>",),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                key="A01",
                statement="<svg onload=alert(1)>",
                required=True,
            ),
            AcceptanceCriterion(
                key="A02",
                statement="Optional display behavior.",
                required=False,
            ),
        ),
    )
    lifecycle = SliceLifecycle(
        slice_id=SLICE_ID,
        phase=LifecyclePhase.READY,
        validity=LifecycleValidity.STALE,
        blockage=Blockage(
            status=BlockageStatus.BLOCKED,
            reasons=(BlockReason(code="WAITING", summary="<script>blocker()</script>"),),
        ),
        revision=4,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    gate = HandoverGate(
        gate_id=GATE_ID,
        revision=1,
        key="implement",
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        source_phase=LifecyclePhase.READY,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.AUTO,
        authorization_required=True,
    )
    context = HandoverContext(
        baseline_id=BASELINE_ID,
        governance_revision=2,
        lifecycle=lifecycle,
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
    )
    recorded_evaluation = GateEvaluation(
        gate_id=GATE_ID,
        gate_revision=1,
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        lifecycle_revision=4,
        governance_revision=2,
        target_phase=LifecyclePhase.IMPLEMENTING,
        light=TrafficLight.RED,
        reasons=(GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
    )
    record = GateEvaluationRecord(
        id="geval_018f47c1-7b2c-7abc-8def-123456789030",
        recorded_at=NOW,
        gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
        context=context,
        evaluations=(recorded_evaluation,),
    )
    dependency = DependencyProjection(
        slice_id=SLICE_ID,
        title="<b>dependency</b>",
        lifecycle_phase=LifecyclePhase.READY,
        lifecycle_validity=LifecycleValidity.STALE,
        origin_resolution=make_test_origin_resolution(
            OriginSubjectType.SLICE,
            SLICE_ID,
            project_id=PROJECT_ID,
        ),
    )
    gate_projection = GateProjection(
        gate_id=GATE_ID,
        gate_revision=1,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.AUTO,
        hard_stop=False,
        authorization_required=True,
        baseline_id=BASELINE_ID,
        evaluation_light=None,
        evaluation_reasons=(),
        evaluation_basis_status=EvaluationBasisStatus.STALE_DURABLE_BASIS,
    )
    card = SliceCard(
        slice_id=SLICE_ID,
        title=slice_value.title,
        definition_revision=1,
        parent_slice_id=None,
        dependency_ids=(SLICE_ID,),
        lane=BoardLane.READY,
        lifecycle=lifecycle,
        origin_resolution=make_test_origin_resolution(
            OriginSubjectType.SLICE,
            SLICE_ID,
            project_id=PROJECT_ID,
        ),
        dependencies=(dependency,),
        outgoing_gates=(gate_projection,),
        latest_evaluation_record_id=record.id,
        latest_evaluation_recorded_at=record.recorded_at,
        evaluation_basis_status=EvaluationBasisStatus.STALE_DURABLE_BASIS,
    )
    board = ProjectBoard(
        project=project,
        project_definition_revision=2,
        project_origin_resolution=make_test_origin_resolution(
            OriginSubjectType.PROJECT,
            PROJECT_ID,
        ),
        situation=project_project_situation((card,)),
        canonical_governance=CanonicalGovernanceInspection(
            durable_target_established=False,
            targets=(),
        ),
        lanes=tuple(BoardLane),
        cards=(card,),
    )
    detail = SliceDetail(
        project=project,
        project_definition_revision=2,
        slice_definition=SliceDefinitionSnapshot(value=slice_value, definition_revision=1),
        lifecycle=lifecycle,
        origin_resolution=make_test_origin_resolution(
            OriginSubjectType.SLICE,
            SLICE_ID,
            project_id=PROJECT_ID,
        ),
        origin_governance_scope_available=True,
        parent=None,
        children=(),
        dependencies=(dependency,),
        outgoing_gate_definitions=(gate,),
        outgoing_gates=(gate_projection,),
        latest_evaluation_observation=record,
        evaluation_basis_status=EvaluationBasisStatus.STALE_DURABLE_BASIS,
        baseline=None,
        evaluation_baseline=None,
        relevant_execution_records=(),
        decision_support=DecisionSupportProjection(),
    )
    return board, detail


def _execution_record(
    *,
    execution_id: ExecutionId,
    event_id: str,
    evaluation_record_id: str,
    source_revision: int,
    resulting_revision: int,
    selected_gate_revision: int,
    occurred_at: datetime,
) -> ExecutionRecord:
    return ExecutionRecord(
        execution_id=execution_id,
        gate_evaluation_record_id=evaluation_record_id,
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        selected_gate_id=GATE_ID,
        selected_gate_revision=selected_gate_revision,
        source_lifecycle_revision=source_revision,
        resulting_lifecycle_revision=resulting_revision,
        event_id=event_id,
        actor=ACTOR,
        occurred_at=occurred_at,
        reason="Authorized lifecycle movement.",
    )


def _governance_summary(detail: SliceDetail) -> str:
    html = render_slice_detail(detail)
    start = html.index('<section aria-labelledby="governance-status-heading">')
    end = html.index("<section><h2>Definition</h2>", start)
    return html[start:end]


def test_slice_detail_requires_decision_support_projection() -> None:
    _, detail = _fixture()
    data = detail.model_dump()
    data.pop("decision_support")
    with pytest.raises(ValidationError):
        SliceDetail.model_validate(data)


def test_decision_card_is_derived_accessible_and_has_digest_bound_question_links() -> None:
    _, detail = _fixture()
    basis = HumanActionBasis(
        evaluation_record_id=detail.human_actions.basis.evaluation_record_id
        if detail.human_actions.basis
        else "geval_018f47c1-7b2c-7abc-8def-123456789099",
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        lifecycle_revision=1,
        governance_revision=1,
        gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
    )
    identity = DecisionBasisIdentityV1(
        decision_kind=DecisionKind.GATE_APPROVAL,
        slice_id=SLICE_ID,
        gate_ref=GateRevisionRef(gate_id=GATE_ID, gate_revision=1),
        target_phase=LifecyclePhase.IMPLEMENTING,
        human_action_basis=basis,
        decision_state=DecisionCardState.PENDING_REQUIRED,
    )
    reference = DecisionSourceRef(
        kind=DecisionSourceKind.HANDOVER_GATE,
        stable_ref=f"{GATE_ID}@r1",
        label="Current handover gate",
    )
    card = DecisionCard(
        decision=PendingDecisionRef(identity=identity, basis_digest=identity.digest()),
        title="Approve or reject",
        state=DecisionCardState.PENDING_REQUIRED,
        why_required=DecisionStatement(
            text="The current gate requires a Human decision.",
            basis=DecisionStatementBasis.CANONICAL_FACT,
            source_refs=(reference,),
        ),
        current_state=DecisionStatement(
            text="READY", basis=DecisionStatementBasis.CANONICAL_FACT, source_refs=(reference,)
        ),
        proposed_outcomes=(
            DecisionProposedOutcome(
                gate_ref=GateRevisionRef(gate_id=GATE_ID, gate_revision=1),
                target_phase=LifecyclePhase.IMPLEMENTING,
                label="Begin implementation",
            ),
        ),
        choices=(),
        components=(),
        consequences=(
            DecisionStatement(
                text="Records the exact decision.", basis=DecisionStatementBasis.CANONICAL_FACT
            ),
        ),
        governance_requirements=(),
        source_refs=(reference,),
        completeness=DecisionBasisCompleteness.COMPLETE,
    )
    projection = DecisionSupportProjection(cards=(card,))
    detail = detail.model_copy(update={"decision_support": projection})
    html = render_slice_detail(detail)
    assert "Human Decisions" in html
    assert "Derived / non-authoritative" in html
    assert "Human decision required" in html
    assert card.decision.basis_digest in html
    assert "Ask: Why Required" in html
    assert "Complete does not prove Human understanding" in html
    assert "proposed_state" not in html


def test_project_board_escapes_text_shows_textual_status_and_hides_stale_light() -> None:
    board, _ = _fixture()
    html = render_project_board(board)
    assert "<script>" not in html
    assert "<img src=x" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "&lt;script&gt;project()&lt;/script&gt;" in html
    assert "Lifecycle: <strong>READY</strong>" in html
    assert "Lifecycle validity: STALE" in html
    assert "<strong>BLOCKED</strong>" in html
    assert "Evaluation: stale durable basis" in html
    assert "Latest recorded evaluation on current durable basis: RED" not in html
    assert "Recorded reason counts" not in html
    assert ":focus-visible" in html
    assert "<main>" in html and "<section" in html


def test_matching_gate_light_is_observational_text_and_color() -> None:
    board, detail = _fixture()
    gate = detail.outgoing_gates[0].model_copy(
        update={
            "evaluation_basis_status": EvaluationBasisStatus.MATCHING_DURABLE_BASIS,
            "evaluation_light": TrafficLight.RED,
            "evaluation_reasons": (GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
        }
    )
    card = board.cards[0].model_copy(
        update={
            "evaluation_basis_status": EvaluationBasisStatus.MATCHING_DURABLE_BASIS,
            "outgoing_gates": (gate,),
        }
    )
    matching_board = board.model_copy(update={"cards": (card,)})
    html = render_project_board(matching_board)
    assert 'class="gate-light red"' in html
    assert "Latest recorded evaluation on current durable basis: <strong>RED</strong>" in html
    assert "Recorded reason counts: 1 blocking; 0 human action." in html


def test_slice_detail_shows_escaped_older_evidence_and_typed_context() -> None:
    _, detail = _fixture()
    html = render_slice_detail(detail)
    assert "<script>scope()" not in html
    assert "&lt;script&gt;scope()&lt;/script&gt;" in html
    assert "&lt;svg onload=alert(1)&gt;" in html
    assert "Older evaluation evidence; stored lights are historical." in html
    assert "<strong>RED</strong>" not in html
    assert "Full recorded HandoverContext" in html
    assert "&quot;baseline_id&quot;" in html
    assert "Latest recorded evaluation on current durable basis" not in html


def test_project_situation_and_canonical_inspection_precede_existing_lanes() -> None:
    board, _ = _fixture()

    html = render_project_board(board)

    situation_position = html.index("Project Situation")
    canonical_position = html.index("Canonical Governance Inspection")
    lanes_position = html.index('<div class="lanes">')
    assert situation_position < canonical_position < lanes_position
    assert "Current frontier:" in html
    assert "ACTIVE (1)" in html
    assert "DONE" in html
    assert "SUPERSEDED" in html
    assert "CANCELLED" in html
    assert "Durable canonical governance target: NOT ESTABLISHED" in html
    assert "Live source-control observation: UNAVAILABLE" in html
    assert "current conformance: UNKNOWN" in html
    assert "No branch name is assumed" in html
    assert 'class="lane"' in html


def test_canonical_inspection_preserves_promotion_outcomes_exactly() -> None:
    board, _ = _fixture()
    outcomes = tuple(PromotionResultOutcome)
    attempts: list[PromotionAttemptInspection] = []
    for index, outcome in enumerate(outcomes, start=1):
        promotion_id = f"prom_018f47c1-7b2c-7abc-8def-{index:012d}"
        attempts.append(
            PromotionAttemptInspection(
                promotion_id=promotion_id,
                intent=None,
                original_authority_status=PromotionIntentAuthorityStatus.UNKNOWN,
                result=RepositoryPromotionResultV1(
                    promotion_id=promotion_id,
                    project_id=PROJECT_ID,
                    repository=REPOSITORY,
                    canonical_ref="refs/heads/review-target",
                    outcome=outcome,
                    expected_parent=CommitRef(repository=REPOSITORY, sha="a" * 40),
                    target_commit=CommitRef(repository=REPOSITORY, sha="b" * 40),
                    observed_head=CommitRef(repository=REPOSITORY, sha="b" * 40),
                    observed_at=NOW,
                ),
                reconciliations=(),
            )
        )
    target = CanonicalTargetInspection(
        repository=REPOSITORY,
        canonical_ref="refs/heads/review-target",
        binding_resolution=CanonicalPromotionPolicyBindingResolution.UNKNOWN_OR_INVALID,
        current_binding=None,
        health=CanonicalRefHealth.QUARANTINED,
        current_authorizability=PromotionAuthorizability.UNKNOWN,
        current_eligibility=PromotionEligibilityState.UNKNOWN,
        reconciliation_preparation_state=ReconciliationPreparationState.UNKNOWN,
        live_observation_status=LiveObservationStatus.UNAVAILABLE,
        live_source_control_observation=None,
        live_source_control_conformance=PromotionPropertyOutcome.UNKNOWN,
        promotion_attempts=tuple(attempts),
    )
    inspection = CanonicalGovernanceInspection(
        durable_target_established=False,
        targets=(target,),
    )
    board_with_history = board.model_copy(update={"canonical_governance": inspection})

    html = render_project_board(board_with_history)

    assert "canonical ref health: <strong>QUARANTINED</strong>" in html
    for outcome in outcomes:
        assert f"<strong>{outcome.value}</strong>" in html
    assert "Reconciliation preparation: UNKNOWN" in html
    assert "Current conformance is UNKNOWN because no live observation was supplied." in html


def test_canonical_inspection_shows_stored_reconciliation_provenance() -> None:
    board, _ = _fixture()
    promotion_id = "prom_018f47c1-7b2c-7abc-8def-123456789091"
    reconciliation = CanonicalPromotionReconciliationV1(
        reconciliation_id="recon_018f47c1-7b2c-7abc-8def-123456789090",
        promotion_id=promotion_id,
        project_id=PROJECT_ID,
        repository=REPOSITORY,
        canonical_ref="refs/heads/review-target",
        original_visible_unverified_result_digest="sha256:" + "1" * 64,
        target_commit=CommitRef(repository=REPOSITORY, sha="b" * 40),
        authorization_id="rma_018f47c1-7b2c-7abc-8def-123456789089",
        reconciliation_subject_digest="sha256:" + "2" * 64,
        original_binding_id="cpb_018f47c1-7b2c-7abc-8def-123456789088",
        original_binding_revision=1,
        original_binding_digest="sha256:" + "3" * 64,
        original_policy_digest="sha256:" + "4" * 64,
        original_governance_basis_digest="sha256:" + "5" * 64,
        current_required_check_observation_digest="sha256:" + "6" * 64,
        current_source_control_observation_digest="sha256:" + "7" * 64,
        reconciled_at=NOW,
        reconciled_by=ActorRef(
            kind=ActorKind.HUMAN,
            id="act_018f47c1-7b2c-7abc-8def-123456789092",
        ),
    )
    attempt = PromotionAttemptInspection(
        promotion_id=promotion_id,
        intent=None,
        original_authority_status=PromotionIntentAuthorityStatus.UNKNOWN,
        result=None,
        reconciliations=(reconciliation,),
    )
    target = CanonicalTargetInspection(
        repository=REPOSITORY,
        canonical_ref="refs/heads/review-target",
        binding_resolution=CanonicalPromotionPolicyBindingResolution.UNKNOWN_OR_INVALID,
        current_binding=None,
        health=CanonicalRefHealth.UNKNOWN,
        current_authorizability=PromotionAuthorizability.UNKNOWN,
        current_eligibility=PromotionEligibilityState.UNKNOWN,
        reconciliation_preparation_state=None,
        live_observation_status=LiveObservationStatus.UNAVAILABLE,
        live_source_control_observation=None,
        live_source_control_conformance=PromotionPropertyOutcome.UNKNOWN,
        promotion_attempts=(attempt,),
    )
    board_with_history = board.model_copy(
        update={
            "canonical_governance": CanonicalGovernanceInspection(
                durable_target_established=False,
                targets=(target,),
            )
        }
    )

    html = render_project_board(board_with_history)

    assert promotion_id in html
    assert "Canonical health is UNKNOWN; stored causal validity is not established." in html
    assert reconciliation.reconciliation_id in html
    assert reconciliation.authorization_id in html
    assert reconciliation.original_visible_unverified_result_digest in html


def test_slice_situation_shows_declared_boundary_and_model_limitations_first() -> None:
    _, detail = _fixture()

    html = render_slice_detail(detail)

    situation_position = html.index("Slice Situation")
    governance_position = html.index("Governance status")
    definition_position = html.index("<h2>Definition</h2>")
    assert situation_position < governance_position < definition_position
    assert "&lt;script&gt;scope()&lt;/script&gt;" in html
    assert "&lt;b&gt;not HTML&lt;/b&gt;" in html
    assert "Required acceptance criteria" in html
    assert "Optional acceptance criteria" in html
    assert "A01" in html and "A02" in html
    assert "Explicit objective: NOT REPRESENTED IN CURRENT RELAY MODEL" in html
    assert "Investment appetite: NOT REPRESENTED IN CURRENT RELAY MODEL" in html
    assert "Automated scope-drift assessment: NOT REPRESENTED" in html
    assert "Convergence assessment: NOT REPRESENTED" in html
    assert "WITHIN SCOPE" not in html
    assert "NO DRIFT" not in html
    assert "ARCHITECTURE HEALTHY" not in html
    assert "READY is a phase and does not grant execution authorization" in html


def test_governance_status_precedes_definition_and_summarizes_ready_lifecycle() -> None:
    _, detail = _fixture()
    html = render_slice_detail(detail)
    summary = _governance_summary(detail)

    assert html.index("Governance status") < html.index("<section><h2>Definition</h2>")
    assert "Lifecycle: <strong>READY</strong>" in summary
    assert "validity STALE; blockage BLOCKED; revision 4" in summary
    assert "READY is a lifecycle phase; it does not grant execution authorization." in summary
    assert "&lt;script&gt;blocker()&lt;/script&gt;" in summary
    assert "READY to execute" not in summary


def test_governance_status_preserves_missing_lifecycle_and_grant_absence() -> None:
    _, detail = _fixture()
    detail = detail.model_copy(update={"lifecycle": None})

    summary = _governance_summary(detail)

    assert "Lifecycle: NOT_STARTED — no lifecycle record." in summary
    assert "Current authorization grants: none projected." in summary
    assert "NOT AUTHORIZED" not in summary


def test_governance_status_shows_matching_gate_light_and_typed_reasons() -> None:
    _, detail = _fixture()
    gate = detail.outgoing_gates[0].model_copy(
        update={
            "evaluation_basis_status": EvaluationBasisStatus.MATCHING_DURABLE_BASIS,
            "evaluation_light": TrafficLight.GREEN,
            "evaluation_reasons": (GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
        }
    )
    detail = detail.model_copy(update={"outgoing_gates": (gate,)})

    summary = _governance_summary(detail)

    assert f"Gate <code>{GATE_ID}</code> revision 1" in summary
    assert "Target lifecycle phase: IMPLEMENTING" in summary
    assert "authorization required: yes" in summary
    assert "Evaluation-basis status: matching durable basis." in summary
    assert 'class="gate-light green"' in summary
    assert "Current traffic light: <strong>GREEN</strong>" in summary
    assert "BLOCKING: EVALUATION_REQUIRED" in summary


def test_governance_status_hides_stale_light_and_distinguishes_other_gate_states() -> None:
    _, detail = _fixture()
    stale_gate = detail.outgoing_gates[0].model_copy(
        update={
            "evaluation_light": TrafficLight.RED,
            "evaluation_reasons": (GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
        }
    )
    stale_summary = _governance_summary(detail.model_copy(update={"outgoing_gates": (stale_gate,)}))
    not_evaluated_gate = stale_gate.model_copy(
        update={"evaluation_basis_status": EvaluationBasisStatus.NOT_EVALUATED}
    )
    not_evaluated_summary = _governance_summary(
        detail.model_copy(update={"outgoing_gates": (not_evaluated_gate,)})
    )
    not_applicable_gate = stale_gate.model_copy(
        update={"evaluation_basis_status": EvaluationBasisStatus.NOT_APPLICABLE}
    )
    not_applicable_summary = _governance_summary(
        detail.model_copy(update={"outgoing_gates": (not_applicable_gate,)})
    )

    assert "Evaluation: stale durable basis — historical traffic lights are not current." in (
        stale_summary
    )
    assert "RED" not in stale_summary
    assert "Evaluation: not evaluated." in not_evaluated_summary
    assert "Evaluation: not applicable." in not_applicable_summary


def test_governance_status_separates_human_authority_evidence_and_escapes_text() -> None:
    _, detail = _fixture()
    display_actor = ACTOR.model_copy(update={"display_name": '<img src=x onerror="grant()">'})
    grant = AuthorizationGrant(
        authorization_id=AUTHORIZATION_ID,
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        gate_id=GATE_ID,
        gate_revision=1,
        actor=display_actor,
        granted_at=NOW,
        reason="test grant",
    )
    approval = HumanApprovalDecision(
        decision_id=HUMAN_DECISION_ID,
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        gate_id=GATE_ID,
        gate_revision=1,
        lifecycle_revision=4,
        governance_revision=2,
        actor=ACTOR,
        occurred_at=NOW,
        decision=HumanApprovalValue.APPROVE,
        reason="approved",
    )
    choice = HumanChoiceDecision(
        decision_id=CHOICE_DECISION_ID,
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        selected_gate_id=GATE_ID,
        selected_gate_revision=1,
        choice_gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
        lifecycle_revision=4,
        governance_revision=2,
        actor=ACTOR,
        occurred_at=NOW,
        reason="chosen",
    )
    human_actions = HumanActionProjection(
        current_authorizations=(grant,),
        current_approval_decisions=(approval,),
        current_choice=choice,
        human_hold=(BlockReason(code="PAUSED", summary="<script>hold()</script>"),),
    )
    detail = detail.model_copy(update={"human_actions": human_actions})

    summary = _governance_summary(detail)

    assert AUTHORIZATION_ID in summary and f"gate <code>{GATE_ID}</code> revision 1" in summary
    assert f"actor &lt;img src=x onerror=&quot;grant()&quot;&gt;; granted {NOW}" in summary
    assert f"Approval decision <code>{HUMAN_DECISION_ID}</code>: APPROVE" in summary
    assert f"Choice decision <code>{CHOICE_DECISION_ID}</code> selected gate" in summary
    assert "Unblocked, READY, authorization grants, and approval decisions are distinct" in summary
    assert "PAUSED: &lt;script&gt;hold()&lt;/script&gt;" in summary
    assert '<img src=x onerror="grant()">' not in summary
    assert "<script>hold()" not in summary


def test_governance_status_separates_result_evaluation_technical_decision_and_promotion() -> None:
    _, detail = _fixture()
    result = SliceResultRecord(
        result_id=RESULT_ID,
        slice_id=SLICE_ID,
        slice_definition_revision=1,
        source_baseline_id=BASELINE_ID,
        result_baseline_id=RESULT_BASELINE_ID,
        lifecycle_revision=4,
        recorded_by=ACTOR,
        recorded_at=NOW,
        reason="verified result",
    )
    evaluation = ManualEvaluationRecord(
        evaluation_id=EVALUATION_ID,
        slice_id=SLICE_ID,
        result_id=RESULT_ID,
        result_baseline_id=RESULT_BASELINE_ID,
        source_baseline_id=BASELINE_ID,
        slice_definition_revision=1,
        lifecycle_revision=4,
        gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
        prior_gate_evaluation_record_id=None,
        evaluator=ACTOR,
        evaluated_at=NOW,
        outcome=EvaluationOutcome.ACCEPT,
        evidence_ids=(EVIDENCE_ID,),
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
        summary="evaluated result",
    )
    technical_decision = HumanApprovalDecision(
        decision_id=HUMAN_DECISION_ID,
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        gate_id=GATE_ID,
        gate_revision=1,
        lifecycle_revision=4,
        governance_revision=2,
        actor=ACTOR,
        occurred_at=NOW,
        decision=HumanApprovalValue.APPROVE,
        reason="technical decision",
    )
    accepted = AcceptedSliceResult(
        slice_id=SLICE_ID,
        result_id=RESULT_ID,
        result_baseline_id=BASELINE_ID,
        commit="a" * 40,
        manual_evaluation_id=EVALUATION_ID,
        human_approval_decision_id=HUMAN_DECISION_ID,
        accepted_execution_id=EXECUTION_ID,
        accepted_at=NOW,
    )
    result_baseline = Baseline(
        id=RESULT_BASELINE_ID,
        project_id=PROJECT_ID,
        commit=CommitRef(repository=REPOSITORY, sha="c" * 40),
        artifact_ids=(),
        decision_ids=(),
    )
    source_baseline = Baseline(
        id=BASELINE_ID,
        project_id=PROJECT_ID,
        commit=CommitRef(repository=REPOSITORY, sha="b" * 40),
        artifact_ids=(),
        decision_ids=(),
    )
    evidence = Evidence(
        id=EVIDENCE_ID,
        claim="supports result",
        recorded_by=ACTOR,
        recorded_at=NOW,
        source_commit=CommitRef(repository=REPOSITORY, sha="d" * 40),
    )
    memory = DevelopmentMemoryProjection(
        slice_id=SLICE_ID,
        source_baseline=source_baseline,
        result_history=(result,),
        evaluation_history=(evaluation,),
        evidence=(evidence,),
        accepted_results=(accepted,),
    )
    manual_evaluation = ManualEvaluationProjection(
        current_result=result,
        current_result_baseline=result_baseline,
        current_evaluation=evaluation,
        current_technical_decision=technical_decision,
        accepted_result=accepted,
        development_memory=memory,
    )
    detail = detail.model_copy(update={"manual_evaluation": manual_evaluation})

    summary = _governance_summary(detail)

    assert "<h4>Engineering result</h4>" in summary
    assert f"Result <code>{RESULT_ID}</code>; result baseline" in summary
    assert f"Exact result commit: <code>{'c' * 40}</code>" in summary
    assert "<h4>Evaluator decision</h4>" in summary
    assert f"Evaluation <code>{EVALUATION_ID}</code>; outcome ACCEPT" in summary
    assert f"result <code>{RESULT_ID}</code>" in summary
    assert "<h4>Human technical decision</h4>" in summary
    assert f"Decision <code>{HUMAN_DECISION_ID}</code>: APPROVE" in summary
    assert "<h4>Accepted-result promotion</h4>" in summary
    assert f"exact accepted commit <code>{'a' * 40}</code>" in summary
    assert f"manual evaluation <code>{EVALUATION_ID}</code>" in summary
    assert f"Human approval decision <code>{HUMAN_DECISION_ID}</code>" in summary
    assert f"accepted execution <code>{EXECUTION_ID}</code>" in summary
    assert "Engineering result, evaluator decision, Human technical decision, and" in summary
    assert f"Development memory source baseline: <code>{BASELINE_ID}</code>" in summary
    assert (
        "Result records: 1; evaluation records: 1; Evidence items: 1; accepted results: 1."
        in summary
    )


def test_governance_summary_keeps_existing_detail_sections_intact() -> None:
    _, detail = _fixture()
    html = render_slice_detail(detail)

    assert "<section><h2>Definition</h2>" in html
    assert "<section><h2>Lifecycle</h2>" in html
    assert "<section><h2>Evaluation and gates</h2>" in html
    assert 'id="human-actions-heading">Human actions</h2>' in html
    assert 'id="manual-evaluation-heading">Manual evaluation and result</h2>' in html
    assert "<section><h2>Execution evidence</h2>" in html


def test_project_index_escapes_project_data_and_search_is_escaped() -> None:
    board, _ = _fixture()
    from relay_engine.board.models import BoardProjection, ProjectSummary

    index = render_project_index(
        BoardProjection(
            projects=(
                ProjectSummary(
                    project=board.project,
                    definition_revision=2,
                    slice_count=1,
                    origin_resolution=board.project_origin_resolution,
                ),
            )
        )
    )
    assert "<script>project()" not in index
    assert "&lt;script&gt;project()&lt;/script&gt;" in index
    filtered = render_project_board(board, query='" autofocus onfocus="alert(1)')
    assert 'value="&quot; autofocus onfocus=&quot;alert(1)"' in filtered
    assert 'value="" autofocus' not in filtered


def test_pre_genesis_without_lifecycle_renders_outside_not_started_lane() -> None:
    board, _ = _fixture()
    card = board.cards[0].model_copy(
        update={
            "lane": None,
            "lifecycle": None,
            "origin_resolution": make_test_origin_resolution(
                OriginSubjectType.SLICE,
                SLICE_ID,
                project_id=PROJECT_ID,
                origin=OperationalOrigin.PRE_GENESIS,
            ),
        }
    )
    projection = board.model_copy(
        update={
            "project_origin_resolution": make_test_origin_resolution(
                OriginSubjectType.PROJECT,
                PROJECT_ID,
                origin=OperationalOrigin.PRE_GENESIS,
            ),
            "cards": (card,),
            "situation": project_project_situation((card,)),
        }
    )

    html = render_project_board(projection)

    assert "PRE-GENESIS — NO RELAY LIFECYCLE (1)" in html
    assert "NOT STARTED</h3><p>None." in html
    assert "NO RELAY LIFECYCLE — ORIGIN NOT ESTABLISHED" not in html


def test_slice_situation_summarizes_completed_governed_movements_in_revision_order() -> None:
    _, detail = _fixture()
    first = _execution_record(
        execution_id="exec_018f47c1-7b2c-7abc-8def-123456789051",
        event_id="evt_018f47c1-7b2c-7abc-8def-123456789053",
        evaluation_record_id="geval_018f47c1-7b2c-7abc-8def-123456789055",
        source_revision=0,
        resulting_revision=1,
        selected_gate_revision=1,
        occurred_at=NOW,
    )
    second = _execution_record(
        execution_id="exec_018f47c1-7b2c-7abc-8def-123456789052",
        event_id="evt_018f47c1-7b2c-7abc-8def-123456789054",
        evaluation_record_id="geval_018f47c1-7b2c-7abc-8def-123456789056",
        source_revision=1,
        resulting_revision=2,
        selected_gate_revision=2,
        occurred_at=datetime(2026, 10, 3, tzinfo=UTC),
    )
    detail = detail.model_copy(update={"relevant_execution_records": (second, first)})

    html = render_slice_detail(detail)
    completed_start = html.index("<h3>What has completed</h3>")
    completed_end = html.index("<h3>What remains deterministically visible</h3>")
    completed = html[completed_start:completed_end]

    assert "Lifecycle phase: <strong>READY</strong>" in html
    assert "Completed governed lifecycle movements" in completed
    assert "revision 0 → 1" in completed
    assert "revision 1 → 2" in completed
    assert completed.index("revision 0 → 1") < completed.index("revision 1 → 2")
    assert first.execution_id in completed
    assert second.execution_id in completed
    assert f"{GATE_ID}@r1" in completed
    assert f"{GATE_ID}@r2" in completed
    assert str(NOW) in completed
    assert str(second.occurred_at) in completed

    situation_position = html.index('id="slice-situation-heading"')
    execution_evidence_position = html.index("<section><h2>Execution evidence</h2>")
    assert situation_position < execution_evidence_position
    assert "Execution evidence" in html
    assert first.execution_id in html[execution_evidence_position:]
    assert second.execution_id in html[execution_evidence_position:]


def test_active_slice_with_no_execution_records_has_truthful_empty_completion_state() -> None:
    _, detail = _fixture()

    html = render_slice_detail(detail)
    completed_start = html.index("<h3>What has completed</h3>")
    completed_end = html.index("<h3>What remains deterministically visible</h3>")
    completed = html[completed_start:completed_end]

    assert "Lifecycle phase: <strong>READY</strong>" in html
    assert (
        "No completed governed movement, terminal lifecycle state, accepted result, "
        "or evaluation record is projected."
    ) in completed
    assert "Completed governed lifecycle movements" not in completed
