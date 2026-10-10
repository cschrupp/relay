# Strategic Amendment to the Phase 1 Assurance and Decision Support Re-baseline

**Record:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001`  
**Status:** IMMUTABLE  
**Decision:** AUTHORIZED  
**Date:** October 10, 2026

## Exact authority basis

```text
Parent re-baseline authority:
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001 — AUTHORIZED

Exact amendment baseline:
dbe77d6f97f8e660bccb74971bcfd7fbd2d95764

Canonical main:
986b67f00958ef348fbf69ff677af630009881a7

Slice 1.8:
OPEN / DESIGN AUTHORIZED / PAUSED — RLY-S18-PAUSE-001

Implementation:
NOT AUTHORIZED
```

## Decision

The Human authorizes a bounded strategic amendment to the existing documentation and architecture re-baseline. It incorporates workflow interoperability, risk-adaptive governance, protected verification assets, governance-effectiveness measurement, and a non-authoritative competitive-validation research plan. It does not restart the re-baseline or resume Slice 1.8.

## Authorized work

This authority covers documentation, architecture, roadmap clarification, product positioning, external-source catalog updates, future-slice scope adjustments, non-authoritative research/validation planning, and the corresponding living projection updates. It permits conceptual design vocabulary only; it does not freeze implementation schemas or interfaces.

## Explicit exclusions

This authority does not authorize production source code, runtime code, tests, dependencies, schema changes, UI or planning-adapter implementation, `GovernanceProfile` implementation, workspace enforcement, verification-asset enforcement, telemetry implementation, competitive benchmark execution, agent execution, GitHub settings, branch protection, a promotion executor, Slice 1.8 resumption, Slice 1.8 Design Revision 2, Human design acceptance, opening Slice 1.9 or Slice 1.10, or opening Phase 3.

## Required boundaries

Relay remains the governance control plane. Relay-native planning is supported but not required; future external planning adapters may normalize source artifacts, but external workflow authority is never imported automatically. A normalized artifact is not an authorized Work Packet.

Governance profiles are selected by Relay policy or explicit Human Authority. An implementer, runtime, agent assertion, or workflow-provider metadata cannot weaken the applicable governance. Unknown required risk inputs fail closed or escalate under policy. Governance-effectiveness telemetry is non-authoritative and cannot automatically relax current controls.

Protected Verification Assets are designated according to policy; this does not mean every implementation test must be immutable or hidden. Their defining concern is mutation authority. The competitive-validation experiment is a future research plan only and must not be executed under this authority.

## Continuing state

```text
Slice 1.8:
OPEN / DESIGN AUTHORIZED / PAUSED

Design Revision 1:
PRESERVED / PRE-REBASELINE INPUT / NOT REVIEWED /
NOT HUMAN-ACCEPTED / NOT IMPLEMENTATION AUTHORITY

Design Revision 2:
NOT PRODUCED

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 1.10:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

No evaluator record is created by this authority. Sol retains independent evaluation responsibility.
