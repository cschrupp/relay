# Phase 1 M0 — Run 002 Relay UI Implementation Authorization

**Document class:** Immutable Human implementation-authorization record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-P1-M0-RUN-002-IMPL-AUTH-001`  
**Outcome:** `AUTHORIZED`

## 1. Human decision

Human Authority explicitly issued:

```text
Authorize Relay M0 Run 002 Governance Status Summary implementation
```

This grants implementation authority only for the exact bounded Run 002 task and accepted design recorded below.

It does not grant implementation evaluation, Human technical acceptance, accepted-result promotion, M0 completion, Phase 1 completion, Phase 2, or Relay agent execution.

## 2. Exact authority basis

```text
Phase 1 M0 authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

Run:
RLY-P1-M0-RUN-002 — OPEN

Target repository:
cschrupp/relay

Exact frozen product baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Task:
Relay Slice Detail — Governance Status Summary

Design authority:
RLY-P1-M0-RUN-002-DESIGN-AUTH-001 — AUTHORIZED
6c29b3dadc07ba9e97e3e1121a676eab50320655

Accepted design:
RLY-P1-M0-RUN-002-DESIGN-001 — COMPLETE
65bda5393fe74ab5c5b1fda03be80b81bbc4fe30

Independent design evaluation:
RLY-P1-M0-RUN-002-DESIGN-EVAL-001 — ACCEPT
75ec3d36d8e15d4d1050c0c2e73b6e4fc62e2a2c

Human design acceptance:
RLY-P1-M0-RUN-002-DESIGN-ACCEPT-001 — ACCEPTED
a0671a4fed7be1361727d4cd2f55f0accb1535c9
```

Later movement of `main` does not silently change the implementation basis.

## 3. Authorized implementation mode

Implementation must be performed externally/manually, for example by Codex operated outside Relay.

Relay itself is not authorized to execute or orchestrate a coding agent during Phase 1 M0.

The implementation candidate must start exactly from:

```text
d14fa79fd13f8f70745d8ed47feafdf2d4892a19
```

Authorized implementation branch:

```text
implementation/m0-run-002-governance-status-summary
```

The branch must remain isolated from `main` until later evaluation and Human acceptance gates are satisfied.

## 4. Authorized production scope

Expected production change surface:

```text
src/relay_engine/board/render.py
```

Expected focused test surface:

```text
tests/unit/test_board_render.py
```

The implementation may add small private rendering helpers and minimal presentation-only CSS in `board/render.py` if needed.

The summary must remain a pure view over existing `SliceDetail` truth.

## 5. Required behavior

The candidate must implement the accepted design verification contract `V002-01` through `V002-14`, including:

- `Governance status` appears before `Definition` on Slice detail;
- READY is explicitly distinguished from authorization;
- each outgoing gate is represented independently;
- current traffic light appears only for matching durable basis;
- stale, not-evaluated, and not-applicable states remain explicit;
- authorization grants are displayed as evidence, not inferred synthetic state;
- approval and choice decisions remain distinct from authorization grants;
- current result, evaluator decision, Human technical decision, and accepted-result promotion remain distinct;
- exact result and accepted commit provenance is displayed when already available in the projection;
- development-memory availability and compact counts are visible when projected;
- externally influenced text remains HTML-escaped;
- existing detailed provenance sections remain intact;
- no governance/domain/persistence semantics change;
- no dependency or toolchain change.

## 6. Anti-circularity hard boundary

Because Relay is governing a presentation-only change to itself, the governance engine under validation is frozen.

The candidate must not modify:

```text
src/relay_engine/governance/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/persistence/**
src/relay_engine/repository_baseline/**
src/relay_engine/repository_contract/**
src/relay_engine/repository_sync/**
```

It must not change:

- gate semantics;
- authorization semantics;
- Human-action availability;
- manual-evaluation semantics;
- accepted-result promotion semantics;
- lifecycle transitions;
- persistence/schema/migrations;
- board/service projection semantics;
- agent runtime/orchestration;
- Phase 2 capability.

## 7. Design-stop / escalation conditions

Stop and return to Human Authority if implementation would require any of the following:

- modifying `src/relay_engine/board/models.py`;
- modifying `src/relay_engine/board/service.py`;
- modifying `src/relay_engine/board/web.py` for semantic reasons;
- adding a dependency;
- introducing a new presentation/domain model;
- defining a synthetic overall traffic light or aggregate governance status;
- changing any write action, action visibility, or eligibility;
- deleting or materially changing the existing detailed provenance sections;
- touching any frozen governance/domain/persistence surface listed above;
- rebasing/merging later `main` into the implementation branch.

No scope widening may be inferred.

## 8. Required implementation evidence

The external implementer must return at minimum:

```text
authorized baseline SHA
implementation branch
candidate SHA
actual executor/model provenance
complete changed-file list
mapping to V002-01 through V002-14
focused test results
full repository test results
Ruff format/lint results
Pyright results
build result
repository-contract / frozen-sync results required by the baseline
git diff --check
GitHub Actions run/status for the exact candidate, if available
dependency/toolchain-change statement
scope deviations or NONE
new work discovered or NONE
```

Passing tests or CI are engineering evidence only. They do not constitute evaluator acceptance or Human technical acceptance.

## 9. Post-implementation gate

After an exact candidate SHA exists, implementation must stop.

The next steps are separately governed:

```text
exact result attachment
-> independent/manual implementation evaluation
-> REWORK if genuinely warranted
-> explicit Human technical acceptance/rejection
-> accepted-result promotion
-> M0 run evaluation
```

No one may infer those authorities from this record.

## 10. State after authorization

```text
Phase 1 M0: AUTHORIZED / IN PROGRESS
Run 002: OPEN
Target: Relay
Task: Governance Status Summary
Frozen product baseline: d14fa79fd13f8f70745d8ed47feafdf2d4892a19
Design: COMPLETE / REVIEWED / HUMAN-ACCEPTED
Implementation: AUTHORIZED — RLY-P1-M0-RUN-002-IMPL-AUTH-001
Implementation candidate: NOT YET PRODUCED
Implementation evaluation: PENDING
Human technical acceptance: NOT GRANTED
M0 completion: NOT ACCEPTED
Phase 1 completion: NOT ACCEPTED
Phase 2: NOT OPEN
Relay agent execution: NOT AUTHORIZED
```
