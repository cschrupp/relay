# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.1 closed / Slice 1.2 design authorized  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted foundation

Phase 0 is complete and closed.

Accepted Phase-0 acceptance-record SHA:

```text
6c1b3e1098cdc6c220868aea8a492c413d3cca35
```

Accepted Phase-0 protocol/document synchronization SHA:

```text
cb9edc453442dc639a523ef301e4a258d0394daa
```

Phase-0 closure evaluation:

```text
RLY-S06-CLOSE-EVAL-001 — ACCEPT
```

---

# 2. Protocol rules in force

Human-accepted Phase-0 process amendments remain:

```text
P0-PR-01  registered living-projection impact preflight
P0-PR-02  visible role/model assignment and execution provenance
P0-PR-03  design review uses ACCEPT / REVISE / ESCALATE
P0-PR-04  review acceptance and next-phase authorization are separate
```

Working model-role convention:

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

When the preferred and executing models differ, the deviation is recorded explicitly.

---

# 3. Slice 1.1 accepted state

```text
Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Accepted design head:
0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b

Independent design evaluation:
RLY-S11-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S11-DESIGN-ACCEPT-001

Implementation authorization:
RLY-S11-AUTH-001

Accepted technical implementation:
ae79b15170c88e776af99944eab9b2fdd6872c2e

Independent implementation evaluation:
RLY-S11-EVAL-001 — ACCEPT

Human implementation acceptance:
RLY-S11-ACCEPT-001

Acceptance-record/finalization:
ccfbfb964064e92aef4e21e11f0ad01290acb16f

Closure evaluation:
RLY-S11-CLOSE-EVAL-001 — ACCEPT
```

The accepted technical implementation SHA remains distinct from the later acceptance-record commit.

---

# 4. Slice 1.2 authority

Human Authority decision:

```text
RLY-S12-OPEN-001
Slice 1.2 OPEN
```

Design authorization:

```text
RLY-S12-DESIGN-AUTH-001
```

Authorized exact starting baseline:

```text
ccfbfb964064e92aef4e21e11f0ad01290acb16f
```

Current Slice 1.2 state:

```text
DESIGN AUTHORIZED
IMPLEMENTATION NOT AUTHORIZED
```

Slice 1.2 objective:

> Register the selected provider-neutral repository as Relay project state and deterministically resolve human-selected repository refs to immutable commit/baseline identity, closing the baseline/worktree proof deferred by Slice 0.6.

Slice 1.2 may design:

- repository registration semantics;
- branch/tag/full-SHA input rules;
- remote ref resolution to canonical commit SHA;
- construction and persistence of accepted `CommitRef`/baseline identity;
- consistency with Slice 1.1 confirmed repository access;
- baseline/snapshot/worktree provenance verification;
- deterministic moved/missing/ambiguous-ref failures;
- restart/replay integrity.

Slice 1.2 does NOT authorize:

- remote `.relay/` writes;
- GitHub contents-write permission;
- branch/commit/PR creation;
- agent execution;
- generic provider abstraction beyond current need.

---

# 5. Accepted Slice 1.1 capability

Accepted capability includes:

- GitHub App RS256 JWT authentication with explicit clock input;
- ephemeral installation access tokens with no durable token storage;
- pinned GitHub REST headers and a narrow standard-library HTTP seam;
- strict validation of external GitHub JSON;
- project-scoped installation/repository access state;
- provider status separated from Relay readiness;
- fail-closed permission-policy validation;
- explicit provider identity → `RepositoryRef` conversion;
- signed webhook verification;
- deterministic semantic delivery digests;
- project-scoped idempotency;
- app-level webhook fanout to existing bindings only;
- monotonic per-binding `state_revision`;
- atomic repository-set replacement;
- immutable GitHub integration events;
- SQLite migration v2.

---

# 6. Explicitly deferred

Still not authorized:

- Slice 1.2 implementation;
- remote `.relay/` initialization/synchronization;
- repository contents writes;
- branch, commit, or pull-request creation;
- user OAuth;
- generic multi-provider infrastructure;
- agent execution.

Slice 1.3 remains:

```text
NOT OPEN / NOT AUTHORIZED
```

---

# 7. Current role/model

```text
Current role/model:
Slice 1.2 Architect — GPT-5.6 Sol

Next role/model:
Independent Design Reviewer — GPT-5.6 Sol
```

Implementation preference, once separately authorized:

```text
GPT-5.6 Luna
```

---

# 8. Authorization state

```text
Phase 1:
OPEN

Slice 1.1:
CLOSED / ACCEPTED

Slice 1.2:
OPEN / DESIGN AUTHORIZED

Slice 1.2 implementation:
NOT AUTHORIZED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
