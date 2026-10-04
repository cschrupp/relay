# Slice 1.7 — Manual Evaluation and Acceptance

**Document class:** Lockable design record  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Document revision:** 1  
**Opening authority:** `RLY-S17-OPEN-001`  
**Design authority:** `RLY-S17-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact design subject baseline:** `0a805d87617b01dd5a02668b15d43cbd81670a46`  
**Design-authority parent:** `8a93f666fbb8dd3099fbc8d5699f8fe3cef7e094`  
**Implementation authorization:** NOT GRANTED

---

# 1. Objective

Complete Relay's human-only development loop without introducing agent execution or automatic acceptance.

The accepted roadmap sequence is:

```text
authorized
    ↓
external/manual implementation
    ↓
resulting commit
    ↓
manual evaluation
    ↓
accepted baseline
```

Slice 1.7 makes four concepts first-class and keeps them separate:

```text
engineering result
        !=
manual evaluator judgment
        !=
Human technical acceptance
        !=
accepted-baseline promotion
```

The deterministic target is:

> Given one exact result commit, one exact current Relay lifecycle/governance basis, one immutable manual evaluation, and one current Human acceptance decision, Relay either performs the exact governed transition to `ACCEPTED` and exposes the promoted Baseline, or fails closed without partial durable state.

Passing tests, successful CI, or an evaluator `ACCEPT` never by themselves produce lifecycle `ACCEPTED`.

---

# 2. Existing accepted substrate

Slice 1.7 reuses the accepted system rather than introducing a parallel workflow.

Existing authoritative primitives include:

- `Baseline`: an immutable exact repository commit plus authoritative artifact and decision references;
- `Evidence`: immutable claim-support evidence with actor/time/exact commit provenance;
- `EvaluationOutcome`: `ACCEPT`, `REWORK`, `ESCALATE_CONTRACT`, `ESCALATE_ARCHITECTURE`, `BLOCKED`, `EXPERIMENT_REQUIRED`;
- `HandoverGate.required_evaluation_outcomes`;
- `HandoverContext.evaluation_outcome`;
- `HumanApprovalDecision` bound to exact slice/baseline/gate/revision/lifecycle/governance basis;
- `GateEvaluationRecord` as immutable deterministic gate-computation evidence;
- `ExecutionRecord` as immutable governed lifecycle-movement evidence;
- lifecycle phases `EVALUATING`, `REWORK`, and `ACCEPTED`;
- the accepted transition matrix `EVALUATING -> REWORK | ACCEPTED` and `REWORK -> EVALUATING`;
- Slice 1.6 exact Human Action Basis, CSRF, actor binding, request-scoped SQLite, and governed handover execution;
- repository baseline resolution that proves an immutable commit and persists a `Baseline`.

Two required M0 concepts do **not** yet exist durably:

1. a Slice-local engineering-result record binding an exact candidate Baseline to the lifecycle attempt being evaluated;
2. an authored evaluator judgment with evaluator identity, exact result subject, evidence, findings, and outcome.

`GateEvaluationRecord` is not this authored evaluation. It records deterministic gate computation. `Evidence` is not an evaluator decision. The accepted Slice 0.2 design explicitly deferred the `Evaluation` concept and baseline-promotion behavior.

---

# 3. S1.7-D01 — Result, evaluation, acceptance, and promotion remain distinct

The controlling causal chain is:

```text
SliceResultRecord
    exact candidate Baseline
          ↓
ManualEvaluationRecord
    exact result + evidence + outcome
          ↓
GateEvaluationRecord
    deterministic current governance consequence
          ↓
HumanApprovalDecision(APPROVE)
    exact ACCEPTED gate/current governance basis
          ↓
ExecutionRecord
    governed EVALUATING -> ACCEPTED
          ↓
AcceptedSliceResult projection
    exact result Baseline is now promoted
```

No step is inferred from the previous one.

In particular:

```text
Evidence PASS
    does not imply ManualEvaluationRecord(ACCEPT)

ManualEvaluationRecord(ACCEPT)
    does not imply HumanApprovalDecision(APPROVE)

HumanApprovalDecision(APPROVE)
    does not imply lifecycle ACCEPTED

branch/ref movement
    does not imply accepted Baseline
```

---

# 4. S1.7-D02 — Reuse `Baseline` for the exact resulting commit

Slice 1.7 does not create a second commit/result snapshot type.

The external/manual implementation result must first be represented by an immutable Relay `Baseline` whose `commit.sha` is the exact resulting commit.

For GitHub-attached projects, the existing `RepositoryBaselineService` remains the authoritative way to verify the commit-pinned repository snapshot and persist that Baseline.

The result input may be entered as an exact full commit SHA. A branch or tag may be used only as a selector to resolve an immutable commit through the accepted baseline-resolution service. The resolved SHA, never the moving selector, is the result identity.

The original gate/authorization `baseline_id` remains the authority baseline for the Slice work. The result Baseline is separate:

```text
source / authority baseline
    answers: from what accepted engineering authority was this work performed?

result baseline
    answers: what exact repository snapshot resulted from the work?
```

Slice 1.7 must not replace `HandoverGate.baseline_id` with the result Baseline. Doing so would invalidate existing authorization semantics.

---

# 5. S1.7-D03 — Introduce `SliceResultRecord`

Slice 1.7 introduces an immutable, append-only result-subject record.

Conceptually:

```python
SliceResultRecord(
    schema_version,
    result_id,
    slice_id,
    slice_definition_revision,
    source_baseline_id,
    result_baseline_id,
    lifecycle_revision,
    supersedes_result_id,
    recorded_by,
    recorded_at,
    reason,
)
```

New identifier:

```text
SliceResultId = res_<uuid7>
```

Rules:

```text
recorded_by.kind = HUMAN in M0
recorded_at is explicit, timezone-aware, UTC-normalized
reason is nonblank
source_baseline_id identifies the exact current gate/authority baseline
result_baseline_id identifies an existing immutable Baseline
result Baseline belongs to the same Project/repository as the Slice
lifecycle phase must be EVALUATING
lifecycle_revision must equal the exact current revision
slice_definition_revision must equal the exact current definition revision
```

The exact commit is obtained through `result_baseline_id -> Baseline.commit`.

A result record never mutates or deletes an earlier result.

---

# 6. S1.7-D04 — Result replacement is explicit historical supersession

The current result is determined from an explicit supersession chain, not timestamp guessing.

For the first result attempt:

```text
supersedes_result_id = None
```

A replacement result may be appended only when the caller supplies the expected current result identity.

If replacing a result during the **same** `EVALUATING` lifecycle revision, replacement is allowed only before any manual evaluation has been recorded for the current result. This supports correcting an incorrectly attached candidate without rewriting history.

Once the current result has a manual evaluation, a new result requires the normal governed rework cycle:

```text
EVALUATING
    ↓ evaluator REWORK
REWORK
    ↓ external/manual rework
EVALUATING at a later lifecycle revision
    ↓ new SliceResultRecord superseding prior result
```

Therefore:

```text
evaluated result A
    cannot silently become
result B in the same evaluation attempt
```

Every prior result remains reconstructable.

Concurrent result attachment uses compare-and-swap semantics over:

```text
expected lifecycle revision
expected slice definition revision
expected current result ID (or explicit NONE)
```

A mismatch is a stale/conflict failure with no write.

---

# 7. S1.7-D05 — Result attachment does not fabricate an evaluation

Attaching an exact result does not create a `ManualEvaluationRecord` and does not manufacture a fresh `GateEvaluationRecord`.

This is intentional.

The existing `HandoverContext` contains assessment facts such as:

```text
evaluation outcome
quality checks
change-surface status
risk status
toolchain-change status
```

Those facts cannot be truthfully inferred merely because a result SHA was attached.

Therefore result attachment:

- persists only the verified immutable Baseline if needed and the `SliceResultRecord`;
- makes any prior evaluation/action projection inapplicable to the new result subject;
- exposes the result as **awaiting manual evaluation**;
- permits no ACCEPTED transition until an authored evaluation establishes current assessment facts.

The system must not fill unknown assessment values with optimistic defaults.

---

# 8. S1.7-D06 — Remote baseline verification and local result attachment are two bounded steps

Git/provider verification cannot participate in the same SQLite transaction as local Relay state.

The sequence is:

```text
1. resolve and verify exact repository commit
2. persist immutable candidate Baseline using accepted repository-baseline service
3. open local Slice 1.7 write transaction
4. re-check current Slice/result/lifecycle basis
5. append SliceResultRecord
```

If step 2 succeeds and step 4 later fails because local state changed, the verified Baseline may remain as an unreferenced immutable Baseline.

That is acceptable and must not be silently deleted or reinterpreted as an accepted result.

```text
verified orphan Baseline
    = durable repository fact
    != attached Slice result
    != accepted Baseline
```

This avoids pretending remote provider I/O and SQLite state can commit atomically.

---

# 9. S1.7-D07 — Introduce authored `ManualEvaluationRecord`

Slice 1.7 introduces the Evaluation concept deferred by Slice 0.2.

Conceptually:

```python
ManualEvaluationRecord(
    schema_version,
    evaluation_id,
    slice_id,
    result_id,
    result_baseline_id,
    source_baseline_id,
    slice_definition_revision,
    lifecycle_revision,
    gate_refs,
    prior_gate_evaluation_record_id,
    supersedes_evaluation_id,
    evaluator,
    evaluated_at,
    outcome,
    evidence_ids,
    quality_checks,
    change_surface_status,
    risk_status,
    toolchain_change_status,
    findings,
    summary,
)
```

New identifier:

```text
ManualEvaluationId = eval_<uuid7>
```

The record uses the existing `EvaluationOutcome` enum. Slice 1.7 does not introduce a competing outcome vocabulary.

The UI may present the minimum evaluator choices as:

```text
ACCEPT
REWORK
ESCALATE_CONTRACT
ESCALATE_ARCHITECTURE
```

The existing `BLOCKED` and `EXPERIMENT_REQUIRED` values remain valid evaluator outcomes when applicable to the project gate policy.

There is no generic untyped `ESCALATE` value.

---

# 10. S1.7-D08 — Evaluator identity and findings

For M0 manual operation:

```text
evaluator.kind = HUMAN
```

The evaluator actor is server-configured/bound, not form-supplied.

The evaluator may be the same human identity as the configured Human Authority in a solo dogfood installation, but the commands remain separate role boundaries:

```text
EVALUATOR command
    records engineering judgment

HUMAN AUTHORITY command
    grants acceptance authority
```

Future agent evaluators are not authorized by Slice 1.7.

`findings` is a deterministic ordered tuple of nonblank textual findings. It may be empty for a clean evaluation. `summary` is nonblank and records the evaluator's rationale.

Slice 1.7 does not create a generalized findings taxonomy or issue subsystem.

---

# 11. S1.7-D09 — Evaluation evidence reuses `Evidence`

A manual evaluation references existing `EvidenceId` values.

For every referenced evidence item:

```text
Evidence must exist
Evidence.source_commit must equal the result Baseline CommitRef
Evidence must be readable inside the same local transaction
Evidence IDs must be unique and canonicalized deterministically
```

Typical evidence may record:

```text
CI run and result
formatter/linter/type-check/test/build outcome
review observations
scope/change-surface observations
specific contract checks
```

Evidence records remain independent durable facts.

Replacing or superseding a manual evaluation never deletes or rewrites its evidence.

A later result commit requires evidence whose `source_commit` matches that later result; evidence from result A cannot silently satisfy result B.

---

# 12. S1.7-D10 — Evaluation binds exact current subject and governance structure

A new manual evaluation is valid only when all of the following still match inside the write transaction:

```text
Slice exists
current Slice definition revision
current lifecycle phase == EVALUATING
current lifecycle revision
current result identity
current result Baseline
current source/authority baseline
current outgoing gate IDs/revisions
expected latest manual evaluation ID (or NONE)
expected latest durable GateEvaluationRecord ID (or NONE)
```

`gate_refs` persisted on the evaluation are the complete sorted current outgoing gate set for that `EVALUATING` lifecycle.

The command fails closed if gate policy changed, lifecycle moved, the current result changed, or a competing evaluator wrote first.

No stale form is silently rebased.

---

# 13. S1.7-D11 — Evaluation supersession is explicit

The first evaluation of a current result has:

```text
supersedes_evaluation_id = None
```

A corrected/reconsidered evaluation may be appended for the **same exact result and same current EVALUATING lifecycle attempt** only when the caller explicitly supplies the expected current evaluation ID.

The successor has:

```text
supersedes_evaluation_id = prior current evaluation ID
```

The prior record remains immutable.

An evaluation may not supersede an evaluation of another result or another lifecycle revision.

At most one successor may claim a given evaluation as its predecessor.

The deterministic current evaluation is the unique tail of this explicit chain.

---

# 14. S1.7-D12 — Extend `HandoverContext` narrowly with exact evaluation subject identity

The existing gate engine already understands `evaluation_outcome`, but the current context cannot identify which result/evaluation produced that outcome.

Slice 1.7 therefore extends `HandoverContext` with backward-compatible optional fields:

```python
result_id: SliceResultId | None = None
result_baseline_id: BaselineId | None = None
manual_evaluation_id: ManualEvaluationId | None = None
```

All default to `None`, so previously persisted GateEvaluationRecords remain valid.

Model invariants:

```text
result_id and result_baseline_id are both present or both absent
manual_evaluation_id requires result_id + result_baseline_id
evaluation_outcome produced by Slice 1.7 requires manual_evaluation_id
```

Existing `HandoverContext.baseline_id` retains its accepted meaning: the current gate/authority baseline.

The new fields identify the evaluated result and authored evaluation without redefining authorization.

---

# 15. S1.7-D13 — Governance revision remains monotonic and evaluation changes it

The existing accepted rule remains controlling:

> `governance_revision` advances when a non-human-decision gate-relevant fact changes without a lifecycle revision change.

A manual evaluator judgment changes at least:

```text
result/evaluation subject identity
evaluation outcome
available evidence
quality-check facts
change-surface assessment
risk assessment
toolchain-change assessment
```

Therefore each newly recorded or superseding `ManualEvaluationRecord` advances `governance_revision` exactly once.

The Slice 1.7 service determines the predecessor revision as the greatest durable `HandoverContext.governance_revision` previously recorded for the Slice, defaulting to `0` when no gate evaluation exists.

The successor evaluation uses:

```text
next_governance_revision = predecessor + 1
```

This preserves monotonicity across lifecycle revisions rather than resetting the counter.

Result attachment alone does not create a `HandoverContext` and therefore does not manufacture a governance revision. The result becomes a current gate fact when the manual evaluator records the judgment and successor GateEvaluationRecord.

Human approval/rejection continues **not** to advance `governance_revision`, preserving the accepted Slice 0.4/Slice 1.6 rule that a Human decision must not immediately stale itself.

---

# 16. S1.7-D14 — Recording an evaluation atomically refreshes deterministic gate truth

After validating the exact current subject, the manual-evaluation transaction performs:

```text
1. load current lifecycle, gates, Slice definition, result chain, evaluation chain
2. validate all referenced Evidence against exact result commit
3. append ManualEvaluationRecord
4. project current authorization grants and Human gate decisions using accepted Slice 1.6 semantics
5. build successor HandoverContext with:
       gate/authority baseline unchanged
       current lifecycle
       current result_id
       current result_baseline_id
       new manual_evaluation_id
       evaluation_outcome from evaluator
       evaluator-supplied evidence/quality/change/risk/toolchain facts
       next governance_revision
6. evaluate COMPLETE current outgoing gate set deterministically
7. append successor GateEvaluationRecord
8. commit atomically
```

The successor `GateEvaluationRecord` is the deterministic governance consequence of the authored evaluation. It is not the authored evaluation itself.

Causal time ordering must satisfy:

```text
result.recorded_at
    <= evidence.recorded_at where newly supplied by this action
    <= manual_evaluation.evaluated_at
    <= successor GateEvaluationRecord.recorded_at
```

Pre-existing evidence may have been recorded after result attachment and before evaluation; all evidence must still point at the exact result commit.

No partial manual evaluation may remain if successor gate-evaluation persistence fails.

---

# 17. S1.7-D15 — No prior current GateEvaluationRecord is required for first evaluation

Entering `EVALUATING` through the accepted governed handover records the execution basis that allowed the transition. It does not guarantee that a new gate observation already exists for the resulting `EVALUATING` lifecycle revision.

Slice 1.7 therefore does not require a matching current `GateEvaluationRecord` before the first manual evaluation.

Instead the evaluator command binds to:

- the exact current lifecycle;
- the exact current result;
- exact current gate revisions;
- the expected latest durable GateEvaluationRecord identity, even if that record belongs to the previous lifecycle revision;
- current durable authorization/Human evidence projections;
- explicit evaluator assessment facts.

The command fails if a newer GateEvaluationRecord appears between rendering and commit.

This permits the manual evaluator to create the first truthful current observation for the `EVALUATING` state without inventing assessment values beforehand.

---

# 18. S1.7-D16 — Evaluator outcome never directly moves lifecycle

Recording any evaluator outcome produces evidence and a successor gate evaluation only.

It does not invoke `transition_phase`.

For example:

```text
ManualEvaluationRecord(REWORK)
       ↓
current REWORK-target handover may become GREEN/YELLOW/RED
       ↓
ordinary governed Human controls resolve any required authority
       ↓
selected GREEN gate executes EVALUATING -> REWORK
```

Similarly:

```text
ManualEvaluationRecord(ACCEPT)
       ↓
ACCEPTED-target handover may become eligible
       ↓
Human technical acceptance still required
       ↓
separate promotion command executes ACCEPTED handover
```

`ESCALATE_CONTRACT`, `ESCALATE_ARCHITECTURE`, `BLOCKED`, and `EXPERIMENT_REQUIRED` are projected through the existing gate definitions. If no current gate accepts the outcome, Relay displays the result but invents no transition.

---

# 19. S1.7-D17 — REWORK reuses the existing lifecycle and governed handover path

Slice 1.7 introduces no new lifecycle phase.

The accepted transition remains:

```text
EVALUATING -> REWORK
```

A current REWORK-target gate must exist and must deterministically evaluate GREEN before it can execute.

If authorization or Human approval is required, the existing Slice 1.6 commands are used.

The evaluated result and evaluation remain immutable after movement to REWORK.

After external/manual rework, the Slice returns to `EVALUATING` through an existing governed handover and a new `SliceResultRecord` identifies the successor candidate.

No result or evaluation row is overwritten.

---

# 20. S1.7-D18 — Human technical acceptance reuses `HumanApprovalDecision`

Slice 1.7 does not create a redundant technical-acceptance table.

The exact Human technical-acceptance authority is the current `HumanApprovalDecision` for the exact current gate whose target is `LifecyclePhase.ACCEPTED`.

A Slice 1.7 technical-acceptance command is a narrow semantic wrapper over the accepted approval machinery and requires:

```text
current phase == EVALUATING
exact current result ID
exact current result Baseline
exact current manual evaluation ID
manual evaluation outcome == ACCEPT
exact current Slice 1.6 HumanActionBasis / latest GateEvaluationRecord
selected gate target == ACCEPTED
server-bound Human Authority actor
explicit reason
```

The command passes caller-generated decision ID/timestamp and successor gate-evaluation ID/timestamp using the accepted Slice 1.6 provenance contract.

The resulting `HumanApprovalDecision(APPROVE)` does not move lifecycle state.

`REJECT` records Human refusal for the ACCEPTED gate and makes that gate RED through existing governance semantics. It does not rewrite the evaluator's `ACCEPT` as `REWORK`.

If the Human wants rework, a valid current REWORK path must be selected through existing governed gates. Relay must not fabricate an evaluator `REWORK` outcome on the Human's behalf.

---

# 21. S1.7-D19 — Human acceptance is exactly bound even though the decision model is reused

No new subject fields are added to `HumanApprovalDecision`.

Exact subject binding is obtained from its accepted basis:

```text
HumanApprovalDecision
    binds lifecycle_revision + governance_revision + gate/revision + baseline

that governance revision's GateEvaluationRecord
    binds result_id + result_baseline_id + manual_evaluation_id
```

The acceptance command additionally requires submitted expected result/evaluation IDs and checks them against the current `HandoverContext` before writing the approval.

If a new evaluation supersedes the accepted evaluation, `governance_revision` advances and the prior approval becomes stale automatically.

This reuses the accepted staleness mechanism instead of adding a second acceptance-decision system.

---

# 22. S1.7-D20 — Only Slice 1.7 may product-execute the ACCEPTED target

Slice 1.6 deliberately refuses generic `ADVANCE` for an `ACCEPTED` target.

That restriction remains unchanged.

Slice 1.7 introduces a dedicated command, conceptually:

```python
promote_accepted_result(...)
```

It is the only M0 product seam that may execute a current gate targeting `ACCEPTED`.

The command requires:

```text
current lifecycle == EVALUATING and CURRENT/CLEAR as required by lifecycle engine
current Slice/result/evaluation exact
current manual evaluation outcome == ACCEPT
current HumanApprovalDecision(APPROVE) for exact ACCEPTED gate/current basis
current complete gate set and latest deterministic GateEvaluationRecord exact
selected ACCEPTED gate evaluates GREEN inside the write transaction
```

Then it calls the existing governed handover execution/persistence path with caller-supplied IDs/timestamps.

No direct `transition_phase(..., ACCEPTED)` call is permitted from Slice 1.7 product code.

---

# 23. S1.7-D21 — Accepted Baseline is derived from the governed ACCEPTED execution

Slice 1.7 introduces no mutable `accepted_baseline_id` pointer and no second Baseline table.

The accepted Baseline is defined causally:

```text
current lifecycle == ACCEPTED
        ↓
latest governed ExecutionRecord producing ACCEPTED
        ↓
ExecutionRecord.gate_evaluation_record_id
        ↓
GateEvaluationRecord.context.manual_evaluation_id
GateEvaluationRecord.context.result_id
GateEvaluationRecord.context.result_baseline_id
        ↓
immutable Baseline
```

The `result_baseline_id` carried by that exact execution basis is the promoted accepted Baseline for the Slice.

Thus:

```text
candidate Baseline may exist before acceptance

but

accepted Baseline status exists only after the governed ACCEPTED execution
```

This satisfies the roadmap requirement that `ACCEPT` creates a new accepted baseline as a **promotion of the exact candidate Baseline**, not as creation of a duplicate snapshot.

A branch head moving later cannot alter the accepted Baseline.

---

# 24. S1.7-D22 — Promotion transaction and causal ordering

The promotion write transaction performs:

```text
1. reload current lifecycle, gates, current result/evaluation, grants, decisions
2. require submitted exact Human Action Basis/current GateEvaluationRecord
3. require context result/evaluation IDs match current chain tails
4. require evaluation outcome ACCEPT
5. project latest Human approval and require current APPROVE on selected ACCEPTED gate
6. deterministically re-evaluate the COMPLETE current gate set
7. require selected ACCEPTED gate GREEN
8. call accepted execute-and-persist handover path
9. atomically append execution GateEvaluationRecord / lifecycle event / lifecycle snapshot / ExecutionRecord according to existing persistence contract
10. commit
```

The execution time must not predate:

```text
result attachment
evaluation time
required authorization grants
current Human acceptance decision
latest evaluation observation
```

If any basis is stale, the transaction rolls back with no lifecycle or execution write.

Retry after the Slice is already `ACCEPTED` may return the already-derived accepted result as target-state idempotent success **only** when the current durable accepted chain identifies the exact same result/evaluation/ACCEPTED execution. A different submitted subject is a conflict.

No duplicate `ExecutionRecord` is created for an idempotent accepted-state retry.

---

# 25. S1.7-D23 — Accepted-state projection

Slice detail gains a typed accepted-result projection, conceptually:

```python
AcceptedSliceResult(
    slice_id,
    result_id,
    result_baseline_id,
    commit,
    manual_evaluation_id,
    human_approval_decision_id,
    accepted_execution_id,
    accepted_at,
)
```

It is derived from durable history and is not stored as a competing mutable current-state row.

Integrity failure is raised if lifecycle `ACCEPTED` exists but the causal accepted-result chain cannot be reconstructed uniquely.

---

# 26. S1.7-D24 — Development memory is a deterministic durable-state projection in M0

The roadmap requires development memory to be generated or updated.

Slice 1.7 satisfies this without repository mutation by introducing a deterministic `DevelopmentMemoryProjection` generated from durable Relay state after evaluation/acceptance.

It contains, at minimum:

```text
Slice identity and definition revision
source/authority Baseline
result lineage and exact commit(s)
manual evaluation lineage
Evidence references
findings and evaluator outcome
Human technical-acceptance decision
ACCEPTED ExecutionRecord when accepted
accepted Baseline
known rework history
```

The projection may be rendered as server-generated Markdown/text on the Slice detail surface.

The underlying durable records are the authority; generated Markdown is a view.

Slice 1.7 does **not** commit or update a repository-side memory file. Repository mutation requires its existing separate authorization mechanisms and is not necessary to complete the M0 human loop.

If the result Baseline already contains a registered development-memory artifact, Relay may display it as evidence, but Slice 1.7 does not mutate it automatically.

A later separately authorized capability may materialize the deterministic projection into `.relay/`.

---

# 27. S1.7-D25 — One small schema migration is necessary and bounded

Unlike Slice 1.6, Slice 1.7 has present-tense requirements not representable by the current schema without abusing another record type.

A single migration is therefore part of the **proposed implementation contract**, subject to later explicit implementation authorization.

It adds only:

```text
slice_results
manual_evaluations
```

Conceptual schema:

```sql
CREATE TABLE slice_results (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id TEXT NOT NULL UNIQUE,
    slice_id TEXT NOT NULL REFERENCES slices(id),
    source_baseline_id TEXT NOT NULL REFERENCES baselines(id),
    result_baseline_id TEXT NOT NULL REFERENCES baselines(id),
    lifecycle_revision INTEGER NOT NULL CHECK (lifecycle_revision >= 0),
    supersedes_result_id TEXT UNIQUE REFERENCES slice_results(result_id),
    payload_json TEXT NOT NULL
);

CREATE TABLE manual_evaluations (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id TEXT NOT NULL UNIQUE,
    slice_id TEXT NOT NULL REFERENCES slices(id),
    result_id TEXT NOT NULL REFERENCES slice_results(result_id),
    result_baseline_id TEXT NOT NULL REFERENCES baselines(id),
    lifecycle_revision INTEGER NOT NULL CHECK (lifecycle_revision >= 0),
    supersedes_evaluation_id TEXT UNIQUE REFERENCES manual_evaluations(evaluation_id),
    payload_json TEXT NOT NULL
);
```

Indexes support deterministic per-Slice/per-result sequence reads.

Both tables receive `BEFORE UPDATE` and `BEFORE DELETE` triggers that fail, matching existing append-only history discipline.

Indexed columns must be cross-validated against typed payloads on load.

No separate technical-acceptance table, accepted-baseline table, mutable current-evaluation table, command log, event bus, or generalized audit table is introduced.

The migration must be added as the next contiguous checksummed migration and included in schema verification.

---

# 28. S1.7-D26 — Persistence chain validation is mandatory

Loading Slice 1.7 history must fail with `PersistenceIntegrityError` when durable rows cannot form an unambiguous chain.

At minimum validate:

```text
result IDs unique
result successor relation acyclic and at most one successor per result
all result records identify the same Slice when traversed as one Slice lineage
result Baselines exist and belong to Slice Project/repository
source Baselines exist
result lifecycle revisions do not regress along supersession
an evaluated result cannot be superseded in the same lifecycle revision

evaluation IDs unique
evaluation successor relation acyclic and at most one successor per evaluation
evaluation result_id exists
evaluation result Baseline equals referenced SliceResultRecord result Baseline
evaluation lifecycle / Slice definition / source baseline match its result subject
evaluation supersession remains on same result and lifecycle revision
evidence IDs exist and source commits equal exact result commit
```

The service must not treat malformed history as merely absent state.

---

# 29. S1.7-D27 — Caller-owned IDs and timestamps

Following Slice 1.6, the application boundary supplies all durable IDs and timestamps.

The manual-evaluation service never calls the clock or `new_id()` implicitly.

Caller-supplied provenance includes as applicable:

```text
result_id
result_recorded_at
manual_evaluation_id
manual_evaluation_at
successor_gate_evaluation_record_id
successor_gate_evaluation_recorded_at
Human decision ID/time
Human decision successor GateEvaluationRecord ID/time
promotion execution ID
promotion lifecycle event ID
promotion GateEvaluationRecord ID/time
promotion occurred_at
```

This keeps the service deterministic and directly testable.

---

# 30. S1.7-D28 — Application boundary

Create one bounded package:

```text
src/relay_engine/manual_evaluation/
    __init__.py
    errors.py
    models.py
    service.py
```

Expected service capabilities are conceptually:

```python
project_manual_evaluation(...)
attach_result(...)
record_manual_evaluation(...)
record_technical_acceptance(...)
record_technical_rejection(...)
promote_accepted_result(...)
project_development_memory(...)
```

`record_technical_acceptance/rejection` must reuse accepted Human-approval behavior rather than duplicate it semantically.

`promote_accepted_result` must reuse accepted governed execution persistence.

No generic command bus, workflow framework, event bus, plugin architecture, repository abstraction, or evaluator framework is introduced.

---

# 31. S1.7-D29 — Board projection and control surface

`SliceDetail` is extended with one typed `ManualEvaluationProjection`, conceptually:

```python
ManualEvaluationProjection(
    current_result,
    result_history,
    current_evaluation,
    evaluation_history,
    evaluation_actions,
    accepted_result,
    development_memory_available,
)
```

The board remains a projection/control surface over durable Relay state.

The Slice detail should expose enough provenance to inspect:

```text
source Baseline
result Baseline + exact commit SHA
Slice definition/lifecycle revision
result ID
manual evaluation ID/outcome
Evidence IDs/findings
GateEvaluationRecord and governance revision
Human acceptance decision ID
ACCEPTED execution / accepted Baseline if present
```

Actions are advisory. Every POST revalidates current durable state.

---

# 32. S1.7-D30 — Minimum HTTP mutations

Add only explicit server-rendered POST routes:

```text
POST /projects/{project_id}/slices/{slice_id}/actions/attach-result
POST /projects/{project_id}/slices/{slice_id}/actions/evaluate
POST /projects/{project_id}/slices/{slice_id}/actions/technical-accept
POST /projects/{project_id}/slices/{slice_id}/actions/technical-reject
POST /projects/{project_id}/slices/{slice_id}/actions/promote-accepted
```

Successful mutation uses:

```text
303 See Other
-> canonical Slice detail GET
```

GET/HEAD never mutate.

Use the accepted Slice 1.6 CSRF policy and request-scoped SQLite ownership unchanged.

Suggested HTTP error categories remain:

```text
404 NOT_FOUND
403 FORBIDDEN / CSRF
409 STALE_OR_CONFLICT
422 ACTION_INVALID
500 INTEGRITY_ERROR
503 UNAVAILABLE
```

No automatic stale-command retry is allowed.

---

# 33. S1.7-D31 — M0 actors and permissions

The application has two explicit configured command actors:

```text
manual_evaluator_actor: ActorRef(kind=HUMAN)
human_authority_actor: ActorRef(kind=HUMAN)
```

They may identify the same Human in a single-user installation.

Command permission is determined by which server-side actor is passed to which service method, not by hidden form fields.

Rules:

```text
attach result               -> HUMAN operator / authority boundary
record manual evaluation    -> configured manual evaluator
technical accept/reject     -> configured Human Authority
promote accepted result     -> configured Human Authority
```

SYSTEM and AGENT actors are rejected for evaluator and technical-acceptance commands in Slice 1.7.

No multi-user authentication, organizations, group membership, policy language, or broad RBAC redesign is authorized.

---

# 34. S1.7-D32 — Relationship with existing Slice 1.6 actions

Slice 1.7 does not duplicate ordinary Human controls.

Existing Slice 1.6 commands continue to own:

```text
AUTHORIZE
APPROVE / REJECT for ordinary gate requirements
CHOOSE_PATH
BLOCK / PAUSE / DEFER / RESUME
ADVANCE for non-ACCEPTED/non-CANCELLED targets
CANCEL
```

Slice 1.7 adds only the semantics needed around result/evaluation/technical acceptance and the dedicated ACCEPTED promotion.

A REWORK gate is executed through existing ordinary governed advancement once it is GREEN.

The dedicated technical-acceptance UI may call the same underlying approval machinery but must be visibly tied to the exact current evaluator ACCEPT/result subject.

---

# 35. S1.7-D33 — Current evaluation projection

For one Slice, current evaluation truth is derived as:

```text
current lifecycle must be EVALUATING
        ↓
unique current SliceResultRecord chain tail for current attempt
        ↓
unique ManualEvaluationRecord chain tail for that result, if present
        ↓
latest GateEvaluationRecord must project that exact result/evaluation before Human acceptance or promotion is available
```

A manual evaluation record existing without a matching successor `GateEvaluationRecord` is an integrity failure because those writes are required to be atomic.

A result with no evaluation is a valid pending-evaluation state.

An old evaluation from a prior result/lifecycle is history only.

---

# 36. S1.7-D34 — Staleness and concurrency rules

Every consequential command carries explicit expected identities.

At minimum:

### Attach result

```text
expected lifecycle revision
expected Slice definition revision
expected current result ID or NONE
```

### Evaluate

```text
expected lifecycle revision
expected Slice definition revision
expected current result ID
expected current manual evaluation ID or NONE
expected latest GateEvaluationRecord ID or NONE
exact current gate refs/revisions
```

### Technical accept/reject

```text
HumanActionBasis
expected result ID
expected manual evaluation ID
exact ACCEPTED gate/revision
```

### Promote accepted

```text
HumanActionBasis
expected result ID
expected manual evaluation ID
expected current Human approval decision ID
exact ACCEPTED gate/revision
```

Any mismatch is 409-style stale/conflict and produces no partial durable mutation.

---

# 37. S1.7-D35 — Idempotency

Safe target-state retries are narrowly defined.

```text
attach exact same result with exact same current basis and matching durable result record
    -> no-op success

record exact same evaluation identity/payload already current
    -> no-op success

technical accept/reject when exact same decision identity/payload already current
    -> accepted Slice 1.6 no-op semantics where applicable

promote exact same already-ACCEPTED result/evaluation
    -> return existing accepted projection, no second execution
```

A request with a new durable identity is not treated as the same retry merely because text fields happen to match.

Conflicting same-basis actions fail closed.

---

# 38. S1.7-D36 — Development memory timing

The development-memory projection is available once a result exists and grows deterministically as evaluation/rework/acceptance history appears.

After lifecycle reaches `ACCEPTED`, the projection must contain enough durable references to reconstruct:

```text
why this exact commit was accepted
what evidence supported the evaluator
what the evaluator decided
what the Human accepted
which governed execution created ACCEPTED state
what prior rework attempts existed
```

This projection is the M0 implementation of the roadmap's development-memory requirement.

---

# 39. S1.7-D37 — Expected schema/dependency/tooling impact

Expected:

```text
schema migration: YES — one bounded append-only migration
new runtime dependency: NONE
new dev/test dependency: NONE
lifecycle transition-matrix change: NONE
new external service: NONE
repository mutation: NONE
agent execution: NONE
```

The schema migration is justified by two currently required durable concepts that were explicitly deferred from earlier slices and cannot be encoded faithfully in existing typed tables.

Implementation authorization must explicitly include this migration. Design authorization alone does not permit applying it.

---

# 40. Expected implementation change surface

New production package:

```text
src/relay_engine/manual_evaluation/
    __init__.py
    errors.py
    models.py
    service.py
```

Expected bounded existing changes:

```text
src/relay_engine/domain/ids.py
src/relay_engine/governance/models.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/records.py          # only if shared durable record exports are useful
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
```

Narrow repository-baseline helper changes are allowed only if needed to reuse existing verified Baseline persistence without duplicating provider logic.

Tests may add dedicated unit/integration files.

A materially broader production surface requires escalation before implementation.

---

# 41. Required tests

Implementation must prove at minimum:

## Result subject

```text
exact result SHA resolves to immutable Baseline
result Baseline project/repository mismatch rejected
result attachment only in EVALUATING
stale lifecycle/definition/result CAS rejected
same-result retry idempotent
replacement before evaluation preserves prior result
replacement after evaluation in same attempt rejected
rework successor result preserves full lineage
orphan verified Baseline after local conflict is not accepted authority
```

## Manual evaluation

```text
EvaluationOutcome existing enum reused
server-bound HUMAN evaluator required
exact result/evidence commit binding
duplicate evidence rejected
missing/mismatched evidence rejected
first evaluation works without fabricated current assessment observation
current gate set/revision staleness rejected
evaluation successor chain deterministic
competing evaluator decision rejected
superseding evaluation increments governance revision exactly once
old Human decisions stale after new evaluation
manual evaluation + successor GateEvaluationRecord atomic rollback
```

## REWORK

```text
REWORK outcome alone does not move lifecycle
REWORK-target gate must exist
RED/YELLOW cannot execute
GREEN governed EVALUATING->REWORK works through existing path
prior result/evaluation immutable after rework
new result requires later EVALUATING attempt
```

## Human technical acceptance

```text
ACCEPT evaluator outcome required
technical acceptance bound exact result/evaluation
non-HUMAN actor rejected
stale HumanActionBasis rejected
new evaluator record stales old acceptance
Human REJECT preserves evaluator ACCEPT history
Human acceptance does not itself transition lifecycle
```

## Promotion

```text
generic Slice 1.6 ADVANCE still refuses ACCEPTED target
dedicated promotion requires exact current evaluator ACCEPT
current Human APPROVE required
selected ACCEPTED gate must be GREEN
complete gate set re-evaluated inside transaction
accepted execution atomic
no direct lifecycle ACCEPTED mutation
accepted Baseline derived from execution context result_baseline_id
moving branch does not change accepted Baseline
retry of exact already-accepted subject creates no duplicate execution
different-subject retry conflicts
corrupt ACCEPTED causal chain fails integrity validation
```

## Persistence/migration

```text
migration version/checksum deterministic
existing database upgrades cleanly
fresh database creates new tables/indexes/triggers
slice_results append-only triggers work
manual_evaluations append-only triggers work
indexed columns checked against typed payload
result/evaluation chain cycles/forks rejected
old GateEvaluationRecords without new optional context fields still load
```

## Board/HTTP

```text
pending result/evaluation/accepted states render correctly
exact provenance displayed
CSRF missing/invalid -> 403 and no write
actor never trusted from form
stale/conflict -> 409
invalid/unavailable -> 422
successful mutation -> 303 PRG
GET/HEAD never mutate
request-scoped DB ownership preserved
```

## Development memory

```text
projection deterministic
includes exact accepted commit/evidence/evaluator/Human/execution provenance
rework lineage retained
projection creates no repository mutation
```

All existing tests remain mandatory.

---

# 42. Quality gate for a future implementation candidate

A future authorized implementation candidate must pass the existing project quality contract, including:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

and successful GitHub Actions CI on the exact candidate SHA.

These are evidence, not acceptance.

---

# 43. Hard exclusions

Slice 1.7 design does not authorize implementation of:

```text
agent execution
AgentRuntime/OpenCode execution
autonomous evaluator agents
automatic acceptance from CI/tests
automatic Human approval
generic workflow engine
command bus
event bus
broad RBAC / organizations / multi-tenancy
repository-side development-memory mutation
repository/provider write operations for acceptance
branch merging or branch-head acceptance semantics
lifecycle transition-matrix redesign
new quality-tool framework
Phase 1 M0 dogfood validation
Phase 2 opening
Slice 2.1 work
unrelated UI or persistence refactoring
```

---

# 44. Implementation stop conditions

A future implementation agent must stop and escalate before continuing if the accepted implementation requires:

```text
a lifecycle transition-matrix change
an additional schema migration beyond the accepted bounded Slice 1.7 migration
a new runtime/dev dependency
new EvaluationOutcome values
a second Human-acceptance persistence system
a mutable accepted-baseline pointer
repository mutation to satisfy development memory
provider mutation beyond existing read/verification behavior
agent execution or autonomous evaluation
a generic workflow/orchestration framework
material production change-surface expansion
```

---

# 45. Acceptance matrix for this design

An independent design evaluator should require all of the following before recommending Human design acceptance:

```text
[ ] exact result commit subject is first-class and immutable
[ ] result history cannot be silently replaced
[ ] authored Evaluation is distinct from gate computation
[ ] existing EvaluationOutcome vocabulary is reused
[ ] evidence is exact-result-bound
[ ] evaluator decision never moves lifecycle directly
[ ] REWORK uses existing lifecycle/gates
[ ] Human technical acceptance is distinct from evaluator ACCEPT
[ ] existing HumanApprovalDecision is reused without weakening exact binding
[ ] Slice 1.6 generic ADVANCE remains unable to enter ACCEPTED
[ ] dedicated ACCEPTED promotion re-evaluates exact current GREEN gate
[ ] accepted Baseline is causally reconstructable from ACCEPTED execution
[ ] no moving ref can become acceptance authority
[ ] development memory requirement is satisfied without unauthorized repository mutation
[ ] stale/concurrent result/evaluation/Human commands fail closed
[ ] historical result/evaluation/rework provenance remains reconstructable
[ ] migration is minimal and presently justified
[ ] prior persisted GateEvaluationRecords remain backward-compatible
[ ] caller owns durable IDs/timestamps
[ ] board remains projection/control surface
[ ] no agent execution or Phase 2 scope is introduced
```

---

# 46. Resulting capability if implemented and accepted

After Slice 1.7 implementation and Human acceptance, Relay M0 will support the complete manual governed development loop:

```text
Human defines work
        ↓
Human authorizes execution/design as governed by gates
        ↓
external/manual work produces exact result commit
        ↓
Relay attaches exact result Baseline
        ↓
Human evaluator records evidence + technical outcome
        ↓
Relay deterministically derives current gate state
        ↓
Human Authority accepts exact evaluator ACCEPT/result
        ↓
Relay re-evaluates and executes exact GREEN ACCEPTED gate
        ↓
accepted Baseline is causally established
        ↓
development memory projection reconstructs why it was accepted
```

This completes the human-only loop while keeping agent execution unauthorized.

---

# 47. Hard stop after Slice 1.7

Even after Slice 1.7 closes:

```text
Phase 1 M0 validation
    remains a separate hard-stop experiment

Phase 2
    remains NOT OPEN until separately authorized

Agent execution
    remains NOT AUTHORIZED
```

The next action after a future Slice 1.7 closure is therefore not automatically AgentRuntime implementation. Relay must first pass the Phase 1 M0 manual-governance validation required by the canonical roadmap.

**Unblocked ≠ authorized. Evaluation ACCEPT ≠ Human acceptance. Human acceptance ≠ lifecycle execution.**
