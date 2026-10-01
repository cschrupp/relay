# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.4 finalized; closure evaluation pending  
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

Slices 1.1–1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
TECHNICAL RESULT ACCEPTED / FINALIZED
CLOSURE EVALUATION PENDING

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

# 2. Slice 1.4 authority and accepted result

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
RLY-S14-CLOSE-AUTH-001 — AUTHORIZED
```

Exact accepted technical result:

```text
ae582c52ec4a6451b54e9d6e018932e93e72e013
```

Canonical technical-acceptance main before finalization:

```text
f5b593a50947a306a7a53ddae98184a4f7f546f5
```

# 3. Accepted Slice 1.4 capability

The accepted Slice 1.4 implementation:

- preserves immutable Project/Slice domain schemas and authority fields;
- introduces SQLite migration v4 definition revisions/history;
- makes the administration service the sole post-v4 runtime Project/Slice creation path;
- requires HUMAN audit metadata;
- enforces strict definition-revision CAS;
- validates same-Project acyclic parent/dependency graphs;
- freezes governed or downstream-consumed Slice definitions;
- guards physical deletion and preserves tombstones/retired identity;
- fails closed on malformed durable definition history;
- adds no runtime dependency;
- adds no board, provider, repository-sync, lifecycle-schema, or agent behavior.

# 4. Current gate

```text
Current governed role:
INDEPENDENT CLOSURE EVALUATOR — GPT-5.6 Sol

Slice 1.4 technical result:
ACCEPTED

Slice 1.4 finalization:
COMPLETE

Next gate:
Independent closure evaluation

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Closing Slice 1.4 does not authorize Slice 1.5.

**Unblocked ≠ authorized.**
