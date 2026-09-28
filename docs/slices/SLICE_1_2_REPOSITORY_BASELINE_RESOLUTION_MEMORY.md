# Slice 1.2 — Repository Baseline Resolution Memory

**Status:** IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION  
**Record state:** WORKING / NOT LOCKED  
**Phase:** 1  
**Slice:** 1.2  
**Accepted design head:** `4acd6be1f93058d1efcafc66a78fc1a9726c16ba`  
**Technical implementation checkpoint:** `08676c0332d0f14a190bf217c43b0ee29a3bc636`

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
Slice 1.2 implementation
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

## Implementation summary

Added provider-neutral baseline package:

```text
src/relay_engine/repository_baseline/
```

with strict selector/result/error semantics, GitHub snapshot orchestration, and atomic verified-baseline persistence.

Extended the accepted GitHub integration only with read behavior needed for:

```text
repository identity reads
commit ref resolution
exact Git commit reads
nonrecursive Git tree reads
exact Git blob reads
repository-scoped access selection/token use
```

Extended the accepted repository contract with a pure `RepositorySnapshotEntry` / `validate_repository_snapshot` seam so GitHub commit-pinned evidence and filesystem validation share the same authority rules.

## Implemented authority behavior

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

No migration v3 was introduced.

Slice 1.2 reuses:

```text
projects
artifacts
decisions
baselines
github_installations
github_installation_repositories
```

All provider I/O completes before the final `BEGIN IMMEDIATE` transaction.

## Dependencies

```text
New runtime dependencies: NONE
```

Slice 1.2 reuses the accepted Slice 1.1 PyJWT/cryptography installation and standard-library HTTP transport.

## Quality evidence

Exact technical checkpoint:

```text
08676c0332d0f14a190bf217c43b0ee29a3bc636
```

GitHub Actions run:

```text
36379051969
```

Quality:

```text
uv sync --frozen --group dev    PASS
Ruff format                     PASS
Ruff lint                       PASS
Pyright                         PASS — 0 errors / 0 warnings
pytest                          PASS — 427 passed
uv build                        PASS
```

New deterministic coverage includes strict selector semantics, exact snapshot validation, `.relay` shape, symlink/submodule rejection, raw digest mismatch, F007 first-binding reuse, missing-Decision rollback, stale-access rollback, duplicate BaselineId, provider identity bracketing, moving-ref pinning, tree truncation, GitHub commit/tree/blob parsing, ref error classification, exact blob size validation, and durable Project repository authority at access-selection capture.

## Model execution provenance

```text
Preferred implementation model:
GPT-5.6 Luna

Executing implementation model:
GPT-5.6 Sol

Deviation:
preferred bounded implementation model unavailable in the active session;
Sol executed against the exact accepted design contract.
```

## Scope boundaries preserved

Not implemented:

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

## Candidate state

```text
Design:
ACCEPTED

Implementation:
COMPLETE / PENDING INDEPENDENT EVALUATION

ADR-0008:
PROPOSED / VALIDATED / PENDING ACCEPTANCE

Memory:
WORKING / NOT LOCKED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED
```

This memory must remain unlocked until independent implementation evaluation and Human Authority acceptance complete.
