# Slice 2.1 — OpenCode V2 Environment Correction Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-ENV-EVAL-001`  
**Outcome:** `READY_FOR_RUN_010_AUTHORIZATION`

## Subject

```text
Environment correction authority:
RLY-S21-SIDECAR-ENV-AUTH-001 — AUTHORIZED

Environment correction handoff:
RLY-S21-SIDECAR-ENV-HANDOFF-001

Governance head:
66f142036c6d7d4da7b9fd24c01ae5fddee6e70f

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Exact beta:
0.0.0-beta-17823

Exact binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

Target:
openrouter / google/gemini-3.8-flash
```

## Operator evidence

The environment-correction operator reported:

```text
exact beta identity: PASS
.env exists / ignored / untracked: PASS / PASS / PASS
OPENROUTER_API_KEY presence: PASS
credential material: NOT RECORDED
protected V1 metadata: UNCHANGED
authenticated /api/health: PASS
new prompts: NONE
new inference calls: NONE
candidate/source changes: NONE
configuration outside disposable profile: NO
```

The exact-beta schema was reported to expose:

- top-level provider configuration;
- provider-scoped model configuration;
- OpenRouter provider ID `openrouter`;
- environment discovery through `OPENROUTER_API_KEY`;
- provider-scoped model registration with a display name.

The minimum disposable non-secret correction registered exact model:

```text
google/gemini-3.8-flash
```

under exact provider:

```text
openrouter
```

without persisting the credential value.

## Readiness result

Final ordered catalog checks established:

```text
provider catalog:
PASS — openrouter present and active

exact model catalog pair:
PASS — openrouter / google/gemini-3.8-flash present, enabled, and active

provider package:
aisdk:@openrouter/ai-sdk-provider

non-inference execution-route resolver:
NOT_AVAILABLE

route catalog readiness:
PASS
```

The exact beta exposes no public non-inference execution-route resolver/validator beyond its catalog/configuration surfaces.

Therefore the correction exhausted the strongest proof available under the explicit no-prompt/no-inference authority.

Session creation is not treated as additional proof.

## Initialization-order finding

The first provider-list query raced catalog initialization and returned empty.

Exact-beta source inspection established that the model-catalog endpoint waits for catalog initialization whereas the provider endpoint does not.

The operator then performed an ordered non-inference check:

```text
model catalog first
provider catalog second
```

and both final catalogs passed.

This is a runtime-readiness ordering detail, not a Relay candidate defect.

## Evaluation

The previous Run-009 failure:

```text
SessionRunnerModel.ModelUnavailableError
provider.no-route
Model unavailable: openrouter/google/gemini-3.8-flash
```

is now addressed at the disposable catalog/configuration layer to the maximum extent provable without inference.

Classification:

```text
Relay candidate defect:
NO

accepted design defect:
NO

environment correction:
SUCCESSFUL

route catalog readiness:
PASS

non-inference execution-route proof:
NOT_AVAILABLE BY EXACT BETA

candidate:
UNCHANGED

candidate deterministic evaluation:
RLY-S21-EVAL-004 — ACCEPT

live inference success:
NOT PROVEN

D21 completion:
NOT PROVEN

Human technical acceptance:
NOT ELIGIBLE
```

## Governance decision

```text
RLY-S21-SIDECAR-ENV-EVAL-001 — READY_FOR_RUN_010_AUTHORIZATION
```

A fresh live sidecar rerun may now be considered by the Human Authority against the same exact candidate and exact corrected disposable environment recipe.

This evaluation does NOT itself authorize Run 010.

A future Run-010 authority must remain:

- exact-SHA bound to `f9a4790c6343561b462d521008c197d776e9ebcf`;
- exact beta bound to `0.0.0-beta-17823`;
- exact provider/model bound to `openrouter / google/gemini-3.8-flash`;
- disposable-profile only;
- credential-contained;
- no real-project work;
- D21 evidence only.

The Run-010 environment must recreate the minimum successful disposable provider/model configuration before D21 execution. It must not rely on state from the prior correction directory as hidden prerequisite.

No Human technical acceptance, promotion, Slice closure, Slice 2.2, Phase 3, or real-project agent execution is authorized.

## Evidence reference

```text
/tmp/relay-s21-sidecar/env-correction-001/evidence/
SHA256SUMS.txt SHA-256:
27784c011ae4c582d303ff65c8c79102e12c43f3aa9b619dc976d798a0b9d8ab
```
