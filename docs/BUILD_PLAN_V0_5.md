# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.2 closed  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after acceptance and closure of Slice 1.2.

Relay continues to be built inside-out:

```text
deterministic domain contracts
        ↓
lifecycle / governance
        ↓
persistence / auditability
        ↓
repository contract
        ↓
provider repository integration
        ↓
human workflow
        ↓
agent execution
        ↓
multi-agent orchestration
```

The governance model remains the product.

Historical Build Plans remain planning context only where they do not conflict with accepted records, the current registry, or later Human Authority decisions.

---

# 2. Current project state

```text
Phase 0:
COMPLETE / CLOSED

Slices 0.1–0.6:
CLOSED / ACCEPTED

Phase 1:
OPEN

Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Accepted Slice 1.1 technical result:
ae79b15170c88e776af99944eab9b2fdd6872c2e

Slice 1.1 acceptance-record:
ccfbfb964064e92aef4e21e11f0ad01290acb16f

Slice 1.1 closure evaluation:
RLY-S11-CLOSE-EVAL-001 — ACCEPT

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Accepted Slice 1.2 design head:
4acd6be1f93058d1efcafc66a78fc1a9726c16ba

Accepted Slice 1.2 technical result:
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d

Independent implementation evaluation:
RLY-S12-EVAL-002 — ACCEPT

Human acceptance:
RLY-S12-ACCEPT-001

Acceptance/finalization:
7e08ad484ce794946ec2e09abf44060879e9fc04

Final canonical head evaluated:
3cbac05d8aa91b09ce79965a83d9887b76c23978

Closure evaluation:
RLY-S12-CLOSE-EVAL-001 — ACCEPT

Slice 1.3:
NOT OPEN / NOT AUTHORIZED
```

---

# 3. Process rules in force

## P0-PR-01 — Registered living-projection preflight

Any authorized change surface modifying a registered living projection includes the corresponding `.relay/registry.json` advancement in the same governed change.

## P0-PR-02 — Role/model visibility

Substantive handovers distinguish role/model assignment from actual execution provenance.

Working role convention:

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

When preferred and executing models differ, both are recorded explicitly.

## P0-PR-03 — Design-review outcome vocabulary

Design review uses:

```text
ACCEPT
REVISE
ESCALATE
```

## P0-PR-04 — Transition discipline

Review acceptance and authorization are separate Human Authority decisions.

**Unblocked ≠ authorized.**

---

# 4. Repository and documentation governance

The accepted schema-v1 repository contract remains:

```text
.relay/
└── registry.json
```

Canonical status is a registry relationship, not a filename.

Registered living projections advance through:

```text
changed current projection
→ new ArtifactId
→ revision N + 1
→ exact new content digest
→ canonical pointer advances
```

Historical locked/immutable records remain immutable.

---

# 5. Phase 1 — GitHub and human-controlled project workflow

Phase 1 is OPEN.

Work remains one governed slice at a time.

## Slice 1.1 — GitHub App Integration

```text
COMPLETE / ACCEPTED / CLOSED
```

Accepted capabilities include:

- GitHub App RS256 authentication;
- read-only installation-token use;
- project-scoped installation and repository-access state;
- fail-closed permission readiness;
- signed installation webhooks;
- semantic delivery idempotency;
- monotonic integration-state concurrency;
- explicit GitHub repository identity → provider-neutral `RepositoryRef` conversion.

## Slice 1.2 — Repository Registration and Baseline Resolution

```text
COMPLETE / ACCEPTED / CLOSED
```

Accepted objective:

> Bind the already accepted provider-neutral project repository identity to a verified GitHub repository snapshot and create immutable Relay baselines whose commit and registered artifact bytes are proven to come from the same repository commit.

Accepted capabilities include:

- `Project.primary_repository` remains the sole project-repository authority;
- explicit branch/tag/full-SHA selectors;
- resolve-once canonical immutable commit identity;
- exact commit/tree/blob snapshot proof;
- exact `.relay/registry.json` and registered-byte verification;
- shared Slice 0.6 repository-contract validation;
- captured GitHub installation/repository identity and `state_revision`;
- pre/post provider repository identity bracketing;
- stable first-binding Artifact semantics preserving F007;
- atomic local authority re-check plus Artifact/Baseline persistence;
- explicit Baseline and Decision identity inputs;
- deterministic fail-closed race/error behavior;
- no migration v3, new runtime dependency, local Git dependency, or GitHub write permission.

Slice 1.2 does NOT:

- initialize or modify remote `.relay/`;
- request GitHub write permission;
- create branches, commits, or pull requests;
- modify accepted Project repository authority;
- execute agents;
- create a generic provider framework.

Those boundaries remain future work.

## Slice 1.3 — `.relay/` Initialization and Sync

Potential objective:

> Recognize or explicitly initialize the accepted repository contract through GitHub when write behavior is separately designed and authorized.

Any required write permission must be separately designed and approved.

```text
NOT OPEN / NOT AUTHORIZED
```

## Slice 1.4 — Project and Slice CRUD

```text
NOT OPEN
```

## Slice 1.5 — Board Projection

```text
NOT OPEN
```

## Slice 1.6 — Human Authorization and Decision Gates

```text
NOT OPEN
```

## Slice 1.7 — Manual Evaluation and Acceptance

```text
NOT OPEN
```

---

# 6. Slice 1.2 completion evidence

The full Slice 1.2 authority chain is complete:

```text
RLY-S12-OPEN-001
RLY-S12-DESIGN-AUTH-001
RLY-S12-DESIGN-EVAL-003 — ACCEPT
RLY-S12-DESIGN-ACCEPT-001
RLY-S12-AUTH-001
RLY-S12-EVAL-001 — REWORK
RLY-S12-EVAL-002 — ACCEPT
RLY-S12-ACCEPT-001
RLY-S12-CLOSE-EVAL-001 — ACCEPT
```

Completion gates:

1. Slice 1.1 closed and accepted. **DONE**
2. Human Authority opened Slice 1.2 and authorized design. **DONE**
3. Revision 1 + Revision 2 + Revision 3 design completed. **DONE**
4. Independent combined design review accepted the design. **DONE**
5. Human Authority accepted the design. **DONE**
6. Human Authority separately authorized implementation. **DONE**
7. Implementation preserved the accepted Slice 0.6 and Slice 1.1 authority boundaries. **DONE**
8. Independent implementation evaluation completed after bounded test-only rework. **DONE**
9. Human Authority accepted exact candidate `9ed4a8da4d989fd41674ae59ef68ba4238c09b5d`. **DONE**
10. Acceptance/finalization records, ADR-0008, architecture record, and Slice 1.2 memory were produced and locked/accepted. **DONE**
11. Finalization and promoted-main CI passed. **DONE**
12. Independent closure audit verified the complete A01–A149 objective surface and accepted closure. **DONE**

Passing CI never by itself implied design, implementation, acceptance, or closure authority.

---

# 7. Phase-1 hard stop — M0 validation

Phase 1 ends only after Relay can govern a real human-controlled project workflow.

Required dogfood questions remain:

- Does the board clarify real project state?
- Are deterministic traffic lights useful?
- Does READY versus AUTHORIZED matter in practice?
- Does durable memory reduce repeated context explanation?
- Are gates useful rather than bureaucratic?
- Can a fresh reviewer reconstruct why an accepted baseline exists?

---

# 8. Later roadmap

Strategic sequence remains:

```text
Phase 2  provider and agent foundation
Phase 3  first autonomous implementation/evaluation loop
Phase 4  upstream architecture/contract/planning automation
Phase 5  research
Phase 6  sidecar experiments
Phase 7  dependency invalidation and staleness
Phase 8  parallel agent development
Phase 9  cost/budgets
Phase 10 security and production hardening
Phase 11 collaboration/organizations
Phase 12 external project-management integrations
Phase 13 commercial productization
```

No roadmap entry is authorization.

---

# 9. Current authorization boundary

```text
Phase 1:
OPEN

Slice 1.1:
CLOSED / ACCEPTED

Slice 1.2:
CLOSED / ACCEPTED

Current role/model:
Human Authority — user

Next governed action:
Human Authority may choose whether to open Slice 1.3.

Slice 1.3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
