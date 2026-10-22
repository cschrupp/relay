"""Pure deterministic Role Contract identity and conformance evaluations."""

import hashlib
import json
from collections.abc import Sequence

from relay_engine.agent_runtime import RuntimeCapability, RuntimeProvenance
from relay_engine.domain import ActorRef, ContentDigest
from relay_engine.role_contracts.models import (
    ApplicableRoleContractFacts,
    ContractSelection,
    RequirementStatus,
    RoleAction,
    RoleApplicabilityEvaluation,
    RoleContract,
    RoleContractApplicability,
    RoleContractIdentityConflict,
    RoleContractRef,
    RoleEligibility,
    RoleInputRequirement,
    RoleOutputRequirement,
    RoleReason,
    RoleRequirementEvaluation,
    RoleRequirementFact,
    RoleSeparationEvaluation,
    RoleSeparationFacts,
    RoleSeparationRequirement,
    RuntimeProvenanceEvaluation,
    SuccessorResolution,
    VerificationAssetPermission,
    WorkDisposition,
)


def canonical_role_contract_json(contract: RoleContract) -> str:
    """Serialize a contract as compact, sorted, Unicode-preserving canonical JSON."""

    return json.dumps(
        contract.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest_role_contract(contract: RoleContract) -> ContentDigest:
    """Return the SHA-256 identity of the canonical schema-v1 contract bytes."""

    digest = hashlib.sha256(canonical_role_contract_json(contract).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def role_contract_ref(contract: RoleContract) -> RoleContractRef:
    """Derive the exact ref for a contract's key, revision, and content."""

    return RoleContractRef(
        role_key=contract.role_key,
        revision=contract.revision,
        content_digest=digest_role_contract(contract),
    )


def role_contract_ref_matches(contract: RoleContract, reference: RoleContractRef) -> bool:
    """Check exact identity without inferring applicability or authority."""

    return role_contract_ref(contract) == reference


def evaluate_role_contract_identity_conflicts(
    references: Sequence[RoleContractRef],
) -> RoleContractIdentityConflict:
    """Detect same-key/revision digest conflicts in one caller-supplied policy group."""

    digests: dict[tuple[str, int], str] = {}
    for reference in references:
        key = (reference.role_key, reference.revision)
        previous_digest = digests.get(key)
        if previous_digest is not None and previous_digest != reference.content_digest:
            return RoleContractIdentityConflict(
                has_conflict=True,
                conflicting_role_key=reference.role_key,
                conflicting_revision=reference.revision,
            )
        digests[key] = reference.content_digest
    return RoleContractIdentityConflict(has_conflict=False)


def evaluate_role_action(
    contract: RoleContract,
    actor: ActorRef,
    action: RoleAction | str,
    *,
    applicability: RoleApplicabilityEvaluation,
) -> RoleEligibility:
    """Evaluate action eligibility only after exact-ref applicability is established."""

    if (
        applicability.role_contract_ref != role_contract_ref(contract)
        or applicability.status is not RoleContractApplicability.APPLICABLE
    ):
        return RoleEligibility.INDETERMINATE
    if actor.kind not in contract.allowed_actor_kinds:
        return RoleEligibility.PROHIBITED_BY_ROLE
    if not isinstance(action, RoleAction):
        return RoleEligibility.INDETERMINATE
    if action in contract.prohibited_actions:
        return RoleEligibility.PROHIBITED_BY_ROLE
    if action in contract.allowed_actions:
        return RoleEligibility.PERMITTED_BY_ROLE
    return RoleEligibility.INDETERMINATE


def evaluate_role_requirements(
    required: Sequence[RoleInputRequirement | RoleOutputRequirement],
    facts: Sequence[RoleRequirementFact],
) -> RoleRequirementEvaluation:
    """Evaluate exact externally established facts for required role inputs or outputs."""

    required_values = tuple(item.value for item in required)
    if len(required_values) != len(set(required_values)):
        raise ValueError("required role requirements must be unique")
    fact_map: dict[str, RequirementStatus] = {}
    for fact in facts:
        key = fact.requirement.value
        if key in fact_map:
            raise ValueError("requirement facts must not contain duplicates")
        fact_map[key] = fact.status
    required_set = set(required_values)
    if set(fact_map) - required_set:
        raise ValueError("requirement facts must not contain unrequested requirements")

    unsatisfied: list[str] = []
    indeterminate: list[str] = []
    for requirement in required_values:
        status = fact_map.get(requirement, RequirementStatus.INDETERMINATE)
        if status is RequirementStatus.UNSATISFIED:
            unsatisfied.append(requirement)
        elif status is RequirementStatus.INDETERMINATE:
            indeterminate.append(requirement)

    if unsatisfied:
        overall = RequirementStatus.UNSATISFIED
    elif indeterminate:
        overall = RequirementStatus.INDETERMINATE
    else:
        overall = RequirementStatus.SATISFIED
    return RoleRequirementEvaluation(
        status=overall,
        unsatisfied=tuple(unsatisfied),
        indeterminate=tuple(indeterminate),
    )


def evaluate_required_inputs(
    contract: RoleContract, facts: Sequence[RoleRequirementFact]
) -> RoleRequirementEvaluation:
    """Evaluate all minimum semantic input obligations in a role contract."""

    return evaluate_role_requirements(contract.required_inputs, facts)


def evaluate_required_outputs(
    contract: RoleContract, facts: Sequence[RoleRequirementFact]
) -> RoleRequirementEvaluation:
    """Evaluate all minimum semantic output obligations in a role contract."""

    return evaluate_role_requirements(contract.required_outputs, facts)


def evaluate_role_contract_applicability(
    facts: ApplicableRoleContractFacts,
) -> RoleApplicabilityEvaluation:
    """Evaluate and bind prospective applicability to one exact RoleContractRef."""

    result = RoleContractApplicability.INDETERMINATE
    reason: RoleReason | None = RoleReason.ROLE_CONTRACT_APPLICABILITY_UNKNOWN

    established = (
        facts.contract_identity_valid,
        facts.governed_subject_bound,
        facts.policy_basis_current,
        facts.governance_profile_current,
        facts.authority_basis_current,
        facts.supersession_clear,
    )
    if any(status is RequirementStatus.INDETERMINATE for status in established):
        pass
    elif any(status is RequirementStatus.UNSATISFIED for status in established):
        result = RoleContractApplicability.NOT_APPLICABLE
        reason = RoleReason.ROLE_CONTRACT_NOT_APPLICABLE
    elif (
        facts.selection_source is None
        or facts.selection
        in {
            ContractSelection.UNKNOWN,
            ContractSelection.CONFLICTING,
        }
        or len(facts.selected_role_contract_refs) != 1
    ):
        pass
    elif facts.selected_role_contract_refs[0] != facts.evaluated_role_contract_ref:
        result = RoleContractApplicability.NOT_APPLICABLE
        reason = RoleReason.ROLE_CONTRACT_NOT_APPLICABLE
    elif facts.selection is ContractSelection.SELECTS_ANOTHER_CONTRACT:
        # The label conflicts with the exact matching ref, so the external facts disagree.
        pass
    else:
        result = RoleContractApplicability.APPLICABLE
        reason = None
    return RoleApplicabilityEvaluation(
        role_contract_ref=facts.evaluated_role_contract_ref,
        status=result,
        reason=reason,
    )


def evaluate_role_separation(
    requirement: RoleSeparationRequirement,
    facts: RoleSeparationFacts,
) -> RoleSeparationEvaluation:
    """Compare exact actor/execution/session facts for policy-required separation."""

    missing: list[str] = []
    violations: list[str] = []
    if requirement.distinct_actor:
        if facts.left_actor is None or facts.right_actor is None:
            missing.append("actor")
        elif facts.left_actor.id == facts.right_actor.id:
            violations.append("actor")
    if requirement.distinct_execution:
        if facts.left_execution_id is None or facts.right_execution_id is None:
            missing.append("execution")
        elif facts.left_execution_id == facts.right_execution_id:
            violations.append("execution")
    if requirement.distinct_runtime_session:
        if facts.left_runtime_session is None or facts.right_runtime_session is None:
            missing.append("runtime_session")
        elif facts.left_runtime_session == facts.right_runtime_session:
            violations.append("runtime_session")
    if violations:
        return RoleSeparationEvaluation(
            status=RequirementStatus.UNSATISFIED,
            reasons=tuple(f"ROLE_SEPARATION_VIOLATION:{item}" for item in violations),
        )
    if missing:
        return RoleSeparationEvaluation(
            status=RequirementStatus.INDETERMINATE,
            reasons=tuple(f"MISSING_COMPARISON_FACT:{item}" for item in missing),
        )
    return RoleSeparationEvaluation(status=RequirementStatus.SATISFIED)


def evaluate_verification_asset_permission(
    granted: Sequence[VerificationAssetPermission],
    required: VerificationAssetPermission,
    *,
    classification_known: bool,
    separate_authority_status: RequirementStatus | None = None,
) -> RequirementStatus:
    """Check role permission plus external authority for protected mutation operations."""

    if not classification_known:
        return RequirementStatus.INDETERMINATE
    if required not in granted:
        return RequirementStatus.UNSATISFIED
    if required in {
        VerificationAssetPermission.MODIFY,
        VerificationAssetPermission.APPROVE_MUTATION,
    }:
        if separate_authority_status is None:
            return RequirementStatus.INDETERMINATE
        return separate_authority_status
    return RequirementStatus.SATISFIED


def evaluate_runtime_provenance(
    required_capabilities: Sequence[RuntimeCapability],
    available_capabilities: Sequence[RuntimeCapability],
    provenance: RuntimeProvenance | None,
    *,
    require_actual_identity: bool,
) -> RuntimeProvenanceEvaluation:
    """Check required runtime capability and actual identity evidence, if required."""

    missing = tuple(item for item in required_capabilities if item not in available_capabilities)
    if missing:
        return RuntimeProvenanceEvaluation(
            status=RequirementStatus.UNSATISFIED,
            missing_capabilities=missing,
            reason=RoleReason.EXECUTION_PROVENANCE_INSUFFICIENT,
        )
    if require_actual_identity and (
        provenance is None
        or provenance.actual_provider_id is None
        or provenance.actual_model_id is None
    ):
        return RuntimeProvenanceEvaluation(
            status=RequirementStatus.INDETERMINATE,
            reason=RoleReason.EXECUTION_PROVENANCE_INSUFFICIENT,
        )
    return RuntimeProvenanceEvaluation(status=RequirementStatus.SATISFIED)


def disposition_for_successor(resolution: SuccessorResolution) -> WorkDisposition:
    """Map exact successor resolution to a bounded current-work disposition."""

    return {
        SuccessorResolution.AUTHORIZED_SUCCESSOR_ESTABLISHED: (
            WorkDisposition.AUTHORIZED_SUCCESSOR_AVAILABLE
        ),
        SuccessorResolution.NO_AUTHORIZED_SUCCESSOR: WorkDisposition.BACKLOG_EXHAUSTED,
        SuccessorResolution.SUCCESSOR_NOT_DETERMINABLE: WorkDisposition.ESCALATION_REQUIRED,
    }[resolution]
