"""Immutable context and work-packet contracts for Slice 2.3."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, Field, StringConstraints, field_validator, model_validator

from relay_engine.agent_runtime import (
    CredentialRef,
    RuntimeCapability,
    RuntimeExecutionLimits,
    RuntimePermissionProfileRef,
    RuntimeSelection,
)
from relay_engine.domain import (
    AcceptanceCriterion,
    Artifact,
    ArtifactId,
    Baseline,
    BaselineId,
    CommitRef,
    ContentDigest,
    ProjectId,
    RepositoryRef,
    ScopeSpec,
    SliceId,
)
from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.role_contracts import (
    RequirementStatus,
    RoleApplicabilityEvaluation,
    RoleContractRef,
    RoleOutputRequirement,
    VerificationAssetPermission,
)

type WorkPacketKey = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=64)]
type ContextManifestKey = Annotated[
    str, StringConstraints(strict=True, min_length=1, max_length=64)
]
type ContextEntryKey = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=64)]
type StableRequirementKey = Annotated[
    str, StringConstraints(strict=True, min_length=1, max_length=64)
]
type StableContextSourceKey = Annotated[
    str, StringConstraints(strict=True, min_length=1, max_length=64)
]
type StableResolverKey = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=64)]
type BoundedText = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=4096),
    AfterValidator(require_nonblank),
]
type OpaqueIdentity = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=256),
    AfterValidator(require_nonblank),
]

_STABLE_KEY = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$", re.ASCII)


def _validate_key(value: str) -> str:
    if not _STABLE_KEY.fullmatch(value):
        raise ValueError("key must be lowercase ASCII segments separated by single hyphens")
    return value


def _tuple_is_unique(values: tuple[object, ...], label: str) -> tuple[object, ...]:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")
    return values


def _require_sorted[T](values: tuple[T, ...], key: Callable[[T], Any], label: str) -> None:
    ordered = tuple(sorted(values, key=key))
    if values != ordered:
        raise ValueError(f"{label} must use canonical ordering")


def _canonical_model_json(value: DomainModel) -> str:
    validated = type(value).model_validate(value.model_dump(mode="python"))
    return json.dumps(
        validated.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: DomainModel) -> ContentDigest:
    return "sha256:" + hashlib.sha256(_canonical_model_json(value).encode("utf-8")).hexdigest()


class AuthorityReferenceType(StrEnum):
    SLICE_AUTHORIZATION_GRANT = "SLICE_AUTHORIZATION_GRANT"
    REPOSITORY_MUTATION_AUTHORIZATION = "REPOSITORY_MUTATION_AUTHORIZATION"
    HUMAN_GOVERNANCE_RECORD = "HUMAN_GOVERNANCE_RECORD"


class ContextClass(StrEnum):
    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"


class ContextSourceKind(StrEnum):
    RELAY_ARTIFACT = "RELAY_ARTIFACT"
    GOVERNANCE_RECORD = "GOVERNANCE_RECORD"
    REPOSITORY_CONTENT = "REPOSITORY_CONTENT"
    TOOL_DEFINITION = "TOOL_DEFINITION"
    SKILL = "SKILL"
    RETRIEVAL_RESULT = "RETRIEVAL_RESULT"
    RUNTIME_OBSERVATION = "RUNTIME_OBSERVATION"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"
    SESSION_EXCERPT = "SESSION_EXCERPT"


class NormalizationStatus(StrEnum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    INDETERMINATE = "INDETERMINATE"


class NormalizationIssueCode(StrEnum):
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    AMBIGUOUS_FIELD = "AMBIGUOUS_FIELD"
    CONFLICTING_FIELD = "CONFLICTING_FIELD"
    UNSUPPORTED_SEMANTIC = "UNSUPPORTED_SEMANTIC"
    SOURCE_UNVERIFIABLE = "SOURCE_UNVERIFIABLE"


class MaterialKind(StrEnum):
    RELAY_ARTIFACT = "RELAY_ARTIFACT"
    REPOSITORY_CONTENT = "REPOSITORY_CONTENT"
    CAPTURED_MATERIAL = "CAPTURED_MATERIAL"


class ControlMirrorKind(StrEnum):
    AUTHORITY_BASIS = "AUTHORITY_BASIS"
    ROLE_CONTRACT = "ROLE_CONTRACT"
    POLICY_BASIS = "POLICY_BASIS"
    GOVERNANCE_PROFILE = "GOVERNANCE_PROFILE"
    ACCEPTED_DESIGN = "ACCEPTED_DESIGN"
    SLICE_DEFINITION = "SLICE_DEFINITION"
    SOURCE_BASELINE = "SOURCE_BASELINE"


class SliceDefinitionRef(DomainModel):
    slice_id: SliceId
    definition_revision: int = Field(ge=1)
    content_digest: ContentDigest


class SourceBaselineRef(DomainModel):
    baseline_id: BaselineId
    project_id: ProjectId
    commit: CommitRef
    content_digest: ContentDigest


class AuthorityBasisRef(DomainModel):
    authority_type: AuthorityReferenceType
    authority_key: StableRequirementKey
    record_digest: ContentDigest
    subject_digest: ContentDigest | None

    @field_validator("authority_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


class PolicyBasisRef(DomainModel):
    policy_key: StableRequirementKey
    policy_version: int = Field(ge=1)
    policy_digest: ContentDigest
    effective_scope_digest: ContentDigest

    @field_validator("policy_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


class GovernanceProfileRef(DomainModel):
    profile_key: StableRequirementKey
    profile_version: int = Field(ge=1)
    content_digest: ContentDigest
    policy_basis_digest: ContentDigest

    @field_validator("profile_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


class WorkspacePolicyRef(DomainModel):
    policy_key: StableRequirementKey
    content_digest: ContentDigest

    @field_validator("policy_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


class PlanningArtifactSourceRef(DomainModel):
    source_key: StableRequirementKey
    source_type: StableRequirementKey
    source_version: BoundedText | None
    content_digest: ContentDigest
    provenance_digest: ContentDigest
    locator: BoundedText | None

    @field_validator("source_key", "source_type")
    @classmethod
    def keys_are_stable(cls, value: str) -> str:
        return _validate_key(value)


class PlanningAdapterRef(DomainModel):
    adapter_key: StableRequirementKey
    adapter_version: int = Field(ge=1)
    adapter_digest: ContentDigest
    supported_source_type: StableRequirementKey

    @field_validator("adapter_key", "supported_source_type")
    @classmethod
    def keys_are_stable(cls, value: str) -> str:
        return _validate_key(value)


class NormalizationIssue(DomainModel):
    issue_code: NormalizationIssueCode
    field_key: StableRequirementKey
    source_key: StableRequirementKey | None

    @field_validator("field_key", "source_key")
    @classmethod
    def keys_are_stable(cls, value: str | None) -> str | None:
        return None if value is None else _validate_key(value)


def _issue_key(issue: NormalizationIssue) -> tuple[str, str, str]:
    return (issue.issue_code.value, issue.field_key, issue.source_key or "")


class NormalizedEngineeringIntent(DomainModel):
    schema_version: Literal[1] = 1
    source_refs: tuple[PlanningArtifactSourceRef, ...]
    adapter_ref: PlanningAdapterRef | None
    objective: BoundedText
    scope: ScopeSpec
    acceptance_criteria: tuple[AcceptanceCriterion, ...]
    dependency_slice_ids: tuple[SliceId, ...]
    quality_requirement_keys: tuple[StableRequirementKey, ...]
    status: NormalizationStatus
    issues: tuple[NormalizationIssue, ...]

    @model_validator(mode="after")
    def canonical_and_complete(self) -> NormalizedEngineeringIntent:
        def source_key(source: PlanningArtifactSourceRef) -> tuple[str, ...]:
            return (
                source.source_type,
                source.source_key,
                source.source_version or "",
                source.content_digest,
                source.provenance_digest,
            )

        _require_sorted(self.source_refs, source_key, "source_refs")
        source_ids = [
            (s.source_type, s.source_key, s.source_version or "") for s in self.source_refs
        ]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("planning sources cannot duplicate or conflict on stable identity")
        for name, statements in (
            ("in_scope", self.scope.in_scope),
            ("out_of_scope", self.scope.out_of_scope),
        ):
            if statements != tuple(sorted(statements, key=lambda item: item.encode("utf-8"))):
                raise ValueError(f"scope {name} must use UTF-8 lexical order")
            if len(statements) != len(set(statements)):
                raise ValueError(f"scope {name} must be unique")
        if set(self.scope.in_scope) & set(self.scope.out_of_scope):
            raise ValueError("scope statements cannot be both in and out of scope")
        criteria_keys = tuple(item.key for item in self.acceptance_criteria)
        if criteria_keys != tuple(sorted(criteria_keys)) or len(set(criteria_keys)) != len(
            criteria_keys
        ):
            raise ValueError("acceptance criteria must be unique and sorted by key")
        _require_sorted(self.dependency_slice_ids, str, "dependency_slice_ids")
        _tuple_is_unique(self.dependency_slice_ids, "dependency_slice_ids")
        _require_sorted(self.quality_requirement_keys, str, "quality_requirement_keys")
        _tuple_is_unique(self.quality_requirement_keys, "quality_requirement_keys")
        for key in self.quality_requirement_keys:
            _validate_key(key)
        _require_sorted(self.issues, _issue_key, "issues")
        _tuple_is_unique(self.issues, "issues")
        if self.status is NormalizationStatus.COMPLETE and (not self.source_refs or self.issues):
            raise ValueError("COMPLETE intent requires source refs and no issues")
        return self


class ArtifactMaterialRef(DomainModel):
    material_kind: Literal["RELAY_ARTIFACT"]
    artifact: Artifact
    provenance_digest: ContentDigest


class RepositoryContentMaterialRef(DomainModel):
    material_kind: Literal["REPOSITORY_CONTENT"]
    repository: RepositoryRef
    commit: CommitRef
    path: BoundedText
    content_digest: ContentDigest
    provenance_digest: ContentDigest

    @field_validator("path")
    @classmethod
    def path_is_canonical_relative(cls, value: str) -> str:
        if (
            value.startswith("/")
            or "\\" in value
            or any(part in {"", ".", ".."} for part in value.split("/"))
        ):
            raise ValueError("path must be canonical repository-relative POSIX path")
        if re.match(r"^[A-Za-z]:", value):
            raise ValueError("path must not be a Windows absolute path")
        return value

    @model_validator(mode="after")
    def repository_matches_commit(self) -> RepositoryContentMaterialRef:
        if self.commit.repository != self.repository:
            raise ValueError("commit repository must match repository")
        return self


class CapturedMaterialRef(DomainModel):
    material_kind: Literal["CAPTURED_MATERIAL"]
    resolver_key: StableResolverKey
    resolver_version: int = Field(ge=1)
    material_key: OpaqueIdentity
    material_version: OpaqueIdentity
    content_digest: ContentDigest
    provenance_digest: ContentDigest

    @field_validator("resolver_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


type ContextMaterialRef = Annotated[
    ArtifactMaterialRef | RepositoryContentMaterialRef | CapturedMaterialRef,
    Field(discriminator="material_kind"),
]


class ContextSourceRef(DomainModel):
    source_kind: ContextSourceKind
    source_key: StableContextSourceKey
    source_version: BoundedText | None
    material_ref: ContextMaterialRef
    locator: BoundedText | None

    @field_validator("source_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)

    @model_validator(mode="after")
    def source_material_compatible(self) -> ContextSourceRef:
        allowed: dict[ContextSourceKind, tuple[type[DomainModel], ...]] = {
            ContextSourceKind.RELAY_ARTIFACT: (ArtifactMaterialRef,),
            ContextSourceKind.GOVERNANCE_RECORD: (
                ArtifactMaterialRef,
                RepositoryContentMaterialRef,
            ),
            ContextSourceKind.REPOSITORY_CONTENT: (RepositoryContentMaterialRef,),
            ContextSourceKind.TOOL_DEFINITION: (ArtifactMaterialRef, CapturedMaterialRef),
            ContextSourceKind.SKILL: (ArtifactMaterialRef, CapturedMaterialRef),
            ContextSourceKind.RETRIEVAL_RESULT: (ArtifactMaterialRef, CapturedMaterialRef),
            ContextSourceKind.RUNTIME_OBSERVATION: (ArtifactMaterialRef, CapturedMaterialRef),
            ContextSourceKind.EXTERNAL_REFERENCE: (ArtifactMaterialRef, CapturedMaterialRef),
            ContextSourceKind.SESSION_EXCERPT: (ArtifactMaterialRef, CapturedMaterialRef),
        }
        if not isinstance(self.material_ref, allowed[self.source_kind]):
            raise ValueError("source kind is incompatible with material kind")
        return self


class ControlMirrorBinding(DomainModel):
    mirror_kind: ControlMirrorKind
    control_subject_digest: ContentDigest


class ContextEntryRef(DomainModel):
    entry_key: ContextEntryKey
    context_class: ContextClass
    source: ContextSourceRef
    control_mirror_binding: ControlMirrorBinding | None

    @field_validator("entry_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


class ContextManifest(DomainModel):
    schema_version: Literal[1] = 1
    project_id: ProjectId
    slice_definition_ref: SliceDefinitionRef
    manifest_key: ContextManifestKey
    revision: int = Field(ge=1)
    entries: tuple[ContextEntryRef, ...]

    @field_validator("manifest_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)

    @field_validator("entries")
    @classmethod
    def entries_are_canonical(
        cls, value: tuple[ContextEntryRef, ...]
    ) -> tuple[ContextEntryRef, ...]:
        keys = tuple(entry.entry_key for entry in value)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("manifest entries must be unique and sorted by entry_key")
        return value


class ContextManifestRef(DomainModel):
    project_id: ProjectId
    slice_id: SliceId
    manifest_key: ContextManifestKey
    revision: int = Field(ge=1)
    content_digest: ContentDigest

    @field_validator("manifest_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


class EvidenceRequirement(DomainModel):
    key: StableRequirementKey
    statement: BoundedText
    required: bool
    role_output_requirement: RoleOutputRequirement | None

    @field_validator("key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


class DeliverableRequirement(EvidenceRequirement):
    pass


class HardStopRequirement(DomainModel):
    key: StableRequirementKey
    statement: BoundedText

    @field_validator("key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


class ProtectedVerificationRequirement(DomainModel):
    artifact: Artifact
    required_operation: VerificationAssetPermission
    separate_authority_ref: AuthorityBasisRef | None


class ProtectedVerificationRequirementRef(DomainModel):
    artifact_id: ArtifactId
    artifact_content_digest: ContentDigest
    required_operation: VerificationAssetPermission
    requirement_digest: ContentDigest


class WorkPacketRef(DomainModel):
    project_id: ProjectId
    slice_id: SliceId
    packet_key: WorkPacketKey
    revision: int = Field(ge=1)
    content_digest: ContentDigest

    @field_validator("packet_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)


def _authority_key(item: AuthorityBasisRef) -> tuple[str, str, str, str]:
    return (
        item.authority_type.value,
        item.authority_key,
        item.record_digest,
        item.subject_digest or "",
    )


def _artifact_key(item: Artifact) -> tuple[str, str, str, str]:
    return (item.path, str(item.id), item.commit.sha, item.content_digest)


def _protected_key(item: ProtectedVerificationRequirement) -> tuple[str, str, str, str, str]:
    authority = (
        ""
        if item.separate_authority_ref is None
        else _canonical_model_json(item.separate_authority_ref)
    )
    return (
        item.artifact.path,
        str(item.artifact.id),
        item.artifact.content_digest,
        item.required_operation.value,
        authority,
    )


class WorkPacket(DomainModel):
    schema_version: Literal[1] = 1
    packet_key: WorkPacketKey
    revision: int = Field(ge=1)
    project_id: ProjectId
    slice_definition_ref: SliceDefinitionRef
    source_baseline_ref: SourceBaselineRef
    authority_refs: tuple[AuthorityBasisRef, ...]
    policy_basis_ref: PolicyBasisRef
    governance_profile_ref: GovernanceProfileRef | None
    role_contract_ref: RoleContractRef
    accepted_design_artifacts: tuple[Artifact, ...]
    normalized_intent: NormalizedEngineeringIntent
    context_manifest_ref: ContextManifestRef
    required_context_keys: tuple[ContextEntryKey, ...]
    evidence_requirements: tuple[EvidenceRequirement, ...]
    deliverable_requirements: tuple[DeliverableRequirement, ...]
    hard_stops: tuple[HardStopRequirement, ...]
    required_runtime_capabilities: tuple[RuntimeCapability, ...]
    runtime_selection_requirement: RuntimeSelection | None
    runtime_limits: RuntimeExecutionLimits
    runtime_permission_profile_ref: RuntimePermissionProfileRef | None
    credential_refs: tuple[CredentialRef, ...]
    workspace_policy_ref: WorkspacePolicyRef | None
    required_workspace_property_keys: tuple[StableRequirementKey, ...]
    protected_verification_requirements: tuple[ProtectedVerificationRequirement, ...]
    authorized_successor_ref: WorkPacketRef | None

    @field_validator("packet_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _validate_key(value)

    @model_validator(mode="after")
    def canonical_and_consistent(self) -> WorkPacket:
        if self.source_baseline_ref.project_id != self.project_id:
            raise ValueError("source baseline project must match packet project")
        if self.slice_definition_ref.slice_id != self.context_manifest_ref.slice_id:
            raise ValueError("packet and context manifest slices must match")
        if (
            self.normalized_intent.status is not NormalizationStatus.COMPLETE
            or self.normalized_intent.issues
        ):
            raise ValueError("WorkPacket requires COMPLETE normalized intent without issues")
        if not self.authority_refs:
            raise ValueError("authority_refs must not be empty")
        _require_sorted(self.authority_refs, _authority_key, "authority_refs")
        _tuple_is_unique(self.authority_refs, "authority_refs")
        _require_sorted(self.accepted_design_artifacts, _artifact_key, "accepted_design_artifacts")
        _tuple_is_unique(self.accepted_design_artifacts, "accepted_design_artifacts")
        _require_sorted(self.required_context_keys, str, "required_context_keys")
        _tuple_is_unique(self.required_context_keys, "required_context_keys")
        for key in self.required_context_keys:
            _validate_key(key)
        for name, values in (
            ("evidence_requirements", self.evidence_requirements),
            ("deliverable_requirements", self.deliverable_requirements),
            ("hard_stops", self.hard_stops),
        ):
            keys = tuple(item.key for item in values)
            if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
                raise ValueError(f"{name} must be unique and sorted by key")
        caps = tuple(RuntimeCapability)
        if self.required_runtime_capabilities != tuple(
            cap for cap in caps if cap in self.required_runtime_capabilities
        ):
            raise ValueError("required_runtime_capabilities must use enum declaration order")
        _tuple_is_unique(self.required_runtime_capabilities, "required_runtime_capabilities")
        credential_ids = tuple(item.credential_id for item in self.credential_refs)
        if credential_ids != tuple(sorted(credential_ids)) or len(credential_ids) != len(
            set(credential_ids)
        ):
            raise ValueError("credential_refs must be unique and sorted by credential_id")
        _require_sorted(
            self.required_workspace_property_keys, str, "required_workspace_property_keys"
        )
        _tuple_is_unique(self.required_workspace_property_keys, "required_workspace_property_keys")
        for key in self.required_workspace_property_keys:
            _validate_key(key)
        _require_sorted(
            self.protected_verification_requirements,
            _protected_key,
            "protected_verification_requirements",
        )
        _tuple_is_unique(
            self.protected_verification_requirements, "protected_verification_requirements"
        )
        authority_identities = tuple(
            (item.authority_type.value, item.authority_key) for item in self.authority_refs
        )
        if len(authority_identities) != len(set(authority_identities)):
            raise ValueError("authority_refs contain conflicting stable identities")
        artifact_identities = tuple(
            (item.path, str(item.id)) for item in self.accepted_design_artifacts
        )
        if len(artifact_identities) != len(set(artifact_identities)):
            raise ValueError("accepted_design_artifacts contain conflicting stable identities")
        artifact_ids = tuple(item.id for item in self.accepted_design_artifacts)
        if len(artifact_ids) != len(set(artifact_ids)):
            raise ValueError("accepted_design_artifacts cannot repeat an ArtifactId")
        protected_identities = tuple(
            (
                item.artifact.path,
                str(item.artifact.id),
                item.required_operation.value,
                ""
                if item.separate_authority_ref is None
                else _canonical_model_json(item.separate_authority_ref),
            )
            for item in self.protected_verification_requirements
        )
        if len(protected_identities) != len(set(protected_identities)):
            raise ValueError("protected verification requirements contain conflicting identities")
        return self


class WorkPacketIdentityConflict(DomainModel):
    has_conflict: bool
    packet_key: WorkPacketKey | None
    revision: int | None


class ContextManifestIdentityConflict(DomainModel):
    has_conflict: bool
    manifest_key: ContextManifestKey | None
    revision: int | None


class SliceDefinitionFact(DomainModel):
    evaluated_ref: SliceDefinitionRef
    status: RequirementStatus


class SourceBaselineFact(DomainModel):
    evaluated_ref: SourceBaselineRef
    status: RequirementStatus


class AuthorityBasisFact(DomainModel):
    evaluated_ref: AuthorityBasisRef
    status: RequirementStatus


class PolicyBasisFact(DomainModel):
    evaluated_ref: PolicyBasisRef
    status: RequirementStatus


class ContextManifestFact(DomainModel):
    evaluated_ref: ContextManifestRef
    status: RequirementStatus


class GovernanceProfileFact(DomainModel):
    evaluated_policy_basis_ref: PolicyBasisRef
    evaluated_profile_ref: GovernanceProfileRef | None
    profile_requirement_status: RequirementStatus
    profile_status: RequirementStatus


class AcceptedDesignFact(DomainModel):
    evaluated_artifact: Artifact
    status: RequirementStatus


class ProtectedVerificationAuthorityFact(DomainModel):
    evaluated_requirement_ref: ProtectedVerificationRequirementRef
    evaluated_authority_ref: AuthorityBasisRef | None
    status: RequirementStatus


class ContextMaterializationFact(DomainModel):
    evaluated_material_ref: ContextMaterialRef
    material_status: RequirementStatus
    observed_content_digest: ContentDigest | None
    observed_provenance_digest: ContentDigest | None

    @model_validator(mode="after")
    def observed_digests_match_status(self) -> ContextMaterializationFact:
        expected_content, expected_provenance = material_digests(self.evaluated_material_ref)
        if self.material_status is RequirementStatus.SATISFIED:
            if self.observed_content_digest is None or self.observed_provenance_digest is None:
                raise ValueError(
                    "SATISFIED materialization requires observed content and provenance digests"
                )
            if (self.observed_content_digest, self.observed_provenance_digest) != (
                expected_content,
                expected_provenance,
            ):
                raise ValueError(
                    "SATISFIED materialization observations must match expected digests"
                )
        return self


class WorkPacketConformanceFacts(DomainModel):
    evaluated_work_packet_ref: WorkPacketRef
    evaluated_context_manifest_ref: ContextManifestRef
    slice_definition_fact: SliceDefinitionFact
    source_baseline_fact: SourceBaselineFact
    authority_facts: tuple[AuthorityBasisFact, ...]
    policy_basis_fact: PolicyBasisFact
    governance_profile_fact: GovernanceProfileFact
    role_contract_applicability: RoleApplicabilityEvaluation
    accepted_design_facts: tuple[AcceptedDesignFact, ...]
    context_manifest_fact: ContextManifestFact
    protected_verification_authority_facts: tuple[ProtectedVerificationAuthorityFact, ...]
    materialization_facts: tuple[ContextMaterializationFact, ...]


class WorkPacketReason(StrEnum):
    WORK_PACKET_IDENTITY_CONFLICT = "WORK_PACKET_IDENTITY_CONFLICT"
    CONTEXT_MANIFEST_IDENTITY_CONFLICT = "CONTEXT_MANIFEST_IDENTITY_CONFLICT"
    WORK_PACKET_REF_MISMATCH = "WORK_PACKET_REF_MISMATCH"
    CONTEXT_MANIFEST_REF_MISMATCH = "CONTEXT_MANIFEST_REF_MISMATCH"
    WORK_PACKET_FACT_SUBJECT_MISMATCH = "WORK_PACKET_FACT_SUBJECT_MISMATCH"
    CONTEXT_MANIFEST_FACT_SUBJECT_MISMATCH = "CONTEXT_MANIFEST_FACT_SUBJECT_MISMATCH"
    SLICE_DEFINITION_FACT_SUBJECT_MISMATCH = "SLICE_DEFINITION_FACT_SUBJECT_MISMATCH"
    SOURCE_BASELINE_FACT_SUBJECT_MISMATCH = "SOURCE_BASELINE_FACT_SUBJECT_MISMATCH"
    AUTHORITY_FACT_SET_MISMATCH = "AUTHORITY_FACT_SET_MISMATCH"
    POLICY_FACT_SUBJECT_MISMATCH = "POLICY_FACT_SUBJECT_MISMATCH"
    GOVERNANCE_PROFILE_FACT_SUBJECT_MISMATCH = "GOVERNANCE_PROFILE_FACT_SUBJECT_MISMATCH"
    ROLE_APPLICABILITY_SUBJECT_MISMATCH = "ROLE_APPLICABILITY_SUBJECT_MISMATCH"
    ACCEPTED_DESIGN_FACT_SET_MISMATCH = "ACCEPTED_DESIGN_FACT_SET_MISMATCH"
    PROTECTED_VERIFICATION_FACT_SET_MISMATCH = "PROTECTED_VERIFICATION_FACT_SET_MISMATCH"
    MATERIALIZATION_FACT_SET_MISMATCH = "MATERIALIZATION_FACT_SET_MISMATCH"
    SLICE_DEFINITION_MISSING = "SLICE_DEFINITION_MISSING"
    SLICE_DEFINITION_STALE = "SLICE_DEFINITION_STALE"
    SLICE_DEFINITION_CONFLICT = "SLICE_DEFINITION_CONFLICT"
    SOURCE_BASELINE_MISSING = "SOURCE_BASELINE_MISSING"
    SOURCE_BASELINE_STALE = "SOURCE_BASELINE_STALE"
    SOURCE_BASELINE_CONFLICT = "SOURCE_BASELINE_CONFLICT"
    SOURCE_BASELINE_REF_MISMATCH = "SOURCE_BASELINE_REF_MISMATCH"
    SOURCE_BASELINE_NONCANONICAL = "SOURCE_BASELINE_NONCANONICAL"
    AUTHORITY_BASIS_MISSING = "AUTHORITY_BASIS_MISSING"
    AUTHORITY_BASIS_STALE = "AUTHORITY_BASIS_STALE"
    AUTHORITY_BASIS_CONFLICT = "AUTHORITY_BASIS_CONFLICT"
    POLICY_BASIS_MISSING = "POLICY_BASIS_MISSING"
    POLICY_BASIS_STALE = "POLICY_BASIS_STALE"
    POLICY_BASIS_CONFLICT = "POLICY_BASIS_CONFLICT"
    GOVERNANCE_PROFILE_REQUIRED = "GOVERNANCE_PROFILE_REQUIRED"
    GOVERNANCE_PROFILE_STALE = "GOVERNANCE_PROFILE_STALE"
    GOVERNANCE_PROFILE_CONFLICT = "GOVERNANCE_PROFILE_CONFLICT"
    ROLE_CONTRACT_NOT_APPLICABLE = "ROLE_CONTRACT_NOT_APPLICABLE"
    ROLE_CONTRACT_APPLICABILITY_UNKNOWN = "ROLE_CONTRACT_APPLICABILITY_UNKNOWN"
    NORMALIZED_INTENT_INCOMPLETE = "NORMALIZED_INTENT_INCOMPLETE"
    NORMALIZED_INTENT_INDETERMINATE = "NORMALIZED_INTENT_INDETERMINATE"
    PLANNING_SOURCE_UNVERIFIABLE = "PLANNING_SOURCE_UNVERIFIABLE"
    WORK_SCOPE_CONFLICT = "WORK_SCOPE_CONFLICT"
    WORK_SCOPE_INDETERMINATE = "WORK_SCOPE_INDETERMINATE"
    REQUIRED_CONTEXT_MISSING = "REQUIRED_CONTEXT_MISSING"
    REQUIRED_CONTEXT_INVALID = "REQUIRED_CONTEXT_INVALID"
    REQUIRED_CONTEXT_INDETERMINATE = "REQUIRED_CONTEXT_INDETERMINATE"
    CONTEXT_SOURCE_UNVERIFIABLE = "CONTEXT_SOURCE_UNVERIFIABLE"
    MUTABLE_CONTEXT_ALIAS_UNRESOLVED = "MUTABLE_CONTEXT_ALIAS_UNRESOLVED"
    CONTEXT_MATERIAL_REF_REQUIRED = "CONTEXT_MATERIAL_REF_REQUIRED"
    CONTEXT_MATERIAL_UNAVAILABLE = "CONTEXT_MATERIAL_UNAVAILABLE"
    CONTEXT_MATERIAL_CONTENT_MISMATCH = "CONTEXT_MATERIAL_CONTENT_MISMATCH"
    CONTEXT_MATERIAL_PROVENANCE_MISMATCH = "CONTEXT_MATERIAL_PROVENANCE_MISMATCH"
    CONTEXT_MATERIAL_RESOLVER_UNSUPPORTED = "CONTEXT_MATERIAL_RESOLVER_UNSUPPORTED"
    CONTEXT_SOURCE_MATERIAL_KIND_INVALID = "CONTEXT_SOURCE_MATERIAL_KIND_INVALID"
    CONTROL_MIRROR_BINDING_REQUIRED = "CONTROL_MIRROR_BINDING_REQUIRED"
    CONTROL_MIRROR_CONFLICT = "CONTROL_MIRROR_CONFLICT"
    ACCEPTED_DESIGN_BASIS_MISSING = "ACCEPTED_DESIGN_BASIS_MISSING"
    ACCEPTED_DESIGN_BASIS_STALE = "ACCEPTED_DESIGN_BASIS_STALE"
    PROTECTED_VERIFICATION_AUTHORITY_REQUIRED = "PROTECTED_VERIFICATION_AUTHORITY_REQUIRED"
    PROTECTED_VERIFICATION_AUTHORITY_INDETERMINATE = (
        "PROTECTED_VERIFICATION_AUTHORITY_INDETERMINATE"
    )
    REQUIRED_EVIDENCE_CONTRACT_MISSING = "REQUIRED_EVIDENCE_CONTRACT_MISSING"
    REQUIRED_DELIVERABLE_CONTRACT_MISSING = "REQUIRED_DELIVERABLE_CONTRACT_MISSING"
    SUCCESSOR_REFERENCE_NOT_AUTHORITY = "SUCCESSOR_REFERENCE_NOT_AUTHORITY"
    NESTED_COLLECTION_NONCANONICAL = "NESTED_COLLECTION_NONCANONICAL"


class ContextConformance(DomainModel):
    status: RequirementStatus
    reasons: tuple[WorkPacketReason, ...]
    missing_context_keys: tuple[ContextEntryKey, ...] = ()

    @model_validator(mode="after")
    def result_collections_are_canonical(self) -> ContextConformance:
        if self.reasons != tuple(reason for reason in WorkPacketReason if reason in self.reasons):
            raise ValueError("context conformance reasons must be unique and enum ordered")
        if self.missing_context_keys != tuple(sorted(set(self.missing_context_keys))):
            raise ValueError("missing context keys must be unique and sorted")
        return self


class WorkPacketConformance(DomainModel):
    status: RequirementStatus
    reasons: tuple[WorkPacketReason, ...]

    @field_validator("reasons")
    @classmethod
    def reasons_are_canonical(
        cls, value: tuple[WorkPacketReason, ...]
    ) -> tuple[WorkPacketReason, ...]:
        if value != tuple(reason for reason in WorkPacketReason if reason in value):
            raise ValueError("work packet conformance reasons must be unique and enum ordered")
        return value


def canonical_baseline_json(baseline: Baseline) -> str:
    """Serialize an existing Baseline only when its ID tuples are canonical."""
    for label, values in (
        ("artifact_ids", baseline.artifact_ids),
        ("decision_ids", baseline.decision_ids),
    ):
        if len(values) != len(set(values)):
            raise ValueError(f"Baseline {label} must be unique")
        if values != tuple(sorted(values)):
            raise ValueError(f"Baseline {label} must be sorted before identity derivation")
    return _canonical_model_json(baseline)


def source_baseline_ref(baseline: Baseline) -> SourceBaselineRef:
    canonical = canonical_baseline_json(baseline)
    digest = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return SourceBaselineRef(
        baseline_id=baseline.id,
        project_id=baseline.project_id,
        commit=baseline.commit,
        content_digest=digest,
    )


def source_baseline_ref_matches(baseline: Baseline, ref: SourceBaselineRef) -> bool:
    try:
        return source_baseline_ref(baseline) == ref
    except ValueError:
        return False


def canonical_context_manifest_json(manifest: ContextManifest) -> str:
    return _canonical_model_json(manifest)


def digest_context_manifest(manifest: ContextManifest) -> ContentDigest:
    return (
        "sha256:"
        + hashlib.sha256(canonical_context_manifest_json(manifest).encode("utf-8")).hexdigest()
    )


def context_manifest_ref(manifest: ContextManifest) -> ContextManifestRef:
    return ContextManifestRef(
        project_id=manifest.project_id,
        slice_id=manifest.slice_definition_ref.slice_id,
        manifest_key=manifest.manifest_key,
        revision=manifest.revision,
        content_digest=digest_context_manifest(manifest),
    )


def context_manifest_ref_matches(manifest: ContextManifest, ref: ContextManifestRef) -> bool:
    return context_manifest_ref(manifest) == ref


def canonical_work_packet_json(packet: WorkPacket) -> str:
    return _canonical_model_json(packet)


def digest_work_packet(packet: WorkPacket) -> ContentDigest:
    return (
        "sha256:" + hashlib.sha256(canonical_work_packet_json(packet).encode("utf-8")).hexdigest()
    )


def work_packet_ref(packet: WorkPacket) -> WorkPacketRef:
    return WorkPacketRef(
        project_id=packet.project_id,
        slice_id=packet.slice_definition_ref.slice_id,
        packet_key=packet.packet_key,
        revision=packet.revision,
        content_digest=digest_work_packet(packet),
    )


def work_packet_ref_matches(packet: WorkPacket, ref: WorkPacketRef) -> bool:
    return work_packet_ref(packet) == ref


def protected_verification_requirement_ref(
    requirement: ProtectedVerificationRequirement,
) -> ProtectedVerificationRequirementRef:
    return ProtectedVerificationRequirementRef(
        artifact_id=requirement.artifact.id,
        artifact_content_digest=requirement.artifact.content_digest,
        required_operation=requirement.required_operation,
        requirement_digest=_digest(requirement),
    )


def material_digests(material: ContextMaterialRef) -> tuple[ContentDigest, ContentDigest]:
    if isinstance(material, ArtifactMaterialRef):
        return material.artifact.content_digest, material.provenance_digest
    return material.content_digest, material.provenance_digest


def evaluate_work_packet_identity_conflicts(
    refs: tuple[WorkPacketRef, ...],
) -> WorkPacketIdentityConflict:
    seen: dict[tuple[ProjectId, SliceId, WorkPacketKey, int], ContentDigest] = {}
    for ref in refs:
        key = (ref.project_id, ref.slice_id, ref.packet_key, ref.revision)
        digest = seen.get(key)
        if digest is not None and digest != ref.content_digest:
            return WorkPacketIdentityConflict(
                has_conflict=True, packet_key=ref.packet_key, revision=ref.revision
            )
        seen[key] = ref.content_digest
    return WorkPacketIdentityConflict(has_conflict=False, packet_key=None, revision=None)


def evaluate_context_manifest_identity_conflicts(
    refs: tuple[ContextManifestRef, ...],
) -> ContextManifestIdentityConflict:
    seen: dict[tuple[ProjectId, SliceId, ContextManifestKey, int], ContentDigest] = {}
    for ref in refs:
        key = (ref.project_id, ref.slice_id, ref.manifest_key, ref.revision)
        digest = seen.get(key)
        if digest is not None and digest != ref.content_digest:
            return ContextManifestIdentityConflict(
                has_conflict=True, manifest_key=ref.manifest_key, revision=ref.revision
            )
        seen[key] = ref.content_digest
    return ContextManifestIdentityConflict(has_conflict=False, manifest_key=None, revision=None)
