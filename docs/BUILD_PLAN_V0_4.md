# Relay — Build Plan and Development Roadmap

**Version:** 0.4  
**Status:** Current living implementation plan — Phase 1 open  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.3 at `docs/BUILD_PLAN.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.4*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan for Relay after formal completion and acceptance of the Phase-0 protocol review.

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
repository integration
        ↓
human workflow
        ↓
agent execution
        ↓
multi-agent orchestration
```

The governance model remains the product.

The detailed long-range roadmap in Build Plan v0.3 remains planning context where it does not conflict with accepted designs, accepted baselines, this projection, or later Human Authority decisions.

---

# 2. Current project state

```text
Phase 0:
COMPLETE / CLOSED

Slices 0.1–0.6:
CLOSED / ACCEPTED

Accepted Phase-0 acceptance-record SHA:
6c1b3e1098cdc6c220868aea8a492c413d3cca35

Phase-0 protocol/document synchronization:
cb9edc453442dc639a523ef301e4a258d0394daa

Phase-0 protocol review:
ACCEPTED

Human review acceptance:
RLY-P0-PROTOCOL-ACCEPT-001

Phase 1:
OPEN

Slice 1.1:
DESIGN AUTHORIZED / IN PROGRESS

Slice 1.1 implementation:
NOT AUTHORIZED
```

---

# 3. Phase-0 protocol amendments now in force

## P0-PR-01 — Registered living-projection preflight

Any authorized change surface that modifies a registered living projection MUST include the corresponding `.relay/registry.json` advancement in the same governed change.

## P0-PR-02 — Role/model visibility

Every substantive handover states:

```text
current role + model
next role + model
```

until model/provider identity becomes first-class execution provenance.

## P0-PR-03 — Design-review outcome vocabulary

Design review uses:

```text
ACCEPT
REVISE
ESCALATE
```

until a typed design-review outcome is introduced.

Implementation evaluation retains the accepted evaluator outcomes.

## P0-PR-04 — Hard-stop transition discipline

A hard-stop review may recommend the next phase but does not authorize it.

Human Authority accepted the Phase-0 review and separately opened Phase 1.

---

# 4. Repository and documentation governance

The accepted schema-v1 repository contract is:

```text
.relay/
└── registry.json
```

Project documents remain at natural repository paths.

Canonical status is a registry relationship, not a filename.

For registered living projections:

```text
changed current projection
→ new ArtifactId
→ revision N + 1
→ exact new content digest
→ canonical pointer advances
```

Historical locked/immutable records remain immutable and are superseded only through accepted lineage rules.

The observation `CommitRef` used during repository resolution is snapshot provenance; it is not rebound into a stable Slice-0.2 `ArtifactId`.

---

# 5. Phase 1 — GitHub and human-controlled project workflow

Phase 1 is OPEN.

Work remains one governed slice at a time.

## Slice 1.1 — GitHub App Integration

Current state:

```text
DESIGN AUTHORIZED
IMPLEMENTATION NOT AUTHORIZED
```

Objective:

> Connect Relay securely to selected GitHub repositories without weakening the provider-neutral Phase-0 domain model.

Design must resolve:

- GitHub App authentication;
- installation identity;
- selected-repository access discovery;
- mapping into explicit provider-neutral `RepositoryRef`;
- least-privilege permission policy;
- installation suspension/deletion and access changes;
- credentials outside repository/persistence;
- project-scoped isolation;
- failure semantics;
- immutable audit evidence;
- signed webhook handling;
- precise boundary with Slices 1.2 and 1.3.

The design record is:

```text
docs/slices/SLICE_1_1_GITHUB_APP_INTEGRATION.md
```

Implementation requires independent design review, Human Authority design acceptance, and a separate implementation authorization.

## Slice 1.2 — Repository Registration and Baseline Resolution

Resolve provider repository identity/ref to Relay project repository state and immutable commit SHAs.

This slice owns the baseline/worktree proof deferred by Slice 0.6.

NOT OPEN.

## Slice 1.3 — `.relay/` Initialization and Sync

Recognize or explicitly initialize the accepted repository contract through GitHub.

Any write permission required by this slice must be separately designed and approved.

NOT OPEN.

## Slice 1.4 — Project and Slice CRUD

Expose human-controlled project/slice mutation through accepted domain/state contracts.

NOT OPEN.

## Slice 1.5 — Board Projection

Build the first human-facing board strictly as a projection of governed state.

NOT OPEN.

## Slice 1.6 — Human Authorization and Decision Gates

Expose durable human approvals, choices, blocks, deferrals, and cancellations through product workflow.

NOT OPEN.

## Slice 1.7 — Manual Evaluation and Acceptance

Complete the human-only workflow from authorization through external/manual implementation, evaluation, acceptance, and baseline promotion.

NOT OPEN.

---

# 6. Slice 1.1 entry contract

Before Slice 1.1 implementation:

1. Phase-0 protocol review is accepted. **DONE**
2. Human Authority explicitly opens Phase 1. **DONE**
3. Slice 1.1 design starts from exact baseline `cb9edc453442dc639a523ef301e4a258d0394daa`. **DONE**
4. Independent design review occurs. **PENDING**
5. Human Authority accepts the reviewed design. **PENDING**
6. Human Authority separately authorizes implementation. **PENDING**
7. GitHub credentials remain outside repository and persisted engineering state.
8. Generic domain/repository semantics remain provider-neutral.
9. Passing CI never implies design or implementation acceptance.

---

# 7. Phase-1 hard stop — M0 validation

Phase 1 ends only after Relay can govern a real human-controlled project workflow.

Required dogfood questions:

- Does the board clarify real project state?
- Are deterministic traffic lights useful?
- Does READY versus AUTHORIZED matter in practice?
- Does durable memory reduce repeated context explanation?
- Are gates useful rather than bureaucratic?
- Can a fresh reviewer reconstruct why an accepted baseline exists?

If Relay is not useful before autonomous coding, governance should be revised before provider/agent execution expands.

---

# 8. Later roadmap

Build Plan v0.3 remains the detailed planning reference for later phases where not superseded.

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
DESIGN ONLY

Current role/model:
Slice 1.1 Architect — GPT-5.6 Sol

Next role/model:
Independent Design Reviewer — GPT-5.6 Sol

Slice 1.1 implementation:
NOT AUTHORIZED

Slice 1.2:
NOT OPEN
```

**Unblocked ≠ authorized.**
