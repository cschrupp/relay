# Slice 1.8 — Governance Assurance Reference Model — Design Revision 1

**Document class:** Lockable design record  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-10  
**Project:** Relay  
**Slice:** 1.8 — Governance Assurance Reference Model  
**Document revision:** 1  
**Opening authority:** RLY-S18-OPEN-001 — OPEN  
**Design authority:** RLY-S18-DESIGN-AUTH-001 — AUTHORIZED  
**Exact design subject baseline:** 986b67f00958ef348fbf69ff677af630009881a7  
**Implementation authorization:** NOT GRANTED

---

# 1. Objective

Define the minimum Relay-native governance-assurance reference model needed to make Relay's existing authority, provenance, evaluation, acceptance, and promotion semantics explicit, composable, externally mappable, and resistant to semantic drift.

This Slice does not make SLSA, NIST SSDF, DORA, or any other external framework Relay's domain model.

The controlling direction is:

~~~text
Relay native semantics
        |
        +--> Relay evidence / verification / authority / promotion model
        |
        +--> external representation / assurance / compliance mapping
                  |
                  +-- SLSA
                  +-- NIST SSDF
                  +-- DORA
                  +-- future standards / enterprise policy
~~~

The reverse direction is forbidden architecture.

---

# 2. Existing accepted substrate

Slice 1.8 reuses the accepted Relay foundation:

- exact repository and Baseline identity;
- append-only/immutable authority and evaluation records;
- deterministic lifecycle/gate semantics;
- Human Authority as root authority;
- explicit evaluator outcome distinct from Human acceptance;
- accepted-result promotion distinct from Human acceptance;
- exact SHA / registry / canonical-projection governance;
- fail-closed stale-basis handling;
- closed Slice 2.1 AgentRuntime boundary;
- established Sol/Luna operating model:
  - Sol = architect / designer / reviewer / governance gatekeeper;
  - Luna/Codex = implementation and bounded implementation-rework executor;
  - Human = root authority.

No second authority system, lifecycle, evaluator system, promotion system, or compliance engine is introduced by this design.

---

# 3. External reference snapshot affecting the design

The design is informed by the following external reference state as of 2026-10-10:

~~~text
SLSA:
Version 1.2
Status: Approved
Approved tracks: Source and Build
Approved attestation concepts: Provenance and Verification Summary Attestation
Approved Verified Properties include:
  SLSA_SOURCE_TWO_PARTY_REVIEWED
  SLSA_BUILD_REPRODUCED

NIST SSDF:
SP 800-218 / SSDF 1.1
Status: Final

NIST SSDF 1.2:
SP 800-218 Rev. 1
Status: Draft
May inform design but cannot be treated as the final compliance baseline.

NIST SP 800-218A:
Status: Final
AI/GenAI SSDF Community Profile
Informative for later AI-development control mapping.

DORA:
Change-approval guidance favors peer review plus automation,
early detection, and platform/toolchain controls over heavyweight
external approval boards.
~~~

External references are version-pinned inputs. A later framework revision cannot silently reinterpret an already-issued Relay claim.

---

# 4. S1.8-D01 — Relay owns semantic authority

Relay owns the meaning of:

~~~text
authorization
design acceptance
implementation authority
execution provenance
evaluation
Human technical acceptance
promotion eligibility
promotion authority
canonical promotion
control state
~~~

External frameworks may:

- validate applicable properties;
- provide assurance vocabulary;
- define external requirements;
- provide representation formats;
- constrain a particular external claim.

They may not:

- create Relay authority;
- rename a Relay lifecycle transition and thereby change its semantics;
- turn external evidence into Human acceptance;
- make an external level/property equivalent to Relay promotion authorization;
- reinterpret Relay's Human Authority model.

---

# 5. S1.8-D02 — Four non-substitutable assurance statement classes

Relay assurance statements are classified conceptually as:

~~~text
FACT / EVIDENCE
VERIFICATION JUDGMENT
AUTHORITY DECISION
EXECUTED TRANSITION / PROMOTION RECORD
~~~

These classes are non-substitutable.

## FACT / EVIDENCE

Describes observed or produced facts, for example:

~~~text
exact commit SHA
CI result
test result
runtime identity
provider/model identity
artifact digest
changed-file set
source-control protection state
external verifier output
~~~

## VERIFICATION JUDGMENT

Applies policy/reasoning to evidence, for example:

~~~text
design evaluation ACCEPT / REVISE / ESCALATE
implementation evaluation ACCEPT / REWORK / ESCALATE
verified property PASS / FAIL / UNKNOWN
scope-conformance judgment
promotion-eligibility judgment
~~~

## AUTHORITY DECISION

Represents explicit Human or previously granted Relay authority, for example:

~~~text
Slice opening
design authorization
design acceptance
implementation authorization
Human technical acceptance
promotion/finalization authorization
~~~

## EXECUTED TRANSITION / PROMOTION RECORD

Records that an already-authorized operation actually occurred, for example:

~~~text
canonical fast-forward performed
accepted baseline established
canonical pointer advanced
promotion attestation emitted
~~~

Normative invariant:

~~~text
evidence cannot become evaluation by implication
evaluation cannot become authority by implication
authority cannot prove execution occurred
execution cannot manufacture authority
~~~

---

# 6. S1.8-D03 — Reference-plane architecture

Relay's assurance architecture is:

~~~text
                         RELAY
                           |
      +--------------------+--------------------+
      |                    |                    |
      v                    v                    v
CONTROL / GOVERNANCE    EXECUTION          EVIDENCE / PROVENANCE
      |                    |                    |
Human Authority         Role execution      CI/test facts
lifecycle policy        AgentRuntime         runtime facts
authorization           workspace/tool use  artifact facts
acceptance              bounded mutation    source-control facts
promotion authority                          external facts
      |                    |                    |
      +--------------------+--------------------+
                           |
                           v
                     VERIFICATION
                           |
              +------------+------------+
              |                         |
              v                         v
       Relay evaluation          External conformance
       Relay property check      verification/mapping
              |                         |
              +------------+------------+
                           |
                           v
                    HUMAN ACCEPTANCE
                           |
                           v
                  PROMOTION ELIGIBILITY
                           |
                           v
               VALID PROMOTION AUTHORITY
                           |
                           v
                MECHANICAL PROMOTION
                           |
                           v
             PROMOTION EVIDENCE / ATTESTATION
~~~

Human acceptance is a Control/Governance act but is displayed after verification to preserve lifecycle causality.

---

# 7. S1.8-D04 — Exact assurance subject identity

Every assurance statement MUST identify an exact subject.

Conceptual subject reference:

~~~text
AssuranceSubjectRef(
    project_id,
    subject_kind,
    slice_id | None,
    repository_id | None,
    git_commit | None,
    artifact_id | None,
    content_digest | None,
    execution_id | None,
    evaluation_id | None,
    authority_record_id | None,
)
~~~

Rules:

- subject_kind determines which identity fields are mandatory;
- exact immutable identifiers are authoritative;
- moving branch names are navigation only;
- human-readable URIs may assist investigation but never replace exact digest/revision identity;
- ambiguous or partially resolved subjects cannot satisfy promotion-critical properties;
- a statement about one exact subject cannot be reused for a successor subject without explicit re-verification.

---

# 8. S1.8-D05 — Policy basis is part of every verification claim

Every verification judgment binds to an exact policy basis.

Conceptual reference:

~~~text
PolicyBasis(
    policy_id,
    policy_version,
    policy_digest,
    effective_scope,
)
~~~

A verification result is not timeless truth.

If policy semantics change incompatibly:

~~~text
old verification
    !=
verification under new policy
~~~

Consumers must not silently reinterpret an old judgment using a newer policy.

---

# 9. S1.8-D06 — Evidence references are immutable inputs, not current truth

A verification judgment references exact evidence identities.

Conceptual shape:

~~~text
EvidenceRef(
    evidence_type,
    evidence_id,
    subject,
    content_digest,
    producer,
    observed_at,
)
~~~

Evidence may later be superseded or contradicted, but historical evidence is never rewritten.

Current applicability is derived from:

~~~text
exact subject
+ exact policy basis
+ evidence freshness rules
+ current authority basis
~~~

---

# 10. S1.8-D07 — Verification judgment contract

A Relay-native verification judgment conceptually contains:

~~~text
VerificationJudgment(
    judgment_id,
    judgment_type,
    subject,
    policy_basis,
    evaluator,
    evidence_refs,
    outcome,
    findings,
    issued_at,
    supersedes | None,
)
~~~

Allowed generic property outcomes:

~~~text
PASS
FAIL
UNKNOWN
~~~

Context-specific design/implementation evaluation outcomes remain their accepted domain vocabulary, for example:

~~~text
ACCEPT
REVISE / REWORK
ESCALATE
~~~

A property PASS is not an evaluation ACCEPT.

An evaluation ACCEPT is not Human acceptance.

---

# 11. S1.8-D08 — Authority records remain first-class and separate

Authority records conceptually contain:

~~~text
AuthorityDecision(
    authority_id,
    authority_type,
    subject,
    authority_actor,
    authority_basis,
    granted_scope,
    explicit_non_authority,
    conditions,
    issued_at,
)
~~~

Authority is not inferred from:

- role name;
- model identity;
- branch ownership;
- successful CI;
- evaluator outcome;
- runtime capability;
- external compliance result.

An attestation representation of an authority record mirrors existing authority. It does not create authority.

---

# 12. S1.8-D09 — Promotion eligibility is derived verification state

Promotion eligibility is NOT authority.

Conceptually:

~~~text
PromotionEligibility(
    subject,
    policy_basis,
    required_properties,
    property_results,
    evaluator_state,
    human_acceptance_state,
    parent_freshness_state,
    result = ELIGIBLE | INELIGIBLE | UNKNOWN,
)
~~~

Eligibility may become ELIGIBLE only when every required predicate is satisfied exactly.

Eligibility becoming ELIGIBLE does not itself authorize promotion.

---

# 13. S1.8-D10 — Promotion authority supports dedicated or pre-issued conditional authority

Valid promotion authority may be:

1. a dedicated exact promotion authorization; or
2. an earlier exact finalization/closure authority whose conditions explicitly authorize promotion once specified predicates are satisfied.

Normative rule:

~~~text
No valid promotion authority:
promotion forbidden.

Valid promotion authority + all required predicates satisfied:
mechanical promotion may proceed without another Human decision.
~~~

The promotion executor performs an already-authorized operation.

It is not a decision maker.

---

# 14. S1.8-D11 — Relay-native attestation family is logical, not yet a wire-format implementation

The following logical predicate identifiers are accepted as the initial Relay-native family:

~~~text
relay.dev/design-evaluation/v1
relay.dev/design-acceptance/v1
relay.dev/implementation-authorization/v1
relay.dev/execution-provenance/v1
relay.dev/evaluation/v1
relay.dev/human-acceptance/v1
relay.dev/promotion-authorization/v1
relay.dev/promotion/v1
relay.dev/control-state/v1
~~~

These are logical predicate identities.

Slice 1.8 does NOT freeze:

- JSON schema;
- signing format;
- transport;
- storage backend;
- signature algorithm;
- in-toto envelope adoption;
- Rekor/transparency-log integration.

A future attestation implementation may serialize Relay-native predicates through an in-toto-compatible envelope if that faithfully preserves Relay semantics.

---

# 15. S1.8-D12 — Common predicate semantics

Every future Relay-native predicate must be able to represent, directly or by exact reference:

~~~text
predicate identity + major version
exact subject
issuer / actor identity
issued_at
policy basis where applicable
authority basis where applicable
evidence references where applicable
outcome / decision
supersession relation
content digest / canonical representation
~~~

A predicate type may omit fields that are semantically inapplicable, but it may not collapse evidence, evaluation, and authority into one ambiguous claim.

---

# 16. S1.8-D13 — Predicate and property versioning

Compatibility policy:

~~~text
same major version:
  semantic meaning remains compatible

additive optional fields:
  allowed without changing major predicate identity

incompatible field requirement:
  new major version

incompatible semantic meaning:
  new predicate/property identity or major version

external-framework mapping:
  always pinned to exact framework version/status
~~~

A verified-property name is semantically immutable once accepted.

If meaning changes materially, create a new property name/version rather than redefining the old one.

---

# 17. S1.8-D14 — Initial Relay-native verified-property vocabulary

The initial property vocabulary is:

~~~text
RELAY_EXACT_AUTHORIZED_BASELINE
RELAY_EVIDENCE_SUBJECT_EXACT
RELAY_IMPLEMENTER_EVALUATOR_SEPARATION
RELAY_SCOPE_CONFORMANCE
RELAY_INDEPENDENT_EVALUATION
RELAY_HUMAN_ACCEPTED
RELAY_PROMOTION_AUTHORIZED
RELAY_CANONICAL_PARENT_CURRENT
RELAY_FAIL_CLOSED
RELAY_RUNTIME_IDENTITY_RECORDED
RELAY_CONTROL_CONTINUITY_VERIFIED
RELAY_CANONICAL_PROJECTION_LINEAGE_VALID
~~~

These are Relay-native properties.

They are not SLSA properties and must not be emitted as if they were standardized SLSA Verified Properties.

---

# 18. S1.8-D15 — Property definitions

## RELAY_EXACT_AUTHORIZED_BASELINE

PASS only when the exact execution/design/evaluation subject is bound to the exact baseline authorized by the governing authority record.

## RELAY_EVIDENCE_SUBJECT_EXACT

PASS only when all required evidence binds to the exact evaluated subject; stale or successor-subject evidence does not pass.

## RELAY_IMPLEMENTER_EVALUATOR_SEPARATION

PASS only when the implementation execution actor/session required by policy is distinct from the evaluator actor/session required by policy.

## RELAY_SCOPE_CONFORMANCE

PASS only when observed changes and behavior remain inside authorized scope and do not exercise explicit non-authority.

## RELAY_INDEPENDENT_EVALUATION

PASS only when the governing policy's evaluator-separation requirements are met and an exact-subject evaluation exists.

## RELAY_HUMAN_ACCEPTED

PASS only when an explicit Human acceptance authority record is bound to the exact accepted subject.

## RELAY_PROMOTION_AUTHORIZED

PASS only when exact valid promotion authority exists and is current for the subject.

## RELAY_CANONICAL_PARENT_CURRENT

PASS only when the expected canonical parent/ref basis remains current at promotion time.

## RELAY_FAIL_CLOSED

PASS only when unresolved required state, stale basis, missing evidence, or integrity ambiguity prevents rather than permits the governed transition.

## RELAY_RUNTIME_IDENTITY_RECORDED

PASS only when the runtime/provider/model provenance required by the applicable execution policy is recorded to the required completeness.

## RELAY_CONTROL_CONTINUITY_VERIFIED

PASS only when the causal chain from authority through execution/evaluation/acceptance to the proposed transition remains reconstructable without an authority gap.

## RELAY_CANONICAL_PROJECTION_LINEAGE_VALID

PASS only when living canonical projections advance according to repository-contract lineage rules without skipped incompatible revisions or history reconstruction.

---

# 19. S1.8-D16 — Property evaluation is three-valued

Property result vocabulary:

~~~text
PASS
FAIL
UNKNOWN
~~~

UNKNOWN is required for cases where truth cannot be established from available evidence.

UNKNOWN is never silently coerced to PASS.

For a promotion-critical required property:

~~~text
UNKNOWN => not eligible
FAIL    => not eligible
PASS    => predicate satisfied
~~~

This gives Relay conservative fail-closed semantics without incorrectly asserting failure where evidence is merely unavailable.

---

# 20. S1.8-D17 — Trust is claim-specific, not global

Relay does not use a single global boolean trusted/untrusted actor model.

Trust is evaluated relative to:

~~~text
claim type
subject
policy
role
issuer
required separation
authority basis
evidence origin
~~~

Conceptual actor roles include:

~~~text
HUMAN_AUTHORITY
ARCHITECT_DESIGNER
IMPLEMENTER
EVALUATOR
MECHANICAL_PROMOTION_EXECUTOR
EXTERNAL_VERIFIER
AGENT_RUNTIME
SYSTEM
~~~

One physical person/model/process may hold multiple roles only where the governing policy permits it.

Role overlap never implies authority overlap.

---

# 21. S1.8-D18 — Default evaluator independence under the Sol/Luna operating model

The default Relay project rule is:

~~~text
IMPLEMENTER != EVALUATOR
~~~

The default does not require:

~~~text
DESIGNER != EVALUATOR
~~~

Therefore:

~~~text
Sol:
  may architect/design
  may review/evaluate

Luna/Codex:
  implements authorized production work

Human:
  grants authority / acceptance
~~~

A future Slice may impose stronger separation, including:

- designer != evaluator;
- multiple trusted human reviewers;
- organizational separation;
- external verifier;
- cryptographic signer separation.

Such stronger requirements must be explicit in that Slice's governing authority/policy.

---

# 22. S1.8-D19 — SLSA mapping is one-way and requirement-specific

SLSA v1.2 mapping rule:

~~~text
SLSA requirement/property
        ↓
applicable Relay control(s)
        ↓
required Relay/external evidence
        ↓
mapping assessment
~~~

Never:

~~~text
SLSA concept
        ↓
redefinition of Relay lifecycle/authority
~~~

Relevant SLSA domains include:

- Source Track source revision identity and source-management controls;
- Source provenance / Source VSA concepts;
- Build Track provenance and builder controls;
- Verification Summary Attestation concepts;
- SLSA-defined Verified Properties.

Relay promotion policy may consume valid SLSA evidence.

SLSA does not define Relay promotion semantics.

---

# 23. S1.8-D20 — SLSA two-party review must never be inferred from Relay AI review

The SLSA Verified Property:

~~~text
SLSA_SOURCE_TWO_PARTY_REVIEWED
~~~

has SLSA-defined semantics requiring two trusted persons under the Source Track requirements.

Therefore:

~~~text
Sol design review
    !=
SLSA_SOURCE_TWO_PARTY_REVIEWED

Sol implementation review
    !=
SLSA_SOURCE_TWO_PARTY_REVIEWED

Sol + Luna model separation
    !=
SLSA_SOURCE_TWO_PARTY_REVIEWED
~~~

Relay may truthfully assert its own:

~~~text
RELAY_IMPLEMENTER_EVALUATOR_SEPARATION
RELAY_INDEPENDENT_EVALUATION
~~~

when their Relay-native requirements are met.

No adapter may translate those properties into the SLSA two-party-reviewed property.

---

# 24. S1.8-D21 — SLSA VSA/provenance reuse is allowed only for faithful external claims

If a future Relay integration produces or consumes SLSA provenance/VSA:

- the external artifact must retain its exact SLSA predicate semantics;
- Relay may reference it as evidence;
- Relay may map its result to applicable Relay controls;
- Relay-native properties must not be inserted into SLSA-defined fields unless the SLSA format explicitly permits and the semantics are valid;
- external VSA PASS does not create Human acceptance or promotion authority.

---

# 25. S1.8-D22 — NIST SSDF is a control catalogue / practice mapping, not workflow authority

Current final baseline:

~~~text
NIST SP 800-218
SSDF Version 1.1
FINAL
~~~

Relay maps applicable SSDF practices/tasks onto Relay controls and evidence.

NIST SSDF does not define:

- Relay Slice lifecycle;
- evaluator outcomes;
- Human acceptance semantics;
- promotion authorization;
- canonical projection rules.

NIST SSDF 1.2 draft may be tracked as informative/draft only until finalized.

A mapping record must include exact version and publication status.

---

# 26. S1.8-D23 — AI-specific SSDF profile is informative until explicitly adopted

NIST SP 800-218A is final and relevant to AI-model/system development.

Relay may later map applicable 800-218A practices to:

- model/provider selection governance;
- AI-generated software risks;
- agent execution controls;
- model provenance;
- testing/evaluation expectations.

Slice 1.8 does not claim 800-218A compliance and does not create new AI-security implementation controls.

---

# 27. S1.8-D24 — DORA is a flow-health guardrail, not a compliance level

DORA guidance is used to prevent Relay governance from degenerating into heavyweight manual ceremony.

Design principles:

~~~text
each manual gate must protect a distinct authority decision

deterministic checks should be automated where practical

machine-verifiable evidence should not be manually re-approved without a separate authority reason

peer/independent review should happen close to the change

higher-risk changes may justify stronger scrutiny

routine low-risk work should not require an unrelated external approval board

approval latency and duplicated gates are governance-health signals
~~~

DORA does not override a Relay Human gate that protects a distinct authority transition.

---

# 28. S1.8-D25 — Governance-overhead budget concept

Future Relay observability may measure:

~~~text
manual authority gates per change
time waiting for Human authority
time waiting for independent evaluation
percentage of deterministic checks automated
duplicate manual verification count
rework-cycle count
promotion latency after all predicates satisfied
~~~

These are health metrics, not authorization inputs by default.

Slice 1.8 defines the principle only; implementation is out of scope.

---

# 29. S1.8-D26 — External mapping record

Conceptual external mapping:

~~~text
ExternalRequirementRef(
    framework_id,
    framework_version,
    publication_status,
    requirement_id,
)

ComplianceMapping(
    external_requirement,
    relay_control_refs,
    required_evidence_types,
    assessment_status,
    rationale,
    assessed_at,
    assessor,
)
~~~

The mapping is many-to-many.

One external requirement may map to multiple Relay controls.

One Relay control may contribute to multiple external requirements.

---

# 30. S1.8-D27 — Requirement-level mapping status vocabulary

Requirement-level assessment status:

~~~text
UNASSESSED
MAPPED
PARTIALLY_SATISFIED
SATISFIED
NOT_SATISFIED
NOT_APPLICABLE
UNKNOWN
~~~

Rules:

- MAPPED means a semantic mapping exists, not that the requirement is satisfied;
- SATISFIED requires the exact evidence required by the pinned external requirement;
- UNKNOWN means the evidence/interpretation is insufficient;
- NOT_APPLICABLE requires rationale;
- framework-level compliant/certified claims are not derived merely by counting SATISFIED rows.

---

# 31. S1.8-D28 — Conservative framework-level claim policy

Relay may describe:

~~~text
mapped controls
available evidence
requirement-level assessment
unassessed requirements
known gaps
not-applicable rationale
~~~

Relay must not claim:

~~~text
certified
compliant
SLSA Source/Build level achieved
SSDF fully conformant
external audit passed
~~~

unless the exact external framework's requirements and verification basis for that claim have actually been satisfied.

Where external certification or auditor authority is required, Relay may record that external result but cannot self-create it.

---

# 32. S1.8-D29 — Current truth is derived; history is immutable

Assurance records are append-only.

A new judgment may supersede an old judgment but never rewrites it.

Current applicability is derived from:

~~~text
exact subject
latest valid chain
exact policy version
evidence freshness
authority freshness
supersession relation
canonical parent freshness where applicable
~~~

A stale PASS remains historical evidence but is not current authorization.

---

# 33. S1.8-D30 — Integrity ambiguity fails closed

Examples that yield UNKNOWN or integrity error rather than PASS:

~~~text
missing subject digest
multiple conflicting current judgments
unknown supersession chain
stale canonical parent
missing authority basis
evidence from different commit
unresolvable external framework version
ambiguous issuer identity
unverifiable policy digest
~~~

Promotion-critical ambiguity blocks promotion.

---

# 34. S1.8-D31 — Cryptographic signing is not required by Slice 1.8

Slice 1.8 does not mandate:

- signed attestations;
- key infrastructure;
- Sigstore;
- transparency logs;
- hardware roots of trust.

The reference model must remain compatible with future authenticated attestations.

Current canonical Git/repository governance remains the authority substrate until separately hardened under Slice 1.9 and future implementation.

---

# 35. S1.8-D32 — Source-control enforcement belongs to Slice 1.9

Slice 1.8 defines the properties and semantics that Slice 1.9 should enforce, including:

~~~text
exact canonical parent
source revision identity
required CI freshness
promotion eligibility
valid promotion authority
mechanical executor boundary
promotion evidence
fail-closed stale-parent behavior
~~~

Slice 1.8 does not change GitHub settings.

---

# 36. S1.8-D33 — Role Contracts consume actor/trust semantics

Slice 2.2 Role Contracts should consume:

~~~text
role identity
allowed/prohibited actions
issuer/actor identity
evidence obligations
implementer/evaluator separation
Human Authority separation
runtime/provider/model provenance obligations
verified-property obligations
escalation conditions
~~~

Slice 2.2 must not redefine Slice 1.8 property semantics.

---

# 37. S1.8-D34 — Work Packets consume exact assurance basis

Slice 2.3 Context and Work-Packet Contract should be able to carry exact references to:

~~~text
authority record
authorized baseline
accepted design
role contract
required verified properties
evidence obligations
policy basis
hard stops
expected result contract
~~~

A work packet is not itself authority unless it references valid authority.

---

# 38. S1.8-D35 — Workspace Authority contributes evidence, not higher-order authority

Slice 2.4 Execution Workspace Authority should produce evidence for properties such as:

~~~text
workspace identity
filesystem scope
network policy
credential scope
resource limits
environment provenance
teardown/retention
~~~

Workspace enforcement may support RELAY_SCOPE_CONFORMANCE and RELAY_FAIL_CLOSED.

Workspace capability never creates implementation authority.

---

# 39. S1.8-D36 — AgentRuntime provenance maps into assurance evidence

Closed Slice 2.1 provides runtime observations such as:

~~~text
runtime identity
adapter/runtime/API generation
requested provider/model
actual provider/model when available
execution/session identity
event continuity/gaps
terminal runtime result
~~~

These are evidence inputs.

Runtime success remains distinct from engineering evaluation and acceptance.

---

# 40. S1.8-D37 — Control continuity is causal, not merely chronological

A valid governed chain must be reconstructable as:

~~~text
Human / governing authority
        ↓
exact authorized subject/baseline
        ↓
authorized execution/design action
        ↓
evidence/provenance
        ↓
independent evaluation
        ↓
Human acceptance where required
        ↓
promotion eligibility
        ↓
valid promotion authority
        ↓
mechanical promotion
        ↓
promotion evidence
~~~

A sequence of timestamps alone does not prove continuity.

Exact record references and subject identity are required.

---

# 41. S1.8-D38 — No authority laundering through adapters

Forbidden patterns include:

~~~text
external PASS -> Relay Human acceptance

CI green -> evaluation ACCEPT

runtime success -> implementation accepted

SLSA VSA -> promotion authorized

role says evaluator -> evaluator independence automatically satisfied

branch owner -> source authority

repository write permission -> implementation authority
~~~

Adapters may translate representation, never authority.

---

# 42. S1.8-D39 — Expected Slice 1.8 implementation surface is documentation-first

If this design is accepted and implementation is later authorized, the expected minimum Slice 1.8 implementation is documentation/governance-model hardening, not runtime code.

Expected bounded surface:

~~~text
docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
narrow supporting policy/mapping documentation only if required
registry / canonical documentation updates required by governance
~~~

Expected:

~~~text
production source changes: NONE
runtime dependency changes: NONE
schema migration: NONE
GitHub settings mutation: NONE
attestation engine: NONE
compliance engine: NONE
agent execution: NONE
~~~

Any need for production/runtime implementation must be separately justified and re-authorized.

---

# 43. S1.8-D40 — Required reference-model examples

A future authorized documentation implementation should include worked examples for at least:

1. design evaluation ACCEPT followed by separate Human design acceptance;
2. implementation evidence PASS followed by evaluator REWORK;
3. evaluator ACCEPT followed by Human refusal to accept;
4. pre-issued conditional promotion authority with later mechanical promotion;
5. stale canonical parent blocking promotion;
6. external SLSA evidence mapped into Relay without creating promotion authority;
7. Relay AI evaluation explicitly not satisfying SLSA two-person review;
8. UNKNOWN property result blocking a promotion-critical gate.

These examples are normative explanatory tests of the model.

---

# 44. S1.8-D41 — Required negative cases

The accepted reference model must clearly reject:

~~~text
evidence == evaluation
evaluation == Human acceptance
Human acceptance == promotion
promotion eligibility == promotion authority
runtime permission == Relay authority
external compliance evidence == Relay authority
model/session separation == SLSA two-party review
moving branch == exact subject
successful mechanical promotion == proof it was authorized
~~~

---

# 45. S1.8-D42 — Design acceptance matrix

An independent design review should require all of the following:

~~~text
[ ] Relay remains semantic authority
[ ] statement classes are non-substitutable
[ ] exact subject identity is mandatory
[ ] policy basis is versioned and digest-bound
[ ] evidence remains immutable historical input
[ ] verification remains separate from authority
[ ] Human Authority remains explicit
[ ] promotion eligibility is derived and non-authoritative
[ ] promotion authority supports dedicated/pre-issued conditional forms
[ ] promotion executor cannot make promotion decisions
[ ] initial Relay predicate family is coherent
[ ] predicate/property versioning is fail-safe
[ ] native verified properties have exact semantics
[ ] PASS / FAIL / UNKNOWN semantics are conservative
[ ] trust is policy/claim-specific
[ ] Sol/Luna evaluator independence is represented correctly
[ ] SLSA mapping is one-way
[ ] SLSA two-party review cannot be inferred from AI review
[ ] NIST SSDF mapping is version/status pinned
[ ] DORA remains a flow-health guardrail
[ ] framework-level compliance claims are conservative
[ ] stale/ambiguous state fails closed
[ ] Slice 1.9 ownership boundary is preserved
[ ] 2.2 / 2.3 / 2.4 consume rather than redefine assurance semantics
[ ] expected Slice 1.8 implementation remains documentation-first
[ ] no implementation or external certification is authorized
~~~

---

# 46. Implementation stop conditions

A future implementation agent must stop and escalate if accepted Slice 1.8 implementation requires:

~~~text
production Python/runtime changes
schema migration
new runtime/dev dependency
GitHub branch protection/ruleset mutation
attestation signing infrastructure
new policy engine
external certification claim
new Human Authority semantics
new lifecycle transition semantics
new evaluator outcome semantics
changing accepted Slice 2.1 runtime contracts
opening Slice 1.9
agent execution
~~~

---

# 47. Resulting capability if implemented and accepted

After Slice 1.8 implementation and acceptance, Relay will have an explicit assurance vocabulary capable of answering:

~~~text
What exact thing is being claimed about?
Is this fact, verification, authority, or executed transition?
What evidence supports it?
Under what exact policy was it judged?
Who/what issued the claim?
What separation assumptions were required?
Which Relay-native verified properties pass/fail/are unknown?
Which external framework requirements map to this control?
What may Relay truthfully claim externally?
Does this evidence create authority?  (normally no)
Is the subject eligible for promotion?
Is there valid promotion authority?
Can a mechanical executor act without a new Human decision?
~~~

This becomes the assurance substrate for Slice 1.9, then Phase 2 Role/Work-Packet/Workspace contracts, and finally governed Phase 3 execution.

---

# 48. Hard stop after design

This design authorizes no implementation.

Current state remains:

~~~text
Slice 1.8:
OPEN

Design:
RLY-S18-DESIGN-AUTH-001 — AUTHORIZED

This design revision:
PROPOSED FOR INDEPENDENT DESIGN REVIEW

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Slice 1.9:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~

The next legitimate action is Sol design review with outcome:

~~~text
ACCEPT
REVISE
ESCALATE
~~~

**Unblocked != authorized. Evidence != evaluation. Evaluation != Human acceptance. Human acceptance != promotion.**
