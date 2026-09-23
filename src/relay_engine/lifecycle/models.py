"""Immutable values describing one slice's structural lifecycle."""

import re
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import SliceId


class LifecyclePhase(StrEnum):
    PROPOSED = "PROPOSED"
    DEFINING = "DEFINING"
    RESEARCHING = "RESEARCHING"
    DESIGNING = "DESIGNING"
    CONTRACTING = "CONTRACTING"
    PLANNING = "PLANNING"
    READY = "READY"
    IMPLEMENTING = "IMPLEMENTING"
    EVALUATING = "EVALUATING"
    REWORK = "REWORK"
    ACCEPTED = "ACCEPTED"
    SUPERSEDED = "SUPERSEDED"
    CANCELLED = "CANCELLED"


class LifecycleValidity(StrEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"


class BlockageStatus(StrEnum):
    CLEAR = "CLEAR"
    BLOCKED = "BLOCKED"


_BLOCK_REASON_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")
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


class BlockReason(DomainModel):
    """One explicit reason that lifecycle work is blocked."""

    code: str = Field(pattern=r"^[A-Z][A-Z0-9_]*$")
    summary: str

    @field_validator("code")
    @classmethod
    def code_is_canonical(cls, value: str) -> str:
        if not _BLOCK_REASON_CODE.fullmatch(value):
            raise ValueError(
                "block reason code must use uppercase letters, digits, and underscores"
            )
        return value

    @field_validator("summary")
    @classmethod
    def summary_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class Blockage(DomainModel):
    """Ordered blocker reasons, independent of lifecycle phase."""

    status: BlockageStatus
    reasons: tuple[BlockReason, ...]

    @field_validator("reasons")
    @classmethod
    def reasons_are_unique(cls, value: tuple[BlockReason, ...]) -> tuple[BlockReason, ...]:
        if len(value) != len(set(value)):
            raise ValueError("block reason values must be unique")
        return value

    @model_validator(mode="after")
    def reasons_match_status(self) -> Blockage:
        if self.status is BlockageStatus.CLEAR and self.reasons:
            raise ValueError("clear blockage must not contain reasons")
        if self.status is BlockageStatus.BLOCKED and not self.reasons:
            raise ValueError("blocked lifecycle must contain at least one reason")
        return self


class SliceLifecycle(DomainModel):
    """Versioned lifecycle snapshot, separate from the domain Slice value."""

    slice_id: SliceId
    phase: LifecyclePhase
    validity: LifecycleValidity
    blockage: Blockage
    revision: int = Field(ge=0)
    updated_at: datetime
    superseded_by_slice_id: SliceId | None

    @field_validator("updated_at")
    @classmethod
    def updated_at_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("updated_at must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def state_is_structurally_valid(self) -> SliceLifecycle:
        if self.blockage.status is BlockageStatus.BLOCKED and self.phase not in _BLOCKABLE_PHASES:
            raise ValueError("this lifecycle phase cannot be blocked")

        if self.phase is LifecyclePhase.SUPERSEDED:
            if self.superseded_by_slice_id is None:
                raise ValueError("superseded lifecycle requires a successor slice")
            if self.superseded_by_slice_id == self.slice_id:
                raise ValueError("a slice cannot supersede itself")
        elif self.superseded_by_slice_id is not None:
            raise ValueError("only a superseded lifecycle may identify a successor slice")
        return self
