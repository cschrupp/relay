# Phase 1 Assurance / Decision Support Re-baseline — Human Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Project:** Relay  
**Record:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-ACCEPT-001`  
**Decision:** `ACCEPTED`  
**Date:** 2026-10-10

## Accepted subject

```text
Complete amended re-baseline candidate:
2910736334241d93a248cc348d20c516e3ea8cc1

Canonical main basis:
986b67f00958ef348fbf69ff677af630009881a7

Parent re-baseline authority:
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001 — AUTHORIZED

Strategic amendment authority:
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001 — AUTHORIZED

Independent evaluation:
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-EVAL-001 — ACCEPT

Evaluation recording commit:
ef19cef843d5ee0d18699032f6e4be7de29d90a4

Candidate exact-head CI:
38089609498 — SUCCESS
```

## Human decision

The Human accepts the complete amended Phase 1 assurance / decision-support re-baseline at exact candidate `2910736334241d93a248cc348d20c516e3ea8cc1`.

This acceptance includes the current roadmap and architecture direction for:

- Relay as the workflow-agnostic governance control plane for AI software engineering;
- Human Decision Support as a non-authoritative projection around policy-required decisions;
- risk-adaptive governance through future `GovernanceProfile` semantics;
- proposed `RELAY_GOVERNANCE_PROFILE_BOUND`;
- policy-designated Protected Verification Assets;
- proposed `RELAY_VERIFICATION_ASSETS_PROTECTED`;
- non-authoritative governance-effectiveness telemetry;
- future external planning/workflow adapters feeding normalized intent without importing authority;
- the future competitive-validation plan as research only, not an established superiority claim;
- the roadmap sequence 1.8, 1.9, 1.10, 2.2, 2.3, 2.4 before any governed Phase 3 autonomous engineering loop.

## Accepted product boundary

```text
Agents perform engineering; Relay governs engineering.

Relay-native planning:
SUPPORTED BUT NOT REQUIRED

External workflow artifacts:
MAY BECOME NORMALIZED INPUTS
DO NOT IMPORT RELAY AUTHORITY

Governance differentiation:
ARCHITECTURAL THESIS / TO BE EMPIRICALLY VALIDATED
```

## Authority boundary

This Human acceptance does not itself authorize canonical promotion.

It also does not resume Slice 1.8 or authorize Design Revision 2.

```text
Canonical promotion:
NOT AUTHORIZED BY THIS ACCEPTANCE ALONE

Slice 1.8:
OPEN / DESIGN AUTHORIZED / PAUSED

Slice 1.8 Design Revision 1:
PRESERVED / PRE-REBASELINE INPUT / NOT REVIEWED /
NOT HUMAN-ACCEPTED / NOT IMPLEMENTATION AUTHORITY

Slice 1.8 Design Revision 2:
NOT PRODUCED

Slice 1.8 implementation:
NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 1.10:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

A separate exact promotion authority is required before `main` may move.

Any later promotion must preserve the full ancestry of the accepted branch and fail closed if canonical `main` has moved from the promotion authority's exact expected SHA.

## Non-authority

This record authorizes no production source/runtime/test/dependency/schema change, no repository-setting mutation, no branch-protection or ruleset mutation, no competitive experiment execution, no Slice opening, no agent execution, and no promotion operation.
