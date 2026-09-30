# Slice 1.4 — Project and Slice CRUD

**Status:** DESIGN REVISION 1 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design record  
**Human version:** Revision 1  
**Project:** Relay  
**Slice:** 1.4  
**Design authority:** `RLY-S14-DESIGN-AUTH-001`  
**Authorized baseline:** `1eaece23e31d831bfd2b27e55a898df389cc45fc`  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-09-29

---

# 1. Objective

Provide the minimum safe human-controlled service contract for creating, reading,
editing, listing, and deleting Relay `Project` and `Slice` definitions while preserving
the accepted domain, lifecycle, governance, repository-authority, and audit contracts.

The accepted roadmap intent is that humans can manually create a complete slice,
edit its definition, set dependencies, scope/out-of-scope, and acceptance criteria,
while invalid edits are rejected.

This slice does **not** turn Project/Slice CRUD into an alternate lifecycle engine.

---

# 2. Accepted constraints

The design starts from the following accepted facts:

1. `Project` is an immutable domain value containing `id`, `name`, and one
   `primary_repository`.
2. `Slice` is an immutable domain value containing `id`, `project_id`, `title`,
   `scope`, `acceptance_criteria`, optional `parent_slice_id`, and
   `dependency_ids`.
3. `Slice` intentionally has **no workflow state**.
4. Lifecycle phase, validity, blockage, cancellation, and supersession belong to
   `SliceLifecycle`.
5. Handover gates, authorizations, decisions, evaluations, and executions are
   immutable governance evidence.
6. `Project.primary_repository` is already durable repository authority for
   Slices 1.1–1.3.
7. SQLite already stores current Project/Slice values and downstream foreign-key
   references.
8. Relay requires historical auditability and optimistic concurrency around
   mutable state.

Therefore Slice 1.4 owns **definition administration**, not lifecycle or
authorization transitions.

---

# 3. Design decisions

## S14-D01 — Preserve accepted Project and Slice domain values

The accepted `Project` and `Slice` schemas remain unchanged.

Slice 1.4 adds service/persistence records around those immutable values rather
than adding workflow status, database revision fields, archival flags, or
provider-specific data to the domain values themselves.

## S14-D02 — Definition identity and ownership are immutable

For the lifetime of an identity:

```text
Project.id                    immutable
Project.primary_repository    immutable

Slice.id                      immutable
Slice.project_id              immutable
```

A Project repository rebind is not ordinary CRUD. It can invalidate GitHub
access, repository mutation authority, Baselines, and repository provenance, so
it requires a future separately governed migration/rebind capability.

## S14-D03 — Mutable definition fields are explicit

Project update may change:

```text
name
```

Slice update may change:

```text
title
scope
acceptance_criteria
parent_slice_id
dependency_ids
```

No CRUD operation may change lifecycle phase, validity, blockage, cancellation,
supersession, gate policy, authorization, Baseline, repository mutation
authority, or accepted evidence.

## S14-D04 — Every definition has an integer definition revision

Current Project and Slice rows expose:

```text
definition_revision >= 1
```

Creation starts at revision 1.

A material update or guarded delete advances the revision exactly once.

An exact target-state no-op does not advance the revision.

Definition revision is independent from lifecycle revision, GitHub installation
`state_revision`, gate revision, artifact revision, and repository-registry
revision.

## S14-D05 — Definition revision history is append-only

Migration v4 adds immutable revision history for Project and Slice definitions.

Conceptually:

```text
project_definition_revisions
slice_definition_revisions
```

Each revision stores:

```text
entity identity
resulting definition revision
operation
exact canonical typed payload, or null for DELETE
human actor / UTC occurrence time / nonblank reason for human mutations
```

Allowed operations:

```text
SEED
CREATE
UPDATE
DELETE
```

`SEED` is reserved for migration/bootstrap compatibility. Human CRUD uses only
CREATE / UPDATE / DELETE.

Revision rows have no foreign key back to the current-row table so deletion of
an unused current entity cannot erase its historical definition revisions.

An identity with any revision history is permanently reserved and cannot be
reused after deletion.

## S14-D06 — Migration v4 is the minimum persistence evolution

Migration v4:

1. adds `definition_revision INTEGER NOT NULL DEFAULT 1 CHECK (...)` to
   `projects`;
2. adds the same column to `slices`;
3. creates the two append-only revision tables;
4. deterministically seeds revision 1 for all pre-existing Project/Slice rows
   with operation `SEED`;
5. adds only indexes required for deterministic entity/revision lookup.

No new runtime dependency, queue, worker, event bus, cache, or generic CRUD
framework is introduced.

## S14-D07 — Existing insert/load functions remain persistence primitives

Existing `insert_project`, `load_project`, `insert_slice`, and `load_slice`
remain low-level persistence primitives for accepted internals and fixtures.

After migration v4, raw inserts establish revision 1 and a `SEED` revision
record.

Human/product mutation must use the Slice 1.4 administration service. Raw
persistence primitives do not constitute product authorization.

## S14-D08 — Service snapshots expose value + exact revision

Read operations return a typed snapshot:

```text
ProjectDefinitionSnapshot
    value: Project
    definition_revision: int

SliceDefinitionSnapshot
    value: Slice
    definition_revision: int
```

Current-row absence returns `None` for direct persistence loads and a typed
`...NotFound` failure at the administration service boundary.

History reads may retrieve an exact `(entity_id, revision)` for audit/testing,
including a DELETE tombstone.

## S14-D09 — Create uses the caller-supplied Relay identity

Creation accepts a complete validated immutable `Project` or `Slice` value plus
human mutation metadata.

The supplied Relay ID is the idempotency identity.

Create behavior:

```text
no current row + no history
    -> create revision 1

current row at revision 1 + exact same value
    -> no-op success

same ID with any different current value
    -> AlreadyExists

no current row + prior history/tombstone
    -> IdentifierRetired
```

The service does not silently generate a second identity on retry.

## S14-D10 — Project creation does not provision GitHub or initialize `.relay`

Project creation records the accepted provider-neutral `RepositoryRef`.

It does not:

- install or authorize a GitHub App;
- resolve a provider repository;
- create a Baseline;
- initialize or synchronize `.relay/`;
- mint repository tokens.

Those remain owned by Slices 1.1–1.3.

## S14-D11 — Slice creation validates the complete structural graph

Before visibility, Slice creation proves:

- owning Project exists;
- parent, if present, exists and belongs to the same Project;
- every dependency exists and belongs to the same Project;
- parent links remain acyclic;
- dependency links remain acyclic;
- accepted local `Slice` invariants hold.

Validation and write happen in one SQLite write transaction.

## S14-D12 — Reads and lists are deterministic

Required read surface:

```text
get_project(project_id)
list_projects()

get_slice(slice_id)
list_slices(project_id)
```

Lists contain only current, non-deleted rows and are ordered by typed Relay ID
text, not insertion order or modification time.

`list_slices(project_id)` fails if the Project does not currently exist.

## S14-D13 — Updates use optimistic compare-and-swap

Update requests include:

```text
expected_definition_revision
target immutable Project/Slice value
human mutation metadata
```

Algorithm:

1. load exact current row inside `BEGIN IMMEDIATE`;
2. validate identity/ownership immutability;
3. if target value exactly equals current value, return current snapshot with
   `changed=false` even when the supplied expected revision is stale;
4. otherwise require expected revision == current revision;
5. validate all mutation-specific invariants;
6. append revision N+1;
7. update current row with `WHERE definition_revision = N`;
8. require exactly one updated row;
9. return revision N+1 with `changed=true`.

This gives target-state idempotency without hidden retry.

## S14-D14 — Project repository authority cannot be changed by update

A target Project whose `primary_repository` differs from current fails with a
typed `ProjectRepositoryImmutable` error before mutation.

Project name may change regardless of downstream use because it is descriptive
metadata and does not alter repository, Baseline, or governance identity.

## S14-D15 — Slice definitions have a bounded editable window

A Slice definition may change only while it is still structurally being defined.

Update is allowed only when all are true:

1. no immutable handover-gate revision exists for the Slice; and
2. lifecycle is absent, or its complete history has never left
   `{PROPOSED, DEFINING}`.

Once the Slice has ever entered any later lifecycle phase, its definition is
permanently frozen under Slice 1.4.

This deliberately avoids building dependency invalidation/staleness machinery
before its later roadmap phase.

## S14-D16 — Downstream dependency use conservatively freezes the depended-on Slice

If any other current Slice names the target Slice in `dependency_ids`, the
target Slice definition is not editable through Slice 1.4.

Without dependency invalidation, silently changing a definition already consumed
by downstream work would make that downstream meaning ambiguous.

A future invalidation/staleness capability may relax this rule explicitly.

## S14-D17 — Parent and dependency graphs are checked from current authoritative definitions

Because parent/dependency relationships are presently part of the typed Slice
payload rather than normalized relational tables, Slice 1.4 scans current Slice
definitions for the owning Project inside the same write transaction.

For the M0 human workflow this is simpler and safer than introducing duplicate
edge tables.

No relation cache or denormalized graph index is added in this slice.

## S14-D18 — Delete means guarded physical removal of only an unused current entity

Slice 1.4 does **not** erase governed history.

Project delete is permitted only when the Project has no current:

- Slice;
- Baseline;
- GitHub installation;
- repository mutation authorization;
- other accepted durable reference that would violate a foreign-key or
  authority invariant.

Slice delete is permitted only when it has no:

- lifecycle current/history;
- handover-gate revision;
- gate evaluation or execution;
- child Slice using it as parent;
- other current Slice using it as a dependency.

The service appends a DELETE tombstone at revision N+1 before deleting the
current row in the same transaction.

No cascade delete is used.

## S14-D19 — Deleting governed work is a lifecycle operation, not CRUD

A Slice that has entered governed lifecycle work cannot be deleted.

Humans use the existing lifecycle/governance semantics for:

```text
BLOCKED / CLEAR
CANCELLED
SUPERSEDED
```

Slice 1.4 does not duplicate those semantics.

This explicitly supersedes the older roadmap wording that grouped
block/unblock/cancel/supersede under CRUD.

## S14-D20 — Delete retries are target-state idempotent

Delete request includes `expected_definition_revision`.

Behavior:

```text
current row exists
    -> expected revision required, guards checked, DELETE revision appended

current row absent + latest history is DELETE
    -> no-op success, already_deleted=true

current row absent + no history
    -> NotFound
```

A deleted ID cannot be recreated.

## S14-D21 — Artifact attachment is not a Slice-definition field

The old roadmap mentioned “attach artifacts.” The accepted Slice model does not
own artifact attachments.

Artifacts remain attached to engineering authority through accepted Artifact,
Baseline, HandoverGate, Evidence, and repository-registry contracts.

Slice 1.4 does not add `artifact_ids` to `Slice` or create a second attachment
authority.

## S14-D22 — Human mutation metadata is mandatory at the service boundary

Human CREATE / UPDATE / DELETE commands require:

```text
actor: ActorRef(kind=HUMAN)
occurred_at: aware UTC datetime
reason: nonblank string
```

The revision history preserves these facts.

This is action provenance, not authorization to advance lifecycle or governance.

## S14-D23 — Typed failures distinguish invalid intent from concurrency

Required service failures include at minimum:

```text
ProjectNotFound
SliceNotFound
ProjectAlreadyExists
SliceAlreadyExists
ProjectIdentifierRetired
SliceIdentifierRetired
DefinitionRevisionConflict
ProjectRepositoryImmutable
CrossProjectSliceReference
SliceParentCycle
SliceDependencyCycle
SliceDefinitionFrozen
SliceHasDownstreamDependents
ProjectDeleteForbidden
SliceDeleteForbidden
```

Persistence corruption continues to use accepted persistence-integrity failures.

## S14-D24 — No hidden mutation or repair

CRUD never:

- rewrites lifecycle events;
- invalidates or rewrites gates/authorizations automatically;
- modifies Baselines;
- rebinds repositories;
- deletes historical definition revisions;
- repairs inconsistent state;
- cascades deletion;
- retries stale writes internally.

Invalid or ambiguous state fails closed.

## S14-D25 — SQLite transaction semantics remain the concurrency boundary

All create/update/delete validation and mutation occurs under the accepted
`BEGIN IMMEDIATE` write transaction.

Two competing updates from the same expected revision cannot both commit.

No distributed lock or additional coordination service is required.

---

# 4. Service contract

The exact names may be adjusted during implementation for local naming
consistency, but behavior is normative.

```python
create_project(database, value, mutation) -> ProjectMutationResult
get_project(database, project_id) -> ProjectDefinitionSnapshot
list_projects(database) -> tuple[ProjectDefinitionSnapshot, ...]
update_project(database, expected_revision, target, mutation) -> ProjectMutationResult
delete_project(database, project_id, expected_revision, mutation) -> ProjectDeleteResult

create_slice(database, value, mutation) -> SliceMutationResult
get_slice(database, slice_id) -> SliceDefinitionSnapshot
list_slices(database, project_id) -> tuple[SliceDefinitionSnapshot, ...]
update_slice(database, expected_revision, target, mutation) -> SliceMutationResult
delete_slice(database, slice_id, expected_revision, mutation) -> SliceDeleteResult
```

Mutation results expose the exact resulting snapshot and whether durable state
changed.

Delete result exposes the deleted identity/revision and whether this call
performed the deletion or observed an already-deleted target state.

---

# 5. Persistence contract

## 5.1 Current tables

`projects` and `slices` remain current materialized definition state and gain
only `definition_revision`.

## 5.2 Revision tables

Revision-table payloads are strict typed records.

For non-DELETE revision rows, `payload_json` must decode to the exact Project or
Slice and match indexed identity/project columns.

For DELETE rows, `payload_json` is null and the prior identity is preserved.

Human metadata must be present for CREATE/UPDATE/DELETE and absent only where
the operation is a deterministic `SEED`.

Revision sequences are contiguous starting at 1.

## 5.3 Integrity verification

Loading current administration state verifies:

- current revision >= 1;
- latest non-delete revision equals current payload and revision;
- a current row cannot have a later DELETE tombstone;
- deleted history cannot coexist with a current row of the same identity;
- indexed identity/project columns agree with typed payload.

Malformed durable state raises `PersistenceIntegrityError`.

---

# 6. Expected implementation change surface

Minimum expected production surface:

```text
src/relay_engine/project_slice/
    __init__.py
    errors.py
    models.py
    service.py

src/relay_engine/persistence/
    migrations.py
    store.py
    __init__.py
```

Expected tests:

```text
tests/unit/test_project_slice_service.py
tests/integration/test_persistence_sqlite.py
tests/unit/test_persistence_models.py   # only if typed revision records live there
```

Possible existing export files may change if required by normal package
exposure.

Expected migration:

```text
SQLite schema migration v4
```

Expected new runtime dependencies:

```text
NONE
```

Not expected:

- provider/GitHub production changes;
- repository-sync production changes;
- lifecycle transition changes;
- governance engine changes;
- UI/board code;
- worker/queue code;
- generic repository framework;
- agent execution.

Material deviation from this surface requires evaluation/escalation.

---

# 7. Acceptance criteria

## Project CRUD

- **A01** Project create persists exact validated value at definition revision 1.
- **A02** Exact revision-1 create retry is a no-op success.
- **A03** Same ProjectId with different current value is rejected.
- **A04** Deleted/retired ProjectId cannot be reused.
- **A05** Get returns exact current value + revision.
- **A06** Project list is deterministic by ProjectId.
- **A07** Project update can change name.
- **A08** Project update cannot change id.
- **A09** Project update cannot change primary_repository.
- **A10** Material Project update increments revision exactly once.
- **A11** Exact target Project update is a no-op without revision increment.
- **A12** Stale material Project update fails.
- **A13** Unused Project delete appends tombstone and removes current row atomically.
- **A14** Project delete is blocked by any current Slice.
- **A15** Project delete is blocked by Baseline authority.
- **A16** Project delete is blocked by GitHub integration state.
- **A17** Project delete is blocked by repository mutation authorization.
- **A18** Delete retry against a tombstone is a no-op success.
- **A19** Delete of never-known ProjectId returns NotFound.
- **A20** No Project delete cascades accepted history.

## Slice CRUD

- **A21** Slice create persists exact value at definition revision 1.
- **A22** Slice create requires an existing owning Project.
- **A23** Parent target must exist in same Project.
- **A24** Dependencies must exist in same Project.
- **A25** Parent cycles are rejected.
- **A26** Dependency cycles are rejected.
- **A27** Exact revision-1 Slice create retry is a no-op.
- **A28** Same SliceId with different current value is rejected.
- **A29** Deleted/retired SliceId cannot be reused.
- **A30** Slice get returns value + revision.
- **A31** Slice list is scoped to an existing Project and deterministic by SliceId.
- **A32** Slice update cannot change id.
- **A33** Slice update cannot change project_id.
- **A34** Slice update can change title, scope, acceptance criteria, parent, dependencies.
- **A35** Material Slice update increments revision exactly once.
- **A36** Exact target Slice update is a no-op without revision increment.
- **A37** Stale material Slice update fails.
- **A38** Slice update is allowed with no lifecycle when structural checks pass.
- **A39** Slice update is allowed while lifecycle history has remained only PROPOSED/DEFINING and no gate exists.
- **A40** Slice update is permanently frozen after lifecycle ever leaves PROPOSED/DEFINING.
- **A41** Any handover-gate revision freezes Slice definition.
- **A42** Any incoming dependency from another current Slice freezes target Slice definition.
- **A43** Slice update never changes lifecycle state.
- **A44** Draft/unused Slice delete appends tombstone and removes current row atomically.
- **A45** Slice delete is blocked by lifecycle current/history.
- **A46** Slice delete is blocked by gate/evaluation/execution history.
- **A47** Slice delete is blocked by child-parent reference.
- **A48** Slice delete is blocked by incoming dependency reference.
- **A49** Delete retry against Slice tombstone is a no-op.
- **A50** Delete of never-known SliceId returns NotFound.
- **A51** No Slice delete cascades accepted history.

## Persistence / audit / concurrency

- **A52** Migration v4 is deterministic and checksummed.
- **A53** Existing Project/Slice rows migrate to definition revision 1.
- **A54** Existing rows receive deterministic SEED revision history.
- **A55** Human CREATE/UPDATE/DELETE revisions require HUMAN actor, UTC time, and reason.
- **A56** Definition revision histories are append-only and contiguous.
- **A57** Current payload/revision must agree with latest non-delete history.
- **A58** Tombstoned identity cannot coexist with a current row.
- **A59** Two competing material updates from one revision cannot both commit.
- **A60** Full mutation validation and durable write occur in one SQLite transaction.
- **A61** No hidden retry or repair occurs.
- **A62** Existing migration-prefix/checksum protections remain intact.
- **A63** Existing 490-test baseline remains green or increases with new tests.
- **A64** Ruff format/lint, Pyright, pytest, and build all pass.
- **A65** No new runtime dependency is added.

## Authority boundaries

- **A66** CRUD cannot mutate blockage.
- **A67** CRUD cannot cancel a governed Slice.
- **A68** CRUD cannot supersede a governed Slice.
- **A69** CRUD cannot create/modify HandoverGate or AuthorizationGrant.
- **A70** CRUD cannot create/modify Baseline authority.
- **A71** CRUD cannot mutate `.relay/` or GitHub.
- **A72** CRUD does not implement artifact attachment outside accepted Artifact/Baseline/gate contracts.
- **A73** Slice 1.5 board work is absent.
- **A74** Agent execution remains absent.

---

# 8. Required tests

At minimum the implementation test set must cover:

- create/get/list/update/delete happy paths for Project and Slice;
- exact-create and exact-target idempotency;
- stale revision races using two SQLite connections;
- repository immutability;
- project ownership immutability;
- cross-project parent/dependency rejection;
- parent cycle and dependency cycle creation/update;
- lifecycle absent / early / later history update boundary;
- gate-created freeze;
- incoming-dependency freeze;
- every guarded-delete blocker;
- tombstone retry and permanent identity reservation;
- migration v3 -> v4 on a populated database;
- migration checksum/prefix failure behavior;
- persisted revision payload/index mismatch corruption;
- concurrent update/delete conflicts;
- proof that CRUD leaves lifecycle/gates/authorization/Baselines unchanged.

---

# 9. Explicit out of scope

- Project primary-repository rebind/migration.
- Artifact attachment model redesign.
- Lifecycle block/unblock/cancel/supersede implementation.
- Dependency invalidation/staleness propagation.
- Board/UI/API transport layer.
- Multi-user authorization/ACLs.
- GitHub/provider mutation.
- `.relay/` synchronization.
- Background workers.
- Agent/model execution.
- Slice 1.5 or later-phase implementation.

---

# 10. Review questions

The independent reviewer should specifically challenge:

1. whether definition revision history is the minimum sufficient mechanism for
   human-editable durable definitions;
2. whether early Slice editability and permanent freeze boundaries prevent stale
   governance without prematurely implementing dependency invalidation;
3. whether guarded physical delete plus tombstone preserves Relay history;
4. whether Project repository immutability correctly preserves Slices 1.1–1.3
   authority;
5. whether graph scans are simpler and safer than normalized relation tables at
   M0 scale;
6. whether any acceptance criterion accidentally authorizes lifecycle,
   governance, board, provider, or agent work.

---

# 11. Authorization boundary

```text
Slice 1.4:
OPEN

Design authority:
RLY-S14-DESIGN-AUTH-001

Design Revision 1:
SUBMITTED FOR INDEPENDENT REVIEW

Implementation:
NOT AUTHORIZED

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

An independent design-review ACCEPT, if achieved, still requires separate Human
design acceptance. Human design acceptance still does not authorize
implementation.

**Unblocked ≠ authorized.**
