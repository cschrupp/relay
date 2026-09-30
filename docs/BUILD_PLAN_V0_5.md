# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.4 design accepted  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after independent acceptance and Human Authority acceptance of the combined Slice 1.4 Revision 1 + Revision 2 design.

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
ACCEPTED

Slice 1.4 implementation:
NOT AUTHORIZED
```

Authority/provenance chain:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001
RLY-S14-DESIGN-EVAL-001 — REVISE
RLY-S14-DESIGN-EVAL-002 — ACCEPT
RLY-S14-DESIGN-ACCEPT-001 — ACCEPTED

Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Accepted Revision 2 design head:
f5a678da360b96701a1f9635d3703b49dc16e779
```

---

# 3. Accepted Slice 1.4 design direction

The accepted combined design:

- preserves accepted immutable `Project` and `Slice` domain values;
- keeps Project repository authority immutable;
- makes the Slice 1.4 administration service the only post-v4 product/runtime creation path;
- introduces integer definition revisions and append-only definition history through SQLite migration v4;
- requires strict compare-and-swap before both material and exact-target updates;
- validates same-project parent/dependency graphs and cycles;
- freezes Slice definition mutation once lifecycle is initialized;
- freezes a Slice definition once another current Slice depends on it;
- permits physical delete only for unused current entities after explicit blocker checks;
- preserves retired identity/history through DELETE tombstones;
- keeps block/unblock/cancel/supersede in lifecycle/governance;
- adds no runtime dependency.

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
HUMAN AUTHORITY / ORCHESTRATOR

Slice 1.4 design:
ACCEPTED

Slice 1.4 implementation:
NOT AUTHORIZED

Next gate:
Explicit Human Authority implementation authorization

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Design acceptance does not authorize implementation.
