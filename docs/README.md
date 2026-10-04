# Relay Documentation

Relay documentation distinguishes current projections from historical engineering records and working future-architecture artifacts.

Canonicality is defined by `.relay/registry.json`, not by filename recency.

## Canonical living documents

Current registry targets are:

- `PRODUCT_PROPOSAL_V0_5.md`
- `BUILD_PLAN_V0_5.md`
- `CURRENT_BASELINE.md`
- `policies/DOCUMENTATION_GOVERNANCE_V0_3.md`
- `policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md`

Older versioned or unversioned proposal/plan/policy files remain historical repository content and are not current merely because they are present.

## Current future-architecture direction

Relay plans to introduce agent execution through a Relay-owned `AgentRuntime` boundary rather than by implementing a bespoke model/tool loop.

The first planned runtime implementation is **OpenCode**. OpenCode is intended to own runtime-local coding-agent mechanics such as model/tool iteration, context management, file and shell tool use, and optional runtime-local subagents. Relay retains authority over exact baselines, authorization, role contracts, work packets, workspace policy, evidence, independent evaluation, rework routing, Human Authority, and acceptance.

Current working documents for this direction are:

- `architecture/AGENT_RUNTIME.md`
- `decisions/ADR-0011-agent-runtime-opencode-first.md`
- `slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT.md`
- `slices/SLICE_3_3_CODING_AGENT_EXECUTION.md`

These are **future planning/design artifacts**. They are not current canonical implementation authority and do not open or authorize Phase 2 or Phase 3 work.

Slice 1.7 — Manual Evaluation and Acceptance — is next planned and remains not open. Agent execution is not authorized.

## Slice records

See `slices/`.

A slice design record may be reviewed or locked without authorizing implementation. Authorization is a separate Human Authority event.

Future-slice proposals must state their non-authority explicitly until the corresponding slice is opened.

## Decisions

See `decisions/`.

Locked ADRs are historical authority and should be amended or superseded rather than rewritten. Proposed ADRs may capture a selected strategic direction before the implementation slice is authorized, provided their status is explicit.

## Reviews and authority records

See `reviews/`.

Submitted evaluations and Human Authority decisions are preserved as historical records.

## Architecture

Accepted or working slice architecture documents live under `architecture/`.

`architecture/AGENT_RUNTIME.md` describes the planned boundary between Relay governance and external coding-agent harnesses. OpenCode is the first planned implementation, but runtime-specific features must not become Relay domain authority.

Current authority and the next planned engineering gate are recorded in `CURRENT_BASELINE.md`.
