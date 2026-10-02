# Slice 1.5 — Implementation Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Authority decision date:** 2026-10-02  
**Project:** Relay  
**Slice:** 1.5 — Board Projection  
**Record:** `RLY-S15-AUTH-001`

## Accepted design authority

```text
Independent combined design evaluation:
RLY-S15-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S15-DESIGN-ACCEPT-001 — ACCEPTED

Exact accepted design head:
25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b
```

The implementation baseline is the canonical repository state immediately after Human design acceptance:

```text
2075be41962591552eded0597e243f0c1754b27f
```

## Human Authority decision

```text
RLY-S15-AUTH-001
Slice 1.5 implementation
AUTHORIZED
```

Implementation is authorized only against the accepted combined Slice 1.5 design:

```text
Revision 1
    e921c2446f7770042a77c2f78e5f9c4af62e204b
+
Revision 2 Amendment
    23199dbc8342c0f04542998bfd738e4d7d79ee23
+
Revision 3 Amendment
    25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b
```

Revision 3 is normative wherever it replaces or qualifies Revision 1 or Revision 2.

---

# Preferred implementation role / model

```text
Role:
IMPLEMENTATION_AGENT

Preferred model:
GPT-5.6 Luna
```

If the executing model differs, the implementation result must record both the preferred and executing model provenance and the deviation.

The implementation agent must not redesign the accepted architecture merely because another design seems cleaner or more extensible. Ambiguity that materially affects authority, persistence semantics, concurrency, or change surface is a stop condition and must be escalated.

---

# Objective

Implement the first human-facing Relay board strictly as a deterministic, read-only projection of already-governed durable state.

The implementation must make the accepted governance model visible without creating a second state machine, a second authority model, or UI-owned truth.

The required runtime direction for Slice 1.5 is:

```text
Relay governed durable state
        ↓
framework-independent board projection/service
        ↓
FastAPI adapter
        ↓
simple server-rendered HTML
```

React/TypeScript/Node and the eventual versioned JSON/OpenAPI contract are explicitly deferred.

---

# Authorized production scope

Luna may implement only the minimum mechanisms required by the accepted design, including:

1. **Board projection models**
   - immutable typed projection/view models;
   - six fixed display-only lanes;
   - exact lifecycle phase preserved on cards;
   - no Slice-wide `TrafficLight` field;
   - explicit `EvaluationBasisStatus` values:
     - `MATCHING_DURABLE_BASIS`
     - `STALE_DURABLE_BASIS`
     - `NOT_EVALUATED`
     - `NOT_APPLICABLE`.

2. **Deterministic board projection service**
   - Project index projection;
   - Project board projection;
   - Slice detail projection;
   - deterministic ordering and display-only filtering;
   - exact current outgoing-gate derivation;
   - lifecycle/history integrity verification;
   - durable evaluation-observation selection;
   - full `gate_refs + HandoverContext` duplicate/conflict semantics;
   - durable structural-basis classification;
   - dependency and parent/child projection without invented blocker semantics;
   - execution/baseline provenance where specified;
   - fail-closed behavior for contradictions/corruption.

3. **Read-consistency persistence support**
   - one read-only SQLite transaction/snapshot per projection request;
   - narrow typed read helpers where existing public persistence APIs are insufficient;
   - deterministic SQL ordering;
   - no schema migration;
   - no write behavior added to board code.

4. **Request-scoped SQLite ownership**
   - application state stores configuration/database path only;
   - each HTTP projection request opens exactly one ordinary `RelayDatabase` connection;
   - connection creation, use, transaction completion, and close occur inside one synchronous request-owned execution context;
   - the complete immutable projection is constructed before the connection closes;
   - HTML rendering performs no database access;
   - connection closes on both success and failure;
   - no app-global connection;
   - no connection pool;
   - no `check_same_thread=False` sharing workaround.

5. **FastAPI read-only adapter**
   - accepted routes:

```text
GET /
GET /projects/{project_id}
GET /projects/{project_id}/slices/{slice_id}
```

   - corresponding read-only HEAD behavior as accepted;
   - POST/PUT/PATCH/DELETE rejected for the accepted board surface;
   - bind loopback by default (`127.0.0.1`), not `0.0.0.0`;
   - framework-generated `/docs`, `/redoc`, `/openapi.json`, and equivalent implicit documentation/schema aliases disabled;
   - no websocket, SSE, polling worker, push channel, or background refresh loop.

6. **Simple server-rendered HTML**
   - plain HTML/CSS only;
   - no JavaScript requirement;
   - no Jinja/template-engine dependency;
   - all dynamic durable text escaped;
   - no arbitrary durable Markdown rendered as HTML;
   - semantic headings/landmarks/links;
   - visible focus state;
   - traffic-light and status meaning expressed in text as well as color;
   - logical narrow-screen reading order.

7. **Dependency changes**
   - only new direct runtime dependency declarations authorized:

```text
fastapi
uvicorn
```

   - resolver-required transitives are permitted through normal `uv.lock` resolution only;
   - `httpx` is explicitly authorized as an optional **dev/test-only** dependency if Luna uses FastAPI/Starlette `TestClient` or an equivalent HTTP-level test helper;
   - no other new direct runtime or dev dependency is authorized without escalation.

8. **Executable entry point**
   - a small `relay-board` console entry point may be added if it remains the minimum sufficient way to launch the accepted local server;
   - it must require an explicit database path and may accept bounded host/port configuration while defaulting to loopback;
   - it must not run schema migrations as part of an ordinary board request path.

---

# Expected change surface

The expected production change surface is:

## New files

```text
src/relay_engine/board/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
```

A very small launcher/CLI module may be added only if required for the accepted `relay-board` entry point and if its responsibility is obvious and local.

## Expected bounded existing-file changes

```text
src/relay_engine/persistence/database.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
pyproject.toml
uv.lock
```

Only narrow read-transaction/read-helper additions are expected in persistence.

## Tests

Expected test surface includes, with exact filenames allowed to vary if repository conventions justify it:

```text
tests/unit/test_board_models.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_web.py
tests/integration/test_board_projection_sqlite.py
```

Additional narrowly-scoped test files are permitted when they materially improve clarity, but a new generalized test framework or fixture architecture is not authorized.

## Documentation

After implementation is complete, Luna may add/update only the bounded implementation memory/evidence needed to hand the exact candidate to an evaluator. Locked accepted design/authority/review records must not be edited in place.

A materially larger production-file surface is a stop condition unless the extra files are clearly mechanical tests or implementation memory and do not expand architecture.

---

# Normative implementation semantics

## Lane derivation

The board uses exactly:

```text
NOT_STARTED  -> no lifecycle
SHAPING      -> PROPOSED, DEFINING, RESEARCHING, DESIGNING, CONTRACTING, PLANNING
READY        -> READY
DELIVERY     -> IMPLEMENTING
EVALUATION   -> EVALUATING, REWORK
TERMINAL     -> ACCEPTED, SUPERSEDED, CANCELLED
```

Lane identity is presentation-only and is never persisted or accepted as lifecycle input.

## READY does not mean authorized

The UI must keep lifecycle readiness and execution authority visibly distinct.

No button, badge, inferred status, or text may convert READY into implicit authorization.

## Gate traffic lights remain observations

There is no Slice-wide traffic light.

When a latest durable evaluation matches the current durable structural basis, the UI may show stored gate lights only with observational wording equivalent to:

```text
Latest recorded evaluation on current durable basis: GREEN / YELLOW / RED
```

The implementation must not present a historical stored light as a freshly recomputed current gate truth.

## Full recorded-basis conflict rule

Two evaluation records are duplicate-basis records only when both:

```text
record_a.gate_refs == record_b.gate_refs
record_a.context == record_b.context
```

If their outputs conflict, projection fails closed with an integrity error.

Different full contexts are distinct observations even when baseline/lifecycle/governance structural identifiers match.

## Current durable structural-basis rule

`MATCHING_DURABLE_BASIS` means only that the currently queryable durable structural facts specified by Revision 3 match.

It does not claim every historical `HandoverContext` input is currently verified.

## Failure mapping

The presentation boundary distinguishes at minimum:

```text
NOT_FOUND
UNAVAILABLE
INTEGRITY_ERROR
```

No partial board or last-known-good cache may be served after integrity failure.

A Project board fails atomically when required Slice state is contradictory/corrupt.

---

# Required tests and evidence

Luna must implement deterministic tests covering the complete accepted design, including at minimum:

## Projection/domain separation

- every lifecycle phase maps to exactly one display lane;
- absent lifecycle maps to `NOT_STARTED`;
- exact lifecycle phase remains available;
- READY does not imply authorization;
- no Slice-wide TrafficLight exists;
- deterministic Project/card/gate/reason/execution ordering;
- parent/dependency relationships do not invent authority or blocker semantics.

## Evaluation observation semantics

- exact current lifecycle + current outgoing gate revision set + baseline -> `MATCHING_DURABLE_BASIS`;
- lifecycle mismatch -> `STALE_DURABLE_BASIS`;
- gate-set/revision mismatch -> `STALE_DURABLE_BASIS`;
- baseline mismatch -> `STALE_DURABLE_BASIS`;
- current gates with no record -> `NOT_EVALUATED`;
- no current-source gates -> `NOT_APPLICABLE`;
- stale durable-basis lights are not shown as current;
- lifecycle `STALE` remains distinct from `STALE_DURABLE_BASIS`;
- structurally equal tuple but different full `HandoverContext` -> distinct valid observations;
- identical full `gate_refs + HandoverContext` + identical output -> redundant evidence allowed;
- identical full basis + conflicting output -> integrity error;
- latest persistence sequence/record-ID rule selects the visible observation;
- rendered wording remains observational.

## SQLite snapshot/ownership

- one projection request observes one consistent SQLite read snapshot;
- a concurrent writer cannot produce a torn projection;
- each HTTP request receives its own SQLite connection;
- two or more concurrent GET requests do not share a connection;
- app state contains configuration/path, not an open connection;
- create/use/transaction completion/close occur in one synchronous ownership context;
- connection closes on success;
- connection closes on mapped failure;
- no request leaves a transaction open;
- no request runs migrations;
- no connection pool exists;
- no `check_same_thread=False` sharing workaround exists;
- rendering executes after authoritative DB access is complete.

## Integrity failures

Representative fail-closed tests must cover:

- lifecycle current/history disagreement;
- malformed persisted typed payload;
- mixed current outgoing-gate baselines;
- contradictory full-basis evaluation outputs;
- execution/evaluation inconsistency detectable by accepted loaders;
- Project/Slice definition-history inconsistency.

## Web adapter

- accepted GET routes;
- accepted HEAD behavior;
- unknown Project/Slice -> 404;
- POST/PUT/PATCH/DELETE -> 405 for the accepted board surface;
- dynamic HTML escaping;
- textual status in addition to color;
- loopback default;
- query filtering is display-only;
- no request mutates durable domain/persistence state;
- `/docs`, `/redoc`, `/openapi.json` not exposed;
- no equivalent generated documentation/schema alias configured.

## Dependency boundary

- only `fastapi` and `uvicorn` are new direct runtime dependencies;
- `httpx`, if added, is dev/test-only;
- no Jinja, ORM, React/Node, websocket, worker, queue, or connection-pool dependency is added;
- lockfile is deterministic and frozen.

---

# Required quality checks

Before submitting an implementation candidate, Luna must run and report:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

If dependencies were changed, Luna must update `uv.lock` first and then demonstrate the frozen sync above from the resulting candidate.

Passing checks are evidence only. They do not constitute acceptance.

GitHub Actions CI for the exact candidate SHA must succeed before independent implementation evaluation.

---

# Explicitly out of scope

Luna is not authorized to implement or redesign:

- React, TypeScript, Node, Vite, or another frontend framework/build chain;
- the final JSON API or versioned OpenAPI contract;
- board mutation controls;
- drag/drop lifecycle transitions;
- human approval/choice mutation workflows;
- Slice 1.6 behavior;
- agent execution;
- repository/provider mutation;
- GitHub synchronization changes unrelated to read projection;
- lifecycle or gate-engine semantic changes;
- new authoritative board state;
- board/projection persistence tables;
- SQLite schema migrations;
- async persistence architecture;
- connection pooling;
- websockets, SSE, polling workers, push refresh, notifications;
- authentication/public-network deployment/multi-user hosting;
- Jinja or another template-engine dependency;
- ORM introduction;
- generic dashboard/plugin architecture;
- opportunistic refactors outside the accepted change surface.

---

# Stop / escalation conditions

Luna must stop implementation and report an escalation if any of the following becomes necessary:

- a schema migration;
- a lifecycle/governance/domain contract change;
- a new authority semantic;
- a materially broader production change surface;
- any additional direct runtime dependency beyond FastAPI/Uvicorn;
- any additional dev dependency beyond the explicitly optional `httpx` test-only allowance;
- disabling SQLite thread protection or sharing one connection across requests;
- a connection pool;
- async persistence redesign;
- React or final JSON API work;
- provider/repository mutation;
- a future-slice capability;
- a contradiction between the accepted design revisions or existing accepted code.

Do not resolve a stop condition by silently broadening the slice.

---

# Implementation working branch and handoff

Recommended implementation branch:

```text
implementation/1.5-board-projection
```

The implementation agent must begin from exact baseline:

```text
2075be41962591552eded0597e243f0c1754b27f
```

At handoff, Luna must provide:

```text
baseline SHA
result/candidate SHA
executing model provenance
changed-file list
summary of implementation by design decision
new direct runtime dependencies
new dev/test dependencies
quality-check results
pytest summary
CI run/status for exact candidate SHA
deviations: NONE or explicit list
new-work-discovered: NONE or explicit list
```

The result is only an implementation candidate.

Luna may not accept its own result, merge/promote it as technically accepted, close Slice 1.5, open Slice 1.6, or authorize agent execution.

The candidate must be returned to an independent evaluator.

**Unblocked ≠ accepted.**
