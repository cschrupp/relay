"""Protected verification oracle for Relay Slice 3.1 Dogfood 001."""

from __future__ import annotations

import copy
import unittest

from dogfood.execution_order import (
    DependencyCycleError,
    UnknownNodeError,
    resolve_execution_order,
)


class ResolveExecutionOrderTests(unittest.TestCase):
    def test_empty_request(self) -> None:
        graph = {"unused": ("missing",)}
        self.assertEqual(resolve_execution_order((), graph), ())

    def test_single_independent_node(self) -> None:
        self.assertEqual(resolve_execution_order(("alpha",), {"alpha": ()}), ("alpha",))

    def test_linear_dependency_chain(self) -> None:
        graph = {
            "build": ("compile",),
            "compile": ("prepare",),
            "prepare": (),
        }
        self.assertEqual(
            resolve_execution_order(("build",), graph),
            ("prepare", "compile", "build"),
        )

    def test_diamond_dependency(self) -> None:
        graph = {
            "build": ("lint", "test"),
            "lint": ("prepare",),
            "test": ("prepare",),
            "prepare": (),
        }
        self.assertEqual(
            resolve_execution_order(("build",), graph),
            ("prepare", "lint", "test", "build"),
        )

    def test_multiple_independent_requested_roots(self) -> None:
        graph = {
            "deploy": ("package",),
            "package": ("build",),
            "build": (),
            "docs": (),
        }
        self.assertEqual(
            resolve_execution_order(("docs", "deploy"), graph),
            ("build", "docs", "package", "deploy"),
        )

    def test_shared_transitive_dependency(self) -> None:
        graph = {
            "service-a": ("compile",),
            "service-b": ("compile",),
            "compile": ("prepare",),
            "prepare": (),
        }
        self.assertEqual(
            resolve_execution_order(("service-b", "service-a"), graph),
            ("prepare", "compile", "service-a", "service-b"),
        )

    def test_duplicate_requested_roots(self) -> None:
        graph = {"build": ("prepare",), "prepare": ()}
        self.assertEqual(
            resolve_execution_order(("build", "build"), graph),
            ("prepare", "build"),
        )

    def test_dictionary_insertion_order_independence(self) -> None:
        graph_a = {
            "deploy": ("package",),
            "package": ("build",),
            "build": (),
            "docs": (),
        }
        graph_b = {
            "docs": (),
            "build": (),
            "package": ("build",),
            "deploy": ("package",),
        }
        expected = ("build", "docs", "package", "deploy")
        self.assertEqual(resolve_execution_order(("deploy", "docs"), graph_a), expected)
        self.assertEqual(resolve_execution_order(("docs", "deploy"), graph_b), expected)

    def test_prerequisite_tuple_order_independence(self) -> None:
        graph_a = {
            "build": ("test", "lint"),
            "lint": ("prepare",),
            "test": ("prepare",),
            "prepare": (),
        }
        graph_b = {
            "build": ("lint", "test"),
            "lint": ("prepare",),
            "test": ("prepare",),
            "prepare": (),
        }
        expected = ("prepare", "lint", "test", "build")
        self.assertEqual(resolve_execution_order(("build",), graph_a), expected)
        self.assertEqual(resolve_execution_order(("build",), graph_b), expected)

    def test_unknown_requested_node(self) -> None:
        with self.assertRaisesRegex(UnknownNodeError, "missing"):
            resolve_execution_order(("missing",), {"known": ()})

    def test_unknown_reachable_prerequisite(self) -> None:
        with self.assertRaisesRegex(UnknownNodeError, "compile"):
            resolve_execution_order(("build",), {"build": ("compile",)})

    def test_direct_self_cycle(self) -> None:
        with self.assertRaisesRegex(DependencyCycleError, "alpha"):
            resolve_execution_order(("alpha",), {"alpha": ("alpha",)})

    def test_multi_node_cycle(self) -> None:
        graph = {
            "alpha": ("beta",),
            "beta": ("gamma",),
            "gamma": ("alpha",),
        }
        with self.assertRaises(DependencyCycleError) as raised:
            resolve_execution_order(("alpha",), graph)
        self.assertTrue(
            any(node in str(raised.exception) for node in ("alpha", "beta", "gamma"))
        )

    def test_unrelated_invalid_component_is_not_traversed(self) -> None:
        graph = {
            "build": ("prepare",),
            "prepare": (),
            "unrelated": ("missing",),
        }
        self.assertEqual(
            resolve_execution_order(("build",), graph),
            ("prepare", "build"),
        )

    def test_inputs_are_not_mutated(self) -> None:
        requested = ("build", "docs")
        graph = {
            "build": ("lint", "test"),
            "lint": ("prepare",),
            "test": ("prepare",),
            "prepare": (),
            "docs": (),
        }
        requested_before = requested
        graph_before = copy.deepcopy(graph)

        resolve_execution_order(requested, graph)

        self.assertEqual(requested, requested_before)
        self.assertEqual(graph, graph_before)


if __name__ == "__main__":
    unittest.main()
