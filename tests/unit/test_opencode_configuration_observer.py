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
