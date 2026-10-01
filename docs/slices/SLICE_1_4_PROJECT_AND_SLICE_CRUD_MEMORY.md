# Slice 1.4 Development Memory — Project and Slice CRUD

**Status:** COMPLETE / ACCEPTED / FINALIZED
**Record state:** LOCKED
**Authority:** `RLY-S14-AUTH-001`
**Closure authority:** `RLY-S14-CLOSE-AUTH-001`
**Accepted design:** Revision 2 — `f5a678da360b96701a1f9635d3703b49dc16e779`
**Accepted technical result:** `ae582c52ec4a6451b54e9d6e018932e93e72e013`
**Independent evaluation:** `RLY-S14-EVAL-002 — ACCEPT`
**Human technical acceptance:** `RLY-S14-ACCEPT-001 — ACCEPTED`

## Objective and boundary

Slice 1.4 implemented human-controlled Project and Slice definition create/read/list/update/guarded-delete, exact definition revisions, append-only history, optimistic concurrency, graph validation, and Human mutation provenance.

The accepted domain `Project` and `Slice` models remain unchanged. No lifecycle, governance, repository, provider, UI, dependency invalidation, Slice 1.5, or agent-execution behavior was added.

## Accepted implementation

- SQLite migration v4 adds definition revisions and append-only Project/Slice definition history.
- Pre-v4 current records are deterministically seeded at revision 1 with migration-only `SEED`.
- Post-v4 runtime CREATE/UPDATE/DELETE flows through `relay_engine.project_slice` with HUMAN actor, aware UTC time, and nonblank reason.
- Public raw Project/Slice insertion bypasses were removed.
- Strict CAS is checked before exact-target no-op behavior; stale exact-target commands conflict.
- Slice parent/dependency references are same-Project and acyclic.
- Lifecycle initialization, handover-gate revisions, and downstream dependencies freeze Slice definition mutation under the accepted contract.
- Graph validation precedes the downstream-dependent guard so malformed proposed cycles produce the contract-specific cycle errors.
- Project repository authority and Slice project ownership remain immutable.
- Guarded physical delete explicitly checks accepted blockers, appends DELETE tombstones, preserves retired identity/history, and fails closed on residual integrity errors.
- Durable definition corruption is detected and never auto-repaired.

## Authority and implementation lineage

```text
Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Design Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Accepted Revision 2 design:
f5a678da360b96701a1f9635d3703b49dc16e779

Implementation authorization:
RLY-S14-AUTH-001

Repaired implementation baseline:
dfe6c20c8f65b42fe69b7d315956a91d2a29487c

Historical first candidate:
e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d

First implementation evaluation:
RLY-S14-EVAL-001 — REWORK

Accepted rework candidate:
ae582c52ec4a6451b54e9d6e018932e93e72e013

Independent implementation evaluation:
RLY-S14-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S14-ACCEPT-001 — ACCEPTED
```

## Accepted evidence

```text
Exact candidate:
ae582c52ec4a6451b54e9d6e018932e93e72e013

GitHub Actions:
36899665799 — SUCCESS

Ruff format:
PASS

Ruff lint:
PASS

Pyright:
PASS — 0 errors / 0 warnings

pytest:
PASS — 525 tests

Project/Slice administration service suite:
PASS — 33 tests

uv build:
PASS

New runtime dependencies:
NONE
```

The bounded rework closed all `RLY-S14-EVAL-001` findings: durable authority provenance, public-path cycle classification, Project/Slice history-corruption fail-closed evidence, two-connection update/delete concurrency, exact authority/design-lineage assertions, and explicit post-v4 Slice `CREATE` versus migration-only `SEED`.

## Finalized boundary

This development memory is locked at Slice 1.4 finalization. Historical candidates, accepted design records, authority records, evaluation records, and the accepted technical SHA remain immutable provenance.

```text
Slice 1.4 technical result:
ACCEPTED

Slice 1.4 finalization:
COMPLETE

Closure evaluation:
PENDING at finalization boundary

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
