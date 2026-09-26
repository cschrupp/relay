# Persistence Model

**Status:** IMPLEMENTATION COMPLETE / PENDING EVALUATION
**Authority:** Slice 0.5 Design Revision 2
**Design SHA:** `2d2822644209e1002e77c39ab8f06757c583103b`

## Purpose and authority boundary

Slice 0.5 adds the first durable runtime-state boundary using Python's standard-library `sqlite3`. It stores validated Slice 0.2 domain values, Slice 0.3 lifecycle history and current projections, and Slice 0.4 gate and authority records. Persistence verifies explicit caller-supplied facts and preserves causal evidence. It does not redefine lifecycle or governance semantics.

SQLite is the only backend. Database paths and infrastructure timestamps are explicit inputs. Connections enable foreign keys and request WAL for file-backed databases where available. Writes use `BEGIN IMMEDIATE`, do not retry automatically, and classify lock/busy conditions as `DatabaseUnavailable`.

## Typed payloads and insert-only domain values

Complete domain values use canonical JSON serialized from validated immutable Pydantic models. SQL identity/index columns are derived from the same model. On load the exact model type validates the payload and each duplicated SQL column is checked against its corresponding typed field. Corruption raises `PersistenceIntegrityError`.

`Project`, `Baseline`, `Slice`, `Artifact`, `Decision`, and `Evidence` are inserted once by stable identity. Duplicate identities are rejected, including equal payloads. Gate revisions, authorization grants, human decisions, gate evaluation records, lifecycle events, and executions are append-only through the public API.

## Schema and migrations

`Migration` values contain an increasing version, nonblank name, and ordered SQL statements. The checksum is `sha256:` plus lowercase SHA-256 of the UTF-8 bytes of canonical JSON containing name, statements, and version. One migration application owns one transaction for all pending migrations in that call. Applied migration metadata records version, name, caller-supplied UTC application time, and checksum. Schema verification is read-only and rejects mismatched or unsupported migration history.

Tables cover projects, baselines, slices, artifacts, decisions, evidence, lifecycle current state and events, gate revisions, authorization grants, human decisions, gate evaluation records, and executions. No triggers create Relay events or governance results.

## Lifecycle causality

Initialization is a distinct atomic transition from absent state to revision zero. It requires a `LifecycleInitialized` event whose single-event replay exactly equals the supplied snapshot. A complete duplicate initialization is a `ConcurrencyConflict`; partial durable state is an integrity error.

Later mutations require the expected current revision. In one transaction the store verifies that durable history replays to durable current state, appends the candidate event in memory, and calls the accepted `replay_lifecycle()` function. The candidate is committed only when replay exactly equals the supplied next snapshot. The event insert and materialized snapshot update commit atomically. Revision races are `ConcurrencyConflict`; broken history or event/snapshot mismatch is `PersistenceIntegrityError`.

Events are the accepted Slice 0.3 union: `LifecycleInitialized`, `PhaseChanged`, `BlockageChanged`, and `ValidityChanged`. Event IDs are globally unique; each slice has one event per resulting revision. History loads in ascending resulting revision and can be checked with `verify_slice_history()`.

## Persisted governance and execution

Gates are immutable rows by `(gate_id, gate_revision)`; old revisions are retained. Grants and human decisions are immutable records by stable ID. Persistence does not select current authority by timestamp or infer the caller's gate set.

`GateEvaluationRecord` captures the caller-supplied canonical gate revision set, exact `HandoverContext`, and complete canonical evaluation tuple. Its ID and recording time are explicit inputs. `ExecutionRecord` links one governed phase-change event to exactly one evaluation record and records the selected gate/revision, baseline, lifecycle source/result revisions, actor, time, and reason.

`execute_and_persist_handover()` begins one immediate transaction and verifies the durable target lifecycle, baseline, each supplied gate, each dependency lifecycle, each supplied grant and human decision, and every listed available artifact/evidence ID. Caller-assessed values remain explicit and are preserved in the evaluation context. It calls `evaluate_handover_gates()` for the complete tuple, then delegates executable authority to `execute_handover()` so Slice 0.4's anti-forgery reevaluation remains intact. It checks selected evaluation equality, proves event-to-snapshot replay, and inserts evaluation evidence, lifecycle event/current snapshot, and execution record atomically.

## Determinism and exclusions

Lists use explicit ordering: lifecycle events by resulting revision, gate revisions by numeric revision, evaluation records by insertion sequence then ID, and executions by resulting revision then ID. The persistence package generates no Relay IDs, reads no clocks for engineering events, accesses no filesystem beyond the explicit SQLite target, and performs no network, GitHub, provider, notification, artifact discovery, or quality-tool work.

This slice does not add an ORM, generic repository or unit-of-work framework, triggers, full event sourcing, alternate database, API, UI, `.relay/` contract, canonical artifact or gate-set discovery, RBAC, revocation/expiry, agents, providers, or Slice 0.6 behavior.
