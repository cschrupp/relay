# Relay — Slice 1.10 Canonical Source and Promotion Enforcement — Human Technical Acceptance 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / ACCEPTED  
**Date:** 2026-10-25  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Acceptance ID:** `RLY-S110-ACCEPT-001 — ACCEPTED`  
**Human decision:** ACCEPTED  
**Exact implementation subject:** `8003170f56120640ab29eb776cc1b2ba53c66a5f`  
**Independent implementation evaluation:** `RLY-S110-IMPL-EVAL-001 — ACCEPT`  
**Evaluation record commit:** `0d151d11cfb5b167678d229cf4234b8a5c95d545`  
**Historical exact-head CI:** `38307308578 — SUCCESS`  
**Compatibility frontier:** canonical `main` `da966f67676a227488ef216d388d405b5e383d93`  
**Compatibility CI:** `40165012106 — SUCCESS`

## 1. Human technical acceptance

The Human Authority accepts exact historical Slice 1.10 implementation candidate:

`8003170f56120640ab29eb776cc1b2ba53c66a5f`

against the Human-accepted Slice 1.10 composite design and the independent technical evaluation:

`RLY-S110-IMPL-EVAL-001 — ACCEPT`.

This acceptance is top-level Slice 1.10 technical acceptance. It is distinct from the already accepted B0–B4 dogfood/onboarding subprogram results.

## 2. Accepted implementation boundary

The accepted implementation is the exact historical subject reviewed under:

- `RLY-S110-DESIGN-EVAL-004 — ACCEPT`;
- `RLY-S110-DESIGN-ACCEPT-001 — ACCEPTED`;
- `RLY-S110-IMPL-AUTH-001 — AUTHORIZED`;
- `RLY-S110-IMPL-EVAL-001 — ACCEPT`.

The accepted technical boundary includes the canonical-source/promotion substrate already independently verified for:

- exact typed Human repository-mutation authority;
- canonical promotion policy and append-only binding history;
- fail-closed binding resolution;
- RepositorySync fencing for managed canonical refs;
- exact promotion subject/digest binding;
- required-check SHA/name/App freshness;
- isolated GET-only source-control verifier;
- exact ruleset conformance;
- non-force canonical ref mutation;
- durable pre-write intent and immutable terminal results;
- restart-first recovery;
- derived `VISIBLE_UNVERIFIED` quarantine;
- exact zero-write Human-authorized reconciliation;
- migration-v6 four-table append-only persistence contract.

## 3. Compatibility with later shared-file evolution

The Human accepts the independent compatibility finding that later accepted shared-file evolution does not invalidate the historical Slice 1.10 implementation subject.

The accepted technical subject remains:

`8003170f56120640ab29eb776cc1b2ba53c66a5f`.

Later changes to shared IDs/persistence infrastructure are not retroactively folded into that subject.

The current canonical main compatibility frontier reviewed under `RLY-S110-IMPL-EVAL-001` is:

`da966f67676a227488ef216d388d405b5e383d93`.

## 4. What this acceptance grants

This record grants Human technical acceptance of exact Slice 1.10 implementation subject:

`8003170f56120640ab29eb776cc1b2ba53c66a5f`.

Slice 1.10 is now eligible for separately governed finalization / closure authority.

## 5. What this acceptance does not grant

This record does not authorize:

- Slice 1.10 closure by itself;
- closure-ready projection/bookkeeping work;
- canonical promotion of any new Slice 1.10 closure state;
- production policy-binding execution;
- live canonical-ref mutation;
- live quarantine reconciliation;
- GitHub ruleset/branch-protection mutation;
- GitHub App/credential/permission mutation;
- production ProjectStateResolver / AuthorityCompiler wiring;
- production WorkPacket compilation/wiring;
- AgentRuntime/provider/model execution;
- real-project autonomous engineering;
- opening Slice 3.1.

Those remain subject to separate authority.

## 6. Resulting governance state

```text
RLY-S110-ACCEPT-001 — ACCEPTED

Slice 1.10 implementation:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Exact accepted implementation subject:
8003170f56120640ab29eb776cc1b2ba53c66a5f

Slice 1.10:
OPEN / TECHNICALLY ACCEPTED / CLOSURE ELIGIBLE

Slice 1.10 closure authority:
NOT YET GRANTED

Phase 3:
OPEN

Slice 3.1:
NOT OPEN / NOT AUTHORIZED

Phase 3 execution:
GATED by Slice 1.10 top-level closure

Real-project execution:
NOT AUTHORIZED
```

**Technical acceptance != closure. Closure remains a separate Human-authorized governance transition.**
