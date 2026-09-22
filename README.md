# Relay

Relay is a control plane for governed agentic software engineering.

Its core thesis is:

> **Agents perform engineering; Relay governs engineering.**

This repository is currently a **foundation starter**. It implements the engineering substrate defined by Slice 0.1 and intentionally does not implement Relay product-domain behavior yet.

## Current status

```text
Product capability: engineering foundation only
Domain model:       not implemented
Lifecycle engine:   not implemented
Handover gates:     not implemented
GitHub integration: not implemented
Agent execution:    not implemented
```

See `docs/CURRENT_BASELINE.md` before starting work.

## Requirements

- Python 3.14
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync --group dev
```

The committed lock file is the authoritative dependency resolution once generated/updated against Python 3.14.

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
src/relay_engine/          minimal runtime foundation
tests/unit/                foundation tests
docs/                      product, policy, slice, and decision records
AGENTS.md                   coding-agent governance instructions
.github/workflows/ci.yml   canonical CI checks
```

## Canonical documentation

Start with:

- `docs/PRODUCT_PROPOSAL.md`
- `docs/BUILD_PLAN.md`
- `docs/CURRENT_BASELINE.md`
- `docs/policies/DOCUMENTATION_GOVERNANCE.md`
- `docs/policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md`

Slice documents live in `docs/slices/`.

## Important development rule

The presence of a future slice document does **not** authorize its implementation.

Do not advance beyond the current authorized boundary without explicit human authorization.
