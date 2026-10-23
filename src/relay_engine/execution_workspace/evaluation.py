"""Pure identity, resolution, preflight, scope, and conformance evaluation."""

from __future__ import annotations

import hashlib
import json

from relay_engine.agent_runtime import RuntimeWorkspaceAttachment
from relay_engine.domain import ContentDigest
from relay_engine.execution_workspace.models import (
    ControlStrength,
    CredentialExposureMode,
    FilesystemAccess,
    FilesystemPolicy,
    ProtectedAssetWorkspaceBinding,
    WorkPacketConformanceFact,
    WorkspaceBackendKind,
    WorkspaceBoundaryClass,
    WorkspaceConformance,
    WorkspaceConformanceFacts,
    WorkspaceControlContinuityEvidence,
    WorkspaceEvidenceSubject,
    WorkspaceInstanceRef,
    WorkspacePlan,
    WorkspacePlanRef,
    WorkspacePlanResolution,
    WorkspacePolicyDefinition,
    WorkspacePreflight,
    WorkspaceProperty,
    WorkspaceProviderDescriptor,
    WorkspaceProviderRef,
    WorkspaceReason,
    WorkspaceResourceDimension,
    WorkspaceTeardownEvidence,
    WorkspaceTerminalDisposition,
    validate_repository_path,
    workspace_plan_ref,
)
from relay_engine.role_contracts import RequirementStatus, RoleContract, role_contract_ref
from relay_engine.work_packets import (
    ProtectedVerificationAuthorityFact,
    WorkPacket,
    WorkPacketRef,
    WorkspacePolicyRef,
    protected_verification_requirement_ref,
    work_packet_ref,
)

_STRENGTH_RANK = {
    ControlStrength.DETECTIVE: 0,
    ControlStrength.MEDIATED: 1,
    ControlStrength.BOUNDARY_ENFORCED: 2,
}


def canonical_workspace_policy_json(policy: WorkspacePolicyDefinition) -> str:
    validated = type(policy).model_validate(policy.model_dump(mode="python"))
    return json.dumps(
        validated.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest_workspace_policy(policy: WorkspacePolicyDefinition) -> ContentDigest:
    return (
        "sha256:"
        + hashlib.sha256(canonical_workspace_policy_json(policy).encode("utf-8")).hexdigest()
    )


def workspace_policy_ref(policy: WorkspacePolicyDefinition) -> WorkspacePolicyRef:
    return WorkspacePolicyRef(
        policy_key=policy.policy_key, content_digest=digest_workspace_policy(policy)
    )


def workspace_policy_ref_matches(
    policy: WorkspacePolicyDefinition, ref: WorkspacePolicyRef
) -> bool:
    return workspace_policy_ref(policy) == ref


def canonical_workspace_plan_json(plan: WorkspacePlan) -> str:
    validated = type(plan).model_validate(plan.model_dump(mode="python"))
    return json.dumps(
        validated.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest_workspace_plan(plan: WorkspacePlan) -> ContentDigest:
    return (
        "sha256:" + hashlib.sha256(canonical_workspace_plan_json(plan).encode("utf-8")).hexdigest()
    )


def workspace_provider_ref(descriptor: WorkspaceProviderDescriptor) -> WorkspaceProviderRef:
    payload = json.dumps(
        descriptor.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return WorkspaceProviderRef(
        provider_id=descriptor.provider_id,
        provider_version=descriptor.provider_version,
        descriptor_digest="sha256:" + hashlib.sha256(payload).hexdigest(),
    )


def workspace_provider_ref_matches(
    descriptor: WorkspaceProviderDescriptor, ref: WorkspaceProviderRef
) -> bool:
    return workspace_provider_ref(descriptor) == ref


def _provider_capability(descriptor: WorkspaceProviderDescriptor, property_key: WorkspaceProperty):
    return next(
        (item for item in descriptor.property_capabilities if item.property is property_key), None
    )


def _semantic_compatibility(
    plan: WorkspacePlan,
    descriptor: WorkspaceProviderDescriptor,
) -> tuple[list[WorkspaceReason], list[WorkspaceReason]]:
    failures: list[WorkspaceReason] = []
    unknown: list[WorkspaceReason] = []
    if plan.shell_policy.mode not in descriptor.supported_shell_modes:
        failures.append(WorkspaceReason.SHELL_POLICY_UNSUPPORTED)
    if plan.network_policy.mode not in descriptor.supported_network_modes:
        failures.append(WorkspaceReason.NETWORK_POLICY_UNSUPPORTED)
    if plan.external_side_effect_policy.mode not in descriptor.supported_external_side_effect_modes:
        failures.append(WorkspaceReason.EXTERNAL_SIDE_EFFECT_POLICY_UNSUPPORTED)
    for grant in plan.workspace_credential_grants:
        if grant.exposure_mode not in descriptor.supported_credential_exposure_modes:
            failures.append(WorkspaceReason.CREDENTIAL_EXPOSURE_UNSUPPORTED)
    if plan.repository_metadata_policy.access not in descriptor.supported_repository_metadata_modes:
        failures.append(WorkspaceReason.PROVIDER_CAPABILITY_INSUFFICIENT)
    for dimension in _required_resource_dimensions_from_plan(plan):
        if dimension not in descriptor.supported_resource_dimensions:
            failures.append(WorkspaceReason.RESOURCE_LIMIT_UNSUPPORTED)
    capabilities = {
        item.file_key: item.content_digest
        for item in descriptor.provider_injected_file_capabilities
    }
    for requirement in plan.provider_injected_files:
        if capabilities.get(requirement.provider_file_key) != requirement.content_digest:
            failures.append(WorkspaceReason.PROVIDER_CAPABILITY_INSUFFICIENT)
    path_capabilities = set(descriptor.path_control_capabilities)
    for requirement in plan.property_requirements:
        if requirement.property not in {
            WorkspaceProperty.FILESYSTEM_SCOPE,
            WorkspaceProperty.PATH_ESCAPE_CONTROL,
        }:
            continue
        supported_values = {item.value for item in path_capabilities}
        needed = {"CANONICAL_REPOSITORY_PATHS"}
        needed.add(
            "SYMLINK_ESCAPE_DETECTION"
            if requirement.minimum_strength is ControlStrength.DETECTIVE
            else "SYMLINK_ESCAPE_PREVENTION"
        )
        if not needed.issubset(supported_values):
            failures.append(WorkspaceReason.PROVIDER_CAPABILITY_INSUFFICIENT)
    if (
        descriptor.backend_kind is WorkspaceBackendKind.LOCAL_CLONE
        and descriptor.boundary_class is WorkspaceBoundaryClass.SAME_USER_NO_SECURITY_BOUNDARY
    ):
        for requirement in plan.property_requirements:
            if (
                requirement.property
                in {
                    WorkspaceProperty.FILESYSTEM_SCOPE,
                    WorkspaceProperty.PATH_ESCAPE_CONTROL,
                    WorkspaceProperty.PROTECTED_ASSET_CONTROL,
                    WorkspaceProperty.NETWORK_REACHABILITY_CONTROL,
                    WorkspaceProperty.EXTERNAL_SIDE_EFFECT_CONTROL,
                    WorkspaceProperty.CREDENTIAL_EXPOSURE_CONTROL,
                    WorkspaceProperty.RESOURCE_LIMIT_CONTROL,
                }
                and requirement.minimum_strength is ControlStrength.BOUNDARY_ENFORCED
            ):
                failures.append(WorkspaceReason.PROVIDER_BOUNDARY_INSUFFICIENT)
    return failures, unknown


def _required_resource_dimensions_from_plan(
    plan: WorkspacePlan,
) -> tuple[WorkspaceResourceDimension, ...]:
    limits = plan.resource_limits
    pairs = (
        (limits.max_memory_bytes, WorkspaceResourceDimension.MEMORY_BYTES),
        (limits.max_disk_bytes, WorkspaceResourceDimension.DISK_BYTES),
        (limits.max_processes, WorkspaceResourceDimension.PROCESS_COUNT),
        (limits.max_cpu_seconds, WorkspaceResourceDimension.CPU_SECONDS),
        (limits.max_open_files, WorkspaceResourceDimension.OPEN_FILES),
    )
    return tuple(dimension for value, dimension in pairs if value is not None)


def evaluate_workspace_preflight(
    plan: WorkspacePlan,
    provider_descriptor: WorkspaceProviderDescriptor | None,
) -> WorkspacePreflight:
    """Evaluate exact plan requirements against declared provider capability."""

    if provider_descriptor is None:
        return WorkspacePreflight(
            status=RequirementStatus.INDETERMINATE,
            reasons=(WorkspaceReason.PROVIDER_DESCRIPTOR_UNAVAILABLE,),
            unsupported_property_keys=(),
        )
    if workspace_provider_ref(provider_descriptor) != plan.provider_ref:
        return WorkspacePreflight(
            status=RequirementStatus.INDETERMINATE,
            reasons=(WorkspaceReason.PROVIDER_REF_MISMATCH,),
            unsupported_property_keys=(),
        )
    reasons: list[WorkspaceReason] = []
    unsupported: list[str] = []
    for requirement in plan.property_requirements:
        capability = _provider_capability(provider_descriptor, requirement.property)
        if capability is None:
            reasons.append(WorkspaceReason.REQUIRED_WORKSPACE_PROPERTY_UNSUPPORTED)
            unsupported.append(requirement.key)
        elif (
            _STRENGTH_RANK[capability.maximum_strength]
            < _STRENGTH_RANK[requirement.minimum_strength]
        ):
            reasons.append(WorkspaceReason.CONTROL_STRENGTH_INSUFFICIENT)
            unsupported.append(requirement.key)
    semantic_failures, _ = _semantic_compatibility(plan, provider_descriptor)
    reasons.extend(semantic_failures)
    reasons_tuple = tuple(dict.fromkeys(reasons))
    status = RequirementStatus.UNSATISFIED if reasons_tuple else RequirementStatus.SATISFIED
    return WorkspacePreflight(
        status=status,
        reasons=reasons_tuple,
        unsupported_property_keys=tuple(sorted(set(unsupported))),
    )


def _expected_authority_subjects(
    bindings: tuple[ProtectedAssetWorkspaceBinding, ...],
) -> tuple[tuple[object, object], ...]:
    return tuple(
        (binding.requirement_ref, binding.separate_authority_ref)
        for binding in bindings
        if binding.separate_authority_ref is not None
    )


def resolve_workspace_plan(
    packet: WorkPacket,
    packet_ref: WorkPacketRef,
    packet_conformance_fact: WorkPacketConformanceFact,
    workspace_policy: WorkspacePolicyDefinition,
    role_contract: RoleContract,
    protected_authority_facts: tuple[ProtectedVerificationAuthorityFact, ...],
    provider_descriptor: WorkspaceProviderDescriptor,
    *,
    plan_key: str,
    revision: int,
) -> WorkspacePlanResolution:
    """Resolve an exact self-contained plan from already-materialized inputs."""

    reasons: list[WorkspaceReason] = []
    known_failure = False
    indeterminate = False
    if work_packet_ref(packet) != packet_ref:
        known_failure = True
        reasons.append(WorkspaceReason.WORK_PACKET_REF_MISMATCH)
    if packet_conformance_fact.evaluated_work_packet_ref != packet_ref:
        known_failure = True
        reasons.append(WorkspaceReason.WORK_PACKET_REF_MISMATCH)
    elif packet_conformance_fact.conformance.status is RequirementStatus.INDETERMINATE:
        indeterminate = True
        reasons.append(WorkspaceReason.WORK_PACKET_CONFORMANCE_REQUIRED)
    elif packet_conformance_fact.conformance.status is RequirementStatus.UNSATISFIED:
        known_failure = True
        reasons.append(WorkspaceReason.WORK_PACKET_CONFORMANCE_REQUIRED)
    if packet.workspace_policy_ref is None:
        known_failure = True
        reasons.append(WorkspaceReason.WORKSPACE_POLICY_REQUIRED)
    elif not workspace_policy_ref_matches(workspace_policy, packet.workspace_policy_ref):
        known_failure = True
        reasons.append(WorkspaceReason.WORKSPACE_POLICY_REF_MISMATCH)
    if workspace_policy.policy_basis_ref != packet.policy_basis_ref:
        known_failure = True
        reasons.append(WorkspaceReason.WORKSPACE_POLICY_REF_MISMATCH)
    if workspace_policy.governance_profile_ref != packet.governance_profile_ref:
        known_failure = True
        reasons.append(WorkspaceReason.GOVERNANCE_PROFILE_MISMATCH)
    if role_contract_ref(role_contract) != packet.role_contract_ref:
        known_failure = True
        reasons.append(WorkspaceReason.ROLE_CONTRACT_REF_MISMATCH)
    policy_keys = {item.key for item in workspace_policy.property_requirements}
    if any(key not in policy_keys for key in packet.required_workspace_property_keys):
        known_failure = True
        reasons.append(WorkspaceReason.REQUIRED_WORKSPACE_PROPERTY_UNKNOWN)
    packet_credentials = {item.credential_id for item in packet.credential_refs}
    if any(
        grant.credential_ref.credential_id not in packet_credentials
        for grant in workspace_policy.credential_policy.grants
    ):
        known_failure = True
        reasons.append(WorkspaceReason.CREDENTIAL_NOT_DECLARED)

    bindings: list[ProtectedAssetWorkspaceBinding] = []
    requirements = tuple(
        (protected_verification_requirement_ref(item), item)
        for item in packet.protected_verification_requirements
    )
    control_property_key = _protected_control_key(workspace_policy)
    if packet.protected_verification_requirements and control_property_key is None:
        known_failure = True
        reasons.append(WorkspaceReason.REQUIRED_WORKSPACE_PROPERTY_UNKNOWN)
    expected_binding_keys: list[tuple[object, ...]] = []
    for requirement_ref, requirement in requirements:
        expected_binding_keys.append((requirement_ref, requirement.separate_authority_ref))
        if requirement.required_operation not in role_contract.verification_asset_permissions:
            known_failure = True
            reasons.append(WorkspaceReason.ROLE_PERMISSION_INSUFFICIENT)
        ordinary_access = effective_filesystem_access(
            workspace_policy.filesystem_policy, requirement.artifact.path
        )
        requires_write = requirement.required_operation.value in {"CREATE", "MODIFY"}
        if ordinary_access is FilesystemAccess.DENY or (
            requires_write and ordinary_access is not FilesystemAccess.READ_WRITE
        ):
            known_failure = True
            reasons.append(WorkspaceReason.FILESYSTEM_SCOPE_VIOLATION)
        bindings.append(
            ProtectedAssetWorkspaceBinding(
                requirement_ref=requirement_ref,
                artifact=requirement.artifact,
                required_operation=requirement.required_operation,
                separate_authority_ref=requirement.separate_authority_ref,
                workspace_path=requirement.artifact.path,
                physical_access=(
                    FilesystemAccess.READ_WRITE if requires_write else FilesystemAccess.READ_ONLY
                ),
                control_property_key=control_property_key or "protected-assets",
            )
        )
    expected = tuple(item for item in expected_binding_keys if item[1] is not None)
    supplied = tuple(
        (item.evaluated_requirement_ref, item.evaluated_authority_ref)
        for item in protected_authority_facts
    )
    if supplied != expected:
        if _is_ordered_subset(supplied, expected):
            indeterminate = True
            reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED)
        else:
            known_failure = True
            reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED)
    else:
        for fact in protected_authority_facts:
            if fact.status is RequirementStatus.UNSATISFIED:
                known_failure = True
                reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED)
            elif fact.status is RequirementStatus.INDETERMINATE:
                indeterminate = True
                reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED)

    policy_ref = packet.workspace_policy_ref
    if policy_ref is None:
        return WorkspacePlanResolution(
            status=RequirementStatus.UNSATISFIED,
            reasons=tuple(dict.fromkeys(reasons)),
            plan=None,
        )
    plan = WorkspacePlan(
        plan_key=plan_key,
        revision=revision,
        work_packet_ref=packet_ref,
        source_baseline_ref=packet.source_baseline_ref,
        role_contract_ref=packet.role_contract_ref,
        workspace_policy_ref=policy_ref,
        governance_profile_ref=packet.governance_profile_ref,
        provider_ref=workspace_provider_ref(provider_descriptor),
        packet_required_property_keys=packet.required_workspace_property_keys,
        property_requirements=workspace_policy.property_requirements,
        protected_asset_bindings=tuple(bindings),
        workspace_credential_grants=workspace_policy.credential_policy.grants,
        provider_injected_files=workspace_policy.provider_injected_files,
        filesystem_policy=workspace_policy.filesystem_policy,
        repository_metadata_policy=workspace_policy.repository_metadata_policy,
        tool_policy=workspace_policy.tool_policy,
        shell_policy=workspace_policy.shell_policy,
        network_policy=workspace_policy.network_policy,
        external_side_effect_policy=workspace_policy.external_side_effect_policy,
        resource_limits=workspace_policy.resource_limits,
        retention_policy=workspace_policy.retention_policy,
    )
    preflight = evaluate_workspace_preflight(plan, provider_descriptor)
    reasons.extend(preflight.reasons)
    if preflight.status is RequirementStatus.UNSATISFIED:
        return WorkspacePlanResolution(
            status=RequirementStatus.UNSATISFIED,
            reasons=tuple(dict.fromkeys(reasons)),
            plan=None,
        )
    if preflight.status is RequirementStatus.INDETERMINATE:
        indeterminate = True
    if known_failure:
        status = RequirementStatus.UNSATISFIED
    elif indeterminate:
        status = RequirementStatus.INDETERMINATE
    else:
        status = RequirementStatus.SATISFIED
    return WorkspacePlanResolution(
        status=status,
        reasons=tuple(dict.fromkeys(reasons)),
        plan=plan if status is RequirementStatus.SATISFIED else None,
    )


def _is_ordered_subset[T](supplied: tuple[T, ...], expected: tuple[T, ...]) -> bool:
    """Whether supplied is an exact ordered subset without reordering."""

    cursor = 0
    for value in supplied:
        try:
            cursor = expected.index(value, cursor) + 1
        except ValueError:
            return False
    return True


def _protected_control_key(policy: WorkspacePolicyDefinition) -> str | None:
    keys = tuple(
        item.key
        for item in policy.property_requirements
        if item.property is WorkspaceProperty.PROTECTED_ASSET_CONTROL
    )
    return keys[0] if len(keys) == 1 else None


def path_has_prefix(path: str, prefix: str) -> bool:
    """Return segment-aware repository path prefix membership."""

    validate_repository_path(path)
    validate_repository_path(prefix, allow_root=True)
    return prefix == "." or path == prefix or path.startswith(prefix + "/")


def effective_filesystem_access(policy: FilesystemPolicy, path: str) -> FilesystemAccess:
    """Apply denied-prefix precedence and exact writable-prefix semantics."""

    validate_repository_path(path)
    if any(path_has_prefix(path, item.value) for item in policy.denied_prefixes):
        return FilesystemAccess.DENY
    if policy.default_access is FilesystemAccess.DENY:
        return FilesystemAccess.DENY
    if any(path_has_prefix(path, item.value) for item in policy.writable_prefixes):
        return FilesystemAccess.READ_WRITE
    return policy.default_access


def derive_runtime_workspace_attachment(
    instance: WorkspaceInstanceRef,
) -> RuntimeWorkspaceAttachment:
    """Derive the accepted Slice 2.1 attachment without invoking a runtime."""

    return RuntimeWorkspaceAttachment(
        workspace_id=instance.workspace_id,
        root=instance.root,
        repository=instance.repository,
        source_commit=instance.source_commit,
    )


def evaluate_workspace_conformance(
    plan: WorkspacePlan,
    instance: WorkspaceInstanceRef,
    provider_ref: WorkspaceProviderRef,
    facts: WorkspaceConformanceFacts,
    *,
    terminal: bool = False,
) -> WorkspaceConformance:
    """Evaluate exact-subject workspace evidence with UNSATISFIED precedence."""

    reasons: list[WorkspaceReason] = []
    unsatisfied: list[str] = []
    indeterminate: list[str] = []
    known_failure = False
    plan_ref = _plan_ref(plan)
    if instance.source_commit != plan.source_baseline_ref.commit:
        reasons.append(WorkspaceReason.SOURCE_BASELINE_MISMATCH)
        known_failure = True
    if instance.plan_ref != plan_ref or instance.provider_ref != provider_ref:
        reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
        known_failure = True
    if (facts.evaluated_plan_ref, facts.evaluated_instance_ref, facts.evaluated_provider_ref) != (
        plan_ref,
        instance,
        provider_ref,
    ):
        reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
        known_failure = True
    if facts.initial_inspection.instance_ref != instance:
        reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
        known_failure = True
    if facts.work_packet_conformance_fact.evaluated_work_packet_ref != plan.work_packet_ref:
        reasons.append(WorkspaceReason.WORK_PACKET_REF_MISMATCH)
        known_failure = True
    elif facts.work_packet_conformance_fact.conformance.status is not RequirementStatus.SATISFIED:
        if facts.work_packet_conformance_fact.conformance.status is RequirementStatus.UNSATISFIED:
            reasons.append(WorkspaceReason.WORK_PACKET_CONFORMANCE_REQUIRED)
            known_failure = True
        else:
            reasons.append(WorkspaceReason.WORK_PACKET_CONFORMANCE_REQUIRED)
            indeterminate.extend(item.key for item in plan.property_requirements)
    if facts.workspace_policy_fact.evaluated_ref != plan.workspace_policy_ref:
        reasons.append(WorkspaceReason.WORKSPACE_POLICY_REF_MISMATCH)
        known_failure = True
    elif facts.workspace_policy_fact.status is not RequirementStatus.SATISFIED:
        reasons.append(WorkspaceReason.WORKSPACE_POLICY_STALE)
        if facts.workspace_policy_fact.status is RequirementStatus.INDETERMINATE:
            indeterminate.append("workspace-policy")
        else:
            known_failure = True
    if facts.role_contract_fact.evaluated_ref != plan.role_contract_ref:
        reasons.append(WorkspaceReason.ROLE_CONTRACT_REF_MISMATCH)
        known_failure = True
    elif facts.role_contract_fact.status is not RequirementStatus.SATISFIED:
        reasons.append(WorkspaceReason.ROLE_CONTRACT_REF_MISMATCH)
        if facts.role_contract_fact.status is RequirementStatus.INDETERMINATE:
            indeterminate.append("role-contract")
        else:
            known_failure = True
    if facts.provider_descriptor_fact.evaluated_ref != provider_ref:
        reasons.append(WorkspaceReason.PROVIDER_REF_MISMATCH)
        known_failure = True
    elif facts.provider_descriptor_fact.status is not RequirementStatus.SATISFIED:
        reasons.append(WorkspaceReason.PROVIDER_DESCRIPTOR_UNAVAILABLE)
        if facts.provider_descriptor_fact.status is RequirementStatus.INDETERMINATE:
            indeterminate.append("provider-descriptor")
        else:
            known_failure = True

    expected_keys = tuple(item.key for item in plan.property_requirements)
    supplied_keys = tuple(item.property_key for item in facts.property_evidence)
    if len(supplied_keys) != len(set(supplied_keys)):
        reasons.append(WorkspaceReason.PROPERTY_EVIDENCE_UNEXPECTED)
        known_failure = True
    if any(key not in expected_keys for key in supplied_keys):
        reasons.append(WorkspaceReason.PROPERTY_EVIDENCE_UNEXPECTED)
        known_failure = True
    else:
        if not _is_ordered_subset(supplied_keys, expected_keys):
            reasons.append(WorkspaceReason.PROPERTY_EVIDENCE_UNEXPECTED)
            known_failure = True
    evidence_by_key = {item.property_key: item for item in facts.property_evidence}
    for requirement in plan.property_requirements:
        evidence = evidence_by_key.get(requirement.key)
        if evidence is None:
            indeterminate.append(requirement.key)
            reasons.append(WorkspaceReason.PROPERTY_EVIDENCE_MISSING)
            continue
        subject = evidence.subject
        if (subject.plan_ref, subject.instance_ref, subject.provider_ref) != (
            plan_ref,
            instance,
            provider_ref,
        ):
            reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
            known_failure = True
        if evidence.property is not requirement.property:
            reasons.append(WorkspaceReason.REQUIRED_WORKSPACE_PROPERTY_UNSATISFIED)
            unsatisfied.append(requirement.key)
            known_failure = True
        if evidence.status is RequirementStatus.UNSATISFIED:
            unsatisfied.append(requirement.key)
            known_failure = True
        elif evidence.status is RequirementStatus.INDETERMINATE:
            indeterminate.append(requirement.key)
        if (
            _STRENGTH_RANK[evidence.established_strength]
            < _STRENGTH_RANK[requirement.minimum_strength]
        ):
            unsatisfied.append(requirement.key)
            reasons.append(WorkspaceReason.CONTROL_STRENGTH_INSUFFICIENT)
            known_failure = True

    if facts.environment_provenance.subject != WorkspaceEvidenceSubject(
        plan_ref=plan_ref, instance_ref=instance, provider_ref=provider_ref
    ):
        reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
        known_failure = True
    expected_continuity = any(
        requirement.property is WorkspaceProperty.CONTROL_CONTINUITY
        for requirement in plan.property_requirements
    )
    if expected_continuity:
        continuity = facts.continuity_evidence
        if continuity is None:
            reasons.append(WorkspaceReason.CONTROL_CONTINUITY_INDETERMINATE)
            indeterminate.append("control-continuity")
        else:
            if continuity.subject != WorkspaceEvidenceSubject(
                plan_ref=plan_ref, instance_ref=instance, provider_ref=provider_ref
            ):
                reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
                known_failure = True
            _validate_evidence_subject(continuity, plan_ref, instance, provider_ref, reasons)
            if continuity.status is RequirementStatus.UNSATISFIED:
                reasons.append(WorkspaceReason.CONTROL_CONTINUITY_INDETERMINATE)
                known_failure = True
            elif continuity.status is RequirementStatus.INDETERMINATE:
                reasons.append(WorkspaceReason.CONTROL_CONTINUITY_INDETERMINATE)
                indeterminate.append("control-continuity")

    expected_authorities = _expected_authority_subjects(plan.protected_asset_bindings)
    supplied_authorities = tuple(
        (item.evaluated_requirement_ref, item.evaluated_authority_ref)
        for item in facts.protected_authority_facts
    )
    if not _is_ordered_subset(supplied_authorities, expected_authorities):
        reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED)
        known_failure = True
    if supplied_authorities != expected_authorities:
        reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED)
        indeterminate.append("protected-authority")
    fact_by_subject = {
        (item.evaluated_requirement_ref, item.evaluated_authority_ref): item
        for item in facts.protected_authority_facts
    }
    for binding in plan.protected_asset_bindings:
        if binding.separate_authority_ref is None:
            continue
        authority_fact = fact_by_subject.get(
            (binding.requirement_ref, binding.separate_authority_ref)
        )
        if authority_fact is None:
            indeterminate.append("protected-authority")
        elif authority_fact.status is RequirementStatus.UNSATISFIED:
            known_failure = True
            reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED)
        elif authority_fact.status is RequirementStatus.INDETERMINATE:
            indeterminate.append("protected-authority")
            reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED)

    if facts.initial_inspection.head_commit != instance.source_commit:
        reasons.append(WorkspaceReason.SOURCE_BASELINE_MISMATCH)
        known_failure = True
    if facts.initial_inspection.tracked_changes or facts.initial_inspection.untracked_paths:
        reasons.append(WorkspaceReason.INITIAL_STATE_DIRTY)
        known_failure = True
    initial_observations = {
        item.requirement_ref: item for item in facts.initial_inspection.protected_asset_observations
    }
    for binding in plan.protected_asset_bindings:
        control_requirement = next(
            (
                item
                for item in plan.property_requirements
                if item.key == binding.control_property_key
            ),
            None,
        )
        if (
            control_requirement is None
            or control_requirement.property is not WorkspaceProperty.PROTECTED_ASSET_CONTROL
        ):
            reasons.append(WorkspaceReason.REQUIRED_WORKSPACE_PROPERTY_UNKNOWN)
            known_failure = True
        initial = initial_observations.get(binding.requirement_ref)
        if initial is None:
            reasons.append(WorkspaceReason.PROTECTED_ASSET_OBSERVATION_MISSING)
            indeterminate.append(binding.control_property_key)
            continue
        if (
            initial.workspace_path != binding.workspace_path
            or binding.required_operation.value == "CREATE"
            and initial.state is not None
        ):
            reasons.append(WorkspaceReason.PROTECTED_ASSET_OBSERVATION_MISMATCH)
            known_failure = True
        elif binding.required_operation.value != "CREATE" and initial.state is None:
            reasons.append(WorkspaceReason.PROTECTED_ASSET_OBSERVATION_MISSING)
            indeterminate.append(binding.control_property_key)
    if terminal:
        if facts.terminal_inspection is None or facts.change_manifest is None:
            reasons.append(WorkspaceReason.CHANGESET_UNAVAILABLE)
            indeterminate.extend(expected_keys)
        elif (
            facts.terminal_inspection.instance_ref != instance
            or facts.change_manifest.instance_ref != instance
        ):
            reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
            known_failure = True
        else:
            for entry in facts.change_manifest.entries:
                if (
                    effective_filesystem_access(plan.filesystem_policy, entry.path)
                    is not FilesystemAccess.READ_WRITE
                ):
                    reasons.append(WorkspaceReason.CHANGE_OUT_OF_SCOPE)
                    known_failure = True
            terminal_observations = {
                item.requirement_ref: item
                for item in facts.terminal_inspection.protected_asset_observations
            }
            changes = {item.path: item for item in facts.change_manifest.entries}
            for binding in plan.protected_asset_bindings:
                initial = initial_observations.get(binding.requirement_ref)
                final = terminal_observations.get(binding.requirement_ref)
                if initial is None or final is None:
                    reasons.append(WorkspaceReason.PROTECTED_ASSET_OBSERVATION_MISSING)
                    indeterminate.append(binding.control_property_key)
                    continue
                if (
                    final.workspace_path != binding.workspace_path
                    or initial.workspace_path != binding.workspace_path
                ):
                    reasons.append(WorkspaceReason.PROTECTED_ASSET_OBSERVATION_MISMATCH)
                    known_failure = True
                    continue
                entry = changes.get(binding.workspace_path)
                if initial.state != final.state:
                    if entry is None or entry.before != initial.state or entry.after != final.state:
                        reasons.append(WorkspaceReason.PROTECTED_ASSET_OBSERVATION_MISMATCH)
                        known_failure = True
                    if binding.required_operation.value not in {"CREATE", "MODIFY"}:
                        reasons.append(WorkspaceReason.PROTECTED_ASSET_MUTATED)
                        known_failure = True
                elif entry is not None:
                    reasons.append(WorkspaceReason.PROTECTED_ASSET_OBSERVATION_MISMATCH)
                    known_failure = True

    expected_credentials = tuple(
        grant
        for grant in plan.workspace_credential_grants
        if grant.exposure_mode is not CredentialExposureMode.NONE
    )
    supplied_credentials = tuple(
        item.credential_ref.credential_id for item in facts.credential_evidence
    )
    expected_credential_ids = tuple(
        item.credential_ref.credential_id for item in expected_credentials
    )
    if not _is_ordered_subset(supplied_credentials, expected_credential_ids):
        reasons.append(WorkspaceReason.UNEXPECTED_CREDENTIAL_EXPOSURE)
        known_failure = True
    if supplied_credentials != expected_credential_ids:
        indeterminate.append("credential-exposure")
    for value in facts.credential_evidence:
        if (
            value.subject.plan_ref != plan_ref
            or value.subject.instance_ref != instance
            or value.subject.provider_ref != provider_ref
        ):
            reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
            known_failure = True
        expected = next(
            (
                grant
                for grant in plan.workspace_credential_grants
                if grant.credential_ref == value.credential_ref
            ),
            None,
        )
        if expected is None or expected.exposure_mode != value.exposure_mode:
            reasons.append(WorkspaceReason.UNEXPECTED_CREDENTIAL_EXPOSURE)
            known_failure = True
        if value.status is RequirementStatus.INDETERMINATE:
            indeterminate.append("credential-exposure")
        elif value.status is RequirementStatus.UNSATISFIED:
            reasons.append(WorkspaceReason.CREDENTIAL_EXPOSURE_UNSUPPORTED)
            known_failure = True

    limits = plan.resource_limits
    has_resource_limits = any(
        value is not None
        for value in (
            limits.max_memory_bytes,
            limits.max_disk_bytes,
            limits.max_processes,
            limits.max_cpu_seconds,
            limits.max_open_files,
        )
    )
    if has_resource_limits:
        resource = facts.resource_evidence
        if resource is None:
            indeterminate.append("resource-limits")
        elif resource.subject != WorkspaceEvidenceSubject(
            plan_ref=plan_ref, instance_ref=instance, provider_ref=provider_ref
        ):
            reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)
            known_failure = True
        elif resource.status is RequirementStatus.UNSATISFIED:
            reasons.append(WorkspaceReason.RESOURCE_LIMIT_MISMATCH)
            known_failure = True
        elif resource.status is RequirementStatus.INDETERMINATE:
            indeterminate.append("resource-limits")
        comparisons = (
            ()
            if resource is None
            else (
                (resource.memory_limit_bytes, limits.max_memory_bytes),
                (resource.disk_limit_bytes, limits.max_disk_bytes),
                (resource.process_limit, limits.max_processes),
                (resource.cpu_seconds_limit, limits.max_cpu_seconds),
                (resource.open_files_limit, limits.max_open_files),
            )
        )
        if any(
            actual is None or actual > expected
            for actual, expected in comparisons
            if expected is not None
        ):
            reasons.append(WorkspaceReason.RESOURCE_LIMIT_MISMATCH)
            known_failure = True

    if terminal and facts.teardown_evidence is not None:
        if facts.teardown_evidence.subject != WorkspaceEvidenceSubject(
            plan_ref=plan_ref, instance_ref=instance, provider_ref=provider_ref
        ):
            known_failure = True
        _validate_evidence_subject(
            facts.teardown_evidence, plan_ref, instance, provider_ref, reasons
        )
        _evaluate_teardown(plan, facts.teardown_evidence, reasons, indeterminate)
        if (
            facts.teardown_evidence.disposition is WorkspaceTerminalDisposition.TEARDOWN_FAILED
            or facts.teardown_evidence.credential_cleanup_status is RequirementStatus.UNSATISFIED
            or (
                plan.retention_policy.mode.value == "DELETE_ON_TERMINAL"
                and facts.teardown_evidence.disposition is not WorkspaceTerminalDisposition.DELETED
            )
        ):
            known_failure = True
    elif terminal:
        reasons.append(WorkspaceReason.TEARDOWN_INDETERMINATE)
        indeterminate.append("teardown")
        indeterminate.append("teardown")
    if known_failure:
        status = RequirementStatus.UNSATISFIED
    elif indeterminate:
        status = RequirementStatus.INDETERMINATE
    elif reasons:
        status = RequirementStatus.UNSATISFIED
    else:
        status = RequirementStatus.SATISFIED
    return WorkspaceConformance(
        status=status,
        reasons=tuple(dict.fromkeys(reasons)),
        unsatisfied_property_keys=tuple(sorted(set(unsatisfied))),
        indeterminate_property_keys=tuple(sorted(set(indeterminate))),
    )


def _validate_evidence_subject(
    evidence: WorkspaceControlContinuityEvidence | WorkspaceTeardownEvidence,
    plan_ref: WorkspacePlanRef,
    instance: WorkspaceInstanceRef,
    provider_ref: WorkspaceProviderRef,
    reasons: list[WorkspaceReason],
) -> None:
    if (
        evidence.subject.plan_ref,
        evidence.subject.instance_ref,
        evidence.subject.provider_ref,
    ) != (plan_ref, instance, provider_ref):
        reasons.append(WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH)


def _evaluate_teardown(
    plan: WorkspacePlan,
    evidence: WorkspaceTeardownEvidence,
    reasons: list[WorkspaceReason],
    indeterminate: list[str],
) -> None:
    if evidence.disposition is WorkspaceTerminalDisposition.TEARDOWN_FAILED:
        reasons.append(WorkspaceReason.TEARDOWN_FAILED)
    elif evidence.disposition is WorkspaceTerminalDisposition.UNKNOWN:
        reasons.append(WorkspaceReason.TEARDOWN_INDETERMINATE)
        indeterminate.append("teardown")
    elif (
        plan.retention_policy.mode.value == "DELETE_ON_TERMINAL"
        and evidence.disposition is not WorkspaceTerminalDisposition.DELETED
    ):
        reasons.append(WorkspaceReason.RETENTION_POLICY_VIOLATION)
    if (
        evidence.disposition is WorkspaceTerminalDisposition.DELETED
        and evidence.workspace_absence_status is not RequirementStatus.SATISFIED
    ):
        if evidence.workspace_absence_status is RequirementStatus.UNSATISFIED:
            reasons.append(WorkspaceReason.TEARDOWN_FAILED)
        else:
            reasons.append(WorkspaceReason.TEARDOWN_INDETERMINATE)
            indeterminate.append("workspace-absence")
    if evidence.credential_cleanup_status is RequirementStatus.INDETERMINATE:
        indeterminate.append("credential-cleanup")
        reasons.append(WorkspaceReason.TEARDOWN_INDETERMINATE)
    elif evidence.credential_cleanup_status is RequirementStatus.UNSATISFIED:
        reasons.append(WorkspaceReason.TEARDOWN_FAILED)


def _plan_ref(plan: WorkspacePlan) -> WorkspacePlanRef:
    return workspace_plan_ref(plan)


def evaluate_workspace_plan_identity_conflicts(
    plans: tuple[WorkspacePlan, ...],
) -> tuple[WorkspacePlanRef, ...]:
    """Return stable plan identities that have conflicting content digests."""

    seen: dict[tuple[WorkPacketRef, str, int], ContentDigest] = {}
    conflicts: list[WorkspacePlanRef] = []
    for plan in plans:
        ref = workspace_plan_ref(plan)
        identity = (ref.work_packet_ref, ref.plan_key, ref.revision)
        prior = seen.get(identity)
        if prior is not None and prior != ref.content_digest:
            conflicts.append(ref)
        else:
            seen[identity] = ref.content_digest
    return tuple(conflicts)
