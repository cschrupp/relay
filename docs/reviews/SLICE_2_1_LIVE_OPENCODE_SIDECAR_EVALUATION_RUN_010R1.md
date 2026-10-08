# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 010r1

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-010R1`  
**Outcome:** `ESCALATE`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

Corrective handoff:
RLY-S21-SIDECAR-RUN010-PREFLIGHT-CORRECTION-001

Governance head:
828357ef4cadc741a6139d90c75f48fc6ae6b2bb

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Candidate evaluation:
RLY-S21-EVAL-004 — ACCEPT
```

## Run result

Run 010r1 corrected the readiness race successfully.

Established:

```text
fresh disposable profile:
PASS

exact beta:
0.0.0-beta-17823 — PASS

wrapper-only V2 execution:
PASS

protected V1:
UNCHANGED

authenticated health:
HTTP 200 / healthy=true — PASS

health attempts:
1

candidate OpenCodeRuntime.describe():
PASS

connection-auth leak check:
PASS

new prompts:
0

provider/model inference calls:
0
```

The route preflight then produced:

```text
model catalog:
PASS

exact model:
google/gemini-3.8-flash

model enabled:
true

model status:
active

model-associated provider package:
aisdk:@openrouter/ai-sdk-provider

provider list/detail HTTP:
200

provider identity/activation/package proof from retained sanitized provider result:
NOT VERIFIED
```

The operator stopped before session creation or D21, as required.

## F010R1-A — health-preflight correction resolved

The prior transient-readiness issue is resolved operationally.

Run 010r1 reached healthy state on the first authenticated attempt, then candidate `describe()` passed.

No candidate or runtime defect is implicated.

## F010R1-B — exact model-side route evidence passed

The exact-beta model catalog exposed the authorized model as enabled and active and associated it with the OpenRouter provider package.

This materially differs from Run 009's prior `provider.no-route` failure.

The model-side catalog portion of the environment correction is live-reproduced in the fresh Run-010r1 profile.

## F010R1-C — provider-preflight evidence is insufficient, not a proven provider failure

The provider catalog/detail requests returned HTTP 200.

However, the retained sanitized result did not expose enough provider identity/readiness/package fields to satisfy the canonical preflight assertion:

```text
provider openrouter active
provider package aisdk:@openrouter/ai-sdk-provider
```

Therefore the correct classification is:

```text
provider absence:
NOT ESTABLISHED

provider route failure:
NOT ESTABLISHED

provider readiness:
NOT PROVEN

provider preflight evidence:
INSUFFICIENT
```

A successful HTTP 200 alone does not satisfy the gate, but neither does the missing retained field prove failure.

## F010R1-D — preflight contract/capture shape requires exact-beta inspection

The next step is to inspect the exact installed beta's provider-list/detail response schemas and the already-retained Run-010r1 response evidence.

The diagnostic must determine:

1. which provider identity/readiness/package fields the exact beta actually exposes;
2. whether the provider response nests those fields differently than the Run-010r1 sanitizer expected;
3. whether the sanitizer/capture omitted fields that existed in the response;
4. whether the exact beta exposes an `active` provider field at all;
5. what minimum non-inference provider-readiness predicate is actually representable without weakening the authorized route constraint.

Do not substitute current upstream OpenCode schema for exact-beta evidence.

## Candidate/design disposition

```text
Relay candidate defect:
NO

accepted Slice 2.1 design defect:
NO

environment correction regression:
NOT ESTABLISHED

provider preflight specification/evidence issue:
ESTABLISHED

candidate:
UNCHANGED

candidate evaluation:
RLY-S21-EVAL-004 — ACCEPT
```

## D21 disposition

D21 did not start.

The pre-D21 descriptor again did not advertise RESUME, but that observation is not counted as a completed D21 run because route preflight never passed.

```text
D21-01 through D21-18:
NOT_RUN
```

## Governance decision

```text
Run 010r1:
STOPPED FAIL-CLOSED BEFORE D21

Evaluation:
RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE

Next:
RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-HANDOFF-001

Existing Human Authority:
RLY-S21-SIDECAR-AUTH-004 — REMAINS VALID

Implementation rework:
NOT AUTHORIZED / NOT JUSTIFIED
```

No new prompt, inference, candidate change, Human technical acceptance, promotion, Slice closure, Slice 2.2, Phase 3, or real-project execution is authorized by this evaluation.
