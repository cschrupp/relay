# Relay — Slice 2.1 Run 010r1 Provider Preflight Diagnostic Handoff

**Document class:** Immutable evidence-diagnostic handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-HANDOFF-001`

## 1. Purpose

Determine why Run 010r1 could prove the exact model entry active but could not prove the provider-side preflight fields required by the handoff.

This is read-only evidence analysis.

## 2. Authority

Operate under the existing exact Run-010 Human Authority context:

```text
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Parent evaluation:
RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE
```

No scope expansion is granted.

## 3. Explicit restrictions

For this diagnostic pass:

```text
new V2 server start:
FORBIDDEN

new HTTP request to OpenCode:
FORBIDDEN

new prompt:
FORBIDDEN

new provider/model inference:
FORBIDDEN

new Relay/OpenCode session:
FORBIDDEN

configuration change:
FORBIDDEN

candidate/source change:
FORBIDDEN

credential-value inspection:
FORBIDDEN

protected V1 content inspection:
FORBIDDEN
```

Do not rerun preflight.

Do not restart Run 010.

## 4. Existing evidence only

Inspect only:

```text
/tmp/relay-s21-sidecar/evidence-run-010r1/
/tmp/relay-s21-sidecar/v2-profile-run-010r1/
```

plus the exact installed beta's non-secret embedded/generated provider/model API schemas or code needed to interpret the already-captured response shape.

Use no current-upstream schema as a substitute for the exact beta.

## 5. Exact questions to resolve

Establish the exact beta response contract for:

```text
GET /api/provider
GET /api/provider/{providerID}
GET /api/model
```

when those routes exist.

For provider responses, determine which of these are actually represented:

```text
provider id
provider name
disabled/enabled/active state
provider API type
provider package
connected/credential-discovered state
provider request metadata
location/data wrapper structure
```

Then inspect the retained Run-010r1 provider evidence and determine whether:

A. `openrouter` was present but the sanitizer/capture omitted or mis-nested the fields;

B. `openrouter` was present and exact-beta provider schema does not expose an `active` field, making the canonical gate over-specified;

C. provider identity was absent;

D. the response was retained too incompletely to decide.

## 6. Model evidence correlation

The retained model catalog already established:

```text
provider/model:
openrouter / google/gemini-3.8-flash

model enabled:
true

model status:
active

provider package:
aisdk:@openrouter/ai-sdk-provider
```

Determine exactly which provider-routing facts that model entry proves under the exact beta.

Do not infer credential consumption or successful inference from catalog presence.

## 7. Classification targets

Return exactly one:

```text
GATE_OVERSPECIFIED
EVIDENCE_CAPTURE_INCOMPLETE
PROVIDER_ABSENT
PROVIDER_PRESENT_NOT_READY
UNKNOWN
```

Use `GATE_OVERSPECIFIED` only if the exact beta does not expose a field the handoff required.

Use `EVIDENCE_CAPTURE_INCOMPLETE` only if the exact beta exposes the needed field but Run-010r1 retained/sanitized evidence failed to capture it.

Do not guess.

## 8. Corrected provider-readiness predicate

If evidence permits, define the strongest non-inference exact-beta provider predicate using only fields the beta genuinely exposes.

Examples of acceptable structure, only when exact-beta evidence supports them:

```text
provider id == openrouter
provider disabled != true
provider api.type == aisdk
provider api.package == @openrouter/ai-sdk-provider
connected contains openrouter
```

or another exact-beta-equivalent predicate.

Do not invent an `active` field if the beta does not expose one.

Do not weaken exact provider/model identity.

## 9. Governance recommendation

Recommend one:

```text
CORRECT_RUN_010_PROVIDER_PREFLIGHT
FURTHER_ENVIRONMENT_CORRECTION
RUNTIME_ESCALATION
UNKNOWN
```

If the issue is only gate shape/capture and no prompt/inference has occurred, state whether the existing `RLY-S21-SIDECAR-AUTH-004` remains sufficient for a fresh corrected preflight attempt.

## 10. Evidence output

Write:

```text
/tmp/relay-s21-sidecar/evidence-run-010r1/provider-preflight-diagnostic-addendum.md
```

Preserve the original Run-010r1 `SHA256SUMS.txt`.

Create a separate:

```text
provider-preflight-diagnostic-SHA256SUMS.txt
```

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

diagnostic handoff:
RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-HANDOFF-001

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

new V2 starts:
NONE

new OpenCode HTTP requests:
NONE

new prompts:
NONE

new inference calls:
NONE

configuration changes:
NONE

classification:
<exact target>

exact beta provider-list schema:
<concise safe summary>

exact beta provider-detail schema:
<concise safe summary or NOT_AVAILABLE>

retained Run-010r1 provider evidence:
<concise result>

model evidence correlation:
<concise result>

corrected provider-readiness predicate:
<exact predicate or unavailable>

candidate defect:
NO/YES/UNKNOWN

environment defect:
NO/YES/UNKNOWN

existing Human Authority remains sufficient:
YES/NO/UNKNOWN

recommended governance route:
<exact route>

diagnostic addendum:
<path>

diagnostic checksum:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
