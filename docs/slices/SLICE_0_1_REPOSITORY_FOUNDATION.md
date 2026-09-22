# Relay Slice 0.1 — Repository Foundation and Engineering Baseline

**Slice:** 0.1  
**Phase:** 0 — Protocol and Deterministic Foundation  
**Status:** PROPOSED FOR DESIGN REVIEW  
**Parent:** *Relay — Build Plan and Development Roadmap v0.1*  
**Depends on:** Product Proposal and Build Plan only  
**Implementation authorization:** NOT YET GRANTED

---

# 1. Objective

Establish the smallest rigorous engineering foundation on which Relay can be developed.

Slice 0.1 creates:

- the repository structure;
- Python runtime and dependency-management policy;
- testing, formatting, linting and type-checking;
- CI;
- runtime configuration foundation;
- structured logging foundation;
- documentation conventions;
- slice-memory conventions;
- initial current-baseline document.

This slice deliberately contains **no Relay product behavior**.

The exit condition is:

> A clean checkout provides a reproducible, tested, typed, documented Python engineering environment ready for Slice 0.2 domain modeling.

---

# 2. Why This Slice Exists

Relay is intended to enforce disciplined development.

Its own repository should therefore begin with:

```text
reproducible environment
+
explicit baseline
+
automated quality checks
+
documented conventions
+
durable development memory
```

before product logic is introduced.

The purpose is not repository decoration.

The purpose is to ensure that every subsequent slice begins from a predictable engineering substrate.

---

# 3. Bootstrap Baseline

Because Relay does not yet have a repository, Slice 0.1 requires a bootstrap step.

The recommended sequence is:

```text
Create private Relay repository
        ↓
Add parent product/build documents
        ↓
Commit bootstrap repository state
        ↓
Record bootstrap commit SHA
        ↓
Authorize Slice 0.1 against that SHA
```

That commit becomes:

```text
BOOTSTRAP_BASELINE
```

Once a real SHA exists, all Slice 0.1 implementation and evaluation must reference it explicitly.

No implementation should use an implicit moving `main`.

---

# 4. Locked Foundation Decisions

The following decisions are proposed for Slice 0.1 review.

They become locked only after human approval.

---

## S0.1-D01 — Backend-First Architecture

Relay begins as a Python backend/control-plane project.

Slice 0.1 does **not** introduce:

- React;
- TypeScript;
- Node;
- frontend tooling;
- monorepo tooling.

The future board UI can be introduced when its own slice requires it.

### Rationale

The foundational product is the governance/state engine, not the UI.

Introducing two language ecosystems before any product semantics exist increases:

- dependency surface;
- CI complexity;
- repository complexity;
- maintenance burden;

without advancing the core product.

---

# 5. S0.1-D02 — Python Runtime

Use:

```text
Python 3.14
```

with:

```text
requires-python = ">=3.14,<3.15"
```

for the initial development baseline.

A `.python-version` file pins:

```text
3.14
```

### Rationale

Relay benefits from modern typing and Python ecosystem support, while Python aligns well with:

- AI provider integration;
- Git automation;
- cloud services;
- scientific tooling;
- experiment infrastructure;
- sandbox orchestration.

A Python minor-version upgrade should later be an explicit maintenance decision rather than silently changing the development baseline.

---

# 6. S0.1-D03 — Dependency and Environment Management

Use:

```text
uv
```

as the canonical Python environment and dependency manager.

The repository commits:

```text
pyproject.toml
uv.lock
.python-version
```

Canonical installation:

```text
uv sync --frozen --group dev
```

### Rules

`uv.lock` is authoritative for the development environment.

CI must use the lock file.

Dependencies must not be manually maintained through parallel:

```text
requirements.txt
requirements-dev.txt
environment.yml
```

unless a future deployment requirement specifically introduces one as a generated artifact.

---

# 7. S0.1-D04 — Distribution and Package Naming

Repository/product name:

```text
Relay
```

Python distribution name:

```text
relay-engine
```

Python import package:

```text
relay_engine
```

### Rationale

`relay` is a highly generic package name and may collide with unrelated ecosystem packages.

The internal name:

```text
relay_engine
```

also reflects the foundational responsibility of the Python service:

> Relay's governance and orchestration engine.

A future user-facing product rename therefore does not require immediate restructuring of every Python import.

---

# 8. S0.1-D05 — Package Layout

Use standard `src/` layout:

```text
src/
└── relay_engine/
```

Do not create empty future package hierarchies simply to mirror the roadmap.

For example, Slice 0.1 should **not** create empty:

```text
domain/
governance/
research/
agents/
experiments/
```

Those appear only when their implementation slices require them.

### Initial package

```text
src/
└── relay_engine/
    ├── __init__.py
    ├── settings.py
    └── observability.py
```

This keeps the initial baseline honest.

---

# 9. S0.1-D06 — Build Backend

Use a conventional PEP 517 build backend.

Proposed:

```text
hatchling
```

Relay should remain installable as a normal Python package:

```text
uv build
```

must succeed.

No custom build process is permitted in Slice 0.1.

---

# 10. S0.1-D07 — Runtime Dependency Policy

Slice 0.1 keeps runtime dependencies minimal.

Proposed runtime dependencies:

```text
pydantic
pydantic-settings
structlog
```

No dependency is added merely because it will probably be useful later.

Explicitly deferred:

```text
FastAPI
SQLAlchemy
Alembic
HTTP clients
GitHub SDK
OpenAI SDK
Anthropic SDK
Redis
Celery
Docker libraries
cloud SDKs
```

Each enters when a slice requires it.

---

# 11. S0.1-D08 — Configuration Model

Operational Relay settings are separate from future project `.relay/` configuration.

This distinction is permanent:

```text
Relay runtime configuration
        ≠
Relay project engineering state
```

Slice 0.1 introduces:

```text
RelaySettings
```

using `pydantic-settings`.

Initial settings should remain intentionally small.

Example semantic surface:

```text
environment
service_name
log_level
log_format
```

No provider credentials or database configuration are required yet.

---

# 12. Configuration Precedence

Initial runtime precedence:

```text
built-in defaults
      ↓
local .env file
      ↓
process environment variables
```

Environment prefix:

```text
RELAY_
```

Examples:

```text
RELAY_ENVIRONMENT
RELAY_LOG_LEVEL
RELAY_LOG_FORMAT
```

`.env` is development convenience only.

It must be gitignored.

Repository includes:

```text
.env.example
```

containing no credentials.

---

# 13. Configuration Rules

Slice 0.1 must enforce:

```text
unknown or invalid critical values fail visibly
```

No silent coercion of obviously invalid settings.

Secrets must not be printed by settings representations once secret-bearing settings are introduced in future slices.

No `.relay/` file participates in runtime infrastructure configuration during Slice 0.1.

That boundary is reserved for Slice 0.6.

---

# 14. S0.1-D09 — Structured Logging

Use:

```text
structlog
```

over Python's standard logging infrastructure.

Provide one configuration entry point:

```text
configure_logging(...)
```

Initial output modes:

```text
console
json
```

Recommended defaults:

```text
local       → console
test        → console/minimal
production  → json
```

---

# 15. Logging Contract

Structured logs should eventually support fields such as:

```text
timestamp
level
event
service
environment
```

Future slices may add:

```text
project_id
slice_id
execution_id
handover_id
agent_role
provider
model
```

Slice 0.1 must not invent those domain types yet.

Logging configuration must be:

- deterministic;
- idempotent;
- usable by libraries without global print statements.

Direct `print()` calls should not be used for application logging.

---

# 16. S0.1-D10 — Testing

Use:

```text
pytest
```

Canonical command:

```text
uv run pytest
```

Initial structure:

```text
tests/
└── unit/
```

Integration and contract test directories should be introduced only when needed.

No arbitrary coverage percentage is required in Slice 0.1.

### Rationale

A coverage target against an almost empty package rewards meaningless tests.

Coverage policy can be introduced when substantive domain behavior exists.

---

# 17. Required Initial Tests

At minimum:

```text
test_package_imports
test_package_version_exposed

test_settings_defaults
test_settings_environment_override
test_invalid_settings_rejected

test_logging_configuration_console
test_logging_configuration_json
test_logging_configuration_idempotent
```

Tests should verify behavior, not merely execute lines.

---

# 18. S0.1-D11 — Formatting and Linting

Use:

```text
Ruff
```

for:

- linting;
- import ordering;
- formatting.

Canonical commands:

```text
uv run ruff check .
uv run ruff format --check .
```

Automatic local formatting:

```text
uv run ruff format .
```

Avoid overlapping formatter/linter stacks such as:

```text
Black + isort + Ruff
```

when Ruff can provide the required function alone.

---

# 19. S0.1-D12 — Static Type Checking

Use:

```text
Pyright
```

for static analysis.

Production package policy:

```text
strict typing
```

Tests may use a slightly less strict configuration if test ergonomics require it.

Canonical command:

```text
uv run pyright
```

Relay's core domain and governance code should eventually be strongly typed because many future invariants depend on:

- states;
- IDs;
- transitions;
- contracts;
- artifact types.

Type discipline begins before those concepts are introduced.

---

# 20. Typing Conventions

Initial source-code conventions:

- explicit public return types;
- avoid `Any` unless boundary code genuinely requires it;
- narrow untrusted external data at boundaries;
- prefer typed value objects in future domain slices;
- avoid dictionaries as substitutes for known domain structures.

No elaborate internal type hierarchy is required in Slice 0.1.

---

# 21. S0.1-D13 — Canonical Quality Command Set

Relay should have a small canonical validation surface.

Required checks:

```text
ruff format --check
ruff check
pyright
pytest
build
```

Equivalent commands:

```text
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
```

These commands define the local and CI quality contract.

No developer should need to guess which commands determine repository health.

---

# 22. S0.1-D14 — CI Provider

Use:

```text
GitHub Actions
```

because GitHub is Relay's initial repository platform.

Initial workflow:

```text
.github/workflows/ci.yml
```

Triggers:

```text
push
pull_request
```

against relevant branches.

---

# 23. CI Pipeline

Initial CI sequence:

```text
checkout
   ↓
install uv
   ↓
install Python 3.14
   ↓
uv sync --frozen --group dev
   ↓
ruff format --check
   ↓
ruff check
   ↓
pyright
   ↓
pytest
   ↓
uv build
```

A failure at any stage fails CI.

No AI agent is permitted to interpret a red CI run as acceptable.

---

# 24. CI Reproducibility Rule

CI must install from:

```text
uv.lock
```

using frozen resolution.

CI must not implicitly upgrade dependency versions.

Dependency upgrades are repository changes.

---

# 25. S0.1-D15 — Local Developer Workflow

Relay should remain easy to develop on:

- Linux;
- macOS;
- Windows.

Canonical onboarding:

```text
git clone ...
cd relay
uv sync --group dev
uv run pytest
```

No dependency on:

```text
make
bash-only scripts
Docker
WSL
```

for ordinary local validation.

Convenience wrappers may be introduced later but must not become the only supported path.

---

# 26. S0.1-D16 — Pre-Commit Hooks

`pre-commit` may be configured as a convenience layer.

It is **not authoritative**.

CI remains authoritative.

If included, hooks should reuse the same Ruff checks rather than implementing separate quality policies.

A developer must still be able to run all canonical checks directly through `uv`.

---

# 27. S0.1-D17 — Documentation Format

Use Markdown for engineering documentation.

No documentation generator such as MkDocs is introduced yet.

Initial documentation:

```text
docs/
├── PRODUCT_PROPOSAL.md
├── BUILD_PLAN.md
├── CURRENT_BASELINE.md
├── decisions/
│   └── README.md
└── slices/
    ├── README.md
    └── SLICE_0_1_REPOSITORY_FOUNDATION_MEMORY.md
```

---

# 28. Documentation Responsibilities

## PRODUCT_PROPOSAL.md

Answers:

> What is Relay and why does it exist?

## BUILD_PLAN.md

Answers:

> How will Relay be built?

## CURRENT_BASELINE.md

Answers:

> What is authoritative now?

## decisions/

Holds future durable architectural decisions.

## slices/

Holds development memories for individual work packages.

---

# 29. S0.1-D18 — Current Baseline Contract

`docs/CURRENT_BASELINE.md` begins intentionally small.

After Slice 0.1 acceptance it should contain:

```text
Accepted SHA

Runtime:
Python 3.14

Dependency manager:
uv

Package:
relay_engine

Quality stack:
pytest
Ruff
Pyright

Configuration:
RelaySettings

Logging:
structured logging foundation

Current product capability:
NONE

Next authorized capability:
determined by explicit Slice 0.2 authorization
```

This explicitly prevents future agents from interpreting repository scaffolding as implemented Relay functionality.

---

# 30. S0.1-D19 — Development Memory

The Slice 0.1 memory is created during implementation:

```text
docs/slices/
SLICE_0_1_REPOSITORY_FOUNDATION_MEMORY.md
```

It begins:

```text
Status: IMPLEMENTING
Baseline: <bootstrap SHA>
```

and is finalized only after evaluation:

```text
Status: COMPLETE / ACCEPTED
Result: <accepted SHA>
```

---

# 31. Development Memory Required Content

The final memory must contain:

```text
Objective

Baseline

Resulting SHA

Locked decisions S0.1-D01 ... Dxx

Files created

Dependencies introduced

Commands

Validation evidence

Evaluation findings

Any deviations from contract

Known limitations

Deferred work

Hard stop

Next slice status
```

---

# 32. S0.1-D20 — Decision Records

Not every slice-level implementation choice requires a standalone ADR.

Use ADRs for decisions expected to materially influence multiple future slices.

Slice 0.1 should create at least one durable decision record covering:

```text
Runtime and engineering tooling baseline
```

Suggested:

```text
docs/decisions/
ADR-0001-runtime-and-tooling-baseline.md
```

The slice memory records local execution detail.

The ADR records the durable cross-project decision.

---

# 33. S0.1-D21 — Version Policy

Initial package version:

```text
0.1.0.dev0
```

Expose through:

```python
relay_engine.__version__
```

Release automation is out of scope.

Version bumps should not be tied automatically to every development slice.

A formal release/versioning policy can be added when Relay has user-visible releases.

---

# 34. S0.1-D22 — Repository Visibility and Licensing

Initial Relay development should use a:

```text
private repository
```

No open-source license should be selected merely as scaffolding.

Licensing is a product/business decision and is explicitly deferred.

The repository may contain copyright notices as appropriate, but Slice 0.1 does not commit Relay to:

```text
MIT
Apache-2.0
GPL
```

or another public distribution model.

---

# 35. S0.1-D23 — Secrets Policy

The repository must ignore:

```text
.env
.env.*
```

while explicitly retaining:

```text
.env.example
```

as appropriate.

Never commit:

- API keys;
- GitHub credentials;
- cloud tokens;
- private certificates;
- provider secrets.

No secrets are actually required by Slice 0.1.

---

# 36. Proposed Repository After Slice 0.1

```text
relay/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
├── .python-version
├── .env.example
│
├── README.md
├── CONTRIBUTING.md
├── pyproject.toml
├── uv.lock
│
├── src/
│   └── relay_engine/
│       ├── __init__.py
│       ├── settings.py
│       └── observability.py
│
├── tests/
│   └── unit/
│       ├── test_package.py
│       ├── test_settings.py
│       └── test_observability.py
│
└── docs/
    ├── PRODUCT_PROPOSAL.md
    ├── BUILD_PLAN.md
    ├── CURRENT_BASELINE.md
    │
    ├── decisions/
    │   ├── README.md
    │   └── ADR-0001-runtime-and-tooling-baseline.md
    │
    └── slices/
        ├── README.md
        └── SLICE_0_1_REPOSITORY_FOUNDATION_MEMORY.md
```

No other production packages are required.

---

# 37. README Requirements

Initial `README.md` should contain only useful repository information.

At minimum:

```text
Relay short description

Status:
pre-MVP / protocol development

Requirements:
Python 3.14
uv

Setup:
uv sync --group dev

Validation:
canonical commands

Key documents:
Product Proposal
Build Plan
Current Baseline
```

Avoid aspirational product marketing inside technical setup instructions.

---

# 38. CONTRIBUTING Requirements

`CONTRIBUTING.md` should establish:

```text
do not implement unauthorized future slices

start from explicit baseline

update slice memory

run canonical checks

do not commit secrets

do not change accepted architecture silently

experiments are not production changes
```

This gives human developers and coding agents the same basic project discipline from the first baseline.

---

# 39. Explicit In Scope

Slice 0.1 authorizes only:

1. repository engineering foundation;
2. package skeleton;
3. runtime settings foundation;
4. logging foundation;
5. quality tooling;
6. CI;
7. documentation conventions;
8. initial ADR;
9. initial slice memory;
10. current-baseline document.

---

# 40. Explicit Out of Scope

The following are **forbidden under Slice 0.1**:

### Relay domain concepts

No implementation of:

```text
Project
Slice
Artifact
Decision
Evidence
Baseline object
Authorization
HandoverGate
Evaluation
Experiment
ResearchTask
AgentRole
```

Those belong to Slice 0.2 onward.

### Persistence

No:

```text
database
ORM
migrations
Redis
event store
```

### Web/API

No:

```text
FastAPI
REST endpoints
GraphQL
web server
frontend
```

### GitHub

No:

```text
GitHub App
GitHub SDK
repository reads/writes
webhooks
```

### AI providers

No:

```text
OpenAI
Anthropic
model routing
agent prompts
tool calls
```

### Execution

No:

```text
Docker sandbox
cloud worker
agent workspace
job queue
```

### `.relay/`

No authoritative `.relay/` schema or synchronization semantics.

That belongs to Slice 0.6.

### Product UI

No board.

### Commercial functionality

No:

```text
billing
organizations
accounts
plans
```

---

# 41. Dependency Groups

Recommended `pyproject.toml` organization:

```text
runtime dependencies
```

and:

```text
development dependency group
```

Development group includes tools such as:

```text
pytest
ruff
pyright
pre-commit if adopted
```

Testing tools must not become runtime dependencies.

---

# 42. Error Policy

Slice 0.1 introduces no broad Relay exception hierarchy.

Errors should use ordinary appropriate Python exceptions.

A `RelayError` base type should not be invented until the domain model provides a concrete reason for one.

This prevents premature framework design.

---

# 43. Public API Policy

Slice 0.1 exports only minimal package metadata.

Expected:

```python
relay_engine.__version__
```

`RelaySettings` and logging helpers may be imported through their modules.

No commitment is made yet to a broad stable package-root API.

That begins when actual domain APIs exist.

---

# 44. Determinism Requirements

The following should be deterministic given the same repository/environment:

- package installation from lock file;
- formatting;
- lint results;
- type-check results;
- test results;
- build success;
- settings parsing from equivalent inputs.

Timestamps/log output obviously vary and are not treated as deterministic artifacts.

---

# 45. Acceptance Matrix

| ID | Requirement | Evidence | Required |
|---|---|---|---:|
| A01 | Clean Python 3.14 environment installs | clean `uv sync --frozen --group dev` | Yes |
| A02 | Package imports | pytest | Yes |
| A03 | Package version available | pytest | Yes |
| A04 | Settings defaults validate | pytest | Yes |
| A05 | Environment overrides work | pytest | Yes |
| A06 | Invalid settings fail visibly | pytest | Yes |
| A07 | Console logging config works | pytest | Yes |
| A08 | JSON logging config works | pytest | Yes |
| A09 | Logging configuration is safe to call repeatedly | pytest | Yes |
| A10 | Formatting clean | Ruff | Yes |
| A11 | Lint clean | Ruff | Yes |
| A12 | Production source type-checks | Pyright | Yes |
| A13 | Full test suite passes | pytest | Yes |
| A14 | Distribution builds | `uv build` | Yes |
| A15 | CI performs canonical checks | GitHub Actions run | Yes |
| A16 | Lockfile committed | repository inspection | Yes |
| A17 | `.env` ignored | repository test/inspection | Yes |
| A18 | `.env.example` contains no credentials | review | Yes |
| A19 | Product proposal and build plan committed | repository inspection | Yes |
| A20 | Current baseline created | review | Yes |
| A21 | ADR-0001 created | review | Yes |
| A22 | Slice memory finalized | review | Yes |
| A23 | No out-of-scope product logic introduced | diff evaluation | Yes |
| A24 | No AI/provider/GitHub dependencies introduced | dependency inspection | Yes |
| A25 | No authoritative `.relay/` schema introduced | diff inspection | Yes |

---

# 46. Canonical Acceptance Commands

The implementation agent must report the exact results of:

```text
uv sync --frozen --group dev

uv run ruff format --check .

uv run ruff check .

uv run pyright

uv run pytest

uv build
```

All must pass from a clean checkout.

---

# 47. Independent Evaluation Checklist

The evaluator should inspect more than whether CI is green.

It should explicitly verify:

### Scope

Did the implementation remain foundation-only?

### Dependency discipline

Were unnecessary frameworks introduced?

### Portability

Can development occur on Windows/macOS/Linux without requiring shell-specific tooling?

### Configuration separation

Has operational configuration remained separate from future project `.relay/` state?

### Documentation

Can a fresh developer determine how to install and validate the repository?

### Baseline discipline

Are bootstrap and accepted commits explicitly represented?

### Future leakage

Did the coder prematurely implement any Slice 0.2+ concepts?

---

# 48. Expected Evaluation Outcomes

Normal successful path:

```text
IMPLEMENTATION COMPLETE
        ↓
EVALUATION
        ↓
ACCEPT
        ↓
Slice 0.1 COMPLETE / ACCEPTED
```

Implementation-level problem:

```text
EVALUATION
   ↓
REWORK
   ↓
implementation correction
```

Foundation-design problem:

```text
EVALUATION
   ↓
DESIGN REVIEW
```

No evaluator should silently broaden Slice 0.1 to solve a future capability.

---

# 49. Exit Bar

Slice 0.1 is accepted only when:

```text
[ ] bootstrap baseline SHA recorded

[ ] Python 3.14 locked

[ ] uv environment reproducible

[ ] relay_engine package installable

[ ] RelaySettings implemented and tested

[ ] structured logging foundation implemented and tested

[ ] Ruff formatting passes

[ ] Ruff linting passes

[ ] Pyright passes

[ ] pytest passes

[ ] package build passes

[ ] GitHub Actions CI passes from repository

[ ] runtime dependencies remain minimal

[ ] no Relay domain behavior exists

[ ] no GitHub integration exists

[ ] no provider integration exists

[ ] no persistence layer exists

[ ] no web/API framework exists

[ ] documentation baseline exists

[ ] ADR-0001 exists

[ ] CURRENT_BASELINE.md reflects actual accepted state

[ ] Slice 0.1 memory is complete

[ ] resulting accepted SHA recorded
```

---

# 50. Resulting Authority

After acceptance, Slice 0.1 establishes authority only for:

```text
runtime
tooling
repository conventions
configuration foundation
logging foundation
quality checks
documentation structure
```

It establishes **no product-domain authority**.

The current product capability remains:

```text
Relay engineering foundation only.
```

---

# 51. Known Limitations After Acceptance

Expected limitations are intentional:

- no Relay domain model;
- no state machine;
- no persistence;
- no GitHub access;
- no `.relay/` contract;
- no UI;
- no agents;
- no external providers;
- no sandbox;
- no research;
- no experiments.

These are not bugs.

They define the boundary of Slice 0.1.

---

# 52. Hard Stop

After Slice 0.1 acceptance:

```text
HARD STOP
```

Relay must **not automatically begin Slice 0.2**.

The resulting baseline should be reviewed for:

- unnecessary complexity;
- tooling burden;
- portability;
- dependency surface;
- documentation quality;
- appropriateness as a long-lived foundation.

Only after explicit human authorization may Slice 0.2 begin.

---

# 53. Candidate Slice 0.2

The next work package is expected to be:

> **Slice 0.2 — Core Domain Model**

But its contract is not authorized by this document.

Slice 0.1 does not pre-decide the detailed representation of:

```text
Project
Slice
Artifact
Decision
Evidence
Baseline
Authorization
HandoverGate
Evaluation
Research
Experiment
```

Those decisions belong to the next design review.

---

# 54. Proposed Slice 0.1 Summary

The intended result is intentionally modest:

```text
private repository
      +
Python 3.14
      +
uv
      +
typed package
      +
settings
      +
structured logging
      +
tests
      +
Ruff
      +
Pyright
      +
CI
      +
engineering documentation
      +
explicit accepted baseline
```

Nothing more.

The value of Slice 0.1 is that every later Relay capability can be built from an environment whose engineering rules are already explicit and mechanically checked.
