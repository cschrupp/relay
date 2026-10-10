# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 hardening frontier re-baselined; Phase 2 open; Slice 2.1 closed
**Document class:** Living canonical projection
**Canonical key:** `product-proposal`
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** October 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs how engineering work is defined, authorized, handed over, implemented, evaluated, accepted, closed, and remembered.

Relay is the authoritative AI software-development and governance framework. External assurance systems such as SLSA, NIST SSDF, and DORA constrain or evaluate applicable subsets of Relay; they do not define Relay's domain model, lifecycle, or authority semantics.

# 2. Accepted technical foundation

```text
Slices 1.1–1.4:
COMPLETE / ACCEPTED / CLOSED

Slices 1.5–1.7:
COMPLETE / ACCEPTED / CLOSED
```

Slice 1.4 remains the accepted human-controlled Project/Slice definition-administration layer.

# 3. Slice 1.5 — Board Projection

Slice 1.5 was opened under:

```text
RLY-S15-OPEN-001
```

Design is authorized under:

```text
RLY-S15-DESIGN-AUTH-001
```

The design was accepted under `RLY-S15-DESIGN-ACCEPT-001`. Implementation was authorized under `RLY-S15-AUTH-001` and is complete at the exact accepted technical candidate:

```text
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
```

Independent implementation evaluation returned `RLY-S15-EVAL-001 — ACCEPT`, followed by Human technical acceptance `RLY-S15-ACCEPT-001 — ACCEPTED`.

Human-authorized design subject baseline:

```text
359cd61f0c05815390a6822739c0c68d3f020c32
```

Authorized architect:

```text
Slice 1.5 Board Projection Architect — GPT-5.6 Sol
```

Roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

The accepted design makes the board useful without turning it into authority. Governed durable state remains the source of truth; the board derives deterministic human-facing views from that state.

Slice 1.5's accepted design covers projection contracts, deterministic display/traffic-light rules, board structure, read-model/application boundaries, refresh/freshness/error behavior, and minimum UI architecture.

It does not authorize Slice 1.6 human-decision mutation behavior or introduce new lifecycle/governance truth.

# 4. Current roadmap

The roadmap is re-baselined under `RLY-P2-ROADMAP-REBASE-001`.

```text
Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Slices 1.1-1.7:
COMPLETE / ACCEPTED / CLOSED

Phase 1 M0:
ACCEPTED / HUMAN-ACCEPTED

Slice 1.8 - Governance Assurance Reference Model:
PLANNED - NEXT / NOT OPEN / NOT AUTHORIZED

Slice 1.9 - Canonical Source and Promotion Enforcement:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 2:
OPEN - RLY-P2-OPEN-001

Slice 2.1 - Agent Runtime Contract:
COMPLETE / ACCEPTED / CLOSED

Slice 2.2 - Role Contracts:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.3 - Context and Work-Packet Contract:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.4 - Execution Workspace Authority:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3 - First Governed Autonomous Engineering Loop:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

The development frontier intentionally returns to Phase 1 hardening before opening Slice 2.2. Slice 1.8 first formalizes Relay's governance-assurance reference model. Slice 1.9 then closes the gap between declared governance and technical source/promotion enforcement.

After those hardening prerequisites, Phase 2 continues upward from the accepted AgentRuntime boundary:

```text
Role Contract
    -> Context / Work Packet
    -> Execution Workspace Authority
    -> AgentRuntime (already accepted in Slice 2.1)
```

Provider/model choice remains configurable beneath or alongside AgentRuntime. It is not restored as Relay's primary workflow abstraction.

The first autonomous execution work is re-numbered as the first Phase 3 slice. Phase 3 requires separate Human opening authority.

# Current Slice 2.1 closed state

```text
Slice 2.1:
COMPLETE / ACCEPTED / CLOSED

Accepted candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Design acceptance:
RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED

Deterministic implementation evaluation:
RLY-S21-EVAL-005 — ACCEPT

Live sidecar evaluation:
RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT

Human technical acceptance:
RLY-S21-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S21-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S21-CLOSE-EVAL-002 — ACCEPT

Slice 2.2:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Independent closure evaluation `RLY-S21-CLOSE-EVAL-002 — ACCEPT` accepted the corrective closure-ready candidate and authorized canonical closure and promotion under `RLY-S21-CLOSE-AUTH-001`.

Roadmap re-baseline authority:
`RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED`

The next planned development work is Slice 1.8. Slices 1.8, 1.9, 2.2, 2.3, and 2.4 remain unopened and unauthorized.

# 5. Implementation and closure governance

The board remains a projection of governed durable state. Slice 1.6 adds the bounded Human command seam while keeping Relay's durable state authoritative. The exact candidate has passed independent implementation evaluation and Human technical acceptance.

Slice 1.5 is closed after independent closure evaluation accepted the exact closure-ready candidate. Its accepted technical result and governance history remain preserved in canonical Git history.

Slice 1.6 implementation is complete and technically accepted at `a62493c733f67a5ce1b2fe5c53892d1833e4c615`. The prior `RLY-S16-EVAL-001 — REWORK` and final `RLY-S16-EVAL-002 — ACCEPT` remain part of its history, followed by Human technical acceptance `RLY-S16-ACCEPT-001`. Independent closure evaluation `RLY-S16-CLOSE-EVAL-001 — ACCEPT` closes Slice 1.6 on the authorized finalization lineage. Canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. No schema migration or new dependency was added.

Slice 1.7 delivers exact result attachment, immutable authored evaluations and evidence, explicit Human technical acceptance, GREEN-gate accepted-result promotion, and causal accepted-Baseline/development-memory projections. Agent execution remains unauthorized.

Slice 1.7 is closed after independent closure evaluation `RLY-S17-CLOSE-EVAL-001 — ACCEPT` verified closure-ready candidate `d7c3876754804ea0f889ec09133b99f569398f1e`. The accepted implementation `2fc1a762e17f45fb1a3d866d8100f2c0c284b435` provides exact result attachment, immutable authored evaluations and evidence, explicit Human technical acceptance, GREEN-gate accepted-result promotion, and causal accepted-Baseline/development-memory projections. Canonical closure commit `5d6773bd5f634246c026b2964ca21e7083a966a1` was promoted to `main`. It uses only authorized migration v5 (`slice_results` and `manual_evaluations`), with no runtime dependency or lifecycle transition-matrix change. Phase 1 M0 validation remains pending and was not performed under Slice 1.7 finalization authority. Phase 2 is open under `RLY-P2-OPEN-001`; Slice 2.1 is complete, accepted, and closed after `RLY-S21-CLOSE-EVAL-002 — ACCEPT`. Slice 2.2, Phase 3, and real-project agent execution remain unauthorized.

**Unblocked ≠ authorized.**
