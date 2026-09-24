# Relay — Current Baseline

**Status:** Slice 0.4 accepted baseline; hard stop active
**Document class:** Living canonical projection
**Canonical key:** `current-baseline`
**Date:** September 2026

---

# 1. Accepted Project Baseline

```text
Accepted Slice: 0.4 — Handover Gates and Traffic Lights
Accepted Slice 0.4 design: Revision 2
Accepted design SHA: 09e2fc2fb5e38687d20c8db8050a4a7e5d2a37bd
Accepted technical implementation SHA: babd0980ed00a8ef686f510075e2848fd84831b5
Ratified original candidate: d740b1712951fdb7543c459541a7c446b407d07e
Accepted Slice 0.4 result: 493571dc13cb5f4afb27367f5f7e1528b0448041
Independent evaluation: RLY-S04-EVAL-002 — ACCEPT
Human acceptance: RLY-S04-ACCEPT-001
Repository branch: main
Visibility: public — human-authorized deviation
```

The accepted Slice 0.4 result SHA identifies the evaluated candidate. This finalization commit is an acceptance record and does not replace the accepted result SHA.

Earlier accepted results remain:

```text
Slice 0.1 implementation SHA: e8598ae5ffb046d4131e04655a0c063ff1e41ccc
Slice 0.2 implementation SHA: cdf5b1fedc92762095f38d684d4655aaa6bf57f0
Slice 0.3 implementation SHA: 7a8d2ad37ef6816335175ca0ccdc37e9c1b13612
Slice 0.3 technical implementation commit: 26e6c300f6b266f811e09084402fe2182d693f0f
Pre-Slice-0.3 accepted repository baseline: cf4a2f5195bdb6e97dfece2a2e608e9c5adf9cbd
```

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

The accepted project includes the Slice 0.1 engineering foundation, Slice 0.2 core domain model, Slice 0.3 deterministic lifecycle state machine, and Slice 0.4 handover governance.

Slice 0.2 vocabulary:

```text
ActorRef, RepositoryRef, CommitRef, Project, Baseline, Slice,
ScopeSpec, AcceptanceCriterion, Artifact, Decision, Evidence
```

Slice 0.3 adds deterministic lifecycle values, immutable lifecycle events, typed lifecycle errors, explicit transitions, and strict event replay. Lifecycle state remains separate from `Slice`.

Slice 0.4 adds:

```text
deterministic handover gates
RED / YELLOW / GREEN traffic-light evaluation
validity / authority / autonomy separation
durable AuthorizationGrant
execution-time HumanApprovalDecision
set-bound HumanChoiceDecision
governance_revision decision-basis freshness
hard-stop governance
artifact/evidence/dependency prerequisites
evaluation-outcome routing
quality evidence
change-surface review
risk review
toolchain-change blocking
canonical reason/result ordering
unique executable-path enforcement
eventless lifecycle transition validation
governed lifecycle execution with authority-causality checks
```

Gate evaluation is deterministic and consumes explicit facts. Governed execution reevaluates current context before delegating to the lifecycle transition operation.

# 4. Accepted Slice 0.3 Records

```text
Accepted design: docs/slices/SLICE_0_3_STATE_MACHINE_AND_LIFECYCLE.md — Revision 4
Accepted development memory: docs/slices/SLICE_0_3_STATE_MACHINE_MEMORY.md — LOCKED
Accepted memory amendment: docs/slices/SLICE_0_3_STATE_MACHINE_MEMORY_AMENDMENT_001.md — LOCKED / ACCEPTED CORRECTION
Accepted decision: docs/decisions/ADR-0003-lifecycle-state-decomposition.md — LOCKED / ACCEPTED
Architecture: docs/architecture/LIFECYCLE_STATE_MACHINE.md
```

The acceptance-record commit is `cad415cebdd0972d429567558d79a8c1f31514d4`. The amendment clarifies the exact Human Authority instruction and is read together with the locked memory.

# 5. Accepted Slice 0.4 Records and Process Exception

```text
Accepted design: docs/slices/SLICE_0_4_HANDOVER_GATES_AND_TRAFFIC_LIGHTS.md — Revision 2
Accepted development memory: docs/slices/SLICE_0_4_HANDOVER_GATES_MEMORY.md — LOCKED / ACCEPTED
Accepted decision: docs/decisions/ADR-0004-handover-governance-separation.md — LOCKED / ACCEPTED
Architecture: docs/architecture/HANDOVER_GOVERNANCE.md
Human ratification: RLY-S04-RATIFY-001
```

Implementation began before explicit pre-execution authorization. Human Authority ratified that one-time deviation through `RLY-S04-RATIFY-001` after independent technical evaluation. The ratification records the actual sequence; it does not claim prior authorization existed or rewrite history.

The accepted Slice 0.4 result is `493571dc13cb5f4afb27367f5f7e1528b0448041`; its technical implementation is `babd0980ed00a8ef686f510075e2848fd84831b5`. The finalization commit is separate acceptance provenance and does not replace either SHA.

# 6. Deferred Capability

Relay does not yet provide:

```text
persistent governance history
database/event store
GitHub product integration
artifact registry/discovery
agent execution
AgentRole / AgentAssignment
handover packet construction
notifications
UI / board
REST/API
RBAC / identity
risk scoring
quality-command execution
provider/model integration
```

Artifact-governance registry semantics remain deferred to Slice 0.6.

# 7. Next Slice and Hard Stop

```text
Slice 0.4: COMPLETE / ACCEPTED
Next slice: Slice 0.5 NOT AUTHORIZED
Hard stop: ACTIVE
```

Do not begin Slice 0.5 design or implementation without new explicit Human Authority authorization. The presence of future design documents does not grant authority.
