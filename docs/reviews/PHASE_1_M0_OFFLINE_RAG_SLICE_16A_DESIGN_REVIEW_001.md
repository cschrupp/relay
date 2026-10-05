# Phase 1 M0 — Offline RAG Slice 16A Independent Design Review 001

**Document class:** Immutable independent design-evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project under test:** Offline RAG  
**Relay milestone:** Phase 1 Hard Stop — M0 Validation  
**Evaluation:** `RLY-P1-M0-S16A-DESIGN-EVAL-001`  
**Outcome:** `ACCEPT`  

## 1. Exact review subject

```text
Design authority:
RLY-P1-M0-S16A-DESIGN-AUTH-001 — AUTHORIZED

Authority commit:
5342a623b01a6c0a77b95b2e4721507606e8c06a

Design record:
RLY-P1-M0-S16A-DESIGN-001

Design commit:
f06c3ec570cc7341d0ca30bef61fa2e0cb670624

Target repository:
cschrupp/offline-rag

Frozen target baseline:
c72215186524c9937de789adb1cf2056be13ea23
```

The review evaluates only the Slice-16A design. It does not authorize implementation or accept any implementation result.

## 2. Review criteria

The design was checked against:

1. `RLY-P1-M0-TASK-001` task selection and behavioral contract;
2. Human design authority `RLY-P1-M0-S16A-DESIGN-AUTH-001`;
3. Offline RAG `docs/slice16_portfolio_ui.md` pre-design frame at the frozen target SHA;
4. current `POST /v1/query` transport and `run_product_query(...)` application behavior;
5. current FastAPI application/lifespan/runtime ownership;
6. current worker ownership/cancellation seam;
7. current project dependency set;
8. current HTTP bind policy;
9. scope discipline and stop conditions;
10. testability and evaluation suitability for Phase-1 M0.

## 3. Boundary review — product/API seam

The most material question is whether the proposed HTML transport:

```text
GET  /ui
POST /ui/query
```

improperly bypasses the accepted Slice-15 product/API seam.

### Reviewer judgment

**It does not, provided D16A-03 and D16A-16 are implemented exactly.**

Reasoning:

- the Slice-16 pre-design frame defines the required architecture as Browser UI -> supported UI/backend interface -> `src/offline_rag/app/`;
- `run_product_query(...)` is the existing canonical app-layer product query use case behind `POST /v1/query`;
- the design does not create alternate retrieval/generation semantics;
- the HTML route is a presentation transport, not a second JSON/scientific query API;
- the design explicitly requires shared runtime readiness, capacity admission, owned-worker execution, disconnect cancellation, and operation release;
- the existing JSON endpoint remains a regression boundary and must retain its exact public semantics.

Therefore the phrase “consume the accepted Slice-15 product/API seam rather than bypass it” is satisfied by reusing the same accepted product use case and transport execution policy rather than requiring a loopback HTTP self-call from the server to its own `/v1/query` endpoint.

A server-to-self HTTP call would add failure/cancellation complexity without increasing semantic fidelity and is not required by the inherited Slice-16 architecture.

## 4. Scope review

### PASS — scientific boundary

The design forbids direct UI access to:

- Qdrant;
- retrievers;
- fusion/reranking;
- generator/model runtime;
- scientific configuration;
- snapshot/recovery selectors.

No scientific mutation is designed.

### PASS — bounded 16A capability

The design is limited to:

- corpus/question input;
- answer;
- citations;
- abstention states;
- safe errors;
- trace/snapshot provenance;
- minimal accessibility/security presentation.

16B–16E remain explicitly deferred.

### PASS — no hidden Slice 17/18 work

No regression-CI program, release packaging, portfolio claim promotion, or M7 closeout is bundled into the design.

## 5. Architecture review

### PASS — same-process ownership

The design correctly reuses the existing FastAPI application and `request.app.state.runtime`. It does not create a second runtime/resource owner.

### PASS — worker lifecycle

The design explicitly preserves the current owned-worker/capacity semantics and requires release only in `finally` after worker termination.

### PASS — application lifespan

No competing startup/shutdown lifecycle is introduced.

### PASS — same-origin delivery

The same-origin model avoids CORS and a second development server, consistent with the local/offline product boundary.

## 6. Dependency/build review

### PASS

The design adds no runtime or dev dependency and no Node/frontend toolchain.

This is mechanically plausible at the frozen baseline because the repository already contains:

- FastAPI;
- Uvicorn;
- `python-multipart`;
- pytest/ruff.

Server-rendered HTML therefore has a materially smaller change surface than an SPA for this M0 task.

## 7. Testability review

### PASS

The server-rendered decision provides deterministic pytest coverage for the exact states required by the M0 task:

- answered;
- citations;
- insufficient evidence;
- model abstention;
- errors;
- trace/snapshot provenance;
- input restrictions;
- XSS escaping;
- security headers;
- worker ownership;
- `/v1/query` regression.

The design does not depend on a browser automation stack to make these assertions.

A real local browser smoke remains supplemental rather than replacing deterministic tests.

## 8. Security review

### PASS

The design:

- treats model output and all externally influenced values as untrusted HTML text;
- requires escaping;
- forbids rendering raw exception/secret material;
- inherits the existing loopback-first bind policy;
- adds no external assets or analytics;
- specifies no-store/nosniff/referrer/CSP headers;
- adds no public-deployment claim.

No auth/RBAC redesign is necessary for this bounded local UI task.

## 9. Compatibility review

### PASS WITH REQUIRED REGRESSION EVIDENCE

The only accepted existing production code expected to need refactoring is the `/v1/query` transport coordinator so the HTML route can reuse identical owned-query execution semantics.

That is acceptable only because the design makes existing `/v1/query` behavior a hard regression boundary.

Implementation evaluation must fail closed if any public JSON API behavior changes unexpectedly.

## 10. Findings

### Blocking findings

```text
NONE
```

### Major findings

```text
NONE
```

### Non-blocking review notes

#### N001 — Keep the shared execution helper private and narrow

If implementation extracts a helper from `api/query.py`, it should coordinate the existing query operation only. It should not become a generalized command/workflow abstraction.

#### N002 — `/ui/query` is HTML transport only

Implementation must not expose it as a second documented machine-facing query API or give it extra product controls.

#### N003 — Preserve target-baseline discipline

Because the connected GitHub integration could not create the target design branch, an implementation agent must explicitly prove its branch begins from:

```text
c72215186524c9937de789adb1cf2056be13ea23
```

or stop for reauthorization if the implementation intentionally needs a later target baseline.

## 11. Review outcome

```text
RLY-P1-M0-S16A-DESIGN-EVAL-001 — ACCEPT
```

The design is internally coherent, bounded, implementable against the frozen target baseline, compatible with the accepted Slice-15 product boundary, and suitable as a real Phase-1 M0 governance subject.

It is ready for **Human design acceptance**.

This evaluation does not grant that acceptance and does not authorize implementation.

## 12. Governance state

```text
Phase 1 M0:
AUTHORIZED

M0 target:
Offline RAG — SELECTED

M0 task:
RLY-P1-M0-TASK-001 — SELECTED

Slice 16A design authority:
RLY-P1-M0-S16A-DESIGN-AUTH-001 — AUTHORIZED

Slice 16A design:
RLY-P1-M0-S16A-DESIGN-001 — COMPLETE

Independent design review:
RLY-P1-M0-S16A-DESIGN-EVAL-001 — ACCEPT

Human design acceptance:
NOT YET GRANTED

Implementation authorization:
NOT AUTHORIZED

Phase 2:
NOT OPEN

Relay agent execution:
NOT AUTHORIZED
```

**Independent reviewer ACCEPT != Human design acceptance != implementation authorization.**
