# Slice 1.10 Dogfood B3 — Stage B Real Materialization — Execution Evaluation 001

**Document class:** Immutable independent execution evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Stage:** B — real operational materialization  
**Record:** `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-EVAL-001`  
**Outcome:** `FAIL_CLOSED / NO MATERIALIZATION`

## Evaluated subject

```text
Stage B authority:
RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-001 — AUTHORIZED

Accepted execution tooling SHA:
042a4a54df7eecadfefa30f1e5c487da52c38b61

Operational DB:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Authorized pre-state DB SHA-256:
54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9

Failure evidence:
/home/user/projects/relay-local-state/adoption-evidence/b3-stageb-materialization-evidence.json

Reported failure-evidence SHA-256:
e8758f045756a834d7f6e6fb37641b52d6c6069e9f7bd89c3c351bcaefa28aa9
```

## Preflight evaluation

The reported preflight passed before any writable materialization attempt.

It matched the authority pins for:

- exact clean execution SHA;
- exact operational DB SHA-256;
- exact B2 terminal-evidence SHA-256;
- accepted migration-8 schema state;
- Project / Repository / Baseline / Adoption / Slice / epoch identities;
- exact adoption-frontier Slice revision and payload;
- established Project PRE_GENESIS and Slice NATIVE_RELAY origin proofs;
- empty lifecycle current/history;
- empty handover history;
- exact frozen B3 target.

No state mismatch or stale-governance condition is reported.

## Consequential attempt

The accepted coordinator `materialize_b3(database, plan)` was invoked exactly once.

The attempt failed on the first durable Slice definition-history write with SQLite:

```text
attempt to write a readonly database
```

Relay surfaced the failure as `DatabaseUnavailable`.

The operator did not retry.

Therefore the one consequential attempt authorized by
`RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-001` is consumed.

## Atomicity and post-failure state

The transaction failed closed.

Reported post-failure evidence establishes:

```text
before DB SHA:
54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9

after DB SHA:
54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9

table snapshots:
MATCH

integrity_check:
ok

foreign-key errors:
0

SQLite sidecars:
absent

Slice definition revision:
1

lifecycle:
absent
```

No B4 state, Slice 2.2 implementation state, execution, evaluation, promotion,
or other downstream state was created.

This is the exact fail-closed behavior required by Stage A and Stage B.

## Technical classification

No evidence identifies a Stage A atomicity, target-payload, lifecycle, origin,
or transaction-boundary defect.

The failure occurred because the execution environment exposed the authorized
operational database as non-writable to SQLite at the first real durable write.

The accepted tooling correctly rolled the transaction back and preserved the
entire pre-state.

## F001 — execution-venue writability was not qualified before consuming the one-shot attempt

**Severity:** PROCESS / EXECUTION-PREFLIGHT DEFECT  
**Effect on durable state:** NONE

The Stage B preflight proved that the target state was correct and unchanged,
but did not prove that the execution environment could perform SQLite writes
against the exact target path.

That omission did not weaken fail-closed safety, but it allowed an
environmental permission/mount condition to consume the single consequential
attempt before any semantic work could occur.

Before another Stage B authority is issued, the execution venue must be
qualified independently for SQLite write capability without modifying the
operational database's semantic contents.

The qualification should establish, at minimum:

- the database file is writable by the executing user/process;
- the containing directory permits SQLite journal/WAL/locking behavior required
  by the accepted tooling;
- the filesystem/mount is not read-only;
- a disposable SQLite database created in the same containing directory can
  successfully execute the same `BEGIN IMMEDIATE` / INSERT / ROLLBACK or
  COMMIT mechanics used by Relay;
- the real operational DB remains byte-identical throughout qualification;
- no persistent sidecar is left next to the real DB.

A future Stage B re-attempt authority must pin the successful environment-
qualification evidence in addition to all original state/tooling pins.

## Independent disposition

```text
RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-EVAL-001
FAIL_CLOSED / NO MATERIALIZATION

Stage B attempt 001:
CONSUMED

Durable Relay state:
UNCHANGED

Stage A tooling:
NO REWORK REQUIRED

B3 materialization:
NOT COMPLETE

Second Stage B attempt:
NOT AUTHORIZED

B4:
NOT OPEN / NOT AUTHORIZED

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED
```

The next eligible work is execution-environment qualification followed by a
new, separately authorized Stage B materialization attempt if and only if that
qualification passes.
