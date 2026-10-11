# Slice 1.8 — Finalization and Closure Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.8 — Governance Assurance Reference Model  
**Authority:** `RLY-S18-CLOSE-AUTH-001 — AUTHORIZED`

## Human Authority decision

Following independent implementation acceptance and explicit Human technical acceptance, the Human authorizes bounded Slice 1.8 finalization and independent closure evaluation of the exact technically accepted result.

```text
Accepted technical candidate:
35046bb378808a1325ecb84eace5aacd3040ca98

Independent implementation evaluation:
RLY-S18-EVAL-002 — ACCEPT

Evaluation record commit:
11ccf7ec6f5a4c4359244e26e9944ac1bbc5a4e3

Human technical acceptance:
RLY-S18-ACCEPT-001 — ACCEPTED

Acceptance lineage head:
3e7b2b18a12ca9b44ec92a4902d661b3be8d95cc

Exact-head candidate CI:
38110149903 — SUCCESS
```

Canonical starting head:

```text
a7cd87fea89e3b0273da1d0c0884336cc7857357
```

The accepted lineage is a direct descendant of that canonical head. This finalization authority is recorded on a separate canonical-based finalization lineage; after this authority/handoff commit exists, finalization must reconcile the finalization lineage and the exact accepted lineage without history rewriting.

## Preserved accepted lineage

The accepted lineage to preserve is:

```text
a7cd87fea89e3b0273da1d0c0884336cc7857357
  -> implementation / governance-model candidate lineage
  -> e81a27384086ffc3c52c8ceac1bbee7c0d0c89fc
     initial implementation candidate
     RLY-S18-EVAL-001 — REWORK
  -> a38582ff7e3a19857733d01ca8dfddb85da50259
     immutable evaluation/registry ordering state
  -> 35046bb378808a1325ecb84eace5aacd3040ca98
     bounded F001/F002 successor
     RLY-S18-EVAL-002 — ACCEPT
  -> 11ccf7ec6f5a4c4359244e26e9944ac1bbc5a4e3
     immutable RLY-S18-EVAL-002 record
  -> 3e7b2b18a12ca9b44ec92a4902d661b3be8d95cc
     immutable RLY-S18-ACCEPT-001 record
```

No rejected or superseded subject may be rewritten or reinterpreted as the accepted result.

## Accepted semantic implementation surface

Finalization must preserve the accepted Slice 1.8 governance-assurance semantics. In particular, these semantic implementation artifacts must not be redesigned during finalization:

```text
docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md
docs/architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md
docs/references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md
docs/architecture/HUMAN_DECISION_SUPPORT.md
docs/architecture/AGENT_RUNTIME.md
```

Status/navigation/living-projection documents may receive only the minimum closure-state corrections authorized below.

All immutable/lockable design, authority, handoff, evaluation, and acceptance records must remain byte-preserved.

## Authorized finalization work

This authority permits only bounded Slice 1.8 finalization:

- create/use `finalization/1.8-governance-assurance-reference-model` from canonical `main` at `a7cd87fea89e3b0273da1d0c0884336cc7857357`;
- preserve this authority record and its finalization handoff;
- perform a true ancestry-preserving reconciliation of exact acceptance-lineage head `3e7b2b18a12ca9b44ec92a4902d661b3be8d95cc` into the finalization lineage;
- preserve `35046bb...`, `RLY-S18-EVAL-001`, `RLY-S18-EVAL-002`, and `RLY-S18-ACCEPT-001` in reachable history;
- reconcile `.relay/registry.json` as a union of the accepted lineage and this authority/handoff lineage without dropping, rewriting, or duplicating historical records;
- update only status/navigation and living projections required to represent Slice 1.8 as technically accepted and closure-ready;
- explicitly correct the intentionally stale Slice 1.8 wording in `docs/PRODUCT_PROPOSAL_V0_5.md`;
- advance living projections monotonically with new ArtifactIds and exact digests;
- validate all registered artifact digests, canonical pointers, registry-transition rules, repository-contract tests, the frozen quality suite, `git diff --check`, and exact-head GitHub Actions CI;
- return the exact closure-ready SHA and evidence for independent Sol closure evaluation.

No production/runtime/test/schema/dependency/workflow/repository-setting behavior change is authorized.

## Expected living-projection advancement

The accepted implementation lineage contains:

```text
Build Plan:       revision 88
Current Baseline: revision 98
Product Proposal: revision 46
```

Finalization is explicitly authorized to make exactly one closure-ready advancement where required:

```text
Build Plan:       88 -> 89
Current Baseline: 98 -> 99
Product Proposal: 46 -> 47
```

Product Proposal revision 47 is authorized specifically to remove the intentionally preserved stale Slice 1.8 implementation-status wording and align it with technical acceptance / closure-ready state.

Each changed living projection must use a new ArtifactId, exact SHA-256 content digest, monotonic revision increment, matching canonical pointer, and preserved predecessor history.

## Closure-ready state

Before independent closure evaluation, the finalization result must remain OPEN and state:

```text
Slice 1.8:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted candidate:
35046bb378808a1325ecb84eace5aacd3040ca98

Independent implementation evaluation:
RLY-S18-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S18-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S18-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Slice 1.9:
NOT OPEN / NOT AUTHORIZED

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Do not mark Slice 1.8 `COMPLETE / ACCEPTED / CLOSED` before independent closure evaluation returns `ACCEPT`.

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

Also verify:

- canonical starting head remains an ancestor;
- exact acceptance-lineage head remains an ancestor;
- exact accepted candidate remains an ancestor;
- accepted semantic implementation artifacts are byte-identical to the accepted technical candidate unless a path is explicitly authorized above for status-only correction;
- all immutable/lockable records remain byte-identical;
- registry contains the full accepted lineage plus this authority/handoff lineage;
- all registry digests and canonical pointers are valid;
- no unauthorized Slice 1.9, Slice 1.10, Phase 3, or real-project execution work exists.

GitHub Actions CI must succeed on the exact closure-ready SHA.

Passing validation is evidence only and does not close the Slice.

## Independent closure evaluation

The independent evaluator must assess the exact closure-ready SHA and return only:

```text
ACCEPT
REWORK
ESCALATE
```

If and only if the result is `ACCEPT`, `RLY-S18-CLOSE-EVAL-001 — ACCEPT` may be frozen and the canonical living projections may then advance from closure-ready to `COMPLETE / ACCEPTED / CLOSED` as part of the already-authorized closure/promotion sequence.

Canonical promotion to `main` is forbidden before closure evaluation `ACCEPT`.

## Not authorized

This authority does not authorize:

- redesign of the accepted governance-assurance model;
- changes to the accepted semantic property vocabulary;
- production/runtime code or behavior changes;
- test changes or weakening;
- schema or dependency changes;
- workflow or repository-setting changes;
- new external compliance/certification claims;
- GovernanceProfile execution;
- Protected Verification Asset enforcement;
- Decision Support UI/Q&A implementation;
- planning-artifact adapter implementation;
- telemetry collection;
- signing/attestation infrastructure;
- Slice 1.9 or Slice 1.10 opening;
- Phase 3;
- real-project agent execution;
- canonical promotion before accepted independent closure evaluation.

**Technical acceptance is not closure. Closure evaluation ACCEPT is required before canonical promotion.**
