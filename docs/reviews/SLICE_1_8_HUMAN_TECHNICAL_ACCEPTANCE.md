# Slice 1.8 — Human Technical Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.8 — Governance Assurance Reference Model  
**Record:** `RLY-S18-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Accepted subject

```text
Repository:
cschrupp/relay

Accepted implementation candidate:
35046bb378808a1325ecb84eace5aacd3040ca98

Implementation authority:
RLY-S18-IMPL-AUTH-001 — AUTHORIZED

Prior implementation evaluation:
RLY-S18-EVAL-001 — REWORK

Accepted independent implementation evaluation:
RLY-S18-EVAL-002 — ACCEPT

Evaluation record commit:
11ccf7ec6f5a4c4359244e26e9944ac1bbc5a4e3

Exact-head CI:
38110149903 — SUCCESS

Human technical acceptance:
RLY-S18-ACCEPT-001 — ACCEPTED
```

## Human Authority decision

The Human explicitly accepts exact candidate `35046bb378808a1325ecb84eace5aacd3040ca98` as the technical implementation result of Slice 1.8 — Governance Assurance Reference Model.

The accepted result is the bounded documentation/governance-model implementation authorized by `RLY-S18-IMPL-AUTH-001`, including the F001/F002 successor rework independently accepted by `RLY-S18-EVAL-002`.

The prior `RLY-S18-EVAL-001 — REWORK` remains preserved as historical provenance and is not rewritten or reinterpreted.

## Accepted implementation characteristics

The accepted technical result:

- materializes the Human-accepted Revision 1 + Revision 2 + Rework 1 governance-assurance design;
- preserves the four non-substitutable statement classes and Relay authority boundaries;
- preserves the exact accepted 17-property native vocabulary;
- preserves Decision Support as non-authoritative;
- preserves GovernanceProfile, Protected Verification Asset, external-mapping, freshness, Human-gate, telemetry, and downstream-ownership semantics;
- preserves external-source mappings as conservative provenance/mapping only, without certification or compliance claims;
- includes worked examples and negative cases required by the implementation authority;
- contains no production/runtime/test/schema/dependency/workflow/repository-setting change.

F001 and F002 from `RLY-S18-EVAL-001` are resolved in the exact accepted candidate.

## Engineering evidence

Exact-head GitHub Actions:

```text
Run:
38110149903

Head SHA:
35046bb378808a1325ecb84eace5aacd3040ca98

Conclusion:
SUCCESS
```

Independent review verified the bounded rework and historical-byte preservation.

Reported final checks include:

```text
uv sync --frozen --group dev — PASS
ruff format --check — PASS
ruff check — PASS
pyright — PASS
repository-contract tests — 43 PASS
full suite — 659 PASS
uv build — PASS
registry transition/preservation — PASS
git diff --check — PASS
```

Tests and CI are engineering evidence. This record is the separate Human Authority decision that accepts the technical result.

## Authority boundary after acceptance

```text
Slice 1.8:
OPEN

Implementation:
COMPLETE / TECHNICALLY ACCEPTED

Exact accepted candidate:
35046bb378808a1325ecb84eace5aacd3040ca98

Independent implementation evaluation:
RLY-S18-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S18-ACCEPT-001 — ACCEPTED

Finalization / closure:
NOT AUTHORIZED BY THIS RECORD

Canonical promotion:
NOT AUTHORIZED BY THIS RECORD

Slice 1.9:
NOT OPEN / NOT AUTHORIZED

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Human technical acceptance does not itself close the Slice or authorize canonical promotion. Finalization and independent closure evaluation require separate Human Authority.

**Independent evaluation ACCEPT != Human technical acceptance. Human technical acceptance != finalization / closure authorization.**
