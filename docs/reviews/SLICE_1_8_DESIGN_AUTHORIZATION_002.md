# Relay — Slice 1.8 Governance Assurance Reference Model — Supplemental Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Record:** `RLY-S18-DESIGN-AUTH-002`  
**Decision:** `AUTHORIZED`  
**Date:** 2026-10-10

## Human decision

The Human authorizes continued architecture, contract, and detailed design work for Slice 1.8 under the now-canonical amended governance architecture.

This authority supplements, rather than erases, `RLY-S18-DESIGN-AUTH-001`.

It specifically authorizes a Design Revision 2 amendment over the preserved Revision 1 design.

## Exact design basis

```text
Canonical design baseline:
ce848515e95155ec16297fe7a5306248ebd0df54

Resume authority:
RLY-S18-RESUME-001 — RESUMED

Original design authority:
RLY-S18-DESIGN-AUTH-001 — AUTHORIZED

Preserved Design Revision 1:
c67fe2147fcb9a37e7ab13de92bfc79bb8688919

Complete amended re-baseline:
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-ACCEPT-001 — ACCEPTED
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-PROMOTE-001 — AUTHORIZED / CANONICALLY PROMOTED
```

## Authorized Revision-2 scope

Revision 2 must preserve the still-valid Revision-1 decisions and amend the design only where the canonical re-baseline expanded or corrected the architecture.

At minimum it must resolve:

1. Human Decision Support as a cross-cutting, non-authoritative projection around policy-required Human decisions.
2. Policy-specific `DecisionBasisProjection` completeness and the distinction among `REQUIRED_PRESENT`, `OPTIONAL_PRESENT`, `NOT_APPLICABLE`, `UNKNOWN`, and `MISSING_REQUIRED`.
3. `RELAY_DECISION_BASIS_COMPLETE`.
4. `RELAY_ACTOR_IDENTITY_BOUND` and the invariant `role != identity != authority`.
5. `RELAY_EXECUTION_PROVENANCE_SUFFICIENT` as policy/risk-relative rather than universal full-trajectory logging.
6. External-assurance mapping freshness and stale-to-`UNKNOWN` semantics for new external claims.
7. The Human-gate necessity rule: discretionary Human authority decisions remain Human; deterministic checks should increasingly be mechanical.
8. Workflow-agnostic governance: Relay-native planning is supported but not required; upstream workflow artifacts cannot import Relay authority.
9. Future planning-artifact normalization boundary and downstream requirements for Slice 2.3 without defining adapter implementation.
10. `GovernanceProfile` semantics, policy/risk inputs, exact subject/profile binding, escalation, downgrade authority, and fail-closed unknown inputs.
11. Proposed `RELAY_GOVERNANCE_PROFILE_BOUND`.
12. Protected Verification Asset semantics, including the distinction between implementation tests and policy/acceptance/evaluation assets and the principle that protection concerns mutation authority rather than secrecy.
13. Proposed `RELAY_VERIFICATION_ASSETS_PROTECTED`.
14. Governance-effectiveness telemetry as non-authoritative observation, preserving separate assurance-value and governance-cost dimensions.
15. Decision Support presentation requirements for profile/risk rationale, required gates/evidence, protected verification assets, and decision-scoped Q&A.
16. Downstream ownership boundaries across Slices 1.9, 1.10, 2.2, 2.3, 2.4, and 3.1.
17. Conservative source provenance and external-standard mapping, preserving Relay-native semantics over SLSA, NIST SSDF, DORA, Consort, Spec Kit, OpenSpec, BMAD, or any other external framework or methodology.
18. Versioning, compatibility, examples, negative cases, and traceability needed to make the combined Revision 1 + Revision 2 design independently reviewable.

## Mandatory invariants

```text
Evidence PASS != Evaluation ACCEPT
Evaluation ACCEPT != Human acceptance
Human acceptance != Promotion

Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Authority

Normalized upstream intent != authorized Work Packet
External workflow status != Relay authority

Role != identity != authority
Implementer cannot self-downgrade governance
Telemetry cannot relax policy

Protection concerns mutation authority;
not every test is immutable or hidden

Execution cannot manufacture authority
Evidence cannot manufacture authority
Evaluation cannot manufacture authority
Promotion executor != promotion decision maker
```

## Design artifact rule

Revision 1 remains immutable historical design input.

Revision 2 should be recorded as a separate amendment document or equivalent new design artifact, with explicit precedence where it differs from Revision 1.

The combined design subject for evaluation is:

```text
Revision 1
+
Revision 2 amendment
```

Do not silently rewrite Revision 1.

## Explicit non-authority

This authority does not authorize:

- Slice 1.8 implementation;
- source/runtime/test/dependency/schema changes;
- database or API implementation;
- Decision Card or Q&A implementation;
- GovernanceProfile implementation;
- planning adapters;
- workspace enforcement;
- Protected Verification Asset enforcement;
- telemetry collection or dashboard implementation;
- attestation or compliance engines;
- branch/ruleset/repository-setting changes;
- trusted promotion executor implementation;
- competitive experiment execution;
- Slice 1.9 or 1.10 opening;
- Phase 3;
- autonomous or real-project agent execution.

If design concludes an excluded implementation capability is necessary, stop at that boundary and escalate.

## Review requirement

The resulting combined Revision 1 + Revision 2 design must receive Sol review with outcome:

```text
ACCEPT
REWORK
ESCALATE
```

Design evaluation does not grant Human design acceptance or implementation authorization.

## Resulting state

```text
Slice 1.8:
OPEN / ACTIVE DESIGN

Design authority:
RLY-S18-DESIGN-AUTH-001 — HISTORICAL / STILL VALID WHERE NOT SUPERSEDED
RLY-S18-DESIGN-AUTH-002 — AUTHORIZED FOR REVISION 2

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED
```
