# Relay - Governance Assurance Reference Model

**Status:** WORKING REFERENCE MODEL - REVIEW READY / NOT IMPLEMENTATION AUTHORITY
**Authority basis:** `RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED`
**Applies to:** Phase 1 hardening, Phase 2 agent foundation, later governed autonomy
**Date:** October 2026

**Current re-baseline:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001`
**Slice 1.8:** OPEN / DESIGN AUTHORIZED / PAUSED — ARCHITECTURE / ROADMAP REBASE / IMPLEMENTATION NOT AUTHORIZED

---

## 1. Framework identity

Relay is an **AI software-development and engineering-governance framework**.

Relay owns project/Slice definition, architecture and design governance, exact authority and baseline binding, human and AI role boundaries, execution governance, evidence/provenance, independent evaluation, rework, Human acceptance, canonical promotion, lifecycle state, and durable project knowledge.

External standards do not define Relay.

```text
Relay native semantics
        |
        +--> external representation / assurance / compliance proof
                  |
                  +-- SLSA
                  +-- NIST SSDF
                  +-- DORA
                  +-- future standards and enterprise policy
```

The reverse direction is not accepted architecture.

## 2. Native Relay lifecycle

```text
INTENT
  -> DESIGN
  -> DESIGN EVALUATION
  -> HUMAN DESIGN ACCEPTANCE
  -> IMPLEMENTATION AUTHORIZATION
  -> EXECUTION
  -> EXECUTION EVIDENCE / PROVENANCE
  -> INDEPENDENT EVALUATION
  -> HUMAN TECHNICAL ACCEPTANCE
  -> PROMOTION ELIGIBILITY
  -> VALID PROMOTION AUTHORITY CHECK
  -> CANONICAL PROMOTION
```

Normative invariants:

```text
Evidence PASS != Evaluation ACCEPT
Evaluation ACCEPT != Human acceptance
Human acceptance != Promotion
Unblocked != authorized
Authorized != accepted
Accepted != promoted
Execution cannot manufacture authority
Evidence cannot manufacture authority
Evaluation cannot manufacture authority
```

## 3. Reference architecture

```text
                              RELAY
                                 |
        +------------------------+------------------------+
        |                        |                        |
        v                        v                        v
 CONTROL / GOVERNANCE        EXECUTION              EVIDENCE
        PLANE                  PLANE                  PLANE
        |                        |                        |
 Human Authority           Role Contract           provenance
 lifecycle                 Work Packet             CI evidence
 policy                    Workspace               artifacts
 authorization             AgentRuntime            build evidence
 promotion authority       tools/runtime           runtime observations
        |                        |                        |
        +------------------------+------------------------+
                                 |
                                 v
                           VERIFICATION
                                 |
                 +---------------+---------------+
                 |                               |
                 v                               v
       Independent evaluation              External standards
       Relay policy verifier               conformance verifier
                                                 |
                                       +---------+---------+
                                       |         |         |
                                      SLSA      SSDF      DORA
                           |
                           v
                     VERIFICATION
                           |
                           v
                  DECISION SUPPORT
                 NON-AUTHORITATIVE
                           |
                           v
                   HUMAN AUTHORITY
                           |
                           v
                  PROMOTION ELIGIBILITY
                           |
                           v
               VALID PROMOTION AUTHORITY
                           |
                           v
                MECHANICAL TRANSITION
                           |
                           v
              TRANSITION / PROMOTION EVIDENCE
```

Decision Support is projection, explanation, navigation, question-answering, traceability, and comprehension support. It is not authority, evidence creator, evaluator, lifecycle/policy owner, or promotion authority. It may summarize facts, evidence, verification, authority, and executed transitions but owns none. `Evidence != Evaluation`; `Evaluation != Human Authority`; `Human Authority != Executed Transition`; and `Decision Support != Evidence / Evaluation / Authority`.

The assurance statement classes remain `FACT / EVIDENCE`, `VERIFICATION JUDGMENT`, `AUTHORITY DECISION`, and `EXECUTED TRANSITION / PROMOTION RECORD`. `DECISION SUPPORT PROJECTION` is a derived view, not a fifth authoritative class. Relay does not assert machine-verifiable Human understanding. See [Human Decision Support](HUMAN_DECISION_SUPPORT.md) for the conceptual `DecisionBasisProjection`, decision-scoped Q&A, optional clarity feedback, and generic governed-subject binding.

The control plane never infers authority from the execution plane.

CI outputs, runtime observations, provenance, test results, artifacts, and external-conformance results are evidence. Independent evaluation is a separately governed verification judgment over evidence.

Neither evidence nor evaluation can manufacture Human Authority. An evaluation result may satisfy a prerequisite for a later Human decision or for a transition already authorized by exact Relay policy, but the evaluation does not create that authority.

## 4. External assurance relationship

**SLSA** tests applicable source/build assurance, provenance, and verification properties. Relay may map relevant SLSA controls and evidence into its own promotion eligibility and promotion policy. SLSA does not define Relay promotion semantics. Relay is not a SLSA wrapper, frontend, or orchestration layer [SRC-SLSA-V1_2]. SLSA v1.2 is Approved [SRC-SLSA-V1_2]. `SLSA_SOURCE_TWO_PARTY_REVIEWED` means review by two trusted persons; Sol review or Sol/Luna separation does not satisfy it [SRC-SLSA-VERIFIED-PROPERTIES]. SLSA informed review also supports showing reviewers a clear representation of change effects, without defining Relay authority [SRC-SLSA-SOURCE-REQUIREMENTS].

**NIST SSDF** is a secure-development control-coverage catalogue, not Relay's workflow. SP 800-218 SSDF 1.1 is Final; SP 800-218 Rev. 1 / SSDF 1.2 is Draft; SP 800-218A is Final [SRC-NIST-SSDF-1_1] [SRC-NIST-SSDF-1_2-DRAFT] [SRC-NIST-SP800-218A]. A mapping does not establish Relay conformance.

**DORA** is delivery research guidance and a flow-health guardrail. Peer review, automation, continuous testing, fast feedback, and risk-based scrutiny can reduce heavyweight approval bureaucracy; this is not Relay lifecycle authority [SRC-DORA-CHANGE-APPROVAL]. Relay distinguishes Human decision from mechanical assurance and preserves the future principle:

```text
Authorized != manually supervised
```

when deterministic mechanics have separately accepted authority.

## 5. Relay-native attestations

Potential native predicates:

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

Rule: use an external schema where it faithfully represents a Relay claim; otherwise use a Relay-native predicate.

Attestations supplement the current canon. They do not silently replace existing immutable authority.

## 6. Relay-native verified properties

```text
RELAY_EXACT_AUTHORIZED_BASELINE
RELAY_EXECUTOR_AUTHORITY_SEPARATION
RELAY_INDEPENDENT_EVALUATION
RELAY_SCOPE_CONFORMANCE
RELAY_HUMAN_ACCEPTED
RELAY_PROMOTION_AUTHORIZED
RELAY_FAIL_CLOSED
RELAY_RUNTIME_IDENTITY_RECORDED
RELAY_CONTROL_CONTINUITY_VERIFIED
RELAY_DECISION_BASIS_COMPLETE
RELAY_ACTOR_IDENTITY_BOUND
RELAY_EXECUTION_PROVENANCE_SUFFICIENT
```

`RELAY_DECISION_BASIS_COMPLETE` passes only when the policy-required DecisionBasisProjection for the exact decision includes subject identity, authority and policy/design basis, evidence/evaluation references, blockers, unknowns, material consequences, and explicit non-authority. It does not measure Human understanding.

`RELAY_ACTOR_IDENTITY_BOUND` passes only when the actor/issuer is independently bound to the identity required by policy; role, identity, and authority remain distinct. A model request does not grant tool authorization [SRC-PAIE-POLICY-GATED-TOOL-EXECUTION-2026] [SRC-PAIE-AGENT-IDENTITY-PLATFORM-2026].

`RELAY_EXECUTION_PROVENANCE_SUFFICIENT` is risk/policy-relative: the recorded exact provenance must suffice to evaluate the required properties. Documentation changes may need exact commit, changed paths, registry transition, and CI; higher-risk autonomous work may need execution, workspace, runtime, provider/model, tool, permission, network, quality, continuity, and terminal evidence. It does not require universal full trajectory logging. Output verification and trajectory evaluation are distinct [SRC-GOOGLE-NEW-SDLC-2026].

Independent AI evaluation is Relay-native. It must not be misrepresented as satisfying an external requirement explicitly defined in terms of multiple trusted persons.

## 7. Canonical source and promotion architecture

```text
Human Authority
      |
      v
Valid Promotion Authority
(dedicated or pre-issued conditional)
      |
      v
Policy Verifier
      |
      +-- candidate SHA exact
      +-- authority basis exact/current
      +-- CI evidence exact/current
      +-- evaluation current
      +-- Human acceptance exact
      +-- canonical parent current
      +-- required attestations valid
      |
      v
Promotion Eligible
      |
      v
Trusted Promotion Executor
      |
      v
Protected Canonical Reference
      |
      v
Promotion Evidence / Attestation
```

The executor performs an already-authorized operation; it does not decide whether promotion is allowed.

Promotion authority is a semantic requirement, not necessarily a new manual approval ceremony. Valid promotion authority may be either:

- a dedicated exact promotion authorization; or
- an earlier exact finalization/closure authority that explicitly authorizes promotion once stated verification predicates are satisfied.

Therefore:

```text
No valid promotion authority:
promotion forbidden.

Valid existing promotion authority + required predicates satisfied:
mechanical promotion may proceed without another Human decision.
```

Checking promotion authority at promotion time does not imply that the authority was created at that moment.

At the roadmap re-baseline basis:

```text
main protected = false
repository rulesets = []
```

That is historical design input for planned Slice 1.10, not authority to change repository settings.

## 8. Standards mapping

Long-term conformance should remain an adapter layer:

```text
ExternalFramework
    framework_id
    version
    requirement_set

ExternalRequirementRef conceptually identifies framework/version/publication status, requirement, and authoritative source. A ComplianceMapping conceptually binds it to Relay controls/evidence, assessment status and rationale, assessor, verification time, and review due date or refresh trigger. Exact schema is deferred. A stale mapping becomes `UNKNOWN` for a new external claim until reverified, not PASS and not automatically FAIL.
```

This generic mechanism is deferred until Relay-native controls are stable enough to map.

## 9. Roadmap consequences

```text
Phase 1 — Deterministic Governance Foundation:
  1.1–1.7 COMPLETE / ACCEPTED / CLOSED
  1.8 Governance Assurance Reference Model — OPEN / PAUSED FOR REBASE
  1.9 Human Decision Support — PLANNED / NOT AUTHORIZED
  1.10 Canonical Source and Promotion Enforcement — PLANNED / NOT AUTHORIZED

Phase 2:
  2.1 Agent Runtime Contract                  CLOSED
  2.2 Role Contracts                         PLANNED
  2.3 Context and Work-Packet Contract       PLANNED
  2.4 Execution Workspace Authority          PLANNED

Phase 3:
  first governed autonomous execution loop
  NOT OPEN / NOT AUTHORIZED
```

Slice 2.2 consumes `RELAY_ACTOR_IDENTITY_BOUND`, `RELAY_IMPLEMENTER_EVALUATOR_SEPARATION`, `RELAY_INDEPENDENT_EVALUATION`, `RELAY_RUNTIME_IDENTITY_RECORDED`, and `RELAY_EXECUTION_PROVENANCE_SUFFICIENT`. Slice 2.3 defines a future ContextManifest separating static rules/design/authority from dynamic retrieval, skills, tools, selected code, runtime observations, external references, and windowed session history. Prompt text is not effective governed context; provenance/version/digest semantics are needed [SRC-GOOGLE-NEW-SDLC-2026]. Slice 2.4 supplies future scope, provenance, fail-closed, and control-continuity evidence. The Phase 3.1 prerequisite chain is 1.8, 1.9, 1.10, 2.2, 2.3, 2.4, and explicit Phase 3 opening.

### Human-gate necessity

A Human gate should exist only when a distinct discretionary authority decision is required. Exact SHA, registry/schema validity, CI, tests, evidence presence, current parent, and digest correctness should increasingly be mechanically verified. Work commencement, architecture acceptability, implementation authority, exact-result acceptance, promotion authority, and exceptions remain Human decisions. DORA favors peer review and automated controls over heavyweight approvals; the Principal AI Engineer Handbook notes Human approval has human-scale latency [SRC-DORA-CHANGE-APPROVAL] [SRC-PAIE-HANDBOOK-2026].

The operating model remains GPT-5.6 Sol for architecture/design/review/evaluation/governance; GPT-5.6 Luna/Codex for bounded implementation/rework and evidence; Human as root authority. `IMPLEMENTER != EVALUATOR` by default; `DESIGNER != EVALUATOR` is not automatic.

## 10. Hard stop

This document is review-ready architecture, not implementation authority. It opens no Slice, changes no repository setting, and authorizes no agent execution.
