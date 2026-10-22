# Relay — Slice 2.3 Design Revision 2 Rework Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Authority:** `RLY-S23-DESIGN-REWORK-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes a bounded Slice 2.3 Design Revision 2 rework in response to:

`RLY-S23-DESIGN-EVAL-001 — REWORK`

This authority permits design correction only.

## Exact rework basis

```text
Repository:
cschrupp/relay

Canonical Slice 2.3 opening baseline:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Design branch:
design/2.3-context-work-packet-contract

Revision 1 candidate:
8e3cb2df658711cd3e18d364cf19fa5332b2ab2f

Revision 1 blob:
d11529c5fdf068a142e79171642cdb735dc290cd

Independent evaluation:
RLY-S23-DESIGN-EVAL-001 — REWORK

Evaluation commit / rework parent:
f0383fe624e99134586198cfcb9be77aae2fb014
```

## Authorized rework scope

Revision 2 must close exactly:

```text
F001 — exact-subject-bound conformance evidence
F002 — recursive canonical identity for every normative collection
F003 — deterministic required-context materialization / reproduction contract
```

The Revision 1 architecture that independently passed review must otherwise remain in force.

## F001 required result

Externally supplied conformance facts must be bound to the exact subjects they attest.

The corrected design must prevent a fact/evaluation established for Packet A, Context A, authority set A, policy/profile A, RoleContract A, accepted-design set A, source baseline A, or protected-verification requirement A from satisfying Packet B.

Plural external facts must be keyed/bound per exact reference or to an exact digest-bound set.

Aggregate unkeyed statuses are insufficient.

## F002 required result

Canonical identity must be closed over every normative sequence reachable from WorkPacket and ContextManifest.

For every such collection Revision 2 must state either:

```text
ORDER IS NORMATIVE
```

or:

```text
ORDER IS NON-SEMANTIC
-> exact canonical ordering is mandatory
-> noncanonical input is rejected
```

The correction must cover embedded/referenced baseline semantics, normalized intent, context/source/material refs, and any new Revision 2 fact/ref collections.

Hard-coded canonical JSON/digest vectors must be required for implementation tests.

## F003 required result

Every required ContextManifest entry must bind an exact materialization source sufficient for an external consumer to obtain exact bytes/provenance deterministically and then verify the expected digests.

This is a contract boundary only.

Revision 2 must not add:

- persistence;
- a content store;
- a vector database;
- retrieval/ranking;
- network access;
- provider calls;
- runtime execution;
- workspace enforcement.

The exact materialization implementation remains outside Slice 2.3.

Digest-known but non-materializable required content must fail closed.

## Non-blocking IR clarification adopted

If control-plane material is mirrored into ContextManifest for runtime/model visibility—authority/non-authority, RoleContract, policy/profile, or accepted design—the mirrored material must exact-match the WorkPacket control reference it represents.

Conflicting mirrored material must fail closed rather than merely being labeled non-authoritative.

## Preservation requirements

Revision 2 must preserve:

- WorkPacket != authority;
- ContextManifest != authority;
- Human root authority external to packet construction;
- provider-neutral planning normalization;
- exact RoleContractRef transport;
- Slice 2.2 input/output mapping;
- Slice 2.1 runtime ownership;
- Slice 2.4 workspace enforcement ownership;
- Phase 3 orchestration ownership;
- protected-verification permission != authority;
- amendment/new-digest/renewed-authority semantics;
- PROPOSED_WORK non-authority;
- successor authority non-inheritance;
- BACKLOG_EXHAUSTED semantics;
- no new UUID prefix for WorkPacket/ContextManifest;
- no initial database migration/persistence.

## Explicitly not authorized

This authority does not permit:

- implementation/source/test changes;
- database migration;
- operational DB mutation;
- lifecycle mutation;
- production WorkPacket creation/wiring;
- context storage/retrieval implementation;
- runtime/provider/model execution;
- workspace enforcement;
- Slice 2.4 opening;
- Phase 3 opening;
- real-project agent execution;
- canonical/main promotion.

## Deliverable

Create one lockable design amendment:

`docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN_REV2_AMENDMENT.md`

Revision 2 is normative over Revision 1 where they differ.

After the amendment is complete, STOP for independent design re-review.

**Rework authority != design acceptance. Design acceptance != implementation authority.**
