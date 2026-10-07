# Relay — Slice 2.1 Provider Environment Sidecar Run 006 Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-PROVIDER-HANDOFF-005`

## Authority and exact subject

```text
Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

V2 provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Run-005 evaluation:
RLY-S21-SIDECAR-EVAL-005 — ESCALATE

Frozen candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Requested provider/model:
openrouter / google/gemini-3.8-flash
```

No source change and no new Human Authority are introduced.

## 1. Human launch prerequisite

Run 006 may begin only from a Codex process launched from a shell where the Human has already set `OPENROUTER_API_KEY`.

The launch must preserve parent environment variables into Codex command execution without persisting the key value in configuration.

A suitable current Codex CLI launch pattern is:

```bash
codex \
  -c 'shell_environment_policy.inherit="all"' \
  -c 'shell_environment_policy.ignore_default_excludes=true'
```

The key value itself MUST NOT appear in `-c`, config files, prompt text, logs, or evidence.

## 2. First action: actual execution-shell credential gate

Before any V2 path lookup, `--version`, server startup, package command, or candidate process:

```bash
test -n "$OPENROUTER_API_KEY"
```

Record only PASS/FAIL.

Do not echo, print, hash, measure, substring, or otherwise inspect the value.

Required:

```text
OPENROUTER_API_KEY present in Codex execution shell:
PASS
```

If absent: STOP immediately. No V2 invocation is permitted.

## 3. Governance provenance

Use a current governance checkout containing this handoff and a separate exact detached candidate checkout:

```text
candidate:
ded3ed03b7070ea095a823129ebe44935cb57997
```

Verify the canonical handoff before execution.

## 4. Fresh run-006 isolation roots

Use fresh disposable roots such as:

```text
ROOT=/tmp/relay-s21-sidecar
PROFILE=$ROOT/v2-profile-run-006
EVIDENCE=$ROOT/evidence-run-006
FIXTURE=$ROOT/fixture-run-006
OUTSIDE=$ROOT/outside-canary-run-006
REMOTE=$ROOT/forbidden-remote-run-006.git
WRAPPER=$ROOT/run-v2-isolated-run-006
```

Capture protected V1 metadata before creating/using the wrapper.

## 5. Mandatory V2 isolation wrapper

Create a non-secret executable wrapper before any V2 invocation.

The wrapper must establish:

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

It must then `exec` the exact validated V2 binary with the supplied arguments.

The wrapper must not contain provider credentials or server-auth passwords.

Every V2 operation, including `--version`, `--help`, server startup, and any utility invocation, MUST use this wrapper.

Direct invocation of the V2 binary is forbidden.

If an operation cannot be performed through the wrapper, STOP.

## 6. Provider environment inheritance

The wrapper must preserve the already-inherited `OPENROUTER_API_KEY` environment variable into the isolated V2 process without copying its value into files.

Do not construct a provider credential file.

Do not use `/connect`.

Do not add the key to OpenCode config.

OpenCode must discover the provider through the inherited environment connection only.

## 7. Re-establish run-004 compatibility gates

Through the wrapper only:

```text
V1 metadata unchanged:
PASS

V2 version:
0.0.0-beta-17823

V2 binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

authenticated /api/health:
PASS

candidate describe():
PASS

connection-auth leak check:
PASS
```

If any regresses, STOP.

## 8. Provider/model gate

Using the authenticated V2 API, verify OpenRouter is exposed from the inherited environment credential.

Requested provider/model is fixed:

```text
provider:
openrouter

model:
google/gemini-3.8-flash
```

Do not select an alternate model.

Verify only availability; do not expose credential material.

If the exact model is unavailable through the authenticated OpenRouter connection, STOP.

## 9. Credential leak gate

Before the first provider/model call, prove programmatically without printing secrets:

```text
OPENROUTER_API_KEY value absent from evidence:
PASS

provider Authorization headers absent from evidence:
PASS

server connection password absent from evidence:
PASS

RuntimeExecutionRequest contains no secret:
PASS

CredentialRef contains identifier only:
PASS
```

## 10. D21 execution

Only after all preceding gates pass, execute the full remaining D21 protocol using fresh run-006 identities.

Re-confirm D21-01, D21-02, and D21-17 and execute:

```text
D21-03 exact workspace binding
D21-04 session creation
D21-05 bounded edit
D21-06 normalized events
D21-07 external canary denial
D21-08 disposable push denial
D21-09 allowed read/edit
D21-10 inspect + independent diff
D21-11 requested/actual provider/model provenance
D21-12 controlled cancellation
D21-13 post-interruption inspection
D21-15 event-stream interruption and continuity
D21-16 controlled safe failure normalization
D21-18 distinct mock evaluator session
```

D21-14 remains NOT APPLICABLE unless RESUME is advertised by the fresh descriptor.

Use the minimum calls/tokens necessary.

No real-project work.

## 11. Evidence package

Write sanitized evidence only beneath:

```text
/tmp/relay-s21-sidecar/evidence-run-006/
```

Required fields include:

```text
Codex execution-shell OPENROUTER_API_KEY presence:
PASS/FAIL

credential material:
NOT RECORDED

all V2 invocations through isolation wrapper:
PASS/FAIL

V1 protected metadata:
UNCHANGED/CHANGED/NOT_ATTESTABLE

requested provider/model:
openrouter / google/gemini-3.8-flash

actual provider/model:
<reported or unavailable>

D21-01 through D21-18:
<status + concise evidence>
```

Do not retain raw secrets, Authorization headers, server passwords, OAuth material, or provider credential-bearing logs.

## 12. Required final report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-001
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001

handoff:
RLY-S21-SIDECAR-PROVIDER-HANDOFF-005

candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

governance head:
<exact>

operator:
Codex

Codex execution-shell OPENROUTER_API_KEY presence:
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
PASS/FAIL/NOT_RUN/NOT_APPLICABLE

fixture final diff:
<summary>

credential leak check:
PASS/FAIL

candidate/source changes:
NONE

real-project calls:
NONE

evidence package:
<path>

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

No ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.

## Stop conditions

STOP before any V2 invocation if the provider key is absent from the actual Codex execution shell.

STOP immediately if:

- any V2 process is invoked directly rather than through the wrapper;
- protected V1 metadata changes;
- authenticated V2 compatibility regresses;
- the exact OpenRouter model is unavailable;
- credential material appears in retained evidence;
- interactive login/OAuth/new credential creation/import would be required;
- any D21 permission/session/cancel/inspect/event invariant fails;
- candidate source changes appear necessary.

A stop remains valid evidence.

**Do not make the experiment pass by weakening environment or isolation controls.**
