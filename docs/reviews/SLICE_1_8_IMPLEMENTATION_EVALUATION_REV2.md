# Relay — Slice 1.8 Independent Implementation Evaluation 002

**Document class:** Immutable implementation evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Evaluation ID:** `RLY-S18-EVAL-002`  
**Outcome:** `ACCEPT`  
**Evaluator:** GPT-5.6 Sol

## Exact evaluated subject

```text
Repository: cschrupp/relay
Implementation authority: RLY-S18-IMPL-AUTH-001 — AUTHORIZED
Accepted design baseline: eae25f0837bbce435e54fc3437b502dea1224744
Initial implementation candidate: e81a27384086ffc3c52c8ceac1bbee7c0d0c89fc
Prior evaluation: RLY-S18-EVAL-001 — REWORK
Rework start: a38582ff7e3a19857733d01ca8dfddb85da50259
Evaluated successor candidate: 35046bb378808a1325ecb84eace5aacd3040ca98
Authorized implementation start: a7cd87fea89e3b0273da1d0c0884336cc7857357
Ahead / behind authorized start: 5 / 0
Ahead / behind rework start: 1 / 0
Exact-head CI: 38110149903 — SUCCESS
```

Canonical `main` remained unchanged at `a7cd87fea89e3b0273da1d0c0884336cc7857357` during review.

## Independent verification

```text
bounded rework surface: PASS
rework commit count above a38582ff...: 1
changed files in bounded rework: exactly 3
production/runtime/test/schema/dependency/workflow/settings changes: NONE
accepted design files byte-preserved: PASS
original implementation handoff byte-preserved: PASS
RLY-S18-EVAL-001 byte-preserved: PASS
registry artifact count: 174
registry predecessor/successor links for handoff revisions: PASS
exact-head CI binding: PASS
```

The bounded rework changes only:

```text
.relay/registry.json
docs/references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md
docs/reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF_REV2.md
```

## F001 — RESOLVED

The prior evaluation found an incorrect attribution of `SLSA_BUILD_REPRODUCED` to Revision-1 D03.

The successor correctly binds the external property to the accepted Revision-1 external-reference snapshot, Section 3, and identifies D19/D21 as the applicable mapping/reuse semantics.

Independent inspection confirms:

```text
Revision-1 Section 3:
SLSA_BUILD_REPRODUCED is present

D19:
one-way, requirement-specific SLSA mapping

D21:
faithful SLSA VSA/provenance reuse
```

D03 is no longer represented as the source of the external property.

The mapping remains `UNASSESSED`; no SLSA reproduction result, level, compliance claim, Relay-native synonym, Human acceptance, or promotion authority is inferred.

```text
F001 — RESOLVED / PASS
```

## F002 — RESOLVED

The original handoff traced D62–D65 to Sections 4, 12, and 14 while claiming coverage of D63's exact 17-property vocabulary.

The immutable successor handoff now traces:

```text
D62–D65 -> Sections 4, 5, 12, 14
```

Independent inspection confirms Section 5 is the exact native verified-property section containing the complete accepted D63 vocabulary of exactly 17 Relay-native properties.

Sections 4, 12, and 14 retain the corresponding predicate/projection, external-source, and downstream-ownership coverage.

```text
F002 — RESOLVED / PASS
```

## Historical integrity

The following historical subjects remain byte-identical across the rework:

```text
docs/reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF.md
docs/reviews/SLICE_1_8_IMPLEMENTATION_EVALUATION.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN_REV2_AMENDMENT.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN_REV2_REWORK_1.md
```

The registry preserves the original handoff as `SUPERSEDED` and the successor handoff as `IMMUTABLE`, with reciprocal revision links. The original evaluation remains immutable and bound to the original candidate; it is not reinterpreted as an acceptance.

## CI and quality evidence

GitHub Actions run `38110149903` is independently verified as:

```text
workflow: CI
event: push
branch: implementation/1.8-governance-assurance-reference-model
head_sha: 35046bb378808a1325ecb84eace5aacd3040ca98
status: completed
conclusion: success
```

The quality job completed successfully through environment synchronization, Ruff format, Ruff lint, Pyright, tests, and build.

The successor handoff additionally reports:

```text
43 repository-contract tests — PASS
659 full-suite tests — PASS
uv build — PASS
registry transition/preservation checks — PASS
git diff --check — PASS
```

These checks are engineering evidence, not authority.

## Decision

```text
RLY-S18-EVAL-002 — ACCEPT
```

Candidate:

```text
35046bb378808a1325ecb84eace5aacd3040ca98
```

faithfully resolves F001/F002, remains within `RLY-S18-IMPL-AUTH-001`, preserves the accepted design and historical evidence, and introduces no unauthorized production/runtime/test/schema/dependency change.

No blocking or non-blocking implementation findings remain from this evaluation.

## Governance boundary

```text
Implementation evaluation:
ACCEPT

Human technical acceptance:
PENDING SEPARATE HUMAN DECISION

Canonical promotion:
NOT AUTHORIZED BY THIS EVALUATION

Slice closure:
NOT AUTHORIZED BY THIS EVALUATION

Slice 1.9 / 1.10:
NOT OPENED

Phase 3:
NOT AUTHORIZED
```

**Independent evaluation ACCEPT != Human technical acceptance.**
