# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.3 Design Revision 4 submitted  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** September 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

Its central thesis is:

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay is not primarily a coding agent and is not primarily a Kanban board.

It governs how engineering work is defined, authorized, handed over, implemented, evaluated, accepted, and remembered.

The board is a human-readable projection of governed state, not the source of truth.

---

# 2. Target users

Relay is designed first for professional developers, technical leads, scientists, and engineers working on long-lived, high-context software where correctness, architecture, evidence, and traceability matter.

The strongest early beachhead remains scientific and engineering software:

- scientific computing;
- industrial and energy software;
- simulation and numerical modeling;
- ML/AI infrastructure;
- optimization;
- robotics;
- technical platforms with substantial domain logic.

---

# 3. Core differentiation

Relay differentiates through engineering governance and continuity:

1. **Durable engineering memory** — accepted reasoning travels with the code.
2. **Explicit roles and authority** — architect, researcher, implementer, evaluator, and Human Authority are not interchangeable.
3. **Governed handovers** — readiness, authority, and autonomy are separate.
4. **Independent evaluation** — implementers do not certify their own substantive work.
5. **Exact baselines and provenance** — acceptance is tied to explicit repository state and evidence.
6. **Research and experiments as evidence** — uncertainty can branch into controlled investigation rather than guesswork.
7. **Human agency at strategic boundaries** — technically unblocked work does not automatically proceed.

---

# 4. Accepted technical foundation

Phase 0 is complete and closed.

Slice 1.1 and Slice 1.2 are complete, accepted, and closed.

Relay now has accepted implementations for:

```text
core domain contracts
deterministic lifecycle semantics
handover gates and traffic lights
authorization / human-decision persistence
event and materialized-state persistence
schema migrations and restart integrity
repository-side canonical artifact governance
read-only GitHub App installation/repository integration
project-scoped provider access readiness
signed webhook convergence and idempotency
verified GitHub commit/tree/blob repository snapshot proof
immutable repository baseline resolution and persistence
stable first-binding Artifact provenance
provider/local authority race guards
```

The accepted repository representation remains deliberately minimal:

```text
ordinary engineering documents at natural repository paths
+
.relay/registry.json
```

Runtime/cloud state and credentials remain separate from repository authority.

---

# 5. Provider and repository authority

Relay distinguishes:

```text
provider-observed repository/access state
repository-authoritative engineering artifacts
runtime/cloud operational state
derived UI/search/agent-context projections
```

Slice 1.1 established provider-specific GitHub read access without changing provider-neutral repository identity.

A confirmed GitHub repository is converted only into an explicit caller-supplied Relay `RepositoryRef`; the provider's numeric repository ID never silently becomes Relay identity.

Slice 1.2 established the accepted read-side authority boundary:

```text
Project.primary_repository
        ↓
captured ACTIVE / READY GitHub provider-access selection
        ↓
pre-snapshot provider identity proof
        ↓
branch / tag / full-SHA resolve-once selection
        ↓
canonical immutable commit
        ↓
exact commit/tree/registry/blob proof
        ↓
post-snapshot provider identity proof
        ↓
final local access-authority guard
        ↓
atomic Artifact + Baseline persistence
```

Provider evidence remains subordinate to accepted Relay authority. Relay does not claim an atomic transaction spanning GitHub and SQLite.

Slice 1.3 is now in independent combined design review preparation after Revision 1, Revision 2, and Revision 3 each received bounded `REVISE` outcomes and Revision 4 addressed the remaining F008 mutation-authority scope issue.

---

# 6. Product workflow

The governed workflow remains:

```text
problem / objective
      ↓
research when needed
      ↓
architecture / contract
      ↓
planning
      ↓
readiness evaluation
      ↓
explicit authorization
      ↓
implementation
      ↓
independent evaluation
      ↓
rework / escalation / acceptance
      ↓
accepted baseline
      ↓
durable engineering memory
```

Repository side-effect authority is distinct from lifecycle handover authority: approving one exact repository synchronization does not make a lifecycle gate GREEN, authorize implementation, or accept a resulting Baseline.

---

# 7. Model and provider philosophy

Relay project semantics do not depend on one model vendor.

Role authority belongs to Relay contracts, not model identity.

During dogfooding, preferred assignment and actual execution provenance are kept distinct when they differ.

Working convention:

```text
architecture / design / review / evaluation:
GPT-5.6 Sol

bounded implementation / rework / finalization:
GPT-5.6 Luna preferred
```

---

# 8. Current roadmap

```text
Phase 0:
COMPLETE / CLOSED

Phase 1:
OPEN

Slice 1.1:
GITHUB APP INTEGRATION — COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
REPOSITORY REGISTRATION AND BASELINE RESOLUTION — COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
.relay INITIALIZATION AND SYNC — OPEN

Slice 1.3 design:
AUTHORIZED / REVISION 4 SUBMITTED FOR INDEPENDENT COMBINED REVIEW

Slice 1.3 implementation:
NOT AUTHORIZED
```

Phase 1 builds a useful human-controlled repository workflow before autonomous coding-agent execution.

---

# 9. Slice 1.3 proposed product boundary

Opening authority:

```text
RLY-S13-OPEN-001
```

Design authority:

```text
RLY-S13-DESIGN-AUTH-001
```

Authorized design baseline:

```text
eb6b3797fb1b317e9158444b9c9dbe469b2ee313
```

Revision 1 design record:

```text
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC.md
```

Independent Revision 1 review:

```text
RLY-S13-DESIGN-EVAL-001 — REVISE
```

Revision 2 amendment:

```text
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV2_AMENDMENT.md
```

Independent combined Revision 1 + Revision 2 review:

```text
RLY-S13-DESIGN-EVAL-002 — REVISE
```

Revision 3 amendment:

```text
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV3_AMENDMENT.md
```

Independent combined Revision 1 + Revision 2 + Revision 3 review:

```text
RLY-S13-DESIGN-EVAL-003 — REVISE
```

Revision 4 amendment:

```text
docs/slices/SLICE_1_3_RELAY_INITIALIZATION_AND_SYNC_REV4_AMENDMENT.md
```

The combined proposed capability remains deliberately narrow:

> Given authoritative Relay project/repository identity, an exact expected default-branch/base commit, an exact target schema-v1 repository contract, and explicit Human Authority over the exact prepared mutation subject, Relay may recognize an already-current target or commit initialization/synchronization to the existing default branch as one atomic Git commit, subject to exact permission, identity, transition, race, path-preservation, and post-write verification guards.

The combined design preserves these product rules:

- `.relay/registry.json` remains repository-side authority;
- schema v1 remains unchanged;
- current repository identity remains `Project.primary_repository`;
- read-only installations remain valid for existing read workflows;
- write-capable installations may add only `contents:write` above metadata read;
- read operations continue using read-scoped tokens;
- a read-only preparation step computes the exact `RepositorySyncSubjectV1` and digest before any write token or Git object exists;
- any non-no-op mutation requires an immutable HUMAN `RepositoryMutationAuthorization` for that exact subject;
- mutation authority is intentionally not an `AuthorizationGrant`, `HandoverGate`, or `HumanGateDecision` and contains no fabricated `BaselineId`, `GateId`, or `SliceId`;
- mutation authority is scoped by `project_id` plus the exact synchronization subject, which already binds repository/provider selection, `state_revision`, expected default branch/base commit, target registry digest, and artifact-write digests;
- preparation and authorization APIs require no Slice context;
- execution re-runs preparation checks and recomputes the exact subject rather than trusting stale preparation state;
- mutation authority is checked before WRITE-token minting and again immediately before ref visibility;
- valid `UNINITIALIZED` repositories with an existing head can be authorized without inventing a repository Baseline or engineering Slice identity;
- existing lifecycle/handover governance remains unchanged and must still be satisfied independently wherever applicable;
- future optional Slice/audit provenance is a higher-level workflow concern and does not alter repository-mutation authority in Slice 1.3;
- repository mutation is one non-force default-branch ref movement;
- registry plus changed registered artifact bytes become visible in the same commit;
- concurrent branch movement causes conflict rather than overwrite/rebase;
- existing unregistered files are adopted only when their exact bytes/mode already satisfy the target; otherwise the operation conflicts;
- `.github/workflows/**` content/mode mutation is not attempted under the contents-only permission ceiling;
- empty repositories with no existing default-branch head are not bootstrapped by Slice 1.3;
- indeterminate ref-update transport outcomes are reconciled by observation and never by hidden write retry;
- existing registry transitions remain governed by the accepted transition validator;
- invalid existing `.relay` state is never automatically repaired;
- successful state vocabulary is `CURRENT`, with `wrote_remote` distinguishing no-op from mutation;
- remote synchronization does not certify or persist its own Relay Baseline;
- deterministic local SQLite migration v3 adds immutable repository-mutation authorization persistence with project and subject indexing only, no Slice foreign key;
- no PR permission, branch creation, force push, background worker, or agent execution is introduced;
- no new runtime dependency is introduced.

The proposed write mechanism continues to use GitHub's Git Data primitives because sequential per-file commits cannot preserve the same-commit registry/artifact invariant for general synchronization.

The local migration does not alter the repository-side schema-v1 contract; it stores Human Authority over a provider side effect in runtime state where that authority belongs.

Design review may still revise or reject the combined proposal. No GitHub write behavior is authorized for production implementation yet.

---

# 10. Product non-goals remain

Relay should not compete mainly on:

- generic agent chat;
- vibe coding;
- running many coding agents;
- free-form Kanban;
- preview environments;
- replacing GitHub/Linear/Jira wholesale.

The product value remains governed engineering continuity:

> Can a human or fresh agent determine what is authoritative, what may proceed, why a decision exists, what exact baseline was evaluated, and what evidence justified acceptance?

---

# 11. Current authority state

```text
Accepted Slice 1.2 design head:
4acd6be1f93058d1efcafc66a78fc1a9726c16ba

Accepted Slice 1.2 technical result:
9ed4a8da4d989fd41674ae59ef68ba4238c09b5d

Independent implementation evaluation:
RLY-S12-EVAL-002 — ACCEPT

Human acceptance:
RLY-S12-ACCEPT-001

Closure evaluation:
RLY-S12-CLOSE-EVAL-001 — ACCEPT

Slice 1.3 opening:
RLY-S13-OPEN-001

Slice 1.3 design authorization:
RLY-S13-DESIGN-AUTH-001

Slice 1.3 Revision 1 evaluation:
RLY-S13-DESIGN-EVAL-001 — REVISE

Slice 1.3 Revision 1 + Revision 2 evaluation:
RLY-S13-DESIGN-EVAL-002 — REVISE

Slice 1.3 Revision 1 + Revision 2 + Revision 3 evaluation:
RLY-S13-DESIGN-EVAL-003 — REVISE

Slice 1.3:
OPEN

Slice 1.3 design:
REVISION 4 SUBMITTED / PENDING INDEPENDENT COMBINED REVIEW

Slice 1.3 implementation:
NOT AUTHORIZED

Slice 1.4:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**

---

# 12. Historical proposals

Product Proposal v0.3 and v0.4 remain historical planning/current-truth snapshots from earlier project states.

They are preserved rather than rewritten.

Canonical current status is determined exclusively by `.relay/registry.json`.