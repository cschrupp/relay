# Relay Agent Instructions

This repository is governed by explicit engineering slices. Documentation about a future slice is **design authority, not permission to implement it**.

## Read first

Before making substantive changes, read:

1. `docs/CURRENT_BASELINE.md`
2. the currently authorized slice under `docs/slices/`
3. `docs/policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md`
4. `docs/policies/DOCUMENTATION_GOVERNANCE.md`
5. relevant ADRs under `docs/decisions/`

Read `docs/PRODUCT_PROPOSAL.md` and `docs/BUILD_PLAN.md` when broader product context is needed.

## Current implementation boundary

This starter implements **Slice 0.1 engineering foundation only**.

Do not implement domain models, lifecycle state, handover gates, persistence, GitHub integration, AI providers, sandboxes, research, experiments, or UI unless a later slice is explicitly authorized by the human project owner.

Future slice documents may be present for review. Presence does not constitute authorization.

## Core governance rules

- Start work from an explicit Git SHA once the repository is committed.
- Unblocked does not mean authorized.
- Plausible does not mean necessary.
- New architectural complexity requires present-tense evidence.
- Use no more architecture than the current problem requires, and no less clarity than a human reviewer requires.
- Abstraction must reduce cognitive load, not merely hide code.
- Do not perform unrelated refactors or speculative generalization.
- Do not add extension mechanisms for hypothetical future requirements.
- Report newly discovered work instead of silently expanding scope.
- Do not change the project toolchain as part of unrelated work.
- Existing declared quality tooling is authoritative until a tooling change is separately authorized.
- Passing tests is evidence, not acceptance.
- Do not edit locked/accepted historical records in place; use amendments or superseding records.
- Never commit secrets.

## Required quality checks

For this repository the declared quality profile is:

```text
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
```

Run all applicable checks before submitting work.

## Implementation style

Prefer:

- explicit control flow;
- small, direct functions;
- typed boundaries;
- existing repository patterns;
- local reasoning;
- narrow dependencies;
- clear failure behavior.

Avoid unless the authorized slice requires them:

- factories for a single construction path;
- registries for fixed sets;
- plugin systems without current extension requirements;
- base classes without a present shared invariant;
- event buses for direct local interactions;
- generic wrappers that only move complexity elsewhere;
- configuration switches for hypothetical alternatives.

If an abstraction is introduced, be prepared to answer:

> Which current accepted requirement becomes materially harder or impossible to satisfy without it?

## Documentation

Living canonical documents may be updated when the active slice authorizes it.

Locked records must not be rewritten. In particular, do not silently edit accepted slice records to make current work look cleaner.

## Stop conditions

Stop implementation and report the issue when:

- the requested work exceeds the authorized slice;
- a locked contract appears insufficient;
- the baseline is ambiguous;
- the required solution would materially expand the declared change surface;
- project tooling would need to change;
- a future-slice capability appears necessary.

Do not solve these conditions by broadening scope on your own.
