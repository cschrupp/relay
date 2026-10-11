# Relay — Slice 1.9 Human Decision Support and Governance Review Surface — Human Design Acceptance

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Record:** RLY-S19-DESIGN-ACCEPT-001  
**Decision:** ACCEPTED

## 1. Human Authority decision

The Human stated:

> Slice 1.9 combined design authorized

At the current governance gate, this is recorded as Human acceptance/authorization of the exact combined Slice 1.9 design. It is not implementation authorization.

## 2. Accepted design lineage

~~~text
Canonical parent:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

Opening:
RLY-S19-OPEN-001 — OPEN
commit 5bf25378b15955b6e21252ec3f9cc91dcf7192d7

Design authority:
RLY-S19-DESIGN-AUTH-001 — AUTHORIZED
commit 8ea33bb01c94dd0fc7d24185702ad4f98ed1b687

Design Revision 1:
47af7b62a1d02f0224cc9a5c696898e8302bff56

Independent evaluation 001:
RLY-S19-DESIGN-EVAL-001 — REVISE
commit d2a0889d35b3cc06e7dcf5375a691b57fb5f185a

Rework 1:
731da541dbbae49ee890736eba9393e5d223b226

Independent evaluation 002:
RLY-S19-DESIGN-EVAL-002 — REVISE
commit 9da55a2c55656928e9aa2cf1e3244a8d595cde44

Rework 2 / exact accepted combined-design subject:
03d6efecf9ad4aaec0c5967b9486650399d0a492

Independent evaluation 003:
RLY-S19-DESIGN-EVAL-003 — ACCEPT
record lineage head d4a7accf38135ad939fccd3114ac2d884254ffc8

Exact-head CI on evaluation-record lineage:
38151731831 — SUCCESS
~~~

## 3. Accepted combined design

The Human accepts:

~~~text
Design Revision 1
+ Rework 1 Addendum
+ Rework 2 Addendum
= ACCEPTED
~~~

Rework 2 is normative where it changes Revision 1 or Rework 1.
Rework 1 is normative where it changes Revision 1.
Revision 1 remains normative where later addenda are silent.

## 4. Accepted architecture boundary

The accepted design establishes:

- a derived, non-authoritative Decision Support layer;
- four bounded Human-decision card kinds;
- exact versioned DecisionBasisIdentityV1 semantics;
- canonical SHA-256 basis-digest construction for navigation/freshness;
- preservation of existing HumanActionBasis and existing POST mutation CAS;
- PENDING_REQUIRED versus RECORDED_REVISABLE decision state;
- per-kind decision-basis applicability/completeness rules;
- exact source/provenance presentation;
- deterministic fact/evaluator/unknown statement separation;
- deterministic structured decision-scoped Q&A with no provider/model execution;
- exact multi-outcome path-choice presentation;
- same-snapshot SliceDetail integration;
- server-rendered accessible UI integration;
- no database migration and no dependency change;
- deferred clarity-feedback persistence and governance-effectiveness telemetry collection;
- preservation of Slice 1.10 and Slices 2.2–2.4 ownership boundaries.

## 5. Preserved non-substitutability

~~~text
Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Human Authority
Decision Support != Executed Transition

question != authorization
answer != evidence
clarity rating != acceptance
basis complete != Human understanding

action exists != decision is pending
basis_digest != mutation authority
UI capability != Relay authority
runtime capability != Relay authority
~~~

## 6. Explicit implementation boundary

This record accepts the design only.

It does not authorize:

- production implementation;
- source/runtime/test changes;
- a database migration;
- new tables;
- runtime or development dependencies;
- lifecycle semantic changes;
- Human Authority semantic changes;
- mutation-service redesign;
- a GovernanceProfile taxonomy or selection engine;
- Protected Verification Asset enforcement;
- free-form Q&A;
- LLM/provider/model execution;
- persistent chat;
- clarity-feedback persistence;
- telemetry collection or governance scoring;
- canonical-source or promotion enforcement;
- repository-setting changes;
- Slice 1.10 opening;
- Slice 2.2–2.4 implementation;
- Phase 3;
- real-project agent execution.

A separate Human implementation authorization is required.

## 7. Resulting state

~~~text
Slice 1.9:
OPEN

Combined design:
RLY-S19-DESIGN-ACCEPT-001 — ACCEPTED

Independent design evaluation:
RLY-S19-DESIGN-EVAL-003 — ACCEPT

Implementation:
NOT AUTHORIZED

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~

**Design accepted != implementation authorized.**
