# Relay - Phase 1 Hardening and Phase 2 Roadmap Re-baseline Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-09  
**Record:** `RLY-P2-ROADMAP-REBASE-001`  
**Decision:** `AUTHORIZED`

## 1. Human Authority decision

The Human explicitly authorizes a documentation-only re-baseline of Relay's roadmap and architecture after canonical closure of Slice 2.1.

The decision is to incorporate the governance-assurance direction developed from the SLSA / SSDF / DORA review while preserving Relay as the authoritative AI software-development and governance framework.

SLSA and other external frameworks are assurance and compliance references. They do not become Relay's domain model or workflow authority.

## 2. Exact canonical basis

```text
Canonical main:
ad0444337efcddb5694d14a57a99c22d18cdfb9c

Slice 2.1:
COMPLETE / ACCEPTED / CLOSED

Slice 2.1 closure evaluation:
RLY-S21-CLOSE-EVAL-002 - ACCEPT

Phase 2:
OPEN - RLY-P2-OPEN-001

Real-project agent execution:
NOT AUTHORIZED
```

## 3. Authorized roadmap reorganization

This authority permits the canonical roadmap and working future-architecture documents to be reorganized around the following sequence:

```text
Phase 1 - accepted deterministic governance baseline / hardening active

  Slice 1.8 - Governance Assurance Reference Model
  Slice 1.9 - Canonical Source and Promotion Enforcement

Phase 2 - provider and agent foundation

  Slice 2.1 - Agent Runtime Contract
              COMPLETE / ACCEPTED / CLOSED

  Slice 2.2 - Role Contracts
  Slice 2.3 - Context and Work-Packet Contract
  Slice 2.4 - Execution Workspace Authority

Phase 3 - first governed autonomous engineering loop

  first execution slice begins only after 1.8, 1.9, 2.2, 2.3,
  and 2.4 satisfy their separately governed prerequisites.
```

The previously proposed Phase 3 coding-agent execution numbering may be superseded in working future-roadmap documents so that the first autonomous execution slice becomes the first Phase 3 slice.

## 4. Authorized architecture direction

The documentation may establish the following architecture:

```text
Relay native semantics
    |
    +-- Control / Governance Plane
    +-- Execution Plane
    +-- Evidence / Provenance Plane
    +-- Verification Plane
    +-- Promotion Plane
    |
    +-- External standards mapping / conformance
            +-- SLSA
            +-- NIST SSDF
            +-- DORA
            +-- future standards and enterprise policies
```

Normative direction:

```text
Relay semantics
    -> external representation / compliance proof

NOT

external standard
    -> Relay semantics
```

The documentation may define a future Relay-native attestation family and verified-property vocabulary, but this authority does not authorize implementation of an attestation subsystem.

## 5. Phase 1 hardening placement

The governance-assurance work is part of Phase 1 hardening because it strengthens the deterministic authority, provenance, verification, and promotion substrate on which later agent autonomy depends.

Slice 1.8 is the next planned development frontier.

Slice 1.9 follows it and owns the source-control / canonical-promotion enforcement gap, including verification of current SCM protections and a trusted mechanical promotion boundary.

Current evidence at this authorization basis shows:

```text
GitHub main protected:
false

GitHub repository rulesets:
none
```

These facts are evidence for Slice 1.9 design. They do not themselves authorize repository-settings changes.

## 6. Phase 2 placement

Slice 2.2 remains the next planned Phase 2 slice after the Phase 1 hardening prerequisites.

Its role-contract design must consume the governance-assurance principles, including:

- actor and verifier identity;
- executor/evaluator separation;
- Human Authority separation;
- capability and non-authority boundaries;
- provenance requirements;
- trust and verified-property semantics.

Slice 2.3 owns exact context and work-packet semantics.

Slice 2.4 owns execution-workspace authority and isolation semantics.

Provider/model routing remains subordinate to the accepted Agent Runtime boundary and is not restored as Relay's primary orchestration abstraction.

## 7. Documentation changes authorized

This record authorizes documentation-only changes required to represent the re-baseline, including:

- `README.md`;
- `docs/PRODUCT_PROPOSAL_V0_5.md`;
- `docs/BUILD_PLAN_V0_6.md`;
- `docs/CURRENT_BASELINE.md`;
- `docs/architecture/AGENT_RUNTIME.md`;
- a new governance-assurance reference-model document;
- `docs/decisions/ADR-0011-agent-runtime-opencode-first.md`;
- the working Slice 2.1 roadmap summary;
- new working future-slice proposals for 1.8, 1.9, 2.2, 2.3, and 2.4;
- supersession / renumbering of the working future Phase 3 coding-agent-execution proposal;
- the canonical registry updates needed for this authority record and changed living projections.

## 8. Explicit non-authority

This record does **not** authorize:

- opening Slice 1.8 or Slice 1.9;
- opening Slice 2.2, 2.3, or 2.4;
- design work under any of those slices beyond preparation of working roadmap proposals;
- implementation under any new slice;
- changing GitHub branch protection, rulesets, repository settings, or promotion mechanics;
- changing the accepted Slice 2.1 implementation;
- new live OpenCode execution;
- real-project agent execution;
- Phase 3 opening;
- autonomous acceptance;
- modifying any prior immutable or locked historical record.

## 9. Governing boundary after this re-baseline

```text
Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Next planned work:
Slice 1.8 - Governance Assurance Reference Model

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 2:
OPEN

Slice 2.1:
COMPLETE / ACCEPTED / CLOSED

Slice 2.2:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.3:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Planned does not mean open. Open does not mean design-authorized. Design acceptance does not imply implementation authority.**
