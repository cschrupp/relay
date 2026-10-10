# Relay — Slice 1.8 Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-10  
**Record:** RLY-S18-OPEN-001  
**Decision:** OPEN

## 1. Human authority

The Human explicitly instructed:

> lets open Slice 1.8 — Governance Assurance Reference Model

This instruction opens Slice 1.8 only.

## 2. Exact opening basis

~~~text
Repository:
cschrupp/relay

Canonical main at opening:
be382eb8e31b51ef6ff0879c3b460a9f4a001a18

Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Roadmap re-baseline:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Roadmap redesign evaluation:
RLY-P2-ROADMAP-REBASE-EVAL-002 — ACCEPT

Roadmap redesign Human acceptance:
RLY-P2-ROADMAP-REBASE-ACCEPT-001 — ACCEPTED

Slice:
1.8 — Governance Assurance Reference Model
~~~

## 3. Authorized state

~~~text
Slice 1.8:
OPEN — ADMINISTRATIVE ONLY

Design:
NOT AUTHORIZED

Implementation:
NOT AUTHORIZED

GitHub branch protection / ruleset mutation:
NOT AUTHORIZED

Promotion-mechanism implementation:
NOT AUTHORIZED

Typed attestation implementation:
NOT AUTHORIZED

External compliance-level claims:
NOT AUTHORIZED BY THIS RECORD

Agent execution:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED
~~~

Opening permits governed inspection of the accepted roadmap/reference-model proposal, design preparation, and preparation for the next explicit Human gate.

## 4. Existing proposal status

docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md exists as the roadmap proposal for this Slice.

Opening the Slice does not make that proposal an accepted design.

Its architecture, verified-property vocabulary, attestation direction, trust terminology, compliance-claim rules, standards mapping, and DORA-style overhead guardrails remain subject to separately authorized design work and Sol review.

## 5. Preserved invariants

- Relay remains the authoritative engineering-governance model.
- External standards remain assurance/compliance references and do not define Relay semantics.
- Evidence remains distinct from evaluation.
- Evaluation remains distinct from Human acceptance.
- Human acceptance remains distinct from promotion.
- Promotion authority may be dedicated or pre-issued/conditional, but execution cannot manufacture authority.
- The established role model remains: Sol architects/designs/reviews; Luna/Codex implements production implementation work; Human Authority is root authority.
- Slice 1.9 remains unopened and unauthorized.
- Phase 3 and real-project agent execution remain unauthorized.

## 6. Scope boundary

This record opens Slice 1.8 administratively only.

It does not authorize:

- detailed Slice 1.8 design;
- design acceptance;
- implementation;
- source/runtime/test/dependency/schema changes;
- GitHub repository-setting changes;
- canonical-reference enforcement changes;
- promotion-executor implementation;
- attestation subsystem implementation;
- Role Contract implementation;
- work-packet or workspace implementation;
- autonomous agent execution;
- SLSA level or equivalent external compliance claims.

## 7. Next authority boundary

The next legitimate Human gate is Slice 1.8 design authorization.

~~~text
Slice open != design authorized
Design complete != design accepted
Design accepted != implementation authorized
Implemented != accepted
Accepted != promoted
Unblocked != authorized
~~~

## 8. Hard stop

~~~text
Slice 1.8:
OPEN — ADMINISTRATIVE ONLY

Slice 1.8 design:
NOT AUTHORIZED

Slice 1.8 implementation:
NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slices 2.2–2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~
