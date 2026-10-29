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
