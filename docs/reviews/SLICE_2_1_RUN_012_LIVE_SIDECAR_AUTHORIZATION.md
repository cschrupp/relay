# Relay — Slice 2.1 Live OpenCode Sidecar Run 012 Authorization

**Document class:** Immutable Human Authority record
**Status:** IMMUTABLE
**Date:** 2026-10-08
**Record:** `RLY-S21-SIDECAR-AUTH-006`
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human Authority authorizes a bounded live OpenCode Slice 2.1 Run 012 against exact candidate:

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

Run 012 MUST collect fresh complete candidate-specific D21-01 through D21-18 evidence against this exact SHA.

Prior Run 011 evidence, including its successful D21-12 cancellation proof, is historical only and MUST NOT be silently inherited.

## Authority basis

```text
Accepted Slice 2.1 design:
RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Candidate deterministic evaluation:
RLY-S21-EVAL-005 — ACCEPT

Run 011 evaluation:
RLY-S21-SIDECAR-EVAL-011 — ESCALATE

Run 011 disposition:
INCOMPLETE LIVE EVIDENCE
NO CANDIDATE REWORK JUSTIFIED
LIVE HTTP 204 CANCELLATION FIX PROVEN

Canonical authorization basis:
6eb0ea1cd2d12714d1c86d091507bf4ab3c3e8d9

Canonical basis CI:
37878702942 — SUCCESS
```

## Mandatory protected-V1 ordering gate

This is a hard precondition for Run 012.

Before ANY V2 invocation of any kind, including version/help/server/utility calls:

1. capture the protected V1 metadata witness;
2. retain only authorized metadata, never protected V1 contents;
3. verify the witness is complete enough to compare after the run.

Only after the protected-V1 baseline witness exists may any wrapped V2 command execute.

If any V2 invocation occurs before the protected-V1 baseline witness is captured:

```text
STOP
PROTECTED V1 = NOT_ATTESTABLE
RUN 012 CANNOT QUALIFY
```

A later matching snapshot cannot repair this ordering violation.

## Exact runtime and wrapper boundary

Every deliberate V2 invocation MUST pass through the Run-012 isolation wrapper.

Direct V2 invocation count must remain zero.

If the exact beta binary is absent, the already-authorized full-isolation provisioning procedure may restore exactly:

```text
@opencode-ai/cli@0.0.0-beta-17823
```

and the exact binary SHA-256 above. No other version is authorized.

## Corrected readiness and route preflight

Use the established bounded health-readiness semantics:

```text
maximum window:
30 seconds from first authenticated health request

maximum rate:
1 request per 250 ms

503:
WAITING while exact V2 process remains alive

200 + healthy=true:
PASS

401/403:
STOP

500:
STOP

process exit:
STOP

malformed response:
STOP

timeout:
STOP
```

Use exact model request semantics:

```text
GET /api/model?location[directory]=<absolute-fixture-directory>
```

Require exact model:

```text
id == "google/gemini-3.8-flash"
providerID == "openrouter"
enabled == true
status == "active"
package == "aisdk:@openrouter/ai-sdk-provider" when present
```

Require exact provider:

```text
id == "openrouter"
activation in {"auto", "enabled"}
package == "aisdk:@openrouter/ai-sdk-provider"
```

Do not require provider fields the exact beta does not expose.

Credential presence is a separate gate and does not prove credential consumption.

## Credential boundary

Use only the existing ignored/untracked repository-root `.env` to deliver the already-existing `OPENROUTER_API_KEY`.

The credential value MUST NOT be printed, inspected, hashed, copied, staged, committed, intentionally persisted in OpenCode configuration/database, or retained in evidence.

No interactive login, OAuth, new credential, protected V1 credential import, alternate credential source, provider alias, model alias, or fallback is authorized.

## D21 authority

After all fresh preflight gates pass, Run 012 may execute the complete fresh D21-01 through D21-18 protocol against exact candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49`.

Canonical disposable fixture task:

```text
Add a subtract(a, b) function to app.py and add one deterministic test.
Do not touch files outside this repository.
Do not push.
```

Only the minimum provider/model calls required by D21 are authorized.

Every applicable D21 item must be freshly exercised. Prior Run 011 PASS results are historical context only.

D21-12 MUST again prove the successor's cancellation behavior:

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
NO
```

If the execution becomes terminal before the interrupt and the adapter returns `ALREADY_TERMINAL`, report that honestly; the D21-12 live proof for Run 012 is incomplete.

D21-16 and D21-18 MUST be freshly run and cannot be inherited from any earlier attempt.

## Stop conditions

STOP on:

- candidate SHA mismatch;
- runtime version/hash mismatch;
- protected-V1 baseline witness not captured before first V2 invocation;
- wrapper isolation failure;
- protected V1 mutation;
- credential containment failure;
- health/readiness failure;
- model/provider preflight failure;
- provider/model mismatch or fallback;
- prompt-admission or execution-wake regression;
- missing requested edit;
- containment/permission denial failure;
- inspect/diff binding failure;
- cancellation targeting/idempotency failure;
- event-continuity contradiction;
- failure to execute D21-16 or D21-18 safely;
- credential material entering retained evidence;
- candidate/source modification requirement;
- any requirement for real-project authority.

Do not patch candidate or runtime configuration after D21 execution begins.

## Explicit non-authority

This record does NOT authorize:

- candidate modification;
- protected V1 modification;
- alternate provider/model;
- Human technical acceptance;
- promotion/merge;
- Slice 2.1 closure;
- Slice 2.2;
- Phase 3;
- real-project agent execution;
- autonomous evaluator authority;
- interactive steering;
- durable runtime/session persistence.

Successful Run 012 evidence creates evidence for independent evaluation only. Human technical acceptance remains a separate Human decision.
