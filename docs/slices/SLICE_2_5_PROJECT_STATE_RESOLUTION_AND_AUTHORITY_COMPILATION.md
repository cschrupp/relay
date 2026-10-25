# Slice 2.5 — Project State Resolution and Authority Compilation

**Status:** OPEN / IMPLEMENTATION HUMAN ACCEPTED / CLOSURE-READY
**Phase:** 2 — Provider and Agent Foundation  
**Strategic authority:** `RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED`
**Opening authority:** `RLY-S25-OPEN-001 — OPEN`
**Design authority:** `RLY-S25-DESIGN-AUTH-001 — AUTHORIZED`
**Independent design evaluation:** `RLY-S25-DESIGN-EVAL-002 — ACCEPT`
**Human design acceptance:** `RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED`  
**Predecessor:** Slice 2.4 — Execution Workspace Authority  
**Phase-3 relationship:** mandatory prerequisite for Phase 3 opening; Slice 2.5 must close first

## Current implementation and closure status

Accepted implementation: `88dcb97110665a60b21b5d36f82f0d82b015b098`
Independent implementation evaluation: `RLY-S25-IMPL-EVAL-003 — ACCEPT`
Human technical acceptance: `RLY-S25-ACCEPT-001 — ACCEPTED`
Closure authority: `RLY-S25-CLOSE-AUTH-001 — AUTHORIZED`
Independent closure evaluation: PENDING

Slice 2.5 remains OPEN / CLOSURE-READY until independent closure evaluation accepts the exact closure-ready candidate. Production ProjectStateResolver/AuthorityCompiler wiring, production WorkPacket compilation, operational persistence/lifecycle mutation, and Phase 3 remain unauthorized.

## Objective

Make accepted project knowledge operationally durable by resolving current canonical Relay state into machine-enforceable prerequisites, inherited constraints, prohibitions, qualification applicability, evidence lineage, and a complete authority candidate before executable work is authorized.

## Product problem

Relay can preserve evidence and authority records while still requiring a Human/SOL/agent to reconstruct the complete predecessor chain manually.

This permits failures such as:

- omitted smoke prerequisites;
- lost environment qualification;
- stale evidence reuse;
- superseded-decision resurrection;
- duplicate architectural infrastructure;
- evidence/authority confusion;
- locally valid but globally incomplete WorkPackets.

Slice 2.5 eliminates dependence on agent memory for these obligations.

## Governing invariants

```text
Relay remains the only governance state machine.
Human Authority remains the source of authorization.
WorkPacket remains the external governed work unit.
Project-state graph is derived, not independently authoritative.
Authority compilation does not grant authority.
Historical evidence remains immutable.
Applicability is derived from exact subject state.
Runtime-local planning remains non-authoritative.
```

## Required design decisions

The future Slice 2.5 design must resolve:

### A. Invariant / Constraint model

How durable accepted rules are identified, scoped, rationalized, and applied to later work.

### B. Qualification Fact model

How environment/runtime/operational qualification is represented without confusing evidence with authority.

### C. Applicability envelope

How evidence is bound to exact executable/runtime/provider/environment/endpoint/fixture identities and how later changes invalidate applicability without rewriting history.

### D. Requirement graph

How governed outcomes encode:

```text
REQUIRES
FORBIDS
CONSUMES
PRODUCES
```

while avoiding a second generic workflow engine.

### E. Negative decision disposition

Exact semantics for at least:

```text
SUPERSEDED
REJECTED
PROHIBITED_UNLESS_REAUTHORIZED
```

### F. Responsibility ownership

How existing components claim architectural responsibilities and how proposed duplication triggers a responsibility collision requiring architecture authority.

### G. Project State Resolver

Inputs, exact-subject semantics, deterministic resolution, failure modes, and present-tense state outputs.

### H. Authority Compiler

How requested outcomes become:

```text
READY
BLOCKED
INDETERMINATE
```

plus a complete authority candidate.

### I. WorkPacket integration

How the compiler gates or supplies WorkPacket construction through existing Slice 2.3 interfaces without duplicating WorkPacket authority.

### J. Knowledge Delta

How execution/evaluation discoveries become proposed durable knowledge and require accepted promotion before constraining future work.

### K. Persistence and projection

What is stored as immutable source records versus derived projection, and how to prevent state divergence.

### L. UI / operator visibility

How Human users see:

- requested outcome;
- resolved prerequisites;
- blockers;
- inherited constraints;
- prohibited approaches;
- evidence applicability;
- why authority is READY/BLOCKED/INDETERMINATE.

## Minimum acceptance scenarios for future design

The design must cover at least these cases:

1. smoke PASS required before live scientific authority;
2. smoke PASS exists but executable identity changed -> not applicable;
3. environment qualification missing -> downstream authority blocked;
4. historical runtime observation exists but current runtime identity is unestablished -> not authorized;
5. second smoke harness proposed while canonical campaign runner owns the responsibility -> collision / architecture review;
6. rejected second semantic engine cannot silently reappear;
7. evidence fact is SATISFIED but does not itself grant authority;
8. accepted predecessor changes -> dependent applicability/facts invalidate deterministically;
9. unresolved required fact -> INDETERMINATE rather than optimistic ALLOW;
10. no authorized successor -> existing BACKLOG_EXHAUSTED semantics remain valid;
11. Knowledge Delta proposed by evaluator does not become canonical until accepted;
12. state graph can be reconstructed from canonical Relay records.

## Proposed architectural concepts

These names are design targets, not frozen production class names:

```text
ProjectStateResolver
AuthorityCompiler
Invariant
QualificationFact
ApplicabilityEvaluation
RequirementEdge
ResponsibilityClaim
ResponsibilityCollision
KnowledgeDelta
```

Future design may rename or consolidate them if the accepted semantics remain intact.

## Relationship to existing slices

### Slice 1.10

Provides canonical-source/promotion discipline. Slice 2.5 consumes canonical accepted state; it does not replace promotion.

### Slice 2.1

Provides AgentRuntime. Slice 2.5 does not own runtime-local reasoning or tool loops.

### Slice 2.2

Provides RoleContract authority/applicability. Slice 2.5 consumes it; it does not create new role authority.

### Slice 2.3

Provides exact ContextManifest/WorkPacket contracts. Slice 2.5 determines what prerequisites and constraints must gate or populate a future WorkPacket; it does not create a parallel work unit.

### Slice 2.4

Provides workspace authority/enforcement. Slice 2.5 may require workspace qualification facts as prerequisites but does not replace the workspace provider/evaluator.

## Proposed implementation staging

No staging is authorized yet. Future design should consider a bounded progression such as:

```text
Stage A — exact domain semantics / derived resolution
Stage B — deterministic resolver and prerequisite evaluation
Stage C — authority-candidate compilation
Stage D — responsibility collision and negative-decision enforcement
Stage E — Knowledge Delta promotion path
Stage F — operator projection / dogfood
```

This is planning guidance only.

## Dogfood targets

Future acceptance should use real scenarios from:

- Relay;
- Wellplot;
- Tension/FEM;
- Seneca.

The exact fixtures and external-project evidence must be separately authorized and sanitized as appropriate.

## Out of scope until separately authorized

- production implementation;
- schema migration;
- graph database;
- new runtime behavior;
- direct OpenCode integration changes;
- changes to current Slice 2.4 implementation;
- automatic Human authority;
- generic planner/task state machine;
- Phase 3 opening;
- real-project autonomous execution.

## Opening condition — satisfied

Opening conditions are satisfied under:

`RLY-S25-OPEN-001 — OPEN`

Exact opening baseline:

`fbe41dfcb72df2dd3d145818c6b22478416de789`

Slice 2.4 is COMPLETE / ACCEPTED / CLOSED under `RLY-S24-CLOSE-EVAL-001 — ACCEPT`.

Slice 2.5 design is authorized under `RLY-S25-DESIGN-AUTH-001 — AUTHORIZED`. The normative design is independently and Human accepted at exact subject `b2f566d3f8ed616e3e901795858b7046aa3fa6c6`. The implementation is independently accepted and Human-accepted at exact candidate `88dcb97110665a60b21b5d36f82f0d82b015b098`; closure evaluation is pending.

## Completion implication

If Slice 2.5 is eventually COMPLETE / ACCEPTED / CLOSED, Relay may become eligible for a separately authorized Phase 3 opening, subject to all other Phase-3 prerequisites.

Completion does not itself open Phase 3.
