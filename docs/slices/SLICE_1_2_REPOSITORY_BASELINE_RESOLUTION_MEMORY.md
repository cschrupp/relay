# Slice 1.2 — Repository Baseline Resolution Memory

**Status:** COMPLETE / ACCEPTED  
**Record state:** LOCKED  
**Phase:** 1  
**Slice:** 1.2  
**Accepted design head:** `4acd6be1f93058d1efcafc66a78fc1a9726c16ba`  
**Accepted technical result:** `9ed4a8da4d989fd41674ae59ef68ba4238c09b5d`  
**Independent implementation evaluation:** `RLY-S12-EVAL-002` — ACCEPT  
**Human acceptance:** `RLY-S12-ACCEPT-001`

## Authority chain

```text
RLY-S12-OPEN-001
        ↓
RLY-S12-DESIGN-AUTH-001
        ↓
Design Revision 1
8d94e7408e4f24bf87e32dfc73273fd42f27a9da
        ↓
RLY-S12-DESIGN-EVAL-001 — REVISE
F001–F003
        ↓
Design Revision 2 amendment
8667b3e8a20e317fb3c5ccc66278e1a14aebdafd
        ↓
RLY-S12-DESIGN-EVAL-002 — REVISE
F004
        ↓
Design Revision 3 amendment
4acd6be1f93058d1efcafc66a78fc1a9726c16ba
        ↓
RLY-S12-DESIGN-EVAL-003 — ACCEPT
        ↓
RLY-S12-DESIGN-ACCEPT-001
        ↓
RLY-S12-AUTH-001
        ↓
Initial implementation checkpoint
08676c0332d0f14a190bf217c43b0ee29a3bc636
        ↓
RLY-S12-EVAL-001 — REWORK
(test-evidence gap only)
        ↓
Bounded test-only rework
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d
        ↓
RLY-S12-EVAL-002 — ACCEPT
        ↓
RLY-S12-ACCEPT-001
HUMAN ACCEPTED
```

## Design finding disposition

```text
RLY-S12-DREV1-F001 — RESOLVED
preserve exact provider binding/access selection

RLY-S12-DREV1-F002 — RESOLVED
capture and atomically re-check Slice 1.1 state_revision

RLY-S12-DREV1-F003 — RESOLVED
live GitHub repository identity validation

RLY-S12-DREV2-F004 — RESOLVED
pre/post snapshot provider identity bracketing
```

## Accepted implementation behavior

- `Project.primary_repository` remains the sole project repository authority.
- Provider-access selection requires durable Project repository equality, `ACTIVE / READY`, confirmed repository membership, stable provider ID/node identity, and captures `state_revision`.
- Repository-scoped installation tokens remain ephemeral.
- BRANCH/TAG/COMMIT_SHA are explicit selector kinds; movable refs resolve once.
- Exact commit object identity and root tree identity are verified.
- Nonrecursive deterministic tree traversal rejects truncated tree evidence.
- `.relay` direct entries are proven from the commit tree.
- Exact registry/artifact blobs are fetched by tree-selected SHA.
- Returned blob SHA and raw SHA-256 digest are verified.
- Registered symlink/submodule/unsupported entries fail closed.
- Provider repository identity is checked before and after the complete snapshot proof.
- The final local transaction re-checks exact Slice 1.1 access revision, readiness, status, repository membership, node identity, and Project repository authority.
- First-seen core Artifacts bind once; later identical observations preserve the first commit binding.
- Missing Decision, Artifact conflict, stale access, duplicate BaselineId, and integrity failures roll back all new Artifact/Baseline writes.

## Persistence

No migration v3 was introduced. Slice 1.2 reuses:

```text
projects
artifacts
decisions
baselines
github_installations
github_installation_repositories
```

All provider I/O completes before the final `BEGIN IMMEDIATE` transaction.

## Independent evaluation and bounded rework

The first implementation evaluation found insufficiently explicit deterministic regression evidence for several accepted Revision-2 / Revision-3 race boundaries.

```text
RLY-S12-EVAL-001 — REWORK
```

This was not a production-code defect and required no architecture or contract escalation.

Bounded rework added only:

```text
tests/unit/test_repository_baseline_races.py
```

covering explicit provider ID/node/full-name mismatch before and after snapshot proof, final provider unavailability, a local authority revision change after the post-snapshot provider check, and the no-network-I/O-inside-final-write-transaction rule.

The resulting accepted candidate is:

```text
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d
```

## Quality evidence

GitHub Actions run:

```text
36380535532
```

Quality:

```text
uv sync --frozen --group dev    PASS
Ruff format                     PASS
Ruff lint                       PASS
Pyright                         PASS — 0 errors / 0 warnings
pytest                          PASS — 436 passed
uv build                        PASS
```

## Model execution provenance

```text
Preferred implementation/rework model:
GPT-5.6 Luna

Executing implementation/rework model:
GPT-5.6 Sol

Independent evaluation model:
GPT-5.6 Sol

Deviation:
the active session remained GPT-5.6 Sol;
review independence was role/process independence rather than model diversity.
```

## Scope boundaries preserved

Not implemented or authorized:

```text
Slice 1.3
remote .relay creation or repair
GitHub write endpoints
Project repository mutation
branch creation
commit creation
pull requests
local Git/clone/worktree management
generic provider framework
background workers
UI
agent execution
```

## Final accepted state

```text
Design:
ACCEPTED

Implementation:
ACCEPTED

ADR-0008:
LOCKED / ACCEPTED

Memory:
LOCKED / ACCEPTED

Slice 1.2:
COMPLETE / ACCEPTED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED
```

This exact memory revision is historical authority and must not be edited in place.
