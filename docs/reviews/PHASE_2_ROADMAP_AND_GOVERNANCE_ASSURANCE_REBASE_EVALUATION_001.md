# Relay Roadmap and Governance-Assurance Redesign — Independent Evaluation 001

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE  
**Project:** Relay  
**Evaluation ID:** `RLY-P2-ROADMAP-REBASE-EVAL-001`  
**Outcome:** `REWORK`  
**Date:** 2026-10-09

## Subject

```text
Canonical basis:
ad0444337efcddb5694d14a57a99c22d18cdfb9c

Roadmap authority:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Evaluated branch:
governance/phase2-roadmap-assurance-rebaseline

Evaluated candidate:
8ad0a147e4902b041b5544bf2f0dfeae65f275e3

Exact-head CI:
38010596114 — SUCCESS
```

## Decision

```text
REWORK
```

The redesign is accepted in overall roadmap topology and phase placement, but requires bounded documentation correction before promotion.

## Passing findings

- documentation-only scope preserved;
- no production source/runtime/test/dependency change;
- accepted Slice 2.1 implementation unchanged;
- candidate is directly ahead of canonical main with no divergence;
- no prior immutable or locked registry record was modified or removed;
- living projection lineage is valid when branch ancestry is preserved;
- exact-head CI passed;
- Phase 1.8 / 1.9 placement accepted;
- Phase 2.2 / 2.3 / 2.4 decomposition accepted;
- Phase 3.3 -> Phase 3.1 coding-agent-execution renumbering accepted;
- Relay remains authoritative over its semantics; external standards remain assurance/compliance references.

## F001 — Evaluation must remain distinct from evidence

The new assurance reference model correctly states `Evidence PASS != Evaluation ACCEPT` but later groups formal evaluation with evidence.

Required correction:

```text
execution observations / CI / provenance / artifacts
        -> evidence

evidence
        -> independent evaluation / verification judgment

evaluation judgment
        -> possible prerequisite for later Human or already-authorized transition
```

Neither evidence nor evaluation may manufacture Human Authority.

The architecture diagram should place formal Relay evaluation in the Verification Plane rather than the Evidence Plane.

## F002 — SLSA wording must remain conservative

The statement that SLSA tests "promotion controls" is too broad because promotion is a Relay lifecycle concept.

Required correction:

```text
SLSA evaluates applicable source/build assurance,
provenance, and verification properties.

Relay maps applicable SLSA controls/evidence into
its own promotion eligibility and policy.
```

External standards must not be described as defining Relay promotion semantics.

## F003 — Promotion authority is semantic, not necessarily a new manual ceremony

The lifecycle separation of acceptance from promotion is correct, but `PROMOTION AUTHORIZATION` must not imply that every promotion requires a new Human click after technical acceptance.

Required correction:

```text
No valid promotion authority:
promotion forbidden.

Valid existing promotion authority + predicates satisfied:
mechanical promotion may proceed without another Human decision.
```

Promotion authority may be a dedicated exact authorization or an earlier exact finalization/closure authority that explicitly makes promotion conditional on stated verification predicates.

The promotion executor remains mechanical and cannot create authority.

## F004 — Planned Slice hard stops must preserve Relay's gate grammar

Future Slice proposals must state explicitly:

```text
PLANNED != OPEN
OPEN != DESIGN AUTHORIZED
DESIGN ACCEPTED != IMPLEMENTATION AUTHORIZED
IMPLEMENTED != ACCEPTED
ACCEPTED != PROMOTED
```

For Slice 1.8 and Slice 1.9:

- opening requires separate Human Authority;
- opening does not authorize design;
- design requires explicit authorization;
- design acceptance does not authorize implementation;
- implementation requires separate explicit authorization.

For Slice 1.9, opening or design authorization also does not authorize mutation of GitHub branch protection, rulesets, repository settings, or promotion mechanisms.

## Corrective boundary

The corrective pass is documentation-only.

Minimum correction surface:

```text
docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
docs/slices/SLICE_1_9_CANONICAL_SOURCE_PROMOTION_ENFORCEMENT.md
```

No new Human Authority is required.

No source/runtime/test/dependency change, repository-setting mutation, new live runtime evidence, Slice opening, Phase 3 opening, or real-project execution is authorized.

## Promotion lineage constraint

The existing branch lineage must be preserved so Product Proposal revisions remain:

```text
38 -> 39 -> 40
```

A squash or history rewrite that presents canonical main with a direct `38 -> 40` living-projection transition is invalid.

## Disposition

```text
RLY-P2-ROADMAP-REBASE-EVAL-001 — REWORK

Roadmap topology:
ACCEPTED

Architecture semantics:
BOUNDED REWORK REQUIRED

Promotion to main:
NOT YET ACCEPTED

New Human Authority:
NOT REQUIRED
```
