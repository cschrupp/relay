# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.4 design authorized  
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

Accepted domain semantics already define `Project` as an engineering project with one primary repository and `Slice` as a bounded intended engineering change with no workflow state.

---

# 3. Slice 1.4 product boundary

```text
Slice 1.4 — Project and Slice CRUD
OPEN
DESIGN AUTHORIZED
IMPLEMENTATION NOT AUTHORIZED
```

Authority:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001
```

Authorized design baseline:

```text
670996ec43d77526adb0ea540c81a57d6e83453b
```

The design must make Project and Slice administration usable without weakening Relay’s authority model. CRUD semantics must not become an alternate path for lifecycle transitions, authority changes, Baseline rewriting, repository mutation, or historical erasure.

Minimum design questions include:

- immutable identity and ownership;
- safe mutable metadata;
- Slice parent/dependency integrity;
- how deletion interacts with durable history and foreign-key references;
- deterministic stale-write and idempotency semantics;
- the minimum persistence evolution needed to support safe mutation.

---

# 4. Current roadmap

```text
Phase 1:
OPEN

Slice 1.4:
PROJECT AND SLICE CRUD — DESIGN AUTHORIZED

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
Current governed role:
ARCHITECT / CONTRACT DESIGNER — GPT-5.6 Sol

Next governed gate:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Independent design-review acceptance, if achieved, still requires a separate Human design-acceptance decision before implementation can be authorized.

**Unblocked ≠ authorized.**
