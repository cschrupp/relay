# Relay — Phase 3 Opening Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Record:** `RLY-P3-OPEN-001`  
**Decision:** `AUTHORIZED`

## 1. Human authority

The Human explicitly authorizes:

> Phase 3 opening.

This record opens Phase 3 at the phase level.

It does not itself open Slice 3.1, authorize Phase 3 implementation, authorize real-project agent execution, or authorize production runtime/persistence/wiring.

## 2. Exact basis

```text
Canonical main before Phase 3 opening:
e0cdfbf5066b81d2e9dbb6811ea48acf92383f79

Slice 2.5:
COMPLETE / ACCEPTED / CLOSED

Accepted Slice 2.5 implementation:
88dcb97110665a60b21b5d36f82f0d82b015b098

Slice 2.5 independent implementation acceptance:
RLY-S25-IMPL-EVAL-003 — ACCEPT

Slice 2.5 Human technical acceptance:
RLY-S25-ACCEPT-001 — ACCEPTED

Slice 2.5 independent closure acceptance:
RLY-S25-CLOSE-EVAL-001 — ACCEPT

Slice 2.5 canonical closed-state commit:
e0cdfbf5066b81d2e9dbb6811ea48acf92383f79
```

The Human phase-opening decision satisfies the previously pending explicit Phase 3 opening gate.

## 3. Phase 3 state

Effective under this record:

```text
Phase 3:
OPEN

Slice 3.1 — Coding Agent Execution / First Governed Autonomous Engineering Loop:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Production ProjectStateResolver / AuthorityCompiler wiring:
NOT AUTHORIZED

Production WorkPacket compilation / wiring:
NOT AUTHORIZED

Operational persistence / lifecycle mutation:
NOT AUTHORIZED

AgentRuntime / provider / model execution for Phase 3 work:
NOT AUTHORIZED BY THIS RECORD
```

The governing distinction remains:

```text
Phase open
    != Slice open
    != design authorized
    != implementation authorized
    != runtime/execution authorized
```

## 4. Remaining prerequisite — Slice 1.10

Canonical project state still records:

```text
Slice 1.10 — Canonical Source and Promotion Enforcement:
OPEN / DESIGN HUMAN ACCEPTED / IMPLEMENTATION AUTHORIZED
B4 COMPLETE / HUMAN ACCEPTED
top-level Slice 1.10 closure:
NOT ESTABLISHED
```

The accepted Phase 3 roadmap names Slice 1.10 among the prerequisite chain for Slice 3.1 / governed autonomous execution.

This Phase 3 opening decision does **not** silently waive or fabricate completion of Slice 1.10.

Therefore:

```text
Phase 3:
OPEN

Phase 3 execution frontier:
GATED

Slice 3.1 opening / implementation / execution:
BLOCKED pending satisfaction or separate explicit Human disposition
of the remaining Slice 1.10 prerequisite.
```

If the Human later chooses to waive, replace, or otherwise re-authorize that prerequisite, that requires a separate explicit authority record.

## 5. Phase 3 product direction

Phase 3 is the product phase in which Relay operationalizes governed autonomous engineering through the already accepted architecture:

```text
Human Authority
    ↓
Project State Resolver / Authority Compiler
    ↓
WorkPacket
    ↓
RoleContract
    ↓
Execution Workspace
    ↓
AgentRuntime
    ↓
agent-owned internal plan / milestones / retries
    ↓
terminal candidate
    ↓
Independent Evaluator
    ↓
Human acceptance / promotion where required
```

Relay remains the only governance state machine.

Runtime-local plans, subagents, checklists, retries, and milestones remain non-authoritative execution mechanics.

The WorkPacket remains the authoritative external work unit.

## 6. Authorized-work granularity direction preserved

Phase 3 must operationalize the already accepted authorized-work decomposition policy:

`RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`

including:

- one cohesive authorized WorkPacket may contain many internal execution steps;
- routine internal milestones do not become Human approval gates;
- implementers may plan, execute, validate, repair, and self-review within exact authority;
- out-of-scope required work becomes non-authoritative `PROPOSED_WORK` and stops for separate Relay authority;
- no authorized successor means successful `BACKLOG_EXHAUSTED` and STOP;
- independent evaluation remains `ACCEPT / REWORK / ESCALATE`;
- internal decomposition must not create a second authoritative planner/task state machine.

This phase opening authorizes the phase boundary, not implementation of these commitments.

## 7. Existing accepted-contract rule

Slices 2.2, 2.3, 2.4, and 2.5 remain accepted contracts and should be treated as sufficient by default.

Phase 3 work must not reopen them merely for convenience.

If a concrete Phase 3 design cannot satisfy an accepted requirement through those interfaces, it must produce an evidenced contract-gap record before any reopening is proposed.

## 8. Documentation authority

This record authorizes a bounded documentation-only current-state transition to represent:

```text
Phase 3:
OPEN

Slice 3.1:
NOT OPEN / NOT AUTHORIZED

Phase 3 execution frontier:
GATED by remaining prerequisite(s), including top-level Slice 1.10 closure

Real-project execution:
NOT AUTHORIZED
```

The documentation transition may update only the current living roadmap/baseline/checklist/product projections and registry entries required to represent this Human decision.

No source, test, dependency, CI, schema, database, runtime, provider, model, WorkPacket, resolver/compiler production wiring, or execution behavior is authorized by this documentation authority.

## 9. Explicit non-authority

This record does **not** authorize:

- opening Slice 3.1;
- Slice 3.1 design;
- Slice 3.1 implementation;
- production ProjectStateResolver / AuthorityCompiler integration;
- production WorkPacket compilation/wiring;
- production execution-workspace provisioning;
- AgentRuntime execution;
- provider/model execution;
- real-project autonomous engineering;
- operational persistence/lifecycle mutation;
- changes to accepted Slice 2.2–2.5 contracts;
- waiver of Slice 1.10 as an accepted prerequisite;
- autonomous acceptance;
- canonical promotion of future Phase 3 implementation.

Those require separately bounded authority.

## 10. Disposition

```text
RLY-P3-OPEN-001 — AUTHORIZED

Phase 3:
OPEN

Slice 3.1:
NOT OPEN / NOT AUTHORIZED

Phase 3 execution:
GATED

Slice 1.10 prerequisite:
UNSATISFIED / NOT WAIVED

Production resolver/compiler wiring:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Phase open != executable work authority.**
