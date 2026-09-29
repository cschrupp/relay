# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.3 implementation authorized  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after acceptance and closure of Slice 1.2, completion of the Slice 1.3 design cycle through Human Authority acceptance, and explicit Slice 1.3 implementation authorization `RLY-S13-AUTH-001`.

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

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
OPEN

Slice 1.3 design:
ACCEPTED

Slice 1.3 implementation:
AUTHORIZED
```

Accepted Slice 1.3 authority chain:

```text
Opening:
RLY-S13-OPEN-001

Design authorization:
RLY-S13-DESIGN-AUTH-001

Revision 1 evaluation:
RLY-S13-DESIGN-EVAL-001 — REVISE

Revision 1 + Revision 2 evaluation:
RLY-S13-DESIGN-EVAL-002 — REVISE

Revision 1 + Revision 2 + Revision 3 evaluation:
RLY-S13-DESIGN-EVAL-003 — REVISE

Revision 1 + Revision 2 + Revision 3 + Revision 4 evaluation:
RLY-S13-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S13-DESIGN-ACCEPT-001

Exact accepted design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9

Implementation authorization:
RLY-S13-AUTH-001
```

Preferred bounded implementation role/model:

```text
IMPLEMENTATION_AGENT
GPT-5.6 Luna
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

## P0-PR-03 — Design-review outcome vocabulary

```text
ACCEPT
REVISE
ESCALATE
```

## P0-PR-04 — Transition discipline

Review acceptance and authorization are separate Human Authority decisions.

**Authorized ≠ accepted.**

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

Phase 1 is OPEN. Work remains one governed slice at a time.

## Slice 1.1 — GitHub App Integration

```text
COMPLETE / ACCEPTED / CLOSED
```

Accepted capabilities include read-only GitHub App authentication, repository-access state, provider identity, fail-closed readiness, webhooks, idempotency, and provider-neutral repository identity conversion.

## Slice 1.2 — Repository Registration and Baseline Resolution

```text
COMPLETE / ACCEPTED / CLOSED
```

Accepted capabilities include commit-pinned repository snapshot proof, exact registry/artifact verification, immutable Baseline persistence, stable Artifact provenance, and provider/local race guards.

## Slice 1.3 — `.relay/` Initialization and Sync

```text
OPEN
DESIGN ACCEPTED
IMPLEMENTATION AUTHORIZED
```

Accepted design records:

```text
Revision 1:
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC.md

Revision 2:
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV2_AMENDMENT.md

Revision 3:
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV3_AMENDMENT.md

Revision 4:
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV4_AMENDMENT.md
```

The authorized implementation must realize the accepted combined design without material redesign. Required behavior includes:

- schema-v1 repository-contract preservation;
- exact `RepositorySyncSubjectV1`;
- read-only `prepare_repository_sync(...)`;
- explicit HUMAN `RepositoryMutationAuthorization` scoped by `project_id` + exact subject;
- deterministic SQLite migration v3 for immutable repository-mutation authority;
- exact READ/WRITE installation permission profiles and repository-scoped token narrowing;
- one Git tree, one commit, one non-force default-branch ref movement;
- stale-head, identity, permission, `state_revision`, path, and post-write verification guards;
- unregistered-file adoption-or-conflict semantics;
- workflow-path mutation prohibition under the contents-only ceiling;
- no bootstrap for repositories without an existing default-branch head;
- observation-based reconciliation for indeterminate ref updates;
- `CURRENT` + `wrote_remote` success semantics;
- no automatic Baseline persistence;
- no PR flow, force push, branch creation, background worker, generic provider framework, or agent execution;
- no new runtime dependency.

All design-review findings F001–F008 are closed.

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

The full Slice 1.2 authority chain remains complete:

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

Passing CI never by itself implies technical acceptance or closure authority.

---

# 7. Slice 1.3 implementation gate

```text
Authorized design baseline:
eb6b3797fb1b317e9158444b9c9dbe469b2ee313

Revision 1:
433910d0b2df7f0f0a3104cbe97f6df5ebba609a

Revision 2:
6070b04ca5b38bd5c4687bb0ec4799f4f782e355

Revision 3:
8e8ab70cf8c9b52d628b0b658179c1fe287c93ea

Revision 4 / exact accepted design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9

Independent combined review:
RLY-S13-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S13-DESIGN-ACCEPT-001

Implementation authorization:
RLY-S13-AUTH-001
```

Current gate state:

1. Slice 1.3 opened. **DONE**
2. Slice 1.3 design authorized. **DONE**
3. Revisions 1–4 designed and independently reviewed. **DONE**
4. Combined Revision 1 + 2 + 3 + 4 independent review. **DONE — ACCEPT**
5. Human design acceptance. **DONE**
6. Separate implementation authorization. **DONE — AUTHORIZED**
7. Bounded implementation. **AUTHORIZED / PENDING**
8. Independent implementation evaluation. **NOT REACHED**
9. Human technical acceptance. **NOT REACHED**

Implementation completion does not imply acceptance.

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

Slice 1.3 architecture / contract / design:
ACCEPTED

Slice 1.3 implementation:
AUTHORIZED

Current governed role:
IMPLEMENTATION_AGENT — GPT-5.6 Luna preferred

Next governed gate after implementation:
INDEPENDENT_EVALUATOR — GPT-5.6 Sol

Slice 1.4:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Authorized ≠ accepted.**
