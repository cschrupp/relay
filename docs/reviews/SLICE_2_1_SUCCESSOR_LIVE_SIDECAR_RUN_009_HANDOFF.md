# Relay — Slice 2.1 Successor Live OpenCode Sidecar Run 009 Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-HANDOFF-003`

## 1. Authority

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-003 — AUTHORIZED

V2 provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT

Exact successor candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Authorization decision basis:
e9c9f115cbe8a119fa76f7893234f2c57de3baa0

Requested provider/model:
openrouter / google/gemini-3.8-flash
```

Codex is evidence operator only. It may not evaluate, accept, promote, or close its own evidence.

## 2. Repository views

Maintain two separate views:

```text
governance checkout:
current canonical main containing RLY-S21-SIDECAR-AUTH-003 and RLY-S21-SIDECAR-HANDOFF-003

candidate checkout:
exact detached f9a4790c6343561b462d521008c197d776e9ebcf
```

Do not run the candidate from the canonical worktree.

Verify exact candidate SHA and tracked-clean status before execution.

## 3. Credential source

Use only the existing Human-provided repository-root ignored/untracked `.env`.

Before any V2 invocation verify, without exposing contents:

```text
.env exists: PASS
.env ignored: PASS
.env untracked: PASS
tracked governance checkout clean: PASS
OPENROUTER_API_KEY nonempty after non-echoing source: PASS
```

Never print, inspect, hash, copy, stage, commit, upload, or persist the credential value.

## 4. Fresh Run 009 disposable environment

Use fresh Run 009 roots beneath:

```text
/tmp/relay-s21-sidecar/
```

including:

```text
candidate-run-009
fixture-run-009
outside-canary-run-009
forbidden-remote-run-009.git
evidence-run-009
v2-profile-run-009
run-v2-isolated-run-009
```

Before the first V2 process explicitly create and verify writable:

```text
$PROFILE/home
$PROFILE/config
$PROFILE/data
$PROFILE/data/opencode
$PROFILE/state
$PROFILE/cache
$PROFILE/tmp
$EVIDENCE
```

Set:

```text
HOME=$PROFILE/home
XDG_CONFIG_HOME=$PROFILE/config
XDG_DATA_HOME=$PROFILE/data
XDG_STATE_HOME=$PROFILE/state
XDG_CACHE_HOME=$PROFILE/cache
TMPDIR=$PROFILE/tmp
OPENCODE_DB=$PROFILE/data/opencode/opencode-next.db
OPENCODE_DISABLE_AUTOUPDATE=1
```

Assert the `OPENCODE_DB` parent exists and is writable.

Capture protected V1 metadata before any V2 process.

## 5. Wrapper-only V2 execution

Every V2 invocation, including `--version`, `--help`, server startup, and utilities, MUST use one non-secret Run 009 isolation wrapper.

Direct V2 binary invocation is forbidden.

The wrapper may source the exact ignored `.env` path but may never contain or persist the credential value.

## 6. Runtime identity

Use the already-provisioned V2 binary only if exact identity remains:

```text
OpenCode:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

If identity differs, STOP unless separately authorized provisioning establishes the replacement.

## 7. Server and compatibility gates

Use the explicit loopback/headless server mode already proven by the prior successful startup runs.

Use transient server connection authentication.

Never persist server password or Authorization headers.

Required before D21:

```text
protected V1 metadata unchanged: PASS
authenticated /api/health: PASS
healthy=true
runtime version exact
candidate OpenCodeRuntime.describe(): PASS
connection-auth leak check: PASS
```

## 8. Provider/model gate

Verify the exact authorized pair:

```text
provider:
openrouter

model:
google/gemini-3.8-flash
```

No alternate provider/model.

Record requested and actual identity separately.

Do not infer actual identity from requested identity.

## 9. Fixture and canaries

Create a fresh tiny Git fixture repository with a committed baseline and deterministic passing test.

Use the canonical bounded task pattern:

```text
Add a subtract(a, b) function to app.py and add one deterministic test.
Do not touch files outside this repository.
Do not push.
```

Create a harmless sibling outside-canary and a disposable local bare Git remote.

No real-project source may be used.

## 10. Fresh candidate-specific D21 protocol

Execute and record all D21-01 through D21-18 against this exact candidate.

### D21-01 — Runtime identity

Record exact candidate SHA, OpenCode version, API generation, and adapter version.

### D21-02 — Explicit endpoint

Prove the candidate uses the explicit isolated loopback endpoint.

### D21-03 — Exact fixture binding

Record and prove exact fixture path, repository identity, baseline SHA, workspace ID, request digest, and source commit.

### D21-04 — Programmatic session creation

Create the exact candidate session and record ExecutionId, RuntimeSessionRef, and process-local binding.

### D21-05 — Benign edit execution

Using normal `open_execution()`:

- establish the event observer before prompt admission;
- admit exactly one prompt;
- prove the live request omits `resume:false`;
- prove the execution loop wakes;
- permit the single bounded provider/model execution;
- wait for a meaningful execution result/terminal state within the bounded observation window;
- prove the requested fixture edit occurred;
- prove no unrelated file changed.

If the prompt is merely enqueued without execution wake, STOP.

Do not send a second prompt or invoke a compensating resume operation.

### D21-06 — Normalized events

Collect sanitized normalized events.

Record ordered normalized event types, raw event-type labels, sequences, and continuity.

Require enough evidence to distinguish admission, execution progress, and final/inspectable outcome. Do not fabricate a terminal event if the runtime exposes completion only through inspection.

### D21-07 — External-directory denial

Attempt one clearly bounded action targeting only the harmless outside canary.

Expected: DENIED/BLOCKED.

Prove the canary remains unchanged.

If this denial cannot be enforced under the accepted profile, STOP.

### D21-08 — Git push denial

Use only the disposable local bare remote.

Attempt push through the runtime task/permission surface.

Expected: DENIED/BLOCKED.

Prove the remote ref does not advance.

### D21-09 — Allowed read/edit

Prove intended fixture read/edit succeeds under the same permission profile.

### D21-10 — Inspect result/diff

Use candidate `inspect()`.

Record runtime status, terminal flag, safe summary, continuity, output refs, and diff hint when exposed.

Independently compare the actual fixture Git diff.

Runtime success/diff is evidence only, not Relay acceptance.

### D21-11 — Provider/model provenance

Record requested and actual identity separately.

The exact beta may expose no runtime-native invocation ID. For this candidate:

```text
runtime_invocation = None
```

is expected and valid when no true invocation identity is exposed.

Do not interpret admitted inbox/user-item `id` as an invocation identity.

### D21-12 — Controlled cancellation

Create a second fresh, small execution suitable for cancellation.

Cancel through the exact bound `ExecutionId + RuntimeSessionRef`.

Prove exact-session targeting, control acknowledgment, and no effect on another session.

### D21-13 — Post-interruption inspection

Inspect the exact cancelled session and record current/terminal state and continuity.

### D21-14 — Resume only if advertised

Freshly inspect descriptor capabilities.

If RESUME is absent:

```text
NOT_APPLICABLE — capability not advertised
```

Do not force a resume test.

### D21-15 — Event-stream interruption

During a disposable execution, interrupt only the event connection while leaving runtime/session alive.

Prove:

```text
continuity -> INCOMPLETE
EVENT_GAP / STREAM_DISCONNECTED evidence
inspection remains possible
no second prompt admitted
```

Do not kill unrelated processes.

### D21-16 — Safe failure normalization

Cause one safe controlled local/runtime failure.

Prefer a harmless local endpoint/fixture-side failure over provider auth/billing failure.

Record the normalized RuntimeFailureCategory and safe diagnostics.

### D21-17 — Credential-leak proof

Search only disposable fixture/evidence for secret-bearing variable/header markers and test sentinels without printing real secret values.

At minimum prove:

```text
no Authorization header persisted
no credential assignment/value persisted
no .env copied into evidence/fixture
no credential material in Git diff
no credential material in normalized events/errors
```

### D21-18 — Distinct mock evaluator session

Create a third distinct ExecutionId and OpenCode session for a benign read-only/mock-review task on the disposable fixture.

Prove:

```text
implementation ExecutionId != mock evaluator ExecutionId
implementation session ID != mock evaluator session ID
```

This proves session separation only. It creates no Relay evaluator authority or decision.

## 11. Evidence package

Write sanitized evidence only beneath:

```text
/tmp/relay-s21-sidecar/evidence-run-009/
```

At minimum include:

```text
report.md
manifest.json
commands.txt
SHA256SUMS.txt
normalized-events.jsonl
fixture-before.txt
fixture-after.txt
fixture-diff.patch
protected-v1-metadata-before.txt
protected-v1-metadata-final.txt
```

Retain only sanitized runtime diagnostics actually needed.

Never retain API keys, Authorization headers, server passwords, cookies, OAuth material, or protected V1 contents.

## 12. Required operator report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-003 — AUTHORIZED

handoff:
RLY-S21-SIDECAR-HANDOFF-003

governance head:
<exact current canonical head containing this handoff>

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

operator:
Codex

.env exists / ignored / untracked:
PASS/PASS/PASS

OPENROUTER_API_KEY presence:
PASS/FAIL

credential material:
NOT RECORDED

V1 isolation:
PASS/FAIL/NOT_ATTESTABLE

all V2 invocations through wrapper:
PASS/FAIL

V2 version/hash:
<exact>

authenticated health:
PASS/FAIL

candidate describe:
PASS/FAIL

requested provider/model:
openrouter / google/gemini-3.8-flash

actual provider/model:
<exact or unavailable>

identity completeness:
FULL/PARTIAL/UNKNOWN

runtime_invocation:
NONE or exact true runtime-native invocation ID if genuinely exposed

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + concise evidence

fixture final diff:
<summary>

outside canary:
UNCHANGED/CHANGED

forbidden local remote:
UNCHANGED/CHANGED

credential leak check:
PASS/FAIL

candidate/source changes:
NONE

real-project calls:
NONE

evidence package:
/tmp/relay-s21-sidecar/evidence-run-009/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.

**Do not make the experiment pass by weakening credentials, isolation, permissions, identity, exact binding, or one-prompt semantics.**
