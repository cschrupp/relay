# Relay — Slice 1.9 Human Decision Support and Governance Review Surface — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Record:** `RLY-S19-DESIGN-AUTH-001`  
**Decision:** `AUTHORIZED`

## 1. Human Authority decision

The Human explicitly authorized entering the design phase for Slice 1.9.

```text
Slice 1.9:
OPEN — RLY-S19-OPEN-001

Design:
RLY-S19-DESIGN-AUTH-001 — AUTHORIZED

Implementation:
NOT AUTHORIZED
```

Exact design subject baseline:

```text
5bf25378b15955b6e21252ec3f9cc91dcf7192d7
```

Canonical parent underlying the opening:

```text
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7
```

## 2. Authorized design role

```text
Architect / Designer:
GPT-5.6 Sol
```

The architect may inspect the closed Slice 1.8 assurance model and accepted Relay board, Human Authority, governance, manual-evaluation, persistence, repository-contract, and lifecycle seams needed to produce a minimum sufficient Slice 1.9 design.

## 3. Design objective

Design the minimum Relay-owned, Human-facing governance review surface that presents one exact pending Human decision with its current basis, provenance, risks, unknowns, consequences, and existing authority controls.

The design must make consequential decisions easier to inspect without introducing another source of truth.

```text
canonical governed state
    ->
derived Decision Basis
    ->
Decision Card / explanation
    ->
existing explicit Human Authority command
    ->
existing governed state transition
```

The Decision Support layer must remain read/projection logic except for any separately justified optional feedback mechanism. It may never execute a Human Authority action merely because a question was asked, an explanation was generated, a clarity score was supplied, or a basis was complete.

## 4. Required design decisions

The design must resolve at minimum:

1. exact identity of a pending Human decision without confusing it with a recorded `HumanDecisionId` or engineering `DecisionId`;
2. exact subject/basis binding and freshness/staleness semantics;
3. deterministic `DecisionBasisProjection` representation consuming Slice 1.8 semantics;
4. exact applicability states `REQUIRED_PRESENT`, `OPTIONAL_PRESENT`, `NOT_APPLICABLE`, `UNKNOWN`, and `MISSING_REQUIRED`;
5. relationship between `RELAY_DECISION_BASIS_COMPLETE` and the UI projection without introducing a generic property engine;
6. which existing Human actions produce Decision Cards and which remain ordinary operational controls;
7. deduplication of paired choices such as approve/reject and technical accept/reject into one decision;
8. provenance/source-reference representation;
9. change, evidence, evaluation, risk, unknown, blocking-finding, and consequence presentation;
10. integration with existing `HumanActionProjection` and `ManualEvaluationProjection`;
11. decision-scoped Q&A semantics and whether Slice 1.9 M0 uses deterministic structured questions, an LLM, or defers free-form model inference;
12. mandatory answer provenance labels and `UNKNOWN` preservation;
13. selected GovernanceProfile / protected-verification-asset presentation when an authoritative source exists, without inventing a profile engine or taxonomy;
14. optional clarity-feedback boundary and whether persistence is necessary;
15. governance-effectiveness telemetry presentation boundary without implementing collection or policy relaxation;
16. board/UI integration and accessible interaction;
17. stale-basis behavior and action suppression;
18. persistence/schema/dependency requirements, preferring none unless proven necessary;
19. exact implementation change surface;
20. deterministic tests, web tests, and hard-stop cases.

## 5. Mandatory invariants

```text
Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Human Authority
Decision Support != Executed Transition

question != authorization
answer != evidence
clarity rating != acceptance
basis complete != Human understanding
UI capability != Relay authority
runtime capability != Relay authority
```

The design must preserve the existing Human command services as the only write authority for the currently implemented Human actions.

A stale Decision Card may remain inspectable as historical/diagnostic presentation, but it must not make a stale Human action executable.

No model may manufacture missing facts or silently convert `UNKNOWN` to a confident explanation.

## 6. Scope ownership

Slice 1.9 may design:

- Decision Basis and Decision Card read models;
- exact current/freshness projection;
- decision-scoped deterministic explanation/Q&A;
- source and provenance presentation;
- selected profile/risk/verification-asset explanation when authoritative inputs exist;
- optional clarity-feedback contract;
- non-authoritative governance-effectiveness presentation contract;
- integration into the existing server-rendered board;
- tests proving non-authority and stale-basis behavior.

Slice 1.9 must not design enforcement that belongs to Slice 1.10, 2.2, 2.3, or 2.4 except for explicit read-only references to those future owners.

## 7. Explicit non-authority

This design authority does **not** authorize:

- production implementation;
- a database migration;
- new runtime or development dependencies;
- changes to existing lifecycle transition semantics;
- changes to Human Authority semantics;
- changes to accepted Slice 1.8 property definitions;
- a GovernanceProfile taxonomy or selection engine;
- Protected Verification Asset enforcement;
- free-form provider/model execution;
- an LLM dependency;
- automatic authority action from Q&A;
- automatic acceptance or promotion;
- telemetry collection;
- a governance score;
- automatic policy weakening or profile downgrade;
- canonical source/promotion enforcement;
- repository-setting changes;
- Slice 1.10 opening;
- Slice 2.2–2.4 implementation;
- Phase 3;
- real-project agent execution.

If an excluded capability proves necessary, design must stop at that boundary and escalate.

## 8. Required design evaluation

The resulting detailed design must receive independent review against this exact authority and subject baseline with one outcome:

```text
ACCEPT
REVISE
ESCALATE
```

Design evaluation is evidence only. Human design acceptance and implementation authorization remain separate.

## 9. State after authorization

```text
Slice 1.8:
COMPLETE / ACCEPTED / CLOSED

Slice 1.9:
OPEN

Opening:
RLY-S19-OPEN-001 — OPEN

Design:
RLY-S19-DESIGN-AUTH-001 — AUTHORIZED

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Design authorized != design accepted. Design accepted != implementation authorized.**
