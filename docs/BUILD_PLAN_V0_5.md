# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.4 Design Revision 2 submitted  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after Slice 1.4 Design Revision 1 received
independent outcome `RLY-S14-DESIGN-EVAL-001 — REVISE` and bounded Revision 2
was prepared to resolve its four findings.

Relay continues to be built inside-out:

```text
deterministic domain contracts
        ↓
lifecycle / governance
        ↓
persistence / auditability
        ↓
repository contract
        ↓
provider repository integration
        ↓
human workflow
        ↓
agent execution
        ↓
multi-agent orchestration
```

The governance model remains the product.

---

# 2. Current project state

```text
Phase 0:
COMPLETE / CLOSED

Phase 1:
OPEN

Slices 1.1–1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
OPEN

Slice 1.4 design:
AUTHORIZED / REVISION 2 SUBMITTED FOR INDEPENDENT REVIEW

Slice 1.4 implementation:
NOT AUTHORIZED
```

Authority/provenance chain:

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

Revision 2 amendment:

```text
docs/slices/SLICE_1_4_PROJECT_AND_SLICE_CRUD_REV2_AMENDMENT.md
```

---

# 3. Revision 2 design direction

Revision 2 preserves Revision 1 architecture and tightens four boundaries:

- exact authority-lineage terminology is corrected without changing Human
  Authority;
- post-v4 Project/Slice runtime creation has one audited product mutation path:
  the Slice 1.4 administration service;
- expected-definition-revision comparison is strict even for exact-target
  updates;
- Slice definition mutation ends once lifecycle is initialized, avoiding a new
  lifecycle/definition-revision binding.

It also makes destructive delete blockers explicit rather than relying on a
catch-all or database cascade.

No lifecycle schema redesign, command-id subsystem, provider change, board work,
or agent work is introduced.

---

# 4. Process rules in force

Registered living-projection changes advance `.relay/registry.json` in the same
governed change.

Role/model convention:

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

Opening, design authorization, independent review, Human design acceptance,
implementation authorization, technical acceptance, and closure remain distinct.

**Unblocked ≠ authorized.**

---

# 5. Current gate

```text
Current governed role:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Review input:
Slice 1.4 Revision 1 + Revision 2 Amendment

Design authority:
RLY-S14-DESIGN-AUTH-001

Human design acceptance:
NOT REACHED

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

The reviewer must return ACCEPT, REVISE, or ESCALATE and stop after the review.
