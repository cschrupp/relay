# Slice 1.5 — Finalization Execution Handoff

**Status:** WORKING HANDOFF — governed by `RLY-S15-CLOSE-AUTH-001`  
**Date:** 2026-10-03  
**Slice:** 1.5 — Board Projection

## Exact starting authority

```text
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED
Finalization authority commit:
2c012905fab8179874143eeaf3089527ea92dd53

Accepted technical candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT
Evaluation commit:
ea26e0ae717e873e4b3ded27f1a8e9b0b278d7be

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED
Acceptance commit:
1f0c6991268440982eef8b6d0f8b5abcdd4616f4

Canonical main before reconciliation:
2789b248085d7772abed80448f8b6bc1ce6de483
```

## Execution objective

Produce one closure-ready canonical candidate that preserves both legitimate histories:

1. canonical `main`, which contains the separately recorded implementation authorization lineage; and
2. the accepted implementation/evaluation/acceptance lineage ending at this finalization authority.

Do not rebase, squash, cherry-pick away, or otherwise rewrite either provenance chain.

## Required sequence

1. Fetch both `main` and `acceptance/1.5-board-projection`.
2. Verify exact heads before mutation.
3. Create/use `finalization/1.5-board-projection` from finalization authority commit `2c012905...`.
4. Reconcile `main` into the finalization lineage using a provenance-preserving merge/reconciliation. Resolve only documentation/registry conflicts; product code from accepted candidate `ff8df665...` must remain byte-identical.
5. Ensure canonical history contains `docs/reviews/SLICE_1_5_IMPLEMENTATION_AUTHORIZATION.md` from `main` plus the independent evaluation, Human acceptance, and finalization authority records.
6. Update only bounded finalization documents/state:
   - `docs/CURRENT_BASELINE.md`
   - `docs/BUILD_PLAN_V0_5.md`
   - `docs/PRODUCT_PROPOSAL_V0_5.md`
   - `.relay/registry.json`
   - optional bounded Slice 1.5 memory/evidence record if repository convention requires it.
7. Before closure evaluation, living projections should truthfully describe Slice 1.5 as technically accepted and closure-ready/finalization-authorized, not prematurely closed.
8. Advance each changed living projection by exactly one registry revision from the prior canonical `main` registry, with a new ArtifactId and exact digest; advance canonical pointers accordingly.
9. Register missing Slice 1.5 accepted records needed for complete provenance. Do not mutate existing registered immutable or locked records.
10. Run registry transition validation from the prior canonical registry to the proposed registry.
11. Run the complete quality suite and obtain successful GitHub Actions CI on the exact closure-ready SHA.
12. Submit that exact SHA to an independent closure evaluator for `ACCEPT / REWORK / ESCALATE`.
13. Only after closure-evaluation `ACCEPT`, record `RLY-S15-CLOSE-EVAL-001`, advance living projections to `COMPLETE / ACCEPTED / CLOSED`, validate registry again, rerun exact-SHA CI if the closure record/projections change the candidate, and promote the final canonical closure head to `main`.

## Product-code immutability check

The finalizer must prove that the accepted product implementation remains unchanged relative to `ff8df665...` for:

```text
pyproject.toml
uv.lock
src/relay_engine/board/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
src/relay_engine/persistence/__init__.py
src/relay_engine/persistence/database.py
src/relay_engine/persistence/store.py
tests/unit/test_board_models.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_web.py
tests/integration/test_board_projection_sqlite.py
```

Changes to those files are a hard stop unless they are solely caused by a proven merge artifact that can be resolved back to the exact accepted bytes.

## Required finalization evidence

Report:

```text
starting main SHA
starting accepted/finalization SHA
merge/reconciliation SHA
closure-ready SHA
changed-file list after accepted candidate
registry transition result
living-projection old/new revisions and ArtifactIds
local quality results
GitHub Actions run ID and exact head SHA
product-code byte-equivalence result versus ff8df665...
any deviations
```

## Hard stops

Stop and escalate if:

- exact heads differ from the values above before reconciliation;
- accepted product bytes cannot be preserved;
- registry transition requires mutating historical immutable/locked records;
- living-projection revision history cannot be advanced monotonically;
- CI fails for a reason not confined to bounded finalization bookkeeping;
- Slice 1.6 or new product behavior becomes necessary;
- any scope beyond `RLY-S15-CLOSE-AUTH-001` is required.

**Unblocked ≠ closed.**
