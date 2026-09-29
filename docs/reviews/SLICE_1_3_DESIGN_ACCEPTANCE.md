# Slice 1.3 — Design Acceptance

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-28  
**Project:** Relay  
**Slice:** 1.3  
**Record:** `RLY-S13-DESIGN-ACCEPT-001`

## Reviewed design

```text
Revision 1:
433910d0b2df7f0f0a3104cbe97f6df5ebba609a

Revision 2 amendment:
6070b04ca5b38bd5c4687bb0ec4799f4f782e355

Revision 3 amendment:
8e8ab70cf8c9b52d628b0b658179c1fe287c93ea

Revision 4 amendment / exact reviewed design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9

Independent combined design evaluation:
RLY-S13-DESIGN-EVAL-004 — ACCEPT
```

## Human Authority decision

```text
RLY-S13-DESIGN-ACCEPT-001
Slice 1.3 Design Revision 1 + Revision 2 + Revision 3 + Revision 4
ACCEPTED
```

The accepted design authority is bound to exact reviewed head:

```text
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
```

## Accepted design boundary

The accepted design includes the combined Slice 1.3 contract for:

- schema-v1 `.relay/registry.json` recognition, initialization, and synchronization;
- exact `RepositorySyncSubjectV1` construction;
- read-only synchronization preparation;
- explicit HUMAN `RepositoryMutationAuthorization` scoped by project plus exact mutation subject;
- deterministic SQLite migration v3 for immutable repository-mutation authority;
- GitHub Git Data single-tree / single-commit / non-force default-branch ref movement;
- provider, local-access, head-race, unregistered-path, workflow-path, and post-write verification guards;
- no automatic Baseline persistence.

All independent design-review findings F001–F008 are closed.

## Authority boundary

This record accepts the design only.

It does **not** authorize:

```text
Slice 1.3 production implementation
GitHub write-capable Relay product behavior
SQLite migration v3 implementation
GitHub App permission-policy implementation change
remote repository mutation by Relay product behavior
branch / commit / ref mutation by Relay product behavior
Slice 1.4
agent execution
```

A separate Human Authority decision is required before Slice 1.3 implementation may begin.

**Unblocked ≠ authorized.**
