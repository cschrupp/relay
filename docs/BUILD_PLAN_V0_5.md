# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slices 1.1–1.4 complete, accepted, and closed  
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

Slices 1.1–1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

# 2. Slice 1.4 authority and closure lineage

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
RLY-S14-CLOSE-EVAL-001 — ACCEPT

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

Finalization baseline:
ba31db3ace9d99f573e26611637c567b3f1e8d44
```

# 3. Accepted Slice 1.4 capability

Slice 1.4 now provides the accepted Project/Slice definition-administration layer:

- migration v4 definition revisions and append-only history;
- audited HUMAN create/update/delete;
- strict optimistic concurrency;
- deterministic reads/lists;
- same-Project acyclic parent/dependency validation;
- lifecycle/gate/downstream definition freezes;
- guarded physical deletion with tombstones and retired identity;
- fail-closed durable-history integrity checking;
- no new runtime dependency;
- no board, provider, repository-sync, lifecycle-schema, or agent behavior.

The development memory is locked at:

`docs/slices/SLICE_1_4_PROJECT_AND_SLICE_CRUD_MEMORY.md`

# 4. Current gate

```text
Current governed role:
HUMAN AUTHORITY / ORCHESTRATOR

Slice 1.4:
COMPLETE / ACCEPTED / CLOSED

Next possible transition:
Explicit Human Authority opening/design authorization for Slice 1.5

Slice 1.5:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

Closure of Slice 1.4 does not itself open Slice 1.5.

**Unblocked ≠ authorized.**
