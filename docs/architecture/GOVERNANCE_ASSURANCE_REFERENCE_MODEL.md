# Relay — Governance Assurance Reference Model

**Status:** IMPLEMENTED / AWAITING INDEPENDENT IMPLEMENTATION EVALUATION
**Document class:** Living canonical projection
**Canonical navigation:** `current-baseline` -> this registered living reference
**Implementation authority:** `RLY-S18-IMPL-AUTH-001`
**Accepted design baseline:** `eae25f0837bbce435e54fc3437b502dea1224744`
**Implementation start:** `a7cd87fea89e3b0273da1d0c0884336cc7857357`
**Scope:** Documentation/governance semantics only; no executable enforcement

## 1. Authority, precedence, and reading path

This is the consolidated reference for the Human-accepted Slice 1.8 design. The governing subject is the combined chain below, not any revision in isolation:

| Record | Exact design head | Precedence |
|---|---|---|
| [Revision 1](../slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN.md) | `c67fe2147fcb9a37e7ab13de92bfc79bb8688919` | Normative wherever not explicitly amended |
| [Revision 2 Amendment](../slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN_REV2_AMENDMENT.md) | `87acec9b961e9d3773f75922dddb29520cb55e3b` | Overrides Revision 1 where explicit |
| [Revision 2 Rework 1](../slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL_DESIGN_REV2_REWORK_1.md) | `ef89856816e1671443eec0a4422742b35e1e32df` | Overrides Revision 2 where explicit |

`RLY-S18-DESIGN-EVAL-002 — ACCEPT`, `RLY-S18-DESIGN-ACCEPT-001 — ACCEPTED`, and `RLY-S18-DESIGN-PROMOTE-001 — AUTHORIZED / PROMOTED` govern that combined design. Historical design headers retain their original submission status. They do not override the subsequent acceptance records. This implementation candidate has not received independent implementation evaluation, Human technical acceptance, or promotion authority.

[Worked examples and negative cases](GOVERNANCE_ASSURANCE_EXAMPLES.md) exercise these semantics. The [external mapping matrix](../references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md) explains mapping boundaries and source traceability. The [source catalog](../references/GOVERNANCE_ASSURANCE_AND_AGENTIC_SDLC_SOURCES.md) remains the authoritative metadata location for external references. External citations provide provenance, never Relay authority.

## 2. Relay owns semantic authority — D01–D03, D43

Relay is a workflow-agnostic governance control plane for AI software engineering. It owns authorization, exact baseline binding, design acceptance, implementation authority, execution provenance, evaluation, Human technical acceptance, promotion eligibility, promotion authority, canonical promotion, and control state. The accepted deterministic substrate remains in place; this model introduces no second lifecycle, authority system, or evaluator system.

External frameworks map onto Relay controls and evidence. They do not redefine the lifecycle or create Human acceptance or promotion authority. Relay-native planning is supported but not required.

The four non-substitutable statement classes are:

| Class | Meaning | Examples |
|---|---|---|
| FACT / EVIDENCE | An observed or produced fact about an exact subject | Commit, digest, changed-file set, CI/test result, runtime/provider/model observation, source-control state, external verifier output |
| VERIFICATION JUDGMENT | Application of exact policy to evidence | Design ACCEPT/REVISE/ESCALATE, implementation ACCEPT/REWORK/ESCALATE, property PASS/FAIL/UNKNOWN, eligibility judgment |
| AUTHORITY DECISION | Explicit Human or previously granted Relay authority | Slice opening, design authorization/acceptance, implementation authorization, technical acceptance, finalization/promotion authority |
| EXECUTED TRANSITION / PROMOTION RECORD | Evidence that an already-authorized operation occurred | Canonical fast-forward, established accepted baseline, advanced canonical pointer, promotion record |

```text
evidence cannot become evaluation by implication
evaluation cannot become authority by implication
authority cannot prove execution occurred
execution cannot manufacture authority

Evidence PASS != Evaluation ACCEPT != Human acceptance != Promotion
Promotion eligibility != Promotion authority
Unblocked != authorized
Authorized != accepted
Accepted != promoted
```

The Control/Governance plane owns policy and authority; the Execution plane performs bounded work; the Evidence/Provenance plane records observations. Verification judges evidence under policy. Human acceptance is an explicit Control/Governance act. Eligibility, valid promotion authority, mechanical execution, and the resulting promotion evidence remain distinct. The control plane never infers authority from execution capability or runtime success.

Decision Support reads across these planes at each policy-required Human decision. It is derived and non-authoritative, not a fifth authoritative statement class or a stage inserted after verification.

## 3. Exact subject, policy, and conceptual contracts — D04–D09

The following are conceptual contracts, not Python types, database schemas, APIs, or serialized formats.

| Concept | Required conceptual content |
|---|---|
| `AssuranceSubjectRef` | `project_id`, `subject_kind`, and applicable exact `slice_id`, `repository_id`, `git_commit`, `artifact_id`, `content_digest`, `execution_id`, `evaluation_id`, `authority_record_id` |
| `PolicyBasis` | `policy_id`, `policy_version`, `policy_digest`, `effective_scope` |
| `EvidenceRef` | `evidence_type`, `evidence_id`, exact `subject`, `content_digest`, `producer`, `observed_at` |
| `VerificationJudgment` | `judgment_id`, `judgment_type`, exact `subject`, `policy_basis`, `evaluator`, `evidence_refs`, `outcome`, `findings`, `issued_at`, optional `supersedes` |
| `AuthorityDecision` | `authority_id`, `authority_type`, exact `subject`, `authority_actor`, `authority_basis`, `granted_scope`, `explicit_non_authority`, `conditions`, `issued_at` |
| `PromotionEligibility` | Exact `subject`, `policy_basis`, `required_properties`, `property_results`, `evaluator_state`, `human_acceptance_state`, `parent_freshness_state`, result `ELIGIBLE / INELIGIBLE / UNKNOWN` |

`subject_kind` determines which subject fields are mandatory; fields that do not apply need not be populated. Exact immutable identifiers are authoritative. A moving branch name or human-readable URI is navigation only. An ambiguous or partially resolved subject cannot satisfy a promotion-critical property.

Evidence belongs to one exact subject. Verification belongs to that subject plus exact policy. Evidence from a stale or successor commit cannot silently pass for the current subject. An old judgment cannot be reinterpreted under an incompatibly changed policy. Evidence can be superseded or contradicted, but its historical bytes are not rewritten.

Authority is never inferred from a role name, model identity, branch ownership, CI success, evaluator outcome, runtime capability, or external compliance result. An attestation representing an existing authority decision mirrors that decision; it does not issue it.

Eligibility is derived verification state, not authority. It is `ELIGIBLE` only when every required predicate is satisfied exactly. Required `FAIL` or `UNKNOWN` prevents eligibility; lack of evidence is not falsely labeled a proven failure.

## 4. Logical predicates and compatibility — D11–D13, D64

The initial Relay-native logical predicate family is:

```text
relay.dev/design-evaluation/v1
relay.dev/design-acceptance/v1
relay.dev/implementation-authorization/v1
relay.dev/execution-provenance/v1
relay.dev/evaluation/v1
relay.dev/human-acceptance/v1
relay.dev/promotion-authorization/v1
relay.dev/promotion/v1
relay.dev/control-state/v1
```

Each future predicate must represent, directly or by exact reference, its identity/major version, exact subject, issuer/actor identity, issuance time, applicable policy/authority basis, applicable evidence, outcome/decision, supersession, and content digest/canonical representation. Semantically inapplicable fields may be omitted, but statement classes cannot be collapsed.

Same-major-version semantics remain compatible. Additive optional fields are allowed; incompatible field requirements require a new major version, and incompatible meanings require a new predicate/property identity or major version. A verified-property name is semantically immutable once accepted. External mappings pin the exact framework version and publication status.

No JSON schema, signing format, transport, storage backend, signature algorithm, in-toto envelope, Sigstore, or transparency log is selected or implemented. Faithful future external envelopes are possible; they cannot change Relay meaning. Slice 1.8 does not require cryptographic signing. Canonical Git/repository governance remains the substrate; source/promotion hardening belongs to Slice 1.10.

`DecisionBasisProjection`, `DecisionClarityFeedback`, and `GovernanceEffectivenessTelemetry` do not become authoritative attestation families. Future serialization remains non-authoritative. A serialized GovernanceProfile is a policy artifact/reference, not authority by virtue of serialization.

## 5. Exact native verified properties — D14–D16, D45, D47–D48, D56, D58, D63

This table is the complete accepted vocabulary. These are Relay-native properties, not standardized SLSA properties. Generic outcomes are exactly `PASS`, `FAIL`, and `UNKNOWN`; context-specific evaluation outcomes retain their existing vocabulary.

For each row, `PASS` requires the stated condition. A demonstrated violation is `FAIL`; insufficient evidence, unresolved applicability, or identity/policy ambiguity is `UNKNOWN`, never implicit `PASS`. A required promotion-critical `FAIL` or `UNKNOWN` blocks promotion. These definitions do not implement a property engine.

| Property | PASS only when |
|---|---|
| `RELAY_EXACT_AUTHORIZED_BASELINE` | The exact execution/design/evaluation subject is bound to the exact baseline authorized by the governing authority record. |
| `RELAY_EVIDENCE_SUBJECT_EXACT` | All required evidence binds to the exact evaluated subject; stale or successor-subject evidence does not pass. |
| `RELAY_IMPLEMENTER_EVALUATOR_SEPARATION` | The implementation execution actor/session required by policy is distinct from the evaluator actor/session required by policy. |
| `RELAY_SCOPE_CONFORMANCE` | Observed changes and behavior remain inside authorized scope and do not exercise explicit non-authority. |
| `RELAY_INDEPENDENT_EVALUATION` | The governing policy's evaluator-separation requirements are met and an exact-subject evaluation exists. |
| `RELAY_HUMAN_ACCEPTED` | An explicit Human acceptance authority record binds to the exact accepted subject. |
| `RELAY_PROMOTION_AUTHORIZED` | Exact valid promotion authority exists and is current for the subject. |
| `RELAY_CANONICAL_PARENT_CURRENT` | The expected canonical parent/ref basis remains current at promotion time. |
| `RELAY_FAIL_CLOSED` | Unresolved required state, stale basis, missing evidence, or integrity ambiguity prevents rather than permits the governed transition. |
| `RELAY_RUNTIME_IDENTITY_RECORDED` | Runtime/provider/model provenance required by the applicable execution policy is recorded to the required completeness. |
| `RELAY_CONTROL_CONTINUITY_VERIFIED` | The causal chain from authority through execution/evaluation/acceptance to the proposed transition is reconstructable without an authority gap. |
| `RELAY_CANONICAL_PROJECTION_LINEAGE_VALID` | Living canonical projections advance under repository-contract lineage rules without skipped incompatible revisions or history reconstruction. |
| `RELAY_DECISION_BASIS_COMPLETE` | Every component required and applicable under the exact policy for the exact Human decision is present/current, and inapplicable components are deterministically or explicitly understood as `NOT_APPLICABLE`. This proves provision of the basis, not cognition. |
| `RELAY_ACTOR_IDENTITY_BOUND` | The actor/issuer responsible for the action/claim is independently bound to the identity required by applicable policy. Self-asserted role/model/session identity is insufficient. |
| `RELAY_EXECUTION_PROVENANCE_SUFFICIENT` | Applicable-policy provenance exists and is exact enough to evaluate every required assurance property for that execution. |
| `RELAY_GOVERNANCE_PROFILE_BOUND` | The exact governed subject is bound, **before the governed action**, to the exact GovernanceProfile and policy basis required for that action. Unknown applicability is `UNKNOWN` and cannot silently permit the action. |
| `RELAY_VERIFICATION_ASSETS_PROTECTED` | All profile-designated verification-critical assets were outside unauthorized implementer mutation authority, or every permitted mutation had the separately required authorization and governance. Unknown classification or mutation authority is `UNKNOWN`. |

## 6. Actors, trust, and execution provenance — D17–D18, D36–D38, D47–D48

Trust is claim-specific: it depends on claim type, subject, policy, role, issuer, required separation, authority basis, and evidence origin. There is no global trusted/untrusted actor flag. Conceptual roles include Human Authority, architect/designer, implementer, evaluator, mechanical promotion executor, external verifier, agent runtime, and system.

```text
role != identity != authority
IMPLEMENTER != EVALUATOR by default
DESIGNER != EVALUATOR is not an automatic requirement
```

The established operating model permits Sol to design and evaluate, Codex/Luna to implement bounded authorized work, and the Human to grant authority and acceptance. Stronger separation—separate designer/evaluator, trusted human reviewers, organizational separation, external verification, or signer separation—must be explicit in the applicable policy. One physical actor may hold multiple roles only where policy permits; role overlap does not imply authority overlap.

A prompt saying “evaluator,” model saying “Sol,” request field saying “Human,” runtime saying “implementer,” or branch owner name does not independently bind policy-required actor identity. The binding mechanism belongs to downstream design; it is not frozen here [SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026] [SRC-PAIE-AGENT-IDENTITY-PLATFORM-2026].

Execution provenance sufficiency is policy/risk-relative, not universal full-trajectory logging. Low-risk documentation may require exact commit, changed-file set, registry transition, and CI. Higher-risk autonomous work may additionally require execution/workspace identity, runtime/provider/model, tool activity, permission events, network policy, credential scope, tests/evals, event continuity/gaps, and terminal result. Correct output does not prove a valid governed trajectory [SRC-GOOGLE-NEW-SDLC-2026].

Closed Slice 2.1 runtime observations—adapter/runtime/API generation, requested and observed model/provider, session identity, event gaps, terminal result—are evidence inputs only. Runtime success is not engineering evaluation or acceptance. Timestamps alone do not establish causal control continuity; exact record references must link authority, subject, execution, evidence, evaluation, required Human acceptance, eligibility, authority, promotion, and promotion evidence.

## 7. Human Decision Support and applicability — D43–D46, D60

Decision Support is **cross-cutting, derived, and non-authoritative**. The same projection pattern applies before design, before execution, and after evaluation, using only policy-applicable inputs:

```text
CANONICAL GOVERNED STATE
  intent / policy / design / applicable evidence / prior authority
  applicable evaluation / risks / unknowns / consequences
                         |
                         v
DECISION BASIS PROJECTION — NON-AUTHORITATIVE
                         |
                         v
PENDING HUMAN DECISION
                         |
                         v
HUMAN AUTHORITY ACT
                         |
                         v
GOVERNED STATE TRANSITION
```

```text
Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Authority
Decision Support != Executed Transition
```

A conceptual `DecisionBasisProjection` binds one exact decision and governed subject. It can contain current state, proposed transition, decision type and reason, authority/policy/design basis, change/non-change summaries, applicable evidence/evaluation, required properties, risks, unknowns, blocking findings, consequences of approval/rejection/deferral, explicit non-authority, sources, and freshness. Components are policy-specific, not universally required.

| Applicability state | Meaning |
|---|---|
| `REQUIRED_PRESENT` | Applicable policy requires the component and the basis contains it; currency and exactness must also hold for completeness. |
| `OPTIONAL_PRESENT` | The component is present but not required by the applicable decision policy. |
| `NOT_APPLICABLE` | Policy deterministically or explicitly establishes that the component does not apply. |
| `UNKNOWN` | Applicability or applicable basis cannot be established. |
| `MISSING_REQUIRED` | Policy requires the component and it cannot be located/provided. |

Pre-design opening with no implementation evaluation requirement is `NOT_APPLICABLE`, not `UNKNOWN`. Technical acceptance with required evaluation absent is `MISSING_REQUIRED`, not `NOT_APPLICABLE`. Unresolved policy applicability is `UNKNOWN`. Presence alone cannot pass completeness if the basis is stale or for another subject.

`RELAY_DECISION_BASIS_COMPLETE` verifies that Relay supplied required current decision material, not that a Human understood, agreed, or will decide correctly. No Human-understanding property or equivalent cognition certification is introduced.

A Human should be able to understand, question, inspect, compare, defer, and decide. Optional `DecisionClarityFeedback` may be self-reported, for example a labelled five-point scale; it is not authority, evaluation, or objective evidence of understanding. Low clarity may improve explanation or invite questions/deferral without automatically invalidating or manufacturing authority [SRC-LITT-UNDERSTANDING-2026] [SRC-GOOGLE-NEW-SDLC-2026].

Future Slice 1.9 Decision Cards/Q&A explain the selected profile/version, why it applies, risk/impact basis, Human decisions, evidence, separation, protected assets, mutation permissions, promotion predicates, and unknowns. They may explain permitted escalation/downgrade but cannot select or relax the profile. [Human Decision Support](HUMAN_DECISION_SUPPORT.md) describes that future interface; none is implemented here.

## 8. GovernanceProfile and prospective authority — D53–D56, RW1-D04

`GovernanceProfile` is a conceptual, policy-bound description of the minimum sufficient governance requirements for exact work. It can specify profile identity/version, policy basis, required Human gates, evidence, evaluator independence, execution isolation/provenance, protected verification requirements, tests/evals, runtime identity, promotion predicates, canonical-reference controls, and escalation triggers.

Potential policy inputs include change category, blast radius, reversibility, production/data/security/privacy impact, destructive potential, schema/migration impact, credentials, network access, external side effects, agent autonomy, workspace capability, novelty/uncertainty, and rollback availability. Policy owns required inputs and classification logic. `LOW`, `STANDARD`, `HIGH`, and `CRITICAL` are examples only, not canonical values. No taxonomy, scoring formula, enum, policy engine, table, object, or UI is implemented.

```text
implementer cannot self-downgrade governance
runtime capability cannot self-downgrade governance
agent assertion cannot self-downgrade governance
workflow-provider metadata cannot self-downgrade governance
```

Profile selection comes from Relay policy and/or explicit Human Authority. Unknown required classification inputs fail closed or escalate under policy. Policy or authorized escalation may select stricter controls. A downgrade requires policy-authorized downgrade or explicit Human Authority **and a durable record** [SRC-PAIE-HANDBOOK-2026] [SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026].

Profile changes are **prospective**. A valid, recorded downgrade can govern a separately governed future action. It cannot convert an already-executed action with missing/wrong/unknown profile, authority, evidence, or controls into conformant execution. Historical actions remain judged under the policy/profile applicable when they occurred. Later escalation likewise governs future or explicitly restarted work rather than rewriting history.

```text
later downgrade != retroactive authorization
execute first -> downgrade later -> claim compliance is invalid
```

## 9. Protected Verification Assets — D57–D58, RW1-D02

Protected Verification Assets are defined by **mutation authority, not secrecy**. Applicable policy/profile may designate acceptance criteria, evaluation fixtures, golden datasets, acceptance tests, security checks, policy rules, verification scripts, expected invariants, or external-validation configuration as protected.

Implementation tests may legitimately be implementer-authored/writable where policy permits. Policy/acceptance/evaluation assets may require read-only or no implementer access, separate mutation authority, or evaluator review as a prerequisite. Not every test is protected; neither immutability nor hidden tests are universal requirements [SRC-CONSORT-PAPER-2026] [SRC-CONSORT-IMPLEMENTATION-2026].

```text
evaluator review != mutation authority
evaluation outcome != mutation authority
```

Actual mutation permission comes from an explicit authority/capability recognized by applicable policy. An evaluator's ACCEPT/PASS/recommendation may be a policy prerequisite; the evaluator role alone never confers mutation authority. If one physical actor evaluates and approves asset mutation, both roles/capabilities must be explicit. Evaluation cannot manufacture authority.

Unknown required asset classification or mutation authority yields `UNKNOWN`, not implicit `PASS`. An implementer may not weaken a protected acceptance test simply to obtain passing output. Asset designation is documented here; no filesystem/tool enforcement is implemented.

## 10. Workflow-neutral intent and effective context — D51–D52, D61

Upstream intent may originate in Relay-native planning, Spec Kit, OpenSpec, BMAD, enterprise workflows, custom processes, or future systems [SRC-GITHUB-SPEC-KIT-2026] [SRC-OPENSPEC-2026] [SRC-BMAD-METHOD-2026].

```text
upstream approved != Relay authorization
upstream ready != Relay authorization
upstream done != Relay acceptance
upstream green != Relay evaluation ACCEPT
```

Future Slice 2.3 may define `PlanningArtifactSourceRef` (source/version, artifact identity/digest, provenance), `PlanningArtifactAdapter` (version and normalization contract), and `NormalizedEngineeringIntent`. Intent may carry objective, problem, source-supported acceptance criteria, design references, work identity, proposed scope, explicit non-scope, quality/verification expectations, dependencies, and provenance.

Normalization cannot manufacture authority, scope, acceptance criteria, or non-scope unsupported by inputs. Missing required normalization is `UNKNOWN` or `MISSING_REQUIRED`, which prevents an authorized Work Packet. Normalized intent is not an authorized Work Packet: Relay must bind exact inputs through its own policy and valid authority before execution. No adapters or packet implementation are introduced.

Future `ContextManifest` separates:

| Static context | Dynamic context |
|---|---|
| Role contract, repository/system rules, architecture, accepted design, authority/non-authority, guardrails, stable conventions | Retrieved artifacts, skills/version, tool definitions, selected code, runtime observations, external references, bounded session context |

`prompt text != effective governed context`. Applicable policy requires enough provenance/version/digest information to identify effective context [SRC-GOOGLE-NEW-SDLC-2026]. No ContextManifest implementation is authorized here.

## 11. Promotion, history, and integrity — D10, D29–D32, D37–D38, RW1-D01

Valid promotion authority may be a dedicated exact authorization or a pre-issued exact finalization/closure authority whose conditions explicitly permit promotion when stated predicates are met. Checking authority at execution time does not mean it must be issued at that time.

```text
No valid promotion authority -> promotion forbidden
Valid authority + all required predicates satisfied
    -> mechanical promotion may proceed without another Human decision
```

The executor performs an already-authorized operation, never a discretionary promotion decision. It must use the exact candidate, applicable policy, current authority, required exact/current CI and evaluation, required Human acceptance, current canonical parent, and other policy-required evidence/properties. Successful execution does not prove it was authorized. Permission to write a repository is not implementation or promotion authority.

Current applicability is derived from exact subject, latest valid chain, exact policy, evidence/authority freshness, supersession, and canonical parent freshness where applicable. Records remain append-only. A new judgment may supersede an old one without rewriting it. A historical PASS is not current authorization.

Missing subject digests, conflicting current judgments, unknown supersession, stale parents, missing authority, evidence for another commit, unresolved framework versions, ambiguous issuers, and unverifiable policy digests yield `UNKNOWN` or integrity errors rather than PASS when truth cannot be established. A positively established violated requirement is FAIL. Promotion-critical ambiguity blocks promotion.

Canonical Git/repository governance remains the substrate. Slice 1.10 owns protected canonical references, required CI/status policy, stale-parent enforcement, promotion predicates, a trusted mechanical executor, promotion evidence, and break-glass policy. Slice 1.9 owns Decision Support, not source/promotion enforcement. No repository settings or executor are changed here.

## 12. External assurance, mapping, and freshness — D19–D28, D49, D65, RW1-D03

Mappings are many-to-many: an exact external requirement can use multiple Relay controls, and a Relay control can contribute to multiple requirements. External requirements determine the meaning and evidence of an external claim; they cannot redefine Relay authority. Source metadata below refers to the catalogued snapshot, not a new live assessment.

Conceptual `ExternalRequirementRef` contains framework ID, framework version, publication status, requirement ID, and authoritative source reference. `ComplianceMapping` contains the external requirement, Relay control/property references, required evidence, assessment status, rationale, assessor, `verified_at`, and `review_due_at` and/or refresh trigger. Exact schemas remain deferred.

| Assessment status | Meaning |
|---|---|
| `UNASSESSED` | No requirement-level assessment has been made. |
| `MAPPED` | Semantic correspondence is identified; satisfaction is not established. |
| `PARTIALLY_SATISFIED` | Evidence establishes only part of the pinned requirement. |
| `SATISFIED` | Exact evidence required by the pinned requirement establishes satisfaction. |
| `NOT_SATISFIED` | Assessment establishes that the requirement is not met. |
| `NOT_APPLICABLE` | Inapplicability has an explicit rationale. |
| `UNKNOWN` | Evidence or interpretation is insufficient. |

Freshness is distinct from assessment status. A mapping outside its accepted freshness window becomes `STALE`; for a new external claim, `STALE -> UNKNOWN until reverified`. Stale is not automatically FAIL, and never current PASS for a new claim. Historical claims keep their original basis; a newer framework cannot silently reinterpret them.

The source catalog pins SLSA v1.2 as Approved; SSDF 1.1/SP 800-218 as Final; SSDF 1.2/SP 800-218 Rev. 1 as Draft; and SP 800-218A as Final. The draft is not a final compliance baseline. DORA remains flow-health guidance, not a compliance level [SRC-SLSA-V1_2] [SRC-NIST-SSDF-1_1] [SRC-NIST-SSDF-1_2-DRAFT] [SRC-NIST-SP800-218A] [SRC-DORA-CHANGE-APPROVAL].

SLSA Source/Build provenance and Verification Summary Attestations may supply evidence under their exact semantics. Relay-native properties must not be presented as SLSA properties or inserted into SLSA fields without format permission and valid semantics. External VSA PASS creates neither Human acceptance nor promotion authority. SLSA's two-trusted-person requirement is not met by Sol review or Sol/Luna model/session separation; no adapter may translate Relay AI separation into `SLSA_SOURCE_TWO_PARTY_REVIEWED` [SRC-SLSA-VERIFIED-PROPERTIES] [SRC-SLSA-SOURCE-REQUIREMENTS].

SSDF practice mapping does not define Relay lifecycle, evaluation, acceptance, or projection rules. SP 800-218A may inform later AI-development controls without adopting or implementing them here. A matrix does not imply certification, SLSA Source/Build levels, full SSDF conformance, or an external audit result. Such claims require the external framework's exact evidence and any required auditor/certification authority. Counting satisfied rows is insufficient.

Practitioner, research, and product references—including Google, Geoffrey Litt, the Principal AI Engineer Handbook, Spec Kit, OpenSpec, BMAD, Consort, GitLab, and OpenAI examples—are design inputs, not compliance frameworks or proof of Relay outcomes. The [matrix and traceability table](../references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md) separate these categories. No competitive superiority claim or experiment is produced.

## 13. Human-gate necessity and telemetry — D24–D25, D50, D59

A Human gate exists only when a distinct discretionary authority decision is required. Hashes/digests, CI, registry/schema validity, parent freshness, required evidence presence, and property evaluability are mechanical candidates. “May work begin?”, “Is this design acceptable?”, “May implementation proceed?”, “Is this exact result accepted?”, “May it become canonical?”, and “Is this exception allowed?” protect distinct Human decisions.

Reduce duplicate ceremony, not authority. Machine-checkable facts should not require repeated Human approval without a separate authority reason. DORA informs peer/independent review close to the change, automation, early feedback, and risk-sensitive scrutiny rather than unrelated heavyweight approval boards [SRC-DORA-CHANGE-APPROVAL]. Policy-gated reference designs inform separation of model requests from authorization [SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026].

`GovernanceEffectivenessTelemetry` is future, observational, and non-authoritative. Keep assurance value (blocked unauthorized operations, scope violations/defects detected, recovery) separate from governance cost (Human decision latency/interaction time, evaluation duration, Human/mechanical gate counts, rework, avoidable escalations, promotion latency, execution duration, token/monetary cost). Work completed without Human intervention, deterministic-check automation rates, and duplicate manual verification can inform observation without granting authority.

```text
telemetry != authority
telemetry != evaluation
low cost != permission to weaken controls
historical success != waiver of current policy
```

No composite governance score, collection, dashboard, or automatic policy relaxation is implemented. Any future automatic relaxation requires separately accepted policy and authority. The competitive validation plan remains non-authoritative research planning; the experiment has not been executed.

## 14. Downstream ownership and implementation limit — D33–D35, D39–D42, D62, D66–D69

| Slice | Ownership consuming this model |
|---|---|
| 1.8 | Assurance semantics, property definitions, exact subject/policy, profile and protected-asset semantics, mapping rules and examples |
| 1.9 | Human Decision Support & Governance Review Surface: Decision Cards, basis/profile/risk/asset explanation, scoped Q&A, clarity feedback, telemetry presentation |
| 1.10 | Canonical Source and Promotion Enforcement: canonical-reference protection, status policy, parent freshness, predicates, mechanical executor, promotion evidence, break-glass policy |
| 2.2 | Role Contracts: independently bound actor identity, policy-required separation, verification-asset read/create/modify/approve/evaluate permissions, provenance obligations |
| 2.3 | Context and Work-Packet Contract: authority/baseline/design/policy/role/property/evidence/hard-stop/result references, planning normalization, ContextManifest, exact profile and protected-asset references |
| 2.4 | Execution Workspace Authority: profile-selected filesystem/tool/network/credential boundaries, resource limits, environment identity, retention/teardown, protected-asset mutation enforcement and evidence |
| 3.1 | Governed coding-agent execution of an authorized packet under profile/workspace restrictions regardless of upstream planning method |

Downstream slices consume rather than redefine these semantics. Workspace capability never creates implementation authority. Phase 3.1 requires 1.8, 1.9, 1.10, 2.2, 2.3, 2.4, and explicit Phase 3 opening.

Slice 1.8 is **IMPLEMENTED / AWAITING INDEPENDENT IMPLEMENTATION EVALUATION** as documentation only. No production/runtime/test code, schema, dependency, workflow, repository setting, signing/attestation/compliance engine, profile engine, UI, adapter, ContextManifest, enforcement, telemetry collection, or agent execution is introduced. The candidate returns to Sol; implementation authorization is not implementation acceptance. Slices 1.9/1.10 remain unopened and Phase 3 unauthorized.
