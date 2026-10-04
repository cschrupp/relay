# Slice 1.6 — Finalization Execution Handoff

**Document class:** Execution handoff  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Authority:** `RLY-S16-CLOSE-AUTH-001 — AUTHORIZED`  
**Authority-recording commit:** `4b5e32844753224fd2ac9f8c0be475b67ea8f6a8`

## Exact starting state

Finalization branch:

```text
finalization/1.6-human-authorization-decision-gates
```

Branch ancestry before this handoff preserves:

```text
canonical implementation-authorization main:
5544f93fb90184909bf6e710bcca54643f689a39

accepted candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

accepted independent evaluation:
15e0899a0947c108aa35b417ae1bcfa427e80301

acceptance-lineage reconciliation:
bd59782a597181fa5d64ff4e1ab8cacaab967bea

Human technical acceptance:
b3fb25d23121ca9a249c56376a8f208bbaf6a1d1

finalization authority:
4b5e32844753224fd2ac9f8c0be475b67ea8f6a8
```

Do not rebase or squash this lineage.

## Finalization objective

Produce one exact **closure-ready** Slice 1.6 candidate in which:

1. the accepted product result remains byte-identical to `a62493c...` across every authorized product file;
2. all Slice 1.6 authority/evaluation/acceptance provenance is present and registered as required;
3. the three living projections truthfully state technical acceptance and **closure-ready / still open pending closure evaluation**;
4. their registry revisions advance monotonically from the prior canonical revisions;
5. the registry transition and exact document digests validate;
6. the full local quality suite passes;
7. GitHub Actions passes on the exact closure-ready SHA;
8. no Slice 1.7 or agent-execution work is introduced.

## Canonical prior registry state

Use `5544f93fb90184909bf6e710bcca54643f689a39` as the prior canonical registry for transition validation.

Expected prior living revisions:

```text
Current Baseline: 39
Build Plan:       29
Product Proposal: 29
```

The closure-ready transition should therefore advance changed living projections exactly once:

```text
Current Baseline: 40
Build Plan:       30
Product Proposal: 30
```

Each successor living revision requires a new ArtifactId, exact SHA-256 content digest, updated timestamp, and canonical-pointer advance. Do not mutate prior ArtifactIds in place.

## Records to carry/register

At minimum preserve and register as repository convention requires:

```text
RLY-S16-AUTH-001
RLY-S16-EVAL-001 — REWORK
RLY-S16-EVAL-002 — ACCEPT
RLY-S16-ACCEPT-001 — ACCEPTED
RLY-S16-CLOSE-AUTH-001 — AUTHORIZED
```

Do not alter the bytes of any existing immutable record.

The follow-up closure evaluation record must not exist until an independent evaluator has reviewed the exact closure-ready SHA and returned `ACCEPT`.

## Closure-ready projection truth

Before closure evaluation, living projections must say, in substance:

```text
Slice 1.6:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted technical candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Independent implementation evaluation:
RLY-S16-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S16-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S16-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Do **not** mark Slice 1.6 closed before the independent closure evaluator returns `ACCEPT`.

## Product immutability check

Compare the closure-ready result against exact accepted candidate `a62493c...`.

All production and implementation-test files introduced/modified by the accepted Slice 1.6 product candidate must be byte-identical. The accepted implementation change surface is the 13-file product/test set from the implementation evaluation.

Any product-code difference is a hard stop unless it is proven to be unrelated pre-existing canonical history already present before the candidate; do not silently repair product code during finalization.

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

## Independent closure evaluation

After closure-ready validation, switch roles to an independent closure evaluator and verify the exact subject SHA against `RLY-S16-CLOSE-AUTH-001`.

Return only one governance outcome:

```text
ACCEPT
REWORK
ESCALATE
```

If and only if the result is `ACCEPT`, create:

```text
docs/reviews/SLICE_1_6_CLOSURE_EVALUATION.md
RLY-S16-CLOSE-EVAL-001 — ACCEPT
```

The evaluation must name the exact closure-ready subject SHA and the exact CI evidence.

## Post-evaluation closure

Only after `RLY-S16-CLOSE-EVAL-001 — ACCEPT`:

- advance the three living projections again from closure-ready to `COMPLETE / ACCEPTED / CLOSED` if their bytes change;
- advance corresponding registry revisions monotonically again, with new ArtifactIds and exact digests;
- register the closure-evaluation record;
- record the exact canonical closure commit;
- promote the preserved accepted closure lineage to `main` without force push or history rewriting;
- leave Slice 1.7 NOT OPEN and agent execution NOT AUTHORIZED.

Do not conflate the closure-ready SHA, the closure-evaluation-recording SHA, the canonical closure commit, and any later bookkeeping commit that records the canonical closure SHA in a living projection. Report all exact SHAs distinctly.

## Hard stops

Stop and escalate if finalization would require:

- any product-code change;
- schema migration or dependency change;
- lifecycle/governance semantic change;
- opening Slice 1.7;
- implementing Slice 1.7 evaluation/acceptance behavior;
- agent execution or AgentRuntime/OpenCode implementation;
- rewriting immutable records;
- force-pushing or discarding accepted history;
- a non-monotonic registry transition;
- a closure-ready candidate that cannot pass exact-SHA CI.

## Final report

Return at minimum:

```text
prior canonical main SHA
finalization authority SHA
closure-ready SHA
closure evaluation ID/outcome and recording SHA
canonical closure commit SHA
final main SHA

accepted product candidate preservation result
changed finalization-only files
living projection revision chain
registry transition validation result
registered artifact digest result
local quality results
exact-SHA GitHub Actions run(s)
model/reviewer provenance
deviations
new work discovered
Slice 1.7 state
agent execution state
```

**Unblocked ≠ closed. Closure evaluation ACCEPT is required before canonical closure.**
