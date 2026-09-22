# Relay Slice 0.2 — Core Domain Model

**Slice:** 0.2  
**Phase:** 0 — Protocol and Deterministic Foundation  
**Status:** DESIGN ACCEPTED  
**Parent:** *Relay — Build Plan and Development Roadmap v0.1*  
**Depends on:** Slice 0.1 — Repository Foundation and Engineering Baseline  
**Design authorization:** ACCEPTED  
**Implementation authorization:** Not implied by this design review

---

## Objective

Define Relay's stable core engineering vocabulary independently of workflow transitions, persistence, GitHub integration, AI providers, agent execution, research execution, experiments, and UI.

The accepted core vocabulary is:

- ActorRef
- RepositoryRef
- CommitRef
- Project
- Baseline
- Slice
- ScopeSpec
- AcceptanceCriterion
- Artifact
- Decision
- Evidence

The following remain deliberately deferred until their own design slices:

- Authorization
- HandoverGate
- Evaluation
- HumanDecision
- AgentRole
- AgentAssignment
- Execution
- ResearchTask
- ResearchFinding
- Source
- Experiment

---

## Locked Decisions

### S0.2-D01 — Immutable domain objects

Core domain models are immutable after construction. Engineering changes produce new immutable snapshots rather than hidden mutation.

### S0.2-D02 — No untyped metadata escape hatches

Core entities do not expose generic `dict[str, Any]` metadata fields. New concepts receive explicit, versioned fields or models.

### S0.2-D03 — Schema version

Every serialized top-level domain entity carries `schema_version`, initially `1`.

### S0.2-D04 — Identifier strategy

Relay uses globally unique, type-readable identifiers such as:

```text
prj_<uuid>
repo_<uuid>
slc_<uuid>
base_<uuid>
art_<uuid>
dec_<uuid>
evd_<uuid>
act_<uuid>
```

UUIDv7 is the recommended generator. Model validation does not secretly create IDs.

### S0.2-D05 — Time semantics

Persisted timestamps are timezone-aware and canonically normalized to UTC. Domain constructors do not call the clock implicitly.

### S0.2-D06 — Serialization

Core interchange is JSON-compatible structured data. Unknown fields are rejected. JSON round-trip and JSON Schema generation are required.

---

## Domain Boundaries

The domain layer represents engineering meaning, not database tables, API request types, UI cards, GitHub responses, or LLM schemas.

It may depend on the Python standard library, Pydantic, and other domain primitives. It must not depend on persistence, providers, GitHub adapters, execution infrastructure, or UI.

---

## Core Models

### ActorRef

Minimal stable identity of a HUMAN, SYSTEM, or AGENT. It contains no permissions, organization membership, provider, model, or OAuth identity.

### RepositoryRef

Provider-neutral Git repository identity. Contains no credentials.

### CommitRef

Immutable repository commit identity. Branch names are not baselines; commit SHAs are authoritative.

### Project

Relay engineering project. Initial design supports one primary repository per project. Multi-repository semantics are deferred.

### Baseline

Immutable engineering snapshot containing:

```text
exact code commit
+
authoritative artifact references
+
authoritative decision references
```

Baseline shape is defined here; promotion/acceptance behavior is not.

### ScopeSpec

Ordered immutable in-scope and out-of-scope statements with local validation only.

### AcceptanceCriterion

First-class acceptance item with key, statement, and required flag.

### Slice

Bounded intended engineering change. It contains no workflow-state field in Slice 0.2. State semantics belong to Slice 0.3.

Local invariants include no self-parent, no self-dependency, no duplicate dependencies, and unique acceptance keys.

### Artifact

Durable engineering artifact with extensible artifact type, repository-relative safe path, immutable commit reference, and content digest.

### Decision

Durable engineering judgment. Initial document statuses are PROPOSED, LOCKED, and SUPERSEDED. Locked decisions are superseded rather than rewritten historically.

### Evidence

Durable claim-support record with provenance. Evidence does not itself imply evaluation or acceptance.

---

## Validation Philosophy

Local invariants belong in models.

Contextual invariants requiring repository, project graph, or accepted-state knowledge are deferred to later services.

No domain constructor performs I/O, database access, repository lookup, graph traversal, or hidden clock access.

---

## Required Documentation

Implementation should add:

```text
docs/architecture/CORE_DOMAIN_MODEL.md
docs/decisions/ADR-0002-core-domain-boundaries.md
docs/slices/SLICE_0_2_CORE_DOMAIN_MODEL_MEMORY.md
```

Representative v1 golden JSON fixtures should live under:

```text
tests/fixtures/domain/v1/
```

for Project, Baseline, Slice, Artifact, Decision, and Evidence.

---

## Acceptance Matrix

| ID | Requirement | Evidence | Required |
|---|---|---|---:|
| A01 | Core domain package exists | repository inspection | Yes |
| A02 | Models immutable | unit tests | Yes |
| A03 | Unknown fields rejected | unit tests | Yes |
| A04 | Top-level schema version present | unit tests | Yes |
| A05 | Prefixed IDs validated | unit tests | Yes |
| A06 | ID generation produces valid unique IDs | unit tests | Yes |
| A07 | Naive timestamps rejected | unit tests | Yes |
| A08 | Timestamp policy deterministic | unit tests | Yes |
| A09 | Repository references are provider-neutral | review | Yes |
| A10 | Commit refs validate canonical hashes | unit tests | Yes |
| A11 | Project validates | unit tests | Yes |
| A12 | Baseline includes exact commit | unit tests | Yes |
| A13 | Baseline includes authority references | unit tests | Yes |
| A14 | Slice has no workflow-state field | inspection | Yes |
| A15 | Self-dependencies rejected | unit tests | Yes |
| A16 | Duplicate dependencies rejected | unit tests | Yes |
| A17 | Scope validation works | unit tests | Yes |
| A18 | Acceptance keys unique | unit tests | Yes |
| A19 | Artifact paths cannot escape repository | unit tests | Yes |
| A20 | Artifact digest validated | unit tests | Yes |
| A21 | Decision supersession invariants work | unit tests | Yes |
| A22 | Evidence requires provenance | unit tests | Yes |
| A23 | JSON round-trip succeeds for all public models | unit tests | Yes |
| A24 | JSON Schema generation succeeds | unit tests | Yes |
| A25 | Golden v1 fixtures exist and load | unit tests | Yes |
| A26 | No untyped metadata escape hatch introduced | inspection | Yes |
| A27 | No persistence dependency introduced | dependency inspection | Yes |
| A28 | No GitHub/provider dependency introduced | dependency inspection | Yes |
| A29 | No future subsystem placeholders introduced | diff inspection | Yes |
| A30 | CORE_DOMAIN_MODEL.md completed | review | Yes |
| A31 | ADR-0002 completed | review | Yes |
| A32 | Slice memory completed | review | Yes |
| A33 | CURRENT_BASELINE updated | review | Yes |
| A34 | All Slice 0.1 quality gates remain green | CI | Yes |

---

## Resulting Authority

Once implemented and accepted, Relay will have authoritative definitions for Actor, Repository, Commit, Project, Baseline, Slice definition, Scope, Acceptance Criterion, Artifact, Decision, and Evidence.

It will still have no authoritative definition for workflow state, authorization, handover, traffic lights, evaluation, execution, research tasks, or experiments.

---

## Hard Stop

The next design slice is:

> **Slice 0.3 — State Machine and Lifecycle Semantics**

Slice 0.3 must determine which concepts are lifecycle phases and which are orthogonal dimensions, especially AUTHORIZED, BLOCKED, STALE, and HARD STOP.
