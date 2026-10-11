# Relay — Slice 1.9 Human Decision Support and Governance Review Surface — Implementation Handoff

**Document class:** Immutable implementation handoff  
**Status:** IMMUTABLE / AUTHORIZED FOR CODEX IMPLEMENTATION  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9  
**Record:** RLY-S19-IMPL-HANDOFF-001  
**Authority:** RLY-S19-IMPL-AUTH-001 — AUTHORIZED  
**Implementation role:** Codex / IMPLEMENTATION_AGENT  
**Independent evaluator:** GPT-5.6 Sol

## 1. Exact identity

~~~text
Repository:
cschrupp/relay

Implementation branch:
implementation/1.9-human-decision-support-governance-review-surface

Exact authorized starting baseline:
a3b489bb4682314a706f66c57ee0bc1bb917542c

Canonical main at authorization:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

Exact accepted combined-design subject:
03d6efecf9ad4aaec0c5967b9486650399d0a492

Independent design evaluation:
RLY-S19-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S19-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authority:
RLY-S19-IMPL-AUTH-001 — AUTHORIZED

Authority record commit:
feb74b4ed9460226dfd2b43035ddf9a9e16c39e2

Acceptance-baseline CI:
38151970093 — SUCCESS
~~~

The implementation branch was created at the exact authorized baseline before the implementation authority record was appended to the design-governance branch.

## 2. Bootstrap — hard preflight

Codex must begin with:

~~~bash
git fetch origin
git checkout implementation/1.9-human-decision-support-governance-review-surface
git rev-parse HEAD
git status --short
~~~

The pre-edit HEAD MUST equal:

~~~text
a3b489bb4682314a706f66c57ee0bc1bb917542c
~~~

The worktree MUST be clean.

Then verify:

~~~bash
git merge-base HEAD 7e690f9fe22b34226fff2d3364d1ed94b91dc9f7
git rev-list --left-right --count 7e690f9fe22b34226fff2d3364d1ed94b91dc9f7...HEAD
~~~

Expected merge base:

~~~text
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7
~~~

Do not merge/rebase newer main before implementation.

## 3. Governing design — mandatory reading order

Read:

1. docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE_DESIGN.md
2. docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE_DESIGN_REWORK_1.md
3. docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE_DESIGN_REWORK_2.md
4. docs/reviews/SLICE_1_9_DESIGN_EVALUATION_003.md
5. docs/reviews/SLICE_1_9_DESIGN_ACCEPTANCE.md

Precedence:

~~~text
Rework 2 > Rework 1 > Revision 1
~~~

where later documents explicitly amend earlier ones.

Do not implement from the older roadmap proposal if it conflicts with the accepted combined design.

## 4. Implementation objective

Implement the minimum deterministic Human Decision Support projection and server-rendered review surface.

Target flow:

~~~text
same SQLite read snapshot
    -> existing SliceDetail durable facts
    -> existing HumanActionProjection
    -> existing ManualEvaluationProjection
    -> new DecisionSupportProjection
    -> Decision Cards + deterministic read-only Q&A
    -> existing Human POST forms/services
~~~

No new authority plane is allowed.

## 5. Authorized file surface

Expected NEW production files:

~~~text
src/relay_engine/decision_support/__init__.py
src/relay_engine/decision_support/models.py
src/relay_engine/decision_support/service.py
~~~

Expected MODIFY:

~~~text
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
~~~

Expected NEW tests:

~~~text
tests/unit/test_decision_support_models.py
tests/unit/test_decision_support_service.py
~~~

Expected MODIFY tests:

~~~text
tests/unit/test_board_models.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_web.py
~~~

A narrowly named extra unit-test file is permitted only if it materially improves deterministic coverage.

Small __init__.py exports are permitted if mechanically necessary.

Anything outside this surface requires STOP unless it is an unavoidable formatting/import-only adjustment with no semantic widening.

## 6. Explicit no-change surface

Do NOT modify semantics in:

~~~text
src/relay_engine/governance/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/persistence/**
src/relay_engine/repository_contract/**
src/relay_engine/repository_baseline/**
src/relay_engine/repository_sync/**
~~~

Do NOT modify:

~~~text
pyproject.toml
uv.lock
.github/workflows/**
repository settings
~~~

No migration. No new table. No dependency change.

## 7. Existing primitives — reuse, do not duplicate

Reuse:

~~~text
DomainModel
ContentDigest
SliceId
BaselineId
HandoverGateId
HumanDecisionId
SliceResultId
ManualEvaluationId
GateEvaluationRecordId
GateRevisionRef
HandoverGate
HandoverPolicy
HumanApprovalDecision
HumanChoiceDecision
HumanApprovalValue
HumanActionBasis
HumanActionKind
HumanActionProjection
ManualEvaluationActionKind
ManualEvaluationProjection
ManualEvaluationRecord
RiskStatus
ChangeSurfaceStatus
ReviewPolicy
LifecyclePhase
~~~

Do not invent a second digest type or a new durable pending-decision ID.

Pending decisions are read-model identities only.

## 8. Core Decision Support enums/models

Implement immutable DomainModel-based values for the accepted concepts.

Required semantic enums:

~~~text
DecisionKind
    GATE_AUTHORIZATION
    GATE_APPROVAL
    GATE_PATH_CHOICE
    TECHNICAL_ACCEPTANCE

DecisionCardState
    PENDING_REQUIRED
    RECORDED_REVISABLE

DecisionBasisApplicability
    REQUIRED_PRESENT
    OPTIONAL_PRESENT
    NOT_APPLICABLE
    UNKNOWN
    MISSING_REQUIRED

DecisionBasisFreshness
    CURRENT
    STALE
    UNKNOWN
    NOT_APPLICABLE

DecisionBasisCompleteness
    COMPLETE
    INCOMPLETE
    UNKNOWN
    STALE

DecisionStatementBasis
    CANONICAL_FACT
    EVALUATOR_JUDGMENT
    EXTERNAL_REFERENCE
    MODEL_INFERENCE
    UNKNOWN

DecisionQuestionKind
    WHY_REQUIRED
    WHAT_IS_CURRENT
    WHAT_WOULD_CHANGE
    WHAT_EVIDENCE_EXISTS
    WHAT_DID_THE_EVALUATOR_FIND
    WHAT_BLOCKS_OR_IS_UNKNOWN
    WHAT_IF_APPROVED
    WHAT_IF_REJECTED
    WHAT_IF_DEFERRED
    WHAT_GOVERNANCE_REQUIREMENTS_APPLY
~~~

Revision 1 implementation MUST emit only:

~~~text
CANONICAL_FACT
EVALUATOR_JUDGMENT
UNKNOWN
~~~

No MODEL_INFERENCE. No provider/model call.

Implement the accepted component/source enums and typed read models, including equivalents of:

~~~text
DecisionBasisIdentityV1
PendingDecisionRef
DecisionSourceRef
DecisionBasisComponent
DecisionProposedOutcome
DecisionChoice discriminated union
DecisionCard
DecisionAnswer
DecisionSupportProjection
~~~

Use exact repository type conventions and strict/frozen/extra-forbid validation.

## 9. DecisionBasisIdentityV1 — exact digest subject

The exact v1 identity fields are:

~~~text
schema_version = 1
decision_kind
slice_id
gate_ref
target_phase
human_action_basis
decision_state
expected_current_approval_decision_id
expected_current_choice_decision_id
expected_result_id
expected_manual_evaluation_id
eligible_choice_gate_refs
~~~

Non-applicable fields MUST serialize explicitly as null or [] according to the design.

human_action_basis is the COMPLETE current HumanActionBasis, including all of its current fields:

~~~text
evaluation_record_id
slice_id
baseline_id
lifecycle_revision
governance_revision
gate_refs
current_approval_decision_ids
current_choice_decision_id
current_result_id
current_result_baseline_id
current_manual_evaluation_id
schema_version
~~~

Do not manually reselect a subset.

## 10. Exact canonical digest

Canonical bytes:

~~~python
json.dumps(
    identity.model_dump(mode="json"),
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
~~~

Digest:

~~~python
"sha256:" + hashlib.sha256(canonical_bytes).hexdigest()
~~~

Use ContentDigest validation.

Requirements:

~~~text
same exact actionable basis -> same digest
any mutation-relevant CAS change -> different digest
presentation-only wording -> same digest
random IDs/timestamps/display prose -> NOT in digest
~~~

For GATE_PATH_CHOICE:

~~~text
target_phase = null
eligible_choice_gate_refs = sorted complete exact choice set
~~~

Target phases are resolved from immutable exact HandoverGate revisions, not duplicated in the digest.

The digest is navigation/freshness identity only.

It MUST NOT replace current POST CAS validation.

## 11. Card generation — exact grouping

Create only four decision kinds.

### GATE_AUTHORIZATION

For each exact current AUTHORIZE action:

~~~text
one card per gate
state = PENDING_REQUIRED
one proposed_outcome
~~~

### GATE_APPROVAL

For an exact gate whose current HumanActionProjection exposes APPROVE/REJECT:

~~~text
one card per gate
choices = APPROVE + REJECT where available
~~~

Do not create two cards.

If an exact current HumanApprovalDecision exists for the gate on the current basis:

~~~text
state = RECORDED_REVISABLE
expected_current_approval_decision_id = exact decision_id
display current APPROVE/REJECT value
~~~

Otherwise:

~~~text
state = PENDING_REQUIRED
expected_current_approval_decision_id = null
~~~

A current REJECT is a recorded Human decision, not "missing approval."

### GATE_PATH_CHOICE

All current CHOOSE_PATH actions form ONE decision card.

eligible_choice_gate_refs must be the exact sorted current HUMAN_CHOICE gate set authorized by the current HumanActionBasis/action projection.

~~~text
one card
multiple choices
multiple proposed_outcomes
~~~

If the current HumanChoiceDecision is exact-current and its selected gate remains in the eligible set:

~~~text
state = RECORDED_REVISABLE
expected_current_choice_decision_id = current choice decision_id
~~~

Else:

~~~text
state = PENDING_REQUIRED
~~~

### TECHNICAL_ACCEPTANCE

Use ManualEvaluationProjection only when:

~~~text
TECHNICAL_ACCEPT and/or TECHNICAL_REJECT is currently available
current_result exists
current_evaluation exists
exact ACCEPTED-target technical_gate_ref exists
HumanActionBasis exists
~~~

One card per exact technical gate.

The decision identity binds:

~~~text
HumanActionBasis
gate_ref
expected_result_id
expected_manual_evaluation_id
expected_current_approval_decision_id
~~~

If exact current technical Human approval/rejection exists for that gate:

~~~text
RECORDED_REVISABLE
~~~

otherwise:

~~~text
PENDING_REQUIRED
~~~

Do not use ManualEvaluationActionBasis as the authority CAS for TECHNICAL_ACCEPT/REJECT; the current POST contract uses HumanActionBasis plus exact result/evaluation/current-approval selectors.

## 12. Operational controls that are NOT Decision Cards

Do not convert these into Decision Cards:

~~~text
BLOCK
PAUSE
DEFER
CLEAR_HOLD
ADVANCE
CANCEL
ATTACH_RESULT
EVALUATE
PROMOTE_ACCEPTED
~~~

They remain current existing controls.

DEFER may be explained by Q&A where existing Human hold behavior is applicable, but Q&A does not execute it.

## 13. Proposed outcomes

DecisionCard has:

~~~text
proposed_outcomes: tuple[DecisionProposedOutcome, ...]
~~~

No singular proposed_state implementation field remains.

Single-outcome kinds:

~~~text
GATE_AUTHORIZATION
GATE_APPROVAL
TECHNICAL_ACCEPTANCE
~~~

must have exactly one proposed outcome.

GATE_PATH_CHOICE must have one exact outcome for every eligible gate.

Each outcome:

~~~text
gate_ref
target_phase
label
~~~

Order by:

~~~text
(gate_id, gate_revision, target_phase.value)
~~~

The outcome gate-ref set MUST equal the eligible choice-ref set exactly.

Mismatch is an integrity failure, not a partial card.

## 14. Decision-card status text

UI section heading:

~~~text
Human Decisions
~~~

not "Pending Human Decisions."

Card status must distinguish:

~~~text
Human decision required
~~~

from:

~~~text
Current decision recorded — change remains available
~~~

For RECORDED_REVISABLE cards, display current exact recorded decision separately.

Do not infer "pending" from action availability.

## 15. Basis component vocabulary and matrix

Required component kinds:

~~~text
DECISION_SUBJECT
CURRENT_STATE
PROPOSED_STATE
AUTHORITY_BASIS
POLICY_OR_GATE_BASIS
DESIGN_OR_SCOPE_BASIS
CHANGE_OR_RESULT_BASIS
EVIDENCE
EVALUATION
RISKS_AND_BLOCKERS
GOVERNANCE_REQUIREMENTS
CONSEQUENCES
SOURCE_PROVENANCE
~~~

M0 requirement matrix:

| Component | Authorization | Approval | Path choice | Technical acceptance |
|---|---|---|---|---|
| DECISION_SUBJECT | R | R | R | R |
| CURRENT_STATE | R | R | R | R |
| PROPOSED_STATE | R | R | R | R |
| AUTHORITY_BASIS | R | O | O | R |
| POLICY_OR_GATE_BASIS | R | R | R | R |
| DESIGN_OR_SCOPE_BASIS | D | D | D | D |
| CHANGE_OR_RESULT_BASIS | NA | NA | NA | R |
| EVIDENCE | D | D | D | R |
| EVALUATION | R | R | R | R |
| RISKS_AND_BLOCKERS | R | R | R | R |
| GOVERNANCE_REQUIREMENTS | R | R | R | R |
| CONSEQUENCES | R | R | R | R |
| SOURCE_PROVENANCE | R | R | R | R |

Legend:

~~~text
R = required
O = optional
D = dynamic required/not-applicable under exact current gate semantics
NA = not applicable
~~~

## 16. Dynamic applicability

### DESIGN_OR_SCOPE_BASIS

If current exact HandoverGate has required_artifact_ids:

~~~text
REQUIRED_PRESENT if exact required basis is current
MISSING_REQUIRED if required artifact absent
STALE if present only for stale basis
~~~

Otherwise NOT_APPLICABLE unless another current accepted policy source explicitly requires it.

### EVIDENCE — gate decisions

If exact gate required_evidence_ids is non-empty:

~~~text
required
~~~

Use current exact GateEvaluationRecord context / reasons to determine current presence or missing status.

If no exact policy requires evidence:

~~~text
NOT_APPLICABLE
~~~

Do not use UNKNOWN for deterministically inapplicable evidence.

### EVIDENCE — technical acceptance

Always required.

Use current ManualEvaluationRecord.evidence_ids and exact current subject binding.

### GOVERNANCE_REQUIREMENTS

Render only current accepted HandoverGate/evaluation semantics:

~~~text
policy
hard_stop
authorization_required
required artifacts
required evidence
required dependency slices
required evaluation outcomes
required quality checks
change_surface_policy
risk_policy
~~~

Do NOT fabricate GovernanceProfile levels, profile names, protected-asset classes, or future role/workspace policy.

## 17. Completeness algorithm

After applicability/freshness is established:

~~~text
if any REQUIRED component is STALE:
    STALE
elif any REQUIRED applicability/freshness is UNKNOWN:
    UNKNOWN
elif any REQUIRED component is MISSING_REQUIRED:
    INCOMPLETE
else:
    COMPLETE
~~~

Optional components do not make a card incomplete.

NOT_APPLICABLE components do not make a card incomplete.

Hard integrity contradictions remain PersistenceIntegrityError or equivalent hard failure and are NOT converted into display state.

The UI may label this as the projection of RELAY_DECISION_BASIS_COMPLETE, but:

~~~text
COMPLETE != Human understanding
COMPLETE != approval
COMPLETE != authorization
~~~

## 18. Same-snapshot integration

This is mandatory.

Inside board.service.slice_detail(), keep one:

~~~python
with read_transaction(database) as connection:
~~~

Compute and retain local variables:

~~~text
human_actions = project_human_actions(...)
manual_evaluation = project_manual_evaluation_from_connection(...)
decision_support = project_decision_support(...)
~~~

Pass the exact already-loaded:

~~~text
Slice definition snapshot
lifecycle
current gates / gate projections
latest GateEvaluationRecord
baselines
relevant executions where needed
human_actions
manual_evaluation
~~~

to Decision Support.

decision_support/service.py must not open its own database connection or transaction.

Avoid a second snapshot.

Extend SliceDetail with a required:

~~~text
decision_support: DecisionSupportProjection
~~~

Update constructors/tests explicitly rather than silently allowing board.service to omit the field.

## 19. Provenance/source refs

Use typed DecisionSourceRef with stable exact refs.

Allowed source kinds should cover accepted design categories such as:

~~~text
SLICE_DEFINITION
LIFECYCLE
HANDOVER_GATE
GATE_EVALUATION
BASELINE
AUTHORIZATION
HUMAN_DECISION
SLICE_RESULT
MANUAL_EVALUATION
EVIDENCE
EXECUTION
ACCEPTED_DESIGN_OR_ARTIFACT
POLICY_REFERENCE
~~~

Stable refs should use exact existing identities/revisions, e.g.:

~~~text
slice id + definition revision
lifecycle revision
gate id + gate revision
gate evaluation record id
baseline id
authorization id
Human decision id
result id
manual evaluation id
evidence id
execution id
~~~

Do not create synthetic Evidence to support the UI.

## 20. Statement basis labels

Every explanation statement that can be mistaken for a claim must be classified.

Revision 1 implementation may emit only:

~~~text
CANONICAL_FACT
EVALUATOR_JUDGMENT
UNKNOWN
~~~

ManualEvaluationRecord findings/summary/outcome are evaluator judgment.

Current gate/lifecycle/baseline/decision identities are canonical facts.

Missing/unresolved information is UNKNOWN.

Do not emit EXTERNAL_REFERENCE unless already directly grounded in a current accepted source and necessary; it is not required for this candidate.

Do not emit MODEL_INFERENCE.

## 21. Risks and blockers

Project only governed facts:

~~~text
GateReason values
lifecycle blockage/holds
ManualEvaluationRecord.risk_status
ManualEvaluationRecord.change_surface_status
ManualEvaluationRecord.toolchain_change_status
manual evaluation findings
missing/stale required components
~~~

Do not add a score.

Do not infer risk severity.

If no additional risk statement exists, use scoped language equivalent to:

~~~text
No additional current risk statement is available in this exact governed basis.
~~~

Do not claim global CLEAR unless exact authoritative RiskStatus says CLEAR.

## 22. Consequences

Consequences must be deterministic summaries of current existing command semantics only.

At minimum:

~~~text
AUTHORIZE:
records exact current authorization grant and reevaluates;
does not itself advance lifecycle.

APPROVE / REJECT:
records exact Human decision and reevaluates;
does not collapse acceptance/promotion.

CHOOSE_PATH:
records exact selected gate choice and reevaluates;
does not execute handover by itself.

TECHNICAL_ACCEPT / TECHNICAL_REJECT:
records exact Human decision over current result/evaluation/gate basis;
technical acceptance != promotion.
~~~

If a consequence is not established by current semantics, return UNKNOWN.

No speculative benefit/risk prose.

## 23. Structured Q&A only

No free-form chat input.

DecisionQuestionKind set is fixed.

Answers are computed only from a current DecisionCard.

DecisionAnswer contains:

~~~text
decision ref
question kind
answer
basis labels
source refs
freshness
~~~

No persistence.

No provider call.

No RAG.

No vector store.

No external web access.

## 24. GET Q&A route behavior

Extend the existing Slice detail GET/HEAD route with optional query parameters equivalent to:

~~~text
decision=<sha256:...>
question=<DecisionQuestionKind>
~~~

Rules:

~~~text
neither supplied:
normal page + Decision Cards

both valid/current:
normal page + requested structured answer

one missing or syntactically malformed:
422

syntactically valid digest but not a current card:
409 STALE_DECISION_BASIS
~~~

HEAD retains no response body.

Do not create a POST Q&A route.

Do not execute Human actions from query handling.

Use deterministic HTML error presentation consistent with existing board behavior.

## 25. Q&A semantics

WHY_REQUIRED:
current policy/gate reason and decision state.

WHAT_IS_CURRENT:
current lifecycle/basis/current recorded Human decision when any.

WHAT_WOULD_CHANGE:
single proposed outcome or full ordered choose-one-of outcome set.

WHAT_EVIDENCE_EXISTS:
exact current required/available evidence and applicability state.

WHAT_DID_THE_EVALUATOR_FIND:
current manual evaluation outcome/summary/findings where applicable;
otherwise NOT_APPLICABLE/UNKNOWN according to exact policy.

WHAT_BLOCKS_OR_IS_UNKNOWN:
current gate reasons, missing/stale/unknown required components, lifecycle blockage.

WHAT_IF_APPROVED:
only meaningful deterministic consequence for approval-style cards; path choice must not be collapsed into a preselected route.

WHAT_IF_REJECTED:
exact existing rejection consequence where relevant.

WHAT_IF_DEFERRED:
explain current existing DEFER/hold behavior only if available; Q&A does not execute it.

WHAT_GOVERNANCE_REQUIREMENTS_APPLY:
current exact HandoverGate requirements only.

## 26. UI integration

In render_slice_detail(), place Human Decisions before raw existing Human action forms.

Each card must show:

1. title;
2. "Derived / non-authoritative";
3. decision status;
4. exact basis digest;
5. current state;
6. proposed outcome(s);
7. why required/revisable;
8. completeness;
9. component applicability/freshness;
10. evidence separately from evaluation;
11. risks/blockers/unknowns;
12. consequences;
13. source refs;
14. structured Ask-about-this-decision links;
15. existing explicit authority form controls, visually distinct.

Do not remove the existing raw Human Actions, Manual Evaluation, governance, history, or execution inspection surfaces unless the accepted design explicitly requires relocation.

Avoid duplicate action forms in a way that makes semantics ambiguous. If a Decision Card renders an existing authority form, preserve the existing form contract exactly and ensure the raw section does not create confusing duplicate submissions. Prefer factoring current form rendering helpers rather than copying POST-field logic.

## 27. Human action forms — preserve exact CAS

Do not redesign POST routes or service calls.

Preserve exact current fields:

### approve/reject

~~~text
basis = HumanActionBasis JSON
gate_id
expected_current_approval_decision_id
reason
csrf_token
~~~

### choose

~~~text
basis
selected_gate_id
expected_current_choice_decision_id
reason
csrf_token
~~~

### technical accept/reject

~~~text
basis = HumanActionBasis JSON
gate_id
expected_result_id
expected_manual_evaluation_id
expected_current_approval_decision_id
reason
csrf_token
~~~

### authorize

Preserve current exact authorization form/service inputs.

Decision Support may prepare render data, but existing mutation services remain authoritative.

## 28. Accessibility

Core behavior must work without JavaScript.

Requirements:

~~~text
semantic headings
semantic lists/tables
keyboard-focusable links/forms
no color-only status
visible COMPLETE/INCOMPLETE/UNKNOWN/STALE text
visible non-authority label
visible stale/incomplete warnings
wrap-safe IDs/digests
distinct accessible labels for question/source/action controls
~~~

Do not introduce a frontend framework.

## 29. Deterministic ordering

Cards:

~~~text
GATE_AUTHORIZATION
GATE_APPROVAL
GATE_PATH_CHOICE
TECHNICAL_ACCEPTANCE
~~~

Within a kind:

~~~text
gate_id or ""
target_phase or ""
basis_digest
~~~

Proposed outcomes:

~~~text
gate_id
gate_revision
target_phase.value
~~~

Choice refs:

~~~text
gate_id
gate_revision
~~~

Source refs/components/findings/questions must have stable deterministic order.

Incidental SQLite row order must not affect projection equality.

## 30. Integrity handling

Do not soften current integrity errors.

Examples:

~~~text
mixed gate baselines
conflicting full-basis evaluation records
missing referenced baseline
current manual evaluation with invalid successor observation
missing accepted-result Human decision
invalid cross-project relation
malformed durable IDs
choice outcome/ref mismatch
~~~

These remain hard integrity errors.

Only non-integrity incompleteness becomes:

~~~text
INCOMPLETE
UNKNOWN
STALE
~~~

## 31. Required focused tests — models/digest

Prove:

~~~text
strict/frozen/extra-forbid
exact enum values
fixed canonical JSON vector + expected SHA-256
same basis -> same digest
every HumanActionBasis field mutation -> different digest
current approval decision ID mutation -> different approval digest
current choice ID mutation -> different choice digest
eligible choice set mutation -> different choice digest
result ID mutation -> different technical digest
manual evaluation ID mutation -> different technical digest
technical current approval ID mutation -> different technical digest
presentation-only text mutation -> same digest
PendingDecisionRef never uses HumanDecisionId as pending identity
~~~

## 32. Required focused tests — generation/state

Prove:

~~~text
AUTHORIZE -> one authorization card
APPROVE + REJECT same gate -> one approval card
CHOOSE_PATH multiple gate actions -> one path-choice card
TECHNICAL_ACCEPT + TECHNICAL_REJECT same gate -> one technical card
operational controls -> no Decision Card
no duplicate cards

no current decision -> PENDING_REQUIRED
current exact APPROVE -> RECORDED_REVISABLE
current exact REJECT -> RECORDED_REVISABLE
current exact path choice -> RECORDED_REVISABLE
current exact technical accept/reject -> RECORDED_REVISABLE
stale prior decision -> not RECORDED_REVISABLE
~~~

## 33. Required focused tests — proposed outcomes

Prove:

~~~text
single-outcome cards have exactly one outcome
path choice has one outcome per eligible exact gate
outcome refs == eligible choice refs
stable ordering
current recorded choice displayed separately
no singular proposed_state model field
~~~

## 34. Required focused tests — completeness

Exercise every decision kind.

Must include:

~~~text
all required/current -> COMPLETE
missing required -> INCOMPLETE
unresolved applicability -> UNKNOWN
required stale -> STALE
pre-evaluation inapplicable evaluation -> NOT_APPLICABLE
gate with no evidence requirement -> EVIDENCE NOT_APPLICABLE
gate with required evidence missing -> MISSING_REQUIRED
technical acceptance evidence -> REQUIRED_PRESENT
absent GovernanceProfile infrastructure -> no false MISSING_REQUIRED
optional missing material -> still COMPLETE when all required current
~~~

## 35. Required focused tests — provenance/statements

Prove:

~~~text
durable state facts -> CANONICAL_FACT
manual evaluator findings -> EVALUATOR_JUDGMENT
unresolved basis -> UNKNOWN
no MODEL_INFERENCE
source refs carry exact stable identities
no synthetic Evidence
~~~

## 36. Required focused tests — Q&A and non-mutation

Prove:

~~~text
GET Q&A causes no DB mutation
all fixed question kinds deterministic
answer reads only current DecisionCard
valid current digest -> 200
valid stale/unknown current digest -> 409
malformed digest/question -> 422
one missing query parameter -> 422
no POST Q&A
no provider/model path
no auto-action from COMPLETE
question link cannot submit authority action
~~~

## 37. Required focused tests — web/action preservation

Prove existing action protections still hold:

~~~text
CSRF required
server-bound HUMAN actor preserved
exact HumanActionBasis preserved
expected current approval/choice IDs preserved
stale POST basis still -> 409
Decision Card does not weaken/reimplement mutation checks
HEAD body remains empty
core page works without JS
evidence and evaluation visibly separate
Derived / non-authoritative visible
recorded revisable decision not labeled pending/missing
path choice says choose one of
~~~

## 38. No persistence/dependency behavior

Explicitly assert/verify:

~~~text
no migration v6
no new DB table
no persisted Decision Card
no persisted answer
no clarity-feedback write
no telemetry write
no new package dependency
no lockfile change
~~~

If any becomes necessary: STOP.

## 39. Implementation sequence

Recommended bounded sequence:

### I1 — Models and digest
Implement decision_support/models.py, canonical identity serialization, digest, validators, deterministic ordering. Add model tests.

### I2 — Pure projector
Implement decision_support/service.py using already-loaded projection values only. Add generation/completeness/provenance/Q&A tests.

### I3 — Board projection integration
Extend SliceDetail and board.service same-snapshot construction. Keep existing projections and integrity behavior. Add board-model/service tests.

### I4 — Render/web integration
Render cards, Q&A links/answers, status, sources, outcomes and existing authority controls. Extend GET/HEAD query handling and exact 409/422 behavior. Add render/web tests.

### I5 — Regression/quality
Run all focused + full quality gates. Inspect diff scope. Commit/push candidate. Stop.

Do not create intermediate governance acceptance records.

## 40. Quality gates

Run exactly:

~~~bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_decision_support_models.py
uv run pytest tests/unit/test_decision_support_service.py
uv run pytest tests/unit/test_board_models.py
uv run pytest tests/unit/test_board_service.py
uv run pytest tests/unit/test_board_render.py
uv run pytest tests/unit/test_board_web.py
uv run pytest tests/unit/test_repository_contract.py

uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
~~~

If formatting repair is needed, inspect changed files afterward.

## 41. Scope verification before commit

Run:

~~~bash
git status --short
git diff --name-only a3b489bb4682314a706f66c57ee0bc1bb917542c...HEAD
git diff --stat a3b489bb4682314a706f66c57ee0bc1bb917542c...HEAD
~~~

Expected changes are only the authorized source/test files.

No design/authority/evaluation/acceptance record may be edited.

## 42. Candidate and push

Create one coherent implementation candidate on:

~~~text
implementation/1.9-human-decision-support-governance-review-surface
~~~

Do NOT update main.

Do NOT update the design branch.

Do NOT rebase.

Do NOT squash accepted design history.

Push candidate and obtain exact remote SHA.

Then verify GitHub Actions for that exact SHA.

## 43. Required Codex report

Return:

~~~text
SLICE 1.9 IMPLEMENTATION: COMPLETE / STOPPED

Authority:
RLY-S19-IMPL-AUTH-001

Repository:
cschrupp/relay

Branch:
implementation/1.9-human-decision-support-governance-review-surface

Authorized baseline:
a3b489bb4682314a706f66c57ee0bc1bb917542c

Accepted design subject:
03d6efecf9ad4aaec0c5967b9486650399d0a492

Candidate SHA:
<exact>

Merge base with authorized baseline:
<exact>

ahead_by / behind_by:
<x> / <y>

Executor:
Codex

Actual model/runtime:
<exact if exposed>

Changed files:
<complete list>

I1 models/digest:
COMPLETE / STOPPED

I2 pure projection/Q&A:
COMPLETE / STOPPED

I3 same-snapshot board integration:
COMPLETE / STOPPED

I4 server-rendered web surface:
COMPLETE / STOPPED

Decision Card kinds:
4 / exact result

New persistence migrations:
NONE

New tables:
NONE

Dependency changes:
NONE

Provider/model calls:
NONE

Focused tests:
<exact counts per command>

Repository-contract tests:
<exact count>

Ruff format:
PASS/FAIL

Ruff lint:
PASS/FAIL

Pyright:
PASS/FAIL

Full pytest:
<exact count>

Build:
PASS/FAIL

git diff --check:
PASS/FAIL

Exact-head GitHub Actions:
<run id> — <status>

Deviations:
NONE or exact list

New work discovered:
NONE or exact list

Final disposition:
STOP FOR SOL INDEPENDENT IMPLEMENTATION REVIEW
~~~

## 44. Hard stop

Codex is NOT authorized to:

- evaluate/accept its own implementation;
- create RLY-S19 implementation-evaluation records;
- grant Human technical acceptance;
- merge/promote to main;
- finalize or close Slice 1.9;
- open Slice 1.10;
- add profile/asset enforcement;
- add free-form LLM Q&A;
- call a provider/model;
- begin Phase 3;
- execute Relay agents on a real project.

Stop after candidate push and evidence report.

**Implementation authorized != implementation accepted.**
