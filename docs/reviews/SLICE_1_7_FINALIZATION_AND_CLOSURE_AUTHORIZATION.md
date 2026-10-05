# Slice 1.7 — Finalization and Closure Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Authority ID:** `RLY-S17-CLOSE-AUTH-001`

## Human Authority decision

The Human Authority explicitly authorizes bounded finalization and independent closure evaluation of Slice 1.7 after technical acceptance of the exact implementation result:

```text
2fc1a762e17f45fb1a3d866d8100f2c0c284b435
```

The authorization follows:

```text
RLY-S17-EVAL-003 — ACCEPT
RLY-S17-ACCEPT-001 — ACCEPTED
```

Independent accepted implementation evaluation record commit:

```text
4c8f218d8ff5ef83fbddba526c2d7a4d2feb15ce
```

Human technical acceptance commit:

```text
3bf20f07aa7a6cef0507daccfaf6f0cfe7ac3e87
```

Provenance-preserving acceptance-lineage reconciliation commit:

```text
7e2b4215c2775b67b8f5be008d49cad5c4166dca
```

Canonical `main` immediately before this finalization sequence is:

```text
4717d44a05231fc1bd5f9fbd057714075d69c20b
```

That canonical branch contains the synchronized Slice 1.7 accepted-design state. The implementation authorization, accepted implementation, all three implementation evaluations, and Human technical acceptance are preserved through the acceptance lineage above. Finalization must preserve that ancestry without history rewriting.

## Authorized work

This authority permits only bounded Slice 1.7 finalization and closure work:

- preserve the exact accepted technical result `2fc1a762e17f45fb1a3d866d8100f2c0c284b435` without product-code modification;
- preserve `RLY-S17-AUTH-001`, `RLY-S17-EVAL-001`, `RLY-S17-EVAL-002`, `RLY-S17-EVAL-003`, and `RLY-S17-ACCEPT-001` in canonical history;
- preserve the implementation-model provenance deviation and accepted Pyright configuration deviation already recorded by the accepted evaluations/acceptance;
- reconcile any remaining canonical documentation lineage without rewriting existing history;
- synchronize `docs/CURRENT_BASELINE.md`, `docs/BUILD_PLAN_V0_5.md`, and `docs/PRODUCT_PROPOSAL_V0_5.md` to the technical-acceptance / closure-ready state;
- advance the corresponding living-projection revisions in `.relay/registry.json` using new ArtifactIds, exact content digests, monotonic revision increments, and canonical pointers;
- register missing accepted Slice 1.7 immutable records required for complete repository provenance, including implementation authorization/handoff, implementation evaluations, Human acceptance, and this authority record, without altering earlier immutable records;
- validate the registry transition from the prior canonical registry;
- run the full required quality suite on the exact closure-ready candidate SHA;
- obtain successful GitHub Actions CI on that exact SHA;
- perform an independent Slice 1.7 closure evaluation against the exact closure-ready SHA;
- record `RLY-S17-CLOSE-EVAL-001` only if that independent evaluation returns `ACCEPT`;
- after accepted closure evaluation, advance canonical living projections to `COMPLETE / ACCEPTED / CLOSED`, promote the accepted closure lineage to `main`, and record the exact canonical closure head.

## Required reconciliation invariants

Finalization must preserve all of the following facts:

```text
Accepted design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authorization:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Initial implementation candidate:
38c4cda99164697be562bba610598423d9dbfbb7

Initial implementation evaluation:
RLY-S17-EVAL-001 — REWORK

Second implementation candidate:
c573051229ecb7714e7ff66b4155388ad953c56d

Second implementation evaluation:
RLY-S17-EVAL-002 — REWORK

Accepted technical candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Independent accepted implementation evaluation:
RLY-S17-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S17-ACCEPT-001 — ACCEPTED
```

The complete rework lineage is accepted provenance and must not be squashed away or misrepresented as a single unevaluated implementation commit.

The accepted implementation includes exactly migration v5 for:

```text
slice_results
manual_evaluations
```

No migration v6 or additional Slice 1.7 persistence table may be introduced during finalization.

Implementation model provenance remains historical:

```text
Preferred implementation model:
GPT-5.6 Luna

Executing implementation model:
Codex / GPT-6 family
exact runtime variant not exposed
```

The accepted two-line Pyright `.venv` configuration adjustment is preserved as accepted tooling configuration provenance and must not be altered during finalization absent separate authority.

## Accepted product change surface

Relative to authorized baseline `4717d44a...`, the accepted implementation comprises exactly the 20 changed files in candidate `2fc1a762...`, including production code, integration/unit tests, and the accepted `pyproject.toml` Pyright configuration adjustment.

Finalization must verify those accepted bytes remain unchanged. Product/code/test/tooling differences after the accepted candidate are a hard stop unless they are exclusively finalization metadata/documentation outside that accepted 20-file surface.

## Registry transition requirements

Prior canonical living-projection revisions at `4717d44a...` are:

```text
Current Baseline: 43
Build Plan:       33
Product Proposal: 33
```

For each changed living projection:

- create a new ArtifactId;
- increment the logical artifact revision by exactly one from the prior canonical revision;
- store the exact SHA-256 digest of the new document bytes;
- preserve artifact class `LIVING_PROJECTION` and state `CURRENT`;
- advance the matching canonical pointer to the new ArtifactId/revision;
- do not mutate a previously registered living revision in place.

Expected closure-ready revisions, if all three living projections change exactly once, are:

```text
Current Baseline: 44
Build Plan:       34
Product Proposal: 34
```

New immutable authority/evaluation/acceptance records may be appended with new ArtifactIds and revision `1` as repository convention requires.

Previously registered immutable or locked records must remain byte-for-byte immutable under `validate_registry_transition`.

The transition must pass repository-contract validation before closure evaluation.

## Required closure-ready quality evidence

Before independent closure evaluation, the exact finalized SHA must pass:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Also validate all registered artifact digests, registry transition semantics, and repository-contract tests.

GitHub Actions CI must succeed on the exact closure-ready SHA.

Passing checks are evidence only. They do not themselves close the Slice.

## Independent closure evaluation

The closure evaluator must independently verify at minimum:

- accepted candidate `2fc1a762...` is preserved as an ancestor and all 20 accepted changed files are byte-identical to that exact candidate;
- `RLY-S17-AUTH-001`, `RLY-S17-EVAL-001`, `RLY-S17-EVAL-002`, `RLY-S17-EVAL-003`, `RLY-S17-ACCEPT-001`, and this authority record are durably present;
- canonical accepted-design history and implementation authorization/evaluation/acceptance histories remain preserved without rewriting;
- migration v5 remains exactly the accepted migration, with no v6 or additional table;
- living projections truthfully state Slice 1.7's accepted/closure-ready or closed status appropriate to the evaluation stage;
- `.relay/registry.json` matches exact document bytes and passes transition validation;
- no historical immutable/locked record was edited in place;
- no Phase 1 M0 hard-stop completion was declared;
- no Phase 2 work was opened or introduced;
- no agent execution / AgentRuntime / OpenCode execution implementation was introduced;
- no product-code, test, schema, dependency, lifecycle, or governance semantic change occurred after the accepted candidate except explicitly authorized finalization metadata/documentation;
- exact-SHA quality evidence and GitHub Actions CI are successful.

The evaluator returns only:

```text
ACCEPT
REWORK
ESCALATE
```

Closure may be recorded only after `ACCEPT`.

## Not authorized

This authority does **not** authorize:

- changing the accepted Slice 1.7 production implementation or tests;
- changing migration v5, adding migration v6, or adding persistence tables;
- redesigning manual evaluation, technical acceptance, accepted-result promotion, Human Action Basis, or REWORK semantics;
- dependency changes or lifecycle transition-matrix changes;
- repository mutation for development-memory materialization;
- declaring the separate Phase 1 M0 hard-stop/dogfood validation complete;
- starting or performing Phase 1 M0 dogfood validation beyond documentation of its still-pending state;
- opening Phase 2;
- Slice 2.1 design or implementation;
- agent execution;
- AgentRuntime/OpenCode execution or integration;
- broad authentication/RBAC/multi-user work;
- unrelated refactoring or toolchain changes;
- rewriting historical authority, design, implementation, evaluation, or acceptance records.

Any such need is a hard stop and requires separate Human Authority.

## Hard stop

```text
Slice 1.7 technical result:
ACCEPTED

Exact accepted candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Slice 1.7 finalization / closure evaluation:
AUTHORIZED

Independent closure evaluation:
PENDING

Canonical closure:
NOT YET RECORDED

Phase 1 M0 hard-stop validation:
PENDING / NOT YET DECLARED COMPLETE

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ closed. Closure evaluation ACCEPT is required before canonical closure.**
