# Slice 1.7 — Manual Evaluation and Acceptance — Revision 2 Amendment

**Document class:** Lockable design amendment  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Design authority:** `RLY-S17-DESIGN-AUTH-001 — AUTHORIZED`  
**Revision 1:** `a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6`  
**Prior independent evaluation:** `RLY-S17-DESIGN-EVAL-001 — REVISE`  
**Purpose:** Resolve findings F001–F004 without expanding the authorized Slice 1.7 boundary.

This amendment is normative over Revision 1 where they differ. Unmodified Revision 1 decisions remain in force.

---

# R2-D01 — Pending/current result identity becomes part of the exact Human Action Basis

Revision 1 correctly prohibited fabricating a GateEvaluationRecord merely because a result was attached. The missing requirement was a mechanical way to ensure an older Slice 1.6 action basis cannot remain valid after that attachment.

Extend the accepted Slice 1.6 `HumanActionBasis` backward-compatibly with:

```python
current_result_id: SliceResultId | None = None
current_result_baseline_id: BaselineId | None = None
current_manual_evaluation_id: ManualEvaluationId | None = None
```

The Human-control durable snapshot must also load the deterministic Slice 1.7 current-subject projection directly from persistence:

```text
current result chain tail for the Slice/current evaluation attempt
current result Baseline
current manual evaluation chain tail for that result, if one exists
```

The projection is current only when its lifecycle binding still identifies the exact current `EVALUATING` attempt. Historical result/evaluation records from prior lifecycle revisions are not current subject state.

The existing `_basis_for_snapshot` semantics are extended so that, in addition to the accepted Slice 1.6 checks, it requires:

```text
latest GateEvaluationRecord.context.result_id
    == durable current result ID

latest GateEvaluationRecord.context.result_baseline_id
    == durable current result Baseline ID

latest GateEvaluationRecord.context.manual_evaluation_id
    == durable current manual evaluation ID
```

with `None` equality when no current result exists.

Therefore:

```text
no current result
+ latest context has no Slice 1.7 subject
    -> ordinary Slice 1.6 exact basis may be valid

current result exists
+ no current evaluation / no successor GateEvaluationRecord
    -> HumanActionRequiresEvaluation
    -> no gate-affecting HumanActionBasis

current result + current evaluation exist
+ latest GateEvaluationRecord projects both exactly
    -> exact HumanActionBasis may be valid
```

This is a service-level invariant, not merely a board-rendering rule.

Direct Slice 1.6 gate-affecting service calls and POST routes must fail closed on the same mismatch.

Existing Human BLOCK / PAUSE / DEFER / CLEAR_HOLD behavior may remain available according to its accepted basis-independent rules.

No fake GateEvaluationRecord is created on result attachment.

---

# R2-D02 — Human-control integration is a bounded authorized change surface

Revision 1's expected change surface is amended to include narrow changes to:

```text
src/relay_engine/human_control/models.py
src/relay_engine/human_control/service.py
```

The only authorized reason is to incorporate the current Slice 1.7 result/evaluation subject into exact Human Action Basis projection and validation.

This does **not** authorize redesign of Slice 1.6 commands, authorization semantics, decision projection, or blockage behavior.

The Human-control layer should depend only on narrow persistence loaders/current-subject values, not on board rendering or a generalized manual-evaluation framework.

---

# R2-D03 — Evidence submission is part of the manual-evaluation command

Slice 1.7 does not introduce generic Evidence CRUD.

Instead, `record_manual_evaluation(...)` accepts a bounded evidence submission alongside any already-existing Evidence references.

Conceptually:

```python
EvaluationEvidenceSubmission(
    evidence_id,
    claim,
    recorded_at,
)
```

The application boundary generates `EvidenceId` and timestamp. The form/user supplies only the claim text; actor and source commit are server-derived.

For every new evidence submission, the service constructs:

```python
Evidence(
    id=submission.evidence_id,
    claim=submission.claim,
    recorded_by=manual_evaluator_actor,
    recorded_at=submission.recorded_at,
    source_commit=current_result_baseline.commit,
)
```

Normative rules:

```text
evidence_id is caller-owned and explicit
claim is nonblank
recorded_at timezone-aware and non-regressing
recorded_by cannot come from form input
source_commit cannot come from form input
source_commit is always the exact current result Baseline commit
```

The evaluation command may also reference existing Evidence IDs. Existing records must load successfully and must have:

```text
Evidence.source_commit == current result Baseline commit
```

After combining newly submitted and existing Evidence, the canonical evaluation evidence set must be:

```text
non-empty
unique by EvidenceId
sorted deterministically by EvidenceId
```

Thus every `ManualEvaluationRecord` references at least one durable Evidence record, satisfying the roadmap exit bar.

A human reviewer observation may itself be entered as an Evidence claim when no automated check exists.

---

# R2-D04 — Evidence + authored evaluation + successor gate observation are one SQLite transaction

After the exact current result/basis is revalidated, `record_manual_evaluation(...)` performs in one caller-owned write transaction:

```text
1. load/validate any referenced existing Evidence
2. validate each new Evidence submission
3. insert new Evidence records
4. append ManualEvaluationRecord referencing the canonical complete Evidence ID set
5. construct exact successor HandoverContext
6. evaluate the complete current outgoing gate set
7. append successor GateEvaluationRecord
8. commit
```

If any later step fails, no new Evidence from that request remains durable.

Existing Evidence supplied by ID is, of course, not removed on rollback because it predates the request.

Same-identity retry rules follow existing Relay immutable-record semantics:

```text
same EvidenceId + byte-identical typed Evidence already durable
    -> may be treated as idempotent input

same EvidenceId + conflicting content/provenance
    -> integrity/conflict failure
```

The command must not silently mint replacement Evidence IDs.

---

# R2-D05 — Technical acceptance is mandatory independent of generic handover policy

Slice 1.7 technical acceptance is a dedicated semantic command and is available for every exact current gate targeting `LifecyclePhase.ACCEPTED` when the current manual evaluation outcome is `ACCEPT`.

Its availability does **not** depend on whether that gate's generic `HandoverPolicy` is `AUTO`, `AUTO_NOTIFY`, `HUMAN_APPROVAL`, or `HUMAN_CHOICE`.

The command reuses the accepted durable model:

```text
HumanApprovalDecision(APPROVE | REJECT)
```

but Slice 1.7 owns the **technical-acceptance availability rule**.

Therefore it need not call Slice 1.6 `record_gate_approval()` if that service rejects a gate for which ordinary approval is not required. It may reuse the same accepted transaction/projection helpers or the minimum shared internal logic necessary to persist the exact decision and successor GateEvaluationRecord.

Normative behavior:

```text
TECHNICAL_ACCEPT
    -> append current HumanApprovalDecision(APPROVE)

TECHNICAL_REJECT
    -> append current HumanApprovalDecision(REJECT)
```

Both decisions bind:

```text
slice
source/authority baseline
exact ACCEPTED gate/revision
current lifecycle revision
current governance revision
server-bound Human Authority actor
explicit caller-owned decision ID/time
reason
```

and are additionally validated against the submitted/current:

```text
result_id
result_baseline_id
manual_evaluation_id
```

via the exact GateEvaluationRecord/HumanActionBasis described in R2-D01.

A current `REJECT` keeps the ACCEPTED gate RED through existing `HUMAN_REJECTED` semantics.

A current `APPROVE` is required by `promote_accepted_result(...)` even if the generic gate would otherwise be GREEN under `AUTO`.

Hence:

```text
generic gate policy may determine normal autonomy

but

Slice 1.7 accepted-baseline promotion always requires explicit current Human technical acceptance
```

No new acceptance table is introduced.

---

# R2-D06 — Successor HandoverContext is reconstructed from exact current durable facts

A manual evaluation must not copy a stale prior-lifecycle `HandoverContext` wholesale.

Inside the same evaluator write transaction, Relay reconstructs every independently queryable current durable fact:

```text
baseline_id
    = exact source/authority baseline shared by the complete current outgoing gate set

lifecycle
    = exact current SliceLifecycle

available_artifact_ids
    = exact current result Baseline.artifact_ids

available_evidence_ids
    = canonical Evidence IDs referenced by the new current ManualEvaluationRecord

dependency_lifecycles
    = current SliceLifecycle values freshly loaded for every declared dependency Slice
    = canonical order by dependency SliceId

authorization_grants
    = accepted deterministic current Slice 1.6 authorization projection for current gates

human_decisions
    = accepted deterministic current Slice 1.6 Human-decision projection for current gates

result_id
    = exact current SliceResultRecord.result_id

result_baseline_id
    = exact current SliceResultRecord.result_baseline_id

manual_evaluation_id
    = newly appended current ManualEvaluationRecord.evaluation_id
```

The evaluator-authored assessment facts are:

```text
evaluation_outcome
quality_checks
change_surface_status
risk_status
toolchain_change_status
```

`governance_revision` is the Revision 1 monotonic predecessor plus exactly one.

No prior context field is copied merely because it existed before the lifecycle/result changed.

This design intentionally gives `available_artifact_ids` the meaning:

> artifact revisions actually present in the exact evaluated result Baseline.

It does **not** mean the source Baseline's old artifact list.

If an accepted contract artifact changed or disappeared in the result and the current gate requires the prior exact ArtifactId, deterministic gate evaluation may become RED. That is preferable to silently claiming the old artifact remains present in the result.

---

# R2-D07 — Dependency projection must be complete, current, and fail closed

For each dependency ID declared by the current Slice definition:

- load the current dependency lifecycle inside the same transaction/snapshot;
- include it exactly once in `dependency_lifecycles`;
- canonicalize by `slice_id`.

If a declared dependency no longer exists or lacks initialized lifecycle state, do not fabricate a placeholder current lifecycle. The successor context must reflect absence in the same deterministic manner already expected by gate evaluation; implementation may either omit the unavailable dependency so the gate produces `DEPENDENCY_MISSING`, or use the existing accepted representation if one already exists at implementation time.

The design must not carry forward a dependency lifecycle from a stale previous GateEvaluationRecord as current truth.

---

# R2-D08 — First evaluation still does not require a current prior GateEvaluationRecord

Revision 1 D15 remains in force, with one clarification.

The evaluator form carries:

```text
expected latest durable GateEvaluationRecord ID or explicit NONE
```

That identity is a concurrency sentinel only when it belongs to an older lifecycle/result basis.

The newly constructed successor context is derived according to R2-D06, not copied from that older record.

If a newer GateEvaluationRecord appears before commit, evaluation fails stale/conflict.

---

# R2-D09 — Current result/evaluation projection definition

The deterministic current Slice 1.7 subject is now defined precisely.

For a Slice whose current lifecycle phase is `EVALUATING`:

1. consider `SliceResultRecord` rows whose `lifecycle_revision` equals the current lifecycle revision;
2. validate their explicit supersession chain;
3. the unique chain tail is the current result;
4. consider `ManualEvaluationRecord` rows whose `result_id` equals that current result and whose lifecycle revision matches;
5. validate their explicit supersession chain;
6. the unique chain tail is the current manual evaluation, if any.

For lifecycle phases other than `EVALUATING`, these records are historical and the **current evaluation subject** is absent.

Historical accepted-result projection is separately reconstructed from the governed ACCEPTED execution and remains available even after a later `ACCEPTED -> SUPERSEDED` transition.

This last rule ensures accepted provenance does not disappear merely because a formerly accepted Slice is later superseded.

---

# R2-D10 — Accepted-result projection remains historical after supersession

Revision 1 D23 is clarified.

`AcceptedSliceResult` is reconstructable whenever a Slice history contains a valid governed execution whose target lifecycle phase was `ACCEPTED`, even if the Slice's current phase is later `SUPERSEDED`.

For a currently `ACCEPTED` Slice, that chain is the current accepted result.

For a `SUPERSEDED` Slice, the same chain is historical accepted provenance.

The subsequent supersession does not change or replace the accepted Baseline that was established by the earlier ACCEPTED execution.

---

# R2-D11 — Updated implementation change surface

Revision 1's expected production change surface is amended to:

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
src/relay_engine/persistence/records.py       # if shared exports/records are mechanically useful
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
```

Narrow repository-baseline changes remain allowed only when mechanically required to reuse existing exact Baseline verification/persistence.

No additional package, dependency, framework, or lifecycle transition change is expected.

---

# R2-D12 — Added required tests

In addition to Revision 1 tests, implementation must prove:

```text
pending current result makes prior HumanActionBasis invalid
pending current result blocks direct Slice 1.6 gate-affecting service calls
pending current result blocks direct Slice 1.6 gate-affecting POST calls
hold/blockage commands retain accepted basis-independent behavior
matching current result + evaluation + GateEvaluationRecord restores exact HumanActionBasis
old GateEvaluationRecords with no result fields remain compatible when no current result exists

manual evaluation can atomically create new Evidence
new Evidence actor is always server-bound evaluator
new Evidence source_commit is always current result commit
form cannot forge Evidence actor/source commit
existing Evidence from a different result commit is rejected
zero-evidence ManualEvaluationRecord is rejected
Evidence insertion rolls back when evaluation or successor GateEvaluationRecord fails

technical ACCEPT/REJECT is available for an AUTO ACCEPTED-target gate
generic AUTO GREEN never bypasses required technical APPROVE in promotion
technical REJECT makes ACCEPTED gate RED
new evaluation stales prior technical acceptance

successor context available artifacts equal result Baseline artifacts
successor dependencies are freshly loaded current lifecycles
stale prior-lifecycle dependency/artifact observations are not copied
current grants/decisions use accepted deterministic projection
assessment fields come from evaluator input rather than stale context copying

accepted-result projection remains reconstructable after Slice supersession
```

---

# R2-D13 — Resolution of independent review findings

```text
RLY-S17-DESIGN-EVAL-001 / F001
RESOLVED by R2-D01, R2-D02, R2-D09

RLY-S17-DESIGN-EVAL-001 / F002
RESOLVED by R2-D03, R2-D04

RLY-S17-DESIGN-EVAL-001 / F003
RESOLVED by R2-D05

RLY-S17-DESIGN-EVAL-001 / F004
RESOLVED by R2-D06, R2-D07, R2-D08
```

All other Revision 1 decisions remain normative.

## Gate state

```text
Slice 1.7:
OPEN

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6

Revision 2 amendment:
THIS COMMIT SUBJECT

Prior independent design evaluation:
RLY-S17-DESIGN-EVAL-001 — REVISE

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Evaluation evidence remains distinct from Human acceptance. Design correction remains distinct from implementation authority.**
