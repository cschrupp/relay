# Relay — Build Plan and Development Roadmap

**Version:** 0.4  
**Status:** Current living implementation plan  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.3 at `docs/BUILD_PLAN.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.4*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan for Relay after formal completion of Phase 0.

The detailed long-range roadmap in Build Plan v0.3 remains useful planning context where it does not conflict with accepted designs, accepted baselines, this projection, or later Human Authority decisions.

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

---

# 2. Current project state

```text
Phase 0:
COMPLETE / CLOSED

Slices 0.1–0.6:
CLOSED / ACCEPTED

Accepted Phase-0 acceptance-record SHA:
6c1b3e1098cdc6c220868aea8a492c413d3cca35

Phase-0 protocol review:
SUBMITTED / PENDING HUMAN ACCEPTANCE

Phase 1:
NOT AUTHORIZED
```

Phase 0 established:

- the engineering foundation and quality gates;
- provider-neutral domain objects;
- deterministic lifecycle semantics;
- deterministic handover gates and traffic lights;
- explicit readiness / authority / autonomy separation;
- durable persistence, event history, migrations, and restart integrity;
- authorization and human-decision records;
- schema-v1 `.relay/registry.json`;
- canonical living projections and immutable/lockable historical records;
- raw-byte content integrity and repository-path safety;
- explicit repository/cloud authority boundaries.

---

# 3. Phase-0 protocol review result

The hard-stop review is recorded in:

```text
docs/reviews/PHASE_0_PROTOCOL_REVIEW.md
```

Reviewer outcome:

```text
ACCEPT WITH PROCESS AMENDMENTS
```

The seven required hard-stop questions all pass.

No Phase-0 architectural rework is required before Phase 1.

The review identified four process amendments for subsequent work:

## P0-PR-01 — Registered living-projection preflight

Any authorized change surface that modifies a registered living projection MUST include the corresponding `.relay/registry.json` advancement in the same governed change.

This prevents a finalization instruction from simultaneously requiring new document bytes and forbidding the registry update needed to validate them.

## P0-PR-02 — Role/model visibility

Every substantive handover should state:

```text
current role + model
next role + model
```

until model/provider identity becomes first-class execution provenance in later phases.

## P0-PR-03 — Review outcome vocabulary

Design review corrections should use an explicit review vocabulary and must not be confused with implementation acceptance.

Until a typed design-review outcome exists, Relay development will use:

```text
ACCEPT
REVISE
ESCALATE
```

for design review, while implementation evaluation retains its accepted evaluator outcomes.

## P0-PR-04 — Hard-stop transition discipline

A hard-stop review may recommend the next phase but does not itself authorize it.

The next phase requires a fresh Human Authority decision made after the review is available.

---

# 4. Repository and documentation governance now in force

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

Historical locked/immutable records remain immutable and are superseded only through the accepted lineage rules.

The observation `CommitRef` used during repository resolution is snapshot provenance; it is not rebound into a stable Slice-0.2 `ArtifactId`.

---

# 5. Phase 1 — GitHub and human-controlled project workflow

Phase 1 begins only after Human Authority accepts the Phase-0 protocol review and explicitly opens the phase.

The first Phase-1 action is **design**, not implementation.

## Slice 1.1 — GitHub App Integration

Objective:

> Connect Relay securely to selected GitHub repositories without weakening the provider-neutral Phase-0 domain model.

Design must resolve at minimum:

- GitHub App installation identity;
- selected repository identity mapping to `RepositoryRef`;
- least-privilege permissions;
- read/content permission requirements;
- installation revocation and stale authorization;
- credential storage outside the repository;
- tenant/project isolation;
- failure semantics and audit evidence;
- boundary between GitHub integration and generic repository semantics.

Out of scope for Slice 1.1:

- autonomous coding-agent execution;
- autonomous branch creation;
- merging;
- PR review agents;
- model-provider integration;
- Phase-2 capability.

## Slice 1.2 — Repository Registration and Baseline Resolution

Resolve repository refs to immutable SHAs and prove the baseline/worktree boundary deferred by Slice 0.6.

## Slice 1.3 — `.relay/` Initialization and Sync

Recognize or explicitly initialize the accepted repository contract. Initialization must be deterministic, reviewable, and isolated in auditable changes.

## Slice 1.4 — Project and Slice CRUD

Expose human-controlled project/slice mutation through the accepted domain/state contracts.

## Slice 1.5 — Board Projection

Build the first human-facing board strictly as a projection of governed state.

## Slice 1.6 — Human Authorization and Decision Gates

Expose durable human approvals, choices, blocks, deferrals, and cancellations through product workflow.

## Slice 1.7 — Manual Evaluation and Acceptance

Complete the human-only loop from authorization through external/manual implementation, evaluation, acceptance, and baseline promotion.

---

# 6. Phase-1 entry contract

Before Slice 1.1 implementation:

1. Phase-0 protocol review is accepted by Human Authority.
2. Human Authority explicitly opens Phase 1.
3. Slice 1.1 design starts from an exact post-review baseline SHA.
4. Independent design review occurs before implementation authorization.
5. No GitHub credentials are written to repository files or ordinary engineering-state tables.
6. Generic domain/repository semantics remain provider-neutral.
7. Any provider-specific data is isolated inside the GitHub integration boundary.
8. Passing CI does not imply acceptance.
9. Phase-1 work remains one governed slice at a time.

---

# 7. Phase-1 hard stop — M0 validation

Phase 1 should end only after Relay can govern a real human-controlled project workflow.

The dogfood questions remain:

- Does the board clarify real project state?
- Are deterministic traffic lights useful?
- Does READY versus AUTHORIZED matter in practice?
- Does durable memory reduce repeated context explanation?
- Are gates useful rather than bureaucratic?
- Can a fresh reviewer reconstruct why an accepted baseline exists?

If Relay is not useful before autonomous coding, the governance abstraction should be revised before provider/agent execution expands.

---

# 8. Later roadmap

Build Plan v0.3 remains the detailed planning reference for Phases 2+ where it is not superseded by later accepted decisions.

The strategic sequence remains:

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

No later roadmap entry is authorization.

---

# 9. Next authorization boundary

Current gate:

```text
PHASE-0 PROTOCOL REVIEW
PENDING HUMAN ACCEPTANCE
```

If accepted, Human Authority may separately authorize:

```text
Phase 1:
OPEN

Slice 1.1:
DESIGN ONLY
```

Implementation remains separately gated after independent design review.

**Unblocked ≠ authorized.**
