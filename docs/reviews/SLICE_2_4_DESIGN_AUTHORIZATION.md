# Relay — Slice 2.4 Execution Workspace Authority — Design Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority:** `RLY-S24-DESIGN-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes detailed design of Slice 2.4 from the exact opened baseline below.

This authority permits design only.

It does not authorize implementation, workspace provisioning, runtime/provider/model execution, real-project execution, Phase 3, or canonical promotion.

## Exact design basis

```text
Repository:
cschrupp/relay

Canonical Slice 2.3 closed baseline:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

Slice 2.3:
COMPLETE / ACCEPTED / CLOSED

Slice 2.3 closure:
RLY-S23-CLOSE-EVAL-001 — ACCEPT

Slice 2.4 opening:
RLY-S24-OPEN-001 — OPEN

Opening record commit:
4a2a97b706c976d5d57680aadb3cdb8faa4474e9

Design branch:
design/2.4-execution-workspace-authority

Existing Slice 2.4 planning proposal:
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY.md

Planning proposal blob:
01edb5cf787280d68d9214b7c8b81abe6d7d5bf9

Accepted Slice 2.1 Agent Runtime implementation:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Accepted Slice 2.2 Role Contracts implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Accepted Slice 2.3 Work-Packet implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

## Authorized design objective

Design the minimum deterministic, provider-neutral Relay contract that can:

1. bind one exact execution workspace to an exact accepted WorkPacket and source baseline;
2. materialize the exact `WorkspacePolicyRef` carried by that WorkPacket into an immutable policy definition;
3. resolve policy, GovernanceProfile, RoleContract, protected-verification, credential, network, tool, filesystem, resource, and retention requirements without weakening any accepted upstream contract;
4. bind one exact workspace provider and its declared capabilities;
5. provision an exact workspace instance only through a separately authorized caller;
6. produce exact enforcement/provenance evidence for the actual workspace instance;
7. deterministically assess workspace conformance as SATISFIED / UNSATISFIED / INDETERMINATE;
8. derive the exact `RuntimeWorkspaceAttachment` required by Slice 2.1 without invoking AgentRuntime;
9. inspect workspace dirty state and extract a bounded exact change manifest;
10. teardown or retain the workspace according to exact policy and produce terminal evidence.

The design must support a minimal local development/dogfood backend without misrepresenting a same-user local workspace as a production-grade isolation boundary.

## Mandatory design invariants

The design must preserve all of the following:

```text
workspace capability != authority
workspace provider capability != control enforcement
workspace creation != work authorization
workspace policy != Human authority
workspace plan != authority
workspace conformance != execution authority
workspace conformance != engineering acceptance

filesystem visibility != write authority
filesystem write capability != permission to mutate every visible path
tool availability != permission to invoke the tool
shell availability != permission for arbitrary side effects
network reachability != permission for network use
credential availability != permission to expose/use a credential
runtime credential != workspace credential exposure
resource availability != permission to consume without limit

protected-asset visibility != mutation authority
protected-asset evaluation != mutation authority
evaluator role != protected-asset mutation authority

exact baseline checkout != authorization
clean workspace != authorization
successful teardown != acceptance
successful prior execution != successor authority

WorkPacket SATISFIED != execution authorized
RoleContract APPLICABLE != execution authorized
RuntimeCapability != workspace authority
PROPOSED_WORK != authorized work
BACKLOG_EXHAUSTED != permission to invent successor work
```

Human root authority and work/execution authority remain external.

## Mandatory ownership boundaries

### Slice 2.1 remains owner of

- RuntimeCapability;
- RuntimeWorkspaceAttachment transport into AgentRuntime;
- runtime sessions/requests/events/results/cancellation;
- requested/actual provider/model/runtime provenance;
- RuntimePermissionProfileRef;
- runtime CredentialRef transport;
- runtime execution limits.

Slice 2.4 may produce a conforming RuntimeWorkspaceAttachment but must not invoke AgentRuntime.

### Slice 2.2 remains owner of

- RoleContract / RoleContractRef;
- actor/action eligibility;
- protected-verification semantic permissions;
- required runtime capabilities;
- role separation;
- work disposition / successor semantics.

Slice 2.4 must consume those semantics and must not redefine role authority.

### Slice 2.3 remains owner of

- WorkPacket / WorkPacketRef;
- SourceBaselineRef;
- WorkspacePolicyRef transport;
- required_workspace_property_keys;
- credential_refs;
- runtime declarations;
- protected_verification_requirements;
- WorkPacket conformance.

Slice 2.4 must consume exact accepted 2.3 values and must not create or amend WorkPackets.

### Phase 3 remains owner of

- selecting the exact currently authorized WorkPacket for execution;
- binding actor identity and execution identity;
- establishing current work/execution authority;
- combining authority + role + packet + workspace + runtime predicates;
- invoking AgentRuntime;
- collecting the engineering result;
- successor orchestration;
- real-project agent execution.

Slice 2.4 must not absorb orchestration.

## Required design coverage

The design must explicitly specify:

1. exact immutable WorkspacePolicyDefinition identity and digest matching `WorkspacePolicyRef`;
2. exact immutable WorkspacePlan identity/digest bound to WorkPacketRef, source baseline, RoleContractRef, policy/profile, provider, and protected requirements;
3. exact provider identity/version/capability description;
4. explicit distinction between provider capability declaration and actual enforcement evidence;
5. workspace instance identity and exact source repository/commit/root binding;
6. filesystem access semantics, including default access, writable/denied paths, canonical path resolution, symlink escape treatment, and repository metadata;
7. protected-verification asset enforcement, including exact operation and separate mutation authority;
8. tool/command policy and the rule that unmediated shell cannot be claimed as narrower than its actual capability;
9. network policy and explicit external-side-effect boundary;
10. credential allowlist/exposure semantics without storing secret bytes;
11. resource limits using deterministic integer values only;
12. exact environment/provider provenance and security-boundary declaration;
13. initial clean-state requirements and source-baseline integrity;
14. workspace-local lifecycle/provision/inspect/teardown semantics without creating Relay lifecycle state;
15. dirty-state/result extraction with exact changed-path/content identities;
16. cancellation cleanup and retention policy;
17. fail-closed handling for unsupported, unavailable, stale, mismatched, bypassable, or unverifiable controls;
18. mapping from `required_workspace_property_keys` to exact workspace property requirements;
19. mapping from RoleContract required assurance/protected-asset permissions without duplicating RoleContract policy;
20. mapping from WorkPacket credentials/runtime declarations without conflating workspace exposure and runtime-provider credentials;
21. derivation of exact Slice 2.1 `RuntimeWorkspaceAttachment`;
22. backend capability model covering at least local development/dogfood, container-capable, and future isolated/cloud providers without pretending all provide equal isolation;
23. evidence sufficient to assess the workspace-relevant assurance properties:
    - RELAY_SCOPE_CONFORMANCE;
    - RELAY_EXECUTION_PROVENANCE_SUFFICIENT;
    - RELAY_VERIFICATION_ASSETS_PROTECTED;
    - RELAY_FAIL_CLOSED;
    - RELAY_CONTROL_CONTINUITY_VERIFIED;
24. a minimum first implementation architecture and deterministic/negative tests;
25. explicit implementation and Phase 3 boundaries.

## Security-boundary requirement

The design must state a concrete threat/boundary model.

At minimum:

```text
local same-user repository/worktree/clone
    != strong filesystem security boundary

declared provider capability
    != observed/enforced control

post-execution detection
    != preventive enforcement

tool mediation
    != OS/container isolation

read-only file mode under same privileged actor
    != unbypassable protected-asset enforcement
```

A backend may be valid for low-risk development/dogfood only when the exact WorkspacePolicyDefinition requires no stronger property than that backend can establish.

If policy requires a control that the backend cannot establish, workspace conformance must fail closed.

## Provider-neutrality requirement

The design may define an interface/protocol for providers.

It must not require Docker, Kubernetes, a specific cloud vendor, OpenCode, or any particular agent/runtime.

Named concrete providers may be used as examples or a bounded first implementation, but the normative contract must remain provider-neutral.

## Design economy

Do not design:

- a second authority system;
- a general IAM/RBAC product;
- a secret manager;
- a generic container platform;
- a cloud scheduler;
- a general policy engine;
- a runtime/orchestrator replacement;
- a shell parser/security language;
- a generic network proxy;
- a SIEM/telemetry platform;
- a new lifecycle state machine;
- a new WorkPacket format;
- a new RoleContract format;
- a general artifact/result store.

## Explicitly out of scope

This design authority does not permit:

- source/test implementation;
- database migration or persistence;
- operational DB mutation;
- production workspace creation;
- real worktree/container/cloud provisioning;
- runtime/provider/model calls;
- network access;
- credential access;
- protected asset mutation;
- production WorkPacket wiring;
- AgentRuntime invocation;
- Phase 3 orchestration;
- real-project agent execution;
- canonical/main promotion.

## Required acceptance criteria

The design must be independently reviewable against at least:

```text
A01 exact immutable WorkspacePolicyDefinition identity/digest matches WorkspacePolicyRef
A02 exact immutable WorkspacePlan identity/digest binds WorkPacketRef + source baseline + provider
A03 workspace plan/conformance cannot create work, Human, role, or execution authority
A04 exact provider identity/capability declaration is separate from enforcement evidence
A05 exact source repository/commit/root binding and initial clean-state semantics
A06 deterministic filesystem allow/deny/write semantics fail closed on escape/unverifiable paths
A07 protected-verification enforcement preserves RoleContract + separate mutation authority
A08 tool/command controls do not overclaim unmediated shell enforcement
A09 network/external-side-effect controls are explicit and fail closed when unsupported
A10 credential policy exposes only exact allowed CredentialRefs and never stores secret bytes
A11 resource/retention/teardown/cancellation semantics are deterministic and evidence-bearing
A12 environment/security-boundary provenance is exact enough to assess required controls
A13 required_workspace_property_keys map to exact policy requirements; unknown required keys fail closed
A14 workspace instance/inspection/change manifest are exact and content-bound
A15 RuntimeWorkspaceAttachment derivation reuses Slice 2.1 and does not invoke runtime
A16 local development backend cannot claim controls stronger than it can establish
A17 missing/stale/conflicting/unsupported/unverifiable required controls -> INDETERMINATE or UNSATISFIED, never implicit PASS
A18 no DB/orchestration/runtime invocation/Phase3/real-project-execution scope leakage
```

## Deliverable

Produce one detailed design candidate under:

`docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN.md`

The design candidate must identify itself as:

`DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED`

After the design candidate is complete:

`STOP FOR SOL INDEPENDENT DESIGN REVIEW`

**Design authority != design acceptance. Design acceptance != implementation authority.**
