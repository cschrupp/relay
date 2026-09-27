# Relay

Relay is a control plane for governed agentic software engineering.

Its core thesis is:

> **Agents perform engineering; Relay governs engineering.**

Relay is being built inside-out: deterministic engineering governance first, then repository integration, human workflow, agents, and higher autonomy.

## Current status

```text
Phase 0:                  COMPLETE / CLOSED
Core domain model:        ACCEPTED
Lifecycle engine:         ACCEPTED
Handover governance:      ACCEPTED
Persistence/events:       ACCEPTED
Repository contract:      ACCEPTED
Phase-0 protocol review:  ACCEPTED
Phase 1:                  OPEN
Slice 1.1 design:         ACCEPTED
Slice 1.1 implementation: COMPLETE / ACCEPTED
Slice 1.2:                NOT OPEN / NOT AUTHORIZED
Agent execution:          NOT IMPLEMENTED
```

The current authority is recorded in `docs/CURRENT_BASELINE.md`.

## What Relay currently provides

The accepted Phase-0 foundation includes:

- immutable provider-neutral domain values;
- deterministic lifecycle transitions and replay;
- validity / authority / autonomy handover gates;
- durable SQLite persistence and migration verification;
- authorization and human-decision persistence;
- repository-side canonical artifact governance through `.relay/registry.json`;
- exact raw-byte digest validation and repository-relative path safety;
- historical artifact locking/supersession semantics;
- explicit canonical living projections.

Slice 1.1 is accepted at `ae79b15170c88e776af99944eab9b2fdd6872c2e` under Human Authority acceptance `RLY-S11-ACCEPT-001`. It adds GitHub App JWT authentication, installation/repository discovery, project-scoped access state, fail-closed permission readiness, signed installation webhooks, optimistic concurrency, and deterministic webhook idempotency.

Slice 1.1 does **not** authorize or implement repository registration, baseline/ref resolution, remote `.relay/` writes, repository mutation, or agent execution.

## Canonical documentation

Canonical document identity is defined by `.relay/registry.json`, not by file name or modification time.

Current canonical projections include:

- Product Proposal v0.4
- Build Plan v0.4
- Current Baseline
- Documentation Governance v0.3
- Engineering Simplicity, Scope, and Quality

Current Slice 1.1 records include:

```text
docs/slices/SLICE_1_1_GITHUB_APP_INTEGRATION.md
docs/slices/SLICE_1_1_GITHUB_APP_INTEGRATION_REV2.md
docs/architecture/GITHUB_APP_INTEGRATION.md
docs/decisions/ADR-0007-github-app-authentication.md
docs/slices/SLICE_1_1_GITHUB_APP_INTEGRATION_MEMORY.md
```

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
src/relay_engine/integrations GitHub/provider-specific integration boundary
tests/                         deterministic regression coverage
docs/                          governed architecture, decisions, slices, and projections
.relay/registry.json           repository artifact/canonical contract
```
