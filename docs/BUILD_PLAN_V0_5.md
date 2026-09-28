# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.3 Design Revision 2 submitted  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after acceptance and closure of Slice 1.2, Human Authority opening of Slice 1.3, explicit authorization of Slice 1.3 architecture / contract / design, independent Revision 1 review, and bounded Revision 2 response.

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

Slice 1.3 opening:
RLY-S13-OPEN-001

Slice 1.3 design authorization:
RLY-S13-DESIGN-AUTH-001

Slice 1.3 Revision 1 review:
RLY-S13-DESIGN-EVAL-001 — REVISE

Slice 1.3:
OPEN

Slice 1.3 architecture / contract / design:
AUTHORIZED — REVISION 2 SUBMITTED FOR INDEPENDENT COMBINED REVIEW

Slice 1.3 implementation:
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

## Slice 1.3 — `.relay/` Initialization and Sync

```text
OPEN
DESIGN AUTHORIZED
REVISION 1 REVIEWED — REVISE
REVISION 2 SUBMITTED FOR INDEPENDENT COMBINED REVIEW
IMPLEMENTATION NOT AUTHORIZED
```

Opening authority:

```text
RLY-S13-OPEN-001
```

Design authority:

```text
RLY-S13-DESIGN-AUTH-001
```

Authorized design baseline:

```text
eb6b3797fb1b317e9158444b9c9dbe469b2ee313
```

Revision 1 design:

```text
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC.md
```

Independent Revision 1 review:

```text
RLY-S13-DESIGN-EVAL-001 — REVISE
```

Revision 2 amendment:

```text
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV2_AMENDMENT.md
```

Revision 1 established the bounded Git Data single-commit architecture. Revision 2 preserves that architecture and resolves the review findings by:

- binding every non-no-op remote mutation to an exact Human Authority `AuthorizationGrant.subject_digest`;
- requiring exact expected default branch and base commit for the authorized write subject;
- preserving pre-existing unregistered files through exact-byte adoption or conflict;
- defining observation-based reconciliation for indeterminate ref-update transport failures;
- rejecting repositories with no existing default-branch head rather than creating a branch;
- prohibiting `.github/workflows/**` content/mode mutation under the contents-only permission ceiling while allowing exact unchanged adoption;
- standardizing successful state vocabulary on `CURRENT` plus `wrote_remote`;
- preserving schema v1, no migration, no new runtime dependency, no PR flow, no force push, and no automatic Baseline persistence.

Any passing combined design review remains separate from Human Authority design acceptance and implementation authorization.

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

Passing CI never by itself implied design, implementation, acceptance, or closure authority.

---

# 7. Slice 1.3 design gate

```text
Pre-opening canonical baseline:
40683b67eb40a28b1ceb8e441804a57d1767cfa1

Opening authority:
RLY-S13-OPEN-001

Pre-design-authorization canonical baseline:
3aa2287f497f80854b03fea3005ee867bca51153

Design authority:
RLY-S13-DESIGN-AUTH-001

Authorized design baseline:
eb6b3797fb1b317e9158444b9c9dbe469b2ee313

Revision 1 submitted head:
433910d0b2df7f0f0a3104cbe97f6df5ebba609a

Revision 1 evaluation:
RLY-S13-DESIGN-EVAL-001 — REVISE
```

Current gate state:

1. Slice 1.2 is closed and accepted. **DONE**
2. Human Authority explicitly opened Slice 1.3. **DONE**
3. Human Authority explicitly authorized Slice 1.3 architecture / contract / design. **DONE**
4. Slice 1.3 Revision 1 architecture / contract / design submitted. **DONE**
5. Independent Revision 1 design review. **DONE — REVISE**
6. Bounded Revision 2 amendment resolving F001–F006. **DONE / SUBMITTED**
7. Independent combined Revision 1 + Revision 2 design review. **PENDING**
8. Human design acceptance. **NOT REACHED**
9. Separate implementation authorization. **NOT REACHED**

No implementation work proceeds from design submission or a future passing design review alone.

---

# 8. Phase-1 hard stop — M0 validation

Phase 1 ends only after Relay can govern a real human-controlled project workflow.

Required dogfood questions remain:

- Does the board clarify real project state?
- Are deterministic traffic lights useful?
- Does READY versus AUTHORIZED matter in practice?
- Does durable memory reduce repeated context explanation?
- Are gates useful rather than bureaucratic?
- Can a fresh reviewer reconstruct why an accepted baseline exists?

---

# 9. Later roadmap

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

# 10. Current authorization boundary

```text
Phase 1:
OPEN

Slice 1.1:
CLOSED / ACCEPTED

Slice 1.2:
CLOSED / ACCEPTED

Slice 1.3:
OPEN

Current role/model:
Architect / Contract Designer — GPT-5.6 Sol

Next governed role:
Independent Design Reviewer — GPT-5.6 Sol

Slice 1.3 architecture / contract / design:
REVISION 2 SUBMITTED / PENDING INDEPENDENT COMBINED REVIEW

Slice 1.3 implementation:
NOT AUTHORIZED

Slice 1.4:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
