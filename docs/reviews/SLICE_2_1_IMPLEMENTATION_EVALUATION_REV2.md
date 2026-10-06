# Slice 2.1 — Independent Implementation Evaluation, Revision 2

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-EVAL-002`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22

Prior implementation candidate:
c947cf607699707b8b56d22cbb9aab4b30a7bf4a

Prior evaluation:
RLY-S21-EVAL-001 — REWORK

Successor candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Implementation branch:
implementation/2.1-agent-runtime-contract
```

The successor is exactly one commit ahead of the preserved REWORK candidate and remains within the authorized cumulative implementation surface.

Exact-SHA CI:

```text
GitHub Actions:
37418144665 — SUCCESS

head:
ded3ed03b7070ea095a823129ebe44935cb57997

full pytest:
646 passed

ruff format:
PASS

ruff lint:
PASS

pyright:
PASS — 0 errors / 0 warnings

build:
PASS
```

The reported `git diff --check` result is PASS. No live OpenCode, provider, model, credential, or real agent execution occurred.

# Prior findings

## F001 — RESOLVED — cancellation exact-binding enforcement

Cancellation now requires an exact process-local `ExecutionId -> RuntimeSessionBinding` before any interrupt request.

```text
missing binding -> SESSION_BINDING_REQUIRED
different session -> REQUEST_CONFLICT
exact binding -> cancellation may proceed
```

Tests prove that unknown executions, mismatched sessions, and bindings known only to another runtime instance emit no interrupt request.

## F002 — RESOLVED — inspection exact-binding enforcement

Inspection now proves the exact process-local request/session identity before remote session access.

It validates:

```text
ExecutionId
RuntimeSessionRef
request digest
known request provenance
```

against the process-local binding before any session GET.

Unknown binding fails `SESSION_BINDING_REQUIRED`; mismatched session/digest fails `REQUEST_CONFLICT`. Tests prove zero remote inspection request on these failures.

## F003 — RESOLVED — uncertain prompt-admission recovery

Prompt-admission timeout/transport uncertainty now preserves:

```text
exact RuntimeSessionBinding
exact provisional RuntimeExecutionHandle
active event observer
one-prompt guard
```

and returns the exact handle so the caller can inspect or cancel the existing session without guessing or sending a second prompt.

Definite 400/403 admission rejection closes/removes the observer and preserves normalized failure classification.

Tests prove:

- timeout uncertainty is inspectable/cancellable;
- transport uncertainty is inspectable/cancellable;
- a second prompt is refused;
- a mismatched session cannot be inspected/cancelled;
- definite rejection leaves no orphan active observer.

This remains within the accepted `AgentRuntime` method signatures and adds no persistence or authority semantics.

# Additional accepted correction

Safe bounded `raw_event_type` provenance is retained when it matches the adapter's accepted event-type pattern. This improves auditability without exposing arbitrary event payload material.

# Regression and scope review

The cumulative baseline-to-successor diff remains limited to:

```text
pyproject.toml
uv.lock
src/relay_engine/agent_runtime/**
tests/unit/test_agent_runtime_contract.py
tests/unit/test_agent_runtime_models.py
tests/unit/test_opencode_runtime.py
tests/unit/test_board_web.py
```

The Board test change remains only the mechanically necessary exact dependency-ownership assertion for the authorized `httpx` dev-to-runtime promotion.

No schema migration, governance mutation, lifecycle mutation, board production behavior, Node/Bun/OpenCode SDK dependency, persistence layer, runtime installer, provider call, or agent execution was introduced.

# Evaluation outcome

```text
RLY-S21-EVAL-002 — ACCEPT
```

Candidate:

```text
ded3ed03b7070ea095a823129ebe44935cb57997
```

is deterministically implementation-acceptable under `RLY-S21-IMPL-AUTH-001`.

However, the accepted Slice 2.1 design explicitly requires separately authorized **live OpenCode sidecar evidence** before Human technical acceptance of the live adapter.

Therefore:

```text
Deterministic implementation evaluation:
ACCEPT

Human technical acceptance:
PENDING / NOT YET ELIGIBLE

Reason:
LIVE OPENCODE SIDECAR EVIDENCE NOT YET AUTHORIZED OR COMPLETED
```

This evaluation does not authorize the live sidecar, provider/model calls, Human technical acceptance, merge/promotion, Slice 2.1 closure, Slice 2.2 work, Phase 3 work, or Relay agent execution.
