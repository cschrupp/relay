# Slice 1.5 — Finalization and Closure Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.5 — Board Projection  
**Authority ID:** `RLY-S15-CLOSE-AUTH-001`

## Human Authority decision

The Human Authority explicitly authorizes bounded finalization and closure of Slice 1.5 after technical acceptance of the exact implementation result:

```text
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
```

The authorization follows:

```text
RLY-S15-EVAL-001 — ACCEPT
RLY-S15-ACCEPT-001 — ACCEPTED
```

Independent evaluation commit:

```text
ea26e0ae717e873e4b3ded27f1a8e9b0b278d7be
```

Human technical acceptance commit:

```text
1f0c6991268440982eef8b6d0f8b5abcdd4616f4
```

Canonical `main` immediately before this finalization sequence remains:

```text
2789b248085d7772abed80448f8b6bc1ce6de483
```

That canonical branch contains the separately recorded implementation authorization lineage, including `RLY-S15-AUTH-001`. The accepted implementation/evaluation/acceptance lineage and canonical-main governance lineage must both be preserved during reconciliation; neither history may be rewritten.

## Authorized work

This authority permits only bounded Slice 1.5 finalization and closure work:

- reconcile the accepted candidate lineage with canonical `main` while preserving both Git histories;
- preserve the exact accepted technical result `ff8df665f36afe60a2d44ee1ed0d735a0dcbc230` without product-code modification;
- carry forward `RLY-S15-AUTH-001`, `RLY-S15-EVAL-001`, and `RLY-S15-ACCEPT-001` into canonical repository history;
- finalize and lock bounded Slice 1.5 development memory/evidence if such memory is required by the repository convention;
- synchronize `docs/CURRENT_BASELINE.md`, `docs/BUILD_PLAN_V0_5.md`, and `docs/PRODUCT_PROPOSAL_V0_5.md` to the technical-acceptance / closure-ready state;
- advance the corresponding living-projection revisions in `.relay/registry.json` using new ArtifactIds, exact content digests, monotonic revision increments, and canonical pointers;
- register the missing accepted Slice 1.5 immutable/locked records required for complete repository provenance, without altering earlier immutable records;
- validate the registry transition from the prior canonical registry;
- run the full required quality suite on the exact closure-ready candidate SHA;
- obtain successful GitHub Actions CI on that exact SHA;
- perform an independent Slice 1.5 closure evaluation against the exact closure-ready SHA;
- record `RLY-S15-CLOSE-EVAL-001` only if that independent evaluation returns `ACCEPT`;
- after accepted closure evaluation, advance canonical living projections to `COMPLETE / ACCEPTED / CLOSED` and promote the accepted closure lineage to `main`;
- record the exact canonical closure head.

## Required reconciliation invariants

Finalization must preserve all of the following facts:

```text
Accepted design head:
25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b

Implementation authorization:
RLY-S15-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
2075be41962591552eded0597e243f0c1754b27f

Product implementation commit:
b529c7b1e4816cea0f4045a9d0efb8064984d0ed

Accepted technical candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED
```

The bounded registry repair at `ff8df665...` is accepted provenance. It must not be squashed away or misrepresented as product implementation.

The executing implementation-model deviation already recorded in the evaluation remains historical provenance:

```text
Preferred model:
GPT-5.6 Luna

Reported executing model:
GPT-6 Codex runtime
```

## Registry transition requirements

Repository finalization must use Relay's accepted repository-contract semantics.

For each changed living projection:

- create a new ArtifactId;
- increment the logical artifact revision by exactly one from the prior canonical revision;
- store the exact SHA-256 digest of the new document bytes;
- preserve artifact class `LIVING_PROJECTION` and state `CURRENT`;
- advance the matching canonical pointer to the new ArtifactId/revision;
- do not mutate a previously registered living revision in place.

New immutable authority/evaluation records may be appended with new ArtifactIds and revision `1` as appropriate.

Previously registered immutable or locked records must remain byte-for-byte semantically immutable under `validate_registry_transition`.

The transition must pass the repository's `validate_registry_transition` / repository-contract tests before closure evaluation.

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

GitHub Actions CI must also succeed on that exact closure-ready SHA.

Passing checks are evidence only. They do not themselves close the Slice.

## Independent closure evaluation

The closure evaluator must independently verify at minimum:

- the accepted technical candidate is preserved unchanged in the reconciled history;
- `RLY-S15-AUTH-001`, `RLY-S15-EVAL-001`, `RLY-S15-ACCEPT-001`, and this authority record are durably present;
- canonical `main` and accepted implementation histories were reconciled without history rewriting;
- living projections truthfully state Slice 1.5's accepted/closure-ready or closed status appropriate to the evaluation stage;
- `.relay/registry.json` matches exact document bytes and passes transition validation;
- no historical immutable/locked record was edited in place;
- no Slice 1.6 work was introduced;
- no product-code change occurred after the accepted candidate except explicitly authorized non-product finalization metadata/documentation;
- exact-SHA local quality evidence and GitHub Actions CI are successful.

The evaluator returns only:

```text
ACCEPT
REWORK
ESCALATE
```

Closure may be recorded only after `ACCEPT`.

## Not authorized

This authority does **not** authorize:

- changing the accepted Slice 1.5 production implementation;
- redesigning Board Projection behavior;
- React, TypeScript, Node, Vite, or a new frontend build chain;
- final JSON/OpenAPI API contract work;
- board mutation or human decision workflows;
- opening or implementing Slice 1.6;
- agent execution;
- repository/provider mutation behavior beyond the bounded Git/document finalization itself;
- lifecycle or governance semantic changes;
- unrelated dependency or toolchain changes;
- rewriting historical authority, design, implementation, evaluation, or acceptance records.

Any such need is a hard stop and requires separate Human Authority.

## Hard stop

```text
Slice 1.5 technical result:
ACCEPTED

Exact accepted candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Slice 1.5 finalization / closure:
AUTHORIZED

Independent closure evaluation:
PENDING

Canonical closure:
NOT YET RECORDED

Slice 1.6:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ closed.**
