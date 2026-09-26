# Relay — Product and Technical Proposal

**Version:** 0.4  
**Status:** Current living product and architecture proposal — Phase 1 open  
**Document class:** Living canonical projection  
**Canonical key:** `product-proposal`  
**Supersedes:** v0.3 at `docs/PRODUCT_PROPOSAL.md`  
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

These projects expose the failure modes Relay is intended to solve: forgotten rationale, stale contracts, accidental authority changes, hidden assumptions, weak provenance, and agents acting beyond authorization.

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

Phase 0 is complete and its protocol review is accepted.

Relay has accepted implementations for:

```text
core domain contracts
deterministic lifecycle semantics
handover gates and traffic lights
authorization / human-decision persistence
event and materialized-state persistence
schema migrations and restart integrity
repository-side canonical artifact governance
```

The accepted repository representation is deliberately minimal:

```text
ordinary engineering documents at natural repository paths
+
.relay/registry.json
```

`.relay/registry.json` provides machine-readable artifact semantics and canonical pointers.

It does not contain duplicated copies of project documents.

Runtime/cloud state remains separate from repository authority.

---

# 5. Repository authority

Relay distinguishes:

```text
repository-authoritative engineering artifacts
runtime/cloud operational state
derived UI/search/agent-context projections
```

Repository documents and canonical registry metadata are version controlled.

Credentials, queues, temporary execution state, model/provider credentials, GitHub App keys, and short-lived provider tokens are not repository authority.

Canonical status is explicit. A filename, newest commit, or modification timestamp does not decide authority.

---

# 6. Product workflow

The target governed workflow remains:

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

Research and sidecar experiments may branch from the main path when uncertainty cannot responsibly be resolved by reasoning alone.

---

# 7. Model and provider philosophy

Relay project semantics do not depend on one model vendor.

Different roles may later use different providers/models, but role authority belongs to Relay contracts, not model identity.

Model/provider identity should become execution provenance when agent execution is introduced.

Until then, Relay dogfooding keeps current role/model and next role/model visible in substantive handovers.

---

# 8. Current roadmap

```text
Phase 0:
COMPLETE / CLOSED

Phase-0 protocol review:
ACCEPTED

Phase 1:
OPEN

Slice 1.1:
GITHUB APP INTEGRATION — DESIGN ONLY

Slice 1.1 implementation:
NOT AUTHORIZED
```

Phase 1 adds GitHub integration and the human-controlled product workflow before autonomous coding-agent execution.

The first provider integration remains subordinate to provider-neutral Phase-0 domain semantics.

Repository registration and immutable baseline resolution remain Slice 1.2.

Repository-side `.relay/` initialization/write synchronization remains Slice 1.3.

Provider/model execution follows only after Relay can govern a useful human-only workflow.

---

# 9. Phase-1 product boundary

Slice 1.1 should allow Relay to answer:

> Is this GitHub App installation valid for this Relay project, which repositories can it currently read, what permissions were granted, and is a selected repository still accessible?

It should not yet answer:

> What commit is the authoritative project baseline?

That belongs to Slice 1.2.

It should not yet write:

> Initialize/update `.relay/` in the remote repository.

That belongs to Slice 1.3 and requires a separately accepted write-permission decision.

---

# 10. Product non-goals remain

Relay should not compete mainly on:

- generic agent chat;
- vibe coding;
- running many coding agents;
- free-form Kanban;
- preview environments;
- replacing GitHub/Linear/Jira wholesale.

Those capabilities may integrate with Relay.

The product value is governed engineering continuity:

> Can a human or fresh agent determine what is authoritative, what may proceed, why a decision exists, what exact baseline was evaluated, and what evidence justified acceptance?

---

# 11. Prior proposal

Product Proposal v0.3 remains a useful long-form record of market context, customer rationale, and the broader roadmap.

Where older proposal text described a broad proposed `.relay/` directory or pre-Phase-0 architecture, accepted Slice 0.6 and this projection supersede it.

Historical proposal text remains preserved rather than rewritten in place.
