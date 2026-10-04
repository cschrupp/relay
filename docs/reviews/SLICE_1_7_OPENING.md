# Slice 1.7 — Human Opening

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Authority ID:** `RLY-S17-OPEN-001`

## Human Authority decision

The Human Authority explicitly opens Slice 1.7:

```text
Slice 1.7 — Manual Evaluation and Acceptance
OPEN
```

The opening follows accepted and independently closed Slice 1.6.

Exact canonical repository head at opening:

```text
7013a0556c50e9c6942c65da37aa413375ca0549
```

Canonical Slice 1.6 closure commit recorded by the living baseline:

```text
9db044036e3591c53d777c81af58af252ebc69a7
```

Independent Slice 1.6 closure evaluation:

```text
RLY-S16-CLOSE-EVAL-001 — ACCEPT
```

Accepted Slice 1.6 technical candidate:

```text
a62493c733f67a5ce1b2fe5c53892d1833e4c615
```

Post-closure documentation synchronization baseline:

```text
7013a0556c50e9c6942c65da37aa413375ca0549
```

## Roadmap scope inherited by Slice 1.7

The canonical roadmap defines Slice 1.7 as:

> Manual Evaluation and Acceptance

Objective:

> Complete the human-only development loop.

The roadmap flow is:

```text
authorized
    ↓
external/manual implementation
    ↓
resulting commit
    ↓
manual evaluation
    ↓
accepted baseline
```

Roadmap exit expectations are:

```text
resulting SHA attached
evidence attached
evaluator decision represented
REWORK path supported
ACCEPT creates new accepted baseline
development memory generated or updated
```

## Scope boundary

This record opens Slice 1.7 administratively only.

It does **not** authorize:

- architecture, contract, or detailed design work;
- production implementation;
- schema migration or dependency changes;
- new lifecycle or governance semantics;
- automatic evaluation;
- automatic technical acceptance;
- autonomous accepted-baseline promotion;
- agent execution;
- AgentRuntime or OpenCode implementation;
- opening Phase 2;
- bypassing the Phase 1 M0 validation hard stop.

A separate Human Authority decision is required before Slice 1.7 design begins.

## Preserved boundary from Slice 1.6

Slice 1.6 remains complete, accepted, and closed. Its Human Authority command seam remains the accepted mechanism for authorization, approval/rejection, choice, holds, governed advancement, and governed cancellation.

Opening Slice 1.7 does not reinterpret those decisions as evaluation or technical acceptance. Slice 1.7 must preserve the distinction:

```text
engineering evidence
    !=
evaluator decision
    !=
Human technical acceptance
    !=
accepted-baseline promotion
```

Passing deterministic checks remains evidence, not acceptance.

## Hard stop

```text
Slices 1.1–1.6:
COMPLETE / ACCEPTED / CLOSED

Slice 1.7:
OPEN — ADMINISTRATIVE ONLY

Slice 1.7 design:
NOT AUTHORIZED

Slice 1.7 implementation:
NOT AUTHORIZED

Phase 1 M0 validation:
NOT YET COMPLETED

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
