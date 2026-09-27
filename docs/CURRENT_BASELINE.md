# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.1 implementation complete / pending independent evaluation  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted technical baseline

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

# 2. Phase-0 protocol review

Review:

```text
RLY-P0-PROTOCOL-REVIEW-001
ACCEPT WITH PROCESS AMENDMENTS
```

Human acceptance:

```text
RLY-P0-PROTOCOL-ACCEPT-001
```

Process amendments in force:

```text
P0-PR-01  registered living-projection impact preflight
P0-PR-02  visible current/next role + model
P0-PR-03  design review uses ACCEPT / REVISE / ESCALATE
P0-PR-04  review acceptance and next-phase authorization are separate
```

---

# 3. Phase-1 authority

Phase 1:

```text
RLY-P1-OPEN-001
OPEN
```

Slice 1.1 design authorization:

```text
RLY-S11-DESIGN-AUTH-001
```

Accepted reviewed design:

```text
Revision 1:
d73daf2ab2a850a4762084e042fa496f7a377e99

Revision 2:
0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b

Independent design evaluation:
RLY-S11-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S11-DESIGN-ACCEPT-001

Implementation authorization:
RLY-S11-AUTH-001
```

Implementation authority is limited to Slice 1.1.

Slice 1.2 remains separately unauthorized.

---

# 4. Current Slice 1.1 state

```text
Slice 1.1:
IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION

Technical implementation checkpoint:
92a65728ab66ededed86d134a845a93fe58ad01d

Technical checkpoint CI:
36338324389 — SUCCESS

Tests:
405 passed
```

The final repository result SHA is the implementation-result handover commit that includes this candidate documentation and registry synchronization.

That result is not accepted until independent evaluation and a separate Human Authority acceptance.

Current role/model:

```text
Implementation Agent — GPT-5.6 Sol
```

Next role/model:

```text
Independent Evaluator — GPT-5.6 Sol
```

---

# 5. Slice 1.1 implemented capability

The candidate implementation provides:

- GitHub App RS256 JWT authentication with explicit clock input;
- ephemeral installation access tokens with no durable token storage;
- pinned GitHub REST headers and a narrow standard-library HTTP transport seam;
- strict validation of external GitHub JSON before typed persistence;
- project-scoped installation and accessible-repository state;
- provider installation status separated from Relay access readiness;
- fail-closed permission-policy validation;
- explicit `RepositoryId` input for provider-neutral `RepositoryRef` conversion;
- signed webhook verification before payload parsing;
- deterministic semantic delivery digests and project-scoped idempotency;
- app-level webhook fanout only to existing project bindings;
- monotonic per-binding `state_revision` optimistic concurrency;
- atomic repository-set replacement;
- immutable GitHub integration events;
- SQLite migration v2 for GitHub integration state.

New runtime dependency:

```text
PyJWT[crypto]
```

The frozen lock currently resolves PyJWT 2.15.0 and cryptography 50.0.1.

---

# 6. Explicitly deferred

Slice 1.1 does not implement or authorize:

- provider-neutral project repository registration;
- branch/tag/ref resolution to immutable commit SHAs;
- baseline/worktree proof;
- remote `.relay/` initialization or synchronization;
- repository content writes;
- branch, commit, or pull-request creation;
- user OAuth;
- generic multi-provider integration infrastructure;
- agent execution.

These remain separately gated.

---

# 7. Authorization state

```text
Phase 1:
OPEN

Slice 1.1:
IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION

Slice 1.1 accepted:
NO

Slice 1.2:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**

---

# 8. Canonical living documents

Canonical status is defined by `.relay/registry.json`.

Current canonical keys remain:

```text
product-proposal
build-plan
current-baseline
documentation-governance
engineering-simplicity-quality
```

Registered living projections advance through a new `ArtifactId` and revision when their exact bytes change.
