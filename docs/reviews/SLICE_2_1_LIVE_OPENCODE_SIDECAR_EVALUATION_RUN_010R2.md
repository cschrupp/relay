# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 010r2

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-08  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-010R2`  
**Outcome:** `ESCALATE`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED

Corrective handoff:
RLY-S21-SIDECAR-RUN010-PROVIDER-PREFLIGHT-CORRECTION-001

Governance head:
2b24ba6d0c5f82f47b78b3c5b577c222f70c492f

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf
```

## Result

Run 010r2 started from fresh disposable state and passed the gates that precede the model-catalog request:

```text
fresh disposable state:
PASS

authenticated health:
PASS

candidate OpenCodeRuntime.describe():
PASS

protected V1:
UNCHANGED

candidate/source state:
UNCHANGED

new prompts:
0

provider/model inference calls:
0
```

The model-catalog request then returned HTTP 400 because the operator encoded the location parameter as JSON rather than using the exact-beta query encoding required by the route.

The operator identified the procedural error as:

```text
incorrect:
JSON location payload

required:
location[directory]=<fixture-directory>
```

The run stopped immediately.

## Classification

```text
Relay candidate defect:
NO

accepted design defect:
NO

OpenCode runtime defect:
NO

provider/model availability finding:
NONE

environment defect:
NO

operator/request-construction defect:
YES

D21:
NOT_STARTED
```

HTTP 400 at this preflight request does not establish provider or model unavailability because the request itself did not satisfy the exact-beta route contract.

## Authority disposition

Existing Human Authority remains sufficient:

```text
RLY-S21-SIDECAR-AUTH-004 — AUTHORIZED
```

No scope expansion occurred:

- no prompt was admitted;
- no provider/model inference occurred;
- no execution/session work began;
- no candidate change occurred;
- no credential boundary changed;
- the next correction changes only the model-catalog query encoding.

## Governance decision

```text
Run 010r2:
STOPPED FAIL-CLOSED BEFORE D21

Evaluation:
RLY-S21-SIDECAR-EVAL-010R2 — ESCALATE

Corrective handoff:
RLY-S21-SIDECAR-RUN010-MODEL-QUERY-CORRECTION-001

Next attempt:
Run 010r3

Implementation rework:
NOT AUTHORIZED / NOT JUSTIFIED
```

No Human technical acceptance, promotion, Slice closure, Slice 2.2, Phase 3, or real-project execution is authorized.
