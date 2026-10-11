# Slice 1.8 - Governance Assurance Reference Model

**Status:** OPEN / DESIGN ACCEPTED / IMPLEMENTATION NOT AUTHORIZED
**Phase:** 1 - Accepted Baseline / Hardening Active
**Opening authority:** RLY-S18-OPEN-001 - OPEN
**Design authority:** RLY-S18-DESIGN-AUTH-001 - AUTHORIZED (historical scope); RLY-S18-DESIGN-AUTH-002 - AUTHORIZED FOR REVISION 2
**Roadmap authority:** RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED

**Pause history:** `RLY-S18-PAUSE-001` — SATISFIED
**Resume:** `RLY-S18-RESUME-001` — RESUMED
**Re-baseline authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001`
**Strategic amendment authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001`

## Current governed state

```text
Slice 1.8: OPEN
Opening: RLY-S18-OPEN-001 — OPEN
Design authority: RLY-S18-DESIGN-AUTH-001 — HISTORICAL / STILL VALID WHERE NOT SUPERSEDED
Resume: RLY-S18-RESUME-001 — RESUMED
Supplemental design authority: RLY-S18-DESIGN-AUTH-002 — AUTHORIZED FOR REVISION 2
Design Revision 1: PRESERVED PRE-REBASELINE INPUT
Design Revision 2 + Rework 1: PRODUCED / INDEPENDENTLY ACCEPTED
Design evaluation: RLY-S18-DESIGN-EVAL-002 — ACCEPT
Human design acceptance: RLY-S18-DESIGN-ACCEPT-001 — ACCEPTED
Implementation: NOT AUTHORIZED
```

Design Revision 1 is the review-ready head `c67fe2147fcb9a37e7ab13de92bfc79bb8688919` on `design/slice-1.8-governance-assurance-reference-model`. It is preserved pre-rebaseline input, not reviewed, not Human-accepted, and not implementation authority. Preserve that branch and head unchanged.

## Objective

Turn the governance-assurance direction into an independently reviewed Relay-native reference model without making SLSA, SSDF, DORA, or another external framework Relay's domain model [SRC-SLSA-V1_2] [SRC-NIST-SSDF-1_1] [SRC-DORA-CHANGE-APPROVAL].

## Design scope

Define and review:

- Relay-native vs external-compliance requirements;
- control, execution, evidence, verification, and promotion planes;
- native lifecycle claim boundaries;
- attestation-envelope direction;
- actor/verifier/trust terminology needed by later Role Contracts;
- Relay-native verified properties;
- conservative compliance-claim rules;
- standards-mapping direction;
- DORA-style governance-overhead guardrails [SRC-DORA-CHANGE-APPROVAL].
- the cross-cutting Decision Support boundary and policy-specific `DecisionBasisProjection` completeness;
- conceptual `GovernanceProfile`, risk inputs, exact subject/profile binding, and escalation/downgrade authority;
- proposed `RELAY_GOVERNANCE_PROFILE_BOUND` and `RELAY_VERIFICATION_ASSETS_PROTECTED` semantics;
- Protected Verification Asset designation, mutation-authority boundary, and role separation;
- governance-effectiveness telemetry as non-authoritative, with assurance value separate from governance cost;
- workflow-agnostic control-plane semantics, including the rule that upstream workflow artifacts cannot import Relay authority;
- external mapping freshness and the previously established identity/provenance properties;
- downstream `ContextManifest` and planning-artifact interoperability requirements for Slice 2.3.

### Future Design Revision 2 expectations

The complete amended re-baseline was independently reviewed, Human-accepted, and canonically promoted. Slice 1.8 was resumed; Revision 2 and Rework 1 now address the requirements above and are accepted as part of the combined design. It should also resolve applicable versus unknown versus missing decision-basis components; define profile-selection inputs without a final scoring formula or taxonomy; prohibit implementer/runtime/provider self-downgrade; define policy-authorized escalation and durable downgrade; distinguish implementation tests from policy/acceptance/evaluation assets; and preserve tri-valued `PASS / FAIL / UNKNOWN` semantics. This expectation list is satisfied by the accepted Revision 2 Amendment and Rework 1, subject to their exact precedence over Revision 1.

## Out of scope

Branch/ruleset mutation, promotion implementation, typed attestation implementation, SLSA level claims, Role Contract implementation, and agent execution.

## Exit bar

```text
[ ] Relay/external-standard boundary accepted
[ ] plane architecture accepted
[ ] verified-property vocabulary accepted
[ ] attestation direction accepted
[ ] compliance-claim policy accepted
[ ] standards-mapping direction accepted
[ ] no external framework becomes Relay's domain model
```

## Hard stop

This proposal preserves Relay's gate grammar:

```text
PLANNED != OPEN
OPEN != DESIGN AUTHORIZED
DESIGN ACCEPTED != IMPLEMENTATION AUTHORIZED
IMPLEMENTED != ACCEPTED
ACCEPTED != PROMOTED
```

Slice 1.8 is opened administratively under RLY-S18-OPEN-001.

Design was originally authorized under `RLY-S18-DESIGN-AUTH-001`; after the canonical re-baseline, Slice 1.8 resumed under `RLY-S18-RESUME-001` and supplemental Revision-2 design authority is `RLY-S18-DESIGN-AUTH-002`. These authorities permit architecture, contract, and detailed design work only.

Human design acceptance is recorded as `RLY-S18-DESIGN-ACCEPT-001`. It does not authorize implementation; implementation requires separate explicit authorization.

The opening and design-authorization records authorize design work but no implementation transition. After the design is produced and independently reviewed by Sol, Human design acceptance remains a separate gate.
