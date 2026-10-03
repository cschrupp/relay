# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.5 closed; Slice 1.6 not open
**Document class:** Living canonical projection
**Canonical key:** `build-plan`
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** October 2026

---

# 1. Current project state

```text
Phase 0:
COMPLETE / CLOSED

Phase 1:
OPEN

Slices 1.1–1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE / ACCEPTED

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Finalization / closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Agent execution:
NOT AUTHORIZED
```

# 2. Slice 1.5 authority

Human opening authority:

```text
RLY-S15-OPEN-001
```

Human design authorization:

```text
RLY-S15-DESIGN-AUTH-001
```

Human design acceptance:

```text
RLY-S15-DESIGN-ACCEPT-001 — ACCEPTED
```

Human-authorized design subject baseline:

```text
359cd61f0c05815390a6822739c0c68d3f020c32
```

Canonical roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

Authorized design role:

```text
Slice 1.5 Board Projection Architect — GPT-5.6 Sol
```

The design must preserve the board as a deterministic, read-only projection of governed state. Slice 1.5 does not own human authorization mutations, new lifecycle/governance semantics, repository/provider mutations, or agent execution.

The exact accepted technical candidate is:

```text
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
```

The candidate was independently evaluated as ACCEPT under `RLY-S15-EVAL-001` and technically accepted under `RLY-S15-ACCEPT-001`.

# 3. Accepted foundation and preserved Slice 1.4 lineage

Slices 1.1–1.4 remain complete, accepted, and closed.

```text
Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Accepted Revision 2 design head:
f5a678da360b96701a1f9635d3703b49dc16e779

Implementation authorization:
RLY-S14-AUTH-001 — AUTHORIZED
```

Slice 1.4 accepted technical result:

```text
ae582c52ec4a6451b54e9d6e018932e93e72e013
```

Slice 1.4 closure evaluation:

```text
RLY-S14-CLOSE-EVAL-001 — ACCEPT
```

# 4. Slice 1.5 implementation and closure gates

The accepted design and bounded implementation are complete. Independent closure evaluation accepted the exact closure-ready candidate under `RLY-S15-CLOSE-EVAL-001`.

Current governed sequence:

```text
Accepted technical candidate: ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
→ independent implementation evaluation: ACCEPT
→ Human technical acceptance: ACCEPTED
→ finalization / closure authorization: RLY-S15-CLOSE-AUTH-001
→ independent closure evaluation: RLY-S15-CLOSE-EVAL-001 — ACCEPT
→ Slice 1.5: COMPLETE / ACCEPTED / CLOSED
```

Passing CI is evidence; it does not constitute closure acceptance.

# 5. Current authority boundary

```text
Current finalization gate:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE / ACCEPTED

Finalization / closure authorization:
AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
