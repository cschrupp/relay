# Slice 1.10 Dogfood B3 — Forward Re-baseline / First Governed Work — Design Authorization

**Document class:** Immutable Human authorization record  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Record:** `RLY-S110-DOGFOOD-B3-DESIGN-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly opens B3 and authorizes B3 design.

This record authorizes design and read-only analysis only. It does not authorize mutation of the operational database, lifecycle initialization, implementation of Slice 2.2, B4 execution, or autonomous/OpenCode execution.

## Exact opening basis

```text
Repository:
cschrupp/relay

B2 Human real-adoption acceptance:
RLY-S110-DOGFOOD-B2-ADOPTION-ACCEPT-001 — ACCEPTED

B2 independently accepted terminal evidence:
89928fdfadbca85fafe549e8b496c7cb97192740dd2b28b6ea583d87c08bbe5c

T1:
2026-10-20T03:27:54.511113Z

Operational database:
/home/user/projects/relay-local-state/relay-operational.sqlite3

ProjectId:
prj_018f47c1-7b2c-7abc-8def-123456789001

Adoption-frontier SliceId:
slc_01a15754-1123-7535-9ded-6a564518e347

Adopted Baseline:
be1dd6f479d601c7ae2eea3985675f53ab748637

Post-B2 governance/design baseline:
ec5ccfcc6a20f41d12996e36efd5e64b0a6c1f24

B3 design branch:
design/1.10-dogfood-b3-forward-rebaseline-first-governed-work
```

The B3 design starts from the post-B2 governance baseline. The immutable T1 Baseline remains the adopted repository state and is not rewritten by this design opening.

## Product objective

Design the minimum forward re-baseline that turns Relay's truthful T1 adoption state into useful normal post-adoption governance.

The core question is:

> Given the adopted Project state, the Human's objectives, and the current repository/roadmap, what is the first normally governed work Relay should own, and how is that work represented durably without inventing history or creating a second source of truth?

## Human-directed first governed work target

The Human direction for B3 is:

```text
First governed work target:
Slice 2.2 — Role Contracts

Required integrated concern:
authorized-work exhaustion
```

The B3 design must treat authorized-work exhaustion as part of the concrete Role Contracts / work-authority problem, not as an independent governance program unless the design proves a separate increment is technically necessary.

The target outcome is that executable work remains traceable to an authoritative work reference; autonomous decomposition may occur only inside the current authorized item; future discoveries remain non-authoritative until promoted; and no authorized successor results in a successful stop such as `BACKLOG_EXHAUSTED`, not invention of new work.

This Human direction establishes the intended first work subject. It does not authorize Slice 2.2 implementation.

## Required design subjects

### 1. Authoritative B3 inputs

Define the exact inputs used for forward re-baselining:

- immutable T1 Project adoption record and orientation;
- exact adopted Baseline;
- current operational Project/Slice identities;
- current repository state and accepted post-T1 governance records;
- Human-confirmed objective, constraints, and first governed focus from B1;
- current accepted roadmap and architecture;
- selected legacy context only when needed for a present/future decision.

The design must specify precedence when a T1 orientation, current repository state, and later accepted post-T1 governance record differ.

### 2. Single-source-of-truth transition

B3 must end the temporary dependence on conversation reconstruction.

It must define which facts become durable Relay operational state and which remain repository documentation/context.

The operational database must remain the authoritative runtime Project/Slice state. Repository documents may project or explain that state but must not create a competing operational backlog.

### 3. Adoption-frontier Slice refinement

B2 already created:

`slc_01a15754-1123-7535-9ded-6a564518e347`

as the NATIVE_RELAY adoption-frontier Slice.

B3 must determine how this existing Slice is refined into the first normally governed work item rather than creating a duplicate first-work identity without necessity.

The preferred design direction is to revise the existing Slice definition so it represents the Human-directed first governed work target:

`Slice 2.2 — Role Contracts`

with authorized-work exhaustion integrated into its objective/acceptance contract.

If the accepted domain model makes that refinement invalid, the design must prove why and define the minimum truthful alternative.

### 4. Definition and lifecycle write path

B3 design must define the exact accepted write path into the operational database.

Requirements:

- use existing Relay Project/Slice administration and lifecycle machinery;
- no raw SQL as a new governance path;
- no duplicate B3-specific definition engine;
- preserve immutable definition history and actor/time/reason provenance;
- preserve project-scoped NATIVE_RELAY origin semantics;
- specify when lifecycle initialization occurs;
- specify the intended phase after B3 materialization;
- no lifecycle initialization during design-only work.

Because no public CLI currently exposes these mutations, the design must explicitly choose the bounded execution seam for B3 materialization rather than silently inventing one.

### 5. Forward work model

Produce the minimum useful CURRENT / NEXT / LATER / BLOCKED model after B3.

At minimum resolve:

- CURRENT — first governed work and its current lifecycle/design state;
- NEXT — the authorized successor only when established;
- LATER — planned but unauthorized roadmap work;
- BLOCKED — actual blockers only, without inferring that historical absence means none exist.

The model must clearly distinguish:

```text
planned != open
open != design-authorized
design-authorized != implementation-authorized
unblocked != authorized
proposed future work != executable work
```

### 6. First governed work contract

For the Role Contracts target, B3 must define enough scope and acceptance criteria that a later Slice 2.2 design authority can proceed without re-inventing the project frontier.

At minimum include:

- role identity/version/class;
- actor/runtime/model identity separation;
- capability versus authority separation;
- allowed/prohibited actions;
- evaluator/Human/promotion separation;
- protected verification assets;
- evidence obligations;
- escalation semantics;
- executor authority exhaustion;
- successor-work resolution;
- `PROPOSED_WORK` versus authorized work;
- `BACKLOG_EXHAUSTED` terminal-success semantics;
- explicit prohibition on executors self-extending the authoritative backlog.

B3 must not design all implementation details of Slice 2.2. It should establish the work boundary and acceptance target, then stop at the normal Slice 2.2 design gate.

### 7. Dependencies and sequencing

Confirm the forward sequence or identify a concrete blocker:

```text
B3 forward re-baseline
  -> B4 onboarding dogfood acceptance
  -> Slice 2.2 Role Contracts
  -> Slice 2.3 Context / Work-Packet Contract
  -> Slice 2.4 Execution Workspace Authority
  -> Phase 3 governed autonomous engineering
```

The design must decide whether B4 should occur immediately after B3 materialization or whether the first governed Slice 2.2 design opening is part of the evidence B4 needs. Prefer the minimum sequence that actually proves onboarding usability.

### 8. B3 materialization and evidence

Define the later, separately authorized B3 execution transaction:

- exact source state;
- exact Human actor;
- exact definition revision(s);
- lifecycle initialization/transition if required;
- board/read-model result;
- operational DB integrity verification;
- evidence proving the first governed work is visible without chat reconstruction;
- rollback/fail-closed behavior.

### 9. B3/B4 boundary

B3 establishes the truthful future-work model and first governed work.

B4 evaluates whether a fresh operator can continue the project from Relay state without reconstructing history or relying on this conversation.

B3 must not self-accept B4.

## Design invariants

```text
T1 is immutable.
The adopted Baseline is immutable history.
Post-T1 current state may advance without rewriting T1.
One operational database remains the runtime source of truth.
The existing adoption-frontier Slice is preferred over duplicate first-work identity.
Definition revision is not lifecycle transition.
Lifecycle state is not authority.
Roadmap placement is not authority.
Agent/runtime capability is not authority.
Executor decomposition may not extend the authoritative backlog.
No authorized successor => BACKLOG_EXHAUSTED / STOP.
```

## Allowed during B3 design

- read-only inspection of the operational database;
- read-only inspection of repository/code/docs/history needed for current/future decisions;
- architecture/design analysis;
- creation of B3 design documents and independent review evidence on this design branch;
- bounded use of BMAD inside the Meta Lane as a disposable planning/decomposition aid, provided BMAD output remains non-authoritative and does not alter Relay scope.

## Explicitly not authorized

- any write to `/home/user/projects/relay-local-state/relay-operational.sqlite3`;
- definition revision or lifecycle initialization of the adoption-frontier Slice;
- creation of a second first-work Slice;
- implementation of Slice 2.2;
- Role Contract source/schema implementation;
- implementation of authorized-work exhaustion;
- Work Packet or Workspace Authority implementation;
- B4 acceptance execution;
- OpenCode/AgentRuntime-managed project execution;
- Phase 3 opening;
- main/canonical promotion;
- rewriting T1 or B2 adoption evidence;
- reconstruction of pre-T1 Relay lifecycle.

## Required B3 design deliverable

Produce:

`docs/slices/SLICE_1_10_DOGFOOD_B3_FORWARD_REBASELINE_FIRST_GOVERNED_WORK_DESIGN.md`

The design must be independently reviewed before Human design acceptance or any operational-state mutation is authorized.

## Success condition

B3 design succeeds when an implementer can later perform one bounded, separately authorized post-T1 materialization equivalent to:

```text
accepted T1 state
  + current repository/governance state
  + Human-directed first work target
        ↓
refine existing adoption-frontier Slice
        ↓
initialize normal post-T1 governance state through accepted Relay machinery
        ↓
CURRENT / NEXT / LATER / BLOCKED readable from Relay
        ↓
first governed work boundary = Role Contracts + authority exhaustion
        ↓
STOP at normal downstream authority gate
```

without creating a second source of truth and without relying on chat reconstruction.

## State after this authorization

```text
B0-F: COMPLETE / HUMAN ACCEPTED
B1: COMPLETE / HUMAN ACCEPTED
B2: COMPLETE / INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED
B3: DESIGN OPEN / AUTHORIZED
B3 operational materialization: NOT AUTHORIZED
B4: NOT OPEN / NOT AUTHORIZED
Slice 2.2 implementation: NOT AUTHORIZED
Phase 3: NOT OPEN / NOT AUTHORIZED
```
