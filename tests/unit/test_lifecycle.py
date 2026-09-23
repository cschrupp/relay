"""Contract tests for the deterministic slice lifecycle."""

from datetime import UTC, datetime, timedelta, timezone
from inspect import signature
from uuid import UUID

import pytest
from pydantic import BaseModel, ValidationError

from relay_engine.domain import EventId, SliceId, new_id
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.lifecycle import (
    Blockage,
    BlockageChanged,
    BlockageStatus,
    BlockReason,
    InvalidLifecycleOperation,
    InvalidPhaseTransition,
    LifecycleError,
    LifecycleInitialized,
    LifecyclePhase,
    LifecycleReplayError,
    LifecycleValidity,
    PhaseChanged,
    SliceLifecycle,
    ValidityChanged,
    clear_blockage,
    initialize_lifecycle,
    mark_stale,
    replay_lifecycle,
    revalidate,
    set_blocked,
    transition_phase,
)

SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789006"
OTHER_SLICE_ID: SliceId = "slc_018f47c1-7b2c-7abc-8def-123456789009"
ACTOR = ActorRef(
    id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN, display_name="Reviewer"
)
T0 = datetime(2026, 9, 23, 12, tzinfo=UTC)


def event_id(number: int) -> EventId:
    return f"evt_018f47c1-7b2c-7abc-8def-{number:012x}"  # type: ignore[return-value]


def reason(
    code: str = "CONTRACT_CONFLICT", summary: str = "A required contract is unresolved."
) -> BlockReason:
    return BlockReason(code=code, summary=summary)


def initial() -> tuple[SliceLifecycle, LifecycleInitialized]:
    return initialize_lifecycle(SLICE_ID, event_id(1), ACTOR, T0, "Open the slice lifecycle.")


def step(
    state: SliceLifecycle,
    phase: LifecyclePhase,
    number: int,
    *,
    successor: SliceId | None = None,
    at: datetime | None = None,
) -> tuple[SliceLifecycle, PhaseChanged]:
    return transition_phase(
        state,
        phase,
        event_id(number),
        ACTOR,
        T0 + timedelta(seconds=number) if at is None else at,
        f"Move to {phase.value}.",
        successor,
    )


def snapshot(
    phase: LifecyclePhase,
    *,
    validity: LifecycleValidity = LifecycleValidity.CURRENT,
    blockage: Blockage | None = None,
    successor: SliceId | None = None,
) -> SliceLifecycle:
    return SliceLifecycle(
        slice_id=SLICE_ID,
        phase=phase,
        validity=validity,
        blockage=blockage or Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=0,
        updated_at=T0,
        superseded_by_slice_id=successor,
    )


def test_ready_does_not_mean_authorized() -> None:
    assert LifecyclePhase.READY.value == "READY"
    assert set(SliceLifecycle.model_fields) == {
        "schema_version",
        "slice_id",
        "phase",
        "validity",
        "blockage",
        "revision",
        "updated_at",
        "superseded_by_slice_id",
    }
    assert not {"AUTHORIZED", "BLOCKED", "STALE", "HARD_STOP"} & {
        phase.value for phase in LifecyclePhase
    }


def test_event_identifier_uses_explicit_accepted_uuidv7_mechanism() -> None:
    generated = new_id("evt_")
    prefix, value = generated.split("_", maxsplit=1)
    assert prefix == "evt"
    assert UUID(value).version == 7
    with pytest.raises(ValueError, match="unsupported domain identifier prefix"):
        new_id("bad_明")  # type: ignore[arg-type]


def test_models_are_immutable_versioned_extra_forbid_and_json_serializable() -> None:
    state, initialized = initial()
    state2, changed = step(state, LifecyclePhase.READY, 2)
    blocked, blockage_event = set_blocked(
        state2, (reason(),), event_id(3), ACTOR, T0 + timedelta(seconds=3), "Record a blocker."
    )
    stale, validity_event = mark_stale(
        blocked, event_id(4), ACTOR, T0 + timedelta(seconds=4), "Upstream authority changed."
    )

    public_models: tuple[BaseModel, ...] = (
        state,
        initialized,
        changed,
        blockage_event,
        validity_event,
        reason(),
        Blockage(status=BlockageStatus.BLOCKED, reasons=(reason(),)),
        stale,
    )
    for model in public_models:
        model_type = type(model)
        assert model.model_config["frozen"] is True
        assert model.model_config["extra"] == "forbid"
        assert model.model_dump(mode="json")["schema_version"] == 1
        assert model_type.model_json_schema()["properties"]["schema_version"]["const"] == 1
        assert model_type.model_validate_json(model.model_dump_json()) == model

    with pytest.raises(ValidationError):
        state.phase = LifecyclePhase.CANCELLED
    with pytest.raises(ValidationError):
        SliceLifecycle.model_validate({**state.model_dump(), "unauthorized": True})

    with pytest.raises(ValidationError, match="resulting_revision zero"):
        LifecycleInitialized(
            event_id=event_id(88),
            slice_id=SLICE_ID,
            actor=ACTOR,
            occurred_at=T0,
            reason="Initialization revision is fixed.",
            resulting_revision=1,
        )


@pytest.mark.parametrize(
    ("phase", "validity", "blockage", "successor"),
    [
        (LifecyclePhase.PROPOSED, LifecycleValidity.CURRENT, BlockageStatus.BLOCKED, None),
        (LifecyclePhase.ACCEPTED, LifecycleValidity.CURRENT, BlockageStatus.BLOCKED, None),
        (LifecyclePhase.CANCELLED, LifecycleValidity.CURRENT, BlockageStatus.BLOCKED, None),
        (LifecyclePhase.SUPERSEDED, LifecycleValidity.CURRENT, BlockageStatus.CLEAR, None),
        (LifecyclePhase.READY, LifecycleValidity.CURRENT, BlockageStatus.CLEAR, OTHER_SLICE_ID),
        (LifecyclePhase.SUPERSEDED, LifecycleValidity.CURRENT, BlockageStatus.CLEAR, SLICE_ID),
    ],
)
def test_snapshot_rejects_structural_contradictions(
    phase: LifecyclePhase,
    validity: LifecycleValidity,
    blockage: BlockageStatus,
    successor: SliceId | None,
) -> None:
    reasons = (reason(),) if blockage is BlockageStatus.BLOCKED else ()
    with pytest.raises(ValidationError):
        SliceLifecycle(
            slice_id=SLICE_ID,
            phase=phase,
            validity=validity,
            blockage=Blockage(status=blockage, reasons=reasons),
            revision=0,
            updated_at=T0,
            superseded_by_slice_id=successor,
        )


def test_timestamp_values_are_aware_and_normalized_to_utc() -> None:
    offset = timezone(timedelta(hours=-4))
    state = snapshot(LifecyclePhase.READY)
    shifted = state.model_copy(update={"updated_at": T0.astimezone(offset)})
    # Revalidation at the serialized boundary applies the same UTC rule.
    normalized = SliceLifecycle.model_validate_json(shifted.model_dump_json())
    assert normalized.updated_at == T0

    with pytest.raises(ValidationError, match="timezone-aware"):
        SliceLifecycle(
            slice_id=SLICE_ID,
            phase=LifecyclePhase.READY,
            validity=LifecycleValidity.CURRENT,
            blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
            revision=0,
            updated_at=datetime(2026, 9, 23),
            superseded_by_slice_id=None,
        )


@pytest.mark.parametrize(
    ("code", "summary"),
    [("lowercase", "Reason"), ("BAD-CODE", "Reason"), ("BAD CODE", "Reason"), ("OK", "  ")],
)
def test_block_reason_rejects_invalid_code_or_blank_summary(code: str, summary: str) -> None:
    with pytest.raises(ValidationError):
        BlockReason(code=code, summary=summary)


def test_blockage_requires_reasons_for_blocked_and_unique_ordered_values() -> None:
    with pytest.raises(ValidationError):
        Blockage(status=BlockageStatus.BLOCKED, reasons=())
    with pytest.raises(ValidationError):
        Blockage(status=BlockageStatus.CLEAR, reasons=(reason(),))
    with pytest.raises(ValidationError):
        Blockage(status=BlockageStatus.BLOCKED, reasons=(reason(), reason()))

    first, second = reason("FIRST", "First issue."), reason("SECOND", "Second issue.")
    blockage = Blockage(status=BlockageStatus.BLOCKED, reasons=(first, second))
    assert blockage.reasons == (first, second)
    assert blockage != Blockage(status=BlockageStatus.BLOCKED, reasons=(second, first))


_MATRIX: dict[LifecyclePhase, set[LifecyclePhase]] = {
    LifecyclePhase.PROPOSED: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.READY,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.DEFINING: {
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.READY,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.RESEARCHING: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.READY,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.DESIGNING: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.READY,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.CONTRACTING: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.READY,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.PLANNING: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.READY,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.READY: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.IMPLEMENTING,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.IMPLEMENTING: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.EVALUATING,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.EVALUATING: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.REWORK,
        LifecyclePhase.ACCEPTED,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.REWORK: {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.EVALUATING,
        LifecyclePhase.CANCELLED,
    },
    LifecyclePhase.ACCEPTED: {LifecyclePhase.SUPERSEDED},
    LifecyclePhase.SUPERSEDED: set(),
    LifecyclePhase.CANCELLED: set(),
}


@pytest.mark.parametrize("source", list(LifecyclePhase))
@pytest.mark.parametrize("target", list(LifecyclePhase))
def test_every_phase_pair_matches_the_explicit_matrix(
    source: LifecyclePhase, target: LifecyclePhase
) -> None:
    state = snapshot(
        source, successor=OTHER_SLICE_ID if source is LifecyclePhase.SUPERSEDED else None
    )
    if target in _MATRIX[source]:
        successor = OTHER_SLICE_ID if target is LifecyclePhase.SUPERSEDED else None
        updated, event = step(state, target, 2, successor=successor)
        assert updated.phase is target
        assert event.from_phase is source
    elif target is source:
        with pytest.raises(InvalidLifecycleOperation):
            step(state, target, 2)
    else:
        with pytest.raises(InvalidPhaseTransition):
            step(state, target, 2)


def _happy_path(targets: tuple[LifecyclePhase, ...]) -> tuple[SliceLifecycle, tuple]:
    state, init_event = initial()
    events = [init_event]
    for number, target in enumerate(targets, start=2):
        state, event = step(state, target, number)
        events.append(event)
    return state, tuple(events)


@pytest.mark.parametrize(
    "targets",
    [
        (
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.ACCEPTED,
        ),
        (
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.ACCEPTED,
        ),
    ],
)
def test_replay_reconstructs_identical_snapshot(
    targets: tuple[LifecyclePhase, ...],
) -> None:
    final, events = _happy_path(targets)
    assert replay_lifecycle(events) == final


def test_rework_requires_reevaluation() -> None:
    state, init_event = initial()
    events: list = [init_event]
    targets = (
        LifecyclePhase.READY,
        LifecyclePhase.IMPLEMENTING,
        LifecyclePhase.EVALUATING,
        LifecyclePhase.REWORK,
    )
    for number, target in enumerate(targets, start=2):
        state, event = step(state, target, number)
        events.append(event)
    assert replay_lifecycle(tuple(events)) == state

    with pytest.raises(InvalidPhaseTransition):
        step(state, LifecyclePhase.ACCEPTED, 6)
    state, evaluation_event = step(state, LifecyclePhase.EVALUATING, 6)
    state, accepted_event = step(state, LifecyclePhase.ACCEPTED, 7)
    assert evaluation_event.from_phase is LifecyclePhase.REWORK
    assert accepted_event.from_phase is LifecyclePhase.EVALUATING


def test_implementation_cannot_accept_itself() -> None:
    with pytest.raises(InvalidPhaseTransition):
        step(snapshot(LifecyclePhase.IMPLEMENTING), LifecyclePhase.ACCEPTED, 2)


def test_definition_escalation_is_direct() -> None:
    state, init_event = initial()
    events: list = [init_event]
    targets = (
        LifecyclePhase.READY,
        LifecyclePhase.IMPLEMENTING,
        LifecyclePhase.EVALUATING,
        LifecyclePhase.DEFINING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.READY,
    )
    for number, target in enumerate(targets, start=2):
        state, event = step(state, target, number)
        events.append(event)
    assert events[4].from_phase is LifecyclePhase.EVALUATING
    assert events[4].to_phase is LifecyclePhase.DEFINING
    assert replay_lifecycle(tuple(events)) == state


def test_contract_escalation_and_architecture_escalation_are_supported() -> None:
    state, _ = initial()
    for number, target in enumerate(
        (
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.READY,
        ),
        start=2,
    ):
        state, event = step(state, target, number)
        assert event.to_phase is target


def test_successful_operations_each_emit_one_event_and_increment_once() -> None:
    state, initialized = initial()
    state, phase_event = step(state, LifecyclePhase.READY, 2)
    state, blocked_event = set_blocked(
        state, (reason(),), event_id(3), ACTOR, T0 + timedelta(seconds=3), "A blocker appeared."
    )
    state, updated_block_event = set_blocked(
        state,
        (reason("FIRST", "First blocker."), reason("SECOND", "Second blocker.")),
        event_id(4),
        ACTOR,
        T0 + timedelta(seconds=4),
        "A second blocker appeared.",
    )
    state, cleared_event = clear_blockage(
        state, event_id(5), ACTOR, T0 + timedelta(seconds=5), "The blockers are resolved."
    )
    state, stale_event = mark_stale(
        state, event_id(6), ACTOR, T0 + timedelta(seconds=6), "The upstream design changed."
    )
    state, current_event = revalidate(
        state, event_id(7), ACTOR, T0 + timedelta(seconds=7), "The implementation was rechecked."
    )
    assert [
        initialized.resulting_revision,
        phase_event.resulting_revision,
        blocked_event.resulting_revision,
        updated_block_event.resulting_revision,
        cleared_event.resulting_revision,
        stale_event.resulting_revision,
        current_event.resulting_revision,
    ] == list(range(7))
    assert state.revision == 6
    assert (
        len(
            {
                initialized.event_id,
                phase_event.event_id,
                blocked_event.event_id,
                updated_block_event.event_id,
                cleared_event.event_id,
                stale_event.event_id,
                current_event.event_id,
            }
        )
        == 7
    )


def test_blocked_preserves_phase_during_remediation() -> None:
    state, init_event = initial()
    state, ready_event = step(state, LifecyclePhase.READY, 2)
    state, implementation_event = step(state, LifecyclePhase.IMPLEMENTING, 3)
    state, blocked_event = set_blocked(
        state,
        (reason(),),
        event_id(4),
        ACTOR,
        T0 + timedelta(seconds=4),
        "Implementation is blocked.",
    )
    state, contract_event = step(state, LifecyclePhase.CONTRACTING, 5)
    assert state.blockage.status is BlockageStatus.BLOCKED

    assert state.phase is LifecyclePhase.CONTRACTING
    assert state.revision == 4
    assert (
        replay_lifecycle(
            (init_event, ready_event, implementation_event, blocked_event, contract_event)
        )
        == state
    )


def test_blocked_cancellation_clears_blockage_once() -> None:
    state, init_event = initial()
    state, ready_event = step(state, LifecyclePhase.READY, 2)
    state, implementation_event = step(state, LifecyclePhase.IMPLEMENTING, 3)
    state, blocked_event = set_blocked(
        state,
        (reason(),),
        event_id(4),
        ACTOR,
        T0 + timedelta(seconds=4),
        "Implementation is blocked.",
    )
    state, contract_event = step(state, LifecyclePhase.CONTRACTING, 5)
    state, cancelled_event = step(state, LifecyclePhase.CANCELLED, 6)
    assert state.phase is LifecyclePhase.CANCELLED
    assert state.blockage == Blockage(status=BlockageStatus.CLEAR, reasons=())
    assert cancelled_event.resulting_revision == 5
    assert (
        replay_lifecycle(
            (
                init_event,
                ready_event,
                implementation_event,
                blocked_event,
                contract_event,
                cancelled_event,
            )
        )
        == state
    )


@pytest.mark.parametrize(
    "target", [LifecyclePhase.IMPLEMENTING, LifecyclePhase.EVALUATING, LifecyclePhase.ACCEPTED]
)
def test_blocked_forward_progress_is_rejected(target: LifecyclePhase) -> None:
    phase = (
        LifecyclePhase.READY
        if target is LifecyclePhase.IMPLEMENTING
        else LifecyclePhase.IMPLEMENTING
    )
    state = snapshot(
        phase,
        blockage=Blockage(status=BlockageStatus.BLOCKED, reasons=(reason(),)),
    )
    with pytest.raises(InvalidPhaseTransition):
        step(state, target, 2)


def test_accepted_can_be_stale() -> None:
    accepted, init_event = initial()
    history: list = [init_event]
    for number, phase in enumerate(
        (
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.ACCEPTED,
        ),
        start=2,
    ):
        accepted, phase_event = step(accepted, phase, number)
        history.append(phase_event)
    stale, event = mark_stale(
        accepted,
        event_id(6),
        ACTOR,
        T0 + timedelta(seconds=6),
        "Upstream authority changed.",
    )
    assert stale.phase is LifecyclePhase.ACCEPTED
    assert stale.validity is LifecycleValidity.STALE
    history.append(event)
    assert replay_lifecycle(tuple(history)) == stale

    ready = snapshot(LifecyclePhase.READY, validity=LifecycleValidity.STALE)
    with pytest.raises(InvalidPhaseTransition):
        step(ready, LifecyclePhase.IMPLEMENTING, 3)
    evaluating = snapshot(LifecyclePhase.EVALUATING, validity=LifecycleValidity.STALE)
    with pytest.raises(InvalidPhaseTransition):
        step(evaluating, LifecyclePhase.ACCEPTED, 4)


def test_stale_preserves_phase() -> None:
    state = snapshot(LifecyclePhase.DESIGNING)
    stale, event = mark_stale(
        state, event_id(2), ACTOR, T0 + timedelta(seconds=2), "Design input changed."
    )
    assert stale.phase is state.phase
    assert stale.blockage == state.blockage
    assert stale.validity is LifecycleValidity.STALE
    assert event.resulting_revision == state.revision + 1


def test_accepted_history_cannot_return_to_rework() -> None:
    with pytest.raises(InvalidPhaseTransition):
        step(snapshot(LifecyclePhase.ACCEPTED), LifecyclePhase.REWORK, 2)


def test_revalidation_preserves_phase_and_blockage() -> None:
    blocked_stale = snapshot(
        LifecyclePhase.CONTRACTING,
        validity=LifecycleValidity.STALE,
        blockage=Blockage(status=BlockageStatus.BLOCKED, reasons=(reason(),)),
    )
    current, event = revalidate(
        blocked_stale, event_id(2), ACTOR, T0 + timedelta(seconds=2), "The contract was rechecked."
    )
    assert current.phase is LifecyclePhase.CONTRACTING
    assert current.blockage == blocked_stale.blockage
    assert current.validity is LifecycleValidity.CURRENT
    assert event.before is LifecycleValidity.STALE
    assert event.after is LifecycleValidity.CURRENT


def test_supersession_preserves_successor_in_snapshot() -> None:
    accepted = snapshot(LifecyclePhase.ACCEPTED, validity=LifecycleValidity.STALE)
    with pytest.raises(InvalidLifecycleOperation, match="requires a successor"):
        step(accepted, LifecyclePhase.SUPERSEDED, 2)
    with pytest.raises(InvalidLifecycleOperation, match="cannot supersede itself"):
        step(accepted, LifecyclePhase.SUPERSEDED, 2, successor=SLICE_ID)
    successor, event = step(accepted, LifecyclePhase.SUPERSEDED, 2, successor=OTHER_SLICE_ID)
    assert successor.superseded_by_slice_id == OTHER_SLICE_ID
    assert successor.validity is LifecycleValidity.STALE
    state, initial_event = initial()
    events: list = [initial_event]
    for number, phase in enumerate(
        (
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.ACCEPTED,
        ),
        start=2,
    ):
        state, phase_event = step(state, phase, number)
        events.append(phase_event)
    state, stale_event = mark_stale(
        state, event_id(6), ACTOR, T0 + timedelta(seconds=6), "Upstream authority changed."
    )
    events.append(stale_event)
    state, superseded_event = step(state, LifecyclePhase.SUPERSEDED, 7, successor=OTHER_SLICE_ID)
    events.append(superseded_event)

    assert SliceLifecycle.model_validate_json(state.model_dump_json()) == state
    assert replay_lifecycle(tuple(events)) == state
    assert superseded_event.superseded_by_slice_id == OTHER_SLICE_ID


def test_supersession_requires_successor() -> None:
    accepted = snapshot(LifecyclePhase.ACCEPTED)
    with pytest.raises(InvalidLifecycleOperation, match="requires a successor"):
        step(accepted, LifecyclePhase.SUPERSEDED, 2)
    with pytest.raises(InvalidLifecycleOperation, match="cannot supersede itself"):
        step(accepted, LifecyclePhase.SUPERSEDED, 2, successor=SLICE_ID)


def test_noop_is_rejected_without_event_or_revision_change() -> None:
    state, _ = initial()
    state, _ = step(state, LifecyclePhase.READY, 2)
    before = state
    with pytest.raises(InvalidLifecycleOperation):
        step(state, LifecyclePhase.READY, 3)
    with pytest.raises(InvalidLifecycleOperation):
        mark_stale(state, event_id(3), ACTOR, T0 + timedelta(seconds=3), "  ")
    with pytest.raises(InvalidLifecycleOperation):
        revalidate(state, event_id(3), ACTOR, T0 + timedelta(seconds=3), "Already current.")
    with pytest.raises(InvalidLifecycleOperation):
        clear_blockage(state, event_id(3), ACTOR, T0 + timedelta(seconds=3), "Already clear.")
    with pytest.raises(InvalidLifecycleOperation):
        transition_phase(
            state,
            LifecyclePhase.IMPLEMENTING,
            "bad_id",
            ACTOR,
            T0 + timedelta(seconds=3),
            "Start work.",
        )  # type: ignore[arg-type]
    with pytest.raises(InvalidLifecycleOperation):
        step(state, LifecyclePhase.IMPLEMENTING, 4, at=T0 - timedelta(seconds=1))

    blocked, _ = set_blocked(
        state, (reason(),), event_id(3), ACTOR, T0 + timedelta(seconds=3), "Block it."
    )
    with pytest.raises(InvalidLifecycleOperation):
        set_blocked(
            blocked, (reason(),), event_id(4), ACTOR, T0 + timedelta(seconds=4), "Repeat it."
        )
    assert state == before


def test_timestamp_regression_is_rejected() -> None:
    state, _ = initial()
    state, _ = step(state, LifecyclePhase.READY, 2)
    with pytest.raises(InvalidLifecycleOperation):
        step(state, LifecyclePhase.IMPLEMENTING, 3, at=T0 - timedelta(seconds=1))


def test_replay_rejects_empty_missing_duplicate_wrong_slice_and_bad_revision() -> None:
    initialized = initial()[1]
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle(())
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle(
            (
                PhaseChanged(
                    event_id=event_id(2),
                    slice_id=SLICE_ID,
                    actor=ACTOR,
                    occurred_at=T0,
                    reason="Missing initialization.",
                    resulting_revision=1,
                    from_phase=LifecyclePhase.PROPOSED,
                    to_phase=LifecyclePhase.DEFINING,
                    superseded_by_slice_id=None,
                ),
            )
        )
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, initialized))

    _, ready = step(initial()[0], LifecyclePhase.READY, 2)
    wrong_slice = ready.model_copy(update={"slice_id": OTHER_SLICE_ID})
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, wrong_slice))
    gap = ready.model_copy(update={"resulting_revision": 9})
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, gap))
    duplicate_id = ready.model_copy(update={"event_id": initialized.event_id})
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, duplicate_id))


def test_replay_rejects_duplicate_event_id() -> None:
    initialized = initial()[1]
    _, ready = step(initial()[0], LifecyclePhase.READY, 2)
    duplicate_id = ready.model_copy(update={"event_id": initialized.event_id})
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, duplicate_id))


def test_replay_rejects_terminal_history_extension() -> None:
    initialized = initial()[1]
    _, ready = step(initial()[0], LifecyclePhase.READY, 2)
    regressed = ready.model_copy(update={"occurred_at": T0 - timedelta(seconds=1)})
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, regressed))

    unexpected = ready.model_copy(update={"from_phase": LifecyclePhase.DEFINING})
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, unexpected))

    state, init_event = initial()
    history: list = [init_event]
    for number, target in enumerate((LifecyclePhase.READY, LifecyclePhase.CANCELLED), start=2):
        state, event = step(state, target, number)
        history.append(event)
    after_terminal = PhaseChanged(
        event_id=event_id(4),
        slice_id=SLICE_ID,
        actor=ACTOR,
        occurred_at=T0 + timedelta(seconds=4),
        reason="Invalid continuation.",
        resulting_revision=3,
        from_phase=LifecyclePhase.CANCELLED,
        to_phase=LifecyclePhase.DEFINING,
        superseded_by_slice_id=None,
    )
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((*history, after_terminal))

    state, init_event = initial()
    history = [init_event]
    for number, target in enumerate(
        (
            LifecyclePhase.READY,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.ACCEPTED,
        ),
        start=2,
    ):
        state, event = step(state, target, number)
        history.append(event)
    state, superseded = step(state, LifecyclePhase.SUPERSEDED, 6, successor=OTHER_SLICE_ID)
    history.append(superseded)
    after_superseded = PhaseChanged(
        event_id=event_id(7),
        slice_id=SLICE_ID,
        actor=ACTOR,
        occurred_at=T0 + timedelta(seconds=7),
        reason="Invalid continuation.",
        resulting_revision=6,
        from_phase=LifecyclePhase.SUPERSEDED,
        to_phase=LifecyclePhase.DEFINING,
        superseded_by_slice_id=None,
    )
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((*history, after_superseded))


def test_replay_rejects_invalid_blockage_validity_and_supersession_history() -> None:
    initialized = initial()[1]
    state, ready = step(initial()[0], LifecyclePhase.READY, 2)
    invalid_blockage = BlockageChanged(
        event_id=event_id(3),
        slice_id=SLICE_ID,
        actor=ACTOR,
        occurred_at=T0 + timedelta(seconds=3),
        reason="Incorrect prior blockage.",
        resulting_revision=2,
        before=Blockage(status=BlockageStatus.BLOCKED, reasons=(reason(),)),
        after=Blockage(status=BlockageStatus.CLEAR, reasons=()),
    )
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, ready, invalid_blockage))

    stale_event = ValidityChanged(
        event_id=event_id(3),
        slice_id=SLICE_ID,
        actor=ACTOR,
        occurred_at=T0 + timedelta(seconds=3),
        reason="Set stale.",
        resulting_revision=2,
        before=LifecycleValidity.STALE,
        after=LifecycleValidity.CURRENT,
    )
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, ready, stale_event))

    stale_transition = PhaseChanged(
        event_id=event_id(4),
        slice_id=SLICE_ID,
        actor=ACTOR,
        occurred_at=T0 + timedelta(seconds=4),
        reason="Attempt to implement stale work.",
        resulting_revision=3,
        from_phase=LifecyclePhase.READY,
        to_phase=LifecyclePhase.IMPLEMENTING,
        superseded_by_slice_id=None,
    )
    current_to_stale = ValidityChanged(
        event_id=event_id(3),
        slice_id=SLICE_ID,
        actor=ACTOR,
        occurred_at=T0 + timedelta(seconds=3),
        reason="Mark stale.",
        resulting_revision=2,
        before=LifecycleValidity.CURRENT,
        after=LifecycleValidity.STALE,
    )
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, ready, current_to_stale, stale_transition))

    malformed_successor = PhaseChanged.model_construct(
        schema_version=1,
        event_id=event_id(3),
        slice_id=SLICE_ID,
        actor=ACTOR,
        occurred_at=T0 + timedelta(seconds=3),
        reason="Malformed supersession.",
        resulting_revision=2,
        from_phase=LifecyclePhase.READY,
        to_phase=LifecyclePhase.SUPERSEDED,
        superseded_by_slice_id=None,
    )
    with pytest.raises(LifecycleReplayError):
        replay_lifecycle((initialized, ready, malformed_successor))


def test_event_inputs_are_explicit_utc_normalized_and_complete() -> None:
    offset = timezone(timedelta(hours=-4))
    state, event = initialize_lifecycle(
        SLICE_ID, event_id(1), ACTOR, T0.astimezone(offset), " Explicit initialization. "
    )
    assert event.occurred_at.tzinfo is UTC
    assert state.updated_at == event.occurred_at
    assert event.reason == " Explicit initialization. "
    assert event.actor == ACTOR
    assert event.event_id == event_id(1)

    with pytest.raises(InvalidLifecycleOperation, match="aware datetime"):
        initialize_lifecycle(
            SLICE_ID,
            event_id(2),
            ACTOR,
            datetime(2026, 9, 23),
            "Reject a naive timestamp.",
        )


def test_identical_inputs_are_deterministic() -> None:
    state_a, event_a = initial()
    state_b, event_b = initial()
    assert state_a == state_b
    assert event_a == event_b
    state_a, phase_a = step(state_a, LifecyclePhase.READY, 2)
    state_b, phase_b = step(state_b, LifecyclePhase.READY, 2)
    assert state_a == state_b
    assert phase_a == phase_b


def test_event_id_is_explicit_and_engine_generates_no_id() -> None:
    parameters = signature(initialize_lifecycle).parameters
    assert parameters["event_id"].default is parameters["event_id"].empty
    state, event = initialize_lifecycle(
        SLICE_ID, event_id(77), ACTOR, T0, "Caller supplies event identity."
    )
    assert state.revision == 0
    assert event.event_id == event_id(77)


def test_terminal_states_have_no_normal_outgoing_transition() -> None:
    for terminal in (LifecyclePhase.SUPERSEDED, LifecyclePhase.CANCELLED):
        current = snapshot(
            terminal,
            successor=OTHER_SLICE_ID if terminal is LifecyclePhase.SUPERSEDED else None,
        )
        for target in LifecyclePhase:
            if target is not terminal:
                with pytest.raises(InvalidPhaseTransition):
                    step(current, target, 2)


def test_lifecycle_operations_raise_only_lifecycle_error_family_for_contract_failures() -> None:
    state, _ = initial()
    with pytest.raises(LifecycleError):
        transition_phase(
            state,
            LifecyclePhase.ACCEPTED,
            event_id(2),
            ACTOR,
            T0 + timedelta(seconds=2),
            "Skip evaluation.",
        )


def test_equal_timestamp_is_allowed() -> None:
    state, initialized = initialize_lifecycle(SLICE_ID, event_id(1), ACTOR, T0, "Initialize.")
    state, first = transition_phase(
        state, LifecyclePhase.READY, event_id(2), ACTOR, T0, "Prepare work."
    )
    state, second = transition_phase(
        state, LifecyclePhase.IMPLEMENTING, event_id(3), ACTOR, T0, "Start work."
    )
    assert first.occurred_at == second.occurred_at
    assert replay_lifecycle((initialized, first, second)) == state
