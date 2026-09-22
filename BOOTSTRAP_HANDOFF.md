# Relay — Codex Bootstrap Handoff

This starter is intentionally positioned **before the first accepted Git baseline**.

## What is already implemented

Only the Slice 0.1 engineering foundation:

```text
relay_engine package/version
operational settings
structured logging
pytest harness
Ruff/Pyright configuration
GitHub Actions CI
documentation and agent governance
```

No Relay product-domain behavior is implemented.

## First Codex session

The recommended first session is foundation validation, not feature development.

1. Read `AGENTS.md`.
2. Read `docs/CURRENT_BASELINE.md`.
3. Confirm Python 3.14 and `uv` are available.
4. Generate the dependency lock:

   ```bash
   uv lock
   ```

5. Run:

   ```bash
   uv sync --frozen --group dev
   uv run ruff format --check .
   uv run ruff check .
   uv run pyright
   uv run pytest
   uv build
   ```

6. Correct foundation-only issues if any appear. Do **not** enter Slice 0.2 implementation while fixing the foundation.
7. Commit the validated starter.
8. Record the resulting commit SHA in `docs/CURRENT_BASELINE.md`.
9. Lock `ADR-0001` and finalize the Slice 0.1 memory only after the foundation is actually evaluated and accepted.
10. Stop for explicit authorization before implementing Slice 0.2.

## Lock-file note

`uv.lock` is intentionally not fabricated in this handoff bundle. The environment that assembled this archive had no external package-index access and no Python 3.14 interpreter available, so it could not produce a trustworthy lock resolution.

The bootstrap CI therefore resolves dependencies non-frozen only while `uv.lock` is absent. Once Codex generates and commits `uv.lock`, CI automatically uses:

```text
uv sync --frozen --group dev
```

A missing lock file is **not acceptable for Slice 0.1 acceptance**.

## Suggested first Codex prompt

```text
Read AGENTS.md, docs/CURRENT_BASELINE.md, and the Slice 0.1 foundation document.
Treat this as foundation validation only. Do not implement Slice 0.2 or later capabilities.
Generate uv.lock under Python 3.14, run all canonical quality checks, fix only foundation issues,
update the Slice 0.1 memory and CURRENT_BASELINE with the exact resulting Git SHA after commit,
and stop before any next-slice implementation.
```
