# Relay — Slice 3.1 Coding Agent Execution — Independent Implementation Evaluation 002

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE / REWORK — NARROW  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Evaluation ID:** `RLY-S31-IMPL-EVAL-002 — REWORK / NARROW`  
**Evaluator:** Independent Implementation Reviewer — GPT-5.6 Sol  
**Exact corrective implementation subject:** `4a060a12a72d80d69138118e7194e61d4bb99542`  
**Corrective parent:** `7977475ee2f5c98dd840b4a228493f58f6c61308`  
**Prior evaluation:** `RLY-S31-IMPL-EVAL-001 — REWORK / NARROW`  
**Implementation authority:** `RLY-S31-IMPL-AUTH-001 — AUTHORIZED`  
**Implementation handoff:** `RLY-S31-IMPL-HANDOFF-001`  
**Accepted design:** `a28a9b88ddd85cd1a32932b30c4e0e668f23b557`  
**Exact-head CI:** `40262364177 — SUCCESS`

## 1. Decision

```text
RLY-S31-IMPL-EVAL-002 — REWORK / NARROW
```

The A17 corrective implementation closes the blocking evaluator-REWORK lineage finding from `RLY-S31-IMPL-EVAL-001`.

One separate exact-contract defect remains in Slice 3.1 reservation identity handling:

`ConsumableRef` identity is `(consumable_key, scope_key)`, but Slice 3.1 canonicalizes and compares reservation identity by `consumable_key` alone in both the base `ExecutionSubject` and the new `CorrectiveSubjectBinding`.

This is a narrow package-local correctness defect. No predecessor reopening or new Human implementation authority is required.

## 2. Exact lineage and corrective scope

PASS.

The corrective candidate:

`4a060a12a72d80d69138118e7194e61d4bb99542`

is exactly one commit ahead of:

`7977475ee2f5c98dd840b4a228493f58f6c61308`

which is the immutable `RLY-S31-IMPL-EVAL-001` record and a direct descendant of the originally reviewed implementation candidate.

The corrective increment changes only:

```text
src/relay_engine/coding_execution/__init__.py
src/relay_engine/coding_execution/coordinator.py
src/relay_engine/coding_execution/evaluation.py
src/relay_engine/coding_execution/models.py
tests/unit/test_coding_execution_evaluation.py
tests/unit/test_coding_execution_scenarios.py
```

No predecessor Slice implementation file changed.

Canonical `main` remains unchanged at:

`26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f`.

Remote implementation branch matches the exact corrective candidate.

## 3. Validation

PASS.

Exact-head CI:

`40262364177 — SUCCESS`

Observed CI steps all passed:

- frozen environment synchronization;
- Ruff format;
- Ruff lint;
- Pyright;
- tests;
- build.

Executor-reported local validation:

```text
focused Slice 3.1 tests:
49 passed

full pytest:
1,193 passed

uv build:
PASS

git diff --check:
PASS

working tree:
CLEAN
```

No live runtime, provider, model, external-service, project-credential, or real-project execution occurred.

## 4. Prior finding I31-F001 — CLOSED

Prior finding:

A17 lacked a typed independent-evaluator REWORK return path linking the exact reviewed candidate, evaluation record, finding IDs, corrective scope, new attempt identity, and applicable fresh grant/reservation.

Corrective result: PASS.

The candidate now implements:

- `EvaluatorReworkBinding`;
- `PriorExecutionBinding`;
- `CorrectiveSubjectBinding`;
- `ReworkDisposition`;
- `EvaluatorReworkEvaluation`;
- `evaluate_evaluator_rework(...)`;
- `evaluate_corrective_subject_binding(...)`;
- terminal candidate/result digest helpers;
- propagation of `CorrectiveSubjectBinding` into the next `ExecutionSubject`.

The pure evaluator returns exactly the required non-lifecycle classification:

```text
IN_SCOPE_REWORK
NEW_AUTHORITY_REQUIRED
INDETERMINATE
```

and does not issue a grant, reserve a resource, create a WorkPacket, create a runtime session, or admit a prompt.

### A17 exact lineage

PASS.

The in-scope corrective binding preserves:

- prior authority-candidate digest;
- prior terminal change-set candidate digest;
- prior terminal-result digest;
- prior evaluator-handoff digest;
- prior WorkPacketRef;
- independent evaluation record identity/digest;
- exact finding IDs;
- exact corrective scope;
- new corrective authority-candidate digest;
- new intended attempt identity;
- new ExecutionId;
- exact fresh grant;
- applicable fresh reservation evidence.

The binding is carried into the next `ExecutionSubject`, and pre-runtime admission validates it against:

- the exact corrective candidate;
- exact intended attempt / ExecutionId;
- exact fresh grant;
- exact reservation set;
- corrective WorkPacket scope.

### New-attempt rule

PASS.

The corrective evaluator rejects reuse of:

- the prior AuthorityCandidate digest;
- the prior intended-attempt identity;
- the prior ExecutionId.

A genuinely new corrective runtime attempt therefore requires a distinct attempt identity and exact fresh candidate/grant/reservation applicability.

### Scope boundary

PASS.

Correction scope is checked against both:

- evaluator-permitted corrective scope;
- prior authorized WorkPacket scope/out-of-scope declarations.

Scope excess returns:

`NEW_AUTHORITY_REQUIRED`.

Missing/conflicting evaluator provenance or reviewed-subject identity returns:

`INDETERMINATE`.

### No-change-manifest case

PASS by implementation semantics.

`prior_execution_binding(...)` returns no terminal-candidate digest when the prior terminal evidence has no change manifest, and `evaluate_evaluator_rework(...)` returns `INDETERMINATE` for an unavailable prior terminal candidate rather than inventing one.

## 5. Finding I31-F002 — consumable exact identity is collapsed to consumable_key

**Severity:** blocking but narrow  
**Disposition:** REWORK REQUIRED

Accepted Slice 2.5 defines:

```text
ConsumableRef(
    consumable_key,
    scope_key
)
```

and describes a consumable as an exact stable reference plus declared scope.

Slice 3.1's own grant/reservation evaluator correctly uses the pair:

```text
(consumable_key, scope_key)
```

when matching `ConsumptionRequirement` to `ConsumableReservationBinding`.

However, two Slice 3.1 model boundaries collapse that exact identity to `consumable_key` alone.

### 5.1 Base ExecutionSubject

`ExecutionSubject.reservations` currently validates canonicality using only:

```text
item.consumable_key
```

and rejects duplicate consumable keys regardless of distinct `scope_key`.

This can reject a valid candidate with two exact consumables such as:

```text
(consumable_key="campaign-budget", scope_key="scope-a")
(consumable_key="campaign-budget", scope_key="scope-b")
```

even though Slice 2.5 represents them as distinct exact references.

### 5.2 CorrectiveSubjectBinding

The new A17 binding repeats the collapse:

- reservation canonicality uses only `consumable_key`;
- `required_reservation_keys` stores only `consumable_key`;
- the exact-match validator compares only those keys.

Therefore the corrective evidence cannot faithfully represent all valid Slice 2.5 reservation sets.

This is inconsistent with the otherwise-correct `_reservation_reasons(...)` implementation, which already matches exact reservation identity as:

```text
(consumable_key, scope_key)
```.

## 6. Required narrow correction

Remain entirely inside:

```text
src/relay_engine/coding_execution/**
tests/unit/test_coding_execution_*.py
```

No predecessor change is justified.

Preserve exact reservation identity everywhere as the ordered pair:

```text
(consumable_key, scope_key)
```

A minimal correction should:

1. canonicalize `ExecutionSubject.reservations` by the exact pair, not key alone;
2. canonicalize `CorrectiveSubjectBinding.reservations` by the exact pair;
3. replace `required_reservation_keys` with an exact pair-based representation, e.g. `required_reservation_refs` or equivalent;
4. compare the complete exact required reservation set to the complete exact supplied reservation set;
5. retain grant digest, candidate digest, intended-attempt, atomic-at-grant, and RESERVED-state checks;
6. sort deterministically by the pair;
7. reject an actual duplicate exact pair;
8. permit the same `consumable_key` under two different `scope_key` values.

Do not weaken or alter Slice 2.5's model.

## 7. Required corrective tests

Add deterministic tests proving at minimum:

1. two reservations with the same `consumable_key` and distinct `scope_key` values are valid and preserved;
2. both exact refs can correspond to two distinct `ConsumptionRequirement` records;
3. duplicate exact `(consumable_key, scope_key)` is rejected;
4. missing one scope-specific reservation remains fail-closed / indeterminate;
5. wrong `scope_key` is rejected even when `consumable_key` matches;
6. `CorrectiveSubjectBinding` preserves the same exact pair set as the corrective candidate's applicable requirements;
7. `ExecutionSubject` accepts the valid multi-scope set and retains exact ordering;
8. existing single-reservation and zero-reservation behavior remains unchanged.

Rerun all focused Slice 3.1 tests and the full repository suite.

## 8. A17 disposition

```text
I31-F001:
CLOSED

A17:
IMPLEMENTED AND SUBSTANTIVELY PROVEN

Evaluator REWORK binding:
PASS

Finding-ID lineage:
PASS

Corrective scope classification:
PASS

Fresh attempt identity:
PASS

Fresh grant/reservation requirement:
PASS

Corrective binding carried into ExecutionSubject:
PASS
```

No additional A17 work is required beyond adapting its reservation identity representation to the exact pair as part of I31-F002.

## 9. Authority

The reservation-identity correction is inside the already authorized Slice 3.1 implementation package and is necessary to conform to the accepted Slice 2.5 contract.

Therefore:

```text
new Human authority:
NOT REQUIRED

predecessor reopening:
NOT REQUIRED

design rework:
NOT REQUIRED

bounded corrective implementation:
AUTHORIZED under RLY-S31-IMPL-AUTH-001
```

## 10. Final disposition

```text
Exact corrective subject:
4a060a12a72d80d69138118e7194e61d4bb99542

Independent implementation evaluation:
RLY-S31-IMPL-EVAL-002 — REWORK / NARROW

Lineage:
PASS

Corrective file scope:
PASS

CI:
PASS

I31-F001 / A17:
CLOSED

I31-F002 / exact consumable reservation identity:
REWORK REQUIRED

Implementation acceptance:
NOT GRANTED

Execution:
NOT AUTHORIZED

Canonical promotion:
NOT AUTHORIZED
```

**REWORK — preserve exact consumable identity as `(consumable_key, scope_key)` across the base and corrective Slice 3.1 reservation bindings, add focused multi-scope tests, rerun validation, and return one exact corrective implementation candidate for independent re-review.**
