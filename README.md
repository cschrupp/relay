# Relay

Relay is a control plane for governed agentic software engineering.

Its core thesis is:

> **Agents perform engineering; Relay governs engineering.**

Relay is being built inside-out: deterministic engineering governance first, then governed runtime/role/context/workspace foundations, then bounded autonomous execution.

## Current status

```text
Phase 0:                  COMPLETE / CLOSED
Phase 1:                  ACCEPTED BASELINE / HARDENING ACTIVE
Slices 1.1-1.7:           COMPLETE / ACCEPTED / CLOSED
Phase 1 M0 viability:     ACCEPTED / HUMAN-ACCEPTED
Slice 1.8:                OPEN / DESIGN AUTHORIZED / PAUSED — ARCHITECTURE / ROADMAP REBASE
Slice 1.9:                Human Decision Support — PLANNED / NOT OPEN / NOT AUTHORIZED
Slice 1.10:               Canonical Source / Promotion — PLANNED / NOT OPEN / NOT AUTHORIZED
Phase 2:                  OPEN
Slice 2.1:                COMPLETE / ACCEPTED / CLOSED
Slice 2.2:                PLANNED / NOT OPEN
Slice 2.3:                PLANNED / NOT OPEN
Slice 2.4:                PLANNED / NOT OPEN
Phase 3:                  NOT OPEN / NOT AUTHORIZED
Real-project execution:   NOT AUTHORIZED
```

The current authority is recorded in `docs/CURRENT_BASELINE.md`.

## What Relay currently provides

The accepted foundation includes:

- immutable provider-neutral domain values;
- deterministic lifecycle transitions and replay;
- validity / authority / autonomy handover gates;
- durable SQLite persistence and migration verification;
- authorization and Human-decision persistence;
- canonical artifact governance through `.relay/registry.json`;
- exact raw-byte digest validation and repository-relative path safety;
- immutable historical authority and explicit living projections;
- GitHub repository integration and governed baseline resolution;
- Project / Slice administration;
- Board Projection and bounded Human Authority actions;
- manual evaluation, technical acceptance, and accepted-result promotion;
- a Relay-owned `AgentRuntime` contract with an accepted OpenCode adapter;
- live sidecar evidence for execution, provenance, cancellation, failure normalization, and evaluator-session separation.

Slice 2.1 closed at canonical head `ad0444337efcddb5694d14a57a99c22d18cdfb9c`.

## Architecture direction

Relay is an **AI software-development and governance framework**. External standards validate applicable parts of Relay; they do not define Relay.

```text
Relay native governance
        |
        +-- Control / Governance Plane
        +-- Execution Plane
        +-- Evidence / Provenance Plane
        +-- Verification Plane
        +-- Promotion Plane
        |
        +-- external assurance mappings
             +-- SLSA [SRC-SLSA-V1_2]
             +-- NIST SSDF [SRC-NIST-SSDF-1_1]
             +-- DORA [SRC-DORA-CHANGE-APPROVAL]
             +-- future standards / enterprise policy
```

The governing direction is:

> **Relay semantics -> external compliance proof, never external standards -> Relay semantics.**

See `docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md` and `docs/references/GOVERNANCE_ASSURANCE_AND_AGENTIC_SDLC_SOURCES.md`. External references inform mappings; they do not define Relay authority.

## Re-baselined development sequence

```text
Phase 1 — Deterministic Governance Foundation
  1.8 Governance Assurance Reference Model        OPEN — PAUSED FOR REBASE
  1.9 Human Decision Support & Governance Review  PLANNED / NOT AUTHORIZED
  1.10 Canonical Source and Promotion Enforcement PLANNED / NOT AUTHORIZED

Phase 2 - provider and agent foundation
  2.1 Agent Runtime Contract                      CLOSED
  2.2 Role Contracts                             PLANNED
  2.3 Context and Work-Packet Contract           PLANNED
  2.4 Execution Workspace Authority              PLANNED

Phase 3 - first governed autonomous engineering loop
  3.1 Coding Agent Execution                     FUTURE / NOT AUTHORIZED
```

Phase 3 cannot begin merely because OpenCode can execute successfully.

## Agent runtime boundary

Relay does **not** own a generic coding-agent reasoning/tool loop unless a future accepted requirement proves one necessary.

```text
Relay governance
  -> Role Contract
  -> Work Packet
  -> Workspace Authority
  -> AgentRuntime
  -> OpenCodeRuntime / future runtime
  -> configured provider/model
```

OpenCode is an execution substrate, not project authority. Runtime permission never creates Relay authorization.

## Governance assurance direction

The immediate hardening frontier is to make Relay's assurance model explicit and then make technical source/promotion enforcement match declared governance.

Historical roadmap-rebaseline evidence recorded:

```text
main protected = false
repository rulesets = []
```

Those facts remain historical design input for planned Slice 1.10. They do not authorize repository-settings changes.

## Canonical documentation

Canonical document identity is defined by `.relay/registry.json`, not filename or modification time.

Current canonical projections include:

- Product Proposal v0.5
- Build Plan v0.6
- Current Baseline
- Documentation Governance v0.3
- Engineering Simplicity, Scope, and Quality

Working future architecture/slice proposals are not implementation authority merely because they exist.

## Key references

- `docs/architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md`
- `docs/architecture/AGENT_RUNTIME.md`
- `docs/decisions/ADR-0011-agent-runtime-opencode-first.md`
- `docs/slices/SLICE_1_8_GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md`
- `docs/architecture/HUMAN_DECISION_SUPPORT.md`
- `docs/slices/SLICE_1_9_HUMAN_DECISION_SUPPORT_GOVERNANCE_REVIEW_SURFACE.md`
- `docs/slices/SLICE_1_9_CANONICAL_SOURCE_PROMOTION_ENFORCEMENT.md`
- `docs/slices/SLICE_1_10_CANONICAL_SOURCE_PROMOTION_ENFORCEMENT.md`
- `docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT.md`
- `docs/slices/SLICE_2_2_ROLE_CONTRACTS.md`
- `docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT.md`
- `docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY.md`
- `docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION.md`

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync --group dev
```

## Quality checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
```
