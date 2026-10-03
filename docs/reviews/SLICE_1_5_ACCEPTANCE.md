# Slice 1.5 — Human Technical Acceptance

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.5 — Board Projection  
**Authority ID:** `RLY-S15-ACCEPT-001`

## Human Authority decision

The Human Authority explicitly accepts the exact independently evaluated Slice 1.5 technical candidate:

```text
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
```

The acceptance follows:

```text
RLY-S15-EVAL-001 — ACCEPT
```

recorded at evaluation commit:

```text
ea26e0ae717e873e4b3ded27f1a8e9b0b278d7be
```

and promotes the exact candidate as the accepted Slice 1.5 technical result.

## Accepted technical lineage

```text
2075be41962591552eded0597e243f0c1754b27f
    authorized implementation baseline
        ↓
b529c7b1e4816cea0f4045a9d0efb8064984d0ed
    Slice 1.5 board-projection implementation
        ↓
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
    bounded current-baseline registry repair
```

The product implementation commit remains intact. The registry-only repair corrected the pre-existing living-projection digest mismatch exposed by CI and does not change the accepted product semantics.

## Accepted result

The accepted technical result implements the first human-facing Relay board as a deterministic, read-only projection of governed durable state, including:

- immutable board projection models and six display-only lanes;
- exact lifecycle state kept separate from board presentation;
- READY kept separate from execution authorization;
- gate-level evaluation observations without a Slice-wide traffic light;
- durable structural-basis evaluation status and full-context duplicate/conflict semantics;
- request-scoped SQLite ownership and one read snapshot per projection operation;
- fail-closed integrity behavior;
- server-rendered escaped HTML;
- local loopback FastAPI/Uvicorn serving;
- disabled generated OpenAPI/Swagger/ReDoc routes;
- bounded direct dependencies exactly as authorized.

GitHub Actions run `37097340325` (#297) completed successfully on the exact accepted candidate, with all 556 tests passing and the package build succeeding.

## Authority boundary

This decision is Human technical acceptance of the exact Slice 1.5 implementation result only.

It authorizes bounded acceptance recording and later promotion/reconciliation of the accepted implementation lineage into canonical repository history.

It does **not** by itself authorize:

- Slice 1.5 closure;
- opening Slice 1.6;
- React/TypeScript/Node work;
- the final JSON/OpenAPI API contract;
- board mutation workflows;
- agent execution;
- repository/provider mutation behavior;
- unrelated product implementation.

Canonical-main living projections and `.relay/registry.json` still require an explicit bounded reconciliation because `main` advanced its own `CURRENT_BASELINE.md` after the implementation technical baseline while the implementation candidate followed the authorized baseline branch.

That reconciliation is governance/finalization work and must preserve both the accepted implementation lineage and the already-recorded implementation authorization history. It must not rewrite the accepted candidate.

## Hard stop

```text
Slice 1.5 technical result:
ACCEPTED

Exact accepted candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED

Canonical promotion/finalization:
NOT YET COMPLETED

Slice 1.5 closure:
NOT YET AUTHORIZED

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
