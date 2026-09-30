# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.4 Design Revision 3 submitted  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

Slice 1.4 remains in architecture / contract / design. Revision 2 received
independent outcome `RLY-S14-DESIGN-EVAL-002 — REVISE`; bounded Revision 3
resolves the remaining semantic-reference and parent-use findings.

Relay continues to be built inside-out, and the governance model remains the
product.

---

# 2. Current state

```text
Phase 1:
OPEN

Slices 1.1–1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
OPEN

Design:
AUTHORIZED / REVISION 3 SUBMITTED FOR INDEPENDENT REVIEW

Implementation:
NOT AUTHORIZED
```

Authority / review chain:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001

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

Revision 3 amendment:

```text
docs/slices/SLICE_1_4_PROJECT_AND_SLICE_CRUD_REV3_AMENDMENT.md
```

---

# 3. Revision 3 direction

Revision 3 preserves the prior architecture and adds two bounded guarantees:

- guarded Slice delete checks all known typed durable semantic references to the
  target Slice, not only foreign-key ownership;
- current parent use freezes the referenced parent definition just as current
  dependency use does.

Immutable gate/lifecycle references that consume a target Slice as dependency or
supersession successor also freeze mutation until a future separately authorized
invalidation design exists.

No new relationship table, lifecycle schema, governance schema, runtime
dependency, provider change, board work, or agent work is introduced.

---

# 4. Current gate

```text
Current role:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Review input:
Revision 1 + Revision 2 + Revision 3

Human design acceptance:
NOT REACHED

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Passing CI or design-review ACCEPT is evidence only and does not authorize
implementation.

**Unblocked ≠ authorized.**
