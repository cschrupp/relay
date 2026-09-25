# Slice 0.5 — Event and Persistence Model

**Document revision:** 1  
**Status:** REVIEW  
**Document class:** Lockable design record  
**Authority:** Human Authority opened Slice 0.5 design work after formal Slice 0.4 closure  
**Baseline SHA:** `c8006306d48624f13599fe448ef677015fd1829e`  
**Implementation authorization:** NOT GRANTED  

---

# 1. Objective

Persist Relay project state without losing historical causality.

Slice 0.5 introduces the first durable runtime state boundary for Relay while preserving the deterministic semantics accepted in Slices 0.2–0.4.

The persistence model is:

```text
current materialized state
+
immutable historical records
```

Relay does not require full event sourcing in this slice.

The system must be able to restart, recover current accepted runtime state, preserve immutable transition chronology, reject conflicting writes, and migrate its schema explicitly.

---

# 2. Architectural principle

Persistence is subordinate to accepted domain and governance semantics.

```text
Domain models
    define engineering meaning

Lifecycle / governance engines
    define valid state change

Persistence
    stores exact resulting state and immutable evidence atomically
```

Database structure must not redefine lifecycle or governance rules.

No lifecycle transition table, gate policy, or authorization semantics may be duplicated in SQL.

---

# 3. S0.5-D01 — SQLite is the Phase-0 persistence backend

Slice 0.5 uses Python's standard-library `sqlite3` module.

No new runtime or development dependency is required.

Reasons:

- restart durability is real rather than mocked;
- ACID transactions are available immediately;
- schema constraints and migrations can be exercised now;
- optimistic concurrency can be tested with multiple connections;
- deployment complexity remains minimal;
- no ORM or cloud database architecture is justified yet.

This decision does NOT establish SQLite as Relay's permanent production backend.

A later production-database decision requires separate evidence and authority.

---

# 4. S0.5-D02 — Persistence is explicit, not a speculative generic repository framework

Slice 0.5 introduces a narrow `relay_engine.persistence` package.

Expected modules:

```text
persistence/
    __init__.py
    database.py
    migrations.py
    records.py
    errors.py
    store.py
```

The implementation may use smaller internal helpers when needed, but must not introduce:

```text
generic repository base classes
unit-of-work framework
ORM
DI container
plugin persistence layer
backend registry
SQL query builder
CQRS framework
event-sourcing framework
```

The public API should expose concrete Relay persistence operations.

---

# 5. S0.5-D03 — Database path and connection creation are explicit

Opening persistence requires an explicit SQLite database target.

Conceptually:

```python
open_database(path) -> RelayDatabase
```

The caller owns the configured database path.

`:memory:` is permitted for tests.

Connection initialization must enable:

```text
PRAGMA foreign_keys = ON
```

File-backed databases should use WAL journal mode unless SQLite rejects it for the selected target.

Persistence operations must not read application configuration implicitly.

---

# 6. S0.5-D04 — Schema migrations are explicit and monotonic

Slice 0.5 introduces an ordered migration mechanism.

The database records applied migrations in:

```text
relay_schema_migrations
```

At minimum:

```text
version INTEGER PRIMARY KEY
name TEXT NOT NULL
applied_at TEXT NOT NULL
checksum TEXT NOT NULL
```

Rules:

```text
versions begin at 1
versions are strictly increasing
one version is applied at most once
unknown future database version is rejected
migration checksum mismatch is rejected
all pending migrations execute in order
migration application is transactional
```

Migration timestamps are explicit inputs from the migration caller or one database-open operation; they are not engineering-domain timestamps.

The migration system is database-infrastructure state, not Relay domain event history.

---

# 7. S0.5-D05 — Initial schema persists accepted runtime categories

The initial schema must persist at least:

```text
projects
baselines
slices
artifacts
decisions
evidence
lifecycle snapshots
lifecycle events
handover gates
authorization grants
human decisions
gate evaluations
executions
```

This fulfills the build-plan categories while retaining accepted Slice 0.2 concepts needed by current project state.

No table is created for future concepts that still lack an accepted domain contract.

In particular, do not add AgentRole, AgentAssignment, ResearchTask, ResearchFinding, Source, or Experiment persistence merely because future phases mention them.

---

# 8. S0.5-D06 — Typed models remain canonical; SQL rows are storage representations

Persisted typed objects are serialized from their accepted Pydantic models.

Where a table stores a complete object, it stores:

```text
identity columns required for constraints/indexing
schema_version
canonical JSON payload
```

Canonical JSON payloads must round-trip through the exact Relay model type before being returned to callers.

SQL rows are not new domain models.

A generic untyped `metadata` or arbitrary facts column is forbidden.

---

# 9. S0.5-D07 — Current materialized state and immutable history have distinct tables

Current-state tables may be updated under optimistic concurrency.

Historical tables are append-only through the public persistence API.

At minimum:

```text
lifecycle_current
lifecycle_events

gate_evaluations
executions
```

have explicit current/history semantics.

`lifecycle_current` is the materialized current lifecycle snapshot for one slice.

`lifecycle_events` is immutable chronology.

Gate evaluations and executions are historical evidence and are never updated in place.

---

# 10. S0.5-D08 — Lifecycle persistence is atomic with its event

Every persisted lifecycle mutation must store, in one database transaction:

```text
new SliceLifecycle snapshot
+
corresponding immutable lifecycle event
```

The transaction either commits both or neither.

A persisted lifecycle snapshot may never advance without the event that caused it.

A lifecycle event may never be committed for a revision that did not become the current persisted lifecycle revision.

---

# 11. S0.5-D09 — Persisted lifecycle writes use expected revision

Every state-changing persistence operation must supply the caller's expected lifecycle revision.

Conceptually:

```python
persist_lifecycle_change(
    current_expected_revision,
    updated_lifecycle,
    event,
)
```

The update succeeds only if the persisted current lifecycle revision equals `current_expected_revision`.

Otherwise:

```text
ConcurrencyConflict
```

No last-write-wins behavior is permitted.

The database writer must check and update the expected revision in the same transaction.

---

# 12. S0.5-D10 — Optimistic concurrency is the semantic conflict mechanism

SQLite writer locking is an implementation mechanism, not Relay's logical concurrency contract.

The logical contract is:

```text
caller observed revision N
caller proposes N → N+1
write succeeds only if persisted revision is still N
```

Two writers starting from revision N cannot both commit revision N+1.

Exactly one may succeed.

The other receives `ConcurrencyConflict`.

---

# 13. S0.5-D11 — Lifecycle events remain Slice 0.3 events

Persistence does not invent replacement event types for accepted lifecycle semantics.

Persist the accepted immutable event union from Slice 0.3:

```text
LifecycleInitialized
PhaseChanged
BlockageChanged
ValidityChanged
```

Event table indexing must expose at minimum:

```text
event_id
slice_id
event_type
resulting_revision
occurred_at
payload_json
```

Constraints:

```text
event_id unique globally
(slice_id, resulting_revision) unique
```

Historical event payloads are immutable after insert.

---

# 14. S0.5-D12 — Lifecycle chronology can be reconstructed

Persistence must expose:

```python
load_lifecycle_events(slice_id) -> tuple[LifecycleEventRecord, ...]
```

ordered by resulting revision.

The loaded event stream must successfully reconstruct the same current lifecycle using the accepted Slice 0.3 `replay_lifecycle()` operation.

A reconstruction mismatch is a persistence-integrity failure.

Do not create a second replay implementation in persistence.

---

# 15. S0.5-D13 — Project restart recovery is deterministic

A new process opening an existing database must be able to load:

```text
Project
current Slice definitions
current SliceLifecycle snapshots
current gate definitions
authorization grants
current supplied human-decision records
historical lifecycle events
historical gate evaluations
historical executions
```

No in-memory cache is authoritative.

Restart recovery must not require GitHub, filesystem repository scanning, an LLM, or any provider.

---

# 16. S0.5-D14 — Gate definitions are revisioned durable records

Handover gates are persisted by exact:

```text
gate_id
gate_revision
baseline_id
```

A new revision is inserted as a new immutable record.

An old gate revision is not overwritten.

The persistence API may load:

```text
exact revision
latest stored revision for one logical gate
all revisions for one logical gate
```

"latest" here is numeric gate revision inside one logical gate, not canonical project authority.

Slice 0.6 still owns canonical repository artifact discovery.

---

# 17. S0.5-D15 — Authorization grants and human decisions are immutable records

Persist:

```text
AuthorizationGrant
HumanApprovalDecision
HumanChoiceDecision
```

by their stable IDs.

Duplicate ID insert with different payload is an integrity error.

The database does not infer which historical record is current by timestamp.

Callers construct the current `HandoverContext` explicitly from selected persisted facts.

Revocation, expiry, and authorization-history semantics remain out of scope unless separately designed.

---

# 18. S0.5-D16 — GateEvaluation is persisted evidence

A persisted gate evaluation stores the exact accepted `GateEvaluation` payload produced by Slice 0.4 plus an explicit evidence ID and persistence timestamp if a stable persisted-record identity is required.

The persistence layer does not recompute gate evaluation.

It records evidence supplied by the caller.

A persisted evaluation must preserve:

```text
gate_id
gate_revision
slice_id
baseline_id
lifecycle_revision
governance_revision
target_phase
light
reasons
```

Evaluation evidence is append-only.

---

# 19. S0.5-D17 — Execution becomes a persisted immutable record

Slice 0.5 introduces a minimal `ExecutionRecord` storage model representing one governed lifecycle execution.

It records at minimum:

```text
execution_id
slice_id
baseline_id
gate_id
gate_revision
source_lifecycle_revision
resulting_lifecycle_revision
event_id
gate_evaluation reference or payload
actor
occurred_at
reason
```

The record means:

> this governed handover was executed and committed.

It does not model agent runtime, subprocesses, sandboxes, logs, tokens, providers, or code-generation execution.

Those belong to later phases.

---

# 20. S0.5-D18 — Persisted governed execution is one transaction

Slice 0.5 must provide a persistence orchestration operation around accepted Slice 0.4 execution.

Conceptually:

```python
execute_and_persist_handover(
    database,
    gates,
    selected_gate_id,
    context,
    expected_lifecycle_revision,
    execution_id,
    event_id,
    actor,
    occurred_at,
    reason,
)
```

Required order inside one logical operation:

```text
BEGIN write transaction
load persisted lifecycle
verify expected revision
verify supplied context lifecycle matches persisted lifecycle
run Slice 0.4 execute_handover()
persist exact GateEvaluation used
insert exact PhaseChanged event
update lifecycle_current using expected revision
insert ExecutionRecord
COMMIT
```

Any failure rolls back all writes.

Persistence does not duplicate gate evaluation or lifecycle transition semantics.

---

# 21. S0.5-D19 — Persisted context mismatch is rejected

For persisted governed execution, the supplied `HandoverContext.lifecycle` must equal the current persisted lifecycle snapshot for the target slice.

If not:

```text
ConcurrencyConflict
```

or a more specific persistence consistency error if the design review establishes one.

The engine must never execute from a stale supplied lifecycle while persisting against a newer database snapshot.

---

# 22. S0.5-D20 — Transaction boundaries are explicit

Public multi-record writes own their transaction.

Nested implicit commits are forbidden.

Low-level persistence helpers must not commit independently when used inside a higher-level transaction.

For write transactions, `BEGIN IMMEDIATE` is the default SQLite mode so writer contention is detected before state-change work proceeds.

A SQLite lock/busy condition is distinct from optimistic revision conflict.

Implementation may surface database-busy as a narrow persistence operational error rather than silently retrying.

Automatic retry is out of scope for Slice 0.5.

---

# 23. S0.5-D21 — Persistence error family is narrow

Introduce:

```text
PersistenceError
├── PersistenceIntegrityError
├── ConcurrencyConflict
├── MigrationError
└── DatabaseUnavailable
```

Pydantic validation errors continue to represent malformed serialized domain payloads where appropriate.

SQLite exceptions must not leak arbitrarily across the public persistence API; translate expected operational/integrity cases into the narrow Relay persistence errors while preserving exception chaining.

Do not build a large database-exception taxonomy.

---

# 24. S0.5-D22 — No credentials or secrets in engineering-state tables

Engineering-state persistence must not contain:

```text
provider API keys
GitHub tokens
OAuth tokens
passwords
private keys
connection credentials
```

Database path/configuration may exist outside engineering-state tables.

Secrets management is a later product concern.

---

# 25. S0.5-D23 — Time semantics remain explicit

Domain timestamps are supplied by accepted domain/governance operations.

The database must not replace them with `CURRENT_TIMESTAMP` as engineering truth.

Infrastructure-only timestamps such as migration application time or persistence-record insertion time may be generated by the caller/database adapter, but they are never substituted for:

```text
occurred_at
granted_at
human decision occurred_at
lifecycle updated_at
```

All serialized datetime values must round-trip as timezone-aware UTC-normalized values.

---

# 26. S0.5-D24 — IDs are caller supplied

Persistence generates no domain IDs.

Use the existing explicit ID mechanism for domain/governance IDs.

If Slice 0.5 introduces `ExecutionId`, extend the accepted prefix mechanism narrowly, e.g.:

```text
exec_
```

The persistence engine itself does not call `new_id()` during state-changing operations.

Migration row identity is infrastructure state and does not use domain IDs.

---

# 27. S0.5-D25 — Database integrity constraints support, but do not replace, domain validation

Use database constraints for structural invariants appropriate to storage:

```text
primary keys
unique IDs
foreign keys where lifecycle-safe
unique event revisions
non-null required storage columns
```

Do not attempt to encode the Relay lifecycle transition matrix or gate-policy rules as SQL CHECK constraints/triggers.

Pydantic/domain engines remain authoritative for engineering semantics.

---

# 28. S0.5-D26 — No database triggers for domain events

Lifecycle events are inserted explicitly by the application transaction that performed the accepted transition.

No SQL trigger may synthesize Relay domain events.

Reason:

```text
domain causality must remain visible in Python contract
```

Database triggers may not create hidden engineering behavior.

---

# 29. S0.5-D27 — Historical records are immutable through public API

The public persistence API provides no update/delete operations for:

```text
lifecycle events
gate evaluations
executions
gate revisions
authorization grants
human decisions
```

Test-only direct SQL mutation may be used to construct corruption fixtures.

Production API does not expose historical record rewriting.

---

# 30. S0.5-D28 — Static/current domain objects use explicit upsert semantics only where authorized

Project, Slice, Artifact, Decision, Evidence, and Baseline persistence must use explicit save semantics.

The store must distinguish:

```text
insert new identity
replace/update current mutable projection where the domain contract permits it
conflicting unexpected overwrite
```

Do not implement generic blind UPSERT for every domain type.

Where an accepted domain object is immutable, storing a different payload under the same ID is `PersistenceIntegrityError`.

---

# 31. S0.5-D29 — Database schema version and model schema_version are separate

Do not conflate:

```text
SQLite database migration version
```

with:

```text
DomainModel.schema_version
```

Database migration changes physical storage.

Model schema version identifies serialized model contract.

Both must remain independently inspectable.

---

# 32. S0.5-D30 — Startup compatibility checks are deterministic

Opening a database must reject:

```text
future unsupported database schema version
migration checksum mismatch
required table/index absence after declared migration version
malformed persisted model payload when loaded
```

Opening may automatically apply known pending migrations when explicitly requested by the caller.

The API must support a mode that verifies schema without applying migrations.

---

# 33. S0.5-D31 — Backup/restore and distributed replication are out of scope

Slice 0.5 does not design:

```text
online backup service
replication
leader election
multi-node consensus
PostgreSQL
cloud database hosting
high availability
cross-region recovery
```

A SQLite file can be copied using SQLite-safe operational practices, but backup product behavior is not a Slice 0.5 contract.

---

# 34. S0.5-D32 — Repository synchronization remains Slice 0.6+

Slice 0.5 persists Relay runtime state.

It does not decide whether a database row or repository artifact is canonical when both exist.

That source-of-truth and `.relay/` contract remains Slice 0.6.

Therefore Slice 0.5 must not:

```text
scan repository files
write .relay/
resolve canonical document paths
infer artifact canonicality from Git
synchronize database state with repository state
```

---

# 35. S0.5-D33 — Persistence does not add an API/service layer

No REST server, CLI workflow, UI, background worker, or message queue is required.

Tests and future callers may invoke persistence directly as Python library operations.

---

# 36. S0.5-D34 — Persistence does not authenticate humans

Persisted `ActorRef` values are historical engineering facts supplied by callers.

Slice 0.5 does not introduce identity verification, user accounts, RBAC, sessions, or authentication.

---

# 37. S0.5-D35 — Deterministic read ordering is explicit

All public list/history operations define stable ordering.

Examples:

```text
lifecycle events → resulting_revision ASC
gate revisions → revision ASC
gate evaluations → persistence sequence ASC or explicit record ID ordering
executions → resulting_lifecycle_revision ASC, then execution_id
```

No caller-visible ordering may depend on SQLite's incidental row order.

---

# 38. S0.5-D36 — Persistence sequence may be infrastructure-local

Historical evidence tables may use an internal monotonic integer primary key for deterministic insertion ordering.

Such a sequence:

```text
is not a Relay domain ID
is not authority
is not exposed as semantic revision
```

It exists only to give stable storage ordering where the persisted record lacks a natural domain sequence.

---

# 39. S0.5-D37 — Corruption is surfaced, not silently repaired

If persisted current lifecycle and lifecycle event history disagree, the persistence layer must raise `PersistenceIntegrityError` when verification is requested.

It must not:

```text
silently rewrite current state
silently delete events
silently regenerate events
pick one source arbitrarily
```

Repair tooling is out of scope.

---

# 40. S0.5-D38 — Integrity verification is a public operation

Provide a deterministic verification operation conceptually:

```python
verify_slice_history(slice_id) -> None
```

It must:

```text
load ordered lifecycle events
replay them with Slice 0.3
load current lifecycle snapshot
compare replay result == stored current snapshot
```

Mismatch raises `PersistenceIntegrityError`.

This is read-only.

---

# 41. S0.5-D39 — Persistence tests use real SQLite

Core persistence tests must exercise actual SQLite connections, not mocked repositories.

Required test modes:

```text
:memory: for isolated unit tests
file-backed temporary database for restart/migration/concurrency tests
multiple connections for optimistic-concurrency tests
```

No external database service is required in CI.

---

# 42. S0.5-D40 — Existing accepted behavior must remain unchanged

Slice 0.2 domain, Slice 0.3 lifecycle, and Slice 0.4 governance APIs continue to work without a database.

Persistence is an additive boundary.

Pure lifecycle/governance tests must not suddenly require SQLite setup.

---

# 43. Expected implementation surface

Expected new production package:

```text
src/relay_engine/persistence/
    __init__.py
    database.py
    migrations.py
    records.py
    errors.py
    store.py
```

Narrow existing modifications may include:

```text
src/relay_engine/domain/ids.py
src/relay_engine/domain/__init__.py
```

only if a new `ExecutionId` is accepted.

Expected tests:

```text
tests/unit/test_persistence_models.py
tests/integration/test_persistence_sqlite.py
```

Implementation documentation, after authorization, may add:

```text
docs/architecture/PERSISTENCE_MODEL.md
docs/decisions/ADR-0005-sqlite-phase0-persistence.md
docs/slices/SLICE_0_5_EVENT_PERSISTENCE_MEMORY.md
```

No implementation file listed here is authorized by this design revision.

---

# 44. Explicitly out of scope

```text
full event sourcing
ORM
SQLAlchemy
PostgreSQL
cloud database service
replication
backup product
message bus
background workers
REST/API
CLI workflow
UI/board
GitHub integration
.relay/ repository contract
canonical artifact registry
repository synchronization
agent execution
AgentRole / AgentAssignment
provider/model execution
notifications
identity / RBAC
authorization revocation/expiry semantics
research / experiments
Slice 0.6 implementation
```

---

# 45. Acceptance criteria

## Core backend and migration

```text
A01 SQLite is the only Slice 0.5 backend.
A02 Slice 0.5 adds no runtime dependency.
A03 connection target is explicit.
A04 foreign keys are enabled.
A05 migrations are ordered and monotonic.
A06 applied migrations are recorded with version/name/checksum/time.
A07 migration checksum mismatch is rejected.
A08 unsupported future schema version is rejected.
A09 pending migrations can be applied transactionally.
A10 schema can be verified without applying migrations.
```

## Persistence categories

```text
A11 accepted Project values round-trip.
A12 accepted Baseline values round-trip.
A13 accepted Slice values round-trip.
A14 accepted Artifact values round-trip.
A15 accepted Decision values round-trip.
A16 accepted Evidence values round-trip.
A17 SliceLifecycle current snapshots round-trip.
A18 lifecycle event union round-trips.
A19 HandoverGate revisions round-trip.
A20 AuthorizationGrant values round-trip.
A21 HumanApprovalDecision values round-trip.
A22 HumanChoiceDecision values round-trip.
A23 GateEvaluation evidence round-trips.
A24 ExecutionRecord values round-trip.
A25 malformed stored model payload is rejected.
```

## Lifecycle causality

```text
A26 current lifecycle update and event append commit atomically.
A27 rollback leaves neither partial snapshot nor event.
A28 event IDs are unique.
A29 one slice cannot have two events for one resulting revision.
A30 event history is returned in revision order.
A31 replay of stored events reproduces stored current lifecycle.
A32 verify_slice_history is read-only.
A33 history mismatch raises PersistenceIntegrityError.
```

## Concurrency

```text
A34 lifecycle mutation requires expected revision.
A35 expected-revision mismatch raises ConcurrencyConflict.
A36 two writers from the same revision cannot both commit.
A37 no last-write-wins fallback exists.
A38 supplied persisted-execution context must match stored lifecycle.
A39 database lock/busy is not reported as ConcurrencyConflict.
A40 no automatic write retry occurs.
```

## Governance persistence

```text
A41 gate revisions are immutable historical rows.
A42 same gate ID may persist multiple explicit revisions.
A43 authorization grants are append-only records.
A44 human decisions are append-only records.
A45 gate evaluations are append-only evidence.
A46 persistence does not recompute GateEvaluation.
A47 persistence does not infer current authority by timestamp.
```

## Governed execution

```text
A48 execute_and_persist_handover loads the current persisted lifecycle.
A49 it verifies expected revision before commit.
A50 it delegates governance to Slice 0.4 execute_handover().
A51 it persists the exact GateEvaluation returned by Slice 0.4.
A52 it persists the exact lifecycle event returned by Slice 0.4/0.3.
A53 it persists the resulting lifecycle snapshot.
A54 it persists one ExecutionRecord.
A55 all execution records commit in one transaction.
A56 any failure rolls back every write from the attempted execution.
A57 successful execution survives database close/reopen.
```

## Historical immutability

```text
A58 public API has no historical lifecycle-event update/delete.
A59 public API has no gate-evaluation update/delete.
A60 public API has no execution update/delete.
A61 public API has no gate-revision update-in-place.
A62 public API has no authorization-grant update/delete.
A63 public API has no human-decision update/delete.
```

## Scope and deterministic behavior

```text
A64 existing lifecycle/governance pure APIs remain database-independent.
A65 persistence performs no Git/GitHub lookup.
A66 persistence performs no LLM/provider call.
A67 persistence performs no artifact discovery.
A68 persistence performs no notification.
A69 persistence stores no credentials in engineering-state tables.
A70 public list/history ordering is deterministic.
A71 persistence generates no Relay domain IDs.
A72 database migration version remains distinct from model schema_version.
A73 no SQL trigger creates Relay domain events.
A74 no SQL rule duplicates lifecycle transition or gate-policy semantics.
A75 no Slice 0.6 capability is implemented.
```

## Quality / restart

```text
A76 file-backed database survives process close/reopen.
A77 restart loads exact current lifecycle state.
A78 restart preserves exact event chronology.
A79 migration tests operate on file-backed temporary databases.
A80 concurrency tests use at least two real SQLite connections.
A81 full existing quality suite remains green.
A82 no new runtime/dev dependency is introduced.
A83 implementation follows Minimum Sufficient Architecture policy.
```

---

# 46. Required design-review questions

Independent design review must explicitly challenge:

```text
Q1 Is SQLite justified now without overcommitting future production architecture?
Q2 Does the design distinguish materialized state from immutable history clearly enough?
Q3 Can the lifecycle snapshot/event pair ever diverge under the proposed transaction contract?
Q4 Is expected-revision concurrency sufficient for Phase 0?
Q5 Does execute_and_persist_handover preserve the accepted Slice 0.4 anti-forgery boundary?
Q6 Are gate evaluations and execution records sufficiently specified without designing agent execution?
Q7 Are historical records truly append-only through the public API?
Q8 Does migration machinery remain infrastructure rather than domain architecture?
Q9 Is any source-of-truth question improperly pulled forward from Slice 0.6?
Q10 Has any unnecessary ORM/repository/event-sourcing abstraction entered the design?
```

---

# 47. Implementation hard stop

This document opens Slice 0.5 design only.

```text
Design Revision 1: COMPLETE / PENDING INDEPENDENT DESIGN REVIEW
Implementation: NOT AUTHORIZED
Slice 0.6: NOT AUTHORIZED
```

Human Authority must explicitly accept a reviewed design and separately authorize implementation before any `src/relay_engine/persistence` production work begins.

Unblocked does not mean authorized.
