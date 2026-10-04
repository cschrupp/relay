# Project and Slice Definition Administration

**Status:** IMPLEMENTED / ACCEPTED / CLOSED
**Authority:** `RLY-S14-AUTH-001`
**Accepted design:** Slice 1.4 Revision 2, `f5a678da360b96701a1f9635d3703b49dc16e779`

## Boundary

`relay_engine.project_slice` is the only post-v4 runtime path for creating or
editing current Project and Slice definitions. It wraps the existing immutable
domain values in definition snapshots and persists human mutation provenance.
Lifecycle, gate, authorization, evaluation, execution, Baseline, repository,
provider, and board behavior remain owned by their existing subsystems.

Project identity and primary repository are immutable. Slice identity and
Project ownership are immutable. Project name and the accepted Slice definition
fields are the only mutable values.

## Persistence

SQLite migration v4 adds `definition_revision` to current `projects` and
`slices`, then creates `project_definition_revisions` and
`slice_definition_revisions`. History stores canonical typed JSON, operation,
revision, and human actor/time/reason for runtime mutations. Migration v4 writes
revision-1 `SEED` records for pre-v4 current values. Database triggers reject
history updates and deletes. History rows have no foreign key to current rows,
so guarded physical deletion leaves tombstones and permanently reserves IDs.

All definition mutations use the existing `BEGIN IMMEDIATE` transaction.
Updates require an exact current revision before checking target equality; a
stale exact target is a conflict. A matching-revision exact target is a no-op.
No command ID or hidden retry mechanism exists.

## Slice validation and deletion

Creation and material updates validate the current same-Project parent and
dependency graphs in the write transaction. Parent and dependency cycles are
rejected. An existing lifecycle row/event, gate revision, or downstream current
dependency freezes the Slice definition. Delete explicitly checks the accepted
current-schema authority references, appends a DELETE revision, then removes
only the current row in the same transaction. Residual integrity failures roll
back both changes.

## Public service

The public service exposes Project and Slice create/get/list/update/delete,
exact revision reads, immutable snapshots/results, and typed failures. Raw
`insert_project` and `insert_slice` persistence entry points are no longer
exported or implemented. Existing `load_project` / `load_slice` remain
low-level reads for accepted integrations.

## Deliberate exclusions

This implementation adds no lifecycle schema fields, governance behavior,
dependency invalidation, repository or GitHub mutation, `.relay/` synchronization,
UI, Slice 1.5 behavior, or agent execution.

## Evaluation state

```text
Slice 1.4 implementation: COMPLETE / ACCEPTED / CLOSED
Independent implementation evaluation: RLY-S14-EVAL-002 — ACCEPT
Human technical acceptance: RLY-S14-ACCEPT-001 — ACCEPTED
Independent closure evaluation: RLY-S14-CLOSE-EVAL-001 — ACCEPT
Canonical closure commit: e44d63c15b7a4941146db5ad42bfcd414b71b444
Slices 1.5–1.6: COMPLETE / ACCEPTED / CLOSED
```
