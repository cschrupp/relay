# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.1 design active  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted technical baseline

Phase 0 is complete and closed.

Accepted Phase-0 acceptance-record SHA:

```text
6c1b3e1098cdc6c220868aea8a492c413d3cca35
```

Accepted Phase-0 protocol/document synchronization SHA:

```text
cb9edc453442dc639a523ef301e4a258d0394daa
```

Accepted Slice 0.6 implementation result:

```text
1903017dd7832dc21f0554be762bac1002891a89
```

Phase-0 closure evaluation:

```text
RLY-S06-CLOSE-EVAL-001 — ACCEPT
```

---

# 2. Phase-0 protocol review

Review:

```text
RLY-P0-PROTOCOL-REVIEW-001
ACCEPT WITH PROCESS AMENDMENTS
```

Human acceptance:

```text
RLY-P0-PROTOCOL-ACCEPT-001
```

Process amendments now in force:

```text
P0-PR-01  registered living-projection impact preflight
P0-PR-02  visible current/next role + model
P0-PR-03  design review uses ACCEPT / REVISE / ESCALATE
P0-PR-04  review acceptance and next-phase authorization are separate
```

Phase 0 remains:

```text
COMPLETE / CLOSED
```

---

# 3. Current phase authority

Human Authority has separately granted:

```text
RLY-P1-OPEN-001
Phase 1 — OPEN
```

and:

```text
RLY-S11-DESIGN-AUTH-001
Slice 1.1 — GitHub App Integration
DESIGN ONLY
```

Exact authorized design baseline:

```text
cb9edc453442dc639a523ef301e4a258d0394daa
```

Current engineering role/model:

```text
Slice 1.1 Architect — GPT-5.6 Sol
```

Next governed role/model after Design Revision 1:

```text
Independent Design Reviewer — GPT-5.6 Sol
```

---

# 4. Authorization state

```text
Phase 1:
OPEN

Slice 1.1:
DESIGN AUTHORIZED / IN PROGRESS

Slice 1.1 implementation:
NOT AUTHORIZED

Slice 1.2:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

A passing Slice 1.1 design review will not by itself authorize implementation.

Human Authority must accept the reviewed design and separately authorize implementation.

**Unblocked ≠ authorized.**

---

# 5. Accepted Phase-0 capability

Relay currently provides:

- immutable provider-neutral domain values;
- deterministic lifecycle transitions and replay;
- deterministic handover gates and traffic lights;
- validity / authority / autonomy separation;
- durable authorization and human-decision records;
- SQLite persistence, migrations, restart recovery, and causal audit records;
- schema-v1 repository artifact registry;
- explicit canonical pointers;
- historical artifact immutability/supersession;
- raw-byte digest and repository-path integrity;
- observation-commit provenance without snapshot-varying core `Artifact` construction.

---

# 6. Canonical living documents

Canonical status is defined by `.relay/registry.json`.

Current canonical keys:

```text
product-proposal
build-plan
current-baseline
documentation-governance
engineering-simplicity-quality
```

Registered living projections must advance through a new ArtifactId/revision when their exact bytes change.

---

# 7. Current Slice 1.1 objective

Slice 1.1 designs the GitHub App integration boundary needed to securely identify installations, discover permitted repositories, validate least-privilege read access, process installation lifecycle signals, persist non-secret provider state, and map selected GitHub repositories into explicit provider-neutral `RepositoryRef` values.

The slice does not yet:

- register authoritative project repository/baseline state;
- resolve branches/tags to immutable commit SHAs;
- initialize or synchronize `.relay/` through GitHub;
- mutate repository content;
- create branches/commits/PRs;
- execute coding agents.

Those capabilities remain separately gated.

---

# 8. Deferred next slices

```text
Slice 1.2
Repository Registration and Baseline Resolution

Slice 1.3
.relay Initialization and Sync

Slice 1.4
Project and Slice CRUD

Slice 1.5
Board Projection

Slice 1.6
Human Authorization and Decision Gates

Slice 1.7
Manual Evaluation and Acceptance
```

No later slice is authorized by roadmap presence.
