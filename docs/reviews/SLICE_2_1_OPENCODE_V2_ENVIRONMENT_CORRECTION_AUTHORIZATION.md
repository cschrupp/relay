# Relay — Slice 2.1 OpenCode V2 Environment Correction Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-ENV-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority authorizes a bounded Slice 2.1 OpenCode V2 environment correction against exact candidate:

```text
f9a4790c6343561b462d521008c197d776e9ebcf
```

The correction is limited to a fresh disposable OpenCode V2 profile and solely to make the exact route:

```text
openrouter / google/gemini-3.8-flash
```

resolvable by exact OpenCode:

```text
0.0.0-beta-17823
binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

## Basis

```text
Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT

Run-009 live evaluation:
RLY-S21-SIDECAR-EVAL-009 — ESCALATE

Run-009 diagnostic evaluation:
RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED

Observed exact-beta failure:
SessionRunnerModel.ModelUnavailableError
provider.no-route
Model unavailable: openrouter/google/gemini-3.8-flash
```

The correction is an environment/provider-route operation, not Relay implementation rework.

## Authorized actions

Codex may:

- inspect the exact beta's non-secret embedded/generated provider, model, and configuration schemas;
- inspect the exact beta's non-secret route-resolution/configuration behavior;
- create a fresh disposable V2 HOME/XDG/data/state/cache/tmp profile;
- create the minimum disposable OpenCode configuration required by the exact beta to register/activate the authorized OpenRouter route;
- source the existing ignored/untracked repository-root `.env` only to provide the existing `OPENROUTER_API_KEY` to the isolated process environment;
- start the exact beta in isolated loopback/headless mode;
- use authenticated local OpenCode health/provider/model/configuration/catalog endpoints;
- perform non-inference route-readiness checks;
- permit only non-inference provider/model discovery performed by the exact beta as part of route/catalog readiness, if that behavior is intrinsic to the beta;
- inspect only the fresh disposable V2 profile and retained sanitized readiness evidence.

## Credential boundary

The existing key may be used only through the ignored repository-root `.env` delivery mechanism.

The credential value MUST NOT be:

- printed;
- inspected;
- hashed;
- copied into the disposable configuration;
- persisted in OpenCode config/database intentionally;
- copied to evidence;
- staged or committed;
- written into Relay candidate/source state.

Configuration must reference environment-based credential discovery if the exact beta supports it.

If exact-beta configuration requires persisting the credential value, STOP.

## Explicitly forbidden

This authority does NOT authorize:

- any prompt;
- any model inference/completion;
- any Relay RuntimeExecutionRequest;
- any new Relay/OpenCode D21 execution session used for agent work;
- any D21 rerun;
- any candidate source change;
- any different provider or model;
- any alias/substitute model ID;
- any protected V1 modification or content inspection;
- any real-project work;
- interactive login or OAuth;
- new credentials;
- Human technical acceptance;
- promotion/merge;
- Slice closure;
- Slice 2.2;
- Phase 3.

## Readiness definition

Environment correction succeeds only if the fresh exact-beta environment can prove, without inference, that the exact pair:

```text
openrouter / google/gemini-3.8-flash
```

is locally resolvable by OpenCode.

Preferred proof order:

1. exact-beta provider/config schema accepts the minimal disposable configuration;
2. isolated server starts healthy;
3. exact beta's own provider/model/catalog surface exposes the exact pair;
4. where the beta provides a non-executing local resolver/validation mechanism, that mechanism accepts the exact pair.

Session creation alone is NOT sufficient proof because prior runs already showed a session could accept the requested pair while execution later failed route resolution.

If the exact beta exposes no non-inference mechanism capable of proving route resolution beyond catalog presence, report that limitation explicitly. Do not use inference to close the evidence gap.

## Stop conditions

STOP if:

- exact beta identity differs;
- candidate SHA differs;
- protected V1 state changes;
- credential value would need to be persisted;
- a provider/model different from the authorized exact pair is required;
- the correction requires Relay source changes;
- the correction requires a prompt or inference;
- route readiness cannot be established without inference;
- environment correction would need to escape the disposable profile.

A stop remains valid evidence.

## Completion boundary

Stop immediately after proving or failing to prove non-inference route readiness.

A successful environment correction does NOT authorize Run 010 or any later live prompt/inference. A separate Human Authority decision is required for a future D21 rerun.
