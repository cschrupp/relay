# Relay — Slice 3.1 Coding Agent Execution — Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / OPEN  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Record:** `RLY-S31-OPEN-001`  
**Decision:** `OPEN`

## 1. Human Authority decision

The Human explicitly authorizes opening:

`Slice 3.1 — Coding Agent Execution`.

This record opens the Slice only.

It does **not** authorize Slice 3.1 design implementation, production wiring, AgentRuntime/provider/model execution, live workspace execution, real-project autonomous engineering, canonical promotion, or any other consequential execution.

## 2. Exact opening baseline

```text
Repository:
cschrupp/relay

Canonical main / opening baseline:
0b18e4a79a0af30d86b04b9b42b96eaa0032604f

Phase 3:
OPEN under RLY-P3-OPEN-001

Slice 1.10:
COMPLETE / ACCEPTED / CLOSED
RLY-S110-CLOSE-EVAL-001 — ACCEPT

Slice 2.1 — Agent Runtime Contract:
COMPLETE / ACCEPTED / CLOSED

Slice 2.2 — Role Contracts:
COMPLETE / ACCEPTED / CLOSED

Slice 2.3 — Context / Work-Packet Contract:
COMPLETE / ACCEPTED / CLOSED

Slice 2.4 — Execution Workspace Authority:
COMPLETE / ACCEPTED / CLOSED

Slice 2.5 — Project State Resolution & Authority Compilation:
COMPLETE / ACCEPTED / CLOSED

Slice 3.1:
OPEN

Slice 3.1 design:
NOT YET AUTHORIZED

Slice 3.1 implementation:
NOT AUTHORIZED

Phase 3 execution:
NOT AUTHORIZED BY THIS RECORD

Real-project agent execution:
NOT AUTHORIZED
```

The prior Phase 3 prerequisite gate is satisfied. Opening Slice 3.1 does not itself create execution authority.

## 3. Existing planning source

The existing proposal:

`docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION.md`

remains a planning input only.

It predates accepted Slice 2.5 and the Human-authorized execution-granularity policy. Opening Slice 3.1 does not freeze that proposal as the normative design.

Any normative Slice 3.1 design must explicitly reconcile the proposal with the accepted contracts and current governance state before implementation can be considered.

## 4. Slice objective

Slice 3.1 owns the first complete Relay-governed coding-agent execution path.

Its objective is to take one exact Human-authorized engineering outcome through the accepted Relay contracts and produce one terminal implementation candidate plus exact evidence, without allowing the implementation agent, runtime, workspace, resolver/compiler, or provider to create authority or accept/promote its own work.

The intended architecture remains:

```text
Human Authority
      ↓
Project State Resolver / Authority Compiler
      ↓
exact authorized WorkPacket
      ↓
RoleContract
      ↓
Execution Workspace
      ↓
AgentRuntime
      ↓
implementation agent
      ↓
agent-owned internal plan / milestones / retries
      ↓
terminal candidate + evidence
      ↓
Independent Evaluator
      ↓
ACCEPT / REWORK / ESCALATE
      ↓
Human acceptance / promotion where required
```

Relay remains the sole governance state machine.

## 5. Mandatory boundary invariants for any future Slice 3.1 design

Any future design must preserve at minimum:

```text
Human Authority remains the authorization source.

Authority Compiler READY != AUTHORIZED.

WorkPacket remains the authoritative external work unit.

RoleContract != authority.

Workspace capability != authority.

Runtime capability != authority.

Provider/model availability != authority.

Agent-owned internal plan != WorkPacket.

Internal milestone != Human approval gate.

Internal milestone != evaluator gate.

Runtime-local retries/subagents/checklists remain non-authoritative.

Implementation agent cannot independently evaluate, accept, or promote its own work.

Successful execution != accepted result.

Terminal candidate != canonical promotion authority.

PROPOSED_WORK != authorized successor work.

Out-of-scope required work -> PROPOSED_WORK -> STOP.

No authorized successor -> BACKLOG_EXHAUSTED -> successful STOP.

Protected Verification Assets remain protected under accepted governance/workspace semantics.

Exact project/baseline/commit/runtime/provider/model/workspace identity must be preserved in execution evidence.

No automatic push/merge/canonical promotion without separate exact authority.

Accepted Slices 2.1–2.5 are sufficient by default and must not be reopened for convenience.
```

## 6. Authorized-work granularity direction

Slice 3.1 must operationalize:

`RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`.

The design must preserve the model:

```text
one cohesive authorized WorkPacket
        ↓
IMPLEMENTER / DECOMPOSE_AUTHORIZED_WORK
        ↓
agent-owned internal plan / milestones / retries
        ↓
terminal candidate
        ↓
Independent Evaluator
        ↓
ACCEPT / REWORK / ESCALATE
```

One authorized WorkPacket may contain many internal implementation steps without repeated Human approval.

External WorkPacket boundaries must reflect coherent authority/review boundaries, not arbitrary file/function/milestone granularity.

The design must explicitly prevent a private authoritative planner/task database or parallel orchestration architecture.

## 7. Project-state / authority-compilation integration

Because Slice 2.5 is now accepted and closed, Slice 3.1 design must treat Project State Resolution and Authority Compilation as part of the governed execution entry path.

The design must determine how an exact requested outcome reaches execution only after applicable prerequisites, inherited constraints, prohibitions, qualifications, evidence lineage, responsibility ownership, and resource/namespace consumption have been resolved.

The resolver/compiler may prepare a complete authority candidate but may not grant Human authority.

No direct bypass from a planning source to AgentRuntime is permitted.

## 8. Design questions now eligible for separate authorization

A later bounded Slice 3.1 design authority may cover:

- exact Slice 3.1 execution subject and identity binding;
- how Human-approved authority candidates become exact WorkPackets without duplicating Slice 2.3 semantics;
- RoleContract selection/binding without duplicating Slice 2.2;
- Execution Workspace selection/provisioning without duplicating Slice 2.4;
- AgentRuntime invocation using accepted Slice 2.1 contracts;
- exact provider/model/runtime/workspace provenance;
- implementation-agent internal decomposition semantics;
- milestone/retry/subagent observability without authority leakage;
- authority/budget/contract/environment hard-stop handling;
- `BACKLOG_EXHAUSTED` and `PROPOSED_WORK` handling;
- normalized terminal implementation result/evidence;
- dirty workspace and partial-result handling;
- cancellation/interruption handling;
- protected verification asset enforcement;
- evaluator handoff and self-evaluation prohibition;
- execution-progress projection distinct from Relay authority state;
- acceptance scenarios and deterministic/mock qualification before any separately authorized live execution;
- concrete contract-gap escalation if an accepted Slice 2.1–2.5 interface proves insufficient.

This list is an opening boundary, not a frozen detailed design.

## 9. Explicitly not authorized

This opening does not authorize:

- production source/test implementation for Slice 3.1;
- production ProjectStateResolver / AuthorityCompiler wiring;
- production WorkPacket compilation/wiring;
- production RoleContract selection/wiring;
- production workspace provisioning;
- AgentRuntime execution;
- provider/model calls;
- credential use;
- network side effects;
- shell/tool execution for governed Slice 3.1 work;
- real-project coding-agent execution;
- autonomous acceptance;
- canonical ref mutation or promotion;
- GitHub ruleset/branch-protection mutation;
- operational database/lifecycle mutation;
- schema migration;
- reopening or changing accepted Slices 2.1–2.5;
- introducing a second authoritative planner/task/workflow engine.

## 10. Documentation reconciliation authority

This record authorizes a bounded documentation-only current-state transition that changes the controlling project truth from:

```text
Slice 3.1:
ELIGIBLE TO OPEN / NOT OPEN / NOT AUTHORIZED
```

to:

```text
Slice 3.1:
OPEN

Design:
NOT YET AUTHORIZED

Implementation:
NOT AUTHORIZED

Phase 3 execution:
NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

The reconciliation may update only the current registry/living roadmap/baseline/product/TODO/navigation projections required to represent this opening.

It may register this immutable opening record.

It may not modify source, tests, dependencies, CI, schema, database state, runtime behavior, provider/model configuration, or repository settings.

## 11. Design lineage

When a separate Human design authorization is granted, use:

`design/3.1-coding-agent-execution`

rooted in the exact accepted opening lineage.

Branch existence does not grant design authority.

## 12. Next gate

The next governance gate is a separate Human decision on bounded Slice 3.1 design authorization.

Until that exists:

```text
RLY-S31-OPEN-001 — OPEN

Slice 3.1:
OPEN

Design:
NOT YET AUTHORIZED

Implementation:
NOT AUTHORIZED

Phase 3 execution:
NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

**Slice open != design authorized. Design authorized != design accepted. Design accepted != implementation authorized. Runtime capability != execution authority.**
