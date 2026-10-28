# Relay — Dogfood 001 Canonical Reconciliation Authority 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-27  
**Record:** `RLY-S31-DOGFOOD-001-CANONICAL-RECONCILIATION-AUTH-001 — AUTHORIZED`

## 1. Human decision

The Human authorizes one bounded reconciliation of the later Dogfood 001 request/grant lineage against the current canonical Relay state.

This authority exists because the accepted runtime-boundary implementation is now canonical, while the later Dogfood request/grant package was compiled against an older source snapshot and registry basis.

Reconciliation must establish current ProjectState truth before any WorkPacket materialization or execution admission.

## 2. Exact canonical base

The reconciliation branch is based exactly on:

`ca92931343241af9c9c9dbc84b2f1bc36c374503`

This is the canonical promoted runtime-boundary state.

All new reconciliation artifacts must descend from this exact canonical base.

## 3. Recovered later Dogfood lineage

Recovered local lineage reported by the operator:

```text
branch:
dogfood/3.1-execution-001-source-coverage

local head:
76c8d57f8e161c367b2db6e92caab70525077a9d
```

This lineage is distinct from the older remote preparation branch:

`dogfood/3.1-execution-001 @ f9bc416b5eae1ef483fa85bd6216afece816a245`

The `f9bc416...` lineage is historical only and must not be treated as the current attempt lineage.

The local `76c8d57...` lineage is an evidence source for reconciliation; this authority does not itself declare its historical snapshot or grant fresh.

## 4. Preserved attempt identity

The later Dogfood package preserves:

```text
intended_attempt_id:
exec-01a17935-8a1a-77cd-b015-c2d65e07496b

ExecutionId:
exec_01a17935-8a1a-77cd-b015-c2d65e07496b
```

Historical AuthorityCandidate digest:

`sha256:efe735e084d504aa815a3b763bda041c303703cc8e71f7dfa0b692d9dde9bbbe`

These values are historical evidence and comparison anchors. They do not establish current freshness.

## 5. Authorized reconciliation work

The worker may:

1. inspect the recovered local Dogfood lineage read-only;
2. copy into the reconciliation lineage only immutable request, recovery, Human-decision/grant, and provenance records required to reconstruct the later attempt;
3. preserve copied historical records byte-for-byte unless a new reconciliation record explicitly references them;
4. rebuild source coverage against canonical `ca929313...`;
5. compute a new exact source-coverage digest;
6. build the current ProjectState snapshot from canonical repository state, accepted operational Slice identity, current registry/canonical projections, and current source basis;
7. run the accepted Slice 2.5 resolver/compiler using the preserved Dogfood request semantics;
8. record exact CompilationStatus;
9. if `READY`, record the new AuthorityCandidate canonical JSON and content digest;
10. record the exact current consumption requirements;
11. compare the fresh candidate digest with historical `sha256:efe735...`;
12. explain every material delta attributable to canonical/runtime-boundary/source-state changes;
13. update only reconciliation/governance records and registry entries needed to preserve this evidence;
14. run deterministic repository/registry/digest validation.

## 6. Freshness and grant rule

The historical grant must not be rebound, rewritten, refreshed, or silently carried forward.

If the fresh compilation yields:

```text
new_candidate_digest !=
sha256:efe735e084d504aa815a3b763bda041c303703cc8e71f7dfa0b692d9dde9bbbe
```

then the existing execution authority is stale for admission and a **new exact Human execution authority is required**.

If the fresh candidate digest is unchanged, the historical grant is still not automatically usable. Its exact applicability, source basis, snapshot basis, reservations, and freshness must be revalidated explicitly before any later WorkPacket materialization.

Equality is evidence of candidate stability, not execution authority.

## 7. Operational Slice basis

The reconciliation must use the accepted materialized Slice 3.1 identity:

```text
slice_id:
slc_01a17b3e-1a64-7614-92d0-b2d6f79664b3

definition_revision:
1

definition_digest:
sha256:1659a313cf123983b8a003d2804141ddeca69e4b83f96c272e96030a9cebf8be
```

Do not infer or recreate a different operational Slice identity.

## 8. Runtime-boundary basis

Current canonical state includes:

- Human-accepted Runtime Boundary Candidate 003;
- Human-accepted corrected implementation `e3b48c9c883d8e2983bbbca3e21f2bc0185f4a46`;
- M001–M003 CLOSED;
- I001–I003 CLOSED.

The reconciliation must include these current facts where applicable to ProjectState/source coverage.

It must not claim that a concrete enforcing backend is qualified merely because the contract implementation is accepted.

## 9. Explicit non-authority

This authority does **not** permit:

- WorkPacket materialization;
- ContextManifest materialization for execution;
- WorkspacePlan resolution for Dogfood execution;
- workspace provisioning;
- concrete backend qualification;
- fixture execution;
- OpenCode launch;
- runtime session creation;
- permission attestation from a live runtime;
- credential reads;
- provider/model calls;
- prompt admission;
- reservation consumption;
- grant mutation or rebinding;
- Dogfood admission or consumption;
- canonical promotion;
- mutation or revival of the stale `f9bc416...` preparation branch;
- source/test/runtime implementation changes unrelated to deterministic reconciliation mechanics.

Dogfood 001 remains:

`AUTHORIZED / NOT ADMITTED / NOT CONSUMED`

## 10. Required successful terminal

Use:

`DOGFOOD_001_CANONICAL_RECONCILIATION_CANDIDATE_COMPLETE`

and classify the fresh result as exactly one of:

```text
READY / CANDIDATE_UNCHANGED
READY / CANDIDATE_CHANGED_NEW_AUTHORITY_REQUIRED
NOT_READY / <exact fail-closed reason>
INDETERMINATE / <exact missing provenance>
```

The reconciliation candidate must state the exact fresh snapshot digest, source-coverage digest, CompilationStatus, AuthorityCandidate digest if present, consumable requirements, and historical-vs-current comparison.

## 11. Continuation

On `DOGFOOD_001_CANONICAL_RECONCILIATION_CANDIDATE_COMPLETE`, proceed directly to independent reconciliation review.

Do not materialize a WorkPacket or attempt admission as part of this authority.

**Disposition:** `AUTHORIZED`
