# Human Decision Support — Derived Projection, Not Authority

**Status:** WORKING ARCHITECTURE — DOCUMENTATION ONLY / NOT IMPLEMENTATION AUTHORITY  
**Authority:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001`  
**Date:** October 10, 2026

## Purpose and boundary

Governance Assurance proves the authority, evidence, and verification chain. Decision Support makes consequential engineering decisions legible to the Human. Neither substitutes for the other. Relay does not attempt to prove Human understanding. Relay is responsible for presenting decisions legibly enough that a Human can understand, question, inspect, compare, defer, and decide. This is a product responsibility, not a cognition predicate.

```text
                    CANONICAL GOVERNED STATE
                             |
          +------------------+-------------------+
          |                  |                   |
        intent              policy          prior authority
        design              evidence        prior evaluation
        risks               unknowns        consequences
          |                  |                   |
          +------------------+-------------------+
                             v
                  DECISION BASIS PROJECTION
                    NON-AUTHORITATIVE
                             v
                  PENDING HUMAN DECISION
                             v
                    HUMAN AUTHORITY ACT
                             v
                  GOVERNED STATE TRANSITION
```

Decision Support is a cross-cutting read/projection seam attached to each pending Human decision required by policy. It is not a lifecycle stage and does not sit only after verification: Relay has Human Authority gates before design or execution evidence exists, including Slice opening, design authorization, implementation authorization, and exception authorization. Exact inputs vary by decision. A design-authorization basis may include intent, roadmap, existing architecture, scope, risk, and non-authority boundaries without implementation evidence or evaluation. Technical acceptance may include implementation result, CI, runtime evidence, evaluation, risks, and unknowns. Promotion authority may additionally require an accepted result, current parent, and promotion eligibility.

The diagram is a decision-gate projection pattern, not a claim that all governed-state changes follow a single lifecycle. Decision Support is projection, explanation, navigation, question-answering, traceability, and human-comprehension support. It is not authority, evidence creator, evaluation authority, promotion authority, lifecycle owner, or policy owner. It may summarize authoritative records but owns none of them.

The statement classes remain `FACT / EVIDENCE`, `VERIFICATION JUDGMENT`, `AUTHORITY DECISION`, and `EXECUTED TRANSITION / PROMOTION RECORD`. `DECISION SUPPORT PROJECTION` is a fifth derived projection category, not a new authoritative statement class.

```text
Evidence != Evaluation
Evaluation != Human Authority
Human Authority != Executed Transition
Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Authority
```

Do not introduce machine-verifiable claims such as `RELAY_HUMAN_UNDERSTANDS`, `HUMAN_COMPREHENSION_PASS`, or `HUMAN_QUIZ_PASSED`. Human cognition is not machine-verifiable. Relay can verify whether it supplied a required decision basis; it cannot verify that the Human understood it.

## DecisionBasisProjection

`DecisionBasisProjection` is a conceptual backend/read-model object that eventually feeds a Human-facing interface. It is bound to a generic governed subject and one exact decision, rather than permanently equating a decision with a Slice. Conceptually it contains:

```text
decision_id, decision_type
governed_subject, exact_subject_identity
current_state, proposed_transition
why_this_decision_exists
policy_required_components and their applicability state
authority_basis, policy_basis, accepted_design_basis (when applicable)
what_changed, what_did_not_change
evidence_summary, evaluation_summary (when applicable)
required_verified_properties, verified_property_results
known_risks, known_unknowns, blocking_findings
consequences_if_approved, consequences_if_rejected,
    consequences_if_deferred
explicit_non_authority, source_references, freshness_state
```

The projection is assembled from the components required for that exact decision by applicable policy. `accepted_design_basis`, evidence, evaluation, and verified-property results are not universal required fields: they may be optional or not applicable at an opening or pre-design gate. This is architecture only; it does not define a database schema, Pydantic model, API, or persistence design.

For conceptual component applicability, distinguish `REQUIRED_PRESENT`, `OPTIONAL_PRESENT`, `NOT_APPLICABLE`, `UNKNOWN`, and `MISSING_REQUIRED`. `RELAY_DECISION_BASIS_COMPLETE` passes only when every component required by policy for the exact decision is present and current, and every inapplicable component is explicitly recorded or deterministically known to be not applicable. A pre-design decision with no evaluator because none is required is `NOT_APPLICABLE`, not `UNKNOWN` or missing evidence. If technical acceptance requires an evaluation and it cannot be located, that component is `MISSING_REQUIRED` and the property does not pass. If the evaluation exists but whether it applies cannot be established, the state is `UNKNOWN`. This verifies Relay supplied the required decision basis, not Human comprehension.

The underlying governed subject may later be a Slice, task, work item, evaluation, promotion candidate, exception, incident, or future governed atomic unit. This architecture does not create a Task or WorkItem domain model.

The current interface may retain a Slice Card as a current work/lifecycle projection. A Decision Card represents one exact Human decision. One Slice may produce multiple Decision Cards, including opening a Slice, authorizing or accepting design, authorizing implementation, technically accepting implementation, authorizing promotion, or granting an exception.

## Decision Card experience

A future Decision Card should identify what decision is required and why now; show current and proposed state; explain what changed and did not change; link evidence and evaluation; expose risks, unknowns, and consequences of approval, rejection, or deferral; and provide actions to ask a question, inspect evidence, view a change or architecture delta, defer, and invoke the applicable explicit Human Authority command. A labelled five-point clarity scale may be offered separately from that command.

The actual Human Authority control is a separate explicit command. A Q&A response or clarity rating must never trigger an authority action.

### Decision-scoped Q&A

Future Q&A may explain, retrieve, compare, summarize, show provenance/evidence/evaluation, describe consequences, surface uncertainty, and answer follow-up questions. It may not authorize, accept, reject, promote, open a Slice, alter lifecycle/evidence/evaluation, manufacture facts, or hide `UNKNOWN`. Each answer should label its basis as applicable: `CANONICAL_FACT`, `EVALUATOR_JUDGMENT`, `EXTERNAL_REFERENCE`, `MODEL_INFERENCE`, or `UNKNOWN`. Q&A context must be bound to the exact Decision Basis and its freshness state.

Questions may include why a decision exists, what changed or remains unchanged, risks and unknowns, why an evaluator reached a result, what evidence supports it, what follows from approval/rejection/deferral, how the architecture changed, plain-language explanation, and comparison to a prior candidate.

### DecisionClarityFeedback

`DecisionClarityFeedback` is optional product telemetry, conceptually containing `decision_id`, a 1–5 rating, optional comment, confusion tags, and recording time. Use a labelled Likert scale:

1. Not clear enough for me to decide
2. I have major unanswered questions
3. I understand the main idea but still have gaps
4. Clear enough for me to make the decision
5. Very clear; I understand the key trade-offs and consequences

Possible tags are scope, rationale, architecture, risk, evidence, evaluation, authority, consequences, technical details, and other. Feedback is not acceptance, authorization, evaluator judgment, or objective proof of understanding. Low ratings may foreground explanation, architecture delta, evidence inspection, questions, or deferral; they do not invalidate Human Authority. There is no mandatory quiz or understanding threshold. Geoffrey Litt's participation-oriented framing informs this design without making quizzes mandatory [SRC-LITT-UNDERSTANDING-2026].

## Identity and execution assurance concepts

`RELAY_ACTOR_IDENTITY_BOUND` passes only when the actor/issuer for a governed action or statement is independently bound to the identity required by policy. A self-asserted role, model name, session label, HTTP header, or prompt is insufficient. Preserve `role != identity != authority`. This property is a future consumer in Slice 2.2 and follows the distinction between a model request and authorization [SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026] [SRC-PAIE-AGENT-IDENTITY-PLATFORM-2026].

`RELAY_EXECUTION_PROVENANCE_SUFFICIENT` passes only when the provenance required by applicable policy and risk is exact enough to evaluate the required assurance properties. A documentation candidate may require exact commit, changed paths, registry transition, and CI. A higher-risk autonomous implementation may require execution/workspace/runtime/provider/model identity, tool activity, permissions, network state, quality execution, event gaps, and terminal result. Relay does not require universal full-trajectory logging. Output verification and trajectory evaluation answer different questions; a plausible artifact alone may not expose a defective process [SRC-GOOGLE-NEW-SDLC-2026].

## GovernanceProfile in a decision basis

When a future policy requires a `GovernanceProfile`, a Decision Card should be able to show the selected profile and version, why it applies, required Human decisions, required evidence, protected verification assets and their mutation permissions, evaluator separation, and expected promotion predicates. It should let the Human ask why the profile applies, why gates are required, whether policy permits a stricter or weaker profile, what would justify a permitted downgrade, and who may modify protected assets. The projection explains Relay policy; it cannot select or relax the profile. The accepted Slice 1.8 semantics are consolidated in [Governance Assurance Reference Model](GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md). No fixed profile taxonomy or selection engine is implemented. Profile changes are prospective: later downgrade cannot authorize earlier work retroactively. Evaluator review may be a prerequisite to asset mutation, but mutation authority must be explicit and policy-recognized.

Governance-effectiveness telemetry may later surface the profile/rationale, expected governance cost, actual decision/evaluation latency, rework, clarity feedback, and the ratio of mechanical to Human gates. This is a future Slice 1.9 direction, not a dashboard design. Telemetry remains non-authoritative and cannot relax a profile [SRC-DORA-CHANGE-APPROVAL].

## External mapping freshness

Conceptual external references identify framework/version/publication status, requirement, and authoritative source. A mapping also records Relay control references, required evidence, assessment and rationale, assessor, verification time, and either review due date or refresh trigger. Exact schema is deferred. A mapping outside its accepted freshness window becomes `STALE`; for a new external claim, stale evidence resolves to `UNKNOWN` until reverified, neither `PASS` nor automatically `FAIL`. This preserves Relay's conservative three-valued semantics.

## Human-gate necessity

A Human gate exists when a **distinct discretionary authority decision** is required. Exact SHA, registry/schema validity, CI, required tests/evidence, current parent, artifact digest, and other machine-evaluable predicates should increasingly be deterministic checks.

For ordinary bounded reversible engineering, Decision Support should implement:

```text
HA-1 DESIGN AUTHORIZATION
    -> final design + AuthorityEnvelope

HA-2 IMPLEMENTATION ACCEPTANCE
    -> final implementation report + independent technical disposition
    -> ACCEPT_AND_PROMOTE / ACCEPT_AND_HOLD / REWORK / REJECT

HA-X EXCEPTIONAL OPERATIONAL AUTHORIZATION
    -> only a distinct consequential external/irreversible action or material deviation
```

Decision Cards should not ask the Human to re-approve routine internal sequencing, commits, CI correction, evaluator-driven in-scope rework, evidence-registration commits, or mechanical promotion already conditionally authorized by HA-2.

Human re-engagement during implementation is driven by material deviation: changed objective/scope, architecture/trust boundary, consequential provider/runtime/model/dependency/network/credential class, risk/profile, destructive/irreversible action, unapproved external effect, budget threshold, or genuine Human trade-off.

Independent evaluation remains separate from Human Authority. `REWORK` inside HA-1 does not create a new Human gate.

DORA supports peer review, automation, continuous testing, fast feedback, and risk-based scrutiny over heavyweight approval bureaucracy [SRC-DORA-CHANGE-APPROVAL]. Policy-gated agent references likewise reserve Human approval for consequential actions [SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026].

See [Human Authority Phase-Gate Model](HUMAN_AUTHORITY_PHASE_GATES.md).

## Assurance, external standards, and roles
## Assurance, external standards, and roles

Relay's existing statement classes and one-way external mapping remain in force. Relay semantics map outward to external representation or compliance proof; external standards never define Relay semantics. Relay is not a SLSA wrapper. In particular, a Sol review or Sol/Luna separation does not satisfy `SLSA_SOURCE_TWO_PARTY_REVIEWED`, which is defined in terms of review by two trusted persons [SRC-SLSA-VERIFIED-PROPERTIES]. SLSA's informed-review direction—show reviewers a clear representation of change effects—supports legibility but does not define Relay Human Authority [SRC-SLSA-SOURCE-REQUIREMENTS].

NIST SP 800-218 SSDF 1.1 is Final; SP 800-218 Rev. 1 / SSDF 1.2 is Draft; SP 800-218A is Final. Mappings do not establish Relay conformance [SRC-NIST-SSDF-1_1] [SRC-NIST-SSDF-1_2-DRAFT] [SRC-NIST-SP800-218A].

The operating model remains GPT-5.6 Sol as architect, designer, reviewer/evaluator, and governance gatekeeper; GPT-5.6 Luna/Codex as implementation or bounded rework executor and evidence producer; Human as root authority. `IMPLEMENTER != EVALUATOR` by default. `DESIGNER != EVALUATOR` is not automatic; a specific policy may require stronger separation.

## ContextManifest downstream requirement

Slice 2.3 should later define a `ContextManifest` distinguishing stable `STATIC CONTEXT` (role contract, system/repository rules, architecture references, accepted design, authority/non-authority, guardrails, conventions) from `DYNAMIC CONTEXT` (retrieval, task skills, tool definitions, selected code, runtime observations, external references, bounded session history). Prompt text is not the effective governed context. The effective context needs provenance, version, and digest semantics and should itself be reviewable [SRC-GOOGLE-NEW-SDLC-2026]. No ContextManifest implementation is authorized here.

## Roadmap and authority

Phase 1 comprises Slices 1.1–1.10, with 1.1–1.7 closed; 1.8 open with its combined design Human-accepted and documentation implemented / awaiting independent implementation evaluation; 1.9 Human Decision Support and 1.10 Source/Promotion Enforcement planned and unauthorized. Phase 2 Slice 2.1 is closed; 2.2–2.4 remain planned and unauthorized. Phase 3.1 remains future and requires 1.8, 1.9, 1.10, 2.2, 2.3, 2.4, plus explicit Phase 3 opening. These statements do not open any Slice.

Slice 1.8 Design Revision 1 remains preserved historical design input. Slice 1.8 was resumed under `RLY-S18-RESUME-001`; Revision 2 plus Rework 1 are independently accepted under `RLY-S18-DESIGN-EVAL-002` and Human-accepted under `RLY-S18-DESIGN-ACCEPT-001`. Documentation implementation is authorized by `RLY-S18-IMPL-AUTH-001` and now awaits independent implementation evaluation. No Decision Card, Q&A, profile engine, or telemetry collection is implemented.

## Source provenance and limitations

External references provide provenance and design inspiration only. They are not Relay authority, do not establish conformance, and must not override Relay's canonical policy and records. Source identity, status, freshness, and limitations are catalogued in `docs/references/GOVERNANCE_ASSURANCE_AND_AGENTIC_SDLC_SOURCES.md`.

Agentic engineering practice emphasizes repository guardrails, feedback loops, and human steering [SRC-OPENAI-HARNESS-ENGINEERING]. Board-centric asynchronous agent work appears in Symphony and Linear Coding Sessions; GitLab documents attributable agent identity, tool approval, workflow trace logging, and session approval checkpoints [SRC-OPENAI-SYMPHONY] [SRC-LINEAR-CODING-SESSIONS] [SRC-GITLAB-DUO-AGENT-PLATFORM]. These are product/architecture examples, not Relay authority. Vibe Kanban is retained only as historical evidence of the interaction pattern: its company announced shutdown while the project continued as open-source/community maintained [SRC-VIBE-KANBAN].
