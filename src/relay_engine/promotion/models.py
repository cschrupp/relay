"""Immutable exact-subject models for canonical promotion governance."""

import hashlib
import json
import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal, cast

from pydantic import Field, field_validator, model_validator

from relay_engine.domain import (
    ActorRef,
    CommitRef,
    ContentDigest,
    ProjectId,
    RepositoryRef,
)
from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import (
    BaselineId,
    CanonicalPromotionBindingId,
    CanonicalPromotionPolicyId,
    CanonicalPromotionReconciliationId,
    ExecutionId,
    HumanDecisionId,
    ManualEvaluationId,
    RepositoryMutationAuthorizationId,
    RepositoryPromotionId,
    SliceId,
    SliceResultId,
)

_SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


def _json_arrays_to_tuples(value: object) -> object:
    """Restore immutable tuple contracts when strict models load JSON arrays."""

    if isinstance(value, list):
        return tuple(_json_arrays_to_tuples(item) for item in cast(list[object], value))
    if isinstance(value, dict):
        mapping = cast(dict[str, object], value)
        converted: dict[str, object] = {
            key: _json_arrays_to_tuples(item) for key, item in mapping.items()
        }
        # A before-validator switches Pydantic into Python-mode validation, where
        # strict datetime fields no longer accept the ISO strings from JSON.
        for key in ("bound_at", "accepted_at", "created_at", "observed_at", "reconciled_at"):
            timestamp = converted.get(key)
            if isinstance(timestamp, str):
                converted[key] = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return converted
    return value


class PromotionModel(DomainModel):
    @model_validator(mode="before")
    @classmethod
    def restore_tuple_fields(cls, value: object) -> object:
        return _json_arrays_to_tuples(value)


class PromotionPropertyOutcome(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class PromotionAuthorizability(StrEnum):
    AUTHORIZABLE = "AUTHORIZABLE"
    INELIGIBLE = "INELIGIBLE"
    UNKNOWN = "UNKNOWN"


class PromotionEligibilityState(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    UNKNOWN = "UNKNOWN"


class CanonicalRefHealth(StrEnum):
    HEALTHY = "HEALTHY"
    QUARANTINED = "QUARANTINED"
    UNKNOWN = "UNKNOWN"


class CanonicalPromotionPolicyBindingState(StrEnum):
    UNMANAGED = "UNMANAGED"
    MANAGED = "MANAGED"


class CanonicalPromotionPolicyBindingResolution(StrEnum):
    UNMANAGED = "UNMANAGED"
    MANAGED = "MANAGED"
    UNKNOWN_OR_INVALID = "UNKNOWN_OR_INVALID"


class PromotionResultOutcome(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    NOT_APPLIED = "NOT_APPLIED"
    CONFLICT = "CONFLICT"
    VISIBLE_UNVERIFIED = "VISIBLE_UNVERIFIED"


class ReconciliationPreparationState(StrEnum):
    RECONCILABLE = "RECONCILABLE"
    INELIGIBLE = "INELIGIBLE"
    UNKNOWN = "UNKNOWN"


class ReconciliationOutcome(StrEnum):
    RECONCILED = "RECONCILED"


class GitHubRequiredCheckV1(PromotionModel):
    """Exact check-run identity required by a promotion policy."""

    name: str
    expected_app_id: int = Field(gt=0)

    @field_validator("name")
    @classmethod
    def name_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class PromotionPropertyRequirementV1(PromotionModel):
    """One bounded Slice 1.10 property and its policy applicability."""

    property_name: str
    required: bool = True

    @field_validator("property_name")
    @classmethod
    def property_name_is_supported(cls, value: str) -> str:
        allowed = {
            "RELAY_EVIDENCE_SUBJECT_EXACT",
            "RELAY_INDEPENDENT_EVALUATION",
            "RELAY_HUMAN_ACCEPTED",
            "RELAY_PROMOTION_AUTHORIZED",
            "RELAY_CANONICAL_PARENT_CURRENT",
            "RELAY_REQUIRED_CHECKS_CURRENT",
            "RELAY_SOURCE_CONTROL_ENFORCED",
            "RELAY_FAIL_CLOSED",
            "RELAY_EXACT_AUTHORIZED_BASELINE",
            "RELAY_GOVERNANCE_PROFILE_BOUND",
            "RELAY_VERIFICATION_ASSETS_PROTECTED",
            "RELAY_CONTROL_CONTINUITY_VERIFIED",
        }
        if value not in allowed:
            raise ValueError("unsupported Slice 1.10 promotion property")
        return value


class CanonicalPromotionPolicyV1(PromotionModel):
    """Immutable canonical-ref enforcement policy."""

    policy_id: CanonicalPromotionPolicyId
    schema_version: Literal[1] = 1
    canonical_branch: str
    promotion_app_id: int = Field(gt=0)
    control_verifier_app_id: int = Field(gt=0)
    integrity_ruleset_id: int = Field(gt=0)
    writer_ruleset_id: int = Field(gt=0)
    allowed_additional_ruleset_ids: tuple[int, ...] = ()
    required_checks: tuple[GitHubRequiredCheckV1, ...]
    require_source_control_enforcement: Literal[True] = True
    require_exact_parent: Literal[True] = True
    allow_force: Literal[False] = False
    allow_delete: Literal[False] = False
    allowed_update_actor_app_id: int = Field(gt=0)
    human_acceptance_must_bind_target: bool
    independent_evaluation_must_bind_target: bool
    promotion_property_requirements: tuple[PromotionPropertyRequirementV1, ...]

    @field_validator("canonical_branch")
    @classmethod
    def branch_is_valid(cls, value: str) -> str:
        value = require_nonblank(value)
        if (
            value.startswith("/")
            or value.endswith("/")
            or "//" in value
            or ".." in value
            or "@{" in value
            or any(character.isspace() or ord(character) < 32 for character in value)
            or any(character in value for character in "~^:?*[\\")
            or any(part.startswith(".") or part.endswith(".lock") for part in value.split("/"))
        ):
            raise ValueError("canonical branch is not a safe Git ref name")
        return value

    @field_validator("required_checks")
    @classmethod
    def required_checks_are_canonical(
        cls, value: tuple[GitHubRequiredCheckV1, ...]
    ) -> tuple[GitHubRequiredCheckV1, ...]:
        keys = tuple((item.name, item.expected_app_id) for item in value)
        if keys != tuple(sorted(set(keys))) or not value:
            raise ValueError("required checks must be non-empty, unique, and canonically ordered")
        return value

    @field_validator("promotion_property_requirements")
    @classmethod
    def properties_are_canonical(
        cls, value: tuple[PromotionPropertyRequirementV1, ...]
    ) -> tuple[PromotionPropertyRequirementV1, ...]:
        names = tuple(item.property_name for item in value)
        if names != tuple(sorted(set(names))):
            raise ValueError("promotion property requirements must be unique and ordered")
        return value

    @field_validator("allowed_additional_ruleset_ids")
    @classmethod
    def additional_rulesets_are_canonical(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if value:
            raise ValueError("Slice 1.10 v1 does not accept additional ruleset IDs")
        return value

    @model_validator(mode="after")
    def ruleset_ids_are_distinct(self) -> CanonicalPromotionPolicyV1:
        ids = (
            self.integrity_ruleset_id,
            self.writer_ruleset_id,
            *self.allowed_additional_ruleset_ids,
        )
        if len(ids) != len(set(ids)):
            raise ValueError("ruleset IDs must be unique")
        if self.allowed_update_actor_app_id != self.promotion_app_id:
            raise ValueError("allowed writer identity must equal the exact Promotion App ID")
        if self.control_verifier_app_id == self.promotion_app_id:
            raise ValueError("Control Verifier and Promotion App identities must be distinct")
        return self


class CanonicalPromotionSubjectV1(PromotionModel):
    """Exact repository, binding, governance, parent, and target mutation subject."""

    subject_type: Literal["CanonicalPromotionSubjectV1"] = "CanonicalPromotionSubjectV1"
    schema_version: Literal[1] = 1
    project_id: ProjectId
    repository: RepositoryRef
    installation_id: int = Field(gt=0)
    github_repository_id: int = Field(gt=0)
    github_node_id: str
    expected_state_revision: int = Field(ge=1)
    canonical_ref: str
    expected_parent: CommitRef
    target_commit: CommitRef
    binding_id: CanonicalPromotionBindingId
    binding_revision: int = Field(ge=1)
    binding_digest: ContentDigest
    promotion_policy_digest: ContentDigest
    governance_basis_digest: ContentDigest
    required_check_specs: tuple[GitHubRequiredCheckV1, ...]

    @field_validator("github_node_id")
    @classmethod
    def node_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("canonical_ref")
    @classmethod
    def canonical_ref_is_safe(cls, value: str) -> str:
        if not value.startswith("refs/heads/"):
            raise ValueError("canonical_ref must be a complete heads ref")
        branch = value.removeprefix("refs/heads/")
        CanonicalPromotionPolicyV1(
            policy_id="cpol_00000000-0000-0000-0000-000000000000",
            canonical_branch=branch,
            promotion_app_id=1,
            control_verifier_app_id=2,
            integrity_ruleset_id=1,
            writer_ruleset_id=2,
            required_checks=(GitHubRequiredCheckV1(name="quality", expected_app_id=1),),
            allowed_update_actor_app_id=1,
            human_acceptance_must_bind_target=True,
            independent_evaluation_must_bind_target=True,
            promotion_property_requirements=(
                PromotionPropertyRequirementV1(property_name="RELAY_FAIL_CLOSED"),
            ),
        )
        return value

    @field_validator("required_check_specs")
    @classmethod
    def checks_are_canonical(
        cls, value: tuple[GitHubRequiredCheckV1, ...]
    ) -> tuple[GitHubRequiredCheckV1, ...]:
        keys = tuple((item.name, item.expected_app_id) for item in value)
        if keys != tuple(sorted(set(keys))) or not value:
            raise ValueError("required check specs must be unique and ordered")
        return value

    @model_validator(mode="after")
    def identities_agree(self) -> CanonicalPromotionSubjectV1:
        for commit in (self.expected_parent, self.target_commit):
            if commit.repository != self.repository or _SHA.fullmatch(commit.sha) is None:
                raise ValueError("subject commits must use its repository and full canonical SHAs")
        if self.expected_parent.sha == self.target_commit.sha:
            raise ValueError("promotion parent and target must differ")
        return self


class CanonicalPolicyBindingSubjectV1(PromotionModel):
    """Exact Human-authorized compare-and-swap for a durable policy binding."""

    subject_type: Literal["CanonicalPolicyBindingSubjectV1"] = "CanonicalPolicyBindingSubjectV1"
    schema_version: Literal[1] = 1
    project_id: ProjectId
    repository: RepositoryRef
    canonical_ref: str
    expected_current_binding_id: CanonicalPromotionBindingId | None
    expected_current_revision: int = Field(ge=0)
    expected_current_binding_digest: ContentDigest | None
    target_revision: int = Field(ge=1)
    target_state: CanonicalPromotionPolicyBindingState
    target_policy: CanonicalPromotionPolicyV1 | None
    target_policy_digest: ContentDigest | None

    @model_validator(mode="after")
    def transition_is_exact(self) -> CanonicalPolicyBindingSubjectV1:
        if self.target_revision != self.expected_current_revision + 1:
            raise ValueError("target binding revision must advance exactly once")
        if self.expected_current_revision == 0 and any(
            item is not None
            for item in (self.expected_current_binding_id, self.expected_current_binding_digest)
        ):
            raise ValueError("initial binding must not name a current binding")
        if self.expected_current_revision > 0 and any(
            item is None
            for item in (self.expected_current_binding_id, self.expected_current_binding_digest)
        ):
            raise ValueError("later binding transition requires exact current identity and digest")
        if self.target_state is CanonicalPromotionPolicyBindingState.UNMANAGED:
            if self.target_policy is not None or self.target_policy_digest is not None:
                raise ValueError("UNMANAGED binding cannot carry a policy")
        elif self.target_policy is None or self.target_policy_digest != policy_digest(
            self.target_policy
        ):
            raise ValueError("MANAGED binding requires its exact policy and digest")
        if self.target_policy is not None and self.canonical_ref != (
            "refs/heads/" + self.target_policy.canonical_branch
        ):
            raise ValueError("policy branch must equal the exact canonical ref")
        return self


class CanonicalPromotionReconciliationSubjectV1(PromotionModel):
    """Exact Human authority for reconciling a visible quarantined target."""

    subject_type: Literal["CanonicalPromotionReconciliationSubjectV1"] = (
        "CanonicalPromotionReconciliationSubjectV1"
    )
    schema_version: Literal[1] = 1
    project_id: ProjectId
    repository: RepositoryRef
    canonical_ref: str
    promotion_id: RepositoryPromotionId
    visible_unverified_result_digest: ContentDigest
    original_subject_digest: ContentDigest
    original_target_commit: CommitRef
    original_binding_id: CanonicalPromotionBindingId
    original_binding_revision: int = Field(ge=1)
    original_binding_digest: ContentDigest
    original_policy_digest: ContentDigest
    expected_visible_head: CommitRef
    original_governance_basis_digest: ContentDigest
    current_required_check_observation_digest: ContentDigest
    current_source_control_observation_digest: ContentDigest

    @model_validator(mode="after")
    def target_is_exact(self) -> CanonicalPromotionReconciliationSubjectV1:
        if (
            self.expected_visible_head != self.original_target_commit
            or self.original_target_commit.repository != self.repository
        ):
            raise ValueError("reconciliation subject must bind exact original visible target")
        return self


class CanonicalPromotionPolicyBindingV1(PromotionModel):
    """One immutable revision in an exact canonical-ref binding chain."""

    binding_id: CanonicalPromotionBindingId
    schema_version: Literal[1] = 1
    project_id: ProjectId
    repository: RepositoryRef
    canonical_ref: str
    revision: int = Field(ge=1)
    state: CanonicalPromotionPolicyBindingState
    policy: CanonicalPromotionPolicyV1 | None
    policy_digest: ContentDigest | None
    authorization_id: RepositoryMutationAuthorizationId
    supersedes_binding_id: CanonicalPromotionBindingId | None
    bound_at: datetime

    @field_validator("bound_at")
    @classmethod
    def bound_time_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("bound_at must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def binding_payload_is_consistent(self) -> CanonicalPromotionPolicyBindingV1:
        if (self.revision == 1) != (self.supersedes_binding_id is None):
            raise ValueError("binding chain root/supersession identity is inconsistent")
        if self.state is CanonicalPromotionPolicyBindingState.UNMANAGED:
            if self.policy is not None or self.policy_digest is not None:
                raise ValueError("UNMANAGED binding cannot carry a policy")
        elif self.policy is None or self.policy_digest != policy_digest(self.policy):
            raise ValueError("MANAGED binding policy digest is invalid")
        return self


class PromotionPropertyResultV1(PromotionModel):
    property_name: str
    outcome: PromotionPropertyOutcome
    exact_subject_ref: ContentDigest
    basis_refs: tuple[str, ...]
    reason_codes: tuple[str, ...]


class PromotionAcceptedResultRefV1(PromotionModel):
    """Exact accepted result reconstructed from durable Slice 1.7 records."""

    result_id: SliceResultId
    result_baseline_id: BaselineId
    accepted_commit: CommitRef
    manual_evaluation_id: ManualEvaluationId
    human_approval_decision_id: HumanDecisionId
    accepted_execution_id: ExecutionId
    accepted_at: datetime


class PromotionIndependentEvaluationRefV1(PromotionModel):
    """Structured independent judgment with its own exact immutable subject."""

    evaluation_id: str
    exact_subject: CommitRef
    outcome: Literal["ACCEPT"] = "ACCEPT"


class PromotionGovernanceBasisV1(PromotionModel):
    """Exact accepted/evaluated ancestry and target continuity basis."""

    schema_version: Literal[1] = 1
    project_id: ProjectId
    slice_id: SliceId | None
    accepted_result_ref: PromotionAcceptedResultRefV1
    independent_evaluation_refs: tuple[PromotionIndependentEvaluationRefV1, ...]
    continuity_anchor_commit: CommitRef
    target_commit: CommitRef
    governance_basis_digest: ContentDigest

    @model_validator(mode="after")
    def subjects_are_exact_and_ordered(self) -> PromotionGovernanceBasisV1:
        commits = (
            self.accepted_result_ref.accepted_commit,
            self.continuity_anchor_commit,
            self.target_commit,
        )
        if any(item.repository != self.target_commit.repository for item in commits):
            raise ValueError("governance basis commits must share one exact repository")
        evaluation_ids = tuple(item.evaluation_id for item in self.independent_evaluation_refs)
        if evaluation_ids != tuple(sorted(set(evaluation_ids))):
            raise ValueError("independent evaluation refs must be unique and canonically ordered")
        if self.governance_basis_digest != governance_basis_digest(self):
            raise ValueError("governance basis digest does not match its exact records")
        return self


class PromotionEligibilityV1(PromotionModel):
    state: PromotionAuthorizability | PromotionEligibilityState
    properties: tuple[PromotionPropertyResultV1, ...]
    basis_digest: ContentDigest
    subject: CanonicalPromotionSubjectV1 | None = None
    subject_digest: ContentDigest | None = None

    @model_validator(mode="after")
    def subject_matches_state(self) -> PromotionEligibilityV1:
        if self.state in {
            PromotionAuthorizability.AUTHORIZABLE,
            PromotionEligibilityState.ELIGIBLE,
        }:
            if self.subject is None or self.subject_digest != canonical_promotion_subject_digest(
                self.subject
            ):
                raise ValueError("authorizable/eligible state requires exact subject digest")
        elif self.subject is not None or self.subject_digest is not None:
            raise ValueError("non-executable state cannot carry a subject")
        return self


class CanonicalPromotionPreparationV1(PromotionModel):
    state: PromotionAuthorizability
    eligibility: PromotionEligibilityV1
    subject: CanonicalPromotionSubjectV1 | None = None
    subject_digest: ContentDigest | None = None
    binding: CanonicalPromotionPolicyBindingV1 | None = None
    policy: CanonicalPromotionPolicyV1 | None = None
    governance_basis: PromotionGovernanceBasisV1 | None = None


class CanonicalPromotionReconciliationPreparationV1(PromotionModel):
    """Read-only exact classification for one quarantined promotion result."""

    state: ReconciliationPreparationState
    reason: str
    subject: CanonicalPromotionReconciliationSubjectV1 | None = None
    subject_digest: ContentDigest | None = None

    @model_validator(mode="after")
    def subject_matches_state(self) -> CanonicalPromotionReconciliationPreparationV1:
        if self.state is ReconciliationPreparationState.RECONCILABLE:
            if self.subject is None or self.subject_digest != reconciliation_subject_digest(
                self.subject
            ):
                raise ValueError("RECONCILABLE preparation requires its exact subject")
        elif self.subject is not None or self.subject_digest is not None:
            raise ValueError("non-reconcilable preparation cannot carry an authority subject")
        return self


class RepositoryPromotionIntentV1(PromotionModel):
    promotion_id: RepositoryPromotionId
    project_id: ProjectId
    repository: RepositoryRef
    canonical_ref: str
    subject: CanonicalPromotionSubjectV1
    subject_digest: ContentDigest
    authorization_id: RepositoryMutationAuthorizationId
    authorization_subject_digest: ContentDigest
    binding: CanonicalPromotionPolicyBindingV1
    policy: CanonicalPromotionPolicyV1
    governance_basis_digest: ContentDigest
    required_check_observation_digest: ContentDigest
    source_control_observation_digest: ContentDigest
    prewrite_basis_digest: ContentDigest
    expected_parent: CommitRef
    target_commit: CommitRef
    created_at: datetime
    executor: ActorRef

    @model_validator(mode="after")
    def intent_is_subject_bound(self) -> RepositoryPromotionIntentV1:
        if (
            self.subject_digest != canonical_promotion_subject_digest(self.subject)
            or self.project_id != self.subject.project_id
            or self.repository != self.subject.repository
            or self.canonical_ref != self.subject.canonical_ref
            or self.expected_parent != self.subject.expected_parent
            or self.target_commit != self.subject.target_commit
            or self.governance_basis_digest != self.subject.governance_basis_digest
        ):
            raise ValueError("promotion intent differs from exact authorized subject")
        return self


class RepositoryPromotionResultV1(PromotionModel):
    promotion_id: RepositoryPromotionId
    project_id: ProjectId
    repository: RepositoryRef
    canonical_ref: str
    outcome: PromotionResultOutcome
    expected_parent: CommitRef
    target_commit: CommitRef
    observed_head: CommitRef | None
    reconciled_after_restart: bool = False
    reason_code: str | None = None
    source_control_observation_digest: ContentDigest | None = None
    observed_at: datetime


class CanonicalPromotionReconciliationV1(PromotionModel):
    reconciliation_id: CanonicalPromotionReconciliationId
    promotion_id: RepositoryPromotionId
    project_id: ProjectId
    repository: RepositoryRef
    canonical_ref: str
    original_visible_unverified_result_digest: ContentDigest
    target_commit: CommitRef
    authorization_id: RepositoryMutationAuthorizationId
    reconciliation_subject_digest: ContentDigest
    original_binding_id: CanonicalPromotionBindingId
    original_binding_revision: int = Field(ge=1)
    original_binding_digest: ContentDigest
    original_policy_digest: ContentDigest
    original_governance_basis_digest: ContentDigest
    current_required_check_observation_digest: ContentDigest
    current_source_control_observation_digest: ContentDigest
    reconciled_at: datetime
    reconciled_by: ActorRef
    outcome: Literal["RECONCILED"] = "RECONCILED"


def canonical_json_digest(value: DomainModel) -> ContentDigest:
    raw = json.dumps(
        value.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def canonical_promotion_subject_digest(subject: CanonicalPromotionSubjectV1) -> ContentDigest:
    return canonical_json_digest(subject)


def policy_digest(policy: CanonicalPromotionPolicyV1) -> ContentDigest:
    return canonical_json_digest(policy)


def binding_digest(binding: CanonicalPromotionPolicyBindingV1) -> ContentDigest:
    return canonical_json_digest(binding)


def canonical_policy_binding_subject_digest(
    subject: CanonicalPolicyBindingSubjectV1,
) -> ContentDigest:
    return canonical_json_digest(subject)


def reconciliation_subject_digest(
    subject: CanonicalPromotionReconciliationSubjectV1,
) -> ContentDigest:
    return canonical_json_digest(subject)


def governance_basis_digest(basis: PromotionGovernanceBasisV1) -> ContentDigest:
    payload = basis.model_dump(mode="json", exclude={"governance_basis_digest"})
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"


__all__ = [
    "CanonicalPromotionPolicyV1",
    "CanonicalPromotionSubjectV1",
    "CanonicalPolicyBindingSubjectV1",
    "CanonicalPromotionReconciliationSubjectV1",
    "CanonicalPromotionPolicyBindingV1",
    "PromotionPropertyOutcome",
    "PromotionAuthorizability",
    "PromotionEligibilityState",
    "PromotionPropertyRequirementV1",
    "PromotionPropertyResultV1",
    "PromotionAcceptedResultRefV1",
    "PromotionIndependentEvaluationRefV1",
    "PromotionGovernanceBasisV1",
    "PromotionEligibilityV1",
    "CanonicalPromotionPreparationV1",
    "CanonicalPromotionReconciliationPreparationV1",
    "RepositoryPromotionIntentV1",
    "RepositoryPromotionResultV1",
    "PromotionResultOutcome",
    "CanonicalPromotionReconciliationV1",
    "CanonicalRefHealth",
    "CanonicalPromotionPolicyBindingState",
    "CanonicalPromotionPolicyBindingResolution",
    "ReconciliationPreparationState",
    "ReconciliationOutcome",
    "GitHubRequiredCheckV1",
    "binding_digest",
    "canonical_json_digest",
    "canonical_policy_binding_subject_digest",
    "canonical_promotion_subject_digest",
    "policy_digest",
    "reconciliation_subject_digest",
    "governance_basis_digest",
]
