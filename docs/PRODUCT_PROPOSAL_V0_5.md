# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slices 1.1–1.4 accepted and closed  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** October 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs how engineering work is defined, authorized, handed over, implemented, evaluated, accepted, closed, and remembered.

# 2. Accepted technical foundation

```text
Slices 1.1–1.4:
COMPLETE / ACCEPTED / CLOSED
```

Slice 1.4 adds human-controlled Project/Slice definition administration while preserving the existing lifecycle, governance, repository, and provider authority boundaries.

# 3. Accepted Slice 1.4 capability

The accepted and closed capability includes:

- immutable Relay identity and Project repository authority;
- migration v4 definition revisions and append-only history;
- one audited post-v4 runtime Project/Slice creation path;
- strict revision compare-and-swap;
- same-Project acyclic parent/dependency graphs;
- conservative lifecycle/gate/downstream definition freezes;
- guarded deletion with tombstones and retired identity;
- fail-closed durable-state integrity verification;
- no new runtime dependency.

Exact accepted technical result:

```text
ae582c52ec4a6451b54e9d6e018932e93e72e013
```

Closure evaluation:

```text
RLY-S14-CLOSE-EVAL-001 — ACCEPT
```

# 4. Current roadmap

```text
Phase 1:
OPEN

Slice 1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
BOARD PROJECTION — NOT OPEN / NOT AUTHORIZED

Slice 1.6:
HUMAN AUTHORIZATION AND DECISION GATES — NOT OPEN

Slice 1.7:
MANUAL EVALUATION AND ACCEPTANCE — NOT OPEN

Agent execution:
NOT AUTHORIZED
```

# 5. Authority boundary

The next Slice may begin only through a separate Human Authority opening/design decision.

Closure of Slice 1.4 grants no board, next-slice, or agent-execution authority.

**Unblocked ≠ authorized.**
