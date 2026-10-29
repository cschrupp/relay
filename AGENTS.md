# Relay Agent Instructions

This repository is governed by explicit engineering slices. Documentation about a future slice is **design authority or planning context, not permission to implement it**.

## Read first

Before making substantive changes, read:

1. `docs/CURRENT_BASELINE.md`
2. the currently authorized slice under `docs/slices/`, if one exists
3. `docs/policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md`
4. `docs/policies/AUTHORIZED_WORK_DECOMPOSITION_AND_EXECUTION_GRANULARITY.md`
5. `docs/architecture/HUMAN_AUTHORITY_PHASE_GATES.md`
6. `docs/policies/DOCUMENTATION_GOVERNANCE_V0_3.md`
7. relevant ADRs under `docs/decisions/`

Read `docs/PRODUCT_PROPOSAL.md` and `docs/BUILD_PLAN.md` when broader product context is needed, but resolve current canonical document identity through `.relay/registry.json`.

## Current implementation boundary

**Do not hard-code the current slice or implementation boundary from this file.**

The authoritative current boundary is `docs/CURRENT_BASELINE.md` plus the exact Human Authority records governing the active slice.

Current status changes frequently. Resolve it from `docs/CURRENT_BASELINE.md` and exact Human Authority records rather than this file. As of the October 23, 2026 documentation re-baseline, Slice 2.2 and 2.3 are closed; Slice 2.4 is open with Human-accepted design and bounded implementation authority; Phase 3 and real-project agent execution remain not open / not authorized. If this sentence ever disagrees with the canonical current baseline, the baseline governs.

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

## Authorized-work decomposition

The WorkPacket is the authoritative external work unit.

Do not turn routine internal implementation steps into separate authority gates.

When acting as an IMPLEMENTER under exact current authority:

- own the internal plan;
- inspect authorized context;
- sequence implementation work;
- run relevant validation after meaningful milestones;
- repair in-scope failures;
- self-review;
- continue without asking for approval after routine internal milestones.

An internal task, checklist item, file boundary, or milestone is not a WorkPacket.

Stop and report only when a real terminal/hard-stop condition is reached, including:

```text
DONE
BLOCKED_BY_AUTHORITY
BLOCKED_BY_CONTRACT
BLOCKED_BY_ENVIRONMENT
BUDGET_EXHAUSTED
BACKLOG_EXHAUSTED
or another exact WorkPacket hard stop
```

If correct completion requires work outside exact authority, record/report `PROPOSED_WORK` and STOP. Do not silently widen scope.

Surgical externally governed tasks are the exception. Prefer them only when narrowness itself reduces material risk, such as migrations, protected assets, irreversible operations, exact identity/digest contracts, delicate scientific/numerical certificates, or narrow independent-review corrections.

Runtime-local plans/subagents do not create Relay authority and do not replace independently governed evaluation or Human acceptance.

## Human Authority phase-gate model

Human Authority is a scarce decision resource. Do not create a Human gate merely because a segment, commit, review cycle, or internal milestone ended.

For normal bounded reversible engineering, use the Human-approved phase-gate direction in `docs/architecture/HUMAN_AUTHORITY_PHASE_GATES.md`:

```text
DESIGN FINAL + required independent design review
        ↓
HA-1 DESIGN AUTHORIZATION
        ↓
bounded implementation / CI / independent review / rework
        ↓
FINAL IMPLEMENTATION REPORT + independent ACCEPT
        ↓
HA-2 IMPLEMENTATION ACCEPTANCE
        ↓
mechanical promotion when HA-2 conditionally authorizes it
```

Request a new Human decision during implementation only for a material deviation: scope/objective change, architecture or trust-boundary change, new consequential dependency/provider/runtime/model/network/credential class, higher risk/profile, destructive/irreversible action, unapproved production/external effect, exceeded budget, or a genuine Human trade-off.

Independent `REWORK` inside the HA-1 envelope does not create a new Human authorization gate. Governance-tail/evidence/CI-record commits do not by themselves stale the reviewed engineering subject or require another Human decision.

HA-X is reserved for distinct consequential operational actions when policy requires a separate Human decision.

Until Relay's workflow implementation catches up, obey current deterministic enforcement that still requires legacy record shapes, but do not invent additional Human gates beyond current policy.

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
