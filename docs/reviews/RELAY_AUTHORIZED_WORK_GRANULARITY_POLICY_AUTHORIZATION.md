# Relay — Authorized-Work Decomposition and Execution Granularity — Documentation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-23  
**Project:** Relay  
**Authority:** `RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly approves the Relay-specific authorized-work decomposition and execution-granularity direction developed from the October 2026 agent-harness research and authorizes a documentation-only repository update to make that direction durable.

The update must integrate with the existing Relay architecture.

It must not create a parallel planner/worker/reviewer state machine.

## Authorized documentation result

Create one detailed cross-cutting policy:

`docs/policies/AUTHORIZED_WORK_DECOMPOSITION_AND_EXECUTION_GRANULARITY.md`

and update the affected living/reference documents so they consistently express the same architecture.

At minimum the update may touch:

```text
docs/CURRENT_BASELINE.md
docs/BUILD_PLAN_V0_6.md
docs/PRODUCT_PROPOSAL_V0_5.md
docs/TODO.md
docs/policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md
docs/architecture/AGENT_RUNTIME.md
AGENTS.md
.relay/registry.json
```

This authority also permits adding this immutable authority record and registering the new/advanced repository artifacts required by documentation governance.

## Frozen architecture direction

The update must preserve:

```text
Relay WorkPacket
    = authoritative external work unit

DECOMPOSE_AUTHORIZED_WORK
    = bounded internal decomposition permission

internal execution step
    != Relay WorkPacket

internal milestone
    != authority gate

runtime-local planner/subagent
    != Relay role authority

planning artifact
    != Relay authority

PROPOSED_WORK
    = non-authoritative discovered future work

out-of-scope required work
    -> PROPOSED_WORK / STOP
    -> separate Relay authority required
```

Existing stable Relay role classes and authority boundaries remain intact.

No new planner/architect/researcher runtime authority class is authorized.

## Task-granularity direction

The documentation may define operational granularity bands and initial tuning targets, provided they are explicitly described as policy/calibration guidance rather than new durable domain enums or authorization semantics.

The default execution unit should be one cohesive, independently verifiable engineering outcome.

Implementers should own internal planning, sequencing, implementation, validation, repair, and self-check within the exact authorized WorkPacket rather than stopping for approval after routine internal milestones.

Surgical externally governed tasks should be the exception and require a concrete risk, integrity, security, irreversible-side-effect, scientific-certification, or authority-boundary reason.

## Research integration

The detailed policy may document the empirical basis from current coding-agent research, including long-horizon harnesses, milestone validation, runtime-local decomposition, human-calibrated task horizons, and evidence that static over-decomposition may increase retry/coordination cost.

Research evidence must not be presented as Relay authority.

Numerical task-size bands and success-rate targets must be identified as provisional calibration heuristics to be refined with Relay's own telemetry.

## Current Slice 2.4 boundary

This documentation update does not alter:

`RLY-S24-IMPL-AUTH-001 — AUTHORIZED`

or:

`RLY-S24-CODEX-SCOPE-001`.

The already-authorized Slice 2.4 implementation remains governed by its exact baseline, file surface, design, and validation contract.

No additional implementation permission is created by this documentation update.

## Explicitly not authorized

This authority does not permit:

- source-code changes;
- database/schema changes;
- lifecycle changes;
- RoleContract schema changes;
- WorkPacket schema changes;
- AgentRuntime schema changes;
- execution-workspace schema changes;
- Phase 3 opening;
- autonomous orchestration implementation;
- real-project agent execution;
- new durable task-state objects;
- new planner/task-graph persistence;
- canonical/main promotion.

## Governance rule

Historical accepted Slice 2.2 / 2.3 / 2.4 design, evaluation, and authority records remain immutable.

Current truth is advanced through living projections, new policy material, and registry revision advancement.

## Disposition

```text
RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED

Documentation re-baseline:
AUTHORIZED

Parallel architecture:
PROHIBITED

New implementation authority:
NONE

Phase 3:
NOT OPEN / NOT AUTHORIZED
```
