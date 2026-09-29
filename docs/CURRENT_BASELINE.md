# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.3 complete / accepted; closure evaluation pending  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted foundation

Phase 0 is complete and closed.

Slice 1.1 and Slice 1.2 are complete, accepted, and closed.

Slice 1.3 is complete and technically accepted.

```text
Accepted Slice 1.3 design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9

Accepted Slice 1.3 technical result:
9b5166d1e95aefeb177d30c29f943f45a591ea05

Independent implementation evaluation:
RLY-S13-EVAL-002 — ACCEPT

Human acceptance:
RLY-S13-ACCEPT-001

Acceptance/finalization:
5164f1a8532e1ca05007531cdfd1f5084755092a

Finalization branch CI:
36612232489 — SUCCESS

Promoted-main CI:
36612444758 — SUCCESS
```

---

# 2. Slice 1.3 accepted authority

```text
RLY-S13-OPEN-001
RLY-S13-DESIGN-AUTH-001
RLY-S13-DESIGN-EVAL-001 — REVISE
RLY-S13-DESIGN-EVAL-002 — REVISE
RLY-S13-DESIGN-EVAL-003 — REVISE
RLY-S13-DESIGN-EVAL-004 — ACCEPT
RLY-S13-DESIGN-ACCEPT-001
RLY-S13-AUTH-001
RLY-S13-EVAL-001 — REWORK
RLY-S13-EVAL-002 — ACCEPT
RLY-S13-ACCEPT-001
```

Accepted behavior includes:

- schema-v1 `.relay/registry.json` preservation;
- exact `RepositorySyncSubjectV1`;
- read-only preparation;
- project/exact-subject HUMAN `RepositoryMutationAuthorization`;
- deterministic SQLite migration v3;
- separate repository-scoped READ/WRITE tokens;
- one Git tree, one exact-parent commit, one non-force default-branch ref movement;
- provider/local/head fail-closed race guards;
- unregistered-path adoption-or-conflict;
- workflow mutation prohibition under the contents-only ceiling;
- no empty-repository bootstrap;
- observation-based indeterminate-ref reconciliation;
- exact visible registry/artifact verification;
- target-state idempotency;
- no automatic Relay Baseline persistence.

---

# 3. Acceptance evidence

```text
Accepted implementation:
9b5166d1e95aefeb177d30c29f943f45a591ea05

Implementation CI:
36600301960 — SUCCESS
490 tests passed
repository_sync tests: 50 passed
Ruff / Pyright / build passed

Acceptance/finalization:
5164f1a8532e1ca05007531cdfd1f5084755092a

Promoted-main CI:
36612444758 — SUCCESS
```

ADR-0009 and the Slice 1.3 memory are locked/accepted.

---

# 4. Closure state

The accepted technical and documentation state is ready for independent closure evaluation.

```text
Slice 1.3:
COMPLETE / ACCEPTED
CLOSURE EVALUATION PENDING

Slice 1.4:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

No Slice 1.4 design or implementation authority exists yet.

**Unblocked ≠ authorized.**
