# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.4 finalized; independent closure evaluation pending  
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
```

Slice 1.3 canonical closure:

```text
RLY-S13-CLOSE-EVAL-001 — ACCEPT
7d266aef282c6d678e059754d2eb6a5ff297d83a
```

# 2. Slice 1.4 authority and accepted result

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
```

# 3. Current gate

```text
Slice 1.4:
TECHNICAL RESULT ACCEPTED / FINALIZED

Locked development memory:
docs/slices/SLICE_1_4_PROJECT_AND_SLICE_CRUD_MEMORY.md

Current role:
INDEPENDENT CLOSURE EVALUATOR — GPT-5.6 Sol

Closure evaluation:
PENDING

Slice 1.5:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

# 4. Accepted Slice 1.4 technical summary

The accepted implementation:

- leaves accepted `Project` and `Slice` domain schemas unchanged;
- introduces definition revisions/history through migration v4;
- establishes the administration service as the only post-v4 runtime Project/Slice creation path;
- requires HUMAN mutation provenance and strict revision CAS;
- keeps Project repository authority and Slice project ownership immutable;
- validates same-Project acyclic parent/dependency graphs;
- freezes Slice definitions after lifecycle initialization, gate creation, or downstream dependency consumption;
- guards physical deletion and preserves tombstones/retired identities;
- detects malformed durable history and fails closed;
- adds no runtime dependency;
- performs no board, provider, repository-sync, lifecycle-schema, or agent work.

Accepted candidate evidence:

```text
GitHub Actions 36899665799 — SUCCESS
pytest — 525 passed
Project/Slice service suite — 33 passed
Ruff format/lint — PASS
Pyright — PASS, 0 errors / 0 warnings
uv build — PASS
```

# 5. Protocol boundary

Technical acceptance and finalization do not automatically open the next Slice.

Exact authority boundaries and exact SHAs remain controlling.

**Unblocked ≠ authorized.**
