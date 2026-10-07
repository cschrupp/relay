# Slice 2.1 — Independent Implementation Evaluation, Revision 3

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-EVAL-003`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Live sidecar finding:
RLY-S21-SIDECAR-EVAL-007 — REWORK

Rework handoff:
RLY-S21-IMPL-REWORK-HANDOFF-001

Exact rework baseline:
ded3ed03b7070ea095a823129ebe44935cb57997

Successor candidate:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

Implementation branch:
implementation/2.1-agent-runtime-contract

Exact-head CI:
37673385489 — SUCCESS
```

The successor is exactly one commit ahead of the preserved live-defective candidate and modifies only:

```text
src/relay_engine/agent_runtime/opencode.py
tests/unit/test_opencode_runtime.py
```

No dependency, schema, persistence, governance, lifecycle, board, repository integration, or Phase 3 surface changed.

## F007-A — RESOLVED DETERMINISTICALLY — pinned-beta prompt body mapping

The prior candidate emitted:

```json
{
  "prompt": {
    "text": "...",
    "files": [],
    "agents": []
  },
  "resume": false
}
```

Run 007 proved that the exact installed beta rejected that shape before inference with:

```text
Missing key at ["text"]
```

The successor now emits:

```json
{
  "text": "...",
  "files": [],
  "agents": [],
  "skills": [],
  "metadata": {},
  "resume": false
}
```

The operator reported that this shape was derived from the exact installed `0.0.0-beta-17823` binary's embedded route schema and independently corroborated by the Run-007 live schema rejection.

The evaluator did not independently inspect the local binary bytes. Therefore this resolution is accepted **deterministically**, with the live sidecar remaining the required proof of exact runtime compatibility.

## F007-B — RESOLVED — deterministic mock now asserts the corrected contract

The mock now requires the exact root-level body and explicitly rejects the obsolete nested `prompt` wrapper.

It also proves:

- event observation is established before the prompt POST;
- exactly one prompt POST is emitted.

This corrects the prior problem where the deterministic mock encoded the same incorrect contract as the implementation.

## F007-C — RESOLVED — prompt HTTP 400 normalization

Prompt HTTP 400 now maps to:

```text
CONFIGURATION
```

rather than:

```text
AGENT_BLOCKED
```

This is consistent with the candidate's existing session-creation treatment of request/schema/configuration rejection and avoids falsely attributing an adapter-generated malformed request to agent behavior.

HTTP 403 remains `PERMISSION_DENIED`.

## Preservation review

The production diff is bounded to the request-body mapping and HTTP-400 category.

The previously accepted semantics remain structurally unchanged:

- exact request/session binding;
- event observer before prompt admission;
- one-prompt guard;
- timeout uncertainty recovery;
- transport uncertainty recovery;
- provisional exact handle retention;
- definite rejection observer cleanup;
- cancellation exact binding;
- inspection exact binding;
- event-continuity behavior;
- provider/model request immutability.

## Validation

Operator-reported local validation:

```text
focused runtime tests: 26 passed
full pytest: 646 passed
uv sync --frozen --group dev: PASS
ruff format: PASS
ruff lint: PASS
pyright: 0 errors / 0 warnings
uv build: PASS
git diff --check HEAD^ HEAD: PASS
live OpenCode/OpenRouter calls: NONE
```

Independent repository verification established:

```text
candidate parent:
ded3ed03b7070ea095a823129ebe44935cb57997

successor:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

ahead by:
1 commit

changed files:
2 authorized files only

remote branch head:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

GitHub Actions:
37673385489 — SUCCESS

CI head:
5df1add9ed829a62a99d7f25f561a0f492ff5c73
```

## Evaluation outcome

```text
RLY-S21-EVAL-003 — ACCEPT
```

Successor candidate:

```text
5df1add9ed829a62a99d7f25f561a0f492ff5c73
```

is deterministically implementation-acceptable under `RLY-S21-IMPL-AUTH-001`.

## Live-evidence authority boundary

The existing live sidecar authority:

```text
RLY-S21-SIDECAR-AUTH-001
```

is explicitly bound to candidate:

```text
ded3ed03b7070ea095a823129ebe44935cb57997
```

and explicitly prohibits silently substituting a later implementation SHA.

Therefore this evaluation does **not** authorize running D21 against `5df1add9...`.

A new narrow Human Authority record is required before the live sidecar may exercise the successor candidate.

Until that authority and successful sidecar evidence exist:

```text
Human technical acceptance:
NOT ELIGIBLE

Slice 2.1 closure:
NOT AUTHORIZED

real-project agent execution:
NOT AUTHORIZED
```
