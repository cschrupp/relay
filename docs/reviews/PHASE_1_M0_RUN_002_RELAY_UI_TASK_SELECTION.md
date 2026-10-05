# Phase 1 M0 — Run 002 Relay UI Task Selection

**Document class:** Immutable M0 run-opening and task-selection record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-P1-M0-RUN-002`  
**Outcome:** `OPENED / TARGET AND TASK SELECTED`

## 1. Authority basis

```text
Phase 1 M0 authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

Prior run:
RLY-P1-M0-RUN-001 — ABORTED

Prior run disposition commit:
f4be3cf991fad59fc894d5bd1c5c854da43037ad
```

Run 002 remains inside Phase 1 M0 only. It does not open Phase 2 and does not authorize Relay agent execution.

## 2. Selected target

```text
Project:
Relay

Repository:
cschrupp/relay

Target branch observed at selection:
main

Exact frozen product baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19
```

The target baseline is the canonical post-Slice-1.7 Relay main head. Later movement of `main` does not silently change this run's engineering basis.

## 3. Circularity boundary

Relay is governing development of Relay itself, so this run has an explicit anti-circularity constraint.

The governance engine under validation is treated as **frozen** for Run 002.

Run 002 may change only a bounded presentation/readability surface in the board UI. It must not change the governance rules that determine authority, lifecycle, evaluation, acceptance, or promotion.

Explicitly forbidden for the M0 implementation task:

```text
src/relay_engine/governance/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/persistence/**
src/relay_engine/repository_baseline/**
src/relay_engine/repository_contract/**
src/relay_engine/repository_sync/**

database schema or migrations
gate semantics
authorization semantics
Human-action availability semantics
manual-evaluation semantics
accepted-result promotion semantics
lifecycle transitions
Phase 2 capability
agent execution/orchestration
```

If the selected UI task cannot be implemented without touching those surfaces, stop and return to Human Authority.

## 4. Selected engineering task

```text
Run 002 task:
Relay Slice Detail — Governance Status Summary
```

### Objective

Add a compact, read-only **Governance status** summary near the top of the existing Slice detail page so a Human can understand the current governed state without mentally reconstructing it from multiple lower sections.

The summary must be a **pure presentation projection of facts already present in `SliceDetail`**. It must not calculate new governance truth, create new stored state, or alter any action availability.

## 5. Why this is appropriate for M0

The existing Slice detail projection already contains:

- lifecycle state and blockage;
- outgoing gate definitions and durable gate-evaluation projections;
- current Human authorization/approval evidence;
- current result and exact result Baseline;
- current manual evaluation;
- current Human technical decision;
- accepted result and exact accepted commit;
- development-memory projection.

The current renderer exposes these facts across separate sections. Run 002 tests whether Relay's board can make the deterministic governance state easier for a Human to understand while leaving all governing semantics unchanged.

This directly supports the canonical M0 questions:

```text
Does the board clarify project state?
Are traffic lights useful?
Does READY vs AUTHORIZED matter in practice?
Does development memory reduce repeated context explanation?
Are gates helpful or bureaucratic?
Can we reconstruct why an accepted commit exists?
```

## 6. Behavioral task contract

The Slice detail page should add an early summary section headed approximately:

```text
Governance status
```

The exact markup and wording remain a later design decision, but the summary should make the following existing facts visible where applicable.

### Lifecycle

- current lifecycle phase;
- lifecycle validity;
- blockage status;
- if blocked, existing blockage reasons.

The summary must preserve the existing distinction:

```text
READY != AUTHORIZED
```

It must never imply that lifecycle READY grants implementation/execution authority.

### Gate evaluation / traffic lights

For each current outgoing gate, summarize:

- gate identity/revision or otherwise unambiguous target;
- target lifecycle phase;
- current evaluation-basis status;
- current traffic light only when there is a matching durable evaluation;
- blocking/Human-action reasons when relevant.

Do not collapse multiple gates into one synthetic overall traffic light unless a separately reviewed design proves such a rule is already canonical. The UI must display existing gate truths, not invent aggregate governance semantics.

### Human authorization / decision evidence

Summarize current Human evidence already present in `detail.human_actions`, including current authorization grants and approval/choice evidence when applicable.

The summary must distinguish:

```text
unblocked
READY
AUTHORIZED
APPROVED
```

and must not infer any missing state.

### Manual evaluation / technical acceptance

Where the Slice 1.7 projection applies, summarize existing current facts:

- current result identity and exact result commit if resolvable;
- current manual evaluation outcome;
- current Human technical decision;
- accepted result identity and exact accepted commit when promoted.

Preserve the canonical distinction:

```text
engineering evidence
!= evaluator decision
!= Human technical acceptance
!= accepted-result promotion
```

### Provenance / development memory

If a development-memory projection exists, provide a compact indication that durable history is available and enough identifying/count information to make provenance discoverable without duplicating the full history.

Do not introduce a new memory store or materialized summary.

## 7. Preferred implementation surface

Expected production change surface:

```text
src/relay_engine/board/render.py
```

Tests should be limited to the board presentation tests appropriate to the repository's existing organization.

Changes to `board/models.py`, `board/service.py`, or `board/web.py` are not expected because the current `SliceDetail` projection already carries the needed facts. If implementation discovers that a projection change is genuinely required, that is a design-review point rather than an automatic scope expansion.

## 8. Explicit non-goals

Run 002 does not authorize:

- new write actions;
- new Human controls;
- changed action visibility/eligibility;
- changed board/service projection semantics;
- persistence/schema changes;
- new API endpoints;
- a frontend framework;
- JavaScript application state;
- new dependencies;
- redesign of the entire board;
- project-index or project-board feature expansion unrelated to the Slice-detail summary;
- autonomous agent execution;
- Phase 2 capability.

## 9. Verification expectations

A future implementation candidate should prove at minimum:

1. the summary is present near the top of Slice detail;
2. lifecycle READY is not presented as authorization;
3. current gate traffic lights are shown only on matching durable basis;
4. stale/not-evaluated/not-applicable gate states remain explicit;
5. current Human authorization evidence is shown without inference;
6. current result/evaluation/technical-decision/accepted-result facts are distinguishable;
7. exact result and accepted commit SHAs are shown when available from the existing projection;
8. development-memory availability is visible when projected;
9. all externally supplied text continues to be HTML-escaped;
10. existing lower detailed sections remain intact unless the later accepted design explicitly permits a bounded deduplication;
11. no governance/domain/persistence semantics change;
12. no dependency change;
13. repository quality gates pass.

## 10. Current state

```text
Phase 1 M0: AUTHORIZED / IN PROGRESS
Run 001: ABORTED
Run 002: OPENED
Run 002 target: Relay — SELECTED
Run 002 task: Governance Status Summary — SELECTED
Run 002 frozen product baseline: d14fa79fd13f8f70745d8ed47feafdf2d4892a19
Run 002 design: NOT AUTHORIZED
Run 002 implementation: NOT AUTHORIZED
Phase 1 completion: NOT ACCEPTED
Phase 2: NOT OPEN
Relay agent execution: NOT AUTHORIZED
```

## 11. Next gate

The next legitimate Human Authority action is design authorization for this exact bounded task.

Suggested wording:

```text
Authorize Relay M0 Run 002 Governance Status Summary design
```

That authorization should permit design only. Implementation remains a later explicit gate after independent design review and Human design acceptance.
