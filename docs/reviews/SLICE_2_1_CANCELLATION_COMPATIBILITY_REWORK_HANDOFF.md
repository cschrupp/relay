# Relay — Slice 2.1 OpenCode Cancellation Compatibility Rework Handoff

**Document class:** Immutable implementation rework handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Record:** `RLY-S21-IMPL-REWORK-HANDOFF-003`

## Authority

Implementation remains under existing Human Authority:

```text
RLY-S21-IMPL-AUTH-001 — AUTHORIZED
```

Independent live evaluation:

```text
RLY-S21-SIDECAR-EVAL-010R3 — REWORK
```

Exact rework baseline:

```text
f9a4790c6343561b462d521008c197d776e9ebcf
```

Accepted Slice 2.1 design remains unchanged.

## Objective

Correct only the OpenCode V2 cancellation-response compatibility defect exposed by live Run 010r3 and the deterministic mock/tests that encoded the wrong success response.

Preserve every behavior already accepted and live-proven through D21-11.

## Authorized production surface

Modify only:

```text
src/relay_engine/agent_runtime/opencode.py
```

and the already-authorized runtime-focused deterministic tests, primarily:

```text
tests/unit/test_opencode_runtime.py
```

No new dependency.

No schema, persistence, lifecycle, governance, board, repository integration, permission-model, provider/model selection, or Phase 3 change.

## 1. Establish exact pinned-beta cancellation contract

Before editing, inspect only non-secret exact-beta embedded/generated route/schema evidence corresponding to:

```text
OpenCode:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

Bind the correction to the exact interrupt endpoint:

```text
POST /api/session/{sessionID}/interrupt
```

Live Run 010r3 already establishes successful:

```text
HTTP 204 No Content
```

Determine whether the exact beta declares 204 as the sole success status or whether another explicit success representation is supported.

Do not infer from a newer upstream release if it differs from the pinned beta.

No live provider/model call is required or authorized for implementation rework.

## 2. Correct cancellation success normalization

The Relay-level contract remains:

```text
RuntimeCancelRequest
    -> RuntimeControlAck
```

A successful exact-beta interrupt response with no body must not be classified as transport failure.

For exact-beta HTTP 204 success, return an acknowledgment consistent with the already-accepted semantics:

```text
state:
REQUESTED

observed_runtime_status:
current known active status if safely known,
otherwise UNKNOWN
```

unless the adapter has already proven the execution terminal before issuing the request, in which case the existing `ALREADY_TERMINAL` behavior remains authoritative.

Do not attempt to parse JSON from a 204 response.

Preserve:

```text
404 -> NOT_FOUND
403 -> DENIED
timeout -> TIMEOUT
transport exception -> TRANSPORT
exact execution/session binding
idempotent cached acknowledgment
cancel serialization
```

If exact-beta schema proves an additional explicit success status, support only that proven success representation.

Do not generalize blindly to arbitrary 2xx responses.

## 3. Deterministic mock correction

Change the deterministic interrupt endpoint model to the exact pinned-beta success behavior.

At minimum the main successful cancellation fixture must return:

```text
HTTP 204
empty body
```

and the candidate test must prove:

```text
cancel() returns RuntimeControlAckState.REQUESTED
no JSON parse is attempted
observed runtime status is preserved/UNKNOWN as appropriate
second identical cancel returns the cached acknowledgment
only one interrupt POST occurs
```

Add a regression proving HTTP 204 cannot normalize to `TRANSPORT`.

Retain separate deterministic coverage for:

```text
404 -> NOT_FOUND
403 -> DENIED
timeout
transport exception
binding mismatch
unknown process-local binding
already-terminal local state
concurrent/idempotent cancellation
```

If the exact beta still supports a distinct 200 success body, preserve it only with exact-beta evidence and add explicit separate coverage.

## 4. Preserve live-proven behavior

Do not regress:

- exact health/runtime compatibility;
- session creation;
- observer-before-prompt;
- root-level prompt schema;
- one-prompt guard;
- execution wake;
- `runtime_invocation=None` provenance semantics;
- exact provider/model binding;
- permission denials;
- allowed fixture edit;
- inspection/diff;
- event continuity;
- credential containment;
- provider/model failure normalization;
- resume capability absence.

No changes are authorized outside the cancellation path and directly related deterministic mock/test behavior unless mechanically necessary.

## 5. Required deterministic tests

At minimum prove:

```text
204 interrupt success -> REQUESTED
204 response body is not parsed
idempotent repeated cancel -> cached ack / one POST
terminal-before-cancel -> ALREADY_TERMINAL without unnecessary semantic change
404 -> NOT_FOUND
403 -> DENIED
timeout -> TIMEOUT
transport failure -> TRANSPORT
binding mismatch -> REQUEST_CONFLICT
unknown binding -> SESSION_BINDING_REQUIRED
```

Run focused cancellation tests plus the full runtime suite.

## 6. Quality gate

Run:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

No live OpenCode server, provider, model, or D21 calls during this implementation step.

## 7. Required implementation report

Return:

```text
branch:
<exact>

exact starting SHA:
f9a4790c6343561b462d521008c197d776e9ebcf

successor SHA:
<exact>

changed files:
<exact>

exact-beta interrupt schema evidence:
<concise>

supported successful interrupt status/body after correction:
<exact>

RuntimeControlAck mapping for 204:
<exact>

focused cancellation tests:
<exact>

full pytest:
<exact>

ruff format:
<exact>

ruff lint:
<exact>

pyright:
<exact>

build:
<exact>

git diff --check:
<exact>

exact-head CI:
<exact or pending>

live OpenCode/provider/model calls:
NONE

candidate/source scope:
ONLY opencode cancellation + deterministic tests
```

Do not ACCEPT your own work.

Do not run the live sidecar.

Do not perform Human technical acceptance, promotion, Slice closure, Slice 2.2, or Phase 3 work.

A successor candidate requires independent deterministic evaluation before any later SHA-bound live sidecar authorization.
