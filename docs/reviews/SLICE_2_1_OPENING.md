# Relay — Slice 2.1 Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-S21-OPEN-001`  
**Decision:** `OPEN`

## 1. Human authority

The Human explicitly instructed:

> proceed with Open Relay Slice 2.1 — Agent Runtime Contract

This instruction opens Slice 2.1 only.

## 2. Exact opening basis

```text
Repository:
cschrupp/relay

Canonical main at opening:
eac62b054af3815cc179c95d0d31aa96f9a374e3

Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Phase 2:
OPEN — RLY-P2-OPEN-001

Slice:
2.1 — Agent Runtime Contract
```

## 3. Authorized state

```text
Slice 2.1:
OPEN

Design:
NOT AUTHORIZED

Implementation:
NOT AUTHORIZED

Sidecar/runtime experiment:
NOT AUTHORIZED BY THIS RECORD

OpenCode integration:
NOT AUTHORIZED

Provider/model execution:
NOT AUTHORIZED

Relay coding-agent execution:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED
```

Opening permits governed planning, inspection of the existing proposal and architectural context, and preparation for the next explicit Human gate.

## 4. Existing proposal status

`docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT.md` exists as a proposal describing the intended AgentRuntime boundary and OpenCode-first direction.

Opening the Slice does not make that proposal an accepted design. Any architecture, contract, sidecar-evidence plan, provider/runtime choice, permission model, workspace semantics, event model, or failure model remains subject to separately authorized design and independent design review.

## 5. Preserved invariants

- Relay governance remains authoritative over runtime/session state.
- Runtime permissions may enforce Relay authority but cannot create Relay authority.
- Phase 1 remains the accepted deterministic baseline under active hardening.
- Phase 1 governance-critical defects block affected Phase 2 work.
- Agent execution remains fail-closed and unauthorized until explicitly granted.

## 6. Next authority boundary

The next legitimate Human gate is Slice 2.1 design authorization.

```text
Slice open ≠ design authorized
Design complete ≠ design accepted
Design accepted ≠ implementation authorized
Unblocked ≠ authorized
```
