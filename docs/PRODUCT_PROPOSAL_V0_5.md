# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.4 open  
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

Phase 0 is complete and closed.

Phase 1 accepted slices:

```text
Slice 1.1 — GitHub App Integration:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2 — Repository Registration and Baseline Resolution:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3 — .relay Initialization and Sync:
COMPLETE / ACCEPTED / CLOSED
```

Slice 1.3 canonical closure:

```text
RLY-S13-CLOSE-EVAL-001 — ACCEPT
7d266aef282c6d678e059754d2eb6a5ff297d83a
```

Accepted foundations include deterministic lifecycle/governance, durable authority and decision state, repository canonical-artifact governance, GitHub App integration, immutable repository snapshot/Baseline proof, and Human-authorized repository initialization/synchronization.

---

# 3. Product workflow

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

Opening a slice does not authorize its design or implementation.

---

# 4. Current roadmap

```text
Phase 1:
OPEN

Slice 1.4:
PROJECT AND SLICE CRUD — OPEN
DESIGN NOT AUTHORIZED
IMPLEMENTATION NOT AUTHORIZED

Slice 1.5:
BOARD PROJECTION — NOT OPEN

Slice 1.6:
HUMAN AUTHORIZATION AND DECISION GATES — NOT OPEN

Slice 1.7:
MANUAL EVALUATION AND ACCEPTANCE — NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Slice 1.4 was opened by Human Authority under:

```text
RLY-S14-OPEN-001
```

Its roadmap scope area is **Project and Slice CRUD**. Detailed requirements, architecture, contracts, persistence changes, and implementation remain subject to later explicit governance decisions.

---

# 5. Current authority state

```text
Slice 1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
OPEN

Slice 1.4 design:
NOT AUTHORIZED

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**

---

# 6. Historical proposals

Product Proposal v0.3 and v0.4 remain historical snapshots. Canonical current status is determined exclusively by `.relay/registry.json`.
