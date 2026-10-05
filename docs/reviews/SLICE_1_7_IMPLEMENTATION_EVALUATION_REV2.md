# Slice 1.7 — Independent Implementation Evaluation, Revision 2

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Record:** `RLY-S17-EVAL-002`  
**Outcome:** `REWORK`

## Evaluated subject

```text
Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Prior implementation candidate:
38c4cda99164697be562bba610598423d9dbfbb7

Prior independent evaluation:
RLY-S17-EVAL-001 — REWORK

Prior evaluation-record commit:
fbb56dcf9329162c3c5e796cf93ca6b101110237

Successor implementation candidate:
c573051229ecb7714e7ff66b4155388ad953c56d

Implementation branch:
implementation/1.7-manual-evaluation-acceptance
```

The successor is exactly one commit ahead of the prior evaluated candidate and preserves that candidate as its direct parent. The remote implementation branch was independently verified at the exact successor SHA.

The candidate changes only:

```text
src/relay_engine/manual_evaluation/service.py
tests/integration/test_manual_evaluation_sqlite.py
```

Migration v5, dependency declarations, and the lifecycle transition matrix are unchanged.

## Independent validation evidence

Exact-SHA GitHub Actions run `37262139290` was independently inspected. Its `quality` job checked out:

```text
c573051229ecb7714e7ff66b4155388ad953c56d
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

The disclosed executor remains Codex / GPT-6 family rather than preferred GPT-5.6 Luna. This remains a non-blocking provenance deviation.

# Prior findings

## F001 — RESOLVED — Exact already-accepted promotion retry

The successor introduces explicit reconstruction of the already-accepted causal chain before target-state no-op success.

The retry path validates the exact submitted pre-promotion Human Action Basis against its durable predecessor GateEvaluationRecord and requires the exact promotion GateEvaluationRecord, accepted ExecutionRecord, ACCEPTED lifecycle event, result, manual evaluation, Human approval decision, gate identity/revision, actor, reason, and timestamps.

It returns the existing `AcceptedSliceResult` only when those durable identities match and performs no new execution, lifecycle event, or gate-evaluation write.

Integration coverage proves:

```text
exact retry -> same AcceptedSliceResult and unchanged durable counts
new promotion identities -> conflict
different manual-evaluation subject -> conflict
different result subject -> conflict
```

F001 is resolved.

## F002 — RESOLVED — Exact same-result attachment retry

`attach_result(...)` now recognizes an already-durable `result_id` before attempting a successor append.

No-op success requires the durable record to remain the current result and to equal the reconstructed command record, including Slice/definition/lifecycle/source/result Baseline/supersession/actor/time/reason provenance. Exact commit selectors are checked against the existing immutable result Baseline.

Conflicting reuse of the same result identity fails closed, while a genuinely new result identity follows the existing supersession path.

Integration coverage verifies no row-count increase for exact retry and explicit lineage for a new result identity.

F002 is resolved.

## F003 — PARTIALLY RESOLVED / REWORK REQUIRED — Technical-decision retry still ignores explicit expected subject IDs

The original F003 defect is substantially corrected:

- semantic equality alone is no longer enough for no-op success;
- the submitted `decision_id` must already identify the durable current `HumanApprovalDecision`;
- the full typed durable decision payload is compared;
- the submitted prior Human Action Basis must exactly identify the predecessor observation;
- the exact successor GateEvaluationRecord must exist, be adjacent, remain latest, and deterministically match the projected decision state;
- a new decision ID is treated as a distinct command rather than silently swallowed;
- conflicting reuse of an existing decision ID is rejected.

However, the exact-retry branch is entered **before** the normal technical-decision subject validation and does not pass or validate:

```text
expected_result_id
expected_manual_evaluation_id
```

These are mandatory command preconditions in the accepted Slice 1.7 design. Technical accept/reject carries:

```text
HumanActionBasis
expected result ID
expected manual evaluation ID
exact ACCEPTED gate/revision
```

and the accepted staleness rule requires any mismatch to fail closed as stale/conflict.

Current behavior permits this contradictory request shape:

```text
same exact durable decision_id/payload
same exact original HumanActionBasis
same exact successor GateEvaluationRecord identity/time
BUT
wrong expected_result_id and/or wrong expected_manual_evaluation_id
```

Because an existing decision identity is found first, `_exact_technical_decision_retry(...)` validates the durable subject against the submitted `basis` but never sees the contradictory explicit expected subject arguments. It can therefore return the existing GateEvaluationRecord as no-op success.

That means the retry is not yet an exact replay of the full accepted command contract.

### Required bounded correction

Keep the current identity-exact retry implementation, but include the explicit subject preconditions in the retry proof.

Before returning no-op success, require:

```text
expected_result_id == basis.current_result_id
expected_manual_evaluation_id == basis.current_manual_evaluation_id
```

and require those identities to equal the exact durable current result/evaluation and the successor observation subject already being validated.

A mismatch must fail closed as `ManualEvaluationConflict` or the existing appropriate stale/conflict error and must perform zero writes.

Add focused tests proving:

```text
exact technical-decision retry with matching expected result/evaluation -> no-op
same durable decision retry + wrong expected_result_id -> conflict, zero writes
same durable decision retry + wrong expected_manual_evaluation_id -> conflict, zero writes
```

No redesign or schema change is required.

F003 is therefore not yet fully resolved.

## F004 — RESOLVED — Mandatory Slice 1.7 REWORK-cycle proof

The successor adds an end-to-end REWORK-cycle integration test covering the accepted required path.

It proves:

```text
ManualEvaluationRecord(REWORK) does not itself move lifecycle
RED REWORK gate cannot execute
YELLOW REWORK gate cannot execute
Human approval resolves the required authority
GREEN REWORK gate executes via existing governed advancement
EVALUATING -> REWORK is recorded through the existing handover path
prior result and evaluation history remains immutable
REWORK -> EVALUATING occurs through the existing governed handover path at a later revision
a new result can then be attached
new result explicitly supersedes the prior result
result/evaluation lineage remains reconstructable in development memory
an evaluated result cannot be replaced in its original EVALUATING attempt
```

F004 is resolved.

# Regression and scope review

No regression was found in the previously accepted Slice 1.7 architecture:

- migration v5 remains unchanged;
- no new persistence table or migration was added;
- no dependencies changed;
- no lifecycle transition-matrix change occurred;
- no repository mutation was introduced;
- no agent execution or Phase 2 work was introduced;
- Decision authority inheritance remains intact;
- evaluator judgment, Human technical acceptance, and accepted-result promotion remain distinct;
- generic Slice 1.6 `ADVANCE` remains unable to execute an ACCEPTED target.

# Evaluation outcome

```text
RLY-S17-EVAL-002 — REWORK
```

The successor candidate is not yet technically eligible for Human acceptance because the explicit result/evaluation CAS identities can still be ignored on the technical-decision idempotent retry path.

The required correction is narrow and remains within `RLY-S17-AUTH-001`. No reauthorization, redesign, migration, dependency change, or lifecycle change is required.

Preserve both prior candidates and both immutable evaluation records. A successor candidate should address only the remaining F003 subject-precondition gap plus mechanically necessary tests.

This evaluation does not grant Human technical acceptance, finalization/closure authority, Phase 1 M0 completion, Phase 2 opening, or agent-execution authority.
