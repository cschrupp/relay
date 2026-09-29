# Relay — Build Plan and Development Roadmap

**Version:** 0.5  
**Status:** Current living implementation plan — Phase 1 / Slice 1.3 accepted, closure evaluation pending  
**Document class:** Living canonical projection  
**Canonical key:** `build-plan`  
**Supersedes:** v0.4 at `docs/BUILD_PLAN_V0_4.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** September 2026

---

# 1. Purpose

This is the current execution plan after Human technical acceptance and bounded finalization of Slice 1.3.

Relay continues to be built inside-out:

```text
deterministic domain contracts
        ↓
lifecycle / governance
        ↓
persistence / auditability
        ↓
repository contract
        ↓
provider repository integration
        ↓
human workflow
        ↓
agent execution
        ↓
multi-agent orchestration
```

The governance model remains the product. Historical Build Plans remain context only where they do not conflict with accepted records, the current registry, or later Human Authority decisions.

---

# 2. Current project state

```text
Phase 0:
COMPLETE / CLOSED

Slices 0.1–0.6:
CLOSED / ACCEPTED

Phase 1:
OPEN

Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
COMPLETE / ACCEPTED
CLOSURE EVALUATION PENDING

Slice 1.4:
NOT OPEN
```

Slice 1.3 authority chain:

```text
RLY-S13-OPEN-001
RLY-S13-DESIGN-AUTH-001
RLY-S13-DESIGN-EVAL-001 — REVISE
RLY-S13-DESIGN-EVAL-002 — REVISE
RLY-S13-DESIGN-EVAL-003 — REVISE
RLY-S13-DESIGN-EVAL-004 — ACCEPT
RLY-S13-DESIGN-ACCEPT-001
RLY-S13-AUTH-001
RLY-S13-EVAL-001 — REWORK
RLY-S13-EVAL-002 — ACCEPT
RLY-S13-ACCEPT-001
```

Exact accepted Slice 1.3 technical result:

```text
9b5166d1e95aefeb177d30c29f943f45a591ea05
```

Acceptance/finalization head:

```text
5164f1a8532e1ca05007531cdfd1f5084755092a
```

Promoted-main CI:

```text
36612444758 — SUCCESS
```

---

# 3. Process rules in force

## P0-PR-01 — Registered living-projection preflight

Any authorized change surface modifying a registered living projection includes the corresponding `.relay/registry.json` advancement in the same governed change.

## P0-PR-02 — Role/model visibility

Substantive handovers distinguish role/model assignment from actual execution provenance.

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

## P0-PR-03 — Design-review outcome vocabulary

```text
ACCEPT
REVISE
ESCALATE
```

## P0-PR-04 — Transition discipline

Review acceptance, Human acceptance, closure, and next-slice opening are distinct governed transitions.

**Unblocked ≠ authorized.**

---

# 4. Repository and documentation governance

The accepted schema-v1 repository contract remains:

```text
.relay/
└── registry.json
```

Canonical status is a registry relationship, not a filename.

Registered living projections advance through:

```text
changed current projection
→ new ArtifactId
→ revision N + 1
→ exact content digest
→ canonical pointer advances
```

Historical locked/immutable records remain immutable.

---

# 5. Phase 1 — GitHub and human-controlled project workflow

## Slice 1.1 — GitHub App Integration

```text
COMPLETE / ACCEPTED / CLOSED
```

## Slice 1.2 — Repository Registration and Baseline Resolution

```text
COMPLETE / ACCEPTED / CLOSED
```

## Slice 1.3 — `.relay/` Initialization and Sync

```text
COMPLETE / ACCEPTED
CLOSURE EVALUATION PENDING
```

Accepted capability includes:

- schema-v1 repository-contract preservation;
- deterministic `RepositorySyncSubjectV1`;
- read-only preparation;
- exact HUMAN repository-mutation authorization;
- deterministic SQLite migration v3;
- separate READ/WRITE token scopes;
- one Git tree, one exact-parent commit, one non-force default-branch ref movement;
- fail-closed local/provider/head race guards;
- unregistered-path adoption-or-conflict;
- workflow-path mutation prohibition under the current permission ceiling;
- no empty-repository bootstrap;
- observation-based reconciliation for indeterminate ref updates;
- exact visible registry/artifact verification;
- target-state idempotency;
- no automatic Baseline persistence.

Accepted design head:

```text
0ba9d3ded4b068c61ca7095b02c751daf0a98fc9
```

Accepted technical result:

```text
9b5166d1e95aefeb177d30c29f943f45a591ea05
```

## Slice 1.4 — Project and Slice CRUD

```text
NOT OPEN
```

## Slice 1.5 — Board Projection

```text
NOT OPEN
```

## Slice 1.6 — Human Authorization and Decision Gates

```text
NOT OPEN
```

## Slice 1.7 — Manual Evaluation and Acceptance

```text
NOT OPEN
```

---

# 6. Slice 1.3 closure gate

```text
Technical acceptance:
RLY-S13-ACCEPT-001 — DONE

Acceptance/finalization:
5164f1a8532e1ca05007531cdfd1f5084755092a — DONE

Promoted-main CI:
36612444758 — SUCCESS

Independent closure evaluation:
PENDING
```

No Slice 1.4 work is valid until Slice 1.3 closure is independently accepted.

---

# 7. Phase-1 hard stop — M0 validation

Phase 1 ends only after Relay can govern a real human-controlled project workflow.

Required dogfood questions remain:

- Does the board clarify real project state?
- Are deterministic traffic lights useful?
- Does READY versus AUTHORIZED matter in practice?
- Does durable memory reduce repeated context explanation?
- Are gates useful rather than bureaucratic?
- Can a fresh reviewer reconstruct why an accepted baseline exists?

---

# 8. Current authorization boundary

```text
Phase 1:
OPEN

Slice 1.1:
CLOSED / ACCEPTED

Slice 1.2:
CLOSED / ACCEPTED

Slice 1.3:
COMPLETE / ACCEPTED
CLOSURE EVALUATION PENDING

Slice 1.4:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**
