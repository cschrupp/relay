# Phase 1 M0 — Run 002 Relay UI Design Acceptance

**Document class:** Immutable Human design-acceptance record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-P1-M0-RUN-002-DESIGN-ACCEPT-001`  
**Outcome:** `ACCEPTED`

## 1. Human decision

Human Authority explicitly accepted the bounded Relay M0 Run 002 design with the instruction:

```text
Accept Relay M0 Run 002 Governance Status Summary design
```

This record represents Human design acceptance only.

It does not itself authorize implementation, technical acceptance of any future candidate, M0 completion, Phase 1 completion, Phase 2, or Relay agent execution.

## 2. Accepted design basis

```text
Phase 1 M0 authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

M0 run:
RLY-P1-M0-RUN-002 — OPEN

Selected target:
Relay

Repository:
cschrupp/relay

Frozen product baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Selected task:
Relay Slice Detail — Governance Status Summary

Design authority:
RLY-P1-M0-RUN-002-DESIGN-AUTH-001 — AUTHORIZED
6c29b3dadc07ba9e97e3e1121a676eab50320655

Accepted design:
RLY-P1-M0-RUN-002-DESIGN-001 — COMPLETE
65bda5393fe74ab5c5b1fda03be80b81bbc4fe30

Independent design evaluation:
RLY-P1-M0-RUN-002-DESIGN-EVAL-001 — ACCEPT
75ec3d36d8e15d4d1050c0c2e73b6e4fc62e2a2c
```

The accepted design is bound to the exact frozen Relay product baseline above. Later movement of `main` does not silently alter this design basis.

## 3. Accepted architecture and boundary

The accepted solution is a compact, read-only `Governance status` summary near the top of the existing Slice detail page.

The summary must remain a pure presentation projection of facts already present in `SliceDetail`.

Expected production change surface:

```text
src/relay_engine/board/render.py
```

Expected test surface:

```text
tests/unit/test_board_render.py
```

Changes to board models, board service, board web routes, persistence, governance, lifecycle, Human-control, manual-evaluation, repository-baseline, repository-contract, repository-sync, or database schema are not part of the accepted design.

If implementation discovers that such a change is necessary, it must stop and return for renewed design authority rather than widening scope implicitly.

## 4. Accepted presentation semantics

The summary must preserve the following distinctions without inventing aggregate governance truth:

```text
READY != AUTHORIZED

unblocked
!= READY
!= authorization grant
!= approval decision

engineering result
!= evaluator decision
!= Human technical decision
!= accepted-result promotion
```

For current outgoing gates:

- each gate remains independently represented;
- current traffic light is shown only when a matching durable evaluation exists;
- stale, not-evaluated, and not-applicable states remain explicit;
- no synthetic overall traffic light is introduced.

For Human evidence:

- current authorization grants, approval decisions, and choice decisions may be summarized only from durable projected facts;
- missing authority must not be inferred.

For manual evaluation / result state:

- current result, exact result commit when projected, evaluator outcome, Human technical decision, accepted result, and exact accepted commit remain distinct facts;
- development-memory availability may be summarized without introducing a new memory store.

## 5. Anti-circularity constraint remains in force

Relay is governing a presentation-only change to Relay itself.

The governance engine under M0 validation remains frozen for Run 002.

The future implementation is not authorized to change:

```text
src/relay_engine/governance/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/persistence/**
src/relay_engine/repository_baseline/**
src/relay_engine/repository_contract/**
src/relay_engine/repository_sync/**
```

Nor may it change gate semantics, authorization semantics, Human-action availability, manual-evaluation semantics, accepted-result promotion, lifecycle transitions, schema/migrations, Phase 2 capability, or agent execution/orchestration.

## 6. Authority boundary after this decision

```text
Phase 1 M0: AUTHORIZED / IN PROGRESS
Run 002: OPEN
Run 002 target: Relay — SELECTED
Run 002 task: Governance Status Summary — SELECTED
Frozen product baseline: d14fa79fd13f8f70745d8ed47feafdf2d4892a19
Design: COMPLETE
Independent design review: ACCEPT
Human design acceptance: ACCEPTED
Implementation: NOT AUTHORIZED
M0 technical evaluation: PENDING
M0 completion: NOT ACCEPTED
Phase 1 completion: NOT ACCEPTED
Phase 2: NOT OPEN
Relay agent execution: NOT AUTHORIZED
```

## 7. Next legitimate gate

The next legitimate Human Authority action is separate implementation authorization bound to this exact accepted design and frozen product baseline.

Suggested wording:

```text
Authorize Relay M0 Run 002 Governance Status Summary implementation
```

That future authorization should permit an external/manual implementation candidate only. It must not automatically grant evaluation, Human technical acceptance, accepted-result promotion, M0 completion, Phase 1 completion, Phase 2, or Relay agent execution.
