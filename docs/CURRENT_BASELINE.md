# Relay — Current Baseline

**Status:** STARTER HANDOFF — NOT YET AN ACCEPTED GIT BASELINE  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Purpose

This document answers:

> What is authoritative now?

The starter has been extracted, locked, validated under Python 3.14, and published to the user's public GitHub repository on `main`. The exact validated foundation commit is recorded in Section 7 and is submitted for independent evaluation. No accepted Git baseline has been established yet.

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

# 6. Repository Bootstrap Status

The public GitHub repository is `https://github.com/cschrupp/relay.git`, with `main` as its default branch. Commit `493043c8185b23c37fb192897ae6b9b3a436bdba` seeded the empty repository with the supplied README. Commit `f1ca0379fb54c2d4c29c7000e4c43942062638db` contains the complete validated starter and generated lock file. The validated snapshot remains pending independent evaluation.

Until an independent evaluation and acceptance decision occur:

```text
Accepted SHA: NONE — no acceptance decision recorded
```

# 7. Validated Bootstrap Snapshot

The complete starter plus generated `uv.lock` was committed after the required
Python 3.14 quality checks passed:

```text
Validated bootstrap snapshot: f1ca0379fb54c2d4c29c7000e4c43942062638db
Status: published on main; submitted for independent evaluation; not accepted
```

This SHA identifies the validated starter snapshot before this provenance entry
was added. It is not an acceptance decision or authorization for a later slice.
