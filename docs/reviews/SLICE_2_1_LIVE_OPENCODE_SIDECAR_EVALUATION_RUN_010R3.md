# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 010r3

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-010R3`  
**Outcome:** `REWORK`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

Corrective handoff:
RLY-S21-SIDECAR-RUN010-MODEL-QUERY-CORRECTION-001

Governance head:
6d3bf8d61ec1215fe1804b8585af3dc8a1aafe78

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Prior deterministic evaluation:
RLY-S21-EVAL-004 — ACCEPT
```

## Live evidence summary

Run 010r3 passed the complete environment and preflight sequence:

```text
fresh profile / wrapper isolation:
PASS

exact V2 version/hash:
PASS

health:
PASS

candidate describe:
PASS

model query shape:
PASS

model preflight:
PASS

provider preflight:
PASS

route preflight:
PASS

credential presence:
PASS

actual provider/model:
openrouter / google/gemini-3.8-flash

runtime_invocation:
NONE
```

It then exercised the candidate through live D21.

Established before the failure:

```text
D21-01 through D21-11:
PASS

requested fixture edit:
PASS

normalized events:
PASS

external-directory denial:
PASS

push denial:
PASS

allowed edit:
PASS

inspect + independent diff:
PASS

provider/model provenance:
PASS
```

The fixture gained `subtract(a, b)` and one deterministic test. Two fixture tests passed.

## F010R3-A — BLOCKING — cancellation success response incompatible with adapter

At D21-12 the unchanged candidate called:

```text
POST /api/session/{sessionID}/interrupt
```

The exact live OpenCode beta returned:

```text
HTTP 204 No Content
```

The candidate currently recognizes cancellation success only when:

```text
status_code == 200
```

and then attempts to parse a JSON response body.

Because 204 is not 200, the candidate normalized the successful interrupt response as:

```text
TRANSPORT
```

and D21-12 failed.

This is an adapter implementation incompatibility.

## Design disposition

The accepted design does not require HTTP 200 or a JSON body for cancellation.

S2.1-D12 requires an idempotent Relay control operation:

```text
RuntimeCancelRequest
    -> RuntimeControlAck
```

with acknowledgment states:

```text
REQUESTED
ALREADY_TERMINAL
NOT_FOUND
DENIED
```

The OpenCode-native response representation remains behind the adapter boundary.

Therefore:

```text
accepted Slice 2.1 design defect:
NO

Relay candidate implementation defect:
YES
```

A successful empty 204 response can be normalized to the Relay-level acknowledgment without changing the accepted public contract.

## Deterministic mock finding

The current deterministic OpenCode mock returns:

```text
HTTP 200
{"data": true}
```

for `/interrupt`.

It therefore encoded the wrong live success contract and could not detect the incompatibility.

The mock must be corrected to the exact pinned-beta interrupt success contract established by live evidence and exact-beta schema inspection.

## D21 disposition

```text
D21-01: PASS
D21-02: PASS
D21-03: PASS
D21-04: PASS
D21-05: PASS
D21-06: PASS
D21-07: PASS
D21-08: PASS
D21-09: PASS
D21-10: PASS
D21-11: PASS
D21-12: FAIL — HTTP 204 success misclassified as TRANSPORT
D21-13: NOT_RUN
D21-14: NOT_APPLICABLE — RESUME not advertised
D21-15: PASS — event-stream interruption remained inspectable
D21-16: NOT_RUN
D21-17: PASS
D21-18: NOT_RUN
```

D21 remains incomplete.

The trailing blank-line warning in the fixture diff is retained evidence but is not the blocking defect.

## Governance decision

```text
Run 010r3:
STOPPED FAIL-CLOSED

Evaluation:
RLY-S21-SIDECAR-EVAL-010R3 — REWORK

Candidate:
PRESERVED
f9a4790c6343561b462d521008c197d776e9ebcf

Prior deterministic evaluation:
RLY-S21-EVAL-004 — HISTORICAL ACCEPT FOR THE EVALUATED CANDIDATE,
BUT LIVE TECHNICAL ELIGIBILITY IS BLOCKED BY THIS FINDING

Accepted design:
UNCHANGED

Implementation rework:
AUTHORIZED UNDER EXISTING RLY-S21-IMPL-AUTH-001 VIA
RLY-S21-IMPL-REWORK-HANDOFF-003
```

No Human technical acceptance, promotion, Slice closure, Slice 2.2, Phase 3, or real-project execution is authorized.

## Evidence

```text
/tmp/relay-s21-sidecar/evidence-run-010r3/

SHA256SUMS.txt SHA-256:
a701a88a6bc513d2bfe2fd166a0bb1e41d9ac72690eeb22c1cc87df446fcfb61
```
