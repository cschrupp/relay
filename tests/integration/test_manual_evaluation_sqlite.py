"""Slice 1.7 result, authored evaluation, and acceptance integration tests."""

import asyncio
import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast
from urllib.parse import urlencode

import httpx
import pytest

import relay_engine.manual_evaluation.service as manual_evaluation_service
from relay_engine.board.service import slice_detail
from relay_engine.board.web import create_app
from relay_engine.domain.ids import (
    ArtifactId,
    BaselineId,
    DecisionId,
    EvidenceId,
    GateEvaluationRecordId,
    HandoverGateId,
    ManualEvaluationId,
    ProjectId,
    SliceId,
    new_id,
)
from relay_engine.domain.models import (
    AcceptanceCriterion,
    Artifact,
    Baseline,
    Project,
    ScopeSpec,
    Slice,
)
from relay_engine.domain.references import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.governance import (
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    HumanApprovalValue,
    QualityCheckResult,
    QualityCheckStatus,
    RiskStatus,
    ToolchainChangeStatus,
    TrafficLight,
)
from relay_engine.human_control.errors import HumanActionRequiresEvaluation
from relay_engine.human_control.models import HumanActionBasis
from relay_engine.human_control.service import (
    basis_if_current,
    load_human_control_snapshot,
    record_gate_approval,
)
from relay_engine.integrations.github.models import GitHubRepositoryAccessSelection
from relay_engine.lifecycle import LifecyclePhase, initialize_lifecycle, transition_phase
from relay_engine.lifecycle.models import SliceLifecycle
from relay_engine.manual_evaluation.errors import ManualEvaluationConflict, ManualEvaluationStale
from relay_engine.manual_evaluation.models import (
    EvaluationEvidenceSubmission,
    SliceResultRecord,
)
from relay_engine.manual_evaluation.service import (
    attach_result,
    promote_accepted_result,
    record_manual_evaluation,
    record_technical_acceptance,
)
from relay_engine.persistence import (
    DEFAULT_MIGRATIONS,
    MANUAL_EVALUATION_MIGRATION,
    GateEvaluationRecord,
    apply_migrations,
    insert_artifact,
    insert_baseline,
    insert_gate_evaluation_record,
    insert_handover_gate,
    insert_slice_result_from_connection,
    load_current_lifecycle,
    load_execution_records,
    load_gate_evaluation_records,
    load_manual_evaluation_history_from_connection,
    load_slice_result_history_from_connection,
    open_database,
    persist_lifecycle_change,
    persist_lifecycle_initialization,
    read_transaction,
    verify_schema,
)
from relay_engine.persistence.errors import PersistenceIntegrityError
from relay_engine.project_slice import MutationMetadata, create_project, create_slice
from relay_engine.repository_baseline.models import (
    RepositoryRevisionKind,
    RepositoryRevisionSelector,
    ResolvedBaselineResult,
)

NOW = datetime(2026, 10, 3, 12, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
SOURCE_BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
GATE_ID: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"
DECISION_ID: DecisionId = "dec_018f47c1-7b2c-7abc-8def-123456789007"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002", host="github.com", path="owner/relay"
)
RESULT_SHA = "b" * 40
RESULT_ARTIFACT: ArtifactId = "art_018f47c1-7b2c-7abc-8def-123456789010"


class _BaselineResolver:
    def __init__(self, database: object) -> None:
        self.database = database
        self.decision_ids: tuple[DecisionId, ...] | None = None

    def resolve_and_persist_github_baseline(
        self,
        *,
        selection: object,
        selector: RepositoryRevisionSelector,
        baseline_id: BaselineId,
        decision_ids: tuple[DecisionId, ...],
        observed_at: datetime,
    ) -> ResolvedBaselineResult:
        del observed_at
        selection = cast(GitHubRepositoryAccessSelection, selection)
        project_id = selection.project_id
        repository = selection.repository
        self.decision_ids = decision_ids
        baseline = Baseline(
            id=baseline_id,
            project_id=project_id,
            commit=CommitRef(repository=repository, sha=RESULT_SHA),
            artifact_ids=(RESULT_ARTIFACT,),
            decision_ids=decision_ids,
        )
        insert_artifact(
            cast(object, self.database),
            Artifact(
                id=RESULT_ARTIFACT,
                artifact_type="DESIGN_RECORD",
                path="docs/result.md",
                commit=baseline.commit,
                content_digest=f"sha256:{'c' * 64}",
            ),
        )
        insert_baseline(cast(object, self.database), baseline)
        return ResolvedBaselineResult(
            project_id=project_id,
            repository=repository,
            selector=selector,
            commit=baseline.commit,
            baseline_id=baseline_id,
            artifact_ids=baseline.artifact_ids,
        )


def _gate(*, policy: HandoverPolicy = HandoverPolicy.AUTO) -> HandoverGate:
    return HandoverGate(
        gate_id=GATE_ID,
        revision=1,
        key="accept-result",
        slice_id=SLICE_ID,
        baseline_id=SOURCE_BASELINE_ID,
        source_phase=LifecyclePhase.EVALUATING,
        target_phase=LifecyclePhase.ACCEPTED,
        policy=policy,
    )


def _seed(
    path: Path, *, policy: HandoverPolicy = HandoverPolicy.AUTO, initial_observation: bool = False
):
    database = open_database(path, apply_migrations=True, migration_applied_at=NOW)
    project = Project(id=PROJECT_ID, name="Relay", primary_repository=REPOSITORY)
    slice_value = Slice(
        id=SLICE_ID,
        project_id=PROJECT_ID,
        title="Manual evaluation fixture",
        scope=ScopeSpec(in_scope=("record exact results",), out_of_scope=("run agents",)),
        acceptance_criteria=(
            AcceptanceCriterion(key="A01", statement="Human evaluation is durable.", required=True),
        ),
    )
    metadata = MutationMetadata(actor=ACTOR, occurred_at=NOW, reason="Create test fixture.")
    create_project(database, project, metadata)
    source = Baseline(
        id=SOURCE_BASELINE_ID,
        project_id=PROJECT_ID,
        commit=CommitRef(repository=REPOSITORY, sha="a" * 40),
        artifact_ids=(),
        decision_ids=(DECISION_ID,),
    )
    insert_baseline(database, source)
    create_slice(database, slice_value, metadata)
    lifecycle, event = initialize_lifecycle(
        SLICE_ID, new_id("evt_"), ACTOR, NOW, "Initialize evaluation fixture."
    )
    persist_lifecycle_initialization(database, lifecycle, event)
    for offset, phase in enumerate(
        (LifecyclePhase.READY, LifecyclePhase.IMPLEMENTING, LifecyclePhase.EVALUATING),
        start=1,
    ):
        lifecycle, phase_event = transition_phase(
            lifecycle,
            phase,
            new_id("evt_"),
            ACTOR,
            NOW + timedelta(seconds=offset),
            "Move fixture through the governed lifecycle model.",
        )
        persist_lifecycle_change(database, lifecycle.revision - 1, lifecycle, phase_event)
    gate = _gate(policy=policy)
    insert_handover_gate(database, gate)
    prior = None
    if initial_observation:
        context = HandoverContext(
            baseline_id=SOURCE_BASELINE_ID,
            governance_revision=1,
            lifecycle=lifecycle,
            change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
            risk_status=RiskStatus.CLEAR,
            toolchain_change_status=ToolchainChangeStatus.NONE,
        )
        from relay_engine.governance import evaluate_handover_gates

        prior = GateEvaluationRecord(
            id=new_id("geval_"),
            recorded_at=NOW + timedelta(seconds=9),
            gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
            context=context,
            evaluations=evaluate_handover_gates((gate,), context),
        )
        insert_gate_evaluation_record(database, prior)
    return database, lifecycle, gate, prior, source


def _attach(database: object, lifecycle: SliceLifecycle, resolver: _BaselineResolver) -> object:
    return attach_result(
        cast(object, database),
        SLICE_ID,
        repository_baseline_service=cast(object, resolver),
        selection=_selection(),
        selector=RepositoryRevisionSelector(
            kind=RepositoryRevisionKind.COMMIT_SHA, value=RESULT_SHA
        ),
        result_id=new_id("res_"),
        result_baseline_id=new_id("base_"),
        expected_lifecycle_revision=lifecycle.revision,
        expected_slice_definition_revision=1,
        expected_current_result_id=None,
        recorded_by=ACTOR,
        recorded_at=NOW + timedelta(seconds=10),
        reason="Attach the exact verified result commit.",
    )


def _selection() -> GitHubRepositoryAccessSelection:
    return GitHubRepositoryAccessSelection(
        project_id=PROJECT_ID,
        installation_id=100,
        github_repository_id=200,
        github_node_id="R_kgDOExample",
        repository=REPOSITORY,
        expected_state_revision=1,
    )


def _basis(database: object) -> HumanActionBasis:
    with read_transaction(cast(object, database)) as connection:
        snapshot = load_human_control_snapshot(connection, SLICE_ID)
        basis = basis_if_current(snapshot)
    assert basis is not None
    return basis


def _evaluation_inputs(
    database: object,
    *,
    evaluation_id: ManualEvaluationId,
    evaluated_at: datetime,
    expected_eval_id: ManualEvaluationId | None,
    expected_gate_id: GateEvaluationRecordId | None,
    outcome: EvaluationOutcome = EvaluationOutcome.ACCEPT,
):
    from relay_engine.persistence import load_slice_1_7_subject_from_connection

    with read_transaction(cast(object, database)) as connection:
        result, _current = load_slice_1_7_subject_from_connection(connection, SLICE_ID)
        assert result is not None
        gate = _gate()
        gate_refs = (GateRevisionRef(gate_id=gate.gate_id, gate_revision=gate.revision),)
    evidence_id: EvidenceId = new_id("evd_")
    evidence_time = evaluated_at - timedelta(seconds=1)
    return record_manual_evaluation(
        cast(object, database),
        SLICE_ID,
        evaluation_id=evaluation_id,
        evaluator=ACTOR,
        evaluated_at=evaluated_at,
        outcome=outcome,
        existing_evidence_ids=(),
        evidence_submissions=(
            EvaluationEvidenceSubmission(
                evidence_id=evidence_id,
                claim="The exact result commit was inspected.",
                recorded_at=evidence_time,
            ),
        ),
        quality_checks=(QualityCheckResult(key="tests", status=QualityCheckStatus.PASS),),
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
        findings=("The authored result satisfies its acceptance criteria.",),
        summary="Manual evaluation of the exact result commit.",
        expected_lifecycle_revision=3,
        expected_slice_definition_revision=1,
        expected_result_id=result.result_id,
        expected_current_evaluation_id=expected_eval_id,
        expected_latest_gate_evaluation_record_id=expected_gate_id,
        expected_gate_refs=gate_refs,
        successor_gate_evaluation_record_id=new_id("geval_"),
        successor_gate_evaluation_recorded_at=evaluated_at + timedelta(seconds=1),
    )


def test_v4_upgrade_and_fresh_schema_install_only_v5_slice_tables(tmp_path: Path) -> None:
    path = tmp_path / "v4-upgrade.sqlite"
    connection = sqlite3.connect(path, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    apply_migrations(connection, DEFAULT_MIGRATIONS[:4], applied_at=NOW)
    before = tuple(
        tuple(row)
        for row in connection.execute(
            "SELECT version, name, checksum FROM relay_schema_migrations ORDER BY version"
        )
    )
    apply_migrations(connection, DEFAULT_MIGRATIONS, applied_at=NOW + timedelta(seconds=1))
    verify_schema(connection)
    after = tuple(
        tuple(row)
        for row in connection.execute(
            "SELECT version, name, checksum FROM relay_schema_migrations ORDER BY version"
        )
    )
    assert after[:4] == before
    assert after[-1][0] == 5
    assert MANUAL_EVALUATION_MIGRATION.version == 5
    assert MANUAL_EVALUATION_MIGRATION.checksum == DEFAULT_MIGRATIONS[-1].checksum
    assert tuple(item.checksum for item in DEFAULT_MIGRATIONS[:4]) == (
        "sha256:00d78d5794e1196b7435a95679cab94cda4e2ea31742a0e6a2e63d4b58eae38e",
        "sha256:735dc501d65e5f3430bacd77503cca9ec6ca726986c786108b9319a9c1e52cb1",
        "sha256:0fc2760a2450787b238391ac17127d78c85df15c61424d35542b600e783c8c73",
        "sha256:f8e2da162ebec9ad73d69fb021c85e063c427ff9acc59a5bcb18ca343b493dbb",
    )
    assert tuple(
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN "
            "('slice_results', 'manual_evaluations') ORDER BY name"
        )
    ) == ("manual_evaluations", "slice_results")
    connection.close()

    fresh = open_database(
        tmp_path / "fresh-v5.sqlite", apply_migrations=True, migration_applied_at=NOW
    )
    try:
        assert (
            fresh.connection.execute("SELECT max(version) FROM relay_schema_migrations").fetchone()[
                0
            ]
            == 5
        )
        for name in (
            "slice_results_by_slice_sequence",
            "manual_evaluations_by_slice_result_sequence",
        ):
            assert fresh.connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?", (name,)
            ).fetchone()
        for name in (
            "slice_results_no_update",
            "slice_results_no_delete",
            "manual_evaluations_no_update",
            "manual_evaluations_no_delete",
        ):
            assert fresh.connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='trigger' AND name=?", (name,)
            ).fetchone()
    finally:
        fresh.close()


def test_v5_result_and_evaluation_tables_are_append_only(tmp_path: Path) -> None:
    database, _lifecycle, _gate_value, _prior, _source = _seed(tmp_path / "append-only.sqlite")
    result_id = new_id("res_")
    evaluation_id = new_id("eval_")
    try:
        database.connection.execute(
            "INSERT INTO slice_results(result_id, slice_id, source_baseline_id, "
            "result_baseline_id, lifecycle_revision, supersedes_result_id, payload_json) "
            "VALUES (?, ?, ?, ?, ?, NULL, '{}')",
            (result_id, SLICE_ID, SOURCE_BASELINE_ID, SOURCE_BASELINE_ID, 3),
        )
        database.connection.execute(
            "INSERT INTO manual_evaluations(evaluation_id, slice_id, result_id, "
            "result_baseline_id, lifecycle_revision, supersedes_evaluation_id, payload_json) "
            "VALUES (?, ?, ?, ?, ?, NULL, '{}')",
            (evaluation_id, SLICE_ID, result_id, SOURCE_BASELINE_ID, 3),
        )
        for table, identity_column, identity in (
            ("slice_results", "result_id", result_id),
            ("manual_evaluations", "evaluation_id", evaluation_id),
        ):
            with pytest.raises(sqlite3.IntegrityError):
                database.connection.execute(
                    f"UPDATE {table} SET payload_json = 'changed' WHERE {identity_column} = ?",
                    (identity,),
                )
            with pytest.raises(sqlite3.IntegrityError):
                database.connection.execute(
                    f"DELETE FROM {table} WHERE {identity_column} = ?", (identity,)
                )
    finally:
        database.close()


def test_result_supersession_rejects_forks_and_cycles(tmp_path: Path) -> None:
    database, _lifecycle, _gate_value, _prior, _source = _seed(tmp_path / "result-chain.sqlite")
    root_id = new_id("res_")
    child_id = new_id("res_")
    fork_id = new_id("res_")
    cycle_id = new_id("res_")
    try:
        root = SliceResultRecord(
            result_id=root_id,
            slice_id=SLICE_ID,
            slice_definition_revision=1,
            source_baseline_id=SOURCE_BASELINE_ID,
            result_baseline_id=SOURCE_BASELINE_ID,
            lifecycle_revision=3,
            recorded_by=ACTOR,
            recorded_at=NOW,
            reason="Root result record.",
        )
        child = root.model_copy(
            update={
                "result_id": child_id,
                "supersedes_result_id": root_id,
                "recorded_at": NOW + timedelta(seconds=1),
            }
        )
        with database.connection:
            insert_slice_result_from_connection(database.connection, root)
            insert_slice_result_from_connection(database.connection, child)
            fork = root.model_copy(
                update={
                    "result_id": fork_id,
                    "supersedes_result_id": root_id,
                    "recorded_at": NOW + timedelta(seconds=2),
                }
            )
            with pytest.raises(sqlite3.IntegrityError):
                insert_slice_result_from_connection(database.connection, fork)
            cycle = root.model_copy(
                update={
                    "result_id": cycle_id,
                    "supersedes_result_id": cycle_id,
                    "recorded_at": NOW + timedelta(seconds=3),
                }
            )
            insert_slice_result_from_connection(database.connection, cycle)
        with (
            read_transaction(database) as connection,
            pytest.raises(PersistenceIntegrityError, match="disconnected or cyclic"),
        ):
            load_slice_result_history_from_connection(connection, SLICE_ID)
    finally:
        database.close()


def test_result_and_evaluation_index_columns_must_match_typed_payload(tmp_path: Path) -> None:
    database, lifecycle, _gate_value, _prior, _source = _seed(tmp_path / "payload-index.sqlite")
    resolver = _BaselineResolver(database)
    try:
        result = _attach(database, lifecycle, resolver)
        _evaluation_inputs(
            database,
            evaluation_id=new_id("eval_"),
            evaluated_at=NOW + timedelta(seconds=12),
            expected_eval_id=None,
            expected_gate_id=None,
        )
        result_record = database.connection.execute(
            "SELECT lifecycle_revision FROM slice_results WHERE result_id = ?",
            (result.result_id,),
        ).fetchone()
        evaluation_record = database.connection.execute(
            "SELECT evaluation_id, lifecycle_revision FROM manual_evaluations WHERE slice_id = ?",
            (SLICE_ID,),
        ).fetchone()
        assert result_record is not None and evaluation_record is not None
        database.connection.execute("DROP TRIGGER slice_results_no_update")
        database.connection.execute("DROP TRIGGER manual_evaluations_no_update")
        database.connection.execute(
            "UPDATE slice_results SET lifecycle_revision = ? WHERE result_id = ?",
            (result_record[0] + 1, result.result_id),
        )
        with (
            read_transaction(database) as connection,
            pytest.raises(PersistenceIntegrityError, match="indexed column"),
        ):
            load_slice_result_history_from_connection(connection, SLICE_ID)
        database.connection.execute(
            "UPDATE slice_results SET lifecycle_revision = ? WHERE result_id = ?",
            (result_record[0], result.result_id),
        )
        database.connection.execute(
            "UPDATE manual_evaluations SET lifecycle_revision = ? WHERE evaluation_id = ?",
            (evaluation_record[1] + 1, evaluation_record[0]),
        )
        with (
            read_transaction(database) as connection,
            pytest.raises(PersistenceIntegrityError, match="indexed column"),
        ):
            load_manual_evaluation_history_from_connection(connection, SLICE_ID)
    finally:
        database.close()


def test_old_gate_contexts_may_keep_evaluation_outcome_without_new_subject(
    tmp_path: Path,
) -> None:
    database, lifecycle, _gate_value, _prior, _source = _seed(
        tmp_path / "historical-context.sqlite"
    )
    try:
        context = HandoverContext(
            baseline_id=SOURCE_BASELINE_ID,
            governance_revision=1,
            lifecycle=lifecycle,
            evaluation_outcome=EvaluationOutcome.ACCEPT,
            change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
            risk_status=RiskStatus.CLEAR,
            toolchain_change_status=ToolchainChangeStatus.NONE,
        )
        assert context.result_id is None
        assert context.manual_evaluation_id is None
        with pytest.raises(ValueError, match="present together"):
            HandoverContext(
                baseline_id=SOURCE_BASELINE_ID,
                governance_revision=1,
                lifecycle=lifecycle,
                evaluation_outcome=EvaluationOutcome.ACCEPT,
                result_id=new_id("res_"),
                change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
                risk_status=RiskStatus.CLEAR,
                toolchain_change_status=ToolchainChangeStatus.NONE,
            )
        with pytest.raises(ValueError, match="manual_evaluation_id requires"):
            HandoverContext(
                baseline_id=SOURCE_BASELINE_ID,
                governance_revision=1,
                lifecycle=lifecycle,
                result_id=new_id("res_"),
                result_baseline_id=SOURCE_BASELINE_ID,
                manual_evaluation_id=new_id("eval_"),
                change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
                risk_status=RiskStatus.CLEAR,
                toolchain_change_status=ToolchainChangeStatus.NONE,
            )
    finally:
        database.close()


def test_result_attachment_inherits_decisions_and_creates_no_evaluation(tmp_path: Path) -> None:
    database, lifecycle, _gate_value, prior, source = _seed(
        tmp_path / "attach-result.sqlite", initial_observation=True
    )
    resolver = _BaselineResolver(database)
    try:
        result = _attach(database, lifecycle, resolver)
        assert resolver.decision_ids == source.decision_ids
        assert result.source_baseline_id == source.id
        assert result.result_baseline_id != source.id
        assert load_gate_evaluation_records(database) == (prior,)
        with read_transaction(database) as connection:
            result_history = load_slice_result_history_from_connection(connection, SLICE_ID)
            evaluation_history = load_manual_evaluation_history_from_connection(
                connection, SLICE_ID
            )
        assert result_history == (result,)
        assert evaluation_history == ()
        assert result.lifecycle_revision == lifecycle.revision
    finally:
        database.close()


def test_pending_result_invalidates_gate_action_basis_until_authored_evaluation(
    tmp_path: Path,
) -> None:
    database, lifecycle, _gate_value, _prior, _source = _seed(
        tmp_path / "pending-basis.sqlite",
        policy=HandoverPolicy.HUMAN_APPROVAL,
        initial_observation=True,
    )
    resolver = _BaselineResolver(database)
    try:
        old_basis = _basis(database)
        _attach(database, lifecycle, resolver)
        with pytest.raises(HumanActionRequiresEvaluation):
            record_gate_approval(
                database,
                SLICE_ID,
                GATE_ID,
                old_basis,
                None,
                ACTOR,
                "Old form must not bypass the evaluation.",
                decision_id=new_id("hdec_"),
                occurred_at=NOW + timedelta(seconds=11),
                successor_evaluation_record_id=new_id("geval_"),
                successor_evaluation_recorded_at=NOW + timedelta(seconds=12),
            )
        assert (
            database.connection.execute("SELECT count(*) FROM human_decisions").fetchone()[0] == 0
        )
    finally:
        database.close()


def test_evaluation_human_approval_and_accepted_execution_are_causal(tmp_path: Path) -> None:
    database, lifecycle, _gate_value, _prior, _source = _seed(tmp_path / "accept-result.sqlite")
    resolver = _BaselineResolver(database)
    try:
        result = _attach(database, lifecycle, resolver)
        first_id: ManualEvaluationId = new_id("eval_")
        first = _evaluation_inputs(
            database,
            evaluation_id=first_id,
            evaluated_at=NOW + timedelta(seconds=12),
            expected_eval_id=None,
            expected_gate_id=None,
        )
        with pytest.raises(ManualEvaluationStale):
            record_manual_evaluation(
                database,
                SLICE_ID,
                evaluation_id=new_id("eval_"),
                evaluator=ACTOR,
                evaluated_at=NOW + timedelta(seconds=12),
                outcome=EvaluationOutcome.ACCEPT,
                existing_evidence_ids=(),
                evidence_submissions=(),
                quality_checks=(),
                change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
                risk_status=RiskStatus.CLEAR,
                toolchain_change_status=ToolchainChangeStatus.NONE,
                findings=(),
                summary="Stale form.",
                expected_lifecycle_revision=lifecycle.revision,
                expected_slice_definition_revision=1,
                expected_result_id=result.result_id,
                expected_current_evaluation_id=None,
                expected_latest_gate_evaluation_record_id=None,
                expected_gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
                successor_gate_evaluation_record_id=new_id("geval_"),
                successor_gate_evaluation_recorded_at=NOW + timedelta(seconds=13),
            )
        first_observation = load_gate_evaluation_records(database)[-1]
        assert first_observation.context.governance_revision == 1
        assert first_observation.context.result_id == result.result_id
        assert first_observation.context.manual_evaluation_id == first_id
        assert first_observation.context.available_artifact_ids == (RESULT_ARTIFACT,)
        assert first_observation.context.evaluation_outcome is EvaluationOutcome.ACCEPT
        assert (
            next(item for item in first_observation.evaluations if item.gate_id == GATE_ID).light
            is TrafficLight.GREEN
        )

        first_approval_id = new_id("hdec_")
        approved = record_technical_acceptance(
            database,
            SLICE_ID,
            GATE_ID,
            _basis(database),
            expected_result_id=result.result_id,
            expected_manual_evaluation_id=first_id,
            expected_current_approval_decision_id=None,
            actor=ACTOR,
            reason="Human technical review approves this exact result.",
            decision_id=first_approval_id,
            occurred_at=NOW + timedelta(seconds=14),
            successor_gate_evaluation_record_id=new_id("geval_"),
            successor_gate_evaluation_recorded_at=NOW + timedelta(seconds=15),
        )
        assert approved.context.human_decisions[0].decision is HumanApprovalValue.APPROVE

        second_id: ManualEvaluationId = new_id("eval_")
        second = record_manual_evaluation(
            database,
            SLICE_ID,
            evaluation_id=second_id,
            evaluator=ACTOR,
            evaluated_at=NOW + timedelta(seconds=17),
            outcome=EvaluationOutcome.ACCEPT,
            existing_evidence_ids=first.context.available_evidence_ids,
            evidence_submissions=(),
            quality_checks=(QualityCheckResult(key="tests", status=QualityCheckStatus.PASS),),
            change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
            risk_status=RiskStatus.CLEAR,
            toolchain_change_status=ToolchainChangeStatus.NONE,
            findings=("Reconsidered against the same exact result.",),
            summary="A superseding authored evaluation.",
            expected_lifecycle_revision=lifecycle.revision,
            expected_slice_definition_revision=1,
            expected_result_id=result.result_id,
            expected_current_evaluation_id=first_id,
            expected_latest_gate_evaluation_record_id=approved.id,
            expected_gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
            successor_gate_evaluation_record_id=new_id("geval_"),
            successor_gate_evaluation_recorded_at=NOW + timedelta(seconds=18),
        )
        assert second.context.governance_revision == 2
        assert second.context.manual_evaluation_id == second_id

        current_approval = first_approval_id
        current_basis = _basis(database)
        second_approval = record_technical_acceptance(
            database,
            SLICE_ID,
            GATE_ID,
            current_basis,
            expected_result_id=result.result_id,
            expected_manual_evaluation_id=second_id,
            expected_current_approval_decision_id=current_approval,
            actor=ACTOR,
            reason="Reaffirm technical approval for the superseding evaluation.",
            decision_id=new_id("hdec_"),
            occurred_at=NOW + timedelta(seconds=19),
            successor_gate_evaluation_record_id=new_id("geval_"),
            successor_gate_evaluation_recorded_at=NOW + timedelta(seconds=20),
        )
        assert second_approval.context.governance_revision == 2
        assert second_approval.context.human_decisions[0].decision_id != current_approval

        promotion_basis = _basis(database)
        accepted = promote_accepted_result(
            database,
            SLICE_ID,
            GATE_ID,
            promotion_basis,
            expected_result_id=result.result_id,
            expected_manual_evaluation_id=second_id,
            expected_current_approval_decision_id=second_approval.context.human_decisions[
                0
            ].decision_id,
            actor=ACTOR,
            reason="Execute the exact green ACCEPTED gate.",
            gate_evaluation_record_id=new_id("geval_"),
            gate_evaluation_recorded_at=NOW + timedelta(seconds=21),
            execution_id=new_id("exec_"),
            event_id=new_id("evt_"),
            occurred_at=NOW + timedelta(seconds=22),
        )
        assert accepted.result_id == result.result_id
        assert accepted.manual_evaluation_id == second_id
        assert accepted.commit == RESULT_SHA
        accepted_lifecycle = load_current_lifecycle(database, SLICE_ID)
        assert accepted_lifecycle is not None
        assert accepted_lifecycle.phase is LifecyclePhase.ACCEPTED
        executions = load_execution_records(database)
        assert len(executions) == 1
        assert (
            load_gate_evaluation_records(database)[-1].id == executions[0].gate_evaluation_record_id
        )
        assert load_gate_evaluation_records(database)[-1].context.manual_evaluation_id == second_id
        with pytest.raises(ManualEvaluationConflict):
            promote_accepted_result(
                database,
                SLICE_ID,
                GATE_ID,
                promotion_basis,
                expected_result_id=result.result_id,
                expected_manual_evaluation_id=second_id,
                expected_current_approval_decision_id=second_approval.context.human_decisions[
                    0
                ].decision_id,
                actor=ACTOR,
                reason="A retry with the old basis must not re-execute.",
                gate_evaluation_record_id=new_id("geval_"),
                gate_evaluation_recorded_at=NOW + timedelta(seconds=23),
                execution_id=new_id("exec_"),
                event_id=new_id("evt_"),
                occurred_at=NOW + timedelta(seconds=24),
            )
    finally:
        database.close()


def test_evaluation_transaction_rolls_back_evidence_and_records_on_late_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database, lifecycle, _gate_value, _prior, _source = _seed(
        tmp_path / "evaluation-rollback.sqlite"
    )
    resolver = _BaselineResolver(database)
    try:
        result = _attach(database, lifecycle, resolver)

        def fail_after_appends(*_args: object, **_kwargs: object) -> None:
            raise RuntimeError("simulated successor evaluation failure")

        monkeypatch.setattr(
            manual_evaluation_service, "record_successor_observation", fail_after_appends
        )
        with pytest.raises(RuntimeError, match="simulated"):
            _evaluation_inputs(
                database,
                evaluation_id=new_id("eval_"),
                evaluated_at=NOW + timedelta(seconds=12),
                expected_eval_id=None,
                expected_gate_id=None,
            )
        assert database.connection.execute("SELECT count(*) FROM evidence").fetchone()[0] == 0
        assert (
            database.connection.execute("SELECT count(*) FROM manual_evaluations").fetchone()[0]
            == 0
        )
        assert (
            database.connection.execute("SELECT count(*) FROM gate_evaluation_records").fetchone()[
                0
            ]
            == 0
        )
        with read_transaction(database) as connection:
            assert (
                load_slice_result_history_from_connection(connection, SLICE_ID)[0].result_id
                == result.result_id
            )
    finally:
        database.close()


def _http_request(app: object, path: str, body: dict[str, str]) -> httpx.Response:
    async def perform() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=cast(object, app)),
            base_url="http://relay.test",
        ) as client:
            return await client.post(
                path,
                content=urlencode(body),
                headers={"content-type": "application/x-www-form-urlencoded"},
                follow_redirects=False,
            )

    return asyncio.run(perform())


def test_slice_17_http_routes_require_csrf_before_any_write(tmp_path: Path) -> None:
    database, _lifecycle, _gate_value, _prior, _source = _seed(tmp_path / "csrf.sqlite")
    app = create_app(database.path, actor=ACTOR, manual_evaluator_actor=ACTOR)
    paths = tuple(
        f"/projects/{PROJECT_ID}/slices/{SLICE_ID}/actions/{action}"
        for action in (
            "attach-result",
            "evaluate",
            "technical-accept",
            "technical-reject",
            "promote-accepted",
        )
    )
    tables = (
        "slice_results",
        "manual_evaluations",
        "evidence",
        "human_decisions",
        "executions",
    )
    before = tuple(
        database.connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in tables
    )
    try:
        for path in paths:
            response = _http_request(app, path, {"reason": "No CSRF token."})
            assert response.status_code == 403
        after = tuple(
            database.connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in tables
        )
        assert after == before
    finally:
        database.close()


def test_slice_17_http_commands_use_303_and_preserve_governed_order(tmp_path: Path) -> None:
    database, _lifecycle, _gate_value, _prior, _source = _seed(
        tmp_path / "slice-17-http-flow.sqlite", policy=HandoverPolicy.AUTO
    )
    app = create_app(
        database.path,
        actor=ACTOR,
        manual_evaluator_actor=ACTOR,
        repository_baseline_service_factory=lambda request_database: _BaselineResolver(
            request_database
        ),
        repository_access_selection_factory=lambda _request_database, _project_id: _selection(),
    )
    prefix = f"/projects/{PROJECT_ID}/slices/{SLICE_ID}/actions"
    csrf = app.state.csrf_token

    def action_basis_fields() -> dict[str, str]:
        detail = slice_detail(database, PROJECT_ID, SLICE_ID)
        basis = detail.manual_evaluation.action_basis
        assert basis is not None
        return {
            "expected_lifecycle_revision": str(basis.lifecycle_revision),
            "expected_slice_definition_revision": str(basis.slice_definition_revision),
            "expected_current_result_id": basis.current_result_id or "",
            "expected_current_evaluation_id": basis.current_manual_evaluation_id or "",
            "expected_latest_gate_evaluation_record_id": (
                basis.latest_gate_evaluation_record_id or ""
            ),
            "expected_gate_refs": json.dumps(
                [reference.model_dump(mode="json") for reference in basis.gate_refs]
            ),
        }

    def human_basis_and_approval() -> tuple[str, str]:
        detail = slice_detail(database, PROJECT_ID, SLICE_ID)
        basis = detail.human_actions.basis
        assert basis is not None
        approval_id = (
            ""
            if not detail.human_actions.current_approval_decisions
            else detail.human_actions.current_approval_decisions[0].decision_id
        )
        return basis.model_dump_json(), approval_id

    try:
        attach_form = {
            **action_basis_fields(),
            "csrf_token": csrf,
            "revision_kind": "COMMIT_SHA",
            "revision_value": RESULT_SHA,
            "reason": "Attach the exact verified commit through the board.",
        }
        attached = _http_request(app, f"{prefix}/attach-result", attach_form)
        assert attached.status_code == 303
        assert attached.headers["location"] == f"/projects/{PROJECT_ID}/slices/{SLICE_ID}"

        detail = slice_detail(database, PROJECT_ID, SLICE_ID)
        current_result = detail.manual_evaluation.current_result
        assert current_result is not None
        evaluate_form = {
            **action_basis_fields(),
            "csrf_token": csrf,
            "outcome": "ACCEPT",
            "evidence_claims": "Inspected exact commit and matching repository snapshot.",
            "existing_evidence_ids": "",
            "quality_checks": "tests=PASS",
            "change_surface_status": "WITHIN_DECLARED",
            "risk_status": "CLEAR",
            "toolchain_change_status": "NONE",
            "findings": "The authored result matches the accepted scope.",
            "summary": "Manual evaluation approves the exact result.",
        }
        evaluated = _http_request(app, f"{prefix}/evaluate", evaluate_form)
        assert evaluated.status_code == 303

        detail = slice_detail(database, PROJECT_ID, SLICE_ID)
        current_result = detail.manual_evaluation.current_result
        current_evaluation = detail.manual_evaluation.current_evaluation
        assert current_result is not None and current_evaluation is not None
        human_basis, current_approval_id = human_basis_and_approval()
        technical_form = {
            "csrf_token": csrf,
            "basis": human_basis,
            "expected_result_id": current_result.result_id,
            "expected_manual_evaluation_id": current_evaluation.evaluation_id,
            "gate_id": GATE_ID,
            "gate_revision": "1",
            "expected_current_approval_decision_id": current_approval_id,
            "reason": "Human rejects pending further review.",
        }
        rejected = _http_request(app, f"{prefix}/technical-reject", technical_form)
        assert rejected.status_code == 303
        rejected_detail = slice_detail(database, PROJECT_ID, SLICE_ID)
        rejected_gate = next(
            gate for gate in rejected_detail.outgoing_gates if gate.gate_id == GATE_ID
        )
        assert rejected_gate.evaluation_light is TrafficLight.RED

        human_basis, reject_id = human_basis_and_approval()
        technical_form.update(
            {
                "basis": human_basis,
                "expected_current_approval_decision_id": reject_id,
                "reason": "Human approves after completing the review.",
            }
        )
        approved = _http_request(app, f"{prefix}/technical-accept", technical_form)
        assert approved.status_code == 303

        detail = slice_detail(database, PROJECT_ID, SLICE_ID)
        basis = detail.human_actions.basis
        assert basis is not None
        approval_id = detail.human_actions.current_approval_decisions[0].decision_id
        promoted = _http_request(
            app,
            f"{prefix}/promote-accepted",
            {
                "csrf_token": csrf,
                "basis": basis.model_dump_json(),
                "expected_result_id": current_result.result_id,
                "expected_manual_evaluation_id": current_evaluation.evaluation_id,
                "expected_current_approval_decision_id": approval_id,
                "gate_id": GATE_ID,
                "gate_revision": "1",
                "reason": "Execute the exact current GREEN ACCEPTED gate.",
            },
        )
        assert promoted.status_code == 303
        assert promoted.headers["location"] == f"/projects/{PROJECT_ID}/slices/{SLICE_ID}"
    finally:
        database.close()
