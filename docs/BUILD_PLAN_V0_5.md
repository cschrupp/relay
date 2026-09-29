# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.4 open  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after independent closure of Slice 1.3 and explicit Human Authority opening of Slice 1.4.

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
NOT AUTHORIZED

Slice 1.4 implementation:
NOT AUTHORIZED
```

Slice 1.3 closure:

```text
RLY-S13-CLOSE-EVAL-001 — ACCEPT
Canonical closure head:
7d266aef282c6d678e059754d2eb6a5ff297d83a
```

Slice 1.4 opening:

```text
RLY-S14-OPEN-001
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

Opening, design authorization, design acceptance, implementation authorization, technical acceptance, and closure are distinct transitions.

**Unblocked ≠ authorized.**

---

# 4. Repository and documentation governance

The accepted schema-v1 repository contract remains:

```text
.relay/
└── registry.json
```

Canonical status is a registry relationship, not a filename. Historical locked/immutable records remain immutable.

---

# 5. Phase 1 roadmap

## Slice 1.1 — GitHub App Integration

```text
COMPLETE / ACCEPTED / CLOSED
```

## Slice 1.2 — Repository Registration and Baseline Resolution

```text
COMPLETE / ACCEPTED / CLOSED
```

## Slice 1.3 — `.relay/` Initialization and Sync

```text
COMPLETE / ACCEPTED / CLOSED
```

## Slice 1.4 — Project and Slice CRUD

```text
OPEN
DESIGN NOT AUTHORIZED
IMPLEMENTATION NOT AUTHORIZED
```

Roadmap objective area:

> Project and Slice CRUD

The opening itself does not elaborate requirements or authorize architecture/contract/design.

## Slice 1.5 — Board Projection

```text
NOT OPEN
```

## Slice 1.6 — Human Authorization and Decision Gates

```text
NOT OPEN
```

## Slice 1.7 — Manual Evaluation and Acceptance

```text
NOT OPEN
```

---

# 6. Current gate

```text
Slice 1.4 opening:
RLY-S14-OPEN-001 — DONE

Slice 1.4 design authorization:
NOT GRANTED

Slice 1.4 implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Next valid Slice 1.4 transition is a separate Human Authority decision on architecture / contract / design authorization.

**Unblocked ≠ authorized.**
