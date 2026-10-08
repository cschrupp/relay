# Slice 2.1 — Run 010r1 Provider Preflight Diagnostic Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001`  
**Outcome:** `CORRECT_RUN_010_PROVIDER_PREFLIGHT`

## Subject

```text
Parent evaluation:
RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE

Diagnostic handoff:
RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-HANDOFF-001

Human Authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Canonical diagnostic basis:
9c19344e887b347241d548b7d45a7565fa7bef09
```

## Runtime restoration after forced restart

The forced restart removed the disposable V2 runtime and the original Run-010r1 disposable evidence/profile directories.

Under existing provisioning authority, the exact runtime was restored in an isolated disposable envelope:

```text
package:
@opencode-ai/cli@0.0.0-beta-17823

binary:
opencode2

restored realpath:
/tmp/relay-s21-sidecar/v2-recovery-001/runtime/npm/lib/node_modules/@opencode-ai/cli/bin/opencode2.exe

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

protected V1:
UNCHANGED

protected V1 version:
1.18.23

protected V1 SHA-256:
de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2
```

The package postinstall ran inside the already-authorized disposable isolation envelope.

No new server start, OpenCode HTTP request, prompt, inference, D21 execution, or candidate change occurred during the diagnostic.

## Evidence-loss note

The forced restart removed the original Run-010r1 raw disposable evidence/profile.

Its historical immutable governance evaluation remains canonical, but the original `SHA256SUMS.txt` is no longer available locally and was not recreated.

The diagnostic did not treat reconstructed material as the original Run-010r1 evidence.

This is an evidence-retention incident, not a candidate/runtime defect.

## Exact-beta provider/model schema

The restored exact beta establishes:

```text
GET /api/provider:
Provider.Info[]

GET /api/provider/{providerID}:
Provider.Info

GET /api/model:
Model.Info[]

HTTP success wrapper:
{ location: Location.Info, data: ... }
```

Exact `Provider.Info` exposes:

```text
id
name
activation: auto | enabled | disabled
package: string
optional settings
optional headers
optional body/request overlays
```

It does NOT expose:

```text
active: boolean
disabled: boolean
enabled: boolean
nested api.type
nested api.package
direct connected/credential-consumed flag
```

Credential/environment references are represented separately through integration connection information.

Exact `Model.Info` exposes the route-relevant fields:

```text
id
providerID
package (optional)
enabled
status including active
```

## Diagnostic classification

```text
classification:
GATE_OVERSPECIFIED
```

The Run-010/010r1 handoff required provider-side facts that do not exist in the exact beta's provider schema.

Therefore failure to prove:

```text
provider active == true
provider.api.type
provider.api.package
```

cannot constitute provider failure.

The canonical provider gate itself was over-specified.

## Corrected exact-beta provider/model readiness predicate

For a fresh non-inference preflight, require all of:

```text
provider.id == "openrouter"

provider.activation in {"auto", "enabled"}

provider.package == "aisdk:@openrouter/ai-sdk-provider"

model.id == "google/gemini-3.8-flash"

model.providerID == "openrouter"

model.enabled == true

model.status == "active"

model.package == "aisdk:@openrouter/ai-sdk-provider"
```

If the exact beta omits the optional model `package` field in a fresh response, the provider root package remains mandatory and the model must still match exact `providerID`, `enabled=true`, and `status=active`.

Credential presence remains a separate gate:

```text
OPENROUTER_API_KEY present in the isolated process environment:
PASS required
```

Neither catalog readiness nor environment-variable presence proves credential consumption or successful inference. That evidence can arise only during an authorized live provider turn.

## Candidate/environment disposition

```text
Relay candidate defect:
NO

accepted Slice 2.1 design defect:
NO

Run-010r1 environment defect:
NOT ESTABLISHED

provider absence:
NOT ESTABLISHED

provider not-ready:
NOT ESTABLISHED

preflight gate defect:
YES — PROCEDURAL / OVER-SPECIFIED

candidate:
UNCHANGED

candidate deterministic evaluation:
RLY-S21-EVAL-004 — ACCEPT
```

## Authority disposition

Existing Human Authority remains sufficient:

```text
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED
```

No scope expansion is introduced because:

- the exact candidate is unchanged;
- the exact beta is unchanged;
- provider/model identity is unchanged;
- credential boundary is unchanged;
- no previous corrected attempt submitted a prompt or inference;
- the correction only replaces impossible provider fields with the strongest exact-beta fields actually available.

## Governance decision

```text
RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001 — CORRECT_RUN_010_PROVIDER_PREFLIGHT

Corrective handoff:
RLY-S21-SIDECAR-RUN010-PROVIDER-PREFLIGHT-CORRECTION-001

Fresh corrected attempt:
Run 010r2

New Human Authority:
NOT REQUIRED

Human technical acceptance:
NOT ELIGIBLE
```

No implementation rework, promotion, Slice closure, Slice 2.2, Phase 3, or real-project agent execution is authorized.

## Diagnostic evidence

```text
provider-preflight diagnostic addendum:
/tmp/relay-s21-sidecar/evidence-run-010r1/provider-preflight-diagnostic-addendum.md

reported SHA-256:
960b1be71e5f2d47e66ee092768826ab10f0f8df1f5348c85a830829ed2ce580

exact-beta schema excerpt:
/tmp/relay-s21-sidecar/v2-recovery-001/evidence/exact-beta-provider-model-api-schema.txt
```
