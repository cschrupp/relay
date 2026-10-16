"""Typed, immutable operational-origin and history-epoch evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal, cast

from pydantic import BaseModel, Field, field_validator, model_validator

from relay_engine.domain._base import (
    DomainModel,
    require_nonblank,
    require_repository_relative_path,
)
from relay_engine.domain.ids import (
    ArtifactId,
    OperationalHistoryEpochId,
    OperationalOriginRecordId,
    ProjectId,
    SliceId,
)
from relay_engine.domain.models import ContentDigest
from relay_engine.domain.references import ActorKind, ActorRef, CommitRef
from relay_engine.project_slice.models import (
    DefinitionOperation,
    ProjectDefinitionRevision,
    SliceDefinitionRevision,
)
from relay_engine.repository_contract.models import (
    RepositoryArtifactClass,
    RepositoryArtifactState,
)


class OperationalOrigin(StrEnum):
    """The two valid durable origin classifications."""

    PRE_GENESIS = "PRE_GENESIS"
    NATIVE_RELAY = "NATIVE_RELAY"


class OriginSubjectType(StrEnum):
    """Entity type carrying an independent origin assertion."""

    PROJECT = "PROJECT"
    SLICE = "SLICE"


class OriginRecordKind(StrEnum):
    """Append-only origin-chain record kind."""

    INITIAL = "INITIAL"
    CORRECTION = "CORRECTION"


class OriginResolutionState(StrEnum):
    """Read-time result; NOT_ESTABLISHED is never persisted as an origin."""

    ESTABLISHED = "ESTABLISHED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


class OriginDiagnosticCode(StrEnum):
    """Fail-closed causes retained for read-only diagnostics."""

    EPOCH_NOT_ESTABLISHED = "EPOCH_NOT_ESTABLISHED"
    NO_ORIGIN_RECORD = "NO_ORIGIN_RECORD"
    INVALID_ORIGIN_RECORD = "INVALID_ORIGIN_RECORD"
    INVALID_PROOF = "INVALID_PROOF"
    INVALID_CREATION_REFERENCE = "INVALID_CREATION_REFERENCE"
    INVALID_CORRECTION_AUTHORITY = "INVALID_CORRECTION_AUTHORITY"
    INVALID_ORIGIN_CHAIN = "INVALID_ORIGIN_CHAIN"
    PROJECT_ORIGIN_NOT_ESTABLISHED = "PROJECT_ORIGIN_NOT_ESTABLISHED"
    HIERARCHY_CONFLICT = "HIERARCHY_CONFLICT"


def _canonical_digest(value: object) -> str:
    def json_ready(item: Any) -> Any:
        if isinstance(item, BaseModel):
            return item.model_dump(mode="json")
        if isinstance(item, dict):
            mapping = cast(dict[str, Any], item)
            return {key: json_ready(nested) for key, nested in mapping.items()}
        if isinstance(item, (tuple, list)):
            sequence = cast(tuple[Any, ...] | list[Any], item)
            return [json_ready(nested) for nested in sequence]
        if isinstance(item, StrEnum):
            return item.value
        if isinstance(item, datetime):
            return item.astimezone(UTC).isoformat().replace("+00:00", "Z")
        return item

    encoded = json.dumps(
        json_ready(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def operational_history_epoch_digest(value: OperationalHistoryEpochV1) -> str:
    """Return the canonical digest for an epoch, excluding its digest field."""

    return _canonical_digest(value.model_dump(mode="json", exclude={"epoch_digest"}))


def operational_origin_record_digest(value: OperationalOriginRecordV1) -> str:
    """Return the canonical digest for an origin record, excluding its digest field."""

    return _canonical_digest(value.model_dump(mode="json", exclude={"record_digest"}))


def definition_payload_digest(value: BaseModel) -> str:
    """Return the canonical digest used to bind an origin to a CREATE payload."""

    return _canonical_digest(value.model_dump(mode="json"))


class OperationalHistoryEpochV1(DomainModel):
    """The single immutable database-wide operational-history cut and trust anchor."""

    schema_version: Literal[1] = 1
    epoch_id: OperationalHistoryEpochId
    genesis_cut_at: datetime
    source_commit: CommitRef
    genesis_package_artifact_id: ArtifactId
    genesis_package_path: str
    genesis_package_digest: ContentDigest
    package_acceptance_artifact_id: ArtifactId
    package_acceptance_digest: ContentDigest
    recorded_at: datetime
    epoch_digest: ContentDigest

    @field_validator("genesis_cut_at", "recorded_at")
    @classmethod
    def timestamps_are_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("epoch timestamps must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("genesis_package_path")
    @classmethod
    def package_path_is_relative(cls, value: str) -> str:
        return require_repository_relative_path(value)

    @model_validator(mode="after")
    def epoch_is_internally_valid(self) -> OperationalHistoryEpochV1:
        if self.recorded_at < self.genesis_cut_at:
            raise ValueError("epoch assertion cannot predate its genesis cut")
        if self.epoch_digest != operational_history_epoch_digest(self):
            raise ValueError("epoch digest does not match its canonical payload")
        return self


def build_operational_history_epoch(**values: object) -> OperationalHistoryEpochV1:
    """Build an epoch with its deterministic digest from validated fields."""

    payload = {"schema_version": 1, **values}
    payload["epoch_digest"] = _canonical_digest(payload)
    return OperationalHistoryEpochV1.model_validate(payload)


class JsonPointerSourceLocatorV1(DomainModel):
    """Exact structured-source locator for one asserted field."""

    locator_type: Literal["JSON_POINTER"]
    pointer: str = Field(min_length=1)

    @field_validator("pointer")
    @classmethod
    def pointer_is_exact(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("JSON Pointer locator must identify an exact field")
        return value


class DocumentBlockSourceLocatorV1(DomainModel):
    """Heading and paragraph/block locator for a pinned document source."""

    locator_type: Literal["DOCUMENT_BLOCK"]
    heading_path: tuple[str, ...] = Field(min_length=1)
    paragraph_locator: str = Field(min_length=1)

    @field_validator("heading_path")
    @classmethod
    def heading_components_are_nonblank(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for part in value:
            require_nonblank(part)
        return value

    @field_validator("paragraph_locator")
    @classmethod
    def paragraph_locator_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)


type OriginSourceLocatorV1 = Annotated[
    JsonPointerSourceLocatorV1 | DocumentBlockSourceLocatorV1,
    Field(discriminator="locator_type"),
]


class PreGenesisOriginProofV1(DomainModel):
    """Pinned, field-locatable evidence that this exact subject existed before T1."""

    proof_type: Literal["PRE_GENESIS"]
    subject_type: OriginSubjectType
    subject_id: ProjectId | SliceId
    source_commit: CommitRef
    source_artifact_id: ArtifactId
    source_path: str
    source_content_digest: ContentDigest
    source_artifact_class: RepositoryArtifactClass
    source_artifact_state: RepositoryArtifactState
    locator: OriginSourceLocatorV1
    assertion: Literal["SUBJECT_EXISTED_BEFORE_T1"]
    package_acceptance_artifact_id: ArtifactId
    package_acceptance_digest: ContentDigest

    @field_validator("source_path")
    @classmethod
    def source_path_is_relative(cls, value: str) -> str:
        return require_repository_relative_path(value)

    @model_validator(mode="after")
    def subject_and_source_are_exact(self) -> PreGenesisOriginProofV1:
        expected_prefix = "prj_" if self.subject_type is OriginSubjectType.PROJECT else "slc_"
        if not self.subject_id.startswith(expected_prefix):
            raise ValueError("origin proof subject ID disagrees with its discriminator")
        qualified = (
            self.source_artifact_class is RepositoryArtifactClass.LOCKABLE_RECORD
            and self.source_artifact_state is RepositoryArtifactState.LOCKED
        ) or (
            self.source_artifact_class is RepositoryArtifactClass.IMMUTABLE_RECORD
            and self.source_artifact_state is RepositoryArtifactState.IMMUTABLE
        )
        if not qualified:
            raise ValueError("PRE_GENESIS evidence must be a locked or immutable record")
        return self


class NativeRelayOriginProofV1(DomainModel):
    """Exact post-T1 CREATE revision that established NATIVE_RELAY origin."""

    proof_type: Literal["NATIVE_RELAY"]
    subject_type: OriginSubjectType
    subject_id: ProjectId | SliceId
    definition_revision: Literal[1]
    operation: Literal["CREATE"]
    creation_payload_digest: ContentDigest
    actor: ActorRef
    created_at: datetime
    reason: str = Field(min_length=1)

    @field_validator("created_at")
    @classmethod
    def creation_time_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("creation timestamp must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("reason")
    @classmethod
    def reason_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def subject_and_actor_are_valid(self) -> NativeRelayOriginProofV1:
        expected_prefix = "prj_" if self.subject_type is OriginSubjectType.PROJECT else "slc_"
        if not self.subject_id.startswith(expected_prefix):
            raise ValueError("origin proof subject ID disagrees with its discriminator")
        if self.actor.kind is not ActorKind.HUMAN:
            raise ValueError("NATIVE_RELAY creation requires the normal Human creation actor")
        return self


type OperationalOriginProofV1 = Annotated[
    PreGenesisOriginProofV1 | NativeRelayOriginProofV1,
    Field(discriminator="proof_type"),
]


class OperationalHistoryEpochResolution(DomainModel):
    """Read-only result of validating the database-wide epoch anchor."""

    state: OriginResolutionState
    epoch: OperationalHistoryEpochV1 | None
    diagnostic: OriginDiagnosticCode | None
    record_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def state_matches_payload(self) -> OperationalHistoryEpochResolution:
        if (self.state is OriginResolutionState.ESTABLISHED) != (
            self.epoch is not None and self.diagnostic is None
        ):
            raise ValueError("epoch resolution state and payload disagree")
        return self


class OperationalOriginRecordV1(DomainModel):
    """One append-only initial origin or exact supersession assertion."""

    schema_version: Literal[1] = 1
    record_id: OperationalOriginRecordId
    subject_type: OriginSubjectType
    subject_id: ProjectId | SliceId
    project_id: ProjectId
    record_kind: OriginRecordKind
    origin: OperationalOrigin
    epoch_id: OperationalHistoryEpochId
    epoch_digest: ContentDigest
    proof: OperationalOriginProofV1
    recorded_at: datetime
    recorded_by: ActorRef
    establishing_authority_id: str = Field(min_length=1)
    supersedes_record_id: OperationalOriginRecordId | None = None
    supersedes_record_digest: ContentDigest | None = None
    correction_authorization_id: str | None = None
    correction_authorization_digest: ContentDigest | None = None
    rationale: str | None = None
    record_digest: ContentDigest

    @field_validator("recorded_at")
    @classmethod
    def recorded_at_is_aware_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("origin timestamp must be timezone-aware")
        return value.astimezone(UTC)

    @field_validator("establishing_authority_id")
    @classmethod
    def authority_reference_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def record_contract_is_valid(self) -> OperationalOriginRecordV1:
        expected_prefix = "prj_" if self.subject_type is OriginSubjectType.PROJECT else "slc_"
        if not self.subject_id.startswith(expected_prefix):
            raise ValueError("origin record subject ID disagrees with its discriminator")
        if self.proof.proof_type != self.origin.value:
            raise ValueError("origin record value and proof discriminator disagree")
        if (
            self.proof.subject_type is not self.subject_type
            or self.proof.subject_id != self.subject_id
        ):
            raise ValueError("origin proof is bound to a different subject")
        if self.record_kind is OriginRecordKind.INITIAL:
            if (
                self.supersedes_record_id is not None
                or self.supersedes_record_digest is not None
                or self.correction_authorization_id is not None
                or self.correction_authorization_digest is not None
                or self.rationale is not None
            ):
                raise ValueError("initial origin records cannot carry correction fields")
            if isinstance(self.proof, NativeRelayOriginProofV1) and (
                self.recorded_at != self.proof.created_at or self.recorded_by != self.proof.actor
            ):
                raise ValueError("NATIVE_RELAY record must match its exact creation actor/time")
        else:
            if (
                self.supersedes_record_id is None
                or self.supersedes_record_digest is None
                or self.correction_authorization_id is None
                or self.correction_authorization_digest is None
                or self.rationale is None
            ):
                raise ValueError("correction records require exact predecessor and Human authority")
            if self.recorded_by.kind is not ActorKind.HUMAN:
                raise ValueError("origin correction requires a HUMAN actor")
            require_nonblank(self.correction_authorization_id)
            require_nonblank(self.rationale)
        if self.record_digest != operational_origin_record_digest(self):
            raise ValueError("origin record digest does not match its canonical payload")
        return self


class OperationalOriginDiagnostic(DomainModel):
    """Safe, read-only explanation of why origin could not be established."""

    code: OriginDiagnosticCode
    message: str = Field(min_length=1)
    record_ids: tuple[OperationalOriginRecordId, ...] = ()


class OperationalOriginResolution(DomainModel):
    """Read-time origin result; NOT ESTABLISHED is a diagnostic, not an enum value."""

    subject_type: OriginSubjectType
    subject_id: ProjectId | SliceId
    state: OriginResolutionState
    origin: OperationalOrigin | None
    record: OperationalOriginRecordV1 | None
    epoch: OperationalHistoryEpochV1 | None
    diagnostic: OperationalOriginDiagnostic | None

    @model_validator(mode="after")
    def resolution_is_unambiguous(self) -> OperationalOriginResolution:
        established = self.state is OriginResolutionState.ESTABLISHED
        if established != (
            self.origin is not None and self.record is not None and self.diagnostic is None
        ):
            raise ValueError("origin resolution state and payload disagree")
        if established and (self.record is None or self.record.origin is not self.origin):
            raise ValueError("effective origin record disagrees with resolved origin")
        if not established and self.diagnostic is None:
            raise ValueError("unestablished origin requires an explicit diagnostic")
        if self.record is not None and (
            self.record.subject_type is not self.subject_type
            or self.record.subject_id != self.subject_id
        ):
            raise ValueError("resolved origin record belongs to a different subject")
        return self


def build_operational_origin_record(**values: object) -> OperationalOriginRecordV1:
    """Build an origin record with its deterministic canonical payload digest."""

    payload = {
        "schema_version": 1,
        "supersedes_record_id": None,
        "supersedes_record_digest": None,
        "correction_authorization_id": None,
        "correction_authorization_digest": None,
        "rationale": None,
        **values,
    }
    payload["record_digest"] = _canonical_digest(payload)
    return OperationalOriginRecordV1.model_validate(payload)


def epoch_resolution_not_established(
    code: OriginDiagnosticCode,
    record_ids: tuple[str, ...] = (),
) -> OperationalHistoryEpochResolution:
    """Construct a consistent epoch diagnostic result."""

    return OperationalHistoryEpochResolution(
        state=OriginResolutionState.NOT_ESTABLISHED,
        epoch=None,
        diagnostic=code,
        record_ids=record_ids,
    )


def origin_resolution_not_established(
    subject_type: OriginSubjectType,
    subject_id: ProjectId | SliceId,
    epoch: OperationalHistoryEpochV1 | None,
    code: OriginDiagnosticCode,
    message: str,
    record_ids: tuple[OperationalOriginRecordId, ...] = (),
) -> OperationalOriginResolution:
    """Construct a consistent per-subject origin diagnostic result."""

    return OperationalOriginResolution(
        subject_type=subject_type,
        subject_id=subject_id,
        state=OriginResolutionState.NOT_ESTABLISHED,
        origin=None,
        record=None,
        epoch=epoch,
        diagnostic=OperationalOriginDiagnostic(
            code=code,
            message=message,
            record_ids=record_ids,
        ),
    )


def resolve_origin_chain(
    records: tuple[OperationalOriginRecordV1, ...],
    *,
    subject_type: OriginSubjectType,
    subject_id: ProjectId | SliceId,
    project_id: ProjectId,
    epoch_resolution: OperationalHistoryEpochResolution,
    creation_revision: ProjectDefinitionRevision | SliceDefinitionRevision | None,
) -> OperationalOriginResolution:
    """Validate one exact origin chain against its epoch and creation evidence."""

    epoch = epoch_resolution.epoch
    if epoch_resolution.state is not OriginResolutionState.ESTABLISHED or epoch is None:
        return origin_resolution_not_established(
            subject_type,
            subject_id,
            None,
            OriginDiagnosticCode.EPOCH_NOT_ESTABLISHED,
            "The database-wide operational-history epoch is not established.",
            tuple(record.record_id for record in records),
        )
    if not records:
        return origin_resolution_not_established(
            subject_type,
            subject_id,
            epoch,
            OriginDiagnosticCode.NO_ORIGIN_RECORD,
            "No durable operational-origin record exists for this subject.",
        )

    record_ids = {record.record_id for record in records}
    if len(record_ids) != len(records):
        return origin_resolution_not_established(
            subject_type,
            subject_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
            "Origin record identities are ambiguous.",
            tuple(record.record_id for record in records),
        )

    by_id = {record.record_id: record for record in records}
    roots: list[OperationalOriginRecordV1] = []
    successors: dict[OperationalOriginRecordId, OperationalOriginRecordV1] = {}
    for record in records:
        if (
            record.subject_type is not subject_type
            or record.subject_id != subject_id
            or record.project_id != project_id
            or record.epoch_id != epoch.epoch_id
            or record.epoch_digest != epoch.epoch_digest
            or record.recorded_at < epoch.genesis_cut_at
            or record.record_digest != operational_origin_record_digest(record)
        ):
            return origin_resolution_not_established(
                subject_type,
                subject_id,
                epoch,
                OriginDiagnosticCode.INVALID_ORIGIN_RECORD,
                "An origin record identity, digest, project, or epoch binding is invalid.",
                tuple(item.record_id for item in records),
            )
        if record.record_kind is OriginRecordKind.INITIAL:
            roots.append(record)
        else:
            predecessor = by_id.get(record.supersedes_record_id or "")
            if (
                predecessor is None
                or predecessor.record_digest != record.supersedes_record_digest
                or predecessor.subject_type is not record.subject_type
                or predecessor.subject_id != record.subject_id
            ):
                return origin_resolution_not_established(
                    subject_type,
                    subject_id,
                    epoch,
                    OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
                    "A correction references a missing, stale, or different-subject predecessor.",
                    tuple(item.record_id for item in records),
                )
            if predecessor.record_id in successors:
                return origin_resolution_not_established(
                    subject_type,
                    subject_id,
                    epoch,
                    OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
                    "An origin record has multiple correction successors.",
                    tuple(item.record_id for item in records),
                )
            successors[predecessor.record_id] = record

        proof = record.proof
        if isinstance(proof, PreGenesisOriginProofV1):
            if (
                proof.source_commit != epoch.source_commit
                or proof.package_acceptance_artifact_id != epoch.package_acceptance_artifact_id
                or proof.package_acceptance_digest != epoch.package_acceptance_digest
                or record.establishing_authority_id != proof.package_acceptance_artifact_id
                or record.recorded_by.kind is not ActorKind.HUMAN
            ):
                return origin_resolution_not_established(
                    subject_type,
                    subject_id,
                    epoch,
                    OriginDiagnosticCode.INVALID_PROOF,
                    "PRE_GENESIS proof is not bound to the accepted pinned source and package.",
                    tuple(item.record_id for item in records),
                )
        else:
            expected_reference = f"{subject_type.value.lower()}_definition_revisions/{subject_id}/1"
            if (
                proof.created_at <= epoch.genesis_cut_at
                or record.establishing_authority_id != expected_reference
                or creation_revision is None
                or not _native_proof_matches_revision(proof, creation_revision)
            ):
                return origin_resolution_not_established(
                    subject_type,
                    subject_id,
                    epoch,
                    OriginDiagnosticCode.INVALID_CREATION_REFERENCE,
                    "NATIVE_RELAY proof does not match an exact post-T1 CREATE revision.",
                    tuple(item.record_id for item in records),
                )

    if len(roots) != 1:
        return origin_resolution_not_established(
            subject_type,
            subject_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
            "An established subject must have exactly one initial origin record.",
            tuple(item.record_id for item in records),
        )

    visited: set[OperationalOriginRecordId] = set()
    current = roots[0]
    while current.record_id not in visited:
        visited.add(current.record_id)
        successor = successors.get(current.record_id)
        if successor is None:
            break
        current = successor
    if len(visited) != len(records):
        return origin_resolution_not_established(
            subject_type,
            subject_id,
            epoch,
            OriginDiagnosticCode.INVALID_ORIGIN_CHAIN,
            "Origin history is cyclic, branched, or disconnected.",
            tuple(item.record_id for item in records),
        )
    if current.record_kind is OriginRecordKind.CORRECTION:
        return origin_resolution_not_established(
            subject_type,
            subject_id,
            epoch,
            OriginDiagnosticCode.INVALID_CORRECTION_AUTHORITY,
            "Origin correction authority is unavailable under the accepted PG1 surface.",
            tuple(item.record_id for item in records),
        )

    return OperationalOriginResolution(
        subject_type=subject_type,
        subject_id=subject_id,
        state=OriginResolutionState.ESTABLISHED,
        origin=current.origin,
        record=current,
        epoch=epoch,
        diagnostic=None,
    )


def _native_proof_matches_revision(
    proof: NativeRelayOriginProofV1,
    revision: ProjectDefinitionRevision | SliceDefinitionRevision,
) -> bool:
    if (
        revision.definition_revision != 1
        or revision.operation is not DefinitionOperation.CREATE
        or revision.payload is None
        or revision.mutation is None
    ):
        return False
    actual_subject_id = (
        revision.project_id
        if isinstance(revision, ProjectDefinitionRevision)
        else revision.slice_id
    )
    payload_digest = _canonical_digest(revision.payload.model_dump(mode="json"))
    return (
        actual_subject_id == proof.subject_id
        and proof.subject_type
        is (
            OriginSubjectType.PROJECT
            if isinstance(revision, ProjectDefinitionRevision)
            else OriginSubjectType.SLICE
        )
        and payload_digest == proof.creation_payload_digest
        and revision.mutation.actor == proof.actor
        and revision.mutation.occurred_at == proof.created_at
        and revision.mutation.reason == proof.reason
    )


__all__ = [
    "DocumentBlockSourceLocatorV1",
    "JsonPointerSourceLocatorV1",
    "OperationalHistoryEpochResolution",
    "OperationalHistoryEpochV1",
    "OperationalOrigin",
    "OperationalOriginDiagnostic",
    "OperationalOriginProofV1",
    "OperationalOriginRecordV1",
    "OperationalOriginResolution",
    "OriginDiagnosticCode",
    "OriginRecordKind",
    "OriginResolutionState",
    "OriginSubjectType",
    "PreGenesisOriginProofV1",
    "NativeRelayOriginProofV1",
    "build_operational_history_epoch",
    "build_operational_origin_record",
    "definition_payload_digest",
    "epoch_resolution_not_established",
    "operational_history_epoch_digest",
    "operational_origin_record_digest",
    "origin_resolution_not_established",
    "resolve_origin_chain",
]
