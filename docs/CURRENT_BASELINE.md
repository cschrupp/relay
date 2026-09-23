# Relay — Current Baseline

**Status:** SLICE 0.1 — COMPLETE / ACCEPTED
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

The Slice 0.1 development memory and ADR-0001 are locked accepted records. Slice 0.2 design documentation is present, but its presence does not authorize implementation. Slice 0.3 remains a design record and is not implemented product behavior.

---

# 5. Next Slice and Hard Stop

```text
Next slice: NOT AUTHORIZED
Hard stop: ACTIVE
```

No Slice 0.2 or later implementation may begin without new explicit authorization from the human authority.
