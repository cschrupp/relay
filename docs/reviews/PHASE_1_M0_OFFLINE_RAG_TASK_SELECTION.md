# Phase 1 M0 — Offline RAG Task Selection

**Document class:** Immutable M0 task-selection record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Milestone:** Phase 1 Hard Stop — M0 Validation  
**Record:** `RLY-P1-M0-TASK-001`  
**Outcome:** `SELECTED`

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

Relay canonical baseline at M0 authorization:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19
```

## Selected real project

```text
Repository:
cschrupp/offline-rag

Target default branch:
main

Exact frozen target baseline:
c72215186524c9937de789adb1cf2056be13ea23
```

The exact baseline was re-read immediately before this task-selection record and remained the current `main` head. It records Slice 15 closed/accepted and keeps later work gated.

The baseline is now frozen for this M0 task. Later movement of Offline RAG `main` does not silently change the governed task basis.

## Selected M0 engineering task

```text
Relay M0 task label:
Offline RAG Slice 16A — Minimal Browser Query Experience
```

`16A` is a bounded/provisional M0 sub-slice label used to identify this experiment. This record does **not** itself open or design-authorize Offline RAG Slice 16 under that project's governance.

### Objective

Create the smallest credible browser-facing query experience that demonstrates the already accepted Offline RAG product query capability without changing retrieval science or inventing a second backend contract.

The task should consume the accepted Slice-15 product/API seam rather than bypass it.

The current accepted query boundary at the frozen baseline is:

```text
POST /v1/query

request:
{
  "corpus": <non-empty string>,
  "question": <non-empty string, <= existing server limit>
}

success projection:
{
  "corpus": ...,
  "snapshot_id": ...,
  "product_mode_id": ...,
  "trace_id": ...,
  "status": "answered" | "insufficient_evidence" | "model_abstain",
  "answer": <string or null>,
  "citations": [...]
}
```

Answered results are already required by the backend to contain validated citations. Abstention/insufficient-evidence outcomes contain no fabricated answer/citations.

## Why this task is selected for M0

This is genuine next product work, not a synthetic governance exercise.

It is bounded enough to complete through one Human-governed loop while still exercising the Phase 1 thesis:

```text
real project state
-> bounded task definition
-> READY vs AUTHORIZED distinction
-> deterministic gate state / traffic lights
-> external implementation
-> exact result SHA attachment
-> evidence
-> Human-authored manual evaluation
-> Human technical decision
-> accepted-result promotion or governed REWORK
-> development-memory/provenance reconstruction
```

It also avoids using Relay itself as the dogfood subject and therefore reduces circular validation.

## Behavioral acceptance contract

The future design may choose the minimum appropriate frontend/delivery technology, but the resulting implementation must prove the following behavior unless a separately accepted design amendment changes it.

### Query submission

- A user can access a browser-facing query surface in the supported local product environment.
- The user can provide the existing product `corpus` value and a natural-language `question`.
- Submitting the query uses the accepted product API seam, not direct retriever/vector-store/generator calls from the UI.
- The UI does not expose new retrieval-science tuning controls as part of this task.

### Answer and abstention presentation

For `status == "answered"`:

- display the returned answer;
- display the returned citations in a human-readable form;
- preserve citation provenance supplied by the API rather than inventing UI-side source attribution.

For `status == "insufficient_evidence"` or `status == "model_abstain"`:

- show an explicit no-answer/abstention state;
- do not fabricate an answer or citation.

### Provenance and diagnosability

- Make the returned `trace_id` available to the user for troubleshooting/provenance.
- Make the exact response snapshot identity (`snapshot_id`) available at least in a secondary/details presentation.
- Preserve the backend's status semantics rather than translating an abstention into a successful generated answer.

### Failure behavior

- Backend/request failures are visibly distinguishable from successful answered/abstention states.
- Do not silently retry mutating operations or synthesize a successful answer after an error.
- Safe server error boundaries remain authoritative; the UI must not expose secrets/internal exception detail merely for convenience.

### Verification

The eventual implementation/evaluation must include deterministic evidence appropriate to the chosen UI technology for at least:

```text
answered response rendering
citation rendering
insufficient-evidence rendering
model-abstain rendering
backend/request error rendering
trace/snapshot provenance availability
request payload constrained to existing product inputs
```

A real local smoke/demo query against the accepted product stack should supplement deterministic tests when practical.

## Explicitly in scope

- minimal browser query interaction;
- corpus + question input sufficient for the existing query API;
- answer/status rendering;
- citation rendering;
- trace/snapshot provenance visibility;
- bounded error/loading interaction needed for a credible query experience;
- tests/evidence for the behaviors above;
- only the minimum app-serving/integration work required by the accepted design.

## Explicitly out of scope

This M0 task selection does not authorize:

- changing retrieval, fusion, reranking, context, embedding, or generation science;
- direct UI access to Qdrant, retrievers, rerankers, generators, model runtimes, or internal stores;
- new scientific/tuning knobs;
- ingestion/admin/corpus-management UX beyond what is mechanically necessary for the selected query experience;
- changing the accepted `/v1/query` semantic contract;
- a new backend query API solely for frontend convenience;
- auth/RBAC/multi-user productization;
- cloud deployment or Internet-facing security redesign;
- Slice 17 regression/CI work;
- Slice 18 packaging/demo-polish work;
- unrelated issue/debt cleanup;
- Relay Phase 2 capability;
- Relay agent execution.

If design shows that the minimal UI genuinely requires a backend/API contract change, stop and return to Human Authority rather than silently widening this M0 task.

## Offline RAG governance boundary

The frozen Offline RAG baseline keeps Slice 16 gated and its pre-design frame requires a separate design-open authorization.

Therefore current state is:

```text
M0 project:
SELECTED — Offline RAG

M0 task:
SELECTED — RLY-P1-M0-TASK-001

Frozen Offline RAG baseline:
c72215186524c9937de789adb1cf2056be13ea23

Offline RAG Slice 16A design:
NOT YET AUTHORIZED

Offline RAG Slice 16A implementation:
NOT AUTHORIZED

M0 execution:
NOT YET STARTED

Phase 2:
NOT OPEN

Relay agent execution:
NOT AUTHORIZED
```

## Next authority gate

The next legitimate Human Authority action is a separate authorization to open bounded design for this exact task against the frozen target baseline.

Suggested authority wording:

```text
Authorize Offline RAG Slice 16A design for Phase 1 M0 validation
```

That authorization should permit design only. Implementation remains a later explicit gate after independent design review and Human design acceptance.

**Task selected != design authorized != implementation authorized != M0 accepted.**
