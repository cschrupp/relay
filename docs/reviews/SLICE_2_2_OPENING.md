# Relay — Slice 2.2 Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-S22-OPEN-001`  
**Decision:** `OPEN`

## 1. Human authority

The Human explicitly approves opening:

`Slice 2.2 — Role Contracts`

This instruction opens Slice 2.2 only. It does not authorize implementation.

## 2. Exact opening basis

```text
Repository:
cschrupp/relay

Opening baseline:
f4697377e5e54de0bb6a3fb8ffd96805bd3790d2

B4 Human result acceptance:
RLY-S110-DOGFOOD-B4-R2-RESULT-ACCEPT-006 — ACCEPTED

B4 independent result:
RLY-S110-DOGFOOD-B4-R2-EXEC-EVAL-006 — PASS

B4:
COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED

Current operational Slice:
slc_01a15754-1123-7535-9ded-6a564518e347
Slice 2.2 — Role Contracts

Design branch:
design/2.2-role-contracts
```

B4 completion satisfies the prerequisite previously frozen for considering Slice 2.2 opening.

## 3. Existing proposal status

`docs/slices/SLICE_2_2_ROLE_CONTRACTS.md` already exists as a future-slice proposal.

Opening Slice 2.2 does not make that proposal an accepted design. It is planning input only until the separately authorized design is completed, independently evaluated, and Human-accepted.

## 4. Authorized state

```text
Slice 2.2:
OPEN

Design:
NOT AUTHORIZED BY THIS RECORD ALONE

Implementation:
NOT AUTHORIZED

Operational DB mutation:
NOT AUTHORIZED

Lifecycle mutation:
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Promotion / merge:
NOT AUTHORIZED
```

Opening permits governed planning and inspection needed for the explicit design gate.

## 5. Preserved invariants

- role, actor identity, runtime identity, model identity, authority, and capability remain distinct;
- runtime/provider capability cannot create Relay authority;
- implementation actor, independent evaluator, Human Authority, and promotion executor remain distinct governance subjects;
- roadmap placement, lifecycle state, proposal existence, or technical capability do not authorize work;
- protected verification assets require explicit role/authority treatment;
- executors may decompose only within current authorized work and may not extend the authoritative backlog;
- no authorized successor means bounded successful exhaustion such as `BACKLOG_EXHAUSTED`, not invention of new authoritative work.

## 6. Next authority boundary

The Human has separately approved Slice 2.2 design authorization. That authority must remain distinct from this opening record.

```text
Slice open != design accepted
Design authorized != design accepted
Design accepted != implementation authorized
Unblocked != authorized
```
