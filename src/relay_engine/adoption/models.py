"""Typed immutable plans and records for B2 existing-project adoption."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from relay_engine.bootstrap_discovery.intake_models import (
    ConstraintAnswer,
    ContextReference,
    WorkFocusKind,
)
from relay_engine.bootstrap_discovery.models import (
    ConfiguredRemote,
    RelayContractObservation,
)
from relay_engine.domain import (
    ActorRef,
    AdoptionId,
    BaselineId,
    ContentDigest,
    OperationalHistoryEpochId,
    ProjectId,
    RepositoryId,
    RepositoryRef,
    SliceId,
)
from relay_engine.domain._base import DomainModel, require_nonblank


class AdoptionModel(DomainModel):
    """Strict immutable base for B2 values."""


class AdoptionFingerprintV1(AdoptionModel):
    """Complete B0-F state subset used for the reviewed repository fingerprint."""

    repository_root: str = Field(min_length=1)
    head_sha: str = Field(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
    branch: str | None
    detached_head: bool
    dirty: bool
    tracked_file_count: int = Field(ge=0)
    remotes: tuple[ConfiguredRemote, ...]
    relay_contract: RelayContractObservation

    @model_validator(mode="after")
    def branch_matches_detached_state(self) -> AdoptionFingerprintV1:
        if self.detached_head != (self.branch is None):
            raise ValueError("branch and detached-head state disagree")
        if self.remotes != tuple(sorted(self.remotes, key=lambda item: item.name)):
            raise ValueError("fingerprint remotes must be ordered by name")
        return self


class AdoptionDriftV1(AdoptionModel):
    """One deterministic report section that changed since B1 intake."""

    pointer: str = Field(min_length=1)
    before_sha256: ContentDigest
    after_sha256: ContentDigest
    changed_item_count: int = Field(ge=1)


class AdoptionPlanV1(AdoptionModel):
    """Exact in-memory Human-reviewed adoption proposal; not yet operational state."""

    schema_version: Literal[1] = 1
    manifest_sha256: ContentDigest
    input_report_sha256: ContentDigest
    fresh_report_sha256: ContentDigest
    fresh_report_state_sha256: ContentDigest
    fresh_repository_fingerprint_sha256: ContentDigest
    fresh_fingerprint: AdoptionFingerprintV1
    repository: RepositoryRef
    project_id: ProjectId
    baseline_id: BaselineId
    initial_slice_id: SliceId
    adoption_id: AdoptionId
    epoch_id: OperationalHistoryEpochId
    project_name: str = Field(min_length=1)
    project_objective: str = Field(min_length=1)
    current_status: str = Field(min_length=1)
    human_objective: str = Field(min_length=1)
    constraints: ConstraintAnswer
    work_focus_kind: WorkFocusKind
    work_focus: str = Field(min_length=1)
    context_references: tuple[ContextReference, ...]
    drift: tuple[AdoptionDriftV1, ...]

    @field_validator(
        "project_name",
        "project_objective",
        "current_status",
        "human_objective",
        "work_focus",
    )
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def plan_bindings_are_consistent(self) -> AdoptionPlanV1:
        if self.fresh_repository_fingerprint_sha256 != fingerprint_digest(self.fresh_fingerprint):
            raise ValueError("fresh fingerprint digest does not match its value")
        if self.fresh_fingerprint.dirty:
            raise ValueError("an adoption plan cannot be prepared for a dirty repository")
        if self.repository.host != self.repository.host.lower():
            raise ValueError("canonical RepositoryRef host must be lowercase")
        if self.context_references != tuple(
            sorted(
                self.context_references,
                key=lambda item: (item.relative_path, item.report_pointer),
            )
        ):
            raise ValueError("context references must remain in B1 canonical order")
        if self.drift != tuple(sorted(self.drift, key=lambda item: item.pointer)):
            raise ValueError("drift entries must be sorted by report pointer")
        return self


class ProjectAdoptionRecordV1(AdoptionModel):
    """Immutable record of the exact Human decision that established Project T1."""

    schema_version: Literal[1] = 1
    adoption_id: AdoptionId
    project_id: ProjectId
    repository_id: RepositoryId
    repository: RepositoryRef
    t1: datetime
    human_actor: ActorRef
    manifest_sha256: ContentDigest
    input_report_sha256: ContentDigest
    fresh_report_sha256: ContentDigest
    fresh_report_state_sha256: ContentDigest
    fresh_repository_fingerprint: AdoptionFingerprintV1
    fresh_repository_fingerprint_sha256: ContentDigest
    post_adopt_report_sha256: ContentDigest
    post_adopt_report_state_sha256: ContentDigest
    post_adopt_fingerprint_sha256: ContentDigest
    baseline_id: BaselineId
    initial_slice_id: SliceId
    project_name: str = Field(min_length=1)
    project_objective: str = Field(min_length=1)
    current_status: str = Field(min_length=1)
    human_objective: str = Field(min_length=1)
    constraints: ConstraintAnswer
    work_focus_kind: WorkFocusKind
    work_focus: str = Field(min_length=1)
    context_references: tuple[ContextReference, ...]
    drift: tuple[AdoptionDriftV1, ...]
    attestation_id: Literal["B2_PRE_T1_EXISTENCE_ATTESTATION_V1"]
    attestation_statement: str = Field(min_length=1)
    recorded_at: datetime
    record_digest: ContentDigest

    @field_validator("t1", "recorded_at")
    @classmethod
    def timestamps_are_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("adoption timestamps must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator(
        "project_name",
        "project_objective",
        "current_status",
        "human_objective",
        "work_focus",
        "attestation_statement",
    )
    @classmethod
    def record_text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def adoption_record_is_bound(self) -> ProjectAdoptionRecordV1:
        if self.repository.id != self.repository_id:
            raise ValueError("repository ID disagrees with exact RepositoryRef")
        if self.recorded_at != self.t1:
            raise ValueError("adoption record time must be the exact Human decision time")
        if self.human_actor.kind.value != "HUMAN":
            raise ValueError("adoption requires a Human actor")
        if self.fresh_repository_fingerprint_sha256 != fingerprint_digest(
            self.fresh_repository_fingerprint
        ):
            raise ValueError("stored fresh fingerprint digest does not match its value")
        if self.fresh_report_state_sha256 != self.post_adopt_report_state_sha256:
            raise ValueError("post-ADOPT report state must match the reviewed report state")
        if self.fresh_repository_fingerprint_sha256 != self.post_adopt_fingerprint_sha256:
            raise ValueError("post-ADOPT fingerprint must match the reviewed fingerprint")
        expected = adoption_record_digest(self)
        if self.record_digest != expected:
            raise ValueError("adoption record digest does not match its canonical payload")
        return self


def adoption_record_digest(value: ProjectAdoptionRecordV1) -> str:
    """Return the canonical digest for an adoption record, excluding its digest field."""

    payload = value.model_dump(mode="json", exclude={"record_digest"})
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def build_adoption_record(**values: object) -> ProjectAdoptionRecordV1:
    """Build a validated adoption record with its canonical digest."""

    payload = {"schema_version": 1, **values}
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    ).encode("utf-8")
    payload["record_digest"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
    return ProjectAdoptionRecordV1.model_validate(payload)


def fingerprint_digest(value: AdoptionFingerprintV1) -> str:
    """Hash a complete canonical repository fingerprint."""

    encoded = json.dumps(
        value.model_dump(mode="json"),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def digest_json_value(value: object) -> str:
    """Hash a JSON-compatible value with deterministic B0-F canonical encoding."""

    encoded = json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _json_default(value: object) -> object:
    if isinstance(value, datetime):
        normalized = value.astimezone(UTC)
        return normalized.isoformat().replace("+00:00", "Z")
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, StrEnum):
        return value.value
    raise TypeError(f"value is not JSON serializable: {type(value).__name__}")


__all__ = [
    "AdoptionDriftV1",
    "AdoptionFingerprintV1",
    "AdoptionPlanV1",
    "ProjectAdoptionRecordV1",
    "adoption_record_digest",
    "build_adoption_record",
    "digest_json_value",
    "fingerprint_digest",
]
