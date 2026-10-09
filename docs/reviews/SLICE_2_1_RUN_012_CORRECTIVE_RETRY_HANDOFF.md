# Relay — Slice 2.1 Run 012 Corrective Retry Handoff

**Document class:** Immutable corrective execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Record:** `RLY-S21-SIDECAR-RUN012-RETRY-HANDOFF-001`

## 1. Authority

Operate under unchanged Human Authority:

```text
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED
```

Independent Run-012 evaluation:

```text
RLY-S21-SIDECAR-EVAL-012 — ESCALATE
```

Exact subject remains:

```text
candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

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
Run 012r1
```

Use entirely fresh disposable state with paths ending in `run-012r1`.

Do not reuse Run-012 HOME/XDG/database/cache/session/workspace/fixture/runtime state.

Prior Run-012 evidence remains historical only.

## 3. Mandatory static-input preparation before startup

Create the fresh fixture and committed baseline before live server startup.

Derive the exact fixture commit using a commit-resolving Git command such as:

```text
git rev-parse --verify HEAD^{commit}
```

Normalize the operator variable before request construction and require:

```text
^[0-9a-f]{40}$
```

with:

```text
length:
40

leading whitespace:
NONE

trailing whitespace:
NONE

embedded newline:
NONE
```

Record only the safe exact SHA in evidence.

If the fixture source commit fails this validation:

```text
STOP
```

Do not start or restart V2 to repair it.

No request object may be constructed from an unvalidated source-commit string.

## 4. Protected-V1 ordering remains mandatory

Freshly capture protected-V1 metadata before ANY V2 invocation.

Required order:

```text
protected V1 baseline witness
    ↓
fixture/source static-input validation complete
    ↓
first wrapped V2 invocation
```

No V2 version/help/server/utility call may precede the V1 baseline witness.

At end of run, compare final metadata using the same scope and require `UNCHANGED`.

## 5. Fresh wrapper/profile

After the V1 witness and static-input validation are complete, create fresh writable Run-012r1 HOME/XDG/data/state/cache/tmp/DB paths.

Every deliberate V2 invocation must use the Run-012r1 wrapper.

Direct V2 invocation count must remain zero.

Verify exact runtime version/hash only through the wrapper.

## 6. Single-server-lifecycle rule

Run 012r1 uses one fresh live server lifecycle.

After the live server starts:

- do not restart it within the same attempt;
- do not create a continuation server;
- do not patch operator inputs or runtime configuration and then restart;
- if any pre-session operator input or request-construction error is discovered, STOP the attempt and report it;
- if readiness fails or the server exits, STOP and retain the safe startup diagnostics.

If startup/readiness fails, retain at minimum:

```text
server process exit code if available
sanitized stderr/log tail
readiness sequence
process-alive transitions
profile paths
exact runtime version/hash
```

Never retain credentials.

The goal is to avoid mixing evidence across multiple server lifecycles.

## 7. Health and route preflight

Retain the established corrected semantics:

- authenticated health;
- 30-second bounded window;
- at most one request per 250 ms;
- 503 means WAITING only while process lives;
- 200 + `healthy=true` means PASS;
- 401/403/500/process exit/malformed/timeout means STOP.

Model catalog remains first:

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

Require exact provider:

```text
id == "openrouter"
activation in {"auto", "enabled"}
package == "aisdk:@openrouter/ai-sdk-provider"
```

Credential presence remains a separate non-secret gate.

## 8. D21

Only after the single server is healthy, candidate `describe()` passes, and route preflight passes, execute a complete fresh D21-01 through D21-18.

No D21 PASS result from Run 012 or Run 011 may be inherited.

All prior exact binding, one-prompt, observer-before-prompt, permission, containment, provenance, cancellation, event-continuity, safe-failure, credential, and evaluator-separation requirements remain binding.

In particular:

### D21-12

Freshly prove exact-beta cancellation:

```text
HTTP 204 No Content
first ack = REQUESTED
second identical cancel = cached equal ack
interrupt POST count = 1
JSON parse = NO
other session unaffected
```

### D21-16

MUST RUN fresh safe failure normalization and retain sanitized normalized category/diagnostic.

### D21-18

MUST RUN fresh distinct benign read-only mock-evaluator session and prove distinct ExecutionId/session identity.

## 9. Evidence

Use fresh evidence only under:

```text
/tmp/relay-s21-sidecar/evidence-run-012r1/
```

Add explicit files:

```text
fixture-source-sha-validation.txt
server-lifecycle.txt
startup-diagnostics.txt
```

alongside the existing Run-012 required evidence set.

Compute `SHA256SUMS.txt` immediately on completion.

## 10. Required report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED

corrective handoff:
RLY-S21-SIDECAR-RUN012-RETRY-HANDOFF-001

attempt:
Run 012r1

governance head:
<exact>

candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

new Human Authority:
NOT REQUIRED

fixture source SHA:
<exact>

fixture source SHA validation:
40 lowercase hex: PASS/FAIL
leading/trailing whitespace: NONE/<exact>
embedded newline: NONE/<exact>

protected V1 baseline before any V2:
PASS/FAIL

single server lifecycle:
PASS/FAIL

server restart count:
0/<exact>

health readiness:
PASS/FAIL + concise sequence

candidate describe:
PASS/FAIL/NOT_RUN

model preflight:
PASS/FAIL/NOT_RUN

provider preflight:
PASS/FAIL/NOT_RUN

route preflight:
PASS/FAIL/NOT_RUN

sessions created:
<exact>

prompts admitted:
<exact>

provider/model inference:
<exact/minimum or unavailable>

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + concise fresh evidence

D21-12:
<exact>

D21-16:
<exact>

D21-18:
<exact>

protected V1 final comparison:
UNCHANGED/CHANGED/NOT_ATTESTABLE

candidate/source changes:
NONE

real-project calls:
NONE

credential material:
NOT RECORDED

evidence package:
/tmp/relay-s21-sidecar/evidence-run-012r1/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
