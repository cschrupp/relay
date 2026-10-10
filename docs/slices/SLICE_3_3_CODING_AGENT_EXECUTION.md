# Slice 3.3 — Coding Agent Execution (Superseded Roadmap Number)

**Status:** SUPERSEDED WORKING ROADMAP PROPOSAL — SEE SLICE 3.1 / NOT OPEN / NOT AUTHORIZED  
**Phase:** 3 — First Autonomous Engineering Loop  
**Planned runtime:** `OpenCodeRuntime` through Relay `AgentRuntime`

---

> Roadmap note: `RLY-P2-ROADMAP-REBASE-001` re-numbered the first autonomous coding-agent execution work as **Slice 3.1** after moving Role Contracts, Context/Work-Packet semantics, and Execution Workspace Authority into Phase 2 prerequisites. This file is retained as working historical context only. Use `SLICE_3_1_CODING_AGENT_EXECUTION.md` for the current future proposal.

## Objective

Execute one authorized implementation role in one isolated workspace through the Relay-owned `AgentRuntime` contract and return a normalized implementation result without allowing the implementation agent to accept its own work.

The first planned runtime path is:

```text
Relay authorization
      ↓
Execution Workspace
      ↓
Implementation Work Packet
      ↓
AgentRuntime
      ↓
OpenCodeRuntime
      ↓
OpenCode coding-agent harness
      ↓
configured provider/model
```

Relay must not implement a second internal model/tool loop around OpenCode.

---

## Preconditions

Execution may begin only when all required upstream authority is valid.

At minimum:

```text
slice exists and is in the correct lifecycle state
implementation is explicitly authorized
baseline SHA exactly matches authorization
role contract version matches authorization
work packet is reproducible from authoritative state
workspace is provisioned for the exact baseline
runtime configuration is valid
provider/model capability requirements are satisfied
permission profile is derived from the authorized role/scope
required credentials are explicitly granted
no hard stop blocks execution
```

An OpenCode session being technically runnable is not sufficient.

---

## Agent return contract

Relay should normalize the runtime result into at least:

```text
execution ID
runtime/session identity
runtime version/config identity
provider/model identity
starting baseline SHA
resulting commit SHA
changed files
implementation summary
tests / quality checks requested
tests / quality checks actually run
test / quality results
actual change surface
deviations
permission denials / escalations
blockers
new work discovered
runtime warnings/errors
usage/cost data where available
```

The exact result schema is designed under the authorized slice.

---

## Runtime event handling

OpenCode runtime events may be translated into Relay execution observations, but they must not bypass Relay's deterministic lifecycle and gate machinery.

Examples:

```text
OpenCode session created
      → execution observation

OpenCode permission required
      → Relay may surface BLOCKED / human action required according to policy

OpenCode file edited
      → execution evidence / changed-file observation

OpenCode session error
      → execution failure observation

OpenCode session idle/completed
      → trigger result inspection, not automatic acceptance
```

A runtime event is evidence about execution state, not direct authority to promote project state.

---

## Permission profile

Relay should provide OpenCode with the narrowest permission profile that satisfies the authorized role.

A candidate implementation-agent profile may permit:

```text
read authorized workspace
edit authorized workspace
Git inspection
approved build/test/lint/type-check commands
bounded commit creation if the slice contract requires it
```

and should deny or separately gate:

```text
push
merge
external filesystem mutation
unapproved credentials
unapproved network access
repository/provider administration
editing locked historical authority
changing project tooling without authorization
```

The runtime profile is enforcement support. The source of authority remains Relay.

---

## `AGENTS.md` and authoritative context

OpenCode may load repository guidance such as `AGENTS.md`, but Relay must still construct the authoritative role/work packet from canonical and baseline-specific state.

`AGENTS.md` is repository guidance, not a substitute for:

```text
exact authorization
role contract
baseline
accepted architecture
accepted contract
scope / out-of-scope
required evidence
current relevant memory
```

If repository guidance conflicts with current canonical authority, Relay should fail visibly rather than silently choose one.

---

## Runtime-local subagents

The implementation runtime may use OpenCode subagents for bounded internal tasks when permitted, such as:

```text
repository exploration
test investigation
dependency analysis
localized code review before submission
```

Runtime-local subagents remain part of the same implementation execution authority.

They may not:

- act as Relay's formal independent evaluator;
- accept the implementation;
- expand slice scope;
- create new authorization;
- bypass runtime or Relay permissions.

---

## Commit production

The implementation execution should normally produce an immutable result commit when the authorized work completes successfully.

Relay must verify:

```text
commit descends from authorized baseline as required by contract
changed-file manifest matches repository diff
unauthorized paths are detectable
resulting SHA is exact
quality evidence refers to the submitted result
no silent push/merge occurred unless explicitly authorized
```

The commit is a submission candidate, not an accepted baseline.

---

## Quality checks

The agent should consume the project-selected quality profile from the work packet.

For Relay itself, the currently declared profile is:

```text
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
```

The runtime must not replace repository tooling merely because it prefers another toolchain.

If a required check cannot run, the result must say so explicitly.

Passing checks is evidence, not acceptance.

---

## Failure and blocker handling

The execution must stop or return a governed blocker when, for example:

```text
baseline is wrong
role contract is stale
work packet conflicts with repository authority
required toolchain is unavailable
solution requires unauthorized scope expansion
locked contract appears insufficient
required external credential is unavailable
runtime permission correctly denies a necessary action
network/provider failure prevents completion
runtime cannot produce the required result contract
```

The agent must report discovered work rather than silently broadening scope.

---

## Independence after implementation

Successful completion routes to Relay's Evaluation Packet slice.

Correct flow:

```text
Implementation execution
      ↓
normalized result commit + evidence
      ↓
Relay builds Evaluation Packet
      ↓
separately governed evaluator execution/session
      ↓
ACCEPT / REWORK / escalation outcome
```

The implementation session's own assessment may be retained as informational evidence but must not dominate or replace independent evaluation.

---

## In scope

- execute one implementation role;
- use `AgentRuntime` / `OpenCodeRuntime`;
- bind execution to exact workspace/baseline;
- translate Relay policy into runtime permissions;
- consume a Relay work packet;
- stream/store execution observations;
- capture commit, diff/change surface, quality evidence, blockers, and provenance;
- normalize success/failure/cancellation.

---

## Out of scope

- formal evaluation in the same session;
- acceptance or baseline promotion;
- automatic merge/push by default;
- multi-slice scheduling;
- parallel production agents;
- architecture/contract rewriting by implementation agent;
- runtime-specific concepts becoming Relay lifecycle authority;
- treating OpenCode worktree isolation as sufficient production tenant isolation;
- provider/model lock-in.

---

## Exit bar

```text
[ ] execution starts only from exact authorized baseline
[ ] Relay work packet is the authoritative execution input
[ ] OpenCode is invoked through AgentRuntime adapter boundary
[ ] runtime-specific types do not leak into Relay domain semantics
[ ] permission profile is derived from Relay authority
[ ] unauthorized paths/actions are detectable and fail visibly
[ ] resulting commit SHA captured exactly
[ ] changed-file manifest captured
[ ] actual change surface captured
[ ] declared quality checks executed or explicitly reported unavailable
[ ] quality evidence tied to submitted result
[ ] runtime/provider/model/config provenance captured
[ ] blockers and deviations structured
[ ] cancellation/failure semantics deterministic at Relay boundary
[ ] runtime-local subagents cannot perform formal Relay evaluation
[ ] implementation cannot accept or promote its own result
[ ] no automatic push/merge unless separately authorized
```

---

## Hard stop

A successful OpenCode execution does not advance the result to accepted state.

The result must proceed through Relay's separately governed evaluation and acceptance path.
