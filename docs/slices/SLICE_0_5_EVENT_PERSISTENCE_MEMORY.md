# Slice 0.5 Development Memory — Event and Persistence Model

**Status:** IMPLEMENTATION COMPLETE / PENDING EVALUATION
**Record state:** WORKING / NOT LOCKED
**Accepted project baseline:** `c8006306d48624f13599fe448ef677015fd1829e`
**Accepted design:** Slice 0.5 Revision 2, `2d2822644209e1002e77c39ab8f06757c583103b`
**Implementation branch:** `slice/0.5-event-persistence`

## Authority and design lineage

- Design Revision 1: `76ea38b98c218ffc0eab797c03699f45e3d4d951`.
- Independent design review: `RLY-S05-DESIGN-EVAL-001` — REVISE; findings F001–F007.
- Design Revision 2: `2d2822644209e1002e77c39ab8f06757c583103b`.
- Independent design review: `RLY-S05-DESIGN-EVAL-002` — ACCEPT.
- Human design acceptance: `RLY-S05-DESIGN-ACCEPT-001`.
- Explicit implementation authorization: `RLY-S05-AUTH-001`.

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

Production additions: `src/relay_engine/persistence/{__init__,database,errors,migrations,records,store}.py`. Existing production edits: `src/relay_engine/domain/ids.py`, `src/relay_engine/domain/__init__.py`. Tests: `tests/unit/test_persistence_models.py`, `tests/integration/test_persistence_sqlite.py`. Required documents: `docs/architecture/PERSISTENCE_MODEL.md`, this working memory, `docs/decisions/ADR-0005-sqlite-phase0-persistence.md`, and candidate projection update in `docs/CURRENT_BASELINE.md`.

Production behavior changes outside persistence and the two authorized ID exports: none. Runtime dependencies changed: none. Development dependencies changed: none. Slice 0.6 files/behavior added: none.

## Validation and evidence

Pending final complete local validation and GitHub Actions on the exact candidate result SHA. The named persistence test files have been exercised during development; final command results and test count will be recorded in the implementation handover. No acceptance is claimed here.

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

Slice 0.5 design is accepted and implementation is explicitly authorized by `RLY-S05-AUTH-001`. The implementation candidate remains pending independent evaluation and Human Authority acceptance. Slice 0.6 has not started and is not authorized. This memory and ADR-0005 remain unlocked pending acceptance.
