# Slice 1.10 Dogfood B4 — Read-Only Harness Preparation — Implementation Authorization

**Document class:** Immutable Human implementation/preparation authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B4 — Relay Dogfood Acceptance  
**Stage:** Read-only harness preparation  
**Record:** `RLY-S110-DOGFOOD-B4-HARNESS-IMPL-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes preparation and verification of the minimal B4 read-only harness.

This authority does not authorize B4 execution.

## Exact authority basis

```text
B4 design authority:
RLY-S110-DOGFOOD-B4-DESIGN-AUTH-001 — AUTHORIZED

Accepted B4 design candidate:
9b274eda204dac30da51181f2c1de25cf7237010

Independent design evaluation:
RLY-S110-DOGFOOD-B4-DESIGN-EVAL-001 — ACCEPT

Human design acceptance:
RLY-S110-DOGFOOD-B4-DESIGN-ACCEPT-001 — ACCEPTED

Harness preparation baseline:
ede1d79d2464a1420c5779768c0247ece3580d55
```

## Objective

Prepare and prove the smallest possible read-only inspection harness for B4.

The harness exists only to expose existing Relay read models against the accepted operational DB through a genuinely read-only SQLite connection.

## Authorized scope

The harness may:

- open the supplied SQLite path using URI `mode=ro`;
- enable `PRAGMA query_only = ON`;
- construct a caller-owned `RelayDatabase` wrapper around that connection without calling the normal writable `open_database()`;
- invoke existing `project_board` and `slice_detail` services;
- serialize/print their existing models deterministically;
- optionally expose exact registry-resolved canonical artifact metadata needed by the B4 protocol;
- provide a deterministic command or script suitable for later pinning by B4 execution authority;
- use disposable databases/fixtures for tests;
- read the real operational DB only for read-only qualification if necessary.

The harness must not:

- add domain interpretation;
- infer authority;
- create CURRENT/NEXT/LATER/BLOCKED semantics beyond the accepted B4 design;
- write, migrate, checkpoint, vacuum, repair, or otherwise mutate the real operational DB;
- expose mutation routes;
- reuse the normal writable `relay-board` launcher against the live DB;
- implement B4 scoring or self-evaluation;
- execute the B4 cold-start session;
- open Slice 2.2.

## Required verification

At minimum prove:

1. the harness opens SQLite with `mode=ro`;
2. `query_only` is enabled;
3. the accepted real DB can be projected without byte changes;
4. `project_board` output is identical to the existing service semantics;
5. `slice_detail` output is identical to the existing service semantics;
6. no mutation SQL can succeed through the harness connection;
7. no migration/journal-mode mutation occurs;
8. the harness produces deterministic serializable output suitable for B4 evidence;
9. full relevant tests/static checks pass.

## Required handoff

Return:

- starting SHA;
- candidate SHA;
- changed paths;
- exact harness interface/command;
- proof of read-only connection mode;
- tests and results;
- before/after real DB SHA if the real DB is read;
- confirmation no B4 execution occurred;
- confirmation no Slice 2.2 work occurred.

Push the exact candidate and STOP for independent technical review.

Do not self-accept.
