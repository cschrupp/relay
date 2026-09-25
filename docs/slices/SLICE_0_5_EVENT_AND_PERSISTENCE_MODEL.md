# Slice 0.5 — Event and Persistence Model

**Document revision:** 2  
**Status:** REVIEW  
**Document class:** Lockable design record  
**Authority:** Human Authority opened Slice 0.5 design work after formal Slice 0.4 closure; Revision 2 resolves `RLY-S05-DESIGN-EVAL-001` findings F001–F007  
**Baseline SHA:** `c8006306d48624f13599fe448ef677015fd1829e`  
**Revision 1 SHA:** `76ea38b98c218ffc0eab797c03699f45e3d4d951`  
**Implementation authorization:** NOT GRANTED  

---

# 1. Objective

Persist Relay project state without losing historical causality.

Slice 0.5 introduces the first durable runtime-state boundary for Relay while preserving the deterministic semantics accepted in Slices 0.2–0.4.

The persistence model is:

```text
current materialized state
+
immutable historical records
```

Relay does not require full event sourcing in this slice.

The system must be able to restart, recover current runtime state, preserve immutable transition chronology, reject conflicting writes, prove that persisted lifecycle events correspond to persisted lifecycle snapshots, preserve the exact governance basis of persisted executions, and migrate its schema explicitly.

---

# 2. Architectural principle

Persistence is subordinate to accepted domain and governance semantics.

```text
Domain models
    define engineering meaning

Lifecycle / governance engines
    define valid state change

Persistence
    verifies durable facts
    proves stored causality
    stores exact resulting state and immutable evidence atomically
```

Database structure must not redefine lifecycle or governance rules.

No lifecycle transition table, gate policy, authorization semantic, or human-choice rule may be duplicated in SQL.

Persistence may verify that caller-supplied durable facts equal stored durable facts. It must then delegate engineering meaning to the accepted Python domain/lifecycle/governance contracts.

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
- no ORM or cloud-database architecture is justified yet.

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

The implementation may use smaller private helpers when needed, but must not introduce:

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

The public API exposes concrete Relay persistence operations.

---

# 5. S0.5-D03 — Database path and connection creation are explicit

Opening persistence requires an explicit SQLite database target.

Conceptually:

```python
open_database(path, *, apply_migrations: bool, migration_applied_at: datetime | None = None) \
    -> RelayDatabase
```

The exact signature may be decomposed for clarity, but these semantics are required:

- the caller owns the configured database path;
- `:memory:` is permitted for tests;
- connection initialization enables `PRAGMA foreign_keys = ON`;
- ordinary file-backed databases use WAL journal mode unless SQLite rejects it for the selected target;
- persistence does not read application configuration implicitly;
- schema verification can occur without migration application.

---

# 6. S0.5-D04 — Schema migrations are explicit, monotonic, checksummed, and batch-atomic

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

Migration definition conceptually contains:

```python
Migration(
    version: int,
    name: str,
    statements: tuple[str, ...],
)
```

Rules:

```text
versions begin at 1
versions are strictly increasing
migration names are nonblank
statement order is semantic
one version is applied at most once
unknown future database version is rejected
migration checksum mismatch is rejected
all pending migrations execute in version order
```

## 6.1 Normative checksum

For one migration, construct this JSON value:

```json
{
  "name": "<exact name>",
  "statements": ["<statement 1>", "<statement 2>"],
  "version": 1
}
```

Serialize with Python-equivalent semantics:

```python
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

Encode the resulting text as UTF-8 without newline transformation.

Checksum is:

```text
sha256:<lowercase 64-hex SHA-256 digest>
```

The exact migration name and exact ordered SQL statement strings therefore participate in the checksum.

## 6.2 Batch transaction rule

One caller invocation that applies pending migrations owns one transaction covering the complete pending batch requested by that invocation.

Conceptually:

```text
validate all already-applied migration checksums
BEGIN IMMEDIATE
apply pending migration N
insert migration N metadata
apply pending migration N+1
insert migration N+1 metadata
...
COMMIT
```

If any pending migration or migration-record insertion fails:

```text
ROLLBACK
```

and none of the pending migrations from that invocation commits.

Previously committed migration versions remain untouched.

Implementation must not use a helper whose implicit transaction behavior defeats this batch-atomic contract.

Migration timestamps are explicit inputs from the migration caller or one database-open operation; they are infrastructure timestamps, not engineering-domain timestamps.

Database migration version remains separate from model `schema_version`.

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
lifecycle current snapshots
lifecycle events
handover gate revisions
authorization grants
human decisions
gate evaluation records
executions
```

This fulfills the build-plan persistence categories using concepts that have accepted contracts through Slice 0.4 plus the narrow persistence records introduced here.

No table is created for future concepts that still lack an accepted domain contract.

In particular, do not add persistence for:

```text
AgentRole
AgentAssignment
ResearchTask
ResearchFinding
Source
Experiment
```

merely because future phases mention them.

---

# 8. S0.5-D06 — Typed models remain canonical; SQL rows are storage representations

Persisted typed objects are serialized from validated Pydantic models.

Where a table stores a complete object, it stores:

```text
identity/index columns needed for constraints and lookup
schema_version where applicable
canonical JSON payload
```

For Slice 0.5, canonical JSON means:

```python
json.dumps(
    model.model_dump(mode="json"),
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

The exact model type must successfully validate the stored payload before a public load returns it.

SQL rows are not new engineering-domain models.

A generic untyped `metadata` or arbitrary facts column is forbidden.

---

# 9. S0.5-D07 — Duplicated indexed columns are derived and verified

When SQL repeats typed-model values in indexed or constrained columns, the database adapter must not accept those duplicated values independently from the caller.

On write:

```text
validate typed object
↓
derive identity/index columns from that object
↓
serialize canonical payload from that same object
```

Examples include:

```text
gate_id
gate_revision
baseline_id
slice_id
event_id
resulting_revision
```

On read:

```text
load row
↓
validate exact typed payload
↓
verify every duplicated identity/index column
matches the corresponding typed-model field
```

Any mismatch is:

```text
PersistenceIntegrityError
```

Persistence must not silently prefer the SQL column or silently prefer the payload.

This is storage-integrity validation, not a duplicate domain-rule engine.

---

# 10. S0.5-D08 — Current materialized state and immutable history have distinct tables

Current-state tables may be updated only where this design explicitly defines a mutable projection.

Historical tables are append-only through the public persistence API.

At minimum:

```text
lifecycle_current
lifecycle_events

gate_evaluation_records
executions
```

have explicit current/history semantics.

`lifecycle_current` is the materialized current lifecycle snapshot for one slice.

`lifecycle_events` is immutable chronology.

Gate evaluation records and executions are immutable historical evidence.

---

# 11. S0.5-D09 — Lifecycle initialization is a distinct ABSENT → revision 0 transaction

Lifecycle initialization is not modeled as an ordinary expected-revision update because no prior lifecycle revision exists.

Provide an explicit operation conceptually:

```python
persist_lifecycle_initialization(
    initial_lifecycle: SliceLifecycle,
    initialized_event: LifecycleInitialized,
) -> None
```

Inside one write transaction it must verify:

```text
no lifecycle_current row exists for slice
no lifecycle event exists for slice
initial_lifecycle.revision == 0
initialized_event.slice_id == initial_lifecycle.slice_id
initialized_event.resulting_revision == 0
replay_lifecycle((initialized_event,)) == initial_lifecycle
```

Then atomically insert:

```text
lifecycle_current revision 0
+
LifecycleInitialized event revision 0
```

If a complete lifecycle already exists for that slice:

```text
ConcurrencyConflict
```

If only one side exists—for example current snapshot without history or history without current snapshot:

```text
PersistenceIntegrityError
```

Any validation/write failure rolls back the complete initialization.

---

# 12. S0.5-D10 — Every later lifecycle mutation proves event→snapshot correspondence before commit

Every persisted lifecycle mutation after initialization must store, in one database transaction:

```text
new SliceLifecycle snapshot
+
corresponding immutable lifecycle event
```

Atomicity alone is not sufficient.

Before committing, persistence must prove that the candidate event actually produces the candidate snapshot from the current durable history.

Conceptually:

```python
persist_lifecycle_change(
    expected_lifecycle_revision: int,
    updated_lifecycle: SliceLifecycle,
    event: LifecycleEvent,
) -> None
```

Required transaction sequence:

```text
BEGIN IMMEDIATE
load current lifecycle
load ordered lifecycle history
verify expected revision
verify stored history replays to current lifecycle
verify event.slice_id == current.slice_id == updated_lifecycle.slice_id
verify event.resulting_revision == expected_revision + 1
verify updated_lifecycle.revision == expected_revision + 1
candidate_history = stored_history + (event,)
replayed = replay_lifecycle(candidate_history)
require replayed == updated_lifecycle
insert immutable event
update lifecycle_current using expected revision
COMMIT
```

If the current persisted lifecycle revision differs from the expected revision:

```text
ConcurrencyConflict
```

If current durable history does not replay to current durable state, or the candidate event does not replay exactly to the supplied updated lifecycle:

```text
PersistenceIntegrityError
```

No lifecycle snapshot may advance without the exact event that caused it.

No event may commit unless its resulting snapshot becomes the durable current lifecycle in the same transaction.

Persistence must use accepted Slice 0.3 `replay_lifecycle()` semantics; it must not implement a second transition/replay engine.

---

# 13. S0.5-D11 — Optimistic concurrency is the semantic conflict mechanism

SQLite writer locking is an implementation mechanism, not Relay's logical concurrency contract.

For an established lifecycle:

```text
caller observed revision N
caller proposes N → N+1
write succeeds only if persisted revision is still N
```

Two writers starting from revision N cannot both commit revision N+1.

Exactly one may succeed.

The other receives:

```text
ConcurrencyConflict
```

There is no last-write-wins fallback.

Lifecycle initialization has its separate ABSENT→0 rule from S0.5-D09.

---

# 14. S0.5-D12 — Lifecycle events remain Slice 0.3 events

Persistence does not invent replacement event types for accepted lifecycle semantics.

Persist the accepted immutable event union from Slice 0.3:

```text
LifecycleInitialized
PhaseChanged
BlockageChanged
ValidityChanged
```

Event indexing exposes at minimum:

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

# 15. S0.5-D13 — Lifecycle chronology can be reconstructed

Persistence exposes:

```python
load_lifecycle_events(slice_id) -> tuple[LifecycleEvent, ...]
```

ordered by `resulting_revision ASC`.

The loaded event stream must reconstruct current lifecycle using accepted Slice 0.3 `replay_lifecycle()`.

Do not create a second replay implementation in persistence.

---

# 16. S0.5-D14 — Project restart recovery is deterministic

A new process opening an existing database must be able to load:

```text
Project
Baseline
Slice
Artifact
Decision
Evidence
current SliceLifecycle snapshots
stored HandoverGate revisions
AuthorizationGrant records
HumanApprovalDecision records
HumanChoiceDecision records
historical lifecycle events
historical GateEvaluationRecord values
historical ExecutionRecord values
```

No in-memory cache is authoritative.

Restart recovery must not require GitHub, repository scanning, an LLM, or any provider.

---

# 17. S0.5-D15 — Gate definitions are revisioned durable records

Handover gates are persisted by exact:

```text
gate_id
gate_revision
baseline_id
```

A new revision is inserted as a new immutable record.

An old revision is never overwritten.

Persistence may load:

```text
exact revision
latest stored numeric revision for one logical gate
all revisions for one logical gate in revision order
```

"latest stored revision" is a storage query only. It does not establish current project authority or canonical repository truth.

Slice 0.6 still owns repository-side canonical artifact discovery/source-of-truth semantics.

---

# 18. S0.5-D16 — Authorization grants and human decisions are immutable records

Persist exact accepted values:

```text
AuthorizationGrant
HumanApprovalDecision
HumanChoiceDecision
```

by stable ID.

Every insertion is append-only.

A duplicate stable ID is rejected even when the supplied payload is byte-for-byte/model-equal to the existing record.

Duplicate identity is:

```text
PersistenceIntegrityError
```

The database does not infer which historical authority record is current by timestamp.

Callers still construct a `HandoverContext` explicitly; persisted governed execution then verifies the persistence-owned facts in that context as specified below.

Revocation and expiry remain out of scope.

---

# 19. S0.5-D17 — Static Slice-0.2 domain identities are insert-only in Slice 0.5

For this slice, the following accepted domain values use insert-once semantics by stable ID:

```text
Project
Baseline
Slice
Artifact
Decision
Evidence
```

Public operations conceptually are explicit inserts/loads, not generic `save()` or blind UPSERT.

After a stable ID exists, any second insertion of that identity is rejected regardless of payload equality:

```text
PersistenceIntegrityError
```

Slice 0.5 does not invent same-ID revision/update semantics for these frozen accepted models.

If a later slice needs a mutable projection or same-ID revision contract for any of these objects, that behavior requires an explicit accepted design.

`lifecycle_current` remains the principal explicitly mutable engineering projection in Slice 0.5.

Gate logical IDs are a separate accepted case: a logical gate may have multiple immutable `gate_revision` rows under its gate ID.

---

# 20. S0.5-D18 — Persisted governed execution distinguishes durable facts from caller assessment facts

The pure Slice 0.4 engine correctly evaluates explicit supplied facts without persistence.

The Slice 0.5 persisted-execution boundary adds one responsibility:

> Facts that claim to be Relay's own durable state must exactly agree with Relay's durable store before an execution may become durable history.

For persisted governed execution, facts are classified as follows.

## 20.1 Persistence-owned facts

The following supplied values must be checked against durable state before gate evaluation/execution is committed:

```text
all supplied HandoverGate revisions
context.lifecycle
context.dependency_lifecycles
context.authorization_grants
context.human_decisions
context.available_artifact_ids membership
context.available_evidence_ids membership
context.baseline_id existence
```

Rules:

### Gates

Every supplied gate must have an exact stored `(gate_id, gate_revision)` record and the complete stored typed `HandoverGate` payload must equal the supplied gate.

Unknown gate revision or payload mismatch:

```text
PersistenceIntegrityError
```

### Target lifecycle

`context.lifecycle` must equal the current persisted lifecycle for the target slice.

If it differs because the durable lifecycle has advanced from the caller's expected revision:

```text
ConcurrencyConflict
```

If the database itself has inconsistent lifecycle current/history state:

```text
PersistenceIntegrityError
```

### Dependency lifecycle projection

Every supplied dependency lifecycle must equal the current durable lifecycle snapshot for that dependency slice.

A durable dependency lifecycle that has advanced relative to the supplied projection is a stale caller projection and causes:

```text
ConcurrencyConflict
```

A missing durable dependency row or corrupted durable dependency state causes:

```text
PersistenceIntegrityError
```

The persistence layer does not add omitted dependency rows to the context; Slice 0.4 remains responsible for deciding whether required dependency facts are present.

### Authorization grants

Every supplied authorization grant must exist by its stable ID and the complete durable typed payload must equal the supplied record.

Unknown or payload-inconsistent immutable authority:

```text
PersistenceIntegrityError
```

### Human decisions

Every supplied human approval/choice decision must exist by stable ID and complete payload equality.

Unknown or payload-inconsistent decision:

```text
PersistenceIntegrityError
```

### Artifacts and evidence

Every ID listed in `available_artifact_ids` must correspond to a persisted `Artifact` record.

Every ID listed in `available_evidence_ids` must correspond to a persisted `Evidence` record.

Unknown listed ID:

```text
PersistenceIntegrityError
```

Persistence does not automatically add all durable artifact/evidence IDs to the caller's availability projection.

### Baseline

`context.baseline_id` must identify a persisted `Baseline` record.

Missing baseline:

```text
PersistenceIntegrityError
```

## 20.2 Caller-supplied current assessment facts

Slice 0.5 has no accepted independent durable authority source for these HandoverContext values:

```text
governance_revision
evaluation_outcome
quality_checks
change_surface_status
risk_status
toolchain_change_status
```

They remain explicit caller-supplied inputs to Slice 0.4.

They MUST be preserved exactly in the immutable evaluation-basis record for auditability.

Persistence does not recompute or infer them.

---

# 21. S0.5-D19 — Persisted gate evaluation evidence has one mandatory stable record contract

Slice 0.5 introduces two narrow persistence IDs using the existing explicit prefix mechanism:

```text
GateEvaluationRecordId
    geval_<uuid7>

ExecutionId
    exec_<uuid7>
```

Both IDs are caller supplied.

Persistence never calls `new_id()` during a state-changing operation.

A persisted governance evidence record is exactly:

```python
GateEvaluationRecord(
    schema_version,
    id,
    recorded_at,
    gate_refs,
    context,
    evaluations,
)
```

where:

```text
schema_version = 1
id = GateEvaluationRecordId
gate_refs = canonical tuple[GateRevisionRef, ...]
context = exact HandoverContext supplied to evaluation
evaluations = exact canonical tuple[GateEvaluation, ...]
```

`recorded_at` is an explicit caller-supplied aware datetime normalized to UTC. It is persistence evidence time, not a replacement for any engineering-domain timestamp.

## 21.1 Gate-reference invariants

`gate_refs` must:

```text
be non-empty
contain no duplicate gate_id
be sorted by gate_id ascending
contain exactly one GateRevisionRef for every supplied outgoing gate
```

The complete gate definitions remain immutable gate-revision records in persistence.

For persisted governed execution, all referenced gate revisions have already exact-matched durable gate records under S0.5-D18.

## 21.2 Evaluation invariants

`evaluations` must:

```text
be non-empty
be sorted by gate_id ascending
contain exactly one evaluation for each gate_ref
match gate_id and gate_revision exactly
match context baseline_id
match context.lifecycle.revision
match context.governance_revision
```

The record stores the full canonical evaluation tuple, not only the selected gate result.

This preserves HUMAN_CHOICE alternatives and multi-path governance causality.

## 21.3 Persistence does not trust caller-created evaluations

The ordinary public operation for persisted governed execution MUST generate the evaluation tuple by invoking accepted Slice 0.4 `evaluate_handover_gates(gates, context)` inside the orchestration operation.

It does not accept a caller-created `GateEvaluationRecord` as proof of executability.

A lower-level append operation may exist for test fixtures or non-execution evidence only if it validates the record shape; it must not become authority for `execute_and_persist_handover()`.

Gate evaluation records are append-only.

Duplicate record ID:

```text
PersistenceIntegrityError
```

---

# 22. S0.5-D20 — ExecutionRecord is a minimal immutable commit record

Slice 0.5 introduces:

```python
ExecutionRecord(
    schema_version,
    execution_id,
    gate_evaluation_record_id,
    slice_id,
    baseline_id,
    selected_gate_id,
    selected_gate_revision,
    source_lifecycle_revision,
    resulting_lifecycle_revision,
    event_id,
    actor,
    occurred_at,
    reason,
)
```

Required semantics:

```text
schema_version = 1
execution_id = ExecutionId
gate_evaluation_record_id = exact committed GateEvaluationRecordId
reason nonblank
occurred_at timezone-aware and UTC normalized
```

The record means:

> this governed lifecycle handover was evaluated from this immutable basis and committed.

It does not model:

```text
agent runtime
subprocesses
sandboxes
logs
tokens
providers
code-generation execution
```

Those belong to later phases.

Execution records are append-only.

Duplicate execution ID:

```text
PersistenceIntegrityError
```

---

# 23. S0.5-D21 — Persisted governed execution is one transaction and preserves Slice 0.4 anti-forgery semantics

Slice 0.5 provides a persistence orchestration operation around accepted Slice 0.4 evaluation/execution.

Conceptually:

```python
execute_and_persist_handover(
    database,
    gates,
    selected_gate_id,
    context,
    expected_lifecycle_revision,
    evaluation_record_id,
    evaluation_recorded_at,
    execution_id,
    event_id,
    actor,
    occurred_at,
    reason,
) -> tuple[SliceLifecycle, PhaseChanged, GateEvaluation, GateEvaluationRecord, ExecutionRecord]
```

Exact return decomposition may be represented as a typed result value if clearer; semantics are fixed.

Required sequence inside one write transaction:

```text
BEGIN IMMEDIATE

1 load current persisted target lifecycle
2 load/verify target history integrity needed for mutation
3 verify expected lifecycle revision
4 verify supplied context.lifecycle == persisted target lifecycle
5 exact-check every persistence-owned context/gate fact under S0.5-D18
6 evaluations = evaluate_handover_gates(gates, context)
7 call Slice 0.4 execute_handover(...) with the same gates/context and explicit event inputs
8 receive resulting lifecycle + exact lifecycle event + selected GateEvaluation
9 require selected GateEvaluation returned by execute_handover()
  == the corresponding selected result in evaluations
10 construct GateEvaluationRecord from exact gate refs + context + evaluations
11 prove candidate lifecycle event→snapshot correspondence under S0.5-D10
12 insert GateEvaluationRecord
13 insert exact lifecycle event
14 update lifecycle_current using expected revision
15 insert ExecutionRecord referencing GateEvaluationRecord

COMMIT
```

Any failure at any step rolls back every write from the attempted operation.

The deliberate double governance evaluation in steps 6 and 7 is acceptable because Slice 0.4 `execute_handover()` intentionally re-evaluates internally rather than trusting caller-created GREEN evidence. Determinism requires the selected result to match the corresponding result from step 6.

Persistence does not bypass or replace that anti-forgery boundary.

The lifecycle event and resulting lifecycle are the exact values returned through accepted Slice 0.4/0.3 execution.

---

# 24. S0.5-D22 — Persisted execution context mismatch is classified deterministically

For persisted governed execution:

```text
expected target lifecycle revision mismatch
→ ConcurrencyConflict

supplied target lifecycle differs from durable target lifecycle
because durable state advanced
→ ConcurrencyConflict

supplied dependency lifecycle differs because durable dependency advanced
→ ConcurrencyConflict

unknown/mismatched immutable gate, authorization, human decision,
baseline, listed artifact, or listed evidence durable fact
→ PersistenceIntegrityError

current durable lifecycle/history corruption
→ PersistenceIntegrityError
```

Database busy/lock remains a separate operational failure and is not translated to `ConcurrencyConflict`.

---

# 25. S0.5-D23 — Transaction boundaries are explicit

Public multi-record writes own their transaction.

Nested implicit commits are forbidden.

Low-level helpers must not commit independently when used inside a higher-level transaction.

For write transactions:

```text
BEGIN IMMEDIATE
```

is the default SQLite mode so writer contention is detected before state-change work proceeds.

A SQLite lock/busy condition is distinct from an expected-revision conflict.

Automatic write retry is out of scope for Slice 0.5.

---

# 26. S0.5-D24 — Persistence error family is narrow

Introduce exactly:

```text
PersistenceError
├── PersistenceIntegrityError
├── ConcurrencyConflict
├── MigrationError
└── DatabaseUnavailable
```

Expected mappings:

```text
durable data inconsistency / duplicate immutable identity
→ PersistenceIntegrityError

expected-revision or stale durable lifecycle projection
→ ConcurrencyConflict

migration definition/schema/checksum/application problem
→ MigrationError

open/lock/busy/operational database unavailability
→ DatabaseUnavailable
```

Pydantic validation errors may represent malformed caller-constructed persistence record values before database access.

Malformed stored payload encountered during load is durable-data corruption and must surface as `PersistenceIntegrityError`, preserving the underlying validation exception through chaining.

SQLite exceptions must not leak arbitrarily from the public persistence API.

Do not build a larger exception taxonomy.

---

# 27. S0.5-D25 — No credentials or secrets in engineering-state tables

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

# 28. S0.5-D26 — Time semantics remain explicit

Engineering timestamps are supplied by accepted domain/governance operations.

The database must not replace them with `CURRENT_TIMESTAMP` as engineering truth.

Infrastructure-only timestamps such as:

```text
migration applied_at
GateEvaluationRecord.recorded_at
```

are explicit caller inputs to their operation and never substitute for:

```text
occurred_at
granted_at
human decision occurred_at
lifecycle updated_at
```

All serialized datetime values round-trip as timezone-aware UTC-normalized values.

---

# 29. S0.5-D27 — IDs are caller supplied

Persistence generates no Relay domain/governance/persistence-record IDs.

Use the existing explicit ID mechanism, narrowly extended with:

```text
geval_
exec_
```

for `GateEvaluationRecordId` and `ExecutionId`.

The persistence engine itself does not call `new_id()` during state-changing operations.

Migration row identity is infrastructure state and does not use Relay IDs.

---

# 30. S0.5-D28 — Database integrity constraints support, but do not replace, domain validation

Use database constraints for structural storage invariants such as:

```text
primary keys
unique IDs
foreign keys where safe
unique event revisions
non-null required storage columns
```

Do not encode the Relay lifecycle transition matrix, gate policy, authorization semantics, or HUMAN_CHOICE rules as SQL CHECK constraints or triggers.

Pydantic/domain/lifecycle/governance engines remain authoritative for engineering semantics.

---

# 31. S0.5-D29 — No database triggers for domain events

Lifecycle events are inserted explicitly by the Python transaction that performed the accepted transition.

No SQL trigger may synthesize Relay domain events or gate evaluations.

Domain causality must remain visible in the Python contract.

---

# 32. S0.5-D30 — Historical records are immutable through public API

The public persistence API provides no update/delete operation for:

```text
lifecycle events
gate evaluation records
execution records
gate revisions
authorization grants
human decisions
```

Test-only direct SQL mutation may construct corruption fixtures.

Production API does not expose historical rewriting.

---

# 33. S0.5-D31 — Database schema version and model schema_version are separate

Do not conflate:

```text
SQLite database migration version
```

with:

```text
Domain/PersistenceRecord model schema_version
```

Database migration changes physical storage.

Model schema version identifies serialized typed contract.

Both remain independently inspectable.

---

# 34. S0.5-D32 — Startup compatibility checks are deterministic

Opening/verifying a database rejects:

```text
future unsupported database schema version
applied migration checksum mismatch
required table/index absence after declared migration version
malformed stored model payload when loaded/verified
indexed-column / payload mismatch when loaded/verified
```

Opening may apply known pending migrations only when explicitly requested.

The API supports verification without applying migrations.

---

# 35. S0.5-D33 — Backup/restore and distributed replication are out of scope

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

SQLite-safe file-copy practice is an operational concern, not a Relay Slice 0.5 product contract.

---

# 36. S0.5-D34 — Repository synchronization remains Slice 0.6+

Slice 0.5 persists Relay runtime state.

It does not decide whether a database row or repository artifact is canonical when both exist.

That source-of-truth and `.relay/` contract remains Slice 0.6.

Slice 0.5 must not:

```text
scan repository files
write .relay/
resolve canonical document paths
infer artifact canonicality from Git
synchronize database state with repository state
```

---

# 37. S0.5-D35 — Persistence does not add an API/service layer

No REST server, CLI workflow, UI, background worker, or message queue is required.

Tests and future callers invoke persistence directly as Python library operations.

---

# 38. S0.5-D36 — Persistence does not authenticate humans

Persisted `ActorRef` values are historical engineering facts supplied by callers.

Slice 0.5 does not introduce identity verification, user accounts, RBAC, sessions, or authentication.

---

# 39. S0.5-D37 — Deterministic read ordering is explicit

All public list/history operations define stable ordering.

Required examples:

```text
lifecycle events
→ resulting_revision ASC

gate revisions
→ gate_revision ASC

gate evaluation records
→ infrastructure persistence sequence ASC, then record_id

executions
→ resulting_lifecycle_revision ASC, then execution_id
```

No caller-visible ordering may depend on incidental SQLite row order.

---

# 40. S0.5-D38 — Persistence sequence may be infrastructure-local

Historical evidence tables may use an internal monotonic integer primary key for stable insertion ordering.

Such a sequence:

```text
is not a Relay domain ID
is not authority
is not a semantic revision
```

It exists only to provide deterministic storage ordering where no natural engineering sequence exists.

---

# 41. S0.5-D39 — Corruption is surfaced, not silently repaired

If durable current lifecycle, event history, typed payload, or duplicated indexed columns disagree, persistence raises:

```text
PersistenceIntegrityError
```

when that data is loaded or explicitly verified.

Persistence must not:

```text
silently rewrite current state
silently delete events
silently regenerate events
silently repair payloads
pick one duplicate representation arbitrarily
```

Repair tooling is out of scope.

---

# 42. S0.5-D40 — Integrity verification is a public read-only operation

Provide a deterministic operation conceptually:

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

It performs no writes.

Database/schema verification separately checks migration/schema/storage contracts from S0.5-D32.

---

# 43. S0.5-D41 — Persistence tests use real SQLite

Core persistence tests exercise actual SQLite connections, not mocked repositories.

Required modes:

```text
:memory: for isolated unit tests
file-backed temporary database for restart/migration tests
multiple connections to one file-backed temporary database for concurrency tests
direct SQL corruption fixtures where needed to test integrity rejection
```

No external database service is required in CI.

---

# 44. S0.5-D42 — Existing accepted behavior remains database-independent

Slice 0.2 domain, Slice 0.3 lifecycle, and Slice 0.4 governance APIs continue to work without a database.

Persistence is additive.

Pure lifecycle/governance tests must not require SQLite setup.

---

# 45. S0.5-D43 — Persistence-owned validation does not become source-of-truth inference

When persisted governed execution checks durable facts, it verifies only explicit references already supplied by the caller.

It must not infer a HandoverContext by scanning all stored records, selecting the newest human decision, selecting the newest authorization, or assembling canonical gate sets by timestamp.

In particular:

```text
current authority selection remains explicit
current human-decision selection remains explicit
governance_revision remains caller-maintained
gate set remains caller-supplied
```

Slice 0.5 verifies that those explicitly supplied durable facts really exist and match durable state.

This prevents persistence from quietly becoming a second governance engine.

---

# 46. Expected implementation surface

Expected narrow existing modifications:

```text
src/relay_engine/domain/ids.py
src/relay_engine/domain/__init__.py
```

only for:

```text
GateEvaluationRecordId / geval_
ExecutionId / exec_
```

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

Expected tests:

```text
tests/unit/test_persistence_models.py
tests/integration/test_persistence_sqlite.py
```

Implementation documentation, only after separate implementation authorization, may add:

```text
docs/architecture/PERSISTENCE_MODEL.md
docs/decisions/ADR-0005-sqlite-phase0-persistence.md
docs/slices/SLICE_0_5_EVENT_PERSISTENCE_MEMORY.md
```

No implementation file listed here is authorized by this design revision.

---

# 47. Explicitly out of scope

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
generic Evaluation aggregate
research / experiments
Slice 0.6 implementation
```

---

# 48. Acceptance criteria

All criteria are mandatory unless explicitly stated otherwise.

## Core backend and migration

```text
A01 SQLite is the only Slice 0.5 backend.
A02 Slice 0.5 adds no runtime dependency.
A03 database target is explicit.
A04 foreign keys are enabled.
A05 migrations are ordered and monotonic.
A06 applied migrations record version/name/checksum/time.
A07 migration checksum mismatch is rejected.
A08 unsupported future schema version is rejected.
A09 one apply-migrations call applies all requested pending migrations atomically.
A10 schema can be verified without applying migrations.
```

## Persistence categories and typed round-trip

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
A23 GateEvaluationRecord values round-trip.
A24 ExecutionRecord values round-trip.
A25 malformed stored model payload is rejected as PersistenceIntegrityError.
```

## Lifecycle causality

```text
A26 established lifecycle update and event append commit atomically.
A27 rollback leaves neither partial snapshot nor candidate event.
A28 event IDs are unique.
A29 one slice cannot have two events for one resulting revision.
A30 event history is returned in resulting-revision order.
A31 replay of stored events reproduces stored current lifecycle.
A32 verify_slice_history is read-only.
A33 history mismatch raises PersistenceIntegrityError.
```

## Concurrency

```text
A34 established lifecycle mutation requires expected revision.
A35 expected-revision mismatch raises ConcurrencyConflict.
A36 two writers from the same revision cannot both commit.
A37 no last-write-wins fallback exists.
A38 persisted-execution target lifecycle must equal durable current lifecycle.
A39 database lock/busy is not reported as ConcurrencyConflict.
A40 no automatic write retry occurs.
```

## Governance persistence

```text
A41 gate revisions are immutable historical rows.
A42 same gate ID may persist multiple explicit revisions.
A43 authorization grants are append-only records.
A44 human decisions are append-only records.
A45 GateEvaluationRecord values are append-only evidence.
A46 persistence does not treat a caller-created evaluation as execution authority.
A47 persistence does not infer current authority by timestamp.
```

## Governed execution

```text
A48 execute_and_persist_handover loads current persisted target lifecycle.
A49 it verifies expected revision before commit.
A50 it invokes Slice 0.4 evaluate_handover_gates() for the full canonical result tuple.
A51 it delegates executable authority to Slice 0.4 execute_handover().
A52 it persists the exact lifecycle event returned through Slice 0.4/0.3.
A53 it persists the exact resulting lifecycle snapshot.
A54 it persists exactly one GateEvaluationRecord.
A55 it persists exactly one ExecutionRecord referencing that evaluation record.
A56 all records from one governed execution commit in one transaction.
A57 any failure rolls back every write from the attempted execution.
```

## Historical immutability

```text
A58 public API has no historical lifecycle-event update/delete.
A59 public API has no gate-evaluation-record update/delete.
A60 public API has no execution-record update/delete.
A61 public API has no gate-revision update-in-place.
A62 public API has no authorization-grant update/delete.
A63 public API has no human-decision update/delete.
```

## Scope and deterministic behavior

```text
A64 existing lifecycle/governance pure APIs remain database-independent.
A65 persistence performs no Git/GitHub lookup.
A66 persistence performs no LLM/provider call.
A67 persistence performs no repository artifact discovery.
A68 persistence performs no notification.
A69 persistence stores no credentials in engineering-state tables.
A70 public list/history ordering is deterministic.
A71 persistence generates no Relay IDs.
A72 database migration version remains distinct from model schema_version.
A73 no SQL trigger creates Relay domain events or gate evaluations.
A74 no SQL rule duplicates lifecycle transition or gate-policy semantics.
A75 no Slice 0.6 capability is implemented.
```

## Quality / restart

```text
A76 file-backed database survives close/reopen.
A77 restart loads exact current lifecycle state.
A78 restart preserves exact event chronology.
A79 migration tests operate on file-backed temporary databases.
A80 concurrency tests use at least two real SQLite connections.
A81 full existing quality suite remains green.
A82 no new runtime/dev dependency is introduced.
A83 implementation follows Minimum Sufficient Architecture policy.
```

## Revision-2 causality / audit / integrity hardening

```text
A84 established lifecycle change is rejected unless stored history plus candidate event replays exactly to supplied new snapshot.
A85 lifecycle initialization requires exact ABSENT → revision 0 initialization semantics and atomic LifecycleInitialized/current insertion.
A86 persisted execution exact-matches every supplied gate revision against the corresponding durable gate record.
A87 persisted execution exact-matches supplied AuthorizationGrant and human-decision records against durable immutable records.
A88 every supplied dependency lifecycle equals that dependency's current durable lifecycle snapshot before persisted execution.
A89 every listed available Artifact/Evidence ID exists durably and context.baseline_id identifies a durable Baseline.
A90 every persisted governance evaluation basis has a mandatory caller-supplied GateEvaluationRecordId.
A91 GateEvaluationRecord preserves the exact canonical outgoing GateRevisionRef set, exact HandoverContext, and exact canonical GateEvaluation tuple.
A92 every ExecutionRecord references exactly one committed GateEvaluationRecord by ID.
A93 the selected GateEvaluation returned by execute_handover equals the selected evaluation in the persisted GateEvaluationRecord.
A94 Project, Baseline, Slice, Artifact, Decision, and Evidence identities are insert-only in Slice 0.5; duplicate stable identity is rejected.
A95 migration checksum is the normative SHA-256 of the defined canonical UTF-8 migration JSON representation.
A96 one apply-migrations invocation is atomic across all pending migrations requested by that invocation.
A97 duplicated indexed/storage columns are derived from validated typed payloads on write and verified against those payloads on load.
```

---

# 49. Required named regression scenarios

Implementation tests must include coverage equivalent to:

```text
test_lifecycle_write_rejects_event_snapshot_mismatch

test_lifecycle_initialization_persists_revision_zero_atomically

test_duplicate_lifecycle_initialization_conflicts

test_partial_initialization_state_is_integrity_error

test_persisted_execution_rejects_unpersisted_gate_revision

test_persisted_execution_rejects_gate_payload_mismatch

test_persisted_execution_rejects_unpersisted_authorization

test_persisted_execution_rejects_authorization_payload_mismatch

test_persisted_execution_rejects_unpersisted_human_decision

test_persisted_execution_rejects_human_decision_payload_mismatch

test_persisted_execution_rejects_stale_dependency_projection

test_persisted_execution_rejects_unknown_available_artifact

test_persisted_execution_rejects_unknown_available_evidence

test_persisted_execution_rejects_unknown_baseline

test_evaluation_record_preserves_exact_context

test_evaluation_record_preserves_exact_gate_set

test_evaluation_record_preserves_full_canonical_evaluation_tuple

test_execution_references_exact_evaluation_record

test_execution_selected_evaluation_matches_evidence_record

test_duplicate_static_domain_identity_is_rejected

test_migration_checksum_is_stable

test_migration_checksum_changes_with_statement_order_or_content

test_pending_migration_batch_rolls_back_as_one_unit

test_index_column_payload_mismatch_is_integrity_error
```

Existing Revision-1 tests implied by A01–A83 remain mandatory where compatible.

---

# 50. Revision-1 independent-review findings resolved in Revision 2

Independent design review:

```text
RLY-S05-DESIGN-EVAL-001 — REVISE
```

## F001 — lifecycle event/snapshot correspondence

Resolved by S0.5-D10.

Every established lifecycle mutation now proves through accepted `replay_lifecycle()` that durable history plus the candidate event equals the supplied candidate snapshot before committing.

## F002 — lifecycle initialization

Resolved by S0.5-D09.

Initialization is a distinct ABSENT→0 atomic operation with exact `LifecycleInitialized` and replay requirements.

## F003 — persisted execution trusts unverified caller state

Resolved by S0.5-D18 and S0.5-D43.

Durable caller-supplied gates, lifecycle projections, authorization grants, human decisions, baseline, artifacts, and evidence are verified against durable state before execution may commit. Persistence does not infer the context.

## F004 — evaluation evidence basis/identity

Resolved by S0.5-D19 through S0.5-D21.

`GateEvaluationRecordId` is mandatory, `GateEvaluationRecord` stores the exact gate-revision set, exact HandoverContext and full canonical evaluation tuple, and `ExecutionRecord` references exactly one such record.

## F005 — static domain identity semantics

Resolved by S0.5-D17.

Accepted Slice-0.2 domain identities are insert-once for Slice 0.5; no generic save/upsert behavior exists.

## F006 — migration checksum and transaction boundary

Resolved by S0.5-D04.

Checksum framing/serialization/SHA-256 are normative and one apply-migrations invocation owns one transaction covering its entire pending batch.

## F007 — indexed column/payload consistency

Resolved by S0.5-D07.

Duplicated columns are derived from the typed object on write and verified against the typed payload on read; mismatch is an integrity error.

No foundational architecture from Revision 1 was changed.

---

# 51. Independent design-review questions for Revision 2

The next independent review should explicitly determine:

```text
Q1 Does event→snapshot proof prevent public persistence APIs from creating internally inconsistent lifecycle history?

Q2 Is ABSENT→0 initialization fully distinct from ordinary optimistic-concurrency updates?

Q3 Are persistence-owned HandoverContext/gate facts defined narrowly enough to prevent fabricated durable authority without turning persistence into governance?

Q4 Does GateEvaluationRecord preserve enough basis to audit HUMAN_CHOICE, hard-stop and multiple-path outcomes after restart?

Q5 Does the deliberate evaluate_handover_gates + execute_handover re-evaluation preserve Slice 0.4 anti-forgery semantics cleanly?

Q6 Are insert-only Slice-0.2 identity semantics safe and sufficiently conservative for this slice?

Q7 Is the migration checksum/batch transaction contract deterministic across implementations?

Q8 Are duplicated SQL columns and typed payloads protected against divergence?

Q9 Has any repository-canonical/source-of-truth behavior leaked forward from Slice 0.6?

Q10 Has Revision 2 introduced any abstraction not required by current accepted requirements?
```

---

# 52. Implementation hard stop

This document remains design only.

```text
Design Revision 2:
COMPLETE / PENDING INDEPENDENT DESIGN REVIEW

Implementation:
NOT AUTHORIZED

Slice 0.6:
NOT AUTHORIZED
```

Human Authority must explicitly accept a reviewed design and separately authorize implementation before any `src/relay_engine/persistence` production work begins.

Unblocked does not mean authorized.
