# Relay — Agent Runtime Roadmap Amendment Proposal

**Status:** WORKING ROADMAP AMENDMENT — NOT CANONICAL / NOT IMPLEMENTATION AUTHORITY  
**Target:** Future revision of the canonical Build Plan after the Phase-1 M0 hard stop  
**Date:** October 2026

---

## Purpose

Record the proposed roadmap adjustment created by the decision to use an external coding-agent harness behind a Relay-owned `AgentRuntime` contract, with OpenCode as the first planned implementation.

The canonical Build Plan remains authoritative until a future governed revision advances `.relay/registry.json`.

---

## What does not change

Relay's milestone order remains sound:

```text
deterministic governance
      ↓
repository integration
      ↓
human workflow
      ↓
single-agent workflow
      ↓
independent evaluation / rework
      ↓
research / experiments
      ↓
parallel agents
      ↓
productization
```

In particular:

- Slice 1.6 Human Authorization and Decision Gates is complete / accepted / closed;
- Slice 1.7 Manual Evaluation and Acceptance is next planned, remains not open, and is required before autonomy;
- the Phase-1 M0 hard stop remains mandatory;
- Phase 3 still begins with isolated execution workspaces and reproducible work packets;
- independent evaluation, rework, and acceptance remain Relay responsibilities;
- parallel agents remain deferred until single-agent governance is proven.

---

## Proposed Phase-2 change

### Existing concept

```text
2.1 Model Provider Interface
2.2 Role Contracts
2.3 Agent Configuration and Model Routing
2.4 Context Builder
```

### Proposed concept

```text
2.1 Agent Runtime Contract
    - runtime-neutral execution/session contract
    - capability discovery
    - failure normalization
    - runtime/provider/model provenance
    - OpenCodeRuntime as first adapter
    - provider/model selection below or alongside runtime

2.2 Role Contracts
    - unchanged in purpose

2.3 Runtime / Provider / Model Routing
    - role → runtime
    - role → provider
    - role → model
    - capability validation
    - permission-profile selection

2.4 Context and Work-Packet Inputs
    - preserve bounded authoritative context
    - keep provider/runtime-specific prompt mechanics behind adapters where possible
```

The key change is that **Relay does not implement a generic coding-agent tool loop as part of the provider layer**.

---

## Proposed Phase-3 change

### 3.1 Execution Workspace

Keep the slice concept.

Workspace isolation is independent from the agent runtime. Local OpenCode worktrees may support dogfooding, but production isolation requires a stronger `WorkspaceProvider` boundary.

### 3.2 Implementation Work Packet

Keep the slice concept substantially unchanged.

The packet remains Relay-authoritative and must include exact baseline, objective, accepted architecture/contract, scope, non-authority, acceptance criteria, evidence requirements, expected change surface, and project quality profile.

### 3.3 Coding Agent Execution

Change implementation strategy:

```text
old expectation:
Relay owns model/tool loop

proposed:
Relay → AgentRuntime → OpenCodeRuntime → OpenCode harness
```

Keep the existing result contract semantics:

```text
resulting commit
changed files
implementation summary
tests run
test results
actual change surface
quality evidence
deviations
blockers
new work discovered
```

### 3.4 Evaluation Packet

Keep.

### 3.5 Independent Evaluator

Keep as a separately governed execution. It may use OpenCodeRuntime too, but it must be a distinct Relay role/session with evaluator permissions and an independent packet.

### 3.6 Automated Rework Loop

Keep. Relay owns routing between implementation and evaluator executions.

### 3.7 Acceptance and Baseline Promotion

Keep entirely Relay-owned.

---

## Proposed new architectural split

```text
                           Relay
                    governance control plane
                            │
                ┌───────────┴───────────┐
                │                       │
        WorkspaceProvider          AgentRuntime
                │                       │
      local / container / cloud    OpenCodeRuntime
                                        │
                                     OpenCode
                                        │
                                  provider/model
```

Neither backend defines Relay project authority.

---

## OpenCode-first rationale

OpenCode is the first planned runtime because it currently provides a strong reusable harness surface for Relay's needs:

- embedded/programmatic SDK;
- sessions;
- event streams;
- worktree operations;
- granular runtime permissions;
- provider/model flexibility;
- plugins/hooks;
- runtime-local subagents;
- local dogfood compatibility.

The selection is intentionally adapter-scoped so Relay can later support Codex or other runtimes without rewriting governance semantics.

---

## Required experiment before canonical lock

After the appropriate Human Authority opens future Phase-2 design/experiment work, run a bounded sidecar experiment covering:

```text
programmatic OpenCode host
exact-SHA checkout/workspace binding
session lifecycle
event stream
permission profiles
AGENTS.md behavior
provider/model provenance
file-change capture
commit capture
quality-command execution
cancel/resume
failure handling
independent implementation/evaluator sessions
local ChatGPT-auth dogfood path where applicable
```

Results should inform the canonical Build Plan revision.

---

## Governance note

This file intentionally does not modify `.relay/registry.json`.

It is a working amendment proposal. The canonical Build Plan v0.5 remains current until a later authorized living-projection revision advances the registry.
