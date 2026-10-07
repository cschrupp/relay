# Relay

Relay is a control plane for governed agentic software engineering.

Its core thesis is:

> **Agents perform engineering; Relay governs engineering.**

Relay is being built inside-out: deterministic engineering governance first, then repository integration, human workflow, bounded agent execution, independent evaluation, and higher autonomy.

## Current status

```text
Phase 0:                  COMPLETE / CLOSED
Phase 1:                  ACCEPTED BASELINE / HARDENING ACTIVE
Slices 1.1–1.7:           COMPLETE / ACCEPTED / CLOSED
Phase 1 M0 viability:     ACCEPTED / HUMAN-ACCEPTED
Phase 2:                  OPEN
Slice 2.1:                OPEN — SUCCESSOR ACCEPTED / SIDECAR REAUTH REQUIRED
Agent execution:          NOT AUTHORIZED
```

The current authority is recorded in `docs/CURRENT_BASELINE.md`.

## What Relay currently provides

The accepted foundation now includes:

- immutable provider-neutral domain values;
- deterministic lifecycle transitions and replay;
- validity / authority / autonomy handover gates;
- durable SQLite persistence and migration verification;
- authorization and human-decision persistence;
- repository-side canonical artifact governance through `.relay/registry.json`;
- exact raw-byte digest validation and repository-relative path safety;
- historical artifact locking/supersession semantics;
- explicit canonical living projections;
- accepted GitHub App read integration with project-scoped installation/repository state;
- fail-closed provider permission readiness;
- signed GitHub installation webhooks;
- optimistic integration-state concurrency;
- deterministic webhook redelivery idempotency;
- provider-neutral repository baseline resolution;
- governed `.relay/` initialization and synchronization;
- governed Project / Slice administration;
- server-rendered Board Projection derived from governed state, with bounded
  Human Authority actions for gate decisions, holds, and governed ADVANCE/CANCEL.

Slice 1.5 closed at canonical closure head `45a3acbc5a26c618176a2d5da32a70b67adb9883`.

## Agent runtime direction

Relay will **not** implement a bespoke coding-agent reasoning/tool loop unless a future accepted requirement proves that necessary.

The planned boundary is:

```text
Relay
  ├─ governance / authority
  ├─ role contracts
  ├─ work packets
  ├─ workspace policy
  ├─ evidence / provenance
  ├─ independent evaluation
  └─ acceptance / baseline promotion
        │
        ▼
   AgentRuntime
        │
        ├─ OpenCodeRuntime   ← first planned implementation
        └─ future runtimes   ← e.g. Codex or other compatible harnesses
```

The first planned runtime is **OpenCode** because it provides an embeddable coding-agent harness with sessions, event streaming, worktree support, permissions, provider/model flexibility, plugins, and subagents while allowing Relay to retain ownership of engineering governance.

OpenCode is an execution substrate, not a source of project authority. Relay remains responsible for exact baselines, authorization, role boundaries, independent evaluation, rework routing, human decisions, and acceptance.

Phase 2 is open under the accepted-baseline / active-hardening model. Slice 2.1 is open and its Agent Runtime Contract design is Human-accepted under `RLY-S21-DESIGN-ACCEPT-001`. The original deterministic successor `ded3ed03...` received `RLY-S21-EVAL-002 — ACCEPT`, but Run 007 exposed a live prompt-schema defect at D21-05. Rework successor `5df1add9ed829a62a99d7f25f561a0f492ff5c73` now received `RLY-S21-EVAL-003 — ACCEPT` with exact-head CI `37673385489 — SUCCESS`. Human technical acceptance remains blocked because the existing sidecar authorization is explicitly SHA-bound to `ded3ed03...`; a new narrow Human Authority record is required before live D21 evidence may resume against the successor. Phase 3 work and Relay agent execution against real work remain unauthorized. Phase 1 remains the accepted deterministic baseline and continues under separately authorized hardening.

See:

- `docs/architecture/AGENT_RUNTIME.md`
- `docs/decisions/ADR-0011-agent-runtime-opencode-first.md`
- `docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT.md`
- `docs/slices/SLICE_3_3_CODING_AGENT_EXECUTION.md`

## Canonical documentation

Canonical document identity is defined by `.relay/registry.json`, not by file name or modification time.

Current canonical projections include:

- Product Proposal v0.5
- Build Plan v0.6
- Current Baseline
- Documentation Governance v0.3
- Engineering Simplicity, Scope, and Quality

The OpenCode / AgentRuntime documents above are currently **working future-architecture artifacts** and are not canonical implementation authority.

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

## Repository structure

```text
src/relay_engine/              Relay runtime foundation
src/relay_engine/integrations  GitHub/provider-specific integration boundary
tests/                         deterministic regression coverage
docs/                          governed architecture, decisions, slices, and projections
.relay/registry.json           repository artifact/canonical contract
```
