"""Frozen deterministic oracle for Relay Dogfood 001."""

from __future__ import annotations

from copy import deepcopy

import pytest

from relay_engine.dogfood.execution_order import (
    DependencyCycleError,
    UnknownNodeError,
    resolve_execution_order,
)


def test_t01_empty_request_ignores_unrelated_invalid_graph() -> None:
    assert resolve_execution_order((), {"broken": ("missing",)}) == ()


def test_t02_single_independent_requested_node() -> None:
    assert resolve_execution_order(("lint",), {"lint": ()}) == ("lint",)


def test_t03_linear_dependency_chain() -> None:
    graph = {"build": ("compile",), "compile": ("prepare",), "prepare": ()}

    assert resolve_execution_order(("build",), graph) == (
        "prepare",
        "compile",
        "build",
    )


def test_t04_diamond_dependency_uses_lexical_tie_breaking() -> None:
    graph = {
        "build": ("test", "lint"),
        "test": ("prepare",),
        "lint": ("prepare",),
        "prepare": (),
    }

    assert resolve_execution_order(("build",), graph) == (
        "prepare",
        "lint",
        "test",
        "build",
    )


def test_t05_multiple_requested_roots_use_global_lexical_tie_breaking() -> None:
    graph = {
        "deploy": ("package",),
        "package": ("build",),
        "build": (),
        "docs": (),
    }

    assert resolve_execution_order(("docs", "deploy"), graph) == (
        "build",
        "docs",
        "package",
        "deploy",
    )


def test_t06_shared_transitive_dependency_appears_once() -> None:
    graph = {
        "service-a": ("compile",),
        "service-b": ("compile",),
        "compile": ("prepare",),
        "prepare": (),
    }

    result = resolve_execution_order(("service-a", "service-b"), graph)

    assert result == ("prepare", "compile", "service-a", "service-b")
    assert result.count("prepare") == 1
    assert result.count("compile") == 1


def test_t07_duplicate_requested_roots_are_deduplicated() -> None:
    graph = {"build": ("compile",), "compile": ()}

    assert resolve_execution_order(("build", "build"), graph) == (
        "compile",
        "build",
    )


def test_t08_dictionary_insertion_order_does_not_change_result() -> None:
    first = {
        "build": ("lint", "test"),
        "lint": ("prepare",),
        "test": ("prepare",),
        "prepare": (),
    }
    second = {
        "prepare": (),
        "test": ("prepare",),
        "lint": ("prepare",),
        "build": ("lint", "test"),
    }

    assert resolve_execution_order(("build",), first) == resolve_execution_order(("build",), second)


def test_t09_prerequisite_tuple_order_does_not_change_result() -> None:
    first = {
        "build": ("test", "lint"),
        "test": ("prepare",),
        "lint": ("prepare",),
        "prepare": (),
    }
    second = {
        "build": ("lint", "test"),
        "test": ("prepare",),
        "lint": ("prepare",),
        "prepare": (),
    }

    assert resolve_execution_order(("build",), first) == resolve_execution_order(("build",), second)


def test_t10_unknown_requested_node_names_the_missing_node() -> None:
    with pytest.raises(UnknownNodeError) as error:
        resolve_execution_order(("unknown-root",), {"build": ()})

    assert "unknown-root" in str(error.value)


def test_t11_unknown_reachable_prerequisite_names_the_missing_node() -> None:
    with pytest.raises(UnknownNodeError) as error:
        resolve_execution_order(("build",), {"build": ("missing-compile",)})

    assert "missing-compile" in str(error.value)


def test_t12_direct_self_cycle_names_the_cycle_node() -> None:
    with pytest.raises(DependencyCycleError) as error:
        resolve_execution_order(("alpha",), {"alpha": ("alpha",)})

    assert "alpha" in str(error.value)


def test_t13_multi_node_cycle_names_a_cycle_member() -> None:
    graph = {
        "alpha": ("beta",),
        "beta": ("gamma",),
        "gamma": ("alpha",),
    }

    with pytest.raises(DependencyCycleError) as error:
        resolve_execution_order(("alpha",), graph)

    assert any(node in str(error.value) for node in graph)


def test_t14_unreachable_invalid_component_is_not_traversed() -> None:
    graph = {
        "build": ("prepare",),
        "prepare": (),
        "unrelated-a": ("unrelated-b",),
        "unrelated-b": ("unrelated-a",),
        "also-unrelated": ("missing-node",),
    }

    assert resolve_execution_order(("build",), graph) == ("prepare", "build")


def test_t15_inputs_remain_unchanged() -> None:
    requested = ("build", "docs")
    graph = {
        "build": ("test", "lint"),
        "lint": ("prepare",),
        "test": ("prepare",),
        "prepare": (),
        "docs": (),
    }
    requested_before = deepcopy(requested)
    graph_before = deepcopy(graph)

    resolve_execution_order(requested, graph)

    assert requested == requested_before
    assert graph == graph_before
