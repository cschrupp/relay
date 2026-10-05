# Slice 1.7 — Human Technical Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Record:** `RLY-S17-ACCEPT-001`

## Human Authority decision

```text
RLY-S17-ACCEPT-001 — ACCEPTED
```

The Human Authority explicitly accepts the exact Slice 1.7 implementation candidate identified below as the technical implementation result of the authorized Slice 1.7 work.

## Exact accepted subject

```text
Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Exact accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Accepted implementation candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Implementation branch:
implementation/1.7-manual-evaluation-acceptance
```

## Preserved implementation lineage

The accepted candidate preserves the complete implementation/rework sequence:

```text
38c4cda99164697be562bba610598423d9dbfbb7
    -> initial implementation candidate

c573051229ecb7714e7ff66b4155388ad953c56d
    -> bounded retry/idempotency and REWORK-cycle rework

2fc1a762e17f45fb1a3d866d8100f2c0c284b435
    -> final bounded F003 subject-identity correction
```

No rejected candidate is rewritten or reinterpreted as accepted.

## Independent implementation evaluation lineage

```text
RLY-S17-EVAL-001 — REWORK
subject: 38c4cda99164697be562bba610598423d9dbfbb7
record commit: fbb56dcf9329162c3c5e796cf93ca6b101110237

RLY-S17-EVAL-002 — REWORK
subject: c573051229ecb7714e7ff66b4155388ad953c56d
record commit: 44bddb0c8c8cdda33565be8e4d3f0c43efc63def

RLY-S17-EVAL-003 — ACCEPT
subject: 2fc1a762e17f45fb1a3d866d8100f2c0c284b435
record commit: 4c8f218d8ff5ef83fbddba526c2d7a4d2feb15ce
```

All four findings raised across the implementation review sequence are resolved in the accepted candidate:

```text
F001 — RESOLVED
F002 — RESOLVED
F003 — RESOLVED
F004 — RESOLVED
```

## Engineering evidence accepted as supporting evidence

Exact-SHA GitHub Actions run:

```text
37266796869
```

checked out:

```text
2fc1a762e17f45fb1a3d866d8100f2c0c284b435
```

and reported:

```text
uv sync --frozen --group dev: PASS
ruff format --check: PASS
ruff check: PASS
pyright: PASS — 0 errors, 0 warnings, 0 informations
pytest: PASS — 592 passed
uv build: PASS
```

The implementation handoff additionally reports `git diff --check` PASS.

Tests and CI remain engineering evidence; this Human acceptance is the separate authority decision that accepts the exact technical candidate.

## Accepted implementation characteristics

The accepted result includes the bounded Slice 1.7 manual evaluation and acceptance capability defined by the accepted Revision 1–4 design, including:

- immutable result attachment and result lineage;
- authored `ManualEvaluationRecord` distinct from deterministic `GateEvaluationRecord`;
- exact result-bound Evidence semantics;
- Slice 1.7 subject identity integrated into Human Action Basis staleness checks;
- backward-compatible `HandoverContext` subject fields;
- governed REWORK behavior and successor-result lineage;
- explicit Human technical acceptance/rejection using existing `HumanApprovalDecision`;
- dedicated exact accepted-result promotion through the governed ACCEPTED gate;
- causal accepted-result/Baseline reconstruction;
- deterministic development-memory projection;
- bounded board/FastAPI controls;
- exact retry/idempotency semantics required by the accepted design.

## Migration and dependency status

The accepted implementation contains exactly the authorized bounded schema migration:

```text
version: 5
purpose: Slice result and manual evaluation history
new durable tables:
- slice_results
- manual_evaluations
```

No migration v6 or third Slice 1.7 table is accepted.

```text
runtime dependency changes: NONE
dev/test dependency changes: NONE
lifecycle transition-matrix changes: NONE
repository mutation for development memory: NONE
agent execution: NONE
```

The previously disclosed Pyright `.venv` configuration adjustment is accepted as a bounded tooling configuration deviation and does not alter dependency declarations or tool versions.

## Model provenance

Preferred implementation model:

```text
GPT-5.6 Luna
```

Actual implementation executor reported:

```text
Codex / GPT-6 family
exact runtime variant not exposed
```

This provenance deviation is acknowledged and accepted as non-blocking for the technical result.

## Reconciliation lineage

Before this acceptance record, the canonical accepted-design state, implementation-authority lineage, exact accepted implementation candidate, and all three implementation-evaluation records were reconciled without rewriting history in:

```text
7e2b4215c2775b67b8f5be008d49cad5c4166dca
```

with the accepted implementation product bytes taken from exact candidate:

```text
2fc1a762e17f45fb1a3d866d8100f2c0c284b435
```

## Authority boundary after this record

```text
Slice 1.7:
OPEN

Implementation:
COMPLETE / TECHNICALLY ACCEPTED

Human technical acceptance:
RLY-S17-ACCEPT-001 — ACCEPTED

Finalization / closure:
NOT AUTHORIZED

Phase 1 M0 hard-stop validation:
NOT YET DECLARED COMPLETE

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

This acceptance does not authorize finalization, closure, Phase 1 M0 completion, Phase 2 opening, or any agent execution.

**Independent evaluation ACCEPT != Human technical acceptance. Human technical acceptance != finalization or closure authority.**