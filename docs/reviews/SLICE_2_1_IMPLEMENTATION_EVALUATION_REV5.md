# Slice 2.1 — Independent Implementation Evaluation, Revision 5

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-EVAL-005`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Live sidecar finding:
RLY-S21-SIDECAR-EVAL-010R3 — REWORK

Rework handoff:
RLY-S21-IMPL-REWORK-HANDOFF-003

Exact rework baseline:
f9a4790c6343561b462d521008c197d776e9ebcf

Successor candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Implementation branch:
implementation/2.1-cancellation-compatibility

Exact-head CI:
37873019090 — SUCCESS
```

## Independent repository verification

The successor is exactly one commit ahead of the preserved Run-010r3 candidate:

```text
parent:
f9a4790c6343561b462d521008c197d776e9ebcf

successor:
4f785f08576e465cd0aa278f927fa4b7253e3f49

ahead by:
1

behind by:
0
```

Changed files are exactly the authorized two-file surface:

```text
src/relay_engine/agent_runtime/opencode.py
tests/unit/test_opencode_runtime.py
```

No dependency, schema, persistence, governance, lifecycle, board, repository-integration, permission-model, provider/model-selection, or Phase 3 surface changed.

Remote branch tip is exactly:

```text
implementation/2.1-cancellation-compatibility
4f785f08576e465cd0aa278f927fa4b7253e3f49
```

Exact-head GitHub Actions:

```text
37873019090 — SUCCESS
head_sha = 4f785f08576e465cd0aa278f927fa4b7253e3f49
```

CI independently shows successful:

```text
Ruff format
Ruff lint
Pyright
Tests
Build
```

## F010R3-A — RESOLVED DETERMINISTICALLY — exact-beta HTTP 204 cancellation success

Run 010r3 established that exact OpenCode `0.0.0-beta-17823` returns:

```text
POST /api/session/{sessionID}/interrupt
HTTP 204 No Content
```

while the prior candidate required HTTP 200 plus a JSON body and therefore misclassified successful cancellation as `TRANSPORT`.

The successor now treats exactly HTTP 204 as the successful interrupt representation and does not parse a response body.

It returns:

```text
RuntimeControlAckState.REQUESTED
```

unless terminality is already independently known, preserving:

```text
ALREADY_TERMINAL
```

semantics where applicable.

The acknowledgment is cached through the existing exact execution/session key.

## Success semantics remain narrow

The implementation does not generalize cancellation success to arbitrary 2xx responses.

It accepts only the exact pinned-beta 204 path, while preserving:

```text
404 -> NOT_FOUND
403 -> DENIED
timeout -> TIMEOUT
httpx transport failure -> TRANSPORT
binding mismatch -> REQUEST_CONFLICT
unknown binding -> SESSION_BINDING_REQUIRED
already-terminal local execution -> ALREADY_TERMINAL
```

This is consistent with the accepted Relay design, which defines idempotent cancellation at the Relay control boundary and leaves OpenCode-native HTTP representation inside the adapter.

## Deterministic mock/test correction

The primary mock interrupt endpoint now returns:

```text
HTTP 204
empty body
```

The deterministic suite proves:

- HTTP 204 -> `REQUESTED`;
- no JSON parsing occurs for 204;
- known active status is preserved and unknown status remains `UNKNOWN`;
- repeated identical cancellation returns the cached acknowledgment;
- only one interrupt POST occurs;
- concurrent cancellation serializes and shares one cached acknowledgment;
- already-terminal cancellation returns `ALREADY_TERMINAL` without an interrupt POST;
- 404 -> `NOT_FOUND`;
- 403 -> `DENIED`;
- timeout -> `TIMEOUT`;
- transport exception -> `TRANSPORT`;
- undeclared 2xx statuses are rejected rather than silently accepted;
- exact process-local binding remains mandatory.

## Preservation review

The production diff is limited to cancellation response handling.

Live-proven behavior through Run 010r3 D21-11 remains structurally untouched:

- exact runtime/health compatibility;
- session creation;
- observer-before-prompt;
- root-level prompt mapping;
- one-prompt guard;
- execution wake;
- `runtime_invocation=None` provenance semantics;
- exact provider/model binding;
- external-directory denial;
- push denial;
- allowed fixture edit;
- inspection/diff;
- normalized event behavior;
- credential containment.

## Validation

Operator-reported local validation:

```text
focused cancellation tests:
17 passed

full pytest:
659 passed

ruff format:
PASS

ruff lint:
PASS

pyright:
0 errors / 0 warnings

uv build:
PASS

git diff --check:
PASS

live OpenCode/provider/model calls:
NONE
```

Independent exact-head CI verification:

```text
GitHub Actions:
37873019090 — SUCCESS

CI head:
4f785f08576e465cd0aa278f927fa4b7253e3f49
```

## Evaluation outcome

```text
RLY-S21-EVAL-005 — ACCEPT
```

Successor:

```text
4f785f08576e465cd0aa278f927fa4b7253e3f49
```

is deterministically implementation-acceptable under `RLY-S21-IMPL-AUTH-001`.

## Live-evidence authority boundary

The most recent Human live sidecar authority:

```text
RLY-S21-SIDECAR-AUTH-004
```

is exact-SHA-bound to:

```text
f9a4790c6343561b462d521008c197d776e9ebcf
```

and does not authorize live D21 against `4f785f08576e465cd0aa278f927fa4b7253e3f49`.

This evaluation does not transfer prior candidate-specific live authority.

A new narrow Human Authority record is required before fresh live sidecar evidence may exercise the successor.

Prior Run-010r3 live PASS results remain historical evidence. They do not substitute for fresh candidate-specific live evidence against `4f785f08576e465cd0aa278f927fa4b7253e3f49`.

Until a new sidecar authority and successful live evidence exist:

```text
Human technical acceptance:
NOT ELIGIBLE

Slice 2.1 closure:
NOT AUTHORIZED

real-project agent execution:
NOT AUTHORIZED
```
