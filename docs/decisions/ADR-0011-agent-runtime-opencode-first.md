# ADR-0011 — Agent Runtime Boundary and OpenCode-First Direction

**Status:** REALIZED BY CLOSED SLICE 2.1 / HISTORICAL DECISION DIRECTION — NOT STANDALONE AUTHORITY  
**Date:** October 2026  
**Scope:** Future Phase 2–3 agent execution architecture  
**Implementation authority:** NONE

---

## Context

Relay's roadmap originally anticipated a provider-neutral model layer followed by a Relay-owned coding-agent execution loop.

Current coding-agent harnesses now provide mature reusable capabilities including sessions, tool iteration, context handling, file/shell tools, event streams, permissions, worktree support, provider/model selection, and runtime-local subagents.

Reimplementing those mechanics inside Relay would create substantial complexity in an area that is not Relay's core product thesis.

Relay's differentiating responsibility is governance:

```text
what work is authorized
which exact baseline is authorized
which role may act
which scope and tools are allowed
which evidence is required
how independent evaluation occurs
how rework is routed
who may accept a result
which commit becomes authoritative
```

The architecture therefore needs a boundary between Relay governance and a reusable coding-agent harness.

---

## Decision direction

Adopt a Relay-owned `AgentRuntime` abstraction for future autonomous role execution.

Use **OpenCode as the first planned `AgentRuntime` implementation**.

Do not make OpenCode-specific sessions, events, permissions, worktrees, providers, or subagent concepts part of Relay's domain authority unless a later accepted requirement explicitly requires that promotion.

OpenCode is selected first because it currently offers a strong combination of:

- embeddable/programmatic control;
- sessions and events;
- worktree operations;
- configurable permissions;
- multiple provider/model options;
- plugin/hook extension points;
- runtime-local subagents;
- compatibility with local dogfooding workflows.

The runtime decision and provider/model decision remain separate.

---

## Intended responsibility boundary

### Relay owns

- lifecycle and handover state;
- exact baseline and repository identity;
- Human Authority;
- role contracts;
- authoritative context/work packets;
- workspace policy;
- scope and explicit non-authority;
- evidence requirements;
- provenance;
- independent evaluator routing;
- rework;
- acceptance and baseline promotion.

### OpenCode / runtime owns

- model/tool iteration;
- context-window/runtime session mechanics;
- file/search/edit tool execution within granted authority;
- shell iteration within granted authority;
- runtime-local subagent orchestration;
- runtime event generation;
- provider/model invocation.

Runtime permission never creates Relay authorization.

---

## Consequences

### Positive

- Relay avoids owning a large generic agent-loop subsystem.
- Relay remains focused on governance and auditability.
- provider/model flexibility can be preserved.
- OpenCode can be used for local dogfooding before production sandbox infrastructure exists.
- additional runtimes can be introduced behind the same Relay contract.
- Relay's independent evaluator remains a first-class governed boundary rather than a runtime-local reviewer.

### Costs / risks

- Relay depends on the behavior and evolution of an external runtime API.
- runtime capabilities differ, so the Relay contract must be capability-aware rather than assuming perfect interchangeability.
- OpenCode worktrees and permissions are not sufficient production security boundaries.
- authentication and billing behavior differs between local dogfooding and production deployment.
- the runtime adapter must normalize events/failures without hiding useful provider/runtime detail.

---

## Required validation before lock

Before this ADR can become locked production architecture, a bounded sidecar experiment should verify:

```text
embedded/programmatic OpenCode invocation
exact-baseline execution
session lifecycle
event streaming
permission enforcement
bounded filesystem mutation
shell restrictions
AGENTS.md/context behavior
commit/result extraction
quality evidence capture
cancel/resume behavior
failure normalization
independent evaluator session isolation
runtime/provider/model provenance
```

The experiment must not be performed as unauthorized Phase 2/3 implementation.

---

## Alternatives considered

### Relay-owned bespoke loop

Rejected as the default direction because it duplicates mature generic coding-agent infrastructure and expands Relay away from its governance thesis.

### Codex-only runtime

Retained as a future adapter option, not selected as Relay's core abstraction. A vendor-native harness can remain valuable where its model/harness pairing provides advantages.

### OpenCode as Relay's domain model

Rejected. OpenCode remains an execution substrate behind a Relay-owned contract.

### Runtime-local reviewer as formal evaluator

Rejected. Formal evaluator independence is a Relay governance property and must remain a separately instantiated governed execution.

---

## Relationship to current authority

The OpenCode-first AgentRuntime direction was subsequently designed, implemented, live-evidenced, Human-accepted, and canonically closed by Slice 2.1.

```text
Slice 2.1:
COMPLETE / ACCEPTED / CLOSED

Accepted candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Closure evaluation:
RLY-S21-CLOSE-EVAL-002 — ACCEPT
```

This ADR remains historical rationale, not standalone implementation authority.

The roadmap is now re-baselined under `RLY-P2-ROADMAP-REBASE-001` around Phase 1 assurance/promotion hardening, then Role Contracts, Context/Work Packets, Execution Workspace Authority, and only afterward Phase 3 autonomous execution.

No new execution is authorized by this ADR.

---

## Expected superseding/locking path

The runtime decision has been realized by Slice 2.1. Future changes to AgentRuntime architecture must proceed through normal Relay governance. The current next sequence is defined by the canonical Build Plan and `RLY-P2-ROADMAP-REBASE-001`.
