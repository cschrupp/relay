# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.4 technical result accepted  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** October 2026

---

# 1. Purpose

This is the current execution plan after independent acceptance and Human Authority acceptance of the exact Slice 1.4 technical result.

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
TECHNICAL RESULT ACCEPTED
```

Authority/provenance chain:

```text
RLY-S14-OPEN-001
RLY-S14-DESIGN-AUTH-001
RLY-S14-DESIGN-EVAL-001 — REVISE
RLY-S14-DESIGN-EVAL-002 — ACCEPT
RLY-S14-DESIGN-ACCEPT-001 — ACCEPTED
RLY-S14-AUTH-001 — AUTHORIZED
RLY-S14-EVAL-001 — REWORK
RLY-S14-EVAL-002 — ACCEPT
RLY-S14-ACCEPT-001 — ACCEPTED

Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Accepted Revision 2 design head:
f5a678da360b96701a1f9635d3703b49dc16e779

Canonical rework baseline:
dfe6c20c8f65b42fe69b7d315956a91d2a29487c

Accepted technical result:
ae582c52ec4a6451b54e9d6e018932e93e72e013
```

---

# 3. Accepted Slice 1.4 technical result

The accepted implementation preserves the combined Slice 1.4 design and provides:

- the sole audited post-v4 Project/Slice runtime creation path;
- migration v4 definition revisions and append-only history;
- strict expected-revision compare-and-swap semantics;
- deterministic read/list behavior;
- same-project parent/dependency validation and cycle rejection;
- lifecycle/gate/downstream-definition freezes;
- explicit guarded delete blockers with tombstones and retired IDs;
- corruption detection that fails closed;
- no new runtime dependency;
- no board, provider, repository-sync, or agent-execution expansion.

The bounded rework also corrected graph-validation ordering so malformed proposed graphs receive the accepted cycle-specific error classification before downstream freeze classification.

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

Opening, design authorization, independent review, Human design acceptance, implementation authorization, technical acceptance, finalization, and closure remain distinct transitions.

**Unblocked ≠ authorized.**

---

# 5. Current gate

```text
Current governed role:
HUMAN AUTHORITY / ORCHESTRATOR

Slice 1.4 technical result:
ACCEPTED — RLY-S14-ACCEPT-001

Accepted candidate:
ae582c52ec4a6451b54e9d6e018932e93e72e013

Finalization / closure:
NOT AUTHORIZED

Next gate:
Explicit bounded finalization / closure authorization

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Technical acceptance does not itself authorize Slice 1.4 closure, Slice 1.5, or agent execution.
