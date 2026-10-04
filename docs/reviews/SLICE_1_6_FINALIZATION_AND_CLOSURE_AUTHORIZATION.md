# Slice 1.6 — Finalization and Closure Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Authority ID:** `RLY-S16-CLOSE-AUTH-001`

## Human Authority decision

The Human Authority explicitly authorizes bounded finalization and independent closure evaluation of Slice 1.6 after technical acceptance of the exact implementation result:

```text
a62493c733f67a5ce1b2fe5c53892d1833e4c615
```

The authorization follows:

```text
RLY-S16-EVAL-002 — ACCEPT
RLY-S16-ACCEPT-001 — ACCEPTED
```

Independent accepted implementation evaluation record commit:

```text
15e0899a0947c108aa35b417ae1bcfa427e80301
```

Human technical acceptance commit:

```text
b3fb25d23121ca9a249c56376a8f208bbaf6a1d1
```

Provenance-preserving acceptance-lineage reconciliation commit:

```text
bd59782a597181fa5d64ff4e1ab8cacaab967bea
```

Canonical `main` immediately before this finalization sequence is:

```text
5544f93fb90184909bf6e710bcca54643f689a39
```

That canonical branch contains the synchronized Slice 1.6 implementation-authorization state. The accepted implementation/evaluation/acceptance lineage and canonical-main governance lineage are already preserved through `bd59782a...`; finalization must preserve that ancestry without history rewriting.

## Authorized work

This authority permits only bounded Slice 1.6 finalization and closure work:

- preserve the exact accepted technical result `a62493c733f67a5ce1b2fe5c53892d1833e4c615` without product-code modification;
- preserve `RLY-S16-AUTH-001`, `RLY-S16-EVAL-001`, `RLY-S16-EVAL-002`, and `RLY-S16-ACCEPT-001` in canonical history;
- preserve the implementation-model provenance deviation already recorded by the accepted evaluation;
- reconcile any remaining canonical documentation lineage without rewriting existing history;
- synchronize `docs/CURRENT_BASELINE.md`, `docs/BUILD_PLAN_V0_5.md`, and `docs/PRODUCT_PROPOSAL_V0_5.md` to the technical-acceptance / closure-ready state;
- advance the corresponding living-projection revisions in `.relay/registry.json` using new ArtifactIds, exact content digests, monotonic revision increments, and canonical pointers;
- register the missing accepted Slice 1.6 immutable records required for complete repository provenance, including this authority record, without altering earlier immutable records;
- optionally finalize and lock bounded Slice 1.6 development memory/evidence only if repository convention requires it;
- validate the registry transition from the prior canonical registry;
- run the full required quality suite on the exact closure-ready candidate SHA;
- obtain successful GitHub Actions CI on that exact SHA;
- perform an independent Slice 1.6 closure evaluation against the exact closure-ready SHA;
- record `RLY-S16-CLOSE-EVAL-001` only if that independent evaluation returns `ACCEPT`;
- after accepted closure evaluation, advance canonical living projections to `COMPLETE / ACCEPTED / CLOSED`, promote the accepted closure lineage to `main`, and record the exact canonical closure head.

## Required reconciliation invariants

Finalization must preserve all of the following facts:

```text
Accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Implementation authorization:
RLY-S16-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3

Prior implementation candidate:
c1fbad66cbede4e16cb39b5065426656df4cfb3a

Prior implementation evaluation:
RLY-S16-EVAL-001 — REWORK

Accepted technical candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Independent accepted implementation evaluation:
RLY-S16-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S16-ACCEPT-001 — ACCEPTED
```

The rework lineage is accepted provenance and must not be squashed away or misrepresented as a single unevaluated implementation commit.

The executing implementation-model deviation remains historical provenance:

```text
Preferred model:
GPT-5.6 Luna

Executing model:
Codex (GPT-6)
```

## Registry transition requirements

Repository finalization must use Relay's accepted repository-contract semantics.

Prior canonical living-projection revisions are:

```text
Current Baseline: 39
Build Plan:       29
Product Proposal: 29
```

For each changed living projection:

- create a new ArtifactId;
- increment the logical artifact revision by exactly one from the prior canonical revision;
- store the exact SHA-256 digest of the new document bytes;
- preserve artifact class `LIVING_PROJECTION` and state `CURRENT`;
- advance the matching canonical pointer to the new ArtifactId/revision;
- do not mutate a previously registered living revision in place.

New immutable authority/evaluation/acceptance records may be appended with new ArtifactIds and revision `1` as appropriate.

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

GitHub Actions CI must also succeed on that exact closure-ready SHA.

Passing checks are evidence only. They do not themselves close the Slice.

## Independent closure evaluation

The closure evaluator must independently verify at minimum:

- the accepted technical candidate `a62493c...` is preserved as an ancestor and its authorized product files remain unchanged;
- `RLY-S16-AUTH-001`, `RLY-S16-EVAL-001`, `RLY-S16-EVAL-002`, `RLY-S16-ACCEPT-001`, and this authority record are durably present;
- canonical implementation-authorization history and accepted implementation/evaluation/acceptance histories remain preserved without rewriting;
- living projections truthfully state Slice 1.6's accepted/closure-ready or closed status appropriate to the evaluation stage;
- `.relay/registry.json` matches exact document bytes and passes transition validation;
- no historical immutable/locked record was edited in place;
- no Slice 1.7 work was introduced;
- no agent execution / AgentRuntime / OpenCode implementation was introduced;
- no product-code change occurred after the accepted candidate except explicitly authorized non-product finalization metadata/documentation;
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

- changing the accepted Slice 1.6 production implementation;
- redesigning Human Authorization and Decision Gate semantics;
- introducing new Human decision types, authorization revocation/expiry, or new lifecycle states;
- transition to `ACCEPTED` as a Slice 1.6 product behavior;
- manual evaluation / technical-acceptance product behavior reserved for Slice 1.7;
- opening, designing, or implementing Slice 1.7;
- agent execution;
- AgentRuntime/OpenCode implementation;
- schema migration or dependency expansion;
- unrelated repository/provider mutation behavior beyond bounded Git/document finalization;
- lifecycle or governance semantic changes;
- unrelated dependency or toolchain changes;
- rewriting historical authority, design, implementation, evaluation, or acceptance records.

Any such need is a hard stop and requires separate Human Authority.

## Hard stop

```text
Slice 1.6 technical result:
ACCEPTED

Exact accepted candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Slice 1.6 finalization / closure evaluation:
AUTHORIZED

Independent closure evaluation:
PENDING

Canonical closure:
NOT YET RECORDED

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ closed.**
