# Slice 2.1 — Independent Implementation Evaluation, Revision 4

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-EVAL-004`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Live sidecar finding:
RLY-S21-SIDECAR-EVAL-008 — REWORK

Rework handoff:
RLY-S21-IMPL-REWORK-HANDOFF-002

Exact rework baseline:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

Successor candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Implementation branch:
implementation/2.1-agent-runtime-contract

Exact-head CI:
37682777614 — SUCCESS
```

The successor is exactly one commit ahead of the preserved Run-008 candidate and modifies only:

```text
src/relay_engine/agent_runtime/opencode.py
tests/unit/test_opencode_runtime.py
```

No dependency, schema, persistence, governance, lifecycle, board, repository-integration, or Phase 3 surface changed.

## F008-A — RESOLVED DETERMINISTICALLY — normal open_execution no longer requests admit-only behavior

The prior candidate sent:

```json
{
  "text": "<input>",
  "files": [],
  "agents": [],
  "skills": [],
  "metadata": {},
  "resume": false
}
```

Run 008 proved that this request is durably admitted but does not wake the OpenCode execution loop.

The successor now omits `resume` from normal `open_execution()`:

```json
{
  "text": "<input>",
  "files": [],
  "agents": [],
  "skills": [],
  "metadata": {}
}
```

The operator reported this was derived from the exact installed `0.0.0-beta-17823` embedded route/generated schema, where omission/true schedules execution and `false` requests admit-only behavior.

The evaluator independently verified the code change and deterministic behavior model. Exact live runtime compatibility still requires sidecar evidence against this SHA.

## F008-B — RESOLVED — deterministic mock now distinguishes admission from execution wake

The deterministic mock now models:

```text
resume:false
    -> session.inbox.enqueued
    -> no execution wake

normal open_execution with resume omitted
    -> admission
    -> execution wake
    -> execution events
```

The normal mapping test also proves:

- event observation exists before prompt POST;
- exactly one prompt POST occurs;
- `resume` is absent;
- the execution-wake path is exercised.

This removes the prior mock behavior that falsely emitted execution events for an admit-only request.

## F008-C — RESOLVED DETERMINISTICALLY — admitted-item ID is not treated as invocation identity

The successor removes the generic prompt-response `id` fallback from runtime invocation provenance.

The operator reported that the exact beta prompt success payload is a user/inbox admitted item whose generic `id` is that admitted item identity, not a runtime invocation identity.

The deterministic mock now returns an admitted user item and the resulting handle correctly preserves:

```text
runtime_invocation = None
```

This conforms to Relay's contract: runtime-native invocation identity is recorded only when exposed; it is not fabricated from unrelated IDs.

## Preservation review

The production diff is minimal:

- remove `resume: false` from normal prompt body;
- stop manufacturing `RuntimeInvocationRef` from prompt response generic `id`;
- remove the now-unused invocation-ID extraction helper.

Previously accepted semantics remain structurally unchanged:

- root-level prompt mapping;
- observer-before-admission;
- one-prompt guard;
- exact request/session binding;
- timeout uncertainty recovery;
- transport uncertainty recovery;
- provisional exact handle retention;
- definite-rejection observer cleanup;
- HTTP 400 -> CONFIGURATION;
- HTTP 403 -> PERMISSION_DENIED;
- cancellation exact binding;
- inspection exact binding;
- event-continuity behavior;
- provider/model request immutability.

The existing deterministic suite still contains focused tests for uncertain prompt admission, definite prompt rejection cleanup, exact-binding inspection, and cancel binding/idempotency.

## Validation

Operator-reported local validation:

```text
focused OpenCode runtime tests: 27 passed
full pytest: 647 passed
uv sync --frozen --group dev: PASS
ruff format: PASS
ruff lint: PASS
pyright: 0 errors / 0 warnings / 0 informations
uv build: PASS
git diff --check: PASS
live OpenCode/OpenRouter/provider/model calls: NONE
```

Independent repository verification established:

```text
candidate parent:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

successor:
f9a4790c6343561b462d521008c197d776e9ebcf

ahead by:
1 commit

changed files:
2 authorized files only

remote branch head:
f9a4790c6343561b462d521008c197d776e9ebcf

GitHub Actions:
37682777614 — SUCCESS

CI head:
f9a4790c6343561b462d521008c197d776e9ebcf
```

## Evaluation outcome

```text
RLY-S21-EVAL-004 — ACCEPT
```

Successor candidate:

```text
f9a4790c6343561b462d521008c197d776e9ebcf
```

is deterministically implementation-acceptable under `RLY-S21-IMPL-AUTH-001`.

## Live-evidence authority boundary

The current live sidecar authority:

```text
RLY-S21-SIDECAR-AUTH-002
```

is explicitly bound to:

```text
5df1add9ed829a62a99d7f25f561a0f492ff5c73
```

and may not silently substitute a later implementation SHA.

Therefore this evaluation does **not** authorize running D21 against `f9a4790...`.

A new narrow Human Authority record is required before live sidecar evidence may exercise the successor.

Until that authority and successful live evidence exist:

```text
Human technical acceptance:
NOT ELIGIBLE

Slice 2.1 closure:
NOT AUTHORIZED

real-project agent execution:
NOT AUTHORIZED
```
