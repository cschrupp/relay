# Slice 1.6 — Independent Design Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Evaluation ID:** `RLY-S16-DESIGN-EVAL-001`  
**Outcome:** `REVISE`  
**Authority:** `RLY-S16-DESIGN-AUTH-001`  
**Human-authorized design subject baseline:** `e9c6e3a5cc7592764bf0ac4932a2ae2659644027`  
**Authority-recording design parent:** `e4923c837f20de35eb96cd1caf615b86860d9222`  
**Evaluated design candidate:** `f3a0fa7d9cc5b344399c070406353e1107ec30ff`  
**Reviewer role:** Independent Slice 1.6 Design Reviewer — GPT-5.6 Sol

## Decision

```text
REVISE
```

Revision 1 has the correct overall architecture: it reuses accepted governance values, keeps decision evidence distinct from lifecycle execution, preserves Slice 1.7 and agent-execution boundaries, retains server-rendered/local architecture, and avoids a speculative workflow framework.

However, several accepted governance invariants are not yet fully preserved by the proposed mutation contract.

---

## F001 — BLOCKING — AUTHORIZE does not preserve governance-revision causality

Accepted Slice 0.4 semantics require `governance_revision` to advance whenever a gate-relevant non-human-decision fact changes without a lifecycle revision change. The accepted design explicitly includes the **authorization projection** in that set.

Revision 1 creates a durable `AuthorizationGrant`, but it does not define how the current `governance_revision` advances or how that successor basis becomes durable/inspectable.

Consequences include:

- a pre-authorization approval/choice could remain bound to the old revision without an explicit successor basis;
- later HumanDecision creation has no unambiguous current governance revision to bind to;
- persisted execution could receive a caller-selected revision rather than a causally advanced one.

### Required revision

For the Slice 1.6 product path, `AUTHORIZE` must require an exact latest durable full-basis gate-evaluation observation suitable for mutation. In the same write transaction it must:

1. prove the current gate/baseline/lifecycle and current durable human-evidence projection still match that observation;
2. append the `AuthorizationGrant`;
3. advance `governance_revision` exactly once;
4. construct a successor `HandoverContext` with the new grant and prior human decisions now naturally stale by revision where applicable;
5. deterministically re-evaluate the complete current outgoing gate set;
6. append a successor `GateEvaluationRecord` with that new context/evaluation tuple.

No new schema is required if the successor evaluation record is the durable observation of the new governance basis.

If there is no suitable matching evaluation basis, `AUTHORIZE` must not guess one.

---

## F002 — BLOCKING — Gate-affecting human decisions leave the Slice 1.5 displayed observation stale

Revision 1 appends APPROVE / REJECT / CHOOSE_PATH decisions but does not append a successor deterministic gate-evaluation observation.

Slice 1.5 deliberately displays durable stored gate observations and does not present an unrecorded recomputation as current gate truth. Therefore POST-Redirect-GET after an approval could still display the pre-decision YELLOW light even though current durable human evidence would change deterministic evaluation.

### Required revision

APPROVE, REJECT, and CHOOSE_PATH must atomically append:

```text
human decision
+
successor GateEvaluationRecord
```

The successor evaluation:

- keeps the same lifecycle revision;
- keeps the same `governance_revision` because human decisions do not advance it;
- preserves the latest accepted non-human observation facts;
- replaces the current human-decision projection with the newly current durable decision selection;
- re-evaluates the complete exact current gate set.

This preserves Slice 1.5's observation semantics while making the redirected board immediately truthful about the latest recorded basis.

---

## F003 — BLOCKING — Direct CANCEL bypasses accepted handover-gate authority

Revision 1 proposes direct `transition_phase(..., CANCELLED)` + lifecycle persistence.

Accepted Slice 0.4 architecture is explicit:

```text
requested lifecycle movement
        -> Handover Gate
        -> governance evaluation
        -> selected + GREEN
        -> lifecycle engine
```

A direct product cancellation transition would bypass gate revision, prerequisites, policy, hard-stop semantics, and execution evidence for a lifecycle movement.

Cancellation is structurally legal in the lifecycle engine, but structural legality is not current governance permission.

### Required revision

`CANCEL` must be a specialized governed handover action:

- a current outgoing gate targeting `CANCELLED` must exist;
- its exact revision/baseline must be current;
- current human evidence must be included;
- the gate must evaluate GREEN;
- execution must use the accepted governed execution/persistence path and record evaluation/event/execution causality.

If no current cancellation gate exists, cancellation is unavailable through Slice 1.6 product workflow.

A duplicate browser retry after the Slice is already CANCELLED may return target-state no-op semantics without manufacturing another execution.

---

## F004 — MAJOR — Same-basis decision replacement lacks product-level optimistic concurrency

Human decisions intentionally do not advance `governance_revision`. Revision 1 therefore allows two stale browser views to submit opposite APPROVE/REJECT or different CHOOSE_PATH records against the same lifecycle/governance basis. Both can be durable, and timestamp ordering alone chooses the current decision.

That is deterministic, but it permits a stale view to silently reverse a human decision it never observed.

### Required revision

The action projection/form basis must include the exact currently projected decision identity, or explicit absence:

```text
expected_current_approval_decision_id: HumanDecisionId | None
expected_current_choice_decision_id: HumanDecisionId | None
```

Inside the same write transaction, the service must recompute the deterministic current selection and require equality before appending a materially different decision.

A same-target retry may be target-state idempotent. A different decision from a stale view returns conflict and requires human review of refreshed state.

Service-generated decision chronology must not regress relative to the currently selected decision.

---

## F005 — MAJOR — Authorization grants are durable permission, not replaceable latest-wins decisions

Revision 1 selects the greatest `(granted_at, authorization_id)` when several exact matching grants exist.

Accepted Slice 0.4 semantics define authorization as durable permission and explicitly defer revocation/expiry/history semantics. A later duplicate grant must not silently replace the earlier permission or move its effective authority time forward.

### Required revision

Slice 1.6 product `AUTHORIZE` must be target-state idempotent when any exact matching active grant already exists.

If redundant matching durable grants exist from legacy/direct persistence, the current-context projector should select the earliest exact matching permission deterministically:

```text
least granted_at
then least authorization_id
```

because permission existed from the earliest matching grant. Later redundant grants remain auditable evidence but do not replace it.

Revocation remains out of scope.

---

## F006 — MAJOR — Roadmap authorization-record and role-permission requirements need an explicit mapping

The detailed accepted roadmap requires an authorization record to capture actor, timestamp, target Slice, baseline, contract/artifact versions, scope, decision, and reason where required, and its exit bar requires role permissions.

Revision 1 correctly avoids duplicating accepted models, but it does not explicitly prove how the existing contract satisfies those requirements.

### Required revision

Document the mapping rather than adding redundant fields:

```text
actor / timestamp   -> AuthorizationGrant.actor / granted_at
Slice               -> slice_id
baseline            -> baseline_id -> exact Baseline commit/artifact/decision refs
contract version    -> gate_id + gate_revision
artifact versions   -> Baseline.artifact_ids / decision_ids and exact Artifact provenance
scope               -> permission to execute that exact gate revision on that exact baseline
human decision      -> grant existence; approval/rejection remains HumanApprovalDecision
reason              -> AuthorizationGrant.reason
```

For Slice 1.6 M0, the application-bound configured `ActorRef(kind=HUMAN)` is the sole Human Authority principal. SYSTEM/AGENT actors must be forbidden at the service boundary. Finer-grained multi-human RBAC is not implied and remains future work.

---

## Accepted aspects of Revision 1

The following direction does not require revision:

- no second authorization/approval domain model;
- BLOCK / PAUSE / DEFER reuse orthogonal `Blockage` rather than new lifecycle phases;
- a bounded inverse human-hold action is justified;
- `ADVANCE` is appropriate in Slice 1.6 when it executes only a currently GREEN non-ACCEPTED gate;
- transition to `ACCEPTED` remains reserved for Slice 1.7;
- no schema migration is required by the findings above;
- no new runtime dependency is justified;
- Slice-detail-only mutation UI is suitably reviewable;
- explicit POST routes are preferable to a generic command endpoint;
- application-bound Human actor identity is honest for the current local single-user product stage;
- anti-CSRF protection is required and can remain dependency-free;
- request-scoped SQLite ownership must remain unchanged;
- AgentRuntime/OpenCode implementation remains out of scope.

## Additional revision clarifications

Revision 2 should also make explicit that:

- BLOCK / PAUSE / DEFER are offered only in accepted blockable phases;
- these controls preserve unrelated blocker ordering deterministically;
- PAUSE and DEFER are indefinite human holds in Slice 1.6, with no scheduler or due-date semantics;
- clearing a human hold never clears unrelated blockers;
- after lifecycle-changing controls, prior revision-bound human decisions are stale by accepted semantics.

---

## Gate state

```text
Slice 1.6:
OPEN

Design authority:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
f3a0fa7d9cc5b344399c070406353e1107ec30ff

Independent design evaluation:
RLY-S16-DESIGN-EVAL-001 — REVISE

Human design acceptance:
NOT YET ELIGIBLE

Implementation:
NOT AUTHORIZED

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ accepted.**
