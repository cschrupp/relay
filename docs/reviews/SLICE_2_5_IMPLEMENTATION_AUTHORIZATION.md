# Relay — Slice 2.5 Project State Resolution and Authority Compilation — Implementation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Authority:** `RLY-S25-IMPL-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes one cohesive bounded implementation of the Human-accepted Slice 2.5 design under the exact implementation scope and baseline below.

This authority permits one coherent implementation candidate.

It does not authorize Phase 3, production authority issuance, production WorkPacket execution, runtime/provider/model execution, real-project autonomous engineering, or canonical/main promotion.

## Exact authorization basis

```text
Repository:
cschrupp/relay

Slice 2.5:
OPEN

Normative design:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Exact accepted design:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Independent design evaluation:
RLY-S25-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED

Implementation scope:
RLY-S25-CODEX-SCOPE-001

Scope commit / authorized implementation baseline:
6203a693efb12ae22858d54b6e2edd46e95a52f4

Scope blob:
2541473f06ced3378c72088af368ff08f1d652b7

Implementation branch:
implementation/2.5-project-state-resolution-authority-compilation
```

The implementation branch must start exactly from the scope commit above.

This implementation authority is an external governance fact. The implementation branch need not contain this authorization commit in its ancestry.

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

No other path is authorized.

## Required implementation contract

The implementation must conform to:

1. exact normative design subject `b2f566d3f8ed616e3e901795858b7046aa3fa6c6`;
2. `RLY-S25-DESIGN-EVAL-002 — ACCEPT`;
3. `RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED`;
4. `RLY-S25-CODEX-SCOPE-001`;
5. `RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`.

The implementation must preserve the accepted boundary:

```text
READY != AUTHORIZED
authority candidate != Human authority
evidence != authority
qualification PASS != authority
project-state projection != source of truth
Project State Resolver != planner
Authority Compiler != planner
requirement graph != workflow engine
WorkPacket remains the external governed work unit
```

## Cohesive WorkPacket rule

This authorization intentionally covers the entire bounded Slice 2.5 implementation as one external governed engineering unit.

The implementation agent may internally:

- plan;
- decompose;
- sequence;
- repair;
- validate intermediate milestones;
- self-review;
- iterate within the authorized nine-file surface.

Those internal milestones do not create new Human authority boundaries.

If implementation requires any path or responsibility outside the authorized scope, STOP and report the exact conflict as proposed/out-of-scope work rather than widening the implementation.

## Mandatory source/provenance behavior

The implementation must structurally preserve:

```text
canonical pointer
    -> current projection selection only

summary/planning projection
    -> navigation / selection / description
    != authority-bearing provenance

authority-bearing predicate
    -> exact owning accepted/immutable/locked record
       OR explicitly authorized external fact

missing backing provenance
    -> INDETERMINATE

contradictory summary vs backing record
    -> INDETERMINATE with contradiction retained
```

No summary projection may become hidden authority.

## Mandatory resolver behavior

The Project State Resolver must be pure, deterministic, exact-subject-bound, provenance-bearing, and fail-closed.

It must resolve only already-materialized exact inputs.

It must not:

- discover "latest";
- scan directories for state;
- infer authority from prose;
- invoke Git/network/runtime/provider/model;
- mutate persistence;
- grant authority;
- build/execute a WorkPacket;
- plan implementation work.

## Mandatory compiler behavior

The Authority Compiler must return exactly:

```text
READY
BLOCKED
INDETERMINATE
```

with deterministic precedence:

```text
known blocker -> BLOCKED
else unresolved required fact -> INDETERMINATE
else -> READY
```

A blocker and unknown may coexist in the trace; status remains `BLOCKED`.

Only `READY` may carry a complete authority candidate.

`READY` is not authorization.

## Mandatory accepted domains

The implementation must cover the accepted design semantics for:

- source coverage;
- exact provenance;
- inherited invariants/rationale;
- QualificationFact;
- applicability envelopes;
- `REQUIRES / FORBIDS / CONSUMES / PRODUCES`;
- `SUPERSEDED / REJECTED / PROHIBITED_UNLESS_REAUTHORIZED`;
- responsibility ownership/collision;
- consumable state;
- candidate freshness;
- Knowledge Delta proposal-only behavior;
- exact canonical identity/digests;
- operator/Human review projection data;
- no-chat-history deterministic reconstruction.

## Mandatory dogfood tests

Synthetic deterministic tests must cover:

- Wellplot environment -> smoke -> independent smoke acceptance -> live confirmation;
- stale smoke applicability;
- second smoke-harness responsibility collision;
- prohibited/rejected fallback/semantic-engine resurrection;
- campaign namespace consumption;
- Tension/FEM attempt/scientific-level/oracle applicability;
- Seneca backend/GPU/runtime/environment invalidation;
- Relay accepted predecessor/design/implementation/acceptance/closure chain;
- `PROPOSED_WORK != authorized work`;
- no authorized successor preserves `BACKLOG_EXHAUSTED`.

No external project calls are authorized.

## Forbidden implementation changes

Do not modify:

```text
src/relay_engine/domain/**
src/relay_engine/repository_contract/**
src/relay_engine/governance/**
src/relay_engine/role_contracts/**
src/relay_engine/work_packets/**
src/relay_engine/execution_workspace/**
src/relay_engine/agent_runtime/**
src/relay_engine/persistence/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/promotion/**
src/relay_engine/repository_sync/**
src/relay_engine/integrations/**
src/relay_engine/decision_support/**
src/relay_engine/board/**
src/relay_engine/adoption/**
pyproject.toml
uv.lock
.github/workflows/**
.relay/registry.json
docs/**
```

No dependency addition.

No schema/database migration.

No production wiring.

## Explicitly not authorized

This authority does not permit:

- automatic Human authority issuance;
- grant/reservation implementation;
- production authority-candidate persistence;
- operational project-state DB/cache;
- graph database;
- generic graph/rule/workflow/planner platform;
- production WorkPacket creation/wiring/execution;
- production workspace provisioning;
- AgentRuntime/OpenCode changes;
- runtime/provider/model calls;
- network access;
- credential use;
- live environment/scientific observations;
- external-project execution;
- Phase 3 opening/orchestration;
- real-project autonomous engineering;
- canonical/main promotion;
- self-evaluation or self-acceptance.

## Required validation

The executor must run:

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

Exact-head GitHub Actions must run on the pushed implementation candidate.

Tests and CI are evidence only.

## Candidate discipline

The implementation executor must:

- start from exact baseline `6203a693efb12ae22858d54b6e2edd46e95a52f4`;
- create/modify only the nine authorized paths;
- use branch `implementation/2.5-project-state-resolution-authority-compilation`;
- produce one coherent implementation candidate;
- verify remote exact candidate SHA;
- report changed paths and validation evidence;
- report zero network/provider/model/AgentRuntime/DB calls;
- STOP for SOL independent implementation review.

Do not self-evaluate or self-accept.

## Authority boundary

```text
RLY-S25-IMPL-AUTH-001 — AUTHORIZED

Slice 2.5:
OPEN

Normative design:
HUMAN ACCEPTED

Implementation:
AUTHORIZED — BOUNDED TO RLY-S25-CODEX-SCOPE-001

Production authority issuance:
NOT AUTHORIZED

Production WorkPacket execution:
NOT AUTHORIZED

AgentRuntime/provider/model execution:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

**Implementation authority != implementation acceptance. READY != authorized.**
