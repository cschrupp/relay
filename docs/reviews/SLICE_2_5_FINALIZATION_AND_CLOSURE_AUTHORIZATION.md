# Slice 2.5 — Finalization and Closure Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Authority:** `RLY-S25-CLOSE-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes bounded Slice 2.5 finalization, independent closure evaluation, and the conditional post-ACCEPT closure/promotion sequence defined by this record.

Technical acceptance is complete. This authority does **not** itself declare Slice 2.5 closed.

## Exact authority basis

```text
Canonical starting main:
fbe41dfcb72df2dd3d145818c6b22478416de789

Accepted Slice 2.5 implementation:
88dcb97110665a60b21b5d36f82f0d82b015b098

Final independent implementation evaluation:
RLY-S25-IMPL-EVAL-003 — ACCEPT

Independent evaluation record:
948444b3b51360e91eb484613ec854627b241253

Human technical acceptance:
RLY-S25-ACCEPT-001 — ACCEPTED

Human acceptance record / current accepted governance head before this authority:
25b1cf66fa059f07b9fec3bf7a96608c0a540d02

Accepted normative design:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Original implementation scope:
RLY-S25-CODEX-SCOPE-001
```

The accepted Slice 2.5 governance lineage is a direct descendant of canonical starting main:

```text
fbe41dfcb72df2dd3d145818c6b22478416de789
    -> 46 commits ahead
    -> 0 commits behind
    -> 25b1cf66fa059f07b9fec3bf7a96608c0a540d02
```

Finalization must preserve this true Git ancestry. No rebase, squash, cherry-pick recreation, manual history recreation, or force update is permitted.

## Finalization branch

Use:

`finalization/2.5-project-state-resolution-authority-compilation`

The finalization branch must be rooted in the exact accepted governance lineage containing this authority and its finalization handoff.

No source/test mutation is authorized during finalization.

## Accepted implementation freeze

The complete authorized Slice 2.5 implementation/test surface must remain byte-identical to exact accepted implementation `88dcb97110665a60b21b5d36f82f0d82b015b098`:

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

If finalization appears to require changing any accepted implementation/test byte, STOP.

## Immutable governance freeze

Do not rewrite, amend in place, or replace the already-created immutable Slice 2.5 authority/evaluation/acceptance records.

Finalization may register them in the Relay artifact registry but may not alter their content.

## Registry reconciliation basis

The exact accepted governance head before this close authority has:

```text
registry artifacts:
338

canonical keys:
5

Build Plan:
revision 145

Current Baseline:
revision 162

Product Proposal:
revision 61

TODO:
revision 53

Slice 2.5 strategic architecture:
revision 4

Slice 2.5 working slice document:
revision 4
```

Eight already-existing Slice 2.5 implementation/governance records are present in Git history but not yet registered:

```text
docs/reviews/SLICE_2_5_CODEX_IMPLEMENTATION_SCOPE.md
docs/reviews/SLICE_2_5_IMPLEMENTATION_AUTHORIZATION.md
docs/reviews/SLICE_2_5_IMPLEMENTATION_EVALUATION_001.md
docs/reviews/SLICE_2_5_IMPLEMENTATION_EVALUATION_002.md
docs/reviews/SLICE_2_5_IMPLEMENTATION_EVALUATION_003.md
docs/reviews/SLICE_2_5_IMPLEMENTATION_REWORK_AUTHORIZATION_001.md
docs/reviews/SLICE_2_5_IMPLEMENTATION_REWORK_AUTHORIZATION_002.md
docs/reviews/SLICE_2_5_IMPLEMENTATION_ACCEPTANCE_001.md
```

This close authority and its finalization handoff add exactly two more immutable records.

Therefore the closure-ready reconciled registry must contain exactly:

```text
338 existing registered artifacts
+ 8 existing unregistered Slice 2.5 implementation/governance records
+ 2 Slice 2.5 finalization records
= 348 artifacts
```

Registry requirements:

```text
artifact count == 348
paths unique
normative ordering valid
all registered content digests exact
canonical keys == 5
all immutable records remain immutable/lockable
```

Do not create duplicate historical rows for the same immutable record.

## Closure-ready living projections

Finalization is authorized to advance exactly once:

```text
Build Plan:
145 -> 146

Current Baseline:
162 -> 163

Product Proposal:
61 -> 62

TODO:
53 -> 54
```

Each living projection must retain its path, receive the required new exact registry identity/revision according to the repository contract, and preserve the existing five canonical-key model. Canonical pointers for Build Plan, Current Baseline, and Product Proposal must move to the new exact revisions. TODO remains current but non-canonical.

The Slice 2.5 working architecture/status documents are also authorized to advance exactly once:

```text
docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
revision 4 -> 5

docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
revision 4 -> 5
```

These revisions may reconcile status/governance truth only. They must not alter the Human-accepted design semantics.

## Required closure-ready truth

Before independent closure evaluation, controlling state must say in substance:

```text
Slice 2.5:
OPEN — IMPLEMENTATION HUMAN ACCEPTED / CLOSURE-READY

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

ProjectStateResolver / AuthorityCompiler production wiring:
NOT AUTHORIZED

Production WorkPacket compilation/wiring:
NOT AUTHORIZED

Operational persistence / lifecycle mutation:
NOT AUTHORIZED

AgentRuntime / provider / model / network execution:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
Slice 2.5 closure remains the final prerequisite before Phase 3 may become eligible to open.

Real-project agent execution:
NOT AUTHORIZED
```

Do **not** mark Slice 2.5 COMPLETE / ACCEPTED / CLOSED before independent closure evaluation returns ACCEPT.

## Authorized finalization surface

Expected mutable paths are limited to:

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

plus creation of the immutable finalization records authorized here.

Navigation/status files may change only where necessary to remove a direct contradiction with the closure-ready truth.

No opportunistic cleanup.

## Prohibited finalization surface

Do not modify:

```text
src/**
tests/**
pyproject.toml
uv.lock
.github/workflows/**
database schema/migrations
operational database state
accepted immutable Slice 2.5 design/review/authority/acceptance records
```

No production ProjectStateResolver/AuthorityCompiler wiring, WorkPacket wiring, persistence integration, AgentRuntime/model/provider execution, Phase 3 work, real-project execution, or unrelated architecture work is authorized.

## Required closure-ready validation

Run on the exact closure-ready SHA:

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

Also prove:

```text
registry artifact count == 348
registry paths unique
registry ordering valid
registered digests exact
canonical keys == 5

Build Plan revision == 146
Current Baseline revision == 163
Product Proposal revision == 62
TODO revision == 54
Slice 2.5 architecture revision == 5
Slice 2.5 slice-document revision == 5

canonical starting main fbe41df... is ancestor
accepted implementation 88dcb971... is ancestor
RLY-S25-IMPL-EVAL-003 record is ancestor
RLY-S25-ACCEPT-001 record is ancestor
this close authority is ancestor
finalization handoff is ancestor

all nine accepted Slice 2.5 implementation/test files remain byte-identical to 88dcb971...

Slice 2.5 remains OPEN / CLOSURE-READY until independent closure ACCEPT
production wiring remains NOT AUTHORIZED
Phase 3 remains NOT OPEN / NOT AUTHORIZED
real-project execution remains NOT AUTHORIZED
```

Exact-head CI must succeed.

## Independent closure evaluation

The finalization executor must STOP after producing the exact closure-ready candidate.

The independent closure evaluator returns exactly:

```text
ACCEPT
REWORK
ESCALATE
```

No closed-state bookkeeping or canonical promotion is permitted before independent closure ACCEPT.

## Conditional post-ACCEPT closure bookkeeping

If and only if the exact closure-ready candidate receives:

`RLY-S25-CLOSE-EVAL-001 — ACCEPT`

this authority also permits bounded post-ACCEPT closed-state bookkeeping.

First preserve/register the immutable closure evaluation.

Then advance the current-state documents exactly one more revision:

```text
Build Plan:
146 -> 147

Current Baseline:
163 -> 164

Product Proposal:
62 -> 63

TODO:
54 -> 55

Slice 2.5 strategic architecture:
5 -> 6

Slice 2.5 working slice document:
5 -> 6
```

After registering the closure-evaluation record:

```text
registry artifact count:
348 -> 349
```

and it remains 349 through the closed-state projection revisions.

Closed-state controlling truth must say:

```text
Slice 2.5:
COMPLETE / ACCEPTED / CLOSED

Independent closure evaluation:
RLY-S25-CLOSE-EVAL-001 — ACCEPT

Accepted implementation:
88dcb97110665a60b21b5d36f82f0d82b015b098

ProjectStateResolver / AuthorityCompiler production wiring:
NOT AUTHORIZED

Production WorkPacket compilation/wiring:
NOT AUTHORIZED

Operational persistence / lifecycle mutation:
NOT AUTHORIZED

Phase 3:
ELIGIBLE TO OPEN / NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Update `docs/architecture/README.md` consistently.

Slice 2.5 closure removes the prerequisite blocker for a separately authorized Phase 3 opening. It does not itself open or authorize Phase 3.

Rerun full validation and exact-head CI.

## Conditional canonical promotion

After closure ACCEPT and green closed-state validation, fast-forward canonical `main` only if:

```text
remote main still equals:
fbe41dfcb72df2dd3d145818c6b22478416de789

closed-state lineage:
ahead of main
behind main by 0

all required ancestry preserved
accepted Slice 2.5 implementation/test bytes preserved
registry contract valid
exact-head CI green
```

Never force-update, rebase, squash, rewrite, or recreate accepted history.

If canonical main moved independently, STOP and reconcile rather than forcing promotion.

## Authority boundary

```text
RLY-S25-CLOSE-AUTH-001 — AUTHORIZED

Technical acceptance:
COMPLETE

Finalization:
AUTHORIZED

Closure-ready candidate:
AUTHORIZED TO PRODUCE

Independent closure evaluation:
REQUIRED

Slice 2.5 CLOSED:
CONDITIONAL ON RLY-S25-CLOSE-EVAL-001 — ACCEPT

Canonical promotion:
CONDITIONAL ON CLOSURE ACCEPT + GREEN CLOSED-STATE VALIDATION + UNCHANGED MAIN

Production ProjectStateResolver / AuthorityCompiler wiring:
NOT AUTHORIZED

Production WorkPacket compilation/wiring:
NOT AUTHORIZED

Operational persistence / lifecycle:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
ELIGIBLE TO OPEN ONLY AFTER SLICE 2.5 CLOSURE ACCEPT

Real-project execution:
NOT AUTHORIZED
```

**Technical acceptance != closure. Finalization authority != closure. Independent closure ACCEPT is required before CLOSED state or canonical promotion.**
