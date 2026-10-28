"""Pure workspace resolution and conformance evaluation tests."""

from __future__ import annotations

import pytest
from test_work_packet_models import packet as make_work_packet

from relay_engine.agent_runtime import CredentialRef, RuntimeCapability
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
    protected_verification_requirement_ref,
    resolve_workspace_plan,
    workspace_plan_ref,
    workspace_policy_ref,
    workspace_provider_ref,
)
from relay_engine.execution_workspace.models import (
    ControlStrength,
    CredentialExposureMode,
    ExternalSideEffectMode,
    ExternalSideEffectPolicy,
    FilesystemAccess,
    FilesystemPolicy,
    NetworkEndpoint,
    NetworkMode,
    NetworkPolicy,
    ProtectedAssetObservation,
    ProtectedVerificationAuthorityFact,
    RepositoryMetadataAccess,
    RepositoryMetadataPolicy,
    RepositoryPathPrefix,
    RoleContractFact,
    ShellMode,
    ShellPolicy,
    ToolDecision,
    ToolPolicy,
    ToolRule,
    WorkPacketConformanceFact,
    WorkspaceBackendKind,
    WorkspaceBoundaryClass,
    WorkspaceChangeEntry,
    WorkspaceChangeManifest,
    WorkspaceConformanceFacts,
    WorkspaceCredentialEvidence,
    WorkspaceCredentialGrant,
    WorkspaceCredentialPolicy,
    WorkspaceEntryKind,
    WorkspaceEntryState,
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
    WorkspaceResourceEvidence,
    WorkspaceResourceLimits,
    WorkspaceRetentionMode,
    WorkspaceRetentionPolicy,
    WorkspaceTeardownEvidence,
    WorkspaceTerminalDisposition,
    WorkspaceToolRef,
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
    AuthorityBasisRef,
    AuthorityReferenceType,
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


def test_trusted_local_preflight_leaves_runtime_controls_with_runtime() -> None:
    plan, descriptor = make_plan()
    runtime_properties = (
        WorkspaceProperty.TOOL_EXPOSURE_CONTROL,
        WorkspaceProperty.NETWORK_REACHABILITY_CONTROL,
        WorkspaceProperty.CREDENTIAL_EXPOSURE_CONTROL,
        WorkspaceProperty.RESOURCE_LIMIT_CONTROL,
    )
    requirements = plan.property_requirements + tuple(
        WorkspacePropertyRequirement(
            key=f"runtime-control-{index}",
            property=property_key,
            minimum_strength=ControlStrength.MEDIATED,
        )
        for index, property_key in enumerate(runtime_properties, start=1)
    )
    runtime_descriptor = descriptor.model_copy(
        update={
            "supported_shell_modes": (),
            "supported_network_modes": (),
            "supported_external_side_effect_modes": (),
            "supported_credential_exposure_modes": (),
            "supported_resource_dimensions": (),
        }
    )
    runtime_controls_plan = plan.model_copy(
        update={
            "property_requirements": requirements,
            "provider_ref": workspace_provider_ref(runtime_descriptor),
        }
    )

    assert (
        evaluate_workspace_preflight(
            runtime_controls_plan, runtime_descriptor, trusted_local=True
        ).status
        is RequirementStatus.SATISFIED
    )
    assert (
        evaluate_workspace_preflight(runtime_controls_plan, runtime_descriptor).status
        is RequirementStatus.UNSATISFIED
    )

    boundary_requirement = WorkspacePropertyRequirement(
        key="runtime-control-boundary",
        property=WorkspaceProperty.TOOL_EXPOSURE_CONTROL,
        minimum_strength=ControlStrength.BOUNDARY_ENFORCED,
    )
    boundary_plan = runtime_controls_plan.model_copy(
        update={"property_requirements": (*requirements, boundary_requirement)}
    )
    assert (
        evaluate_workspace_preflight(boundary_plan, runtime_descriptor, trusted_local=True).status
        is RequirementStatus.UNSATISFIED
    )


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


def terminal_change_facts(
    plan: WorkspacePlan,
    descriptor: WorkspaceProviderDescriptor,
    path: str,
) -> tuple[WorkspaceInstanceRef, WorkspaceConformanceFacts]:
    instance, facts = conformance_fixture(plan, descriptor)
    before = WorkspaceEntryState(
        kind=WorkspaceEntryKind.REGULAR_FILE,
        content_digest="sha256:" + "1" * 64,
        symlink_target_digest=None,
        executable=False,
    )
    after = WorkspaceEntryState(
        kind=WorkspaceEntryKind.REGULAR_FILE,
        content_digest="sha256:" + "2" * 64,
        symlink_target_digest=None,
        executable=False,
    )
    terminal_inspection = facts.initial_inspection.model_copy(update={"tracked_changes": (path,)})
    manifest = WorkspaceChangeManifest(
        instance_ref=instance,
        source_commit=instance.source_commit,
        entries=(WorkspaceChangeEntry(path=path, before=before, after=after),),
    )
    return instance, facts.model_copy(
        update={
            "terminal_inspection": terminal_inspection,
            "change_manifest": manifest,
            "teardown_evidence": WorkspaceTeardownEvidence(
                subject=facts.environment_provenance.subject,
                disposition=WorkspaceTerminalDisposition.DELETED,
                credential_cleanup_status=RequirementStatus.SATISFIED,
                workspace_absence_status=RequirementStatus.SATISFIED,
                retained_until=None,
                evidence_payload_digest="sha256:" + "f" * 64,
            ),
        }
    )


@pytest.mark.parametrize(
    ("policy", "changed_path", "expected_status"),
    (
        (
            FilesystemPolicy(
                default_access=FilesystemAccess.READ_WRITE,
                writable_prefixes=(),
                denied_prefixes=(RepositoryPathPrefix(value="tracked.txt"),),
            ),
            "tracked.txt",
            RequirementStatus.UNSATISFIED,
        ),
        (
            FilesystemPolicy(
                default_access=FilesystemAccess.READ_ONLY,
                writable_prefixes=(),
                denied_prefixes=(),
            ),
            "tracked.txt",
            RequirementStatus.UNSATISFIED,
        ),
        (
            FilesystemPolicy(
                default_access=FilesystemAccess.READ_ONLY,
                writable_prefixes=(RepositoryPathPrefix(value="allowed"),),
                denied_prefixes=(),
            ),
            "tracked.txt",
            RequirementStatus.UNSATISFIED,
        ),
        (
            FilesystemPolicy(
                default_access=FilesystemAccess.READ_ONLY,
                writable_prefixes=(RepositoryPathPrefix(value="tracked.txt"),),
                denied_prefixes=(),
            ),
            "tracked.txt",
            RequirementStatus.SATISFIED,
        ),
    ),
)
def test_terminal_changes_obey_denied_read_only_out_of_scope_and_writable_paths(
    policy: FilesystemPolicy,
    changed_path: str,
    expected_status: RequirementStatus,
) -> None:
    plan, descriptor = make_plan()
    plan = plan.model_copy(update={"filesystem_policy": policy})
    instance, facts = terminal_change_facts(plan, descriptor, changed_path)

    result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, facts, terminal=True)

    assert result.status is expected_status
    if expected_status is RequirementStatus.UNSATISFIED:
        assert WorkspaceReason.CHANGE_OUT_OF_SCOPE in result.reasons


def test_required_symlink_escape_evidence_missing_is_indeterminate() -> None:
    plan, descriptor = make_plan()
    path_requirement = WorkspacePropertyRequirement(
        key="path-escape",
        property=WorkspaceProperty.PATH_ESCAPE_CONTROL,
        minimum_strength=ControlStrength.DETECTIVE,
    )
    plan = plan.model_copy(
        update={"property_requirements": (*plan.property_requirements, path_requirement)}
    )
    instance, facts = conformance_fixture(plan, descriptor)
    incomplete = facts.model_copy(update={"property_evidence": facts.property_evidence[:1]})

    result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, incomplete)

    assert result.status is RequirementStatus.INDETERMINATE
    assert WorkspaceReason.PROPERTY_EVIDENCE_MISSING in result.reasons


@pytest.mark.parametrize(
    ("plan_update", "provider_update", "expected_reason"),
    (
        (
            {"shell_policy": ShellPolicy(mode=ShellMode.UNRESTRICTED_WITHIN_DECLARED_BOUNDARY)},
            {"supported_shell_modes": (ShellMode.DENY,)},
            WorkspaceReason.SHELL_POLICY_UNSUPPORTED,
        ),
        (
            {
                "network_policy": NetworkPolicy(
                    mode=NetworkMode.ALLOWLIST,
                    allowed_endpoints=(
                        NetworkEndpoint(scheme="https", host="example.invalid", port=443),
                    ),
                )
            },
            {"supported_network_modes": (NetworkMode.DENY_ALL,)},
            WorkspaceReason.NETWORK_POLICY_UNSUPPORTED,
        ),
        (
            {
                "external_side_effect_policy": ExternalSideEffectPolicy(
                    mode=ExternalSideEffectMode.UNRESTRICTED,
                    allowed_effects=(),
                )
            },
            {
                "supported_external_side_effect_modes": (
                    ExternalSideEffectMode.DENY_MUTATING_EFFECTS,
                )
            },
            WorkspaceReason.EXTERNAL_SIDE_EFFECT_POLICY_UNSUPPORTED,
        ),
    ),
)
def test_preflight_fails_closed_for_unsupported_shell_network_and_effect_modes(
    plan_update: dict[str, object],
    provider_update: dict[str, object],
    expected_reason: WorkspaceReason,
) -> None:
    plan, descriptor = make_plan()
    descriptor = descriptor.model_copy(update=provider_update)
    plan = plan.model_copy(
        update={"provider_ref": workspace_provider_ref(descriptor), **plan_update}
    )

    result = evaluate_workspace_preflight(plan, descriptor)

    assert result.status is RequirementStatus.UNSATISFIED
    assert expected_reason in result.reasons


def test_tool_policy_keeps_unknown_tools_denied_by_default() -> None:
    denied_tool = WorkspaceToolRef(
        tool_key="external-write",
        tool_definition_digest="sha256:" + "e" * 64,
    )
    policy = ToolPolicy(
        default_decision=ToolDecision.DENY,
        rules=(ToolRule(tool_ref=denied_tool, decision=ToolDecision.DENY),),
    )

    assert policy.default_decision is ToolDecision.DENY
    assert policy.rules[0].tool_ref == denied_tool
    assert policy.rules[0].decision is ToolDecision.DENY


def test_preflight_rejects_unavailable_credential_and_resource_controls() -> None:
    plan, descriptor = make_plan()
    grant = WorkspaceCredentialGrant(
        credential_ref=CredentialRef(credential_id="credential-test"),
        exposure_mode=CredentialExposureMode.ENVIRONMENT,
        exposure_key="TEST_CREDENTIAL",
    )
    plan = plan.model_copy(
        update={
            "workspace_credential_grants": (grant,),
            "resource_limits": WorkspaceResourceLimits(max_memory_bytes=100),
        }
    )

    result = evaluate_workspace_preflight(plan, descriptor)

    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.CREDENTIAL_EXPOSURE_UNSUPPORTED in result.reasons
    assert WorkspaceReason.RESOURCE_LIMIT_UNSUPPORTED in result.reasons


def test_credential_resolution_and_exposure_fail_closed_without_secret_values() -> None:
    packet, packet_ref, policy, role, provider = resolver_fixture()
    credential = CredentialRef(credential_id="credential-test")
    grant = WorkspaceCredentialGrant(
        credential_ref=credential,
        exposure_mode=CredentialExposureMode.ENVIRONMENT,
        exposure_key="TEST_CREDENTIAL",
    )
    undeclared_policy = policy.model_copy(
        update={
            "credential_policy": WorkspaceCredentialPolicy(grants=(grant,)),
        }
    )
    conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    undeclared = resolve_workspace_plan(
        packet,
        packet_ref,
        conformance,
        undeclared_policy,
        role,
        (),
        provider,
        plan_key="workspace-plan",
        revision=1,
    )
    assert undeclared.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.CREDENTIAL_NOT_DECLARED in undeclared.reasons

    packet_values = packet.model_dump()
    packet_values["credential_refs"] = (credential,)
    packet_with_credential = WorkPacket.model_validate(packet_values)
    packet_with_credential_ref = work_packet_ref(packet_with_credential)
    packet_conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_with_credential_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    resolved = resolve_workspace_plan(
        packet_with_credential,
        packet_with_credential_ref,
        packet_conformance,
        policy,
        role,
        (),
        provider,
        plan_key="workspace-plan",
        revision=1,
    )
    assert resolved.status is RequirementStatus.SATISFIED
    assert resolved.plan is not None
    assert resolved.plan.workspace_credential_grants == ()
    instance, facts = conformance_fixture(resolved.plan, provider)
    unexpected = WorkspaceCredentialEvidence(
        subject=facts.environment_provenance.subject,
        credential_ref=credential,
        exposure_mode=CredentialExposureMode.ENVIRONMENT,
        status=RequirementStatus.SATISFIED,
        revoked_or_removed=RequirementStatus.SATISFIED,
    )
    exposed = facts.model_copy(update={"credential_evidence": (unexpected,)})
    result = evaluate_workspace_conformance(
        resolved.plan, instance, resolved.plan.provider_ref, exposed
    )
    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.UNEXPECTED_CREDENTIAL_EXPOSURE in result.reasons
    assert set(CredentialRef.model_fields) == {"schema_version", "credential_id"}
    assert not any(
        "secret" in field_name.lower() for field_name in WorkspaceCredentialEvidence.model_fields
    )


def test_required_credential_exposure_missing_is_indeterminate() -> None:
    plan, descriptor = make_plan()
    grant = WorkspaceCredentialGrant(
        credential_ref=CredentialRef(credential_id="credential-test"),
        exposure_mode=CredentialExposureMode.ENVIRONMENT,
        exposure_key="TEST_CREDENTIAL",
    )
    plan = plan.model_copy(update={"workspace_credential_grants": (grant,)})
    instance, facts = conformance_fixture(plan, descriptor)

    result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, facts)

    assert result.status is RequirementStatus.INDETERMINATE


@pytest.mark.parametrize(
    ("resource_evidence", "expected_status", "expected_reason"),
    (
        (None, RequirementStatus.INDETERMINATE, None),
        (
            "weaker",
            RequirementStatus.UNSATISFIED,
            WorkspaceReason.RESOURCE_LIMIT_MISMATCH,
        ),
    ),
)
def test_resource_limit_evidence_is_exact_and_required(
    resource_evidence: WorkspaceResourceEvidence | str | None,
    expected_status: RequirementStatus,
    expected_reason: WorkspaceReason | None,
) -> None:
    plan, descriptor = make_plan()
    plan = plan.model_copy(
        update={
            "resource_limits": WorkspaceResourceLimits(max_memory_bytes=100),
        }
    )
    instance, facts = conformance_fixture(plan, descriptor)
    if resource_evidence == "weaker":
        resource_evidence = WorkspaceResourceEvidence(
            subject=facts.environment_provenance.subject,
            memory_limit_bytes=101,
            disk_limit_bytes=None,
            process_limit=None,
            cpu_seconds_limit=None,
            open_files_limit=None,
            status=RequirementStatus.SATISFIED,
            evidence_payload_digest="sha256:" + "9" * 64,
        )
    facts = facts.model_copy(update={"resource_evidence": resource_evidence})

    result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, facts)

    assert result.status is expected_status
    if expected_reason is not None:
        assert expected_reason in result.reasons


def test_no_resource_limit_does_not_require_synthetic_resource_evidence() -> None:
    plan, descriptor = make_plan()
    instance, facts = conformance_fixture(plan, descriptor)

    result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, facts)

    assert result.status is RequirementStatus.SATISFIED


def test_exact_subject_mismatch_families_fail_closed() -> None:
    plan, descriptor = make_plan()
    instance, facts = conformance_fixture(plan, descriptor)
    wrong_instance = instance.model_copy(update={"root": "/tmp/other-workspace"})
    wrong_subject = WorkspaceEvidenceSubject(
        plan_ref=wrong_instance.plan_ref,
        instance_ref=wrong_instance,
        provider_ref=wrong_instance.provider_ref,
    )
    wrong_plan_ref = plan.work_packet_ref.model_copy(update={"packet_key": "other-packet"})
    mismatches = (
        facts.model_copy(
            update={
                "work_packet_conformance_fact": facts.work_packet_conformance_fact.model_copy(
                    update={"evaluated_work_packet_ref": wrong_plan_ref}
                )
            }
        ),
        facts.model_copy(
            update={
                "workspace_policy_fact": facts.workspace_policy_fact.model_copy(
                    update={
                        "evaluated_ref": facts.workspace_policy_fact.evaluated_ref.model_copy(
                            update={"policy_key": "other-policy"}
                        )
                    }
                )
            }
        ),
        facts.model_copy(
            update={
                "role_contract_fact": facts.role_contract_fact.model_copy(
                    update={
                        "evaluated_ref": facts.role_contract_fact.evaluated_ref.model_copy(
                            update={"role_key": "other-role"}
                        )
                    }
                )
            }
        ),
        facts.model_copy(
            update={
                "provider_descriptor_fact": facts.provider_descriptor_fact.model_copy(
                    update={
                        "evaluated_ref": facts.provider_descriptor_fact.evaluated_ref.model_copy(
                            update={"provider_id": "other-provider"}
                        )
                    }
                )
            }
        ),
        facts.model_copy(update={"evaluated_instance_ref": wrong_instance}),
        facts.model_copy(
            update={
                "environment_provenance": facts.environment_provenance.model_copy(
                    update={"subject": wrong_subject}
                )
            }
        ),
    )

    for mismatched_facts in mismatches:
        result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, mismatched_facts)
        assert result.status is RequirementStatus.UNSATISFIED
        assert WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH in result.reasons or (
            WorkspaceReason.WORK_PACKET_REF_MISMATCH in result.reasons
            or WorkspaceReason.WORKSPACE_POLICY_REF_MISMATCH in result.reasons
            or WorkspaceReason.ROLE_CONTRACT_REF_MISMATCH in result.reasons
            or WorkspaceReason.PROVIDER_REF_MISMATCH in result.reasons
        )

    credential = CredentialRef(credential_id="credential-test")
    credential_plan = plan.model_copy(
        update={
            "workspace_credential_grants": (
                WorkspaceCredentialGrant(
                    credential_ref=credential,
                    exposure_mode=CredentialExposureMode.ENVIRONMENT,
                    exposure_key="TEST_CREDENTIAL",
                ),
            )
        }
    )
    credential_instance, credential_facts = conformance_fixture(credential_plan, descriptor)
    credential_facts = credential_facts.model_copy(
        update={
            "credential_evidence": (
                WorkspaceCredentialEvidence(
                    subject=wrong_subject,
                    credential_ref=credential,
                    exposure_mode=CredentialExposureMode.ENVIRONMENT,
                    status=RequirementStatus.SATISFIED,
                    revoked_or_removed=RequirementStatus.SATISFIED,
                ),
            )
        }
    )
    credential_result = evaluate_workspace_conformance(
        credential_plan,
        credential_instance,
        credential_plan.provider_ref,
        credential_facts,
    )
    assert credential_result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH in credential_result.reasons

    resource_plan = plan.model_copy(
        update={"resource_limits": WorkspaceResourceLimits(max_memory_bytes=100)}
    )
    resource_instance, resource_facts = conformance_fixture(resource_plan, descriptor)
    resource_facts = resource_facts.model_copy(
        update={
            "resource_evidence": WorkspaceResourceEvidence(
                subject=wrong_subject,
                memory_limit_bytes=100,
                disk_limit_bytes=None,
                process_limit=None,
                cpu_seconds_limit=None,
                open_files_limit=None,
                status=RequirementStatus.SATISFIED,
                evidence_payload_digest="sha256:" + "a" * 64,
            )
        }
    )
    resource_result = evaluate_workspace_conformance(
        resource_plan, resource_instance, resource_plan.provider_ref, resource_facts
    )
    assert resource_result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.EVIDENCE_SUBJECT_MISMATCH in resource_result.reasons


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


def resolved_plan_for_protected_operation(
    operation: VerificationAssetPermission,
) -> tuple[WorkspacePlan, WorkspaceProviderDescriptor]:
    packet, _, policy, role, provider = resolver_fixture()
    role = role.model_copy(
        update={"verification_asset_permissions": tuple(VerificationAssetPermission)}
    )
    policy = policy.model_copy(
        update={
            "filesystem_policy": FilesystemPolicy(
                default_access=FilesystemAccess.READ_WRITE,
                writable_prefixes=(),
                denied_prefixes=(),
            )
        }
    )
    packet_values = packet.model_dump()
    packet_values.update(
        {
            "role_contract_ref": role_contract_ref(role),
            "workspace_policy_ref": workspace_policy_ref(policy),
            "protected_verification_requirements": (
                packet.protected_verification_requirements[0].model_copy(
                    update={"required_operation": operation}
                ),
            ),
        }
    )
    packet = WorkPacket.model_validate(packet_values)
    packet_ref = work_packet_ref(packet)
    conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )

    resolution = resolve_workspace_plan(
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

    assert resolution.status is RequirementStatus.SATISFIED
    assert resolution.plan is not None
    return resolution.plan, provider


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


@pytest.mark.parametrize(
    ("operation", "ordinary_access"),
    (
        (VerificationAssetPermission.MODIFY, FilesystemAccess.READ_ONLY),
        (VerificationAssetPermission.MODIFY, FilesystemAccess.DENY),
        (VerificationAssetPermission.CREATE, FilesystemAccess.READ_ONLY),
        (VerificationAssetPermission.CREATE, FilesystemAccess.DENY),
    ),
)
def test_protected_write_requires_ordinary_read_write_access(
    operation: VerificationAssetPermission,
    ordinary_access: FilesystemAccess,
) -> None:
    packet, _, policy, role, provider = resolver_fixture()
    role = role.model_copy(
        update={"verification_asset_permissions": tuple(VerificationAssetPermission)}
    )
    packet_values = packet.model_dump()
    packet_values["role_contract_ref"] = role_contract_ref(role)
    packet_values["protected_verification_requirements"] = (
        packet.protected_verification_requirements[0].model_copy(
            update={"required_operation": operation}
        ),
    )
    packet = WorkPacket.model_validate(packet_values)
    packet_ref = work_packet_ref(packet)
    policy = policy.model_copy(
        update={
            "filesystem_policy": FilesystemPolicy(
                default_access=ordinary_access,
                writable_prefixes=(),
                denied_prefixes=(),
            )
        }
    )
    packet_values = packet.model_dump()
    packet_values["workspace_policy_ref"] = workspace_policy_ref(policy)
    packet = WorkPacket.model_validate(packet_values)
    packet_ref = work_packet_ref(packet)
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

    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.FILESYSTEM_SCOPE_VIOLATION in result.reasons
    assert result.plan is None


def test_protected_read_access_only_narrows_ordinary_read_write_policy() -> None:
    packet, packet_ref, policy, role, provider = resolver_fixture()
    policy = policy.model_copy(
        update={
            "filesystem_policy": FilesystemPolicy(
                default_access=FilesystemAccess.READ_WRITE,
                writable_prefixes=(),
                denied_prefixes=(),
            )
        }
    )
    packet_values = packet.model_dump()
    packet_values["workspace_policy_ref"] = workspace_policy_ref(policy)
    packet = WorkPacket.model_validate(packet_values)
    packet_ref = work_packet_ref(packet)
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
    assert result.plan.protected_asset_bindings[0].physical_access is FilesystemAccess.READ_ONLY


def test_protected_authority_is_required_only_when_exact_ref_is_present() -> None:
    packet, packet_ref, policy, role, provider = resolver_fixture()
    authority = AuthorityBasisRef(
        authority_type=AuthorityReferenceType.HUMAN_GOVERNANCE_RECORD,
        authority_key="protected-mutation",
        record_digest="sha256:" + "a" * 64,
        subject_digest=None,
    )
    packet_values = packet.model_dump()
    packet_values["protected_verification_requirements"] = (
        packet.protected_verification_requirements[0].model_copy(
            update={"separate_authority_ref": authority}
        ),
    )
    packet = WorkPacket.model_validate(packet_values)
    packet_ref = work_packet_ref(packet)
    conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )

    missing = resolve_workspace_plan(
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
    assert missing.status is RequirementStatus.INDETERMINATE
    assert WorkspaceReason.PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED in missing.reasons

    requirement_ref = protected_verification_requirement_ref(
        packet.protected_verification_requirements[0]
    )
    authority_fact = ProtectedVerificationAuthorityFact(
        evaluated_requirement_ref=requirement_ref,
        evaluated_authority_ref=authority,
        status=RequirementStatus.SATISFIED,
    )
    resolved = resolve_workspace_plan(
        packet,
        packet_ref,
        conformance,
        policy,
        role,
        (authority_fact,),
        provider,
        plan_key="workspace-plan",
        revision=1,
    )
    assert resolved.status is RequirementStatus.SATISFIED
    assert resolved.plan is not None
    instance, facts = conformance_fixture(resolved.plan, provider)
    binding = resolved.plan.protected_asset_bindings[0]
    state = WorkspaceEntryState(
        kind=WorkspaceEntryKind.REGULAR_FILE,
        content_digest="sha256:" + "b" * 64,
        symlink_target_digest=None,
        executable=False,
    )
    observation = ProtectedAssetObservation(
        requirement_ref=binding.requirement_ref,
        workspace_path=binding.workspace_path,
        state=state,
    )
    initial = facts.initial_inspection.model_copy(
        update={"protected_asset_observations": (observation,)}
    )
    terminal_inspection = initial.model_copy()
    manifest = WorkspaceChangeManifest(
        instance_ref=instance,
        source_commit=instance.source_commit,
        entries=(),
    )
    complete = facts.model_copy(
        update={
            "protected_authority_facts": (authority_fact,),
            "initial_inspection": initial,
            "terminal_inspection": terminal_inspection,
            "change_manifest": manifest,
            "teardown_evidence": WorkspaceTeardownEvidence(
                subject=facts.environment_provenance.subject,
                disposition=WorkspaceTerminalDisposition.DELETED,
                credential_cleanup_status=RequirementStatus.SATISFIED,
                workspace_absence_status=RequirementStatus.SATISFIED,
                retained_until=None,
                evidence_payload_digest="sha256:" + "f" * 64,
            ),
        }
    )
    result = evaluate_workspace_conformance(
        resolved.plan, instance, resolved.plan.provider_ref, complete, terminal=True
    )
    assert result.status is RequirementStatus.SATISFIED


def test_read_protected_asset_mutation_is_unsatisfied() -> None:
    packet, packet_ref, policy, role, provider = resolver_fixture()
    conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    resolved = resolve_workspace_plan(
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
    assert resolved.plan is not None
    plan = resolved.plan
    instance, facts = conformance_fixture(plan, provider)
    binding = plan.protected_asset_bindings[0]
    before = WorkspaceEntryState(
        kind=WorkspaceEntryKind.REGULAR_FILE,
        content_digest="sha256:" + "c" * 64,
        symlink_target_digest=None,
        executable=False,
    )
    after = before.model_copy(update={"content_digest": "sha256:" + "d" * 64})
    initial_observation = ProtectedAssetObservation(
        requirement_ref=binding.requirement_ref,
        workspace_path=binding.workspace_path,
        state=before,
    )
    terminal_observation = initial_observation.model_copy(update={"state": after})
    initial = facts.initial_inspection.model_copy(
        update={"protected_asset_observations": (initial_observation,)}
    )
    terminal_inspection = initial.model_copy(
        update={
            "tracked_changes": (binding.workspace_path,),
            "protected_asset_observations": (terminal_observation,),
        }
    )
    manifest = WorkspaceChangeManifest(
        instance_ref=instance,
        source_commit=instance.source_commit,
        entries=(
            WorkspaceChangeEntry(
                path=binding.workspace_path,
                before=before,
                after=after,
            ),
        ),
    )
    terminal_facts = facts.model_copy(
        update={
            "initial_inspection": initial,
            "terminal_inspection": terminal_inspection,
            "change_manifest": manifest,
        }
    )

    result = evaluate_workspace_conformance(
        plan, instance, plan.provider_ref, terminal_facts, terminal=True
    )

    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.PROTECTED_ASSET_MUTATED in result.reasons


def test_protected_control_key_and_strength_are_enforced() -> None:
    packet, packet_ref, policy, role, provider = resolver_fixture()
    conformance = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_ref,
        conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    resolved = resolve_workspace_plan(
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
    assert resolved.plan is not None
    bad_binding = resolved.plan.protected_asset_bindings[0].model_copy(
        update={"control_property_key": "unknown-control"}
    )
    missing_key_plan = resolved.plan.model_copy(update={"protected_asset_bindings": (bad_binding,)})
    instance, facts = conformance_fixture(missing_key_plan, provider)
    missing_key_result = evaluate_workspace_conformance(
        missing_key_plan, instance, missing_key_plan.provider_ref, facts
    )
    assert missing_key_result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.REQUIRED_WORKSPACE_PROPERTY_UNKNOWN in missing_key_result.reasons

    stronger_properties = tuple(
        requirement.model_copy(update={"minimum_strength": ControlStrength.MEDIATED})
        if requirement.property is WorkspaceProperty.PROTECTED_ASSET_CONTROL
        else requirement
        for requirement in resolved.plan.property_requirements
    )
    weak_plan = resolved.plan.model_copy(update={"property_requirements": stronger_properties})
    weak_instance, weak_facts = conformance_fixture(
        weak_plan, provider, established_strength=ControlStrength.DETECTIVE
    )
    weak_result = evaluate_workspace_conformance(
        weak_plan, weak_instance, weak_plan.provider_ref, weak_facts
    )
    assert weak_result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.CONTROL_STRENGTH_INSUFFICIENT in weak_result.reasons


@pytest.mark.parametrize(
    ("operation", "physical_access"),
    (
        (VerificationAssetPermission.MODIFY, FilesystemAccess.READ_ONLY),
        (VerificationAssetPermission.MODIFY, FilesystemAccess.DENY),
        (VerificationAssetPermission.CREATE, FilesystemAccess.READ_ONLY),
        (VerificationAssetPermission.CREATE, FilesystemAccess.DENY),
        (VerificationAssetPermission.READ, FilesystemAccess.DENY),
        (VerificationAssetPermission.EXECUTE, FilesystemAccess.DENY),
        (VerificationAssetPermission.EVALUATE, FilesystemAccess.DENY),
    ),
)
def test_final_conformance_rejects_incompatible_protected_physical_access(
    operation: VerificationAssetPermission,
    physical_access: FilesystemAccess,
) -> None:
    plan, descriptor = resolved_plan_for_protected_operation(operation)
    binding = plan.protected_asset_bindings[0].model_copy(
        update={"physical_access": physical_access}
    )
    plan_values = plan.model_dump(mode="python")
    plan_values["protected_asset_bindings"] = (binding.model_dump(mode="python"),)
    plan = WorkspacePlan.model_validate(plan_values)
    instance, facts = conformance_fixture(plan, descriptor)

    result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, facts)

    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.FILESYSTEM_SCOPE_VIOLATION in result.reasons


@pytest.mark.parametrize(
    "operation",
    (
        VerificationAssetPermission.PROPOSE_MUTATION,
        VerificationAssetPermission.APPROVE_MUTATION,
    ),
)
def test_proposal_and_approval_operations_do_not_require_physical_write_access(
    operation: VerificationAssetPermission,
) -> None:
    plan, descriptor = resolved_plan_for_protected_operation(operation)
    binding = plan.protected_asset_bindings[0].model_copy(
        update={"physical_access": FilesystemAccess.DENY}
    )
    plan_values = plan.model_dump(mode="python")
    plan_values["protected_asset_bindings"] = (binding.model_dump(mode="python"),)
    plan = WorkspacePlan.model_validate(plan_values)
    instance, facts = conformance_fixture(plan, descriptor)

    result = evaluate_workspace_conformance(plan, instance, plan.provider_ref, facts)

    assert WorkspaceReason.FILESYSTEM_SCOPE_VIOLATION not in result.reasons
