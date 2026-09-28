# Slice 1.3 — `.relay/` Initialization and Sync — Revision 3 Amendment

**Status:** REVIEW  
**Design revision:** Revision 3 Amendment  
**Design authority:** `RLY-S13-DESIGN-AUTH-001`  
**Parent design:** `docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC.md`  
**Revision 2:** `docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV2_AMENDMENT.md`  
**Revision 2 head:** `6070b04ca5b38bd5c4687bb0ec4799f4f782e355`  
**Review handover:** `RLY-S13-DESIGN-EVAL-002 — REVISE`  
**Role:** Architect / Contract Designer  
**Preferred model:** GPT-5.6 Sol  
**Executing model:** GPT-5.6 Sol  
**Implementation:** NOT AUTHORIZED  
**Date:** 2026-09-28

---

# 1. Amendment purpose

This bounded amendment resolves only combined-review finding F007.

Revision 1 and Revision 2 remain authoritative except where this amendment explicitly replaces Revision 2 F001 authorization semantics.

Finding addressed:

```text
F007 BLOCKING — Revision 2 reused baseline-bound AuthorizationGrant / HandoverGate
                semantics for repository mutation even though the UNINITIALIZED
                path has no verified repository Baseline and S13-D26 did not run
                the accepted full handover-gate evaluation contract.
```

Preserved without redesign:

```text
schema-v1 .relay/registry.json
RepositorySyncSubjectV1 exact subject digest
GitHub Git Data API
one target tree
one target commit
one non-force default-branch ref movement
expected default branch and expected base commit
provider/local access bracketing
unregistered-path adoption-or-conflict
workflow-path mutation prohibition
no-default-head boundary
indeterminate ref-update reconciliation
CURRENT + wrote_remote result vocabulary
no automatic Baseline persistence
no branch creation
no pull request
no force push
no agent execution
```

Revision 3 deliberately introduces one small local persistence migration because preserving the accepted meanings of `Baseline`, `AuthorizationGrant`, and `HandoverGate` is more important than preserving Revision 2's no-migration simplification.

---

# 2. F007 — dedicated repository-mutation authority

## S13-D36 — Repository mutation authority is not a HandoverGate authorization

Slice 1.3 remote repository mutation uses a dedicated durable authority record:

```text
RepositoryMutationAuthorization
```

It is not an `AuthorizationGrant`, is not a `HumanGateDecision`, and is not a `HandoverGate` evaluation result.

Repository mutation is a provider side effect, not a lifecycle phase transition. Therefore Slice 1.3 MUST NOT claim that a partial subset of handover checks is equivalent to a GREEN handover gate.

Existing `AuthorizationGrant`, `HandoverGate`, `HumanGateDecision`, and `evaluate_handover_gates(...)` semantics remain unchanged.

This amendment does not weaken or bypass them. If a later workflow requires a lifecycle handover before invoking repository synchronization, that handover must independently satisfy the complete accepted governance engine.

## S13-D37 — Exact repository-mutation authorization model

New domain model:

```text
RepositoryMutationAuthorization
  authorization_id: RepositoryMutationAuthorizationId
  project_id: ProjectId
  slice_id: SliceId
  subject_schema_version: 1
  subject: RepositorySyncSubjectV1
  subject_digest: ContentDigest
  actor: ActorRef
  granted_at: datetime
  reason: str
```

Invariants:

- `actor.kind == HUMAN`;
- `reason` is nonblank;
- `granted_at` is timezone-aware UTC;
- `subject_schema_version == 1`;
- `subject.project_id == project_id`;
- `subject_digest == sha256(canonical RepositorySyncSubjectV1 bytes)`;
- the record is immutable once inserted.

The authorization contains no `baseline_id` and no `gate_id`.

That omission is intentional: an `UNINITIALIZED` repository may legitimately have no verified Relay repository Baseline yet.

The authorization remains slice-scoped for auditability but does not mutate Slice lifecycle state.

## S13-D38 — RepositorySyncSubjectV1 remains the exact authority subject

Revision 2 S13-D25 is preserved.

The authorized subject continues to bind:

```text
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

`target_registry_digest` remains the SHA-256 digest of the exact deterministic schema-v1 registry serialization.

`artifact_write_digests` remains the canonical path-sorted sequence of path plus SHA-256 raw-byte digest.

Therefore Human Authority approves one exact repository, provider binding, access revision, branch/base commit, target registry, and artifact-byte set.

## S13-D39 — Read-only preparation precedes Human Authority approval

Slice 1.3 adds a read-only preparation operation:

```text
prepare_repository_sync(request_without_authorization)
    -> RepositorySyncPreparation
```

Preparation performs the non-mutating checks required to establish the exact write subject:

```text
Project.primary_repository check
captured local access selection check
READ-token mint
provider identity / non-archived check
default-branch check
exact current-head resolution
no-default-head check
current .relay classification
current snapshot validation when initialized
expected-base check for non-no-op target
registry transition validation when initialized
unregistered-path adoption/conflict validation
workflow-path restriction validation
complete logical target validation
RepositorySyncSubjectV1 construction
subject_digest construction
```

Preparation creates no Git blob, tree, commit, branch, or ref update and does not mint a WRITE token.

Normative preparation result for a write candidate:

```text
RepositorySyncPreparation
  state: SYNCHRONIZABLE
  prior_commit: CommitRef
  subject: RepositorySyncSubjectV1
  subject_digest: ContentDigest
  changed_paths: tuple[str, ...]
```

If the exact target is already current:

```text
state = CURRENT
subject = None
subject_digest = None
changed_paths = ()
```

No mutation authorization is required for an exact no-op recognition.

Preparation is evidence for Human Authority and is never trusted as a substitute for execution-time rechecks.

## S13-D40 — Human Authority persists the exact prepared subject

A separate local operation records approval:

```text
authorize_repository_sync(
    authorization_id,
    preparation,
    actor,
    granted_at,
    reason,
)
    -> RepositoryMutationAuthorization
```

It is valid only when:

- `preparation.state == SYNCHRONIZABLE`;
- `preparation.subject` and `preparation.subject_digest` are present;
- the actor is HUMAN;
- the digest exactly matches canonical serialization of the supplied subject.

The authorization is persisted before any WRITE token is minted or remote Git object is created.

No free-form reason text is interpreted as authority.

## S13-D41 — Execution recomputes and matches exact authority

`RepositorySyncRequest.authorization_id` is amended to:

```text
RepositoryMutationAuthorizationId | None
```

For every non-no-op execution, Relay recomputes the exact `RepositorySyncSubjectV1` from the supplied target and current captured access selection.

Before WRITE-token minting Relay loads the immutable `RepositoryMutationAuthorization` and requires:

```text
authorization exists
authorization.actor.kind == HUMAN
authorization.project_id == selection.project_id
authorization.slice_id == current Slice 1.3 authority context
authorization.subject_schema_version == 1
authorization.subject == recomputed subject
authorization.subject_digest == recomputed subject digest
```

Immediately before ref visibility Relay loads the authorization again and repeats the exact subject match together with the accepted local/provider/head guards.

Any mismatch fails closed with:

```text
RepositorySyncAuthorizationRequired
RepositorySyncAuthorizationStale
```

No Baseline or HandoverGate is synthesized to satisfy this check.

## S13-D42 — Authorization is exact-subject idempotent, not a remote transaction claim

`RepositoryMutationAuthorization` is immutable approval for one exact subject, not a claim that GitHub and SQLite form one atomic transaction.

Repeated execution with the same authorization is safe because:

- if the target is already exact, execution returns `CURRENT` with `wrote_remote=false` before any write authorization is needed;
- if the branch still equals the exact authorized base, the only permitted visible write is the same exact target commit construction;
- concurrent executions race on one non-force ref update, so at most one can move the branch from the authorized base;
- if the branch no longer equals the authorized base, execution conflicts and the authorization cannot silently retarget another head.

No automatic authorization consumption state is introduced in Slice 1.3 because such local state could not be made atomic with the GitHub ref update and would add a second distributed-transaction problem without improving the exact-subject guarantee.

## S13-D43 — Existing handover governance remains orthogonal

This dedicated mutation authorization answers only:

> Has a Human Authority approved this exact remote repository side effect?

It does not answer:

- whether a lifecycle handover is GREEN;
- whether a Slice may change phase;
- whether implementation work is authorized;
- whether evaluation or acceptance gates have passed;
- whether a resulting repository commit is an accepted Relay Baseline.

Those remain governed by their existing contracts.

---

# 3. Persistence amendment

## S13-D44 — Local migration v3

Revision 2 A96 is replaced.

Slice 1.3 now requires one deterministic SQLite migration v3 adding:

```text
repository_mutation_authorizations
```

Normative minimum table shape:

```text
CREATE TABLE repository_mutation_authorizations (
    authorization_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    slice_id TEXT NOT NULL REFERENCES slices(id),
    subject_digest TEXT NOT NULL,
    payload_json TEXT NOT NULL
)
```

Normative index:

```text
CREATE INDEX repository_mutation_authorizations_by_project_subject
ON repository_mutation_authorizations(project_id, subject_digest)
```

The typed JSON payload is the authority record. Indexed columns MUST agree with the typed payload on load using the accepted persistence-integrity pattern.

Migration requirements remain deterministic and checksummed under the existing migration engine.

No existing table or column is reinterpreted.

This is a local runtime-state migration only. It does not change schema-v1 `.relay/registry.json`.

## S13-D45 — Persistence operations are narrow

Required persistence API:

```text
insert_repository_mutation_authorization(...)
load_repository_mutation_authorization(...)
```

Insert is append-only / immutable-by-ID.

Loading malformed payloads or indexed-column disagreement fails with the existing persistence-integrity contract.

No update/delete API is introduced for this authority record in Slice 1.3.

---

# 4. Revised normative synchronization order

Revision 2 Section 8 is replaced only where authorization semantics change.

```text
A. PREPARATION / HUMAN AUTHORITY

1.  Validate request structure, target-registry identity, expected branch, and expected base CommitRef.
2.  Load Project and require Project.primary_repository == selection.repository.
3.  Recheck captured local Slice 1.1 access selection.
4.  Mint repository-scoped READ token.
5.  Read provider repository identity; require ID/node/full_name match and non-archived.
6.  Require provider default_branch == expected_default_branch.
7.  Resolve exact default-branch head.
8.  If no head exists, return RepositorySyncNoDefaultHead.
9.  Capture exact commit/root tree and inspect/classify .relay.
10. If exact current snapshot already equals target, return CURRENT with wrote_remote=false.
11. Require current head == expected_base_commit.
12. For initialized state, validate current -> target registry transition.
13. Validate unregistered-path adoption/conflict and workflow-path restrictions.
14. Construct and validate complete logical target snapshot.
15. Construct exact RepositorySyncSubjectV1 and subject_digest.
16. Return SYNCHRONIZABLE preparation. No WRITE token or remote Git objects exist yet.
17. Human Authority explicitly persists RepositoryMutationAuthorization for that exact subject.

B. EXECUTION

18. Re-run steps 1-15; preparation is not trusted as current state.
19. Load exact RepositoryMutationAuthorization and require S13-D41 match.
20. Require stored WRITE PROFILE.
21. Mint repository-scoped WRITE token.
22. Create only permitted changed artifact blobs and target registry blob.
23. Create one target tree from exact base tree.
24. Create one commit whose single parent is expected_base_commit.
25. Reload and revalidate the exact RepositoryMutationAuthorization.
26. Recheck local access authority, state_revision, membership, and WRITE PROFILE.
27. Re-read provider identity/default branch/non-archived state.
28. Re-resolve default-branch head; require expected_base_commit.
29. Call one non-force default-branch ref update.
30. On definitive success, continue.
31. On definitive rejection, return typed failure.
32. On indeterminate transport outcome, reconcile by Revision 2 S13-D31; never retry the write.
33. Require visible branch head == created commit SHA before success.
34. Re-read provider identity/default branch/non-archived state.
35. Recheck local access authority for observability.
36. Read and validate exact resulting commit/tree/registry/artifact bytes.
37. Return exact prior/resulting CommitRefs with state=CURRENT.
```

Steps 22-24 may leave unreachable Git objects after a later pre-visibility guard failure. They never become repository authority unless the ref moves and exact post-write verification succeeds.

---

# 5. API and model amendments

## 5.1 Remove Revision 2 AuthorizationGrant extension

Revision 2 S13-D23 through S13-D27 are replaced by Revision 3 S13-D36 through S13-D43.

`AuthorizationGrant` is NOT extended with `subject_digest` by Slice 1.3.

Its accepted baseline/gate semantics remain unchanged.

## 5.2 Repository sync request

Normative request:

```text
RepositorySyncRequest
  selection: GitHubRepositoryAccessSelection
  expected_default_branch: str
  expected_base_commit: CommitRef
  target_registry: RepositoryRegistry
  artifact_writes: tuple[RepositoryArtifactWrite, ...]
  authorization_id: RepositoryMutationAuthorizationId | None
```

## 5.3 Preparation result

New public model:

```text
RepositorySyncPreparation
  state: RepositoryContractState
  prior_commit: CommitRef
  subject: RepositorySyncSubjectV1 | None
  subject_digest: ContentDigest | None
  changed_paths: tuple[str, ...]
```

`state` for a successful preparation is either `CURRENT` or `SYNCHRONIZABLE`.

## 5.4 New authority identity

New typed ID:

```text
RepositoryMutationAuthorizationId
```

A distinct ID type avoids conflating mutation authority with existing `AuthorizationId` / handover authorization semantics.

---

# 6. Acceptance-criteria amendment

Revision 1 A01-A80 and Revision 2 F002-F006 amendments remain in force.

Revision 2 A85-A87 and A96 are replaced.

Replacement and additional criteria:

- **A85-R3** — Every non-no-op remote mutation requires an immutable `RepositoryMutationAuthorization` issued by a HUMAN actor for the exact `RepositorySyncSubjectV1`.
- **A86-R3** — Mutation authorization is checked before WRITE-token minting and reloaded/rechecked immediately before ref visibility.
- **A87-R3** — Slice 1.3 does not alter or reinterpret existing `AuthorizationGrant`, `HandoverGate`, or `HumanGateDecision` semantics.
- **A96-R3** — Slice 1.3 adds deterministic SQLite migration v3 for `repository_mutation_authorizations`; repository schema v1 and runtime dependencies remain unchanged.
- **A97** — Read-only preparation produces the exact subject/digest Human Authority approves and creates no remote Git object.
- **A98** — Execution re-runs preparation checks and recomputes the subject; a prior preparation result is not trusted as current provider state.
- **A99** — Repository mutation authorization contains no BaselineId and therefore works for a valid `UNINITIALIZED` repository with an existing default-branch head.
- **A100** — Mutation authorization cannot make any lifecycle handover GREEN and is not accepted by the existing handover engine as an `AuthorizationGrant`.
- **A101** — Persisted authorization indexed columns and typed payload are integrity-checked using the accepted persistence pattern.
- **A102** — No authorization update/delete or automatic consumption state is introduced in Slice 1.3.
- **A103** — Reuse of the exact authorization cannot retarget a different branch head because expected-base equality and non-force ref movement remain mandatory.
- **A104** — A resulting synchronized commit is not automatically persisted or treated as a Relay Baseline.

---

# 7. Required-test amendment

Implementation evidence must additionally cover:

```text
prepare UNINITIALIZED repository without Baseline
prepare SYNCHRONIZABLE creates no WRITE token
prepare SYNCHRONIZABLE creates no Git objects
prepare CURRENT requires no mutation authorization
human actor required for mutation authorization
persist/load RepositoryMutationAuthorization round trip
payload/index disagreement fails integrity verification
subject digest mismatch rejected at authorization insert
missing mutation authorization before WRITE token
wrong project authorization rejected
wrong slice authorization rejected
wrong subject authorization rejected
authorization rechecked before ref visibility
provider/base change after preparation causes stale/conflict before visibility
existing AuthorizationGrant does not authorize repository mutation
RepositoryMutationAuthorization is not accepted as HandoverGate authorization
migration v3 checksum and restart verification
schema-v1 .relay registry remains unchanged
```

Race tests must continue proving that mutation authority, provider identity, local access state, `state_revision`, and head checks all occur before ref visibility.

---

# 8. Revised implementation change surface

Revision 3 changes the expected implementation surface only enough to add dedicated authority persistence and preparation.

| Dimension | Revision 3 expectation |
|---|---:|
| Existing production files touched | 6-8 |
| Existing governance model semantics changed | 0 |
| New production package | `repository_sync` remains |
| New production files | 3-5 |
| New runtime dependencies | 0 |
| Persistent schema changes | 1 table + 1 index |
| New migrations | 1 (`v3`) |
| Repository-contract schema changes | 0 |

Expected existing surfaces may include:

```text
domain IDs / exports
persistence migrations
persistence exports
GitHub client protocol / HTTP adapter
GitHub integration token minting
```

Expected new Slice 1.3 surfaces remain:

```text
repository_sync models
repository_sync errors
repository_sync persistence/service
```

Minimum Sufficient Architecture remains mandatory; F007 does not authorize unrelated governance refactoring.

---

# 9. Revision 3 closure

F007 is addressed by separating repository side-effect authority from lifecycle handover authority:

```text
exact read-only preparation
        ↓
RepositorySyncSubjectV1 + digest
        ↓
explicit HUMAN RepositoryMutationAuthorization
        ↓
durable local authority record without BaselineId/GateId
        ↓
execution recomputes exact subject
        ↓
authority checked before WRITE token
        ↓
Git objects built
        ↓
authority + provider/local/head checks repeated
        ↓
one non-force ref movement
        ↓
exact post-write verification
```

This supports both initialized and uninitialized repositories without fabricating a Baseline, while preserving the accepted handover-gate engine untouched.

Architecture escalation is not required.

Implementation remains NOT AUTHORIZED.
