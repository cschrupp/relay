# Relay — Slice 2.1 Run 009 Failure Diagnostic Handoff

**Document class:** Immutable evidence-diagnostic handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-DIAG-HANDOFF-001`

## Authority and purpose

This handoff operates under the existing exact-SHA sidecar authority:

```text
RLY-S21-SIDECAR-AUTH-003 — AUTHORIZED
candidate: f9a4790c6343561b462d521008c197d776e9ebcf
```

and follows:

```text
RLY-S21-SIDECAR-EVAL-009 — ESCALATE
```

Purpose:

> Determine the cause of Run 009's terminal OpenCode `FAILED` state using existing isolated Run-009 evidence and runtime-local diagnostics, without performing another provider/model inference.

This is evidence analysis only.

## Explicit restrictions

For this diagnostic pass:

```text
new provider/model inference calls: FORBIDDEN
new prompt admission: FORBIDDEN
new Relay execution/session creation: FORBIDDEN
candidate source changes: FORBIDDEN
real-project work: FORBIDDEN
protected V1 content inspection: FORBIDDEN
credential-value inspection: FORBIDDEN
```

Do not restart D21.

Do not retry the task.

Do not create a new candidate.

## 1. Start from existing Run 009 artifacts

Inspect only:

```text
/tmp/relay-s21-sidecar/evidence-run-009/
/tmp/relay-s21-sidecar/v2-profile-run-009/
```

and the existing sanitized/isolated Run-009 runtime log/database metadata needed to classify the failure.

Do not inspect protected V1 contents.

Do not copy `.env`.

## 2. Identify the exact terminal failure source

Locate the event/log/session record corresponding to:

```text
ExecutionId:
exec_01a11896-7fc6-7169-9dca-5c510a89d384

OpenCode session:
ses_ee7698030ffeUPBN4i6sdgwJgO
```

Extract only sanitized structured failure facts.

Preferred fields when available:

```text
runtime event type
error class/name/tag
safe error code
safe bounded message
providerID
modelID
HTTP status if any
retryability/retry event if any
OpenCode failure phase
suggestions/model candidates if explicitly supplied
```

Do not retain:

```text
API key
Authorization headers
server password
cookies
raw prompt body beyond already-public fixture task
full stack traces unless required and sanitized
environment dumps
protected V1 paths/content
```

## 3. Diagnostic sources in priority order

Use the least invasive source that resolves the cause:

1. existing sanitized Run-009 event/raw-event capture;
2. existing isolated V2 stdout/stderr/logs;
3. isolated V2 session/database record for this disposable session, restricted to non-secret error/status/provider/model metadata;
4. exact installed beta's non-secret embedded/generated error schema, only to interpret an observed error tag/code.

Do not use current upstream behavior to replace missing exact-beta evidence.

## 4. Classification targets

Classify only if evidence supports one of:

```text
PROVIDER_MODEL_NOT_FOUND
PROVIDER_NOT_CONFIGURED
AUTHENTICATION
PROVIDER_HTTP_REJECTION
RATE_LIMIT_OR_QUOTA
RUNTIME_CONFIGURATION
AGENT_CONFIGURATION
PERMISSION_BLOCK
RUNTIME_INTERNAL
TRANSPORT
UNKNOWN
```

Do not guess.

## 5. Model-catalog hypothesis

Because earlier live evidence found the exact model at OpenRouter while the OpenCode beta's own model listing did not expose the pair, specifically check for a safe exact-beta error equivalent to:

```text
ProviderModelNotFoundError
model not found
unknown model
provider/model unavailable
```

This is a hypothesis only.

Do not alter OpenCode configuration to make the model appear during this diagnostic pass.

## 6. Credential/authentication distinction

If the failure is authentication-related, determine only whether the isolated runtime reported an auth failure.

Do not inspect the key value.

Do not attempt a new authenticated inference.

Presence of `OPENROUTER_API_KEY` alone does not prove that the beta consumed it successfully.

## 7. Candidate-defect threshold

Do not classify a Relay candidate defect merely because OpenCode execution failed.

A candidate defect requires evidence that the adapter:

- constructed a request contrary to the exact beta contract;
- mis-bound workspace/session/provider/model identity;
- caused the failure through an adapter-controlled field;
- mis-normalized a runtime/provider failure in a way that violates the accepted contract; or
- lost required safe diagnostic information contrary to the accepted design.

Otherwise classify the issue as runtime/provider/environmental.

## 8. Required output

Write a sanitized diagnostic addendum beneath:

```text
/tmp/relay-s21-sidecar/evidence-run-009/diagnostic-addendum.md
```

and update the Run-009 evidence checksum manifest only if doing so does not overwrite the original immutable evidence package semantics. Prefer a separate:

```text
diagnostic-SHA256SUMS.txt
```

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-003 — AUTHORIZED

diagnostic handoff:
RLY-S21-SIDECAR-DIAG-HANDOFF-001

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

new provider/model calls:
NONE

new prompts:
NONE

failure classification:
<one exact target>

observed error tag/class:
<safe value or unavailable>

safe error code/status:
<safe value or unavailable>

safe bounded diagnostic:
<sanitized concise message or unavailable>

provider/model implicated:
<exact or unavailable>

candidate defect established:
YES/NO/UNKNOWN

runtime/provider/environment defect established:
YES/NO/UNKNOWN

recommended governance route:
REWORK / ESCALATE / ENVIRONMENT_CORRECTION / UNKNOWN

evidence source:
<exact Run-009 local artifacts used>

diagnostic addendum:
<path>

diagnostic checksum:
<exact>
```

Codex remains evidence operator only.

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2, or Phase 3 authority.
