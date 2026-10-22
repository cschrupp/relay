# Slice 1.10 Dogfood B4 Revision 2 — Design Rework Authorization

**Document class:** Immutable Human design authority
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001`
**Decision:** `AUTHORIZED`

## Human decision

The Human authorizes a bounded B4 Revision 2 design rework following
`RLY-S110-DOGFOOD-B4-EXEC-EVAL-005 — FAIL — PROTOCOL/DESIGN AMBIGUITY ESTABLISHED`.

## Authorized design scope

Revision 2 may design only:

1. alignment of the visible B4 operator questions with the evaluator answer boundaries, specifically the defects exposed around Q6, Q8, and Q10;
2. a deterministic execution/evidence wrapper above the accepted read-only B4 harness;
3. deterministic evidence schemas, sealing, validation, invocation-count, and before/after state checks needed by that wrapper;
4. focused tests and implementation acceptance criteria for a later separately authorized implementation.

## Required invariants

- Keep `scripts/b4_readonly_harness.py` semantics unchanged unless Revision 2 proves a blocker.
- Do not change `project_board`, `slice_detail`, lifecycle, Human-control, or persistence semantics.
- Do not encode expected factual answers into the operator prompt or runner.
- Keep semantic interpretation with the fresh operator and correctness judgment with the independent evaluator.
- Move deterministic protocol correctness out of prompt compliance wherever code can enforce it.
- Preserve cold-start custody and source precedence.
- Preserve the live operational DB read-only boundary.
- No B4 execution is authorized by this design authority.
- No Slice 2.2 design or implementation is authorized.

## Explicitly out of scope

- implementation of the Revision 2 runner;
- changes to the operational DB;
- lifecycle or Slice mutation;
- Role Contracts / Slice 2.2 work;
- Axis B onboarding replay;
- Phase 3 work;
- promotion;
- B4 attempt 006.

## Starting point

```text
Parent:
0d74d594486c7b5471feed4a15d5a1cad70840c9

Branch:
design/1.10-dogfood-b4-rev2-protocol-runner

Finding basis:
RLY-S110-DOGFOOD-B4-EXEC-EVAL-005
```

## Authority status

```text
RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001 — AUTHORIZED

B4 Revision 2 design:
OPEN

B4 Revision 2 implementation:
NOT AUTHORIZED

B4 attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```
