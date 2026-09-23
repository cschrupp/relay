"""Contract tests for Slice 0.4 gate evaluation and governed execution."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from relay_engine.domain.ids import new_id
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.governance import (
    AuthorizationGrant,
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateReason,
    GateReasonCode,
    GateReasonKind,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverNotExecutable,
    HandoverPolicy,
    HumanApprovalDecision,
    HumanApprovalValue,
    HumanChoiceDecision,
    InvalidGateSet,
    QualityCheckResult,
    QualityCheckStatus,
    ReviewPolicy,
    RiskStatus,
    ToolchainChangeStatus,
    TrafficLight,
    evaluate_handover_gates,
    execute_handover,
)
from relay_engine.lifecycle import (
    Blockage,
    BlockageStatus,
    BlockReason,
    InvalidLifecycleOperation,
    InvalidPhaseTransition,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
    transition_phase,
    validate_phase_transition,
)

BASELINE = "base_00000000-0000-0000-0000-000000000001"
OTHER_BASELINE = "base_00000000-0000-0000-0000-000000000002"
SLICE = "slc_00000000-0000-0000-0000-000000000001"
OTHER_SLICE = "slc_00000000-0000-0000-0000-000000000002"
GATE_A = "gate_00000000-0000-0000-0000-000000000001"
GATE_B = "gate_00000000-0000-0000-0000-000000000002"
ACTOR = ActorRef(id="act_00000000-0000-0000-0000-000000000001", kind=ActorKind.HUMAN)
NOW = datetime(2026, 1, 1, tzinfo=UTC)


def lifecycle(
    phase: LifecyclePhase = LifecyclePhase.READY,
    *,
    revision: int = 4,
    validity: LifecycleValidity = LifecycleValidity.CURRENT,
) -> SliceLifecycle:
    return SliceLifecycle(
        slice_id=SLICE,
        phase=phase,
        validity=validity,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=revision,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )


def gate(
    gate_id: str = GATE_A,
    *,
    revision: int = 1,
    target: LifecyclePhase = LifecyclePhase.IMPLEMENTING,
    policy: HandoverPolicy = HandoverPolicy.AUTO,
    **changes: object,
) -> HandoverGate:
    values: dict[str, object] = {
        "gate_id": gate_id,
        "revision": revision,
        "key": "test-gate",
        "slice_id": SLICE,
        "baseline_id": BASELINE,
        "source_phase": LifecyclePhase.READY,
        "target_phase": target,
        "policy": policy,
    }
    values.update(changes)
    return HandoverGate.model_validate(values)


def context(
    *,
    gates_baseline: str = BASELINE,
    lifecycle_value: SliceLifecycle | None = None,
    governance_revision: int = 2,
    **changes: object,
) -> HandoverContext:
    values: dict[str, object] = {
        "baseline_id": gates_baseline,
        "governance_revision": governance_revision,
        "lifecycle": lifecycle_value or lifecycle(),
        "change_surface_status": ChangeSurfaceStatus.WITHIN_DECLARED,
        "risk_status": RiskStatus.CLEAR,
        "toolchain_change_status": ToolchainChangeStatus.NONE,
    }
    values.update(changes)
    return HandoverContext.model_validate(values)


def approval(
    gate_id: str = GATE_A,
    *,
    value: HumanApprovalValue = HumanApprovalValue.APPROVE,
    lifecycle_revision: int = 4,
    governance_revision: int = 2,
    baseline_id: str = BASELINE,
    gate_revision: int = 1,
    occurred_at: datetime = NOW,
) -> HumanApprovalDecision:
    return HumanApprovalDecision(
        decision_id=new_id("hdec_"),
        slice_id=SLICE,
        baseline_id=baseline_id,
        gate_id=gate_id,
        gate_revision=gate_revision,
        lifecycle_revision=lifecycle_revision,
        governance_revision=governance_revision,
        actor=ACTOR,
        occurred_at=occurred_at,
        decision=value,
        reason="reviewed",
    )


def grant(
    gate_id: str = GATE_A,
    *,
    baseline_id: str = BASELINE,
    gate_revision: int = 1,
    granted_at: datetime = NOW,
) -> AuthorizationGrant:
    return AuthorizationGrant(
        authorization_id=new_id("auth_"),
        slice_id=SLICE,
        baseline_id=baseline_id,
        gate_id=gate_id,
        gate_revision=gate_revision,
        actor=ACTOR,
        granted_at=granted_at,
        reason="authorized",
    )


def code_set(result: object) -> set[GateReasonCode]:
    return {reason.code for reason in result.reasons}  # type: ignore[attr-defined]


def test_auto_gate_is_green_but_readiness_is_not_an_authorization_field() -> None:
    result = evaluate_handover_gates((gate(),), context())[0]
    assert result.light is TrafficLight.GREEN
    assert result.reasons == ()
    assert "traffic_light" not in SliceLifecycle.model_fields


def test_gate_policy_values_and_reason_kind_mapping_are_fixed() -> None:
    assert [item.value for item in TrafficLight] == ["GREEN", "YELLOW", "RED"]
    assert GateReasonCode.HUMAN_APPROVAL_REQUIRED.value == "HUMAN_APPROVAL_REQUIRED"
    assert GateReasonKind.BLOCKING.value == "BLOCKING"


@pytest.mark.parametrize(
    ("changes", "reason", "light"),
    [
        (
            {"authorization_required": True},
            GateReasonCode.AUTHORIZATION_REQUIRED,
            TrafficLight.YELLOW,
        ),
        (
            {"required_artifact_ids": ("art_00000000-0000-0000-0000-000000000001",)},
            GateReasonCode.MISSING_REQUIRED_ARTIFACT,
            TrafficLight.RED,
        ),
        (
            {"required_evidence_ids": ("evd_00000000-0000-0000-0000-000000000001",)},
            GateReasonCode.MISSING_REQUIRED_EVIDENCE,
            TrafficLight.RED,
        ),
        (
            {"required_evaluation_outcomes": (EvaluationOutcome.ACCEPT,)},
            GateReasonCode.EVALUATION_REQUIRED,
            TrafficLight.RED,
        ),
        (
            {"required_quality_checks": ("pytest",)},
            GateReasonCode.QUALITY_CHECK_MISSING,
            TrafficLight.RED,
        ),
        (
            {"change_surface_policy": ReviewPolicy.BLOCK},
            GateReasonCode.CHANGE_SURFACE_BLOCKED,
            TrafficLight.RED,
        ),
        ({"risk_policy": ReviewPolicy.BLOCK}, GateReasonCode.RISK_BLOCKED, TrafficLight.RED),
    ],
)
def test_missing_or_blocked_facts_have_expected_light(
    changes: dict[str, object], reason: GateReasonCode, light: TrafficLight
) -> None:
    facts: dict[str, object] = {}
    if "change_surface_policy" in changes:
        facts["change_surface_status"] = ChangeSurfaceStatus.MATERIAL_DEVIATION
    if "risk_policy" in changes:
        facts["risk_status"] = RiskStatus.FLAGGED
    result = evaluate_handover_gates((gate(**changes),), context(**facts))[0]
    assert result.light is light
    assert reason in code_set(result)


def test_authorization_is_durable_but_binds_baseline_and_gate_revision() -> None:
    authorized_gate = gate(authorization_required=True)
    authorized = grant()
    first = context(authorization_grants=(authorized,))
    assert evaluate_handover_gates((authorized_gate,), first)[0].light is TrafficLight.GREEN
    later = context(
        lifecycle_value=lifecycle(revision=5),
        governance_revision=3,
        authorization_grants=(authorized,),
    )
    assert evaluate_handover_gates((authorized_gate,), later)[0].light is TrafficLight.GREEN
    stale_revision = evaluate_handover_gates(
        (gate(authorization_required=True, revision=2),), later
    )[0]
    assert stale_revision.light is TrafficLight.YELLOW
    assert GateReasonCode.AUTHORIZATION_STALE in code_set(stale_revision)
    stale_baseline = evaluate_handover_gates(
        (gate(authorization_required=True, baseline_id=OTHER_BASELINE),),
        context(authorization_grants=(authorized,)),
    )[0]
    assert stale_baseline.light is TrafficLight.RED
    assert code_set(stale_baseline) == {GateReasonCode.BASELINE_MISMATCH}


def test_authorization_may_exist_while_gate_is_red_then_become_usable() -> None:
    policy = gate(
        authorization_required=True,
        required_artifact_ids=("art_00000000-0000-0000-0000-000000000001",),
    )
    authorized = grant()
    assert (
        evaluate_handover_gates((policy,), context(authorization_grants=(authorized,)))[0].light
        is TrafficLight.RED
    )
    available = context(
        authorization_grants=(authorized,),
        available_artifact_ids=("art_00000000-0000-0000-0000-000000000001",),
    )
    assert evaluate_handover_gates((policy,), available)[0].light is TrafficLight.GREEN


def test_human_approval_and_rejection_are_bound_to_both_revisions() -> None:
    policy = gate(policy=HandoverPolicy.HUMAN_APPROVAL)
    assert evaluate_handover_gates((policy,), context())[0].light is TrafficLight.YELLOW
    current = approval()
    assert (
        evaluate_handover_gates((policy,), context(human_decisions=(current,)))[0].light
        is TrafficLight.GREEN
    )
    stale = approval(governance_revision=1)
    result = evaluate_handover_gates((policy,), context(human_decisions=(stale,)))[0]
    assert GateReasonCode.HUMAN_APPROVAL_REQUIRED in code_set(result)
    assert GateReasonCode.HUMAN_DECISION_STALE in code_set(result)
    rejected = approval(value=HumanApprovalValue.REJECT)
    result = evaluate_handover_gates((policy,), context(human_decisions=(rejected,)))[0]
    assert result.light is TrafficLight.RED
    assert GateReasonCode.HUMAN_REJECTED in code_set(result)


def test_hard_stop_overrides_auto_but_approval_cannot_override_red() -> None:
    stopped = gate(hard_stop=True)
    assert evaluate_handover_gates((stopped,), context())[0].light is TrafficLight.YELLOW
    assert (
        evaluate_handover_gates((stopped,), context(human_decisions=(approval(),)))[0].light
        is TrafficLight.GREEN
    )
    invalid = gate(hard_stop=True, required_quality_checks=("pytest",))
    result = evaluate_handover_gates(
        (invalid,),
        context(
            human_decisions=(approval(),),
            quality_checks=(QualityCheckResult(key="pytest", status=QualityCheckStatus.FAIL),),
        ),
    )[0]
    assert result.light is TrafficLight.RED


def test_human_choice_is_set_bound_and_nonselected_viable_gate_is_red() -> None:
    first = gate(GATE_A, policy=HandoverPolicy.HUMAN_CHOICE)
    second = gate(GATE_B, policy=HandoverPolicy.HUMAN_CHOICE)
    decision = HumanChoiceDecision(
        decision_id=new_id("hdec_"),
        slice_id=SLICE,
        baseline_id=BASELINE,
        selected_gate_id=GATE_A,
        selected_gate_revision=1,
        choice_gate_refs=(
            GateRevisionRef(gate_id=GATE_A, gate_revision=1),
            GateRevisionRef(gate_id=GATE_B, gate_revision=1),
        ),
        lifecycle_revision=4,
        governance_revision=2,
        actor=ACTOR,
        occurred_at=NOW,
        reason="selected route",
    )
    evaluations = evaluate_handover_gates((second, first), context(human_decisions=(decision,)))
    assert [item.gate_id for item in evaluations] == [GATE_A, GATE_B]
    assert evaluations[0].light is TrafficLight.GREEN
    assert evaluations[1].light is TrafficLight.RED
    assert GateReasonCode.NOT_SELECTED_BY_HUMAN in code_set(evaluations[1])
    changed = gate("gate_00000000-0000-0000-0000-000000000003", policy=HandoverPolicy.HUMAN_CHOICE)
    stale = evaluate_handover_gates((first, changed), context(human_decisions=(decision,)))
    assert all(GateReasonCode.HUMAN_CHOICE_REQUIRED in code_set(item) for item in stale)


def test_invalid_choice_cannot_bypass_red_prerequisite() -> None:
    policy = gate(policy=HandoverPolicy.HUMAN_CHOICE, required_quality_checks=("pytest",))
    decision = HumanChoiceDecision(
        decision_id=new_id("hdec_"),
        slice_id=SLICE,
        baseline_id=BASELINE,
        selected_gate_id=GATE_A,
        selected_gate_revision=1,
        choice_gate_refs=(GateRevisionRef(gate_id=GATE_A, gate_revision=1),),
        lifecycle_revision=4,
        governance_revision=2,
        actor=ACTOR,
        occurred_at=NOW,
        reason="selected route",
    )
    result = evaluate_handover_gates((policy,), context(human_decisions=(decision,)))[0]
    assert result.light is TrafficLight.RED
    assert GateReasonCode.QUALITY_CHECK_MISSING in code_set(result)


def test_hard_stop_on_human_choice_is_satisfied_by_the_current_choice() -> None:
    policy = gate(policy=HandoverPolicy.HUMAN_CHOICE, hard_stop=True)
    decision = HumanChoiceDecision(
        decision_id=new_id("hdec_"),
        slice_id=SLICE,
        baseline_id=BASELINE,
        selected_gate_id=GATE_A,
        selected_gate_revision=1,
        choice_gate_refs=(GateRevisionRef(gate_id=GATE_A, gate_revision=1),),
        lifecycle_revision=4,
        governance_revision=2,
        actor=ACTOR,
        occurred_at=NOW,
        reason="selected route",
    )
    result = evaluate_handover_gates((policy,), context(human_decisions=(decision,)))[0]
    assert result.light is TrafficLight.GREEN
    assert GateReasonCode.HARD_STOP_REQUIRES_HUMAN not in code_set(result)


def test_multiple_green_gates_are_all_red_with_pairwise_reasons() -> None:
    results = evaluate_handover_gates((gate(GATE_B), gate(GATE_A)), context())
    assert [item.light for item in results] == [TrafficLight.RED, TrafficLight.RED]
    assert results[0].reasons[-1].subject == GATE_B
    assert results[1].reasons[-1].subject == GATE_A
    assert all(GateReasonCode.MULTIPLE_EXECUTABLE_PATHS in code_set(item) for item in results)


def test_baseline_validation_and_result_order_are_deterministic() -> None:
    first = gate(GATE_A)
    second = gate(GATE_B)
    with pytest.raises(InvalidGateSet):
        evaluate_handover_gates((first, gate(GATE_B, baseline_id=OTHER_BASELINE)), context())
    noncurrent = evaluate_handover_gates(
        (gate(GATE_B, baseline_id=OTHER_BASELINE), gate(GATE_A, baseline_id=OTHER_BASELINE)),
        context(),
    )
    assert [item.gate_id for item in noncurrent] == [GATE_A, GATE_B]
    assert all(item.light is TrafficLight.RED for item in noncurrent)
    assert all(code_set(item) == {GateReasonCode.BASELINE_MISMATCH} for item in noncurrent)
    assert evaluate_handover_gates((first, second), context()) == evaluate_handover_gates(
        (second, first), context()
    )


def test_dependency_evaluation_quality_change_risk_and_toolchain_rules() -> None:
    dependency = SliceLifecycle(
        slice_id=OTHER_SLICE,
        phase=LifecyclePhase.ACCEPTED,
        validity=LifecycleValidity.STALE,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=1,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    policy = gate(
        required_dependency_slice_ids=(OTHER_SLICE,),
        required_evaluation_outcomes=(EvaluationOutcome.ACCEPT,),
        required_quality_checks=("pytest",),
    )
    facts = context(
        dependency_lifecycles=(dependency,),
        evaluation_outcome=EvaluationOutcome.REWORK,
        quality_checks=(QualityCheckResult(key="pytest", status=QualityCheckStatus.FAIL),),
        toolchain_change_status=ToolchainChangeStatus.UNAUTHORIZED,
    )
    result = evaluate_handover_gates((policy,), facts)[0]
    assert {
        GateReasonCode.DEPENDENCY_STALE,
        GateReasonCode.EVALUATION_OUTCOME_NOT_ALLOWED,
        GateReasonCode.QUALITY_CHECK_FAILED,
        GateReasonCode.UNAUTHORIZED_TOOLCHAIN_CHANGE,
    } <= code_set(result)
    passed = context(
        dependency_lifecycles=(
            dependency.model_copy(update={"validity": LifecycleValidity.CURRENT}),
        ),
        evaluation_outcome=EvaluationOutcome.ACCEPT,
        quality_checks=(QualityCheckResult(key="pytest", status=QualityCheckStatus.PASS),),
    )
    assert evaluate_handover_gates((policy,), passed)[0].light is TrafficLight.GREEN


def test_absent_and_unaccepted_dependencies_are_distinct_blockers() -> None:
    policy = gate(required_dependency_slice_ids=(OTHER_SLICE,))
    missing = evaluate_handover_gates((policy,), context())[0]
    assert missing.reasons[0].code is GateReasonCode.DEPENDENCY_MISSING
    active = SliceLifecycle(
        slice_id=OTHER_SLICE,
        phase=LifecyclePhase.IMPLEMENTING,
        validity=LifecycleValidity.CURRENT,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=2,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    not_accepted = evaluate_handover_gates((policy,), context(dependency_lifecycles=(active,)))[0]
    assert not_accepted.reasons[0].code is GateReasonCode.DEPENDENCY_NOT_ACCEPTED


@pytest.mark.parametrize(
    ("surface", "risk", "expected"),
    [
        (
            ChangeSurfaceStatus.MATERIAL_DEVIATION,
            RiskStatus.CLEAR,
            GateReasonCode.CHANGE_SURFACE_REVIEW_REQUIRED,
        ),
        (
            ChangeSurfaceStatus.WITHIN_DECLARED,
            RiskStatus.FLAGGED,
            GateReasonCode.RISK_REVIEW_REQUIRED,
        ),
    ],
)
def test_review_policies_need_current_positive_approval(
    surface: ChangeSurfaceStatus, risk: RiskStatus, expected: GateReasonCode
) -> None:
    policy = gate(
        change_surface_policy=ReviewPolicy.HUMAN_REVIEW, risk_policy=ReviewPolicy.HUMAN_REVIEW
    )
    result = evaluate_handover_gates(
        (policy,), context(change_surface_status=surface, risk_status=risk)
    )[0]
    assert result.light is TrafficLight.YELLOW
    assert expected in code_set(result)
    approved = evaluate_handover_gates(
        (policy,),
        context(change_surface_status=surface, risk_status=risk, human_decisions=(approval(),)),
    )[0]
    assert approved.light is TrafficLight.GREEN


def test_auto_notify_has_auto_light_semantics_without_side_effects() -> None:
    automatic = evaluate_handover_gates((gate(policy=HandoverPolicy.AUTO),), context())[0]
    notify = evaluate_handover_gates((gate(policy=HandoverPolicy.AUTO_NOTIFY),), context())[0]
    assert notify == automatic


def test_stale_authorization_is_yellow_when_baseline_is_current() -> None:
    policy = gate(authorization_required=True)
    stale = grant(baseline_id=OTHER_BASELINE)
    result = evaluate_handover_gates((policy,), context(authorization_grants=(stale,)))[0]
    assert result.light is TrafficLight.YELLOW
    assert GateReasonCode.AUTHORIZATION_STALE in code_set(result)


def test_choice_stales_on_governance_revision_and_gate_revision() -> None:
    policy = gate(policy=HandoverPolicy.HUMAN_CHOICE)
    choice = HumanChoiceDecision(
        decision_id=new_id("hdec_"),
        slice_id=SLICE,
        baseline_id=BASELINE,
        selected_gate_id=GATE_A,
        selected_gate_revision=1,
        choice_gate_refs=(GateRevisionRef(gate_id=GATE_A, gate_revision=1),),
        lifecycle_revision=4,
        governance_revision=2,
        actor=ACTOR,
        occurred_at=NOW,
        reason="selected route",
    )
    changed_context = evaluate_handover_gates(
        (policy,), context(governance_revision=3, human_decisions=(choice,))
    )[0]
    changed_gate = evaluate_handover_gates(
        (gate(policy=HandoverPolicy.HUMAN_CHOICE, revision=2),),
        context(human_decisions=(choice,)),
    )[0]
    for result in (changed_context, changed_gate):
        assert result.light is TrafficLight.YELLOW
        assert GateReasonCode.HUMAN_CHOICE_REQUIRED in code_set(result)
        assert GateReasonCode.HUMAN_DECISION_STALE in code_set(result)


def test_reason_cardinality_and_canonical_order() -> None:
    policy = gate(
        required_artifact_ids=(
            "art_00000000-0000-0000-0000-000000000002",
            "art_00000000-0000-0000-0000-000000000001",
        ),
        required_quality_checks=("ruff", "pytest"),
    )
    result = evaluate_handover_gates((policy,), context())[0]
    assert [reason.code for reason in result.reasons] == [
        GateReasonCode.MISSING_REQUIRED_ARTIFACT,
        GateReasonCode.MISSING_REQUIRED_ARTIFACT,
        GateReasonCode.QUALITY_CHECK_MISSING,
        GateReasonCode.QUALITY_CHECK_MISSING,
    ]
    assert [reason.subject for reason in result.reasons[:2]] == sorted(
        reason.subject for reason in result.reasons[:2]
    )


def test_gate_models_are_frozen_versioned_and_json_round_trip() -> None:
    policy = gate()
    assert policy.schema_version == 1
    assert type(policy).model_validate_json(policy.model_dump_json()) == policy
    assert type(policy).model_json_schema()["additionalProperties"] is False
    with pytest.raises(ValidationError):
        policy.revision = 2  # type: ignore[misc]
    with pytest.raises(ValidationError):
        gate(target=LifecyclePhase.READY)
    with pytest.raises(ValidationError):
        gate(target=LifecyclePhase.SUPERSEDED)
    with pytest.raises(ValidationError):
        AuthorizationGrant.model_validate(
            {
                **grant().model_dump(),
                "actor": ActorRef(id=ACTOR.id, kind=ActorKind.AGENT),
            }
        )


def test_governance_ids_extend_existing_explicit_generator() -> None:
    assert new_id("gate_").startswith("gate_")
    assert new_id("auth_").startswith("auth_")
    assert new_id("hdec_").startswith("hdec_")


def test_context_rejects_ambiguous_duplicate_projections() -> None:
    with pytest.raises(ValidationError):
        context(available_evidence_ids=("evd_00000000-0000-0000-0000-000000000001",) * 2)
    with pytest.raises(ValidationError):
        context(authorization_grants=(grant(), grant()))
    with pytest.raises(ValidationError):
        context(human_decisions=(approval(), approval()))


def test_review_allow_policy_does_not_block_material_deviation_or_flagged_risk() -> None:
    result = evaluate_handover_gates(
        (gate(change_surface_policy=ReviewPolicy.ALLOW, risk_policy=ReviewPolicy.ALLOW),),
        context(
            change_surface_status=ChangeSurfaceStatus.MATERIAL_DEVIATION,
            risk_status=RiskStatus.FLAGGED,
        ),
    )[0]
    assert result.light is TrafficLight.GREEN


def test_unauthorized_toolchain_is_red_even_with_approval() -> None:
    policy = gate(policy=HandoverPolicy.HUMAN_APPROVAL)
    result = evaluate_handover_gates(
        (policy,),
        context(
            human_decisions=(approval(),),
            toolchain_change_status=ToolchainChangeStatus.UNAUTHORIZED,
        ),
    )[0]
    assert result.light is TrafficLight.RED
    assert GateReasonCode.UNAUTHORIZED_TOOLCHAIN_CHANGE in code_set(result)


def test_human_approval_stales_when_lifecycle_revision_changes() -> None:
    policy = gate(policy=HandoverPolicy.HUMAN_APPROVAL)
    old = approval(lifecycle_revision=3)
    result = evaluate_handover_gates((policy,), context(human_decisions=(old,)))[0]
    assert GateReasonCode.HUMAN_DECISION_STALE in code_set(result)
    assert GateReasonCode.HUMAN_APPROVAL_REQUIRED in code_set(result)


def test_evaluation_outcome_routes_only_configured_results() -> None:
    policy = gate(required_evaluation_outcomes=(EvaluationOutcome.ACCEPT,))
    accepted = evaluate_handover_gates(
        (policy,), context(evaluation_outcome=EvaluationOutcome.ACCEPT)
    )[0]
    rework = evaluate_handover_gates(
        (policy,), context(evaluation_outcome=EvaluationOutcome.REWORK)
    )[0]
    assert accepted.light is TrafficLight.GREEN
    assert rework.light is TrafficLight.RED
    assert GateReasonCode.EVALUATION_OUTCOME_NOT_ALLOWED in code_set(rework)


def test_green_evaluation_serializes_with_bound_revisions_and_no_reasons() -> None:
    result = evaluate_handover_gates((gate(),), context())[0]
    assert result.lifecycle_revision == 4
    assert result.governance_revision == 2
    assert result.baseline_id == BASELINE
    assert result.reasons == ()
    assert type(result).model_validate_json(result.model_dump_json()) == result


def test_reason_code_order_and_kind_mapping_match_normative_enums() -> None:
    expected_order = [
        "BASELINE_MISMATCH",
        "SOURCE_PHASE_MISMATCH",
        "INVALID_LIFECYCLE_TRANSITION",
        "MISSING_REQUIRED_ARTIFACT",
        "MISSING_REQUIRED_EVIDENCE",
        "DEPENDENCY_MISSING",
        "DEPENDENCY_NOT_ACCEPTED",
        "DEPENDENCY_STALE",
        "EVALUATION_REQUIRED",
        "EVALUATION_OUTCOME_NOT_ALLOWED",
        "QUALITY_CHECK_MISSING",
        "QUALITY_CHECK_FAILED",
        "CHANGE_SURFACE_BLOCKED",
        "CHANGE_SURFACE_REVIEW_REQUIRED",
        "RISK_BLOCKED",
        "RISK_REVIEW_REQUIRED",
        "UNAUTHORIZED_TOOLCHAIN_CHANGE",
        "AUTHORIZATION_REQUIRED",
        "AUTHORIZATION_STALE",
        "HUMAN_APPROVAL_REQUIRED",
        "HUMAN_CHOICE_REQUIRED",
        "HUMAN_DECISION_STALE",
        "HARD_STOP_REQUIRES_HUMAN",
        "HUMAN_REJECTED",
        "NOT_SELECTED_BY_HUMAN",
        "MULTIPLE_EXECUTABLE_PATHS",
    ]
    assert [code.value for code in GateReasonCode] == expected_order
    human_codes = {
        GateReasonCode.CHANGE_SURFACE_REVIEW_REQUIRED,
        GateReasonCode.RISK_REVIEW_REQUIRED,
        GateReasonCode.AUTHORIZATION_REQUIRED,
        GateReasonCode.AUTHORIZATION_STALE,
        GateReasonCode.HUMAN_APPROVAL_REQUIRED,
        GateReasonCode.HUMAN_CHOICE_REQUIRED,
        GateReasonCode.HUMAN_DECISION_STALE,
        GateReasonCode.HARD_STOP_REQUIRES_HUMAN,
    }
    for code in GateReasonCode:
        subject = (
            "auth_00000000-0000-0000-0000-000000000001"
            if code is GateReasonCode.AUTHORIZATION_STALE
            else "hdec_00000000-0000-0000-0000-000000000001"
            if code in {GateReasonCode.HUMAN_DECISION_STALE, GateReasonCode.HUMAN_REJECTED}
            else "gate_00000000-0000-0000-0000-000000000001"
            if code
            in {GateReasonCode.NOT_SELECTED_BY_HUMAN, GateReasonCode.MULTIPLE_EXECUTABLE_PATHS}
            else "art_00000000-0000-0000-0000-000000000001"
            if code is GateReasonCode.MISSING_REQUIRED_ARTIFACT
            else "evd_00000000-0000-0000-0000-000000000001"
            if code is GateReasonCode.MISSING_REQUIRED_EVIDENCE
            else "slc_00000000-0000-0000-0000-000000000001"
            if code
            in {
                GateReasonCode.DEPENDENCY_MISSING,
                GateReasonCode.DEPENDENCY_NOT_ACCEPTED,
                GateReasonCode.DEPENDENCY_STALE,
            }
            else "pytest"
            if code in {GateReasonCode.QUALITY_CHECK_MISSING, GateReasonCode.QUALITY_CHECK_FAILED}
            else None
        )
        reason = GateReasonKind.HUMAN_ACTION if code in human_codes else GateReasonKind.BLOCKING
        assert GateReason(kind=reason, code=code, subject=subject).code is code


def test_eventless_lifecycle_validation_uses_live_transition_rules() -> None:
    current = lifecycle()
    validate_phase_transition(current, LifecyclePhase.IMPLEMENTING)
    with pytest.raises(InvalidLifecycleOperation):
        validate_phase_transition(current, LifecyclePhase.READY)
    with pytest.raises(InvalidLifecycleOperation):
        transition_phase(current, LifecyclePhase.READY, new_id("evt_"), ACTOR, NOW, "no-op")
    blocked = current.model_copy(
        update={
            "blockage": Blockage(
                status=BlockageStatus.BLOCKED,
                reasons=(BlockReason(code="WAITING", summary="waiting"),),
            )
        }
    )
    with pytest.raises(InvalidPhaseTransition):
        validate_phase_transition(blocked, LifecyclePhase.IMPLEMENTING)
    assert current.revision == 4


def test_execute_rechecks_context_enforces_temporal_authority_and_transitions_once() -> None:
    policy = gate(authorization_required=True, policy=HandoverPolicy.HUMAN_APPROVAL)
    current_grant = grant(granted_at=NOW + timedelta(seconds=2))
    current_approval = approval(occurred_at=NOW + timedelta(seconds=3))
    facts = context(authorization_grants=(current_grant,), human_decisions=(current_approval,))
    with pytest.raises(HandoverNotExecutable):
        execute_handover(
            (policy,), GATE_A, facts, new_id("evt_"), ACTOR, NOW + timedelta(seconds=2), "execute"
        )
    with pytest.raises(HandoverNotExecutable):
        execute_handover(
            (policy,), GATE_A, facts, new_id("evt_"), ACTOR, NOW + timedelta(seconds=1), "execute"
        )
    updated, event, evaluation = execute_handover(
        (policy,), GATE_A, facts, new_id("evt_"), ACTOR, NOW + timedelta(seconds=4), "execute"
    )
    assert updated.phase is LifecyclePhase.IMPLEMENTING
    assert updated.revision == 5
    assert event.resulting_revision == 5
    assert evaluation.light is TrafficLight.GREEN
    assert updated.updated_at == NOW + timedelta(seconds=4)


def test_execute_rejects_yellow_red_and_does_not_mutate_lifecycle() -> None:
    current = lifecycle()
    for policy in (gate(authorization_required=True), gate(required_quality_checks=("ruff",))):
        facts = context(lifecycle_value=current)
        with pytest.raises(HandoverNotExecutable):
            execute_handover((policy,), GATE_A, facts, new_id("evt_"), ACTOR, NOW, "execute")
    assert current.phase is LifecyclePhase.READY
    assert current.revision == 4


def test_identical_complete_green_execution_inputs_are_deterministic() -> None:
    policy = gate()
    facts = context()
    event_id = new_id("evt_")
    first = execute_handover((policy,), GATE_A, facts, event_id, ACTOR, NOW, "execute")
    second = execute_handover((policy,), GATE_A, facts, event_id, ACTOR, NOW, "execute")
    assert first == second
