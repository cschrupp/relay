# Project State Resolution and Authority Compilation

**Status:** Human-directed strategic architecture — Slice 2.5 OPEN; normative design HUMAN ACCEPTED; bounded implementation AUTHORIZED  
**Authority:** `RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED`
**Design authority:** `RLY-S25-DESIGN-AUTH-001 — AUTHORIZED`
**Independent design evaluation:** `RLY-S25-DESIGN-EVAL-002 — ACCEPT`
**Human design acceptance:** `RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED`
**Implementation scope:** `RLY-S25-CODEX-SCOPE-001`
**Implementation authority:** `RLY-S25-IMPL-AUTH-001 — AUTHORIZED`  
**Date:** 2026-10-24  
**Target slice:** Slice 2.5 — Project State Resolution and Authority Compilation — OPEN under `RLY-S25-OPEN-001`

## 1. Problem statement

Relay already preserves substantial engineering history: authority records, exact baselines, accepted designs, evidence, evaluations, decisions, context manifests, WorkPackets, workspace requirements, and immutable results.

The recurring failure is not primarily missing historical information.

The failure is:

> **Accepted historical knowledge is not always transformed into machine-resolvable obligations that constrain later authority.**

A later agent can therefore receive a locally plausible task while missing part of the accepted dependency chain.

Examples include:

```text
SMOKE_PASS -> prerequisite of SCIENTIFIC_LIVE_AUTH
```

or:

```text
environment qualification
-> smoke
-> smoke acceptance
-> live campaign
```

If these relationships exist only in prose, a future authority can omit them.

Other manifestations include:

- rules documented but not enforced;
- authority-state drift;
- operational prerequisite loss;
- architecture rediscovery and duplicate infrastructure;
- superseded or rejected decisions resurfacing;
- stale evidence being treated as current;
- evidence being mistaken for authority.

## 2. Core architectural principle

> **Accepted knowledge is not operationally durable until Relay converts it into machine-resolvable state that constrains subsequent authority.**

Corresponding execution principle:

> **Agents must not be responsible for reconstructing project invariants, prerequisites, prohibitions, or evidence applicability from historical context. Relay must resolve and inject the applicable envelope before work begins.**

## 3. No second governance architecture

This capability must not create a parallel task manager, planner state machine, or competing project truth.

The existing architecture remains:

```text
Human Authority
      ↓
Relay governance state
      ↓
WorkPacket
      ↓
RoleContract applicability
      ↓
Execution Workspace
      ↓
AgentRuntime
      ↓
terminal candidate/evidence
      ↓
Independent Evaluator
      ↓
Human acceptance / promotion where required
```

Project State Resolution is inserted before authority issuance:

```text
requested outcome
      ↓
Project State Resolver
      ↓
Authority Compiler
      ↓
READY / BLOCKED / INDETERMINATE
      ↓
complete authority candidate
      ↓
Human Authority
      ↓
WorkPacket
```

The resolver/compiler is a deterministic consumer of Relay state. It is not another authority source.

## 4. Derived project-state graph

Relay should maintain or derive a machine-readable project-state graph.

The graph is a projection over canonical Relay records such as:

- project/slice state;
- accepted baselines;
- authority records;
- accepted decisions;
- evidence and evaluations;
- qualification facts;
- accepted invariants;
- supersession/rejection dispositions;
- architecture responsibility claims;
- WorkPacket and ContextManifest identities;
- environment/runtime/workspace facts.

The graph itself must not become an independent authoritative database whose state can disagree with canonical Relay records.

Preferred rule:

```text
canonical Relay records
        ↓ deterministic resolution
derived project-state graph
```

not:

```text
canonical records <-> independently mutable graph state
```

## 5. First-class concept: Invariant / Constraint

An invariant is a durable accepted rule that subsequent work may inherit.

Examples:

```text
LIVE_SMOKE_REQUIRED
ONE_CANONICAL_ENGINE
NO_REPLAY
NO_MODEL_SUBSTITUTION
NO_SECOND_SMOKE_HARNESS
```

A future exact schema should preserve at least:

- stable identity;
- concise statement;
- scope/applicability;
- status;
- provenance / source decision;
- rationale;
- what failure it protects against;
- required predecessor/successor relationship where applicable.

The rationale is normative context, not decoration. It prevents future agents from "optimizing away" a rule whose necessity was already established experimentally.

## 6. First-class concept: Qualification Fact

A Qualification Fact records that an operational or technical prerequisite was established for an exact applicability envelope.

Examples:

- environment LAN reachability;
- sandbox capability;
- credential availability;
- model/runtime identity;
- GPU/model-server readiness;
- writable artifact/custody path;
- smoke PASS;
- fresh namespace readiness.

A qualification is evidence, not authority.

Conceptually:

```text
qualification:
    LIVE_SMOKE_PASS

result:
    PASS

subject/applicability:
    executable = E
    runtime = R
    provider_contract = P
    endpoint = EP
    environment = ENV
```

## 7. Applicability and invalidation

Historical evidence must remain immutable.

Changing current conditions changes applicability, not historical truth.

Example:

```text
SMOKE-001
result = PASS
endpoint = EP1
```

Later execution:

```text
endpoint = EP2
```

Derived state:

```text
SMOKE-001 historical result = PASS
current applicability = NOT_APPLICABLE
reason = endpoint mismatch
```

Relay must not rewrite `SMOKE-001` as FAIL or STALE.

Applicability should be evaluated from exact subject identities and explicit invalidation rules.

## 8. First-class concept: Requirement Edge

Requirement edges encode the governed dependency graph.

Minimum conceptual relation families:

```text
REQUIRES
FORBIDS
CONSUMES
PRODUCES
```

Example:

```text
SCIENTIFIC_LIVE_AUTH
    REQUIRES D5_5J_ACCEPTED
    REQUIRES RUNTIME_IDENTITY_VALID
    REQUIRES ENVIRONMENT_QUALIFIED
    REQUIRES LIVE_SMOKE_PASS
    REQUIRES LIVE_SMOKE_ACCEPTED
    REQUIRES CUSTODY_READY
    REQUIRES FRESH_CAMPAIGN_NAMESPACE

    FORBIDS REPLAY
    FORBIDS MODEL_SUBSTITUTION
    FORBIDS SECOND_SEMANTIC_ENGINE
    FORBIDS SECOND_SMOKE_HARNESS

    CONSUMES LIVE_CONFIRMATION_AUTHORITY
    CONSUMES CAMPAIGN_NAMESPACE
```

An unresolved required predecessor must prevent downstream authority eligibility.

## 9. Supersession, rejection, and prohibition

A single `SUPERSEDED_DO_NOT_REPEAT` state is too coarse.

Future design should distinguish at least:

```text
SUPERSEDED
    no longer current; may have been replaced for ordinary reasons

REJECTED
    evaluated and rejected

PROHIBITED_UNLESS_REAUTHORIZED
    accepted negative architectural constraint;
    cannot reappear without explicit new authority
```

Examples likely suitable for the last category:

- second semantic engine;
- second smoke harness;
- fallback execution path that bypasses the canonical engine;
- unbounded correction loop.

This preserves the option of deliberate future reconsideration while preventing silent resurrection.

## 10. First-class concept: Responsibility Claim

Relay should know which component owns an architectural responsibility.

Example:

```text
responsibility:
    LIVE_SEMANTIC_CAMPAIGN_EXECUTION

owner:
    D5CampaignRunner

supporting_components:
    canonical live adapter
    custody subsystem
    physical attempt observer
```

When proposed work introduces a new component claiming materially overlapping responsibility:

```text
RESPONSIBILITY_COLLISION
```

must be raised.

Ordinary implementation may extend an existing owner inside accepted boundaries.

Creating a competing owner is an architectural change and requires explicit design justification/authority.

## 11. Project State Resolver

The resolver consumes canonical Relay records plus current exact observations and derives present-tense state.

Conceptually:

```text
D5_5J_ACCEPTED               SATISFIED
QWEN_RUNTIME_IDENTITY        SATISFIED
ENVIRONMENT_QUALIFIED        INDETERMINATE
LIVE_SMOKE_ACCEPTED          UNSATISFIED
SECOND_SMOKE_HARNESS         PROHIBITED_UNLESS_REAUTHORIZED
```

The resolver must preserve the distinction:

```text
historical fact
current applicability
current state
authority
```

No evidence fact grants authority merely by being true.

## 12. Authority Compiler

The Authority Compiler accepts a requested governed outcome and resolves all applicable predecessor and constraint state.

Conceptual input:

```text
requested outcome:
    D5-5J Qwen live confirmation
```

Possible result:

```text
BLOCKED

missing:
    ENVIRONMENT_QUALIFICATION
    ACCEPTED_LIVE_SMOKE
```

or:

```text
INDETERMINATE

cannot establish:
    CURRENT_RUNTIME_IDENTITY
```

or:

```text
READY

authority candidate:
    exact baseline
    exact accepted predecessors
    inherited invariants
    prohibitions
    qualification facts
    evidence lineage
    required context
    hard stops
    resource/namespace consumption
```

Only `READY` is eligible to proceed toward Human authorization.

`READY` is not itself authorization.

## 13. Relationship to WorkPacket

Slice 2.3 remains correct.

It answers:

> What does an exact executable WorkPacket contain and how is its exact subject/context validated?

Slice 2.5 answers:

> How does Relay determine the complete set of prerequisites, constraints, and exact facts that must be reflected in or gate construction of that WorkPacket?

Therefore Slice 2.5 should build on Slice 2.3 rather than reopen it by default.

Conceptually:

```text
canonical project state
      ↓
resolver/compiler
      ↓
authority candidate
      ↓
Human authorization
      ↓
WorkPacket
```

## 14. Operational prerequisites

Operational prerequisites must be typed, machine-resolvable dependencies rather than prose-only checklist items.

Examples:

- network/LAN qualification;
- sandbox or listener capability;
- credential readiness;
- artifact directory writability;
- GPU/model server state;
- runtime/provider route identity;
- fresh campaign namespace;
- smoke acceptance.

Different missing prerequisites may map to existing Relay terminal categories such as `BLOCKED_BY_ENVIRONMENT` or `BLOCKED_BY_CONTRACT`. Slice 2.5 design should reuse existing semantics where sufficient and add a new category only if proven necessary.

## 15. Knowledge Delta

Execution and independent evaluation can discover knowledge that should constrain future work.

They must not silently promote it.

A Knowledge Delta is a proposal for durable state change.

Potential classes:

```text
NEW_INVARIANT
NEW_PREREQUISITE
NEW_APPLICABILITY_RULE
NEW_PROHIBITION
NEW_RESPONSIBILITY_CLAIM
INVALIDATION_RULE
```

Conceptual flow:

```text
terminal evidence / evaluation
        ↓
Knowledge Delta proposal
        ↓
appropriate Relay governance / Human acceptance
        ↓
canonical state
        ↓
future State Resolver
```

This closes the learning loop without granting evaluator or worker authority.

## 16. Example: smoke before scientific live authority

Accepted knowledge:

```text
LIVE_SMOKE_REQUIRED
```

Rationale:

```text
A live campaign previously reached STARTED and failed before turn 1,
consuming a one-shot namespace with zero scientific generation calls.
```

Protects against:

- network/sandbox restrictions;
- provider initialization failure;
- harness initialization failure;
- custody initialization failure;
- environment mismatch.

Dependency:

```text
SCIENTIFIC_LIVE_AUTH
    REQUIRES
        ENVIRONMENT_QUALIFICATION
        LIVE_SMOKE_PASS
        LIVE_SMOKE_INDEPENDENTLY_ACCEPTED
```

A future request for scientific live authority cannot bypass this chain merely because a local agent omitted it from a prompt.

## 17. Example: architecture rediscovery

Existing responsibility:

```text
LIVE_SEMANTIC_CAMPAIGN_EXECUTION
    owner = canonical D5 campaign runner
```

Proposed new component:

```text
SmokeHarnessV2
    responsibility = LIVE_SEMANTIC_CAMPAIGN_EXECUTION
```

Resolver result:

```text
RESPONSIBILITY_COLLISION
existing owner already established
architecture authority required
```

## 18. Phase placement

This capability belongs at the end of Phase 2, after Relay has:

- AgentRuntime contract;
- Role Contracts;
- exact Context/WorkPacket contracts;
- Execution Workspace Authority.

It must precede Phase 3 because Phase 3 is where autonomous execution makes manual reconstruction of predecessor chains especially dangerous.

Proposed ordering:

```text
2.1 Agent Runtime Contract
2.2 Role Contracts
2.3 Context / Work-Packet Contract
2.4 Execution Workspace Authority
2.5 Project State Resolution & Authority Compilation
        ↓
explicit Phase 3 opening
        ↓
governed autonomous engineering loop
```

## 19. Dogfood acceptance direction

Slice 2.5 should eventually dogfood against real failure modes from multiple projects rather than synthetic examples only.

Candidate fixtures include:

- Wellplot: smoke-before-live, exact runtime identity, second-harness prohibition;
- Tension/FEM: scientific-level consumption, exact oracle applicability, one-shot authority;
- Seneca: GPU/backend qualification and experiment succession;
- Relay: exact accepted-predecessor and promotion/closure dependencies.

No external project-specific state is imported by this architecture document.

## 20. Non-goals

This direction does not authorize:

- graph database introduction;
- generic workflow language;
- planner task database;
- automatic Human authority;
- autonomous successor invention;
- reopening accepted WorkPacket/RoleContract schemas without evidence;
- Phase 3 execution;
- production code changes.

The exact domain model, persistence strategy, algorithms, and UI are Slice 2.5 design work under future separate authority.

## 21. Governing summary

```text
accepted knowledge
       ↓
canonical Relay state
       ↓
Project State Resolver
       ↓
Authority Compiler
       ↓
complete authority candidate
       ↓
Human Authority
       ↓
WorkPacket
       ↓
execution
       ↓
independent evaluation
       ↓
Knowledge Delta proposal
       └───────────(after accepted promotion)──→ canonical Relay state
```

This is an extension of Relay's current governance architecture, not a replacement for it.
