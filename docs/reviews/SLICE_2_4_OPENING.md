# Relay — Slice 2.4 Opening

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Record:** `RLY-S24-OPEN-001`  
**Decision:** `OPEN`

## Human Authority decision

The Human explicitly authorizes opening Slice 2.4 — Execution Workspace Authority.

This record opens the Slice only.

It does **not** authorize Slice 2.4 design work, implementation, workspace provisioning, production integration, agent/runtime execution, Phase 3, or real-project execution.

---

## Exact opening baseline

```text
Repository:
cschrupp/relay

Canonical main:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

Slice 2.3:
COMPLETE / ACCEPTED / CLOSED

Slice 2.3 closure:
RLY-S23-CLOSE-EVAL-001 — ACCEPT

Slice 2.3 accepted implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7

Slice 2.4:
OPEN

Slice 2.4 design:
NOT AUTHORIZED BY THIS RECORD

Slice 2.4 implementation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

The exact canonical baseline above is the starting point for any future Slice 2.4 design authority.

---

## Existing planning source

The existing planning artifact:

`docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY.md`

remains a **future-slice proposal / planning input**.

Opening Slice 2.4 does not convert that proposal into an accepted design, implementation contract, or execution authority.

Any normative Slice 2.4 design must be created under a separate Human design authorization and independently reviewed before implementation can be considered.

---

## Slice objective

The Slice 2.4 objective remains bounded to defining Relay-owned execution-workspace authority and enforcement semantics for work bound to exact governed inputs, including the already accepted boundaries from:

- Slice 2.1 Agent Runtime Contract;
- Slice 2.2 Role Contracts;
- Slice 2.3 Context / Work-Packet Contract;
- accepted GovernanceProfile / protected-verification semantics where applicable.

The design must preserve the principle that a workspace is an enforcement substrate, not an authority issuer.

---

## Mandatory boundary invariants for any future design

Any future Slice 2.4 design must preserve at minimum:

```text
workspace capability != authority

workspace creation != work authorization

workspace policy != Human authority

filesystem access != mutation authority

tool availability != permission to use the tool for governed work

credential availability != authorization to use a credential

network reachability != permission for an external side effect

protected-asset visibility != protected-asset mutation authority

runtime capability != workspace authority

WorkPacket conformance != execution authority

workspace conformance != engineering acceptance

successful execution != Human acceptance

workspace teardown != lifecycle promotion

PROPOSED_WORK != authorized successor work
```

Human root authority remains external.

---

## Design questions now eligible for separate authorization

A future Slice 2.4 design authority may cover the bounded design of:

- workspace identity;
- exact Project/Slice/WorkPacket/baseline binding;
- exact RoleContract / GovernanceProfile / workspace-policy inputs;
- filesystem read/write authority;
- allowed / denied paths;
- protected verification asset controls;
- mutation-authority separation;
- network policy;
- credential / secret grants;
- tool / command policy;
- external side-effect policy;
- resource limits;
- environment provenance;
- workspace lifecycle;
- teardown / retention;
- result extraction;
- dirty-state handling;
- cancellation cleanup;
- provider/backend capability representation;
- local worktree / container / future isolated backend capability differences;
- evidence sufficient to assess workspace scope conformance, provenance sufficiency, protected-asset enforcement, fail-closed behavior, and control continuity.

This list is an opening boundary only. It does not freeze the detailed design.

---

## Explicitly not authorized

This opening does not authorize:

- editing production source or tests for Slice 2.4;
- creating a workspace provider;
- creating or mutating real worktrees/containers for governed execution;
- production WorkPacket wiring;
- runtime/provider/model calls;
- credential use;
- network access;
- protected-asset mutation;
- operational DB or lifecycle mutation;
- schema migration;
- production orchestration;
- Phase 3 work;
- real-project agent execution;
- canonical/main promotion arising from Slice 2.4 work.

---

## Design lineage

The Slice 2.4 design lineage is:

`design/2.4-execution-workspace-authority`

and begins exactly at:

`3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc`

No downstream authority may be inferred from branch existence.

---

## Disposition

```text
RLY-S24-OPEN-001 — OPEN

Slice 2.4:
OPEN

Design:
NOT YET AUTHORIZED

Implementation:
NOT AUTHORIZED

Workspace provisioning/enforcement:
NOT AUTHORIZED

Runtime/provider/model execution:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Slice open != design authorized. Design authorized != implementation authorized. Unblocked != authorized.**
