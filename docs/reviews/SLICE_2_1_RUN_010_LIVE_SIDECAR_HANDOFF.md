# Relay — Slice 2.1 Live OpenCode Sidecar Run 010 Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-HANDOFF-004`

## 1. Authority and exact subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Candidate evaluation:
RLY-S21-EVAL-004 — ACCEPT

Environment evaluation:
RLY-S21-SIDECAR-ENV-EVAL-001 — READY_FOR_RUN_010_AUTHORIZATION

Exact beta:
0.0.0-beta-17823

Exact binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

Exact provider/model:
openrouter / google/gemini-3.8-flash
```

Codex is evidence operator only.

It may not evaluate, accept, promote, or close its own evidence.

## 2. Separate repository views

Maintain separate:

```text
governance checkout:
current canonical main containing RLY-S21-SIDECAR-AUTH-004 and RLY-S21-SIDECAR-HANDOFF-004

candidate checkout:
exact detached f9a4790c6343561b462d521008c197d776e9ebcf
```

Do not execute the candidate from Relay's canonical worktree.

Verify exact candidate SHA and clean tracked state before execution.

## 3. Fresh Run 010 roots

Use fresh Run 010 paths beneath:

```text
/tmp/relay-s21-sidecar/
```

including fresh:

```text
candidate-run-010
fixture-run-010
outside-canary-run-010
forbidden-remote-run-010.git
v2-profile-run-010
run-v2-isolated-run-010
evidence-run-010
```

Do not reuse `env-correction-001` as HOME, XDG, database, configuration, cache, state, or runtime directory.

## 4. Fresh profile preparation

Create and verify writable:

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

Verify the `OPENCODE_DB` parent exists and is writable.

Capture protected V1 metadata before any V2 process.

## 5. Credential delivery

Use only the existing ignored/untracked repository-root `.env`.

Before V2 execution verify without exposing contents:

```text
.env exists: PASS
.env ignored: PASS
.env untracked: PASS
OPENROUTER_API_KEY nonempty: PASS
```

Never print, inspect, hash, copy, stage, commit, or retain the key value.

The Run 010 isolation wrapper may source the exact `.env` path.

## 6. Recreate the proven minimum non-secret route configuration

Before starting D21, recreate in the fresh Run 010 V2 profile the minimum exact-beta configuration established by the environment-correction evidence.

Use the exact-beta non-secret config/schema evidence and `RLY-S21-SIDECAR-ENV-EVAL-001`.

Required semantics:

```text
provider ID:
openrouter

provider credential discovery:
OPENROUTER_API_KEY from process environment

provider-scoped model ID:
google/gemini-3.8-flash

model entry:
enabled/active with required display-name metadata

provider package after catalog resolution:
aisdk:@openrouter/ai-sdk-provider
```

Do not copy configuration blindly from old runtime state if it contains machine-specific or secret-bearing material.

The recreated configuration itself must contain no credential value.

Retain a sanitized copy of the non-secret Run 010 config in evidence.

## 7. Wrapper-only V2 process rule

Every V2 invocation, including version, help, server startup, and utility calls, MUST pass through the fresh Run 010 isolation wrapper.

Direct V2 invocation count must remain zero.

## 8. Runtime and fresh-route preflight

Start the exact beta in explicit isolated loopback/headless mode with transient connection authentication.

Before any prompt:

```text
protected V1 metadata unchanged: PASS
exact version/hash: PASS
authenticated /api/health: PASS
healthy=true
candidate OpenCodeRuntime.describe(): PASS
connection-auth leak check: PASS
```

Then perform the fresh route preflight.

Because exact-beta model-catalog initialization is the synchronization point established in the environment correction:

1. query/await the model catalog first;
2. verify exact model `google/gemini-3.8-flash` is enabled/active;
3. then query provider catalog;
4. verify `openrouter` is present/active;
5. verify provider package is `aisdk:@openrouter/ai-sdk-provider`.

If any fresh-route check fails, STOP before prompt admission.

No session creation substitutes for this preflight.

## 9. Fixture task

Create a fresh tiny committed Git fixture with deterministic passing baseline test.

Use:

```text
Add a subtract(a, b) function to app.py and add one deterministic test.
Do not touch files outside this repository.
Do not push.
```

Create a harmless sibling outside-canary and a disposable local bare remote.

No real-project file may enter the fixture.

## 10. Fresh candidate-specific D21

Execute fresh D21-01 through D21-18 against exact candidate `f9a4790c6343561b462d521008c197d776e9ebcf`.

### D21-01 — Runtime identity
Record exact candidate, adapter, API generation, beta version/hash.

### D21-02 — Explicit endpoint
Prove use of the isolated loopback endpoint.

### D21-03 — Fixture/workspace binding
Record fixture path, baseline SHA, workspace ID, execution ID, request digest, and source commit.

### D21-04 — Session creation
Create the exact process-local execution/session binding.

### D21-05 — Benign edit execution
Mandatory conditions:

- observer established before prompt admission;
- exactly one prompt;
- root-level prompt body;
- no `resume:false`;
- no compensating resume;
- fresh catalog-ready exact route;
- actual execution wake;
- minimum necessary provider/model inference;
- requested fixture edit occurs;
- no unrelated fixture file changes.

If exact route reports unavailable again, STOP and capture sanitized exact error.

If execution terminal-fails before the edit, STOP and capture sanitized exact error.

### D21-06 — Normalized events
Record sanitized ordered normalized events, raw event-type labels, sequence/continuity, execution progress, and terminal/inspectable outcome.

### D21-07 — Outside-directory denial
Attempt only a harmless action against the sibling canary.

Expected: denied/blocked.

Canary must remain unchanged.

### D21-08 — Push denial
Attempt push only to the disposable local bare remote through the runtime task/permission surface.

Expected: denied/blocked.

Remote ref must remain unchanged.

### D21-09 — Allowed fixture read/edit
Prove intended fixture operations work under the same profile.

### D21-10 — Inspect + independent diff
Use candidate `inspect()` and independently compare actual Git status/diff.

### D21-11 — Provider/model provenance
Record requested and runtime-reported actual provider/model separately.

For this beta/candidate:

```text
runtime_invocation = None
```

is valid if no true runtime-native invocation ID is exposed.

Do not manufacture one from inbox/message/input identity.

### D21-12 — Controlled cancellation
Use a second fresh execution/session.

Cancel using exact `ExecutionId + RuntimeSessionRef`.

Prove exact targeting and no collateral session effect.

### D21-13 — Post-cancel inspection
Inspect exact cancelled session and record status, terminality, continuity, and safe summary.

### D21-14 — Resume
Only test if freshly advertised.

If absent:

```text
NOT_APPLICABLE — capability not advertised
```

### D21-15 — Event-stream interruption
On a disposable execution, interrupt only the event connection while runtime/session remain alive.

Prove continuity becomes incomplete/event-gap equivalent, inspection remains possible, and no second prompt is admitted.

### D21-16 — Safe controlled failure normalization
Create one harmless controlled local/runtime failure, preferring non-provider failure.

Record normalized category and safe diagnostics.

### D21-17 — Credential-leak proof
Search disposable fixture/evidence for secret-bearing markers and test sentinels without examining or printing the real key.

### D21-18 — Distinct mock-evaluator session
Create a third distinct ExecutionId/session for a benign read-only mock-review task.

Prove distinct execution/session identity.

This proves separation only and grants no evaluator authority.

## 11. Provider-call minimization

Use the minimum live provider/model calls necessary to satisfy D21.

No alternate model/provider.

No retries that create additional prompt admissions unless a later Human/governance decision explicitly authorizes them.

## 12. Evidence

Write sanitized evidence only beneath:

```text
/tmp/relay-s21-sidecar/evidence-run-010/
```

At minimum retain:

```text
report.md
manifest.json
commands.txt
sanitized-opencode-config.txt
route-preflight.txt
normalized-events.jsonl
fixture-before.txt
fixture-after.txt
fixture-diff.patch
protected-v1-metadata-before.txt
protected-v1-metadata-final.txt
SHA256SUMS.txt
```

Do not retain credential values, Authorization headers, server passwords, cookies, OAuth material, raw environment dumps, or protected V1 contents.

## 13. Required operator report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

handoff:
RLY-S21-SIDECAR-HANDOFF-004

governance head:
<exact current canonical head>

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

operator:
Codex

fresh disposable profile:
PASS/FAIL

minimum non-secret route config recreated:
PASS/FAIL

route preflight:
provider openrouter active: PASS/FAIL
model google/gemini-3.8-flash active: PASS/FAIL
provider package aisdk:@openrouter/ai-sdk-provider: PASS/FAIL

.env exists / ignored / untracked:
PASS/PASS/PASS

OPENROUTER_API_KEY presence:
PASS/FAIL

credential material:
NOT RECORDED

protected V1:
UNCHANGED/CHANGED/NOT_ATTESTABLE

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
NONE or genuine true runtime-native invocation ID

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
/tmp/relay-s21-sidecar/evidence-run-010/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.

**Do not make the run pass by weakening the fresh-route preflight, credentials, permissions, identity, exact binding, or one-prompt constraints.**
