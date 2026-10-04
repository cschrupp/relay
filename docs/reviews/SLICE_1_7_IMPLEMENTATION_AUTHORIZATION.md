# Slice 1.7 — Implementation Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Record:** `RLY-S17-AUTH-001`

## Human Authority decision

```text
RLY-S17-AUTH-001 — AUTHORIZED
```

The Human Authority explicitly authorizes bounded implementation of the independently reviewed and Human-accepted Slice 1.7 design.

## Exact authority basis

```text
Canonical implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Exact accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Independent combined design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT
10afbeac26bbd2d7de9021e09752a5e8eaf8539b
```

The accepted precedence is:

```text
Revision 4 normative over Revision 3
Revision 3 normative over Revision 2
Revision 2 normative over Revision 1
```

## Authorized implementation scope

Implementation may add the minimum production capability necessary to complete the Human-only manual evaluation and acceptance loop defined by the accepted Slice 1.7 design, including:

- exact result attachment through verified immutable result `Baseline` plus append-only `SliceResultRecord`;
- exact preservation of source/authority Baseline `decision_ids` in every result Baseline;
- authored immutable `ManualEvaluationRecord` distinct from `GateEvaluationRecord`;
- result-bound Evidence creation/reference with server-bound evaluator identity and exact result-commit provenance;
- atomic Evidence + ManualEvaluationRecord + successor GateEvaluationRecord persistence;
- exact Slice 1.7 result/evaluation identity in Human Action Basis validation;
- backward-compatible optional Slice 1.7 identity fields on `HandoverContext`;
- evaluator `REWORK` through existing governed lifecycle handover semantics;
- explicit Human technical ACCEPT/REJECT using existing `HumanApprovalDecision` semantics;
- dedicated accepted-result promotion through the exact current GREEN ACCEPTED-target gate;
- causal accepted-Baseline reconstruction from durable result/evaluation/Human-decision/execution history;
- deterministic development-memory projection from durable Relay state;
- bounded board/FastAPI controls and projections required by the accepted design;
- narrow persistence helpers and typed records necessary for the accepted implementation.

## Explicit schema-migration authority

This authorization **explicitly authorizes** the one bounded append-only Slice 1.7 schema migration accepted by the design.

The current canonical schema ends at migration version 4. Implementation may therefore add exactly one next migration:

```text
version: 5
purpose: Slice 1.7 manual evaluation and result history
```

The migration may create only the new durable concepts accepted by the design:

```text
slice_results
manual_evaluations
```

plus only the indexes, foreign keys, constraints, and append-only triggers mechanically required to enforce the accepted typed persistence contract.

The migration must:

- be deterministic and checksummed through the existing migration framework;
- preserve all existing databases and migration history;
- upgrade an existing v4 database cleanly;
- create the complete current schema on a fresh database;
- extend schema verification sets consistently;
- enforce append-only history for both new record tables;
- preserve typed payload/index integrity;
- introduce no other table or mutable accepted-baseline pointer.

No second migration is authorized.

## Authorized bounded change surface

Expected new package:

```text
src/relay_engine/manual_evaluation/
    __init__.py
    errors.py
    models.py
    service.py
```

Bounded existing production changes may include only what is mechanically required in:

```text
src/relay_engine/domain/ids.py
src/relay_engine/governance/models.py
src/relay_engine/human_control/models.py
src/relay_engine/human_control/service.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/records.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
```

Narrow repository-baseline changes are authorized only when mechanically necessary to reuse the accepted exact Baseline verification/persistence path while forcing the result Baseline Decision set to equal the durable source Baseline Decision set.

Tests may be added/updated as required to prove the accepted contract.

## Explicitly not authorized

This authorization does **not** permit:

- any lifecycle transition-matrix change;
- any schema migration beyond the accepted single v5 migration;
- any new runtime or development dependency;
- new `EvaluationOutcome` values;
- a second Human-acceptance persistence model;
- a mutable accepted-baseline pointer;
- generic Evidence CRUD;
- a generic evaluation/workflow/command/event framework;
- repository/provider mutation for development memory;
- autonomous evaluation or autonomous Human acceptance;
- Phase 1 M0 hard-stop validation itself;
- Phase 2 opening;
- Slice 2.1 implementation;
- AgentRuntime/OpenCode execution or integration;
- agent execution of governed Relay work;
- broad authentication/RBAC/multi-user work;
- unrelated refactoring or toolchain changes.

## Implementation role

```text
Role:
Slice 1.7 IMPLEMENTATION_AGENT

Requested executor:
Codex
```

The implementation agent may produce an implementation candidate and supporting engineering evidence only.

It may not independently evaluate, technically accept, finalize, close Slice 1.7, complete the Phase 1 M0 hard stop, open Phase 2, or authorize agent execution.

## Stop conditions

Stop and escalate before widening implementation if the accepted design appears to require any excluded capability above, including an additional migration, changed lifecycle semantics, new dependency, broader persistence authority, repository mutation, or a contradiction among accepted Revisions 1–4 and current canonical code.

**Implementation authorized ≠ implementation accepted. Tests/CI are evidence, not acceptance.**