"""Durable Human Authority commands and exact-basis concurrency checks."""

import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast
from urllib.parse import urlencode

import httpx
import pytest
from fastapi import FastAPI

import relay_engine.board.web as board_web
import relay_engine.human_control.service as human_service
from relay_engine.board.web import create_app
from relay_engine.domain.ids import (
    ArtifactId,
    BaselineId,
    HandoverGateId,
    ProjectId,
    SliceId,
    new_id,
)
from relay_engine.domain.models import (
    AcceptanceCriterion,
    Baseline,
    Project,
    ScopeSpec,
    Slice,
)
from relay_engine.domain.references import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.governance import (
    AuthorizationGrant,
    ChangeSurfaceStatus,
    GateReasonCode,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    HumanApprovalDecision,
    HumanApprovalValue,
    HumanChoiceDecision,
    HumanGateDecision,
    ReviewPolicy,
    RiskStatus,
    ToolchainChangeStatus,
    evaluate_handover_gates,
)
from relay_engine.human_control.errors import (
    HumanActionBasisStale,
    HumanActionConflict,
    HumanActionForbidden,
    HumanActionInvalidChoice,
    HumanActionNotAvailable,
    HumanActionRequiresEvaluation,
)
from relay_engine.human_control.models import HumanActionBasis, HumanActionKind
from relay_engine.human_control.service import (
    advance_green_handover,
    cancel_slice,
    clear_human_hold,
    grant_gate_authorization,
    project_human_actions,
    record_gate_approval,
    record_gate_choice,
    record_gate_rejection,
    set_human_hold,
)
from relay_engine.lifecycle import (
    LifecyclePhase,
    initialize_lifecycle,
    set_blocked,
    transition_phase,
)
from relay_engine.lifecycle.models import BlockageStatus, BlockReason, SliceLifecycle
from relay_engine.persistence import (
    DatabaseUnavailable,
    GateEvaluationRecord,
    RelayDatabase,
    insert_authorization_grant,
    insert_baseline,
    insert_gate_evaluation_record,
    insert_handover_gate,
    insert_human_decision,
    load_current_lifecycle,
    load_execution_records,
    load_gate_evaluation_records,
    load_human_decision,
    open_database,
    persist_lifecycle_change,
    persist_lifecycle_initialization,
    read_transaction,
)
from relay_engine.persistence.records import ExecutionRecord
from relay_engine.project_slice import MutationMetadata, create_project, create_slice

NOW = datetime(2026, 10, 2, 12, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
OTHER_PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789011"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
GATE_A: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"
GATE_B: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789021"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="owner/relay",
)


def _grant(
    gate_id: HandoverGateId,
    *,
    baseline_id: BaselineId = BASELINE_ID,
    gate_revision: int = 1,
    granted_at: datetime = NOW,
) -> AuthorizationGrant:
    return AuthorizationGrant(
        authorization_id=new_id("auth_"),
        slice_id=SLICE_ID,
        baseline_id=baseline_id,
        gate_id=gate_id,
        gate_revision=gate_revision,
        actor=ACTOR,
        granted_at=granted_at,
        reason="Persisted test authorization.",
    )


def _approval(
    gate_id: HandoverGateId,
    lifecycle: SliceLifecycle,
    *,
    governance_revision: int = 1,
    decision: HumanApprovalValue = HumanApprovalValue.APPROVE,
    occurred_at: datetime = NOW + timedelta(seconds=2),
) -> HumanApprovalDecision:
    return HumanApprovalDecision(
        decision_id=new_id("hdec_"),
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        gate_id=gate_id,
        gate_revision=1,
        lifecycle_revision=lifecycle.revision,
        governance_revision=governance_revision,
        actor=ACTOR,
        occurred_at=occurred_at,
        decision=decision,
        reason="Persisted test approval.",
    )


def _gate(
    gate_id: HandoverGateId = GATE_A,
    *,
    source_phase: LifecyclePhase = LifecyclePhase.PROPOSED,
    target_phase: LifecyclePhase = LifecyclePhase.READY,
    policy: HandoverPolicy = HandoverPolicy.AUTO,
    authorization_required: bool = False,
    required_artifact_ids: tuple[ArtifactId, ...] = (),
    change_surface_policy: ReviewPolicy = ReviewPolicy.ALLOW,
) -> HandoverGate:
    return HandoverGate(
        gate_id=gate_id,
        revision=1,
        key=f"gate-{gate_id[-1]}",
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        source_phase=source_phase,
        target_phase=target_phase,
        policy=policy,
        authorization_required=authorization_required,
        required_artifact_ids=required_artifact_ids,
        change_surface_policy=change_surface_policy,
    )


def _seed(
    path: Path,
    gates: tuple[HandoverGate, ...] | None = None,
    *,
    phase: LifecyclePhase = LifecyclePhase.PROPOSED,
    persisted_grants: tuple[AuthorizationGrant, ...] = (),
    context_grants: tuple[AuthorizationGrant, ...] = (),
    persisted_decisions: tuple[HumanGateDecision, ...] = (),
    context_decisions: tuple[HumanGateDecision, ...] = (),
    unrelated_blockers: tuple[BlockReason, ...] = (),
    evaluate: bool = True,
):
    database = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    project = Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY)
    slice_value = Slice(
        id=SLICE_ID,
        project_id=PROJECT_ID,
        title="Human control fixture",
        scope=ScopeSpec(in_scope=("governed actions",), out_of_scope=("automation",)),
        acceptance_criteria=(
            AcceptanceCriterion(key="A01", statement="Commands stay governed.", required=True),
        ),
    )
    metadata = MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Create fixture.")
    create_project(database, project, metadata)
    insert_baseline(
        database,
        Baseline(
            id=BASELINE_ID,
            project_id=PROJECT_ID,
            commit=CommitRef(repository=REPOSITORY, sha="a" * 40),
            artifact_ids=(),
            decision_ids=(),
        ),
    )
    create_slice(database, slice_value, metadata)
    lifecycle, initialized = initialize_lifecycle(
        SLICE_ID, new_id("evt_"), ACTOR, NOW, "Initialize fixture."
    )
    persist_lifecycle_initialization(database, lifecycle, initialized)
    phase_path = {
        LifecyclePhase.PROPOSED: (),
        LifecyclePhase.READY: (LifecyclePhase.READY,),
        LifecyclePhase.IMPLEMENTING: (
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
        ),
        LifecyclePhase.EVALUATING: (
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.EVALUATING,
        ),
    }.get(phase)
    if phase_path is None:
        raise ValueError("test fixture does not define a path to this lifecycle phase")
    for index, next_phase in enumerate(phase_path, start=1):
        lifecycle, event = transition_phase(
            lifecycle,
            next_phase,
            new_id("evt_"),
            ACTOR,
            NOW + timedelta(seconds=index),
            "Move fixture to the authorized test phase.",
        )
        persist_lifecycle_change(database, lifecycle.revision - 1, lifecycle, event)
    if unrelated_blockers:
        lifecycle, event = set_blocked(
            lifecycle,
            unrelated_blockers,
            new_id("evt_"),
            ACTOR,
            NOW + timedelta(seconds=len(phase_path) + 1),
            "Install unrelated test blockers.",
        )
        persist_lifecycle_change(database, lifecycle.revision - 1, lifecycle, event)
    gate_values = gates or (_gate(source_phase=phase),)
    for gate in gate_values:
        insert_handover_gate(database, gate)
    for grant in persisted_grants:
        insert_authorization_grant(database, grant)
    for decision in persisted_decisions:
        insert_human_decision(database, decision)
    latest = None
    if evaluate:
        context = HandoverContext(
            baseline_id=BASELINE_ID,
            governance_revision=1,
            lifecycle=lifecycle,
            authorization_grants=context_grants,
            human_decisions=context_decisions,
            change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
            risk_status=RiskStatus.CLEAR,
            toolchain_change_status=ToolchainChangeStatus.NONE,
        )
        latest = GateEvaluationRecord(
            id=new_id("geval_"),
            recorded_at=NOW + timedelta(seconds=10),
            gate_refs=tuple(
                # Gate input is required to use canonical order in every fixture.
                GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision)
                for gate in sorted(gate_values, key=lambda item: item.gate_id)
            ),
            context=context,
            evaluations=evaluate_handover_gates(gate_values, context),
        )
        insert_gate_evaluation_record(database, latest)
    return database, lifecycle, gate_values, latest


def _basis(database, gates: tuple[HandoverGate, ...]) -> HumanActionBasis:
    from relay_engine.persistence import (
        load_current_lifecycle_from_connection,
        load_gate_evaluation_records_for_slice_from_connection,
    )

    with read_transaction(database) as connection:
        lifecycle = load_current_lifecycle_from_connection(connection, SLICE_ID)
        assert lifecycle is not None
        records = load_gate_evaluation_records_for_slice_from_connection(connection, SLICE_ID)
        projection = project_human_actions(
            connection, SLICE_ID, lifecycle, gates, records[-1] if records else None
        )
        assert projection.basis is not None
        return projection.basis


def _gate_eval(record: GateEvaluationRecord, gate_id: HandoverGateId):
    return next(item for item in record.evaluations if item.gate_id == gate_id)


def _http_request(
    app: FastAPI, method: str, path: str, form: dict[str, str] | None = None
) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver", follow_redirects=False
        ) as client:
            if form is None:
                return await client.request(method, path)
            return await client.request(
                method,
                path,
                content=urlencode(form),
                headers={"content-type": "application/x-www-form-urlencoded"},
            )

    return asyncio.run(send())


def test_authorization_projector_prefers_earliest_exact_and_latest_stale(tmp_path: Path) -> None:
    first = _grant(GATE_A, granted_at=NOW + timedelta(seconds=1))
    second = _grant(GATE_A, granted_at=NOW + timedelta(seconds=2))
    database, lifecycle, gates, _ = _seed(
        tmp_path / "exact-grants.sqlite",
        (_gate(authorization_required=True),),
        persisted_grants=(second, first),
        context_grants=(first,),
    )
    try:
        with read_transaction(database) as connection:
            projection = project_human_actions(connection, SLICE_ID, lifecycle, gates, None)
        assert tuple(item.authorization_id for item in projection.current_authorizations) == (
            first.authorization_id,
        )
    finally:
        database.close()

    stale_older = _grant(GATE_A, gate_revision=2, granted_at=NOW + timedelta(seconds=1))
    stale_latest = _grant(GATE_A, gate_revision=3, granted_at=NOW + timedelta(seconds=2))
    database, _, gates, latest = _seed(
        tmp_path / "stale-grants.sqlite",
        (_gate(authorization_required=True),),
        persisted_grants=(stale_older, stale_latest),
        context_grants=(stale_latest,),
    )
    try:
        assert latest is not None
        assert GateReasonCode.AUTHORIZATION_STALE in {
            reason.code for reason in _gate_eval(latest, GATE_A).reasons
        }
        assert GateReasonCode.AUTHORIZATION_REQUIRED not in {
            reason.code for reason in _gate_eval(latest, GATE_A).reasons
        }
        with read_transaction(database) as connection:
            projection = project_human_actions(
                connection,
                SLICE_ID,
                load_current_lifecycle(database, SLICE_ID),
                gates,
                latest,
            )
        assert (
            projection.current_authorizations[-1].authorization_id == stale_latest.authorization_id
        )
    finally:
        database.close()


def test_authorize_is_atomic_advances_governance_and_keeps_gate_outcome_truthful(
    tmp_path: Path,
) -> None:
    gate = _gate(
        authorization_required=True,
        required_artifact_ids=(cast(ArtifactId, "art_018f47c1-7b2c-7abc-8def-123456789099"),),
    )
    database, _, gates, prior = _seed(tmp_path / "authorize.sqlite", (gate,))
    try:
        assert prior is not None
        basis = _basis(database, gates)
        successor = grant_gate_authorization(
            database, SLICE_ID, GATE_A, basis, ACTOR, "Authorize this exact handover."
        )
        grant = successor.context.authorization_grants[0]
        assert successor.context.governance_revision == prior.context.governance_revision + 1
        assert prior.recorded_at <= grant.granted_at <= successor.recorded_at
        assert _gate_eval(successor, GATE_A).light.value == "RED"
        assert GateReasonCode.AUTHORIZATION_REQUIRED not in {
            reason.code for reason in _gate_eval(successor, GATE_A).reasons
        }
        assert GateReasonCode.MISSING_REQUIRED_ARTIFACT in {
            reason.code for reason in _gate_eval(successor, GATE_A).reasons
        }
        assert len(load_gate_evaluation_records(database)) == 2
        assert (
            load_human_decision(database, cast(str, "hdec_018f47c1-7b2c-7abc-8def-123456789098"))
            is None
        )
    finally:
        database.close()


def test_unsynchronized_exact_grant_fails_closed_and_synchronized_retry_is_noop(
    tmp_path: Path,
) -> None:
    database, _, gates, _ = _seed(
        tmp_path / "unsynced.sqlite", (_gate(authorization_required=True),)
    )
    try:
        stale_basis = _basis(database, gates)
        existing = _grant(GATE_A, granted_at=NOW + timedelta(seconds=11))
        insert_authorization_grant(database, existing)
        before_evaluations = len(load_gate_evaluation_records(database))
        with pytest.raises(HumanActionRequiresEvaluation):
            grant_gate_authorization(
                database, SLICE_ID, GATE_A, stale_basis, ACTOR, "Do not synthesize an evaluation."
            )
        assert len(load_gate_evaluation_records(database)) == before_evaluations
    finally:
        database.close()

    database, _, gates, _ = _seed(tmp_path / "synced.sqlite", (_gate(authorization_required=True),))
    try:
        first = grant_gate_authorization(
            database, SLICE_ID, GATE_A, _basis(database, gates), ACTOR, "Authorize once."
        )
        count = len(load_gate_evaluation_records(database))
        retry = grant_gate_authorization(
            database, SLICE_ID, GATE_A, _basis(database, gates), ACTOR, "Retry authorization."
        )
        assert retry.id == first.id
        assert len(load_gate_evaluation_records(database)) == count
    finally:
        database.close()


def test_approval_rejection_retry_optimistic_identity_and_chronology(tmp_path: Path) -> None:
    gate = _gate(policy=HandoverPolicy.HUMAN_APPROVAL)
    database, _, gates, prior = _seed(tmp_path / "approvals.sqlite", (gate,))
    try:
        assert prior is not None
        first_basis = _basis(database, gates)
        approved = record_gate_approval(
            database,
            SLICE_ID,
            GATE_A,
            first_basis,
            None,
            ACTOR,
            "Approve this gate.",
            occurred_at=NOW + timedelta(seconds=11),
        )
        approval = next(
            item
            for item in approved.context.human_decisions
            if isinstance(item, HumanApprovalDecision)
        )
        assert approved.context.governance_revision == prior.context.governance_revision
        assert prior.recorded_at <= approval.occurred_at <= approved.recorded_at
        assert _gate_eval(approved, GATE_A).light.value == "GREEN"
        current_basis = _basis(database, gates)
        count = len(load_gate_evaluation_records(database))
        retry = record_gate_approval(
            database,
            SLICE_ID,
            GATE_A,
            current_basis,
            approval.decision_id,
            ACTOR,
            "Same target retry.",
        )
        assert retry.id == approved.id
        assert len(load_gate_evaluation_records(database)) == count
        with pytest.raises(HumanActionConflict):
            record_gate_rejection(
                database,
                SLICE_ID,
                GATE_A,
                current_basis,
                None,
                ACTOR,
                "A stale form cannot replace the current decision.",
            )
        rejected = record_gate_rejection(
            database,
            SLICE_ID,
            GATE_A,
            current_basis,
            approval.decision_id,
            ACTOR,
            "Reject after review.",
            occurred_at=NOW,
        )
        current = next(
            item
            for item in rejected.context.human_decisions
            if isinstance(item, HumanApprovalDecision)
        )
        assert current.decision is HumanApprovalValue.REJECT
        assert current.occurred_at >= approval.occurred_at
        assert _gate_eval(rejected, GATE_A).light.value == "RED"
        assert GateReasonCode.HUMAN_REJECTED in {
            reason.code for reason in _gate_eval(rejected, GATE_A).reasons
        }
    finally:
        database.close()


def test_choice_uses_exact_sorted_set_and_newer_choice_replaces_current_projection(
    tmp_path: Path,
) -> None:
    gates = tuple(
        sorted(
            (
                _gate(GATE_A, policy=HandoverPolicy.HUMAN_CHOICE),
                _gate(GATE_B, policy=HandoverPolicy.HUMAN_CHOICE),
            ),
            key=lambda item: item.gate_id,
        )
    )
    database, _, gates, _ = _seed(tmp_path / "choice.sqlite", gates)
    try:
        first = record_gate_choice(
            database,
            SLICE_ID,
            GATE_A,
            _basis(database, gates),
            None,
            ACTOR,
            "Select path A.",
        )
        choice = next(
            item for item in first.context.human_decisions if isinstance(item, HumanChoiceDecision)
        )
        assert tuple(item.gate_id for item in choice.choice_gate_refs) == (GATE_A, GATE_B)
        current_basis = _basis(database, gates)
        lifecycle = load_current_lifecycle(database, SLICE_ID)
        observations = load_gate_evaluation_records(database)
        assert lifecycle is not None
        with read_transaction(database) as connection:
            projection = project_human_actions(
                connection, SLICE_ID, lifecycle, gates, observations[-1]
            )
        assert any(action.kind is HumanActionKind.CHOOSE_PATH for action in projection.actions)
        with pytest.raises(HumanActionConflict):
            record_gate_choice(
                database,
                SLICE_ID,
                GATE_B,
                current_basis,
                None,
                ACTOR,
                "A stale expected identity conflicts.",
            )
        second = record_gate_choice(
            database,
            SLICE_ID,
            GATE_B,
            current_basis,
            choice.decision_id,
            ACTOR,
            "Select path B after review.",
        )
        latest_choice = next(
            item for item in second.context.human_decisions if isinstance(item, HumanChoiceDecision)
        )
        assert latest_choice.selected_gate_id == GATE_B
        assert latest_choice.decision_id != choice.decision_id
        assert GateReasonCode.NOT_SELECTED_BY_HUMAN in {
            reason.code for reason in _gate_eval(second, GATE_A).reasons
        }
    finally:
        database.close()


def test_human_hold_preserves_unrelated_blockers_advances_revision_and_stales_decision(
    tmp_path: Path,
) -> None:
    gate = _gate(
        source_phase=LifecyclePhase.READY,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.HUMAN_APPROVAL,
    )
    blocker = BlockReason(code="WAITING_FOR_INPUT", summary="An unrelated dependency is pending.")
    database, lifecycle, gates, _ = _seed(
        tmp_path / "hold.sqlite",
        (gate,),
        phase=LifecyclePhase.READY,
        unrelated_blockers=(blocker,),
        evaluate=False,
    )
    try:
        # Install a valid current observation, including a current approved decision.
        decision = _approval(GATE_A, lifecycle)
        insert_human_decision(database, decision)
        context = HandoverContext(
            baseline_id=BASELINE_ID,
            governance_revision=1,
            lifecycle=lifecycle,
            human_decisions=(decision,),
            change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
            risk_status=RiskStatus.CLEAR,
            toolchain_change_status=ToolchainChangeStatus.NONE,
        )
        initial = GateEvaluationRecord(
            id=new_id("geval_"),
            recorded_at=NOW + timedelta(seconds=10),
            gate_refs=(GateRevisionRef(gate_id=GATE_A, gate_revision=1),),
            context=context,
            evaluations=evaluate_handover_gates(gates, context),
        )
        insert_gate_evaluation_record(database, initial)
        before_revision = lifecycle.revision
        blocked = set_human_hold(
            database,
            SLICE_ID,
            HumanActionKind.PAUSE,
            before_revision,
            ACTOR,
            "Pause pending a human review.",
        )
        assert blocked.revision == before_revision + 1
        assert blocked.blockage.status is BlockageStatus.BLOCKED
        assert blocked.blockage.reasons == (
            blocker,
            BlockReason(code="HUMAN_PAUSE", summary="Pause pending a human review."),
        )
        observations = load_gate_evaluation_records(database)
        assert len(observations) == 2
        assert GateReasonCode.HUMAN_DECISION_STALE in {
            reason.code for reason in _gate_eval(observations[-1], GATE_A).reasons
        }
        resumed = clear_human_hold(
            database,
            SLICE_ID,
            blocked.revision,
            ACTOR,
            "Remove only the Human pause.",
        )
        assert resumed.revision == blocked.revision + 1
        assert resumed.blockage.status is BlockageStatus.BLOCKED
        assert resumed.blockage.reasons == (blocker,)
    finally:
        database.close()


def test_hold_without_valid_evaluation_persists_without_fabricating_observation(
    tmp_path: Path,
) -> None:
    database, lifecycle, _, _ = _seed(
        tmp_path / "hold-no-eval.sqlite",
        (_gate(source_phase=LifecyclePhase.READY, target_phase=LifecyclePhase.IMPLEMENTING),),
        phase=LifecyclePhase.READY,
        evaluate=False,
    )
    try:
        updated = set_human_hold(
            database,
            SLICE_ID,
            HumanActionKind.DEFER,
            lifecycle.revision,
            ACTOR,
            "Defer indefinitely.",
        )
        assert updated.revision == lifecycle.revision + 1
        assert load_gate_evaluation_records(database) == ()
        assert updated.blockage.reasons[-1].code == "HUMAN_DEFER"
    finally:
        database.close()


def test_hold_replaces_prior_human_hold_and_clear_removes_only_human_codes(tmp_path: Path) -> None:
    blocker = BlockReason(code="WAITING_FOR_REVIEW", summary="Review is pending.")
    database, lifecycle, _, _ = _seed(
        tmp_path / "hold-replace.sqlite",
        (_gate(source_phase=LifecyclePhase.READY, target_phase=LifecyclePhase.IMPLEMENTING),),
        phase=LifecyclePhase.READY,
        unrelated_blockers=(blocker,),
        evaluate=False,
    )
    try:
        first = set_human_hold(
            database, SLICE_ID, HumanActionKind.BLOCK, lifecycle.revision, ACTOR, "Block work."
        )
        second = set_human_hold(
            database, SLICE_ID, HumanActionKind.DEFER, first.revision, ACTOR, "Defer work."
        )
        assert second.blockage.reasons == (
            blocker,
            BlockReason(code="HUMAN_DEFER", summary="Defer work."),
        )
        cleared = clear_human_hold(database, SLICE_ID, second.revision, ACTOR, "Resume work.")
        assert cleared.blockage.reasons == (blocker,)
    finally:
        database.close()


def test_advance_rechecks_green_basis_and_persists_evaluation_event_execution(
    tmp_path: Path,
) -> None:
    database, lifecycle, gates, prior = _seed(tmp_path / "advance.sqlite")
    try:
        assert prior is not None
        basis = _basis(database, gates)
        execution = advance_green_handover(
            database, SLICE_ID, GATE_A, basis, ACTOR, "Advance through the current green gate."
        )
        current = load_current_lifecycle(database, SLICE_ID)
        assert current is not None and current.phase is LifecyclePhase.READY
        assert execution.gate_evaluation_record_id != prior.id
        assert execution.source_lifecycle_revision == lifecycle.revision
        assert execution.resulting_lifecycle_revision == lifecycle.revision + 1
        records = load_gate_evaluation_records(database)
        assert len(records) == 2
        assert records[-1].recorded_at <= execution.occurred_at
        assert load_execution_records(database)[-1] == execution
        with pytest.raises(HumanActionBasisStale):
            advance_green_handover(
                database, SLICE_ID, GATE_A, basis, ACTOR, "A second advance is stale."
            )
    finally:
        database.close()


def test_advance_rejects_red_yellow_and_accepted_target(tmp_path: Path) -> None:
    red_gate = _gate(
        required_artifact_ids=(cast(ArtifactId, "art_018f47c1-7b2c-7abc-8def-123456789099"),)
    )
    database, _, gates, _ = _seed(tmp_path / "advance-red.sqlite", (red_gate,))
    try:
        with pytest.raises(HumanActionNotAvailable):
            advance_green_handover(
                database, SLICE_ID, GATE_A, _basis(database, gates), ACTOR, "No."
            )
    finally:
        database.close()

    yellow_gate = _gate(authorization_required=True)
    database, _, gates, _ = _seed(tmp_path / "advance-yellow.sqlite", (yellow_gate,))
    try:
        with pytest.raises(HumanActionNotAvailable):
            advance_green_handover(
                database, SLICE_ID, GATE_A, _basis(database, gates), ACTOR, "No."
            )
    finally:
        database.close()

    accepted_gate = _gate(
        source_phase=LifecyclePhase.EVALUATING,
        target_phase=LifecyclePhase.ACCEPTED,
    )
    database, _, gates, _ = _seed(
        tmp_path / "advance-accepted.sqlite", (accepted_gate,), phase=LifecyclePhase.EVALUATING
    )
    try:
        with pytest.raises(HumanActionNotAvailable):
            advance_green_handover(
                database,
                SLICE_ID,
                GATE_A,
                _basis(database, gates),
                ACTOR,
                "Acceptance is excluded.",
            )
    finally:
        database.close()


def test_newer_reject_beats_older_approval_for_advance(tmp_path: Path) -> None:
    gate = _gate(policy=HandoverPolicy.HUMAN_APPROVAL)
    database, lifecycle, gates, _ = _seed(tmp_path / "newer-reject.sqlite", (gate,))
    try:
        approved = record_gate_approval(
            database, SLICE_ID, GATE_A, _basis(database, gates), None, ACTOR, "Approve."
        )
        approval = next(
            item
            for item in approved.context.human_decisions
            if isinstance(item, HumanApprovalDecision)
        )
        rejected = record_gate_rejection(
            database,
            SLICE_ID,
            GATE_A,
            _basis(database, gates),
            approval.decision_id,
            ACTOR,
            "Reject after reconsideration.",
        )
        current_decision = next(
            item
            for item in rejected.context.human_decisions
            if isinstance(item, HumanApprovalDecision)
        )
        assert current_decision.decision is HumanApprovalValue.REJECT
        assert len(load_execution_records(database)) == 0
        with pytest.raises(HumanActionNotAvailable):
            advance_green_handover(
                database,
                SLICE_ID,
                GATE_A,
                _basis(database, gates),
                ACTOR,
                "A prior approval cannot bypass the rejection.",
            )
        assert load_current_lifecycle(database, SLICE_ID) == lifecycle
    finally:
        database.close()


def test_cancel_requires_current_green_cancel_gate_and_is_governed(tmp_path: Path) -> None:
    gate = _gate(target_phase=LifecyclePhase.CANCELLED)
    database, lifecycle, gates, _ = _seed(tmp_path / "cancel.sqlite", (gate,))
    try:
        execution = cancel_slice(
            database,
            SLICE_ID,
            GATE_A,
            _basis(database, gates),
            ACTOR,
            "Cancel through the current gate.",
        )
        assert isinstance(execution, ExecutionRecord)
        cancelled = load_current_lifecycle(database, SLICE_ID)
        assert cancelled is not None and cancelled.phase is LifecyclePhase.CANCELLED
        assert execution.resulting_lifecycle_revision == lifecycle.revision + 1
        assert len(load_execution_records(database)) == 1
        assert cancel_slice(database, SLICE_ID, None, None, ACTOR, "Idempotent retry.") is None
        assert len(load_execution_records(database)) == 1
    finally:
        database.close()


def test_cancel_requires_existing_green_gate_and_does_not_mutate_phase_directly(
    tmp_path: Path,
) -> None:
    database, lifecycle, gates, _ = _seed(tmp_path / "cancel-no-gate.sqlite", (_gate(),))
    try:
        with pytest.raises(HumanActionNotAvailable):
            cancel_slice(
                database, SLICE_ID, GATE_A, _basis(database, gates), ACTOR, "Not a cancel gate."
            )
        assert load_current_lifecycle(database, SLICE_ID) == lifecycle
        assert load_execution_records(database) == ()
    finally:
        database.close()

    red_gate = _gate(
        target_phase=LifecyclePhase.CANCELLED,
        required_artifact_ids=(cast(ArtifactId, "art_018f47c1-7b2c-7abc-8def-123456789098"),),
    )
    database, lifecycle, gates, _ = _seed(tmp_path / "cancel-red.sqlite", (red_gate,))
    try:
        with pytest.raises(HumanActionNotAvailable):
            cancel_slice(
                database,
                SLICE_ID,
                GATE_A,
                _basis(database, gates),
                ACTOR,
                "Red cancellation is unavailable.",
            )
        assert load_current_lifecycle(database, SLICE_ID) == lifecycle
        assert load_execution_records(database) == ()
    finally:
        database.close()

    yellow = _gate(target_phase=LifecyclePhase.CANCELLED, authorization_required=True)
    database, lifecycle, gates, _ = _seed(tmp_path / "cancel-yellow.sqlite", (yellow,))
    try:
        with pytest.raises(HumanActionNotAvailable):
            cancel_slice(
                database, SLICE_ID, GATE_A, _basis(database, gates), ACTOR, "Yellow is unavailable."
            )
        assert load_current_lifecycle(database, SLICE_ID) == lifecycle
        assert load_execution_records(database) == ()
    finally:
        database.close()


def test_competing_decisions_serialize_and_failed_action_leaves_no_partial_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gate = _gate(policy=HandoverPolicy.HUMAN_APPROVAL)
    path = tmp_path / "concurrent.sqlite"
    database, _, gates, _ = _seed(path, (gate,))
    basis = _basis(database, gates)
    database.close()

    def command(target: HumanApprovalValue) -> str:
        connection = open_database(path, apply_migrations=False)
        try:
            if target is HumanApprovalValue.APPROVE:
                record_gate_approval(
                    connection, SLICE_ID, GATE_A, basis, None, ACTOR, "Competing approve."
                )
            else:
                record_gate_rejection(
                    connection, SLICE_ID, GATE_A, basis, None, ACTOR, "Competing reject."
                )
            return "accepted"
        except HumanActionBasisStale, HumanActionConflict:
            return "stale"
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(pool.map(command, (HumanApprovalValue.APPROVE, HumanApprovalValue.REJECT)))
    assert sorted(results) == ["accepted", "stale"]

    database = open_database(path, apply_migrations=False)
    try:
        decision_count = database.connection.execute(
            "SELECT count(*) FROM human_decisions"
        ).fetchone()[0]
        observation_count = len(load_gate_evaluation_records(database))
        current_basis = _basis(database, gates)
        current_id = current_basis.current_approval_decision_ids[0].decision_id
        current = load_human_decision(database, current_id)
        assert isinstance(current, HumanApprovalDecision)

        def fail_after_decision(*args, **kwargs):
            raise RuntimeError("force rollback after durable decision insert")

        monkeypatch.setattr(human_service, "_record_successor", fail_after_decision)
        if current.decision is HumanApprovalValue.APPROVE:
            command_value = record_gate_rejection
        else:
            command_value = record_gate_approval
        with pytest.raises(RuntimeError):
            command_value(
                database,
                SLICE_ID,
                GATE_A,
                current_basis,
                current.decision_id,
                ACTOR,
                "A later evaluation failure rolls back the decision.",
            )
        assert (
            database.connection.execute("SELECT count(*) FROM human_decisions").fetchone()[0]
            == decision_count
        )
        assert len(load_gate_evaluation_records(database)) == observation_count
    finally:
        database.close()


def test_non_human_actor_is_forbidden_before_write(tmp_path: Path) -> None:
    database, _, gates, _ = _seed(tmp_path / "actor.sqlite", (_gate(authorization_required=True),))
    system = ActorRef(id=new_id("act_"), kind=ActorKind.SYSTEM)
    try:
        before = len(load_gate_evaluation_records(database))
        with pytest.raises(HumanActionForbidden):
            grant_gate_authorization(
                database,
                SLICE_ID,
                GATE_A,
                _basis(database, gates),
                system,
                "System cannot authorize.",
            )
        assert len(load_gate_evaluation_records(database)) == before
    finally:
        database.close()


def test_expected_gate_choice_must_be_exact_current_choice_set(tmp_path: Path) -> None:
    gates = (_gate(GATE_A, policy=HandoverPolicy.HUMAN_CHOICE),)
    database, _, gates, _ = _seed(tmp_path / "invalid-choice.sqlite", gates)
    try:
        with pytest.raises(HumanActionInvalidChoice):
            record_gate_choice(
                database,
                SLICE_ID,
                GATE_B,
                _basis(database, gates),
                None,
                ACTOR,
                "Choose outside current set.",
            )
    finally:
        database.close()


def test_web_controls_are_accessible_csrf_protected_server_bound_and_prg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database, _, gates, _ = _seed(
        tmp_path / "human-web.sqlite", (_gate(authorization_required=True),)
    )
    app = create_app(database.path, actor=ACTOR)
    path = f"/projects/{PROJECT_ID}/slices/{SLICE_ID}"
    try:
        page = _http_request(app, "GET", path)
        assert page.status_code == 200
        assert '<section aria-labelledby="human-actions-heading">' in page.text
        assert "Current Human evidence" in page.text
        assert "evaluation <code>" in page.text
        assert 'name="csrf_token"' in page.text
        assert "<fieldset><legend>Authorize</legend>" in page.text
        assert "<label>Reason <textarea" in page.text

        original_open = board_web.open_database
        opened: list[RelayDatabase] = []

        def tracked_open(database_path, *, apply_migrations, **kwargs):
            connection = original_open(database_path, apply_migrations=apply_migrations, **kwargs)
            opened.append(connection)
            return connection

        monkeypatch.setattr(board_web, "open_database", tracked_open)
        form = {
            "gate_id": GATE_A,
            "basis": _basis(database, gates).model_dump_json(),
            "reason": "Authorize using the server-bound Human actor.",
        }
        missing_csrf = _http_request(app, "POST", f"{path}/actions/authorize", form)
        assert missing_csrf.status_code == 403
        assert opened == []
        assert (
            database.connection.execute("SELECT count(*) FROM authorization_grants").fetchone()[0]
            == 0
        )

        form.update(
            {
                "csrf_token": app.state.csrf_token,
                "actor_kind": "SYSTEM",
                "actor_id": new_id("act_"),
            }
        )
        response = _http_request(app, "POST", f"{path}/actions/authorize", form)
        assert response.status_code == 303
        assert response.headers["location"] == path
        assert len(opened) == 1
        with pytest.raises(sqlite3.ProgrammingError):
            opened[0].connection.execute("SELECT 1")
        rows = database.connection.execute(
            "SELECT payload_json FROM authorization_grants"
        ).fetchall()
        assert len(rows) == 1
        assert AuthorizationGrant.model_validate_json(rows[0][0]).actor == ACTOR
    finally:
        database.close()


def test_choice_control_posts_to_explicit_choose_route(tmp_path: Path) -> None:
    database, _, gates, _ = _seed(
        tmp_path / "human-choice-form.sqlite",
        (_gate(policy=HandoverPolicy.HUMAN_CHOICE),),
    )
    app = create_app(database.path, actor=ACTOR)
    path = f"/projects/{PROJECT_ID}/slices/{SLICE_ID}"
    try:
        page = _http_request(app, "GET", path)
        assert page.status_code == 200
        assert f'<form method="post" action="{path}/actions/choose">' in page.text
        assert f"{path}/actions/choose_path" not in page.text
    finally:
        database.close()


def test_web_maps_invalid_stale_not_found_integrity_and_unavailable_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gate = _gate(
        source_phase=LifecyclePhase.READY,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.HUMAN_CHOICE,
    )
    database, lifecycle, gates, _ = _seed(
        tmp_path / "human-web-errors.sqlite", (gate,), phase=LifecyclePhase.READY
    )
    app = create_app(database.path, actor=ACTOR)
    token = app.state.csrf_token
    path = f"/projects/{PROJECT_ID}/slices/{SLICE_ID}"
    basis_json = _basis(database, gates).model_dump_json()
    try:
        invalid = _http_request(
            app,
            "POST",
            f"{path}/actions/choose",
            {
                "csrf_token": token,
                "basis": basis_json,
                "selected_gate_id": GATE_B,
                "expected_current_choice_decision_id": "",
                "reason": "Invalid gate should be rejected.",
            },
        )
        assert invalid.status_code == 422

        set_human_hold(
            database,
            SLICE_ID,
            HumanActionKind.BLOCK,
            lifecycle.revision,
            ACTOR,
            "Advance the lifecycle revision to stale the form.",
        )
        stale = _http_request(
            app,
            "POST",
            f"{path}/actions/choose",
            {
                "csrf_token": token,
                "basis": basis_json,
                "selected_gate_id": GATE_A,
                "expected_current_choice_decision_id": "",
                "reason": "Stale form should not rebase.",
            },
        )
        assert stale.status_code == 409

        missing_slice_project = _http_request(
            app,
            "POST",
            f"/projects/{OTHER_PROJECT_ID}/slices/{SLICE_ID}/actions/choose",
            {
                "csrf_token": token,
                "basis": basis_json,
                "selected_gate_id": GATE_A,
                "reason": "Wrong project is not found.",
            },
        )
        assert missing_slice_project.status_code == 404

        database.connection.execute(
            "INSERT INTO human_decisions(decision_id, decision_type, baseline_id, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (new_id("hdec_"), "BrokenDecision", BASELINE_ID, "{}"),
        )
        integrity = _http_request(
            app,
            "POST",
            f"{path}/actions/choose",
            {
                "csrf_token": token,
                "basis": basis_json,
                "selected_gate_id": GATE_A,
                "reason": "Corrupt decision payload should fail closed.",
            },
        )
        assert integrity.status_code == 500
        assert "INTEGRITY_ERROR" in integrity.text

        def unavailable(*args: object, **kwargs: object) -> RelayDatabase:
            raise DatabaseUnavailable("simulated unavailable storage")

        monkeypatch.setattr(board_web, "open_database", unavailable)
        unavailable_response = _http_request(
            app,
            "POST",
            f"{path}/actions/resume",
            {"csrf_token": token},
        )
        assert unavailable_response.status_code == 503
        assert "UNAVAILABLE" in unavailable_response.text
    finally:
        database.close()


def test_web_rejects_system_actor_for_human_command(tmp_path: Path) -> None:
    database, _, gates, _ = _seed(
        tmp_path / "human-web-system.sqlite", (_gate(authorization_required=True),)
    )
    app = create_app(database.path, actor=ActorRef(id=new_id("act_"), kind=ActorKind.SYSTEM))
    path = f"/projects/{PROJECT_ID}/slices/{SLICE_ID}/actions/authorize"
    before = database.connection.execute("SELECT count(*) FROM authorization_grants").fetchone()[0]
    try:
        response = _http_request(
            app,
            "POST",
            path,
            {
                "csrf_token": app.state.csrf_token,
                "basis": _basis(database, gates).model_dump_json(),
                "gate_id": GATE_A,
                "reason": "System actor must not authorize.",
            },
        )
        assert response.status_code == 403
        assert (
            database.connection.execute("SELECT count(*) FROM authorization_grants").fetchone()[0]
            == before
        )
    finally:
        database.close()
