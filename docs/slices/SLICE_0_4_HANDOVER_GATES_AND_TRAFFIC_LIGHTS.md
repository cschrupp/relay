# Relay Slice 0.4 — Handover Gates, Authorization, Human Decisions, and Traffic Lights

**Slice:** 0.4  
**Phase:** 0 — Protocol and Deterministic Foundation  
**Status:** PROPOSED FOR DESIGN REVIEW  
**Document class:** Lockable record  
**Artifact state:** REVIEW  
**Document revision:** 1  
**Parent:** *Relay — Build Plan and Development Roadmap v0.3*  
**Depends on:** Slice 0.3 — State Machine and Lifecycle Semantics — COMPLETE / ACCEPTED  
**Accepted project baseline:** `e3a8501e0e2a410d04e2e95fd566b01622535016`  
**Design authorization:** Explicit Human Authority request to define Slice 0.4 in detail  
**Implementation authorization:** NOT GRANTED  
**Execution state:** DESIGN ONLY — post-Slice-0.3 hard stop remains active

---

# 1. Objective

Define Relay's deterministic handover-governance layer.

Slice 0.3 answered:

> Is this lifecycle movement structurally possible?

Slice 0.4 answers:

> Is that movement permissible now?

> Are the required engineering prerequisites present?

> Does authority exist?

> Does a human have to act before Relay may execute it?

> Is the handover red, yellow, or green?

The governing composition is:

```text
requested lifecycle movement
          ↓
    Handover Gate
          ↓
  VALIDITY / AUTHORITY / AUTONOMY
          ↓
       traffic light
     RED / YELLOW / GREEN
          ↓
   if selected + GREEN
          ↓
 Slice 0.3 lifecycle engine
```

The deterministic exit condition is:

> Given the same immutable gate definitions, the same baseline, the same lifecycle snapshot, the same prerequisite context, and the same current authorization/human-decision projection, Relay produces the same gate evaluations and the same executable path—or rejects execution with the same governance error category.

No LLM participates in gate evaluation or handover execution.

---

# 2. Foundational Boundary from Slice 0.3

Slice 0.3 remains authoritative for structural lifecycle truth:

```text
SliceLifecycle
    = Phase + Validity + Blockage
```

Slice 0.4 must not redefine that model.

Governance remains separate:

```text
Lifecycle
    answers WHERE THE WORK IS

Handover Gate
    answers WHETHER A MOVEMENT MAY HAPPEN NOW
```

The key invariant remains:

> **Lifecycle truth and transition permission are different things.**

`READY` therefore remains a lifecycle phase.

`AUTHORIZED` remains absent from `LifecyclePhase`.

`HARD_STOP` remains absent from `LifecyclePhase`.

Traffic lights belong to handovers, not slices, agents, or lifecycle phases.

---

# 3. S0.4-D01 — A Handover Gate Evaluates Three Independent Concerns

Every gate evaluates:

```text
VALIDITY
    Are the structural and engineering prerequisites satisfied?

AUTHORITY
    Does explicit permission exist where permission is required?

AUTONOMY
    May Relay perform the handover without another human action?
```

These dimensions must not collapse into one boolean.

Examples:

```text
validity = false
authorization = granted
autonomy = automatic
→ RED
```

because permission cannot override missing engineering prerequisites.

```text
validity = true
authorization = missing
autonomy = automatic
→ YELLOW
```

because the engineering path is valid but a human-remediable authority action is still required.

```text
validity = true
authorization = granted
autonomy = HUMAN_APPROVAL
→ YELLOW until current approval exists
```

```text
validity = true
authorization = granted
autonomy = AUTO
→ GREEN
```

---

# 4. S0.4-D02 — Traffic-Light Semantics Are Normative

The only traffic-light values are:

```text
GREEN
YELLOW
RED
```

Semantics:

## GREEN

The gate is currently executable through the governance API.

All blocking validity conditions are satisfied, required authorization exists, and no unresolved human-action requirement remains.

## YELLOW

No non-overridable validity failure prevents the handover, but at least one required human-remediable authority/autonomy action remains.

Examples:

```text
missing required authorization
human approval required
human choice required
hard-stop confirmation required
material change-surface review required
risk review required
```

## RED

The handover is currently prohibited.

A human approval must never override a red validity condition.

Examples:

```text
wrong source phase
structurally illegal lifecycle transition
baseline mismatch
missing required artifact/evidence
failed or missing required quality evidence
unsatisfied dependency
incompatible evaluation outcome
unauthorized toolchain change
risk policy = BLOCK with flagged risk
change-surface policy = BLOCK with material deviation
explicit current human rejection
multiple simultaneously executable paths
```

Precedence is:

```text
RED > YELLOW > GREEN
```

There is no `UNKNOWN` light in Slice 0.4.

Missing information that is required by a gate is represented by a specific RED or YELLOW reason according to its semantics.

---

# 5. S0.4-D03 — Traffic Lights Belong to Gates

A slice does not become globally GREEN, YELLOW, or RED.

A single lifecycle snapshot may expose multiple outgoing gates with different lights:

```text
EVALUATING

accept                  RED
automatic rework        GREEN
contract escalation     YELLOW
architecture escalation RED
```

The same actor may therefore have access to one green handover and one red handover simultaneously.

No traffic-light field is added to `SliceLifecycle`.

---

# 6. S0.4-D04 — HandoverGate Is an Immutable, Revisioned Specification

Slice 0.4 introduces an immutable serialized `HandoverGate` model.

Conceptually:

```python
HandoverGate(
    schema_version,
    gate_id,
    revision,
    key,
    slice_id,
    baseline_id,
    source_phase,
    target_phase,
    superseded_by_slice_id,
    policy,
    hard_stop,
    authorization_required,
    required_artifact_ids,
    required_evidence_ids,
    required_dependency_slice_ids,
    required_evaluation_outcomes,
    required_quality_checks,
    change_surface_policy,
    risk_policy,
)
```

Normative rules:

```text
schema_version = 1
revision >= 1
key = validated stable slug
source_phase != target_phase
required reference tuples contain no duplicates
required_dependency_slice_ids must not contain slice_id
```

Supersession rule:

```text
target_phase == SUPERSEDED
    → superseded_by_slice_id required

otherwise
    → superseded_by_slice_id must be None
```

The successor must not equal `slice_id`.

The gate is configuration/policy, not runtime mutable state.

A substantive gate-policy change creates a new gate revision.

---

# 7. S0.4-D05 — Gate Revision Is Part of Authority

`gate_id` identifies the logical gate.

`revision` identifies the exact policy definition being evaluated.

An authorization granted against:

```text
gate_id = G
revision = 1
```

must not authorize:

```text
gate_id = G
revision = 2
```

without an explicit new authorization.

Human approvals and choices are likewise bound to the exact gate revision.

Slice 0.4 does not implement a gate revision history store. It defines the immutable values and binding semantics only.

Persistence and historical reconstruction belong to Slice 0.5.

---

# 8. S0.4-D06 — Gate, Authorization, Decisions, and Context Bind to an Exact Baseline

Relay's exact-baseline discipline applies to governance.

`HandoverGate` includes:

```text
baseline_id: BaselineId
```

The evaluation context also supplies the current:

```text
baseline_id
```

A baseline mismatch is RED.

`AuthorizationGrant`, `HumanApprovalDecision`, and `HumanChoiceDecision` also bind to the relevant `baseline_id`.

This prevents permission or approval created for an earlier accepted baseline from silently becoming valid after project authority changes.

Baseline identity is used rather than a moving branch name.

Slice 0.4 does not resolve `BaselineId` from Git or a database; the exact baseline is an explicit input.

---

# 9. S0.4-D07 — New Governance IDs Extend the Existing ID Mechanism Narrowly

Slice 0.4 extends the accepted UUIDv7 ID vocabulary with:

```text
HandoverGateId     gate_<uuid7>
AuthorizationId    auth_<uuid7>
HumanDecisionId    hdec_<uuid7>
```

These use the existing `new_id()` mechanism.

ID generation occurs explicitly at the caller boundary.

The gate engine itself performs no UUID generation.

No second identifier framework is introduced.

---

# 10. S0.4-D08 — Slice 0.4 Adds an Eventless Lifecycle Validation Query

Slice 0.3 already contains the authoritative structural phase-transition validator internally.

Governance must consult the same logic without manufacturing a fake lifecycle event.

Slice 0.4 therefore authorizes one narrow, backward-compatible public lifecycle query:

```python
validate_phase_transition(
    current: SliceLifecycle,
    target_phase: LifecyclePhase,
    superseded_by_slice_id: SliceId | None = None,
) -> None
```

Semantics:

- pure;
- no state mutation;
- no event creation;
- no IDs;
- no timestamps;
- no I/O;
- same structural transition rules as `transition_phase()`;
- raises the existing lifecycle error family on structural invalidity.

`transition_phase()` must reuse the same underlying validation logic.

The governance engine must not duplicate Slice 0.3's transition matrix.

---

# 11. S0.4-D09 — Slice 0.4 Gates Lifecycle Transitions, Not Agent Assignment

A Slice 0.4 gate governs one proposed lifecycle movement for one slice.

It does not yet assign work to an AgentRole or AgentAssignment.

Therefore a gate binds:

```text
slice_id
source_phase
target_phase
```

and may contain prerequisites and policy.

Role-only handovers with no lifecycle movement are out of scope in Slice 0.4.

Agent assignment and structured agent execution arrive in later phases.

This keeps Phase 0 focused on deterministic governance rather than orchestration.

---

# 12. S0.4-D10 — Authorization Is Durable Permission, Not Execution-Time Approval

Slice 0.4 introduces:

```text
AuthorizationGrant
```

Conceptually:

```python
AuthorizationGrant(
    schema_version,
    authorization_id,
    slice_id,
    baseline_id,
    gate_id,
    gate_revision,
    actor,
    granted_at,
    reason,
)
```

Rules:

```text
schema_version = 1
actor.kind = HUMAN in Slice 0.4
granted_at timezone-aware and UTC-normalized
reason non-empty / non-whitespace
```

Authorization binds to:

```text
slice
baseline
gate identity
gate revision
```

Authorization deliberately does **not** bind to lifecycle revision.

This allows permission to be granted before other prerequisites become valid.

Example:

```text
implementation authorization GRANTED
+
design acceptance missing
→ gate remains RED

later design acceptance appears
+
same exact authorization remains valid
→ gate may become GREEN without requiring a second authorization
```

This is the intended difference between durable permission and execution-time approval.

Slice 0.4 models active grants only.

Revocation, expiry, authorization history, and permission administration are deferred to persistence/identity work.

A caller representing current project state omits grants that are no longer active.

---

# 13. S0.4-D11 — Missing Authorization Is YELLOW, Not RED

When a gate declares:

```text
authorization_required = True
```

and every validity prerequisite is otherwise satisfied, absence of a matching current authorization produces:

```text
YELLOW
AUTHORIZATION_REQUIRED
```

because obtaining authorization is a human-remediable authority action.

If an authorization exists for the same logical gate but the baseline or gate revision no longer matches, the reason is:

```text
AUTHORIZATION_STALE
```

and the gate remains YELLOW unless a RED condition also exists.

Authorization never overrides a RED validity reason.

---

# 14. S0.4-D12 — Human Decisions Are Execution-Time Decisions

Human decisions are distinct from authorization.

They bind to the exact current lifecycle revision so that an approval cannot silently survive a state change.

Slice 0.4 introduces two immutable decision types.

## HumanApprovalDecision

```python
HumanApprovalDecision(
    schema_version,
    decision_id,
    slice_id,
    baseline_id,
    gate_id,
    gate_revision,
    lifecycle_revision,
    actor,
    occurred_at,
    decision,
    reason,
)
```

where:

```text
decision = APPROVE | REJECT
actor.kind = HUMAN
```

## HumanChoiceDecision

```python
HumanChoiceDecision(
    schema_version,
    decision_id,
    slice_id,
    baseline_id,
    selected_gate_id,
    selected_gate_revision,
    lifecycle_revision,
    actor,
    occurred_at,
    reason,
)
```

where:

```text
actor.kind = HUMAN
```

Both timestamps are explicit, timezone-aware, and UTC-normalized.

Human decisions do not mutate lifecycle state by themselves.

---

# 15. S0.4-D13 — Current Context Is a Projection, Not Decision History

`HandoverContext` represents the current facts used for one deterministic evaluation.

It is not the audit/event history.

The context may contain at most one current approval decision for an exact:

```text
baseline_id + gate_id + gate_revision + lifecycle_revision
```

and at most one current human choice for the current:

```text
baseline_id + lifecycle_revision
```

Historical superseded approvals/choices belong to Slice 0.5 persistence/event history, not the current evaluation projection.

This avoids hidden "latest decision wins" logic and clock-based arbitration inside Slice 0.4.

---

# 16. S0.4-D14 — Handover Policies

The autonomy policy enum is:

```text
AUTO
AUTO_NOTIFY
HUMAN_APPROVAL
HUMAN_CHOICE
```

## AUTO

No policy-level human action is required.

If validity and authority pass, the gate may be GREEN.

## AUTO_NOTIFY

Same traffic-light semantics as AUTO.

If validity and authority pass, the gate may be GREEN.

Notification delivery is explicitly out of scope.

The future caller can inspect the gate policy and issue notification after execution.

## HUMAN_APPROVAL

A current matching `HumanApprovalDecision(APPROVE)` is required.

Without it:

```text
YELLOW
HUMAN_APPROVAL_REQUIRED
```

A current matching `REJECT` produces RED.

## HUMAN_CHOICE

A current `HumanChoiceDecision` must select this exact gate/revision at the current lifecycle revision.

Without a current valid choice:

```text
YELLOW
HUMAN_CHOICE_REQUIRED
```

Human choice is evaluated over the full outgoing gate set, not one gate in isolation.

---

# 17. S0.4-D15 — Hard Stop Is Gate Policy, Not Lifecycle State

`HandoverGate` contains:

```text
hard_stop: bool
```

When `hard_stop = True`, the gate cannot become GREEN without a current positive human decision that directly names the gate.

A positive decision is:

- `HumanApprovalDecision(APPROVE)` for the exact gate; or
- `HumanChoiceDecision` selecting the exact gate when the gate policy is `HUMAN_CHOICE`.

If no such decision exists:

```text
YELLOW
HARD_STOP_REQUIRES_HUMAN
```

Hard stop dominates AUTO and AUTO_NOTIFY.

Examples:

```text
policy = AUTO
hard_stop = True
validity = pass
authorization = present
human approval = absent
→ YELLOW
```

```text
policy = AUTO
hard_stop = True
validity = pass
authorization = present
human approval = APPROVE
→ GREEN
```

A human decision cannot turn a structurally RED gate green.

---

# 18. S0.4-D16 — Evaluation Outcome Is a Typed Gate Input

Slice 0.4 introduces the minimal typed evaluation-outcome vocabulary needed for routing:

```text
ACCEPT
REWORK
ESCALATE_CONTRACT
ESCALATE_ARCHITECTURE
BLOCKED
EXPERIMENT_REQUIRED
```

This is an input fact, not a full persisted `Evaluation` domain object.

A gate may declare:

```text
required_evaluation_outcomes: tuple[EvaluationOutcome, ...]
```

Rules:

```text
empty tuple
    → no evaluation outcome required

non-empty tuple + no current outcome
    → RED / EVALUATION_REQUIRED

current outcome not in allowed tuple
    → RED / EVALUATION_OUTCOME_NOT_ALLOWED
```

Examples:

```text
EVALUATING → ACCEPTED
required outcome = ACCEPT
```

```text
EVALUATING → REWORK
required outcome = REWORK
```

```text
EVALUATING → CONTRACTING
required outcome = ESCALATE_CONTRACT
```

```text
EVALUATING → DESIGNING
required outcome = ESCALATE_ARCHITECTURE
```

The full Evaluation record, findings model, and evaluator execution workflow are deferred.

---

# 19. S0.4-D17 — Exact Artifact and Evidence Prerequisites

A gate may require exact existing domain IDs:

```text
required_artifact_ids: tuple[ArtifactId, ...]
required_evidence_ids: tuple[EvidenceId, ...]
```

`HandoverContext` supplies the exact currently available IDs.

Missing required IDs are RED:

```text
MISSING_REQUIRED_ARTIFACT
MISSING_REQUIRED_EVIDENCE
```

Slice 0.4 does not resolve file names, canonical keys, Git paths, artifact maturity, or supersession chains.

Those repository/canonical-registry semantics remain deferred to Slice 0.6.

Using exact IDs prevents the gate engine from guessing authority from file names or repository recency.

---

# 20. S0.4-D18 — Dependency Readiness Means ACCEPTED + CURRENT

A gate may require:

```text
required_dependency_slice_ids: tuple[SliceId, ...]
```

For each required dependency, `HandoverContext` supplies its `SliceLifecycle` snapshot.

The dependency requirement passes only when:

```text
phase = ACCEPTED
validity = CURRENT
```

Failure reasons:

```text
dependency lifecycle absent
    → DEPENDENCY_MISSING

phase != ACCEPTED
    → DEPENDENCY_NOT_ACCEPTED

phase == ACCEPTED and validity == STALE
    → DEPENDENCY_STALE
```

`SUPERSEDED` does not satisfy an `ACCEPTED` dependency requirement; the consuming work should reference the appropriate current successor explicitly.

Cross-project lookup is out of scope because no persistence layer exists yet.

---

# 21. S0.4-D19 — Required Quality Checks Are Explicit Named Facts

Slice 0.4 introduces:

```text
QualityCheckStatus
    PASS
    FAIL
```

and:

```python
QualityCheckResult(
    key,
    status,
)
```

Quality keys are validated stable slugs.

A gate declares:

```text
required_quality_checks: tuple[str, ...]
```

The context supplies current check results.

Semantics:

```text
required key absent
    → RED / QUALITY_CHECK_MISSING

required key present with FAIL
    → RED / QUALITY_CHECK_FAILED

required key present with PASS
    → satisfied
```

Slice 0.4 does not execute the tools that produce these facts.

It only consumes the declared results deterministically.

---

# 22. S0.4-D20 — Change-Surface Policy Is Deterministic

The current change-surface status is:

```text
WITHIN_DECLARED
MATERIAL_DEVIATION
```

Each gate declares:

```text
change_surface_policy:
    ALLOW
    HUMAN_REVIEW
    BLOCK
```

Semantics when status is `MATERIAL_DEVIATION`:

```text
ALLOW
    → no gate effect

HUMAN_REVIEW
    → YELLOW / CHANGE_SURFACE_REVIEW_REQUIRED
       until current HumanApprovalDecision(APPROVE)

BLOCK
    → RED / CHANGE_SURFACE_BLOCKED
```

A current human rejection remains RED.

This operationalizes the accepted scope/simplicity policy without creating a new lifecycle state.

---

# 23. S0.4-D21 — Risk Policy Consumes a Flag, It Does Not Calculate Risk

Slice 0.4 does not implement a risk-scoring engine.

The context provides:

```text
RiskStatus
    CLEAR
    FLAGGED
```

Each gate declares:

```text
risk_policy:
    ALLOW
    HUMAN_REVIEW
    BLOCK
```

When risk is `FLAGGED`:

```text
ALLOW
    → no gate effect

HUMAN_REVIEW
    → YELLOW / RISK_REVIEW_REQUIRED
       until current HumanApprovalDecision(APPROVE)

BLOCK
    → RED / RISK_BLOCKED
```

The origin of the risk flag is outside Slice 0.4.

This keeps risk calculation separable from deterministic gate enforcement.

---

# 24. S0.4-D22 — Unauthorized Toolchain Change Is Always RED

The current toolchain-change status is:

```text
NONE
AUTHORIZED
UNAUTHORIZED
```

Semantics:

```text
NONE
    → no gate effect

AUTHORIZED
    → no gate effect

UNAUTHORIZED
    → RED / UNAUTHORIZED_TOOLCHAIN_CHANGE
```

A human approval decision does not override an unauthorized toolchain change.

The proper remediation is to obtain authority and update the context, not to bypass the finding.

---

# 25. S0.4-D23 — HandoverContext

Slice 0.4 introduces one immutable current-context model.

Conceptually:

```python
HandoverContext(
    schema_version,
    baseline_id,
    lifecycle,
    available_artifact_ids,
    available_evidence_ids,
    dependency_lifecycles,
    evaluation_outcome,
    authorization_grants,
    human_decisions,
    quality_checks,
    change_surface_status,
    risk_status,
    toolchain_change_status,
)
```

All public models follow existing Relay model discipline:

```text
immutable
schema_version = 1
extra fields forbidden
JSON-compatible serialization
JSON round trip
JSON Schema generation
```

Uniqueness requirements:

```text
artifact IDs unique
evidence IDs unique
dependency lifecycles unique by slice_id
quality checks unique by key
authorization IDs unique
human decision IDs unique
```

The context is explicit data.

The gate engine performs no repository, database, GitHub, filesystem, CI, model, or network lookup.

---

# 26. S0.4-D24 — Current Authorization Projection Must Be Unambiguous

`HandoverContext` may contain authorization grants for several gates.

For one exact:

```text
baseline_id + gate_id + gate_revision
```

at most one active authorization grant may be present in the current projection.

Slice 0.4 does not choose among duplicate grants by timestamp.

A caller needing historical grant/revoke chronology must use the future persistence/event layer.

---

# 27. S0.4-D25 — GateEvaluation Is an Immutable Derived Result

Each gate evaluation returns:

```python
GateEvaluation(
    schema_version,
    gate_id,
    gate_revision,
    slice_id,
    baseline_id,
    lifecycle_revision,
    target_phase,
    light,
    reasons,
)
```

`GateEvaluation` does not contain generated IDs or timestamps.

It is a deterministic derivation of explicit inputs.

A GREEN evaluation has:

```text
reasons = ()
```

A YELLOW or RED evaluation contains one or more typed reasons.

The evaluation is bound to the lifecycle revision and gate revision that produced it.

---

# 28. S0.4-D26 — Gate Reasons Are Typed and Deterministically Ordered

Slice 0.4 introduces:

```text
GateReasonKind
    BLOCKING
    HUMAN_ACTION
```

and a closed initial `GateReasonCode` enum.

Required codes:

```text
BASELINE_MISMATCH
SOURCE_PHASE_MISMATCH
INVALID_LIFECYCLE_TRANSITION
MISSING_REQUIRED_ARTIFACT
MISSING_REQUIRED_EVIDENCE
DEPENDENCY_MISSING
DEPENDENCY_NOT_ACCEPTED
DEPENDENCY_STALE
EVALUATION_REQUIRED
EVALUATION_OUTCOME_NOT_ALLOWED
QUALITY_CHECK_MISSING
QUALITY_CHECK_FAILED
CHANGE_SURFACE_BLOCKED
CHANGE_SURFACE_REVIEW_REQUIRED
RISK_BLOCKED
RISK_REVIEW_REQUIRED
UNAUTHORIZED_TOOLCHAIN_CHANGE
AUTHORIZATION_REQUIRED
AUTHORIZATION_STALE
HUMAN_APPROVAL_REQUIRED
HUMAN_CHOICE_REQUIRED
HUMAN_DECISION_STALE
HARD_STOP_REQUIRES_HUMAN
HUMAN_REJECTED
NOT_SELECTED_BY_HUMAN
MULTIPLE_EXECUTABLE_PATHS
```

Conceptually:

```python
GateReason(
    kind,
    code,
    subject,
)
```

`subject` may identify the relevant artifact ID, evidence ID, dependency slice ID, quality-check key, or gate ID where useful.

It is a scalar string or `None`; there is no generic metadata dictionary.

Reasons are returned in a fixed canonical order defined by the engine, with same-code subjects ordered lexicographically.

Input tuple order must not change semantic reason ordering.

---

# 29. S0.4-D27 — Human Decisions Cannot Override Blocking Reasons

Gate evaluation collects independent reasons.

A current human approval may satisfy only requirements explicitly classified as human-remediable:

```text
HUMAN_APPROVAL_REQUIRED
HARD_STOP_REQUIRES_HUMAN
CHANGE_SURFACE_REVIEW_REQUIRED
RISK_REVIEW_REQUIRED
```

A human choice may satisfy `HUMAN_CHOICE_REQUIRED` for the selected gate.

Neither approval nor choice can remove:

```text
BASELINE_MISMATCH
INVALID_LIFECYCLE_TRANSITION
missing required artifact/evidence
dependency failure
evaluation mismatch
quality failure
BLOCK policy result
unauthorized toolchain change
```

This prevents "approve anyway" from bypassing deterministic engineering constraints.

---

# 30. S0.4-D28 — Current Human Rejection Is Explicitly Blocking

A current matching:

```text
HumanApprovalDecision(decision = REJECT)
```

produces:

```text
RED / HUMAN_REJECTED
```

Rejection is bound to the same:

```text
baseline
gate revision
lifecycle revision
```

A rejection from an older lifecycle revision is stale and does not block the new state.

Slice 0.4 does not mutate or delete the historical rejected decision; the current context simply does not treat it as current after lifecycle revision changes.

---

# 31. S0.4-D29 — Stale Authorization and Stale Human Decisions Are Different

Authorization is durable permission and is not bound to lifecycle revision.

Therefore a lifecycle revision change does not by itself stale a matching authorization grant.

Authorization becomes stale when its:

```text
baseline_id
gate_id
gate_revision
```

no longer match.

Human approval/choice is execution-time authority and binds to lifecycle revision.

Therefore a lifecycle revision change invalidates the previous decision for execution.

If the gate currently requires human action and only an older matching decision exists, evaluation includes:

```text
HUMAN_DECISION_STALE
```

plus the applicable current human-action requirement.

---

# 32. S0.4-D30 — HUMAN_CHOICE Is Evaluated Across the Outgoing Gate Set

Public gate evaluation operates on the full current outbound gate set:

```python
evaluate_handover_gates(
    gates: tuple[HandoverGate, ...],
    context: HandoverContext,
) -> tuple[GateEvaluation, ...]
```

All gates in one call must target the same:

```text
slice_id
baseline_id
```

and are evaluated against the same lifecycle snapshot.

A current `HumanChoiceDecision` selects one exact gate/revision at the current lifecycle revision.

If the selected gate is currently structurally/prerequisite valid, that choice satisfies `HUMAN_CHOICE_REQUIRED` for the selected gate.

Other currently viable `HUMAN_CHOICE` gates receive:

```text
RED / NOT_SELECTED_BY_HUMAN
```

for that current choice projection.

A choice cannot make an otherwise RED selected gate executable.

If a choice refers to a missing gate, wrong gate revision, wrong baseline, or old lifecycle revision, it is stale and does not satisfy the current choice requirement.

---

# 33. S0.4-D31 — Relay Never Arbitrarily Chooses Between Multiple Executable Paths

After all gate-local validity, authority, and autonomy conditions are evaluated, Relay checks the set-level result.

The engine must never return more than one GREEN gate for the same lifecycle snapshot.

If two or more gates would otherwise be GREEN, each provisional GREEN gate becomes:

```text
RED / MULTIPLE_EXECUTABLE_PATHS
```

This is a governance/configuration conflict.

Relay must not select:

- the first gate in tuple order;
- the lexicographically smallest gate;
- the newest gate;
- a random gate;
- an LLM-preferred gate.

Expected alternatives must instead be disambiguated by mutually exclusive prerequisites or explicit `HUMAN_CHOICE` policy/current choice.

---

# 34. S0.4-D32 — Gate Evaluation Algorithm

For each call to `evaluate_handover_gates()`:

## Step 1 — Validate the gate set

Reject malformed set structure such as:

```text
empty gate set
duplicate gate_id
mixed slice_id
mixed baseline_id
gate slice does not match context lifecycle slice
gate baseline does not match context baseline at the structural set level
```

Baseline mismatch may alternatively be represented per gate when all gates consistently reference one other baseline; implementation must follow one documented behavior consistently. Revision 1 recommends rejecting mixed gate baselines structurally and returning per-gate `BASELINE_MISMATCH` for a uniform set targeting a non-current baseline.

## Step 2 — Evaluate structural lifecycle validity

Check:

```text
source_phase matches current lifecycle phase
validate_phase_transition() passes
```

## Step 3 — Evaluate engineering prerequisites

Check:

```text
required artifact IDs
required evidence IDs
required dependencies
required evaluation outcome
required quality checks
change-surface BLOCK policy
risk BLOCK policy
unauthorized toolchain change
```

## Step 4 — Evaluate explicit current rejection

Matching current `REJECT` is blocking.

## Step 5 — Evaluate authorization

If required and no current matching authorization exists, add YELLOW authority reason.

## Step 6 — Evaluate human-remediable review conditions

Check:

```text
change-surface HUMAN_REVIEW
risk HUMAN_REVIEW
hard stop
HUMAN_APPROVAL policy
```

A single exact current APPROVE decision may satisfy all approval-type requirements for that gate at that lifecycle revision.

## Step 7 — Evaluate HUMAN_CHOICE across the gate set

Apply current valid selection, stale-choice semantics, and non-selected reasons.

## Step 8 — Derive provisional light

```text
any BLOCKING reason
    → RED
else any HUMAN_ACTION reason
    → YELLOW
else
    → GREEN
```

## Step 9 — Enforce unique executable path

If more than one provisional GREEN remains:

```text
all provisional GREEN gates
    → RED / MULTIPLE_EXECUTABLE_PATHS
```

## Step 10 — Canonicalize reason order

Return evaluations in the same order as the input gate tuple.

Within each evaluation, reasons use canonical engine ordering.

---

# 35. S0.4-D33 — Handover Execution Re-Evaluates Governance

Slice 0.4 introduces a governed execution operation conceptually equivalent to:

```python
execute_handover(
    gates,
    selected_gate_id,
    context,
    event_id,
    actor,
    occurred_at,
    reason,
) -> tuple[SliceLifecycle, PhaseChanged, GateEvaluation]
```

Execution rules:

1. call `evaluate_handover_gates(gates, context)` internally;
2. locate `selected_gate_id`;
3. require its light to be GREEN;
4. call Slice 0.3 `transition_phase()` with the gate target and successor reference;
5. return the resulting lifecycle snapshot, `PhaseChanged` event, and the exact gate evaluation used.

The function must not accept a caller-constructed GREEN `GateEvaluation` as sufficient authority.

It re-evaluates from gate definitions and context so a forged or stale evaluation cannot bypass governance.

`event_id`, `actor`, `occurred_at`, and `reason` remain explicit Slice 0.3 lifecycle-operation inputs.

The lifecycle event actor records who caused execution; it does not itself prove authority.

If the selected gate is RED or YELLOW, execution raises a typed governance error and produces no lifecycle event.

---

# 36. S0.4-D34 — GateEvaluation Is Evidence, Not Persistence

A `GateEvaluation` is an immutable deterministic value returned by the engine.

Slice 0.4 does not persist it.

`execute_handover()` returns the evaluation used so later persistence can preserve the decision context.

Slice 0.5 will decide how gate evaluations, authorizations, human decisions, and handover executions become durable event/history records.

Slice 0.4 must not add a database, event store, repository layer, or transaction abstraction in anticipation of that work.

---

# 37. S0.4-D35 — AUTO_NOTIFY Has No Notification Side Effect in Slice 0.4

`AUTO_NOTIFY` differs from `AUTO` only as policy metadata for a future orchestrator.

It has the same traffic-light calculation as AUTO.

Slice 0.4 does not:

```text
send email
send Slack messages
create GitHub notifications
invoke webhooks
queue notification jobs
```

No notification interface or provider abstraction is introduced.

---

# 38. S0.4-D36 — The Gate Engine Is Pure and Provider-Neutral

The gate engine performs no:

```text
clock reads
UUID generation
randomness
filesystem access
Git access
GitHub access
database access
HTTP/network access
LLM/model calls
notification calls
CI execution
quality-tool execution
artifact discovery
```

All relevant facts are explicit immutable inputs.

Therefore:

```text
same gates
+
same context
=
same GateEvaluation tuple
```

and:

```text
same executable handover inputs
=
same lifecycle result + PhaseChanged event + GateEvaluation
```

subject to the already accepted deterministic Slice 0.3 lifecycle contract.

---

# 39. S0.4-D37 — Handover Packets Are Not Implemented Yet

The Product Proposal describes structured handover packets containing accepted authority, scope, memory, repository context, and risks.

Packet construction requires repository artifact discovery and later agent/role context.

Slice 0.4 therefore does not implement:

```text
HandoverPacket
context assembly
role prompt construction
repository file selection
agent conversation transfer
```

The gate engine establishes whether a handover is permissible.

A later slice will construct the receiving agent's context when agent execution exists.

---

# 40. S0.4-D38 — Authorization Is Not Identity/RBAC

Slice 0.4 models an explicit active authorization grant supplied as current governance context.

It does not implement:

```text
user accounts
organizations
roles/permissions
OAuth
ACLs
policy administration
who is allowed to create an AuthorizationGrant
cryptographic signatures
```

For the Phase 0 implementation, an `AuthorizationGrant` must identify a HUMAN actor.

The application layer is responsible for ensuring only a legitimate human authority can create the grant.

A later production identity/permissions system may broaden or harden grant authority without changing the core distinction between authorization and lifecycle state.

---

# 41. S0.4-D39 — Governance Models Are Separate from Slice Definition

Do not add authorization, gates, traffic lights, quality status, risk status, or human decisions to the Slice 0.2 `Slice` model.

The domain boundaries remain:

```text
Slice
    intended bounded work

SliceLifecycle
    structural work state

HandoverGate
    governance policy for one possible movement

HandoverContext
    current facts used to evaluate that policy

AuthorizationGrant
    active durable permission

HumanGateDecision
    current execution-time human authority

GateEvaluation
    deterministic derived decision
```

This separation avoids turning `Slice` into a mutable workflow aggregate.

---

# 42. Public Governance Types

Required public vocabulary:

```text
HandoverGateId
AuthorizationId
HumanDecisionId

TrafficLight
HandoverPolicy
ReviewPolicy
EvaluationOutcome
QualityCheckStatus
ChangeSurfaceStatus
RiskStatus
ToolchainChangeStatus
HumanApprovalValue
GateReasonKind
GateReasonCode

HandoverGate
AuthorizationGrant
HumanApprovalDecision
HumanChoiceDecision
HumanGateDecision
QualityCheckResult
HandoverContext
GateReason
GateEvaluation
```

A materially different public vocabulary requires design review before implementation.

Private helper decomposition remains implementation discretion.

---

# 43. Public Governance Operations

Required public capability:

```python
evaluate_handover_gates(...)
execute_handover(...)
```

and the narrow Slice 0.3 query:

```python
validate_phase_transition(...)
```

No public repository/service/provider abstraction is required.

---

# 44. Governance Error Family

The public governance error family is:

```text
GovernanceError
├── InvalidGateSet
├── InvalidHandoverContext
└── HandoverNotExecutable
```

Semantics:

- `InvalidGateSet` — the supplied outgoing gate set is structurally inconsistent for evaluation.
- `InvalidHandoverContext` — a validly shaped context contains mutually ambiguous current-projection facts that cannot be interpreted deterministically.
- `HandoverNotExecutable` — `execute_handover()` was asked to execute a gate that is absent, RED, or YELLOW.

Normal missing prerequisites are not exceptions during evaluation. They produce gate reasons and traffic lights.

Pydantic/schema validation remains responsible for malformed individual serialized models.

Lifecycle structural errors remain owned by the Slice 0.3 lifecycle error family.

---

# 45. Required Gate Scenarios

Implementation tests must cover at least the following scenarios.

## Valid and automatically authorized

```text
READY / CURRENT / CLEAR
required prerequisites present
authorization present
policy AUTO
→ GREEN
```

## Authorization pre-granted before prerequisite completion

```text
authorization present
required design artifact missing
→ RED

same authorization
artifact later present
→ GREEN
```

No second authorization is required because gate/baseline revision did not change.

## Missing authorization

```text
all validity checks pass
authorization required but absent
→ YELLOW / AUTHORIZATION_REQUIRED
```

## Stale authorization

```text
matching logical gate ID
old gate revision authorization only
→ YELLOW / AUTHORIZATION_STALE
```

## HUMAN_APPROVAL

```text
valid + authorized + no decision
→ YELLOW

current APPROVE
→ GREEN

current REJECT
→ RED
```

## Hard stop with AUTO

```text
valid + authorized + AUTO + hard_stop
no human approval
→ YELLOW

current APPROVE
→ GREEN
```

## HUMAN_CHOICE

```text
two currently valid HUMAN_CHOICE gates
no choice
→ both YELLOW

human selects one
→ selected gate eligible to become GREEN
→ other viable choice gate RED / NOT_SELECTED_BY_HUMAN
```

## Invalid chosen path

```text
human choice selects a gate whose prerequisites are now RED
→ selected gate remains RED
→ human choice does not override validity
```

## Multiple executable paths

```text
two gates provisionally GREEN
→ both RED / MULTIPLE_EXECUTABLE_PATHS
```

## Dependency accepted/current

```text
required dependency = ACCEPTED + CURRENT
→ passes
```

## Dependency stale

```text
required dependency = ACCEPTED + STALE
→ RED / DEPENDENCY_STALE
```

## Evaluation routing

```text
outcome ACCEPT
→ acceptance gate can pass outcome check
→ rework/escalation gates fail outcome check
```

Equivalent cases required for REWORK, ESCALATE_CONTRACT, and ESCALATE_ARCHITECTURE.

## Quality evidence

```text
required check absent
→ RED

required check FAIL
→ RED

required check PASS
→ passes
```

## Material change-surface review

```text
MATERIAL_DEVIATION + HUMAN_REVIEW + no approval
→ YELLOW

current approval
→ passes

MATERIAL_DEVIATION + BLOCK
→ RED
```

## Risk review

Equivalent ALLOW / HUMAN_REVIEW / BLOCK behavior.

## Unauthorized toolchain change

```text
UNAUTHORIZED
→ RED regardless of human approval
```

## Stale human approval

```text
approval lifecycle_revision = N
current lifecycle_revision = N + 1
→ approval does not satisfy gate
```

## Governed execution

```text
GREEN selected gate
→ one Slice 0.3 PhaseChanged event
→ resulting snapshot matches direct structural transition
```

```text
YELLOW or RED selected gate
→ HandoverNotExecutable
→ no lifecycle event
```

---

# 46. Explicit In Scope

Slice 0.4 design authorizes a future implementation, only after separate Human Authority implementation authorization, of:

1. governance ID types `gate_`, `auth_`, `hdec_`;
2. `TrafficLight`;
3. `HandoverPolicy`;
4. `ReviewPolicy`;
5. minimal `EvaluationOutcome` routing enum;
6. quality/change-surface/risk/toolchain current-fact enums;
7. `HandoverGate` immutable revisioned specification;
8. exact baseline binding;
9. `AuthorizationGrant`;
10. `HumanApprovalDecision`;
11. `HumanChoiceDecision`;
12. current-projection `HandoverContext`;
13. exact artifact/evidence prerequisite checks;
14. dependency `ACCEPTED + CURRENT` checks;
15. required evaluation-outcome checks;
16. required quality-check checks;
17. change-surface review policy;
18. risk review policy;
19. unauthorized toolchain-change blocking;
20. hard-stop enforcement;
21. set-level HUMAN_CHOICE semantics;
22. typed gate reasons;
23. deterministic traffic-light derivation;
24. no-more-than-one-GREEN invariant;
25. `GateEvaluation`;
26. `evaluate_handover_gates()`;
27. `execute_handover()` governance wrapper;
28. narrow eventless `validate_phase_transition()` lifecycle query;
29. governance unit/schema tests;
30. governance architecture documentation;
31. ADR-0004;
32. Slice 0.4 development memory;
33. `CURRENT_BASELINE.md` candidate projection update during implementation.

---

# 47. Explicit Out of Scope

Forbidden in Slice 0.4 implementation unless separately authorized:

```text
agent execution
AgentRole / AgentAssignment
handover packet assembly
prompt/context assembly
notifications or notification providers
UI / board
REST/API layer
database
persistence repositories
event store
transactions
schema migrations
Git/GitHub integration
artifact registry
canonical document discovery
file/path-based artifact discovery
RBAC / identity / organizations
authorization expiry/revocation history
risk scoring engine
quality command execution
CI provider integration
change-surface computation
evaluator agent execution
full Evaluation domain record
research execution
experiments
provider/model integration
background queues
webhooks
```

Do not create placeholder implementations for these concepts.

---

# 48. Expected Implementation Change Surface

Expected existing production files touched:

```text
src/relay_engine/domain/ids.py
src/relay_engine/domain/__init__.py
src/relay_engine/lifecycle/engine.py
src/relay_engine/lifecycle/__init__.py
```

Lifecycle modification is limited to exposing the eventless structural validation query without changing existing transition semantics.

Expected new production area:

```text
src/relay_engine/governance/
```

A reasonable minimum-sufficient package is:

```text
__init__.py
models.py
engine.py
errors.py
```

No additional module is required merely to separate enums or reasons if the code remains clearer in these files.

Expected tests:

```text
tests/unit/test_governance.py
```

Existing domain/lifecycle tests may be modified narrowly for new IDs and the validation query.

Expected new runtime dependencies:

```text
0
```

Expected new development dependencies:

```text
0
```

Forbidden architectural expansion:

```text
generic policy language
rules DSL
expression parser
plugin policy engine
event bus
repository/service layer
DI framework
workflow framework
state-machine framework
notification abstraction
persistence abstraction
generic facts dictionary
untyped metadata bag
```

Use direct Python/Pydantic models and explicit deterministic logic.

---

# 49. Required Documentation During Implementation

Implementation should create:

```text
docs/architecture/HANDOVER_GOVERNANCE.md
docs/decisions/ADR-0004-handover-governance-separation.md
docs/slices/SLICE_0_4_HANDOVER_GATES_MEMORY.md
```

ADR-0004 must record at minimum:

1. gates evaluate validity, authority, and autonomy separately;
2. traffic lights belong to handovers;
3. authorization is durable permission, not lifecycle phase or execution-time approval;
4. human decisions bind lifecycle revision;
5. gates and authorizations bind exact baseline and gate revision;
6. hard stop is gate policy, not lifecycle state;
7. human decisions cannot override RED validity;
8. HUMAN_CHOICE is evaluated across outgoing gates;
9. Relay never arbitrarily chooses among multiple executable paths;
10. gate evaluation is pure and provider-neutral;
11. governed execution re-evaluates context and then delegates to Slice 0.3 lifecycle transition;
12. persistence/notifications/agents remain deferred.

Before Slice 0.4 human acceptance:

```text
ADR-0004 = PROPOSED / VALIDATED / PENDING ACCEPTANCE
Slice 0.4 memory = IMPLEMENTATION COMPLETE / PENDING EVALUATION
```

Neither is locked before acceptance.

---

# 50. Acceptance Matrix

All criteria are mandatory unless the accepted design is explicitly revised.

| ID | Requirement | Evidence |
|---|---|---|
| A01 | Governance remains separate from `Slice` and `SliceLifecycle` | inspection |
| A02 | Traffic light enum is exactly GREEN/YELLOW/RED | schema/unit test |
| A03 | Gate evaluates validity, authority, and autonomy separately | scenario tests |
| A04 | RED dominates YELLOW and GREEN | unit tests |
| A05 | Human approval cannot override RED prerequisite failures | unit tests |
| A06 | Traffic lights are per-gate, not stored on lifecycle | inspection |
| A07 | `HandoverGate` immutable/versioned/extra-forbid | schema tests |
| A08 | Gate revision starts at >=1 | schema test |
| A09 | Gate source and target phases differ | schema test |
| A10 | Supersession gate requires distinct successor | schema/unit test |
| A11 | Gates bind exact `BaselineId` | schema/unit test |
| A12 | `gate_`, `auth_`, `hdec_` extend existing UUIDv7 mechanism | ID tests |
| A13 | Governance engine generates no IDs | inspection |
| A14 | Eventless `validate_phase_transition()` exposed | unit test/API inspection |
| A15 | Validation query and live transition use same structural rules | regression tests |
| A16 | Governance does not duplicate lifecycle transition table | inspection |
| A17 | Authorization grant immutable and baseline/gate-revision bound | schema tests |
| A18 | Authorization grant requires HUMAN actor in Slice 0.4 | schema test |
| A19 | Authorization does not bind lifecycle revision | schema/inspection |
| A20 | Missing required authorization produces YELLOW | unit test |
| A21 | Old baseline/gate-revision authorization is stale | unit tests |
| A22 | Human approval binds lifecycle revision | schema/unit tests |
| A23 | Human choice binds lifecycle revision | schema/unit tests |
| A24 | Current matching REJECT produces RED | unit test |
| A25 | Old lifecycle-revision decision cannot authorize current handover | unit test |
| A26 | AUTO can become GREEN without policy-level human decision | unit test |
| A27 | AUTO_NOTIFY has AUTO light semantics and no notification side effect | test/inspection |
| A28 | HUMAN_APPROVAL requires current APPROVE | unit tests |
| A29 | HUMAN_CHOICE evaluated across gate set | scenario tests |
| A30 | Hard stop overrides automatic policy | unit tests |
| A31 | Positive current human decision can satisfy hard stop | unit tests |
| A32 | Hard stop remains unable to override RED validity | unit test |
| A33 | Evaluation outcomes typed and routed deterministically | unit tests |
| A34 | Missing required evaluation outcome produces RED | unit test |
| A35 | Exact artifact prerequisites enforced | unit tests |
| A36 | Exact evidence prerequisites enforced | unit tests |
| A37 | Dependency absent produces RED | unit test |
| A38 | Dependency not ACCEPTED produces RED | unit test |
| A39 | ACCEPTED + STALE dependency produces RED | unit test |
| A40 | ACCEPTED + CURRENT dependency satisfies dependency gate | unit test |
| A41 | Required quality check missing produces RED | unit test |
| A42 | Required quality check FAIL produces RED | unit test |
| A43 | Required quality check PASS satisfies quality prerequisite | unit test |
| A44 | Change-surface ALLOW/HUMAN_REVIEW/BLOCK semantics enforced | parametrized tests |
| A45 | Risk ALLOW/HUMAN_REVIEW/BLOCK semantics enforced | parametrized tests |
| A46 | Unauthorized toolchain change always RED | unit test |
| A47 | Human approval cannot bypass unauthorized toolchain change | unit test |
| A48 | Gate reasons typed and canonically ordered | unit tests |
| A49 | GREEN evaluation has no reasons | unit test |
| A50 | `GateEvaluation` binds gate/baseline/lifecycle revisions | schema tests |
| A51 | Current context rejects duplicate ambiguous projections | schema/unit tests |
| A52 | Human choice selects one exact current gate/revision | unit test |
| A53 | Non-selected viable choice gate becomes RED | unit test |
| A54 | Choice cannot make invalid selected gate executable | unit test |
| A55 | Engine never returns more than one GREEN gate | set-level tests |
| A56 | Multiple provisional GREEN gates become RED with typed reason | unit test |
| A57 | `execute_handover()` internally re-evaluates governance | inspection/unit test |
| A58 | RED/YELLOW selected gate cannot execute | unit tests |
| A59 | GREEN selected gate delegates to Slice 0.3 transition exactly once | unit test |
| A60 | Governed execution returns lifecycle snapshot, PhaseChanged, and evaluation | unit test |
| A61 | Gate evaluation performs no I/O, clock read, UUID generation, randomness, or LLM call | inspection |
| A62 | Same gate set + same context gives identical evaluation tuple | determinism test |
| A63 | Same complete GREEN execution inputs give identical result | determinism test |
| A64 | No agent, persistence, notification, UI, provider, or GitHub integration introduced | inspection |
| A65 | No generic policy DSL/metadata escape hatch introduced | inspection |
| A66 | No new runtime/development dependency introduced | dependency inspection |
| A67 | `HANDOVER_GOVERNANCE.md` completed | review |
| A68 | ADR-0004 completed | review |
| A69 | Slice 0.4 memory completed | review |
| A70 | `CURRENT_BASELINE.md` distinguishes accepted baseline from 0.4 candidate before acceptance | review |
| A71 | All prior Slice 0.1–0.3 quality gates remain green | CI |

---

# 51. Named Regression Tests

At minimum, implementation should include tests equivalent to:

```text
test_ready_does_not_become_authorized_phase
test_gate_light_belongs_to_handover_not_lifecycle
test_authorization_can_exist_while_gate_is_red
test_missing_authorization_is_yellow_after_validity_passes
test_authorization_survives_lifecycle_revision_change
test_authorization_does_not_survive_gate_revision_change
test_authorization_does_not_survive_baseline_change
test_human_approval_is_bound_to_lifecycle_revision
test_current_rejection_is_red
test_hard_stop_overrides_auto_policy
test_hard_stop_cannot_override_red_validity
test_human_choice_selects_one_current_gate
test_human_choice_cannot_select_through_red_prerequisites
test_nonselected_choice_gate_is_red
test_multiple_executable_paths_are_rejected
test_dependency_must_be_accepted_and_current
test_required_evaluation_outcome_routes_gate
test_required_quality_check_must_be_present_and_pass
test_change_surface_human_review_requires_approval
test_change_surface_block_is_red
test_risk_human_review_requires_approval
test_risk_block_is_red
test_unauthorized_toolchain_change_is_red
test_approval_cannot_bypass_unauthorized_toolchain_change
test_gate_reasons_have_canonical_order
test_green_gate_has_no_reasons
test_validate_phase_transition_is_eventless
test_governance_uses_lifecycle_validator_without_transition_matrix_duplication
test_execute_handover_rechecks_gate_context
test_red_or_yellow_gate_cannot_execute
test_green_gate_executes_exactly_one_lifecycle_transition
test_auto_notify_performs_no_notification_side_effect
test_gate_evaluation_is_deterministic
test_governed_execution_is_deterministic
```

---

# 52. Resulting Authority After Acceptance

After eventual Slice 0.4 implementation and acceptance, Relay will know:

```text
what a slice is
where the slice is structurally
whether the slice is stale or blocked
which structural transitions are legal

AND

which outgoing handovers are currently valid
which exact prerequisites are missing
whether permission exists
whether a human must act
whether a hard stop applies
whether a quality/dependency/evaluation requirement blocks progress
whether change-surface/risk review is required
which handover is red, yellow, or green
whether one exact GREEN handover may execute
```

Relay still will not know how to:

```text
persist governance state
reconstruct authorization/decision history after restart
connect to GitHub product APIs
resolve canonical artifacts from repository files
assign agents
run agents
construct handover packets
send notifications
render a board UI
```

Those remain future slices.

---

# 53. Design-State and Authorization Gate

Current design state:

```text
Slice 0.4 Design Revision 1
Artifact state: REVIEW
Design acceptance: PENDING
```

Human Authority has authorized **design definition** by requesting a formal detailed Slice 0.4.

That instruction does not constitute implementation authorization.

Implementation state remains:

```text
NOT AUTHORIZED
```

The Slice 0.3 post-acceptance hard stop remains active throughout design review.

Implementation may begin only after:

```text
1. independent design review of this revision
2. explicit Human Authority design acceptance
3. explicit Human Authority Slice 0.4 implementation authorization
```

A design-acceptance statement may also explicitly grant implementation authorization, but the two decisions must remain semantically distinguishable in the record.

---

# 54. Hard Stop

Until implementation authorization is explicitly granted:

```text
HARD STOP — ACTIVE
```

Do not:

```text
create governance production code
extend IDs for gate/auth/hdec
modify lifecycle public API
create governance tests as implementation
create ADR-0004 as if accepted implementation exists
modify CURRENT_BASELINE to claim Slice 0.4 capability
begin Slice 0.5
```

Design review and design-document correction are permitted under the current design authorization.

---

# 55. Summary

The resulting governance model is:

```text
                    Slice
                      │
                      ▼
                SliceLifecycle
         phase / validity / blockage
                      │
                      │ proposed movement
                      ▼
                HandoverGate
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
     VALIDITY      AUTHORITY      AUTONOMY
        │             │             │
 artifacts        authorization    policy
 evidence         baseline/gate    approval
 dependencies     revision          choice
 evaluation                         hard stop
 quality                            review
 scope/risk/toolchain
        └─────────────┬─────────────┘
                      ▼
              GateEvaluation
            RED / YELLOW / GREEN
                      │
                  if GREEN
                      ▼
              execute_handover
                      │
                      ▼
        Slice 0.3 transition_phase
```

The design deliberately keeps:

```text
authorization ≠ lifecycle state
approval ≠ authorization
hard stop ≠ lifecycle state
traffic light ≠ slice state
gate evaluation ≠ persistence
risk flag ≠ risk engine
quality evidence ≠ quality execution
handover gate ≠ agent assignment
```

The central invariant is:

> **A structurally possible transition is not necessarily permissible, and a permissible transition is not necessarily autonomous.**

Slice 0.4 makes that distinction deterministic.