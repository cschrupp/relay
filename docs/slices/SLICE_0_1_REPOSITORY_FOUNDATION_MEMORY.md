# Slice 0.1 — Repository Foundation and Engineering Baseline — Development Memory

**Status:** STARTER IMPLEMENTED / VALIDATION PENDING  
**Baseline:** No accepted Git SHA yet  
**Result SHA:** Pending first repository commit and evaluation

---

## Objective

Create the smallest reproducible engineering foundation required before Relay product-domain implementation.

## Implemented in this starter

- Python package `relay_engine`;
- package version `0.1.0.dev0`;
- operational settings through `pydantic-settings`;
- structured console/JSON logging through `structlog`;
- pytest unit-test harness;
- Ruff format/lint configuration;
- strict Pyright configuration for production source;
- Hatchling package build;
- GitHub Actions quality workflow;
- root `AGENTS.md` for Codex/agent governance;
- canonical project documentation and policies.

## Explicitly not implemented

- core Relay domain model;
- lifecycle/state machine;
- handover gates;
- persistence;
- `.relay/` schema;
- GitHub App integration;
- AI providers or agents;
- execution sandbox;
- research or experiments;
- board/UI.

## Dependency-lock status

`uv.lock` is pending generation in a Python 3.14 environment with package-index access.

The archive-building environment could not create a trustworthy lock because it had neither Python 3.14 nor external package-index access.

This prevents Slice 0.1 from being marked accepted yet.

## Validation still required

```text
uv lock
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
```

## Hard stop

After the foundation is validated, committed, and its exact SHA recorded, stop for explicit authorization before implementing Slice 0.2.
