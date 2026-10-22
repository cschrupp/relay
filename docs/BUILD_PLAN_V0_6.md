# Relay — Build Plan and Development Roadmap

**Version:** 0.6  
**Status:** Current living implementation plan — Slice 2.2 implementation is COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY under `RLY-S22-CLOSE-AUTH-001`; independent closure evaluation is PENDING; strict B0 remains blocked
**Document class:** Living canonical projection
**Canonical key:** `build-plan`
**Supersedes:** v0.5 at `docs/BUILD_PLAN_V0_5.md`  
**Parent document:** *Relay — Product and Technical Proposal v0.5*  
**Date:** October 2026

---

# 0. CURRENT ROADMAP — Slice 2.2 Closure-Ready

**Controlling summary:** this section is the current roadmap summary. Older detailed sections below are retained for historical traceability; where an older status statement conflicts with this section, this section controls until the next accepted roadmap projection.

```text
Phase 1 foundation:
Slices 1.1–1.9                  COMPLETE / ACCEPTED / CLOSED

Slice 1.10 core:
Canonical source/promotion      IMPLEMENTED / HUMAN ACCEPTED
Dogfood V1 control surface      COMPLETE / HUMAN ACCEPTED
PG1 pre-genesis representation COMPLETE / HUMAN ACCEPTED
B0 Rev3 design                  HUMAN ACCEPTED

B0 evidence preparation:
independent evaluation          ACCEPT
usable Genesis package          BLOCKED
blocking facts                  7
Bootstrap V2                    NOT CREATED

B0-F Bootstrap Engine Finish:
design                          HUMAN ACCEPTED
implementation                 COMPLETE / HUMAN ACCEPTED
behavior                        READ-ONLY LOCAL REPOSITORY INSPECTION
strict importer / database      NOT IMPLEMENTED / NOT AUTHORIZED

B1 Project Discovery & Human Intake:
design                          HUMAN ACCEPTED
implementation                 COMPLETE / HUMAN ACCEPTED
accepted candidate              22fb742965ed6424a18275b4234e1399021d4aed
real-world dogfood              AUTHORIZED / NOT EXECUTED BEFORE ACCEPTANCE

B2 Existing Project Adoption / T1 Genesis:
design                          COMPLETE / HUMAN ACCEPTED
implementation                 COMPLETE / HUMAN ACCEPTED
actual adoption / T1            COMPLETE / HUMAN ACCEPTED
B3 design                       COMPLETE / HUMAN ACCEPTED
B3 Stage A tooling              COMPLETE / HUMAN ACCEPTED
B3 Stage B materialization      COMPLETE / HUMAN ACCEPTED
B4 design                       COMPLETE / HUMAN ACCEPTED
B4 read-only harness            COMPLETE / HUMAN ACCEPTED
B4 Attempt 006                  VALID / SEALED / AWAITING SEMANTIC EVALUATION
Slice 2.2 Role Contracts        OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY
independent closure evaluation  PENDING

Phase 2:
2.1 Agent Runtime Contract      COMPLETE / ACCEPTED / CLOSED
2.3–2.4                         PLANNED / NOT OPEN / NOT AUTHORIZED
```

## Product decision

Relay will not treat legacy-project onboarding as historical reconstruction.

B0-F supplies read-only repository discovery without requiring Relay state. Strict B0 bootstrap remains blocked until its exact historical identity, origin, and definition evidence exists. The planned B1/B2 path is forward-looking adoption: inspect the current repository, ask the Human for semantic facts and objectives that code cannot establish, establish an operational T1, and govern continuation from that point forward.

See [Existing Project Adoption and Forward-Governance Strategy](strategy/EXISTING_PROJECT_ADOPTION_AND_FORWARD_GOVERNANCE.md).

## Planned execution sequence

```text
B0-F  Bootstrap Engine Finish — COMPLETE / HUMAN ACCEPTED
  -> B1 Project Discovery & Human Intake — COMPLETE / HUMAN ACCEPTED
  -> B2 Existing Project Adoption / T1 Genesis — IMPLEMENTATION COMPLETE / HUMAN ACCEPTED
       real Relay adoption/T1 remains behind a separate exact execution gate
  -> B3 Forward Re-baseline / First Governed Work
  -> B4 Relay Dogfood Acceptance
  -> 2.2 Role Contracts — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY
  -> 2.3 Context / Work-Packet Contract
  -> 2.4 Execution Workspace Authority
  -> Phase 3 governed autonomous engineering loop
```

B0-F is COMPLETE / HUMAN ACCEPTED under `RLY-S110-DOGFOOD-B0F-IMPL-ACCEPT-001`, with exact accepted candidate `65bf57f69f8de4526d080e03da9f796bc20f46ec`. B1 design was opened under `RLY-S110-DOGFOOD-B1-DESIGN-AUTH-001` at `4283c2e55da17af8b1c07af6b554a581028e51db`. Revision 1 received `RLY-S110-DOGFOOD-B1-DESIGN-EVAL-001 — REWORK`; the Revision 2 amendment closed F001/F002 and the composite design was independently accepted by `RLY-S110-DOGFOOD-B1-DESIGN-EVAL-002 — ACCEPT`. The Human accepted exact composite candidate `837edeae8bf36c414e78aa7c68af708590b9e90b` under `RLY-S110-DOGFOOD-B1-DESIGN-ACCEPT-001`. B1 implementation is COMPLETE / HUMAN ACCEPTED under `RLY-S110-DOGFOOD-B1-IMPL-ACCEPT-001` at exact candidate `22fb742965ed6424a18275b4234e1399021d4aed`, after `RLY-S110-DOGFOOD-B1-IMPL-EVAL-001 — REWORK` and `RLY-S110-DOGFOOD-B1-IMPL-EVAL-002 — ACCEPT`. Real-world dogfood was authorized but no completed dogfood result is recorded before acceptance. B2 Revision 1 plus the Revision 2 Integrity Amendment is independently accepted and Human-accepted at composite candidate `80b1f77c4d4cd1f3303b4a1072a46b0cfb605621` under `RLY-S110-DOGFOOD-B2-DESIGN-ACCEPT-001`, following `RLY-S110-DOGFOOD-B2-DESIGN-EVAL-002 — ACCEPT`. B2 implementation is independently accepted under `RLY-S110-DOGFOOD-B2-IMPL-EVAL-002` and Human-accepted under `RLY-S110-DOGFOOD-B2-IMPL-ACCEPT-001` at exact candidate `0b3c07dc41d4a0cb81749e8c00a3d006b9645097`. The authorized real Relay B2 adoption executed from clean HEAD `be1dd6f479d601c7ae2eea3985675f53ab748637` and is independently accepted under `RLY-S110-DOGFOOD-B2-ADOPTION-EVAL-001`. T1 is `2026-10-20T03:27:54.511113Z`; the external operational database is published and verified. Human result acceptance is recorded under `RLY-S110-DOGFOOD-B2-ADOPTION-ACCEPT-001`. B2 real adoption is complete. B3 design is OPEN / AUTHORIZED under `RLY-S110-DOGFOOD-B3-DESIGN-AUTH-001`. The Human-directed first governed work target is Slice 2.2 Role Contracts with authorized-work exhaustion integrated. B3 operational materialization and B4 are separately governed. Slice 2.2 implementation is accepted at `4400bd1da0db04e41077c3a6ed1c16d258104ba5`; closure evaluation is pending.

## Anti-drift guardrail

Governance hardening must serve delivery. As a planning target, product/code/test/integration work should normally account for at least two-thirds of active engineering effort. New governance work must name the concrete capability it unblocks or the observed integrity/security failure it fixes. If governance/documentation dominates two consecutive increments without shipping or unblocking product capability, stop and require explicit Human roadmap review.

The live execution checklist is [docs/TODO.md](TODO.md).

## Documentation synchronization rule

Every accepted increment that changes current project state, roadmap/frontier, planned slice sequence, product direction, major architecture, blockers, or the next Human action must update the corresponding living documents in the same increment. At minimum, closeout checks `docs/CURRENT_BASELINE.md`, `docs/BUILD_PLAN_V0_6.md`, and `docs/TODO.md`. Strategy/architecture documents are updated when their underlying direction changes. Immutable historical records are preserved rather than rewritten. Documentation freshness is part of increment closeout, not a separate governance phase.


---

# 1. Current project state

```text
Phase 1 — DETERMINISTIC GOVERNANCE FOUNDATION
ACCEPTED BASELINE / HARDENING ACTIVE

Slices 1.1–1.7: COMPLETE / ACCEPTED / CLOSED
Slice 1.8 — Governance Assurance Reference Model:
  OPEN; RLY-S18-OPEN-001; RESUMED under RLY-S18-RESUME-001;
  DESIGN ACCEPTED under RLY-S18-DESIGN-ACCEPT-001;
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
  PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 2: OPEN; Slice 2.1 COMPLETE / ACCEPTED / CLOSED;
  2.2 OPEN / IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY;
  2.3–2.4 PLANNED / NOT OPEN / NOT AUTHORIZED
Phase 3: 3.1 FUTURE / NOT OPEN / NOT AUTHORIZED
Prerequisites: 1.8, 1.9, 1.10, 2.2, 2.3, 2.4, and explicit Phase 3 opening
Real-project agent execution: NOT AUTHORIZED
```

```text
Phase 0:
COMPLETE / CLOSED

Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Slices 1.1–1.4:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE / ACCEPTED

Independent implementation evaluation:
RLY-S15-EVAL-001 — ACCEPT

Finalization / closure authorization:
RLY-S15-CLOSE-AUTH-001 — AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Slice 1.6:
COMPLETE / ACCEPTED / CLOSED

Accepted technical candidate:
a62493c733f67a5ce1b2fe5c53892d1833e4c615

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

Slice 1.7:
COMPLETE / ACCEPTED / CLOSED

Accepted combined design head:
d2f4cc20ae4d85f267b11e8f3ef3f892bceee73b

Independent design evaluation:
RLY-S17-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S17-DESIGN-ACCEPT-001 — ACCEPTED

Implementation authority:
RLY-S17-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
4717d44a05231fc1bd5f9fbd057714075d69c20b

Accepted technical candidate:
2fc1a762e17f45fb1a3d866d8100f2c0c284b435

Prior implementation evaluations:
RLY-S17-EVAL-001 — REWORK
RLY-S17-EVAL-002 — REWORK

Independent implementation evaluation:
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

Implementation:
COMPLETE / TECHNICALLY ACCEPTED

Accepted schema migration:
VERSION 5 — slice_results + manual_evaluations ONLY

Runtime dependencies:
UNCHANGED

Phase 1 M0 viability gate:
ACCEPTED / HUMAN-ACCEPTED — RLY-P1-M0-ACCEPT-001

Roadmap re-baseline authority:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Assurance / decision-support re-baseline:
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001 — AUTHORIZED
Slice 1.8 pause history: RLY-S18-PAUSE-001 — SATISFIED BY CANONICAL REBASELINE PROMOTION
Slice 1.8 resume: RLY-S18-RESUME-001 — RESUMED
Supplemental design authority: RLY-S18-DESIGN-AUTH-002 — AUTHORIZED FOR REVISION 2
Combined design evaluation: RLY-S18-DESIGN-EVAL-002 — ACCEPT
Human design acceptance: RLY-S18-DESIGN-ACCEPT-001 — ACCEPTED
Implementation authority: RLY-S18-IMPL-AUTH-001 — AUTHORIZED

Slice 1.8 — Governance Assurance Reference Model:
COMPLETE / ACCEPTED / CLOSED — RLY-S18-EVAL-002 — ACCEPT / RLY-S18-ACCEPT-001 — ACCEPTED / RLY-S18-CLOSE-EVAL-001 — ACCEPT / RLY-S18-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE 0946d083b1bc1ccd7773f709efacb04a0c00aacc

Slice 1.9 — Human Decision Support and Governance Review Surface:
COMPLETE / ACCEPTED / CLOSED — RLY-S19-CLOSE-EVAL-002 — ACCEPT / RLY-S19-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE e8dd2970df445f39954be19dea7ee8241294f44a

Slice 1.10 — Canonical Source and Promotion Enforcement:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 2:
OPEN — RLY-P2-OPEN-001

Slice 2.1 — Agent Runtime Contract:
COMPLETE / ACCEPTED / CLOSED
Design: RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED
Implementation: COMPLETE / TECHNICALLY ACCEPTED
Candidate: 4f785f08576e465cd0aa278f927fa4b7253e3f49
Deterministic implementation evaluation: RLY-S21-EVAL-005 — ACCEPT
Live sidecar evaluation: RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT
Human technical acceptance: RLY-S21-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S21-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: RLY-S21-CLOSE-EVAL-002 — ACCEPT

Slice 2.2 — Role Contracts:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY
Accepted implementation: 4400bd1da0db04e41077c3a6ed1c16d258104ba5
Effective quality-repaired subject: 07bda21295d87602e2a2234622478551920c5014
Independent implementation evaluation: RLY-S22-IMPL-EVAL-003 — ACCEPT
Human technical acceptance: RLY-S22-ACCEPT-001 — ACCEPTED
Finalization / closure authority: RLY-S22-CLOSE-AUTH-001 — AUTHORIZED
Independent closure evaluation: PENDING

Slice 2.3 — Context and Work-Packet Contract:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.4 — Execution Workspace Authority:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

# 1A. Phase model after the M0 viability gate

M0 remains a **viability / continued-investment gate**, not a declaration that every Phase 1 surface is production-complete.

```text
Phase 1 — deterministic governance foundation
ACCEPTED BASELINE / HARDENING ACTIVE
        |
        +-- M0 viability: PASSED / HUMAN-ACCEPTED
        +-- Slices 1.1-1.7: CLOSED
        +-- 1.8 Governance Assurance Reference Model      COMPLETE / ACCEPTED / CLOSED
        +-- 1.9 Human Decision Support                   COMPLETE / ACCEPTED / CLOSED
        +-- 1.10 Canonical Source / Promotion Enforcement PLANNED
                 |
                 +-------------------------------+
                                                 |
                                                 v
Phase 2 — provider and agent foundation
OPEN
        |
        +-- 2.1 Agent Runtime Contract            CLOSED
        +-- 2.2 Role Contracts                    OPEN / CLOSURE-READY
        +-- 2.3 Context / Work-Packet Contract    PLANNED
        +-- 2.4 Execution Workspace Authority     PLANNED
                                                 |
                                                 v
Phase 3 — first governed autonomous engineering loop
NOT OPEN / NOT AUTHORIZED
```

Phase 1 hardening and Phase 2 remain concurrent at the phase level. Slice 2.2 is closure-ready; independent closure evaluation is pending before any later slice proceeds.

Any Phase 1 deficiency that threatens authority integrity, deterministic state, provenance, Human control, evaluator independence, promotion integrity, or fail-closed behavior blocks dependent Phase 2/3 work.

# 1B. Re-baselined development sequence

```text
1.8  Governance Assurance Reference Model — COMPLETE / ACCEPTED / CLOSED — RLY-S18-EVAL-002 — ACCEPT / RLY-S18-ACCEPT-001 — ACCEPTED / RLY-S18-CLOSE-EVAL-001 — ACCEPT / RLY-S18-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE 0946d083b1bc1ccd7773f709efacb04a0c00aacc
     -> closed after independent closure evaluation RLY-S18-CLOSE-EVAL-001 — ACCEPT

1.9  Human Decision Support and Governance Review Surface — COMPLETE / ACCEPTED / CLOSED — RLY-S19-CLOSE-EVAL-002 — ACCEPT / CLOSURE CANDIDATE e8dd2970df445f39954be19dea7ee8241294f44a
     -> future legibility and decision-scoped review design

1.10 Canonical Source and Promotion Enforcement — PLANNED / NOT AUTHORIZED
     -> make SCM/promotion enforcement match declared governance

2.2  Role Contracts
     -> define who may do what, with explicit non-authority

2.3  Context and Work-Packet Contract
     -> define exact authorized execution input

2.4  Execution Workspace Authority
     -> define where/how the authorized role may execute

3.1  Coding Agent Execution
     -> first governed autonomous implementation execution

Phase 3.1 prerequisites are the complete chain: 1.8 Governance Assurance, 1.9 Human Decision Support, 1.10 Source/Promotion Enforcement, 2.2 Role Contracts, 2.3 Context/Work Packets, 2.4 Workspace Authority, and explicit Phase 3 opening.

## 1B.1 Strategic control-plane amendment — planned ownership

This documentation-only amendment was authorized by `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001` and has been canonically promoted. Slice 1.8 is now resumed under `RLY-S18-RESUME-001`; Design Revision 1 remains byte-preserved and normative where not explicitly amended by the accepted Revision 2 + Rework 1 chain; acceptance applies to the combined design, not Revision 1 alone. Revision 2 and Rework 1 have been independently accepted under `RLY-S18-DESIGN-EVAL-002` and Human-accepted under `RLY-S18-DESIGN-ACCEPT-001`. Implementation is authorized under `RLY-S18-IMPL-AUTH-001` for documentation/governance-model hardening only; production/runtime code remains out of scope.

```text
Relay:
governance control plane for AI software engineering

Relay-native planning:
SUPPORTED / NOT REQUIRED

Future external planning adapters:
PLANNED / NOT IMPLEMENTED / DO NOT IMPORT AUTHORITY

GovernanceProfile:
SLICE 1.8 SEMANTICS DOCUMENTED / NOT EXECUTABLE

Protected Verification Assets:
SLICE 1.8 SEMANTICS DOCUMENTED; FUTURE 2.2 ROLE AUTHORITY;
2.3 EXACT REFERENCES; 2.4 ENFORCEMENT; 3.1 RESTRICTED EXECUTION

GovernanceEffectivenessTelemetry:
FUTURE NON-AUTHORITATIVE MEASUREMENT; NOT IMPLEMENTED

Competitive validation:
PLANNED RESEARCH ONLY / NOT EXECUTED
```

Future ownership direction:

- **1.8** documents GovernanceProfile semantics and risk/profile binding, prospective escalation/downgrade authority, `RELAY_GOVERNANCE_PROFILE_BOUND`, Protected Verification Asset designation and `RELAY_VERIFICATION_ASSETS_PROTECTED`, governance telemetry's non-authority boundary, and workflow-agnostic governance. No profile taxonomy or final scoring formula is frozen.
- **1.9** has delivered the accepted Decision Support design and implementation, including Decision Cards and required-gate presentation. Additional dashboard or governance-effectiveness telemetry UX remains future work and is not authorized.
- **1.10** should define profile-selected promotion predicates, including required evidence/evaluation, Human acceptance and promotion authority, parent freshness, and protected-verification evidence. The promotion executor cannot create policy or authority.
- **2.2** should define profile-required role separation and verification-asset read/create/modify/approve/evaluate permissions; role, actor identity, runtime/model identity, authority, and capability remain distinct.
- **2.3** should define ContextManifest and interoperable `PlanningArtifactSourceRef`, `PlanningArtifactAdapter`, and `NormalizedEngineeringIntent`, preserving source and adapter identity/version, digest, mapping diagnostics, unknown required fields, and exact accepted references. Normalization does not authorize a Work Packet.
- **2.4** should define workspace enforcement for profile restrictions, protected asset paths, allowed/denied writes, network, credentials, and tools, with evidence for scope conformance, provenance sufficiency, asset protection, and fail-closed behavior.
- **3.1** should consume a normalized Relay Work Packet without hard-coding its upstream planning provider.

The external planning landscape includes different spec/change/task processes [SRC-GITHUB-SPEC-KIT-2026] [SRC-OPENSPEC-2026] [SRC-BMAD-METHOD-2026]. This informs interoperability planning only, not a comparative product claim.
```

No planned Slice is opened by roadmap placement.

## Slice 1.8 closure result

Status: **COMPLETE / ACCEPTED / CLOSED**. `RLY-S18-EVAL-002 — ACCEPT`; `RLY-S18-ACCEPT-001 — ACCEPTED`; `RLY-S18-CLOSE-EVAL-001 — ACCEPT`; `RLY-S18-CLOSE-AUTH-001 — AUTHORIZED`. Accepted technical candidate: `35046bb378808a1325ecb84eace5aacd3040ca98`; closure candidate: `0946d083b1bc1ccd7773f709efacb04a0c00aacc`.

Authority: `RLY-S18-IMPL-AUTH-001`; implementation start `a7cd87fea89e3b0273da1d0c0884336cc7857357`; accepted combined-design baseline `eae25f0837bbce435e54fc3437b502dea1224744`.

The consolidated [reference model](architecture/GOVERNANCE_ASSURANCE_REFERENCE_MODEL.md) contains all 17 native properties, exact subject/policy contracts, cross-cutting Decision Support, prospective GovernanceProfile rules, protected-asset mutation-authority separation, workflow neutrality, external mapping/freshness, and downstream ownership. Supporting documents provide [20 worked examples and 30 negative cases](architecture/GOVERNANCE_ASSURANCE_EXAMPLES.md) and [mapping/source traceability](references/GOVERNANCE_ASSURANCE_MAPPING_MATRIX.md). See the [implementation handoff](reviews/SLICE_1_8_IMPLEMENTATION_HANDOFF_REV2.md) for design coverage and quality evidence.

No runtime, production/test source, schema, dependency, workflow, or repository-setting change is included. Profiles remain non-executable; protected assets are not enforced; adapters and ContextManifest remain future; telemetry is not collected; the competitive experiment is not executed. Independent implementation evaluation, Human technical acceptance, and independent closure evaluation are accepted. Slice 1.8 is closed under the existing finalization authority. At the time of this Slice 1.8 record, Slices 1.9 and 1.10 had not opened. Current status: Slice 1.9 is COMPLETE / ACCEPTED / CLOSED after `RLY-S19-CLOSE-EVAL-001 — REWORK` and corrective `RLY-S19-CLOSE-EVAL-002 — ACCEPT` under `RLY-S19-CLOSE-AUTH-001`; closure candidate `e8dd2970df445f39954be19dea7ee8241294f44a`. Slice 1.10 remains PLANNED / NOT OPEN / NOT AUTHORIZED. Phase 3 and agent execution remain unauthorized.

# 1C. Slice 2.1 historical opening boundary

```text
RLY-S21-OPEN-001 — OPEN

Opening baseline:
eac62b054af3815cc179c95d0d31aa96f9a374e3

Design authorization:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

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

The combined Slice 2.1 Agent Runtime Contract design is Human-accepted, and implementation is explicitly authorized under `RLY-S21-IMPL-AUTH-001`. Candidate `c947cf607699707b8b56d22cbb9aab4b30a7bf4a` is preserved with `RLY-S21-EVAL-001 — REWORK`. Successor `ded3ed03b7070ea095a823129ebe44935cb57997` received `RLY-S21-EVAL-002 — ACCEPT`. At that historical checkpoint, Human technical acceptance was pending live OpenCode sidecar evidence; Run 012r3 later passed and Human technical acceptance was recorded as `RLY-S21-ACCEPT-001 — ACCEPTED`. Run 004 remains the successful live authenticated V2 compatibility checkpoint for the exact frozen candidate. Run 005 did not reach that checkpoint: the OpenRouter credential exported by the Human was absent from the actual Codex command-execution environment, and an inadvertent direct `opencode2 --version` invocation occurred before the required disposable HOME/XDG envelope. That invocation received `EROFS` while attempting to open the protected V1 log; subsequent metadata comparison showed the protected V1 executable and known persistent-state metadata unchanged. `RLY-S21-SIDECAR-EVAL-005 — ESCALATE` classifies these as operator/execution-environment defects, not Relay candidate or accepted-design defects. Run 006 passed credential-delivery and wrapper-isolation gates, but the isolated V2 server exited with code 1 before readiness. RLY-S21-SIDECAR-EVAL-006 — ESCALATE leaves the Relay candidate and accepted design unchanged. The Run-006 handoff omitted the explicit disposable-profile and OPENCODE_DB-parent creation required by Run 003; this procedural regression is established, while causality for the server exit is not yet proven. Run 007 passed startup, authenticated health, candidate describe, fixture binding, and session creation, then failed at D21-05 when the live beta rejected the candidate prompt body with HTTP 400 `Missing key at ["text"]` before provider inference. `RLY-S21-SIDECAR-EVAL-007 — REWORK` establishes a bounded OpenCode adapter implementation defect, not a design defect. The deterministic mock encoded the same wrong prompt contract, and the prompt 400 was also misclassified as `AGENT_BLOCKED`. Successor `5df1add9ed829a62a99d7f25f561a0f492ff5c73` resolves the bounded live prompt-mapping findings and received `RLY-S21-EVAL-003 — ACCEPT`; exact-head CI `37673385489` is green. The production diff is limited to the OpenCode prompt-body mapping and HTTP-400 normalization, with deterministic mock/regression updates only. Run 008 passed live prompt-schema compatibility and HTTP admission but exposed a second bounded adapter defect: normal `open_execution()` sends `resume: false`, which OpenCode V2 treats as durable admit-only behavior, so no execution wake/provider turn followed. `RLY-S21-SIDECAR-EVAL-008 — REWORK` establishes an implementation defect, not a design defect. The deterministic mock also masked the bug by manually emitting execution-like events after an admit-only request. Successor `f9a4790c6343561b462d521008c197d776e9ebcf` resolves the execution-wake and invocation-provenance findings and received `RLY-S21-EVAL-004 — ACCEPT`; exact-head CI `37682777614` is green. The production diff removes admit-only `resume:false` from normal `open_execution()` and stops fabricating `RuntimeInvocationRef` from the admitted inbox item's generic ID, with deterministic mock/regression updates only. Run 009 live-confirmed the corrected prompt mapping, execution wake, and absence of fabricated invocation identity. OpenCode then entered execution and terminated `FAILED` before any fixture mutation, with zero reported usage. `RLY-S21-SIDECAR-EVAL-009 — ESCALATE` does not establish a Relay candidate or accepted-design defect because the sanitized evidence does not identify the underlying runtime/provider failure. The Run-009 diagnostic established exact-beta `SessionRunnerModel.ModelUnavailableError` / `provider.no-route` for `openrouter/google/gemini-3.8-flash`. `RLY-S21-SIDECAR-DIAG-EVAL-001 — ENVIRONMENT_CORRECTION_REQUIRED` establishes a disposable OpenCode runtime/provider environment issue, not a Relay candidate or accepted-design defect. Candidate `f9a4790...` remains deterministically accepted. The disposable exact-beta environment correction succeeded: OpenCode now exposes active `openrouter` and exact model `google/gemini-3.8-flash` in its own catalog under the minimum non-secret provider/model configuration, with protected V1 unchanged and no prompt/inference. `RLY-S21-SIDECAR-ENV-EVAL-001 — READY_FOR_RUN_010_AUTHORIZATION` records the strongest non-inference readiness proof the beta exposes; it has no public non-inference execution-route resolver. Candidate `f9a4790...` remains unchanged and accepted. Run 010 recreated the fresh disposable profile and non-secret route configuration but stopped before candidate `describe()` and before D21 when authenticated `/api/health` returned HTTP 503 with `healthy=false`. `RLY-S21-SIDECAR-EVAL-010 — ESCALATE` establishes a pre-D21 disposable runtime/environment failure, not a Relay candidate or accepted-design defect. Candidate `f9a4790...` remains accepted under `RLY-S21-EVAL-004`. Run 010r1 cleared the corrected health gate and candidate `describe()`, and the exact model catalog showed `google/gemini-3.8-flash` enabled/active with the OpenRouter provider package. The provider list/detail calls returned HTTP 200, but the retained sanitized provider response did not prove the provider identity/readiness/package fields demanded by the handoff. `RLY-S21-SIDECAR-EVAL-010R1 — ESCALATE` classifies this as a pre-D21 provider-preflight evidence/specification issue, not a Relay candidate or design defect and not a proven provider absence. The exact-beta provider-preflight diagnostic classified the gate as `GATE_OVERSPECIFIED`. `Provider.Info` exposes `id`, `activation` (`auto|enabled|disabled`), and root `package`; it does not expose provider `active` or nested `api.type/api.package`. `Model.Info` exposes the route-specific `providerID`, `enabled`, `status`, and optional package. `RLY-S21-SIDECAR-PROVIDER-PREFLIGHT-DIAG-EVAL-001 — CORRECT_RUN_010_PROVIDER_PREFLIGHT` therefore replaces impossible provider assertions with the strongest exact-beta predicate while preserving exact provider/model identity and the separate credential-presence gate. Run 010r2 passed health and candidate `describe()` but stopped before route readiness when the operator sent the model-catalog location in the wrong request shape, producing HTTP 400. `RLY-S21-SIDECAR-EVAL-010R2 — ESCALATE` establishes an operator/request-construction defect only; it establishes no provider/model availability, OpenCode runtime, Relay candidate, or design defect. Existing Human Authority remains valid because no prompt/inference or D21 work occurred. Run 010r3 finally reached the candidate end-to-end: exact route preflight passed, the fixture edit executed, denials/inspection/provenance passed through D21-11, and actual provider/model was `openrouter/google/gemini-3.8-flash`. D21-12 then exposed a bounded adapter defect: the exact beta returns successful HTTP 204 No Content for session interrupt, while candidate `f9a4790...` accepts only HTTP 200 and parses JSON, misclassifying 204 as `TRANSPORT`. Successor `4f785f08...` resolves the exact-beta cancellation mismatch by accepting only HTTP 204 No Content for interrupt success without JSON parsing, while preserving idempotent ack caching, exact binding, terminal handling, 403/404, timeout/transport normalization, and rejection of undeclared 2xx responses. `RLY-S21-EVAL-005 — ACCEPT` independently verifies the one-commit/two-file bounded diff and exact-head CI `37873019090 — SUCCESS`. Run 012r1 fixed the fixture-SHA and lifecycle discipline defects but stopped before readiness when the exact V2 server exited with `EPERM: operation not permitted, listen`. `RLY-S21-SIDECAR-EVAL-012R1 — ESCALATE` establishes a listener/startup environment failure, not a Relay candidate or accepted-design defect; no session, prompt, or inference occurred. Existing `RLY-S21-SIDECAR-AUTH-006` remains sufficient for fresh Run 012r2 under `RLY-S21-SIDECAR-RUN012-LISTENER-PREFLIGHT-HANDOFF-001`. The retry adds a non-V2 generic loopback listener capability preflight before starting OpenCode, preserving the same exact candidate/runtime/provider scope. Run 012r2 then failed at generic socket creation with `EPERM` before bind/listen; `RLY-S21-SIDECAR-EVAL-012R2 — ESCALATE` establishes a host/container socket/listener restriction and leaves OpenCode-specific listener behavior untested. Candidate `4f785f08576e465cd0aa278f927fa4b7253e3f49` remains `RLY-S21-EVAL-005 — ACCEPT / UNCHANGED`, implementation rework is not justified, and Human technical acceptance remains ineligible. `RLY-S21-SIDECAR-RUN012-EXECUTION-ENV-HANDOFF-001` targets Run 012r3 under unchanged `RLY-S21-SIDECAR-AUTH-006`, with a fresh environment that passes the generic loopback socket create/bind/listen preflight. Run 012r3 was later executed after the canonical checkpoint and exact-head CI succeeded; it received `RLY-S21-SIDECAR-EVAL-012R3 — ACCEPT`, followed by Human technical acceptance `RLY-S21-ACCEPT-001 — ACCEPTED`. This was a historical instruction and no longer applies. Relay real-project agent execution remains unauthorized.


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

Slice 2.2:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

The first independent closure evaluation returned `RLY-S21-CLOSE-EVAL-001 — REWORK` on stale projection wording. The corrective projections were accepted by `RLY-S21-CLOSE-EVAL-002 — ACCEPT`, authorizing canonical closure and promotion under `RLY-S21-CLOSE-AUTH-001`.

# 2. Slice 1.5 authority

Human opening authority:

```text
RLY-S15-OPEN-001
```

Human design authorization:

```text
RLY-S15-DESIGN-AUTH-001
```

Human design acceptance:

```text
RLY-S15-DESIGN-ACCEPT-001 — ACCEPTED
```

Human-authorized design subject baseline:

```text
359cd61f0c05815390a6822739c0c68d3f020c32
```

Canonical roadmap objective:

> Build the first human-facing board strictly as a projection of governed state.

Authorized design role:

```text
Slice 1.5 Board Projection Architect — GPT-5.6 Sol
```

The design must preserve the board as a deterministic, read-only projection of governed state. Slice 1.5 does not own human authorization mutations, new lifecycle/governance semantics, repository/provider mutations, or agent execution.

The exact accepted technical candidate is:

```text
ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
```

The candidate was independently evaluated as ACCEPT under `RLY-S15-EVAL-001` and technically accepted under `RLY-S15-ACCEPT-001`.

# 3. Accepted foundation and preserved Slice 1.4 lineage

Slices 1.1–1.4 remain complete, accepted, and closed.

```text
Human-authorized subject baseline:
670996ec43d77526adb0ea540c81a57d6e83453b

Authority-recording design parent:
1eaece23e31d831bfd2b27e55a898df389cc45fc

Revision 1:
430b1e1ff5eb06c26d4c63225b455feda14b6710

Accepted Revision 2 design head:
f5a678da360b96701a1f9635d3703b49dc16e779

Implementation authorization:
RLY-S14-AUTH-001 — AUTHORIZED
```

Slice 1.4 accepted technical result:

```text
ae582c52ec4a6451b54e9d6e018932e93e72e013
```

Slice 1.4 closure evaluation:

```text
RLY-S14-CLOSE-EVAL-001 — ACCEPT
```

# 4. Slice 1.5 implementation and closure gates

The accepted design and bounded implementation are complete. Independent closure evaluation accepted the exact closure-ready candidate under `RLY-S15-CLOSE-EVAL-001`.

Current governed sequence:

```text
Accepted technical candidate: ff8df665f36afe60a2d44ee1ed0d735a0dcbc230
→ independent implementation evaluation: ACCEPT
→ Human technical acceptance: ACCEPTED
→ finalization / closure authorization: RLY-S15-CLOSE-AUTH-001
→ independent closure evaluation: RLY-S15-CLOSE-EVAL-001 — ACCEPT
→ Slice 1.5: COMPLETE / ACCEPTED / CLOSED
```

Passing CI is evidence; it does not constitute closure acceptance.

# 5. Current authority boundary

```text
Current finalization gate:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5:
COMPLETE / ACCEPTED / CLOSED

Slice 1.5 design:
ACCEPTED

Slice 1.5 implementation:
COMPLETE / ACCEPTED

Finalization / closure authorization:
AUTHORIZED

Independent closure evaluation:
RLY-S15-CLOSE-EVAL-001 — ACCEPT

Slice 1.6:
COMPLETE / ACCEPTED / CLOSED

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

Implementation:
COMPLETE / TECHNICALLY ACCEPTED

Accepted schema migration:
VERSION 5 — slice_results + manual_evaluations ONLY

Runtime dependencies:
UNCHANGED

Phase 1 M0 viability gate:
ACCEPTED / HUMAN-ACCEPTED — RLY-P1-M0-ACCEPT-001

Roadmap re-baseline:
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED

Slice 1.8:
COMPLETE / ACCEPTED / CLOSED — RLY-S18-EVAL-002 — ACCEPT / RLY-S18-ACCEPT-001 — ACCEPTED / RLY-S18-CLOSE-EVAL-001 — ACCEPT / RLY-S18-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE 0946d083b1bc1ccd7773f709efacb04a0c00aacc

Slice 1.9 — Human Decision Support and Governance Review Surface:
COMPLETE / ACCEPTED / CLOSED — RLY-S19-CLOSE-EVAL-002 — ACCEPT / RLY-S19-CLOSE-AUTH-001 — AUTHORIZED / CLOSURE CANDIDATE e8dd2970df445f39954be19dea7ee8241294f44a

Slice 1.10 — Canonical Source and Promotion Enforcement:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 2:
OPEN — RLY-P2-OPEN-001

Slice 2.1:
COMPLETE / ACCEPTED / CLOSED

Slice 2.2:
OPEN — IMPLEMENTATION COMPLETE / TECHNICALLY ACCEPTED / CLOSURE-READY

Slice 2.3:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Agent execution:
NOT AUTHORIZED
```

The accepted Slice 1.6 implementation adds the bounded Human Authority command seam to the existing server-rendered board. The exact candidate completed independent implementation evaluation and Human technical acceptance. Independent closure evaluation accepted the exact closure-ready candidate, and Slice 1.6 is closed. Canonical closure commit `9db044036e3591c53d777c81af58af252ebc69a7` was promoted to `main`. No schema migration or new dependency was introduced.

Slice 1.7 is complete, accepted, and closed following independent closure evaluation `RLY-S17-CLOSE-EVAL-001 — ACCEPT` of closure-ready candidate `d7c3876754804ea0f889ec09133b99f569398f1e`. The REWORK, REWORK, ACCEPT implementation evaluation history and Human technical acceptance `RLY-S17-ACCEPT-001` remain preserved with exact accepted implementation `2fc1a762e17f45fb1a3d866d8100f2c0c284b435`. Canonical closure commit `5d6773bd5f634246c026b2964ca21e7083a966a1` was promoted to `main`. The implementation uses only migration v5, with no dependency or lifecycle transition-matrix changes. Phase 1 M0 is Human-accepted, Phase 1 remains an accepted baseline under active hardening, Phase 2 is open under RLY-P2-OPEN-001, and agent execution remains unauthorized.

**Unblocked ≠ authorized.**
