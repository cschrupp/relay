# Slice 1.6 — Design Authorization

**Document class:** Immutable authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Authority ID:** `RLY-S16-DESIGN-AUTH-001`

## Human Authority decision

The Human Authority explicitly authorizes Slice 1.6 architecture, contract, and detailed design work.

```text
Slice 1.6 — Human Authorization and Decision Gates
DESIGN AUTHORIZED
```

Human-authorized design subject baseline:

```text
e9c6e3a5cc7592764bf0ac4932a2ae2659644027
```

Opening authority:

```text
RLY-S16-OPEN-001
```

Canonical roadmap objective:

> Implement explicit human authority and expose durable human approvals, choices, blocks, deferrals, and cancellations through product workflow.

The older detailed Phase-1 roadmap names the initial human actions as:

```text
APPROVE
REJECT
CHOOSE_PATH
PAUSE
BLOCK
DEFER
CANCEL
```

Slice 1.7 remains the owner of manual evaluation, technical acceptance, accepted-baseline promotion, and the remainder of the human-only implementation/evaluation loop.

## Authorized design role

```text
Slice 1.6 Human Authorization and Decision Gates Architect — GPT-5.6 Sol
```

The role is governance-led rather than UI-led. The primary design risk is allowing a convenient human interaction to bypass Relay's accepted gate, baseline, lifecycle, staleness, audit, or hard-stop semantics.

## Authorized design scope

The architect may define:

- the application/service boundary for durable Human Authority commands;
- product semantics for authorization grants, approvals/rejections, path choices, blocks, pauses, deferrals, cancellation, and any strictly necessary inverse action such as clearing a human hold;
- deterministic action-availability projection from accepted durable state;
- exact basis/staleness and optimistic-concurrency requirements for each command;
- how accepted `AuthorizationGrant`, `HumanApprovalDecision`, and `HumanChoiceDecision` values are created, selected, persisted, and surfaced;
- how human control actions reuse accepted lifecycle blockage/cancellation semantics without inventing parallel lifecycle truth;
- how a human may execute an already-valid GREEN handover without conflating decision evidence with execution;
- the boundary between Slice 1.6 human decisions and Slice 1.7 manual evaluation/acceptance;
- the minimum mutation-capable extension to the Slice 1.5 board and local FastAPI adapter;
- request security appropriate to a local mutation-capable board, including anti-CSRF behavior and actor binding;
- deterministic error behavior, accessibility, idempotency, testability, and audit requirements;
- the expected implementation change surface and explicit acceptance evidence.

## Mandatory architectural constraints

1. Reuse the accepted governance domain. Slice 1.6 must not create a second approval/authorization model when `AuthorizationGrant`, `HumanApprovalDecision`, `HumanChoiceDecision`, `HandoverGate`, and deterministic gate evaluation already exist.
2. Human decisions are durable evidence. They are not equivalent to lifecycle execution.
3. A stale decision, stale gate revision, stale baseline, stale lifecycle revision, or stale governance basis must never silently act as current authority.
4. Hard stops and RED gates cannot be bypassed through ordinary product actions.
5. The board may submit governed commands but remains a projection of durable state; presentation state is never authority.
6. Slice 1.6 must not invent `PAUSED` or `DEFERRED` lifecycle phases unless the accepted model proves insufficient and the design escalates that need explicitly.
7. Existing blockage and cancellation semantics should be reused where they correctly represent the required action.
8. Slice 1.7 retains manual evaluation, technical acceptance, and accepted-baseline promotion.
9. Agent execution remains unauthorized.
10. The OpenCode/AgentRuntime proposal is future architecture context only and must not expand Slice 1.6.
11. Use Minimum Sufficient Architecture: no generic workflow engine, event bus, plugin system, user/organization subsystem, or new frontend stack without present-tense necessity.
12. No implementation work is authorized by this record.

## Not authorized

This authority does **not** authorize:

- production implementation;
- changing accepted lifecycle or governance semantics without an explicit design escalation;
- autonomous approvals or automatic Human Authority substitution;
- manual evaluator-result capture or acceptance workflows owned by Slice 1.7;
- accepted-baseline promotion;
- repository/provider mutation behavior;
- agent execution or AgentRuntime/OpenCode implementation;
- opening Slice 1.7;
- multi-user authentication, organizations, or broad RBAC unless the design demonstrates they are strictly necessary for the current local Human Authority workflow;
- unrelated refactoring or toolchain changes.

## Design gate

The architect must produce a durable Slice 1.6 design record from a commit containing this authority record and must bind the design to the exact authorized baseline above.

The design must receive independent design review using:

```text
ACCEPT
REVISE
ESCALATE
```

Human design acceptance and implementation authorization are separate later gates.

## Hard stop

```text
Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.6:
OPEN

Slice 1.6 design:
AUTHORIZED

Slice 1.6 implementation:
NOT AUTHORIZED

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
