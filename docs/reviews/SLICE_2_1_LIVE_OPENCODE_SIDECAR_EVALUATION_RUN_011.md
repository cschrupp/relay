# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 011

**Document class:** Immutable evaluation record
**Status:** IMMUTABLE
**Date:** 2026-10-08
**Project:** Relay
**Slice:** 2.1 — Agent Runtime Contract
**Record:** `RLY-S21-SIDECAR-EVAL-011`
**Outcome:** `ESCALATE`

## Subject

```text
Human Authority:
RLY-S21-SIDECAR-AUTH-005 — AUTHORIZED

Execution handoff:
RLY-S21-SIDECAR-HANDOFF-005

Governance head:
4227448806a8834bd9ff2129a3e85329cf2f3299

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate deterministic evaluation:
RLY-S21-EVAL-005 — ACCEPT

Exact OpenCode:
0.0.0-beta-17823

Exact provider/model:
openrouter / google/gemini-3.8-flash
```

## Evaluation summary

Run 011 is incomplete.

It successfully exercised the accepted successor through the live cancellation fix and most of D21, but it did not complete the full candidate-specific evidence gate.

The correct disposition is:

```text
candidate defect:
NO

accepted design defect:
NO

live cancellation compatibility:
PROVEN

complete D21 evidence:
NOT PROVEN

protected V1 precondition:
NOT_ATTESTABLE

implementation rework:
NOT JUSTIFIED

Human technical acceptance:
NOT ELIGIBLE
```

## Fresh environment and route evidence

Run 011 established:

```text
fresh disposable profile:
PASS

.env exists / ignored / untracked:
PASS / PASS / PASS

OPENROUTER_API_KEY presence:
PASS

credential material:
NOT RECORDED

wrapper isolation:
PASS

direct V2 invocations:
0

OpenCode:
0.0.0-beta-17823

binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

health:
PASS

health attempts:
4

first readiness state:
CONNECTING

final health:
HTTP 200 / healthy=true

elapsed to ready:
0.845 seconds

503 observed:
NO

candidate describe:
PASS

model request:
GET /api/model with location[directory] — PASS / HTTP 200

model preflight:
PASS

provider preflight:
PASS

route preflight:
PASS

requested provider/model:
openrouter / google/gemini-3.8-flash

actual provider/model:
openrouter / google/gemini-3.8-flash

identity completeness:
FULL

runtime_invocation:
NONE
```

## F011-A — LIVE SUCCESS — cancellation compatibility fix proven

D21-12 freshly exercised the successor's corrected cancellation behavior.

Live evidence established:

```text
interrupt response:
HTTP 204 No Content

first Relay cancellation acknowledgment:
REQUESTED

observed runtime status:
RUNNING

JSON parse required:
NO

JSON parse attempts:
0

second identical cancel:
cached equal acknowledgment

interrupt POST count:
1

other session:
UNAFFECTED / remained SUCCEEDED
```

This directly resolves the live incompatibility that caused Run 010r3 D21-12 to fail.

The successor's exact-beta 204 cancellation correction is therefore live-proven.

No candidate rework is justified by D21-12.

## F011-B — BLOCKING EVIDENCE GAP — D21-16 and D21-18 not run

The continuation server exited before:

```text
D21-16 — safe failure normalization
D21-18 — distinct mock evaluator session
```

These checks therefore remain:

```text
NOT_RUN
```

Prior-candidate or prior-run evidence cannot be silently inherited because Run 011 authority explicitly required fresh candidate-specific D21 evidence against the successor.

The full D21 gate is consequently incomplete.

## F011-C — BLOCKING ATTESTATION GAP — protected V1 baseline captured too late

The Run 011 handoff required:

```text
Capture protected V1 metadata before any V2 process.
```

The operator instead captured the protected-V1 metadata snapshot after the wrapped V2 version invocation.

Final metadata matched that later snapshot, but the run cannot prove whether any protected V1 metadata changed before the snapshot was taken.

Therefore:

```text
protected V1:
NOT_ATTESTABLE
```

This is an evidence-ordering/operator defect, not proof that protected V1 changed.

It also is not a Relay candidate defect.

A continuation from the existing post-start state cannot repair this evidence gap; a future qualifying run must capture the V1 witness before any V2 invocation.

## F011-D — continuation failure is not a candidate failure

D21-15 evidence was successfully captured before an operator evidence-collector field-name error.

A continuation server was then started but exited before D21-16 and D21-18 could be completed.

No evidence establishes that the accepted candidate caused that continuation-server exit.

Therefore:

```text
candidate/runtime adapter defect from continuation exit:
NOT ESTABLISHED

operator/evidence-harness issue:
ESTABLISHED

environment/runtime defect:
NOT ESTABLISHED
```

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
D21-12: PASS
D21-13: PASS
D21-14: NOT_APPLICABLE — RESUME not advertised
D21-15: PASS
D21-16: NOT_RUN
D21-17: PASS
D21-18: NOT_RUN
```

Three prompts were admitted during the run. At least one provider/model inference completed; exact provider request count is unavailable.

## Containment disposition

```text
fixture:
requested subtract(a, b) + one deterministic test

fixture tests:
2 passed

outside canary:
UNCHANGED

forbidden local remote:
UNCHANGED

candidate/source changes:
NONE

real-project calls:
NONE

credential containment:
PASS
```

## Governance decision

```text
Run 011:
INCOMPLETE

Evaluation:
RLY-S21-SIDECAR-EVAL-011 — ESCALATE

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Candidate deterministic status:
RLY-S21-EVAL-005 — ACCEPT / UNCHANGED

Live 204 cancellation fix:
PROVEN

Full live D21 gate:
INCOMPLETE

Human technical acceptance:
NOT ELIGIBLE

Implementation rework:
NOT AUTHORIZED / NOT JUSTIFIED

Next qualifying live run:
FRESH HUMAN AUTHORITY REQUIRED
```

Because Run 011 already exercised live provider/model execution and the protected-V1 precondition cannot be repaired by continuation, the next qualifying evidence collection must be a fresh run from new disposable state under a new exact-SHA Human Authority.

That future authority is not granted by this evaluation.

No promotion, Slice 2.1 closure, Slice 2.2, Phase 3, or real-project execution is authorized.

## Evidence

```text
evidence package:
/tmp/relay-s21-sidecar/evidence-run-011/

report:
/tmp/relay-s21-sidecar/evidence-run-011/report.md

manifest:
/tmp/relay-s21-sidecar/evidence-run-011/manifest.json

SHA256SUMS.txt SHA-256:
fc78243cd2ef15dbd0ed774387f36c4484814759b8155105405a29b195c2c356
```
