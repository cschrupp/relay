# Slice 1.4 Development Memory — Project and Slice CRUD

**Status:** IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION
**Record state:** WORKING / NOT LOCKED
**Authority:** `RLY-S14-AUTH-001`
**Accepted design:** Revision 2 — `f5a678da360b96701a1f9635d3703b49dc16e779`
**Rework baseline:** `dfe6c20c8f65b42fe69b7d315956a91d2a29487c`
**Rework branch:** `implementation/1.4-project-slice-crud-rework`
**Prior candidate:** `e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d`
**Prior evaluation:** `RLY-S14-EVAL-001 — REWORK`

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
- E1 exposed an error-classification ordering defect: validate the proposed
  graph before applying the downstream-dependency freeze rejection. Invalid
  cycles now return `SliceDependencyCycle`; valid mutations remain blocked when
  a downstream Slice depends on the target.
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

The prior candidate passed the following local checks and exact-SHA CI before
independent evaluation identified the bounded evidence gaps:

```text
uv sync --frozen --group dev     PASS
ruff format --check              PASS
ruff check                       PASS
pyright                          PASS — 0 errors / 0 warnings
pytest                           PASS — 521 passed
uv build                         PASS
git diff --check                 PASS
GitHub Actions                   PASS — run 36881760825, prior SHA e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d
```

The prior Slice 1.4-specific service suite contained 29 tests; the integration
suite added two migration-v4/restart tests. Rework evidence adds public-path
dependency-cycle rejection, Project/Slice history-index corruption, a
two-connection update/delete race, exact authority-lineage checks, and an
explicit post-v4 Slice `CREATE` assertion. The rework-specific service suite
contains 33 tests.

Rework local validation:

```text
uv sync --frozen --group dev     PASS
ruff format --check              PASS
ruff check                       PASS
pyright                          PASS — 0 errors / 0 warnings
pytest                           PASS — 525 passed
uv build                         PASS
git diff --check                 PASS
GitHub Actions                   pending publication of the rework result
```

## Governance state

```text
Accepted project baseline before rework: dfe6c20c8f65b42fe69b7d315956a91d2a29487c
Historical initial implementation: e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d
RLY-S14-EVAL-001: REWORK — governance provenance repaired; bounded evidence rework authorized
Rework candidate: pending result commit / independent reevaluation
Slice 1.4: OPEN / IMPLEMENTATION REWORK / PENDING EVALUATION
Technical acceptance: NOT REACHED
Human technical acceptance: NOT REACHED
Slice 1.5: NOT OPEN
Agent execution: NOT AUTHORIZED
```
