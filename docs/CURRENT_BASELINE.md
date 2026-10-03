# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.5 implementation authorized  
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

Implementation authorization:
RLY-S15-AUTH-001 — AUTHORIZED

Implementation baseline:
2075be41962591552eded0597e243f0c1754b27f

Preferred implementation role/model:
IMPLEMENTATION_AGENT — GPT-5.6 Luna
```

Roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

# 3. Authorized Slice 1.5 implementation boundary

Implementation is authorized only for the accepted read-only Board Projection design.

The implementation may add:

- typed immutable board projection models;
- deterministic Project index, Project board, and Slice detail projection service;
- narrow read-only SQLite transaction/read helpers with no migration;
- request-scoped SQLite connection ownership;
- FastAPI + Uvicorn as direct runtime dependencies;
- optional `httpx` as a dev/test-only dependency if required for HTTP-level tests;
- simple server-rendered HTML/CSS;
- bounded local `relay-board` launcher if needed;
- deterministic tests and implementation evidence.

The implementation must preserve:

- exact lifecycle authority and display-only lanes;
- READY distinct from authorization;
- gate-level evaluation observations only;
- full persisted evaluation-context identity for duplicate/conflict integrity;
- `MATCHING_DURABLE_BASIS` / `STALE_DURABLE_BASIS` semantics;
- one SQLite connection and one read snapshot per request;
- loopback-default read-only serving;
- disabled framework-generated OpenAPI/Swagger/ReDoc routes;
- no board mutation, React, final JSON API, async persistence, connection pooling, schema migration, repository/provider mutation, Slice 1.6, or agent execution.

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
SLICE 1.5 IMPLEMENTATION_AGENT — GPT-5.6 LUNA

Slice 1.5:
OPEN

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
AUTHORIZED

Implementation baseline:
2075be41962591552eded0597e243f0c1754b27f

Technical acceptance:
NOT YET GRANTED

React frontend:
DEFERRED / NOT AUTHORIZED IN SLICE 1.5

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

The next governed gate is implementation completion followed by independent implementation evaluation of the exact candidate SHA.

**Unblocked ≠ accepted.**
