# Slice 1.5 — Board Projection — Revision 3 Amendment

**Status:** DESIGN REVISION 3 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design amendment  
**Human version:** Revision 3 Amendment  
**Project:** Relay  
**Slice:** 1.5  
**Design authority:** `RLY-S15-DESIGN-AUTH-001`  
**Revision 1 design head:** `e921c2446f7770042a77c2f78e5f9c4af62e204b`  
**Revision 2 amendment head:** `23199dbc8342c0f04542998bfd738e4d7d79ee23`  
**Independent review:** `RLY-S15-DESIGN-EVAL-001 — REVISE`  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-10-02

---

# 1. Purpose

This bounded amendment resolves exactly the four findings from
`RLY-S15-DESIGN-EVAL-001`.

Revision 1 and Revision 2 remain historical and are not edited in place. This amendment
is normative wherever it conflicts with either earlier revision.

The accepted architecture direction is preserved:

```text
Relay governed state
        ↓
Board Projection Service
        ↓
FastAPI
        ↓
simple server-rendered HTML          Slice 1.5
        ↓
FastAPI JSON API + React             later accepted slice
```

This amendment does not authorize React, mutation endpoints, agent execution, repository
mutation, background workers, websockets, async persistence, a connection pool, a schema
migration, or Slice 1.6 work.

No architecture escalation is required.

---

# 2. Review findings resolved

## F001 — BLOCKING — FastAPI request/thread ownership of SQLite connections is undefined

Revision 2 selected FastAPI but did not specify who owns the `RelayDatabase` connection
for one HTTP request. The accepted persistence layer wraps one ordinary
`sqlite3.Connection`, so connection lifetime and thread ownership must be explicit.

### Resolution — S15-D56 — Request-scoped RelayDatabase ownership

FastAPI application state stores only immutable database configuration, principally the
explicit database path. It MUST NOT hold an open `RelayDatabase` or
`sqlite3.Connection` for reuse by requests.

Each Project-board or Slice-detail request owns one database connection for exactly one
projection operation:

```text
HTTP request
    -> enter one synchronous projection execution context
    -> open RelayDatabase(path, apply_migrations=False)
    -> open one Slice 1.5 read transaction
    -> load and verify all required durable state
    -> construct the complete immutable projection
    -> end the read transaction
    -> close RelayDatabase
    -> render/return from projection values only
```

Project-index requests follow the same ownership rule even when they require fewer
source tables.

A request MUST NOT borrow an application-global SQLite connection.

### S15-D57 — One synchronous ownership context per connection

Creation, use, transaction completion, and close of a request's SQLite connection MUST
occur inside one synchronous execution context owned by that request.

Minimum sufficient implementations include either:

1. a synchronous FastAPI route (`def`) that opens, uses, and closes the connection within
   that route invocation; or
2. an asynchronous route that delegates the complete open/project/close operation to one
   synchronous callable.

The design does not rely on a connection being safely transferable between threads.

The implementation MUST NOT set `check_same_thread=False` merely to share a connection
across FastAPI workers, and MUST NOT introduce a SQLite connection pool.

If implementation requires a materially different concurrency model, that is a design
deviation and must be escalated before continuing.

### S15-D58 — Read transaction and connection lifetimes are nested and fail closed

Revision 1 S15-D06 and S15-D20 are clarified as:

```text
request-owned RelayDatabase connection
    contains exactly one projection read_transaction
        contains every authoritative SQLite read for that projection
```

The read transaction:

- uses SQLite `BEGIN` as specified by Revision 1;
- begins only after the request-owned connection is open;
- ends before the connection is closed;
- commits/ends on successful projection construction;
- rolls back on any exception;
- leaves no transaction open after the projection call returns or raises.

The connection is closed on both success and failure.

HTML rendering receives only immutable projection values. Rendering MUST NOT retain,
reopen, lazily query, or otherwise depend on the closed database handle.

No database migration is run by an ordinary board request.

---

## F002 — BLOCKING — “exact evaluation basis” is narrower than persisted HandoverContext

Revision 1 correctly treats `GateEvaluationRecord` as historical evidence, but D12/D14
used the term “exact basis” for a subset of the persisted `HandoverContext`.

That terminology is replaced by two separate contracts.

### Resolution — S15-D59 — Full recorded evaluation identity

For duplicate/conflict detection, the full recorded evaluation basis is exactly:

```text
canonical gate_refs
+
full typed HandoverContext
```

Two `GateEvaluationRecord` values have the same full recorded basis only when:

```text
record_a.gate_refs == record_b.gate_refs
and
record_a.context == record_b.context
```

using accepted typed semantic equality.

The complete `HandoverContext` includes all persisted evaluation inputs, including:

- baseline;
- governance revision;
- exact lifecycle;
- dependency lifecycles;
- available artifacts;
- available evidence;
- supplied evaluation outcome;
- authorization grants;
- human decisions;
- quality checks;
- change-surface status;
- risk status;
- toolchain-change status.

Records that share gate/baseline/lifecycle/governance revisions but differ in any other
`HandoverContext` field are distinct historical observations, not duplicate-basis
records.

### S15-D60 — EvaluationBasisStatus means durable structural-basis status only

Revision 1 S15-D12 and the `EvaluationBasisStatus` conceptual contract are replaced.

The four statuses are:

```text
MATCHING_DURABLE_BASIS
STALE_DURABLE_BASIS
NOT_EVALUATED
NOT_APPLICABLE
```

`NOT_APPLICABLE`:

- no lifecycle exists; or
- no current-source gate definitions exist.

`NOT_EVALUATED`:

- current-source gates exist; and
- no durable evaluation record exists for the Slice.

`MATCHING_DURABLE_BASIS` applies to the latest durable evaluation observation when all
of these currently queryable structural facts match:

- record context Slice identity equals the current Slice;
- record context lifecycle equals the exact current durable lifecycle snapshot;
- record gate refs equal the exact sorted `(gate_id, latest revision)` set of current
  outgoing gates;
- record context baseline equals the single baseline of those current outgoing gates;
- each stored evaluation remains structurally valid against its own persisted
  `GateEvaluationRecord` context under the accepted model validation contract.

Otherwise the latest observation is `STALE_DURABLE_BASIS`.

This status deliberately does **not** claim that every field inside the historical
`HandoverContext` is still current. Slice 1.5 has no independently maintained
current-facts store for several supplied inputs such as quality-check, risk,
change-surface, toolchain-change, and evaluation-outcome facts.

### S15-D61 — Latest observation selection remains deterministic

Revision 1 S15-D11 remains normative: records are ordered by accepted durable sequence,
then record ID, and the final item is the latest observation.

Distinct observations with different full `HandoverContext` values may legitimately
occur on the same durable structural basis. The latest remains the visible observation.
Earlier records remain historical evidence.

The board MUST NOT treat those distinct contexts as corruption merely because their gate
refs, baseline, lifecycle revision, or governance revision happen to match.

### S15-D62 — Conflicting full-basis duplicates fail closed

Revision 1 S15-D14 is replaced.

For any two durable evaluation records with identical full recorded basis under S15-D59:

```text
same gate_refs
+
same full HandoverContext
```

then:

- identical evaluation outputs are redundant evidence and may be collapsed for display,
  retaining the latest record as the visible observation;
- different evaluation outputs are contradictory evidence and the affected Slice
  projection fails closed with `INTEGRITY_ERROR`.

Records whose full contexts differ are not subject to this duplicate-conflict rule.

### S15-D63 — Observational UI language is mandatory

Revision 1 S15-D13 and S15-D28 are amended.

When status is `MATCHING_DURABLE_BASIS`, stored lights may be displayed only with
observational language equivalent to:

```text
Latest recorded evaluation on current durable basis: GREEN / YELLOW / RED
```

The UI MUST NOT say or imply:

```text
Current evaluation: GREEN
Fresh evaluation: GREEN
Gate is currently GREEN
```

unless a later accepted contract establishes a complete current-facts evaluation model.

When status is `STALE_DURABLE_BASIS`:

- display `Evaluation: stale durable basis` or semantically equivalent language;
- do not expose historical lights as current gate lights;
- detail may show them only as explicitly older historical evidence.

Lifecycle `LifecycleValidity.STALE` remains a different fact from
`STALE_DURABLE_BASIS`.

The board still uses no wall-clock freshness TTL.

---

## F003 — MAJOR — “only new runtime dependencies” must mean direct dependencies

### Resolution — S15-D64 — Direct runtime dependency boundary

Revision 2 S15-D50, S15-D55, and A17 are clarified.

The only new **direct project runtime dependency declarations** authorized in
`pyproject.toml` by Slice 1.5 are:

```text
fastapi
uvicorn
```

Their resolver-required transitive dependencies are permitted only as normal locked
resolution output in `uv.lock`.

Transitive packages are not separate architecture choices and MUST NOT be promoted into
additional direct dependencies without an accepted need.

This does not authorize direct dependencies on:

- Jinja2;
- an ORM;
- React/Node/frontend tooling;
- websocket libraries;
- background-worker frameworks;
- a database connection pool.

Implementation evaluation audits direct additions in `pyproject.toml` and separately
verifies that `uv.lock` is frozen and consistent.

---

## F004 — MAJOR — default FastAPI documentation/OpenAPI routes exceed the bounded surface

### Resolution — S15-D65 — Framework-provided API documentation is disabled

Slice 1.5 intentionally does not freeze the future React JSON API contract.

The FastAPI application therefore MUST disable framework-provided documentation/schema
routes for Slice 1.5, semantically equivalent to:

```python
FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
```

The following default surfaces MUST NOT be exposed:

```text
/docs
/redoc
/openapi.json
```

or aliases that provide the same accidental framework documentation/API surface.

This does not prohibit a later accepted API slice from intentionally enabling and
versioning an OpenAPI contract.

The accepted human-facing Slice 1.5 routes remain:

```text
GET /
GET /projects/{project_id}
GET /projects/{project_id}/slices/{slice_id}
```

with corresponding read-only `HEAD` behavior as already specified.

No additional API route is authorized by this amendment.

---

# 3. Revised conceptual projection contract

Revision 1 S15-D18 is amended only for the evaluation-basis enum names.

```text
EvaluationBasisStatus
    MATCHING_DURABLE_BASIS
    STALE_DURABLE_BASIS
    NOT_EVALUATED
    NOT_APPLICABLE
```

All other conceptual projection fields remain unchanged.

`GateProjection.evaluation_basis_status` and
`SliceCard.evaluation_basis_status` use these precise semantics.

No slice-wide `TrafficLight` field is introduced.

---

# 4. Revised FastAPI / persistence composition boundary

The expected composition is now:

```text
FastAPI app
    stores database path/config only
        |
        v
sync request projection callable
    opens RelayDatabase(app_config.path, apply_migrations=False)
        |
        v
board/service.py
    opens one read_transaction(database)
    constructs immutable ProjectBoard / SliceDetail / ProjectSummary values
        |
        v
read transaction ends
RelayDatabase closes
        |
        v
board/render.py
    renders only immutable values
        |
        v
HTMLResponse
```

Exact function placement may vary, but the ownership and lifetime contract may not.

The board service remains framework-independent. `board/service.py` MUST NOT import
FastAPI.

Persistence remains unaware of FastAPI.

---

# 5. Amended test contract

Revision 1 S15-D39–D44 and Revision 2 S15-D54–D55 remain normative except where updated
below.

## S15-D66 — Request-scoped database ownership tests

Tests must prove:

- application state contains configuration/path, not an open RelayDatabase connection;
- each board/detail request opens its own RelayDatabase;
- two or more concurrent GET requests do not share one SQLite connection;
- each connection is created, used, transaction-completed, and closed in one synchronous
  ownership context;
- connection close occurs on successful projection;
- connection close occurs when projection raises `NOT_FOUND`, `UNAVAILABLE`, or
  `INTEGRITY_ERROR`-mapped failures as applicable;
- no request leaves `connection.in_transaction == True` after its projection scope;
- rendering occurs after the authoritative read transaction is closed;
- no request runs migrations;
- no implementation relies on `check_same_thread=False` to share a connection;
- no connection pool is introduced.

The existing concurrent-writer snapshot test from S15-D41 remains required.

## S15-D67 — Evaluation-basis tests

Revision 1 S15-D40 is replaced by tests proving:

- exact current lifecycle + exact current outgoing gate revision set + baseline match ->
  `MATCHING_DURABLE_BASIS`;
- lifecycle value/revision mismatch -> `STALE_DURABLE_BASIS`;
- current gate revision-set mismatch -> `STALE_DURABLE_BASIS`;
- baseline mismatch -> `STALE_DURABLE_BASIS`;
- current gates without any record -> `NOT_EVALUATED`;
- no current-source gates -> `NOT_APPLICABLE`;
- stale durable-basis record lights are not exposed as current lights;
- lifecycle `STALE` and evaluation `STALE_DURABLE_BASIS` remain distinct;
- same gate/baseline/lifecycle/governance structural tuple but different full
  `HandoverContext` -> distinct valid observations, not integrity error;
- same full `gate_refs + HandoverContext` and identical outputs -> redundant evidence;
- same full `gate_refs + HandoverContext` and different outputs -> `INTEGRITY_ERROR`;
- latest sequence/record-ID ordering selects the visible observation among distinct
  contexts;
- UI text for matching durable basis remains explicitly observational.

## S15-D68 — Direct dependency tests

Implementation/evaluation must prove:

- `pyproject.toml` adds no new direct runtime dependency beyond `fastapi` and `uvicorn`;
- resolver-required transitive packages may appear in `uv.lock`;
- `uv sync --frozen --group dev` succeeds;
- no React/Node/Jinja/ORM/worker/pool direct dependency is introduced.

## S15-D69 — FastAPI surface tests

Tests must prove:

- `/`, Project board, and Slice detail routes behave as specified;
- `/docs` is not exposed;
- `/redoc` is not exposed;
- `/openapi.json` is not exposed;
- no equivalent framework-generated documentation/schema alias is configured;
- POST/PUT/PATCH/DELETE remain rejected for the accepted board resource surface;
- the application remains loopback-default at executable/server configuration level.

---

# 6. Revised acceptance criteria

Revision 1 and Revision 2 acceptance criteria remain normative except where this section
replaces or extends them.

### A09 — Matching durable structural basis

Replaces the Revision 1 meaning of A09.

The latest evaluation receives `MATCHING_DURABLE_BASIS` only when its currently
queryable structural durable facts match under S15-D60. This status does not claim that
every historical `HandoverContext` input is currently verified.

### A10 — Stale durable structural basis

Replaces the Revision 1 meaning of A10.

Any mismatch in the structural durable comparison defined by S15-D60 yields
`STALE_DURABLE_BASIS`, without changing lifecycle validity.

### A11 — Historical light presentation

Replaces the Revision 1 meaning of A11.

Stored gate lights are presented as latest recorded observations only when their durable
structural basis matches, using explicitly observational language. Stale-basis lights are
not rendered as current gate state.

### A12 — Full-basis duplicate integrity

Replaces the duplicate/conflict portion of the Revision 1 acceptance contract.

Only records with identical canonical gate refs and full typed `HandoverContext` are
full-basis duplicates. Conflicting outputs on that identical full basis fail closed.
Distinct contexts are distinct observations.

### A17 — Bounded direct runtime dependencies

Replaces Revision 2 A17.

The only new direct runtime dependency declarations are FastAPI and Uvicorn. Resolver
transitives may appear in the frozen lockfile.

### A31 — Request-scoped SQLite ownership

Every HTTP projection request owns one ordinary RelayDatabase connection. No open SQLite
connection is stored in application state or shared across concurrent requests.

### A32 — Same-context SQLite use

Connection create/use/transaction completion/close occur inside one synchronous
request-owned execution context. No `check_same_thread=False` sharing workaround or
connection pool is introduced.

### A33 — Projection complete before close/render

Every authoritative read occurs inside one read transaction on the request-owned
connection. The immutable projection is complete before the database connection closes,
and rendering performs no database access.

### A34 — FastAPI implicit documentation disabled

Framework-provided OpenAPI/Swagger/ReDoc routes are disabled in Slice 1.5.

### A35 — React/API future remains unfrozen

Disabling the Slice 1.5 OpenAPI surface does not preclude a later accepted slice from
adding an intentional versioned JSON/OpenAPI contract for React.

---

# 7. Review boundary

Independent review must evaluate the combined design:

```text
Revision 1
+
Revision 2 Amendment
+
Revision 3 Amendment
```

The next reviewer must specifically verify that all findings from
`RLY-S15-DESIGN-EVAL-001` are closed:

```text
F001 request/thread SQLite ownership
F002 full evaluation identity vs durable structural-basis status
F003 direct dependency terminology
F004 disabled implicit FastAPI docs/OpenAPI surface
```

Allowed independent review outcomes remain:

```text
ACCEPT
REVISE
ESCALATE
```

---

# 8. Hard stop

```text
Slice 1.5:
OPEN

Design authority:
RLY-S15-DESIGN-AUTH-001

Revision 1:
e921c2446f7770042a77c2f78e5f9c4af62e204b

Revision 2:
23199dbc8342c0f04542998bfd738e4d7d79ee23

Independent review:
RLY-S15-DESIGN-EVAL-001 — REVISE

Revision 3:
SUBMITTED FOR INDEPENDENT REVIEW

Combined design:
REVISION 1 + REVISION 2 + REVISION 3

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

Revision 1 + Revision 2 + Revision 3 must receive independent design review before any
human design acceptance or implementation authorization.

**Unblocked ≠ authorized.**
