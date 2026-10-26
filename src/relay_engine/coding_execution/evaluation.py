"""Pure fail-closed checks for exact Slice 3.1 execution admission."""

from __future__ import annotations

import hashlib
import json

from relay_engine.agent_runtime import (
    RuntimeDescriptor,
    RuntimeEventEnvelope,
    RuntimeEventType,
    RuntimeInputPayload,
)
from relay_engine.coding_execution.models import (
    AdmissionEvidence,
    AdmissionStatus,
    ConsumableReservationBinding,
    CorrectiveSubjectBinding,
    EvaluatorReworkBinding,
    EvaluatorReworkEvaluation,
    ExecutionTerminalOutcome,
    HumanGrantBinding,
    PriorExecutionBinding,
    ProposedWorkObservation,
    ReworkDisposition,
    RuntimePayloadEvidence,
    RuntimePermissionEvidence,
    TerminalExecutionResult,
    digest_evaluator_rework_record,
    digest_terminal_candidate,
    digest_terminal_result,
    execution_id_for_attempt,
)
from relay_engine.domain import ActorRef, ContentDigest, ExecutionId
from relay_engine.domain._base import DomainModel
from relay_engine.execution_workspace.models import ShellMode, ToolDecision, WorkspacePlan
from relay_engine.project_state import (
    AuthorityCandidate,
    AuthorityCompilation,
    CandidateFreshnessStatus,
    CompilationStatus,
    ConsumptionRequirement,
    ResolutionSnapshot,
    check_candidate_freshness,
)
from relay_engine.role_contracts import (
    ApplicableRoleContractFacts,
    RequirementStatus,
    RoleAction,
    RoleClass,
    RoleContract,
    RoleEligibility,
    RoleInputRequirement,
    RoleOutputRequirement,
    RoleRequirementFact,
    RoleSeparationFacts,
    RoleSeparationRequirement,
    SuccessorResolution,
    WorkDisposition,
    disposition_for_successor,
    evaluate_required_inputs,
    evaluate_required_outputs,
    evaluate_role_action,
    evaluate_role_contract_applicability,
    evaluate_role_separation,
    role_contract_ref,
)
from relay_engine.work_packets import (
    AuthorityReferenceType,
    ContextManifest,
    ContextManifestRef,
    ContextMaterializationFact,
    WorkPacket,
    WorkPacketConformanceFacts,
    WorkPacketRef,
    evaluate_context_conformance,
    evaluate_work_packet_conformance,
)


class AdmissionInputs(DomainModel):
    """Exact immutable facts required to evaluate pre-runtime admission."""

    compilation: AuthorityCompilation
    candidate: AuthorityCandidate
    current_snapshot: ResolutionSnapshot
    grant: HumanGrantBinding | None
    reservations: tuple[ConsumableReservationBinding, ...] = ()
    work_packet: WorkPacket | None = None
    context_manifest: ContextManifest | None = None
    work_packet_facts: WorkPacketConformanceFacts | None = None
    context_materialization_facts: tuple[ContextMaterializationFact, ...] = ()
    role_contract: RoleContract
    role_applicability_facts: ApplicableRoleContractFacts
    actor: ActorRef
    role_input_facts: tuple[RoleRequirementFact, ...] = ()
    role_output_facts: tuple[RoleRequirementFact, ...] = ()
    role_separation_requirement: RoleSeparationRequirement | None = None
    role_separation_facts: RoleSeparationFacts | None = None
    provider_runtime_status: RequirementStatus = RequirementStatus.INDETERMINATE
    workspace_status: RequirementStatus = RequirementStatus.INDETERMINATE
    protected_verification_status: RequirementStatus = RequirementStatus.INDETERMINATE
    resource_limit_status: RequirementStatus = RequirementStatus.INDETERMINATE
    runtime_descriptor: RuntimeDescriptor
    permission_evidence: RuntimePermissionEvidence
    workspace_plan: WorkspacePlan | None = None
    corrective_subject_binding: CorrectiveSubjectBinding | None = None


def evaluate_grant_and_reservations(
    compilation: AuthorityCompilation,
    candidate: AuthorityCandidate,
    current_snapshot: ResolutionSnapshot,
    grant: HumanGrantBinding | None,
    reservations: tuple[ConsumableReservationBinding, ...],
    *,
    project_id: str,
    slice_id: str,
) -> AdmissionEvidence:
    """Verify exact READY, current candidate, Human grant and grant-time holds."""

    reasons: list[str] = []
    digest = candidate.content_digest
    attempt_id = candidate.request.intended_attempt_id
    if compilation.status is not CompilationStatus.READY:
        reasons.append("authority:not-ready")
    elif compilation.candidate is None or compilation.candidate.content_digest != digest:
        reasons.append("authority:candidate-mismatch")
    if attempt_id is None:
        reasons.append("attempt:missing")
    else:
        freshness = check_candidate_freshness(candidate, current_snapshot)
        if freshness.status is CandidateFreshnessStatus.STALE:
            reasons.append("candidate:stale")
        elif freshness.status is CandidateFreshnessStatus.INDETERMINATE:
            reasons.append("candidate:freshness-indeterminate")
    if grant is None:
        reasons.append("grant:missing")
    elif (
        grant.authority_candidate_digest != digest
        or grant.intended_attempt_id != attempt_id
        or grant.project_id != project_id
        or grant.slice_id != slice_id
    ):
        reasons.append("grant:subject-mismatch")
    elif not grant.valid or not grant.applicable:
        reasons.append("grant:invalid-or-inapplicable")
    if attempt_id is not None:
        bad, missing, reservation_reasons = _reservation_reasons(
            candidate.resolution.consumption_requirements,
            reservations,
            digest,
            attempt_id,
        )
        for reservation in reservations:
            if grant is not None and reservation.grant_record_digest != grant.grant_record_digest:
                bad = True
                reservation_reasons.append("reservation:grant-mismatch")
            if not reservation.created_atomically_at_grant:
                bad = True
                reservation_reasons.append("reservation:not-atomic-at-grant")
        if bad or missing:
            reasons.extend(reservation_reasons)
    if any(
        reason not in {"candidate:freshness-indeterminate", "reservation:missing"}
        for reason in reasons
    ):
        status = AdmissionStatus.DENY
    elif reasons:
        status = AdmissionStatus.INDETERMINATE
    else:
        status = AdmissionStatus.ADMIT
    return AdmissionEvidence(
        status=status,
        reasons=tuple(sorted(set(reasons))),
        checked_candidate_digest=digest,
        checked_attempt_id=attempt_id,
    )


def evaluate_evaluator_rework(
    prior: PriorExecutionBinding,
    evaluator_binding: EvaluatorReworkBinding | None,
    corrective_compilation: AuthorityCompilation,
    corrective_candidate: AuthorityCandidate,
    current_snapshot: ResolutionSnapshot,
    grant: HumanGrantBinding | None,
    reservations: tuple[ConsumableReservationBinding, ...],
    correction_scope: tuple[str, ...],
) -> EvaluatorReworkEvaluation:
    """Classify a REWORK request without issuing authority or creating work."""

    if evaluator_binding is None:
        return _rework_indeterminate("rework:evaluator-record-missing")

    if (
        evaluator_binding.registered_record_digest is None
        or evaluator_binding.projection_digest != digest_evaluator_rework_record(evaluator_binding)
        or evaluator_binding.provenance_status is not RequirementStatus.SATISFIED
        or evaluator_binding.evaluator_identity is None
        or evaluator_binding.source_role != "INDEPENDENT_EVALUATION"
        or not evaluator_binding.finding_ids
        or not evaluator_binding.permitted_correction_scope
    ):
        return _rework_indeterminate("rework:evaluator-provenance-incomplete-or-conflicting")

    if prior.terminal_candidate_digest is None:
        return _rework_indeterminate("rework:prior-terminal-candidate-unavailable")
    if (
        evaluator_binding.reviewed_candidate_digest != prior.terminal_candidate_digest
        or evaluator_binding.reviewed_handoff_digest != prior.handoff_digest
    ):
        return _rework_indeterminate("rework:reviewed-subject-mismatch")

    normalized_scope = tuple(sorted(set(correction_scope), key=lambda item: item.encode("utf-8")))
    if not correction_scope or normalized_scope != correction_scope:
        return _rework_indeterminate("rework:correction-scope-missing-or-noncanonical")

    permitted_scope = set(evaluator_binding.permitted_correction_scope)
    authorized_scope = set(prior.authority_scope)
    prohibited_scope = set(prior.authority_out_of_scope)
    if (
        not set(normalized_scope) <= permitted_scope
        or not set(normalized_scope) <= authorized_scope
        or set(normalized_scope) & prohibited_scope
    ):
        return EvaluatorReworkEvaluation(
            disposition=ReworkDisposition.NEW_AUTHORITY_REQUIRED,
            reasons=("rework:scope-exceeds-evaluator-or-original-authority",),
        )

    attempt_id = corrective_candidate.request.intended_attempt_id
    if (
        corrective_candidate.content_digest == prior.authority_candidate_digest
        or attempt_id is None
        or attempt_id == prior.intended_attempt_id
    ):
        return _rework_indeterminate("rework:corrective-candidate-or-attempt-not-new")
    try:
        corrective_execution_id = execution_id_for_attempt(attempt_id)
    except ValueError:
        return _rework_indeterminate("rework:corrective-attempt-identity-invalid")
    if corrective_execution_id == prior.execution_id:
        return _rework_indeterminate("rework:execution-identity-reused")

    if corrective_candidate.resolution.snapshot.project_id != prior.project_id:
        return _rework_indeterminate("rework:project-mismatch")

    if grant is None:
        return _rework_indeterminate("rework:fresh-grant-missing")
    grant_check = evaluate_grant_and_reservations(
        corrective_compilation,
        corrective_candidate,
        current_snapshot,
        grant,
        reservations,
        project_id=prior.project_id,
        slice_id=prior.slice_id,
    )
    if grant_check.status is not AdmissionStatus.ADMIT:
        reasons = tuple(f"rework:{reason}" for reason in grant_check.reasons)
        return _rework_indeterminate(*reasons or ("rework:fresh-grant-or-reservation-unverified",))

    required_reservation_keys = tuple(
        sorted(
            requirement.consumable.consumable_key
            for requirement in corrective_candidate.resolution.consumption_requirements
        )
    )
    subject = CorrectiveSubjectBinding(
        prior_authority_candidate_digest=prior.authority_candidate_digest,
        prior_terminal_candidate_digest=prior.terminal_candidate_digest,
        prior_terminal_result_digest=prior.terminal_result_digest,
        prior_handoff_digest=prior.handoff_digest,
        prior_work_packet_ref=prior.work_packet_ref,
        evaluation_record_id=evaluator_binding.evaluation_record_id,
        evaluation_record_digest=evaluator_binding.registered_record_digest,
        finding_ids=evaluator_binding.finding_ids,
        correction_scope=normalized_scope,
        corrective_candidate_digest=corrective_candidate.content_digest,
        intended_attempt_id=attempt_id,
        execution_id=corrective_execution_id,
        grant=grant,
        reservations=reservations,
        required_reservation_keys=required_reservation_keys,
    )
    return EvaluatorReworkEvaluation(
        disposition=ReworkDisposition.IN_SCOPE_REWORK,
        reasons=(),
        corrective_subject=subject,
    )


def prior_execution_binding(
    result: TerminalExecutionResult,
) -> PriorExecutionBinding:
    """Project exact prior terminal identity and packet scope for REWORK evaluation."""

    return PriorExecutionBinding(
        authority_candidate_digest=result.subject.candidate_digest,
        terminal_candidate_digest=digest_terminal_candidate(result),
        terminal_result_digest=digest_terminal_result(result),
        handoff_digest=result.evaluator_handoff_digest,
        intended_attempt_id=result.subject.intended_attempt_id,
        execution_id=result.subject.execution_id,
        project_id=result.subject.project_id,
        slice_id=result.subject.slice_id,
        work_packet_ref=result.subject.work_packet_ref,
        authority_scope=result.subject.work_packet.normalized_intent.scope.in_scope,
        authority_out_of_scope=result.subject.work_packet.normalized_intent.scope.out_of_scope,
    )


def _rework_indeterminate(*reasons: str) -> EvaluatorReworkEvaluation:
    return EvaluatorReworkEvaluation(
        disposition=ReworkDisposition.INDETERMINATE,
        reasons=tuple(sorted(set(reasons))),
    )


def evaluate_packet_before_workspace(
    grant: HumanGrantBinding,
    candidate: AuthorityCandidate,
    packet: WorkPacket,
    manifest: ContextManifest,
    packet_facts: WorkPacketConformanceFacts,
    materialization_facts: tuple[ContextMaterializationFact, ...],
) -> AdmissionEvidence:
    """Verify grant linkage and exact packet/context conformance pre-resolution."""

    reasons: list[str] = []
    refs = tuple(
        ref
        for ref in packet.authority_refs
        if ref.authority_type is AuthorityReferenceType.SLICE_AUTHORIZATION_GRANT
    )
    if not any(
        ref.authority_key == grant.grant_record_id
        and ref.record_digest == grant.grant_record_digest
        and ref.subject_digest == candidate.content_digest
        for ref in refs
    ):
        reasons.append("work-packet:grant-link-mismatch")
    if packet.project_id != candidate.resolution.snapshot.project_id:
        reasons.append("work-packet:project-mismatch")
    if (
        grant.project_id != packet.project_id
        or grant.slice_id != packet.slice_definition_ref.slice_id
    ):
        reasons.append("work-packet:grant-scope-mismatch")
    packet_result = evaluate_work_packet_conformance(packet, manifest, packet_facts)
    context_result = evaluate_context_conformance(packet, manifest, materialization_facts)
    for label, status in (
        ("work-packet", packet_result.status),
        ("context", context_result.status),
    ):
        if status is RequirementStatus.UNSATISFIED:
            reasons.append(label + ":unsatisfied")
        elif status is RequirementStatus.INDETERMINATE:
            reasons.append(label + ":indeterminate")
    status = (
        AdmissionStatus.DENY
        if any(reason.endswith("unsatisfied") or reason.endswith("mismatch") for reason in reasons)
        else AdmissionStatus.INDETERMINATE
        if reasons
        else AdmissionStatus.ADMIT
    )
    return AdmissionEvidence(
        status=status,
        reasons=tuple(sorted(set(reasons))),
        checked_candidate_digest=candidate.content_digest,
        checked_attempt_id=candidate.request.intended_attempt_id,
    )


def evaluate_runtime_payload_evidence(
    packet: WorkPacket,
    packet_ref: WorkPacketRef,
    manifest_ref: ContextManifestRef,
    payload: RuntimeInputPayload,
    evidence: RuntimePayloadEvidence,
) -> AdmissionEvidence:
    """Require the prompt to bind exactly to conformed, allowed packet context."""

    reasons: list[str] = []
    payload_content_digest = digest_runtime_payload_content(payload)
    if payload.payload_digest != payload_content_digest:
        reasons.append("payload:content-digest-mismatch")
    if evidence.work_packet_ref != packet_ref:
        reasons.append("payload:work-packet-ref-mismatch")
    if evidence.context_manifest_ref != manifest_ref:
        reasons.append("payload:context-manifest-ref-mismatch")
    if evidence.payload_digest != payload.payload_digest:
        reasons.append("payload:digest-mismatch")
    if evidence.included_context_keys != packet.required_context_keys:
        reasons.append("payload:context-selection-mismatch")
    credential_status = evidence.credential_exposure_status
    if credential_status == "EXPOSED":
        reasons.append("payload:credential-exposed")
    elif packet.credential_refs and credential_status == "NOT_APPLICABLE":
        reasons.append("payload:credential-applicability-mismatch")
    elif credential_status not in (
        {"CLEAR"} if packet.credential_refs else {"CLEAR", "NOT_APPLICABLE"}
    ):
        reasons.append("payload:credential-exposure-unknown")
    if evidence.protected_content_exposed is True:
        reasons.append("payload:protected-content-exposed")
    elif evidence.protected_content_exposed is None:
        reasons.append("payload:protected-content-unknown")
    if evidence.evaluator_only_content_exposed is True:
        reasons.append("payload:evaluator-content-exposed")
    elif evidence.evaluator_only_content_exposed is None:
        reasons.append("payload:evaluator-content-unknown")
    if evidence.status is RequirementStatus.UNSATISFIED:
        reasons.append("payload:unsatisfied")
    elif evidence.status is RequirementStatus.INDETERMINATE:
        reasons.append("payload:indeterminate")

    hard_failure = any(
        reason.endswith("mismatch") or reason.endswith("exposed") or reason == "payload:unsatisfied"
        for reason in reasons
    )
    status = (
        AdmissionStatus.DENY
        if hard_failure
        else AdmissionStatus.INDETERMINATE
        if reasons
        else AdmissionStatus.ADMIT
    )
    return AdmissionEvidence(
        status=status,
        reasons=tuple(sorted(set(reasons))),
    )


def digest_runtime_payload_content(payload: RuntimeInputPayload) -> ContentDigest:
    """Hash the exact prompt text and attachment identities canonically."""

    content = {
        "text": payload.text,
        "attachment_refs": [item.model_dump(mode="json") for item in payload.attachment_refs],
    }
    encoded = json.dumps(
        content,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def apply_scope_and_successor_disposition(
    outcome: ExecutionTerminalOutcome,
    hard_stop_keys: tuple[str, ...],
    proposed_work: tuple[ProposedWorkObservation, ...],
    successor_resolution: SuccessorResolution | None,
) -> tuple[ExecutionTerminalOutcome, tuple[str, ...]]:
    """Apply existing hard-stop and successor semantics without creating work."""

    reasons: list[str] = []
    allowed_stops = set(hard_stop_keys)
    if any(item.applicable_hard_stop_key not in allowed_stops for item in proposed_work):
        return ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT, ("proposed-work:hard-stop-unbound",)
    if proposed_work and outcome is ExecutionTerminalOutcome.DONE:
        outcome = ExecutionTerminalOutcome.BLOCKED_BY_AUTHORITY
        reasons.append("proposed-work:scope-stop")
    if successor_resolution is not None:
        disposition = disposition_for_successor(successor_resolution)
        if (
            disposition is WorkDisposition.BACKLOG_EXHAUSTED
            and outcome is ExecutionTerminalOutcome.DONE
        ):
            outcome = ExecutionTerminalOutcome.BACKLOG_EXHAUSTED
        elif disposition is WorkDisposition.ESCALATION_REQUIRED:
            outcome = ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
            reasons.append("successor:resolution-escalation-required")
    return outcome, tuple(sorted(reasons))


def _collect_requirement_status(
    required: tuple[RoleInputRequirement | RoleOutputRequirement, ...],
    facts: tuple[RoleRequirementFact, ...],
    *,
    inputs: bool,
) -> tuple[RequirementStatus, tuple[str, ...]]:
    if inputs:
        result = evaluate_required_inputs(required, facts)  # type: ignore[arg-type]
    else:
        result = evaluate_required_outputs(required, facts)  # type: ignore[arg-type]
    reason = "role-inputs" if inputs else "role-outputs"
    if result.status is RequirementStatus.SATISFIED:
        return result.status, ()
    if result.status is RequirementStatus.UNSATISFIED:
        return result.status, (reason + ":unsatisfied",)
    return result.status, (reason + ":indeterminate",)


def _reservation_reasons(
    requirements: tuple[ConsumptionRequirement, ...],
    reservations: tuple[ConsumableReservationBinding, ...],
    candidate_digest: str,
    attempt_id: str,
) -> tuple[bool, bool, list[str]]:
    """Return (known failure, unknown, reasons) for exact reservation matching."""

    reasons: list[str] = []
    expected = {
        (item.consumable.consumable_key, item.consumable.scope_key): item for item in requirements
    }
    actual: dict[tuple[str, str], ConsumableReservationBinding] = {}
    known_failure = False
    unknown = False
    if len(expected) != len(requirements):
        known_failure = True
        reasons.append("reservation:duplicate-requirement")
    for reservation in reservations:
        key = (reservation.consumable_key, reservation.scope_key)
        if key in actual:
            known_failure = True
            reasons.append("reservation:duplicate")
        actual[key] = reservation
        if (reservation.authority_candidate_digest, reservation.intended_attempt_id) != (
            candidate_digest,
            attempt_id,
        ):
            known_failure = True
            reasons.append("reservation:subject-mismatch")
        if reservation.state != "RESERVED":
            known_failure = True
            reasons.append("reservation:not-reserved")
    evidence_ids = tuple(item.evidence_id for item in reservations)
    if len(evidence_ids) != len(set(evidence_ids)):
        known_failure = True
        reasons.append("reservation:evidence-identity-reused")
    if set(actual) - set(expected):
        known_failure = True
        reasons.append("reservation:unexpected")
    for key in expected:
        if key not in actual:
            unknown = True
            reasons.append("reservation:missing")
    if set(actual) == set(expected):
        for _key, requirement in expected.items():
            if requirement.intended_attempt_id != attempt_id:
                known_failure = True
                reasons.append("reservation:requirement-attempt-mismatch")
    return known_failure, unknown, reasons


def evaluate_admission(inputs: AdmissionInputs) -> AdmissionEvidence:
    """Evaluate exact authority and conformance without creating any authority."""

    deny: list[str] = []
    indeterminate: list[str] = []
    candidate = inputs.candidate
    digest = candidate.content_digest
    attempt_id = candidate.request.intended_attempt_id
    if inputs.compilation.status is not CompilationStatus.READY:
        deny.append("authority:not-ready")
    elif (
        inputs.compilation.candidate is None
        or inputs.compilation.candidate.content_digest != digest
    ):
        deny.append("authority:candidate-mismatch")
    if attempt_id is None:
        deny.append("attempt:missing")
    else:
        try:
            execution_id_for_attempt(attempt_id)
        except ValueError:
            deny.append("attempt:malformed")
        freshness = check_candidate_freshness(candidate, inputs.current_snapshot)
        if freshness.status is CandidateFreshnessStatus.STALE:
            deny.append("candidate:stale")
        elif freshness.status is CandidateFreshnessStatus.INDETERMINATE:
            indeterminate.append("candidate:freshness-indeterminate")

    grant = inputs.grant
    if grant is None:
        deny.append("grant:missing")
    elif grant.authority_candidate_digest != digest or grant.intended_attempt_id != attempt_id:
        deny.append("grant:subject-mismatch")
    elif not grant.valid or not grant.applicable:
        deny.append("grant:invalid-or-inapplicable")

    requirements = candidate.resolution.consumption_requirements
    if attempt_id is not None:
        bad, missing, reasons = _reservation_reasons(
            requirements, inputs.reservations, digest, attempt_id
        )
        if bad:
            deny.extend(reasons)
        elif missing:
            indeterminate.extend(reasons)

    packet = inputs.work_packet
    if packet is None or inputs.context_manifest is None or inputs.work_packet_facts is None:
        deny.append("work-packet:materialization-missing")
        return AdmissionEvidence(
            status=AdmissionStatus.DENY if deny else AdmissionStatus.INDETERMINATE,
            reasons=tuple(sorted(set(deny + indeterminate))),
            checked_candidate_digest=digest,
            checked_attempt_id=attempt_id,
        )
    if grant is not None and (
        grant.project_id != packet.project_id
        or grant.slice_id != packet.slice_definition_ref.slice_id
    ):
        deny.append("grant:subject-mismatch")
    if inputs.corrective_subject_binding is not None:
        corrective_check = evaluate_corrective_subject_binding(
            inputs.corrective_subject_binding,
            candidate,
            packet,
            grant,
            inputs.reservations,
        )
        if corrective_check.status is AdmissionStatus.DENY:
            deny.extend(corrective_check.reasons)
        elif corrective_check.status is AdmissionStatus.INDETERMINATE:
            indeterminate.extend(corrective_check.reasons)
    if grant is not None:
        exact_authority = evaluate_grant_and_reservations(
            inputs.compilation,
            candidate,
            inputs.current_snapshot,
            grant,
            inputs.reservations,
            project_id=packet.project_id,
            slice_id=packet.slice_definition_ref.slice_id,
        )
        if exact_authority.status is AdmissionStatus.DENY:
            deny.extend(exact_authority.reasons)
        elif exact_authority.status is AdmissionStatus.INDETERMINATE:
            indeterminate.extend(exact_authority.reasons)
    authority_refs = tuple(
        reference
        for reference in packet.authority_refs
        if reference.authority_type is AuthorityReferenceType.SLICE_AUTHORIZATION_GRANT
    )
    if grant is None or not any(
        reference.record_digest == grant.grant_record_digest and reference.subject_digest == digest
        for reference in authority_refs
    ):
        deny.append("work-packet:grant-link-mismatch")

    packet_admission = (
        evaluate_packet_before_workspace(
            grant,
            candidate,
            packet,
            inputs.context_manifest,
            inputs.work_packet_facts,
            inputs.context_materialization_facts,
        )
        if grant is not None
        else AdmissionEvidence(
            status=AdmissionStatus.DENY,
            reasons=("grant:missing",),
        )
    )
    if packet_admission.status is AdmissionStatus.DENY:
        deny.extend(packet_admission.reasons)
    elif packet_admission.status is AdmissionStatus.INDETERMINATE:
        indeterminate.extend(packet_admission.reasons)

    role_ref = role_contract_ref(inputs.role_contract)
    if role_ref != packet.role_contract_ref:
        deny.append("role:reference-mismatch")
    if inputs.role_contract.role_class is not RoleClass.IMPLEMENTER:
        deny.append("role:not-implementer")
    applicability = evaluate_role_contract_applicability(inputs.role_applicability_facts)
    implement_action = evaluate_role_action(
        inputs.role_contract,
        inputs.actor,
        RoleAction.IMPLEMENTATION_MUTATE,
        applicability=applicability,
    )
    if implement_action is RoleEligibility.PROHIBITED_BY_ROLE:
        deny.append("role:implementation-prohibited")
    elif implement_action is RoleEligibility.INDETERMINATE:
        indeterminate.append("role:implementation-indeterminate")
    for action in (RoleAction.ACCEPT_RESULT, RoleAction.EVALUATE_RESULT, RoleAction.PROMOTE_RESULT):
        eligibility = evaluate_role_action(
            inputs.role_contract,
            inputs.actor,
            action,
            applicability=applicability,
        )
        if eligibility is RoleEligibility.PERMITTED_BY_ROLE:
            deny.append("role:self-authority:" + action.value)
    for required, facts, is_input in (
        (inputs.role_contract.required_inputs, inputs.role_input_facts, True),
        (inputs.role_contract.required_outputs, inputs.role_output_facts, False),
    ):
        status, reasons = _collect_requirement_status(required, facts, inputs=is_input)
        if status is RequirementStatus.UNSATISFIED:
            deny.extend(reasons)
        elif status is RequirementStatus.INDETERMINATE:
            indeterminate.extend(reasons)
    if inputs.role_separation_requirement is not None:
        if inputs.role_separation_facts is None:
            indeterminate.append("role-separation:missing")
        else:
            separation = evaluate_role_separation(
                inputs.role_separation_requirement, inputs.role_separation_facts
            )
            if separation.status is RequirementStatus.UNSATISFIED:
                deny.append("role-separation:unsatisfied")
            elif separation.status is RequirementStatus.INDETERMINATE:
                indeterminate.append("role-separation:indeterminate")

    for label, status in (
        ("provider-runtime", inputs.provider_runtime_status),
        ("workspace", inputs.workspace_status),
        ("protected-verification", inputs.protected_verification_status),
        ("resource-limits", inputs.resource_limit_status),
    ):
        if status is RequirementStatus.UNSATISFIED:
            deny.append(label + ":unsatisfied")
        elif status is RequirementStatus.INDETERMINATE:
            indeterminate.append(label + ":indeterminate")

    profile_ref = packet.runtime_permission_profile_ref
    permission = inputs.permission_evidence
    if profile_ref is None or permission.effective_profile_ref != profile_ref:
        indeterminate.append("runtime-permissions:profile-unbound")
    if permission.completeness is RequirementStatus.UNSATISFIED:
        deny.append("runtime-permissions:unsatisfied")
    elif permission.completeness is RequirementStatus.INDETERMINATE:
        indeterminate.append("runtime-permissions:incomplete")
    # The exact ToolPolicy/ShellPolicy lives on the resolved WorkspacePlan.
    # Its comparison with actual exposure is done by
    # evaluate_effective_tool_exposure after the plan exists.
    selection = packet.runtime_selection_requirement
    if selection is None:
        indeterminate.append("runtime:selection-missing")
    elif inputs.runtime_descriptor.runtime_id != selection.runtime_id:
        deny.append("runtime:identity-mismatch")
    if not set(packet.required_runtime_capabilities).issubset(
        set(inputs.runtime_descriptor.capabilities)
    ):
        deny.append("runtime:capability-mismatch")
    if inputs.workspace_plan is None:
        indeterminate.append("workspace:plan-unbound")
    else:
        try:
            expected_execution_id = (
                execution_id_for_attempt(attempt_id) if attempt_id is not None else None
            )
        except ValueError:
            expected_execution_id = None
        exposure_result = evaluate_effective_tool_exposure(
            inputs.workspace_plan,
            permission,
            expected_execution_id=expected_execution_id,
            expected_runtime_id=inputs.runtime_descriptor.runtime_id,
        )
        if exposure_result.status is AdmissionStatus.DENY:
            deny.extend(exposure_result.reasons)
        elif exposure_result.status is AdmissionStatus.INDETERMINATE:
            indeterminate.extend(exposure_result.reasons)
    if selection is not None and (
        permission.actual_provider_id != selection.requested_provider_id
        or permission.actual_model_id != selection.requested_model_id
    ):
        indeterminate.append("runtime-permissions:provider-model-identity-unbound")

    status = (
        AdmissionStatus.DENY
        if deny
        else AdmissionStatus.INDETERMINATE
        if indeterminate
        else AdmissionStatus.ADMIT
    )
    return AdmissionEvidence(
        status=status,
        reasons=tuple(sorted(set(deny + indeterminate))),
        checked_candidate_digest=digest,
        checked_attempt_id=attempt_id,
    )


def evaluate_corrective_subject_binding(
    binding: CorrectiveSubjectBinding,
    candidate: AuthorityCandidate,
    packet: WorkPacket,
    grant: HumanGrantBinding | None,
    reservations: tuple[ConsumableReservationBinding, ...],
) -> AdmissionEvidence:
    """Require an in-scope evaluator REWORK binding to survive packet admission."""

    attempt_id = candidate.request.intended_attempt_id
    try:
        execution_id = execution_id_for_attempt(attempt_id) if attempt_id is not None else None
    except ValueError:
        execution_id = None
    reasons: list[str] = []
    if (
        binding.corrective_candidate_digest != candidate.content_digest
        or attempt_id is None
        or binding.intended_attempt_id != attempt_id
        or binding.execution_id != execution_id
    ):
        reasons.append("rework:corrective-subject-mismatch")
    if grant is None or binding.grant != grant:
        reasons.append("rework:fresh-grant-mismatch")
    if binding.reservations != reservations:
        reasons.append("rework:fresh-reservations-mismatch")
    packet_scope = set(packet.normalized_intent.scope.in_scope)
    if not packet_scope.issubset(set(binding.correction_scope)):
        reasons.append("rework:packet-exceeds-evaluator-permitted-scope")
    return AdmissionEvidence(
        status=AdmissionStatus.DENY if reasons else AdmissionStatus.ADMIT,
        reasons=tuple(sorted(set(reasons))),
        checked_candidate_digest=candidate.content_digest,
        checked_attempt_id=attempt_id,
    )


def evaluate_effective_tool_exposure(
    plan: object,
    evidence: RuntimePermissionEvidence,
    *,
    expected_execution_id: ExecutionId | None = None,
    expected_runtime_id: str | None = None,
) -> AdmissionEvidence:
    """Compare effective named-tool/shell exposure with the exact workspace plan."""

    from relay_engine.execution_workspace.models import WorkspacePlan

    if not isinstance(plan, WorkspacePlan):
        return AdmissionEvidence(status=AdmissionStatus.INDETERMINATE, reasons=("plan:unknown",))
    reasons: list[str] = []
    if expected_execution_id is not None and evidence.execution_id != expected_execution_id:
        reasons.append("runtime-permissions:execution-mismatch")
    if expected_runtime_id is not None and evidence.runtime_id != expected_runtime_id:
        reasons.append("runtime-permissions:runtime-mismatch")
    status = AdmissionStatus.DENY if reasons else AdmissionStatus.ADMIT
    if evidence.unknown_tool_identity or evidence.exposed_tools is None:
        reasons.append("runtime-permissions:tool-identity-unknown")
        status = AdmissionStatus.INDETERMINATE
    else:
        by_key = {rule.tool_ref.tool_key: rule.decision for rule in plan.tool_policy.rules}
        denied_exposed = [
            key
            for key in evidence.exposed_tools
            if by_key.get(key, plan.tool_policy.default_decision) is ToolDecision.DENY
        ]
        if denied_exposed:
            reasons.append("runtime-permissions:denied-tool-exposed")
            status = AdmissionStatus.DENY
        elif status is not AdmissionStatus.DENY:
            status = AdmissionStatus.ADMIT
    if evidence.shell_exposed is None and status is not AdmissionStatus.DENY:
        status = AdmissionStatus.INDETERMINATE
        reasons.append("runtime-permissions:shell-exposure-unknown")
    if plan.shell_policy.mode is ShellMode.DENY:
        if evidence.shell_exposed is True:
            status = AdmissionStatus.DENY
            reasons.append("runtime-permissions:denied-shell-exposed")
        elif evidence.shell_exposed is None and status is not AdmissionStatus.DENY:
            status = AdmissionStatus.INDETERMINATE
            reasons.append("runtime-permissions:shell-exposure-unknown")
    if evidence.completeness is not RequirementStatus.SATISFIED:
        if evidence.completeness is RequirementStatus.UNSATISFIED:
            status = AdmissionStatus.DENY
            reasons.append("runtime-permissions:unsatisfied")
        elif status is AdmissionStatus.ADMIT:
            status = AdmissionStatus.INDETERMINATE
            reasons.append("runtime-permissions:incomplete")
    if evidence.provenance_status is RequirementStatus.UNSATISFIED:
        status = AdmissionStatus.DENY
        reasons.append("runtime-permissions:provenance-invalid")
    elif (
        evidence.provenance_status is RequirementStatus.INDETERMINATE
        and status is AdmissionStatus.ADMIT
    ):
        status = AdmissionStatus.INDETERMINATE
        reasons.append("runtime-permissions:provenance-incomplete")
    if any(
        reason
        in {
            "runtime-permissions:execution-mismatch",
            "runtime-permissions:runtime-mismatch",
            "runtime-permissions:denied-tool-exposed",
            "runtime-permissions:denied-shell-exposed",
            "runtime-permissions:unsatisfied",
        }
        for reason in reasons
    ):
        status = AdmissionStatus.DENY
    return AdmissionEvidence(status=status, reasons=tuple(sorted(set(reasons))))


def evaluate_runtime_tool_events(
    plan: WorkspacePlan,
    events: tuple[RuntimeEventEnvelope, ...],
) -> AdmissionEvidence:
    """Interpret tool events without inferring exposure or successful execution."""

    reasons: list[str] = []
    for event in events:
        if event.event_type not in {
            RuntimeEventType.TOOL_REQUESTED,
            RuntimeEventType.TOOL_COMPLETED,
        }:
            continue
        tool_identity = event.payload.get("tool_identity")
        if not isinstance(tool_identity, str) or not tool_identity:
            reasons.append("runtime-event:tool-identity-unknown")
            continue
        decision = next(
            (
                rule.decision
                for rule in plan.tool_policy.rules
                if rule.tool_ref.tool_key == tool_identity
            ),
            plan.tool_policy.default_decision,
        )
        if event.event_type is RuntimeEventType.TOOL_COMPLETED and decision is ToolDecision.DENY:
            # The normalized event contract does not establish universal proof
            # of invocation success, so this claim remains indeterminate.
            reasons.append("runtime-event:denied-tool-completion-semantics-unknown")
    return AdmissionEvidence(
        status=AdmissionStatus.INDETERMINATE if reasons else AdmissionStatus.ADMIT,
        reasons=tuple(sorted(set(reasons))),
    )
