# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.4 Design Revision 1 submitted  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after independent closure of Slice 1.3, Human opening of Slice 1.4, explicit Slice 1.4 design authorization, and submission of Slice 1.4 Design Revision 1 for independent review.

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

Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
OPEN

Slice 1.4 design:
AUTHORIZED / REVISION 1 SUBMITTED FOR INDEPENDENT REVIEW

Slice 1.4 implementation:
NOT AUTHORIZED
```

Authority chain:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001
```

Exact authorized design baseline:

```text
1eaece23e31d831bfd2b27e55a898df389cc45fc
```

Design record:

```text
docs/slices/SLICE_1_4_PROJECT_AND_SLICE_CRUD.md
```

---

# 3. Slice 1.4 design direction

Revision 1 preserves the accepted immutable `Project` and `Slice` domain values and adds a bounded human administration layer.

Normative direction:

- Project/Slice identity and ownership remain immutable.
- Project `primary_repository` remains immutable repository authority.
- Project name is editable.
- Slice title/scope/acceptance criteria/parent/dependencies are editable only within a bounded early-definition window.
- Slice workflow state remains owned by the lifecycle subsystem.
- Definition changes use integer optimistic revisions and append-only definition history.
- SQLite migration v4 supplies definition revisions/history with no new runtime dependency.
- Parent and dependency graphs remain same-project and acyclic.
- A Slice already consumed by downstream dependency or governed state is frozen rather than silently invalidated.
- Delete is a guarded cleanup of unused current entities only; governed work is cancelled/superseded through lifecycle.
- Delete leaves an immutable tombstone/history and never cascades accepted authority.
- Artifact attachment remains owned by accepted Artifact/Baseline/gate contracts rather than being added to `Slice`.
- No board, provider, agent, or autonomous work is authorized.

---

# 4. Process rules in force

Registered living-projection changes advance `.relay/registry.json` in the same governed change.

Role/model convention:

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

Opening, design authorization, independent review, Human design acceptance, implementation authorization, technical acceptance, and closure remain distinct transitions.

**Unblocked ≠ authorized.**

---

# 5. Current gate

```text
Current governed role:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Review input:
Slice 1.4 Design Revision 1

Design authority:
RLY-S14-DESIGN-AUTH-001

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

The independent reviewer must return ACCEPT, REVISE, or ESCALATE and stop at the Human design-acceptance gate after ACCEPT.
