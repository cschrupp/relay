# ADR-0005 — SQLite Phase-0 Persistence

**Status:** PROPOSED / VALIDATED / PENDING ACCEPTANCE
**Decision date:** 2026-09-26
**Authority:** Slice 0.5 Design Revision 2 (`2d2822644209e1002e77c39ab8f06757c583103b`)
**Implementation state:** Candidate pending independent evaluation

## Context

Relay has accepted immutable domain values, deterministic lifecycle operations, and explicit handover governance, but it has no durable runtime-state boundary. Slice 0.5 requires persistence without changing those semantics or introducing speculative infrastructure.

## Decision

1. Use SQLite through Python's standard-library `sqlite3`; add no runtime or development dependency.
2. Keep validated Pydantic values as canonical typed payloads. Derive constrained/indexed columns from those values and verify agreement on load.
3. Treat Project, Baseline, Slice, Artifact, Decision, and Evidence as insert-once by stable identity. Persist gate revisions, lifecycle events, grants, human decisions, evaluation records, and execution records append-only through the public API.
4. Store lifecycle current state as a materialized projection and accepted Slice 0.3 events as immutable chronology. Require replay equality for initialization and each later state change.
5. Use explicit expected revisions and SQLite immediate transactions. Revision staleness is a semantic concurrency conflict; database busy/lock is an operational availability error. Never retry automatically.
6. Preserve complete gate-evaluation context and results as `GateEvaluationRecord`; require each `ExecutionRecord` to reference that exact record.
7. For persisted governed execution, verify caller-supplied persistence-owned facts, then call the accepted Slice 0.4 evaluation and execution APIs. Do not infer authority or canonical gate sets from stored rows.
8. Use ordered, checksummed migrations with a canonical SHA-256 input and one transaction for the complete pending batch.
9. Keep GitHub integration, artifact discovery, repositories, APIs, UI, ORM, alternate stores, RBAC, providers, and Slice 0.6 semantics out of scope.

## Consequences

Relay can recover exact domain records, lifecycle state/history, gate revisions, authority records, evaluations, and governed executions after reopening a file-backed database. Stored payload/index corruption and event-history divergence are detectable. SQLite locking is reported as `DatabaseUnavailable`; it is not converted into last-write-wins behavior.

Caller-supplied governance assessment facts and gate sets remain explicit. Persistence verifies their durable references but does not decide which authority or gate set is canonical. SQLite is the only Slice 0.5 backend, and there is no automatic retry or SQL trigger that manufactures Relay semantics.

## Acceptance

Human design acceptance: `RLY-S05-DESIGN-ACCEPT-001`
Implementation authorization: `RLY-S05-AUTH-001`
Technical implementation result: pending independent evaluation
Human implementation acceptance: pending
