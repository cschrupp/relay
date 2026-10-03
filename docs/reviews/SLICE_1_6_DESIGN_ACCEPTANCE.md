# Slice 1.6 — Design Acceptance

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Record:** `RLY-S16-DESIGN-ACCEPT-001`

## Reviewed design

```text
Human-authorized design subject baseline:
e9c6e3a5cc7592764bf0ac4932a2ae2659644027

Authority-recording design parent:
e4923c837f20de35eb96cd1caf615b86860d9222

Revision 1:
f3a0fa7d9cc5b344399c070406353e1107ec30ff

Independent evaluation 1:
RLY-S16-DESIGN-EVAL-001 — REVISE
2b4c4d0677813cbcf64f3bf1120075f56574d081

Revision 2 amendment:
9a114b81f4347df10db7dfcb75677a606f18262e

Independent evaluation 2:
RLY-S16-DESIGN-EVAL-002 — REVISE
ed68bc0c9716704f1cd8f54c2004869d38259b21

Revision 3 amendment / exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent combined design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Evaluation record commit:
48e11982b63fd1d9078e4c4b089cd3cfbde76c71

Canonical lineage-preservation merge:
baff8936e79427013d2a0c584bf41d18757863b4
```

## Human Authority decision

```text
RLY-S16-DESIGN-ACCEPT-001
Slice 1.6 Revision 1 + Revision 2 Amendment + Revision 3 Amendment
ACCEPTED
```

The Human Authority explicitly accepts the exact combined design ending at:

```text
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb
```

Revision 3 is normative wherever it replaces or qualifies Revision 2. Revision 2 is normative wherever it replaces or qualifies Revision 1.

## Accepted design boundary

The accepted combined design defines the minimum safe product seam for explicit Human Authority while preserving the already accepted Relay governance model.

It includes:

- durable `AuthorizationGrant`, `HumanApprovalDecision`, and `HumanChoiceDecision` product workflows without introducing a second authority model;
- exact Human Action Basis and stale-view concurrency protection;
- deterministic current authorization/decision projection, including `AUTHORIZATION_STALE` evidence;
- atomic successor gate-evaluation observations after gate-affecting Human Authority mutations;
- separate decision evidence and governed lifecycle execution;
- `ADVANCE` and `CANCEL` only through exact current GREEN handover gates;
- `BLOCK`, `PAUSE`, and `DEFER` through existing orthogonal `Blockage`, with bounded `CLEAR_HOLD` / Resume semantics;
- preservation of unrelated blockers and no new PAUSED/DEFERRED lifecycle phases;
- Slice-detail action projection and explicit mutation routes on the accepted local FastAPI/server-rendered board;
- request-scoped SQLite ownership, anti-CSRF protection, and server-bound HUMAN actor identity;
- no new schema migration and no new runtime dependency;
- transition to `ACCEPTED`, manual evaluation, technical acceptance, and accepted-baseline promotion reserved for Slice 1.7.

## Authority boundary

This record accepts the design only.

It does **not** by itself authorize:

- Slice 1.6 production implementation;
- board mutation endpoints or Human Authority controls to be deployed;
- Slice 1.7;
- manual evaluation or technical acceptance;
- accepted-baseline promotion;
- repository/provider mutation;
- agent execution or AgentRuntime/OpenCode implementation;
- broader authentication, organizations, or RBAC;
- unrelated refactoring or toolchain changes.

A separate Human Authority implementation authorization is required before Slice 1.6 implementation may begin.

**Unblocked ≠ authorized.**
