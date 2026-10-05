# Phase 1 M0 — Offline RAG Slice 16A Implementation Authorization

**Document class:** Immutable Human implementation-authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Relay milestone:** Phase 1 Hard Stop — M0 Validation  
**Target project:** Offline RAG  
**Record:** `RLY-P1-M0-S16A-IMPL-AUTH-001`  
**Outcome:** `AUTHORIZED`

## 1. Human authority

The Human Authority explicitly authorized:

```text
Authorize Offline RAG Slice 16A implementation for Phase 1 M0 validation
```

This record authorizes **implementation only** of the exact Human-accepted Slice 16A design below.

It does **not** constitute implementation evaluation, Human technical acceptance, accepted-result promotion, M0 acceptance/completion, Phase 2 opening, or Relay agent-execution authority.

## 2. Exact authority basis

```text
Phase 1 M0 validation authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

M0 target:
RLY-P1-M0-TARGET-001 — Offline RAG — SELECTED

M0 task:
RLY-P1-M0-TASK-001 — SELECTED

Target repository:
cschrupp/offline-rag

Exact frozen implementation baseline:
c72215186524c9937de789adb1cf2056be13ea23

Design authority:
RLY-P1-M0-S16A-DESIGN-AUTH-001 — AUTHORIZED

Accepted design artifact:
RLY-P1-M0-S16A-DESIGN-001
commit f06c3ec570cc7341d0ca30bef61fa2e0cb670624

Independent design evaluation:
RLY-P1-M0-S16A-DESIGN-EVAL-001 — ACCEPT
commit 533d677c80e41db3472d1539554dc30015f56dec

Human design acceptance:
RLY-P1-M0-S16A-DESIGN-ACCEPT-001 — ACCEPTED
commit 48719fdd050e8d9f183e6e3401af160ee35a432f
```

The implementation must start from the exact frozen Offline RAG SHA above. Later movement of target `main` does not silently change this basis.

If the target baseline cannot be checked out exactly or relevant upstream changes make the accepted design unsafe/inapplicable, implementation must stop and return to Human Authority rather than rebase or widen scope.

## 3. Authorized implementation objective

Implement **Offline RAG Slice 16A — Minimal Browser Query Experience** as accepted in `RLY-P1-M0-S16A-DESIGN-001`.

The implementation must provide a minimal same-origin browser query experience over the already accepted Slice-15 product semantics while preserving the canonical application-layer query path.

The authorized architecture is:

```text
Browser
  -> GET /ui | POST /ui/query
  -> same FastAPI process / same origin
  -> API-layer UI adapter
  -> existing ApplicationRuntime
  -> existing query-capacity + owned-worker semantics
  -> run_product_query(...)
  -> accepted Offline RAG application/domain/infrastructure
```

No alternative frontend architecture is authorized by this record.

## 4. Authorized production change surface

Expected new production file:

```text
src/offline_rag/api/ui.py
```

Authorized existing production files, only as mechanically required by the accepted design:

```text
src/offline_rag/api/app.py
src/offline_rag/api/query.py
```

A tiny existing import/export file may be changed only if mechanically required for router registration and does not widen the product surface.

No other production package is authorized without a design-stop escalation.

## 5. Authorized test surface

Tests may be added/updated only as needed to prove the accepted design and preserve `/v1/query` regression behavior.

Expected test area:

```text
tests/unit/api/test_ui.py
```

or the repository's nearest equivalent bounded test path.

Existing query/API tests may be minimally updated where required by a shared execution helper extraction.

No unrelated test cleanup is authorized.

## 6. Required functional behavior

### 6.1 `GET /ui`

Must:

- return `200` HTML;
- render a browser form;
- expose exactly product inputs `corpus` and `question` plus submit control;
- submit via `POST /ui/query`;
- execute no product query;
- allocate no query trace;
- mutate no product/corpus state.

### 6.2 `POST /ui/query`

Must:

- accept form data containing exactly `corpus` and `question`;
- reject missing, empty, duplicate, or unexpected query fields deterministically;
- preserve existing server-authoritative question validation and max length;
- use the canonical product query semantics;
- preserve runtime readiness, query-capacity admission, owned-worker execution, disconnect cancellation, and operation release;
- render exactly one terminal browser state.

### 6.3 Answered state

For `status == "answered"`:

- render the returned answer as escaped text;
- render returned validated citation provenance;
- render returned `trace_id`;
- render returned `snapshot_id`;
- preserve the backend status as answered;
- do not invent source attribution or citation data.

### 6.4 Abstention states

For `insufficient_evidence` and `model_abstain`:

- render distinct explicit states;
- render no fabricated answer;
- render no fabricated citation;
- keep trace/snapshot provenance available when returned.

### 6.5 Error state

Product/application failures must:

- render an error state, never an answered state;
- use canonical safe product error information only;
- preserve normative HTTP status where one exists;
- expose trace identity when safely present;
- never render stack traces, exception internals, secret material, request headers, paths, or unsanitized provider details.

### 6.6 HTML safety

All externally influenced values must be HTML-escaped, including:

```text
corpus
question
answer
citation fields
trace_id
snapshot_id
product_mode_id
safe error fields
```

No model-generated or user-supplied HTML may be interpreted as trusted markup.

### 6.7 Browser security headers

HTML responses must include the accepted defensive policy at minimum:

```text
Content-Type: text/html; charset=utf-8
Cache-Control: no-store
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Content-Security-Policy:
  default-src 'none';
  style-src 'unsafe-inline';
  form-action 'self';
  base-uri 'none';
  frame-ancestors 'none'
```

If inline CSS is removed, `style-src 'self'` may replace `'unsafe-inline'` without redesign.

No external font/script/CDN/network asset is authorized.

## 7. Canonical execution seam

The UI must reuse the same canonical `run_product_query(...)` application-layer use case used by `POST /v1/query`.

Implementation may extract a **private API-layer coordination helper** from `src/offline_rag/api/query.py` so both transports share:

```text
runtime.require_ready()
operation = runtime.operations.admit_query()
run_owned_worker(... watch_disconnect=True ...)
runtime.operations.release(operation) in finally
```

The helper may coordinate execution only. It must not define a second product/query semantic contract.

The UI must not directly construct or call:

```text
Qdrant client
retrievers
fusion/reranker implementation
generator/model runtime
snapshot internals
scientific pipeline objects
```

## 8. `/v1/query` is a regression boundary

Existing JSON API behavior must remain unchanged, including:

```text
request schema
extra-field rejection
success response shape
error envelope/status mapping
disconnect behavior
capacity ownership
trace semantics
```

No accepted Slice-15 response field may be removed or reinterpreted.

## 9. Dependency and build authority

Expected deltas:

```text
runtime dependencies: NONE
dev/test dependencies: NONE
Node/npm/frontend toolchain: NONE
external assets/CDNs: NONE
new runtime process/service: NONE
new listening port: NONE
```

Existing `python-multipart` is sufficient for HTML form parsing.

Any dependency/toolchain addition is a **design stop** and is not authorized here.

## 10. Explicitly forbidden work

This authority does not permit:

```text
changes to retrieval/fusion/reranking/context/generation science
embedding/model configuration changes
new product statuses
citation semantic changes
new JSON query API
new query modes
algorithm selectors
snapshot pinning
recovery selectors
corpus ingest/admin UI
Slice 16B/16C/16D/16E
Slice 17
Slice 18
PORTFOLIO_DEMO claim promotion
Milestone 7 closeout
Node/npm/Vite/React/Vue/Svelte/HTMX
new authentication/RBAC
public/cloud deployment redesign
new runtime/service/process
unrelated debt cleanup
Relay Phase 2 capability
Relay agent execution
```

## 11. Required deterministic verification

The candidate must include evidence/tests covering the accepted V16A-01 through V16A-12 contract, including:

```text
GET /ui initial page / no query or trace
answered rendering
citation rendering
insufficient-evidence rendering
model-abstain rendering
safe error rendering + status preservation
strict form contract
missing/empty/over-limit/extra/duplicate input rejection
XSS/HTML escaping
security headers
canonical query seam
/v1/query regression
owned-worker/capacity release semantics
no-new-dependency / no-external-asset boundary
```

A real local smoke/demo query should supplement deterministic tests when the accepted product environment is available. If unavailable, record that limitation explicitly; do not fabricate smoke evidence.

## 12. Required quality gates

At minimum run on the exact candidate SHA:

```bash
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

Also run any additional canonical repository gate that exists at implementation time. Do not add a new quality tool merely to satisfy this authority.

Run:

```bash
git diff --check
```

and report the result.

If GitHub Actions exists for the target repository/branch, obtain and report exact-SHA CI status. If no applicable workflow exists, report `NOT AVAILABLE`; do not invent CI evidence.

## 13. Branch and provenance requirements

The connected Relay reviewer does not have target-repository branch-write permission, so the implementation agent must create/push the target branch itself using its available repository credentials.

Authorized implementation branch name:

```text
implementation/16a-browser-query-experience
```

Bootstrap must prove exact basis before modifying files:

```bash
git fetch origin
git checkout -B implementation/16a-browser-query-experience c72215186524c9937de789adb1cf2056be13ea23
git rev-parse HEAD
```

The final command must return exactly:

```text
c72215186524c9937de789adb1cf2056be13ea23
```

Do not rebase onto a later `main` without new Human authority.

The implementation agent must report:

```text
requested executor/model
actual executing model if exposed
model provenance deviation if any
```

Executor/model identity is provenance only and does not itself confer governance authority.

## 14. Hard stop / escalation conditions

Stop before implementation or further mutation if any of the following becomes necessary:

- target baseline cannot be reproduced exactly;
- accepted design conflicts with target code;
- `/v1/query` semantics would need to change;
- product statuses/citations would need to change;
- new backend JSON endpoint is required;
- dependency or frontend toolchain addition is required;
- direct UI access below application/product layer is required;
- a new runtime/service/process/listening port is required;
- auth/RBAC/public deployment work is required;
- Slice 16B+ work is required;
- unrelated backend refactor is required beyond the bounded shared execution seam;
- later target-main changes must be incorporated for correctness.

In those cases, preserve the branch and return the exact blocker. Do not infer scope expansion.

## 15. Candidate handoff boundary

The implementation agent may produce and push an implementation candidate with evidence.

It may **not**:

- independently evaluate or accept the candidate;
- issue the M0 evaluator decision;
- grant Human technical acceptance;
- promote an accepted result;
- declare Slice 16A complete/accepted;
- declare M0 complete;
- open Phase 2;
- authorize or execute Relay agents.

**AUTHORIZED implementation != evaluated implementation != Human technical acceptance != M0 acceptance.**
