# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 005

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-005`  
**Outcome:** `ESCALATE`

## Subject

```text
Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

V2 provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Prior evaluation:
RLY-S21-SIDECAR-EVAL-004 — ESCALATE

Run-005 handoff:
RLY-S21-SIDECAR-PROVIDER-HANDOFF-004

Governance head:
9701f510b7bb41a06db3d612603c02b2cc796f29

Implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Requested provider/model:
openrouter / google/gemini-3.8-flash
```

## Operator-reported evidence

```text
Run status:
STOPPED FAIL-CLOSED

OPENROUTER_API_KEY in Codex execution shell:
ABSENT

provider/model availability check:
NOT RUN

provider/model calls:
NONE

authenticated V2 health:
NOT RUN

candidate describe():
NOT RUN

candidate/source changes:
NONE

real-project calls:
NONE
```

The operator also reported one inadvertent direct V2 `--version` invocation outside the required isolated profile. That process attempted to open the protected V1 log and received `EROFS`.

Post-event checks reported:

```text
V1 executable hash:
UNCHANGED

known protected V1 state metadata:
UNCHANGED

protected contents:
NOT INSPECTED
```

The run stopped before server startup, fixture/session creation, or D21 execution.

## Evidence package

Reported package:

```text
/tmp/relay-s21-sidecar/evidence-run-005/
```

Reported SHA-256 of `SHA256SUMS.txt`:

```text
319275449b6f2cf2c668300aad2f8f40c23e5b58ff34f47758f2c7076431fab6
```

The operator reported checksum verification passed and `manifest.json` parsed successfully. This evaluation does not claim independent byte-level access to the local evidence package.

# Findings

## F005-A — Provider credential did not reach the actual Codex command environment

The Human had supplied an existing OpenRouter credential through `OPENROUTER_API_KEY`, but the variable was absent where Codex executed shell commands.

OpenCode V2 supports provider-standard environment variables as automatic provider connections. Therefore this run did not test OpenRouter availability or the requested model.

Current Codex configuration also makes command-environment inheritance explicitly policy controlled through `shell_environment_policy`, including `inherit` and `ignore_default_excludes`.

This is an execution-environment prerequisite defect, not a Relay candidate defect.

## F005-B — First V2 invocation was not enclosed by the run isolation boundary

The direct `opencode2 --version` call violated the run-005 procedural requirement that all V2 invocations occur inside the disposable HOME/XDG profile.

The resulting `EROFS` prevented the attempted protected-log open from succeeding, and protected metadata remained unchanged. Nevertheless the run cannot claim V1 isolation PASS because the process crossed the boundary.

This is an operator-procedure defect.

## Model identifier verification

The requested exact OpenRouter model is valid:

```text
provider:
openrouter

model:
google/gemini-3.8-flash
```

OpenRouter currently lists that exact model ID and exposes active endpoints.

# Classification

```text
Relay candidate deterministic defect:
NOT ESTABLISHED

accepted Slice 2.1 design defect:
NOT ESTABLISHED

run-004 live authenticated V2 compatibility:
REMAINS ESTABLISHED

run-005 provider credential propagation:
FAIL

run-005 V1 isolation procedure:
FAIL

protected V1 persistent-state mutation:
NOT OBSERVED

provider/model execution:
NOT TESTED

D21:
NOT RUN

Human technical acceptance:
NOT ELIGIBLE
```

# Governance decision

```text
Run 005:
STOPPED FAIL-CLOSED

Evaluation:
RLY-S21-SIDECAR-EVAL-005 — ESCALATE

Candidate:
UNCHANGED
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation:
RLY-S21-EVAL-002 — ACCEPT
```

No Relay source/design rework is authorized by this evidence.

# Run 006 correction

No new Human Authority is required.

Run 006 is a narrower retry under the existing sidecar/provider authority, with two mandatory gates before any OpenCode process may run:

1. Codex command-environment credential presence check:
   `test -n "$OPENROUTER_API_KEY"`
   must PASS inside the actual Codex-executed shell, without printing the value.

2. Every V2 process must be invoked through a pre-created non-secret isolation wrapper that establishes the disposable HOME/XDG/OPENCODE_DB/TMPDIR envelope before `exec` of the V2 binary. Direct invocation of the V2 binary is forbidden.

If gate 1 fails, STOP before locating/running the V2 binary.

This evaluation does not authorize interactive provider login, OAuth, new credential creation, protected V1 credential import, Human technical acceptance, promotion, Slice closure, Slice 2.2, or Phase 3.
