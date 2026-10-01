# Slice 1.5 — Design Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-01  
**Project:** Relay  
**Slice:** 1.5  
**Authority ID:** `RLY-S15-DESIGN-AUTH-001`

## Human Authority decision

The Human Authority explicitly authorizes Slice 1.5 architecture, contract, and detailed design work.

```text
Slice 1.5 — Board Projection
DESIGN AUTHORIZED
```

Human-authorized design subject baseline:

```text
359cd61f0c05815390a6822739c0c68d3f020c32
```

Opening authority:

```text
RLY-S15-OPEN-001
```

Canonical roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

## Authorized design role

```text
Slice 1.5 Board Projection Architect — GPT-5.6 Sol
```

The role is intentionally architecture-led rather than UI-led. The primary design risk is not visual styling; it is preserving Relay's authority model while projecting governed state into a useful human-facing board.

## Authorized design scope

The architect may define:

- the read-only board projection contract and view model;
- which accepted Project, Slice, lifecycle, gate, handover, evaluation, baseline, and authority facts are projected;
- deterministic board columns, labels, badges, traffic lights, and derived display states;
- project/slice hierarchy, dependency, and blocking visibility;
- projection freshness, refresh, loading, empty, stale, unavailable, and integrity-error behavior;
- deterministic ordering and filtering;
- navigation/drill-down boundaries;
- the application/service boundary used to read governed state;
- the minimum UI/application architecture required for the first human-facing board;
- technology choices necessary to specify the implementation contract;
- accessibility and testability requirements;
- explicit acceptance criteria and evidence expected from implementation.

## Mandatory architectural constraints

1. The board is a **projection**, never a source of truth.
2. Board state must be deterministically derived from already-governed durable state.
3. No drag/drop, button, endpoint, or UI interaction may mutate Project, Slice, lifecycle, gate, authorization, evaluation, baseline, repository, or agent state in Slice 1.5.
4. The board must not invent authority semantics, lifecycle transitions, or new domain truth.
5. Missing, contradictory, stale, or corrupt source state must fail closed and be visible rather than silently repaired or guessed.
6. Deterministic derivation belongs in testable projection/application code, not hidden presentation conditionals.
7. The design should reuse accepted domain/persistence/service mechanisms and obey Minimum Sufficient Architecture.
8. Slice 1.6 remains the owner of Human Authorization and Decision Gates.
9. Agent execution remains unauthorized.

## Not authorized

This authority does **not** authorize:

- production implementation;
- persistence/schema changes unless independently surfaced as a design escalation and later accepted;
- new lifecycle or governance semantics;
- human approval/decision mutation workflows;
- repository/provider mutations;
- agent execution;
- Slice 1.6 or later slices.

## Design gate

The architect must produce a durable Slice 1.5 design record from the canonical commit containing this authority record.

That design must receive independent design review using:

```text
ACCEPT
REVISE
ESCALATE
```

Human design acceptance and implementation authorization are separate later gates.

## Hard stop

```text
Slice 1.5:
OPEN

Slice 1.5 design:
AUTHORIZED

Slice 1.5 implementation:
NOT AUTHORIZED

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
