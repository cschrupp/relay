"""Static architecture boundaries for the Slice 2.4 package."""

from __future__ import annotations

import ast
from pathlib import Path

PACKAGE = Path(__file__).parents[2] / "src/relay_engine/execution_workspace"


def test_production_package_has_no_runtime_persistence_network_or_authority_wiring() -> None:
    forbidden_roots = {
        "relay_engine.persistence",
        "relay_engine.lifecycle",
        "relay_engine.human_control",
        "relay_engine.manual_evaluation",
        "relay_engine.promotion",
        "httpx",
        "requests",
        "urllib",
        "boto3",
        "docker",
    }
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                names = (node.module,)
            else:
                continue
            assert not any(
                name == root or name.startswith(root + ".")
                for name in names
                for root in forbidden_roots
            ), path
    runtime_models = (PACKAGE / "models.py").read_text(encoding="utf-8")
    assert "RuntimeWorkspaceAttachment" in runtime_models
    assert "AgentRuntime" not in runtime_models


def test_local_provider_has_no_remote_git_or_agentruntime_invocation() -> None:
    source = (PACKAGE / "local_clone.py").read_text(encoding="utf-8")
    for forbidden in ('"fetch"', '"pull"', '"push"', "AgentRuntime(", "requests.", "urllib."):
        assert forbidden not in source


def test_plan_preflight_is_policy_independent() -> None:
    evaluation_source = (PACKAGE / "evaluation.py").read_text(encoding="utf-8")
    signature = evaluation_source.split("def evaluate_workspace_preflight(", maxsplit=1)[1].split(
        ") ->", maxsplit=1
    )[0]
    assert "WorkspacePlan" in signature
    assert "WorkspacePolicyDefinition" not in signature
