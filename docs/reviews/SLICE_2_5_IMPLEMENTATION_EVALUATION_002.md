# Relay — Slice 2.5 Project State Resolution and Authority Compilation — Implementation Evaluation 002

**Document class:** Immutable independent SOL implementation evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Evaluation:** `RLY-S25-IMPL-EVAL-002 — REWORK / NARROW`

## Evaluated subject

```text
Repository:
cschrupp/relay

Corrective branch:
implementation/2.5-project-state-resolution-authority-compilation-rework-001

Reviewed corrective candidate:
18a4a6c4d8553c165d4a6888e09c87478be3474c

Exact corrective parent:
f509bd35ce5d6903d647095d6ec03dc2b881a8d4

Corrective authority:
RLY-S25-IMPL-REWORK-AUTH-001 — AUTHORIZED

Prior implementation evaluation:
RLY-S25-IMPL-EVAL-001 — REWORK / NARROW
```

The candidate is exactly one commit ahead of the authorized corrective baseline, changes only authorized Slice 2.5 implementation/test files, and exact-head GitHub Actions run `40155227384` completed successfully for the reviewed SHA.

Build/test success is evidence only and does not establish engineering acceptance.

## Disposition

```text
RLY-S25-IMPL-EVAL-002 — REWORK / NARROW
```

The first corrective pass materially closes I001–I004 and substantially improves I005. Two narrow residual defects remain.

No broad redesign is required or authorized.

## R2-I001 — independent-evaluation qualification acceptance is not admitted

**Severity:** BLOCKING

The accepted Slice 2.5 design allows a qualification to require independent or Human acceptance.

The implementation's qualification-acceptance verifier currently admits only:

```text
HUMAN_ACCEPTANCE
TECHNICAL_ACCEPTANCE
```

and rejects an exact accepted `INDEPENDENT_EVALUATION` record.

This incorrectly prevents a qualification whose governing contract requires independent acceptance from satisfying the current qualification requirement.

The dogfood helper currently creates a Human acceptance record for `acceptance_required=True`, so the required independent-acceptance path is not exercised.

### Required correction

Qualification acceptance verification must admit the exact independently accepted evaluation role where that record:

- is present in the exact pinned snapshot;
- matches the exact reference identity;
- is accepted/current for the requested scope;
- explicitly asserts acceptance of the exact qualification subject/digest.

An unrelated independent evaluation must not satisfy the qualification.

Add deterministic coverage proving both the valid exact-independent-acceptance case and the unrelated-independent-evaluation rejection case.

## R2-I002 — SUPERSEDED qualification successor lookup uses the prior target key

**Severity:** BLOCKING

The supersession repair correctly computes the replacement predecessor key:

```text
predecessor_key = superseding_key
```

but the qualification branch later resolves `ResolvedQualification` using the old `edge.target_key` instead of the computed `predecessor_key`.

For a valid relation:

```text
old qualification
    SUPERSEDED BY
new qualification
```

the resolver can therefore fail to find the accepted successor qualification and may raise `StopIteration` rather than deterministically resolving the successor.

### Required correction

Resolve a qualification successor using the computed successor/current predecessor key, not the obsolete target key.

Add deterministic coverage for:

- accepted/satisfied qualification successor;
- known unsatisfied qualification successor -> blocker;
- unresolved/missing qualification successor -> indeterminate.

The prior superseded subject must not become a generic prohibition.

## Findings closed from RLY-S25-IMPL-EVAL-001

The following first-review findings are considered substantively closed and must be preserved:

### I001 — typed normative content binding

Authority-bearing typed values are now bound to deterministic normative-content digests and altered typed payloads fail closed against accepted backing assertions.

### I002 — qualification evidence and acceptance lineage

Exact qualification evidence is checked against pinned source identity, scope, accepted status, expected evidence predicate, and exact evidence identity. Acceptance records are bound to the exact qualification digest rather than accepted merely because an unrelated acceptance record exists.

The residual R2-I001 is limited to the accepted role set, not a reopening of this architecture.

### I003 — SUPERSEDED semantics

`SUPERSEDED` is no longer treated as a generic prohibition. The residual R2-I002 is a narrow successor-qualification lookup defect.

### I004 — ProducedExpectation ingress

Direct unprovenanced caller ingress is removed. Produced expectations are derived from satisfied provenance-verified `PRODUCES` edges, and the derived-state model rejects forged expectations.

### I005 — frozen dogfood matrix

The corrective candidate now adds substantive end-to-end WellPlot, Tension/FEM, Seneca, and Relay resolver/compiler scenarios. The only remaining coverage needed is the two residual semantic paths named above.

## Preserved accepted implementation

The next correction must preserve:

- deterministic exact-content backing;
- exact pinned source/snapshot semantics;
- historical PASS separate from current applicability;
- fail-closed missing/conflicting provenance;
- responsibility-collision behavior;
- consumable-state behavior;
- Knowledge Delta proposal-only semantics;
- derived `ProducedExpectation` enforcement;
- `READY != AUTHORIZED`;
- pure resolver/compiler package boundary;
- no persistence, network, runtime, provider, model, Human-authority, or production-orchestration side effects.

## Authority consequence

```text
Candidate 18a4a6c4d8553c165d4a6888e09c87478be3474c:
REWORK REQUIRED / NOT ACCEPTED

Required next gate:
RLY-S25-IMPL-REWORK-AUTH-002

Corrective scope:
R2-I001 + R2-I002 ONLY

Human technical acceptance:
NOT AUTHORIZED

Slice 2.5 closure:
NOT AUTHORIZED

Production wiring:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

**The candidate is close to acceptable, but these two deterministic contract defects must be corrected before implementation acceptance.**
