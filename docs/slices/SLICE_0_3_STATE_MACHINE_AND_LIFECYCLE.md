# Relay Slice 0.3 — State Machine and Lifecycle Semantics

**Slice:** 0.3  
**Phase:** 0 — Protocol and Deterministic Foundation  
**Status:** PROPOSED FOR DESIGN REVIEW  
**Document class:** Lockable record  
**Artifact state:** REVIEW  
**Document revision:** 3  
**Parent:** *Relay — Build Plan and Development Roadmap v0.1*  
**Depends on:** Slice 0.2 — Core Domain Model  
**Implementation authorization:** NOT YET GRANTED

---

# 1. Objective

Define Relay's authoritative lifecycle semantics for a development slice.

Slice 0.3 must answer:

> Where is the work in its engineering lifecycle?

while deliberately separating that question from:

> Is the work authorized?

> Is the work blocked?

> Is the work stale?

> Is an outgoing handover behind a hard stop?

The exit condition is:

> Given the same lifecycle snapshot and the same requested operation, Relay deterministically produces the same valid next snapshot and immutable lifecycle event—or rejects the operation.

No LLM participates in this process.

---

# 2. Central Design Decision

Relay will **not** use one flat status enum containing:

```text
READY
AUTHORIZED
BLOCKED
STALE
HARD_STOP
IMPLEMENTING
...
```

because these terms describe different dimensions.

Instead:

```text
                 Slice lifecycle

                      PHASE
                        │
                        │
             ┌──────────┴─────────┐
             │                    │
          VALIDITY             BLOCKAGE
             │                    │
       CURRENT / STALE       CLEAR / BLOCKED
```

while:

```text
AUTHORIZATION
```

belongs to transition authority, and:

```text
HARD STOP
```

belongs to handover policy.

This distinction is foundational.

---

# 3. Why a Flat State Model Fails

A slice may be both `IMPLEMENTING` and `BLOCKED`. Replacing `IMPLEMENTING → BLOCKED` loses information about where work was occurring.

Likewise, `ACCEPTED` and `STALE` can both be true. An implementation may have been historically accepted but no longer validated against a newly changed upstream contract.

And `READY` and `AUTHORIZED` represent different facts:

```text
READY
= technically prepared to execute

AUTHORIZED
= permission exists to execute
```

Relay must preserve these distinctions.

---

# 4. S0.3-D01 — Lifecycle Phase

The authoritative primary lifecycle enum is:

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

These represent **where the slice is in its engineering lifecycle**.

---

# 5. Phase Meanings

## PROPOSED

The work exists but has not yet acquired enough engineering definition to proceed.

## DEFINING

Objective, boundaries, value, success criteria, and non-goals are being established.

## RESEARCHING

External or internal evidence required for the current engineering question is being gathered.

Dedicated sidecar research objects come later.

## DESIGNING

Architecture or technical design is being developed or revised.

## CONTRACTING

Implementation boundaries, APIs, invariants, failure semantics, and acceptance expectations are being made explicit.

## PLANNING

Accepted engineering intent is being decomposed into executable work.

## READY

The slice has completed the preparation required by its configured workflow and is waiting to proceed toward implementation.

`READY` does **not** imply authorization.

## IMPLEMENTING

An implementation attempt is active.

## EVALUATING

An implementation result is under independent assessment.

## REWORK

An implementation-level correction is being performed without invalidating accepted upstream architecture or contract.

## ACCEPTED

The slice has historically satisfied its acceptance process.

Acceptance is a historical engineering fact.

## SUPERSEDED

The accepted result has been explicitly replaced by later authoritative work.

## CANCELLED

Work has been deliberately terminated without acceptance.

---

# 6. S0.3-D02 — READY Is a Real Phase

`READY` remains a primary lifecycle phase.

It represents a stable queue boundary:

```text
engineering preparation complete
        ↓
READY
        ↓
waiting for permission/execution capacity
```

This state is useful even before authorization exists.

---

# 7. S0.3-D03 — AUTHORIZED Is Not a Phase

There will be no `LifecyclePhase.AUTHORIZED`.

Authorization is a permission relationship, not engineering progress.

The authoritative future representation will conceptually be:

```text
Slice lifecycle:
phase = READY

Authorization:
GRANTED
```

The slice remains `READY` until implementation actually starts.

At that point:

```text
READY
  ↓
IMPLEMENTING
```

---

# 8. Board Consequence

The future board may choose to display:

```text
READY + valid authorization
```

as an `AUTHORIZED` column or visual lane.

That is a **projection**, not the underlying lifecycle phase.

---

# 9. S0.3-D04 — BLOCKED Is Orthogonal

A slice may be blocked while:

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

Therefore `BLOCKED` is not a lifecycle phase.

The lifecycle snapshot carries a blockage condition independently.

---

# 10. Blockage Model

Proposed:

```text
BlockageStatus

CLEAR
BLOCKED
```

with `BlockReason` containing:

```text
code
summary
```

A blocked snapshot must contain at least one reason.

A clear snapshot contains no blocker reasons.

Example:

```text
phase: IMPLEMENTING

blockage:
    status: BLOCKED
    reasons:
      - code: CONTRACT_CONFLICT
        summary: Current API contract does not define failure behavior.
```

---

# 11. Multiple Blockers

Multiple active blocker reasons are allowed.

Reason codes are extensible validated slugs rather than a permanently closed enum.

---

# 12. S0.3-D05 — STALE Is Orthogonal

`STALE` does not mean wrong.

It means:

> Validity against the currently authoritative upstream context has not been established.

Lifecycle validity:

```text
CURRENT
STALE
```

is separate from lifecycle phase.

---

# 13. Why ACCEPTED + STALE Must Be Possible

Suppose:

```text
Contract C3
    ↓
Slice S12 implemented
    ↓
S12 ACCEPTED
```

Later:

```text
Contract C4 supersedes C3
```

The historical fact remains:

```text
S12 was accepted against C3.
```

But its current validity may become `STALE`.

Therefore the correct representation is:

```text
phase: ACCEPTED
validity: STALE
```

---

# 14. S0.3-D06 — HARD STOP Is Not Lifecycle State

There will be no `LifecyclePhase.HARD_STOP`.

A Hard Stop controls an **outgoing handover**.

The accepted slice itself remains `ACCEPTED`.

Hard Stop semantics therefore belong to Slice 0.4: Handover Gates and Traffic Lights.

---

# 15. Resulting State Decomposition

```text
Slice lifecycle
│
├── Phase
│   ├── PROPOSED
│   ├── DEFINING
│   ├── RESEARCHING
│   ├── DESIGNING
│   ├── CONTRACTING
│   ├── PLANNING
│   ├── READY
│   ├── IMPLEMENTING
│   ├── EVALUATING
│   ├── REWORK
│   ├── ACCEPTED
│   ├── SUPERSEDED
│   └── CANCELLED
│
├── Validity
│   ├── CURRENT
│   └── STALE
│
└── Blockage
    ├── CLEAR
    └── BLOCKED
```

Separate future governance:

```text
Authorization
Handover policy
Hard Stop
Traffic light
```

---

# 16. S0.3-D07 — Separate Lifecycle Snapshot

Slice 0.2 deliberately kept workflow state out of `Slice`.

Slice 0.3 introduces a separate immutable object:

```text
SliceLifecycle
```

Conceptually:

```python
SliceLifecycle(
    schema_version,
    slice_id,
    phase,
    validity,
    blockage,
    revision,
    updated_at,
)
```

This allows `Slice` to describe what the work is while `SliceLifecycle` describes where the work currently is.

---

# 17. S0.3-D08 — Lifecycle Is Immutable

A transition does not mutate the existing lifecycle object.

Instead:

```text
old snapshot
     ↓
state engine
     ↓
new snapshot
+
immutable event
```

---

# 18. Lifecycle Revision

Every lifecycle snapshot carries `revision`, initially `0`.

Every accepted lifecycle operation increments revision by exactly one.

---

# 19. No Hidden Clock

State transitions receive:

```text
actor
occurred_at
reason
```

explicitly.

The lifecycle engine does not call the clock internally.

---

# 20. Lifecycle Events

Every accepted lifecycle operation produces an immutable event.

Initial event categories:

```text
LifecycleInitialized
PhaseChanged
BlockageChanged
ValidityChanged
```

No event is persisted yet.

---

# 21. Common Event Fields

Every lifecycle event contains at minimum:

```text
event_id
slice_id
actor
occurred_at
reason
resulting_revision
```

Specific events include their before/after values.

---

# 22. Event Identifier

Introduce:

```text
evt_<uuid7>
```

following Slice 0.2's ID convention.

---

# 23. Actor Does Not Imply Authority

Events identify who requested or caused the operation.

Slice 0.3 does not answer whether that actor was allowed to do it.

Authority belongs to governance.

---

# 24. Initialization

A newly initialized lifecycle begins:

```text
phase: PROPOSED
validity: CURRENT
blockage: CLEAR
revision: 0
```

Initialization produces `LifecycleInitialized` with explicit actor and timestamp.

---

# 25. S0.3-D09 — Explicit Transition Matrix

Legal phase transitions are represented by an explicit transition table.

Do not infer legality from enum ordering.

---

# 26. Allowed Phase Transitions

## PROPOSED

```text
DEFINING
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
READY
CANCELLED
```

## DEFINING

```text
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
READY
CANCELLED
```

## RESEARCHING

```text
DEFINING
DESIGNING
CONTRACTING
PLANNING
READY
CANCELLED
```

## DESIGNING

```text
RESEARCHING
CONTRACTING
PLANNING
READY
CANCELLED
```

## CONTRACTING

```text
RESEARCHING
DESIGNING
PLANNING
READY
CANCELLED
```

## PLANNING

```text
RESEARCHING
DESIGNING
CONTRACTING
READY
CANCELLED
```

## READY

```text
DEFINING
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
IMPLEMENTING
CANCELLED
```

## IMPLEMENTING

```text
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
EVALUATING
CANCELLED
```

## EVALUATING

```text
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
REWORK
ACCEPTED
CANCELLED
```

## REWORK

```text
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
EVALUATING
CANCELLED
```

## ACCEPTED

```text
SUPERSEDED
```

## SUPERSEDED

Terminal.

## CANCELLED

Terminal.

---

# 27. Structural Transition Rules

Implementation cannot transition directly to `ACCEPTED`.

Rework cannot transition directly to `ACCEPTED`.

Only `EVALUATING → ACCEPTED` is structurally valid.

Implementation always passes through `READY`.

Evaluation requires either `IMPLEMENTING` or `REWORK` as its source.

Accepted work never returns to rework.

Accepted work is superseded by new authoritative work rather than historically rewritten.

---

# 28. Supersession Reference

Transitioning:

```text
ACCEPTED → SUPERSEDED
```

must identify `superseded_by_slice_id` or equivalent explicit successor reference.

---

# 29. S0.3-D10 — Transition Reason

Every phase transition requires a non-empty reason.

Relay should not rely on transition direction alone to explain engineering history.

---

# 30. Blockage Operations

Lifecycle supports:

```text
set_blocked(reasons)
clear_blockage(reason)
```

No state change means no event.

Terminal phases `ACCEPTED`, `SUPERSEDED`, and `CANCELLED` cannot become blocked.

---

# 31. Blocked Phase Restrictions

While blocked, normal forward progression into:

```text
IMPLEMENTING
EVALUATING
ACCEPTED
```

is rejected unless blockage has first been cleared.

Blocked work may still transition toward remediation where structurally legal.

---

# 32. Validity Operations

Lifecycle supports:

```text
mark_stale(reason)
revalidate(reason)
```

Allowed:

```text
CURRENT → STALE
STALE → CURRENT
```

When stale, transition into `IMPLEMENTING` or `ACCEPTED` is prohibited without revalidation.

`ACCEPTED + STALE` is valid.

`CANCELLED` and `SUPERSEDED` reject validity operations.

---

# 33. S0.3-D11 — State Engine Is Pure

The state engine performs no:

```text
database access
Git access
GitHub calls
HTTP calls
model calls
filesystem access
clock access
```

Conceptually:

```text
current lifecycle
+
requested operation
        ↓
pure state engine
        ↓
new lifecycle
+
event
```

or a typed error.

---

# 34. Proposed Package Structure

```text
src/
└── relay_engine/
    ├── domain/
    │   └── ...
    │
    └── lifecycle/
        ├── __init__.py
        ├── models.py
        ├── events.py
        ├── transitions.py
        ├── engine.py
        └── errors.py
```

---

# 35. Proposed Public Lifecycle Surface

Conceptually:

```python
initialize_lifecycle(...)

transition_phase(...)

set_blocked(...)

clear_blockage(...)

mark_stale(...)

revalidate(...)

replay_lifecycle(...)
```

---

# 36. Lifecycle Errors

Narrow typed exceptions may include:

```text
InvalidPhaseTransition
InvalidLifecycleOperation
LifecycleReplayError
```

---

# 37. No Silent No-Ops

Requests such as:

```text
READY → READY
CURRENT → CURRENT
CLEAR → CLEAR
```

should not create fake history.

Recommended behavior: reject as no-op with a typed lifecycle error.

---

# 38. Event Replay

Relay must be able to reconstruct lifecycle state from ordered lifecycle events.

Replay must reject malformed history such as:

```text
revision gap
event for wrong slice
event from unexpected prior phase
duplicate initialization
inconsistent blockage event
inconsistent validity event
```

Persistence is not required.

Replay semantics are.

---

# 39. Revision Semantics

Recommended:

```text
LifecycleInitialized
resulting_revision = 0
```

Then:

```text
first change = revision 1
second change = revision 2
...
```

Every state-changing event increments exactly once.

---

# 40. Required Lifecycle Fixtures

## Full happy path

```text
PROPOSED
↓
DEFINING
↓
RESEARCHING
↓
DESIGNING
↓
CONTRACTING
↓
PLANNING
↓
READY
↓
IMPLEMENTING
↓
EVALUATING
↓
ACCEPTED
```

## Short path

```text
PROPOSED
↓
READY
↓
IMPLEMENTING
↓
EVALUATING
↓
ACCEPTED
```

## Rework

```text
READY
↓
IMPLEMENTING
↓
EVALUATING
↓
REWORK
↓
EVALUATING
↓
ACCEPTED
```

## Contract escalation

```text
IMPLEMENTING
↓
EVALUATING
↓
CONTRACTING
↓
PLANNING
↓
READY
↓
IMPLEMENTING
↓
EVALUATING
```

## Architecture escalation

```text
EVALUATING
↓
DESIGNING
↓
CONTRACTING
↓
PLANNING
↓
READY
```

## Blocker

```text
IMPLEMENTING / CLEAR
↓
IMPLEMENTING / BLOCKED
↓
CONTRACTING / BLOCKED
↓
CONTRACTING / CLEAR
```

## Staleness

```text
ACCEPTED / CURRENT
↓
ACCEPTED / STALE
↓
ACCEPTED / CURRENT
```

## Supersession

```text
ACCEPTED
↓
SUPERSEDED
```

with explicit successor reference.

---

# 41. Relationship to Authorization

Slice 0.3 deliberately does not implement `Authorization`.

It creates the boundary authorization will control:

```text
READY
   │
   │ future authorization/gate
   ▼
IMPLEMENTING
```

---

# 42. Relationship to Handover Gates

Slice 0.4 will wrap structural lifecycle transitions with governance:

```text
requested transition
        ↓
Handover Gate
        ↓
validity
authority
autonomy
        ↓
🔴 / 🟡 / 🟢
        ↓
if permitted
        ↓
Slice 0.3 state engine
```

The state engine defines what is structurally possible.

The gate engine defines what is currently permissible.

---

# 43. State Engine Exclusions

The state engine must not:

- produce traffic lights;
- validate artifacts;
- check whether tests passed;
- decide whether dependencies are complete;
- validate actor permissions;
- evaluate authorization;
- enforce hard stops;
- call external systems.

---

# 44. Required Documentation

Implementation should create:

```text
docs/architecture/LIFECYCLE_STATE_MACHINE.md
docs/decisions/ADR-0003-lifecycle-state-decomposition.md
docs/slices/SLICE_0_3_STATE_MACHINE_MEMORY.md
```

ADR-0003 records that:

1. READY is a phase.
2. AUTHORIZED is not a phase.
3. BLOCKED is orthogonal.
4. STALE is orthogonal.
5. HARD STOP belongs to handover governance.
6. lifecycle is separate from Slice definition.
7. lifecycle transitions are event-producing and deterministic.
8. accepted history is immutable except explicit supersession.

---

# 44A. Documentation-Lifecycle Boundary

Document/artifact maturity is distinct from slice lifecycle.

A slice may be:

```text
phase = DESIGNING
```

while its architecture artifact is:

```text
artifact state = REVIEW
```

Likewise, a slice may become `ACCEPTED`, causing designated acceptance records such as its final slice memory to become `LOCKED`.

Slice 0.3 does not implement artifact locking. It only establishes the boundary.

For the documents produced by this slice:

```text
LIFECYCLE_STATE_MACHINE.md
    → living architecture projection

ADR-0003-lifecycle-state-decomposition.md
    → lockable historical record

SLICE_0_3_STATE_MACHINE_MEMORY.md
    → mutable while active; LOCKED at slice acceptance
```

Lifecycle events themselves are immutable records immediately upon occurrence.

The exact repository metadata and canonical registry are deferred to Slice 0.6 and governed by `DOCUMENTATION_GOVERNANCE.md`.

---

# 44B. Scope, Simplicity, and Quality Are Not Lifecycle States

Relay's cross-cutting policy:

```text
ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md
```

does not add lifecycle phases such as:

```text
OVERENGINEERED
OUT_OF_SCOPE
QUALITY_FAILED
```

These are findings, prerequisite conditions, or governance concerns.

Examples:

```text
phase = IMPLEMENTING
finding = CHANGE_SURFACE_EXCEEDED

phase = EVALUATING
finding = UNNECESSARY_ABSTRACTION

phase = READY
required quality evidence = missing
```

The lifecycle remains structural.

Slice 0.4 will determine how such conditions affect handover traffic lights.

Later evaluation slices will determine how semantic simplicity/clarity findings route to `REWORK`.

This preserves the principle:

> **Lifecycle truth and engineering permission/evaluation are different things.**

---

# 45. Explicit In Scope

Slice 0.3 authorizes design/implementation of:

1. LifecyclePhase;
2. LifecycleValidity;
3. BlockageStatus;
4. BlockReason;
5. Blockage;
6. SliceLifecycle;
7. lifecycle event models;
8. explicit phase transition table;
9. pure state engine;
10. phase transition validation;
11. blocker operations;
12. staleness operations;
13. event replay;
14. lifecycle revision semantics;
15. narrow lifecycle errors;
16. lifecycle documentation;
17. ADR-0003;
18. lifecycle tests;
19. Slice 0.3 memory;
20. current-baseline update.

---

# 46. Explicit Out of Scope

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
GitHub
provider integration
agents
research execution
experiments
board UI
REST/API layer
```

---

# 47. Acceptance Matrix

| ID | Requirement | Evidence | Required |
|---|---|---|---:|
| A01 | Lifecycle is separate from Slice | inspection | Yes |
| A02 | READY is a lifecycle phase | unit test/schema | Yes |
| A03 | AUTHORIZED absent from phase enum | inspection | Yes |
| A04 | BLOCKED absent from phase enum | inspection | Yes |
| A05 | STALE absent from phase enum | inspection | Yes |
| A06 | HARD_STOP absent from phase enum | inspection | Yes |
| A07 | Blockage modeled orthogonally | unit tests | Yes |
| A08 | Validity modeled orthogonally | unit tests | Yes |
| A09 | Full transition matrix explicit | inspection | Yes |
| A10 | Every phase pair tested | parametrized tests | Yes |
| A11 | Direct IMPLEMENTING→ACCEPTED rejected | unit test | Yes |
| A12 | Direct REWORK→ACCEPTED rejected | unit test | Yes |
| A13 | READY required before IMPLEMENTING | unit tests | Yes |
| A14 | IMPLEMENTING/REWORK required before EVALUATING | unit tests | Yes |
| A15 | ACCEPTED only reachable from EVALUATING | unit tests | Yes |
| A16 | ACCEPTED→SUPERSEDED supported | unit test | Yes |
| A17 | ACCEPTED→CANCELLED rejected | unit test | Yes |
| A18 | SUPERSEDED terminal | unit test | Yes |
| A19 | CANCELLED terminal | unit test | Yes |
| A20 | Rework loop supported | fixture test | Yes |
| A21 | Architecture escalation supported | fixture test | Yes |
| A22 | Contract escalation supported | fixture test | Yes |
| A23 | Blocked forward execution rejected | unit tests | Yes |
| A24 | Blocked remediation transitions possible | unit tests | Yes |
| A25 | Stale implementation rejected | unit test | Yes |
| A26 | Stale acceptance rejected | unit test | Yes |
| A27 | ACCEPTED + STALE supported | unit test | Yes |
| A28 | Revalidation preserves phase | unit test | Yes |
| A29 | Every successful operation emits one event | unit tests | Yes |
| A30 | No-op requests emit no event | unit tests | Yes |
| A31 | Revisions increment exactly once | unit tests | Yes |
| A32 | Event replay reconstructs lifecycle | unit tests | Yes |
| A33 | Malformed replay rejected | unit tests | Yes |
| A34 | Event actor/time/reason explicit | schema tests | Yes |
| A35 | State engine performs no I/O | inspection | Yes |
| A36 | No authorization semantics introduced | inspection | Yes |
| A37 | No traffic-light logic introduced | inspection | Yes |
| A38 | No persistence dependency introduced | dependency inspection | Yes |
| A39 | LIFECYCLE_STATE_MACHINE.md completed | review | Yes |
| A40 | ADR-0003 completed | review | Yes |
| A41 | Slice memory completed | review | Yes |
| A42 | CURRENT_BASELINE updated | review | Yes |
| A43 | All prior quality gates remain green | CI | Yes |

---

# 48. Named Regression Tests

At minimum:

```text
test_ready_does_not_mean_authorized
test_implementation_cannot_accept_itself
test_rework_requires_reevaluation
test_accepted_history_cannot_return_to_rework
test_blocked_preserves_phase
test_stale_preserves_phase
test_accepted_can_be_stale
test_supersession_requires_successor
test_terminal_states_have_no_normal_outgoing_transition
test_replay_reconstructs_identical_snapshot
```

---

# 49. Resulting Authority

After acceptance, Relay will authoritatively know:

```text
what a slice is
+
where that slice is
+
whether its current validity is established
+
whether it is presently blocked
+
which structural lifecycle movements are legal
+
what lifecycle events occurred
```

Relay still will **not** know:

```text
whether a transition is authorized
whether required artifacts exist
whether a human must approve
whether a transition should run automatically
whether a hard stop applies
whether an evaluator has approved the work
```

Those are deliberately next-layer concerns.

---

# 50. Hard Stop

After acceptance:

```text
HARD STOP
```

Review specifically:

- whether READY is correctly placed;
- whether authorization is sufficiently separated;
- whether blockage belongs outside phase;
- whether staleness semantics preserve accepted history;
- whether the transition matrix is too permissive;
- whether backward transitions are expressive enough;
- whether lifecycle events are sufficient for later persistence;
- whether any governance logic leaked prematurely into the state engine.

Do not begin Handover Gate implementation automatically.

---

# 51. Candidate Next Slice

Expected:

> **Slice 0.4 — Handover Gates and Traffic Lights**

It will answer:

```text
A structural transition is possible.

But may it happen now?

Who must approve it?

Can Relay execute it automatically?

What makes the handover red, yellow, or green?
```

This is where authorization, human approval, hard stops, prerequisite artifacts, and traffic lights begin to enter the executable governance model.

---

# 52. Slice 0.3 Summary

The core model becomes:

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
                🔴     🟡     🟢
                       │
                       ▼
                 State Engine
```

The central invariant is:

> **Lifecycle truth and transition permission are different things.**

A slice can be ready without being authorized.

A slice can be implementing while blocked.

A slice can be accepted while stale.

A slice can be accepted while its outgoing handover is under a hard stop.

Those distinctions give Relay enough semantic precision to build its traffic-light governance system cleanly in Slice 0.4.
