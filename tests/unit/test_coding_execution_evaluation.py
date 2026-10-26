"""Deterministic grant, reservation, and runtime exposure decisions."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
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
    evaluate_corrective_subject_binding,
    evaluate_effective_tool_exposure,
    evaluate_evaluator_rework,
    evaluate_grant_and_reservations,
    evaluate_runtime_payload_evidence,
    evaluate_runtime_tool_events,
)
from relay_engine.coding_execution.models import (
    AdmissionStatus,
    ConsumableReservationBinding,
    EvaluatorReworkBinding,
    HumanGrantBinding,
    PriorExecutionBinding,
    ReworkDisposition,
    RuntimePayloadEvidence,
    digest_evaluator_rework_record,
    execution_id_for_attempt,
)
from relay_engine.execution_workspace import resolve_workspace_plan
from relay_engine.project_state import ConsumableRef, ConsumableState, ConsumptionRequirement
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


def rework_fixture(*, with_consumable: bool = False):
    from test_execution_workspace_evaluation import resolver_fixture
    from test_project_state_dogfood import _consume

    packet, packet_ref, _, _, _ = resolver_fixture()
    attempt_id = "exec-018f47c1-7b2c-7abc-8def-123456789008"
    scenario = _scenario(scope="execution", attempt=attempt_id)
    snapshot = scenario.snapshot.model_copy(update={"project_id": packet.project_id})
    scenario = scenario.__class__(
        request=scenario.request,
        snapshot=snapshot,
        coverage=scenario.coverage,
        records=scenario.records,
    )
    consumable = None
    edge = None
    if with_consumable:
        scenario, consumable, edge = _consume(
            scenario,
            "correction-budget",
            ConsumableState.AVAILABLE,
            True,
        )
    facts = {}
    if consumable is not None and edge is not None:
        facts = {
            "consumable_facts": (consumable,),
            "requirement_edges": (edge,),
        }
    compilation = _compile(scenario, _resolve(scenario, **facts))
    candidate = compilation.candidate
    assert candidate is not None
    prior_attempt = "exec-018f47c1-7b2c-7abc-8def-123456789007"
    prior = PriorExecutionBinding(
        authority_candidate_digest="sha256:" + "b" * 64,
        terminal_candidate_digest="sha256:" + "d" * 64,
        terminal_result_digest="sha256:" + "e" * 64,
        handoff_digest="sha256:" + "c" * 64,
        intended_attempt_id=prior_attempt,
        execution_id=execution_id_for_attempt(prior_attempt),
        project_id=packet.project_id,
        slice_id=packet.slice_definition_ref.slice_id,
        work_packet_ref=packet_ref,
        authority_scope=packet.normalized_intent.scope.in_scope,
        authority_out_of_scope=packet.normalized_intent.scope.out_of_scope,
    )
    evaluator = EvaluatorReworkBinding(
        evaluation_record_id="independent-eval-001",
        registered_record_digest=_A,
        projection_digest=_A,
        evaluator_identity="independent-reviewer",
        source_role="INDEPENDENT_EVALUATION",
        provenance_status=RequirementStatus.SATISFIED,
        outcome="REWORK",
        reviewed_candidate_digest=prior.terminal_candidate_digest,
        reviewed_handoff_digest=prior.handoff_digest,
        finding_ids=("finding-a17-1",),
        permitted_correction_scope=packet.normalized_intent.scope.in_scope,
    )
    evaluator = evaluator.model_copy(
        update={"projection_digest": digest_evaluator_rework_record(evaluator)}
    )
    grant = HumanGrantBinding(
        grant_record_id="corrective-human-grant",
        grant_record_digest=_A,
        authority_candidate_digest=candidate.content_digest,
        intended_attempt_id=attempt_id,
        project_id=packet.project_id,
        slice_id=packet.slice_definition_ref.slice_id,
        valid=True,
        applicable=True,
    )
    reservations = ()
    if candidate.resolution.consumption_requirements:
        requirement = candidate.resolution.consumption_requirements[0]
        reservations = (
            ConsumableReservationBinding(
                consumable_key=requirement.consumable.consumable_key,
                scope_key=requirement.consumable.scope_key,
                grant_record_digest=grant.grant_record_digest,
                authority_candidate_digest=candidate.content_digest,
                intended_attempt_id=attempt_id,
                evidence_id="correction-reservation-001",
                evidence_digest="sha256:" + "b" * 64,
                state="RESERVED",
                created_atomically_at_grant=True,
            ),
        )
    return scenario, compilation, candidate, prior, evaluator, grant, reservations


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


def test_in_scope_evaluator_rework_links_both_candidates_and_requires_fresh_grant() -> None:
    from test_execution_workspace_evaluation import resolver_fixture

    (
        scenario,
        compilation,
        candidate,
        prior,
        evaluator,
        grant,
        reservations,
    ) = rework_fixture()

    result = evaluate_evaluator_rework(
        prior,
        evaluator,
        compilation,
        candidate,
        scenario.snapshot,
        grant,
        reservations,
        ("add models",),
    )

    assert result.disposition is ReworkDisposition.IN_SCOPE_REWORK
    assert result.corrective_subject is not None
    assert (
        result.corrective_subject.prior_terminal_candidate_digest == prior.terminal_candidate_digest
    )
    assert (
        result.corrective_subject.prior_authority_candidate_digest
        == prior.authority_candidate_digest
    )
    assert result.corrective_subject.prior_handoff_digest == prior.handoff_digest
    assert result.corrective_subject.evaluation_record_id == evaluator.evaluation_record_id
    assert result.corrective_subject.finding_ids == evaluator.finding_ids
    assert result.corrective_subject.intended_attempt_id != prior.intended_attempt_id
    assert result.corrective_subject.execution_id != prior.execution_id
    assert result.corrective_subject.grant == grant
    assert result.corrective_subject.reservations == reservations
    packet = resolver_fixture()[0]
    packet_check = evaluate_corrective_subject_binding(
        result.corrective_subject,
        candidate,
        packet,
        grant,
        reservations,
    )
    assert packet_check.status is AdmissionStatus.ADMIT

    expanded_intent = packet.normalized_intent.model_copy(
        update={
            "scope": packet.normalized_intent.scope.model_copy(
                update={"in_scope": ("execute agents",)}
            )
        }
    )
    expanded_packet = packet.model_copy(update={"normalized_intent": expanded_intent})
    expanded_check = evaluate_corrective_subject_binding(
        result.corrective_subject,
        candidate,
        expanded_packet,
        grant,
        reservations,
    )
    assert expanded_check.status is AdmissionStatus.DENY
    assert "rework:packet-exceeds-evaluator-permitted-scope" in expanded_check.reasons


def test_evaluator_rework_scope_excess_requires_new_authority() -> None:
    scenario, compilation, candidate, prior, evaluator, grant, reservations = rework_fixture()

    result = evaluate_evaluator_rework(
        prior,
        evaluator,
        compilation,
        candidate,
        scenario.snapshot,
        grant,
        reservations,
        ("execute agents",),
    )

    assert result.disposition is ReworkDisposition.NEW_AUTHORITY_REQUIRED
    assert result.corrective_subject is None


@pytest.mark.parametrize(
    ("binding_change", "expected_reason"),
    (
        ({"reviewed_candidate_digest": "sha256:" + "f" * 64}, "reviewed-subject-mismatch"),
        ({"reviewed_handoff_digest": "sha256:" + "f" * 64}, "reviewed-subject-mismatch"),
        ({"provenance_status": RequirementStatus.INDETERMINATE}, "provenance"),
        ({"registered_record_digest": None}, "provenance"),
    ),
)
def test_evaluator_rework_missing_or_conflicting_provenance_is_indeterminate(
    binding_change: dict[str, object], expected_reason: str
) -> None:
    scenario, compilation, candidate, prior, evaluator, grant, reservations = rework_fixture()
    evaluator = evaluator.model_copy(update=binding_change)
    if {"reviewed_candidate_digest", "reviewed_handoff_digest"} & set(binding_change):
        digest = digest_evaluator_rework_record(evaluator)
        evaluator = evaluator.model_copy(update={"projection_digest": digest})

    result = evaluate_evaluator_rework(
        prior,
        evaluator,
        compilation,
        candidate,
        scenario.snapshot,
        grant,
        reservations,
        ("add models",),
    )

    assert result.disposition is ReworkDisposition.INDETERMINATE
    assert result.corrective_subject is None
    assert any(expected_reason in reason for reason in result.reasons)


def test_corrective_attempt_requires_new_identity_and_exact_reservations() -> None:
    (
        scenario,
        compilation,
        candidate,
        prior,
        evaluator,
        grant,
        reservations,
    ) = rework_fixture(with_consumable=True)

    missing_reservation = evaluate_evaluator_rework(
        prior,
        evaluator,
        compilation,
        candidate,
        scenario.snapshot,
        grant,
        (),
        ("add models",),
    )
    assert missing_reservation.disposition is ReworkDisposition.INDETERMINATE
    assert missing_reservation.corrective_subject is None

    missing_grant = evaluate_evaluator_rework(
        prior,
        evaluator,
        compilation,
        candidate,
        scenario.snapshot,
        None,
        reservations,
        ("add models",),
    )
    assert missing_grant.disposition is ReworkDisposition.INDETERMINATE
    assert missing_grant.corrective_subject is None

    reused_request = candidate.request.model_copy(
        update={"intended_attempt_id": prior.intended_attempt_id}
    )
    reused_resolution = candidate.resolution.model_copy(update={"request": reused_request})
    reused_attempt = candidate.model_copy(
        update={"request": reused_request, "resolution": reused_resolution}
    )
    reused_compilation = compilation.model_copy(update={"candidate": reused_attempt})
    reused_grant = grant.model_copy(
        update={
            "authority_candidate_digest": reused_attempt.content_digest,
            "intended_attempt_id": prior.intended_attempt_id,
        }
    )
    reused_result = evaluate_evaluator_rework(
        prior,
        evaluator,
        reused_compilation,
        reused_attempt,
        scenario.snapshot,
        reused_grant,
        reservations,
        ("add models",),
    )
    assert reused_result.disposition is ReworkDisposition.INDETERMINATE
    assert reused_result.corrective_subject is None

    accepted = evaluate_evaluator_rework(
        prior,
        evaluator,
        compilation,
        candidate,
        scenario.snapshot,
        grant,
        reservations,
        ("add models",),
    )
    assert accepted.disposition is ReworkDisposition.IN_SCOPE_REWORK
    assert accepted.corrective_subject is not None
    assert accepted.corrective_subject.required_reservation_keys == tuple(
        sorted(item.consumable_key for item in reservations)
    )


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
