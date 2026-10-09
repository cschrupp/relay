"""Relay-owned immutable values for runtime observation and execution requests."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any, cast

from pydantic import AfterValidator, Field, StringConstraints, field_validator, model_validator

from relay_engine.domain import (
    BaselineId,
    CommitRef,
    ContentDigest,
    ExecutionId,
    RepositoryRef,
    SliceId,
)
from relay_engine.domain._base import DomainModel, require_nonblank

type RuntimeIdentifier = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=128),
    AfterValidator(require_nonblank),
]
type RuntimeText = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=200_000),
    AfterValidator(require_nonblank),
]
type SafeSummary = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=512),
    AfterValidator(require_nonblank),
]
_SAFE_KEY = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_SECRET_TEXT = re.compile(
    r"(?i)\b(bearer\s+)[^\s,;]+|\b(api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)"
    r"(\s*[:=]\s*)[^\s,;]+"
)


def _normalize_timestamp(value: datetime) -> datetime:
    """Require an aware timestamp and represent it in UTC."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return value.astimezone(UTC)


def _normalize_safe_text(value: str) -> str:
    """Bound and redact credential-like text before retaining it as a summary."""

    redacted = _SECRET_TEXT.sub("[redacted]", value)
    redacted = "".join(character for character in redacted if character.isprintable())
    bounded = redacted[:512]
    return require_nonblank(bounded)


class RuntimeCapability(StrEnum):
    """A runtime operation that an adapter can explicitly provide."""

    SESSION_CREATE = "SESSION_CREATE"
    EXECUTE = "EXECUTE"
    EVENT_STREAM = "EVENT_STREAM"
    CANCEL = "CANCEL"
    RESULT_INSPECTION = "RESULT_INSPECTION"
    RESUME = "RESUME"
    STEER = "STEER"
    PERMISSION_PROMPTS = "PERMISSION_PROMPTS"
    DIFF_INSPECTION = "DIFF_INSPECTION"
    USAGE_REPORTING = "USAGE_REPORTING"
    ACTUAL_PROVIDER_IDENTITY = "ACTUAL_PROVIDER_IDENTITY"
    ACTUAL_MODEL_IDENTITY = "ACTUAL_MODEL_IDENTITY"
    EVENT_REPLAY = "EVENT_REPLAY"
    NATIVE_WORKTREE = "NATIVE_WORKTREE"


class RuntimeStatus(StrEnum):
    """Runtime-reported state, separate from Relay lifecycle state."""

    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


class RuntimeEventType(StrEnum):
    """Stable Relay vocabulary for runtime observations."""

    EXECUTION_STARTED = "EXECUTION_STARTED"
    PROGRESS = "PROGRESS"
    TOOL_REQUESTED = "TOOL_REQUESTED"
    TOOL_COMPLETED = "TOOL_COMPLETED"
    PERMISSION_REQUIRED = "PERMISSION_REQUIRED"
    EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
    EXECUTION_IDLE = "EXECUTION_IDLE"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_CANCELLED = "EXECUTION_CANCELLED"
    EVENT_GAP = "EVENT_GAP"


class RuntimeContinuityState(StrEnum):
    """Completeness of the runtime event observation channel."""

    COMPLETE = "COMPLETE"
    LIVE_ONLY = "LIVE_ONLY"
    INCOMPLETE = "INCOMPLETE"


class RuntimeContinuityReason(StrEnum):
    """Known reasons why runtime event continuity is incomplete."""

    BUFFER_OVERFLOW = "BUFFER_OVERFLOW"
    STREAM_DISCONNECTED = "STREAM_DISCONNECTED"
    EVENT_ATTRIBUTION = "EVENT_ATTRIBUTION"
    OBSERVATION_UNAVAILABLE = "OBSERVATION_UNAVAILABLE"


class RuntimeFailureCategory(StrEnum):
    """Stable, safe categories for adapter failures."""

    UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
    UNSUPPORTED_RUNTIME_VERSION = "UNSUPPORTED_RUNTIME_VERSION"
    REQUEST_CONFLICT = "REQUEST_CONFLICT"
    CONFIGURATION = "CONFIGURATION"
    AUTHENTICATION = "AUTHENTICATION"
    PROVIDER_MODEL = "PROVIDER_MODEL"
    RUNTIME_UNAVAILABLE = "RUNTIME_UNAVAILABLE"
    WORKSPACE_ACCESS = "WORKSPACE_ACCESS"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    EVENT_CONTINUITY = "EVENT_CONTINUITY"
    EVENT_OBSERVATION_UNAVAILABLE = "EVENT_OBSERVATION_UNAVAILABLE"
    EVENT_ATTRIBUTION = "EVENT_ATTRIBUTION"
    SESSION_BINDING_REQUIRED = "SESSION_BINDING_REQUIRED"
    TIMEOUT = "TIMEOUT"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    CANCELLED = "CANCELLED"
    AGENT_BLOCKED = "AGENT_BLOCKED"
    RESULT_INSPECTION = "RESULT_INSPECTION"
    TRANSPORT = "TRANSPORT"
    INTERNAL = "INTERNAL"


class RuntimeControlAckState(StrEnum):
    """Result of an idempotent runtime control request."""

    REQUESTED = "REQUESTED"
    ALREADY_TERMINAL = "ALREADY_TERMINAL"
    NOT_FOUND = "NOT_FOUND"
    DENIED = "DENIED"


class RuntimeIdentityCompleteness(StrEnum):
    """Whether actual runtime identity fields were exposed by the runtime."""

    FULL = "FULL"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class RuntimeDescriptor(DomainModel):
    """Adapter identity, compatibility profile, and supported capabilities."""

    runtime_id: RuntimeIdentifier
    adapter_version: RuntimeIdentifier
    runtime_version: RuntimeIdentifier | None
    api_generation: RuntimeIdentifier
    capabilities: tuple[RuntimeCapability, ...]

    @field_validator("capabilities")
    @classmethod
    def capabilities_are_unique(
        cls, value: tuple[RuntimeCapability, ...]
    ) -> tuple[RuntimeCapability, ...]:
        if len(set(value)) != len(value):
            raise ValueError("capabilities must not contain duplicates")
        return value


class RuntimeSessionRef(DomainModel):
    """Opaque runtime-native session identity namespaced by runtime."""

    runtime_id: RuntimeIdentifier
    session_id: RuntimeIdentifier


class RuntimeInvocationRef(DomainModel):
    """Opaque runtime-native invocation identity, when exposed."""

    runtime_id: RuntimeIdentifier
    session_id: RuntimeIdentifier
    invocation_id: RuntimeIdentifier | None = None


class RuntimeSelection(DomainModel):
    """Requested runtime/provider/model identity locked into an execution basis."""

    runtime_id: RuntimeIdentifier
    requested_provider_id: RuntimeIdentifier
    requested_model_id: RuntimeIdentifier


class RuntimeProvenance(DomainModel):
    """Runtime-reported identity, preserving requested and actual values separately."""

    runtime_id: RuntimeIdentifier
    adapter_version: RuntimeIdentifier
    runtime_version: RuntimeIdentifier | None
    api_generation: RuntimeIdentifier
    requested_provider_id: RuntimeIdentifier
    requested_model_id: RuntimeIdentifier
    actual_provider_id: RuntimeIdentifier | None = None
    actual_model_id: RuntimeIdentifier | None = None
    identity_completeness: RuntimeIdentityCompleteness

    @model_validator(mode="after")
    def completeness_matches_actual_identity(self) -> RuntimeProvenance:
        actual_count = sum(
            value is not None for value in (self.actual_provider_id, self.actual_model_id)
        )
        expected = {
            0: RuntimeIdentityCompleteness.UNKNOWN,
            1: RuntimeIdentityCompleteness.PARTIAL,
            2: RuntimeIdentityCompleteness.FULL,
        }[actual_count]
        if self.identity_completeness is not expected:
            raise ValueError("identity completeness must match exposed actual identities")
        return self


class RuntimeInputAttachmentRef(DomainModel):
    """Opaque, content-bound attachment reference for a finalized input payload."""

    reference_id: RuntimeIdentifier
    content_digest: ContentDigest
    media_type: RuntimeIdentifier | None = None


class RuntimeWorkspaceAttachment(DomainModel):
    """Relay-supplied exact repository workspace; adapters may not widen it."""

    workspace_id: RuntimeIdentifier
    root: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=2048)]
    repository: RepositoryRef
    source_commit: CommitRef

    @field_validator("root")
    @classmethod
    def root_is_explicit_absolute_path(cls, value: str) -> str:
        require_nonblank(value)
        if not value.startswith("/") or "\\" in value:
            raise ValueError("workspace root must be an absolute POSIX path")
        if any(part in {".", ".."} for part in value.split("/")):
            raise ValueError("workspace root must not contain relative path segments")
        if any(ord(character) < 32 for character in value):
            raise ValueError("workspace root must not contain control characters")
        return value

    @model_validator(mode="after")
    def source_commit_uses_bound_repository(self) -> RuntimeWorkspaceAttachment:
        if self.source_commit.repository != self.repository:
            raise ValueError("source commit repository must match workspace repository")
        return self


class RuntimeInputPayload(DomainModel):
    """Finalized text and attachment references produced outside this runtime slice."""

    text: RuntimeText
    payload_digest: ContentDigest
    attachment_refs: tuple[RuntimeInputAttachmentRef, ...] = ()

    @field_validator("attachment_refs")
    @classmethod
    def attachment_refs_are_unique(
        cls, value: tuple[RuntimeInputAttachmentRef, ...]
    ) -> tuple[RuntimeInputAttachmentRef, ...]:
        identifiers = [attachment.reference_id for attachment in value]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("attachment references must not contain duplicate identifiers")
        return value


class RuntimePermissionProfileRef(DomainModel):
    """Reference to immutable, separately materialized runtime permission policy."""

    profile_id: RuntimeIdentifier
    content_digest: ContentDigest


class CredentialRef(DomainModel):
    """Identifier for externally managed credential material; never contains a secret."""

    credential_id: RuntimeIdentifier


class RuntimeExecutionLimits(DomainModel):
    """Integer-only declared limits that are part of execution request identity."""

    max_duration_seconds: int | None = Field(default=None, strict=True, ge=1)
    max_tool_calls: int | None = Field(default=None, strict=True, ge=1)
    max_output_bytes: int | None = Field(default=None, strict=True, ge=1)


class RuntimeExecutionBasis(DomainModel):
    """Immutable, runtime-neutral inputs whose canonical digest identifies a request."""

    execution_id: ExecutionId
    slice_id: SliceId
    source_baseline_id: BaselineId
    workspace: RuntimeWorkspaceAttachment
    input_payload: RuntimeInputPayload
    runtime_selection: RuntimeSelection
    permission_profile_ref: RuntimePermissionProfileRef
    credential_refs: tuple[CredentialRef, ...] = ()
    required_capabilities: tuple[RuntimeCapability, ...] = ()
    limits: RuntimeExecutionLimits = Field(default_factory=RuntimeExecutionLimits)

    @field_validator("credential_refs")
    @classmethod
    def credential_refs_are_unique(
        cls, value: tuple[CredentialRef, ...]
    ) -> tuple[CredentialRef, ...]:
        identifiers = [reference.credential_id for reference in value]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("credential references must not contain duplicates")
        return value

    @field_validator("required_capabilities")
    @classmethod
    def required_capabilities_are_unique(
        cls, value: tuple[RuntimeCapability, ...]
    ) -> tuple[RuntimeCapability, ...]:
        if len(set(value)) != len(value):
            raise ValueError("required capabilities must not contain duplicates")
        return value


def _contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        values = cast(dict[object, object], value)
        return any(_contains_float(key) or _contains_float(item) for key, item in values.items())
    if isinstance(value, (list, tuple)):
        values = cast(list[Any] | tuple[Any, ...], value)
        return any(_contains_float(item) for item in values)
    return False


def canonical_execution_basis_json(basis: RuntimeExecutionBasis) -> str:
    """Return the exact schema-v1 canonical JSON used by the request digest."""

    values: dict[str, object] = basis.model_dump(mode="json")
    if _contains_float(values):
        raise ValueError("schema-v1 execution basis must not contain floating-point values")
    return json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def digest_execution_basis(basis: RuntimeExecutionBasis) -> ContentDigest:
    """Hash exact canonical schema-v1 bytes using Relay ContentDigest syntax."""

    canonical = canonical_execution_basis_json(basis)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


class RuntimeExecutionRequest(DomainModel):
    """Exact immutable request paired with its independently recomputable digest."""

    basis: RuntimeExecutionBasis
    request_digest: ContentDigest

    @model_validator(mode="after")
    def request_digest_matches_basis(self) -> RuntimeExecutionRequest:
        if self.request_digest != digest_execution_basis(self.basis):
            raise ValueError("request digest does not match execution basis")
        return self


class RuntimeSessionBinding(DomainModel):
    """Process-local proof that one exact runtime session was created for a request."""

    execution_id: ExecutionId
    runtime_session: RuntimeSessionRef
    request_digest: ContentDigest
    workspace_id: RuntimeIdentifier
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def created_at_is_utc(cls, value: datetime) -> datetime:
        return _normalize_timestamp(value)


class RuntimeExecutionHandle(DomainModel):
    """Opaque handle for runtime interaction with an exact request/session binding.

    The handle may also be returned when prompt admission is uncertain, so callers
    can inspect or cancel the exact session without retrying prompt admission.
    """

    execution_id: ExecutionId
    runtime_session: RuntimeSessionRef
    runtime_invocation: RuntimeInvocationRef | None = None
    request_digest: ContentDigest
    opened_at: datetime

    @field_validator("opened_at")
    @classmethod
    def opened_at_is_utc(cls, value: datetime) -> datetime:
        return _normalize_timestamp(value)


class RuntimeEventEnvelope(DomainModel):
    """Safe normalized runtime event with adapter-assigned sequence provenance."""

    execution_id: ExecutionId
    runtime_session: RuntimeSessionRef
    sequence: int = Field(strict=True, ge=1)
    event_type: RuntimeEventType
    observed_at: datetime
    runtime_event_id: RuntimeIdentifier | None = None
    raw_event_type: RuntimeIdentifier | None = None
    payload: dict[str, str | int | bool | None] = Field(default_factory=dict)

    @field_validator("observed_at")
    @classmethod
    def observed_at_is_utc(cls, value: datetime) -> datetime:
        return _normalize_timestamp(value)

    @field_validator("payload")
    @classmethod
    def payload_is_small_and_safe(
        cls, value: dict[str, str | int | bool | None]
    ) -> dict[str, str | int | bool | None]:
        if len(value) > 16:
            raise ValueError("event payload must contain at most 16 safe fields")
        for key, item in value.items():
            if not _SAFE_KEY.fullmatch(key) or "token" in key or "secret" in key:
                raise ValueError("event payload contains an unsafe field name")
            if isinstance(item, str) and (len(item) > 128 or _SECRET_TEXT.search(item)):
                raise ValueError("event payload contains unsafe text")
        return value


class EventContinuity(DomainModel):
    """Runtime event continuity observation, never inferred to include replay."""

    state: RuntimeContinuityState
    reason: RuntimeContinuityReason | None = None

    @model_validator(mode="after")
    def reason_matches_state(self) -> EventContinuity:
        if self.state is not RuntimeContinuityState.INCOMPLETE and self.reason is not None:
            raise ValueError("only incomplete continuity may have a reason")
        return self


class RuntimeUsage(DomainModel):
    """Integer usage totals when explicitly reported by the runtime."""

    input_tokens: int | None = Field(default=None, strict=True, ge=0)
    output_tokens: int | None = Field(default=None, strict=True, ge=0)
    reasoning_tokens: int | None = Field(default=None, strict=True, ge=0)
    cache_read_tokens: int | None = Field(default=None, strict=True, ge=0)
    cache_write_tokens: int | None = Field(default=None, strict=True, ge=0)


class RuntimeExecutionInspection(DomainModel):
    """Runtime-only status, safe summary, identity, continuity, and output hints."""

    execution_id: ExecutionId
    runtime_session: RuntimeSessionRef
    runtime_status: RuntimeStatus
    terminal: bool
    summary: SafeSummary | None = None
    provenance: RuntimeProvenance
    continuity: EventContinuity
    usage: RuntimeUsage | None = None
    runtime_output_refs: tuple[RuntimeIdentifier, ...] = ()
    runtime_diff_hint: SafeSummary | None = None

    @field_validator("summary", "runtime_diff_hint")
    @classmethod
    def summary_is_sanitized(cls, value: str | None) -> str | None:
        return None if value is None else _normalize_safe_text(value)

    @model_validator(mode="after")
    def terminal_matches_runtime_status(self) -> RuntimeExecutionInspection:
        terminal_statuses = {
            RuntimeStatus.SUCCEEDED,
            RuntimeStatus.FAILED,
            RuntimeStatus.BLOCKED,
            RuntimeStatus.CANCELLED,
        }
        if self.terminal != (self.runtime_status in terminal_statuses):
            raise ValueError("terminal flag must match runtime terminal status")
        return self


class RuntimeCancelRequest(DomainModel):
    """Idempotent request to stop one exact runtime session for an execution."""

    execution_id: ExecutionId
    runtime_session: RuntimeSessionRef
    reason: SafeSummary


class RuntimeControlAck(DomainModel):
    """Runtime response to cancellation; it does not mutate Relay lifecycle."""

    execution_id: ExecutionId
    state: RuntimeControlAckState
    observed_runtime_status: RuntimeStatus | None = None


class RuntimeFailure(DomainModel):
    """Normalized safe failure details without native response bodies or credentials."""

    category: RuntimeFailureCategory
    message: SafeSummary
    retryable: bool
    runtime_code: RuntimeIdentifier | None = None
    execution_id: ExecutionId | None = None
    runtime_session: RuntimeSessionRef | None = None

    @field_validator("message")
    @classmethod
    def message_is_sanitized(cls, value: str) -> str:
        return _normalize_safe_text(value)
