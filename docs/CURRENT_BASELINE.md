# Relay — Current Baseline

**Status:** Slice 0.3 accepted baseline; Slice 0.4 implementation candidate pending evaluation
**Document class:** Living canonical projection
**Canonical key:** `current-baseline`
**Date:** September 2026

---

# 1. Accepted Project Baseline

```text
Accepted Slice: 0.3 — State Machine and Lifecycle Semantics
Accepted implementation result SHA: 7a8d2ad37ef6816335175ca0ccdc37e9c1b13612
Accepted technical implementation commit: 26e6c300f6b266f811e09084402fe2182d693f0f
Accepted Design Revision 4 SHA: 6c49a90aa819d66db2a44d0b933e9c40ceb9e320
Independent evaluation: RLY-S03-EVAL-002 — ACCEPT
Human acceptance: RLY-S03-ACCEPT-001 — explicit instruction “proceed”
Repository branch: main
Visibility: public — human-authorized deviation
```

The accepted result SHA identifies the implementation candidate with the exact accepted Revision 4 design in its ancestry. The later acceptance-record commit is separate provenance and does not replace that result SHA.

Earlier accepted results remain:

```text
Slice 0.1 implementation SHA: e8598ae5ffb046d4131e04655a0c063ff1e41ccc
Slice 0.2 implementation SHA: cdf5b1fedc92762095f38d684d4655aaa6bf57f0
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

The accepted project includes the Slice 0.1 engineering foundation, Slice 0.2 core domain model, and Slice 0.3 deterministic lifecycle state machine.

Slice 0.2 vocabulary:

```text
ActorRef, RepositoryRef, CommitRef, Project, Baseline, Slice,
ScopeSpec, AcceptanceCriterion, Artifact, Decision, Evidence
```

Slice 0.3 adds:

```text
LifecyclePhase, LifecycleValidity, BlockageStatus, BlockReason,
Blockage, SliceLifecycle, immutable lifecycle events, typed lifecycle errors,
explicit deterministic transitions, strict event replay
```

Lifecycle state remains separate from `Slice`. The engine models structural lifecycle semantics only; it does not decide whether a transition is authorized.

The accepted project still has no authorization model, handover gates, traffic lights, hard-stop enforcement mechanism, persistence, `.relay/` schema or artifact registry, GitHub product integration, providers, agent execution, API, or UI. Artifact-governance registry semantics remain deferred to Slice 0.6.

# 4. Accepted Slice 0.3 Records

```text
Accepted design: docs/slices/SLICE_0_3_STATE_MACHINE_AND_LIFECYCLE.md — Revision 4
Accepted development memory: docs/slices/SLICE_0_3_STATE_MACHINE_MEMORY.md — LOCKED
Accepted memory amendment: docs/slices/SLICE_0_3_STATE_MACHINE_MEMORY_AMENDMENT_001.md — LOCKED / ACCEPTED CORRECTION
Accepted decision: docs/decisions/ADR-0003-lifecycle-state-decomposition.md — LOCKED / ACCEPTED
Architecture: docs/architecture/LIFECYCLE_STATE_MACHINE.md
```

The acceptance-record commit is `cad415cebdd0972d429567558d79a8c1f31514d4`. The amendment clarifies the exact Human Authority instruction and is read together with the locked memory.

# 5. Slice 0.4 Candidate and Authority

```text
Accepted Slice 0.4 design: Revision 2
Accepted design SHA: 09e2fc2fb5e38687d20c8db8050a4a7e5d2a37bd
Implementation authorization: RLY-S04-IMPLEMENT-SCOPE-001
Candidate branch: slice/0.4-handover-gates
Candidate status: IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION
Candidate result SHA: recorded in the implementation handover
```

The candidate is not yet an accepted project baseline. The accepted baseline remains Slice 0.3 on `main` at the accepted provenance commit below. Slice 0.4 is being implemented under explicit Human Authority authorization against the exact accepted Revision 2 design.

Slice 0.4 candidate records:

```text
Design: docs/slices/SLICE_0_4_HANDOVER_GATES_AND_TRAFFIC_LIGHTS.md — Revision 2
Architecture: docs/architecture/HANDOVER_GOVERNANCE.md — candidate
Development memory: docs/slices/SLICE_0_4_HANDOVER_GATES_MEMORY.md — pending evaluation, not locked
ADR-0004: docs/decisions/ADR-0004-handover-governance-separation.md — pending acceptance, not locked
```

The accepted Slice 0.3 capability statement above describes `main`; candidate governance code is not promoted or accepted by this living projection.

# 6. Next Slice and Hard Stop

```text
Slice 0.4: IMPLEMENTATION AUTHORIZED — candidate pending evaluation
Next implementation slice: Slice 0.5 NOT AUTHORIZED
Post-Slice-0.4 hard stop: ACTIVE after submission
```

Do not begin Slice 0.5 or later work without new explicit Human Authority authorization. The presence of future design documents does not grant implementation authority.
