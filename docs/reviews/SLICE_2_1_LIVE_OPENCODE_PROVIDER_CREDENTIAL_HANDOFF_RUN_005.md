# Relay — Slice 2.1 Provider-Credential Sidecar Run 005 Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-06  
**Record:** `RLY-S21-SIDECAR-PROVIDER-HANDOFF-004`

## Authority and execution precondition

```text
Sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

V2 provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

Run-004 evaluation:
RLY-S21-SIDECAR-EVAL-004 — ESCALATE

Frozen implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Deterministic implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT
```

Run 005 is executable only if an **already-existing provider credential** is available through an authorized external/environment mechanism before Codex begins provider/model execution.

If no such credential is present, STOP at the prerequisite. Do not create or import one.

## 1. Governance provenance

Use:

```text
governance checkout:
current canonical main containing this handoff

candidate checkout:
exact detached ded3ed03b7070ea095a823129ebe44935cb57997
```

Verify this exact handoff exists in the governance checkout before execution.

Do not expect the historical candidate checkout to contain later governance records.

## 2. Preserve the proven run-004 runtime boundary

Reuse the validated V2 binary only if its exact version/hash remain:

```text
OpenCode V2:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

Otherwise reprovision under the fully isolated run-003 procedure.

Use a fresh run-005 HOME/XDG/OPENCODE_DB/TMPDIR profile.

Preserve the protected-V1 metadata checks and transient server-auth procedure that passed run 004.

Before D21 continuation, re-establish:

```text
V1 isolation:
PASS

authenticated /api/health:
PASS

candidate describe():
PASS

connection-auth leak check:
PASS
```

## 3. Provider credential preflight

Do not read or print credential values.

Determine only whether a provider credential source is already present through an approved external/environment mechanism.

OpenCode V2 supports provider-standard environment variables as provider connections. Therefore an environment variable may be used if it is already available to the operator/runtime environment before the run.

Permitted evidence:

```text
credential source class:
environment / external mechanism

credential variable/provider identifier:
name only if non-sensitive

credential value:
NOT READ / NOT RECORDED
```

Do not enumerate the whole environment into evidence.

Do not run commands that print secret-bearing variables.

Do not inspect protected V1 auth/config/database contents.

## 4. Forbidden credential acquisition

STOP if provider access would require any of:

```text
interactive OpenCode /connect
OAuth browser/code flow
new API-key creation
new provider account
copying a protected auth file
copying/importing the V1 OpenCode database
extracting a token/key/cookie from protected state
writing provider credentials into fixture/repository/evidence
```

These actions are not authorized by this handoff.

## 5. Provider/model availability check

After the isolated V2 server starts with the already-existing external credential available, use the authenticated V2 API to inspect only sanitized provider/model availability.

Select exactly one provider/model that:

- is available with the existing credential;
- is capable of the tiny fixture edit;
- requires no new login/configuration;
- does not require general provider experimentation.

Record only provider/model identifiers and availability state.

Once selected, freeze the requested provider/model into the digest-bound RuntimeExecutionRequest and do not switch during that execution.

If no usable provider/model appears, STOP.

## 6. Credential leak gate

Before the first provider/model call prove programmatically, without printing the literal credential:

```text
provider credential absent from repository
provider credential absent from fixture
provider credential absent from evidence
provider credential absent from RuntimeExecutionRequest
CredentialRef contains identifier only, no secret
provider credential absent from normalized errors/events
server connection password likewise absent
```

Record only PASS/FAIL.

## 7. D21 continuation

Run 005 starts from the already-proven compatibility boundary but must use fresh run-005 execution/session identities.

Attempt all still-unproven D21 items:

```text
D21-03 exact fixture/workspace binding
D21-04 programmatic session creation
D21-05 benign bounded edit
D21-06 normalized events
D21-07 external-directory denial
D21-08 disposable local push denial
D21-09 allowed read/edit
D21-10 inspect plus independent diff
D21-11 requested/actual provider-model provenance
D21-12 controlled cancellation
D21-13 post-interruption inspection
D21-15 stream interruption / continuity
D21-16 safe controlled failure
D21-18 distinct mock evaluator session
```

D21-14 remains NOT APPLICABLE unless the runtime descriptor changes and advertises RESUME.

Re-confirm D21-01, D21-02, and D21-17 in the run-005 evidence package.

All original sidecar stop conditions remain binding.

## 8. Provider/model call minimization

Use the minimum calls/tokens needed to satisfy the evidence protocol.

The tiny fixture task remains bounded.

Do not perform exploratory prompts, benchmarking, or unrelated model comparisons.

No real-project work.

## 9. Evidence package

Write only to:

```text
/tmp/relay-s21-sidecar/evidence-run-005/
```

Include:

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

Evidence may state:

```text
provider credential source class:
environment / external mechanism

provider credential:
NOT RECORDED
```

Never retain raw credentials, provider Authorization headers, server passwords, cookies, or OAuth material.

## 10. Required final operator report

Return:

```text
authority:
RLY-S21-SIDECAR-AUTH-001
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001

handoff:
RLY-S21-SIDECAR-PROVIDER-HANDOFF-004

candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

governance head:
<exact>

operator:
Codex

V1 isolation:
PASS/FAIL/NOT_ATTESTABLE

V2 version/hash:
<exact>

authenticated health:
PASS/FAIL

candidate describe:
PASS/FAIL

provider credential source:
environment / external mechanism / unavailable

provider credential material:
NOT RECORDED

requested provider/model:
<exact or unavailable>

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
<path>

SHA256SUMS.txt SHA-256:
<exact>

deviations/findings:
<exact>
```

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, or Slice closure.

## Stop conditions

STOP without source mutation if:

- no already-existing external/environment provider credential is available;
- credential value would need to be read/copied/imported;
- interactive login/OAuth/new credential creation would be needed;
- provider/model cannot be selected without experimentation;
- protected V1 state changes;
- authenticated health or candidate describe regresses;
- a provider/model secret leaks;
- any D21 permission/session/cancel/inspect/event invariant fails;
- candidate SHA differs;
- Relay source/dependency/schema/governance/lifecycle/persistence change is required.

A stop remains valid evidence.

**Existing external credential availability is a prerequisite, not something Codex may manufacture.**
