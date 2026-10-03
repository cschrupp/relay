# Slice 1.5 — Independent Implementation Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.5 — Board Projection  
**Evaluation ID:** `RLY-S15-EVAL-001`  
**Outcome:** `ACCEPT`  
**Authority:** `RLY-S15-AUTH-001`  
**Accepted design head:** `25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b`  
**Authorized implementation baseline:** `2075be41962591552eded0597e243f0c1754b27f`  
**Implementation commit:** `b529c7b1e4816cea0f4045a9d0efb8064984d0ed`  
**Evaluated candidate / exact subject:** `ff8df665f36afe60a2d44ee1ed0d735a0dcbc230`  
**Reviewer role:** Independent Slice 1.5 Implementation Evaluator

---

# 1. Evaluation decision

```text
ACCEPT
```

The exact candidate `ff8df665f36afe60a2d44ee1ed0d735a0dcbc230` satisfies the accepted Slice 1.5 Revision 1 + Revision 2 + Revision 3 design and the bounded implementation authorization `RLY-S15-AUTH-001`.

The candidate implements the first human-facing Relay board as a deterministic, read-only projection of governed durable state. No implementation finding requires product rework or architecture escalation.

This evaluation is technical acceptance evidence only. It does not itself constitute Human Authority technical acceptance, promotion to `main`, Slice 1.5 closure, Slice 1.6 opening, or agent-execution authorization.

---

# 2. Exact lineage and change surface

The evaluated candidate has the exact lineage:

```text
2075be41962591552eded0597e243f0c1754b27f
    authorized implementation baseline
        ↓
b529c7b1e4816cea0f4045a9d0efb8064984d0ed
    Slice 1.5 product implementation
        ↓
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
    bounded registry repair
```

The product implementation commit remains intact. The second commit changes only `.relay/registry.json` to repair a pre-existing living-projection registry mismatch introduced when the authorized baseline advanced `docs/CURRENT_BASELINE.md` without its corresponding registry advancement.

The full baseline-to-candidate surface is bounded to:

```text
.relay/registry.json
pyproject.toml
uv.lock
src/relay_engine/board/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
src/relay_engine/persistence/__init__.py
src/relay_engine/persistence/database.py
src/relay_engine/persistence/store.py
tests/unit/test_board_models.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_web.py
tests/integration/test_board_projection_sqlite.py
```

No unrelated production package, lifecycle engine, governance engine, repository-sync subsystem, provider integration, React/Node surface, or Slice 1.6 implementation was added.

---

# 3. Projection and authority-model conformance

The implementation preserves Relay's accepted authority model.

## Board projection models

The candidate introduces immutable, extra-forbid typed board values through the existing `DomainModel` contract.

It implements exactly six display-only lanes:

```text
NOT_STARTED
SHAPING
READY
DELIVERY
EVALUATION
TERMINAL
```

Lifecycle phase remains present on the projected card and is not replaced by lane identity.

No Slice-wide synthetic `TrafficLight` field is introduced.

The accepted evaluation-basis states are implemented exactly:

```text
MATCHING_DURABLE_BASIS
STALE_DURABLE_BASIS
NOT_EVALUATED
NOT_APPLICABLE
```

## READY versus authorization

READY remains a lifecycle phase only. The renderer explicitly states that lifecycle READY does not grant execution authorization, while current gate policy/evaluation evidence is displayed separately.

No board status, badge, route, or mutation converts READY into an authorization fact.

**Result:** CONFORMANT.

---

# 4. Deterministic projection service

`board/service.py` remains framework-independent and owns the accepted derivation semantics.

The evaluator verified:

- Project index projection;
- Project board projection;
- Slice detail projection;
- deterministic lane and card ordering;
- current outgoing gate selection from the latest revision per logical gate ID;
- filtering after complete projection construction so filters cannot hide integrity failures;
- lifecycle current/history replay through accepted persistence loaders;
- parent/dependency projection without invented blocker semantics;
- baseline and execution provenance projection;
- fail-closed handling of contradictory durable state.

The service does not import FastAPI and does not persist board state.

**Result:** CONFORMANT.

---

# 5. Evaluation-observation semantics

The implementation correctly preserves the Revision 3 distinction between historical evaluation identity and currently queryable durable structural basis.

## Full recorded basis

Duplicate/conflict identity is implemented as:

```text
same gate_refs
+
same full typed HandoverContext
```

Records with different `HandoverContext` values remain distinct historical observations even when structural gate/baseline/lifecycle/governance identifiers match.

Conflicting outputs on an identical full recorded basis raise `PersistenceIntegrityError` and fail the projection closed.

## Durable structural basis

The latest durable observation is compared against current lifecycle, current outgoing gate revisions, Slice identity, and current gate baseline.

A match produces `MATCHING_DURABLE_BASIS`; a mismatch produces `STALE_DURABLE_BASIS`.

The implementation does not claim that all historical `HandoverContext` inputs are currently verified.

## Presentation

Matching stored lights are labelled observationally as:

```text
Latest recorded evaluation on current durable basis: ...
```

Stale-basis lights are removed from current gate projections. Slice detail may show them only inside explicitly historical observation evidence.

Lifecycle validity `STALE` remains distinct from evaluation `STALE_DURABLE_BASIS`.

**Result:** CONFORMANT.

---

# 6. SQLite consistency and ownership

The candidate adds the accepted deferred `read_transaction()` boundary and narrow typed read helpers without a schema migration.

For one projection operation:

```text
request-owned RelayDatabase
    ↓
one BEGIN read transaction
    ↓
all authoritative reads
    ↓
complete immutable projection
    ↓
transaction ends
    ↓
connection closes
    ↓
HTML rendering
```

The evaluator verified:

- nested read transactions are rejected;
- exceptions roll back active read transactions;
- busy/SQLite failures remain inside the persistence error taxonomy;
- lifecycle reads still replay history and detect disagreement;
- gate/evaluation/execution helper ordering is deterministic;
- one concurrent writer cannot create a torn board projection;
- board projection does not mutate semantic durable tables.

No connection pool or `check_same_thread=False` workaround is present.

**Result:** CONFORMANT.

---

# 7. FastAPI request boundary

The FastAPI adapter stores only an explicit database path in application state.

Each accepted GET/HEAD request opens its own `RelayDatabase` with:

```text
apply_migrations=False
```

and closes it before rendering.

The connection open, projection, transaction completion, and close occur in one synchronous callable execution context for that request. The adapter does not transfer an open SQLite connection between threads.

The accepted local route surface is exactly:

```text
GET/HEAD /
GET/HEAD /projects/{project_id}
GET/HEAD /projects/{project_id}/slices/{slice_id}
```

POST/PUT/PATCH/DELETE are rejected by the framework for those resources.

The executable binds to:

```text
127.0.0.1
```

by default.

Framework-generated API surfaces are disabled:

```text
/docs
/redoc
/openapi.json
```

No websocket, SSE, worker, polling loop, connection pool, mutation endpoint, or API-generalization layer was introduced.

**Result:** CONFORMANT.

---

# 8. HTML and accessibility boundary

The implementation uses direct server-rendered HTML/CSS with no JavaScript or template-engine dependency.

Dynamic durable values and query text are escaped. Internal route components are URL-quoted. Durable Markdown is not rendered as HTML.

The board provides:

- semantic headings and `main`/`nav` landmarks;
- keyboard-operable links/forms;
- visible focus styling;
- text labels in addition to traffic-light color;
- a single-column narrow-screen layout;
- explicit empty states and fail-closed error pages.

Slice detail exposes exact lifecycle, definition revision, current/historical gate evidence, full recorded `HandoverContext`, baseline commit provenance, and execution records without treating them as new authority.

**Result:** CONFORMANT.

---

# 9. Dependency and tooling boundary

The only new direct runtime dependencies are:

```text
fastapi
uvicorn
```

`httpx` is present only in the development/test dependency group, as separately permitted by `RLY-S15-AUTH-001`.

No Jinja, ORM, React/Node, websocket, worker/queue, or connection-pool dependency was added.

The accepted existing Python/tooling boundary remains intact.

**Result:** CONFORMANT.

---

# 10. Integrity and evidence coverage

The implementation test surface covers the accepted high-risk semantics, including:

- every lifecycle phase -> exact display lane;
- no lifecycle -> `NOT_STARTED`;
- READY distinct from execution authority;
- deterministic Project/card/gate/reason/execution ordering;
- current outgoing gate revision selection;
- matching/stale/not-evaluated/not-applicable evaluation states;
- full-context-distinct evaluation observations;
- identical-full-basis conflict failure;
- lifecycle current/history corruption;
- malformed persisted typed payloads;
- Project/Slice definition-history corruption;
- mixed current gate baselines;
- execution/evaluation contradiction;
- single read snapshot under a concurrent writer;
- request-scoped connection creation and close;
- separate concurrent request connections;
- close after success, not-found, unavailable, and integrity failure;
- rendering after connection close;
- no request migrations;
- disabled generated documentation routes;
- accepted HTTP method behavior;
- display-only search that cannot suppress integrity checking;
- dynamic HTML escaping and textual status labels;
- loopback executable configuration;
- dependency boundaries.

**Result:** SUFFICIENT.

---

# 11. Registry repair assessment

The original implementation candidate `b529c7b1e4816cea0f4045a9d0efb8064984d0ed` exposed a pre-existing canonical registry mismatch:

```text
.relay/registry.json
    current-baseline revision 33
    old digest

versus

docs/CURRENT_BASELINE.md
    bytes already changed at authorized baseline 2075be41...
```

The product implementation did not cause this mismatch.

The repaired candidate advances the candidate branch's current-baseline registry entry to revision 34 with a new ArtifactId and the exact digest of the already-existing document bytes. The repair changes no product source or accepted design semantics, and the repository-contract validation now passes.

This evaluation accepts the repaired candidate as the exact technical subject.

A separate canonical-main reconciliation remains required during later Human Authority acceptance/finalization because `main` has subsequently advanced its own `CURRENT_BASELINE.md` to the implementation-authorized state. That future synchronization is not a defect in the evaluated implementation candidate and must not be silently folded into technical evaluation.

---

# 12. Quality and CI evidence

Exact GitHub Actions evidence:

```text
Workflow: CI
Run: 37097340325 (#297)
Head SHA: ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
Conclusion: SUCCESS
Python: 3.14.8
Frozen sync: PASS
Ruff format: PASS
Ruff lint: PASS
Pyright: PASS — 0 errors / 0 warnings
pytest: PASS — 556 passed
uv build: PASS
```

The Human/implementation-agent handoff additionally reports `git diff --check` PASS on the exact candidate.

The prior CI failure on `b529c7b1...` is not implementation evidence against the board code: all board suites passed there as well, and the only failure was the pre-existing repository registry digest mismatch later repaired at `ff8df665...`.

---

# 13. Implementation model provenance

```text
Preferred model under RLY-S15-AUTH-001:
GPT-5.6 Luna

Reported executing model:
GPT-6 Codex runtime
```

This is a recorded provenance deviation, not an implementation defect. The authorization explicitly permits a differing executing model when the deviation is recorded.

---

# 14. Scope result

```text
Architecture escalation: NONE
Unauthorized product scope expansion: NONE IDENTIFIED
Schema migration: NONE
New direct runtime dependencies beyond FastAPI/Uvicorn: NONE
React/Node work: NONE
Slice 1.6 work: NONE
Agent execution: NONE
Repository/provider mutation behavior: NONE
Implementation rework required: NO
```

---

# 15. Governance consequence

The independent implementation-evaluation gate is complete with:

```text
RLY-S15-EVAL-001 — ACCEPT
```

Current state:

```text
Slice 1.5:
OPEN

Design:
ACCEPTED

Implementation authorization:
RLY-S15-AUTH-001 — AUTHORIZED

Exact evaluated candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
NOT YET GRANTED

Promotion / canonical finalization:
NOT AUTHORIZED BY THIS EVALUATION

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

The next governed action is Human Authority technical acceptance of the exact evaluated candidate. Canonical-main documentation/registry reconciliation and Slice 1.5 closure remain separate later actions.

**Unblocked ≠ accepted by Human Authority.**
