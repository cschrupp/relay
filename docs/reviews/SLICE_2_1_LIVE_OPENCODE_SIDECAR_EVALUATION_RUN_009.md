# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 009

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-009`  
**Outcome:** `ESCALATE`

## Evaluated subject

```text
Human sidecar authority:
RLY-S21-SIDECAR-AUTH-003 — AUTHORIZED

Run-009 handoff:
RLY-S21-SIDECAR-HANDOFF-003

Governance head:
ddaf62672a507022d59ecf88c861f82a24cf202c

Candidate:
f9a4790c6343561b462d521008c197d776e9ebcf

Independent implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT

Requested provider/model:
openrouter / google/gemini-3.8-flash
```

## Live evidence summary

Run 009 passed all pre-execution and adapter-compatibility gates:

```text
credential source/containment: PASS
protected V1 integrity: PASS
wrapper-only V2 execution: PASS
OpenCode version/hash: PASS
authenticated health: PASS
candidate describe(): PASS
exact model availability at OpenRouter: PASS
fixture/session binding: PASS
prompt schema/admission: PASS
resume:false absent: PASS
observer-before-admission: PASS
one-prompt guard: PASS
execution wake: PASS
runtime_invocation=None: PASS / EXPECTED
```

The event sequence then showed:

```text
session.inbox.enqueued
execution started
instructions updated
inbox delivered
execution failed
```

Inspection reached terminal:

```text
FAILED
```

with zero reported usage and no fixture mutation.

Evidence package:

```text
/tmp/relay-s21-sidecar/evidence-run-009/
```

Reported SHA-256 of `SHA256SUMS.txt`:

```text
25f242b9f51af3fe9162bbbe29f476bf39d86fafc214cd9cf6332dc2ca8f0eb3
```

All 51 reported evidence entries verified.

## F009-A — Run-008 execution-wake finding is resolved live

The exact successor proved that normal `open_execution()` now:

- admits the prompt;
- omits `resume:false`;
- wakes the OpenCode execution loop;
- observes execution-start/progress/failure events;
- keeps exactly one prompt admission.

Therefore the execution-wake correction accepted by `RLY-S21-EVAL-004` is live-confirmed.

## F009-B — invocation provenance correction is live-compatible

The live runtime did not expose a true runtime-native invocation identifier.

The candidate retained:

```text
runtime_invocation = None
```

without fabricating one from an admitted inbox/message ID.

This is consistent with the accepted Relay contract.

## F009-C — BLOCKING EXTERNAL/RUNTIME FAILURE CAUSE IS NOT ESTABLISHED

The OpenCode execution loop started and then terminated as `FAILED` before any fixture edit.

The evidence summary reports zero usage and no provider-side output sufficient to identify the failure cause.

This does **not** establish:

- a Relay adapter defect;
- an accepted-design defect;
- a provider inference defect;
- an authentication defect;
- a model-resolution defect;
- an OpenCode runtime defect.

Those remain hypotheses until sanitized Run-009 runtime diagnostics identify the failure.

The earlier sidecar history makes one hypothesis worth checking without treating it as fact: the exact model was present at OpenRouter, while an earlier OpenCode-beta model listing did not expose the exact pair. A provider/model catalog-resolution failure inside OpenCode could therefore explain execution failure before usage, but Run 009's current report does not prove that cause.

## F009-D — reported provider/model identity does not prove successful inference

Run 009 reported:

```text
openrouter / google/gemini-3.8-flash
identity completeness: FULL
```

This is valid as runtime-reported session/provider-model provenance available to the adapter.

However, because execution failed with zero usage before any successful model turn was observed, the record MUST NOT be interpreted as proof that OpenRouter actually completed an inference request.

No design change follows from this distinction.

## D21 disposition

```text
D21-01 PASS
D21-02 PASS
D21-03 PASS
D21-04 PASS
D21-05 FAIL — runtime execution terminal FAILED; requested edit absent
D21-06 PASS — live normalized sequence through terminal failure
D21-07 NOT_RUN
D21-08 NOT_RUN
D21-09 NOT_RUN
D21-10 FAIL — independent fixture diff empty
D21-11 PASS — runtime-reported requested/actual identity recorded; no invocation ID fabricated
D21-12 NOT_RUN
D21-13 NOT_RUN
D21-14 NOT_APPLICABLE
D21-15 NOT_RUN
D21-16 NOT_RUN
D21-17 PASS
D21-18 NOT_RUN
```

## Classification

```text
candidate prompt mapping:
PASS

candidate execution wake:
PASS

candidate event observation:
PASS

candidate terminal failure observation:
PASS

Relay candidate implementation defect:
NOT ESTABLISHED

accepted design defect:
NOT ESTABLISHED

OpenCode/provider execution prerequisite or runtime defect:
POSSIBLE / NOT YET CLASSIFIED

exact underlying failure cause:
NOT ESTABLISHED

D21:
INCOMPLETE

Human technical acceptance:
NOT ELIGIBLE
```

## Governance decision

```text
Run 009:
STOPPED FAIL-CLOSED

Evaluation:
RLY-S21-SIDECAR-EVAL-009 — ESCALATE

Candidate:
UNCHANGED
f9a4790c6343561b462d521008c197d776e9ebcf

Implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT REMAINS THE CURRENT DETERMINISTIC CANDIDATE EVALUATION
```

No implementation/design rework is authorized by Run 009 at this stage.

Proceed only with bounded diagnostic extraction under `RLY-S21-SIDECAR-DIAG-HANDOFF-001`.

No Human technical acceptance, promotion, Slice closure, Slice 2.2, or Phase 3 authority is issued.
