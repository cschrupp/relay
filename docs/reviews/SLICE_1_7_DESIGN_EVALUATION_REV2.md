# Slice 1.7 — Independent Design Evaluation — Revision 2

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Evaluation ID:** `RLY-S17-DESIGN-EVAL-002`  
**Outcome:** `REVISE`  
**Design authority:** `RLY-S17-DESIGN-AUTH-001 — AUTHORIZED`  
**Revision 1:** `a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6`  
**Exact evaluated Revision 2 head:** `af91ae03a6b4eb76c68c190d71d782b04a509f90`  
**Prior evaluation:** `RLY-S17-DESIGN-EVAL-001 — REVISE`  
**Reviewer role:** Independent Slice 1.7 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REVISE
```

Revision 2 satisfactorily resolves `RLY-S17-DESIGN-EVAL-001` findings F001–F004. The architecture is otherwise coherent and remains minimal.

One backward-compatibility contradiction remains in Revision 1 D14 and must be corrected before design acceptance.

---

# F005 — BLOCKING — `evaluation_outcome -> manual_evaluation_id` cannot be a global `HandoverContext` model invariant

Revision 1 D14 proposes backward-compatible optional fields:

```text
result_id
result_baseline_id
manual_evaluation_id
```

and correctly states that they default to `None` so previously persisted `GateEvaluationRecord` payloads remain valid.

However, the same section states the model invariant:

```text
evaluation_outcome produced by Slice 1.7 requires manual_evaluation_id
```

As written, this is not implementable as a generic `HandoverContext` validator without either hidden provenance metadata or breaking accepted pre-Slice-1.7 contexts.

`HandoverContext.evaluation_outcome` existed since Slice 0.4 and existing durable/test contexts may legitimately contain:

```text
evaluation_outcome = ACCEPT | REWORK | ...
manual_evaluation_id = None
result_id = None
```

Those contexts are valid historical governance observations and must continue to deserialize unchanged.

A validator such as:

```text
if evaluation_outcome is not None and manual_evaluation_id is None:
    reject
```

would violate the design's own backward-compatibility requirement and could make historical GateEvaluationRecords unreadable.

### Required bounded correction

Keep only model invariants that can be evaluated from the serialized shape without reinterpreting historical semantics:

```text
result_id and result_baseline_id are both present or both absent

manual_evaluation_id != None
    -> result_id != None
    -> result_baseline_id != None
    -> evaluation_outcome != None
```

Do **not** require the reverse globally:

```text
evaluation_outcome != None
    -/-> manual_evaluation_id required
```

Instead, enforce the stronger Slice 1.7 rule at Slice 1.7 application/service boundaries:

```text
record_manual_evaluation successor context
technical_accept / technical_reject
promote_accepted_result
current Slice 1.7 evaluated-subject projection
```

must require that the current evaluation outcome used as Slice 1.7 authored evaluation truth is accompanied by the exact current:

```text
result_id
result_baseline_id
manual_evaluation_id
```

This preserves historical Slice 0.4–1.6 contexts while making Slice 1.7-produced contexts exact.

Add compatibility tests that deserialize/evaluate old-style non-null `evaluation_outcome` contexts with all new fields absent.

---

# Revision 2 findings resolved

The evaluator confirms that Revision 2 resolves the prior review as follows:

```text
F001 — pending result could leave old Human Action Basis valid
RESOLVED

F002 — no complete evidence-creation path
RESOLVED

F003 — technical acceptance could depend on generic gate policy
RESOLVED

F004 — successor HandoverContext source facts under-specified
RESOLVED
```

Accepted Revision 2 corrections include:

- exact result/evaluation identities in `HumanActionBasis` and Human-control durable validation;
- no fabricated GateEvaluationRecord for a merely attached result;
- atomic creation of result-bound Evidence during evaluator submission;
- non-empty evaluation Evidence requirement;
- server-bound Evidence actor and exact result commit;
- mandatory technical acceptance for every ACCEPTED-target gate regardless of generic policy;
- explicit Human APPROVE requirement in promotion even for AUTO gates;
- fresh reconstruction of result artifacts, dependency lifecycles, grants, and Human decisions;
- evaluator-owned assessment facts kept separate from re-derived durable facts;
- historical accepted-result projection surviving later Slice supersession;
- bounded Human-control change surface and added tests.

No other blocking or major findings were identified in this pass.

## Required Revision 3 evidence

Revision 3 must:

```text
remove the reverse global evaluation_outcome -> manual_evaluation_id requirement
preserve manual_evaluation_id -> result + outcome requirement
place Slice 1.7 stronger subject checks at service/application boundaries
require backward-compat tests for pre-1.7 HandoverContext/GateEvaluationRecord payloads
```

No implementation is authorized.

## Gate state

```text
Slice 1.7:
OPEN

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Revision 2:
af91ae03a6b4eb76c68c190d71d782b04a509f90

Independent design evaluation:
RLY-S17-DESIGN-EVAL-002 — REVISE

Human design acceptance:
NOT ELIGIBLE YET

Implementation:
NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```
