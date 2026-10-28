# Relay Dogfood 001 — Canonical Reconciliation Candidate 001

**Document class:** Reconciliation candidate
**Status:** CANDIDATE / INDETERMINATE — NOT AN EXECUTION AUTHORITY
**Terminal:** `DOGFOOD_001_CANONICAL_RECONCILIATION_CANDIDATE_COMPLETE`
**Authority:** `RLY-S31-DOGFOOD-001-CANONICAL-RECONCILIATION-AUTH-001 — AUTHORIZED`
**Date:** 2026-10-28

## 1. Exact lineages and preserved attempt

The reconciliation starts from canonical Relay base
`ca92931343241af9c9c9dbc84b2f1bc36c374503` and authority branch tip
`8afe4f7bb105f8d692d7645a9a558fbb2239dd5c`. The recovered Dogfood evidence
lineage is `dogfood/3.1-execution-001-source-coverage` at
`76c8d57f8e161c367b2db6e92caab70525077a9d`.

The earlier `dogfood/3.1-execution-001` lineage at `f9bc416…` was not used.
Thirteen exact request, source, role, Human-decision, grant, recovery, and
pre-admission records were copied from the recovered lineage. Their bytes and
historical registry artifact objects were verified unchanged.

The preserved request is `dogfood-001-01a17935-8a1a-77cd-b015-c2d65e07496b`
with digest
`sha256:06b5caddaafcce9322c136e3606d7afffc3d6a5ba9c0bec73e4a8b0e147344ec`.
Its attempt pair remains:

```text
intended_attempt_id: exec-01a17935-8a1a-77cd-b015-c2d65e07496b
ExecutionId:        exec_01a17935-8a1a-77cd-b015-c2d65e07496b
```

The historical Human execution authorization remains byte-identical at
`docs/reviews/SLICE_3_1_DOGFOOD_001_EXECUTION_AUTHORIZATION_001.md`. It is
not rebound or represented as fresh authority.

## 2. Current canonical source basis

The exact operational Slice identity included in the current source package is:

```text
SliceId: slc_01a17b3e-1a64-7614-92d0-b2d6f79664b3
revision: 1
content_digest: sha256:1659a313cf123983b8a003d2804141ddeca69e4b83f96c272e96030a9cebf8be
```

The source package also pins the accepted runtime-boundary design and
implementation acceptance/evaluation records, the canonical promotion
authority, and the accepted workspace-provider gap evaluation. It does not
claim that a concrete enforcing backend is qualified. Fixture/source durable
reachability remains unresolved.

The current `current-baseline` canonical pointer is artifact
`art_61c0c336-e2fc-41f4-9588-7d10cef70048`, revision 172, digest
`sha256:96c4c9b893c915f5ce28b17e2d7b62788cd04be719fc7266140a7b642e00526f`.
All five current canonical pointers are included in Snapshot 004.

## 3. Rebuilt coverage and snapshot

Coverage 004 preserves the exact Dogfood 001 outcome and scope, the prior
accepted source set, and its bounded completeness assertions. It updates the
canonical baseline identity and includes the exact current operational-Slice,
runtime-boundary, and reconciliation-authority records.

```text
Coverage 004 logical digest:
sha256:3974a5c6516ef2d26cd0b6a13f9331712751ca719b911e29499fcd6f7cfd1a9d

Coverage 004 registered file digest:
sha256:f2c6d519ea45c06125f5a835e319551d50e12f355249aa288bdb480d08ae181d

Snapshot 004 digest:
sha256:aa87e7b3f5f135cf6a870e3d6fa1d136e7b9f9cabc67c334fd533e13ba8507f4

Snapshot source commit:
7368b4c035defb5d8320df61a09bb554651c5736

Registry digest pinned by Snapshot 004:
sha256:49bcaee5df68764f3a1b5ffec8d259d56afbf67d27ec03438dd8fcb77b13112d
```

Coverage 004 is a pending candidate. It has no exact accepted owning record.
The completeness assertions are therefore not treated as accepted facts.

## 4. Actual resolver/compiler result

The committed `PROJECT_STATE_REQUEST_002.json` was deserialized through the
production `ProjectStateRequest` model. The accepted production
`resolve_project_state()` and `compile_authority()` functions were run with
Coverage 004, Snapshot 004, the exact source records, the accepted RoleContract
selection, and the previously accepted WorkPacket constraints.

```text
Resolution:                    INDETERMINATE
RoleContract applicability:    APPLICABLE
Work-contract representability: SATISFIED
AuthorityCompilation:           INDETERMINATE
AuthorityCandidate:             NOT PRODUCED
Consumption requirements:       0
```

The exact resolver reason is:

```text
SOURCE_COVERAGE_MISSING / UNKNOWN
deterministic-dependency-resolution coverage declaration lacks its exact
accepted owning record
```

The exact resolver inputs and outputs, including all 37 source references,
source metadata, role-applicability facts, compilation result, and freshness
comparison, are recorded in
`docs/reviews/SLICE_3_1_DOGFOOD_001_CANONICAL_RECONCILIATION_RESULT_001.json`.

## 5. Historical candidate and grant applicability

The historical candidate digest remains
`sha256:efe735e084d504aa815a3b763bda041c303703cc8e71f7dfa0b692d9dde9bbbe`.
The production freshness check against Snapshot 004 returns `STALE` because
the candidate is bound to a different exact source snapshot.

No new AuthorityCandidate was produced because the current compilation is not
`READY`. Therefore a new candidate digest cannot yet be compared with the
historical digest. The historical execution authorization is not usable for
admission against this snapshot. No grant was rebound, refreshed, or replaced.

The zero-consumable result is preserved: no reservation was fabricated,
created, or consumed. The attempt remains historically
`AUTHORIZED / NOT ADMITTED / NOT CONSUMED`; this record does not authorize
admission.

## 6. Explicit boundary

This reconciliation performed no WorkPacket or WorkspacePlan materialization,
workspace provisioning, backend qualification, fixture execution, OpenCode
launch/session creation, credential access, provider/model call, prompt
admission, reservation mutation, or Dogfood execution.

The concrete enforcing backend remains unqualified, and fixture/source
durable reachability remains unresolved. A future accepted Coverage 004 owner
record and a subsequent actual resolver/compiler run are required before a
new READY candidate can exist. Any resulting changed candidate requires a
new exact Human execution authority.

**Disposition:** `INDETERMINATE / exact accepted source-coverage owner missing`
