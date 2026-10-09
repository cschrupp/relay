# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 012r1

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-012R1`  
**Outcome:** `ESCALATE`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED

Corrective handoff:
RLY-S21-SIDECAR-RUN012-RETRY-HANDOFF-001

Governance head:
c05d7c220f0452701d0218fa0f851f5409c76bd7

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate deterministic evaluation:
RLY-S21-EVAL-005 — ACCEPT

Exact OpenCode:
0.0.0-beta-17823
```

## Evaluation summary

Run 012r1 stopped before runtime readiness, session creation, prompt admission, or provider/model inference.

The exact startup failure was retained:

```text
EPERM: operation not permitted, listen
```

The correct classification is:

```text
Relay candidate defect:
NO

accepted design defect:
NO

provider/model defect:
NO

operator source-SHA defect:
RESOLVED

protected-V1 ordering defect:
RESOLVED

listener/startup environment failure:
YES

OpenCode-specific listener defect:
NOT ESTABLISHED

implementation rework:
NOT JUSTIFIED

Human technical acceptance:
NOT ELIGIBLE
```

## F012R1-A — PASS — static binding correction

The fixture source commit was normalized and validated before server startup:

```text
fixture source SHA:
692f7ace5dbd25d64c93b818dcaa6006df08b755

length:
40

lowercase hexadecimal:
PASS

leading/trailing whitespace:
NONE

embedded newline:
NONE
```

This resolves the operator request-construction defect established by Run 012.

## F012R1-B — PASS — protected V1 ordering and final attestation

Fresh Run-012r1 evidence establishes:

```text
protected V1 baseline:
CAPTURED BEFORE ANY V2 INVOCATION

first V2 invocation:
AFTER BASELINE

final protected V1 comparison:
UNCHANGED
```

Therefore:

```text
protected V1:
ATTESTABLE / UNCHANGED
```

## F012R1-C — PASS — wrapper and single-lifecycle discipline

```text
deliberate V2 invocations:
2

all through Run-012r1 wrapper:
PASS

direct V2 invocations:
0

server starts:
1

server restarts:
0

single-server-lifecycle rule:
PASS
```

The exact runtime remained:

```text
OpenCode:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

## F012R1-D — BLOCKING STARTUP FAILURE — loopback listen denied with EPERM

The sole server process failed before readiness.

Sanitized startup diagnostics retained:

```text
process exit code:
1

startup failure:
EPERM: operation not permitted, listen
```

Health observed only CONNECTING attempts before process exit.

This establishes that the process was denied while attempting to create its listening endpoint.

It does NOT establish whether the denial arose from:

- the broader execution environment's socket-listen policy; or
- behavior specific to the exact OpenCode executable/runtime startup path.

No generic non-V2 listener capability witness was collected before V2 startup, so that distinction remains unresolved.

Therefore:

```text
listener/startup environment failure:
ESTABLISHED

candidate adapter defect:
NO

OpenCode-specific defect:
NOT ESTABLISHED

host/container listener restriction:
POSSIBLE / NOT YET ISOLATED
```

## Preflight and D21 disposition

```text
candidate describe:
NOT_RUN

model preflight:
NOT_RUN

provider preflight:
NOT_RUN

route preflight:
NOT_RUN

sessions created:
0

prompts admitted:
0

provider/model inference:
NONE

D21-01:
NOT_RUN — static candidate/binary identity checked, describe not reached

D21-02:
PASS — explicit loopback endpoint selected

D21-03:
PASS — fixture/source typed binding validated before startup

D21-04 through D21-18:
NOT_RUN
```

No Run-011 or Run-012 PASS evidence is inherited.

## Containment

```text
fixture:
UNCHANGED

fixture tests:
1 baseline test PASS

outside canary:
UNCHANGED

forbidden local remote:
UNCHANGED

credential leak check:
NOT_RUN

credential material:
NOT RECORDED

candidate/source changes:
NONE

real-project calls:
NONE
```

## Authority disposition

Existing exact-SHA Human Authority remains sufficient:

```text
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED
```

because:

```text
sessions:
0

prompts:
0

inference:
0

candidate:
UNCHANGED

runtime/provider/model scope:
UNCHANGED
```

The next retry may therefore remain under the existing Human Authority, provided it is limited to fresh disposable state plus an operator/environment listener preflight and the same already-authorized live D21 scope.

## Governance decision

```text
Run 012r1:
STOPPED FAIL-CLOSED BEFORE READINESS

Evaluation:
RLY-S21-SIDECAR-EVAL-012R1 — ESCALATE

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate status:
RLY-S21-EVAL-005 — ACCEPT / UNCHANGED

Implementation rework:
NOT AUTHORIZED / NOT JUSTIFIED

Next attempt:
Run 012r2

New Human Authority:
NOT REQUIRED

Corrective handoff:
RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001
```

No Human technical acceptance, promotion, Slice closure, Slice 2.2, Phase 3, or real-project execution is authorized.

## Evidence

```text
/tmp/relay-s21-sidecar/evidence-run-012r1/

SHA256SUMS.txt SHA-256:
43e09e4910d222c4cb9ff12f28d5881da507b6e28a9c767fd232a199df5a7445
```
