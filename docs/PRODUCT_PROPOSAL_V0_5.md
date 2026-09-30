# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.4 Revision 3 under independent review  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** September 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs how engineering work is defined, authorized, handed over,
implemented, evaluated, accepted, and remembered. The board is a projection of
governed state, not the source of truth.

---

# 2. Accepted foundation

Slices 1.1–1.3 are COMPLETE / ACCEPTED / CLOSED.

Slice 1.4 remains design-only under `RLY-S14-DESIGN-AUTH-001`.

```text
Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710
RLY-S14-DESIGN-EVAL-001 — REVISE

Revision 2:
f5a678da360b96701a1f9635d3703b49dc16e779
RLY-S14-DESIGN-EVAL-002 — REVISE
```

---

# 3. Slice 1.4 product boundary

The combined Revision 1–3 design provides human-controlled Project/Slice
definition administration while preserving lifecycle/governance authority.

Revision 3 closes the remaining reference-integrity boundary:

- a Slice physically disappears from current state only when no accepted durable
  workflow/authority record semantically retains that SliceId outside its own
  definition history;
- parent use and dependency use both conservatively freeze the referenced Slice
  definition;
- immutable gate/lifecycle consumption likewise freezes the target when no exact
  definition revision is bound into that record.

This remains Minimum Sufficient Architecture for the M0 human workflow: typed
record scans are preferred over a new normalized relationship/index subsystem.

---

# 4. Current roadmap

```text
Slice 1.4:
PROJECT AND SLICE CRUD — DESIGN REVISION 3 UNDER REVIEW

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

Human design acceptance:
NOT REACHED

Slice 1.4 implementation:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
