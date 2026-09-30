# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.4 design accepted  
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
Slices 1.1–1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4 — Project and Slice CRUD:
DESIGN ACCEPTED
IMPLEMENTATION NOT AUTHORIZED
```

Accepted foundations include deterministic lifecycle/governance, durable authority and decision state, repository canonical-artifact governance, GitHub App integration, immutable repository snapshot/Baseline proof, Human-authorized repository initialization/synchronization, and the accepted Slice 1.4 Project/Slice administration design.

---

# 3. Accepted Slice 1.4 product boundary

Authority chain:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001
RLY-S14-DESIGN-EVAL-002 — ACCEPT
RLY-S14-DESIGN-ACCEPT-001 — ACCEPTED
```

Exact accepted design head:

```text
f5a678da360b96701a1f9635d3703b49dc16e779
```

The accepted design provides human-controlled definition administration without turning CRUD into an alternate governance engine.

The accepted boundary preserves:

- immutable Relay IDs and Slice project ownership;
- immutable Project repository authority;
- one audited post-v4 runtime creation path;
- auditable optimistic definition revisions/history;
- strict stale-write rejection;
- lifecycle initialization as the permanent Slice-definition freeze boundary;
- same-project acyclic parent/dependency graphs;
- conservative freeze before downstream dependency semantics become stale;
- guarded deletion only for unused/draft entities;
- lifecycle ownership of block/unblock/cancel/supersede;
- accepted Artifact/Baseline/gate ownership of artifact authority.

Slice 1.4 does not implement dependency invalidation, board projection, provider mutation, repository sync, or agent execution.

---

# 4. Current roadmap

```text
Phase 1:
OPEN

Slice 1.4:
PROJECT AND SLICE CRUD — DESIGN ACCEPTED

Slice 1.4 implementation:
NOT AUTHORIZED

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
Human design acceptance:
RLY-S14-DESIGN-ACCEPT-001 — ACCEPTED

Current role:
HUMAN AUTHORITY / ORCHESTRATOR

Next governed gate:
Explicit Slice 1.4 implementation authorization

Slice 1.4 implementation:
NOT AUTHORIZED
```

Passing design review and Human design acceptance do not themselves authorize implementation.

**Unblocked ≠ authorized.**
