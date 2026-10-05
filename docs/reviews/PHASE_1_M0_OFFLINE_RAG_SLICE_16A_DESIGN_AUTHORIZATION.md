# Phase 1 M0 — Offline RAG Slice 16A Design Authorization

**Document class:** Immutable Human design-authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Milestone:** Phase 1 Hard Stop — M0 Validation  
**Record:** `RLY-P1-M0-S16A-DESIGN-AUTH-001`  
**Outcome:** `AUTHORIZED`

## Human authority

The Human Authority explicitly issued:

```text
Authorize Offline RAG Slice 16A design for Phase 1 M0 validation
```

This record is the durable interpretation of that instruction.

## Authority basis

```text
Phase 1 M0 validation authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

authority-record commit:
3fdbe6336e064eb533b4eaad226347d8730a1b41

M0 target selection:
RLY-P1-M0-TARGET-001 — Offline RAG

target-selection commit:
b9bbba03f40834ff760474ee67e7868d2962af29

M0 task selection:
RLY-P1-M0-TASK-001 — SELECTED

task-selection commit:
5e342af72f843716b2967bb7865bf467b93481e1
```

## Governed target

```text
Repository:
cschrupp/offline-rag

Target default branch:
main

Exact frozen target baseline:
c72215186524c9937de789adb1cf2056be13ea23

Target task:
Offline RAG Slice 16A — Minimal Browser Query Experience
```

The frozen target baseline remains the design basis. Later movement of Offline RAG `main` does not silently change this authority.

## Offline RAG prerequisite state

At the frozen target baseline:

```text
Slice 14: COMPLETE / ACCEPTED
Slice 15: COMPLETE / ACCEPTED
Slice 15H: COMPLETE / ACCEPTED
Slice 16: PLANNED / DESIGN NOT OPEN / NOT AUTHORIZED
```

The Slice-16 roadmap frame states that Slice 15 closeout satisfies the prerequisites for opening design and that explicit separate design authorization is the remaining gate.

This Human action satisfies that gate for the bounded M0 sub-slice identified as **Slice 16A**.

## Authorized design scope

Design may now determine the minimum architecture and delivery model for a browser-facing query experience that consumes the already accepted Slice-15 product/API boundary.

The design must cover at least:

- query-surface user flow;
- corpus and question input behavior;
- answer rendering;
- citation and provenance rendering;
- explicit `insufficient_evidence` and `model_abstain` presentation;
- backend/request failure presentation;
- `trace_id` and `snapshot_id` availability;
- loading/submission state needed for a credible local browser experience;
- frontend delivery architecture and technology choice;
- same-origin vs separate frontend decision;
- static asset/build/dependency policy;
- test/evidence strategy;
- exact proposed production change surface;
- local/offline runtime implications;
- security and safe-error-boundary implications.

## Inherited product boundary

The design must preserve the accepted Slice-15 query contract unless it stops and returns to Human Authority for an explicit scope amendment:

```text
POST /v1/query

request:
{
  "corpus": <non-empty string>,
  "question": <non-empty string>
}

success status:
answered | insufficient_evidence | model_abstain
```

The browser surface remains an adapter/client of the product/backend surface.

## Forbidden during design

This authority does **not** authorize design that silently requires or assumes:

- changing retrieval, fusion, reranking, context, embedding, or generation science;
- direct browser access to Qdrant, retrievers, rerankers, generators, model runtimes, or internal stores;
- UI-owned RAG pipeline logic;
- new algorithm/mode selectors in `/v1/query`;
- client snapshot pinning or recovery-mode selection;
- new scientific/tuning knobs;
- ingestion/admin/corpus-management product expansion beyond the selected 16A task;
- a new backend query API solely for frontend convenience;
- Slice 16B/16C/16D/16E implementation;
- Slice 17 regression/CI work;
- Slice 18 packaging/release work;
- unrelated technical-debt cleanup;
- Relay Phase 2;
- Relay agent execution.

If the design determines that a backend/API semantic change is genuinely necessary, it must stop and return to Human Authority rather than widening scope.

## Design deliverables

The authorized design phase should produce a reviewable Slice-16A design artifact containing:

1. problem statement and bounded objective;
2. inherited constraints and accepted API assumptions;
3. selected UI/delivery architecture with rationale;
4. request/response and state-flow model;
5. citation/provenance presentation contract;
6. abstention and error-state contract;
7. security/offline/dependency implications;
8. proposed file/change surface;
9. deterministic test/evidence plan;
10. explicit non-goals and stop conditions;
11. implementation acceptance criteria;
12. unresolved decisions, if any.

## Review and later gates

The design produced under this authority is **not self-accepting**.

Required sequence remains:

```text
design authorization
-> design
-> independent design review
-> Human design acceptance
-> implementation authorization
-> implementation
-> manual evaluation
-> Human technical acceptance/rejection
-> accepted-result promotion or governed REWORK
```

Implementation remains forbidden until a later explicit Human implementation authorization is issued against an accepted design.

## Current authority state

```text
Phase 1 M0:
AUTHORIZED

M0 target:
Offline RAG — SELECTED

M0 task:
RLY-P1-M0-TASK-001 — SELECTED

Offline RAG Slice 16A design:
RLY-P1-M0-S16A-DESIGN-AUTH-001 — AUTHORIZED

Offline RAG Slice 16A implementation:
NOT AUTHORIZED

Phase 2:
NOT OPEN

Relay agent execution:
NOT AUTHORIZED
```

**Design authorized != design accepted != implementation authorized != implementation accepted != M0 validated.**
