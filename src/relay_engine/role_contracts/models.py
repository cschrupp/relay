"""Immutable domain values for provider-neutral Relay Role Contracts."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator, model_validator

from relay_engine.agent_runtime import RuntimeCapability, RuntimeSessionRef
from relay_engine.domain import ActorKind, ActorRef, ContentDigest, ExecutionId
from relay_engine.domain._base import DomainModel

type RoleKey = Annotated[
    str,
    StringConstraints(
        strict=True, min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"
    ),
]
type AssurancePropertyKey = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=128, pattern=r"^[A-Z][A-Z0-9_]*$"),
]


class RoleClass(StrEnum):
    IMPLEMENTER = "IMPLEMENTER"
    INDEPENDENT_EVALUATOR = "INDEPENDENT_EVALUATOR"
    HUMAN_AUTHORITY = "HUMAN_AUTHORITY"
    PROMOTION_EXECUTOR = "PROMOTION_EXECUTOR"


class RoleAction(StrEnum):
    CONTEXT_READ = "CONTEXT_READ"
    IMPLEMENTATION_MUTATE = "IMPLEMENTATION_MUTATE"
    IMPLEMENTATION_TEST_MUTATE = "IMPLEMENTATION_TEST_MUTATE"
    VERIFICATION_EXECUTE = "VERIFICATION_EXECUTE"
    EVALUATE_RESULT = "EVALUATE_RESULT"
    AUTHORIZE_WORK = "AUTHORIZE_WORK"
    ACCEPT_RESULT = "ACCEPT_RESULT"
    PROMOTE_RESULT = "PROMOTE_RESULT"
    DECOMPOSE_AUTHORIZED_WORK = "DECOMPOSE_AUTHORIZED_WORK"
    PROPOSE_FUTURE_WORK = "PROPOSE_FUTURE_WORK"


class VerificationAssetPermission(StrEnum):
    READ = "READ"
    CREATE = "CREATE"
    PROPOSE_MUTATION = "PROPOSE_MUTATION"
    MODIFY = "MODIFY"
    APPROVE_MUTATION = "APPROVE_MUTATION"
    EXECUTE = "EXECUTE"
    EVALUATE = "EVALUATE"


class RoleInputRequirement(StrEnum):
    ACTOR_IDENTITY_BINDING = "ACTOR_IDENTITY_BINDING"
    APPLICABLE_ROLE_CONTRACT_BINDING = "APPLICABLE_ROLE_CONTRACT_BINDING"
    GOVERNANCE_PROFILE_BINDING = "GOVERNANCE_PROFILE_BINDING"
    AUTHORIZED_WORK_BASIS = "AUTHORIZED_WORK_BASIS"
    SOURCE_BASELINE = "SOURCE_BASELINE"
    ACCEPTED_DESIGN_BASIS = "ACCEPTED_DESIGN_BASIS"
    EVALUATION_SUBJECT = "EVALUATION_SUBJECT"
    EVIDENCE_BASIS = "EVIDENCE_BASIS"
    DECISION_BASIS = "DECISION_BASIS"
    PROMOTION_BASIS = "PROMOTION_BASIS"
    RUNTIME_EXECUTION_BASIS = "RUNTIME_EXECUTION_BASIS"


class RoleOutputRequirement(StrEnum):
    ENGINEERING_RESULT = "ENGINEERING_RESULT"
    EXECUTION_EVIDENCE = "EXECUTION_EVIDENCE"
    EVALUATION_JUDGMENT = "EVALUATION_JUDGMENT"
    HUMAN_DECISION = "HUMAN_DECISION"
    PROMOTION_EVIDENCE = "PROMOTION_EVIDENCE"
    WORK_DISPOSITION = "WORK_DISPOSITION"


class RoleEligibility(StrEnum):
    PERMITTED_BY_ROLE = "PERMITTED_BY_ROLE"
    PROHIBITED_BY_ROLE = "PROHIBITED_BY_ROLE"
    INDETERMINATE = "INDETERMINATE"


class RequirementStatus(StrEnum):
    SATISFIED = "SATISFIED"
    UNSATISFIED = "UNSATISFIED"
    INDETERMINATE = "INDETERMINATE"


class RoleContractApplicability(StrEnum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INDETERMINATE = "INDETERMINATE"


class SuccessorResolution(StrEnum):
    AUTHORIZED_SUCCESSOR_ESTABLISHED = "AUTHORIZED_SUCCESSOR_ESTABLISHED"
    NO_AUTHORIZED_SUCCESSOR = "NO_AUTHORIZED_SUCCESSOR"
    SUCCESSOR_NOT_DETERMINABLE = "SUCCESSOR_NOT_DETERMINABLE"


class WorkDisposition(StrEnum):
    AUTHORIZED_SUCCESSOR_AVAILABLE = "AUTHORIZED_SUCCESSOR_AVAILABLE"
    BACKLOG_EXHAUSTED = "BACKLOG_EXHAUSTED"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"


class SelectionSource(StrEnum):
    """Accepted external source classes; executor/runtime/model are excluded."""

    POLICY = "POLICY"
    HUMAN_AUTHORITY = "HUMAN_AUTHORITY"


class ContractSelection(StrEnum):
    SELECTS_THIS_CONTRACT = "SELECTS_THIS_CONTRACT"
    SELECTS_ANOTHER_CONTRACT = "SELECTS_ANOTHER_CONTRACT"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"


class RoleReason(StrEnum):
    ROLE_ACTION_PROHIBITED = "ROLE_ACTION_PROHIBITED"
    ROLE_ACTION_UNSPECIFIED = "ROLE_ACTION_UNSPECIFIED"
    ROLE_ACTION_UNKNOWN_TO_CONTRACT_SCHEMA = "ROLE_ACTION_UNKNOWN_TO_CONTRACT_SCHEMA"
    ACTOR_KIND_NOT_ALLOWED = "ACTOR_KIND_NOT_ALLOWED"
    ACTOR_IDENTITY_NOT_BOUND = "ACTOR_IDENTITY_NOT_BOUND"
    ROLE_SEPARATION_VIOLATION = "ROLE_SEPARATION_VIOLATION"
    ROLE_CONTRACT_NOT_APPLICABLE = "ROLE_CONTRACT_NOT_APPLICABLE"
    ROLE_CONTRACT_APPLICABILITY_UNKNOWN = "ROLE_CONTRACT_APPLICABILITY_UNKNOWN"
    ROLE_CONTRACT_IDENTITY_CONFLICT = "ROLE_CONTRACT_IDENTITY_CONFLICT"
    GOVERNANCE_PROFILE_REQUIRED = "GOVERNANCE_PROFILE_REQUIRED"
    GOVERNANCE_PROFILE_CONFLICT = "GOVERNANCE_PROFILE_CONFLICT"
    PROTECTED_ASSET_PERMISSION_REQUIRED = "PROTECTED_ASSET_PERMISSION_REQUIRED"
    PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED = "PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED"
    REQUIRED_ASSURANCE_EVIDENCE_MISSING = "REQUIRED_ASSURANCE_EVIDENCE_MISSING"
    EXECUTION_PROVENANCE_INSUFFICIENT = "EXECUTION_PROVENANCE_INSUFFICIENT"
    REQUIRED_ROLE_INPUT_MISSING = "REQUIRED_ROLE_INPUT_MISSING"
    REQUIRED_ROLE_INPUT_INVALID = "REQUIRED_ROLE_INPUT_INVALID"
    REQUIRED_ROLE_INPUT_INDETERMINATE = "REQUIRED_ROLE_INPUT_INDETERMINATE"
    REQUIRED_ROLE_OUTPUT_MISSING = "REQUIRED_ROLE_OUTPUT_MISSING"
    REQUIRED_ROLE_OUTPUT_INVALID = "REQUIRED_ROLE_OUTPUT_INVALID"
    REQUIRED_ROLE_OUTPUT_INDETERMINATE = "REQUIRED_ROLE_OUTPUT_INDETERMINATE"
    WORK_AUTHORITY_MISSING = "WORK_AUTHORITY_MISSING"
    WORK_AUTHORITY_STALE = "WORK_AUTHORITY_STALE"
    WORK_AUTHORITY_CONFLICT = "WORK_AUTHORITY_CONFLICT"
    WORK_SCOPE_EXCEEDED = "WORK_SCOPE_EXCEEDED"
    SUCCESSOR_NOT_DETERMINABLE = "SUCCESSOR_NOT_DETERMINABLE"


class RoleContract(DomainModel):
    """Immutable, digest-bound semantic policy for one stable role revision."""

    schema_version: Literal[1] = 1
    role_key: RoleKey
    revision: int = Field(ge=1)
    role_class: RoleClass
    allowed_actor_kinds: tuple[ActorKind, ...]
    allowed_actions: tuple[RoleAction, ...]
    prohibited_actions: tuple[RoleAction, ...]
    required_inputs: tuple[RoleInputRequirement, ...]
    required_outputs: tuple[RoleOutputRequirement, ...]
    verification_asset_permissions: tuple[VerificationAssetPermission, ...]
    required_runtime_capabilities: tuple[RuntimeCapability, ...]
    required_assurance_properties: tuple[AssurancePropertyKey, ...]

    @field_validator(
        "allowed_actor_kinds",
        "allowed_actions",
        "prohibited_actions",
        "required_inputs",
        "required_outputs",
        "verification_asset_permissions",
        "required_runtime_capabilities",
    )
    @classmethod
    def enum_tuple_is_unique_and_canonical(cls, value: tuple[StrEnum, ...]) -> tuple[StrEnum, ...]:
        if len(value) != len(set(value)):
            raise ValueError("tuple values must be unique")
        if value != tuple(sorted(value, key=lambda item: list(type(item)).index(item))):
            raise ValueError("tuple values must use enum declaration order")
        return value

    @field_validator("required_assurance_properties")
    @classmethod
    def assurance_properties_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("assurance properties must be unique")
        if value != tuple(sorted(value)):
            raise ValueError("assurance properties must be in lexical order")
        return value

    @model_validator(mode="after")
    def role_contract_is_complete_and_consistent(self) -> RoleContract:
        if not self.allowed_actor_kinds:
            raise ValueError("allowed_actor_kinds must not be empty")
        if set(self.allowed_actions) & set(self.prohibited_actions):
            raise ValueError("allowed and prohibited actions must be disjoint")
        if set(self.allowed_actions) | set(self.prohibited_actions) != set(RoleAction):
            raise ValueError("schema-v1 contracts must classify every RoleAction")
        if self.role_class is RoleClass.HUMAN_AUTHORITY and self.allowed_actor_kinds != (
            ActorKind.HUMAN,
        ):
            raise ValueError("HUMAN_AUTHORITY contracts may allow only HUMAN actors")
        return self


class RoleContractRef(DomainModel):
    """Exact role-key, revision, and canonical content-digest identity."""

    role_key: RoleKey
    revision: int = Field(ge=1)
    content_digest: ContentDigest


class RoleActionBinding(DomainModel):
    """Evidence binding a role contract, actor, action, and optional execution."""

    role_contract_ref: RoleContractRef
    actor: ActorRef
    action: RoleAction
    execution_id: ExecutionId | None = None


class RoleRequirementFact(DomainModel):
    """Externally established status for one semantic input or output obligation."""

    requirement: RoleInputRequirement | RoleOutputRequirement
    status: RequirementStatus


class RoleRequirementEvaluation(DomainModel):
    """Deterministic aggregate for required input/output conformance."""

    status: RequirementStatus
    unsatisfied: tuple[str, ...] = ()
    indeterminate: tuple[str, ...] = ()


class ApplicableRoleContractFacts(DomainModel):
    """Consume already-established facts; Human root authority is independent of RoleContract."""

    evaluated_role_contract_ref: RoleContractRef
    selected_role_contract_refs: tuple[RoleContractRef, ...]
    contract_identity_valid: RequirementStatus
    governed_subject_bound: RequirementStatus
    policy_basis_current: RequirementStatus
    governance_profile_current: RequirementStatus
    selection_source: SelectionSource | None
    selection: ContractSelection
    authority_basis_current: RequirementStatus
    supersession_clear: RequirementStatus

    @field_validator("selected_role_contract_refs")
    @classmethod
    def selected_references_are_unique(
        cls, value: tuple[RoleContractRef, ...]
    ) -> tuple[RoleContractRef, ...]:
        if len(value) != len(set(value)):
            raise ValueError("selected RoleContractRefs must be unique")
        return value


class RoleContractIdentityConflict(DomainModel):
    """Conflict result for refs already grouped by one exact PolicyBasis."""

    has_conflict: bool
    conflicting_role_key: RoleKey | None = None
    conflicting_revision: int | None = None


class RoleSeparationRequirement(DomainModel):
    """Policy-selected distinctions between two roles/actor executions."""

    left_role_class: RoleClass
    right_role_class: RoleClass
    distinct_actor: bool = False
    distinct_execution: bool = False
    distinct_runtime_session: bool = False


class RoleSeparationFacts(DomainModel):
    """Exact comparison facts supplied by the orchestration/evaluation layer."""

    left_actor: ActorRef | None = None
    right_actor: ActorRef | None = None
    left_execution_id: ExecutionId | None = None
    right_execution_id: ExecutionId | None = None
    left_runtime_session: RuntimeSessionRef | None = None
    right_runtime_session: RuntimeSessionRef | None = None


class RoleSeparationEvaluation(DomainModel):
    status: RequirementStatus
    reasons: tuple[str, ...] = ()


class RoleApplicabilityEvaluation(DomainModel):
    role_contract_ref: RoleContractRef
    status: RoleContractApplicability
    reason: RoleReason | None = None


class RuntimeProvenanceEvaluation(DomainModel):
    status: RequirementStatus
    missing_capabilities: tuple[RuntimeCapability, ...] = ()
    reason: RoleReason | None = None
