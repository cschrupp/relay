import ast
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]


def _production_ref_update_calls() -> list[tuple[str, int, ast.Call]]:
    calls: list[tuple[str, int, ast.Call]] = []
    source_root = ROOT / "src"
    for path in source_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if isinstance(function, ast.Attribute) and function.attr == "update_git_ref":
                calls.append((path.relative_to(ROOT).as_posix(), node.lineno, node))
    return calls


def test_production_canonical_ref_writer_callsite_allowlist_is_exact() -> None:
    calls = _production_ref_update_calls()
    assert Counter(path for path, _, _ in calls) == {
        "src/relay_engine/promotion/service.py": 1,
        "src/relay_engine/repository_sync/service.py": 1,
    }
    for _, _, call in calls:
        force = next((item.value for item in call.keywords if item.arg == "force"), None)
        assert isinstance(force, ast.Constant) and force.value is False


def test_separate_ruleset_verifier_has_no_non_get_request() -> None:
    path = ROOT / "src/relay_engine/integrations/github/ruleset_verifier.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    requests = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "GitHubRequest"
    ]
    assert requests
    assert all(
        any(
            keyword.arg == "method"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value == "GET"
            for keyword in request.keywords
        )
        for request in requests
    )
