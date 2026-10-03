"""Immutable presentation contract tests for board projection values."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from relay_engine.board.models import (
    BoardLane,
    DependencyProjection,
    EvaluationBasisStatus,
    GateProjection,
    ProjectBoard,
    SliceCard,
)
from relay_engine.domain.ids import BaselineId, HandoverGateId, ProjectId, SliceId
from relay_engine.domain.models import Project
from relay_engine.domain.references import RepositoryRef
from relay_engine.governance.models import HandoverPolicy
from relay_engine.lifecycle.models import (
    Blockage,
    BlockageStatus,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
)

NOW = datetime(2026, 10, 2, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
BASELINE_ID: BaselineId = "base_018f47c1-7b2c-7abc-8def-123456789003"
GATE_ID: HandoverGateId = "gate_018f47c1-7b2c-7abc-8def-123456789020"


def _project() -> Project:
    return Project(
        id=PROJECT_ID,
        name="Relay",
        primary_repository=RepositoryRef(
            id="repo_018f47c1-7b2c-7abc-8def-123456789002",
            host="github.com",
            path="owner/relay",
        ),
    )


def _lifecycle(phase: LifecyclePhase) -> SliceLifecycle:
    return SliceLifecycle(
        slice_id=SLICE_ID,
        phase=phase,
        validity=LifecycleValidity.CURRENT,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=1,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )


def _ready_card() -> SliceCard:
    gate = GateProjection(
        gate_id=GATE_ID,
        gate_revision=1,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.AUTO,
        hard_stop=False,
        authorization_required=True,
        baseline_id=BASELINE_ID,
        evaluation_light=None,
        evaluation_reasons=(),
        evaluation_basis_status=EvaluationBasisStatus.NOT_EVALUATED,
    )
    return SliceCard(
        slice_id=SLICE_ID,
        title="Ready but not authorized",
        definition_revision=1,
        parent_slice_id=None,
        dependency_ids=(),
        lane=BoardLane.READY,
        lifecycle=_lifecycle(LifecyclePhase.READY),
        dependencies=(),
        outgoing_gates=(gate,),
        latest_evaluation_record_id=None,
        latest_evaluation_recorded_at=None,
        evaluation_basis_status=EvaluationBasisStatus.NOT_EVALUATED,
    )


def test_ready_lane_preserves_lifecycle_and_does_not_add_slice_authority() -> None:
    card = _ready_card()
    assert card.lane is BoardLane.READY
    assert card.lifecycle is not None and card.lifecycle.phase is LifecyclePhase.READY
    assert card.outgoing_gates[0].authorization_required is True
    assert card.outgoing_gates[0].evaluation_light is None
    assert "traffic_light" not in SliceCard.model_fields
    with pytest.raises(ValidationError):
        SliceCard.model_validate({**card.model_dump(), "authorized": True})


def test_projection_models_are_immutable_extra_forbid_and_lane_ordered() -> None:
    card = _ready_card()
    project = _project()
    board = ProjectBoard(
        project=project,
        project_definition_revision=1,
        lanes=tuple(BoardLane),
        cards=(card,),
    )
    assert board.cards[0] == card
    with pytest.raises(ValidationError):
        board.project = project.model_copy(update={"name": "Changed"})  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ProjectBoard(
            project=project,
            project_definition_revision=1,
            lanes=tuple(reversed(tuple(BoardLane))),
            cards=(card,),
        )
    with pytest.raises(ValidationError):
        DependencyProjection(
            slice_id=SLICE_ID,
            title=None,
            lifecycle_phase=None,
            lifecycle_validity=None,
            invented_blocker=True,
        )
