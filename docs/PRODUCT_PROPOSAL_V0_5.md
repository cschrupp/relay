# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 / Slice 1.5 and Slice 1.6 closed; Slice 1.6 canonical closure promoted
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
MANUAL EVALUATION AND ACCEPTANCE — NOT OPEN

Agent execution:
NOT AUTHORIZED
```

# 5. Implementation and closure governance

The board remains a projection of governed durable state. Slice 1.6 adds the bounded Human command seam while keeping Relay's durable state authoritative. The exact candidate has passed independent implementation evaluation and Human technical acceptance.

Slice 1.5 is closed after independent closure evaluation accepted the exact closure-ready candidate. Its accepted technical result and governance history remain preserved in canonical Git history.

Slice 1.6 implementation is complete and technically accepted at `a62493c733f67a5ce1b2fe5c53892d1833e4c615`. The prior `RLY-S16-EVAL-001 — REWORK` and final `RLY-S16-EVAL-002 — ACCEPT` remain part of its history, followed by Human technical acceptance `RLY-S16-ACCEPT-001`. Independent closure evaluation `RLY-S16-CLOSE-EVAL-001 — ACCEPT` closes Slice 1.6 on the authorized finalization lineage. Canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. No schema migration or new dependency was added. Slice 1.7 remains not open, and agent execution remains unauthorized.

**Unblocked ≠ authorized.**
