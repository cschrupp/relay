"""Small deterministic coordinator over the accepted Relay slice contracts."""

from __future__ import annotations

import hashlib
import json
import secrets
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import NoReturn, cast

from relay_engine.agent_runtime import (
    AgentRuntime,
    RuntimeCancelRequest,
    RuntimeCapability,
    RuntimeContinuityState,
    RuntimeDescriptor,
    RuntimeEventEnvelope,
    RuntimeEventType,
    RuntimeExecutionBasis,
    RuntimeExecutionHandle,
    RuntimeExecutionInspection,
    RuntimeExecutionRequest,
    RuntimeInputPayload,
    RuntimePermissionProfileRef,
    RuntimeSessionBinding,
    RuntimeSessionRef,
    RuntimeStatus,
    digest_execution_basis,
)
from relay_engine.agent_runtime.boundary import (
    RuntimeEvidenceCompleteness,
    RuntimeLaunchSubject,
    RuntimePermissionAttestation,
    RuntimeRequestV2,
    build_runtime_request_v2,
)
from relay_engine.agent_runtime.opencode import OpenCodeConfigurationBinding
from relay_engine.agent_runtime.protocol import BoundaryManagedAgentRuntime
from relay_engine.coding_execution.evaluation import (
    AdmissionInputs,
    apply_scope_and_successor_disposition,
    candidate_configuration_qualification_ref,
    candidate_execution_profile,
    evaluate_admission,
    evaluate_effective_tool_exposure,
    evaluate_grant_and_reservations,
    evaluate_packet_before_workspace,
    evaluate_runtime_payload_evidence,
    evaluate_runtime_tool_events,
    evaluate_trusted_local_runtime_controls,
)
from relay_engine.coding_execution.models import (
    AdmissionStatus,
    CleanupStatus,
    ConsumableReservationBinding,
    ContractGapAnalysis,
    ExecutionEvidenceBundle,
    ExecutionProfile,
    ExecutionSubject,
    ExecutionTerminalOutcome,
    HumanGrantBinding,
    InternalProgressObservation,
    PermissionEvidenceProvenance,
    PromptFreeSessionCleanupEvidence,
    ProposedWorkObservation,
    RuntimeEvidenceBindingRef,
    RuntimePayloadEvidence,
    RuntimePermissionEvidence,
    StableExecutionKey,
    TerminalExecutionResult,
    digest_evaluator_handoff,
    digest_execution_profile_binding,
    digest_runtime_permission_evidence,
    execution_id_for_attempt,
)
from relay_engine.domain import ContentDigest, SliceId
from relay_engine.domain._base import DomainModel
from relay_engine.execution_workspace import (
    BoundaryScopedRuntimeLauncher,
    WorkspaceProvider,
    derive_runtime_workspace_attachment,
    evaluate_workspace_conformance,
    evaluate_workspace_preflight,
    resolve_workspace_plan,
)
from relay_engine.execution_workspace.boundary import (
    RuntimePlacementAttestation,
    RuntimePlacementContinuityEvidence,
    RuntimeProcessTeardownEvidence,
    WorkspaceBoundaryRef,
    placement_attestation_matches_boundary,
)
from relay_engine.execution_workspace.evaluation import workspace_plan_ref, workspace_provider_ref
from relay_engine.execution_workspace.models import (
    ControlStrength,
    ProtectedVerificationAuthorityFact,
    WorkPacketConformanceFact,
    WorkspaceCandidateCapture,
    WorkspaceChangeManifest,
    WorkspaceConformanceFacts,
    WorkspaceInspection,
    WorkspaceInstanceRef,
    WorkspacePlan,
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

    def __init__(
        self,
        outcome: ExecutionTerminalOutcome,
        reason: str,
        *,
        boundary_failure: BoundaryPreparationFailure | None = None,
        trusted_local_failure: TrustedLocalPreparationFailure | None = None,
    ) -> None:
        super().__init__(reason)
        self.outcome = outcome
        self.reason = reason
        self.boundary_failure = boundary_failure
        self.trusted_local_failure = trusted_local_failure


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
    boundary_nonce_factory: Callable[[], str] | None = None
    boundary_runtime_launcher: BoundaryScopedRuntimeLauncher | None = None


@dataclass(frozen=True)
class BoundaryRuntimePreparation:
    """Exact no-prompt V2 session and evidence before final admission."""

    boundary: WorkspaceBoundaryRef
    launch_subject: RuntimeLaunchSubject
    placement: RuntimePlacementAttestation
    request_v2: RuntimeRequestV2
    session: RuntimeSessionBinding
    permission_attestation: RuntimePermissionAttestation
    continuity: RuntimePlacementContinuityEvidence
    permission_evidence: RuntimePermissionEvidence


@dataclass(frozen=True)
class BoundaryPreparationFailure:
    """Exact available preparation evidence retained when admission stops early."""

    boundary: WorkspaceBoundaryRef
    launch_subject: RuntimeLaunchSubject
    placement: RuntimePlacementAttestation
    request_v2: RuntimeRequestV2 | None
    session: RuntimeSessionBinding | None
    permission_attestation: RuntimePermissionAttestation | None
    continuity: RuntimePlacementContinuityEvidence | None
    teardown: RuntimeProcessTeardownEvidence | None
    failure_reason: str
    cleanup_error_type: str | None = None


@dataclass(frozen=True)
class TrustedLocalPreparation:
    """Exact prompt-free OpenCode session and configuration before admission."""

    configuration_binding: OpenCodeConfigurationBinding
    session: RuntimeSessionBinding
    permission_evidence: RuntimePermissionEvidence


@dataclass(frozen=True)
class TrustedLocalPreparationFailure:
    """Retained exact preparation and cleanup evidence after admission rejection."""

    configuration_binding: OpenCodeConfigurationBinding
    session: RuntimeSessionBinding
    permission_evidence: RuntimePermissionEvidence
    cleanup: PromptFreeSessionCleanupEvidence
    failure_reason: str


async def _stop_with_boundary_evidence(
    *,
    launcher: BoundaryScopedRuntimeLauncher,
    boundary: WorkspaceBoundaryRef,
    launch_subject: RuntimeLaunchSubject,
    placement: RuntimePlacementAttestation,
    execution_id: str,
    outcome: ExecutionTerminalOutcome,
    reason: str,
    request_v2: RuntimeRequestV2 | None = None,
    session: RuntimeSessionBinding | None = None,
    permission: RuntimePermissionAttestation | None = None,
    continuity: RuntimePlacementContinuityEvidence | None = None,
) -> NoReturn:
    """Tear down one prepared tree and attach exact partial evidence to the stop."""

    cleanup_error_type = None
    if request_v2 is not None:
        try:
            continuity = launcher.inspect_runtime_continuity(
                boundary,
                placement,
                execution_id=execution_id,
                request_digest_v2=request_v2.request_digest_v2,
            )
        except Exception as error:
            cleanup_error_type = type(error).__name__
    teardown = None
    try:
        teardown = await launcher.teardown_runtime(
            boundary,
            placement,
            execution_id=execution_id,
        )
    except Exception as error:
        cleanup_error_type = type(error).__name__
    failure = BoundaryPreparationFailure(
        boundary=boundary,
        launch_subject=launch_subject,
        placement=placement,
        request_v2=request_v2,
        session=session,
        permission_attestation=permission,
        continuity=continuity,
        teardown=teardown,
        failure_reason=reason,
        cleanup_error_type=cleanup_error_type,
    )
    raise AdmissionRejected(outcome, reason, boundary_failure=failure)


def _canonical_model_digest(value: DomainModel) -> ContentDigest:
    payload = json.dumps(
        value.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _requires_strong_boundary(plan: WorkspacePlan) -> bool:
    return any(
        item.minimum_strength is ControlStrength.BOUNDARY_ENFORCED
        for item in plan.property_requirements
    )


def _permission_evidence_from_attestation(
    attestation: RuntimePermissionAttestation,
) -> RuntimePermissionEvidence:
    completeness = RequirementStatus(attestation.completeness.value)
    return RuntimePermissionEvidence(
        execution_id=attestation.execution_id,
        runtime_id=attestation.session_binding.runtime_session.runtime_id,
        attestation_id=attestation.attestation_id,
        evidence_digest=attestation.content_digest,
        effective_profile_ref=attestation.expected_permission_profile_ref,
        completeness=completeness,
        exposed_tools=attestation.effective_tool_exposure,
        unknown_tool_identity=attestation.unknown_tool_identity,
        shell_exposed=attestation.effective_shell_exposure,
        actual_provider_id=attestation.actual_provider_id,
        actual_model_id=attestation.actual_model_id,
        provenance_status=completeness,
        provenance=PermissionEvidenceProvenance.RUNTIME_OBSERVED,
        session_binding=attestation.session_binding,
    )


def _permission_evidence_from_configuration(
    binding: OpenCodeConfigurationBinding,
    session: RuntimeSessionBinding,
    *,
    execution_id: str,
    runtime_id: str,
) -> RuntimePermissionEvidence:
    """Bind configuration-derived exposure to the exact prompt-free session."""

    completeness = (
        RequirementStatus.SATISFIED
        if binding.status is RequirementStatus.SATISFIED
        and binding.precedence_complete
        and session.actual_identity_status.value == "FULL"
        else RequirementStatus.INDETERMINATE
    )
    evidence = RuntimePermissionEvidence(
        execution_id=execution_id,
        runtime_id=runtime_id,
        attestation_id=binding.binding_id,
        evidence_digest="sha256:" + "0" * 64,
        effective_profile_ref=binding.permission_profile_ref,
        completeness=completeness,
        exposed_tools=binding.effective_tool_exposure,
        unknown_tool_identity=not binding.precedence_complete,
        shell_exposed=binding.shell_exposed,
        actual_provider_id=session.actual_provider_id,
        actual_model_id=session.actual_model_id,
        provenance_status=completeness,
        provenance=PermissionEvidenceProvenance.CONFIGURATION_DERIVED,
        configuration_binding_ref=RuntimeEvidenceBindingRef(
            evidence_id=binding.binding_id,
            content_digest=binding.content_digest,
        ),
        session_binding=session,
    )
    return evidence.model_copy(
        update={"evidence_digest": digest_runtime_permission_evidence(evidence)}
    )


async def _prepare_trusted_local_runtime(
    runtime: AgentRuntime,
    request: RuntimeExecutionRequest,
    descriptor: RuntimeDescriptor,
    accepted_qualification_source_refs: tuple[tuple[str, str], ...],
) -> TrustedLocalPreparation:
    """Resolve qualified OpenCode configuration, then prepare one prompt-free session."""

    prepare = getattr(runtime, "prepare_trusted_local_session", None)
    if not callable(prepare):
        raise AdmissionRejected(
            ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
            "runtime:version-qualified-configuration-observer-missing",
        )
    try:
        prepare_typed = cast(
            Callable[
                [RuntimeExecutionRequest, RuntimeDescriptor, tuple[tuple[str, str], ...]],
                Awaitable[tuple[OpenCodeConfigurationBinding, RuntimeSessionBinding]],
            ],
            prepare,
        )
        configuration, session = await prepare_typed(
            request, descriptor, accepted_qualification_source_refs
        )
    except AdmissionRejected:
        raise
    except Exception as error:
        raise AdmissionRejected(
            ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
            "runtime:trusted-local-configuration-or-session-preparation-failed",
        ) from error
    if type(configuration) is not OpenCodeConfigurationBinding:
        raise AdmissionRejected(
            ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            "runtime:configuration-binding-untyped",
        )
    permission = _permission_evidence_from_configuration(
        configuration,
        session,
        execution_id=request.basis.execution_id,
        runtime_id=descriptor.runtime_id,
    )
    preparation = TrustedLocalPreparation(
        configuration_binding=configuration,
        session=session,
        permission_evidence=permission,
    )
    if (
        session.execution_id != request.basis.execution_id
        or session.request_digest != request.request_digest
        or session.runtime_session.runtime_id != descriptor.runtime_id
        or session.workspace_id != request.basis.workspace.workspace_id
    ):
        await _reject_prepared_trusted_local(
            runtime,
            preparation,
            "runtime:trusted-local-session-binding-mismatch",
            ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
        )
    return preparation


async def _reject_prepared_trusted_local(
    runtime: AgentRuntime,
    preparation: TrustedLocalPreparation,
    reason: str,
    outcome: ExecutionTerminalOutcome,
) -> NoReturn:
    """Clean up a rejected prepared session and retain exact failure evidence."""

    cleanup_method = getattr(runtime, "close_prepared_session", None)
    cleanup_status = RequirementStatus.INDETERMINATE
    cleanup_digest = None
    cleanup_error_type = None
    if callable(cleanup_method):
        try:
            cleanup_typed = cast(
                Callable[[RuntimeSessionBinding], Awaitable[RequirementStatus]],
                cleanup_method,
            )
            cleanup_result = await cleanup_typed(preparation.session)
            cleanup_status = (
                cleanup_result
                if type(cleanup_result) is RequirementStatus
                else RequirementStatus.INDETERMINATE
            )
        except Exception as error:
            cleanup_error_type = type(error).__name__
    cleanup = PromptFreeSessionCleanupEvidence(
        session_binding=preparation.session,
        status=CleanupStatus(cleanup_status.value),
        reason=reason,
        cleanup_acknowledgement_digest=cleanup_digest,
    )
    failure = TrustedLocalPreparationFailure(
        configuration_binding=preparation.configuration_binding,
        session=preparation.session,
        permission_evidence=preparation.permission_evidence,
        cleanup=cleanup,
        failure_reason=(
            reason
            if cleanup_error_type is None
            else reason + ":cleanup-error:" + cleanup_error_type
        ),
    )
    raise AdmissionRejected(
        outcome,
        reason,
        trusted_local_failure=failure,
    )


async def _prepare_boundary_runtime(
    *,
    launcher: BoundaryScopedRuntimeLauncher,
    runtime: AgentRuntime,
    descriptor: RuntimeDescriptor,
    request: RuntimeExecutionRequest,
    candidate: AuthorityCandidate,
    grant: HumanGrantBinding,
    packet: WorkPacket,
    packet_ref: WorkPacketRef,
    manifest_ref: ContextManifestRef,
    plan: WorkspacePlan,
    instance: WorkspaceInstanceRef,
    permission_profile_ref: RuntimePermissionProfileRef,
    nonce_factory: Callable[[], str],
) -> BoundaryRuntimePreparation:
    """Launch in the provider boundary and prepare one exact session without prompt."""

    execution_id = request.basis.execution_id
    intended_attempt_id = candidate.request.intended_attempt_id
    if intended_attempt_id is None:
        raise AdmissionRejected(
            ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            "runtime-boundary:intended-attempt-missing",
        )
    if (
        descriptor.runtime_version is None
        or descriptor.executable_digest is None
        or descriptor.configuration_digest is None
    ):
        raise AdmissionRejected(
            ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
            "runtime-descriptor:version-executable-or-configuration-digest-missing",
        )
    boundary = launcher.boundary_ref(instance)
    if boundary.instance_ref != instance or boundary.plan_ref != workspace_plan_ref(plan):
        raise AdmissionRejected(
            ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            "runtime-boundary:workspace-ref-mismatch",
        )
    selection = request.basis.runtime_selection
    nonce = nonce_factory()
    if not nonce.strip() or len(nonce) > 256:
        raise AdmissionRejected(
            ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            "runtime-boundary:launch-nonce-invalid",
        )
    descriptor_digest = _canonical_model_digest(descriptor)
    plan_ref = workspace_plan_ref(plan)
    launch_subject = RuntimeLaunchSubject(
        execution_id=execution_id,
        intended_attempt_id=intended_attempt_id,
        authority_candidate_digest=candidate.content_digest,
        human_grant_digest=grant.grant_record_digest,
        work_packet_ref_digest=_canonical_model_digest(packet_ref),
        context_manifest_ref_digest=_canonical_model_digest(manifest_ref),
        workspace_plan_ref_digest=_canonical_model_digest(plan_ref),
        workspace_instance_digest=_canonical_model_digest(instance),
        workspace_boundary_digest=boundary.content_digest,
        runtime_descriptor_digest=descriptor_digest,
        runtime_id=descriptor.runtime_id,
        runtime_version=descriptor.runtime_version,
        adapter_id=descriptor.runtime_id,
        adapter_version=descriptor.adapter_version,
        challenge_or_launch_nonce=nonce,
        executable_identity=(
            f"{descriptor.runtime_id}@{descriptor.runtime_version}#{descriptor.executable_digest}"
        ),
        runtime_configuration_digest=descriptor.configuration_digest,
        runtime_api_generation=descriptor.api_generation,
        endpoint_allocation_policy="explicit-loopback-no-discovery-no-credentials",
        requested_provider_id=selection.requested_provider_id,
        requested_model_id=selection.requested_model_id,
        permission_profile_ref=permission_profile_ref,
        credential_reference_ids=tuple(
            sorted(item.credential_id for item in request.basis.credential_refs)
        ),
        runtime_request_payload_digest=request.basis.input_payload.payload_digest,
        runtime_limits_digest=_canonical_model_digest(request.basis.limits),
    )
    placement = await launcher.launch_runtime(boundary, launch_subject)
    if not placement_attestation_matches_boundary(
        boundary,
        placement,
        launch_subject_digest=launch_subject.content_digest,
        runtime_descriptor_digest=descriptor_digest,
        launch_nonce=nonce,
    ):
        await _stop_with_boundary_evidence(
            launcher=launcher,
            boundary=boundary,
            launch_subject=launch_subject,
            placement=placement,
            execution_id=execution_id,
            outcome=ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            reason="runtime-boundary:placement-attestation-invalid",
        )
    request_v2 = build_runtime_request_v2(
        request=request,
        launch_subject=launch_subject,
        placement_attestation_ref=placement.ref,
        endpoint_identity=placement.endpoint_identity,
    )
    managed_runtime = runtime
    for method in ("create_session_v2", "attest_permissions_v2", "open_execution_v2"):
        if not callable(getattr(managed_runtime, method, None)):
            await _stop_with_boundary_evidence(
                launcher=launcher,
                boundary=boundary,
                launch_subject=launch_subject,
                placement=placement,
                execution_id=execution_id,
                outcome=ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
                reason="runtime:boundary-v2-capability-missing",
                request_v2=request_v2,
            )
    boundary_runtime = cast(BoundaryManagedAgentRuntime, managed_runtime)
    try:
        session = await boundary_runtime.create_session_v2(request_v2)
    except Exception as error:
        await _stop_with_boundary_evidence(
            launcher=launcher,
            boundary=boundary,
            launch_subject=launch_subject,
            placement=placement,
            execution_id=execution_id,
            outcome=ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
            reason="runtime:prompt-free-session-creation-failed",
            request_v2=request_v2,
        )
        raise AssertionError("unreachable") from error
    if (
        session.execution_id != execution_id
        or session.request_digest != request.request_digest
        or session.request_digest_v2 != request_v2.request_digest_v2
        or session.runtime_session.runtime_id != descriptor.runtime_id
        or session.workspace_id != instance.workspace_id
    ):
        await _stop_with_boundary_evidence(
            launcher=launcher,
            boundary=boundary,
            launch_subject=launch_subject,
            placement=placement,
            execution_id=execution_id,
            outcome=ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            reason="runtime:session-v2-binding-mismatch",
            request_v2=request_v2,
            session=session,
        )
    try:
        continuity = launcher.inspect_runtime_continuity(
            boundary,
            placement,
            execution_id=execution_id,
            request_digest_v2=request_v2.request_digest_v2,
        )
    except Exception as error:
        await _stop_with_boundary_evidence(
            launcher=launcher,
            boundary=boundary,
            launch_subject=launch_subject,
            placement=placement,
            execution_id=execution_id,
            outcome=ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
            reason="runtime-boundary:pre-admission-continuity-observation-failed",
            request_v2=request_v2,
            session=session,
        )
        raise AssertionError("unreachable") from error
    if (
        continuity.workspace_boundary_ref_digest != boundary.content_digest
        or continuity.placement_attestation_ref != placement.ref
        or continuity.execution_id != execution_id
        or continuity.request_digest_v2 != request_v2.request_digest_v2
        or continuity.process_tree_identity != placement.process_tree_identity
        or continuity.status is not RequirementStatus.SATISFIED
    ):
        await _stop_with_boundary_evidence(
            launcher=launcher,
            boundary=boundary,
            launch_subject=launch_subject,
            placement=placement,
            execution_id=execution_id,
            outcome=ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            reason="runtime-boundary:continuity-unverified-before-admission",
            request_v2=request_v2,
            session=session,
            continuity=continuity,
        )
    try:
        permission = await boundary_runtime.attest_permissions_v2(request_v2, session)
    except Exception as error:
        await _stop_with_boundary_evidence(
            launcher=launcher,
            boundary=boundary,
            launch_subject=launch_subject,
            placement=placement,
            execution_id=execution_id,
            outcome=ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
            reason="runtime:permission-attestation-failed",
            request_v2=request_v2,
            session=session,
            continuity=continuity,
        )
        raise AssertionError("unreachable") from error
    if (
        permission.execution_id != execution_id
        or permission.request_digest_v2 != request_v2.request_digest_v2
        or permission.session_binding != session
        or permission.runtime_descriptor_digest != descriptor_digest
        or permission.launch_subject_digest != launch_subject.content_digest
        or permission.placement_attestation_digest != placement.content_digest
        or permission.expected_permission_profile_ref != permission_profile_ref
        or permission.completeness is not RuntimeEvidenceCompleteness.SATISFIED
        or permission.observed_from < session.created_at
    ):
        await _stop_with_boundary_evidence(
            launcher=launcher,
            boundary=boundary,
            launch_subject=launch_subject,
            placement=placement,
            execution_id=execution_id,
            outcome=ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            reason="runtime:permission-attestation-invalid",
            request_v2=request_v2,
            session=session,
            permission=permission,
            continuity=continuity,
        )
    return BoundaryRuntimePreparation(
        boundary=boundary,
        launch_subject=launch_subject,
        placement=placement,
        request_v2=request_v2,
        session=session,
        permission_attestation=permission,
        continuity=continuity,
        permission_evidence=_permission_evidence_from_attestation(permission),
    )


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
    execution_profile = candidate_execution_profile(candidate)
    if execution_profile is None:
        return _blocked_result(inputs, execution_id, "execution-profile:authority-binding")

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
    boundary_required_by_policy = any(
        item.minimum_strength is ControlStrength.BOUNDARY_ENFORCED
        for item in inputs.workspace_policy.property_requirements
    )
    trusted_local = execution_profile is ExecutionProfile.TRUSTED_LOCAL_EXECUTION
    if boundary_required_by_policy and trusted_local:
        return _blocked_result(inputs, execution_id, "execution-profile:boundary-required")
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
        trusted_local=trusted_local,
    )
    if plan_resolution.status is not RequirementStatus.SATISFIED or plan_resolution.plan is None:
        return _blocked_result(inputs, execution_id, "workspace:plan-resolution")
    plan = plan_resolution.plan
    if (
        _requires_strong_boundary(plan)
        and execution_profile is not ExecutionProfile.RELAY_MANAGED_STRONG_BOUNDARY
    ):
        return _blocked_result(inputs, execution_id, "execution-profile:boundary-required")
    runtime_control_evidence = evaluate_trusted_local_runtime_controls(plan)
    if trusted_local and runtime_control_evidence.status is not AdmissionStatus.ADMIT:
        return _blocked_result(
            inputs,
            execution_id,
            "runtime-control:" + runtime_control_evidence.status.value.lower(),
        )
    provider_ref = workspace_provider_ref(provider_descriptor)
    preflight = evaluate_workspace_preflight(plan, provider_descriptor, trusted_local=trusted_local)
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
        plan,
        provision.instance_ref,
        provider_ref,
        workspace_facts,
        trusted_local=trusted_local,
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

    boundary_preparation: BoundaryRuntimePreparation | None = None
    runtime_permission_evidence = inputs.runtime_permission_evidence
    trusted_preparation: TrustedLocalPreparation | None = None
    if execution_profile is ExecutionProfile.RELAY_MANAGED_STRONG_BOUNDARY:
        if inputs.boundary_runtime_launcher is None:
            return _blocked_result(inputs, execution_id, "runtime:boundary-launcher-missing")
        if RuntimeCapability.EFFECTIVE_PERMISSION_ATTESTATION not in descriptor.capabilities:
            return _blocked_result(
                inputs, execution_id, "runtime:permission-attestation-unsupported"
            )
        try:
            boundary_preparation = await _prepare_boundary_runtime(
                launcher=inputs.boundary_runtime_launcher,
                runtime=runtime,
                descriptor=descriptor,
                request=request,
                candidate=candidate,
                grant=grant,
                packet=packet,
                packet_ref=packet_ref,
                manifest_ref=manifest_ref,
                plan=plan,
                instance=provision.instance_ref,
                permission_profile_ref=inputs.permission_profile_ref,
                nonce_factory=inputs.boundary_nonce_factory or secrets.token_urlsafe,
            )
        except AdmissionRejected:
            raise
        runtime_permission_evidence = boundary_preparation.permission_evidence
    else:
        qualification_ref = candidate_configuration_qualification_ref(candidate)
        if qualification_ref is None:
            return _blocked_result(
                inputs, execution_id, "runtime:accepted-configuration-qualification-invalid"
            )
        trusted_preparation = await _prepare_trusted_local_runtime(
            runtime,
            request,
            descriptor,
            (qualification_ref,),
        )
        runtime_permission_evidence = trusted_preparation.permission_evidence
    boundary_launcher = inputs.boundary_runtime_launcher
    if boundary_preparation is not None:
        assert boundary_launcher is not None, (
            "prepared runtime boundary requires its exact launcher"
        )
    if boundary_preparation is None and (
        (
            runtime_permission_evidence.actual_provider_id is not None
            and runtime_permission_evidence.actual_provider_id != selection.requested_provider_id
        )
        or (
            runtime_permission_evidence.actual_model_id is not None
            and runtime_permission_evidence.actual_model_id != selection.requested_model_id
        )
    ):
        if trusted_preparation is not None:
            await _reject_prepared_trusted_local(
                runtime,
                trusted_preparation,
                "runtime:provider-model-identity-mismatch",
                ExecutionTerminalOutcome.BLOCKED_BY_AUTHORITY,
            )
        return _blocked_result(inputs, execution_id, "runtime:provider-model-identity-mismatch")
    exposure = evaluate_effective_tool_exposure(
        plan,
        runtime_permission_evidence,
        expected_execution_id=execution_id,
        expected_runtime_id=descriptor.runtime_id,
    )
    if exposure.status is not AdmissionStatus.ADMIT:
        if boundary_preparation is not None:
            await _stop_with_boundary_evidence(
                launcher=cast(BoundaryScopedRuntimeLauncher, boundary_launcher),
                boundary=boundary_preparation.boundary,
                launch_subject=boundary_preparation.launch_subject,
                placement=boundary_preparation.placement,
                execution_id=execution_id,
                outcome=ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
                reason="runtime:effective-permission-unproven",
                request_v2=boundary_preparation.request_v2,
                session=boundary_preparation.session,
                permission=boundary_preparation.permission_attestation,
                continuity=boundary_preparation.continuity,
            )
        if trusted_preparation is not None:
            await _reject_prepared_trusted_local(
                runtime,
                trusted_preparation,
                "runtime:effective-permission-unproven",
                ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            )
        return _blocked_result(inputs, execution_id, "runtime:effective-permission-unproven")
    if runtime_permission_evidence.effective_profile_ref != inputs.permission_profile_ref:
        if boundary_preparation is not None:
            await _stop_with_boundary_evidence(
                launcher=cast(BoundaryScopedRuntimeLauncher, boundary_launcher),
                boundary=boundary_preparation.boundary,
                launch_subject=boundary_preparation.launch_subject,
                placement=boundary_preparation.placement,
                execution_id=execution_id,
                outcome=ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
                reason="runtime:effective-profile-mismatch",
                request_v2=boundary_preparation.request_v2,
                session=boundary_preparation.session,
                permission=boundary_preparation.permission_attestation,
                continuity=boundary_preparation.continuity,
            )
        if trusted_preparation is not None:
            await _reject_prepared_trusted_local(
                runtime,
                trusted_preparation,
                "runtime:effective-profile-mismatch",
                ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            )
        return _blocked_result(inputs, execution_id, "runtime:effective-profile-mismatch")

    pre_admission_inspection = workspace_provider.inspect(provision.instance_ref)
    if pre_admission_inspection.model_dump(exclude={"inspected_at"}) != (
        provision.initial_inspection.model_dump(exclude={"inspected_at"})
    ):
        if boundary_preparation is not None:
            await _stop_with_boundary_evidence(
                launcher=cast(BoundaryScopedRuntimeLauncher, boundary_launcher),
                boundary=boundary_preparation.boundary,
                launch_subject=boundary_preparation.launch_subject,
                placement=boundary_preparation.placement,
                execution_id=execution_id,
                outcome=ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
                reason="workspace:changed-before-admission",
                request_v2=boundary_preparation.request_v2,
                session=boundary_preparation.session,
                permission=boundary_preparation.permission_attestation,
                continuity=boundary_preparation.continuity,
            )
        if trusted_preparation is not None:
            await _reject_prepared_trusted_local(
                runtime,
                trusted_preparation,
                "workspace:changed-before-admission",
                ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
            )
        return _blocked_result(inputs, execution_id, "workspace:changed-before-admission")
    if inputs.current_snapshot_reader is None or inputs.grant_reservation_reader is None:
        if boundary_preparation is not None:
            await _stop_with_boundary_evidence(
                launcher=cast(BoundaryScopedRuntimeLauncher, boundary_launcher),
                boundary=boundary_preparation.boundary,
                launch_subject=boundary_preparation.launch_subject,
                placement=boundary_preparation.placement,
                execution_id=execution_id,
                outcome=ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
                reason="admission:final-revalidation-unavailable",
                request_v2=boundary_preparation.request_v2,
                session=boundary_preparation.session,
                permission=boundary_preparation.permission_attestation,
                continuity=boundary_preparation.continuity,
            )
        if trusted_preparation is not None:
            await _reject_prepared_trusted_local(
                runtime,
                trusted_preparation,
                "admission:final-revalidation-unavailable",
                ExecutionTerminalOutcome.BLOCKED_BY_ENVIRONMENT,
            )
        return _blocked_result(inputs, execution_id, "admission:final-revalidation-unavailable")
    latest_snapshot = inputs.current_snapshot_reader()
    latest_grant, latest_reservations = inputs.grant_reservation_reader()
    staged = admission.model_copy(
        update={
            "provider_runtime_status": RequirementStatus.SATISFIED,
            "workspace_status": RequirementStatus.SATISFIED,
            "runtime_descriptor": descriptor,
            "permission_evidence": runtime_permission_evidence,
            "runtime_request": request,
            "execution_profile": execution_profile,
            "runtime_configuration_binding_ref": (
                RuntimeEvidenceBindingRef(
                    evidence_id=trusted_preparation.configuration_binding.binding_id,
                    content_digest=trusted_preparation.configuration_binding.content_digest,
                )
                if trusted_preparation is not None
                else None
            ),
            "workspace_plan": plan,
            "current_snapshot": latest_snapshot,
            "grant": latest_grant,
            "reservations": latest_reservations,
            "runtime_request_v2": (
                boundary_preparation.request_v2 if boundary_preparation is not None else None
            ),
            "workspace_boundary_ref": (
                boundary_preparation.boundary if boundary_preparation is not None else None
            ),
            "runtime_placement_attestation": (
                boundary_preparation.placement if boundary_preparation is not None else None
            ),
            "runtime_session_binding": (
                boundary_preparation.session
                if boundary_preparation is not None
                else trusted_preparation.session
                if trusted_preparation is not None
                else None
            ),
            "runtime_permission_attestation": (
                boundary_preparation.permission_attestation
                if boundary_preparation is not None
                else None
            ),
            "runtime_placement_continuity": (
                boundary_preparation.continuity if boundary_preparation is not None else None
            ),
        }
    )
    final_admission = evaluate_admission(staged)
    if final_admission.status is not AdmissionStatus.ADMIT:
        if boundary_preparation is not None:
            await _stop_with_boundary_evidence(
                launcher=cast(BoundaryScopedRuntimeLauncher, boundary_launcher),
                boundary=boundary_preparation.boundary,
                launch_subject=boundary_preparation.launch_subject,
                placement=boundary_preparation.placement,
                execution_id=execution_id,
                outcome=(
                    ExecutionTerminalOutcome.BLOCKED_BY_AUTHORITY
                    if final_admission.status is AdmissionStatus.DENY
                    else ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
                ),
                reason="admission:" + final_admission.status.value,
                request_v2=boundary_preparation.request_v2,
                session=boundary_preparation.session,
                permission=boundary_preparation.permission_attestation,
                continuity=boundary_preparation.continuity,
            )
        if trusted_preparation is not None:
            await _reject_prepared_trusted_local(
                runtime,
                trusted_preparation,
                "admission:" + final_admission.status.value,
                (
                    ExecutionTerminalOutcome.BLOCKED_BY_AUTHORITY
                    if final_admission.status is AdmissionStatus.DENY
                    else ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
                ),
            )
        return _blocked_result(inputs, execution_id, "admission:" + final_admission.status.value)
    freshness = check_candidate_freshness(candidate, latest_snapshot)
    if freshness.status is not CandidateFreshnessStatus.CURRENT:
        if boundary_preparation is not None:
            await _stop_with_boundary_evidence(
                launcher=cast(BoundaryScopedRuntimeLauncher, boundary_launcher),
                boundary=boundary_preparation.boundary,
                launch_subject=boundary_preparation.launch_subject,
                placement=boundary_preparation.placement,
                execution_id=execution_id,
                outcome=ExecutionTerminalOutcome.BLOCKED_BY_AUTHORITY,
                reason="candidate:final-freshness-failed",
                request_v2=boundary_preparation.request_v2,
                session=boundary_preparation.session,
                permission=boundary_preparation.permission_attestation,
                continuity=boundary_preparation.continuity,
            )
        if trusted_preparation is not None:
            await _reject_prepared_trusted_local(
                runtime,
                trusted_preparation,
                "candidate:final-freshness-failed",
                ExecutionTerminalOutcome.BLOCKED_BY_AUTHORITY,
            )
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
        execution_profile=execution_profile,
        execution_profile_binding_digest=digest_execution_profile_binding(
            execution_profile,
            candidate.content_digest,
            packet_ref,
            workspace_plan_ref(plan),
            provider_ref,
        ),
        runtime_descriptor=descriptor,
        runtime_configuration_binding_ref=(
            RuntimeEvidenceBindingRef(
                evidence_id=trusted_preparation.configuration_binding.binding_id,
                content_digest=trusted_preparation.configuration_binding.content_digest,
            )
            if trusted_preparation is not None
            else None
        ),
        runtime_request=request,
        runtime_request_v2=(
            boundary_preparation.request_v2 if boundary_preparation is not None else None
        ),
        workspace_boundary_ref=(
            boundary_preparation.boundary if boundary_preparation is not None else None
        ),
        runtime_placement_attestation=(
            boundary_preparation.placement if boundary_preparation is not None else None
        ),
        runtime_permission_attestation=(
            boundary_preparation.permission_attestation
            if boundary_preparation is not None
            else None
        ),
        runtime_permission_attestation_ref=(
            boundary_preparation.permission_attestation.ref
            if boundary_preparation is not None
            else None
        ),
        runtime_session_binding=(
            boundary_preparation.session
            if boundary_preparation is not None
            else None
            if trusted_preparation is None
            else trusted_preparation.session
        ),
        runtime_payload_evidence=materialized_payload.evidence,
        runtime_permission_evidence=runtime_permission_evidence,
        corrective_subject_binding=admission.corrective_subject_binding,
        actual_provider_id=runtime_permission_evidence.actual_provider_id,
        actual_model_id=runtime_permission_evidence.actual_model_id,
        runtime_session=(
            boundary_preparation.session.runtime_session
            if boundary_preparation is not None
            else None
        ),
        reservations=staged.reservations,
        control_references=tuple(sorted(packet.required_workspace_property_keys)),
        resource_references=tuple(sorted(inputs.admission.candidate.work_packet_constraints)),
    )

    if boundary_preparation is None:
        session = (
            trusted_preparation.session
            if trusted_preparation is not None
            else await runtime.create_session(request)
        )
        if session.execution_id != execution_id or session.request_digest != request.request_digest:
            if trusted_preparation is not None:
                await _reject_prepared_trusted_local(
                    runtime,
                    trusted_preparation,
                    "runtime:session-binding-mismatch",
                    ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
                )
            return _blocked_result(inputs, execution_id, "runtime:session-binding-mismatch")
        handle = await runtime.open_execution(request, session)
    else:
        session = boundary_preparation.session
        boundary_runtime = cast(BoundaryManagedAgentRuntime, runtime)
        handle = await boundary_runtime.open_execution_v2(
            boundary_preparation.request_v2,
            session,
            boundary_preparation.permission_attestation,
        )
    if (
        handle.execution_id != execution_id
        or handle.request_digest != request.request_digest
        or boundary_preparation is not None
        and handle.request_digest_v2 != boundary_preparation.request_v2.request_digest_v2
    ):
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
    terminal_boundary_continuity: RuntimePlacementContinuityEvidence | None = None
    runtime_process_teardown: RuntimeProcessTeardownEvidence | None = None
    boundary_terminal_ok = True
    if boundary_preparation is not None:
        assert inputs.boundary_runtime_launcher is not None
        terminal_boundary_continuity = inputs.boundary_runtime_launcher.inspect_runtime_continuity(
            boundary_preparation.boundary,
            boundary_preparation.placement,
            execution_id=execution_id,
            request_digest_v2=boundary_preparation.request_v2.request_digest_v2,
        )
        runtime_process_teardown = await inputs.boundary_runtime_launcher.teardown_runtime(
            boundary_preparation.boundary,
            boundary_preparation.placement,
            execution_id=execution_id,
        )
        boundary_terminal_ok = all(
            (
                terminal_boundary_continuity.workspace_boundary_ref_digest
                == boundary_preparation.boundary.content_digest,
                terminal_boundary_continuity.placement_attestation_ref
                == boundary_preparation.placement.ref,
                terminal_boundary_continuity.execution_id == execution_id,
                terminal_boundary_continuity.request_digest_v2
                == boundary_preparation.request_v2.request_digest_v2,
                terminal_boundary_continuity.process_tree_identity
                == boundary_preparation.placement.process_tree_identity,
                terminal_boundary_continuity.status is RequirementStatus.SATISFIED,
                runtime_process_teardown.workspace_boundary_ref_digest
                == boundary_preparation.boundary.content_digest,
                runtime_process_teardown.placement_attestation_ref
                == boundary_preparation.placement.ref,
                runtime_process_teardown.execution_id == execution_id,
                runtime_process_teardown.process_tree_identity
                == boundary_preparation.placement.process_tree_identity,
                runtime_process_teardown.process_tree_terminated is RequirementStatus.SATISFIED,
                runtime_process_teardown.credential_cleanup is RequirementStatus.SATISFIED,
            )
        )
    changes = workspace_provider.extract_changes(provision.instance_ref)
    capture_method = getattr(workspace_provider, "capture_candidate", None)
    stable_capture: WorkspaceCandidateCapture | None = None
    if callable(capture_method):
        try:
            capture_typed = cast(
                Callable[
                    [WorkspaceInstanceRef, WorkspaceChangeManifest],
                    WorkspaceCandidateCapture,
                ],
                capture_method,
            )
            stable_capture = capture_typed(provision.instance_ref, changes)
        except Exception:
            stable_capture = None
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
            trusted_local=trusted_local,
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
        event_bindings_valid
        and inspection.continuity.state is RuntimeContinuityState.COMPLETE
        and boundary_terminal_ok
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
        or (
            stable_capture is None
            and not (boundary_preparation is not None and boundary_terminal_ok)
        )
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
            "runtime_session_binding": session,
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
        runtime_request_v2=(
            boundary_preparation.request_v2 if boundary_preparation is not None else None
        ),
        workspace_boundary_ref=(
            boundary_preparation.boundary if boundary_preparation is not None else None
        ),
        runtime_placement_attestation=(
            boundary_preparation.placement if boundary_preparation is not None else None
        ),
        runtime_placement_continuity=terminal_boundary_continuity,
        runtime_process_teardown=runtime_process_teardown,
        runtime_permission_attestation=(
            boundary_preparation.permission_attestation
            if boundary_preparation is not None
            else None
        ),
        runtime_permission_attestation_ref=(
            boundary_preparation.permission_attestation.ref
            if boundary_preparation is not None
            else None
        ),
        runtime_payload_evidence=materialized_payload.evidence,
        runtime_permission_evidence=runtime_permission_evidence,
        runtime_configuration_binding=(
            trusted_preparation.configuration_binding if trusted_preparation is not None else None
        ),
        runtime_configuration_binding_ref=(
            RuntimeEvidenceBindingRef(
                evidence_id=trusted_preparation.configuration_binding.binding_id,
                content_digest=trusted_preparation.configuration_binding.content_digest,
            )
            if trusted_preparation is not None
            else None
        ),
        stable_candidate_capture=stable_capture,
        stable_candidate_status=(
            RequirementStatus.SATISFIED
            if stable_capture is not None
            or (boundary_preparation is not None and boundary_terminal_ok)
            else RequirementStatus.INDETERMINATE
        ),
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
