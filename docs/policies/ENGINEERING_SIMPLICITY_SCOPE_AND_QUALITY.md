# Relay — Engineering Simplicity, Scope, and Quality Governance

**Policy version:** 0.1  
**Status:** ACCEPTED CROSS-CUTTING DESIGN PRINCIPLE  
**Document class:** Living canonical policy  
**Canonical key:** `engineering-simplicity-quality`  
**Implementation:** Distributed across future governance, execution, evaluation, and UI slices  
**Date:** September 2026

---

# 1. Purpose

Agentic coding makes implementation cheap enough that unnecessary structure can accumulate faster than humans can review it.

Relay must therefore govern not only whether code works, but whether an implementation remains:

- inside the authorized scope;
- structurally necessary;
- clear enough for human review;
- consistent with the project's existing engineering conventions;
- verified through deterministic checks selected by the project.

The governing objective is:

> **Produce the clearest implementation with the minimum structural complexity necessary to satisfy the current accepted requirements and constraints.**

Relay is not trying to minimize line count.

Relay is trying to minimize **unnecessary cognitive and architectural burden**.

---

# 2. Core Principles

## SG-1 — Minimum Sufficient Architecture

A change should contain the minimum structural complexity necessary to satisfy the **current accepted requirements and constraints**.

Not the architecture that might someday be useful.

Not the most extensible architecture an agent can imagine.

Not the most elegant generic framework.

The smallest architecture that correctly solves the accepted problem.

---

## SG-2 — Clarity Is a Requirement

> **Use no more architecture than the current problem requires, and no less clarity than a human reviewer requires.**

The shortest implementation is not automatically the simplest implementation.

A solution should remain understandable to a competent engineer without requiring unnecessary indirection, framework knowledge, or reconstruction of a deep abstraction hierarchy.

---

## SG-3 — Plausible Does Not Mean Necessary

> **Plausible ≠ necessary.**

An architectural idea being reasonable, fashionable, elegant, or generally useful does not establish that the current requirement needs it.

---

## SG-4 — Complexity Requires Present-Tense Evidence

> **New architectural complexity requires present-tense evidence.**

Interfaces, factories, registries, plugin systems, event buses, generalized frameworks, new dependencies, configuration layers, or other structural mechanisms require justification from current accepted requirements.

Hypothetical future needs are not sufficient by themselves.

---

## SG-5 — Shorter Does Not Mean Clearer

> **Shorter ≠ clearer.**

Reducing line count, collapsing logic into generic helpers, or hiding behavior behind a compact abstraction is not an improvement if it makes the system harder to inspect, understand, debug, or modify.

---

## SG-6 — Abstraction Must Reduce Cognitive Load

> **An abstraction must reduce cognitive load, not merely hide code.**

An abstraction is justified when it gives the reader a simpler and more accurate mental model of the current system.

Moving complexity behind another interface without reducing the complexity a developer must understand is not simplification.

---

## SG-7 — Prefer Obvious Code Over Clever Code

When two implementations satisfy the same accepted requirements and constraints, Relay should favor the implementation whose behavior can be understood with:

- fewer assumptions;
- fewer jumps between files;
- less framework-specific knowledge;
- less hidden control flow;
- fewer speculative extension points.

This does not prohibit advanced architecture when the problem requires it.

---

## SG-8 — Unblocked Does Not Mean Authorized

Existing Relay principle:

> **Unblocked ≠ authorized.**

A technically possible next step does not imply permission to perform it.

This principle applies equally to architecture expansion.

A coder discovering that a broader redesign could be useful does not receive authority to perform it.

---

# 3. Human Reviewability

Important code must remain understandable to a human engineer.

A reviewer should be able to answer, without reconstructing unnecessary machinery:

```text
What does this code do?

Why is it here?

What calls it?

What does it depend on?

What happens when it fails?

Which current requirement requires this structure?
```

If an implementation makes these questions materially harder to answer without a corresponding current engineering benefit, it has introduced unnecessary complexity.

---

# 4. Minimality Test

For every newly introduced architectural mechanism, the evaluator should be able to ask:

> **What current accepted requirement would become materially harder or impossible to satisfy if this abstraction were removed?**

If no convincing answer exists, the abstraction is presumptively unnecessary.

This is not an automatic rejection rule.

It establishes a burden of justification.

---

# 5. Clarity Test

The evaluator should also ask:

> **Does this abstraction make the current system easier for a human engineer to understand, or does it only make the implementation shorter, more generic, or more extensible?**

Being shorter, more generic, or more extensible is not sufficient justification by itself.

---

# 6. No Speculative Generalization

Implementation agents must not expand a local requirement into a generalized capability unless that generalized capability is part of the accepted scope.

Examples include:

```text
single implementation
    → unsolicited plugin architecture

one constructor
    → unsolicited factory framework

two direct calls
    → unsolicited event bus

fixed set of handlers
    → unsolicited dynamic registry

local configuration
    → unsolicited generic configuration subsystem
```

Such ideas may be reported as:

```text
NEW_WORK_DISCOVERED
```

or:

```text
ARCHITECTURE_CONCERN
```

but they are not silently implemented.

---

# 7. No Opportunistic Refactoring

An agent working on Slice A must not use the opportunity to:

- rename unrelated concepts;
- reorganize adjacent packages;
- replace established dependencies;
- migrate formatting/lint/type tooling;
- generalize APIs unrelated to the slice;
- "clean up" broad areas of the repository;
- redesign neighboring components;

unless that work is explicitly in scope or separately authorized.

Passing tests does not convert unrelated work into authorized work.

---

# 8. Reuse Before Introduction

Before creating a new architectural mechanism, an implementation agent should determine whether the repository already contains a clear, accepted mechanism that satisfies the current need.

The preference order is:

```text
reuse an accepted clear mechanism
        ↓
extend it narrowly if authorized
        ↓
introduce a new mechanism only when current requirements justify it
```

This is not a rule to force reuse of bad abstractions.

If existing architecture is inadequate, the agent should escalate rather than silently work around it.

---

# 9. Change Surface

Every substantive implementation slice should eventually declare an **expected change surface**.

The purpose is not to enforce arbitrary numeric limits.

The purpose is to make architectural expansion visible.

A change surface may include:

```text
expected existing files touched
expected new production files
expected new modules/packages
new runtime dependencies
new public interfaces/types
new configuration keys
persistent-schema changes
new external services
new architectural mechanisms
```

Example:

| Dimension | Expected |
|---|---:|
| Existing files touched | 3 |
| New production files | 0 |
| New packages/modules | 0 |
| New runtime dependencies | 0 |
| New public interfaces | 0 |
| New configuration keys | 1 |
| Persistent schema changes | 0 |
| New architectural mechanisms | 0 |

---

# 10. Change Surface Is Not an LOC Budget

Relay should not use line count as the primary definition of minimality.

This is intentionally **not**:

```text
maximum 100 lines
maximum 3 files
```

A clear 200-line implementation may be better than a compressed 70-line generic framework.

Change-surface values are engineering expectations and governance signals.

They are not universal aesthetic limits.

---

# 11. Change-Surface Deviation

If actual implementation materially exceeds the declared change surface, Relay should surface the deviation explicitly.

Examples:

```text
planned new dependencies: 0
actual new dependencies: 2

planned new public interfaces: 0
actual new public interfaces: 5

planned new production files: 1
actual new production files: 9
```

A deviation is not automatically wrong.

It requires explanation and, depending on policy, may require human or architectural review.

The exact traffic-light behavior belongs to Slice 0.4.

---

# 12. Complexity Exception Record

When additional structural complexity is genuinely necessary, the implementation or evaluator should record:

```text
mechanism introduced
current requirement requiring it
simpler alternative considered
why the simpler alternative is inadequate
scope impact
future maintenance consequence if material
```

The objective is not bureaucracy.

It is to make architectural expansion deliberate rather than accidental.

---

# 13. Deterministic Engineering Constraints

Relay adopts another cross-cutting principle:

> **If a requirement can be expressed as a deterministic check, prefer the check over additional prose instructions.**

Examples:

```text
format check
lint check
type check
test suite
build check
schema validation
custom project validation
```

These checks provide agents with executable feedback rather than asking a model to infer quality from natural-language guidance alone.

---

# 14. Project-Selected Quality Profile

Relay governs **quality capabilities**, not specific tool brands.

A project may declare capabilities such as:

```text
FORMAT
LINT
TYPE_CHECK
TEST
BUILD
SCHEMA_VALIDATE
CUSTOM_CHECK
```

The project maps each capability to its chosen command or tool.

Example:

```yaml
quality:
  format:
    command: "uv run ruff format --check ."

  lint:
    command: "uv run ruff check ."

  type_check:
    command: "uv run pyright"

  test:
    command: "uv run pytest"

  build:
    command: "uv build"
```

Another project may use an entirely different toolchain.

---

# 15. Tool Choice Belongs to the Project

Relay must not universally require:

```text
Ruff
pytest
Pyright
Pydantic
Black
mypy
ESLint
Vitest
or any other specific tool
```

Relay may provide recommended presets.

The user or repository determines the active toolchain.

---

# 16. Existing Repository Tooling Has Precedence

For an imported repository, precedence is:

```text
1. Existing explicit repository quality contract
        ↓
2. User-approved Relay project configuration
        ↓
3. Relay recommended language profile
        ↓
4. No automatic migration
```

Relay may detect likely tools and propose configuration.

Detection does not make the tool authoritative.

The user or project configuration must adopt it.

---

# 17. No Toolchain Migration Without Authorization

An agent must not replace project tooling as part of unrelated work.

Examples:

```text
Black → Ruff
mypy → Pyright
unittest → pytest
Marshmallow → Pydantic
npm → pnpm
```

may be reasonable changes.

They are still separate engineering changes.

Tooling migration requires explicit scope and authorization.

---

# 18. Pydantic and Similar Schema Tools

Runtime/schema validation is an optional architectural capability, not a mandatory Relay requirement.

For Python projects, Pydantic may be an excellent project choice at validated boundaries such as:

- configuration;
- API payloads;
- durable schemas;
- structured agent outputs;
- serialized domain state.

Relay must not require a project to represent every internal object with Pydantic.

Equivalent project-selected technologies may be used.

---

# 19. Declared Quality Checks Become the Contract

Once a project explicitly declares a quality profile, the declared checks become part of its engineering quality contract.

An implementation work packet should eventually include:

```text
QUALITY CONTRACT

FORMAT       required
LINT         required
TYPE_CHECK   required
TEST         required
BUILD        required
```

with the exact project-selected commands.

The coding agent may not silently skip required checks.

---

# 20. Quality Evidence

Implementation submission should capture the results of declared checks.

Conceptually:

```text
FORMAT      PASS
LINT        PASS
TYPE_CHECK  PASS
TEST        PASS — 143 tests
BUILD       PASS
```

The command, exit status, and relevant result metadata should be preserved as evidence according to project policy.

A coder saying:

```text
"all tests passed"
```

is not equivalent to recorded evidence.

---

# 21. Quality Checks Are Not Acceptance

Deterministic checks answer questions such as:

```text
Does it format?
Does it lint?
Does it type-check?
Do declared tests pass?
Does it build?
```

They do not establish:

```text
Is the architecture appropriate?
Is the scope correct?
Is the code understandable?
Are the tests sufficient?
Is the domain logic correct?
Was unnecessary complexity introduced?
```

Therefore:

> **Green tooling does not imply engineering acceptance.**

---

# 22. Evaluator Responsibilities

The existing Evaluator should assess:

```text
functional correctness
contract compliance
scope compliance
evidence completeness
minimum sufficient architecture
human clarity
change-surface deviation
declared quality checks
```

There is no new `SIMPLIFY` evaluator outcome.

Unnecessary complexity routes through the existing:

```text
REWORK
```

outcome with structured findings.

This avoids adding a new workflow state or agent merely for simplicity.

---

# 23. Example Evaluator Findings

```text
UNAUTHORIZED_SCOPE_EXPANSION

UNNECESSARY_ABSTRACTION

CHANGE_SURFACE_EXCEEDED

UNJUSTIFIED_DEPENDENCY

UNRELATED_REFACTOR

CLARITY_REGRESSION

QUALITY_CHECK_FAILED

QUALITY_EVIDENCE_MISSING

TOOLCHAIN_CHANGED_WITHOUT_AUTHORIZATION
```

These are findings/reason codes, not lifecycle states.

---

# 24. Simplification Is Valid Rework

A change may be functionally correct and still require rework because its implementation is unnecessarily complex.

Example:

```text
tests pass
type check passes
build passes
        ↓
Evaluator:
UNNECESSARY_ABSTRACTION
        ↓
REWORK
        ↓
simpler implementation
        ↓
full reevaluation
```

This is a deliberate Relay capability.

---

# 25. No Dedicated Simplicity Agent Yet

Relay does not introduce a specialized "Simplicity Agent" or "Minimizer" at this stage.

That would add orchestration complexity before evidence shows it is needed.

Initial responsibility belongs to:

- the implementation contract;
- the coding agent's scope constraints;
- deterministic change-surface checks where possible;
- the independent evaluator.

A specialized role may only be introduced later if measured results justify it.

---

# 26. Quality Profiles as Options

Relay may eventually offer optional presets such as:

```text
python-modern
typescript-standard
rust-standard
```

A preset is a convenience for new projects.

It is not imposed on existing repositories.

Example Python preset could suggest:

```text
Ruff
Pyright
pytest
```

and optionally Pydantic for validated schemas.

The user can:

- accept;
- modify;
- replace;
- disable;

individual capabilities.

---

# 27. UI Requirements

The future UI should make the quality and simplicity contract visible without overwhelming the user.

A slice detail may show:

```text
Change surface
  3 expected files
  0 new dependencies
  0 new public interfaces

Quality profile
  Format       Ruff        required
  Lint         Ruff        required
  Type check   Pyright     required
  Tests        pytest      required
  Build        uv          required
```

After implementation:

```text
Change surface
  expected files: 3
  actual files:   4    ⚠ deviation

Quality
  Format       ✓
  Lint         ✓
  Type check   ✓
  Tests        ✓
  Build        ✓

Evaluator
  Clarity      review complete
  Scope        review complete
  Architecture review complete
```

The UI should distinguish deterministic checks from semantic evaluation.

---

# 28. Agent Context Requirements

Implementation agents should receive the relevant policy in concise form, not the entire policy document unless needed.

A work packet should eventually contain:

```text
current objective
in scope
out of scope
explicit non-authority
expected change surface
declared quality profile
minimum-sufficient-architecture rule
clarity requirement
escalation instructions
```

The agent should not need to infer these from project history.

---

# 29. Explicit Non-Authority

A work packet should be able to state that the agent is not authorized to:

```text
redesign adjacent systems
generalize APIs
introduce extension mechanisms
change project tooling
replace dependencies
perform unrelated refactors
add future-facing infrastructure
```

If one becomes necessary, the agent should surface it as discovered work or an upstream concern.

---

# 30. Metrics and Signals

Relay may record signals such as:

```text
files touched
new files
new modules
new dependencies
new public interfaces
new configuration keys
change-surface deviation
rework due to unnecessary complexity
rework due to scope expansion
```

Traditional metrics such as LOC or cyclomatic complexity may be collected as diagnostics.

They should not become universal pass/fail rules.

---

# 31. Non-Goals

This policy does not require:

- the shortest possible implementation;
- zero duplication at all costs;
- banning design patterns;
- banning abstraction;
- fixed LOC limits;
- one universal toolchain;
- Pydantic everywhere;
- mandatory Ruff/pytest/Pyright for user projects;
- automatic refactoring;
- a separate simplicity agent;
- eliminating architectural judgment.

The goal is disciplined complexity, not primitive code.

---

# 32. Integration With Relay Slices

## Slice 0.3 — Lifecycle

Scope/quality findings are **not lifecycle phases**.

A slice does not become:

```text
OVERENGINEERED
```

as a state.

Lifecycle remains structural.

## Slice 0.4 — Handover Gates

Must define how:

- missing required quality evidence;
- failed declared checks;
- unauthorized toolchain changes;
- material change-surface deviations;

affect RED/YELLOW/GREEN handovers.

## Slice 2.4 — Context Builder

Must include the concise scope/simplicity/quality contract relevant to the role.

## Slice 3.2 — Implementation Work Packet

Must carry:

- explicit non-authority;
- expected change surface;
- project-selected quality profile.

## Slice 3.3 — Coding Agent Execution

Must capture:

- actual change surface;
- declared quality-check results;
- deviations and justification.

## Slice 3.5 — Independent Evaluator

Must evaluate:

- scope;
- unnecessary complexity;
- clarity;
- change-surface deviation;
- quality evidence.

## Slice 3.6 — Rework

Must allow simplification and scope correction through ordinary `REWORK`.

## Board/UI

Should display change-surface and quality status while keeping deterministic checks visually distinct from semantic evaluation.

---

# 33. Core Invariants

### SQG-1

Current requirements, not hypothetical future requirements, justify architectural complexity.

### SQG-2

Clarity is not traded away merely to minimize line count.

### SQG-3

An abstraction must reduce cognitive load or provide a current engineering necessity.

### SQG-4

Agents may report broader opportunities but may not silently implement them.

### SQG-5

Material deviation from the expected change surface must be visible and explained.

### SQG-6

Change-surface metrics are signals, not universal LOC/file-count limits.

### SQG-7

Projects choose their quality tools.

### SQG-8

Existing repository tooling takes precedence unless a tooling change is explicitly authorized.

### SQG-9

Relay may suggest tools but may not silently make suggestions authoritative.

### SQG-10

Declared quality checks become enforceable project requirements.

### SQG-11

Passing deterministic checks does not imply acceptance.

### SQG-12

Functionally correct but unnecessarily complex code may be returned for rework.

### SQG-13

No dedicated simplicity agent is introduced without evidence that the additional role improves outcomes.

---

# 34. Working Conclusion

Relay should not solve agentic overengineering by adding more architectural ceremony.

It should solve it with a small number of strong rules:

```text
Minimum Sufficient Architecture
        +
Human Clarity
        +
Explicit Scope
        +
Visible Change Surface
        +
Project-Selected Deterministic Checks
        +
Independent Evaluation
```

The target is:

> **the clearest implementation with the least architecture required by the current accepted problem, verified by tools the project itself has chosen.**
