# Relay — Slice 1.8 Governance Assurance Reference Model — Human Design Acceptance

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-10  
**Record:** RLY-S18-DESIGN-ACCEPT-001  
**Decision:** ACCEPTED

## Reviewed design lineage

~~~text
Slice opening: RLY-S18-OPEN-001 — OPEN
Original design authorization: RLY-S18-DESIGN-AUTH-001 — AUTHORIZED
Pause: RLY-S18-PAUSE-001 — PAUSED
Resume: RLY-S18-RESUME-001 — RESUMED
Supplemental design authorization: RLY-S18-DESIGN-AUTH-002 — AUTHORIZED

Revision 1:
c67fe2147fcb9a37e7ab13de92bfc79bb8688919

Revision 2 Amendment:
87acec9b961e9d3773f75922dddb29520cb55e3b

Independent combined evaluation 1:
RLY-S18-DESIGN-EVAL-001 — REWORK
f19f8023fc01a16be70a298b4cb7fd6c204a9555

Revision 2 Rework 1:
ef89856816e1671443eec0a4422742b35e1e32df

Independent combined evaluation 2:
RLY-S18-DESIGN-EVAL-002 — ACCEPT
c41f47089e9d8bf311a3f8c4b39ca803665888cc

Canonical design-lineage preservation merge:
84c8a83a912c40ef51c414bae809b876fd6d930c
~~~

## Human Authority decision

The Human explicitly accepts the exact combined Slice 1.8 design:

~~~text
Revision 1
+ Revision 2 Amendment
+ Revision 2 Rework 1
= ACCEPTED
~~~

Revision 2 Rework 1 is normative where it resolves or qualifies Revision 2. Revision 2 is normative where it changes or qualifies Revision 1. Revision 1 remains normative where later amendments are silent.

## Accepted architecture boundary

The accepted design establishes Relay's governance-assurance reference model for exact assurance subjects, evidence/evaluation/authority separation, cross-cutting Human Decision Support, policy-specific decision-basis completeness, actor identity binding, policy-relative execution provenance, risk-adaptive GovernanceProfile semantics, Protected Verification Assets, workflow-agnostic planning-artifact normalization, non-authoritative governance-effectiveness telemetry, external-assurance mapping freshness, and the corrected downstream Slice ownership model.

Accepted native properties added or clarified by the combined design include:

~~~text
RELAY_DECISION_BASIS_COMPLETE
RELAY_ACTOR_IDENTITY_BOUND
RELAY_EXECUTION_PROVENANCE_SUFFICIENT
RELAY_GOVERNANCE_PROFILE_BOUND
RELAY_VERIFICATION_ASSETS_PROTECTED
~~~

## Accepted non-substitutability

~~~text
Evidence PASS != Evaluation ACCEPT
Evaluation ACCEPT != Human acceptance
Human acceptance != Promotion

Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Authority

Role != identity != authority
Normalized upstream intent != authorized Work Packet
External workflow state != Relay authority
Evaluator review != verification-asset mutation authority
Telemetry != authority
Telemetry != evaluation
~~~

## Authority boundary

This record accepts the design only.

It does not authorize Slice 1.8 implementation, production source/runtime/test/dependency/schema changes, Decision Card or Q&A implementation, GovernanceProfile implementation, planning adapters, Protected Verification Asset enforcement, workspace enforcement, telemetry collection, attestation/compliance engines, repository-setting mutation, trusted promotion-executor implementation, competitive benchmark execution, Slice 1.9 or 1.10 opening, Phase 3, or autonomous/real-project agent execution.

A separate Human implementation authorization is required.

**Design accepted != implementation authorized. Unblocked != authorized.**
