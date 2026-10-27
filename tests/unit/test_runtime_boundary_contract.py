"""Deterministic identity and fail-closed tests for runtime-boundary contracts."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import httpx
import pytest
from pydantic import ValidationError
from test_execution_workspace_evaluation import make_plan

from relay_engine.agent_runtime.boundary import (
    RuntimeEvidenceCompleteness,
    RuntimeLaunchSubject,
    RuntimePermissionAttestation,
    RuntimePlacementAttestationRef,
    RuntimeRequestV2,
    build_runtime_request_v2,
    digest_runtime_permission_attestation,
    digest_runtime_request_v2,
)
from relay_engine.agent_runtime.errors import AgentRuntimeError
from relay_engine.agent_runtime.models import (
    RuntimeExecutionBasis,
    RuntimeExecutionRequest,
    RuntimeInputPayload,
    RuntimePermissionProfileRef,
    RuntimeSelection,
    RuntimeSessionBinding,
    RuntimeSessionRef,
    RuntimeWorkspaceAttachment,
    digest_execution_basis,
)
from relay_engine.agent_runtime.opencode import OpenCodePermissionProfile, OpenCodeRuntime
from relay_engine.coding_execution.evaluation import evaluate_runtime_boundary_evidence
from relay_engine.coding_execution.models import AdmissionStatus, RuntimePermissionEvidence
from relay_engine.domain import CommitRef, RepositoryRef
from relay_engine.execution_workspace.boundary import (
    PlacementAttesterRef,
    RuntimePlacementAttestation,
    RuntimePlacementContinuityEvidence,
    WorkspaceBoundaryRef,
    placement_attestation_matches_boundary,
)
from relay_engine.execution_workspace.evaluation import workspace_plan_ref, workspace_provider_ref
from relay_engine.execution_workspace.models import WorkspaceInstanceRef
from relay_engine.role_contracts import RequirementStatus

_DIGEST = "sha256:" + "1" * 64
_NOW = datetime(2026, 10, 27, tzinfo=UTC)


def runtime_request() -> RuntimeExecutionRequest:
    repository = RepositoryRef(
        id="repo_00000000-0000-0000-0000-000000000099",
        host="local",
        path="fixture",
    )
    basis = RuntimeExecutionBasis(
        execution_id="exec_018f47c1-7b2c-7abc-8def-123456789011",
        slice_id="slc_018f47c1-7b2c-7abc-8def-123456789012",
        source_baseline_id="base_018f47c1-7b2c-7abc-8def-123456789013",
        workspace=RuntimeWorkspaceAttachment(
            workspace_id="workspace-boundary",
            root="/tmp/relay-boundary",
            repository=repository,
            source_commit=CommitRef(repository=repository, sha="a" * 40),
        ),
        input_payload=RuntimeInputPayload(
            text="bounded deterministic prompt",
            payload_digest=_DIGEST,
        ),
        runtime_selection=RuntimeSelection(
            runtime_id="opencode",
            requested_provider_id="provider-a",
            requested_model_id="model-a",
        ),
        permission_profile_ref=RuntimePermissionProfileRef(
            profile_id="profile-a",
            content_digest=_DIGEST,
        ),
    )
    return RuntimeExecutionRequest(basis=basis, request_digest=digest_execution_basis(basis))


def launch_subject(request: RuntimeExecutionRequest) -> RuntimeLaunchSubject:
    return RuntimeLaunchSubject(
        execution_id=request.basis.execution_id,
        intended_attempt_id="exec-018f47c1-7b2c-7abc-8def-123456789011",
        authority_candidate_digest=_DIGEST,
        human_grant_digest=_DIGEST,
        work_packet_ref_digest=_DIGEST,
        context_manifest_ref_digest=_DIGEST,
        workspace_plan_ref_digest=_DIGEST,
        workspace_instance_digest=_DIGEST,
        workspace_boundary_digest=_DIGEST,
        runtime_descriptor_digest=_DIGEST,
        runtime_id="opencode",
        runtime_version="0.0.0-beta-test",
        adapter_id="opencode",
        adapter_version="0.1.0",
        challenge_or_launch_nonce="nonce-1",
        executable_identity="opencode@1.2.3+sha256:abc",
        runtime_configuration_digest=_DIGEST,
        runtime_api_generation="v2",
        endpoint_allocation_policy="explicit-loopback-no-discovery",
        requested_provider_id="provider-a",
        requested_model_id="model-a",
        permission_profile_ref=request.basis.permission_profile_ref,
        runtime_request_payload_digest=request.basis.input_payload.payload_digest,
        runtime_limits_digest=_DIGEST,
    )


def request_v2() -> RuntimeRequestV2:
    request = runtime_request()
    return build_runtime_request_v2(
        request=request,
        launch_subject=launch_subject(request),
        placement_attestation_ref=RuntimePlacementAttestationRef(
            attestation_id="placement-1",
            content_digest=_DIGEST,
        ),
        endpoint_identity="http://127.0.0.1:4096",
    )


def permission_attestation(request: RuntimeRequestV2) -> RuntimePermissionAttestation:
    binding = RuntimeSessionBinding(
        execution_id=request.request.basis.execution_id,
        runtime_session=RuntimeSessionRef(runtime_id="opencode", session_id="session-1"),
        request_digest=request.request.request_digest,
        request_digest_v2=request.request_digest_v2,
        workspace_id=request.request.basis.workspace.workspace_id,
        created_at=_NOW,
    )
    return RuntimePermissionAttestation(
        attestation_id="permission-1",
        execution_id=binding.execution_id,
        request_digest_v2=request.request_digest_v2,
        session_binding=binding,
        runtime_descriptor_digest=request.launch_subject.runtime_descriptor_digest,
        launch_subject_digest=request.launch_subject.content_digest,
        placement_attestation_digest=request.placement_attestation_digest,
        expected_permission_profile_ref=request.launch_subject.permission_profile_ref,
        observed_effective_profile_digest=_DIGEST,
        effective_tool_exposure=("read",),
        effective_shell_exposure=False,
        actual_provider_id="provider-a",
        actual_model_id="model-a",
        completeness=RuntimeEvidenceCompleteness.SATISFIED,
        observation_provenance_digest=_DIGEST,
        adapter_identity="opencode-adapter",
        adapter_version="0.1.0",
        observed_from=_NOW,
        observed_until=_NOW,
    )


def test_v2_request_digest_binds_launch_and_placement_without_changing_v1() -> None:
    request = request_v2()
    assert request.request_digest_v2 == digest_runtime_request_v2(request)
    assert request.request.request_digest == digest_execution_basis(request.request.basis)

    changed = request.model_dump(mode="python")
    changed["endpoint_identity"] = "http://127.0.0.1:4097"
    with pytest.raises(ValidationError, match="V2 request digest"):
        RuntimeRequestV2.model_validate(changed)


@pytest.mark.parametrize(
    "endpoint",
    (
        "http://example.test:4096",
        "http://127.0.0.1",
        "http://user:password@127.0.0.1:4096",
        "http://127.0.0.1:4096/?token=secret",
    ),
)
def test_v2_request_rejects_non_loopback_or_ambiguous_endpoint(endpoint: str) -> None:
    request = request_v2()
    changed = request.model_dump(mode="python")
    changed["endpoint_identity"] = endpoint
    changed["request_digest_v2"] = "sha256:" + "2" * 64
    with pytest.raises(ValidationError):
        RuntimeRequestV2.model_validate(changed)


def test_open_code_does_not_create_session_without_managed_launch_capability() -> None:
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        if request.url.path == "/api/health":
            return httpx.Response(200, json={"healthy": True, "version": "1.2.3"})
        raise AssertionError(f"Unexpected OpenCode request: {request.method} {request.url.path}")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    request = request_v2()
    runtime = OpenCodeRuntime(
        "http://127.0.0.1:4096",
        expected_runtime_version="1.2.3",
        permission_profile=OpenCodePermissionProfile(
            reference=request.request.basis.permission_profile_ref,
            agent_id="relay-test-agent",
            allow=("read",),
            deny=("bash",),
        ),
        client=client,
    )

    async def exercise() -> None:
        try:
            with pytest.raises(AgentRuntimeError, match="boundary-managed launch"):
                await runtime.create_session_v2(request)
            assert paths == ["/api/health"]
        finally:
            await client.aclose()

    asyncio.run(exercise())


def test_open_code_permission_attestation_uses_relay_id_and_is_idempotent() -> None:
    request = request_v2()
    binding = permission_attestation(request).session_binding
    reader_calls = 0
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(500)))

    def reader(
        exact_request: RuntimeRequestV2,
        exact_binding: RuntimeSessionBinding,
    ) -> RuntimePermissionAttestation:
        nonlocal reader_calls
        reader_calls += 1
        return permission_attestation(exact_request).model_copy(
            update={"session_binding": exact_binding}
        )

    runtime = OpenCodeRuntime(
        "http://127.0.0.1:4096",
        expected_runtime_version="1.2.3",
        permission_profile=OpenCodePermissionProfile(
            reference=request.request.basis.permission_profile_ref,
            agent_id="relay-test-agent",
            allow=("read",),
            deny=("bash",),
        ),
        client=client,
        permission_attestation_reader=reader,
        permission_attestation_id_factory=lambda: "evd_relay-owned",
    )
    runtime._v2_bindings[binding.execution_id] = (request.request_digest_v2, binding)

    async def exercise() -> None:
        try:
            first = await runtime.attest_permissions_v2(request, binding)
            second = await runtime.attest_permissions_v2(request, binding)
            assert first.attestation_id == "evd_relay-owned"
            assert second == first
            assert reader_calls == 1
        finally:
            await client.aclose()

    asyncio.run(exercise())


def test_permission_attestation_digest_binds_exact_session_and_permission_payload() -> None:
    request = request_v2()
    attestation = permission_attestation(request)
    digest = digest_runtime_permission_attestation(attestation)
    assert attestation.ref.content_digest == digest

    changed = attestation.model_dump(mode="python")
    changed["effective_shell_exposure"] = True
    altered = RuntimePermissionAttestation.model_validate(changed)
    assert altered.ref.attestation_id == attestation.ref.attestation_id
    assert altered.ref.content_digest != attestation.ref.content_digest


def test_permission_attestation_rejects_unknown_or_incomplete_as_satisfied() -> None:
    attestation = permission_attestation(request_v2())
    changed = attestation.model_dump(mode="python")
    changed["unknown_tool_identity"] = True
    with pytest.raises(ValidationError, match="complete permission evidence"):
        RuntimePermissionAttestation.model_validate(changed)


def test_workspace_boundary_placement_attester_is_exact_and_provider_bound() -> None:
    plan, descriptor = make_plan()
    plan_ref = workspace_plan_ref(plan)
    provider_ref = workspace_provider_ref(descriptor)
    instance = WorkspaceInstanceRef(
        workspace_id="instance-1",
        plan_ref=plan_ref,
        provider_ref=provider_ref,
        repository=plan.source_baseline_ref.commit.repository,
        source_commit=plan.source_baseline_ref.commit,
        root="/tmp/relay-instance",
    )
    expected = PlacementAttesterRef(
        provider_ref=provider_ref,
        attester_id="fixture-attester",
        attester_version="v1",
        authenticated_channel_key="in-process-provider-channel",
    )
    boundary = WorkspaceBoundaryRef(
        plan_ref=plan_ref,
        instance_ref=instance,
        provider_ref=provider_ref,
        boundary_instance_key="boundary-1",
        boundary_policy_digest=_DIGEST,
        boundary_mechanism_key="deterministic-fake",
        boundary_evidence_digest=_DIGEST,
        expected_placement_attester_ref=expected,
    )
    subject = launch_subject(runtime_request())
    attestation = RuntimePlacementAttestation(
        attestation_id="placement-1",
        launch_subject_digest=subject.content_digest,
        workspace_boundary_ref_digest=boundary.content_digest,
        runtime_descriptor_digest=subject.runtime_descriptor_digest,
        process_tree_identity="tree-1",
        runtime_server_identity="server-1",
        endpoint_identity="http://127.0.0.1:4096",
        observed_boundary_membership=RequirementStatus.SATISFIED,
        enforcement_evidence_digest=_DIGEST,
        credential_separation_status=RequirementStatus.SATISFIED,
        credential_separation_evidence_digest=_DIGEST,
        attester_id="fixture-attester",
        attester_version="v1",
        authenticated_channel_key="in-process-provider-channel",
        trust_evidence_digest=_DIGEST,
        challenge_or_launch_nonce="nonce-1",
        observed_from=_NOW,
        observed_until=_NOW,
        completeness=RequirementStatus.SATISFIED,
    )
    assert placement_attestation_matches_boundary(
        boundary,
        attestation,
        launch_subject_digest=subject.content_digest,
        runtime_descriptor_digest=subject.runtime_descriptor_digest,
        launch_nonce=subject.challenge_or_launch_nonce,
    )
    changed = attestation.model_dump(mode="python")
    changed["attester_id"] = "untrusted-attester"
    mismatched = RuntimePlacementAttestation.model_validate(changed)
    assert not placement_attestation_matches_boundary(
        boundary,
        mismatched,
        launch_subject_digest=subject.content_digest,
        runtime_descriptor_digest=subject.runtime_descriptor_digest,
        launch_nonce=subject.challenge_or_launch_nonce,
    )


def test_boundary_evaluator_denies_known_credential_separation_failure() -> None:
    plan, descriptor = make_plan()
    plan_ref = workspace_plan_ref(plan)
    provider_ref = workspace_provider_ref(descriptor)
    instance = WorkspaceInstanceRef(
        workspace_id="instance-boundary-evaluation",
        plan_ref=plan_ref,
        provider_ref=provider_ref,
        repository=plan.source_baseline_ref.commit.repository,
        source_commit=plan.source_baseline_ref.commit,
        root="/tmp/relay-instance-evaluation",
    )
    expected_attester = PlacementAttesterRef(
        provider_ref=provider_ref,
        attester_id="fixture-attester",
        attester_version="v1",
        trust_anchor_digest=_DIGEST,
    )
    boundary = WorkspaceBoundaryRef(
        plan_ref=plan_ref,
        instance_ref=instance,
        provider_ref=provider_ref,
        boundary_instance_key="boundary-evaluation",
        boundary_policy_digest=_DIGEST,
        boundary_mechanism_key="deterministic-fake",
        boundary_evidence_digest=_DIGEST,
        expected_placement_attester_ref=expected_attester,
    )
    request = runtime_request()
    subject = launch_subject(request).model_copy(
        update={"workspace_boundary_digest": boundary.content_digest}
    )
    placement = RuntimePlacementAttestation(
        attestation_id="placement-evaluation",
        launch_subject_digest=subject.content_digest,
        workspace_boundary_ref_digest=boundary.content_digest,
        runtime_descriptor_digest=subject.runtime_descriptor_digest,
        process_tree_identity="tree-evaluation",
        runtime_server_identity="server-evaluation",
        endpoint_identity="http://127.0.0.1:4096",
        observed_boundary_membership=RequirementStatus.SATISFIED,
        enforcement_evidence_digest=_DIGEST,
        credential_separation_status=RequirementStatus.UNSATISFIED,
        credential_separation_evidence_digest=_DIGEST,
        attester_id=expected_attester.attester_id,
        attester_version=expected_attester.attester_version,
        trust_anchor_digest=expected_attester.trust_anchor_digest,
        trust_evidence_digest=_DIGEST,
        challenge_or_launch_nonce=subject.challenge_or_launch_nonce,
        observed_from=_NOW,
        observed_until=_NOW,
        completeness=RequirementStatus.SATISFIED,
    )
    request_v2 = build_runtime_request_v2(
        request=request,
        launch_subject=subject,
        placement_attestation_ref=placement.ref,
        endpoint_identity=placement.endpoint_identity,
    )
    session = RuntimeSessionBinding(
        execution_id=request.basis.execution_id,
        runtime_session=RuntimeSessionRef(runtime_id="opencode", session_id="session-eval"),
        request_digest=request.request_digest,
        request_digest_v2=request_v2.request_digest_v2,
        workspace_id=instance.workspace_id,
        created_at=_NOW,
    )
    permission = permission_attestation(request_v2).model_copy(update={"session_binding": session})
    continuity = RuntimePlacementContinuityEvidence(
        workspace_boundary_ref_digest=boundary.content_digest,
        placement_attestation_ref=placement.ref,
        execution_id=request.basis.execution_id,
        request_digest_v2=request_v2.request_digest_v2,
        process_tree_identity=placement.process_tree_identity,
        observer_id="fixture-observer",
        observed_from=_NOW,
        observed_until=_NOW,
        status=RequirementStatus.SATISFIED,
        evidence_digest=_DIGEST,
    )
    permission_evidence = RuntimePermissionEvidence(
        execution_id=request.basis.execution_id,
        runtime_id="opencode",
        attestation_id=permission.attestation_id,
        evidence_digest=permission.content_digest,
        effective_profile_ref=permission.expected_permission_profile_ref,
        completeness=RequirementStatus.SATISFIED,
        exposed_tools=permission.effective_tool_exposure,
        shell_exposed=permission.effective_shell_exposure,
        actual_provider_id=permission.actual_provider_id,
        actual_model_id=permission.actual_model_id,
        provenance_status=RequirementStatus.SATISFIED,
    )
    result = evaluate_runtime_boundary_evidence(
        plan,
        boundary,
        placement,
        request_v2,
        session,
        permission,
        continuity,
        runtime_id="opencode",
        runtime_permission_evidence=permission_evidence,
    )
    assert result.status is AdmissionStatus.DENY
    assert "runtime-boundary:credential-separation-unsatisfied" in result.reasons
