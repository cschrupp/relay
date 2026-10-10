# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Phase 1 deterministic governance foundation; Slice 1.8 paused for architecture/roadmap re-baseline; Phase 2 open
**Document class:** Living canonical projection
**Canonical key:** `product-proposal`
**Supersedes:** v0.4 at `docs/PRODUCT_PROPOSAL_V0_4.md`  
**Date:** October 2026

---

# 1. Product thesis

Relay is the governance control plane for AI software engineering.

> **Nondeterministic agents should operate inside a deterministic engineering state machine.**

Relay governs authority, policy, exact subject and baseline, execution identity and scope, evidence, evaluation, Human decisions, promotion eligibility, and canonical transition.

## Product boundary

Relay is the governance control plane, authority system, policy-enforcement layer, evidence/provenance framework, evaluation/acceptance framework, Human decision-support surface, and canonical-transition governance layer for AI software engineering.

Relay-native planning is **SUPPORTED** and **NOT REQUIRED**. Relay does not require a proprietary specification method, task-decomposition method, coding agent, or orchestration methodology. Future explicit adapters may accept external planning/workflow artifacts, but their authority is never imported automatically. An upstream `approved`, `ready`, `accepted`, `done`, or `green` label is source information, not Relay Human acceptance, authorization, evaluation, or lifecycle state.

Planning and specification generation are treated as commoditized, replaceable capabilities for product-boundary purposes; this is an assumption, not a claim that every method is interchangeable. Governance is Relay's core product thesis. Competitive differentiation and the value of its additional governance cost remain hypotheses for empirical validation, not proven superiority claims. Mature workflow interoperability is preferred to rebuilding planning methodology only for product completeness [SRC-GITHUB-SPEC-KIT-2026] [SRC-OPENSPEC-2026] [SRC-BMAD-METHOD-2026] [SRC-CONSORT-PAPER-2026] [SRC-CONSORT-IMPLEMENTATION-2026].

## Strategic architecture direction

Future `GovernanceProfile` design is intended to select the minimum sufficient controls for exact work from policy and risk context. Implementers, runtimes, agent assertions, and workflow-provider metadata cannot lower that profile. Protected Verification Assets are policy-designated by mutation authority; this does not imply every test is immutable or hidden. `GovernanceEffectivenessTelemetry` is intended to compare assurance value with governance cost without a single score or automatic weakening of controls. These remain future concepts and hypotheses, not implemented product capabilities.

External planning artifacts may eventually be normalized through explicit adapters, with source provenance and adapter identity/version preserved. A normalized artifact is not an authorized Relay Work Packet. Relay binds exact input to its own authority and policy. Spec Kit, OpenSpec, BMAD, and Consort document different workflows and controls; they are reference points for interoperability and research, not evidence of Relay superiority [SRC-GITHUB-SPEC-KIT-2026] [SRC-OPENSPEC-2026] [SRC-BMAD-METHOD-2026] [SRC-CONSORT-PAPER-2026] [SRC-CONSORT-IMPLEMENTATION-2026]. A future controlled comparison is specified only as a non-authoritative research plan in `docs/references/RELAY_COMPETITIVE_VALIDATION_PLAN.md`; it has not been run.

Relay is authoritative for its own governed subjects, policy, and lifecycle decisions. External assurance systems such as SLSA, NIST SSDF, and DORA may inform or evaluate applicable subsets of Relay; they do not define Relay's domain model, lifecycle, or authority semantics [SRC-SLSA-V1_2] [SRC-NIST-SSDF-1_1] [SRC-DORA-CHANGE-APPROVAL].

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

The roadmap is re-baselined under `RLY-P2-ROADMAP-REBASE-001` and amended by `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001`.

```text
Phase 1:
DETERMINISTIC GOVERNANCE FOUNDATION — ACCEPTED BASELINE / HARDENING ACTIVE

Slices 1.1-1.7:
COMPLETE / ACCEPTED / CLOSED

Phase 1 M0:
ACCEPTED / HUMAN-ACCEPTED

Slice 1.8 - Governance Assurance Reference Model:
OPEN - RLY-S18-OPEN-001 / DESIGN AUTHORIZED - PAUSED — ARCHITECTURE / ROADMAP REBASE under RLY-S18-PAUSE-001 / IMPLEMENTATION NOT AUTHORIZED

Slice 1.9 - Human Decision Support and Governance Review Surface:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 1.10 - Canonical Source and Promotion Enforcement:
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

The development frontier intentionally returns to Phase 1 hardening before opening Slice 2.2. Slice 1.8 formalizes Relay's governance-assurance reference model; it is paused before review during this re-baseline. Slice 1.9 is planned to design decision support; Slice 1.10 carries the former source/promotion enforcement proposal.

After those hardening prerequisites, Phase 2 continues upward from the accepted AgentRuntime boundary:

```text
Role Contract
    -> Context / Work Packet
    -> Execution Workspace Authority
    -> AgentRuntime (already accepted in Slice 2.1)
```

Runtime and provider/model choice remain execution-substrate concerns. Relay does not require a particular upstream planning or SDLC workflow.

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

Slice 1.8 is OPEN and paused under RLY-S18-PAUSE-001 for architecture/roadmap re-baseline; design review has not started and implementation remains unauthorized. Slice 1.9 Human Decision Support, Slice 1.10 Source/Promotion, and Slices 2.2–2.4 remain planned, unopened, and unauthorized.

# 5. Implementation and closure governance

The board remains a projection of governed durable state. Slice 1.6 adds the bounded Human command seam while keeping Relay's durable state authoritative. The exact candidate has passed independent implementation evaluation and Human technical acceptance.

Slice 1.5 is closed after independent closure evaluation accepted the exact closure-ready candidate. Its accepted technical result and governance history remain preserved in canonical Git history.

Slice 1.6 implementation is complete and technically accepted at `a62493c733f67a5ce1b2fe5c53892d1833e4c615`. The prior `RLY-S16-EVAL-001 — REWORK` and final `RLY-S16-EVAL-002 — ACCEPT` remain part of its history, followed by Human technical acceptance `RLY-S16-ACCEPT-001`. Independent closure evaluation `RLY-S16-CLOSE-EVAL-001 — ACCEPT` closes Slice 1.6 on the authorized finalization lineage. Canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. No schema migration or new dependency was added.

Slice 1.7 delivers exact result attachment, immutable authored evaluations and evidence, explicit Human technical acceptance, GREEN-gate accepted-result promotion, and causal accepted-Baseline/development-memory projections. Agent execution remains unauthorized.

Slice 1.7 is closed after independent closure evaluation `RLY-S17-CLOSE-EVAL-001 — ACCEPT` verified closure-ready candidate `d7c3876754804ea0f889ec09133b99f569398f1e`. The accepted implementation `2fc1a762e17f45fb1a3d866d8100f2c0c284b435` provides exact result attachment, immutable authored evaluations and evidence, explicit Human technical acceptance, GREEN-gate accepted-result promotion, and causal accepted-Baseline/development-memory projections. Canonical closure commit `5d6773bd5f634246c026b2964ca21e7083a966a1` was promoted to `main`. It uses only authorized migration v5 (`slice_results` and `manual_evaluations`), with no runtime dependency or lifecycle transition-matrix change. Phase 1 M0 viability is accepted and Human-accepted under `RLY-P1-M0-ACCEPT-001`; Phase 1 remains an accepted baseline under active hardening. Phase 2 is open under `RLY-P2-OPEN-001`; Slice 2.1 is complete, accepted, and closed after `RLY-S21-CLOSE-EVAL-002 — ACCEPT`. The assurance / decision-support re-baseline and its authorized strategic amendment keep Slice 1.8 paused before review while incorporating workflow interoperability, GovernanceProfile semantics, Protected Verification Assets, and non-authoritative governance-effectiveness measurement. Slice 1.9 is Human Decision Support, Slice 1.10 is Source/Promotion Enforcement, and Slices 2.2–2.4 remain planned. Phase 3 and real-project agent execution remain unauthorized.

**Unblocked ≠ authorized.**
