# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.4 Design Revision 3 submitted for independent review  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted foundation

```text
Slices 1.1–1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3 closure:
RLY-S13-CLOSE-EVAL-001 — ACCEPT
7d266aef282c6d678e059754d2eb6a5ff297d83a
```

---

# 2. Slice 1.4 lineage

```text
Opening:
RLY-S14-OPEN-001

Design authorization:
RLY-S14-DESIGN-AUTH-001

Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording canonical commit / design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710
RLY-S14-DESIGN-EVAL-001 — REVISE

Revision 2:
f5a678da360b96701a1f9635d3703b49dc16e779
RLY-S14-DESIGN-EVAL-002 — REVISE
```

Revision 3:

```text
docs/slices/SLICE_1_4_PROJECT_AND_SLICE_CRUD_REV3_AMENDMENT.md
SUBMITTED FOR INDEPENDENT REVIEW
```

---

# 3. Combined design summary

Revision 1–3:

- preserves accepted immutable `Project` / `Slice` domain schemas;
- adds definition revision/history through SQLite migration v4;
- requires audited HUMAN product/runtime creation through the administration
  service;
- uses strict optimistic compare-and-swap;
- freezes Slice definition mutation once lifecycle exists;
- freezes Slice definitions consumed as current parent/dependency or immutable
  gate/lifecycle dependency/successor;
- permits physical delete only for ungoverned, durably unreferenced current
  entities while retaining immutable definition history/tombstones;
- performs semantic reference checks through typed persisted records;
- adds no runtime dependency and no board/provider/agent work.

---

# 4. Current gate

```text
Slice 1.4:
OPEN

Design:
AUTHORIZED / REVISION 3 REVIEW PENDING

Current role:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Human design acceptance:
NOT REACHED

Implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
