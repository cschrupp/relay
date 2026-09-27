# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.2 design authorized  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after acceptance and closure of Slice 1.1.

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
OPEN FOR DESIGN / DESIGN AUTHORIZED

Slice 1.2 implementation:
NOT AUTHORIZED
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

Slice 1.1 does not register a repository as Relay project authority and does not resolve an immutable project baseline.

## Slice 1.2 — Repository Registration and Baseline Resolution

```text
DESIGN AUTHORIZED
IMPLEMENTATION NOT AUTHORIZED
```

Objective:

> Bind a confirmed provider-neutral `RepositoryRef` to Relay project state and deterministically resolve human-selected repository refs to immutable commit identity without weakening the accepted repository contract.

Slice 1.2 owns:

- provider-neutral repository registration for a Relay project;
- explicit branch/tag/full-SHA input semantics;
- remote ref resolution to canonical immutable commit SHA;
- repository identity consistency checks against the Slice 1.1 confirmed GitHub repository;
- construction/use of accepted `CommitRef`;
- baseline identity and persistence semantics;
- byte/snapshot provenance required to close the Slice-0.6 baseline/worktree trust-boundary deferral;
- restart/replay integrity for registered repository/baseline state;
- deterministic error classification for moved/missing/ambiguous refs.

Slice 1.2 must NOT:

- initialize or modify remote `.relay/`;
- request GitHub write permission;
- create branches, commits, or pull requests;
- modify the accepted Slice 1.1 permission ceiling;
- execute agents;
- create a generic multi-provider framework without present-tense need.

Any implementation requires independent design review, Human Authority design acceptance, and separate implementation authorization.

## Slice 1.3 — `.relay/` Initialization and Sync

Recognize or explicitly initialize the accepted repository contract through GitHub.

Any required write permission must be separately designed and approved.

```text
NOT OPEN
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

# 6. Slice 1.2 design-entry contract

Before Slice 1.2 implementation:

1. Slice 1.1 is closed and accepted. **DONE**
2. Human Authority opens Slice 1.2 and authorizes design. **DONE**
3. Design begins from exact baseline `ccfbfb964064e92aef4e21e11f0ad01290acb16f`. **DONE**
4. Accepted Slice 0.6 repository-contract deferrals are explicitly traced. **REQUIRED**
5. Accepted Slice 1.1 `RepositoryRef`/read-access boundary is preserved. **REQUIRED**
6. Independent Slice 1.2 design review occurs. **PENDING**
7. Human Authority accepts the reviewed design. **PENDING**
8. Human Authority separately authorizes implementation. **PENDING**
9. Passing CI never implies design or implementation acceptance.

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
DESIGN AUTHORIZED

Current role/model:
Slice 1.2 Architect — GPT-5.6 Sol

Next role/model:
Independent Design Reviewer — GPT-5.6 Sol

Slice 1.2 implementation:
NOT AUTHORIZED

Slice 1.3:
NOT OPEN
```

**Unblocked ≠ authorized.**
