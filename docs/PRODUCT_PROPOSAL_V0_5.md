# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 2 open; Slice 2.1 closure evaluation pending; Phase 1 M0 validation pending
**Document class:** Living canonical projection
**Canonical key:** `product-proposal`
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** October 2026

---

# 1. Product thesis

Relay is a control plane for governed agentic software engineering.

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs how engineering work is defined, authorized, handed over, implemented, evaluated, accepted, closed, and remembered.

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

```text
Phase 1:
OPEN

Slice 1.5:
BOARD PROJECTION — COMPLETE / ACCEPTED / CLOSED

Slice 1.5 independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Slice 1.6:
HUMAN AUTHORIZATION AND DECISION GATES — COMPLETE / ACCEPTED / CLOSED

Opening authority:
RLY-S16-OPEN-001

Canonical repository head at opening:
d757885ff417cd573b2d3f566d778dd4a37520b3

Slice 1.6 design:
ACCEPTED — RLY-S16-DESIGN-ACCEPT-001

Exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Slice 1.6 implementation:
COMPLETE / TECHNICALLY ACCEPTED — RLY-S16-AUTH-001

Authorized implementation baseline:
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3

Accepted technical candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Prior implementation candidate:
c1fbad66cbede4e16cb39b5065426656df4cfb3a

Prior implementation evaluation:
RLY-S16-EVAL-001 — REWORK

Independent implementation evaluation:
RLY-S16-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S16-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S16-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S16-CLOSE-EVAL-001 — ACCEPT

Canonical closure:
PROMOTED TO MAIN

Canonical closure commit:
9db044036e3591c53d777c81af58af252ebc69a7

Closure evaluation record commit:
fc407e603593a7340515313bfb0b13bc5d286125

Implementation branch:
implementation/1.6-human-authorization-decision-gates

Preferred implementation model:
GPT-5.6 Luna

Executing implementation model:
Codex (GPT-6); provenance deviation recorded in RLY-S16-EVAL-002

Slice 1.7:
MANUAL EVALUATION AND ACCEPTANCE — COMPLETE / ACCEPTED / CLOSED

Design:
ACCEPTED — RLY-S17-DESIGN-ACCEPT-001

Accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Independent design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT

Design acceptance record commit:
9bbf67d9f49c1a81b0a07707f26c0c352d4ef03c

Design evaluation record commit:
10afbeac26bbd2d7de9021e09752a5e8eaf8539b

Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Accepted technical candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Implementation evaluation history:
RLY-S17-EVAL-001 — REWORK
RLY-S17-EVAL-002 — REWORK
RLY-S17-EVAL-003 — ACCEPT

Human technical acceptance:
RLY-S17-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S17-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S17-CLOSE-EVAL-001 — ACCEPT

Closure-ready candidate:
d7c3876754804ea0f889ec09133b99f569398f1e

Closure evaluation record commit:
965d481b02e6dc29e73d9285a3afa31a4f8ce39a

Canonical closure:
PROMOTED TO MAIN

Canonical closure commit:
5d6773bd5f634246c026b2964ca21e7083a966a1

Accepted schema migration:
VERSION 5 — slice_results + manual_evaluations ONLY

Runtime dependencies:
UNCHANGED

Phase 1 M0 validation:
PENDING / NOT YET DECLARED COMPLETE

Phase 2:
OPEN — RLY-P2-OPEN-001

Agent execution:
NOT AUTHORIZED
```

# Current Slice 2.1 closure-ready state

```text
Slice 2.1:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Accepted candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Human technical acceptance:
RLY-S21-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S21-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Slice 2.2:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Slice 2.1 remains open pending independent closure evaluation of the exact closure-ready SHA. The finalization authority does not itself close the Slice.

# 5. Implementation and closure governance

The board remains a projection of governed durable state. Slice 1.6 adds the bounded Human command seam while keeping Relay's durable state authoritative. The exact candidate has passed independent implementation evaluation and Human technical acceptance.

Slice 1.5 is closed after independent closure evaluation accepted the exact closure-ready candidate. Its accepted technical result and governance history remain preserved in canonical Git history.

Slice 1.6 implementation is complete and technically accepted at `a62493c733f67a5ce1b2fe5c53892d1833e4c615`. The prior `RLY-S16-EVAL-001 — REWORK` and final `RLY-S16-EVAL-002 — ACCEPT` remain part of its history, followed by Human technical acceptance `RLY-S16-ACCEPT-001`. Independent closure evaluation `RLY-S16-CLOSE-EVAL-001 — ACCEPT` closes Slice 1.6 on the authorized finalization lineage. Canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. No schema migration or new dependency was added.

Slice 1.7 delivers exact result attachment, immutable authored evaluations and evidence, explicit Human technical acceptance, GREEN-gate accepted-result promotion, and causal accepted-Baseline/development-memory projections. Agent execution remains unauthorized.

Slice 1.7 is closed after independent closure evaluation `RLY-S17-CLOSE-EVAL-001 — ACCEPT` verified closure-ready candidate `d7c3876754804ea0f889ec09133b99f569398f1e`. The accepted implementation `2fc1a762e17f45fb1a3d866d8100f2c0c284b435` provides exact result attachment, immutable authored evaluations and evidence, explicit Human technical acceptance, GREEN-gate accepted-result promotion, and causal accepted-Baseline/development-memory projections. Canonical closure commit `5d6773bd5f634246c026b2964ca21e7083a966a1` was promoted to `main`. It uses only authorized migration v5 (`slice_results` and `manual_evaluations`), with no runtime dependency or lifecycle transition-matrix change. Phase 1 M0 validation remains pending and was not performed under Slice 1.7 finalization authority. Phase 2 is open under `RLY-P2-OPEN-001`; Slice 2.1 is closure-ready and remains open pending independent closure evaluation. Slice 2.2, Phase 3, and real-project agent execution remain unauthorized.

**Unblocked ≠ authorized.**
