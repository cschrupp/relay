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
        ("provider-model-mismatch", "PRE_ADMISSION_DENY"),
        ("runtime-identity-mismatch", "PRE_ADMISSION_DENY"),
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
    from relay_engine.execution_workspace.models import (
        WorkspaceChangeManifest,
        WorkspaceConformance,
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
    )

    class ScriptedWorkspace:
        def __init__(self) -> None:
            self.calls: list[str] = []
            self.provision_result = None
            self.workspace_facts = None

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

        def teardown(self, instance_ref):
            self.calls.append("teardown")

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

        async def open_execution(self, request, binding):
            self.calls.append("open-execution")
            return RuntimeExecutionHandle(
                execution_id=request.basis.execution_id,
                runtime_session=binding.runtime_session,
                request_digest=request.request_digest,
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
                "provider-model-mismatch": (
                    RuntimeEventType.EXECUTION_STARTED,
                    RuntimeEventType.EXECUTION_COMPLETED,
                ),
                "runtime-identity-mismatch": (
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

    monkeypatch.setattr(
        coordinator_module,
        "evaluate_admission",
        lambda *_args: AdmissionEvidence(status=CodingAdmissionStatus.ADMIT),
    )
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
        cancellation_requested=(lambda: True) if script == "cancellation" else None,
    )

    if expected_outcome == "PRE_ADMISSION_DENY":
        with pytest.raises(AdmissionRejected):
            asyncio.run(
                execute_governed_attempt(
                    inputs,
                    cast(WorkspaceProvider, workspace),
                    cast(AgentRuntime, runtime),
                )
            )
        assert "create-session" not in runtime.calls
        assert "open-execution" not in runtime.calls
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
    assert runtime.calls.count("open-execution") == 1
    assert "opencode" not in runtime.calls
    assert result.evidence.execution_subject_digest == result.subject.content_digest
    if script == "cancellation":
        assert runtime.calls.count("cancel") == 1
        assert result.evidence.cancellation_ack is not None
