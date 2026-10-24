# Relay — Current Baseline

**Status:** Current living baseline — Slice 2.4 COMPLETE / ACCEPTED / CLOSED; Slice 2.5 OPEN under RLY-S25-OPEN-001 / DESIGN NOT YET AUTHORIZED / IMPLEMENTATION NOT AUTHORIZED
**Document class:** Living canonical projection
**Canonical key:** `current-baseline`
**Date:** October 24, 2026

---

# 0. Executive current state — Slice 2.4 closed; Slice 2.5 open

This is the controlling current-state summary. Older detailed records below remain useful history but may contain superseded status text.

```text
Core governance foundation:
1.1–1.9                       COMPLETE / CLOSED
1.10 canonical/promotion core OPEN / DESIGN ACCEPTED / IMPLEMENTATION AUTHORIZED
2.1 Agent Runtime Contract    COMPLETE / CLOSED

Dogfood/onboarding:
V1 Human control surface      HUMAN ACCEPTED
PG1 pre-genesis origin        HUMAN ACCEPTED
B0 Rev3 design                HUMAN ACCEPTED
B0 evidence preparation       INDEPENDENT ACCEPT — VALID FAIL-CLOSED STOP
B0 usable Genesis package     BLOCKED
Blocking evidence facts       7
Bootstrap V2                  NOT CREATED
B0-F design                    HUMAN ACCEPTED
B0-F implementation           COMPLETE / HUMAN ACCEPTED
B0-F behavior                  READ-ONLY LOCAL REPOSITORY INSPECTION
B0 importer / database        NOT IMPLEMENTED / NOT AUTHORIZED
B1 implementation             COMPLETE / HUMAN ACCEPTED
B1 accepted candidate          22fb742965ed6424a18275b4234e1399021d4aed
B1 real-world dogfood          AUTHORIZED / NOT EXECUTED BEFORE ACCEPTANCE
B2 design                       COMPLETE / HUMAN ACCEPTED
B2 accepted composite           80b1f77c4d4cd1f3303b4a1072a46b0cfb605621
B2 implementation               COMPLETE / HUMAN ACCEPTED
B2 actual adoption / T1          COMPLETE / HUMAN ACCEPTED
B2 operational database          PUBLISHED / VERIFIED
B2 real-adoption authority         RLY-S110-DOGFOOD-B2-ADOPTION-AUTH-001 — AUTHORIZED

Slice 2.2 — Role Contracts:
COMPLETE / ACCEPTED / CLOSED
Accepted Role Contracts implementation: 4400bd1da0db04e41077c3a6ed1c16d258104ba5
Accepted quality-repaired effective subject: 07bda21295d87602e2a2234622478551920c5014
Independent implementation evaluation: RLY-S22-IMPL-EVAL-003 — ACCEPT
Human technical acceptance: RLY-S22-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S22-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: RLY-S22-CLOSE-EVAL-001 — ACCEPT
Evaluated closure-ready candidate: 358e499ffd571e01d43343449f4bb4a0f50efd6b
Production Role Contract wiring: NOT AUTHORIZED
Slice 2.3 — Context / Work-Packet Contract:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation: 861ccb6bda528a98e1f570a32dcddc61358732e7
Independent implementation evaluation: RLY-S23-IMPL-EVAL-002 — ACCEPT
Human technical acceptance: RLY-S23-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S23-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: RLY-S23-CLOSE-EVAL-001 — ACCEPT
Production WorkPacket / ContextManifest wiring: NOT AUTHORIZED
Context material resolver/storage: NOT AUTHORIZED
Operational DB / lifecycle mutation: NOT AUTHORIZED
Runtime/provider/model execution: NOT AUTHORIZED
Workspace enforcement: NOT AUTHORIZED
Slice 2.4: COMPLETE / ACCEPTED / CLOSED under RLY-S24-CLOSE-EVAL-001 — ACCEPT
Accepted implementation: 73a1525282e41464d31cd458b8a50703bfa9553c
Independent implementation evaluation: RLY-S24-IMPL-EVAL-003 — ACCEPT
Human technical acceptance: RLY-S24-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S24-CLOSE-AUTH-001 — AUTHORIZED
Closure-ready candidate: 8633a08d5ecffa95e518fda1a06765ce0b439388
Independent closure evaluation: RLY-S24-CLOSE-EVAL-001 — ACCEPT
Slice 2.5: OPEN / DESIGN NOT YET AUTHORIZED / IMPLEMENTATION NOT AUTHORIZED — Project State Resolution & Authority Compilation
Opening authority: RLY-S25-OPEN-001 — OPEN
Strategic authority: RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED
Phase 3: NOT OPEN / NOT AUTHORIZED
Real-project agent execution: NOT AUTHORIZED

Current product problem:
Relay can govern state once it exists, but normal onboarding of an existing
project must not require reconstruction of fictional Relay-native history.

Current roadmap direction:
B0-F can inspect ordinary Git repositories without Relay state. B1 Design Revision 1 received REWORK for observed-value revalidation and observation-correction semantics. Revision 2 closed those findings and the composite design was independently accepted and Human-accepted. The B1 intake implementation is independently accepted and Human-accepted at exact candidate `22fb742965ed6424a18275b4234e1399021d4aed`. The authorized Relay/WellPlot real-world dogfood has no completed result recorded before acceptance. B2 Revision 1 plus its Revision 2 Integrity Amendment is independently accepted and Human-accepted at exact composite candidate `80b1f77c4d4cd1f3303b4a1072a46b0cfb605621`. B2 implementation is independently accepted under `RLY-S110-DOGFOOD-B2-IMPL-EVAL-002` and Human-accepted under `RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001` at exact candidate `0b3c07dc41d4a0cb81749e8c00a3d006b9645097`. The authorized real Relay B2 adoption executed from clean HEAD `be1dd6f479d601c7ae2eea3985675f53ab748637`. The Human entered exact `ADOPT`; T1 is `2026-10-20T03:27:54.511113Z`; the operational database was atomically published at `/home/user/projects/relay-local-state/relay-operational.sqlite3`. Terminal evidence SHA-256 is `89928fdfadbca85fafe549e8b496c7cb97192740dd2b28b6ea583d87c08bbe5c`. Independent review `RLY-S110-DOGFOOD-B2-ADOPTION-EVAL-001 — ACCEPT` found no blocking discrepancy. Human acceptance is recorded under `RLY-S110-DOGFOOD-B2-ADOPTION-ACCEPT-001`. B2 real adoption is closed; B3 design, Stage A tooling, and Stage B materialization are COMPLETE / HUMAN ACCEPTED; B4 Revision 2 Attempt 006 is COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED; Slice 2.2 is COMPLETE / ACCEPTED / CLOSED. Strict historical bootstrap remains blocked and is separate from B2.
```

## Authorized-work decomposition and execution granularity

Human-approved cross-cutting direction:

`RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED`

Detailed policy:

`docs/policies/AUTHORIZED_WORK_DECOMPOSITION_AND_EXECUTION_GRANULARITY.md`

Current controlling interpretation:

```text
WorkPacket
    = authoritative external work unit

DECOMPOSE_AUTHORIZED_WORK
    = bounded internal execution decomposition

internal task / milestone
    != WorkPacket
    != Human approval gate

out-of-scope required work
    -> PROPOSED_WORK
    -> STOP
    -> separate Relay authority
```

Relay will not create a parallel planner/worker/reviewer state machine. Planning personas, runtime-local plans, and runtime-local subagents remain non-authoritative inputs/execution mechanics inside the existing RoleContract → WorkPacket → Workspace → AgentRuntime → independent-evaluation → Human-acceptance architecture.

Initial operational target: prefer cohesive STANDARD/EXTENDED implementation outcomes (roughly 2–6 human-expert hours as a provisional calibration band) and use SURGICAL external granularity only when risk, authority, independent acceptance, rollback, or measured reliability justifies it.

The active Slice 2.4 implementation was authorized before this documentation re-baseline and remains governed by its exact existing scope. This policy does not retroactively alter `RLY-S24-CODEX-SCOPE-001`.

## Slice 2.4 implementation review and corrective authority

The exact implementation candidate `8bb3534ac0803e56e411105233c294eaa1c4586a` was independently reviewed under `RLY-S24-IMPL-EVAL-001 — REWORK`, recorded at governance commit `41d819e96b619dcb10a16cd2815a105ead418827`.

Blocking findings are exactly:

```text
I001 unsupported filesystem/Git node kinds are silently omitted
I002 protected physical-access compatibility can widen ordinary filesystem policy
I003 frozen minimum deterministic test matrix is materially incomplete
```

Human corrective authority is now:

`RLY-S24-IMPL-REWORK-AUTH-001 — AUTHORIZED`

Dedicated corrective branch:

`implementation/2.4-execution-workspace-authority-rework-001`

The corrective implementation is limited to I001/I002/I003 and the exact mutable surface named by the authority record. Human technical acceptance, Slice 2.4 closure, production wiring, AgentRuntime execution, Phase 3, and canonical/main promotion remain unauthorized.

Corrective candidate `aa9d71fb749137b60ba8ad620cd43ef7155ad310` received `RLY-S24-IMPL-EVAL-002 — ESCALATE`. I001 and I002 were closed by that candidate. I003-R1 was closed by exact corrective candidate `73a1525282e41464d31cd458b8a50703bfa9553c`. I003-R2 was resolved by Design Revision 6, independently accepted under `RLY-S24-I003-R2-DESIGN-EVAL-002 — ACCEPT` and Human-accepted under `RLY-S24-I003-R2-DESIGN-ACCEPT-001 — ACCEPTED`. Runtime tool/shell exposure obligations remain preserved for runtime integration. Final independent implementation evaluation `RLY-S24-IMPL-EVAL-003 — ACCEPT` accepts exact implementation candidate `73a1525282e41464d31cd458b8a50703bfa9553c`. Human technical acceptance is recorded under `RLY-S24-ACCEPT-001 — ACCEPTED`. Independent closure evaluation `RLY-S24-CLOSE-EVAL-001 — ACCEPT` accepts closure-ready candidate `8633a08d5ecffa95e518fda1a06765ce0b439388`; Slice 2.4 is COMPLETE / ACCEPTED / CLOSED. Production workspace provisioning, production WorkPacket wiring, runtime-exposure implementation, Slice 2.5 implementation, Phase 3, and real-project execution remain unauthorized.


## Strategic Phase-2 addition — Project State Resolution and Authority Compilation

Human strategic authority:

`RLY-P2-STATE-AUTHORITY-COMPILATION-STRATEGIC-AMEND-001 — AUTHORIZED`

Architecture direction:

`docs/architecture/PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md`

Proposed Slice:

`docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION.md`

The observed integrity failure is that Relay can preserve accepted knowledge without deterministically propagating it as prerequisites and inherited constraints for later authority. Slice 2.5 addresses this by deriving current project state from canonical records and compiling requested outcomes against exact predecessors, invariants, prohibitions, qualification applicability, responsibility ownership, and evidence lineage.

Frozen strategic rules:

```text
Relay remains the only governance state machine.
Project state graph is derived, not independently authoritative.
Authority Compiler does not grant Human authority.
WorkPacket remains the authoritative external work unit.
Historical evidence remains immutable; current applicability is derived.
Slice 2.5 must close before Phase 3 becomes eligible to open.
```

Slice 2.5 is OPEN under `RLY-S25-OPEN-001`. Normative design work is not yet authorized, and no production implementation is authorized.

## Current product principle

For legacy projects, the past is context; the future is the product.

Relay should inspect what exists now, ask the Human for current objectives/status/constraints that code cannot establish, create a trustworthy adoption boundary T1, and govern future continuation/refactor/rework. Historical reconstruction is required only when a current/future decision materially depends on it.

Strategy: [Existing Project Adoption and Forward-Governance Strategy](strategy/EXISTING_PROJECT_ADOPTION_AND_FORWARD_GOVERNANCE.md)  
Execution checklist: [Development TODO](TODO.md)

## Current planned frontier

```text
B0-F Bootstrap Engine Finish              COMPLETE / HUMAN ACCEPTED
B1 Project Discovery & Human Intake       COMPLETE / HUMAN ACCEPTED
B2 Existing Project Adoption / T1 Genesis DESIGN COMPLETE / HUMAN ACCEPTED
B2 implementation COMPLETE / HUMAN ACCEPTED
B2 real Relay adoption / T1 COMPLETE / HUMAN ACCEPTED
B3 Forward Re-baseline / First Work       COMPLETE / HUMAN ACCEPTED
B4 Relay Dogfood Acceptance               COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED

Then:
2.2 Role Contracts — COMPLETE / ACCEPTED / CLOSED; 2.3 Context / Work-Packet Contract — COMPLETE / ACCEPTED / CLOSED; 2.4 Execution Workspace Authority — COMPLETE / ACCEPTED / CLOSED under RLY-S24-CLOSE-EVAL-001 — ACCEPT; 2.5 Project State Resolution & Authority Compilation — PROPOSED / NOT OPEN / NOT AUTHORIZED
```

B0-F implementation is Human-accepted under `RLY-S110-DOGFOOD-B0F-IMPL-ACCEPT-001` at exact candidate `65bf57f69f8de4526d080e03da9f796bc20f46ec`. B1 design was authorized under `RLY-S110-DOGFOOD-B1-DESIGN-AUTH-001` from opening tip `4283c2e55da17af8b1c07af6b554a581028e51db`. Revision 1 plus `docs/slices/SLICE_1_10_DOGFOOD_B1_PROJECT_DISCOVERY_HUMAN_INTAKE_DESIGN_REV2_OBSERVATION_INTEGRITY.md` is the accepted composite design at `837edeae8bf36c414e78aa7c68af708590b9e90b`. `RLY-S110-DOGFOOD-B1-DESIGN-EVAL-002 — ACCEPT` and `RLY-S110-DOGFOOD-B1-DESIGN-ACCEPT-001 — ACCEPTED` are recorded. B1 implementation is Human-accepted under `RLY-S110-DOGFOOD-B1-IMPL-ACCEPT-001` at exact candidate `22fb742965ed6424a18275b4234e1399021d4aed`, following `RLY-S110-DOGFOOD-B1-IMPL-EVAL-002 — ACCEPT`. Real-world dogfood was authorized but no completed result is recorded before acceptance. B2 design is Human-accepted under `RLY-S110-DOGFOOD-B2-DESIGN-ACCEPT-001` at exact composite `80b1f77c4d4cd1f3303b4a1072a46b0cfb605621`, comprising Revision 1 `189bb329e8d131c758a2a4d578f6ca2e701687b6` plus the Revision 2 Integrity Amendment. F001 and F002 from `RLY-S110-DOGFOOD-B2-DESIGN-EVAL-001 — REWORK` are closed by `RLY-S110-DOGFOOD-B2-DESIGN-EVAL-002 — ACCEPT`. B2 implementation is Human-accepted under `RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001` at exact candidate `0b3c07dc41d4a0cb81749e8c00a3d006b9645097`, following `RLY-S110-DOGFOOD-B2-IMPL-EVAL-001 — REWORK` and corrective `RLY-S110-DOGFOOD-B2-IMPL-EVAL-002 — ACCEPT`. Real Relay B2 adoption executed successfully from the pinned clean checkout and was independently accepted under `RLY-S110-DOGFOOD-B2-ADOPTION-EVAL-001`. T1 is `2026-10-20T03:27:54.511113Z`; the published external operational database passed integrity, foreign-key, provenance, report-state, fingerprint, and minimal-history checks. Human result acceptance is recorded under `RLY-S110-DOGFOOD-B2-ADOPTION-ACCEPT-001`. B2 real adoption is COMPLETE. B3 design, Stage A tooling, and Stage B materialization are COMPLETE / HUMAN ACCEPTED. The Human-directed first governed work target was Slice 2.2 Role Contracts with authorized-work exhaustion integrated into the work boundary. B4 Revision 2 Attempt 006 is COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED under `RLY-S110-DOGFOOD-B4-R2-EXEC-EVAL-006 — PASS` and `RLY-S110-DOGFOOD-B4-R2-RESULT-ACCEPT-006 — ACCEPTED`. Slice 2.2 is COMPLETE / ACCEPTED / CLOSED under `RLY-S22-CLOSE-EVAL-001 — ACCEPT`; accepted implementation `4400bd1da0db04e41077c3a6ed1c16d258104ba5` remains unchanged.


---

# 1. Accepted foundation

```text
Phase 1 — DETERMINISTIC GOVERNANCE FOUNDATION
ACCEPTED BASELINE / HARDENING ACTIVE
Slices 1.1–1.7: COMPLETE / ACCEPTED / CLOSED
Slice 1.8 — Governance Assurance Reference Model:
  OPEN; RLY-S18-OPEN-001; resumed by RLY-S18-RESUME-001;
  combined design accepted by RLY-S18-DESIGN-ACCEPT-001;
  COMPLETE / ACCEPTED / CLOSED
  RLY-S18-EVAL-002 — ACCEPT; RLY-S18-ACCEPT-001 — ACCEPTED;
  RLY-S18-CLOSE-EVAL-001 — ACCEPT; RLY-S18-CLOSE-AUTH-001 — AUTHORIZED
  Accepted technical candidate: 35046bb378808a1325ecb84eace5aacd3040ca98
  Exact closure candidate: 0946d083b1bc1ccd7773f709efacb04a0c00aacc
Slice 1.9 — Human Decision Support & Governance Review Surface:
  COMPLETE / ACCEPTED / CLOSED
  Accepted technical candidate: 77ad34cf47828464a430ebdbecf1b816f158ae55
  RLY-S19-EVAL-003 — ACCEPT; RLY-S19-ACCEPT-001 — ACCEPTED
  RLY-S19-CLOSE-EVAL-001 — REWORK; RLY-S19-CLOSE-EVAL-002 — ACCEPT
  RLY-S19-CLOSE-AUTH-001 — AUTHORIZED
  Exact closure candidate: e8dd2970df445f39954be19dea7ee8241294f44a
Slice 1.10 — Canonical Source and Promotion Enforcement:
  OPEN — DESIGN HUMAN ACCEPTED / IMPLEMENTATION AUTHORIZED; B4 COMPLETE / HUMAN ACCEPTED
Phase 2: OPEN; Slice 2.1 COMPLETE / ACCEPTED / CLOSED;
  2.2 COMPLETE / ACCEPTED / CLOSED;
  2.3 COMPLETE / ACCEPTED / CLOSED — RLY-S23-CLOSE-EVAL-001 — ACCEPT;
  2.4 OPEN / DESIGN HUMAN ACCEPTED / IMPLEMENTATION AUTHORIZED
Phase 3: NOT OPEN / NOT AUTHORIZED
Real-project agent execution: NOT AUTHORIZED
```

```text
Slice 1.1:
COMPLETE / ACCEPTED / CLOSED

Slice 1.2:
COMPLETE / ACCEPTED / CLOSED

Slice 1.3:
COMPLETE / ACCEPTED / CLOSED

Slice 1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.6:
COMPLETE / ACCEPTED / CLOSED

Slice 1.7:
COMPLETE / ACCEPTED / CLOSED
```

# 1A. Phase 1 viability and Phase 2 opening

```text
Phase 1 M0 evaluation:
RLY-P1-M0-EVAL-001 — ACCEPT

Human M0 acceptance:
RLY-P1-M0-ACCEPT-001 — ACCEPTED

Accepted engineering baseline entering the Phase 2 transition:
cf8aae9d44bfef5019500bac37ae6baf3cdb5235

Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Phase 1 production maturity:
NOT CLAIMED

Phase 2 opening authority:
RLY-P2-OPEN-001 — AUTHORIZED

Phase 2:
OPEN

Slice 2.1: COMPLETE / ACCEPTED / CLOSED
Design: RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED
Implementation: COMPLETE / TECHNICALLY ACCEPTED
Candidate: 4f785f08576e465cd0aa278f927fa4b7253e3f49
Deterministic implementation evaluation: RLY-S21-EVAL-005 — ACCEPT
Live sidecar evaluation: RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT
Human technical acceptance: RLY-S21-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S21-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: RLY-S21-CLOSE-EVAL-002 — ACCEPT
Roadmap re-baseline: RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED
Slice 1.8 — Governance Assurance Reference Model: COMPLETE / ACCEPTED / CLOSED — RLY-S18-EVAL-002 — ACCEPT / RLY-S18-ACCEPT-001 — ACCEPTED / RLY-S18-CLOSE-EVAL-001 — ACCEPT / RLY-S18-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE 0946d083b1bc1ccd7773f709efacb04a0c00aacc
Slice 1.9 — Human Decision Support and Governance Review Surface: COMPLETE / ACCEPTED / CLOSED — RLY-S19-CLOSE-EVAL-002 — ACCEPT / RLY-S19-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE e8dd2970df445f39954be19dea7ee8241294f44a
Slice 1.10 — Canonical Source and Promotion Enforcement: OPEN — DESIGN HUMAN ACCEPTED / IMPLEMENTATION AUTHORIZED; B4 COMPLETE / HUMAN ACCEPTED
Slice 2.2 — Role Contracts: COMPLETE / ACCEPTED / CLOSED
Slice 2.3 — Context and Work-Packet Contract: COMPLETE / ACCEPTED / CLOSED under RLY-S23-CLOSE-EVAL-001 — ACCEPT
Slice 2.4 — Execution Workspace Authority: COMPLETE / ACCEPTED / CLOSED / RLY-S24-CLOSE-EVAL-001 — ACCEPT
Phase 3: NOT OPEN / NOT AUTHORIZED
Real-project agent execution: NOT AUTHORIZED

Relay agent execution:
NOT AUTHORIZED
```

M0 established project viability and justified continued investment. It did not assert that the Phase 1 product surface is production-ready.

Phase 1 remains the deterministic governing substrate for later phases and continues to receive separately authorized hardening for practicality, governance clarity, UI/UX, information hierarchy, development memory, and operator workflow.

Phase 2 may proceed on that accepted baseline. A Phase 1 defect that threatens authority integrity, determinism, provenance, Human control, evaluator independence, accepted-result promotion, or fail-closed behavior blocks affected Phase 2 work until resolved.

**Unblocked ≠ authorized. Phase open ≠ Slice open. Slice open ≠ design authorized. Design accepted ≠ implementation authorized.**

# 1B. Re-baselined development frontier

```text
Current Phase 1 roadmap:
1.8 — Governance Assurance Reference Model: COMPLETE / ACCEPTED / CLOSED — RLY-S18-EVAL-002 — ACCEPT / RLY-S18-ACCEPT-001 — ACCEPTED / RLY-S18-CLOSE-EVAL-001 — ACCEPT / RLY-S18-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE 0946d083b1bc1ccd7773f709efacb04a0c00aacc
1.9 — Human Decision Support and Governance Review Surface: COMPLETE / ACCEPTED / CLOSED — RLY-S19-CLOSE-EVAL-002 — ACCEPT / RLY-S19-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE e8dd2970df445f39954be19dea7ee8241294f44a
1.10 — Canonical Source and Promotion Enforcement: OPEN — DESIGN HUMAN ACCEPTED / IMPLEMENTATION AUTHORIZED; B4 COMPLETE / HUMAN ACCEPTED

Then Phase 2 continues:
2.2 — Role Contracts: COMPLETE / ACCEPTED / CLOSED — RLY-S22-CLOSE-EVAL-001 — ACCEPT
2.3 — Context and Work-Packet Contract
2.4 — Execution Workspace Authority

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

This ordering places assurance and promotion hardening beneath later agent autonomy. External standards remain compliance/assurance references; Relay-native semantics remain authoritative.

## 1B.1 Strategic amendment state

`RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001` authorized the documentation and architecture re-baseline, which is now independently accepted, Human-accepted, and canonically promoted. The prior pause incorporated workflow interoperability, risk-adaptive governance through a future GovernanceProfile, Protected Verification Assets, and governance-effectiveness measurement. Slice 1.8 has resumed under `RLY-S18-RESUME-001`; Design Revision 1 remains byte-preserved and normative where not explicitly amended by the accepted Revision 2 + Rework 1 chain; acceptance applies to the combined design, not Revision 1 alone. Design Revision 2 and Rework 1 are independently accepted under `RLY-S18-DESIGN-EVAL-002` and Human-accepted under `RLY-S18-DESIGN-ACCEPT-001`. The documentation/governance-model implementation was accepted at the exact candidate recorded above. Independent closure evaluation `RLY-S18-CLOSE-EVAL-001 — ACCEPT` closed Slice 1.8 on the exact closure candidate recorded above; production/runtime code remains unauthorized.

```text
Relay:
governance control plane for AI software engineering

Relay-native planning:
SUPPORTED / NOT REQUIRED

External workflow authority:
NEVER IMPORTED AUTOMATICALLY

GovernanceProfile and protected-verification semantics:
SEMANTICS DOCUMENTED / NO EXECUTABLE ENGINE OR ENFORCEMENT

GovernanceEffectivenessTelemetry:
FUTURE / NON-AUTHORITATIVE / NOT IMPLEMENTED

Competitive validation:
PLANNED RESEARCH ONLY / NOT EXECUTED
```

## Slice 1.8 closure result

Status: **COMPLETE / ACCEPTED / CLOSED**. `RLY-S18-EVAL-002 — ACCEPT`; `RLY-S18-ACCEPT-001 — ACCEPTED`; `RLY-S18-CLOSE-EVAL-001 — ACCEPT`; `RLY-S18-CLOSE-AUTH-001 — AUTHORIZED`. Accepted technical candidate: `35046bb378808a1325ecb84eace5aacd3040ca98`; closure candidate: `0946d083b1bc1ccd7773f709efacb04a0c00aacc`.

Authority: `RLY-S18-IMPL-AUTH-001`; implementation start `a7cd87fea89e3b0273da1d0c0884336cc7857357`; accepted combined-design baseline `eae25f0837bbce435e54fc3437b502dea1224744`.

The consolidated [reference model](architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md) contains all 17 native properties, exact subject/policy contracts, cross-cutting Decision Support, prospective GovernanceProfile rules, protected-asset mutation-authority separation, workflow neutrality, external mapping/freshness, and downstream ownership. Supporting documents provide [20 worked examples and 30 negative cases](architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md) and [mapping/source traceability](references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md). See the [implementation handoff](reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF_REV2.md) for design coverage and quality evidence.

Product Proposal revision 50 records Slice 1.8 and Slice 1.9 closure. Slice 1.9 is COMPLETE / ACCEPTED / CLOSED under `RLY-S19-CLOSE-EVAL-002 — ACCEPT` and `RLY-S19-CLOSE-AUTH-001 — AUTHORIZED`; closure candidate `e8dd2970df445f39954be19dea7ee8241294f44a`. Historical Slice 2.1 roadmap references to Slice 1.9 source/promotion enforcement are superseded by accepted RW1-D01: Slice 1.9 owns Decision Support and Slice 1.10 owns enforcement.

No runtime, production/test source, schema, dependency, workflow, or repository-setting change is included. Profiles remain non-executable; protected assets are not enforced; adapters and ContextManifest remain future; telemetry is not collected; the competitive experiment is not executed. Independent implementation evaluation and Human technical acceptance were followed by `RLY-S18-CLOSE-EVAL-001 — ACCEPT`; Slice 1.8 is closed under the existing finalization authority. At the time of this Slice 1.8 record, Slices 1.9 and 1.10 had not opened. Current status: Slice 1.9 is COMPLETE / ACCEPTED / CLOSED after `RLY-S19-CLOSE-EVAL-001 — REWORK` and corrective `RLY-S19-CLOSE-EVAL-002 — ACCEPT` under `RLY-S19-CLOSE-AUTH-001`; closure candidate `e8dd2970df445f39954be19dea7ee8241294f44a`. Slice 1.10 is OPEN under `RLY-S110-DESIGN-ACCEPT-001 — ACCEPTED` and `RLY-S110-IMPL-AUTH-001 — AUTHORIZED`; B4 is COMPLETE / INDEPENDENTLY PASS / HUMAN ACCEPTED, while no top-level Slice 1.10 closure record is established. Phase 3 and agent execution remain unauthorized.

# 1C. Slice 2.1 historical opening

```text
Slice:
2.1 — Agent Runtime Contract

Opening authority:
RLY-S21-OPEN-001 — OPEN

Opening baseline:
eac62b054af3815cc179c95d0d31aa96f9a374e3

Design authorization:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

Design subject baseline:
2a02da12954a2ed54afdf088576e55dc19283a78

Exact accepted combined design head:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Independent design evaluation:
RLY-S21-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authorization:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Implementation:
COMPLETE / TECHNICALLY ACCEPTED

Accepted candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Deterministic implementation evaluation:
RLY-S21-EVAL-005 — ACCEPT

Live sidecar evaluation:
RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT

Human technical acceptance:
RLY-S21-ACCEPT-001 — ACCEPTED

Finalization / closure authority:
RLY-S21-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
PENDING

Authorized implementation baseline:
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22

Prior implementation candidate:
c947cf607699707b8b56d22cbb9aab4b30a7bf4a

Prior implementation evaluation:
RLY-S21-EVAL-001 — REWORK

Current implementation candidate:
ded3ed03b7070ea095a823129ebe44935cb57997

Independent implementation evaluation:
RLY-S21-EVAL-002 — ACCEPT

Implementation:
DETERMINISTICALLY ACCEPTED

Live OpenCode sidecar authority:
RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED

Live OpenCode sidecar run 001:
STOPPED FAIL-CLOSED

Live OpenCode sidecar evaluation:
RLY-S21-SIDECAR-EVAL-001 — ESCALATE

Evidence finding:
OpenCode 1.18.23 / V1 environment does not satisfy the candidate's pinned V2 contract

Live OpenCode sidecar evidence:
INCOMPLETE / COMPATIBLE V2 RUNTIME REQUIRED

V2 sidecar runtime provisioning authority:
RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED

V2 sidecar run 002:
STOPPED FAIL-CLOSED BEFORE COMPATIBILITY PREFLIGHT

V2 sidecar run 002 evaluation:
RLY-S21-SIDECAR-EVAL-002 — ESCALATE

Run 002 finding:
V2 package postinstall inherited protected V1 HOME/XDG state; V1 state integrity is not attestable

V2 sidecar run 003:
STOPPED FAIL-CLOSED AT AUTHENTICATED COMPATIBILITY PREFLIGHT

V2 sidecar run 003 evaluation:
RLY-S21-SIDECAR-EVAL-003 — ESCALATE

Run 003 finding:
isolated V2 server required HTTP authentication; unauthenticated candidate client correctly normalized 401 as AUTHENTICATION

V2 sidecar run 004:
STOPPED AT PROVIDER CREDENTIAL PREREQUISITE AFTER LIVE V2 COMPATIBILITY PASS

V2 sidecar run 004 evaluation:
RLY-S21-SIDECAR-EVAL-004 — ESCALATE

Run 004 established:
AUTHENTICATED V2 /api/health PASS
UNCHANGED CANDIDATE describe() PASS
V1 ISOLATION PASS

V2 sidecar run 005:
STOPPED FAIL-CLOSED BEFORE SERVER START

V2 sidecar run 005 evaluation:
RLY-S21-SIDECAR-EVAL-005 — ESCALATE

Run 005 findings:
OPENROUTER_API_KEY ABSENT FROM CODEX EXECUTION SHELL
ONE DIRECT V2 --version INVOCATION ESCAPED ISOLATION AND HIT EROFS
PROTECTED V1 METADATA REMAINED UNCHANGED
PROVIDER/MODEL CALLS NONE

V2 sidecar run 006:
STOPPED FAIL-CLOSED AT V2 SERVER STARTUP

V2 sidecar run 006 evaluation:
RLY-S21-SIDECAR-EVAL-006 — ESCALATE

Run 006 established:
.env CREDENTIAL DELIVERY PASS
WRAPPER-ENFORCED V2 ISOLATION PASS
V1 PROTECTED METADATA UNCHANGED
V2 VERSION/HASH PASS
SERVER STARTUP FAIL — EXIT 1 BEFORE READINESS
PROVIDER/MODEL AVAILABILITY NOT TESTED

Run 007:
STOPPED FAIL-CLOSED AT D21-05 PROMPT ADMISSION

Run 007 evaluation:
RLY-S21-SIDECAR-EVAL-007 — REWORK

Blocking findings:
LIVE V2 PROMPT REQUEST SCHEMA MISMATCH
DETERMINISTIC MOCK ENCODED SAME INCORRECT PROMPT CONTRACT
HTTP 400 PROMPT SCHEMA REJECTION MISCLASSIFIED AS AGENT_BLOCKED

Implementation rework successor:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

Independent implementation evaluation:
RLY-S21-EVAL-003 — ACCEPT

Successor exact-head CI:
37673385489 — SUCCESS

Run 008:
STOPPED FAIL-CLOSED AT D21-05 EXECUTION WAKE

Run 008 evaluation:
RLY-S21-SIDECAR-EVAL-008 — REWORK

Established live findings:
PROMPT SCHEMA PASS
PROMPT ADMISSION PASS
RESUME:false PRODUCES ADMIT-ONLY / NO EXECUTION WAKE
DETERMINISTIC MOCK MASKED ADMIT-ONLY SEMANTICS

Implementation rework successor:
f9a4790c6343561b462d521008c197d776e9ebcf

Independent implementation evaluation:
RLY-S21-EVAL-004 — ACCEPT

Successor exact-head CI:
37682777614 — SUCCESS

Run 009:
STOPPED FAIL-CLOSED AT D21-05 RUNTIME FAILURE

Run 009 evaluation:
RLY-S21-SIDECAR-EVAL-009 — ESCALATE

Established:
PROMPT SCHEMA PASS
PROMPT ADMISSION PASS
EXECUTION WAKE PASS
RUNTIME_INVOCATION NONE PASS
TERMINAL OPENCode FAILED BEFORE FIXTURE MUTATION
ZERO REPORTED USAGE
EXACT FAILURE CAUSE NOT ESTABLISHED

Run 009 diagnostic evaluation:
RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED

Established failure:
PROVIDER_MODEL_NOT_FOUND
SessionRunnerModel.ModelUnavailableError
provider.no-route
Model unavailable: openrouter/google/gemini-3.8-flash

Candidate:
UNCHANGED — RLY-S21-EVAL-004 — ACCEPT

Run 010:
STOPPED FAIL-CLOSED BEFORE D21

Run 010 evaluation:
RLY-S21-SIDECAR-EVAL-010 — ESCALATE

Failure gate:
AUTHENTICATED /api/health HTTP 503
healthy=false

Candidate:
UNCHANGED — RLY-S21-EVAL-004 — ACCEPT

Run 010r1:
STOPPED FAIL-CLOSED BEFORE D21

Run 010r1 evaluation:
RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE

Established:
HEALTH READINESS PASS
CANDIDATE DESCRIBE PASS
EXACT MODEL CATALOG PASS
OPENROUTER MODEL PACKAGE PASS
PROVIDER ENDPOINT HTTP 200
PROVIDER READINESS FIELDS NOT PROVEN FROM RETAINED SANITIZED RESPONSE

Provider-preflight diagnostic evaluation:
RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001 — CORRECT_RUN_010_PROVIDER_PREFLIGHT

Established:
GATE_OVERSPECIFIED
EXACT BETA PROVIDER SCHEMA USES id / activation / package
NO provider.active BOOLEAN
NO nested provider.api.type / provider.api.package
EXACT MODEL SCHEMA USES providerID / enabled / status / optional package

Run 010r2:
STOPPED FAIL-CLOSED BEFORE D21

Run 010r2 evaluation:
RLY-S21-SIDECAR-EVAL-010R2 — ESCALATE

Established:
HEALTH PASS
CANDIDATE DESCRIBE PASS
MODEL-CATALOG REQUEST HTTP 400 DUE TO OPERATOR QUERY-SHAPE ERROR
NO PROVIDER/MODEL AVAILABILITY FINDING
NO PROMPT / NO INFERENCE

Run 010r3:
HISTORICAL REWORK FINDING AT D21-12

Cancellation successor:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Independent implementation evaluation:
RLY-S21-EVAL-005 — ACCEPT

Exact-head CI:
37873019090 — SUCCESS

Run 012r1:
STOPPED FAIL-CLOSED BEFORE READINESS

Run 012r1 evaluation:
RLY-S21-SIDECAR-EVAL-012R1 — ESCALATE

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49 — RLY-S21-EVAL-005 ACCEPT / UNCHANGED

Run 012r1 findings:
FIXTURE SOURCE SHA VALIDATION PASS
PROTECTED V1 ORDERING + FINAL ATTESTATION PASS
WRAPPER ISOLATION PASS
SINGLE SERVER LIFECYCLE PASS
LISTENER STARTUP FAILED WITH EPERM
NO SESSION / NO PROMPT / NO INFERENCE

Implementation rework:
NOT JUSTIFIED

Existing Human Authority:
RLY-S21-SIDECAR-AUTH-006 — REMAINS VALID / NO SCOPE EXPANSION

Corrective listener-preflight handoff:
RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001

Next attempt:
Run 012r2

Run 012r2:
STOPPED FAIL-CLOSED AT GENERIC LISTENER PREFLIGHT

Run 012r2 evaluation:
RLY-S21-SIDECAR-EVAL-012R2 — ESCALATE

Generic non-V2 socket creation:
EPERM (errno 1); bind/listen NOT REACHED

Host/container socket/listener restriction:
ESTABLISHED

OpenCode-specific listener defect:
NOT TESTED

Candidate:
4f785f08576e465cd0aa278f927fa4b7253e3f49 — RLY-S21-EVAL-005 ACCEPT / UNCHANGED

Relay candidate defect:
NO

Accepted design defect:
NO

Implementation defect:
NO

Provider/model defect:
NO

Implementation rework:
NOT JUSTIFIED

Existing Human Authority:
RLY-S21-SIDECAR-AUTH-006 — REMAINS VALID / NO SCOPE EXPANSION

Next attempt:
Run 012r3 — only in an execution environment with proven loopback socket create/bind/listen capability

Corrective execution-environment handoff:
RLY-S21-SIDECAR-RUN012-EXECUTION-ENV-HANDOFF-001

New Human Authority:
NOT REQUIRED IF THE AUTHORIZED SUBJECT AND SCOPE REMAIN UNCHANGED

Human technical acceptance:
NOT ELIGIBLE

Agent execution:
NOT AUTHORIZED
```

Slice 2.1 has a Human-accepted Agent Runtime Contract design and explicit implementation authority under `RLY-S21-IMPL-AUTH-001`. Candidate `c947cf607699707b8b56d22cbb9aab4b30a7bf4a` received `RLY-S21-EVAL-001 — REWORK`. Successor `ded3ed03b7070ea095a823129ebe44935cb57997` resolves those findings and received `RLY-S21-EVAL-002 — ACCEPT`. At that historical checkpoint, Human technical acceptance was pending the live OpenCode sidecar evidence gate; Run 012r3 later passed and Human technical acceptance was recorded as `RLY-S21-ACCEPT-001 — ACCEPTED`. Run 004 remains the successful live authenticated V2 compatibility checkpoint for the exact frozen candidate. Run 005 stopped before server startup because the Human-exported OpenRouter credential was absent from the actual Codex command-execution environment. In addition, one direct `opencode2 --version` invocation escaped the required disposable HOME/XDG envelope and received `EROFS` while attempting to open the protected V1 log; protected V1 executable/state metadata remained unchanged afterward. `RLY-S21-SIDECAR-EVAL-005 — ESCALATE` classifies both findings as operator/execution-environment defects, not Relay candidate or accepted-design defects. Run 006 passed credential-delivery and wrapper-isolation gates, but the isolated V2 server exited with code 1 before readiness. RLY-S21-SIDECAR-EVAL-006 — ESCALATE leaves the Relay candidate and accepted design unchanged. The Run-006 handoff omitted the explicit disposable-profile and OPENCODE_DB-parent creation required by Run 003; this procedural regression is established, while causality for the server exit is not yet proven. Run 007 passed startup, authenticated health, candidate describe, fixture binding, and session creation, then failed at D21-05 when the live beta rejected the candidate prompt body with HTTP 400 `Missing key at ["text"]` before provider inference. `RLY-S21-SIDECAR-EVAL-007 — REWORK` establishes a bounded OpenCode adapter implementation defect, not a design defect. The deterministic mock encoded the same wrong prompt contract, and the prompt 400 was also misclassified as `AGENT_BLOCKED`. Successor `5df1add9ed829a62a99d7f25f561a0f492ff5c73` resolves the bounded live prompt-mapping findings and received `RLY-S21-EVAL-003 — ACCEPT`; exact-head CI `37673385489` is green. Run 008 passed live prompt-schema compatibility and HTTP admission but exposed a second bounded adapter defect: normal `open_execution()` sends `resume: false`, which OpenCode V2 treats as durable admit-only behavior, so no execution wake/provider turn followed. `RLY-S21-SIDECAR-EVAL-008 — REWORK` establishes an implementation defect, not a design defect. The deterministic mock also masked the bug by emitting execution-like events after an admit-only request. Successor `f9a4790c6343561b462d521008c197d776e9ebcf` resolves the execution-wake and invocation-provenance findings and received `RLY-S21-EVAL-004 — ACCEPT`; exact-head CI `37682777614` is green. Run 009 live-confirmed the corrected prompt mapping, execution wake, and absence of fabricated invocation identity. OpenCode then entered execution and terminated `FAILED` before any fixture mutation, with zero reported usage. `RLY-S21-SIDECAR-EVAL-009 — ESCALATE` does not establish a Relay candidate or accepted-design defect because the sanitized evidence does not identify the underlying runtime/provider failure. The Run-009 diagnostic established exact-beta `SessionRunnerModel.ModelUnavailableError` / `provider.no-route` for `openrouter/google/gemini-3.8-flash`. `RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED` establishes a disposable OpenCode runtime/provider environment issue, not a Relay candidate or accepted-design defect. Candidate `f9a4790...` remains deterministically accepted. The disposable exact-beta environment correction succeeded: OpenCode now exposes active `openrouter` and exact model `google/gemini-3.8-flash` in its own catalog under the minimum non-secret provider/model configuration, with protected V1 unchanged and no prompt/inference. `RLY-S21-SIDECAR-ENV-EVAL-001 — READY_FOR_RUN_010_AUTHORIZATION` records the strongest non-inference readiness proof the beta exposes; it has no public non-inference execution-route resolver. Candidate `f9a4790...` remains unchanged and accepted. Run 010 recreated the fresh disposable profile and non-secret route configuration but stopped before candidate `describe()` and before D21 when authenticated `/api/health` returned HTTP 503 with `healthy=false`. `RLY-S21-SIDECAR-EVAL-010 — ESCALATE` establishes a pre-D21 disposable runtime/environment failure, not a Relay candidate or accepted-design defect. Candidate `f9a4790...` remains accepted under `RLY-S21-EVAL-004`. Run 010r1 cleared the corrected health gate and candidate `describe()`, and the exact model catalog showed `google/gemini-3.8-flash` enabled/active with the OpenRouter provider package. The provider list/detail calls returned HTTP 200, but the retained sanitized provider response did not prove the provider identity/readiness/package fields demanded by the handoff. `RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE` classifies this as a pre-D21 provider-preflight evidence/specification issue, not a Relay candidate or design defect and not a proven provider absence. The exact-beta provider-preflight diagnostic classified the gate as `GATE_OVERSPECIFIED`. `Provider.Info` exposes `id`, `activation` (`auto|enabled|disabled`), and root `package`; it does not expose provider `active` or nested `api.type/api.package`. `Model.Info` exposes the route-specific `providerID`, `enabled`, `status`, and optional package. `RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001 — CORRECT_RUN_010_PROVIDER_PREFLIGHT` therefore replaces impossible provider assertions with the strongest exact-beta predicate while preserving exact provider/model identity and the separate credential-presence gate. Run 010r2 passed health and candidate `describe()` but stopped before route readiness when the operator sent the model-catalog location in the wrong request shape, producing HTTP 400. `RLY-S21-SIDECAR-EVAL-010R2 — ESCALATE` establishes an operator/request-construction defect only; it establishes no provider/model availability, OpenCode runtime, Relay candidate, or design defect. Existing Human Authority remains valid because no prompt/inference or D21 work occurred. Run 010r3 finally reached the candidate end-to-end: exact route preflight passed, the fixture edit executed, denials/inspection/provenance passed through D21-11, and actual provider/model was `openrouter/google/gemini-3.8-flash`. D21-12 then exposed a bounded adapter defect: the exact beta returns successful HTTP 204 No Content for session interrupt, while candidate `f9a4790...` accepts only HTTP 200 and parses JSON, misclassifying 204 as `TRANSPORT`. Successor `4f785f08...` resolves the exact-beta cancellation mismatch by accepting only HTTP 204 No Content for interrupt success without JSON parsing, while preserving idempotent ack caching, exact binding, terminal handling, 403/404, timeout/transport normalization, and rejection of undeclared 2xx responses. `RLY-S21-EVAL-005 — ACCEPT` independently verifies the one-commit/two-file bounded diff and exact-head CI `37873019090 — SUCCESS`. Run 012r1 fixed the fixture-SHA and lifecycle discipline defects but stopped before readiness when the exact V2 server exited with `EPERM: operation not permitted, listen`. `RLY-S21-SIDECAR-EVAL-012R1 — ESCALATE` establishes a listener/startup environment failure, not a Relay candidate or accepted-design defect; no session, prompt, or inference occurred. Existing `RLY-S21-SIDECAR-AUTH-006` remains sufficient for fresh Run 012r2 under `RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001`. The retry adds a non-V2 generic loopback listener capability preflight before starting OpenCode, preserving the same exact candidate/runtime/provider scope. Run 012r2 then failed at generic socket creation with `EPERM` before bind/listen; `RLY-S21-SIDECAR-EVAL-012R2 — ESCALATE` establishes a host/container socket/listener restriction and leaves OpenCode-specific listener behavior untested. Candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49` remains `RLY-S21-EVAL-005 — ACCEPT / UNCHANGED`; no candidate, design, implementation, or provider/model defect is established, implementation rework is not justified, and Human technical acceptance remains ineligible. `RLY-S21-SIDECAR-RUN012-EXECUTION-ENV-HANDOFF-001` targets Run 012r3 under the unchanged `RLY-S21-SIDECAR-AUTH-006`, requiring a fresh execution environment that passes the generic loopback socket create/bind/listen preflight. Run 012r3 was later executed after this governance checkpoint was canonical and its exact-head CI succeeded; it received `RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT`, followed by Human technical acceptance `RLY-S21-ACCEPT-001 — ACCEPTED`. This was a historical instruction and no longer applies.


## Current Slice 2.1 closed state

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

Roadmap re-baseline:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Slice 1.8:
COMPLETE / ACCEPTED / CLOSED — RLY-S18-EVAL-002 — ACCEPT / RLY-S18-ACCEPT-001 — ACCEPTED / RLY-S18-CLOSE-EVAL-001 — ACCEPT / RLY-S18-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE 0946d083b1bc1ccd7773f709efacb04a0c00aacc

Slice 1.9 — Human Decision Support and Governance Review Surface:
COMPLETE / ACCEPTED / CLOSED — RLY-S19-CLOSE-EVAL-002 — ACCEPT / RLY-S19-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE e8dd2970df445f39954be19dea7ee8241294f44a

Slice 1.10 — Canonical Source and Promotion Enforcement:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.2:
COMPLETE / ACCEPTED / CLOSED

Slice 2.3:
COMPLETE / ACCEPTED / CLOSED

Slice 2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

The first independent closure evaluation returned `RLY-S21-CLOSE-EVAL-001 — REWORK` on stale projection wording. The corrective projections were accepted by `RLY-S21-CLOSE-EVAL-002 — ACCEPT`, authorizing canonical closure and promotion under `RLY-S21-CLOSE-AUTH-001`.

# 2. Slice 1.5 authority and accepted design

```text
Slice:
1.5 — Board Projection

Opening authority:
RLY-S15-OPEN-001

Opening baseline:
e44d63c15b7a4941146db5ad42bfcd414b71b444

Design authorization:
RLY-S15-DESIGN-AUTH-001 — AUTHORIZED

Human-authorized design subject baseline:
359cd61f0c05815390a6822739c0c68d3f020c32

Revision 1:
e921c2446f7770042a77c2f78e5f9c4af62e204b

Revision 2:
23199dbc8342c0f04542998bfd738e4d7d79ee23

Revision 3 / exact accepted design head:
25aa5c7dccf9b1b856344e5d2c60fa621de8aa9b

Prior independent design evaluation:
RLY-S15-DESIGN-EVAL-001 — REVISE

Current independent design evaluation:
RLY-S15-DESIGN-EVAL-002 — ACCEPT

Human design acceptance:
RLY-S15-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authorization:
RLY-S15-AUTH-001 — AUTHORIZED

Implementation baseline:
2075be41962591552eded0597e243f0c1754b27f

Accepted implementation candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED

Finalization and closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Canonical closure commit promoted to main:
45a3acbc5a26c618176a2d5da32a70b67adb9883

Preferred implementation role/model:
IMPLEMENTATION_AGENT — GPT-5.6 Luna
```

Roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

# 3. Completed Slice 1.5 implementation boundary

The authorized read-only Board Projection implementation is complete at the accepted candidate above.

The implementation added:

- typed immutable board projection models;
- deterministic Project index, Project board, and Slice detail projection service;
- narrow read-only SQLite transaction/read helpers with no migration;
- request-scoped SQLite connection ownership;
- FastAPI + Uvicorn as direct runtime dependencies;
- optional `httpx` as a dev/test-only dependency if required for HTTP-level tests;
- simple server-rendered HTML/CSS;
- bounded local `relay-board` launcher if needed;
- deterministic tests and implementation evidence.

The implementation preserves:

- exact lifecycle authority and display-only lanes;
- READY distinct from authorization;
- gate-level evaluation observations only;
- full persisted evaluation-context identity for duplicate/conflict integrity;
- `MATCHING_DURABLE_BASIS` / `STALE_DURABLE_BASIS` semantics;
- one SQLite connection and one read snapshot per request;
- loopback-default read-only serving;
- disabled framework-generated OpenAPI/Swagger/ReDoc routes;
- no board mutation, React, final JSON API, async persistence, connection pooling, schema migration, repository/provider mutation, Slice 1.6, or agent execution.

# 4. Preserved Slice 1.4 accepted state

```text
Canonical rework baseline:
dfe6c20c8f65b42fe69b7d315956a91d2a29487c

Prior implementation candidate:
e5cfc5aeeb4abad2a231dd0f923af3aff13e2c6d

Prior implementation evaluation:
RLY-S14-EVAL-001 — REWORK

Accepted technical result:
ae582c52ec4a6451b54e9d6e018932e93e72e013

Independent closure evaluation:
RLY-S14-CLOSE-EVAL-001 — ACCEPT

Canonical closure head:
e44d63c15b7a4941146db5ad42bfcd414b71b444
```

# 5. Slice 1.6 accepted design

```text
Slice:
1.6 — Human Authorization and Decision Gates

Opening authority:
RLY-S16-OPEN-001

Canonical repository head at opening:
d757885ff417cd573b2d3f566d778dd4a37520b3

Human-authorized design subject baseline:
e9c6e3a5cc7592764bf0ac4932a2ae2659644027

Design authorization:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Authority-recording design parent:
e4923c837f20de35eb96cd1caf615b86860d9222

Revision 1:
f3a0fa7d9cc5b344399c070406353e1107ec30ff

Independent design evaluation 1:
RLY-S16-DESIGN-EVAL-001 — REVISE

Revision 2 amendment:
9a114b81f4347df10db7dfcb75677a606f18262e

Independent design evaluation 2:
RLY-S16-DESIGN-EVAL-002 — REVISE

Revision 3 amendment / exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent combined design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S16-DESIGN-ACCEPT-001 — ACCEPTED

Human design acceptance record commit:
0d23067c96eb9f3cec0ea3a3fa21b2fa605e4de1
```

The accepted Slice 1.6 design preserves the existing Relay governance model and defines the minimum Human Authority product seam. It requires exact action-basis binding, deterministic durable human-evidence projection, atomic successor gate-evaluation observations after gate-affecting human mutations, and explicit separation between human decision evidence and governed lifecycle execution.

The accepted design keeps `BLOCK`, `PAUSE`, and `DEFER` as orthogonal blockage controls; requires `ADVANCE` and `CANCEL` to execute only exact current GREEN gates; keeps the local server-rendered FastAPI board and request-scoped SQLite architecture; requires no new schema migration or runtime dependency; and reserves transition to `ACCEPTED`, manual evaluation, technical acceptance, and accepted-baseline promotion for Slice 1.7.

# 6. Current authority boundary

```text
Current finalization gate:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE

Accepted technical candidate:
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Human technical acceptance:
RLY-S15-ACCEPT-001 — ACCEPTED

Finalization / closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

React frontend:
DEFERRED / NOT AUTHORIZED IN SLICE 1.5

Slice 1.6:
COMPLETE / ACCEPTED / CLOSED

Slice 1.6 design authorization:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Slice 1.6 design:
ACCEPTED

Exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
RLY-S16-DESIGN-ACCEPT-001 — ACCEPTED

Slice 1.6 implementation:
COMPLETE / TECHNICALLY ACCEPTED — RLY-S16-AUTH-001

Authorized implementation baseline:
7bb7363375cc3cc3ac26758741ac9f2c6ca991e3

Prior implementation candidate:
c1fbad66cbede4e16cb39b5065426656df4cfb3a

Prior implementation evaluation:
RLY-S16-EVAL-001 — REWORK

Accepted technical candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

Independent implementation evaluation:
RLY-S16-EVAL-002 — ACCEPT

Human technical acceptance:
RLY-S16-ACCEPT-001 — ACCEPTED

Human technical acceptance commit:
b3fb25d23121ca9a249c56376a8f208bbaf6a1d1

Finalization / closure authority:
RLY-S16-CLOSE-AUTH-001 — AUTHORIZED

Finalization authority commit:
4b5e32844753224fd2ac9f8c0be475b67ea8f6a8

Finalization branch:
finalization/1.6-human-authorization-decision-gates

Finalization handoff commit:
141367c935fbc28822dc79bc1c82b06b1bb2bef2

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

Implementation handoff:
docs/reviews/SLICE_1_6_IMPLEMENTATION_HANDOFF.md

Slice 1.7:
COMPLETE / ACCEPTED / CLOSED

Opening authority:
RLY-S17-OPEN-001

Design authorization:
RLY-S17-DESIGN-AUTH-001 — AUTHORIZED

Accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Independent design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT

Design evaluation record commit:
10afbeac26bbd2d7de9021e09752a5e8eaf8539b

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Design acceptance record commit:
9bbf67d9f49c1a81b0a07707f26c0c352d4ef03c

Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Accepted implementation candidate:
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

Preferred implementation model:
GPT-5.6 Luna

Executing implementation model:
Codex / GPT-6 family; exact runtime variant not exposed

Schema migration:
Version 5 — slice_results and manual_evaluations only

Runtime dependencies:
UNCHANGED

Phase 1 M0 viability gate:
ACCEPTED / HUMAN-ACCEPTED — RLY-P1-M0-ACCEPT-001

Roadmap re-baseline:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Slice 1.8:
COMPLETE / ACCEPTED / CLOSED — RLY-S18-EVAL-002 — ACCEPT / RLY-S18-ACCEPT-001 — ACCEPTED / RLY-S18-CLOSE-EVAL-001 — ACCEPT / RLY-S18-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE 0946d083b1bc1ccd7773f709efacb04a0c00aacc

Slice 1.9:
COMPLETE / ACCEPTED / CLOSED — RLY-S19-CLOSE-EVAL-002 — ACCEPT / RLY-S19-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE e8dd2970df445f39954be19dea7ee8241294f44a

Phase 2:
OPEN — RLY-P2-OPEN-001

Slice 2.1:
COMPLETE / ACCEPTED / CLOSED

Slice 2.2:
COMPLETE / ACCEPTED / CLOSED

Slice 2.3:
COMPLETE / ACCEPTED / CLOSED

Slice 2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

Slice 1.6 implementation is complete and technically accepted at `a62493c733f67a5ce1b2fe5c53892d1833e4c615`, following the preserved `RLY-S16-EVAL-001 — REWORK` and `RLY-S16-EVAL-002 — ACCEPT` history. Human technical acceptance is recorded as `RLY-S16-ACCEPT-001`. Independent closure evaluation `RLY-S16-CLOSE-EVAL-001 — ACCEPT` closed the slice; canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. The implementation adds no schema migration or new dependency.

Slice 1.7 is complete, accepted, and closed following independent closure evaluation `RLY-S17-CLOSE-EVAL-001 — ACCEPT` of closure-ready candidate `d7c3876754804ea0f889ec09133b99f569398f1e`. Its combined Revision 1–4 design, accepted implementation `2fc1a762e17f45fb1a3d866d8100f2c0c284b435`, REWORK, REWORK, ACCEPT evaluation history, and Human technical acceptance `RLY-S17-ACCEPT-001` remain preserved. Canonical closure commit `5d6773bd5f634246c026b2964ca21e7083a966a1` was promoted to `main`. The implementation includes only authorized migration v5 (`slice_results` and `manual_evaluations`); dependencies and lifecycle/governance semantics are unchanged. Phase 1 M0 is Human-accepted; Phase 1 is an accepted baseline under active hardening; Phase 2 is open under RLY-P2-OPEN-001; agent execution remains unauthorized.

**Unblocked ≠ authorized.**
