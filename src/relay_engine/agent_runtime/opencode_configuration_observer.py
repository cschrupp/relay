"""Exact-version OpenCode 1.18.23 configuration observation for trusted-local execution."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import subprocess
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
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
        if not self.layer.strip() or not self.identity.strip() or not self.observation_method.strip():
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
            raise ValueError("qualified profile requires external plugins disabled with OPENCODE_PURE=1")
        if env.get("OPENCODE_MODELS_PATH") != self.catalog_path:
            raise ValueError("startup context must bind OPENCODE_MODELS_PATH to catalog_path")
        if env.get("OPENCODE_CONFIG_CONTENT") is not None or env.get("OPENCODE_PERMISSION") is not None:
            raise ValueError("minimal qualified profile requires inline config and permission env to be absent")

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
            raise ValueError("observer endpoint must bind explicit loopback port without credentials")
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
            raise OpenCodeObserverError("request workspace does not match bound server startup context")
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
            raise OpenCodeObserverError("OpenCode configuration source census changed during observation")
        if catalog_a != catalog_b:
            raise OpenCodeObserverError("OpenCode model catalog changed during observation")
        if diagnostic_tree_a != diagnostic_tree_b:
            raise OpenCodeObserverError("OpenCode diagnostic mutated a bound configuration directory")
        if snapshot_a["digest"] != snapshot_b["digest"]:
            raise OpenCodeObserverError("OpenCode effective configuration changed during observation")

        agent = self._selected_agent(snapshot_b["agents"])
        debug_agent = self._normalize_debug_agent(debug)
        if self._agent_identity(agent) != self._agent_identity(debug_agent):
            raise OpenCodeObserverError("debug-agent identity differs from running-server agent state")

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
            runtime_version=descriptor.runtime_version,
            runtime_api_generation=descriptor.api_generation,
            adapter_version=descriptor.adapter_version,
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
            raise OpenCodeObserverError("runtime descriptor does not match qualified OpenCode 1.18.23")

    def _validate_observer_environment(self) -> None:
        for key, expected in self._startup.environment:
            actual = os.environ.get(key)
            if actual != expected:
                raise OpenCodeObserverError(f"observer environment mismatch for {key}")
        if os.environ.get("OPENCODE_DISABLE_MODELS_FETCH") != "1":
            raise OpenCodeObserverError("observer models.dev fetch-disable flag is not active")
        if os.environ.get("OPENCODE_MODELS_PATH") != self._startup.catalog_path:
            raise OpenCodeObserverError("observer model catalog path does not match startup context")

    def _source_refs(self) -> tuple[str, ...]:
        refs: list[str] = []
        for observation in self._startup.source_observations:
            for item in observation.files:
                path = Path(item.path)
                if observation.state == "PRESENT":
                    if not path.is_file() or _digest_bytes(path.read_bytes()) != item.content_digest:
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
