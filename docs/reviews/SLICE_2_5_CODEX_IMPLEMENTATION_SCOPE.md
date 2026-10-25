# Relay — Slice 2.5 Project State Resolution and Authority Compilation — Codex Implementation Scope

**Document class:** Prepared implementation handoff / scope  
**Status:** IMPLEMENTATION SCOPE — HUMAN DESIGN ACCEPTED / IMPLEMENTATION AUTHORIZATION PENDING RECORD  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Record:** `RLY-S25-CODEX-SCOPE-001`

## 1. Governance status

```text
Slice opening:
RLY-S25-OPEN-001 — OPEN

Design authorization:
RLY-S25-DESIGN-AUTH-001 — AUTHORIZED

Corrective normative design:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Independent design evaluation:
RLY-S25-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED

Current accepted-design governance tip before this scope:
a0a5d272c5af63ada46eb0a3e063b2b18ce7196e
```

The exact accepted normative design is:

`docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_DESIGN.md`

at exact accepted subject:

`b2f566d3f8ed616e3e901795858b7046aa3fa6c6`

If this scope conflicts with that accepted design or `RLY-S25-DESIGN-EVAL-002`, STOP and report the conflict. Do not reinterpret the design.

## 2. Executor and objective

Planned executor:

```text
Codex / Luna implementation environment
```

Objective:

Implement the minimum deterministic Slice 2.5 contract package that:

1. models exact project-state inputs and provenance;
2. evaluates current evidence applicability without rewriting historical evidence;
3. resolves invariants, requirements, prohibitions, responsibility ownership, qualifications, and consumables from an exact supplied snapshot;
4. compiles exactly one of `READY / BLOCKED / INDETERMINATE`;
5. emits a complete exact authority candidate only for `READY`;
6. preserves `READY != AUTHORIZED`;
7. supplies/gates the existing WorkPacket path without creating or executing a WorkPacket;
8. contains no persistence, network, runtime, provider, model, workspace, or Human-authority side effects.

This is a **pure project-state resolution and authority-candidate compilation library** plus deterministic tests.

It is not production orchestration.

## 3. Implementation branch and exact baseline

Planned implementation branch:

`implementation/2.5-project-state-resolution-authority-compilation`

The separate implementation-authorization record must pin the exact commit containing this scope as the authorized implementation baseline.

The implementation branch must begin exactly from that scope commit.

After authorization:

- verify local/remote implementation branch HEAD equals the exact authorized baseline before edits;
- do not merge/rebase later `main` or design-branch work;
- do not rewrite accepted design history;
- do not cherry-pick unrelated work;
- do not widen the file surface.

## 4. Exact authorized implementation surface

Expected NEW production files only:

```text
src/relay_engine/project_state/__init__.py
src/relay_engine/project_state/models.py
src/relay_engine/project_state/resolution.py
src/relay_engine/project_state/compilation.py
```

Expected NEW tests only:

```text
tests/unit/test_project_state_models.py
tests/unit/test_project_state_resolution.py
tests/unit/test_authority_compilation.py
tests/unit/test_project_state_dogfood.py
tests/unit/test_project_state_architecture.py
```

Expected existing production files modified:

```text
NONE
```

Expected dependency / lock / schema changes:

```text
NONE
```

If implementation requires any other path, STOP before editing it.

## 5. Existing Relay contracts to reuse unchanged

Use accepted Relay primitives rather than introducing competitors.

### Domain / repository identity

Reuse exact existing types where applicable, including:

```text
ArtifactId / stable artifact identity primitives
CommitRef
ContentDigest
RepositoryRef
DomainModel
```

Use the repository-contract package only as a source of already-materialized exact registry/canonical facts if its accepted public models support that use.

Do not modify repository-contract behavior.

### Slice 2.2

Reuse accepted actor/action eligibility and status primitives where applicable:

```text
RequirementStatus
RoleContractRef
```

Do not modify RoleContract semantics.

### Slice 2.3

Reuse accepted exact references/constraints where applicable:

```text
WorkPacketRef
SourceBaselineRef
ContextManifestRef
AuthorityBasisRef
GovernanceProfileRef
WorkspacePolicyRef
StableRequirementKey
```

The Slice 2.5 authority candidate may carry exact references and requirements for later WorkPacket construction.

It must not instantiate a competing external work unit.

### Slice 2.4

Reuse exact workspace/provider/qualification references where applicable.

Do not modify WorkspacePolicy, WorkspacePlan, provider, or conformance semantics.

### Human Authority

Human authority/grant remains external.

Do not call or modify `human_control`.

The implementation may model an exact candidate digest/reference for Human review but may not grant, validate, reserve, or execute authority.

## 6. models.py responsibility

`models.py` owns strict immutable Slice 2.5 schema-v1 values, enums, exact subject bindings, canonical ordering validation, and canonical/digest helpers.

Implement mechanically equivalent strict concepts for the accepted design, including at minimum:

```text
SourceRole
SourceDisposition
SourceCoverageDeclaration
SourceCoverageItem
ResolutionSnapshot
SourceRecordRef
BackingProvenanceRef

InvariantDisposition
Invariant
QualificationResult
QualificationFact
ApplicabilityResult
ApplicabilityEnvelope
ApplicabilityEvaluation

RequirementRelationKind
RequirementEdge

NegativeDisposition
NegativeDecision

ResponsibilityClaim
ResponsibilityCollisionResult
ResponsibilityEvaluation

ConsumableState
ConsumableRef
ConsumableFact
ConsumptionRequirement

ProducedExpectation

KnowledgeDeltaKind
KnowledgeDeltaProposal

ResolutionStatus
ResolutionReason
ResolvedRequirement
ResolvedProjectState

CompilationStatus
AuthorityCandidate
AuthorityCompilation
```

Exact Python names may vary only where typing or collision avoidance requires a mechanically equivalent representation.

All models must be:

```text
frozen
strict
extra-forbid
validate-defaults
side-effect free
```

No model may contain secret bytes, live handles, mutable callbacks, DB sessions, runtime clients, or authority-grant operations.

## 7. Canonical identity rules

Provide pure canonical JSON / SHA-256 helpers for exact Slice 2.5 content-addressed values.

At minimum freeze canonical identities for:

```text
SourceCoverageDeclaration
ResolutionSnapshot
Invariant
QualificationFact
RequirementEdge
NegativeDecision
ResponsibilityClaim
ConsumableFact
KnowledgeDeltaProposal
ResolvedProjectState
AuthorityCandidate
AuthorityCompilation
```

Canonical JSON must follow the accepted Relay style:

```text
UTF-8
sort_keys=True
separators=(",", ":")
ensure_ascii=False
allow_nan=False
no normative floats
arrays in their frozen stable-key order
duplicate/conflicting stable identities rejected
digest field excluded from its own digest input
```

Do not silently sort invalid input where the design requires canonical order to be supplied/validated.

Tests must include fixed canonical JSON and SHA-256 vectors.

## 8. Canonical source / provenance contract

The implementation must encode the accepted distinction:

```text
canonical pointer
    -> selects current registered projection
    != authority for every claim inside it
```

A living summary/planning projection may provide navigation/selection/descriptive state but cannot by itself establish an authority-bearing predicate.

A living canonical policy may establish normative rules only within the exact ownership/scope/authority of its accepted policy contract.

Authority-bearing predicates require:

```text
exact accepted / immutable / locked owning record
OR
explicitly authorized external fact whose accepted contract permits it
```

Required missing backing provenance:

`INDETERMINATE`

Summary claim contradicting exact backing record:

`INDETERMINATE` with contradiction provenance retained.

No path-based, text-search, newest-revision, branch-head, wildcard, directory-scan, or "latest" discovery is permitted inside the resolver.

All source collections are already materialized exact inputs.

## 9. SourceCoverageDeclaration

Implement an exact accepted source-coverage input that identifies:

- stable requested-outcome/scope identity;
- required canonical keys;
- required exact immutable/locked record refs;
- admissible source roles;
- acceptance/disposition conditions;
- explicit closure rules for predecessor/evidence/qualification/prohibition/responsibility relationships;
- completeness assertions for declared source collections.

The implementation evaluates supplied declarations; it does not create or accept declarations.

Missing, ambiguous, incomplete, conflicting, or unsupported required source coverage:

`INDETERMINATE`

## 10. Applicability

Implement pure deterministic applicability evaluation.

Historical evidence/result is immutable.

Current applicability is one of:

```text
APPLICABLE
NOT_APPLICABLE
INDETERMINATE
```

Applicability compares only explicitly declared required dimensions.

Required dimension known mismatch:

`NOT_APPLICABLE`

Required dimension unknown/unverifiable:

`INDETERMINATE`

Non-required dimension change:

does not invalidate.

Relevant dimensions must support exact references for the accepted use cases, including where applicable:

- executable/content identity;
- runtime build;
- provider/endpoint;
- environment;
- workspace/provider identity;
- model identity;
- fixture/data/custody identity;
- accepted predecessor revision.

The applicability evaluator must not contact an external environment.

## 11. Requirement relations

Implement only:

```text
REQUIRES
FORBIDS
CONSUMES
PRODUCES
```

Unknown relation kind:

`INDETERMINATE`

The relation model must remain bounded to authority-resolution semantics.

Do not implement:

- a generic graph traversal framework;
- task scheduling;
- workflow execution;
- dependency execution;
- callbacks;
- retries;
- queue semantics;
- planner decomposition.

## 12. Invariants and negative decisions

An invariant/constraint must preserve exact:

- stable identity;
- normative rule;
- scope/applicability;
- source authority/provenance;
- rationale;
- protects-against rationale;
- disposition;
- typed relation links where required.

Implement exact negative-decision semantics for:

```text
SUPERSEDED
REJECTED
PROHIBITED_UNLESS_REAUTHORIZED
```

A matching active `REJECTED` or `PROHIBITED_UNLESS_REAUTHORIZED` subject without exact reauthorization is a known blocker.

`SUPERSEDED` is not automatically a universal prohibition; apply its accepted scope/successor semantics exactly.

Ordinary implementation cannot self-reauthorize.

## 13. Responsibility claims

Implement deterministic responsibility evaluation.

Required outcomes must be mechanically equivalent to:

```text
NO_COLLISION
COLLISION_REQUIRES_ARCHITECTURE_AUTHORITY
INDETERMINATE
```

`NO_COLLISION` requires:

- a complete accepted responsibility-key set for the declared scope;
- complete accepted owner set;
- exact scope comparison.

Absence of a text match is not proof of no collision.

Distinct accepted owner collision:

known blocker pending separate architecture authority.

Unknown/incomplete ownership:

`INDETERMINATE`.

No component creation occurs.

## 14. Consumables

Implement exact evidence-bearing consumable state:

```text
AVAILABLE
RESERVED
CONSUMED
INDETERMINATE
```

Compilation may inspect supplied consumable state only.

It must not reserve, consume, release, or mutate a consumable.

Known already-consumed required target:

`BLOCKED`.

Incomplete/unknown ledger:

`INDETERMINATE`.

Candidate content carries intended exact attempt/consumption identity where required.

Atomic reservation/consumption is a future integration requirement at the Human-grant/execution boundary and is not authorized by this implementation.

## 15. resolution.py — Project State Resolver

Implement one pure deterministic resolver over exact already-materialized inputs.

Conceptually:

```python
resolve_project_state(
    request,
    resolution_snapshot,
    source_coverage,
    source_records,
    invariants,
    qualification_facts,
    requirement_edges,
    negative_decisions,
    responsibility_claims,
    consumable_facts,
    knowledge_delta_proposals=(),
) -> ResolvedProjectState
```

Exact signature may differ, but semantics may not.

Required sequence:

1. verify exact snapshot/source-coverage identity and canonical completeness;
2. verify source roles/dispositions/acceptance conditions;
3. verify backing provenance for every authority-bearing predicate used;
4. resolve exact predecessor/source closure;
5. evaluate invariant applicability;
6. evaluate qualification applicability/result/required acceptance;
7. evaluate typed requirement edges;
8. resolve negative decisions and reauthorization;
9. resolve responsibility ownership/collision;
10. resolve consumable state;
11. include Knowledge Delta only as non-authoritative proposal evidence;
12. produce deterministic ordered reasons/provenance and exact resolved-state digest.

The resolver must not:

- grant authority;
- construct WorkPackets;
- invoke Human control;
- inspect Git/network/runtime directly;
- read the filesystem for discovery;
- mutate persistence;
- execute tasks;
- choose "latest";
- infer facts from chat/prose.

## 16. compilation.py — Authority Compiler

Implement pure deterministic compilation from normalized request + exact `ResolvedProjectState` + applicable accepted RoleContract/work references.

Return exactly one status:

```text
READY
BLOCKED
INDETERMINATE
```

Aggregation:

```text
known hard blocker
    -> BLOCKED

otherwise any unresolved required fact
    -> INDETERMINATE

otherwise
    -> READY
```

If blocker and unknown coexist:

- status is `BLOCKED`;
- both blocker and unknown remain in the trace.

Only `READY` may include a complete `AuthorityCandidate`.

`BLOCKED` and `INDETERMINATE` must not expose a candidate eligible for authorization.

## 17. AuthorityCandidate content

A `READY` candidate must carry exact normalized content sufficient for Human review:

- requested outcome / normalized intent identity;
- exact source baseline / resolution snapshot;
- accepted predecessor/design/implementation/closure refs as applicable;
- inherited invariants and provenance;
- all required predecessor/evidence results;
- prohibition/negative-decision results;
- qualification facts + applicability envelopes;
- consumable requirements and exact current state evidence;
- intended attempt identity where required;
- produced expectations/evidence requirements;
- responsibility ownership/collision results;
- RoleContract applicability references;
- exact requirements/constraints/hard stops that must gate or populate the existing WorkPacket/ContextManifest path;
- explicit out-of-scope actions;
- exact candidate content digest.

It contains no:

- Human grant;
- execution lease;
- mutable latest reference;
- runtime handle;
- WorkPacket object claiming authorization.

Any normative content change changes candidate digest.

## 18. Candidate freshness

A candidate is bound to one exact resolution snapshot.

The implementation must expose a pure exact comparison/freshness check sufficient to establish that changed relevant source identity invalidates ordinary current-state use.

At minimum a candidate becomes not-current when a relevant exact input changes, including:

- canonical pointer set/digest;
- required accepted source closure;
- applicable observation/qualification;
- applicability result;
- negative decision;
- responsibility owner;
- consumable state.

Do not silently "refresh" or mutate candidate content.

Historical snapshot use requires separate Human authority outside this package.

## 19. WorkPacket integration boundary

The implementation may produce exact data that later gates or populates existing Slice 2.3 fields.

It must not:

- instantiate a second WorkPacket format;
- create a competing task/work identity;
- issue a Human authority;
- persist an authority candidate as accepted truth;
- construct/execute a production WorkPacket;
- add a sidecar authority format;
- modify `work_packets/**`.

If a required accepted constraint cannot be represented through existing WorkPacket/ContextManifest contracts, compilation must return `BLOCKED` or `INDETERMINATE` with an exact reason.

No silent omission.

## 20. Knowledge Delta

Implement Knowledge Delta only as immutable proposal data.

A Knowledge Delta may propose:

- invariant;
- prerequisite;
- applicability rule;
- prohibition;
- responsibility claim;
- qualification requirement;
- consumption rule.

It must carry exact evidence/provenance and affected scope.

It must not enter active resolved constraints unless an exact accepted source record supplied to a later resolution establishes it.

No self-promotion.

## 21. Operator projection

The compilation/result models must expose enough deterministic data for a later UI/projection to display:

- request identity;
- snapshot identity/digest;
- status;
- predecessors;
- qualifications/applicability;
- invariants/rationale;
- prohibitions/reauthorization;
- responsibility owners/collisions;
- consumables;
- evidence lineage;
- blockers/unknowns/hard stops;
- exact candidate digest if READY.

Do not implement a web UI in Slice 2.5.

## 22. Required dogfood tests

`tests/unit/test_project_state_dogfood.py` must encode synthetic exact fixtures representing the accepted failure classes without calling external projects.

### Wellplot

Test:

```text
accepted predecessor
-> environment qualification
-> smoke result
-> independent smoke acceptance
-> live confirmation candidate
```

Required assertions:

1. known missing environment qualification -> `BLOCKED`;
2. known missing accepted smoke -> `BLOCKED`;
3. smoke PASS for different executable/runtime/provider/endpoint/environment/fixture/predecessor -> historical PASS retained + `NOT_APPLICABLE` + required live request `BLOCKED`;
4. required runtime identity unknown -> `INDETERMINATE`;
5. second smoke-harness responsibility collision -> `BLOCKED`;
6. rejected/prohibited second semantic engine/fallback -> `BLOCKED` absent exact reauthorization;
7. consumed campaign namespace -> `BLOCKED`;
8. incomplete namespace ledger -> `INDETERMINATE`.

### Tension/FEM

Test exact scientific-level/attempt/namespace consumption and exact oracle/fixture applicability.

Known consumed -> `BLOCKED`.

Different frozen oracle subject -> historical PASS + `NOT_APPLICABLE`.

Unknown ledger/subject -> `INDETERMINATE`.

### Seneca

Test backend/GPU/runtime/environment qualification applicability.

Required identity mismatch -> old PASS retained + `NOT_APPLICABLE` + required new qualification blocks.

Unknown required identity -> `INDETERMINATE`.

### Relay self-dogfood

Test exact accepted predecessor/design/implementation/Human acceptance/closure chain, current source selection, inherited constraints, and no-chat-history reconstruction.

Test that:

```text
PROPOSED_WORK != authorized work
no authorized successor -> BACKLOG_EXHAUSTED semantics preserved
```

The resolver/compiler must not invent a successor.

## 23. Required model/resolution tests

At minimum cover:

- fixed canonical JSON/SHA-256 vectors;
- stable ordering and duplicate/conflict rejection;
- canonical pointer selection != claim authority;
- living summary without backing provenance -> `INDETERMINATE`;
- summary contradicting backing record -> `INDETERMINATE`;
- living policy outside accepted ownership scope cannot establish predicate;
- accepted exact backing record establishes only its owned predicate;
- source-coverage missing/incomplete/ambiguous -> `INDETERMINATE`;
- historical PASS + exact applicability mismatch -> `NOT_APPLICABLE`;
- required unknown applicability -> `INDETERMINATE`;
- `REQUIRES`, `FORBIDS`, `CONSUMES`, `PRODUCES`;
- unknown relation -> `INDETERMINATE`;
- negative disposition semantics;
- responsibility complete/no-collision, collision, incomplete;
- consumable AVAILABLE/RESERVED/CONSUMED/INDETERMINATE;
- Knowledge Delta cannot constrain active resolution without accepted source;
- known blocker + unknown -> `BLOCKED` while retaining both traces;
- no blocker + unknown -> `INDETERMINATE`;
- complete exact facts -> `READY`;
- only READY contains eligible candidate;
- candidate digest changes with normative content;
- candidate freshness fails on relevant snapshot/input change;
- candidate contains no authority/grant state.

## 24. Architecture tests

`tests/unit/test_project_state_architecture.py` must prove the package does not import or call:

- persistence/database mutation;
- lifecycle mutation;
- Human control;
- manual evaluation mutation;
- promotion mutation;
- AgentRuntime/adapters;
- ExecutionWorkspace provider invocation;
- network/http clients;
- Git subprocess/discovery;
- filesystem discovery;
- model/provider clients;
- scheduler/queue/workflow framework.

It may import existing immutable domain/reference/model types needed for exact interoperability.

No dependency addition.

## 25. Exact forbidden implementation changes

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

No DB migration.

No dependency addition.

No production wiring.

If a required accepted design behavior appears impossible inside the nine-file surface, STOP and report the exact conflict rather than widening scope.

## 26. Required validation

Codex must run:

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

## 27. Candidate discipline

After implementation authorization, Codex must:

- start exactly from the authorized implementation baseline;
- modify/create only the nine authorized implementation/test paths;
- create one coherent implementation candidate;
- use branch `implementation/2.5-project-state-resolution-authority-compilation`;
- internally plan/decompose/repair within this single WorkPacket under `RLY-GOV-AUTHWORK-GRANULARITY-001`;
- not request new Human authority for ordinary internal milestones;
- stop only for a genuine out-of-scope/authority/contract/environment blocker or terminal candidate;
- push the exact candidate;
- verify remote candidate SHA;
- report exact changed paths and validation evidence;
- report zero provider/model/AgentRuntime/network/DB calls;
- STOP for SOL independent implementation review.

Do not self-evaluate or self-accept.

## 28. Explicitly out of implementation scope

Not authorized:

- automatic Human authority issuance;
- Human grant/reservation implementation;
- production authority-candidate persistence;
- operational project-state DB/cache;
- schema migration;
- graph database;
- generic rule/graph/workflow engine;
- production WorkPacket creation/wiring;
- production workspace provisioning;
- AgentRuntime/OpenCode changes;
- runtime/provider/model calls;
- network access;
- credential use;
- live environment/scientific observations;
- external-project execution;
- Phase 3 orchestration;
- real-project autonomous engineering;
- canonical/main promotion.

## 29. Governance disposition

```text
RLY-S25-CODEX-SCOPE-001 — PREPARED

Slice 2.5:
OPEN

Normative design:
RLY-S25-DESIGN-EVAL-002 — ACCEPT
RLY-S25-DESIGN-ACCEPT-001 — ACCEPTED

Implementation scope:
PREPARED / EXACT / COHESIVE

Implementation authority:
PENDING IMMUTABLE AUTHORITY RECORD

Planned branch:
implementation/2.5-project-state-resolution-authority-compilation

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

**One WorkPacket may contain many internal implementation milestones. Internal decomposition does not create new authority boundaries.**
