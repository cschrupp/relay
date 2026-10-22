"""Strict, versioned models for the local B1 adoption intake."""

import math
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal, cast
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from relay_engine.bootstrap_discovery.models import InspectionState
from relay_engine.domain._base import require_nonblank

type Sha256Digest = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
type CommitSha = Annotated[str, Field(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")]


class IntakeModel(BaseModel):
    """Immutable strict base for serialized B1 values."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
    )


class ManifestStatus(StrEnum):
    INCOMPLETE = "INCOMPLETE"
    READY_FOR_B2_REVIEW = "READY_FOR_B2_REVIEW"


class UnresolvedKey(StrEnum):
    PROJECT_NAME = "PROJECT_NAME"
    CANONICAL_REPOSITORY = "CANONICAL_REPOSITORY"
    PROJECT_OBJECTIVE = "PROJECT_OBJECTIVE"
    CURRENT_STATUS = "CURRENT_STATUS"
    HUMAN_OBJECTIVE = "HUMAN_OBJECTIVE"
    CONSTRAINTS = "CONSTRAINTS"
    WORK_FOCUS_KIND = "WORK_FOCUS_KIND"
    WORK_FOCUS = "WORK_FOCUS"


class WorkFocusKind(StrEnum):
    CURRENT_FRONTIER = "CURRENT_FRONTIER"
    FIRST_GOVERNED_WORK = "FIRST_GOVERNED_WORK"


class ConstraintState(StrEnum):
    EXPLICIT_NONE = "EXPLICIT_NONE"
    ITEMS = "ITEMS"


class ConstraintAnswer(IntakeModel):
    state: ConstraintState
    items: tuple[str, ...]

    @field_validator("items")
    @classmethod
    def items_are_nonblank(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        for value in values:
            require_nonblank(value)
        return values

    @model_validator(mode="after")
    def state_matches_items(self) -> ConstraintAnswer:
        if self.state is ConstraintState.EXPLICIT_NONE and self.items:
            raise ValueError("EXPLICIT_NONE constraints cannot contain items")
        if self.state is ConstraintState.ITEMS and not self.items:
            raise ValueError("ITEMS constraints require at least one item")
        return self


class HumanConfirmedText(IntakeModel):
    origin: Literal["HUMAN_CONFIRMED"]
    value: str
    captured_at: datetime

    @field_validator("value")
    @classmethod
    def value_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("captured_at")
    @classmethod
    def capture_time_is_utc(cls, value: datetime) -> datetime:
        return _require_utc(value)


class HumanConfirmedConstraints(IntakeModel):
    origin: Literal["HUMAN_CONFIRMED"]
    value: ConstraintAnswer
    captured_at: datetime

    @field_validator("captured_at")
    @classmethod
    def capture_time_is_utc(cls, value: datetime) -> datetime:
        return _require_utc(value)


class HumanConfirmedWorkFocusKind(IntakeModel):
    origin: Literal["HUMAN_CONFIRMED"]
    value: WorkFocusKind
    captured_at: datetime

    @field_validator("captured_at")
    @classmethod
    def capture_time_is_utc(cls, value: datetime) -> datetime:
        return _require_utc(value)


class UnresolvedFact(IntakeModel):
    origin: Literal["UNRESOLVED"]
    reason: str = Field(min_length=1, max_length=1000)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


type TextFact = Annotated[HumanConfirmedText | UnresolvedFact, Field(discriminator="origin")]
type ConstraintsFact = Annotated[
    HumanConfirmedConstraints | UnresolvedFact, Field(discriminator="origin")
]
type WorkFocusKindFact = Annotated[
    HumanConfirmedWorkFocusKind | UnresolvedFact, Field(discriminator="origin")
]


class HumanFacts(IntakeModel):
    project_name: TextFact
    canonical_repository: TextFact
    project_objective: TextFact
    current_status: TextFact
    human_objective: TextFact
    constraints: ConstraintsFact
    work_focus_kind: WorkFocusKindFact
    work_focus: TextFact

    @model_validator(mode="after")
    def canonical_repository_has_no_credentials_or_query(self) -> HumanFacts:
        fact = self.canonical_repository
        if isinstance(fact, HumanConfirmedText):
            value = fact.value
            if value.startswith("git@"):
                raise ValueError("canonical repository must not contain URI user information")
            if "://" in value:
                parsed = urlsplit(value)
                if (
                    parsed.username is not None
                    or parsed.password is not None
                    or parsed.query
                    or parsed.fragment
                    or not parsed.hostname
                ):
                    raise ValueError(
                        "canonical repository URI must not contain credentials, query, or fragment"
                    )
        return self


class ObservedFact(IntakeModel):
    origin: Literal["OBSERVED"] = "OBSERVED"
    value: Any
    report_pointer: str = Field(min_length=1)

    @field_validator("value")
    @classmethod
    def value_is_json(cls, value: Any) -> Any:
        if not _is_json_value(value):
            raise ValueError("observed value must contain only finite JSON values")
        return value


class ObservedProjection(IntakeModel):
    repository_path: ObservedFact
    observed_at: ObservedFact
    discovery_status: ObservedFact
    diagnostics: ObservedFact
    head_sha: ObservedFact
    branch: ObservedFact
    detached_head: ObservedFact
    dirty: ObservedFact
    tracked_file_count: ObservedFact
    remotes: ObservedFact
    manifests: ObservedFact
    language_signals: ObservedFact
    ci_files: ObservedFact
    relay_contract: ObservedFact
    unresolved_human_questions: ObservedFact


class ReportBinding(IntakeModel):
    sha256: Sha256Digest
    format: Literal["relay-bootstrap-discovery"]
    schema_version: Literal[1]
    observed_at: datetime
    repository_path: str = Field(min_length=1)
    report_head_sha: CommitSha

    @field_validator("observed_at")
    @classmethod
    def observed_at_is_utc(cls, value: datetime) -> datetime:
        return _require_utc(value)

    @field_validator("repository_path")
    @classmethod
    def repository_path_is_absolute(cls, value: str) -> str:
        from pathlib import Path

        if not Path(value).is_absolute():
            raise ValueError("report repository_path must be absolute")
        return value


class ContextReference(IntakeModel):
    report_pointer: str = Field(min_length=1)
    relative_path: str = Field(min_length=1)
    sha256: Sha256Digest
    inspection_state: InspectionState
    selected_at: datetime

    @field_validator("selected_at")
    @classmethod
    def selection_time_is_utc(cls, value: datetime) -> datetime:
        return _require_utc(value)


class UnresolvedItem(IntakeModel):
    key: UnresolvedKey
    reason: str = Field(min_length=1, max_length=1000)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


class ReviewNote(IntakeModel):
    report_pointer: str = Field(min_length=1)
    note: str = Field(min_length=1, max_length=2000)
    captured_at: datetime

    @field_validator("note")
    @classmethod
    def note_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("captured_at")
    @classmethod
    def capture_time_is_utc(cls, value: datetime) -> datetime:
        return _require_utc(value)


class AdoptionManifestV1(IntakeModel):
    format: Literal["relay-adoption-manifest"] = "relay-adoption-manifest"
    schema_version: Literal[1] = 1
    preparation_status: ManifestStatus
    created_at: datetime
    updated_at: datetime
    input_report: ReportBinding
    observed: ObservedProjection
    human_facts: HumanFacts
    context_references: tuple[ContextReference, ...]
    unresolved_items: tuple[UnresolvedItem, ...]
    review_notes: tuple[ReviewNote, ...]

    @field_validator("created_at", "updated_at")
    @classmethod
    def timestamps_are_utc(cls, value: datetime) -> datetime:
        return _require_utc(value)

    @model_validator(mode="after")
    def state_is_derived_and_order_is_stable(self) -> AdoptionManifestV1:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot precede created_at")
        expected_unresolved = unresolved_items_for(self.human_facts)
        if self.unresolved_items != expected_unresolved:
            raise ValueError("unresolved_items must exactly reflect human_facts")
        expected_status = (
            ManifestStatus.INCOMPLETE if expected_unresolved else ManifestStatus.READY_FOR_B2_REVIEW
        )
        if self.preparation_status is not expected_status:
            raise ValueError("preparation_status must be derived from required Human facts")
        expected_context = tuple(
            sorted(
                self.context_references,
                key=lambda item: (item.relative_path, item.report_pointer),
            )
        )
        if self.context_references != expected_context:
            raise ValueError("context_references must be sorted by path and report pointer")
        if len({item.report_pointer for item in self.context_references}) != len(
            self.context_references
        ):
            raise ValueError("context_references must not contain duplicate report pointers")
        expected_notes = tuple(
            sorted(
                self.review_notes,
                key=lambda item: (item.captured_at, item.report_pointer, item.note),
            )
        )
        if self.review_notes != expected_notes:
            raise ValueError("review_notes must use capture-time/pointer/text ordering")
        return self


def unresolved_items_for(facts: HumanFacts) -> tuple[UnresolvedItem, ...]:
    """Derive the stable unresolved list from the required Human fact fields."""

    keys = (
        UnresolvedKey.PROJECT_NAME,
        UnresolvedKey.CANONICAL_REPOSITORY,
        UnresolvedKey.PROJECT_OBJECTIVE,
        UnresolvedKey.CURRENT_STATUS,
        UnresolvedKey.HUMAN_OBJECTIVE,
        UnresolvedKey.CONSTRAINTS,
        UnresolvedKey.WORK_FOCUS_KIND,
        UnresolvedKey.WORK_FOCUS,
    )
    items: list[UnresolvedItem] = []
    for key in keys:
        fact = getattr(facts, _field_name(key))
        if isinstance(fact, UnresolvedFact):
            items.append(UnresolvedItem(key=key, reason=fact.reason))
    return tuple(items)


def _field_name(key: UnresolvedKey) -> str:
    return {
        UnresolvedKey.PROJECT_NAME: "project_name",
        UnresolvedKey.CANONICAL_REPOSITORY: "canonical_repository",
        UnresolvedKey.PROJECT_OBJECTIVE: "project_objective",
        UnresolvedKey.CURRENT_STATUS: "current_status",
        UnresolvedKey.HUMAN_OBJECTIVE: "human_objective",
        UnresolvedKey.CONSTRAINTS: "constraints",
        UnresolvedKey.WORK_FOCUS_KIND: "work_focus_kind",
        UnresolvedKey.WORK_FOCUS: "work_focus",
    }[key]


def _require_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(UTC)


def _is_json_value(value: Any) -> bool:
    if value is None or type(value) in {str, bool, int}:
        return True
    if type(value) is float:
        return math.isfinite(value)
    if type(value) is list:
        return all(_is_json_value(item) for item in cast(list[Any], value))
    if type(value) is dict:
        values = cast(dict[Any, Any], value)
        return all(type(key) is str and _is_json_value(item) for key, item in values.items())
    return False
