# Relay — Product and Technical Proposal

**Version:** 0.3  
**Status:** Current living product and architecture proposal  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.2  
**Date:** September 2026

---

# 1. Executive Summary

Relay is a cloud-based control plane for agentic software engineering.

It connects to a Git repository and coordinates specialized AI agents across the software-development lifecycle while preserving explicit human authority, engineering context, architectural intent, traceability, and independent evaluation.

Relay is **not primarily a coding agent** and is **not primarily a Kanban board**.

Its purpose is to govern how multiple agents collaborate on complex, long-lived software projects.

Relay's central thesis is:

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Modern coding agents are increasingly capable of implementing substantial software changes. The emerging bottleneck is therefore shifting from code generation toward:

- defining the right work;
- preserving project context;
- maintaining architectural boundaries;
- coordinating multiple agents;
- controlling when work may proceed;
- evaluating changes independently;
- resolving uncertainty through research and experiments;
- preserving the reasoning behind accepted decisions.

Relay formalizes these activities.

A typical Relay project may involve:

```text
Product / Requirements Agent
        ↓
Researcher
        ↓
Architect
        ↓
Contract Engineer
        ↓
Planner
        ↓
Implementation Agents
        ↓
Independent Evaluator
        ↓
Acceptance / Rework / Escalation
```

Research and experimental work may branch from this main development flow when uncertainty cannot responsibly be resolved through reasoning alone.

Relay's board is the human-readable projection of this underlying engineering state machine.

The repository remains the durable engineering record through a version-controlled `.relay/` directory containing project definition, architecture, contracts, decisions, slice development memories, research records, experiment results, and configuration.

Relay's cloud infrastructure maintains runtime state such as agent executions, credentials, queues, temporary workspaces, model usage, and notifications.

---

# 2. Product Positioning

## 2.1 Relay is not primarily a vibe-coding product

Relay is not initially designed around the workflow:

```text
idea
 ↓
prompt
 ↓
agent writes application
 ↓
preview
 ↓
ship
```

That workflow is valuable, but it optimizes primarily for speed and ease of creation.

Relay instead optimizes for software where maintaining engineering intent becomes a significant part of the difficulty.

The target workflow is closer to:

```text
problem
  ↓
research
  ↓
engineering decisions
  ↓
architecture
  ↓
contracts
  ↓
implementation
  ↓
independent evaluation
  ↓
evidence
  ↓
accepted baseline
  ↓
durable engineering memory
```

The distinction is commercially important.

Vibe Kanban demonstrated real demand for coordinating coding agents: its creators reported thousands of software engineers using it daily. However, the company behind it shut down in April 2026 after finding that the large majority of users remained free and that the team could not find a business model it wanted to pursue. The project continues as open source.

Relay should therefore avoid competing primarily on:

- agent Kanban visualization;
- running several coding agents;
- diff viewing;
- previews;
- lightweight project management.

Those capabilities may exist in Relay, but they are infrastructure rather than the core value proposition.

---

# 3. Initial Target Customer

Relay is designed first for:

> **Professional developers, technical leads, scientists, and engineers using coding agents on long-lived, high-context software where correctness, architecture, evidence, and traceability matter.**

The strongest initial beachhead is expected to be **scientific and engineering software development**.

Examples include:

- scientific computing;
- industrial software;
- energy and subsurface applications;
- simulation and numerical modeling;
- ML and AI infrastructure;
- optimization systems;
- robotics;
- developer infrastructure;
- quantitative systems;
- security-sensitive systems;
- complex internal platforms;
- technical SaaS products with substantial domain logic.

These projects often have characteristics that make Relay valuable:

```text
substantial domain knowledge
+
long-lived architecture
+
many interacting assumptions
+
experiments
+
specialized validation
+
high cost of subtle mistakes
+
large accumulated context
```

A developer working in such a codebase needs agents to understand more than the latest feature request.

They need to understand:

> Why does the system work this way?

> Which architectural decisions are authoritative?

> What assumptions are scientifically or technically justified?

> Which contracts may not be changed?

> What experiments rejected alternative approaches?

> What remains deliberately unsupported?

> Which exact baseline was evaluated?

> What evidence justified acceptance?

Relay exists to preserve and operationalize those answers.

---

# 4. Broader Market

Relay's broader market is professional software engineering.

The market can be considered as three concentric groups:

| Segment | Initial Relay fit | Primary need |
|---|---:|---|
| Vibe coding / lightweight app generation | Lower | Fast creation |
| Professional software teams | High | Reliable multi-agent development |
| Scientific / engineering teams | Very high | Reliability + evidence + domain traceability |

Relay should build from the third group outward.

It should not require that all customers be scientists.

Rather, scientific and engineering development provides an environment where Relay's differentiating features are immediately valuable instead of appearing to be process overhead.

---

# 5. Market Context

The market is already validating the broader move toward agentic development orchestration.

OpenAI's Symphony explicitly describes a project-management board such as Linear as a **control plane for coding agents**, assigning open work to agents while humans review results.

Linear allows cloud coding sessions using coding agents directly from issues, combining planning, implementation, review, and iteration in its workspace.

GitLab's Duo Agent Platform provides multi-step development flows, code review, security review, custom flows, session logs, and multi-agent workflows.

These developments validate the overall direction while increasing competitive pressure.

Therefore Relay should not depend on the novelty of:

> "AI agents connected to a development board."

Its differentiation must exist one level above that.

---

# 6. Relay's Core Differentiation

Relay focuses on **engineering governance and continuity**.

Its core differentiators are:

### 6.1 Durable engineering memory

Accepted reasoning travels with the code.

### 6.2 Explicit engineering roles

Architect, Researcher, Contract Engineer, Coder, and Evaluator have different authority.

### 6.3 Governed handovers

Agent-to-agent transitions occur through explicit gates.

### 6.4 Independent evaluation

Implementers do not certify their own substantive work.

### 6.5 Explicit authorization

Technically ready work is not automatically authorized.

### 6.6 Research provenance

External evidence can be connected to engineering decisions.

### 6.7 Sidecar experiments

Agents can resolve uncertainty experimentally without contaminating the production baseline.

### 6.8 Versioned development contracts

Architecture, contracts, scope and acceptance criteria belong to the repository.

### 6.9 Model independence

Roles remain stable while model providers may change.

### 6.10 Deterministic governance

Ordinary software enforces transitions wherever reasoning is unnecessary.

The resulting proposition is:

> **Relay coordinates autonomous engineering work without allowing the engineering intent behind the work to disappear.**

---

# 7. Product Thesis

Relay is built around several fundamental observations.

## 7.1 Coding is becoming cheaper

AI coding agents increasingly handle implementation work that previously required substantial developer time.

## 7.2 Supervision is becoming the bottleneck

As the number and capability of agents increases, developers spend more time:

- decomposing work;
- reconstructing context;
- reviewing;
- correcting scope;
- deciding what to do next;
- coordinating parallel execution.

## 7.3 Chat history is not engineering memory

Important decisions need a durable representation independent of conversation context.

## 7.4 Repository structure alone cannot explain intent

Future agents can inspect code but cannot reliably infer why rejected alternatives were rejected or why particular boundaries exist.

## 7.5 More capable models do not eliminate governance

A model can reason better without becoming authoritative.

## 7.6 Some questions should be measured rather than debated

Sidecar experiments provide a systematic mechanism for turning uncertainty into evidence.

---

# 8. Core Principle

The central architectural principle is:

> **Agents perform engineering. Relay governs engineering.**

Relay therefore separates:

```text
Reasoning authority
        from
Transition authority
```

An Architect can propose architecture.

A Coder can implement code.

An Evaluator can assess it.

But the rules controlling whether a project transition is valid belong to Relay's governance engine.

---

# 9. Development Unit: The Slice

Relay organizes significant work into bounded **development slices**.

A slice is not merely a task.

It represents:

> **a controlled change from one accepted project baseline to another.**

Every significant slice has:

```text
identity
objective
parent objective

baseline

dependencies

scope
out of scope

authoritative artifacts

assigned role

acceptance criteria

authorization

implementation

evidence

evaluation

resulting baseline

development memory
```

A slice must be sufficiently bounded that its engineering effect can be understood and evaluated.

---

# 10. Standard Development Flow

A fully elaborated slice may proceed through:

```text
PROPOSED
   ↓
DEFINING
   ↓
RESEARCHING
   ↓
DESIGNING
   ↓
CONTRACTING
   ↓
PLANNING
   ↓
READY
   ↓
AUTHORIZED
   ↓
IMPLEMENTING
   ↓
EVALUATING
   ↓
ACCEPTED
```

But this is not a mandatory linear pipeline.

A small slice may consume already accepted architecture and begin at planning or implementation.

Evaluation may send work backward:

```text
                    ┌── REWORK
                    │
EVALUATING ─────────┼── CONTRACT REVIEW
                    │
                    └── ARCHITECTURE REVIEW
```

Research and experiments may branch sideways.

The result is therefore a **development graph**, not a simple workflow pipeline.

---

# 11. Board Model

The Relay board represents **state**, not organizational role.

Primary columns may include:

```text
PROPOSED
DEFINING
DESIGNING
CONTRACTING
READY
AUTHORIZED
IMPLEMENTING
EVALUATING
REWORK
ACCEPTED
```

Additional states include:

```text
RESEARCHING
BLOCKED
STALE
HARD STOP
SUPERSEDED
```

Roles should not be primary columns.

Instead, the same slice changes ownership as it progresses:

```text
S042
  Architect
      ↓
  Contract Engineer
      ↓
  Planner
      ↓
  Coder
      ↓
  Evaluator
```

The work item persists.

Responsibility changes.

---

# 12. Core Agent Roles

## 12.1 Product / Definition Agent

Responsible for understanding:

```text
what should be built
why it matters
what outcome is desired
what is outside scope
```

It may clarify requirements but may not implement production code.

## 12.2 Researcher

Responsible for investigating external knowledge relevant to engineering decisions.

Research modes include:

### Literature research

- peer-reviewed papers;
- books;
- technical notes;
- standards;
- scientific references.

### Code research

- open-source implementations;
- libraries;
- frameworks;
- algorithms;
- repository architectures.

### Practice research

- current documentation;
- engineering conventions;
- known implementation patterns;
- failure modes;
- ecosystem best practices.

The Researcher produces evidence.

It does **not** automatically decide architecture.

The authority chain remains:

```text
source
  ↓
research finding
  ↓
engineering decision
```

not:

```text
source
  ↓
automatic engineering decision
```

## 12.3 Architect

Responsible for:

- component boundaries;
- ownership;
- dependency direction;
- state models;
- interfaces between subsystems;
- major alternatives;
- migration implications.

The Architect may request research or sidecar experiments.

## 12.4 Contract Engineer

Turns architecture into precise implementation constraints.

Typical outputs include:

```text
APIs
schemas
types
invariants
failure semantics
allowed dependencies
forbidden dependencies
scope limits
acceptance matrices
```

The contract removes unnecessary interpretation from implementation.

## 12.5 Planner

Decomposes accepted engineering work into executable tasks.

It may identify:

- dependencies;
- parallelization;
- likely files;
- execution order;
- integration points.

It may not redesign architecture.

## 12.6 Implementation Agent

Responsible for coding within an explicitly authorized contract.

It can:

- modify authorized code;
- write tests;
- run validation;
- produce commits.

It cannot silently:

- expand scope;
- rewrite architecture;
- alter upstream contracts;
- authorize future work;
- accept its own implementation.

## 12.7 Evaluator

Independently evaluates implementation against authoritative project artifacts.

Its inputs may include:

```text
original objective
accepted architecture
accepted contract
baseline SHA
resulting SHA
diff
tests
CI results
relevant project memory
```

Its allowed outputs include:

```text
ACCEPT
REWORK
ESCALATE_CONTRACT
ESCALATE_ARCHITECTURE
BLOCKED
EXPERIMENT_REQUIRED
```

The Evaluator should not silently repair code while evaluating it.

## 12.8 State / Board Agent

Handles low-value administrative work:

- summaries;
- card descriptions;
- metadata extraction;
- human-readable explanations.

Actual state transitions should use deterministic software whenever possible.

---

# 13. Handover Gates

Every meaningful transfer between roles passes through a **Handover Gate**.

Example:

```text
Architect
    ↓
deliverable
    ↓
HANDOVER GATE
    ↓
Contract Engineer
```

A handover gate evaluates three independent concerns:

```text
VALIDITY
Are prerequisites satisfied?

AUTHORITY
Is the transition permitted?

AUTONOMY
May Relay perform it without a human?
```

---

# 14. Traffic-Light Model

Relay derives a traffic light for every possible handover.

## Green — automatic

```text
🟢
```

All requirements are satisfied and Relay may perform the transition automatically.

## Yellow — human required

```text
🟡
```

The transition is technically valid but policy requires human approval or choice.

## Red — prohibited

```text
🔴
```

The transition is currently invalid.

This may result from:

- missing artifact;
- failed evaluation;
- unsatisfied dependency;
- blocker;
- invalid baseline;
- contract violation;
- explicit policy.

The traffic light belongs to the **handover**, not to the agent.

A single work item can therefore expose several possible transitions:

```text
Evaluation complete

Accept                 🔴
Implementation rework  🟢
Contract review        🟡
Architecture review    🔴
```

This gives Relay a deterministic mechanism for choosing the next valid action.

---

# 15. Handover Policies

Each gate may declare one of several autonomy policies.

```text
AUTO
AUTO_NOTIFY
HUMAN_APPROVAL
HUMAN_CHOICE
```

## AUTO

Transition immediately when valid.

## AUTO_NOTIFY

Transition immediately and notify relevant humans.

## HUMAN_APPROVAL

Transition becomes yellow until explicitly approved.

## HUMAN_CHOICE

Several valid next paths exist and a human must select one.

---

# 16. Initial Human-in-the-Loop Defaults

Relay should initially err toward explicit human authority at strategic boundaries.

Recommended defaults:

| Handover | Initial policy |
|---|---|
| Definition → Architecture | Human approval |
| Architecture → Contract | Human approval |
| Contract → Planning | Automatic |
| Planning → Ready | Automatic |
| Ready → Authorized | Human approval |
| Authorized → Implementation | Automatic |
| Implementation → Evaluation | Automatic |
| Evaluation → Rework | Automatic |
| Rework → Evaluation | Automatic |
| Evaluation → Acceptance | Configurable |
| Evaluation → Contract escalation | Human choice |
| Evaluation → Architecture escalation | Human choice |
| Accepted → unrelated next slice | Human approval |
| Hard Stop → downstream execution | Human only |

Projects can gradually increase autonomy as confidence develops.

---

# 17. Hard Stops

A Hard Stop is a special governance boundary.

Examples include:

- completion of a major architecture phase;
- scientific model validation;
- migration to production runtime;
- destructive schema changes;
- security-sensitive work;
- entry into expensive computation;
- expansion into a previously unauthorized capability.

A hard stop cannot be crossed automatically.

```text
Slice accepted
      ↓
  HARD STOP
      ↓
 Human decision
      ↓
new authorization
```

---

# 18. Handover Packets

Agents should not simply inherit previous agents' conversations.

Instead Relay constructs structured handover packets.

Example:

```text
HANDOVER
Architecture → Contract

Slice:
S042

Baseline:
151efd0

Accepted artifacts:
architecture.md
ADR-014
ADR-015

Locked decisions:
D42-1
D42-2
D42-3

Affected interfaces:
ProviderV2
SectionDraft
GateAContext

In scope:
...

Out of scope:
...

Known risks:
...

Unresolved questions:
None
```

The receiving agent's context becomes:

```text
role contract
+
accepted project authority
+
relevant project memories
+
required repository context
+
handover packet
```

This reduces context pollution and prevents one agent's speculative reasoning from silently becoming another agent's authority.

---

# 19. Research System

Research is a first-class Relay capability rather than an informal web-search step.

Research may be initiated by:

```text
Product Agent
Architect
Contract Engineer
Implementation Agent
Evaluator
Human
```

A research task defines:

```text
research question
context
scope
source requirements
budget
expected deliverable
```

Its output includes:

```text
findings
sources
confidence
conflicting evidence
assumptions
open questions
possible engineering impact
```

---

# 20. Research Provenance

Research findings should be reproducible.

For papers and books, Relay should record appropriate bibliographic identifiers.

For source-code research, Relay should preferably record:

```text
repository
commit SHA
path
relevant symbols
```

rather than only a moving URL.

A durable chain may eventually look like:

```text
Paper
  ↓
Research Finding R14
  ↓
Architecture Decision D22
  ↓
Contract C31
  ↓
Implementation commit
  ↓
Acceptance test
```

This creates an **evidence graph** connecting external knowledge to production code.

This is particularly valuable for scientific and engineering software.

---

# 21. Sidecar Experiments

Relay introduces **Sidecar Experiments** for questions that should be measured rather than argued.

An experiment is a bounded child of a parent engineering decision.

Example:

```text
S042 — Retrieval Architecture
         │
         ├── EXP-S042-01
         │     hybrid retrieval benchmark
         │
         └── EXP-S042-02
               reranker latency benchmark
```

A sidecar experiment has:

```text
question
hypothesis
baseline
method
success criterion
failure criterion
scope
budget
result
conclusion
```

Possible conclusions:

```text
SUPPORTED
REJECTED
INCONCLUSIVE
```

---

# 22. Experiment Isolation

Experiments should normally execute in isolated branches or ephemeral workspaces.

```text
accepted baseline
      │
      ├── production slice
      │
      └── experimental branch
```

A crucial Relay invariant is:

> **Experimental code is evidence, not automatically production code.**

The normal path is:

```text
Experiment
    ↓
Evidence
    ↓
Architecture / Contract decision
    ↓
Authorized production slice
    ↓
Clean implementation
```

not:

```text
Experiment
    ↓
automatic merge
```

Promotion may eventually be supported, but it must pass the normal acceptance gates.

---

# 23. Parallel Experiments

Relay may run competing approaches in parallel.

```text
        Engineering question
          /      |      \
       EXP-A    EXP-B   EXP-C
          \      |      /
             Evidence
                ↓
             Decision
```

This provides a powerful mechanism for reducing architectural decisions based solely on model rhetoric.

---

# 24. Durable Repository State: `.relay/`

Each Relay-enabled repository contains a version-controlled:

```text
.relay/
```

directory.

An initial structure may be:

```text
.relay/
├── relay.yaml
│
├── project/
│   ├── definition.md
│   ├── architecture.md
│   ├── current-baseline.md
│   └── constraints.md
│
├── decisions/
├── research/
├── experiments/
├── slices/
│   ├── S001/
│   │   ├── slice.yaml
│   │   ├── definition.md
│   │   ├── architecture.md
│   │   ├── contract.md
│   │   ├── acceptance.md
│   │   ├── evaluation.md
│   │   └── memory.md
│   └── ...
│
├── agents/
│   ├── architect.yaml
│   ├── researcher.yaml
│   ├── contract.yaml
│   ├── planner.yaml
│   ├── coder.yaml
│   └── evaluator.yaml
│
└── templates/
```

The exact layout remains subject to detailed design.

---

# 25. Machine State vs Human-Readable Memory

Relay should distinguish machine-readable state from durable human-readable engineering records.

Example:

```text
.relay/slices/S056/slice.yaml
.relay/slices/S056/memory.md
```

`slice.yaml` supports automation.

`memory.md` explains the engineering history.

This prevents Markdown parsing from becoming the primary workflow database while preserving repository-native transparency.

---

# 25A. Documentation and Canonical Artifact Governance

Relay distinguishes three primary forms of engineering documentation:

```text
WORKING ARTIFACT
editable while work is active

LOCKED RECORD
immutable historical authority

LIVING PROJECTION
mutable representation of current truth
```

The governing rule is:

> **Historical authority is immutable. Current truth is mutable.**

Examples of locked records include accepted slice memories, locked ADRs, accepted contracts, submitted evaluations, authorizations, published research findings used as authority, experiment protocols after execution begins, experiment results, and evidence records.

Examples of living projections include:

```text
Product Proposal
Build Plan
Current Baseline
Current Architecture
Known Limitations
```

Relay must maintain an explicit canonical registry rather than infer canonical status from file names, folder position, or modification time.

The future UI and agent context builder should resolve the same canonical keys to the same current artifact revisions.

A canonical document presentation should expose, as appropriate:

```text
title
human-facing version
artifact revision
current / draft / locked / superseded status
source commit
content digest
supersession relationship
```

Git commit and content hash identify exact bytes. They do not replace semantic version or authority status.

The exact `.relay/` representation is deferred to the repository-contract slice, but the semantic policy is established in `DOCUMENTATION_GOVERNANCE.md`.

---

# 25B. Engineering Simplicity, Scope, and Quality Governance

Relay treats unnecessary structural complexity as an engineering-governance problem.

The central principle is:

> **Produce the clearest implementation with the minimum structural complexity necessary to satisfy the current accepted requirements and constraints.**

Supporting rules include:

> **Plausible ≠ necessary.**

> **New architectural complexity requires present-tense evidence.**

> **Shorter ≠ clearer.**

> **An abstraction must reduce cognitive load, not merely hide code.**

Implementation slices should eventually declare an expected **change surface** covering relevant dimensions such as:

```text
files
new modules
runtime dependencies
public interfaces
configuration keys
persistent-schema changes
new architectural mechanisms
```

Change surface is a governance signal, not an arbitrary LOC or file-count budget.

Material deviation must be surfaced and justified rather than silently absorbed.

Relay also prefers deterministic engineering constraints over additional prose whenever a project can express them as executable checks.

However, Relay governs **quality capabilities**, not specific tool brands.

Projects choose their formatter, linter, type checker, test runner, build command, schema validation, and custom checks. Existing repository tooling takes precedence unless a tooling migration is separately authorized.

Passing those checks does not establish engineering acceptance.

The Evaluator must still assess:

```text
scope
contract compliance
minimum sufficient architecture
human clarity
change-surface deviation
evidence sufficiency
```

A functionally correct change may therefore be returned for ordinary `REWORK` because it introduced unnecessary complexity.

The detailed policy is maintained in:

```text
ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md
```

---

# 26. Development Memory

Every significant accepted slice should produce development memory.

Recommended content:

```text
Status

Baseline
Resulting commit

Objective

Dependencies

Architecture

Locked decisions

Contract

Scope

Out of scope

Failure semantics

Implementation summary

Evaluation history

Acceptance evidence

Known limitations

Newly discovered work

Deferred work

Research / provenance

Hard stop / next authorization boundary
```

The purpose is not merely documentation.

It is **future agent context**.

A fresh agent should be able to understand why the codebase reached its present architecture without replaying months of conversations.

---

# 27. Current Baseline

Relay should maintain a concise current-baseline artifact answering:

> **What is authoritative now?**

It may summarize:

```text
accepted commit
architecture
public interfaces
active contracts
known-good behavior
regression baselines
known limitations
deferred capabilities
currently unauthorized work
```

Historical slice memories explain evolution.

Current Baseline explains present truth.

---

# 28. GitHub Integration

Relay should initially integrate through a GitHub App with least-privilege repository permissions.

Possible requirements include:

```text
repository metadata       read
contents                  read/write
pull requests             read/write
checks/actions            read
issues                    optional
```

Exact permissions should be validated during security design.

Relay should never describe work only as:

> work on main.

Every execution should resolve:

```text
repository
baseline SHA
working branch
work item
resulting SHA
```

---

# 29. Baseline Discipline

The baseline must be immutable for a given authorization.

Example:

```text
Authorized baseline:
151efd0
```

If `main` advances while an agent works, Relay still knows exactly what that agent was authorized to modify.

Later integration logic can determine whether rebasing or reevaluation is necessary.

This is essential for reproducibility.

---

# 30. Cloud Execution

Implementation agents should run in isolated ephemeral environments.

Conceptual flow:

```text
GitHub
  ↓
Relay
  ↓
Ephemeral workspace
  ↓
Checkout exact baseline
  ↓
Agent execution
  ↓
Tests
  ↓
Commit
  ↓
Push branch
  ↓
Independent evaluation
```

Parallel agents should not share a mutable checkout.

Each receives an isolated workspace or equivalent worktree.

---

# 31. Relay Cloud Architecture

A preliminary architecture is:

```text
                RELAY CLOUD

        ┌───────────────────────┐
        │      Board / UI       │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │   Governance Engine   │
        │                       │
        │ State machine         │
        │ Handover gates        │
        │ Authorization         │
        │ Dependency graph      │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │ Agent Orchestrator    │
        │                       │
        │ Context construction  │
        │ Role routing          │
        │ Model routing         │
        │ Execution lifecycle   │
        └───────────┬───────────┘
                    │
         ┌──────────┼───────────┐
         ▼          ▼           ▼
     Sandbox     Research    Evaluators
         │
         └──────────┬───────────┘
                    │
         ┌──────────▼───────────┐
         │   Model Providers    │
         └──────────┬───────────┘
                    │
         OpenAI-compatible
         Anthropic
         future providers

                    │
                    ▼
                  GitHub
                    │
                    ▼
                  Repo
                 /    \
              source  .relay/
```

---

# 32. Model Provider Abstraction

Relay must not bind agent roles to model vendors.

Providers may include:

```text
OpenAI-compatible
Anthropic-compatible
native OpenAI
native Anthropic
Azure
self-hosted inference
future providers
```

Configuration might conceptually look like:

```yaml
agents:

  architect:
    provider: primary_frontier
    model: frontier-model
    reasoning: high

  researcher:
    provider: primary_frontier
    model: frontier-model
    reasoning: high

  planner:
    provider: economical
    model: mid-tier-model

  coder:
    provider: coding
    model: coding-model

  evaluator:
    provider: independent_frontier
    model: frontier-model
    reasoning: high
```

Roles define authority.

Models provide capability.

---

# 33. Cost-Aware Routing

Relay should allow expensive reasoning to be concentrated where errors propagate most strongly.

Example policy:

| Role | Typical model class |
|---|---|
| Product definition | Frontier |
| Research synthesis | Frontier |
| Architecture | Frontier |
| Contract design | Frontier |
| Planning | Medium |
| Coding | Specialized coding model |
| Evaluation | Frontier |
| State synchronization | Deterministic / inexpensive |

This introduces an explicit engineering-economics layer.

Relay may eventually report:

```text
Architecture reasoning    $...
Research                  $...
Implementation            $...
Evaluation                $...
Total cost per accepted slice
```

Cost should be evaluated against **accepted engineering output**, not raw token usage.

---

# 34. Independent Evaluation Policy

For higher-risk work, Relay should support independent model evaluation.

Example:

```text
Implementation:
Provider A / Model X

Evaluation:
Provider B / Model Y
```

This does not guarantee correctness.

It reduces identical-context self-confirmation.

Possible configuration:

```yaml
evaluation:
  independent_provider_required: true
```

Projects may select a cheaper policy where appropriate.

---

# 35. Deterministic Governance

Relay should not use an LLM for checks normal software can perform reliably.

Examples:

```text
dependency accepted?
required artifact exists?
authorization exists?
commit exists?
CI passed?
forbidden file changed?
evaluation attached?
hard stop active?
```

These should be deterministic.

Reasoning models are appropriate for questions such as:

```text
Does this implementation satisfy architectural intent?

Are these tests sufficient?

Does the contract contain a conceptual inconsistency?

Does a research finding invalidate an assumption?
```

This separation is fundamental to Relay's trust model.

---

# 36. Core Data Model

Initial first-class objects include:

```text
Project
Repository
Slice
Artifact
Decision
Evidence
Baseline
Authorization
HandoverGate
Evaluation
ResearchTask
ResearchFinding
Source
Experiment
AgentRole
AgentAssignment
Execution
HumanDecision
```

Relationships between these objects form the project's development graph.

---

# 37. Dependency Invalidation

Relay should explicitly model the consequences of upstream changes.

Example:

```text
Contract v3
   │
   ├── Implementation A
   ├── Implementation B
   └── Test Suite C
```

If Contract v4 supersedes Contract v3, downstream claims may become:

```text
STALE
```

Stale means:

> The artifact is not necessarily wrong, but its validity against current authority has not been established.

This is more precise than silently assuming old implementation remains correct.

---

# 38. Human Authority

Humans remain responsible for strategic authority.

Typical human decision points include:

- project direction;
- major architectural choices;
- significant scope changes;
- scientific assumptions;
- consequential risk acceptance;
- security-sensitive transitions;
- hard stops;
- high-cost execution;
- abandoning or deferring work.

Relay's objective is not to eliminate human judgment.

It is to stop wasting human attention on mechanical coordination.

---

# 39. Human Intervention

Humans should be able to intervene proactively:

```text
PAUSE
BLOCK
REQUEST REVIEW
CHANGE PRIORITY
RETURN TO CONTRACT
RETURN TO ARCHITECTURE
DEFER
CANCEL
```

However, the board should not behave like an unconstrained Trello board.

Dragging:

```text
IMPLEMENTING
    ↓
ACCEPTED
```

must not silently bypass the acceptance process.

Human overrides should be explicit, permission-controlled, and auditable.

---

# 40. Human Decisions as Evidence

Important human decisions become part of project history.

Example:

```text
Architecture v3
approved by: project owner
date: ...
baseline: ...
reason: ...
```

Future agents can then distinguish:

```text
accepted decision
```

from:

```text
historical suggestion
```

This prevents human judgment from disappearing into ephemeral UI interactions.

---

# 41. Core Invariants

Relay should ultimately enforce several platform-level invariants.

### Invariant 1

No implementation without an explicit baseline.

### Invariant 2

No autonomous execution without authorization.

### Invariant 3

An agent cannot authoritatively approve its own substantive work.

### Invariant 4

Accepted upstream contracts cannot be silently changed downstream.

### Invariant 5

Scope expansion creates explicit new project state.

### Invariant 6

Acceptance requires evidence.

### Invariant 7

Accepted significant work creates durable engineering memory.

### Invariant 8

Upstream changes invalidate dependent claims until reevaluated.

### Invariant 9

Hard Stops cannot be crossed automatically.

### Invariant 10

Sidecar experiments cannot silently become production authority.

### Invariant 11

The board reflects project truth; it does not invent project truth.

### Invariant 12

Model identity and agent authority remain separate concepts.


### Invariant 13

Architectural complexity must be justified by current accepted requirements or constraints.

### Invariant 14

Clarity is a first-class engineering requirement; shorter or more generic code is not automatically simpler.

### Invariant 15

An implementation agent may not silently expand scope, generalize architecture, or migrate project tooling.

### Invariant 16

Declared project quality checks are deterministic evidence requirements, but passing them does not imply engineering acceptance.

---

# 42. Minimal Complete Engineering Chain

A fully traceable Relay work item has:

```text
WHY
Project objective
   ↓
WHAT
Slice definition
   ↓
EVIDENCE
Research where required
   ↓
HOW
Architecture
   ↓
RULES
Contract
   ↓
PERMISSION
Authorization
   ↓
CHANGE
Commit
   ↓
PROOF
Tests / evidence
   ↓
JUDGMENT
Independent evaluation
   ↓
AUTHORITY
Accepted baseline
   ↓
MEMORY
Development record
```

This chain is Relay's fundamental unit of trustworthy progress.

---

# 43. MVP Philosophy

Relay v0 should **not** attempt to build an entire autonomous software company.

It should test one product hypothesis:

> **Does formal engineering state, durable memory, governed handovers, and independent evaluation materially reduce the human effort required to supervise coding agents on complex projects?**

The MVP therefore focuses on the control plane.

---

# 44. MVP Scope

The first useful Relay implementation should include:

### Repository

- GitHub App connection;
- repository selection;
- exact SHA resolution;
- branch/commit visibility.

### `.relay/`

- configuration;
- project definition;
- slices;
- development memories;
- architecture/contracts;
- evaluations.

### Core state engine

- work item states;
- dependencies;
- authorization;
- deterministic transitions.

### Board

- visual state projection;
- human decisions;
- blockers;
- traffic lights.

### Handover gates

- prerequisites;
- automatic transitions;
- human approval;
- human choice.

### Initial roles

At minimum:

```text
Architect
Researcher
Implementation Agent
Evaluator
```

Contract and Planner roles can either exist separately or initially be composed with Architecture depending on MVP complexity.

### Model routing

- OpenAI-compatible provider;
- Anthropic-compatible provider;
- configurable role-to-model mapping.

### Evaluation loop

```text
Coder
 ↓
Evaluator
 ├── Accept
 └── Rework → Coder
```

### Sidecar experiment primitive

Initially lightweight but represented explicitly.

---

# 45. Explicit MVP Non-Goals

Relay v0 should not prioritize:

- replacing GitHub;
- replacing Linear/Jira;
- building a proprietary foundation model;
- building a new IDE;
- competing with Cursor;
- building a complete coding-agent runtime from scratch;
- sophisticated organization billing;
- generalized no-code application generation;
- large marketplace ecosystems;
- full compliance certification.

Existing coding agents should be reused where possible.

The first question is whether Relay's **governance layer** has value.

---

# 46. Dogfooding Strategy

Relay should be developed using Relay's own methodology as early as practical.

The system itself becomes a test project.

However, validation should also use an existing complex codebase.

A good dogfood project has:

```text
meaningful architecture
multiple slices
real regressions
external research
experiments
nontrivial tests
human decision points
```

The purpose is not merely to prove Relay can execute tasks.

It is to determine whether it reduces supervision.

---

# 47. Experimental Success Metrics

Relay should measure product value using engineering outcomes.

## Human interventions per accepted slice

How often does a human need to manually restart, redirect, or clarify agent work?

## Context restatement

How frequently must previously established decisions be manually explained again?

## Rework cycles

How many implementation/evaluation loops occur?

## Correct escalation

When failure occurs, does Relay correctly distinguish:

```text
implementation defect
contract defect
architecture defect
missing evidence
```

## Escaped violations

How often do accepted changes violate upstream contracts?

## Autonomous depth

How many valid transitions occur between meaningful human decisions?

## Cost per accepted slice

Model + compute cost divided by accepted work.

## Time to accepted slice

Elapsed development cycle time.

## Memory reuse

Can a new agent correctly continue the project using stored Relay artifacts?

---

# 48. Initial Product Success Criterion

The relevant question is not:

> Did Relay generate more code?

It is:

> **Did Relay allow trustworthy engineering work to advance with materially less human project supervision?**

If not, Relay adds process without adding value.

If yes, the product hypothesis is validated.

---

# 49. Competitive Positioning

Relay should not position itself as:

> "another AI Kanban"

or:

> "another multi-agent coding environment."

The market already provides increasingly capable versions of both.

Relay should position itself around:

> **Governed agentic engineering for complex software.**

Its distinguishing combination is:

```text
durable project memory
+
explicit engineering authority
+
typed handovers
+
human control points
+
independent evaluation
+
research provenance
+
bounded experimentation
+
model-independent execution
```

---

# 50. Potential Product Language

Working descriptions include:

> **Relay is the control plane for governed agentic software engineering.**

or:

> **Relay coordinates AI engineering teams without losing architecture, context, or control.**

or:

> **Relay turns coding agents into a governed engineering workflow.**

The exact commercial language remains open.

---

# 51. Why the Name Relay Fits

The name reflects the core operation of the system.

Engineering work is relayed between specialized roles:

```text
Requirement
  ↓
Research
  ↓
Architecture
  ↓
Contract
  ↓
Implementation
  ↓
Evaluation
```

But each relay is controlled.

Context is transferred through explicit artifacts rather than informal conversational inheritance.

Therefore the metaphor describes both:

- collaboration;
- handover discipline.

---

# 52. Principal Risks

## 52.1 Over-process

Relay could make simple work unnecessarily cumbersome.

Mitigation:

- configurable workflows;
- bypass lightweight stages where justified;
- progressive governance.

## 52.2 False confidence

Structured workflows may create the appearance of correctness.

Mitigation:

- evidence requirements;
- independent evaluation;
- explicit uncertainty;
- human gates.

## 52.3 Evaluator weakness

An evaluator can miss defects.

Mitigation:

- deterministic validation;
- tests;
- alternative models;
- specialized evaluation roles;
- human escalation.

## 52.4 Context explosion

Development memory may grow indefinitely.

Mitigation:

- current-baseline summaries;
- scoped retrieval;
- structured artifacts;
- supersession relationships.

## 52.5 Cost explosion

Parallel frontier agents and experiments can become expensive.

Mitigation:

- budgets;
- model routing;
- execution limits;
- per-slice cost reporting.

## 52.6 Agent vendor convergence

GitHub, GitLab, Linear, OpenAI, Anthropic and others may continue adding orchestration features.

Mitigation:

Relay should remain model- and executor-independent and differentiate at the engineering-governance layer.

## 52.7 Security

Relay receives meaningful repository permissions and executes untrusted/generated code.

Mitigation requires dedicated design around:

- least privilege;
- isolated sandboxes;
- credential separation;
- network policies;
- audit logs;
- secrets handling.

## 52.8 Commercial willingness to pay

Usage does not automatically create monetization.

Relay therefore needs to prove that governance solves an expensive professional problem, not merely that developers enjoy using agent orchestration.

---

# 53. Open Product Questions

The following remain intentionally unresolved:

1. What precise project complexity threshold makes Relay worthwhile?
2. How much process should be configurable versus opinionated?
3. Should Relay integrate with Linear/Jira or initially rely only on its own board?
4. How should agent prompts and role contracts be versioned?
5. How much project state belongs in Git versus the Relay database?
6. How should large historical memories be compacted?
7. Should evaluations always use different model providers?
8. When may experimental code be promoted rather than reimplemented?
9. How should merge conflicts between parallel agents be governed?
10. How should cost budgets influence autonomous routing?
11. What permissions should researchers receive for external sources?
12. How should scientific/domain expert review appear as a specialized human gate?
13. How should multi-repository projects be represented?
14. Which agent roles belong in the initial MVP versus later releases?

These should be resolved through design slices rather than prematurely fixed in this proposal.

---

# 54. Proposed Development Roadmap

## Slice 0 — Relay Protocol

Formalize:

```text
state machine
objects
invariants
handover semantics
authorization
evaluation outcomes
```

No significant product UI yet.

## Slice 1 — Repository Integration

Implement:

```text
GitHub App
repository discovery
baseline resolution
.relay initialization
```

## Slice 2 — Project State and Board

Implement:

```text
Project
Slice
Artifact
Decision
Evidence
board projection
```

## Slice 3 — Handover Gates

Implement:

```text
traffic lights
AUTO
AUTO_NOTIFY
HUMAN_APPROVAL
HUMAN_CHOICE
hard stops
```

## Slice 4 — Agent and Provider Configuration

Implement:

```text
role contracts
OpenAI-compatible providers
Anthropic-compatible providers
model routing
secrets
```

## Slice 5 — Implementation/Evaluation Loop

Implement:

```text
authorization
ephemeral workspace
coding execution
submission
independent evaluation
rework
acceptance
```

This slice represents the first meaningful autonomous loop.

## Slice 6 — Development Memory

Implement automated creation and maintenance of:

```text
slice memory
current baseline
decision history
accepted artifacts
```

## Slice 7 — Research

Implement:

```text
research requests
source records
findings
research handovers
research provenance
```

## Slice 8 — Sidecar Experiments

Implement:

```text
experiment contracts
isolated execution
budgets
results
evidence return
```

## Slice 9 — Parallel Development

Implement:

```text
work graph scheduling
parallel execution
file ownership
integration
staleness propagation
```

## Slice 10 — Organizational Governance

Later work may include:

```text
teams
permissions
policies
audit
organization-wide agent rules
cost allocation
```

---

# 55. Proposed Next Artifact

This proposal establishes Relay's product thesis and architectural direction.

The next document should be normative rather than descriptive:

# Relay Development Protocol and State Machine Specification

It should define exactly:

```text
entities
schemas

states

legal transitions

handover gate evaluation

traffic-light derivation

authorization semantics

human decision semantics

role authority

evaluation outcomes

sidecar lifecycle

research lifecycle

dependency invalidation

hard-stop behavior

development-memory requirements
```

That specification should become the contract used to implement Relay Slice 0.

---

# 56. Working Conclusion

The opportunity is not to build another interface around coding agents.

The opportunity is to solve the engineering problem that emerges **after coding agents become capable enough to do substantial work**.

That problem is:

```text
How do we let many capable,
nondeterministic agents perform
increasing amounts of engineering
without losing:

context,
architecture,
evidence,
accountability,
or human control?
```

Relay's answer is:

```text
structured project state

+ specialized roles

+ explicit handovers

+ deterministic governance

+ human authorization

+ independent evaluation

+ external research

+ bounded experimentation

+ durable engineering memory
```

If that combination materially reduces the supervision burden on complex software projects while preserving engineering quality, Relay has a distinct product position separate from both conventional project-management software and general-purpose coding agents.
