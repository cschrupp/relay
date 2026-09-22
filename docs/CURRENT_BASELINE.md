# Relay — Current Baseline

**Status:** STARTER HANDOFF — NOT YET AN ACCEPTED GIT BASELINE  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Purpose

This document answers:

> What is authoritative now?

This starter has not yet been committed into the user's Relay repository, so there is no authoritative Git baseline SHA yet.

The first Codex/repository action should be to inspect the starter, run the quality checks in a Python 3.14 environment, commit the foundation, and record the resulting SHA before beginning any later implementation slice.

---

# 2. Engineering Foundation

```text
Runtime:             Python 3.14
Dependency manager: uv
Distribution:        relay-engine
Import package:      relay_engine
Build backend:       hatchling
Configuration:       pydantic-settings
Structured logging: structlog
Formatter/linter:    Ruff
Type checker:        Pyright
Test runner:         pytest
CI:                  GitHub Actions
```

---

# 3. Current Implemented Capability

Implemented:

```text
package/version foundation
operational settings
structured logging
unit-test harness
format/lint/type/test/build quality profile
CI
engineering documentation
Codex agent instructions
```

Not implemented:

```text
Relay core domain objects
lifecycle/state machine
handover gates / traffic lights
authorization
persistence / event store
.relay repository schema
GitHub App integration
model providers
agent roles/execution
research
experiments
board/UI
billing/organizations
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

Slice 0.2 is an accepted design record and must not be silently rewritten.

Slice 0.3 is currently a review-stage design record, not implemented product behavior.

---

# 5. Current Implementation Boundary

The starter intentionally stops at the Slice 0.1 engineering foundation.

Future slice documents are present so Codex can understand the intended architecture and continue when explicitly authorized.

Their presence does not authorize implementation.

---

# 6. Required First Repository Baseline Action

After importing this starter into Git:

1. create/confirm the repository;
2. run the canonical quality checks under Python 3.14;
3. resolve any foundation-only issues without entering Slice 0.2 semantics;
4. commit the starter;
5. record the exact resulting SHA here;
6. only then authorize the next implementation slice.

Until that occurs:

```text
Accepted SHA: NONE — starter is uncommitted handoff material
```
