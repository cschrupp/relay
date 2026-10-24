# Slice 2.4 — Finalization Handoff

**Document class:** Finalization execution handoff  
**Status:** AUTHORIZED / READY FOR EXECUTION  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Record:** `RLY-S24-FINALIZATION-HANDOFF-001`  
**Authority:** `RLY-S24-CLOSE-AUTH-001 — AUTHORIZED`  
**Authority commit:** `afad951b50593d0e06288e24fbb1333fde6b7672`

## Objective

Produce exactly one Slice 2.4 closure-ready candidate that preserves the accepted Slice 2.4 implementation/governance lineage and the separately authorized proposed Slice 2.5 strategic lineage, then STOP for independent closure evaluation.

Do not mark Slice 2.4 closed before closure evaluation ACCEPT.

## Exact governed subjects

```text
Repository:
cschrupp/relay

Canonical main:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

Accepted Slice 2.4 implementation:
73a1525282e41464d31cd458b8a50703bfa9553c

Final implementation evaluation:
RLY-S24-IMPL-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S24-ACCEPT-001 — ACCEPTED

Accepted Slice 2.4 governance head before close authority:
2d81ff876db2260f58446401a4546ebeb8fb6bae

Close authority:
afad951b50593d0e06288e24fbb1333fde6b7672
RLY-S24-CLOSE-AUTH-001 — AUTHORIZED

Strategic Phase-2 / proposed Slice 2.5 lineage:
95fa58717de87086d550f0c1a22f68c0d385754c

Finalization branch:
finalization/2.4-execution-workspace-authority
```

## Required merge topology

The finalization branch is created from the current accepted Slice 2.4 governance line containing the close authority and this handoff.

The closure-ready candidate must be a true merge descendant of both:

```text
Slice 2.4 accepted/finalization lineage
strategic lineage 95fa58717de87086d550f0c1a22f68c0d385754c
```

No rebase, squash, cherry-pick recreation, manual history recreation, or force push.

The merged tree must preserve the exact strategic architecture/authority/slice documents while reconciling the living projections into one current truth.

## Accepted implementation freeze

The ten Slice 2.4 production/test paths listed in `RLY-S24-CLOSE-AUTH-001` remain byte-identical to `73a1525282e41464d31cd458b8a50703bfa9553c`.

No source/test mutation is allowed.

## Registry reconciliation

Starting accepted Slice 2.4 registry:

```text
326 artifacts
Build Plan       r140
Current Baseline r154
Product Proposal r56
TODO             r48
```

Add/register:

```text
Slice 2.4 close authority
Slice 2.4 finalization handoff
strategic architecture document
strategic Human authority
proposed Slice 2.5 document
```

Closure-ready target:

```text
331 artifacts
Build Plan       r141
Current Baseline r155
Product Proposal r57
TODO             r49
canonical keys   exactly 5
```

All living projection revisions receive new ArtifactIds.

Do not import the strategic branch's parallel living rows as simultaneous current rows.

## Closure-ready status

The controlling state must establish:

```text
Slice 2.4:
OPEN — IMPLEMENTATION HUMAN ACCEPTED / CLOSURE-READY

Independent closure evaluation:
PENDING

Slice 2.5:
PROPOSED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

and preserve all production/runtime non-authorizations from the close authority.

## Strategic state to preserve

The following exact files from strategic lineage must be present unchanged:

```text
docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
docs/reviews/PHASE_2_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_STRATEGIC_AMENDMENT_AUTHORIZATION.md
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
```

The roadmap/backlog must preserve that Slice 2.5 closes the authority-state-resolution gap and is a prerequisite before Phase 3 opening.

## Authorized mutable surface

During finalization reconciliation:

```text
.relay/registry.json
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/TODO.md
docs/architecture/README.md
```

plus the exact strategic files arriving unchanged through merge ancestry.

Do not mutate immutable accepted records.

## Validation

Run:

```bash
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest tests/unit/test_repository_contract.py
uv run pytest
uv build
git diff --check
```

Additionally prove:

```text
registry count == 331
registry paths unique
registry order valid
registered digests exact
canonical keys == 5

Build Plan == 141
Current Baseline == 155
Product Proposal == 57
TODO == 49

main 3ea0bcf... ancestor
accepted implementation 73a1525... ancestor
close authority ancestor
this handoff ancestor
strategic lineage 95fa587... ancestor

accepted Slice 2.4 source/test bytes unchanged

Slice 2.5 NOT OPEN / NOT AUTHORIZED
Phase 3 NOT OPEN / NOT AUTHORIZED
```

Push the exact closure-ready candidate and require exact-head CI success.

## Required stop

STOP after producing the closure-ready candidate and validation report.

Do not:

- write the independent closure evaluation as the finalization executor;
- mark Slice 2.4 CLOSED;
- perform post-ACCEPT closed-state bookkeeping;
- update main.

Those actions are conditional on the independent closure evaluation required by `RLY-S24-CLOSE-AUTH-001`.
