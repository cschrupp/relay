"""Static boundaries for the pure Slice 2.3 contract package."""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[2]
PACKAGE = ROOT / "src/relay_engine/work_packets"
AUTHORIZED_FILES = {
    "src/relay_engine/work_packets/__init__.py",
    "src/relay_engine/work_packets/models.py",
    "src/relay_engine/work_packets/evaluation.py",
    "tests/unit/test_work_packet_models.py",
    "tests/unit/test_work_packet_evaluation.py",
    "tests/unit/test_work_packet_architecture.py",
}
FORBIDDEN_IMPORT_PREFIXES = (
    "relay_engine.persistence",
    "relay_engine.lifecycle",
    "relay_engine.human_control",
    "relay_engine.manual_evaluation",
    "relay_engine.promotion",
    "relay_engine.bootstrap",
    "relay_engine.agent_runtime.protocol",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "sqlite3",
)
FORBIDDEN_CALLS = {
    "authorize_work",
    "accept_result",
    "promote_result",
    "execute_packet",
    "invoke_agent",
    "create_workspace",
    "resolve_material",
}


def _import_name(node: ast.Import | ast.ImportFrom) -> str:
    if isinstance(node, ast.Import):
        return node.names[0].name
    return node.module or ""


def test_production_package_has_no_execution_storage_or_network_imports() -> None:
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = [
            node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        names = [_import_name(node) for node in imports]
        assert not any(
            imported == prefix or imported.startswith(prefix + ".")
            for imported in names
            for prefix in FORBIDDEN_IMPORT_PREFIXES
        ), f"forbidden import in {path}: {names}"
        assert not any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in FORBIDDEN_CALLS
            for node in ast.walk(tree)
        )
        assert not any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in FORBIDDEN_CALLS
            for node in ast.walk(tree)
        )


def test_package_has_no_mutable_resolver_registry_or_filesystem_materialization() -> None:
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        assert not any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"open", "Path"}
            for node in ast.walk(tree)
        )
        assert not any(
            isinstance(node, ast.Name) and node.id in {"resolver_registry", "RESOLVER_REGISTRY"}
            for node in ast.walk(tree)
        )


def test_package_does_not_define_authority_or_latest_resolution_operations() -> None:
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        functions = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert not set(functions) & FORBIDDEN_CALLS
        assert not any("latest" in name or "best_match" in name for name in functions)


def test_change_surface_is_exactly_the_six_authorized_files() -> None:
    result = subprocess.run(
        ["git", "diff", "--name-only", "f0996a1909bff8dda76a455d6d88d027b4b736f2...HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    changed = set(result.stdout.splitlines())
    # Uncommitted authorized edits are included separately while developing.
    status = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    changed.update(line[3:] for line in status.stdout.splitlines() if line)
    assert changed <= AUTHORIZED_FILES
