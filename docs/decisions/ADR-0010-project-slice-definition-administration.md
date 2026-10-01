# ADR-0010 — Audited Project and Slice Definition Administration

**Status:** PROPOSED / VALIDATED / PENDING ACCEPTANCE
**Decision date:** 2026-09-30
**Authority:** `RLY-S14-AUTH-001`
**Accepted design:** Slice 1.4 Revision 2, `f5a678da360b96701a1f9635d3703b49dc16e779`
**Implementation result:** pending independent evaluation

## Context

Relay needs human-controlled Project and Slice definition CRUD while preserving
the accepted immutable domain schemas, lifecycle/governance ownership, and
history. Concurrent edits must not silently overwrite another human's decision,
and deleted identities must not be reused.

## Decision

1. Keep `Project` and `Slice` domain values immutable and unchanged. Return
   administration snapshots containing the value and exact definition revision.
2. Route all post-v4 runtime Project/Slice creation and edits through the
   `relay_engine.project_slice` service with HUMAN actor, aware UTC timestamp,
   and nonblank reason.
3. Add SQLite migration v4 with revision columns and append-only typed history.
   Deterministically seed existing rows at revision 1; reserve `SEED` for this
   migration only.
4. Require strict compare-and-swap before exact-target no-op detection. Keep all
   validation and mutation in one `BEGIN IMMEDIATE` transaction.
5. Preserve Project repository authority and Slice ownership as immutable.
   Validate parent/dependency graph integrity within the same Project.
6. Freeze Slice definition mutation after lifecycle initialization, for any gate
   revision, or when another current Slice depends on it.
7. Permit physical deletion only after explicit authority-reference guards;
   append a tombstone and remove current state atomically without cascading.

## Consequences

Definition history survives current-row deletion and prevents identity reuse.
Stale commands fail clearly; callers reconcile ambiguous outcomes by reading
current state and issuing a new explicit command. Existing lifecycle and
governance contracts remain unchanged. No runtime dependency is added.

## Acceptance state

```text
Initial implementation candidate:
e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d — RLY-S14-EVAL-001 REWORK

Bounded rework candidate: pending independent reevaluation
Human implementation acceptance: NOT GRANTED
Decision state: PROPOSED / VALIDATED / PENDING ACCEPTANCE
```
