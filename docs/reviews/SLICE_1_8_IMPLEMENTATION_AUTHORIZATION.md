# Relay — Slice 1.8 Governance Assurance Reference Model — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-10  
**Record:** RLY-S18-IMPL-AUTH-001  
**Decision:** AUTHORIZED

## Human Authority decision

The Human explicitly authorizes bounded implementation of Slice 1.8 — Governance Assurance Reference Model and requests a detailed Codex implementation scope.

## Exact implementation basis

~~~text
Repository:
cschrupp/relay

Canonical accepted-design baseline:
eae25f0837bbce435e54fc3437b502dea1224744

Slice opening:
RLY-S18-OPEN-001 — OPEN

Resume:
RLY-S18-RESUME-001 — RESUMED

Design authorities:
RLY-S18-DESIGN-AUTH-001 — AUTHORIZED
RLY-S18-DESIGN-AUTH-002 — AUTHORIZED

Accepted combined design:
Revision 1:
c67fe2147fcb9a37e7ab13de92bfc79bb8688919
Revision 2 Amendment:
87acec9b961e9d3773f75922dddb29520cb55e3b
Revision 2 Rework 1:
ef89856816e1671443eec0a4422742b35e1e32df

Independent design evaluation:
RLY-S18-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S18-DESIGN-ACCEPT-001 — ACCEPTED

Canonical design promotion:
RLY-S18-DESIGN-PROMOTE-001 — AUTHORIZED / PROMOTED
~~~

Implementation must preserve the exact accepted combined design and may not redesign the architecture merely because another representation appears cleaner.

## Authorized implementation objective

Materialize the Human-accepted Slice 1.8 design into Relay's canonical governance-assurance reference documentation.

This Slice is deliberately documentation/governance-model hardening. It is not production/runtime implementation.

## Authorized change surface

Primary expected files:

~~~text
docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
~~~

Narrow supporting documentation may be added or updated only when required to make the accepted model complete, reviewable, and traceable. Permitted categories are:

~~~text
worked governance-assurance examples
negative-case catalogue
Relay-to-external-assurance mapping documentation
source-traceability/freshness documentation
implementation handoff/evidence
registry and current canonical documentation projections
~~~

Suggested supporting paths, if needed:

~~~text
docs/architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md
docs/references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md
docs/reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF.md
~~~

Exact supporting filenames may follow repository conventions. Do not create extra documents merely to expand surface area.

## Mandatory implementation content

The canonical reference model must incorporate the accepted Revision 1 + Revision 2 + Rework 1 semantics, including at minimum:

- four non-substitutable statement classes: evidence, verification judgment, authority decision, executed transition;
- exact assurance subject and policy basis;
- evidence/verification/authority/promotion non-substitutability;
- cross-cutting non-authoritative Decision Support;
- policy-specific DecisionBasisProjection completeness and REQUIRED_PRESENT / OPTIONAL_PRESENT / NOT_APPLICABLE / UNKNOWN / MISSING_REQUIRED distinctions;
- RELAY_DECISION_BASIS_COMPLETE;
- role != identity != authority and RELAY_ACTOR_IDENTITY_BOUND;
- policy-relative RELAY_EXECUTION_PROVENANCE_SUFFICIENT;
- external mapping freshness and stale-to-UNKNOWN semantics for new claims;
- Human-gate necessity: discretionary authority remains Human, deterministic checks should be mechanical;
- workflow-agnostic governance and explicit prohibition on importing upstream workflow authority;
- planning-artifact normalization as future Slice 2.3 input only;
- GovernanceProfile semantics, policy/risk inputs, fail-closed unknowns, no implementer/runtime/provider self-downgrade, and prospective-only profile changes;
- RELAY_GOVERNANCE_PROFILE_BOUND;
- Protected Verification Assets defined by mutation authority rather than secrecy;
- explicit separation of evaluator judgment from verification-asset mutation authority;
- RELAY_VERIFICATION_ASSETS_PROTECTED;
- non-authoritative GovernanceEffectivenessTelemetry, with assurance value and governance cost kept separate;
- ContextManifest static/dynamic downstream requirement;
- Slice ownership: 1.9 Decision Support, 1.10 source/promotion enforcement, 2.2 roles, 2.3 context/work packet, 2.4 workspace authority, 3.1 execution;
- conservative external-source provenance and mapping.

## Required explanatory examples

Implementation must include the original Revision-1 worked examples plus the Revision-2 cases.

At minimum cover:

1. design evaluation ACCEPT followed by separate Human design acceptance;
2. implementation evidence PASS followed by evaluator REWORK;
3. evaluator ACCEPT followed by Human refusal to accept;
4. pre-issued conditional promotion authority followed by mechanical promotion;
5. stale canonical parent blocking promotion;
6. SLSA evidence mapped into Relay without creating promotion authority;
7. AI evaluator separation not satisfying a SLSA requirement defined in terms of two trusted persons;
8. UNKNOWN property blocking a promotion-critical gate;
9. Slice opening DecisionBasisProjection with implementation evidence NOT_APPLICABLE;
10. technical acceptance with required evaluation MISSING_REQUIRED;
11. unknown GovernanceProfile applicability blocking work;
12. profile escalation and prospective Human/policy-authorized downgrade;
13. implementer attempt to modify a protected acceptance/evaluation asset;
14. implementer-authored unit test that is not protected;
15. Spec Kit/OpenSpec/BMAD planning artifact normalized into intent but still awaiting Relay authorization;
16. external workflow says approved while Relay remains unauthorized;
17. stale external mapping becoming UNKNOWN for a new claim;
18. low clarity feedback affecting explanation only, not authority;
19. costly governance telemetry not weakening policy.

## Required negative cases

The implementation must explicitly reject at minimum:

~~~text
evidence == evaluation
evaluation == Human acceptance
Human acceptance == promotion
promotion eligibility == promotion authority
Decision Support == authority
clarity feedback == authority
missing-but-inapplicable == UNKNOWN
missing-required == NOT_APPLICABLE
agent-selected low risk == valid GovernanceProfile
runtime capability == permission to downgrade governance
later downgrade == retroactive authorization
historical success == policy bypass
all tests == protected tests
protected == secret
evaluator ACCEPT == mutation authority
implementer may weaken acceptance assets to obtain PASS
external workflow approved == Relay authorized
normalized intent == authorized Work Packet
adapter inference == Human scope decision
stale mapping == current PASS
telemetry == evaluation
~~~

## External assurance and source boundary

External sources and standards are inputs/provenance only. They never create Relay authority.

The implementation may refine current documentation for SLSA v1.2, NIST SSDF, DORA, Google New SDLC, Geoffrey Litt, the Principal AI Engineer Handbook, Spec Kit, OpenSpec, BMAD, Consort, GitLab, and other already catalogued sources only where supported by the existing source catalog.

Do not claim new certifications, SLSA levels, NIST compliance, product superiority, or empirical safety advantage.

## Explicitly unauthorized implementation

~~~text
production Python/source changes: NONE
runtime behavior changes: NONE
test-suite source changes: NONE unless a repository-contract test fails solely because current documentation registration mechanically requires an existing-test fixture update; STOP before such a test change
schema migration: NONE
new runtime dependency: NONE
new dev dependency: NONE
GitHub settings/ruleset/branch-protection mutation: NONE
Decision Card implementation: NONE
Q&A implementation: NONE
GovernanceProfile policy engine: NONE
planning-artifact adapters: NONE
role-contract implementation: NONE
workspace enforcement: NONE
verification-asset enforcement: NONE
telemetry collection/dashboard: NONE
attestation engine/signing: NONE
compliance engine: NONE
promotion executor: NONE
competitive experiment execution: NONE
agent execution: NONE
Slice 1.9 or 1.10 opening: NONE
Phase 3 capability: NONE
~~~

## Locked/immutable records

Codex must not edit in place:

~~~text
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN_REV2_AMENDMENT.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN_REV2_REWORK_1.md
docs/reviews/SLICE_1_8_DESIGN_EVALUATION_001.md
docs/reviews/SLICE_1_8_DESIGN_EVALUATION_002.md
docs/reviews/SLICE_1_8_DESIGN_ACCEPTANCE.md
docs/reviews/SLICE_1_8_DESIGN_PROMOTION_AUTHORITY.md
this implementation authorization record
~~~

Historical authority/evaluation/source records are immutable.

## Preferred implementation role

~~~text
Role: IMPLEMENTATION_AGENT
Preferred executor: Codex / GPT-5.6 Luna-equivalent implementation role
Evaluator: GPT-5.6 Sol
~~~

Implementer and evaluator remain distinct.

## Quality evidence

Before handoff, the candidate must pass:

~~~text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
~~~

Run repository-contract/registry tests directly when available.

GitHub Actions CI must succeed on the exact candidate SHA before independent implementation evaluation.

Passing checks are evidence only, not acceptance.

## Stop / escalation conditions

STOP and report rather than widening scope if implementation appears to require:

- any production/runtime code change;
- any test code change beyond a purely mechanical repository-contract fixture issue;
- any dependency or lockfile change;
- schema/persistence change;
- lifecycle, authority, evaluator, or Human-decision semantic change;
- a concrete GovernanceProfile taxonomy/scoring engine;
- executable policy automation;
- external workflow adapter code;
- Decision Support/Q&A UI;
- filesystem/tool/network enforcement;
- repository settings mutation;
- signing/attestation infrastructure;
- a new external compliance or certification claim;
- opening another Slice;
- executing the competitive benchmark;
- agent/runtime/provider calls;
- contradiction among the accepted Revision 1, Revision 2, Rework 1, and current canonical architecture.

## Authority boundary

This authorization permits production of a Slice 1.8 implementation candidate and implementation evidence only.

It does not authorize the implementer to independently evaluate or accept its own result, Human technical acceptance, canonical promotion, Slice 1.8 closure, Slice 1.9/1.10 work, Phase 3, or real-project agent execution.

**Implementation authorized != implementation accepted.**
