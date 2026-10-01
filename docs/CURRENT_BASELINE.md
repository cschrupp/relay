# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.4 technical result accepted; finalization/closure pending separate authorization
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** October 2026

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

# 2. Slice 1.4 authority, design, and accepted technical result

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

Independent combined design review:
RLY-S14-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S14-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authorization:
RLY-S14-AUTH-001 — AUTHORIZED

Canonical rework baseline:
dfe6c20c8f65b42fe69b7d315956a91d2a29487c

Prior implementation candidate:
e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d

Prior implementation evaluation:
RLY-S14-EVAL-001 — REWORK

Accepted rework candidate:
ae582c52ec4a6451b54e9d6e018932e93e72e013

Independent implementation evaluation:
RLY-S14-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S14-ACCEPT-001 — ACCEPTED
```

Current gate:

```text
Slice 1.4:
OPEN

Slice 1.4 design:
ACCEPTED

Slice 1.4 technical result:
ACCEPTED

Accepted technical result SHA:
ae582c52ec4a6451b54e9d6e018932e93e72e013

Current role:
HUMAN AUTHORITY / ORCHESTRATOR

Finalization / closure:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

---

# 3. Accepted Slice 1.4 technical summary

The accepted implementation:

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
- detects malformed durable definition history and fails closed;
- routes block/unblock/cancel/supersede through accepted lifecycle/governance;
- adds no runtime dependency;
- performs no board, provider, repository-sync, or agent work.

The accepted bounded rework closes `RLY-S14-EVAL-001` evidence findings and corrects graph-validation error-classification ordering without architectural redesign.

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

Technical acceptance does not imply closure or authorize the next Slice.

Exact authority boundaries and exact SHAs remain controlling.

**Unblocked ≠ authorized.**
