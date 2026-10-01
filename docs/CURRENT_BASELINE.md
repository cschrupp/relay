# Relay — Current Baseline

**Status:** Phase 1 open — Slices 1.1–1.4 complete, accepted, and closed  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** October 2026

---

# 1. Accepted foundation

```text
Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
COMPLETE / ACCEPTED / CLOSED
```

# 2. Slice 1.4 canonical authority and closure

```text
Opening:
RLY-S14-OPEN-001

Design authorization:
RLY-S14-DESIGN-AUTH-001

Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Design Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Accepted Revision 2 design:
f5a678da360b96701a1f9635d3703b49dc16e779

Implementation authorization:
RLY-S14-AUTH-001 — AUTHORIZED

Canonical rework baseline:
dfe6c20c8f65b42fe69b7d315956a91d2a29487c

Prior implementation candidate:
e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d

Prior implementation evaluation:
RLY-S14-EVAL-001 — REWORK

Accepted technical result:
ae582c52ec4a6451b54e9d6e018932e93e72e013

Independent implementation evaluation:
RLY-S14-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S14-ACCEPT-001 — ACCEPTED

Finalization / closure authorization:
RLY-S14-CLOSE-AUTH-001 — AUTHORIZED

Finalization baseline:
ba31db3ace9d99f573e26611637c567b3f1e8d44

Independent closure evaluation:
RLY-S14-CLOSE-EVAL-001 — ACCEPT
```

# 3. Accepted Slice 1.4 technical result

The exact accepted implementation result remains:

```text
ae582c52ec4a6451b54e9d6e018932e93e72e013
```

Final locked development memory:

`docs/slices/SLICE_1_4_PROJECT_AND_SLICE_CRUD_MEMORY.md`

Finalization evidence:

```text
Finalization branch CI 36907196036 — SUCCESS
Promoted-main CI 36907265025 — SUCCESS
525 tests — PASS
Ruff format/lint — PASS
Pyright — PASS
uv build — PASS
```

# 4. Current authority boundary

```text
Current role:
HUMAN AUTHORITY / ORCHESTRATOR

Slice 1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

Opening Slice 1.5 requires a separate explicit Human Authority decision.

**Unblocked ≠ authorized.**
