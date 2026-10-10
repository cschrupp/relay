# Slice 1.8 - Governance Assurance Reference Model

**Status:** FUTURE HARDENING SLICE PROPOSAL - NOT OPEN / NOT AUTHORIZED  
**Phase:** 1 - Accepted Baseline / Hardening Active  
**Roadmap authority:** `RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED`

## Objective

Turn the governance-assurance direction into an independently reviewed Relay-native reference model without making SLSA, SSDF, DORA, or another external framework Relay's domain model.

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
- DORA-style governance-overhead guardrails.

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

Opening this Slice requires separate Human Authority.
