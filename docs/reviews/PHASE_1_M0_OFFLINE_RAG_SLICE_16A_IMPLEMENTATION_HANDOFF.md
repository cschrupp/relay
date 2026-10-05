# Phase 1 M0 — Offline RAG Slice 16A Implementation Handoff

**Document class:** Durable implementation handoff  
**Status:** AUTHORIZED FOR EXTERNAL IMPLEMENTATION  
**Date:** 2026-10-05  
**Authority:** `RLY-P1-M0-S16A-IMPL-AUTH-001 — AUTHORIZED`  
**Authority commit:** `06361f22fa721d73c9987a9dbef5b67a4797669a`

## 1. Exact implementation basis

```text
Target repository:
cschrupp/offline-rag

Frozen baseline:
c72215186524c9937de789adb1cf2056be13ea23

Accepted design:
RLY-P1-M0-S16A-DESIGN-001
f06c3ec570cc7341d0ca30bef61fa2e0cb670624

Independent design evaluation:
RLY-P1-M0-S16A-DESIGN-EVAL-001 — ACCEPT
533d677c80e41db3472d1539554dc30015f56dec

Human design acceptance:
RLY-P1-M0-S16A-DESIGN-ACCEPT-001 — ACCEPTED
48719fdd050e8d9f183e6e3401af160ee35a432f

Implementation authority:
RLY-P1-M0-S16A-IMPL-AUTH-001 — AUTHORIZED
06361f22fa721d73c9987a9dbef5b67a4797669a
```

## 2. Bootstrap

The implementation agent must work in `cschrupp/offline-rag` and prove the exact governed basis before changes:

```bash
git fetch origin
git checkout -B implementation/16a-browser-query-experience c72215186524c9937de789adb1cf2056be13ea23
git rev-parse HEAD
```

Expected exact output:

```text
c72215186524c9937de789adb1cf2056be13ea23
```

If not exact, stop. Do not rebase or merge later `main`.

## 3. Implementation objective

Implement the accepted **Slice 16A — Minimal Browser Query Experience**:

```text
same FastAPI process
same origin
GET /ui
POST /ui/query
server-rendered HTML
minimal repository-owned CSS
no client-side JavaScript requirement
no new dependency/toolchain
canonical run_product_query(...) semantics
```

The implementation is a browser adapter over the existing product/application layer. It is not a new RAG pipeline or API generation surface.

## 4. Expected production files

### New

```text
src/offline_rag/api/ui.py
```

Expected responsibilities:

- define an APIRouter for `/ui` and `/ui/query`;
- parse strict form input;
- build presentation-only page state;
- render escaped HTML;
- add accepted security headers;
- call the canonical shared query execution seam;
- preserve normative AppError HTTP status.

### Existing, bounded modifications

```text
src/offline_rag/api/app.py
src/offline_rag/api/query.py
```

`app.py`:

- import/register UI router only.

`query.py`:

- optionally extract a private helper for owned query execution so JSON and HTML transports share the same readiness/admission/worker/release behavior;
- keep `/v1/query` public semantics unchanged.

A tiny import/export adjustment elsewhere in `src/offline_rag/api/` is acceptable only if mechanically necessary.

Do not change app/domain/retrieval/science layers.

## 5. Recommended internal shape

Keep the implementation small and explicit. A reasonable shape is:

```python
# query.py
async def execute_product_query_owned(
    request: Request,
    *,
    runtime: ApplicationRuntime,
    corpus: str,
    question: str,
) -> ProductQueryResponse:
    ...
```

or an equivalent private API-layer helper.

Both transports should call the same helper:

```text
POST /v1/query
  -> request validation
  -> execute_product_query_owned(...)
  -> result.as_dict()

POST /ui/query
  -> strict form validation
  -> execute_product_query_owned(...)
  -> presentation projection
  -> escaped HTML
```

Do not move product semantics out of `run_product_query(...)`.

Do not introduce a generic command/service framework.

## 6. Strict HTML form contract

`GET /ui` renders a form with exactly:

```text
corpus
question
submit control
```

No scientific/runtime configuration field is allowed.

`POST /ui/query` must reject:

```text
missing corpus
missing question
empty corpus
empty question
question > MAX_QUESTION_CHARS
unexpected form field
duplicate corpus field
duplicate question field
```

Do not rely on `Form(...)` behavior if it silently accepts duplicate/unexpected keys. Inspect the parsed form/multidict and enforce the accepted contract explicitly.

Reuse existing canonical validators where possible; do not create conflicting product validation semantics.

## 7. Page-state model

Use a presentation-only model or equivalent local structure:

```text
idle
answered
insufficient_evidence
model_abstain
error
```

Suggested fields:

```text
state
corpus
question
answer
citations
trace_id
snapshot_id
product_mode_id
error_code
error_message
retryable
```

This is not persisted and must not become a domain model.

## 8. HTML renderer requirements

The renderer must:

- produce complete valid-enough HTML for browser display;
- render labels for corpus/question;
- use semantic headings;
- render answer and citations distinctly;
- render abstention states distinctly;
- render errors distinctly;
- retain the user's submitted corpus/question for context when safe;
- show trace and snapshot provenance;
- use no external assets;
- require no JavaScript;
- use repository-owned CSS only.

All externally influenced text must pass through HTML escaping. Prefer Python stdlib `html.escape(..., quote=True)` or an equivalently obvious escaping primitive.

Never interpolate unescaped:

```text
user question
corpus
model answer
citation fields
error code/message
trace/snapshot/product_mode identities
```

No model-generated HTML is trusted.

## 9. Citation rendering

Render only the existing public citation projection fields:

```text
evidence_unit_id
document_id
source_chunk_id
kind
section_path
page_start
page_end
line_start
line_end
clipped
```

It is acceptable to omit empty optional location values from display.

Do not:

- fetch document content;
- infer source text;
- invent page/section labels;
- reconstruct citations client-side;
- expose internal scientific trace objects.

## 10. Status rendering

### answered

Must show:

```text
returned answer
returned citations
trace_id
snapshot_id
```

May show `product_mode_id` as diagnostic provenance.

### insufficient_evidence

Must show explicit insufficient-evidence status and no generated answer/citations.

### model_abstain

Must show explicit model-abstain status and no generated answer/citations.

The two abstention states must be visibly distinguishable.

## 11. Error handling

For `AppError`:

- render from `AppError.to_error_response()` / canonical safe projection;
- preserve `exc.http_status` where non-null;
- display only safe code/message/retryability/trace and safe identity detail if deliberately included;
- never expose `repr(exc)`, traceback, cause, headers, secrets, paths, or raw provider output.

For a non-HTTP terminal cancellation whose browser connection is already gone, preserve the existing disconnect behavior rather than inventing a UI error response.

Unexpected exceptions should continue to map through the existing safe internal-error boundary; do not expose them in HTML.

## 12. Query ownership and cancellation

Preserve exactly the accepted operational sequence:

```text
runtime.require_ready()
operation = runtime.operations.admit_query()
run_owned_worker(
    request=request,
    operation=operation,
    worker=... run_product_query(...),
    watch_disconnect=True,
)
runtime.operations.release(operation) in finally
```

Requirements:

- one admitted query operation per query;
- no detached task;
- no background execution;
- no second timeout model;
- no early release while worker still runs;
- no second ApplicationRuntime/resource pool;
- UI disconnect follows the existing cooperative cancellation path.

## 13. Security headers

Every HTML response from `/ui` and `/ui/query` must include:

```text
Cache-Control: no-store
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'
```

and a correct HTML Content-Type.

If CSS is moved to a same-origin static asset without a build system, `style-src 'self'` may be used only if packaging/tests prove availability. Inline bounded CSS is preferred for this slice.

No external URL should appear in HTML asset/script/font/style references.

## 14. Accessibility/minimum UX

Include:

- `<label for=...>` for both inputs;
- logical heading structure;
- a descriptive submit button;
- semantic citation list/details;
- text labels for status (not color-only meaning);
- browser-default or explicit visible focus state.

Do not turn 16A into visual-polish work.

## 15. `/v1/query` regression requirements

If extracting a helper from `query.py`, prove the JSON API remains unchanged.

At minimum test:

```text
valid answered response shape
valid abstention response
extra JSON field remains rejected
request validation/status mapping unchanged
AppError envelope unchanged
trace semantics unchanged
capacity ownership/release unchanged
disconnect behavior unchanged where existing test seam supports it
```

Do not change `ProductQueryRequest`, `ProductQueryResponse`, or application-layer product statuses unless mechanically unnecessary whitespace/import changes only.

## 16. Mandatory UI tests

Add deterministic tests covering:

### Initial page

```text
GET /ui -> 200
HTML content type
form method POST
form target /ui/query
only corpus/question product inputs
no query execution
no trace allocation
security headers present
```

### Answered rendering

Controlled canonical result:

```text
status=answered
answer text visible
citation identity/provenance visible
trace_id visible
snapshot_id visible
answered state visible
```

### Insufficient evidence

```text
status=insufficient_evidence
explicit state visible
no fabricated answer
no fabricated citation
trace/snapshot provenance visible
```

### Model abstain

```text
status=model_abstain
explicit distinct state visible
no fabricated answer/citation
```

### Error rendering

At least:

```text
request_invalid
one runtime/provider error, e.g. generation_unavailable or runtime_not_ready
```

Prove:

```text
correct HTTP status
safe code/message visible
retryability if rendered
trace visible when present
secret/internal payload absent
```

### Strict form validation

Prove rejection of:

```text
missing question
empty question
over-limit question
extra field
duplicate field
```

Include corpus invalidity/missing coverage appropriate to current canonical validator behavior.

### Escaping/XSS

Use adversarial strings in multiple surfaces, e.g.:

```text
<script>alert(1)</script>
"><img src=x onerror=alert(1)>
```

Test at least:

```text
question
answer
one citation field
one identity/error display field
```

Assert escaped text is present and executable/raw markup is absent.

### Owned-worker semantics

Prove operation release on:

```text
success
AppError
```

and preserve existing cancellation/disconnect semantics where practical through the existing helper seams.

### No-new-dependency boundary

Compare candidate to frozen baseline and prove:

```text
pyproject dependency lists unchanged
no package.json
no package-lock.json
no yarn.lock
no pnpm-lock.yaml
no external CDN/script/font reference
```

## 17. Suggested test implementation strategy

Prefer FastAPI/Starlette `TestClient` or the repository's existing ASGI test approach, with controlled runtime/query doubles rather than running real embedding/generation models in deterministic tests.

Tests should isolate the UI transport and presentation behavior while preserving at least one integration-level proof that the route reaches the canonical query execution seam.

Do not mock away the exact behavior under test.

## 18. Local smoke evidence

When the accepted local stack is available, perform one practical smoke run:

```text
start existing Offline RAG server
open /ui
submit a real corpus + question
observe answered or legitimate abstention
capture exact candidate SHA
capture returned trace_id
capture snapshot_id
```

Record whether citations were displayed for an answered result.

If the model/corpus environment is unavailable, state:

```text
local smoke: NOT EXECUTED — environment unavailable
```

with the concrete reason. This is an evidence limitation, not automatic implementation failure if deterministic tests are complete.

## 19. Dependencies / packaging / deployment

Do not modify dependency declarations or lock dependencies to add anything.

Do not introduce:

```text
Jinja2
frontend framework
Node/npm
CSS framework
external fonts
analytics
CDN
separate web service
new port
CORS configuration
TLS/public deployment
```

Python stdlib rendering is sufficient.

Container/package modifications are not expected. If implementation discovers they are required merely to expose `/ui`, stop and report why instead of expanding scope.

## 20. Authorized change-surface expectation

Expected candidate should be approximately:

```text
NEW    src/offline_rag/api/ui.py
MODIFY src/offline_rag/api/app.py
MODIFY src/offline_rag/api/query.py    # only if sharing owned execution helper
NEW    bounded UI tests
MODIFY bounded existing query tests    # only if helper extraction requires it
```

A candidate touching retrieval, generation, domain, storage, configuration, deployment, Docker, docs claims, evaluation science, or unrelated files requires explicit explanation and likely stop/escalation.

## 21. Quality gates

Run from a clean checkout at the exact candidate SHA:

```bash
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pytest
git diff --check
```

Also run any repository-owned canonical gate discovered at implementation time, but do not add new tooling.

Report exact test count.

If GitHub Actions exists and runs for the pushed branch/candidate, report exact run ID and exact candidate SHA. If not available, report that explicitly.

## 22. Candidate push

Push only the implementation candidate branch:

```text
implementation/16a-browser-query-experience
```

Do not merge to `main`.

Do not update Offline RAG roadmap/milestone acceptance status as if the implementation were accepted.

## 23. Hard-stop conditions

Stop and return to Human Authority if any of these arise:

```text
baseline SHA mismatch
later main needed
new dependency/toolchain needed
new backend JSON endpoint needed
/v1/query semantic change needed
new status/citation semantics needed
new auth/RBAC or public-host security design needed
separate process/port needed
direct UI-to-Qdrant/retriever/generator access needed
Slice 16B+ capability needed
unrelated refactor needed
accepted design contradicts actual target code
```

Do not solve a governance/design stop by silently widening implementation.

## 24. Final Codex handoff

Return exactly enough provenance for independent evaluation:

```text
authorized frozen baseline SHA
candidate SHA
branch
requested executor/model
actual executing model if exposed
model provenance deviation if any
complete changed-file list
implementation summary mapped to D16A-01..D16A-20
confirmation /v1/query public semantics unchanged
runtime dependency changes: NONE or explicit deviation
dev/test dependency changes: NONE or explicit deviation
frontend toolchain changes: NONE or explicit deviation
external asset/CDN changes: NONE or explicit deviation
quality-gate commands + results
pytest exact passed/failed/skipped count
git diff --check result
exact GitHub Actions run/status if available
local smoke result, trace_id, snapshot_id if executed
deviations: NONE or exact list
new work discovered: NONE or exact list
```

Candidate only.

Do not independently evaluate/accept it, do not grant Human technical acceptance, do not declare Slice 16A or M0 complete, do not open Phase 2, and do not authorize/execute Relay agents.
