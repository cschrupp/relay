# Slice 1.10 Dogfood B3 — Stage B Real Materialization — Consequential Execution Authorization 002

**Document class:** Immutable Human consequential execution authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Stage:** B — real operational materialization  
**Record:** `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-002`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes one new consequential Stage B materialization attempt.

Attempt 001 remains consumed under
`RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-001` and may not be retried or reused.

This authority permits exactly one new invocation of the accepted
`materialize_b3` coordinator after all attempt-002 preflight checks pass.

## Accepted tooling and review basis

```text
B3 accepted design:
b032b0f28e1b476097b99b375be647cfe5ada64d

Stage A accepted tooling:
042a4a54df7eecadfefa30f1e5c487da52c38b61

Stage A independent evaluation:
RLY-S110-DOGFOOD-B3-STAGEA-IMPL-EVAL-001 — ACCEPT

Stage A Human acceptance:
RLY-S110-DOGFOOD-B3-STAGEA-IMPL-ACCEPT-001 — ACCEPTED

Stage B attempt-001 evaluation:
RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-EVAL-001
FAIL_CLOSED / NO MATERIALIZATION

Execution-environment qualification evaluation:
RLY-S110-DOGFOOD-B3-STAGEB-ENV-EVAL-001 — ACCEPT
```

The execution checkout MUST be exactly:

`042a4a54df7eecadfefa30f1e5c487da52c38b61`

Do not pull this authority or later governance commits into the execution checkout.

## Attempt-001 evidence pin

```text
Artifact:
/home/user/projects/relay-local-state/adoption-evidence/b3-stageb-materialization-evidence.json

SHA-256:
e8758f045756a834d7f6e6fb37641b52d6c6069e9f7bd89c3c351bcaefa28aa9
```

Attempt 002 preflight must verify this failed-attempt evidence artifact remains unchanged.

## Execution-environment qualification pin

```text
Artifact:
/home/user/projects/relay-local-state/adoption-evidence/b3-stageb-execution-environment-qualification.json

SHA-256:
4c174dcda1045655bbdce369d784060132b6aac766c10fb160144ad11fc4338e
```

The accepted qualification establishes that the approved execution venue supports:

- OS-level read/write access to the operational DB path;
- ext4 read/write filesystem semantics;
- same-directory SQLite WAL behavior;
- `BEGIN IMMEDIATE`;
- commit;
- rollback;
- integrity checking;
- cleanup without leaving sidecars beside the operational DB.

Attempt 002 must run in the same qualified execution venue.

If the operator cannot establish that it is the same venue, or if the relevant
filesystem/mount/access conditions differ, STOP before opening the real DB
writable. A fresh environment qualification is then required.

## Exact operational subject

```text
Operational database:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Required attempt-002 pre-state SHA-256:
54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9

B2 terminal evidence:
/home/user/projects/relay-local-state/adoption-evidence/b2-adoption-terminal-evidence.json

B2 terminal evidence SHA-256:
89928fdfadbca85fafe549e8b496c7cb97192740dd2b28b6ea583d87c08bbe5c

ProjectId:
prj_018f47c1-7b2c-7abc-8def-123456789001

RepositoryId:
repo_018f47c1-7b2c-7abc-8def-123456789002

BaselineId:
base_01a15754-1123-7535-9ded-6a5578cebb50

AdoptionId:
adopt_01a15754-1123-7535-9ded-6a57d1dcc465

SliceId:
slc_01a15754-1123-7535-9ded-6a564518e347

Expected Slice definition revision:
1

Expected lifecycle:
ABSENT

Expected lifecycle event history:
EMPTY

Expected handover history:
EMPTY

Project operational epoch:
ohe_01a15754-1123-7535-9ded-6a587338a7b1

Project PRE_GENESIS origin record:
oor_01a15759-f0ff-765d-a7b4-82cbd2f4358f

Slice NATIVE_RELAY origin record:
oor_01a15759-f100-7051-9dde-ce7dad8b867a
```

The exact origin proofs/digests must still match the canonical B2 terminal
evidence, not merely the record IDs.

## Exact Human mutation provenance

Use exactly:

```text
ActorRef:
act_01a15759-f08f-75d3-a5b2-2363eaf71e4c

kind:
HUMAN

display_name:
interactive Human root authority

reason:
RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-002 — materialize accepted B3 forward re-baseline and initialize the first governed work at PROPOSED
```

`occurred_at` must be the actual timezone-aware UTC execution instant
immediately before construction of the attempt-002 plan.

Allocate exactly one fresh Relay `evt_` UUIDv7 for attempt 002.

No event ID from attempt 001 may be reused.

## Frozen target

The target is exactly `B3_TARGET_SLICE` imported from accepted tooling SHA
`042a4a54df7eecadfefa30f1e5c487da52c38b61`.

No target field may be supplied, edited, re-derived, or paraphrased at
execution time.

Required result:

```text
same ProjectId
same SliceId

Slice definition revision:
1 -> 2

title:
Slice 2.2 — Role Contracts

parent_slice_id:
null

dependency_ids:
[]

lifecycle:
revision 0
phase PROPOSED

LifecycleInitialized:
exactly one new event from attempt 002
```

## Mandatory attempt-002 preflight

Before any writable Relay database open:

1. verify exact execution checkout SHA `042a4a54...`;
2. verify clean execution worktree;
3. verify attempt-001 evidence SHA exactly `e8758f04...`;
4. verify environment-qualification evidence SHA exactly `4c174dcd...`;
5. verify B2 terminal-evidence SHA exactly `89928fdf...`;
6. verify operational DB SHA exactly `54618a6a...`;
7. verify no SQLite sidecars are present beside the operational DB;
8. verify execution is occurring in the same qualified venue and the target path
   remains OS-level writable with the containing ext4 filesystem mounted
   read/write;
9. open the operational DB using SQLite URI `mode=ro` only for semantic
   preflight;
10. verify `integrity_check = ok` and zero foreign-key errors;
11. verify accepted Relay migration-8 schema state;
12. verify all exact Project/Repository/Baseline/Adoption/Slice/epoch/origin
    identities and origin proof/digest data;
13. verify Slice definition revision is exactly 1 and payload is exactly
    `B3_INITIAL_FRONTIER`;
14. verify lifecycle current/history remain absent;
15. verify handover history remains absent;
16. verify no unexpected current/successor/downstream operational state makes
    the planned B3 materialization stale;
17. verify `B3_TARGET_SLICE` from the accepted tooling validates exactly.

Any mismatch => HARD STOP before writable open.

The preflight may be repeated if needed and does not consume attempt 002.

Do not repair, migrate, vacuum, normalize, checkpoint, or otherwise modify the
real DB during preflight.

## One permitted consequential attempt 002

Only after every preflight check passes:

1. open the exact operational DB with accepted Relay tooling using
   `apply_migrations=False`;
2. construct exactly one `B3MaterializationPlan` with:
   - `target=B3_TARGET_SLICE`;
   - `expected_definition_revision=1`;
   - exact Human ActorRef above;
   - actual UTC `occurred_at`;
   - exact attempt-002 reason above;
   - one fresh attempt-002 `evt_` UUIDv7;
3. invoke `materialize_b3(database, plan)` exactly once;
4. do not provide `failure_hook`.

The moment `materialize_b3` is invoked, attempt 002 is consumed whether the
transaction commits or rolls back.

Do not retry automatically or manually under this authority.

Any exception after invocation => collect terminal evidence and STOP for
independent review.

## Required post-commit verification

If the transaction commits:

- close the writable Relay connection;
- compute the new DB SHA-256;
- verify `integrity_check = ok`;
- verify zero foreign-key errors;
- verify exact Slice revision 2 payload;
- verify definition history is the original CREATE plus one Human UPDATE;
- verify lifecycle current = revision 0 / PROPOSED;
- verify exactly one attempt-002 `LifecycleInitialized` event and replay
  equality;
- verify Project/Slice origin records and proof/digests are unchanged;
- verify T1, adoption, Baseline, Repository, Project, epoch, and all unrelated
  operational records are unchanged;
- render the existing Project board/read model and verify the retained Slice is
  shown as the current proposed first governed work;
- verify no B4, Slice 2.2 design/implementation, execution, evaluation, or
  promotion state was created;
- verify no unwanted SQLite sidecars remain after normal close.

## Required attempt-002 terminal evidence

Write a distinct evidence artifact:

`/home/user/projects/relay-local-state/adoption-evidence/b3-stageb-materialization-evidence-attempt-002.json`

Do not overwrite attempt-001 evidence.

Record at least:

- attempt-002 authority identity;
- exact tooling SHA;
- attempt-001 evidence SHA;
- environment-qualification evidence SHA;
- B2 terminal-evidence SHA;
- pre-state DB SHA;
- every attempt-002 preflight result;
- venue-qualification match result;
- all operational identities;
- exact origin proof/digest comparisons;
- actual `occurred_at`;
- Human ActorRef;
- new attempt-002 event ID;
- exact target payload/value and digest;
- one-shot invocation count;
- transaction outcome;
- Slice before/after revisions;
- lifecycle current/event/readback;
- board/read-model result;
- post-state DB SHA;
- integrity/FK results;
- unrelated-state equality results;
- sidecar result;
- proof no B4/2.2 execution occurred.

Compute and return SHA-256 of the attempt-002 evidence artifact.

## Explicitly not authorized

This authority does not permit:

- any second attempt-002 invocation;
- reuse of attempt 001;
- retry after invocation;
- schema migration;
- target-payload edit;
- new Slice creation;
- lifecycle transition beyond initial `PROPOSED`;
- B4;
- Slice 2.2 design opening;
- Role Contracts implementation;
- Slice 2.3 / 2.4;
- OpenCode/AgentRuntime execution;
- Phase 3;
- source-code changes;
- promotion.

## Stop condition

After the single attempt-002 invocation, return terminal evidence and STOP for
independent result review.

Do not self-accept the result.
