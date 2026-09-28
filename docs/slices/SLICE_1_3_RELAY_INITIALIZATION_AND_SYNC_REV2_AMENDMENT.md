# Slice 1.3 — `.relay/` Initialization and Sync — Revision 2 Amendment

**Status:** REVIEW  
**Design revision:** Revision 2 Amendment  
**Design authority:** `RLY-S13-DESIGN-AUTH-001`  
**Parent design:** `docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC.md`  
**Parent design head:** `433910d0b2df7f0f0a3104cbe97f6df5ebba609a`  
**Review handover:** `RLY-S13-DESIGN-EVAL-001 — REVISE`  
**Role:** Architect / Contract Designer  
**Preferred model:** GPT-5.6 Sol  
**Executing model:** GPT-5.6 Sol  
**Implementation:** NOT AUTHORIZED  
**Date:** 2026-09-28

---

# 1. Amendment purpose

This bounded amendment resolves the six findings from the independent Revision 1 design review without changing the accepted architecture direction.

Revision 1 remains the base design. This amendment is authoritative wherever it explicitly adds to or replaces Revision 1 semantics.

Findings resolved:

```text
F001 BLOCKING — bind remote mutation to explicit Human Authority
F002 BLOCKING — prevent overwrite of pre-existing unregistered files
F003 MAJOR    — define indeterminate ref-update reconciliation
F004 MAJOR    — define empty/no-head repository behavior
F005 MAJOR    — reconcile workflow-file paths with the permission ceiling
F006 MINOR    — remove CURRENT / ALREADY_CURRENT inconsistency
```

Preserved architecture:

```text
schema-v1 .relay/registry.json
GitHub Git Data API
one target tree
one target commit
one non-force default-branch ref movement
exact provider/local authority bracketing
exact post-write snapshot verification
no automatic Baseline persistence
no migration
no new runtime dependency
no branch creation
no pull request
no force push
no agent execution
```

---

# 2. F001 — exact Human Authority binding

## S13-D23 — Write authority is bound to an exact synchronization subject

A remote write requires one durable `AuthorizationGrant` issued by Human Authority for the exact synchronization subject.

`AuthorizationGrant` is extended compatibly with one optional field:

```text
subject_digest: ContentDigest | None = None
```

Existing grants with no `subject_digest` remain valid for their existing governance uses.

Slice 1.3 remote mutation requires `subject_digest` to be non-null and equal the exact synchronization subject digest defined below.

This reuses Relay's existing Human Authority and authorization persistence. It does not introduce a second authorization subsystem or a new database table.

## S13-D24 — The request carries an exact expected write base

Revision 1 `RepositorySyncRequest` is amended to:

```text
RepositorySyncRequest
  selection: GitHubRepositoryAccessSelection
  expected_default_branch: str
  expected_base_commit: CommitRef
  target_registry: RepositoryRegistry
  artifact_writes: tuple[RepositoryArtifactWrite, ...]
  authorization_id: AuthorizationId | None
```

Invariants:

- `expected_base_commit.repository == selection.repository`;
- `expected_base_commit.sha` is a full canonical SHA;
- `expected_default_branch` is nonblank;
- a no-op `CURRENT` result may omit `authorization_id`;
- any operation that would create Git objects requires `authorization_id`.

The provider-reported default branch must equal `expected_default_branch`.

For a non-no-op write, the provider default-branch head must equal `expected_base_commit`.

The caller still cannot choose an arbitrary write ref: Relay writes only the provider-reported default branch, and the caller's expected branch must match it exactly.

## S13-D25 — Synchronization subject digest is deterministic and exact

Relay deterministically computes:

```text
RepositorySyncSubjectV1
  schema_version = 1
  project_id
  RepositoryRef
  installation_id
  github_repository_id
  github_node_id
  expected_state_revision
  expected_default_branch
  expected_base_commit
  target_registry_digest
  artifact_write_digests
```

Where:

```text
target_registry_digest =
sha256(serialize_repository_registry(target_registry))

artifact_write_digests =
tuple sorted by path of:
  path
  sha256(raw_bytes)
```

The canonical JSON serialization uses sorted keys, compact separators, UTF-8, and no insignificant whitespace.

The resulting authorization subject is:

```text
sha256(canonical RepositorySyncSubjectV1 bytes)
```

The authorization ID itself is not part of the subject digest.

The target-registry digest transitively binds the complete target registry, including ArtifactIds, paths, revisions, content digests, states, supersession links, and canonical pointers.

## S13-D26 — Authorization is checked twice

Before minting a write token or creating any remote Git object, Relay loads the durable `AuthorizationGrant` and the latest revision of its referenced `HandoverGate`.

The write is eligible only when:

```text
grant exists
grant.actor is HUMAN
gate exists
gate is the latest revision for grant.gate_id
grant.slice_id == gate.slice_id
grant.baseline_id == gate.baseline_id
grant.gate_revision == gate.revision
gate.authorization_required == true
grant.subject_digest == computed sync subject digest
```

Immediately before ref visibility, Relay repeats the authorization-grant and latest-gate checks together with the Revision 1 local/provider access checks.

Any mismatch is `RepositorySyncAuthorizationRequired` or `RepositorySyncAuthorizationStale` and prevents the ref update.

No free-form `reason` text is parsed as authority.

## S13-D27 — No-op recognition does not require write authority

Relay may inspect and recognize an exact already-current target without a write authorization.

When the exact current snapshot already equals the target:

```text
state = CURRENT
wrote_remote = false
```

No write token is minted and no remote Git object is created.

---

# 3. F002 — unregistered-path preservation

## S13-D28 — Existing unregistered files cannot be overwritten

For every path represented in the target registry but not represented in the current registry, Relay inspects the exact base-tree path before target construction.

If the path is absent, it may be created subject to the normal target-registry checks.

If the path already exists as an unregistered base-tree object, Relay may adopt it only when:

```text
object is an accepted regular-file mode
existing exact bytes hash to target content_digest
no content or mode mutation is required
```

In that case the existing blob/mode is reused and the target registry may begin governing the file.

If an existing unregistered path has different bytes, unsupported mode/type, or would otherwise need mutation, the operation is `CONFLICT`.

Caller-supplied bytes do not authorize overwrite of an existing unregistered file.

## S13-D29 — Adoption is not a file write

If an unregistered existing regular file already has the exact target bytes and accepted mode:

- Relay may register/adopt it;
- Relay does not create a replacement blob for that path;
- the only visible change for that path is the repository-contract metadata in the new registry/commit.

This preserves Revision 1 A42.

---

# 4. F003 — indeterminate ref-update reconciliation

## S13-D30 — Ref-update outcomes distinguish definitive rejection from indeterminate transport failure

A provider response that definitively rejects the non-force update is handled by the existing typed conflict/protected/permission failure semantics.

A transport failure for which Relay cannot know whether GitHub applied the ref update is an indeterminate ref-update outcome.

Relay MUST NOT retry the write call.

## S13-D31 — Indeterminate update is reconciled by observation

After an indeterminate ref-update outcome, Relay uses read-side access to resolve the exact target default-branch ref.

Three outcomes are normative:

```text
observed head == created commit SHA
    → treat visibility as having occurred
    → continue the normal post-write identity/authority/snapshot checks

observed head == expected base commit SHA
    → visibility did not occur
    → return a typed non-visible ref-update failure carrying created commit SHA

observed head == any other SHA
or the ref cannot be established
    → RepositorySyncPostWriteVerificationError
    → carry exact created commit SHA
    → human/operator reconciliation required
```

No hidden second ref update, rebase, merge, reverse commit, or force push is permitted.

---

# 5. F004 — empty/no-head repositories

## S13-D32 — Slice 1.3 requires an existing default-branch head

Slice 1.3 does not bootstrap an empty GitHub repository.

If the provider repository has no resolvable existing default-branch ref/head:

```text
RepositorySyncNoDefaultHead
```

is returned before a write token is minted.

No branch is created and no initial ref is synthesized.

A repository with an existing default-branch head but no `.relay` entry remains `UNINITIALIZED` and may follow the normal initialization path.

This preserves the bounded default-branch-only architecture.

---

# 6. F005 — workflow-file permission ceiling

## S13-D33 — Workflow content is outside the Slice 1.3 write set

The exact Slice 1.3 permission ceiling remains:

```text
contents: write
metadata: read
```

Slice 1.3 does not add GitHub workflow permission.

Therefore Relay MUST NOT create, replace, or change file mode/content for any path under:

```text
.github/workflows/
```

A requested content mutation at such a path fails before write-token minting with:

```text
RepositorySyncWorkflowMutationUnsupported
```

## S13-D34 — Unchanged workflow files may remain or be adopted

A workflow file may:

- remain registered and unchanged;
- remain unregistered and untouched;
- become newly registered only by exact-byte adoption under S13-D28/S13-D29.

No workflow content mutation is performed.

This keeps repository snapshot verification complete without expanding GitHub App permissions.

---

# 7. F006 — one successful state vocabulary

## S13-D35 — `CURRENT` is the sole successful contract state

`ALREADY_CURRENT` is removed from the normative Slice 1.3 vocabulary.

All successful results use:

```text
RepositorySyncResult
  state: CURRENT
  prior_commit: CommitRef
  resulting_commit: CommitRef
  wrote_remote: bool
```

No-op/current recognition:

```text
state = CURRENT
prior_commit == resulting_commit
wrote_remote = false
```

Successful mutation:

```text
state = CURRENT
prior_commit != resulting_commit
wrote_remote = true
```

Revision 1 D19, algorithm step 9, and A66 are amended accordingly wherever they used `ALREADY_CURRENT`.

---

# 8. Revised normative synchronization order

Revision 1 Section 8 is amended to the following order:

```text
1.  Validate request structure, target-registry identity, expected branch, and expected base CommitRef.
2.  Load Project and require Project.primary_repository == selection.repository.
3.  Recheck captured local Slice 1.1 access selection.
4.  Mint repository-scoped READ token.
5.  Read provider repository identity; require ID/node/full_name match and non-archived.
6.  Require provider default_branch == expected_default_branch.
7.  Resolve the exact default-branch head.
8.  If no default-branch head exists, return RepositorySyncNoDefaultHead.
9.  Capture exact commit/root tree and inspect/classify `.relay` at that head.
10. If the exact current snapshot already equals the target, return CURRENT with wrote_remote=false.
11. For any non-no-op path, require current head == expected_base_commit.
12. For initialized state, validate current → target registry transition.
13. Validate unregistered-path adoption/conflict rules and workflow-path restrictions.
14. Construct and validate the complete logical target snapshot.
15. Compute the exact RepositorySyncSubjectV1 digest.
16. Load and validate the durable Human Authority AuthorizationGrant and latest gate revision.
17. Require stored WRITE PROFILE.
18. Mint repository-scoped WRITE token.
19. Create only permitted changed artifact blobs and target registry blob.
20. Create one target tree from the exact base tree.
21. Create one commit whose single parent is expected_base_commit.
22. Recheck Human Authority grant/latest gate, local access authority, state_revision, membership, and WRITE PROFILE.
23. Re-read provider identity/default branch/non-archived state.
24. Re-resolve default-branch head; require expected_base_commit.
25. Call one non-force default-branch ref update.
26. On a definitive success, continue.
27. On a definitive rejection, return its typed failure.
28. On an indeterminate transport outcome, reconcile by read observation under S13-D31; never retry the write.
29. Require visible branch head == created commit SHA before success.
30. Re-read provider identity/default branch/non-archived state.
31. Recheck local access authority for observability.
32. Read and validate exact resulting commit/tree/registry/artifact bytes.
33. Return exact prior/resulting CommitRefs with state=CURRENT.
```

Steps 19–21 may leave unreachable Git objects if a later pre-visibility guard fails. They do not become repository authority.

---

# 9. API amendments

## 9.1 Authorization grant

Compatible addition:

```text
AuthorizationGrant
  ...
  subject_digest: ContentDigest | None = None
```

No SQLite schema migration is required because authorization grants are already persisted as typed JSON payloads and the new field is optional for pre-Slice-1.3 records.

## 9.2 Sync request

Normative request after Revision 2:

```text
RepositorySyncRequest
  selection: GitHubRepositoryAccessSelection
  expected_default_branch: str
  expected_base_commit: CommitRef
  target_registry: RepositoryRegistry
  artifact_writes: tuple[RepositoryArtifactWrite, ...]
  authorization_id: AuthorizationId | None
```

## 9.3 Additional typed errors

Revision 2 adds:

```text
RepositorySyncAuthorizationRequired
RepositorySyncAuthorizationStale
RepositorySyncNoDefaultHead
RepositorySyncWorkflowMutationUnsupported
RepositorySyncRefUpdateNotVisible
```

`RepositorySyncPostWriteVerificationError` remains the ambiguous/visible-mutation reconciliation error and MUST carry the exact created commit SHA.

---

# 10. Acceptance-criteria amendment

Revision 1 A01–A80 remain in force except where explicitly amended below.

Replacement:

- **A66-R2** — If the target state is already exact, a retry returns `state=CURRENT`, identical prior/resulting commits, and `wrote_remote=false`; no additional commit is created.

Additional criteria:

- **A81** — A non-no-op request supplies exact `expected_default_branch` and full `expected_base_commit`.
- **A82** — Provider default branch must equal `expected_default_branch`.
- **A83** — Any non-no-op write requires current head to equal `expected_base_commit`.
- **A84** — Synchronization subject digest is deterministic and binds repository/provider selection, state revision, expected branch/base, target registry digest, and ordered artifact-write digests.
- **A85** — A remote write requires a durable Human Authority `AuthorizationGrant` whose non-null `subject_digest` equals A84.
- **A86** — Authorization grant and latest referenced gate revision are checked before write-token minting and again immediately before ref visibility.
- **A87** — Existing authorization grants without `subject_digest` remain valid for pre-existing governance uses but cannot authorize Slice 1.3 writes.
- **A88** — An existing unregistered path may be adopted only when exact bytes and accepted regular-file mode already satisfy the target Artifact; otherwise synchronization is `CONFLICT`.
- **A89** — Adoption of an exact existing unregistered file causes no content or mode mutation for that path.
- **A90** — Indeterminate ref-update transport failure is reconciled by ref observation and never by hidden write retry.
- **A91** — Reconciliation distinguishes new SHA, unchanged base SHA, and other/unobservable head exactly as S13-D31 specifies.
- **A92** — A repository with no existing default-branch head returns `RepositorySyncNoDefaultHead` and no branch/ref is created.
- **A93** — Slice 1.3 never creates or changes `.github/workflows/**` content or mode under the contents-only write permission ceiling.
- **A94** — Exact unchanged workflow files may remain registered or be adopted without content mutation.
- **A95** — `CURRENT` is the only successful `RepositoryContractState`; `wrote_remote` distinguishes no-op from mutation.
- **A96** — Revision 2 requires no persistent-schema migration and no new runtime dependency.

---

# 11. Required-test amendment

Implementation evidence must additionally cover:

```text
authorization grant subject digest exact match
authorization missing before write token
authorization stale gate revision before write token
authorization becomes stale before ref update
no-op CURRENT without write authorization
expected default-branch mismatch
expected base-commit mismatch
existing unregistered exact-file adoption
existing unregistered differing-file conflict
existing unregistered non-regular object conflict
workflow file unchanged
workflow file exact adoption
workflow content mutation refusal
repository with no default-branch head
indeterminate ref update then observed new SHA
indeterminate ref update then observed base SHA
indeterminate ref update then observed third-party SHA
indeterminate ref update then unreadable ref
no hidden write retry after indeterminate outcome
CURRENT retry vocabulary and wrote_remote=false
```

Race tests must prove that authorization, provider identity, access state, and head checks occur before ref visibility.

---

# 12. Revised implementation change surface

Revision 1's bounded implementation surface remains substantially correct but is amended for F001.

Expected production surface:

| Dimension | Revision 2 expectation |
|---|---:|
| Existing production files touched | 4–6 |
| Existing governance files touched | 1–2 |
| New production package | `repository_sync` |
| New production files | 3–4 |
| New runtime dependencies | 0 |
| Persistent schema changes | 0 |
| New migrations | 0 |
| New provider integrations | 0 |
| New GitHub permission names | 0 |

The expected governance change is the backward-compatible optional `AuthorizationGrant.subject_digest` plus any minimal export/validation support required to consume it.

Material expansion beyond this surface requires explicit implementation handover disclosure and evaluator scrutiny.

---

# 13. Revision 2 closure

All six `RLY-S13-DESIGN-EVAL-001` findings are addressed by this amendment:

```text
F001 → S13-D23 through S13-D27; A81–A87
F002 → S13-D28 through S13-D29; A88–A89
F003 → S13-D30 through S13-D31; A90–A91
F004 → S13-D32; A92
F005 → S13-D33 through S13-D34; A93–A94
F006 → S13-D35; A66-R2 and A95
```

No Revision 1 architectural decision is otherwise withdrawn.

```text
Slice 1.3 Design Revision 1
        +
Revision 2 Amendment
        ↓
combined design authority for independent review
```

Implementation remains NOT AUTHORIZED.

The next governed action is independent combined design review of Revision 1 + Revision 2.
