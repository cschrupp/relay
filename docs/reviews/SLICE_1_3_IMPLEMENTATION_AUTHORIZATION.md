# Slice 1.3 — Implementation Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-28  
**Project:** Relay  
**Slice:** 1.3  
**Record:** `RLY-S13-AUTH-001`

## Accepted design authority

```text
Independent combined design evaluation:
RLY-S13-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S13-DESIGN-ACCEPT-001

Exact accepted design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
```

## Human Authority decision

```text
RLY-S13-AUTH-001
Slice 1.3 implementation
AUTHORIZED
```

Implementation authority is bounded by the complete accepted Slice 1.3 design chain:

```text
Revision 1:
433910d0b2df7f0f0a3104cbe97f6df5ebba609a

Revision 2:
6070b04ca5b38bd5c4687bb0ec4799f4f782e355

Revision 3:
8e8ab70cf8c9b52d628b0b658179c1fe287c93ea

Revision 4 / accepted design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
```

The implementation baseline is the canonical repository state after design acceptance:

```text
d2aa7cdcf8a309461e0c3a65c5251c7e1ffc09e7
```

## Preferred implementation role / model

```text
Role:
IMPLEMENTATION_AGENT

Preferred model:
GPT-5.6 Luna
```

If the executing model differs, the implementation result must record both preferred and executing model provenance and the deviation.

## Authorized production scope

Implementation may add only the minimum production mechanisms required by the accepted design, including:

- schema-v1 `.relay/registry.json` recognition, initialization, and synchronization;
- read-only `prepare_repository_sync(...)` and exact `RepositorySyncSubjectV1` construction;
- immutable project + exact-subject scoped `RepositoryMutationAuthorization`;
- deterministic local SQLite migration v3 and persistence for repository-mutation authority;
- GitHub permission-policy support for the accepted exact READ and WRITE profiles;
- repository-scoped READ and WRITE installation-token narrowing;
- Git Data primitives needed for blob/tree/commit/non-force default-branch-ref mutation;
- repository synchronization models/errors/service implementation;
- exact authority, identity, state_revision, default-branch, head-race, path-preservation, workflow-path, and post-write verification guards;
- deterministic idempotent `CURRENT` / no-op behavior;
- required tests and documentation/memory/registry updates inside the accepted change surface.

## Required behavioral boundary

Implementation must preserve these accepted constraints:

- `.relay/registry.json` remains schema v1;
- no migration of the repository-side contract;
- no PR workflow;
- no arbitrary branch selection or branch creation;
- no force push or ruleset bypass;
- no GitHub administration permission;
- no background workers or scheduling;
- no automatic conflict resolution / merge / rebase;
- no generic multi-provider abstraction;
- no local Git clone/worktree mechanism;
- no new runtime dependency unless architecture escalation is explicitly approved;
- no automatic Relay Baseline persistence after remote synchronization;
- no Project repository mutation outside the exact accepted synchronization subject;
- no agent execution;
- no Slice 1.4 implementation.

Any material deviation, required scope expansion, unresolved contradiction, or architecture insufficiency must stop and return an escalation rather than silently redesigning the accepted contract.

## Evaluation boundary

A completed implementation is only a technical candidate. It must be returned to an independent evaluator with exact result SHA, diff/change surface, tests, CI, migration evidence, and deviations.

The implementation agent may not accept its own result, advance Slice 1.3 to accepted, or open Slice 1.4.

**Unblocked ≠ accepted.**
