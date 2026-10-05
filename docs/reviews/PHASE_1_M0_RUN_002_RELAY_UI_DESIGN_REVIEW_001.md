# Phase 1 M0 — Run 002 Relay UI Design Review 001

**Document class:** Design-review record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-P1-M0-RUN-002-DESIGN-EVAL-001`  
**Outcome:** `ACCEPT`

## 1. Review basis

```text
Run:
RLY-P1-M0-RUN-002

Frozen Relay product baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Task-selection commit:
45221e6337699f4ae6592b928d76530ac1b10d63

Design authority:
RLY-P1-M0-RUN-002-DESIGN-AUTH-001
commit 6c29b3dadc07ba9e97e3e1121a676eab50320655

Design under review:
RLY-P1-M0-RUN-002-DESIGN-001
commit 65bda5393fe74ab5c5b1fda03be80b81bbc4fe30
```

This review assesses design correctness only. It does not grant Human design acceptance or implementation authority.

## 2. Review criteria

The design was reviewed for:

1. anti-circularity safety;
2. use of existing `SliceDetail` facts only;
3. preservation of READY vs authorization semantics;
4. preservation of gate-evaluation basis semantics;
5. absence/not-projected semantics;
6. separation of engineering result, evaluator decision, Human technical decision, and accepted-result promotion;
7. bounded implementation surface;
8. deterministic testability;
9. HTML escaping/accessibility;
10. dependency/toolchain neutrality.

## 3. Findings

### F001 — Anti-circularity boundary

**PASS.**

The design does not require mutation of governance, lifecycle, Human-control, manual-evaluation, persistence, repository-baseline, repository-contract, or repository-sync semantics.

The governance engine under M0 remains frozen.

### F002 — Existing projection sufficiency

**PASS.**

Current `SliceDetail` already carries the required facts through:

```text
lifecycle
outgoing_gates
human_actions
manual_evaluation
```

Existing Human evidence models expose exact durable authorization, approval, and choice identities and gate revisions. Existing manual-evaluation projection exposes current result, evaluation, technical decision, accepted result, and development memory.

No board model/service/web expansion is required by the accepted design.

### F003 — READY versus authority

**PASS.**

The design explicitly requires the summary to state that READY is a lifecycle phase and does not grant execution authorization.

It further preserves the distinction among unblocked, READY, authorization grants, and approval decisions.

### F004 — Gate traffic-light truth

**PASS.**

The design permits a current traffic light only for `MATCHING_DURABLE_BASIS` and explicitly suppresses historical lights from being presented as current on stale basis.

`NOT_EVALUATED` and `NOT_APPLICABLE` remain distinct.

No synthetic global traffic light is introduced.

### F005 — Absence semantics

**PASS.**

The design uses “none projected” for absent current authorization grants rather than manufacturing a canonical negative decision such as `NOT AUTHORIZED`.

This is important because absence of a projected grant is evidence absence, not a new persisted governance event.

### F006 — Manual evaluation causal distinctions

**PASS.**

The design separately renders:

```text
current result
current evaluator decision
current Human technical decision
accepted-result promotion
```

and explicitly forbids collapsing them into one acceptance badge.

Exact result and accepted commit provenance remain separately visible when available.

### F007 — Development memory

**PASS.**

The design exposes only a compact derived indication and counts from the existing development-memory projection. It does not create a new materialized memory or persistence surface.

### F008 — Change surface

**PASS.**

Expected production change is limited to:

```text
src/relay_engine/board/render.py
```

with focused tests in:

```text
tests/unit/test_board_render.py
```

The design correctly treats model/service/web changes as stop conditions rather than assumed scope.

### F009 — Deterministic evaluation contract

**PASS.**

V002-01 through V002-14 are sufficient to evaluate placement, lifecycle semantics, traffic-light basis handling, Human evidence, result/evaluation distinctions, exact SHA provenance, memory visibility, escaping, preservation of detailed sections, change surface, and repository quality gates.

### F010 — Presentation safety and accessibility

**PASS.**

The design preserves the repository's existing `_e(...)` HTML escaping boundary and requires semantic headings/lists and textual traffic-light meaning.

No JavaScript, framework, external asset, or dependency is required.

## 4. Blocking findings

```text
NONE
```

## 5. Non-blocking implementation guidance

1. Prefer small private rendering helpers in `board/render.py` rather than one large string-construction function.
2. Keep exact durable IDs in `<code>` elements where the existing renderer uses that convention.
3. Preserve current lower sections byte-semantically where practical; the new summary should duplicate selected facts for scanability, not refactor existing provenance during the M0 experiment.
4. Test “none projected” wording explicitly so future cleanup does not accidentally turn absence into inferred denial.
5. Keep current traffic-light text visible even if color styling is used.

These are implementation-quality notes, not scope expansions.

## 6. Review conclusion

The design is bounded, implementable from existing projection data, deterministic to test, and does not alter the governance engine being validated.

```text
RLY-P1-M0-RUN-002-DESIGN-EVAL-001 — ACCEPT
```

## 7. Governance state after review

```text
Phase 1 M0: AUTHORIZED / IN PROGRESS
Run 002: OPEN
Target: Relay
Frozen product baseline: d14fa79fd13f8f70745d8ed47feafdf2d4892a19
Design authority: AUTHORIZED
Design: COMPLETE
Design review: ACCEPT
Human design acceptance: NOT YET GRANTED
Implementation: NOT AUTHORIZED
Phase 2: NOT OPEN
Relay agent execution: NOT AUTHORIZED
```

The next legitimate gate is explicit Human design acceptance.
