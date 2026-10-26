# Relay — Slice 3.1 Coding Agent Execution — Human Design Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE / ACCEPTED  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Record:** `RLY-S31-DESIGN-ACCEPT-001 — ACCEPTED`

## 1. Human decision

The Human accepts the exact corrective Slice 3.1 normative design:

`a28a9b88ddd85cd1a32932b30c4e0e668f23b557`.

Independent design evaluation:

`RLY-S31-DESIGN-EVAL-002 — ACCEPT`

Evaluation record commit:

`62799a886affe070f34298b0743cbcc20b141d69`.

The accepted design artifact is:

`docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION_DESIGN.md`

at design revision 2 with registered digest:

`sha256:f988c859de6b2127efde63436a81a89e5aa4a37f1104e859fa58c829e1258f78`.

## 2. Acceptance scope

Human acceptance freezes the design semantics for Slice 3.1 implementation planning.

In particular, accepted semantics include:

- Slice 2.5 `AuthorityCandidate` is the exact Human-grant subject;
- Human grant atomically reserves applicable consumables against candidate digest + intended attempt identity;
- Slice 3.1 verifies but does not create/move reservation state;
- authority-linked WorkPacket materialization and conformance precede exact `WorkPacketRef`;
- `WorkspacePlan` resolution follows the exact conformed WorkPacketRef;
- `ProjectStateRequest.intended_attempt_id` maps one-to-one to Slice 2.1 `ExecutionId`;
- runtime sessions/handles remain subordinate execution evidence;
- WorkPacket remains the authoritative external unit;
- agent-local decomposition, milestones, retries and subagents remain non-authoritative;
- `ProposedWorkObservation` is evidence, not terminal status or authority;
- independent evaluation remains separate from implementation;
- no automatic push, merge, canonical mutation or promotion;
- accepted Slices 2.1–2.5 remain owning contracts and are not reopened by this acceptance.

## 3. Preserved non-authority

This Human design acceptance does not by itself authorize:

- implementation;
- production authority issuance/reservation mutation;
- operational database/schema changes;
- production WorkPacket or WorkspacePlan lifecycle wiring;
- live AgentRuntime/OpenCode/provider/model execution;
- credential use;
- network side effects;
- real-project autonomous coding execution;
- canonical promotion.

Those require separate exact authority.

## 4. Disposition

```text
RLY-S31-DESIGN-ACCEPT-001 — ACCEPTED

Exact design:
a28a9b88ddd85cd1a32932b30c4e0e668f23b557

Independent design evaluation:
RLY-S31-DESIGN-EVAL-002 — ACCEPT

Slice 3.1:
OPEN

Design:
ACCEPTED

Implementation:
NOT AUTHORIZED BY THIS RECORD

Execution:
NOT AUTHORIZED
```

**Design acceptance freezes the accepted design; it does not itself grant implementation or execution authority.**
