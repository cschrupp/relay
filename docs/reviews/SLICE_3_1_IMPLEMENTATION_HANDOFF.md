# Relay — Slice 3.1 Coding Agent Execution — Codex Implementation Handoff

**Document class:** Immutable implementation handoff  
**Status:** IMMUTABLE / READY FOR IMPLEMENTER  
**Date:** 2026-10-25  
**Project:** Relay  
**Slice:** 3.1 — Coding Agent Execution  
**Handoff:** `RLY-S31-IMPL-HANDOFF-001`  
**Implementation authority:** `RLY-S31-IMPL-AUTH-001 — AUTHORIZED`

## Exact basis

```text
Accepted design:
a28a9b88ddd85cd1a32932b30c4e0e668f23b557

Independent design evaluation:
RLY-S31-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S31-DESIGN-ACCEPT-001 — ACCEPTED
commit e8678b86a5a3b87aa0bf71fa0b9ec38d4439eaa0

Implementation authority:
RLY-S31-IMPL-AUTH-001 — AUTHORIZED
commit 24c6128a22f3322c257c7cfdb48cf376bcfe6962

Implementation branch:
implementation/3.1-coding-agent-execution
```

## Implementer instruction

Implement the complete bounded Slice 3.1 deterministic orchestration substrate described by:

- `docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION_DESIGN.md`;
- `docs/reviews/SLICE_3_1_IMPLEMENTATION_AUTHORIZATION.md`.

Treat both as mandatory. Where they appear to differ, the accepted design owns semantics and the implementation authority owns implementation scope.

The goal is one terminal candidate, not a sequence of Human-gated microtasks.

## Required result

Create the minimum `relay_engine.coding_execution` package that composes the accepted Slices 2.1–2.5 and can deterministically prove:

```text
fresh READY AuthorityCandidate
    -> exact Human-grant binding
    -> exact grant-time reservation verification
    -> exact authority-linked WorkPacket conformance
    -> exact WorkPacketRef
    -> WorkspacePlan resolution from that ref
    -> workspace/runtime identity binding
    -> intended-attempt / ExecutionId binding
    -> exact ExecutionSubject
    -> fail-closed admission
    -> fake-runtime governed execution
    -> exact terminal result/evidence
    -> immutable evaluator handoff
```

All real Human-grant/reservation mutation and live runtime/provider/model execution remain outside this implementation.

## Worker discretion

Codex owns internal decomposition. It may make cohesive implementation commits, repair tests, and refactor inside the authorized new package without returning for routine approval.

Do not split the work into Relay WorkPackets or ask for permission at each internal milestone.

## Hard stops

Immediately stop and report if implementation requires:

- a substantive change to accepted Slices 2.1–2.5;
- a DB/schema migration;
- production Human Authority mutation;
- production consumable reservation/consumption mutation;
- a live provider/model/OpenCode call;
- credentials;
- real-project execution;
- canonical Git promotion;
- a second planner/lifecycle/authority system.

## Required validation

Run all focused Slice 3.1 tests, then the complete existing quality suite defined in `RLY-S31-IMPL-AUTH-001`.

## Terminal report

Return one implementation candidate with exact SHA, changed paths, test/CI evidence, A01–A22 coverage matrix, and zero live provider/model/runtime calls.

Then:

```text
STOP FOR SOL INDEPENDENT IMPLEMENTATION REVIEW
```
