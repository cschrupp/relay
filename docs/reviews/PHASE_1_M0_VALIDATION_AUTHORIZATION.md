# Phase 1 M0 — Validation Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Milestone:** Phase 1 Hard Stop — M0 Validation  
**Authority ID:** `RLY-P1-M0-AUTH-001`

## Human Authority decision

```text
RLY-P1-M0-AUTH-001 — AUTHORIZED
```

The Human Authority explicitly authorizes bounded Phase 1 M0 validation of Relay's completed Human-only governance capability.

## Exact authority basis

```text
Canonical Relay main at authorization:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Slices 1.1–1.7:
COMPLETE / ACCEPTED / CLOSED

Slice 1.7 canonical closure commit:
5d6773bd5f634246c026b2964ca21e7083a966a1

Slice 1.7 accepted technical candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Slice 1.7 closure evaluation:
RLY-S17-CLOSE-EVAL-001 — ACCEPT
```

This authority is grounded in the canonical Phase 1 hard-stop requirement that Relay be used to govern at least one real project manually before Phase 2 is considered.

## Canonical M0 purpose

M0 means:

> Humans can use Relay to represent and govern engineering work without autonomous coding.

The validation must therefore test Relay as an operational governance system, not merely rerun Relay's own unit or integration tests.

At least one real engineering project must be governed through a bounded manual development loop.

Canonical candidate dogfood projects are:

```text
WellPlot
tension-modeling
Offline RAG
Relay itself
```

No dogfood target is selected by this authority record. The Human Authority must explicitly name the target project before target-specific M0 execution begins.

## Authorized validation work

Once a target project is explicitly selected, this authority permits bounded M0 setup and execution sufficient to test the completed Phase 1 capability, including:

- identify an exact target repository and baseline commit;
- define one small real engineering task or Slice with a meaningful but bounded acceptance contract;
- represent the target work in Relay using existing Phase 1 domain, lifecycle, governance, persistence, board, Human-control, manual-evaluation, and accepted-result capabilities;
- exercise READY versus AUTHORIZED semantics explicitly;
- create and inspect deterministic Handover Gates / traffic-light state;
- authorize external/manual implementation only through the existing Human Authority semantics;
- allow implementation to occur outside Relay, by a human or separately operated external coding tool, provided Relay itself does not execute an agent;
- attach the exact resulting target-repository commit through the accepted Slice 1.7 result path;
- attach or create exact-result Evidence through the accepted manual-evaluation path;
- record an authored Human manual evaluation;
- use the existing Human technical acceptance/rejection path;
- use the accepted governed result-promotion path when the target result is accepted;
- exercise a genuine REWORK cycle if the real engineering outcome warrants REWORK, without manufacturing a fake failure solely to satisfy the experiment;
- inspect the board, traffic lights, Human action availability, durable result/evaluation history, accepted-result provenance, and development-memory projection;
- record structured observations against the canonical M0 questions;
- produce a bounded M0 validation report and an independent M0 evaluation outcome.

## Required experiment questions

The validation report must answer, with evidence from the real governed task:

```text
Does the board clarify project state?

Are traffic lights useful?

Does READY vs AUTHORIZED matter in practice?

Does development memory reduce repeated context explanation?

Are gates helpful or bureaucratic?

Can we reconstruct why an accepted commit exists?
```

The report should distinguish observed evidence from evaluator judgment and Human Authority decisions.

## Minimum required evidence

A valid M0 run must preserve enough exact provenance to reconstruct at least:

```text
Relay canonical baseline used for the experiment
target project identity / repository
exact target baseline commit
target task / Slice definition
Human authorization basis
implementation result commit(s)
Evidence used by evaluation
manual evaluation outcome(s)
REWORK history, if any
Human technical decision
accepted result / exact accepted target commit, if accepted
board / gate observations relevant to the six M0 questions
development-memory projection or equivalent durable history
known friction / limitations / workarounds
```

## M0 evaluation outcome

After the real project run, an independent M0 evaluator must return one of:

```text
ACCEPT
REWORK
ESCALATE
```

`ACCEPT` means the evidence supports the Phase 1 M0 thesis that Relay is useful for Human-only engineering governance before autonomous agent execution.

`REWORK` means the experiment uncovered bounded problems that should be corrected or re-tested before Phase 1 can complete.

`ESCALATE` means the Phase 1 governance abstraction has a material conceptual or architectural problem that cannot be addressed as bounded M0 rework.

Passing Relay CI, target-project CI, or task acceptance checks are engineering evidence only and do not themselves constitute M0 acceptance.

## Phase 1 completion boundary

This authorization does not itself declare Phase 1 complete.

After an independent M0 `ACCEPT`, a separate Human Authority decision is still required to accept the Phase 1 M0 validation / declare Phase 1 complete before Phase 2 can be opened.

## Explicitly not authorized

This authority does **not** authorize:

- opening Phase 2;
- Slice 2.1 design or implementation;
- Relay AgentRuntime/OpenCode/provider-agent execution;
- autonomous coding initiated or orchestrated by Relay;
- automatic Human approval or autonomous evaluator authority;
- multi-agent orchestration;
- broad new Relay product development unrelated to defects directly discovered by M0;
- new Relay schema migrations, dependencies, lifecycle states, governance semantics, or agent abstractions unless separately authorized after an M0 finding;
- silent selection of a dogfood target;
- silent expansion of the selected target task;
- mutation of an external target repository by Relay itself;
- treating external coding-tool use as Relay agent execution authority;
- declaring Phase 1 complete solely because one target task succeeds technically.

## External implementation boundary

M0 validates Relay's governance of work, not Relay's ability to execute coding agents.

Therefore implementation of the selected real task may occur externally using ordinary human development or a separately operated coding tool. Relay may govern, record, evaluate, and accept the result, but Relay must not invoke or autonomously control that coding agent under this authority.

## Hard stop

Stop and return to Human Authority before proceeding if M0 requires:

- a Phase 2 capability;
- autonomous agent execution by Relay;
- a new provider/model execution interface;
- a new schema migration or lifecycle/governance semantic change;
- material product changes not clearly attributable to a bounded M0 defect;
- changing the selected target project or materially widening the target task after validation begins;
- bypassing Human authorization, manual evaluation, or Human technical acceptance because the manual loop is inconvenient.

## Current boundary after authorization

```text
Phase 1 M0 validation:
AUTHORIZED — RLY-P1-M0-AUTH-001

Dogfood target:
NOT YET SELECTED

M0 execution:
NOT YET STARTED

M0 independent evaluation:
PENDING

Phase 1 completion:
NOT YET ACCEPTED

Phase 2:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked != authorized. M0 validation authorized != Phase 1 accepted != Phase 2 open.**
