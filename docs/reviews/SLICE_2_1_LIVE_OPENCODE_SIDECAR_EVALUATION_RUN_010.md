# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 010

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-010`  
**Outcome:** `ESCALATE`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

Run-010 handoff:
RLY-S21-SIDECAR-HANDOFF-004

Governance head:
32d076c5f99565952db1416a56456fa76b411272

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Candidate evaluation:
RLY-S21-EVAL-004 — ACCEPT

Environment evaluation:
RLY-S21-SIDECAR-ENV-EVAL-001 — READY_FOR_RUN_010_AUTHORIZATION
```

## Run result

Run 010 recreated a fresh disposable V2 profile and the minimum non-secret route configuration, then stopped at the mandatory health gate before candidate `describe()`, route preflight, session creation, or any D21 prompt.

Observed:

```text
exact beta:
0.0.0-beta-17823 — PASS

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7 — PASS

fresh profile:
PASS

minimum non-secret route config:
PASS

.env exists / ignored / untracked:
PASS / PASS / PASS

OPENROUTER_API_KEY presence:
PASS

protected V1 metadata:
UNCHANGED

wrapper-only V2 execution:
PASS

authenticated /api/health:
HTTP 503

healthy:
false

candidate describe():
NOT_RUN

route preflight:
NOT_RUN

prompt/inference:
NONE
```

## Classification

This failure occurred before the Relay candidate was exercised.

Therefore:

```text
Relay candidate defect:
NOT ESTABLISHED

accepted Slice 2.1 design defect:
NOT ESTABLISHED

D21 failure:
NOT ESTABLISHED — D21 DID NOT START

OpenCode disposable runtime/environment failure:
ESTABLISHED AT HEALTH GATE

exact underlying cause:
NOT ESTABLISHED
```

The candidate remains unchanged and its deterministic evaluation remains:

```text
RLY-S21-EVAL-004 — ACCEPT
```

## Health interpretation boundary

Run 010 returned authenticated HTTP 503 with `healthy=false`.

That is not sufficient by itself to distinguish among:

- exact-beta configuration parse/validation failure;
- profile/database initialization failure;
- provider/catalog initialization failure;
- service/application initialization failure;
- transient readiness failure;
- another exact-beta runtime error.

The prior environment-correction run proved that a disposable profile using the same intended non-secret provider/model recipe can reach authenticated healthy state and active catalogs. Run 010 therefore requires diagnostic comparison before another rerun or environment change.

Do not assume the 503 is merely a timing race.

Do not attribute it to Relay.

## D21 disposition

```text
D21-01 through D21-18:
NOT_RUN

Reason:
mandatory authenticated health gate failed before candidate describe and D21 start
```

The separate pre-D21 connection-auth leak check passed, but D21-17 itself was not executed.

## Governance decision

```text
Run 010:
STOPPED FAIL-CLOSED

Evaluation:
RLY-S21-SIDECAR-EVAL-010 — ESCALATE

Candidate:
UNCHANGED
f9a4790c6343561b462d521008c197d776e9ebcf

Implementation rework:
NOT AUTHORIZED / NOT JUSTIFIED

Next action:
RLY-S21-SIDECAR-HEALTH-DIAG-HANDOFF-001
```

Proceed only with diagnostic extraction from existing disposable Run-010 evidence and profile.

No new prompt, provider/model inference, D21 rerun, configuration correction, candidate change, Human technical acceptance, promotion, Slice closure, Slice 2.2, or Phase 3 authority is issued.
