# Slice 1.7 — Independent Design Evaluation — Revision 4

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Evaluation ID:** `RLY-S17-DESIGN-EVAL-004`  
**Outcome:** `ACCEPT`  
**Design authority:** `RLY-S17-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact accepted combined design head:** `d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b`  
**Revision chain:** Revision 1 + Revision 2 + Revision 3 + Revision 4  
**Prior evaluations:** `RLY-S17-DESIGN-EVAL-001 — REVISE`; `RLY-S17-DESIGN-EVAL-002 — REVISE`; `RLY-S17-DESIGN-EVAL-003 — REVISE`  
**Reviewer role:** Independent Slice 1.7 Design Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The combined Revision 1 + Revision 2 + Revision 3 + Revision 4 design satisfies `RLY-S17-DESIGN-AUTH-001` and the canonical Slice 1.7 roadmap objective.

Revision 4 is normative over Revision 3 where they differ; Revision 3 is normative over Revision 2; Revision 2 is normative over Revision 1. All six findings raised across the prior independent evaluations are resolved without unauthorized scope expansion.

No blocking or major findings remain.

---

# Accepted architectural result

The design completes the human-only development loop with the following causal separation:

```text
verified exact result Baseline
        ↓
immutable SliceResultRecord
        ↓
immutable authored ManualEvaluationRecord + Evidence
        ↓
deterministic GateEvaluationRecord
        ↓
explicit HumanApprovalDecision on exact ACCEPTED gate
        ↓
exact GREEN governed ACCEPTED handover
        ↓
ExecutionRecord + ACCEPTED lifecycle
        ↓
causally promoted accepted Baseline
```

The design preserves the mandatory distinctions:

```text
engineering evidence
    !=
evaluator decision
    !=
Human technical acceptance
    !=
accepted-baseline promotion
```

and:

```text
passing CI
    !=
evaluation ACCEPT
    !=
ACCEPTED lifecycle state
```

and:

```text
moving branch/ref
    !=
accepted Baseline
```

---

# Findings resolution

## F001 — stale Slice 1.6 actions after result attachment

```text
RESOLVED
```

Current result/result-Baseline/manual-evaluation identity becomes part of the exact Human Action Basis and durable Human-control validation. A newly attached result with no matching authored evaluation/successor GateEvaluationRecord fails closed as `HumanActionRequiresEvaluation`; no fake assessment record is created.

## F002 — missing evidence-creation path

```text
RESOLVED
```

The manual-evaluation command accepts bounded new Evidence submissions and optional existing Evidence IDs. New Evidence actor and exact result commit are server-bound, at least one Evidence record is required, and new Evidence + evaluation + successor gate observation commit atomically.

## F003 — Human acceptance could depend on generic gate policy

```text
RESOLVED
```

Technical acceptance is a Slice 1.7 semantic command available for every exact current ACCEPTED-target gate after authored evaluator `ACCEPT`, regardless of generic HandoverPolicy. It reuses `HumanApprovalDecision`, while promotion independently requires a current exact Human `APPROVE` even for AUTO gates.

## F004 — successor context facts under-specified

```text
RESOLVED
```

Successor HandoverContext reconstructs current durable facts from the database: result Baseline artifacts, current dependency lifecycles, authorization projection, Human-decision projection, exact result/evaluation identity, and evaluator-supplied assessment facts. Stale prior-lifecycle context is not copied as current truth.

## F005 — backward-incompatible evaluation-outcome invariant

```text
RESOLVED
```

The generic HandoverContext remains backward-compatible. A manual evaluation ID requires exact result identity and an evaluation outcome, but a historical bare evaluation outcome remains valid. Slice 1.7 services apply the stronger exact-subject rule only where Slice 1.7 authored evaluation authority is required.

## F006 — result Baseline Decision authority could drift

```text
RESOLVED
```

Result Baseline `decision_ids` are loaded server-side from and must equal the exact source/authority Baseline Decision tuple. Attach-result cannot accept Decision authority from the client. Evaluation, promotion, and accepted-result reconstruction revalidate this invariant.

---

# Accepted domain and persistence boundary

The design introduces only the missing present-tense M0 concepts:

```text
SliceResultRecord
ManualEvaluationRecord
```

with new typed IDs:

```text
res_<uuid7>
eval_<uuid7>
```

One bounded append-only schema migration is justified to add:

```text
slice_results
manual_evaluations
```

with typed JSON payloads, deterministic indexed fields, append-only triggers, explicit supersession chains, and chain-integrity validation.

The evaluator agrees that existing tables cannot faithfully represent these concepts without overloading `Evidence`, `GateEvaluationRecord`, or another accepted record type.

No separate tables are introduced for:

```text
technical acceptance
accepted-baseline pointer
current evaluation
commands
workflow orchestration
```

This remains minimum sufficient architecture.

**Important authority boundary:** design acceptance of this architecture would not itself authorize applying the schema migration. A later implementation authorization must explicitly include the accepted bounded migration.

---

# Accepted result semantics

The existing immutable `Baseline` represents the exact result repository snapshot.

For each result:

```text
source Baseline
    = exact work/gate authority

result Baseline
    = exact resulting repository snapshot
```

The result Baseline:

- carries the exact verified result commit;
- carries registered artifact revisions actually present in that result snapshot;
- preserves exactly the source Baseline Decision IDs;
- belongs to the same Project/repository;
- is not accepted merely because it exists.

Result attachment is append-only and explicit. Evaluated results cannot be silently replaced in the same evaluation attempt. Rework creates a successor result lineage after the governed rework cycle.

---

# Accepted evaluator semantics

The design correctly reuses the existing `EvaluationOutcome` enum rather than inventing another outcome system.

Manual evaluation:

- requires current `EVALUATING` state;
- binds exact Slice definition/lifecycle/result/gates/source Baseline/result Baseline;
- records a server-bound HUMAN evaluator in M0;
- requires non-empty exact-result Evidence;
- records findings and summary;
- may be explicitly superseded without rewriting history;
- advances `governance_revision` exactly once;
- atomically emits the successor deterministic GateEvaluationRecord;
- never directly transitions lifecycle.

The accepted evaluator outcome set remains the existing domain vocabulary, including `ACCEPT`, `REWORK`, specific escalation outcomes, `BLOCKED`, and `EXPERIMENT_REQUIRED`.

---

# Accepted REWORK semantics

`REWORK` is not a new state or direct evaluator side effect.

The evaluator records `REWORK`; then an existing current REWORK-target handover must be selected and become GREEN through the accepted governance system before `EVALUATING -> REWORK` executes.

Prior result/evaluation provenance remains immutable.

A later reworked result is a new exact result record and Baseline, not a rewrite of the previous candidate.

---

# Accepted Human technical-acceptance semantics

Human technical acceptance reuses the accepted `HumanApprovalDecision` model and durable Human-decision table.

The dedicated Slice 1.7 command owns the mandatory technical-acceptance availability rule and binds it to:

```text
exact current result
exact current result Baseline
exact current authored evaluator ACCEPT
exact ACCEPTED gate/revision
exact current lifecycle revision
governance revision
source/authority Baseline
server-bound HUMAN actor
```

A new evaluation naturally stales the prior technical acceptance because governance revision advances.

A Human `REJECT` does not falsify evaluator evidence or manufacture `REWORK`.

---

# Accepted promotion semantics

The existing Slice 1.6 generic `ADVANCE` prohibition on ACCEPTED remains unchanged.

Slice 1.7 owns one dedicated promotion command. It:

- reloads exact current durable state inside one transaction;
- requires current authored evaluator `ACCEPT`;
- requires exact current Human `APPROVE` even if generic gate policy is AUTO;
- revalidates source/result Decision-set equality;
- re-evaluates the complete current gate set;
- requires the selected ACCEPTED gate to be GREEN;
- calls the accepted governed handover execution/persistence path;
- never invokes direct lifecycle ACCEPTED mutation.

The accepted Baseline is then reconstructed causally from the ACCEPTED ExecutionRecord's GateEvaluationRecord context and exact `result_baseline_id`.

No mutable accepted-baseline pointer is required.

The accepted result remains historical provenance even if the Slice is later `SUPERSEDED`.

---

# Accepted development-memory interpretation

The evaluator accepts the M0 interpretation of the roadmap's development-memory requirement:

```text
DevelopmentMemoryProjection
```

is a deterministic human-readable projection of durable result/evaluation/rework/acceptance/execution history.

Repository-side `.relay/` mutation is not required for Slice 1.7 and remains separately governed. This avoids conflating development-memory generation with repository write authority.

---

# Expected future implementation boundary

New:

```text
src/relay_engine/manual_evaluation/
    __init__.py
    errors.py
    models.py
    service.py
```

Bounded existing changes:

```text
src/relay_engine/domain/ids.py
src/relay_engine/governance/models.py
src/relay_engine/human_control/models.py
src/relay_engine/human_control/service.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/records.py       # only if mechanically useful
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
```

Narrow repository-baseline changes are permitted only if mechanically necessary to reuse exact existing Baseline resolution/persistence.

Expected:

```text
schema migration: ONE bounded append-only migration
new runtime dependency: NONE
new dev dependency: NONE
lifecycle transition change: NONE
provider mutation: NONE
repository mutation: NONE
agent execution: NONE
```

---

# Review conclusion

The combined design is sufficiently exact to authorize implementation later without requiring the implementation agent to reinterpret core governance semantics.

It preserves:

- exact-baseline authority;
- historical provenance;
- fail-closed staleness;
- deterministic current subject identity;
- explicit evaluator/Human separation;
- governed lifecycle execution;
- current result/evaluation concurrency;
- minimum sufficient architecture;
- Phase 2 and agent-execution boundaries.

No design-level rework remains.

## Gate state

```text
Slice 1.7:
OPEN

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Exact independently accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Independent design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Phase 1 M0 validation:
NOT YET COMPLETED

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Independent design ACCEPT is evidence. It does not grant Human design acceptance or implementation authorization.**
