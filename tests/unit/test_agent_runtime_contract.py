"""Contract tests for exact requests, sessions, and authority separation."""

import asyncio

import httpx
import pytest

from relay_engine.agent_runtime.errors import AgentRuntimeError
from relay_engine.agent_runtime.models import (
    CredentialRef,
    RuntimeCapability,
    RuntimeExecutionBasis,
    RuntimeExecutionRequest,
    RuntimePermissionProfileRef,
    RuntimeSelection,
    RuntimeSessionRef,
    RuntimeWorkspaceAttachment,
    digest_execution_basis,
)
from relay_engine.agent_runtime.opencode import OpenCodePermissionProfile, OpenCodeRuntime
from relay_engine.domain import CommitRef, RepositoryRef

EXECUTION_ID = "exec_018f47c1-7b2c-7abc-8def-123456789011"
SLICE_ID = "slc_018f47c1-7b2c-7abc-8def-123456789012"
BASELINE_ID = "base_018f47c1-7b2c-7abc-8def-123456789013"
REPOSITORY_ID = "repo_018f47c1-7b2c-7abc-8def-123456789014"
COMMIT_SHA = "e8598ae5ffb046d4131e04655a0c063ff1e41ccc"
DIGEST = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
ROOT = "/tmp/relay-runtime-contract"


def permission_ref() -> RuntimePermissionProfileRef:
    return RuntimePermissionProfileRef(profile_id="noninteractive", content_digest=DIGEST)


def execution_request(**updates: object) -> RuntimeExecutionRequest:
    repository = RepositoryRef(id=REPOSITORY_ID, host="github.com", path="team/project")
    basis = RuntimeExecutionBasis(
        execution_id=EXECUTION_ID,
        slice_id=SLICE_ID,
        source_baseline_id=BASELINE_ID,
        workspace=RuntimeWorkspaceAttachment(
            workspace_id="workspace-1",
            root=ROOT,
            repository=repository,
            source_commit=CommitRef(repository=repository, sha=COMMIT_SHA),
        ),
        input_payload={
            "text": "Do not send this until events are ready.",
            "payload_digest": DIGEST,
            "attachment_refs": (),
        },
        runtime_selection=RuntimeSelection(
            runtime_id="opencode",
            requested_provider_id="provider-test",
            requested_model_id="model-test",
        ),
        permission_profile_ref=permission_ref(),
        credential_refs=(CredentialRef(credential_id="provider-credential-ref"),),
        required_capabilities=(RuntimeCapability.EVENT_STREAM,),
    )
    values: dict[str, object] = {"basis": basis, "request_digest": digest_execution_basis(basis)}
    values.update(updates)
    return RuntimeExecutionRequest(**values)  # type: ignore[arg-type]


def permission_profile(*, ask: tuple[str, ...] = ()) -> OpenCodePermissionProfile:
    return OpenCodePermissionProfile(
        reference=permission_ref(),
        agent_id="relay-noninteractive",
        allow=("read", "edit"),
        deny=("external_directory", "git_push"),
        ask=ask,
    )


def runtime_for(
    handler,
    *,
    ask: tuple[str, ...] = (),
) -> tuple[OpenCodeRuntime, httpx.AsyncClient, list[httpx.Request]]:
    calls: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return handler(request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(recording_handler))
    runtime = OpenCodeRuntime(
        "http://opencode.test:4096",
        expected_runtime_version="1.2.3",
        permission_profile=permission_profile(ask=ask),
        client=client,
    )
    return runtime, client, calls


def health_response(request: httpx.Request) -> httpx.Response:
    assert request.url.path == "/api/health"
    return httpx.Response(200, json={"healthy": True, "version": "1.2.3", "pid": 4})


def test_agent_runtime_protocol_is_runtime_neutral_and_session_creation_has_no_prompt() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/health":
            return health_response(request)
        assert request.method == "POST"
        assert request.url.path == "/api/session"
        body = request.read()
        assert b"Do not send this until events are ready." not in body
        assert b"provider-credential-ref" not in body
        return httpx.Response(
            200,
            json={
                "data": {
                    "id": "ses_exact_binding",
                    "location": {"directory": ROOT},
                }
            },
        )

    runtime, client, calls = runtime_for(handler)

    async def exercise() -> None:
        try:
            assert all(
                hasattr(runtime, method)
                for method in (
                    "describe",
                    "create_session",
                    "open_execution",
                    "events",
                    "cancel",
                    "inspect",
                )
            )
            request = execution_request()
            binding = await runtime.create_session(request)
            assert binding.execution_id == request.basis.execution_id
            assert binding.request_digest == request.request_digest
            assert binding.workspace_id == request.basis.workspace.workspace_id
            assert binding.runtime_session.session_id == "ses_exact_binding"
            assert [call.url.path for call in calls] == ["/api/health", "/api/session"]
        finally:
            await client.aclose()

    asyncio.run(exercise())


def test_same_execution_and_digest_reuses_binding_but_changed_digest_conflicts() -> None:
    create_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal create_calls
        if request.url.path == "/api/health":
            return health_response(request)
        create_calls += 1
        return httpx.Response(
            200,
            json={"data": {"id": "ses_one", "location": {"directory": ROOT}}},
        )

    runtime, client, _ = runtime_for(handler)

    async def exercise() -> None:
        try:
            original = execution_request()
            first = await runtime.create_session(original)
            repeated = await runtime.create_session(original)
            assert first is repeated
            assert create_calls == 1

            changed_basis = original.basis.model_copy(
                update={
                    "runtime_selection": RuntimeSelection(
                        runtime_id="opencode",
                        requested_provider_id="different-provider",
                        requested_model_id="model-test",
                    )
                }
            )
            changed = RuntimeExecutionRequest(
                basis=changed_basis,
                request_digest=digest_execution_basis(changed_basis),
            )
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.create_session(changed)
            assert exc_info.value.failure.category.value == "REQUEST_CONFLICT"
            assert create_calls == 1
        finally:
            await client.aclose()

    asyncio.run(exercise())


@pytest.mark.parametrize("mismatch", ["execution", "digest", "workspace", "runtime", "session"])
def test_binding_mismatch_fails_before_event_observer_or_prompt(mismatch: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/health":
            return health_response(request)
        if request.url.path == "/api/session":
            return httpx.Response(
                200,
                json={"data": {"id": "ses_bound", "location": {"directory": ROOT}}},
            )
        pytest.fail(f"unexpected HTTP request before binding validation: {request.url.path}")

    runtime, client, calls = runtime_for(handler)

    async def exercise() -> None:
        try:
            request = execution_request()
            binding = await runtime.create_session(request)
            updates: dict[str, object] = {}
            if mismatch == "execution":
                updates["execution_id"] = "exec_018f47c1-7b2c-7abc-8def-123456789099"
            elif mismatch == "digest":
                updates["request_digest"] = "sha256:" + "9" * 64
            elif mismatch == "workspace":
                updates["workspace_id"] = "workspace-other"
            elif mismatch == "runtime":
                updates["runtime_session"] = RuntimeSessionRef(
                    runtime_id="other-runtime", session_id=binding.runtime_session.session_id
                )
            else:
                updates["runtime_session"] = RuntimeSessionRef(
                    runtime_id="opencode", session_id="ses_unbound"
                )
            mismatched = binding.model_copy(update=updates)

            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.open_execution(request, mismatched)
            assert exc_info.value.failure.category.value == "REQUEST_CONFLICT"
            assert [call.url.path for call in calls] == ["/api/health", "/api/session"]
        finally:
            await client.aclose()

    asyncio.run(exercise())


def test_missing_process_local_binding_fails_without_session_discovery() -> None:
    runtime, client, calls = runtime_for(lambda _request: pytest.fail("no HTTP allowed"))

    async def exercise() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.open_execution(execution_request(), None)
            assert exc_info.value.failure.category.value == "SESSION_BINDING_REQUIRED"
            assert calls == []
        finally:
            await client.aclose()

    asyncio.run(exercise())


def test_missing_required_capability_fails_before_session_creation() -> None:
    runtime, client, calls = runtime_for(health_response)
    basis = execution_request().basis.model_copy(
        update={"required_capabilities": (RuntimeCapability.RESUME,)}
    )
    request = RuntimeExecutionRequest(basis=basis, request_digest=digest_execution_basis(basis))

    async def exercise() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.create_session(request)
            assert exc_info.value.failure.category.value == "UNSUPPORTED_CAPABILITY"
            assert [call.url.path for call in calls] == ["/api/health"]
        finally:
            await client.aclose()

    asyncio.run(exercise())


def test_ask_permission_profile_is_blocked_before_session_creation() -> None:
    runtime, client, calls = runtime_for(health_response, ask=("bash",))

    async def exercise() -> None:
        try:
            with pytest.raises(AgentRuntimeError) as exc_info:
                await runtime.create_session(execution_request())
            assert exc_info.value.failure.category.value == "AGENT_BLOCKED"
            assert calls == []
        finally:
            await client.aclose()

    asyncio.run(exercise())


def test_open_code_permission_profile_keeps_allow_and_deny_explicit() -> None:
    profile = permission_profile()
    assert profile.allow == ("read", "edit")
    assert profile.deny == ("external_directory", "git_push")
    assert profile.ask == ()
    with pytest.raises(ValueError, match="must not overlap"):
        OpenCodePermissionProfile(
            reference=permission_ref(),
            agent_id="relay-agent",
            allow=("read",),
            deny=("read",),
        )
