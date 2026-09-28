# Slice 1.2 — Design Acceptance and Implementation Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-28  
**Project:** Relay  
**Slice:** 1.2

## Reviewed design

```text
Revision 1:
8d94e7408e4f24bf87e32dfc73273fd42f27a9da

Revision 2 amendment:
8667b3e8a20e317fb3c5ccc66278e1a14aebdafd

Revision 3 amendment:
4acd6be1f93058d1efcafc66a78fc1a9726c16ba

Independent design evaluation:
RLY-S12-DESIGN-EVAL-003 — ACCEPT
```

## Human Authority decisions

```text
RLY-S12-DESIGN-ACCEPT-001
Slice 1.2 Design Revision 1 + Revision 2 + Revision 3
ACCEPTED
```

and separately:

```text
RLY-S12-AUTH-001
Slice 1.2 implementation
AUTHORIZED
```

Implementation authority is against exact accepted design head:

```text
4acd6be1f93058d1efcafc66a78fc1a9726c16ba
```

## Model assignment

```text
Preferred implementation model:
GPT-5.6 Luna

Executing implementation model:
GPT-5.6 Sol

Deviation:
preferred bounded implementation model unavailable in the active session;
execution provenance must remain visible in the implementation result.
```

## Boundary

This authority permits implementation of Slice 1.2 only.

It does not authorize:

```text
Slice 1.3
remote .relay creation or repair
GitHub repository writes
Project repository mutation
branch/commit/pull-request creation
local Git/worktree management
agent execution
```

A completed Slice 1.2 implementation still requires independent evaluation and a separate Human Authority acceptance before it becomes accepted project authority.

**Unblocked ≠ authorized.**
