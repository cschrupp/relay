# Relay Slice 0.3 — State Machine and Lifecycle Semantics

**Slice:** 0.3  
**Phase:** 0 — Protocol and Deterministic Foundation  
**Status:** PROPOSED FOR DESIGN REVIEW  
**Document class:** Lockable record  
**Artifact state:** REVIEW  
**Document revision:** 4  
**Parent:** *Relay — Build Plan and Development Roadmap v0.1*  
**Depends on:** Slice 0.2 — Core Domain Model  
**Prior implementation authorization:** `RLY-S03-AUTH-001` — GRANTED AGAINST REVISION 3  
**Execution state:** BLOCKED pending Revision 4 design acceptance and authorization revalidation

---

# 1. Objective

Define Relay's authoritative structural lifecycle semantics for a development slice.

Slice 0.3 answers:

> Where is the work in its engineering lifecycle?

while deliberately separating that question from:

> Is the work authorized?

> Is the work blocked?

> Is the work stale?

> Is an outgoing handover behind a hard stop?

The deterministic exit condition is:

> Given the same lifecycle snapshot and the same complete operation inputs, Relay produces the same valid next snapshot and the same immutable lifecycle event—or rejects the operation with the same lifecycle error category.

A **complete operation input** includes every value that appears in the resulting event, including `event_id`, `actor`, `occurred_at`, and `reason`.

No LLM participates in lifecycle execution.

---

# 2. Central Design Decision

Relay does not use a flat status enum containing unrelated concepts such as:

```text
READY
AUTHORIZED
BLOCKED
STALE
HARD_STOP
IMPLEMENTING
```

Lifecycle truth is decomposed as:

```text
                 Slice lifecycle

                      PHASE
                        │
             ┌──────────┴─────────┐
             │                    │
          VALIDITY             BLOCKAGE
             │                    │
       CURRENT / STALE       CLEAR / BLOCKED
```

Separate governance owns:

```text
AUTHORIZATION
HANDOVER POLICY
HARD STOP
TRAFFIC LIGHT
```

The governing invariant remains:

> **Lifecycle truth and transition permission are different things.**

---

# 3. S0.3-D01 — Lifecycle Phase

The authoritative lifecycle phase enum is:

```text
PROPOSED
DEFINING
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
READY
IMPLEMENTING
EVALUATING
REWORK
ACCEPTED
SUPERSEDED
CANCELLED
```

Meanings:

- `PROPOSED` — work exists but is not yet sufficiently defined.
- `DEFINING` — objective, boundaries, value, success criteria, and non-goals are being established or revised.
- `RESEARCHING` — evidence needed for the current engineering question is being gathered.
- `DESIGNING` — architecture or technical design is being developed or revised.
- `CONTRACTING` — APIs, invariants, failure semantics, implementation boundaries, and acceptance expectations are being made explicit.
- `PLANNING` — accepted engineering intent is being decomposed into executable work.
- `READY` — required preparation is complete and the slice is waiting to proceed toward implementation.
- `IMPLEMENTING` — an implementation attempt is active.
- `EVALUATING` — an implementation result is under independent assessment.
- `REWORK` — an implementation-level correction is active without invalidating accepted upstream architecture or contract.
- `ACCEPTED` — the slice historically satisfied its acceptance process.
- `SUPERSEDED` — the accepted result has been explicitly replaced by later authoritative work.
- `CANCELLED` — work was deliberately terminated without acceptance.

---

# 4. S0.3-D02 — READY Is a Real Phase

`READY` is a primary lifecycle phase:

```text
engineering preparation complete
        ↓
READY
        ↓
waiting for permission / execution capacity
```

`READY` does not imply authorization.

---

# 5. S0.3-D03 — AUTHORIZED Is Not a Phase

There is no `LifecyclePhase.AUTHORIZED`.

Authorization is a permission relationship, not engineering progress.

A future governance layer may observe:

```text
phase = READY
authorization = GRANTED
```

but the lifecycle remains `READY` until implementation actually starts.

The future board may project this combination as an `AUTHORIZED` lane. That projection does not alter the underlying phase.

---

# 6. S0.3-D04 — BLOCKED Is Orthogonal

`BLOCKED` is not a lifecycle phase.

A slice may be blocked while in:

```text
DEFINING
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
READY
IMPLEMENTING
EVALUATING
REWORK
```

`PROPOSED`, `ACCEPTED`, `SUPERSEDED`, and `CANCELLED` cannot carry `BLOCKED` blockage.

---

# 7. S0.3-D05 — STALE Is Orthogonal

Lifecycle validity is:

```text
CURRENT
STALE
```

`STALE` means:

> Validity against the currently authoritative upstream context has not been established.

It does not mean the historical result was wrong.

Therefore:

```text
phase = ACCEPTED
validity = STALE
```

is valid.

---

# 8. S0.3-D06 — HARD STOP Is Not Lifecycle State

There is no `LifecyclePhase.HARD_STOP`.

A Hard Stop governs an outgoing handover. It belongs to Slice 0.4.

An accepted slice remains `ACCEPTED` while an outgoing handover may independently be under a hard stop.

---

# 9. S0.3-D07 — Separate Lifecycle Snapshot

Slice 0.2 deliberately keeps workflow state out of `Slice`.

Slice 0.3 introduces a separate immutable serialized model:

```python
SliceLifecycle(
    schema_version,
    slice_id,
    phase,
    validity,
    blockage,
    revision,
    updated_at,
    superseded_by_slice_id,
)
```

Normative field semantics:

```text
schema_version = 1
slice_id = existing SliceId
revision >= 0
updated_at = timezone-aware and UTC-normalized
superseded_by_slice_id = SliceId | None
```

`SliceLifecycle` follows the established Slice 0.2 serialized-model discipline:

```text
immutable
extra fields forbidden
schema_version fixed at 1
JSON-compatible serialization
JSON round trip
JSON Schema generation
```

Structural model invariants:

```text
blockage == BLOCKED
    → phase is one of DEFINING..REWORK allowed blockage phases

phase in {PROPOSED, ACCEPTED, SUPERSEDED, CANCELLED}
    → blockage == CLEAR

phase == SUPERSEDED
    → superseded_by_slice_id is required

phase != SUPERSEDED
    → superseded_by_slice_id must be None

superseded_by_slice_id != slice_id
```

The model enforces structural validity. The state engine additionally enforces legal movement between valid snapshots.

---

# 10. S0.3-D08 — Lifecycle Is Immutable

Lifecycle operations never mutate an existing snapshot.

```text
old snapshot
     ↓
pure state engine
     ↓
new snapshot
+
immutable event
```

Every successful state-changing operation after initialization increments `revision` by exactly one.

Initialization creates revision `0`.

---

# 11. S0.3-D09 — Explicit Phase Transition Matrix

Legal phase transitions are represented by an explicit transition table. Legality must never be inferred from enum ordering.

The authoritative matrix is:

| From | Allowed targets |
|---|---|
| `PROPOSED` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `READY`, `CANCELLED` |
| `DEFINING` | `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `READY`, `CANCELLED` |
| `RESEARCHING` | `DEFINING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `READY`, `CANCELLED` |
| `DESIGNING` | `DEFINING`, `RESEARCHING`, `CONTRACTING`, `PLANNING`, `READY`, `CANCELLED` |
| `CONTRACTING` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `PLANNING`, `READY`, `CANCELLED` |
| `PLANNING` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `READY`, `CANCELLED` |
| `READY` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `IMPLEMENTING`, `CANCELLED` |
| `IMPLEMENTING` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `EVALUATING`, `CANCELLED` |
| `EVALUATING` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `REWORK`, `ACCEPTED`, `CANCELLED` |
| `REWORK` | `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, `PLANNING`, `EVALUATING`, `CANCELLED` |
| `ACCEPTED` | `SUPERSEDED` |
| `SUPERSEDED` | none |
| `CANCELLED` | none |

Definition-level escalation is deliberately direct. Relay must not fabricate a false `RESEARCHING` event merely to route later work back to `DEFINING`.

Structural consequences:

```text
READY is the only source of IMPLEMENTING.

IMPLEMENTING and REWORK are the only sources of EVALUATING.

EVALUATING is the only source of ACCEPTED.

IMPLEMENTING → ACCEPTED is invalid.

REWORK → ACCEPTED is invalid.

ACCEPTED never returns to REWORK or an active phase.

ACCEPTED is replaced only through explicit supersession.
```

---

# 12. S0.3-D10 — Every Operation Requires an Explicit Reason

Every successful event-producing lifecycle operation receives an explicit non-empty, non-whitespace `reason`.

This applies to:

```text
initialization
phase transition
set blocked
clear blockage
mark stale
revalidate
```

Relay never relies only on transition direction to explain engineering history.

---

# 13. S0.3-D11 — State Engine Is Pure

The lifecycle engine performs no:

```text
database access
Git access
GitHub calls
HTTP calls
model/LLM calls
filesystem access
clock access
randomness / UUID generation
```

The caller supplies all nondeterministic/external values before invoking the engine.

Conceptually:

```text
current lifecycle
+
complete operation input
        ↓
pure lifecycle engine
        ↓
new lifecycle
+
event
```

or a typed lifecycle error.

---

# 14. S0.3-D12 — Explicit Event Identity and Determinism

Lifecycle events use:

```text
evt_<uuid7>
```

through the existing Slice 0.2 identifier mechanism.

Slice 0.3 narrowly extends the accepted ID vocabulary with:

```text
EventId
evt_
```

and extends `new_id()` to allow `new_id("evt_")`.

This is an authorized narrow extension of the existing ID mechanism, not a new ID framework.

Critically:

> The lifecycle engine does not generate event IDs.

Every event-producing operation receives `event_id` explicitly.

Thus identical snapshots plus identical complete operation inputs—including the same `event_id`—produce identical output.

---

# 15. S0.3-D13 — Operation Context and Time

Every event-producing operation receives:

```text
event_id: EventId
actor: ActorRef
occurred_at: timezone-aware datetime
reason: non-empty string
```

`occurred_at` is UTC-normalized.

Initialization:

```text
updated_at = occurred_at
revision = 0
```

Every successful later operation:

```text
updated_at = occurred_at
revision = prior revision + 1
```

Timestamp regression is invalid:

```text
occurred_at < current.updated_at
    → InvalidLifecycleOperation
```

Equal timestamps are allowed. Revision establishes authoritative event ordering.

Rejected operations do not change revision or `updated_at` and produce no event.

---

# 16. S0.3-D14 — Blockage Model

```text
BlockageStatus

CLEAR
BLOCKED
```

`BlockReason` contains:

```text
code
summary
```

Normative validation:

```text
code pattern: ^[A-Z][A-Z0-9_]*$
summary: non-empty / non-whitespace
```

`Blockage` contains:

```text
status: BlockageStatus
reasons: ordered immutable tuple[BlockReason, ...]
```

Invariants:

```text
CLEAR   → zero reasons
BLOCKED → one or more reasons
```

Duplicate identical `BlockReason` values are rejected.

Caller order is preserved.

Blockage equality is structural ordered equality.

No blocker registry is introduced.

## set_blocked

`set_blocked(reasons, ...)` is allowed only while phase is one of:

```text
DEFINING
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
READY
IMPLEMENTING
EVALUATING
REWORK
```

It may change:

```text
CLEAR → BLOCKED
BLOCKED → BLOCKED with different reasons
```

Supplying the identical current ordered blockage is a semantic no-op and is rejected.

## clear_blockage

`clear_blockage(...)` requires current blockage `BLOCKED`.

`CLEAR → CLEAR` is a semantic no-op and is rejected.

## Blocked phase restrictions

While blocked, phase transition into:

```text
IMPLEMENTING
EVALUATING
ACCEPTED
```

is rejected until blockage is cleared.

Blocked work may move to a structurally legal remediation phase such as `DEFINING`, `RESEARCHING`, `DESIGNING`, `CONTRACTING`, or `PLANNING`, preserving its blockage.

---

# 17. S0.3-D15 — Cancellation Normalizes Blockage

A blocked active slice may transition to `CANCELLED`.

Cancellation is terminal and atomically produces:

```text
phase = CANCELLED
blockage = CLEAR
```

The prior blocker history remains represented by preceding lifecycle events.

Cancellation emits exactly one `PhaseChanged` event and increments revision exactly once.

No synthetic `BlockageChanged` event is emitted for cancellation normalization.

Validity is preserved unchanged by cancellation.

Replay applies this same deterministic normalization.

---

# 18. S0.3-D16 — Validity Operations

Lifecycle supports:

```text
mark_stale(...)
revalidate(...)
```

Allowed state changes:

```text
CURRENT → STALE
STALE → CURRENT
```

`mark_stale` and `revalidate` preserve phase and blockage.

Semantic no-ops are rejected:

```text
STALE → STALE
CURRENT → CURRENT
```

`SUPERSEDED` and `CANCELLED` reject validity operations.

`ACCEPTED` permits validity operations, so both are valid:

```text
ACCEPTED / CURRENT
ACCEPTED / STALE
```

When validity is `STALE`, transition into:

```text
IMPLEMENTING
ACCEPTED
```

is rejected until revalidation.

Other structurally legal transitions remain possible while stale.

---

# 19. S0.3-D17 — Supersession Successor Is Part of Lifecycle State

`ACCEPTED → SUPERSEDED` requires explicit:

```text
superseded_by_slice_id: SliceId
```

The successor must not equal the current `slice_id`.

The resulting snapshot stores that reference:

```text
phase = SUPERSEDED
superseded_by_slice_id = <successor>
```

All non-`SUPERSEDED` snapshots require:

```text
superseded_by_slice_id = None
```

Cross-record existence, project membership, and acceptance of the successor are not checked in Slice 0.3; those require higher-level governance/context.

Supersession preserves current validity and requires clear blockage because `ACCEPTED` cannot be blocked.

---

# 20. S0.3-D18 — No Silent No-Ops

Every semantic no-op is rejected with:

```text
InvalidLifecycleOperation
```

No event is produced.

Revision and `updated_at` remain unchanged.

This includes at minimum:

```text
phase X → phase X
CURRENT → CURRENT
STALE → STALE
CLEAR → CLEAR
set_blocked(existing identical ordered blockage)
```

Silent successful no-ops are forbidden.

---

# 21. S0.3-D19 — Lifecycle Events

Every successful lifecycle operation produces exactly one immutable event.

Event categories are:

```text
LifecycleInitialized
PhaseChanged
BlockageChanged
ValidityChanged
```

All event models follow the accepted serialized-model discipline:

```text
immutable
schema_version = 1
extra fields forbidden
JSON-compatible serialization
JSON round trip
JSON Schema generation
```

Common event fields:

```text
schema_version
event_id
slice_id
actor
occurred_at
reason
resulting_revision
```

Common validation:

```text
event_id is EventId
event_id supplied explicitly
actor is ActorRef
occurred_at timezone-aware and UTC-normalized
reason non-empty / non-whitespace
resulting_revision >= 0
```

## LifecycleInitialized

Initialization event has:

```text
resulting_revision = 0
```

It deterministically represents initialization to:

```text
phase = PROPOSED
validity = CURRENT
blockage = CLEAR
revision = 0
updated_at = occurred_at
superseded_by_slice_id = None
```

## PhaseChanged

Additional fields:

```text
from_phase
to_phase
superseded_by_slice_id: SliceId | None
```

Rules:

```text
to_phase == SUPERSEDED
    → superseded_by_slice_id required

otherwise
    → superseded_by_slice_id must be None
```

Cancellation blockage normalization is derived deterministically from `to_phase == CANCELLED` and the prior snapshot; it does not require a second event.

## BlockageChanged

Additional fields:

```text
before: Blockage
after: Blockage
```

`before != after` is required.

## ValidityChanged

Additional fields:

```text
before: LifecycleValidity
after: LifecycleValidity
```

`before != after` is required.

---

# 22. S0.3-D20 — Initialization

Public initialization operation:

```text
initialize_lifecycle(
    slice_id,
    event_id,
    actor,
    occurred_at,
    reason,
)
```

produces:

```text
SliceLifecycle(
    slice_id = slice_id,
    phase = PROPOSED,
    validity = CURRENT,
    blockage = CLEAR,
    revision = 0,
    updated_at = occurred_at,
    superseded_by_slice_id = None,
)
```

plus one `LifecycleInitialized` event.

Initialization performs no external lookup and does not check whether `slice_id` exists in storage.

---

# 23. Public Lifecycle Operations

The required public capability is conceptually:

```python
initialize_lifecycle(...)
transition_phase(...)
set_blocked(...)
clear_blockage(...)
mark_stale(...)
revalidate(...)
replay_lifecycle(...)
```

Exact private helper/module decomposition is implementation discretion.

Every event-producing operation other than replay receives explicit:

```text
event_id
actor
occurred_at
reason
```

`transition_phase()` additionally receives:

```text
target_phase
superseded_by_slice_id when target is SUPERSEDED
```

`set_blocked()` additionally receives the ordered blocker reasons.

The engine validates structural lifecycle rules only. It does not validate authorization or external prerequisites.

---

# 24. Lifecycle Errors

The public error family is:

```text
LifecycleError
├── InvalidPhaseTransition
├── InvalidLifecycleOperation
└── LifecycleReplayError
```

Semantics:

- `InvalidPhaseTransition` — requested source/target phase movement is not structurally legal or is forbidden by current blockage/validity constraints.
- `InvalidLifecycleOperation` — non-phase operation is invalid, operation context is invalid, or the request is a semantic no-op.
- `LifecycleReplayError` — recorded history is internally inconsistent or cannot be deterministically replayed.

Pydantic/schema validation remains responsible for malformed individual serialized model values. The lifecycle errors govern validly shaped values used in invalid lifecycle operations/history.

No broader exception hierarchy is required in this slice.

---

# 25. S0.3-D21 — Strict Event Replay

`replay_lifecycle(events)` reconstructs a lifecycle snapshot from an ordered non-empty sequence of lifecycle events.

Replay is pure. It does not generate IDs, timestamps, events, or external data.

The first event must be exactly one `LifecycleInitialized` event with:

```text
resulting_revision = 0
```

All later events must use the same `slice_id` and increment resulting revision exactly once.

Replay must reject at minimum:

```text
empty history
missing initialization
duplicate initialization
duplicate event_id
event for wrong slice
revision gap
duplicate / non-advancing revision
timestamp regression
unexpected from_phase
illegal phase transition
blocked transition into IMPLEMENTING / EVALUATING / ACCEPTED
stale transition into IMPLEMENTING / ACCEPTED
inconsistent blockage before value
invalid blockage after value
inconsistent validity before value
invalid validity after value
invalid supersession payload
event after CANCELLED
event after SUPERSEDED
```

Replay maintains a set of previously observed event IDs and rejects reuse.

For each event:

```text
event.occurred_at >= current.updated_at
```

is required. Equal timestamps are valid.

Replay applies the same normative structural rules as live operations, including cancellation blockage normalization and supersession storage.

After a successful replay, the reconstructed snapshot must be identical to the snapshot produced by applying the corresponding live operations with the same complete inputs.

---

# 26. Required Lifecycle Scenarios

Implementation tests and fixtures must cover at least:

## Full happy path

```text
PROPOSED
→ DEFINING
→ RESEARCHING
→ DESIGNING
→ CONTRACTING
→ PLANNING
→ READY
→ IMPLEMENTING
→ EVALUATING
→ ACCEPTED
```

## Short path

```text
PROPOSED
→ READY
→ IMPLEMENTING
→ EVALUATING
→ ACCEPTED
```

## Rework

```text
READY
→ IMPLEMENTING
→ EVALUATING
→ REWORK
→ EVALUATING
→ ACCEPTED
```

## Contract escalation

```text
IMPLEMENTING
→ EVALUATING
→ CONTRACTING
→ PLANNING
→ READY
→ IMPLEMENTING
→ EVALUATING
```

## Architecture escalation

```text
EVALUATING
→ DESIGNING
→ CONTRACTING
→ PLANNING
→ READY
```

## Definition escalation

```text
EVALUATING
→ DEFINING
→ DESIGNING
→ CONTRACTING
→ PLANNING
→ READY
```

## Blocker remediation

```text
IMPLEMENTING / CLEAR
→ IMPLEMENTING / BLOCKED
→ CONTRACTING / BLOCKED
→ CONTRACTING / CLEAR
```

## Blocked cancellation

```text
IMPLEMENTING / BLOCKED
→ CANCELLED / CLEAR
```

## Staleness

```text
ACCEPTED / CURRENT
→ ACCEPTED / STALE
→ ACCEPTED / CURRENT
```

## Supersession

```text
ACCEPTED
→ SUPERSEDED(successor)
```

## Replay

Every scenario above must replay to the identical final snapshot from its event sequence.

---

# 27. Relationship to Authorization

Slice 0.3 does not implement `Authorization`.

It creates the structural boundary authorization will later control:

```text
READY
   │
   │ future authorization / gate
   ▼
IMPLEMENTING
```

`ActorRef` on a lifecycle event records who requested or caused the operation. It does not prove that actor had authority.

---

# 28. Relationship to Handover Gates

Slice 0.4 will wrap structural lifecycle operations with governance:

```text
requested transition
        ↓
Handover Gate
        ↓
validity / authority / autonomy / prerequisites
        ↓
red / yellow / green
        ↓
if permitted
        ↓
Slice 0.3 lifecycle engine
```

The lifecycle engine defines what is structurally possible.

The gate engine defines what is currently permissible.

---

# 29. State Engine Exclusions

The state engine must not:

- produce traffic lights;
- validate engineering artifacts;
- check whether tests passed;
- decide whether dependencies are complete;
- validate actor permissions;
- evaluate authorization;
- enforce hard stops;
- perform persistence;
- call external systems.

---

# 30. Documentation-Lifecycle Boundary

Document/artifact maturity is distinct from slice lifecycle.

A slice may be:

```text
phase = DESIGNING
```

while its architecture artifact is:

```text
artifact state = REVIEW
```

Slice 0.3 does not implement artifact locking or a canonical artifact registry.

Documents produced by Slice 0.3 have these intended classes:

```text
LIFECYCLE_STATE_MACHINE.md
    → living architecture projection

ADR-0003-lifecycle-state-decomposition.md
    → lockable historical record

SLICE_0_3_STATE_MACHINE_MEMORY.md
    → working while active; locked at slice acceptance
```

Lifecycle events themselves are immutable immediately upon occurrence.

Exact repository metadata and canonical registry semantics remain deferred to Slice 0.6 under `DOCUMENTATION_GOVERNANCE.md`.

---

# 31. Scope, Simplicity, and Quality Are Not Lifecycle States

Cross-cutting findings do not create lifecycle phases such as:

```text
OVERENGINEERED
OUT_OF_SCOPE
QUALITY_FAILED
```

They remain findings, prerequisite conditions, or governance concerns.

Examples:

```text
phase = IMPLEMENTING
finding = CHANGE_SURFACE_EXCEEDED

phase = EVALUATING
finding = UNNECESSARY_ABSTRACTION

phase = READY
required quality evidence = missing
```

Slice 0.4 may later use such conditions as handover-gate inputs.

---

# 32. Explicit In Scope

Slice 0.3 authorizes implementation of:

1. `LifecyclePhase`;
2. `LifecycleValidity`;
3. `BlockageStatus`;
4. `BlockReason`;
5. `Blockage`;
6. `SliceLifecycle`;
7. `EventId` / `evt_` as a narrow extension of the accepted ID mechanism;
8. lifecycle event models;
9. explicit phase transition table;
10. pure lifecycle engine;
11. phase transition validation;
12. direct definition-level backward escalation;
13. blocker operations;
14. deterministic blocked-cancellation normalization;
15. staleness operations;
16. supersession successor storage;
17. explicit operation-context validation;
18. strict no-op rejection;
19. event replay;
20. lifecycle revision/time semantics;
21. narrow lifecycle errors;
22. lifecycle documentation;
23. ADR-0003;
24. lifecycle tests/fixtures;
25. Slice 0.3 memory;
26. current-baseline candidate update.

---

# 33. Explicit Out of Scope

Forbidden in Slice 0.3:

```text
Authorization model
HandoverGate
traffic lights
AUTO / HUMAN_APPROVAL policies
Hard Stop implementation
artifact prerequisite checks
dependency readiness checks
evaluation model
database
event persistence
GitHub integration
provider/model integration
agents
research execution
experiments
board UI
REST/API layer
canonical artifact registry
```

Do not create placeholder implementations for these future concepts.

---

# 34. Expected Implementation Change Surface

The design expects one small lifecycle package and a narrow extension of the accepted ID vocabulary.

Expected existing production files touched:

```text
src/relay_engine/domain/ids.py
src/relay_engine/domain/__init__.py   # only if needed to expose EventId consistently
```

Expected new production area:

```text
src/relay_engine/lifecycle/
```

A reasonable implementation may use cohesive modules such as:

```text
__init__.py
models.py
events.py
engine.py
errors.py
```

A separate `transitions.py` is optional, not required. The implementation agent should not create one merely to match an illustrative tree if the transition table is clearer inside `engine.py`.

Expected dependencies:

```text
new runtime dependencies: 0
new development dependencies: 0
```

Forbidden architectural expansion:

```text
event bus
repository pattern
persistence abstraction
service layer
plugin registry
state-machine framework dependency
dependency-injection framework
```

Use direct Python/Pydantic constructs and the existing Relay domain values.

---

# 35. Required Documentation

Implementation creates:

```text
docs/architecture/LIFECYCLE_STATE_MACHINE.md
docs/decisions/ADR-0003-lifecycle-state-decomposition.md
docs/slices/SLICE_0_3_STATE_MACHINE_MEMORY.md
```

ADR-0003 must record at minimum:

1. READY is a phase.
2. AUTHORIZED is not a phase.
3. BLOCKED is orthogonal.
4. STALE is orthogonal.
5. HARD STOP belongs to handover governance.
6. lifecycle is separate from Slice definition.
7. lifecycle operations are deterministic and event-producing.
8. event IDs and time are explicit operation inputs.
9. accepted history is immutable except explicit supersession.
10. supersession successor is retained in lifecycle state.

Before human acceptance:

```text
ADR-0003 status = PROPOSED / VALIDATED / PENDING ACCEPTANCE
Slice 0.3 memory = IMPLEMENTATION COMPLETE / PENDING EVALUATION
```

Neither is locked before acceptance.

---

# 36. Acceptance Matrix

All requirements are mandatory.

| ID | Requirement | Evidence |
|---|---|---|
| A01 | Lifecycle is separate from `Slice` | inspection |
| A02 | READY is a lifecycle phase | unit test/schema |
| A03 | AUTHORIZED absent from phase enum | inspection |
| A04 | BLOCKED absent from phase enum | inspection |
| A05 | STALE absent from phase enum | inspection |
| A06 | HARD_STOP absent from phase enum | inspection |
| A07 | Blockage modeled orthogonally | unit tests |
| A08 | Validity modeled orthogonally | unit tests |
| A09 | Full transition matrix explicit | inspection |
| A10 | Every phase pair tested | parametrized tests |
| A11 | Direct IMPLEMENTING→ACCEPTED rejected | unit test |
| A12 | Direct REWORK→ACCEPTED rejected | unit test |
| A13 | READY required before IMPLEMENTING | unit tests |
| A14 | IMPLEMENTING/REWORK required before EVALUATING | unit tests |
| A15 | ACCEPTED only reachable from EVALUATING | unit tests |
| A16 | ACCEPTED→SUPERSEDED supported | unit test |
| A17 | ACCEPTED→CANCELLED rejected | unit test |
| A18 | SUPERSEDED terminal | unit test |
| A19 | CANCELLED terminal | unit test |
| A20 | Rework loop supported | fixture test |
| A21 | Architecture escalation supported | fixture test |
| A22 | Contract escalation supported | fixture test |
| A23 | Blocked forward execution rejected | unit tests |
| A24 | Blocked remediation transitions possible | unit tests |
| A25 | Stale implementation rejected | unit test |
| A26 | Stale acceptance rejected | unit test |
| A27 | ACCEPTED + STALE supported | unit test |
| A28 | Revalidation preserves phase | unit test |
| A29 | Every successful operation emits exactly one event | unit tests |
| A30 | No-op requests raise typed error and emit no event | unit tests |
| A31 | Revisions increment exactly once | unit tests |
| A32 | Event replay reconstructs lifecycle | unit tests |
| A33 | Malformed replay rejected | unit tests |
| A34 | Event actor/time/reason explicit | schema tests |
| A35 | State engine performs no I/O, clock, or randomness | inspection |
| A36 | No authorization semantics introduced | inspection |
| A37 | No traffic-light logic introduced | inspection |
| A38 | No persistence dependency introduced | dependency inspection |
| A39 | `LIFECYCLE_STATE_MACHINE.md` completed | review |
| A40 | ADR-0003 completed | review |
| A41 | Slice memory completed | review |
| A42 | `CURRENT_BASELINE.md` distinguishes accepted baseline from candidate | review |
| A43 | All prior quality gates remain green | CI |
| A44 | Event ID supplied explicitly; engine generates no ID | unit test/inspection |
| A45 | EventId uses `evt_<uuid7>` through accepted ID mechanism | unit test/schema |
| A46 | Blocked→CANCELLED deterministically yields CANCELLED/CLEAR | unit/replay test |
| A47 | Supersession successor preserved in snapshot and replay | unit/replay test |
| A48 | Semantic no-ops preserve revision/time and emit nothing | unit tests |
| A49 | BlockReason syntax/order/equality/duplicate semantics enforced | unit tests |
| A50 | All successful operations require explicit nonblank reason | unit/schema tests |
| A51 | Lifecycle/event timestamps are aware and UTC-normalized | unit/schema tests |
| A52 | `updated_at` equals successful operation `occurred_at` | unit tests |
| A53 | Timestamp regression rejected; equal timestamp allowed | unit tests |
| A54 | Lifecycle and event models immutable/versioned/extra-forbid | schema tests |
| A55 | Duplicate event IDs rejected during replay | replay test |
| A56 | Replay rejects malformed terminal history | replay tests |
| A57 | Direct definition-level backward escalation supported | transition tests |
| A58 | Identical snapshot + identical complete operation input yields identical result | determinism test |

---

# 37. Named Regression Tests

At minimum:

```text
test_ready_does_not_mean_authorized
test_implementation_cannot_accept_itself
test_rework_requires_reevaluation
test_accepted_history_cannot_return_to_rework
test_blocked_preserves_phase_during_remediation
test_blocked_cancellation_clears_blockage_once
test_stale_preserves_phase
test_accepted_can_be_stale
test_supersession_requires_successor
test_supersession_preserves_successor_in_snapshot
test_terminal_states_have_no_normal_outgoing_transition
test_noop_is_rejected_without_event_or_revision_change
test_event_id_is_explicit_and_engine_generates_no_id
test_timestamp_regression_is_rejected
test_equal_timestamp_is_allowed
test_definition_escalation_is_direct
test_replay_reconstructs_identical_snapshot
test_replay_rejects_duplicate_event_id
test_replay_rejects_terminal_history_extension
test_identical_inputs_are_deterministic
```

---

# 38. Design Review Findings Resolved in Revision 4

Revision 4 resolves `RLY-S03-DESIGN-EVAL-001` findings as follows:

| Finding | Resolution |
|---|---|
| `RLY-S03-D001` | Event IDs are explicit operation inputs; engine performs no UUID generation. |
| `RLY-S03-D002` | Blocked cancellation is legal and atomically normalizes blockage to CLEAR with one PhaseChanged event. |
| `RLY-S03-D003` | `superseded_by_slice_id` is stored in `SliceLifecycle` and replayed. |
| `RLY-S03-D004` | All semantic no-ops raise `InvalidLifecycleOperation`; no event/revision/time change. |
| `RLY-S03-D005` | BlockReason syntax, ordered tuple semantics, duplicate handling, and structural equality are normative. |
| `RLY-S03-D006` | All operations require explicit event ID/actor/time/reason; UTC/update/timestamp rules are locked. |
| `RLY-S03-D007` | Event payloads and strict replay rejection rules are explicit. |
| `RLY-S03-D008` | Direct backward escalation to DEFINING is supported from later active phases. |
| `RLY-S03-D009` | Externally observable semantics are normative; public lifecycle error family is locked. |
| `RLY-S03-D010` | Authorization metadata records `RLY-S03-AUTH-001` as Revision-3 authorization requiring revalidation for Revision 4. |

---

# 39. Resulting Authority After Acceptance

After Revision 4 design acceptance and successful Slice 0.3 implementation/acceptance, Relay will know:

```text
what a slice is
where that slice is
whether its current validity is established
whether it is presently blocked
which structural lifecycle movements are legal
what lifecycle events occurred
how to replay those events deterministically
which slice superseded an accepted slice
```

Relay still will not know:

```text
whether a transition is authorized
whether required artifacts exist
whether a human must approve
whether a transition should run automatically
whether a hard stop applies
whether an evaluator approved the work
```

Those are next-layer governance concerns.

---

# 40. Design-State and Authorization Gate

Current state of this document:

```text
Revision 4
Artifact state: REVIEW
Design acceptance: PENDING
```

Prior implementation authorization:

```text
RLY-S03-AUTH-001
```

was granted against Revision 3.

Because Revision 4 materially changes the public contract, implementation may begin only after both:

```text
1. Human acceptance of Design Revision 4
2. Explicit revalidation of RLY-S03-AUTH-001 against Revision 4
```

Until then:

```text
AUTHORIZATION HISTORY: PRESENT
EXECUTION: BLOCKED
```

No Slice 0.3 production code may be started from this review branch.

---

# 41. Hard Stop

After eventual Slice 0.3 acceptance:

```text
HARD STOP
```

Do not begin Slice 0.4 automatically.

The next design candidate remains:

> **Slice 0.4 — Handover Gates and Traffic Lights**

which will answer:

```text
A structural transition is possible.

But may it happen now?

Who must approve it?

Can Relay execute it automatically?

What makes the handover red, yellow, or green?
```

---

# 42. Summary

The authoritative decomposition remains:

```text
                 WHAT THE WORK IS
                       Slice
                         │
                         ▼
                WHERE THE WORK IS
                  LifecyclePhase
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
           Validity              Blockage
        CURRENT/STALE         CLEAR/BLOCKED


             FUTURE GOVERNANCE

                  Authorization
                       │
                       ▼
                  Handover Gate
                       │
                red / yellow / green
                       │
                       ▼
                 State Engine
```

The lifecycle engine is deterministic because all external/nondeterministic values are explicit inputs.

A slice can be ready without being authorized.

A slice can be implementing while blocked.

A slice can be accepted while stale.

A blocked slice can be cancelled without creating contradictory terminal blockage.

A superseded lifecycle retains its explicit successor.

Those distinctions provide the semantic precision required for Slice 0.4 without leaking governance into the state engine.
