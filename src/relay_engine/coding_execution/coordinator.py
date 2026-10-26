"""Small deterministic coordinator over the accepted Relay slice contracts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass

from relay_engine.agent_runtime import (
    AgentRuntime,
    RuntimeCancelRequest,
    RuntimeContinuityState,
    RuntimeEventEnvelope,
    RuntimeEventType,
    RuntimeExecutionBasis,
    RuntimeExecutionHandle,
    RuntimeExecutionInspection,
    RuntimeExecutionRequest,
    RuntimeInputPayload,
    RuntimePermissionProfileRef,
    RuntimeSessionRef,
    RuntimeStatus,
    digest_execution_basis,
)
from relay_engine.coding_execution.evaluation import (
    AdmissionInputs,
    apply_scope_and_successor_disposition,
    evaluate_admission,
    evaluate_effective_tool_exposure,
    evaluate_grant_and_reservations,
    evaluate_packet_before_workspace,
    evaluate_runtime_payload_evidence,
    evaluate_runtime_tool_events,
)
from relay_engine.coding_execution.models import (
    AdmissionStatus,
    ConsumableReservationBinding,
    ContractGapAnalysis,
    ExecutionEvidenceBundle,
    ExecutionSubject,
    ExecutionTerminalOutcome,
    HumanGrantBinding,
    InternalProgressObservation,
    ProposedWorkObservation,
    RuntimePayloadEvidence,
    RuntimePermissionEvidence,
    StableExecutionKey,
    TerminalExecutionResult,
    digest_evaluator_handoff,
    execution_id_for_attempt,
)
from relay_engine.domain import ContentDigest, SliceId
from relay_engine.execution_workspace import (
    WorkspaceProvider,
    derive_runtime_workspace_attachment,
    evaluate_workspace_conformance,
    evaluate_workspace_preflight,
    resolve_workspace_plan,
)
from relay_engine.execution_workspace.evaluation import workspace_plan_ref, workspace_provider_ref
from relay_engine.execution_workspace.models import (
    ProtectedVerificationAuthorityFact,
    WorkPacketConformanceFact,
    WorkspaceConformanceFacts,
    WorkspaceInspection,
    WorkspaceInstanceRef,
    WorkspacePolicyDefinition,
)
from relay_engine.project_state import (
    AuthorityCandidate,
    CandidateFreshnessStatus,
    ResolutionSnapshot,
    check_candidate_freshness,
)
from relay_engine.role_contracts import (
    RequirementStatus,
    SuccessorResolution,
)
from relay_engine.work_packets import (
    ContextManifest,
    ContextManifestRef,
    ContextMaterializationFact,
    WorkPacket,
    WorkPacketConformanceFacts,
    WorkPacketRef,
    context_manifest_ref,
    evaluate_context_conformance,
    evaluate_work_packet_conformance,
    work_packet_ref,
)


@dataclass(frozen=True)
class MaterializedWorkPacket:
    """Exact packet/context values materialized after grant verification."""

    packet: WorkPacket
    context_manifest: ContextManifest
    conformance_facts: WorkPacketConformanceFacts
    materialization_facts: tuple[ContextMaterializationFact, ...]


@dataclass(frozen=True)
class MaterializedRuntimePayload:
    """Prompt payload plus evidence tied to the exact conformed packet context."""

    payload: RuntimeInputPayload
    evidence: RuntimePayloadEvidence


type WorkspaceFactsFactory = Callable[..., WorkspaceConformanceFacts]
type WorkPacketMaterializer = Callable[
    [AuthorityCandidate, HumanGrantBinding], MaterializedWorkPacket
]
type RuntimePayloadMaterializer = Callable[
    [WorkPacket, WorkPacketRef, ContextManifest, ContextManifestRef], MaterializedRuntimePayload
]
type SnapshotReader = Callable[[], ResolutionSnapshot]
type GrantReservationReader = Callable[
    [], tuple[HumanGrantBinding | None, tuple[ConsumableReservationBinding, ...]]
]


class AdmissionRejected(RuntimeError):
    """Fail-closed preflight stop before any runtime prompt is admitted."""

    def __init__(self, outcome: ExecutionTerminalOutcome, reason: str) -> None:
        super().__init__(reason)
        self.outcome = outcome
        self.reason = reason


@dataclass(frozen=True)
class CoordinatorInputs:
    """Already-materialized, immutable records needed for one attempt."""

    admission: AdmissionInputs
    authorized_slice_id: SliceId
    work_packet_materializer: WorkPacketMaterializer | None
    workspace_policy: WorkspacePolicyDefinition
    protected_authority_facts: tuple[ProtectedVerificationAuthorityFact, ...]
    plan_key: str
    plan_revision: int
    runtime_permission_evidence: RuntimePermissionEvidence
    runtime_payload_materializer: RuntimePayloadMaterializer | None
    permission_profile_ref: RuntimePermissionProfileRef
    validation_evidence_refs: tuple[StableExecutionKey, ...] = ()
    evidence_refs: tuple[StableExecutionKey, ...] = ()
    protected_verification_projection_refs: tuple[StableExecutionKey, ...] = ()
    proposed_work: tuple[ProposedWorkObservation, ...] = ()
    progress_observations: tuple[InternalProgressObservation, ...] = ()
    contract_gaps: tuple[ContractGapAnalysis, ...] = ()
    successor_resolution: SuccessorResolution | None = None
    cancellation_requested: Callable[[], bool] | None = None
    external_effects_status: str = "UNKNOWN"
    credential_exposure_status: str = "NOT_APPLICABLE"
    workspace_facts_factory: WorkspaceFactsFactory | None = None
    terminal_workspace_facts_factory: WorkspaceFactsFactory | None = None
    current_snapshot_reader: SnapshotReader | None = None
    grant_reservation_reader: GrantReservationReader | None = None


def _digest_json(value: object) -> ContentDigest:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def derive_workspace_change_state(
    instance: WorkspaceInstanceRef,
    inspection: WorkspaceInspection,
) -> tuple[bool, str | None, str | None]:
    """Return dirty state and exact local commit/parent identities."""

    if inspection.instance_ref != instance:
        raise ValueError("inspection must bind the exact workspace instance")
    dirty = bool(inspection.tracked_changes or inspection.untracked_paths)
    has_new_commit = inspection.head_commit != instance.source_commit
    return (
        dirty,
        inspection.head_commit.sha if has_new_commit else None,
        instance.source_commit.sha if has_new_commit else None,
    )


def runtime_event_stream_is_contiguous(
    events: tuple[RuntimeEventEnvelope, ...],
    execution_id: str,
    runtime_session: RuntimeSessionRef,
) -> bool:
    """Check contiguous one-based events bound to the intended exact session."""

    return all(
        event.execution_id == execution_id
        and event.runtime_session == runtime_session
        and event.event_type is not RuntimeEventType.EVENT_GAP
        for event in events
    ) and tuple(event.sequence for event in events) == tuple(range(1, len(events) + 1))


def runtime_output_limit_contract_gap(
    request: RuntimeExecutionRequest,
) -> ContractGapAnalysis | None:
    """Describe the exact Slice 2.1 output-byte evidence gap when required."""

    if request.basis.limits.max_output_bytes is None:
        return None
    values: dict[str, str] = {
        "owning_slice": "slice-2-1",
        "contract_reference": "agent-runtime-runtime-usage",
        "required_behavior": "Prove the exact output byte count for the governed runtime request.",
        "failing_scenario": (
            "A WorkPacket declares max_output_bytes, but terminal inspection has no byte total."
        ),
        "missing_contract_element": "Exact terminal output byte usage evidence.",
        "composition_failure": (
            "RuntimeUsage reports token totals only; summaries and output refs do not prove bytes."
        ),
        "minimum_amendment": (
            "Add a runtime-owned exact output-byte usage observation bound to ExecutionId."
        ),
        "security_consequences": (
            "Without the metric Relay cannot prove that the declared output limit was enforced."
        ),
    }
    return ContractGapAnalysis(
        owning_slice=values["owning_slice"],
        contract_reference=values["contract_reference"],
        required_behavior=values["required_behavior"],
        failing_scenario=values["failing_scenario"],
        missing_contract_element=values["missing_contract_element"],
        composition_failure=values["composition_failure"],
        minimum_amendment=values["minimum_amendment"],
        security_consequences=values["security_consequences"],
        analysis_digest=_digest_json(values),
    )


async def execute_governed_attempt(
    inputs: CoordinatorInputs,
    workspace_provider: WorkspaceProvider,
    runtime: AgentRuntime,
) -> TerminalExecutionResult:
    """Run one exact, already-authorized attempt and return evaluator evidence.

    This function never creates authority or consumable reservations. It computes
    the WorkPacketRef only after exact packet/context conformance, then passes
    that ref to the Slice 2.4 resolver.
    """

    admission = inputs.admission
    candidate = admission.candidate
    attempt = candidate.request.intended_attempt_id
    if attempt is None:
        raise ValueError("candidate has no intended_attempt_id")
    execution_id = execution_id_for_attempt(attempt)
    grant = admission.grant
    grant_check = evaluate_grant_and_reservations(
        admission.compilation,
        candidate,
        admission.current_snapshot,
        grant,
        admission.reservations,
        project_id=candidate.resolution.snapshot.project_id,
        slice_id=inputs.authorized_slice_id,
    )
    if grant_check.status is not AdmissionStatus.ADMIT:
        return _blocked_result(
            inputs,
            execution_id,
            "grant-reservation:" + grant_check.status.value,
        )
    assert grant is not None

    if inputs.work_packet_materializer is None:
        return _blocked_result(inputs, execution_id, "work-packet:materializer-missing")
    materialized = inputs.work_packet_materializer(candidate, grant)
    admission = admission.model_copy(
        update={
            "work_packet": materialized.packet,
            "context_manifest": materialized.context_manifest,
            "work_packet_facts": materialized.conformance_facts,
            "context_materialization_facts": materialized.materialization_facts,
        }
    )

    packet = admission.work_packet
    manifest = admission.context_manifest
    assert packet is not None and manifest is not None
    assert admission.work_packet_facts is not None
    packet_check = evaluate_packet_before_workspace(
        grant,
        candidate,
        packet,
        manifest,
        admission.work_packet_facts,
        admission.context_materialization_facts,
    )
    if packet_check.status is not AdmissionStatus.ADMIT:
        return _blocked_result(inputs, execution_id, "work-packet:" + packet_check.status.value)
    context_result = evaluate_context_conformance(
        packet, manifest, admission.context_materialization_facts
    )
    packet_result = evaluate_work_packet_conformance(packet, manifest, admission.work_packet_facts)
    if context_result.status is not RequirementStatus.SATISFIED or (
        packet_result.status is not RequirementStatus.SATISFIED
    ):
        return _blocked_result(inputs, execution_id, "work-packet:conformance")

    # This exact ref exists before resolve_workspace_plan is invoked.
    packet_ref = work_packet_ref(packet)
    manifest_ref = context_manifest_ref(manifest)
    if inputs.runtime_payload_materializer is None:
        return _blocked_result(inputs, execution_id, "context:runtime-payload-materializer-missing")
    materialized_payload = inputs.runtime_payload_materializer(
        packet, packet_ref, manifest, manifest_ref
    )
    payload_check = evaluate_runtime_payload_evidence(
        packet,
        packet_ref,
        manifest_ref,
        materialized_payload.payload,
        materialized_payload.evidence,
    )
    if payload_check.status is not AdmissionStatus.ADMIT:
        return _blocked_result(
            inputs, execution_id, "context:runtime-payload:" + payload_check.status.value
        )
    packet_fact = WorkPacketConformanceFact(
        evaluated_work_packet_ref=packet_ref,
        conformance=packet_result,
    )
    provider_descriptor = workspace_provider.describe()
    plan_resolution = resolve_workspace_plan(
        packet,
        packet_ref,
        packet_fact,
        inputs.workspace_policy,
        admission.role_contract,
        inputs.protected_authority_facts,
        provider_descriptor,
        plan_key=inputs.plan_key,
        revision=inputs.plan_revision,
    )
    if plan_resolution.status is not RequirementStatus.SATISFIED or plan_resolution.plan is None:
        return _blocked_result(inputs, execution_id, "workspace:plan-resolution")
    plan = plan_resolution.plan
    provider_ref = workspace_provider_ref(provider_descriptor)
    preflight = evaluate_workspace_preflight(plan, provider_descriptor)
    if preflight.status is not RequirementStatus.SATISFIED:
        return _blocked_result(inputs, execution_id, "workspace:preflight")

    provision = workspace_provider.provision(plan)
    attachment = derive_runtime_workspace_attachment(provision.instance_ref)
    if attachment != provision.runtime_attachment:
        return _blocked_result(inputs, execution_id, "workspace:attachment-mismatch")
    if inputs.workspace_facts_factory is None:
        return _blocked_result(inputs, execution_id, "workspace:conformance-facts-missing")
    workspace_facts = inputs.workspace_facts_factory(
        plan_resolution, provision, provider_descriptor
    )
    workspace_result = evaluate_workspace_conformance(
        plan, provision.instance_ref, provider_ref, workspace_facts
    )
    if workspace_result.status is not RequirementStatus.SATISFIED:
        return _blocked_result(inputs, execution_id, "workspace:conformance")

    descriptor = await runtime.describe()
    selection = packet.runtime_selection_requirement
    if selection is None:
        return _blocked_result(inputs, execution_id, "runtime:selection-missing")
    if descriptor.runtime_id != selection.runtime_id:
        return _blocked_result(inputs, execution_id, "runtime:identity-mismatch")
    if not set(packet.required_runtime_capabilities).issubset(set(descriptor.capabilities)):
        return _blocked_result(inputs, execution_id, "runtime:capability-mismatch")
    if inputs.permission_profile_ref != packet.runtime_permission_profile_ref:
        return _blocked_result(inputs, execution_id, "runtime:permission-profile-mismatch")
    if (
        inputs.runtime_permission_evidence.actual_provider_id != selection.requested_provider_id
        or inputs.runtime_permission_evidence.actual_model_id != selection.requested_model_id
    ):
        return _blocked_result(inputs, execution_id, "runtime:provider-model-identity-unbound")
    exposure = evaluate_effective_tool_exposure(
        plan,
        inputs.runtime_permission_evidence,
        expected_execution_id=execution_id,
        expected_runtime_id=descriptor.runtime_id,
    )
    if exposure.status is not AdmissionStatus.ADMIT:
        return _blocked_result(inputs, execution_id, "runtime:effective-permission-unproven")
    if inputs.runtime_permission_evidence.effective_profile_ref != inputs.permission_profile_ref:
        return _blocked_result(inputs, execution_id, "runtime:effective-profile-mismatch")

    basis = RuntimeExecutionBasis(
        execution_id=execution_id,
        slice_id=packet.slice_definition_ref.slice_id,
        source_baseline_id=packet.source_baseline_ref.baseline_id,
        workspace=attachment,
        input_payload=materialized_payload.payload,
        runtime_selection=selection,
        permission_profile_ref=inputs.permission_profile_ref,
        credential_refs=packet.credential_refs,
        required_capabilities=packet.required_runtime_capabilities,
        limits=packet.runtime_limits,
    )
    request = RuntimeExecutionRequest(basis=basis, request_digest=digest_execution_basis(basis))

    pre_admission_inspection = workspace_provider.inspect(provision.instance_ref)
    if pre_admission_inspection.model_dump(exclude={"inspected_at"}) != (
        provision.initial_inspection.model_dump(exclude={"inspected_at"})
    ):
        return _blocked_result(inputs, execution_id, "workspace:changed-before-admission")
    if inputs.current_snapshot_reader is None or inputs.grant_reservation_reader is None:
        return _blocked_result(inputs, execution_id, "admission:final-revalidation-unavailable")
    latest_snapshot = inputs.current_snapshot_reader()
    latest_grant, latest_reservations = inputs.grant_reservation_reader()
    staged = admission.model_copy(
        update={
            "provider_runtime_status": RequirementStatus.SATISFIED,
            "workspace_status": RequirementStatus.SATISFIED,
            "runtime_descriptor": descriptor,
            "permission_evidence": inputs.runtime_permission_evidence,
            "workspace_plan": plan,
            "current_snapshot": latest_snapshot,
            "grant": latest_grant,
            "reservations": latest_reservations,
        }
    )
    final_admission = evaluate_admission(staged)
    if final_admission.status is not AdmissionStatus.ADMIT:
        return _blocked_result(inputs, execution_id, "admission:" + final_admission.status.value)
    freshness = check_candidate_freshness(candidate, latest_snapshot)
    if freshness.status is not CandidateFreshnessStatus.CURRENT:
        return _blocked_result(inputs, execution_id, "candidate:final-freshness-failed")

    assert staged.grant is not None
    subject = ExecutionSubject(
        project_id=packet.project_id,
        slice_id=packet.slice_definition_ref.slice_id,
        candidate_digest=candidate.content_digest,
        human_grant=staged.grant,
        intended_attempt_id=attempt,
        execution_id=execution_id,
        work_packet=packet,
        work_packet_ref=packet_ref,
        context_manifest_ref=context_manifest_ref(manifest),
        role_contract_ref=packet.role_contract_ref,
        actor=admission.actor,
        workspace_plan_ref=workspace_plan_ref(plan),
        workspace_instance=provision.instance_ref,
        runtime_workspace_attachment=attachment,
        workspace_provider_ref=provider_ref,
        runtime_descriptor=descriptor,
        runtime_request=request,
        runtime_payload_evidence=materialized_payload.evidence,
        runtime_permission_evidence=inputs.runtime_permission_evidence,
        corrective_subject_binding=admission.corrective_subject_binding,
        actual_provider_id=inputs.runtime_permission_evidence.actual_provider_id,
        actual_model_id=inputs.runtime_permission_evidence.actual_model_id,
        reservations=staged.reservations,
        control_references=tuple(sorted(packet.required_workspace_property_keys)),
        resource_references=tuple(sorted(inputs.admission.candidate.work_packet_constraints)),
    )

    session = await runtime.create_session(request)
    if session.execution_id != execution_id or session.request_digest != request.request_digest:
        return _blocked_result(inputs, execution_id, "runtime:session-binding-mismatch")
    handle = await runtime.open_execution(request, session)
    if handle.execution_id != execution_id or handle.request_digest != request.request_digest:
        return _blocked_result(inputs, execution_id, "runtime:handle-binding-mismatch")
    observed_events: list[RuntimeEventEnvelope] = []
    cancellation_ack = None
    cancellation_sent = False
    async for event in runtime.events(handle):
        observed_events.append(event)
        if (
            inputs.cancellation_requested is not None
            and inputs.cancellation_requested()
            and not cancellation_sent
        ):
            cancellation_ack = await runtime.cancel(
                RuntimeCancelRequest(
                    execution_id=execution_id,
                    runtime_session=session.runtime_session,
                    reason="Human cancellation requested",
                )
            )
            cancellation_sent = True
    if (
        inputs.cancellation_requested is not None
        and inputs.cancellation_requested()
        and not cancellation_sent
    ):
        cancellation_ack = await runtime.cancel(
            RuntimeCancelRequest(
                execution_id=execution_id,
                runtime_session=session.runtime_session,
                reason="Human cancellation requested",
            )
        )
        cancellation_sent = True
    events = tuple(observed_events)
    inspection = await runtime.inspect(handle)
    event_bindings_valid = runtime_event_stream_is_contiguous(
        events,
        execution_id,
        session.runtime_session,
    )
    changes = workspace_provider.extract_changes(provision.instance_ref)
    terminal_inspection = workspace_provider.inspect(provision.instance_ref)
    if terminal_inspection.instance_ref != provision.instance_ref:
        return _blocked_result(inputs, execution_id, "workspace:terminal-inspection-mismatch")

    terminal_facts = (
        inputs.terminal_workspace_facts_factory(
            plan_resolution,
            provision,
            provider_descriptor,
            terminal_inspection,
            changes,
        )
        if inputs.terminal_workspace_facts_factory is not None
        else None
    )
    terminal_status = (
        evaluate_workspace_conformance(
            plan,
            provision.instance_ref,
            provider_ref,
            terminal_facts,
            terminal=True,
        ).status
        if terminal_facts is not None
        else RequirementStatus.INDETERMINATE
    )
    identity_matches = (
        inspection.execution_id == execution_id
        and inspection.runtime_session == session.runtime_session
        and inspection.provenance.runtime_id == descriptor.runtime_id
        and inspection.provenance.requested_provider_id == selection.requested_provider_id
        and inspection.provenance.requested_model_id == selection.requested_model_id
        and inspection.provenance.actual_provider_id == selection.requested_provider_id
        and inspection.provenance.actual_model_id == selection.requested_model_id
        and inspection.provenance.identity_completeness.value == "FULL"
    )
    continuity_ok = (
        event_bindings_valid and inspection.continuity.state is RuntimeContinuityState.COMPLETE
    )
    event_conformance = evaluate_runtime_tool_events(plan, events)
    outcome = ExecutionTerminalOutcome.DONE
    usage_exhausted, usage_unknown = _evaluate_usage_limits(request, handle, inspection, events)
    contract_gaps_by_digest = {item.analysis_digest: item for item in inputs.contract_gaps}
    output_limit_gap = runtime_output_limit_contract_gap(request)
    if output_limit_gap is not None:
        contract_gaps_by_digest[output_limit_gap.analysis_digest] = output_limit_gap
    if inspection.runtime_status is RuntimeStatus.CANCELLED:
        outcome = ExecutionTerminalOutcome.CANCELLED
    elif cancellation_sent or not inspection.terminal or not continuity_ok:
        outcome = ExecutionTerminalOutcome.INTERRUPTED
    elif usage_exhausted:
        outcome = ExecutionTerminalOutcome.BUDGET_EXHAUSTED
    elif usage_unknown or (
        not identity_matches
        or terminal_status is not RequirementStatus.SATISFIED
        or event_conformance.status is not AdmissionStatus.ADMIT
    ):
        outcome = ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
    elif inspection.runtime_status is not RuntimeStatus.SUCCEEDED:
        outcome = ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT
    outcome, disposition_reasons = apply_scope_and_successor_disposition(
        outcome,
        tuple(item.key for item in packet.hard_stops),
        inputs.proposed_work,
        inputs.successor_resolution,
    )
    required_evidence = {
        item.key
        for item in (*packet.evidence_requirements, *packet.deliverable_requirements)
        if item.required
    }
    supplied_evidence = set(inputs.evidence_refs) | set(inputs.validation_evidence_refs)
    if required_evidence - supplied_evidence:
        outcome = ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
    if (
        packet.protected_verification_requirements
        and not inputs.protected_verification_projection_refs
    ):
        outcome = ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
    if packet.credential_refs and inputs.credential_exposure_status != "CLEAR":
        outcome = ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
    if inputs.external_effects_status != "CLEAR":
        outcome = ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
    subject = subject.model_copy(
        update={
            "actual_provider_id": inspection.provenance.actual_provider_id,
            "actual_model_id": inspection.provenance.actual_model_id,
            "runtime_session": session.runtime_session,
            "runtime_handle": handle,
        }
    )

    initial_digest = _digest_json(provision.initial_inspection.model_dump(mode="json"))
    final_digest = _digest_json(terminal_inspection.model_dump(mode="json"))
    dirty, local_commit, commit_parent = derive_workspace_change_state(
        provision.instance_ref, terminal_inspection
    )
    evidence = ExecutionEvidenceBundle(
        execution_subject_digest=subject.content_digest,
        grant=grant,
        reservations=admission.reservations,
        runtime_request=request,
        runtime_payload_evidence=materialized_payload.evidence,
        runtime_permission_evidence=inputs.runtime_permission_evidence,
        runtime_session=session,
        runtime_handle=handle,
        runtime_inspection=inspection,
        runtime_events=events,
        runtime_event_reasons=event_conformance.reasons,
        cancellation_ack=cancellation_ack,
        workspace_instance=provision.instance_ref,
        initial_workspace_inspection=provision.initial_inspection,
        terminal_workspace_inspection=terminal_inspection,
        terminal_workspace_conformance_status=terminal_status,
        initial_workspace_digest=initial_digest,
        terminal_workspace_digest=final_digest,
        changes=changes,
        validation_evidence_refs=inputs.validation_evidence_refs,
        evidence_refs=inputs.evidence_refs,
        protected_verification_projection_refs=inputs.protected_verification_projection_refs,
        hard_stop_reasons=tuple(
            sorted(item.applicable_hard_stop_key for item in inputs.proposed_work)
        ),
        blockers=tuple(
            sorted(
                set(disposition_reasons)
                | (set() if outcome is ExecutionTerminalOutcome.DONE else {outcome.value})
            )
        ),
        proposed_work=inputs.proposed_work,
        progress_observations=inputs.progress_observations,
        contract_gaps=tuple(
            contract_gaps_by_digest[key] for key in sorted(contract_gaps_by_digest)
        ),
        dirty=dirty,
        local_commit=local_commit,
        commit_parent=commit_parent,
        external_effects_status=inputs.external_effects_status,
        credential_exposure_status=inputs.credential_exposure_status,
    )
    handoff_digest = digest_evaluator_handoff(subject, outcome, evidence)
    return TerminalExecutionResult(
        execution_id=execution_id,
        subject=subject,
        outcome=outcome,
        evidence=evidence,
        evaluator_handoff_digest=handoff_digest,
    )


def _blocked_result(
    inputs: CoordinatorInputs, execution_id: str, reason: str
) -> TerminalExecutionResult:
    """Raise a typed fail-closed stop before runtime/session creation."""

    del inputs, execution_id
    outcome = (
        ExecutionTerminalOutcome.BLOCKED_BY_AUTHORITY
        if reason.startswith(
            ("grant:", "grant-reservation:", "candidate:", "reservation:", "admission:DENY")
        )
        else ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
        if reason.startswith(("work-packet:", "context:", "role:", "runtime:effective"))
        else ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT
    )
    raise AdmissionRejected(outcome, reason)


def _evaluate_usage_limits(
    request: RuntimeExecutionRequest,
    handle: RuntimeExecutionHandle,
    inspection: RuntimeExecutionInspection,
    events: tuple[RuntimeEventEnvelope, ...],
) -> tuple[bool, bool]:
    """Evaluate measurable limits and fail closed where a required metric is absent."""

    limits = request.basis.limits
    if limits.max_tool_calls is not None:
        calls = sum(item.event_type is RuntimeEventType.TOOL_REQUESTED for item in events)
        if calls > limits.max_tool_calls:
            return True, False
    if limits.max_duration_seconds is not None:
        terminal_events = tuple(
            event
            for event in events
            if event.event_type
            in {
                RuntimeEventType.EXECUTION_COMPLETED,
                RuntimeEventType.EXECUTION_FAILED,
                RuntimeEventType.EXECUTION_BLOCKED,
                RuntimeEventType.EXECUTION_CANCELLED,
            }
        )
        stream_is_complete = (
            inspection.terminal
            and inspection.continuity.state is RuntimeContinuityState.COMPLETE
            and runtime_event_stream_is_contiguous(
                events,
                handle.execution_id,
                handle.runtime_session,
            )
            and len(terminal_events) == 1
            and events[-1] == terminal_events[0]
        )
        if not stream_is_complete:
            return False, True
        duration = (terminal_events[0].observed_at - handle.opened_at).total_seconds()
        if duration < 0:
            return False, True
        if duration > limits.max_duration_seconds:
            return True, False
    if limits.max_output_bytes is not None:
        # Slice 2.1 reports token usage and safe summaries, not exact output
        # bytes. Neither can prove a byte cap.
        return False, True
    return False, False
