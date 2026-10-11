# Slice 1.8 — Finalization Execution Handoff

**Document class:** Immutable execution handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.8 — Governance Assurance Reference Model  
**Authority:** `RLY-S18-CLOSE-AUTH-001 — AUTHORIZED`

## Role and stop condition

```text
Execution role:
FINALIZATION / GOVERNANCE IMPLEMENTATION AGENT

Preferred executor:
Codex

Independent evaluator:
GPT-5.6 Sol
```

The executor performs bounded finalization only. It must stop after producing and pushing the exact closure-ready candidate plus evidence. It must not self-evaluate, close the Slice, or promote `main`.

## Exact starting state

```text
Repository:
cschrupp/relay

Finalization branch:
finalization/1.8-governance-assurance-reference-model

Canonical starting head:
a7cd87fea89e3b0273da1d0c0884336cc7857357

Accepted technical candidate:
35046bb378808a1325ecb84eace5aacd3040ca98

Accepted implementation evaluation:
RLY-S18-EVAL-002 — ACCEPT

Evaluation record commit:
11ccf7ec6f5a4c4359244e26e9944ac1bbc5a4e3

Human technical acceptance:
RLY-S18-ACCEPT-001 — ACCEPTED

Acceptance-lineage head:
3e7b2b18a12ca9b44ec92a4902d661b3be8d95cc

Canonical/accepted merge base:
a7cd87fea89e3b0273da1d0c0884336cc7857357
```

This handoff and its authority are recorded on a branch rooted at the exact canonical starting head. After that governance commit, the finalization lineage and acceptance lineage are distinct and must be reconciled by ancestry-preserving merge.

## Required reconciliation

Do not rebase, squash, cherry-pick/recreate, or manually copy the accepted lineage.

After fetching all refs:

```text
1. verify finalization branch started from exact canonical head;
2. verify acceptance-lineage head is exactly 3e7b2b18...;
3. merge the exact acceptance-lineage head into the finalization branch with history preservation;
4. resolve only documentation/registry conflicts required by this authority;
5. prove both the finalization-authority lineage and acceptance-lineage head are ancestors of the closure-ready result;
6. prove exact accepted candidate 35046bb... is an ancestor.
```

If any conflict requires changing accepted governance-assurance semantics, STOP and report.

## Semantic immutability

The following accepted semantic artifacts must remain byte-identical to candidate `35046bb378808a1325ecb84eace5aacd3040ca98` unless this handoff explicitly says otherwise:

```text
docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
docs/architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md
docs/references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md
docs/architecture/HUMAN_DECISION_SUPPORT.md
docs/architecture/AGENT_RUNTIME.md
```

Do not edit any accepted design, Human Authority, implementation handoff, evaluation, or acceptance record in place.

## Registry reconciliation

The canonical starting registry has 168 artifacts.

The acceptance lineage has 176 artifacts and includes the complete Slice 1.8 implementation/evaluation/acceptance provenance.

The authority/handoff lineage adds two immutable records.

The merge must preserve the union. Before new closure-ready living-projection revisions, the reconciled registry should therefore contain 178 distinct artifacts.

Then add exactly one new living revision for each authorized changed canonical projection:

```text
Build Plan:       88 -> 89
Current Baseline: 98 -> 99
Product Proposal: 46 -> 47
```

If all three advance exactly once, the expected closure-ready registry count is 181.

For every changed living projection:

- new ArtifactId;
- exact content digest;
- revision increment by exactly one;
- predecessor marked/superseded according to existing repository convention;
- matching canonical pointer advanced to the new record;
- no historical registry entry rewritten to fabricate state.

Preserve the existing five canonical keys. Do not create a new canonical key for the governance-assurance reference model.

## Closure-ready documentation

Update only what is necessary to truthfully represent:

```text
Slice 1.8:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted technical candidate:
35046bb378808a1325ecb84eace5aacd3040ca98

RLY-S18-EVAL-002:
ACCEPT

RLY-S18-ACCEPT-001:
ACCEPTED

RLY-S18-CLOSE-AUTH-001:
AUTHORIZED

Independent closure evaluation:
PENDING
```

At minimum inspect/update as necessary:

```text
docs/BUILD_PLAN_V0_6.md
docs/CURRENT_BASELINE.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
README.md
docs/README.md
docs/slices/README.md
```

Product Proposal revision 47 is explicitly authorized to correct the stale statements that Slice 1.8 implementation is unauthorized.

Do not open Slice 1.9 or Slice 1.10.

## Prohibited change surface

```text
src/**                         NO CHANGES
tests/**                       NO CHANGES
pyproject.toml                 NO CHANGES
uv.lock                        NO CHANGES
.github/workflows/**           NO CHANGES
schema/migrations              NO CHANGES
repository settings            NO CHANGES
accepted design records        NO CHANGES
accepted semantic model docs   NO SEMANTIC CHANGES
```

No new runtime capability, dependency, policy engine, profile engine, UI, adapter, telemetry collector, signing/attestation engine, or agent execution is authorized.

## Validation

Run on the exact closure-ready candidate:

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

Also perform explicit governance checks:

```text
canonical starting head is ancestor                     PASS required
acceptance-lineage head 3e7b2b18... is ancestor       PASS required
accepted candidate 35046bb... is ancestor              PASS required
accepted semantic artifacts byte-identical              PASS required
immutable/lockable records byte-identical               PASS required
registry union complete                                  PASS required
registry transition valid                                PASS required
canonical pointers valid                                 PASS required
all registered digests exact                             PASS required
five canonical keys preserved                           PASS required
Slice 1.9/1.10 unopened                                  PASS required
Phase 3 / real-project execution absent                  PASS required
```

Push the closure-ready branch and require exact-head GitHub Actions CI `SUCCESS`.

## Independent closure-review handoff

Return:

```text
finalization branch
closure-ready SHA
parents / ancestry proof
merge base
ahead / behind canonical start
accepted-candidate ancestry proof
acceptance-lineage ancestry proof
changed files
registry artifact count
living projection revisions
all local validation results
exact-head CI run ID / conclusion
working-tree status
```

Then STOP for GPT-5.6 Sol independent closure evaluation.

Do not create `RLY-S18-CLOSE-EVAL-001`, mark Slice 1.8 closed, or update `main`.

**Finalization authority != closure.**
