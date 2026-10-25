# Slice 2.5 — Finalization Handoff

**Document class:** Finalization execution handoff  
**Status:** AUTHORIZED / READY FOR EXECUTION  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Record:** `RLY-S25-FINALIZATION-HANDOFF-001`  
**Authority:** `RLY-S25-CLOSE-AUTH-001 — AUTHORIZED`  
**Authority commit:** `529b80d56ff989c41fa5fa320670662e278b0d56`

## Objective

Produce exactly one Slice 2.5 closure-ready candidate that preserves the accepted implementation and governance lineage, reconciles current registry/projection truth, then STOP for independent closure evaluation.

Do not mark Slice 2.5 closed before `RLY-S25-CLOSE-EVAL-001 — ACCEPT`.

## Exact governed subjects

```text
Repository:
cschrupp/relay

Canonical starting main:
fbe41dfcb72df2dd3d145818c6b22478416de789

Accepted Slice 2.5 implementation:
88dcb97110665a60b21b5d36f82f0d82b015b098

Final implementation evaluation:
RLY-S25-IMPL-EVAL-003 — ACCEPT
948444b3b51360e91eb484613ec854627b241253

Human technical acceptance:
RLY-S25-ACCEPT-001 — ACCEPTED
25b1cf66fa059f07b9fec3bf7a96608c0a540d02

Finalization / closure authority:
RLY-S25-CLOSE-AUTH-001 — AUTHORIZED
529b80d56ff989c41fa5fa320670662e278b0d56

Finalization branch:
finalization/2.5-project-state-resolution-authority-compilation
```

## Required lineage

The finalization branch must be a true descendant of:

```text
fbe41dfcb72df2dd3d145818c6b22478416de789
88dcb97110665a60b21b5d36f82f0d82b015b098
948444b3b51360e91eb484613ec854627b241253
25b1cf66fa059f07b9fec3bf7a96608c0a540d02
529b80d56ff989c41fa5fa320670662e278b0d56
this handoff
```

No rebase, squash, cherry-pick recreation, force update, or manual history recreation.

## Accepted implementation freeze

The following paths must remain byte-identical to exact accepted implementation `88dcb97110665a60b21b5d36f82f0d82b015b098`:

```text
src/relay_engine/project_state/__init__.py
src/relay_engine/project_state/models.py
src/relay_engine/project_state/resolution.py
src/relay_engine/project_state/compilation.py

tests/unit/test_project_state_models.py
tests/unit/test_project_state_resolution.py
tests/unit/test_authority_compilation.py
tests/unit/test_project_state_dogfood.py
tests/unit/test_project_state_architecture.py
```

No implementation mutation is allowed.

## Registry reconciliation

Starting exact registry:

```text
artifact count:
338

canonical keys:
5

Build Plan:
145

Current Baseline:
162

Product Proposal:
61

TODO:
53

Slice 2.5 architecture:
4

Slice 2.5 slice document:
4
```

Register the eight existing unregistered Slice 2.5 implementation/governance records plus:

```text
SLICE_2_5_FINALIZATION_AND_CLOSURE_AUTHORIZATION.md
SLICE_2_5_FINALIZATION_HANDOFF.md
```

Closure-ready target:

```text
artifact count:
348

Build Plan:
146

Current Baseline:
163

Product Proposal:
62

TODO:
54

Slice 2.5 architecture:
5

Slice 2.5 slice document:
5

canonical keys:
exactly 5
```

All paths and digests must be exact and unique.

## Closure-ready status

Controlling truth must establish:

```text
Slice 2.5:
OPEN / IMPLEMENTATION HUMAN ACCEPTED / CLOSURE-READY

Accepted implementation:
88dcb97110665a60b21b5d36f82f0d82b015b098

Independent implementation evaluation:
RLY-S25-IMPL-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S25-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S25-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Production ProjectStateResolver / AuthorityCompiler wiring:
NOT AUTHORIZED

Production WorkPacket compilation/wiring:
NOT AUTHORIZED

Operational persistence/lifecycle:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

Do not declare Slice 2.5 closed.

## Authorized mutable surface

Exactly the bounded finalization/status surface:

```text
.relay/registry.json
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/TODO.md
docs/architecture/README.md
docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
```

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
registry count == 348
registry paths unique
registry ordering valid
all registered digests exact
canonical keys == 5

Build Plan == 146
Current Baseline == 163
Product Proposal == 62
TODO == 54
Slice 2.5 architecture == 5
Slice 2.5 slice document == 5

main fbe41df... ancestor
accepted implementation 88dcb971... ancestor
implementation evaluation 948444b3... ancestor
Human acceptance 25b1cf66... ancestor
close authority 529b80d5... ancestor
this handoff ancestor

all nine accepted implementation/test paths unchanged

Slice 2.5 remains OPEN / CLOSURE-READY
Phase 3 remains NOT OPEN / NOT AUTHORIZED
production wiring remains NOT AUTHORIZED
```

Push the exact closure-ready candidate and require exact-head CI success.

## Required stop

STOP after producing the closure-ready candidate and validation report.

Do not:

- write the independent closure evaluation as the finalization executor;
- mark Slice 2.5 CLOSED;
- perform post-ACCEPT closed-state bookkeeping;
- open or authorize Phase 3;
- update canonical main.

Those actions are conditional on the independent closure evaluation required by `RLY-S25-CLOSE-AUTH-001`.
