# Relay — Slice 2.1 Successor Live OpenCode Sidecar Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Record:** `RLY-S21-SIDECAR-AUTH-002`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority explicitly authorizes a bounded live OpenCode Slice 2.1 sidecar rerun against exact successor candidate:

```text
5df1add9ed829a62a99d7f25f561a0f492ff5c73
```

under the same safety, credential, disposable-fixture, provider/model, and no-real-project-work constraints as `RLY-S21-SIDECAR-AUTH-001` and the existing V2 provisioning authority.

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

Canonical authority/evaluation basis:
d1d1f05c8e0b40ee12555f5b8d18d0f9ab357398

Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Independent implementation evaluation:
RLY-S21-EVAL-003 — ACCEPT

Exact successor candidate under evidence:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

Exact accepted design:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Prior live sidecar finding:
RLY-S21-SIDECAR-EVAL-007 — REWORK
```

This authority is SHA-bound. The sidecar MUST exercise the exact successor above and may not silently substitute another implementation SHA.

## Authorized purpose

The sole purpose is to collect candidate-specific live compatibility and behavioral evidence required before Human technical acceptance.

This is evidence generation, not product execution.

Because the candidate changed after Run 007, Run 008 must produce a fresh candidate-specific D21 evidence record. Prior environment/procedure lessons may be reused, but prior D21 PASS results are not automatically inherited as proof for this SHA.

## Authorized environment

The sidecar MUST use:

- a disposable candidate checkout at the exact successor SHA;
- a disposable fixture repository/workspace;
- a disposable outside-directory canary;
- a disposable local bare remote for push-denial testing;
- an explicit isolated OpenCode V2 loopback endpoint;
- a fresh disposable HOME/XDG/OPENCODE_DB/TMPDIR profile;
- wrapper-enforced V2 isolation for every V2 invocation;
- the Human-selected ignored/untracked repository-root local `.env` only as the delivery mechanism for the already-existing OpenRouter credential.

The `.env` value remains secret and external to Relay durable state. It must not be copied into candidate, fixture, evidence, OpenCode configuration as an intentionally persisted credential, or Git history.

Protected V1 OpenCode state must remain metadata-only and unchanged.

## Provider/model authority

This record authorizes only the minimum real provider/model calls necessary to execute the accepted D21 fixture protocol using:

```text
openrouter / google/gemini-3.8-flash
```

Rules:

- requested provider/model identity must be recorded;
- actual provider/model identity must be recorded when exposed;
- missing actual identity must be PARTIAL/UNKNOWN, never inferred;
- no alternate provider/model may be selected implicitly;
- provider/model selection remains fixed within each digest-bound execution;
- no interactive login, OAuth flow, new credential creation, or protected V1 credential import;
- token/cost consumption must be minimized;
- no provider/model call may perform Relay's real engineering work.

## D21 requirement

Run 008 must attempt and record fresh evidence for all D21 items 01 through 18 against the successor candidate.

Resume remains tested only if freshly advertised.

The mock evaluator-role session proves session separation only; it does not confer evaluator authority.

## Stop conditions

STOP and report if:

- candidate SHA differs;
- protected V1 state changes;
- V2 isolation cannot be maintained;
- authenticated V2 compatibility regresses;
- prompt admission still fails;
- exact model is unavailable;
- provider/model identity cannot be represented as designed;
- permission denial semantics cannot be proven;
- external-directory or push denial cannot be demonstrated;
- cancellation/inspection would require weakening exact binding;
- event behavior contradicts accepted semantics;
- credentials appear in retained evidence;
- candidate source modification appears necessary;
- persistence/schema/lifecycle/governance changes appear necessary;
- any broader real-project authority would be required.

Do not patch around a live mismatch during the sidecar.

## Explicit non-authority

This record does NOT authorize:

- Human technical acceptance;
- promotion/merge;
- Slice 2.1 closure;
- Slice 2.2 work;
- Phase 3;
- real-project agent execution;
- autonomous evaluator authority;
- interactive steering;
- persistent runtime/session storage;
- mutation of Relay's canonical worktree.

Successful sidecar evidence makes the successor eligible for independent sidecar-evidence evaluation only. Human acceptance remains a separate decision.

**Live runtime evidence != Human technical acceptance.**
