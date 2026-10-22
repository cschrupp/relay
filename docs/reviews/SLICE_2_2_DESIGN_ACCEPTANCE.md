# Relay — Slice 2.2 Role Contracts — Human Design Acceptance

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-S22-DESIGN-ACCEPT-001`  
**Decision:** `ACCEPTED`

## Human Authority decision

The Human explicitly accepts the independently accepted combined Slice 2.2 Role Contracts design.

## Accepted design lineage

```text
Slice opening:
RLY-S22-OPEN-001 — OPEN

Design authorization:
RLY-S22-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
63895f87e8f47a0e22a192e6cdbd002e6d51e45d
blob 04d3b0bb3691779b395262a7aff54727a8f43896

Independent evaluation 1:
RLY-S22-DESIGN-EVAL-001 — REWORK
ee2d03b6c4cab767381dae2fc9576ade2ef2ec02

Revision 2 amendment:
f95b26d7123152627418f50b01cb99f9eb3ca0a3
blob a3244554e6cc78c0ac4dce18ab01f04e20d35115

Independent evaluation 2:
RLY-S22-DESIGN-EVAL-002 — ACCEPT
43270ec185889f995ce12a602dee47ba606df3d3
```

Revision 2 is normative over Revision 1 where they differ. All unaffected Revision 1 decisions remain in force.

## Accepted design boundary

The Human accepts the combined design including:

- immutable, digest-bound Relay Role Contracts;
- stable role key + revision + content digest identity;
- exact role-key/revision/digest conflict semantics within one PolicyBasis;
- bounded initial role classes: IMPLEMENTER, INDEPENDENT_EVALUATOR, HUMAN_AUTHORITY, PROMOTION_EXECUTOR;
- complete per-schema action classification;
- explicit separation of role, actor identity, runtime/model identity, capability, and authority;
- `PERMITTED_BY_ROLE != AUTHORIZED`;
- explicit required semantic inputs and outputs at the Role Contract boundary;
- deterministic SATISFIED / UNSATISFIED / INDETERMINATE requirement evaluation;
- prospective ApplicableRoleContractBinding semantics;
- Control/Governance-plane selection of the applicable RoleContractRef;
- executor/runtime/model inability to self-select or downgrade role policy;
- policy-selected evaluator/implementer separation;
- explicit protected-verification read/create/propose-mutation/modify/approve/execute/evaluate semantics;
- reuse of Slice 2.1 ExecutionId, RuntimeCapability, and RuntimeProvenance;
- bounded internal decomposition inside current authorized work only;
- structurally non-authoritative PROPOSED_WORK;
- tri-state successor resolution;
- BACKLOG_EXHAUSTED only for positively established absence of authorized successor;
- fail-closed escalation for indeterminate successor state;
- no initial role-contract DB/table, role catalog, generic IAM/RBAC system, Work Packet implementation, workspace enforcement, or autonomous execution.

The non-blocking independent-review clarification is also accepted:

```text
Human root authority exists independently of RoleContract.
RoleContract may constrain/record Human-role conformance.
RoleContract never creates or bootstraps Human Authority.
```

## Authority boundary

This record accepts the design only.

It does **not** authorize:

- Slice 2.2 production implementation;
- creation of an implementation branch;
- source/test modifications;
- schema/database migration;
- role-contract persistence/catalog;
- live operational database mutation;
- lifecycle transition;
- Slice 2.3 or Slice 2.4 work;
- OpenCode/provider/model execution;
- autonomous project execution;
- Phase 3;
- promotion/merge/main update.

A separate explicit implementation authorization remains required.

## Disposition

```text
RLY-S22-DESIGN-ACCEPT-001 — ACCEPTED

Slice 2.2:
OPEN

Combined Role Contracts design:
INDEPENDENTLY ACCEPTED / HUMAN ACCEPTED

Implementation:
ELIGIBLE FOR SEPARATE AUTHORIZATION
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

**Design accepted != implementation authorized.**
