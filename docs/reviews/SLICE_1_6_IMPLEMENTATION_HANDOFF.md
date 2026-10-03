# Slice 1.6 — Luna Implementation Handoff

**Status:** AUTHORIZED IMPLEMENTATION HANDOFF  
**Authority:** `RLY-S16-AUTH-001`  
**Preferred executor:** GPT-5.6 Luna  
**Implementation baseline:** `7bb7363375cc3cc3ac26758741ac9f2c6ca991e3`  
**Exact accepted design head:** `c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb`  
**Independent design evaluation:** `RLY-S16-DESIGN-EVAL-003 — ACCEPT`

This handoff normalizes Revision 1 + Revision 2 + Revision 3 into one implementation contract. Where this handoff differs from Revision 1, the accepted Revision 2/3 amendments control.

---

# 1. Start state

Create/use:

```text
implementation/1.6-human-authorization-decision-gates
```

The branch must begin from exactly:

```text
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3
```

Verify before coding:

```bash
git fetch origin
git checkout implementation/1.6-human-authorization-decision-gates
git rev-parse HEAD
```

Expected `HEAD`:

```text
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3
```

Do not rebase the authorized baseline onto later `main` unless Human Authority explicitly reauthorizes the implementation baseline.

Before substantive work, read:

```text
docs/reviews/SLICE_1_6_IMPLEMENTATION_AUTHORIZATION.md
docs/slices/SLICE_1_6_HUMAN_AUTHORIZATION_AND_DECISION_GATES.md
docs/slices/SLICE_1_6_HUMAN_AUTHORIZATION_AND_DECISION_GATES_REV2_AMENDMENT.md
docs/slices/SLICE_1_6_HUMAN_AUTHORIZATION_AND_DECISION_GATES_REV3_AMENDMENT.md
docs/reviews/SLICE_1_6_DESIGN_EVALUATION_REV3.md
docs/policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md
docs/policies/DOCUMENTATION_GOVERNANCE_V0_3.md
```

If this implementation branch does not contain the authorization/handoff records because it intentionally starts from the design-accepted baseline, read those records from `origin/governance/1.6-implementation-authorization` without changing the implementation baseline.

---

# 2. Objective

Implement the minimum safe Human Authority mutation seam over Relay's accepted durable governance state.

The central invariant is:

```text
human durable decision / permission
        !=
governed lifecycle execution
```

The board may submit Human Authority commands, but it remains a projection of durable state and never becomes an independent workflow state machine.

No Human action may silently bypass:

```text
exact baseline
exact gate revision
exact lifecycle revision
exact governance revision
latest durable evaluation observation
latest deterministic Human evidence projection
RED / hard-stop semantics
```

---

# 3. Authorized action set

Implement exactly these Human Authority controls:

```text
AUTHORIZE
APPROVE
REJECT
CHOOSE_PATH
BLOCK
PAUSE
DEFER
CLEAR_HOLD / RESUME
ADVANCE
CANCEL
```

Do not add generic commands or additional action types.

## Decision-only actions

These create durable Human evidence but do not execute a lifecycle handover:

```text
AUTHORIZE
APPROVE
REJECT
CHOOSE_PATH
```

## Lifecycle-control actions

```text
BLOCK
PAUSE
DEFER
CLEAR_HOLD / RESUME
```

These use accepted lifecycle `Blockage`; they do not create new lifecycle phases.

## Governed execution actions

```text
ADVANCE
CANCEL
```

Both require exact current GREEN handover gates. `CANCEL` is not a direct phase mutation.

---

# 4. Human-control package

Create the minimum application boundary:

```text
src/relay_engine/human_control/
    __init__.py
    errors.py
    models.py
    service.py
```

This package must be callable independently of FastAPI/HTML.

It must not become:

```text
generic command bus
workflow framework
event bus
repository abstraction
unit-of-work framework
plugin system
```

Recommended service capabilities; exact names may follow repository conventions:

```text
project_human_actions(...)
grant_gate_authorization(...)
record_gate_approval(...)
record_gate_choice(...)
set_human_hold(...)
clear_human_hold(...)
advance_green_handover(...)
cancel_slice(...)
```

Required typed application errors include at least:

```text
HumanActionNotAvailable
HumanActionBasisStale
HumanActionConflict
HumanActionRequiresEvaluation
HumanActionInvalidChoice
HumanActionForbidden
```

Do not convert persistence-integrity, database-unavailable, lifecycle, or governance corruption into false product success.

---

# 5. Human Action Basis — normative final semantics

Do not implement Revision-1's weaker structural-only mutation basis.

For consequential gate-affecting actions, define/use a typed basis equivalent to:

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

Authorization identity may be represented directly or validated through the deterministic authorization projection below.

A valid Human Action Basis means:

> the latest durable gate-evaluation observation whose independently queryable durable structural facts and deterministic durable Human-evidence projection still agree with current Relay state.

It does NOT mean that every external assessment fact has been freshly re-observed at POST time.

Inside the same write transaction, prove at minimum:

```text
submitted evaluation_record_id == latest durable evaluation record for Slice
current lifecycle == record.context.lifecycle
current outgoing gate refs/revisions == record.gate_refs
current gate baseline == record.context.baseline_id
current deterministic authorization projection == record.context.authorization_grants
current deterministic approval projection == record.context human approval projection
current deterministic choice projection == record.context human choice projection
submitted expected current decision IDs == actual deterministic current decision IDs
```

Assessment facts without another accepted current authority source remain inherited from the latest durable observation:

```text
evaluation_outcome
quality_checks
change_surface_status
risk_status
toolchain_change_status
available artifact/evidence observations where not independently rederived
```

Never silently rebase a submitted Human action to a newer observation.

---

# 6. Deterministic current Human evidence projection

## 6.1 Authorization projection — Revision 3 controls

For each current logical gate, load durable grants matching:

```text
slice_id
gate_id
```

Then select at most one projected grant.

### Exact current grant exists

Exact means both:

```text
baseline_id == current gate baseline
gate_revision == current gate revision
```

If one or more exact grants exist, project the earliest established permission:

```text
least granted_at
then least authorization_id
```

Later exact duplicates remain immutable evidence but do not replace or delay authority.

### No exact grant, but stale same-gate grants exist

Project the latest stale explanatory grant:

```text
greatest granted_at
then greatest authorization_id
```

This is deliberately supplied so the accepted gate engine can emit:

```text
AUTHORIZATION_STALE
```

rather than collapsing the condition into `AUTHORIZATION_REQUIRED`.

### No same-gate grant

Project no authorization.

Use this same projector consistently for:

```text
Human Action Basis checks
successor GateEvaluationRecord contexts
governed execution validation
Slice-detail Human action projection
```

No revocation/expiry model is authorized.

## 6.2 Approval projection

For one logical gate, order relevant durable approval history by:

```text
occurred_at
then decision_id
```

The greatest pair is the projected latest approval/rejection evidence, even if it is stale relative to current lifecycle/governance revision. The accepted gate engine decides whether it is current or emits stale/rejection reasons.

## 6.3 Choice projection

Order relevant durable choice history by:

```text
occurred_at
then decision_id
```

The greatest pair is the projected latest choice evidence. The accepted gate engine decides whether it matches the exact current choice set/basis.

---

# 7. AUTHORIZE transaction contract

AUTHORIZE has exactly three cases.

## Case A — synchronized exact current grant already exists

If:

```text
exact current grant exists
AND deterministic projector selects it
AND latest Human Action Basis already contains that selected grant
AND all other basis checks match
```

return target-state no-op success:

```text
no new grant
no governance_revision increment
no new GateEvaluationRecord
```

## Case B — exact current grant exists but latest observation does not project it

This is an unsynchronized durable-authority state.

Return:

```text
HumanActionBasisStale or HumanActionRequiresEvaluation
```

with:

```text
NO WRITE
```

Do not create a duplicate grant, invent a missing governance transition, or silently repair history.

## Case C — no exact current grant exists

Within one write transaction:

```text
load latest Human Action Basis
recheck lifecycle/gate refs/baseline/Human evidence
insert AuthorizationGrant
new governance_revision = prior + 1
construct successor HandoverContext
project new exact authorization using final deterministic projector
retain latest relevant Human decisions, now stale by governance revision where applicable
re-evaluate COMPLETE current gate set
append successor GateEvaluationRecord
COMMIT
```

Causal time order must satisfy:

```text
prior evaluation recorded_at
    <= grant.granted_at
    <= successor evaluation recorded_at
```

The authorization may be recorded even if another non-authority condition keeps the gate RED; the successor evaluation must truthfully show that.

---

# 8. APPROVE / REJECT transaction contract

For a materially new approval/rejection, require:

```text
expected_evaluation_record_id
expected_current_approval_decision_id: HumanDecisionId | None
exact gate ID/revision
exact baseline
exact lifecycle revision
exact governance revision
HUMAN server-bound actor
nonblank reason
```

Inside one write transaction:

```text
load latest Human Action Basis
recompute deterministic current approval selection
compare expected_current_approval_decision_id
insert HumanApprovalDecision
construct successor context at SAME governance_revision
replace projected current approval with new decision
re-evaluate COMPLETE current gate set
append successor GateEvaluationRecord
COMMIT
```

Causal order:

```text
prior evaluation recorded_at
    <= decision.occurred_at
    <= successor evaluation recorded_at
```

Same-target retry on the exact current basis may return no-op success.

If expected current decision differs from actual and requested target differs, return conflict/409 with no write.

A materially new decision must not have an `occurred_at` earlier than the currently projected decision it replaces.

---

# 9. CHOOSE_PATH transaction contract

Require exact canonical sorted current `choice_gate_refs` plus:

```text
expected_evaluation_record_id
expected_current_choice_decision_id: HumanDecisionId | None
selected_gate_id
selected_gate_revision
baseline
lifecycle revision
governance revision
HUMAN actor
nonblank reason
```

Inside one write transaction:

```text
load latest Human Action Basis
recompute deterministic current choice
prove exact choice set is unchanged
compare expected_current_choice_decision_id
insert HumanChoiceDecision
construct successor context at SAME governance_revision
replace projected current choice
re-evaluate COMPLETE current gate set
append successor GateEvaluationRecord
COMMIT
```

Same selection retry on exact basis may be no-op success.

Different selection from a stale browser view returns conflict; do not silently overwrite/rebase.

---

# 10. Human hold controls

Do NOT add `PAUSED` or `DEFERRED` lifecycle phases.

Use existing `Blockage` with reserved Human control codes:

```text
HUMAN_BLOCK
HUMAN_PAUSE
HUMAN_DEFER
```

Offer these only in lifecycle phases accepted as blockable by the lifecycle engine.

## Setting a hold

Deterministic reason handling:

```text
1. preserve unrelated existing BlockReason values in durable order
2. remove prior HUMAN_BLOCK / HUMAN_PAUSE / HUMAN_DEFER reasons
3. append exactly one requested Human hold reason last
```

Persist through accepted lifecycle blockage semantics.

PAUSE and DEFER are indefinite holds only:

```text
no due date
no scheduler
no auto-resume
no notification subsystem
```

## CLEAR_HOLD / Resume

Remove only:

```text
HUMAN_BLOCK
HUMAN_PAUSE
HUMAN_DEFER
```

If unrelated blockers remain, lifecycle remains blocked with those reasons in prior order.

If no blockers remain, use accepted clear-blockage semantics.

A hold/clear-hold advances lifecycle revision. Existing revision-bound Human decisions become stale naturally.

If the command started from an exact current evaluation basis and phase/gate set is unchanged, a successor deterministic GateEvaluationRecord may be appended in the same transaction using preserved non-Human observation facts and the new lifecycle revision.

If no exact current evaluation basis exists, persist the hold but do NOT fabricate an evaluation from unknown assessment facts; the board should then show prior observation as stale until another governed evaluation exists.

---

# 11. ADVANCE execution contract

ADVANCE requires:

```text
expected_evaluation_record_id
exact selected gate ID/revision
latest current lifecycle
latest current baseline
latest deterministic authorization projection
latest deterministic approval projection
latest deterministic choice projection
```

Inside one write transaction:

```text
reload lifecycle/gate refs/baseline
reload deterministic current Human evidence
prove latest evaluation context's Human projection matches that evidence
re-run accepted deterministic gate evaluation over COMPLETE gate set
require selected gate GREEN
reject if target phase == ACCEPTED
call accepted governed lifecycle execution path exactly once
atomically persist evaluation + lifecycle event/current + execution record
```

A stored historical GREEN light is never enough by itself.

A newer REJECT/choice must prevent execution even if an older APPROVE/choice remains durable.

Repeated ADVANCE after lifecycle already moved is stale/conflict, not target-state success.

Do not implement a second execution engine.

---

# 12. CANCEL execution contract

Revision 2 overrides Revision 1: CANCEL is NOT direct `transition_phase(CANCELLED)` product mutation.

CANCEL is a specialized governed handover request.

Require:

```text
current outgoing gate targeting LifecyclePhase.CANCELLED exists
exact gate revision/baseline is current
expected_evaluation_record_id is latest Human Action Basis
latest Human evidence matches basis
re-evaluation inside write transaction returns GREEN for selected cancellation gate
```

Then use the accepted governed execution/persistence path and record evaluation/event/execution causality atomically.

If cancellation gate is YELLOW, Human must first perform required AUTHORIZE/APPROVE/CHOOSE_PATH action.

If RED, cancellation is unavailable.

If there is no current cancellation gate, Slice 1.6 must not manufacture one and must not call direct lifecycle cancellation.

If browser retry finds Slice already CANCELLED, target-state no-op is allowed without a second execution record.

---

# 13. Persistence work

No migration.

Add only narrow caller-owned-transaction helpers needed by the service, expected examples:

```text
load_authorization_grants_for_slice_from_connection(...)
load_human_decisions_for_slice_from_connection(...)
insert_authorization_grant_from_connection(...)
insert_human_decision_from_connection(...)
```

and only the minimum extension required to verify current Human evidence before existing governed execution.

Preserve:

```text
typed payload/index integrity checks
explicit deterministic SQL ordering
caller-owned transaction
no nested write transaction
no ORM
no generic repository layer
```

A tiny persistence record/export adjustment is allowed only if mechanically required.

---

# 14. Board projection changes

Extend Slice detail with a typed Human action projection, conceptually:

```text
HumanActionProjection
    basis
    actions
    current_authorizations
    current_approval_decisions
    current_choice
    human_hold
```

Projection remains advisory/display-only. POST service revalidates everything.

Expose actions only from durable state and latest accepted observation logic.

Normal gate-action mapping after applying Revision 2/3 basis rules:

```text
AUTHORIZATION_REQUIRED or AUTHORIZATION_STALE
    -> AUTHORIZE when action basis is valid

HUMAN_APPROVAL_REQUIRED
CHANGE_SURFACE_REVIEW_REQUIRED
RISK_REVIEW_REQUIRED
HARD_STOP_REQUIRES_HUMAN
    -> APPROVE / REJECT

HUMAN_CHOICE_REQUIRED
    -> CHOOSE_PATH over exact canonical choice set

current GREEN non-ACCEPTED gate
    -> ADVANCE

current GREEN CANCELLED-target gate
    -> CANCEL
```

Do not expose approval controls on unrelated AUTO/GREEN gates merely because a Human is viewing the page.

A gate targeting `ACCEPTED` may be displayed, but Slice 1.6 renders no ADVANCE control for it.

Show exact basis/provenance near consequential controls so the Human can inspect:

```text
gate/revision
target phase
baseline
latest evaluation observation identity
current lifecycle revision
current governance revision
relevant reasons/current Human evidence
```

---

# 15. HTTP / FastAPI contract

Keep server-rendered HTML; no JS framework.

Explicit POST routes:

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

`hold` accepts only:

```text
BLOCK
PAUSE
DEFER
```

Successful mutation:

```text
303 See Other
-> canonical Slice detail GET
```

GET/HEAD never mutate.

PUT/PATCH/DELETE remain unavailable on board surface.

## Server-bound actor

`create_app(...)` receives/constructs one configured:

```text
ActorRef(kind=HUMAN)
```

Forms never supply/trust actor identity.

SYSTEM/AGENT configured actors must be rejected for Human Authority actions.

## CSRF

Mutation-capable board requires anti-CSRF.

Use one unpredictable per-process token:

```text
stored only in application/process state
rendered in same-origin forms
validated before opening write transaction
not persisted as engineering state
```

No new dependency is justified solely for form parsing; standard-library parsing of `application/x-www-form-urlencoded` is allowed.

Invalid/missing CSRF:

```text
403
NO WRITE
```

## Request-scoped SQLite

App state may hold only configuration such as:

```text
database path
Human ActorRef
CSRF token
```

Each POST opens its own ordinary RelayDatabase and completes command/commit/rollback/close in the same synchronous request-owned execution context.

No app-global DB connection, pool, or `check_same_thread=False`.

---

# 16. HTTP error mapping

Minimum mapping:

```text
404 NOT_FOUND
403 FORBIDDEN
409 STALE_OR_CONFLICT
422 ACTION_INVALID
500 INTEGRITY_ERROR
503 UNAVAILABLE
```

Use 403 for invalid CSRF/non-Human configured actor.

Use 409 for stale exact basis or competing mutation.

Use 422 for unavailable action, invalid choice, invalid intent, or action structurally not applicable.

Never auto-resubmit a stale Human decision against refreshed state.

---

# 17. Idempotency rules

Safe no-op success:

```text
synchronized exact current authorization already present
same current APPROVE/REJECT value on same exact basis
same CHOOSE_PATH selection on same exact choice basis
human hold request would produce exact current blockage
CLEAR_HOLD when no Slice-1.6 Human hold exists
CANCEL retry when Slice already CANCELLED
```

Not no-op:

```text
ADVANCE after lifecycle already moved -> stale/conflict
exact grant exists but latest observation does not project it -> fail closed
opposite approval/choice from stale view -> conflict
```

---

# 18. Expected change surface

## New production files

```text
src/relay_engine/human_control/__init__.py
src/relay_engine/human_control/errors.py
src/relay_engine/human_control/models.py
src/relay_engine/human_control/service.py
```

## Bounded existing production changes

```text
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
```

Tiny export/record adjustments elsewhere are permitted only when mechanically required.

No expected changes to:

```text
lifecycle transition matrix
governance domain semantics
schema migrations
pyproject runtime dependencies
uv.lock for new dependencies
provider/repository integrations
AgentRuntime/OpenCode
```

If implementation genuinely requires one of those, STOP and escalate.

---

# 19. Required tests

At minimum prove:

## Human evidence / projection

- exact grant beats stale grants;
- earliest exact grant selected deterministically;
- latest stale same-gate grant selected only when no exact exists;
- stale grant produces `AUTHORIZATION_STALE` through accepted engine;
- latest approval selected by `(occurred_at, decision_id)`;
- latest choice selected by `(occurred_at, decision_id)`;
- equal timestamps use ID tie-breakers;
- old evidence remains auditable.

## AUTHORIZE

- no exact grant -> grant + governance revision `N -> N+1` + successor evaluation atomically;
- stale grant -> new exact grant + one governance increment + successor evaluation;
- synchronized exact grant -> no-op success;
- exact grant missing from latest observation -> fail closed, no write;
- prior revision-bound Human decisions become stale after authorization revision increment;
- successor evaluation contains new exact grant and correct resulting light/reasons.

## APPROVE / REJECT

- append decision + successor evaluation in one transaction;
- governance revision unchanged;
- resulting stored observation changes appropriately;
- same-target exact-basis retry no-op;
- stale expected current decision ID conflicts;
- opposite decision from stale browser view cannot silently replace current decision;
- non-regressing decision chronology enforced.

## CHOOSE_PATH

- exact sorted choice set required;
- append decision + successor evaluation atomically;
- governance revision unchanged;
- stale gate set/revision/baseline/lifecycle/governance basis rejects;
- same selection retry no-op;
- different choice with stale expected ID conflicts.

## Human holds

- BLOCK/PAUSE/DEFER accepted only in blockable phases;
- unrelated blocker order preserved;
- prior Human hold replaced by exactly one new Human hold reason;
- CLEAR_HOLD removes only reserved Human reasons;
- unrelated blockers remain;
- final Human hold removal yields CLEAR when no blockers remain;
- lifecycle revision increments;
- old revision-bound decisions become stale;
- successor evaluation appended only when exact observation basis exists and can be safely carried forward;
- no fabricated evaluation when basis absent.

## ADVANCE

- exact expected evaluation record required;
- current Human evidence reloaded inside transaction;
- newer REJECT cannot be bypassed with old APPROVE;
- latest choice enforced;
- deterministic full gate set re-evaluated;
- RED/YELLOW never execute;
- GREEN non-ACCEPTED gate executes atomically;
- target `ACCEPTED` unavailable in Slice 1.6;
- retry after lifecycle movement returns stale/conflict;
- no partial evaluation/event/execution on failure.

## CANCEL

- direct lifecycle cancellation is not used;
- current cancellation gate required;
- GREEN required;
- YELLOW requires prior Human action;
- RED unavailable;
- missing cancellation gate unavailable;
- atomic governed execution evidence persisted;
- already CANCELLED retry is target-state no-op without duplicate execution.

## Concurrency

- two opposite decisions from same browser basis serialize; one loses with 409/conflict;
- concurrent lifecycle change invalidates old action basis;
- newer evaluation invalidates older `expected_evaluation_record_id` even if gate/lifecycle structural tuple otherwise matches;
- failed transaction leaves no partial grant/decision/evaluation/event/execution.

## Web / security

- GET/HEAD never mutate;
- every successful POST returns 303 PRG;
- invalid/missing CSRF -> 403 + no write;
- actor cannot be overridden through form data;
- non-Human app actor rejected;
- unknown Project/Slice -> 404;
- stale/conflict -> 409;
- unavailable/invalid action -> 422;
- integrity/unavailable -> 500/503;
- every request closes its DB connection;
- exact basis/reasons rendered near consequential controls;
- forms keyboard accessible and action meaning text-visible;
- no generated docs/OpenAPI surface is re-enabled.

---

# 20. Full regression / quality gate

Run exactly:

```bash
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

All pre-existing tests must remain green.

GitHub Actions must succeed on the exact candidate SHA before independent implementation evaluation.

Do not weaken strict typing, formatting, lint, or test configuration to make the slice pass.

---

# 21. Hard out-of-scope boundary

Do not implement:

```text
Slice 1.7 manual evaluator-result capture
technical acceptance
accepted-baseline promotion
transition to ACCEPTED through 1.6 controls
Slice 1.7 opening
agent execution
AgentRuntime/OpenCode execution
provider/repository mutation
automatic Human approval
grant revocation/expiry
generic workflow/command framework
React/TypeScript/Node/Vite
final JSON/OpenAPI API
multi-user authentication/organizations/RBAC
async persistence redesign
SQLite connection pooling
background jobs/workers
websocket/SSE/polling notification system
unrelated refactors/toolchain changes
```

---

# 22. Stop / escalation conditions

STOP and report before continuing if any of these appears necessary:

```text
schema migration
lifecycle transition-matrix change
governance/domain semantic change
new Human authority semantic
revocation/expiry semantics
new direct runtime or dev dependency
material production-surface expansion
connection sharing / check_same_thread=False
connection pool
async persistence redesign
repository/provider mutation
Slice 1.7 behavior
agent execution
contradiction between accepted R1/R2/R3 design and current code
```

Do not solve a stop condition by silently widening the implementation.

---

# 23. Implementation candidate handoff

When finished, provide:

```text
implementation baseline SHA
candidate SHA
branch
preferred model
actual executing model
model-provenance deviation, if any
complete changed-file list
summary mapped to accepted design decisions
new runtime dependencies: NONE or explicit escalation
new dev/test dependencies: NONE or explicit escalation
schema migration: NONE or explicit escalation
quality-check outputs
pytest summary
GitHub Actions run/status for exact candidate SHA
git diff --check result
deviations: NONE or explicit list
new-work-discovered: NONE or explicit list
```

Also explicitly state whether accepted production files outside the authorized surface changed and why.

The result is an implementation candidate only.

Do NOT:

```text
accept your own implementation
promote technical acceptance
close Slice 1.6
open Slice 1.7
authorize agent execution
```

Return the exact candidate SHA to an independent implementation evaluator.

**Unblocked ≠ accepted.**
