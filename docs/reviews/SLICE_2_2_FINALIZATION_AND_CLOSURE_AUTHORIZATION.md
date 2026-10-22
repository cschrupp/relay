# Slice 2.2 — Finalization and Closure Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Slice:** 2.2 — Role Contracts  
**Authority:** `RLY-S22-CLOSE-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes bounded Slice 2.2 finalization, independent closure evaluation, and the conditional post-ACCEPT canonical closure/promotion sequence defined by this record.

Technical acceptance is complete. This authority does not itself declare Slice 2.2 closed.

## Exact authority basis

```text
Canonical starting main:
0a0b415ceafd78401e6fa2cae24c208e0fe82a75

Accepted Role Contracts implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Accepted quality-repaired effective subject:
07bda21295d87602e2a2234622478551920c5014

Final independent implementation evaluation:
RLY-S22-IMPL-EVAL-003 — ACCEPT

Implementation evaluation record commit:
e9b43e9b853682c84a7c895616524befeb6ec04d

Human technical acceptance:
RLY-S22-ACCEPT-001 — ACCEPTED

Acceptance-lineage head:
7ea9beefb38dc39a74125b86d737de57dd1ae33b

Separate repair authority:
RLY-QUALITY-RUFF-MARKDOWN-REPAIR-AUTH-001 — AUTHORIZED

Repair-authority commit:
74a63434f72a0c3b9d4a6fe048949bf91251f0c9

Repository-quality repair evaluation:
RLY-QUALITY-RUFF-MARKDOWN-REPAIR-EVAL-001 — ACCEPT

Exact-head quality CI:
39710508282 — SUCCESS
```

The acceptance lineage is a direct descendant of canonical starting main. The repair-authority commit is a sibling governance record and is not an ancestor of the Human-acceptance head; finalization MUST preserve it explicitly as a separate ancestor.

## Finalization branch

`finalization/2.2-role-contracts` starts exactly at canonical main `0a0b415ceafd78401e6fa2cae24c208e0fe82a75` before this authority/handoff lineage is appended.

## Required ancestry preservation

The closure-ready result must preserve as ancestors: canonical starting main `0a0b415c...`; acceptance head `7ea9beef...`; accepted implementation `4400bd1d...`; accepted repair candidate `07bda212...`; final implementation evaluation `e9b43e9b...`; and repair-authority commit `74a63434...`.

Use true ancestry-preserving merges. Rebase, squash, cherry-pick recreation, manual recreation, and history rewriting are prohibited. If a conflict requires changing accepted Role Contracts source/tests, accepted Ruff repair bytes, or immutable governance records, STOP.

## Accepted implementation immutability

The following paths must remain byte-identical to `4400bd1da0db04e41077c3a6ed1c16d258104ba5`:

```text
src/relay_engine/role_contracts/__init__.py
src/relay_engine/role_contracts/models.py
src/relay_engine/role_contracts/evaluation.py
tests/unit/test_role_contract_models.py
tests/unit/test_role_contract_evaluation.py
tests/unit/test_role_contract_architecture.py
```

`pyproject.toml` must remain byte-identical to the accepted repair candidate `07bda21295d87602e2a2234622478551920c5014`. Do not modify `uv.lock` or `.github/workflows/ci.yml`.

## Registry reconciliation basis

At the Human-acceptance head the registry has 258 artifacts. Build Plan is revision 134; Current Baseline 143; Product Proposal 50; TODO 41.

The latest registry-changing ancestor is `f1c4accd18c499f7c620a918204cbdaa9c063ea0`. Between that registry anchor and the acceptance head, 35 new documentation artifacts were added without registry advancement.

Finalization must additionally register the separate Ruff repair authority, this close authority, and the finalization handoff. Therefore Stage A is exactly:

```text
258 existing registry artifacts
+35 unregistered accepted-lineage documentation artifacts
+1 Ruff repair authority
+1 Slice 2.2 close authority
+1 Slice 2.2 finalization handoff
=296 artifacts
```

Stage A must preserve unique paths, normative ordering, exact digests, all five canonical keys, and all immutable/lockable history.

## Closure-ready living projections

The accepted lineage contains stale Slice 2.2 status. Finalization is authorized to advance exactly once:

```text
Build Plan:       134 -> 135
Current Baseline: 143 -> 144
Product Proposal: 50  -> 51
TODO:             41  -> 42
```

Each changed living projection uses the same path, a new ArtifactId, revision +1, exact SHA-256 digest, artifact_class LIVING_PROJECTION, artifact_state CURRENT, supersedes null, superseded_by null. Move canonical pointers for Build Plan, Current Baseline, and Product Proposal. TODO remains a current living artifact without a canonical pointer. Stage-B registry cardinality remains 296.

## Closure-ready truth

Before independent closure evaluation the exact closure-ready subject must state:

```text
Slice 2.2:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted Role Contracts implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Accepted quality-repaired effective subject:
07bda21295d87602e2a2234622478551920c5014

Independent implementation evaluation:
RLY-S22-IMPL-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S22-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S22-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Production Role Contract wiring:
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Do not mark Slice 2.2 COMPLETE / ACCEPTED / CLOSED before independent closure evaluation returns ACCEPT.

## Authorized finalization work

This authority permits only: preserve this authority/handoff lineage; ancestry-preserving merge of exact acceptance head `7ea9beef...`; ancestry-preserving merge of exact repair-authority commit `74a63434...`; reconcile Stage-A registry to 296; advance the four living projections to closure-ready truth; update directly contradictory status/navigation docs only if inspection proves necessary; run complete repository-contract and quality validation; produce one closure-ready candidate; STOP for independent closure evaluation.

Expected primary closure-ready changes are `.relay/registry.json`, `docs/BUILD_PLAN_V0_6.md`, `docs/CURRENT_BASELINE.md`, `docs/PRODUCT_PROPOSAL_V0_5.md`, and `docs/TODO.md`. `README.md`, `docs/README.md`, or `docs/slices/README.md` may change only if they directly contradict Slice 2.2 closure-ready truth.

## Prohibited finalization surface

Do not modify `src/**`, `tests/**`, `uv.lock`, `.github/workflows/**`, database schema/migrations, operational DB state, accepted Slice 2.2 design/implementation/evaluation records, Human technical acceptance, or accepted repair evaluation. `pyproject.toml` may only arrive unchanged through the accepted repair lineage.

No production Role Contract wiring, Work Packet implementation, workspace enforcement, provider/model execution, lifecycle mutation, Slice 2.3/2.4 work, Phase 3 work, or real-project agent execution is authorized.

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

Also prove: Stage-A count 296; Stage-B count 296; unique paths; normative ordering; all registered digests exact; exactly five canonical keys; Build Plan target revision 135; Current Baseline target 144; Product Proposal target 51; TODO current revision 42; canonical main ancestor; acceptance-head ancestor; repair-authority ancestor; accepted implementation bytes preserved; accepted `pyproject.toml` bytes preserved; immutable/lockable records preserved; Slice 2.3/2.4 and Phase 3 remain unauthorized; no real-project execution.

Exact-head GitHub Actions CI must succeed. Passing checks are evidence only.

## Independent closure evaluation and conditional promotion

The finalization executor must STOP after producing the closure-ready candidate. The independent evaluator returns exactly ACCEPT, REWORK, or ESCALATE.

If and only if the exact closure-ready candidate receives `RLY-S22-CLOSE-EVAL-001 — ACCEPT`, this authority also permits bounded post-ACCEPT closure bookkeeping: preserve the closure-evaluation record; update the four living projections from CLOSURE-READY to COMPLETE / ACCEPTED / CLOSED with next one-step revisions and exact registry updates; preserve all ancestry; rerun validation and exact-head CI; fast-forward canonical `main` only if remote main still equals `0a0b415ceafd78401e6fa2cae24c208e0fe82a75` and the closed-state lineage is ahead with zero commits behind.

Canonical promotion before independent closure evaluation ACCEPT is forbidden. Never force-update, rebase, squash, or rewrite canonical history.

## Not authorized

This authority does not authorize changing accepted implementation or repair bytes, closure without independent evaluation, production Role Contract integration, operational DB/lifecycle mutation, Slice 2.3/2.4 opening, Phase 3 opening, or real-project agent execution.

**Technical acceptance != closure. Finalization authority != closure. Independent closure ACCEPT is required before canonical promotion.**