"""Immutable schema-v1 execution-workspace values.

These models describe workspace policy and evidence. None of them grants
execution, governance, or Human authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints, field_validator, model_validator

from relay_engine.agent_runtime import CredentialRef, RuntimeWorkspaceAttachment
from relay_engine.agent_runtime.models import RuntimeIdentifier
from relay_engine.domain import Artifact, CommitRef, ContentDigest, RepositoryRef
from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.role_contracts import (
    RequirementStatus,
    RoleContractRef,
    VerificationAssetPermission,
)
from relay_engine.work_packets import (
    AuthorityBasisRef,
    GovernanceProfileRef,
    PolicyBasisRef,
    ProtectedVerificationAuthorityFact,
    ProtectedVerificationRequirementRef,
    SourceBaselineRef,
    StableRequirementKey,
    WorkPacketConformance,
    WorkPacketRef,
    WorkspacePolicyRef,
)

type BoundedText = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=4096)]
type RepositoryPath = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=4096)]
type WorkspacePlanKey = StableRequirementKey

_KEY = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$", re.ASCII)


def _stable_key(value: str) -> str:
    if not _KEY.fullmatch(value):
        raise ValueError("key must be lowercase ASCII segments separated by single hyphens")
    return value


def _sorted_unique[T](values: tuple[T, ...], key: Callable[[T], str], label: str) -> None:
    keys = tuple(key(value) for value in values)
    if keys != tuple(sorted(keys)):
        raise ValueError(f"{label} must use canonical ordering")
    if len(keys) != len(set(keys)):
        raise ValueError(f"{label} must be unique")


def _json(value: DomainModel) -> str:
    normalized = type(value).model_validate(value.model_dump(mode="python"))
    return json.dumps(
        normalized.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: DomainModel) -> ContentDigest:
    return "sha256:" + hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


class ControlStrength(StrEnum):
    DETECTIVE = "DETECTIVE"
    MEDIATED = "MEDIATED"
    BOUNDARY_ENFORCED = "BOUNDARY_ENFORCED"


class WorkspaceProperty(StrEnum):
    EXACT_SOURCE_BASELINE = "EXACT_SOURCE_BASELINE"
    CLEAN_INITIAL_STATE = "CLEAN_INITIAL_STATE"
    REPOSITORY_METADATA_ISOLATED = "REPOSITORY_METADATA_ISOLATED"
    FILESYSTEM_SCOPE = "FILESYSTEM_SCOPE"
    PATH_ESCAPE_CONTROL = "PATH_ESCAPE_CONTROL"
    PROTECTED_ASSET_CONTROL = "PROTECTED_ASSET_CONTROL"
    TOOL_EXPOSURE_CONTROL = "TOOL_EXPOSURE_CONTROL"
    NETWORK_REACHABILITY_CONTROL = "NETWORK_REACHABILITY_CONTROL"
    EXTERNAL_SIDE_EFFECT_CONTROL = "EXTERNAL_SIDE_EFFECT_CONTROL"
    CREDENTIAL_EXPOSURE_CONTROL = "CREDENTIAL_EXPOSURE_CONTROL"
    RESOURCE_LIMIT_CONTROL = "RESOURCE_LIMIT_CONTROL"
    ENVIRONMENT_PROVENANCE = "ENVIRONMENT_PROVENANCE"
    DIRTY_STATE_INSPECTION = "DIRTY_STATE_INSPECTION"
    CHANGESET_EXTRACTION = "CHANGESET_EXTRACTION"
    RETENTION_CONTROL = "RETENTION_CONTROL"
    TEARDOWN_CONTROL = "TEARDOWN_CONTROL"
    CONTROL_CONTINUITY = "CONTROL_CONTINUITY"


class FilesystemAccess(StrEnum):
    DENY = "DENY"
    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"


class RepositoryMetadataAccess(StrEnum):
    DENY = "DENY"
    READ_ONLY = "READ_ONLY"
    LOCAL_MUTATION = "LOCAL_MUTATION"


class ToolDecision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class ShellMode(StrEnum):
    DENY = "DENY"
    UNRESTRICTED_WITHIN_DECLARED_BOUNDARY = "UNRESTRICTED_WITHIN_DECLARED_BOUNDARY"


class NetworkMode(StrEnum):
    DENY_ALL = "DENY_ALL"
    ALLOWLIST = "ALLOWLIST"
    UNRESTRICTED = "UNRESTRICTED"


class ExternalSideEffectMode(StrEnum):
    DENY_MUTATING_EFFECTS = "DENY_MUTATING_EFFECTS"
    ALLOW_EXPLICIT_EFFECTS = "ALLOW_EXPLICIT_EFFECTS"
    UNRESTRICTED = "UNRESTRICTED"


class CredentialExposureMode(StrEnum):
    NONE = "NONE"
    ENVIRONMENT = "ENVIRONMENT"
    FILE = "FILE"
    PROVIDER_NATIVE = "PROVIDER_NATIVE"


class WorkspaceResourceDimension(StrEnum):
    MEMORY_BYTES = "MEMORY_BYTES"
    DISK_BYTES = "DISK_BYTES"
    PROCESS_COUNT = "PROCESS_COUNT"
    CPU_SECONDS = "CPU_SECONDS"
    OPEN_FILES = "OPEN_FILES"


class WorkspacePathControlCapability(StrEnum):
    CANONICAL_REPOSITORY_PATHS = "CANONICAL_REPOSITORY_PATHS"
    SYMLINK_ESCAPE_DETECTION = "SYMLINK_ESCAPE_DETECTION"
    SYMLINK_ESCAPE_PREVENTION = "SYMLINK_ESCAPE_PREVENTION"
    HARDLINK_ESCAPE_DETECTION = "HARDLINK_ESCAPE_DETECTION"
    HARDLINK_ESCAPE_PREVENTION = "HARDLINK_ESCAPE_PREVENTION"
    MOUNT_OR_REPARSE_ESCAPE_DETECTION = "MOUNT_OR_REPARSE_ESCAPE_DETECTION"
    MOUNT_OR_REPARSE_ESCAPE_PREVENTION = "MOUNT_OR_REPARSE_ESCAPE_PREVENTION"


class WorkspaceBackendKind(StrEnum):
    LOCAL_CLONE = "LOCAL_CLONE"
    LOCAL_WORKTREE = "LOCAL_WORKTREE"
    CONTAINER = "CONTAINER"
    REMOTE_ISOLATED = "REMOTE_ISOLATED"
    OTHER = "OTHER"


class WorkspaceBoundaryClass(StrEnum):
    SAME_USER_NO_SECURITY_BOUNDARY = "SAME_USER_NO_SECURITY_BOUNDARY"
    MEDIATED_PROCESS_BOUNDARY = "MEDIATED_PROCESS_BOUNDARY"
    CONTAINER_BOUNDARY = "CONTAINER_BOUNDARY"
    REMOTE_ISOLATED_BOUNDARY = "REMOTE_ISOLATED_BOUNDARY"


class WorkspaceEntryKind(StrEnum):
    REGULAR_FILE = "REGULAR_FILE"
    SYMLINK = "SYMLINK"


class WorkspaceTerminalDisposition(StrEnum):
    DELETED = "DELETED"
    RETAINED_BY_POLICY = "RETAINED_BY_POLICY"
    RETAINED_PENDING_RELEASE = "RETAINED_PENDING_RELEASE"
    TEARDOWN_FAILED = "TEARDOWN_FAILED"
    UNKNOWN = "UNKNOWN"


class WorkspaceRetentionMode(StrEnum):
    DELETE_ON_TERMINAL = "DELETE_ON_TERMINAL"
    RETAIN_ON_FAILURE = "RETAIN_ON_FAILURE"
    RETAIN_UNTIL_EXPLICIT_RELEASE = "RETAIN_UNTIL_EXPLICIT_RELEASE"


class WorkspaceReason(StrEnum):
    WORK_PACKET_REF_MISMATCH = "WORK_PACKET_REF_MISMATCH"
    WORK_PACKET_CONFORMANCE_REQUIRED = "WORK_PACKET_CONFORMANCE_REQUIRED"
    WORKSPACE_POLICY_REQUIRED = "WORKSPACE_POLICY_REQUIRED"
    WORKSPACE_POLICY_REF_MISMATCH = "WORKSPACE_POLICY_REF_MISMATCH"
    WORKSPACE_POLICY_STALE = "WORKSPACE_POLICY_STALE"
    WORKSPACE_POLICY_CONFLICT = "WORKSPACE_POLICY_CONFLICT"
    GOVERNANCE_PROFILE_MISMATCH = "GOVERNANCE_PROFILE_MISMATCH"
    ROLE_CONTRACT_REF_MISMATCH = "ROLE_CONTRACT_REF_MISMATCH"
    ROLE_PERMISSION_INSUFFICIENT = "ROLE_PERMISSION_INSUFFICIENT"
    REQUIRED_WORKSPACE_PROPERTY_UNKNOWN = "REQUIRED_WORKSPACE_PROPERTY_UNKNOWN"
    REQUIRED_WORKSPACE_PROPERTY_UNSUPPORTED = "REQUIRED_WORKSPACE_PROPERTY_UNSUPPORTED"
    REQUIRED_WORKSPACE_PROPERTY_INDETERMINATE = "REQUIRED_WORKSPACE_PROPERTY_INDETERMINATE"
    REQUIRED_WORKSPACE_PROPERTY_UNSATISFIED = "REQUIRED_WORKSPACE_PROPERTY_UNSATISFIED"
    CONTROL_STRENGTH_INSUFFICIENT = "CONTROL_STRENGTH_INSUFFICIENT"
    PROVIDER_REF_MISMATCH = "PROVIDER_REF_MISMATCH"
    PROVIDER_DESCRIPTOR_UNAVAILABLE = "PROVIDER_DESCRIPTOR_UNAVAILABLE"
    PROVIDER_CAPABILITY_INSUFFICIENT = "PROVIDER_CAPABILITY_INSUFFICIENT"
    PROVIDER_BOUNDARY_INSUFFICIENT = "PROVIDER_BOUNDARY_INSUFFICIENT"
    SOURCE_BASELINE_MISMATCH = "SOURCE_BASELINE_MISMATCH"
    INITIAL_STATE_DIRTY = "INITIAL_STATE_DIRTY"
    REPOSITORY_METADATA_NOT_ISOLATED = "REPOSITORY_METADATA_NOT_ISOLATED"
    FILESYSTEM_SCOPE_VIOLATION = "FILESYSTEM_SCOPE_VIOLATION"
    PATH_ESCAPE_UNCONTROLLED = "PATH_ESCAPE_UNCONTROLLED"
    PROTECTED_ASSET_PERMISSION_REQUIRED = "PROTECTED_ASSET_PERMISSION_REQUIRED"
    PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED = "PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED"
    PROTECTED_ASSET_MUTATED = "PROTECTED_ASSET_MUTATED"
    TOOL_NOT_ALLOWED = "TOOL_NOT_ALLOWED"
    SHELL_POLICY_UNSUPPORTED = "SHELL_POLICY_UNSUPPORTED"
    NETWORK_POLICY_UNSUPPORTED = "NETWORK_POLICY_UNSUPPORTED"
    NETWORK_POLICY_VIOLATION = "NETWORK_POLICY_VIOLATION"
    EXTERNAL_SIDE_EFFECT_POLICY_UNSUPPORTED = "EXTERNAL_SIDE_EFFECT_POLICY_UNSUPPORTED"
    EXTERNAL_SIDE_EFFECT_VIOLATION = "EXTERNAL_SIDE_EFFECT_VIOLATION"
    CREDENTIAL_NOT_DECLARED = "CREDENTIAL_NOT_DECLARED"
    CREDENTIAL_EXPOSURE_UNSUPPORTED = "CREDENTIAL_EXPOSURE_UNSUPPORTED"
    UNEXPECTED_CREDENTIAL_EXPOSURE = "UNEXPECTED_CREDENTIAL_EXPOSURE"
    RESOURCE_LIMIT_UNSUPPORTED = "RESOURCE_LIMIT_UNSUPPORTED"
    RESOURCE_LIMIT_MISMATCH = "RESOURCE_LIMIT_MISMATCH"
    ENVIRONMENT_PROVENANCE_INSUFFICIENT = "ENVIRONMENT_PROVENANCE_INSUFFICIENT"
    CONTROL_CONTINUITY_INDETERMINATE = "CONTROL_CONTINUITY_INDETERMINATE"
    CHANGESET_UNAVAILABLE = "CHANGESET_UNAVAILABLE"
    CHANGE_OUT_OF_SCOPE = "CHANGE_OUT_OF_SCOPE"
    RETENTION_POLICY_VIOLATION = "RETENTION_POLICY_VIOLATION"
    TEARDOWN_INDETERMINATE = "TEARDOWN_INDETERMINATE"
    TEARDOWN_FAILED = "TEARDOWN_FAILED"
    EVIDENCE_SUBJECT_MISMATCH = "EVIDENCE_SUBJECT_MISMATCH"
    PROPERTY_EVIDENCE_MISSING = "PROPERTY_EVIDENCE_MISSING"
    PROPERTY_EVIDENCE_UNEXPECTED = "PROPERTY_EVIDENCE_UNEXPECTED"
    PROTECTED_ASSET_OBSERVATION_MISSING = "PROTECTED_ASSET_OBSERVATION_MISSING"
    PROTECTED_ASSET_OBSERVATION_MISMATCH = "PROTECTED_ASSET_OBSERVATION_MISMATCH"


class WorkspacePropertyRequirement(DomainModel):
    key: StableRequirementKey
    property: WorkspaceProperty
    minimum_strength: ControlStrength

    @field_validator("key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _stable_key(value)


class RepositoryPathPrefix(DomainModel):
    value: RepositoryPath

    @field_validator("value")
    @classmethod
    def path_is_canonical(cls, value: str) -> str:
        return validate_repository_path(value, allow_root=True)


def validate_repository_path(value: str, *, allow_root: bool = False) -> str:
    if value == "." and allow_root:
        return value
    if (
        value.startswith("/")
        or "\\" in value
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
        or any(part in {"", ".", ".."} for part in value.split("/"))
        or re.match(r"^[A-Za-z]:", value)
    ):
        raise ValueError("path must be canonical repository-relative POSIX path")
    return value


class FilesystemPolicy(DomainModel):
    default_access: FilesystemAccess
    writable_prefixes: tuple[RepositoryPathPrefix, ...]
    denied_prefixes: tuple[RepositoryPathPrefix, ...]

    @model_validator(mode="after")
    def canonical_prefixes(self) -> FilesystemPolicy:
        for name, values in (
            ("writable_prefixes", self.writable_prefixes),
            ("denied_prefixes", self.denied_prefixes),
        ):
            _sorted_unique(values, lambda item: item.value, name)
        if set(item.value for item in self.writable_prefixes) & set(
            item.value for item in self.denied_prefixes
        ):
            raise ValueError("a path prefix cannot be both writable and denied")
        return self


class RepositoryMetadataPolicy(DomainModel):
    access: RepositoryMetadataAccess


class WorkspaceToolRef(DomainModel):
    tool_key: StableRequirementKey
    tool_definition_digest: ContentDigest

    @field_validator("tool_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _stable_key(value)


class ToolRule(DomainModel):
    tool_ref: WorkspaceToolRef
    decision: ToolDecision


class ToolPolicy(DomainModel):
    default_decision: ToolDecision
    rules: tuple[ToolRule, ...]

    @model_validator(mode="after")
    def rules_are_canonical(self) -> ToolPolicy:
        _sorted_unique(self.rules, lambda item: item.tool_ref.tool_key, "tool rules")
        return self


class ShellPolicy(DomainModel):
    mode: ShellMode


class NetworkEndpoint(DomainModel):
    scheme: BoundedText
    host: BoundedText
    port: int = Field(strict=True, ge=1, le=65535)

    @field_validator("scheme")
    @classmethod
    def scheme_is_canonical(cls, value: str) -> str:
        if (
            not value.isascii()
            or value != value.lower()
            or not re.fullmatch(r"[a-z][a-z0-9+.-]*", value)
        ):
            raise ValueError("scheme must be lowercase ASCII URI scheme")
        return value

    @field_validator("host")
    @classmethod
    def host_is_canonical(cls, value: str) -> str:
        if (
            not value.isascii()
            or value != value.lower()
            or any(c.isspace() for c in value)
            or "*" in value
            or value.endswith(".")
        ):
            raise ValueError("host must be exact lowercase ASCII without wildcard or trailing dot")
        return value


class NetworkPolicy(DomainModel):
    mode: NetworkMode
    allowed_endpoints: tuple[NetworkEndpoint, ...]

    @model_validator(mode="after")
    def endpoints_match_mode(self) -> NetworkPolicy:
        if self.mode is NetworkMode.ALLOWLIST:
            if not self.allowed_endpoints:
                raise ValueError("ALLOWLIST requires at least one endpoint")
            endpoint_keys = tuple(
                (item.scheme, item.host, item.port) for item in self.allowed_endpoints
            )
            if endpoint_keys != tuple(sorted(endpoint_keys)) or len(endpoint_keys) != len(
                set(endpoint_keys)
            ):
                raise ValueError("allowed_endpoints must be unique and canonically ordered")
        elif self.allowed_endpoints:
            raise ValueError("only ALLOWLIST may contain endpoints")
        return self


class ExternalEffectRef(DomainModel):
    effect_key: StableRequirementKey
    definition_digest: ContentDigest

    @field_validator("effect_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _stable_key(value)


class ExternalSideEffectPolicy(DomainModel):
    mode: ExternalSideEffectMode
    allowed_effects: tuple[ExternalEffectRef, ...]

    @model_validator(mode="after")
    def effects_match_mode(self) -> ExternalSideEffectPolicy:
        if self.mode is ExternalSideEffectMode.ALLOW_EXPLICIT_EFFECTS:
            if not self.allowed_effects:
                raise ValueError("ALLOW_EXPLICIT_EFFECTS requires at least one effect")
            _sorted_unique(self.allowed_effects, lambda item: item.effect_key, "allowed_effects")
        elif self.allowed_effects:
            raise ValueError("only ALLOW_EXPLICIT_EFFECTS may contain effects")
        return self


class WorkspaceCredentialGrant(DomainModel):
    credential_ref: CredentialRef
    exposure_mode: CredentialExposureMode
    exposure_key: BoundedText | None

    @model_validator(mode="after")
    def key_matches_mode(self) -> WorkspaceCredentialGrant:
        if (self.exposure_mode is CredentialExposureMode.NONE) != (self.exposure_key is None):
            raise ValueError("NONE requires no exposure key; exposed modes require one")
        if self.exposure_key is not None:
            require_nonblank(self.exposure_key)
        return self


class WorkspaceCredentialPolicy(DomainModel):
    grants: tuple[WorkspaceCredentialGrant, ...]

    @model_validator(mode="after")
    def grants_are_canonical(self) -> WorkspaceCredentialPolicy:
        keys = tuple(item.credential_ref.credential_id for item in self.grants)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("credential grants must be unique and sorted by credential_id")
        return self


class WorkspaceResourceLimits(DomainModel):
    max_memory_bytes: int | None = Field(default=None, strict=True, ge=1)
    max_disk_bytes: int | None = Field(default=None, strict=True, ge=1)
    max_processes: int | None = Field(default=None, strict=True, ge=1)
    max_cpu_seconds: int | None = Field(default=None, strict=True, ge=1)
    max_open_files: int | None = Field(default=None, strict=True, ge=1)


class WorkspaceRetentionPolicy(DomainModel):
    mode: WorkspaceRetentionMode
    max_retention_seconds: int | None = Field(default=None, strict=True, ge=1)


class ProviderInjectedFileRequirement(DomainModel):
    path: RepositoryPath
    provider_file_key: StableRequirementKey
    content_digest: ContentDigest

    @field_validator("path")
    @classmethod
    def path_is_canonical(cls, value: str) -> str:
        return validate_repository_path(value)

    @field_validator("provider_file_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _stable_key(value)


class ProviderInjectedFileCapability(DomainModel):
    file_key: StableRequirementKey
    content_digest: ContentDigest

    @field_validator("file_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _stable_key(value)


class WorkspacePolicyDefinition(DomainModel):
    policy_key: StableRequirementKey
    policy_basis_ref: PolicyBasisRef
    governance_profile_ref: GovernanceProfileRef | None
    property_requirements: tuple[WorkspacePropertyRequirement, ...]
    filesystem_policy: FilesystemPolicy
    repository_metadata_policy: RepositoryMetadataPolicy
    tool_policy: ToolPolicy
    shell_policy: ShellPolicy
    network_policy: NetworkPolicy
    external_side_effect_policy: ExternalSideEffectPolicy
    credential_policy: WorkspaceCredentialPolicy
    resource_limits: WorkspaceResourceLimits
    retention_policy: WorkspaceRetentionPolicy
    provider_injected_files: tuple[ProviderInjectedFileRequirement, ...]

    @field_validator("policy_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _stable_key(value)

    @model_validator(mode="after")
    def nested_values_are_canonical(self) -> WorkspacePolicyDefinition:
        _sorted_unique(self.property_requirements, lambda item: item.key, "property_requirements")
        injected_paths = tuple(item.path for item in self.provider_injected_files)
        injected_keys = tuple(item.provider_file_key for item in self.provider_injected_files)
        if injected_paths != tuple(sorted(injected_paths)) or len(injected_paths) != len(
            set(injected_paths)
        ):
            raise ValueError("provider injected files must be unique and sorted by path")
        if len(injected_keys) != len(set(injected_keys)):
            raise ValueError("provider file keys must be unique within policy")
        return self


class WorkspaceProviderPropertyCapability(DomainModel):
    property: WorkspaceProperty
    maximum_strength: ControlStrength


class WorkspaceProviderDescriptor(DomainModel):
    provider_id: RuntimeIdentifier
    provider_version: RuntimeIdentifier
    backend_kind: WorkspaceBackendKind
    boundary_class: WorkspaceBoundaryClass
    property_capabilities: tuple[WorkspaceProviderPropertyCapability, ...]
    supported_shell_modes: tuple[ShellMode, ...]
    supported_network_modes: tuple[NetworkMode, ...]
    supported_external_side_effect_modes: tuple[ExternalSideEffectMode, ...]
    supported_credential_exposure_modes: tuple[CredentialExposureMode, ...]
    supported_resource_dimensions: tuple[WorkspaceResourceDimension, ...]
    supported_repository_metadata_modes: tuple[RepositoryMetadataAccess, ...]
    path_control_capabilities: tuple[WorkspacePathControlCapability, ...]
    provider_injected_file_capabilities: tuple[ProviderInjectedFileCapability, ...]

    @model_validator(mode="after")
    def capabilities_are_canonical(self) -> WorkspaceProviderDescriptor:
        properties = tuple(item.property for item in self.property_capabilities)
        if properties != tuple(item for item in WorkspaceProperty if item in properties) or len(
            properties
        ) != len(set(properties)):
            raise ValueError("property capabilities must be unique and enum ordered")
        _enum_values_are_canonical(self.supported_shell_modes, ShellMode, "supported_shell_modes")
        _enum_values_are_canonical(
            self.supported_network_modes, NetworkMode, "supported_network_modes"
        )
        _enum_values_are_canonical(
            self.supported_external_side_effect_modes,
            ExternalSideEffectMode,
            "supported_external_side_effect_modes",
        )
        _enum_values_are_canonical(
            self.supported_credential_exposure_modes,
            CredentialExposureMode,
            "supported_credential_exposure_modes",
        )
        _enum_values_are_canonical(
            self.supported_resource_dimensions,
            WorkspaceResourceDimension,
            "supported_resource_dimensions",
        )
        _enum_values_are_canonical(
            self.supported_repository_metadata_modes,
            RepositoryMetadataAccess,
            "supported_repository_metadata_modes",
        )
        _enum_values_are_canonical(
            self.path_control_capabilities,
            WorkspacePathControlCapability,
            "path_control_capabilities",
        )
        _sorted_unique(
            self.provider_injected_file_capabilities,
            lambda item: item.file_key,
            "provider_injected_file_capabilities",
        )
        if self.backend_kind is WorkspaceBackendKind.LOCAL_CLONE:
            if self.boundary_class is not WorkspaceBoundaryClass.SAME_USER_NO_SECURITY_BOUNDARY:
                raise ValueError("LOCAL_CLONE must declare SAME_USER_NO_SECURITY_BOUNDARY")
            for capability in self.property_capabilities:
                if (
                    capability.property
                    in {
                        WorkspaceProperty.FILESYSTEM_SCOPE,
                        WorkspaceProperty.PATH_ESCAPE_CONTROL,
                        WorkspaceProperty.PROTECTED_ASSET_CONTROL,
                        WorkspaceProperty.NETWORK_REACHABILITY_CONTROL,
                        WorkspaceProperty.EXTERNAL_SIDE_EFFECT_CONTROL,
                        WorkspaceProperty.CREDENTIAL_EXPOSURE_CONTROL,
                        WorkspaceProperty.RESOURCE_LIMIT_CONTROL,
                    }
                    and capability.maximum_strength is ControlStrength.BOUNDARY_ENFORCED
                ):
                    raise ValueError(
                        "same-user LOCAL_CLONE cannot claim boundary-enforced isolation"
                    )
        return self


class WorkspaceProviderRef(DomainModel):
    provider_id: RuntimeIdentifier
    provider_version: RuntimeIdentifier
    descriptor_digest: ContentDigest


class ProtectedAssetWorkspaceBinding(DomainModel):
    requirement_ref: ProtectedVerificationRequirementRef
    artifact: Artifact
    required_operation: VerificationAssetPermission
    separate_authority_ref: AuthorityBasisRef | None
    workspace_path: RepositoryPath
    physical_access: FilesystemAccess
    control_property_key: StableRequirementKey

    @field_validator("workspace_path")
    @classmethod
    def path_is_canonical(cls, value: str) -> str:
        return validate_repository_path(value)

    @field_validator("control_property_key")
    @classmethod
    def control_key_is_stable(cls, value: str) -> str:
        return _stable_key(value)

    @model_validator(mode="after")
    def artifact_matches_ref(self) -> ProtectedAssetWorkspaceBinding:
        if (
            self.requirement_ref.artifact_id,
            self.requirement_ref.artifact_content_digest,
            self.requirement_ref.required_operation,
        ) != (self.artifact.id, self.artifact.content_digest, self.required_operation):
            raise ValueError("protected binding artifact and requirement ref must match")
        return self


class WorkspacePlan(DomainModel):
    plan_key: StableRequirementKey
    revision: int = Field(ge=1)
    work_packet_ref: WorkPacketRef
    source_baseline_ref: SourceBaselineRef
    role_contract_ref: RoleContractRef
    workspace_policy_ref: WorkspacePolicyRef
    governance_profile_ref: GovernanceProfileRef | None
    provider_ref: WorkspaceProviderRef
    packet_required_property_keys: tuple[StableRequirementKey, ...]
    property_requirements: tuple[WorkspacePropertyRequirement, ...]
    protected_asset_bindings: tuple[ProtectedAssetWorkspaceBinding, ...]
    workspace_credential_grants: tuple[WorkspaceCredentialGrant, ...]
    provider_injected_files: tuple[ProviderInjectedFileRequirement, ...]
    filesystem_policy: FilesystemPolicy
    repository_metadata_policy: RepositoryMetadataPolicy
    tool_policy: ToolPolicy
    shell_policy: ShellPolicy
    network_policy: NetworkPolicy
    external_side_effect_policy: ExternalSideEffectPolicy
    resource_limits: WorkspaceResourceLimits
    retention_policy: WorkspaceRetentionPolicy

    @field_validator("plan_key", "packet_required_property_keys")
    @classmethod
    def stable_values(cls, value: str | tuple[str, ...]) -> str | tuple[str, ...]:
        if isinstance(value, tuple):
            for item in value:
                _stable_key(item)
            if value != tuple(sorted(value)) or len(value) != len(set(value)):
                raise ValueError("packet property keys must be unique and sorted")
            return value
        return _stable_key(value)

    @model_validator(mode="after")
    def plan_collections_are_canonical(self) -> WorkspacePlan:
        _sorted_unique(self.property_requirements, lambda item: item.key, "property_requirements")
        _sorted_unique(
            self.workspace_credential_grants,
            lambda item: item.credential_ref.credential_id,
            "workspace_credential_grants",
        )
        _sorted_unique(
            self.provider_injected_files, lambda item: item.path, "provider_injected_files"
        )
        bindings = tuple(
            (
                item.artifact.path,
                item.requirement_ref.artifact_id,
                item.requirement_ref.artifact_content_digest,
                list(VerificationAssetPermission).index(item.required_operation),
                item.requirement_ref.requirement_digest,
            )
            for item in self.protected_asset_bindings
        )
        if bindings != tuple(sorted(bindings)) or len(bindings) != len(set(bindings)):
            raise ValueError("protected bindings must be unique and canonically ordered")
        return self


class WorkspacePlanRef(DomainModel):
    work_packet_ref: WorkPacketRef
    plan_key: StableRequirementKey
    revision: int = Field(ge=1)
    content_digest: ContentDigest

    @field_validator("plan_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _stable_key(value)


class WorkspaceEvidenceSubject(DomainModel):
    plan_ref: WorkspacePlanRef
    instance_ref: WorkspaceInstanceRef
    provider_ref: WorkspaceProviderRef

    @model_validator(mode="after")
    def refs_match(self) -> WorkspaceEvidenceSubject:
        if (
            self.instance_ref.plan_ref != self.plan_ref
            or self.instance_ref.provider_ref != self.provider_ref
        ):
            raise ValueError("evidence subject references must match the exact instance")
        return self


class WorkspaceInstanceRef(DomainModel):
    workspace_id: RuntimeIdentifier
    plan_ref: WorkspacePlanRef
    provider_ref: WorkspaceProviderRef
    repository: RepositoryRef
    source_commit: CommitRef
    root: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=2048)]

    @field_validator("root")
    @classmethod
    def root_is_absolute(cls, value: str) -> str:
        if (
            not value.startswith("/")
            or "\\" in value
            or any(part in {".", ".."} for part in value.split("/"))
        ):
            raise ValueError("root must be a canonical absolute POSIX path")
        return value

    @model_validator(mode="after")
    def commit_matches_repository(self) -> WorkspaceInstanceRef:
        if self.source_commit.repository != self.repository:
            raise ValueError("source commit repository must match instance repository")
        return self


class WorkspacePropertyEvidence(DomainModel):
    subject: WorkspaceEvidenceSubject
    property_key: StableRequirementKey
    property: WorkspaceProperty
    established_strength: ControlStrength
    status: RequirementStatus
    evidence_payload_digest: ContentDigest

    @field_validator("property_key")
    @classmethod
    def key_is_stable(cls, value: str) -> str:
        return _stable_key(value)


class WorkspaceEntryState(DomainModel):
    kind: WorkspaceEntryKind
    content_digest: ContentDigest | None
    symlink_target_digest: ContentDigest | None
    executable: bool | None

    @model_validator(mode="after")
    def fields_match_kind(self) -> WorkspaceEntryState:
        if self.kind is WorkspaceEntryKind.REGULAR_FILE:
            if (
                self.content_digest is None
                or self.symlink_target_digest is not None
                or self.executable is None
            ):
                raise ValueError("regular files require content digest and executable state only")
        elif (
            self.content_digest is not None
            or self.symlink_target_digest is None
            or self.executable is not None
        ):
            raise ValueError("symlinks require target digest and no file mode/content fields")
        return self


class ProtectedAssetObservation(DomainModel):
    requirement_ref: ProtectedVerificationRequirementRef
    workspace_path: RepositoryPath
    state: WorkspaceEntryState | None

    @field_validator("workspace_path")
    @classmethod
    def path_is_canonical(cls, value: str) -> str:
        return validate_repository_path(value)


class WorkspaceInspection(DomainModel):
    instance_ref: WorkspaceInstanceRef
    inspected_at: BoundedText
    head_commit: CommitRef
    tracked_changes: tuple[RepositoryPath, ...]
    untracked_paths: tuple[RepositoryPath, ...]
    provider_injected_paths: tuple[RepositoryPath, ...]
    protected_asset_observations: tuple[ProtectedAssetObservation, ...]
    property_evidence: tuple[WorkspacePropertyEvidence, ...]

    @model_validator(mode="after")
    def lists_are_canonical(self) -> WorkspaceInspection:
        for name in ("tracked_changes", "untracked_paths", "provider_injected_paths"):
            values = getattr(self, name)
            if values != tuple(sorted(values)) or len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique and sorted")
        observation_keys = tuple(
            (
                item.requirement_ref.artifact_id,
                item.requirement_ref.artifact_content_digest,
                list(VerificationAssetPermission).index(item.requirement_ref.required_operation),
                item.requirement_ref.requirement_digest,
                item.workspace_path,
            )
            for item in self.protected_asset_observations
        )
        if observation_keys != tuple(sorted(observation_keys)) or len(
            {item[0:4] for item in observation_keys}
        ) != len(observation_keys):
            raise ValueError("protected observations must be unique and canonically ordered")
        evidence_keys = tuple(item.property_key for item in self.property_evidence)
        if evidence_keys != tuple(sorted(evidence_keys)) or len(evidence_keys) != len(
            set(evidence_keys)
        ):
            raise ValueError(
                "inspection property evidence must be unique and sorted by property_key"
            )
        return self


class WorkspaceChangeEntry(DomainModel):
    path: RepositoryPath
    before: WorkspaceEntryState | None
    after: WorkspaceEntryState | None

    @field_validator("path")
    @classmethod
    def path_is_canonical(cls, value: str) -> str:
        return validate_repository_path(value)

    @model_validator(mode="after")
    def states_differ(self) -> WorkspaceChangeEntry:
        if self.before is None and self.after is None or self.before == self.after:
            raise ValueError("change entry must describe an exact non-no-op transition")
        return self


class WorkspaceChangeManifest(DomainModel):
    instance_ref: WorkspaceInstanceRef
    source_commit: CommitRef
    entries: tuple[WorkspaceChangeEntry, ...]

    @model_validator(mode="after")
    def entries_are_canonical(self) -> WorkspaceChangeManifest:
        if self.source_commit != self.instance_ref.source_commit:
            raise ValueError("manifest source commit must match exact instance")
        _sorted_unique(self.entries, lambda item: item.path, "change entries")
        return self


class WorkspaceChangeManifestRef(DomainModel):
    instance_ref: WorkspaceInstanceRef
    content_digest: ContentDigest


class WorkspaceEnvironmentProvenance(DomainModel):
    subject: WorkspaceEvidenceSubject
    boundary_class: WorkspaceBoundaryClass
    backend_kind: WorkspaceBackendKind
    platform_key: StableRequirementKey
    platform_version: BoundedText
    image_digest: ContentDigest | None
    environment_payload_digest: ContentDigest


class WorkspaceCredentialEvidence(DomainModel):
    subject: WorkspaceEvidenceSubject
    credential_ref: CredentialRef
    exposure_mode: CredentialExposureMode
    status: RequirementStatus
    revoked_or_removed: RequirementStatus | None


class WorkspaceResourceEvidence(DomainModel):
    subject: WorkspaceEvidenceSubject
    memory_limit_bytes: int | None = Field(default=None, strict=True, ge=1)
    disk_limit_bytes: int | None = Field(default=None, strict=True, ge=1)
    process_limit: int | None = Field(default=None, strict=True, ge=1)
    cpu_seconds_limit: int | None = Field(default=None, strict=True, ge=1)
    open_files_limit: int | None = Field(default=None, strict=True, ge=1)
    status: RequirementStatus
    evidence_payload_digest: ContentDigest


class WorkspaceControlContinuityEvidence(DomainModel):
    subject: WorkspaceEvidenceSubject
    start_evidence_digest: ContentDigest
    terminal_evidence_digest: ContentDigest
    status: RequirementStatus


class WorkspaceTeardownEvidence(DomainModel):
    subject: WorkspaceEvidenceSubject
    disposition: WorkspaceTerminalDisposition
    credential_cleanup_status: RequirementStatus
    workspace_absence_status: RequirementStatus
    retained_until: BoundedText | None
    evidence_payload_digest: ContentDigest


class WorkPacketConformanceFact(DomainModel):
    evaluated_work_packet_ref: WorkPacketRef
    conformance: WorkPacketConformance


class WorkspacePolicyFact(DomainModel):
    evaluated_ref: WorkspacePolicyRef
    status: RequirementStatus


class RoleContractFact(DomainModel):
    evaluated_ref: RoleContractRef
    status: RequirementStatus


class WorkspaceProviderDescriptorFact(DomainModel):
    evaluated_ref: WorkspaceProviderRef
    status: RequirementStatus


class WorkspacePreflight(DomainModel):
    status: RequirementStatus
    reasons: tuple[WorkspaceReason, ...]
    unsupported_property_keys: tuple[StableRequirementKey, ...]


class WorkspacePlanResolution(DomainModel):
    status: RequirementStatus
    reasons: tuple[WorkspaceReason, ...]
    plan: WorkspacePlan | None

    @model_validator(mode="after")
    def plan_matches_status(self) -> WorkspacePlanResolution:
        if (self.status is RequirementStatus.SATISFIED) != (self.plan is not None):
            raise ValueError("only SATISFIED plan resolution carries a plan")
        return self


class WorkspaceProvisionResult(DomainModel):
    instance_ref: WorkspaceInstanceRef
    runtime_attachment: RuntimeWorkspaceAttachment
    environment_provenance: WorkspaceEnvironmentProvenance
    initial_inspection: WorkspaceInspection
    property_evidence: tuple[WorkspacePropertyEvidence, ...]

    @model_validator(mode="after")
    def attachment_and_inspection_match(self) -> WorkspaceProvisionResult:
        if self.initial_inspection.instance_ref != self.instance_ref:
            raise ValueError("initial inspection must refer to provisioned instance")
        if (
            self.runtime_attachment.workspace_id != self.instance_ref.workspace_id
            or self.runtime_attachment.root != self.instance_ref.root
            or self.runtime_attachment.repository != self.instance_ref.repository
            or self.runtime_attachment.source_commit != self.instance_ref.source_commit
        ):
            raise ValueError("runtime attachment must derive from exact instance")
        return self


class WorkspaceConformance(DomainModel):
    status: RequirementStatus
    reasons: tuple[WorkspaceReason, ...]
    unsatisfied_property_keys: tuple[StableRequirementKey, ...]
    indeterminate_property_keys: tuple[StableRequirementKey, ...]


class WorkspaceConformanceFacts(DomainModel):
    evaluated_plan_ref: WorkspacePlanRef
    evaluated_instance_ref: WorkspaceInstanceRef
    evaluated_provider_ref: WorkspaceProviderRef
    work_packet_conformance_fact: WorkPacketConformanceFact
    workspace_policy_fact: WorkspacePolicyFact
    role_contract_fact: RoleContractFact
    provider_descriptor_fact: WorkspaceProviderDescriptorFact
    protected_authority_facts: tuple[ProtectedVerificationAuthorityFact, ...]
    initial_inspection: WorkspaceInspection
    property_evidence: tuple[WorkspacePropertyEvidence, ...]
    credential_evidence: tuple[WorkspaceCredentialEvidence, ...]
    resource_evidence: WorkspaceResourceEvidence | None
    environment_provenance: WorkspaceEnvironmentProvenance
    terminal_inspection: WorkspaceInspection | None
    change_manifest: WorkspaceChangeManifest | None
    continuity_evidence: WorkspaceControlContinuityEvidence | None
    teardown_evidence: WorkspaceTeardownEvidence | None

    @model_validator(mode="after")
    def evidence_populations_are_canonical(self) -> WorkspaceConformanceFacts:
        keys = tuple(item.property_key for item in self.property_evidence)
        if len(keys) != len(set(keys)):
            raise ValueError("property evidence keys must be unique")
        credentials = tuple(item.credential_ref.credential_id for item in self.credential_evidence)
        if credentials != tuple(sorted(credentials)) or len(credentials) != len(set(credentials)):
            raise ValueError("credential evidence must be unique and sorted by credential_id")
        return self


def workspace_plan_ref(plan: WorkspacePlan) -> WorkspacePlanRef:
    return WorkspacePlanRef(
        work_packet_ref=plan.work_packet_ref,
        plan_key=plan.plan_key,
        revision=plan.revision,
        content_digest=_digest(plan),
    )


def workspace_change_manifest_ref(manifest: WorkspaceChangeManifest) -> WorkspaceChangeManifestRef:
    return WorkspaceChangeManifestRef(
        instance_ref=manifest.instance_ref, content_digest=_digest(manifest)
    )


def digest_workspace_change_manifest(manifest: WorkspaceChangeManifest) -> ContentDigest:
    return _digest(manifest)


WorkspaceEvidenceSubject.model_rebuild()
WorkspacePlan.model_rebuild()


def _enum_values_are_canonical[T: StrEnum](
    values: tuple[T, ...], enum_type: type[T], label: str
) -> None:
    if values != tuple(item for item in enum_type if item in values) or len(values) != len(
        set(values)
    ):
        raise ValueError(f"{label} must be unique and enum ordered")


__all__ = [
    "BoundedText",
    "ControlStrength",
    "CredentialExposureMode",
    "ExternalEffectRef",
    "ExternalSideEffectMode",
    "ExternalSideEffectPolicy",
    "FilesystemAccess",
    "FilesystemPolicy",
    "NetworkEndpoint",
    "NetworkMode",
    "NetworkPolicy",
    "ProviderInjectedFileCapability",
    "ProviderInjectedFileRequirement",
    "ProtectedAssetObservation",
    "ProtectedAssetWorkspaceBinding",
    "RepositoryMetadataAccess",
    "RepositoryMetadataPolicy",
    "RepositoryPath",
    "RepositoryPathPrefix",
    "RoleContractFact",
    "ShellMode",
    "ShellPolicy",
    "ToolDecision",
    "ToolPolicy",
    "ToolRule",
    "WorkspaceBackendKind",
    "WorkspaceBoundaryClass",
    "WorkspaceChangeEntry",
    "WorkspaceChangeManifest",
    "WorkspaceChangeManifestRef",
    "WorkspaceConformance",
    "WorkspaceConformanceFacts",
    "WorkspaceCredentialEvidence",
    "WorkspaceCredentialGrant",
    "WorkspaceCredentialPolicy",
    "WorkspaceEntryKind",
    "WorkspaceEntryState",
    "WorkspaceEnvironmentProvenance",
    "WorkspaceEvidenceSubject",
    "WorkspaceInspection",
    "WorkspaceInstanceRef",
    "WorkspacePathControlCapability",
    "WorkspacePlan",
    "WorkspacePlanKey",
    "WorkspacePlanRef",
    "WorkspacePlanResolution",
    "WorkspacePolicyDefinition",
    "WorkspacePolicyFact",
    "WorkspacePreflight",
    "WorkspaceProperty",
    "WorkspacePropertyEvidence",
    "WorkspacePropertyRequirement",
    "WorkspaceProviderDescriptor",
    "WorkspaceProviderDescriptorFact",
    "WorkspaceProviderPropertyCapability",
    "WorkspaceProviderRef",
    "WorkspaceProvisionResult",
    "WorkspaceReason",
    "WorkspaceResourceDimension",
    "WorkspaceResourceEvidence",
    "WorkspaceResourceLimits",
    "WorkspaceRetentionMode",
    "WorkspaceRetentionPolicy",
    "WorkspaceTeardownEvidence",
    "WorkspaceTerminalDisposition",
    "WorkspaceToolRef",
    "WorkPacketConformanceFact",
    "digest_workspace_change_manifest",
    "validate_repository_path",
    "workspace_change_manifest_ref",
    "workspace_plan_ref",
]
