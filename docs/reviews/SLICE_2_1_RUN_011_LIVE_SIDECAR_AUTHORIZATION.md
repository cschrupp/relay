# Relay — Slice 2.1 Live OpenCode Sidecar Run 011 Authorization

**Document class:** Immutable Human Authority record
**Status:** IMMUTABLE
**Date:** 2026-10-08
**Record:** `RLY-S21-SIDECAR-AUTH-005`
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority authorizes a bounded live OpenCode Slice 2.1 Run 011 against exact accepted successor:

```text
4f785f08576e465cd0aa278f927fa4b7253e3f49
```

using exact runtime:

```text
OpenCode: 0.0.0-beta-17823
binary SHA-256: e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7
```

and exact provider/model:

```text
openrouter / google/gemini-3.8-flash
```

under the established disposable-fixture, wrapper-isolation, credential-containment, corrected health-readiness, corrected exact-beta provider/model preflight, no-real-project-work, and D21 safety constraints.

Run 011 MUST collect fresh candidate-specific D21 evidence against this exact successor SHA. Prior Run 010r3 results remain historical evidence only and MUST NOT be silently inherited.

## Authority basis

```text
Accepted Slice 2.1 design:
RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Run 010r3 live evaluation:
RLY-S21-SIDECAR-EVAL-010R3 — REWORK

Cancellation rework:
RLY-S21-IMPL-REWORK-HANDOFF-003

Successor evaluation:
RLY-S21-EVAL-005 — ACCEPT

Successor CI:
37873019090 — SUCCESS

Canonical authorization basis:
053dbfa2faec8d9c45c8a1c9779c33e162dc1eab

Canonical basis CI:
37873295980 — SUCCESS
```

The prior live authority `RLY-S21-SIDECAR-AUTH-004` remains immutable and exact-SHA-bound to `f9a4790c6343561b462d521008c197d776e9ebcf`. It does not transfer to this successor.

## Corrected preflight contract

Health polling is bounded to 30 seconds from the first authenticated request and no more than one request per 250 ms. HTTP 503 is WAITING only while the exact V2 process remains alive. HTTP 200 with `healthy=true` is PASS. HTTP 401/403, HTTP 500, process exit, malformed response, or timeout are STOP conditions.

Model catalog request semantics:

```text
GET /api/model?location[directory]=<absolute-fixture-directory>
```

Model predicate:

```text
id == "google/gemini-3.8-flash"
providerID == "openrouter"
enabled == true
status == "active"
package == "aisdk:@openrouter/ai-sdk-provider" when present
```

Provider predicate:

```text
id == "openrouter"
activation in {"auto", "enabled"}
package == "aisdk:@openrouter/ai-sdk-provider"
```

Do not require nonexistent exact-beta provider fields such as `active`, boolean `enabled/disabled`, or nested `api.type/api.package`.

Credential presence remains a separate gate. Catalog readiness does not prove credential consumption.

## Credential boundary

Use only the existing ignored/untracked repository-root `.env` to deliver the already-existing `OPENROUTER_API_KEY` into the isolated process environment.

The credential value MUST NOT be printed, inspected, hashed, copied, staged, committed, intentionally persisted in OpenCode configuration/database, or retained in evidence.

No interactive login, OAuth, new credential, protected V1 credential import, or alternate credential source is authorized.

## D21 authority

After all fresh preflight gates pass, Run 011 may execute the complete fresh D21-01 through D21-18 protocol against exact successor `4f785f08576e465cd0aa278f927fa4b7253e3f49`.

The canonical disposable fixture task remains:

```text
Add a subtract(a, b) function to app.py and add one deterministic test.
Do not touch files outside this repository.
Do not push.
```

Only the minimum provider/model calls required by D21 are authorized. No alternate provider/model, alias, or fallback is authorized.

`runtime_invocation=None` remains correct if the pinned beta exposes no true runtime-native invocation identity.

D21-12 MUST specifically exercise the corrected cancellation path and prove:

```text
POST /api/session/{sessionID}/interrupt
-> HTTP 204 No Content

candidate cancel()
-> RuntimeControlAckState.REQUESTED

second identical cancel()
-> cached identical acknowledgment

interrupt POST count:
1

JSON body parse:
NOT REQUIRED
```

If the execution becomes terminal before interrupt and the adapter returns `ALREADY_TERMINAL`, report that honestly; the 204 fix remains unproven for that attempt.

## Stop conditions

STOP on candidate/runtime identity mismatch, wrapper-isolation failure, protected V1 mutation, credential containment failure, readiness/preflight failure, provider/model mismatch or fallback, prompt/execution-wake regression, missing requested edit, permission-denial failure, inspect/binding failure, cancellation mismatch, credential leakage, candidate/source modification need, or any requirement for broader real-project authority.

Do not patch the candidate or runtime configuration after D21 execution begins.

## Explicit non-authority

This record does NOT authorize candidate modification, protected V1 modification, alternate provider/model, Human technical acceptance, promotion/merge, Slice 2.1 closure, Slice 2.2, Phase 3, real-project agent execution, autonomous evaluator authority, interactive steering, or durable runtime/session persistence.

Successful Run 011 evidence creates evidence for independent evaluation only.
