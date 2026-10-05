# Phase 1 M0 — Run 002 Implementation Result and Evidence

**Document class:** Immutable result-attachment and evidence record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Result record:** `RLY-P1-M0-RUN-002-RESULT-001`  
**Evidence set:** `RLY-P1-M0-RUN-002-EVIDENCE-001`

## 1. Authority basis

```text
Phase 1 M0 authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

Run:
RLY-P1-M0-RUN-002 — OPEN

Implementation authority:
RLY-P1-M0-RUN-002-IMPL-AUTH-001 — AUTHORIZED
fec580e06848286a919091be5d2fb8b1400f21f3

Implementation handoff:
3cd01142d3c4ec403d33b9f744aec97b66136a32

Frozen product baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Accepted design:
65bda5393fe74ab5c5b1fda03be80b81bbc4fe30

Human design acceptance:
a0671a4fed7be1361727d4cd2f55f0accb1535c9
```

## 2. Human-submitted implementation result

Human Authority supplied the external Codex implementation handoff for:

```text
branch:
implementation/m0-run-002-governance-status-summary

candidate SHA:
cf8aae9d44bfef5019500bac37ae6baf3cdb5235

executor:
Codex

actual model:
GPT-6 family; exact runtime variant not exposed
```

The candidate is attached as the exact engineering result for Run 002. This attachment is not technical acceptance or promotion.

## 3. Independently verified repository provenance

GitHub verification established:

```text
remote implementation branch head:
cf8aae9d44bfef5019500bac37ae6baf3cdb5235

candidate parent:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

compare status:
ahead by exactly 1 commit
behind by 0
merge base:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19
```

Therefore the result is directly based on the exact authorized frozen baseline, with no intervening merge/rebase from later `main`.

## 4. Independently verified change surface

The exact baseline-to-candidate compare contains only:

```text
src/relay_engine/board/render.py
tests/unit/test_board_render.py
```

No dependency, lockfile, governance, lifecycle, persistence, manual-evaluation, repository-contract, repository-sync, model, service, or web-route file changed.

## 5. Implementation evidence submitted by executor

Executor-reported local evidence:

```text
focused board-render tests: 11 passed
ruff format: PASS — 231 files already formatted
ruff lint: PASS
pyright: PASS — 0 errors, 0 warnings
full pytest: 599 passed
build: PASS
git diff --check: PASS
frozen sync: PASS
repository contract/sync tests: PASS within full suite
dependencies/toolchain: UNCHANGED
deviations: NONE
new work discovered: NONE
```

These local command counts are preserved as submitted implementation evidence; independent evaluation additionally verified the exact remote diff and GitHub CI below.

## 6. Independently verified GitHub CI evidence

```text
workflow:
CI

run id:
37378048595

head branch:
implementation/m0-run-002-governance-status-summary

head SHA:
cf8aae9d44bfef5019500bac37ae6baf3cdb5235

status:
completed

conclusion:
success
```

The single `quality` job completed successfully on the exact candidate SHA, including repository-owned steps:

```text
Sync environment       PASS
Ruff format            PASS
Ruff lint              PASS
Pyright                PASS
Tests                   PASS
Build                   PASS
```

## 7. Design-contract evidence

Patch inspection confirms the candidate:

- inserts a read-only `Governance status` section before `Definition`;
- derives the summary only from existing `SliceDetail` projection fields;
- preserves explicit READY-vs-execution-authority wording;
- renders outgoing gates independently;
- renders a current traffic light only for `MATCHING_DURABLE_BASIS`;
- suppresses stale traffic-light claims and labels stale / not-evaluated / not-applicable states explicitly;
- represents current Human authorization grants, approval decisions, choice decisions, and Human holds separately;
- represents missing authorization grants as `none projected` rather than inferring a negative Human decision;
- keeps engineering result, evaluator decision, Human technical decision, and accepted-result promotion as distinct records;
- exposes exact result/accepted commit provenance when already projected;
- summarizes development-memory provenance/counts without persisting new state;
- continues escaping externally influenced fields through the existing `_e(...)` path;
- preserves existing detailed provenance sections.

## 8. Result state

```text
Run 002 exact implementation result:
ATTACHED — RLY-P1-M0-RUN-002-RESULT-001

Candidate:
cf8aae9d44bfef5019500bac37ae6baf3cdb5235

Independent implementation evaluation:
PENDING at the time of this record

Human technical acceptance:
NOT GRANTED

Promotion / merge:
NOT AUTHORIZED

M0 completion:
NOT ACCEPTED

Phase 2:
NOT OPEN
```
