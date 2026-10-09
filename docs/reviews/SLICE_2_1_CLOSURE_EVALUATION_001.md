# Slice 2.1 — Independent Closure Evaluation

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-09  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Evaluation ID:** `RLY-S21-CLOSE-EVAL-001`  
**Outcome:** `REWORK`

## Subject

```text
Closure authority:
RLY-S21-CLOSE-AUTH-001 — AUTHORIZED

Prior canonical main:
a9f6742c9f8af0b2f089f16fdeb3111ca34af793

Accepted technical candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Closure-ready candidate:
7f736d3ec3384f69f0aeb9724ffff58921f83b64

Finalization branch:
finalization/2.1-agent-runtime-contract

Reconciliation merge:
5b8f8f8ad8973dd20944234debf1048aa028500d

Finalization authority/handoff commit:
ec59b589360fb9a02b5ab7cf9712fb9030f5a2ed

Exact-head CI:
37976979525 — SUCCESS
```

## Decision

`REWORK`

The evaluated result preserves the accepted implementation and ancestry, and its registry, validation, technical quality, live evidence, and exact-head CI are sound. Rework is limited to two living canonical projections whose current wording contradicts the authorized and accepted state. No product implementation rework is required.

## Verified passing evidence

Both the canonical basis `a9f6742c9f8af0b2f089f16fdeb3111ca34af793` and accepted candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49` are ancestors of `7f736d3ec3384f69f0aeb9724ffff58921f83b64`. The reconciliation is ancestry-preserving. All eleven accepted implementation paths are byte-identical to the accepted candidate, and none changed between the candidate and closure-ready result.

Finalization scope is limited to the accepted implementation lineage and the authorized governance records/projections. The registry contains 141 registered artifacts; registered digests, canonical pointers, the registry transition from the prior canonical state, and repository-contract tests passed. The reported frozen quality suite passed: sync, Ruff format, Ruff lint, Pyright, pytest (659 passed), build, repository-contract tests, and working-tree `git diff --check`. GitHub Actions run `37976979525` succeeded.

## Findings

### F001 — REWORK — Build Plan contradicts current closure authority

`docs/BUILD_PLAN_V0_6.md` records `RLY-S21-CLOSE-AUTH-001 — AUTHORIZED` and the pending independent evaluation, but elsewhere states “Finalization and closure remain unauthorized.” This stale statement contradicts the current authority.

Correct the living projection to state that finalization authority is authorized, `RLY-S21-CLOSE-EVAL-001` returned `REWORK`, Slice 2.1 remains open, and closure has not been accepted.

### F002 — REWORK — Current Baseline and Build Plan retain stale pre-Run-012r3 narrative

Both living projections describe Human technical acceptance as pending the live sidecar evidence gate and instruct the reader not to execute Run 012r3. Run 012r3 has completed, received independent `RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT`, and the candidate received Human technical acceptance `RLY-S21-ACCEPT-001 — ACCEPTED`.

Rewrite the affected passages as historical chronology or completed-state facts. Do not alter immutable historical records.

### O001 — NON-BLOCKING — Markdown hard-break whitespace

The supplemental historical range check reports trailing spaces used for Markdown hard breaks in the immutable authority and handoff records. The required working-state `git diff --check` passed. This is non-blocking; the immutable records must remain byte-for-byte unchanged.

## Corrective boundary

The existing `RLY-S21-CLOSE-AUTH-001` remains sufficient. Correct only the living Current Baseline and Build Plan and their registry successors, and register this evaluation. Product Proposal remains at revision 37. Do not alter accepted implementation paths, immutable/locked records, runtime behavior, provider/model configuration, or perform new live execution.

The corrected projections must state:

```text
Slice 2.1:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Human technical acceptance:
RLY-S21-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S21-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S21-CLOSE-EVAL-001 — REWORK

Corrective closure-ready evaluation:
PENDING

Slice 2.2:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Expected changed projection revisions are Build Plan `77 → 78` and Current Baseline `87 → 88`. Product Proposal remains revision 37. Revalidate ancestry, all eleven implementation-path bytes, immutable-record integrity, registry transition/digests/pointers, repository-contract tests, full frozen quality suite, `git diff --check`, and exact-head CI. No closure acceptance or promotion is authorized by this evaluation.

## Governance disposition

```text
Accepted implementation:
UNCHANGED

Human technical acceptance:
RLY-S21-ACCEPT-001 — ACCEPTED / UNCHANGED

Implementation rework:
NOT REQUIRED

Live sidecar re-evidence:
NOT REQUIRED

Finalization documentation rework:
REQUIRED

Slice 2.1:
OPEN

Closure:
NOT ACCEPTED

Promotion to main:
NOT AUTHORIZED

Slice 2.2:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```
