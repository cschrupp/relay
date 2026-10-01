# Slice 1.4 — Implementation Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Authority decision date:** 2026-09-30  
**Durable record date:** 2026-10-01  
**Project:** Relay  
**Slice:** 1.4  
**Record:** `RLY-S14-AUTH-001`

## Accepted design authority

```text
Independent combined design evaluation:
RLY-S14-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S14-DESIGN-ACCEPT-001 — ACCEPTED

Exact accepted design head:
f5a678da360b96701a1f9635d3703b49dc16e779
```

The implementation baseline is the canonical repository state after Human design acceptance:

```text
d9d78350b9ae605c44191330047a8a697ad1b121
```

## Human Authority decision

```text
RLY-S14-AUTH-001
Slice 1.4 implementation
AUTHORIZED
```

This immutable record durably persists the Human Authority implementation decision that was already issued before implementation work began. The repository omission of this record was an orchestration bookkeeping defect. Recording it now does not broaden the original authority, does not alter the accepted design, and does not constitute technical acceptance of any implementation candidate.

## Preferred implementation role / model

```text
Role:
IMPLEMENTATION_AGENT

Preferred model:
GPT-5.6 Luna
```

If the executing model differs, the implementation result must record the preferred and executing model provenance and the deviation.

## Authorized production scope

Implementation is bounded by the complete accepted Slice 1.4 Revision 1 + Revision 2 design and may implement only the minimum mechanisms required for Project and Slice definition administration, including:

- SQLite migration v4 with deterministic migration-only `SEED` history;
- append-only Project/Slice definition revisions and guarded retired identities;
- the Slice 1.4 administration service as the sole post-v4 product/runtime creation path;
- typed create/read/list/update/delete results and failures;
- mandatory HUMAN mutation provenance;
- strict definition-revision compare-and-swap;
- same-project parent/dependency validation and cycle rejection;
- lifecycle/gate/downstream-dependency definition freezes;
- explicit Project and Slice delete blockers, DELETE tombstones, and atomic fail-closed behavior;
- integrity verification, deterministic tests, and bounded implementation documentation/registry updates.

## Required boundary

Implementation must preserve the accepted constraints:

- accepted immutable `Project` and `Slice` domain schemas remain unchanged;
- Project repository authority is immutable under Slice 1.4;
- `SEED` is migration-only and cannot be created by ordinary post-v4 runtime CRUD;
- lifecycle event/model schemas are not redesigned;
- lifecycle/governance remains authoritative for block/unblock/cancel/supersede;
- no dependency invalidation/staleness subsystem;
- no provider/GitHub or repository-sync production redesign;
- no board/UI implementation;
- no generic CRUD framework, worker, queue, event bus, or new runtime dependency;
- no Slice 1.5 work;
- no agent execution.

Material deviation, required scope expansion, or architecture contradiction must stop and return an escalation rather than silently redesigning the accepted contract.

## Evaluation boundary

A completed implementation is only a technical candidate. It must be returned to an independent evaluator with its exact result SHA, exact baseline lineage, changed-file surface, migration evidence, tests, CI, and deviations.

The implementation agent may not accept its own result, promote it as technically accepted, close Slice 1.4, open Slice 1.5, or authorize agent execution.

**Unblocked ≠ accepted.**
