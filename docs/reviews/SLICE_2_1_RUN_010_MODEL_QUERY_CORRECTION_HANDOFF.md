# Relay — Slice 2.1 Run 010 Model Query Correction Handoff

**Document class:** Immutable corrective execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Record:** `RLY-S21-SIDECAR-RUN010-MODEL-QUERY-CORRECTION-001`

## 1. Authority

Operate under unchanged Human Authority:

```text
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED
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

## 2. Attempt

Use a fresh attempt:

```text
Run 010r3
```

with fresh disposable paths ending in `run-010r3`.

Do not reuse Run-010r2 HOME/XDG/DB/session/fixture state.

## 3. Preserve all accepted prior corrections

Retain unchanged:

- bounded health readiness with HTTP 503 as WAITING;
- exact candidate `describe()` gate;
- model catalog before provider catalog;
- corrected exact-beta provider predicate using `id`, `activation`, and root `package`;
- exact model predicate using `id`, `providerID`, `enabled`, `status`, and optional `package`;
- separate credential-presence gate;
- all credential/isolation/permission/D21 constraints.

## 4. Exact model-catalog request encoding

For the exact-beta model-catalog request, encode the workspace location as the route's nested query parameter.

Required semantic request:

```text
GET /api/model?location[directory]=<absolute-fixture-directory>
```

If a workspace value is required by the exact beta, encode it separately as:

```text
location[workspace]=<workspace-id>
```

Do NOT send location as:

- a JSON request body;
- a JSON-encoded query value;
- an unrelated top-level `directory` key.

Percent-encoding performed by the HTTP client is acceptable provided the decoded query semantics are exactly `location[directory]`.

Retain sanitized evidence of:

```text
HTTP method
route path
query key names
HTTP status
```

Do not retain authentication material.

If this exact request returns HTTP 400 again, STOP and capture the sanitized response contract/error; do not improvise another request form.

## 5. Corrected route preflight

After model-list HTTP 200, apply the already-canonical predicates.

### Model

Require:

```text
id == "google/gemini-3.8-flash"
providerID == "openrouter"
enabled == true
status == "active"
```

If model `package` is present:

```text
package == "aisdk:@openrouter/ai-sdk-provider"
```

### Provider

Then query provider list/detail with the same exact-beta location-query semantics.

Require:

```text
id == "openrouter"
activation in {"auto", "enabled"}
package == "aisdk:@openrouter/ai-sdk-provider"
```

Do not require nonexistent provider fields.

### Credential

Separately require `OPENROUTER_API_KEY` presence in the isolated environment without inspecting or persisting its value.

## 6. D21

Only after corrected route preflight PASS, execute the unchanged canonical Run-010 D21-01 through D21-18 protocol.

All prior exact-binding, one-prompt, observer-before-prompt, containment, provider/model identity, cancellation, inspection, event-continuity, credential-leak, and mock-evaluator separation requirements remain binding.

## 7. Evidence

Use a fresh evidence directory:

```text
/tmp/relay-s21-sidecar/evidence-run-010r3/
```

Retain at minimum the prior Run-010r2 evidence set plus:

```text
model-query-shape.txt
```

This file should record only the sanitized route/method/query-key shape and response status.

## 8. Required report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

corrective handoff:
RLY-S21-SIDECAR-RUN010-MODEL-QUERY-CORRECTION-001

governance head:
<exact>

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

attempt:
Run 010r3

new Human Authority:
NOT REQUIRED

health readiness:
PASS/FAIL

candidate describe:
PASS/FAIL/NOT_RUN

model-catalog request:
method: GET
path: /api/model
location[directory] encoded: PASS/FAIL
HTTP status: <exact>

corrected model preflight:
PASS/FAIL/NOT_RUN

corrected provider preflight:
PASS/FAIL/NOT_RUN

credential presence:
PASS/FAIL

route preflight:
PASS/FAIL

new prompts:
<exact count>

new inference calls:
<minimum exact count or unavailable>

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + concise evidence

protected V1:
UNCHANGED/CHANGED/NOT_ATTESTABLE

candidate/source changes:
NONE

real-project calls:
NONE

credential material:
NOT RECORDED

evidence package:
/tmp/relay-s21-sidecar/evidence-run-010r3/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
