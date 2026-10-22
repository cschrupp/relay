# Slice 1.10 Dogfood B4 — Read-Only Harness — Implementation Evaluation 001

**Document class:** Immutable independent implementation evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B4 — Relay Dogfood Acceptance  
**Stage:** Read-only harness preparation  
**Record:** `RLY-S110-DOGFOOD-B4-HARNESS-IMPL-EVAL-001`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Authority:
RLY-S110-DOGFOOD-B4-HARNESS-IMPL-AUTH-001 — AUTHORIZED

Starting SHA:
03f327a342be585bb423c6aee1729de8836b8e49

Candidate SHA:
36a53179c9951375450a94c0283e68a9428143fb

Branch:
implementation/1.10-dogfood-b4-readonly-harness

Changed paths:
scripts/b4_readonly_harness.py
tests/integration/test_b4_readonly_harness.py

Exact-head CI:
PASS
```

## Independent findings

No blocking discrepancy was found.

### Scope

The candidate is exactly two new non-production paths:

- one B4 inspection harness under `scripts/`;
- one focused integration-test module.

There are no changes under `src/relay_engine`.

The harness does not implement B4 scoring, CURRENT/NEXT/LATER/BLOCKED interpretation,
authority inference, lifecycle transition, Slice creation, or Role Contracts.

### Read-only connection boundary

The harness does not call Relay's normal writable `open_database()`.

It:

1. resolves the supplied database path;
2. constructs a SQLite file URI with `mode=ro`;
3. opens with `uri=True` and `isolation_level=None`;
4. enables foreign-key enforcement;
5. enables `PRAGMA query_only = ON`;
6. verifies `query_only == 1`;
7. runs the existing read-only `verify_schema()`;
8. wraps the caller-owned connection in `RelayDatabase`;
9. invokes only existing `project_board` and `slice_detail` projections.

`verify_schema()` performs SELECT-only schema/checksum/table/index/trigger validation and does
not apply migrations or write schema state.

The negative test is stronger than merely checking `query_only`: it explicitly turns
`query_only` back OFF on the same connection and confirms an UPDATE still fails as read-only.
Therefore the underlying SQLite `mode=ro` connection is itself enforcing the primary mutation
boundary.

### Semantic neutrality

The emitted Relay semantic objects are direct JSON-mode serializations of the existing:

- `project_board(...)`;
- `slice_detail(...)`.

The harness adds only inspection-envelope facts:

- database path;
- Project ID;
- Slice ID;
- query-only state;
- applied Relay schema version.

It adds no domain interpretation or governance decision.

Focused equivalence testing proves the board/detail values match calls through the existing
services against the same disposable state.

### Determinism and error behavior

The CLI uses sorted compact JSON serialization and repeated invocation is asserted byte-equal.

A missing database fails without creating a file.

Unknown Project/Slice identities preserve the existing Relay service errors rather than
inventing fallback semantics.

### Verification

Reported and accepted verification:

```text
Focused tests:
6 passed

Board/read-model regressions:
10 passed

Full pytest:
880 passed

Ruff:
format check PASS
lint PASS

Pyright:
0 errors / 0 warnings / 0 informations

uv build:
PASS

git diff --check:
PASS

Exact-head CI:
PASS
```

### Live operational DB qualification

The bounded live read remained non-consequential:

```text
DB SHA before:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

DB SHA after:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

query_only:
1

schema version:
8

sidecars before and after:
-shm = 32768 bytes
-wal = 0 bytes
unchanged / untouched
```

The unchanged DB digest establishes that the real operational database was not modified by the
qualification read.

The unchanged pre-existing sidecars are observational only and correctly were not checkpointed,
deleted, normalized, or treated as B4 failure criteria.

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-HARNESS-IMPL-EVAL-001 — ACCEPT

B4 read-only harness:
IMPLEMENTED / INDEPENDENTLY ACCEPTED
HUMAN TECHNICAL ACCEPTANCE PENDING

B4 execution:
NOT AUTHORIZED

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED
```

The candidate is suitable to become the pinned inspection mechanism for a later B4 execution
authority after explicit Human technical acceptance.

This evaluation does not authorize the B4 dogfood run, Axis B replay, any write to the live
operational DB, lifecycle mutation, Slice 2.2 design/implementation, Phase 3, or promotion.
