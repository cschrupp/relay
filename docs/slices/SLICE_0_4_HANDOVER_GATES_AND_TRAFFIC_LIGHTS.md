# Relay Slice 0.4 — Handover Gates, Authorization, Human Decisions, and Traffic Lights

**Slice:** 0.4  
**Phase:** 0 — Protocol and Deterministic Foundation  
**Status:** PROPOSED FOR DESIGN REVIEW  
**Document class:** Lockable record  
**Artifact state:** REVIEW  
**Document revision:** 2  
**Parent:** *Relay — Build Plan and Development Roadmap v0.3*  
**Depends on:** Slice 0.3 — State Machine and Lifecycle Semantics — COMPLETE / ACCEPTED  
**Accepted project baseline:** `e3a8501e0e2a410d04e2e95fd566b01622535016`  
**Design authorization:** Human Authority authorized detailed Slice 0.4 design and Revision 2 correction  
**Implementation authorization:** NOT GRANTED  
**Execution state:** DESIGN ONLY — post-Slice-0.3 hard stop remains active

---

# 1. Objective

Define Relay's deterministic handover-governance layer.

Slice 0.3 answers:

> Is this lifecycle movement structurally possible?

Slice 0.4 answers:

> Is that movement permissible now?

> Are required engineering prerequisites present?

> Does durable permission exist?

> Does a human need to act now?

> Is the handover RED, YELLOW, or GREEN?

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

> Given the same immutable gate set, the same baseline, the same lifecycle snapshot, the same governance-decision basis, and the same explicit current facts, Relay produces the same canonically ordered gate evaluations and the same executable path—or rejects execution with the same governance error category.

No LLM participates in gate evaluation or handover execution.

---

# 2. Foundational Boundary from Slice 0.3

Slice 0.3 remains authoritative for structural lifecycle truth:

```text
SliceLifecycle
    = Phase + Validity + Blockage
```

Slice 0.4 does not redefine that model.

Governance remains separate:

```text
Lifecycle
    answers WHERE THE WORK IS

Handover Gate
    answers WHETHER A MOVEMENT MAY HAPPEN NOW
```

The invariant remains:

> **Lifecycle truth and transition permission are different things.**

`READY` remains a lifecycle phase.

`AUTHORIZED` remains absent from `LifecyclePhase`.

`HARD_STOP` remains absent from `LifecyclePhase`.

Traffic lights belong to handovers, not slices, agents, or lifecycle phases.

---

# 3. S0.4-D01 — Gates Evaluate Validity, Authority, and Autonomy Separately

Every gate evaluates:

```text
VALIDITY
    Are structural and engineering prerequisites satisfied?

AUTHORITY
    Does explicit durable permission exist when required?

AUTONOMY
    May Relay perform the handover without another current human decision?
```

These dimensions do not collapse into one boolean.

Examples:

```text
validity = false
authorization = granted
autonomy = automatic
→ RED
```

```text
validity = true
authorization = missing
autonomy = automatic
→ YELLOW
```

```text
validity = true
authorization = granted
autonomy = HUMAN_APPROVAL
→ YELLOW until a current approval exists
```

```text
validity = true
authorization = granted
autonomy = AUTO
→ GREEN
```

---

# 4. S0.4-D02 — Traffic-Light Semantics

The only traffic-light values are:

```text
GREEN
YELLOW
RED
```

## GREEN

The gate is currently executable through the governance API.

All blocking validity conditions are satisfied, required authorization exists, and no unresolved current human-action requirement remains.

## YELLOW

No non-overridable validity failure prevents the handover, but at least one human-remediable authority/autonomy action remains.

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

Human approval never overrides a RED validity condition.

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
not selected by current human choice
multiple simultaneously executable paths
```

Precedence:

```text
RED > YELLOW > GREEN
```

There is no `UNKNOWN` light in Slice 0.4.

---

# 5. S0.4-D03 — Traffic Lights Belong to Gates

A slice does not become globally GREEN, YELLOW, or RED.

One lifecycle snapshot may expose several outgoing gates with different lights.

No traffic-light field is added to `Slice` or `SliceLifecycle`.

---

# 6. S0.4-D04 — HandoverGate Is Immutable and Revisioned

Slice 0.4 introduces an immutable serialized `HandoverGate`.

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
reference tuples contain no duplicates
required_dependency_slice_ids must not contain slice_id
```

Supersession:

```text
target_phase == SUPERSEDED
    → superseded_by_slice_id required

otherwise
    → superseded_by_slice_id must be None
```

The successor must differ from `slice_id`.

A substantive gate-policy change creates a new gate revision.

---

# 7. S0.4-D05 — Gate Revision Is Part of Authority

`gate_id` identifies the logical gate.

`revision` identifies the exact policy definition.

Authorization or human decisions for:

```text
gate_id = G
revision = 1
```

do not apply to:

```text
gate_id = G
revision = 2
```

without new authority appropriate to that new revision.

Persistence of revision history remains deferred to Slice 0.5.

---

# 8. S0.4-D06 — Exact Baseline Binding

Relay governance binds to an exact `BaselineId`.

`HandoverGate` includes:

```text
baseline_id: BaselineId
```

`HandoverContext` supplies the current:

```text
baseline_id: BaselineId
```

`AuthorizationGrant`, `HumanApprovalDecision`, and `HumanChoiceDecision` also bind to the applicable baseline.

A moving branch name is never authority.

Slice 0.4 performs no Git/database lookup to resolve the baseline.

## Gate-set baseline rules

The public behavior is normative:

```text
mixed gate baseline IDs in one supplied gate set
    → InvalidGateSet
```

If all supplied gates use one baseline but it differs from `context.baseline_id`:

```text
return every gate as:
RED / BASELINE_MISMATCH
```

For that uniform non-current-baseline case:

```text
do not continue ordinary prerequisite evaluation
do not consult authorization
do not consult human decisions
do not derive YELLOW or GREEN
```

This resolves `RLY-S04-DREV1-F001`.

---

# 9. S0.4-D07 — Governance IDs Extend the Existing Mechanism Narrowly

Slice 0.4 adds:

```text
HandoverGateId     gate_<uuid7>
AuthorizationId    auth_<uuid7>
HumanDecisionId    hdec_<uuid7>
```

These extend the existing `new_id()` mechanism.

ID generation occurs outside the gate engine.

No second identifier framework is introduced.

---

# 10. S0.4-D08 — Eventless Lifecycle Validation Query

Governance must consume the authoritative Slice 0.3 transition rules without manufacturing an event.

Slice 0.4 authorizes:

```python
validate_phase_transition(
    current: SliceLifecycle,
    target_phase: LifecyclePhase,
    superseded_by_slice_id: SliceId | None = None,
) -> None
```

Semantics:

```text
pure
no mutation
no event
no ID
no timestamp
no I/O
same structural rules as transition_phase()
```

`transition_phase()` and `validate_phase_transition()` must reuse the same underlying structural validation logic.

The governance engine must not duplicate the Slice 0.3 transition matrix.

---

# 11. S0.4-D09 — Gates Govern Lifecycle Movement, Not Agent Assignment

A Slice 0.4 gate governs one possible lifecycle movement for one slice.

It binds:

```text
slice_id
source_phase
target_phase
```

Role-only handovers, AgentRole, AgentAssignment, prompt construction, and agent execution remain out of scope.

---

# 12. S0.4-D10 — Authorization Is Durable Permission

Slice 0.4 introduces:

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
reason nonblank
```

Authorization binds to:

```text
slice
baseline
gate identity
gate revision
```

Authorization deliberately does not bind to lifecycle revision or governance revision.

It is durable permission.

Therefore an authorization may be granted while another prerequisite is still RED and remain usable when that prerequisite later becomes satisfied, provided baseline and gate revision remain unchanged.

Slice 0.4 models active grants only.

Revocation, expiry, and authorization history remain deferred.

---

# 13. S0.4-D11 — Missing or Stale Authorization Is YELLOW

When:

```text
authorization_required = True
```

and validity otherwise passes:

```text
no matching current grant
→ YELLOW / AUTHORIZATION_REQUIRED
```

If the current projection contains one grant for the same logical gate but baseline or gate revision no longer matches:

```text
→ YELLOW / AUTHORIZATION_STALE
```

Authorization never overrides RED validity.

---

# 14. S0.4-D12 — Human Decisions Are Execution-Time Decisions

Human decisions are distinct from authorization.

They must not silently survive either:

```text
lifecycle state changes
```

or:

```text
non-lifecycle governance-fact changes
```

Slice 0.4 therefore binds human decisions to both:

```text
lifecycle_revision
governance_revision
```

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
    governance_revision,
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
    choice_gate_refs,
    lifecycle_revision,
    governance_revision,
    actor,
    occurred_at,
    reason,
)
```

where:

```text
actor.kind = HUMAN
```

Decision timestamps are explicit, timezone-aware, and UTC-normalized.

Human decisions do not mutate lifecycle state.

This resolves the core of `RLY-S04-DREV1-F003`.

---

# 15. S0.4-D13 — governance_revision Defines the Human-Decision Basis

`HandoverContext` includes:

```text
governance_revision: int
```

with:

```text
governance_revision >= 0
```

It is a caller-maintained monotonic revision of the current non-human-decision facts relevant to gate evaluation for the supplied lifecycle snapshot.

It is not a database revision and does not introduce persistence.

The caller must advance `governance_revision` whenever a gate-relevant fact capable of changing evaluation changes without a lifecycle revision change.

At minimum this includes changes to:

```text
available artifact IDs
available evidence IDs
dependency lifecycle projection
evaluation outcome
authorization projection
quality-check results
change-surface status
risk status
toolchain-change status
```

A lifecycle revision change already invalidates old human decisions independently.

Adding, replacing, or removing a human decision does not itself advance `governance_revision`; otherwise a new decision would immediately stale itself.

A human decision is current only when its:

```text
baseline binding
gate binding where applicable
lifecycle_revision
governance_revision
```

all match the current evaluation basis.

If only an older otherwise-relevant decision is supplied, the gate may report `HUMAN_DECISION_STALE` together with the current human-action requirement.

The governance engine does not increment `governance_revision`; it validates and consumes it.

---

# 16. S0.4-D14 — HandoverContext Is Current Explicit Data

`HandoverContext` is a current-facts projection, not history.

Conceptually:

```python
HandoverContext(
    schema_version,
    baseline_id,
    governance_revision,
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

All public models follow existing Relay discipline:

```text
immutable
schema_version = 1
extra fields forbidden
JSON-compatible serialization
JSON round trip
JSON Schema generation
```

Set-like/current-projection fields have deterministic uniqueness rules:

```text
artifact IDs unique
evidence IDs unique
dependency lifecycles unique by slice_id
quality checks unique by key
authorization IDs unique
human decision IDs unique
```

Additional projection unambiguity:

```text
at most one AuthorizationGrant per logical gate_id in the current context
at most one HumanApprovalDecision per logical gate_id in the current context
at most one HumanChoiceDecision for the current outgoing handover set
```

A caller needing historical grant/decision chronology must use the future persistence/event layer.

The gate engine performs no external lookup.

---

# 17. S0.4-D15 — Handover Policies

The autonomy policy enum is:

```text
AUTO
AUTO_NOTIFY
HUMAN_APPROVAL
HUMAN_CHOICE
```

## AUTO

No policy-level human decision is required.

If validity and authority pass, the gate may be GREEN.

## AUTO_NOTIFY

Same light semantics as AUTO.

Notification side effects remain out of scope.

## HUMAN_APPROVAL

A current matching `HumanApprovalDecision(APPROVE)` is required.

Without it:

```text
YELLOW / HUMAN_APPROVAL_REQUIRED
```

A current matching REJECT is RED.

## HUMAN_CHOICE

A current matching `HumanChoiceDecision` must select the gate as part of the exact current HUMAN_CHOICE alternative set.

Without a current choice:

```text
YELLOW / HUMAN_CHOICE_REQUIRED
```

HUMAN_CHOICE is evaluated over the outgoing gate set, not gate-locally.

---

# 18. S0.4-D16 — Hard Stop Is Gate Policy

`HandoverGate` contains:

```text
hard_stop: bool
```

When true, the gate cannot become GREEN without a current positive human decision directly naming/selecting the gate.

Positive decisions are:

```text
HumanApprovalDecision(APPROVE)
```

or, for HUMAN_CHOICE:

```text
HumanChoiceDecision selecting the gate
```

Without one:

```text
YELLOW / HARD_STOP_REQUIRES_HUMAN
```

Hard stop dominates AUTO and AUTO_NOTIFY.

Human action never overrides RED validity.

---

# 19. S0.4-D17 — Evaluation Outcome Is a Typed Routing Input

Minimal routing vocabulary:

```text
ACCEPT
REWORK
ESCALATE_CONTRACT
ESCALATE_ARCHITECTURE
BLOCKED
EXPERIMENT_REQUIRED
```

A gate may declare:

```text
required_evaluation_outcomes: tuple[EvaluationOutcome, ...]
```

Rules:

```text
empty tuple
→ no evaluation outcome required

non-empty + no current outcome
→ RED / EVALUATION_REQUIRED

current outcome not allowed
→ RED / EVALUATION_OUTCOME_NOT_ALLOWED
```

The full persisted Evaluation model is deferred.

---

# 20. S0.4-D18 — Exact Artifact and Evidence Prerequisites

A gate may require exact existing IDs:

```text
required_artifact_ids
required_evidence_ids
```

The context supplies exact currently available IDs.

Each missing required artifact produces one:

```text
MISSING_REQUIRED_ARTIFACT / subject=<artifact_id>
```

Each missing required evidence item produces one:

```text
MISSING_REQUIRED_EVIDENCE / subject=<evidence_id>
```

No file-name, path, canonical-key, or recency inference occurs.

Canonical artifact discovery remains deferred to Slice 0.6.

---

# 21. S0.4-D19 — Dependency Readiness Means ACCEPTED + CURRENT

A required dependency passes only when its supplied `SliceLifecycle` is:

```text
phase = ACCEPTED
validity = CURRENT
```

Per dependency:

```text
absent
→ DEPENDENCY_MISSING / subject=<slice_id>

phase != ACCEPTED
→ DEPENDENCY_NOT_ACCEPTED / subject=<slice_id>

ACCEPTED + STALE
→ DEPENDENCY_STALE / subject=<slice_id>
```

`SUPERSEDED` does not satisfy an ACCEPTED dependency requirement.

---

# 22. S0.4-D20 — Required Quality Checks Are Explicit Facts

```text
QualityCheckStatus
    PASS
    FAIL
```

```python
QualityCheckResult(
    key,
    status,
)
```

Required quality keys are explicit stable slugs.

For each required key:

```text
absent
→ QUALITY_CHECK_MISSING / subject=<key>

FAIL
→ QUALITY_CHECK_FAILED / subject=<key>

PASS
→ satisfied
```

Slice 0.4 consumes results; it does not execute quality tools.

---

# 23. S0.4-D21 — Change-Surface Policy

Current fact:

```text
WITHIN_DECLARED
MATERIAL_DEVIATION
```

Gate policy:

```text
ALLOW
HUMAN_REVIEW
BLOCK
```

When status is MATERIAL_DEVIATION:

```text
ALLOW
→ no effect

HUMAN_REVIEW
→ YELLOW / CHANGE_SURFACE_REVIEW_REQUIRED
  until a current APPROVE exists

BLOCK
→ RED / CHANGE_SURFACE_BLOCKED
```

A current rejection remains RED.

---

# 24. S0.4-D22 — Risk Policy Consumes a Flag

Current fact:

```text
RiskStatus
    CLEAR
    FLAGGED
```

Gate policy:

```text
ALLOW
HUMAN_REVIEW
BLOCK
```

When FLAGGED:

```text
ALLOW
→ no effect

HUMAN_REVIEW
→ YELLOW / RISK_REVIEW_REQUIRED
  until a current APPROVE exists

BLOCK
→ RED / RISK_BLOCKED
```

Risk calculation remains outside this slice.

---

# 25. S0.4-D23 — Unauthorized Toolchain Change Is Always RED

Current fact:

```text
NONE
AUTHORIZED
UNAUTHORIZED
```

Semantics:

```text
NONE or AUTHORIZED
→ no effect

UNAUTHORIZED
→ RED / UNAUTHORIZED_TOOLCHAIN_CHANGE
```

Human approval cannot bypass it.

---

# 26. S0.4-D24 — Current Authorization Projection Must Be Unambiguous

The context may carry grants for several gates, but at most one grant for a logical `gate_id` may appear in the current projection.

A grant matches a gate only when all are equal:

```text
slice_id
baseline_id
gate_id
gate_revision
```

A grant with the same logical gate ID but wrong baseline/revision is stale evidence and may produce:

```text
AUTHORIZATION_STALE / subject=<authorization_id>
```

The engine never chooses grants by timestamp.

---

# 27. S0.4-D25 — GateRevisionRef and Exact HUMAN_CHOICE Set Binding

Revision 2 introduces one small inspectable value:

```python
GateRevisionRef(
    gate_id,
    gate_revision,
)
```

It is immutable/versioned under normal Relay model discipline and exists only to identify exact gate definitions compactly.

For one evaluation call, the current HUMAN_CHOICE alternative set is:

```text
all supplied gates whose policy == HUMAN_CHOICE
```

represented as a canonical tuple of `GateRevisionRef` sorted ascending by `gate_id`.

`HumanChoiceDecision.choice_gate_refs` must:

```text
be non-empty
contain no duplicate gate_id
be stored in canonical ascending gate_id order
contain selected_gate_id + selected_gate_revision
```

A choice is current only when its `choice_gate_refs` exactly equal the current canonical HUMAN_CHOICE alternative set and its baseline/lifecycle/governance revisions match.

Adding, removing, or revising a HUMAN_CHOICE alternative invalidates the old choice.

The engine does not hash the choice set; the explicit tuple is the authority record.

This resolves `RLY-S04-DREV1-F004`.

---

# 28. S0.4-D26 — GateEvaluation Is a Deterministic Derived Result

Each gate evaluation returns:

```python
GateEvaluation(
    schema_version,
    gate_id,
    gate_revision,
    slice_id,
    baseline_id,
    lifecycle_revision,
    governance_revision,
    target_phase,
    light,
    reasons,
)
```

`baseline_id` is the current `context.baseline_id` used for that evaluation.

`GateEvaluation` contains no generated ID or timestamp.

GREEN requires:

```text
reasons = ()
```

YELLOW/RED require one or more typed reasons.

Evaluation is bound to the exact lifecycle and governance decision basis that produced it.

---

# 29. S0.4-D27 — Gate Reason Codes, Kinds, and Canonical Order Are Normative

`GateReasonKind`:

```text
BLOCKING
HUMAN_ACTION
```

`GateReasonCode` declaration order is the canonical primary reason order:

```text
01 BASELINE_MISMATCH                  BLOCKING
02 SOURCE_PHASE_MISMATCH              BLOCKING
03 INVALID_LIFECYCLE_TRANSITION       BLOCKING
04 MISSING_REQUIRED_ARTIFACT          BLOCKING
05 MISSING_REQUIRED_EVIDENCE          BLOCKING
06 DEPENDENCY_MISSING                 BLOCKING
07 DEPENDENCY_NOT_ACCEPTED            BLOCKING
08 DEPENDENCY_STALE                   BLOCKING
09 EVALUATION_REQUIRED                BLOCKING
10 EVALUATION_OUTCOME_NOT_ALLOWED     BLOCKING
11 QUALITY_CHECK_MISSING              BLOCKING
12 QUALITY_CHECK_FAILED               BLOCKING
13 CHANGE_SURFACE_BLOCKED             BLOCKING
14 CHANGE_SURFACE_REVIEW_REQUIRED     HUMAN_ACTION
15 RISK_BLOCKED                       BLOCKING
16 RISK_REVIEW_REQUIRED               HUMAN_ACTION
17 UNAUTHORIZED_TOOLCHAIN_CHANGE      BLOCKING
18 AUTHORIZATION_REQUIRED             HUMAN_ACTION
19 AUTHORIZATION_STALE                HUMAN_ACTION
20 HUMAN_APPROVAL_REQUIRED            HUMAN_ACTION
21 HUMAN_CHOICE_REQUIRED              HUMAN_ACTION
22 HUMAN_DECISION_STALE               HUMAN_ACTION
23 HARD_STOP_REQUIRES_HUMAN           HUMAN_ACTION
24 HUMAN_REJECTED                     BLOCKING
25 NOT_SELECTED_BY_HUMAN              BLOCKING
26 MULTIPLE_EXECUTABLE_PATHS          BLOCKING
```

The code→kind mapping is fixed.

Within the same code, reasons are ordered lexicographically by `subject`, with `None` before non-`None` only for codes where both are legally possible; Revision 2 avoids mixed subject cardinality for one code whenever possible.

This resolves part of `RLY-S04-DREV1-F005`.

---

# 30. S0.4-D28 — GateReason Subject and Cardinality Are Normative

Conceptually:

```python
GateReason(
    kind,
    code,
    subject,
)
```

`subject` is one scalar string or `None`. There is no metadata dictionary.

Subject rules:

| Code | Subject |
|---|---|
| BASELINE_MISMATCH | `None` |
| SOURCE_PHASE_MISMATCH | `None` |
| INVALID_LIFECYCLE_TRANSITION | `None` |
| MISSING_REQUIRED_ARTIFACT | required `ArtifactId` |
| MISSING_REQUIRED_EVIDENCE | required `EvidenceId` |
| DEPENDENCY_MISSING | required `SliceId` |
| DEPENDENCY_NOT_ACCEPTED | required `SliceId` |
| DEPENDENCY_STALE | required `SliceId` |
| EVALUATION_REQUIRED | `None` |
| EVALUATION_OUTCOME_NOT_ALLOWED | `None` |
| QUALITY_CHECK_MISSING | required quality-check key |
| QUALITY_CHECK_FAILED | required quality-check key |
| CHANGE_SURFACE_BLOCKED | `None` |
| CHANGE_SURFACE_REVIEW_REQUIRED | `None` |
| RISK_BLOCKED | `None` |
| RISK_REVIEW_REQUIRED | `None` |
| UNAUTHORIZED_TOOLCHAIN_CHANGE | `None` |
| AUTHORIZATION_REQUIRED | `None` |
| AUTHORIZATION_STALE | required `AuthorizationId` |
| HUMAN_APPROVAL_REQUIRED | `None` |
| HUMAN_CHOICE_REQUIRED | `None` |
| HUMAN_DECISION_STALE | required `HumanDecisionId` |
| HARD_STOP_REQUIRES_HUMAN | `None` |
| HUMAN_REJECTED | required `HumanDecisionId` |
| NOT_SELECTED_BY_HUMAN | required selected `HandoverGateId` |
| MULTIPLE_EXECUTABLE_PATHS | required conflicting `HandoverGateId` |

Cardinality rules:

```text
one missing/failing subject
→ one reason
```

Therefore three missing artifacts produce three reasons, one per artifact.

For `MULTIPLE_EXECUTABLE_PATHS`, each provisional GREEN gate receives one reason for every other provisional GREEN gate, subject to that other gate's ID.

For `NOT_SELECTED_BY_HUMAN`, each otherwise viable non-selected HUMAN_CHOICE gate receives one reason whose subject is the currently selected gate ID.

These rules complete `RLY-S04-DREV1-F005`.

---

# 31. S0.4-D29 — Human Decisions Cannot Override Blocking Reasons

Current approval may satisfy only human-remediable requirements:

```text
HUMAN_APPROVAL_REQUIRED
HARD_STOP_REQUIRES_HUMAN
CHANGE_SURFACE_REVIEW_REQUIRED
RISK_REVIEW_REQUIRED
```

Current choice may satisfy:

```text
HUMAN_CHOICE_REQUIRED
```

Neither can remove blocking conditions such as:

```text
baseline mismatch
structural transition failure
missing artifact/evidence
dependency failure
evaluation mismatch
quality failure
BLOCK policy result
unauthorized toolchain change
```

---

# 32. S0.4-D30 — Current Human Rejection Is Blocking

A current matching:

```text
HumanApprovalDecision(REJECT)
```

produces:

```text
RED / HUMAN_REJECTED / subject=<decision_id>
```

A rejection whose lifecycle or governance revision is stale does not block the current basis.

---

# 33. S0.4-D31 — Authorization Staleness and Human-Decision Staleness Differ

Authorization is durable and becomes stale only when its relevant durable binding no longer matches:

```text
baseline_id
gate_id
gate_revision
```

Human decisions are execution-time authority and become stale when any applicable decision-basis binding changes:

```text
baseline
gate revision where applicable
lifecycle revision
governance revision
choice set for HumanChoiceDecision
```

If a stale otherwise-relevant human decision is supplied while current human action is required, emit:

```text
HUMAN_DECISION_STALE / subject=<decision_id>
```

plus the current applicable human-action reason.

---

# 34. S0.4-D32 — HUMAN_CHOICE Is Set-Level

Public evaluation operates on the full outgoing gate set:

```python
evaluate_handover_gates(
    gates: tuple[HandoverGate, ...],
    context: HandoverContext,
) -> tuple[GateEvaluation, ...]
```

A current HumanChoiceDecision must match:

```text
baseline_id
lifecycle_revision
governance_revision
exact canonical HUMAN_CHOICE GateRevisionRef set
selected gate identity/revision
```

If current and the selected gate is otherwise valid, it satisfies `HUMAN_CHOICE_REQUIRED` for the selected gate.

An otherwise viable non-selected HUMAN_CHOICE gate becomes:

```text
RED / NOT_SELECTED_BY_HUMAN / subject=<selected_gate_id>
```

A selected gate that is independently RED remains RED.

A stale or mismatched choice satisfies nothing.

---

# 35. S0.4-D33 — Relay Never Arbitrarily Chooses Among Executable Paths

After gate-local evaluation and HUMAN_CHOICE processing, Relay checks the set-level result.

The engine must never return more than one GREEN gate.

If two or more gates would otherwise be GREEN, every provisional GREEN gate becomes RED and receives one:

```text
MULTIPLE_EXECUTABLE_PATHS / subject=<other_green_gate_id>
```

for each other provisional GREEN gate.

Relay must not choose using:

```text
input order
canonical sort order
recency
randomness
LLM judgment
```

Canonical ordering is presentation/determinism only, never arbitration.

---

# 36. S0.4-D34 — Gate-Set Structural Validation and Baseline Handling

Before gate-local evaluation, validate the supplied gate set.

Raise `InvalidGateSet` for:

```text
empty gate set
duplicate gate_id
mixed slice_id
mixed baseline_id
gate slice_id different from context.lifecycle.slice_id
```

Do not raise `InvalidGateSet` merely because a uniform gate-set baseline differs from `context.baseline_id`.

That case deterministically returns all gates RED with only:

```text
BASELINE_MISMATCH
```

before ordinary gate evaluation.

---

# 37. S0.4-D35 — Gate Evaluation Algorithm

For each `evaluate_handover_gates()` call:

## Step 1 — Validate set structure

Apply Section 36.

## Step 2 — Handle uniform non-current baseline

If the uniform gate baseline differs from `context.baseline_id`:

```text
build RED / BASELINE_MISMATCH evaluation for every gate
skip Steps 3–10
return in canonical gate_id order
```

## Step 3 — Evaluate structural lifecycle validity

Per gate:

```text
source_phase must match current lifecycle phase
validate_phase_transition() must pass
```

Failures:

```text
SOURCE_PHASE_MISMATCH
INVALID_LIFECYCLE_TRANSITION
```

## Step 4 — Evaluate engineering prerequisites

Per gate:

```text
required artifacts
required evidence
required dependencies
required evaluation outcome
required quality checks
change-surface BLOCK
risk BLOCK
unauthorized toolchain change
```

Emit one subject-specific reason per failed subject where Section 30 requires it.

## Step 5 — Evaluate current rejection

A current matching REJECT is blocking.

## Step 6 — Evaluate authorization

If required:

```text
matching grant present
→ satisfied

none present
→ AUTHORIZATION_REQUIRED

one logical-gate grant present but stale by baseline/revision
→ AUTHORIZATION_STALE / authorization_id
```

## Step 7 — Evaluate approval-type human requirements

Check:

```text
change-surface HUMAN_REVIEW
risk HUMAN_REVIEW
hard stop
HUMAN_APPROVAL policy
```

One exact current APPROVE decision may satisfy all approval-type requirements for that one gate and exact current decision basis.

An old lifecycle/governance-basis decision satisfies none.

## Step 8 — Evaluate HUMAN_CHOICE across the gate set

Construct canonical HUMAN_CHOICE `GateRevisionRef` set and apply Section 34.

## Step 9 — Derive provisional light

```text
any BLOCKING reason
→ RED

else any HUMAN_ACTION reason
→ YELLOW

else
→ GREEN
```

## Step 10 — Enforce unique executable path

If more than one provisional GREEN exists, apply `MULTIPLE_EXECUTABLE_PATHS` as specified in Section 35.

## Step 11 — Canonicalize reasons

Order by:

```text
GateReasonCode declaration order
then subject lexicographically
```

## Step 12 — Canonicalize evaluations

Return evaluations sorted ascending by:

```text
gate_id
```

Input gate tuple order has no semantic meaning.

Therefore any permutation of the same exact gate set with the same context yields the identical GateEvaluation tuple.

This resolves `RLY-S04-DREV1-F002`.

---

# 38. S0.4-D36 — Governed Execution Re-Evaluates Governance

Slice 0.4 introduces conceptually:

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

Execution:

1. re-run `evaluate_handover_gates(gates, context)`;
2. locate selected gate by ID;
3. require it GREEN;
4. enforce authority temporal causality from Section 39;
5. call Slice 0.3 `transition_phase()` exactly once;
6. return new lifecycle, `PhaseChanged`, and the exact evaluation used.

A caller-constructed GREEN evaluation is never sufficient authority.

If selected gate is absent, RED, or YELLOW:

```text
raise HandoverNotExecutable
produce no lifecycle event
```

---

# 39. S0.4-D37 — Governed Execution Preserves Authority Causality

Authority records have explicit timestamps and the lifecycle event has explicit `occurred_at`.

Execution must not create an event that historically predates the authority used to permit it.

For every matching authorization required and used by the GREEN gate:

```text
execution occurred_at >= AuthorizationGrant.granted_at
```

For every current human approval/choice required and used by the GREEN gate:

```text
execution occurred_at >= HumanDecision.occurred_at
```

If either rule fails:

```text
raise HandoverNotExecutable
produce no lifecycle event
```

No new governance exception type is required.

Slice 0.3 continues to enforce lifecycle timestamp monotonicity against `current.updated_at`.

Gate evaluation itself remains a timeless deterministic current-projection operation; the causality check is required when creating the governed lifecycle event.

This resolves `RLY-S04-DREV1-F006`.

---

# 40. S0.4-D38 — GateEvaluation Is Evidence, Not Persistence

A GateEvaluation is immutable deterministic evidence of one evaluation basis.

Slice 0.4 does not persist it.

`execute_handover()` returns the evaluation used so a future persistence layer can preserve decision context.

Slice 0.5 decides how gate evaluations, authorizations, human decisions, and executions become durable records.

No database/event-store abstraction is introduced here.

---

# 41. S0.4-D39 — AUTO_NOTIFY Has No Side Effect

AUTO_NOTIFY and AUTO have the same light calculation.

Slice 0.4 sends no notification and introduces no notification abstraction.

---

# 42. S0.4-D40 — Gate Evaluation Is Pure and Provider-Neutral

The gate engine performs no:

```text
clock reads
UUID generation
randomness
filesystem access
Git/GitHub access
database access
HTTP/network access
LLM/model calls
notification calls
CI execution
quality-tool execution
artifact discovery
```

All facts are explicit immutable inputs.

Determinism invariant:

```text
same exact gate set
regardless of input permutation
+
same HandoverContext
=
same canonically ordered GateEvaluation tuple
```

Governed execution is deterministic over all complete explicit inputs subject to accepted Slice 0.3 semantics.

---

# 43. S0.4-D41 — Handover Packets Are Deferred

Slice 0.4 does not implement:

```text
HandoverPacket
context assembly
role prompt construction
repository file selection
conversation transfer
```

Gate evaluation answers whether movement is permissible; later agent-execution work constructs receiving context.

---

# 44. S0.4-D42 — Authorization Is Not Identity/RBAC

Slice 0.4 does not implement:

```text
user accounts
organizations
RBAC
OAuth
ACLs
policy administration
cryptographic signatures
```

Phase-0 AuthorizationGrant requires a HUMAN actor.

The application layer remains responsible for ensuring the supplied actor legitimately represents Human Authority.

---

# 45. S0.4-D43 — Governance Models Remain Separate from Slice Definition

Do not add governance fields to the accepted Slice model.

Boundaries:

```text
Slice
    intended bounded work

SliceLifecycle
    structural work state

HandoverGate
    policy for one possible movement

HandoverContext
    current explicit facts and decision basis

AuthorizationGrant
    durable permission

HumanApprovalDecision
    execution-time gate approval/rejection

HumanChoiceDecision
    execution-time set-level choice

GateEvaluation
    deterministic derived decision
```

---

# 46. Public Governance Types

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

GateRevisionRef
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

A materially different public vocabulary requires design review.

---

# 47. Public Governance Operations

Required public operations:

```python
evaluate_handover_gates(...)
execute_handover(...)
```

plus the narrow lifecycle query:

```python
validate_phase_transition(...)
```

No public repository/service/provider abstraction is required.

---

# 48. Governance Error Family

Public errors:

```text
GovernanceError
├── InvalidGateSet
├── InvalidHandoverContext
└── HandoverNotExecutable
```

Semantics:

- `InvalidGateSet`: supplied gate set is structurally inconsistent.
- `InvalidHandoverContext`: validly shaped context contains mutually ambiguous current-projection facts that cannot be interpreted deterministically.
- `HandoverNotExecutable`: selected gate is absent/RED/YELLOW, or governed execution violates required authority temporal causality.

Ordinary missing prerequisites are evaluation results, not exceptions.

Pydantic/schema validation owns malformed individual values.

Lifecycle structural errors remain owned by Slice 0.3.

---

# 49. Required Gate Scenarios

Implementation must cover at least:

## Automatic valid path

```text
READY / CURRENT / CLEAR
prerequisites present
authorization present
AUTO
→ GREEN
```

## Authorization granted while validity is RED

```text
authorization present
required artifact missing
→ RED

artifact later present
same baseline + gate revision
→ durable authorization still matches
```

Any prior human approval must be revalidated through current lifecycle/governance revision rules.

## Missing authorization

```text
otherwise valid + authorization required + absent
→ YELLOW / AUTHORIZATION_REQUIRED
```

## Stale authorization

```text
same logical gate ID
old baseline or gate revision grant
→ YELLOW / AUTHORIZATION_STALE
```

## Human approval

```text
valid + authorized + no current approval
→ YELLOW

current APPROVE
→ GREEN unless set-level conflict

current REJECT
→ RED
```

## Governance-basis change after approval

```text
approval at governance_revision N
non-human gate fact changes
governance_revision N+1
→ old approval stale
```

## Hard stop

```text
AUTO + hard_stop + no current approval
→ YELLOW

current approval
→ may become GREEN
```

## HUMAN_CHOICE

```text
G1 and G2 HUMAN_CHOICE
choice_gate_refs = [G1@r, G2@r]
select G1
→ G1 may become GREEN
→ otherwise viable G2 RED / NOT_SELECTED_BY_HUMAN
```

## Choice-set change

```text
old choice set [G1, G2]
current set [G1, G3]
→ old choice stale
```

## Invalid selected path

Human choice selects a gate that is independently RED:

```text
→ remains RED
```

## Multiple executable paths

Two provisional GREEN gates:

```text
→ both RED / MULTIPLE_EXECUTABLE_PATHS
```

## Baseline set rules

```text
mixed gate baselines
→ InvalidGateSet
```

```text
uniform non-current gate baseline
→ all RED / BASELINE_MISMATCH
```

## Canonical output

Permuting input gates:

```text
→ identical GateEvaluation tuple ordered by gate_id
```

## Dependency

```text
ACCEPTED + CURRENT
→ satisfies

ACCEPTED + STALE
→ RED / DEPENDENCY_STALE
```

## Evaluation routing

ACCEPT, REWORK, ESCALATE_CONTRACT, and ESCALATE_ARCHITECTURE each enable only appropriately configured gates.

## Quality evidence

```text
missing → RED per key
FAIL    → RED per key
PASS    → satisfied
```

## Change-surface and risk review

ALLOW/HUMAN_REVIEW/BLOCK semantics must be covered.

## Unauthorized toolchain change

```text
UNAUTHORIZED
→ RED regardless of approval
```

## Reason cardinality

Several missing artifacts/checks/dependencies produce one typed reason per failed subject in canonical order.

## Temporal authority

```text
execution time < required grant time
→ HandoverNotExecutable

execution time < required human-decision time
→ HandoverNotExecutable
```

## Governed execution

```text
GREEN selected gate
→ exactly one Slice 0.3 PhaseChanged event
```

```text
RED/YELLOW selected gate
→ HandoverNotExecutable
→ no lifecycle event
```

---

# 50. Explicit In Scope

After separate implementation authorization, Slice 0.4 permits implementation of:

1. `gate_`, `auth_`, `hdec_` IDs;
2. traffic-light and policy enums;
3. minimal evaluation/quality/scope/risk/toolchain fact enums;
4. `GateRevisionRef`;
5. immutable revisioned `HandoverGate`;
6. exact baseline binding;
7. `AuthorizationGrant`;
8. lifecycle/governance-revision-bound human approval;
9. lifecycle/governance/choice-set-bound human choice;
10. `HandoverContext` and `governance_revision`;
11. exact artifact/evidence prerequisite checks;
12. dependency ACCEPTED+CURRENT checks;
13. evaluation-outcome checks;
14. quality checks;
15. change-surface review policy;
16. risk review policy;
17. unauthorized toolchain blocking;
18. hard-stop enforcement;
19. set-level HUMAN_CHOICE;
20. typed reason code/kind/subject/cardinality contract;
21. deterministic canonical reason ordering;
22. canonical gate-evaluation ordering;
23. no-more-than-one-GREEN invariant;
24. `GateEvaluation`;
25. `evaluate_handover_gates()`;
26. `execute_handover()`;
27. authority temporal-causality validation;
28. eventless `validate_phase_transition()`;
29. governance tests and schema tests;
30. governance architecture document;
31. ADR-0004;
32. Slice 0.4 memory;
33. candidate CURRENT_BASELINE update during implementation only.

---

# 51. Explicit Out of Scope

Forbidden unless separately authorized:

```text
agent execution
AgentRole / AgentAssignment
handover packet assembly
prompt/context assembly
notifications
UI / board
REST/API
database
persistence repositories
event store
transactions
schema migrations
Git/GitHub integration
artifact registry
canonical document discovery
file/path artifact discovery
RBAC / identity / organizations
authorization expiry/revocation history
risk scoring
quality-command execution
CI provider integration
change-surface computation
evaluator agent execution
full Evaluation aggregate
research execution
experiments
provider/model integration
background queues
webhooks
generic rules/policy DSL
```

Do not create placeholders for future concepts.

---

# 52. Expected Implementation Change Surface

Expected existing production files touched:

```text
src/relay_engine/domain/ids.py
src/relay_engine/domain/__init__.py
src/relay_engine/lifecycle/engine.py
src/relay_engine/lifecycle/__init__.py
```

Lifecycle modification is limited to exposing the eventless structural validation query without changing accepted transition semantics.

Expected new package:

```text
src/relay_engine/governance/
    __init__.py
    models.py
    engine.py
    errors.py
```

Expected tests:

```text
tests/unit/test_governance.py
```

Existing domain/lifecycle tests may be changed narrowly for IDs and the validation query.

Expected dependencies:

```text
runtime: 0 new
development: 0 new
```

Forbidden architectural expansion:

```text
rules DSL
generic policy language
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

# 53. Required Documentation During Implementation

Implementation should create:

```text
docs/architecture/HANDOVER_GOVERNANCE.md
docs/decisions/ADR-0004-handover-governance-separation.md
docs/slices/SLICE_0_4_HANDOVER_GATES_MEMORY.md
```

ADR-0004 must record at minimum:

1. validity/authority/autonomy separation;
2. traffic lights belong to handovers;
3. authorization is durable permission;
4. human decisions are execution-time decisions;
5. human decisions bind lifecycle and governance revision;
6. human choice also binds exact choice set;
7. gates/authorization bind exact baseline and gate revision;
8. hard stop is gate policy;
9. human decisions cannot override RED validity;
10. HUMAN_CHOICE is set-level;
11. Relay never arbitrarily chooses among multiple executable paths;
12. result/reason ordering is canonical and not selection authority;
13. governed execution re-evaluates context and enforces temporal authority causality;
14. gate evaluation is pure/provider-neutral;
15. persistence/notifications/agents remain deferred.

Before human acceptance:

```text
ADR-0004 = PROPOSED / VALIDATED / PENDING ACCEPTANCE
Slice 0.4 memory = IMPLEMENTATION COMPLETE / PENDING EVALUATION
```

Neither is locked before acceptance.

---

# 54. Acceptance Matrix

All criteria are mandatory unless design is explicitly revised.

| ID | Requirement | Evidence |
|---|---|---|
| A01 | Governance remains separate from `Slice` and `SliceLifecycle` | inspection |
| A02 | Traffic-light enum exactly GREEN/YELLOW/RED | schema/unit |
| A03 | Validity, authority, autonomy evaluated distinctly | scenarios |
| A04 | RED dominates YELLOW/GREEN | unit |
| A05 | Human action cannot override RED validity | unit |
| A06 | Traffic lights are per gate | inspection |
| A07 | HandoverGate immutable/versioned/extra-forbid | schema |
| A08 | Gate revision >=1 | schema |
| A09 | Gate source != target | schema |
| A10 | Supersession gate requires distinct successor | schema/unit |
| A11 | Gates bind exact BaselineId | schema/unit |
| A12 | `gate_`, `auth_`, `hdec_` extend existing ID mechanism | ID tests |
| A13 | Gate engine generates no IDs | inspection |
| A14 | Eventless validate_phase_transition exposed | API/unit |
| A15 | Validation query/live transition share structural logic | regression |
| A16 | Governance does not duplicate lifecycle transition table | inspection |
| A17 | Authorization immutable and baseline/gate-revision bound | schema |
| A18 | Authorization requires HUMAN actor in Slice 0.4 | schema |
| A19 | Authorization not bound to lifecycle/governance revision | schema/inspection |
| A20 | Missing required authorization produces YELLOW | unit |
| A21 | Wrong baseline/gate-revision authorization is stale | unit |
| A22 | Human approval binds lifecycle revision | schema/unit |
| A23 | Human choice binds lifecycle revision | schema/unit |
| A24 | Current matching REJECT produces RED | unit |
| A25 | Old lifecycle revision decision cannot authorize current handover | unit |
| A26 | AUTO may become GREEN without policy-level human decision | unit |
| A27 | AUTO_NOTIFY has AUTO light semantics and no side effect | test/inspection |
| A28 | HUMAN_APPROVAL requires current APPROVE | unit |
| A29 | HUMAN_CHOICE evaluated across gate set | scenarios |
| A30 | Hard stop overrides AUTO/AUTO_NOTIFY | unit |
| A31 | Current positive human decision may satisfy hard stop | unit |
| A32 | Hard stop cannot override RED validity | unit |
| A33 | Evaluation outcomes typed/routed deterministically | unit |
| A34 | Missing required evaluation outcome produces RED | unit |
| A35 | Exact artifact prerequisites enforced | unit |
| A36 | Exact evidence prerequisites enforced | unit |
| A37 | Dependency absent produces RED | unit |
| A38 | Dependency not ACCEPTED produces RED | unit |
| A39 | ACCEPTED+STALE dependency produces RED | unit |
| A40 | ACCEPTED+CURRENT dependency satisfies requirement | unit |
| A41 | Required quality check missing produces RED | unit |
| A42 | Required quality check FAIL produces RED | unit |
| A43 | Required quality check PASS satisfies requirement | unit |
| A44 | Change-surface ALLOW/HUMAN_REVIEW/BLOCK semantics | parametrized |
| A45 | Risk ALLOW/HUMAN_REVIEW/BLOCK semantics | parametrized |
| A46 | Unauthorized toolchain change always RED | unit |
| A47 | Approval cannot bypass unauthorized toolchain change | unit |
| A48 | Reasons typed and canonically ordered | unit |
| A49 | GREEN evaluation has no reasons | unit |
| A50 | Evaluation binds gate/baseline/lifecycle/governance revisions | schema |
| A51 | Current context rejects ambiguous duplicate projections | schema/unit |
| A52 | Human choice selects exact current gate/revision | unit |
| A53 | Non-selected viable choice gate becomes RED | unit |
| A54 | Choice cannot make invalid selected gate executable | unit |
| A55 | Engine never returns >1 GREEN | set-level |
| A56 | Multiple provisional GREEN gates become RED with typed conflict reasons | unit |
| A57 | execute_handover re-evaluates governance | inspection/unit |
| A58 | RED/YELLOW selected gate cannot execute | unit |
| A59 | GREEN selected gate delegates to Slice 0.3 exactly once | unit |
| A60 | Governed execution returns lifecycle, PhaseChanged, evaluation | unit |
| A61 | Gate evaluation performs no I/O/clock/UUID/randomness/LLM | inspection |
| A62 | Same exact gate set regardless of input permutation + same context gives identical canonically ordered evaluation tuple | determinism |
| A63 | Same complete GREEN execution inputs give identical result | determinism |
| A64 | No agent/persistence/notification/UI/provider/GitHub integration | inspection |
| A65 | No generic policy DSL/metadata escape hatch | inspection |
| A66 | No new runtime/development dependency | dependency inspection |
| A67 | HANDOVER_GOVERNANCE.md completed | review |
| A68 | ADR-0004 completed | review |
| A69 | Slice 0.4 memory completed | review |
| A70 | CURRENT_BASELINE distinguishes accepted baseline from candidate pre-acceptance | review |
| A71 | Prior quality gates remain green | CI |
| A72 | Mixed gate baseline IDs raise InvalidGateSet | unit |
| A73 | Uniform non-current baseline returns every gate RED/BASELINE_MISMATCH | unit |
| A74 | Evaluation output order canonical by gate_id and independent of input tuple order | unit |
| A75 | Human approval binds current governance decision basis | schema/unit |
| A76 | Human choice binds current governance decision basis | schema/unit |
| A77 | Human choice binds exact canonical HUMAN_CHOICE alternative set | schema/unit |
| A78 | Added/removed/revised HUMAN_CHOICE candidate invalidates prior choice | unit |
| A79 | GateReasonCode→GateReasonKind mapping is fixed | unit/schema |
| A80 | Reason subject requirements and per-subject cardinality are fixed | unit |
| A81 | Reason-code canonical ordering equals declared normative order | unit |
| A82 | Governed execution cannot predate required authorization | unit |
| A83 | Governed execution cannot predate required human decision | unit |

---

# 55. Named Regression Tests

At minimum:

```text
test_ready_does_not_become_authorized_phase
test_gate_light_belongs_to_handover_not_lifecycle
test_authorization_can_exist_while_gate_is_red
test_missing_authorization_is_yellow_after_validity_passes
test_authorization_survives_lifecycle_revision_change
test_authorization_survives_governance_revision_change
test_authorization_does_not_survive_gate_revision_change
test_authorization_does_not_survive_baseline_change
test_human_approval_is_bound_to_lifecycle_revision
test_human_approval_is_bound_to_governance_revision
test_current_rejection_is_red
test_hard_stop_overrides_auto_policy
test_hard_stop_cannot_override_red_validity
test_human_choice_selects_one_current_gate
test_human_choice_cannot_select_through_red_prerequisites
test_nonselected_choice_gate_is_red
test_choice_stales_when_candidate_gate_set_changes
test_multiple_executable_paths_are_rejected
test_dependency_must_be_accepted_and_current
test_required_evaluation_outcome_routes_gate
test_required_quality_check_must_be_present_and_pass
test_change_surface_human_review_requires_current_approval
test_change_surface_block_is_red
test_risk_human_review_requires_current_approval
test_risk_block_is_red
test_unauthorized_toolchain_change_is_red
test_approval_cannot_bypass_unauthorized_toolchain_change
test_gate_reasons_have_canonical_order
test_gate_reason_code_to_kind_mapping_is_locked
test_multiple_missing_artifacts_emit_one_reason_per_artifact
test_multiple_failed_quality_checks_emit_one_reason_per_check
test_green_gate_has_no_reasons
test_validate_phase_transition_is_eventless
test_governance_uses_lifecycle_validator_without_matrix_duplication
test_mixed_gate_baselines_raise_invalid_gate_set
test_uniform_noncurrent_baseline_returns_red_evaluations
test_gate_evaluation_order_is_canonical_across_input_permutations
test_approval_stales_when_governance_fact_revision_changes
test_choice_stales_when_governance_fact_revision_changes
test_execute_handover_rechecks_gate_context
test_execution_cannot_predate_required_authorization
test_execution_cannot_predate_required_human_decision
test_red_or_yellow_gate_cannot_execute
test_green_gate_executes_exactly_one_lifecycle_transition
test_auto_notify_performs_no_notification_side_effect
test_gate_evaluation_is_deterministic
test_governed_execution_is_deterministic
```

---

# 56. Revision-1 Review Findings Resolved in Revision 2

Revision 2 resolves `RLY-S04-DESIGN-EVAL-002`:

| Finding | Resolution |
|---|---|
| `RLY-S04-DREV1-F001` | Mixed gate baselines are InvalidGateSet; a uniform gate baseline different from context returns every gate RED/BASELINE_MISMATCH and short-circuits ordinary evaluation. |
| `RLY-S04-DREV1-F002` | Evaluations are returned in canonical ascending gate_id order; input permutation has no semantic effect and ordering never selects a path. |
| `RLY-S04-DREV1-F003` | `governance_revision` binds execution-time human decisions to non-lifecycle gate-fact changes; authorization remains durable and unbound to it. |
| `RLY-S04-DREV1-F004` | HumanChoiceDecision carries the exact canonical HUMAN_CHOICE `GateRevisionRef` set; added/removed/revised choice alternatives stale the prior choice. |
| `RLY-S04-DREV1-F005` | Reason code→kind mapping, subject rules, per-subject cardinality, conflict cardinality, and canonical code order are normative. |
| `RLY-S04-DREV1-F006` | Governed execution may not predate required authorization or human decisions; violation raises HandoverNotExecutable before lifecycle mutation. |

The foundational Revision-1 architecture is unchanged.

---

# 57. Resulting Authority After Acceptance

After eventual Slice 0.4 implementation and acceptance, Relay will know:

```text
what a slice is
where it is structurally
whether it is stale or blocked
which structural transitions are legal

and

which outgoing handovers are valid
which prerequisites are missing
whether durable permission exists
whether a current human decision is required
whether an existing human decision is stale
whether a hard stop applies
whether quality/dependency/evaluation conditions block progress
whether scope/risk review is required
which handover is RED/YELLOW/GREEN
whether exactly one GREEN handover may execute
```

Relay still will not know how to:

```text
persist governance history
connect to GitHub product APIs
resolve canonical artifacts from repository files
assign/run agents
construct handover packets
send notifications
render a board UI
```

---

# 58. Design State and Hard Stop

Current design state:

```text
Slice 0.4 Design Revision 2
Artifact state: REVIEW
Design acceptance: PENDING
```

Human Authority authorized design correction only.

Implementation remains:

```text
NOT AUTHORIZED
```

The post-Slice-0.3 hard stop remains:

```text
ACTIVE
```

Implementation may begin only after:

```text
1. independent design review of Revision 2
2. explicit Human Authority design acceptance
3. explicit Human Authority Slice 0.4 implementation authorization
```

Design acceptance and implementation authorization may be expressed together only if both decisions are explicit and semantically distinguishable.

Do not begin Slice 0.5.

---

# 59. Summary

The governance model is:

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
 dependencies     revision          choice-set
 evaluation                         hard stop
 quality                            decision basis
 scope/risk/toolchain
        └─────────────┬─────────────┘
                      ▼
              GateEvaluation
            RED / YELLOW / GREEN
                      │
              at most one GREEN
                      │
                  if selected
                      ▼
              execute_handover
                      │
          temporal authority check
                      │
                      ▼
        Slice 0.3 transition_phase
```

The design deliberately preserves:

```text
authorization ≠ lifecycle state
approval ≠ authorization
hard stop ≠ lifecycle state
traffic light ≠ slice state
gate evaluation ≠ persistence
risk flag ≠ risk engine
quality evidence ≠ quality execution
handover gate ≠ agent assignment
canonical ordering ≠ path selection
```

The central invariant is:

> **A structurally possible transition is not necessarily permissible, and a permissible transition is not necessarily autonomous.**

Revision 2 additionally guarantees that execution-time human authority applies only to the exact current decision basis and, for human choice, the exact choice set the human was presented.