# Slice 1.6 — Human Authorization and Decision Gates

**Status:** DESIGN REVISION 1 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design record  
**Human version:** Revision 1  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Design authority:** `RLY-S16-DESIGN-AUTH-001`  
**Human-authorized design subject baseline:** `e9c6e3a5cc7592764bf0ac4932a2ae2659644027`  
**Authority-recording design parent:** `e4923c837f20de35eb96cd1caf615b86860d9222`  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-10-03

---

# 1. Objective

Implement the minimum safe product workflow for **explicit Human Authority** without creating a second authority model, a second lifecycle engine, or UI-owned truth.

The accepted detailed roadmap requires the initial human actions:

```text
APPROVE
REJECT
CHOOSE_PATH
PAUSE
BLOCK
DEFER
CANCEL
```

The current accepted codebase already contains most of the governing semantics required by those actions:

- `AuthorizationGrant`;
- `HumanApprovalDecision`;
- `HumanChoiceDecision`;
- `HandoverGate` and `HandoverPolicy`;
- deterministic `evaluate_handover_gates(...)`;
- exact basis/staleness checks for approvals and choices;
- durable authorization and human-decision tables;
- lifecycle blockage and cancellation semantics;
- atomic governed handover execution;
- a read-only Slice 1.5 board that projects current gates and durable evaluation observations.

Slice 1.6 therefore owns the **application and product mutation seam** that safely exposes these accepted semantics to the Human Authority.

It does not redesign them.

---

# 2. Boundary with adjacent slices

## 2.1 Slice 1.5 remains projection authority

Slice 1.5 remains responsible for deterministic human-facing projection of governed state.

Slice 1.6 may extend Slice 1.5 Slice-detail projection with action availability and action provenance, but the board remains a projection. The UI does not become an independent workflow state machine.

## 2.2 Slice 1.7 remains evaluation and acceptance authority

Slice 1.7 owns:

- manual/external implementation-result capture;
- manual evaluator outcome entry;
- REWORK / ACCEPT evaluation workflow;
- technical acceptance;
- accepted-baseline promotion;
- final human-only implementation/evaluation loop.

Slice 1.6 must not introduce a generic evaluator-result form, technical-acceptance mutation, or accepted-baseline promotion.

## 2.3 Agent execution remains out of scope

No Slice 1.6 action starts OpenCode, Codex, another runtime, or an agent.

The AgentRuntime/OpenCode architecture merged before this Slice is future architecture context only.

---

# 3. Accepted semantics that Slice 1.6 must preserve

## S16-D01 — Reuse the accepted governance model

Slice 1.6 uses the existing:

```text
AuthorizationGrant
HumanApprovalDecision
HumanChoiceDecision
HandoverGate
HandoverContext
GateEvaluation
SliceLifecycle
Blockage
BlockReason
```

No new generic `Approval`, `WorkflowDecision`, `CommandState`, or UI-owned authorization object is introduced.

## S16-D02 — Human decision evidence is not execution

Relay preserves the distinction:

```text
human decision / permission
        ≠
governed lifecycle execution
```

Submitting an APPROVE, REJECT, CHOOSE_PATH, or authorization command records durable human evidence only.

It does **not** silently execute the gate in the same product action.

After the decision is committed, the board re-projects the current gate state. A separate explicit `ADVANCE` action may execute a currently GREEN handover.

This separation keeps decision provenance independently inspectable and prevents an approval click from hiding a second state mutation.

## S16-D03 — Exact-basis binding remains normative

An `AuthorizationGrant` remains bound to:

```text
slice_id
baseline_id
gate_id
gate_revision
```

A `HumanApprovalDecision` remains additionally bound to:

```text
lifecycle_revision
governance_revision
```

A `HumanChoiceDecision` remains additionally bound to the exact canonical sorted set:

```text
choice_gate_refs
```

Slice 1.6 does not weaken these contracts.

## S16-D04 — Staleness fails closed

A product action must never reinterpret stale evidence as current.

If the requested action basis no longer matches durable state, the mutation fails with a typed stale/conflict result and performs no hidden refresh/retry.

The user must review the newly projected state and submit a new decision.

---

# 4. Product action taxonomy

Slice 1.6 exposes the following governed action categories.

## S16-D05 — AUTHORIZE

Purpose: grant the durable permission required by a current gate whose `authorization_required` flag is true.

Representation:

```text
AuthorizationGrant
```

Requirements:

- current gate exists;
- exact gate revision matches;
- exact baseline matches;
- actor is HUMAN;
- reason is nonblank.

A matching existing grant for the same current `(slice, baseline, gate, gate_revision)` is target-state idempotent and is returned rather than duplicated.

A later gate revision or baseline change naturally makes the old grant non-current under accepted governance semantics.

No explicit grant revocation model is added in Slice 1.6. A Human Authority can still REJECT or BLOCK current work; a future requirement for durable revocation must be separately designed.

## S16-D06 — APPROVE / REJECT

Purpose: record a Human Authority disposition for one exact current gate when human approval or review is required.

Representation:

```text
HumanApprovalDecision
```

APPROVE produces a current positive decision only when its complete accepted basis matches current state.

REJECT produces durable blocking evidence through the already accepted `HUMAN_REJECTED` gate reason.

A later opposite decision on the same current basis does not rewrite history. It appends a new immutable decision and becomes the latest current decision under deterministic selection rules.

Submitting the same decision value again against the same exact basis is a no-op success and returns the already-current decision.

## S16-D07 — CHOOSE_PATH

Purpose: select exactly one path from the complete current `HUMAN_CHOICE` gate set.

Representation:

```text
HumanChoiceDecision
```

The submitted choice must bind to the exact sorted current `choice_gate_refs` set. A different gate revision, gate addition/removal, baseline, lifecycle revision, or governance revision makes an old choice stale.

Submitting the same selected path again against the same exact choice basis is a no-op success.

A different later choice appends new immutable evidence and becomes the current choice.

## S16-D08 — BLOCK / PAUSE / DEFER reuse blockage

Slice 1.6 does not add lifecycle phases named `BLOCKED`, `PAUSED`, or `DEFERRED`.

`BLOCK`, `PAUSE`, and `DEFER` are Human Authority control intents represented through the existing orthogonal lifecycle `Blockage` contract.

Reserved Slice 1.6 block-reason codes are:

```text
HUMAN_BLOCK
HUMAN_PAUSE
HUMAN_DEFER
```

The human-supplied reason is stored in the corresponding `BlockReason.summary` and the `BlockageChanged` event reason.

Applying one of these actions:

1. loads the exact current lifecycle under optimistic concurrency;
2. preserves all non-Slice-1.6 blocker reasons;
3. replaces any prior `HUMAN_BLOCK` / `HUMAN_PAUSE` / `HUMAN_DEFER` reason with the new selected human-control reason;
4. persists the resulting lifecycle/event atomically.

This preserves the semantic distinction among the three product actions without inventing new lifecycle state.

## S16-D09 — RESUME / CLEAR_HOLD is a necessary inverse

The older roadmap did not list an explicit inverse action, but BLOCK / PAUSE / DEFER would be unusable as product controls without one.

Slice 1.6 therefore exposes one bounded inverse action, presented as `RESUME` or `Clear human hold`.

It removes only the reserved Slice 1.6 human-control blocker reason(s).

If other blocker reasons remain, lifecycle stays BLOCKED with those reasons.

If none remain, the accepted `clear_blockage(...)` semantics are used.

The action never clears unrelated system/domain blockers.

## S16-D10 — CANCEL reuses the accepted CANCELLED phase

`CANCEL` is a direct Human Authority terminal lifecycle control using the existing legal transition to `LifecyclePhase.CANCELLED`.

It requires:

- HUMAN actor;
- expected exact lifecycle revision;
- nonblank reason;
- accepted lifecycle transition validation.

Cancellation is intentionally not implemented as a new gate policy or new state.

It is not a bypass of a hard stop because it does not advance work past the stop; it terminates the Slice. The accepted lifecycle engine already clears blockage on cancellation.

If the Slice is already CANCELLED, the command may return target-state no-op success. Other terminal states are not silently converted to CANCELLED.

## S16-D11 — ADVANCE executes only a current GREEN gate

Slice 1.6 exposes an explicit human-requested `ADVANCE` action for a currently GREEN handover.

It uses the accepted governed execution semantics and creates:

```text
GateEvaluationRecord
PhaseChanged
ExecutionRecord
```

atomically with the lifecycle transition.

The action is available only when:

- the current outgoing gate exists at the exact revision;
- the latest durable evaluation observation is on `MATCHING_DURABLE_BASIS`;
- the selected gate is GREEN after current Human Authority evidence is included;
- the target phase is not `ACCEPTED` in Slice 1.6.

Transition to `ACCEPTED` is reserved for Slice 1.7 manual evaluation/acceptance.

Slice 1.6 may advance to other legal phases when the accepted gate is GREEN, including deterministic manual progression through the human-controlled workflow.

---

# 5. Current human evidence selection

Durable records are append-only evidence. Product projection needs one deterministic **current** record per logical subject without deleting history.

## S16-D12 — Current authorization selection

For one current gate, matching authorization candidates satisfy exact:

```text
slice_id
gate_id
gate_revision
baseline_id
```

If more than one matching immutable grant exists, current projection selects deterministically by:

```text
greatest granted_at
then greatest authorization_id as a stable tie-breaker
```

All records remain durable and inspectable.

## S16-D13 — Current approval selection

For one current gate, matching approval candidates must satisfy the existing exact basis contract.

Current projection selects:

```text
greatest occurred_at
then greatest decision_id
```

Older same-gate decisions remain history and become non-current evidence.

## S16-D14 — Current choice selection

A current choice must match the complete current choice set, baseline, lifecycle revision, and governance revision.

If several matching immutable choices exist, select by:

```text
greatest occurred_at
then greatest decision_id
```

Only that decision is supplied as the current choice in `HandoverContext`.

## S16-D15 — Equal-timestamp conflicts remain deterministic, not ambiguous

Actor timestamps are preserved as authority provenance, but a UUID-backed Relay ID is the stable tie-breaker when timestamps are equal.

This prevents database insertion order from becoming authority.

---

# 6. Action availability projection

## S16-D16 — Actions derive from durable state, not presentation guesses

Slice detail gains a typed human-action projection produced inside the same verified read snapshot as the existing Slice detail.

Conceptually:

```text
HumanActionProjection
    basis
    actions
    current_authorizations
    current_approval_decisions
    current_choice
    human_hold
```

The projection is advisory/display-only. Submission is revalidated under the write transaction.

## S16-D17 — Gate actions require a matching durable evaluation observation

APPROVE, REJECT, CHOOSE_PATH, and ADVANCE are offered only when the latest durable gate evaluation has:

```text
EvaluationBasisStatus.MATCHING_DURABLE_BASIS
```

This is necessary because current Human Authority action requirements may depend on durable observed inputs that do not have independent current tables, including:

- change-surface status;
- risk status;
- quality checks;
- evaluation outcome;
- other complete `HandoverContext` values.

Slice 1.6 must not reconstruct or guess those values from UI state.

AUTHORIZE may be offered from the exact current gate definition when `authorization_required=true`, because the accepted authorization model itself binds directly to gate revision and baseline.

## S16-D18 — Human-action reasons drive available decision controls

For a matching evaluation:

```text
AUTHORIZATION_REQUIRED
    -> AUTHORIZE

HUMAN_APPROVAL_REQUIRED
CHANGE_SURFACE_REVIEW_REQUIRED
RISK_REVIEW_REQUIRED
HARD_STOP_REQUIRES_HUMAN
    -> APPROVE / REJECT

HUMAN_CHOICE_REQUIRED
    -> CHOOSE_PATH over the exact canonical choice set
```

REJECT remains available when an approval/review action is current even if the user is declining to clear the gate.

The UI does not expose an approval button for an unrelated GREEN/AUTO gate merely because a human is viewing it.

## S16-D19 — ADVANCE availability is recomputed after current human evidence

The stored Slice 1.5 evaluation observation is historical evidence.

For ADVANCE, Relay uses its matching full context as the non-human observation basis, replaces the context's human authorization/decision projection with the latest current durable human evidence, and re-runs deterministic gate evaluation.

Only a gate that evaluates GREEN under that reconstructed current human basis may be advanced.

The stored historical light is never blindly trusted as execution authority.

---

# 7. Atomicity and concurrency

## S16-D20 — Every mutation revalidates inside a write transaction

Form basis tokens are concurrency expectations, not authority.

The service must load and verify the current durable subject under the same SQLite write transaction that appends the new evidence or lifecycle event.

At minimum the command basis contains, as applicable:

```text
slice_id
baseline_id
gate_id
gate_revision
expected_lifecycle_revision
expected_governance_revision
choice_gate_refs
```

Mismatch yields a typed stale/conflict result with no write.

## S16-D21 — No hidden optimistic retry

If another action changes relevant state first, Relay returns a conflict and asks the human to review the refreshed projection.

The service does not silently rebase a human decision onto a newer lifecycle or gate revision.

## S16-D22 — Execution must prove supplied human evidence is current, not merely durable

The existing `execute_and_persist_handover(...)` verifies that supplied decisions/grants are durable, but Slice 1.6 introduces concurrent human mutation paths.

Therefore the Slice 1.6 execution path must additionally prove, inside the execution transaction, that the human evidence used for execution is the deterministic latest current evidence for the exact gate basis.

A newer REJECT/choice must not be ignored merely because an older APPROVE is still durable.

Implementation may satisfy this by a narrow extension of the accepted persistence execution function or by a bounded Slice 1.6 execution service that performs the proof before the existing pure governance execution logic.

No second execution engine is introduced.

---

# 8. Application/service boundary

## S16-D23 — Introduce one small human-control application package

Expected package:

```text
src/relay_engine/human_control/
    __init__.py
    errors.py
    models.py
    service.py
```

This boundary is justified because Human Authority commands are domain/application operations that should remain callable independently of the HTML board.

The package must not become a generic command bus or workflow framework.

## S16-D24 — Normative service capabilities

Exact names may follow repository naming conventions, but behavior is normative:

```text
grant_gate_authorization(...)
record_gate_approval(... APPROVE | REJECT ...)
record_gate_choice(...)
set_human_hold(... BLOCK | PAUSE | DEFER ...)
clear_human_hold(...)
cancel_slice(...)
advance_green_handover(...)
project_human_actions(...)
```

Each command receives explicit IDs/timestamps/reason from its caller for deterministic testing. The web adapter may generate UUIDv7 IDs and UTC times at the request boundary.

## S16-D25 — Typed service errors

Required distinctions include at minimum:

```text
HumanActionNotAvailable
HumanActionBasisStale
HumanActionConflict
HumanActionRequiresEvaluation
HumanActionInvalidChoice
HumanActionForbidden
```

Existing `PersistenceIntegrityError`, `DatabaseUnavailable`, and lifecycle/governance errors remain integrity/infrastructure/domain boundaries and are not converted into false success.

---

# 9. Persistence design

## S16-D26 — No schema migration is required

The current schema already contains:

```text
authorization_grants
human_decisions
lifecycle_current
lifecycle_events
gate_evaluation_records
executions
```

Slice 1.6 should not add a schema migration merely for query convenience.

The M0 local workflow is small enough to load/parse the relevant immutable records deterministically.

If measured performance later proves inadequate, indexing is separate work.

## S16-D27 — Add narrow caller-owned-transaction helpers where needed

Expected persistence extensions are narrow helpers such as:

```text
load_authorization_grants_for_slice_from_connection(...)
load_human_decisions_for_slice_from_connection(...)
insert_authorization_grant_from_connection(...)
insert_human_decision_from_connection(...)
```

and, if required, a bounded current-evidence validation extension for governed execution.

These helpers preserve typed-payload/index integrity checks and avoid nested write transactions.

No ORM, repository abstraction, event bus, or generic unit-of-work layer is introduced.

---

# 10. Board and HTTP product contract

## S16-D28 — Mutations are exposed only on Slice detail in Revision 1

The Project board remains primarily navigational.

Human decision forms appear on the Slice detail page, where the exact gate, reasons, baseline, lifecycle revision, and evidence basis can be inspected before mutation.

This avoids compact card controls that hide critical authority context.

## S16-D29 — Server-rendered HTML remains the UI architecture

Slice 1.6 keeps the accepted FastAPI + plain HTML/CSS architecture.

No React, TypeScript, Node, Vite, websocket, SSE, or background worker is required.

No new runtime dependency is expected.

## S16-D30 — POST-Redirect-GET for successful mutations

Mutation routes use POST.

Successful mutation returns `303 See Other` to the canonical Slice detail GET route.

This avoids browser form-resubmission on refresh and ensures the resulting screen is a fresh projection of durable state.

GET and HEAD never mutate.

PUT/PATCH/DELETE remain unavailable on the board surface unless separately designed.

## S16-D31 — Explicit action routes

The minimum clear route surface is:

```text
POST /projects/{project_id}/slices/{slice_id}/actions/authorize
POST /projects/{project_id}/slices/{slice_id}/actions/approve
POST /projects/{project_id}/slices/{slice_id}/actions/reject
POST /projects/{project_id}/slices/{slice_id}/actions/choose
POST /projects/{project_id}/slices/{slice_id}/actions/advance
POST /projects/{project_id}/slices/{slice_id}/actions/hold
POST /projects/{project_id}/slices/{slice_id}/actions/resume
POST /projects/{project_id}/slices/{slice_id}/actions/cancel
```

`hold` accepts only the closed set:

```text
BLOCK
PAUSE
DEFER
```

The explicit route set is preferred over a generic arbitrary command endpoint because the current actions are fixed and reviewability matters more than hypothetical extensibility.

## S16-D32 — Actor identity is application-bound, not form-supplied

The local board is currently a loopback Human Authority tool, not a multi-user identity system.

`create_app(...)` receives or constructs one explicit `ActorRef(kind=HUMAN)` for the running Human Authority session/configuration.

Mutation forms never supply an actor ID that the server trusts.

This provides truthful provenance without pretending Slice 1.6 implements authentication or organization RBAC.

Multi-user authentication/authorization remains future product hardening/collaboration work.

## S16-D33 — Anti-CSRF is mandatory once the board can mutate

A read-only loopback board did not require a write-request CSRF boundary. Slice 1.6 does.

The application creates or receives an unpredictable per-process CSRF token, stores it only in process/application state, renders it in same-origin mutation forms, and validates it on every POST before opening a write transaction.

The token is never persisted as engineering state.

To preserve the no-new-dependency constraint, simple `application/x-www-form-urlencoded` bodies may be parsed with the Python standard library rather than adding a form-parsing package solely for this slice.

Missing/incorrect token returns a non-mutating forbidden response.

## S16-D34 — Request-scoped database ownership remains intact

Application state may contain only configuration such as:

```text
database path
Human ActorRef
CSRF token
```

Each mutation request opens its own ordinary `RelayDatabase`, performs the complete governed command, commits/rolls back, and closes it in the same synchronous execution context.

No app-global SQLite connection and no `check_same_thread=False` workaround are introduced.

---

# 11. HTTP error contract

Minimum presentation mapping:

```text
404 NOT_FOUND
403 FORBIDDEN          # invalid CSRF / non-human configured actor
409 STALE_OR_CONFLICT  # stale exact basis / competing mutation
422 ACTION_INVALID     # action not available / invalid choice / invalid intent
500 INTEGRITY_ERROR
503 UNAVAILABLE
```

A failed mutation renders no success state and performs no hidden compensating mutation.

The error page should tell the human to return to the Slice detail and review current state rather than automatically resubmit against a new basis.

---

# 12. Idempotency

## S16-D35 — Target-state idempotency where safe

The following exact repeated actions are no-op success:

- existing exact current authorization grant;
- same current APPROVE/REJECT decision value on the same basis;
- same current CHOOSE_PATH selection on the same choice basis;
- applying a human hold that would produce the exact current blockage;
- clearing a human hold when no Slice-1.6 human hold exists;
- CANCEL when already CANCELLED.

A repeated ADVANCE after the lifecycle already moved is not silently treated as success. Its expected lifecycle revision is stale and returns conflict, because the caller may now be looking at a different outgoing gate set.

---

# 13. Slice 1.7 hard boundary

Slice 1.6 must reject or omit product actions that would constitute Slice 1.7 behavior.

In particular:

```text
manual EvaluationOutcome submission       NOT AUTHORIZED
manual implementation-result SHA capture  NOT AUTHORIZED
technical acceptance                      NOT AUTHORIZED
advance to ACCEPTED through 1.6 UI        NOT AUTHORIZED
accepted-baseline promotion               NOT AUTHORIZED
closure/finalization workflow              NOT AUTHORIZED
```

A current gate targeting `ACCEPTED` may be displayed, but Slice 1.6 does not render an ADVANCE control for it.

---

# 14. Expected implementation change surface

Minimum expected new production surface:

```text
src/relay_engine/human_control/
    __init__.py
    errors.py
    models.py
    service.py
```

Expected bounded existing-file changes:

```text
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
```

Possible tiny export changes elsewhere are acceptable if mechanically required.

Expected persistence migration:

```text
NONE
```

Expected new runtime dependencies:

```text
NONE
```

Not expected:

- governance model rewrite;
- lifecycle transition-matrix changes;
- repository/provider code changes;
- Project/Slice CRUD redesign;
- React/Node/toolchain additions;
- authentication/organization subsystem;
- AgentRuntime/OpenCode implementation;
- Slice 1.7 implementation;
- generic command bus/workflow framework.

Material production-surface expansion requires evaluation/escalation.

---

# 15. Required deterministic tests

## 15.1 Domain reuse and action mapping

- AUTHORIZE creates accepted `AuthorizationGrant` only.
- APPROVE/REJECT create accepted `HumanApprovalDecision` only.
- CHOOSE_PATH creates accepted `HumanChoiceDecision` only.
- BLOCK/PAUSE/DEFER use blockage, not new lifecycle phases.
- CANCEL uses the existing CANCELLED transition.
- RESUME removes only Slice-1.6 human-control blocker reasons.

## 15.2 Exact-basis / stale behavior

- stale baseline rejects authorization/decision;
- stale gate revision rejects action;
- stale lifecycle revision rejects approval/choice/control mutation where applicable;
- stale governance revision rejects approval/choice;
- stale choice set rejects CHOOSE_PATH;
- stale action never silently retries on current state.

## 15.3 Current evidence selection

- latest matching approval wins deterministically;
- latest matching choice wins deterministically;
- latest matching authorization projection is deterministic;
- equal timestamps use stable ID tie-break;
- old decisions remain auditable but are not supplied as current authority.

## 15.4 Hold behavior

- BLOCK/PAUSE/DEFER preserve unrelated blockers;
- one human hold replaces prior Slice-1.6 human hold without deleting other reasons;
- RESUME leaves unrelated blockers intact;
- clear final human hold restores CLEAR;
- hold mutation advances lifecycle revision and stales prior revision-bound decisions.

## 15.5 Gate execution

- ADVANCE requires matching durable evaluation basis;
- current human evidence is re-evaluated, not historical light trusted blindly;
- RED never advances;
- YELLOW never advances;
- GREEN advances atomically with evaluation/event/execution records;
- newer REJECT cannot be bypassed by supplying older durable APPROVE;
- ACCEPTED-target gate has no Slice-1.6 ADVANCE path.

## 15.6 Concurrency

- two competing decisions from the same exact expected basis serialize deterministically;
- lifecycle mutation concurrent with approval causes stale-basis failure as appropriate;
- concurrent gate/lifecycle change cannot commit an action against old basis;
- failed transaction leaves no partial decision/event/execution record.

## 15.7 Web safety

- GET/HEAD do not mutate;
- successful POST uses 303 PRG;
- invalid CSRF returns 403 and no write;
- actor cannot be overridden by form input;
- unknown Project/Slice returns 404;
- stale mutation returns 409;
- unavailable action returns 422;
- persistence integrity/unavailability map to 500/503;
- database connection closes on every success/failure path;
- Slice detail renders exact basis and reasons near consequential actions;
- forms remain keyboard accessible and action meaning is text-visible.

---

# 16. Acceptance criteria for implementation

Implementation is eligible for independent evaluation only if all are true:

```text
[ ] existing governance/lifecycle models reused without parallel authority truth
[ ] durable human decisions/authorizations are exact-basis bound
[ ] stale evidence fails closed
[ ] hard stop / RED cannot be bypassed
[ ] decision recording is separate from handover execution
[ ] current decision selection is deterministic and history-preserving
[ ] BLOCK/PAUSE/DEFER use existing blockage semantics
[ ] CANCEL uses existing lifecycle semantics
[ ] Slice 1.7 acceptance/evaluation boundary preserved
[ ] mutation UI limited to Slice detail
[ ] Human actor is server-bound, not trusted from form input
[ ] CSRF protection present
[ ] request-scoped SQLite ownership preserved
[ ] no schema migration unless separately escalated and accepted
[ ] no new runtime dependency unless separately escalated and accepted
[ ] full repository quality profile passes
[ ] implementation change surface remains bounded and reviewable
```

Passing tests and CI remain evidence only and do not constitute Human acceptance.

---

# 17. Explicit non-authority

This design does not authorize implementation.

It does not open Slice 1.7.

It does not authorize agent execution.

It does not canonically adopt the AgentRuntime/OpenCode working proposal as current execution authority.

It does not authorize multi-user auth/RBAC, background automation, automatic gate execution, or a generalized workflow engine.

---

# 18. Design handoff

```text
Current role/model:
Slice 1.6 Human Authorization and Decision Gates Architect — GPT-5.6 Sol

Next role/model:
Independent Slice 1.6 Design Reviewer — GPT-5.6 Sol (or another independent capable reviewer)

Design review outcome vocabulary:
ACCEPT / REVISE / ESCALATE
```

Human design acceptance and implementation authorization remain separate later decisions.

**Unblocked ≠ authorized.**
