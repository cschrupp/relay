# Slice 2.4 — Finalization and Closure Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority:** `RLY-S24-CLOSE-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes bounded Slice 2.4 finalization, independent closure evaluation, and the conditional post-ACCEPT closure/promotion sequence defined by this record.

Technical acceptance is complete. This authority does not itself declare Slice 2.4 closed.

## Exact authority basis

```text
Canonical starting main:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

Accepted implementation:
73a1525282e41464d31cd458b8a50703bfa9553c

Final independent implementation evaluation:
RLY-S24-IMPL-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S24-ACCEPT-001 — ACCEPTED

Human-accepted Slice 2.4 governance head before this authority:
2d81ff876db2260f58446401a4546ebeb8fb6bae

Accepted Revision 6:
4f743d0e8d782ba86903055849f8550e42ae3eeb

Revision 6 Human acceptance:
RLY-S24-I003-R2-DESIGN-ACCEPT-001 — ACCEPTED

Parallel strategic Phase-2 / proposed Slice 2.5 lineage:
95fa58717de87086d550f0c1a22f68c0d385754c

Strategic authority:
RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED
```

Both the accepted Slice 2.4 governance line and the proposed Slice 2.5 strategic line are direct descendants of canonical starting main and diverge after exact implementation subject `73a1525...`.

Finalization must preserve both lineages as true Git ancestors.

## Finalization branch

Use:

`finalization/2.4-execution-workspace-authority`

The finalization branch is rooted in the Human-accepted Slice 2.4 governance lineage containing this authority and its handoff.

The closure-ready candidate must additionally merge the exact strategic lineage `95fa58717de87086d550f0c1a22f68c0d385754c` using true merge ancestry.

No rebase, squash, cherry-pick recreation, manual history recreation, or force-update is permitted.

## Required ancestry

The closure-ready result must preserve as true ancestors at minimum:

```text
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc
    canonical starting main

73a1525282e41464d31cd458b8a50703bfa9553c
    accepted Slice 2.4 implementation

4f743d0e8d782ba86903055849f8550e42ae3eeb
    accepted Revision 6 subject

2d81ff876db2260f58446401a4546ebeb8fb6bae
    Human-accepted Slice 2.4 governance head before close authority

95fa58717de87086d550f0c1a22f68c0d385754c
    proposed Slice 2.5 strategic lineage

this authority
this finalization handoff
```

If reconciliation requires changing accepted Slice 2.4 source/test bytes or immutable governance records, STOP.

## Accepted implementation freeze

These paths must remain byte-identical to exact accepted implementation `73a1525282e41464d31cd458b8a50703bfa9553c`:

```text
src/relay_engine/execution_workspace/__init__.py
src/relay_engine/execution_workspace/models.py
src/relay_engine/execution_workspace/evaluation.py
src/relay_engine/execution_workspace/provider.py
src/relay_engine/execution_workspace/local_clone.py

tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
```

No corrective source/test mutation is authorized during finalization.

## Strategic-line reconciliation

The proposed Slice 2.5 work is documentation/architecture strategy only.

Finalization must preserve exact strategic artifacts:

```text
docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
docs/reviews/PHASE_2_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_STRATEGIC_AMENDMENT_AUTHORIZATION.md
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
```

and preserve the strategic meaning:

```text
Slice 2.5:
PROPOSED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Slice 2.5 COMPLETE / ACCEPTED / CLOSED:
required before Phase 3 becomes eligible to open
```

The strategic branch's parallel living-projection revisions are historical branch state. Reconciliation must advance the accepted Slice 2.4 living-projection lineage once; it must not preserve conflicting parallel living rows as simultaneous current truth.

## Registry reconciliation basis

The Human-accepted Slice 2.4 governance head currently has:

```text
artifact count: 326
Build Plan:       revision 140
Current Baseline: revision 154
Product Proposal: revision 56
TODO:             revision 48
canonical keys:   exactly 5
```

This close authority and its handoff add two immutable records.

The strategic lineage contributes exactly three new registered artifacts not already present in the accepted Slice 2.4 registry:

```text
docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
docs/reviews/PHASE_2_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_STRATEGIC_AMENDMENT_AUTHORIZATION.md
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md
```

Therefore the closure-ready reconciled registry must contain exactly:

```text
326 existing artifacts
+2 Slice 2.4 finalization records
+3 strategic artifacts
=331 artifacts
```

with unique paths, normative ordering, exact digests, all immutable/lockable history, and exactly five canonical keys.

## Closure-ready living projections

Finalization is authorized to advance exactly once from the accepted Slice 2.4 lineage:

```text
Build Plan:
140 -> 141

Current Baseline:
154 -> 155

Product Proposal:
56 -> 57

TODO:
48 -> 49
```

Each changed living projection must use the same path, a new ArtifactId, revision +1 exactly, exact SHA-256 digest, `LIVING_PROJECTION / CURRENT`, and null supersession fields.

Move canonical pointers for Build Plan, Current Baseline, and Product Proposal. TODO remains current but non-canonical.

The closure-ready living projections must also incorporate the Human-authorized proposed Slice 2.5 strategic direction.

## Required closure-ready truth

Before independent closure evaluation, controlling living state must say in substance:

```text
Slice 2.4:
OPEN — IMPLEMENTATION HUMAN ACCEPTED / CLOSURE-READY

Accepted implementation:
73a1525282e41464d31cd458b8a50703bfa9553c

Independent implementation evaluation:
RLY-S24-IMPL-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S24-ACCEPT-001 — ACCEPTED

Composite design Revisions 1–6:
HUMAN ACCEPTED

Finalization / closure authority:
RLY-S24-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Slice 2.5:
PROPOSED / NOT OPEN / NOT AUTHORIZED

Production workspace provisioning:
NOT AUTHORIZED

Production WorkPacket wiring:
NOT AUTHORIZED

AgentRuntime / runtime-exposure implementation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Do not mark Slice 2.4 COMPLETE / ACCEPTED / CLOSED before independent closure evaluation returns ACCEPT.

## Authorized finalization surface

Expected mutable paths are:

```text
.relay/registry.json
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/TODO.md
docs/architecture/README.md
```

plus exact strategic artifacts arriving unchanged through the merged strategic lineage.

Navigation/status files may change only when needed to remove direct contradiction with closure-ready truth.

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
accepted Slice 2.4 immutable design/review/acceptance records
```

No production workspace wiring, production WorkPacket wiring, AgentRuntime/model execution, runtime tool/shell integration, Slice 2.5 implementation, Phase 3 work, or real-project execution is authorized.

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
registry artifact count == 331
registry paths unique
registry ordering valid
all registered digests exact
canonical keys == 5

Build Plan revision == 141
Current Baseline revision == 155
Product Proposal revision == 57
TODO revision == 49

canonical main 3ea0bcf... is ancestor
accepted implementation 73a1525... is ancestor
Human-accepted Slice 2.4 governance lineage is ancestor
strategic lineage 95fa587... is ancestor
close authority and handoff are ancestors

accepted Slice 2.4 source/test bytes remain exact

Slice 2.5 remains PROPOSED / NOT OPEN / NOT AUTHORIZED
Phase 3 remains NOT OPEN / NOT AUTHORIZED
real-project execution remains NOT AUTHORIZED
```

Exact-head CI must succeed.

## Independent closure evaluation

The finalization executor must stop after producing the exact closure-ready candidate.

The independent closure evaluator returns exactly ACCEPT, REWORK, or ESCALATE.

No closed-state bookkeeping or canonical promotion is permitted before independent closure ACCEPT.

## Conditional post-ACCEPT closure bookkeeping

If and only if the exact closure-ready candidate receives:

`RLY-S24-CLOSE-EVAL-001 — ACCEPT`

this authority also permits bounded post-ACCEPT closure bookkeeping.

First preserve/register the immutable closure evaluation.

Then advance the four living projections exactly one more revision:

```text
Build Plan:       141 -> 142
Current Baseline: 155 -> 156
Product Proposal: 57  -> 58
TODO:             49  -> 50
```

The closed-state controlling truth must say:

```text
Slice 2.4:
COMPLETE / ACCEPTED / CLOSED

Independent closure evaluation:
RLY-S24-CLOSE-EVAL-001 — ACCEPT

Accepted implementation:
73a1525282e41464d31cd458b8a50703bfa9553c

Slice 2.5:
PROPOSED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Production workspace / WorkPacket / AgentRuntime wiring:
NOT AUTHORIZED
```

After registering the closure-evaluation record the registry cardinality is 332 and remains 332 through closed-state living-projection advancement.

Update `docs/architecture/README.md` from Slice 2.4 OPEN to COMPLETE / ACCEPTED / CLOSED if it would otherwise contradict the closed state.

Rerun full validation and exact-head CI.

## Conditional canonical promotion

After closure ACCEPT and green closed-state validation, fast-forward canonical `main` only if:

```text
remote main still equals:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

closed-state lineage:
ahead of main
behind main by 0

all required ancestry preserved
accepted source/test bytes preserved
registry contract valid
exact-head CI green
```

Never force-update, rebase, squash, rewrite, or recreate accepted history.

If canonical main moved independently, STOP and reconcile rather than forcing promotion.

## Authority boundary

```text
RLY-S24-CLOSE-AUTH-001 — AUTHORIZED

Technical acceptance:
COMPLETE

Finalization:
AUTHORIZED

Closure-ready candidate:
AUTHORIZED TO PRODUCE

Independent closure evaluation:
REQUIRED

Slice 2.4 CLOSED:
CONDITIONAL ON RLY-S24-CLOSE-EVAL-001 — ACCEPT

Canonical promotion:
CONDITIONAL ON CLOSURE ACCEPT + GREEN VALIDATION + UNCHANGED MAIN

Slice 2.5:
PROPOSED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

**Technical acceptance != closure. Finalization authority != closure. Independent closure ACCEPT is required before CLOSED state or canonical promotion.**
