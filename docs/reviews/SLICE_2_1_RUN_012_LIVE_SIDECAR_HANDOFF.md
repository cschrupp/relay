# Relay — Slice 2.1 Live OpenCode Sidecar Run 012 Handoff

**Document class:** Immutable execution handoff
**Status:** IMMUTABLE
**Date:** 2026-10-08
**Record:** `RLY-S21-SIDECAR-HANDOFF-006`

## 1. Authority and exact subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED

Authority record commit:
c3f73dacf55daf82e3ea3909a8792285f4da19dd

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate evaluation:
RLY-S21-EVAL-005 — ACCEPT

Prior live evaluation:
RLY-S21-SIDECAR-EVAL-011 — ESCALATE / INCOMPLETE

Exact OpenCode:
0.0.0-beta-17823

Exact binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

Exact provider/model:
openrouter / google/gemini-3.8-flash
```

Codex is evidence operator only. It MUST NOT evaluate, accept, promote, technically accept, or close its own evidence.

## 2. Fresh evidence rule

Run 012 is a fresh candidate-specific live run.

Prior Run 011 results are historical evidence only, including:

```text
D21-12 live HTTP 204 cancellation proof
D21-01 through D21-15 results
D21-17 credential containment result
```

Do NOT mark any Run-012 D21 item PASS because it passed earlier.

Every applicable D21-01 through D21-18 item must be freshly exercised against exact candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49`.

## 3. Fresh disposable roots

Use fresh paths beneath `/tmp/relay-s21-sidecar/`:

```text
candidate-run-012
fixture-run-012
outside-canary-run-012
forbidden-remote-run-012.git
v2-profile-run-012
run-v2-isolated-run-012
evidence-run-012
```

Do not reuse Run-011 HOME/XDG/database/cache/session/workspace/fixture state.

Maintain separate governance and candidate checkouts.

Candidate checkout must be detached exactly at:

```text
4f785f08576e465cd0aa278f927fa4b7253e3f49
```

and clean before execution.

## 4. HARD ORDERING GATE — protected V1 before any V2

This order is mandatory:

```text
STEP 1:
capture protected V1 metadata witness

STEP 2:
verify witness successfully retained

STEP 3:
only then permit first V2 invocation
```

The protected-V1 metadata witness must exist before:

- `opencode2 --version`;
- help/version probes;
- server startup;
- package/native helper invocation deliberately initiated for Run 012;
- any other deliberate V2 CLI operation.

Do not inspect protected V1 contents.

Record a safe sequence witness such as:

```text
protected-v1-baseline timestamp/order marker:
BEFORE_FIRST_V2

first-v2-invocation timestamp/order marker:
AFTER_V1_BASELINE
```

If any deliberate V2 invocation precedes the baseline witness:

```text
STOP
protected V1 = NOT_ATTESTABLE
Run 012 cannot qualify
```

Do not attempt to repair this with a later snapshot.

## 5. Wrapper isolation

After the V1 baseline witness is complete, create fresh writable:

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

Every deliberate V2 invocation MUST pass through one Run-012 isolation wrapper.

Direct V2 invocation count must remain zero.

Verify exact runtime version and binary SHA through the wrapper only after the protected-V1 baseline witness exists.

## 6. Credential delivery

Use only the existing ignored/untracked repository-root `.env`.

Verify without exposing values:

```text
.env exists: PASS
.env ignored: PASS
.env untracked: PASS
OPENROUTER_API_KEY nonempty: PASS
```

Never print, inspect, hash, copy, stage, commit, or retain credential material.

No OAuth, interactive login, new credential, alternate credential source, or protected V1 credential import.

## 7. Minimum non-secret route configuration

Recreate from scratch the exact-beta non-secret route configuration:

```text
provider:
openrouter

model:
google/gemini-3.8-flash

provider package:
aisdk:@openrouter/ai-sdk-provider
```

No old profile/config/runtime state may be reused.

## 8. Bounded authenticated health readiness

Poll authenticated `GET /api/health` only after V2 startup.

Use:

```text
maximum readiness window:
30 seconds

maximum rate:
1 request per 250 ms

503:
WAITING while exact process lives

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

Retain only sanitized readiness sequence.

## 9. Candidate descriptor

Only after health PASS:

1. call successor `OpenCodeRuntime.describe()`;
2. require exact runtime/API identity;
3. perform connection-auth leak check.

Any failure is a STOP.

## 10. Exact-beta route preflight

Query MODEL catalog first.

Required semantics:

```text
GET /api/model?location[directory]=<absolute-fixture-directory>
```

Require exact model:

```text
id == "google/gemini-3.8-flash"
providerID == "openrouter"
enabled == true
status == "active"
package == "aisdk:@openrouter/ai-sdk-provider" when present
```

Then query provider list/detail and require:

```text
id == "openrouter"
activation in {"auto", "enabled"}
package == "aisdk:@openrouter/ai-sdk-provider"
```

Do NOT require nonexistent provider fields.

Separately require nonempty `OPENROUTER_API_KEY` presence.

If any route-preflight condition fails, STOP before session/prompt.

## 11. Fixture and canaries

Create a fresh tiny Git fixture with committed passing baseline.

Canonical task:

```text
Add a subtract(a, b) function to app.py and add one deterministic test.
Do not touch files outside this repository.
Do not push.
```

Create a harmless outside canary and disposable local bare remote.

No real-project source is authorized.

## 12. Fresh D21-01 through D21-18

### D21-01
Fresh runtime identity: successor SHA, runtime version, API generation, adapter version.

### D21-02
Explicit isolated loopback endpoint.

### D21-03
Exact fixture/workspace/request/source binding.

### D21-04
Programmatic session creation with exact `ExecutionId`, `RuntimeSessionRef`, and process-local binding.

### D21-05
Benign edit execution using normal `open_execution()`:

- observer before prompt;
- exactly one prompt;
- root-level exact-beta prompt body;
- no `resume:false`;
- no compensating resume;
- execution wake;
- exact authorized provider/model;
- requested fixture edit;
- no unrelated changes.

If execution fails before requested edit, STOP with sanitized evidence.

Do not patch environment/config after first prompt.

### D21-06
Fresh normalized events and continuity.

### D21-07
Fresh outside-directory denial; canary must remain unchanged.

### D21-08
Fresh push denial against disposable local bare remote; remote ref unchanged.

### D21-09
Fresh allowed fixture read/edit.

### D21-10
Fresh candidate `inspect()` plus independent Git diff.

### D21-11
Fresh requested/actual provider-model provenance. If no genuine runtime-native invocation identity exists, require `runtime_invocation=None`.

### D21-12 — cancellation proof
Create a second fresh execution/session suitable for cancellation.

Fresh evidence must show:

```text
POST /api/session/{sessionID}/interrupt
HTTP 204 No Content

candidate cancel():
REQUESTED

JSON parse:
NO

second identical cancel:
cached equal acknowledgment

interrupt POST count:
1

other session:
unaffected
```

If target becomes terminal before interrupt and returns `ALREADY_TERMINAL`, report honestly and STOP: Run-012 cancellation proof is incomplete.

### D21-13
Fresh post-cancellation inspection.

### D21-14
Resume only if freshly advertised. If absent: `NOT_APPLICABLE — capability not advertised`.

### D21-15
Fresh event-stream interruption. Prove continuity becomes incomplete, inspection remains available, and no second prompt is admitted.

### D21-16 — MUST RUN
Cause one safe controlled local/runtime failure.

Prefer a harmless local/runtime failure over provider auth/billing failure.

Require fresh evidence of:

```text
normalized failure category
sanitized safe message/diagnostic
no credential material
correct execution/session binding where applicable
```

Do not rely on prior runs.

### D21-17
Fresh credential containment proof.

### D21-18 — MUST RUN
Create a third distinct `ExecutionId` and OpenCode session for a benign read-only/mock-review task.

Require:

```text
implementation ExecutionId != mock-evaluator ExecutionId
implementation session != mock-evaluator session
mock-evaluator task is read-only/benign
no evaluator authority is granted
```

Do not rely on prior runs.

## 13. Final protected-V1 attestation

After all V2 work is stopped, capture final protected-V1 metadata using the same metadata scope as the pre-V2 baseline witness.

Require:

```text
baseline witness:
captured before first V2 invocation

final witness:
captured after all V2 activity

comparison:
UNCHANGED
```

If comparison cannot be made exactly, report `NOT_ATTESTABLE`.

## 14. Evidence package

Write sanitized evidence only under:

```text
/tmp/relay-s21-sidecar/evidence-run-012/
```

At minimum retain:

```text
report.md
manifest.json
commands.txt
ordering-witness.txt
protected-v1-metadata-before.txt
protected-v1-metadata-final.txt
health-readiness-sequence.txt
model-query-shape.txt
sanitized-opencode-config.txt
model-preflight.txt
provider-preflight.txt
route-preflight.txt
normalized-events.jsonl
cancellation-evidence.txt
failure-normalization-evidence.txt
evaluator-separation-evidence.txt
fixture-before.txt
fixture-after.txt
fixture-diff.patch
SHA256SUMS.txt
```

Never retain API keys, Authorization headers, transient passwords, cookies, OAuth material, or protected V1 contents.

Compute the checksum manifest immediately when evidence is complete.

## 15. Required operator report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED

handoff:
RLY-S21-SIDECAR-HANDOFF-006

governance head:
<exact canonical head containing these records>

candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

operator:
Codex

protected V1 baseline captured before ANY V2 invocation:
PASS/FAIL

ordering witness:
<concise>

fresh Run 012 profile:
PASS/FAIL

.env exists / ignored / untracked:
PASS/PASS/PASS

OPENROUTER_API_KEY presence:
PASS/FAIL

credential material:
NOT RECORDED

all V2 invocations through wrapper:
PASS/FAIL

direct V2 invocations:
0/<exact nonzero>

V2 version/hash:
<exact>

health readiness:
<exact concise sequence>

candidate describe:
PASS/FAIL

model request:
GET /api/model
location[directory] encoded: PASS/FAIL
HTTP status: <exact>

model preflight:
PASS/FAIL + safe exact fields

provider preflight:
PASS/FAIL + safe exact fields

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
PASS/FAIL/NOT_APPLICABLE + concise fresh evidence

D21-12:
interrupt HTTP status: <exact>
first ack: <exact>
second cancel ack: <exact>
interrupt POST count: <exact>
JSON parse required: YES/NO
other session unaffected: PASS/FAIL

D21-16:
normalized failure category: <exact>
safe diagnostic: <concise>

D21-18:
implementation/evaluator ExecutionIds distinct: PASS/FAIL
implementation/evaluator sessions distinct: PASS/FAIL

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

protected V1 final comparison:
UNCHANGED/CHANGED/NOT_ATTESTABLE

candidate/source changes:
NONE

real-project calls:
NONE

evidence package:
/tmp/relay-s21-sidecar/evidence-run-012/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.

Do not make the experiment pass by weakening identity, credentials, isolation, exact provider/model selection, binding, permissions, cancellation, failure-normalization, evaluator-separation, protected-V1 ordering, or evidence requirements.
