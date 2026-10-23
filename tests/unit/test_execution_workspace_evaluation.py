"""Pure workspace resolution and conformance evaluation tests."""

from __future__ import annotations

from test_work_packet_models import packet as make_work_packet

from relay_engine.agent_runtime import RuntimeCapability
from relay_engine.domain import (
    ActorKind,
    CommitRef,
    RepositoryRef,
)
from relay_engine.execution_workspace.evaluation import (
    derive_runtime_workspace_attachment,
    digest_workspace_plan,
    evaluate_workspace_conformance,
    evaluate_workspace_plan_identity_conflicts,
    evaluate_workspace_preflight,
    resolve_workspace_plan,
    workspace_plan_ref,
    workspace_policy_ref,
    workspace_provider_ref,
)
from relay_engine.execution_workspace.models import (
    ControlStrength,
    ExternalSideEffectMode,
    ExternalSideEffectPolicy,
    FilesystemAccess,
    FilesystemPolicy,
    NetworkMode,
    NetworkPolicy,
    RepositoryMetadataAccess,
    RepositoryMetadataPolicy,
    RoleContractFact,
    ShellMode,
    ShellPolicy,
    ToolDecision,
    ToolPolicy,
    WorkPacketConformanceFact,
    WorkspaceBackendKind,
    WorkspaceBoundaryClass,
    WorkspaceChangeManifest,
    WorkspaceConformanceFacts,
    WorkspaceCredentialPolicy,
    WorkspaceEnvironmentProvenance,
    WorkspaceEvidenceSubject,
    WorkspaceInspection,
    WorkspaceInstanceRef,
    WorkspacePlan,
    WorkspacePolicyDefinition,
    WorkspacePolicyFact,
    WorkspaceProperty,
    WorkspacePropertyEvidence,
    WorkspacePropertyRequirement,
    WorkspaceProviderDescriptor,
    WorkspaceProviderDescriptorFact,
    WorkspaceProviderPropertyCapability,
    WorkspaceReason,
    WorkspaceResourceLimits,
    WorkspaceRetentionMode,
    WorkspaceRetentionPolicy,
    digest_workspace_change_manifest,
    workspace_change_manifest_ref,
)
from relay_engine.role_contracts import (
    RequirementStatus,
    RoleAction,
    RoleClass,
    RoleContract,
    RoleContractRef,
    RoleInputRequirement,
    RoleOutputRequirement,
    VerificationAssetPermission,
    role_contract_ref,
)
from relay_engine.work_packets import (
    SourceBaselineRef,
    WorkPacket,
    WorkPacketConformance,
    WorkPacketRef,
    WorkspacePolicyRef,
    work_packet_ref,
)


def make_plan(
    maximum: ControlStrength = ControlStrength.DETECTIVE,
) -> tuple[WorkspacePlan, WorkspaceProviderDescriptor]:
    repo = RepositoryRef(
        id="repo_00000000-0000-0000-0000-000000000001", host="local", path="fixture"
    )
    commit = CommitRef(repository=repo, sha="a" * 40)
    packet_ref = WorkPacketRef(
        project_id="prj_00000000-0000-0000-0000-000000000001",
        slice_id="slc_00000000-0000-0000-0000-000000000001",
        packet_key="packet",
        revision=1,
        content_digest="sha256:" + "3" * 64,
    )
    provider = WorkspaceProviderDescriptor(
        provider_id="fixture-provider",
        provider_version="1",
        backend_kind=WorkspaceBackendKind.OTHER,
        boundary_class=WorkspaceBoundaryClass.MEDIATED_PROCESS_BOUNDARY,
        property_capabilities=(
            WorkspaceProviderPropertyCapability(
                property=WorkspaceProperty.EXACT_SOURCE_BASELINE, maximum_strength=maximum
            ),
        ),
        supported_shell_modes=(ShellMode.DENY,),
        supported_network_modes=(NetworkMode.DENY_ALL,),
        supported_external_side_effect_modes=(ExternalSideEffectMode.DENY_MUTATING_EFFECTS,),
        supported_credential_exposure_modes=(),
        supported_resource_dimensions=(),
        supported_repository_metadata_modes=(RepositoryMetadataAccess.READ_ONLY,),
        path_control_capabilities=(),
        provider_injected_file_capabilities=(),
    )
    plan = WorkspacePlan(
        plan_key="plan",
        revision=1,
        work_packet_ref=packet_ref,
        source_baseline_ref=SourceBaselineRef(
            baseline_id="base_00000000-0000-0000-0000-000000000001",
            project_id=packet_ref.project_id,
            commit=commit,
            content_digest="sha256:" + "4" * 64,
        ),
        role_contract_ref=RoleContractRef(
            role_key="implementer", revision=1, content_digest="sha256:" + "5" * 64
        ),
        workspace_policy_ref=WorkspacePolicyRef(
            policy_key="workspace", content_digest="sha256:" + "6" * 64
        ),
        governance_profile_ref=None,
        provider_ref=workspace_provider_ref(provider),
        packet_required_property_keys=("exact-source",),
        property_requirements=(
            WorkspacePropertyRequirement(
                key="exact-source",
                property=WorkspaceProperty.EXACT_SOURCE_BASELINE,
                minimum_strength=ControlStrength.DETECTIVE,
            ),
        ),
        protected_asset_bindings=(),
        workspace_credential_grants=(),
        provider_injected_files=(),
        filesystem_policy=FilesystemPolicy(
            default_access=FilesystemAccess.READ_WRITE, writable_prefixes=(), denied_prefixes=()
        ),
        repository_metadata_policy=RepositoryMetadataPolicy(
            access=RepositoryMetadataAccess.READ_ONLY
        ),
        tool_policy=ToolPolicy(default_decision=ToolDecision.DENY, rules=()),
        shell_policy=ShellPolicy(mode=ShellMode.DENY),
        network_policy=NetworkPolicy(mode=NetworkMode.DENY_ALL, allowed_endpoints=()),
        external_side_effect_policy=ExternalSideEffectPolicy(
            mode=ExternalSideEffectMode.DENY_MUTATING_EFFECTS, allowed_effects=()
        ),
        resource_limits=WorkspaceResourceLimits(),
        retention_policy=WorkspaceRetentionPolicy(mode=WorkspaceRetentionMode.DELETE_ON_TERMINAL),
    )
    return plan, provider


def test_preflight_compares_maximum_strength_to_full_plan_requirements() -> None:
    plan, descriptor = make_plan(ControlStrength.DETECTIVE)
    assert evaluate_workspace_preflight(plan, descriptor).status is RequirementStatus.SATISFIED
    stronger_plan = plan.model_copy(
        update={
            "property_requirements": (
                WorkspacePropertyRequirement(
                    key="exact-source",
                    property=WorkspaceProperty.EXACT_SOURCE_BASELINE,
                    minimum_strength=ControlStrength.MEDIATED,
                ),
            ),
        }
    )
    result = evaluate_workspace_preflight(stronger_plan, descriptor)
    assert result.status is RequirementStatus.UNSATISFIED
    assert result.unsupported_property_keys == ("exact-source",)


def test_stale_provider_descriptor_is_indeterminate() -> None:
    plan, descriptor = make_plan()
    stale = descriptor.model_copy(update={"provider_version": "2"})
    result = evaluate_workspace_preflight(plan, stale)
    assert result.status is RequirementStatus.INDETERMINATE
    assert result.reasons == (WorkspaceReason.PROVIDER_REF_MISMATCH,)


def test_runtime_attachment_is_pure_exact_derivation() -> None:
    plan, descriptor = make_plan()
    ref = workspace_plan_ref(plan)
    from relay_engine.execution_workspace.models import WorkspaceInstanceRef

    instance = WorkspaceInstanceRef(
        workspace_id="fixture-instance",
        plan_ref=ref,
        provider_ref=workspace_provider_ref(descriptor),
        repository=plan.source_baseline_ref.commit.repository,
        source_commit=plan.source_baseline_ref.commit,
        root="/tmp/workspace",
    )
    attachment = derive_runtime_workspace_attachment(instance)
    assert (
        attachment.workspace_id,
        attachment.root,
        attachment.repository,
        attachment.source_commit,
    ) == (
        instance.workspace_id,
        instance.root,
        instance.repository,
        instance.source_commit,
    )


def test_plan_and_change_manifest_have_fixed_non_self_referential_digests() -> None:
    plan, descriptor = make_plan()
    assert digest_workspace_plan(plan) == (
        "sha256:86c712aaa5f808a5960e306d8d0242ddb4b819a7f429eb19a31173291fe2403b"
    )
    instance = WorkspaceInstanceRef(
        workspace_id="fixture-instance",
        plan_ref=workspace_plan_ref(plan),
        provider_ref=workspace_provider_ref(descriptor),
        repository=plan.source_baseline_ref.commit.repository,
        source_commit=plan.source_baseline_ref.commit,
        root="/tmp/workspace",
    )
    manifest = WorkspaceChangeManifest(
        instance_ref=instance,
        source_commit=instance.source_commit,
        entries=(),
    )
    expected_digest = "sha256:34310a29d98cfe1320ad7633586b934a46fc7d1c7fb5df49c914d9046f7c30f2"
    assert digest_workspace_change_manifest(manifest) == expected_digest
    assert workspace_change_manifest_ref(manifest).content_digest == expected_digest


def conformance_fixture(
    plan: WorkspacePlan,
    descriptor: WorkspaceProviderDescriptor,
    property_evidence: tuple[WorkspacePropertyEvidence, ...] | None = None,
    established_strength: ControlStrength | None = None,
) -> tuple[WorkspaceInstanceRef, WorkspaceConformanceFacts]:
    plan_ref = workspace_plan_ref(plan)
    provider_ref = workspace_provider_ref(descriptor)
    instance = WorkspaceInstanceRef(
        workspace_id="fixture-instance",
        plan_ref=plan_ref,
        provider_ref=provider_ref,
        repository=plan.source_baseline_ref.commit.repository,
        source_commit=plan.source_baseline_ref.commit,
        root="/tmp/workspace",
    )
    subject = WorkspaceEvidenceSubject(
        plan_ref=plan_ref, instance_ref=instance, provider_ref=provider_ref
    )
    if property_evidence is None:
        property_evidence = tuple(
            WorkspacePropertyEvidence(
                subject=subject,
                property_key=requirement.key,
                property=requirement.property,
                established_strength=established_strength or requirement.minimum_strength,
                status=RequirementStatus.SATISFIED,
                evidence_payload_digest="sha256:" + "7" * 64,
            )
            for requirement in plan.property_requirements
        )
    inspection = WorkspaceInspection(
        instance_ref=instance,
        inspected_at="2026-10-22T00:00:00Z",
        head_commit=instance.source_commit,
        tracked_changes=(),
        untracked_paths=(),
        provider_injected_paths=(),
        protected_asset_observations=(),
        property_evidence=property_evidence,
    )
    facts = WorkspaceConformanceFacts(
        evaluated_plan_ref=plan_ref,
        evaluated_instance_ref=instance,
        evaluated_provider_ref=provider_ref,
        work_packet_conformance_fact=WorkPacketConformanceFact(
            evaluated_work_packet_ref=plan.work_packet_ref,
            conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
        ),
        workspace_policy_fact=WorkspacePolicyFact(
            evaluated_ref=plan.workspace_policy_ref, status=RequirementStatus.SATISFIED
        ),
        role_contract_fact=RoleContractFact(
            evaluated_ref=plan.role_contract_ref, status=RequirementStatus.SATISFIED
        ),
        provider_descriptor_fact=WorkspaceProviderDescriptorFact(
            evaluated_ref=provider_ref, status=RequirementStatus.SATISFIED
        ),
        protected_authority_facts=(),
        initial_inspection=inspection,
        property_evidence=property_evidence,
        credential_evidence=(),
        resource_evidence=None,
        environment_provenance=WorkspaceEnvironmentProvenance(
            subject=subject,
            boundary_class=descriptor.boundary_class,
            backend_kind=descriptor.backend_kind,
            platform_key="test-platform",
            platform_version="1",
            image_digest=None,
            environment_payload_digest="sha256:" + "8" * 64,
        ),
        terminal_inspection=None,
        change_manifest=None,
        continuity_evidence=None,
        teardown_evidence=None,
    )
    return instance, facts


def test_property_conformance_distinguishes_missing_and_insufficient_evidence() -> None:
    plan, descriptor = make_plan()
    instance, facts = conformance_fixture(plan, descriptor)
    assert (
        evaluate_workspace_conformance(plan, instance, plan.provider_ref, facts).status
        is RequirementStatus.SATISFIED
    )

    missing = facts.model_copy(update={"property_evidence": ()})
    assert (
        evaluate_workspace_conformance(plan, instance, plan.provider_ref, missing).status
        is RequirementStatus.INDETERMINATE
    )

    stronger_plan = plan.model_copy(
        update={
            "property_requirements": (
                WorkspacePropertyRequirement(
                    key="exact-source",
                    property=WorkspaceProperty.EXACT_SOURCE_BASELINE,
                    minimum_strength=ControlStrength.MEDIATED,
                ),
            )
        }
    )
    stronger_instance, stronger_facts = conformance_fixture(
        stronger_plan, descriptor, established_strength=ControlStrength.DETECTIVE
    )
    result = evaluate_workspace_conformance(
        stronger_plan, stronger_instance, stronger_plan.provider_ref, stronger_facts
    )
    assert result.status is RequirementStatus.UNSATISFIED


def test_property_population_known_violations_are_unsatisfied() -> None:
    plan, descriptor = make_plan()
    instance, facts = conformance_fixture(plan, descriptor)
    evidence = facts.property_evidence[0]

    extra = facts.model_copy(
        update={"property_evidence": (evidence.model_copy(update={"property_key": "unexpected"}),)}
    )
    duplicate = facts.model_copy(update={"property_evidence": (evidence, evidence)})
    wrong_property = facts.model_copy(
        update={
            "property_evidence": (
                evidence.model_copy(update={"property": WorkspaceProperty.CLEAN_INITIAL_STATE}),
            )
        }
    )
    wrong_subject = facts.model_copy(
        update={
            "property_evidence": (
                evidence.model_copy(
                    update={"subject": evidence.subject.model_copy(update={"plan_ref": None})}
                ),
            )
        }
    )
    for malformed in (extra, duplicate, wrong_property, wrong_subject):
        result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, malformed)
        assert result.status is RequirementStatus.UNSATISFIED


def test_property_evidence_must_follow_canonical_requirement_order() -> None:
    plan, descriptor = make_plan()
    plan = plan.model_copy(
        update={
            "property_requirements": (
                plan.property_requirements[0],
                WorkspacePropertyRequirement(
                    key="second-property",
                    property=WorkspaceProperty.CLEAN_INITIAL_STATE,
                    minimum_strength=ControlStrength.DETECTIVE,
                ),
            )
        }
    )
    instance, facts = conformance_fixture(plan, descriptor)
    reordered = facts.model_copy(
        update={"property_evidence": tuple(reversed(facts.property_evidence))}
    )
    result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, reordered)
    assert result.status is RequirementStatus.UNSATISFIED


def test_plan_stable_identity_conflict_is_reported() -> None:
    plan, _ = make_plan()
    conflicting = plan.model_copy(
        update={
            "retention_policy": plan.retention_policy.model_copy(
                update={"max_retention_seconds": 60}
            )
        }
    )
    conflicts = evaluate_workspace_plan_identity_conflicts((plan, conflicting))
    assert len(conflicts) == 1
    assert conflicts[0].plan_key == plan.plan_key


def resolver_fixture() -> tuple[
    WorkPacket,
    WorkPacketRef,
    WorkspacePolicyDefinition,
    RoleContract,
    WorkspaceProviderDescriptor,
]:
    packet = make_work_packet()
    role = RoleContract(
        role_key="implementer",
        revision=1,
        role_class=RoleClass.IMPLEMENTER,
        allowed_actor_kinds=(ActorKind.AGENT,),
        allowed_actions=(RoleAction.CONTEXT_READ,),
        prohibited_actions=tuple(
            action for action in RoleAction if action is not RoleAction.CONTEXT_READ
        ),
        required_inputs=(RoleInputRequirement.AUTHORIZED_WORK_BASIS,),
        required_outputs=(RoleOutputRequirement.ENGINEERING_RESULT,),
        verification_asset_permissions=(VerificationAssetPermission.READ,),
        required_runtime_capabilities=(RuntimeCapability.EXECUTE,),
        required_assurance_properties=("RELAY_ACTOR_IDENTITY_BOUND",),
    )
    packet_values = packet.model_dump()
    packet_values.update(
        {
            "role_contract_ref": role_contract_ref(role),
            "workspace_policy_ref": None,
            "required_workspace_property_keys": ("exact-source",),
        }
    )
    packet = WorkPacket.model_validate(packet_values)
    policy = WorkspacePolicyDefinition(
        policy_key="workspace-read-only",
        policy_basis_ref=packet.policy_basis_ref,
        governance_profile_ref=None,
        property_requirements=(
            WorkspacePropertyRequirement(
                key="exact-source",
                property=WorkspaceProperty.EXACT_SOURCE_BASELINE,
                minimum_strength=ControlStrength.DETECTIVE,
            ),
            WorkspacePropertyRequirement(
                key="protected-control",
                property=WorkspaceProperty.PROTECTED_ASSET_CONTROL,
                minimum_strength=ControlStrength.DETECTIVE,
            ),
        ),
        filesystem_policy=FilesystemPolicy(
            default_access=FilesystemAccess.READ_ONLY,
            writable_prefixes=(),
            denied_prefixes=(),
        ),
        repository_metadata_policy=RepositoryMetadataPolicy(
            access=RepositoryMetadataAccess.READ_ONLY
        ),
        tool_policy=ToolPolicy(default_decision=ToolDecision.DENY, rules=()),
        shell_policy=ShellPolicy(mode=ShellMode.DENY),
        network_policy=NetworkPolicy(mode=NetworkMode.DENY_ALL, allowed_endpoints=()),
        external_side_effect_policy=ExternalSideEffectPolicy(
            mode=ExternalSideEffectMode.DENY_MUTATING_EFFECTS,
            allowed_effects=(),
        ),
        credential_policy=WorkspaceCredentialPolicy(grants=()),
        resource_limits=WorkspaceResourceLimits(),
        retention_policy=WorkspaceRetentionPolicy(mode=WorkspaceRetentionMode.DELETE_ON_TERMINAL),
        provider_injected_files=(),
    )
    packet_values = packet.model_dump()
    packet_values["workspace_policy_ref"] = workspace_policy_ref(policy)
    packet = WorkPacket.model_validate(packet_values)
    provider = WorkspaceProviderDescriptor(
        provider_id="fixture-provider",
        provider_version="1",
        backend_kind=WorkspaceBackendKind.OTHER,
        boundary_class=WorkspaceBoundaryClass.MEDIATED_PROCESS_BOUNDARY,
        property_capabilities=(
            WorkspaceProviderPropertyCapability(
                property=WorkspaceProperty.EXACT_SOURCE_BASELINE,
                maximum_strength=ControlStrength.DETECTIVE,
            ),
            WorkspaceProviderPropertyCapability(
                property=WorkspaceProperty.PROTECTED_ASSET_CONTROL,
                maximum_strength=ControlStrength.DETECTIVE,
            ),
        ),
        supported_shell_modes=(ShellMode.DENY,),
        supported_network_modes=(NetworkMode.DENY_ALL,),
        supported_external_side_effect_modes=(ExternalSideEffectMode.DENY_MUTATING_EFFECTS,),
        supported_credential_exposure_modes=(),
        supported_resource_dimensions=(),
        supported_repository_metadata_modes=(RepositoryMetadataAccess.READ_ONLY,),
        path_control_capabilities=(),
        provider_injected_file_capabilities=(),
    )
    return packet, work_packet_ref(packet), policy, role, provider


def test_plan_resolution_preserves_policy_added_requirements_and_no_authority_case() -> None:
    packet, packet_ref, policy, role, provider = resolver_fixture()
    conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    result = resolve_workspace_plan(
        packet,
        packet_ref,
        conformance,
        policy,
        role,
        (),
        provider,
        plan_key="workspace-plan",
        revision=1,
    )
    assert result.status is RequirementStatus.SATISFIED
    assert result.plan is not None
    assert result.plan.packet_required_property_keys == packet.required_workspace_property_keys
    assert result.plan.property_requirements == policy.property_requirements
    assert tuple(item.key for item in result.plan.property_requirements) == (
        "exact-source",
        "protected-control",
    )
    assert result.plan.protected_asset_bindings[0].separate_authority_ref is None


def test_plan_resolution_requires_workspace_policy_reference() -> None:
    packet, packet_ref, policy, role, provider = resolver_fixture()
    packet_values = packet.model_dump()
    packet_values["workspace_policy_ref"] = None
    packet_without_policy = WorkPacket.model_validate(packet_values)
    packet_without_policy_ref = work_packet_ref(packet_without_policy)
    conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_without_policy_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    result = resolve_workspace_plan(
        packet_without_policy,
        packet_without_policy_ref,
        conformance,
        policy,
        role,
        (),
        provider,
        plan_key="workspace-plan",
        revision=1,
    )
    assert result.status is RequirementStatus.UNSATISFIED
    assert result.plan is None
    assert WorkspaceReason.WORKSPACE_POLICY_REQUIRED in result.reasons


def test_protected_permission_does_not_promote_read_to_modify() -> None:
    packet, _, policy, role, provider = resolver_fixture()
    values = packet.model_dump()
    values["protected_verification_requirements"] = (
        packet.protected_verification_requirements[0].model_copy(
            update={"required_operation": VerificationAssetPermission.MODIFY}
        ),
    )
    modified_packet = WorkPacket.model_validate(values)
    modified_ref = work_packet_ref(modified_packet)
    conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=modified_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    result = resolve_workspace_plan(
        modified_packet,
        modified_ref,
        conformance,
        policy,
        role,
        (),
        provider,
        plan_key="workspace-plan",
        revision=1,
    )
    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.ROLE_PERMISSION_INSUFFICIENT in result.reasons
