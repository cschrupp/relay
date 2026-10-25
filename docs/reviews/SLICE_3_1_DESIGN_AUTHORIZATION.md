# Relay — Slice 3.1 Coding Agent Execution — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Authority:** `RLY-S31-DESIGN-AUTH-001 — AUTHORIZED`

## 1. Human Authority decision

The Human explicitly authorizes one cohesive bounded detailed design of Slice 3.1 — Coding Agent Execution.

This authority permits **design only**.

It does **not** authorize implementation, production wiring, workspace/runtime/provider/model execution, credential use, network side effects, operational database mutation, real-project autonomous engineering, canonical ref mutation, or promotion.

## 2. Exact design basis

```text
Repository:
cschrupp/relay

Canonical opening baseline:
cc35e14d8fd5fedf436354a692fb31edffc709c3

Slice 3.1 opening:
RLY-S31-OPEN-001 — OPEN

Opening record:
docs/reviews/SLICE_3_1_OPENING.md

Opening record commit:
cc35e14d8fd5fedf436354a692fb31edffc709c3

Design branch:
design/3.1-coding-agent-execution

Phase 3:
OPEN under RLY-P3-OPEN-001

Slice 1.10:
COMPLETE / ACCEPTED / CLOSED
RLY-S110-CLOSE-EVAL-001 — ACCEPT

Slice 2.1 — Agent Runtime Contract:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Slice 2.2 — Role Contracts:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Slice 2.3 — Context / Work-Packet Contract:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7

Slice 2.4 — Execution Workspace Authority:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation:
73a1525282e41464d31cd458b8a50703bfa9553c

Slice 2.5 — Project State Resolution & Authority Compilation:
COMPLETE / ACCEPTED / CLOSED
Accepted implementation:
88dcb97110665a60b21b5d36f82f0d82b015b098

Authorized-work decomposition policy:
RLY-GOV-AUTHWORK-GRANULARITY-001 — AUTHORIZED
```

## 3. Exact design-source pins

The design must treat the following accepted or controlling sources as inputs rather than rewrite them:

```text
Slice 2.1 Design Revision 1
docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT_DESIGN.md
blob 56cbb7968577547dee3a31db0e2ee0cca7cb0659

Slice 2.1 Revision 2 Amendment
docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT_DESIGN_REV2_AMENDMENT.md
blob f93f74c45b14abaf28927fa4800a7ee752e1728b

Slice 2.1 Revision 3 Amendment
docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT_DESIGN_REV3_AMENDMENT.md
blob 551c1660c72433404d47e3218f99dde942b8325b

Slice 2.2 Design Revision 1
docs/slices/SLICE_2_2_ROLE_CONTRACTS.md
blob 04d3b0bb3691779b395262a7aff54727a8f43896

Slice 2.2 Revision 2 Amendment
docs/slices/SLICE_2_2_ROLE_CONTRACTS_DESIGN_REV2_AMENDMENT.md
blob a3244554e6cc78c0ac4dce18ab01f04e20d35115

Slice 2.3 Design Revision 1
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN.md
blob d11529c5fdf068a142e79171642cdb735dc290cd

Slice 2.3 Revision 2 Amendment
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN_REV2_AMENDMENT.md
blob c781a3de90cfd54156f3cce6009ac4baa46ce6af

Slice 2.4 Design Revision 1
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN.md
blob 9fd36c9b75f38576687122a7f865081ff275e3fa

Slice 2.4 Revision 6 Amendment
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV6_AMENDMENT.md
blob 3e5f68ba7848295ee9e22519860534e465e8fc80

Slice 2.5 normative design
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_DESIGN.md
blob d14812812374424bbff0e692ed9eca8ebd55196c

Authorized-work decomposition policy
docs/policies/AUTHORIZED_WORK_DECOMPOSITION_AND_EXECUTION_GRANULARITY.md
blob 316a59fcfe87cc6cc2225dff6a9c137434b859d9

Existing Slice 3.1 planning proposal
docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION.md
blob f6805d75b32b79d43670420d5e57db267a8bdd23
```

The existing Slice 3.1 proposal is planning input only. It is not normative where it conflicts with later accepted 2.1–2.5 contracts or the authorized-work decomposition policy.

## 4. Authorized design objective

Design the minimum deterministic Relay-owned orchestration contract for one complete governed coding-agent execution loop.

The design must define how one exact Human-authorized engineering outcome progresses through already-accepted Relay contracts:

```text
requested engineering outcome
        ↓
Project State Resolver
        ↓
Authority Compiler
        ↓
READY / BLOCKED / INDETERMINATE
        ↓
complete authority candidate
        ↓
Human Authority
        ↓
exact WorkPacket
        ↓
RoleContract
        ↓
Execution Workspace
        ↓
AgentRuntime
        ↓
implementation agent
        ↓
agent-owned internal decomposition / retries / milestones
        ↓
terminal implementation candidate + evidence
        ↓
Independent Evaluator
        ↓
ACCEPT / REWORK / ESCALATE
        ↓
Human acceptance / promotion where required
```

Slice 3.1 owns orchestration across these contracts. It must not duplicate their internal semantics.

## 5. Mandatory authority invariants

The design must preserve all of the following:

```text
Human Authority remains the sole root authorization source.

ProjectStateResolver != authority issuer.

AuthorityCompiler != authority issuer.

READY != AUTHORIZED.

Authority candidate != Human authority.

Evidence != authority.

WorkPacket remains the authoritative external work unit.

RoleContract != authority.

Workspace capability != authority.

Workspace conformance != execution authority.

Runtime capability != authority.

Provider/model availability != authority.

Runtime permission != Relay authority.

Agent-owned internal plan != WorkPacket.

Internal milestone != Human approval gate.

Internal milestone != independent-evaluation gate.

Internal retry != new authority.

Internal subagent != new Relay actor authority unless separately represented by accepted RoleContract semantics.

Successful runtime completion != accepted engineering result.

Terminal implementation candidate != accepted result.

Implementation actor cannot evaluate, accept, or promote its own result.

PROPOSED_WORK != authorized successor work.

Out-of-scope required work -> PROPOSED_WORK -> STOP.

No authorized successor -> BACKLOG_EXHAUSTED -> successful STOP.

No automatic push/merge/canonical promotion without exact separate authority.

Relay remains the only authoritative governance state machine.
```

## 6. Ownership boundaries

### Slice 2.5 remains owner of

- deterministic current project-state resolution;
- inherited constraints/prerequisites/prohibitions;
- evidence/qualification applicability;
- responsibility ownership/collision;
- consumable/resource state;
- authority-candidate compilation;
- READY / BLOCKED / INDETERMINATE.

Slice 3.1 consumes an exact resolved/compiled authority basis. It must not invent a second project-state resolver or bypass authority compilation.

### Slice 2.3 remains owner of

- WorkPacket / WorkPacketRef;
- ContextManifest;
- exact normalized work intent;
- exact baseline/context transport;
- WorkspacePolicyRef and runtime declarations carried by the packet;
- packet conformance.

Slice 3.1 may request/consume an exact authorized WorkPacket but must not create a second governed work-unit schema.

### Slice 2.2 remains owner of

- RoleContract / RoleContractRef;
- actor/action eligibility;
- required assurances/capabilities;
- protected-verification permissions;
- role separation;
- work disposition and successor/exhaustion semantics.

Slice 3.1 orchestrates an accepted role but must not redefine role authority.

### Slice 2.4 remains owner of

- WorkspacePolicyDefinition / WorkspacePlan;
- workspace provider/capability/enforcement evidence;
- workspace conformance;
- filesystem/tool/network/credential/resource restrictions;
- protected-verification workspace enforcement;
- RuntimeWorkspaceAttachment derivation;
- dirty-state/result extraction and workspace teardown evidence.

Slice 3.1 may provision/consume workspace services only through separately authorized production wiring. It must not redefine workspace enforcement.

### Slice 2.1 remains owner of

- AgentRuntime;
- runtime session/request/event/result/cancellation contracts;
- runtime/provider/model identity and provenance;
- runtime permission profile;
- runtime credential transport;
- runtime limits and event normalization.

Slice 3.1 may invoke AgentRuntime only through separately authorized implementation/execution and must not create a second runtime abstraction.

### Slice 1.10 remains owner of

- canonical-source discipline;
- promotion authorization and exact canonical mutation;
- quarantine/reconciliation semantics.

Slice 3.1 result production must not imply canonical promotion authority.

## 7. Required design coverage

The design must explicitly specify at least the following.

### A. Exact governed execution subject

Define an immutable exact execution subject/digest that binds at least:

- Project identity;
- Slice identity;
- exact Human authority reference;
- exact authority-candidate/compiled-state reference where applicable;
- WorkPacketRef;
- RoleContractRef;
- WorkspacePlan / workspace instance identity;
- RuntimeWorkspaceAttachment;
- AgentRuntime implementation/runtime identity;
- requested provider/model/runtime constraints;
- exact source baseline / commit;
- execution budget/limits;
- protected-verification requirements;
- terminal/evidence contract version.

The design must distinguish preparation from actual execution authority.

### B. Execution readiness compilation

Define deterministic execution-readiness evaluation over the already accepted contracts.

At minimum, execution must not start unless:

- the exact Human authority is current and matches the execution subject;
- Project State Resolution is SATISFIED/READY for the requested outcome;
- WorkPacket conformance is SATISFIED;
- RoleContract applicability is SATISFIED;
- workspace conformance is SATISFIED;
- runtime capability/permission requirements are SATISFIED;
- required provider/model/environment qualifications are applicable and current;
- no relevant prohibition or responsibility collision is unresolved;
- required consumables/resources are AVAILABLE for the exact intended attempt.

Missing/conflicting/unverifiable required facts must fail closed.

### C. Cohesive WorkPacket execution

Operationalize `RLY-GOV-AUTHWORK-GRANULARITY-001`.

One authorized WorkPacket may contain many agent-owned internal steps.

The design must define how an implementation agent may:

- plan internally;
- decompose internally;
- invoke permitted tools;
- retry locally;
- validate milestones;
- repair within scope;
- self-review;
- continue across routine milestones;

without creating new Relay authority records or repeated Human approval gates.

### D. Internal-progress model

Define non-authoritative execution-progress/provenance sufficient to inspect long-running work without turning internal steps into WorkPackets.

At minimum distinguish:

```text
Relay authority state
vs
runtime execution state
vs
agent-owned internal progress
```

Internal plans/checklists/subagents/milestones may be retained as provenance but cannot control Relay lifecycle/authority.

### E. Hard-stop and terminal semantics

The design must specify exact behavior for at least:

```text
DONE
BLOCKED_BY_AUTHORITY
BLOCKED_BY_CONTRACT
BLOCKED_BY_ENVIRONMENT
BUDGET_EXHAUSTED
BACKLOG_EXHAUSTED
CANCELLED / INTERRUPTED
exact WorkPacket hard-stop conditions
```

Reuse accepted terminal vocabulary where already established; do not create duplicate categories merely for Slice 3.1.

Routine internal milestone completion is not terminal.

### F. Scope-bound discovery

If execution discovers required work outside the exact authority:

```text
record non-authoritative PROPOSED_WORK
STOP current governed execution
do not mutate authoritative backlog
do not invent successor authority
```

The design must specify the evidence carried by such a proposal without converting it to accepted state.

### G. Result and evidence contract

Define the normalized terminal result required from one coding-agent execution.

At minimum bind:

- execution identity;
- exact governed subject;
- actual runtime/provider/model identity;
- exact workspace identity;
- actual source baseline;
- resulting workspace state;
- exact changed-path/change-manifest/content identities;
- commands/tools or normalized runtime events sufficient for provenance;
- validation/test evidence;
- budget/resource usage where available;
- terminal reason;
- unresolved blockers;
- PROPOSED_WORK references;
- dirty/uncommitted state;
- resulting commit identity if one exists.

Do not assume a successful execution always creates a commit.

### H. Commit / Git behavior

Design explicit Git boundaries.

At minimum:

- implementation execution may create local commits only if exact workspace/tool policy permits;
- commit creation != canonical promotion;
- push != authorized unless separately granted;
- merge != authorized unless separately granted;
- canonical ref mutation remains Slice 1.10 controlled;
- dirty or partially committed work must remain inspectable and cannot be misreported as a clean terminal candidate.

### I. Protected Verification Assets

Preserve the accepted assurance model.

The design must distinguish:

- implementation-visible verification material;
- protected verification material;
- evaluator-only verification;
- separately authorized protected-asset mutation.

An implementation agent cannot gain protected verification mutation rights merely because runtime or filesystem capability exists.

### J. Independent-evaluator handoff

Define the exact handoff from implementation execution to independent evaluation.

The evaluator must receive exact immutable subject/evidence references sufficient to judge:

- scope conformance;
- authority conformance;
- implementation correctness;
- provenance sufficiency;
- protected-asset integrity;
- unexpected side effects;
- granularity quality;
- whether rework is bounded to the accepted authority.

The implementation actor may self-review but may not issue `ACCEPT / REWORK / ESCALATE` for its own terminal candidate.

### K. Rework semantics

Define how independent `REWORK` returns to execution.

The design must preserve:

- original authority unless rework remains strictly inside it;
- narrow corrective authority where the finding exceeds original scope;
- no implicit scope expansion;
- no automatic successor WorkPacket creation;
- exact relationship between prior candidate, finding, corrective subject, and new terminal candidate.

### L. Cancellation and recovery

Specify deterministic behavior for:

- Human cancellation;
- runtime cancellation;
- runtime crash;
- workspace/provider failure;
- lost connection;
- ambiguous side effect;
- retry/recovery;
- preserved partial evidence;
- whether a fresh execution identity/authority is required.

Unknown side-effect state must fail closed.

### M. Budget/resource exhaustion

Define budget semantics without treating the runtime as an authority source.

Budget exhaustion must stop execution with preserved evidence and must not silently widen limits or continue with a new provider/model.

### N. Backend/provider neutrality

The normative design must remain provider/runtime neutral.

OpenCode may be the first bounded implementation/runtime substrate because the accepted Slice 2.1 implementation already supports it, but the Slice 3.1 contract must not hard-code OpenCode semantics into Relay authority.

### O. First implementation boundary

The design must identify the minimum production integration surface required for a first implementation while avoiding broad orchestration.

It should prefer composition/adapters over rewriting accepted contracts.

Any needed change to Slices 2.1–2.5 must be expressed as a concrete **contract gap**, not implemented opportunistically.

## 8. Contract-gap rule

Accepted Slices 2.1–2.5 are sufficient by default.

If the design concludes that an accepted contract cannot support Slice 3.1, it must produce a concrete gap statement containing:

```text
accepted owning contract
exact required behavior
exact missing/insufficient interface or invariant
why composition cannot solve it
minimum required amendment
risk of amendment
```

A contract-gap finding does not authorize reopening or changing the predecessor Slice.

Separate Human authority is required.

## 9. Security and side-effect boundary

The design must explicitly distinguish:

```text
tool available != tool authorized
shell available != arbitrary side effects authorized
network reachable != network use authorized
credential present != credential use authorized
repository write capability != canonical mutation authority
runtime can call provider != provider/model call authorized
workspace can access file != mutation authorized
```

Unknown or unverifiable enforcement of a required control must fail closed.

## 10. Design economy

Do not design:

- a second workflow engine;
- a generic planner database;
- a generic multi-agent framework;
- a new WorkPacket format;
- a new RoleContract format;
- a replacement workspace subsystem;
- a replacement AgentRuntime;
- a replacement ProjectStateResolver/AuthorityCompiler;
- a generic CI/CD system;
- a generic Git hosting abstraction;
- a general telemetry platform;
- a new authority system;
- a new lifecycle state machine.

The first design should be the minimum composition layer necessary to execute one governed coding-agent role correctly.

## 11. Required design acceptance scenarios

The design must be independently reviewable against at least these scenarios:

```text
A01 exact Human authority + READY compiled state + conforming packet/role/workspace/runtime -> executable candidate

A02 READY compiled state without exact Human execution authority -> execution denied

A03 Human authority for different WorkPacket / baseline / role / workspace / runtime subject -> denied

A04 stale qualification or changed provider/model/runtime/workspace identity -> fail closed

A05 unresolved prohibition / responsibility collision / consumed resource -> denied

A06 implementation agent decomposes one cohesive WorkPacket internally without new Human gates -> allowed

A07 internal milestone completes -> execution continues, no Relay acceptance event

A08 out-of-scope required work discovered -> PROPOSED_WORK + STOP, no successor authority

A09 authorized backlog exhausted -> BACKLOG_EXHAUSTED successful STOP, no invented work

A10 implementation agent attempts protected verification mutation without separate authority -> denied/fail closed

A11 runtime exposes a tool/shell beyond effective policy -> execution not conforming / fail closed according to accepted runtime/workspace ownership

A12 runtime/provider/model actual identity differs from authorized/qualified subject -> fail closed

A13 execution produces dirty workspace but no commit -> exact dirty result remains reviewable

A14 execution creates local commit -> commit recorded, no implied push/merge/promotion

A15 ambiguous external side effect after runtime failure -> fail closed and require explicit recovery/reconciliation

A16 independent evaluator receives exact immutable terminal evidence and implementation actor cannot self-accept

A17 REWORK within original exact authority -> bounded retry/correction without scope expansion

A18 REWORK requiring new authority -> STOP / separate Human authority

A19 Human cancellation -> terminal evidence preserved; no silent resume

A20 budget exhaustion -> BUDGET_EXHAUSTED with evidence; no silent limit/provider/model expansion

A21 accepted 2.1–2.5 contract is insufficient -> concrete contract-gap record, no opportunistic predecessor rewrite

A22 phase/slice opening or design authority alone -> never sufficient to execute
```

## 12. Authorized design surface

This authority permits creation of one normative design candidate:

`docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION_DESIGN.md`

and the minimum documentation/registry projection changes necessary to record:

```text
Slice 3.1:
OPEN

Design:
AUTHORIZED / CANDIDATE PENDING OR UNDER REVIEW

Implementation:
NOT AUTHORIZED

Phase 3 execution:
NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

The existing proposal `docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION.md` should remain preserved as historical planning input unless a documentation-only status note is necessary; do not rewrite its historical design content into the new normative candidate.

No source or test implementation is authorized.

## 13. Deliverable

Produce one detailed normative design candidate at:

`docs/slices/SLICE_3_1_CODING_AGENT_EXECUTION_DESIGN.md`

The candidate must identify itself as:

```text
DESIGN CANDIDATE — UNACCEPTED
IMPLEMENTATION NOT AUTHORIZED
EXECUTION NOT AUTHORIZED
```

The design must include:

- exact authority/baseline/source pins;
- component/ownership map;
- data model / exact identities;
- deterministic orchestration sequence;
- authority checks;
- state/terminal semantics;
- failure/recovery semantics;
- result/evidence model;
- protected-verification treatment;
- evaluator handoff;
- rework/cancellation/budget behavior;
- first implementation boundary;
- deterministic and negative test plan;
- contract-gap procedure;
- explicit non-authority.

## 14. Required stop

After producing the exact design candidate and validation:

`STOP FOR SOL INDEPENDENT DESIGN REVIEW`.

Do not implement.

Do not run AgentRuntime/provider/model execution.

Do not perform real-project coding-agent work.

## 15. Disposition

```text
RLY-S31-DESIGN-AUTH-001 — AUTHORIZED

Slice 3.1:
OPEN

Design:
AUTHORIZED

Design acceptance:
PENDING

Implementation:
NOT AUTHORIZED

Production wiring:
NOT AUTHORIZED

Phase 3 execution:
NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

**Design authority != design acceptance. Design acceptance != implementation authority. Runtime capability != execution authority.**
