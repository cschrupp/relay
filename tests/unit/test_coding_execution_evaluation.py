"""Deterministic grant, reservation, and runtime exposure decisions."""

from __future__ import annotations

from datetime import UTC, datetime

from test_execution_workspace_evaluation import resolver_fixture
from test_project_state_dogfood import _compile, _resolve, _scenario

from relay_engine.agent_runtime import (
    RuntimeEventEnvelope,
    RuntimeEventType,
    RuntimeInputPayload,
    RuntimeSessionRef,
)
from relay_engine.coding_execution.evaluation import (
    RuntimePermissionEvidence,
    digest_runtime_payload_content,
    evaluate_effective_tool_exposure,
    evaluate_grant_and_reservations,
    evaluate_runtime_payload_evidence,
    evaluate_runtime_tool_events,
)
from relay_engine.coding_execution.models import (
    AdmissionStatus,
    ConsumableReservationBinding,
    HumanGrantBinding,
    RuntimePayloadEvidence,
)
from relay_engine.execution_workspace import resolve_workspace_plan
from relay_engine.project_state import ConsumableRef, ConsumptionRequirement
from relay_engine.role_contracts import RequirementStatus
from relay_engine.work_packets import (
    WorkPacketConformance,
    context_manifest_ref,
    work_packet_ref,
)

_A = "sha256:" + "a" * 64
_ATTEMPT = "exec-018f47c1-7b2c-7abc-8def-123456789008"


def ready_candidate():
    scenario = _scenario(scope="execution", attempt=_ATTEMPT)
    resolution = _resolve(scenario)
    compilation = _compile(scenario, resolution)
    assert compilation.candidate is not None
    return scenario, compilation, compilation.candidate


def test_exact_candidate_grant_and_zero_reservations_are_admissible() -> None:
    scenario, compilation, candidate = ready_candidate()
    grant = HumanGrantBinding(
        grant_record_id="human-grant-1",
        grant_record_digest=_A,
        authority_candidate_digest=candidate.content_digest,
        intended_attempt_id=_ATTEMPT,
        project_id=scenario.snapshot.project_id,
        slice_id="slc_018f47c1-7b2c-7abc-8def-123456789008",
        valid=True,
        applicable=True,
    )
    result = evaluate_grant_and_reservations(
        compilation,
        candidate,
        scenario.snapshot,
        grant,
        (),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )
    assert result.status is AdmissionStatus.ADMIT


def test_wrong_candidate_grant_is_denied_even_when_compilation_is_ready() -> None:
    scenario, compilation, candidate = ready_candidate()
    grant = HumanGrantBinding(
        grant_record_id="human-grant-1",
        grant_record_digest=_A,
        authority_candidate_digest="sha256:" + "b" * 64,
        intended_attempt_id=_ATTEMPT,
        project_id=scenario.snapshot.project_id,
        slice_id="slc_018f47c1-7b2c-7abc-8def-123456789008",
        valid=True,
        applicable=True,
    )
    result = evaluate_grant_and_reservations(
        compilation,
        candidate,
        scenario.snapshot,
        grant,
        (),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )
    assert result.status is AdmissionStatus.DENY
    assert "grant:subject-mismatch" in result.reasons


def test_stale_authority_candidate_is_denied_before_packet_or_workspace_admission() -> None:
    scenario, compilation, candidate = ready_candidate()
    grant = HumanGrantBinding(
        grant_record_id="human-grant-1",
        grant_record_digest=_A,
        authority_candidate_digest=candidate.content_digest,
        intended_attempt_id=_ATTEMPT,
        project_id=scenario.snapshot.project_id,
        slice_id="slc_018f47c1-7b2c-7abc-8def-123456789008",
        valid=True,
        applicable=True,
    )
    changed_snapshot = scenario.snapshot.model_copy(
        update={"registry_digest": "sha256:" + "f" * 64}
    )

    result = evaluate_grant_and_reservations(
        compilation,
        candidate,
        changed_snapshot,
        grant,
        (),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )

    assert result.status is AdmissionStatus.DENY
    assert "candidate:stale" in result.reasons


def test_old_attempt_grant_cannot_authorize_a_new_candidate_attempt() -> None:
    scenario, compilation, candidate = ready_candidate()
    grant = HumanGrantBinding(
        grant_record_id="human-grant-1",
        grant_record_digest=_A,
        authority_candidate_digest=candidate.content_digest,
        intended_attempt_id=_ATTEMPT,
        project_id=scenario.snapshot.project_id,
        slice_id="slc_018f47c1-7b2c-7abc-8def-123456789008",
        valid=True,
        applicable=True,
    )
    next_attempt = "exec-018f47c1-7b2c-7abc-8def-123456789009"
    new_request = candidate.request.model_copy(update={"intended_attempt_id": next_attempt})
    new_resolution = candidate.resolution.model_copy(update={"request": new_request})
    new_candidate = candidate.model_copy(
        update={"request": new_request, "resolution": new_resolution}
    )
    new_compilation = compilation.model_copy(update={"candidate": new_candidate})

    result = evaluate_grant_and_reservations(
        new_compilation,
        new_candidate,
        scenario.snapshot,
        grant,
        (),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )

    assert result.status is AdmissionStatus.DENY
    assert "grant:subject-mismatch" in result.reasons


def test_missing_required_reservation_is_indeterminate_and_wrong_one_denied() -> None:
    scenario, compilation, candidate = ready_candidate()
    consumable_ref = ConsumableRef(
        consumable_key="attempt-namespace",
        scope_key="execution",
    )
    consumption_requirement = ConsumptionRequirement(
        consumable=consumable_ref,
        intended_attempt_id=_ATTEMPT,
    )
    requirement = candidate.resolution.model_copy(
        update={"consumption_requirements": (consumption_requirement,)}
    )
    changed_candidate = candidate.model_copy(update={"resolution": requirement})
    changed_compilation = compilation.model_copy(update={"candidate": changed_candidate})
    grant = HumanGrantBinding(
        grant_record_id="human-grant-1",
        grant_record_digest=_A,
        authority_candidate_digest=changed_candidate.content_digest,
        intended_attempt_id=_ATTEMPT,
        project_id=scenario.snapshot.project_id,
        slice_id="slc_018f47c1-7b2c-7abc-8def-123456789008",
        valid=True,
        applicable=True,
    )
    common = (changed_compilation, changed_candidate, scenario.snapshot, grant)
    missing = evaluate_grant_and_reservations(
        *common,
        (),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )
    assert missing.status is AdmissionStatus.INDETERMINATE

    reservation = ConsumableReservationBinding(
        consumable_key=consumable_ref.consumable_key,
        scope_key=consumable_ref.scope_key,
        grant_record_digest=grant.grant_record_digest,
        authority_candidate_digest=changed_candidate.content_digest,
        intended_attempt_id=_ATTEMPT,
        evidence_id="reservation-1",
        evidence_digest=_A,
        state="RESERVED",
        created_atomically_at_grant=True,
    )
    satisfied = evaluate_grant_and_reservations(
        *common,
        (reservation,),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )
    assert satisfied.status is AdmissionStatus.ADMIT

    duplicate = evaluate_grant_and_reservations(
        *common,
        (reservation, reservation),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )
    assert duplicate.status is AdmissionStatus.DENY
    not_atomic = reservation.model_copy(update={"created_atomically_at_grant": False})
    non_atomic = evaluate_grant_and_reservations(
        *common,
        (not_atomic,),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )
    assert non_atomic.status is AdmissionStatus.DENY
    wrong_state = reservation.model_copy(update={"state": "CONSUMED"})
    consumed = evaluate_grant_and_reservations(
        *common,
        (wrong_state,),
        project_id=scenario.snapshot.project_id,
        slice_id=grant.slice_id,
    )
    assert consumed.status is AdmissionStatus.DENY


def test_default_denied_tool_and_shell_exposure_fail_closed() -> None:
    packet, packet_ref, policy, role, provider = resolver_fixture()
    from relay_engine.execution_workspace.models import WorkPacketConformanceFact

    resolution = resolve_workspace_plan(
        packet,
        packet_ref,
        WorkPacketConformanceFact(
            evaluated_work_packet_ref=packet_ref,
            conformance=WorkPacketConformance(
                status=RequirementStatus.SATISFIED,
                reasons=(),
            ),
        ),
        policy,
        role,
        (),
        provider,
        plan_key="execution-plan",
        revision=1,
    )
    assert resolution.plan is not None
    allowed_evidence = RuntimePermissionEvidence(
        execution_id="exec_018f47c1-7b2c-7abc-8def-123456789008",
        runtime_id="runtime-test",
        attestation_id="attestation-test",
        evidence_digest=_A,
        effective_profile_ref=packet.runtime_permission_profile_ref,
        completeness=RequirementStatus.SATISFIED,
        provenance_status=RequirementStatus.SATISFIED,
        actual_provider_id="provider-local",
        actual_model_id="model-a",
        exposed_tools=(),
        shell_exposed=False,
    )
    assert evaluate_effective_tool_exposure(resolution.plan, allowed_evidence).status is (
        AdmissionStatus.ADMIT
    )
    exposed_denied_tool = allowed_evidence.model_copy(update={"exposed_tools": ("bash",)})
    assert evaluate_effective_tool_exposure(resolution.plan, exposed_denied_tool).status is (
        AdmissionStatus.DENY
    )
    exposed_shell = allowed_evidence.model_copy(update={"shell_exposed": True})
    assert evaluate_effective_tool_exposure(resolution.plan, exposed_shell).status is (
        AdmissionStatus.DENY
    )
    unknown = allowed_evidence.model_copy(
        update={"exposed_tools": None, "unknown_tool_identity": True}
    )
    assert evaluate_effective_tool_exposure(resolution.plan, unknown).status is (
        AdmissionStatus.INDETERMINATE
    )
    wrong_subject = evaluate_effective_tool_exposure(
        resolution.plan,
        allowed_evidence,
        expected_execution_id="exec_018f47c1-7b2c-7abc-8def-123456789009",
        expected_runtime_id="another-runtime",
    )
    assert wrong_subject.status is AdmissionStatus.DENY


def test_tool_request_is_not_proof_of_execution_and_unknown_identity_is_indeterminate() -> None:
    packet, _, policy, role, provider = resolver_fixture()
    plan, _, _, _ = resolve_plan_fixture(packet, policy, role, provider)
    session = RuntimeSessionRef(runtime_id="runtime-test", session_id="session-test")
    requested = RuntimeEventEnvelope(
        execution_id="exec_018f47c1-7b2c-7abc-8def-123456789008",
        runtime_session=session,
        sequence=1,
        event_type=RuntimeEventType.TOOL_REQUESTED,
        observed_at=datetime(2026, 10, 1, tzinfo=UTC),
        payload={"tool_identity": "bash"},
    )
    assert evaluate_runtime_tool_events(plan, (requested,)).status is AdmissionStatus.ADMIT
    unknown_identity = requested.model_copy(update={"payload": {}})
    assert evaluate_runtime_tool_events(plan, (unknown_identity,)).status is (
        AdmissionStatus.INDETERMINATE
    )
    completed = requested.model_copy(update={"event_type": RuntimeEventType.TOOL_COMPLETED})
    assert evaluate_runtime_tool_events(plan, (completed,)).status is (
        AdmissionStatus.INDETERMINATE
    )


def test_runtime_payload_must_bind_exact_packet_context_and_prove_no_protected_exposure() -> None:
    packet, packet_ref, _, _, _ = resolver_fixture()
    from test_work_packet_models import manifest

    context = manifest()
    manifest_ref = context_manifest_ref(context)
    payload = RuntimeInputPayload(
        text="Implement this exact authorized work.",
        payload_digest=_A,
    )
    payload = payload.model_copy(update={"payload_digest": digest_runtime_payload_content(payload)})
    evidence = RuntimePayloadEvidence(
        work_packet_ref=packet_ref,
        context_manifest_ref=manifest_ref,
        payload_digest=payload.payload_digest,
        included_context_keys=packet.required_context_keys,
        status=RequirementStatus.SATISFIED,
        protected_content_exposed=False,
        evaluator_only_content_exposed=False,
        credential_exposure_status="CLEAR",
        evidence_digest="sha256:" + "e" * 64,
    )
    result = evaluate_runtime_payload_evidence(packet, packet_ref, manifest_ref, payload, evidence)
    assert result.status is AdmissionStatus.ADMIT

    mismatched = evidence.model_copy(
        update={
            "work_packet_ref": evidence.work_packet_ref.model_copy(
                update={"revision": evidence.work_packet_ref.revision + 1}
            )
        }
    )
    assert (
        evaluate_runtime_payload_evidence(
            packet, packet_ref, manifest_ref, payload, mismatched
        ).status
        is AdmissionStatus.DENY
    )

    exposed = evidence.model_copy(update={"protected_content_exposed": True})
    assert (
        evaluate_runtime_payload_evidence(packet, packet_ref, manifest_ref, payload, exposed).status
        is AdmissionStatus.DENY
    )

    unknown = evidence.model_copy(
        update={
            "evaluator_only_content_exposed": None,
            "status": RequirementStatus.INDETERMINATE,
        }
    )
    assert (
        evaluate_runtime_payload_evidence(packet, packet_ref, manifest_ref, payload, unknown).status
        is AdmissionStatus.INDETERMINATE
    )


def resolve_plan_fixture(packet, policy, role, provider):
    from relay_engine.execution_workspace.models import WorkPacketConformanceFact

    packet_ref = work_packet_ref(packet)
    result = resolve_workspace_plan(
        packet,
        packet_ref,
        WorkPacketConformanceFact(
            evaluated_work_packet_ref=packet_ref,
            conformance=WorkPacketConformance(status=RequirementStatus.SATISFIED, reasons=()),
        ),
        policy,
        role,
        (),
        provider,
        plan_key="event-plan",
        revision=1,
    )
    assert result.plan is not None
    return result.plan, packet_ref, policy, role
