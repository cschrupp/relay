# Phase 1 M0 — Run 002 Relay UI Design Authorization

**Document class:** Immutable Human design-authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-P1-M0-RUN-002-DESIGN-AUTH-001`  
**Outcome:** `AUTHORIZED`

## 1. Human authority

The Human Authority explicitly authorized:

```text
Authorize Relay M0 Run 002 Governance Status Summary design
```

This authority permits **design work only** for the bounded Run 002 task. It does not authorize implementation, result attachment, evaluation, technical acceptance, accepted-result promotion, Phase 1 completion, Phase 2, or Relay agent execution.

## 2. Exact basis

```text
Phase 1 M0 authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

Run:
RLY-P1-M0-RUN-002 — OPENED / TARGET AND TASK SELECTED

Run/task-selection commit:
45221e6337699f4ae6592b928d76530ac1b10d63

Target repository:
cschrupp/relay

Exact frozen product baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Task:
Relay Slice Detail — Governance Status Summary
```

The design basis does not move with later `main` changes.

## 3. Authorized design scope

Design a compact, read-only **Governance status** summary near the top of the existing Slice detail page, derived exclusively from facts already available in the current `SliceDetail` projection.

The design may specify:

- information hierarchy and wording;
- deterministic projection/rendering rules;
- traffic-light presentation using existing gate truth;
- Human authorization/decision evidence presentation;
- result/evaluation/technical-decision/accepted-result distinctions;
- development-memory discoverability;
- accessibility and HTML-escaping requirements;
- bounded rendering tests;
- exact expected presentation-only change surface.

## 4. Frozen anti-circularity boundary

Design must not require changes to:

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

Nor may it redesign:

```text
gate semantics
authorization semantics
Human-action availability
manual-evaluation semantics
accepted-result promotion
lifecycle transitions
database schema/migrations
Phase 2 capability
agent execution/orchestration
```

The governance engine being validated remains frozen.

## 5. Expected design surface

Preferred implementation surface to be evaluated during design:

```text
src/relay_engine/board/render.py
tests/unit/test_board_render.py
```

Changes to `board/models.py`, `board/service.py`, or `board/web.py` are not presumed authorized. If the design cannot be satisfied from the existing `SliceDetail` projection, the design must stop and surface that as a finding rather than silently expanding scope.

## 6. Required design invariants

The design must preserve at least:

```text
READY != AUTHORIZED
unblocked != READY != AUTHORIZED != APPROVED
engineering evidence != evaluator decision
!= Human technical acceptance != accepted-result promotion
```

It must not synthesize a new global traffic light or aggregate governance state unless that state already exists canonically.

Absence of projected evidence must be described as absence/not projected, not inferred as a new negative governance decision.

## 7. Next gates

Authorized sequence:

```text
design
-> separate design review
-> Human design acceptance
```

Implementation remains explicitly unauthorized until a later Human Authority event.
