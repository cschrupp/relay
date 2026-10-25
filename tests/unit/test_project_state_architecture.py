"""Static boundary checks for the pure Slice 2.5 project-state package."""

from __future__ import annotations

import ast
from pathlib import Path

PACKAGE = Path(__file__).parents[2] / "src" / "relay_engine" / "project_state"
FORBIDDEN_IMPORTS = (
    "relay_engine.database",
    "relay_engine.db",
    "relay_engine.lifecycle",
    "relay_engine.agent_runtime",
    "relay_engine.execution_workspace",
    "relay_engine.providers",
    "sqlalchemy",
    "sqlite3",
    "subprocess",
    "socket",
    "httpx",
    "requests",
    "openai",
    "anthropic",
    "opencode",
)


def _imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.append(node.module)
    return tuple(names)


def test_project_state_has_no_runtime_io_persistence_or_execution_dependencies() -> None:
    paths = tuple(sorted(PACKAGE.glob("*.py")))
    assert {path.name for path in paths} == {
        "__init__.py",
        "compilation.py",
        "models.py",
        "resolution.py",
    }
    imports = tuple(name for path in paths for name in _imports(path))
    violations = tuple(
        imported
        for imported in imports
        if any(
            imported == forbidden or imported.startswith(f"{forbidden}.")
            for forbidden in FORBIDDEN_IMPORTS
        )
    )
    assert violations == ()


def test_resolver_and_compiler_are_explicit_pure_functions() -> None:
    resolution = ast.parse((PACKAGE / "resolution.py").read_text(encoding="utf-8"))
    compilation = ast.parse((PACKAGE / "compilation.py").read_text(encoding="utf-8"))
    resolution_functions = {
        node.name for node in resolution.body if isinstance(node, ast.FunctionDef)
    }
    compilation_functions = {
        node.name for node in compilation.body if isinstance(node, ast.FunctionDef)
    }
    assert "resolve_project_state" in resolution_functions
    assert "evaluate_applicability" in resolution_functions
    assert {"compile_authority", "check_candidate_freshness"} <= compilation_functions
    assert "AgentRuntime" not in (PACKAGE / "resolution.py").read_text(encoding="utf-8")
