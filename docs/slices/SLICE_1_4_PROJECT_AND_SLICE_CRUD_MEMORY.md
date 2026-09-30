# Slice 1.4 Development Memory — Project and Slice CRUD

**Status:** IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION
**Record state:** WORKING / NOT LOCKED
**Authority:** `RLY-S14-AUTH-001`
**Accepted design:** Revision 2 — `f5a678da360b96701a1f9635d3703b49dc16e779`
**Implementation baseline:** `d9d78350b9ae605c44191330047a8a697ad1b121`
**Branch:** `implementation/1.4-project-slice-crud`

## Objective and boundary

Implemented human-controlled Project and Slice definition create/read/list/
update/guarded-delete, exact definition revisions, append-only history,
optimistic concurrency, graph validation, and mutation provenance.

The accepted domain `Project` and `Slice` models remain unchanged. No lifecycle,
governance, repository, provider, UI, dependency invalidation, Slice 1.5, or agent
execution behavior was added.

## Implementation

- Migration v4 adds definition revisions and project/slice revision tables.
- Pre-v4 current records are deterministically seeded at revision 1 with
  migration-only `SEED` operations.
- Runtime CREATE/UPDATE/DELETE flows through `relay_engine.project_slice` with
  HUMAN actor, aware UTC occurrence time, and nonblank reason.
- Revision history uses canonical typed payloads and append-only database
  triggers; DELETE tombstones remain after current-row removal.
- CAS is checked before exact-target no-op behavior.
- Slice graph validation enforces same-Project references and acyclic parent and
  dependency graphs. Lifecycle, gate, and downstream dependency guards freeze
  Slice definitions.
- Project and Slice deletion explicitly checks accepted references and rolls
  back tombstone/current-row changes on residual integrity failure.

## Design lineage

```text
Human-authorized subject baseline: 670996ec43d77526adb0ea540c81a57d6e83453b
Authority-recording design parent: 1eaece23e31d831bfd2b27e55a898df389cc45fc
Revision 1: 430b1e1ff5eb06c26d4c63225b455feda14b6710
Revision 2 accepted design: f5a678da360b96701a1f9635d3703b49dc16e779
Combined design review: RLY-S14-DESIGN-EVAL-002 — ACCEPT
Human design acceptance: RLY-S14-DESIGN-ACCEPT-001
Implementation authorization: RLY-S14-AUTH-001
```

## Validation evidence

Local validation on this candidate:

```text
uv sync --frozen --group dev     PASS
ruff format --check              PASS
ruff check                       PASS
pyright                          PASS — 0 errors / 0 warnings
pytest                           PASS — 521 passed
uv build                         PASS
git diff --check                 PASS
```

The Slice 1.4-specific service suite contains 29 tests; the integration suite
adds two migration-v4/restart tests. CI for the exact pushed candidate SHA is
reported in the implementation handover.

## Governance state

```text
Accepted project baseline: d9d78350b9ae605c44191330047a8a697ad1b121
Slice 1.4: OPEN / IMPLEMENTATION CANDIDATE / PENDING EVALUATION
Technical acceptance: NOT REACHED
Human technical acceptance: NOT REACHED
Slice 1.5: NOT OPEN
Agent execution: NOT AUTHORIZED
```
