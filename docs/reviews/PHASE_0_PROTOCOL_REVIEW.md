# Relay — Phase 0 Protocol Review

**Review ID:** `RLY-P0-PROTOCOL-REVIEW-001`  
**Status:** SUBMITTED / PENDING HUMAN ACCEPTANCE  
**Document class:** Immutable review record  
**Review baseline:** `6c1b3e1098cdc6c220868aea8a492c413d3cca35`  
**Reviewer role/model:** Phase-0 Protocol Reviewer — GPT-5.6 Sol  
**Date:** 2026-09-26

---

# 1. Purpose

This review satisfies the Phase-0 hard stop defined by the Build Plan.

Phase 0 was intended to answer whether Relay's governance substrate is coherent and useful **without requiring an AI model**.

No GitHub write integration or Phase-1 implementation may begin merely because Phase 0 is technically complete.

---

# 2. Evidence reviewed

Accepted Phase-0 slices:

```text
0.1 Repository and Engineering Foundation
0.2 Core Domain Model
0.3 State Machine and Lifecycle
0.4 Handover Gates and Traffic Lights
0.5 Event and Persistence Model
0.6 .relay Repository Contract
```

Accepted Phase-0 baseline / acceptance-record SHA:

```text
6c1b3e1098cdc6c220868aea8a492c413d3cca35
```

The review also considers the actual dogfooding sequence used to design, implement, independently evaluate, rework, accept, and finalize the Phase-0 slices.

---

# 3. Required hard-stop questions

## Q1 — Can important Relay workflows be represented without an AI model?

**PASS.**

Lifecycle transitions, authorization, human decisions, gate evaluation, persistence, canonical artifact resolution, acceptance provenance, and hard-stop behavior are deterministic.

AI may later produce proposals or implementation work, but the authoritative workflow substrate does not depend on it.

## Q2 — Are authorization and readiness distinct?

**PASS.**

Slice 0.4 explicitly separates validity, authority, and autonomy.

A transition may be structurally valid while still requiring Human Authority.

Dogfooding repeatedly exercised the rule:

> **Unblocked ≠ authorized.**

## Q3 — Are traffic lights deterministic?

**PASS.**

Gate evaluation is a pure deterministic function of explicit context and gate contracts.

RED, YELLOW, and GREEN do not depend on model judgment.

## Q4 — Can project history be reconstructed?

**PASS.**

Relay now combines:

- immutable lifecycle events and replay;
- durable persistence and migration history;
- exact result/baseline SHAs;
- immutable evaluation/acceptance records;
- Git history;
- repository artifact revision/digest metadata;
- locked slice memories and ADRs.

Later repository/baseline integration will prove observation-commit/worktree correspondence, but its absence does not prevent Phase-0 governance history from being reconstructed.

## Q5 — Is `.relay/` authoritative where expected?

**PASS.**

Schema v1 has one repository-contract file:

```text
.relay/registry.json
```

It is authoritative for repository artifact semantics and canonical pointers.

It is not a competing copy of document content and it is not the authority for credentials or runtime operational state.

## Q6 — Do domain objects prematurely assume one provider or UI?

**PASS.**

Core domain and governance objects are provider-neutral.

`RepositoryRef` is generic.

No Phase-0 domain contract requires GitHub, one model provider, or a board UI.

Provider-specific behavior may now be added behind a Phase-1 integration boundary without contaminating the accepted core.

## Q7 — Can a future board be derived from the model without becoming authoritative itself?

**PASS.**

Lifecycle state, gates, authorization, dependencies, baseline/result identity, and artifact authority are represented outside the UI.

A board can therefore be a projection and route requested transitions through the deterministic state/governance layer.

---

# 4. Dogfooding findings

Phase 0 exposed useful process defects without invalidating the architecture.

## P0-PR-01 — Registered living-projection impact must be preflighted

During Slice 0.6 acceptance finalization, the authorized change required modifying `CURRENT_BASELINE.md` while initially forbidding `.relay/registry.json`.

Because `CURRENT_BASELINE.md` was a registered living projection, those instructions were contradictory.

The implementation agent correctly escalated rather than bypassing the contract.

**Required protocol amendment:** any authorized change surface that modifies registered artifact bytes must preflight the registry impact and include the necessary registry advancement.

## P0-PR-02 — Model attribution should remain visible

Relay dogfooding uses different models for architecture/evaluation versus bounded implementation.

That attribution is useful provenance even before provider/model execution is first-class.

**Required convention:** substantive handovers state current role/model and next role/model.

## P0-PR-03 — Design-review outcome vocabulary should be explicit

Design review used `REVISE`, while implementation evaluation has a different accepted outcome vocabulary.

The distinction was understandable but not machine-typed.

**Required convention:** use `ACCEPT / REVISE / ESCALATE` for design review until a later typed design-review contract is introduced. Do not reinterpret an implementation-evaluation outcome.

## P0-PR-04 — Hard-stop review and next-phase authorization are separate

The review may conclude that the next phase is ready.

That conclusion is not itself permission to start.

**Required convention:** Human Authority accepts the review and then separately opens the next phase/slice.

---

# 5. Minimum Sufficient Architecture review

**PASS.**

Phase 0 did not introduce:

- model-provider abstractions before model execution;
- GitHub-specific fields into provider-neutral domain contracts;
- a UI source of truth;
- a generic Git backend before repository integration;
- a repository/cloud last-write-wins scheme;
- full event sourcing where simpler persistence sufficed.

The architecture grew in response to concrete failures found through independent review and dogfooding.

---

# 6. Outcome

```text
OUTCOME:
ACCEPT WITH PROCESS AMENDMENTS

ARCHITECTURE REWORK:
NOT REQUIRED

PHASE-0 TECHNICAL REWORK:
NOT REQUIRED

PROCESS AMENDMENTS:
P0-PR-01 ... P0-PR-04

PHASE 1:
READY FOR HUMAN AUTHORITY DECISION
NOT AUTHORIZED BY THIS REVIEW
```

The process amendments are documentation/protocol conventions and do not require changing Phase-0 production code before Phase 1.

---

# 7. Recommended next action

After Human Authority accepts this review:

1. explicitly open Phase 1;
2. open **Slice 1.1 design only** against the exact post-review baseline;
3. design GitHub App integration without changing accepted provider-neutral semantics;
4. independently review that design;
5. authorize implementation separately.

No Phase-1 implementation is authorized by this review record.
