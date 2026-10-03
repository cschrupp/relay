"""HTML escaping, observational wording, and accessibility presentation tests."""

from datetime import UTC, datetime

from relay_engine.board.models import (
    BoardLane,
    DependencyProjection,
    EvaluationBasisStatus,
    GateProjection,
    ProjectBoard,
    SliceCard,
    SliceDetail,
)
from relay_engine.board.render import (
    render_project_board,
    render_project_index,
    render_slice_detail,
)
from relay_engine.domain.ids import BaselineId, HandoverGateId, ProjectId, SliceId
from relay_engine.domain.models import (
    AcceptanceCriterion,
    Project,
    ScopeSpec,
    Slice,
)
from relay_engine.domain.references import (
    ActorKind,
    ActorRef,
    RepositoryRef,
)
from relay_engine.governance.models import (
    ChangeSurfaceStatus,
    GateEvaluation,
    GateReason,
    GateReasonCode,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    RiskStatus,
    ToolchainChangeStatus,
    TrafficLight,
)
from relay_engine.lifecycle.models import (
    Blockage,
    BlockageStatus,
    BlockReason,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
)
from relay_engine.persistence.records import GateEvaluationRecord
from relay_engine.project_slice.models import SliceDefinitionSnapshot

NOW = datetime(2026, 10, 2, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
GATE_ID: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="owner/relay",
)


def _fixture() -> tuple[ProjectBoard, SliceDetail]:
    project = Project(
        id=PROJECT_ID,
        name="<script>project()</script>",
        primary_repository=REPOSITORY,
    )
    slice_value = Slice(
        id=SLICE_ID,
        project_id=PROJECT_ID,
        title="<img src=x onerror=alert(1)>",
        scope=ScopeSpec(
            in_scope=("<script>scope()</script>",),
            out_of_scope=("<b>not HTML</b>",),
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                key="A01",
                statement="<svg onload=alert(1)>",
                required=True,
            ),
        ),
    )
    lifecycle = SliceLifecycle(
        slice_id=SLICE_ID,
        phase=LifecyclePhase.READY,
        validity=LifecycleValidity.STALE,
        blockage=Blockage(
            status=BlockageStatus.BLOCKED,
            reasons=(BlockReason(code="WAITING", summary="<script>blocker()</script>"),),
        ),
        revision=4,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    gate = HandoverGate(
        gate_id=GATE_ID,
        revision=1,
        key="implement",
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        source_phase=LifecyclePhase.READY,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.AUTO,
        authorization_required=True,
    )
    context = HandoverContext(
        baseline_id=BASELINE_ID,
        governance_revision=2,
        lifecycle=lifecycle,
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
    )
    recorded_evaluation = GateEvaluation(
        gate_id=GATE_ID,
        gate_revision=1,
        slice_id=SLICE_ID,
        baseline_id=BASELINE_ID,
        lifecycle_revision=4,
        governance_revision=2,
        target_phase=LifecyclePhase.IMPLEMENTING,
        light=TrafficLight.RED,
        reasons=(GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
    )
    record = GateEvaluationRecord(
        id="geval_018f47c1-7b2c-7abc-8def-123456789030",
        recorded_at=NOW,
        gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
        context=context,
        evaluations=(recorded_evaluation,),
    )
    dependency = DependencyProjection(
        slice_id=SLICE_ID,
        title="<b>dependency</b>",
        lifecycle_phase=LifecyclePhase.READY,
        lifecycle_validity=LifecycleValidity.STALE,
    )
    gate_projection = GateProjection(
        gate_id=GATE_ID,
        gate_revision=1,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.AUTO,
        hard_stop=False,
        authorization_required=True,
        baseline_id=BASELINE_ID,
        evaluation_light=None,
        evaluation_reasons=(),
        evaluation_basis_status=EvaluationBasisStatus.STALE_DURABLE_BASIS,
    )
    card = SliceCard(
        slice_id=SLICE_ID,
        title=slice_value.title,
        definition_revision=1,
        parent_slice_id=None,
        dependency_ids=(SLICE_ID,),
        lane=BoardLane.READY,
        lifecycle=lifecycle,
        dependencies=(dependency,),
        outgoing_gates=(gate_projection,),
        latest_evaluation_record_id=record.id,
        latest_evaluation_recorded_at=record.recorded_at,
        evaluation_basis_status=EvaluationBasisStatus.STALE_DURABLE_BASIS,
    )
    board = ProjectBoard(
        project=project,
        project_definition_revision=2,
        lanes=tuple(BoardLane),
        cards=(card,),
    )
    detail = SliceDetail(
        project=project,
        project_definition_revision=2,
        slice_definition=SliceDefinitionSnapshot(value=slice_value, definition_revision=1),
        lifecycle=lifecycle,
        parent=None,
        children=(),
        dependencies=(dependency,),
        outgoing_gate_definitions=(gate,),
        outgoing_gates=(gate_projection,),
        latest_evaluation_observation=record,
        evaluation_basis_status=EvaluationBasisStatus.STALE_DURABLE_BASIS,
        baseline=None,
        evaluation_baseline=None,
        relevant_execution_records=(),
    )
    return board, detail


def test_project_board_escapes_text_shows_textual_status_and_hides_stale_light() -> None:
    board, _ = _fixture()
    html = render_project_board(board)
    assert "<script>" not in html
    assert "<img src=x" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "&lt;script&gt;project()&lt;/script&gt;" in html
    assert "Lifecycle: <strong>READY</strong>" in html
    assert "Lifecycle validity: STALE" in html
    assert "<strong>BLOCKED</strong>" in html
    assert "Evaluation: stale durable basis" in html
    assert "Latest recorded evaluation on current durable basis: RED" not in html
    assert "Recorded reason counts" not in html
    assert ":focus-visible" in html
    assert "<main>" in html and "<section" in html


def test_matching_gate_light_is_observational_text_and_color() -> None:
    board, detail = _fixture()
    gate = detail.outgoing_gates[0].model_copy(
        update={
            "evaluation_basis_status": EvaluationBasisStatus.MATCHING_DURABLE_BASIS,
            "evaluation_light": TrafficLight.RED,
            "evaluation_reasons": (GateReason.for_code(GateReasonCode.EVALUATION_REQUIRED),),
        }
    )
    card = board.cards[0].model_copy(
        update={
            "evaluation_basis_status": EvaluationBasisStatus.MATCHING_DURABLE_BASIS,
            "outgoing_gates": (gate,),
        }
    )
    matching_board = board.model_copy(update={"cards": (card,)})
    html = render_project_board(matching_board)
    assert 'class="gate-light red"' in html
    assert "Latest recorded evaluation on current durable basis: <strong>RED</strong>" in html
    assert "Recorded reason counts: 1 blocking; 0 human action." in html


def test_slice_detail_shows_escaped_older_evidence_and_typed_context() -> None:
    _, detail = _fixture()
    html = render_slice_detail(detail)
    assert "<script>scope()" not in html
    assert "&lt;script&gt;scope()&lt;/script&gt;" in html
    assert "&lt;svg onload=alert(1)&gt;" in html
    assert "Older evaluation evidence; stored lights are historical." in html
    assert "<strong>RED</strong>" not in html
    assert "Full recorded HandoverContext" in html
    assert "&quot;baseline_id&quot;" in html
    assert "Latest recorded evaluation on current durable basis" not in html
    assert "READY is a phase and does not grant execution authorization" in html


def test_project_index_escapes_project_data_and_search_is_escaped() -> None:
    board, _ = _fixture()
    from relay_engine.board.models import BoardProjection, ProjectSummary

    index = render_project_index(
        BoardProjection(
            projects=(
                ProjectSummary(
                    project=board.project,
                    definition_revision=2,
                    slice_count=1,
                ),
            )
        )
    )
    assert "<script>project()" not in index
    assert "&lt;script&gt;project()&lt;/script&gt;" in index
    filtered = render_project_board(board, query='" autofocus onfocus="alert(1)')
    assert 'value="&quot; autofocus onfocus=&quot;alert(1)"' in filtered
    assert 'value="" autofocus' not in filtered
