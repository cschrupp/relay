# Slice 1.7 — Finalization Execution Handoff

**Document class:** Execution handoff  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Authority:** `RLY-S17-CLOSE-AUTH-001 — AUTHORIZED`  
**Authority-recording commit:** `2ba54406ede23ea565fb3306b08474e31434ec67`

## Exact starting state

Finalization branch:

```text
finalization/1.7-manual-evaluation-acceptance
```

Branch ancestry before this handoff must preserve:

```text
canonical accepted-design main:
4717d44a05231fc1bd5f9fbd057714075d69c20b

implementation authority/handoff lineage:
f6676568d93ed50ab972191af8a6ab90cf6ec943

initial candidate:
38c4cda99164697be562bba610598423d9dbfbb7

second candidate:
c573051229ecb7714e7ff66b4155388ad953c56d

accepted technical candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

implementation evaluations:
RLY-S17-EVAL-001 — REWORK
RLY-S17-EVAL-002 — REWORK
RLY-S17-EVAL-003 — ACCEPT

final accepted evaluation record commit:
4c8f218d8ff5ef83fbddba526c2d7a4d2feb15ce

acceptance-lineage reconciliation:
7e2b4215c2775b67b8f5be008d49cad5c4166dca

Human technical acceptance:
RLY-S17-ACCEPT-001 — ACCEPTED
3bf20f07aa7a6cef0507daccfaf6f0cfe7ac3e87

finalization authority:
RLY-S17-CLOSE-AUTH-001 — AUTHORIZED
2ba54406ede23ea565fb3306b08474e31434ec67
```

Do not rebase or squash this lineage.

## Finalization objective

Produce one exact **closure-ready** Slice 1.7 candidate in which:

1. the accepted product/result remains byte-identical to `2fc1a762...` across the accepted 20-file implementation surface;
2. all Slice 1.7 authority/evaluation/acceptance provenance is present and registered as required;
3. the three living projections truthfully state technical acceptance and **closure-ready / still open pending closure evaluation**;
4. their registry revisions advance monotonically from the prior canonical revisions;
5. the registry transition and exact document digests validate;
6. the full quality suite passes;
7. GitHub Actions passes on the exact closure-ready SHA;
8. Phase 1 M0 remains pending;
9. Phase 2 remains not open;
10. agent execution remains unauthorized.

## Canonical prior registry state

Use canonical `main`:

```text
4717d44a05231fc1bd5f9fbd057714075d69c20b
```

as the prior canonical registry for transition validation.

Prior living revisions:

```text
Current Baseline: 43
Build Plan:       33
Product Proposal: 33
```

If all three living projections change for closure-ready state, advance them exactly once:

```text
Current Baseline: 44
Build Plan:       34
Product Proposal: 34
```

Each successor living revision requires a new ArtifactId, exact SHA-256 content digest, updated timestamp, and canonical-pointer advance. Do not mutate prior ArtifactIds in place.

## Records to preserve/register

At minimum preserve and register as repository convention requires:

```text
RLY-S17-OPEN-001
RLY-S17-DESIGN-AUTH-001
RLY-S17-DESIGN-EVAL-001 — REVISE
RLY-S17-DESIGN-EVAL-002 — REVISE
RLY-S17-DESIGN-EVAL-003 — REVISE
RLY-S17-DESIGN-EVAL-004 — ACCEPT
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED
RLY-S17-AUTH-001 — AUTHORIZED
RLY-S17-EVAL-001 — REWORK
RLY-S17-EVAL-002 — REWORK
RLY-S17-EVAL-003 — ACCEPT
RLY-S17-ACCEPT-001 — ACCEPTED
RLY-S17-CLOSE-AUTH-001 — AUTHORIZED
```

Do not alter the bytes of any existing immutable record.

The closure-evaluation record must not exist until an independent evaluator has reviewed the exact closure-ready SHA and returned `ACCEPT`.

## Closure-ready projection truth

Before closure evaluation, living projections must say, in substance:

```text
Slice 1.7:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted technical candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Independent implementation evaluation:
RLY-S17-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S17-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S17-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Phase 1 M0 hard-stop validation:
PENDING / NOT YET DECLARED COMPLETE

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Do **not** mark Slice 1.7 closed before the independent closure evaluator returns `ACCEPT`.

## Accepted implementation immutability check

Compare the closure-ready result against exact accepted candidate:

```text
2fc1a762e17f45fb1a3d866d8100f2c0c284b435
```

The following accepted implementation surface must remain byte-identical:

```text
pyproject.toml
src/relay_engine/board/models.py
src/relay_engine/board/render.py
src/relay_engine/board/service.py
src/relay_engine/board/web.py
src/relay_engine/domain/ids.py
src/relay_engine/governance/models.py
src/relay_engine/human_control/models.py
src/relay_engine/human_control/service.py
src/relay_engine/manual_evaluation/__init__.py
src/relay_engine/manual_evaluation/errors.py
src/relay_engine/manual_evaluation/models.py
src/relay_engine/manual_evaluation/service.py
src/relay_engine/persistence/__init__.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/store.py
tests/integration/test_manual_evaluation_sqlite.py
tests/integration/test_persistence_sqlite.py
tests/unit/test_github_store.py
tests/unit/test_repository_sync.py
```

Any difference is a hard stop. Do not silently repair product/test/tooling files during finalization.

Migration v5 must remain exactly the accepted migration; no v6 and no additional table are allowed.

## Finalization-only change surface

Finalization may change only repository governance/finalization material mechanically required for closure, principally:

```text
.relay/registry.json
docs/CURRENT_BASELINE.md
docs/BUILD_PLAN_V0_5.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/reviews/SLICE_1_7_FINALIZATION_AND_CLOSURE_AUTHORIZATION.md
docs/reviews/SLICE_1_7_FINALIZATION_HANDOFF.md
```

and, after an independent `ACCEPT`, the new immutable closure-evaluation record plus bounded living-projection/registry closure bookkeeping.

If another file appears necessary, stop and justify it before modifying it.

## Required validation

Run against the exact closure-ready SHA:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Also validate:

```text
all registered artifact digests
validate_registry_transition(previous_canonical_registry, closure_ready_registry)
repository contract tests
```

Obtain successful GitHub Actions CI on the exact closure-ready SHA.

Passing checks are evidence, not closure authority.

## Independent closure evaluation

After closure-ready validation, switch to an independent evaluator role and verify the exact subject SHA against `RLY-S17-CLOSE-AUTH-001`.

The evaluator must independently verify:

- exact accepted 20-file surface remains byte-identical to `2fc1a762...`;
- all implementation/rework/evaluation/acceptance lineage is preserved;
- migration v5 is unchanged and remains the highest migration;
- dependency declarations and lifecycle transition matrix have not changed;
- living projections and registry truthfully represent closure-ready state;
- all prior registered immutable/locked bytes remain unchanged;
- registry transition/digests validate;
- exact-SHA local checks and CI pass;
- Phase 1 M0 has not been falsely declared complete;
- Phase 2 remains not open;
- agent execution remains unauthorized;
- no AgentRuntime/OpenCode execution implementation was introduced.

Return only one governance outcome:

```text
ACCEPT
REWORK
ESCALATE
```

If and only if the result is `ACCEPT`, create:

```text
docs/reviews/SLICE_1_7_CLOSURE_EVALUATION.md
RLY-S17-CLOSE-EVAL-001 — ACCEPT
```

The record must name the exact closure-ready subject SHA and exact CI evidence.

## Post-evaluation closure

Only after `RLY-S17-CLOSE-EVAL-001 — ACCEPT`:

- advance the three living projections again from closure-ready to `COMPLETE / ACCEPTED / CLOSED` if their bytes change;
- advance corresponding registry revisions monotonically again, with new ArtifactIds and exact digests;
- register the closure-evaluation record;
- record the exact canonical closure commit;
- promote the preserved accepted closure lineage to `main` without force push or history rewriting;
- if later bookkeeping is required to write the canonical closure SHA into a living projection, record that as a distinct subsequent commit/revision;
- leave Phase 1 M0 validation pending until separately authorized/performed;
- leave Phase 2 NOT OPEN;
- leave agent execution NOT AUTHORIZED.

Do not conflate:

```text
closure-ready SHA
closure-evaluation-recording SHA
canonical closure commit SHA
final bookkeeping/main SHA
```

Report each distinctly.

## Hard stops

Stop and escalate if finalization would require:

- any change to the accepted 20-file implementation surface;
- any migration v6 or migration-v5 change;
- dependency changes;
- lifecycle/governance semantic changes;
- development-memory repository materialization;
- performing or declaring Phase 1 M0 hard-stop validation complete;
- opening Phase 2;
- Slice 2.1 work;
- agent execution;
- AgentRuntime/OpenCode execution or integration;
- rewriting immutable records;
- force-pushing or discarding accepted history;
- a non-monotonic registry transition;
- a closure-ready candidate that cannot pass exact-SHA CI.

## Final report

Return at minimum:

```text
prior canonical main SHA
finalization authority SHA
finalization handoff SHA
closure-ready SHA
closure evaluation ID/outcome and recording SHA
canonical closure commit SHA
final main SHA

accepted candidate preservation result
changed finalization-only files
living projection revision chain
registry transition validation result
registered artifact digest result
local quality results
exact-SHA GitHub Actions run(s)
model/reviewer provenance
deviations
new work discovered
Phase 1 M0 state
Phase 2 state
agent execution state
```

**Unblocked ≠ closed. Closure evaluation ACCEPT is required before canonical closure.**
