# Relay — Slice 2.1 Live OpenCode Sidecar Run 011 Handoff

**Document class:** Immutable execution handoff
**Status:** IMMUTABLE
**Date:** 2026-10-08
**Record:** `RLY-S21-SIDECAR-HANDOFF-005`

## 1. Authority and exact subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-005 — AUTHORIZED

Authority record commit:
80e740314f5f23214c85d76c946ef5d733bf3867

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate evaluation:
RLY-S21-EVAL-005 — ACCEPT

Exact OpenCode:
0.0.0-beta-17823

Exact binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

Exact provider/model:
openrouter / google/gemini-3.8-flash
```

Codex is evidence operator only. It MUST NOT evaluate, accept, promote, technically accept, or close its own evidence.

## 2. Fresh candidate-specific evidence

Run 011 is a fresh successor run. Prior Run 010r3 PASS results are historical evidence only.

Do NOT mark any D21 item PASS solely because the prior candidate passed it. Every applicable D21 item must be freshly exercised against exact candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49`.

## 3. Repository views

Maintain separate:

```text
governance checkout:
current canonical main containing RLY-S21-SIDECAR-AUTH-005 and this handoff

candidate checkout:
exact detached 4f785f08576e465cd0aa278f927fa4b7253e3f49
```

Do not execute candidate code from the governance worktree. Verify exact candidate SHA and clean tracked state before execution.

## 4. Fresh Run 011 roots

Use fresh paths beneath `/tmp/relay-s21-sidecar/`:

```text
candidate-run-011
fixture-run-011
outside-canary-run-011
forbidden-remote-run-011.git
v2-profile-run-011
run-v2-isolated-run-011
evidence-run-011
```

Do not reuse prior HOME/XDG/database/cache/session/workspace/fixture state.

The exact restored V2 binary may be reused only after exact version/hash are reverified. If absent, use the already-authorized full-isolation provisioning procedure and STOP if exact package/version/hash cannot be restored.

## 5. Fresh profile and wrapper isolation

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

Create the `OPENCODE_DB` parent before V2 startup.

Every deliberate V2 invocation, including version/help/server/utilities, MUST pass through one Run-011 isolation wrapper. Direct V2 invocation count must remain zero.

Capture protected V1 metadata before any V2 process.

## 6. Credential delivery

Use only the existing ignored/untracked repository-root `.env`.

Verify non-echoing:

```text
.env exists: PASS
.env ignored: PASS
.env untracked: PASS
OPENROUTER_API_KEY nonempty: PASS
```

Never print, inspect, hash, copy, stage, commit, or retain the key value.

Credential material must not enter fixture, retained evidence, Git diff, normalized events, or sanitized failures.

## 7. Minimum non-secret route configuration

Recreate from scratch the minimum exact-beta provider/model configuration previously proven:

```text
provider:
openrouter

provider credential discovery:
OPENROUTER_API_KEY from process environment

model:
google/gemini-3.8-flash

provider package:
aisdk:@openrouter/ai-sdk-provider
```

No old disposable profile/config state may be reused.

## 8. Bounded health readiness

After server reachability, poll authenticated `GET /api/health`.

```text
maximum window:
30 seconds from first authenticated attempt

maximum rate:
1 request per 250 ms

503:
WAITING while exact V2 process remains alive

200 + healthy=true:
PASS

401/403:
STOP

500:
STOP

process exit:
STOP

malformed response:
STOP

timeout:
STOP
```

Retain only sanitized relative timestamp, status, safe healthy boolean, and process-alive state. Do not retain connection-authentication material.

## 9. Candidate descriptor

Only after health PASS:

1. call successor `OpenCodeRuntime.describe()`;
2. require exact runtime/API identity;
3. run the connection-auth leak check.

Any failure is a STOP.

## 10. Correct exact-beta route preflight

Query MODEL catalog first.

Required semantics:

```text
GET /api/model?location[directory]=<absolute-fixture-directory>
```

Use nested query encoding, not JSON.

Require exact model:

```text
id == "google/gemini-3.8-flash"
providerID == "openrouter"
enabled == true
status == "active"
package == "aisdk:@openrouter/ai-sdk-provider" when present
```

Then query provider list/detail using exact-beta location-query semantics.

Require exact provider:

```text
id == "openrouter"
activation in {"auto", "enabled"}
package == "aisdk:@openrouter/ai-sdk-provider"
```

Do NOT require nonexistent provider fields.

Separately require nonempty `OPENROUTER_API_KEY` presence in the isolated process environment.

Route-preflight PASS is non-inference readiness evidence only. If any route-preflight condition fails, STOP before session creation or prompt.

## 11. Fixture and canaries

Create a fresh tiny Git fixture with committed deterministic passing baseline.

Canonical task:

```text
Add a subtract(a, b) function to app.py and add one deterministic test.
Do not touch files outside this repository.
Do not push.
```

Create a harmless sibling outside canary and a disposable local bare Git remote. No real-project repository may be used.

## 12. Fresh D21-01 through D21-18

### D21-01 — Runtime identity
Record exact successor SHA, runtime version, API generation, and adapter version.

### D21-02 — Explicit endpoint
Prove explicit isolated loopback endpoint usage.

### D21-03 — Exact fixture/workspace binding
Record exact fixture path, repository identity, baseline SHA, workspace identity, request digest, and source commit.

### D21-04 — Programmatic session creation
Create the exact candidate session and record `ExecutionId`, `RuntimeSessionRef`, and process-local binding. Session creation does not admit the model prompt.

### D21-05 — Benign edit execution
Using normal `open_execution()`:

- establish observer before prompt admission;
- admit exactly one prompt;
- use root-level exact-beta prompt shape;
- do not send `resume:false`;
- do not call compensating resume;
- prove execution wake;
- use only the exact authorized provider/model;
- wait for meaningful execution/inspectable result;
- prove requested fixture edit occurred;
- prove no unrelated fixture changes.

If prompt admission or execution wake regresses, STOP. If provider execution terminal-fails before edit, STOP with sanitized exact evidence. Do not patch environment/config after first prompt.

### D21-06 — Normalized events
Collect sanitized normalized event sequence and continuity. Do not fabricate terminal events.

### D21-07 — External-directory denial
Attempt one bounded action targeting only the harmless outside canary. Expected DENIED/BLOCKED. Prove canary unchanged.

### D21-08 — Push denial
Attempt push only to the disposable bare remote through runtime/permission surface. Expected DENIED/BLOCKED. Prove remote ref unchanged.

### D21-09 — Allowed fixture read/edit
Prove intended fixture read/edit remains allowed under the same permission profile.

### D21-10 — Inspect + independent diff
Use candidate `inspect()`. Record runtime status, terminality, safe summary, continuity, and safe refs/diff hints if exposed. Independently compare actual Git diff.

### D21-11 — Provider/model provenance
Record requested and actual identities separately. If no true runtime-native invocation ID is exposed, require `runtime_invocation=None`. Do not manufacture identity from admitted message/inbox/input IDs.

### D21-12 — Controlled cancellation — live successor fix
Create a second fresh execution/session suitable for cancellation.

Cancel through exact bound:

```text
ExecutionId + RuntimeSessionRef
```

Fresh evidence MUST show:

```text
POST /api/session/{sessionID}/interrupt
HTTP 204 No Content

candidate cancel()
RuntimeControlAckState.REQUESTED

JSON body parse:
NO
```

Invoke the identical Relay `cancel()` request one additional time and require:

```text
second ack == cached first ack
interrupt POST count == 1
```

Prove another session is unaffected.

If execution becomes terminal before interrupt and the adapter returns `ALREADY_TERMINAL`, report that honestly and STOP: the live 204 fix has not been re-proven.

### D21-13 — Post-cancellation inspection
Inspect the exact cancelled session and record current/terminal state and continuity.

### D21-14 — Resume only if advertised
Freshly inspect descriptor capabilities. If RESUME absent, record `NOT_APPLICABLE — capability not advertised`. Do not force resume.

### D21-15 — Event-stream interruption
Interrupt only the event connection while leaving runtime/session alive. Prove continuity becomes incomplete with event-gap/stream-disconnected evidence as exposed, inspection remains possible, and no second prompt is admitted.

### D21-16 — Safe failure normalization
Cause one safe controlled local/runtime failure, preferring a harmless local/runtime failure over provider auth/billing failure. Record normalized category and sanitized diagnostics.

### D21-17 — Credential containment
Search only disposable fixture/evidence for secret-bearing markers/test sentinels without printing real secret values. Prove no Authorization header, credential assignment/value, copied `.env`, Git-diff secret, or normalized-event/failure secret persists.

### D21-18 — Distinct mock evaluator session
Create a third distinct `ExecutionId` and OpenCode session for a benign read-only/mock-review task. Prove implementation and evaluator IDs/sessions differ. This proves separation only and grants no evaluator authority.

## 13. Evidence

Write sanitized evidence only under:

```text
/tmp/relay-s21-sidecar/evidence-run-011/
```

At minimum retain:

```text
report.md
manifest.json
commands.txt
health-readiness-sequence.txt
model-query-shape.txt
sanitized-opencode-config.txt
model-preflight.txt
provider-preflight.txt
route-preflight.txt
normalized-events.jsonl
cancellation-evidence.txt
fixture-before.txt
fixture-after.txt
fixture-diff.patch
protected-v1-metadata-before.txt
protected-v1-metadata-final.txt
SHA256SUMS.txt
```

Never retain API keys, Authorization headers, transient server passwords, cookies, OAuth material, or protected V1 contents.

Compute evidence checksums immediately when the package is complete.

## 14. Required operator report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-005 — AUTHORIZED

handoff:
RLY-S21-SIDECAR-HANDOFF-005

governance head:
<exact canonical head containing these records>

candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

operator:
Codex

fresh Run 011 profile:
PASS/FAIL

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

direct V2 invocations:
0/<exact nonzero>

V2 version/hash:
<exact>

health readiness:
attempt count: <n>
first status: <exact>
final status: <exact>
elapsed to ready: <duration>
503 observed: YES/NO

candidate describe:
PASS/FAIL

model request:
GET /api/model
location[directory] encoded: PASS/FAIL
HTTP status: <exact>

model preflight:
PASS/FAIL + exact safe fields

provider preflight:
PASS/FAIL + exact safe fields

credential presence:
PASS/FAIL

route preflight:
PASS/FAIL

requested provider/model:
openrouter / google/gemini-3.8-flash

actual provider/model:
<exact or unavailable>

identity completeness:
FULL/PARTIAL/UNKNOWN

runtime_invocation:
NONE or genuine runtime-native ID

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + concise evidence

D21-12 cancellation:
interrupt HTTP status: <exact>
first ack: <exact>
second identical cancel ack: <exact>
interrupt POST count: <exact>
JSON parse required: YES/NO
other session unaffected: PASS/FAIL

fixture final diff:
<summary>

fixture tests:
<exact>

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
/tmp/relay-s21-sidecar/evidence-run-011/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.

Do not make the experiment pass by weakening identity, credentials, isolation, permissions, exact binding, one-prompt semantics, exact provider/model selection, cancellation targeting, or evidence requirements.
