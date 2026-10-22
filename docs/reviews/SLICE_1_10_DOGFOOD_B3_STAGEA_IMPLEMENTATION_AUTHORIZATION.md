# Slice 1.10 Dogfood B3 — Stage A Materialization Tooling / Preparation — Implementation Authorization

**Document class:** Immutable Human implementation/preparation authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Stage:** A — materialization tooling / preparation  
**Record:** `RLY-S110-DOGFOOD-B3-STAGEA-IMPL-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes Stage A tooling/preparation for B3.

This authority permits only reversible implementation/refactoring and deterministic verification on disposable databases. It does not authorize any write to the live Relay operational database and does not authorize B3 materialization.

## Exact authority basis

```text
B3 design authority:
RLY-S110-DOGFOOD-B3-DESIGN-AUTH-001 — AUTHORIZED

Accepted B3 design candidate:
b032b0f28e1b476097b99b375be647cfe5ada64d

Independent design evaluation:
RLY-S110-DOGFOOD-B3-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S110-DOGFOOD-B3-DESIGN-ACCEPT-001 — ACCEPTED

Accepted-design governance tip / Stage A implementation baseline:
f337e08c5f96fd23225f047468abfbf2ed71d60a

Stage A branch:
implementation/1.10-dogfood-b3-stage-a-materialization-tooling
```

## Stage A objective

Prepare and prove the minimum reusable internal tooling required so a later, separately authorized Stage B can perform one atomic B3 materialization transaction safely.

The prepared tooling must support, within one caller-owned SQLite transaction:

1. exact Slice definition update using the accepted Project/Slice administration rules;
2. lifecycle initialization at revision zero / `PROPOSED`;
3. same-transaction readback of the existing Project board / situation projection;
4. one bounded orchestration path proving all-or-nothing behavior.

Stage A is successful when those capabilities are deterministically tested on disposable databases and independently reviewable without touching the live Relay operational state.

## Authorized implementation scope

### A1 — caller-owned Slice update primitive

Factor the existing accepted `relay_engine.project_slice.update_slice` implementation so the same validation and persistence logic can execute on a caller-owned SQLite connection.

Requirements:

- retain the existing public transaction-owning `update_slice` behavior;
- reuse one implementation path rather than duplicate validation;
- preserve exact revision-concurrency checks;
- preserve immutable Project ownership;
- preserve definition-freeze behavior once lifecycle or handover history exists;
- preserve graph validation and downstream-dependent checks;
- preserve immutable definition revision history and Human mutation provenance;
- preserve existing origin semantics.

A connection-owned helper may be added/exported internally as needed.

### A2 — caller-owned lifecycle initialization primitive

Factor the existing accepted `persist_lifecycle_initialization` behavior so lifecycle revision-zero initialization can be persisted inside a caller-owned SQLite transaction.

Requirements:

- retain the existing public transaction-owning wrapper and behavior;
- preserve absence/partial-history checks;
- preserve revision-zero requirements;
- preserve replay equivalence between `LifecycleInitialized` and resulting `SliceLifecycle`;
- preserve event/current-row atomic consistency;
- no new lifecycle semantics.

### A3 — caller-owned board projection

Factor/reuse the existing `project_board` projection so the exact same projection logic may be invoked against the caller-owned transaction snapshot.

Requirements:

- retain existing public `project_board` behavior;
- no second board/read-model implementation;
- no B3-specific CURRENT/NEXT/LATER/BLOCKED model;
- preserve existing “not determinable” behavior where evidence is absent.

### A4 — bounded Stage A coordinator

Implement the minimum internal one-shot orchestration seam needed to prove the accepted B3 transaction shape on disposable databases.

It must be capable of composing:

```text
validate exact pre-state
  -> exact Slice UPDATE
  -> initialize lifecycle at PROPOSED
  -> same-transaction readback / validation
  -> COMMIT
```

and fail atomically:

```text
any validation / concurrency / integrity / readback failure
  -> ROLLBACK
  -> no partial Slice/lifecycle state
```

The coordinator may use an internal typed plan/input object if useful, but it must not introduce a new authority model, lifecycle model, backlog model, or alternate persistence engine.

Stage A does not need to freeze the Stage B launcher UX. Stage B will separately pin the exact accepted tooling SHA, real DB identity, Project/Slice IDs, revision/origin/lifecycle pre-state, target payload, Human actor, and permitted attempt.

## Frozen target used by Stage A tests

Stage A tests must exercise the exact B3 target shape frozen by the accepted design:

```text
ProjectId:
prj_018f47c1-7b2c-7abc-8def-123456789001

SliceId:
slc_01a15754-1123-7535-9ded-6a564518e347

title:
Slice 2.2 — Role Contracts

parent_slice_id:
null

dependency_ids:
[]
```

The exact ordered `scope.in_scope`, `scope.out_of_scope`, and A01–A11 acceptance criteria are those in accepted design candidate `b032b0f28e1b476097b99b375be647cfe5ada64d`.

Tests may construct equivalent disposable fixtures with test-only IDs where necessary to exercise generic primitives, but at least one deterministic test must validate the exact frozen target payload against the accepted `Slice` model.

## Required verification

At minimum add deterministic coverage for:

1. connection-owned Slice update produces the same result/history semantics as the existing public wrapper;
2. existing public Slice update regression behavior remains unchanged;
3. connection-owned lifecycle initialization produces the same event/current-state semantics as the existing public wrapper;
4. existing public lifecycle initialization regression behavior remains unchanged;
5. caller-owned board projection equals the existing public projection for the same durable state;
6. successful coordinator transaction:
   - updates exactly one Slice definition revision;
   - preserves Project/Slice identity and established origin;
   - initializes exactly one lifecycle event/current row at `PROPOSED`;
   - produces expected board/readback state;
7. injected failure after definition update but before lifecycle persistence rolls back the definition update;
8. injected failure after lifecycle persistence but before commit/readback completion rolls back both definition and lifecycle writes;
9. stale definition revision fails closed;
10. pre-existing lifecycle or handover history fails closed before mutation;
11. payload mismatch / alternate target fails closed where enforced by the coordinator contract;
12. unrelated Project/Slice/adoption/Baseline/origin data remain unchanged;
13. full existing repository tests and static checks remain green.

## Permitted code surface

Changes may touch only the minimum files required within these existing subsystems and their tests:

- `src/relay_engine/project_slice/`
- `src/relay_engine/persistence/`
- `src/relay_engine/board/`
- one minimal internal B3 materialization/coordinator module under `src/relay_engine/`;
- corresponding tests;
- directly necessary package exports;
- directly necessary Stage A implementation/handoff documentation.

Do not add a general public CLI for B3.

Do not add a database migration unless a concrete implementation blocker is discovered. If a schema migration appears necessary, STOP and escalate rather than adding it under this authority.

## Hard prohibition — live Relay operational DB

Stage A MUST NOT write to, migrate, vacuum, checkpoint, repair, or otherwise mutate:

`/home/user/projects/relay-local-state/relay-operational.sqlite3`

Stage A verification must use temporary/disposable databases only.

Read-only inspection of the live database is permitted only when required to verify an already-known precondition or compare structure; it must not be used as a test fixture and must not alter any bytes, WAL/SHM state, or connection pragmas that produce persistent changes.

The accepted B2/B3 durable evidence files must also remain unchanged.

## Explicitly not authorized

This authority does not permit:

- Stage B execution;
- real B3 materialization;
- updating the real adoption-frontier Slice definition;
- initializing lifecycle in the real operational DB;
- creation of another first-work Slice;
- B4 execution;
- Slice 2.2 design opening;
- implementation of Role Contracts;
- implementation of runtime `PROPOSED_WORK` or `BACKLOG_EXHAUSTED` semantics beyond what is strictly necessary to represent/test the frozen B3 target;
- Work Packet or Workspace Authority implementation;
- OpenCode/AgentRuntime project execution;
- Phase 3;
- main/canonical promotion;
- authority/governance redesign;
- unrelated refactoring.

## Required handoff

Return:

- starting SHA;
- candidate SHA;
- changed paths;
- exact connection-owned primitives introduced/refactored;
- coordinator interface and transaction boundary;
- disposable-database tests added;
- focused test results;
- full-suite test result;
- Ruff / Pyright / repository-contract results;
- proof the exact frozen B3 target payload validates;
- proof rollback works at the required injected failure points;
- confirmation the live operational DB was not modified;
- confirmation no Stage B/B4/Slice 2.2 work occurred.

Push the exact candidate and STOP for independent technical review.

Do not self-accept.
Do not run Stage B.
