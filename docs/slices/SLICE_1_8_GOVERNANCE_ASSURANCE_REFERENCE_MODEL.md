# Slice 1.8 - Governance Assurance Reference Model

**Status:** OPEN / DESIGN AUTHORIZED / PAUSED — ARCHITECTURE / ROADMAP REBASE / IMPLEMENTATION NOT AUTHORIZED
**Phase:** 1 - Accepted Baseline / Hardening Active
**Opening authority:** RLY-S18-OPEN-001 - OPEN
**Design authority:** RLY-S18-DESIGN-AUTH-001 - AUTHORIZED
**Roadmap authority:** RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED

**Pause:** `RLY-S18-PAUSE-001`
**Re-baseline authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001`

## Current governed state

```text
Slice 1.8: OPEN
Opening: RLY-S18-OPEN-001 — OPEN
Design authority: RLY-S18-DESIGN-AUTH-001 — AUTHORIZED
Pause: RLY-S18-PAUSE-001 — PAUSED — ARCHITECTURE / ROADMAP REBASE
Design Revision 1: PRESERVED PRE-REBASELINE INPUT
Design review: NOT STARTED
Human design acceptance: NOT GRANTED
Implementation: NOT AUTHORIZED
Design Revision 2: NOT PRODUCED / NOT AUTHORIZED
```

Design Revision 1 is the review-ready head `c67fe2147fcb9a37e7ab13de92bfc79bb8688919` on `design/slice-1.8-governance-assurance-reference-model`. It is not reviewed, not Human-accepted, and not implementation authority. Preserve that branch and head unchanged.

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

### Future Design Revision 2 expectations

If separately authorized after the re-baseline is reviewed and Human-accepted, a future revision should address the Decision Support boundary and `DecisionBasisProjection`; `RELAY_DECISION_BASIS_COMPLETE`; `RELAY_ACTOR_IDENTITY_BOUND`; `RELAY_EXECUTION_PROVENANCE_SUFFICIENT`; external mapping freshness; Human-gate necessity; and the downstream Slice 2.3 `ContextManifest` requirement. External source references provide provenance, not Relay authority. No Revision 2 is produced or authorized here.

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

Design is authorized under RLY-S18-DESIGN-AUTH-001. This authorization permits architecture, contract, and detailed design work only.

Design acceptance does not authorize implementation. Implementation requires separate explicit authorization.

The opening and design-authorization records authorize design work but no implementation transition. After the design is produced and independently reviewed by Sol, Human design acceptance remains a separate gate.
