# Relay — Slice 2.1 Live OpenCode Sidecar Run 010 Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-AUTH-004`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority authorizes a bounded live OpenCode Slice 2.1 Run 010 against exact candidate:

```text
f9a4790c6343561b462d521008c197d776e9ebcf
```

using exact runtime:

```text
OpenCode:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

and exact provider/model:

```text
openrouter / google/gemini-3.8-flash
```

under the same disposable-fixture, credential-containment, no-real-project-work, and D21 safety constraints as `RLY-S21-SIDECAR-AUTH-003`.

## Authority basis

```text
Candidate implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT

Run-009 live evaluation:
RLY-S21-SIDECAR-EVAL-009 — ESCALATE

Run-009 diagnostic evaluation:
RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED

Environment correction authority:
RLY-S21-SIDECAR-ENV-AUTH-001 — AUTHORIZED

Environment correction evaluation:
RLY-S21-SIDECAR-ENV-EVAL-001 — READY_FOR_RUN_010_AUTHORIZATION

Canonical authorization basis:
6b0a1873cf02b9471a7b62591f1c5e11fcae97bf
```

## Mandatory environment precondition

Run 010 MUST use a completely fresh disposable V2 profile.

It MUST recreate, from exact-beta schema/evidence, the minimum non-secret provider/model configuration proven by `RLY-S21-SIDECAR-ENV-EVAL-001` to expose:

```text
provider:
openrouter

model:
google/gemini-3.8-flash
```

in the exact beta's active catalogs.

It MUST NOT reuse the prior environment-correction directory as runtime state.

The prior correction may be consulted only as evidence of the required non-secret recipe.

Before any D21 prompt, Run 010 must prove in the fresh profile:

```text
provider catalog:
openrouter present and active

model catalog:
google/gemini-3.8-flash present, enabled, and active

provider package:
aisdk:@openrouter/ai-sdk-provider
```

The final readiness check must respect the exact-beta initialization ordering discovered during environment correction: perform the model-catalog readiness query before relying on the provider-catalog result.

If the exact route is not active in the fresh profile, STOP before any prompt.

## Credential boundary

The existing ignored/untracked repository-root `.env` may provide `OPENROUTER_API_KEY` only through process environment delivery.

The credential value MUST NOT be printed, inspected, hashed, copied into OpenCode configuration, intentionally persisted in the disposable database, retained in evidence, staged, or committed.

No interactive login, OAuth, credential import, or new credential is authorized.

## D21 authority

After all fresh-environment readiness gates pass, Run 010 may execute the full candidate-specific D21 protocol.

Only the minimum provider/model calls needed for D21 are authorized.

No alternate provider/model, alias, or fallback is authorized.

The canonical fixture task remains a tiny disposable benign edit.

Because the candidate's exact-beta prompt success does not expose a runtime-native invocation identity, `runtime_invocation=None` remains valid and MUST NOT be fabricated from inbox/message IDs.

## Exact stop conditions

STOP if:

- candidate SHA differs;
- exact beta identity differs;
- fresh profile cannot reproduce active exact-route catalog readiness;
- protected V1 state changes;
- credential containment cannot be maintained;
- prompt admission regresses;
- execution wake regresses;
- exact route again reports unavailable;
- provider/model identity differs;
- outside-directory denial cannot be demonstrated;
- push denial cannot be demonstrated;
- exact cancellation/inspection binding cannot be demonstrated;
- event behavior contradicts accepted semantics;
- credentials appear in retained evidence;
- candidate source modification appears necessary;
- broader real-project authority would be required.

Do not patch configuration after the first D21 prompt. Any correction after live execution begins requires a later governance decision.

## Explicit non-authority

This record does NOT authorize:

- Relay candidate/source changes;
- protected V1 modification or content inspection;
- alternate provider/model;
- real-project engineering;
- Human technical acceptance;
- promotion/merge;
- Slice 2.1 closure;
- Slice 2.2;
- Phase 3;
- autonomous evaluator authority.

Successful Run 010 evidence makes the candidate eligible only for independent sidecar-evidence evaluation.
