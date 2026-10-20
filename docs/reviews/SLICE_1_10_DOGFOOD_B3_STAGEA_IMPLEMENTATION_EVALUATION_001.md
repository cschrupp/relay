# Slice 1.10 Dogfood B3 — Stage A Materialization Tooling — Independent Technical Evaluation 001

**Document class:** Immutable independent technical evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Stage:** A — materialization tooling / preparation  
**Record:** `RLY-S110-DOGFOOD-B3-STAGEA-IMPL-EVAL-001`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Stage A authority:
RLY-S110-DOGFOOD-B3-STAGEA-IMPL-AUTH-001 — AUTHORIZED

Starting SHA:
348c6c29a0acc3881848f5d178a680fcda18e43b

Candidate SHA:
042a4a54df7eecadfefa30f1e5c487da52c38b61

Branch:
implementation/1.10-dogfood-b3-stage-a-materialization-tooling

Candidate CI:
PASS
```

## Scope evaluation

The candidate remains within the authorized Stage A preparation envelope.

Changed production surfaces are limited to:

- `relay_engine.project_slice`;
- `relay_engine.persistence`;
- `relay_engine.board`;
- one internal `relay_engine.b3_materialization` coordinator module;
- corresponding integration tests.

No database migration, public B3 CLI, Role Contract implementation, Stage B execution path, B4 work, Slice 2.2 implementation, Phase 3 work, or unrelated refactor is introduced.

## Connection-owned primitive evaluation

### Slice definition update

The existing public `update_slice` wrapper now delegates to
`update_slice_from_connection`.

The factored connection-owned primitive preserves:

- caller-owned active-transaction requirement;
- exact definition-revision concurrency;
- immutable Project ownership;
- lifecycle/handover freeze behavior;
- graph validation;
- downstream dependency protection;
- immutable definition-revision append semantics;
- Human mutation provenance;
- existing error translation for SQLite integrity failures.

No duplicate Slice mutation engine is introduced.

### Lifecycle initialization

The existing public `persist_lifecycle_initialization` wrapper now delegates to
`persist_lifecycle_initialization_from_connection`.

The connection-owned primitive preserves:

- active-transaction requirement;
- absent/partial-history checks;
- revision-zero requirement;
- replay proof;
- event/snapshot identity consistency;
- atomic event/current-state persistence semantics.

No new lifecycle semantics are introduced.

### Board projection

The public `project_board` wrapper delegates to
`project_board_from_connection`.

The connection-owned projection requires the supplied connection to be the
database connection and to be inside an active transaction. It reuses the
existing Project/Slice/origin/lifecycle/gate/evaluation projection logic and
does not introduce a second B3-specific board model.

The test suite proves equality between public and connection-owned projection
for the same durable state.

## Coordinator evaluation

The internal `materialize_b3(database, plan, failure_hook=None)` operation owns
exactly one `write_transaction`.

It enforces:

- exact frozen B3 target payload;
- exact frozen Project/Slice identity;
- Human actor requirement;
- exact adoption-frontier pre-state;
- exact definition revision pin;
- absence of lifecycle state/history;
- absence of handover history;
- established Project and NATIVE_RELAY Slice origins;
- unchanged adoption record;
- unchanged Project/Slice identity inventory;
- post-write exact target readback;
- revision-zero `PROPOSED` lifecycle readback;
- unchanged operational origins;
- same-transaction board/readback validation.

This is appropriately a Stage A internal proof seam, not the final Stage B
authority launcher. Stage B remains responsible for separately pinning the
accepted tooling SHA, live DB identity/pre-state, exact authority identity,
Human ActorRef, and one permitted consequential attempt.

## Atomicity / rollback

The candidate proves both required injected failure boundaries on disposable
databases:

```text
after_slice_update
    -> rollback
    -> original Slice definition restored
    -> no lifecycle rows/events

after_lifecycle_initialization
    -> rollback
    -> original Slice definition restored
    -> no lifecycle rows/events
```

The successful path produces:

- exactly one additional Slice definition revision;
- unchanged Project/Slice identity;
- preserved origin state;
- exactly one lifecycle initialization event;
- one lifecycle current row;
- lifecycle phase `PROPOSED`;
- lifecycle revision `0`;
- matching board projection;
- unchanged unrelated records.

## Frozen target verification

The integration test extracts the exact JSON target from the Human-accepted B3
design and asserts:

`B3_TARGET_SLICE.model_dump(mode="json") == accepted_payload`

It also verifies ordered A01–A11 and `required: true` for all acceptance
criteria.

This is stronger than a hand-maintained approximate payload comparison and
prevents Stage A drift from the accepted design.

## Verification evidence

Reported local verification:

```text
Focused Stage A tests: 13 passed
Full suite: 874 passed
Ruff format: PASS
Ruff lint: PASS
Pyright: 0 errors
uv build: PASS
git diff --check: PASS
repository-contract tests: PASS within full suite
```

Exact-head GitHub Actions run `39486382670` for candidate
`042a4a54df7eecadfefa30f1e5c487da52c38b61` completed successfully.
Its quality job passed Ruff format, Ruff lint, Pyright, tests, and build.

## Live operational database boundary

The reported live operational database SHA-256 before and after Stage A
verification is identical:

`54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9`

No evidence indicates a Stage B transaction, real lifecycle initialization,
B4 work, or Slice 2.2 implementation occurred.

## Independent disposition

No blocking discrepancy was found against
`RLY-S110-DOGFOOD-B3-STAGEA-IMPL-AUTH-001`.

```text
RLY-S110-DOGFOOD-B3-STAGEA-IMPL-EVAL-001 — ACCEPT
```

Stage A tooling candidate
`042a4a54df7eecadfefa30f1e5c487da52c38b61`
is technically eligible for explicit Human acceptance.

This ACCEPT does not authorize:

- Stage B materialization;
- any write to the live Relay operational database;
- real adoption-frontier Slice mutation;
- real lifecycle initialization;
- B4 execution;
- Slice 2.2 design opening or implementation;
- OpenCode/AgentRuntime project execution;
- Phase 3;
- promotion.
