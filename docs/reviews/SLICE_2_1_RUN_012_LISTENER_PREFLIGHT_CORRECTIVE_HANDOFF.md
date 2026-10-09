# Relay — Slice 2.1 Run 012 Listener Preflight Corrective Handoff

**Document class:** Immutable corrective execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Record:** `RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001`

## 1. Authority

Operate under unchanged Human Authority:

```text
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED
```

Independent Run-012r1 evaluation:

```text
RLY-S21-SIDECAR-EVAL-012R1 — ESCALATE
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

## 2. Attempt

Next attempt:

```text
Run 012r2
```

Use entirely fresh disposable paths ending in `run-012r2`.

Do not reuse any Run-012r1 HOME/XDG/database/cache/session/workspace/fixture/server state.

## 3. Preserve all corrected preconditions

Before any V2 invocation:

1. create and commit the fresh fixture;
2. resolve source commit;
3. normalize and validate exact source SHA against `^[0-9a-f]{40}$`;
4. capture protected-V1 metadata baseline;
5. verify the baseline witness exists;
6. only then permit the first wrapped V2 invocation.

No deliberate V2 call may occur before the V1 baseline witness.

At end, final V1 metadata must compare `UNCHANGED`.

## 4. Non-V2 listener capability preflight — REQUIRED

Before starting the OpenCode server, perform one bounded generic loopback-listener capability check using a non-V2 runtime already available in the operator environment, such as Python standard-library sockets.

The purpose is only to distinguish host/container listener policy from OpenCode-specific startup behavior.

Requirements:

- bind only to loopback;
- use an unprivileged ephemeral or explicitly selected unprivileged port;
- do not contact any external network;
- listen briefly;
- close immediately;
- retain only safe endpoint/errno/result metadata;
- do not retain credentials.

Required result:

```text
generic loopback bind/listen:
PASS
```

If the generic loopback bind/listen returns `EPERM`, `EACCES`, or otherwise cannot listen:

```text
STOP BEFORE V2 SERVER START
```

Report the host/container listener restriction and do not invoke live OpenCode server startup.

If generic loopback bind/listen PASSes, continue.

## 5. Endpoint selection

Choose the exact OpenCode loopback endpoint only after the generic listener preflight passes.

Require:

- loopback host only;
- unprivileged port;
- endpoint string free of whitespace/newlines;
- selected port not already occupied at preflight time.

Record only safe endpoint metadata.

Do not use privileged ports.

## 6. Wrapper/profile

Create fresh Run-012r2 isolated HOME/XDG/data/state/cache/tmp/DB paths.

Every deliberate V2 invocation must pass through the Run-012r2 wrapper.

Direct V2 invocation count must remain zero.

Verify exact runtime version/hash through wrapper only.

## 7. Single server lifecycle

Run 012r2 gets exactly one OpenCode server lifecycle.

No restart.
No continuation server.
No in-attempt patch-and-restart.

If V2 startup fails:

- STOP;
- retain process exit code;
- retain sanitized startup stderr/log tail;
- retain readiness sequence;
- retain process-alive transition;
- retain the prior generic listener-preflight result.

This distinction is required:

### Case A — generic listener preflight FAILS

Classify only:

```text
host/container listener restriction:
ESTABLISHED
OpenCode-specific listener defect:
NOT TESTED
```

### Case B — generic listener preflight PASSES, OpenCode listen returns EPERM

Classify only:

```text
generic host/container loopback listening:
AVAILABLE

OpenCode startup listener failure:
ESTABLISHED

OpenCode-specific or wrapper/runtime startup interaction:
NARROWED / REQUIRES EVALUATION
```

Do not modify candidate source.

## 8. Health and route preflight

If server starts, use existing corrected health policy:

- authenticated health;
- 30-second maximum;
- <= 1 request / 250 ms;
- 503 = WAITING only while exact process lives;
- 200 + healthy=true = PASS;
- 401/403/500/process exit/malformed/timeout = STOP.

Then:

1. candidate `describe()`;
2. connection-auth leak gate;
3. model catalog first with exact nested `location[directory]`;
4. exact model predicate;
5. exact provider predicate;
6. separate credential-presence gate.

Only after route preflight PASS may session creation occur.

## 9. D21

If startup/readiness/preflight all pass, execute complete fresh D21-01 through D21-18.

No prior PASS may be inherited.

All Run-012 requirements remain binding, including:

- observer before prompt;
- one prompt per execution;
- exact provider/model;
- no fallback;
- exact binding;
- containment/permissions;
- inspection/diff;
- `runtime_invocation=None` unless genuine runtime-native ID exists;
- D21-12 exact HTTP-204 cancellation proof;
- D21-16 safe failure normalization;
- D21-18 distinct benign read-only mock-evaluator session;
- credential containment;
- final protected-V1 attestation.

## 10. Evidence

Use only:

```text
/tmp/relay-s21-sidecar/evidence-run-012r2/
```

At minimum add:

```text
listener-preflight.txt
selected-endpoint.txt
startup-diagnostics.txt
server-lifecycle.txt
fixture-source-sha-validation.txt
ordering-witness.txt
```

plus the normal Run-012 evidence set.

## 11. Required report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED

corrective handoff:
RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001

attempt:
Run 012r2

governance head:
<exact>

candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

new Human Authority:
NOT REQUIRED

fixture source SHA validation:
PASS/FAIL

protected V1 baseline before any V2:
PASS/FAIL

generic loopback listener preflight:
PASS/FAIL

generic listener errno/result:
<safe exact>

selected loopback endpoint:
<safe exact>

all V2 invocations through wrapper:
PASS/FAIL

direct V2 invocations:
<exact>

server lifecycle count:
<exact>

server restart count:
0/<exact>

server exit code:
<exact or N/A>

startup diagnostic:
<safe concise>

health readiness:
PASS/FAIL/NOT_RUN + concise sequence

candidate describe:
PASS/FAIL/NOT_RUN

route preflight:
PASS/FAIL/NOT_RUN

sessions created:
<exact>

prompts admitted:
<exact>

provider/model inference:
<exact/minimum/none>

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + concise fresh evidence

protected V1 final comparison:
UNCHANGED/CHANGED/NOT_ATTESTABLE

candidate/source changes:
NONE

real-project calls:
NONE

credential material:
NOT RECORDED

evidence package:
/tmp/relay-s21-sidecar/evidence-run-012r2/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
