# Relay — Slice 2.5 Implementation Rework Authorization 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Authority:** `RLY-S25-IMPL-REWORK-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human authorizes one cohesive bounded corrective implementation pass responding only to:

`RLY-S25-IMPL-EVAL-001 — REWORK / NARROW`

This authority is limited to findings **I001–I005**.

The corrective implementation must preserve candidate `4311912303cde089e165c9fa6bdd803d3b402918` behavior except where I001–I005 require correction.

G001 is a governance-lineage issue and is **not** corrective implementation scope. Its missing original authority record has been materialized separately as `RLY-S25-IMPL-AUTH-001`.

## Exact rework basis

```text
Repository:
cschrupp/relay

Accepted normative design:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Original implementation scope:
RLY-S25-CODEX-SCOPE-001

Original implementation authority:
RLY-S25-IMPL-AUTH-001 — AUTHORIZED

Original authorized implementation baseline:
6203a693efb12ae22858d54b6e2edd46e95a52f4

Reviewed implementation candidate:
4311912303cde089e165c9fa6bdd803d3b402918

Independent implementation evaluation:
RLY-S25-IMPL-EVAL-001 — REWORK / NARROW

Evaluation record commit:
1a758d6ab58179c276f3509b0105cc63b34f3dc2

Original implementation branch:
implementation/2.5-project-state-resolution-authority-compilation

Dedicated corrective branch:
implementation/2.5-project-state-resolution-authority-compilation-rework-001
```

The commit containing this authority record is the exact governance-consistent corrective checkout baseline.

The dedicated corrective branch must be created from that exact commit. That checkout therefore contains:

1. exact reviewed implementation content from `4311912303cde089e165c9fa6bdd803d3b402918`;
2. the materialized original implementation-authority lineage repair;
3. `RLY-S25-IMPL-EVAL-001`;
4. this corrective authority.

No rebase, merge, branch-head refresh, unrelated cherry-pick, or later canonical update is permitted before corrective implementation.

## Authorized mutable production files

Exactly:

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

If any corrective requirement appears to require another path, STOP and report the exact conflict.

## I001 — bind authority-bearing typed content to accepted backing value

Correct the provenance contract so an authority-bearing typed object cannot become resolved accepted state merely by carrying a valid provenance reference whose accepted predicate/value assertion describes different normative content.

For each authority-bearing typed value used by resolution, establish a deterministic exact content binding to the accepted backing predicate value used to authorize it.

The binding may use an explicit normative digest field, a canonical sub-payload digest, or another mechanically equivalent exact mechanism, provided:

```text
accepted backing assertion value_digest
    == exact digest of the normative typed value being established
```

where the design requires the typed value itself to be the authority-bearing fact.

At minimum protect the semantic classes used for:

- invariants;
- qualifications;
- requirement edges;
- negative decisions;
- responsibility claims;
- consumable facts;
- equivalent typed authority-bearing values.

A backing mismatch must fail closed as `INDETERMINATE` with deterministic provenance/reason evidence.

Do not weaken exact accepted-source requirements.

## I002 — qualification evidence and acceptance lineage

Correct qualification resolution so a qualification satisfies a required predicate only when its exact evidence and required acceptance lineage are established.

Required behavior:

```text
qualification historical PASS
    != sufficient by itself

evidence ref absent / digest mismatch / wrong exact subject
    -> INDETERMINATE unless known governed absence is explicitly modeled as blocker

required acceptance known absent
    -> BLOCKED

required acceptance unresolved
    -> INDETERMINATE

unrelated accepted Human/technical record
    -> cannot satisfy qualification acceptance
```

Every acceptance used for a qualification must explicitly bind to the exact qualification/evidence subject it accepts.

Historical PASS must remain preserved independently from current applicability and acceptance.

## I003 — repair SUPERSEDED semantics

Implement the accepted distinction:

```text
SUPERSEDED
    exact prior subject is no longer current
    exact prior subject cannot satisfy current predecessor/current-state use
    accepted successor is used where required
    not a blanket prohibition on different successors

REJECTED
    matching request BLOCKED absent exact reauthorization

PROHIBITED_UNLESS_REAUTHORIZED
    matching request BLOCKED absent exact Human reauthorization
```

Do not emit a generic prohibition solely because a historical subject is `SUPERSEDED`.

If the required successor/current-state relationship cannot be established exactly, return `INDETERMINATE`.

## I004 — eliminate unprovenanced ProducedExpectation ingress

A caller must not be able to inject arbitrary normative `ProducedExpectation` values into resolved state.

Preferred correction:

- derive produced expectations from provenance-verified accepted `PRODUCES` edges.

A mechanically equivalent design is allowed only if direct expectations themselves carry and verify exact accepted provenance/content binding.

No caller-supplied ungoverned normative output/evidence expectation may reach a `READY` candidate.

## I005 — complete frozen dogfood matrix

Implement deterministic resolver/compiler dogfood tests for the frozen accepted scenarios.

### WellPlot

Must cover:

1. missing environment qualification -> `BLOCKED`;
2. missing accepted smoke -> `BLOCKED`;
3. historical PASS for mismatched exact subject -> historical PASS retained, `NOT_APPLICABLE`, required live request `BLOCKED`;
4. unknown required runtime identity -> `INDETERMINATE`;
5. responsibility collision -> `BLOCKED`;
6. rejected/prohibited second semantic/fallback path -> `BLOCKED`;
7. consumed campaign namespace -> `BLOCKED`;
8. incomplete namespace ledger -> `INDETERMINATE`.

### Tension/FEM

Must cover:

- exact scientific level, attempt, namespace, oracle/fixture applicability;
- known consumed -> `BLOCKED`;
- different frozen oracle subject -> historical PASS retained + `NOT_APPLICABLE`;
- unknown ledger/subject -> `INDETERMINATE`.

### Seneca

Must cover:

- backend/GPU/runtime/environment qualification applicability;
- exact identity mismatch -> historical PASS retained + `NOT_APPLICABLE` and required new qualification blocked;
- unknown required identity -> `INDETERMINATE`.

### Relay self-dogfood

Must cover:

- exact accepted predecessor/design/implementation/Human-acceptance/closure chain;
- current source selection and inherited constraints;
- no chat-history reconstruction;
- `PROPOSED_WORK != authorized work`;
- no authorized successor preserves `BACKLOG_EXHAUSTED`;
- no invented successor.

Fixture factoring is allowed. Isolated applicability tests alone are insufficient.

## Preservation requirements

The corrective candidate must preserve all accepted Slice 2.5 design decisions and all sound behavior already present in candidate `4311912303cde089e165c9fa6bdd803d3b402918`, including:

- pure resolver/compiler architecture;
- no filesystem/Git/network discovery inside resolution;
- exact pinned source snapshot;
- canonical pointer selection distinct from claim authority;
- accepted/authorized backing requirements;
- historical result separate from current applicability;
- bounded relation set `REQUIRES/FORBIDS/CONSUMES/PRODUCES`;
- responsibility collision semantics;
- exact consumable state and intended attempt identity;
- Knowledge Delta proposal-only semantics;
- deterministic canonical ordering/digests;
- blocker precedence while retaining unknown trace;
- only `READY` carries an authority candidate;
- `READY != AUTHORIZED`;
- no Human authority side effect;
- no WorkPacket creation;
- no persistence/database mutation;
- no AgentRuntime/provider/model/runtime calls;
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

- start exactly from the dedicated corrective branch created at this authority-record commit;
- verify that the checkout contains exact reviewed implementation `4311912303cde089e165c9fa6bdd803d3b402918` beneath the governance-only commits;
- modify only the nine authorized implementation/test files;
- make changes only for I001–I005;
- internally plan, implement, validate, repair, and self-review without creating routine Human gates;
- create one cohesive corrective candidate;
- push only `implementation/2.5-project-state-resolution-authority-compilation-rework-001`;
- verify the remote branch exact SHA;
- report exact changed files and focused I001–I005 evidence;
- report complete validation and exact-head CI evidence;
- report zero AgentRuntime/provider/model/network/database/runtime calls;
- STOP FOR `RLY-S25-IMPL-EVAL-002`.

No self-evaluation or self-acceptance.

## Authority boundary

```text
RLY-S25-IMPL-REWORK-AUTH-001 — AUTHORIZED

Corrective implementation:
AUTHORIZED — I001 / I002 / I003 / I004 / I005 ONLY

Mutable surface:
EXACT NINE EXISTING SLICE 2.5 IMPLEMENTATION/TEST FILES ONLY

G001 governance-lineage repair:
SEPARATE / DOES NOT EXPAND IMPLEMENTATION SCOPE

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
