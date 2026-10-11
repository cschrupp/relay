# Slice 1.9 — Independent Implementation Evaluation

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Record:** RLY-S19-EVAL-001  
**Outcome:** REWORK  
**Evaluator:** GPT-5.6 Sol — independent implementation reviewer / governance gatekeeper

## Evaluated subject

~~~text
Implementation authority:
RLY-S19-IMPL-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
a3b489bb4682314a706f66c57ee0bc1bb917542c

Exact accepted combined design subject:
03d6efecf9ad4aaec0c5967b9486650399d0a492

Human design acceptance:
RLY-S19-DESIGN-ACCEPT-001 — ACCEPTED

Implementation candidate:
becf1c80965d8c7c36cb081a3bfa1e66b074c13a

Implementation branch:
implementation/1.9-human-decision-support-governance-review-surface
~~~

The remote implementation branch was independently verified at the exact candidate SHA. The candidate is exactly one commit ahead and zero behind the authorized baseline, with merge base equal to the authorized baseline.

## Independent evidence reviewed

The evaluator independently inspected the exact ancestry and changed-file surface, the accepted Revision 1 + Rework 1 + Rework 2 design, implementation authority, Decision Support models and projector, same-snapshot SliceDetail integration, board rendering and GET/HEAD Q&A, existing POST/CAS preservation, focused tests, and exact-head CI.

Exact-head GitHub Actions run 38167151931 is SUCCESS at the exact candidate SHA. CI independently confirms Ruff format/lint PASS, Pyright 0 errors / 0 warnings / 0 informations, 671 tests PASS, and build PASS.

## Passed characteristics

- changed-file scope is entirely within the authorized production/test surface;
- no migrations, new tables, dependencies, lockfile changes, workflow changes, provider/model calls, RAG, telemetry persistence, or clarity-feedback persistence;
- DecisionBasisIdentityV1 and canonical SHA-256 digest semantics match the accepted contract;
- paired approval/rejection and technical accept/reject actions are grouped into one decision;
- path choice is represented as one decision with all exact proposed outcomes;
- PENDING_REQUIRED versus RECORDED_REVISABLE is represented explicitly;
- same-snapshot SliceDetail construction is preserved;
- Decision Support opens no database transaction;
- GET/HEAD Q&A is deterministic, non-persistent, read-only, and keyed by current digest;
- malformed Q&A parameters fail 422 and non-current valid digests fail 409;
- no POST Q&A route exists;
- existing POST Human-action services and CAS fields remain authoritative and unchanged;
- Decision Cards are visibly derived/non-authoritative;
- evidence and evaluator findings remain visually distinct;
- no MODEL_INFERENCE is emitted;
- operational controls remain outside Decision Card generation.

# Findings

## F001 — BLOCKING — GATE_PATH_CHOICE basis/completeness is projected from only one representative gate

The accepted design defines GATE_PATH_CHOICE as one Human decision over the complete exact eligible HUMAN_CHOICE gate set. The candidate correctly computes all proposed outcomes, but project_decision_support first selects choice_gates[0] as a representative and calls the single-gate card builder. It later replaces only the decision identity, state, recorded choice, proposed_outcomes, choices, and title.

Components, artifact/evidence applicability, governance requirements, gate reasons/blockers, risk statements, source refs, evidence statements, why_required, and consequence provenance therefore remain derived exclusively from the first eligible gate.

A second eligible path can carry different artifact/evidence requirements, hard-stop/risk policy, or blockers without participating in RELAY_DECISION_BASIS_COMPLETE or Human-facing governance Q&A.

### Required correction

Project path-choice policy from the complete eligible gate set. Include every eligible gate in provenance; aggregate/display governance requirements per exact gate; evaluate artifact/evidence applicability across every eligible gate; aggregate reasons/blockers/risk facts with gate identity; and compute completeness over the complete choice basis. Add heterogeneous multi-path tests proving no requirement from a non-first path can be omitted while the card remains COMPLETE.

## F002 — BLOCKING — Required artifact basis/provenance is incomplete, especially for TECHNICAL_ACCEPTANCE

Rework 1 requires DESIGN_OR_SCOPE_BASIS to be REQUIRED_PRESENT when the exact gate or current technical subject requires artifacts, and requires exact artifact IDs in source refs.

The ordinary gate helper checks required_artifact_ids but the source-ref builder emits no artifact refs. More importantly, the technical component helper receives no HandoverGate/current artifact basis and unconditionally marks DESIGN_OR_SCOPE_BASIS NOT_APPLICABLE with text claiming no current gate policy requires design/scope material.

A technical ACCEPTED-target gate with required artifacts can therefore be misrepresented as artifact-inapplicable and still COMPLETE.

### Required correction

Add exact artifact source refs; pass the exact technical gate/current artifact basis into technical component construction; mark required technical artifacts REQUIRED_PRESENT; missing required artifacts MISSING_REQUIRED; stale/unknown material accordingly; and use NOT_APPLICABLE only when current policy establishes it. Add present/missing/no-requirement artifact tests for ordinary and technical decisions.

## F003 — MAJOR — SliceDetail does not enforce Decision Support as a required projection

The accepted handoff requires decision_support: DecisionSupportProjection as a required SliceDetail field and explicitly says constructors/tests must be updated rather than silently allowing omission.

The candidate instead gives decision_support a default factory. Production board.service supplies the field, but any alternative SliceDetail constructor can omit Decision Support silently and still produce a valid detail projection.

### Required correction

Remove the default and make decision_support required. Update every constructor/test explicitly. Add a model-level test proving omission fails validation and a service-level test proving the production projector always supplies it.

## F004 — MAJOR — RECORDED_REVISABLE why_required semantics do not satisfy Rework 1

Rework 1 requires why_required for a recorded revisable decision to explain why revision remains available before the governed transition and what exact decision is currently recorded.

The candidate correctly displays state and current_recorded_decision separately, but the gate-card why_required is computed independently of state from gate reasons or generic policy text, and the technical card likewise uses the same pending-style explanation for both states.

### Required correction

For GATE_APPROVAL, GATE_PATH_CHOICE, and TECHNICAL_ACCEPTANCE, build state-specific RECORDED_REVISABLE why_required statements that identify the current exact Human decision and explain why revision remains available. Keep PENDING_REQUIRED wording distinct and include the current Human decision in source refs. Add tests for current approve, reject, path choice, technical accept, and technical reject.

# Rework boundary

This is bounded implementation rework under existing RLY-S19-IMPL-AUTH-001 authority. No architecture/design escalation or new Human implementation authority is required.

Do not redesign DecisionBasisIdentityV1 or digest semantics; change existing Human mutation CAS/services; add persistence/migration/dependencies; add provider/model execution or free-form Q&A; add telemetry/clarity persistence; implement GovernanceProfile/Protected Verification Asset enforcement; alter lifecycle/governance semantics; open Slice 1.10; begin Phase 3; or merge/promote to main.

Preserve becf1c80965d8c7c36cb081a3bfa1e66b074c13a as immutable evaluated history.

# Evaluation outcome

~~~text
RLY-S19-EVAL-001 — REWORK
~~~

The candidate is not technically eligible for Human acceptance yet. The rework is bounded and implementation-local.