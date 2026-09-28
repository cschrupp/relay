# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.2 closed  
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

Slice 1.2 establishes the next accepted boundary:

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
.relay INITIALIZATION AND SYNC — NOT OPEN / NOT AUTHORIZED
```

Phase 1 builds a useful human-controlled repository workflow before autonomous coding-agent execution.

Slice 1.2 now provides verified read-only remote repository baseline authority. Remote `.relay/` initialization/write synchronization remains a separate possible Slice 1.3 responsibility and is not authorized.

---

# 9. Slice 1.2 accepted product boundary

Relay can now answer:

> Which provider-neutral repository is authoritative for this Relay project, what immutable commit does the human-selected branch/tag/SHA identify for this operation, and what exact registered repository snapshot was proven before the immutable Baseline was persisted?

The accepted implementation closes the Slice 0.6 trust-boundary deferral for the GitHub path: an authoritative Baseline is derived from the resolved commit's exact tree and registered blob bytes rather than from caller-asserted snapshot provenance.

It also preserves two explicit boundaries:

1. remote snapshot proof does not prove a future agent's local uncommitted worktree cleanliness; and
2. remote repository initialization or mutation remains outside Slice 1.2.

Relay still does not answer:

> Should Relay initialize or change `.relay/` in that remote repository?

That potential behavior belongs to separately governed future work. Slice 1.3 is not open.

Slice 1.2 does not create branches, commits, pull requests, broaden GitHub permissions, mutate Project repository authority, or execute agents.

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

Slice 1.3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ authorized.**

---

# 12. Historical proposals

Product Proposal v0.3 and v0.4 remain historical planning/current-truth snapshots from earlier project states.

They are preserved rather than rewritten.

Canonical current status is determined exclusively by `.relay/registry.json`.
