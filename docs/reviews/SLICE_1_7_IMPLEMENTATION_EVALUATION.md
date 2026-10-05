# Slice 1.7 — Independent Implementation Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Record:** `RLY-S17-EVAL-001`  
**Outcome:** `REWORK`

## Evaluated subject

```text
Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Exact accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Implementation candidate:
38c4cda99164697be562bba610598423d9dbfbb7

Implementation branch:
implementation/1.7-manual-evaluation-acceptance
```

The candidate is exactly one commit ahead of the authorized baseline. The remote implementation branch was verified at the exact candidate SHA.

## Independent evidence reviewed

The evaluator independently inspected:

- the baseline-to-candidate commit comparison and exact changed-file surface;
- the accepted Revision 1 + Revision 2 + Revision 3 + Revision 4 design, with `R4 > R3 > R2 > R1` precedence;
- `RLY-S17-AUTH-001` and its explicit v5 migration authority;
- the new manual-evaluation application service and models;
- Human Action Basis integration;
- `HandoverContext` compatibility semantics;
- Slice 1.7 persistence and migration code;
- accepted-result promotion and causal reconstruction;
- board/FastAPI integration;
- Slice 1.7 integration tests;
- exact-SHA GitHub Actions run `37245459142`.

Exact-SHA CI independently confirms:

```text
checkout:
38c4cda99164697be562bba610598423d9dbfbb7

uv sync --frozen --group dev:
PASS

ruff format --check:
PASS — 222 files already formatted

ruff check:
PASS

pyright:
PASS — 0 errors, 0 warnings, 0 informations

pytest:
PASS — 589 passed

build:
PASS
```

The implementation handoff additionally reports `git diff --check` PASS.

## Accepted implementation characteristics

The following parts of the candidate are technically sound and do not require redesign:

- migration v5 is bounded to the authorized `slice_results` and `manual_evaluations` tables plus required indexes/append-only triggers;
- no v6 or third table is introduced;
- no runtime/dev/test dependency was added;
- the lifecycle transition matrix remains unchanged;
- result Baselines inherit and revalidate the exact source Baseline Decision set;
- authored `ManualEvaluationRecord` remains distinct from deterministic `GateEvaluationRecord`;
- Evidence creation, authored evaluation, and successor gate observation are transactional;
- pending result identity invalidates stale Slice 1.6 gate-affecting Human Action Basis state;
- historical pre-1.7 `HandoverContext.evaluation_outcome` remains backward-compatible;
- generic Slice 1.6 `ADVANCE` still refuses `ACCEPTED`, preventing an AUTO gate from bypassing Slice 1.7 technical acceptance;
- promotion revalidates exact evaluator `ACCEPT`, current Human `APPROVE`, Decision authority, deterministic complete-gate truth, and uses the accepted governed execution path;
- accepted-result reconstruction is causal rather than a mutable accepted-baseline pointer;
- development memory remains a derived durable-state projection without repository mutation.

These findings establish that the rework is bounded to the issues below.

# Findings

## F001 — BLOCKING — Exact already-accepted promotion retry is not idempotent

The accepted Revision 1 idempotency contract requires:

```text
promote exact same already-ACCEPTED result/evaluation
    -> return existing accepted projection, no second execution
```

and the required test contract explicitly requires:

```text
retry of exact already-accepted subject creates no duplicate execution
different-subject retry conflicts
```

The candidate instead begins `promote_accepted_result(...)` by rejecting any Slice whose lifecycle is already `ACCEPTED`:

```text
if lifecycle is not None and lifecycle.phase is LifecyclePhase.ACCEPTED:
    raise ManualEvaluationConflict(...)
```

Therefore even an exact target-state retry using the same durable result/evaluation/promotion identities cannot return the already-established accepted projection.

This is not only an HTTP convenience issue. A client may lose the successful `303` response after the transaction commits. Relay must be able to distinguish an exact replay of the already-committed promotion from a conflicting second command without creating another execution.

### Required correction

Before rejecting the already-`ACCEPTED` state, reconstruct the accepted causal chain and permit no-op success only when the submitted command identifies the exact already-established promotion, including the exact result/evaluation and the durable promotion identities needed to prove it is the same command. Return the existing `AcceptedSliceResult` and create no new GateEvaluationRecord, LifecycleEvent, or ExecutionRecord.

A changed durable identity or different result/evaluation subject must remain a conflict.

Add explicit tests for both exact retry success and different-identity/subject conflict.

## F002 — MAJOR — Exact same-result attachment retry is not idempotent

Revision 1 D35 and the required test contract require:

```text
attach exact same result with exact same current basis and matching durable result record
    -> no-op success

same-result retry idempotent
```

`attach_result(...)` has no target-state retry branch for an already-durable exact `SliceResultRecord`.

After the first successful attachment, replaying the original command encounters a changed current-result CAS and fails stale; if the caller instead supplies the now-current result as the expected current result, the function proceeds toward appending a successor and can attempt to reuse the same `result_id`, rather than recognizing the exact existing durable result as the target state.

### Required correction

Add exact target-state idempotency before any successor append:

- if the supplied `result_id` already identifies the current durable result and the complete typed result identity/provenance matches the command and verified Baseline, return that existing record with no new `SliceResultRecord`;
- do not create self-supersession;
- the same durable ID with conflicting content/provenance must fail conflict/integrity;
- a genuinely new result ID remains a distinct result command and follows the existing CAS/supersession rules.

Add the mandatory same-result retry test.

## F003 — MAJOR — Technical decision no-op predicate ignores durable decision identity/payload

Revision 1 D35 states that technical accept/reject may be a no-op when the **exact same decision identity/payload** is already current, and further states:

```text
A request with a new durable identity is not treated as the same retry merely because text fields happen to match.
```

The candidate's `_record_technical_decision(...)` returns the latest observation whenever the current decision has the same `APPROVE`/`REJECT` value and same gate/lifecycle/governance basis. That no-op predicate does not require the submitted `decision_id` to equal the durable current decision ID and does not prove byte-equivalent typed payload/provenance.

Consequently a command carrying a new Human decision identity can be silently swallowed as though it were an exact retry.

### Required correction

Make target-state no-op semantics identity-exact:

- no-op only when the submitted durable `decision_id` identifies the exact already-current `HumanApprovalDecision` and its full typed payload/provenance matches;
- a new durable identity must not be silently reclassified as an old retry;
- preserve existing current-decision CAS and staleness rules.

Add tests proving exact-identity retry no-op and new-identity non-equivalence.

## F004 — MAJOR — Mandatory Slice 1.7 REWORK-cycle proof is absent

The accepted Revision 1 required-test contract explicitly requires the Slice 1.7 implementation to prove:

```text
REWORK outcome alone does not move lifecycle
REWORK-target gate must exist
RED/YELLOW cannot execute
GREEN governed EVALUATING->REWORK works through existing path
prior result/evaluation immutable after rework
new result requires later EVALUATING attempt
```

The new Slice 1.7 integration suite contains no `EvaluationOutcome.REWORK` / Slice 1.7 REWORK-cycle test. Existing generic lifecycle/governance tests do not prove the new result/evaluation subject projection across `EVALUATING -> REWORK -> EVALUATING`, nor the required successor-result lineage after re-entry.

The source architecture appears compatible with the intended path, so this is not presently assessed as an architectural defect. It is nevertheless a required acceptance proof for a core Slice 1.7 exit path.

### Required correction

Add an end-to-end integration test proving:

1. authored `ManualEvaluationRecord(REWORK)` does not itself move lifecycle;
2. the correct REWORK-target gate becomes executable only when deterministically GREEN;
3. existing governed advancement performs `EVALUATING -> REWORK`;
4. the result/evaluation remain immutable historical records while in REWORK;
5. existing governed advancement returns `REWORK -> EVALUATING` at a later lifecycle revision;
6. a new result can then supersede the prior result and the full lineage remains reconstructable;
7. no result replacement is possible while still in the evaluated original EVALUATING attempt.

# Non-blocking provenance observations

## Implementation model deviation

Requested executor/model was GPT-5.6 Luna. The implementation handoff reports Codex / GPT-6 family, exact variant not exposed. This is a provenance deviation, not a technical blocker.

## Pyright configuration adjustment

`pyproject.toml` adds only the local Pyright virtual-environment location (`venvPath` / `venv`) required for the mandated `uv run pyright` command to resolve the repository's standard `.venv`. No package declaration, lockfile, tool version, runtime dependency, or dev/test dependency changed. The exact-SHA CI run passes Pyright cleanly. This is accepted as a bounded tooling-configuration deviation and does not independently require rework.

# Evaluation outcome

```text
RLY-S17-EVAL-001 — REWORK
```

The candidate is **not technically eligible for Human acceptance yet** because F001 is blocking and F002–F004 are material accepted-contract gaps.

The rework is bounded. Do not redesign Slice 1.7, add another migration, add dependencies, alter lifecycle transitions, or expand product scope.

A successor candidate must preserve `38c4cda99164697be562bba610598423d9dbfbb7` as evaluated history and address only the findings above plus mechanically necessary tests/code adjustments.

This evaluation does not grant Human technical acceptance, finalization/closure authority, Phase 1 M0 completion, Phase 2 opening, or agent-execution authority.
