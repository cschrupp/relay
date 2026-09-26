# Relay — Current Baseline

**Status:** Slice 0.5 accepted baseline
**Document class:** Living canonical projection
**Canonical key:** `current-baseline`
**Date:** September 2026

---

# 1. Accepted Project Baseline

```text
Accepted Slice: 0.5 — Event and Persistence Model
Accepted design: Slice 0.5 Design Revision 2
Accepted design SHA: 2d2822644209e1002e77c39ab8f06757c583103b
Accepted implementation result: d3ee53a572483e0bd96dbac2554bfad24c06136a
Independent evaluation: RLY-S05-EVAL-002 — ACCEPT
Human acceptance: RLY-S05-ACCEPT-001
Repository branch: main
Visibility: public — human-authorized deviation
```

The acceptance-record commit is separate provenance and does not replace the accepted Slice 0.5 result SHA.

Slice 0.5 lineage:

```text
Accepted Slice: 0.5 — Event and Persistence Model
Accepted design: Slice 0.5 Design Revision 2
Accepted design SHA: 2d2822644209e1002e77c39ab8f06757c583103b
Initial implementation candidate: 32f92b154d380a77188db36d9ea00c874748664a
Independent evaluation: RLY-S05-EVAL-001 — REWORK
Bounded migration rework: 5e387a9d3f123b6333f9b700b22a8f9846a51f0b
Accepted Slice 0.5 result: d3ee53a572483e0bd96dbac2554bfad24c06136a
Independent reevaluation: RLY-S05-EVAL-002 — ACCEPT
Human acceptance: RLY-S05-ACCEPT-001
```

The initial evaluation returned REWORK and required technical corrections. Bounded rework under `RLY-S05-EVAL-001` completed successfully, and independent reevaluation `RLY-S05-EVAL-002` returned ACCEPT. The acceptance-record commit is separate provenance and does not replace the accepted Slice 0.5 result SHA.

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

Slice 0.5 adds:

```text
SQLite Phase-0 persistence
typed canonical JSON payload persistence
insert-only stable domain identities
immutable lifecycle event history
materialized current lifecycle projection
event→snapshot replay verification
ABSENT→revision-0 lifecycle initialization
expected-revision optimistic concurrency
explicit migration versioning/checksums
contiguous applied migration history
atomic pending migration batches
post-migration physical-schema verification
durable gate revisions
durable authorization grants
durable human decisions
GateEvaluationRecord audit evidence
ExecutionRecord causal linkage
persisted governed handover execution
restart recovery and integrity verification
```

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
GitHub product integration
artifact registry/discovery
canonical artifact discovery
canonical gate-set discovery
repository synchronization
`.relay/` repository contract
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
authorization expiry/revocation
cloud database
backup/replication product
full event sourcing
```

The future UI requirement remains tracked separately in GitHub Issue #1: “Future UI: governance handover cards and structured human decision controls.” It was not implemented in Slice 0.5. Artifact-governance registry semantics remain deferred to Slice 0.6.

# 7. Next Slice and Hard Stop

```text
Slice 0.4: COMPLETE / ACCEPTED
Slice 0.5: COMPLETE / ACCEPTED
Accepted project baseline: Slice 0.5
Accepted project baseline before Slice 0.5: c8006306d48624f13599fe448ef677015fd1829e
Accepted Slice 0.5 design: Revision 2, 2d2822644209e1002e77c39ab8f06757c583103b
Initial implementation candidate: 32f92b154d380a77188db36d9ea00c874748664a
Independent evaluation: RLY-S05-EVAL-001 — REWORK
Bounded migration rework: 5e387a9d3f123b6333f9b700b22a8f9846a51f0b
Accepted Slice 0.5 result: d3ee53a572483e0bd96dbac2554bfad24c06136a
Independent reevaluation: RLY-S05-EVAL-002 — ACCEPT
Human acceptance: RLY-S05-ACCEPT-001
Slice 0.5 memory: LOCKED / ACCEPTED
ADR-0005: LOCKED / ACCEPTED
Slice 0.6: IMPLEMENTATION AUTHORIZED / CANDIDATE PENDING EVALUATION
Authorization: RLY-S06-AUTH-001
Accepted Slice 0.6 design: Revision 4, adc3164c41b847543181e106c37c0dbad82c7c6a
Phase 1 / Slice 1.1: NOT AUTHORIZED
Hard stop after Slice 0.6 acceptance: ACTIVE
```

The initial Slice 0.5 submission received REWORK before the bounded technical corrections and later acceptance. Slice 0.5 remains the accepted project baseline until the Slice 0.6 candidate is independently evaluated and accepted. The Slice 0.6 authorization is limited to its accepted repository-contract design; it does not authorize Phase 1 / Slice 1.1.

# 8. Slice 0.6 Candidate Projection

```text
Slice: 0.6 — .relay/ Repository Contract
Accepted project baseline: Slice 0.5
Accepted design: Revision 4, adc3164c41b847543181e106c37c0dbad82c7c6a
Implementation authorization: RLY-S06-AUTH-001
Candidate branch: slice/0.6-repository-contract
Candidate status: IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION
Phase 1 / Slice 1.1: NOT AUTHORIZED
```

The implementation-result SHA is reported in the handover and is not embedded in the same commit. Slice 0.6 remains a candidate; no acceptance is claimed here.
