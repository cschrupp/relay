# Phase 1 M0 — Offline RAG Slice 16A Design Acceptance

**Document class:** Immutable Human design-acceptance record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Milestone:** Phase 1 Hard Stop — M0 Validation  
**Target project:** `cschrupp/offline-rag`  
**Record:** `RLY-P1-M0-S16A-DESIGN-ACCEPT-001`  
**Outcome:** `ACCEPTED`

## Human decision

Human Authority explicitly accepted the bounded design for:

```text
Offline RAG Slice 16A — Minimal Browser Query Experience
```

for use as the Phase 1 M0 validation task.

This record accepts the design only. It does not authorize implementation.

## Authority basis

```text
Phase 1 M0 validation authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

M0 target selection:
RLY-P1-M0-TARGET-001 — Offline RAG

M0 task selection:
RLY-P1-M0-TASK-001 — Offline RAG Slice 16A

Slice 16A design authority:
RLY-P1-M0-S16A-DESIGN-AUTH-001 — AUTHORIZED

design-authority commit:
5342a623b01a6c0a77b95b2e4721507606e8c06a
```

## Exact accepted design

```text
Design record:
RLY-P1-M0-S16A-DESIGN-001 — COMPLETE

design commit:
f06c3ec570cc7341d0ca30bef61fa2e0cb670624

Independent design evaluation:
RLY-P1-M0-S16A-DESIGN-EVAL-001 — ACCEPT

review commit:
533d677c80e41db3472d1539554dc30015f56dec
```

The accepted design remains bound to the frozen Offline RAG target baseline:

```text
c72215186524c9937de789adb1cf2056be13ea23
```

Later movement of Offline RAG `main` does not change the implementation basis unless a separately governed rebase or authority update is issued.

## Accepted architectural direction

The accepted design uses a same-process, same-origin, server-rendered FastAPI browser surface over the existing accepted product query seam.

The design preserves the existing product semantics and keeps the browser outside retrieval/generation internals.

Key accepted constraints include:

- browser-facing query UI remains an adapter/client of the product layer;
- `GET /ui` renders the query page;
- `POST /ui/query` submits the bounded UI query request;
- execution reuses the canonical product query use case rather than calling Qdrant, retrievers, rerankers, or generators directly;
- existing `/v1/query` behavior remains a regression boundary;
- answered, insufficient-evidence, model-abstain, and safe error states remain semantically distinct;
- returned citations remain backend-authored provenance;
- `trace_id` and `snapshot_id` remain visible for provenance/diagnostics;
- no retrieval-science knobs or client algorithm selector are introduced;
- no new Node/SPA toolchain is required;
- no new runtime dependency is required by the accepted design;
- existing loopback-first HTTP bind policy remains authoritative;
- deterministic UI tests must cover the accepted answer/abstention/error/provenance states.

## Governance boundary

This Human acceptance grants no implementation authority.

The following remain unauthorized by this record:

- changing product query semantics;
- changing retrieval/fusion/reranking/context/generation science;
- adding direct UI access to Qdrant or model/runtime internals;
- introducing new scientific/tuning controls;
- Slice 16B/16C/16D/16E work beyond mechanically necessary design boundaries;
- Slice 17 or Slice 18 work;
- unrelated cleanup/debt work;
- Relay Phase 2;
- Relay agent execution.

Any implementation must start from the exact frozen target baseline unless a new Human authority changes that basis.

## Current state after acceptance

```text
Phase 1 M0 validation:
AUTHORIZED

Target project:
Offline RAG — SELECTED

M0 task:
Offline RAG Slice 16A — SELECTED

Frozen Offline RAG baseline:
c72215186524c9937de789adb1cf2056be13ea23

Slice 16A design:
COMPLETE

Independent design evaluation:
ACCEPT

Human design acceptance:
RLY-P1-M0-S16A-DESIGN-ACCEPT-001 — ACCEPTED

Slice 16A implementation:
NOT AUTHORIZED

Phase 1 M0 completion:
NOT YET ACCEPTED

Phase 2:
NOT OPEN

Relay agent execution:
NOT AUTHORIZED
```

## Next gate

The next legitimate Human Authority action is a separate bounded implementation authorization for this exact accepted design and frozen Offline RAG baseline.

Suggested wording:

```text
Authorize Offline RAG Slice 16A implementation for Phase 1 M0 validation
```

**Design accepted != implementation authorized != M0 accepted != Phase 2 open.**
