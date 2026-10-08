# Relay — Slice 2.1 Run 010 Provider Preflight Correction Handoff

**Document class:** Immutable corrective execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Record:** `RLY-S21-SIDECAR-RUN010-PROVIDER-PREFLIGHT-CORRECTION-001`

## 1. Authority

This corrective handoff remains under:

```text
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED
```

and follows:

```text
RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE
RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001 — CORRECT_RUN_010_PROVIDER_PREFLIGHT
```

Exact subject remains:

```text
candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

OpenCode:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

provider/model:
openrouter / google/gemini-3.8-flash
```

No Human Authority scope changes.

## 2. Attempt identity

The next attempt is:

```text
Run 010r2
```

Use entirely fresh disposable state:

```text
/tmp/relay-s21-sidecar/candidate-run-010r2
/tmp/relay-s21-sidecar/fixture-run-010r2
/tmp/relay-s21-sidecar/outside-canary-run-010r2
/tmp/relay-s21-sidecar/forbidden-remote-run-010r2.git
/tmp/relay-s21-sidecar/v2-profile-run-010r2
/tmp/relay-s21-sidecar/run-v2-isolated-run-010r2
/tmp/relay-s21-sidecar/evidence-run-010r2
```

Do not reuse runtime state from prior attempts.

The restored exact V2 binary may be reused only after verifying its exact version/hash:

```text
/tmp/relay-s21-sidecar/v2-recovery-001/runtime/npm/bin/opencode2

version:
0.0.0-beta-17823

SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

If missing again, use the already-authorized full-isolation provisioning procedure before continuing.

## 3. Recreate all safety gates

Recreate from scratch:

- exact detached candidate checkout;
- fresh disposable fixture and committed baseline;
- outside canary;
- disposable local bare remote;
- fresh V2 HOME/XDG/data/state/cache/tmp profile;
- writable `OPENCODE_DB` parent;
- minimum non-secret OpenRouter/model configuration;
- wrapper-only V2 execution;
- protected V1 metadata witness;
- ignored/untracked repository-root `.env` credential delivery;
- transient loopback connection authentication.

No candidate or Relay source changes.

## 4. Health readiness

Use the accepted bounded health-readiness correction from:

```text
RLY-S21-SIDECAR-HEALTH-DIAG-EVAL-001
RLY-S21-SIDECAR-RUN010-PREFLIGHT-CORRECTION-001
```

Rules remain:

```text
maximum readiness window:
30 seconds from first authenticated health attempt

maximum request rate:
1 per 250 ms

HTTP 503:
WAITING while exact process remains alive

HTTP 200 + healthy=true:
PASS

HTTP 401/403:
STOP

HTTP 500:
STOP

process exit:
STOP

malformed/unexpected response:
STOP

timeout:
STOP
```

Do not advance while health remains 503.

## 5. Candidate descriptor

After health PASS:

1. call unchanged candidate `OpenCodeRuntime.describe()`;
2. require exact runtime/API identity;
3. run the connection-auth leak check.

Any failure remains a STOP.

## 6. Corrected exact-beta route preflight

Query the model catalog first as the exact-beta initialization synchronization point.

### Model predicate

Require one exact model record satisfying:

```text
id == "google/gemini-3.8-flash"
providerID == "openrouter"
enabled == true
status == "active"
```

If `package` is present on that model record, require:

```text
package == "aisdk:@openrouter/ai-sdk-provider"
```

### Provider predicate

Then query provider list and/or exact provider detail.

Require an exact provider record satisfying:

```text
id == "openrouter"

activation == "enabled"
OR
activation == "auto"

package == "aisdk:@openrouter/ai-sdk-provider"
```

Do NOT require nonexistent exact-beta fields:

```text
active
enabled boolean
disabled boolean
api.type
api.package
```

Do NOT treat their absence as failure.

### Credential-presence predicate

Separately require:

```text
OPENROUTER_API_KEY present/nonempty in isolated process environment:
PASS
```

Do not infer credential consumption from this.

### Route preflight PASS

Route preflight passes only if:

```text
health ready
candidate describe PASS
exact model predicate PASS
exact provider predicate PASS
credential presence PASS
```

This remains non-inference readiness evidence only.

## 7. D21

Only after corrected route preflight PASS, execute the complete original Run-010 D21 protocol from:

```text
docs/reviews/SLICE_2_1_RUN_010_LIVE_SIDECAR_HANDOFF.md
```

with all later corrections incorporated.

Core invariants remain:

- observer before prompt;
- exactly one prompt for normal D21-05 execution;
- root-level prompt body;
- no `resume:false`;
- no compensating resume;
- exact provider/model only;
- minimum necessary provider/model calls;
- requested fixture edit only;
- no unrelated fixture mutation;
- outside-canary denial;
- disposable push denial;
- exact inspect/cancel binding;
- event continuity evidence;
- safe failure normalization;
- credential leak proof;
- distinct mock-evaluator session;
- no real-project work.

For this beta/candidate:

```text
runtime_invocation = None
```

remains valid unless a true runtime-native invocation ID is exposed.

Do not fabricate an invocation identity.

## 8. Stop conditions

STOP if:

- exact candidate/runtime/hash differs;
- health fails under corrected readiness semantics;
- corrected model/provider predicates fail;
- exact provider/model changes or falls back;
- credential containment fails;
- execution returns route unavailable;
- prompt admission/wake regresses;
- requested fixture edit does not occur;
- any D21 containment/binding invariant fails;
- candidate/source modification appears necessary.

Do not patch environment or preflight after the first prompt.

## 9. Evidence

Write fresh evidence only to:

```text
/tmp/relay-s21-sidecar/evidence-run-010r2/
```

Retain at minimum:

```text
report.md
manifest.json
commands.txt
health-readiness-sequence.txt
sanitized-opencode-config.txt
model-preflight.txt
provider-preflight.txt
route-preflight.txt
normalized-events.jsonl
fixture-before.txt
fixture-after.txt
fixture-diff.patch
protected-v1-metadata-before.txt
protected-v1-metadata-final.txt
SHA256SUMS.txt
```

Preserve only sanitized provider/model fields required by the corrected predicates.

Never retain secret values, Authorization headers, server passwords, cookies, or protected V1 contents.

Because prior `/tmp` evidence was lost after a forced restart, compute and report `SHA256SUMS.txt` immediately when the package is complete.

Do not reconstruct missing historical raw evidence.

## 10. Required operator report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

corrective handoff:
RLY-S21-SIDECAR-RUN010-PROVIDER-PREFLIGHT-CORRECTION-001

governance head:
<exact>

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

attempt:
Run 010r2

new Human Authority:
NOT REQUIRED

exact V2 version/hash:
<exact>

fresh disposable profile:
PASS/FAIL

health readiness:
PASS/FAIL + concise sequence

candidate describe:
PASS/FAIL/NOT_RUN

corrected model preflight:
id: PASS/FAIL
providerID=openrouter: PASS/FAIL
enabled=true: PASS/FAIL
status=active: PASS/FAIL
package: PASS/FAIL/NOT_PRESENT

corrected provider preflight:
id=openrouter: PASS/FAIL
activation: <exact>
activation acceptable: PASS/FAIL
package: <safe exact value>
package match: PASS/FAIL

credential presence:
PASS/FAIL

route preflight:
PASS/FAIL

new prompts:
<exact count>

new inference calls:
<minimum exact count or unavailable>

requested provider/model:
openrouter / google/gemini-3.8-flash

actual provider/model:
<exact or unavailable>

runtime_invocation:
NONE or genuine runtime-native identity

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

protected V1:
UNCHANGED/CHANGED/NOT_ATTESTABLE

candidate/source changes:
NONE

real-project calls:
NONE

evidence package:
/tmp/relay-s21-sidecar/evidence-run-010r2/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Codex remains evidence operator only.

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
