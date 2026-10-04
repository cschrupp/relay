# Slice 1.7 — Manual Evaluation and Acceptance — Revision 3 Amendment

**Document class:** Lockable design amendment  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Design authority:** `RLY-S17-DESIGN-AUTH-001 — AUTHORIZED`  
**Revision 1:** `a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6`  
**Revision 2:** `af91ae03a6b4eb76c68c190d71d782b04a509f90`  
**Prior independent evaluations:** `RLY-S17-DESIGN-EVAL-001 — REVISE`; `RLY-S17-DESIGN-EVAL-002 — REVISE`  
**Purpose:** Resolve `RLY-S17-DESIGN-EVAL-002` finding F005 while preserving historical HandoverContext compatibility.

This amendment is normative over Revision 1 and Revision 2 where they differ. All unmodified decisions remain in force.

---

# R3-D01 — Backward-compatible `HandoverContext` shape invariants

Revision 1 D14 is corrected.

Slice 1.7 still adds the optional fields:

```python
result_id: SliceResultId | None = None
result_baseline_id: BaselineId | None = None
manual_evaluation_id: ManualEvaluationId | None = None
```

The only global model invariants are:

```text
result_id is present
    iff
result_baseline_id is present
```

and:

```text
manual_evaluation_id is present
    -> result_id is present
    -> result_baseline_id is present
    -> evaluation_outcome is present
```

There is deliberately **no reverse invariant**:

```text
evaluation_outcome is present
    does NOT globally require manual_evaluation_id
```

because `evaluation_outcome` predates Slice 1.7 and historical Slice 0.4–1.6 contexts may validly contain an evaluation outcome without authored Slice 1.7 result/evaluation identity.

Thus old serialized `HandoverContext` and `GateEvaluationRecord` payloads remain valid with the new fields absent.

---

# R3-D02 — Slice 1.7-produced evaluation truth has the stronger application invariant

Although the generic model remains backward-compatible, Slice 1.7 application services enforce a stronger rule for **current authored manual-evaluation truth**.

Whenever Slice 1.7 treats `HandoverContext.evaluation_outcome` as the outcome of the current `ManualEvaluationRecord`, the context must contain all four exact values:

```text
result_id
result_baseline_id
manual_evaluation_id
evaluation_outcome
```

and they must agree with the deterministic current Slice 1.7 subject/evaluation chain loaded from durable state.

This stronger rule is mandatory in:

```text
record_manual_evaluation successor-context construction
project_manual_evaluation current-state projection
Human-control exact-basis validation when a current result exists
record_technical_acceptance
record_technical_rejection
promote_accepted_result
accepted-result causal-chain reconstruction
```

Therefore an old-style context such as:

```text
evaluation_outcome = ACCEPT
result_id = None
result_baseline_id = None
manual_evaluation_id = None
```

remains a valid historical/general governance context, but it can **never** satisfy Slice 1.7 current manual-evaluation subject requirements or authorize Slice 1.7 technical acceptance/promotion.

---

# R3-D03 — Slice 1.7 promotion never infers authored evaluation from a bare outcome

`promote_accepted_result(...)` must reject a context that has:

```text
evaluation_outcome = ACCEPT
```

without exact current:

```text
result_id
result_baseline_id
manual_evaluation_id
```

Even if the ACCEPTED-target gate otherwise evaluates GREEN, a bare pre-1.7 or externally supplied `EvaluationOutcome.ACCEPT` is insufficient for Slice 1.7 accepted-baseline promotion.

The same rule applies to technical-acceptance controls.

This preserves:

```text
generic governance evaluation outcome
    !=
Slice 1.7 authored ManualEvaluationRecord
```

---

# R3-D04 — Compatibility and negative tests are mandatory

Add to the future implementation test contract:

```text
pre-1.7 HandoverContext with evaluation_outcome=ACCEPT and all new fields absent still validates
pre-1.7 HandoverContext with evaluation_outcome=REWORK and all new fields absent still validates
old GateEvaluationRecord fixtures/payloads deserialize unchanged
result_id without result_baseline_id rejected
result_baseline_id without result_id rejected
manual_evaluation_id without result identity rejected
manual_evaluation_id without evaluation_outcome rejected
bare evaluation_outcome ACCEPT cannot expose Slice 1.7 technical-accept action
bare evaluation_outcome ACCEPT cannot promote accepted result
current Slice 1.7 evaluation context with exact result/evaluation identity succeeds
```

---

# R3-D05 — Resolution of F005

```text
RLY-S17-DESIGN-EVAL-002 / F005
RESOLVED
```

The correction preserves both:

```text
historical schema compatibility
```

and:

```text
exact Slice 1.7 authored-evaluation authority
```

without adding another provenance field, schema concept, or migration.

## Gate state

```text
Slice 1.7:
OPEN

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6

Revision 2:
af91ae03a6b4eb76c68c190d71d782b04a509f90

Revision 3 amendment:
THIS COMMIT SUBJECT

Prior independent evaluation:
RLY-S17-DESIGN-EVAL-002 — REVISE

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Backward compatibility does not weaken current authority. Current authority does not rewrite historical semantics.**
