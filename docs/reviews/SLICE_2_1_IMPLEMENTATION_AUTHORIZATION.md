# Relay — Slice 2.1 Agent Runtime Contract — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-S21-IMPL-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority explicitly authorizes implementation of:

```text
Slice 2.1 — Agent Runtime Contract
IMPLEMENTATION AUTHORIZED
```

and requests a detailed Codex implementation scope.

## Exact implementation basis

```text
Repository:
cschrupp/relay

Authorized implementation baseline:
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22

Slice opening:
RLY-S21-OPEN-001

Design authorization:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

Exact accepted combined design head:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Independent exact-head design evaluation:
RLY-S21-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED
```

Implementation MUST start from the exact authorized baseline above.

## Authorized production surface

Expected new package:

```text
src/relay_engine/agent_runtime/
    __init__.py
    errors.py
    models.py
    protocol.py
    opencode.py
```

A single small private helper module under `agent_runtime/` is permitted only if required to keep the OpenCode event pump / transport implementation clear.

Expected bounded existing-file changes:

```text
pyproject.toml
uv.lock
```

`src/relay_engine/domain/ids.py` may change only if a mechanically necessary import/export/type alias adjustment is required. A new Relay execution ID is NOT authorized; existing `ExecutionId` must be reused.

No other production package is authorized by default.

## Explicit dependency authority

The accepted design contemplated one dependency change. This implementation authority explicitly permits:

```text
httpx>=0.28,<1
```

to move from the dev-only dependency group into `[project].dependencies`.

The implementation should remove the duplicate dev-only declaration if the runtime dependency already satisfies tests.

Corresponding `uv.lock` metadata change is authorized.

No other runtime or development dependency is authorized.

Node, Bun, OpenCode SDK packages, and OpenCode installation are NOT authorized.

## Authorized behavior

Implement the accepted Relay-owned runtime-neutral contracts and one `OpenCodeRuntime` HTTP adapter that can be exercised entirely with deterministic mocked HTTP/event transports.

The implementation must include:

- exact `ExecutionId` reuse;
- runtime/session/invocation opaque references;
- runtime descriptor and required/optional capability model;
- strict runtime/API-version compatibility behavior;
- immutable `RuntimeExecutionBasis` and `RuntimeExecutionRequest`;
- deterministic v1 request digest;
- exact `RuntimeSessionBinding`;
- exact request/binding conflict checks;
- runtime selection / requested-vs-actual provenance;
- external credential references only;
- runtime permission-profile reference only;
- workspace attachment supplied by Relay;
- `AgentRuntime` protocol with `describe`, `create_session`, `open_execution`, `events`, `cancel`, and `inspect`;
- optional capability protocols only where accepted;
- bounded pre-admission event pump for live-only OpenCode events;
- exact session/location event attribution;
- explicit event continuity and `EVENT_GAP`;
- bounded queue overflow semantics;
- idempotent cancellation;
- process-lifetime binding/retry semantics;
- fail-closed `SESSION_BINDING_REQUIRED` restart boundary;
- runtime inspection distinct from engineering-result verification;
- normalized safe failure categories;
- non-interactive first OpenCode permission profile;
- no mutable provider/model/agent switching after request-basis lock.

## Live-runtime boundary

This implementation authorization does NOT authorize:

- installing OpenCode;
- launching an OpenCode server;
- connecting to a live OpenCode server;
- provider/model calls;
- using user credentials;
- executing a coding agent against Relay or another repository;
- the designed live sidecar experiment.

All OpenCode adapter tests in this implementation must use deterministic mocks/fakes/local in-process test transport only.

## No-governance-mutation boundary

Slice 2.1 implementation must not modify:

```text
src/relay_engine/governance/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/persistence/**
src/relay_engine/repository_baseline/**
src/relay_engine/repository_contract/**
src/relay_engine/repository_sync/**
src/relay_engine/board/**
```

unless the Human Authority separately expands scope after a stop/escalation.

No schema migration is authorized.

No lifecycle/governance semantics change is authorized.

No runtime event may call governance/lifecycle mutation services.

## Testing authority

Add deterministic tests expected under:

```text
tests/unit/test_agent_runtime_models.py
tests/unit/test_agent_runtime_contract.py
tests/unit/test_opencode_runtime.py
```

Additional narrowly named unit-test modules under `tests/unit/` are permitted only if required for clarity.

No integration test may contact a live runtime/provider.

## Quality contract

The candidate must pass:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

and GitHub Actions CI on the exact candidate SHA.

## Stop conditions

STOP and report before continuing if implementation requires:

- new lifecycle/governance/Human Authority semantics;
- any persistence/schema change;
- runtime-session durable storage;
- a new dependency other than the authorized `httpx` promotion;
- Node/Bun;
- OpenCode SDK types crossing the adapter boundary;
- live OpenCode/provider access;
- automatic OpenCode install/launch/discovery;
- runtime-created authority-expanding workspace;
- interactive steering;
- Human runtime-permission reply UI;
- role-contract/work-packet/workspace/orchestration implementation;
- Phase 3 capability;
- unrelated Phase 1 hardening.

## Authority boundary

This record authorizes implementation candidate production only.

It does not authorize:

- independent evaluation of the candidate by its implementer;
- Human technical acceptance;
- live sidecar execution;
- accepted-result promotion;
- Slice 2.1 closure;
- Slice 2.2+ work;
- Phase 3;
- Relay agent execution.

**Implementation authorized ≠ runtime execution authorized.**
