# Slice 1.6 — Implementation Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Authority decision date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Record:** `RLY-S16-AUTH-001`

## Accepted design authority

```text
Design authorization:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
f3a0fa7d9cc5b344399c070406353e1107ec30ff

Revision 2 Amendment:
9a114b81f4347df10db7dfcb75677a606f18262e

Revision 3 Amendment / exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent combined design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S16-DESIGN-ACCEPT-001 — ACCEPTED

Human design acceptance record:
0d23067c96eb9f3cec0ea3a3fa21b2fa605e4de1
```

The implementation baseline is the canonical repository state immediately after Human design acceptance:

```text
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3
```

## Human Authority decision

```text
RLY-S16-AUTH-001
Slice 1.6 implementation
AUTHORIZED
```

Implementation is authorized only against the accepted combined Slice 1.6 design ending at:

```text
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb
```

Revision 3 is normative wherever it replaces or qualifies Revision 2. Revision 2 is normative wherever it replaces or qualifies Revision 1.

## Preferred implementation role / model

```text
Role:
IMPLEMENTATION_AGENT

Preferred model:
GPT-5.6 Luna
```

If the executing model differs, the implementation result must record both the preferred and executing model provenance and the deviation.

The implementation agent must not redesign the accepted architecture merely because another design seems cleaner or more extensible. Any ambiguity that materially affects Human Authority semantics, governance revision causality, stale-basis handling, persistence atomicity, lifecycle/gate execution, security boundaries, or change surface is a stop condition and must be escalated.

## Authorized objective

Implement the minimum safe product seam for explicit Human Authority over already-governed Relay state.

The implementation must expose durable Human Authority actions through the existing local server-rendered board while preserving the accepted principle:

```text
human durable decision / permission
        !=
governed lifecycle execution
```

and the accepted handover path:

```text
requested lifecycle movement
        -> exact HandoverGate
        -> deterministic evaluation
        -> selected + GREEN
        -> accepted lifecycle engine
```

## Authorized product actions

Slice 1.6 may implement only the accepted action set:

```text
AUTHORIZE
APPROVE
REJECT
CHOOSE_PATH
BLOCK
PAUSE
DEFER
CLEAR_HOLD / RESUME
ADVANCE
CANCEL
```

`ADVANCE` and `CANCEL` are governed execution actions, not direct lifecycle bypasses. Transition to `ACCEPTED` remains reserved for Slice 1.7.

## Architectural constraints

1. Reuse existing `AuthorizationGrant`, `HumanApprovalDecision`, `HumanChoiceDecision`, `HandoverGate`, `HandoverContext`, gate evaluation, lifecycle, blockage, and execution semantics.
2. Do not create a second approval/authorization domain model or UI-owned authority state.
3. Human gate-affecting actions must bind to the exact latest durable Human Action Basis and fail closed on stale/conflicting state.
4. New authorization changes advance `governance_revision` exactly once and atomically append a successor `GateEvaluationRecord`.
5. New APPROVE/REJECT/CHOOSE_PATH decisions keep the same governance revision and atomically append a successor `GateEvaluationRecord`.
6. The board continues to display durable stored gate observations, not unrecorded live truth.
7. Cancellation must execute through an exact current GREEN cancellation gate; direct `transition_phase(..., CANCELLED)` from product code is not authorized.
8. `BLOCK`, `PAUSE`, and `DEFER` reuse existing orthogonal `Blockage`; no new PAUSED/DEFERRED lifecycle phases are authorized.
9. `CLEAR_HOLD` removes only Slice-1.6 Human-control blockers and preserves unrelated blockers.
10. Request-scoped SQLite ownership from Slice 1.5 must remain intact.
11. Mutation routes require anti-CSRF protection and server-bound HUMAN actor identity.
12. No schema migration and no new runtime dependency are authorized.

## Expected production change surface

### New package

```text
src/relay_engine/human_control/
    __init__.py
    errors.py
    models.py
    service.py
```

### Bounded existing-file changes

```text
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
```

A tiny persistence record/export adjustment is permitted only when mechanically required by the accepted transaction contract.

### Expected tests

```text
tests/unit/test_human_control_models.py
tests/unit/test_human_control_service.py
tests/integration/test_human_control_sqlite.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_web.py
```

Exact test filenames may follow repository conventions. Additional narrowly scoped tests are permitted when necessary to prove an accepted invariant; a new generalized test framework is not authorized.

## Dependency and schema boundary

```text
new runtime dependencies: NONE
new schema migration: NONE
```

Existing FastAPI/Uvicorn/httpx declarations from Slice 1.5 may be reused. Any proposal for another direct runtime or dev/test dependency is a stop condition and requires Human Authority escalation.

## Explicitly out of scope

This authorization does **not** authorize:

- Slice 1.7 manual evaluation, technical acceptance, or accepted-baseline promotion;
- transition to `LifecyclePhase.ACCEPTED` through Slice 1.6 controls;
- opening Slice 1.7;
- agent execution;
- AgentRuntime/OpenCode execution or integration;
- repository/provider mutation;
- autonomous approval or substitution for Human Authority;
- a generic workflow engine, command bus, event bus, plugin architecture, ORM, or new frontend framework;
- React/TypeScript/Node/Vite;
- final JSON/OpenAPI product API work;
- multi-user authentication, organizations, or broad RBAC;
- async persistence redesign, connection pooling, background workers, websocket/SSE/polling systems;
- unrelated refactors or toolchain changes.

## Required quality evidence

Before handing off a candidate, Luna must run and report:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

GitHub Actions CI must succeed on the exact candidate SHA before independent implementation evaluation.

Passing checks are evidence only and do not constitute acceptance.

## Stop / escalation conditions

Luna must stop and escalate rather than silently widen the slice if implementation requires:

- schema migration;
- accepted lifecycle/governance/domain semantic changes;
- a new authority semantic or revocation/expiry model;
- a materially broader production change surface;
- another direct dependency;
- connection sharing, `check_same_thread=False`, or pooling;
- async persistence redesign;
- Slice 1.7 functionality;
- repository/provider mutation;
- agent execution;
- contradiction among the accepted design revisions and existing accepted code.

## Handoff boundary

The implementation result is only a candidate. Luna may not:

- independently accept its own implementation;
- promote it as technically accepted;
- authorize finalization/closure;
- close Slice 1.6;
- open Slice 1.7;
- authorize agent execution.

The candidate must return to an independent implementation evaluator.

**Unblocked ≠ accepted.**
