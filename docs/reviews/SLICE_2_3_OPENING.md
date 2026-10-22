# Relay — Slice 2.3 Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Record:** `RLY-S23-OPEN-001`  
**Decision:** `OPEN`  
**Slice:** 2.3 — Context / Work-Packet Contract

## 1. Human Authority

The Human directed Relay to continue from the canonical post-Slice-2.2 state.

At the current governance frontier, this is recorded as explicit opening of:

`Slice 2.3 — Context / Work-Packet Contract`

Opening is limited to governed design work. It does not authorize implementation.

## 2. Exact opening basis

```text
Repository:
cschrupp/relay

Canonical main / opening baseline:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Slice 2.2:
COMPLETE / ACCEPTED / CLOSED

Slice 2.2 closure evaluation:
RLY-S22-CLOSE-EVAL-001 — ACCEPT

Slice 2.2 accepted implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Existing Slice 2.3 proposal:
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT.md

Proposal blob:
575f3ae1bca0752f0bd5840559d4dea0010352f4

Design branch:
design/2.3-context-work-packet-contract
```

The opening baseline is the documentation-consistent canonical state after Slice 2.2 closure.

## 3. Opening objective

Slice 2.3 owns the deterministic contract that transports exact governed work and exact effective context between already-established Relay authority, Role Contracts, runtime capability, and later workspace enforcement.

The design must make an exact Work Packet reproducible from durable Relay state plus explicitly authorized inputs.

The Slice must preserve the already-accepted invariant:

```text
packet != authority
context != authority
prompt != authority
planning artifact != authority
normalization != authority
role != authority
runtime capability != authority
workspace capability != authority
```

## 4. Existing proposal status

The existing proposal is planning input only.

Opening Slice 2.3 does not make the proposal an accepted design and does not authorize its implementation.

The design may refine the proposal where needed to align it with accepted Slice 2.1 runtime semantics and accepted Slice 2.2 Role Contract semantics.

## 5. Authorized state

```text
Slice 2.3:
OPEN

Design:
SEPARATELY AUTHORIZED BY RLY-S23-DESIGN-AUTH-001

Implementation:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Production Work Packet wiring:
NOT AUTHORIZED

Workspace/path/tool/network enforcement:
NOT AUTHORIZED — Slice 2.4 ownership

Agent/runtime execution:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED BY THIS RECORD
```

No new operational SliceId, database row, lifecycle transition, or execution state is created by this opening record.

## 6. Preserved boundaries

Slice 2.3 must:

- reuse ProjectId, SliceId, Baseline/CommitRef, ContentDigest, Artifact identity, and other existing exact identity values where applicable;
- transport exact RoleContractRef values rather than duplicate Slice 2.2 role semantics;
- consume established authority/policy/profile facts without creating or validating Human root authority;
- treat normalized planning intent as non-authoritative until separately bound by exact Relay authority;
- keep workspace enforcement in Slice 2.4;
- keep runtime execution/orchestration in Phase 3;
- keep provider/model invocation in Slice 2.1/Phase 3 boundaries;
- preserve PROPOSED_WORK and BACKLOG_EXHAUSTED semantics from Slice 2.2.

## 7. Next gate

The separately authorized design must produce one exact design candidate for independent review.

```text
Slice open != design accepted
Design authorized != design accepted
Design accepted != implementation authorized
Packet conformance != work authority
Unblocked != authorized
```
