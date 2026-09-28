# Slice 1.3 — `.relay/` Initialization and Sync — Revision 4 Amendment

**Status:** REVIEW  
**Design revision:** Revision 4 Amendment  
**Design authority:** `RLY-S13-DESIGN-AUTH-001`  
**Parent design:** `docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC.md`  
**Revision 2:** `docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV2_AMENDMENT.md`  
**Revision 3:** `docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV3_AMENDMENT.md`  
**Revision 3 head:** `8e8ab70cf8c9b52d628b0b658179c1fe287c93ea`  
**Review handover:** `RLY-S13-DESIGN-EVAL-003 — REVISE`  
**Role:** Architect / Contract Designer  
**Preferred model:** GPT-5.6 Sol  
**Executing model:** GPT-5.6 Sol  
**Implementation:** NOT AUTHORIZED  
**Date:** 2026-09-28

---

# 1. Amendment purpose

This bounded amendment resolves only combined-review finding F008.

Revision 1, Revision 2, and Revision 3 remain authoritative except where this amendment explicitly removes Slice identity from the Revision 3 repository-mutation authority contract.

Finding addressed:

```text
F008 BLOCKING — RepositoryMutationAuthorization carried a mandatory SliceId,
                but SliceId was absent from RepositorySyncSubjectV1,
                absent from preparation and authorization APIs,
                and compared at execution against an undefined
                "current Slice 1.3 authority context".
```

Preserved without redesign:

```text
schema-v1 .relay/registry.json
RepositorySyncSubjectV1 exact subject digest
read-only preparation before Human Authority approval
dedicated RepositoryMutationAuthorization
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
SQLite migration v3 concept
no automatic Baseline persistence
no branch creation
no pull request
no force push
no agent execution
```

Revision 4 does not reopen F001–F007.

---

# 2. F008 — repository mutation authority is project / exact-subject scoped

## S13-D46 — Remove SliceId from repository-mutation authority

Revision 3 S13-D37 is amended.

Normative model:

```text
RepositoryMutationAuthorization
  authorization_id: RepositoryMutationAuthorizationId
  project_id: ProjectId
  subject_schema_version: 1
  subject: RepositorySyncSubjectV1
  subject_digest: ContentDigest
  actor: ActorRef
  granted_at: datetime
  reason: str
```

There is no `slice_id` field.

Invariants remain:

- `actor.kind == HUMAN`;
- `reason` is nonblank;
- `granted_at` is timezone-aware UTC;
- `subject_schema_version == 1`;
- `subject.project_id == project_id`;
- `subject_digest == sha256(canonical RepositorySyncSubjectV1 bytes)`;
- the record is immutable once inserted.

The authorization contains no `baseline_id`, no `gate_id`, and no `slice_id`.

This is intentional. The authority answers exactly one question:

> Has Human Authority approved this exact repository side effect for this Relay project/repository subject?

Engineering Slice identity is workflow/audit context, not part of the repository-mutation authority proof.

## S13-D47 — Project and repository subject already provide complete mutation scope

`RepositorySyncSubjectV1` already binds:

```text
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

Therefore the mutation authority is already constrained to one exact:

```text
Relay project
repository identity
provider binding
provider-access revision
default branch
base commit
target registry
artifact byte set
```

Adding a separate SliceId does not narrow the remote side effect further.

Removing SliceId avoids coupling repository synchronization to future general Slice CRUD or to an undefined runtime interpretation of the development-roadmap label "Slice 1.3".

## S13-D48 — Preparation and authorization APIs require no Slice context

Revision 3 S13-D39 and S13-D40 are preserved without adding a Slice parameter.

Normative preparation remains:

```text
prepare_repository_sync(request_without_authorization)
    -> RepositorySyncPreparation
```

Normative Human Authority operation remains:

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

Human Authority approves the exact prepared subject shown by Relay.

No caller-supplied SliceId is needed to create or validate that approval.

## S13-D49 — Execution checks project and exact subject, not Slice identity

Revision 3 S13-D41 is amended.

For every non-no-op execution, before WRITE-token minting Relay loads the immutable `RepositoryMutationAuthorization` and requires:

```text
authorization exists
authorization.actor.kind == HUMAN
authorization.project_id == selection.project_id
authorization.subject_schema_version == 1
authorization.subject == recomputed subject
authorization.subject_digest == recomputed subject digest
```

Immediately before ref visibility Relay reloads the same authorization and repeats the exact project/subject match together with the accepted local/provider/head guards.

The following Revision 3 condition is removed and has no replacement:

```text
authorization.slice_id == current Slice 1.3 authority context
```

There is no mutation-time Slice authority lookup.

This does not authorize implementation or lifecycle transitions. Existing handover governance remains independently applicable exactly as Revision 3 S13-D36/S13-D43 require.

## S13-D50 — Optional future audit relationships must not change mutation authority semantics

A later workflow may record that a repository mutation was requested by, associated with, or produced during some engineering Slice.

Such provenance may be represented by a higher-level audit relationship when that workflow exists.

It MUST NOT retroactively become a required field of `RepositoryMutationAuthorization` unless separately designed and authorized.

Slice 1.3 therefore does not introduce a speculative Slice linkage merely for provenance convenience.

---

# 3. Persistence amendment

## S13-D51 — Migration v3 removes SliceId from the table

Revision 3 S13-D44 is amended.

Normative minimum table shape:

```text
CREATE TABLE repository_mutation_authorizations (
    authorization_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    subject_digest TEXT NOT NULL,
    payload_json TEXT NOT NULL
)
```

Normative index remains:

```text
CREATE INDEX repository_mutation_authorizations_by_project_subject
ON repository_mutation_authorizations(project_id, subject_digest)
```

There is no `slice_id` column and no foreign key to `slices`.

The typed JSON payload remains the authority record. Indexed columns MUST agree with the typed payload on load using the accepted persistence-integrity pattern.

Migration requirements remain deterministic and checksummed under the existing migration engine.

No existing table or column is reinterpreted.

This remains a local runtime-state migration only; schema-v1 `.relay/registry.json` is unchanged.

## S13-D52 — Persistence API remains narrow

Revision 3 S13-D45 is preserved:

```text
insert_repository_mutation_authorization(...)
load_repository_mutation_authorization(...)
```

Insert remains append-only / immutable-by-ID.

No update/delete API is introduced.

Removing SliceId does not add replacement persistence state.

---

# 4. Acceptance-criteria amendment

All combined Revision 1 + Revision 2 + Revision 3 criteria remain in force except where explicitly amended here.

Replacement:

- **A99-R4** — `RepositoryMutationAuthorization` contains no BaselineId, GateId, or SliceId and therefore supports a valid `UNINITIALIZED` repository with an existing default-branch head without fabricated lifecycle/repository authority.

Additional criteria:

- **A105** — Mutation authorization is scoped by `project_id` plus exact `RepositorySyncSubjectV1`; no SliceId participates in preparation, authorization persistence, or execution validation.
- **A106** — Migration v3 `repository_mutation_authorizations` has no `slice_id` column or foreign key to `slices`.
- **A107** — Execution rejects wrong-project or wrong-subject authorization but performs no Slice authority lookup.
- **A108** — Removing SliceId does not alter the existing handover-gate engine, lifecycle authority, or implementation authorization boundary.
- **A109** — Future optional Slice/audit provenance is outside Slice 1.3 and cannot silently change repository-mutation authority semantics.

---

# 5. Required-test amendment

Revision 3 test requirements remain, with the following changes.

Remove:

```text
wrong slice authorization rejected
```

Add:

```text
RepositoryMutationAuthorization model has no SliceId
migration v3 table has no slice_id column or slices FK
authorization insert/load succeeds without Slice record
authorization validates exact project + subject only
wrong project authorization rejected
wrong subject authorization rejected
execution performs no Slice lookup for mutation authority
existing handover governance remains unaffected
```

Race tests remain unchanged: mutation authority, provider identity, local access state, `state_revision`, and exact head checks must all occur before ref visibility.

---

# 6. Revised implementation change surface

Revision 3 implementation-size expectations remain materially unchanged.

| Dimension | Revision 4 expectation |
|---|---:|
| Existing production files touched | 6–8 |
| Existing governance model semantics changed | 0 |
| New production package | `repository_sync` remains |
| New production files | 3–5 |
| New runtime dependencies | 0 |
| Persistent schema changes | 1 table + 1 index |
| New migrations | 1 (`v3`) |
| Repository-contract schema changes | 0 |

Revision 4 reduces coupling; it does not authorize any additional implementation surface.

Minimum Sufficient Architecture remains mandatory.

---

# 7. Revision 4 closure

F008 is resolved by making remote repository-mutation authority project/exact-subject scoped:

```text
read-only preparation
        ↓
RepositorySyncSubjectV1 + digest
        ↓
explicit HUMAN approval
        ↓
RepositoryMutationAuthorization
(project + exact subject; no BaselineId/GateId/SliceId)
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

This removes the undefined `current Slice 1.3 authority context` without weakening any remote-write constraint.

Architecture escalation is not required.

Implementation remains NOT AUTHORIZED.