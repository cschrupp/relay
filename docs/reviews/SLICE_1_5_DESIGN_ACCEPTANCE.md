# Slice 1.5 — Design Acceptance

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-02  
**Project:** Relay  
**Slice:** 1.5 — Board Projection  
**Record:** `RLY-S15-DESIGN-ACCEPT-001`

## Reviewed design

```text
Human-authorized design subject baseline:
359cd61f0c05815390a6822739c0c68d3f020c32

Authority-recording design parent:
a9fd4ed7a82eb0f42ac19b4e0702db0060bcea6c

Revision 1:
e921c2446f7770042a77c2f78e5f9c4af62e204b

Revision 2 amendment:
23199dbc8342c0f04542998bfd738e4d7d79ee23

Revision 3 amendment / exact reviewed design head:
25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b

Prior independent evaluation:
RLY-S15-DESIGN-EVAL-001 — REVISE

Independent combined design evaluation:
RLY-S15-DESIGN-EVAL-002 — ACCEPT

Evaluation record commit:
bf94223b722b0f9e4d97e6ec123f71fa10b994ee
```

## Human Authority decision

```text
RLY-S15-DESIGN-ACCEPT-001
Slice 1.5 Revision 1 + Revision 2 Amendment + Revision 3 Amendment
ACCEPTED
```

The Human Authority explicitly accepts the exact combined design ending at:

```text
25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b
```

## Accepted design boundary

The accepted combined design covers the first human-facing read-only Relay board and includes:

- deterministic board projection over accepted durable Project, Slice, lifecycle, gate, evaluation, baseline, dependency, and execution state;
- six fixed non-authoritative display lanes while preserving exact lifecycle phase;
- explicit separation of READY from authorization;
- gate-level traffic-light observations only, with no Slice-wide traffic light;
- `MATCHING_DURABLE_BASIS`, `STALE_DURABLE_BASIS`, `NOT_EVALUATED`, and `NOT_APPLICABLE` evaluation-observation states;
- full `gate_refs + HandoverContext` identity for duplicate-evidence integrity;
- fail-closed handling of contradictory, corrupt, unavailable, or structurally stale source state;
- one request-scoped SQLite connection and one read transaction/snapshot per projection request;
- framework-independent board projection/service semantics;
- FastAPI + Uvicorn as the bounded backend/web transport seam;
- simple server-rendered HTML for Slice 1.5;
- disabled framework-provided OpenAPI/Swagger/ReDoc endpoints;
- loopback-default read-only serving;
- FastAPI and Uvicorn as the only new direct runtime dependency declarations;
- React/TypeScript/Node and the final JSON/OpenAPI contract explicitly deferred.

## Authority boundary

This record accepts the design only.

It does **not** by itself authorize production implementation, React, mutation endpoints, human-decision workflows, repository/provider mutation, background workers, websockets, async persistence, connection pooling, Slice 1.6, or agent execution.

A separate Human Authority implementation authorization is required before Slice 1.5 implementation may begin.

**Unblocked ≠ authorized.**
