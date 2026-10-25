# Relay — Slice 2.5 Project State Resolution and Authority Compilation — Implementation Authorization

**Document class:** Immutable Human Authority record / governance-lineage repair  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Authority:** `RLY-S25-IMPL-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human authorized one cohesive bounded implementation of the Human-accepted Slice 2.5 design under the exact Codex scope and baseline below.

The Human decision existed before implementation candidate `4311912303cde089e165c9fa6bdd803d3b402918` was created. This record is being materialized after that candidate solely to repair the omitted durable repository record identified as governance finding G001.

This lineage repair does **not**:

- accept or approve candidate `4311912303cde089e165c9fa6bdd803d3b402918`;
- alter `RLY-S25-IMPL-EVAL-001 — REWORK / NARROW`;
- authorize corrective implementation;
- authorize Slice 2.5 acceptance or closure;
- authorize production wiring, Phase 3, or real-project execution.

## Exact authorization basis

```text
Repository:
cschrupp/relay

Slice 2.5:
OPEN

Corrective normative design:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Independent design evaluation:
RLY-S25-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED

Codex implementation scope:
RLY-S25-CODEX-SCOPE-001

Scope commit / original authorized implementation baseline:
6203a693efb12ae22858d54b6e2edd46e95a52f4

Implementation branch:
implementation/2.5-project-state-resolution-authority-compilation
```

The authorized implementation baseline was the exact scope commit above.

The omission was the durable authority record, not the Human decision itself.

## Authorized production files

Exactly:

```text
src/relay_engine/project_state/__init__.py
src/relay_engine/project_state/models.py
src/relay_engine/project_state/resolution.py
src/relay_engine/project_state/compilation.py
```

## Authorized test files

Exactly:

```text
tests/unit/test_project_state_models.py
tests/unit/test_project_state_resolution.py
tests/unit/test_authority_compilation.py
tests/unit/test_project_state_dogfood.py
tests/unit/test_project_state_architecture.py
```

No other implementation path was authorized.

## Required implementation contract

Implementation was required to conform to:

1. the exact Human-accepted Slice 2.5 normative design at `b2f566d3f8ed616e3e901795858b7046aa3fa6c6`;
2. `RLY-S25-DESIGN-EVAL-002 — ACCEPT`;
3. `RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED`;
4. `RLY-S25-CODEX-SCOPE-001`.

The package boundary is a pure deterministic project-state resolver and authority-candidate compiler. It does not grant authority, persist operational state, execute WorkPackets, invoke AgentRuntime, call providers/models, perform network discovery, mutate databases, or perform production orchestration.

## Mandatory invariants

The implementation must preserve:

```text
canonical pointer != claim authority
living summary != authority-bearing source
historical evidence result != current applicability
PASS != authority
READY != AUTHORIZED
derived project state != authoritative durable state
Knowledge Delta proposal != accepted project state
WorkPacket remains the authoritative external work unit
ProjectStateResolver != planner
AuthorityCompiler != planner or authority issuer
unknown required fact != optimistic readiness
```

Only exact accepted/immutable/locked owning records or explicitly authorized external facts may establish authority-bearing predicates.

Required missing/conflicting provenance yields `INDETERMINATE`.

Known applicable hard blockers yield `BLOCKED`.

Only complete exact state with no blockers or unknowns may yield `READY`, and `READY` contains no Human grant.

## Explicitly not authorized

This authority did not authorize:

- Human authority issuance or mutation;
- production authority-candidate persistence;
- operational project-state database/cache;
- graph database or generic workflow engine;
- production WorkPacket creation/wiring;
- workspace provisioning;
- AgentRuntime/OpenCode changes;
- provider/model/runtime calls;
- network access or credential use;
- live external-project execution;
- Phase 3 orchestration;
- real-project autonomous engineering;
- canonical/main promotion;
- self-evaluation or self-acceptance.

## Governance disposition

```text
RLY-S25-IMPL-AUTH-001 — AUTHORIZED

Original bounded implementation:
AUTHORIZED at exact baseline 6203a693efb12ae22858d54b6e2edd46e95a52f4

Durable-record omission:
REPAIRED BY THIS IMMUTABLE RECORD

Candidate 4311912303cde089e165c9fa6bdd803d3b402918:
NOT ACCEPTED — SUBJECT TO RLY-S25-IMPL-EVAL-001

Corrective implementation:
NOT AUTHORIZED BY THIS RECORD

Slice 2.5 acceptance / closure:
NOT AUTHORIZED

Production wiring:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

**This record repairs governance lineage; it does not rewrite implementation history or convert a reviewed candidate into an accepted candidate.**
