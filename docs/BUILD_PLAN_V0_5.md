# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.4 design authorized  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after independent closure of Slice 1.3, Human opening of Slice 1.4, and explicit authorization of the Slice 1.4 architecture / contract / design phase.

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
AUTHORIZED

Slice 1.4 implementation:
NOT AUTHORIZED
```

Slice 1.3 closure:

```text
RLY-S13-CLOSE-EVAL-001 — ACCEPT
7d266aef282c6d678e059754d2eb6a5ff297d83a
```

Slice 1.4 authority chain:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001
```

Authorized design baseline:

```text
670996ec43d77526adb0ea540c81a57d6e83453b
```

---

# 3. Process rules in force

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

# 4. Slice 1.4 — Project and Slice CRUD

```text
OPEN
DESIGN AUTHORIZED
IMPLEMENTATION NOT AUTHORIZED
```

The design phase must derive its contract from accepted Relay semantics rather than inventing a parallel project-management model.

The architect must define:

- exact Project and Slice create/read/update/delete semantics;
- immutable identity and project ownership rules;
- preservation of Baseline, lifecycle, governance, GitHub, repository-sync, and audit history;
- which fields may be updated and under what preconditions;
- whether “delete” means hard deletion, guarded deletion of never-used records, archival/retirement, or another bounded semantic;
- parent/dependency graph integrity;
- concurrency and stale-write behavior;
- persistence/migration requirements;
- typed failures and deterministic idempotency;
- acceptance criteria and expected implementation change surface.

The minimum safe architecture must preserve the accepted fact that `Slice` contains intended engineering scope and has no workflow state; lifecycle state remains owned by the lifecycle subsystem.

---

# 5. Later Phase-1 slices

```text
Slice 1.5 — Board Projection:
NOT OPEN

Slice 1.6 — Human Authorization and Decision Gates:
NOT OPEN

Slice 1.7 — Manual Evaluation and Acceptance:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

---

# 6. Current gate

```text
Slice 1.4 opening:
RLY-S14-OPEN-001 — DONE

Slice 1.4 design authorization:
RLY-S14-DESIGN-AUTH-001 — AUTHORIZED

Current governed role:
ARCHITECT / CONTRACT DESIGNER — GPT-5.6 Sol

Next gate:
INDEPENDENT DESIGN REVIEWER — GPT-5.6 Sol

Slice 1.4 implementation:
NOT AUTHORIZED
```

The design reviewer must stop for Human design acceptance after an ACCEPT outcome.

**Unblocked ≠ authorized.**
