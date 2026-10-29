"""Exact-version OpenCode 1.18.23 configuration observation for trusted-local execution."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, TypedDict, cast
from urllib.parse import urlsplit

import httpx
from pydantic import field_validator, model_validator

from relay_engine.agent_runtime.models import RuntimeDescriptor, RuntimeExecutionRequest
from relay_engine.agent_runtime.opencode import (
    OPENCODE_ADAPTER_VERSION,
    OPENCODE_API_GENERATION,
    OPENCODE_RUNTIME_ID,
    OpenCodeConfigurationBinding,
    OpenCodeConfigurationBindingReader,
    OpenCodeConfigurationObserverRef,
    OpenCodeConfigurationQualificationRef,
    OpenCodePermissionProfile,
)
from relay_engine.domain import ContentDigest
from relay_engine.domain._base import DomainModel
from relay_engine.role_contracts import RequirementStatus

OPENCODE_V11823 = "1.18.23"
OPENCODE_V11823_OBSERVER_ID = "opencode-v1.18.23-config-observer-v1"


def opencode_v11823_observer_ref() -> OpenCodeConfigurationObserverRef:
    """Return the content-bound identity of this exact observer implementation."""

    module_bytes = Path(__file__).read_bytes()
    return OpenCodeConfigurationObserverRef(
        observer_id=OPENCODE_V11823_OBSERVER_ID,
        content_digest="sha256:" + hashlib.sha256(module_bytes).hexdigest(),
    )


_SOURCE_LAYER_ORDER = (
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
_RELEVANT_ENV_KEYS = (
    "HOME",
    "XDG_CACHE_HOME",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "XDG_STATE_HOME",
    "OPENCODE_TEST_HOME",
    "OPENCODE_CONFIG",
    "OPENCODE_CONFIG_DIR",
    "OPENCODE_CONFIG_CONTENT",
    "OPENCODE_PERMISSION",
    "OPENCODE_DISABLE_PROJECT_CONFIG",
    "OPENCODE_DISABLE_MODELS_FETCH",
    "OPENCODE_MODELS_PATH",
    "OPENCODE_MODELS_URL",
    "OPENCODE_PURE",
)
_SECRET_ENV_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "AUTH")
_SECRET_FIELD_NAMES = {
    "apikey",
    "api_key",
    "authorization",
    "cookie",
    "credentials",
    "credential",
    "key",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "token",
    "access_token",
    "headers",
}


class OpenCodeObserverError(RuntimeError):
    """Fail-closed observer error; callers must treat it as INDETERMINATE."""


type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
type PermissionAction = Literal["allow", "deny", "ask"]


class _PermissionRule(TypedDict):
    permission: str
    pattern: str
    action: PermissionAction


class _ModelRef(TypedDict):
    providerID: str
    modelID: str


class _ProjectedAgent(TypedDict):
    name: str
    mode: str
    hidden: bool | None
    permission: tuple[_PermissionRule, ...]
    model: _ModelRef | None


class _DebugAgent(_ProjectedAgent):
    tools: dict[str, bool]


class _ProjectedConfig(TypedDict):
    plugins: tuple[str, ...]
    mcp_names: tuple[str, ...]
    agent_names: tuple[str, ...]
    legacy_tools_present: bool
    permission_present: bool


class _ServerSnapshot(TypedDict):
    path: dict[str, str]
    config: _ProjectedConfig
    agents: list[_ProjectedAgent]
    mcp: dict[str, str]
    digest: ContentDigest


class OpenCodeObservedFile(DomainModel):
    """One exact non-secret file identity committed by the startup source census."""

    path: str
    content_digest: ContentDigest

    @field_validator("path")
    @classmethod
    def absolute_file_path(cls, value: str) -> str:
        if not value.strip() or not Path(value).is_absolute():
            raise ValueError("observed file path must be absolute")
        return value


class OpenCodeConfigurationSourceObservation(DomainModel):
    """One source-layer observation in exact OpenCode 1.18.23 precedence order."""

    precedence_index: int
    layer: str
    state: Literal["PRESENT", "ABSENT"]
    identity: str
    observation_method: str
    files: tuple[OpenCodeObservedFile, ...] = ()
    sanitized_content_digest: ContentDigest | None = None

    @model_validator(mode="after")
    def valid_source_observation(self) -> OpenCodeConfigurationSourceObservation:
        if self.precedence_index < 1:
            raise ValueError("source precedence index must be positive")
        if (
            not self.layer.strip()
            or not self.identity.strip()
            or not self.observation_method.strip()
        ):
            raise ValueError("source observation identity must be explicit")
        if self.state == "ABSENT" and self.files:
            raise ValueError("absent source observation cannot bind files")
        if self.state == "PRESENT" and not self.files and self.sanitized_content_digest is None:
            raise ValueError("present source observation needs files or sanitized content digest")
        paths = tuple(item.path for item in self.files)
        if paths != tuple(sorted(set(paths))):
            raise ValueError("source observation files must be unique and canonically ordered")
        return self

    def canonical_ref(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )


class OpenCodeServerStartupContext(DomainModel):
    """Immutable non-secret startup context for the exact OpenCode server being observed."""

    runtime_version: str
    runtime_api_generation: str
    adapter_version: str
    workspace_root: str
    home: str
    state_root: str
    config_root: str
    worktree_root: str
    environment: tuple[tuple[str, str | None], ...]
    source_observations: tuple[OpenCodeConfigurationSourceObservation, ...]
    catalog_path: str
    catalog_digest: ContentDigest
    credential_environment_names: tuple[str, ...] = ()
    context_source: str

    @model_validator(mode="after")
    def exact_context(self) -> OpenCodeServerStartupContext:
        if (
            self.runtime_version != OPENCODE_V11823
            or self.runtime_api_generation != OPENCODE_API_GENERATION
            or self.adapter_version != OPENCODE_ADAPTER_VERSION
        ):
            raise ValueError("startup context must bind exact OpenCode 1.18.23 adapter identity")
        for value in (
            self.workspace_root,
            self.home,
            self.state_root,
            self.config_root,
            self.worktree_root,
            self.catalog_path,
        ):
            if not value.strip() or not Path(value).is_absolute():
                raise ValueError("startup context paths must be absolute")
        if not self.context_source.strip():
            raise ValueError("startup context source must be explicit")
        if self.credential_environment_names != tuple(
            sorted(set(self.credential_environment_names))
        ):
            raise ValueError("credential environment names must be unique and sorted")
        if any(
            not name.strip() or any(ord(char) < 32 for char in name)
            for name in self.credential_environment_names
        ):
            raise ValueError("credential environment names must be explicit")

        env_keys = tuple(key for key, _value in self.environment)
        if env_keys != tuple(sorted(_RELEVANT_ENV_KEYS)):
            raise ValueError("startup context must bind every qualified non-secret environment key")
        if any(any(marker in key.upper() for marker in _SECRET_ENV_MARKERS) for key in env_keys):
            raise ValueError("startup context must not contain credential-bearing environment keys")
        env = dict(self.environment)
        if env.get("OPENCODE_DISABLE_MODELS_FETCH") != "1":
            raise ValueError("startup context must disable models.dev fetch with literal 1")
        if env.get("OPENCODE_DISABLE_PROJECT_CONFIG") != "1":
            raise ValueError("qualified profile requires project config discovery disabled")
        if env.get("OPENCODE_PURE") != "1":
            raise ValueError(
                "qualified profile requires external plugins disabled with OPENCODE_PURE=1"
            )
        if env.get("OPENCODE_MODELS_PATH") != self.catalog_path:
            raise ValueError("startup context must bind OPENCODE_MODELS_PATH to catalog_path")
        if (
            env.get("OPENCODE_CONFIG_CONTENT") is not None
            or env.get("OPENCODE_PERMISSION") is not None
        ):
            raise ValueError(
                "minimal qualified profile requires inline config and permission env to be absent"
            )

        expected_layers = tuple(_SOURCE_LAYER_ORDER)
        observed_layers = tuple(item.layer for item in self.source_observations)
        observed_indexes = tuple(item.precedence_index for item in self.source_observations)
        if observed_layers != expected_layers or observed_indexes != tuple(
            range(1, len(expected_layers) + 1)
        ):
            raise ValueError("startup source census must cover exact layers in precedence order")
        return self

    @property
    def content_digest(self) -> ContentDigest:
        payload = json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
        return "sha256:" + hashlib.sha256(payload).hexdigest()


class OpenCodeV11823ConfigurationObserver:
    """Concrete production observer for the accepted OpenCode 1.18.23 trusted-local profile."""

    def __init__(
        self,
        endpoint: str,
        *,
        permission_profile: OpenCodePermissionProfile,
        qualification_ref: OpenCodeConfigurationQualificationRef,
        startup_context: OpenCodeServerStartupContext,
        executable: str = "opencode",
        client: httpx.Client | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        parts = urlsplit(endpoint)
        if parts.scheme not in {"http", "https"} or parts.hostname not in {
            "127.0.0.1",
            "::1",
            "localhost",
        }:
            raise ValueError("observer endpoint must be explicit loopback HTTP(S)")
        if parts.port is None or parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError(
                "observer endpoint must bind explicit loopback port without credentials"
            )
        if qualification_ref.runtime_version != OPENCODE_V11823:
            raise ValueError("observer requires an OpenCode 1.18.23 qualification")
        if qualification_ref.runtime_api_generation != OPENCODE_API_GENERATION:
            raise ValueError("observer qualification API generation mismatch")
        if qualification_ref.adapter_version != OPENCODE_ADAPTER_VERSION:
            raise ValueError("observer qualification adapter version mismatch")
        self._endpoint = endpoint.rstrip("/")
        self._profile = permission_profile
        self._qualification = qualification_ref
        self._startup = startup_context
        self._executable = executable
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=httpx.Timeout(10.0),
            follow_redirects=False,
        )
        self._clock = clock or (lambda: datetime.now(UTC))

        if self.observer_ref != qualification_ref.observer_ref:
            raise ValueError("qualification does not bind this exact observer implementation")

    @property
    def observer_ref(self) -> OpenCodeConfigurationObserverRef:
        return opencode_v11823_observer_ref()

    def as_binding_reader(self) -> OpenCodeConfigurationBindingReader:
        return OpenCodeConfigurationBindingReader(observer_ref=self.observer_ref, read=self.read)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OpenCodeV11823ConfigurationObserver:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def read(
        self,
        request: RuntimeExecutionRequest,
        descriptor: RuntimeDescriptor,
    ) -> OpenCodeConfigurationBinding:
        self._validate_descriptor(descriptor)
        if request.basis.workspace.root != self._startup.workspace_root:
            raise OpenCodeObserverError(
                "request workspace does not match bound server startup context"
            )
        self._validate_observer_environment()

        sources_a = self._source_refs()
        catalog_a = self._catalog_state()
        snapshot_a = self._server_snapshot(request.basis.workspace.root)
        self._validate_server_paths(snapshot_a["path"])
        diagnostic_tree_a = self._diagnostic_tree_state()
        self._validate_catalog_cli(request.basis.workspace.root)
        debug = self._debug_agent(request.basis.workspace.root)
        diagnostic_tree_b = self._diagnostic_tree_state()
        snapshot_b = self._server_snapshot(request.basis.workspace.root)
        sources_b = self._source_refs()
        catalog_b = self._catalog_state()

        if sources_a != sources_b:
            raise OpenCodeObserverError(
                "OpenCode configuration source census changed during observation"
            )
        if catalog_a != catalog_b:
            raise OpenCodeObserverError("OpenCode model catalog changed during observation")
        if diagnostic_tree_a != diagnostic_tree_b:
            raise OpenCodeObserverError(
                "OpenCode diagnostic mutated a bound configuration directory"
            )
        if snapshot_a["digest"] != snapshot_b["digest"]:
            raise OpenCodeObserverError(
                "OpenCode effective configuration changed during observation"
            )

        agent = self._selected_agent(snapshot_b["agents"])
        debug_agent = self._normalize_debug_agent(debug)
        if self._agent_identity(agent) != self._agent_identity(debug_agent):
            raise OpenCodeObserverError(
                "debug-agent identity differs from running-server agent state"
            )

        allow, deny, ask = self._normalize_permissions(agent)
        tools = self._enabled_tools(debug_agent)
        plugins = self._plugin_exposure(snapshot_b["config"])
        mcp = self._mcp_exposure(snapshot_b["config"], snapshot_b["mcp"])
        subagents = self._subagent_exposure(snapshot_b["agents"], agent)

        config_payload = {
            "agent_id": self._profile.agent_id,
            "configuration_source_refs": sources_b,
            "normalized_allow_rules": allow,
            "normalized_deny_rules": deny,
            "normalized_ask_rules": ask,
            "effective_tool_exposure": tools,
            "plugin_exposure": plugins,
            "mcp_exposure": mcp,
            "subagent_exposure": subagents,
        }
        effective_digest = _digest_json(config_payload)
        provenance_digest = _digest_json(
            {
                "startup_context_digest": self._startup.content_digest,
                "server_snapshot_digest": snapshot_b["digest"],
                "catalog": catalog_b,
                "diagnostic_tree_digest": _digest_json(diagnostic_tree_b),
                "debug_agent_digest": _digest_json(debug_agent),
                "configuration_source_refs": sources_b,
            }
        )
        return OpenCodeConfigurationBinding(
            binding_id="opencode-config-" + provenance_digest.removeprefix("sha256:")[:24],
            runtime_id=OPENCODE_RUNTIME_ID,
            runtime_version=OPENCODE_V11823,
            runtime_api_generation=OPENCODE_API_GENERATION,
            adapter_version=OPENCODE_ADAPTER_VERSION,
            integration_qualification_ref=self._qualification,
            observer_ref=self.observer_ref,
            permission_profile_ref=request.basis.permission_profile_ref,
            agent_id=self._profile.agent_id,
            configuration_source_refs=sources_b,
            effective_configuration_digest=effective_digest,
            normalized_allow_rules=allow,
            normalized_deny_rules=deny,
            normalized_ask_rules=ask,
            effective_tool_exposure=tools,
            shell_exposed="bash" in tools,
            plugin_exposure=plugins,
            mcp_exposure=mcp,
            subagent_exposure=subagents,
            precedence_complete=True,
            observation_source="opencode-v1.18.23-running-server+local-cli",
            trust_basis="version-qualified-trusted-local-observer",
            provenance_digest=provenance_digest,
            observed_at=self._clock(),
            status=RequirementStatus.SATISFIED,
        )

    def _validate_descriptor(self, descriptor: RuntimeDescriptor) -> None:
        if (
            descriptor.runtime_id != OPENCODE_RUNTIME_ID
            or descriptor.runtime_version != OPENCODE_V11823
            or descriptor.api_generation != OPENCODE_API_GENERATION
            or descriptor.adapter_version != OPENCODE_ADAPTER_VERSION
        ):
            raise OpenCodeObserverError(
                "runtime descriptor does not match qualified OpenCode 1.18.23"
            )

    def _validate_observer_environment(self) -> None:
        for key, expected in self._startup.environment:
            actual = os.environ.get(key)
            if actual != expected:
                raise OpenCodeObserverError(f"observer environment mismatch for {key}")
        if os.environ.get("OPENCODE_DISABLE_MODELS_FETCH") != "1":
            raise OpenCodeObserverError("observer models.dev fetch-disable flag is not active")
        if os.environ.get("OPENCODE_MODELS_PATH") != self._startup.catalog_path:
            raise OpenCodeObserverError(
                "observer model catalog path does not match startup context"
            )
        for name in self._startup.credential_environment_names:
            if name not in os.environ:
                raise OpenCodeObserverError(
                    f"required credential environment presence missing: {name}"
                )

    def _source_refs(self) -> tuple[str, ...]:
        refs: list[str] = []
        for observation in self._startup.source_observations:
            for item in observation.files:
                path = Path(item.path)
                if observation.state == "PRESENT" and (
                    not path.is_file() or _digest_bytes(path.read_bytes()) != item.content_digest
                ):
                    raise OpenCodeObserverError(
                        f"configuration source changed or disappeared: {item.path}"
                    )
            refs.append(observation.canonical_ref())
        return tuple(refs)

    def _catalog_state(self) -> tuple[str, ContentDigest, int, int]:
        path = Path(self._startup.catalog_path)
        if not path.is_file():
            raise OpenCodeObserverError("bound OpenCode model catalog is unavailable")
        stat = path.stat()
        digest = _digest_bytes(path.read_bytes())
        if digest != self._startup.catalog_digest:
            raise OpenCodeObserverError("bound OpenCode model catalog digest changed")
        return (str(path), digest, stat.st_size, stat.st_mtime_ns)

    def _diagnostic_tree_state(self) -> tuple[tuple[str, int, int], ...]:
        roots: set[Path] = {
            Path(self._startup.config_root),
            Path(self._startup.home) / ".opencode",
        }
        config_dir = dict(self._startup.environment).get("OPENCODE_CONFIG_DIR")
        if config_dir:
            roots.add(Path(config_dir))
        workspace = Path(self._startup.workspace_root)
        stop = Path(self._startup.worktree_root)
        current = workspace
        while True:
            roots.add(current / ".opencode")
            if current == stop or current.parent == current:
                break
            current = current.parent

        state: list[tuple[str, int, int]] = []
        for root in sorted(roots):
            if not root.exists():
                state.append((str(root), -1, -1))
                continue
            for item in sorted(root.rglob("*")):
                try:
                    stat = item.stat()
                except OSError as exc:
                    raise OpenCodeObserverError(
                        "cannot census diagnostic configuration tree"
                    ) from exc
                state.append((str(item), stat.st_size, stat.st_mtime_ns))
        return tuple(state)

    def _server_snapshot(self, directory: str) -> _ServerSnapshot:
        path_info = _project_path(self._get_json("/path", directory))
        config = _project_config(self._get_json("/config", directory))
        agents = _project_agents(self._get_json("/agent", directory))
        mcp = _project_mcp_status(self._get_json("/mcp", directory))
        projected: _ServerSnapshot = {
            "path": path_info,
            "config": config,
            "agents": agents,
            "mcp": mcp,
            "digest": "sha256:" + "0" * 64,
        }
        projected["digest"] = _digest_json(
            {
                "path": projected["path"],
                "config": projected["config"],
                "agents": projected["agents"],
                "mcp": projected["mcp"],
            }
        )
        return projected

    def _get_json(self, route: str, directory: str) -> JsonValue:
        try:
            response = self._client.get(
                self._endpoint + route,
                params={"directory": directory},
            )
        except httpx.RequestError as exc:
            raise OpenCodeObserverError(
                f"OpenCode observation request failed for {route}"
            ) from exc
        if response.status_code != 200:
            raise OpenCodeObserverError(f"OpenCode observation request rejected for {route}")
        try:
            payload = _coerce_json(cast(object, response.json()))
        except (TypeError, ValueError) as exc:
            raise OpenCodeObserverError(
                f"OpenCode observation response is not safe JSON for {route}"
            ) from exc
        if isinstance(payload, dict) and set(payload) == {"data"}:
            return payload["data"]
        return payload

    def _validate_server_paths(self, value: dict[str, str]) -> None:
        expected = {
            "home": self._startup.home,
            "state": self._startup.state_root,
            "config": self._startup.config_root,
            "worktree": self._startup.worktree_root,
            "directory": self._startup.workspace_root,
        }
        if value != expected:
            raise OpenCodeObserverError("OpenCode server path identity does not match startup context")

    def _validate_catalog_cli(self, directory: str) -> None:
        self._require_cli_version(directory)
        result = self._run_cli(("models", "openrouter"), directory)
        rows = tuple(line.strip() for line in result.splitlines() if line.strip())
        expected = "openrouter/~deepseek/deepseek-flash-latest"
        if expected not in rows:
            raise OpenCodeObserverError("OpenCode model catalog does not expose the selected alias")
        if any(not row.startswith("openrouter/") for row in rows):
            raise OpenCodeObserverError("OpenCode model catalog output is not provider-scoped")

    def _debug_agent(self, directory: str) -> _DebugAgent:
        output = self._run_cli(("debug", "agent", self._profile.agent_id), directory)
        try:
            payload = _coerce_json(cast(object, json.loads(output)))
        except (TypeError, ValueError) as exc:
            raise OpenCodeObserverError("OpenCode debug-agent output is not safe JSON") from exc
        return _project_debug_agent(payload)

    def _require_cli_version(self, directory: str) -> None:
        version = self._run_cli(("--version",), directory).strip()
        if version != OPENCODE_V11823:
            raise OpenCodeObserverError("OpenCode CLI version differs from qualified runtime")

    def _run_cli(self, args: tuple[str, ...], directory: str) -> str:
        if "--verbose" in args or "--refresh" in args or "--tool" in args:
            raise OpenCodeObserverError("forbidden OpenCode diagnostic option")
        try:
            completed = subprocess.run(
                (self._executable, *args),
                cwd=directory,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
                text=True,
                encoding="utf-8",
                errors="strict",
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
            raise OpenCodeObserverError("OpenCode diagnostic command failed") from exc
        if completed.returncode != 0:
            raise OpenCodeObserverError("OpenCode diagnostic command was rejected")
        return completed.stdout

    def _selected_agent(self, agents: list[_ProjectedAgent]) -> _ProjectedAgent:
        matches = [agent for agent in agents if agent["name"] == self._profile.agent_id]
        if len(matches) != 1:
            raise OpenCodeObserverError(
                "exact configured Dogfood agent is unavailable or ambiguous"
            )
        return matches[0]

    def _normalize_debug_agent(self, value: _DebugAgent) -> _DebugAgent:
        return value

    def _agent_identity(self, agent: _ProjectedAgent) -> tuple[str, str, str, str]:
        model = agent["model"]
        if model is None:
            raise OpenCodeObserverError("configured agent lacks explicit model identity")
        provider = model["providerID"]
        model_id = model["modelID"]
        if provider != "openrouter" or model_id != "~deepseek/deepseek-flash-latest":
            raise OpenCodeObserverError(
                "configured agent does not bind the selected OpenRouter alias"
            )
        return (agent["name"], provider, model_id, _digest_json(agent["permission"]))

    def _normalize_permissions(
        self, agent: _ProjectedAgent
    ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
        buckets: dict[PermissionAction, list[str]] = {"allow": [], "deny": [], "ask": []}
        for rule in agent["permission"]:
            normalized = (
                rule["permission"]
                if rule["pattern"] == "*"
                else f'{rule["permission"]}:{rule["pattern"]}'
            )
            buckets[rule["action"]].append(normalized)
        result = (
            tuple(sorted(set(buckets["allow"]))),
            tuple(sorted(set(buckets["deny"]))),
            tuple(sorted(set(buckets["ask"]))),
        )
        expected = (
            tuple(sorted(self._profile.allow)),
            tuple(sorted(self._profile.deny)),
            tuple(sorted(self._profile.ask)),
        )
        if result != expected:
            raise OpenCodeObserverError("effective permission rules do not match accepted profile")
        return result

    def _enabled_tools(self, debug_agent: _DebugAgent) -> tuple[str, ...]:
        enabled = tuple(sorted(key for key, value in debug_agent["tools"].items() if value))
        policy_tools = self._profile.allowed_tools or self._profile.allow
        expected_tools = tuple(
            sorted(
                (
                    *policy_tools,
                    *self._profile.allowed_plugins,
                    *self._profile.allowed_mcp_servers,
                    *self._profile.allowed_subagents,
                )
            )
        )
        if enabled != expected_tools:
            raise OpenCodeObserverError("effective tool exposure does not match accepted profile")
        return enabled

    def _plugin_exposure(self, config: _ProjectedConfig) -> tuple[str, ...]:
        result = config["plugins"]
        if result != self._profile.allowed_plugins:
            raise OpenCodeObserverError("resolved plugin exposure does not match accepted profile")
        return result

    def _mcp_exposure(
        self, config: _ProjectedConfig, status: dict[str, str]
    ) -> tuple[str, ...]:
        result = tuple(sorted(set(config["mcp_names"]) | set(status)))
        if result != self._profile.allowed_mcp_servers:
            raise OpenCodeObserverError("resolved MCP exposure does not match accepted profile")
        return result

    def _subagent_exposure(
        self,
        agents: list[_ProjectedAgent],
        selected: _ProjectedAgent,
    ) -> tuple[str, ...]:
        exposed: list[str] = []
        for agent in agents:
            if agent["mode"] != "subagent":
                continue
            name = agent["name"]
            action = _permission_action("task", name, selected["permission"])
            if action == "allow":
                exposed.append(name)
            elif action == "ask":
                raise OpenCodeObserverError("subagent exposure remains interactive/ambiguous")
        result = tuple(sorted(set(exposed)))
        if result != self._profile.allowed_subagents:
            raise OpenCodeObserverError(
                "resolved subagent exposure does not match accepted profile"
            )
        return result


def _permission_action(
    permission: str, pattern: str, rules: tuple[_PermissionRule, ...]
) -> PermissionAction:
    result: PermissionAction = "ask"
    matched = False
    for rule in rules:
        if rule["permission"] not in {"*", permission}:
            continue
        if fnmatch.fnmatchcase(pattern, rule["pattern"]):
            result = rule["action"]
            matched = True
    return result if matched else "ask"


def _project_path(value: JsonValue) -> dict[str, str]:
    data = _as_object(value, "path")
    required = ("home", "state", "config", "worktree", "directory")
    result: dict[str, str] = {}
    for key in required:
        item = data.get(key)
        if not isinstance(item, str):
            raise OpenCodeObserverError(f"OpenCode /path field is malformed: {key}")
        result[key] = item
    return result


def _project_config(value: JsonValue) -> _ProjectedConfig:
    config = _as_object(value, "config")
    plugin_value = config.get("plugin", [])
    if plugin_value is None:
        plugin_value = []
    if not isinstance(plugin_value, list):
        raise OpenCodeObserverError("resolved plugin configuration is malformed")
    plugins: list[str] = []
    for item in plugin_value:
        if isinstance(item, str):
            plugins.append(item)
            continue
        if isinstance(item, list) and item and isinstance(item[0], str):
            plugins.append(item[0])
            continue
        raise OpenCodeObserverError("resolved plugin configuration is malformed")

    mcp_value = config.get("mcp", {})
    if mcp_value is None:
        mcp_value = {}
    mcp = _as_object(mcp_value, "MCP configuration")

    agent_value = config.get("agent", {})
    if agent_value is None:
        agent_value = {}
    agents = _as_object(agent_value, "agent configuration")

    return {
        "plugins": tuple(sorted(set(plugins))),
        "mcp_names": tuple(sorted(mcp)),
        "agent_names": tuple(sorted(agents)),
        "legacy_tools_present": bool(config.get("tools")),
        "permission_present": bool(config.get("permission")),
    }


def _project_agents(value: JsonValue) -> list[_ProjectedAgent]:
    return [_project_agent(item) for item in _as_array(value, "agent list")]


def _project_agent(value: JsonValue) -> _ProjectedAgent:
    data = _as_object(value, "agent")
    name = data.get("name")
    mode = data.get("mode")
    hidden_value = data.get("hidden")
    if not isinstance(name, str) or not isinstance(mode, str):
        raise OpenCodeObserverError("resolved agent identity is malformed")
    if hidden_value is not None and not isinstance(hidden_value, bool):
        raise OpenCodeObserverError("resolved agent hidden state is malformed")

    model_value = data.get("model")
    model = None if model_value is None else _project_model(model_value)
    rules = _project_permission_rules(data.get("permission"))
    return {
        "name": name,
        "mode": mode,
        "hidden": hidden_value,
        "permission": rules,
        "model": model,
    }


def _project_debug_agent(value: JsonValue) -> _DebugAgent:
    data = _as_object(value, "debug agent")
    base = _project_agent(value)
    tools_value = _as_object(data.get("tools"), "debug-agent tools")
    tools: dict[str, bool] = {}
    for key, item in tools_value.items():
        if not isinstance(item, bool):
            raise OpenCodeObserverError("debug-agent tool exposure is malformed")
        tools[key] = item
    return {
        **base,
        "tools": tools,
    }


def _project_model(value: JsonValue) -> _ModelRef:
    data = _as_object(value, "agent model")
    provider = data.get("providerID")
    model_id = data.get("modelID")
    if not isinstance(provider, str) or not isinstance(model_id, str):
        raise OpenCodeObserverError("configured agent model identity is malformed")
    return {"providerID": provider, "modelID": model_id}


def _project_permission_rules(value: JsonValue | None) -> tuple[_PermissionRule, ...]:
    if value is None:
        raise OpenCodeObserverError("configured agent permission rules are unavailable")
    result: list[_PermissionRule] = []
    for item in _as_array(value, "permission rules"):
        rule = _as_object(item, "permission rule")
        permission = rule.get("permission")
        pattern = rule.get("pattern")
        action = rule.get("action")
        if (
            not isinstance(permission, str)
            or not isinstance(pattern, str)
            or action not in {"allow", "deny", "ask"}
        ):
            raise OpenCodeObserverError("configured agent permission rule is malformed")
        result.append(
            {
                "permission": permission,
                "pattern": pattern,
                "action": cast(PermissionAction, action),
            }
        )
    return tuple(result)


def _project_mcp_status(value: JsonValue) -> dict[str, str]:
    status = _as_object(value, "MCP status")
    result: dict[str, str] = {}
    for name, item in status.items():
        if isinstance(item, str):
            result[name] = item
            continue
        data = _as_object(item, "MCP status entry")
        selected: dict[str, str | bool | int] = {}
        for key in ("status", "state", "type"):
            field = data.get(key)
            if isinstance(field, (str, bool, int)):
                selected[key] = field
        if not selected:
            raise OpenCodeObserverError("resolved MCP status is not safely classifiable")
        result[name] = _digest_json(selected)
    return result


def _as_object(value: JsonValue | None, label: str) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise OpenCodeObserverError(f"{label} must be a JSON object")
    return value


def _as_array(value: JsonValue, label: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise OpenCodeObserverError(f"{label} must be a JSON array")
    return value


def _coerce_json(value: object) -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        raw_list = cast(list[object], value)
        return [_coerce_json(item) for item in raw_list]
    if isinstance(value, dict):
        raw_object = cast(dict[object, object], value)
        result: dict[str, JsonValue] = {}
        for key, item in raw_object.items():
            if not isinstance(key, str):
                raise TypeError("JSON object key is not a string")
            result[key] = _coerce_json(item)
        return result
    raise TypeError("unsupported JSON value")


def _digest_bytes(value: bytes) -> ContentDigest:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _digest_json(value: object) -> ContentDigest:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return _digest_bytes(payload)
