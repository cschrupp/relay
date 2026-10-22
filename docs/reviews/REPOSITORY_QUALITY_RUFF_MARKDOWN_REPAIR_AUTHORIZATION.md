# Relay — Repository Quality Baseline — Ruff Markdown Format Boundary Repair Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-QUALITY-RUFF-MARKDOWN-REPAIR-AUTH-001`  
**Decision:** `AUTHORIZED`

## Human Authority decision

The Human explicitly selects Path B from:

`RLY-S22-IMPL-EVAL-002 — ESCALATE`

and authorizes a separate bounded repository-quality repair for the inherited Ruff Markdown formatting condition blocking exact-head CI on the current Slice 2.2 lineage.

This is **not** a Slice 2.2 implementation-scope expansion.

## Exact repair basis

```text
Repository:
cschrupp/relay

Current Slice 2.2 implementation branch:
implementation/2.2-role-contracts

Escalation record / repair authority baseline:
1252356a3bc65767ebe7b8d44ad6d1c24876a310

Technically ready Slice 2.2 rework candidate:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Independent implementation evaluation:
RLY-S22-IMPL-EVAL-002 — ESCALATE

Dedicated repair branch:
maintenance/ruff-markdown-format-boundary
```

The repair branch must start from the exact authority baseline above.

## Established defect

The declared quality command is:

```bash
uv run ruff format --check .
```

The current locked Ruff version is:

```text
ruff 0.16.8
```

That Ruff generation discovers and formats Python code blocks inside Markdown files.

The exact-head Slice 2.2 CI therefore reaches immutable governance records under Markdown formatting even though those records are historical authority and may not be edited in place.

The current failure is demonstrated by the unchanged immutable record:

```text
docs/reviews/SLICE_1_10_DOGFOOD_B4_REV2_IMPLEMENTATION_EVALUATION_001.md

Git blob at authorized Slice 2.2 implementation baseline:
2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8

Git blob at technically ready candidate:
2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8
```

The baseline itself had CI failures at the same repository-wide Ruff format step.

This is a repository quality-boundary defect, not a Role Contracts code defect.

## Governing policy

Documentation governance requires:

```text
Historical authority is immutable.
Current truth advances through explicit revision.
```

Immutable evaluation records must not be reformatted in place merely to satisfy a later formatter version.

Engineering quality policy also establishes the declared formatting check as part of the repository quality contract.

The repair must therefore reconcile both requirements without weakening the remaining quality gates.

## Authorized repair

Modify exactly:

`pyproject.toml`

to add a **formatter-only Markdown exclusion** equivalent to:

```toml
[tool.ruff.format]
exclude = ["*.md"]
```

Purpose:

- preserve the canonical quality command `uv run ruff format --check .`;
- keep Ruff formatting active for supported non-Markdown code;
- prevent Ruff from attempting to rewrite Markdown governance/history artifacts;
- avoid editing immutable historical records;
- leave Ruff lint, Pyright, pytest, build, dependencies, and CI workflow unchanged.

A mechanically equivalent formatter-only configuration is permitted only if it produces exactly the same boundary.

## Why all Markdown is excluded from Ruff formatting

The repository quality contract is a Python engineering-format contract.

Ruff's later Markdown code-block discovery expanded the effective scope of:

`ruff format --check .`

without an explicit Relay governance decision.

This repair restores the intended boundary rather than introducing per-record exceptions.

A path-specific exclusion for one immutable record is intentionally not preferred because the same governance conflict can recur for future immutable Markdown records.

Markdown content remains governed by documentation review and repository-contract semantics; it is simply not subject to Ruff's Python formatter.

## Authorized change surface

Expected MODIFY:

```text
pyproject.toml
```

Expected other changes:

```text
NONE
```

Do not modify:

- `uv.lock`;
- `.github/workflows/ci.yml`;
- any file under `docs/reviews/`;
- any immutable/locked historical artifact;
- Slice 2.2 production source;
- Slice 2.2 tests;
- dependencies;
- repository schema;
- registry;
- lifecycle/governance code;
- main/canonical branch.

If any additional file is required, STOP and report before changing it.

## Required preservation checks

The repair must prove:

1. the failing historical document remains byte-identical;
2. its Git blob remains:
   `2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8`;
3. no Markdown file is modified;
4. no dependency or lockfile changes;
5. no Slice 2.2 source/test changes;
6. no CI workflow changes.

## Required validation

Run:

```bash
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

The repository-wide Ruff format check must now pass without changing Markdown files.

GitHub Actions must run on the exact repair candidate SHA and complete successfully.

If any later quality step fails for a condition unrelated to the one authorized here, STOP and report rather than expanding repair scope.

## Candidate discipline

Produce one repair candidate only.

Do not self-accept.

Push only:

`maintenance/ruff-markdown-format-boundary`

Return:

```text
authority:
RLY-QUALITY-RUFF-MARKDOWN-REPAIR-AUTH-001

repair baseline:
1252356a3bc65767ebe7b8d44ad6d1c24876a310

branch:
maintenance/ruff-markdown-format-boundary

candidate SHA:
<exact>

changed files:
pyproject.toml only

exact config change:
<exact>

immutable B4 evaluation blob:
2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8 unchanged: YES/NO

Markdown files changed:
NONE / exact deviation

uv.lock changed:
NO / exact deviation

Slice 2.2 source/tests changed:
NO / exact deviation

ruff format:
PASS/FAIL

ruff lint:
PASS/FAIL

pyright:
PASS/FAIL

full pytest:
<count/result>

build:
PASS/FAIL

git diff --check:
PASS/FAIL

GitHub Actions:
<run id / exact SHA / status>

deviations:
NONE or exact list
```

## Authority boundary

This authority does not authorize:

- editing historical Markdown to satisfy Ruff;
- changing documentation content;
- dependency/tool version changes;
- CI workflow changes;
- disabling Ruff formatting for Python code;
- weakening Ruff lint;
- skipping Pyright/tests/build;
- Slice 2.2 code rework;
- Human technical acceptance of Slice 2.2;
- merge/promotion to `main`;
- Slice 2.3/2.4;
- Phase 3.

After an independently accepted repair candidate has green exact-head CI, the Slice 2.2 implementation lineage must return to independent implementation disposition under its own governance.

**Quality repair authority != Slice 2.2 technical acceptance.**
