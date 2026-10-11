# Relay — Slice 1.9 Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Record:** `RLY-S19-OPEN-001`  
**Decision:** `OPEN`

## 1. Human Authority

The Human explicitly instructed:

> lets open Slice 1.9, you are authorized to enter the design phase

This record captures the Slice-opening event. Design authorization is a distinct Human Authority event recorded separately.

## 2. Exact opening basis

```text
Repository:
cschrupp/relay

Canonical main at opening:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

Slice 1.8:
COMPLETE / ACCEPTED / CLOSED

Slice 1.8 closure evaluation:
RLY-S18-CLOSE-EVAL-001 — ACCEPT

Slice:
1.9 — Human Decision Support and Governance Review Surface
```

## 3. Roadmap objective

Slice 1.9 consumes the closed Slice 1.8 Governance Assurance Reference Model and makes exact pending Human decisions legible and inspectable without changing Relay authority semantics.

The accepted ownership boundary remains:

```text
Slice 1.8:
assurance semantics and verified-property definitions

Slice 1.9:
Decision Cards, exact decision-basis projection,
profile/risk/asset explanation,
decision-scoped Q&A,
clarity feedback direction,
governance-effectiveness presentation

Slice 1.10:
canonical source / promotion enforcement
```

## 4. Opening state

```text
Slice 1.9:
OPEN

Design:
AUTHORIZED BY SEPARATE RLY-S19-DESIGN-AUTH-001 RECORD

Implementation:
NOT AUTHORIZED

Schema/dependency changes:
NOT AUTHORIZED

Provider/model execution:
NOT AUTHORIZED

Autonomous agent execution:
NOT AUTHORIZED

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

## 5. Preserved invariants

- Decision Support is derived and non-authoritative.
- Decision Support is not evidence, evaluation, Human Authority, or an executed transition.
- Evidence remains distinct from evaluation.
- Evaluation remains distinct from Human acceptance.
- Human acceptance remains distinct from promotion.
- A Human-facing explanation cannot manufacture authority, facts, policy, evidence, or evaluator judgment.
- Unknown or stale required basis must remain visible and fail closed where the underlying authority action requires a current basis.
- Slice 1.9 consumes Slice 1.8 assurance semantics and does not redefine the accepted 17-property vocabulary.
- Slice 1.10 retains ownership of canonical-source and promotion enforcement.
- Slice 2.2 retains ownership of role/identity contracts; Slice 2.3 of context/work packets; Slice 2.4 of workspace authority.
- Phase 3 and real-project execution remain unauthorized.

## 6. Existing proposal status

`docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE.md` and
`docs/architecture/HUMAN_DECISION_SUPPORT.md` are design inputs.

Opening this Slice does not convert either document into an accepted implementation contract. Detailed architecture, exact models, freshness semantics, Q&A boundaries, UI behavior, persistence decisions, and implementation surface remain subject to authorized design and independent design review.

## 7. Authority boundary

```text
Slice open != design accepted
Design authorized != implementation authorized
Decision Support != Human Authority
Readable != authorized
Green checks != Human acceptance
```

No production implementation is authorized by this opening record.
