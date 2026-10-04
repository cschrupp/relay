# Slice 1.7 — Design Acceptance

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-04  
**Project:** Relay  
**Slice:** 1.7 — Manual Evaluation and Acceptance  
**Record:** `RLY-S17-DESIGN-ACCEPT-001`

## Reviewed design

```text
Slice 1.7 opening authority:
RLY-S17-OPEN-001
0a805d87617b01dd5a02668b15d43cbd81670a46

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED
8a93f666fbb8dd3099fbc8d5699f8fe3cef7e094

Revision 1:
a53c4f3a8613d23643cb5a4affc7a6f6b5ee08c6

Independent evaluation 1:
RLY-S17-DESIGN-EVAL-001 — REVISE
a73c400947964fbf1d1fc8210c925c3d021e5e16

Revision 2 amendment:
af91ae03a6b4eb76c68c190d71d782b04a509f90

Independent evaluation 2:
RLY-S17-DESIGN-EVAL-002 — REVISE
df587b6f3d611e7ba11501125d1e645d4a6190e4

Revision 3 amendment:
44c2ea1f141968c0e79ac92d571261fbe83f2f5c

Independent evaluation 3:
RLY-S17-DESIGN-EVAL-003 — REVISE
dd746877e20d045d8c0575d86dba9be7c9af024f

Revision 4 amendment / exact accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Independent combined design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT
10afbeac26bbd2d7de9021e09752a5e8eaf8539b

Canonical lineage-preservation merge:
da38050529ac1c0b8309dd69a29ce1cf5da0ff47
```

## Human Authority decision

```text
RLY-S17-DESIGN-ACCEPT-001
Slice 1.7 Revision 1 + Revision 2 Amendment + Revision 3 Amendment + Revision 4 Amendment
ACCEPTED
```

The Human Authority explicitly accepts the exact combined design ending at:

```text
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b
```

Revision 4 is normative wherever it replaces or qualifies Revision 3. Revision 3 is normative wherever it replaces or qualifies Revision 2. Revision 2 is normative wherever it replaces or qualifies Revision 1.

## Accepted design boundary

The accepted combined design completes the architecture and contract for the Human-only manual evaluation and technical-acceptance loop while preserving Relay's existing deterministic governance model.

It includes:

- exact result identity through an immutable verified result `Baseline` plus append-only `SliceResultRecord` provenance;
- exact preservation of the source/authority Baseline Decision set in every result Baseline;
- immutable authored `ManualEvaluationRecord` distinct from deterministic `GateEvaluationRecord`;
- reuse of the existing `EvaluationOutcome` vocabulary;
- result-bound Evidence with server-bound evaluator actor and exact result commit provenance;
- atomic evaluator submission of Evidence, ManualEvaluationRecord, and successor gate observation;
- exact result/evaluation identity in Human Action Basis so pending or superseded results fail closed;
- backward-compatible historical `HandoverContext` semantics;
- evaluator `REWORK` routed through the existing governed `EVALUATING -> REWORK` path rather than direct lifecycle mutation;
- mandatory Human technical acceptance on the exact ACCEPTED-target gate using existing `HumanApprovalDecision`, regardless of generic gate autonomy policy;
- dedicated accepted-result promotion that revalidates exact evaluator ACCEPT, exact Human APPROVE, complete GREEN gate state, source/result Decision authority equality, and uses the accepted governed handover execution path;
- causal reconstruction of the accepted Baseline from the ACCEPTED execution rather than a mutable accepted-baseline pointer;
- deterministic development-memory projection over durable result/evaluation/rework/acceptance/execution history without repository mutation in M0;
- a bounded server-rendered board/FastAPI product seam consistent with Slice 1.6 actor binding, CSRF, request-scoped SQLite ownership, and fail-closed stale-basis behavior;
- one justified append-only schema migration adding only `slice_results` and `manual_evaluations`;
- no new runtime or development dependency;
- no lifecycle transition-matrix change;
- no agent execution, AgentRuntime/OpenCode implementation, or Phase 2 opening.

## Accepted causal separation

The design preserves:

```text
engineering evidence
    !=
evaluator decision
    !=
Human technical acceptance
    !=
accepted-baseline promotion
```

and:

```text
passing CI
    !=
evaluation ACCEPT
    !=
ACCEPTED lifecycle state
```

and:

```text
moving branch/ref
    !=
accepted Baseline
```

## Authority boundary

This record accepts the design only.

It does **not** by itself authorize:

- Slice 1.7 production implementation;
- applying the accepted schema migration;
- creation of `slice_results` or `manual_evaluations` tables in any implementation baseline;
- manual-evaluation or technical-acceptance product endpoints to be deployed;
- transition to `LifecyclePhase.ACCEPTED` through new Slice 1.7 product controls;
- accepted-baseline promotion in production;
- repository/provider mutation;
- Phase 1 M0 hard-stop validation;
- Phase 2 opening;
- Slice 2.1 design or implementation;
- agent execution;
- AgentRuntime/OpenCode execution or integration;
- autonomous evaluation or Human acceptance;
- unrelated refactoring, toolchain changes, new dependencies, or broader RBAC.

A separate Human Authority implementation authorization is required before any Slice 1.7 implementation begins. That authorization must explicitly include the accepted bounded append-only schema migration if implementation is to apply it.

**Unblocked ≠ authorized. Design accepted ≠ implementation authorized.**
