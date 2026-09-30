# Slice 1.4 — Design Acceptance

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-09-30  
**Project:** Relay  
**Slice:** 1.4  
**Record:** `RLY-S14-DESIGN-ACCEPT-001`

## Reviewed design

```text
Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Revision 2 amendment / exact reviewed design head:
f5a678da360b96701a1f9635d3703b49dc16e779

Independent combined design evaluation:
RLY-S14-DESIGN-EVAL-002 — ACCEPT
```

## Human Authority decision

```text
RLY-S14-DESIGN-ACCEPT-001
Slice 1.4 Design Revision 1 + Revision 2 Amendment
ACCEPTED
```

The accepted design is bound to exact reviewed head:

```text
f5a678da360b96701a1f9635d3703b49dc16e779
```

## Accepted design boundary

The accepted combined design covers human-controlled Project and Slice definition administration while preserving existing lifecycle and governance authority. It includes:

- immutable Project/Slice identities and immutable Project repository authority;
- audited Project/Slice CREATE, deterministic reads/lists, guarded UPDATE, and guarded DELETE;
- strict optimistic definition revisions and append-only definition history;
- SQLite migration v4 with migration-only SEED revisions;
- one post-v4 runtime creation path through the administration service;
- same-project parent/dependency validation and cycle protection;
- permanent Slice-definition freeze once lifecycle is initialized;
- conservative freeze for downstream dependency use;
- explicit destructive-delete blockers and retired-identity tombstones;
- lifecycle ownership of block/unblock/cancel/supersede;
- no new runtime dependency.

Independent review findings F001–F004 are closed by Revision 2.

## Authority boundary

This record accepts the design only.

It does **not** authorize:

```text
Slice 1.4 production implementation
SQLite migration v4 implementation
production Project/Slice CRUD behavior
Slice 1.5
board/UI work
agent execution
```

A separate Human Authority decision is required before Slice 1.4 implementation may begin.

**Unblocked ≠ authorized.**
