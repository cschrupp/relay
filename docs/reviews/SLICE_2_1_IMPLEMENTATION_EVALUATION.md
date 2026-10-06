# Slice 2.1 — Independent Implementation Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-EVAL-001`  
**Outcome:** `REWORK`

## Evaluated subject

```text
Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22

Exact accepted combined design:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Human design acceptance:
RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED

Implementation candidate:
c947cf607699707b8b56d22cbb9aab4b30a7bf4a

Implementation branch:
implementation/2.1-agent-runtime-contract
```

The candidate is exactly one commit ahead of the authorized baseline. The remote implementation branch was independently verified at the exact candidate SHA.

Exact-SHA GitHub Actions run:

```text
37416076480 — SUCCESS
head: c947cf607699707b8b56d22cbb9aab4b30a7bf4a
```

The reported local quality evidence is also clean:

```text
focused runtime-model tests: 10 passed
focused runtime-contract tests: 11 passed
focused OpenCode tests: 16 passed
ruff format: PASS
ruff lint: PASS
pyright: PASS — 0 errors / 0 warnings
full pytest: PASS — 636 passed
build: PASS
git diff --check: PASS
live OpenCode/provider calls: NONE
```

## Scope review

The candidate changes the authorized AgentRuntime package, three runtime-focused test modules, `pyproject.toml`, and `uv.lock`.

It additionally changes:

```text
tests/unit/test_board_web.py
```

by five lines solely to update the repository's existing exact dependency-ownership assertion from:

```text
httpx is dev-only
```

to:

```text
httpx is a runtime dependency and no longer duplicated in dev
```

This is a mechanically necessary test-maintenance consequence of the explicitly authorized `httpx` promotion. It introduces no Board behavior or production-surface change and is accepted as a bounded non-substantive deviation.

No forbidden governance/lifecycle mutation import was found in `agent_runtime`.

## Accepted implementation characteristics

The evaluator accepts the following parts of the candidate as sound:

- Relay's existing `ExecutionId` is reused;
- Relay's existing `ContentDigest` and frozen strict `DomainModel` conventions are reused;
- `RuntimeExecutionBasis` and `RuntimeExecutionRequest` are immutable and digest-bound;
- the schema-v1 canonical digest has a fixed external expected-vector test;
- session creation receives the exact request and does not admit the prompt;
- exact binding mismatch fails before event observation/prompt admission;
- provider/model requested identity remains distinct from actual identity;
- OpenCode integration is isolated behind a Python/httpx HTTP adapter;
- no OpenCode SDK, Node, Bun, persistence schema, board behavior, lifecycle mutation, or governance mutation is introduced;
- the event observer is established before prompt admission;
- event queues are bounded and exact-session filtering is implemented;
- ambiguous event attribution marks continuity incomplete;
- queue overflow and stream disconnect produce explicit incomplete continuity;
- runtime success remains distinct from Relay engineering-result/evaluation/acceptance;
- live OpenCode, credentials, provider/model calls, and real agent execution were not performed.

These accepted characteristics should be preserved during rework.

# Findings

## F001 — BLOCKING — cancel() can mutate an unbound OpenCode session

The accepted design requires runtime control to remain bound to the exact Relay execution/session identity.

The candidate's cancellation path verifies only that:

```text
runtime_session.runtime_id == "opencode"
```

and, when a local active execution exists, that the active session is not different.

If no local active execution exists for the submitted `ExecutionId`, the candidate will send:

```text
POST /api/session/<caller-supplied-session>/interrupt
```

for any syntactically valid OpenCode session ID.

Therefore a caller can construct:

```text
RuntimeCancelRequest(
    execution_id=<arbitrary Relay ExecutionId>,
    runtime_session=RuntimeSessionRef("opencode", <unrelated session>)
)
```

and cause a mutating control request against a session that was never proven to be the exact bound session for that Relay execution.

That violates the exact-binding, fail-closed, and no-authority-expansion requirements.

### Required correction

Before any cancellation HTTP request, require exact process-local proof that the submitted `ExecutionId` and `RuntimeSessionRef` correspond to the known exact binding/open execution.

For the base Slice 2.1 process-local profile:

```text
known exact binding/active session
    -> cancellation may proceed

missing exact binding
    -> SESSION_BINDING_REQUIRED / fail closed

different exact session
    -> REQUEST_CONFLICT / fail closed
```

Do not discover, guess, or accept a caller-supplied unbound session.

Add deterministic tests proving no HTTP interrupt is sent for:

- unknown ExecutionId;
- known ExecutionId + different session ID;
- process-state loss / missing binding.

## F002 — BLOCKING — inspect() can read an unbound OpenCode session before exact binding proof

`inspect()` has the same identity problem on the read path.

When no `_active` execution exists, the method validates only the runtime ID and then performs:

```text
GET /api/session/<handle.runtime_session.session_id>
```

before proving that the supplied session ID equals the exact process-local binding for the supplied Relay `ExecutionId`.

If `create_session()` has already populated requested-identity provenance for an ExecutionId, a caller can construct a `RuntimeExecutionHandle` for another OpenCode session and cause Relay to inspect that unrelated runtime session.

This contaminates provenance even though the operation is read-only.

### Required correction

Before any remote inspection request:

- require exact `ExecutionId -> RuntimeSessionBinding` proof;
- require handle execution ID, session ref, request digest, and known binding to agree;
- if an active handle exists, continue requiring exact handle identity;
- if process-local binding is unavailable, fail closed with `SESSION_BINDING_REQUIRED`;
- never perform the remote GET before this proof.

Add focused tests demonstrating zero HTTP inspection requests for an unknown or mismatched session.

## F003 — BLOCKING — uncertain prompt admission is not recoverable through the public contract

The accepted design explicitly treats prompt-admission timeout/transport uncertainty as a state that must not be followed by a blind second start. Relay must retain enough exact identity to inspect the already-bound session.

The candidate correctly establishes the event observer before prompt admission. However, after that point, these paths raise an exception:

```text
prompt POST timeout
prompt POST transport failure
HTTP prompt rejection
```

while leaving process-local state such as:

```text
_opened contains ExecutionId
_active contains the observer/session
```

and returning no `RuntimeExecutionHandle` to the caller.

The caller is then unable to use the public `inspect(handle)` contract because no handle was returned, while a second `open_execution()` is rejected as already opened.

This creates an orphaned process-local execution state and fails the accepted recovery contract.

The timeout/transport cases are especially important because the remote runtime may have admitted the prompt even though Relay did not receive the response.

### Required correction

Preserve fail-closed semantics while making uncertain admission inspectable.

A bounded solution must ensure that after prompt-admission uncertainty Relay can:

1. retain the exact request/session binding;
2. obtain or reconstruct a contract-valid exact handle for inspection without guessing;
3. prevent a second prompt from being admitted;
4. keep the already-established event observer attached where appropriate;
5. permit `inspect()` and `cancel()` only through the exact-bound identity;
6. cleanly dispose the observer on definite pre-execution rejection when no execution could have started.

Do not solve this by auto-retrying the prompt or creating a replacement session.

Add tests for at least:

```text
prompt timeout -> no second prompt; exact session remains inspectable
transport uncertainty -> no second prompt; exact session remains inspectable
definite permission/config rejection -> no orphan event pump
recovery inspection cannot target another session
```

If satisfying this requires changing the accepted public protocol rather than a bounded adapter/internal state correction, STOP and escalate instead of redesigning under implementation authority.

# Non-blocking observations

## O001 — raw event type is currently discarded

`_ActiveExecution._make_event(..., raw_event_type=...)` currently constructs the envelope with:

```text
raw_event_type=None
```

even when a safe normalized caller supplies a raw runtime type.

The design permits runtime-native event type/ID provenance when safe, so this is not independently blocking, but preserving the already-sanitized bounded raw event type would improve auditability.

## O002 — exact live OpenCode API behavior is still unproven

The candidate's HTTP paths and response mappings are mock-tested only, as required by implementation authority.

The accepted design requires a separately authorized live OpenCode sidecar before Human technical acceptance of the live adapter.

Therefore even after the code defects above are resolved and deterministic implementation evaluation reaches ACCEPT:

```text
Human technical acceptance:
BLOCKED PENDING LIVE SIDECAR EVIDENCE
```

unless the Human separately authorizes and the project successfully completes that evidence gate.

# Evaluation outcome

```text
RLY-S21-EVAL-001 — REWORK
```

Candidate:

```text
c947cf607699707b8b56d22cbb9aab4b30a7bf4a
```

is not technically eligible for Human acceptance.

The rework is bounded to F001–F003 plus mechanically necessary tests and closely related cleanup. No redesign, reauthorization, persistence/schema change, new dependency, live OpenCode call, provider/model call, or agent execution is required or authorized.

Preserve this candidate and this immutable REWORK evaluation in history. A successor candidate should be a descendant of `c947cf607699707b8b56d22cbb9aab4b30a7bf4a`.

This evaluation does not grant Human technical acceptance, live-sidecar authority, result promotion, Slice 2.1 closure, Slice 2.2 work, Phase 3 work, or Relay agent execution.
