# Slice 0.5 Development Memory — Event and Persistence Model

**Status:** COMPLETE / ACCEPTED
**Record state:** LOCKED
**Accepted project baseline:** `c8006306d48624f13599fe448ef677015fd1829e`
**Accepted design:** Slice 0.5 Revision 2, `2d2822644209e1002e77c39ab8f06757c583103b`
**Implementation branch:** `slice/0.5-event-persistence`
**Accepted implementation result:** `d3ee53a572483e0bd96dbac2554bfad24c06136a`
**Independent reevaluation:** `RLY-S05-EVAL-002` — ACCEPT
**Human acceptance:** `RLY-S05-ACCEPT-001`

## Authority and design lineage

- Design Revision 1: `76ea38b98c218ffc0eab797c03699f45e3d4d951`.
- Independent design review: `RLY-S05-DESIGN-EVAL-001` — REVISE; findings F001–F007.
- Design Revision 2: `2d2822644209e1002e77c39ab8f06757c583103b`.
- Independent design review: `RLY-S05-DESIGN-EVAL-002` — ACCEPT.
- Human design acceptance: `RLY-S05-DESIGN-ACCEPT-001`.
- Explicit implementation authorization: `RLY-S05-AUTH-001`.
- Accepted Slice 0.5 implementation result: `d3ee53a572483e0bd96dbac2554bfad24c06136a`.
- Independent reevaluation: `RLY-S05-EVAL-002` — ACCEPT.
- Human acceptance: `RLY-S05-ACCEPT-001`.

Revision 2 preserves the Revision 1 architecture and resolves F001–F007 with explicit lifecycle replay causality, distinct initialization, durable exact-fact checks for governed execution, complete evaluation evidence identity, insert-only static identities, canonical migration checksums and batch atomicity, and index/payload integrity checks.

## Objective and locked boundaries

Implement the first durable runtime-state boundary as current materialized state plus immutable historical records using SQLite and Python's standard library. Preserve accepted Slice 0.2 domain, Slice 0.3 lifecycle, and Slice 0.4 governance semantics.

The implementation adds no dependencies and no generic repository, ORM, unit-of-work, event-sourcing, DI, plugin, or backend framework. Persistence verifies explicit caller-supplied facts; it does not infer canonical authority, gate sets, artifacts, or governance facts. Slice 0.6 remains outside scope.

## Implementation summary

- Added `relay_engine.persistence` with an explicit SQLite connection boundary, migration/checksum logic, typed immutable evidence records, exact error family, and concrete insert/load and transactional operations.
- Added `geval_` and `exec_` ID types to the accepted ID mechanism. IDs remain caller supplied to persistence operations.
- Added insert-only Project/Baseline/Slice/Artifact/Decision/Evidence records; append-only gate revisions, grants, human decisions, lifecycle events, gate evaluations, and execution records.
- Added lifecycle initialization and expected-revision mutation with accepted replay proof and atomic current/history writes.
- Added persisted governed execution that verifies durable references, preserves exact context and canonical gate results, calls Slice 0.4 evaluation/execution, and atomically records event, snapshot, evaluation, and execution evidence.
- Added SQLite model/integration tests, including all named Revision-2 regression scenarios.

## Change surface

Production additions: `src/relay_engine/persistence/{__init__,database,errors,migrations,records,store}.py`. Existing production edits: `src/relay_engine/domain/ids.py`, `src/relay_engine/domain/__init__.py`. Tests: `tests/unit/test_persistence_models.py`, `tests/integration/test_persistence_sqlite.py`. Required documents: `docs/architecture/PERSISTENCE_MODEL.md`, this working memory, `docs/decisions/ADR-0005-sqlite-phase0-persistence.md`, and living baseline update in `docs/CURRENT_BASELINE.md`.

Production behavior changes outside persistence and the two authorized ID exports: none. Runtime dependencies changed: none. Development dependencies changed: none. Slice 0.6 files/behavior added: none.

## Independent evaluation and bounded rework

Submitted candidate: `32f92b154d380a77188db36d9ea00c874748664a`. Independent evaluation `RLY-S05-EVAL-001` returned REWORK; architecture and contract escalations were not required. Findings are limited to:

- F001: verify the physical schema after both migration-apply and verify-only startup paths.
- F002: reject applied migration history that is not a contiguous prefix before applying pending SQL.
- F003: correct the migration-batch rollback test so an already-committed migration remains while a successful pending migration and a later failing migration are both rolled back.

The evaluator verified accepted-design ancestry, authorized scope, the existing persistence/governance behavior, and green CI on the submitted SHA. The bounded corrections are complete in the authorized migration/database code and SQLite integration tests, with this memory/current-baseline projection updated. ADR-0005, the accepted design, and the persistence architecture document remain unchanged.

Bounded migration rework implementation: `5e387a9d3f123b6333f9b700b22a8f9846a51f0b`. Rework result: `d3ee53a572483e0bd96dbac2554bfad24c06136a`. Independent reevaluation `RLY-S05-EVAL-002` returned ACCEPT. Human Authority accepted the exact result under `RLY-S05-ACCEPT-001`.

Implementation findings:

- `RLY-S05-EVAL-F001` — RESOLVED.
- `RLY-S05-EVAL-F002` — RESOLVED.
- `RLY-S05-EVAL-F003` — RESOLVED.

## Validation and evidence

Validation on the rework implementation commit `5e387a9d3f123b6333f9b700b22a8f9846a51f0b`:

```text
uv sync --frozen --group dev     PASS
ruff format --check              PASS
ruff check                       PASS
pyright                          PASS — 0 errors
pytest                           PASS — 332 passed
uv build                         PASS
git diff --check                 PASS
GitHub Actions                   PASS — run 36206187380
```

The validation above records the rework implementation commit. The acceptance-record commit is separate provenance and does not replace the accepted implementation result SHA.

## Acceptance criteria

The implementation is being validated against all A01–A97 in the accepted design. Revision-2 finding coverage is explicit:

- F001 — candidate lifecycle history must replay exactly to supplied next snapshot.
- F002 — initialization is a distinct, atomic absent-to-revision-zero operation.
- F003 — governed execution exact-checks persistence-owned caller facts against durable records.
- F004 — GateEvaluationRecord preserves exact gate set, context, and complete result tuple; executions link to it.
- F005 — static domain identities reject every duplicate insert.
- F006 — migration checksum framing is canonical and pending batches are atomic.
- F007 — duplicated SQL columns are derived from and checked against typed payloads.

## Known limitations and deferred work

SQLite is the only backend. No database backup/replication product, cloud service, ORM, repository synchronization, API/CLI/UI, `.relay/` contract, artifact registry/discovery, canonical gate-set selection, GitHub integration, notifications, identity/RBAC, authorization expiry/revocation, risk scoring, quality execution, agent/provider execution, generic Evaluation aggregate, research/experiments, or Slice 0.6 capability is included.

## Governance state and hard stop

Slice 0.5 is COMPLETE / ACCEPTED under `RLY-S05-ACCEPT-001`; this development memory is LOCKED. The accepted implementation result is `d3ee53a572483e0bd96dbac2554bfad24c06136a`. Slice 0.6 has not started and is NOT AUTHORIZED. Hard stop: ACTIVE. Corrections to this locked memory must follow Documentation Governance amendment or supersession rules.
