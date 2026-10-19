# Relay — Agent Runtime Boundary

**Status:** ACCEPTED RUNTIME DIRECTION REALIZED BY CLOSED SLICE 2.1 — REFERENCE ARCHITECTURE / NOT NEW AUTHORITY  
**Decision direction:** OpenCode first  
**Applies to:** Future Phase 2 provider/agent foundation and Phase 3 autonomous engineering loop  
**Date:** October 2026

---

## 1. Purpose

Relay should govern software-engineering work without reimplementing a general-purpose coding-agent reasoning and tool loop.

The intended boundary is:

> **Relay governs engineering. An agent runtime executes the bounded engineering role.**

Relay therefore owns a stable `AgentRuntime` contract and delegates runtime-local reasoning/tool iteration to an external coding-agent harness.

The first planned runtime implementation is **OpenCode**.

Slice 2.1 has implemented and closed the AgentRuntime boundary at accepted candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49`, with closure evaluation `RLY-S21-CLOSE-EVAL-002 — ACCEPT`. This document remains reference architecture, not new execution authority. The next prerequisites are Phase 1 assurance/promotion hardening, then Role Contracts, deterministic Context/Work Packets, and Execution Workspace Authority.

---

## 2. Why this boundary exists

A bespoke Relay agent loop would require Relay to own concerns such as:

```text
model/tool iteration
context compaction
shell and file tool dispatch
session continuation
runtime-local subagent mechanics
provider-specific tool protocols
termination heuristics
```

Those concerns are substantial but are not Relay's differentiating product thesis.

Relay's differentiating responsibilities are:

```text
exact baseline authority
human authorization
role contracts
bounded work packets
workspace entitlement
scope and non-authority
provenance and evidence
independent evaluation
rework routing
Human Authority decisions
acceptance and baseline promotion
```

The architecture should keep those responsibilities explicit and testable while using a mature coding-agent harness for the inner execution loop.

`AgentRuntime` consumes a Relay-governed execution contract. It is independent of whether upstream engineering intent originated in Relay-native planning, Spec Kit, OpenSpec, BMAD, an enterprise workflow, or another supported source. Those sources must first be normalized and bound to Relay authority; the runtime neither imports upstream workflow authority nor needs to know which planning method produced the contract. This clarifies the future architecture boundary and does not change the accepted Slice 2.1 runtime contract.

---

## 3. Planned architecture

```text
                         Relay
                           │
                 governed role execution
                           │
                    AgentRuntime
                           │
              ┌────────────┴────────────┐
              │                         │
       OpenCodeRuntime             future runtime
              │                         │
         OpenCode host             e.g. Codex
              │
      provider / model choice
```

`AgentRuntime` is a Relay-owned boundary. OpenCode is an implementation of that boundary, not part of Relay's domain model.

Relay must remain able to add another runtime later without changing lifecycle, authorization, evaluation, or acceptance semantics.

---

## 4. Responsibility split

### 4.1 Relay owns

Relay remains authoritative for:

- project and slice state;
- exact repository baseline SHA;
- Human Authority records;
- role contracts;
- work-packet construction;
- allowed scope and explicit non-authority;
- workspace provisioning policy;
- credential grants and execution budgets;
- evidence requirements;
- execution provenance;
- evaluator independence;
- rework routing;
- hard stops;
- acceptance;
- baseline promotion;
- durable project memory and canonical projections.

### 4.2 Agent runtime owns

The runtime may own implementation details such as:

- reasoning/model iteration;
- runtime session state;
- context-window management and compaction;
- file discovery;
- file edits within granted authority;
- shell-command iteration within granted authority;
- LSP/tool use;
- runtime-local subagents;
- runtime event production;
- provider/model invocation.

### 4.3 Runtime permissions are not Relay authority

OpenCode permission rules are defense in depth. They may enforce or narrow Relay policy, but they do not create authorization.

For example:

```text
OpenCode permission says git commit is allowed
              ≠
Relay has authorized implementation
```

Relay must refuse to start an execution when its own authority checks fail even if the runtime itself would permit the requested action.

---

## 5. First planned implementation: OpenCode

OpenCode is the first planned runtime because its current SDK/runtime surface provides capabilities relevant to Relay without requiring Relay to own the inner agent loop:

- embeddable SDK host;
- programmatic sessions;
- event streaming;
- worktree support;
- configurable permissions;
- provider/model flexibility;
- plugins and hooks;
- runtime-local subagents;
- provider use policies;
- local or external execution contexts depending on deployment design.

OpenCode's provider flexibility is particularly important: Relay can select a runtime independently from the model/provider used by a role.

For local dogfooding, OpenCode can authenticate to supported providers, including OpenAI through ChatGPT Plus/Pro where supported by the provider integration. Production credential and billing policy remains a separate future design decision.

---

## 6. Proposed Relay contract

The exact interface must be designed under the authorized Phase 2 slice, but the expected conceptual shape is:

```python
class AgentRuntime(Protocol):
    async def create_session(...): ...
    async def execute(...): ...
    async def stream_events(...): ...
    async def steer(...): ...
    async def cancel(...): ...
    async def resume(...): ...
    async def inspect_result(...): ...
```

The contract should be capability-oriented rather than tied to OpenCode API object names.

A runtime adapter should normalize runtime behavior into Relay-owned records such as:

```text
ExecutionStarted
ExecutionEvent
ExecutionBlocked
ExecutionCompleted
ExecutionFailed
ExecutionResult
```

The exact domain additions remain subject to future slice design.

---

## 7. Workspace boundary remains separate

`AgentRuntime` and execution workspace are separate abstractions.

```text
Relay
  ├─ WorkspaceProvider
  │    ├─ local worktree backend
  │    ├─ container backend
  │    └─ future isolated/cloud backend
  │
  └─ AgentRuntime
       ├─ OpenCodeRuntime
       └─ future runtime
```

An OpenCode Git worktree is useful for local dogfooding but is not, by itself, a production security boundary.

Production execution must still satisfy future workspace requirements including filesystem isolation, secret restriction, network policy, resource limits, and teardown.

---

## 8. Independent evaluation boundary

Runtime-local subagents must not replace Relay's independent evaluator.

Correct future flow:

```text
Relay authorizes implementation
        ↓
OpenCode implementation session
        ↓
resulting commit + evidence
        ↓
Relay constructs independent evaluation packet
        ↓
new evaluator execution/session
        ↓
structured Relay evaluation outcome
```

An implementer may use runtime-local subagents for bounded internal tasks such as exploration or test analysis, but acceptance cannot be delegated to a reviewer subagent spawned by the implementation execution.

---

## 9. Proposed runtime-selection model

Future role configuration may eventually resemble:

```yaml
agents:
  implementation:
    runtime: opencode
    provider: openai
    model: <configured model>

  evaluator:
    runtime: opencode
    provider: <configured provider>
    model: <configured model>
```

Runtime, provider, and model are separate choices.

Changing a model should not modify Relay workflow semantics. Changing the runtime should not modify project-state semantics.

---

## 10. Evidence required before implementation lock

Before OpenCode becomes an accepted production runtime, Relay should run a bounded sidecar experiment that verifies at least:

```text
exact-SHA workspace startup
programmatic embedded/runtime invocation
session creation and continuation
event visibility
permission enforcement
AGENTS.md / governed context behavior
bounded file mutation
command restrictions
resulting commit capture
changed-file manifest capture
quality-check evidence capture
interruption / cancellation behavior
resume behavior
failure normalization
independent evaluator session separation
provider/model provenance
local ChatGPT-auth dogfood path where applicable
```

Experiment success is evidence only. It does not automatically make the integration production architecture.

---

## 11. Relationship to current roadmap

```text
Phase 1 hardening:
  1.8 Governance Assurance Reference Model — IMPLEMENTED / AWAITING INDEPENDENT IMPLEMENTATION EVALUATION
  1.9 Human Decision Support and Governance Review Surface — PLANNED
  1.10 Canonical Source and Promotion Enforcement — PLANNED

Phase 2:
  2.1 Agent Runtime Contract                  CLOSED
  2.2 Role Contracts                         PLANNED
  2.3 Context and Work-Packet Contract       PLANNED
  2.4 Execution Workspace Authority          PLANNED

Phase 3:
  3.1 Coding Agent Execution                 FUTURE / NOT AUTHORIZED
```

Provider/model capability and routing remain beneath or alongside the runtime abstraction. Role, work-packet, workspace, evaluation, rework, acceptance, and promotion semantics remain Relay-owned.

Decision Support is a cross-cutting, derived, non-authoritative projection at every policy-required Human decision, including before design or implementation evidence exists; it is not a lifecycle stage after verification. It makes a decision legible but creates no evidence, evaluation, authority, or lifecycle transition. See `HUMAN_DECISION_SUPPORT.md`. Slice 3.1 depends on 1.8, 1.9, 1.10, 2.2, 2.3, 2.4, and explicit Phase 3 opening authority.

The canonical Build Plan is authoritative for roadmap state.

---

## 12. Non-goals

This direction does not authorize or require:

- OpenCode integration during Slice 1.6 or 1.7;
- replacing Relay lifecycle semantics with OpenCode session state;
- making OpenCode worktrees a production sandbox boundary;
- allowing runtime-local subagents to approve their parent execution;
- coupling Relay domain objects to OpenCode-specific IDs or event types;
- requiring one provider or model family;
- deleting Relay evaluation, evidence, or acceptance machinery;
- bypassing Human Authority because a runtime can act autonomously.

---

## 12.1 Authorized-work exhaustion and terminal semantics

Relay must distinguish **authority to execute work** from **authority to create new work**.

An implementation/runtime session may autonomously decompose its current authorized work into whatever bounded internal steps are needed to satisfy that work: inspect, diagnose, edit, test, repair, retry, and use runtime-local subagents. Those internal steps do not become durable backlog items and do not survive the authority that justified them.

The runtime must not infer that completing an authorized item grants authority to invent its successor. Successor selection belongs to Relay's control plane.

The required execution shape is:

```text
authorized work item
        ↓
autonomous bounded execution
        ↓
item completion
        ↓
Relay resolves next authorized item
        │
        ├─ successor exists ──► next governed execution
        │
        └─ none exists ───────► BACKLOG_EXHAUSTED
                                  ↓
                                 STOP
```

`BACKLOG_EXHAUSTED` is a successful semantic terminal state. It means all currently authorized work is complete and no authorized successor exists. It is not an invitation for the runtime to search for a plausible next improvement.

The control plane must not ask the runtime to generate another execution turn merely because the current turn completed. In particular, an empty authorized queue must never be translated into prompts such as "find the next useful task", "continue improving the project", or equivalent open-ended continuation.

Agent-discovered future work may be retained only as non-authoritative proposal material, conceptually:

```text
PROPOSED_WORK
```

A proposal may describe a useful refactor, defect, investigation, or future Slice, but it has zero execution authority until an authorized planning or Human decision promotes it into the governed backlog.

Planning authority is therefore separate from execution authority. A role explicitly authorized to propose a roadmap may create proposed work. It still may not execute those proposals merely because it created them.

Semantic completion must also remain distinct from resource termination:

```text
BACKLOG_EXHAUSTED
    successful completion: no authorized work remains

BUDGET / STEP / TOKEN / TIME LIMIT
    execution safeguard: work may remain incomplete
```

A max-step, max-token, timeout, or cost limit is a watchdog. It must never substitute for the semantic completion predicate.

This boundary preserves strong agent autonomy **inside** authorized work while preventing recursive self-employment after scope is consumed.

> **An executor may decompose authorized work, but it may not extend the authoritative backlog.**

> **When no authorized successor exists, Relay stops.**

---

## 13. Core invariants

### AR-1

Relay project authority is independent of runtime state.

### AR-2

A runtime may execute only an already authorized Relay role/work packet.

### AR-3

Runtime permission is never sufficient evidence of Relay authorization.

### AR-4

Runtime/provider/model identity is captured as execution provenance but does not define workflow semantics.

### AR-5

The implementation agent may submit work but may not accept it.

### AR-6

Formal evaluation is a separately governed execution boundary.

### AR-7

Workspace isolation policy remains independent from the agent runtime.

### AR-8

OpenCode-specific features stay behind the Relay-owned runtime adapter unless a future accepted requirement explicitly promotes one into Relay semantics.

---

### AR-9

Every executable Relay action must trace to an existing authoritative work reference. Absence of such a reference means no execution authority exists.

### AR-10

Runtime-local decomposition is permitted only to satisfy the current authorized item. Internal subtasks do not become durable successor backlog.

### AR-11

Completion or closure of an authorized item consumes that item's execution scope; adjacent or follow-on work requires an independent authority basis.

### AR-12

If Relay resolves no authorized successor after item completion, the scheduler enters `BACKLOG_EXHAUSTED` and terminates successfully without another agent execution turn.

### AR-13

Agent-discovered future work is non-authoritative `PROPOSED_WORK` until explicitly promoted by an authorized planning/Human decision.

### AR-14

Semantic completion and resource exhaustion are distinct. Step, token, time, and cost limits are safety watchdogs and cannot define successful backlog completion.

---

## 14. Current conclusion

Relay should not compete with coding-agent harnesses.

It should make them governable.

The planned first implementation is:

```text
Relay governance
      ↓
AgentRuntime
      ↓
OpenCodeRuntime
      ↓
OpenCode coding-agent harness
      ↓
configured model/provider
```

This design preserves Relay's central product idea while removing a large amount of unnecessary custom agent-loop infrastructure.
