# Slice 1.7 — Independent Design Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Evaluation ID:** `RLY-S17-DESIGN-EVAL-001`  
**Outcome:** `REVISE`  
**Design authority:** `RLY-S17-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact evaluated Revision 1 SHA:** `a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6`  
**Exact design subject baseline:** `0a805d87617b01dd5a02668b15d43cbd81670a46`  
**Reviewer role:** Independent Slice 1.7 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REVISE
```

Revision 1 has the correct overall architecture and remains inside the authorized Slice 1.7 boundary. It cleanly separates engineering results, evaluator judgment, Human technical acceptance, and governed accepted-baseline promotion. It correctly reuses existing Baseline, Evidence, EvaluationOutcome, HumanApprovalDecision, gate evaluation, lifecycle, and ExecutionRecord semantics and gives a present-tense justification for one bounded append-only schema migration.

However, four contract gaps must be resolved before Human design acceptance. Two are blocking because they could permit stale Slice 1.6 controls or leave the roadmap's evidence-attachment flow unimplementable through the authorized product seam.

No lifecycle redesign, extra dependency, agent execution, or broader architecture is required.

---

# F001 — BLOCKING — Result attachment does not mechanically invalidate pre-result Slice 1.6 Human Action Basis

Revision 1 correctly says that attaching a result must make any prior evaluation/action projection inapplicable and must not fabricate assessment facts.

But the accepted Slice 1.6 `HumanActionBasis` and `_basis_for_snapshot()` currently validate only:

```text
lifecycle
current gate refs/baseline
latest GateEvaluationRecord
current authorization projection
current Human decision projection
```

They do not query Slice 1.7 result/evaluation history.

Therefore the following state is possible under Revision 1 as written:

```text
current EVALUATING lifecycle
latest GateEvaluationRecord structurally matches that lifecycle
        ↓
Slice 1.7 attaches a new result
        ↓
no successor GateEvaluationRecord is written by design
        ↓
old Slice 1.6 HumanActionBasis may still validate
```

Hiding controls in the board would not be sufficient because direct service calls must also fail closed.

### Required bounded correction

Extend the exact Human-action basis/current durable projection so Slice 1.6 gate-affecting commands know the current Slice 1.7 result/evaluation subject.

A minimum compatible design is:

```text
HumanActionBasis adds optional:
    current_result_id
    current_result_baseline_id
    current_manual_evaluation_id
```

with backward-compatible `None` defaults.

The Human-control snapshot must load the deterministic current result/evaluation projection from the new append-only tables and require the latest `GateEvaluationRecord.context` result/evaluation fields to match it.

Semantics:

```text
no current result
    + latest context result=None
    -> ordinary Slice 1.6 basis may be current

current result exists
    + no matching ManualEvaluationRecord / successor GateEvaluationRecord
    -> HumanActionRequiresEvaluation / no gate-affecting action basis

current result + current evaluation exist
    + latest context identifies both exactly
    -> ordinary exact-basis actions may resume
```

Human hold/blockage controls that intentionally do not require a gate-evaluation basis may remain available according to their existing semantics.

Do not create a fake GateEvaluationRecord merely to stale old forms.

---

# F002 — BLOCKING — Evidence attachment has no complete M0 application path

The roadmap exit bar requires evidence to be attached. Revision 1 makes `ManualEvaluationRecord` reference existing `EvidenceId` values, but the authorized HTTP surface contains no route or command that actually creates the Evidence a manual evaluator needs.

Existing low-level persistence `insert_evidence()` is not a Human-facing application contract.

Revision 1 hints that evidence may be newly supplied during evaluation but never makes that normative.

### Required bounded correction

Make evidence submission part of the manual-evaluation command rather than adding a generic evidence-management subsystem.

The minimum contract should allow:

```text
new evidence submissions
    evidence_id
    claim
    recorded_at

plus, optionally:
existing_evidence_ids
```

For new submissions the service must construct/persist `Evidence` using:

```text
recorded_by = server-bound evaluator actor
source_commit = exact current result Baseline commit
```

The form must never supply a different actor or source commit.

All newly created Evidence plus the `ManualEvaluationRecord` and successor `GateEvaluationRecord` must commit atomically in the same SQLite transaction.

Existing referenced Evidence must be validated against the same exact result commit.

To satisfy the roadmap exit bar, every `ManualEvaluationRecord` should reference at least one Evidence record after combining new and existing evidence. A reviewer observation may itself be recorded as Evidence when no automated check exists.

No generic Evidence CRUD UI is required.

---

# F003 — MAJOR — Human technical acceptance must remain mandatory even when the ACCEPTED gate's generic policy is AUTO

Revision 1 correctly reuses `HumanApprovalDecision`, but it describes technical acceptance as a wrapper over the existing approval machinery without resolving an important policy case.

Slice 1.6 normally exposes/records approval when gate policy or another review requirement needs Human approval. An ACCEPTED-target gate could nevertheless be configured as `AUTO` and become GREEN after evaluator `ACCEPT`.

Slice 1.7's controlling invariant is stronger:

```text
evaluator ACCEPT != Human technical acceptance
```

Therefore Human technical acceptance cannot depend on whether generic gate policy happens to ask for approval.

### Required bounded correction

The dedicated Slice 1.7 technical-acceptance command must be available for every exact current ACCEPTED-target gate after a current evaluator `ACCEPT`, regardless of `HandoverPolicy`.

It must reuse the existing `HumanApprovalDecision` model and durable decision table, but it need not reuse Slice 1.6's ordinary **availability rule** for `record_gate_approval()`.

Normative behavior:

```text
technical ACCEPT
    -> append current HumanApprovalDecision(APPROVE)

technical REJECT
    -> append current HumanApprovalDecision(REJECT)
```

Both bind the exact current lifecycle/governance/gate/baseline basis.

Promotion must independently require a current `APPROVE` on the exact ACCEPTED gate even when the gate would otherwise evaluate GREEN under `AUTO`.

A current `REJECT` continues to make the gate RED through accepted governance semantics.

No new acceptance table is needed.

---

# F004 — MAJOR — Successor HandoverContext construction must distinguish freshly re-derived durable facts from evaluator-supplied assessment facts

Revision 1 lists the fields that a manual evaluation changes, but it does not fully specify where the other successor `HandoverContext` facts come from.

The first evaluation may occur after a lifecycle transition where the latest GateEvaluationRecord belongs to the prior lifecycle revision. Copying that stale context wholesale would risk carrying old dependency or artifact facts into a new supposedly current gate observation.

### Required bounded correction

Define successor context construction explicitly.

Inside the evaluator write transaction, independently re-derive every durable fact that Relay can know exactly from the database:

```text
baseline_id
    = current gate/source authority baseline

lifecycle
    = current lifecycle

available_artifact_ids
    = exact current result Baseline artifact_ids

available_evidence_ids
    = exact Evidence IDs referenced by the current ManualEvaluationRecord

dependency_lifecycles
    = freshly loaded current lifecycles for the Slice's declared dependency IDs

authorization_grants
    = accepted deterministic current authorization projection

human_decisions
    = accepted deterministic current Human-decision projection

result_id / result_baseline_id / manual_evaluation_id
    = exact current Slice 1.7 chain tails
```

Evaluator-authored assessment facts are:

```text
evaluation_outcome
quality_checks
change_surface_status
risk_status
toolchain_change_status
```

`governance_revision` advances exactly once according to the Revision 1 monotonic rule.

Do not claim that unrelated external facts have been freshly observed unless the evaluator explicitly supplied them as assessment/evidence.

This also makes the meaning of `available_artifact_ids` unambiguous: the current result snapshot, not stale artifacts copied from the authority baseline.

---

# Accepted Revision 1 aspects

The following design decisions are accepted and should remain unless a later correction necessarily touches them:

- result Baseline is distinct from source/authority Baseline;
- exact result commit is represented by existing immutable `Baseline`;
- `SliceResultRecord` is append-only with explicit supersession;
- evaluated result cannot be silently replaced in the same evaluation attempt;
- result attachment does not fabricate assessment values;
- verified orphan Baseline after local CAS failure is harmless and not acceptance authority;
- authored `ManualEvaluationRecord` is distinct from `GateEvaluationRecord`;
- existing `EvaluationOutcome` vocabulary is reused without generic `ESCALATE`;
- evaluator actor is HUMAN in M0 and remains distinct as a command role from Human Authority;
- evidence remains separate durable claim-support state;
- evaluation supersession is explicit and append-only;
- `HandoverContext` receives backward-compatible optional exact result/evaluation identity fields;
- manual evaluation changes `governance_revision` exactly once and preserves monotonicity;
- evaluator outcomes never directly transition lifecycle;
- REWORK uses the existing `EVALUATING -> REWORK` governed path;
- Human technical acceptance reuses `HumanApprovalDecision`, not a new acceptance table;
- generic Slice 1.6 `ADVANCE` remains unable to execute an ACCEPTED target;
- dedicated Slice 1.7 promotion re-evaluates the exact ACCEPTED gate and uses existing governed execution persistence;
- accepted Baseline is derived causally from the accepted execution's exact result context rather than a mutable pointer;
- development memory is a deterministic projection over durable history and does not require repository mutation in M0;
- one append-only migration adding only `slice_results` and `manual_evaluations` is presently justified;
- caller-owned IDs/timestamps remain mandatory;
- no new dependency, lifecycle transition, AgentRuntime, autonomous evaluation, or Phase 2 scope is introduced.

---

# Required Revision 2 review evidence

A Revision 2 amendment should explicitly resolve F001–F004 and add/update implementation tests for:

```text
pending result invalidates old Human Action Basis
pending result blocks direct Slice 1.6 gate-affecting POST/service calls
matching evaluated result restores exact Human action basis
new Evidence creation through evaluate action
Evidence actor/source_commit cannot be forged by form input
at least one Evidence required per ManualEvaluationRecord
Evidence + evaluation + successor GateEvaluationRecord atomic rollback
technical acceptance available on AUTO ACCEPTED gate
promotion still impossible without current Human APPROVE
successor HandoverContext uses result Baseline artifacts and current dependencies
stale prior-lifecycle context facts are not copied as current durable facts
```

No implementation is authorized by this evaluation.

## Gate state

```text
Slice 1.7:
OPEN

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6

Independent design evaluation:
RLY-S17-DESIGN-EVAL-001 — REVISE

Human design acceptance:
NOT ELIGIBLE YET

Implementation:
NOT AUTHORIZED

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```
