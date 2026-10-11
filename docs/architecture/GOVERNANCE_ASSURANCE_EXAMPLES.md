# Governance Assurance — Worked Examples and Negative Cases

**Status:** IMPLEMENTATION SUPPORT / AWAITING INDEPENDENT IMPLEMENTATION EVALUATION
**Document class:** Working review material
**Authority:** `RLY-S18-IMPL-AUTH-001`
**Semantic basis:** [Canonical reference model](GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md), accepted Revision 1 + Revision 2 + Rework 1

These examples are normative explanatory tests of the accepted semantics, not actual evaluations, authority records, executed transitions, or a new test suite. Symbols `C`, `P`, `Q`, and `A` denote exact immutable candidate, parent, policy, and authority identities within each example; they are not moving branches or real grants. Any future implementation must bind real exact identities and policy-required evidence.

## E01 — Design evaluation followed by Human acceptance

An independent evaluator reviews exact design subject C under Q and issues ACCEPT with exact evidence references. That verification judgment does not accept the design for the Human. The Human subsequently issues a separate design-acceptance authority record bound to C. The two records retain separate issuers, meanings, and exact subjects. Implementation still needs separate implementation authority. Covers D02, D07–D08.

## E02 — Passing implementation evidence followed by REWORK

CI and required tests pass on exact implementation C. The evaluator uses that evidence but finds C changes behavior outside A's scope and issues REWORK. Evidence PASS remains a true historical observation; it never becomes evaluation ACCEPT. Correct output does not establish scope-conformant execution. Covers D02, D15, D38, D48.

## E03 — Evaluator ACCEPT followed by Human refusal or deferral

The evaluator ACCEPTs C under Q. The Human declines technical acceptance or defers the decision because a consequential trade-off remains unacceptable. The evaluation record remains intact, but there is no Human acceptance record for C. Required acceptance is absent, so evaluation alone cannot satisfy promotion predicates or permit promotion. Covers D08–D09, D15.

## E04 — Conditional authority followed by mechanical promotion

A Human-issued finalization authority A already binds exact candidate C, expected parent P, and explicit conditions: exact/current CI, independent ACCEPT, exact Human acceptance, and all other Q-required properties. Later those conditions become satisfied and P is still canonical. The executor checks A and the predicates, performs the authorized operation, and records the resulting transition. No second discretionary approval is required merely to repeat deterministic checks. A alone did not prove promotion occurred, and eligibility alone did not authorize it. Covers D09–D10, D37, D50.

## E05 — Stale canonical parent blocks promotion

A binds C and expected canonical parent P. Before promotion, canonical main advances to a different exact parent P2. `RELAY_CANONICAL_PARENT_CURRENT` cannot PASS; the established mismatch blocks promotion even if C's CI and evaluation passed. The executor does not silently rebase, merge, substitute P2, or reinterpret A. It reports the changed basis for the separately governed next action. Covers D15–D16, D30.

## E06 — External SLSA evidence without Relay authority

An external verifier supplies pinned SLSA v1.2 provenance/VSA about exact C. A requirement-specific mapping may use that evidence only under the external predicate's exact meaning and Relay's applicable policy. Even a valid external PASS is evidence, not a Relay Human acceptance or promotion-authority record. With A absent, Relay promotion remains forbidden. No SLSA level or certification is claimed by this example. Covers D19, D21, D28, D38; sources `SRC-SLSA-V1_2`, `SRC-SLSA-SOURCE-REQUIREMENTS` in the [catalog](../references/GOVERNANCE_ASSURANCE_AND_AGENTIC_SDLC_SOURCES.md).

## E07 — AI independence is not two trusted persons

Codex/Luna implements C and Sol independently evaluates it under Relay policy Q. The applicable Relay separation properties may PASS if the required actor/session identities and exact evaluation are established. No evidence of two trusted human persons is provided. Neither model separation nor two model sessions satisfies the catalogued SLSA two-trusted-person requirement; an adapter must not emit `SLSA_SOURCE_TWO_PARTY_REVIEWED` from those Relay properties. Missing external evidence cannot become SATISFIED. Covers D18, D20; sources `SRC-SLSA-VERIFIED-PROPERTIES`, `SRC-SLSA-SOURCE-REQUIREMENTS`.

## E08 — UNKNOWN blocks a promotion-critical predicate

Q requires `RELAY_CONTROL_CONTINUITY_VERIFIED` for C, but an authority-to-execution reference cannot be resolved. Available evidence cannot establish continuity, so the result is UNKNOWN, not PASS or an invented proven violation. C cannot become promotion-eligible while that required property is unresolved. Mechanical success would not repair the missing authority chain. Covers D16, D29–D30, D37.

## E09 — Opening decision with inapplicable implementation evaluation

The pending decision is whether to open design work. Q requires exact intent, roadmap basis, scope, risks, and authority context, but no implementation evaluation exists or is required at this gate. The projection marks implementation evidence/evaluation NOT_APPLICABLE with that policy basis. If every required applicable component is current and present, `RELAY_DECISION_BASIS_COMPLETE` may PASS. This neither certifies Human understanding nor opens the Slice. Opening still requires the explicit Human act. Covers D43–D46.

## E10 — Required evaluation missing at technical acceptance

The pending decision is technical acceptance of C. Q explicitly requires independent evaluation, but the record cannot be located. The projection reports MISSING_REQUIRED rather than NOT_APPLICABLE, and decision-basis completeness does not PASS. If the uncertainty were whether Q requires evaluation at all, the applicability would instead be UNKNOWN. The explanation cannot invent evaluation or acceptance. Covers D44–D45.

## E11 — Unknown GovernanceProfile applicability

C proposes a change with unresolved production/data impact, an input Q requires before classification. The implementer's “low risk” assertion does not settle it. Profile applicability is UNKNOWN, `RELAY_GOVERNANCE_PROFILE_BOUND` cannot PASS, and action is blocked or escalated according to Q. Runtime access and a green upstream workflow do not permit execution while the pre-action basis is unresolved. Covers D53–D56.

## E12 — Policy-driven escalation

Before execution of C, a newly established credential-access requirement triggers Q's stricter controls. The governed basis identifies the policy-selected stricter profile/version and required evidence, separation, and workspace restrictions. Action waits for valid pre-action binding and satisfied requirements. If previous work already occurred, escalation governs future or explicitly restarted work, without rewriting that previous trajectory. Covers D54–D56, RW1-D04.

## E13 — Authorized prospective downgrade

A Human or a policy-authorized rule grants a downgrade for a separately governed future action and records the exact profile/policy, authority, scope, and effective basis durably. That future action can use the newly valid profile once bound before execution. Earlier action C ran with missing required controls: its historical judgment remains under the profile applicable when it ran. The later downgrade cannot change C to PASS or retrospectively authorize it. Covers D55–D56, RW1-D04.

## E14 — Attempted mutation of a protected acceptance test

Q/profile designates an acceptance test as protected and grants the implementer no mutation authority. The implementer requests a change that would weaken the acceptance threshold to obtain PASS. In a future enforcing workspace, the write is blocked and recorded. If it actually succeeds without authority, the trajectory is non-conformant rather than repaired by passing tests. Evaluator ACCEPT or a recommendation is not mutation permission: any permitted change requires explicit policy-recognized authority/capability and any separate review prerequisite. One physical evaluator/approver must explicitly hold both capabilities. This example describes required semantics, not implemented enforcement. Covers D57–D58, RW1-D02.

## E15 — Implementer-authored unit test is not universally protected

The exact profile allows implementation tests within scope and does not designate a new unit test as protected. The implementer writes the test under valid implementation authority. Test authorship is permitted; it does not waive protection for other profile-designated acceptance/evaluation assets. `RELAY_VERIFICATION_ASSETS_PROTECTED` is assessed against actual designated assets and mutation authority, not a blanket rule that all tests are immutable or hidden. Covers D57–D58.

## E16 — Normalization still awaits Relay authorization

A future adapter receives an exact Spec Kit, OpenSpec, or BMAD artifact with source version/digest and supported objective, scope, and criteria. It preserves provenance and produces NormalizedEngineeringIntent under an identified normalization contract. That intent is an input awaiting Relay policy and authority, not an authorized Work Packet. If an input lacks a required acceptance criterion or explicit non-scope, the adapter exposes UNKNOWN or MISSING_REQUIRED and does not fabricate a Human scope decision. No adapter is executed by this example. Covers D51–D52, D61; sources `SRC-GITHUB-SPEC-KIT-2026`, `SRC-OPENSPEC-2026`, `SRC-BMAD-METHOD-2026`.

## E17 — Upstream approved while Relay is unauthorized

An enterprise workflow marks an artifact approved/ready and its checks green. Relay has no exact implementation authority for that input. Relay remains unauthorized: approved/ready do not authorize, done does not mean Human acceptance, and green does not mean evaluation ACCEPT. Importing the source label preserves provenance only. Covers D51–D52, D65.

## E18 — Stale mapping becomes UNKNOWN for a new claim

A historical mapping assessed an exact framework requirement/version with evidence, assessor, verified_at, and a review trigger. That trigger occurs before a new external claim. Freshness becomes STALE, so the new claim resolves to UNKNOWN until reverified even if the prior assessment was SATISFIED. The old record is preserved. Stale is not automatically FAIL and never current PASS; neither the old mapping nor re-verification supplies Relay promotion authority. Covers D26–D29, D49.

## E19 — Low clarity changes support, not authority

A Human reports low DecisionClarityFeedback for the exact pending decision. Future Decision Support surfaces explanations, basis references, comparisons, or questions and may encourage deferral. It neither issues a defer/accept command automatically nor invalidates a valid authority act. The rating measures self-reported clarity, not objectively proven cognition or evaluation quality. Covers D43–D46, D60, D64.

## E20 — Costly governance does not waive policy

Future GovernanceEffectivenessTelemetry shows long Human wait time, duplicated mechanical checks, and high cost alongside defects detected. Assurance value and governance cost remain separate observations. Those observations can inform a separately governed policy discussion; they do not weaken the current profile, waive evidence, replace evaluation, or authorize promotion. Historical success likewise grants no policy waiver. No telemetry is collected and no competitive experiment is run here. Covers D24–D25, D50, D59.

## Explicit negative cases

Each row rejects the stated substitution or shortcut. These 30 cases supplement the worked examples without adding normative property names.

| ID | Rejected claim | Required boundary |
|---|---|---|
| N01 | evidence == evaluation | Facts require a separately governed judgment. |
| N02 | evaluation == Human acceptance | Human acceptance is an explicit exact-subject authority act. |
| N03 | Human acceptance == promotion | Acceptance neither executes nor independently authorizes promotion. |
| N04 | promotion eligibility == promotion authority | Derived predicates require a valid separate grant. |
| N05 | Decision Support == authority | A projection cannot issue a governance command. |
| N06 | clarity score == authority | Self-reported clarity neither grants nor invalidates authority. |
| N07 | missing-but-inapplicable == UNKNOWN | Policy-established inapplicability is NOT_APPLICABLE. |
| N08 | missing-required == NOT_APPLICABLE | Required absent material is MISSING_REQUIRED. |
| N09 | role == identity == authority | Each has a distinct policy-bound basis. |
| N10 | agent-selected low risk == valid GovernanceProfile | Relay policy and/or Human Authority selects profiles. |
| N11 | runtime capability == governance downgrade authority | Capability cannot weaken policy. |
| N12 | later downgrade == retroactive authorization | Historical actions retain their original applicable basis. |
| N13 | past success == policy waiver | Current policy still governs. |
| N14 | all tests == protected | Policy designates protected assets; implementation tests may be writable. |
| N15 | protected == secret | Mutation authority defines protection, not secrecy. |
| N16 | evaluator ACCEPT == mutation authority | Review can be a prerequisite; explicit mutation authority is separate. |
| N17 | implementer may rewrite acceptance assets to get PASS | Unauthorized mutation remains non-conformant regardless of resulting output. |
| N18 | external workflow approved == Relay authorized | Upstream status is provenance only. |
| N19 | normalized intent == authorized Work Packet | Relay must bind exact input through its own policy and authority. |
| N20 | adapter inference == Human scope decision | Unsupported scope, criteria, or non-scope cannot be invented. |
| N21 | stale external mapping == current PASS | New claims are UNKNOWN until reverified. |
| N22 | telemetry == evaluation | Observation is not a separately governed judgment. |
| N23 | telemetry == authority | Metrics cannot grant or relax controls. |
| N24 | runtime permission == Relay authority | Tool/repository capability is defense in depth, not a grant. |
| N25 | external compliance evidence == Relay authority | External evidence cannot create acceptance or promotion authority. |
| N26 | model/session separation == SLSA two-party review | AI separation does not supply evidence of two trusted persons. |
| N27 | moving branch == exact subject | Resolve immutable subject identity before judging. |
| N28 | successful mechanical promotion == proof of authority | Executed transition and valid prior grant remain distinct. |
| N29 | source citation or competitor behavior == proven Relay outcome | References inform design, not authority or empirical guarantees. |
| N30 | same actor is evaluator -> mutation authority inferred | Both roles/capabilities must be explicitly policy-recognized. |

These cases do not independently evaluate or accept the Slice 1.8 candidate. Sol retains independent implementation evaluation responsibility.
