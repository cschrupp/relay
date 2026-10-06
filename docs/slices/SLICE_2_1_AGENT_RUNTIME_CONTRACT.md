# Slice 2.1 — Agent Runtime Contract

**Status:** OPEN — DESIGN ACCEPTED / IMPLEMENTATION AUTHORIZED  
**Phase:** 2 — Provider and Agent Foundation  
**Opening authority:** `RLY-S21-OPEN-001`  
**Design authority:** `RLY-S21-DESIGN-AUTH-001 — AUTHORIZED`  
**Human design acceptance:** `RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED`  
**Exact accepted design head:** `fc55a50167e8c83d05bad9664c6b8e8fed59db42`  
**Implementation authority:** `RLY-S21-IMPL-AUTH-001 — AUTHORIZED`  
**Authorized implementation baseline:** `aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22`  
**Opening baseline:** `eac62b054af3815cc179c95d0d31aa96f9a374e3`  
**Supersedes roadmap concept:** low-level `Model Provider Interface` as the primary orchestration boundary  
**First planned runtime:** OpenCode

---

## Objective

Define the Relay-owned contract for executing governed engineering roles through an external coding-agent runtime without coupling Relay project semantics to one harness, provider, or model family.

The first planned implementation of the contract is `OpenCodeRuntime`.

The detailed Agent Runtime Contract design has been independently reviewed and Human-accepted. This document remains a roadmap/proposal summary; the accepted Revision 1 + Revision 2 + Revision 3 design records govern implementation semantics. Implementation is separately authorized under `RLY-S21-IMPL-AUTH-001` for deterministic contract/OpenCode-adapter code only. Live runtime execution remains unauthorized.

---

## Problem statement

Relay needs coding-agent capability, but its product thesis does not require Relay to own a generic model/tool loop.

The boundary should therefore be:

```text
Relay governance
      ↓
AgentRuntime contract
      ↓
runtime adapter
      ↓
external coding-agent harness
      ↓
provider/model
```

Provider/model choice remains configurable, but Relay should not directly encode every provider's tool protocol into lifecycle and governance logic.

---

## Required design decisions

Slice 2.1 must define at least:

```text
runtime identity
runtime capability discovery
session identity
execution start contract
execution event contract
steering contract
cancel contract
resume contract
result inspection contract
failure normalization
runtime/provider/model provenance
permission-profile attachment
workspace attachment
credential reference semantics
usage/cost reporting where available
```

The design must distinguish required capabilities from optional runtime-specific capabilities.

---

## Proposed conceptual interface

The exact language/API is intentionally deferred to design review, but the shape should remain similar to:

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

Relay-owned value objects should cross this boundary. OpenCode SDK object types should remain inside the adapter.

---

## First adapter: OpenCodeRuntime

The first planned adapter should map Relay concepts onto OpenCode capabilities such as:

```text
Relay execution         → OpenCode session
Relay workspace         → OpenCode location/worktree binding
Relay permission profile→ OpenCode permissions/policies
Relay runtime events    ← OpenCode event stream
Relay role prompt       → OpenCode session prompt/context
Relay cancel            → runtime cancellation
Relay result inspection ← session/diff/tool evidence
```

The mapping is implementation detail and must not invert authority.

OpenCode session state must never become authoritative Relay project state.

---

## Provider and model routing

This slice should preserve provider/model flexibility beneath or alongside the runtime abstraction.

Conceptually:

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

Requirements:

- runtime selection independent of workflow semantics;
- provider selection independent of workflow semantics;
- model selection independent of workflow semantics;
- capability validation before execution;
- provider/runtime/model identity captured in execution provenance;
- credentials referenced externally and never committed to `.relay/`.

Local dogfooding may use provider authentication mechanisms available through OpenCode, including ChatGPT account authentication where supported. Production auth/billing remains a separate design concern.

---

## Runtime permissions

Relay should compile or translate a governed execution policy into runtime permissions where the runtime supports them.

Example intent:

```text
read authorized workspace          allow
edit authorized workspace          allow
inspect Git                        allow
run declared quality commands      allow/ask per policy
commit authorized result           allow/ask per policy
push                               deny unless separately authorized
external filesystem access         deny by default
unapproved network/tool access     deny/ask per policy
```

Important invariant:

> Runtime permissions enforce Relay authority; they do not define Relay authority.

A misconfigured runtime policy must not allow Relay to start an otherwise unauthorized execution.

---

## Workspace separation

The runtime contract must consume a workspace reference supplied by Relay's execution-workspace layer.

`AgentRuntime` must not silently provision an authority-expanding workspace on its own.

For local dogfood, an OpenCode-managed Git worktree may be an implementation backend. Production isolation remains governed by the later Execution Workspace slice.

---

## Event normalization

Relay should preserve useful runtime detail while exposing a small stable event vocabulary.

Candidate normalized events:

```text
ExecutionStarted
ExecutionProgress
ToolRequested
ToolCompleted
PermissionRequired
ExecutionBlocked
ExecutionCompleted
ExecutionFailed
ExecutionCancelled
```

Raw runtime event metadata may be retained as provenance where useful.

Runtime event arrival must not directly mutate Relay lifecycle state without the deterministic Relay transition/gate path.

---

## Failure semantics

The contract should distinguish at least:

```text
configuration/capability failure
workspace failure
authentication failure
provider/model failure
runtime crash
permission denial
agent-declared blocker
execution timeout/resource limit
user/system cancellation
result-contract failure
```

Normalization must not erase runtime/provider detail needed for diagnosis.

---

## In scope

- `AgentRuntime` contract design;
- runtime capability model;
- normalized runtime/session/error contracts;
- OpenCode adapter design;
- provider/model routing placement;
- runtime permission-profile semantics;
- execution provenance requirements;
- bounded sidecar validation plan.

---

## Out of scope

- production coding-agent execution;
- Phase-3 execution workspace implementation;
- automated evaluation/rework;
- acceptance;
- production cloud sandbox infrastructure;
- replacing Relay lifecycle state with runtime session state;
- multi-agent DAG scheduling;
- runtime-local subagents acting as Relay evaluators;
- committing secrets or provider credentials.

---

## Required sidecar evidence before implementation acceptance

A separately authorized experiment should demonstrate:

```text
OpenCode SDK can be invoked programmatically
sessions can be created and observed
runtime events are available
permissions can deny/ask/allow expected operations
workspace scope is enforceable enough for local dogfood
AGENTS.md/project context behaves predictably
provider/model identity can be recorded
execution can be cancelled
session behavior after interruption is understood
runtime failures can be normalized
```

This evidence informs implementation but does not substitute for independent design review.

---

## Exit bar

```text
[ ] AgentRuntime contract is runtime-neutral
[ ] OpenCode-specific types remain behind adapter boundary
[ ] provider/model routing remains independent of Relay workflow semantics
[ ] required vs optional capabilities are explicit
[ ] runtime permission semantics are subordinate to Relay authority
[ ] workspace ownership boundary is explicit
[ ] event normalization cannot bypass deterministic Relay transitions
[ ] failure categories are explicit
[ ] provenance captures runtime/provider/model/config identity
[ ] credential references remain external to repository state
[ ] bounded OpenCode sidecar protocol is defined
[ ] no production agent execution is enabled by this slice alone
```

---

## Hard stop

Do not proceed to coding-agent execution merely because OpenCode can run successfully.

The next step requires separately accepted role contracts, context/work-packet semantics, execution-workspace authority, and explicit Human Authority for Phase 3.
