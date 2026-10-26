"""Deterministic scenario outcomes and authority boundary checks."""

from __future__ import annotations

import pytest

from relay_engine.coding_execution.coordinator import (
    derive_workspace_change_state,
    runtime_event_stream_is_contiguous,
    runtime_output_limit_contract_gap,
)
from relay_engine.coding_execution.evaluation import apply_scope_and_successor_disposition
from relay_engine.coding_execution.models import (
    ContractGapAnalysis,
    ExecutionTerminalOutcome,
    InternalProgressObservation,
    ProposedWorkObservation,
    execution_id_for_attempt,
)
from relay_engine.role_contracts import (
    SuccessorResolution,
    WorkDisposition,
    disposition_for_successor,
)

_D = "sha256:" + "d" * 64
_EXECUTION = "exec_018f47c1-7b2c-7abc-8def-123456789008"


def test_internal_progress_is_non_authoritative_and_bound_to_execution() -> None:
    observations = (
        InternalProgressObservation(
            execution_id=_EXECUTION,
            milestone_key="implementation",
            status="COMPLETE",
            evidence_digest=_D,
        ),
        InternalProgressObservation(
            execution_id=_EXECUTION,
            milestone_key="validation",
            status="COMPLETE",
            evidence_digest="sha256:" + "e" * 64,
        ),
    )
    assert all(item.execution_id == _EXECUTION for item in observations)
    assert all(item.status != "ACCEPT" for item in observations)
    assert tuple(item.milestone_key for item in observations) == ("implementation", "validation")


def test_proposed_work_observation_is_not_a_terminal_result() -> None:
    proposed = ProposedWorkObservation(
        source_execution_id=_EXECUTION,
        summary="A follow-up is needed",
        rationale="The discovery is outside the packet.",
        proposal_digest=_D,
        applicable_hard_stop_key="scope-expansion",
    )
    assert proposed.applicable_hard_stop_key == "scope-expansion"
    assert "PROPOSED_WORK" not in {item.value for item in ExecutionTerminalOutcome}


def test_no_authorized_successor_preserves_existing_backlog_exhausted_disposition() -> None:
    assert (
        disposition_for_successor(SuccessorResolution.NO_AUTHORIZED_SUCCESSOR)
        is WorkDisposition.BACKLOG_EXHAUSTED
    )


def test_scope_expansion_records_observation_and_stops_under_packet_hard_stop() -> None:
    proposed = ProposedWorkObservation(
        source_execution_id=_EXECUTION,
        summary="A separate deployment task was discovered",
        rationale="Deployment is outside the authorized coding packet.",
        proposal_digest=_D,
        applicable_hard_stop_key="scope-expansion",
    )
    outcome, reasons = apply_scope_and_successor_disposition(
        ExecutionTerminalOutcome.DONE,
        ("scope-expansion",),
        (proposed,),
        None,
    )
    assert outcome is ExecutionTerminalOutcome.BLOCKED_BY_AUTHORITY
    assert reasons == ("proposed-work:scope-stop",)

    unbound_outcome, unbound_reasons = apply_scope_and_successor_disposition(
        ExecutionTerminalOutcome.DONE,
        (),
        (proposed,),
        None,
    )
    assert unbound_outcome is ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT
    assert unbound_reasons == ("proposed-work:hard-stop-unbound",)


def test_backlog_exhaustion_is_successful_stop_and_does_not_override_existing_blocker() -> None:
    outcome, reasons = apply_scope_and_successor_disposition(
        ExecutionTerminalOutcome.DONE,
        (),
        (),
        SuccessorResolution.NO_AUTHORIZED_SUCCESSOR,
    )
    assert outcome is ExecutionTerminalOutcome.BACKLOG_EXHAUSTED
    assert reasons == ()

    blocked, _ = apply_scope_and_successor_disposition(
        ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT,
        (),
        (),
        SuccessorResolution.NO_AUTHORIZED_SUCCESSOR,
    )
    assert blocked is ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT


def test_new_attempt_identity_cannot_be_replaced_by_runtime_session() -> None:
    first = "exec-018f47c1-7b2c-7abc-8def-123456789008"
    second = "exec-018f47c1-7b2c-7abc-8def-123456789009"
    assert execution_id_for_attempt(first) == _EXECUTION
    assert execution_id_for_attempt(second) != _EXECUTION


def test_event_gap_and_session_substitution_fail_exact_runtime_continuity() -> None:
    from datetime import UTC, datetime

    from relay_engine.agent_runtime import (
        RuntimeEventEnvelope,
        RuntimeEventType,
        RuntimeSessionRef,
    )

    session = RuntimeSessionRef(runtime_id="fake-runtime", session_id="session-one")
    event = RuntimeEventEnvelope(
        execution_id=_EXECUTION,
        runtime_session=session,
        sequence=1,
        event_type=RuntimeEventType.EXECUTION_STARTED,
        observed_at=datetime(2026, 10, 1, tzinfo=UTC),
    )
    assert runtime_event_stream_is_contiguous((event,), _EXECUTION, session)
    assert not runtime_event_stream_is_contiguous(
        (event.model_copy(update={"sequence": 2}),), _EXECUTION, session
    )
    assert not runtime_event_stream_is_contiguous(
        (event,), _EXECUTION, session.model_copy(update={"session_id": "other-session"})
    )
    gap = event.model_copy(update={"event_type": RuntimeEventType.EVENT_GAP})
    assert not runtime_event_stream_is_contiguous((gap,), _EXECUTION, session)


def test_contract_gap_record_does_not_authorize_predecessor_mutation() -> None:
    gap = ContractGapAnalysis(
        owning_slice="slice-2-1",
        contract_reference="agent-runtime-contract",
        required_behavior="Prove exact terminal output bytes",
        failing_scenario="runtime output cap is active but adapter omits byte count",
        missing_contract_element="exact output byte usage",
        composition_failure="existing inspection does not report the metric",
        minimum_amendment="add a typed output-byte observation",
        security_consequences="without it the output limit cannot be proven",
        analysis_digest=_D,
    )
    assert gap.owning_slice == "slice-2-1"


def test_unobservable_output_byte_limit_yields_exact_predecessor_contract_gap() -> None:
    from types import SimpleNamespace
    from typing import cast

    from relay_engine.agent_runtime import RuntimeExecutionRequest

    request = cast(
        RuntimeExecutionRequest,
        SimpleNamespace(
            basis=SimpleNamespace(
                limits=SimpleNamespace(
                    max_output_bytes=1024,
                )
            )
        ),
    )

    gap = runtime_output_limit_contract_gap(request)

    assert gap is not None
    assert gap.owning_slice == "slice-2-1"
    assert gap.contract_reference == "agent-runtime-runtime-usage"
    assert "byte" in gap.missing_contract_element.lower()


def test_implementer_cannot_self_accept_exact_terminal_handoff() -> None:

    from test_execution_workspace_evaluation import conformance_fixture, resolver_fixture
    from test_work_packet_models import manifest

    from relay_engine.agent_runtime import (
        RuntimeDescriptor,
        RuntimeExecutionBasis,
        RuntimeExecutionRequest,
        RuntimeInputPayload,
        digest_execution_basis,
    )
    from relay_engine.coding_execution.evaluation import (
        digest_runtime_payload_content,
        prior_execution_binding,
    )
    from relay_engine.coding_execution.models import (
        ConsumableReservationBinding,
        ExecutionEvidenceBundle,
        ExecutionSubject,
        HumanGrantBinding,
        RuntimePayloadEvidence,
        RuntimePermissionEvidence,
        TerminalExecutionResult,
        _digest_canonical_model,
        digest_evaluator_handoff,
    )
    from relay_engine.domain import ActorKind, ActorRef
    from relay_engine.execution_workspace import derive_runtime_workspace_attachment
    from relay_engine.execution_workspace.evaluation import (
        resolve_workspace_plan,
        workspace_plan_ref,
        workspace_provider_ref,
    )
    from relay_engine.execution_workspace.models import WorkPacketConformanceFact
    from relay_engine.role_contracts import RequirementStatus
    from relay_engine.work_packets import (
        WorkPacketConformance,
        context_manifest_ref,
    )

    packet, packet_ref, policy, role, provider = resolver_fixture()
    context = manifest()
    plan_resolution = resolve_workspace_plan(
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
        plan_key="self-acceptance-test",
        revision=1,
    )
    assert plan_resolution.plan is not None
    plan = plan_resolution.plan
    workspace_instance, workspace_facts = conformance_fixture(plan, provider)
    attachment = derive_runtime_workspace_attachment(workspace_instance)
    attempt = "exec-018f47c1-7b2c-7abc-8def-123456789008"
    execution_id = execution_id_for_attempt(attempt)
    candidate_digest = "sha256:" + "a" * 64
    grant = HumanGrantBinding(
        grant_record_id="human-grant-immutable",
        grant_record_digest="sha256:" + "b" * 64,
        authority_candidate_digest=candidate_digest,
        intended_attempt_id=attempt,
        project_id=packet.project_id,
        slice_id=packet.slice_definition_ref.slice_id,
        valid=True,
        applicable=True,
    )
    selection = packet.runtime_selection_requirement
    permission_ref = packet.runtime_permission_profile_ref
    assert selection is not None and permission_ref is not None
    descriptor = RuntimeDescriptor(
        runtime_id=selection.runtime_id,
        adapter_version="1",
        runtime_version=None,
        api_generation="test-v1",
        capabilities=packet.required_runtime_capabilities,
    )
    payload = RuntimeInputPayload(
        text="Exact packet prompt.",
        payload_digest="sha256:" + "c" * 64,
    )
    payload = payload.model_copy(update={"payload_digest": digest_runtime_payload_content(payload)})
    basis = RuntimeExecutionBasis(
        execution_id=execution_id,
        slice_id=packet.slice_definition_ref.slice_id,
        source_baseline_id=packet.source_baseline_ref.baseline_id,
        workspace=attachment,
        input_payload=payload,
        runtime_selection=selection,
        permission_profile_ref=permission_ref,
        credential_refs=packet.credential_refs,
        required_capabilities=packet.required_runtime_capabilities,
        limits=packet.runtime_limits,
    )
    request = RuntimeExecutionRequest(
        basis=basis,
        request_digest=digest_execution_basis(basis),
    )
    runtime_payload_evidence = RuntimePayloadEvidence(
        work_packet_ref=packet_ref,
        context_manifest_ref=context_manifest_ref(context),
        payload_digest=payload.payload_digest,
        included_context_keys=packet.required_context_keys,
        status=RequirementStatus.SATISFIED,
        protected_content_exposed=False,
        evaluator_only_content_exposed=False,
        credential_exposure_status="CLEAR",
        evidence_digest="sha256:" + "d" * 64,
    )
    runtime_permission_evidence = RuntimePermissionEvidence(
        execution_id=execution_id,
        runtime_id=selection.runtime_id,
        attestation_id="runtime-permission-attestation",
        evidence_digest="sha256:" + "e" * 64,
        effective_profile_ref=permission_ref,
        completeness=RequirementStatus.SATISFIED,
        exposed_tools=(),
        shell_exposed=False,
        actual_provider_id=selection.requested_provider_id,
        actual_model_id=selection.requested_model_id,
        provenance_status=RequirementStatus.SATISFIED,
    )
    subject = ExecutionSubject(
        project_id=packet.project_id,
        slice_id=packet.slice_definition_ref.slice_id,
        candidate_digest=candidate_digest,
        human_grant=grant,
        intended_attempt_id=attempt,
        execution_id=execution_id,
        work_packet=packet,
        work_packet_ref=packet_ref,
        context_manifest_ref=context_manifest_ref(context),
        role_contract_ref=packet.role_contract_ref,
        actor=ActorRef(
            id="act_018f47c1-7b2c-7abc-8def-123456789008",
            kind=ActorKind.AGENT,
        ),
        workspace_plan_ref=workspace_plan_ref(plan),
        workspace_instance=workspace_instance,
        runtime_workspace_attachment=attachment,
        workspace_provider_ref=workspace_provider_ref(provider),
        runtime_descriptor=descriptor,
        runtime_request=request,
        runtime_payload_evidence=runtime_payload_evidence,
        runtime_permission_evidence=runtime_permission_evidence,
        actual_provider_id=selection.requested_provider_id,
        actual_model_id=selection.requested_model_id,
    )

    reservation_a = ConsumableReservationBinding(
        consumable_key="campaign-budget",
        scope_key="scope-a",
        grant_record_digest=grant.grant_record_digest,
        authority_candidate_digest=candidate_digest,
        intended_attempt_id=attempt,
        evidence_id="reservation-a",
        evidence_digest="sha256:" + "c" * 64,
        state="RESERVED",
        created_atomically_at_grant=True,
    )
    reservation_b = reservation_a.model_copy(
        update={"scope_key": "scope-b", "evidence_id": "reservation-b"}
    )
    pair_subject_data = subject.model_dump(mode="python")
    pair_subject_data["reservations"] = (reservation_a, reservation_b)
    pair_subject = ExecutionSubject.model_validate(pair_subject_data)
    assert pair_subject.reservations == (reservation_a, reservation_b)

    duplicate_subject_data = dict(pair_subject_data)
    duplicate_subject_data["reservations"] = (
        reservation_a,
        reservation_a.model_copy(update={"evidence_id": "reservation-duplicate"}),
    )
    with pytest.raises(ValueError, match="unique and sorted by consumable and scope"):
        ExecutionSubject.model_validate(duplicate_subject_data)

    evidence = ExecutionEvidenceBundle(
        execution_subject_digest=subject.content_digest,
        grant=grant,
        reservations=(),
        runtime_request=request,
        runtime_payload_evidence=runtime_payload_evidence,
        runtime_permission_evidence=runtime_permission_evidence,
        runtime_session=None,
        runtime_handle=None,
        runtime_inspection=None,
        workspace_instance=workspace_instance,
        initial_workspace_inspection=workspace_facts.initial_inspection,
        terminal_workspace_conformance_status=RequirementStatus.SATISFIED,
        initial_workspace_digest=_digest_canonical_model(workspace_facts.initial_inspection),
    )
    outcome = ExecutionTerminalOutcome.BLOCKED_BY_CONTRACT

    result = TerminalExecutionResult(
        execution_id=execution_id,
        subject=subject,
        outcome=outcome,
        evidence=evidence,
        evaluator_handoff_digest=digest_evaluator_handoff(subject, outcome, evidence),
    )
    prior = prior_execution_binding(result)
    assert prior.authority_candidate_digest == subject.candidate_digest
    assert prior.terminal_candidate_digest is None
    assert prior.terminal_result_digest.startswith("sha256:")
    assert prior.handoff_digest == result.evaluator_handoff_digest
    assert prior.intended_attempt_id == subject.intended_attempt_id
    assert prior.execution_id == subject.execution_id
    assert prior.work_packet_ref == subject.work_packet_ref

    with pytest.raises(ValueError, match="cannot self-accept"):
        TerminalExecutionResult(
            execution_id=execution_id,
            subject=subject,
            outcome=outcome,
            evidence=evidence,
            evaluator_handoff_digest=digest_evaluator_handoff(subject, outcome, evidence),
            self_acceptance_attempted=True,
        )


def test_dirty_workspace_without_commit_is_reported_without_inventing_commit() -> None:
    from test_execution_workspace_evaluation import conformance_fixture, resolver_fixture

    from relay_engine.execution_workspace import resolve_workspace_plan
    from relay_engine.execution_workspace.models import WorkPacketConformanceFact
    from relay_engine.role_contracts import RequirementStatus
    from relay_engine.work_packets import WorkPacketConformance

    packet, packet_ref, policy, role, provider = resolver_fixture()
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
        plan_key="scenario-dirty-workspace",
        revision=1,
    )
    assert resolution.plan is not None
    instance, facts = conformance_fixture(resolution.plan, provider)
    dirty_inspection = facts.initial_inspection.model_copy(
        update={"tracked_changes": ("src/relay_engine/coding_execution.py",)}
    )

    dirty, local_commit, parent = derive_workspace_change_state(instance, dirty_inspection)

    assert dirty is True
    assert local_commit is None
    assert parent is None


def test_new_local_commit_binds_the_exact_source_parent() -> None:
    from test_execution_workspace_evaluation import conformance_fixture, resolver_fixture

    from relay_engine.execution_workspace import resolve_workspace_plan
    from relay_engine.execution_workspace.models import WorkPacketConformanceFact
    from relay_engine.role_contracts import RequirementStatus
    from relay_engine.work_packets import WorkPacketConformance

    packet, packet_ref, policy, role, provider = resolver_fixture()
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
        plan_key="scenario-local-commit",
        revision=1,
    )
    assert resolution.plan is not None
    instance, facts = conformance_fixture(resolution.plan, provider)
    new_commit = instance.source_commit.model_copy(update={"sha": "f" * 40})
    committed_inspection = facts.initial_inspection.model_copy(update={"head_commit": new_commit})

    dirty, local_commit, parent = derive_workspace_change_state(instance, committed_inspection)

    assert dirty is False
    assert local_commit == "f" * 40
    assert parent == instance.source_commit.sha


def test_runtime_reported_tool_call_limit_is_detected_and_unobservable_limits_block() -> None:
    from datetime import UTC, datetime
    from types import SimpleNamespace
    from typing import cast

    from relay_engine.agent_runtime import (
        RuntimeContinuityState,
        RuntimeEventEnvelope,
        RuntimeEventType,
        RuntimeSessionRef,
    )
    from relay_engine.agent_runtime.models import (
        RuntimeExecutionHandle,
        RuntimeExecutionInspection,
        RuntimeExecutionRequest,
    )
    from relay_engine.coding_execution.coordinator import _evaluate_usage_limits

    session = RuntimeSessionRef(runtime_id="fake-runtime", session_id="session-one")
    tool_events = tuple(
        RuntimeEventEnvelope(
            execution_id=_EXECUTION,
            runtime_session=session,
            sequence=index,
            event_type=RuntimeEventType.TOOL_REQUESTED,
            observed_at=datetime(2026, 10, 1, tzinfo=UTC),
            payload={"tool_identity": "unit-test-tool"},
        )
        for index in (1, 2)
    )
    request = cast(
        RuntimeExecutionRequest,
        SimpleNamespace(
            basis=SimpleNamespace(
                limits=SimpleNamespace(
                    max_tool_calls=1,
                    max_duration_seconds=None,
                    max_output_bytes=None,
                )
            )
        ),
    )
    overrun, unknown = _evaluate_usage_limits(
        request,
        cast(RuntimeExecutionHandle, None),
        cast(RuntimeExecutionInspection, None),
        tool_events,
    )
    assert overrun is True
    assert unknown is False

    request_with_unobservable_limit = cast(
        RuntimeExecutionRequest,
        SimpleNamespace(
            basis=SimpleNamespace(
                limits=SimpleNamespace(
                    max_tool_calls=None,
                    max_duration_seconds=10,
                    max_output_bytes=None,
                )
            )
        ),
    )
    overrun, unknown = _evaluate_usage_limits(
        request_with_unobservable_limit,
        cast(RuntimeExecutionHandle, None),
        cast(
            RuntimeExecutionInspection,
            SimpleNamespace(
                terminal=False,
                continuity=SimpleNamespace(state=RuntimeContinuityState.INCOMPLETE),
            ),
        ),
        (),
    )
    assert overrun is False
    assert unknown is True


def test_protected_asset_mutation_without_exact_authority_is_nonconformant() -> None:
    from test_execution_workspace_evaluation import conformance_fixture, resolver_fixture

    from relay_engine.execution_workspace import (
        evaluate_workspace_conformance,
        resolve_workspace_plan,
    )
    from relay_engine.execution_workspace.models import (
        ProtectedAssetObservation,
        WorkPacketConformanceFact,
        WorkspaceChangeEntry,
        WorkspaceChangeManifest,
        WorkspaceEntryKind,
        WorkspaceEntryState,
        WorkspaceReason,
    )
    from relay_engine.role_contracts import RequirementStatus
    from relay_engine.work_packets import WorkPacketConformance

    packet, packet_ref, policy, role, provider = resolver_fixture()
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
        plan_key="scenario-protected-mutation",
        revision=1,
    )
    assert resolution.plan is not None
    plan = resolution.plan
    instance, facts = conformance_fixture(plan, provider)
    binding = plan.protected_asset_bindings[0]
    before = WorkspaceEntryState(
        kind=WorkspaceEntryKind.REGULAR_FILE,
        content_digest="sha256:" + "1" * 64,
        symlink_target_digest=None,
        executable=False,
    )
    after = before.model_copy(update={"content_digest": "sha256:" + "2" * 64})
    initial_observation = ProtectedAssetObservation(
        requirement_ref=binding.requirement_ref,
        workspace_path=binding.workspace_path,
        state=before,
    )
    terminal_observation = initial_observation.model_copy(update={"state": after})
    initial = facts.initial_inspection.model_copy(
        update={"protected_asset_observations": (initial_observation,)}
    )
    terminal = initial.model_copy(
        update={
            "tracked_changes": (binding.workspace_path,),
            "protected_asset_observations": (terminal_observation,),
        }
    )
    changes = WorkspaceChangeManifest(
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
            "terminal_inspection": terminal,
            "change_manifest": changes,
        }
    )

    result = evaluate_workspace_conformance(
        plan,
        instance,
        plan.provider_ref,
        terminal_facts,
        terminal=True,
    )

    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkspaceReason.PROTECTED_ASSET_MUTATED in result.reasons
