# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 007

**Document class:** Immutable evaluation record
**Status:** IMMUTABLE
**Date:** 2026-10-07
**Record:** `RLY-S21-SIDECAR-EVAL-007`
**Outcome:** `REWORK`

## Subject

- Sidecar authority: `RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED`
- V2 provisioning authority: `RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED`
- Run-007 handoff: `RLY-S21-SIDECAR-PROVIDER-HANDOFF-006`
- Governance head: `97e5fe3b1cd0a39873aa63e8f8db091cee29ab57`
- Frozen candidate: `ded3ed03b7070ea095a823129ebe44935cb57997`
- Prior deterministic evaluation: `RLY-S21-EVAL-002 — ACCEPT`

## Live evidence

Run 007 passed the environment and compatibility gates that had blocked prior runs:

- ignored/untracked local credential delivery: PASS;
- wrapper-enforced V2 isolation: PASS;
- protected V1 integrity: PASS;
- exact V2 version/hash: PASS;
- authenticated loopback health: PASS;
- unchanged candidate `OpenCodeRuntime.describe()`: PASS;
- exact fixture binding: PASS;
- programmatic session creation: PASS.

The first execution prompt was then rejected before admission with HTTP 400. Sanitized live runtime evidence reported:

`Missing key at ["text"]`

No provider inference occurred. Fixture, canary, and local bare remote remained unchanged.

Evidence package:
`/tmp/relay-s21-sidecar/evidence-run-007/`

Reported SHA-256 of `SHA256SUMS.txt`:
`18766b9263f473c9969a914cbb1285534f4e4f06b6b99e974d2161d744bac8e1`

## F007-A — BLOCKING — live V2 prompt request schema does not match candidate mapping

The frozen candidate sends the execution prompt as:

```json
{
  "prompt": {
    "text": "<input>",
    "files": [],
    "agents": []
  },
  "resume": false
}
```

to `POST /api/session/{sessionID}/prompt`.

The exact installed OpenCode V2 beta rejected that body at schema validation before admission and reported the missing `text` key.

Therefore the candidate's prompt/input HTTP mapping is not compatible with the exact runtime generation exercised by the authorized sidecar.

This is an adapter implementation defect. It is not an accepted-design defect: S2.1-D20 intentionally keeps OpenCode-native request mapping behind the adapter and requires the supported pinned generation to be proven by live sidecar evidence.

### Required correction

Do not guess the replacement JSON shape from current upstream source alone.

Before changing the deterministic mock, bind the correction to the exact `0.0.0-beta-17823` prompt schema using sanitized sidecar evidence and/or the exact installed beta's non-secret local/generated schema surface.

Then make the smallest change to `OpenCodeRuntime.open_execution()` that emits the exact accepted body for that beta.

No provider call is required to establish request-schema acceptance.

## F007-B — BLOCKING — deterministic mock encoded the same incorrect prompt contract

The current mock server explicitly asserts the candidate's nested `prompt.text` plus `resume` body. Therefore deterministic tests proved internal consistency, not compatibility with the pinned live runtime.

Required correction:

- update the mock to the exact pinned beta prompt schema;
- add an exact-body assertion test;
- add a regression test for a live-style schema rejection;
- preserve observer-before-admission and one-prompt semantics.

## F007-C — BLOCKING — prompt HTTP 400 is misclassified as AGENT_BLOCKED

The live schema rejection is an adapter/request-contract failure, not an agent refusal.

The candidate currently maps every prompt HTTP 400 to `AGENT_BLOCKED`, while its session-creation path already maps HTTP 400 configuration/schema rejection to `CONFIGURATION`.

Required correction:

- do not classify prompt request-schema rejection as `AGENT_BLOCKED`;
- use the accepted failure taxonomy consistently;
- a definite prompt schema/configuration rejection must normalize as `CONFIGURATION` unless the exact pinned runtime exposes a more specific accepted category;
- retain safe non-secret diagnostics only.

## D21 disposition

- D21-01: PASS
- D21-02: PASS
- D21-03: PASS
- D21-04: PASS
- D21-05: FAIL — blocking prompt-schema incompatibility
- D21-06 through D21-13: NOT RUN
- D21-14: NOT APPLICABLE
- D21-15/16: NOT RUN
- D21-17: PASS
- D21-18: NOT RUN

## Classification

```text
Relay candidate implementation defect: ESTABLISHED
accepted Slice 2.1 design defect: NOT ESTABLISHED
live V2 connection compatibility: PASS
session creation compatibility: PASS
prompt admission compatibility: FAIL
provider/model inference: NOT REACHED
D21 gate: INCOMPLETE / BLOCKED
Human technical acceptance: NOT ELIGIBLE
```

## Governance decision

```text
Run 007: STOPPED FAIL-CLOSED
Evaluation: RLY-S21-SIDECAR-EVAL-007 — REWORK
Candidate: PRESERVED
Prior deterministic evaluation: HISTORICAL ACCEPT; superseded for live-acceptance eligibility by this live finding
```

No Human technical acceptance, promotion, Slice closure, Slice 2.2, or Phase 3 authority is issued.
