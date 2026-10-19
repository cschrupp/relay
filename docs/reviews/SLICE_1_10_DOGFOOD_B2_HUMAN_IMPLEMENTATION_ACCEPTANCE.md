# Slice 1.10 Dogfood B2 — Human Implementation Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Decision date:** 2026-10-18  
**Recorded:** 2026-10-19  
**Project:** Relay  
**Increment:** B2 — Existing Project Adoption / T1 Genesis  
**Record:** `RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

The Human explicitly accepted the independently reviewed B2 implementation.

## Exact accepted subject

```text
Human-accepted composite B2 design:
80b1f77c4d4cd1f3303b4a1072a46b0cfb605621

Implementation authority:
RLY-S110-DOGFOOD-B2-IMPL-AUTH-001 — AUTHORIZED

Initial implementation candidate:
1a97fa1b51306f7a6adcf86d7510703f3c90b908

Independent implementation evaluation 1:
RLY-S110-DOGFOOD-B2-IMPL-EVAL-001 — REWORK

Corrective candidate / exact accepted implementation:
0b3c07dc41d4a0cb81749e8c00a3d006b9645097

Independent implementation evaluation 2:
RLY-S110-DOGFOOD-B2-IMPL-EVAL-002 — ACCEPT

Human implementation acceptance:
RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001 — ACCEPTED
```

## Accepted capability

The accepted implementation provides the bounded B2 capability to admit a valid B1 Adoption Manifest, perform a fresh read-only repository observation, disclose drift, obtain explicit Human `ADOPT` plus the accepted pre-T1 existence attestation, bind actual decision-time T1, create the schema-v8 project-scoped adoption/origin state in a new external database, verify that staged state, and publish it atomically with no-replace semantics.

The accepted capability also preserves strict-v7 origin behavior, keeps strict B0 separate, leaves the adoption-frontier Slice pre-lifecycle for B3, and exposes Project adoption orientation for forward governance.

## Authority boundary

B2 implementation is COMPLETE / HUMAN ACCEPTED.

This acceptance does **not** authorize:

- invoking B2 adoption for Relay or another real project;
- creating the actual Relay T1 or adoption record;
- allocating actual durable adoption identifiers;
- creating, migrating, or publishing the real Relay operational database;
- B3 Forward Re-baseline / First Governed Work;
- B4 onboarding dogfood acceptance;
- canonical/main promotion;
- Slice 2.2+ implementation or Phase 3 agent execution.

Actual Relay adoption/T1 remains behind a separate explicit execution authority.
