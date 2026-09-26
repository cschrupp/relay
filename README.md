# Relay

Relay is a control plane for governed agentic software engineering.

Its core thesis is:

> **Agents perform engineering; Relay governs engineering.**

Relay is being built inside-out: deterministic engineering governance first, then repository integration, human workflow, agents, and higher autonomy.

## Current status

```text
Phase 0:                 COMPLETE / CLOSED
Core domain model:       ACCEPTED
Lifecycle engine:        ACCEPTED
Handover governance:     ACCEPTED
Persistence/events:      ACCEPTED
Repository contract:     ACCEPTED
Phase-0 protocol review: ACCEPTED
Phase 1:                 OPEN
Slice 1.1:               DESIGN ONLY
Slice 1.1 implementation: NOT AUTHORIZED
Agent execution:         NOT IMPLEMENTED
```

The current authority is recorded in `docs/CURRENT_BASELINE.md`.

## What Phase 0 provides

Relay currently implements:

- immutable provider-neutral domain values;
- deterministic lifecycle transitions and replay;
- validity / authority / autonomy handover gates;
- durable SQLite persistence and migration verification;
- authorization and human-decision persistence;
- repository-side canonical artifact governance through `.relay/registry.json`;
- exact raw-byte digest validation and repository-relative path safety;
- historical artifact locking/supersession semantics;
- explicit canonical living projections.

Phase 1 has now opened. Slice 1.1 is **design only** and concerns GitHub App integration. No GitHub product implementation is authorized until that design is independently reviewed and Human Authority separately authorizes implementation.

## Canonical documentation

Canonical document identity is defined by `.relay/registry.json`, not by file name or modification time.

Current canonical projections include:

- Product Proposal v0.4
- Build Plan v0.4
- Current Baseline
- Documentation Governance v0.3
- Engineering Simplicity, Scope, and Quality

Phase-0 protocol review:

```text
docs/reviews/PHASE_0_PROTOCOL_REVIEW.md
```

Phase-0 review acceptance / Phase-1 opening:

```text
docs/reviews/PHASE_0_PROTOCOL_REVIEW_ACCEPTANCE.md
```

Current Slice 1.1 design:

```text
docs/slices/SLICE_1_1_GITHUB_APP_INTEGRATION.md
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
src/relay_engine/          accepted Relay runtime foundation
tests/                     deterministic regression coverage
docs/                      product, policy, architecture, slice, and review records
.relay/registry.json       schema-v1 canonical artifact registry
AGENTS.md                   coding-agent governance instructions
.github/workflows/ci.yml   canonical CI checks
```

## Development rule

**Unblocked is not authorized.**

The existence of a design, roadmap entry, passing CI, or passing review does not authorize implementation. Follow the current authority recorded in `docs/CURRENT_BASELINE.md`.
