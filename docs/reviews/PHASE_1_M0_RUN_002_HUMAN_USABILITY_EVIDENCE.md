# Phase 1 M0 — Run 002 Human Usability Evidence

**Document class:** Immutable Human usability evidence  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-P1-M0-RUN-002-USABILITY-001`

## 1. Evaluation basis

Run 002 engineering loop was finalized against canonical Relay main:

```text
cf8aae9d44bfef5019500bac37ae6baf3cdb5235
```

A disposable local SQLite demonstration database was created through Relay's accepted persistence/service APIs. The Human inspected the real Relay board and Slice-detail UI using two representative states:

- Slice A: READY with a current YELLOW gate requiring Human authorization and no authorization grant.
- Slice B: ACCEPTED with durable result, manual evaluation, Human technical acceptance, accepted-result promotion, and development-memory history.

No canonical project/governance state was mutated by this usability exercise.

## 2. Human usability judgment

The Human judged the experiment successful and explicitly approved M0.

The Human's substantive observations were:

- Relay is moving in the right direction.
- The information exposed by the board is useful for tracking project state.
- There is substantial room for improvement in the presentation.
- UI/UX best practices are not yet adequately reflected.
- The amount of information shown by default is too high to be maximally helpful.
- Significant product work remains before Relay becomes a genuinely usable project-management board.

## 3. Observed strengths

The Human walkthrough confirmed that the UI can communicate important governance distinctions, especially:

- lifecycle state versus execution authority;
- READY versus AUTHORIZED;
- current gate evaluation and Human-action requirement;
- Human technical acceptance and accepted-result promotion;
- exact accepted commit provenance;
- persistent development-memory history.

The READY-but-not-authorized demonstration made the distinction operationally meaningful rather than merely conceptual.

## 4. Observed usability deficiencies

The walkthrough exposed non-blocking but material product findings:

1. The default Slice-detail page is information-dense and mixes operator workflow, audit provenance, and raw diagnostic state at equal visual priority.
2. Large raw structures such as the full `HandoverContext` are useful for audit/debugging but are too prominent for normal project-management use.
3. Lifecycle, gate, authority, and provenance information is repeated across the summary and detailed sections.
4. The compact accepted-state summary does not surface all provenance layers as clearly as intended after promotion; in the demonstration, the accepted-result chain remained reconstructible, but some current-result/evaluator information required looking below the compact summary.
5. Development memory is valuable, but counts alone are not yet enough to make the history maximally useful without drilling down.
6. The board is functional as a governed engineering control plane, but not yet polished as a project-management UX.

## 5. Human conclusion

```text
M0 experiment:
APPROVED

Overall product direction:
POSITIVE

Would use the board:
YES, WITH CHANGES

Primary follow-on theme:
UI / UX simplification and operator-first information hierarchy
```

This evidence approves the M0 experiment only. It does not by itself declare Phase 1 complete, open Phase 2, or authorize Relay agent execution.
