# Slice 1.2 — Repository Registration and Baseline Resolution
## Revision 3 Amendment

**Document revision:** 3 amendment  
**Status:** REVIEW  
**Document class:** Lockable design record amendment  
**Phase:** 1 — GitHub and Human-Controlled Project Workflow  
**Slice:** 1.2  
**Authorized baseline:** `1ec84fe0507f5e1a7dfff3098d285db628cb3649`  
**Amends:** Revision 1 at `8d94e7408e4f24bf87e32dfc73273fd42f27a9da` plus Revision 2 at `8667b3e8a20e317fb3c5ccc66278e1a14aebdafd`  
**Review finding source:** `RLY-S12-DESIGN-EVAL-002` — REVISE  
**Implementation:** NOT AUTHORIZED  
**Date:** 2026-09-27

---

# 1. Amendment authority and precedence

This amendment resolves exactly:

```text
RLY-S12-DREV2-F004
REMOTE_REPOSITORY_IDENTITY_DOES_NOT_BRACKET_SNAPSHOT
```

Revision 1 and Revision 2 remain normative except where this amendment explicitly replaces or tightens them.

Combined Slice 1.2 design authority is:

```text
Revision 1
8d94e7408e4f24bf87e32dfc73273fd42f27a9da

+

Revision 2 amendment
8667b3e8a20e317fb3c5ccc66278e1a14aebdafd

+

Revision 3 amendment
<this commit>
```

No production implementation, migration, dependency change, or Slice 1.3 work is authorized by this document.

---

# 2. P1-D90 — Provider identity brackets the remote snapshot

The same captured provider repository identity MUST be validated both before and after the remote commit/tree/blob proof.

The GitHub-controlled operation therefore uses this sequence:

```text
capture Slice 1.1 provider-access selection
        ↓
mint token scoped to selection.github_repository_id
        ↓
PRE-SNAPSHOT repository identity check
        ↓
validate:
provider id == selection.github_repository_id
provider node_id == selection.github_node_id
provider full_name == selection.repository.path
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
POST-SNAPSHOT repository identity check
        ↓
validate the same:
provider id == selection.github_repository_id
provider node_id == selection.github_node_id
provider full_name == selection.repository.path
        ↓
BEGIN IMMEDIATE
        ↓
final local Slice 1.1 access guard from Revision 2
        ↓
Artifact + Baseline persistence
```

The pre-snapshot and post-snapshot checks MUST use the same captured:

```text
project_id
installation_id
github_repository_id
github_node_id
RepositoryRef
expected_state_revision
```

No provider binding, repository, or installation may be rediscovered between those checks.

---

# 3. P1-D91 — Post-snapshot identity failure is fail-closed

If the post-snapshot provider check does not exactly match the captured selection:

```text
RepositoryProviderIdentityChanged
or equivalent typed error
```

and:

```text
no new Artifact
no Baseline
```

is persisted.

The same fail-closed result applies if the post-snapshot identity request cannot establish repository identity because the token/repository is unavailable, authentication is lost, the provider rate limits the request, or provider JSON is malformed.

Remote proof is complete only after the post-snapshot identity check succeeds.

---

# 4. P1-D92 — Redirects are revalidated after snapshot proof

Revision 2 P1-D85 remains in force and is tightened.

Ordinary HTTPS redirects may occur, but redirects never become Relay authority.

The post-snapshot provider identity check MUST again validate:

```text
provider repository id
provider node_id
provider canonical full_name
```

against the same captured selection.

Therefore a rename, transfer, redirect change, or old-path reuse that becomes observable during snapshot resolution blocks persistence.

Relay MUST NOT update `Project.primary_repository` or the captured `RepositoryRef` to follow provider-side changes.

---

# 5. P1-D93 — No cross-system atomicity claim

Relay MUST NOT claim an atomic transaction spanning GitHub and local SQLite.

The guarantee is instead bounded by observable authority:

```text
provider side:
any repository identity/access change that becomes observable
during snapshot resolution or the final provider identity check
blocks persistence

local Relay side:
any Slice 1.1 state/access change reflected in Relay before the
final SQLite transaction commits blocks persistence
```

There is inevitably a distributed-system observation boundary between the final successful GitHub identity response and the local SQLite commit.

The design does not fabricate stronger atomicity than the systems can provide.

---

# 6. P1-D94 — Revised A89 semantics

Revision 1 A89 is replaced by:

```text
A89
Any provider access revocation or repository identity change that
becomes observable during snapshot resolution or the final provider
identity check leaves no new Artifact or Baseline.

Any Slice 1.1 access-state change reflected in Relay before the final
SQLite transaction commits leaves no new Artifact or Baseline.

Relay does not claim an atomic transaction spanning GitHub and SQLite.
```

This wording supersedes any broader reading of Revision 1 A89.

All other Revision 1 acceptance criteria remain unchanged except where Revision 2 or Revision 3 explicitly tightens them.

---

# 7. P1-D95 — Final provider check precedes local transaction

The post-snapshot provider identity check occurs after all remote commit/tree/blob/registry/artifact reads are complete and before `BEGIN IMMEDIATE`.

Required ordering:

```text
remote snapshot proof complete
        ↓
post-snapshot provider identity proof
        ↓
BEGIN IMMEDIATE
        ↓
local state_revision / ACTIVE / READY / membership guard
        ↓
Artifact + Baseline persistence
```

The SQLite transaction MUST NOT be held open while performing provider network requests.

This preserves a bounded local transaction and avoids holding a database write lock across remote I/O.

---

# 8. Revised high-level operation

The Revision-2 operation remains:

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

with this tightened flow:

```text
load Project
    ↓
validate selection.repository == Project.primary_repository
    ↓
mint repo-scoped token from captured provider IDs
    ↓
PRE provider identity proof
    ↓
resolve selector once
    ↓
commit/tree/blob/registry/artifact proof
    ↓
POST provider identity proof
    ↓
BEGIN IMMEDIATE
    ↓
Revision-2 final local access guard
    ↓
verify/create immutable Artifacts
verify Decisions
insert Baseline
    ↓
COMMIT
```

No hidden retry may replace either identity check or refresh the provider-access selection.

A caller may explicitly restart the full command.

---

# 9. Revised race semantics

## Repository rename during snapshot

```text
selection:
id 900
node R_900
full_name old/name

PRE check:
old/name → id 900 / R_900 / old/name
PASS

snapshot reads begin

provider rename:
old/name → new/name

POST check:
provider canonical full_name != old/name

→ RepositoryProviderIdentityChanged
→ no Artifact
→ no Baseline
```

## Repository transfer during snapshot

```text
PRE check:
captured provider identity PASS

provider transfer occurs

POST check:
canonical provider identity/path differs
or repository is unavailable

→ fail closed
→ no persistence
```

## Old path reused during snapshot

```text
PRE check:
old/name → id 900 / node R_900

path later resolves to different provider repository:
id 901 / node R_901

POST check:
identity mismatch

→ fail closed
```

## Local access state changes after POST provider check

```text
POST provider identity check:
PASS

webhook arrives before/during final SQLite transaction:
state_revision N → N+1

final Revision-2 local guard:
current revision != expected revision

→ rollback
→ no baseline
```

## Provider change after final observable check

```text
POST provider identity check:
PASS

provider changes after the response
before/during local commit
but change is not yet observable locally

local state remains unchanged

→ design makes no impossible cross-system atomicity claim
```

A later operation will observe the new provider/local state under the normal Slice 1.1/1.2 rules.

---

# 10. Acceptance-criteria additions

Revision 1 A01–A110 and Revision 2 A111–A132 remain in force except for revised A89.

Additional criteria:

```text
A133 provider repository identity is checked before snapshot reads.

A134 provider repository identity is checked again after all snapshot reads.

A135 both identity checks use the exact same captured provider-access selection.

A136 post-snapshot provider repository ID must equal the selected provider ID.

A137 post-snapshot node_id must equal the selected node ID.

A138 post-snapshot canonical full_name must equal RepositoryRef.path.

A139 redirect behavior cannot bypass the post-snapshot identity proof.

A140 post-snapshot identity mismatch leaves no new Artifact or Baseline.

A141 post-snapshot inability to establish provider identity fails closed.

A142 no provider-selection rediscovery occurs between the two identity checks.

A143 no hidden retry refreshes the identity evidence.

A144 the post-snapshot provider check completes before BEGIN IMMEDIATE.

A145 provider network I/O is not performed while the final SQLite write
     transaction is held open.

A146 Relay makes no atomicity claim spanning GitHub and SQLite.

A147 observable provider revocation/identity change blocks persistence.

A148 local Slice 1.1 authority change before SQLite commit blocks persistence.

A149 Slice 1.3 remains unauthorized.
```

---

# 11. Required Revision-3 regressions

Implementation must include deterministic coverage equivalent to:

```text
test_provider_identity_checked_before_snapshot

test_provider_identity_checked_after_snapshot

test_pre_and_post_identity_checks_use_same_selection

test_repository_rename_during_snapshot_blocks_baseline

test_repository_transfer_during_snapshot_blocks_baseline

test_old_path_reuse_during_snapshot_blocks_baseline

test_post_snapshot_repository_id_mismatch_blocks_baseline

test_post_snapshot_node_id_mismatch_blocks_baseline

test_post_snapshot_full_name_mismatch_blocks_baseline

test_post_snapshot_identity_failure_leaves_no_artifact

test_post_snapshot_identity_failure_leaves_no_baseline

test_same_provider_identity_before_and_after_allows_final_guard

test_provider_network_io_finishes_before_final_write_transaction

test_local_revision_change_after_post_check_still_blocks_baseline
```

Revision 1 and Revision 2 regressions remain required.

---

# 12. Finding disposition

```text
RLY-S12-DREV1-F001
RESOLVED BY REVISION 2

RLY-S12-DREV1-F002
RESOLVED BY REVISION 2

RLY-S12-DREV1-F003
RESOLVED BY REVISION 2

RLY-S12-DREV2-F004
RESOLVED BY P1-D90 / D91 / D92 / D93 / D94 / D95
```

---

# 13. Scope confirmation

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

# 14. Required next gate

The combined Revision 1 + Revision 2 + Revision 3 design must return to:

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
