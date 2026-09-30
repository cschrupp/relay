# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.4 Design Revision 1 submitted for independent review  
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

# 2. Slice 1.4 authority

```text
Opening:
RLY-S14-OPEN-001

Design authorization:
RLY-S14-DESIGN-AUTH-001

Exact authorized design baseline:
1eaece23e31d831bfd2b27e55a898df389cc45fc
```

Design Revision 1:

```text
docs/slices/SLICE_1_4_PROJECT_AND_SLICE_CRUD.md

Status:
SUBMITTED FOR INDEPENDENT REVIEW
```

Current gate:

```text
Slice 1.4:
OPEN

Slice 1.4 design:
AUTHORIZED / REVIEW PENDING

Current role:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

---

# 3. Revision 1 design summary

The proposed contract:

- leaves accepted `Project` and `Slice` schemas unchanged;
- introduces independent definition revisions/history in persistence;
- uses exact optimistic revision checks and target-state idempotency;
- keeps Project repository authority immutable;
- validates same-project parent/dependency graphs and cycles;
- permits Slice definition edits only before governed/downstream use makes them unsafe;
- guards physical delete to unused entities and preserves tombstones/history;
- routes block/unblock/cancel/supersede through accepted lifecycle/governance;
- adds SQLite migration v4 only;
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
