"""Exact-version tests for the OpenCode 1.18.23 configuration observer."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from relay_engine.agent_runtime.models import (
    RuntimeDescriptor,
    RuntimeExecutionBasis,
    RuntimeExecutionRequest,
    RuntimePermissionProfileRef,
    RuntimeSelection,
    RuntimeWorkspaceAttachment,
    digest_execution_basis,
)
from relay_engine.agent_runtime.opencode import (
    OPENCODE_ADAPTER_VERSION,
    OPENCODE_API_GENERATION,
    OpenCodeConfigurationQualificationRef,
    OpenCodePermissionProfile,
)
from relay_engine.agent_runtime.opencode_configuration_observer import (
    OPENCODE_V11823,
    OpenCodeConfigurationSourceObservation,
    OpenCodeObservedFile,
    OpenCodeObserverError,
    OpenCodeServerStartupContext,
    OpenCodeV11823ConfigurationObserver,
    opencode_v11823_observer_ref,
)
from relay_engine.domain import CommitRef, RepositoryRef
from relay_engine.role_contracts import RequirementStatus

DIGEST = "sha256:" + "1" * 64
ALIAS = "~deepseek/deepseek-flash-latest"
AGENT_ID = "relay-dogfood"


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _request(root: Path) -> RuntimeExecutionRequest:
    repository = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789501",
        host="github.com",
        path="team/relay",
    )
    basis = RuntimeExecutionBasis(
        execution_id="exec_018f47c1-7b2c-7abc-8def-123456789502",
        slice_id="slc_018f47c1-7b2c-7abc-8def-123456789503",
        source_baseline_id="base_018f47c1-7b2c-7abc-8def-123456789504",
        workspace=RuntimeWorkspaceAttachment(
            workspace_id="workspace-observer",
            root=str(root),
            repository=repository,
            source_commit=CommitRef(
                repository=repository,
                sha="0e23a593eba96ba55bdb4edaf88867dd0e0fd199",
            ),
        ),
        input_payload={
            "text": "not admitted by observer tests",
            "payload_digest": DIGEST,
            "attachment_refs": (),
        },
        runtime_selection=RuntimeSelection(
            runtime_id="opencode",
            requested_provider_id="openrouter",
            requested_model_id=ALIAS,
        ),
        permission_profile_ref=RuntimePermissionProfileRef(
            profile_id="dogfood-observer-profile",
            content_digest=DIGEST,
        ),
    )
    return RuntimeExecutionRequest(basis=basis, request_digest=digest_execution_basis(basis))


def _profile(request: RuntimeExecutionRequest) -> OpenCodePermissionProfile:
    return OpenCodePermissionProfile(
        reference=request.basis.permission_profile_ref,
        agent_id=AGENT_ID,
        allow=("edit", "read"),
        deny=("bash", "task"),
        allowed_tools=("edit", "read"),
    )


def _rules() -> list[dict[str, str]]:
    return [
        {"permission": "edit", "pattern": "*", "action": "allow"},
        {"permission": "read", "pattern": "*", "action": "allow"},
        {"permission": "bash", "pattern": "*", "action": "deny"},
        {"permission": "task", "pattern": "*", "action": "deny"},
    ]


def _selected_agent() -> dict[str, object]:
    return {
        "name": AGENT_ID,
        "mode": "primary",
        "permission": _rules(),
        "model": {"providerID": "openrouter", "modelID": ALIAS},
        "options": {},
    }


def _agents() -> list[dict[str, object]]:
    return [
        _selected_agent(),
        {
            "name": "general",
            "mode": "subagent",
            "permission": [],
            "options": {},
        },
    ]


def _debug_agent() -> dict[str, object]:
    return {
        **_selected_agent(),
        "tools": {"read": True, "edit": True, "bash": False, "task": False},
    }


def _environment(
    *,
    home: Path,
    config: Path,
    cache: Path,
    data: Path,
    state: Path,
    catalog: Path,
) -> tuple[tuple[str, str | None], ...]:
    values: dict[str, str | None] = {
        "HOME": str(home),
        "XDG_CACHE_HOME": str(cache),
        "XDG_CONFIG_HOME": str(config.parent),
        "XDG_DATA_HOME": str(data.parent),
        "XDG_STATE_HOME": str(state.parent),
        "OPENCODE_TEST_HOME": None,
        "OPENCODE_CONFIG": None,
        "OPENCODE_CONFIG_DIR": None,
        "OPENCODE_CONFIG_CONTENT": None,
        "OPENCODE_PERMISSION": None,
        "OPENCODE_DISABLE_PROJECT_CONFIG": "1",
        "OPENCODE_DISABLE_MODELS_FETCH": "1",
        "OPENCODE_MODELS_PATH": str(catalog),
        "OPENCODE_MODELS_URL": None,
        "OPENCODE_PURE": "1",
    }
    return tuple(sorted(values.items()))


def _sources(config_file: Path, catalog: Path) -> tuple[OpenCodeConfigurationSourceObservation, ...]:
    layers = (
        "remote-well-known",
        "global-config-json",
        "global-opencode-json",
        "global-opencode-jsonc",
        "global-legacy-config",
        "opencode-config",
        "project-config-files",
        "config-directories",
        "opencode-config-content",
        "console-organization",
        "system-managed-config",
        "macos-managed-preferences",
        "opencode-permission",
        "legacy-tools-translation",
        "plugin-origins",
        "opencode-disable-models-fetch",
        "opencode-models-path",
    )
    result: list[OpenCodeConfigurationSourceObservation] = []
    for index, layer in enumerate(layers, start=1):
        if layer == "global-opencode-jsonc":
            result.append(
                OpenCodeConfigurationSourceObservation(
                    precedence_index=index,
                    layer=layer,
                    state="PRESENT",
                    identity=str(config_file),
                    observation_method="relay-launch-file-census",
                    files=(
                        OpenCodeObservedFile(
                            path=str(config_file),
                            content_digest=_sha256(config_file.read_bytes()),
                        ),
                    ),
                )
            )
        elif layer == "config-directories":
            result.append(
                OpenCodeConfigurationSourceObservation(
                    precedence_index=index,
                    layer=layer,
                    state="PRESENT",
                    identity=str(config_file.parent),
                    observation_method="relay-launch-directory-census",
                    sanitized_content_digest=_sha256(str(config_file.parent).encode()),
                )
            )
        elif layer == "opencode-disable-models-fetch":
            result.append(
                OpenCodeConfigurationSourceObservation(
                    precedence_index=index,
                    layer=layer,
                    state="PRESENT",
                    identity="OPENCODE_DISABLE_MODELS_FETCH",
                    observation_method="relay-launch-environment",

                    sanitized_content_digest=_sha256(b"1"),
                )
            )
        elif layer == "opencode-models-path":
            result.append(
                OpenCodeConfigurationSourceObservation(
                    precedence_index=index,
                    layer=layer,
                    state="PRESENT",
                    identity=str(catalog),
                    observation_method="relay-launch-environment+file-census",
                    files=(
                        OpenCodeObservedFile(
                            path=str(catalog),
                            content_digest=_sha256(catalog.read_bytes()),
                        ),
                    ),
                )
            )
        else:
            result.append(
                OpenCodeConfigurationSourceObservation(
                    precedence_index=index,
                    layer=layer,
                    state="ABSENT",
                    identity=f"{layer}:absent",
                    observation_method="relay-launch-source-census",
                )
            )
    return tuple(result)


def _install_environment(
    monkeypatch: pytest.MonkeyPatch,
    environment: tuple[tuple[str, str | None], ...],
) -> None:
    for key, value in environment:
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    workspace = tmp_path / "workspace"
    home = tmp_path / "home"
    config = tmp_path / "xdg-config" / "opencode"
    cache = tmp_path / "xdg-cache" / "opencode"
    data = tmp_path / "xdg-data" / "opencode"
    state = tmp_path / "xdg-state" / "opencode"
    for path_value in (workspace, home, config, cache, data, state):
        path_value.mkdir(parents=True)
    config_file = config / "opencode.jsonc"
    config_file.write_text('{"$schema":"https://opencode.ai/config.json"}\n')
    catalog = tmp_path / "models.json"
    catalog.write_text('{"openrouter":{"id":"openrouter","models":{}}}\n')

    environment = _environment(
        home=home,
        config=config,
        cache=cache,
        data=data,
        state=state,
        catalog=catalog,
    )
    _install_environment(monkeypatch, environment)
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy-test-key-never-persisted")

    request = _request(workspace)
    profile = _profile(request)
    startup = OpenCodeServerStartupContext(
        runtime_version=OPENCODE_V11823,
        runtime_api_generation=OPENCODE_API_GENERATION,
        adapter_version=OPENCODE_ADAPTER_VERSION,
        workspace_root=str(workspace),
        home=str(home),
        state_root=str(state),
        config_root=str(config),
        worktree_root=str(workspace),
        environment=environment,
        source_observations=_sources(config_file, catalog),
        catalog_path=str(catalog),
        catalog_digest=_sha256(catalog.read_bytes()),
        credential_environment_names=("OPENROUTER_API_KEY",),
        context_source="relay-launch-context-test-v1",
    )
    observer_ref = opencode_v11823_observer_ref()
    qualification = OpenCodeConfigurationQualificationRef.create(
        qualification_id="opencode-v11823-observer-test",
        runtime_version=OPENCODE_V11823,
        runtime_api_generation=OPENCODE_API_GENERATION,
        adapter_version=OPENCODE_ADAPTER_VERSION,
        observer_ref=observer_ref,
    )
    descriptor = RuntimeDescriptor(
        runtime_id="opencode",
        adapter_version=OPENCODE_ADAPTER_VERSION,
        runtime_version=OPENCODE_V11823,
        api_generation=OPENCODE_API_GENERATION,
        capabilities=(),
    )

    paths: list[tuple[str, str]] = []

    def handle(req: httpx.Request) -> httpx.Response:
        paths.append((req.method, req.url.path))
        if req.url.path == "/path":
            return httpx.Response(
                200,
                json={
                    "home": str(home),
                    "state": str(state),
                    "config": str(config),
                    "worktree": str(workspace),
                    "directory": str(workspace),
                },
            )
        if req.url.path == "/config":
            return httpx.Response(
                200,
                json={
                    "plugin": [],
                    "mcp": {},
                    "provider": {"openrouter": {"options": {"apiKey": "never-retain-me"}}},
                },
            )
        if req.url.path == "/agent":
            return httpx.Response(200, json=_agents())
        if req.url.path == "/mcp":
            return httpx.Response(200, json={})
        return httpx.Response(404)

    def fake_run(
        args: tuple[str, ...],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if args[-1] == "--version":
            return subprocess.CompletedProcess(args, 0, OPENCODE_V11823 + "\n", "")
        if args[-2:] == ("models", "openrouter"):
            return subprocess.CompletedProcess(
                args,
                0,
                "openrouter/~deepseek/deepseek-flash-latest\n",
                "",
            )
        if len(args) >= 4 and args[-3:-1] == ("debug", "agent"):
            return subprocess.CompletedProcess(args, 0, json.dumps(_debug_agent()), "")
        raise AssertionError(f"unexpected command: {args!r}")

    monkeypatch.setattr(
        "relay_engine.agent_runtime.opencode_configuration_observer.subprocess.run",
        fake_run,
    )
    client = httpx.Client(transport=httpx.MockTransport(handle))
    observer = OpenCodeV11823ConfigurationObserver(
        "http://127.0.0.1:4096",
        permission_profile=profile,
        qualification_ref=qualification,
        startup_context=startup,
        client=client,
        clock=lambda: datetime(2026, 10, 29, tzinfo=UTC),
    )
    return request, descriptor, observer, paths, catalog, config_file


def test_exact_observer_produces_satisfied_content_bound_binding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, _config_file = _fixture(
        tmp_path, monkeypatch
    )
    try:
        binding = observer.read(request, descriptor)
    finally:
        observer.close()

    assert binding.status is RequirementStatus.SATISFIED
    assert binding.precedence_complete is True
    assert binding.agent_id == AGENT_ID
    assert binding.normalized_allow_rules == ("edit", "read")
    assert binding.normalized_deny_rules == ("bash", "task")
    assert binding.normalized_ask_rules == ()
    assert binding.effective_tool_exposure == ("edit", "read")
    assert binding.plugin_exposure == ()
    assert binding.mcp_exposure == ()
    assert binding.subagent_exposure == ()
    assert ("GET", "/config/providers") not in paths
    assert not any(method == "POST" for method, _path in paths)
    serialized = json.dumps(binding.model_dump(mode="json"))
    assert "never-retain-me" not in serialized
    assert "dummy-test-key-never-persisted" not in serialized


def test_missing_alias_fails_closed_without_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, _config_file = _fixture(
        tmp_path, monkeypatch
    )

    def no_alias(
        args: tuple[str, ...],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if args[-1] == "--version":
            return subprocess.CompletedProcess(args, 0, OPENCODE_V11823 + "\n", "")
        if args[-2:] == ("models", "openrouter"):
            return subprocess.CompletedProcess(args, 0, "openrouter/other-model\n", "")
        raise AssertionError("debug agent must not run after catalog mismatch")

    monkeypatch.setattr(
        "relay_engine.agent_runtime.opencode_configuration_observer.subprocess.run",
        no_alias,
    )
    try:
        with pytest.raises(OpenCodeObserverError, match="selected alias"):
            observer.read(request, descriptor)
    finally:
        observer.close()
    assert not any(method == "POST" for method, _path in paths)
