# Repository Baseline Resolution — Slice 1.2

**Status:** IMPLEMENTED / PENDING INDEPENDENT EVALUATION  
**Authority:** Slice 1.2 Design Revision 1 + Revision 2 + Revision 3  
**Accepted design head:** `4acd6be1f93058d1efcafc66a78fc1a9726c16ba`  
**Technical implementation checkpoint:** `08676c0332d0f14a190bf217c43b0ee29a3bc636`  
**Scope:** Read-only GitHub repository snapshot proof and atomic immutable Relay Baseline persistence

## Purpose

Slice 1.2 turns a currently authorized Slice 1.1 GitHub repository selection into a verified immutable Relay `CommitRef`, proves the accepted `.relay/registry.json` and every registered artifact byte against that exact commit, and atomically materializes any first-seen core `Artifact` values plus one `Baseline`.

It closes the GitHub-side trust-boundary deferral left by Slice 0.6 without adding a second repository-registration authority. `Project.primary_repository` remains the sole Relay project repository authority.

## Package boundary

Provider-neutral baseline orchestration lives under:

```text
src/relay_engine/repository_baseline/
    __init__.py
    errors.py
    models.py
    persistence.py
    service.py
```

The GitHub adapter adds only read operations and provider-specific values under:

```text
src/relay_engine/integrations/github/
```

The accepted repository contract gains one pure commit-pinned snapshot validation seam in:

```text
src/relay_engine/repository_contract/snapshot.py
```

No accepted core `Project`, `RepositoryRef`, `CommitRef`, `Artifact`, or `Baseline` schema changes were required.

## Provider-access selection

Slice 1.2 captures one ephemeral `GitHubRepositoryAccessSelection` containing:

```text
ProjectId
installation_id
github_repository_id
github_node_id
RepositoryRef
expected_state_revision
```

Selection creation reads durable `Project.primary_repository` and requires exact equality. It also requires the Slice 1.1 binding to be `ACTIVE / READY` and the selected GitHub repository to remain in the confirmed repository set.

The selection is operation evidence only. It is not a second repository-registration record.

## Ref resolution and commit pinning

Selectors are explicit:

```text
BRANCH
TAG
COMMIT_SHA
```

Branch and tag selectors are provider inputs only. The service resolves them once and thereafter uses the canonical full commit SHA and descendant Git object SHAs. Full explicit commit selectors must resolve to exactly the requested SHA.

## Provider identity bracketing

A repository-scoped short-lived installation token is minted from the captured provider IDs.

Before any snapshot reads, Relay fetches live repository metadata and requires exact equality of:

```text
GitHub repository ID
node_id
canonical full_name
```

against the captured selection.

After all commit/tree/registry/artifact reads and validations complete, Relay repeats the same identity proof using the same captured selection. Rename, transfer, redirect identity change, old-path reuse, or inability to establish the final identity fails closed before local persistence.

Relay makes no claim of an atomic transaction spanning GitHub and SQLite.

## Commit/tree/blob snapshot proof

The read-only proof chain is:

```text
explicit selector
→ canonical commit SHA
→ exact Git commit object
→ root tree SHA
→ deterministic nonrecursive subtree traversal
→ complete direct .relay entries
→ exact .relay/registry.json blob
→ every registry-declared artifact path
→ exact Git blob bytes
→ raw SHA-256 verification
```

Every requested tree response must identify the requested SHA and be non-truncated. Registered symlinks, submodules, unsupported object types, missing paths, unexpected direct `.relay/` entries, blob-SHA mismatches, and content-digest mismatches fail closed.

The Git blob client validates base64 content and declared decoded byte length before bytes enter repository-contract validation.

## Repository-contract reuse

`validate_repository_snapshot` shares accepted Slice 0.6 semantics rather than duplicating them in the GitHub adapter. It validates:

- safe unique repository-relative paths;
- schema-v1 direct `.relay/` shape;
- exact registry project/repository identity;
- ordinary-file modes for registered artifacts;
- tree-selected SHA versus returned blob SHA;
- exact SHA-256 content digests.

Existing filesystem repository-contract behavior remains unchanged.

## Stable core Artifact binding

First verified materialization of a registry `ArtifactId` creates one immutable core `Artifact` bound to the verified commit where it was first materialized.

A later verified baseline may reuse that same ArtifactId when repository, path, artifact type, and content digest agree. Its original `Artifact.commit` is not rewritten. Changed bytes require a different registry ArtifactId.

This preserves the accepted Slice 0.6 F007 invariant:

```text
one ArtifactId → one immutable core Artifact payload
```

## Atomic local persistence

All provider I/O completes before Relay opens the final SQLite write transaction.

Inside one `BEGIN IMMEDIATE` transaction Relay re-checks:

```text
Project exists
Project.primary_repository is unchanged
same GitHub binding exists
state_revision == captured expected_state_revision
binding is ACTIVE / READY
selected repository is still present
stored provider node_id/full_name still match
```

Only after those checks pass may Relay:

```text
materialize missing immutable Artifacts
verify existing Artifact bindings
verify explicit Decision IDs
insert one immutable Baseline
```

Any failure rolls back all new Artifact/Baseline writes. No hidden retry refreshes authorization evidence.

## Persistence schema

Slice 1.2 reuses existing tables:

```text
projects
artifacts
decisions
baselines
github_installations
github_installation_repositories
```

Migration v3 was not required.

## Deliberate exclusions

Slice 1.2 contains no GitHub write method, repository mutation, `.relay/` creation or repair, local Git/clone/worktree subsystem, generic VCS/provider framework, background worker, UI, or agent execution.

Slice 1.3 remains separately unauthorized.
