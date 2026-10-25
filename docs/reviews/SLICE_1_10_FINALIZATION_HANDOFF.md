# Relay — Slice 1.10 Canonical Source and Promotion Enforcement — Finalization Handoff

**Document class:** Finalization execution handoff  
**Status:** AUTHORIZED / READY FOR EXECUTION  
**Date:** 2026-10-25  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Record:** `RLY-S110-FINALIZATION-HANDOFF-001`  
**Authority:** `RLY-S110-CLOSE-AUTH-001 — AUTHORIZED`  
**Authority commit:** `b69a2564809988fe5853b225e2ecb75fa058d7de`

## Objective

Produce exactly one Slice 1.10 closure-ready candidate that preserves the accepted historical implementation subject, preserves all later compatible shared-file evolution, reconciles current governance/projection truth, and then STOP for independent closure evaluation.

Do not mark Slice 1.10 closed before `RLY-S110-CLOSE-EVAL-001 — ACCEPT`.

## Exact governed subjects

```text
Repository:
cschrupp/relay

Canonical main:
da966f67676a227488ef216d388d405b5e383d93

Historical accepted implementation:
8003170f56120640ab29eb776cc1b2ba53c66a5f

Independent implementation evaluation:
RLY-S110-IMPL-EVAL-001 — ACCEPT
0d151d11cfb5b167678d229cf4234b8a5c95d545

Human technical acceptance:
RLY-S110-ACCEPT-001 — ACCEPTED
bf038bf3e8cfc94bf3747c044e2ea61935eda325

Finalization / closure authority:
RLY-S110-CLOSE-AUTH-001 — AUTHORIZED
b69a2564809988fe5853b225e2ecb75fa058d7de

Finalization branch:
finalization/1.10-canonical-source-promotion-enforcement
```

## Required lineage

The finalization branch must preserve true ancestry from:

```text
da966f67676a227488ef216d388d405b5e383d93
8003170f56120640ab29eb776cc1b2ba53c66a5f
0d151d11cfb5b167678d229cf4234b8a5c95d545
bf038bf3e8cfc94bf3747c044e2ea61935eda325
b69a2564809988fe5853b225e2ecb75fa058d7de
this handoff
```

No rebase, squash, cherry-pick recreation, force update, or manual history recreation.

## Source/test freeze

No source or test file may change during finalization:

```text
src/**
tests/**
```

The finalization candidate must preserve current canonical code/test bytes from `da966f...`.

This also preserves the independently accepted historical Slice 1.10 implementation semantics and later compatible shared-file evolution.

## Registry reconciliation

Starting exact registry at the Human-acceptance lineage:

```text
artifact count:
350

canonical keys:
5

Build Plan:
148

Current Baseline:
165

Product Proposal:
64

TODO:
56
```

Register these four immutable records not present in the starting registry:

```text
docs/reviews/SLICE_1_10_IMPLEMENTATION_EVALUATION_001.md
docs/reviews/SLICE_1_10_IMPLEMENTATION_ACCEPTANCE_001.md
docs/reviews/SLICE_1_10_FINALIZATION_AND_CLOSURE_AUTHORIZATION.md
docs/reviews/SLICE_1_10_FINALIZATION_HANDOFF.md
```

Closure-ready target:

```text
artifact count:
354

canonical keys:
5

Build Plan:
149

Current Baseline:
166

Product Proposal:
65

TODO:
57
```

All registered paths and digests must be exact and unique.

## Closure-ready status

Controlling truth must establish:

```text
Slice 1.10:
OPEN / IMPLEMENTATION HUMAN ACCEPTED / CLOSURE-READY

Exact implementation:
8003170f56120640ab29eb776cc1b2ba53c66a5f

Independent implementation evaluation:
RLY-S110-IMPL-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S110-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S110-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Phase 3:
OPEN

Slice 3.1:
NOT OPEN / NOT AUTHORIZED

Phase 3 execution:
GATED by Slice 1.10 closure

Live canonical-promotion execution:
NOT AUTHORIZED

Production resolver/compiler wiring:
NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

Do not declare Slice 1.10 closed.

## Authorized mutable surface

Expected finalization/status surface:

```text
.relay/registry.json
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/TODO.md
docs/architecture/README.md
```

Additional navigation/status files may change only if direct contradictory current-state text requires reconciliation.

No source/test/configuration/dependency/CI/database/runtime mutation.

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
registry count == 354
registry paths unique
registry ordering valid
registered digests exact
canonical keys == 5

Build Plan == 149
Current Baseline == 166
Product Proposal == 65
TODO == 57

canonical main da966f... ancestor
historical implementation 8003170f... ancestor
implementation evaluation 0d151d11... ancestor
Human acceptance bf038bf3... ancestor
close authority b69a2564... ancestor
this handoff ancestor

no src/** or tests/** changes from da966f...

Slice 1.10 remains OPEN / CLOSURE-READY
Phase 3 remains OPEN
Slice 3.1 remains NOT OPEN / NOT AUTHORIZED
live promotion/runtime execution remains NOT AUTHORIZED
```

Push the exact closure-ready candidate and require exact-head CI success.

## Required stop

STOP after producing the closure-ready candidate and validation report.

Do not:

- write the independent closure evaluation as the finalization executor;
- mark Slice 1.10 CLOSED;
- perform post-ACCEPT closed-state bookkeeping;
- open or authorize Slice 3.1;
- update canonical main;
- execute live promotion, policy binding, reconciliation, provider/model runtime, or real-project agent work.

Those actions remain conditional on the independent closure evaluation required by `RLY-S110-CLOSE-AUTH-001`.
