# Phase 2 — Project State Resolution and Authority Compilation Strategic Amendment Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-24  
**Project:** Relay  
**Authority ID:** `RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED`  
**Subject baseline:** `73a1525282e41464d31cd458b8a50703bfa9553c`  
**Authority type:** documentation / architecture / roadmap / backlog strategic amendment only

## 1. Human decision

The Human Authority accepts the following strategic direction:

> Accepted project knowledge is not operationally durable until Relay can resolve it into machine-enforceable prerequisites, inherited constraints, prohibitions, applicability judgments, and evidence lineage for subsequent authority.

Relay must not depend on an agent reconstructing these obligations from historical prose or conversation context.

The strategic capability is named:

```text
Project State Resolution
        +
Authority Compilation
```

It is proposed as a new final Phase-2 foundation slice:

```text
Slice 2.5 — Project State Resolution and Authority Compilation
```

Slice 2.5 must be completed before Phase 3 governed autonomous execution becomes eligible to open.

## 2. Failure class being addressed

This amendment responds to observed recurring failures across governed projects:

- prerequisite knowledge exists but is not enforced;
- accepted rules are promoted into documentation without becoming executable gates;
- authority is issued from a locally correct but incomplete view of predecessor state;
- operational prerequisites such as environment qualification or smoke tests disappear from later execution authority;
- architecture ownership is rediscovered and duplicate components are proposed;
- previously rejected approaches reappear because their negative disposition is absent from active context;
- historical evidence is confused with current applicability or present authority.

Representative example:

```text
requested:
    SCIENTIFIC_LIVE_AUTH

actual prerequisite chain:
    accepted predecessor
    -> environment qualification
    -> live smoke
    -> smoke acceptance
    -> scientific live authority
```

The absence of one executable dependency edge must prevent issuance of the downstream authority.

## 3. Architectural constraints

The new capability must extend existing Relay architecture rather than create a second governance system.

Frozen constraints:

```text
Relay remains the only governance state machine.

WorkPacket remains the authoritative external work unit.

Human Authority remains the source of authorization.

Independent evaluation remains independent.

AgentRuntime remains execution, not project authority.

Project State Graph is a derived projection over canonical Relay records,
not a second source of truth.

Authority Compiler produces an authority candidate / eligibility result.
It does not grant Human authority.

Runtime-local plans and subagent tasks remain non-authoritative.

Historical evidence is immutable.
Current applicability is derived.
```

## 4. Required future capability families

Slice 2.5 design must cover at least:

1. durable invariant / constraint representation;
2. exact qualification facts and present applicability evaluation;
3. requirement/dependency edges between governed outcomes;
4. prohibitions and superseded/rejected dispositions;
5. architecture responsibility ownership and collision detection;
6. deterministic project-state resolution;
7. authority candidate compilation;
8. READY / BLOCKED / INDETERMINATE eligibility semantics;
9. inherited constraint injection into WorkPackets or their construction path;
10. evidence applicability / invalidation rules without rewriting historical evidence;
11. operational prerequisite resolution;
12. Knowledge Delta proposal and accepted promotion back into canonical state.

## 5. Required decision distinctions

The future design must distinguish at minimum:

```text
historical fact
current applicability
current state
authority
```

and:

```text
SUPERSEDED
REJECTED
PROHIBITED_UNLESS_REAUTHORIZED
```

A historical PASS must remain historically true even when its applicability to a later execution becomes false.

A prohibition must not be silently resurrected by a future agent.

## 6. Authority compilation principle

The intended future flow is:

```text
Human / SOL requests an outcome
        ↓
Project State Resolver
        ↓
resolve:
  current baseline
  accepted predecessors
  active invariants
  qualification facts
  evidence applicability
  prohibitions
  responsibility ownership
        ↓
Authority Compiler
        ↓
READY / BLOCKED / INDETERMINATE
        ↓
if READY:
  complete authority candidate
        ↓
Human Authority
        ↓
WorkPacket
        ↓
execution
```

A compiler result is not authorization.

## 7. Knowledge Delta principle

Independent execution/review may discover durable knowledge, but no evaluator or worker may silently promote it into project authority.

Conceptual flow:

```text
execution / independent evaluation
        ↓
Knowledge Delta proposal
        ↓
appropriate governance / Human acceptance
        ↓
canonical Relay state
        ↓
future State Resolver
```

Possible Knowledge Delta classes include:

- NEW_INVARIANT;
- NEW_PREREQUISITE;
- NEW_APPLICABILITY_RULE;
- NEW_PROHIBITION;
- NEW_RESPONSIBILITY_CLAIM;
- INVALIDATION_RULE.

The exact production schema is future Slice 2.5 design scope.

## 8. Roadmap decision

The Phase-2 frontier becomes:

```text
2.1 Agent Runtime Contract                         COMPLETE / CLOSED
2.2 Role Contracts                                 COMPLETE / CLOSED
2.3 Context / Work-Packet Contract                 COMPLETE / CLOSED
2.4 Execution Workspace Authority                  CURRENT / OPEN
2.5 Project State Resolution & Authority Compilation
                                                   PROPOSED / NOT OPEN / NOT AUTHORIZED
```

Phase 3 remains:

```text
NOT OPEN / NOT AUTHORIZED
```

and gains the explicit prerequisite:

```text
Slice 2.5 COMPLETE / ACCEPTED / CLOSED
```

in addition to existing prerequisites.

## 9. What this authority permits now

This authority permits documentation-only work to:

- create the architecture direction document;
- create the proposed Slice 2.5 definition;
- update the current build-plan roadmap projection;
- update the current development TODO/backlog projection;
- update the current baseline projection;
- update architecture navigation;
- mechanically register these artifacts in `.relay/registry.json`.

## 10. What this authority does not permit

This authority does not:

- open Slice 2.5;
- authorize Slice 2.5 design;
- authorize Slice 2.5 implementation;
- reopen Slices 2.2, 2.3, or 2.4;
- modify production code;
- modify tests;
- add database schema or migrations;
- add a graph database;
- add new WorkPacket fields;
- add runtime execution behavior;
- modify AgentRuntime;
- open Phase 3;
- authorize real-project agent execution.

Any such work requires separate authority.

## 11. Current Slice 2.4 isolation

The active Slice 2.4 corrective and I003-R2 clarification work remain separate.

The strategic amendment must not alter the exact Slice 2.4 production candidate `73a1525282e41464d31cd458b8a50703bfa9553c` or use the proposed Slice 2.5 capability as a reason to expand current Slice 2.4 implementation scope.

**AUTHORIZED FOR DOCUMENTATION / ARCHITECTURE / ROADMAP / BACKLOG ONLY.**
