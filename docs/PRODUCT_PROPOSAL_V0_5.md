# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.3 implementation authorized  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** September 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

Its central thesis is:

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs how engineering work is defined, authorized, handed over, implemented, evaluated, accepted, and remembered. The board is a human-readable projection of governed state, not the source of truth.

---

# 2. Core differentiation

Relay differentiates through durable engineering memory, explicit role/authority separation, governed handovers, independent evaluation, exact baselines/provenance, controlled research/experiments, and Human Authority at strategic boundaries.

---

# 3. Accepted technical foundation

Phase 0 is complete and closed. Slice 1.1 and Slice 1.2 are complete, accepted, and closed.

Accepted foundations include deterministic lifecycle/governance, authorization/human-decision persistence, repository-side canonical artifact governance, GitHub App read integration, exact GitHub commit/tree/blob snapshot proof, immutable Baseline resolution, stable Artifact provenance, and provider/local race guards.

The accepted repository representation remains deliberately minimal:

```text
ordinary engineering documents at natural repository paths
+
.relay/registry.json
```

Runtime/cloud state and credentials remain separate from repository authority.

---

# 4. Provider and repository authority

Relay distinguishes provider-observed repository/access state, repository-authoritative engineering artifacts, runtime/cloud operational state, and derived UI/search/agent-context projections.

Slice 1.3 has an independently reviewed, Human-accepted design and explicit implementation authorization.

```text
Independent combined design evaluation:
RLY-S13-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S13-DESIGN-ACCEPT-001

Implementation authorization:
RLY-S13-AUTH-001

Exact accepted design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
```

---

# 5. Product workflow

The governed workflow remains:

```text
problem / objective
      ↓
research when needed
      ↓
architecture / contract
      ↓
planning
      ↓
readiness evaluation
      ↓
explicit authorization
      ↓
implementation
      ↓
independent evaluation
      ↓
rework / escalation / acceptance
      ↓
accepted baseline
      ↓
durable engineering memory
```

Repository side-effect authority remains distinct from lifecycle handover authority.

---

# 6. Model and provider philosophy

Relay project semantics do not depend on one model vendor. Role authority belongs to Relay contracts, not model identity.

Working convention:

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

---

# 7. Current roadmap

```text
Phase 0:
COMPLETE / CLOSED

Phase 1:
OPEN

Slice 1.1:
GITHUB APP INTEGRATION — COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
REPOSITORY REGISTRATION AND BASELINE RESOLUTION — COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
.relay INITIALIZATION AND SYNC — OPEN

Slice 1.3 design:
ACCEPTED

Slice 1.3 implementation:
AUTHORIZED

Slice 1.4:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

---

# 8. Slice 1.3 accepted and authorized product boundary

Accepted design records:

```text
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC.md
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV2_AMENDMENT.md
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV3_AMENDMENT.md
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV4_AMENDMENT.md
```

Authorized implementation capability remains deliberately narrow:

> Given authoritative Relay project/repository identity, an exact expected default-branch/base commit, an exact target schema-v1 repository contract, and explicit Human Authority over the exact prepared mutation subject, Relay may recognize an already-current target or commit initialization/synchronization to the existing default branch as one atomic Git commit, subject to exact permission, identity, transition, race, path-preservation, and post-write verification guards.

Required rules include:

- `.relay/registry.json` remains repository-side authority and schema v1 remains unchanged;
- read-only installations remain valid for read workflows;
- accepted WRITE profile adds only `contents:write` above metadata read;
- read operations remain read-token scoped;
- `prepare_repository_sync(...)` computes exact `RepositorySyncSubjectV1` before write capability is used;
- any non-no-op mutation requires immutable HUMAN `RepositoryMutationAuthorization` scoped by `project_id` + exact subject;
- mutation authority contains no fabricated `BaselineId`, `GateId`, or `SliceId`;
- execution recomputes exact subject and rechecks authority before WRITE-token minting and before ref visibility;
- deterministic SQLite migration v3 persists immutable repository-mutation authority using project + subject indexing only;
- repository mutation uses GitHub Git Data as one target tree, one commit, and one non-force update of the existing default-branch ref;
- concurrent branch movement conflicts rather than overwriting/rebasing;
- existing unregistered files use adoption-or-conflict semantics;
- `.github/workflows/**` content/mode mutation is outside the permission ceiling;
- repositories without an existing default-branch head are not bootstrapped;
- indeterminate ref-update outcomes are reconciled by observation, never hidden write retry;
- invalid existing `.relay` state is never automatically repaired;
- successful state is `CURRENT`, with `wrote_remote` distinguishing no-op from mutation;
- synchronization does not certify or persist its own Relay Baseline;
- no PR permission, branch creation, force push, admin bypass, background worker, generic provider framework, local Git/worktree, or agent execution is introduced;
- no new runtime dependency is introduced without explicit architecture escalation.

All independent design-review findings F001–F008 are closed.

Implementation authority does not imply technical acceptance. The completed candidate must undergo independent implementation evaluation and later Human technical acceptance.

---

# 9. Current authority state

```text
Slice 1.3 opening:
RLY-S13-OPEN-001

Slice 1.3 design authorization:
RLY-S13-DESIGN-AUTH-001

Slice 1.3 independent combined design evaluation:
RLY-S13-DESIGN-EVAL-004 — ACCEPT

Slice 1.3 Human design acceptance:
RLY-S13-DESIGN-ACCEPT-001

Slice 1.3 implementation authorization:
RLY-S13-AUTH-001

Exact accepted design:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9

Slice 1.3:
OPEN

Slice 1.3 design:
ACCEPTED

Slice 1.3 implementation:
AUTHORIZED

Preferred implementation role/model:
IMPLEMENTATION_AGENT — GPT-5.6 Luna

Slice 1.4:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Authorized ≠ accepted.**

---

# 10. Historical proposals

Product Proposal v0.3 and v0.4 remain historical planning/current-truth snapshots from earlier project states. Canonical current status is determined exclusively by `.relay/registry.json`.
