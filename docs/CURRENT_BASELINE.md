# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.2 Design Revision 1 complete / pending independent review  
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

# 4. Slice 1.2 Design Revision 1

Design document:

```text
docs/slices/SLICE_1_2_REPOSITORY_REGISTRATION_AND_BASELINE_RESOLUTION.md
```

Current design state:

```text
REVISION 1 COMPLETE
PENDING INDEPENDENT DESIGN REVIEW
```

The design preserves the accepted provider-neutral core and proposes:

- `Project.primary_repository` remains the sole project repository registration authority;
- no duplicate repository-registration table;
- explicit BRANCH / TAG / COMMIT_SHA selector semantics;
- resolve moving refs once, then pin every later read to canonical commit/tree/blob identity;
- GitHub commit/tree/blob read proof using the existing `Contents: read` permission ceiling;
- exact `.relay/registry.json` and registered-artifact validation against the selected commit tree;
- deterministic handling of truncated trees, symlinks, submodules, missing blobs, and digest mismatch;
- stable first-binding of registry `ArtifactId` into immutable core `Artifact` values, preserving the Slice-0.6 F007 rule;
- atomic verified Artifact + Baseline persistence using existing tables;
- no migration v3 absent evidence;
- no GitHub writes, local Git dependency, agent execution, or Slice 1.3 behavior.

Independent review must explicitly challenge snapshot proof, F007 artifact binding, atomicity, and the remote-snapshot versus future local-worktree boundary.

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

Slice 1.2 Design Revision 1:
COMPLETE / PENDING INDEPENDENT REVIEW

Slice 1.2 implementation:
NOT AUTHORIZED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
