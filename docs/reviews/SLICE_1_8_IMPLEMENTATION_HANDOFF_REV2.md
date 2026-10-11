# Slice 1.8 — Implementation Handoff — Revision 2

**Document class:** Immutable implementation evidence on submission
**Status:** REWORK CANDIDATE / AWAITING INDEPENDENT IMPLEMENTATION EVALUATION
**Authority:** `RLY-S18-IMPL-AUTH-001`
**Rework basis:** `RLY-S18-EVAL-001 — REWORK`
**Supersedes:** [Implementation Handoff revision 1](SLICE_1_8_IMPLEMENTATION_HANDOFF.md), preserved byte-for-byte
**Executor:** Codex / GPT-6 family; exact runtime variant not exposed
**Independent evaluator:** GPT-5.6 Sol

## Exact subjects and scope

```text
Repository: cschrupp/relay
Delivery branch: implementation/1.8-governance-assurance-reference-model
Authorized implementation start: a7cd87fea89e3b0273da1d0c0884336cc7857357
Accepted design baseline: eae25f0837bbce435e54fc3437b502dea1224744
Evaluated implementation candidate: e81a27384086ffc3c52c8ceac1bbee7c0d0c89fc
Review-record / rework start: a38582ff7e3a19857733d01ca8dfddb85da50259
```

Revision 1's combined-design basis and implementation descriptions remain applicable except for the explicit traceability correction below. Its test counts, candidate observations, registry count, and file inventory describe the original candidate; they are not new observations of this successor. The immutable evaluation remains bound to the original evaluated candidate and is not reinterpreted as acceptance of the rework.

The rework changes only the mapping attribution, this successor handoff, and the necessary registry identities/digests/supersession links. No current projection or source-catalog fact changes. No architecture, SLSA semantics, property vocabulary, UNASSESSED status, source/runtime/test code, schema, dependency, workflow, repository setting, or downstream capability changes.

## F001 — External-reference attribution correction

The mapping matrix now identifies `SLSA_BUILD_REPRODUCED` in the accepted Revision-1 external-reference snapshot (Section 3), with mapping/reuse semantics governed by D19/D21. D03 remains the reference-plane architecture decision and is no longer attributed as the source of that external property. The row remains UNASSESSED; all other row content is unchanged.

## F002 — Corrected D62–D65 implementation traceability

This row replaces only the D62–D65 row in the original handoff's coverage table:

| Accepted decisions | Materialized content and review location |
|---|---|
| D62–D65 | Sections 4, 5, 12, 14 of the [reference model](../architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md): corrected downstream ownership, exactly 17 properties, projections not new authority predicates, conservative source traceability |

Section 5 contains the D63 vocabulary and definitions. Sections 4, 12, and 14 retain their existing predicate/projection, external-source, and ownership coverage. This correction is implementation traceability, not independent evaluation.

## Registry and preservation

The working mapping artifact advances from revision 1 to 2 with a new ArtifactId and digest. The original immutable handoff retains its exact bytes, identity, digest, and revision; its registry state becomes SUPERSEDED with an explicit reciprocal link to this IMMUTABLE_RECORD/IMMUTABLE revision 2 successor. The evaluation record and all other historical files remain unchanged.

Registry count: 173 -> 174. Build Plan remains 88, Current Baseline remains 98, Product Proposal remains 46; all current projections and canonical pointers are unchanged. Historical mapping revision 1 remains reconstructable at the evaluated candidate through Git.

## Validation and delivery binding

The external delivery report binds this successor's exact commit SHA, changed paths, ancestry, local quality results, and exact-head CI run/result. It must distinguish the original candidate's CI `38109030810` from the new candidate's CI. A post-commit SHA/run cannot be inserted into this same immutable record without changing its subject.

Required checks remain frozen environment synchronization, Ruff format/lint, Pyright, repository-contract tests, the full test suite, build, whitespace checks, registry-transition validation, and exact historical-byte preservation. No test change is authorized or needed.

## Disposition

Return this bounded successor to Sol for a new independent implementation evaluation. No technical acceptance, canonical promotion, closure, Slice 1.9/1.10 opening, or agent execution is claimed or performed.

**STOP FOR SOL INDEPENDENT IMPLEMENTATION REVIEW.**
