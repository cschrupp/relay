# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.3 complete / accepted  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted foundation

Phase 0 is complete and closed.

Slice 1.1 is complete, accepted, and closed.

```text
Accepted Slice 1.1 technical implementation:
ae79b15170c88e776af99944eab9b2fdd6872c2e

Slice 1.1 acceptance-record/finalization:
ccfbfb964064e92aef4e21e11f0ad01290acb16f

Slice 1.1 closure evaluation:
RLY-S11-CLOSE-EVAL-001 — ACCEPT
```

Slice 1.2 is complete, accepted, and closed.

```text
Accepted Slice 1.2 design head:
4acd6be1f93058d1efcafc66a78fc1a9726c16ba

Accepted Slice 1.2 technical result:
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d

Independent implementation evaluation:
RLY-S12-EVAL-002 — ACCEPT

Human acceptance:
RLY-S12-ACCEPT-001

Acceptance-record/finalization:
7e08ad484ce794946ec2e09abf44060879e9fc04

Closure evaluation:
RLY-S12-CLOSE-EVAL-001 — ACCEPT
```

Slice 1.3 is complete and accepted.

```text
Accepted Slice 1.3 design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9

Accepted Slice 1.3 technical result:
9b5166d1e95aefeb177d30c29f943f45a591ea05

Independent implementation evaluation:
RLY-S13-EVAL-002 — ACCEPT

Human acceptance:
RLY-S13-ACCEPT-001
```

---

# 2. Protocol rules in force

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

If preferred and executing models differ, both are recorded.

---

# 3. Slice 1.3 accepted authority

Authority chain:

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

Authorized implementation baseline:

```text
c4dd5484c9b90894f3a4ca06a4f7ccde76e1f2bd
```

The initial implementation checkpoint `9456b31344d6dd880943eef04e99a9f5dc5da0d2` remains historical provenance. The exact accepted implementation is `9b5166d1e95aefeb177d30c29f943f45a591ea05` after bounded rework closing the exact-registry-byte and test-evidence findings.

Accepted behavior includes:

- schema-v1 `.relay/registry.json` preservation;
- exact read-only preparation and `RepositorySyncSubjectV1`;
- project/exact-subject HUMAN `RepositoryMutationAuthorization`;
- deterministic SQLite migration v3 for immutable mutation authority;
- separate repository-scoped READ and WRITE tokens;
- one Git tree, one exact-parent commit, one non-force default-branch ref movement;
- exact provider/local/head race guards;
- unregistered-path adoption-or-conflict;
- workflow-path mutation prohibition under the current permission ceiling;
- no bootstrap for repositories without an existing default-branch head;
- observation-based indeterminate-ref reconciliation;
- exact visible registry-byte and artifact verification;
- `CURRENT` plus `wrote_remote` result semantics;
- no automatic Relay Baseline persistence.

---

# 4. Acceptance evidence

Exact accepted candidate:

```text
9b5166d1e95aefeb177d30c29f943f45a591ea05
```

GitHub Actions:

```text
36600301960
```

Quality:

```text
Ruff format    PASS
Ruff lint      PASS
Pyright        PASS — 0 errors / 0 warnings
pytest         PASS — 490 passed
repository_sync tests — 50 passed
uv build       PASS
```

ADR-0009 and the Slice 1.3 memory are locked/accepted during bounded finalization.

---

# 5. Current canonical living documents

Registry-current projections are:

```text
Product Proposal v0.5
Build Plan v0.5
Current Baseline
Documentation Governance v0.3
Engineering Simplicity, Scope, and Quality
```

Canonicality remains a `.relay/registry.json` relationship.

---

# 6. Authorization state

```text
Phase 1:
OPEN

Slice 1.1:
CLOSED / ACCEPTED

Slice 1.2:
CLOSED / ACCEPTED

Slice 1.3:
COMPLETE / ACCEPTED

Slice 1.4:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

The next governed action is independent Slice 1.3 closure evaluation. Slice 1.4 requires a new explicit Human Authority opening after closure.

**Unblocked ≠ authorized.**
