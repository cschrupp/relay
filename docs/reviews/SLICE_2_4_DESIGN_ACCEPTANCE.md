# Relay — Slice 2.4 Execution Workspace Authority — Human Design Acceptance

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Record:** `RLY-S24-DESIGN-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

The Human explicitly accepts the independently accepted combined Slice 2.4 Execution Workspace Authority design.

## Accepted design lineage

```text
Slice opening:
RLY-S24-OPEN-001 — OPEN
4a2a97b706c976d5d57680aadb3cdb8faa4474e9

Design authorization:
RLY-S24-DESIGN-AUTH-001 — AUTHORIZED
7e96c34d97729daadc3606d6809d95f9e3145e51

Revision 1:
913d65841fecb4cf8ed172531b4d22e9c45f92cc

Independent evaluation 001:
RLY-S24-DESIGN-EVAL-001 — REWORK
59a9f9dc6d9401245f3a927e85075a3b16d44bd0

Revision 2:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

Independent evaluation 002:
RLY-S24-DESIGN-EVAL-002 — REWORK
8165a241b8a146142ea2dcb199147946367fdb60

Revision 3:
5370888cf9a8704d00f6b3beafa25f0becec86f8

Independent evaluation 003:
RLY-S24-DESIGN-EVAL-003 — REWORK
4e3b065ad0a40027cd551a3e99faf861f27da14c

Revision 4:
67af9f5e149cd9bf2f1bb620f79d510935eff1b0

Independent evaluation 004:
RLY-S24-DESIGN-EVAL-004 — REWORK
c13ac9d34679775048c3d6004197398460b1e806

Revision 5:
910449b2c984f7f2d14281f573e46fc46ebce399

Independent evaluation 005:
RLY-S24-DESIGN-EVAL-005 — ACCEPT
f4aaf4cd0590af7c7aeaddb9f01f15ede5dac46a
```

Revisions 2–5 are additive amendments and are normative over earlier revisions where they explicitly differ.

All prior independent-review findings F001–F012 are closed.

## Accepted design boundary

The Human accepts the combined design including:

- exact immutable WorkspacePolicyDefinition identity and digest;
- exact immutable WorkspacePlan / WorkspacePlanRef identity;
- exact WorkPacket / source-baseline / RoleContract / GovernanceProfile / provider binding;
- complete resolved property requirements inside WorkspacePlan;
- WorkPacket required workspace-property keys preserved as an exact subset trace;
- provider capability declarations separated from exact instance enforcement evidence;
- DETECTIVE / MEDIATED / BOUNDARY_ENFORCED control-strength semantics;
- exact filesystem/path policy and fail-closed path-escape behavior;
- exact repository-metadata policy;
- exact protected-verification semantic permission plus separate physical control;
- exact protected-authority fact consumption aligned with accepted Slice 2.3;
- exact tool / shell / network / external-side-effect policy;
- exact workspace credential exposure policy with no secret material in Relay models;
- exact resource/retention policy;
- exact provider-injected-file capability/requirement transport through WorkspacePlan;
- exact environment provenance;
- exact initial/terminal WorkspaceInspection;
- exact WorkspaceChangeManifest / WorkspaceChangeManifestRef;
- exact property evidence and tri-state WorkspaceConformance;
- exact RuntimeWorkspaceAttachment derivation without runtime invocation;
- provider-neutral WorkspaceProvider contract;
- bounded local disposable-clone provider as the preferred initial backend;
- explicit local same-user security ceiling;
- no database/persistence requirement;
- no new Relay lifecycle state;
- Phase 3 ownership of orchestration/current execution authority preserved.

## Binding implementation clarifications

The Human also accepts the two clarifications recorded by `RLY-S24-DESIGN-EVAL-005`.

### C01 — WorkspacePlan stable identity

```text
plan_key:
StableRequirementKey

revision:
int >= 1

stable identity:
(work_packet_ref, plan_key, revision)

same stable identity + different content_digest
    -> identity conflict / fail closed

no latest/max revision resolution
```

### C02 — provider property-capability uniqueness

```text
WorkspaceProviderDescriptor.property_capabilities

canonical order:
WorkspaceProperty enum declaration order

stable identity:
WorkspaceProperty

duplicate WorkspaceProperty:
invalid

same WorkspaceProperty + different maximum_strength:
conflicting stable identity / invalid
```

## Authority boundary

This record accepts the design only.

It does not authorize implementation.

Implementation is eligible for a separately prepared exact Codex scope and separate Human implementation authorization.

This acceptance itself does not authorize:

- implementation source/test mutation;
- database schema/migration;
- operational DB mutation;
- production workspace provisioning;
- real-project Git clone/worktree execution;
- credential use;
- network access;
- AgentRuntime/provider/model calls;
- production WorkPacket wiring;
- protected-asset mutation;
- Phase 3 orchestration;
- real-project agent execution;
- canonical/main promotion.

## Disposition

```text
RLY-S24-DESIGN-ACCEPT-001 — ACCEPTED

Slice 2.4:
OPEN

Combined design:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Implementation:
ELIGIBLE FOR EXPLICIT AUTHORIZATION

Workspace provisioning:
NOT AUTHORIZED

AgentRuntime invocation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Design accepted != implementation complete. Implementation authorized != execution authorized.**
