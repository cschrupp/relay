# Contributing to Relay

Relay uses bounded, explicitly authorized development slices.

## Before coding

Read `AGENTS.md` and `docs/CURRENT_BASELINE.md`.

Identify the exact authorized slice and, once the repository has a Git history, the exact baseline SHA.

## Scope

Implement only the accepted scope.

Do not silently:

- introduce future-slice capabilities;
- refactor unrelated code;
- generalize APIs for hypothetical use cases;
- add dependencies that are not currently necessary;
- change project tooling;
- rewrite locked engineering records.

If broader work is needed, report it as discovered work for separate authorization.

## Simplicity and clarity

Use the minimum sufficient architecture and preserve human reviewability.

The target is not minimum line count. Prefer obvious, direct code over clever compression or speculative abstraction.

See `docs/policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md`.

## Quality

Run:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
```

CI is authoritative for these checks.

## Documentation

Working artifacts may evolve. Locked records do not change in place. Living projections represent current truth.

See `docs/policies/DOCUMENTATION_GOVERNANCE.md`.

## Secrets

Never commit credentials, API keys, tokens, certificates, or private configuration.
