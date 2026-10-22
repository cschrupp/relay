# Slice 1.10 Dogfood B3 — Forward Re-baseline / First Governed Work — Design Evaluation 001

**Document class:** Immutable independent design evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Record:** `RLY-S110-DOGFOOD-B3-DESIGN-EVAL-001`  
**Outcome:** `REWORK`

## Evaluated subject

```text
Design authority:
RLY-S110-DOGFOOD-B3-DESIGN-AUTH-001 — AUTHORIZED

Authority baseline:
7a214973be618e0e648fcbb2994e675f99f84a3b

Design candidate:
290a6c7ab6b9c23926ef1831c2a1c7a8273e95ec

Changed path:
docs/slices/SLICE_1_10_DOGFOOD_B3_FORWARD_REBASELINE_FIRST_GOVERNED_WORK_DESIGN.md

Candidate CI:
PASS
```

## Accepted direction

The following B3 design direction is sound and should be preserved in rework:

- retain the existing adoption-frontier Slice identity `slc_01a15754-1123-7535-9ded-6a564518e347`;
- refine that Slice into the first normal post-adoption governed work rather than create a duplicate identity;
- first governed work target = Slice 2.2 — Role Contracts;
- authorized-work exhaustion is integrated into the Role Contracts boundary rather than split into an independent governance program;
- preserve immutable T1 and adopted Baseline;
- operational database remains runtime source of truth;
- update the Slice definition before lifecycle initialization;
- initialize lifecycle at `PROPOSED`, not DESIGNING/READY/IMPLEMENTING;
- `PROPOSED_WORK` is non-authoritative future work;
- no authorized successor means `BACKLOG_EXHAUSTED` / STOP;
- B4 should occur after B3 materialization and before formal Slice 2.2 design opening;
- no B3-specific backlog, lifecycle, origin, or board subsystem.

No finding reopens these decisions.

## F001 — Proposed first-work definition is not yet a deterministic `Slice` payload

**Severity:** BLOCKING DESIGN PRECISION

The candidate correctly identifies the accepted `Slice` domain object as the durable first-work definition, but Section 4.2 expresses fields that the actual accepted model does not have.

The accepted `Slice` model is:

```text
id
project_id
title
scope.in_scope
scope.out_of_scope
acceptance_criteria
parent_slice_id
dependency_ids
```

There is no `objective` field.

Also, `dependency_ids` accepts only actual `SliceId` values. The candidate's prose “Dependencies” includes B3 acceptance/materialization, B4 dogfood, and accepted governance/lifecycle/evaluation contracts while simultaneously stating that no new operational dependency Slice is created. Those are governance prerequisites/context, not representable Slice dependency IDs.

As written, a later materializer would have to invent the mapping from:

- “Objective”
- “Dependencies”
- the listed in-scope/out-of-scope statements
- the eleven acceptance criteria

into the exact accepted `Slice` payload.

That violates the B3 requirement that the first governed work definition be deterministic before consequential materialization.

### Required correction

Freeze the exact canonical target `Slice` field mapping.

At minimum specify:

```text
id = existing adoption-frontier SliceId
project_id = existing ProjectId
title = exact string

scope.in_scope = exact ordered tuple of strings
scope.out_of_scope = exact ordered tuple of strings

acceptance_criteria =
  exact ordered tuple of:
    key
    statement
    required

parent_slice_id = exact value
dependency_ids = exact tuple of existing SliceIds
```

If the prose “Objective” is retained for readability, explicitly state where that semantic content lives in the actual `Slice` payload; do not imply a nonexistent model field.

Classify B3/B4/design/authority prerequisites separately as governance prerequisites/context. Do not encode them into `dependency_ids` unless they are represented by real operational Slice identities and the design intentionally chooses that relationship.

Preferred result for the current B3 direction is likely `dependency_ids = ()`, unless read-only inspection establishes an actual current Slice dependency that must be preserved.

## F002 — Preparatory tooling and consequential live materialization are not sufficiently separated

**Severity:** BLOCKING AUTHORITY BOUNDARY

Section 7 correctly identifies that the current public paths cannot atomically compose:

- Slice definition update;
- lifecycle initialization;
- same-snapshot board verification.

It therefore proposes factoring connection-owned primitives and creating a one-shot coordinator.

That is reasonable technically, but the current sequence says, in effect, “after a separate B3 materialization authority, use one reviewed one-shot entry point,” while the required factoring/coordinator does not yet exist.

This leaves ambiguous whether the same consequential authority that permits writing the real adopted operational database would also permit creating/debugging the new orchestration code that performs that write.

Relay should preserve the preparation/execution separation already established in prior consequential work.

### Required correction

Define a two-stage post-design boundary:

```text
Stage A — B3 materialization tooling/preparation
  separately authorized implementation/preparation
  factor only the minimum connection-owned primitives needed
  build the bounded one-shot coordinator
  deterministic tests on disposable databases
  prove atomic rollback, exact payload, lifecycle-init, and board readback
  no write to the real Relay operational database
  independent review / Human acceptance of the tooling candidate

Stage B — real B3 materialization
  separate consequential execution authority
  pin:
    accepted tooling SHA
    exact operational DB identity/hash or equivalent fresh-state evidence
    exact Project/Slice identities
    exact pre-state revision/lifecycle/origin facts
    exact canonical target Slice payload
    exact Human actor / execution subject
  execute one real atomic transaction
  collect terminal evidence
  stop for independent result review
```

The design does not need to create bureaucracy beyond these boundaries. Stage A may remain a small implementation increment. The important requirement is that unreviewed orchestration code is not first exercised against the real adopted Relay database under the same gate that authorizes the consequential mutation.

## Other observations

The candidate correctly notes the current board limitation: there is no dedicated persisted four-column CURRENT/NEXT/LATER/BLOCKED roadmap model. Preserving “not determinable” where current projections lack evidence is acceptable for B3. Do not create a new roadmap subsystem under this rework.

The proposed lifecycle order is valid relative to current accepted behavior: `update_slice` rejects mutation once lifecycle or handover history exists, so definition refinement must occur before lifecycle initialization. Atomic composition in that order is appropriate.

The accepted persistence layer already provides caller-owned lifecycle mutation helpers for later lifecycle changes; factoring initialization and Slice definition update into connection-owned equivalents is a bounded refactor rather than a new domain model.

## Disposition

```text
RLY-S110-DOGFOOD-B3-DESIGN-EVAL-001 — REWORK

F001 — exact canonical Slice payload mapping required
F002 — preparatory tooling authority must be separated from real DB materialization authority

B3 design remains OPEN / AUTHORIZED.
B3 operational materialization remains NOT AUTHORIZED.
B4 remains NOT OPEN / NOT AUTHORIZED.
Slice 2.2 implementation remains NOT AUTHORIZED.
```

Rework should be a narrow amendment or direct candidate correction limited to F001 and F002. Do not reopen the accepted B3 direction.
