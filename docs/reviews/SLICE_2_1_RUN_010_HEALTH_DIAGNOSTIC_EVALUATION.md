# Slice 2.1 — Run 010 Health Diagnostic Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-HEALTH-DIAG-EVAL-001`  
**Outcome:** `CORRECT_RUN_010_PREFLIGHT`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

Run-010 evaluation:
RLY-S21-SIDECAR-EVAL-010 — ESCALATE

Health diagnostic handoff:
RLY-S21-SIDECAR-HEALTH-DIAG-HANDOFF-001

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf
```

## Diagnostic result

The existing Run-010 disposable evidence establishes:

```text
failure classification:
TRANSIENT_READINESS_RACE

authenticated /api/health:
HTTP 503

candidate describe:
NOT_RUN

D21:
NOT_STARTED

new diagnostic server starts:
NONE

new prompts:
NONE

new inference calls:
NONE

configuration changes:
NONE
```

The isolated Run-010 log recorded the health HTTP 503 at:

```text
2026-10-08T01:37:59.116Z
```

and database schema bootstrap with 44 migrations beginning 23 ms later.

The retained evidence contains no exception class, runtime error tag, database error, or bootstrap failure.

The health response body was not retained, so the operator-reported `healthy=false` cannot be independently reconstructed from that body; the HTTP 503 itself is preserved.

## Exact-beta interpretation

Read-only inspection of the exact beta's embedded service-monitor logic established that a valid health HTTP 503 is treated as a **waiting/not-ready** state, whereas HTTP 500 is treated as failed.

This supports readiness sequencing rather than an underlying runtime/profile failure.

The retained evidence does not expose the exact internal branch that emitted the 503.

Therefore the evaluation does not overstate causality beyond:

```text
server was reachable/authenticated
health returned 503 before database bootstrap had materially progressed
database bootstrap began 23 ms later
no underlying initialization defect was observed
```

## Structural comparison

Run 010 and the successful environment-correction setup matched on the material environment prerequisites:

- disposable profile structure;
- writable database parent;
- configuration location;
- route-specific provider/model declaration;
- explicit loopback server shape.

Observed structural differences included:

- Run 010 additional agent/permission configuration;
- correction wrapper `umask 077` absent from Run 010;
- Run 010 used `set -a` when sourcing `.env` while correction explicitly exported the key.

No evidence connects any of those differences to the HTTP 503.

They are therefore not classified as causes.

## Candidate/runtime disposition

```text
Relay candidate defect:
NO

accepted Slice 2.1 design defect:
NO

underlying runtime/profile defect:
NOT ESTABLISHED

preflight readiness-ordering defect:
ESTABLISHED

candidate:
UNCHANGED

candidate evaluation:
RLY-S21-EVAL-004 — ACCEPT
```

## Authority disposition

No new Human Authority is required for the corrected Run-010 attempt.

Rationale:

- `RLY-S21-SIDECAR-AUTH-004` already authorizes the exact candidate, exact beta, exact provider/model, fresh disposable profile, and D21 evidence run;
- the aborted attempt submitted no prompt and performed no provider/model inference;
- the correction does not change candidate, provider, model, credential scope, permissions, fixture scope, or D21 authority;
- the only change is the pre-D21 readiness procedure: authenticated HTTP 503 is treated as bounded WAITING rather than immediate terminal failure.

The original Run-010 evidence remains immutable and must not be overwritten.

## Required corrected preflight

The corrected attempt MUST use a new fresh disposable profile and evidence directory.

After the V2 process is reachable:

1. poll authenticated `GET /api/health` at a bounded low rate;
2. treat HTTP 503 as `WAITING` only while the exact V2 process remains alive;
3. continue waiting for HTTP 200 / `healthy=true`;
4. STOP on HTTP 401/403, HTTP 500, process exit, malformed response, or readiness timeout;
5. do not call candidate `describe()`, route catalogs, create a session, or submit a prompt until health reaches 200 / healthy=true.

Use a maximum readiness window of 30 seconds from the first authenticated health attempt, with no more than one health request per 250 ms.

After health is ready, continue the already accepted Run-010 ordering:

```text
candidate describe
model catalog first
provider catalog second
exact-route preflight
D21
```

No second provider/model prompt may be added as compensation for a readiness delay.

## Governance decision

```text
RLY-S21-SIDECAR-HEALTH-DIAG-EVAL-001 — CORRECT_RUN_010_PREFLIGHT

Existing authority:
RLY-S21-SIDECAR-AUTH-004 — REMAINS VALID

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf — UNCHANGED

Implementation rework:
NOT AUTHORIZED / NOT JUSTIFIED

Corrected handoff:
RLY-S21-SIDECAR-RUN010-PREFLIGHT-CORRECTION-001
```

No Human technical acceptance, promotion, Slice closure, Slice 2.2, Phase 3, or real-project agent execution is authorized.
