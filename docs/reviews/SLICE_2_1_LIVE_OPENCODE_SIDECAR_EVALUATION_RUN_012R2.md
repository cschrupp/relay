# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 012r2

**Document class:** Immutable evaluation record
**Status:** IMMUTABLE
**Date:** 2026-10-09
**Project:** Relay
**Slice:** 2.1 — Agent Runtime Contract
**Record:** `RLY-S21-SIDECAR-EVAL-012R2`
**Outcome:** `ESCALATE`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED

Corrective handoff:
RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001

Governance head:
ed3d6662f46dd574296ce59e2ab1ec3a21eab02c

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate deterministic evaluation:
RLY-S21-EVAL-005 — ACCEPT

Exact OpenCode:
0.0.0-beta-17823

Binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

Provider/model:
openrouter / google/gemini-3.8-flash
```

## Evaluation summary

Run 012r2 stopped fail-closed at the required generic non-V2 loopback listener preflight. The single `AF_INET/SOCK_STREAM` socket attempt failed during socket creation with `EPERM` (errno 1). Bind and listen were not reached. No OpenCode invocation or server startup occurred.

The evaluation disposition is:

```text
Relay candidate defect:
NO

Accepted design defect:
NO

Implementation defect:
NO

Provider/model defect:
NO

Host/container socket/listener restriction:
ESTABLISHED

OpenCode-specific listener defect:
NOT TESTED

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49 — RLY-S21-EVAL-005 ACCEPT / UNCHANGED

Implementation rework:
NOT JUSTIFIED

Human technical acceptance:
NOT ELIGIBLE
```

The provider/model classification is limited to the fact that Run 012r2 did not reach provider/model preflight; it is not a live provider/model availability result.

## F012R2-A — PASS — fresh fixture source binding

```text
fixture source SHA:
6e962f528623693527b287647df5e1a0c7ce32e1

length:
40

lowercase hexadecimal:
PASS

leading/trailing whitespace:
NONE

embedded newline:
NONE

fixture baseline test:
1 passed
```

## F012R2-B — PASS — protected V1 ordering and final comparison

```text
protected V1 baseline:
CAPTURED AND VERIFIED BEFORE ANY V2 INVOCATION

V2 invocations:
0

final protected V1 comparison:
UNCHANGED
```

## F012R2-C — BLOCKING ENVIRONMENT PREFLIGHT — socket creation denied

The one generic listener preflight recorded:

```text
host:
127.0.0.1

port:
ephemeral unprivileged (not allocated)

socket creation:
EPERM (errno 1)

bind:
NOT REACHED

listen:
NOT REACHED
```

This establishes that the current execution environment blocks the socket capability required even to perform the generic listener experiment. It does not establish any OpenCode-specific behavior. No alternate interface, retry, workaround, endpoint selection, or server startup was attempted.

## Runtime and D21 disposition

```text
V2 version/hash:
NOT TESTED — no V2 invocation was permitted

server lifecycle:
0

server restarts:
0

health readiness:
NOT_RUN

candidate describe:
NOT_RUN

route preflight:
NOT_RUN

sessions:
0

prompts:
0

provider/model inference:
NONE

D21-01 through D21-18:
NOT_RUN
```

No prior Run-011, Run-012, or Run-012r1 PASS evidence is inherited.

## Containment

```text
candidate/source changes:
NONE

real-project calls:
NONE

credential material:
NOT RECORDED

protected V1 final comparison:
UNCHANGED
```

## Authority disposition

The exact subject and D21 scope did not change, and Run 012r2 produced zero V2 calls, sessions, prompts, or inference. Existing `RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED` remains valid for a fresh retry if candidate, runtime, provider/model, credential source, and D21 scope remain identical. No new Human Authority is required for that unchanged scope.

## Governance decision

```text
Run 012r2:
STOPPED FAIL-CLOSED AT GENERIC LISTENER PREFLIGHT

Evaluation:
RLY-S21-SIDECAR-EVAL-012R2 — ESCALATE

Generic socket creation:
EPERM (errno 1)

Host/container socket/listener restriction:
ESTABLISHED

OpenCode-specific listener defect:
NOT TESTED

Candidate status:
RLY-S21-EVAL-005 — ACCEPT / UNCHANGED

Implementation rework:
NOT AUTHORIZED / NOT JUSTIFIED

Human technical acceptance:
NOT ELIGIBLE

Next attempt:
Run 012r3

Required correction:
EXECUTION ENVIRONMENT WITH PROVEN LOOPBACK SOCKET CREATE/BIND/LISTEN CAPABILITY

Corrective handoff:
RLY-S21-SIDECAR-RUN012-EXECUTION-ENV-HANDOFF-001

New Human Authority:
NOT REQUIRED IF THE AUTHORIZED SUBJECT AND SCOPE REMAIN UNCHANGED
```

No Human technical acceptance, promotion, Slice closure, Slice 2.2, Phase 3, or real-project execution is authorized.

## Evidence

```text
/tmp/relay-s21-sidecar/evidence-run-012r2/

SHA256SUMS.txt SHA-256:
9307b4a4abafa9aebf71270f57c1ff529febfaf96b0001cf4918252ec7b2e177
```
