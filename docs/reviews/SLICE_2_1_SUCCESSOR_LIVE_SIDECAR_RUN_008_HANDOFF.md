# Relay — Slice 2.1 Successor Live OpenCode Sidecar Run 008 Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-HANDOFF-002`

## 1. Authority

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-002 — AUTHORIZED

V2 provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Implementation evaluation:
RLY-S21-EVAL-003 — ACCEPT

Exact successor candidate:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

Canonical governance basis:
d1d1f05c8e0b40ee12555f5b8d18d0f9ab357398

Requested provider/model:
openrouter / google/gemini-3.8-flash
```

Codex is evidence operator only. It may not ACCEPT/REWORK its own evidence.

## 2. Repository views

Maintain separate views:

```text
governance checkout:
current canonical main containing this authority and handoff

candidate checkout:
exact detached 5df1add9ed829a62a99d7f25f561a0f492ff5c73
```

Do not run the candidate from Relay's canonical worktree.

Verify the candidate checkout is exact and tracked-clean before execution.

## 3. Credential source

Use only the existing Human-provided repository-root ignored/untracked `.env`.

Before any V2 invocation verify without exposing contents:

```text
.env exists: PASS
.env ignored: PASS
.env untracked: PASS
tracked governance checkout clean: PASS
OPENROUTER_API_KEY nonempty after non-echoing source: PASS
```

Never print, inspect, hash, copy, stage, commit, upload, or persist the credential value.

## 4. Fresh Run 008 disposable environment

Use fresh Run 008 roots beneath:

```text
/tmp/relay-s21-sidecar/
```

including candidate, fixture, outside-canary, forbidden local bare remote, evidence, fresh V2 profile, and wrapper.

Before any V2 process explicitly create writable:

```text
$PROFILE/home
$PROFILE/config
$PROFILE/data
$PROFILE/data/opencode
$PROFILE/state
$PROFILE/cache
$PROFILE/tmp
$EVIDENCE
```

Set:

```text
HOME=$PROFILE/home
XDG_CONFIG_HOME=$PROFILE/config
XDG_DATA_HOME=$PROFILE/data
XDG_STATE_HOME=$PROFILE/state
XDG_CACHE_HOME=$PROFILE/cache
TMPDIR=$PROFILE/tmp
OPENCODE_DB=$PROFILE/data/opencode/opencode-next.db
OPENCODE_DISABLE_AUTOUPDATE=1
```

Assert the `OPENCODE_DB` parent exists and is writable.

## 5. V2 wrapper

Every V2 invocation, including `--version`, `--help`, server startup, and utility calls, MUST use one non-secret Run 008 isolation wrapper.

Direct V2 binary invocation is forbidden.

The wrapper may source the exact ignored `.env` path, but may never contain or persist the credential value.

## 6. Runtime identity

Use the same already-provisioned V2 binary only if exact identity remains:

```text
OpenCode V2:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

If identity differs, STOP unless a separately authorized provisioning action establishes the replacement.

## 7. Server startup and authentication

Use the explicit loopback/headless server mode that succeeded in Run 007/Run 004.

Use transient server connection authentication.

Never persist server password or Authorization headers.

Required before D21:

```text
protected V1 metadata unchanged: PASS
authenticated /api/health: PASS
healthy=true
runtime version exact
candidate OpenCodeRuntime.describe(): PASS
connection-auth leak check: PASS
```

## 8. Provider/model gate

Verify exactly:

```text
provider:
openrouter

model:
google/gemini-3.8-flash
```

No alternate model.

If the exact model is unavailable, STOP.

Do not infer actual provider/model identity from requested identity.

## 9. Fresh D21 protocol

Run the complete candidate-specific D21-01 through D21-18 protocol with fresh Run 008 identities.

Required sequence includes:

```text
D21-01 runtime/candidate identity
D21-02 explicit endpoint
D21-03 exact fixture/workspace binding
D21-04 programmatic session creation
D21-05 benign bounded edit
D21-06 normalized events
D21-07 external-directory denial
D21-08 disposable local push denial
D21-09 allowed read/edit
D21-10 result inspection + independent Git diff
D21-11 requested/actual provider-model provenance
D21-12 controlled cancellation
D21-13 post-interruption inspection
D21-14 resume only if freshly advertised
D21-15 deliberate event-stream interruption / continuity behavior
D21-16 controlled safe failure normalization
D21-17 credential-leak proof
D21-18 distinct mock-evaluator session
```

Observer-before-prompt and one-prompt semantics remain mandatory.

Any prompt schema/admission mismatch is a STOP.

## 10. Fixture task

Use a tiny disposable benign edit only.

No real-project code.

The fixture must have a recorded baseline commit. After the run independently compare Git status/diff to the runtime inspection result.

The outside-canary and local bare remote exist only to prove denials.

## 11. Evidence

Write only beneath:

```text
/tmp/relay-s21-sidecar/evidence-run-008/
```

At minimum include:

```text
report.md
manifest.json
commands.txt
SHA256SUMS.txt
normalized-events.jsonl
fixture-before.txt
fixture-after.txt
fixture-diff.patch
protected-v1-metadata-before.txt
protected-v1-metadata-final.txt
```

Sanitize all runtime diagnostics.

Never retain API keys, Authorization headers, server passwords, cookies, OAuth material, or raw protected V1 contents.

## 12. Required operator report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-002 — AUTHORIZED

handoff:
RLY-S21-SIDECAR-HANDOFF-002

governance head:
<exact>

candidate:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

operator:
Codex

.env exists / ignored / untracked:
PASS/PASS/PASS

OPENROUTER_API_KEY presence:
PASS/FAIL

credential material:
NOT RECORDED

V1 isolation:
PASS/FAIL/NOT_ATTESTABLE

all V2 invocations through wrapper:
PASS/FAIL

V2 version/hash:
<exact>

authenticated health:
PASS/FAIL

candidate describe:
PASS/FAIL

requested provider/model:
openrouter / google/gemini-3.8-flash

actual provider/model:
<exact or unavailable>

identity completeness:
FULL/PARTIAL/UNKNOWN

D21-01 through D21-18:
PASS/FAIL/NOT_RUN/NOT_APPLICABLE + concise evidence

fixture final diff:
<summary>

credential leak check:
PASS/FAIL

candidate/source changes:
NONE

real-project calls:
NONE

evidence package:
/tmp/relay-s21-sidecar/evidence-run-008/

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.

**Do not make the experiment pass by weakening credentials, isolation, permissions, identity, or exact-binding controls.**
