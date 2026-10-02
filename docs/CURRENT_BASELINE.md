# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.5 design accepted  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** October 2026

---

# 1. Accepted foundation

```text
Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
COMPLETE / ACCEPTED / CLOSED
```

# 2. Slice 1.5 authority and accepted design

```text
Slice:
1.5 — Board Projection

Opening authority:
RLY-S15-OPEN-001

Opening baseline:
e44d63c15b7a4941146db5ad42bfcd414b71b444

Design authorization:
RLY-S15-DESIGN-AUTH-001 — AUTHORIZED

Human-authorized design subject baseline:
359cd61f0c05815390a6822739c0c68d3f020c32

Revision 1:
e921c2446f7770042a77c2f78e5f9c4af62e204b

Revision 2:
23199dbc8342c0f04542998bfd738e4d7d79ee23

Revision 3 / exact accepted design head:
25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b

Prior independent design evaluation:
RLY-S15-DESIGN-EVAL-001 — REVISE

Current independent design evaluation:
RLY-S15-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S15-DESIGN-ACCEPT-001 — ACCEPTED
```

Roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

# 3. Accepted Slice 1.5 design boundary

The accepted design specifies a deterministic read-only board projection over already-governed durable state.

It preserves:

- exact lifecycle authority and derived display lanes;
- READY distinct from authorization;
- gate-level evaluation observations only;
- full persisted evaluation-context identity for duplicate/conflict integrity;
- durable structural-basis freshness semantics;
- fail-closed projection behavior;
- one request-scoped SQLite connection and one read transaction/snapshot per request;
- FastAPI + Uvicorn as the bounded backend/web seam;
- simple server-rendered HTML for Slice 1.5;
- disabled framework-generated OpenAPI/Swagger/ReDoc routes;
- React/TypeScript/Node and the final JSON API deferred.

# 4. Preserved Slice 1.4 accepted state

```text
Canonical rework baseline:
dfe6c20c8f65b42fe69b7d315956a91d2a29487c

Prior implementation candidate:
e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d

Prior implementation evaluation:
RLY-S14-EVAL-001 — REWORK

Accepted technical result:
ae582c52ec4a6451b54e9d6e018932e93e72e013

Independent closure evaluation:
RLY-S14-CLOSE-EVAL-001 — ACCEPT

Canonical closure head:
e44d63c15b7a4941146db5ad42bfcd414b71b444
```

# 5. Current authority boundary

```text
Current role:
HUMAN AUTHORITY / SLICE 1.5 DESIGN ACCEPTANCE COMPLETE

Slice 1.5:
OPEN

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
NOT YET AUTHORIZED

React frontend:
DEFERRED / NOT AUTHORIZED IN SLICE 1.5

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

The next governed gate is a separate Human Authority implementation authorization bound to the exact accepted Slice 1.5 design and an explicit implementation baseline.

**Unblocked ≠ authorized.**
