# Phase 1 M0 — Dogfood Target Selection

**Document class:** Immutable Human target-selection record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Milestone:** Phase 1 Hard Stop — M0 Validation  
**Record:** `RLY-P1-M0-TARGET-001`

## Human Authority selection

```text
RLY-P1-M0-TARGET-001 — SELECTED
```

The Human Authority selects **Offline RAG** as the real project to be governed during the Phase 1 M0 validation authorized by `RLY-P1-M0-AUTH-001`.

This selection replaces the prior recommendation to use WellPlot. WellPlot was never formally selected, so no prior target-selection authority is superseded or revoked.

## Relay validation authority basis

```text
Phase 1 M0 validation authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

Relay canonical main at M0 authorization:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

M0 validation branch:
validation/phase-1-m0
```

## Selected target repository

```text
Project name:
Offline RAG

Repository:
cschrupp/offline-rag

Default branch:
main

Exact repository head observed at target selection:
c72215186524c9937de789adb1cf2056be13ea23
```

The observed target head is an experiment-selection reference point only. The exact engineering-task baseline must be revalidated and explicitly frozen in the forthcoming target-task contract before implementation begins.

## Selection rationale

Offline RAG is selected because its current development structure is sufficiently explicit for a meaningful Phase 1 M0 governance experiment. At the observed head, the repository records Slice 15 as closed while later milestone/slice work remains gated, providing a clear boundary from which a small real next task can be selected without inventing artificial work.

## What this selection authorizes

This record authorizes target-specific M0 preparation for `cschrupp/offline-rag`, including:

- inspect current canonical/project documentation and recent slice history;
- identify a small real next engineering task suitable for the M0 experiment;
- determine the exact target baseline SHA immediately before the task contract is frozen;
- define the target Slice/task objective, acceptance contract, quality evidence, and explicit READY-versus-AUTHORIZED boundary;
- prepare Relay-side M0 representations and validation observations required by `RLY-P1-M0-AUTH-001`.

## What remains unauthorized

This selection does **not** itself authorize:

- implementation of any Offline RAG task;
- mutation of the Offline RAG repository;
- choosing a specific Slice/task without a separate explicit task contract;
- Relay agent execution;
- autonomous coding initiated by Relay;
- Phase 2 opening;
- Slice 2.1 work;
- widening the M0 experiment beyond the selected bounded Offline RAG task once frozen;
- declaring M0 or Phase 1 accepted.

External implementation may later be separately authorized under the existing M0 authority boundary and may be performed by a human or separately operated coding tool, but Relay itself remains prohibited from executing an agent.

## Next governed step

The next step is to inspect Offline RAG's current roadmap/state and produce a **target-task proposal** naming:

```text
exact target baseline SHA
small real engineering task / Slice
objective
in scope
out of scope
acceptance criteria
quality commands / evidence
expected change surface
READY criteria
separate implementation-authorization gate
M0 observation plan
```

The Human Authority must explicitly accept/select that task contract before implementation begins.

## Current boundary

```text
Phase 1 M0 validation:
AUTHORIZED — RLY-P1-M0-AUTH-001

Dogfood target:
Offline RAG — SELECTED

Target-selection record:
RLY-P1-M0-TARGET-001

Target repository:
cschrupp/offline-rag

Observed target head:
c72215186524c9937de789adb1cf2056be13ea23

Specific M0 engineering task:
NOT YET SELECTED / CONTRACTED

M0 implementation:
NOT AUTHORIZED

M0 independent evaluation:
PENDING

Phase 1 completion:
NOT YET ACCEPTED

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Target selected != task selected != implementation authorized.**
