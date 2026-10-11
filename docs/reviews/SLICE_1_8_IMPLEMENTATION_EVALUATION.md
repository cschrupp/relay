# Relay — Slice 1.8 Independent Implementation Evaluation 001

**Document class:** Immutable implementation evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-10  
**Evaluation ID:** `RLY-S18-EVAL-001`  
**Outcome:** `REWORK`  
**Evaluator:** GPT-5.6 Sol

## Exact evaluated subject

```text
Repository: cschrupp/relay
Implementation authority: RLY-S18-IMPL-AUTH-001 — AUTHORIZED
Authorized implementation start: a7cd87fea89e3b0273da1d0c0884336cc7857357
Accepted design baseline: eae25f0837bbce435e54fc3437b502dea1224744
Implementation candidate: e81a27384086ffc3c52c8ceac1bbee7c0d0c89fc
Merge base: a7cd87fea89e3b0273da1d0c0884336cc7857357
ahead / behind: 1 / 0
Exact-head CI: 38109030810 — SUCCESS
```

Canonical main remained unchanged at the authorized implementation start during review.

## Independent verification

```text
documentation-only scope: PASS
production/runtime/test/schema/dependency/workflow/settings changes: NONE
163 starting LOCKABLE_RECORD / IMMUTABLE_RECORD artifacts preserved exactly: PASS
accepted design files byte-preserved: PASS
Build Plan 87 -> 88: PASS
Current Baseline 97 -> 98: PASS
Product Proposal 46 -> 46: PASS under explicit implementation constraint
registry transition: PASS
exact accepted 17-property vocabulary: PASS
worked examples E01-E20: PASS
negative cases N01-N30: PASS
required source IDs present: PASS
Slice ownership 1.9/1.10: PASS
exact-head CI: PASS
```

The recorded Codex/GPT-6-family executor provenance deviation does not widen authority. Product Proposal r46's disclosed stale status wording is not a finding because the implementation authority explicitly constrained that projection to 46 -> 46.

## F001 — Incorrect SLSA_BUILD_REPRODUCED design traceability

**Outcome:** REWORK

`docs/references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md` states:

```text
SLSA_BUILD_REPRODUCED from accepted Revision 1 D03
```

Revision 1 D03 is the reference-plane architecture decision. `SLSA_BUILD_REPRODUCED` appears in the accepted Revision-1 external-reference snapshot; faithful SLSA mapping/reuse semantics are governed by D19/D21.

Required bounded correction: remove the D03 attribution and bind the row to the accepted external-reference snapshot plus D19/D21, or equivalent exact wording. Preserve its UNASSESSED status and external semantics.

## F002 — Handoff D62-D65 traceability omits Section 5

**Outcome:** REWORK

`docs/reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF.md` maps D62-D65 to Sections 4, 12, 14 while claiming coverage of the exact 17-property vocabulary. D63 is materialized in Section 5.

Required bounded correction:

```text
D62-D65 -> Sections 4, 5, 12, 14
```

or equivalent exact traceability that explicitly includes Section 5.

## Rework boundary

This is documentation-traceability rework only. No architecture redesign or new Human Authority is required.

Authorized rework surface:

```text
docs/references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md
docs/reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF.md
.relay/registry.json
```

If repository artifact-governance rules require a successor handoff artifact instead of editing the submitted immutable handoff, preserve the original and create the required successor. Preserve this evaluation record.

Do not modify production source, tests, schema, dependencies, workflows, accepted design records, Human authority records, source-catalog facts, or current projections.

## Decision

```text
RLY-S18-EVAL-001 — REWORK
```

The candidate is not eligible for Human technical acceptance until a bounded successor corrects F001/F002, exact-head CI succeeds, and Sol performs a new independent implementation evaluation.
