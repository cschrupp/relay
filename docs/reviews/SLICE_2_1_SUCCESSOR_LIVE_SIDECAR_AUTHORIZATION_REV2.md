# Relay — Slice 2.1 Successor Live OpenCode Sidecar Authorization — Revision 2

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-AUTH-003`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority explicitly authorizes a bounded live OpenCode Slice 2.1 sidecar rerun against exact candidate:

```text
f9a4790c6343561b462d521008c197d776e9ebcf
```

under the same safety, credential, disposable-fixture, provider/model, and no-real-project-work constraints as `RLY-S21-SIDECAR-AUTH-002` and the existing V2 provisioning authority.

The existing OpenRouter credential and exact model:

```text
provider:
openrouter

model:
google/gemini-3.8-flash
```

are authorized solely to complete the D21 evidence protocol.

## Exact subject

```text
Repository:
cschrupp/relay

Canonical governance basis at authorization decision:
e9c9f115cbe8a119fa76f7893234f2c57de3baa0

Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Independent implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT

Exact successor candidate under evidence:
f9a4790c6343561b462d521008c197d776e9ebcf

Exact accepted design:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Prior live sidecar finding:
RLY-S21-SIDECAR-EVAL-008 — REWORK
```

This authority is exact-SHA-bound. Run 009 may not silently substitute any later implementation SHA.

## Purpose and evidence boundary

The sole purpose is candidate-specific live compatibility and behavioral evidence required before Human technical acceptance.

Run 009 must collect fresh evidence for D21-01 through D21-18 against this exact candidate. Prior runs remain historical evidence; their PASS results are not automatically inherited as proof for this SHA.

Procedural lessons from prior runs may be reused.

This is evidence generation, not real Relay engineering.

## Authorized environment and credential handling

The sidecar MUST use:

- a disposable detached candidate checkout at the exact successor SHA;
- a disposable fixture repository/workspace;
- a disposable outside-directory canary;
- a disposable local bare remote for push-denial testing;
- an explicit isolated OpenCode V2 loopback endpoint;
- a fresh disposable HOME/XDG/OPENCODE_DB/TMPDIR profile;
- wrapper-enforced V2 isolation for every V2 invocation;
- the Human-selected ignored/untracked repository-root local `.env` only as delivery for the already-existing OpenRouter credential.

The credential value remains secret and external to Relay durable state. It must never enter candidate source, fixture content, retained evidence, OpenCode configuration as an intentionally persisted credential, or Git history.

Protected V1 OpenCode state remains metadata-only and must remain unchanged.

## Provider/model authority

Only the minimum real provider/model calls needed for D21 are authorized.

Exact selection:

```text
openrouter / google/gemini-3.8-flash
```

No alternate model may be selected implicitly.

Requested and actual identities must be recorded separately. Missing actual identity must remain PARTIAL/UNKNOWN, never inferred.

No interactive login, OAuth flow, new credential creation, or protected V1 credential import is authorized.

## Candidate-specific expected invocation semantics

The accepted successor intentionally leaves:

```text
RuntimeExecutionHandle.runtime_invocation = None
```

when the pinned beta exposes only an admitted inbox/user-item ID and no runtime-native invocation identity.

Run 009 must not manufacture an invocation identity from the admitted message/input ID, and the absence of a true invocation ID is not itself a failure.

## Stop conditions

STOP and report if:

- candidate SHA differs;
- protected V1 state changes;
- V2 isolation cannot be maintained;
- authenticated V2 compatibility regresses;
- prompt admission or execution wake fails;
- the exact model is unavailable;
- provider/model identity contradicts the request or cannot be represented safely;
- external-directory or push denial cannot be demonstrated;
- cancellation/inspection requires weakening exact binding;
- event behavior contradicts accepted semantics;
- credentials appear in retained evidence;
- candidate source modification appears necessary;
- persistence/schema/lifecycle/governance changes appear necessary;
- broader real-project authority would be required.

Do not patch around a live mismatch during the sidecar.

## Explicit non-authority

This record does NOT authorize:

- Human technical acceptance;
- promotion/merge;
- Slice 2.1 closure;
- Slice 2.2;
- Phase 3;
- real-project agent execution;
- autonomous evaluator authority;
- interactive steering;
- persistent runtime/session storage;
- mutation of Relay's canonical worktree.

Successful evidence makes the candidate eligible only for independent sidecar-evidence evaluation. Human acceptance remains a separate decision.
