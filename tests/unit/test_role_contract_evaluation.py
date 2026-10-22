"""Deterministic Role Contract conformance and authority-boundary tests."""

import pytest

from relay_engine.agent_runtime import (
    RuntimeCapability,
    RuntimeIdentityCompleteness,
    RuntimeProvenance,
    RuntimeSessionRef,
)
from relay_engine.domain import ActorKind, ActorRef
from relay_engine.role_contracts import (
    ApplicableRoleContractFacts,
    ContractSelection,
    RequirementStatus,
    RoleAction,
    RoleApplicabilityEvaluation,
    RoleClass,
    RoleContract,
    RoleContractApplicability,
    RoleEligibility,
    RoleInputRequirement,
    RoleOutputRequirement,
    RoleRequirementFact,
    RoleSeparationFacts,
    RoleSeparationRequirement,
    SelectionSource,
    SuccessorResolution,
    VerificationAssetPermission,
    WorkDisposition,
    disposition_for_successor,
    evaluate_required_inputs,
    evaluate_required_outputs,
    evaluate_role_action,
    evaluate_role_contract_applicability,
    evaluate_role_contract_identity_conflicts,
    evaluate_role_separation,
    evaluate_runtime_provenance,
    evaluate_verification_asset_permission,
    role_contract_ref,
)

AGENT_A = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.AGENT)
AGENT_B = ActorRef(id="act_018f47c1-7b2c-7abc-1234-123456789009", kind=ActorKind.AGENT)
HUMAN = ActorRef(id="act_018f47c1-7b2c-7abc-1234-123456789010", kind=ActorKind.HUMAN)


def contract(**updates: object) -> RoleContract:
    values: dict[str, object] = {
        "role_key": "implementer",
        "revision": 1,
        "role_class": RoleClass.IMPLEMENTER,
        "allowed_actor_kinds": (ActorKind.AGENT,),
        "allowed_actions": (RoleAction.CONTEXT_READ, RoleAction.EVALUATE_RESULT),
        "prohibited_actions": tuple(
            action
            for action in RoleAction
            if action not in {RoleAction.CONTEXT_READ, RoleAction.EVALUATE_RESULT}
        ),
        "required_inputs": (
            RoleInputRequirement.ACTOR_IDENTITY_BINDING,
            RoleInputRequirement.AUTHORIZED_WORK_BASIS,
        ),
        "required_outputs": (RoleOutputRequirement.ENGINEERING_RESULT,),
        "verification_asset_permissions": (VerificationAssetPermission.READ,),
        "required_runtime_capabilities": (RuntimeCapability.EXECUTE,),
        "required_assurance_properties": (),
    }
    values.update(updates)
    return RoleContract(**values)  # type: ignore[arg-type]


def applicability_facts(**updates: object) -> ApplicableRoleContractFacts:
    values: dict[str, object] = {
        "evaluated_role_contract_ref": role_contract_ref(contract()),
        "selected_role_contract_refs": (role_contract_ref(contract()),),
        "contract_identity_valid": RequirementStatus.SATISFIED,
        "governed_subject_bound": RequirementStatus.SATISFIED,
        "policy_basis_current": RequirementStatus.SATISFIED,
        "governance_profile_current": RequirementStatus.SATISFIED,
        "selection_source": SelectionSource.POLICY,
        "selection": ContractSelection.SELECTS_THIS_CONTRACT,
        "authority_basis_current": RequirementStatus.SATISFIED,
        "supersession_clear": RequirementStatus.SATISFIED,
    }
    values.update(updates)
    return ApplicableRoleContractFacts(**values)  # type: ignore[arg-type]


def applicable_for(value: RoleContract) -> RoleApplicabilityEvaluation:
    reference = role_contract_ref(value)
    return evaluate_role_contract_applicability(
        applicability_facts(
            evaluated_role_contract_ref=reference,
            selected_role_contract_refs=(reference,),
        )
    )


def test_role_action_is_eligibility_not_authority() -> None:
    value = contract()
    applicability = applicable_for(value)
    assert (
        evaluate_role_action(
            value,
            AGENT_A,
            RoleAction.CONTEXT_READ,
            applicability=applicability,
        ).value
        == "PERMITTED_BY_ROLE"
    )
    assert (
        evaluate_role_action(
            value, AGENT_A, RoleAction.AUTHORIZE_WORK, applicability=applicability
        ).value
        == "PROHIBITED_BY_ROLE"
    )
    assert (
        evaluate_role_action(
            value, HUMAN, RoleAction.CONTEXT_READ, applicability=applicability
        ).value
        == "PROHIBITED_BY_ROLE"
    )
    assert (
        evaluate_role_action(value, AGENT_A, "FUTURE_ACTION", applicability=applicability).value
        == "INDETERMINATE"
    )
    assert "AUTHORIZED" not in {
        item.value
        for item in type(
            evaluate_role_action(
                value, AGENT_A, RoleAction.CONTEXT_READ, applicability=applicability
            )
        )
    }


def test_required_inputs_and_outputs_report_satisfied_missing_invalid_and_indeterminate() -> None:
    value = contract()
    all_inputs = (
        RoleRequirementFact(
            requirement=RoleInputRequirement.ACTOR_IDENTITY_BINDING,
            status=RequirementStatus.SATISFIED,
        ),
        RoleRequirementFact(
            requirement=RoleInputRequirement.AUTHORIZED_WORK_BASIS,
            status=RequirementStatus.SATISFIED,
        ),
    )
    assert evaluate_required_inputs(value, all_inputs).status is RequirementStatus.SATISFIED
    missing = evaluate_required_inputs(value, all_inputs[:1])
    assert missing.status is RequirementStatus.INDETERMINATE
    assert missing.indeterminate == (RoleInputRequirement.AUTHORIZED_WORK_BASIS.value,)
    wrong = (
        all_inputs[0],
        RoleRequirementFact(
            requirement=RoleInputRequirement.AUTHORIZED_WORK_BASIS,
            status=RequirementStatus.UNSATISFIED,
        ),
    )
    result = evaluate_required_inputs(value, wrong)
    assert result.status is RequirementStatus.UNSATISFIED
    assert result.unsatisfied == (RoleInputRequirement.AUTHORIZED_WORK_BASIS.value,)
    assert (
        evaluate_required_outputs(
            value,
            (
                RoleRequirementFact(
                    requirement=RoleOutputRequirement.ENGINEERING_RESULT,
                    status=RequirementStatus.SATISFIED,
                ),
            ),
        ).status
        is RequirementStatus.SATISFIED
    )


def test_requirement_evaluator_rejects_duplicates_and_unrequested_facts() -> None:
    value = contract()
    fact = RoleRequirementFact(
        requirement=RoleInputRequirement.ACTOR_IDENTITY_BINDING,
        status=RequirementStatus.SATISFIED,
    )
    with pytest.raises(ValueError, match="duplicates"):
        evaluate_required_inputs(value, (fact, fact))
    with pytest.raises(ValueError, match="unrequested"):
        evaluate_required_outputs(value, (fact,))


def test_digest_or_executor_self_selection_cannot_establish_applicability() -> None:
    assert (
        evaluate_role_contract_applicability(
            applicability_facts(
                selection=ContractSelection.UNKNOWN,
                selection_source=None,
                selected_role_contract_refs=(),
            )
        ).status
        is RoleContractApplicability.INDETERMINATE
    )
    with pytest.raises(ValueError):
        applicability_facts(selection_source="EXECUTOR")
    assert (
        evaluate_role_contract_applicability(
            applicability_facts(selection_source=SelectionSource.HUMAN_AUTHORITY)
        ).status
        is RoleContractApplicability.APPLICABLE
    )


@pytest.mark.parametrize("selection", [ContractSelection.UNKNOWN, ContractSelection.CONFLICTING])
def test_stale_or_conflicting_selection_fails_closed(selection: ContractSelection) -> None:
    assert (
        evaluate_role_contract_applicability(applicability_facts(selection=selection)).status
        is RoleContractApplicability.INDETERMINATE
    )
    assert (
        evaluate_role_contract_applicability(
            applicability_facts(policy_basis_current=RequirementStatus.INDETERMINATE)
        ).status
        is RoleContractApplicability.INDETERMINATE
    )


def test_policy_selecting_another_contract_is_not_applicable() -> None:
    other_ref = role_contract_ref(contract(role_key="evaluator"))
    assert (
        evaluate_role_contract_applicability(
            applicability_facts(
                selection=ContractSelection.SELECTS_ANOTHER_CONTRACT,
                selected_role_contract_refs=(other_ref,),
            )
        ).status
        is RoleContractApplicability.NOT_APPLICABLE
    )
    assert (
        evaluate_role_contract_applicability(
            applicability_facts(contract_identity_valid=RequirementStatus.UNSATISFIED)
        ).status
        is RoleContractApplicability.NOT_APPLICABLE
    )
    assert (
        evaluate_role_contract_applicability(
            applicability_facts(
                selection=ContractSelection.SELECTS_ANOTHER_CONTRACT,
                selected_role_contract_refs=(),
                selection_source=None,
            )
        ).status
        is RoleContractApplicability.INDETERMINATE
    )


def test_applicability_binds_selection_to_one_exact_role_contract_ref() -> None:
    contract_a = contract(role_key="implementer")
    contract_b = contract(role_key="evaluator")
    ref_a = role_contract_ref(contract_a)
    ref_b = role_contract_ref(contract_b)

    applicable_a = evaluate_role_contract_applicability(
        applicability_facts(
            evaluated_role_contract_ref=ref_a,
            selected_role_contract_refs=(ref_a,),
        )
    )
    assert applicable_a.role_contract_ref == ref_a
    assert applicable_a.status is RoleContractApplicability.APPLICABLE
    assert (
        evaluate_role_action(
            contract_b,
            AGENT_A,
            RoleAction.CONTEXT_READ,
            applicability=applicable_a,
        )
        is RoleEligibility.INDETERMINATE
    )

    mismatched = evaluate_role_contract_applicability(
        applicability_facts(
            evaluated_role_contract_ref=ref_b,
            selected_role_contract_refs=(ref_a,),
        )
    )
    assert mismatched.role_contract_ref == ref_b
    assert mismatched.status is RoleContractApplicability.NOT_APPLICABLE
    assert (
        evaluate_role_action(
            contract_b,
            AGENT_A,
            RoleAction.CONTEXT_READ,
            applicability=mismatched,
        )
        is RoleEligibility.INDETERMINATE
    )

    unresolved = evaluate_role_contract_applicability(
        applicability_facts(selected_role_contract_refs=())
    )
    assert unresolved.status is RoleContractApplicability.INDETERMINATE
    conflicting = evaluate_role_contract_applicability(
        applicability_facts(selected_role_contract_refs=(ref_a, ref_b))
    )
    assert conflicting.status is RoleContractApplicability.INDETERMINATE


def test_role_key_revision_digest_conflicts_are_fail_closed() -> None:
    reference = role_contract_ref(contract())
    same = role_contract_ref(contract())
    conflict = reference.model_copy(update={"content_digest": "sha256:" + "0" * 64})
    assert not evaluate_role_contract_identity_conflicts((reference, same)).has_conflict
    result = evaluate_role_contract_identity_conflicts((reference, conflict))
    assert result.has_conflict
    assert result.conflicting_role_key == reference.role_key
    assert result.conflicting_revision == reference.revision
    successor = role_contract_ref(contract(revision=2))
    assert not evaluate_role_contract_identity_conflicts((reference, successor)).has_conflict


def test_required_actor_execution_and_session_separation_is_policy_selected() -> None:
    requirement = RoleSeparationRequirement(
        left_role_class=RoleClass.IMPLEMENTER,
        right_role_class=RoleClass.INDEPENDENT_EVALUATOR,
        distinct_actor=True,
        distinct_execution=True,
        distinct_runtime_session=True,
    )
    same = evaluate_role_separation(
        requirement,
        RoleSeparationFacts(
            left_actor=AGENT_A,
            right_actor=AGENT_A.model_copy(update={"display_name": "Different display label"}),
            left_execution_id="exec_018f47c1-7b2c-7abc-8def-123456789011",
            right_execution_id="exec_018f47c1-7b2c-7abc-8def-123456789011",
            left_runtime_session=RuntimeSessionRef(runtime_id="runtime", session_id="one"),
            right_runtime_session=RuntimeSessionRef(runtime_id="runtime", session_id="one"),
        ),
    )
    assert same.status is RequirementStatus.UNSATISFIED
    assert len(same.reasons) == 3
    distinct = evaluate_role_separation(
        requirement,
        RoleSeparationFacts(
            left_actor=AGENT_A,
            right_actor=AGENT_B,
            left_execution_id="exec_018f47c1-7b2c-7abc-8def-123456789011",
            right_execution_id="exec_018f47c1-7b2c-7abc-1234-123456789012",
            left_runtime_session=RuntimeSessionRef(runtime_id="runtime", session_id="one"),
            right_runtime_session=RuntimeSessionRef(runtime_id="runtime", session_id="two"),
        ),
    )
    assert distinct.status is RequirementStatus.SATISFIED
    assert (
        evaluate_role_separation(requirement, RoleSeparationFacts()).status
        is RequirementStatus.INDETERMINATE
    )
    no_global_separation = RoleSeparationRequirement(
        left_role_class=RoleClass.IMPLEMENTER,
        right_role_class=RoleClass.INDEPENDENT_EVALUATOR,
    )
    assert (
        evaluate_role_separation(no_global_separation, RoleSeparationFacts()).status
        is RequirementStatus.SATISFIED
    )


def test_protected_asset_permissions_do_not_imply_each_other() -> None:
    assert (
        evaluate_verification_asset_permission(
            (VerificationAssetPermission.READ,),
            VerificationAssetPermission.MODIFY,
            classification_known=True,
        )
        is RequirementStatus.UNSATISFIED
    )
    assert (
        evaluate_verification_asset_permission(
            (VerificationAssetPermission.MODIFY,),
            VerificationAssetPermission.APPROVE_MUTATION,
            classification_known=True,
        )
        is RequirementStatus.UNSATISFIED
    )
    assert (
        evaluate_verification_asset_permission(
            (VerificationAssetPermission.EVALUATE,),
            VerificationAssetPermission.MODIFY,
            classification_known=True,
        )
        is RequirementStatus.UNSATISFIED
    )
    assert (
        evaluate_verification_asset_permission(
            (), VerificationAssetPermission.MODIFY, classification_known=False
        )
        is RequirementStatus.INDETERMINATE
    )


@pytest.mark.parametrize(
    "permission",
    [VerificationAssetPermission.MODIFY, VerificationAssetPermission.APPROVE_MUTATION],
)
def test_mutation_and_approval_require_external_authority_status(
    permission: VerificationAssetPermission,
) -> None:
    granted = (permission,)
    assert (
        evaluate_verification_asset_permission(granted, permission, classification_known=True)
        is RequirementStatus.INDETERMINATE
    )
    assert (
        evaluate_verification_asset_permission(
            granted,
            permission,
            classification_known=True,
            separate_authority_status=RequirementStatus.UNSATISFIED,
        )
        is RequirementStatus.UNSATISFIED
    )
    assert (
        evaluate_verification_asset_permission(
            granted,
            permission,
            classification_known=True,
            separate_authority_status=RequirementStatus.INDETERMINATE,
        )
        is RequirementStatus.INDETERMINATE
    )
    assert (
        evaluate_verification_asset_permission(
            granted,
            permission,
            classification_known=True,
            separate_authority_status=RequirementStatus.SATISFIED,
        )
        is RequirementStatus.SATISFIED
    )


def test_non_mutating_asset_permission_needs_no_separate_authority_fact() -> None:
    assert (
        evaluate_verification_asset_permission(
            (VerificationAssetPermission.READ,),
            VerificationAssetPermission.READ,
            classification_known=True,
        )
        is RequirementStatus.SATISFIED
    )


def test_runtime_capability_and_actual_identity_are_separate_from_requested_identity() -> None:
    missing = evaluate_runtime_provenance(
        (RuntimeCapability.EXECUTE,), (), None, require_actual_identity=False
    )
    assert missing.status is RequirementStatus.UNSATISFIED
    provenance = RuntimeProvenance(
        runtime_id="runtime",
        adapter_version="1",
        runtime_version=None,
        api_generation="v1",
        requested_provider_id="requested-provider",
        requested_model_id="requested-model",
        actual_provider_id="actual-provider",
        actual_model_id="actual-model",
        identity_completeness=RuntimeIdentityCompleteness.FULL,
    )
    checked = evaluate_runtime_provenance(
        (RuntimeCapability.EXECUTE,),
        (RuntimeCapability.EXECUTE,),
        provenance,
        require_actual_identity=True,
    )
    assert checked.status is RequirementStatus.SATISFIED
    assert provenance.requested_model_id != provenance.actual_model_id
    absent = evaluate_runtime_provenance((), (), None, require_actual_identity=True)
    assert absent.status is RequirementStatus.INDETERMINATE


@pytest.mark.parametrize(
    ("resolution", "expected"),
    [
        (
            SuccessorResolution.AUTHORIZED_SUCCESSOR_ESTABLISHED,
            WorkDisposition.AUTHORIZED_SUCCESSOR_AVAILABLE,
        ),
        (SuccessorResolution.NO_AUTHORIZED_SUCCESSOR, WorkDisposition.BACKLOG_EXHAUSTED),
        (SuccessorResolution.SUCCESSOR_NOT_DETERMINABLE, WorkDisposition.ESCALATION_REQUIRED),
    ],
)
def test_successor_resolution_maps_to_bounded_work_disposition(
    resolution: SuccessorResolution, expected: WorkDisposition
) -> None:
    assert disposition_for_successor(resolution) is expected
