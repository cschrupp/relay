# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.3 accepted, closure evaluation pending  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** September 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs how engineering work is defined, authorized, handed over, implemented, evaluated, accepted, and remembered. The board is a human-readable projection of governed state, not the source of truth.

---

# 2. Core differentiation

Relay differentiates through durable engineering memory, explicit role/authority separation, governed handovers, independent evaluation, exact baselines/provenance, controlled research/experiments, and Human Authority at strategic boundaries.

---

# 3. Accepted technical foundation

Phase 0 is complete and closed. Slice 1.1 and Slice 1.2 are complete, accepted, and closed. Slice 1.3 is technically complete and accepted; its independent closure audit is the remaining gate before any Slice 1.4 opening becomes effective.

Accepted foundations now include deterministic lifecycle/governance, authorization/human-decision persistence, repository-side canonical artifact governance, GitHub App integration, exact GitHub commit/tree/blob snapshot proof, immutable Baseline resolution, stable Artifact provenance, provider/local race guards, and Human-authorized repository initialization/synchronization.

The accepted repository representation remains deliberately minimal:

```text
ordinary engineering documents at natural repository paths
+
.relay/registry.json
```

Runtime/cloud state and credentials remain separate from repository authority.

---

# 4. Provider and repository authority

`Project.primary_repository` remains the durable Relay project-repository authority.

Slice 1.3 adds a distinct remote side-effect authority:

```text
read-only preparation
→ exact RepositorySyncSubjectV1
→ HUMAN RepositoryMutationAuthorization
→ fresh execution guards
→ one non-force default-branch commit
→ exact post-write proof
```

Repository-mutation authority remains orthogonal to lifecycle/handover authority and never certifies a Relay Baseline.

---

# 5. Product workflow

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

Review, Human acceptance, closure, and next-slice opening remain separate transitions.

---

# 6. Model and provider philosophy

Relay project semantics do not depend on one model vendor. Role authority belongs to Relay contracts, not model identity.

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
.relay INITIALIZATION AND SYNC — COMPLETE / ACCEPTED
CLOSURE EVALUATION PENDING

Slice 1.4:
PROJECT AND SLICE CRUD — NOT OPEN

Slice 1.5:
BOARD PROJECTION — NOT OPEN

Slice 1.6:
HUMAN AUTHORIZATION AND DECISION GATES — NOT OPEN

Slice 1.7:
MANUAL EVALUATION AND ACCEPTANCE — NOT OPEN

Agent execution:
NOT AUTHORIZED
```

---

# 8. Slice 1.3 accepted product boundary

Accepted design:

```text
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
```

Accepted technical result:

```text
9b5166d1e95aefeb177d30c29f943f45a591ea05
```

Independent implementation evaluation:

```text
RLY-S13-EVAL-002 — ACCEPT
```

Human technical acceptance:

```text
RLY-S13-ACCEPT-001
```

Acceptance/finalization head:

```text
5164f1a8532e1ca05007531cdfd1f5084755092a
```

Promoted-main CI:

```text
36612444758 — SUCCESS
```

The accepted capability is deliberately narrow: exact read-only preparation, exact HUMAN mutation authority, contents-only write permission, one-tree/one-commit/non-force ref visibility, fail-closed races, exact post-write proof, target-state idempotency, and no automatic Baseline persistence.

Slice 1.3 does not add PR orchestration, branch creation, force pushes, ruleset bypass, background synchronization, generic provider abstraction, local Git/worktree management, Project/Slice CRUD, board projection, or agent execution.

---

# 9. Current authority state

```text
Slice 1.3:
COMPLETE / ACCEPTED
CLOSURE EVALUATION PENDING

Slice 1.4:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

The next valid gate is independent Slice 1.3 closure evaluation.

**Unblocked ≠ authorized.**

---

# 10. Historical proposals

Product Proposal v0.3 and v0.4 remain historical snapshots. Canonical current status is determined exclusively by `.relay/registry.json`.
