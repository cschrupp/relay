# Relay — Slice 2.3 Context / Work-Packet Contract — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Authority:** `RLY-S23-DESIGN-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes detailed design of Slice 2.3 from the exact opened baseline below.

This authority permits design only.

## Exact design basis

```text
Repository:
cschrupp/relay

Canonical opening baseline:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Slice 2.3 opening:
RLY-S23-OPEN-001 — OPEN

Opening record commit:
bddc6a25ab31cfe7395b07135d7f05f5ac3c8e0f

Design branch:
design/2.3-context-work-packet-contract

Existing proposal:
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT.md

Proposal blob:
575f3ae1bca0752f0bd5840559d4dea0010352f4

Accepted Slice 2.2 implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Slice 2.2 closure:
RLY-S22-CLOSE-EVAL-001 — ACCEPT
```

## Authorized design objective

Design the minimum deterministic, provider-neutral Relay contract that binds:

- exact Project/Slice identity;
- exact Slice definition revision/content;
- exact source baseline;
- exact current authority references;
- exact RoleContractRef;
- exact applicable policy/GovernanceProfile references where required;
- normalized engineering intent;
- exact effective context and provenance;
- explicit in-scope/out-of-scope work;
- acceptance criteria;
- required evidence;
- deliverable/result contract;
- runtime requirements as declarations;
- workspace requirements as declarations;
- hard stops/escalation conditions;
- already-established successor-work references where applicable.

The resulting Work Packet must be immutable, reproducible, content-addressed, and incapable of manufacturing authority.

## Mandatory design invariants

The design must preserve all of the following:

```text
WorkPacket != authority
ContextManifest != authority
NormalizedEngineeringIntent != authority
planning source != authority
adapter output != authority
prompt != governed context
document presence != authority
packet completeness != authorization
packet digest != authorization
role eligibility != authorization
runtime capability != authorization
workspace capability != authorization
successful prior execution != authorization
PROPOSED_WORK != authorized work
```

An exact external Human/governance authority remains mandatory.

No packet field may bootstrap Human root authority.

## Required design coverage

The design must explicitly specify:

1. immutable WorkPacket identity, revisioning, canonical serialization, and digest;
2. immutable ContextManifest identity, static/dynamic classification, provenance, and digest;
3. exact Project/Slice/baseline/design/authority/policy/role/profile reference transport;
4. normalized planning-source provenance without coupling Relay to Spec Kit, OpenSpec, BMAD, or any other provider;
5. treatment of missing, stale, conflicting, unverifiable, or incomplete planning/context facts;
6. scope/non-scope and acceptance-criteria semantics;
7. required evidence and deliverable/result contract semantics;
8. mapping to Slice 2.2 RoleInputRequirement / RoleOutputRequirement without duplicating Role Contract policy;
9. declarative runtime requirements reusing Slice 2.1 values;
10. declarative workspace/tool/network/credential/resource requirements without Slice 2.4 enforcement;
11. protected-verification references/classification/authority transport without granting permissions;
12. bounded amendment/revision semantics: changed normative content changes digest and requires new external authority binding;
13. successor reference transport preserving Slice 2.2 successor/exhaustion semantics;
14. deterministic conformance/refusal semantics;
15. a minimal initial implementation architecture with no database migration unless independently justified by the design;
16. deterministic/negative test obligations;
17. explicit boundaries for Slice 2.4 and Phase 3.

## Context requirements

The design must distinguish at least:

```text
STATIC CONTEXT
repository/system rules
accepted architecture/design/policy references
RoleContract reference
authority/non-authority
stable conventions/guardrails

DYNAMIC CONTEXT
selected repository content
retrieved documents
skills
tool definitions
runtime observations
external references
bounded session excerpts
```

Every required context entry must have exact content identity and sufficient provenance.

Mutable aliases such as "latest", implicit chat history, current working tree state, current web content, or current tool definitions are not reproducible governed context unless frozen into an exact referenced snapshot.

Prompt text may be generated from a Work Packet, but prompt text is not the Work Packet and cannot add authority or scope.

## Workflow-provider interoperability

The design may define provider-neutral source/adapter/intention vocabulary.

It must not authorize or require implementation of adapters for named external planning systems.

Normalization rules must be fail-closed:

- missing required source meaning -> missing/indeterminate;
- conflicting source meaning -> conflict/indeterminate;
- unsupported source meaning -> unsupported/indeterminate;
- no inference of authority, acceptance criteria, scope, non-scope, or Human decisions from ambiguous prose;
- Human clarification may resolve ambiguity only through separately governed decision/authority.

## Reuse requirements

Prefer existing Relay values rather than new identity systems:

- ProjectId;
- SliceId;
- BaselineId / Baseline / CommitRef;
- ArtifactId / ContentDigest;
- ActorRef where actor identity is needed;
- RoleContractRef;
- RoleInputRequirement / RoleOutputRequirement;
- RuntimeCapability and runtime provenance values;
- existing governance/Human-authority identities where applicable.

Do not create a new UUID prefix merely for Work Packets or Context Manifests unless the design demonstrates a concrete requirement that content-addressed identity cannot satisfy.

## Design economy

Do not design:

- a generic RAG platform;
- a workflow engine;
- a generic policy engine;
- a second artifact registry;
- a second authority system;
- a general IAM/RBAC layer;
- a prompt-management product;
- a vector database;
- an orchestration queue;
- a workspace manager;
- a credential manager;
- a generic external-planning adapter framework beyond the smallest deterministic interface needed for source provenance.

## Explicitly out of scope

This design authority does not permit:

- production implementation;
- source/test changes;
- database migration or persistence;
- operational DB mutation;
- lifecycle mutation;
- production Work Packet creation;
- external planning-provider calls;
- runtime/provider/model calls;
- workspace/path/network/credential enforcement;
- Slice 2.4 design or implementation;
- Phase 3 orchestration;
- real-project agent execution;
- canonical/main promotion.

## Required acceptance criteria

The design must be independently reviewable against at least:

```text
A01 exact immutable WorkPacket identity/revision/digest
A02 exact Project/Slice/baseline binding
A03 exact external authority/policy/profile/role references; packet cannot create authority
A04 reproducible ContextManifest with exact provenance and fail-closed required context
A05 provider-neutral normalized intent with exact source/adapter provenance and no semantic invention
A06 explicit objective/scope/non-scope/acceptance/deliverable/evidence contract
A07 exact mapping to Slice 2.2 required inputs/outputs without duplicating Role Contract semantics
A08 runtime requirements declarative only and reuse Slice 2.1
A09 workspace/tool/network/credential requirements declarative only; Slice 2.4 enforcement preserved
A10 protected-verification reference transport cannot grant mutation/evaluation authority
A11 amendments/revisions require exact new digest and renewed authority binding; no latest lookup
A12 successor/proposed-work transport preserves no-authority-inheritance and BACKLOG_EXHAUSTED semantics
A13 missing/stale/conflicting/unverifiable required facts fail closed
A14 no DB/RAG/orchestration/provider execution/2.4/Phase3 scope leakage
```

## Deliverable

Produce one detailed design candidate under:

`docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN.md`

The design candidate must identify itself as unaccepted and implementation-not-authorized.

After the design candidate is complete, STOP for independent design review.

**Design authority != design acceptance. Design acceptance != implementation authority.**
