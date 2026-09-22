# ADR-0001 — Runtime and Tooling Baseline

**Status:** PROPOSED / STARTER IMPLEMENTED FOR VALIDATION  
**Date:** September 2026

## Context

Relay needs a small reproducible engineering substrate before product-domain implementation begins.

## Decision

The starter uses:

```text
Python 3.14
uv
hatchling
Pydantic / pydantic-settings
structlog
Ruff
Pyright
pytest
GitHub Actions
```

The Python distribution is `relay-engine` and the import package is `relay_engine`.

The repository is backend-first; no frontend, API framework, database, GitHub SDK, AI-provider SDK, sandbox, or `.relay/` schema is introduced by this decision.

## Rationale

The stack provides a compact typed/tested foundation while preserving the Slice 0.1 boundary.

## Consequences

- all quality checks are explicit and reproducible;
- runtime dependencies remain minimal;
- future tooling changes require explicit authorization;
- this ADR should become `LOCKED` only after the starter is validated and accepted in the real Git repository.
