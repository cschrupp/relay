# Relay — Product and Technical Proposal

**Version:** 0.5  
**Status:** Current living product and architecture proposal — Slice 2.4 COMPLETE / ACCEPTED / CLOSED; Slice 2.5 OPEN under RLY-S25-OPEN-001 / DESIGN NOT YET AUTHORIZED / IMPLEMENTATION NOT AUTHORIZED; Phase 2 open
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

## Authorized work, specialized agents, and execution granularity

Relay does not need a second planner/worker/reviewer architecture to obtain higher agent autonomy.

The product boundary is:

```text
Human Authority
      ↓
authorized WorkPacket
      ↓
exact RoleContract binding
      ↓
Execution Workspace / AgentRuntime
      ↓
Implementer-owned bounded internal decomposition
      ↓
terminal candidate
      ↓
Independent Evaluator
      ↓
Human acceptance / authorized promotion
```

Planning, architecture, and research agents/personas may produce source artifacts or normalized intent, but those artifacts do not create Relay authority. Runtime-local plans, checklists, subagents, and milestones remain execution mechanics inside the current WorkPacket.

The detailed policy is:

`docs/policies/AUTHORIZED_WORK_DECOMPOSITION_AND_EXECUTION_GRANULARITY.md`

The strategic product rule is:

> **Control should live primarily in exact authority, constraints, deterministic oracles, independent evaluation, and Human acceptance—not in repeated Human permission prompts for routine internal steps that are already authorized.**

When an Implementer discovers required work outside the exact WorkPacket, it must surface non-authoritative `PROPOSED_WORK` and stop rather than expanding its own authority.

This preserves the accepted specialized-agent separation while allowing capable coding agents to work at PR-sized/cohesive-outcome scale instead of being reduced to one-edit-at-a-time natural-language terminals.

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
COMPLETE / ACCEPTED / CLOSED
RLY-S18-EVAL-002 — ACCEPT; RLY-S18-ACCEPT-001 — ACCEPTED;
RLY-S18-CLOSE-EVAL-001 — ACCEPT; RLY-S18-CLOSE-AUTH-001 — AUTHORIZED
Accepted technical candidate: 35046bb378808a1325ecb84eace5aacd3040ca98
Exact closure candidate: 0946d083b1bc1ccd7773f709efacb04a0c00aacc

Slice 1.9 - Human Decision Support and Governance Review Surface:
COMPLETE / ACCEPTED / CLOSED
Accepted technical candidate: 77ad34cf47828464a430ebdbecf1b816f158ae55
RLY-S19-EVAL-003 — ACCEPT; RLY-S19-ACCEPT-001 — ACCEPTED
RLY-S19-CLOSE-EVAL-001 — REWORK; RLY-S19-CLOSE-EVAL-002 — ACCEPT
RLY-S19-CLOSE-AUTH-001 — AUTHORIZED
Exact closure candidate: e8dd2970df445f39954be19dea7ee8241294f44a

Slice 1.10 - Canonical Source and Promotion Enforcement:
OPEN — DESIGN HUMAN ACCEPTED / IMPLEMENTATION AUTHORIZED; B4 COMPLETE / HUMAN ACCEPTED

Phase 2:
OPEN - RLY-P2-OPEN-001

Slice 2.1 - Agent Runtime Contract:
COMPLETE / ACCEPTED / CLOSED

Slice 2.2 - Role Contracts:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation: 4400bd1da0db04e41077c3a6ed1c16d258104ba5
Accepted quality-repaired effective subject: 07bda21295d87602e2a2234622478551920c5014
Independent implementation evaluation: RLY-S22-IMPL-EVAL-003 — ACCEPT
Human technical acceptance: RLY-S22-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S22-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: RLY-S22-CLOSE-EVAL-001 — ACCEPT
Evaluated closure-ready candidate: 358e499ffd571e01d43343449f4bb4a0f50efd6b
Production Role Contract wiring: NOT AUTHORIZED

Slice 2.3 - Context and Work-Packet Contract:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation: 861ccb6bda528a98e1f570a32dcddc61358732e7
Independent implementation evaluation: RLY-S23-IMPL-EVAL-002 — ACCEPT
Human technical acceptance: RLY-S23-ACCEPT-001 — ACCEPTED
Closure authority: RLY-S23-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: RLY-S23-CLOSE-EVAL-001 — ACCEPT
Production wiring, material resolver/storage, DB/lifecycle mutation, runtime execution,
workspace enforcement: NOT AUTHORIZED

Slice 2.4 - Execution Workspace Authority:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation: 73a1525282e41464d31cd458b8a50703bfa9553c
Independent implementation evaluation: RLY-S24-IMPL-EVAL-003 — ACCEPT
Human technical acceptance: RLY-S24-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S24-CLOSE-AUTH-001 — AUTHORIZED
Closure-ready candidate: 8633a08d5ecffa95e518fda1a06765ce0b439388
Independent closure evaluation: RLY-S24-CLOSE-EVAL-001 — ACCEPT

Slice 2.5 - Project State Resolution & Authority Compilation:
OPEN / DESIGN NOT YET AUTHORIZED / IMPLEMENTATION NOT AUTHORIZED
Opening authority: RLY-S25-OPEN-001 — OPEN
Strategic authority: RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED

Phase 3 - First Governed Autonomous Engineering Loop:
NOT OPEN / NOT AUTHORIZED
Slice 2.5 COMPLETE / ACCEPTED / CLOSED is a prerequisite before Phase 3 opening eligibility.

Real-project agent execution:
NOT AUTHORIZED
```

Slice 1.9 Human Decision Support is COMPLETE / ACCEPTED / CLOSED. Accepted technical candidate `77ad34cf47828464a430ebdbecf1b816f158ae55` was accepted for closure by `RLY-S19-CLOSE-EVAL-002 — ACCEPT` under `RLY-S19-CLOSE-AUTH-001`; closure candidate `e8dd2970df445f39954be19dea7ee8241294f44a`. Slice 1.10 carries the source/promotion enforcement work and is OPEN under `RLY-S110-DESIGN-ACCEPT-001 — ACCEPTED` and `RLY-S110-IMPL-AUTH-001 — AUTHORIZED`; B4 Relay Dogfood Acceptance is COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED, while no top-level Slice 1.10 closure record is established.

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
COMPLETE / ACCEPTED / CLOSED under RLY-S22-CLOSE-EVAL-001 — ACCEPT

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

Independent closure evaluation `RLY-S21-CLOSE-EVAL-002 — ACCEPT` accepted the corrective closure-ready candidate and authorized canonical closure and promotion under `RLY-S21-CLOSE-AUTH-001`.

Roadmap re-baseline authority:
`RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED`

Slice 1.8 is COMPLETE / ACCEPTED / CLOSED under `RLY-S18-CLOSE-EVAL-001 — ACCEPT` and `RLY-S18-CLOSE-AUTH-001 — AUTHORIZED`; accepted technical candidate `35046bb378808a1325ecb84eace5aacd3040ca98`, exact closure candidate `0946d083b1bc1ccd7773f709efacb04a0c00aacc`. Slice 1.9 is COMPLETE / ACCEPTED / CLOSED under `RLY-S19-CLOSE-EVAL-002 — ACCEPT` and `RLY-S19-CLOSE-AUTH-001 — AUTHORIZED`; accepted technical candidate `77ad34cf47828464a430ebdbecf1b816f158ae55`, closure candidate `e8dd2970df445f39954be19dea7ee8241294f44a`. Slice 1.10 is OPEN with Human-accepted design and authorized implementation; B4 is COMPLETE / HUMAN ACCEPTED, while top-level Slice 1.10 closure is not established. Slice 2.2 is COMPLETE / ACCEPTED / CLOSED under `RLY-S22-CLOSE-EVAL-001 — ACCEPT`; Slice 2.3 is COMPLETE / ACCEPTED / CLOSED under `RLY-S23-CLOSE-EVAL-001 — ACCEPT`; Slice 2.4 is COMPLETE / ACCEPTED / CLOSED under `RLY-S24-CLOSE-EVAL-001 — ACCEPT`; Slice 2.5 is OPEN under `RLY-S25-OPEN-001`; design and implementation remain separately unauthorized.

# 5. Implementation and closure governance

The board remains a projection of governed durable state. Slice 1.6 adds the bounded Human command seam while keeping Relay's durable state authoritative. The exact candidate has passed independent implementation evaluation and Human technical acceptance.

Slice 1.5 is closed after independent closure evaluation accepted the exact closure-ready candidate. Its accepted technical result and governance history remain preserved in canonical Git history.

Slice 1.6 implementation is complete and technically accepted at `a62493c733f67a5ce1b2fe5c53892d1833e4c615`. The prior `RLY-S16-EVAL-001 — REWORK` and final `RLY-S16-EVAL-002 — ACCEPT` remain part of its history, followed by Human technical acceptance `RLY-S16-ACCEPT-001`. Independent closure evaluation `RLY-S16-CLOSE-EVAL-001 — ACCEPT` closes Slice 1.6 on the authorized finalization lineage. Canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. No schema migration or new dependency was added.

Slice 1.7 delivers exact result attachment, immutable authored evaluations and evidence, explicit Human technical acceptance, GREEN-gate accepted-result promotion, and causal accepted-Baseline/development-memory projections. Agent execution remains unauthorized.

Slice 1.7 is closed after independent closure evaluation `RLY-S17-CLOSE-EVAL-001 — ACCEPT` verified closure-ready candidate `d7c3876754804ea0f889ec09133b99f569398f1e`. The accepted implementation `2fc1a762e17f45fb1a3d866d8100f2c0c284b435` provides exact result attachment, immutable authored evaluations and evidence, explicit Human technical acceptance, GREEN-gate accepted-result promotion, and causal accepted-Baseline/development-memory projections. Canonical closure commit `5d6773bd5f634246c026b2964ca21e7083a966a1` was promoted to `main`. It uses only authorized migration v5 (`slice_results` and `manual_evaluations`), with no runtime dependency or lifecycle transition-matrix change. Phase 1 M0 viability is accepted and Human-accepted under `RLY-P1-M0-ACCEPT-001`; Phase 1 remains an accepted baseline under active hardening. Phase 2 is open under `RLY-P2-OPEN-001`; Slice 2.1 is complete, accepted, and closed after `RLY-S21-CLOSE-EVAL-002 — ACCEPT`. The assurance / decision-support re-baseline and its strategic amendment are now canonically promoted; the combined Slice 1.8 design incorporating workflow interoperability, GovernanceProfile semantics, Protected Verification Assets, and non-authoritative governance-effectiveness measurement is Human-accepted; implementation candidate `35046bb378808a1325ecb84eace5aacd3040ca98` is technically accepted, and Slice 1.8 is closed under `RLY-S18-CLOSE-EVAL-001 — ACCEPT` at closure candidate `0946d083b1bc1ccd7773f709efacb04a0c00aacc`. Slice 1.9 Human Decision Support is COMPLETE / ACCEPTED / CLOSED under `RLY-S19-CLOSE-EVAL-002 — ACCEPT`; Slice 1.10 Source/Promotion Enforcement is OPEN with accepted design and implementation authority, and its B4 dogfood gate is COMPLETE / HUMAN ACCEPTED; Slice 2.3 is COMPLETE / ACCEPTED / CLOSED under `RLY-S23-CLOSE-EVAL-001 — ACCEPT`; Slice 2.4 is COMPLETE / ACCEPTED / CLOSED under `RLY-S24-CLOSE-EVAL-001 — ACCEPT`; Slice 2.5 is OPEN under `RLY-S25-OPEN-001`; design and implementation remain separately unauthorized; Slice 2.2 is COMPLETE / ACCEPTED / CLOSED under `RLY-S22-CLOSE-EVAL-001 — ACCEPT`. Phase 3 and real-project agent execution remain unauthorized.

**Unblocked ≠ authorized.**
