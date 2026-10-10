# Relay - Governance Assurance Reference Model

**Status:** WORKING REFERENCE MODEL - REVIEW READY / NOT IMPLEMENTATION AUTHORITY  
**Authority basis:** `RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED`  
**Applies to:** Phase 1 hardening, Phase 2 agent foundation, later governed autonomy  
**Date:** October 2026

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
                         HUMAN ACCEPTANCE
                                 |
                                 v
                            PROMOTION
```

The control plane never infers authority from the execution plane.

CI outputs, runtime observations, provenance, test results, artifacts, and external-conformance results are evidence. Independent evaluation is a separately governed verification judgment over evidence.

Neither evidence nor evaluation can manufacture Human Authority. An evaluation result may satisfy a prerequisite for a later Human decision or for a transition already authorized by exact Relay policy, but the evaluation does not create that authority.

## 4. External assurance relationship

**SLSA** tests applicable source/build assurance, provenance, and verification properties. Relay may map relevant SLSA controls and evidence into its own promotion eligibility and promotion policy. SLSA does not define Relay promotion semantics. Relay is not a SLSA wrapper, frontend, or orchestration layer.

**NIST SSDF** is a secure-development control-coverage catalogue, not Relay's workflow.

**DORA** is a flow-health guardrail. Relay distinguishes Human decision from mechanical assurance and preserves the future principle:

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
```

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

That is design input for Slice 1.9, not authority to change repository settings.

## 8. Standards mapping

Long-term conformance should remain an adapter layer:

```text
ExternalFramework
    framework_id
    version
    requirement_set

ComplianceMapping
    external_requirement
    relay_control
    implementation_evidence
    status
    rationale
```

This generic mechanism is deferred until Relay-native controls are stable enough to map.

## 9. Roadmap consequences

```text
Phase 1 hardening:
  1.8 Governance Assurance Reference Model
  1.9 Canonical Source and Promotion Enforcement

Phase 2:
  2.1 Agent Runtime Contract                  CLOSED
  2.2 Role Contracts                         PLANNED
  2.3 Context and Work-Packet Contract       PLANNED
  2.4 Execution Workspace Authority          PLANNED

Phase 3:
  first governed autonomous execution loop
  NOT OPEN / NOT AUTHORIZED
```

Slice 2.2 consumes actor/verifier identity, authority separation, trust, and verified-property concepts. Slice 2.3 makes authority/context/evidence inputs reproducible. Slice 2.4 makes workspace entitlement/isolation explicit.

## 10. Hard stop

This document is review-ready architecture, not implementation authority. It opens no Slice, changes no repository setting, and authorizes no agent execution.
