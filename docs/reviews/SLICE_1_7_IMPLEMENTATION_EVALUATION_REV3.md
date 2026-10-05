# Slice 1.7 — Independent Implementation Evaluation, Revision 3

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Record:** `RLY-S17-EVAL-003`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Prior implementation candidates:
38c4cda99164697be562bba610598423d9dbfbb7
c573051229ecb7714e7ff66b4155388ad953c56d

Prior independent evaluations:
RLY-S17-EVAL-001 — REWORK
RLY-S17-EVAL-002 — REWORK

Successor implementation candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Implementation branch:
implementation/1.7-manual-evaluation-acceptance
```

The successor is exactly one commit ahead of `c573051229ecb7714e7ff66b4155388ad953c56d`, which remains its direct parent. The remote implementation branch was independently verified at the exact successor SHA.

The final rework commit changes only:

```text
src/relay_engine/manual_evaluation/service.py
tests/integration/test_manual_evaluation_sqlite.py
```

The final delta is narrowly scoped to the remaining F003 subject-precondition gap. Migration v5, dependency declarations, and the lifecycle transition matrix are unchanged.

## Independent validation evidence

Exact-SHA GitHub Actions run `37266796869` was independently inspected. Its `quality` job checked out:

```text
2fc1a762e17f45fb1a3d866d8100f2c0c284b435
```

and reports:

```text
uv sync --frozen --group dev: PASS
ruff format --check: PASS — 222 files already formatted
ruff check: PASS
pyright: PASS — 0 errors, 0 warnings, 0 informations
pytest: PASS — 592 passed
uv build: PASS
```

The implementation handoff additionally reports `git diff --check` PASS.

The disclosed implementation-model provenance deviation remains Codex / GPT-6 family instead of preferred GPT-5.6 Luna. No new deviation was introduced by this final rework.

# Finding disposition

## F001 — RESOLVED

The prior accepted finding resolution remains intact: exact already-accepted promotion retries reconstruct and validate the durable accepted causal chain and return the existing `AcceptedSliceResult` only for the same durable command identities and subject. No duplicate GateEvaluationRecord, LifecycleEvent, or ExecutionRecord is created. Different promotion identities or different result/evaluation subjects fail closed.

## F002 — RESOLVED

The prior accepted finding resolution remains intact: exact same-result attachment retries return the existing durable `SliceResultRecord` with no additional row. Conflicting reuse fails closed; a genuinely new result identity follows the normal supersession path.

## F003 — RESOLVED

The remaining Revision-2 defect is corrected.

`_exact_technical_decision_retry(...)` now receives the command's explicit:

```text
expected_result_id
expected_manual_evaluation_id
```

and requires them to agree simultaneously with:

```text
the submitted HumanActionBasis subject
current durable SliceResultRecord
current durable ManualEvaluationRecord
the exact successor GateEvaluationRecord subject
```

Therefore an exact durable technical-decision identity/payload can no longer mask contradictory explicit result/evaluation CAS inputs.

Focused integration coverage proves:

```text
exact durable decision retry + matching expected subject -> no-op success
wrong expected_result_id -> ManualEvaluationConflict and zero new writes
wrong expected_manual_evaluation_id -> ManualEvaluationConflict and zero new writes
```

The tests explicitly confirm both Human-decision count and GateEvaluationRecord count remain unchanged for the two conflicting retry shapes.

F003 is resolved.

## F004 — RESOLVED

The prior accepted finding resolution remains intact. The implementation includes an end-to-end governed REWORK-cycle proof covering evaluator REWORK without direct lifecycle movement, RED/YELLOW refusal, GREEN governed `EVALUATING -> REWORK`, governed later `REWORK -> EVALUATING`, preservation of prior result/evaluation history, and explicit successor-result lineage.

# Regression and scope review

No regression or scope expansion was found in the final rework:

- migration v5 remains unchanged;
- no new migration or persistence table was added;
- no dependencies changed;
- lifecycle transition matrix remains unchanged;
- no repository mutation was introduced;
- no agent execution or Phase 2 work was introduced;
- Decision authority inheritance remains intact;
- authored evaluator judgment, Human technical acceptance, and accepted-result promotion remain distinct;
- generic Slice 1.6 `ADVANCE` remains unable to execute an `ACCEPTED` target;
- all prior implementation candidates and REWORK evaluation records remain immutable history.

# Evaluation outcome

```text
RLY-S17-EVAL-003 — ACCEPT
```

Candidate `2fc1a762e17f45fb1a3d866d8100f2c0c284b435` is technically eligible for explicit Human technical acceptance.

This `ACCEPT` is independent implementation evaluation evidence only. It does **not** itself grant Human technical acceptance, authorize finalization/closure, declare the Phase 1 M0 hard stop complete, open Phase 2, or authorize agent execution.
