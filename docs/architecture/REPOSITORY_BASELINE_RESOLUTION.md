# Repository Baseline Resolution — Slice 1.2

**Status:** IMPLEMENTED / ACCEPTED  
**Authority:** Slice 1.2 Design Revision 1 + Revision 2 + Revision 3  
**Accepted design head:** `4acd6be1f93058d1efcafc66a78fc1a9726c16ba`  
**Accepted technical result:** `9ed4a8da4d989fd41674ae59ef68ba4238c09b5d`  
**Independent implementation evaluation:** `RLY-S12-EVAL-002` — ACCEPT  
**Human acceptance:** `RLY-S12-ACCEPT-001`  
**Scope:** Read-only GitHub repository snapshot proof and atomic immutable Relay Baseline persistence

## Purpose

Slice 1.2 turns a currently authorized Slice 1.1 GitHub repository selection into a verified immutable Relay `CommitRef`, proves the accepted `.relay/registry.json` and every registered artifact byte against that exact commit, and atomically materializes any first-seen core `Artifact` values plus one `Baseline`.

It closes the GitHub-side trust-boundary deferral left by Slice 0.6 without adding a second repository-registration authority. `Project.primary_repository` remains the sole Relay project repository authority.

## Package boundary

Provider-neutral baseline orchestration lives under:

```text
src/relay_engine/repository_baseline/
```

The GitHub adapter adds only the read operations and provider-specific values needed for repository identity, ref resolution, exact Git commit/tree/blob reads, and repository-scoped access selection/token use.

The accepted repository contract gains one pure commit-pinned snapshot validation seam in:

```text
src/relay_engine/repository_contract/snapshot.py
```

No accepted core `Project`, `RepositoryRef`, `CommitRef`, `Artifact`, or `Baseline` schema changes were required.

## Provider-access authority

Slice 1.2 captures one ephemeral `GitHubRepositoryAccessSelection` containing:

```text
ProjectId
installation_id
github_repository_id
github_node_id
RepositoryRef
expected_state_revision
```

Selection creation reads durable `Project.primary_repository`, requires exact equality, requires the Slice 1.1 binding to be `ACTIVE / READY`, and requires the selected GitHub repository to remain in the confirmed repository set. The selection is operation evidence only; it is not a second repository-registration authority.

## Commit-pinned proof

Selectors are explicit `BRANCH`, `TAG`, or `COMMIT_SHA`. Branch/tag selectors resolve once. All later reads use the canonical full commit SHA or descendant Git object SHAs.

The proof chain is:

```text
captured provider selection
→ repository-scoped token
→ pre-snapshot provider identity proof
→ explicit selector resolution
→ exact Git commit object
→ root tree SHA
→ deterministic nonrecursive subtree traversal
→ complete direct .relay entries
→ exact .relay/registry.json blob
→ exact registered artifact blobs
→ raw SHA-256 verification
→ post-snapshot provider identity proof
→ final local authority guard
→ Artifact/Baseline persistence
```

Every requested tree response must identify the requested SHA and be non-truncated. Registered symlinks, submodules, unsupported object types, missing paths, unexpected direct `.relay/` entries, blob-SHA mismatches, and content-digest mismatches fail closed.

The same captured GitHub repository ID, node ID, and canonical full name are checked both before and after all remote snapshot reads. Relay does not claim an atomic transaction spanning GitHub and SQLite.

## Repository-contract reuse and F007

`validate_repository_snapshot` reuses accepted Slice 0.6 semantics for safe paths, schema-v1 `.relay/` shape, exact project/repository identity, regular-file modes, tree/blob identity, and exact SHA-256 digests.

First verified materialization of a registry `ArtifactId` creates one immutable core `Artifact` bound to the verified commit where it was first materialized. Later identical observations may reuse that same ArtifactId when repository, path, artifact type, and digest agree; the original `Artifact.commit` is not rewritten.

```text
one ArtifactId → one immutable core Artifact payload
```

## Atomic local persistence

All provider I/O completes before the final SQLite write transaction.

Inside one `BEGIN IMMEDIATE` transaction Relay re-checks:

```text
Project exists
Project.primary_repository unchanged
same GitHub binding exists
state_revision == captured expected_state_revision
binding ACTIVE / READY
selected repository still present
stored provider node_id/full_name still match
```

Only after those checks pass may Relay materialize missing immutable Artifacts, verify existing Artifact bindings, verify explicit Decision IDs, and insert one immutable Baseline. Any failure rolls back all new Artifact/Baseline writes.

No migration v3 was required.

## Acceptance evidence

The initial implementation checkpoint `08676c0332d0f14a190bf217c43b0ee29a3bc636` passed its quality suite. `RLY-S12-EVAL-001` then required additional deterministic race/identity regression evidence without changing production code.

The accepted technical result is:

```text
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d
```

Exact CI run `36380535532` passed:

```text
Ruff format    PASS
Ruff lint      PASS
Pyright        PASS — 0 errors / 0 warnings
pytest         PASS — 436 passed
uv build       PASS
```

## Deliberate exclusions

Slice 1.2 contains no GitHub write method, repository mutation, `.relay/` creation or repair, local Git/clone/worktree subsystem, generic VCS/provider framework, background worker, UI, or agent execution.

Slice 1.3 remains separately unauthorized.
