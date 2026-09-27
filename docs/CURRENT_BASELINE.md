# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.2 Design Revision 2 complete / pending independent review  
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

# 3. Slice 1.2 authority

Human Authority:

```text
RLY-S12-OPEN-001
Slice 1.2 OPEN

RLY-S12-DESIGN-AUTH-001
Slice 1.2 DESIGN AUTHORIZED
```

Exact authorized design baseline:

```text
1ec84fe0507f5e1a7dfff3098d285db628cb3649
```

Slice 1.2 implementation remains:

```text
NOT AUTHORIZED
```

---

# 4. Slice 1.2 design authority

Revision 1:

```text
docs/slices/SLICE_1_2_REPOSITORY_REGISTRATION_AND_BASELINE_RESOLUTION.md

8d94e7408e4f24bf87e32dfc73273fd42f27a9da
```

Independent review:

```text
RLY-S12-DESIGN-EVAL-001 — REVISE

F001 provider binding identity lost
F002 access revocation race before persistence
F003 live provider repository identity not revalidated
```

Revision 2 amendment:

```text
docs/slices/
SLICE_1_2_REPOSITORY_REGISTRATION_AND_BASELINE_RESOLUTION_REV2_AMENDMENT.md
```

Current design state:

```text
REVISION 1 + REVISION 2 AMENDMENT COMPLETE
PENDING INDEPENDENT DESIGN REVIEW
```

Revision 2 resolves the review findings by requiring:

- an explicit ephemeral GitHub repository-access selection containing project ID, installation ID, GitHub repository ID, GitHub node ID, exact `RepositoryRef`, and captured Slice 1.1 `state_revision`;
- repository-scoped token minting from the captured provider IDs rather than rediscovery by path;
- a live read-only GitHub repository identity check before ref resolution;
- fail-closed comparison of provider repository ID, node ID, and canonical `full_name`;
- an atomic final SQLite guard that requires the original Slice 1.1 binding revision to remain unchanged and `ACTIVE / READY`;
- final selected-repository membership and stored provider identity revalidation before any Artifact/Baseline insertion;
- rollback of both Artifact and Baseline writes if the access guard fails;
- no hidden retry or implicit refresh of authorization evidence;
- targeted tree traversal as a permitted minimum-sufficient alternative to whole-repository recursive enumeration.

The design continues to preserve:

- `Project.primary_repository` as the sole Relay project-repository authority;
- no duplicate repository-registration table;
- explicit BRANCH / TAG / COMMIT_SHA selector semantics;
- resolve-once then immutable commit/tree/blob pinning;
- Slice-0.6 repository-contract semantics and F007;
- first-binding immutable core Artifact semantics;
- atomic Artifact + Baseline persistence;
- no migration v3 absent evidence;
- no GitHub writes, local Git dependency, or Slice 1.3 behavior.

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

# 6. Current role/model

```text
Current role/model:
Independent Design Reviewer — GPT-5.6 Sol

If REVISE:
Slice 1.2 Architect — GPT-5.6 Sol

If ACCEPT:
Human Authority — user
```

Preferred future implementation model, only if separately authorized:

```text
GPT-5.6 Luna
```

---

# 7. Authorization state

```text
Phase 1:
OPEN

Slice 1.1:
CLOSED / ACCEPTED

Slice 1.2:
OPEN

Slice 1.2 Design Revision 1 + Revision 2 Amendment:
COMPLETE / PENDING INDEPENDENT REVIEW

Slice 1.2 implementation:
NOT AUTHORIZED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
