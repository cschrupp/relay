"""Coordinator gates authority before touching a workspace or runtime."""

from __future__ import annotations

import asyncio
from typing import cast

import pytest
from test_project_state_dogfood import _compile, _resolve, _scenario
from test_work_packet_models import packet

from relay_engine.agent_runtime import AgentRuntime
from relay_engine.coding_execution.coordinator import (
    AdmissionRejected,
    CoordinatorInputs,
    execute_governed_attempt,
)
from relay_engine.coding_execution.evaluation import AdmissionInputs, RuntimePermissionEvidence
from relay_engine.execution_workspace import WorkspaceProvider
from relay_engine.role_contracts import RequirementStatus


class UntouchedWorkspace:
    def __init__(self) -> None:
        self.calls = 0

    def describe(self):
        self.calls += 1
        raise AssertionError("workspace must not be queried before exact grant")

    def provision(self, plan):
        self.calls += 1
        raise AssertionError("workspace must not be provisioned before exact grant")

    def inspect(self, instance_ref):
        self.calls += 1
        raise AssertionError("workspace must not be inspected")

    def extract_changes(self, instance_ref):
        self.calls += 1
        raise AssertionError("workspace changes must not be extracted")

    def teardown(self, instance_ref):
        self.calls += 1
        raise AssertionError("workspace must not be torn down")


class UntouchedRuntime:
    def __init__(self) -> None:
        self.calls = 0

    async def describe(self):
        self.calls += 1
        raise AssertionError("runtime must not be queried before exact grant")

    async def create_session(self, request):
        self.calls += 1
        raise AssertionError("runtime session must not be created")

    async def open_execution(self, request, binding):
        self.calls += 1
        raise AssertionError("runtime prompt must not be admitted")

    def events(self, handle):
        self.calls += 1
        raise AssertionError("runtime events must not be requested")

    async def cancel(self, request):
        self.calls += 1
        raise AssertionError("runtime must not be cancelled")

    async def inspect(self, handle):
        self.calls += 1
        raise AssertionError("runtime must not be inspected")


def test_ready_without_exact_human_grant_never_reaches_workspace_or_runtime() -> None:
    scenario = _scenario(
        scope="execution",
        attempt="exec-018f47c1-7b2c-7abc-8def-123456789008",
    )
    compilation = _compile(scenario, _resolve(scenario))
    candidate = compilation.candidate
    assert candidate is not None
    packet_value = packet()
    admission = AdmissionInputs.model_construct(
        compilation=compilation,
        candidate=candidate,
        current_snapshot=scenario.snapshot,
        grant=None,
        reservations=(),
        work_packet=packet_value,
    )
    workspace = UntouchedWorkspace()
    runtime = UntouchedRuntime()
    coordinator_inputs = CoordinatorInputs(
        admission=admission,
        authorized_slice_id="slc_018f47c1-7b2c-7abc-8def-123456789008",
        work_packet_materializer=None,
        workspace_policy=cast(object, None),
        protected_authority_facts=(),
        plan_key="slice-3-1-plan",
        plan_revision=1,
        runtime_permission_evidence=cast(RuntimePermissionEvidence, None),
        runtime_payload_materializer=None,
        permission_profile_ref=cast(object, None),
    )

    with pytest.raises(AdmissionRejected, match="grant-reservation:DENY"):
        asyncio.run(
            execute_governed_attempt(
                coordinator_inputs,
                cast(WorkspaceProvider, workspace),
                cast(AgentRuntime, runtime),
            )
        )
    assert workspace.calls == 0
    assert runtime.calls == 0


def test_work_packet_ref_is_computed_before_workspace_resolver_call() -> None:
    import inspect

    from relay_engine.coding_execution import coordinator

    source = inspect.getsource(coordinator.execute_governed_attempt)
    packet_conformance = source.index("evaluate_packet_before_workspace(")
    packet_reference = source.index("packet_ref = work_packet_ref(packet)")
    workspace_resolution = source.index("resolve_workspace_plan(")
    assert packet_conformance < packet_reference < workspace_resolution


def test_permission_evidence_requires_known_effective_profile_status() -> None:
    value = RuntimePermissionEvidence(
        execution_id="exec_018f47c1-7b2c-7abc-8def-123456789008",
        runtime_id="runtime-test",
        attestation_id="attestation-test",
        evidence_digest="sha256:" + "a" * 64,
        effective_profile_ref=None,
        completeness=RequirementStatus.INDETERMINATE,
        provenance_status=RequirementStatus.INDETERMINATE,
        exposed_tools=None,
        unknown_tool_identity=True,
        shell_exposed=None,
    )
    assert value.completeness is RequirementStatus.INDETERMINATE


def test_grant_precedes_materialization_and_exact_packet_ref_precedes_workspace_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from test_execution_workspace_evaluation import resolver_fixture
    from test_work_packet_evaluation import conforming_facts, materialization_facts_for

    from relay_engine.agent_runtime import (
        RuntimeInputPayload,
        RuntimePermissionProfileRef,
    )
    from relay_engine.coding_execution import coordinator as coordinator_module
    from relay_engine.coding_execution.coordinator import (
        MaterializedRuntimePayload,
        MaterializedWorkPacket,
    )
    from relay_engine.coding_execution.evaluation import digest_runtime_payload_content
    from relay_engine.coding_execution.models import (
        AdmissionEvidence,
        HumanGrantBinding,
        RuntimePayloadEvidence,
    )
    from relay_engine.coding_execution.models import AdmissionStatus as CodingAdmissionStatus
    from relay_engine.domain import ActorKind, ActorRef
    from relay_engine.execution_workspace.models import (
        WorkspacePlanResolution,
        WorkspaceReason,
    )
    from relay_engine.project_state import AuthorityCandidate
    from relay_engine.work_packets import (
        ContextConformance,
        WorkPacketConformance,
        work_packet_ref,
    )

    scenario = _scenario(
        scope="execution",
        attempt="exec-018f47c1-7b2c-7abc-8def-123456789008",
    )
    compilation = _compile(scenario, _resolve(scenario))
    candidate = compilation.candidate
    assert candidate is not None
    packet_value, _, policy, role, descriptor = resolver_fixture()
    snapshot = candidate.resolution.snapshot.model_copy(
        update={"project_id": packet_value.project_id}
    )
    candidate = candidate.model_copy(
        update={"resolution": candidate.resolution.model_copy(update={"snapshot": snapshot})}
    )
    compilation = compilation.model_copy(update={"candidate": candidate})
    grant = HumanGrantBinding(
        grant_record_id="human-grant-exact",
        grant_record_digest="sha256:" + "a" * 64,
        authority_candidate_digest=candidate.content_digest,
        intended_attempt_id=candidate.request.intended_attempt_id,
        project_id=packet_value.project_id,
        slice_id=packet_value.slice_definition_ref.slice_id,
        valid=True,
        applicable=True,
    )
    authority_ref = packet_value.authority_refs[0].model_copy(
        update={
            "authority_key": grant.grant_record_id,
            "record_digest": grant.grant_record_digest,
            "subject_digest": candidate.content_digest,
        }
    )
    values = packet_value.model_dump(mode="python")
    values["authority_refs"] = (authority_ref,)
    packet_value = type(packet_value).model_validate(values)
    context = __import__("test_work_packet_models", fromlist=["manifest"]).manifest()
    trace: list[str] = []

    def materialize_payload(exact_packet, exact_ref, exact_manifest, exact_manifest_ref):
        trace.append("materialize-payload-after-packet-ref")
        payload = RuntimeInputPayload(
            text="Implement the authorized packet.",
            payload_digest="sha256:" + "c" * 64,
        )
        payload = payload.model_copy(
            update={"payload_digest": digest_runtime_payload_content(payload)}
        )
        evidence = RuntimePayloadEvidence(
            work_packet_ref=exact_ref,
            context_manifest_ref=exact_manifest_ref,
            payload_digest=payload.payload_digest,
            included_context_keys=exact_packet.required_context_keys,
            status=RequirementStatus.SATISFIED,
            protected_content_exposed=False,
            evaluator_only_content_exposed=False,
            credential_exposure_status="CLEAR",
            evidence_digest="sha256:" + "d" * 64,
        )
        assert exact_manifest == context
        return MaterializedRuntimePayload(payload=payload, evidence=evidence)

    def materialize(
        exact_candidate: AuthorityCandidate, exact_grant: HumanGrantBinding
    ) -> MaterializedWorkPacket:
        assert exact_candidate.content_digest == exact_grant.authority_candidate_digest
        trace.append("materialize-after-grant")
        return MaterializedWorkPacket(
            packet=packet_value,
            context_manifest=context,
            conformance_facts=conforming_facts(packet_value, context),
            materialization_facts=materialization_facts_for(packet_value, context),
        )

    def resolve(*args, **kwargs):
        trace.append("resolve-workspace")
        assert args[1] == work_packet_ref(packet_value)
        return WorkspacePlanResolution(
            status=RequirementStatus.UNSATISFIED,
            reasons=(WorkspaceReason.WORK_PACKET_REF_MISMATCH,),
            plan=None,
        )

    monkeypatch.setattr(
        coordinator_module,
        "evaluate_packet_before_workspace",
        lambda *a: AdmissionEvidence(status=CodingAdmissionStatus.ADMIT),
    )
    monkeypatch.setattr(
        coordinator_module,
        "evaluate_context_conformance",
        lambda *args: ContextConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    monkeypatch.setattr(
        coordinator_module,
        "evaluate_work_packet_conformance",
        lambda *args: WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
    )
    monkeypatch.setattr(coordinator_module, "resolve_workspace_plan", resolve)

    class DescribedWorkspace(UntouchedWorkspace):
        def describe(self):
            trace.append("provider-describe")
            return descriptor

    admission = AdmissionInputs.model_construct(
        compilation=compilation,
        candidate=candidate,
        current_snapshot=snapshot,
        grant=grant,
        reservations=(),
        role_contract=role,
        actor=ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.AGENT),
    )
    inputs = CoordinatorInputs(
        admission=admission,
        authorized_slice_id=packet_value.slice_definition_ref.slice_id,
        work_packet_materializer=materialize,
        workspace_policy=policy,
        protected_authority_facts=(),
        plan_key="test-plan",
        plan_revision=1,
        runtime_permission_evidence=cast(RuntimePermissionEvidence, None),
        runtime_payload_materializer=materialize_payload,
        permission_profile_ref=cast(RuntimePermissionProfileRef, None),
    )
    workspace = DescribedWorkspace()
    runtime = UntouchedRuntime()
    with pytest.raises(AdmissionRejected, match="workspace:plan-resolution"):
        asyncio.run(
            execute_governed_attempt(
                inputs,
                cast(WorkspaceProvider, workspace),
                cast(AgentRuntime, runtime),
            )
        )
    assert trace == [
        "materialize-after-grant",
        "materialize-payload-after-packet-ref",
        "provider-describe",
        "resolve-workspace",
    ]
    assert workspace.calls == 0
    assert runtime.calls == 0


@pytest.mark.parametrize(
    ("script", "expected_outcome"),
    (
        ("success", "DONE"),
        ("runtime-failure", "BLOCKED_BY_ENVIRONMENT"),
        ("cancellation", "CANCELLED"),
        ("event-gap", "INTERRUPTED"),
        ("uncertain-admission", "INTERRUPTED"),
        ("usage-exhausted", "BUDGET_EXHAUSTED"),
        ("incomplete-evidence", "BLOCKED_BY_CONTRACT"),
        ("capture-unavailable", "BLOCKED_BY_CONTRACT"),
        ("provider-model-mismatch", "PRE_ADMISSION_DENY"),
        ("configuration-mismatch", "PRE_ADMISSION_DENY"),
        ("runtime-identity-mismatch", "PRE_ADMISSION_DENY"),
        ("boundary-success", "DONE"),
        ("boundary-permission-missing", "PRE_ADMISSION_DENY"),
        ("boundary-permission-incomplete", "PRE_ADMISSION_DENY"),
        ("boundary-permission-stale", "PRE_ADMISSION_DENY"),
        ("boundary-permission-mismatch", "PRE_ADMISSION_DENY"),
    ),
)
def test_scripted_fake_runtime_reaches_exact_terminal_result(
    monkeypatch: pytest.MonkeyPatch,
    script: str,
    expected_outcome: str,
) -> None:
    from datetime import UTC, datetime, timedelta

    from test_execution_workspace_evaluation import conformance_fixture, resolver_fixture
    from test_project_state_dogfood import _compile, _resolve, _scenario
    from test_work_packet_evaluation import conforming_facts, materialization_facts_for
    from test_work_packet_models import manifest

    from relay_engine.agent_runtime import (
        EventContinuity,
        RuntimeCapability,
        RuntimeContinuityState,
        RuntimeControlAck,
        RuntimeControlAckState,
        RuntimeDescriptor,
        RuntimeEventEnvelope,
        RuntimeEventType,
        RuntimeExecutionHandle,
        RuntimeExecutionInspection,
        RuntimeExecutionLimits,
        RuntimeIdentityCompleteness,
        RuntimeInputPayload,
        RuntimeProvenance,
        RuntimeSessionBinding,
        RuntimeSessionRef,
        RuntimeStatus,
        RuntimeUsage,
    )
    from relay_engine.agent_runtime.boundary import (
        RuntimeEvidenceCompleteness,
        RuntimePermissionAttestation,
        RuntimeRequestV2,
    )
    from relay_engine.agent_runtime.opencode import (
        OpenCodeConfigurationBinding,
        OpenCodeConfigurationQualificationRef,
    )
    from relay_engine.coding_execution import coordinator as coordinator_module
    from relay_engine.coding_execution.coordinator import (
        MaterializedRuntimePayload,
        MaterializedWorkPacket,
    )
    from relay_engine.coding_execution.evaluation import (
        digest_runtime_payload_content,
    )
    from relay_engine.coding_execution.models import (
        AdmissionEvidence,
        HumanGrantBinding,
        RuntimePayloadEvidence,
    )
    from relay_engine.coding_execution.models import (
        AdmissionStatus as CodingAdmissionStatus,
    )
    from relay_engine.domain import ActorKind, ActorRef
    from relay_engine.execution_workspace import (
        derive_runtime_workspace_attachment,
    )
    from relay_engine.execution_workspace.boundary import (
        PlacementAttesterRef,
        RuntimePlacementAttestation,
        RuntimePlacementContinuityEvidence,
        RuntimeProcessTeardownEvidence,
        WorkspaceBoundaryRef,
    )
    from relay_engine.execution_workspace.evaluation import (
        workspace_policy_ref,
        workspace_provider_ref,
    )
    from relay_engine.execution_workspace.models import (
        ControlStrength,
        WorkspaceBackendKind,
        WorkspaceBoundaryClass,
        WorkspaceCandidateCapture,
        WorkspaceChangeManifest,
        WorkspaceConformance,
        WorkspaceProviderPropertyCapability,
        WorkspaceProvisionResult,
    )
    from relay_engine.project_state import AuthorityCandidate
    from relay_engine.role_contracts import RequirementStatus

    scenario = _scenario(
        scope="execution",
        attempt="exec-018f47c1-7b2c-7abc-8def-123456789008",
    )
    compilation = _compile(scenario, _resolve(scenario))
    candidate = compilation.candidate
    assert candidate is not None
    packet_value, _, policy, role, workspace_descriptor = resolver_fixture()
    boundary_mode = script.startswith("boundary-")
    trace: list[str] = []
    if boundary_mode:
        policy = policy.model_copy(
            update={
                "property_requirements": tuple(
                    item.model_copy(update={"minimum_strength": ControlStrength.BOUNDARY_ENFORCED})
                    for item in policy.property_requirements
                )
            }
        )
        workspace_descriptor = workspace_descriptor.model_copy(
            update={
                "backend_kind": WorkspaceBackendKind.CONTAINER,
                "boundary_class": WorkspaceBoundaryClass.CONTAINER_BOUNDARY,
                "property_capabilities": tuple(
                    WorkspaceProviderPropertyCapability(
                        property=item.property,
                        maximum_strength=ControlStrength.BOUNDARY_ENFORCED,
                    )
                    for item in workspace_descriptor.property_capabilities
                ),
            }
        )
        packet_fields = packet_value.model_dump(mode="python")
        packet_fields["workspace_policy_ref"] = workspace_policy_ref(policy)
        packet_value = type(packet_value).model_validate(packet_fields)
    snapshot = candidate.resolution.snapshot.model_copy(
        update={"project_id": packet_value.project_id}
    )
    candidate = candidate.model_copy(
        update={"resolution": candidate.resolution.model_copy(update={"snapshot": snapshot})}
    )
    compilation = compilation.model_copy(update={"candidate": candidate})
    grant = HumanGrantBinding(
        grant_record_id="human-grant-exact",
        grant_record_digest="sha256:" + "a" * 64,
        authority_candidate_digest=candidate.content_digest,
        intended_attempt_id=candidate.request.intended_attempt_id,
        project_id=packet_value.project_id,
        slice_id=packet_value.slice_definition_ref.slice_id,
        valid=True,
        applicable=True,
    )
    authority_ref = packet_value.authority_refs[0].model_copy(
        update={
            "authority_key": grant.grant_record_id,
            "record_digest": grant.grant_record_digest,
            "subject_digest": candidate.content_digest,
        }
    )
    packet_fields = packet_value.model_dump(mode="python")
    packet_fields["authority_refs"] = (authority_ref,)
    if script == "usage-exhausted":
        packet_fields["runtime_limits"] = RuntimeExecutionLimits(max_tool_calls=1)
    packet_value = type(packet_value).model_validate(packet_fields)
    context = manifest()
    runtime_selection = packet_value.runtime_selection_requirement
    permission_ref = packet_value.runtime_permission_profile_ref
    assert runtime_selection is not None and permission_ref is not None
    runtime_descriptor = RuntimeDescriptor(
        runtime_id=(
            "different-runtime"
            if script == "runtime-identity-mismatch"
            else runtime_selection.runtime_id
        ),
        adapter_version="fake-1",
        runtime_version="fake-runtime-1",
        api_generation="fake-v1",
        capabilities=tuple(RuntimeCapability),
        executable_digest="sha256:" + "b" * 64 if boundary_mode else None,
        configuration_digest="sha256:" + "c" * 64 if boundary_mode else None,
    )

    class ScriptedWorkspace:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.provision_result = None
            self.workspace_facts = None
            self.boundary = None

        def describe(self):
            self.calls.append("describe")
            return workspace_descriptor

        def provision(self, plan):
            self.calls.append("provision")
            instance, facts = conformance_fixture(plan, workspace_descriptor)
            self.workspace_facts = facts
            attachment = derive_runtime_workspace_attachment(instance)
            self.provision_result = WorkspaceProvisionResult(
                instance_ref=instance,
                runtime_attachment=attachment,
                environment_provenance=facts.environment_provenance,
                initial_inspection=facts.initial_inspection,
                property_evidence=facts.property_evidence,
            )
            return self.provision_result

        def inspect(self, instance_ref):
            self.calls.append("inspect")
            assert self.provision_result is not None
            assert instance_ref == self.provision_result.instance_ref
            return self.provision_result.initial_inspection

        def extract_changes(self, instance_ref):
            self.calls.append("changes")
            return WorkspaceChangeManifest(
                instance_ref=instance_ref,
                source_commit=instance_ref.source_commit,
                entries=(),
            )

        def capture_candidate(self, instance_ref, changes):
            import hashlib
            import json

            if script == "capture-unavailable":
                raise RuntimeError("candidate capture unavailable")
            digest = (
                "sha256:"
                + hashlib.sha256(
                    json.dumps(
                        changes.model_dump(mode="json"),
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                        allow_nan=False,
                    ).encode("utf-8")
                ).hexdigest()
            )
            return WorkspaceCandidateCapture(
                instance_ref=instance_ref,
                source_commit=instance_ref.source_commit,
                git_object_format="sha1",
                tree_object_id="0" * 40,
                change_manifest_digest=digest,
                captured_at="2026-10-25T00:00:00Z",
            )

        def teardown(self, instance_ref):
            self.calls.append("teardown")

        def boundary_ref(self, instance_ref):
            assert boundary_mode and self.provision_result is not None
            expected_attester = PlacementAttesterRef(
                provider_ref=workspace_provider_ref(workspace_descriptor),
                attester_id="fake-boundary-attester",
                attester_version="v1",
                trust_anchor_digest="sha256:" + "f" * 64,
            )
            self.boundary = WorkspaceBoundaryRef(
                plan_ref=instance_ref.plan_ref,
                instance_ref=instance_ref,
                provider_ref=instance_ref.provider_ref,
                boundary_instance_key="fake-boundary-instance",
                boundary_policy_digest="sha256:" + "1" * 64,
                boundary_mechanism_key="deterministic-container-fake",
                boundary_evidence_digest="sha256:" + "2" * 64,
                expected_placement_attester_ref=expected_attester,
            )
            return self.boundary

        async def launch_runtime(self, boundary, subject):
            trace.append("launch_runtime")
            assert boundary == self.boundary
            return RuntimePlacementAttestation(
                attestation_id="fake-placement-attestation",
                launch_subject_digest=subject.content_digest,
                workspace_boundary_ref_digest=boundary.content_digest,
                runtime_descriptor_digest=subject.runtime_descriptor_digest,
                process_tree_identity="fake-process-tree",
                runtime_server_identity="fake-runtime-server",
                endpoint_identity="https://executor.example:8443/runtime/control",
                observed_boundary_membership=RequirementStatus.SATISFIED,
                enforcement_evidence_digest="sha256:" + "3" * 64,
                credential_separation_status=RequirementStatus.SATISFIED,
                credential_separation_evidence_digest="sha256:" + "4" * 64,
                attester_id="fake-boundary-attester",
                attester_version="v1",
                trust_anchor_digest="sha256:" + "f" * 64,
                trust_evidence_digest="sha256:" + "5" * 64,
                challenge_or_launch_nonce=subject.challenge_or_launch_nonce,
                observed_from=datetime(2026, 10, 25, tzinfo=UTC),
                observed_until=datetime(2026, 10, 25, tzinfo=UTC),
                completeness=RequirementStatus.SATISFIED,
            )

        def inspect_runtime_continuity(
            self, boundary, placement, *, execution_id, request_digest_v2
        ):
            trace.append("inspect-boundary-continuity")
            return RuntimePlacementContinuityEvidence(
                workspace_boundary_ref_digest=boundary.content_digest,
                placement_attestation_ref=placement.ref,
                execution_id=execution_id,
                request_digest_v2=request_digest_v2,
                process_tree_identity=placement.process_tree_identity,
                observer_id="fake-boundary-observer",
                observed_from=datetime(2026, 10, 25, tzinfo=UTC),
                observed_until=datetime(2026, 10, 25, tzinfo=UTC),
                status=RequirementStatus.SATISFIED,
                evidence_digest="sha256:" + "6" * 64,
            )

        async def teardown_runtime(self, boundary, placement, *, execution_id):
            self.calls.append("teardown-runtime")
            trace.append("teardown-runtime")
            return RuntimeProcessTeardownEvidence(
                workspace_boundary_ref_digest=boundary.content_digest,
                placement_attestation_ref=placement.ref,
                execution_id=execution_id,
                process_tree_identity=placement.process_tree_identity,
                process_tree_terminated=RequirementStatus.SATISFIED,
                credential_cleanup=RequirementStatus.SATISFIED,
                evidence_digest="sha256:" + "7" * 64,
            )

    class ScriptedRuntime:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.request = None
            self.session = RuntimeSessionRef(
                runtime_id=runtime_descriptor.runtime_id,
                session_id="fake-session-1",
            )

        async def describe(self):
            self.calls.append("describe")
            return runtime_descriptor

        async def create_session(self, request):
            self.calls.append("create-session")
            self.request = request
            return RuntimeSessionBinding(
                execution_id=request.basis.execution_id,
                runtime_session=self.session,
                request_digest=request.request_digest,
                workspace_id=request.basis.workspace.workspace_id,
                created_at=datetime(2026, 10, 25, tzinfo=UTC),
            )

        async def prepare_trusted_local_session(self, request, descriptor):
            import hashlib
            import json

            trace.append("configuration-binding")
            self.request = request
            exposure = ()
            source_refs = ("fake-agent-config",)
            config_payload = {
                "agent_id": "fixture-agent",
                "configuration_source_refs": source_refs,
                "normalized_allow_rules": (),
                "normalized_deny_rules": (),
                "normalized_ask_rules": (),
                "effective_tool_exposure": exposure,
                "plugin_exposure": (),
                "mcp_exposure": (),
                "subagent_exposure": (),
            }
            config_digest = (
                "sha256:"
                + hashlib.sha256(
                    json.dumps(
                        config_payload,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                        allow_nan=False,
                    ).encode("utf-8")
                ).hexdigest()
            )
            qualification = OpenCodeConfigurationQualificationRef(
                qualification_id="fake-version-qualified-config",
                content_digest="sha256:" + "9" * 64,
                runtime_version=descriptor.runtime_version,
                runtime_api_generation=descriptor.api_generation,
                adapter_version=descriptor.adapter_version,
            )
            configuration = OpenCodeConfigurationBinding(
                binding_id="fake-config-binding",
                runtime_id=descriptor.runtime_id,
                runtime_version=descriptor.runtime_version,
                runtime_api_generation=descriptor.api_generation,
                adapter_version=descriptor.adapter_version,
                integration_qualification_ref=qualification,
                permission_profile_ref=(
                    permission_ref.model_copy(update={"content_digest": "sha256:" + "7" * 64})
                    if script == "configuration-mismatch"
                    else permission_ref
                ),
                agent_id="fixture-agent",
                configuration_source_refs=source_refs,
                effective_configuration_digest=config_digest,
                normalized_allow_rules=(),
                normalized_deny_rules=(),
                normalized_ask_rules=(),
                effective_tool_exposure=exposure,
                shell_exposed=False,
                plugin_exposure=(),
                mcp_exposure=(),
                subagent_exposure=(),
                precedence_complete=True,
                observation_source="deterministic-test-reader",
                trust_basis="test-injected-only",
                provenance_digest="sha256:" + "8" * 64,
                observed_at=datetime(2026, 10, 25, tzinfo=UTC),
                status=RequirementStatus.SATISFIED,
            )
            session = await self.create_session(request)
            session = session.model_copy(
                update={
                    "actual_provider_id": (
                        "different-provider"
                        if script == "provider-model-mismatch"
                        else runtime_selection.requested_provider_id
                    ),
                    "actual_model_id": runtime_selection.requested_model_id,
                    "actual_identity_status": RuntimeIdentityCompleteness.FULL,
                }
            )
            self.session = session.runtime_session
            trace.append("create_session_prompt_free")
            return configuration, session

        async def close_prepared_session(self, binding):
            self.calls.append("close-prepared-session")
            assert binding.runtime_session == self.session
            return RequirementStatus.SATISFIED

        async def create_session_v2(self, request: RuntimeRequestV2):
            self.calls.append("create_session_v2")
            trace.append("create_session_v2")
            self.request = request.request
            return RuntimeSessionBinding(
                execution_id=request.request.basis.execution_id,
                runtime_session=self.session,
                request_digest=request.request.request_digest,
                request_digest_v2=request.request_digest_v2,
                workspace_id=request.request.basis.workspace.workspace_id,
                created_at=datetime(2026, 10, 25, tzinfo=UTC),
            )

        async def attest_permissions_v2(self, request: RuntimeRequestV2, binding):
            self.calls.append("attest_permissions_v2")
            trace.append("attest_permissions_v2")
            if script == "boundary-permission-missing":
                raise RuntimeError("fake permission observation unavailable")
            attestation = RuntimePermissionAttestation(
                attestation_id="fake-permission-attestation",
                execution_id=binding.execution_id,
                request_digest_v2=request.request_digest_v2,
                session_binding=binding,
                runtime_descriptor_digest=request.launch_subject.runtime_descriptor_digest,
                launch_subject_digest=request.launch_subject.content_digest,
                placement_attestation_digest=request.placement_attestation_digest,
                expected_permission_profile_ref=permission_ref,
                observed_effective_profile_digest=permission_ref.content_digest,
                effective_tool_exposure=(),
                unknown_tool_identity=False,
                effective_shell_exposure=False,
                actual_provider_id=runtime_selection.requested_provider_id,
                actual_model_id=runtime_selection.requested_model_id,
                completeness=(
                    RuntimeEvidenceCompleteness.INDETERMINATE
                    if script == "boundary-permission-incomplete"
                    else RuntimeEvidenceCompleteness.SATISFIED
                ),
                observation_provenance_digest="sha256:" + "8" * 64,
                adapter_identity="fake-runtime-adapter",
                adapter_version="fake-1",
                observed_from=(
                    datetime(2026, 10, 24, tzinfo=UTC)
                    if script == "boundary-permission-stale"
                    else datetime(2026, 10, 25, tzinfo=UTC)
                ),
                observed_until=datetime(2026, 10, 25, tzinfo=UTC),
            )
            if script == "boundary-permission-mismatch":
                attestation = attestation.model_copy(
                    update={"request_digest_v2": "sha256:" + "9" * 64}
                )
            return attestation

        async def open_execution(self, request, binding):
            self.calls.append("open-execution")
            trace.append("open_execution")
            return RuntimeExecutionHandle(
                execution_id=request.basis.execution_id,
                runtime_session=binding.runtime_session,
                request_digest=request.request_digest,
                opened_at=datetime(2026, 10, 25, tzinfo=UTC),
            )

        async def open_execution_v2(self, request, binding, permission_attestation):
            self.calls.append("open_execution_v2")
            trace.append("open_execution_v2")
            assert binding.request_digest_v2 == request.request_digest_v2
            assert permission_attestation.request_digest_v2 == request.request_digest_v2
            return RuntimeExecutionHandle(
                execution_id=request.request.basis.execution_id,
                runtime_session=binding.runtime_session,
                request_digest=request.request.request_digest,
                request_digest_v2=request.request_digest_v2,
                opened_at=datetime(2026, 10, 25, tzinfo=UTC),
            )

        async def events(self, handle):
            self.calls.append("events")
            event_types = {
                "success": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
                "runtime-failure": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_FAILED,
                ),
                "cancellation": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_CANCELLED,
                ),
                "event-gap": (
                    RuntimeEventType.EVENT_GAP,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
                "uncertain-admission": (RuntimeEventType.EXECUTION_STARTED,),
                "usage-exhausted": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.TOOL_REQUESTED,
                    RuntimeEventType.TOOL_REQUESTED,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
                "incomplete-evidence": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
                "capture-unavailable": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
                "provider-model-mismatch": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
                "runtime-identity-mismatch": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
                "boundary-success": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
            }[script]
            for index, event_type in enumerate(event_types, start=1):
                payload = (
                    {"tool_identity": "test-tool"}
                    if event_type is RuntimeEventType.TOOL_REQUESTED
                    else {}
                )
                yield RuntimeEventEnvelope(
                    execution_id=handle.execution_id,
                    runtime_session=handle.runtime_session,
                    sequence=index,
                    event_type=event_type,
                    observed_at=datetime(2026, 10, 25, tzinfo=UTC) + timedelta(seconds=15 * index),
                    payload=payload,
                )

        async def cancel(self, request):
            self.calls.append("cancel")
            assert request.execution_id == "exec_018f47c1-7b2c-7abc-8def-123456789008"
            assert request.runtime_session == self.session
            return RuntimeControlAck(
                execution_id=request.execution_id,
                state=RuntimeControlAckState.REQUESTED,
                observed_runtime_status=RuntimeStatus.CANCELLED,
            )

        async def inspect(self, handle):
            self.calls.append("inspect")
            assert self.request is not None
            return RuntimeExecutionInspection(
                execution_id=handle.execution_id,
                runtime_session=handle.runtime_session,
                runtime_status=(
                    RuntimeStatus.CANCELLED
                    if script == "cancellation"
                    else RuntimeStatus.FAILED
                    if script == "runtime-failure"
                    else RuntimeStatus.RUNNING
                    if script == "uncertain-admission"
                    else RuntimeStatus.SUCCEEDED
                ),
                terminal=script != "uncertain-admission",
                provenance=RuntimeProvenance(
                    runtime_id=runtime_descriptor.runtime_id,
                    adapter_version=runtime_descriptor.adapter_version,
                    runtime_version=runtime_descriptor.runtime_version,
                    api_generation=runtime_descriptor.api_generation,
                    requested_provider_id=runtime_selection.requested_provider_id,
                    requested_model_id=runtime_selection.requested_model_id,
                    actual_provider_id=runtime_selection.requested_provider_id,
                    actual_model_id=runtime_selection.requested_model_id,
                    identity_completeness=RuntimeIdentityCompleteness.FULL,
                ),
                continuity=EventContinuity(state=RuntimeContinuityState.COMPLETE),
                usage=RuntimeUsage(),
            )

    workspace = ScriptedWorkspace()
    runtime = ScriptedRuntime()

    def evaluate_final_admission(*_args):
        trace.append("final-admission")
        return AdmissionEvidence(status=CodingAdmissionStatus.ADMIT)

    actual_freshness_check = coordinator_module.check_candidate_freshness

    def check_final_freshness(*args):
        trace.append("final-freshness")
        return actual_freshness_check(*args)

    monkeypatch.setattr(coordinator_module, "evaluate_admission", evaluate_final_admission)
    monkeypatch.setattr(coordinator_module, "check_candidate_freshness", check_final_freshness)
    monkeypatch.setattr(
        coordinator_module,
        "evaluate_workspace_conformance",
        lambda *_args, **_kwargs: WorkspaceConformance(
            status=RequirementStatus.SATISFIED,
            reasons=(),
            unsatisfied_property_keys=(),
            indeterminate_property_keys=(),
        ),
    )

    def materialize_packet(
        exact_candidate: AuthorityCandidate,
        exact_grant: HumanGrantBinding,
    ) -> MaterializedWorkPacket:
        assert exact_candidate.content_digest == exact_grant.authority_candidate_digest
        return MaterializedWorkPacket(
            packet=packet_value,
            context_manifest=context,
            conformance_facts=conforming_facts(packet_value, context),
            materialization_facts=materialization_facts_for(packet_value, context),
        )

    def materialize_payload(exact_packet, packet_ref, exact_context, context_ref):
        payload = RuntimeInputPayload(
            text="Only exact authorized packet context is sent.",
            payload_digest="sha256:" + "c" * 64,
        )
        payload = payload.model_copy(
            update={"payload_digest": digest_runtime_payload_content(payload)}
        )
        return MaterializedRuntimePayload(
            payload=payload,
            evidence=RuntimePayloadEvidence(
                work_packet_ref=packet_ref,
                context_manifest_ref=context_ref,
                payload_digest=payload.payload_digest,
                included_context_keys=exact_packet.required_context_keys,
                status=RequirementStatus.SATISFIED,
                protected_content_exposed=False,
                evaluator_only_content_exposed=False,
                credential_exposure_status="CLEAR",
                evidence_digest="sha256:" + "d" * 64,
            ),
        )

    admission = AdmissionInputs.model_construct(
        compilation=compilation,
        candidate=candidate,
        current_snapshot=snapshot,
        grant=grant,
        reservations=(),
        role_contract=role,
        actor=ActorRef(
            id="act_018f47c1-7b2c-7abc-8def-123456789008",
            kind=ActorKind.AGENT,
        ),
    )
    inputs = CoordinatorInputs(
        admission=admission,
        authorized_slice_id=packet_value.slice_definition_ref.slice_id,
        work_packet_materializer=materialize_packet,
        workspace_policy=policy,
        protected_authority_facts=(),
        plan_key="fake-runtime-plan",
        plan_revision=1,
        runtime_permission_evidence=RuntimePermissionEvidence(
            execution_id="exec_018f47c1-7b2c-7abc-8def-123456789008",
            runtime_id=runtime_descriptor.runtime_id,
            attestation_id="fake-permission-attestation",
            evidence_digest="sha256:" + "e" * 64,
            effective_profile_ref=permission_ref,
            completeness=RequirementStatus.SATISFIED,
            exposed_tools=(),
            unknown_tool_identity=False,
            shell_exposed=False,
            actual_provider_id=(
                "different-provider"
                if script == "provider-model-mismatch"
                else runtime_selection.requested_provider_id
            ),
            actual_model_id=runtime_selection.requested_model_id,
            provenance_status=RequirementStatus.SATISFIED,
        ),
        runtime_payload_materializer=materialize_payload,
        permission_profile_ref=permission_ref,
        evidence_refs=()
        if script == "incomplete-evidence"
        else tuple(
            sorted(
                item.key
                for item in (
                    *packet_value.evidence_requirements,
                    *packet_value.deliverable_requirements,
                )
                if item.required
            )
        ),
        protected_verification_projection_refs=tuple(
            sorted(
                f"protected-verification-{index}"
                for index, _item in enumerate(
                    packet_value.protected_verification_requirements, start=1
                )
            )
        ),
        external_effects_status="CLEAR",
        credential_exposure_status="CLEAR",
        workspace_facts_factory=lambda *_args: workspace.workspace_facts,
        terminal_workspace_facts_factory=lambda *_args: workspace.workspace_facts,
        current_snapshot_reader=lambda: snapshot,
        grant_reservation_reader=lambda: (grant, ()),
        boundary_nonce_factory=(lambda: "fake-launch-nonce") if boundary_mode else None,
        boundary_runtime_launcher=workspace if boundary_mode else None,
        cancellation_requested=(lambda: True) if script == "cancellation" else None,
    )

    if expected_outcome == "PRE_ADMISSION_DENY":
        with pytest.raises(AdmissionRejected) as rejection:
            asyncio.run(
                execute_governed_attempt(
                    inputs,
                    cast(WorkspaceProvider, workspace),
                    cast(AgentRuntime, runtime),
                )
            )
        if script in {"provider-model-mismatch", "configuration-mismatch"}:
            assert runtime.calls.count("create-session") == 1
            assert runtime.calls.count("close-prepared-session") == 1
            assert rejection.value.trusted_local_failure is not None
            assert rejection.value.trusted_local_failure.cleanup.status.value == "SATISFIED"
        else:
            assert "create-session" not in runtime.calls
        assert "open-execution" not in runtime.calls
        if boundary_mode:
            assert runtime.calls.count("create_session_v2") == 1
            assert "open_execution_v2" not in runtime.calls
            assert "open-execution" not in runtime.calls
            assert workspace.calls.count("teardown-runtime") == 1
            assert rejection.value.boundary_failure is not None
            assert rejection.value.boundary_failure.session is not None
            assert rejection.value.boundary_failure.teardown is not None
        return

    result = asyncio.run(
        execute_governed_attempt(
            inputs,
            cast(WorkspaceProvider, workspace),
            cast(AgentRuntime, runtime),
        )
    )

    assert result.execution_id == "exec_018f47c1-7b2c-7abc-8def-123456789008"
    assert result.subject.intended_attempt_id == "exec-018f47c1-7b2c-7abc-8def-123456789008"
    assert result.subject.work_packet_ref == result.subject.workspace_plan_ref.work_packet_ref
    assert result.evidence.runtime_handle is not None
    assert result.evidence.runtime_inspection is not None
    assert result.outcome.value == expected_outcome
    if boundary_mode:
        assert "open-execution" not in runtime.calls
    else:
        assert runtime.calls.count("open-execution") == 1
    assert "opencode" not in runtime.calls
    assert result.evidence.execution_subject_digest == result.subject.content_digest
    if script == "capture-unavailable":
        assert result.outcome.value == "BLOCKED_BY_CONTRACT"
        assert result.evidence.stable_candidate_capture is None
        assert result.evidence.stable_candidate_status is RequirementStatus.INDETERMINATE
    else:
        assert result.evidence.stable_candidate_capture is not None
        assert result.evidence.stable_candidate_status is RequirementStatus.SATISFIED
    if script == "cancellation":
        assert runtime.calls.count("cancel") == 1
        assert result.evidence.cancellation_ack is not None
    if script == "boundary-success":
        assert result.subject.execution_profile.value == "RELAY_MANAGED_STRONG_BOUNDARY"
        assert result.subject.runtime_configuration_binding_ref is None
        assert runtime.calls.count("create_session_v2") == 1
        assert runtime.calls.count("attest_permissions_v2") == 1
        assert runtime.calls.count("open_execution_v2") == 1
        expected_order = (
            "launch_runtime",
            "create_session_v2",
            "attest_permissions_v2",
            "final-admission",
            "final-freshness",
            "open_execution_v2",
        )
        assert tuple(item for item in trace if item in expected_order) == expected_order
        assert result.subject.runtime_request_v2 is not None
        assert result.subject.runtime_placement_attestation is not None
        assert result.subject.runtime_permission_attestation_ref is not None
        assert result.evidence.runtime_placement_continuity is not None
        assert result.evidence.runtime_process_teardown is not None
        assert result.subject.runtime_request_v2.endpoint_identity.startswith("https://executor.")
        assert RuntimeCapability.EFFECTIVE_PERMISSION_ATTESTATION in runtime_descriptor.capabilities
    elif not boundary_mode:
        assert result.subject.execution_profile.value == "TRUSTED_LOCAL_EXECUTION"
        assert result.subject.runtime_request_v2 is None
        assert result.subject.workspace_boundary_ref is None
        assert result.subject.runtime_placement_attestation is None
        assert result.subject.runtime_permission_attestation is None
        assert result.subject.runtime_configuration_binding_ref is not None
        assert trace.index("configuration-binding") < trace.index("create_session_prompt_free")
        assert trace.index("create_session_prompt_free") < trace.index("final-admission")
        assert trace.index("final-admission") < trace.index("final-freshness")
        assert trace.index("final-freshness") < trace.index("open_execution")
