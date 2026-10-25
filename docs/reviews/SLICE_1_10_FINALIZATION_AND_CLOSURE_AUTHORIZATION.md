# Relay — Slice 1.10 Canonical Source and Promotion Enforcement — Finalization and Closure Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-25  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Authority:** `RLY-S110-CLOSE-AUTH-001 — AUTHORIZED`

## 1. Human Authority decision

The Human explicitly authorizes bounded top-level Slice 1.10 finalization, independent closure evaluation, and the conditional post-ACCEPT closed-state bookkeeping and canonical fast-forward defined by this record.

Top-level technical acceptance is complete.

This authority does **not** itself declare Slice 1.10 closed.

## 2. Exact authority basis

```text
Canonical starting main:
da966f67676a227488ef216d388d405b5e383d93

Exact historical implementation subject:
8003170f56120640ab29eb776cc1b2ba53c66a5f

Independent top-level implementation evaluation:
RLY-S110-IMPL-EVAL-001 — ACCEPT

Evaluation record commit:
0d151d11cfb5b167678d229cf4234b8a5c95d545

Human top-level technical acceptance:
RLY-S110-ACCEPT-001 — ACCEPTED

Human acceptance record:
bf038bf3e8cfc94bf3747c044e2ea61935eda325

Historical exact-head implementation CI:
38307308578 — SUCCESS

Current-main compatibility CI:
40165012106 — SUCCESS

B4 Relay Dogfood Acceptance:
COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED
```

The exact implementation subject remains historical candidate `8003170f...`.

Later accepted shared-file evolution is preserved as current canonical code state and was independently found compatible under `RLY-S110-IMPL-EVAL-001`.

## 3. Finalization branch

Use:

`finalization/1.10-canonical-source-promotion-enforcement`

The branch must be rooted in the exact Human-accepted Slice 1.10 governance lineage containing this authority and its handoff.

Because that governance lineage is already a direct descendant of canonical main `da966f...`, no merge recreation is required.

No rebase, squash, cherry-pick recreation, history rewrite, or force update is permitted.

## 4. Source/test freeze

Finalization is documentation/governance reconciliation only.

No file under:

```text
src/**
tests/**
```

may change during closure preparation.

This preserves both:

- exact historical accepted implementation semantics at `8003170f...`;
- all later accepted compatible shared-file evolution already present at canonical main `da966f...`.

If closure preparation appears to require source/test mutation, STOP.

## 5. Immutable governance freeze

Do not rewrite or amend in place:

- accepted Slice 1.10 design records;
- implementation authority/handoff;
- B0–B4 accepted/evaluated records;
- `RLY-S110-IMPL-EVAL-001`;
- `RLY-S110-ACCEPT-001`;
- this authority;
- its finalization handoff.

Finalization may register previously unregistered immutable records but may not alter their bytes.

## 6. Registry reconciliation basis

At exact Human-acceptance head `bf038bf3...`:

```text
registry artifacts:
350

canonical keys:
5

Build Plan:
revision 148

Current Baseline:
revision 165

Product Proposal:
revision 64

TODO:
revision 56
```

Two already-created top-level Slice 1.10 governance records are present in Git but not yet registered:

```text
docs/reviews/SLICE_1_10_IMPLEMENTATION_EVALUATION_001.md
docs/reviews/SLICE_1_10_IMPLEMENTATION_ACCEPTANCE_001.md
```

This closure authority and its handoff add exactly two additional immutable records:

```text
docs/reviews/SLICE_1_10_FINALIZATION_AND_CLOSURE_AUTHORIZATION.md
docs/reviews/SLICE_1_10_FINALIZATION_HANDOFF.md
```

Therefore the closure-ready reconciled registry must contain exactly:

```text
350 existing registered artifacts
+ 2 previously unregistered top-level implementation governance records
+ 2 finalization records
= 354 artifacts
```

Requirements:

```text
artifact count == 354
paths unique
normative ordering valid
registered digests exact
canonical keys == 5
immutable/locked records retain correct state
```

Do not create duplicate historical rows for the same immutable path.

## 7. Closure-ready living projections

Finalization is authorized to advance exactly once:

```text
Build Plan:
148 -> 149

Current Baseline:
165 -> 166

Product Proposal:
64 -> 65

TODO:
56 -> 57
```

Build Plan, Current Baseline, and Product Proposal canonical pointers must move to their exact new revisions.

TODO remains current but non-canonical.

`docs/architecture/README.md` may be reconciled as navigation/status text but is not a registered living projection.

## 8. Required closure-ready truth

Before independent closure evaluation, controlling state must say in substance:

```text
Slice 1.10:
OPEN — IMPLEMENTATION HUMAN ACCEPTED / CLOSURE-READY

Exact accepted implementation subject:
8003170f56120640ab29eb776cc1b2ba53c66a5f

Independent implementation evaluation:
RLY-S110-IMPL-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S110-ACCEPT-001 — ACCEPTED

B4:
COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED

Finalization / closure authority:
RLY-S110-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Phase 3:
OPEN

Slice 3.1:
NOT OPEN / NOT AUTHORIZED

Phase 3 execution:
GATED by Slice 1.10 top-level closure

Live canonical-promotion execution:
NOT AUTHORIZED

Live policy-binding execution:
NOT AUTHORIZED

Live quarantine reconciliation:
NOT AUTHORIZED

GitHub ruleset / branch-protection mutation:
NOT AUTHORIZED

Credential / App-permission mutation:
NOT AUTHORIZED

Production ProjectStateResolver / AuthorityCompiler wiring:
NOT AUTHORIZED

Real-project autonomous engineering:
NOT AUTHORIZED
```

Do not mark Slice 1.10 COMPLETE / ACCEPTED / CLOSED before independent closure evaluation returns ACCEPT.

## 9. Authorized finalization surface

Expected mutable paths are limited to:

```text
.relay/registry.json
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/TODO.md
docs/architecture/README.md
```

plus creation/registration of the immutable finalization records authorized here.

Additional status/navigation text may change only if inspection proves it directly contradicts the closure-ready truth.

No opportunistic cleanup.

## 10. Prohibited finalization surface

Do not modify:

```text
src/**
tests/**
pyproject.toml
uv.lock
.github/workflows/**
database schema/migrations
operational database state
repository settings
accepted immutable design/review/authority/acceptance records
```

No live canonical ref mutation, policy-binding execution, quarantine reconciliation, GitHub ruleset mutation, credential/App-permission mutation, production resolver/compiler wiring, AgentRuntime/provider/model execution, Slice 3.1 work, or real-project execution is authorized.

## 11. Required closure-ready validation

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

Additionally prove:

```text
registry artifact count == 354
registry paths unique
registry ordering valid
registered digests exact
canonical keys == 5

Build Plan revision == 149
Current Baseline revision == 166
Product Proposal revision == 65
TODO revision == 57

canonical main da966f... is ancestor
historical implementation 8003170f... is ancestor
implementation evaluation 0d151d11... is ancestor
Human acceptance bf038bf3... is ancestor
this close authority is ancestor
finalization handoff is ancestor

no src/** or tests/** path changed from da966f... during finalization

Slice 1.10 remains OPEN / CLOSURE-READY
Phase 3 remains OPEN
Slice 3.1 remains NOT OPEN / NOT AUTHORIZED
live promotion/runtime execution remains NOT AUTHORIZED
```

Exact-head CI must succeed.

## 12. Independent closure evaluation

The finalization executor must STOP after producing the closure-ready candidate.

The independent evaluator returns exactly:

```text
ACCEPT
REWORK
ESCALATE
```

No CLOSED state, Slice 3.1 opening, or canonical promotion is permitted before independent closure ACCEPT.

## 13. Conditional post-ACCEPT closed-state bookkeeping

If and only if the exact closure-ready candidate receives:

`RLY-S110-CLOSE-EVAL-001 — ACCEPT`

this authority also permits bounded closed-state bookkeeping.

First preserve/register the immutable closure-evaluation record.

Then advance exactly once more:

```text
Build Plan:
149 -> 150

Current Baseline:
166 -> 167

Product Proposal:
65 -> 66

TODO:
57 -> 58
```

After registering the closure evaluation:

```text
registry artifact count:
354 -> 355
```

and it remains 355 through closed-state living-projection replacement.

Closed-state controlling truth must say:

```text
Slice 1.10:
COMPLETE / ACCEPTED / CLOSED

Independent closure evaluation:
RLY-S110-CLOSE-EVAL-001 — ACCEPT

Exact accepted implementation:
8003170f56120640ab29eb776cc1b2ba53c66a5f

Phase 3:
OPEN

Slice 3.1:
ELIGIBLE TO OPEN / NOT OPEN / NOT AUTHORIZED

Phase 3 execution:
NOT AUTHORIZED until separate Slice 3.1 authority

Live canonical-promotion execution:
NOT AUTHORIZED by Slice closure

Production resolver/compiler wiring:
NOT AUTHORIZED

Real-project autonomous engineering:
NOT AUTHORIZED
```

Slice 1.10 closure removes the remaining prerequisite blocker for considering a separately authorized Slice 3.1 opening. It does not itself open or authorize Slice 3.1.

Rerun full validation and exact-head CI.

## 14. Conditional canonical promotion

After closure ACCEPT and green closed-state validation, fast-forward canonical `main` only if:

```text
remote main still equals:
da966f67676a227488ef216d388d405b5e383d93

closed-state lineage:
ahead of main
behind main by 0

required ancestry preserved
registry contract valid
exact-head CI green
```

Never force-update, rebase, squash, or rewrite accepted history.

If canonical main moved independently, STOP and reconcile instead of forcing promotion.

## 15. Authority boundary

```text
RLY-S110-CLOSE-AUTH-001 — AUTHORIZED

Technical acceptance:
COMPLETE

Finalization:
AUTHORIZED

Closure-ready candidate:
AUTHORIZED TO PRODUCE

Independent closure evaluation:
REQUIRED

Slice 1.10 CLOSED:
CONDITIONAL ON RLY-S110-CLOSE-EVAL-001 — ACCEPT

Canonical promotion:
CONDITIONAL ON CLOSURE ACCEPT + GREEN CLOSED-STATE VALIDATION + UNCHANGED MAIN

Slice 3.1:
NOT OPEN / NOT AUTHORIZED
ELIGIBLE ONLY AFTER SLICE 1.10 CLOSURE ACCEPT

Live promotion / policy-binding / reconciliation execution:
NOT AUTHORIZED

Production ProjectStateResolver / AuthorityCompiler wiring:
NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

**Technical acceptance != closure. Finalization authority != closure. Independent closure ACCEPT is required before CLOSED state or canonical promotion.**
