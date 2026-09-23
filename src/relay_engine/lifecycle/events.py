"""Immutable, versioned events emitted by lifecycle operations."""

from datetime import UTC, datetime
from typing import Annotated

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import EventId, SliceId
from relay_engine.domain.references import ActorRef
from relay_engine.lifecycle.models import (
    Blockage,
    LifecyclePhase,
    LifecycleValidity,
)


class _LifecycleEvent(DomainModel):
    """Shared provenance for a single successful lifecycle operation."""

    event_id: EventId
    slice_id: SliceId
    actor: ActorRef
    occurred_at: datetime
    reason: str
    resulting_revision: Annotated[int, Field(ge=0)]

    @field_validator("occurred_at")
    @classmethod
    def occurred_at_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class LifecycleInitialized(_LifecycleEvent):
    """The initial lifecycle snapshot for one slice."""

    @model_validator(mode="after")
    def revision_is_zero(self) -> LifecycleInitialized:
        if self.resulting_revision != 0:
            raise ValueError("initialization event must have resulting_revision zero")
        return self


class PhaseChanged(_LifecycleEvent):
    """A lifecycle phase change, including cancellation or supersession."""

    from_phase: LifecyclePhase
    to_phase: LifecyclePhase
    superseded_by_slice_id: SliceId | None

    @model_validator(mode="after")
    def successor_matches_target(self) -> PhaseChanged:
        if self.from_phase is self.to_phase:
            raise ValueError("phase change must change the phase")
        if self.to_phase is LifecyclePhase.SUPERSEDED and self.superseded_by_slice_id is None:
            raise ValueError("supersession event requires a successor slice")
        if (
            self.to_phase is not LifecyclePhase.SUPERSEDED
            and self.superseded_by_slice_id is not None
        ):
            raise ValueError("only supersession events may identify a successor slice")
        if self.superseded_by_slice_id == self.slice_id:
            raise ValueError("a slice cannot supersede itself")
        return self


class BlockageChanged(_LifecycleEvent):
    """A change to the ordered set of explicit blocker reasons."""

    before: Blockage
    after: Blockage

    @model_validator(mode="after")
    def blockage_must_change(self) -> BlockageChanged:
        if self.before == self.after:
            raise ValueError("blockage event must change blockage")
        return self


class ValidityChanged(_LifecycleEvent):
    """A lifecycle validity change between CURRENT and STALE."""

    before: LifecycleValidity
    after: LifecycleValidity

    @model_validator(mode="after")
    def validity_must_change(self) -> ValidityChanged:
        if self.before is self.after:
            raise ValueError("validity event must change validity")
        return self


type LifecycleEvent = LifecycleInitialized | PhaseChanged | BlockageChanged | ValidityChanged
type LifecycleEventRecord = LifecycleEvent
