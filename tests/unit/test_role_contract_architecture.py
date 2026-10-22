"""Static boundary checks for the isolated Role Contracts package."""

import ast
from pathlib import Path

from relay_engine.role_contracts import (
    ContractSelection,
    RoleContractApplicability,
    SelectionSource,
)

PACKAGE_ROOT = Path(__file__).parents[2] / "src" / "relay_engine" / "role_contracts"
FORBIDDEN_IMPORTS = (
    "relay_engine.persistence",
    "relay_engine.lifecycle",
    "relay_engine.human_control",
    "relay_engine.manual_evaluation",
    "relay_engine.promotion",
    "relay_engine.board",
    "relay_engine.bootstrap_discovery",
)


def test_package_has_no_governance_mutation_or_ui_imports() -> None:
    for source_path in PACKAGE_ROOT.glob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = tuple(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported = (node.module or "",)
            else:
                continue
            assert not any(
                name == forbidden or name.startswith(f"{forbidden}.")
                for name in imported
                for forbidden in FORBIDDEN_IMPORTS
            ), f"forbidden import in {source_path}: {imported}"


def test_package_has_no_runtime_calls_or_authority_mutators() -> None:
    prohibited_names = {
        "authorize_work",
        "issue_authority",
        "accept_result",
        "promote_result",
        "advance_lifecycle",
        "create_successor",
        "AgentRuntime",
        "requests",
        "httpx",
        "urlopen",
    }
    names: set[str] = set()
    calls: set[str] = set()
    for source_path in PACKAGE_ROOT.glob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        names.update(node.id for node in ast.walk(tree) if isinstance(node, ast.Name))
        calls.update(
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        )
    assert not prohibited_names.intersection(names | calls)


def test_human_root_authority_is_external_and_not_bootstrapped_by_contract() -> None:
    assert set(SelectionSource) == {SelectionSource.POLICY, SelectionSource.HUMAN_AUTHORITY}
    assert set(RoleContractApplicability) == {
        RoleContractApplicability.APPLICABLE,
        RoleContractApplicability.NOT_APPLICABLE,
        RoleContractApplicability.INDETERMINATE,
    }
    assert ContractSelection.SELECTS_THIS_CONTRACT.value == "SELECTS_THIS_CONTRACT"
    model_source = (PACKAGE_ROOT / "models.py").read_text(encoding="utf-8")
    evaluation_source = (PACKAGE_ROOT / "evaluation.py").read_text(encoding="utf-8")
    assert "Human root authority" in model_source
    assert "already-established facts" in model_source
    assert "role_contract_ref(contract)" in evaluation_source
    assert "applicability.status is not RoleContractApplicability.APPLICABLE" in evaluation_source


def test_package_has_no_role_catalog_latest_resolver_or_role_uuid_prefix() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in PACKAGE_ROOT.glob("*.py"))
    assert "latest_role_contract" not in source
    assert "max_revision" not in source
    assert '"role_"' not in source
    assert "registry: dict" not in source
    assert "ProposedWorkObservation" not in source
    assert "def authorize_work" not in source
