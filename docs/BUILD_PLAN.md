# Relay — Build Plan and Development Roadmap

**Version:** 0.3  
**Status:** Current living implementation plan  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.2  
**Parent document:** *Relay — Product and Technical Proposal v0.3*  
**Date:** September 2026

---

# 1. Purpose

This document defines how Relay should be built from an empty repository into a dogfoodable and subsequently production-capable system.

The Product and Technical Proposal defines:

> what Relay is and why it should exist.

This document defines:

> how Relay will be constructed without violating the engineering principles Relay itself is intended to enforce.

Relay development should therefore use the same methodology Relay will ultimately provide to its users.

Development will proceed through:

- explicit baselines;
- bounded slices;
- locked design decisions;
- implementation contracts;
- acceptance matrices;
- independent evaluation;
- development memory;
- controlled experiments;
- hard stops between major capability phases.

The objective is not to reach maximum autonomy as quickly as possible.

The objective is to build the smallest trustworthy substrate required for each subsequent capability.

---

# 2. Development Philosophy

Relay should be built **inside-out**.

The order is:

```text
domain contracts
      ↓
state machine
      ↓
governance
      ↓
persistence
      ↓
repository integration
      ↓
human workflow
      ↓
single-agent workflow
      ↓
evaluation/rework
      ↓
research/experiments
      ↓
parallel agents
      ↓
productization
```

Relay should not begin with:

```text
UI
+
multiple agents
+
cloud sandboxes
+
complex orchestration
```

and attempt to discover governance later.

The governance model is the product.

---

# 3. Engineering Principles for Building Relay

## 3.1 Every implementation slice starts from an exact baseline

Each slice records:

```text
repository
branch
baseline SHA
```

No slice begins from an ambiguous concept such as:

> latest main.

## 3.2 Design lock, implementation completion, and acceptance are separate

Relay itself should adopt the state distinction already proven useful in complex projects:

```text
DESIGN LOCKED
      ≠
IMPLEMENTATION COMPLETE
      ≠
ACCEPTED
```

A slice may therefore have:

```text
Design:          LOCKED
Implementation: COMPLETE
Evaluation:     REWORK REQUIRED
Overall:        NOT ACCEPTED
```

## 3.3 Every significant slice produces development memory

The minimum record should contain:

```text
baseline
resulting SHA
objective
dependencies
locked decisions
implementation
tests
evaluation
known limitations
deferred work
next authorization boundary
```

## 3.4 Experimental code does not become production automatically

Relay development may use sidecar experiments extensively.

However:

```text
experiment success
      ≠
production acceptance
```

The normal path is:

```text
experiment
   ↓
evidence
   ↓
decision
   ↓
production contract
   ↓
implementation
```

## 3.5 Hard stops are intentional

Major phases should terminate in explicit hard stops.

The next phase begins only after the current capability has been evaluated against its intended purpose.

---

# 4. Proposed Repository Structure

Initial repository structure:

```text
relay/
├── README.md
├── LICENSE
├── pyproject.toml
│
├── src/
│   └── relay/
│       ├── domain/
│       ├── governance/
│       ├── persistence/
│       ├── git/
│       ├── providers/
│       ├── agents/
│       ├── execution/
│       ├── research/
│       ├── experiments/
│       ├── api/
│       └── cli/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── fixtures/
│
├── docs/
│   ├── PRODUCT_PROPOSAL.md
│   ├── BUILD_PLAN.md
│   ├── CURRENT_BASELINE.md
│   ├── architecture/
│   ├── decisions/
│   └── slices/
│
└── .relay/
    └── ...
```

Exact implementation language and framework remain subject to Slice 0.1 design lock.

The architectural boundary is more important than the initial language choice.

---

# 4A. Documentation and Artifact Governance

Relay documentation follows the policy defined in:

```text
DOCUMENTATION_GOVERNANCE.md
```

Three primary classes are recognized:

```text
working artifact
locked record
living projection
```

Key build-plan consequences:

1. Accepted slice memories and other accepted engineering records lock and are never edited in place.
2. Product Proposal, Build Plan, Current Baseline, and Current Architecture are living projections and may be continuously updated.
3. Canonical status is explicit and must not be inferred from path or modification time.
4. The future `.relay/` contract must provide a canonical registry mapping stable logical keys to current artifact revisions.
5. Future UI and agent-context systems must consume that same registry.
6. Git commit and content digest provide provenance; a separate Relay revision and optional human-facing document version provide semantic presentation.
7. If an accepted design record needs clarification, create an amendment or superseding record rather than rewriting history.

---

# 4B. Engineering Simplicity, Scope, and Quality Governance

Relay development follows:

```text
ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md
```

The build-plan implications are:

1. Each substantive implementation slice should declare an expected change surface when the concept becomes operational.
2. Change surface is a visibility and authorization mechanism, not a universal LOC/file-count limit.
3. Implementation agents receive explicit non-authority as well as in-scope/out-of-scope boundaries.
4. New architecture must be justified by current accepted requirements.
5. Clarity is evaluated independently from code compactness.
6. Projects select their own formatter, linter, type checker, test runner, build command, schema-validation tools, and custom checks.
7. Existing repository tooling takes precedence unless a tooling migration is separately authorized.
8. Passing deterministic checks produces evidence but does not imply acceptance.
9. The existing Evaluator owns simplicity/clarity review initially; Relay does not add a dedicated minimization agent.
10. Unnecessary complexity routes through ordinary `REWORK`.

---

# 5. Development Memory Convention

Every significant Relay slice receives:

```text
docs/slices/
    SLICE_<phase>_<slice>_<name>_MEMORY.md
```

Example:

```text
docs/slices/
SLICE_0_3_STATE_MACHINE_MEMORY.md
```

Each memory should use the following structure:

```text
# Slice X.Y — Title

Status

Baseline
Result SHA

Depends on

Objective

Locked decisions

Architecture

In scope

Out of scope

Implementation

Acceptance evidence

Evaluation findings

Known limitations

Deferred work

Hard stop / next authorization
```

---

# 6. Major Milestones

Relay development is divided into five principal capability milestones.

## M0 — Relay governs work

Humans can use Relay to represent and govern engineering work without autonomous coding.

## M1 — Relay governs one coding agent

Relay can authorize an implementation, execute it, independently evaluate it, send it through rework, and accept a new baseline.

## M2 — Relay supports engineering intelligence

Research and sidecar experiments can inform decisions through controlled evidence paths.

## M3 — Relay governs multiple agents

Parallel work, dependency DAGs, independent workspaces, staleness, and integration become first-class.

## M4 — Relay becomes a deployable collaborative product

Identity, organizations, permissions, billing, integrations, observability, and production hardening are added.

---

# 7. Phase 0 — Protocol and Deterministic Foundation

Phase 0 builds the part of Relay that must remain trustworthy even if every AI provider disappears.

No agent execution is required.

The core question is:

> Can Relay represent engineering work and deterministically determine what transitions are valid?

---

# Slice 0.1 — Repository and Engineering Foundation

## Objective

Create the Relay repository, development conventions, quality tooling, packaging, and documentation baseline.

## In scope

- repository structure;
- package skeleton;
- test harness;
- formatting/linting;
- type checking where appropriate;
- structured logging foundation;
- configuration loading foundation;
- documentation structure;
- development-memory template;
- baseline document.

## Out of scope

- Relay domain model;
- state machine;
- GitHub integration;
- model APIs;
- cloud execution;
- UI.

## Locked design questions

Slice 0.1 should explicitly resolve:

- implementation language;
- package/build tooling;
- schema/validation framework;
- test framework;
- migration strategy for persisted schemas;
- logging conventions;
- configuration hierarchy.

## Exit bar

```text
[ ] repository installs from clean checkout
[ ] test command works
[ ] lint command works
[ ] formatter works
[ ] type checks configured if adopted
[ ] package imports successfully
[ ] docs structure exists
[ ] development-memory template exists
[ ] CURRENT_BASELINE.md exists
[ ] CI executes baseline quality checks
```

## Hard stop

No substantive Relay domain model should be implemented until the project foundation is accepted.

---

# Slice 0.2 — Core Domain Model

## Objective

Define Relay's fundamental objects independently of persistence, UI, GitHub, or AI providers.

## Required objects

At minimum:

```text
Project
RepositoryRef
Slice
Artifact
Decision
Evidence
Baseline
Authorization
HandoverGate
Evaluation
HumanDecision
AgentRole
AgentAssignment
Execution
ResearchTask
ResearchFinding
Source
Experiment
```

## Important distinction

Domain objects should describe **engineering meaning**, not database tables.

Persistence follows the domain model, not the reverse.

## Required semantics

Every object should have:

- stable ID;
- timestamps where meaningful;
- versioning strategy;
- ownership/project relationship;
- serialization contract;
- validation rules.

## In scope

- typed domain models;
- enums;
- identifiers;
- validation;
- serialization;
- domain invariants local to individual objects.

## Out of scope

- transition logic;
- database;
- Git;
- external providers;
- agent behavior.

## Exit bar

```text
[ ] all initial domain objects represented
[ ] round-trip serialization tests
[ ] invalid construction rejected
[ ] IDs deterministic or explicitly generated according to contract
[ ] schema version represented
[ ] objects contain no provider-specific assumptions
[ ] objects contain no GitHub-specific assumptions except generic repository references
```

---

# Slice 0.3 — State Machine

## Objective

Implement the authoritative Relay work-state model.

## Candidate states

Initial candidate vocabulary:

```text
PROPOSED
DEFINING
RESEARCHING
DESIGNING
CONTRACTING
PLANNING
READY
AUTHORIZED
IMPLEMENTING
EVALUATING
REWORK
BLOCKED
ACCEPTED
STALE
HARD_STOP
SUPERSEDED
CANCELLED
```

One design question must be resolved explicitly:

> Which concepts are true states and which are orthogonal properties?

In particular:

```text
AUTHORIZED
HARD_STOP
BLOCKED
STALE
```

may not all belong in one flat state enum.

The design should prefer correct semantics over a visually convenient board model.

## Requirements

The state engine must:

- enumerate legal transitions;
- reject illegal transitions;
- record transition reason;
- record actor;
- preserve prior state;
- produce immutable transition events;
- support human and system actors;
- not require an LLM.

## Exit bar

```text
[ ] legal transitions enumerated
[ ] illegal transitions rejected
[ ] READY and authorization semantics distinct
[ ] hard-stop semantics explicit
[ ] blocking semantics explicit
[ ] staleness semantics explicit
[ ] every transition emits immutable event
[ ] deterministic unit tests cover full transition matrix
[ ] state engine has zero model-provider dependencies
```

---

# Slice 0.4 — Handover Gates and Traffic Lights

## Objective

Formalize agent/human handovers.

## Gate inputs

A Handover Gate should be able to evaluate:

```text
required source state
required artifacts
required evidence
dependency state
evaluation result
authorization
human policy
risk policy
hard-stop policy
declared quality-check status when applicable
change-surface deviation when applicable
unauthorized toolchain-change finding when applicable
```

## Traffic-light outputs

```text
GREEN
YELLOW
RED
```

Semantics:

```text
GREEN
transition valid and may execute automatically

YELLOW
transition valid but human action required

RED
transition currently invalid
```

## Handover policies

```text
AUTO
AUTO_NOTIFY
HUMAN_APPROVAL
HUMAN_CHOICE
```

## In scope

- deterministic gate evaluation;
- reason codes;
- multiple possible outbound gates;
- human-action requirement representation.

## Out of scope

- actual agents;
- notifications;
- UI;
- model-based semantic evaluation.

## Exit bar

```text
[ ] each gate produces light + reasons
[ ] same inputs always produce same light
[ ] RED cannot transition
[ ] YELLOW cannot auto-transition
[ ] GREEN may transition when policy permits
[ ] multiple outgoing gates supported
[ ] hard stop always dominates automatic policy
[ ] missing/failed required quality evidence can block a configured handover
[ ] material change-surface deviation can require review according to policy
[ ] unauthorized toolchain change cannot silently pass a gate
[ ] tests cover conflicting prerequisite conditions
```

---

# Slice 0.5 — Event and Persistence Model

## Objective

Persist Relay's project state without losing historical causality.

## Principle

Relay should maintain:

```text
current materialized state
+
immutable event history
```

The exact implementation need not be full event sourcing, but historical transitions must remain reconstructable.

## Persisted categories

At minimum:

```text
projects
slices
artifacts
decisions
gates
authorizations
evaluations
executions
human decisions
events
```

## Requirements

- transactions around state transitions;
- optimistic concurrency or equivalent conflict protection;
- schema migrations;
- deterministic IDs where appropriate;
- historical auditability.

## Exit bar

```text
[ ] project survives process restart
[ ] state and events remain consistent
[ ] concurrent invalid transitions rejected
[ ] schema migration mechanism exists
[ ] event history reconstructs transition chronology
[ ] no credentials stored in engineering-state tables
```

---

# Slice 0.6 — `.relay/` Repository Contract

## Objective

Define the version-controlled durable engineering representation and the repository-side contract for canonical document discovery.

## Required decisions

Establish which information is:

```text
repository-authoritative
Relay-cloud-authoritative
derived/synchronized
```

and formalize:

```text
working artifacts
locked records
living projections
canonical pointers
artifact revisions
supersession chains
```

## Canonical registry

Slice 0.6 must define a machine-readable canonical registry mapping stable logical keys to the exact artifact revision that humans and agents should consult.

Conceptually:

```text
product-proposal       → current artifact revision
build-plan             → current artifact revision
documentation-governance → current artifact revision
current-baseline       → current artifact revision
current-architecture   → current artifact revision
```

Canonicality must not be inferred from folder position, file name, Git recency, or modification time.

## Artifact presentation metadata

The repository contract must support, directly or through an artifact registry:

```text
canonical_key
artifact_id
artifact_class
artifact_state
revision
human_version
source_commit
content_digest
supersedes
superseded_by
scope
```

The exact representation is intentionally deferred to this slice.

## Initial proposed `.relay/`

```text
.relay/
├── relay.yaml
├── project/
│   ├── definition.md
│   ├── architecture.md
│   ├── constraints.md
│   └── current-baseline.md
├── decisions/
├── research/
├── experiments/
├── slices/
├── agents/
└── <canonical/artifact registry representation to be designed>
```

The physical tree is not itself authority.

## Key invariants

Cloud database runtime state and repository development memory must not become competing sources of truth.

Additionally:

> **Historical authority is immutable. Current truth is represented through living projections and explicit canonical pointers.**

Locked artifacts must remain addressable by exact revision, commit, and content digest after supersession.

## Exit bar

```text
[ ] canonical paths and/or registry location locked
[ ] machine-readable vs human-readable files distinguished
[ ] schema versions represented
[ ] artifact class semantics represented
[ ] DRAFT/REVIEW/LOCKED/SUPERSEDED semantics represented where applicable
[ ] living projections represented without pretending they are immutable records
[ ] canonical logical keys resolve deterministically
[ ] at most one project-current canonical revision exists per canonical key
[ ] source commit captured
[ ] content digest captured outside self-referential document content
[ ] supersession chain represented
[ ] invalid repository state detectable
[ ] broken canonical reference detectable
[ ] synchronization ownership documented
[ ] no secrets permitted in .relay/
[ ] examples validate against schema
[ ] same canonical registry can serve future UI and agent context
```

---

# Phase 0 Hard Stop

At the end of Phase 0:

```text
HARD STOP — PROTOCOL REVIEW
```

Required review questions:

1. Can all important Relay workflows be represented without an AI model?
2. Are authorization and readiness distinct?
3. Are traffic lights deterministic?
4. Can project history be reconstructed?
5. Is `.relay/` authoritative where expected?
6. Do any domain objects prematurely assume one provider or UI?
7. Can the future board be derived from the model without becoming authoritative itself?

No GitHub write integration proceeds until this review is accepted.

---

# 8. Milestone M0 — Relay Can Govern Humans

M0 is achieved after Phase 1.

This is deliberately before autonomous coding.

A user should be able to manage a real project using Relay's governance model manually.

---

# 9. Phase 1 — GitHub and Human-Controlled Project Workflow

## Slice 1.1 — GitHub App Integration

### Objective

Connect Relay securely to selected GitHub repositories.

### In scope

- GitHub App installation;
- installation/repository identity;
- read repository metadata;
- selected content access;
- permission inspection;
- secure credential handling.

### Security principles

- least privilege;
- no personal access tokens as primary architecture;
- credentials never written to repository;
- tenant isolation.

### Out of scope

- agent execution;
- autonomous branch creation;
- merging;
- PR reviews.

### Exit bar

```text
[ ] install flow works
[ ] repository selection works
[ ] installation identity persisted
[ ] revoked installation detected
[ ] permissions inspected
[ ] secrets encrypted outside repository
[ ] unauthorized repository access rejected
```

## Slice 1.2 — Repository Registration and Baseline Resolution

### Objective

Represent an attached Git repository as a Relay project repository and resolve immutable baselines.

### Requirements

Relay should resolve:

```text
repository
branch/ref
commit SHA
```

The SHA becomes authoritative for executions.

### Exit bar

```text
[ ] branch resolves to SHA
[ ] tag resolves to SHA
[ ] explicit SHA accepted
[ ] unknown ref rejected
[ ] main advancing does not mutate existing authorization baseline
[ ] baseline stored with originating ref for display only
```

## Slice 1.3 — `.relay/` Initialization and Sync

### Objective

Initialize a Relay repository and synchronize durable project artifacts.

### Typical flow

```text
connect repository
      ↓
inspect .relay/
      ↓
initialize if absent
      ↓
validate
      ↓
register project state
```

### Important policy

Initialization should be explicit and reviewable.

Relay must not unexpectedly scatter administrative files throughout a repository.

### Exit bar

```text
[ ] clean repo can be initialized
[ ] existing valid .relay recognized
[ ] incompatible schema detected
[ ] malformed .relay fails visibly
[ ] generated files deterministic where practical
[ ] initialization commit isolated and auditable
```

## Slice 1.4 — Project and Slice CRUD

### Objective

Allow humans to create and manage Relay projects and slices using the domain/state model.

### Capabilities

- create slice;
- edit definition;
- set dependencies;
- attach artifacts;
- mark scope/out-of-scope;
- add acceptance criteria;
- block/unblock;
- cancel;
- supersede.

### Out of scope

- LLM-generated work;
- code execution.

### Exit bar

```text
[ ] complete slice can be created manually
[ ] dependencies enforced
[ ] invalid state edits rejected
[ ] artifacts linked
[ ] all mutations audited
```

## Slice 1.5 — Board Projection

### Objective

Provide the first human-facing board.

### Principle

The board is:

> a projection of project state.

It is not a free-form source of truth.

### Required card information

At minimum:

```text
slice ID
title
state
assigned role
traffic-light summary
authorization
dependencies
baseline
result SHA
acceptance/evaluation status
blockers
```

### Requirements

- filtering;
- state columns;
- card detail;
- visible traffic lights;
- human-required attention.

### Important restriction

Dragging a card must invoke a legal transition request.

The UI cannot directly mutate state.

### Exit bar

```text
[ ] board reconstructed entirely from domain state
[ ] illegal drag rejected
[ ] yellow gates visibly require human decision
[ ] red reasons inspectable
[ ] green gate action deterministic
[ ] board refresh never changes project truth
```

## Slice 1.6 — Human Authorization and Decision Gates

### Objective

Implement explicit human authority.

### Required human actions

Initially:

```text
APPROVE
REJECT
CHOOSE_PATH
PAUSE
BLOCK
DEFER
CANCEL
```

### Authorization record

Must include:

```text
actor
timestamp
target slice
baseline
contract/artifact versions
scope
decision
reason if required
```

### Exit bar

```text
[ ] authorization pinned to exact baseline
[ ] contract change invalidates relevant authorization
[ ] human decision auditable
[ ] hard stop cannot be bypassed through normal UI
[ ] role permissions enforced
```

## Slice 1.7 — Manual Evaluation and Acceptance

### Objective

Complete the human-only development loop.

A user should be able to record:

```text
authorized
    ↓
external/manual implementation
    ↓
resulting commit
    ↓
manual evaluation
    ↓
accepted baseline
```

### Exit bar

```text
[ ] resulting SHA attached
[ ] evidence attached
[ ] evaluator decision represented
[ ] REWORK path supported
[ ] ACCEPT creates new accepted baseline
[ ] development memory generated or updated
```

---

# Phase 1 Hard Stop — M0 Validation

At this point Relay should be used to govern at least one real project manually.

Candidate dogfood project:

- WellPlot;
- tension-modeling;
- Offline RAG;
- Relay itself.

Required experiment:

```text
Does the board clarify project state?

Are traffic lights useful?

Does READY vs AUTHORIZED matter in practice?

Does development memory reduce repeated context explanation?

Are gates helpful or bureaucratic?

Can we reconstruct why an accepted commit exists?
```

If Relay is not useful before autonomy, the governance abstraction requires revision.

---

# 10. Phase 2 — Provider and Agent Foundation

Phase 2 introduces AI capability but not yet unconstrained multi-agent orchestration.

## Slice 2.1 — Model Provider Interface

### Objective

Create provider-independent model access.

### Initial provider classes

At minimum:

```text
OpenAI-compatible
Anthropic-compatible
```

Native optimizations may be added later.

### Generic capabilities

Provider abstraction should express capabilities rather than assume identical APIs.

Examples:

```text
text generation
structured output
tool use
reasoning control
context limit
streaming
usage reporting
```

### Exit bar

```text
[ ] provider interface model-neutral
[ ] two provider families supported
[ ] capability discovery/validation
[ ] usage reported
[ ] failures normalized without hiding provider detail
[ ] credentials external to .relay/
```

## Slice 2.2 — Role Contracts

### Objective

Formalize engineering roles.

Initial roles:

```text
Architect
Researcher
Contract Engineer
Planner
Implementation Agent
Evaluator
```

The Board/State role should remain primarily deterministic.

### Each role contract defines

```text
purpose
authority
required inputs
allowed tools
forbidden actions
required outputs
possible escalations
```

### Exit bar

```text
[ ] roles independent of models
[ ] roles serializable/versioned
[ ] forbidden actions explicit
[ ] required output schemas explicit
[ ] role contract included in execution provenance
```

## Slice 2.3 — Agent Configuration and Model Routing

### Objective

Assign models/providers to roles without coupling project semantics to vendor identity.

Conceptual configuration:

```yaml
agents:
  architect:
    provider: frontier
    model: ...

  coder:
    provider: coding
    model: ...

  evaluator:
    provider: independent
    model: ...
```

### Requirements

- project defaults;
- organization defaults later;
- per-slice overrides;
- model capability validation.

### Exit bar

```text
[ ] role can change model without modifying workflow
[ ] unavailable model detected before execution
[ ] provider credentials referenced, never committed
[ ] configuration version captured per execution
```

## Slice 2.4 — Context Builder

### Objective

Construct bounded, authoritative context for each role.

### Inputs may include

```text
role contract
handover packet
current baseline
accepted architecture
accepted contracts
relevant development memories
relevant repository files
research findings
evaluation findings
applicable scope/simplicity policy
project-selected quality profile
```

### Principle

Do not simply forward all previous conversations.

### Requirements

- deterministic authority ordering;
- explicit provenance of context components;
- context budget;
- scoped retrieval;
- separation of authoritative vs informational content.

### Exit bar

```text
[ ] every context item has source
[ ] accepted authority distinguishable from suggestions
[ ] stale/superseded artifacts excluded or marked
[ ] context size bounded
[ ] generated prompt reproducible from stored inputs
```

---

# 11. Phase 3 — First Autonomous Engineering Loop

This phase creates the first capability that can directly validate Relay's product thesis.

## Slice 3.1 — Execution Workspace

### Objective

Provide isolated ephemeral execution environments.

### Required behavior

```text
authorization
   ↓
provision workspace
   ↓
checkout exact baseline SHA
   ↓
configure allowed credentials/tools
   ↓
execute role
```

### Security requirements

- tenant isolation;
- filesystem isolation;
- restricted secrets;
- configurable network policy;
- resource budgets;
- teardown.

### Exit bar

```text
[ ] exact SHA checkout
[ ] clean environment per execution
[ ] execution time/resource limits
[ ] workspace destroyed after completion
[ ] artifacts retained according to policy
[ ] secrets unavailable unless explicitly granted
```

## Slice 3.2 — Implementation Work Packet

### Objective

Convert an authorized slice into an implementation packet.

Required packet fields:

```text
slice ID
baseline SHA
objective
accepted architecture
contract
scope
out-of-scope
allowed files if constrained
acceptance criteria
required evidence
handover provenance
explicit non-authority
expected change surface
project-selected quality profile
```

### Exit bar

```text
[ ] packet generated only from authoritative state
[ ] authorization and baseline consistent
[ ] stale contract prevents generation
[ ] packet reproducible
[ ] explicit non-authority is present where applicable
[ ] expected change surface is included where configured
[ ] project-selected quality profile is included without changing repository tooling
[ ] no unrelated conversation history required
```

## Slice 3.3 — Coding Agent Execution

### Objective

Execute one implementation agent in one isolated workspace.

### Agent return contract

```text
resulting commit
changed files
implementation summary
tests run
test results
actual change surface
declared quality-check results
deviations
blockers
new work discovered
```

### Important rule

The implementation agent may submit work.

It may not accept it.

### Exit bar

```text
[ ] agent starts from exact baseline
[ ] unauthorized paths detectable where configured
[ ] commit produced
[ ] changed-file manifest captured
[ ] actual change surface captured
[ ] declared quality checks executed or explicitly reported unavailable
[ ] quality evidence captured
[ ] toolchain not changed unless explicitly authorized
[ ] no automatic acceptance
```

## Slice 3.4 — Evaluation Packet

### Objective

Construct an evaluator context independent of implementation conversation.

Inputs:

```text
objective
architecture
contract
baseline
result SHA
diff
tests
CI evidence
relevant memory
```

Implementation self-justification should not dominate evaluator context.

### Exit bar

```text
[ ] evaluator receives authoritative inputs
[ ] diff linked to exact SHAs
[ ] implementer chat not required
[ ] missing evidence explicit
```

## Slice 3.5 — Independent Evaluator

### Objective

Produce structured evaluation outcomes.

Allowed outcomes:

```text
ACCEPT
REWORK
ESCALATE_CONTRACT
ESCALATE_ARCHITECTURE
BLOCKED
EXPERIMENT_REQUIRED
```

Evaluation findings should identify:

```text
finding ID
severity
affected requirement
evidence
recommended routing
```

The evaluator must also assess, where applicable:

```text
scope adherence
minimum sufficient architecture
human clarity
change-surface deviation
declared quality evidence
unauthorized toolchain changes
```

Unnecessary complexity uses the existing `REWORK` outcome rather than introducing a new evaluator outcome.

### Exit bar

```text
[ ] evaluator cannot write production branch
[ ] output schema enforced
[ ] acceptance tied to contract version
[ ] findings structured
[ ] unnecessary complexity can route to REWORK
[ ] change-surface deviation reviewed when present
[ ] project quality evidence distinguished from semantic acceptance
[ ] model/provider recorded
[ ] evaluation reproducible from stored packet
```

## Slice 3.6 — Automated Rework Loop

### Objective

Automatically return implementation-level defects to the coder.

Flow:

```text
Coder
  ↓
Evaluator
  ↓ REWORK
Coder
  ↓
Evaluator
```

### Constraints

- same accepted upstream contract;
- correction scope includes evaluator findings;
- each iteration produces new immutable result;
- iteration budget configurable.

### Exit bar

```text
[ ] REWORK auto-routes
[ ] previous failed commit retained
[ ] evaluator findings attached
[ ] new commit reevaluated fully
[ ] loop limit prevents unbounded cycles
[ ] repeated failure escalates
```

## Slice 3.7 — Acceptance and Baseline Promotion

### Objective

Convert an accepted implementation into an authoritative project baseline.

Acceptance should:

```text
record evaluation
record evidence
record result SHA
update current baseline
generate/update development memory
invalidate affected downstream work if required
```

### Exit bar

```text
[ ] accepted SHA immutable
[ ] current baseline updated transactionally
[ ] prior baseline retained historically
[ ] development memory generated
[ ] downstream dependency effects computed
```

---

# Phase 3 Hard Stop — M1 Validation

This is the most important early hard stop.

Relay must dogfood several real slices using:

```text
human authorization
      ↓
coding agent
      ↓
independent evaluator
      ↓
automatic rework where appropriate
      ↓
accepted baseline
```

Measure:

- human interventions per slice;
- number of unnecessary clarification turns;
- evaluation accuracy;
- rework convergence;
- cost;
- cycle time;
- contract violations;
- memory usefulness.

Do not begin multi-agent swarms before this loop proves useful.

---

# 12. Phase 4 — Architecture, Contract, and Planning Automation

Once Relay reliably governs implementation, upstream roles can become executable.

## Slice 4.1 — Definition Agent

Produces bounded slice definitions from project objectives.

Must not authorize implementation.

## Slice 4.2 — Architecture Agent

Produces:

```text
architecture artifact
decisions
alternatives
affected boundaries
risks
research requests
experiment requests
```

Requires independent architecture gate policy.

## Slice 4.3 — Contract Agent

Produces:

```text
API/interface contracts
invariants
failure semantics
scope boundaries
acceptance criteria
```

Must consume accepted architecture.

## Slice 4.4 — Planner

Creates execution DAG without changing architecture or contracts.

Outputs:

```text
tasks
dependencies
parallelizable groups
integration points
```

## Slice 4.5 — Full Governed Role Chain

Target:

```text
Definition
   ↓
Architecture
   ↓
Contract
   ↓
Planning
   ↓
Authorization
   ↓
Implementation
   ↓
Evaluation
```

Initial strategic handovers remain human-approved.

---

# Phase 4 Hard Stop

Evaluate whether upstream agentization improves or degrades engineering quality.

If human review is repeatedly rewriting architecture and contracts, keep these stages primarily human-assisted rather than autonomous.

Relay should optimize actual value, not maximum agent count.

---

# 13. Phase 5 — Research

## Slice 5.1 — Research Task Contract

Define:

```text
question
context
source types
scope
budget
expected result
```

## Slice 5.2 — Source and Provenance Model

Support:

```text
papers
books
standards
official documentation
technical notes
Git repositories
code files/symbols
```

Code sources should prefer pinned commits.

## Slice 5.3 — Researcher Execution

Researcher may:

- search;
- collect;
- compare;
- synthesize;
- flag disagreement;
- identify validity limits.

It may not silently change architecture.

## Slice 5.4 — Research Gate

Research completeness should consider:

```text
question answered?
sources present?
source quality adequate?
conflicting evidence represented?
assumptions explicit?
open questions visible?
```

## Slice 5.5 — Research → Engineering Handover

A finding may result in:

```text
return to requester
architecture review
contract review
new experiment
human/domain expert review
```

---

# Phase 5 Exit Bar — M2 Partial

A real project should demonstrate:

```text
external source
    ↓
research finding
    ↓
engineering decision
    ↓
contract
    ↓
implementation
```

with traceable provenance.

---

# 14. Phase 6 — Sidecar Experiments

## Slice 6.1 — Experiment Domain Model

Required fields:

```text
parent work item
question
hypothesis
baseline
method
success criteria
failure criteria
budget
status
result
conclusion
```

## Slice 6.2 — Experiment Authorization

Experiment autonomy should consider:

- compute cost;
- external side effects;
- sensitive data;
- network access;
- branch permissions.

Low-risk experiments may auto-run.

Higher-risk experiments require human approval.

## Slice 6.3 — Isolated Experiment Workspace

Experiments should normally execute independently from production implementation branches.

## Slice 6.4 — Experiment Evidence

Capture:

```text
code
configuration
input data references
results
metrics
logs
environment
conclusion
```

## Slice 6.5 — Parent Integration

Experiment conclusion:

```text
SUPPORTED
REJECTED
INCONCLUSIVE
```

returns evidence to the parent.

It does not directly mutate production contracts.

## Slice 6.6 — Parallel Comparative Experiments

Support:

```text
EXP-A
EXP-B
EXP-C
```

from the same baseline with a common evaluation protocol.

---

# Phase 6 Hard Stop — M2 Complete

Demonstrate a genuine decision where Relay:

1. detects uncertainty;
2. creates an experiment;
3. runs it;
4. collects evidence;
5. returns evidence;
6. changes or confirms an engineering decision;
7. creates a clean production implementation.

---

# 15. Phase 7 — Dependency Invalidation and Staleness

As Relay's project graph becomes richer, upstream change propagation becomes essential.

## Slice 7.1 — Artifact Dependency Graph

Represent:

```text
decision → architecture
architecture → contract
contract → implementation
implementation → tests
research → decision
experiment → decision
```

## Slice 7.2 — Staleness Propagation

If an upstream authority changes:

```text
downstream artifact
    ↓
STALE
```

does not imply incorrectness.

It means reevaluation is required.

## Slice 7.3 — Revalidation

Allow downstream work to be revalidated against new authority without mandatory reimplementation.

## Exit bar

```text
[ ] upstream supersession finds dependents
[ ] dependents marked stale deterministically
[ ] stale work cannot silently become new authority
[ ] revalidation can restore validity
```

---

# 16. Phase 8 — Parallel Agent Development

Only begin after single-agent governance and staleness semantics are stable.

## Slice 8.1 — Work DAG Scheduler

Resolve which work is:

```text
BLOCKED
READY
AUTHORIZED
RUNNABLE
```

## Slice 8.2 — Parallel Workspaces

Each agent receives its own isolated environment.

No shared mutable checkout.

## Slice 8.3 — File and Resource Ownership

Detect likely collisions before execution.

Potential strategies:

- declared path ownership;
- package/module ownership;
- optimistic merge with conflict detection.

Exact policy requires design evaluation.

## Slice 8.4 — Integration Agent or Integration Procedure

Parallel branches must be recombined through a controlled integration step.

Integration is not merely:

```text
git merge everything
```

It must evaluate:

- contract compatibility;
- conflicts;
- combined tests;
- emergent behavior.

## Slice 8.5 — Integration Evaluation

Independent evaluation of the combined result.

## Slice 8.6 — Multi-Slice Orchestration

Enable:

```text
          S10
        /     \
      S11     S12
        \     /
          S13
```

with automatic readiness propagation.

---

# Phase 8 Hard Stop — M3

Relay must prove that parallel execution actually decreases cycle time without unacceptable integration/review burden.

If parallelism increases rework faster than throughput, scheduling policy requires revision.

---

# 17. Phase 9 — Cost, Budgets, and Operational Control

## Slice 9.1 — Token and API Accounting

Associate provider usage with:

```text
project
slice
role
execution
```

## Slice 9.2 — Compute Accounting

Track sandbox runtime and specialized compute.

## Slice 9.3 — Budgets

Possible limits:

```text
per execution
per slice
per experiment
per day
per project
```

## Slice 9.4 — Cost-Aware Routing

Allow policy such as:

```text
board summarization → cheap model
architecture → frontier
coding → coding model
evaluation → independent frontier
```

## Slice 9.5 — Cost per Accepted Slice

Primary metric:

```text
total model + compute expenditure
---------------------------------
accepted engineering output
```

Raw token usage is secondary.

---

# 18. Phase 10 — Security and Production Hardening

Security work begins earlier, but this phase prepares wider deployment.

Areas include:

- sandbox isolation;
- secrets management;
- network egress policy;
- malicious repository content;
- prompt injection from repository text;
- supply-chain risks;
- user authorization;
- audit logs;
- credential rotation;
- dependency scanning;
- incident response.

Security acceptance requires a separate dedicated plan.

---

# 19. Phase 11 — Collaboration and Organizations

Only after technical product value is established.

Capabilities may include:

```text
users
teams
organizations
project roles
approval policies
domain experts
review groups
cost centers
```

A scientific project may, for example, require:

```text
software reviewer
+
domain reviewer
```

before a yellow gate becomes green.

---

# 20. Phase 12 — External Project-Management Integrations

Potential systems:

```text
Linear
GitHub Issues
Jira
```

Relay should not initially depend on one.

External issue trackers may eventually become alternative projections or input sources.

Relay's engineering state remains governed by Relay's protocol.

---

# 21. Phase 13 — Commercial Productization

Potential later capabilities:

- onboarding;
- organization administration;
- billing;
- usage plans;
- support tooling;
- templates;
- enterprise policies;
- analytics;
- compliance features.

These should follow evidence that teams will pay for governed agentic engineering.

---

# 22. Experimental Sidecars During Relay Development

Relay's own development should permit `EXP-RLY-*` experiments.

Examples:

```text
EXP-RLY-01
Compare structured-output reliability across provider APIs.

EXP-RLY-02
Test whether handover packets outperform full conversation replay.

EXP-RLY-03
Compare same-model vs cross-model evaluation.

EXP-RLY-04
Measure evaluator accuracy with diff-only versus repository-context access.

EXP-RLY-05
Determine optimal development-memory retrieval strategy.

EXP-RLY-06
Compare experimental promotion vs clean reimplementation.
```

Each experiment should record:

```text
baseline
hypothesis
method
budget
result
decision impact
```

Experiments do not automatically become production architecture.

---

# 23. Dogfooding Strategy

Relay should be tested against multiple project archetypes.

## 23.1 Relay itself

Tests recursion and protocol completeness.

## 23.2 WellPlot

Useful for:

- architecture stabilization;
- agentic pipelines;
- structured-output contracts;
- evaluation;
- experimental branches;
- frequent rework.

## 23.3 Tension model

Useful for:

- scientific correctness;
- provenance;
- mathematical assumptions;
- locked architecture;
- explicit unauthorized future physics;
- hard stops;
- research;
- experimental validation.

## 23.4 Offline RAG

Useful for:

- incremental infrastructure;
- strong interfaces;
- deterministic artifacts;
- CLI contracts;
- evaluation pipelines;
- long multi-slice evolution.

The projects stress different Relay capabilities.

That is preferable to validating only on Relay itself.

---

# 24. Validation Matrix

Relay should eventually be validated across several project types.

| Capability | Relay | WellPlot | Tension | Offline RAG |
|---|---:|---:|---:|---:|
| Basic slices | ✓ | ✓ | ✓ | ✓ |
| Architecture handovers | ✓ | strong | strong | strong |
| Contracts | ✓ | strong | strong | strong |
| Evaluation/rework | ✓ | very strong | strong | strong |
| Research | moderate | moderate | very strong | moderate |
| Sidecars | strong | very strong | strong | useful |
| Provenance | moderate | useful | very strong | moderate |
| Hard stops | strong | strong | very strong | strong |
| Parallel agents | later | useful | selective | useful |

---

# 25. Development Metrics

Relay should instrument itself from early dogfooding.

## Core metrics

### Human interventions per accepted slice

Lower is generally better, subject to quality.

### Human decision density

Strategic human decisions should remain while mechanical interventions decline.

### Autonomous transition depth

Number of valid automatic handovers between required human decisions.

### Rework cycles

Number and cause.

### Escaped contract violations

Critical quality metric.

### Incorrect escalation rate

Did the evaluator route an implementation problem to architecture unnecessarily, or fail to escalate an upstream defect?

### Context restatement rate

How frequently must the human re-explain an accepted decision?

### Time to accepted baseline

End-to-end cycle time.

### Model cost per accepted slice

Economic metric.

### Experiment utility

Fraction of experiments that materially influence decisions.

### Memory retrieval accuracy

Can a fresh agent recover the right authority without broad conversational replay?


### Change-surface deviation

How often does implementation materially exceed the structure anticipated by the authorized slice?

### Complexity rework rate

How often does independent evaluation require simplification or removal of unauthorized/speculative architecture?

### Toolchain deviation

How often do agents attempt to add, replace, or reconfigure project quality tooling outside explicit scope?

---

# 26. Acceptance Philosophy

A slice is not accepted because:

```text
the agent says it is done
```

or:

```text
tests pass
```

or:

```text
the UI moved it to Done
```

Acceptance means the slice has satisfied its complete exit contract.

Depending on the slice, this may include:

```text
implementation
tests
architecture compliance
contract compliance
security checks
scientific evidence
evaluation
development memory
baseline identification
```

---

# 27. Slice Acceptance Template

Every implementation slice should contain an acceptance matrix.

Example:

| ID | Requirement | Evidence | Required |
|---|---|---|---:|
| A1 | Illegal transition rejected | unit test | yes |
| A2 | Transition emits event | unit test | yes |
| A3 | Hard stop blocks AUTO | integration test | yes |
| A4 | Human approval clears yellow gate | integration test | yes |
| A5 | State survives restart | persistence test | yes |

Acceptance matrices should be explicit before implementation begins.

---

# 28. Hard-Stop Policy for Relay Development

Recommended hard stops:

```text
HS0
Protocol foundation accepted

HS1
Human-only Relay workflow proven useful

HS2
Single-agent implementation/evaluation loop proven useful

HS3
Upstream role automation reviewed

HS4
Research + sidecars proven useful

HS5
Parallel agents shown to improve throughput

HS6
Security review before external beta

HS7
Commercial review before significant SaaS investment
```

These prevent momentum from becoming justification for continued investment.

---

# 29. Initial MVP Boundary

The smallest product deserving the name Relay should likely include:

```text
GitHub repository connection

.relay/ durable project memory

Project + Slice model

state machine

handover gates

traffic lights

human authorization

board projection

configurable coding agent

independent evaluator

automatic rework

accepted baseline promotion

development-memory update
```

Research and sidecar experiments are strategically important but may follow the first autonomous loop if implementation time requires prioritization.

---

# 30. MVP Non-Goals

The MVP does not need:

- dozens of agents;
- swarm behavior;
- autonomous product management;
- its own IDE;
- its own foundation model;
- generalized CI platform;
- enterprise billing;
- marketplace;
- every Git provider;
- mobile application;
- elaborate dashboards;
- full Jira replacement;
- automated organizational management.

The MVP tests governance.

---

# 31. First Dogfood Scenario

A recommended first serious dogfood flow is:

```text
Human creates real slice
        ↓
Architect/contract artifacts attached
        ↓
Relay evaluates readiness
        ↓
🟡 authorization
        ↓
Human approves
        ↓
🟢 Implementation Agent
        ↓
commit
        ↓
🟢 Independent Evaluator
        ↓
REWORK if needed
        ↓
automatic coder/evaluator loop
        ↓
ACCEPT candidate
        ↓
configured human or automatic acceptance
        ↓
new baseline
        ↓
memory generated
        ↓
next work becomes READY
but not automatically AUTHORIZED
```

That one workflow exercises most of Relay's core thesis.

---

# 32. Recommended First Build Order

The practical implementation order should therefore be:

```text
0.1 Repository foundation
0.2 Domain objects
0.3 State machine
0.4 Handover gates
0.5 Persistence/events
0.6 .relay contract

1.1 GitHub App
1.2 Baselines
1.3 .relay sync
1.4 Project/slice management
1.5 Board
1.6 Human authorization
1.7 Manual acceptance

DOGFOOD M0

2.1 Provider abstraction
2.2 Role contracts
2.3 Model routing
2.4 Context builder

3.1 Sandbox
3.2 Work packet
3.3 Coding execution
3.4 Evaluation packet
3.5 Evaluator
3.6 Rework loop
3.7 Acceptance/baseline

DOGFOOD M1
```

Only then:

```text
Definition/Architecture/Contract automation
Research
Experiments
Dependency invalidation
Parallel agents
Productization
```

---

# 33. Recommended Initial Repository Baseline

Before coding begins, Relay should create:

```text
README.md
docs/PRODUCT_PROPOSAL.md
docs/BUILD_PLAN.md
docs/CURRENT_BASELINE.md
docs/slices/
docs/decisions/
```

Then Slice 0.1 should be explicitly authorized.

The initial development memory becomes:

```text
SLICE_0_1_REPOSITORY_FOUNDATION_MEMORY.md
```

Relay should therefore be developed using its own documentary conventions from the first commit.

---

# 34. Conditions for Continuing Investment

Relay should not continue indefinitely merely because the project is technically interesting.

After M1, the team should explicitly evaluate:

## Continue if

- supervision burden decreases;
- context preservation materially improves agent performance;
- evaluation/rework loops reduce manual correction;
- project state is clearer than chat + Git alone;
- users find governance valuable rather than burdensome;
- accepted-slice economics are plausible.

## Reconsider if

- humans repeatedly bypass gates;
- development memory is rarely useful;
- evaluator loops create more work than direct review;
- coding-agent vendors absorb the important differentiation;
- Relay adds significant ceremony without reducing supervision;
- users value the board but will not pay for governance.

---

# 35. Build-Plan Invariants

The following apply throughout Relay development.

### BP-1

No future phase may invalidate accepted protocol semantics silently.

### BP-2

New automation must be introduced behind already-valid deterministic governance.

### BP-3

No provider becomes part of the core domain model.

### BP-4

No experiment becomes production architecture merely because it worked.

### BP-5

No parallelism before isolated single-agent execution is trustworthy.

### BP-6

No automatic acceptance before independent evaluation is operational.

### BP-7

No durable project decision should exist solely in cloud conversation history.

### BP-8

No secret belongs in `.relay/`.

### BP-9

Every accepted significant slice advances an explicit baseline.

### BP-10

Every major phase ends with a reviewable hard stop.


### BP-11

New architectural complexity requires justification from current accepted requirements or constraints.

### BP-12

Clarity is not sacrificed merely to reduce visible code or create a more generic abstraction.

### BP-13

Relay governs declared quality capabilities but does not impose a universal user-project toolchain.

### BP-14

Tooling migrations require explicit authorization and may not ride inside unrelated slices.

### BP-15

Passing deterministic quality checks does not by itself establish acceptance.

---

# 36. Definition of Initial Success

Relay's initial technical success is achieved when the following is possible:

```text
A complex project has an accepted baseline.

A new bounded engineering slice is created.

Relay knows what artifacts and dependencies are required.

Relay shows that the work is READY but not authorized.

A human authorizes it.

Relay constructs a clean implementation packet.

A coding agent works from the exact baseline.

Relay captures the resulting commit and evidence.

An independent evaluator reviews it.

Implementation-level failures automatically return to the coder.

Upstream failures escalate rather than being patched around.

When accepted, the resulting SHA becomes the new baseline.

Relay updates durable development memory.

Downstream work becomes ready according to dependency rules.

The human did not need to repeatedly reconstruct project context or manually coordinate every transition.
```

If Relay can do this reliably, the central product thesis has meaningful evidence.

---

# 37. Immediate Next Step

The next development artifact should be:

# **Relay Slice 0.1 — Repository Foundation and Engineering Baseline**

Before implementation, Slice 0.1 should lock:

- language/runtime;
- package management;
- schema library;
- testing stack;
- lint/format/type-check policy;
- service/API skeleton boundaries;
- documentation conventions;
- baseline CI;
- development-memory format.

Once Slice 0.1 is accepted, Relay development can begin without repeatedly reopening foundation-level choices.

---

# 38. Working Conclusion

Relay should be built the same way it expects serious engineering projects to be built:

```text
small bounded changes
      +
explicit authority
      +
locked contracts
      +
evidence
      +
independent evaluation
      +
durable memory
```

The sequencing matters.

The tempting route is:

```text
board
→ agents
→ parallelism
→ impressive demo
```

The Relay route should instead be:

```text
protocol
→ governance
→ repository truth
→ human workflow
→ one trustworthy agent loop
→ research and experiments
→ parallel engineering
→ productization
```

That path is slower to produce a flashy swarm demonstration.

It is substantially more likely to produce the differentiated product Relay is intended to become.
