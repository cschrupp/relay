# Relay — Slice 2.1 Run 010 Health Failure Diagnostic Handoff

**Document class:** Immutable evidence-diagnostic handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-HEALTH-DIAG-HANDOFF-001`

## Authority and purpose

This diagnostic follows:

```text
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED
RLY-S21-SIDECAR-EVAL-010 — ESCALATE

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf
```

Purpose:

> Determine why the fresh Run-010 exact-beta server returned authenticated HTTP 503 / healthy=false before candidate describe or route preflight.

This is diagnostic analysis of existing disposable evidence only.

## Explicit restrictions

For this diagnostic pass:

```text
new V2 server startup:
FORBIDDEN

new prompt:
FORBIDDEN

new provider/model inference:
FORBIDDEN

new Relay/OpenCode execution session:
FORBIDDEN

configuration changes:
FORBIDDEN

candidate/source changes:
FORBIDDEN

protected V1 content inspection:
FORBIDDEN

credential-value inspection:
FORBIDDEN
```

Do not retry health.

Do not rerun catalog preflight.

Do not restart Run 010.

## 1. Existing evidence only

Inspect only existing Run-010 disposable material:

```text
/tmp/relay-s21-sidecar/evidence-run-010/
/tmp/relay-s21-sidecar/v2-profile-run-010/
```

and, if present, the fresh Run-010 wrapper/server stdout/stderr or isolated OpenCode logs created by that run.

Do not inspect protected V1 contents.

Do not copy or read `.env` contents.

## 2. Identify the HTTP 503 source

Locate the exact error associated with the authenticated `/api/health` request or with server initialization immediately preceding it.

Extract only sanitized structured facts where available:

```text
error class/name/tag
safe status/code
safe bounded message
failure phase
configuration path (disposable only)
database/profile path (disposable only)
provider/catalog initialization marker
retry/readiness marker
causal error chain names
```

Do not retain secrets, raw environment dumps, Authorization headers, server passwords, or unsanitized full stack traces.

## 3. Compare to the successful environment-correction recipe

Compare Run 010 against the successful environment-correction evidence only for non-secret structural facts:

```text
profile directory creation/order
config location
sanitized config structure
provider/model declaration
server invocation shape
environment variable names present/not-present (never values)
database parent creation
startup/readiness sequence
catalog initialization ordering
```

Do not copy old runtime state into Run 010.

The comparison should identify any material difference that could explain why the correction run reached healthy state while Run 010 returned 503.

## 4. Exact-beta interpretation

Use the exact installed beta's non-secret embedded/generated schema or code only to interpret an observed Run-010 error or readiness condition.

Do not substitute current upstream behavior for missing exact-beta evidence.

No execution of the V2 binary is authorized in this diagnostic pass.

## 5. Classification targets

Classify only when supported by evidence as one of:

```text
CONFIGURATION_INVALID
PROFILE_OR_DATABASE_INITIALIZATION
PROVIDER_CATALOG_INITIALIZATION
SERVICE_INITIALIZATION
TRANSIENT_READINESS_RACE
AUTHENTICATION_LAYER
RUNTIME_INTERNAL
OTHER_ENVIRONMENT_FAILURE
UNKNOWN
```

Do not guess.

## 6. Candidate-defect threshold

A Relay candidate defect cannot be established from Run 010 unless evidence shows candidate code was actually executed and caused the health failure.

Because candidate `describe()` was NOT_RUN, the default classification is NOT a candidate defect.

## 7. Required output

Write a sanitized addendum beneath:

```text
/tmp/relay-s21-sidecar/evidence-run-010/health-diagnostic-addendum.md
```

Preserve the original Run-010 `SHA256SUMS.txt` unchanged.

Create a separate:

```text
health-diagnostic-SHA256SUMS.txt
```

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

diagnostic handoff:
RLY-S21-SIDECAR-HEALTH-DIAG-HANDOFF-001

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

new V2 server starts:
NONE

new prompts:
NONE

new inference calls:
NONE

configuration changes:
NONE

failure classification:
<exact target>

observed error class/tag:
<safe value or unavailable>

safe status/code:
<safe value or unavailable>

safe bounded diagnostic:
<sanitized concise value or unavailable>

material difference from successful env correction:
<exact non-secret difference or NONE/UNKNOWN>

candidate defect established:
NO/YES/UNKNOWN

environment/runtime defect established:
NO/YES/UNKNOWN

recommended governance route:
CORRECT_RUN_010_PREFLIGHT / FURTHER_ENVIRONMENT_CORRECTION / RUNTIME_ESCALATION / UNKNOWN

evidence source:
<exact local files used>

diagnostic addendum:
<path>

diagnostic checksum:
<exact>
```

Codex remains evidence operator only.

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
