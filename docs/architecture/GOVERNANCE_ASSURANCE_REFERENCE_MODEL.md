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
  -> PROMOTION AUTHORIZATION
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
 authorization             AgentRuntime            evaluations
 promotion authority       tools/runtime           build evidence
        |                        |                        |
        +------------------------+------------------------+
                                 |
                                 v
                           VERIFICATION
                                 |
                 +---------------+---------------+
                 |                               |
                 v                               v
          Relay policy                     External standards
          verification                     conformance
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

The control plane never infers authority from the execution plane. CI, runtime execution, evaluation, and compliance checks are evidence unless an explicit Relay authority transition says otherwise.

## 4. External assurance relationship

**SLSA** tests source/build assurance, provenance, verification, and promotion controls. Relay is not a SLSA wrapper, frontend, or orchestration layer.

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
Relay Promotion Authorization
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
Trusted Promotion Executor
      |
      v
Protected Canonical Reference
      |
      v
Promotion Evidence / Attestation
```

The executor performs an already-authorized operation; it does not decide whether promotion is allowed.

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
