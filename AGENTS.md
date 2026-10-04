# Relay Agent Instructions

This repository is governed by explicit engineering slices. Documentation about a future slice is **design authority or planning context, not permission to implement it**.

## Read first

Before making substantive changes, read:

1. `docs/CURRENT_BASELINE.md`
2. the currently authorized slice under `docs/slices/`, if one exists
3. `docs/policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md`
4. `docs/policies/DOCUMENTATION_GOVERNANCE.md`
5. relevant ADRs under `docs/decisions/`

Read `docs/PRODUCT_PROPOSAL.md` and `docs/BUILD_PLAN.md` when broader product context is needed, but resolve current canonical document identity through `.relay/registry.json`.

## Current implementation boundary

**Do not hard-code the current slice or implementation boundary from this file.**

The authoritative current boundary is `docs/CURRENT_BASELINE.md` plus the exact Human Authority records governing the active slice.

As of the current repository baseline, Slices 1.1–1.6 are complete / accepted / closed, Slice 1.7 — Manual Evaluation and Acceptance — is next planned but not open, and agent execution is not authorized. If these statements ever disagree with `docs/CURRENT_BASELINE.md`, the canonical current baseline governs.

Future slice documents may be present for review. Presence does not constitute authorization.

## Agent runtime direction

Relay's planned future agent-execution boundary is an `AgentRuntime` abstraction. The first planned implementation is OpenCode.

This is a future architecture direction only. It does not authorize implementation of OpenCode integration, provider/model routing, execution workspaces, coding-agent execution, autonomous evaluation, or rework loops until the corresponding slices are explicitly opened and authorized.

When agent execution is eventually authorized:

- Relay owns governance, exact baselines, authorization, role contracts, work packets, evidence, evaluation routing, human decisions, and acceptance.
- The external agent runtime owns its internal reasoning/tool loop, context management, tool iteration, and runtime-local subagents.
- Runtime-local subagents do not replace Relay's independently governed evaluator or Human Authority boundaries.
- Runtime permissions are defense in depth; they do not replace Relay authorization.

See `docs/architecture/AGENT_RUNTIME.md` for the proposed boundary.

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

Run all applicable checks before submitting implementation work. Documentation-only work should still preserve repository consistency and must not claim implementation evidence that was not produced.

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

Living canonical documents may be updated only under appropriate current authority and must remain synchronized with `.relay/registry.json` according to repository-contract rules.

Locked records must not be rewritten. In particular, do not silently edit accepted slice records to make current work look cleaner.

Working future-architecture documents must clearly state that they are not implementation authorization.

## Stop conditions

Stop implementation and report the issue when:

- the requested work exceeds the authorized slice;
- a locked contract appears insufficient;
- the baseline is ambiguous;
- the required solution would materially expand the declared change surface;
- project tooling would need to change;
- a future-slice capability appears necessary;
- a runtime or model feature would bypass Relay's authorization or independent-evaluation boundaries.

Do not solve these conditions by broadening scope on your own.
