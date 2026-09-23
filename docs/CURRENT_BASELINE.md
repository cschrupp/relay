# Relay — Current Baseline

**Status:** SLICE 0.3 IMPLEMENTATION CANDIDATE — PENDING INDEPENDENT EVALUATION
**Document class:** Living canonical projection
**Canonical key:** `current-baseline`
**Date:** September 2026

---

# 1. Accepted Project Baseline

```text
Accepted Slice: 0.2 — Core Domain Model
Accepted implementation SHA: cdf5b1fedc92762095f38d684d4655aaa6bf57f0
Accepted repository baseline on main: cf4a2f5195bdb6e97dfece2a2e608e9c5adf9cbd
Independent evaluation: RLY-S02-EVAL-001 — ACCEPT
Human acceptance: RLY-S02-ACCEPT-001
Repository: cschrupp/relay
Visibility: public — human-authorized deviation
```

The accepted Slice 0.2 technical SHA remains distinct from the acceptance-record baseline commit. Slice 0.1 remains accepted at implementation SHA `e8598ae5ffb046d4131e04655a0c063ff1e41ccc`.

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

# 3. Accepted Capability

`main` contains the Slice 0.1 engineering foundation and accepted Slice 0.2 core domain model:

```text
ActorRef, RepositoryRef, CommitRef, Project, Baseline, Slice,
ScopeSpec, AcceptanceCriterion, Artifact, Decision, Evidence
```

In the accepted baseline, `Slice` has no lifecycle state. The lifecycle implementation below is a candidate on a separate branch until evaluation and acceptance.

The accepted baseline still has no authorization model, handover gates, persistence, `.relay/` schema, provider integration, agent execution, or UI.

# 4. Slice 0.3 Authority

Slice 0.3 Design Revision 4 is the governing design, at `6c49a90aa819d66db2a44d0b933e9c40ceb9e320`. Independent design review `RLY-S03-DESIGN-EVAL-002` returned ACCEPT. Human Authority accepted Revision 4 and revalidated `RLY-S03-AUTH-001` against it on 2026-09-23.

The design and authorization permit lifecycle implementation only. Slice 0.4 and later implementation remain unauthorized.

# 5. Slice 0.3 Candidate

```text
Candidate slice: 0.3 — State Machine and Lifecycle Semantics
Candidate branch: slice/0.3-lifecycle-state-machine
Authorized implementation baseline: cf4a2f5195bdb6e97dfece2a2e608e9c5adf9cbd
Governing design SHA: 6c49a90aa819d66db2a44d0b933e9c40ceb9e320
Candidate status: IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION
Candidate result SHA: Reported in the implementation handover and Git; not embedded in its own commit.
```

The candidate adds immutable lifecycle snapshots and events, the explicit structural transition engine, blocker and staleness operations, event replay, tests, and Slice 0.3 documentation. It introduces no authorization, handover gates, traffic lights, hard-stop behavior, artifact/dependency evaluation, persistence, integrations, agents, providers, API, or UI.

The candidate branch does not replace the accepted project baseline on `main` before acceptance.

# 6. Next Slice and Hard Stop

```text
Next implementation slice: NOT AUTHORIZED
Slice 0.4: DESIGN/IMPLEMENTATION AUTHORITY NOT GRANTED
Hard stop: ACTIVE after Slice 0.3 acceptance
```

After Slice 0.3 acceptance, stop. Do not begin Slice 0.4 or later work without new human authorization.
