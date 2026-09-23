"""Pure lifecycle operations and deterministic event replay."""

import re
from collections.abc import Sequence
from datetime import UTC, datetime

from pydantic import ValidationError

from relay_engine.domain.ids import EventId, SliceId
from relay_engine.domain.references import ActorRef
from relay_engine.lifecycle.errors import (
    InvalidLifecycleOperation,
    InvalidPhaseTransition,
    LifecycleError,
    LifecycleReplayError,
)
from relay_engine.lifecycle.events import (
    BlockageChanged,
    LifecycleEventRecord,
    LifecycleInitialized,
    PhaseChanged,
    ValidityChanged,
)
from relay_engine.lifecycle.models import (
    Blockage,
    BlockageStatus,
    BlockReason,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
)

_EVENT_ID_PATTERN = re.compile(
    r"^evt_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
_BLOCKABLE_PHASES = frozenset(
    {
        LifecyclePhase.DEFINING,
        LifecyclePhase.RESEARCHING,
        LifecyclePhase.DESIGNING,
        LifecyclePhase.CONTRACTING,
        LifecyclePhase.PLANNING,
        LifecyclePhase.READY,
        LifecyclePhase.IMPLEMENTING,
        LifecyclePhase.EVALUATING,
        LifecyclePhase.REWORK,
    }
)
_TERMINAL_PHASES = frozenset({LifecyclePhase.CANCELLED, LifecyclePhase.SUPERSEDED})
_PHASE_TRANSITIONS: dict[LifecyclePhase, frozenset[LifecyclePhase]] = {
    LifecyclePhase.PROPOSED: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.READY,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.DEFINING: frozenset(
        {
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.READY,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.RESEARCHING: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.READY,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.DESIGNING: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.READY,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.CONTRACTING: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.READY,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.PLANNING: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.READY,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.READY: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.IMPLEMENTING,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.IMPLEMENTING: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.EVALUATING: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.REWORK,
            LifecyclePhase.ACCEPTED,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.REWORK: frozenset(
        {
            LifecyclePhase.DEFINING,
            LifecyclePhase.RESEARCHING,
            LifecyclePhase.DESIGNING,
            LifecyclePhase.CONTRACTING,
            LifecyclePhase.PLANNING,
            LifecyclePhase.EVALUATING,
            LifecyclePhase.CANCELLED,
        }
    ),
    LifecyclePhase.ACCEPTED: frozenset({LifecyclePhase.SUPERSEDED}),
    LifecyclePhase.SUPERSEDED: frozenset(),
    LifecyclePhase.CANCELLED: frozenset(),
}


def initialize_lifecycle(
    slice_id: SliceId,
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[SliceLifecycle, LifecycleInitialized]:
    """Create the revision-zero lifecycle and its initialization event."""

    event_id, occurred_at = _operation_context(event_id, actor, occurred_at, reason)
    snapshot = SliceLifecycle(
        slice_id=slice_id,
        phase=LifecyclePhase.PROPOSED,
        validity=LifecycleValidity.CURRENT,
        blockage=_clear_blockage(),
        revision=0,
        updated_at=occurred_at,
        superseded_by_slice_id=None,
    )
    event = LifecycleInitialized(
        event_id=event_id,
        slice_id=slice_id,
        actor=actor,
        occurred_at=occurred_at,
        reason=reason,
        resulting_revision=0,
    )
    return snapshot, event


def transition_phase(
    current: SliceLifecycle,
    target_phase: LifecyclePhase,
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
    superseded_by_slice_id: SliceId | None = None,
) -> tuple[SliceLifecycle, PhaseChanged]:
    """Apply one structurally valid phase transition and emit its event."""

    event_id, occurred_at = _operation_context(event_id, actor, occurred_at, reason)
    _ensure_non_regressing_time(current, occurred_at)
    _validate_phase_change(current, target_phase, superseded_by_slice_id)

    blockage = current.blockage
    if target_phase is LifecyclePhase.CANCELLED and blockage.status is BlockageStatus.BLOCKED:
        blockage = _clear_blockage()

    updated = _snapshot(
        current,
        phase=target_phase,
        blockage=blockage,
        revision=current.revision + 1,
        updated_at=occurred_at,
        superseded_by_slice_id=superseded_by_slice_id,
    )
    event = PhaseChanged(
        event_id=event_id,
        slice_id=current.slice_id,
        actor=actor,
        occurred_at=occurred_at,
        reason=reason,
        resulting_revision=updated.revision,
        from_phase=current.phase,
        to_phase=target_phase,
        superseded_by_slice_id=superseded_by_slice_id,
    )
    return updated, event


def validate_phase_transition(
    current: SliceLifecycle,
    target_phase: LifecyclePhase,
    superseded_by_slice_id: SliceId | None = None,
) -> None:
    """Validate a phase movement without creating an event or changing state."""

    _validate_phase_change(current, target_phase, superseded_by_slice_id)


def set_blocked(
    current: SliceLifecycle,
    reasons: tuple[BlockReason, ...],
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[SliceLifecycle, BlockageChanged]:
    """Set or replace blockers while preserving their supplied order."""

    event_id, occurred_at = _operation_context(event_id, actor, occurred_at, reason)
    _ensure_non_regressing_time(current, occurred_at)
    if current.phase not in _BLOCKABLE_PHASES:
        raise InvalidLifecycleOperation("this lifecycle phase cannot be blocked")
    after = Blockage(status=BlockageStatus.BLOCKED, reasons=reasons)
    if after == current.blockage:
        raise InvalidLifecycleOperation("setting the current blockage is a no-op")

    updated = _snapshot(
        current,
        blockage=after,
        revision=current.revision + 1,
        updated_at=occurred_at,
    )
    event = BlockageChanged(
        event_id=event_id,
        slice_id=current.slice_id,
        actor=actor,
        occurred_at=occurred_at,
        reason=reason,
        resulting_revision=updated.revision,
        before=current.blockage,
        after=after,
    )
    return updated, event


def clear_blockage(
    current: SliceLifecycle,
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[SliceLifecycle, BlockageChanged]:
    """Clear an existing blockage and emit one event."""

    event_id, occurred_at = _operation_context(event_id, actor, occurred_at, reason)
    _ensure_non_regressing_time(current, occurred_at)
    if current.blockage.status is BlockageStatus.CLEAR:
        raise InvalidLifecycleOperation("clearing an already clear blockage is a no-op")

    after = _clear_blockage()
    updated = _snapshot(
        current,
        blockage=after,
        revision=current.revision + 1,
        updated_at=occurred_at,
    )
    event = BlockageChanged(
        event_id=event_id,
        slice_id=current.slice_id,
        actor=actor,
        occurred_at=occurred_at,
        reason=reason,
        resulting_revision=updated.revision,
        before=current.blockage,
        after=after,
    )
    return updated, event


def mark_stale(
    current: SliceLifecycle,
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[SliceLifecycle, ValidityChanged]:
    """Mark nonterminal work stale without changing its phase or blockage."""

    return _change_validity(
        current,
        LifecycleValidity.STALE,
        event_id,
        actor,
        occurred_at,
        reason,
    )


def revalidate(
    current: SliceLifecycle,
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[SliceLifecycle, ValidityChanged]:
    """Restore current validity without changing phase or blockage."""

    return _change_validity(
        current,
        LifecycleValidity.CURRENT,
        event_id,
        actor,
        occurred_at,
        reason,
    )


def replay_lifecycle(events: Sequence[LifecycleEventRecord]) -> SliceLifecycle:
    """Reconstruct one lifecycle from a strict ordered event history."""

    if not events:
        raise LifecycleReplayError("lifecycle replay requires a non-empty event sequence")

    validated_events = tuple(_validated_replay_event(event) for event in events)
    first = validated_events[0]
    if not isinstance(first, LifecycleInitialized) or first.resulting_revision != 0:
        raise LifecycleReplayError("history must begin with one revision-zero initialization event")

    try:
        current = SliceLifecycle(
            slice_id=first.slice_id,
            phase=LifecyclePhase.PROPOSED,
            validity=LifecycleValidity.CURRENT,
            blockage=_clear_blockage(),
            revision=0,
            updated_at=first.occurred_at,
            superseded_by_slice_id=None,
        )
    except ValidationError as error:
        raise LifecycleReplayError(
            "initialization event cannot produce a valid snapshot"
        ) from error

    seen_event_ids = {first.event_id}
    for event in validated_events[1:]:
        if isinstance(event, LifecycleInitialized):
            raise LifecycleReplayError("initialization may occur only once at the start of history")
        if event.event_id in seen_event_ids:
            raise LifecycleReplayError("event IDs must be unique within one lifecycle history")
        seen_event_ids.add(event.event_id)
        if event.slice_id != current.slice_id:
            raise LifecycleReplayError("event slice_id does not match the initialized lifecycle")
        if event.resulting_revision != current.revision + 1:
            raise LifecycleReplayError("event revision must advance exactly once")
        if event.occurred_at < current.updated_at:
            raise LifecycleReplayError("event time must not regress")
        current = _apply_replay_event(current, event)
    return current


def _change_validity(
    current: SliceLifecycle,
    target: LifecycleValidity,
    event_id: EventId,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[SliceLifecycle, ValidityChanged]:
    event_id, occurred_at = _operation_context(event_id, actor, occurred_at, reason)
    _ensure_non_regressing_time(current, occurred_at)
    if current.phase in _TERMINAL_PHASES:
        raise InvalidLifecycleOperation("terminal lifecycle validity cannot change")
    if target is current.validity:
        raise InvalidLifecycleOperation("setting the current validity is a no-op")

    updated = _snapshot(
        current,
        validity=target,
        revision=current.revision + 1,
        updated_at=occurred_at,
    )
    event = ValidityChanged(
        event_id=event_id,
        slice_id=current.slice_id,
        actor=actor,
        occurred_at=occurred_at,
        reason=reason,
        resulting_revision=updated.revision,
        before=current.validity,
        after=target,
    )
    return updated, event


def _operation_context(
    event_id: str,
    actor: ActorRef,
    occurred_at: datetime,
    reason: str,
) -> tuple[EventId, datetime]:
    if not _EVENT_ID_PATTERN.fullmatch(event_id):
        raise InvalidLifecycleOperation("event_id must be an explicit evt_<uuid7> identifier")
    if occurred_at.tzinfo is None:
        raise InvalidLifecycleOperation("occurred_at must be an explicit aware datetime")
    if occurred_at.utcoffset() is None:
        raise InvalidLifecycleOperation("occurred_at must be an explicit aware datetime")
    if not reason.strip():
        raise InvalidLifecycleOperation("reason must be non-empty and non-whitespace")
    return event_id, occurred_at.astimezone(UTC)


def _ensure_non_regressing_time(current: SliceLifecycle, occurred_at: datetime) -> None:
    if occurred_at < current.updated_at:
        raise InvalidLifecycleOperation("occurred_at must not precede updated_at")


def _validate_phase_change(
    current: SliceLifecycle,
    target_phase: LifecyclePhase,
    successor: SliceId | None,
) -> None:
    if target_phase is current.phase:
        raise InvalidLifecycleOperation("transitioning to the current phase is a no-op")
    if target_phase not in _PHASE_TRANSITIONS[current.phase]:
        raise InvalidPhaseTransition(f"transition {current.phase} → {target_phase} is not allowed")
    if current.blockage.status is BlockageStatus.BLOCKED and target_phase in {
        LifecyclePhase.IMPLEMENTING,
        LifecyclePhase.EVALUATING,
        LifecyclePhase.ACCEPTED,
    }:
        raise InvalidPhaseTransition("blocked lifecycle cannot enter an execution/evaluation phase")
    if current.validity is LifecycleValidity.STALE and target_phase in {
        LifecyclePhase.IMPLEMENTING,
        LifecyclePhase.ACCEPTED,
    }:
        raise InvalidPhaseTransition("stale lifecycle must be revalidated before this transition")
    if target_phase is LifecyclePhase.SUPERSEDED:
        if successor is None:
            raise InvalidLifecycleOperation("supersession requires a successor slice")
        if successor == current.slice_id:
            raise InvalidLifecycleOperation("a slice cannot supersede itself")
    elif successor is not None:
        raise InvalidLifecycleOperation("a successor slice is valid only for supersession")


def _snapshot(
    current: SliceLifecycle,
    *,
    phase: LifecyclePhase | None = None,
    validity: LifecycleValidity | None = None,
    blockage: Blockage | None = None,
    revision: int,
    updated_at: datetime,
    superseded_by_slice_id: SliceId | None = None,
) -> SliceLifecycle:
    return SliceLifecycle(
        slice_id=current.slice_id,
        phase=current.phase if phase is None else phase,
        validity=current.validity if validity is None else validity,
        blockage=current.blockage if blockage is None else blockage,
        revision=revision,
        updated_at=updated_at,
        superseded_by_slice_id=superseded_by_slice_id,
    )


def _clear_blockage() -> Blockage:
    return Blockage(status=BlockageStatus.CLEAR, reasons=())


def _validated_replay_event(event: object) -> LifecycleEventRecord:
    event_type = type(event)
    if event_type not in {
        LifecycleInitialized,
        PhaseChanged,
        BlockageChanged,
        ValidityChanged,
    }:
        raise LifecycleReplayError("history contains an unknown lifecycle event type")
    try:
        return event_type.model_validate_json(event.model_dump_json())  # type: ignore[attr-defined, no-any-return]
    except (AttributeError, TypeError, ValueError, ValidationError) as error:
        raise LifecycleReplayError("history contains a malformed lifecycle event") from error


def _apply_replay_event(
    current: SliceLifecycle,
    event: LifecycleEventRecord,
) -> SliceLifecycle:
    revision = event.resulting_revision
    timestamp = event.occurred_at
    try:
        if isinstance(event, PhaseChanged):
            if event.from_phase is not current.phase:
                raise LifecycleReplayError("phase event from_phase does not match prior state")
            _validate_phase_change(current, event.to_phase, event.superseded_by_slice_id)
            blockage = current.blockage
            if event.to_phase is LifecyclePhase.CANCELLED:
                blockage = _clear_blockage()
            return _snapshot(
                current,
                phase=event.to_phase,
                blockage=blockage,
                revision=revision,
                updated_at=timestamp,
                superseded_by_slice_id=event.superseded_by_slice_id,
            )

        if isinstance(event, BlockageChanged):
            if event.before != current.blockage:
                raise LifecycleReplayError("blockage event before value does not match prior state")
            if current.phase not in _BLOCKABLE_PHASES:
                raise LifecycleReplayError("blockage cannot change in this lifecycle phase")
            return _snapshot(
                current,
                blockage=event.after,
                revision=revision,
                updated_at=timestamp,
            )

        if isinstance(event, ValidityChanged):
            if event.before is not current.validity:
                raise LifecycleReplayError("validity event before value does not match prior state")
            if current.phase in _TERMINAL_PHASES:
                raise LifecycleReplayError("validity cannot change after a terminal phase")
            return _snapshot(
                current,
                validity=event.after,
                revision=revision,
                updated_at=timestamp,
            )
    except LifecycleReplayError:
        raise
    except (LifecycleError, ValidationError, TypeError, ValueError) as error:
        raise LifecycleReplayError("event violates lifecycle transition rules") from error
    raise LifecycleReplayError("history contains an unsupported lifecycle event")
