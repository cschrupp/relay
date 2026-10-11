# Slice 1.9 — Finalization and Closure Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Authority:** `RLY-S19-CLOSE-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes bounded Slice 1.9 finalization, independent closure evaluation, and the conditional post-ACCEPT canonical closure/promotion sequence defined by this record.

Technical acceptance is already complete. This authority does not itself declare Slice 1.9 closed.

## Exact authority basis

```text
Canonical starting main:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

Accepted combined-design subject:
03d6efecf9ad4aaec0c5967b9486650399d0a492

Accepted technical candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Independent implementation evaluation:
RLY-S19-EVAL-003 — ACCEPT

Evaluation record commit:
43ebfdc57b7fe70ce943dc688fe0068fc8a4f659

Human technical acceptance:
RLY-S19-ACCEPT-001 — ACCEPTED

Acceptance-lineage head:
52e6c95d94d55dc8de1d1605f8490420b384ad79

Candidate exact-head CI:
38170054185 — SUCCESS

Evaluation-record CI:
38170877228 — SUCCESS

Human-acceptance record CI:
38171824138 — SUCCESS
```

The exact acceptance lineage is a direct descendant of canonical starting main. Finalization authority is intentionally recorded on a separate branch rooted at canonical main, then reconciled with the exact acceptance lineage by an ancestry-preserving merge.

## Finalization branch

```text
finalization/1.9-human-decision-support-governance-review-surface
```

The branch MUST start exactly at canonical main `7e690f9fe22b34226fff2d3364d1ed94b91dc9f7` before this authority/handoff lineage is appended.

## Preserved accepted lineage

Finalization must preserve the complete reachable history containing:

```text
77ad34cf47828464a430ebdbecf1b816f158ae55
    accepted technical implementation candidate

43ebfdc57b7fe70ce943dc688fe0068fc8a4f659
    RLY-S19-EVAL-003 — ACCEPT

52e6c95d94d55dc8de1d1605f8490420b384ad79
    RLY-S19-ACCEPT-001 — ACCEPTED
```

The prior implementation candidates and REWORK evaluations in that ancestry must remain reachable and immutable.

## Accepted implementation immutability

Finalization must not redesign or alter the technically accepted Slice 1.9 implementation. In particular, the exact accepted bytes under the implementation/code/test surface must be preserved unless a closure evaluator later identifies an explicit finalization defect requiring separate bounded rework authority.

Accepted semantic/design/authority/evaluation records are immutable and must remain byte-preserved.

## Authorized finalization work

This authority permits only bounded closure preparation:

- create/use the finalization branch rooted at exact canonical main;
- preserve this authority record and its finalization handoff;
- merge exact acceptance-lineage head `52e6c95d94d55dc8de1d1605f8490420b384ad79` into the finalization lineage with true ancestry preservation;
- do not rebase, squash, cherry-pick/recreate, or copy the accepted implementation history;
- reconcile `.relay/registry.json` according to current schema-v1 path identity and living-projection rules;
- update only living status/navigation/projection documents necessary to state the current Slice 1.9 closure-ready truth;
- correct the stale pre-opening/pre-implementation wording in Slice 1.9 status/navigation documents;
- preserve all accepted production/runtime/test bytes from candidate `77ad34cf47828464a430ebdbecf1b816f158ae55`;
- run the frozen quality and repository-contract suites;
- push an exact closure-ready candidate and stop for independent GPT-5.6 Sol closure evaluation.

## Registry mechanics

Canonical main currently contains 180 registered artifacts.

The Human-accepted Slice 1.9 lineage contains 190 registered artifacts.

This finalization authority and its handoff add two distinct immutable records to the canonical-rooted finalization lineage.

After ancestry-preserving merge/reconciliation and before living-projection advancement, the valid Stage-A registry MUST therefore contain:

```text
accepted-lineage artifacts: 190
+ finalization authority:     1
+ finalization handoff:       1
= Stage-A total:            192
```

Artifact paths must remain unique and normatively ordered.

For LIVING_PROJECTION updates, Relay schema v1 uses replacement at the same path:

```text
same path
new ArtifactId
revision + 1
new exact SHA-256 content digest
artifact_state = CURRENT
supersedes = null
superseded_by = null
canonical pointer moves to the new ArtifactId/revision
```

Do not retain duplicate living revisions in the current registry. Historical living revisions remain reconstructable through Git history.

Therefore Stage-B closure-ready registry cardinality remains 192.

## Authorized closure-ready living-projection advancement

Current accepted-lineage/canonical revisions are:

```text
Build Plan:       90
Current Baseline: 100
Product Proposal: 48
```

Finalization is authorized to advance exactly once to:

```text
Build Plan:       90 -> 91
Current Baseline: 100 -> 101
Product Proposal: 48 -> 49
```

Each update must use a new ArtifactId, exact digest, one-step revision increment, and matching canonical pointer.

## Closure-ready truth

Before independent closure evaluation, the exact closure-ready result must state:

```text
Slice 1.9:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted technical candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Independent implementation evaluation:
RLY-S19-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S19-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S19-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Slice 1.10:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Do not mark Slice 1.9 COMPLETE / ACCEPTED / CLOSED before independent closure evaluation returns ACCEPT.

## Expected closure-ready documentation surface

Inspect and update only as necessary:

```text
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE.md
README.md
docs/README.md
docs/slices/README.md
.relay/registry.json
```

Additional status/navigation files may be updated only if inspection proves they contain stale Slice 1.9 status that would contradict closure-ready truth.

## Prohibited finalization surface

During closure preparation, do NOT modify:

```text
src/**
tests/**
pyproject.toml
uv.lock
.github/workflows/**
database schema/migrations
repository settings
accepted design records
implementation authority/handoff records
implementation evaluation records
Human technical acceptance record
```

No GovernanceProfile engine, Protected Verification Asset enforcement, provider/model execution, free-form Q&A, telemetry collection, persistence feature, Slice 1.10 work, Phase 3 work, or real-project agent execution is authorized.

## Required closure-ready validation

On the exact closure-ready SHA:

```text
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

- canonical starting main is an ancestor;
- finalization authority/handoff lineage is an ancestor;
- exact acceptance-lineage head is an ancestor;
- exact accepted technical candidate is an ancestor;
- exact accepted implementation/code/test bytes are preserved;
- immutable/lockable historical records are byte-preserved;
- Stage-A and Stage-B registries parse and satisfy repository contract;
- artifact paths are unique and normatively ordered;
- all registered digests are exact;
- all five canonical keys are preserved;
- canonical pointers match the new living projection revisions;
- Slice 1.10 remains unopened/unauthorized;
- Phase 3 and real-project execution remain unauthorized.

Exact-head GitHub Actions CI must succeed on the closure-ready SHA.

Passing validation is engineering evidence only.

## Independent closure evaluation and conditional promotion

The finalization executor must STOP after producing the closure-ready candidate.

The independent evaluator must return one of:

```text
ACCEPT
REWORK
ESCALATE
```

If and only if the exact closure-ready candidate receives `RLY-S19-CLOSE-EVAL-001 — ACCEPT`, this authority also permits the bounded post-ACCEPT closure bookkeeping sequence:

- freeze the immutable closure-evaluation record;
- update the living status projections from CLOSURE-READY to COMPLETE / ACCEPTED / CLOSED, with the next one-step living revisions and exact registry/canonical-pointer updates;
- preserve accepted implementation and closure-ready ancestry;
- run exact-head validation/CI on the final closed-state head;
- fast-forward canonical `main` only if main still equals the expected canonical starting head and the closed-state lineage is ahead with zero commits behind;
- never force-update, rebase, squash, or rewrite canonical history.

Canonical promotion before independent closure evaluation ACCEPT is forbidden.

## Not authorized

This authority does not authorize closure without independent evaluation, changes to the accepted implementation, new feature work, Slice 1.10 opening, Phase 3 opening, or real-project agent execution.

**Technical acceptance != closure. Finalization authority != closure. Closure evaluation ACCEPT is required before canonical promotion.**