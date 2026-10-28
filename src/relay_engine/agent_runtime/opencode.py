"""OpenCode V2 HTTP adapter with exact-session event filtering and safe mapping."""

from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import json
import re
from collections.abc import AsyncIterator, Callable
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, cast
from urllib.parse import quote, urlsplit

import httpx
from pydantic import model_validator

from relay_engine.agent_runtime.boundary import (
    RuntimeEvidenceCompleteness,
    RuntimePermissionAttestation,
    RuntimeRequestV2,
    verify_runtime_permission_attestation_ref,
)
from relay_engine.agent_runtime.errors import AgentRuntimeError, fail
from relay_engine.agent_runtime.models import (
    EventContinuity,
    RuntimeCancelRequest,
    RuntimeCapability,
    RuntimeContinuityReason,
    RuntimeContinuityState,
    RuntimeControlAck,
    RuntimeControlAckState,
    RuntimeDescriptor,
    RuntimeEventEnvelope,
    RuntimeEventType,
    RuntimeExecutionHandle,
    RuntimeExecutionInspection,
    RuntimeExecutionRequest,
    RuntimeFailureCategory,
    RuntimeIdentityCompleteness,
    RuntimePermissionProfileRef,
    RuntimeProvenance,
    RuntimeSessionBinding,
    RuntimeSessionRef,
    RuntimeStatus,
    RuntimeUsage,
)
from relay_engine.domain import ContentDigest, new_id
from relay_engine.domain._base import DomainModel
from relay_engine.role_contracts import RequirementStatus

OPENCODE_RUNTIME_ID = "opencode"
OPENCODE_API_GENERATION = "v2"
OPENCODE_ADAPTER_VERSION = "0.1.0.dev0"
_MAX_SSE_LINE = 16_384
_RELEVANT_EVENT_MARKERS = (
    "session",
    "message",
    "tool",
    "permission",
    "part",
    "execution",
)
_SAFE_TOOL_NAMES = {
    "apply_patch",
    "bash",
    "edit",
    "glob",
    "grep",
    "list",
    "lsp",
    "question",
    "read",
    "skill",
    "task",
    "todowrite",
    "todoread",
    "webfetch",
    "websearch",
    "write",
}
_SAFE_EVENT_STATUSES = {
    "busy",
    "cancelled",
    "canceled",
    "completed",
    "error",
    "failed",
    "idle",
    "retry",
    "running",
    "success",
    "succeeded",
}


class OpenCodePermissionAction(StrEnum):
    """A preconfigured OpenCode permission outcome; ASK is never auto-approved."""

    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


@dataclass(frozen=True, slots=True)
class OpenCodePermissionProfile:
    """Bind a Relay permission reference to a preconfigured non-interactive agent.

    The OpenCode agent named by ``agent_id`` must already have the listed explicit
    rules in the separately managed OpenCode configuration. The HTTP adapter selects
    that agent and never replies to runtime permission prompts.
    """

    reference: RuntimePermissionProfileRef
    agent_id: str
    allow: tuple[str, ...]
    deny: tuple[str, ...]
    ask: tuple[str, ...] = ()
    allowed_plugins: tuple[str, ...] = ()
    allowed_mcp_servers: tuple[str, ...] = ()
    allowed_subagents: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.agent_id.strip() or len(self.agent_id) > 128:
            raise ValueError("OpenCode permission agent ID must be nonblank and bounded")
        all_rules = (*self.allow, *self.deny, *self.ask)
        if not self.allow or not self.deny:
            raise ValueError("OpenCode permission profile requires explicit allow and deny rules")
        if any(not rule.strip() or len(rule) > 128 for rule in all_rules):
            raise ValueError("OpenCode permission rules must be nonblank and bounded")
        if len(set(all_rules)) != len(all_rules):
            raise ValueError("OpenCode permission rules must not overlap or repeat")
        for label, values in (
            ("plugin", self.allowed_plugins),
            ("MCP server", self.allowed_mcp_servers),
            ("subagent", self.allowed_subagents),
        ):
            if values != tuple(sorted(set(values))) or any(not value.strip() for value in values):
                raise ValueError(f"allowed {label} identities must be unique and sorted")


class OpenCodeConfigurationQualificationRef(DomainModel):
    """Exact version-specific qualification of the configuration observation contract."""

    qualification_id: str
    content_digest: ContentDigest
    runtime_version: str
    runtime_api_generation: str
    adapter_version: str


class OpenCodeConfigurationBinding(DomainModel):
    """Immutable observation of the effective configuration for one OpenCode agent."""

    binding_id: str
    runtime_id: str
    runtime_version: str
    runtime_api_generation: str
    adapter_version: str
    integration_qualification_ref: OpenCodeConfigurationQualificationRef
    permission_profile_ref: RuntimePermissionProfileRef
    agent_id: str
    configuration_source_refs: tuple[str, ...]
    effective_configuration_digest: ContentDigest
    normalized_allow_rules: tuple[str, ...]
    normalized_deny_rules: tuple[str, ...]
    normalized_ask_rules: tuple[str, ...]
    effective_tool_exposure: tuple[str, ...]
    shell_exposed: bool
    plugin_exposure: tuple[str, ...]
    mcp_exposure: tuple[str, ...]
    subagent_exposure: tuple[str, ...]
    precedence_complete: bool
    observation_source: str
    trust_basis: str
    provenance_digest: ContentDigest
    observed_at: datetime
    status: RequirementStatus

    @model_validator(mode="after")
    def canonical_binding(self) -> OpenCodeConfigurationBinding:
        for name in (
            "normalized_allow_rules",
            "normalized_deny_rules",
            "normalized_ask_rules",
            "effective_tool_exposure",
            "plugin_exposure",
            "mcp_exposure",
            "subagent_exposure",
        ):
            values = getattr(self, name)
            if values != tuple(sorted(set(values))):
                raise ValueError(f"{name} must be unique and canonically ordered")
        if len(self.configuration_source_refs) != len(set(self.configuration_source_refs)):
            raise ValueError("configuration source refs must be unique in precedence order")
        if (
            not self.agent_id.strip()
            or not self.observation_source.strip()
            or not self.trust_basis.strip()
        ):
            raise ValueError("configuration binding identity and provenance must be explicit")
        return self

    @property
    def content_digest(self) -> ContentDigest:
        payload = json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(payload).hexdigest()

    @property
    def ref(self) -> OpenCodeConfigurationBindingRef:
        return OpenCodeConfigurationBindingRef(
            binding_id=self.binding_id,
            content_digest=self.content_digest,
        )


class OpenCodeConfigurationBindingRef(DomainModel):
    """Immutable reference to one exact effective OpenCode configuration."""

    binding_id: str
    content_digest: ContentDigest


@dataclass(slots=True)
class _ActiveExecution:
    """Private queue and stream state for one exact Relay execution."""

    execution_id: str
    runtime_session: RuntimeSessionRef
    request_digest: str
    workspace_root: str
    queue_limit: int
    queue: asyncio.Queue[RuntimeEventEnvelope] = field(init=False)
    ready: asyncio.Event = field(default_factory=asyncio.Event)
    wake: asyncio.Event = field(default_factory=asyncio.Event)
    response: httpx.Response | None = None
    pump_task: asyncio.Task[None] | None = None
    handle: RuntimeExecutionHandle | None = None
    continuity_state: RuntimeContinuityState = RuntimeContinuityState.LIVE_ONLY
    continuity_reason: RuntimeContinuityReason | None = None
    sequence: int = 0
    closed: bool = False
    consumed: bool = False
    overflow_gap_pending: bool = False
    runtime_status: RuntimeStatus = RuntimeStatus.UNKNOWN
    terminal: bool = False

    def __post_init__(self) -> None:
        self.queue = asyncio.Queue(maxsize=self.queue_limit)

    def continuity(self) -> EventContinuity:
        return EventContinuity(state=self.continuity_state, reason=self.continuity_reason)

    def mark_incomplete(self, reason: RuntimeContinuityReason) -> None:
        self.continuity_state = RuntimeContinuityState.INCOMPLETE
        self.continuity_reason = reason

    def _make_event(
        self,
        event_type: RuntimeEventType,
        *,
        raw_event_type: str | None = None,
        payload: dict[str, str | int | bool | None] | None = None,
    ) -> RuntimeEventEnvelope:
        self.sequence += 1
        safe_raw_event_type = (
            raw_event_type
            if raw_event_type is not None
            and re.fullmatch(
                r"(?:session|message|tool|permission|part|execution)\.[A-Za-z0-9_.-]{1,120}",
                raw_event_type,
            )
            else None
        )
        return RuntimeEventEnvelope(
            execution_id=self.execution_id,
            runtime_session=self.runtime_session,
            sequence=self.sequence,
            event_type=event_type,
            observed_at=datetime.now(UTC),
            raw_event_type=safe_raw_event_type,
            payload=payload or {},
        )

    def enqueue(
        self,
        event_type: RuntimeEventType,
        *,
        raw_event_type: str | None = None,
        payload: dict[str, str | int | bool | None] | None = None,
    ) -> None:
        self.flush_overflow_gap()
        event = self._make_event(event_type, raw_event_type=raw_event_type, payload=payload)
        try:
            self.queue.put_nowait(event)
            self.wake.set()
        except asyncio.QueueFull:
            self.mark_incomplete(RuntimeContinuityReason.BUFFER_OVERFLOW)
            self.overflow_gap_pending = True

    def flush_overflow_gap(self) -> None:
        if not self.overflow_gap_pending or self.queue.full():
            return
        event = self._make_event(
            RuntimeEventType.EVENT_GAP,
            payload={"reason": RuntimeContinuityReason.BUFFER_OVERFLOW.value},
        )
        self.queue.put_nowait(event)
        self.overflow_gap_pending = False
        self.wake.set()


class OpenCodeRuntime:
    """A single-generation OpenCode HTTP adapter.

    The endpoint, exact runtime version, and permission profile are explicit. No
    server discovery, process management, credential lookup, or API-generation
    fallback occurs here.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        expected_runtime_version: str,
        permission_profile: OpenCodePermissionProfile,
        client: httpx.AsyncClient | None = None,
        event_buffer_size: int = 256,
        executable_digest: str | None = None,
        configuration_digest: str | None = None,
        configuration_qualification_ref: OpenCodeConfigurationQualificationRef | None = None,
        configuration_binding_reader: Callable[
            [RuntimeExecutionRequest, RuntimeDescriptor], OpenCodeConfigurationBinding
        ]
        | None = None,
        permission_attestation_reader: Callable[
            [RuntimeRequestV2, RuntimeSessionBinding], RuntimePermissionAttestation
        ]
        | None = None,
        permission_attestation_id_factory: Callable[[], str] | None = None,
    ) -> None:
        endpoint_url = httpx.URL(endpoint)
        endpoint_parts = urlsplit(endpoint)
        endpoint_host = endpoint_parts.hostname
        try:
            endpoint_is_loopback = (
                endpoint_host is not None and ipaddress.ip_address(endpoint_host).is_loopback
            )
        except ValueError:
            endpoint_is_loopback = (
                endpoint_host is not None and endpoint_host.lower() == "localhost"
            )
        if (
            endpoint_url.scheme not in {"http", "https"}
            or not endpoint_url.host
            or not endpoint_is_loopback
            or endpoint_parts.port is None
            or bool(endpoint_url.username)
            or bool(endpoint_url.password)
            or endpoint_url.query
            or endpoint_url.fragment
        ):
            raise ValueError(
                "OpenCode endpoint must be explicit loopback HTTP(S) without credentials"
            )
        if not expected_runtime_version.strip() or len(expected_runtime_version) > 128:
            raise ValueError("expected OpenCode runtime version must be nonblank and bounded")
        if event_buffer_size < 1 or event_buffer_size > 65_536:
            raise ValueError("event buffer size must be between 1 and 65536")

        self._endpoint = endpoint_url.copy_with(path=endpoint_url.path.rstrip("/"))
        self._expected_runtime_version = expected_runtime_version
        self._permission_profile = permission_profile
        self._event_buffer_size = event_buffer_size
        self._executable_digest = executable_digest
        self._configuration_digest = configuration_digest
        self._configuration_qualification_ref = configuration_qualification_ref
        self._configuration_binding_reader = configuration_binding_reader
        self._permission_attestation_reader = permission_attestation_reader
        self._permission_attestation_id_factory = permission_attestation_id_factory or (
            lambda: new_id("evd_")
        )
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10, read=None, write=10, pool=10),
            follow_redirects=False,
        )
        self._bindings: dict[str, RuntimeSessionBinding] = {}
        self._configuration_bindings: dict[str, tuple[str, OpenCodeConfigurationBinding]] = {}
        self._v2_bindings: dict[str, tuple[str, RuntimeSessionBinding]] = {}
        self._permission_attestations: dict[
            str, tuple[str, RuntimeSessionBinding, RuntimePermissionAttestation]
        ] = {}
        self._create_attempts: dict[str, str] = {}
        self._requested_identities: dict[str, tuple[str, str, str]] = {}
        self._opened: set[str] = set()
        self._active: dict[str, _ActiveExecution] = {}
        self._cancel_acks: dict[tuple[str, str], RuntimeControlAck] = {}
        self._lock = asyncio.Lock()
        self._cancel_lock = asyncio.Lock()

    async def aclose(self) -> None:
        """Close adapter-owned event streams and its internally created client."""

        for active in self._active.values():
            await self._close_active(active)
        if self._owns_client:
            await self._client.aclose()

    async def describe(self) -> RuntimeDescriptor:
        """Validate the explicit server endpoint, API generation, and runtime version."""

        try:
            response = await self._client.get(self._url("/api/health"))
        except httpx.TimeoutException:
            raise fail(
                RuntimeFailureCategory.TIMEOUT,
                "OpenCode health check timed out.",
                retryable=True,
            ) from None
        except httpx.RequestError:
            raise fail(
                RuntimeFailureCategory.RUNTIME_UNAVAILABLE,
                "OpenCode endpoint is unavailable.",
                retryable=True,
            ) from None

        if response.status_code != 200:
            category = (
                RuntimeFailureCategory.UNSUPPORTED_RUNTIME_VERSION
                if response.status_code == 404
                else self._http_failure_category(response.status_code)
            )
            raise fail(category, "OpenCode V2 health check was rejected.")

        payload = self._read_json(response, RuntimeFailureCategory.UNSUPPORTED_RUNTIME_VERSION)
        version = payload.get("version")
        if (
            payload.get("healthy") is not True
            or not isinstance(version, str)
            or not version.strip()
        ):
            raise fail(
                RuntimeFailureCategory.UNSUPPORTED_RUNTIME_VERSION,
                "OpenCode health response does not expose a compatible runtime version.",
            )
        if version != self._expected_runtime_version:
            raise fail(
                RuntimeFailureCategory.UNSUPPORTED_RUNTIME_VERSION,
                "OpenCode runtime version is outside the configured compatibility profile.",
            )

        capabilities = [
            RuntimeCapability.SESSION_CREATE,
            RuntimeCapability.EXECUTE,
            RuntimeCapability.EVENT_STREAM,
            RuntimeCapability.CANCEL,
            RuntimeCapability.RESULT_INSPECTION,
            RuntimeCapability.USAGE_REPORTING,
            RuntimeCapability.ACTUAL_PROVIDER_IDENTITY,
            RuntimeCapability.ACTUAL_MODEL_IDENTITY,
        ]
        if self._permission_attestation_reader is not None:
            capabilities.append(RuntimeCapability.EFFECTIVE_PERMISSION_ATTESTATION)
        return RuntimeDescriptor(
            runtime_id=OPENCODE_RUNTIME_ID,
            adapter_version=OPENCODE_ADAPTER_VERSION,
            runtime_version=version,
            api_generation=OPENCODE_API_GENERATION,
            capabilities=tuple(capabilities),
            executable_digest=self._executable_digest,
            configuration_digest=self._configuration_digest,
        )

    async def create_session(self, request: RuntimeExecutionRequest) -> RuntimeSessionBinding:
        """Create an exact-session binding without sending any prompt content."""

        execution_id = request.basis.execution_id
        self._validate_request_digest(request)
        async with self._lock:
            existing = self._bindings.get(execution_id)
            if existing is not None:
                if existing.request_digest != request.request_digest:
                    raise fail(
                        RuntimeFailureCategory.REQUEST_CONFLICT,
                        "Execution ID is already bound to a different request digest.",
                        execution_id=execution_id,
                    )
                return existing

            attempted_digest = self._create_attempts.get(execution_id)
            if attempted_digest is not None:
                if attempted_digest != request.request_digest:
                    raise fail(
                        RuntimeFailureCategory.REQUEST_CONFLICT,
                        "Execution ID already has a session creation attempt for another request.",
                        execution_id=execution_id,
                    )
                raise fail(
                    RuntimeFailureCategory.SESSION_BINDING_REQUIRED,
                    "Exact session binding is required after an uncertain session creation.",
                    execution_id=execution_id,
                )

            self._validate_permission_profile(request.basis.permission_profile_ref, execution_id)
            descriptor = await self.describe()
            self._require_capabilities(descriptor, request, execution_id)
            self._requested_identities[execution_id] = (
                request.basis.runtime_selection.requested_provider_id,
                request.basis.runtime_selection.requested_model_id,
                request.request_digest,
            )

            body = {
                "agent": self._permission_profile.agent_id,
                "location": {"directory": request.basis.workspace.root},
                "model": {
                    "id": request.basis.runtime_selection.requested_model_id,
                    "providerID": request.basis.runtime_selection.requested_provider_id,
                },
            }
            self._create_attempts[execution_id] = request.request_digest
            try:
                response = await self._client.post(self._url("/api/session"), json=body)
            except httpx.TimeoutException:
                raise fail(
                    RuntimeFailureCategory.TIMEOUT,
                    "OpenCode session creation timed out; exact binding is required before retry.",
                    execution_id=execution_id,
                ) from None
            except httpx.RequestError:
                raise fail(
                    RuntimeFailureCategory.TRANSPORT,
                    "OpenCode session creation response was not received; "
                    "exact binding is required.",
                    execution_id=execution_id,
                ) from None

            if response.status_code != 200:
                category = self._http_failure_category(response.status_code)
                if response.status_code == 400:
                    category = RuntimeFailureCategory.CONFIGURATION
                raise fail(
                    category,
                    "OpenCode rejected session creation.",
                    execution_id=execution_id,
                )

            payload = self._read_json(response, RuntimeFailureCategory.TRANSPORT)
            session_data = self._unwrap_object(payload)
            session_id = self._session_id_from(session_data)
            location = self._object(session_data.get("location"))
            directory = location.get("directory")
            if session_id is None or directory != request.basis.workspace.root:
                raise fail(
                    RuntimeFailureCategory.WORKSPACE_ACCESS,
                    "OpenCode did not confirm the exact requested workspace and session.",
                    execution_id=execution_id,
                )

            runtime_session = RuntimeSessionRef(
                runtime_id=OPENCODE_RUNTIME_ID,
                session_id=session_id,
            )
            actual_provider, actual_model = self._actual_model_identity(session_data)
            identity_status = (
                RuntimeIdentityCompleteness.FULL
                if actual_provider is not None and actual_model is not None
                else RuntimeIdentityCompleteness.PARTIAL
                if actual_provider is not None or actual_model is not None
                else RuntimeIdentityCompleteness.UNKNOWN
            )
            binding = RuntimeSessionBinding(
                execution_id=execution_id,
                runtime_session=runtime_session,
                request_digest=request.request_digest,
                workspace_id=request.basis.workspace.workspace_id,
                created_at=datetime.now(UTC),
                actual_provider_id=actual_provider,
                actual_model_id=actual_model,
                actual_identity_status=identity_status,
            )
            self._bindings[execution_id] = binding
            return binding

    async def prepare_trusted_local_session(
        self,
        request: RuntimeExecutionRequest,
        descriptor: RuntimeDescriptor,
        accepted_qualification_source_refs: tuple[tuple[str, str], ...],
    ) -> tuple[OpenCodeConfigurationBinding, RuntimeSessionBinding]:
        """Verify snapshot-qualified effective configuration before session creation."""

        if (
            self._configuration_binding_reader is None
            or self._configuration_qualification_ref is None
        ):
            raise fail(
                RuntimeFailureCategory.UNSUPPORTED_CAPABILITY,
                "Version-qualified OpenCode configuration evidence is unavailable.",
                execution_id=request.basis.execution_id,
            )
        current_descriptor = await self.describe()
        if current_descriptor != descriptor:
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "OpenCode descriptor changed before configuration binding.",
                execution_id=request.basis.execution_id,
            )
        qualification_identity = (
            self._configuration_qualification_ref.qualification_id,
            self._configuration_qualification_ref.content_digest,
        )
        if (
            accepted_qualification_source_refs
            != tuple(sorted(set(accepted_qualification_source_refs)))
            or qualification_identity not in accepted_qualification_source_refs
        ):
            raise fail(
                RuntimeFailureCategory.CONFIGURATION,
                "OpenCode configuration qualification is absent from the exact accepted "
                "source snapshot.",
                execution_id=request.basis.execution_id,
            )
        self._validate_request_digest(request)
        self._validate_permission_profile(
            request.basis.permission_profile_ref, request.basis.execution_id
        )
        try:
            binding = self._configuration_binding_reader(request, descriptor)
        except Exception:
            raise fail(
                RuntimeFailureCategory.CONFIGURATION,
                "OpenCode effective configuration could not be resolved exactly.",
                execution_id=request.basis.execution_id,
            ) from None
        self._validate_configuration_binding(binding, request, descriptor)
        existing = self._configuration_bindings.get(request.basis.execution_id)
        if existing is not None and existing != (request.request_digest, binding):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Execution ID is already bound to a different OpenCode configuration.",
                execution_id=request.basis.execution_id,
            )
        self._configuration_bindings[request.basis.execution_id] = (
            request.request_digest,
            binding,
        )
        session = await self.create_session(request)
        return binding, session

    async def close_prepared_session(self, binding: RuntimeSessionBinding) -> RequirementStatus:
        """Close one exact prompt-free session; unsupported cleanup stays indeterminate."""

        known = self._bindings.get(binding.execution_id)
        if known != binding:
            return RequirementStatus.INDETERMINATE
        try:
            response = await self._client.delete(
                self._url("/api/session/" + quote(binding.runtime_session.session_id, safe=""))
            )
        except httpx.RequestError:
            return RequirementStatus.INDETERMINATE
        if response.status_code in {200, 204}:
            return RequirementStatus.SATISFIED
        if response.status_code in {401, 403, 409}:
            return RequirementStatus.UNSATISFIED
        return RequirementStatus.INDETERMINATE

    def _validate_configuration_binding(
        self,
        binding: OpenCodeConfigurationBinding,
        request: RuntimeExecutionRequest,
        descriptor: RuntimeDescriptor,
    ) -> None:
        qualification = self._configuration_qualification_ref
        profile = self._permission_profile
        expected_configuration_payload = {
            "agent_id": binding.agent_id,
            "configuration_source_refs": binding.configuration_source_refs,
            "normalized_allow_rules": binding.normalized_allow_rules,
            "normalized_deny_rules": binding.normalized_deny_rules,
            "normalized_ask_rules": binding.normalized_ask_rules,
            "effective_tool_exposure": binding.effective_tool_exposure,
            "plugin_exposure": binding.plugin_exposure,
            "mcp_exposure": binding.mcp_exposure,
            "subagent_exposure": binding.subagent_exposure,
        }
        expected_configuration_digest = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(
                    expected_configuration_payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8")
            ).hexdigest()
        )
        if (
            qualification is None
            or binding.integration_qualification_ref != qualification
            or qualification.runtime_version != descriptor.runtime_version
            or qualification.runtime_api_generation != descriptor.api_generation
            or qualification.adapter_version != descriptor.adapter_version
            or binding.runtime_id != descriptor.runtime_id
            or binding.runtime_version != descriptor.runtime_version
            or binding.runtime_api_generation != descriptor.api_generation
            or binding.adapter_version != descriptor.adapter_version
            or binding.permission_profile_ref != request.basis.permission_profile_ref
            or binding.agent_id != profile.agent_id
            or binding.normalized_allow_rules != tuple(sorted(profile.allow))
            or binding.normalized_deny_rules != tuple(sorted(profile.deny))
            or binding.normalized_ask_rules != tuple(sorted(profile.ask))
            or binding.effective_tool_exposure
            != tuple(
                sorted(
                    (
                        *profile.allow,
                        *profile.allowed_plugins,
                        *profile.allowed_mcp_servers,
                        *profile.allowed_subagents,
                    )
                )
            )
            or binding.shell_exposed != ("bash" in binding.effective_tool_exposure)
            or binding.plugin_exposure != profile.allowed_plugins
            or binding.mcp_exposure != profile.allowed_mcp_servers
            or binding.subagent_exposure != profile.allowed_subagents
            or not binding.precedence_complete
            or not binding.configuration_source_refs
            or binding.status is not RequirementStatus.SATISFIED
            or binding.effective_configuration_digest != expected_configuration_digest
        ):
            raise fail(
                RuntimeFailureCategory.CONFIGURATION,
                "OpenCode configuration binding does not match exact qualified policy.",
                execution_id=request.basis.execution_id,
            )

    async def create_session_v2(self, request: RuntimeRequestV2) -> RuntimeSessionBinding:
        """Create one prompt-free session for a placement-bound V2 request."""

        if str(self._endpoint).rstrip("/") != request.endpoint_identity.rstrip("/"):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Configured OpenCode endpoint does not match the attested V2 endpoint.",
                execution_id=request.request.basis.execution_id,
            )
        descriptor = await self.describe()
        if RuntimeCapability.EFFECTIVE_PERMISSION_ATTESTATION not in descriptor.capabilities:
            raise fail(
                RuntimeFailureCategory.UNSUPPORTED_CAPABILITY,
                "OpenCode effective permission inspection is not configured.",
                execution_id=request.request.basis.execution_id,
            )
        if request.launch_subject.runtime_descriptor_digest != self._descriptor_digest(descriptor):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "OpenCode descriptor does not match the exact launch subject.",
                execution_id=request.request.basis.execution_id,
            )
        execution_id = request.request.basis.execution_id
        known = self._v2_bindings.get(execution_id)
        if known is not None:
            if known[0] != request.request_digest_v2:
                raise fail(
                    RuntimeFailureCategory.REQUEST_CONFLICT,
                    "Execution ID already has a different V2 request binding.",
                    execution_id=execution_id,
                )
            return known[1]

        binding = await self.create_session(request.request)
        bound = binding.model_copy(update={"request_digest_v2": request.request_digest_v2})
        self._v2_bindings[execution_id] = (request.request_digest_v2, bound)
        return bound

    async def attest_permissions_v2(
        self,
        request: RuntimeRequestV2,
        binding: RuntimeSessionBinding,
    ) -> RuntimePermissionAttestation:
        """Read trustworthy effective permission evidence for one exact session."""

        self._validate_v2_binding(request, binding)
        if self._permission_attestation_reader is None:
            raise fail(
                RuntimeFailureCategory.UNSUPPORTED_CAPABILITY,
                "OpenCode effective permission inspection is not configured.",
                execution_id=binding.execution_id,
                runtime_session=binding.runtime_session,
            )
        existing = self._permission_attestations.get(binding.execution_id)
        if existing is not None:
            if existing[0] != request.request_digest_v2 or existing[1] != binding:
                raise fail(
                    RuntimeFailureCategory.REQUEST_CONFLICT,
                    "Execution ID already has a different V2 permission observation.",
                    execution_id=binding.execution_id,
                    runtime_session=binding.runtime_session,
                )
            return existing[2]
        evidence = self._permission_attestation_reader(request, binding)
        if (
            evidence.execution_id != binding.execution_id
            or evidence.request_digest_v2 != request.request_digest_v2
            or evidence.session_binding != binding
            or evidence.runtime_descriptor_digest
            != request.launch_subject.runtime_descriptor_digest
            or evidence.launch_subject_digest != request.launch_subject.content_digest
            or evidence.placement_attestation_digest != request.placement_attestation_digest
            or evidence.expected_permission_profile_ref
            != request.launch_subject.permission_profile_ref
            or evidence.observed_effective_profile_digest
            != request.launch_subject.permission_profile_ref.content_digest
            or evidence.completeness is not RuntimeEvidenceCompleteness.SATISFIED
        ):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "OpenCode permission evidence does not bind the exact V2 session.",
                execution_id=binding.execution_id,
                runtime_session=binding.runtime_session,
            )
        # The adapter owns the immutable Relay evidence identity. Any identifier
        # supplied by the runtime-specific observation reader is discarded.
        evidence_values = evidence.model_dump(mode="python")
        evidence_values["attestation_id"] = self._permission_attestation_id_factory()
        evidence = RuntimePermissionAttestation.model_validate(evidence_values)
        self._permission_attestations[binding.execution_id] = (
            request.request_digest_v2,
            binding,
            evidence,
        )
        return evidence

    async def open_execution_v2(
        self,
        request: RuntimeRequestV2,
        binding: RuntimeSessionBinding,
        permission_attestation: RuntimePermissionAttestation,
    ) -> RuntimeExecutionHandle:
        """Admit one prompt only after exact V2 session permission evidence."""

        self._validate_v2_binding(request, binding)
        if (
            permission_attestation.execution_id != binding.execution_id
            or permission_attestation.request_digest_v2 != request.request_digest_v2
            or permission_attestation.session_binding != binding
            or permission_attestation.expected_permission_profile_ref
            != request.launch_subject.permission_profile_ref
            or permission_attestation.observed_effective_profile_digest
            != request.launch_subject.permission_profile_ref.content_digest
            or not verify_runtime_permission_attestation_ref(
                permission_attestation, permission_attestation.ref
            )
            or permission_attestation.completeness is not RuntimeEvidenceCompleteness.SATISFIED
        ):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Exact complete permission attestation is required before V2 prompt admission.",
                execution_id=binding.execution_id,
                runtime_session=binding.runtime_session,
            )
        v1_binding = binding.model_copy(update={"request_digest_v2": None})
        handle = await self.open_execution(request.request, v1_binding)
        v2_handle = handle.model_copy(update={"request_digest_v2": request.request_digest_v2})
        active = self._active.get(handle.execution_id)
        if active is not None and active.handle == handle:
            active.handle = v2_handle
        return v2_handle

    async def open_execution(
        self,
        request: RuntimeExecutionRequest,
        binding: RuntimeSessionBinding | None,
    ) -> RuntimeExecutionHandle:
        """Observe before prompt admission and return an exact handle for recovery."""

        execution_id = request.basis.execution_id
        if binding is None:
            raise fail(
                RuntimeFailureCategory.SESSION_BINDING_REQUIRED,
                "An exact runtime session binding is required to open execution.",
                execution_id=execution_id,
            )
        self._validate_binding(request, binding)
        self._validate_permission_profile(request.basis.permission_profile_ref, execution_id)
        self._requested_identities[execution_id] = (
            request.basis.runtime_selection.requested_provider_id,
            request.basis.runtime_selection.requested_model_id,
            request.request_digest,
        )

        async with self._lock:
            if execution_id in self._opened:
                raise fail(
                    RuntimeFailureCategory.REQUEST_CONFLICT,
                    "An invocation has already been opened for this Relay execution.",
                    execution_id=execution_id,
                    runtime_session=binding.runtime_session,
                )
            self._opened.add(execution_id)

        try:
            descriptor = await self.describe()
            self._require_capabilities(descriptor, request, execution_id)
            active = await self._establish_event_observer(request, binding)
        except Exception:
            async with self._lock:
                self._opened.discard(execution_id)
            raise

        opened_at = datetime.now(UTC)
        provisional_handle = RuntimeExecutionHandle(
            execution_id=execution_id,
            runtime_session=binding.runtime_session,
            request_digest=request.request_digest,
            opened_at=opened_at,
        )
        active.handle = provisional_handle
        self._active[execution_id] = active

        # Give the pump a scheduling turn so an immediately closed observer fails closed.
        await asyncio.sleep(0)
        if active.closed or active.pump_task is None or active.pump_task.done():
            await self._close_active(active)
            self._active.pop(execution_id, None)
            async with self._lock:
                self._opened.discard(execution_id)
            raise fail(
                RuntimeFailureCategory.EVENT_OBSERVATION_UNAVAILABLE,
                "OpenCode event observation ended before prompt admission.",
                execution_id=execution_id,
                runtime_session=binding.runtime_session,
            )

        prompt_body: dict[str, Any] = {
            "text": request.basis.input_payload.text,
            "files": [],
            "agents": [],
            "skills": [],
            "metadata": {},
        }
        try:
            response = await self._client.post(
                self._session_url(binding.runtime_session, "/prompt"),
                json=prompt_body,
            )
        except httpx.TimeoutException:
            # The server may have admitted the prompt before the response timed out.
            # Keep the observer and one-prompt guard, and return the exact session handle
            # so the caller can inspect or cancel without guessing.
            return provisional_handle
        except httpx.RequestError:
            # Request transport errors are also ambiguous about prompt admission.
            return provisional_handle

        if response.status_code != 200:
            if response.status_code >= 500 or 200 <= response.status_code < 300:
                # A server failure or unexpected success response may follow admission.
                return provisional_handle

            if response.status_code == 403:
                category = RuntimeFailureCategory.PERMISSION_DENIED
            elif response.status_code == 400:
                category = RuntimeFailureCategory.CONFIGURATION
            else:
                category = self._http_failure_category(response.status_code)
            await self._discard_active(execution_id, active)
            raise fail(
                category,
                "OpenCode rejected prompt admission.",
                execution_id=execution_id,
                runtime_session=binding.runtime_session,
            )

        try:
            self._unwrap_data(self._read_json(response, RuntimeFailureCategory.TRANSPORT))
        except AgentRuntimeError:
            # A successful response with an unusable body may still represent admission.
            return provisional_handle
        return provisional_handle

    def events(self, handle: RuntimeExecutionHandle) -> AsyncIterator[RuntimeEventEnvelope]:
        """Consume the already-running adapter queue without opening another stream."""

        active = self._active_for_handle(handle)
        if active.consumed:
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Runtime event queue already has a consumer.",
                execution_id=handle.execution_id,
                runtime_session=handle.runtime_session,
            )
        active.consumed = True
        return self._consume_events(active)

    async def cancel(self, request: RuntimeCancelRequest) -> RuntimeControlAck:
        """Interrupt the exact runtime session idempotently and report runtime state."""

        async with self._cancel_lock:
            return await self._cancel_once(request)

    async def _cancel_once(self, request: RuntimeCancelRequest) -> RuntimeControlAck:
        """Serialize cancellation requests so concurrent retries share one result."""

        binding = self._bindings.get(request.execution_id)
        if binding is None:
            raise fail(
                RuntimeFailureCategory.SESSION_BINDING_REQUIRED,
                "Exact process-local session binding is required for cancellation.",
                execution_id=request.execution_id,
            )
        if (
            binding.execution_id != request.execution_id
            or binding.runtime_session != request.runtime_session
        ):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Cancellation session does not match the exact process-local binding.",
                execution_id=request.execution_id,
                runtime_session=binding.runtime_session,
            )
        self._validate_session_runtime(binding.runtime_session)

        cache_key = (request.execution_id, request.runtime_session.session_id)
        cached = self._cancel_acks.get(cache_key)
        if cached is not None:
            return cached

        active = self._active.get(request.execution_id)
        if active is not None and (
            active.runtime_session != binding.runtime_session
            or active.request_digest != binding.request_digest
        ):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Cancellation state does not match the exact process-local binding.",
                execution_id=request.execution_id,
                runtime_session=request.runtime_session,
            )
        if active is not None and active.terminal:
            ack = RuntimeControlAck(
                execution_id=request.execution_id,
                state=RuntimeControlAckState.ALREADY_TERMINAL,
                observed_runtime_status=active.runtime_status,
            )
            self._cancel_acks[cache_key] = ack
            return ack

        try:
            response = await self._client.post(
                self._session_url(request.runtime_session, "/interrupt")
            )
        except httpx.TimeoutException:
            raise fail(
                RuntimeFailureCategory.TIMEOUT,
                "OpenCode cancellation request timed out.",
                retryable=True,
                execution_id=request.execution_id,
                runtime_session=request.runtime_session,
            ) from None
        except httpx.RequestError:
            raise fail(
                RuntimeFailureCategory.TRANSPORT,
                "OpenCode cancellation request failed.",
                retryable=True,
                execution_id=request.execution_id,
                runtime_session=request.runtime_session,
            ) from None

        if response.status_code == 404:
            state = RuntimeControlAckState.NOT_FOUND
            status = RuntimeStatus.UNKNOWN
        elif response.status_code == 403:
            state = RuntimeControlAckState.DENIED
            status = active.runtime_status if active else RuntimeStatus.UNKNOWN
        elif response.status_code != 204:
            raise fail(
                self._http_failure_category(response.status_code),
                "OpenCode rejected cancellation.",
                execution_id=request.execution_id,
                runtime_session=request.runtime_session,
            )
        else:
            # The pinned V2 interrupt contract is 204 No Content, not a JSON response.
            status = active.runtime_status if active else RuntimeStatus.UNKNOWN
            state = (
                RuntimeControlAckState.ALREADY_TERMINAL
                if active is not None and active.terminal
                else RuntimeControlAckState.REQUESTED
            )

        ack = RuntimeControlAck(
            execution_id=request.execution_id,
            state=state,
            observed_runtime_status=status,
        )
        self._cancel_acks[cache_key] = ack
        return ack

    async def inspect(self, handle: RuntimeExecutionHandle) -> RuntimeExecutionInspection:
        """Read runtime status and safe provenance independently of event consumption."""

        binding = self._bindings.get(handle.execution_id)
        request_identity = self._requested_identities.get(handle.execution_id)
        if binding is None or request_identity is None:
            raise fail(
                RuntimeFailureCategory.SESSION_BINDING_REQUIRED,
                "Exact process-local request and session binding are required for inspection.",
                execution_id=handle.execution_id,
            )
        if (
            handle.execution_id != binding.execution_id
            or handle.runtime_session != binding.runtime_session
            or handle.request_digest != binding.request_digest
            or request_identity[2] != binding.request_digest
        ):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Inspection handle does not match the exact process-local request binding.",
                execution_id=handle.execution_id,
                runtime_session=binding.runtime_session,
            )
        self._validate_session_runtime(binding.runtime_session)

        active = self._active.get(handle.execution_id)
        if active is not None and (
            active.runtime_session != binding.runtime_session
            or active.request_digest != binding.request_digest
        ):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Inspection state does not match the exact process-local request binding.",
                execution_id=handle.execution_id,
                runtime_session=handle.runtime_session,
            )
        descriptor = await self.describe()
        if RuntimeCapability.RESULT_INSPECTION not in descriptor.capabilities:
            raise fail(
                RuntimeFailureCategory.UNSUPPORTED_CAPABILITY,
                "OpenCode profile does not support result inspection.",
                execution_id=handle.execution_id,
                runtime_session=handle.runtime_session,
            )

        try:
            response = await self._client.get(self._session_url(handle.runtime_session, ""))
        except httpx.TimeoutException:
            raise fail(
                RuntimeFailureCategory.TIMEOUT,
                "OpenCode inspection timed out.",
                retryable=True,
                execution_id=handle.execution_id,
                runtime_session=handle.runtime_session,
            ) from None
        except httpx.RequestError:
            raise fail(
                RuntimeFailureCategory.RESULT_INSPECTION,
                "OpenCode inspection is unavailable.",
                retryable=True,
                execution_id=handle.execution_id,
                runtime_session=handle.runtime_session,
            ) from None

        if response.status_code != 200:
            category = (
                RuntimeFailureCategory.RESULT_INSPECTION
                if response.status_code == 404
                else self._http_failure_category(response.status_code)
            )
            raise fail(
                category,
                "OpenCode could not inspect the exact runtime session.",
                execution_id=handle.execution_id,
                runtime_session=handle.runtime_session,
            )

        session_data = self._unwrap_object(
            self._read_json(response, RuntimeFailureCategory.RESULT_INSPECTION)
        )
        actual_provider, actual_model = self._actual_model_identity(session_data)
        provenance = RuntimeProvenance(
            runtime_id=OPENCODE_RUNTIME_ID,
            adapter_version=descriptor.adapter_version,
            runtime_version=descriptor.runtime_version,
            api_generation=descriptor.api_generation,
            requested_provider_id=self._requested_for(handle.execution_id, "provider"),
            requested_model_id=self._requested_for(handle.execution_id, "model"),
            actual_provider_id=actual_provider,
            actual_model_id=actual_model,
            identity_completeness=self._identity_completeness(actual_provider, actual_model),
        )
        reported_status = self._runtime_status_from(session_data.get("status"))
        if reported_status is RuntimeStatus.UNKNOWN and active is not None:
            reported_status = active.runtime_status
        terminal = reported_status in {
            RuntimeStatus.SUCCEEDED,
            RuntimeStatus.FAILED,
            RuntimeStatus.BLOCKED,
            RuntimeStatus.CANCELLED,
        }
        if active is not None and active.terminal and reported_status is RuntimeStatus.UNKNOWN:
            terminal = True

        return RuntimeExecutionInspection(
            execution_id=handle.execution_id,
            runtime_session=handle.runtime_session,
            runtime_status=reported_status,
            terminal=terminal,
            summary=(
                f"OpenCode reported runtime status {reported_status.value}."
                if reported_status is not RuntimeStatus.UNKNOWN
                else None
            ),
            provenance=provenance,
            continuity=active.continuity()
            if active is not None
            else EventContinuity(state=RuntimeContinuityState.LIVE_ONLY),
            usage=self._runtime_usage(session_data),
            runtime_output_refs=(),
            runtime_diff_hint=self._diff_hint(session_data),
        )

    def continuity(self, handle: RuntimeExecutionHandle) -> EventContinuity:
        """Expose current event continuity without consuming the event queue."""

        return self._active_for_handle(handle).continuity()

    async def _establish_event_observer(
        self,
        request: RuntimeExecutionRequest,
        binding: RuntimeSessionBinding,
    ) -> _ActiveExecution:
        active = _ActiveExecution(
            execution_id=request.basis.execution_id,
            runtime_session=binding.runtime_session,
            request_digest=request.request_digest,
            workspace_root=request.basis.workspace.root,
            queue_limit=self._event_buffer_size,
        )
        request_obj = self._client.build_request(
            "GET",
            self._url("/api/event"),
            headers={"accept": "text/event-stream"},
        )
        try:
            response = await self._client.send(request_obj, stream=True)
        except httpx.TimeoutException:
            raise fail(
                RuntimeFailureCategory.EVENT_OBSERVATION_UNAVAILABLE,
                "OpenCode event observation could not be established.",
                execution_id=request.basis.execution_id,
                runtime_session=binding.runtime_session,
            ) from None
        except httpx.RequestError:
            raise fail(
                RuntimeFailureCategory.EVENT_OBSERVATION_UNAVAILABLE,
                "OpenCode event observation could not be established.",
                execution_id=request.basis.execution_id,
                runtime_session=binding.runtime_session,
            ) from None

        content_type = response.headers.get("content-type", "").lower()
        if response.status_code != 200 or not content_type.startswith("text/event-stream"):
            await response.aclose()
            raise fail(
                RuntimeFailureCategory.EVENT_OBSERVATION_UNAVAILABLE,
                "OpenCode did not provide the configured V2 event stream.",
                execution_id=request.basis.execution_id,
                runtime_session=binding.runtime_session,
            )

        active.response = response
        active.pump_task = asyncio.create_task(self._pump_events(active))
        try:
            await asyncio.wait_for(active.ready.wait(), timeout=5)
        except TimeoutError:
            await self._close_active(active)
            raise fail(
                RuntimeFailureCategory.EVENT_OBSERVATION_UNAVAILABLE,
                "OpenCode event pump did not become ready before prompt admission.",
                execution_id=request.basis.execution_id,
                runtime_session=binding.runtime_session,
            ) from None
        if active.closed:
            await self._close_active(active)
            raise fail(
                RuntimeFailureCategory.EVENT_OBSERVATION_UNAVAILABLE,
                "OpenCode event stream closed before prompt admission.",
                execution_id=request.basis.execution_id,
                runtime_session=binding.runtime_session,
            )
        return active

    async def _pump_events(self, active: _ActiveExecution) -> None:
        response = active.response
        if response is None:
            active.mark_incomplete(RuntimeContinuityReason.OBSERVATION_UNAVAILABLE)
            active.closed = True
            active.ready.set()
            active.wake.set()
            return

        active.ready.set()
        data_lines: list[str] = []
        event_name: str | None = None
        event_id: str | None = None
        try:
            async for line in response.aiter_lines():
                if len(line) > _MAX_SSE_LINE:
                    active.mark_incomplete(RuntimeContinuityReason.EVENT_ATTRIBUTION)
                    active.enqueue(
                        RuntimeEventType.EVENT_GAP,
                        payload={"reason": RuntimeContinuityReason.EVENT_ATTRIBUTION.value},
                    )
                    data_lines.clear()
                    event_name = None
                    event_id = None
                    continue
                if not line:
                    if data_lines:
                        await self._normalize_sse_event(
                            active, "\n".join(data_lines), event_name, event_id
                        )
                    data_lines.clear()
                    event_name = None
                    event_id = None
                    continue
                if line.startswith(":"):
                    continue
                field_name, separator, field_value = line.partition(":")
                if separator and field_value.startswith(" "):
                    field_value = field_value[1:]
                if field_name == "data":
                    data_lines.append(field_value)
                elif field_name == "event":
                    event_name = field_value
                elif field_name == "id":
                    event_id = field_value
        except asyncio.CancelledError:
            raise
        except Exception:
            active.mark_incomplete(RuntimeContinuityReason.STREAM_DISCONNECTED)
            active.enqueue(
                RuntimeEventType.EVENT_GAP,
                payload={"reason": RuntimeContinuityReason.STREAM_DISCONNECTED.value},
            )
        else:
            active.mark_incomplete(RuntimeContinuityReason.STREAM_DISCONNECTED)
            active.enqueue(
                RuntimeEventType.EVENT_GAP,
                payload={"reason": RuntimeContinuityReason.STREAM_DISCONNECTED.value},
            )
        finally:
            active.closed = True
            active.wake.set()
            await response.aclose()

    async def _normalize_sse_event(
        self,
        active: _ActiveExecution,
        raw_data: str,
        event_name: str | None,
        event_id: str | None,
    ) -> None:
        del event_id  # Runtime event IDs are optional provenance and are omitted by default.
        try:
            payload: Any = json.loads(raw_data)
        except json.JSONDecodeError, TypeError:
            active.mark_incomplete(RuntimeContinuityReason.EVENT_ATTRIBUTION)
            active.enqueue(
                RuntimeEventType.EVENT_GAP,
                payload={"reason": RuntimeContinuityReason.EVENT_ATTRIBUTION.value},
            )
            return
        if not isinstance(payload, dict):
            return
        payload = self._object(payload)
        if isinstance(payload.get("data"), str):
            try:
                inner: Any = json.loads(payload["data"])
            except json.JSONDecodeError:
                inner = None
            inner_payload = self._object(inner)
            if inner_payload:
                payload = {**payload, **inner_payload}

        runtime_type = payload.get("type") or payload.get("event") or event_name
        if not isinstance(runtime_type, str) or not runtime_type:
            return
        properties = self._object(payload.get("properties"))
        if not properties:
            properties = self._object(payload.get("data"))
        if not properties:
            properties = payload

        directory = self._event_directory(payload, properties)
        if directory is not None and directory != active.workspace_root:
            return
        session_id = self._event_session_id(payload, properties, runtime_type)
        if session_id is None:
            if runtime_type.lower().startswith(("server.", "global.", "health.")):
                return
            if any(marker in runtime_type.lower() for marker in _RELEVANT_EVENT_MARKERS):
                active.mark_incomplete(RuntimeContinuityReason.EVENT_ATTRIBUTION)
                active.enqueue(
                    RuntimeEventType.EVENT_GAP,
                    raw_event_type=runtime_type,
                    payload={"reason": RuntimeContinuityReason.EVENT_ATTRIBUTION.value},
                )
            return
        if session_id != active.runtime_session.session_id:
            return

        event_type, status = self._normalize_event_type(runtime_type, properties)
        if status is not None:
            active.runtime_status = status
            active.terminal = status in {
                RuntimeStatus.SUCCEEDED,
                RuntimeStatus.FAILED,
                RuntimeStatus.BLOCKED,
                RuntimeStatus.CANCELLED,
            }
        active.enqueue(
            event_type,
            raw_event_type=runtime_type,
            payload=self._safe_event_payload(properties),
        )

    async def _consume_events(
        self, active: _ActiveExecution
    ) -> AsyncIterator[RuntimeEventEnvelope]:
        while True:
            try:
                event = active.queue.get_nowait()
            except asyncio.QueueEmpty:
                active.flush_overflow_gap()
                if active.closed and active.queue.empty():
                    return
                active.wake.clear()
                if not active.queue.empty() or active.closed:
                    continue
                await active.wake.wait()
            else:
                yield event
                active.flush_overflow_gap()

    async def _close_active(self, active: _ActiveExecution) -> None:
        response = active.response
        if response is not None:
            await response.aclose()
        task = active.pump_task
        if task is not None and not task.done():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        active.closed = True
        active.wake.set()

    async def _discard_active(self, execution_id: str, active: _ActiveExecution) -> None:
        """Dispose an observer after a definite prompt rejection."""

        await self._close_active(active)
        if self._active.get(execution_id) is active:
            self._active.pop(execution_id, None)

    def _validate_binding(
        self,
        request: RuntimeExecutionRequest,
        binding: RuntimeSessionBinding,
    ) -> None:
        known_binding = self._bindings.get(request.basis.execution_id)
        if (
            binding.execution_id != request.basis.execution_id
            or binding.request_digest != request.request_digest
            or binding.workspace_id != request.basis.workspace.workspace_id
            or binding.runtime_session.runtime_id != request.basis.runtime_selection.runtime_id
            or request.request_digest != self._recompute_digest(request)
            or (known_binding is not None and binding != known_binding)
        ):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Runtime session binding does not match the exact execution request.",
                execution_id=request.basis.execution_id,
                runtime_session=binding.runtime_session,
            )
        self._validate_session_runtime(binding.runtime_session)

    def _validate_v2_binding(
        self,
        request: RuntimeRequestV2,
        binding: RuntimeSessionBinding,
    ) -> None:
        known = self._v2_bindings.get(request.request.basis.execution_id)
        if (
            known is None
            or known[0] != request.request_digest_v2
            or known[1] != binding
            or binding.request_digest_v2 != request.request_digest_v2
            or binding.execution_id != request.request.basis.execution_id
            or binding.request_digest != request.request.request_digest
            or binding.runtime_session.runtime_id
            != request.request.basis.runtime_selection.runtime_id
        ):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Runtime session binding does not match the exact V2 request.",
                execution_id=request.request.basis.execution_id,
                runtime_session=binding.runtime_session,
            )
        self._validate_session_runtime(binding.runtime_session)

    @staticmethod
    def _descriptor_digest(descriptor: RuntimeDescriptor) -> str:
        payload = json.dumps(
            descriptor.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(payload).hexdigest()

    def _validate_permission_profile(
        self,
        reference: RuntimePermissionProfileRef,
        execution_id: str,
    ) -> None:
        if reference != self._permission_profile.reference:
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Execution permission profile does not match configured OpenCode profile.",
                execution_id=execution_id,
            )
        if self._permission_profile.ask:
            raise fail(
                RuntimeFailureCategory.AGENT_BLOCKED,
                "OpenCode profile requires interactive permission approval and is unsupported.",
                execution_id=execution_id,
            )

    def _validate_request_digest(self, request: RuntimeExecutionRequest) -> None:
        if request.request_digest != self._recompute_digest(request):
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Request digest does not match the exact execution basis.",
                execution_id=request.basis.execution_id,
            )

    def _require_capabilities(
        self,
        descriptor: RuntimeDescriptor,
        request: RuntimeExecutionRequest,
        execution_id: str,
    ) -> None:
        if request.basis.runtime_selection.runtime_id != descriptor.runtime_id:
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Requested runtime identity does not match this OpenCode adapter.",
                execution_id=execution_id,
            )
        required = {
            RuntimeCapability.SESSION_CREATE,
            RuntimeCapability.EXECUTE,
            RuntimeCapability.EVENT_STREAM,
            RuntimeCapability.CANCEL,
            RuntimeCapability.RESULT_INSPECTION,
            *request.basis.required_capabilities,
        }
        missing = required.difference(descriptor.capabilities)
        if missing:
            raise fail(
                RuntimeFailureCategory.UNSUPPORTED_CAPABILITY,
                "OpenCode profile does not support all required runtime capabilities.",
                execution_id=execution_id,
            )

    def _active_for_handle(self, handle: RuntimeExecutionHandle) -> _ActiveExecution:
        self._validate_session_runtime(handle.runtime_session)
        active = self._active.get(handle.execution_id)
        if active is None or active.handle != handle:
            raise fail(
                RuntimeFailureCategory.SESSION_BINDING_REQUIRED,
                "Exact process-local execution binding is required for this operation.",
                execution_id=handle.execution_id,
                runtime_session=handle.runtime_session,
            )
        return active

    def _validate_session_runtime(self, runtime_session: RuntimeSessionRef) -> None:
        if runtime_session.runtime_id != OPENCODE_RUNTIME_ID:
            raise fail(
                RuntimeFailureCategory.REQUEST_CONFLICT,
                "Runtime session belongs to a different runtime identity.",
                runtime_session=runtime_session,
            )

    def _requested_for(self, execution_id: str, identity: str) -> str:
        requested = self._requested_identities.get(execution_id)
        if requested is None:
            raise fail(
                RuntimeFailureCategory.SESSION_BINDING_REQUIRED,
                "Exact execution request provenance is not available in this process.",
                execution_id=execution_id,
            )
        active = self._active.get(execution_id)
        if active is not None and active.request_digest != requested[2]:
            raise fail(
                RuntimeFailureCategory.SESSION_BINDING_REQUIRED,
                "Exact execution request provenance is not available in this process.",
                execution_id=execution_id,
            )
        return requested[0 if identity == "provider" else 1]

    def _event_directory(self, payload: dict[str, Any], properties: dict[str, Any]) -> str | None:
        for container in (
            payload,
            properties,
            self._object(properties.get("info")),
            self._object(properties.get("location")),
        ):
            directory = container.get("directory")
            if isinstance(directory, str):
                return directory
        session = self._object(properties.get("session"))
        location = self._object(session.get("location"))
        directory = location.get("directory")
        return directory if isinstance(directory, str) else None

    def _event_session_id(
        self,
        payload: dict[str, Any],
        properties: dict[str, Any],
        runtime_type: str,
    ) -> str | None:
        containers = (
            properties,
            self._object(properties.get("info")),
            self._object(properties.get("part")),
            self._object(properties.get("message")),
            self._object(properties.get("session")),
            payload,
        )
        for container in containers:
            for key in ("sessionID", "sessionId", "session_id"):
                value = container.get(key)
                if isinstance(value, str):
                    return value
        session_value = containers[4].get("id")
        if isinstance(session_value, str):
            return session_value
        if runtime_type.lower().startswith("session."):
            info_value = containers[1].get("id")
            if isinstance(info_value, str):
                return info_value
        return None

    def _normalize_event_type(
        self,
        runtime_type: str,
        properties: dict[str, Any],
    ) -> tuple[RuntimeEventType, RuntimeStatus | None]:
        lowered = runtime_type.lower()
        status_value = properties.get("status")
        if isinstance(status_value, dict):
            status_data = self._object(status_value)
            status_value = status_data.get("type") or status_data.get("status")
        if not isinstance(status_value, str):
            status_value = ""
        status_lower = status_value.lower()

        if "permission" in lowered:
            permission = self._object(properties.get("permission"))
            effect = permission.get("effect") or properties.get("effect")
            if isinstance(effect, str) and effect.lower() == "deny":
                return RuntimeEventType.EXECUTION_BLOCKED, RuntimeStatus.BLOCKED
            return RuntimeEventType.PERMISSION_REQUIRED, RuntimeStatus.BLOCKED
        if "tool" in lowered:
            if any(
                marker in lowered for marker in ("completed", "finished", "result")
            ) or status_lower in {
                "completed",
                "complete",
                "success",
                "done",
            }:
                return RuntimeEventType.TOOL_COMPLETED, RuntimeStatus.RUNNING
            return RuntimeEventType.TOOL_REQUESTED, RuntimeStatus.RUNNING
        if any(marker in lowered for marker in ("error", "failed")) or status_lower in {
            "error",
            "failed",
        }:
            return RuntimeEventType.EXECUTION_FAILED, RuntimeStatus.FAILED
        if any(marker in lowered for marker in ("aborted", "cancelled", "canceled")):
            return RuntimeEventType.EXECUTION_CANCELLED, RuntimeStatus.CANCELLED
        if any(marker in lowered for marker in ("completed", "succeeded", "finished")):
            return RuntimeEventType.EXECUTION_COMPLETED, RuntimeStatus.SUCCEEDED
        if status_lower in {"idle", "ready"} or lowered.endswith(".idle"):
            return RuntimeEventType.EXECUTION_IDLE, None
        if status_lower in {"busy", "running"}:
            return RuntimeEventType.EXECUTION_STARTED, RuntimeStatus.RUNNING
        if "created" in lowered or "started" in lowered:
            return RuntimeEventType.EXECUTION_STARTED, RuntimeStatus.RUNNING
        return RuntimeEventType.PROGRESS, None

    def _safe_event_payload(self, properties: dict[str, Any]) -> dict[str, str | int | bool | None]:
        safe: dict[str, str | int | bool | None] = {}
        status = properties.get("status")
        if isinstance(status, dict):
            status_data = self._object(status)
            status = status_data.get("type") or status_data.get("status")
        if isinstance(status, str) and status.lower() in _SAFE_EVENT_STATUSES:
            safe["status"] = status.lower()

        part = self._object(properties.get("part"))
        tool = part.get("tool") or properties.get("tool")
        if isinstance(tool, str) and tool.lower() in _SAFE_TOOL_NAMES:
            safe["tool"] = tool.lower()

        count = properties.get("count")
        if isinstance(count, int) and not isinstance(count, bool) and 0 <= count <= 1_000_000:
            safe["count"] = count
        return safe

    def _actual_model_identity(self, data: dict[str, Any]) -> tuple[str | None, str | None]:
        model = self._object(data.get("model"))
        provider = model.get("providerID")
        model_id = model.get("id")
        return (
            provider
            if isinstance(provider, str) and provider.strip() and len(provider) <= 128
            else None,
            model_id
            if isinstance(model_id, str) and model_id.strip() and len(model_id) <= 128
            else None,
        )

    def _runtime_usage(self, data: dict[str, Any]) -> RuntimeUsage | None:
        tokens = self._object(data.get("tokens"))
        cache = self._object(tokens.get("cache"))
        fields = {
            "input_tokens": tokens.get("input"),
            "output_tokens": tokens.get("output"),
            "reasoning_tokens": tokens.get("reasoning"),
            "cache_read_tokens": cache.get("read"),
            "cache_write_tokens": cache.get("write"),
        }
        normalized: dict[str, int] = {}
        for key, value in fields.items():
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                normalized[key] = value
        if not normalized:
            return None
        return RuntimeUsage(
            input_tokens=normalized.get("input_tokens"),
            output_tokens=normalized.get("output_tokens"),
            reasoning_tokens=normalized.get("reasoning_tokens"),
            cache_read_tokens=normalized.get("cache_read_tokens"),
            cache_write_tokens=normalized.get("cache_write_tokens"),
        )

    def _diff_hint(self, data: dict[str, Any]) -> str | None:
        candidates: list[object] = []
        diff = data.get("diff")
        if isinstance(diff, list):
            candidates.extend(cast(list[Any], diff))
        paths: set[str] = set()
        for item in candidates:
            file_path = self._object(item).get("file")
            if isinstance(file_path, str):
                paths.add(file_path)
        if not paths:
            return None
        return f"OpenCode reported {len(paths)} session file change hint(s)."

    def _runtime_status_from(self, value: Any) -> RuntimeStatus:
        if isinstance(value, dict):
            status = self._object(value)
            value = status.get("type") or status.get("status")
        if not isinstance(value, str):
            return RuntimeStatus.UNKNOWN
        normalized = value.lower()
        if normalized in {"busy", "running", "working"}:
            return RuntimeStatus.RUNNING
        if normalized in {"success", "succeeded", "completed", "complete"}:
            return RuntimeStatus.SUCCEEDED
        if normalized in {"error", "failed", "failure"}:
            return RuntimeStatus.FAILED
        if normalized in {"blocked", "permission_required", "permission"}:
            return RuntimeStatus.BLOCKED
        if normalized in {"cancelled", "canceled", "aborted"}:
            return RuntimeStatus.CANCELLED
        return RuntimeStatus.UNKNOWN

    def _identity_completeness(
        self,
        actual_provider: str | None,
        actual_model: str | None,
    ) -> RuntimeIdentityCompleteness:
        if actual_provider is not None and actual_model is not None:
            return RuntimeIdentityCompleteness.FULL
        if actual_provider is not None or actual_model is not None:
            return RuntimeIdentityCompleteness.PARTIAL
        return RuntimeIdentityCompleteness.UNKNOWN

    def _read_json(
        self,
        response: httpx.Response,
        category: RuntimeFailureCategory,
    ) -> dict[str, Any]:
        try:
            payload: Any = response.json()
        except json.JSONDecodeError, UnicodeDecodeError:
            raise fail(category, "OpenCode returned a malformed JSON response.") from None
        if not isinstance(payload, dict):
            raise fail(category, "OpenCode returned an unexpected response shape.")
        return self._object(payload)

    def _unwrap_data(self, payload: dict[str, Any]) -> dict[str, Any] | bool:
        data = payload.get("data", payload)
        if isinstance(data, bool):
            return data
        if isinstance(data, dict):
            return self._object(data)
        raise fail(
            RuntimeFailureCategory.TRANSPORT, "OpenCode returned an unexpected response shape."
        )

    def _session_id_from(self, data: dict[str, Any] | bool) -> str | None:
        if isinstance(data, bool):
            return None
        for key in ("sessionID", "sessionId", "id"):
            value = data.get(key)
            if isinstance(value, str) and value.strip() and len(value) <= 128:
                return value
            if isinstance(value, dict):
                nested = self._object(value).get("id")
                if isinstance(nested, str) and nested.strip() and len(nested) <= 128:
                    return nested
        return None

    def _recompute_digest(self, request: RuntimeExecutionRequest) -> str:
        from relay_engine.agent_runtime.models import digest_execution_basis

        return digest_execution_basis(request.basis)

    def _http_failure_category(self, status_code: int) -> RuntimeFailureCategory:
        if status_code == 401:
            return RuntimeFailureCategory.AUTHENTICATION
        if status_code == 403:
            return RuntimeFailureCategory.PERMISSION_DENIED
        if status_code in {408, 504}:
            return RuntimeFailureCategory.TIMEOUT
        if status_code in {429, 502, 503}:
            return RuntimeFailureCategory.RUNTIME_UNAVAILABLE
        return RuntimeFailureCategory.TRANSPORT

    def _url(self, path: str) -> httpx.URL:
        base = str(self._endpoint).rstrip("/")
        return httpx.URL(f"{base}{path}")

    def _session_url(self, runtime_session: RuntimeSessionRef, suffix: str) -> httpx.URL:
        encoded_session = quote(runtime_session.session_id, safe="")
        return self._url(f"/api/session/{encoded_session}{suffix}")

    def _unwrap_object(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = self._unwrap_data(payload)
        if isinstance(data, bool):
            raise fail(
                RuntimeFailureCategory.TRANSPORT,
                "OpenCode returned an unexpected response shape.",
            )
        return data

    def _object(self, value: Any) -> dict[str, Any]:
        return cast(dict[str, Any], value) if isinstance(value, dict) else {}
