"""Exact-version tests for the OpenCode 1.18.23 configuration observer."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import replace
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
        expected_agent_mode="primary",
        expected_agent_hidden=False,
        allow=("edit", "read"),
        deny=("bash", "task"),
        allowed_tools=("read", "write"),
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
        "hidden": False,
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
        "tools": {
            "read": True,
            "write": True,
            "edit": False,
            "bash": False,
            "task": False,
        },
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


def _sources(
    config_file: Path, catalog: Path, home: Path, workspace: Path
) -> tuple[OpenCodeConfigurationSourceObservation, ...]:
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
            files = tuple(
                OpenCodeObservedFile(path=str(path), content_digest=_sha256(path.read_bytes()))
                for path in sorted(config_file.parent.rglob("*"))
                if path.is_file()
            )
            directories = tuple(
                str(path) for path in sorted(config_file.parent.rglob("*")) if path.is_dir()
            )
            result.append(
                OpenCodeConfigurationSourceObservation(
                    precedence_index=index,
                    layer=layer,
                    state="PRESENT",
                    identity=str(config_file.parent),
                    observation_method="relay-launch-directory-census",
                    files=files,
                    directory_members=directories,
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
        elif layer in {
            "remote-well-known",
            "console-organization",
            "system-managed-config",
            "macos-managed-preferences",
            "opencode-permission",
            "opencode-config-content",
            "legacy-tools-translation",
            "plugin-origins",
        }:
            result.append(
                OpenCodeConfigurationSourceObservation(
                    precedence_index=index,
                    layer=layer,
                    state="UNOBSERVABLE",
                    identity=f"{layer}:requires-independent-server-startup-evidence",
                    observation_method="not-established-by-caller-context",
                )
            )
        else:
            known_absent = {
                "global-config-json": (home / ".config/opencode/config.json",),
                "global-opencode-json": (home / ".config/opencode/opencode.json",),
                "global-legacy-config": (home / ".config/opencode/config.jsonc",),
                "opencode-config": (home / ".config/opencode.json",),
                "project-config-files": (
                    workspace / "opencode.json",
                    workspace / "opencode.jsonc",
                    workspace / ".opencode" / "opencode.json",
                    workspace / ".opencode" / "opencode.jsonc",
                ),
            }
            probe_paths = tuple(sorted(str(path) for path in known_absent.get(layer, ())))
            result.append(
                OpenCodeConfigurationSourceObservation(
                    precedence_index=index,
                    layer=layer,
                    state="ABSENT",
                    identity=f"{layer}:absent",
                    observation_method="relay-launch-source-census",
                    probe_paths=probe_paths,
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


def _fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    executable: Path | None = None,
):
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
        source_observations=_sources(config_file, catalog, home, workspace),
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
    if executable is None:
        executable = tmp_path / "opencode-test"
        executable.write_bytes(b"test-only OpenCode executable identity\n")
        executable.chmod(0o755)
    client = httpx.Client(transport=httpx.MockTransport(handle))
    observer = OpenCodeV11823ConfigurationObserver(
        "http://127.0.0.1:4096",
        permission_profile=profile,
        qualification_ref=qualification,
        startup_context=startup,
        executable=str(executable),
        client=client,
        clock=lambda: datetime(2026, 10, 29, tzinfo=UTC),
    )
    return request, descriptor, observer, paths, catalog, config_file


def test_unqualified_server_startup_context_remains_indeterminate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, _config_file = _fixture(tmp_path, monkeypatch)
    try:
        binding = observer.read(request, descriptor)
    finally:
        observer.close()

    assert binding.status is RequirementStatus.INDETERMINATE
    assert binding.precedence_complete is False
    assert binding.agent_id == AGENT_ID
    assert binding.normalized_allow_rules == ("edit", "read")
    assert binding.normalized_deny_rules == ("bash", "task")
    assert binding.normalized_ask_rules == ()
    assert binding.effective_tool_exposure == ("read", "write")
    assert binding.plugin_exposure == ()
    assert binding.mcp_exposure == ()
    assert binding.subagent_exposure == ()
    assert ("GET", "/config/providers") not in paths
    assert not any(method == "POST" for method, _path in paths)
    serialized = json.dumps(binding.model_dump(mode="json"))
    assert "never-retain-me" not in serialized
    assert "dummy-test-key-never-persisted" not in serialized


def test_request_route_mismatch_fails_before_server_observation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, _config_file = _fixture(tmp_path, monkeypatch)
    basis = request.basis.model_copy(
        update={
            "runtime_selection": RuntimeSelection(
                runtime_id="opencode",
                requested_provider_id="other-provider",
                requested_model_id=ALIAS,
            )
        }
    )
    mismatched = RuntimeExecutionRequest(
        basis=basis,
        request_digest=digest_execution_basis(basis),
    )
    try:
        with pytest.raises(OpenCodeObserverError, match="requested provider/model"):
            observer.read(mismatched, descriptor)
    finally:
        observer.close()
    assert paths == []


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("mode", "subagent", "mode"),
        ("hidden", True, "hidden state"),
    ),
)
def test_selected_agent_mode_and_hidden_are_exactly_bound(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
    message: str,
) -> None:
    _request_value, _descriptor, observer, _paths, _catalog, _config_file = _fixture(
        tmp_path, monkeypatch
    )
    agent = {
        "name": AGENT_ID,
        "mode": "primary",
        "hidden": False,
        "permission": _rules(),
        "model": {"providerID": "openrouter", "modelID": ALIAS},
    }
    agent[field] = value
    try:
        with pytest.raises(OpenCodeObserverError, match=message):
            observer._agent_identity(cast_agent(agent))
    finally:
        observer.close()


def cast_agent(value: dict[str, object]):
    from relay_engine.agent_runtime.opencode_configuration_observer import _project_agent

    return _project_agent(value)


def test_allowed_tools_are_distinct_from_permission_rule_identities(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _request_value, _descriptor, observer, _paths, _catalog, _config_file = _fixture(
        tmp_path, monkeypatch
    )
    try:
        assert observer._normalize_permissions(cast_agent(_selected_agent())) == (
            ("edit", "read"),
            ("bash", "task"),
            (),
        )
        assert observer._enabled_tools(_debug_agent()) == ("read", "write")
        observer._profile = replace(observer._profile, allowed_tools=())
        fallback = _debug_agent()
        fallback["tools"] = {"edit": True, "read": True, "bash": False, "task": False}
        assert observer._enabled_tools(fallback) == ("edit", "read")
    finally:
        observer.close()


def test_claimed_absence_is_reprobed_before_server_observation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, _config_file = _fixture(tmp_path, monkeypatch)
    absent_path = Path(observer._startup.source_observations[1].probe_paths[0])
    absent_path.parent.mkdir(parents=True)
    absent_path.write_text("{}\n")
    try:
        with pytest.raises(OpenCodeObserverError, match="previously absent is now present"):
            observer.read(request, descriptor)
    finally:
        observer.close()
    assert paths == []


def test_same_size_restored_mtime_diagnostic_mutation_is_detected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, _paths, _catalog, _config_file = _fixture(tmp_path, monkeypatch)
    diagnostic_file = Path(request.basis.workspace.root) / ".opencode" / "agent.json"
    diagnostic_file.parent.mkdir()
    diagnostic_file.write_bytes(b"{}\n")
    previous_stat = diagnostic_file.stat()

    def mutate_diagnostic(
        args: tuple[str, ...],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if args[-1] == "--version":
            return subprocess.CompletedProcess(args, 0, OPENCODE_V11823 + "\n", "")
        if args[-2:] == ("models", "openrouter"):
            return subprocess.CompletedProcess(
                args, 0, "openrouter/~deepseek/deepseek-flash-latest\n", ""
            )
        if args[-3:-1] == ("debug", "agent"):
            diagnostic_file.write_bytes(b"[]\n")
            os.utime(
                diagnostic_file,
                ns=(previous_stat.st_atime_ns, previous_stat.st_mtime_ns),
            )
            return subprocess.CompletedProcess(args, 0, json.dumps(_debug_agent()), "")
        raise AssertionError(f"unexpected command: {args!r}")

    monkeypatch.setattr(
        "relay_engine.agent_runtime.opencode_configuration_observer.subprocess.run",
        mutate_diagnostic,
    )
    try:
        with pytest.raises(OpenCodeObserverError, match="directory|content changed"):
            observer.read(request, descriptor)
    finally:
        observer.close()


def test_cli_executable_replacement_during_catalog_diagnostic_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "opencode-test"
    executable.write_bytes(b"#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    monkeypatch.setattr(
        "relay_engine.agent_runtime.opencode_configuration_observer.shutil.which",
        lambda _name: str(executable),
    )
    request, descriptor, observer, _paths, _catalog, _config_file = _fixture(
        tmp_path / "fixture", monkeypatch, executable=executable
    )
    calls: list[tuple[str, ...]] = []

    def replace_after_models(
        args: tuple[str, ...],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args[-1] == "--version":
            return subprocess.CompletedProcess(args, 0, OPENCODE_V11823 + "\n", "")
        if args[-2:] == ("models", "openrouter"):
            executable.write_bytes(b"#!/bin/sh\nexit 1\n")
            return subprocess.CompletedProcess(
                args, 0, "openrouter/~deepseek/deepseek-flash-latest\n", ""
            )
        raise AssertionError("debug-agent must not run after executable replacement")

    monkeypatch.setattr(
        "relay_engine.agent_runtime.opencode_configuration_observer.subprocess.run",
        replace_after_models,
    )
    try:
        with pytest.raises(OpenCodeObserverError, match="executable changed"):
            observer.read(request, descriptor)
    finally:
        observer.close()
    assert [call[-1] for call in calls] == ["--version", "openrouter"]


def test_redirect_following_injected_client_cannot_escape_exact_origin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, _paths, _catalog, _config_file = _fixture(tmp_path, monkeypatch)
    observer._client.close()

    request_hosts: list[str] = []

    def redirect(req: httpx.Request) -> httpx.Response:
        request_hosts.append(req.url.host)
        if req.url.host == "127.0.0.1":
            return httpx.Response(302, headers={"location": "https://outside.example/path"})
        return httpx.Response(
            200,
            json={"home": observer._startup.home},
        )

    class RedirectFollowingClient(httpx.Client):
        def get(self, url: object, **kwargs: object) -> httpx.Response:
            # Simulate a caller client that ignores the observer's per-request
            # redirect prohibition while still using an isolated mock transport.
            kwargs["follow_redirects"] = True
            return super().get(url, **kwargs)  # type: ignore[arg-type]

    observer._client = RedirectFollowingClient(
        transport=httpx.MockTransport(redirect),
        follow_redirects=True,
    )
    try:
        with pytest.raises(OpenCodeObserverError, match="redirected|origin changed"):
            observer.read(request, descriptor)
    finally:
        observer.close()
    assert request_hosts == ["127.0.0.1", "outside.example"]


def test_missing_alias_fails_closed_without_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, _config_file = _fixture(tmp_path, monkeypatch)

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


def test_catalog_mutation_during_diagnostic_is_indeterminate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, catalog, _config_file = _fixture(tmp_path, monkeypatch)

    def mutate_catalog(
        args: tuple[str, ...],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if args[-1] == "--version":
            return subprocess.CompletedProcess(args, 0, OPENCODE_V11823 + "\n", "")
        if args[-2:] == ("models", "openrouter"):
            catalog.write_text('{"mutated":true}\n')
            return subprocess.CompletedProcess(
                args, 0, "openrouter/~deepseek/deepseek-flash-latest\n", ""
            )
        if len(args) >= 4 and args[-3:-1] == ("debug", "agent"):
            return subprocess.CompletedProcess(args, 0, json.dumps(_debug_agent()), "")
        raise AssertionError

    monkeypatch.setattr(
        "relay_engine.agent_runtime.opencode_configuration_observer.subprocess.run",
        mutate_catalog,
    )
    try:
        with pytest.raises(OpenCodeObserverError, match="catalog"):
            observer.read(request, descriptor)
    finally:
        observer.close()
    assert not any(method == "POST" for method, _path in paths)


def test_diagnostic_config_tree_mutation_is_indeterminate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, config_file = _fixture(tmp_path, monkeypatch)

    def mutate_config(
        args: tuple[str, ...],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        if args[-1] == "--version":
            return subprocess.CompletedProcess(args, 0, OPENCODE_V11823 + "\n", "")
        if args[-2:] == ("models", "openrouter"):
            return subprocess.CompletedProcess(
                args, 0, "openrouter/~deepseek/deepseek-flash-latest\n", ""
            )
        if len(args) >= 4 and args[-3:-1] == ("debug", "agent"):
            config_file.write_text(config_file.read_text() + "\n")
            return subprocess.CompletedProcess(args, 0, json.dumps(_debug_agent()), "")
        raise AssertionError

    monkeypatch.setattr(
        "relay_engine.agent_runtime.opencode_configuration_observer.subprocess.run",
        mutate_config,
    )
    try:
        with pytest.raises(OpenCodeObserverError, match="configuration directory|source changed"):
            observer.read(request, descriptor)
    finally:
        observer.close()
    assert not any(method == "POST" for method, _path in paths)


def test_observer_environment_mismatch_fails_before_cli_or_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, _config_file = _fixture(tmp_path, monkeypatch)
    monkeypatch.setenv("OPENCODE_DISABLE_MODELS_FETCH", "0")
    try:
        with pytest.raises(OpenCodeObserverError, match="environment mismatch|fetch-disable"):
            observer.read(request, descriptor)
    finally:
        observer.close()
    assert paths == []
    assert not any(method == "POST" for method, _path in paths)


def test_runtime_state_mutation_between_a_and_b_is_indeterminate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, descriptor, observer, paths, _catalog, _config_file = _fixture(tmp_path, monkeypatch)
    original_client = observer._client
    calls = 0

    def handle(req: httpx.Request) -> httpx.Response:
        nonlocal calls
        if req.url.path == "/path":
            startup = observer._startup
            return httpx.Response(
                200,
                json={
                    "home": startup.home,
                    "state": startup.state_root,
                    "config": startup.config_root,
                    "worktree": startup.worktree_root,
                    "directory": startup.workspace_root,
                },
            )
        if req.url.path == "/config":
            return httpx.Response(200, json={"plugin": [], "mcp": {}})
        if req.url.path == "/mcp":
            return httpx.Response(200, json={})
        if req.url.path == "/agent":
            calls += 1
            data = _agents()
            if calls > 1:
                data[0]["model"] = {"providerID": "openrouter", "modelID": "changed"}
            return httpx.Response(200, json=data)
        return httpx.Response(404)

    original_client.close()
    observer._client = httpx.Client(transport=httpx.MockTransport(handle))
    try:
        with pytest.raises(OpenCodeObserverError, match="changed during observation|alias"):
            observer.read(request, descriptor)
    finally:
        observer.close()
    assert not any(method == "POST" for method, _path in paths)


def test_wrong_qualification_observer_is_rejected_before_observation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _request_value, _descriptor, observer, _paths, _catalog, _config_file = _fixture(
        tmp_path, monkeypatch
    )
    startup = observer._startup
    profile = observer._profile
    observer_ref = observer.observer_ref
    observer.close()
    wrong = observer_ref.model_copy(update={"content_digest": "sha256:" + "f" * 64})
    qualification = OpenCodeConfigurationQualificationRef.create(
        qualification_id="wrong-observer",
        runtime_version=OPENCODE_V11823,
        runtime_api_generation=OPENCODE_API_GENERATION,
        adapter_version=OPENCODE_ADAPTER_VERSION,
        observer_ref=wrong,
    )
    client = httpx.Client(transport=httpx.MockTransport(lambda _r: httpx.Response(500)))
    try:
        with pytest.raises(ValueError, match="exact observer"):
            OpenCodeV11823ConfigurationObserver(
                "http://127.0.0.1:4096",
                permission_profile=profile,
                qualification_ref=qualification,
                startup_context=startup,
                executable=str(observer._executable),
                client=client,
            )
    finally:
        client.close()


def test_startup_context_requires_complete_ordered_source_census(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _request_value, _descriptor, observer, _paths, _catalog, _config_file = _fixture(
        tmp_path, monkeypatch
    )
    payload = observer._startup.model_dump(mode="python")
    payload["source_observations"] = payload["source_observations"][:-1]
    observer.close()
    with pytest.raises(ValueError, match="exact layers"):
        OpenCodeServerStartupContext.model_validate(payload)
