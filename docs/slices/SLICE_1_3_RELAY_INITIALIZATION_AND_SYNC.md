# Slice 1.3 — `.relay/` Initialization and Sync

**Status:** REVIEW  
**Design revision:** Revision 1  
**Design authority:** `RLY-S13-DESIGN-AUTH-001`  
**Authorized baseline:** `eb6b3797fb1b317e9158444b9c9dbe469b2ee313`  
**Role:** Architect / Contract Designer  
**Preferred model:** GPT-5.6 Sol  
**Executing model:** GPT-5.6 Sol  
**Implementation:** NOT AUTHORIZED  
**Date:** 2026-09-28

---

# 1. Objective

Design the minimum safe mechanism by which Relay may recognize, initialize, or synchronize its accepted repository-side contract through GitHub while preserving all accepted authority, provenance, and fail-closed behavior from Slices 0.6, 1.1, and 1.2.

The target product capability is:

```text
accepted Relay project authority
        ↓
captured GitHub repository access
        ↓
inspect exact default-branch head
        ↓
classify repository-contract state
        ↓
validate desired target contract locally
        ↓
explicit write-capability check
        ↓
prepare one atomic Git commit
        ↓
non-force compare-and-swap ref update
        ↓
verify exact resulting snapshot
        ↓
return exact commit evidence
```

This slice owns the safe repository-write transport for Relay contract synchronization. It does not own generation of future project/slice documents, automatic human authorization, pull-request workflow, agent execution, or persistence of a new Relay Baseline.

---

# 2. Accepted starting boundary

Slice 1.3 starts from the following accepted behavior.

## 2.1 Repository contract

Schema v1 remains:

```text
.relay/
└── registry.json
```

`.relay/registry.json` is the sole direct `.relay/` child. Ordinary registered artifacts remain at natural repository-relative paths.

`RepositoryRegistry` already enforces:

- exact `project_id` and `RepositoryRef` identity;
- normative artifact ordering;
- unique ArtifactIds and paths;
- canonical-pointer integrity;
- immutable/lockable supersession rules;
- living-projection state rules;
- safe repository-relative artifact paths.

An empty `artifacts` tuple and empty `canonical` tuple are valid schema-v1 values, so a minimal initialized registry does not require inventing documents that belong to later slices.

## 2.2 Transition validation

`validate_registry_transition(previous, current)` already protects repository identity, historical immutability, canonical-key continuity, Artifact byte identity, living-projection replacement rules, and supersession lineage.

Slice 1.3 reuses this function. It does not create a competing transition model.

## 2.3 Snapshot validation

`validate_repository_snapshot(...)` already validates commit-pinned `.relay/registry.json` bytes plus exact registered artifact bytes and modes.

Slice 1.3 reuses this validator both when inspecting an existing initialized repository and when validating a proposed post-write snapshot.

## 2.4 GitHub access authority

Slice 1.1 already persists installation permission state, repository membership, provider repository identity, and monotonic `state_revision`.

`GitHubRepositoryAccessSelection` already captures:

```text
project_id
installation_id
github_repository_id
github_node_id
RepositoryRef
expected_state_revision
```

Slice 1.3 preserves this as the local/provider authority bracket.

## 2.5 Read-side proof

Slice 1.2 already proves:

```text
selected ref
→ canonical commit
→ exact commit tree
→ exact registry blob
→ exact registered artifact blobs
```

and brackets the provider repository identity before and after snapshot reads.

Slice 1.3 must not weaken that proof model merely because the operation now has a write side.

---

# 3. Current implementation facts that constrain the design

The current GitHub integration intentionally has a read-only ceiling:

```text
contents: read
metadata: read
```

`permission_policy_allows(...)` currently requires that exact profile, and installation-token minting requests `contents: read`.

The existing permission model already represents `READ`, `WRITE`, and `ADMIN`, so Slice 1.3 does not need a new persistence schema merely to represent write capability.

The current `GitHubClient` contains read-side repository/ref/commit/tree/blob methods but no repository mutation methods.

These facts lead to a bounded extension rather than a new provider framework.

---

# 4. Design decisions

## S13-D01 — Preserve schema v1

Slice 1.3 does not change `.relay/registry.json` schema version and introduces no persistence migration.

```text
schema_version = 1
```

No migration v3 is authorized or required.

## S13-D02 — Two exact installation permission profiles are allowed

The GitHub installation is considered policy-compliant only when its effective repository permissions are exactly one of:

```text
READ PROFILE
contents: read
metadata: read
```

or:

```text
WRITE PROFILE
contents: write
metadata: read
```

No other permission is accepted.

In particular, Relay does not request or tolerate:

```text
administration
pull_requests
workflows
issues
members
secrets
or unrelated repository permissions
```

This preserves an explicit permission ceiling while allowing existing read-only installations to remain usable.

## S13-D03 — Read operations remain read-scoped

A write-capable installation does not cause ordinary read operations to mint write-capable tokens.

Existing baseline-resolution and inspection paths continue to request:

```text
contents: read
```

A distinct write-token path may request:

```text
contents: write
```

only for the captured repository and only for an explicit synchronization operation.

## S13-D04 — Write capability is checked independently from general readiness

`ACTIVE / READY` remains the general provider-access condition.

A Slice 1.3 write additionally requires the stored installation snapshot to contain the exact WRITE PROFILE.

A READ PROFILE installation remains usable for Slice 1.1/1.2 behavior but a write attempt fails closed with a typed `WRITE_PERMISSION_REQUIRED` outcome before any remote mutation.

No automatic permission upgrade or reauthorization flow is introduced.

## S13-D05 — Slice 1.3 writes only the existing default branch

The write target is the repository default branch observed during the operation.

Slice 1.3 does not:

- create a branch;
- choose an arbitrary caller-supplied branch;
- create a pull request;
- merge a pull request;
- force-update a ref;
- bypass branch protection.

If the default branch rejects the update because of repository rules or branch protection, Relay reports the provider rejection and performs no workaround.

## S13-D06 — Use the Git Data API, not sequential Contents API writes

Initialization/synchronization may change multiple registered artifact files plus `.relay/registry.json`.

Sequential file-by-file commits could expose a repository commit in which registry bytes and registered artifact bytes disagree.

Therefore the write mechanism is:

```text
create changed blobs
        ↓
create one tree based on exact base tree
        ↓
create one commit with exact expected head as parent
        ↓
update default-branch ref once
```

The single ref movement is the visibility boundary.

This is the minimum mechanism that preserves the Slice 1.2 same-commit snapshot invariant for multi-file synchronization.

## S13-D07 — No force updates

The default-branch ref update MUST use GitHub's non-force semantics.

The new commit MUST name the exact observed base head as its single parent.

If another writer advances the branch before Relay updates the ref, Relay's update fails rather than overwriting or rebasing over the new work.

Relay never retries by silently rebuilding on a new head.

## S13-D08 — Repository state is classified before mutation

The exact default-branch head is classified as one of five states:

### `UNINITIALIZED`

No `.relay` entry exists at the exact head.

### `CURRENT`

A valid schema-v1 contract exists and the requested target registry plus all target registered artifact bytes already match the exact head.

No write occurs.

### `SYNCHRONIZABLE`

A valid schema-v1 contract exists, the requested target registry is a valid transition from it, and the proposed target snapshot can be constructed without unsupported path/object conflicts.

### `CONFLICT`

The current contract is valid, but the requested target cannot be applied without violating transition rules, overwriting an unsupported object/path shape, or proceeding from an obsolete expected head.

### `INVALID`

`.relay` exists but the exact head does not satisfy the accepted schema-v1 repository contract or its project/repository identity.

Relay does not repair `CONFLICT` or `INVALID` repositories automatically.

## S13-D09 — Initialization is fail-closed

Initialization is permitted only from `UNINITIALIZED`.

If `.relay` already exists in any form, Relay does not overwrite it under initialization semantics.

The target registry may be either:

- the minimal valid registry with no registered artifacts; or
- a caller-supplied valid schema-v1 registry whose complete registered artifact bytes are included in or already satisfied by the proposed target snapshot.

This permits one atomic initial commit without inventing a second initialization format.

## S13-D10 — Synchronization is a validated registry transition

For an initialized repository, the proposed target registry MUST pass:

```text
validate_registry_transition(current_registry, target_registry)
```

The target registry must retain the exact Relay `project_id` and full `RepositoryRef`.

No synchronization path can mutate project repository identity.

## S13-D11 — The write set is contract-bounded

Caller-supplied file writes may target only paths represented by Artifact revisions in the target registry.

The caller does not supply `.relay/registry.json`; Relay serializes it deterministically from the validated target `RepositoryRegistry`.

Writes under `.relay/` other than `.relay/registry.json` are prohibited.

Slice 1.3 does not perform arbitrary source-code edits, deletes, renames, chmod operations, or repository cleanup.

For an existing artifact path, the current regular-file mode is preserved. A newly created registered artifact uses mode `100644`.

## S13-D12 — Candidate bytes must satisfy the target registry before any visible write

Before updating a Git ref, Relay constructs the logical target snapshot from:

```text
exact base snapshot
+
authorized artifact writes
+
deterministically serialized target registry
```

Every target registry Artifact revision must resolve to exact target bytes whose SHA-256 equals its registered `content_digest`.

Unchanged registered artifacts must already exist at the base head and match the target registry.

The resulting logical snapshot must satisfy the accepted repository-contract validation semantics before any branch ref is mutated.

## S13-D13 — Provider identity is bracketed more strictly for writes

Before preparing a write, immediately before ref mutation, and after ref mutation Relay verifies the same:

```text
github_repository_id
node_id
full_name
default_branch
```

The repository must also remain non-archived.

A rename, transfer, old-path reuse, default-branch change, archive transition, or inability to establish identity fails closed.

## S13-D14 — Local access authority is rechecked immediately before visibility

After blobs/tree/commit may have been prepared but before moving the default-branch ref, Relay rechecks the captured Slice 1.1 authority:

```text
Project.primary_repository
installation_id
ACTIVE / READY
expected state_revision
repository membership
github_repository_id
node_id
full_name
WRITE PROFILE
```

If this recheck fails, the branch ref is not mutated.

Git objects already created but unreachable from a ref may remain at the provider; they carry no repository authority and require no cleanup operation.

## S13-D15 — Remote head is rechecked immediately before ref update

Immediately before the non-force update Relay resolves the exact target branch again.

It MUST still equal the captured base commit SHA.

Otherwise the operation returns `CONFLICT` and does not move the ref.

## S13-D16 — There is no claimed GitHub/SQLite atomic transaction

Slice 1.3 explicitly does not claim atomicity between local Relay state and GitHub.

The guarantee is observability-based:

- all candidate validation occurs before ref visibility;
- local authority is checked immediately before the write;
- the ref update is one provider-side visibility event;
- local/provider authority and exact resulting bytes are checked again after the write;
- ambiguous post-write states return the exact created commit SHA for reconciliation.

No database write transaction is held across network I/O.

## S13-D17 — Post-write snapshot verification is mandatory

After a successful ref update Relay resolves the default branch and requires it to equal the newly created commit SHA.

Relay then reads that exact commit/tree/registry/artifact snapshot and validates it with the accepted repository-contract semantics.

Success is returned only when the exact visible commit proves the requested target registry and bytes.

## S13-D18 — No automatic rollback after a visible commit

If the default-branch ref moved successfully but subsequent authority or snapshot verification fails, Relay does not attempt a compensating force push or automatic reverse commit.

The result is a typed post-write failure carrying the exact written commit SHA.

Human/operator reconciliation is required before another mutation.

This avoids turning one uncertain remote mutation into two.

## S13-D19 — Idempotency is target-state based

A retry first inspects the new exact default-branch head.

If the requested target registry and registered bytes are already present and valid, Relay returns `CURRENT` / `ALREADY_CURRENT` and creates no additional commit.

Therefore a lost client response after a successful write can be recovered without a durable synchronization-attempt table.

Concurrent identical writers may race; at most one ref update succeeds. A subsequent retry of the loser observes the target state and returns `ALREADY_CURRENT`.

## S13-D20 — No automatic Baseline persistence

A successful repository synchronization returns the exact resulting `CommitRef` but does not create a Relay `Baseline`.

If the caller needs an authoritative Baseline, it invokes the already accepted Slice 1.2 commit-pinned baseline-resolution path separately against that exact commit.

This keeps repository mutation and Baseline acceptance/provenance as separate authorities.

## S13-D21 — No new persistent state

Slice 1.3 introduces:

```text
no new database table
no schema migration
no token cache
no durable sync queue
no background worker
```

The remote commit plus exact result SHA are the durable provider-side evidence for the write operation.

## S13-D22 — No new runtime dependency

The existing standard-library HTTP transport remains sufficient.

No GitHub SDK or local Git dependency is introduced.

---

# 5. Proposed domain/API contract

Names are normative at the semantic level; implementation may adjust private helper names without changing the contract.

## 5.1 Repository contract state

```text
RepositoryContractState
  UNINITIALIZED
  CURRENT
  SYNCHRONIZABLE
  CONFLICT
  INVALID
```

## 5.2 File write

```text
RepositoryArtifactWrite
  path: repository-relative path
  raw_bytes: exact bytes
```

Invariants:

- paths unique;
- no `.relay/*` path permitted;
- each path must be represented by exactly one Artifact revision in the target registry;
- byte digest must equal the target revision's `content_digest`.

## 5.3 Sync request

```text
RepositorySyncRequest
  selection: GitHubRepositoryAccessSelection
  target_registry: RepositoryRegistry
  artifact_writes: tuple[RepositoryArtifactWrite, ...]
```

The service, not the caller, determines:

```text
default branch
exact base head
base tree
registry serialization
new blob SHAs
new tree SHA
new commit SHA
```

The caller cannot request force, arbitrary refs, pull requests, or deletion.

## 5.4 Sync result

```text
RepositorySyncResult
  state: CURRENT
  prior_commit: CommitRef
  resulting_commit: CommitRef
  wrote_remote: bool
```

For a no-op:

```text
prior_commit == resulting_commit
wrote_remote == false
```

For a successful mutation:

```text
resulting_commit != prior_commit
wrote_remote == true
```

A successful result always identifies exact commit authority.

---

# 6. GitHub client extension contract

The current narrow client is extended only with the Git Data operations needed by S13-D06.

Required operations:

```text
create_git_blob(raw_bytes) -> blob_sha
create_git_tree(base_tree_sha, entries) -> tree_sha
create_git_commit(message, tree_sha, parent_sha) -> commit_sha
update_git_ref(branch, commit_sha, force=False) -> resolved_ref_sha
```

The existing read operations remain the source of repository/ref/commit/tree/blob verification.

The ref-update method MUST NOT expose `force=True` through the Slice 1.3 service.

The commit message is Relay-controlled and includes the target registry SHA-256 digest for auditability. Commit-message content is not authority and is never used to establish idempotency.

---

# 7. Permission contract

## 7.1 Installation policy

Accepted installation profiles after Slice 1.3 implementation would be exactly:

```text
{contents: read, metadata: read}
```

or:

```text
{contents: write, metadata: read}
```

Any other permission set remains `PERMISSION_POLICY_VIOLATION`.

## 7.2 Token policy

Read token:

```text
repository_ids = [captured github_repository_id]
permissions = {contents: read}
```

Write token:

```text
repository_ids = [captured github_repository_id]
permissions = {contents: write}
```

The write token is minted only after the operation has established a write-capable stored installation profile.

---

# 8. Synchronization algorithm

Normative order:

```text
1. Validate request structure and target-registry identity.
2. Load Project and require Project.primary_repository == selection.repository.
3. Recheck captured local Slice 1.1 access selection.
4. Mint repository-scoped READ token.
5. Read provider repository identity; require ID/node/full_name match, non-archived.
6. Capture default_branch.
7. Resolve exact default-branch head and exact commit/root tree.
8. Inspect/classify `.relay` state at that exact head.
9. If current target is already exact, return ALREADY_CURRENT; no write token is minted.
10. For initialized state, validate current → target registry transition.
11. Construct and validate the complete logical target snapshot.
12. Require stored WRITE PROFILE.
13. Mint repository-scoped WRITE token.
14. Create only changed artifact blobs and target registry blob.
15. Create one target tree using the exact base tree.
16. Create one commit whose single parent is the exact captured head.
17. Recheck local access authority and WRITE PROFILE.
18. Re-read provider identity/default branch/non-archived state.
19. Re-resolve default-branch head; require exact captured head.
20. Update the exact default-branch ref with force=false.
21. Resolve branch; require exact new commit SHA.
22. Re-read provider identity/default branch/non-archived state.
23. Recheck local access authority for observability.
24. Read and validate exact resulting commit/tree/registry/artifact bytes.
25. Return exact prior/resulting CommitRefs.
```

Steps 14–16 can create unreachable Git objects before the final authority/head checks. They do not modify a repository ref and therefore do not become repository authority.

---

# 9. Error and conflict semantics

Provider transport/authentication/rate-limit errors retain existing typed GitHub failures and are translated into Slice 1.3 repository-sync errors.

Normative high-level outcomes include:

```text
RepositoryWritePermissionRequired
RepositorySyncInvalidRemote
RepositorySyncConflict
RepositorySyncAccessChanged
RepositorySyncProviderIdentityChanged
RepositorySyncDefaultBranchChanged
RepositorySyncProtectedBranch
RepositorySyncSnapshotIntegrityError
RepositorySyncPostWriteVerificationError
```

`RepositorySyncPostWriteVerificationError` MUST carry the exact commit SHA when the ref may already have moved.

Automatic retry is permitted only for a fresh top-level invocation that begins by re-inspecting current state. Internal hidden retry after a conflict is prohibited.

---

# 10. Concurrency and race guarantees

## 10.1 Concurrent branch writer

If another actor advances the default branch after Relay captures the head:

```text
head recheck fails
or
non-force ref update fails
```

Relay does not overwrite, rebase, merge, or silently retry.

## 10.2 Concurrent GitHub installation/access change

If `state_revision`, ACTIVE/READY state, repository membership, provider identity, or write permission changes before the ref update, Relay refuses the visible mutation.

If the change occurs after the final pre-write check but before/during the provider ref mutation, cross-system atomicity is impossible. The post-write rechecks surface the condition together with the exact resulting commit when applicable.

## 10.3 Rename/transfer/path reuse

Numeric repository ID, node ID, and full name must remain aligned with the captured `RepositoryRef`. A mismatch blocks the operation.

## 10.4 Default-branch change

The default branch is part of the write target bracket. Relay does not follow a changed default branch mid-operation.

## 10.5 Concurrent identical Relay operations

One non-force ref update may win. Others conflict. A fresh retry recognizes the exact target state and becomes a no-op.

---

# 11. Initialization semantics

For `UNINITIALIZED` repositories:

1. `.relay` must be absent from the exact base tree.
2. The target registry identity must exactly match the Relay project and repository.
3. All target Artifact bytes must be provable in the logical target snapshot.
4. Relay creates `.relay/registry.json` as part of the same single commit as any newly registered artifact bytes.
5. A concurrent actor creating `.relay` or advancing the branch causes conflict rather than overwrite.

If the target is the minimal registry, deterministic serialization represents:

```text
schema_version = 1
project_id = exact ProjectId
repository = exact Project.primary_repository
artifacts = ()
canonical = ()
```

No default project documents are invented by Slice 1.3.

---

# 12. Synchronization semantics

For `SYNCHRONIZABLE` repositories:

- existing valid historical records remain protected by `validate_registry_transition`;
- target living projections use their new ArtifactIds/revisions/digests according to existing governance;
- exact target artifact bytes are committed together with the target registry;
- unregistered ordinary repository files are not modified;
- files formerly registered but absent from the target registry are not deleted automatically;
- `.relay/registry.json` is always generated from the typed target model, never accepted as arbitrary caller bytes.

This makes Slice 1.3 a transport/enforcement boundary, not an artifact-authoring subsystem.

---

# 13. Post-write relationship to Slice 1.2

A successful Slice 1.3 result provides:

```text
CommitRef(repository=<exact RepositoryRef>, sha=<new exact SHA>)
```

That commit is not automatically a Relay Baseline.

To persist authoritative baseline state, a caller may separately request Slice 1.2 resolution using:

```text
COMMIT_SHA = exact Slice 1.3 resulting SHA
```

Slice 1.2 then independently proves provider identity and exact registry/artifact bytes before local Artifact/Baseline persistence.

This separation prevents repository synchronization from certifying its own durable Baseline authority.

---

# 14. Expected implementation change surface

Expected production surface:

| Dimension | Expected |
|---|---:|
| Existing production files touched | 3–5 |
| New production package | `repository_sync` |
| New production files | 3–4 |
| New runtime dependencies | 0 |
| Persistent schema changes | 0 |
| New migrations | 0 |
| New provider integrations | 0 |
| New GitHub permission names | 0 |
| Maximum GitHub installation ceiling | `contents:write + metadata:read` |
| Pull-request permission | 0 |
| Force-push capability | 0 |
| Background workers | 0 |

Likely existing files:

```text
src/relay_engine/integrations/github/client.py
src/relay_engine/integrations/github/service.py
src/relay_engine/integrations/github/__init__.py
possibly integrations/github/models.py or errors.py
```

Likely new package:

```text
src/relay_engine/repository_sync/
    __init__.py
    models.py
    errors.py
    service.py
```

Implementation may reduce this surface. Material expansion requires explanation and evaluator scrutiny.

---

# 15. Quality contract

Implementation must pass the repository's existing declared quality profile:

```text
FORMAT      uv run ruff format --check .
LINT        uv run ruff check .
TYPE_CHECK  uv run pyright
TEST        uv run pytest
BUILD       uv build
```

Green tooling is required evidence but is not engineering acceptance.

---

# 16. Acceptance criteria

## Identity and authority

- **A01** — Sync accepts one captured `GitHubRepositoryAccessSelection` and never derives a new Relay `RepositoryRef` from provider IDs.
- **A02** — `Project.primary_repository` remains the sole durable project-repository authority.
- **A03** — Target registry `project_id` must equal the selection project.
- **A04** — Target registry full `RepositoryRef` must equal the selection repository.
- **A05** — Provider repository ID, node ID, and full name are checked before write preparation.
- **A06** — Provider repository ID, node ID, full name, and default branch are rechecked immediately before ref mutation.
- **A07** — Provider repository identity/default branch are checked again after ref mutation.
- **A08** — Archived repositories cannot be mutated.
- **A09** — Captured local `state_revision` is rechecked immediately before ref mutation.
- **A10** — ACTIVE/READY state and repository membership are rechecked immediately before ref mutation.
- **A11** — Write permission is rechecked immediately before ref mutation.
- **A12** — No network I/O is performed inside a SQLite write transaction.

## Permissions and credentials

- **A13** — READ PROFILE remains accepted.
- **A14** — WRITE PROFILE becomes accepted.
- **A15** — Any permission set other than the two exact profiles is rejected.
- **A16** — Read operations mint only `contents:read` tokens even when installation ceiling is write-capable.
- **A17** — Write tokens are repository-narrowed to the captured GitHub repository ID.
- **A18** — Write tokens request only `contents:write`.
- **A19** — No token cache is introduced.
- **A20** — Read-only installations fail write attempts before remote mutation.

## Repository-state classification

- **A21** — Absence of `.relay` is `UNINITIALIZED`.
- **A22** — A valid exact target snapshot is `CURRENT` and causes no remote write.
- **A23** — A valid current registry plus valid non-no-op target transition is `SYNCHRONIZABLE` when path/object checks pass.
- **A24** — Valid current authority plus incompatible requested transition/path shape is `CONFLICT`.
- **A25** — Existing invalid `.relay` contract is `INVALID`.
- **A26** — Initialization never overwrites an existing `.relay` entry.
- **A27** — Invalid or conflicting repositories are not auto-repaired.

## Registry and artifact contract

- **A28** — Existing `RepositoryRegistry` schema v1 remains unchanged.
- **A29** — Existing `validate_registry_transition` is used for initialized sync.
- **A30** — Existing repository snapshot semantics are reused for current/target verification.
- **A31** — Relay deterministically serializes target registry bytes.
- **A32** — Caller cannot provide arbitrary registry bytes.
- **A33** — Caller artifact-write paths are unique and safe repository-relative paths.
- **A34** — Caller artifact-write paths cannot be under `.relay/`.
- **A35** — Every caller artifact write maps to a target registry Artifact revision.
- **A36** — Every written artifact byte digest equals target `content_digest`.
- **A37** — Every unchanged target Artifact is proven from exact base bytes.
- **A38** — Target snapshot has exactly `.relay/registry.json` as the direct `.relay` child.
- **A39** — New registered artifact files use regular mode `100644`.
- **A40** — Existing registered artifact file modes are preserved and must remain accepted regular-file modes.
- **A41** — Slice 1.3 performs no arbitrary deletes.
- **A42** — Slice 1.3 performs no arbitrary source-code or unregistered-file edits.

## Git object construction and visibility

- **A43** — Base head is resolved from the provider-reported default branch.
- **A44** — Exact base commit and tree are captured before target construction.
- **A45** — Only changed artifact blobs plus registry blob are newly created.
- **A46** — New tree is constructed from the exact base tree.
- **A47** — New commit has exactly the captured base head as parent.
- **A48** — Ref update targets only the captured default branch.
- **A49** — Ref update is non-force.
- **A50** — No branch is created.
- **A51** — No pull request is created.
- **A52** — No merge is performed.
- **A53** — No branch-protection bypass is attempted.
- **A54** — Head is re-resolved immediately before ref update and must still equal the captured base SHA.
- **A55** — A concurrent head change blocks mutation rather than causing hidden retry/rebase.

## Verification and failure semantics

- **A56** — After ref update, branch head must resolve to exact created commit SHA.
- **A57** — Exact resulting commit/tree/registry/artifact bytes are re-read and validated.
- **A58** — Successful result returns exact prior and resulting `CommitRef`s.
- **A59** — No-op returns same prior/resulting commit and `wrote_remote=false`.
- **A60** — Post-write failure that may follow visible mutation carries exact created commit SHA.
- **A61** — No automatic rollback/force push occurs after visible mutation.
- **A62** — Provider authentication, rate-limit, permission, unavailable-object, and repository-unavailable failures remain typed.
- **A63** — Protected/default-branch rejection is surfaced without workaround.
- **A64** — Hidden retry after conflict is prohibited.

## Idempotency

- **A65** — Retry begins with a fresh repository/head inspection.
- **A66** — If target state is already exact, retry returns `ALREADY_CURRENT` without a new commit.
- **A67** — Concurrent identical operations cannot both overwrite branch history.
- **A68** — No persistent sync-attempt table is required for idempotency.

## Baseline and persistence boundaries

- **A69** — Successful sync does not automatically insert/update a Relay `Baseline`.
- **A70** — Successful sync does not rewrite existing core `Artifact.commit` bindings.
- **A71** — Resulting SHA can be supplied separately to accepted Slice 1.2 COMMIT_SHA resolution.
- **A72** — No persistence migration is introduced.
- **A73** — No new durable sync queue/state is introduced.

## Scope and simplicity

- **A74** — No generic provider-write framework is introduced.
- **A75** — No local Git clone/worktree dependency is introduced.
- **A76** — No new runtime dependency is introduced.
- **A77** — No automatic document generation is introduced.
- **A78** — No agent execution is introduced.
- **A79** — No Slice 1.4 behavior is introduced.
- **A80** — Material expansion beyond the declared change surface is explicitly reported for evaluation.

---

# 17. Required tests

At minimum, implementation evidence must cover:

```text
read-only installation remains READY and read-capable
write-profile installation becomes READY
extra permissions remain policy violations
read token from write-profile installation is still read-scoped
write attempt on read-profile installation fails before writes
repository-scoped write-token request shape
UNINITIALIZED classification
CURRENT no-op classification
valid SYNCHRONIZABLE transition
INVALID existing .relay refusal
CONFLICT transition refusal
initialization with minimal registry
initialization with registered artifacts
artifact digest mismatch refusal
unregistered write-path refusal
.relay extra-entry refusal
symlink/submodule/non-regular path refusal
provider ID/node/full-name mismatch before write
archived repository refusal
default-branch change before write
state_revision change before write
permission downgrade before write
repository-membership removal before write
concurrent head advancement before ref update
non-force ref update request
branch-protection/provider rejection
multi-file single-tree/single-commit construction
post-write exact head verification
post-write exact snapshot verification
post-write authority-change error carries commit SHA
lost-response/retry target already current
concurrent identical write loser becomes no-op on fresh retry
no automatic Baseline persistence
no migration/schema change
```

Race tests must prove call ordering, not merely final exceptions.

---

# 18. Out of scope

Explicitly out of scope for Slice 1.3:

```text
pull-request workflow
branch creation strategy
merge automation
force push
repository-rule bypass
GitHub administration permissions
multi-provider abstraction
local clones/worktrees
background sync workers
scheduled synchronization
automatic conflict resolution
three-way merge
file deletion/rename engine
automatic authoring of project/slice documents
Project/Slice CRUD
board projection
agent execution
persistent job orchestration
new database schema
```

If implementation discovers that any of these is required, it escalates rather than silently expanding scope.

---

# 19. Design rationale

The central design choice is the Git Data API single-commit/ref-update path.

A simpler single-file Contents API call is sufficient only for an empty-registry initialization. It is not sufficient for general synchronization because target registry and registered artifacts must become visible at the same commit. Designing initialization and synchronization as two unrelated write mechanisms would duplicate race, permission, and identity logic and would create a weaker multi-file path later.

The proposed mechanism is therefore slightly more explicit at the provider boundary but materially simpler at the authority boundary:

```text
one target snapshot
one commit
one ref visibility event
one verification path
```

It also avoids the additional permissions and workflow state required by automatic pull requests.

---

# 20. Design completion gate

Revision 1 is complete when this document and its registry entry are committed on the design branch and CI passes.

Next role:

```text
Independent Design Reviewer — GPT-5.6 Sol
```

Allowed design-review outcomes:

```text
ACCEPT
REVISE
ESCALATE
```

A design-review ACCEPT does not authorize implementation.

**STOP after design submission.**
