# Relay — Slice 1.9 Human Decision Support and Governance Review Surface — Design Revision 1

**Document class:** Lockable design record  
**Status:** LOCKED / PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Design revision:** 1  
**Design authority:** RLY-S19-DESIGN-AUTH-001 — AUTHORIZED  
**Design subject baseline:** 5bf25378b15955b6e21252ec3f9cc91dcf7192d7  
**Design-authority commit:** 8ea33bb01c94dd0fc7d24185702ad4f98ed1b687  
**Canonical parent:** 7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

## 1. Design objective

Slice 1.9 adds a deterministic, Human-facing Decision Support projection to the existing Relay board.

It does not add another authority plane.

The implementation target is the minimum surface that lets a Human answer, for one exact pending decision:

~~~text
What am I deciding?
Why is this decision required now?
What exact state and subject does it apply to?
What evidence/evaluation supports it?
What is missing, stale, blocked, risky, or unknown?
What happens if I approve, reject, choose, or defer?
Where did each statement come from?
Which existing explicit Human command performs the decision?
~~~

The governing direction is:

~~~text
durable governed Relay state
        |
        v
exact deterministic read projection
        |
        v
Decision Card / structured explanation
        |
        v
existing explicit Human Authority command
        |
        v
existing governed mutation service
~~~

The projection may explain authority. It never becomes authority.

## 2. Accepted constraints consumed from Slice 1.8

The design consumes, without redefining:

~~~text
Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Human Authority
Decision Support != Executed Transition

RELAY_DECISION_BASIS_COMPLETE
RELAY_ACTOR_IDENTITY_BOUND
RELAY_GOVERNANCE_PROFILE_BOUND
RELAY_VERIFICATION_ASSETS_PROTECTED

REQUIRED_PRESENT
OPTIONAL_PRESENT
NOT_APPLICABLE
UNKNOWN
MISSING_REQUIRED
~~~

The complete Slice 1.8 verified-property vocabulary remains unchanged.

No RELAY_HUMAN_UNDERSTANDS, comprehension PASS, quiz gate, inferred cognition claim, or equivalent property is introduced.

## 3. Current product seam

Relay already has the required authority and durable-state foundations:

- SliceDetail is built from one SQLite read snapshot.
- HumanActionProjection exposes current advisory controls plus exact HumanActionBasis.
- ManualEvaluationProjection exposes exact result/evaluation/technical-acceptance state.
- Existing Human command services perform durable writes with stale-basis checks.
- Existing board forms carry exact basis and CSRF protection.
- Current gate evaluation, baselines, result history, evaluation history, and execution records are already projected.

Slice 1.9 therefore introduces no parallel state machine and no parallel authority service.

## 4. D01 — Decision Support is a derived read model

Introduce a new bounded package:

~~~text
src/relay_engine/decision_support/
    __init__.py
    models.py
    service.py
~~~

Its public responsibility is pure projection/explanation.

It may consume existing immutable/durable projections and return typed presentation models. It does not own SQLite writes, Human decisions, lifecycle transitions, evaluation records, authorizations, or promotion.

No method in decision_support may call a Human mutation service.

## 5. D02 — Pending decision identity is not a recorded decision identity

Do not reuse:

~~~text
DecisionId       # durable engineering judgment
HumanDecisionId  # durable Human decision already made
~~~

for a decision that is merely pending.

Define a read-model identity:

~~~text
PendingDecisionRef
    slice_id
    decision_kind
    basis_digest
    gate_id? / gate_revision? / target_phase?
    result_id?
    manual_evaluation_id?
~~~

basis_digest is a ContentDigest computed from deterministic canonical serialization of the exact decision-basis identity.

It is deterministic, non-durable, non-authoritative, suitable for GET navigation/stale detection, and recomputed whenever its exact basis changes.

No new UUID prefix is required.

~~~text
pending decision ref != HumanDecisionId
basis digest != authority
~~~

## 6. D03 — Supported Decision Card kinds are intentionally narrow

Revision 1 defines exactly four pending discretionary decision kinds:

~~~text
GATE_AUTHORIZATION
GATE_APPROVAL
GATE_PATH_CHOICE
TECHNICAL_ACCEPTANCE
~~~

Projection rules:

1. HumanActionKind.AUTHORIZE -> one GATE_AUTHORIZATION card for that exact gate.
2. APPROVE and REJECT for the same exact gate -> one GATE_APPROVAL card with two explicit authority choices.
3. CHOOSE_PATH -> one GATE_PATH_CHOICE card; choices remain the exact current eligible gate paths.
4. TECHNICAL_ACCEPT and TECHNICAL_REJECT for the same exact result/evaluation basis -> one TECHNICAL_ACCEPTANCE card with two explicit authority choices.

The following existing controls remain ordinary operational/governed controls, not pending Decision Cards in Revision 1:

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

This does not downgrade their governance. It prevents Slice 1.9 from falsely labeling every clickable control as a distinct pending Human decision.

DEFER may be offered adjacent to a Decision Card as an existing Human hold action when already available, but it is not part of the pending decision identity.

Promotion semantics remain owned by accepted prior behavior plus Slice 1.10 hardening; Slice 1.9 does not reinterpret PROMOTE_ACCEPTED.

## 7. D04 — Exact DecisionBasisProjection contract

Define:

~~~text
DecisionSupportProjection
    cards: tuple[DecisionCard, ...]
    stale_notice: DecisionSupportNotice | None

DecisionCard
    decision: PendingDecisionRef
    title
    why_required
    current_state
    proposed_state
    choices: tuple[DecisionChoice, ...]
    components: tuple[DecisionBasisComponent, ...]
    evidence_summary
    evaluation_summary
    risks
    unknowns
    blocking_findings
    consequences
    governance_requirements
    source_refs
    completeness
    explicit_non_authority
    question_kinds
~~~

The card is immutable presentation data.

A DecisionChoice references an existing Human/manual-evaluation action kind and the exact current basis needed by the existing form. The Decision Support package does not define a new mutation command.

## 8. D05 — Basis components and applicability

Define a fixed component vocabulary sufficient for current Relay decisions:

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

Each DecisionBasisComponent contains:

~~~text
kind
applicability:
    REQUIRED_PRESENT
    OPTIONAL_PRESENT
    NOT_APPLICABLE
    UNKNOWN
    MISSING_REQUIRED

freshness:
    CURRENT
    STALE
    UNKNOWN
    NOT_APPLICABLE

summary
source_refs
~~~

Rules:

- absence of a non-required component is NOT_APPLICABLE only when current policy/gate semantics establish non-applicability;
- unresolved applicability is UNKNOWN;
- a required component that cannot be located is MISSING_REQUIRED;
- a present but stale component is still present, but the basis is not complete;
- a component for another result/gate/baseline is stale or integrity-invalid, never silently current.

## 9. D06 — Decision-basis completeness

Define:

~~~text
DecisionBasisCompleteness:
    COMPLETE
    INCOMPLETE
    UNKNOWN
    STALE
~~~

This is a projection of accepted RELAY_DECISION_BASIS_COMPLETE semantics, not a generic verified-property engine.

Rules:

- COMPLETE: every policy-required component is REQUIRED_PRESENT and CURRENT; all explicitly inapplicable components are NOT_APPLICABLE; no required applicability is unresolved.
- INCOMPLETE: at least one required component is MISSING_REQUIRED.
- UNKNOWN: applicability or exact basis needed to establish completeness is UNKNOWN.
- STALE: required material exists but is stale or bound to a superseded/currently different basis.

The UI may display the property name RELAY_DECISION_BASIS_COMPLETE, but must not claim that completeness proves understanding, correctness, acceptance, or authorization.

No generic property evaluator is introduced.

## 10. D07 — Same-snapshot construction is mandatory

Decision Support must be computed from the same caller-owned SQLite read transaction used to build SliceDetail.

Do not open a second transaction to construct a Decision Card.

The board service should:

1. load current Slice/lifecycle/gates/evaluation/baselines/executions;
2. compute HumanActionProjection;
3. compute ManualEvaluationProjection;
4. pass those exact projections plus already loaded detail inputs to the Decision Support projector;
5. construct one SliceDetail containing all three projections.

This prevents a card from explaining one state while its authority form is bound to another.

## 11. D08 — Existing action basis remains the mutation CAS

Decision Support must not invent a weaker stale-check mechanism.

For generic Human controls, existing HumanActionBasis remains the mutation compare-and-swap basis.

For Slice 1.7 manual-evaluation actions, existing ManualEvaluationActionBasis fields remain authoritative.

A Decision Card may include the current basis for rendering, but POST routes continue to validate the existing exact bases in the existing services.

~~~text
Decision Card basis digest
    !=
replacement for HumanActionBasis / ManualEvaluationActionBasis
~~~

If an exact actionable basis is unavailable, the card is omitted from actionable cards or rendered as non-actionable diagnostic information with a stale/incomplete notice.

## 12. D09 — Provenance is explicit and typed

Define:

~~~text
DecisionSourceKind:
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

DecisionSourceRef:
    kind
    stable_ref
    label
~~~

stable_ref uses an existing durable ID/revision/commit/digest where available.

Do not create synthetic Evidence merely to support a UI explanation.

Source references are navigation/provenance metadata, not authority.

## 13. D10 — Facts, evaluator judgment, and explanation remain distinct

Every rendered explanatory statement carries one of the accepted basis labels:

~~~text
CANONICAL_FACT
EVALUATOR_JUDGMENT
EXTERNAL_REFERENCE
MODEL_INFERENCE
UNKNOWN
~~~

Revision 1 implementation may emit CANONICAL_FACT, EVALUATOR_JUDGMENT, and UNKNOWN only.

It must not emit MODEL_INFERENCE because no model execution is authorized.

EXTERNAL_REFERENCE is not required initially unless an already-authoritative current source reference is directly available.

Unknowns remain explicit.

## 14. D11 — Risks and blockers are projected, not invented

Risk/blocking material may come from:

- current gate reasons;
- current manual-evaluation findings;
- explicit RiskStatus;
- explicit ChangeSurfaceStatus;
- explicit toolchain status;
- missing/stale required components;
- current lifecycle blockage/hold state;
- exact dependency/gate facts already loaded.

There is no new risk scorer.

No model may infer a hidden risk level.

If no authoritative risk statement exists, do not convert absence into CLEAR unless current governed state explicitly says CLEAR.

## 15. D12 — Consequences are deterministic command semantics

A Decision Card may explain only consequences supported by accepted command semantics.

Examples:

- gate authorization records a current authorization grant and causes governed basis reevaluation; it does not itself advance lifecycle;
- gate approval/rejection records a Human decision and reevaluates current gates;
- path choice records the selected current gate path and reevaluates;
- technical acceptance/rejection records the exact Human decision over current result/evaluation basis; acceptance is distinct from promotion.

When a consequence cannot be established, show UNKNOWN.

No speculative benefit/risk prose is allowed in deterministic Revision 1.

## 16. D13 — Structured decision-scoped Q&A, no LLM

Revision 1 implements deterministic structured Q&A, not free-form model inference.

Define:

~~~text
DecisionQuestionKind:
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

Define:

~~~text
DecisionAnswer
    decision: PendingDecisionRef
    question_kind
    answer
    basis_labels
    source_refs
    freshness
~~~

The answer is generated only from the current DecisionCard.

No provider/model call, retrieval agent, vector database, internet call, or external tool is authorized.

Future free-form Q&A may consume the same exact Decision Basis, but requires separate authority and must preserve MODEL_INFERENCE labeling and current-basis binding.

## 17. D14 — Q&A is GET/read-only and freshness-bound

The existing Slice detail route may accept optional query parameters equivalent to:

~~~text
decision=<basis_digest>
question=<DecisionQuestionKind>
~~~

No new POST mutation route is required for Q&A.

Behavior:

- no query -> normal detail page plus Decision Cards;
- valid current decision + valid question -> deterministic answer;
- malformed question/key -> 422;
- syntactically valid decision key that is no longer current -> 409 STALE_DECISION_BASIS;
- question never executes a Human action.

Answers are not persisted.

Refreshing after state changes recomputes the basis.

## 18. D15 — Human Authority controls remain separate

The Decision Card visually and structurally separates explanation/provenance/question controls from the explicit Human Authority action form.

A question link, expandable explanation, source link, or completeness indicator can never submit an authority form.

Existing CSRF protection and server-bound HUMAN actor checks remain unchanged for POST actions.

Decision Support does not add a generic approve endpoint.

## 19. D16 — GovernanceProfile and protected-asset presentation is fail-honest

Slice 1.8 defines conceptual GovernanceProfile and Protected Verification Asset semantics, but the current product has no accepted profile taxonomy, selector, persisted profile binding, or enforcement engine.

Revision 1 must not invent:

- a profile name;
- a risk score;
- a profile level;
- protected-asset classification;
- mutation permission;
- compliance status.

If an authoritative current source is absent, the card states that the governed source is not implemented/available for this decision.

Applicability is NOT_APPLICABLE only when current policy establishes non-applicability. Otherwise it is UNKNOWN.

Typed presentation fields are reserved so later 2.2–2.4 consumers can populate them without redefining the card.

## 20. D17 — Clarity feedback is designed but deferred from implementation

DecisionClarityFeedback remains an optional product concept:

~~~text
decision basis identity
rating 1..5
optional comment
optional confusion tags
recorded_at
~~~

It is not authority, evidence, evaluation, or proof of understanding.

Revision 1 implementation does not persist or collect clarity feedback because that durable write is unnecessary for the minimum Decision Card objective.

No disabled fake feedback form should be rendered.

A later increment requires separate authority if persistent feedback is desired.

## 21. D18 — Governance-effectiveness telemetry is presentation-only and deferred

Slice 1.9 owns future presentation of governance-effectiveness measures, not telemetry collection or policy adaptation.

Revision 1 does not add telemetry tables, event instrumentation, aggregation jobs, dashboards, composite scores, or automatic profile changes.

If already-existing exact facts are displayed, they retain their source semantics and are not promoted into a governance score.

~~~text
telemetry != authority
low latency != permission to weaken controls
high clarity != acceptance
historical success != waiver
~~~

## 22. D19 — Board integration

Extend SliceDetail with:

~~~text
decision_support: DecisionSupportProjection
~~~

The existing Slice Card remains the lifecycle/work overview.

The Slice detail page gains a Pending Human Decisions section before raw existing Human action forms.

Each Decision Card renders:

1. decision title and explicit Derived / non-authoritative label;
2. exact subject/basis identity and freshness;
3. current -> proposed state;
4. why the decision is required;
5. completeness/applicability summary;
6. evidence/evaluation;
7. risks, blockers, unknowns;
8. deterministic consequences;
9. source references;
10. structured Ask about this decision links;
11. existing explicit Human Authority form(s), visually separated.

Existing raw governance/evaluation/history sections remain inspectable.

## 23. D20 — Accessibility and information hierarchy

Use the existing server-rendered HTML architecture.

Requirements:

- semantic headings and lists;
- no color-only state communication;
- text labels for COMPLETE/INCOMPLETE/UNKNOWN/STALE;
- keyboard-focusable question/source/action controls;
- explicit stale/incomplete warning text;
- no JavaScript requirement for core review/decision behavior;
- long IDs/digests remain wrap-safe;
- source and action controls have distinct accessible labels.

No frontend framework is introduced.

## 24. D21 — No persistence migration and no dependency change

The minimum implementation requires:

~~~text
database migration: NONE
new tables: NONE
new persisted decision-support objects: NONE
runtime dependencies: NONE
development dependencies: NONE
~~~

Decision Support is reconstructed from current durable Relay state.

If implementation discovers that required current Decision Basis cannot be projected without new persistence, that is a design-contract escalation, not permission to add migration v6.

## 25. D22 — Expected implementation surface

Authorized implementation, if later granted, should be bounded principally to:

~~~text
src/relay_engine/decision_support/__init__.py
src/relay_engine/decision_support/models.py
src/relay_engine/decision_support/service.py

src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py

tests/unit/test_decision_support_models.py
tests/unit/test_decision_support_service.py
tests/unit/test_board_models.py
tests/unit/test_board_service.py
tests/unit/test_board_render.py
tests/unit/test_board_web.py
~~~

No changes are expected in:

~~~text
src/relay_engine/persistence/migrations.py
pyproject.toml
uv.lock
.github/workflows/**
repository settings
lifecycle transition matrix
human_control mutation semantics
manual_evaluation mutation semantics
Slice 1.8 semantic documents
~~~

Small import/export adjustments in package __init__.py files are permissible if mechanically required.

## 26. D23 — Deterministic ordering

Decision Cards use fixed ordering:

~~~text
GATE_AUTHORIZATION
GATE_APPROVAL
GATE_PATH_CHOICE
TECHNICAL_ACCEPTANCE
~~~

Within a kind, order by gate_id or empty, target_phase or empty, then basis_digest.

Components, sources, choices, risk statements, findings, and question kinds use deterministic stable ordering.

The same durable snapshot must serialize to byte-equivalent projection values regardless of incidental database row order.

## 27. D24 — Integrity handling

Conflicting durable facts that existing services classify as PersistenceIntegrityError remain hard errors.

Decision Support must not soften:

- mixed gate baselines;
- conflicting full-basis evaluations;
- missing referenced baseline;
- current manual evaluation without exact current successor observation;
- missing accepted-result Human decision;
- invalid cross-project relationship;
- malformed durable IDs.

For non-integrity incompleteness, render fail-honestly:

~~~text
integrity contradiction -> ERROR
missing required basis -> INCOMPLETE
unresolved applicability -> UNKNOWN
stale basis -> STALE
~~~

## 28. D25 — Required implementation tests

### Projection identity and determinism

- identical current basis -> identical basis_digest;
- lifecycle/gate/evaluation/result basis change -> different digest;
- ordering deterministic under reordered source rows;
- pending ref never aliases HumanDecisionId or DecisionId.

### Decision-card generation

- one authorization action -> one authorization card;
- approve + reject same gate -> exactly one approval card;
- technical accept + technical reject -> exactly one technical-acceptance card;
- choice paths project one exact choice decision basis;
- operational controls do not become pending Decision Cards;
- no duplicate cards.

### Completeness/applicability

- required present/current -> COMPLETE;
- missing required -> INCOMPLETE;
- unresolved applicability -> UNKNOWN;
- stale exact basis -> STALE;
- inapplicable evaluation at a pre-evaluation gate -> NOT_APPLICABLE rather than UNKNOWN.

### Provenance and statement classes

- evaluator findings -> EVALUATOR_JUDGMENT;
- durable current facts -> CANONICAL_FACT;
- missing/unresolved material -> UNKNOWN;
- no MODEL_INFERENCE emitted in Revision 1.

### Authority separation

- Q&A GET cannot mutate database;
- Decision Support service calls no mutation command;
- existing POST still requires CSRF, HUMAN actor, and exact existing basis;
- stale card key cannot execute or expose stale authority action;
- completeness never triggers action automatically.

### Q&A

- each fixed question returns only current-card material;
- stale basis digest -> 409;
- malformed key/question -> 422;
- no free-form provider/model request exists;
- source refs accompany factual/evaluator answers.

### UI and regression

- card says Derived / non-authoritative;
- evidence and evaluation are separately labeled;
- unknowns/blockers visible;
- authority form visually separated;
- core path works without JavaScript;
- existing Human action tests pass;
- existing manual-evaluation tests pass;
- repository-contract tests pass;
- full suite passes;
- no migration v6;
- no dependency/lockfile change.

## 29. D26 — Explicit non-goals

Revision 1 does not implement:

- free-form LLM Q&A;
- provider/model execution;
- retrieval/RAG;
- persistent chat history;
- clarity-feedback storage;
- telemetry collection/aggregation;
- governance scoring;
- profile taxonomy/selection;
- protected-asset enforcement;
- actor-identity redesign;
- ContextManifest;
- work packets;
- workspace policy;
- canonical-source protection;
- promotion-executor hardening;
- new Human Authority semantics;
- automatic approval/acceptance/promotion;
- Phase 3 execution.

## 30. D27 — Design-to-implementation acceptance contract

A later implementation candidate is conformant only if:

~~~text
Decision Support is purely derived/read-only
AND current Decision Cards bind exact current action bases
AND paired Human choices are represented as one decision
AND UNKNOWN / MISSING_REQUIRED / STALE remain visible
AND structured Q&A is deterministic and read-only
AND no model/provider call exists
AND existing mutation services remain authoritative
AND no migration/dependency/lifecycle semantic change occurs
AND Slice 1.10 / 2.2 / 2.3 / 2.4 ownership is preserved
~~~

Passing tests are engineering evidence only.

## 31. Required design review

This design must receive independent evaluation against:

~~~text
RLY-S19-OPEN-001
RLY-S19-DESIGN-AUTH-001
canonical parent 7e690f9fe22b34226fff2d3364d1ed94b91dc9f7
closed Slice 1.8 assurance semantics
existing accepted Human/manual-evaluation command contracts
~~~

The evaluator returns only:

~~~text
ACCEPT
REVISE
ESCALATE
~~~

No implementation is authorized by this design record.

## 32. Gate state after design submission

~~~text
Slice 1.9:
OPEN

Design:
COMPLETE / SUBMITTED FOR INDEPENDENT DESIGN REVIEW

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~

**A clear decision surface is not authority. It is the interface through which authority is exercised deliberately.**
