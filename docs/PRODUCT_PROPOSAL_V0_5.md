# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.4 Revision 2 under independent review  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** September 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs how engineering work is defined, authorized, handed over,
implemented, evaluated, accepted, and remembered. The board is a human-readable
projection of governed state, not the source of truth.

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

Accepted foundations include deterministic lifecycle/governance, durable
authority and decision state, repository canonical-artifact governance, GitHub
App integration, immutable repository snapshot/Baseline proof, and
Human-authorized repository initialization/synchronization.

Accepted domain semantics keep `Project` and `Slice` definition data separate
from Slice lifecycle/governance state.

---

# 3. Slice 1.4 product boundary

```text
Slice 1.4 — Project and Slice CRUD
OPEN

Design:
AUTHORIZED / REVISION 2 SUBMITTED FOR INDEPENDENT REVIEW

Implementation:
NOT AUTHORIZED
```

Authority lineage:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001

Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Independent review:
RLY-S14-DESIGN-EVAL-001 — REVISE
```

Revision 2 preserves human-controlled definition administration and adds four
tightened guarantees:

- product/runtime creation cannot bypass the audited administration service;
- stale definition revisions never succeed merely because payloads converge;
- lifecycle initialization freezes subsequent Slice-definition mutation;
- exact authority lineage is unambiguous.

Guarded physical delete remains limited to unused current entities and keeps
append-only retired-identity history.

---

# 4. Current roadmap

```text
Phase 1:
OPEN

Slice 1.4:
PROJECT AND SLICE CRUD — DESIGN REVISION 2 UNDER REVIEW

Slice 1.5:
BOARD PROJECTION — NOT OPEN

Slice 1.6:
HUMAN AUTHORIZATION AND DECISION GATES — NOT OPEN

Slice 1.7:
MANUAL EVALUATION AND ACCEPTANCE — NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Slice 1.4 still does not implement dependency invalidation, board projection,
provider mutation, repository sync, or agent execution.

---

# 5. Current authority state

```text
Current role:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Review input:
Revision 1 + Revision 2 Amendment

Human design acceptance:
NOT REACHED

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Passing CI or an independent design-review ACCEPT does not authorize
implementation.

**Unblocked ≠ authorized.**
