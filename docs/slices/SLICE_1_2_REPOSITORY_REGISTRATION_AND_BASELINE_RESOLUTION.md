# Slice 1.2 — Repository Registration and Baseline Resolution

**Document revision:** 1  
**Status:** REVIEW  
**Document class:** Lockable design record  
**Phase:** 1 — GitHub and Human-Controlled Project Workflow  
**Slice:** 1.2  
**Authorized baseline:** `1ec84fe0507f5e1a7dfff3098d285db628cb3649`  
**Slice opening:** `RLY-S12-OPEN-001`  
**Design authorization:** `RLY-S12-DESIGN-AUTH-001`  
**Reviewer next:** Independent Design Reviewer — GPT-5.6 Sol  
**Implementation:** NOT AUTHORIZED  
**Date:** 2026-09-27

---

# 1. Objective

Bind the already accepted provider-neutral project repository identity to a verified GitHub repository snapshot and create immutable Relay baselines whose commit and registered artifact bytes are proven to come from the same repository commit.

Slice 1.2 closes the most important trust-boundary deferral left by Slice 0.6:

```text
caller says these bytes came from commit C
```

becomes:

```text
Relay resolves commit C
        ↓
Relay reads C's Git tree
        ↓
Relay reads exact blobs named by that tree
        ↓
Relay validates .relay/registry.json + registered bytes
        ↓
Relay persists immutable Artifact/Baseline authority
```

The slice remains read-only with respect to GitHub.

It does not initialize `.relay/`, modify repository contents, create refs, or execute agents.

---

# 2. Governing accepted contracts

## 2.1 Project repository authority already exists

Accepted `Project` contains:

```python
Project(
    id: ProjectId,
    name: str,
    primary_repository: RepositoryRef,
)
```

`Project` is an insert-once static domain value.

Slice 1.2 MUST NOT create a second mutable project→repository authority table.

For an existing project:

```text
Project.primary_repository
```

is the registered Relay repository.

Slice 1.2 verifies provider access/identity against that value.

Future project creation may establish a new project's `primary_repository`, but Project CRUD remains Slice 1.4.

## 2.2 Commit identity already exists

Accepted `CommitRef` is provider-neutral:

```python
CommitRef(
    repository: RepositoryRef,
    sha: canonical 40- or 64-hex,
)
```

Slice 1.2 does not add branch/tag names to `CommitRef`.

Movable refs are selection inputs only.

## 2.3 Baseline already exists

Accepted `Baseline` remains:

```python
Baseline(
    id: BaselineId,
    project_id: ProjectId,
    commit: CommitRef,
    artifact_ids: tuple[ArtifactId, ...],
    decision_ids: tuple[DecisionId, ...],
)
```

No semantic change to this core model is required.

## 2.4 Slice 0.6 repository contract

Slice 0.6 already defines:

- strict `.relay/registry.json`;
- full `ProjectId` / `RepositoryRef` equality;
- exact SHA-256 registered-byte integrity;
- safe paths and regular-file requirements;
- explicit observation `CommitRef`;
- canonical/historical semantics;
- the F007 rule preventing one `ArtifactId` from materializing as unequal core `Artifact` payloads.

Slice 1.2 must preserve those semantics.

## 2.5 Slice 1.1 access boundary

Slice 1.1 already proves:

```text
GitHub installation:
ACTIVE / READY

repository:
present in confirmed access set

RepositoryRef:
explicit Relay RepositoryId + github.com + owner/repository
```

Slice 1.2 requires that confirmed selection before remote baseline resolution.

No new GitHub permission above:

```text
metadata: read
contents: read
```

is permitted.

---

# 3. Current GitHub facts used by the design

The current GitHub REST API supports the required read path using GitHub App installation tokens with `Contents: read`:

- `GET /repos/{owner}/{repo}/commits/{ref}` resolves a commit reference and returns canonical commit SHA;
- branch selectors can use `heads/<branch>`;
- tag selectors can use `tags/<tag>`;
- `GET /repos/{owner}/{repo}/git/commits/{sha}` returns the exact commit object and root tree SHA;
- `GET /repos/{owner}/{repo}/git/trees/{tree_sha}` returns Git tree entries and supports recursive traversal;
- recursive tree responses may be truncated and therefore cannot be blindly accepted;
- `GET /repos/{owner}/{repo}/git/blobs/{blob_sha}` returns exact blob bytes (base64 in the JSON representation) up to GitHub's supported blob-size limit;
- all of these required reads are available with repository `Contents: read`.

All provider response fields remain untrusted external input until validated.

---

# 4. Design decisions

## P1-D39 — No duplicate repository-registration model

Repository registration for Slice 1.2 is the accepted:

```text
Project.primary_repository
```

No new `RepositoryRegistration`, mutable binding table, or alternate project repository field is introduced.

A resolution command first loads the project and requires exact equality between:

```text
project.primary_repository
```

and the Slice 1.1 confirmed selected `RepositoryRef`.

Mismatch is an integrity/authority failure, not an update request.

## P1-D40 — Existing Project remains immutable

Slice 1.2 never modifies or reinserts an existing `Project`.

If the project does not exist, repository baseline resolution fails.

Project creation remains separately governed by Slice 1.4.

## P1-D41 — Explicit ref selector type

Movable repository selection is represented by a strict value equivalent to:

```python
RepositoryRevisionSelector(
    kind: BRANCH | TAG | COMMIT_SHA,
    value: str,
)
```

The selector is operation input, not immutable baseline identity.

`BRANCH` and `TAG` are explicit so a branch and tag with the same textual name cannot be ambiguous.

## P1-D42 — Selector validation

Rules:

```text
BRANCH:
nonblank Git ref name
must not include refs/heads/ prefix

TAG:
nonblank Git ref name
must not include refs/tags/ prefix

COMMIT_SHA:
canonical lowercase full SHA only
no abbreviated SHA
```

Provider-specific URL escaping occurs only inside the GitHub client.

Slice 1.2 does not accept free-form ambiguous "whatever GitHub resolves" text.

## P1-D43 — Resolve once, then pin

A branch or tag is resolved exactly once to a canonical immutable commit SHA.

After resolution:

```text
selector name
MUST NOT be used for later tree/blob reads
```

All subsequent reads use the canonical full commit SHA or object SHAs descended from that commit.

This prevents ref movement during the operation from changing the verified snapshot.

## P1-D44 — Commit selector exactness

For `COMMIT_SHA`, GitHub must return the exact requested full SHA.

If the provider returns another commit identity, resolution fails.

No implicit prefix expansion or abbreviation is allowed.

## P1-D45 — Canonical CommitRef

Successful resolution constructs exactly:

```python
CommitRef(
    repository=project.primary_repository,
    sha=<provider-returned canonical commit SHA>,
)
```

No provider URL, branch, tag, installation ID, or token enters `CommitRef`.

## P1-D46 — Commit object proof

After canonical SHA resolution, Relay reads the Git commit object by that exact SHA and requires:

```text
response commit SHA == CommitRef.sha
```

The commit object's root tree SHA becomes the only starting point for snapshot enumeration.

## P1-D47 — Tree enumeration is commit-pinned

Relay enumerates the repository from the root tree SHA.

Recursive tree output is accepted only when:

```text
truncated == false
```

If GitHub reports truncation, implementation must either:

1. deterministically traverse subtrees non-recursively until the required complete tree is known; or
2. fail closed with a typed incomplete-snapshot error.

It MUST NOT validate a partial recursive tree as complete.

The preferred implementation is deterministic subtree fallback rather than an artificial repository-size ceiling.

## P1-D48 — Tree-entry validation

For the paths used by repository-contract validation:

```text
ordinary file:
type == blob
mode in {100644, 100755}

symlink:
mode == 120000 → reject for a registered artifact

submodule:
mode == 160000 / type commit → reject for a registered artifact
```

Tree paths must be unique canonical repository-relative POSIX paths.

## P1-D49 — `.relay/` direct-entry proof

At the resolved commit, the complete Git tree must prove that the only direct schema-v1 `.relay/` entry is:

```text
.relay/registry.json
```

Unexpected direct `.relay/` entries fail repository-contract validation.

This reproduces the accepted Slice 0.6 rule against the actual commit tree rather than an asserted filesystem snapshot.

## P1-D50 — Exact registry blob

Relay identifies `.relay/registry.json` through the commit tree, fetches that exact blob by blob SHA, decodes exact bytes, and parses the accepted schema-v1 registry.

The registry's:

```text
project_id
repository
```

must equal the loaded Project and `Project.primary_repository` exactly.

## P1-D51 — Registered artifact tree proof

Every registry artifact path must correspond to one regular Git blob entry in the resolved commit tree.

Missing path, tree, symlink, submodule, or unsupported entry type fails validation.

## P1-D52 — Exact artifact bytes

For every registered artifact entry, Relay fetches the exact Git blob named by the resolved commit tree.

Required validation:

```text
blob response SHA == tree entry blob SHA
SHA-256(raw blob bytes) == registry.content_digest
```

No download URL, branch name, or mutable ref is accepted as artifact-byte provenance.

## P1-D53 — GitHub blob-size boundary

The GitHub Git-blob API currently supports blobs up to 100 MB.

If a registered artifact cannot be retrieved completely through the accepted read API, Slice 1.2 fails closed with an explicit unsupported/incomplete snapshot error.

It must never hash truncated provider content.

A later clone/local-worktree path may lift this provider boundary if needed.

## P1-D54 — Provider snapshot evidence

The provider-specific resolver returns an immutable verified result equivalent to:

```python
VerifiedRepositorySnapshot(
    project_id,
    repository: RepositoryRef,
    commit: CommitRef,
    tree_sha,
    registry: RepositoryRegistry,
    blobs: tuple[VerifiedRepositoryBlob, ...],
)
```

This is integration/service evidence, not a new core domain authority model.

It may be provider-specific internally.

## P1-D55 — Snapshot proof closes Slice 0.6 caller assertion

For the GitHub path, Slice 1.2 removes the Slice 0.6 assumption that callers supplied filesystem bytes matching a claimed commit.

The resolved commit itself selects the tree and blobs being validated.

This closes:

```text
remote repository snapshot ↔ CommitRef
```

proof for GitHub.

It does not yet claim anything about a future agent's local uncommitted worktree cleanliness.

Local execution-worktree state remains out of scope until execution/workspace behavior exists.

## P1-D56 — Repository-contract validation reuse

Implementation MUST reuse the accepted repository-contract models/invariants.

It may add a narrow pure byte/tree validation entry point to `relay_engine.repository_contract` so filesystem and GitHub snapshot adapters share one semantic validator.

It MUST NOT copy the registry/canonical/path/digest rules into a separate GitHub-only implementation.

Existing public Slice 0.6 behavior must remain backward compatible.

## P1-D57 — No remote `.relay/` mutation

A missing or invalid `.relay/registry.json` causes a typed failure.

Slice 1.2 does not offer to create or repair it.

Remote initialization/synchronization belongs to Slice 1.3.

## P1-D58 — Stable core Artifact binding

A verified repository artifact revision may be materialized as the accepted core:

```python
Artifact(
    id=registry.artifact_id,
    artifact_type=registry.artifact_type,
    path=registry.path,
    commit=<verified baseline CommitRef>,
    content_digest=registry.content_digest,
)
```

only through the Slice 1.2 verified-baseline persistence path.

## P1-D59 — First binding wins for Artifact.commit

Because Slice 0.2 `Artifact` is immutable and Slice 0.5 identity is insert-once:

- if a registry `ArtifactId` has never been persisted as a core `Artifact`, Slice 1.2 binds it once to the current verified `CommitRef`;
- if it already exists, Relay does not create or update it;
- the existing Artifact's repository, path, artifact type, and content digest must agree with the currently verified registry revision;
- its previously bound `commit` may be an earlier commit where identical bytes/revision were first materialized.

This gives each stable ArtifactId one stable core payload and preserves F007.

## P1-D60 — Existing Artifact repository consistency

An existing core Artifact referenced by the current verified registry must have:

```text
artifact.commit.repository == Project.primary_repository
```

Cross-repository reuse of the same `ArtifactId` is an integrity error.

## P1-D61 — Baseline artifact set

A Slice 1.2 baseline references the complete ordered set of current registered artifact IDs from the verified repository registry.

The persisted tuple uses deterministic registry order.

The baseline therefore points to the repository authority that was verified at its commit.

## P1-D62 — Baseline decisions are explicit inputs

`decision_ids` are explicit caller inputs.

Slice 1.2 does not invent decisions from commit messages, GitHub metadata, or documentation.

Before baseline persistence, every referenced decision ID must already exist durably.

An empty decision set is valid.

## P1-D63 — Explicit BaselineId

`BaselineId` remains explicit caller input.

No model validator, provider response, commit SHA, timestamp, or hidden random generator silently creates the ID.

## P1-D64 — Atomic verified-baseline persistence

Slice 1.2 adds one bounded atomic persistence operation equivalent to:

```text
persist_verified_baseline(...)
```

Within one SQLite write transaction it:

1. verifies the Project exists and exact repository identity matches;
2. verifies/creates missing core Artifacts under D58–D60;
3. verifies all requested Decision IDs exist;
4. inserts the immutable Baseline exactly once.

If any check/insert fails, no new Artifact or Baseline row remains.

## P1-D65 — No migration v3 required

Slice 1.2 reuses existing:

```text
projects
artifacts
decisions
baselines
```

tables.

No new repository-registration table exists.

No migration v3 is justified by the current contract.

If implementation discovers a required new durable state that cannot be represented without a migration, that is a design escalation.

## P1-D66 — Baseline insert-once semantics remain

Baseline identity remains Slice 0.5 insert-once by `BaselineId`.

A repeated BaselineId is rejected even if payload bytes are equal.

Slice 1.2 introduces no same-ID update semantics.

## P1-D67 — Same commit may have multiple baselines

The design does not add a unique constraint on:

```text
(project_id, commit SHA)
```

Different Baseline IDs may legitimately reference the same commit with different explicit authority/decision sets.

No deduplication policy is invented in Slice 1.2.

## P1-D68 — Ref selector is not persisted into Baseline

Branch/tag selector text is not baseline identity.

The authoritative baseline stores the immutable `CommitRef`.

If later product UX needs to retain "selected from branch main" as user intent/audit context, it should be represented through accepted decision/evidence workflow rather than mutating `Baseline`.

## P1-D69 — GitHub client extension stays read-only

The existing Slice 1.1 GitHub client may add only the reads required for:

```text
commit ref resolution
commit object
Git tree
Git blob
```

No write method or broader permission is authorized.

## P1-D70 — Installation token scope

Snapshot resolution uses a short-lived installation token restricted to the selected repository when the provider supports that restriction.

No token cache is introduced.

Secrets remain ephemeral.

## P1-D71 — Selected repository must still be usable

Before ref resolution, the service verifies the selected repository through the Slice 1.1 `ACTIVE / READY` access path.

If access became stale/revoked, baseline resolution fails before remote snapshot authority is persisted.

A successful baseline does not make future provider access READY.

## P1-D72 — GitHub repository identity is checked twice

The selected GitHub repository must map to the exact `Project.primary_repository` before network snapshot resolution.

The fetched registry must independently contain that same full `RepositoryRef`.

These are separate checks:

```text
provider-selected repo → Project
registry repo → Project
```

Either mismatch fails.

## P1-D73 — Remote error classification

Slice 1.2 distinguishes at least:

```text
repository/project mismatch
invalid selector
ref not found
commit unavailable
repository access unavailable
rate limited
provider protocol failure
tree incomplete
blob unavailable/too large
registry contract invalid
snapshot integrity failure
baseline persistence integrity failure
concurrency/database failure
```

Authentication/rate-limit errors must not be misclassified as missing refs.

## P1-D74 — No hidden retry

Ref resolution and snapshot verification perform one explicit operation.

No hidden retry loop may silently resolve a moved branch twice and choose a later commit.

A caller may explicitly retry the whole command.

## P1-D75 — Deterministic operation result

The high-level command returns an immutable result equivalent to:

```python
ResolvedBaselineResult(
    project_id,
    repository,
    selector,
    commit,
    baseline_id,
    artifact_ids,
)
```

The result exposes the immutable commit actually persisted.

## P1-D76 — No local Git dependency

Slice 1.2 does not require the `git` executable, clone/fetch, libgit2, Dulwich, or another Git implementation.

For the current GitHub-controlled workflow, commit/tree/blob proof comes from the authenticated GitHub Git database API.

A future local workspace verifier may be introduced only when execution/worktree behavior exists.

## P1-D77 — No new third-party dependency

The design requires no new runtime dependency.

Existing stdlib HTTP + PyJWT/cryptography integration is sufficient.

## P1-D78 — Architecture boundary

Expected implementation surface is bounded to:

```text
src/relay_engine/integrations/github/
    narrow read extensions

src/relay_engine/repository_baseline/
    provider-neutral selector/service/result/error semantics

src/relay_engine/repository_contract/
    narrow shared snapshot-byte validation extension if required

src/relay_engine/persistence/
    atomic verified-baseline insert operation

tests/
docs/
```

No UI, worker, queue, agent, provider framework, or generic VCS abstraction.

## P1-D79 — Repository-baseline package is small

The provider-neutral `repository_baseline` package exists only to own:

- strict ref-selector values;
- orchestration between Project, selected RepositoryRef, verified provider snapshot, core Artifact, and Baseline;
- provider-neutral operation errors/results.

It is not a multi-provider plugin framework.

## P1-D80 — Human authority boundary

Passing Slice 1.2 tests or independent design review does not authorize implementation or acceptance.

Implementation requires separate Human Authority authorization.

Slice 1.3 remains closed.

---

# 5. Required high-level operation

Conceptually:

```python
resolve_and_persist_baseline(
    *,
    project_id: ProjectId,
    selected_repository: RepositoryRef,
    selector: RepositoryRevisionSelector,
    baseline_id: BaselineId,
    decision_ids: tuple[DecisionId, ...],
    observed_at: datetime,
) -> ResolvedBaselineResult
```

Required flow:

```text
load Project
    ↓
Project.primary_repository == selected_repository
    ↓
Slice 1.1 selected repo is ACTIVE / READY
    ↓
mint repo-scoped installation token
    ↓
resolve selector once → canonical full commit SHA
    ↓
read exact commit object → root tree SHA
    ↓
enumerate complete tree pinned to tree SHA
    ↓
read exact registry blob
    ↓
validate project/repository registry identity
    ↓
read every registered artifact blob from that tree
    ↓
validate modes/paths/SHA-256/registry semantics
    ↓
construct verified CommitRef + artifact candidates
    ↓
single SQLite transaction:
    verify Project
    bind missing Artifacts once
    verify existing Artifacts
    verify Decisions
    insert Baseline
    ↓
return immutable persisted result
```

No repository write occurs.

---

# 6. Snapshot validator contract

A shared pure validation seam should accept data equivalent to:

```python
RepositorySnapshotEntry(
    path: str,
    mode: str,
    object_type: str,
    object_sha: str,
    raw_bytes: bytes | None,
)
```

and return a validated registry/snapshot representation.

Provider adapters are responsible for obtaining complete entries/bytes.

The pure validator remains responsible for accepted repository-contract semantics.

Provider transport errors do not leak into repository-contract errors until there is actual semantic/integrity content to classify.

---

# 7. Artifact-binding examples

## First observed baseline

Registry:

```text
ArtifactId A
path docs/foo.md
digest D
```

Verified at commit C1.

No core Artifact A exists.

Persist:

```text
Artifact A.commit = C1
Baseline B1.commit = C1
Baseline B1.artifact_ids includes A
```

## Same unchanged artifact at later baseline

Same registry ArtifactId A, same path/type/digest, verified at commit C2.

Core Artifact A already exists bound to C1.

Do NOT rewrite it to C2.

Persist:

```text
Baseline B2.commit = C2
Baseline B2.artifact_ids includes A
```

The baseline proves A's bytes are present at C2; Artifact A retains stable first-binding provenance C1.

## Changed living projection

Changed bytes require new registry ArtifactId A2.

Verified at C3.

Persist A2 once with `commit=C3`.

This preserves the accepted living-projection and F007 rules.

---

# 8. Failure and race semantics

## Moving branch after resolution

```text
main → C1
Relay resolves main → C1
main moves → C2
Relay continues using C1/tree(C1)/blobs(C1)
```

Result remains C1.

## Provider access revoked mid-operation

Any subsequent provider request fails.

No baseline/artifact persistence occurs until the complete remote snapshot is verified.

## Database failure after remote proof

Atomic persistence rolls back all new Artifact/Baseline inserts.

Caller may explicitly retry using the same or a new selector.

## Existing Artifact conflicts

If existing ArtifactId disagrees with registry path/type/digest/repository:

```text
integrity failure
no baseline inserted
```

No repair or overwrite occurs.

## Registry invalid at selected commit

Resolution fails.

Slice 1.2 does not initialize or repair remote `.relay/`.

---

# 9. Acceptance criteria

## Identity and scope

A01 Project.primary_repository is the sole project repository authority.
A02 no second repository-registration table/model is added.
A03 existing Project values are never updated.
A04 missing Project fails resolution.
A05 selected RepositoryRef must exactly equal Project.primary_repository.
A06 Slice 1.1 ACTIVE/READY access is required.
A07 registry RepositoryRef must exactly equal Project.primary_repository.
A08 GitHub numeric repository ID never becomes Relay RepositoryId implicitly.
A09 Slice 1.3 remains unauthorized.
A10 GitHub write permissions remain absent.

## Selector and commit resolution

A11 selector kind is explicit BRANCH/TAG/COMMIT_SHA.
A12 branch/tag names are nonblank and unprefixed.
A13 commit selector is full canonical SHA only.
A14 abbreviated SHAs are rejected.
A15 branch and tag with same text remain unambiguous by kind.
A16 selector resolves once.
A17 later reads never reuse the moving ref name.
A18 returned commit SHA is canonical.
A19 COMMIT_SHA result must equal requested SHA.
A20 CommitRef repository is exact Project.primary_repository.

## Snapshot proof

A21 exact commit object is read by canonical SHA.
A22 returned commit-object SHA must match CommitRef.
A23 root tree SHA comes from that exact commit object.
A24 tree enumeration is commit/tree-SHA pinned.
A25 truncated recursive tree cannot be accepted as complete.
A26 subtree fallback, if implemented, is deterministic.
A27 tree paths are unique.
A28 registered files require blob type.
A29 registered symlink mode is rejected.
A30 registered submodule mode/type is rejected.
A31 `.relay/registry.json` is present as regular blob.
A32 unknown direct `.relay/` entries are rejected.
A33 registry bytes come from the exact tree-selected blob.
A34 registry duplicate-key/schema rules remain enforced.
A35 registry ProjectId equals target project.
A36 registry RepositoryRef equals Project.primary_repository.
A37 every registered artifact path exists in exact tree.
A38 every registered artifact is regular blob.
A39 blob response SHA equals tree entry SHA.
A40 SHA-256 raw bytes equal registry digest.
A41 truncated blob bytes are never hashed as complete.
A42 provider blob-size limit fails closed.
A43 successful result proves snapshot↔CommitRef correspondence.
A44 no local-worktree-cleanliness claim is fabricated.

## Repository-contract reuse

A45 Slice 0.6 canonical rules remain unchanged.
A46 historical/supersession rules remain unchanged.
A47 living projection identity rules remain unchanged.
A48 path safety semantics remain unchanged.
A49 existing filesystem validation API remains compatible.
A50 shared pure validation avoids duplicated GitHub-only repository rules.

## Artifact binding / F007

A51 missing core Artifact may be materialized only after verified snapshot.
A52 new Artifact uses exact registry ArtifactId.
A53 new Artifact path/type/digest match registry.
A54 new Artifact commit is verified baseline CommitRef.
A55 existing Artifact is never updated.
A56 existing Artifact path/type/digest must match registry.
A57 existing Artifact repository must match project repository.
A58 existing Artifact commit may be earlier first-binding commit.
A59 same ArtifactId never produces unequal persisted payload.
A60 changed living bytes/new ArtifactId can bind at later commit.
A61 all current registry artifact IDs enter baseline artifact_ids.
A62 artifact ID ordering is deterministic.

## Baseline persistence

A63 BaselineId is explicit input.
A64 Baseline commit is canonical resolved CommitRef.
A65 Baseline project_id is exact target ProjectId.
A66 decision_ids are explicit input.
A67 referenced decisions must exist.
A68 empty decision_ids is valid.
A69 verified-baseline persistence is one SQLite transaction.
A70 new Artifacts and Baseline roll back together on failure.
A71 duplicate BaselineId is rejected.
A72 same project/commit may have multiple BaselineIds.
A73 no migration v3 is added absent escalation.
A74 restart loads identical Baseline/Artifact values.
A75 persisted indexed columns and typed payloads remain consistent.

## GitHub/provider boundary

A76 existing Contents:read permission ceiling is sufficient.
A77 no GitHub write endpoint is added.
A78 installation token remains ephemeral.
A79 token is repo-scoped when supported.
A80 no token cache is added.
A81 authentication errors remain distinct from missing refs.
A82 rate limits remain distinct from missing refs.
A83 missing ref is typed separately.
A84 commit object mismatch fails.
A85 tree incomplete fails.
A86 blob unavailable/oversized fails.
A87 provider malformed JSON fails strict validation.

## Determinism / races

A88 moving branch after resolution cannot change operation commit.
A89 provider revocation before persistence leaves no baseline.
A90 remote partial snapshot leaves no baseline.
A91 DB failure leaves no partial artifact binding.
A92 no hidden retry changes selected commit.
A93 explicit retry is caller-controlled.
A94 operation result reports exact persisted commit.
A95 no timestamps/randomness hidden in model validation.
A96 no ref selector text is silently treated as immutable authority.

## Scope / quality

A97 no remote `.relay/` mutation.
A98 no branch/commit/PR creation.
A99 no agent execution.
A100 no generic provider/plugin framework.
A101 no local Git dependency.
A102 no new runtime dependency.
A103 core Project/RepositoryRef/CommitRef/Baseline semantics remain provider-neutral.
A104 full existing quality suite remains green.
A105 Slice 1.2 design/memory/ADR are produced when implementation is authorized.
A106 exact implementation evidence names design/result SHAs.
A107 registered living-projection changes include registry advancement.
A108 model assignment/execution deviation is explicit in substantive handovers.
A109 implementation is still separately authorized by Human Authority.
A110 Slice 1.3 remains separately unauthorized.

---

# 10. Required regression scenarios

At implementation time include deterministic coverage equivalent to:

```text
test_project_repository_is_registration_authority
test_selected_repository_mismatch_is_rejected
test_missing_project_is_rejected
test_branch_selector_resolves_once_then_pins_commit
test_tag_selector_resolves_once_then_pins_commit
test_full_sha_requires_exact_provider_identity
test_abbreviated_sha_is_rejected
test_tree_truncation_cannot_validate_partial_snapshot
test_registered_symlink_is_rejected
test_registered_submodule_is_rejected
test_unknown_direct_relay_entry_is_rejected
test_registry_identity_must_match_project
test_blob_sha_must_match_tree_entry
test_registered_digest_must_match_raw_blob_bytes
test_provider_blob_too_large_fails_closed
test_first_verified_snapshot_binds_core_artifact_once
test_later_unchanged_snapshot_reuses_existing_artifact_binding
test_existing_artifact_conflict_blocks_baseline
test_verified_baseline_persistence_is_atomic
test_missing_decision_blocks_baseline_atomically
test_duplicate_baseline_id_is_rejected
test_same_commit_can_have_distinct_baseline_ids
test_restart_recovers_verified_baseline
test_access_revocation_leaves_no_baseline
test_rate_limit_is_not_ref_not_found
test_remote_404_ref_is_not_authentication_failure
test_slice_0_6_filesystem_contract_still_passes
test_no_github_write_request_exists
```

---

# 11. Minimum Sufficient Architecture check

Required additions are limited to:

```text
one strict selector/result/error package
narrow GitHub read methods
one shared repository-snapshot validation seam
one atomic verified-baseline persistence operation
tests/docs
```

Explicitly rejected for Slice 1.2:

```text
RepositoryRegistration table
mutable Project repository binding
generic VCS interface hierarchy
generic provider plugin system
Git clone/worktree manager
background synchronization worker
repository cache
ref watch/polling
write-capable GitHub API
new ORM
new migration absent evidence
UI
agent runtime
```

These are plausible future mechanisms but not necessary for the present contract.

---

# 12. Design review challenge areas

Independent review should challenge especially:

1. whether `Project.primary_repository` truly eliminates need for a registration table;
2. whether GitHub commit/tree/blob reads prove the exact remote snapshot strongly enough;
3. tree truncation/fallback semantics;
4. symlink/submodule and `.relay/` direct-entry proof;
5. stable first-binding core Artifact semantics and F007;
6. whether all registry ArtifactIds should enter Baseline.artifact_ids;
7. atomic Artifact + Baseline persistence without migration v3;
8. selector ambiguity and moving-ref races;
9. distinction between remote snapshot proof and future local worktree cleanliness;
10. whether any hidden Slice 1.3/write behavior leaked into the design;
11. Minimum Sufficient Architecture.

---

# 13. Authority state

```text
Phase 1:
OPEN

Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
DESIGN AUTHORIZED

Slice 1.2 Design Revision 1:
COMPLETE / PENDING INDEPENDENT DESIGN REVIEW

Slice 1.2 implementation:
NOT AUTHORIZED

Slice 1.3:
NOT OPEN / NOT AUTHORIZED
```

STOP after independent design review. A passing review does not authorize implementation.
