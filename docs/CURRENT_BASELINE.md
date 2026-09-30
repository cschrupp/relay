# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.4 design accepted / implementation not authorized  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted foundation

```text
Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
COMPLETE / ACCEPTED / CLOSED
```

Slice 1.3 canonical closure:

```text
RLY-S13-CLOSE-EVAL-001 — ACCEPT
7d266aef282c6d678e059754d2eb6a5ff297d83a
```

---

# 2. Slice 1.4 authority and accepted design

```text
Opening:
RLY-S14-OPEN-001

Design authorization:
RLY-S14-DESIGN-AUTH-001

Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Design Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Independent Revision 1 review:
RLY-S14-DESIGN-EVAL-001 — REVISE

Revision 2 / exact reviewed design head:
f5a678da360b96701a1f9635d3703b49dc16e779

Independent combined review:
RLY-S14-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S14-DESIGN-ACCEPT-001 — ACCEPTED
```

Current gate:

```text
Slice 1.4:
OPEN

Slice 1.4 design:
ACCEPTED

Current role:
HUMAN AUTHORITY / ORCHESTRATOR

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

---

# 3. Accepted Slice 1.4 design summary

The accepted combined contract:

- leaves accepted `Project` and `Slice` domain schemas unchanged;
- introduces definition revisions/history through migration v4;
- makes the administration service the only post-v4 product/runtime Project/Slice creation path;
- requires strict optimistic compare-and-swap before exact-target or material updates;
- keeps Project repository authority immutable;
- validates same-project parent/dependency graphs and cycles;
- freezes Slice definitions once lifecycle is initialized;
- freezes definitions consumed by downstream dependencies;
- guards physical delete to unused current entities and preserves tombstones/history;
- explicitly checks destructive-delete blockers;
- routes block/unblock/cancel/supersede through accepted lifecycle/governance;
- adds no runtime dependency;
- performs no board, provider, repository-sync, or agent work.

---

# 4. Protocol rules in force

```text
registered living-projection change
→ registry advancement in same governed change

architecture / design / review / evaluation
→ GPT-5.6 Sol

bounded implementation / rework / finalization
→ GPT-5.6 Luna preferred
```

Exact authority boundaries and exact SHAs remain controlling.

**Unblocked ≠ authorized.**
