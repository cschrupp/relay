# Slice 1.10 Dogfood B2 — Existing Project Adoption / T1 Genesis — Design Authorization

**Document class:** Immutable Human authorization record  
**Status:** IMMUTABLE  
**Date:** 2026-10-18  
**Project:** Relay  
**Increment:** B2 — Existing Project Adoption / T1 Genesis  
**Record:** `RLY-S110-DOGFOOD-B2-DESIGN-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly opened B2 design after Human acceptance of B1 Project Discovery and Human Intake.

This record authorizes **design only**. B2 implementation, T1 creation, operational-state creation, and repository adoption are not authorized.

## Exact design baseline

```text
Repository:
cschrupp/relay

B1 Human implementation acceptance:
RLY-S110-DOGFOOD-B1-IMPL-ACCEPT-001 — ACCEPTED

B1 accepted implementation:
22fb742965ed6424a18275b4234e1399021d4aed

B1 acceptance successor / B2 design baseline:
0108a9299575bbb3913eb96d2c19bc6c525d5a4f

B2 design authority:
RLY-S110-DOGFOOD-B2-DESIGN-AUTH-001 — AUTHORIZED
```

## Product objective

Design the bounded adoption transaction that converts a valid B1 Adoption Manifest candidate plus fresh repository evidence into a trustworthy Relay operational starting point at T1.

The core question is:

> How does Relay establish an existing project's first truthful operational state from now forward without pretending that Relay governed the project's pre-T1 history?

## Required design subjects

1. **B1 admission contract**
   - exact accepted manifest format/version and readiness requirement;
   - validation of B1 provenance and report binding;
   - treatment of incomplete or stale manifests;
   - no implicit promotion from READY_FOR_B2_REVIEW to adoption.

2. **Fresh repository re-observation**
   - B2 must define how current repository state is re-observed immediately before adoption;
   - define what happens when HEAD, branch, dirty state, canonical repository evidence, or other relevant observed facts differ from the B1-bound discovery report;
   - stale evidence must not be silently adopted.

3. **Human adoption decision**
   - define the exact Human decision that authorizes creation of T1 operational state;
   - distinguish manifest review/readiness from actual adoption authorization;
   - no agent/model may self-authorize adoption.

4. **T1 semantics**
   - define the exact meaning of T1 and its timestamp/provenance;
   - identify which facts become the operational baseline at T1;
   - explicitly state that no Relay lifecycle, approval, execution, evaluation, or promotion history is asserted before T1.

5. **Project and Slice identity creation**
   - define when Relay-native ProjectId/SliceId values are created;
   - define which present/future work receives an initial Slice identity;
   - distinguish identity creation time from whether the underlying project/work existed before T1.

6. **PG1 origin reconciliation**
   - reconcile B2 adoption with `PRE_GENESIS | NATIVE_RELAY` operational-origin semantics;
   - do not equate a newly allocated Relay ID with `NATIVE_RELAY` if the represented subject actually existed before T1;
   - define origin assignment for the adopted Project and any initial Slice/work subject.

7. **Operational state initialization**
   - define the minimum Relay state created at adoption;
   - objective, current status, constraints, repository binding, frontier/first governed focus, blockers, next Human action, and selected legacy context;
   - define what belongs in durable Relay state versus descriptive context.

8. **Persistence / atomicity / restart safety**
   - define the durable transaction boundary for T1;
   - partial adoption must fail closed and must not leave ambiguous half-created operational state;
   - define retry/reconciliation behavior without inventing duplicate identities or duplicate T1 events.

9. **Board/current-state projection**
   - define the minimum Human-readable CURRENT / NEXT / LATER / BLOCKED state produced by adoption;
   - B2 must make the adopted project usable without reconstructing context from chat.

10. **B2/B3 boundary**
   - B2 creates the truthful operational starting point;
   - B3 performs the forward work re-baseline, prioritization, acceptance criteria, dependencies, and opening of the first normal post-adoption governed Slice;
   - do not pull general planning into B2 unless required to make the T1 state coherent.

## Provenance rules

The design must preserve:

```text
OBSERVED
!= HUMAN_CONFIRMED
!= historical context
!= operational fact created at T1
```

Selected legacy names/releases/issues/documents may be retained as context, but they must not be transformed into fabricated Relay-native historical lifecycle records.

## Design constraints

- Existing-project adoption is the normal legacy path; strict B0 exact-state bootstrap remains separate and fail-closed.
- B2 must use the accepted B1 manifest contract rather than creating a second Human questionnaire.
- Fresh machine facts should be re-observed rather than Human-overridden.
- Human intent remains authoritative only where the design explicitly requires Human confirmation.
- Prefer the minimum sufficient operational state needed to make B3 useful.
- No LLM/model output may become adoption authority or authoritative state merely by inference.

## Explicit non-goals / not authorized

- B2 implementation.
- execution of a real adoption or creation of T1.
- ProjectId/SliceId allocation in a real repository/database.
- database migration or operational database writes.
- target-repository mutation.
- synthesis of pre-T1 Relay lifecycle/history.
- B3 implementation or first normal governed post-adoption Slice.
- B4 dogfood acceptance.
- Slice 2.2+ or Phase 3.
- canonical/main promotion.

## Design success condition

The B2 design is successful when an implementer can build a flow equivalent to:

```text
valid READY_FOR_B2_REVIEW manifest
        +
fresh repository observation
        ↓
Human adoption decision
        ↓
atomic T1 genesis
        ↓
Relay-native operational identities + truthful current baseline
        ↓
CURRENT / NEXT / LATER / BLOCKED visible
        ↓
ready for B3 forward re-baseline
```

with no fictional pre-T1 Relay history and no ambiguity about whether adoption actually occurred.

## Governance-cost guardrail

B2 is a product-state transition design, not an ontology exercise. Any new artifact, state, authority type, or persistence rule must identify the concrete adoption-integrity or usability problem it solves.

## Documentation synchronization

Opening B2 changes the active frontier. Build Plan, Current Baseline, and TODO are updated in this same authority increment. B2 design closeout must repeat the synchronization check.

## Boundary after authorization

```text
B0-F: COMPLETE / HUMAN ACCEPTED
B1: COMPLETE / HUMAN ACCEPTED
B2: DESIGN OPEN / AUTHORIZED
B2 implementation: NOT AUTHORIZED
T1 creation: NOT AUTHORIZED
B3/B4: PLANNED / NOT OPEN / NOT AUTHORIZED
Strict B0: BLOCKED / separate exact-state path
Canonical/main promotion: NOT AUTHORIZED
```
