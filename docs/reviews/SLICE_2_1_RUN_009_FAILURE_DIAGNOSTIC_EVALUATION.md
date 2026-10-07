# Slice 2.1 — Run 009 Failure Diagnostic Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-DIAG-EVAL-001`  
**Outcome:** `ENVIRONMENT_CORRECTION_REQUIRED`

## Subject

```text
Parent live evaluation:
RLY-S21-SIDECAR-EVAL-009 — ESCALATE

Diagnostic handoff:
RLY-S21-SIDECAR-DIAG-HANDOFF-001

Exact candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Diagnostic addendum checksum:
75829c0eb7fcac0377773f42900deb06ae171835d83225fe92f1418e72821cdf

Original Run-009 evidence checksum:
25f242b9f51af3fe9162bbbe29f476bf39d86fafc214cd9cf6332dc2ca8f0eb3
```

## Established failure

The Run-009 terminal failure is classified:

```text
PROVIDER_MODEL_NOT_FOUND
```

The exact installed beta reported:

```text
error class:
SessionRunnerModel.ModelUnavailableError

safe route code:
provider.no-route

safe bounded diagnostic:
Model unavailable: openrouter/google/gemini-3.8-flash
```

The exact beta's embedded error definition identifies provider/model fields and constructs this model-unavailable failure.

No HTTP status was present on the target failure record.

## Interpretation

The evidence establishes:

```text
candidate prompt schema:
PASS

candidate prompt admission:
PASS

candidate execution wake:
PASS

candidate runtime_invocation handling:
PASS

OpenCode route resolution for requested exact pair:
FAIL

provider usage:
ZERO REPORTED

fixture mutation:
NONE
```

The failure occurred inside the OpenCode runtime's provider/model route-resolution layer after Relay had successfully created/bound the exact session and woken execution.

## Candidate/design disposition

```text
Relay candidate defect:
NO

accepted Slice 2.1 design defect:
NO

runtime/provider/environment issue:
YES

environment correction required:
YES
```

No implementation rework is justified by this evidence.

The current deterministic candidate evaluation remains:

```text
RLY-S21-EVAL-004 — ACCEPT
```

for exact candidate:

```text
f9a4790c6343561b462d521008c197d776e9ebcf
```

## Important limit

The diagnostic establishes that the beta could not resolve:

```text
openrouter / google/gemini-3.8-flash
```

for the target session.

It does NOT establish the root reason for route absence.

Possible causes such as beta catalog omission, provider configuration, model registration, or credential-dependent provider activation remain unproven until a bounded environment-correction preflight inspects the exact beta's configuration/route contract.

Credential presence was already proven, but credential consumption was not.

No authentication error was observed.

## Governance route

```text
Required next route:
ENVIRONMENT_CORRECTION

Candidate source:
UNCHANGED

New candidate:
NOT REQUIRED

Further implementation evaluation:
NOT REQUIRED

Another live inference:
NOT AUTHORIZED BY THIS EVALUATION
```

Because `RLY-S21-SIDECAR-AUTH-003` required Run 009 to stop when the exact model was unavailable and prohibited patching around a live mismatch during the sidecar, the environment correction must be separately and explicitly Human-authorized before OpenCode configuration is changed for another attempt.

A future environment-correction authority should remain bounded to the disposable V2 profile and exact:

```text
provider:
openrouter

model:
google/gemini-3.8-flash

candidate:
f9a4790c6343561b462d521008c197d776e9ebcf
```

It must not modify Relay candidate source, protected V1 state, or real projects.

After environment readiness is proven, a subsequent live D21 rerun requires explicit run authority.

## Human technical acceptance

```text
NOT ELIGIBLE
```

No promotion, Slice closure, Slice 2.2, Phase 3, or real-project agent execution is authorized.
