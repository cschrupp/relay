# Relay — Slice 2.5 Project State Resolution and Authority Compilation — Human Design Acceptance

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Record:** `RLY-S25-DESIGN-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

The Human explicitly accepts the independently accepted Slice 2.5 normative design.

## Accepted design lineage

```text
Slice opening:
RLY-S25-OPEN-001 — OPEN

Design authorization:
RLY-S25-DESIGN-AUTH-001 — AUTHORIZED

Design candidate revision 1:
1e64b6b9b7c9e2e9e30e788607e9591f1eea456e

Independent evaluation 001:
RLY-S25-DESIGN-EVAL-001 — REWORK

Corrective design candidate revision 2:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Independent evaluation 002:
RLY-S25-DESIGN-EVAL-002 — ACCEPT
```

Revision 2 is the exact Human-accepted normative design subject.

## Accepted architecture

The Human accepts the Slice 2.5 design including:

- deterministic Project State Resolver semantics;
- deterministic Authority Compiler semantics;
- explicit `READY / BLOCKED / INDETERMINATE` results;
- the structural rule `READY != AUTHORIZED`;
- exact canonical-source and provenance resolution;
- canonical-pointer selection distinct from claim authority;
- authority-bearing predicates requiring exact backing accepted/immutable/locked records or explicitly authorized external facts;
- immutable historical evidence separated from present applicability;
- exact applicability envelopes and `APPLICABLE / NOT_APPLICABLE / INDETERMINATE` semantics;
- invariant / inherited-constraint representation with rationale and protects-against context;
- QualificationFact as evidence, not authority;
- typed `REQUIRES / FORBIDS / CONSUMES / PRODUCES` relations;
- exact negative-decision semantics for `SUPERSEDED / REJECTED / PROHIBITED_UNLESS_REAUTHORIZED`;
- responsibility ownership and collision detection;
- exact consumption semantics preventing silent one-shot reuse;
- existing Slice 2.3 WorkPacket primacy;
- Knowledge Delta remaining non-authoritative until separately accepted/promoted;
- reconstructible derived state with no second authoritative project-state database;
- bounded Human/operator projection;
- deterministic failure-closed reconstruction without chat-history dependency;
- the Wellplot, Tension/FEM, Seneca, and Relay acceptance scenarios.

## Accepted ownership boundaries

The Human accepts that Slice 2.5 does not replace or absorb:

- Human Authority;
- Slice 1.10 canonical source/promotion discipline;
- Slice 2.1 AgentRuntime/runtime execution;
- Slice 2.2 RoleContract semantics;
- Slice 2.3 WorkPacket/ContextManifest ownership;
- Slice 2.4 WorkspacePolicy/WorkspacePlan enforcement;
- Phase 3 real-execution orchestration.

The resolver is not a planner.

The compiler is not a planner or authority issuer.

The derived requirement graph is not a generic workflow engine.

The project-state projection is not a second source of truth.

## Binding provenance clarification

The Human explicitly accepts the Revision-2 clarification:

```text
canonical pointer
    -> selects the current registered projection
    != authority for every claim inside it

summary/planning projection
    -> may navigate, select, and describe
    -> cannot by itself establish authority-bearing predicates

authority-bearing predicate
    -> exact owning accepted / immutable / locked record
       OR explicitly authorized external fact
          whose accepted contract permits that predicate

missing backing provenance
    -> INDETERMINATE

summary contradicts backing record
    -> INDETERMINATE
       contradiction retained in provenance trace
```

Living canonical policy is normative only within the exact ownership, scope, and authority granted by its accepted policy contract.

## Authority boundary

This record accepts the Slice 2.5 design only.

It does **not** authorize implementation.

It does not authorize:

- production ProjectStateResolver implementation or execution;
- production AuthorityCompiler implementation or execution;
- source/test mutation for Slice 2.5 implementation;
- database schema/migration;
- graph database introduction;
- independently mutable project-state storage;
- automatic authority issuance;
- production WorkPacket creation or execution;
- production workspace provisioning;
- AgentRuntime/OpenCode changes;
- provider/model/runtime calls;
- credential use;
- Phase 3 opening;
- real-project autonomous execution;
- canonical/main promotion.

Any Slice 2.5 implementation requires separate Human implementation authority.

## Disposition

```text
RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED

Slice 2.5:
OPEN

Normative design:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Exact accepted design:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Implementation:
ELIGIBLE FOR SEPARATE EXPLICIT AUTHORIZATION
NOT YET AUTHORIZED

Production ProjectStateResolver:
NOT AUTHORIZED

Production AuthorityCompiler:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

**Design accepted != implementation authorized. READY != authorized.**
