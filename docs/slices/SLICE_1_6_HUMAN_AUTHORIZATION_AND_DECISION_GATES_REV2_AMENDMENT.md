# Slice 1.6 — Human Authorization and Decision Gates — Revision 2 Amendment

**Status:** DESIGN REVISION 2 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design record  
**Human version:** Revision 2 Amendment  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Design authority:** `RLY-S16-DESIGN-AUTH-001`  
**Human-authorized design subject baseline:** `e9c6e3a5cc7592764bf0ac4932a2ae2659644027`  
**Authority-recording design parent:** `e4923c837f20de35eb96cd1caf615b86860d9222`  
**Revision 1:** `f3a0fa7d9cc5b344399c070406353e1107ec30ff`  
**Independent Revision-1 review:** `RLY-S16-DESIGN-EVAL-001 — REVISE`  
**Review record commit:** `2b4c4d0677813cbcf64f3bf1120075f56574d081`  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-10-03

Revision 1 remains historical design evidence. This amendment is normative wherever it replaces or qualifies Revision 1.

---

# 1. Purpose

Resolve all findings from `RLY-S16-DESIGN-EVAL-001` without widening Slice 1.6.

The architecture remains:

```text
accepted durable governance/lifecycle state
        ↓
small human-control application service
        ↓
request-scoped mutation adapter on Slice detail
        ↓
durable decision / authorization / lifecycle evidence
        ↓
deterministic stored gate-evaluation observation
        ↓
Slice 1.5 projection
```

No generic workflow engine, new frontend stack, broad identity system, AgentRuntime implementation, or Slice 1.7 behavior is introduced.

---

# 2. R2-D01 — Define a stronger Human Action Basis

Revision 1's `EvaluationBasisStatus.MATCHING_DURABLE_BASIS` remains a Slice 1.5 **structural observation** classification. It is intentionally not sufficient by itself to authorize a mutation.

Slice 1.6 introduces a bounded service/presentation value conceptually:

```text
HumanActionBasis
    evaluation_record_id
    slice_id
    baseline_id
    lifecycle_revision
    governance_revision
    gate_refs
    current_approval_decision_ids
    current_choice_decision_id
```

The exact serialization shape may be normalized, but its semantics are fixed.

A gate-affecting Human Authority mutation is eligible only when:

1. the referenced evaluation record is the latest durable evaluation record for the Slice by persistence sequence;
2. its current lifecycle snapshot exactly matches durable lifecycle state;
3. its exact gate-revision set is still the current outgoing gate set;
4. its baseline is still the exact current gate baseline;
5. the authorization and human-decision projection in its `HandoverContext` agrees with the deterministic current durable projection defined below;
6. the submitted expected current decision identities agree with the same projection.

Mismatch returns stale/conflict. The service never rebases the command to a newer observation silently.

The basis token is an optimistic-concurrency expectation, not authority by itself.

---

# 3. R2-D02 — Current durable human-evidence projection

Slice 1.6 now owns the explicit current-selection policy that Slice 0.5 intentionally deferred.

## 3.1 Authorization grants

Authorization is durable positive permission. Revocation/expiry remain out of scope.

For one exact current gate basis:

```text
slice_id
baseline_id
gate_id
gate_revision
```

all matching grants express the same positive permission.

The product service MUST treat AUTHORIZE as target-state idempotent when any exact matching grant already exists.

If redundant exact matching durable grants exist from legacy/direct persistence, the context projector selects the earliest established permission deterministically:

```text
least granted_at
then least authorization_id
```

A later redundant grant does not replace or delay an already-active permission.

This replaces Revision 1 S16-D12's latest-wins rule for authorization.

## 3.2 Approval decisions

For each current logical gate ID, the relevant durable approval history is ordered by:

```text
occurred_at
then decision_id
```

The greatest pair is the projected current approval/rejection evidence for that logical gate, including when it is stale relative to the current lifecycle/governance revision. Supplying stale latest evidence allows the accepted gate engine to explain `HUMAN_DECISION_STALE` rather than erasing history from the projection.

## 3.3 Choice decisions

The relevant durable choice history for the Slice is ordered by:

```text
occurred_at
then decision_id
```

The greatest pair is the projected current choice evidence. The accepted gate engine determines whether that choice is current for the exact outgoing choice set or stale.

## 3.4 Product chronology

A materially new approval/choice submitted through Slice 1.6 must not use an `occurred_at` earlier than the currently projected decision it is replacing.

The local web adapter generates UTC occurrence times. Tests and non-web callers may inject explicit times, but the service enforces non-regression.

---

# 4. R2-D03 — AUTHORIZE atomically advances the governance basis

This resolves `RLY-S16-DESIGN-EVAL-001/F001`.

Accepted Slice 0.4 semantics require an authorization-projection change to advance `governance_revision`.

Therefore a new Slice 1.6 AUTHORIZE operation requires an exact matching Human Action Basis and performs one write transaction:

```text
load latest exact evaluation observation
        ↓
recheck current lifecycle / gate refs / baseline / human evidence
        ↓
prove no exact current grant already exists
        ↓
insert AuthorizationGrant
        ↓
new governance_revision = previous + 1
        ↓
construct successor HandoverContext
        ↓
deterministically evaluate complete current gate set
        ↓
append successor GateEvaluationRecord
        ↓
COMMIT
```

The successor context:

- preserves the prior evaluation's non-human assessment facts;
- contains the new deterministic current authorization projection;
- contains the latest relevant human-decision projection;
- increments `governance_revision` exactly once;
- keeps the same lifecycle revision;
- naturally makes prior revision-bound approval/choice decisions stale.

The caller supplies explicit new `authorization_id`, successor `evaluation_record_id`, grant time, and evaluation-record time. Required causal order is:

```text
prior evaluation recorded_at
    <= grant granted_at
    <= successor evaluation recorded_at
```

If an exact matching grant already exists, AUTHORIZE is a no-op success and appends neither grant nor evaluation record.

If no current full evaluation basis exists, AUTHORIZE returns `HumanActionRequiresEvaluation`; it does not invent current assessment facts.

A gate may still be RED for non-authority reasons while accepting durable authorization. The pre-action observation must simply be current and complete enough to advance its governance basis deterministically.

No new table is required: the successor `GateEvaluationRecord` is the durable observation carrying the new caller-maintained governance revision.

---

# 5. R2-D04 — APPROVE / REJECT / CHOOSE_PATH atomically append successor evaluation evidence

This resolves `RLY-S16-DESIGN-EVAL-001/F002`.

Human decisions do **not** increment `governance_revision` under accepted Slice 0.4 semantics.

A materially new approval/rejection/choice therefore performs one write transaction:

```text
load latest exact Human Action Basis
        ↓
recheck current durable human evidence
        ↓
compare expected current decision identity
        ↓
insert HumanApprovalDecision or HumanChoiceDecision
        ↓
construct successor context at SAME governance_revision
        ↓
replace projected current human decision with new durable decision
        ↓
deterministically evaluate complete current gate set
        ↓
append successor GateEvaluationRecord
        ↓
COMMIT
```

Required causal order:

```text
prior evaluation recorded_at
    <= decision occurred_at
    <= successor evaluation recorded_at
```

The successor evaluation record makes the resulting GREEN/YELLOW/RED value durable evidence.

The Slice 1.5 board continues to display **stored observations only**. Slice 1.6 does not overwrite `GateProjection.evaluation_light` with an unrecorded live recomputation.

A same-target exact-basis retry may return no-op success without another decision/evaluation pair.

---

# 6. R2-D05 — Decision replacement uses explicit optimistic concurrency

This resolves `RLY-S16-DESIGN-EVAL-001/F004`.

Because human decisions do not increment lifecycle or governance revision, the action basis additionally carries expected current decision identity.

Approval/rejection command:

```text
expected_current_approval_decision_id: HumanDecisionId | None
```

Choice command:

```text
expected_current_choice_decision_id: HumanDecisionId | None
```

Inside the write transaction, the service recomputes the deterministic current durable selection.

Behavior:

```text
expected == actual current decision
    -> materially different valid decision may append

requested target already equals actual current decision on exact basis
    -> no-op success

expected != actual and requested target differs
    -> HumanActionConflict / HTTP 409
```

Thus a stale browser view cannot silently reverse a decision it never observed.

---

# 7. R2-D06 — Every gate-affecting action names the exact observed evaluation

AUTHORIZE, APPROVE, REJECT, CHOOSE_PATH, ADVANCE, and CANCEL include:

```text
expected_evaluation_record_id
```

The service requires it to equal the latest durable evaluation record for the Slice and to satisfy the Human Action Basis checks.

If a newer gate assessment arrives—even with the same lifecycle phase and same gate IDs—the stale form cannot act on the older observation.

This is especially important for assessment facts such as:

- quality checks;
- evaluation outcome;
- change-surface status;
- risk status;
- toolchain-change status.

---

# 8. R2-D07 — CANCEL is governed handover execution, never a direct phase mutation

This resolves `RLY-S16-DESIGN-EVAL-001/F003` and replaces Revision 1 S16-D10.

Slice 0.4 remains authoritative:

```text
lifecycle movement
    -> HandoverGate
    -> selected + GREEN
    -> lifecycle engine
```

The Slice 1.6 `CANCEL` product action is a specialized execution request for an exact current outgoing gate whose target is:

```text
LifecyclePhase.CANCELLED
```

Requirements:

- exact current cancellation gate exists;
- submitted gate ID/revision belongs to the current gate set;
- expected evaluation record is the latest Human Action Basis;
- current durable authorization/decisions are exactly the projected basis;
- deterministic re-evaluation inside the write transaction returns GREEN for the selected cancellation gate;
- governed execution records the evaluation/event/execution causality atomically.

If the cancellation gate is YELLOW, the human first performs the required AUTHORIZE / APPROVE / CHOOSE_PATH action. If RED, ordinary product cancellation is unavailable.

If no current cancellation gate exists, Slice 1.6 does not manufacture one and does not call `transition_phase(CANCELLED)` directly.

A browser retry that observes an already-CANCELLED Slice may return target-state no-op without manufacturing a second execution record.

---

# 9. R2-D08 — ADVANCE uses only the latest persisted full human basis

Revision 1 S16-D11 is retained and tightened.

ADVANCE requires the exact latest Human Action Basis and selected gate ID/revision.

Inside the same write transaction the execution path must:

1. reload current lifecycle/gate revisions/baseline;
2. reload deterministic current authorization and human-decision projections;
3. prove they equal the latest evaluation context's human projection;
4. re-run accepted deterministic gate evaluation;
5. require selected gate GREEN;
6. call the accepted governed lifecycle execution path exactly once;
7. atomically persist execution evaluation, lifecycle event/current snapshot, and execution record.

A newer durable REJECT/choice can therefore never be bypassed by passing an older still-durable APPROVE.

The Slice 1.6 UI still refuses ADVANCE for a gate targeting `ACCEPTED`. That remains Slice 1.7 authority.

---

# 10. R2-D09 — Human hold controls are bounded lifecycle controls

Revision 1 BLOCK / PAUSE / DEFER / clear-hold direction is retained with these clarifications.

## Availability

BLOCK / PAUSE / DEFER are available only in phases accepted by the lifecycle engine as blockable.

No Slice 1.6 service catches `InvalidLifecycleOperation` and pretends a non-blockable phase may be held.

## Meaning

```text
HUMAN_BLOCK   -> explicit human blocker
HUMAN_PAUSE   -> indefinite human-requested temporary stop
HUMAN_DEFER   -> indefinite human-requested deferral
```

PAUSE and DEFER have no scheduler, due date, notification, or automatic resume semantics in Slice 1.6.

## Reason ordering

When setting one Human hold:

1. preserve unrelated existing `BlockReason` values in their durable order;
2. remove any prior Slice-1.6 reserved human-control reasons;
3. append the one new Human hold reason last.

This produces deterministic replayable blockage values.

## Clear hold

`CLEAR_HOLD` / UI label `Resume` removes only:

```text
HUMAN_BLOCK
HUMAN_PAUSE
HUMAN_DEFER
```

If unrelated reasons remain, blockage remains BLOCKED with their prior order. If none remain, accepted `clear_blockage(...)` semantics apply.

## Observation behavior

A hold/clear-hold advances lifecycle revision, so all old revision-bound human decisions become stale automatically.

If the command started from a latest exact Human Action Basis, implementation may append a successor deterministic `GateEvaluationRecord` in the same transaction because:

- phase/gate set remains unchanged;
- the command itself changes only the lifecycle snapshot;
- all other observation facts are preserved from the exact pre-action context.

If no exact current evaluation basis exists, the human hold may still be persisted, but Slice 1.6 must not fabricate an evaluation from unknown assessment facts. The board then truthfully reports the prior observation as stale until another governed evaluation is recorded.

This conditional successor observation is bounded to hold/clear-hold because they do not change lifecycle phase or gate set.

---

# 11. R2-D10 — Authorization-record roadmap mapping is explicit

This resolves `RLY-S16-DESIGN-EVAL-001/F006` without duplicating accepted data.

The older roadmap's required authorization-record fields map to accepted Relay authority as follows:

```text
actor
    -> AuthorizationGrant.actor

timestamp
    -> AuthorizationGrant.granted_at

target slice
    -> AuthorizationGrant.slice_id

baseline
    -> AuthorizationGrant.baseline_id
    -> Baseline.commit is the exact immutable code commit

contract version
    -> AuthorizationGrant.gate_id + gate_revision
    -> exact immutable HandoverGate revision

artifact / decision versions
    -> Baseline.artifact_ids + decision_ids
    -> Artifact values carry exact commit + content digest

scope
    -> permission to execute that exact gate revision
       for that exact Slice and Baseline

decision
    -> existence of the positive AuthorizationGrant
       (execution-time APPROVE / REJECT remains HumanApprovalDecision)

reason
    -> AuthorizationGrant.reason
```

The product should display the relevant baseline/gate identity near AUTHORIZE so the human can see what exact authority is being granted.

No duplicate free-text scope or copied artifact-version fields are added to `AuthorizationGrant`.

---

# 12. R2-D11 — M0 role permission means explicit Human Authority principal

The detailed roadmap requires role permissions to be enforced.

Relay currently has accepted actor kinds, not a multi-user RBAC model.

For Slice 1.6 M0:

```text
configured application Human Authority principal
    = ActorRef(kind=HUMAN)
```

All human-control service commands require that actor kind exactly.

```text
ActorKind.SYSTEM -> forbidden
ActorKind.AGENT  -> forbidden
```

The web form cannot supply or override actor identity.

This is the complete current role-permission boundary. It does not claim authentication, organizations, multiple human roles, or remote-user authorization.

Those remain later product/security work unless separately authorized.

---

# 13. R2-D12 — Revised action/evaluation service contract

Revision 1 service names remain acceptable, with these normative additions.

Gate-affecting commands carry exact observation identity and explicit successor evaluation provenance:

```text
grant_gate_authorization(
    ...,
    expected_evaluation_record_id,
    authorization_id,
    granted_at,
    successor_evaluation_record_id,
    successor_evaluation_recorded_at,
)

record_gate_approval(
    ...,
    expected_evaluation_record_id,
    expected_current_approval_decision_id,
    decision_id,
    occurred_at,
    successor_evaluation_record_id,
    successor_evaluation_recorded_at,
)

record_gate_choice(
    ...,
    expected_evaluation_record_id,
    expected_current_choice_decision_id,
    decision_id,
    occurred_at,
    successor_evaluation_record_id,
    successor_evaluation_recorded_at,
)

advance_green_handover(
    ...,
    expected_evaluation_record_id,
    selected_gate_id,
    selected_gate_revision,
)

cancel_via_green_handover(
    ...,
    expected_evaluation_record_id,
    selected_gate_id,
    selected_gate_revision,
)
```

Exact parameter grouping may use small typed request values for clarity. The implementation must not create a generic command bus.

Human hold/clear commands remain lifecycle-revision CAS operations and may optionally receive the current evaluation ID solely to enable the bounded successor-observation behavior from R2-D09.

---

# 14. R2-D13 — Revised persistence expectations

The expected schema remains unchanged.

```text
SQLite migration:
NONE
```

Required narrow persistence support may include:

```text
load_authorization_grants_for_slice_from_connection(...)
load_human_decisions_for_slice_from_connection(...)
insert_authorization_grant_from_connection(...)
insert_human_decision_from_connection(...)
load_latest_gate_evaluation_for_slice_from_connection(...)
insert_gate_evaluation_record_from_connection(...)
```

and a bounded extension/refactor of governed execution so latest-current human-evidence proof occurs in the same write transaction before execution.

All helpers must preserve typed payload/index integrity checks.

No new repository abstraction, ORM, unit-of-work framework, or event bus is authorized.

---

# 15. R2-D14 — Revised board semantics

The Slice 1.5 gate observation contract remains unchanged:

> `GateProjection.evaluation_light` is a durable stored observation, not an unrecorded live truth.

HumanActionProjection may explain which Human Authority action is available on that exact observation basis, but it does not overwrite the gate light.

Because gate-affecting Slice 1.6 decisions append successor evaluation records atomically, ordinary POST-Redirect-GET returns a Slice detail whose latest stored observation already includes the accepted human evidence change.

A stale/conflicting action never creates a replacement observation.

---

# 16. R2-D15 — Revised deterministic tests

In addition to Revision 1 tests, implementation must prove:

## Governance revision causality

- AUTHORIZE with no current grant increments governance revision exactly once;
- grant + successor evaluation are one atomic commit;
- old approval/choice becomes stale after authorization revision advance;
- exact repeated AUTHORIZE is no-op and does not increment again;
- AUTHORIZE without exact current evaluation basis fails without write.

## Successor observation

- APPROVE appends decision + successor GREEN/YELLOW/RED evaluation atomically;
- REJECT appends decision + successor RED evaluation atomically;
- CHOOSE_PATH appends decision + complete-gate-set evaluation atomically;
- decision mutation keeps governance revision unchanged;
- board GET after successful PRG consumes the successor stored observation, not an unrecorded recomputation.

## Decision CAS

- opposite approval from stale expected decision ID returns conflict;
- different path from stale expected choice ID returns conflict;
- same-target retry is no-op;
- product decision time cannot regress;
- equal timestamps use decision ID only as deterministic tie-break.

## Authorization selection

- exact matching existing grant makes AUTHORIZE idempotent;
- redundant matching legacy grants project earliest permission;
- later duplicate grant does not move permission time forward.

## Cancellation

- cancellation without current cancellation gate is unavailable;
- YELLOW/RED cancellation gate cannot execute;
- GREEN cancellation gate uses governed execution and records evaluation/event/execution causality;
- no Slice 1.6 code directly phase-transitions to CANCELLED outside governed execution.

## Holds

- non-blockable phases reject hold actions;
- unrelated blocker ordering is preserved;
- exactly one reserved Human hold is appended last;
- PAUSE/DEFER do not schedule future work;
- clear-hold leaves unrelated blockers unchanged;
- lifecycle revision change stales old decisions;
- optional successor evaluation is written only when the pre-action full basis was exact.

## Principal boundary

- HUMAN configured actor accepted;
- SYSTEM/AGENT actor rejected before durable mutation;
- form actor fields cannot override configured principal.

---

# 17. Resolution matrix

```text
F001 governance_revision causality
    -> RESOLVED by R2-D01, D03, D06, D12, D13, D15

F002 durable successor gate observation
    -> RESOLVED by R2-D04, D14, D15

F003 CANCEL bypasses gate governance
    -> RESOLVED by R2-D07, D08, D12, D15

F004 stale-view decision replacement
    -> RESOLVED by R2-D01, D02, D05, D06, D12, D15

F005 authorization latest-wins semantics
    -> RESOLVED by R2-D02, D03, D15

F006 authorization-record / role-permission mapping
    -> RESOLVED by R2-D10, D11, D15
```

---

# 18. Preserved implementation boundary

Expected new production package remains:

```text
src/relay_engine/human_control/
    __init__.py
    errors.py
    models.py
    service.py
```

Expected bounded existing-file changes remain:

```text
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
```

A tiny change to an existing persistence record/export module is permitted only if mechanically required for the accepted transaction contract.

Still expected:

```text
new runtime dependencies: NONE
schema migration: NONE
```

Still out of scope:

- governance/lifecycle redesign;
- direct lifecycle phase bypass around gates;
- repository/provider mutation;
- AgentRuntime/OpenCode implementation;
- React/Node/new frontend toolchain;
- authentication/organizations/general RBAC;
- generic workflow/command framework;
- manual evaluation/technical acceptance/baseline promotion from Slice 1.7;
- agent execution.

---

# 19. Review handoff

```text
Combined design subject:
Revision 1
f3a0fa7d9cc5b344399c070406353e1107ec30ff
+
Revision 2 Amendment
<this amendment commit>

Next role:
Independent Slice 1.6 Design Reviewer

Outcome vocabulary:
ACCEPT / REVISE / ESCALATE
```

Human design acceptance and implementation authorization remain separate later gates.

**Unblocked ≠ authorized.**
