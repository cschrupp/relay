# Slice 1.2 — Repository Registration and Baseline Resolution
## Revision 2 Amendment

**Document revision:** 2 amendment  
**Status:** REVIEW  
**Document class:** Lockable design record amendment  
**Phase:** 1 — GitHub and Human-Controlled Project Workflow  
**Slice:** 1.2  
**Authorized baseline:** `1ec84fe0507f5e1a7dfff3098d285db628cb3649`  
**Amends:** Revision 1 at `8d94e7408e4f24bf87e32dfc73273fd42f27a9da`  
**Review finding source:** `RLY-S12-DESIGN-EVAL-001` — REVISE  
**Implementation:** NOT AUTHORIZED  
**Date:** 2026-09-27

---

# 1. Amendment authority and precedence

This amendment resolves exactly:

```text
RLY-S12-DREV1-F001
RESOLUTION_CONTRACT_LOSES_GITHUB_BINDING_IDENTITY

RLY-S12-DREV1-F002
ACCESS_REVOCATION_CAN_RACE_BASELINE_PERSISTENCE

RLY-S12-DREV1-F003
REMOTE_PROVIDER_REPOSITORY_IDENTITY_NOT_REVALIDATED
```

Revision 1 remains normative except where this amendment explicitly replaces or tightens it.

Combined Slice 1.2 design authority is:

```text
Revision 1
8d94e7408e4f24bf87e32dfc73273fd42f27a9da

+

Revision 2 amendment
<this commit>
```

No production implementation, migration, dependency change, or Slice 1.3 work is authorized by this document.

---

# 2. P1-D81 — Explicit GitHub repository-access selection

Slice 1.2 MUST preserve the provider binding that proved access rather than collapsing immediately to `RepositoryRef`.

The GitHub-controlled entry path uses an immutable ephemeral value equivalent to:

```python
GitHubRepositoryAccessSelection(
    project_id: ProjectId,
    installation_id: int,
    github_repository_id: int,
    github_node_id: str,
    repository: RepositoryRef,
    expected_state_revision: int,
)
```

Equivalent naming is acceptable.

The value may be constructed only from a Slice 1.1 binding where all of the following are true at selection time:

```text
binding belongs to project_id

installation status == ACTIVE

readiness == READY

github_repository_id is present in the confirmed repository set

captured node_id comes from that same confirmed repository row

repository == Project.primary_repository

expected_state_revision == current binding state_revision
```

This value is operation evidence only.

It is NOT:

```text
a new core domain object
a second repository-registration authority
a new durable repository binding
a generic provider abstraction
```

The accepted `Project.primary_repository` remains the sole Relay project-repository authority.

---

# 3. P1-D82 — Selection creation is fail-closed

The Slice 1.1 integration/store layer may expose one narrow read operation that returns the provider-access selection.

Selection creation MUST fail if:

```text
project binding does not exist

installation is not ACTIVE

readiness is not READY

repository ID is absent

repository path cannot produce the exact Project.primary_repository

provider repository identity fields are malformed

state_revision is unavailable
```

No hidden synchronization is performed.

No stale or non-READY binding is promoted by selection creation.

---

# 4. P1-D83 — Repository-scoped token uses captured provider identity

The installation token used for Slice 1.2 MUST be minted using:

```text
selection.installation_id
selection.github_repository_id
```

when GitHub supports repository narrowing.

The token remains short-lived and ephemeral.

No token cache is introduced.

The operation MUST NOT rediscover an installation by repository path or search across project bindings after selection has been captured.

---

# 5. P1-D84 — Live provider repository identity proof

Before ref resolution, Relay performs a read-only remote repository identity check against the captured selection.

Conceptually:

```text
GET /repos/{owner}/{repository}
```

using the repository-scoped installation token.

The response is accepted only when:

```text
provider repository id
==
selection.github_repository_id

provider node_id
==
selection.github_node_id

provider canonical full_name
==
selection.repository.path

selection.repository
==
Project.primary_repository
```

The provider response fields remain untrusted until strictly validated.

Repository rename, transfer, redirect to a new canonical path, or path reuse therefore fails closed rather than silently rebinding Relay authority.

Slice 1.2 MUST NOT update:

```text
Project.primary_repository
RepositoryRef
```

to follow provider-side identity changes.

Any authority change is separately governed.

---

# 6. P1-D85 — Redirect semantics do not weaken identity proof

The transport may follow ordinary HTTPS redirects.

A redirect is not authority.

After any redirect, Relay MUST validate the final provider payload under P1-D84.

Thus:

```text
old owner/repo
→ HTTP redirect
→ new canonical repository payload
```

is accepted only if all stable provider identity and canonical-name checks still match the captured selection.

Otherwise:

```text
RepositoryProviderIdentityChanged
or equivalent typed error
```

and no baseline is persisted.

---

# 7. P1-D86 — Access revision is captured before remote work

The operation's authorization snapshot includes:

```text
selection.expected_state_revision
```

captured before token minting and remote snapshot resolution.

This revision is not merely diagnostic metadata.

It is an optimistic concurrency guard over the exact Slice 1.1 access authority used to authorize the operation.

---

# 8. P1-D87 — Final atomic access guard

After the complete remote commit/tree/blob snapshot has been verified, but before any new core `Artifact` or `Baseline` is inserted, the final SQLite write transaction MUST re-check the Slice 1.1 binding.

Within the same transaction used for Artifact/Baseline persistence require:

```text
Project still exists

Project.primary_repository == selection.repository

GitHub binding exists for:
(project_id, installation_id)

binding.state_revision
==
selection.expected_state_revision

binding installation status == ACTIVE

binding readiness == READY

selection.github_repository_id
still exists in github_installation_repositories

stored repository node_id
==
selection.github_node_id

stored repository full_name
==
selection.repository.path
```

Only after all checks pass may the transaction:

```text
verify/materialize missing Artifacts

verify existing Artifact bindings

verify Decision IDs

insert Baseline
```

Any mismatch causes one typed access/concurrency failure and the transaction rolls back completely.

No Artifact or Baseline remains.

---

# 9. P1-D88 — Any state revision change invalidates the operation

For Slice 1.2, equality of `state_revision` is intentionally strict.

Even if a later state again appears:

```text
ACTIVE / READY
```

a revision change means the authorization evidence used at operation start is no longer the same evidence.

Therefore:

```text
current state_revision != expected_state_revision
→ fail closed
```

The service MUST NOT inspect event history and decide that an intervening change was harmless.

The caller may explicitly restart the entire operation to obtain a fresh selection.

No hidden retry occurs.

---

# 10. P1-D89 — Remote proof does not override local authority

Successful GitHub commit/tree/blob reads prove only the provider snapshot.

They do not supersede Relay's local authorization state.

A valid remote snapshot with stale local access evidence MUST NOT become a durable Baseline.

Both are required:

```text
verified remote snapshot
+
unchanged local Slice 1.1 access authority
```

---

# 11. Revised high-level operation

The GitHub-controlled operation is tightened to the equivalent of:

```python
resolve_and_persist_github_baseline(
    *,
    selection: GitHubRepositoryAccessSelection,
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
validate selection.repository == Project.primary_repository
    ↓
validate captured Slice 1.1 selection was ACTIVE / READY
    ↓
mint token narrowed to selection.github_repository_id
    ↓
GET repository identity
    ↓
validate provider id + node_id + canonical full_name
    ↓
resolve selector once → canonical commit SHA
    ↓
read exact commit object → root tree
    ↓
prove required tree paths and .relay direct entries
    ↓
read exact registry/artifact blobs
    ↓
validate repository contract + raw-byte digests
    ↓
construct verified CommitRef + artifact candidates
    ↓
BEGIN IMMEDIATE / one SQLite transaction
    ↓
re-check Project
re-check exact binding state_revision
re-check ACTIVE / READY
re-check repository ID/node_id/full_name membership
    ↓
verify/create immutable Artifacts
verify Decisions
insert Baseline
    ↓
COMMIT
```

If any final guard fails:

```text
ROLLBACK
no new Artifact
no Baseline
```

---

# 12. Persistence boundary

Revision 2 does not justify a schema migration.

Existing durable state is sufficient:

```text
projects

artifacts

decisions

baselines

github_installations

github_installation_repositories
```

The final access guard is a transactional read of existing Slice 1.1 state followed by existing Slice 1.2 Artifact/Baseline writes.

Migration v3 remains:

```text
NOT JUSTIFIED
```

If implementation discovers that atomicity cannot be achieved with the existing SQLite transaction boundary, STOP and escalate the design.

---

# 13. Targeted tree traversal clarification

Revision 1 permitted complete recursive repository enumeration.

Revision 2 clarifies that Slice 1.2 need only prove the repository paths relevant to accepted repository authority:

```text
.relay directory existence/type

all direct .relay entries

.relay/registry.json

every registry-declared artifact path

all tree nodes needed to reach those paths
```

Implementation MAY use complete recursive enumeration if the provider reports a complete non-truncated tree.

If recursive output is truncated, deterministic targeted subtree traversal is preferred.

Unrelated repository files do not need to be materialized merely to validate the Relay authority set.

Completeness of the `.relay` direct-entry check and every registered artifact path remains mandatory.

---

# 14. Error-contract additions

Revision 2 requires typed distinction equivalent to:

```text
RepositoryAccessChanged
    local binding revision/status/readiness/repository membership changed

RepositoryProviderIdentityChanged
    live provider repository id/node_id/full_name differs from selection

RepositorySelectionInvalid
    captured provider-access selection is internally inconsistent
```

Equivalent names are acceptable.

These errors MUST remain distinct from:

```text
ref not found
authentication failure
rate limit
snapshot integrity failure
baseline persistence integrity failure
```

---

# 15. Revised race semantics

## Suspension during snapshot

```text
start:
state_revision 12
ACTIVE / READY

remote proof underway

webhook:
state_revision 13
SUSPENDED

final transaction:
13 != 12
→ rollback
→ no baseline
```

## Repository removal during snapshot

```text
start:
repository 900 present
revision 20

webhook removal:
revision 21
repository 900 removed

final transaction:
revision mismatch / membership failure
→ rollback
```

## Permission change followed by successful resync

```text
start:
revision 30

permission webhook:
revision 31

explicit resync:
revision 32
ACTIVE / READY again

old operation finalizes:
32 != 30
→ fail
```

A fresh caller retry may start from revision 32.

## Repository rename/transfer

```text
selection:
id 900
node R_900
full_name old/name

live provider payload:
id 900
node R_900
full_name new/name

→ provider identity changed
→ no baseline
```

Relay does not silently mutate its repository authority.

---

# 16. Acceptance-criteria amendments

Revision 1 A01–A110 remain in force except where tightened below.

Additional criteria:

```text
A111 provider-access selection includes project, installation ID,
     GitHub repository ID, node ID, RepositoryRef, and expected state revision.

A112 selection can be produced only from the current ACTIVE / READY
     confirmed repository set.

A113 operation never searches for an installation by repository path
     after selection capture.

A114 installation token is scoped to the selected GitHub repository ID
     when supported.

A115 live repository metadata is fetched before ref resolution.

A116 live GitHub repository ID must equal the captured provider ID.

A117 live GitHub node_id must equal the captured node ID.

A118 live canonical full_name must equal RepositoryRef.path.

A119 redirects cannot bypass A116–A118.

A120 remote identity mismatch fails without mutating Project/RepositoryRef.

A121 selection captures the current Slice 1.1 state_revision.

A122 final Artifact/Baseline transaction re-checks that exact revision.

A123 final transaction requires ACTIVE / READY.

A124 final transaction requires selected repository membership.

A125 final transaction re-checks stored repository node_id/full_name identity.

A126 any state_revision change invalidates the in-flight operation.

A127 access-guard failure leaves no new Artifact or Baseline.

A128 no hidden retry refreshes the access selection.

A129 a fresh explicit caller retry may obtain a new selection.

A130 remote snapshot proof alone cannot authorize persistence.

A131 no migration v3 is introduced for these corrections.

A132 Slice 1.3 remains unauthorized.
```

---

# 17. Required Revision-2 regressions

Implementation must include deterministic coverage equivalent to:

```text
test_access_selection_requires_active_ready_binding

test_access_selection_captures_state_revision

test_access_selection_preserves_installation_and_repository_ids

test_operation_does_not_rediscover_installation_by_path

test_repo_scoped_token_uses_selected_repository_id

test_remote_repository_id_must_match_selection

test_remote_repository_node_id_must_match_selection

test_remote_repository_full_name_must_match_project_repository

test_repository_rename_redirect_fails_closed

test_reused_owner_repo_path_cannot_replace_selected_repository

test_webhook_suspension_during_snapshot_blocks_baseline

test_repository_removal_during_snapshot_blocks_baseline

test_permission_change_during_snapshot_blocks_baseline

test_resync_to_ready_still_invalidates_old_operation

test_unchanged_access_revision_allows_baseline

test_final_guard_is_atomic_with_artifact_and_baseline_insert

test_access_guard_failure_rolls_back_new_artifacts

test_no_hidden_retry_refreshes_access_selection
```

Revision 1 regressions remain required.

---

# 18. Finding disposition

```text
RLY-S12-DREV1-F001
RESOLVED BY P1-D81 / D82 / D83

RLY-S12-DREV1-F002
RESOLVED BY P1-D86 / D87 / D88 / D89

RLY-S12-DREV1-F003
RESOLVED BY P1-D84 / D85
```

---

# 19. Scope confirmation

Still not authorized:

```text
production implementation

migration v3

GitHub write APIs

Project repository mutation

remote .relay creation/repair

Slice 1.3

generic provider framework

local Git/worktree manager

background workers

agent execution
```

---

# 20. Required next gate

The combined Revision 1 + Revision 2 design must return to:

```text
Independent Design Reviewer — GPT-5.6 Sol
```

Allowed outcomes:

```text
ACCEPT
REVISE
ESCALATE
```

Passing review still does not authorize implementation.

STOP.
