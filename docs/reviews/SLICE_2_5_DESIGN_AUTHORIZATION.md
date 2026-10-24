# Relay — Slice 2.5 Project State Resolution and Authority Compilation — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Authority:** `RLY-S25-DESIGN-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes bounded detailed design of Slice 2.5 from the exact opened-state baseline below.

This is one cohesive design authority.

It permits design only.

It does **not** authorize implementation, database/schema mutation, production state resolution, production authority compilation, WorkPacket creation/execution, workspace/runtime/provider/model execution, Phase 3, real-project autonomous execution, or canonical promotion.

## Exact design basis

```text
Repository:
cschrupp/relay

Canonical opening baseline:
fbe41dfcb72df2dd3d145818c6b22478416de789

Slice 2.5 opening:
RLY-S25-OPEN-001 — OPEN

Opening record commit:
073604b32a9a731e154fe4bc2e02c68d2e496e69

Opened-state governance tip:
f73639ca14f6c6e2e288078d994f5c9ebecb435a

Design branch:
design/2.5-project-state-resolution-authority-compilation

Strategic authority:
RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED

Opened planning source:
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md

Opened planning-source blob:
458d5b5de725c8c84d11533522b75ab163bd0278

Strategic architecture:
docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md

Opened architecture blob:
1dfbb346fc0b49f50e66e8ddad94ac7a1678877b

Slice 2.4:
COMPLETE / ACCEPTED / CLOSED

Accepted Slice 2.4 implementation:
73a1525282e41464d31cd458b8a50703bfa9553c

Slice 2.4 closure:
RLY-S24-CLOSE-EVAL-001 — ACCEPT

Accepted Slice 2.3 Work-Packet implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7

Accepted Slice 2.2 Role Contracts implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Accepted Slice 2.1 Agent Runtime implementation:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

## Authorized design objective

Design the minimum deterministic Relay contract that transforms accepted canonical project knowledge into present-tense, machine-resolvable prerequisites and inherited constraints before downstream authority is issued.

The design must define a bounded path from:

```text
requested outcome
      ↓
deterministic project-state resolution
      ↓
applicability / predecessor / prohibition / responsibility evaluation
      ↓
READY / BLOCKED / INDETERMINATE
      ↓
complete authority candidate
      ↓
Human Authority
      ↓
existing WorkPacket path
```

The design must eliminate dependence on Human/SOL/worker memory for reconstructing settled project obligations while preserving all existing Relay authority boundaries.

## Mandatory architectural invariants

The design must preserve:

```text
Relay remains the only governance state machine.

Human Authority remains the source of authorization.

Project-state graph/projection != independent authoritative truth.

Authority Compiler != authority issuer.

Authority candidate != authority.

READY != AUTHORIZED.

Evidence != authority.

Qualification PASS != authority.

Historical evidence remains immutable.

Current applicability is derived; it does not rewrite historical evidence.

WorkPacket remains the authoritative external work unit.

ContextManifest remains Slice 2.3-owned context transport.

RoleContract remains Slice 2.2-owned actor/action contract.

Execution Workspace remains Slice 2.4-owned workspace enforcement substrate.

AgentRuntime remains Slice 2.1-owned runtime/tool execution abstraction.

Project State Resolver != planner.

Authority Compiler != planner.

Requirement graph != generic workflow/task engine.

Runtime-local task graph != Relay authority.

Knowledge Delta proposal != accepted durable knowledge.

Responsibility collision != authority to create a new component.

SUPERSEDED / REJECTED / PROHIBITED_UNLESS_REAUTHORIZED
    != ordinary implementation choice.

No authorized successor -> existing BACKLOG_EXHAUSTED semantics remain valid.

Slice 2.5 COMPLETE != Phase 3 OPEN.
```

## Mandatory ownership boundaries

### Human Authority remains owner of

- opening/closing Slice authority;
- design/implementation authority;
- technical acceptance where required;
- reauthorization of prohibited/superseded approaches;
- final authority grant after an authority candidate is compiled.

Slice 2.5 may produce a deterministic authority candidate and blocker explanation but may not self-authorize.

### Slice 1.10 remains owner of

- canonical-source / promotion discipline;
- accepted-source identity and promotion gates.

Slice 2.5 consumes canonical accepted state and must not create a competing promotion mechanism.

### Slice 2.1 remains owner of

- AgentRuntime;
- runtime/provider/model provenance;
- runtime permission/profile transport;
- runtime sessions/events/results/cancellation;
- actual runtime execution.

Slice 2.5 may reason over accepted runtime qualification/evidence but must not invoke or redefine AgentRuntime.

### Slice 2.2 remains owner of

- RoleContract / RoleContractRef;
- actor/action eligibility;
- successor / exhaustion semantics;
- role separation.

Slice 2.5 may resolve whether an exact RoleContract fact is applicable but must not manufacture role authority.

### Slice 2.3 remains owner of

- WorkPacket / WorkPacketRef;
- ContextManifest;
- exact source-baseline/context transport;
- normalized engineering intent;
- packet conformance.

Slice 2.5 must gate/supply the existing WorkPacket construction path and must not create a parallel governed work unit.

### Slice 2.4 remains owner of

- WorkspacePolicy / WorkspacePlan;
- provider/workspace capability;
- workspace conformance;
- filesystem/protected/network/credential/resource enforcement semantics;
- RuntimeWorkspaceAttachment derivation.

Slice 2.5 may require exact workspace qualification facts but must not reopen or duplicate workspace enforcement.

### Phase 3 remains owner of

- selecting a currently authorized WorkPacket for real execution;
- combining current authority + role + packet + workspace + runtime predicates;
- invoking AgentRuntime;
- engineering-result orchestration;
- real-project autonomous engineering.

Slice 2.5 must not absorb Phase-3 orchestration.

## Required design coverage

The design must explicitly specify at least the following.

### 1. Canonical source model

Define exactly which accepted Relay records may contribute to project-state resolution.

The design must identify:

- canonical accepted records;
- immutable historical evidence;
- living projections;
- exact references/digests;
- authoritative versus descriptive inputs;
- reconstruction rules;
- source conflicts and missing sources.

The derived state must be reproducible from canonical Relay records plus explicitly authorized external facts.

### 2. Invariant / inherited-constraint model

Define a durable accepted invariant/constraint representation with at least:

- stable identity;
- normative statement;
- applicability scope;
- source authority/decision;
- rationale;
- protects-against rationale;
- status/disposition;
- exact subject bindings where required.

Rationale is part of the durable rule context so future agents cannot silently optimize away a settled rule.

### 3. Qualification Fact model

Define exact qualification evidence for environment/runtime/operational prerequisites, including at least:

- qualification identity;
- result;
- exact subject/applicability envelope;
- provenance;
- evidence reference;
- acceptance reference where qualification requires independent/Human acceptance;
- validity/applicability semantics.

Qualification facts are evidence, not authority.

### 4. Applicability evaluation and invalidation

Define deterministic applicability semantics.

Historical evidence must remain immutable while current applicability may become:

```text
APPLICABLE
NOT_APPLICABLE
INDETERMINATE
```

or an equivalently precise accepted vocabulary.

The design must specify exact mismatch/invalidation behavior for relevant identities such as:

- executable/content identity;
- runtime build;
- provider contract/version;
- endpoint;
- environment;
- workspace/provider identity;
- model identity where relevant;
- fixture/data/custody identity;
- accepted predecessor revision.

A previously PASS fact whose applicability envelope no longer matches must not be treated as current PASS authority.

### 5. Requirement edges

Define machine-readable relation semantics for at least:

```text
REQUIRES
FORBIDS
CONSUMES
PRODUCES
```

The design must distinguish:

- dependency/prerequisite;
- prohibition;
- one-shot/consumable authority/resource/namespace state;
- produced evidence/result.

The relation model must remain bounded and must not become a second generic workflow engine.

### 6. Negative-decision dispositions

Define exact semantics for at least:

```text
SUPERSEDED
REJECTED
PROHIBITED_UNLESS_REAUTHORIZED
```

The design must specify:

- whether the disposition applies to an idea, component, path, design, or exact subject;
- provenance/rationale;
- applicability;
- reauthorization requirements;
- how ordinary implementation is prevented from silently resurrecting the approach.

### 7. Responsibility claims and collision detection

Define a bounded representation of architecture responsibility ownership.

The design must specify how a proposed new component/action can be checked against accepted existing owners.

A high-confidence responsibility collision must not silently authorize duplication.

The design must define deterministic outcomes such as:

```text
NO_COLLISION
COLLISION_REQUIRES_ARCHITECTURE_AUTHORITY
INDETERMINATE
```

or equivalent accepted semantics.

### 8. Project State Resolver

Define exact:

- inputs;
- source-resolution order;
- exact-subject matching;
- derivation rules;
- conflict handling;
- missing/unsupported handling;
- present-state output;
- provenance/evidence trace;
- deterministic failure modes.

The resolver must fail closed.

It must not silently infer accepted authority, prerequisites, or prohibitions from ambiguous prose.

### 9. Authority Compiler

Define how a requested outcome becomes:

```text
READY
BLOCKED
INDETERMINATE
```

plus a complete authority candidate.

The design must freeze the rule:

```text
READY
    != AUTHORIZED
```

A compiled candidate must expose all applicable inherited constraints, exact predecessors, blockers, prohibitions, consumables, evidence lineage, and hard stops required for Human review and later WorkPacket creation.

### 10. WorkPacket integration

Define the smallest integration with Slice 2.3.

The compiler/resolver may gate or supply WorkPacket construction, but:

- it must not create a second WorkPacket format;
- it must not create a competing authoritative task identity;
- it must not bypass WorkPacket exact identity/revision/digest rules;
- changed compiled normative content must yield changed exact governed content/identity as required by the accepted 2.3 contract.

### 11. Knowledge Delta

Define how workers/evaluators may propose new knowledge such as:

- discovered invariant;
- new prerequisite;
- invalidation rule;
- responsibility ownership;
- rejected/superseded approach;
- qualification requirement.

A Knowledge Delta is non-authoritative until separately accepted/promoted through Relay governance.

The design must prevent runtime/worker self-promotion of new durable constraints.

### 12. Persistence and derived projection

Define what is:

```text
immutable source record
living canonical projection
derived/reconstructible state
ephemeral evaluation result
```

The design must prevent an independently mutable project-state graph from becoming a second source of truth.

If persistence is proposed for performance, it must be a rebuildable cache/projection whose invalidation/reconstruction semantics are exact.

No graph database is required or authorized by this design authority.

### 13. Consumption semantics

Define how `CONSUMES` interacts with:

- one-shot authority;
- campaign namespace;
- scientific-run budget;
- externally accepted attempt identity;
- already-consumed facts.

Consumption state must be exact and evidence-bearing.

A consumed resource/authority must not silently become reusable.

### 14. Operator/Human projection

Define a bounded review surface that can show:

- requested outcome;
- READY/BLOCKED/INDETERMINATE;
- required predecessors;
- missing/stale/inapplicable qualification;
- inherited invariants;
- prohibited approaches;
- responsibility collisions;
- consumables;
- evidence lineage;
- reason for each blocker;
- exact authority candidate identity/content.

The UI/projection is descriptive and must not grant authority.

### 15. Deterministic reconstruction

Define how current derived state can be reconstructed from canonical Relay records without chat history.

The design must specify reproducibility and conflict behavior.

### 16. Failure modes

At minimum, the design must fail closed for:

- missing required canonical source;
- conflicting accepted facts;
- unknown exact subject;
- stale/not-applicable qualification;
- unresolved predecessor;
- prohibited approach without reauthorization;
- responsibility collision requiring authority;
- consumed one-shot resource;
- unknown requirement relation;
- unsupported applicability rule;
- incomplete evidence lineage.

No unresolved required fact may become optimistic READY.

## Mandatory dogfood / acceptance scenarios

The design must be independently reviewable against at least the following real failure patterns.

### Wellplot live campaign

```text
D5-5J accepted
-> environment qualification
-> live smoke
-> smoke independently accepted
-> live confirmation
```

Required outcomes:

1. missing environment qualification blocks live authority candidate;
2. missing accepted live smoke blocks live authority candidate;
3. smoke PASS for a different executable/runtime/provider/environment is historical PASS but current NOT_APPLICABLE;
4. stale runtime identity cannot be converted into current authorization;
5. new second smoke harness colliding with canonical campaign ownership requires architecture authority;
6. a rejected second semantic engine / fallback execution path cannot silently reappear.

### Tension/FEM

The design must represent:

- scientific-level/attempt consumption;
- one-shot authority/resource state;
- exact oracle/evidence applicability to frozen subject identities;
- no reuse after consumption unless separately reauthorized.

### Seneca

The design must represent invalidation of environment/backend qualification when relevant GPU/backend/runtime/environment identity changes.

### Relay self-dogfood

The design must demonstrate deterministic resolution of:

- accepted predecessor;
- accepted design/implementation;
- closure/promotion;
- exact current baseline;
- inherited constraints;
- no-authorized-successor / BACKLOG_EXHAUSTED behavior;

without reconstructing those facts from chat history.

## Required design economy

Do not design:

- a second workflow engine;
- a second task database;
- a second authoritative project-state database;
- a generic graph platform;
- a generic rule engine;
- a generic planner;
- a generic orchestration scheduler;
- a new WorkPacket format;
- a new RoleContract format;
- a new workspace abstraction;
- a new AgentRuntime;
- a generic event-sourcing platform;
- an ontology product;
- a generic policy language.

Prefer the minimum exact domain model needed for the accepted failure cases.

## Explicitly out of scope

This design authority does not permit:

- production source/test implementation;
- database migration;
- operational DB mutation;
- graph database introduction;
- production ProjectStateResolver execution;
- production AuthorityCompiler execution;
- automatic authority issuance;
- production WorkPacket creation/wiring;
- production workspace provisioning;
- AgentRuntime/OpenCode integration changes;
- provider/model/runtime calls;
- credential use;
- network/live scientific execution;
- real-project autonomous work;
- reopening Slices 2.2, 2.3, or 2.4;
- Phase 3 opening;
- canonical/main promotion.

## Required acceptance criteria

The design must be independently reviewable against at least:

```text
A01 canonical source set and exact provenance are deterministic
A02 derived state is reconstructible and is not independent authority
A03 invariant/constraint identity, scope, provenance, rationale, and applicability are exact
A04 QualificationFact is evidence only and binds an exact applicability envelope
A05 historical evidence is immutable while current applicability can become NOT_APPLICABLE
A06 required exact applicability unknown -> INDETERMINATE, never optimistic READY
A07 REQUIRES semantics block missing/unaccepted predecessors
A08 FORBIDS semantics prevent ordinary resurrection of prohibited approaches
A09 CONSUMES semantics prevent silent reuse of one-shot authority/resources/namespaces
A10 PRODUCES semantics bind produced results/evidence without manufacturing authority
A11 SUPERSEDED / REJECTED / PROHIBITED_UNLESS_REAUTHORIZED semantics are exact
A12 responsibility ownership/collision is deterministic and does not self-authorize duplication
A13 ProjectStateResolver is deterministic, provenance-bearing, provider-neutral, and fail-closed
A14 AuthorityCompiler emits READY/BLOCKED/INDETERMINATE plus complete candidate and never grants authority
A15 READY != AUTHORIZED is structurally preserved
A16 existing WorkPacket remains the authoritative external work unit
A17 Slice 2.2/2.3/2.4/2.1 ownership boundaries are preserved
A18 KnowledgeDelta remains non-authoritative until separately accepted/promoted
A19 derived persistence/cache, if any, is reconstructible and not independent truth
A20 operator projection exposes blockers/inherited constraints/evidence lineage without granting authority
A21 Wellplot smoke/environment/applicability failure sequence is representable and deterministic
A22 responsibility collision catches the second-smoke-harness failure pattern
A23 rejected/superseded engine/fallback patterns cannot silently reappear
A24 Tension/FEM consumption and exact oracle applicability are representable
A25 Seneca backend/environment qualification invalidation is deterministic
A26 Relay state can be reconstructed without chat-history dependency
A27 BACKLOG_EXHAUSTED and PROPOSED_WORK semantics remain intact
A28 no DB/runtime/workspace/Phase3/real-project-execution scope leakage
```

## Deliverable

Produce one detailed normative design candidate under:

`docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_DESIGN.md`

The candidate must identify itself as:

`DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED`

It may revise or supersede planning details from the opened proposal where required, but it must explicitly identify any such differences.

After the design candidate is complete:

`STOP FOR SOL INDEPENDENT DESIGN REVIEW`

## Authority boundary

```text
RLY-S25-DESIGN-AUTH-001 — AUTHORIZED

Slice 2.5:
OPEN

Design:
AUTHORIZED

Design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Production authority compilation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

**Design authority != design acceptance. Design acceptance != implementation authority. READY != authorized.**
