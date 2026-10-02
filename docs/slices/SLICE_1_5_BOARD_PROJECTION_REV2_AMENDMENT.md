# Slice 1.5 — Board Projection — Revision 2 Amendment

**Status:** DESIGN REVISION 2 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design amendment  
**Human version:** Revision 2 Amendment  
**Project:** Relay  
**Slice:** 1.5  
**Design authority:** `RLY-S15-DESIGN-AUTH-001`  
**Revision 1 design head:** `e921c2446f7770042a77c2f78e5f9c4af62e204b`  
**Human direction:** FastAPI backend now; React frontend deferred to a later slice  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-10-02

---

# 1. Purpose

This bounded amendment refines the Slice 1.5 transport/presentation architecture before
independent design review.

Revision 1 remains historical and is not edited in place. This amendment is normative
wherever it conflicts with Revision 1.

The Human Authority has selected the long-term product direction:

```text
backend: FastAPI
frontend: React
```

Slice 1.5 adopts FastAPI now as the durable backend/transport seam, while deliberately
deferring React and the Node/frontend toolchain. The current board remains a simple
server-rendered, read-only validation surface.

This change does not broaden Slice 1.5 into human decision workflows, agent execution,
repository/provider mutation, or Slice 1.6 behavior.

---

# 2. Why the transport decision changes

Revision 1 selected a zero-new-runtime-dependency stdlib WSGI adapter. That was
sufficient for a disposable local board, but it would intentionally create a web
transport layer that the project already expects to replace.

Because Slice 1.5 design authority explicitly permits technology choices necessary to
specify the implementation contract, the minimum sufficient architecture is now:

```text
Relay governed state
        ↓
Board Projection Service
        ↓
FastAPI adapter
        ↓
simple server-rendered HTML          Slice 1.5
        ↓
FastAPI JSON API + React             later accepted slice
```

The durable boundary is the projection service plus FastAPI backend. The temporary part
is only the initial HTML presentation.

Flask is not introduced as an intermediate framework.

---

# 3. Normative design amendments

## S15-D45 — FastAPI is the backend and transport seam

Revision 1 S15-D32 is replaced.

Slice 1.5 uses FastAPI as the HTTP application framework.

FastAPI is not domain authority and does not own board derivation. Route handlers are
thin adapters over `board/service.py`.

Normative dependency direction:

```text
domain / persistence
        ↓
board models + board service
        ↓
FastAPI route adapter
        ↓
HTML rendering
```

No FastAPI object, request object, response object, or route concern may enter the
domain, persistence, lifecycle, governance, or board-projection derivation contracts.

## S15-D46 — React is explicitly deferred

React is the intended later frontend, but Slice 1.5 does not add:

- React;
- TypeScript;
- Node;
- npm/pnpm/yarn;
- Vite or another frontend bundler;
- client-side routing;
- client-side state management;
- generated TypeScript API clients;
- a frontend test/build pipeline.

This is deliberate scope control, not architectural uncertainty.

A later accepted slice may add React against the FastAPI backend without changing the
governed projection semantics.

## S15-D47 — Slice 1.5 HTML is intentionally replaceable

The first board remains server-rendered HTML with plain CSS.

The FastAPI adapter may return `HTMLResponse` values built from the existing deterministic
rendering layer. Slice 1.5 does not require Jinja2 or another template-engine dependency.

The HTML renderer is presentation-only and may be replaced by React later. The board
models and board service are not temporary.

## S15-D48 — One source of projection truth

HTML rendering and any future JSON API must consume the same immutable board projection
values.

The implementation must not create:

```text
HTML-specific lifecycle rules
HTML-specific gate derivation
route-specific blocker semantics
future React-specific board truth
```

All lifecycle lane mapping, evaluation-basis classification, stale-evidence suppression,
gate ordering, dependency semantics, and fail-closed integrity logic remain in the
projection/application layer defined by Revision 1.

## S15-D49 — JSON API is compatible by design but not required yet

Slice 1.5 is not required to expose the final React JSON API.

The projection models must remain serialization-safe and suitable for a later read-only
FastAPI JSON boundary, but API versioning, browser client contracts, generated schemas,
and React consumption are deferred until explicitly authorized.

This avoids prematurely freezing a public API before the board is dogfooded.

A later API route should be able to expose the existing projection service rather than
re-derive board semantics.

## S15-D50 — Bounded new runtime dependencies

Revision 1 A17 and the zero-new-runtime-dependency claim are replaced.

Slice 1.5 may add only the web runtime dependencies required for this accepted direction:

```text
fastapi
uvicorn
```

No other new runtime dependency is authorized merely by this amendment.

In particular, this amendment does not authorize Jinja2, an ORM, a JavaScript runtime,
a frontend framework, a websocket stack, or a background-job framework.

Exact package versions are resolved and locked through the existing `uv` workflow at
implementation time.

## S15-D51 — FastAPI runtime remains local and read-only

Revision 1 S15-D33, S15-D34, and S15-D35 remain semantically valid with FastAPI as the
adapter.

The Slice 1.5 server:

- binds to `127.0.0.1` by default;
- serves only the accepted read surface;
- supports `GET` and `HEAD`;
- returns `405 Method Not Allowed` for mutation methods;
- has no board mutation endpoints;
- has no websocket, SSE, polling worker, or push channel;
- recomputes the board on ordinary request/refresh;
- does not add auth merely to compensate for a broader network bind.

`uvicorn` is the expected local ASGI server.

## S15-D52 — FastAPI does not authorize asynchronous complexity

FastAPI adoption does not imply that board projection code should become asynchronous.

SQLite access and projection composition may remain synchronous unless an accepted
implementation requirement demonstrates otherwise.

No async repository abstraction, connection pool, task queue, or concurrency framework
is introduced solely because FastAPI supports async handlers.

## S15-D53 — Future React remains a client of governed projection

When React is later authorized, it must consume backend projection/API values rather than
reconstruct Relay authority semantics in browser code.

In particular, the React client must not independently decide:

- lifecycle lane assignment;
- whether READY means authorized;
- gate traffic-light meaning;
- evaluation-basis freshness;
- lifecycle versus evaluation staleness;
- dependency blocker semantics;
- integrity-repair behavior.

Those remain backend projection semantics.

---

# 4. Amended implementation surface

Revision 1 Section 20 is amended as follows.

Expected new files:

```text
src/relay_engine/board/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/api.py

tests/unit/test_board_models.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_api.py
tests/integration/test_board_projection_sqlite.py
```

`api.py` owns the FastAPI application/route adapter. `render.py` owns the replaceable
Slice 1.5 HTML presentation.

Revision 1's proposed `board/web.py` stdlib-WSGI adapter is removed from the expected
surface unless implementation demonstrates a naming-only reason to retain `web.py`.
There must not be parallel WSGI and ASGI application stacks.

Expected bounded existing-file changes additionally include:

```text
pyproject.toml
uv.lock
```

for the accepted FastAPI/Uvicorn runtime dependencies and, if used, the `relay-board`
console entry point.

No database migration is authorized.

---

# 5. Route contract amendment

Revision 1 Sections 15–17 remain applicable except for the web-framework implementation.

The human-facing route shape remains:

```text
GET /
GET /projects/{project_id}
GET /projects/{project_id}/slices/{slice_id}
```

`HEAD` may mirror `GET` without a body.

The FastAPI app must preserve the Revision 1 presentation boundary:

```text
NOT_FOUND
UNAVAILABLE
INTEGRITY_ERROR
```

with deterministic mapping to appropriate HTTP responses/pages.

No POST/PUT/PATCH/DELETE endpoint is authorized.

The HTML routes are not declared the final React API contract.

---

# 6. Test-contract amendments

Revision 1 S15-D39–D44 remain normative, with the following additional requirements.

## S15-D54 — FastAPI adapter tests

Tests must prove:

- the application is a FastAPI application;
- board route handlers call the projection/service boundary rather than owning
  projection derivation;
- `GET` Project index, Project board, and Slice detail behave as specified;
- `HEAD` behavior is read-only;
- POST/PUT/PATCH/DELETE are rejected;
- unknown Project/Slice behavior remains deterministic;
- `UNAVAILABLE` and `INTEGRITY_ERROR` do not become successful partial pages;
- dynamic HTML remains escaped;
- no request mutates governed state;
- loopback is the default runtime bind configured by the executable/entry point.

## S15-D55 — Dependency-boundary tests

Implementation/evaluation must verify that:

- FastAPI and Uvicorn are the only new runtime dependencies introduced by this design
  direction unless separately escalated;
- no Node/React/frontend build artifacts enter Slice 1.5;
- board models/service do not import FastAPI;
- domain/persistence/lifecycle/governance modules do not import FastAPI;
- HTML rendering does not contain independent authority derivation.

---

# 7. Revised / additional acceptance criteria

Revision 1 acceptance criteria remain normative except where explicitly amended below.

### A17 — Bounded permanent backend dependency

Replaces Revision 1 A17.

Slice 1.5 introduces FastAPI and Uvicorn as the bounded web runtime dependencies. No
React/Node/frontend dependency is introduced.

### A18 — Local FastAPI boundary

Replaces Revision 1 A18.

The FastAPI server defaults to loopback only and exposes only GET/HEAD read routes;
mutation methods are rejected.

### A25 — Permanent backend seam

FastAPI route handling is a thin adapter over the deterministic board projection service;
board semantics do not live in route handlers.

### A26 — React deferred cleanly

No React, Node, TypeScript, frontend bundler, client-side state system, or frontend build
pipeline is introduced in Slice 1.5.

### A27 — Replaceable current presentation

Slice 1.5 HTML/CSS rendering can be replaced later without changing board projection
models, projection semantics, or governed durable state.

### A28 — Future API compatibility without premature API freeze

Board projection values are typed/serialization-safe and suitable for later FastAPI JSON
exposure, while Slice 1.5 does not claim to define the final React API contract.

### A29 — No duplicated authority semantics

No HTML-specific or future-client-specific code duplicates lifecycle, gate, authorization,
freshness, dependency, or integrity derivation owned by the board service.

### A30 — No framework-driven async expansion

FastAPI adoption does not introduce async persistence/repository abstractions, background
workers, websockets, or other concurrency architecture without a separately accepted
need.

---

# 8. Revised design-review package

Independent review must evaluate Revision 1 together with this Revision 2 amendment.

In addition to Revision 1 Section 25, review should verify:

1. FastAPI is a justified bounded dependency rather than a premature platform layer;
2. the board service remains framework-independent;
3. React is clearly deferred rather than partially introduced;
4. the initial HTML surface is replaceable without reworking projection semantics;
5. the design does not prematurely freeze the final React JSON API;
6. FastAPI adoption does not trigger unnecessary async/concurrency abstractions;
7. no Flask/stdlib parallel web stack remains in the intended implementation surface.

Allowed independent design-review outcomes remain:

```text
ACCEPT
REVISE
ESCALATE
```

---

# 9. Updated decision summary

Revision 1 S15-D01–D44 remain normative except where this amendment explicitly replaces
or qualifies them.

```text
S15-D45  FastAPI is the permanent backend/transport seam
S15-D46  React/Node frontend is deferred
S15-D47  Slice 1.5 HTML is intentionally replaceable
S15-D48  One backend source of projection truth
S15-D49  Final JSON API is compatible by design but not frozen now
S15-D50  New runtime dependencies bounded to FastAPI + Uvicorn
S15-D51  FastAPI runtime remains loopback and read-only
S15-D52  FastAPI does not imply async architecture
S15-D53  Future React is a client of governed backend projection
S15-D54  FastAPI adapter test contract
S15-D55  Dependency-boundary test contract
```

---

# 10. Hard stop

```text
Slice 1.5:
OPEN

Design authority:
RLY-S15-DESIGN-AUTH-001

Revision 1 design head:
e921c2446f7770042a77c2f78e5f9c4af62e204b

Revision 2 amendment:
SUBMITTED FOR INDEPENDENT REVIEW

Combined design:
REVISION 1 + REVISION 2 AMENDMENT

Human design acceptance:
NOT GRANTED

Slice 1.5 implementation:
NOT AUTHORIZED

React frontend:
DEFERRED / NOT AUTHORIZED IN SLICE 1.5

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Revision 1 plus this amendment must receive independent design review before any human
design acceptance or implementation authorization.

**Unblocked ≠ authorized.**
