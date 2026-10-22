# Relay — Slice 2.3 Context / Work-Packet Contract — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Authority:** `RLY-S23-IMPL-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes bounded implementation of the Human-accepted Slice 2.3 Context / Work-Packet Contract design under the exact Codex scope and baseline below.

This authority permits one implementation candidate only.

## Exact authorization basis

```text
Repository:
cschrupp/relay

Slice 2.3:
OPEN

Combined design:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Independent design evaluation:
RLY-S23-DESIGN-EVAL-002 — ACCEPT
af163408b33d3b8fe3fe340aaa36b2be94c76c94

Human design acceptance:
RLY-S23-DESIGN-ACCEPT-001 — ACCEPTED
852da5033a51adfc1a9dde9383ffecdd81ac552c

Codex implementation scope:
RLY-S23-CODEX-SCOPE-001

Scope commit / authorized implementation baseline:
f0996a1909bff8dda76a455d6d88d027b4b736f2

Scope blob:
509a5e730c18e11960365801c3bd6b65b2d4fd22

Implementation branch:
implementation/2.3-context-work-packet-contract
```

The implementation branch must start exactly at the scope commit above.

This implementation authority is an external governance fact. The implementation branch need not contain this authorization commit in its ancestry.

## Authorized production files

Exactly:

```text
src/relay_engine/work_packets/__init__.py
src/relay_engine/work_packets/models.py
src/relay_engine/work_packets/evaluation.py
```

## Authorized test files

Exactly:

```text
tests/unit/test_work_packet_models.py
tests/unit/test_work_packet_evaluation.py
tests/unit/test_work_packet_architecture.py
```

No other path is authorized.

## Required implementation contract

Codex must implement the exact accepted Slice 2.3 contract defined by:

1. `SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN.md`;
2. `SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN_REV2_AMENDMENT.md`;
3. `RLY-S23-DESIGN-EVAL-002 — ACCEPT`;
4. `RLY-S23-DESIGN-ACCEPT-001 — ACCEPTED`;
5. `RLY-S23-CODEX-SCOPE-001`.

Revision 2 is normative over Revision 1 where they differ.

## Mandatory implementation invariants

The candidate must preserve:

```text
WorkPacket != authority
ContextManifest != authority
NormalizedEngineeringIntent != authority
AuthorityBasisRef != authority issuance
AuthorityBasisFact != authority issuance
WorkPacketConformance SATISFIED != AUTHORIZED
RoleApplicabilityEvaluation APPLICABLE != work authority
RuntimeCapability != authority
CredentialRef availability != authority
WorkspacePolicyRef != enforcement
materialization success != authority
ControlMirrorBinding != authority
accepted-design fact != Human acceptance
authorized_successor_ref != execution authority
```

Human root authority remains external.

## Mandatory F001 closure

All external conformance evidence must be exact-subject-bound.

Codex must not replace the accepted exact-ref fact models with unbound aggregate statuses.

Packet A facts must not satisfy Packet B.

## Mandatory F002 closure

Canonicality is recursive.

Every normative collection reachable from WorkPacket / ContextManifest must be:

- normatively ordered; or
- canonical non-semantic with explicit deterministic order.

Noncanonical input must be rejected, not silently sorted.

Same stable identity / sort key + conflicting content must be rejected.

Literal canonical JSON / SHA-256 fixtures are mandatory.

## Mandatory F003 closure

Every required context entry must carry an exact ContextMaterialRef.

No digest-only required context.

Materialization evidence is externally supplied only.

The package must not implement:

- storage;
- resolver registry;
- retrieval;
- network access;
- filesystem materialization;
- provider/tool calls.

Unavailable exact material/provenance is INDETERMINATE.

Observed mismatch is UNSATISFIED.

## Mandatory accepted-type reuse

Reuse exact public accepted Relay values, especially:

- domain Project/Slice/Baseline/Artifact/Repository/Commit/ContentDigest identities;
- Slice 2.2 `RoleApplicabilityEvaluation`, `RoleContractRef`, `RequirementStatus`, `RoleOutputRequirement`, `VerificationAssetPermission`;
- Slice 2.1 runtime declaration models/enums.

Do not duplicate those contracts.

## Forbidden implementation changes

Do not modify:

```text
src/relay_engine/domain/**
src/relay_engine/governance/**
src/relay_engine/role_contracts/**
src/relay_engine/agent_runtime/**
src/relay_engine/persistence/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/repository_sync/**
pyproject.toml
uv.lock
.github/workflows/**
.relay/registry.json
docs/**
```

The only documentation governance fact on the design branch is this authority; Codex must not modify documentation during implementation.

## Explicitly not authorized

This authority does not permit:

- production WorkPacket/ContextManifest wiring into existing Relay callers;
- WorkPacket/ContextManifest persistence;
- database schema/migration;
- operational DB mutation;
- lifecycle mutation;
- Human authority creation/validation;
- real authority issuance;
- context/material storage;
- resolver registry/implementation;
- RAG/vector search;
- external planning-provider adapters;
- network/tool/provider/model calls;
- AgentRuntime invocation;
- prompt rendering/execution;
- workspace creation/enforcement;
- protected asset mutation;
- Slice 2.4 work;
- Phase 3 work;
- real-project agent execution;
- main/canonical promotion;
- self-evaluation or self-acceptance.

## Required validation

Codex must run:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_work_packet_models.py
uv run pytest tests/unit/test_work_packet_evaluation.py
uv run pytest tests/unit/test_work_packet_architecture.py

uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Exact-head GitHub Actions must be allowed to run on the pushed candidate.

Tests/CI are evidence only.

## Candidate discipline

Codex must:

- begin from exact baseline `f0996a1909bff8dda76a455d6d88d027b4b736f2`;
- create only the six authorized files;
- create one coherent implementation commit/candidate;
- push only `implementation/2.3-context-work-packet-contract`;
- verify remote candidate SHA;
- report complete evidence using `RLY-S23-CODEX-SCOPE-001`;
- STOP for SOL independent implementation review.

If any accepted design requirement appears impossible inside the six-file surface, STOP and report the exact conflict rather than widening scope.

## Authority boundary

```text
RLY-S23-IMPL-AUTH-001 — AUTHORIZED

Implementation:
AUTHORIZED — BOUNDED TO RLY-S23-CODEX-SCOPE-001

Production wiring:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Context storage / material resolver:
NOT AUTHORIZED

Runtime/provider/model execution:
NOT AUTHORIZED

Workspace enforcement:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

**Implementation authority != engineering acceptance. Engineering acceptance != Human technical acceptance.**
