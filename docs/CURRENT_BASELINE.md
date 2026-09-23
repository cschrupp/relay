# Relay — Current Baseline

**Status:** SLICE 0.2 — COMPLETE / ACCEPTED
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted Baseline

```text
Accepted Slice: 0.2 — Core Domain Model
Accepted implementation SHA: cdf5b1fedc92762095f38d684d4655aaa6bf57f0
Independent evaluation: RLY-S02-EVAL-001 — ACCEPT
Human acceptance: RLY-S02-ACCEPT-001
Accepted repository baseline: main contains accepted Slice 0.2
```

The accepted Slice 0.2 technical implementation SHA is distinct from the later acceptance-record commit. Promotion to `main` was a fast-forward from the accepted Slice 0.1 governance baseline; the technical commit was not recreated or changed.

The project includes these domain values:

```text
ActorRef, RepositoryRef, CommitRef, Project, Baseline, Slice,
ScopeSpec, AcceptanceCriterion, Artifact, Decision, Evidence
```

Boundaries remain explicit:

```text
Slice contains no lifecycle state.
No authorization model exists yet.
No handover-gate model exists yet.
No persistence layer exists.
No GitHub product adapter exists.
No AI/model provider exists.
No execution subsystem exists.
No canonical artifact registry exists.
Artifact-governance registry semantics remain deferred to Slice 0.6.
```

```text
Prior accepted Slice: 0.1
Accepted implementation SHA: e8598ae5ffb046d4131e04655a0c063ff1e41ccc
Evaluation: RLY-S01-EVAL-002 — ACCEPT
Human acceptance: RLY-S01-ACCEPT-001
Repository: cschrupp/relay
Visibility: public — human-authorized deviation
```

The accepted implementation SHA identifies the Slice 0.1 technical result. The later acceptance-record commit records governance metadata and does not replace or redefine that implementation SHA. Its SHA is available in Git history and the implementation handover.

---

# 2. Engineering Foundation

```text
Runtime:             Python 3.14
Dependency manager: uv
Distribution:        relay-engine
Import package:      relay_engine
Build backend:       hatchling
Configuration:       Pydantic settings
Structured logging: structlog
Formatter/linter:    Ruff
Type checker:        Pyright
Test runner:         pytest
CI:                  GitHub Actions
```

---

# 3. Current Capability

```text
Relay engineering foundation and core domain model
```

This includes the Slice 0.1 Python package and version foundation, operational settings, structured logging, unit-test harness, quality checks, build configuration, CI, and engineering documentation, plus the Slice 0.2 provider-neutral immutable domain values.

The following are intentionally absent:

```text
no lifecycle engine
no handover gates
no persistence
no .relay schema
no provider integration
no agent execution
no UI
```

---

# 4. Documentation Authority

Current living canonical documents:

```text
PRODUCT_PROPOSAL.md
BUILD_PLAN.md
CURRENT_BASELINE.md
policies/DOCUMENTATION_GOVERNANCE.md
policies/ENGINEERING_SIMPLICITY_SCOPE_AND_QUALITY.md
```

Slice 0.1 locked records:

```text
docs/slices/SLICE_0_1_REPOSITORY_FOUNDATION_MEMORY.md
docs/slices/SLICE_0_1_REPOSITORY_FOUNDATION_MEMORY_AMENDMENT_001.md
docs/decisions/ADR-0001-runtime-and-tooling-baseline.md
```

The amendment is to be understood together with the original locked memory. It corrects only the stated decision range and does not change the accepted implementation SHA.

Slice 0.2 design documentation was implemented under its explicit authorization and is now accepted. Slice 0.3 remains a design record; its presence does not authorize implementation and it is not implemented product behavior.

Slice 0.2 locked records:

```text
docs/slices/SLICE_0_2_CORE_DOMAIN_MODEL_MEMORY.md
docs/decisions/ADR-0002-core-domain-boundaries.md
```

---

# 5. Accepted Slice 0.2 Implementation

```text
Accepted slice: 0.2 — Core Domain Model
Accepted technical SHA: cdf5b1fedc92762095f38d684d4655aaa6bf57f0
Candidate branch: slice/0.2-core-domain-model (preserved as historical evidence)
Status: COMPLETE / ACCEPTED
Authorized baseline: 8d24039f982139ea76c9651abfc8c06b6ed58bb3
```

The accepted technical commit is now on `main`. The acceptance-record commit is separate provenance and does not replace the accepted implementation SHA.

# 6. Next Slice and Hard Stop

```text
Next implementation slice: NOT AUTHORIZED
Slice 0.3: DESIGN PRESENT / IMPLEMENTATION NOT AUTHORIZED
Hard stop: ACTIVE
```

Acceptance of Slice 0.2 does not authorize Slice 0.3 or later implementation. No further development is authorized until a new human authorization is received.
