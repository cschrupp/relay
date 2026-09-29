# Relay — Current Baseline

**Status:** Phase 1 open — Slice 1.3 implementation authorized  
**Document class:** Living canonical projection  
**Canonical key:** `current-baseline`  
**Date:** September 2026

---

# 1. Accepted foundation

Phase 0 is complete and closed.

Slice 1.1 is complete, accepted, and closed.

```text
Accepted Slice 1.1 technical implementation:
ae79b15170c88e776af99944eab9b2fdd6872c2e

Slice 1.1 acceptance-record/finalization:
ccfbfb964064e92aef4e21e11f0ad01290acb16f

Slice 1.1 closure evaluation:
RLY-S11-CLOSE-EVAL-001 — ACCEPT
```

Slice 1.2 is complete, accepted, and closed.

```text
Accepted Slice 1.2 design head:
4acd6be1f93058d1efcafc66a78fc1a9726c16ba

Accepted Slice 1.2 technical result:
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d

Independent implementation evaluation:
RLY-S12-EVAL-002 — ACCEPT

Human acceptance:
RLY-S12-ACCEPT-001

Acceptance-record/finalization:
7e08ad484ce794946ec2e09abf44060879e9fc04

Final canonical head evaluated:
3cbac05d8aa91b09ce79965a83d9887b76c23978

Closure evaluation:
RLY-S12-CLOSE-EVAL-001 — ACCEPT
```

Slice 1.3 is open. Its combined architecture / contract / design has been independently reviewed and accepted by Human Authority, and implementation is explicitly authorized.

```text
Opening:
RLY-S13-OPEN-001

Design authorization:
RLY-S13-DESIGN-AUTH-001

Independent combined design evaluation:
RLY-S13-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S13-DESIGN-ACCEPT-001

Exact accepted design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9

Implementation authorization:
RLY-S13-AUTH-001
```

---

# 2. Protocol rules in force

```text
P0-PR-01  registered living-projection impact preflight
P0-PR-02  visible role/model assignment and execution provenance
P0-PR-03  design review uses ACCEPT / REVISE / ESCALATE
P0-PR-04  review acceptance and next-phase authorization are separate
```

Working model-role convention:

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

If preferred and executing models differ, both are recorded.

---

# 3. Slice 1.2 accepted authority

Authority chain:

```text
RLY-S12-OPEN-001
RLY-S12-DESIGN-AUTH-001
RLY-S12-DESIGN-EVAL-003 — ACCEPT
RLY-S12-DESIGN-ACCEPT-001
RLY-S12-AUTH-001
RLY-S12-EVAL-001 — REWORK
RLY-S12-EVAL-002 — ACCEPT
RLY-S12-ACCEPT-001
RLY-S12-CLOSE-EVAL-001 — ACCEPT
```

The exact accepted implementation is `9ed4a8da4d989fd41674ae59ef68ba4238c09b5d`.

Accepted behavior includes repository authority, commit/tree/blob proof, exact `.relay/registry.json` validation, provider/local race guards, stable Artifact provenance, and atomic local Artifact/Baseline persistence.

---

# 4. Slice 1.3 accepted design and implementation authority

Exact authorized design baseline:

```text
eb6b3797fb1b317e9158444b9c9dbe469b2ee313
```

Accepted reviewed design sequence:

```text
Revision 1:
433910d0b2df7f0f0a3104cbe97f6df5ebba609a

Revision 2:
6070b04ca5b38bd5c4687bb0ec4799f4f782e355

Revision 3:
8e8ab70cf8c9b52d628b0b658179c1fe287c93ea

Revision 4 / exact accepted design head:
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
```

Implementation authority:

```text
RLY-S13-AUTH-001
Slice 1.3 implementation:
AUTHORIZED
```

The accepted design specifies the minimum safe mechanism for recognizing, initializing, or synchronizing the accepted repository contract through GitHub while preserving authority, provenance, race safety, and fail-closed behavior.

Accepted design highlights include:

- schema-v1 `.relay/registry.json` remains unchanged;
- exact `RepositorySyncSubjectV1`;
- read-only preparation before Human Authority approval;
- project + exact-subject scoped `RepositoryMutationAuthorization`;
- deterministic SQLite migration v3 for immutable mutation authority;
- GitHub Git Data single-tree / single-commit / non-force default-branch ref movement;
- provider, local-state, branch-head, path, permission, and post-write verification guards;
- no automatic Baseline persistence;
- no PR flow, force push, background worker, or agent execution.

All independent design-review findings F001–F008 are closed.

Implementation is authorized against the accepted design only. Material design deviation requires escalation rather than silent redesign.

---

# 5. Current canonical living documents

Registry-current projections are:

```text
Product Proposal v0.5
Build Plan v0.5
Current Baseline
Documentation Governance v0.3
Engineering Simplicity, Scope, and Quality
```

Canonicality remains a `.relay/registry.json` relationship.

---

# 6. Authorization state

```text
Phase 1:
OPEN

Slice 1.1:
CLOSED / ACCEPTED

Slice 1.2:
CLOSED / ACCEPTED

Slice 1.3:
OPEN

Slice 1.3 architecture / contract / design:
ACCEPTED

Slice 1.3 implementation:
AUTHORIZED

Preferred implementation role/model:
IMPLEMENTATION_AGENT — GPT-5.6 Luna

Slice 1.4:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

Next governed gate: bounded Slice 1.3 implementation result returned to an independent evaluator.

**Authorized ≠ accepted.**
