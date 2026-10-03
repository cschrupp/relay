# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.5 closed; Slice 1.6 implementation authorized; implementation not yet complete
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

Slice 1.5:
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

Accepted implementation candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED

Finalization and closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Canonical closure commit promoted to main:
45a3acbc5a26c618176a2d5da32a70b67adb9883

Preferred implementation role/model:
IMPLEMENTATION_AGENT — GPT-5.6 Luna
```

Roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

# 3. Completed Slice 1.5 implementation boundary

The authorized read-only Board Projection implementation is complete at the accepted candidate above.

The implementation added:

- typed immutable board projection models;
- deterministic Project index, Project board, and Slice detail projection service;
- narrow read-only SQLite transaction/read helpers with no migration;
- request-scoped SQLite connection ownership;
- FastAPI + Uvicorn as direct runtime dependencies;
- optional `httpx` as a dev/test-only dependency if required for HTTP-level tests;
- simple server-rendered HTML/CSS;
- bounded local `relay-board` launcher if needed;
- deterministic tests and implementation evidence.

The implementation preserves:

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

# 5. Slice 1.6 accepted design

```text
Slice:
1.6 — Human Authorization and Decision Gates

Opening authority:
RLY-S16-OPEN-001

Canonical repository head at opening:
d757885ff417cd573b2d3f566d778dd4a37520b3

Human-authorized design subject baseline:
e9c6e3a5cc7592764bf0ac4932a2ae2659644027

Design authorization:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Authority-recording design parent:
e4923c837f20de35eb96cd1caf615b86860d9222

Revision 1:
f3a0fa7d9cc5b344399c070406353e1107ec30ff

Independent design evaluation 1:
RLY-S16-DESIGN-EVAL-001 — REVISE

Revision 2 amendment:
9a114b81f4347df10db7dfcb75677a606f18262e

Independent design evaluation 2:
RLY-S16-DESIGN-EVAL-002 — REVISE

Revision 3 amendment / exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent combined design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S16-DESIGN-ACCEPT-001 — ACCEPTED

Human design acceptance record commit:
0d23067c96eb9f3cec0ea3a3fa21b2fa605e4de1
```

The accepted Slice 1.6 design preserves the existing Relay governance model and defines the minimum Human Authority product seam. It requires exact action-basis binding, deterministic durable human-evidence projection, atomic successor gate-evaluation observations after gate-affecting human mutations, and explicit separation between human decision evidence and governed lifecycle execution.

The accepted design keeps `BLOCK`, `PAUSE`, and `DEFER` as orthogonal blockage controls; requires `ADVANCE` and `CANCEL` to execute only exact current GREEN gates; keeps the local server-rendered FastAPI board and request-scoped SQLite architecture; requires no new schema migration or runtime dependency; and reserves transition to `ACCEPTED`, manual evaluation, technical acceptance, and accepted-baseline promotion for Slice 1.7.

# 6. Current authority boundary

```text
Current finalization gate:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE

Accepted technical candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED

Finalization / closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

React frontend:
DEFERRED / NOT AUTHORIZED IN SLICE 1.5

Slice 1.6:
OPEN

Slice 1.6 design authorization:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Slice 1.6 design:
ACCEPTED

Exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S16-DESIGN-ACCEPT-001 — ACCEPTED

Slice 1.6 implementation:
AUTHORIZED — RLY-S16-AUTH-001

Authorized implementation baseline:
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3

Implementation branch:
implementation/1.6-human-authorization-decision-gates

Preferred implementation model:
GPT-5.6 Luna

Implementation handoff:
docs/reviews/SLICE_1_6_IMPLEMENTATION_HANDOFF.md

Mutation endpoints / board controls:
AUTHORIZED FOR IMPLEMENTATION WITHIN ACCEPTED SLICE 1.6 DESIGN

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Slice 1.6 implementation is authorized under `RLY-S16-AUTH-001` against the exact accepted design and implementation baseline above. The implementation is not yet complete; the currently implemented Slice 1.5 board remains read-only. No schema migration or new dependency is authorized. Slice 1.7 and agent execution remain outside this authority.

**Unblocked ≠ authorized.**
