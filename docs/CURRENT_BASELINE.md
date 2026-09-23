# Relay — Current Baseline

**Status:** SLICE 0.2 CANDIDATE — PENDING INDEPENDENT EVALUATION
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted Baseline

```text
Accepted Slice: 0.1
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
Relay engineering foundation only
```

This includes the Python package and version foundation, operational settings, structured logging, unit-test harness, quality checks, build configuration, CI, and engineering documentation.

The following are intentionally absent:

```text
no core domain model
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

Slice 0.2 design documentation is present, but its presence does not authorize implementation. Slice 0.3 remains a design record and is not implemented product behavior.

---

# 5. Candidate Implementation

```text
Candidate slice: 0.2 — Core Domain Model
Candidate branch: slice/0.2-core-domain-model
Candidate status: IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION
Authorized baseline: 8d24039f982139ea76c9651abfc8c06b6ed58bb3
```

The candidate branch is being implemented against the accepted Slice 0.1 project baseline. It does not replace the accepted implementation SHA or the accepted project state on `main`. Slice 0.2 remains pending independent evaluation and human acceptance.

# 6. Next Slice and Hard Stop

```text
Next slice after 0.2: NOT AUTHORIZED
Slice 0.3: NOT AUTHORIZED
Hard stop: ACTIVE after Slice 0.2 submission
```

The authorization for Slice 0.2 does not authorize Slice 0.3 or later implementation. Do not merge the candidate branch before independent evaluation and explicit human acceptance.
