# Relay Slice 3.1 — Dogfood 001 — Frozen Engineering Task

**Document class:** Immutable dogfood task specification  
**Status:** IMMUTABLE / FROZEN  
**Date:** 2026-10-26  
**Record:** `RLY-S31-DOGFOOD-001-TASK-001`  
**Canonical Relay basis:** `6c0add5611e2e8eab942787e0d6a1afafaa4a2f4`

## 1. Objective

Implement one pure-Python function in a disposable dogfood repository:

```python
def resolve_execution_order(
    requested: tuple[str, ...],
    prerequisites: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    ...
```

The function returns the deterministic topological execution order for the requested nodes and their reachable prerequisite closure.

## 2. Public API

The implementation module must expose exactly:

```python
class UnknownNodeError(ValueError):
    pass


class DependencyCycleError(ValueError):
    pass


def resolve_execution_order(
    requested: tuple[str, ...],
    prerequisites: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    ...
```

The exception classes and function signature are frozen.

## 3. Normative behavior

1. Include every requested node exactly once.
2. Duplicate requested nodes do not duplicate output.
3. Include every direct and transitive prerequisite reachable from requested nodes.
4. Exclude graph nodes unrelated to requested nodes.
5. Every prerequisite appears before every dependent node.
6. When multiple required nodes are simultaneously eligible, select the lexicographically smallest Python string.
7. Dictionary insertion order, prerequisite tuple order, and independent requested-root order must not change the result.
8. Empty `requested` returns `()`; unrelated invalid graph components need not be traversed.
9. Unknown requested node -> `UnknownNodeError`.
10. Unknown reachable prerequisite -> `UnknownNodeError`.
11. Reachable self-cycle or multi-node cycle -> `DependencyCycleError`.
12. Shared dependencies appear once.
13. Inputs must not be mutated.
14. Standard library only.
15. No filesystem, network, subprocess, environment-variable, clock, randomness, or global mutable-state dependency.

## 4. Representative exact cases

### Diamond

```python
requested = ("build",)
prerequisites = {
    "build": ("lint", "test"),
    "lint": ("prepare",),
    "test": ("prepare",),
    "prepare": (),
}
```

Expected:

```python
("prepare", "lint", "test", "build")
```

### Multiple roots

```python
requested = ("docs", "deploy")
prerequisites = {
    "deploy": ("package",),
    "package": ("build",),
    "build": (),
    "docs": (),
}
```

Expected:

```python
("build", "docs", "package", "deploy")
```

### Shared dependency

```python
requested = ("service-a", "service-b")
prerequisites = {
    "service-a": ("compile",),
    "service-b": ("compile",),
    "compile": ("prepare",),
    "prepare": (),
}
```

Expected:

```python
("prepare", "compile", "service-a", "service-b")
```

## 5. Disposable fixture layout

Preparation must materialize exactly this repository layout:

```text
src/dogfood/__init__.py
src/dogfood/execution_order.py
tests/__init__.py
tests/test_execution_order.py
```

No dependency/configuration file is required.

Initial `src/dogfood/execution_order.py`:

```python
"""Dogfood target: deterministic prerequisite resolution."""


class UnknownNodeError(ValueError):
    pass


class DependencyCycleError(ValueError):
    pass


def resolve_execution_order(
    requested: tuple[str, ...],
    prerequisites: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    raise NotImplementedError
```

Both `__init__.py` files are empty.

## 6. Protected verification oracle

`tests/test_execution_order.py` is a **Protected Verification Asset**.

The implementation actor may READ and EXECUTE it but MUST NOT WRITE, replace, chmod, rename, delete, regenerate, or indirectly mutate it.

The frozen oracle must deterministically test at least:

```text
T01 empty request
T02 single independent node
T03 linear dependency chain
T04 diamond dependency
T05 multiple independent requested roots
T06 shared transitive dependency
T07 duplicate requested roots
T08 dictionary insertion-order independence
T09 prerequisite tuple-order independence
T10 unknown requested node
T11 unknown reachable prerequisite
T12 direct self-cycle
T13 multi-node cycle
T14 unrelated invalid component not traversed
T15 input values unchanged
```

The preparation operator may materialize the protected test file from this frozen specification before the governed runtime starts. Once the fixture baseline commit is created, the test file is immutable for the attempt.

The oracle command is:

```bash
PYTHONPATH=src python -m unittest -v tests.test_execution_order
```

The execution environment must prove that the selected `python` provides the standard library only; no dependency installation is authorized.

## 7. Authorized mutation surface

The implementation actor may mutate exactly:

```text
src/dogfood/execution_order.py
```

Maximum changed production files: **1**.

The actor may not modify:

```text
src/dogfood/__init__.py
tests/__init__.py
tests/test_execution_order.py
.git/**
```

No other file may be created, deleted, renamed, or modified.

## 8. Runtime-visible task text

The runtime payload must communicate this outcome, not an implementation recipe:

> Implement `resolve_execution_order()` according to the frozen task contract. Preserve the public API. Modify only `src/dogfood/execution_order.py`. The protected verification file `tests/test_execution_order.py` is read/execute only and must not be changed. Standard library only. Run the authorized oracle and stop when the bounded task reaches a terminal candidate.

Algorithm choice remains the implementation agent's internal engineering decision.

## 9. Hard stops

Stop without widening scope if:

- the target API cannot be implemented inside the one authorized source file;
- a dependency/configuration change appears necessary;
- the protected test file would need modification;
- a file outside the authorized source file would need mutation;
- the oracle cannot be executed with the prequalified Python environment;
- the runtime/provider/model identity differs from the authorized execution subject;
- a network/external side effect beyond the provider transport would be required.

## 10. Success oracle

A Relay terminal `DONE` is eligible only if all of the following hold:

```text
authorized mutation surface respected
protected verification unchanged
exact public API preserved
oracle command exits 0
all 15 protected tests pass
workspace change manifest contains exactly one modified source file
no dependency/configuration changes
no unauthorized network/external effect
runtime evidence is continuous
resource limits are not exceeded
```

Runtime/model self-report alone cannot establish success.

## 11. Git boundary

Local workspace mutation and an optional local commit are permitted only if the later execution authority explicitly permits them.

The dogfood task itself never authorizes:

- push;
- merge;
- pull request creation;
- tag/release;
- canonical promotion;
- remote branch mutation.

## 12. Result boundary

The implementation actor stops at one terminal candidate and evidence package.

It may not independently ACCEPT, promote, create successor authority, or widen the WorkPacket.
