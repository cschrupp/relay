# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.4 design under independent review  
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

# 2. Accepted technical foundation

```text
Slice 1.1 — GitHub App Integration:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2 — Repository Registration and Baseline Resolution:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3 — .relay Initialization and Sync:
COMPLETE / ACCEPTED / CLOSED
```

Accepted foundations include deterministic lifecycle/governance, durable authority and decision state, repository canonical-artifact governance, GitHub App integration, immutable repository snapshot/Baseline proof, and Human-authorized repository initialization/synchronization.

Accepted domain semantics define `Project` as an engineering project with one primary repository and `Slice` as a bounded intended engineering change with no workflow state.

---

# 3. Slice 1.4 product boundary

```text
Slice 1.4 — Project and Slice CRUD
OPEN

Design:
AUTHORIZED / REVISION 1 SUBMITTED FOR INDEPENDENT REVIEW

Implementation:
NOT AUTHORIZED
```

Authority:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001
```

Exact authorized design baseline:

```text
1eaece23e31d831bfd2b27e55a898df389cc45fc
```

Revision 1 defines human-controlled definition administration without turning CRUD into an alternate governance engine.

The proposed boundary preserves:

- immutable Relay IDs and Slice project ownership;
- immutable Project repository authority;
- auditable, optimistic definition revisions;
- bounded early Slice definition editing;
- same-project acyclic parent/dependency graphs;
- conservative freeze before stale downstream authority can arise;
- guarded deletion only for unused/draft entities;
- lifecycle ownership of block/unblock/cancel/supersede;
- existing Artifact/Baseline/gate ownership of artifact authority.

The design intentionally does not implement dependency invalidation, board projection, provider mutation, or agent execution.

---

# 4. Current roadmap

```text
Phase 1:
OPEN

Slice 1.4:
PROJECT AND SLICE CRUD — DESIGN REVISION 1 UNDER REVIEW

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

# 5. Current authority state

```text
Current role:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Design review outcome:
PENDING

Human design acceptance:
NOT REACHED

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Passing CI or independent-review acceptance does not authorize implementation.

**Unblocked ≠ authorized.**
