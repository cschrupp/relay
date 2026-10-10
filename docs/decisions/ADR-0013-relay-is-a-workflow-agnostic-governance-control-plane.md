# ADR-0013 — Relay Is a Workflow-Agnostic Governance Control Plane

**Status:** PROPOSED ARCHITECTURAL DECISION — NOT ACCEPTED / NOT IMPLEMENTATION AUTHORITY
**Date:** October 10, 2026
**Authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001`

## Context

AI engineering systems already produce specifications, plans, task lists, code, and review artifacts through multiple methods. Spec Kit, OpenSpec, and BMAD document different planning and delivery workflows; their existence is evidence of a varied landscape, not evidence that one workflow is best or that Relay has a competitive advantage [SRC-GITHUB-SPEC-KIT-2026] [SRC-OPENSPEC-2026] [SRC-BMAD-METHOD-2026]. Relay's product boundary should remain useful when upstream engineering intent comes from Relay-native planning, an external method, an enterprise process, or a custom system.

## Proposed decision

1. Relay does not require a specific upstream SDLC or planning methodology.
2. Relay-native planning may exist and is one supported source, not a prerequisite.
3. External planning artifacts may eventually enter through explicit, versioned adapters that preserve source provenance and normalize intent.
4. External artifacts do not import authority. `approved`, `ready`, `accepted`, `done`, or `green` in a source workflow does not itself authorize, evaluate, accept, or transition Relay work.
5. Relay owns normalized authority, policy, exact subject and baseline, execution, evidence, evaluation, Human decisions, promotion eligibility, and canonical transition.
6. Specification generation, task decomposition, generic multi-agent role prompting, and basic workflow orchestration are not claimed as unique Relay differentiators.
7. Interoperability is preferable to rebuilding mature external planning methodology purely for product completeness.

## Consequences

Future Slice 2.3 design may define `PlanningArtifactSourceRef`, `PlanningArtifactAdapter`, and a normalized engineering-intent boundary. A normalized artifact is not an authorized Work Packet; Relay must bind the exact normalized input through its own authority and policy. Incomplete required normalization remains `UNKNOWN` or `MISSING_REQUIRED` and cannot produce an authorized packet.

Relay's strategic distinction is an architectural thesis to validate, not a proven comparative advantage. A non-authoritative controlled research plan is recorded in `docs/references/RELAY_COMPETITIVE_VALIDATION_PLAN.md`. No experiment is authorized or executed by this ADR.

## Non-authority

This ADR is proposed architecture under the strategic amendment authority. It is not accepted, does not create implementation authority, does not open a Slice, and does not authorize adapter implementation, workflow changes, Slice 1.8 resumption, Design Revision 2, or Phase 3.
