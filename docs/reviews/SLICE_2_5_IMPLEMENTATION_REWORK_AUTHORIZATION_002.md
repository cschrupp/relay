# Relay — Slice 2.5 Implementation Rework Authorization 002

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Authority:** `RLY-S25-IMPL-REWORK-AUTH-002 — AUTHORIZED`

## Human Authority decision

The Human authorizes one cohesive bounded corrective implementation pass responding only to:

`RLY-S25-IMPL-EVAL-002 — REWORK / NARROW`

This authority is limited to the two residual findings:

- **R2-I001** — exact independent-evaluation qualification acceptance;
- **R2-I002** — SUPERSEDED qualification-successor lookup.

No other Slice 2.5 implementation change is authorized.

## Exact rework basis

```text
Repository:
cschrupp/relay

Accepted normative design:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Original implementation authority:
RLY-S25-IMPL-AUTH-001 — AUTHORIZED

Prior corrective authority:
RLY-S25-IMPL-REWORK-AUTH-001 — AUTHORIZED

Reviewed corrective candidate / exact implementation subject:
18a4a6c4d8553c165d4a6888e09c87478be3474c

Independent implementation evaluation:
RLY-S25-IMPL-EVAL-002 — REWORK / NARROW

Evaluation record commit:
8e16d85065a25afc7a627bd5bd908b3dca418bed

Source corrective branch:
implementation/2.5-project-state-resolution-authority-compilation-rework-001

Dedicated corrective branch:
implementation/2.5-project-state-resolution-authority-compilation-rework-002
```

The exact implementation base for this rework is candidate `18a4a6c4d8553c165d4a6888e09c87478be3474c`.

The commit containing this authority record is the governance-consistent corrective checkout baseline. It contains that exact implementation subject plus only the immutable evaluation/authority records needed to establish the new gate.

The dedicated corrective branch must start exactly from the authority-record commit. No rebase, merge, branch-head refresh, unrelated cherry-pick, or later canonical update is permitted before corrective implementation.

## Authorized mutable production files

The existing Slice 2.5 nine-file ceiling remains in force, but this authority should require mutation only where necessary for the two residual findings.

Authorized production files remain exactly:

```text
src/relay_engine/project_state/__init__.py
src/relay_engine/project_state/models.py
src/relay_engine/project_state/resolution.py
src/relay_engine/project_state/compilation.py
```

## Authorized mutable test files

Exactly:

```text
tests/unit/test_project_state_models.py
tests/unit/test_project_state_resolution.py
tests/unit/test_authority_compilation.py
tests/unit/test_project_state_dogfood.py
tests/unit/test_project_state_architecture.py
```

No other production, test, documentation, configuration, dependency, registry, CI, database, lifecycle, runtime, WorkPacket, RoleContract, governance, or Phase 3 file may be modified by the corrective implementation.

If either residual correction appears to require another path or design change, STOP and report the exact conflict.

## R2-I001 — independent-evaluation qualification acceptance

Correct qualification acceptance verification so an exact accepted independent evaluation can satisfy a qualification when the governing acceptance contract permits that acceptance class.

Required behavior:

```text
exact pinned independent evaluation
+ exact scope
+ accepted/current source
+ exact accepts-<qualification> assertion
+ assertion value digest == exact qualification normative digest
    -> may satisfy required qualification acceptance

unrelated independent evaluation
wrong qualification subject
wrong digest
wrong scope
unpinned / mismatched identity
unaccepted source
    -> must not satisfy acceptance
```

Do not weaken existing Human/technical acceptance verification.

Do not treat arbitrary independent-evaluation presence as acceptance.

Add deterministic tests that exercise the exact accepted independent-evaluation path and rejection of unrelated independent evaluation.

## R2-I002 — SUPERSEDED qualification successor lookup

Correct REQUIRES resolution when the old target is SUPERSEDED by an exact qualification successor.

The resolver must use the computed successor/current predecessor key when locating the resolved qualification.

Required behavior:

```text
old qualification
SUPERSEDED BY new qualification

new qualification exact + applicable + accepted + PASS
    -> predecessor requirement SATISFIED

new qualification exact + applicable + known FAIL/unaccepted
    -> predecessor requirement UNSATISFIED / BLOCKED

successor missing, conflicting, unverifiable, or applicability unresolved
    -> predecessor requirement INDETERMINATE

SUPERSEDED alone
    -> never generic PROHIBITED_SUBJECT
```

No planner, fallback, or successor invention is authorized.

Add deterministic regression coverage for satisfied, known-unsatisfied, and unresolved qualification successors.

## Preservation requirements

The corrective candidate must preserve all behavior already accepted from candidate `18a4a6c4d8553c165d4a6888e09c87478be3474c`, including:

- I001 typed normative content binding;
- I002 exact qualification evidence/acceptance subject binding;
- I003 non-prohibitive SUPERSEDED semantics;
- I004 derived-only `ProducedExpectation`;
- the expanded WellPlot/Tension/Seneca/Relay dogfood matrix;
- deterministic canonical ordering and digests;
- exact snapshot/source verification;
- blocker-versus-indeterminate semantics;
- responsibility collision behavior;
- consumable state and exact intended-attempt behavior;
- Knowledge Delta proposal-only behavior;
- only `READY` may carry an authority candidate;
- `READY != AUTHORIZED`;
- no persistence/database/lifecycle mutation;
- no WorkPacket creation;
- no AgentRuntime/provider/model/network/runtime execution;
- no production orchestration.

No broad redesign.

## Required validation

Run at minimum:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_project_state_models.py
uv run pytest tests/unit/test_project_state_resolution.py
uv run pytest tests/unit/test_authority_compilation.py
uv run pytest tests/unit/test_project_state_dogfood.py
uv run pytest tests/unit/test_project_state_architecture.py

uv run ruff format --check .
uv run ruff check .
uv run pyright

uv run pytest tests/unit/test_repository_contract.py
uv run pytest

uv build
git diff --check
```

Exact-head GitHub Actions must pass.

Tests and CI are evidence only.

## Candidate discipline

The Implementer must:

- begin exactly from the dedicated corrective branch established by this authority record;
- verify that candidate `18a4a6c4d8553c165d4a6888e09c87478be3474c` is the exact implementation subject beneath the governance-only commits;
- change only what is required for R2-I001 and R2-I002;
- remain within the existing nine-file ceiling;
- internally plan, implement, validate, repair, and self-review without introducing routine Human gates;
- create one cohesive corrective candidate;
- push only `implementation/2.5-project-state-resolution-authority-compilation-rework-002`;
- verify exact remote candidate SHA;
- report focused evidence for both residual findings;
- report complete validation and exact-head CI;
- report zero AgentRuntime/provider/model/network/database/runtime calls;
- STOP FOR `RLY-S25-IMPL-EVAL-003`.

No self-evaluation or self-acceptance.

## Authority boundary

```text
RLY-S25-IMPL-REWORK-AUTH-002 — AUTHORIZED

Corrective implementation:
AUTHORIZED — R2-I001 + R2-I002 ONLY

Implementation subject:
18a4a6c4d8553c165d4a6888e09c87478be3474c

Mutable ceiling:
EXISTING NINE SLICE 2.5 IMPLEMENTATION/TEST FILES ONLY

Human technical acceptance:
NOT AUTHORIZED BY THIS RECORD

Slice 2.5 closure:
NOT AUTHORIZED

Production authority/work wiring:
NOT AUTHORIZED

Operational DB/lifecycle:
NOT AUTHORIZED

AgentRuntime/provider/model/runtime execution:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

**Bounded corrective authority != implementation acceptance.**
