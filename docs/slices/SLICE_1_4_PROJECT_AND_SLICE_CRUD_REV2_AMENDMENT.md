# Slice 1.4 — Project and Slice CRUD — Revision 2 Amendment

**Status:** DESIGN REVISION 2 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design amendment  
**Human version:** Revision 2 Amendment  
**Project:** Relay  
**Slice:** 1.4  
**Design authority:** `RLY-S14-DESIGN-AUTH-001`  
**Revision 1 head:** `430b1e1ff5eb06c26d4c63225b455feda14b6710`  
**Independent review:** `RLY-S14-DESIGN-EVAL-001 — REVISE`  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-09-30

---

# 1. Purpose

This bounded amendment resolves exactly the four findings from the independent
review of Slice 1.4 Design Revision 1.

Revision 1 remains historical and is not edited in place. This amendment is
normative wherever it conflicts with Revision 1.

The accepted architecture direction is preserved:

- immutable `Project` and `Slice` domain values;
- bounded human-controlled definition administration;
- integer definition revisions plus append-only definition history;
- SQLite migration v4;
- Project repository authority remains immutable;
- lifecycle/governance remain separate from CRUD;
- guarded delete only for unused current entities;
- no board, provider, repository-sync, or agent work.

No architecture escalation is required.

---

# 2. Review findings resolved

## F001 — BLOCKING — authority-lineage terminology is contradictory

The immutable authorization record `RLY-S14-DESIGN-AUTH-001` names:

```text
670996ec43d77526adb0ea540c81a57d6e83453b
```

as the exact baseline to which the Human Authority decision applies.

The authority-recording commit is:

```text
1eaece23e31d831bfd2b27e55a898df389cc45fc
```

and Design Revision 1 is directly parented by that authority-recording commit.

Revision 1 and the living projections incorrectly called `1eaece23…` the
"exact authorized design baseline."

### Resolution

Normative terminology is now:

```text
Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording canonical commit / design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1 design head:
430b1e1ff5eb06c26d4c63225b455feda14b6710
```

This is a provenance clarification only. It does not broaden or replace
`RLY-S14-DESIGN-AUTH-001`.

Where Revision 1 says `Authorized baseline: 1eaece23…`, read it as
`Authority-recording design parent: 1eaece23…`.

## F002 — BLOCKING — raw Project/Slice insert primitives bypass audited human CRUD

Revision 1 retained publicly exported `insert_project` / `insert_slice`
persistence primitives and proposed that they create `SEED` history after
migration v4.

That leaves a second mutation path capable of creating current Project/Slice
state without the Slice 1.4 human mutation contract.

### Resolution — S14-D26

After migration v4, product/runtime creation of current Project/Slice state MUST
flow through the Slice 1.4 administration service.

The persistence package MUST NOT publicly export a runtime Project/Slice creation
primitive that can establish current state without the Slice 1.4 mutation
contract.

The existing `insert_project` and `insert_slice` functions may be:

1. removed from the public persistence export surface and replaced by private,
   explicitly test/bootstrap-only helpers; or
2. refactored into internal helpers used only beneath the administration service.

Either implementation must satisfy the same normative boundary:

```text
runtime/product Project or Slice creation
        -> Slice 1.4 administration service
        -> validated HUMAN mutation metadata
        -> CREATE definition-history revision
        -> current row
```

`SEED` is migration-only. It is created only by deterministic migration v4 for
rows that existed before definition history was introduced.

No post-v4 runtime API may create a new Project/Slice current row with a `SEED`
revision.

Low-level persistence tests may construct pre-v4 fixtures before migration, but
that fixture mechanism is not a runtime API.

## F003 — MAJOR — stale exact-target update bypasses compare-and-swap causality

Revision 1 checked target equality before checking
`expected_definition_revision`. Therefore a stale caller could receive success
whenever its target happened to equal the current payload, even after one or more
intervening definition revisions.

Without a persisted command identity, Relay cannot distinguish:

- a safe retry after a lost response; from
- a distinct stale human command that merely converges on the same value.

### Resolution — S14-D27

Update compare-and-swap is strict.

Normative algorithm:

1. load current row inside `BEGIN IMMEDIATE`;
2. validate immutable identity/ownership fields;
3. require `expected_definition_revision == current.definition_revision`;
4. only then compare the target value to the current value;
5. if equal, return `changed=false` at the current revision;
6. otherwise validate mutation invariants;
7. append revision N+1 and update the current row with
   `WHERE definition_revision = N`;
8. require exactly one updated row.

Therefore:

```text
stale expected revision
    -> DefinitionRevisionConflict

matching expected revision + exact target
    -> no-op success, changed=false

matching expected revision + material target
    -> revision advances exactly once
```

Slice 1.4 does not introduce mutation-command IDs or hidden retry machinery.
After an ambiguous client/network outcome, the caller reads current state and
makes a new explicit decision.

Revision 1 A11, A12, A36, and A37 are amended accordingly.

## F004 — MAJOR — lifecycle events are not bound to a definition revision

Revision 1 permitted Slice definition changes after lifecycle initialization
while lifecycle history remained in `{PROPOSED, DEFINING}`.

Accepted lifecycle events carry `slice_id` and lifecycle revision, but not a
Slice definition revision. Allowing definition mutation after lifecycle history
exists would therefore make the exact definition associated with an earlier
lifecycle event non-authoritative without adding a new cross-contract binding.

Adding definition revision to lifecycle events would expand Slice 1.4 into
lifecycle-contract redesign.

### Resolution — S14-D28

The minimum sufficient rule is:

```text
Slice definition update is allowed only while lifecycle is absent.
```

Once a `SliceLifecycle` has been initialized for a Slice, its Slice definition
is permanently frozen under Slice 1.4.

A handover-gate revision also freezes the definition, but in valid state the
lifecycle-existence rule is already sufficient once governed workflow begins.

This preserves exact causality without modifying lifecycle models/events.

Revision 1 S14-D15 is replaced by this rule.

Revision 1 A38–A41 are replaced by the criteria in Section 5 below.

---

# 3. Consolidated normative amendments

## S14-D29 — CREATE idempotency does not create an audit bypass

Revision 1 create behavior remains target-state idempotent only for the exact
revision-1 state:

```text
no current row + no history
    -> HUMAN CREATE at revision 1

current row at revision 1 + exact same value
    -> no-op observation, changed=false

same ID with different current value
    -> AlreadyExists

no current row + prior history/tombstone
    -> IdentifierRetired
```

The no-op path performs no new mutation and writes no new human audit record.

Because any material update advances the revision beyond 1, an exact-create retry
cannot silently cross an intervening definition update.

## S14-D30 — DELETE retry is an observation, not a second causal claim

Revision 1 delete retry semantics remain:

```text
current row + matching expected revision
    -> guarded DELETE revision

current row + stale expected revision
    -> DefinitionRevisionConflict

current row absent + latest history DELETE
    -> already_deleted=true, no new mutation

current row absent + no history
    -> NotFound
```

`already_deleted=true` means only that the requested target state is already
observable. It does not claim that the current caller performed the historical
delete.

## S14-D31 — Exact delete blockers must be explicit

To remove ambiguity from Revision 1 S14-D18, Project delete must explicitly prove
absence of all direct current-schema references that can retain Project
authority:

```text
current Slice rows
Baseline rows
GitHub installation rows
repository mutation authorization rows
```

Slice delete must explicitly prove absence of:

```text
lifecycle_current / lifecycle_events
handover_gate_revisions
gate_evaluation_records
executions
current child Slice parent references
current Slice dependency references
```

No `ON DELETE CASCADE` may be relied on to satisfy these guards.

A database foreign-key failure after the explicit guards is treated as a
fail-closed persistence-integrity/concurrency failure, not as the primary delete
policy.

Historical Project/Slice definition revision rows intentionally do not block
deletion of otherwise-unused current rows; they preserve the retired identity.

---

# 4. Revised expected implementation surface

Revision 1's implementation surface remains valid with these bounded
clarifications.

Expected additional impact:

```text
src/relay_engine/persistence/__init__.py
    remove/replace public raw Project/Slice creation exports as required by S14-D26

existing test setup
    migrate runtime-facing Project/Slice creation tests to the administration service
    retain explicit pre-v4 migration fixtures only where migration behavior is under test
```

No change is authorized to:

- lifecycle event/model schemas;
- governance engine semantics;
- GitHub/provider code;
- repository sync;
- board/UI;
- agent execution.

No new runtime dependency is required.

---

# 5. Revised / additional acceptance criteria

These criteria replace or extend Revision 1 where stated.

## Authority / mutation path

- **A75** Human-authorized subject baseline is exactly
  `670996ec43d77526adb0ea540c81a57d6e83453b`.
- **A76** Authority-recording design parent is exactly
  `1eaece23e31d831bfd2b27e55a898df389cc45fc`.
- **A77** No post-v4 public runtime persistence API can create a Project current
  row without the Slice 1.4 administration service.
- **A78** No post-v4 public runtime persistence API can create a Slice current
  row without the Slice 1.4 administration service.
- **A79** `SEED` revisions are migration-only and cannot be created by ordinary
  post-v4 runtime Project/Slice creation.

## Strict concurrency

- **A80** Any stale Project update fails with `DefinitionRevisionConflict`,
  including when the target equals the current value.
- **A81** Any stale Slice update fails with `DefinitionRevisionConflict`,
  including when the target equals the current value.
- **A82** Matching-revision exact-target update is a no-op without revision
  increment.
- **A83** Ambiguous client outcomes are reconciled by read + new explicit command;
  Slice 1.4 has no hidden retry or command-ID subsystem.

Revision 1 A11/A12/A36/A37 are interpreted through A80–A83.

## Lifecycle causality

Revision 1 A38–A41 are replaced by:

- **A84** Slice update is allowed only while no lifecycle current/history exists
  and all other structural/freeze guards pass.
- **A85** Lifecycle initialization permanently freezes Slice definition mutation
  under Slice 1.4.
- **A86** Any handover-gate revision freezes Slice definition mutation.
- **A87** Slice 1.4 does not add definition-revision fields to lifecycle
  snapshots/events.

## Explicit delete guards

- **A88** Project delete explicitly checks current Slice, Baseline, GitHub
  installation, and repository-mutation-authorization blockers.
- **A89** Slice delete explicitly checks lifecycle, gate, gate-evaluation,
  execution, child-parent, and incoming-dependency blockers.
- **A90** Delete policy does not rely on cascade behavior.
- **A91** A residual foreign-key failure after explicit guards fails closed and
  does not partially delete current/history state.

---

# 6. Required test amendments

In addition to Revision 1 tests, independent evaluation must require:

- stale exact-target Project update -> conflict;
- stale exact-target Slice update -> conflict;
- matching-revision exact-target update -> no-op;
- lifecycle initialized at PROPOSED -> Slice update frozen;
- lifecycle initialized then moved to DEFINING -> Slice update frozen;
- public persistence export audit proving no post-v4 raw Project/Slice creation
  bypass;
- migration v3 -> v4 seeds existing rows but ordinary post-v4 create produces
  CREATE, never SEED;
- each explicit Project delete blocker independently;
- each explicit Slice delete blocker independently;
- exact lineage/provenance assertions for `670996ec…`, `1eaece23…`, and
  `430b1e1f…`.

---

# 7. Review boundary

```text
Slice 1.4:
OPEN

Design authority:
RLY-S14-DESIGN-AUTH-001

Independent Revision 1 review:
RLY-S14-DESIGN-EVAL-001 — REVISE

Revision 2:
SUBMITTED FOR INDEPENDENT REVIEW

Implementation:
NOT AUTHORIZED

Human design acceptance:
NOT REACHED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Revision 2 must return to an independent design reviewer.

**Unblocked ≠ authorized.**
