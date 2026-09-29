# Repository Initialization and Synchronization — Slice 1.3

**Status:** IMPLEMENTED / ACCEPTED  
**Authority:** Slice 1.3 Design Revision 1 + Revision 2 + Revision 3 + Revision 4  
**Accepted design head:** `0ba9d3ded4b068c61ca7095b02c751daf0a98fc9`  
**Accepted technical result:** `9b5166d1e95aefeb177d30c29f943f45a591ea05`  
**Independent implementation evaluation:** `RLY-S13-EVAL-002` — ACCEPT  
**Human acceptance:** `RLY-S13-ACCEPT-001`  
**Scope:** Human-authorized GitHub repository-contract initialization and synchronization

## Purpose

Slice 1.3 adds the minimum safe write boundary needed for Relay to recognize, initialize, and synchronize the accepted schema-v1 `.relay` repository contract without weakening project authority, repository provenance, or fail-closed race behavior.

`Project.primary_repository` remains the durable project-repository authority. A successful repository mutation returns exact commit evidence but does not certify or persist a Relay Baseline.

## Preparation and exact Human Authority

Repository synchronization begins with read-only preparation. Relay proves the current provider repository identity, default branch, exact head, repository-contract state, target transition, target paths, and target bytes before constructing `RepositorySyncSubjectV1`.

The exact subject binds:

```text
project_id
RepositoryRef
installation_id
GitHub repository ID / node ID
expected state_revision
expected default branch
expected base CommitRef
target registry digest
ordered artifact-write digests
```

Human Authority persists a dedicated immutable `RepositoryMutationAuthorization` for that exact subject. It is project/exact-subject scoped and contains no `BaselineId`, `GateId`, or `SliceId`. Existing lifecycle `AuthorizationGrant` / `HandoverGate` semantics remain orthogonal.

## Permission boundary

Two exact installation profiles are accepted:

```text
READ  = contents:read  + metadata:read
WRITE = contents:write + metadata:read
```

Ordinary reads remain read-scoped even for write-capable installations. A write-capable repository token is minted only after exact Human mutation authority is proven. The token is narrowed to the captured repository.

Slice 1.3 adds no pull-request, workflow, administration, force-push, or branch-creation permission.

## Repository state and write construction

Repository contract state is classified as:

```text
UNINITIALIZED
CURRENT
SYNCHRONIZABLE
CONFLICT
INVALID
```

`CURRENT` requires the parsed registry and the actual tree-selected registry bytes to equal Relay's deterministic target serialization.

For a real mutation Relay creates:

```text
changed artifact blobs
+ deterministic registry blob
        ↓
one tree from the exact captured base tree
        ↓
one commit with the exact base head as its single parent
        ↓
one non-force update of the existing provider-reported default branch
```

No hidden rebase, merge, force update, branch creation, or automatic conflict resolution exists.

## Preservation and path rules

Existing unregistered files cannot be overwritten merely because a target registry begins governing the path. Exact existing regular-file bytes may be adopted without mutation; otherwise the operation conflicts.

`.github/workflows/**` may remain unchanged or be adopted by exact bytes, but Slice 1.3 cannot mutate workflow content or mode under the contents-only permission ceiling.

Repositories without an existing default-branch head are not bootstrapped.

## Race and failure guarantees

Before ref visibility Relay rechecks exact Human mutation authority, local installation/access authority, `state_revision`, repository membership, WRITE permission, provider identity, default branch, archive state, and branch head.

An indeterminate ref update is reconciled by observation and is never blindly retried:

```text
new commit observed → continue exact post-write verification
base commit observed → typed non-visible failure
other/unreadable head → typed post-write reconciliation failure
```

Visible post-write failures carry the exact created commit SHA when reconciliation may be required.

## Exact post-write verification

Relay rereads the visible branch head, exact commit, tree, registry bytes, and registered artifacts. The actual visible `.relay/registry.json` bytes must equal the deterministic target registry bytes before success.

The final result is:

```text
state = CURRENT
prior_commit = exact prior CommitRef
resulting_commit = exact resulting CommitRef
wrote_remote = true | false
```

A fresh exact-target retry is a no-op with `wrote_remote=false`.

## Persistence

SQLite migration v3 adds only immutable repository-mutation authority persistence:

```text
repository_mutation_authorizations
+ project/subject index
```

No SliceId/BaselineId/GateId is introduced into that authority record, and no durable sync queue, attempt table, token cache, worker state, or new runtime dependency is added.

## Relationship to Slice 1.2

Repository synchronization does not create or update a Relay Baseline. A resulting SHA may be submitted separately to the accepted Slice 1.2 `COMMIT_SHA` verification path, which independently proves the repository snapshot before local Artifact/Baseline persistence.

## Acceptance evidence

The initial candidate `9456b31344d6dd880943eef04e99a9f5dc5da0d2` passed CI but received `RLY-S13-EVAL-001 — REWORK`.

The accepted result is:

```text
9b5166d1e95aefeb177d30c29f943f45a591ea05
```

Exact CI run `36600301960` passed:

```text
Ruff format    PASS
Ruff lint      PASS
Pyright        PASS — 0 errors / 0 warnings
pytest         PASS — 490 passed
uv build       PASS
```

## Deliberate exclusions

Slice 1.3 contains no PR workflow, branch creation strategy, merge automation, force push, ruleset bypass, generic provider abstraction, local Git clone/worktree subsystem, background worker, scheduled synchronization, automatic conflict resolution, Project/Slice CRUD, board projection, or agent execution.

Slice 1.4 remains separately unopened and unauthorized.
