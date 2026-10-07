# Relay — Slice 2.1 OpenCode Execution-Wake Rework Handoff

**Document class:** Immutable implementation rework handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-IMPL-REWORK-HANDOFF-002`

## Authority

Implementation remains under existing Human Authority:

```text
RLY-S21-IMPL-AUTH-001 — AUTHORIZED
```

Independent live evaluation:

```text
RLY-S21-SIDECAR-EVAL-008 — REWORK
```

Exact rework baseline:

```text
5df1add9ed829a62a99d7f25f561a0f492ff5c73
```

Accepted Slice 2.1 design remains unchanged.

## Objective

Correct only the exact OpenCode V2 execution-wake semantics exposed by Run 008 and any directly related prompt-success invocation-provenance mismatch confirmed by the pinned beta.

Preserve all already accepted behavior.

## Authorized production surface

Modify only:

```text
src/relay_engine/agent_runtime/opencode.py
```

and the already-authorized deterministic runtime tests, primarily:

```text
tests/unit/test_opencode_runtime.py
```

No new dependency.

No schema, persistence, governance, lifecycle, board, repository integration, or Phase 3 change.

## Required pre-edit proof

Start from exact SHA:

```text
5df1add9ed829a62a99d7f25f561a0f492ff5c73
```

Verify clean tracked state.

Do not merge/rebase current main into the implementation branch.

## 1. Establish exact pinned-beta execution semantics

Before editing, use only non-secret local/generated/embedded schema or route evidence corresponding to exact:

```text
OpenCode:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

Establish exactly what the prompt endpoint means for:

```text
resume omitted
resume true
resume false
```

No provider/model call is needed or authorized for this implementation step.

If exact beta semantics cannot be established without guessing, STOP.

## 2. Correct normal open_execution semantics

The normal Relay `open_execution()` path must:

```text
establish observer
admit exactly one prompt
cause execution wake
return the exact handle
```

It must not intentionally request admit-only behavior.

Use the smallest exact-beta-compatible request correction.

If omission is the exact beta's normal wake behavior, prefer omitting `resume`.

Do not:

- submit a second prompt;
- call a separate resume operation to compensate;
- weaken the one-prompt guard;
- change Relay's public protocol;
- advertise RESUME capability.

## 3. Verify prompt-success response provenance

Inspect the exact beta's prompt-success schema.

Determine whether its generic response `id` is:

```text
a true runtime invocation ID
or
an admitted prompt/message/input ID
```

Only create `RuntimeInvocationRef.invocation_id` from a field proven to be a runtime invocation identity.

If no invocation identity is exposed, leave:

```text
runtime_invocation = None
```

Do not fabricate runtime invocation identity from a prompt/message/admission ID.

## 4. Deterministic mock correction

The mock must model the exact beta behavior sufficiently to prevent recurrence.

Required cases:

```text
resume false
    -> admission only
    -> no execution wake/event

normal open_execution request
    -> admission + execution wake/event
```

The normal candidate test must prove:

- observer established before prompt;
- exactly one prompt POST;
- request uses exact execution-starting semantics;
- no `resume: false` regression;
- allowed execution event follows only for execution-starting request.

Prompt success response must match the exact beta's semantic identity fields.

Do not fabricate `invocation-1` through a generic `id` unless exact beta evidence proves that field is an invocation ID.

## 5. Preserve accepted behaviors

Do not regress:

- root-level prompt body mapping;
- exact request/session binding;
- requested provider/model binding;
- observer-before-admission;
- one-prompt guard;
- timeout/transport uncertain-admission recovery;
- provisional exact handle;
- definite-rejection observer cleanup;
- HTTP 400 -> CONFIGURATION;
- HTTP 403 -> PERMISSION_DENIED;
- cancellation exact binding;
- inspection exact binding;
- event continuity;
- credential safety.

## 6. Required deterministic tests

At minimum prove:

```text
exact execution-starting prompt body
no resume:false on normal open_execution path
admit-only semantics represented separately
observer before prompt
exactly one prompt
success-response invocation provenance correct
timeout uncertainty remains inspectable/cancellable
transport uncertainty remains inspectable/cancellable
definite rejection disposes observer
cancel/inspect exact-binding tests remain green
```

## 7. Quality gate

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

No live OpenCode/provider/model calls during implementation or deterministic testing.

## 8. Required implementation report

Return:

```text
branch
exact starting SHA
successor SHA
changed files

exact beta evidence used for resume semantics
exact normal prompt body after correction

exact beta prompt-success response semantics
runtime_invocation behavior after correction

focused tests
full pytest
ruff format/lint
pyright
build
git diff --check
exact-head CI

live runtime/provider calls:
NONE
```

Do not ACCEPT your own work.

Do not run the live sidecar.

Do not perform Human technical acceptance, promotion, or Slice closure.

A later successor candidate will require a new SHA-bound sidecar authority before further D21 live execution.
