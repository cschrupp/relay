# Relay — Slice 2.1 OpenCode V2 Environment Correction Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-ENV-HANDOFF-001`

## 1. Authority

```text
Environment correction authority:
RLY-S21-SIDECAR-ENV-AUTH-001 — AUTHORIZED

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT

Diagnostic evaluation:
RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED

Exact beta:
0.0.0-beta-17823

Exact binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

Exact target route:
openrouter / google/gemini-3.8-flash
```

Codex is environment/evidence operator only.

No implementation, evaluation, acceptance, or promotion authority is granted.

## 2. Fresh disposable correction root

Use a fresh root such as:

```text
/tmp/relay-s21-sidecar/env-correction-001/
```

Create fresh isolated:

```text
profile/home
profile/config
profile/data
profile/data/opencode
profile/state
profile/cache
profile/tmp
evidence
wrapper
```

Set:

```text
HOME=<fresh>/profile/home
XDG_CONFIG_HOME=<fresh>/profile/config
XDG_DATA_HOME=<fresh>/profile/data
XDG_STATE_HOME=<fresh>/profile/state
XDG_CACHE_HOME=<fresh>/profile/cache
TMPDIR=<fresh>/profile/tmp
OPENCODE_DB=<fresh>/profile/data/opencode/opencode-next.db
OPENCODE_DISABLE_AUTOUPDATE=1
```

Verify all required directories and the database parent exist and are writable.

Capture protected V1 metadata before any V2 process and compare again at completion.

## 3. Credential gate

From the governance repository root, verify without reading content:

```text
.env exists: PASS
.env ignored: PASS
.env untracked: PASS
OPENROUTER_API_KEY nonempty after non-echoing source: PASS
```

Do not output, inspect, hash, copy, or persist the credential value.

The isolation wrapper may source the exact `.env` path and export the variable into the V2 process environment.

The disposable OpenCode configuration MUST NOT contain the key value.

## 4. Exact-beta contract inspection

Before writing configuration, inspect the exact installed beta's non-secret embedded/generated schemas to determine:

- accepted config file location(s);
- provider registration/configuration shape;
- OpenRouter provider identifier expected by the beta;
- environment-variable credential discovery;
- model registration/catalog override shape if any;
- provider/model route-resolution rules;
- local provider/model/catalog endpoint(s);
- any non-executing route validation/resolver surface.

Do not infer configuration from current upstream if it differs from the exact beta.

Record the exact non-secret schema evidence used.

## 5. Minimal disposable correction

Create only the minimum exact-beta-compatible configuration necessary to expose/activate:

```text
provider:
openrouter

model:
google/gemini-3.8-flash
```

Rules:

- exact provider ID must remain `openrouter`;
- exact model ID must remain `google/gemini-3.8-flash`;
- no aliases that change Relay's requested identity;
- no alternate provider/model;
- no persistent secret value;
- no modification outside the fresh V2 profile;
- no candidate/source changes.

If the exact beta can use an environment credential with only a non-secret provider/model declaration, prefer that.

## 6. Wrapper-only runtime checks

Every V2 invocation MUST use the fresh isolation wrapper.

Direct invocation is forbidden.

Verify exact version/hash through the wrapper.

Start the exact beta in explicit isolated loopback/headless mode with transient server authentication.

Required:

```text
protected V1 metadata unchanged: PASS
authenticated /api/health: PASS
exact runtime version: PASS
```

## 7. Non-inference route-readiness proof

Do NOT create a prompt.

Do NOT request model completion/inference.

Use only exact-beta local/provider/model/configuration/catalog surfaces.

Readiness PASS requires:

```text
OpenCode provider catalog exposes provider "openrouter"
AND
OpenCode model catalog exposes exact model "google/gemini-3.8-flash"
AND
the exact pair is represented as one resolvable route by any available non-executing local resolver/validation surface
```

If no explicit local resolver exists, report:

```text
route catalog readiness:
PASS/FAIL

non-inference execution-route proof:
NOT_AVAILABLE
```

Do not substitute an actual prompt to prove it.

Session creation by itself does not satisfy readiness.

A non-inference provider catalog refresh intrinsic to exact-beta startup/catalog discovery is permitted. Do not issue a direct manual OpenRouter inference request.

## 8. Failure classification

If readiness still fails, determine only from sanitized exact-beta evidence whether the reason is:

```text
PROVIDER_NOT_REGISTERED
MODEL_NOT_REGISTERED
PROVIDER_CREDENTIAL_NOT_DISCOVERED
CONFIGURATION_INVALID
ROUTE_RESOLUTION_UNAVAILABLE
OTHER_EXACT_BETA_ENVIRONMENT_FAILURE
UNKNOWN
```

Do not guess.

## 9. Evidence package

Write only sanitized evidence beneath:

```text
/tmp/relay-s21-sidecar/env-correction-001/evidence/
```

At minimum retain:

```text
report.md
manifest.json
commands.txt
config-schema-evidence.txt
sanitized-config.txt
health.txt
provider-catalog.txt
model-catalog.txt
route-readiness.txt
protected-v1-metadata-before.txt
protected-v1-metadata-final.txt
SHA256SUMS.txt
```

The sanitized configuration must redact/remove any unexpected secret-bearing value before retention.

Do not retain raw environment dumps.

## 10. Required operator report

Return:

```text
authority:
RLY-S21-SIDECAR-ENV-AUTH-001 — AUTHORIZED

handoff:
RLY-S21-SIDECAR-ENV-HANDOFF-001

governance head:
<exact>

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

new prompts:
NONE

new inference calls:
NONE

candidate/source changes:
NONE

protected V1:
UNCHANGED/CHANGED/NOT_ATTESTABLE

exact beta version/hash:
<exact>

.env exists / ignored / untracked:
PASS/PASS/PASS

OPENROUTER_API_KEY presence:
PASS/FAIL

credential material:
NOT RECORDED

exact beta config schema evidence:
<concise>

minimum disposable correction:
<non-secret concise summary>

provider catalog:
<result>

model catalog exact pair:
<result>

non-inference route resolver:
PASS/FAIL/NOT_AVAILABLE

route readiness:
PASS/FAIL/PARTIAL

failure classification if not PASS:
<exact target or N/A>

configuration persisted outside disposable profile:
NO

candidate defect:
NO

recommended next governance route:
AUTHORIZE_RUN_010 / FURTHER_ENVIRONMENT_CORRECTION / ESCALATE

evidence package:
<path>

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, Run 010 authority, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
