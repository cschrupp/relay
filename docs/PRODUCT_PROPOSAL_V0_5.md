# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.4 finalized; closure evaluation pending  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** October 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs how engineering work is defined, authorized, handed over, implemented, evaluated, accepted, and remembered. The board is a projection of governed state, not the source of truth.

# 2. Accepted technical foundation

```text
Slices 1.1–1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4 — Project and Slice CRUD:
DESIGN ACCEPTED
IMPLEMENTATION ACCEPTED
FINALIZED
CLOSURE EVALUATION PENDING
```

Slice 1.4 adds auditable human-controlled Project/Slice definition administration without creating an alternate lifecycle or governance engine.

# 3. Accepted Slice 1.4 boundary

The accepted capability preserves:

- immutable Relay identity and ownership;
- immutable Project repository authority;
- one audited post-v4 runtime creation path;
- append-only definition history and strict optimistic concurrency;
- migration-only `SEED` and runtime `CREATE`;
- lifecycle/gate/downstream freeze boundaries;
- same-Project acyclic Slice graphs;
- guarded deletion of unused definitions only;
- fail-closed durable-state integrity checking;
- lifecycle ownership of block/unblock/cancel/supersede;
- existing Artifact/Baseline/gate authority.

Exact accepted technical result:

```text
ae582c52ec4a6451b54e9d6e018932e93e72e013
```

# 4. Current roadmap

```text
Phase 1:
OPEN

Slice 1.4:
FINALIZED — CLOSURE EVALUATION PENDING

Slice 1.5:
BOARD PROJECTION — NOT OPEN

Slice 1.6:
HUMAN AUTHORIZATION AND DECISION GATES — NOT OPEN

Slice 1.7:
MANUAL EVALUATION AND ACCEPTANCE — NOT OPEN

Agent execution:
NOT AUTHORIZED
```

# 5. Authority boundary

```text
Independent implementation evaluation:
RLY-S14-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S14-ACCEPT-001 — ACCEPTED

Finalization / closure authorization:
RLY-S14-CLOSE-AUTH-001 — AUTHORIZED

Next governed gate:
Independent closure evaluation
```

Closure authority does not authorize Slice 1.5 or any new product implementation.

**Unblocked ≠ authorized.**
