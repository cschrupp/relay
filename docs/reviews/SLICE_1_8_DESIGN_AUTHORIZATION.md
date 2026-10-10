# Relay — Slice 1.8 Governance Assurance Reference Model — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-10  
**Record:** RLY-S18-DESIGN-AUTH-001  
**Decision:** AUTHORIZED

## 1. Human Authority decision

The Human Authority explicitly authorizes architecture, contract, and detailed design work for:

~~~text
Slice 1.8 — Governance Assurance Reference Model
DESIGN AUTHORIZED
~~~

This authority follows:

~~~text
Slice 1.8 opening:
RLY-S18-OPEN-001 — OPEN

Exact canonical design subject baseline:
920d0a97b68f34c17b88fbd81339e39168dc87e6
~~~

## 2. Authorized design role

~~~text
Slice 1.8 Architect / Designer / Reviewer:
GPT-5.6 Sol
~~~

The architect may inspect canonical Relay governance, lifecycle, repository-contract, AgentRuntime, promotion, evidence, evaluation, and authority records as needed to produce the minimum sufficient Slice 1.8 design.

## 3. Roadmap objective

The accepted roadmap objective is to establish a Relay-native governance-assurance reference model without making SLSA, NIST SSDF, DORA, or another external framework Relay's domain model.

Normative direction:

~~~text
Relay native semantics
        ↓
external representation / assurance / compliance proof

NOT

external standard
        ↓
Relay semantics
~~~

## 4. Authorized design scope

The design may define only the architecture and contracts needed to formalize Relay's governance-assurance model.

At minimum, the design must resolve:

1. Relay-native versus external-assurance requirements and ownership boundaries.
2. Exact Control/Governance, Execution, Evidence/Provenance, Verification, Human Acceptance, and Promotion plane responsibilities.
3. Native lifecycle claim boundaries and permitted transitions between evidence, evaluation, Human acceptance, promotion eligibility, valid promotion authority, and canonical promotion.
4. Relay-native attestation-envelope direction, including when an external schema is sufficient and when a Relay-native predicate is required.
5. Minimum native predicate family and versioning semantics for design evaluation, design acceptance, implementation authorization, execution provenance, evaluation, Human acceptance, promotion authorization, promotion, and control-state claims.
6. Relay-native verified-property vocabulary, definitions, claim subjects, evidence requirements, and failure semantics.
7. Actor, verifier, executor, Human Authority, and trust terminology needed by later Slice 2.2 Role Contracts.
8. Exact meaning of independent evaluation under the established Sol/Luna role model, preserving implementation-actor versus evaluator separation unless stronger separation is explicitly authorized.
9. Conservative compliance-claim policy: what Relay may claim, what requires external verification, and what must remain unsupported/unknown.
10. Standards-mapping model for SLSA, NIST SSDF, DORA, and future frameworks, keeping mappings as adapters rather than source semantics.
11. DORA-style flow-health / governance-overhead guardrails so deterministic governance does not become unnecessary manual ceremony.
12. Promotion-authority semantics, including dedicated versus pre-issued conditional authority and the rule that the promotion executor cannot manufacture authority.
13. Versioning and compatibility policy for assurance predicates, verified properties, and future compliance mappings.
14. Required design artifacts, diagrams, examples, negative cases, and traceability back to canonical Relay invariants.

## 5. Mandatory invariants

~~~text
Evidence PASS != Evaluation ACCEPT
Evaluation ACCEPT != Human acceptance
Human acceptance != Promotion
Unblocked != authorized
Authorized != accepted
Accepted != promoted
Execution cannot manufacture authority
Evidence cannot manufacture authority
Evaluation cannot manufacture authority
Promotion executor != promotion decision maker
~~~

External standards may constrain or validate applicable Relay properties, but they do not create Relay authority or redefine Relay lifecycle semantics.

Independent AI evaluation remains a Relay-native property and must not be misrepresented as satisfying an external requirement explicitly defined in terms of multiple trusted humans or other stronger trust assumptions.

## 6. Expected design preference

Prefer minimum sufficient architecture and reuse of accepted Relay concepts over new systems.

The design should primarily refine:

- docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md;
- docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md;
- explicit design/review records and any narrowly necessary supporting governance documentation.

A new runtime service, database abstraction, event system, policy engine, attestation store, or compliance engine requires explicit justification and is not authorized for implementation by this record.

## 7. Explicit non-authority

This authority does not authorize:

- Slice 1.8 implementation;
- production source/runtime/test/dependency/schema changes;
- GitHub branch protection, ruleset, repository-setting, or promotion-mechanism mutation;
- trusted promotion-executor implementation;
- typed attestation subsystem implementation;
- cryptographic signing infrastructure;
- compliance automation;
- SLSA level or other external certification claims;
- Role Contract implementation;
- work-packet or execution-workspace implementation;
- OpenCode/provider/model execution;
- autonomous agent execution;
- Phase 3 opening;
- Slice 1.9 opening or design;
- changes to accepted Slice 2.1 implementation;
- broad redesign of Relay governance unrelated to the Slice objective.

If the architect concludes an excluded capability is necessary, design work must stop at that boundary and escalate instead of silently widening scope.

## 8. Required design evaluation

The resulting Slice 1.8 design must receive Sol review against this exact authority and baseline with outcome:

~~~text
ACCEPT
REVISE
ESCALATE
~~~

Design evaluation does not itself grant Human design acceptance or implementation authorization.

## 9. State after authorization

~~~text
Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Slice 1.8:
OPEN

Opening:
RLY-S18-OPEN-001 — OPEN

Design:
RLY-S18-DESIGN-AUTH-001 — AUTHORIZED

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slices 2.2–2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~

**Unblocked != authorized. Design authorized != implementation authorized.**
