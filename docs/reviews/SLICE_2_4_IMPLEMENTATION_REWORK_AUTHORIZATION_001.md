# Relay — Slice 2.4 Implementation Rework Authorization 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-23  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority:** `RLY-S24-IMPL-REWORK-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human authorizes one bounded corrective implementation pass responding only to:

`RLY-S24-IMPL-EVAL-001 — REWORK`

This authority is limited to findings I001–I003.

The corrective implementation must preserve the rejected candidate's already-passing behavior except where I001–I003 require correction.

## Exact rework basis

```text
Repository:
cschrupp/relay

Original implementation authority:
RLY-S24-IMPL-AUTH-001 — AUTHORIZED

Original authorized implementation baseline:
0de6f21184aea9ff644dfb852f82ae04db370aaa

Rejected / reviewed implementation candidate:
8bb3534ac0803e56e411105233c294eaa1c4586a

Independent implementation evaluation:
RLY-S24-IMPL-EVAL-001 — REWORK

Evaluation record commit:
41d819e96b619dcb10a16cd2815a105ead418827

Original implementation branch:
implementation/2.4-execution-workspace-authority

Dedicated corrective branch:
implementation/2.4-execution-workspace-authority-rework-001
```

The dedicated corrective checkout must contain the exact reviewed implementation content from `8bb3534ac0803e56e411105233c294eaa1c4586a` together with the current Slice 2.4 governance records and living baseline. Materializing that checkout is governance/lineage preparation, not corrective implementation.

## Authorized mutable files

Exactly:

```text
src/relay_engine/execution_workspace/evaluation.py
src/relay_engine/execution_workspace/local_clone.py

tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
```

No other production, test, documentation, configuration, dependency, registry, CI, database, lifecycle, runtime, WorkPacket, RoleContract, governance, or Phase 3 file may be modified by the corrective implementation.

If a correction appears to require any other file, STOP and report the exact reason.

## I001 — unsupported filesystem / Git node kinds silently omitted

Correct the bounded local provider so unsupported tracked Git entry kinds and unsupported non-directory worktree node kinds fail closed rather than disappearing from exact state/change accounting.

Required behavior includes:

```text
gitlink / submodule tracked entry
    -> normalized provider inspection/change-extraction failure

unsupported non-directory worktree node kind
    -> normalized provider inspection/change-extraction failure
```

Do not add another `WorkspaceEntryKind`.

Do not widen schema v1.

Add deterministic disposable-repository regression coverage.

## I002 — protected physical access may widen ordinary filesystem policy

Correct plan resolution so protected physical access can only narrow ordinary filesystem access.

Required behavior includes:

```text
MODIFY + ordinary READ_ONLY
    -> UNSATISFIED

MODIFY + ordinary DENY
    -> UNSATISFIED

CREATE + ordinary DENY
    -> UNSATISFIED

protected READ over ordinary READ_WRITE
    -> allowed only as narrowing; no manufactured write authority
```

For MODIFY/CREATE, effective ordinary access must be `READ_WRITE`.

For read/evaluate/execute requirements, require the applicable minimum read access without manufacturing write access.

No RoleContract, WorkPacket, WorkspacePolicyDefinition, or schema change is authorized.

## I003 — frozen minimum deterministic test matrix incomplete

Complete the frozen negative/canonicality test families required by the accepted Slice 2.4 design and `RLY-S24-CODEX-SCOPE-001`.

At minimum prove the accepted semantics for:

- filesystem/path negative cases;
- protected-asset compatibility and mutation cases;
- tool/shell/network/external-effect cases;
- credential cases;
- resource cases;
- exact-subject mismatch families;
- unsupported-node fail-closed behavior;
- non-authority semantics.

Equivalent assertions need not be duplicated mechanically, but each frozen semantic family must have deterministic evidence.

## Preservation requirements

The corrective candidate must preserve:

- all accepted Slice 2.4 design decisions and Revisions 1–5;
- F001–F012 design closures;
- C01 WorkspacePlan stable identity;
- C02 provider property-capability uniqueness;
- exact canonical JSON / SHA-256 vectors;
- WorkspacePlan self-containment;
- provider capability versus evidence separation;
- local-provider `SAME_USER_NO_SECURITY_BOUNDARY` ceiling;
- independent Git object storage;
- exact provider-injected-material semantics;
- `SATISFIED != AUTHORIZED`;
- no persistence/orchestration leakage;
- no production workspace provisioning;
- no production WorkPacket wiring;
- no AgentRuntime invocation;
- no runtime/provider/model call;
- no Phase 3 work;
- no real-project agent execution;
- no canonical/main promotion.

## Validation

Run at minimum:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_execution_workspace_models.py
uv run pytest tests/unit/test_execution_workspace_evaluation.py
uv run pytest tests/unit/test_execution_workspace_provider_contract.py
uv run pytest tests/integration/test_local_clone_workspace_provider.py
uv run pytest tests/unit/test_execution_workspace_architecture.py

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

- start from the dedicated governance-consistent corrective checkout;
- verify that its checkout contains the exact reviewed implementation state before corrective mutation;
- modify only the seven authorized files;
- internally plan, implement, validate, repair, and self-review without stopping at routine internal milestones;
- create one coherent corrective candidate;
- push only `implementation/2.4-execution-workspace-authority-rework-001`;
- verify the remote branch exact SHA;
- report focused I001/I002/I003 evidence plus the complete validation chain;
- report zero network/provider/model/AgentRuntime calls;
- STOP FOR SOL INDEPENDENT IMPLEMENTATION RE-REVIEW.

No self-acceptance.

The authorized-work granularity policy applies: internal execution steps are not separate Human gates.

## Authority boundary

```text
RLY-S24-IMPL-REWORK-AUTH-001 — AUTHORIZED

Corrective implementation:
AUTHORIZED — I001 / I002 / I003 ONLY

Human technical acceptance:
NOT AUTHORIZED BY THIS RECORD

Slice 2.4 closure:
NOT AUTHORIZED

Production workspace provisioning:
NOT AUTHORIZED

Production WorkPacket wiring:
NOT AUTHORIZED

Operational DB / lifecycle:
NOT AUTHORIZED

AgentRuntime / provider / model execution:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

**Bounded rework authority != acceptance.**
