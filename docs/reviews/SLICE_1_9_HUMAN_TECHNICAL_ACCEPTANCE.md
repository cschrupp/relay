# Slice 1.9 — Human Technical Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Record:** `RLY-S19-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

The Human stated:

> accepted

At the current governance gate, this is recorded as explicit Human technical acceptance of the exact independently accepted Slice 1.9 implementation candidate identified below.

## Exact accepted subject

```text
Repository:
cschrupp/relay

Implementation authority:
RLY-S19-IMPL-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
a3b489bb4682314a706f66c57ee0bc1bb917542c

Exact accepted combined-design subject:
03d6efecf9ad4aaec0c5967b9486650399d0a492

Accepted implementation candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Implementation branch:
implementation/1.9-human-decision-support-governance-review-surface

Independent implementation evaluation:
RLY-S19-EVAL-003 — ACCEPT

Evaluation record commit:
43ebfdc57b7fe70ce943dc688fe0068fc8a4f659

Candidate exact-head CI:
38170054185 — SUCCESS

Evaluation-record exact-head CI:
38170877228 — SUCCESS

Human technical acceptance:
RLY-S19-ACCEPT-001 — ACCEPTED
```

## Preserved implementation and review lineage

```text
becf1c80965d8c7c36cb081a3bfa1e66b074c13a
    -> initial implementation candidate

6b2565559223cee8f0b08e9299d26eba020feac4
    -> RLY-S19-EVAL-001 — REWORK

707531ebea574a014cbb1c60f8d6714484a7205e
    -> first bounded implementation rework candidate

6d97ccc187df721fb520324268b7d1679b6369ff
    -> RLY-S19-EVAL-002 — REWORK

77ad34cf47828464a430ebdbecf1b816f158ae55
    -> final bounded implementation rework candidate

43ebfdc57b7fe70ce943dc688fe0068fc8a4f659
    -> RLY-S19-EVAL-003 — ACCEPT
```

No rejected or rework candidate is rewritten or reinterpreted as accepted.

## Accepted implementation characteristics

The Human accepts the exact candidate as the technical Slice 1.9 result, including:

- deterministic, derived, non-authoritative Human Decision Support;
- four bounded Decision Card kinds: gate authorization, gate approval, path choice, and technical acceptance;
- exact DecisionBasisIdentityV1 and canonical SHA-256 basis-digest semantics;
- same-snapshot Decision Support projection inside SliceDetail;
- preservation of existing HumanActionBasis and existing mutation-service CAS authority;
- explicit PENDING_REQUIRED versus RECORDED_REVISABLE semantics;
- complete multi-path choice projection over every eligible exact HUMAN_CHOICE gate;
- deterministic Decision Basis applicability, freshness, completeness, provenance, evidence, risk/blocker, and consequence presentation;
- exact artifact provenance and technical artifact applicability;
- deterministic structured read-only Q&A with current-basis freshness checking;
- server-rendered Human Decisions UI with explicit derived/non-authoritative labeling;
- no Decision Support persistence, no Q&A persistence, no telemetry collection, no clarity-feedback persistence, no provider/model execution, and no RAG;
- no database migration, new table, dependency, workflow, lifecycle-semantic, or Human mutation-semantic change.

All findings raised by `RLY-S19-EVAL-001` and `RLY-S19-EVAL-002` are resolved in the accepted candidate.

## Engineering evidence

Exact candidate GitHub Actions:

```text
Run:
38170054185

Head SHA:
77ad34cf47828464a430ebdbecf1b816f158ae55

Conclusion:
SUCCESS

Full suite:
681 passed

Ruff:
PASS

Pyright:
0 errors / 0 warnings / 0 informations

Build:
PASS
```

The implementation handoff/rework reports focused and repository-contract tests plus `git diff --check` PASS.

Tests, CI, and independent evaluation are engineering evidence. This record is the distinct Human Authority decision accepting the technical result.

## Preserved non-substitutability

```text
Decision Support != Evidence
Decision Support != Evaluation
Decision Support != Human Authority
Decision Support != Executed Transition

question != authorization
answer != evidence
basis_digest != mutation authority
basis complete != Human understanding
technical acceptance != canonical promotion
```

## Authority boundary after acceptance

```text
Slice 1.9:
OPEN

Implementation:
COMPLETE / TECHNICALLY ACCEPTED

Exact accepted candidate:
77ad34cf47828464a430ebdbecf1b816f158ae55

Independent implementation evaluation:
RLY-S19-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S19-ACCEPT-001 — ACCEPTED

Finalization / closure:
NOT AUTHORIZED BY THIS RECORD

Canonical promotion / merge to main:
NOT AUTHORIZED BY THIS RECORD

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Human technical acceptance does not itself close Slice 1.9 or authorize canonical promotion. Finalization/closure and any promotion require separate Human Authority.

**Independent evaluation ACCEPT != Human technical acceptance. Human technical acceptance != finalization / closure or promotion authority.**