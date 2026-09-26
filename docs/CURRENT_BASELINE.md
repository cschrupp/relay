# Relay — Current Baseline

**Status:** Phase 0 complete — protocol review submitted  
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

Accepted Slice 0.6 implementation result:

```text
1903017dd7832dc21f0554be762bac1002891a89
```

Slice 0.6 closure evaluation:

```text
RLY-S06-CLOSE-EVAL-001 — ACCEPT
```

The current repository may include a later documentation/protocol-review synchronization commit. That commit is separate provenance and is not embedded into this same living projection to avoid self-reference.

---

# 2. Phase-0 state

```text
Slice 0.1: CLOSED / ACCEPTED
Slice 0.2: CLOSED / ACCEPTED
Slice 0.3: CLOSED / ACCEPTED
Slice 0.4: CLOSED / ACCEPTED
Slice 0.5: CLOSED / ACCEPTED
Slice 0.6: CLOSED / ACCEPTED

Phase 0:
COMPLETE / CLOSED
```

Accepted Phase-0 capability includes:

- Python 3.14 / uv engineering foundation;
- provider-neutral immutable domain values;
- deterministic lifecycle transitions and replay;
- deterministic handover gates and traffic lights;
- validity / authority / autonomy separation;
- durable authorization and human-decision records;
- SQLite persistence, migrations, restart recovery, and causal audit records;
- schema-v1 repository artifact registry;
- explicit canonical pointers;
- historical artifact immutability/supersession;
- raw-byte digest and path integrity;
- observation-commit provenance without snapshot-varying core `Artifact` construction.

---

# 3. Canonical living documents

Canonical status is defined by `.relay/registry.json`.

Current living projections include:

```text
product-proposal
build-plan
current-baseline
documentation-governance
engineering-simplicity-quality
```

The current registry revision is authoritative for the exact target path and revision of each key.

---

# 4. Phase-0 protocol review

Review record:

```text
docs/reviews/PHASE_0_PROTOCOL_REVIEW.md
```

Review ID:

```text
RLY-P0-PROTOCOL-REVIEW-001
```

Submitted reviewer outcome:

```text
ACCEPT WITH PROCESS AMENDMENTS
```

Required amendments:

```text
P0-PR-01 registered living-projection impact preflight
P0-PR-02 visible current/next role + model
P0-PR-03 explicit design-review outcome vocabulary
P0-PR-04 review acceptance and next-phase authorization remain separate
```

The review is submitted but still requires Human Authority acceptance.

---

# 5. Current hard stop

```text
PHASE-0 PROTOCOL REVIEW:
SUBMITTED / PENDING HUMAN ACCEPTANCE

PHASE 1:
NOT AUTHORIZED

SLICE 1.1:
NOT OPEN

HARD STOP:
ACTIVE
```

A pre-review request to proceed to Phase 1 does not satisfy the accepted rule requiring a fresh Human Authority decision after the review is available.

---

# 6. Deferred capability

Relay does not yet provide:

- GitHub App/product integration;
- repository registration or baseline/worktree proof;
- clone/fetch/pull/push product workflow;
- branch/commit/PR creation workflow;
- repository↔SQLite synchronization;
- stable registry-revision → core-Artifact commit binding;
- human-facing board;
- model/provider execution;
- agent workspaces;
- implementation/evaluation automation;
- research/experiment execution;
- multi-agent orchestration.

These remain later-phase capabilities.

---

# 7. Next legitimate decision

Human Authority may now review:

```text
RLY-P0-PROTOCOL-REVIEW-001
```

If accepted, Human Authority may separately authorize:

```text
Phase 1:
OPEN

Slice 1.1:
DESIGN ONLY
```

Slice 1.1 implementation would remain unauthorized until its design is independently reviewed and explicitly authorized.

**Unblocked ≠ authorized.**
