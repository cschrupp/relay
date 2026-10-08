# Relay — Slice 2.1 Run 010 Preflight Correction Handoff

**Document class:** Immutable corrective execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-RUN010-PREFLIGHT-CORRECTION-001`

## 1. Authority

This corrective handoff remains under:

```text
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED
```

and follows:

```text
RLY-S21-SIDECAR-EVAL-010 — ESCALATE
RLY-S21-SIDECAR-HEALTH-DIAG-EVAL-001 — CORRECT_RUN_010_PREFLIGHT
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

No authority scope changes.

## 2. Preserve the aborted Run-010 attempt

Do not modify or overwrite:

```text
/tmp/relay-s21-sidecar/evidence-run-010/
```

That package remains historical evidence of the preflight readiness race.

Use a new corrected-attempt namespace:

```text
/tmp/relay-s21-sidecar/candidate-run-010r1
/tmp/relay-s21-sidecar/fixture-run-010r1
/tmp/relay-s21-sidecar/outside-canary-run-010r1
/tmp/relay-s21-sidecar/forbidden-remote-run-010r1.git
/tmp/relay-s21-sidecar/v2-profile-run-010r1
/tmp/relay-s21-sidecar/run-v2-isolated-run-010r1
/tmp/relay-s21-sidecar/evidence-run-010r1
```

## 3. Recreate all original Run-010 safety gates

Recreate from scratch:

- detached exact candidate checkout;
- fresh fixture and committed baseline;
- outside canary;
- local bare remote;
- fresh V2 HOME/XDG/data/state/cache/tmp directories;
- writable OPENCODE_DB parent;
- minimum non-secret OpenRouter/model configuration;
- wrapper-only V2 execution;
- protected V1 metadata snapshots;
- ignored/untracked `.env` credential delivery;
- no secret persistence.

No old disposable runtime/profile state may be reused.

## 4. Corrected health-readiness gate

After the wrapped V2 process is reachable and connection authentication is available, perform bounded authenticated readiness polling.

Rules:

```text
maximum readiness window:
30 seconds from first authenticated health attempt

maximum request rate:
1 request per 250 ms
```

Interpret:

```text
HTTP 503:
WAITING
only while the exact V2 process remains alive

HTTP 200 with healthy=true:
READY / PASS

HTTP 401 or 403:
STOP — authentication failure

HTTP 500:
STOP — runtime/server failure

process exit:
STOP

malformed/unexpected health response:
STOP

30-second readiness timeout:
STOP
```

Record each health attempt only as sanitized:

```text
relative timestamp
HTTP status
healthy boolean if safely present
process-alive state
```

Do not retain Authorization headers or server passwords.

A 503 MUST NOT advance to candidate `describe()` or catalog checks.

## 5. Post-health ordering

Only after authenticated health reaches:

```text
HTTP 200
healthy=true
```

continue:

1. unchanged candidate `OpenCodeRuntime.describe()`;
2. connection-auth leak check;
3. model catalog query FIRST as the exact-beta initialization synchronization point;
4. verify `google/gemini-3.8-flash` active/enabled;
5. provider catalog query SECOND;
6. verify `openrouter` active;
7. verify provider package `aisdk:@openrouter/ai-sdk-provider`.

If route preflight fails, STOP before prompt.

## 6. D21

After all corrected preflight gates pass, execute the original canonical Run-010 D21-01 through D21-18 requirements from:

```text
docs/reviews/SLICE_2_1_RUN_010_LIVE_SIDECAR_HANDOFF.md
```

All original constraints remain in force, including:

- exact one-prompt semantics;
- observer before prompt;
- no `resume:false`;
- no compensating resume;
- exact provider/model only;
- minimum provider/model calls;
- `runtime_invocation=None` valid when no true invocation ID exists;
- outside-canary denial;
- local push denial;
- exact cancellation/inspection binding;
- event-gap behavior;
- credential leak proof;
- distinct mock-evaluator session;
- no real-project work;
- no candidate changes.

## 7. Evidence

Write corrected-attempt evidence only beneath:

```text
/tmp/relay-s21-sidecar/evidence-run-010r1/
```

At minimum retain the original Run-010 required evidence plus:

```text
health-readiness-sequence.txt
```

The report must clearly distinguish:

```text
Run 010 initial attempt:
ABORTED PRE-D21 / preserved separately

Run 010 corrected attempt:
010r1
```

## 8. Required operator report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

corrective handoff:
RLY-S21-SIDECAR-RUN010-PREFLIGHT-CORRECTION-001

governance head:
<exact>

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

attempt:
Run 010r1

new Human Authority:
NOT REQUIRED — SAME AUTHORITY / NO SCOPE EXPANSION

fresh disposable profile:
PASS/FAIL

health readiness:
attempt count: <n>
first status: <status>
final status: <status>
elapsed to ready: <duration or unavailable>
503 observed: YES/NO
readiness timeout: YES/NO

candidate describe:
PASS/FAIL/NOT_RUN

route preflight:
provider openrouter active: PASS/FAIL/NOT_RUN
model google/gemini-3.8-flash active: PASS/FAIL/NOT_RUN
provider package: PASS/FAIL/NOT_RUN

new prompts:
<exact count>

new inference calls:
<minimum exact count or unavailable>

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + concise evidence

candidate/source changes:
NONE

real-project calls:
NONE

protected V1:
UNCHANGED/CHANGED/NOT_ATTESTABLE

credential material:
NOT RECORDED

evidence package:
/tmp/relay-s21-sidecar/evidence-run-010r1/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
