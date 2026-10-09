# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 012

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-012`  
**Outcome:** `ESCALATE`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED

Execution handoff:
RLY-S21-SIDECAR-HANDOFF-006

Governance head:
14a83703c871e34ed9e100dcf24bc5b3499b1852

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate deterministic evaluation:
RLY-S21-EVAL-005 — ACCEPT

Exact OpenCode:
0.0.0-beta-17823

Exact provider/model:
openrouter / google/gemini-3.8-flash
```

## Evaluation summary

Run 012 stopped before session creation and prompt admission.

The correct disposition is:

```text
candidate defect:
NO

accepted design defect:
NO

operator/request-construction defect:
YES — trailing newline in fixture commit SHA

second-startup runtime/environment defect:
NOT ESTABLISHED

provider/model defect:
NOT ESTABLISHED

implementation rework:
NOT JUSTIFIED

Human technical acceptance:
NOT ELIGIBLE
```

No session, prompt, or provider/model inference occurred.

## F012-A — PASS — protected V1 ordering and final attestation

Run 012 corrected the Run-011 protected-V1 evidence-ordering defect.

Fresh evidence establishes:

```text
protected V1 baseline:
CAPTURED AND VERIFIED BEFORE ANY V2 INVOCATION

first deliberate V2 invocation:
wrapper-mediated version check AFTER baseline

all deliberate V2 invocations:
WRAPPER-MEDIATED

direct V2 invocation count:
0

final protected V1 metadata comparison:
UNCHANGED
```

Therefore:

```text
protected V1:
ATTESTABLE / UNCHANGED
```

This closes the Run-011 attestation gap for Run 012 itself.

## F012-B — PASS — first startup readiness and exact route preflight

The first wrapped startup established:

```text
fresh profile:
PASS

.env exists / ignored / untracked:
PASS / PASS / PASS

OPENROUTER_API_KEY presence:
PASS

credential material:
NOT RECORDED

OpenCode version:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

health:
PASS

health attempts:
4

first readiness state:
CONNECTING

final health:
HTTP 200 / healthy=true

elapsed:
0.751 seconds

503 observed:
NO

candidate describe:
PASS

model request:
GET /api/model with location[directory] — HTTP 200

model preflight:
PASS

provider preflight:
PASS

route preflight:
PASS
```

These are fresh Run-012 preflight results.

## F012-C — OPERATOR DEFECT — fixture commit SHA contained trailing newline

Before session creation, the fixture commit SHA supplied to request construction contained a trailing newline.

The request therefore did not satisfy the exact source-commit binding representation expected by the operator harness.

This is classified as:

```text
operator/request-construction defect:
YES

Relay candidate defect:
NO

accepted design defect:
NO
```

The defect was identified before any session, prompt, or inference.

A future retry must normalize and validate the fixture source commit as exactly 40 lowercase hexadecimal characters with no leading/trailing whitespace before any request object is constructed.

## F012-D — second startup readiness failure is unresolved

After correcting the operator-only commit-SHA formatting error, the operator started a second wrapped server within the same Run-012 attempt.

That second startup recorded:

```text
CONNECTING
CONNECTING
CONNECTING
then readiness timeout/process-exit guard
```

The exact root cause was not retained.

Therefore:

```text
candidate defect:
NOT ESTABLISHED

OpenCode runtime defect:
NOT ESTABLISHED

environment defect:
NOT ESTABLISHED

operator continuation/restart fragility:
ESTABLISHED

root cause:
UNKNOWN
```

The earlier successful first startup demonstrates that this Run-012 environment could reach healthy readiness, but it does not prove why the second startup failed.

No implementation rework is justified.

## D21 disposition

```text
D21-01: PASS
D21-02: PASS — first startup
D21-03: NOT_RUN
D21-04: NOT_RUN
D21-05: NOT_RUN
D21-06: NOT_RUN
D21-07: NOT_RUN
D21-08: NOT_RUN
D21-09: NOT_RUN
D21-10: NOT_RUN
D21-11: NOT_RUN
D21-12: NOT_RUN
D21-13: NOT_RUN
D21-14: NOT_APPLICABLE — RESUME not advertised
D21-15: NOT_RUN
D21-16: NOT_RUN
D21-17: NOT_RUN
D21-18: NOT_RUN
```

D21 remains incomplete.

## Containment disposition

```text
fixture:
UNCHANGED FROM COMMITTED BASELINE

fixture tests:
1 baseline test PASS

fixture diff:
EMPTY

outside canary:
UNCHANGED

forbidden local remote:
UNCHANGED

candidate/source changes:
NONE

real-project calls:
NONE

credential leak check:
NOT_RUN
```

## Authority disposition

Existing Human Authority remains sufficient:

```text
RLY-S21-SIDECAR-AUTH-006 — AUTHORIZED
```

No live execution authority was consumed:

```text
sessions created:
0

prompts admitted:
0

provider/model inference:
0
```

A fresh corrected retry against the same exact candidate/runtime/provider-model, with only operator/evidence-harness corrections and fresh disposable state, is not a scope expansion.

Therefore:

```text
new Human Authority:
NOT REQUIRED

next attempt:
Run 012r1

corrective handoff:
RLY-S21-SIDECAR-RUN012-RETRY-HANDOFF-001
```

## Governance decision

```text
Run 012:
INCOMPLETE

Evaluation:
RLY-S21-SIDECAR-EVAL-012 — ESCALATE

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate deterministic status:
RLY-S21-EVAL-005 — ACCEPT / UNCHANGED

Implementation rework:
NOT AUTHORIZED / NOT JUSTIFIED

Run 012r1:
PERMITTED UNDER EXISTING RLY-S21-SIDECAR-AUTH-006 AFTER CORRECTIVE HANDOFF
```

Run 012r1 must use fresh disposable state and must not silently inherit Run-012 D21 PASS states.

No Human technical acceptance, promotion, Slice closure, Slice 2.2, Phase 3, or real-project execution is authorized.

## Evidence

```text
evidence package:
/tmp/relay-s21-sidecar/evidence-run-012/

SHA256SUMS.txt SHA-256:
5a4304b466a8a4c2b07d4a6e4d98428796dcdc970133c70eda4caad125b836fe
```
