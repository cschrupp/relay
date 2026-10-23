# Relay — Authorized-Work Decomposition and Execution Granularity

**Policy version:** 0.1  
**Status:** HUMAN-APPROVED CROSS-CUTTING POLICY DIRECTION  
**Document class:** Living canonical policy  
**Canonical key:** `authorized-work-granularity`  
**Applies to:** Relay planning, WorkPacket construction, RoleContract execution semantics, AgentRuntime use, implementation handoffs, independent evaluation, rework, future Phase 3 orchestration, and execution telemetry  
**Authority:** `RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`  
**Date:** October 23, 2026

---

# 1. Purpose

Relay must obtain the productivity benefits of increasingly capable coding agents without weakening its authority, scope, evaluation, or Human-control model.

A recurring failure mode in agentic development is **external over-decomposition**:

```text
Human gives task
    ↓
agent performs one small edit
    ↓
agent stops
    ↓
Human says "proceed"
    ↓
agent performs next small edit
    ↓
agent stops
    ↓
repeat
```

This preserves apparent control but wastes the capabilities of the implementation agent.

It turns an agentic coding harness into a natural-language terminal.

Relay already contains the correct architectural mechanism for avoiding this failure:

```text
current authorized work
        ↓
bounded internal decomposition
        ↓
implementation / validation / repair
        ↓
terminal candidate
        ↓
independent evaluation
```

This policy defines how Relay should size externally governed work, how much autonomy an Implementer receives inside an authorized WorkPacket, when work must be split, and when a discovered requirement must become `PROPOSED_WORK` rather than an internal task.

The central rule is:

> **The WorkPacket is the externally governed engineering unit. Internal decomposition belongs to the executing agent.**

---

# 2. This policy does not create a parallel architecture

This policy is a refinement of existing Relay semantics.

It does **not** introduce:

```text
PlannerAgent
    -> private task graph
    -> WorkerAgent
    -> ReviewerAgent
```

as a second authoritative workflow beside Relay.

Relay remains the only governance state machine.

The existing control path remains:

```text
Human Authority
      ↓
exact authorized work
      ↓
WorkPacket
      ↓
RoleContract applicability
      ↓
Execution Workspace / Runtime
      ↓
Implementer execution
      ↓
terminal candidate/evidence
      ↓
Independent Evaluator
      ↓
Human acceptance
      ↓
authorized closure/promotion
```

Any runtime-local plan, checklist, subagent, scratchpad, milestone list, or feature list exists **inside** that governed execution.

It does not create Relay authority.

---

# 3. Frozen architecture relationships

The following relationships are controlling:

```text
WorkPacket
    = authoritative external work unit

NormalizedEngineeringIntent
    != authority

planning artifact
    != authority

runtime-local plan
    != authority

internal execution task
    != WorkPacket

internal milestone
    != Human approval gate

runtime-local subagent
    != Relay role authority

DECOMPOSE_AUTHORIZED_WORK
    != AUTHORIZE_WORK

Role eligibility
    != authority

Runtime capability
    != authority

Workspace capability
    != authority

PROPOSED_WORK
    != authorized work

BACKLOG_EXHAUSTED
    = successful stop when no authorized successor exists
```

No agent can manufacture authority by decomposing work.

---

# 4. Existing Relay role model remains controlling

This policy does not add permanent product role classes.

The accepted stable governance classes remain centered on:

```text
IMPLEMENTER
INDEPENDENT_EVALUATOR
HUMAN_AUTHORITY
PROMOTION_EXECUTOR
```

Architect, planner, researcher, reviewer, and vendor-specific agent names remain behaviors/personas unless a future separately accepted requirement proves that another stable Relay role class is necessary.

Operational personas such as SOL and Luna/Codex do not create another authority layer.

The governing relationship is:

```text
persona
    != RoleContract
    != actor identity
    != runtime identity
    != authority
```

---

# 5. External work versus internal execution

Relay distinguishes three different kinds of decomposition.

## 5.1 Roadmap decomposition

Durable and Relay-governed.

Examples:

```text
Phase
    ↓
Slice
    ↓
authorized engineering work
```

Roadmap decomposition defines independently governable outcomes.

It requires normal Relay authority.

## 5.2 Governed work decomposition

Durable when the decomposition creates independent outcomes.

Example:

```text
Slice 3.x
    ├─ WorkPacket A — implement orchestration
    ├─ WorkPacket B — implement crash recovery
    └─ WorkPacket C — build operator UI
```

Separate WorkPackets are justified when the outcomes have materially independent:

- authority boundaries;
- rollback/commit boundaries;
- acceptance criteria;
- delivery value;
- risk profiles;
- ownership;
- dependencies;
- execution environments.

## 5.3 Internal execution decomposition

Agent-owned and non-authoritative.

Example:

```text
one authorized WorkPacket

internal plan:
    inspect repository
    map contracts
    implement models
    implement evaluator
    implement provider
    write tests
    run validation
    repair failures
    self-review
```

These are **not separate Relay tasks**.

They do not require separate Human approval.

They may be created, reordered, retried, merged, or removed by the Implementer as execution strategy.

---

# 6. Governing invariant

Freeze:

```text
AUTHORIZED_WORK_UNIT
    !=
INTERNAL_EXECUTION_TASK
```

The first is governed by Relay.

The second is execution strategy.

The Implementer may autonomously derive internal execution tasks only when every task remains inside:

```text
exact WorkPacket scope
exact Human authority
exact baseline
exact RoleContract
exact WorkspacePolicy
exact runtime limits
exact quality/evidence contract
exact hard stops
```

Internal decomposition inherits the WorkPacket envelope.

It cannot widen it.

---

# 7. DECOMPOSE_AUTHORIZED_WORK semantics

The accepted RoleAction `DECOMPOSE_AUTHORIZED_WORK` should be interpreted operationally as:

> An eligible Implementer may derive and execute non-authoritative internal execution steps necessary to complete the exact currently authorized work.

Internal steps:

- inherit the exact WorkPacket authority envelope;
- may sequence implementation work;
- may inspect authorized repository context;
- may create temporary plans/checklists;
- may run authorized verification;
- may repair failures;
- may refactor within exact authorized scope;
- may self-review;
- may revisit earlier internal steps;
- require no individual Human approval merely because an intermediate milestone completed;
- may be retained as execution provenance;
- do not become independent Relay work authority.

Internal decomposition must not:

- expand the file/action scope;
- add dependencies outside authority;
- alter protected assets outside exact permission;
- create a new authoritative successor;
- create lifecycle state;
- issue Human authority;
- promote its own result;
- redefine acceptance criteria;
- silently weaken required verification.

---

# 8. Default task unit

The default externally authorized execution unit should be:

> **One cohesive, independently verifiable engineering outcome.**

The default should not be:

- one file;
- one class;
- one function;
- one test;
- one command;
- one internal milestone;
- one obvious "next step."

A WorkPacket should normally be large enough that the Implementer can exercise meaningful engineering agency.

---

# 9. Granularity labels

The following labels are **operational calibration terms only**.

They are not new Relay domain enums.

They do not create authority.

They do not require schema implementation unless a later accepted design explicitly adds them.

## SURGICAL

Typical human-equivalent effort:

```text
less than about 1 hour
```

Characteristics:

- deliberately narrow;
- high precision;
- usually one fragile invariant or bounded correction;
- low tolerance for collateral changes.

Use when narrowness directly reduces risk.

## STANDARD

Typical human-equivalent effort:

```text
about 1–4 hours
```

Characteristics:

- one coherent engineering outcome;
- several internally dependent implementation steps;
- usually one primary subsystem;
- one meaningful terminal candidate.

This is the normal minimum target.

## EXTENDED

Typical human-equivalent effort:

```text
about 4–8 hours
```

Characteristics:

- cohesive feature/contract implementation;
- several internal milestones;
- potentially multiple files/modules;
- strong deterministic validation;
- still one coherent acceptance boundary.

For mature frontier coding agents under a strong Relay envelope, the preferred default should often sit between upper STANDARD and lower EXTENDED.

Initial Relay target:

```text
approximately 2–6 human-expert hours
per externally governed implementation task
```

## CAMPAIGN

Typical human-equivalent effort:

```text
greater than about 8 hours
```

A campaign is appropriate only when the work remains one coherent authorized outcome and has strong durable milestone/evidence support.

If a campaign actually contains multiple independently valuable outcomes or authority boundaries, it should become multiple WorkPackets.

---

# 10. Human-equivalent effort is a calibration variable

The time bands above do not represent agent wall-clock time.

They represent an estimate of how long a competent human engineer, already familiar enough with the relevant repository context, would need to complete the engineering outcome.

This follows the useful idea in METR's task-horizon methodology: task difficulty can be calibrated against human completion time rather than model token count or runtime.

Relay must not treat the estimate as exact science.

Its purpose is to provide a consistent task-size calibration signal.

---

# 11. Task size is governed by semantic cohesion first

File count and line count are secondary signals.

A fifteen-file change may be one excellent WorkPacket if it implements one tightly coupled contract under one oracle.

A three-file change may require multiple WorkPackets if it crosses:

- an irreversible production side effect;
- a separate Human authority boundary;
- a protected verification boundary;
- a schema migration;
- an independent deployment/rollback unit.

The primary split question is:

> **Would these pieces normally be authorized, reviewed, accepted, and rolled back together?**

If yes, they are strong candidates to remain one WorkPacket.

---

# 12. When a task should be split

Externally split work when one or more of the following is true.

## 12.1 Independent authority

One portion requires authority the other does not.

## 12.2 Independent acceptance

The outcomes can be independently accepted or rejected without invalidating the other.

## 12.3 Independent rollback

The changes have materially separate rollback boundaries.

## 12.4 Different risk classes

One portion involves a materially different security, scientific, financial, operational, migration, or irreversible-side-effect risk.

## 12.5 Context coherence is lost

The combined working set is so broad that the agent repeatedly loses constraints, changes unrelated concepts, or fails to preserve invariant relationships.

## 12.6 Weak coupling

The parts do not require continuous shared reasoning and gain little from remaining in one execution trajectory.

## 12.7 Measured reliability

Relay telemetry shows that this class of combined task is beyond the reliable task horizon of the chosen model/runtime/harness.

---

# 13. When a task should not be split

Do not externally split merely because:

- several files are involved;
- several classes are needed;
- implementation has natural milestones;
- models and evaluators are separate modules;
- tests are separate files;
- the agent can describe multiple steps;
- a previous harness historically stopped after each step.

These are usually internal-decomposition concerns.

---

# 14. Surgical tasks are an exception

SURGICAL external granularity is justified when narrowness itself provides assurance.

Typical reasons:

```text
exact identity/digest contract
schema migration
cryptographic or security boundary
irreversible production side effect
protected verification asset
scientific certificate or scarce-run gate
delicate numerical invariant
narrow independent-review finding
high-risk compatibility repair
```

A WorkPacket should not become SURGICAL merely because the agent prefers small instructions.

---

# 15. Initial implementation versus corrective rework

Relay should normally use asymmetric granularity:

```text
initial implementation
    -> cohesive / larger

independent evaluation
    -> whole terminal candidate

corrective rework
    -> as narrow as the proven defect allows
```

This preserves throughput during construction and precision during correction.

A good independent review should make subsequent work smaller by proving exactly what is wrong.

---

# 16. Implementer execution loop

Inside one authorized WorkPacket, the Implementer should normally own:

```text
orientation
internal planning
repository inspection
implementation sequencing
local design choices inside accepted architecture
tests
validation
repair
bounded refactoring
self-review
terminal report
```

The Implementer should not return control merely because one internal phase completed.

---

# 17. Terminal conditions

An Implementer should continue autonomously until one of the following terminal conditions is reached.

## DONE

All authorized deliverables and required validation are complete.

## BLOCKED_BY_AUTHORITY

A required next action lies outside current exact authority.

## BLOCKED_BY_CONTRACT

Accepted requirements are materially contradictory, ambiguous, or impossible to implement inside the authorized envelope.

## BLOCKED_BY_ENVIRONMENT

A required tool/environment capability is unavailable and cannot be repaired inside scope.

## BUDGET_EXHAUSTED

An explicit execution budget has been reached.

## BACKLOG_EXHAUSTED

The current authorized work is complete and no authorized successor exists.

---

# 18. Non-terminal events

The Implementer should **not** stop merely because:

- one internal milestone is complete;
- one file is complete;
- a unit-test subset passes;
- a reasonable next internal step exists;
- the agent would normally ask "shall I proceed?";
- the implementation plan changed inside scope;
- an internal repair is required;
- self-review identified an in-scope defect.

These are ordinary execution events.

---

# 19. Authority expansion remains expensive and governed

If the Implementer discovers that correct completion requires work outside the WorkPacket, the correct path is:

```text
current execution
      ↓
discovered outside-scope requirement
      ↓
PROPOSED_WORK
      ↓
STOP
      ↓
Relay/Human authority decides whether successor work exists
```

The Implementer must not create:

```text
"internal task 11: modify unauthorized subsystem"
```

and proceed.

The architectural objective is:

```text
internal decomposition
    = cheap and autonomous

authority expansion
    = explicit and governed
```

---

# 20. Independent evaluator behavior

The Independent Evaluator should normally receive the **terminal candidate**, not every internal implementation milestone.

Its job is to evaluate the governed engineering result against the exact contract.

Normal outcomes remain:

```text
ACCEPT
REWORK
ESCALATE
```

The evaluator does not become a continuous implementation copilot merely because the Implementer has internal milestones.

If review returns REWORK, the next authorized corrective scope may be narrower than the original implementation task.

---

# 21. Human Authority behavior

Human involvement should remain strongest at real governance boundaries:

- work authorization;
- design acceptance where required;
- materially expanded scope;
- protected/irreversible operations;
- technical/result acceptance;
- closure/promotion authority.

Human involvement should normally be absent from routine internal sequencing.

The goal is not "less Human control."

The goal is:

> **Human control at authority boundaries instead of Human micromanagement inside already-authorized work.**

---

# 22. Promotion remains separate

Even a perfect autonomous implementation run cannot promote itself.

The existing separation remains:

```text
implementation complete
    !=
independent acceptance
    !=
Human acceptance
    !=
promotion authority
    !=
promotion execution
```

Task-size policy does not weaken this chain.

---

# 23. Specialized agent mapping

Relay's existing specialized-agent structure should be interpreted as follows.

## Implementer

Primary actions:

```text
DECOMPOSE_AUTHORIZED_WORK
IMPLEMENTATION_MUTATE
IMPLEMENTATION_TEST_MUTATE
VERIFICATION_EXECUTE
```

The Implementer should have substantial autonomy inside the exact WorkPacket.

## Independent Evaluator

Primary action:

```text
EVALUATE_RESULT
```

The evaluator receives the terminal governed candidate/evidence subject.

## Human Authority

Owns:

```text
AUTHORIZE_WORK
ACCEPT_RESULT
```

as defined by the applicable governance contract.

## Promotion Executor

Performs only already-authorized mechanical promotion/finalization.

It does not decide promotion policy.

---

# 24. Planner/research/architect behavior

Planning, research, and architecture remain valid behaviors.

They do not create parallel authority.

Possible source flow:

```text
planner / researcher / architect output
        ↓
planning artifact / research artifact
        ↓
NormalizedEngineeringIntent where applicable
        ↓
Relay authority
        ↓
WorkPacket
```

External methods such as Spec Kit, OpenSpec, BMAD, enterprise workflows, or future planning systems may generate input.

Relay consumes their result through existing normalization/authority boundaries.

Their internal task graph is not Relay state.

---

# 25. Runtime-local planning and subagents

AgentRuntime owns runtime-local execution mechanics such as:

- internal planning;
- context compaction;
- tool iteration;
- session management;
- runtime-local subagents;
- retry strategy;
- scratchpads;
- milestone status.

Relay may observe these for provenance and progress.

Relay must not confuse them with:

- Human authority;
- RoleContract;
- WorkPacket;
- authorized successor work;
- independent evaluation;
- Human acceptance.

A runtime-local subagent inherits no Relay authority merely because the parent runtime created it.

The parent execution remains responsible for staying inside the exact Relay envelope.

---

# 26. No duplicate task database

This policy explicitly rejects a second authoritative task graph for internal execution.

Relay should not introduce, merely for implementation convenience:

```text
agent_task table
planner_task state machine
private autonomous backlog
agent-created authoritative child WorkPackets
parallel lifecycle for runtime subtasks
```

unless a later present-tense requirement proves such persistence necessary.

Execution progress may be recorded as provenance/observations without turning it into authority.

---

# 27. Campaign execution

A CAMPAIGN may use durable runtime-local milestone/status artifacts when necessary to survive context resets.

Those artifacts may contain:

- current milestone;
- completed milestones;
- validation results;
- decisions;
- remaining internal work;
- known issues.

They remain execution memory.

They are not automatically Relay roadmap/work authority.

If a milestone becomes an independently governable outcome, Relay should deliberately promote it into separately authorized work rather than silently treating the runtime plan as authoritative.

---

# 28. Provisional task-sizing targets

Initial Relay calibration should use:

```text
SURGICAL:
< ~1 human-expert hour

STANDARD:
~1–4 human-expert hours

EXTENDED:
~4–8 human-expert hours

CAMPAIGN:
> ~8 human-expert hours
```

Preferred default starting band:

```text
~2–6 human-expert hours
```

These numbers are provisional.

They are not authorization limits.

They should be revised from Relay's own observed execution/evaluation data.

---

# 29. Task horizon calibration

Relay should eventually estimate model/runtime/harness-specific task horizons.

Suggested future metrics:

```text
Relay-H50(model, runtime, harness)
Relay-H80(model, runtime, harness)
```

where H50/H80 represent approximate human-equivalent task durations at which the configured system completes governed tasks with 50% / 80% reliability under Relay's own workload distribution.

Until sufficient Relay data exists, a conservative operational heuristic is:

```text
normal target:
about 20–35% of measured H50

extended-task ceiling:
about 50–60% of measured H50

near/above H50:
use campaign structure or externally split independent outcomes
```

This is a Relay heuristic inspired by task-horizon research.

It is not a METR recommendation.

---

# 30. Execution telemetry

When Phase 3 execution exists, Relay should measure enough data to improve granularity policy empirically.

Candidate telemetry:

```text
estimated human-expert minutes
granularity label
files touched
net LOC changed
subsystems touched
agent actions
tool calls
tokens
agent wall time
Human interventions
internal milestones
first independent-review outcome
number of rework cycles
rework size relative to original task
escaped defects
rollback/rejection events
```

The goal is not agent productivity scoring.

The goal is to estimate where task size begins to harm correctness, cost, or review efficiency.

---

# 31. Initial operating targets

Before Relay has enough data for statistically grounded calibration, use these as operational targets rather than hard requirements:

```text
median Human implementation interventions:
0

normal terminal reports per WorkPacket:
1

median independent-review rework cycles:
0–1

initial first-pass independent acceptance target:
roughly 70–85%
```

Interpretation:

- persistently near-100% first-pass acceptance plus very short agent trajectories may indicate under-sized tasks;
- persistently poor first-pass acceptance, repeated context loss, or multi-cycle rework may indicate over-sized tasks or inadequate harness support;
- neither metric alone proves optimal granularity.

---

# 32. Anti-fragmentation signals

Relay should detect or at least surface patterns such as:

```text
many WorkPackets touching the same tiny change
repeated Human "proceed" decisions inside one coherent outcome
one-file-per-WorkPacket behavior without risk justification
implementation tasks with almost no internal agent action
sequential WorkPackets whose acceptance criteria are inseparable
repeated context reload caused by external microtasking
```

These are signals of pathological external decomposition.

They are not automatic failures.

---

# 33. Overload signals

Relay should also surface the opposite failure mode:

```text
frequent scope drift
repeated forgotten constraints
large unrelated refactors
many independent subsystems changed under one result
multiple independent rollback units
repeated evaluator discovery of unrelated defect classes
rework approaching the size of the original task
agent repeatedly exhausts context/budget before terminal candidate
```

These suggest that the authorized work may be too large or poorly scaffolded.

---

# 34. Quality controls replace micromanagement

Relay should prefer:

```text
exact authority
exact scope
exact baseline
RoleContract
WorkspacePolicy
deterministic validation
hard stops
independent evaluation
Human acceptance
```

over repeated natural-language permission checks.

If an action is already exactly authorized and remains inside deterministic constraints, asking the Human again usually adds latency without adding authority integrity.

---

# 35. Internal milestone validation

Internal milestones are encouraged for larger tasks.

Recommended pattern:

```text
milestone
    ↓
run relevant validation
    ↓
failure?
    ├─ yes -> repair before moving on
    └─ no  -> continue
```

Milestone completion should normally remain internal.

It becomes an external gate only when the WorkPacket or applicable governance contract explicitly says so.

---

# 36. Prompt/handoff requirements

Implementation handoffs should explicitly tell the agent:

```text
You own internal decomposition of this exact authorized work.

Continue through implementation, validation, repair, and self-review
without asking for approval after routine internal milestones.

Stop only when:
DONE
BLOCKED_BY_AUTHORITY
BLOCKED_BY_CONTRACT
BLOCKED_BY_ENVIRONMENT
BUDGET_EXHAUSTED
BACKLOG_EXHAUSTED
or another exact hard stop in the WorkPacket is reached.

If future/out-of-scope work is discovered:
record PROPOSED_WORK and stop;
do not expand current authority.
```

This language should become standard in future Relay handoffs.

---

# 37. WorkPacket construction guidance

When constructing a WorkPacket, prefer one cohesive terminal outcome.

Good WorkPacket:

```text
Implement the accepted execution-workspace contract,
including exact models, pure evaluation, one bounded local provider,
tests, validation, and terminal candidate evidence.
```

Over-fragmented form:

```text
WP1 create enum
WP2 create first model
WP3 create second model
WP4 write evaluator helper
WP5 write one test file
WP6 run tests
```

unless one of those steps crosses a real authority/risk boundary.

---

# 38. Independent-review guidance

Independent evaluation should ask:

```text
Was the externally governed task a coherent outcome?

Did the Implementer exercise internal decomposition appropriately?

Did it stop unnecessarily at routine milestones?

Did it silently convert discovered future work into current work?

Did task size contribute to missed constraints?

Would rework benefit from a narrower corrective scope?
```

Granularity quality is therefore reviewable without making internal plans authoritative.

---

# 39. Future UI implications

A future Relay UI may show:

```text
current WorkPacket
execution status
runtime-local milestone/progress summary
validation status
proposed future work
hard-stop reason
terminal candidate
evaluation state
```

The UI must visually preserve:

```text
runtime progress
    !=
Relay authority state
```

An internal milestone marked complete must never look like an accepted Relay work item.

---

# 40. Phase 3 integration

Phase 3 should operationalize this policy inside the existing Relay loop.

It should not create a parallel orchestration architecture.

The desired Phase 3 shape is:

```text
Human Authority
      ↓
WorkPacket
      ↓
exact IMPLEMENTER binding
      ↓
Execution Workspace
      ↓
AgentRuntime
      ↓
bounded internal decomposition
      ↓
terminal candidate
      ↓
exact INDEPENDENT_EVALUATOR binding
      ↓
ACCEPT / REWORK / ESCALATE
      ↓
Human acceptance where required
      ↓
authorized closure/promotion
```

Rework may create a new narrow authorized WorkPacket or bounded corrective authority according to the applicable lifecycle/governance design.

---

# 41. Current Slice 2.4 implementation

The currently authorized Slice 2.4 implementation is already consistent with this policy's direction.

It is one cohesive implementation outcome spanning the exact authorized execution-workspace package and test surface.

This policy does not alter:

`RLY-S24-CODEX-SCOPE-001`

or:

`RLY-S24-IMPL-AUTH-001`.

No file, authority, or acceptance contract from the active implementation is changed by this documentation policy.

---

# 42. Empirical basis

This policy incorporates current research and engineering evidence but does not treat external evidence as Relay authority.

## 42.1 OpenAI — agent-first engineering

OpenAI's 2026 harness-engineering report describes a workflow where humans specify intent and constraints while Codex agents execute substantial engineering work, supported by repository structure, tests, feedback loops, review, and enforceable boundaries.

Relevant implication:

```text
control through environment + validation + review
can replace line-by-line Human steering
```

Source:

https://openai.com/index/harness-engineering/

## 42.2 OpenAI — long-horizon Codex experiment

OpenAI documented a roughly 25-hour uninterrupted Codex experiment with a frozen specification, milestone plan, validation after milestones, stop-and-fix behavior, and durable status/decision records.

Relevant implication:

```text
large external objective
+
internal milestone decomposition
+
continuous verification
```

can be more effective than repeated external micro-prompts.

Source:

https://developers.openai.com/blog/run-long-horizon-tasks-with-codex

This was explicitly an experiment, not proof that every production task should run for 25 hours.

## 42.3 Anthropic — long-running harnesses

Anthropic's long-running-agent work emphasizes environment scaffolding, durable feature/status state, and incremental internal progress.

Its "one feature at a time" recommendation should be understood at a meaningful feature/outcome level, not one edit/file at a time.

Source:

https://www.anthropic.com/research/effective-harnesses-for-long-running-agents

Anthropic's later harness work also stresses that harness assumptions can become stale as models improve.

Source:

https://www.anthropic.com/research/managed-agents

Relevant Relay implication:

```text
agent autonomy policy must be recalibratable
rather than frozen around the limitations of an older model generation
```

## 42.4 Runtime-structured decomposition research

A 2026 study comparing monolithic, static-decomposition, and runtime-structured coding workflows reported that static decomposition alone could increase retry cost, while runtime-structured selective re-execution reduced retry cost in the tested workloads.

Source:

https://arxiv.org/abs/2605.15425

The study is small and should not be generalized mechanically.

Relay uses it as evidence for the narrower proposition:

> **More externally fixed subtasks do not automatically produce lower cost or higher reliability.**

## 42.5 METR human-calibrated task horizons

METR defines model task horizon using the human time required for software/reasoning tasks and shows that task duration is strongly predictive of autonomous completion probability.

Sources:

https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/

https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/

Relevant Relay implication:

```text
task-size policy should eventually be calibrated
against human-equivalent engineering difficulty
and actual Relay success data
```

not only file count, LOC, token count, or agent wall-clock time.

---

# 43. Evidence boundaries

The research above supports several directional conclusions:

- capable agents can sustain materially longer engineering trajectories when the harness provides durable goals and verification;
- runtime/internal decomposition is valuable;
- static decomposition is not automatically more efficient;
- model capability changes quickly enough that harness policies need recalibration;
- human-equivalent task duration is a useful difficulty signal.

The research does **not** prove:

- a universal 2–6 hour optimal task size;
- that every agent should run for many hours;
- that Human review is unnecessary;
- that one WorkPacket should contain an entire release;
- that all models/runtimes have the same horizon.

Relay's numerical bands are therefore provisional engineering policy.

---

# 44. Adoption rule

Effective immediately for future governed handoffs:

> **Externally authorize cohesive outcomes; let the Implementer decompose internally; use narrow externally governed tasks only when risk, authority, independence, or measured reliability justifies the split.**

Future product implementation may add telemetry or explicit granularity metadata only through separately authorized design/implementation.

This policy itself does not modify existing accepted schemas.

---

# 45. Compact policy

```text
ONE RELAY WORKPACKET
    = one cohesive governed engineering outcome

IMPLEMENTER
    owns bounded internal decomposition

INTERNAL TASK / MILESTONE
    != authority
    != WorkPacket
    != Human gate

ROUTINE INTERNAL PROGRESS
    -> continue autonomously

OUT-OF-SCOPE REQUIRED WORK
    -> PROPOSED_WORK
    -> STOP
    -> separate authority

TERMINAL CANDIDATE
    -> independent evaluation

REWORK
    -> narrow corrective scope where possible

HUMAN CONTROL
    stays at authority / acceptance / irreversible-risk boundaries

NO PARALLEL TASK ARCHITECTURE
```

The intended result is higher development throughput without weakening Relay's deterministic governance model.
