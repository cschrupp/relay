# Slice 2.1 Finalization Execution Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-09  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Authority:** `RLY-S21-CLOSE-AUTH-001 — AUTHORIZED`

## Exact starting state

Finalization branch:

```text
finalization/2.1-agent-runtime-contract
```

Canonical starting head:

```text
a9f6742c9f8af0b2f089f16fdeb3111ca34af793
```

Exact accepted candidate:

```text
4f785f08576e465cd0aa278f927fa4b7253e3f49
```

Merge base:

```text
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22
```

Do not rebase, squash, cherry-pick into recreated history, or manually recreate candidate changes. Create the finalization branch from the exact canonical starting head and merge the exact candidate as a real merge. Afterward verify:

```text
canonical basis a9f6742c9f8af0b2f089f16fdeb3111ca34af793 is an ancestor: PASS
accepted candidate 4f785f08576e465cd0aa278f927fa4b7253e3f49 is an ancestor: PASS
```

The complete candidate implementation lineage from `aaec399b...` through `c947cf6...`, `ded3ed0...`, `5df1add...`, `f9a4790...`, and `4f785f0...` must remain intact and reachable.

## Accepted implementation immutability check

Compare each listed path in the merge result directly with candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49`. All must be byte-identical:

```text
pyproject.toml
uv.lock
src/relay_engine/agent_runtime/__init__.py
src/relay_engine/agent_runtime/errors.py
src/relay_engine/agent_runtime/models.py
src/relay_engine/agent_runtime/opencode.py
src/relay_engine/agent_runtime/protocol.py
tests/unit/test_agent_runtime_contract.py
tests/unit/test_agent_runtime_models.py
tests/unit/test_board_web.py
tests/unit/test_opencode_runtime.py
```

A mismatch is a hard stop. Do not edit, reformat, or otherwise alter any of these files during finalization.

## Finalization-only surface and projections

The finalization branch may add only the exact accepted candidate lineage and the records/projections required by this authority. Do not add product behavior, tests, dependencies, schema, or unrelated refactors.

At canonical basis `a9f6742...`, registry revisions are:

```text
Build Plan:       76
Current Baseline: 86
Product Proposal: 36
```

Change only projections that need updating to state the closure-ready, still-open result. For each changed living projection, use a new ArtifactId, increment its logical revision by exactly one, calculate the exact content digest, update its timestamp, and move the canonical pointer. Do not mutate an existing immutable/locked artifact or reuse a living ArtifactId for changed bytes. Preserve every unrelated registry entry.

Closure-ready projections must state:

```text
Slice 2.1:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Human technical acceptance:
RLY-S21-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S21-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Slice 2.2:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Do not mark Slice 2.1 closed, create a closure-evaluation record, or promote the closure-ready result to `main` before independent closure evaluation returns `ACCEPT`.

## Validation

On the exact closure-ready SHA, run:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Also:

- run repository-contract tests;
- validate every registered artifact digest and every canonical pointer;
- validate the registry transition from the exact canonical registry at `a9f6742...`;
- verify the exact closure-ready SHA and its ancestry;
- require GitHub Actions CI `SUCCESS` for that exact SHA.

Passing checks are evidence only; they do not close the Slice.

## Independent closure evaluation handoff

Return the exact closure-ready SHA and evidence for independent review of:

- both-parent ancestry and the full accepted implementation lineage;
- byte identity of all eleven accepted paths;
- design, implementation authorization, rework/evaluation, live sidecar, and Human technical acceptance records;
- immutable/locked record integrity;
- truthful closure-ready projections and valid registry transition/digests;
- full local quality checks and exact-head CI;
- absence of unauthorized Slice 2.2, Phase 3, or real-project execution work.

The independent evaluator returns only `ACCEPT`, `REWORK`, or `ESCALATE`. Stop after returning the closure-ready evidence. No self-evaluation, acceptance, closure, or promotion is authorized for the evidence operator.
