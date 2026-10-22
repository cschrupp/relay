# Slice 1.10 Dogfood B3 — Stage B Real Materialization — Consequential Execution Authorization

**Document class:** Immutable Human consequential execution authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B3 — Forward Re-baseline / First Governed Work  
**Stage:** B — real operational materialization  
**Record:** `RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly accepts Stage A tooling and authorizes one consequential Stage B materialization attempt for the real adopted Relay operational database.

This authority is narrow and one-shot. It authorizes no other Project/Slice mutation and no retry after the accepted coordinator is invoked.

## Accepted tooling basis

```text
Stage A implementation authority:
RLY-S110-DOGFOOD-B3-STAGEA-IMPL-AUTH-001 — AUTHORIZED

Accepted Stage A tooling candidate:
042a4a54df7eecadfefa30f1e5c487da52c38b61

Independent Stage A evaluation:
RLY-S110-DOGFOOD-B3-STAGEA-IMPL-EVAL-001 — ACCEPT

Human Stage A acceptance:
RLY-S110-DOGFOOD-B3-STAGEA-IMPL-ACCEPT-001 — ACCEPTED

Stage A accepted-governance tip:
67ec0c54a110ed27cef160a1af4b3cda81b5a159
```

The execution checkout MUST use the exact accepted tooling SHA
`042a4a54df7eecadfefa30f1e5c487da52c38b61`.
The descendant governance commits that record acceptance and this authority
must not be pulled into the execution checkout before materialization.

## Exact operational subject

```text
Operational database:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Authorized pre-state database SHA-256:
54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9

Canonical B2 terminal evidence:
/home/user/projects/relay-local-state/adoption-evidence/b2-adoption-terminal-evidence.json

Canonical B2 terminal evidence SHA-256:
89928fdfadbca85fafe549e8b496c7cb97192740dd2b28b6ea583d87c08bbe5c

ProjectId:
prj_018f47c1-7b2c-7abc-8def-123456789001

RepositoryId:
repo_018f47c1-7b2c-7abc-8def-123456789002

Adopted BaselineId:
base_01a15754-1123-7535-9ded-6a5578cebb50

AdoptionId:
adopt_01a15754-1123-7535-9ded-6a57d1dcc465

Adoption-frontier SliceId:
slc_01a15754-1123-7535-9ded-6a564518e347

Expected current Slice definition revision:
1

Expected lifecycle:
ABSENT — no lifecycle_current row and no lifecycle_events

Expected handover history:
ABSENT — no handover_gate_revisions for the Slice

Project operational epoch:
ohe_01a15754-1123-7535-9ded-6a587338a7b1

Project PRE_GENESIS origin record:
oor_01a15759-f0ff-765d-a7b4-82cbd2f4358f

Slice NATIVE_RELAY origin record:
oor_01a15759-f100-7051-9dde-ce7dad8b867a

Human ActorRef:
act_01a15759-f08f-75d3-a5b2-2363eaf71e4c

Human display name:
interactive Human root authority
```

The exact origin proof payloads/digests are those bound by the canonical B2
terminal-evidence artifact above. Stage B preflight must compare the current
database's exact origin records/proofs/digests to that pinned evidence; record
identity alone is insufficient.

## Exact target

The target is exactly `B3_TARGET_SLICE` from accepted tooling SHA
`042a4a54df7eecadfefa30f1e5c487da52c38b61`, which is byte/semantic-equivalent
to the exact canonical Slice JSON frozen in accepted B3 design candidate
`b032b0f28e1b476097b99b375be647cfe5ada64d`.

No field may be supplied dynamically except the already-frozen target object
loaded from that accepted tooling.

The materialized result must be:

```text
same ProjectId
same SliceId
definition revision: 1 -> 2
title: Slice 2.2 — Role Contracts
parent_slice_id: null
dependency_ids: []

lifecycle:
phase = PROPOSED
revision = 0
exactly one LifecycleInitialized event
```

T1, adopted Baseline, adoption record, operational epoch, and operational
origin records remain unchanged.

## Human mutation provenance

Use exactly:

```text
actor:
act_01a15759-f08f-75d3-a5b2-2363eaf71e4c
HUMAN
interactive Human root authority

reason:
RLY-S110-DOGFOOD-B3-STAGEB-MATERIALIZATION-AUTH-001 — materialize accepted B3 forward re-baseline and initialize the first governed work at PROPOSED
```

`occurred_at` must be the actual timezone-aware UTC execution time immediately
before constructing the materialization plan.

The lifecycle event ID must be one freshly allocated Relay `evt_` UUIDv7 for
this one attempt. It is not permission for any additional event or retry.

## Read-only preflight — mandatory before any writable open

Preflight may be repeated read-only if needed to collect evidence. It does not
consume the one consequential attempt.

Preflight MUST:

1. verify the execution repository is exactly the intended Relay repository;
2. verify the execution checkout is exactly
   `042a4a54df7eecadfefa30f1e5c487da52c38b61`;
3. verify the execution worktree is clean;
4. SHA-256 the live operational DB and require exact equality to
   `54618a6a6be5eff5a022a1e38e29b17076677b3a9b92e8e4df27a41f319242e9`;
5. SHA-256 the B2 terminal evidence and require exact equality to
   `89928fdfadbca85fafe549e8b496c7cb97192740dd2b28b6ea583d87c08bbe5c`;
6. open the operational DB through a SQLite URI with `mode=ro`; do not use
   Relay `open_database` for preflight because its journal-mode setup is not a
   purely read-only operation;
7. verify SQLite integrity and zero foreign-key errors read-only;
8. verify schema migration state is the accepted Relay migration-8 state;
9. verify exact Project, Repository, Baseline, Adoption, Slice, epoch, and
   origin identities;
10. verify the current Slice definition is exactly the accepted B2
    adoption-frontier value and revision 1;
11. verify lifecycle current/history are absent;
12. verify handover-gate history is absent;
13. verify Project and Slice origins are established and exact proof/digest data
    match the pinned terminal-evidence artifact;
14. verify no unexpected successor/current work record exists that would make
    this B3 materialization stale or ambiguous;
15. verify the exact target loaded from the accepted tooling validates against
    the accepted `Slice` model.

Any mismatch is a HARD STOP before any writable database open.

Do not repair, migrate, normalize, checkpoint, vacuum, or modify the DB during
preflight.

## One permitted consequential attempt

Only after all preflight checks PASS may the operator open the exact database
through accepted tooling with `apply_migrations=False` and call
`materialize_b3` exactly once.

The exact plan is:

```text
target:
B3_TARGET_SLICE

expected_definition_revision:
1

mutation.actor:
exact Human ActorRef above

mutation.occurred_at:
actual UTC execution instant

mutation.reason:
exact authority reason above

event_id:
one newly allocated evt_ UUIDv7
```

No alternate DB path, ProjectId, SliceId, target payload, revision, actor, or
reason is authorized.

No `failure_hook` is permitted for the real transaction.

Once `materialize_b3()` is invoked, this authority's consequential attempt is
consumed whether it commits or rolls back. Do not retry automatically. Any
exception/failure after invocation requires terminal evidence and a fresh Human
authority before another real attempt.

## Required post-transaction verification

After a successful commit:

1. close the writable Relay connection;
2. compute the new operational DB SHA-256;
3. verify SQLite `integrity_check = ok`;
4. verify zero foreign-key errors;
5. verify Slice definition revision = 2 and exact target payload equality;
6. verify definition revision history contains the original CREATE revision and
   exactly one Human-attributed UPDATE revision;
7. verify lifecycle current = revision 0 / PROPOSED;
8. verify exactly one `LifecycleInitialized` event for the Slice and replay
   equality;
9. verify Project/Slice origin records and proof/digests are unchanged;
10. verify T1 adoption record, Baseline, Project, Repository, epoch, and all
    unrelated records are unchanged;
11. render the existing Project board/read model and verify the retained Slice
    is the current proposed first governed work;
12. verify no B4, Slice 2.2 design/implementation, execution, evaluation, or
    promotion record was created by Stage B;
13. verify no stray SQLite staging/backup/sidecar files were created by the
    operator beyond SQLite's normal transient handling; close/checkpoint only
    if the accepted database path already does so safely and without additional
    semantic writes. Do not perform cleanup writes merely to improve evidence.

## Required terminal evidence

Write evidence outside the repository and outside the operational DB, preferably:

`/home/user/projects/relay-local-state/adoption-evidence/b3-stageb-materialization-evidence.json`

The evidence must include at least:

- authority identity;
- exact execution SHA;
- exact command/operator-script digest if a script file is used;
- preflight DB SHA;
- terminal-evidence SHA;
- every preflight result;
- exact Project/Slice/adoption/baseline/epoch/origin identities;
- exact origin proof/digest comparison result;
- actual `occurred_at`;
- Human ActorRef;
- generated event ID;
- exact target payload digest/value;
- transaction outcome;
- before/after Slice revisions;
- lifecycle event/current snapshot;
- board/read-model result;
- before/after DB SHA;
- integrity/FK results;
- proof unrelated records were unchanged;
- proof no downstream B4/2.2 execution occurred.

Compute and return SHA-256 of the evidence artifact.

## Explicitly not authorized

This authority does NOT permit:

- a second `materialize_b3` invocation;
- any retry after transaction invocation;
- schema migrations;
- target-payload edits;
- creation of another Slice;
- lifecycle transition beyond initial `PROPOSED`;
- B4 execution;
- Slice 2.2 design opening;
- Role Contracts implementation;
- `PROPOSED_WORK` / `BACKLOG_EXHAUSTED` runtime implementation;
- Slice 2.3 / 2.4;
- OpenCode/AgentRuntime project execution;
- Phase 3;
- repository source modification during execution;
- promotion.

## Stop condition

After the one attempt, return terminal evidence and STOP for independent Stage B
result review.

Do not self-accept the materialization.
Do not open B4.
Do not open Slice 2.2 design.
