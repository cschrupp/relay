# Relay — Slice 2.4 Execution Workspace Authority — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority:** `RLY-S24-IMPL-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes bounded implementation of the Human-accepted Slice 2.4 Execution Workspace Authority design under the exact Codex scope and baseline below.

This authority permits one implementation candidate only.

## Exact authorization basis

```text
Repository:
cschrupp/relay

Slice 2.4:
OPEN

Combined design:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Independent design evaluation:
RLY-S24-DESIGN-EVAL-005 — ACCEPT
f4aaf4cd0590af7c7aeaddb9f01f15ede5dac46a

Human design acceptance:
RLY-S24-DESIGN-ACCEPT-001 — ACCEPTED
103e27bb48e775f42601dea45822c34896feb730

Codex implementation scope:
RLY-S24-CODEX-SCOPE-001

Scope commit / authorized implementation baseline:
0de6f21184aea9ff644dfb852f82ae04db370aaa

Scope blob:
e1625adbf898adef71dd3b3c2e9bfee2e383be1d

Implementation branch:
implementation/2.4-execution-workspace-authority
```

The implementation branch must start exactly at the scope commit above.

This implementation authority is an external governance fact. The implementation branch need not contain this authorization commit in its ancestry.

## Authorized production files

Exactly:

```text
src/relay_engine/execution_workspace/__init__.py
src/relay_engine/execution_workspace/models.py
src/relay_engine/execution_workspace/evaluation.py
src/relay_engine/execution_workspace/provider.py
src/relay_engine/execution_workspace/local_clone.py
```

## Authorized test files

Exactly:

```text
tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
```

No other path is authorized.

## Required implementation contract

Codex must implement the exact accepted combined Slice 2.4 design defined by:

1. `SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN.md`;
2. `SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV2_AMENDMENT.md`;
3. `SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV3_AMENDMENT.md`;
4. `SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV4_AMENDMENT.md`;
5. `SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV5_AMENDMENT.md`;
6. `RLY-S24-DESIGN-EVAL-005 — ACCEPT`;
7. `RLY-S24-DESIGN-ACCEPT-001 — ACCEPTED`;
8. `RLY-S24-CODEX-SCOPE-001`.

Later revisions are normative over earlier revisions only where they explicitly differ.

## Mandatory implementation invariants

The candidate must preserve:

```text
WorkspacePolicyDefinition != authority
WorkspacePlan != authority
WorkspacePlanResolution SATISFIED != execution authority
WorkspacePreflight SATISFIED != execution authority
WorkspaceProvider capability != control enforcement
WorkspaceInstanceRef != authority
WorkspacePropertyEvidence != authority
WorkspaceConformance SATISFIED != execution authority
RuntimeWorkspaceAttachment != execution authority
filesystem visibility != write authority
tool availability != permission
network reachability != external-mutation authority
credential availability != authority
protected semantic permission != physical mutation authority
successful provisioning != engineering acceptance
successful teardown != Human acceptance
```

Human root authority and current execution authority remain external.

## Mandatory F001–F012 closure

Codex must preserve all independently accepted closures.

In particular:

- exact-subject-bound facts/evidence;
- complete finite provider capability schema;
- non-ordinal protected VerificationAssetPermission semantics;
- exact WorkspaceChangeManifest / ref identity;
- no implicit workspace policy when WorkPacket.workspace_policy_ref is None;
- honest local same-user control-strength ceiling;
- no standalone ProtectedAssetEvidence;
- exact repository metadata / credential policy;
- no protected authority fact for `separate_authority_ref=None`;
- provider-injected files transported through exact WorkspacePlan;
- complete Tool/Shell/Network/ExternalSideEffect policy schemas;
- complete `WorkspacePlan.property_requirements` transport and no downstream policy lookup.

## Binding clarifications

### C01 WorkspacePlan stable identity

```text
plan_key:
StableRequirementKey

revision:
int >= 1

stable identity:
(work_packet_ref, plan_key, revision)

same stable identity + different content_digest:
identity conflict / fail closed

no latest/max revision resolution
```

### C02 provider property-capability uniqueness

```text
WorkspaceProviderDescriptor.property_capabilities

canonical order:
WorkspaceProperty enum declaration order

stable identity:
WorkspaceProperty

duplicate WorkspaceProperty:
invalid

same WorkspaceProperty + different maximum_strength:
invalid
```

## Local-clone provider boundary

The authorized concrete provider is only:

```text
LOCAL_CLONE
SAME_USER_NO_SECURITY_BOUNDARY
```

It is a development/dogfood evidence provider.

It may perform local disposable-repository mechanics only.

It must not claim strong generic filesystem, network, credential, resource, or protected-asset isolation unless an exact mechanism actually establishes such a control.

## Forbidden implementation changes

Do not modify:

```text
src/relay_engine/domain/**
src/relay_engine/governance/**
src/relay_engine/role_contracts/**
src/relay_engine/agent_runtime/**
src/relay_engine/work_packets/**
src/relay_engine/persistence/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/promotion/**
src/relay_engine/repository_sync/**
src/relay_engine/integrations/**
pyproject.toml
uv.lock
.github/workflows/**
.relay/registry.json
docs/**
```

No dependency addition.

No DB migration.

No production wiring.

## Explicitly not authorized

This authority does not permit:

- production workspace provisioning;
- real-project workspace creation;
- production WorkPacket wiring;
- operational DB/persistence;
- lifecycle mutation;
- Human authority creation/validation;
- secret retrieval;
- real credential exposure;
- network access;
- remote Git fetch/pull/push;
- Docker/Kubernetes/cloud provider implementation;
- remote isolated provider implementation;
- AgentRuntime/provider/model calls;
- prompt rendering/execution;
- protected-asset mutation outside disposable tests;
- Phase 3 orchestration;
- real-project agent execution;
- main/canonical promotion;
- self-evaluation or self-acceptance.

## Required validation

Codex must run:

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

Exact-head GitHub Actions must be allowed to run on the pushed implementation candidate.

Tests and CI are evidence only.

## Candidate discipline

Codex must:

- begin from exact baseline `0de6f21184aea9ff644dfb852f82ae04db370aaa`;
- create only the ten authorized files;
- create one coherent implementation candidate;
- push only `implementation/2.4-execution-workspace-authority`;
- verify remote candidate SHA;
- report exact changed files and validation evidence;
- report zero network/provider/model/AgentRuntime calls;
- report disposable local repositories only for integration tests;
- STOP for SOL independent implementation review.

If any accepted design requirement appears impossible inside the ten-file surface, STOP and report the exact conflict rather than widening scope.

## Authority boundary

```text
RLY-S24-IMPL-AUTH-001 — AUTHORIZED

Implementation:
AUTHORIZED — BOUNDED TO RLY-S24-CODEX-SCOPE-001

Production workspace provisioning:
NOT AUTHORIZED

Production WorkPacket wiring:
NOT AUTHORIZED

Operational DB/lifecycle mutation:
NOT AUTHORIZED

Network/credentials:
NOT AUTHORIZED

AgentRuntime/provider/model execution:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

**Implementation authority != engineering acceptance. Engineering acceptance != Human technical acceptance.**
