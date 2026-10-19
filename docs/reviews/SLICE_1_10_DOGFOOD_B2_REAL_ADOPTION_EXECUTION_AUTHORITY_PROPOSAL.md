# Slice 1.10 Dogfood B2 — Real Relay Adoption / T1 Execution Authority Proposal

**Document class:** Working authority proposal  
**Status:** PROPOSED / NOT AUTHORIZED  
**Prepared:** 2026-10-19  
**Project:** Relay  
**Increment:** B2 — Existing Project Adoption / T1 Genesis  
**Proposed record:** `RLY-S110-DOGFOOD-B2-ADOPTION-AUTH-001`

## Purpose

Prepare the consequential execution gate for adopting the Relay repository itself with the Human-accepted B2 implementation.

This document is **not authority**. It defines the evidence and exact bindings that must exist before the Human can issue the real-adoption authorization.

## Accepted implementation basis

```text
Human-accepted B2 implementation:
0b3c07dc41d4a0cb81749e8c00a3d006b9645097

Independent implementation evaluation:
RLY-S110-DOGFOOD-B2-IMPL-EVAL-002 — ACCEPT

Human implementation acceptance:
RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001 — ACCEPTED
```

## Target execution

The proposed authority is limited to one real adoption transaction for:

```text
Project:
Relay

Canonical repository:
github.com/cschrupp/relay

Operation:
B2 Existing Project Adoption / T1 Genesis
```

The execution must use the accepted B2 implementation capability without widening its semantics.

## Required evidence before authorization

The actual immutable execution authority must bind, at minimum:

1. the exact Human-accepted B2 implementation candidate `0b3c07dc...`;
2. one fresh B0-F report produced from the real Relay checkout;
3. one Human-reviewed B1 Adoption Manifest bound to that exact report;
4. the exact canonical repository identity resolved from the B1 Human-confirmed fact;
5. the exact inspected repository root and clean observed HEAD entering the adoption plan;
6. the selected external operational database destination;
7. confirmation that the destination does not already exist and is outside the inspected repository;
8. the exact Human actor who will perform the `ADOPT` decision;
9. the accepted B2 requirement that T1 is the actual UTC decision timestamp generated only after exact interactive `ADOPT`;
10. confirmation that B3/B4 and lifecycle initialization remain outside this authority.

If any required input is missing, unresolved, stale, inconsistent, or materially changes before the Human decision, the real-adoption authority must not be issued or the execution must stop fail-closed.

## Proposed authorized execution envelope

Once the required bindings exist and the Human explicitly authorizes the operation, the execution authority may permit only:

- read-only fresh inspection of the real Relay checkout;
- strict admission of the exact B0-F report and B1 manifest;
- display of the deterministic B2 adoption plan and drift disclosure;
- display of the accepted pre-T1 Human attestation;
- one exact interactive `ADOPT` decision by the bound Human actor;
- actual decision-time T1 creation;
- post-ADOPT full report-state and repository-fingerprint equality verification;
- same-directory staging of one new external schema-v8 operational database;
- creation of the B2 Project, exact baseline, immutable adoption record, project-scoped adoption epoch, Project PRE_GENESIS origin, and adoption-frontier NATIVE_RELAY Slice;
- complete staged integrity/origin/read-model verification;
- final repository HEAD/clean verification;
- atomic no-replace publication of that one new external database;
- read-only inspection of the resulting Project adoption orientation;
- collection of execution evidence for independent B2 real-adoption review.

## Explicitly outside the proposed authority

The eventual authority must not permit:

- target-repository mutation as part of adoption;
- changing the accepted B2 implementation;
- backdating or caller-supplying T1;
- reconstructing pre-T1 Relay lifecycle, authority, evaluation, execution, or promotion history;
- applying migration v8 to an existing operational database;
- replacing or overwriting an existing database destination;
- initializing lifecycle for the adoption-frontier Slice;
- B3 forward re-baseline work;
- B4 dogfood acceptance;
- main/canonical promotion;
- Slice 2.2+, OpenCode-managed execution, or Phase 3 work.

## Stop conditions

The execution must stop before publication on any:

- invalid/stale B0-F or B1 input;
- canonical repository identity conflict;
- dirty repository state;
- Human cancellation or non-exact `ADOPT`;
- post-ADOPT report-state or fingerprint mismatch;
- database destination collision;
- staged database integrity/origin/read-model failure;
- final repository identity/HEAD/cleanliness mismatch;
- attempt to cross into B3/B4 or mutate the target repository.

## Next gate

Before this proposal can become `RLY-S110-DOGFOOD-B2-ADOPTION-AUTH-001 — AUTHORIZED`, complete the real B1 dogfood input for Relay and bind the exact resulting report, manifest, repository observation, actor, and external database destination.

Until then:

```text
REAL RELAY ADOPTION / T1 — NOT AUTHORIZED
```
