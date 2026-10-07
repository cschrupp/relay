"""Deterministic mocked HTTP and event-stream tests for the OpenCode adapter."""

import asyncio
import json
from datetime import UTC, datetime

import httpx
import pytest

from relay_engine.agent_runtime.errors import AgentRuntimeError
from relay_engine.agent_runtime.models import (
    EventContinuity,
    RuntimeCancelRequest,
    RuntimeCapability,
    RuntimeContinuityReason,
    RuntimeContinuityState,
    RuntimeControlAckState,
    RuntimeEventType,
    RuntimeExecutionBasis,
    RuntimeExecutionHandle,
    RuntimeExecutionInspection,
    RuntimeExecutionRequest,
    RuntimeIdentityCompleteness,
    RuntimePermissionProfileRef,
    RuntimeSelection,
    RuntimeSessionBinding,
    RuntimeSessionRef,
    RuntimeStatus,
    RuntimeWorkspaceAttachment,
    digest_execution_basis,
)
from relay_engine.agent_runtime.opencode import OpenCodePermissionProfile, OpenCodeRuntime
from relay_engine.domain import CommitRef, RepositoryRef

EXECUTION_ID = "exec_018f47c1-7b2c-7abc-8def-123456789021"
SLICE_ID = "slc_018f47c1-7b2c-7abc-8def-123456789022"
BASELINE_ID = "base_018f47c1-7b2c-7abc-8def-123456789023"
REPOSITORY_ID = "repo_018f47c1-7b2c-7abc-8def-123456789024"
COMMIT_SHA = "e8598ae5ffb046d4131e04655a0c063ff1e41ccc"
DIGEST = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
ROOT = "/tmp/opencode-adapter-test"
SESSION_ID = "ses_runtime_test"
AUTH_SENTINEL = "fake-auth-sentinel-never-return-this"


def execution_request() -> RuntimeExecutionRequest:
    repository = RepositoryRef(id=REPOSITORY_ID, host="github.com", path="team/project")
    basis = RuntimeExecutionBasis(
        execution_id=EXECUTION_ID,
        slice_id=SLICE_ID,
        source_baseline_id=BASELINE_ID,
        workspace=RuntimeWorkspaceAttachment(
            workspace_id="workspace-test",
            root=ROOT,
            repository=repository,
            source_commit=CommitRef(repository=repository, sha=COMMIT_SHA),
        ),
        input_payload={
            "text": "Perform one bounded mocked task.",
            "payload_digest": DIGEST,
            "attachment_refs": (),
        },
        runtime_selection=RuntimeSelection(
            runtime_id="opencode",
            requested_provider_id="requested-provider",
            requested_model_id="requested-model",
        ),
        permission_profile_ref=RuntimePermissionProfileRef(
            profile_id="safe-noninteractive",
            content_digest=DIGEST,
        ),
    )
    return RuntimeExecutionRequest(basis=basis, request_digest=digest_execution_basis(basis))


def permission_profile(*, ask: tuple[str, ...] = ()) -> OpenCodePermissionProfile:
    request = execution_request()
    return OpenCodePermissionProfile(
        reference=request.basis.permission_profile_ref,
        agent_id="relay-safe-agent",
        allow=("read", "edit"),
        deny=("external_directory", "git_push"),
        ask=ask,
    )


class QueueEventStream(httpx.AsyncByteStream):
    """In-process event stream controlled by the deterministic test."""

    def __init__(self) -> None:
        self._chunks: asyncio.Queue[bytes | None] = asyncio.Queue()
        self._finished = False
        self.events: list[dict[str, object]] = []

    def feed(self, event: dict[str, object]) -> None:
        self.events.append(event)
        payload = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
        self._chunks.put_nowait(f"data: {payload}\n\n".encode())

    def finish(self) -> None:
        if not self._finished:
            self._finished = True
            self._chunks.put_nowait(None)

    async def __aiter__(self):
        while True:
            chunk = await self._chunks.get()
            if chunk is None:
                return
            yield chunk

    async def aclose(self) -> None:
        self.finish()


class MockOpenCodeServer:
    """Small explicit V2 endpoint model that records all adapter HTTP requests."""

    def __init__(
        self,
        *,
        prompt_events: tuple[dict[str, object], ...] = (),
        prompt_status: int = 200,
        close_events_after_prompt: bool = False,
        inspection: dict[str, object] | None = None,
        runtime_version: str = "1.2.3",
        health_status: int = 200,
        malformed_session_response: bool = False,
    ) -> None:
        self.requests: list[httpx.Request] = []
        self.stream = QueueEventStream()
        self.prompt_events = prompt_events
        self.prompt_status = prompt_status
        self.close_events_after_prompt = close_events_after_prompt
        self.inspection = inspection or {"data": {"status": "busy"}}
        self.runtime_version = runtime_version
        self.health_status = health_status
        self.malformed_session_response = malformed_session_response
        self.event_observer_ready = False
        self.prompt_bodies: list[dict[str, object]] = []
        self.prompt_effects: list[str] = []

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.url.path == "/api/health":
            return httpx.Response(
                self.health_status,
                json={
                    "healthy": self.health_status == 200,
                    "version": self.runtime_version,
                    "pid": 7,
                    "message": AUTH_SENTINEL,
                },
            )
        if request.url.path == "/api/session" and request.method == "POST":
            body = json.loads(request.content)
            assert "prompt" not in body
            assert body["location"]["directory"] == ROOT
            assert body["model"] == {
                "id": "requested-model",
                "providerID": "requested-provider",
            }
            assert body["agent"] == "relay-safe-agent"
            if self.malformed_session_response:
                return httpx.Response(200, text=AUTH_SENTINEL)
            return httpx.Response(
                200,
                json={"data": {"id": SESSION_ID, "location": {"directory": ROOT}}},
            )
        if request.url.path == "/api/event" and request.method == "GET":
            self.event_observer_ready = True
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=self.stream,
            )
        if request.url.path == f"/api/session/{SESSION_ID}/prompt":
            assert self.event_observer_ready
            body = json.loads(request.content)
            prompt_body = {
                "text": "Perform one bounded mocked task.",
                "files": [],
                "agents": [],
                "skills": [],
                "metadata": {},
            }
            assert {key: body[key] for key in prompt_body} == prompt_body
            assert set(body) <= {*prompt_body, "resume"}
            assert body.get("resume") in (None, False, True)
            assert "prompt" not in body
            self.prompt_bodies.append(body)
            if self.prompt_status == 200:
                self.stream.feed(
                    {
                        "type": "session.inbox.enqueued",
                        "properties": {"sessionID": SESSION_ID},
                    }
                )
                self.prompt_effects.append("admission")
                if body.get("resume") is not False:
                    self.stream.feed(
                        {
                            "type": "session.execution.started",
                            "properties": {"sessionID": SESSION_ID},
                        }
                    )
                    self.prompt_effects.append("execution_wake")
                    for event in self.prompt_events:
                        self.stream.feed(event)
                if self.close_events_after_prompt:
                    self.stream.finish()
                response_body = {
                    "data": {
                        "id": "msg_mock_admitted_user_1",
                        "sessionID": SESSION_ID,
                        "timeCreated": 1_728_000_000_000,
                        "type": "user",
                        "payload": {
                            "text": body["text"],
                            "files": body["files"],
                            "agents": body["agents"],
                            "skills": body["skills"],
                            "metadata": body["metadata"],
                        },
                        "delivery": "steer",
                    }
                }
            elif self.prompt_status == 400:
                response_body = {
                    "error": {
                        "kind": "Payload",
                        "message": "Invalid request payload schema",
                    }
                }
            else:
                response_body = {"error": AUTH_SENTINEL}
            return httpx.Response(self.prompt_status, json=response_body)
        if request.url.path == f"/api/session/{SESSION_ID}/interrupt":
            return httpx.Response(200, json={"data": True})
        if request.url.path == f"/api/session/{SESSION_ID}" and request.method == "GET":
            return httpx.Response(200, json=self.inspection)
        raise AssertionError(f"Unexpected OpenCode request: {request.method} {request.url.path}")


def setup_runtime(
    server: MockOpenCodeServer,
    *,
    event_buffer_size: int = 16,
    auth_header: bool = False,
) -> tuple[OpenCodeRuntime, httpx.AsyncClient]:
    headers = {"Authorization": f"Bearer {AUTH_SENTINEL}"} if auth_header else None
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(server.handle),
        headers=headers,
    )
    runtime = OpenCodeRuntime(
        "http://opencode.mock:4096",
        expected_runtime_version="1.2.3",
        permission_profile=permission_profile(),
        client=client,
        event_buffer_size=event_buffer_size,
    )
    return runtime, client


async def create_open_execution(
    runtime: OpenCodeRuntime,
    request: RuntimeExecutionRequest | None = None,
) -> tuple[RuntimeExecutionRequest, RuntimeSessionBinding, object]:
    exact_request = execution_request() if request is None else request
    binding = await runtime.create_session(exact_request)
    handle = await runtime.open_execution(exact_request, binding)
    return exact_request, binding, handle


async def wait_until(predicate, *, attempts: int = 100) -> None:
    for _ in range(attempts):
        if predicate():
            return
        await asyncio.sleep(0)
    raise AssertionError("condition was not reached by deterministic event pump")


@pytest.mark.parametrize("version", ["0.0.1", "2.0.0"])
def test_runtime_version_mismatch_fails_before_session_creation_without_api_fallback(
    version: str,
) -> None:
    server = MockOpenCodeServer(runtime_version=version)
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.create_session(execution_request())
            assert exc_info.value.failure.category.value == "UNSUPPORTED_RUNTIME_VERSION"
            assert [request.url.path for request in server.requests] == ["/api/health"]
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_missing_v2_health_endpoint_fails_without_v1_fallback() -> None:
    server = MockOpenCodeServer(health_status=404)
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.create_session(execution_request())
            assert exc_info.value.failure.category.value == "UNSUPPORTED_RUNTIME_VERSION"
            assert [request.url.path for request in server.requests] == ["/api/health"]
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_session_and_prompt_mapping_observe_before_admission_and_wake_execution() -> None:
    started_event = {
        "type": "session.status",
        "properties": {"sessionID": SESSION_ID, "status": {"type": "busy"}},
    }
    server = MockOpenCodeServer(prompt_events=(started_event,))
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            request, binding, handle = await create_open_execution(runtime)
            assert binding.request_digest == request.request_digest
            assert handle.runtime_session == binding.runtime_session
            assert handle.runtime_invocation is None
            assert server.prompt_bodies == [
                {
                    "text": "Perform one bounded mocked task.",
                    "files": [],
                    "agents": [],
                    "skills": [],
                    "metadata": {},
                }
            ]
            assert "resume" not in server.prompt_bodies[0]
            assert server.prompt_effects == ["admission", "execution_wake"]
            assert [request.url.path for request in server.requests] == [
                "/api/health",
                "/api/session",
                "/api/health",
                "/api/event",
                f"/api/session/{SESSION_ID}/prompt",
            ]
            prompt_posts = [
                item
                for item in server.requests
                if item.method == "POST" and item.url.path.endswith("/prompt")
            ]
            assert len(prompt_posts) == 1
            assert server.requests.index(prompt_posts[0]) > next(
                index
                for index, item in enumerate(server.requests)
                if item.method == "GET" and item.url.path == "/api/event"
            )
            active = runtime._active[EXECUTION_ID]
            await wait_until(lambda: active.sequence == 3)
            event_iterator = runtime.events(handle)
            observed = [await asyncio.wait_for(anext(event_iterator), timeout=1) for _ in range(3)]
            assert [event.event_type for event in observed] == [
                RuntimeEventType.PROGRESS,
                RuntimeEventType.EXECUTION_STARTED,
                RuntimeEventType.EXECUTION_STARTED,
            ]
            assert [event.raw_event_type for event in observed] == [
                "session.inbox.enqueued",
                "session.execution.started",
                "session.status",
            ]
            assert [event.sequence for event in observed] == [1, 2, 3]
            await event_iterator.aclose()

            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.open_execution(request, binding)
            assert exc_info.value.failure.category.value == "REQUEST_CONFLICT"
            assert len(server.requests) == 5
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_resume_false_models_admission_without_execution_wake() -> None:
    server = MockOpenCodeServer()
    server.event_observer_ready = True
    prompt_body = {
        "text": "Perform one bounded mocked task.",
        "files": [],
        "agents": [],
        "skills": [],
        "metadata": {},
        "resume": False,
    }
    request = httpx.Request(
        "POST",
        f"http://opencode.mock:4096/api/session/{SESSION_ID}/prompt",
        json=prompt_body,
    )

    response = server.handle(request)

    assert response.status_code == 200
    assert server.prompt_bodies == [prompt_body]
    assert server.prompt_effects == ["admission"]
    assert [event["type"] for event in server.stream.events] == ["session.inbox.enqueued"]
    assert response.json()["data"]["type"] == "user"
    assert response.json()["data"]["id"] == "msg_mock_admitted_user_1"


def test_unrelated_events_are_ignored_and_ambiguous_events_mark_incomplete() -> None:
    events = (
        {
            "type": "message.updated",
            "properties": {"sessionID": "ses_another", "directory": ROOT},
        },
        {"type": "server.connected", "properties": {"directory": ROOT}},
        {"type": "tool.execute", "properties": {"directory": ROOT}},
        {
            "type": "message.updated",
            "properties": {"sessionID": SESSION_ID, "directory": "/tmp/outside"},
        },
        {
            "type": "message.updated",
            "properties": {"sessionID": SESSION_ID, "directory": ROOT},
        },
    )
    server = MockOpenCodeServer(prompt_events=events)
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            _, _, handle = await create_open_execution(runtime)
            active = runtime._active[EXECUTION_ID]
            await wait_until(lambda: active.sequence == 4)
            event_iterator = runtime.events(handle)
            observed = [
                await asyncio.wait_for(anext(event_iterator), timeout=1),
                await asyncio.wait_for(anext(event_iterator), timeout=1),
                await asyncio.wait_for(anext(event_iterator), timeout=1),
                await asyncio.wait_for(anext(event_iterator), timeout=1),
            ]
            await event_iterator.aclose()
            assert [event.sequence for event in observed] == [1, 2, 3, 4]
            assert [event.event_type for event in observed] == [
                RuntimeEventType.PROGRESS,
                RuntimeEventType.EXECUTION_STARTED,
                RuntimeEventType.EVENT_GAP,
                RuntimeEventType.PROGRESS,
            ]
            continuity = runtime.continuity(handle)
            assert continuity.state is RuntimeContinuityState.INCOMPLETE
            assert continuity.reason is RuntimeContinuityReason.EVENT_ATTRIBUTION
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_queue_overflow_emits_gap_when_space_becomes_available() -> None:
    events = tuple(
        {
            "type": "message.updated",
            "properties": {"sessionID": SESSION_ID, "directory": ROOT, "sequence": index},
        }
        for index in range(3)
    )
    server = MockOpenCodeServer(prompt_events=events)
    runtime, client = setup_runtime(server, event_buffer_size=1)

    async def exercise() -> None:
        try:
            _, _, handle = await create_open_execution(runtime)
            active = runtime._active[EXECUTION_ID]
            await wait_until(lambda: active.overflow_gap_pending)
            event_iterator = runtime.events(handle)
            first = await asyncio.wait_for(anext(event_iterator), timeout=1)
            gap = await asyncio.wait_for(anext(event_iterator), timeout=1)
            await event_iterator.aclose()
            assert first.event_type is RuntimeEventType.PROGRESS
            assert gap.event_type is RuntimeEventType.EVENT_GAP
            assert gap.sequence > first.sequence
            assert runtime.continuity(handle) == EventContinuity(
                state=RuntimeContinuityState.INCOMPLETE,
                reason=RuntimeContinuityReason.BUFFER_OVERFLOW,
            )
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_stream_disconnect_emits_gap_without_claiming_replay() -> None:
    server = MockOpenCodeServer(
        prompt_events=(
            {
                "type": "session.status",
                "properties": {"sessionID": SESSION_ID, "status": {"type": "busy"}},
            },
        ),
        close_events_after_prompt=True,
    )
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            _, _, handle = await create_open_execution(runtime)
            active = runtime._active[EXECUTION_ID]
            await wait_until(lambda: active.closed)
            iterator = runtime.events(handle)
            observed = [
                await asyncio.wait_for(anext(iterator), timeout=1),
                await asyncio.wait_for(anext(iterator), timeout=1),
                await asyncio.wait_for(anext(iterator), timeout=1),
                await asyncio.wait_for(anext(iterator), timeout=1),
            ]
            await iterator.aclose()
            assert [event.event_type for event in observed] == [
                RuntimeEventType.PROGRESS,
                RuntimeEventType.EXECUTION_STARTED,
                RuntimeEventType.EXECUTION_STARTED,
                RuntimeEventType.EVENT_GAP,
            ]
            assert runtime.continuity(handle).state is RuntimeContinuityState.INCOMPLETE
            assert runtime.continuity(handle).reason is RuntimeContinuityReason.STREAM_DISCONNECTED
            assert RuntimeCapability.EVENT_REPLAY not in (await runtime.describe()).capabilities
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_event_observer_failure_prevents_prompt_admission() -> None:
    server = MockOpenCodeServer()
    original_handler = server.handle

    def no_event_stream(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/event":
            server.requests.append(request)
            return httpx.Response(404, json={"message": AUTH_SENTINEL})
        return original_handler(request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(no_event_stream))
    runtime = OpenCodeRuntime(
        "http://opencode.mock:4096",
        expected_runtime_version="1.2.3",
        permission_profile=permission_profile(),
        client=client,
    )

    async def exercise() -> None:
        try:
            request = execution_request()
            binding = await runtime.create_session(request)
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.open_execution(request, binding)
            assert exc_info.value.failure.category.value == "EVENT_OBSERVATION_UNAVAILABLE"
            assert f"/api/session/{SESSION_ID}/prompt" not in [
                item.url.path for item in server.requests
            ]
            assert AUTH_SENTINEL not in str(exc_info.value)
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


@pytest.mark.parametrize("error_type", [httpx.ReadTimeout, httpx.ConnectError])
def test_uncertain_prompt_admission_returns_recoverable_exact_handle(
    error_type: type[httpx.RequestError],
) -> None:
    server = MockOpenCodeServer(inspection={"data": {"status": "busy"}})
    prompt_path = f"/api/session/{SESSION_ID}/prompt"
    prompt_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == prompt_path:
            server.requests.append(request)
            prompt_requests.append(request)
            raise error_type(AUTH_SENTINEL, request=request)
        return server.handle(request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    runtime = OpenCodeRuntime(
        "http://opencode.mock:4096",
        expected_runtime_version="1.2.3",
        permission_profile=permission_profile(),
        client=client,
    )

    async def exercise() -> None:
        try:
            request = execution_request()
            binding = await runtime.create_session(request)
            handle = await runtime.open_execution(request, binding)
            assert handle.execution_id == request.basis.execution_id
            assert handle.runtime_session == binding.runtime_session
            assert handle.request_digest == request.request_digest
            assert runtime._active[EXECUTION_ID].handle == handle

            with pytest.raises(AgentRuntimeError) as retry_info:
                await runtime.open_execution(request, binding)
            assert retry_info.value.failure.category.value == "REQUEST_CONFLICT"
            assert len(prompt_requests) == 1

            wrong_session = RuntimeSessionRef(runtime_id="opencode", session_id="ses_other")
            wrong_handle = handle.model_copy(update={"runtime_session": wrong_session})
            with pytest.raises(AgentRuntimeError) as inspect_info:
                await runtime.inspect(wrong_handle)
            assert inspect_info.value.failure.category.value == "REQUEST_CONFLICT"
            with pytest.raises(AgentRuntimeError) as cancel_info:
                await runtime.cancel(
                    RuntimeCancelRequest(
                        execution_id=request.basis.execution_id,
                        runtime_session=wrong_session,
                        reason="must stay on the exact session",
                    )
                )
            assert cancel_info.value.failure.category.value == "REQUEST_CONFLICT"
            assert not any(
                item.method == "GET" and item.url.path.startswith("/api/session/")
                for item in server.requests
            )
            assert not any(item.url.path.endswith("/interrupt") for item in server.requests)

            inspection = await runtime.inspect(handle)
            assert inspection.execution_id == request.basis.execution_id
            assert inspection.runtime_session == binding.runtime_session
            cancel_ack = await runtime.cancel(
                RuntimeCancelRequest(
                    execution_id=request.basis.execution_id,
                    runtime_session=binding.runtime_session,
                    reason="resolve uncertain admission",
                )
            )
            assert cancel_ack.state is RuntimeControlAckState.REQUESTED
            assert len(prompt_requests) == 1
            assert any(
                item.method == "GET" and item.url.path == f"/api/session/{SESSION_ID}"
                for item in server.requests
            )
            assert any(item.url.path.endswith("/interrupt") for item in server.requests)
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


@pytest.mark.parametrize(
    ("status_code", "failure_category"),
    [(400, "CONFIGURATION"), (403, "PERMISSION_DENIED")],
)
def test_definite_prompt_rejection_disposes_event_observer(
    status_code: int,
    failure_category: str,
) -> None:
    server = MockOpenCodeServer(prompt_status=status_code)
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            request = execution_request()
            binding = await runtime.create_session(request)
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.open_execution(request, binding)
            assert exc_info.value.failure.category.value == failure_category
            assert EXECUTION_ID not in runtime._active
            assert server.stream._finished
            prompt_calls = [item for item in server.requests if item.url.path.endswith("/prompt")]
            assert len(prompt_calls) == 1

            with pytest.raises(AgentRuntimeError) as retry_info:
                await runtime.open_execution(request, binding)
            assert retry_info.value.failure.category.value == "REQUEST_CONFLICT"
            assert len([item for item in server.requests if item.url.path.endswith("/prompt")]) == 1
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_inspection_is_independent_and_preserves_requested_vs_actual_identity() -> None:
    session_data = {
        "data": {
            "status": "completed",
            "summary": AUTH_SENTINEL,
            "model": {"providerID": "actual-provider", "id": "actual-model"},
            "tokens": {
                "input": 10,
                "output": 20,
                "reasoning": 3,
                "cache": {"read": 4, "write": 5},
            },
            "diff": [{"file": "src/safe.py", "patch": AUTH_SENTINEL}],
        }
    }
    server = MockOpenCodeServer(inspection=session_data)
    runtime, client = setup_runtime(server, auth_header=True)

    async def exercise() -> None:
        try:
            request, _, handle = await create_open_execution(runtime)
            # The event queue is deliberately not consumed before inspection.
            inspection = await runtime.inspect(handle)
            assert isinstance(inspection, RuntimeExecutionInspection)
            assert inspection.runtime_status is RuntimeStatus.SUCCEEDED
            assert inspection.terminal is True
            assert inspection.provenance.requested_provider_id == "requested-provider"
            assert inspection.provenance.requested_model_id == "requested-model"
            assert inspection.provenance.actual_provider_id == "actual-provider"
            assert inspection.provenance.actual_model_id == "actual-model"
            assert inspection.provenance.identity_completeness is RuntimeIdentityCompleteness.FULL
            assert inspection.usage is not None
            assert inspection.usage.input_tokens == 10
            assert (
                inspection.runtime_diff_hint == "OpenCode reported 1 session file change hint(s)."
            )
            assert inspection.runtime_output_refs == ()
            assert AUTH_SENTINEL not in inspection.model_dump_json()
            assert inspection.summary == "OpenCode reported runtime status SUCCEEDED."
            assert inspection.execution_id == request.basis.execution_id
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_inspection_requires_known_process_local_binding_before_http() -> None:
    server = MockOpenCodeServer()
    runtime, client = setup_runtime(server)
    request = execution_request()
    unbound_handle = RuntimeExecutionHandle(
        execution_id=request.basis.execution_id,
        runtime_session=RuntimeSessionRef(runtime_id="opencode", session_id=SESSION_ID),
        request_digest=request.request_digest,
        opened_at=datetime.now(UTC),
    )

    async def exercise() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.inspect(unbound_handle)
            assert exc_info.value.failure.category.value == "SESSION_BINDING_REQUIRED"
            assert server.requests == []
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


@pytest.mark.parametrize("mismatch", ["session", "digest"])
def test_inspection_binding_mismatch_fails_before_session_get(mismatch: str) -> None:
    server = MockOpenCodeServer()
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            _, _, handle = await create_open_execution(runtime)
            if mismatch == "session":
                mismatched = handle.model_copy(
                    update={
                        "runtime_session": RuntimeSessionRef(
                            runtime_id="opencode", session_id="ses_other"
                        )
                    }
                )
            else:
                mismatched = handle.model_copy(update={"request_digest": "sha256:" + "9" * 64})

            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.inspect(mismatched)
            assert exc_info.value.failure.category.value == "REQUEST_CONFLICT"
            assert not any(
                item.method == "GET" and item.url.path.startswith("/api/session/")
                for item in server.requests
            )
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_cancel_is_idempotent_and_terminal_cancel_is_safe() -> None:
    server = MockOpenCodeServer()
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            request, _, handle = await create_open_execution(runtime)
            cancel_request = RuntimeCancelRequest(
                execution_id=request.basis.execution_id,
                runtime_session=handle.runtime_session,
                reason="operator requested cancellation",
            )
            first = await runtime.cancel(cancel_request)
            second = await runtime.cancel(cancel_request)
            assert first.state is RuntimeControlAckState.REQUESTED
            assert first.observed_runtime_status is RuntimeStatus.UNKNOWN
            assert second == first
            assert sum(item.url.path.endswith("/interrupt") for item in server.requests) == 1
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_cancel_requires_known_process_local_binding_before_interrupt() -> None:
    server = MockOpenCodeServer()
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.cancel(
                    RuntimeCancelRequest(
                        execution_id=EXECUTION_ID,
                        runtime_session=RuntimeSessionRef(
                            runtime_id="opencode", session_id=SESSION_ID
                        ),
                        reason="unknown execution",
                    )
                )
            assert exc_info.value.failure.category.value == "SESSION_BINDING_REQUIRED"
            assert server.requests == []
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_cancel_rejects_different_session_for_known_execution_without_interrupt() -> None:
    server = MockOpenCodeServer()
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            request = execution_request()
            await runtime.create_session(request)
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.cancel(
                    RuntimeCancelRequest(
                        execution_id=request.basis.execution_id,
                        runtime_session=RuntimeSessionRef(
                            runtime_id="opencode", session_id="ses_other"
                        ),
                        reason="wrong session",
                    )
                )
            assert exc_info.value.failure.category.value == "REQUEST_CONFLICT"
            assert not any(item.url.path.endswith("/interrupt") for item in server.requests)
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_cancel_requires_binding_in_this_process_even_when_session_ref_is_known_elsewhere() -> None:
    source_server = MockOpenCodeServer()
    source_runtime, source_client = setup_runtime(source_server)
    target_server = MockOpenCodeServer()
    target_runtime, target_client = setup_runtime(target_server)

    async def exercise() -> None:
        try:
            binding = await source_runtime.create_session(execution_request())
            with pytest.raises(AgentRuntimeError) as exc_info:
                await target_runtime.cancel(
                    RuntimeCancelRequest(
                        execution_id=EXECUTION_ID,
                        runtime_session=binding.runtime_session,
                        reason="binding belongs to another process",
                    )
                )
            assert exc_info.value.failure.category.value == "SESSION_BINDING_REQUIRED"
            assert target_server.requests == []
        finally:
            await source_runtime.aclose()
            await source_client.aclose()
            await target_runtime.aclose()
            await target_client.aclose()

    asyncio.run(exercise())


def test_cancel_of_already_terminal_execution_does_not_interrupt_again() -> None:
    completed_event = {
        "type": "session.completed",
        "properties": {"info": {"id": SESSION_ID}},
    }
    server = MockOpenCodeServer(prompt_events=(completed_event,))
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            request, _, handle = await create_open_execution(runtime)
            active = runtime._active[EXECUTION_ID]
            await wait_until(lambda: active.terminal)
            ack = await runtime.cancel(
                RuntimeCancelRequest(
                    execution_id=request.basis.execution_id,
                    runtime_session=handle.runtime_session,
                    reason="cancel after completion",
                )
            )
            assert ack.state is RuntimeControlAckState.ALREADY_TERMINAL
            assert not any(item.url.path.endswith("/interrupt") for item in server.requests)
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_permission_ask_and_deny_are_never_approved() -> None:
    ask_event = {
        "type": "permission.asked",
        "properties": {"sessionID": SESSION_ID, "directory": ROOT},
    }
    denied_event = {
        "type": "permission.denied",
        "properties": {
            "sessionID": SESSION_ID,
            "directory": ROOT,
            "permission": {"effect": "deny", "permission": "external_directory"},
        },
    }
    server = MockOpenCodeServer(prompt_events=(ask_event, denied_event))
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            _, _, handle = await create_open_execution(runtime)
            active = runtime._active[EXECUTION_ID]
            await wait_until(lambda: active.sequence == 4)
            iterator = runtime.events(handle)
            observed = [
                await asyncio.wait_for(anext(iterator), timeout=1),
                await asyncio.wait_for(anext(iterator), timeout=1),
                await asyncio.wait_for(anext(iterator), timeout=1),
                await asyncio.wait_for(anext(iterator), timeout=1),
            ]
            await iterator.aclose()
            assert [event.event_type for event in observed[-2:]] == [
                RuntimeEventType.PERMISSION_REQUIRED,
                RuntimeEventType.EXECUTION_BLOCKED,
            ]
            assert active.runtime_status is RuntimeStatus.BLOCKED
            assert not any("permission" in item.url.path for item in server.requests)
            assert not any("reply" in item.url.path for item in server.requests)
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_runtime_permission_denial_is_normalized_without_reply_channel() -> None:
    server = MockOpenCodeServer(prompt_status=403)
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            request = execution_request()
            binding = await runtime.create_session(request)
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.open_execution(request, binding)
            assert exc_info.value.failure.category.value == "PERMISSION_DENIED"
            assert any(item.url.path.endswith("/prompt") for item in server.requests)
            assert not any("permission" in item.url.path for item in server.requests)
            assert not any("reply" in item.url.path for item in server.requests)
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_missing_actual_model_identity_remains_unknown() -> None:
    server = MockOpenCodeServer(inspection={"data": {"status": "completed"}})
    runtime, client = setup_runtime(server)

    async def exercise() -> None:
        try:
            _, _, handle = await create_open_execution(runtime)
            inspection = await runtime.inspect(handle)
            assert inspection.provenance.actual_provider_id is None
            assert inspection.provenance.actual_model_id is None
            assert (
                inspection.provenance.identity_completeness is RuntimeIdentityCompleteness.UNKNOWN
            )
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())


def test_authentication_and_malformed_response_failures_do_not_leak_sentinel() -> None:
    server = MockOpenCodeServer(health_status=401)
    runtime, client = setup_runtime(server, auth_header=True)

    async def check_authentication() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.create_session(execution_request())
            assert exc_info.value.failure.category.value == "AUTHENTICATION"
            assert AUTH_SENTINEL not in str(exc_info.value)
            assert AUTH_SENTINEL not in exc_info.value.failure.model_dump_json()
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(check_authentication())

    malformed = MockOpenCodeServer(malformed_session_response=True)
    malformed_runtime, malformed_client = setup_runtime(malformed)

    async def check_malformed() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await malformed_runtime.create_session(execution_request())
            assert exc_info.value.failure.category.value == "TRANSPORT"
            assert AUTH_SENTINEL not in str(exc_info.value)
        finally:
            await malformed_runtime.aclose()
            await malformed_client.aclose()

    asyncio.run(check_malformed())


def test_transport_failure_does_not_retry_session_creation() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/api/health":
            return httpx.Response(200, json={"healthy": True, "version": "1.2.3", "pid": 1})
        raise httpx.ConnectError(AUTH_SENTINEL, request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    runtime = OpenCodeRuntime(
        "http://opencode.mock:4096",
        expected_runtime_version="1.2.3",
        permission_profile=permission_profile(),
        client=client,
    )

    async def exercise() -> None:
        try:
            request = execution_request()
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.create_session(request)
            assert exc_info.value.failure.category.value == "TRANSPORT"
            assert AUTH_SENTINEL not in str(exc_info.value)
            with pytest.raises(AgentRuntimeError) as retry_info:
                await runtime.create_session(request)
            assert retry_info.value.failure.category.value == "SESSION_BINDING_REQUIRED"
            assert [item.url.path for item in requests] == ["/api/health", "/api/session"]
        finally:
            await runtime.aclose()
            await client.aclose()

    asyncio.run(exercise())
