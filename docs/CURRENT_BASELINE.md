# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.2 Design Revision 3 complete / pending independent review  
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

8667b3e8a20e317fb3c5ccc66278e1a14aebdafd
```

Independent review:

```text
RLY-S12-DESIGN-EVAL-002 — REVISE

F001–F003 resolved
F004 remote repository identity does not bracket snapshot
```

Revision 3 amendment:

```text
docs/slices/
SLICE_1_2_REPOSITORY_REGISTRATION_AND_BASELINE_RESOLUTION_REV3_AMENDMENT.md
```

Current design state:

```text
REVISION 1 + REVISION 2 + REVISION 3 AMENDMENTS COMPLETE
PENDING INDEPENDENT DESIGN REVIEW
```

Revision 3 resolves F004 by requiring:

- the same captured GitHub provider identity to be checked both before and after all commit/tree/blob/registry/artifact snapshot reads;
- the pre- and post-snapshot checks to use the same project ID, installation ID, GitHub repository ID, node ID, `RepositoryRef`, and expected Slice 1.1 `state_revision`;
- repository rename, transfer, redirect change, old-path reuse, or inability to establish provider identity to fail closed before any SQLite persistence;
- the post-snapshot provider identity check to complete before `BEGIN IMMEDIATE`;
- all provider network I/O to finish before the final SQLite write transaction;
- the Revision-2 local atomic access guard to remain the final gate before Artifact/Baseline insertion;
- explicit acknowledgment that Relay does not claim an atomic transaction spanning GitHub and SQLite;
- revised A89 wording limited to provider changes that become observable during snapshot/final provider proof and local access changes reflected in Relay before local commit.

The combined design continues to preserve:

- `Project.primary_repository` as the sole Relay project-repository authority;
- no duplicate repository-registration table;
- explicit provider-access selection with captured Slice 1.1 revision;
- repository-scoped token minting from captured provider IDs;
- explicit BRANCH / TAG / COMMIT_SHA selector semantics;
- resolve-once then immutable commit/tree/blob pinning;
- Slice-0.6 repository-contract semantics and F007;
- first-binding immutable core Artifact semantics;
- atomic local Artifact + Baseline persistence with a final Slice 1.1 access guard;
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

Slice 1.2 Design Revision 1 + Revision 2 + Revision 3:
COMPLETE / PENDING INDEPENDENT REVIEW

Slice 1.2 implementation:
NOT AUTHORIZED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
