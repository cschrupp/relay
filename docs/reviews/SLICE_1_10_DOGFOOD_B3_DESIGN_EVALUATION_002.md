# Slice 1.10 Dogfood B3 — Forward Re-baseline / First Governed Work — Design Evaluation 002

**Document class:** Immutable independent design evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Record:** `RLY-S110-DOGFOOD-B3-DESIGN-EVAL-002`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Design authority:
RLY-S110-DOGFOOD-B3-DESIGN-AUTH-001 — AUTHORIZED

Prior evaluation:
RLY-S110-DOGFOOD-B3-DESIGN-EVAL-001 — REWORK

Rework baseline:
cc0731fb272bfb67e8b2ee9bf169373aa0f3c535

Corrective design candidate:
b032b0f28e1b476097b99b375be647cfe5ada64d

Changed path:
docs/slices/SLICE_1_10_DOGFOOD_B3_FORWARD_REBASELINE_FIRST_GOVERNED_WORK_DESIGN.md

Candidate CI:
PASS
```

## F001 closure — exact canonical Slice payload

F001 is closed.

The corrective candidate freezes one exact accepted-domain `Slice` payload for the existing adoption-frontier Slice:

```text
SliceId:
slc_01a15754-1123-7535-9ded-6a564518e347

ProjectId:
prj_018f47c1-7b2c-7abc-8def-123456789001

title:
Slice 2.2 — Role Contracts

parent_slice_id:
null

dependency_ids:
[]
```

The target payload also freezes, in order:

- nine exact `scope.in_scope` statements;
- five exact `scope.out_of_scope` statements;
- A01–A11 as an exact ordered acceptance-criteria tuple;
- `required: true` for all eleven criteria.

The design explicitly states that the accepted `Slice` model has no `objective` field and maps the previously described objective into the exact `scope.in_scope` payload. Surrounding prose cannot be used by a later materializer to paraphrase, add, remove, reorder, or derive target fields.

B3/B4/design acceptance/authority/architecture prerequisites are correctly classified as governance prerequisites/context, not Slice dependencies. No placeholder Slice identity is introduced to represent them.

This removes the prior ambiguity that would have required the later materializer to invent the operational payload.

## F002 closure — preparation and live materialization authority split

F002 is closed.

The corrected design now defines two distinct post-design stages.

### Stage A — materialization tooling/preparation

Stage A requires a separate implementation/preparation authority after B3 design acceptance.

It is bounded to:

- factoring the existing Slice update path into a caller-owned connection primitive while retaining the accepted public wrapper;
- factoring lifecycle initialization persistence into a caller-owned connection primitive while retaining the accepted public path;
- reusing/exposing the existing board projection against the caller-owned transaction snapshot as necessary;
- building one bounded one-shot coordinator;
- deterministic testing on disposable databases;
- proving exact-payload persistence, definition-update-before-lifecycle-init ordering, atomic commit/rollback, `PROPOSED` initialization, and readback behavior.

Stage A explicitly forbids writes to the real Relay operational database and requires independent technical review and Human acceptance of the exact tooling candidate.

### Stage B — consequential real B3 materialization

Stage B requires a separate immutable execution authority after accepted Stage A tooling.

The design requires that authority to pin at least:

- accepted tooling SHA and review/Human-acceptance identities;
- exact operational DB destination/identity and fresh pre-state evidence;
- ProjectId;
- existing adoption-frontier SliceId;
- exact expected definition revision;
- absence of lifecycle state/history;
- established origin identity/digests;
- exact frozen target Slice payload;
- exact Human ActorRef;
- exact authority identity;
- exact execution checkout/tooling inputs;
- one permitted transaction attempt.

The real transaction is one caller-owned `write_transaction` that:

1. revalidates all pins and preconditions;
2. performs the exact Slice definition update;
3. initializes lifecycle at revision zero / `PROPOSED`;
4. verifies exact history/origin/lifecycle/board readback before commit;
5. commits once or rolls back both writes.

Unreviewed Stage A orchestration code cannot be first exercised against the real adopted database under Stage B.

This satisfies the required separation between reversible preparatory engineering and consequential operational-state mutation.

## Preserved accepted direction

The corrective candidate preserves the previously accepted B3 direction without drift:

- retain the existing adoption-frontier Slice identity;
- do not create a duplicate first-work Slice;
- first governed work = Slice 2.2 — Role Contracts;
- authorized-work exhaustion remains integrated into Role Contracts;
- T1 and the adopted Baseline remain immutable;
- the operational DB remains the runtime source of truth;
- definition update precedes lifecycle initialization;
- lifecycle initializes at `PROPOSED`;
- roadmap/lifecycle/capability remain distinct from authority;
- executor decomposition cannot extend the authoritative backlog;
- discoveries remain `PROPOSED_WORK` until separately authorized;
- no authorized successor means successful `BACKLOG_EXHAUSTED` / STOP;
- B4 occurs after B3 materialization and before formal Slice 2.2 design opening;
- the current board limitation is preserved honestly as “not determinable” where evidence is unavailable rather than creating a new B3 roadmap subsystem.

## Independent evaluation

No remaining blocking discrepancy was found between candidate
`b032b0f28e1b476097b99b375be647cfe5ada64d` and
`RLY-S110-DOGFOOD-B3-DESIGN-AUTH-001`.

```text
RLY-S110-DOGFOOD-B3-DESIGN-EVAL-002 — ACCEPT
```

The B3 design is technically eligible for explicit Human design acceptance.

This ACCEPT does not authorize:

- Stage A tooling implementation/preparation;
- any write to the real operational database;
- B3 materialization;
- lifecycle initialization;
- B4 execution;
- Slice 2.2 design opening or implementation;
- OpenCode/AgentRuntime project execution;
- Phase 3;
- promotion.
