# ADR-0012 — Human Decision Support Is Projection, Not Authority

**Status:** PROPOSED ARCHITECTURAL DECISION — NOT IMPLEMENTATION AUTHORITY  
**Date:** October 10, 2026  
**Authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001`

## Context

Relay must preserve its verifiable governance chain while making consequential decisions legible to the Human. A derived explanation can help a Human understand, question, inspect, compare, defer, and decide, but it cannot establish that the Human understood or create an authority decision. This distinction is informed by decision-support and agentic engineering practice [SRC-LITT-UNDERSTANDING-2026] [SRC-GOOGLE-NEW-SDLC-2026].

## Decision

1. Decision Support is a derived projection over canonical facts, evidence, verification judgments, authority decisions, and executed transitions. It is non-authoritative and creates none of those statements.
2. Human Authority remains an explicit governed command. Q&A, explanations, and clarity feedback cannot authorize, accept, reject, promote, open a Slice, or mutate lifecycle state.
3. Relay optimizes legibility without claiming to measure cognition. Optional clarity feedback is telemetry, not proof, acceptance, or authority; no mandatory quiz or comprehension threshold is introduced.
4. A Decision Card binds to one exact decision and generic governed subject. A Slice Card remains a work/lifecycle projection; a Slice may have multiple Decision Cards.
5. Decision Q&A is scoped to the exact Decision Basis, exposes source/provenance categories and `UNKNOWN`, and cannot alter governance records.

## Consequences

Future architecture may define `DecisionBasisProjection`, `DecisionClarityFeedback`, decision-scoped Q&A, and `RELAY_DECISION_BASIS_COMPLETE`. Those remain conceptual until separately authorized. No Human-understanding predicate is permitted. The source catalog provides provenance, not authority.

## Non-authority

This proposed ADR and the architecture/roadmap re-baseline do not open or authorize Slice 1.9 or 1.10, resume Slice 1.8, authorize Design Revision 2, or authorize implementation. Slice 1.8 Design Revision 1 remains preserved pre-rebaseline input, not reviewed, not Human-accepted, and not implementation authority.
