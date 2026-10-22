# Relay — Slice 2.4 Execution Workspace Authority — Design Rework Authorization 004

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority:** `RLY-S24-DESIGN-REWORK-AUTH-004 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes one bounded Slice 2.4 Design Revision 5 rework pass responding only to:

`RLY-S24-DESIGN-EVAL-004 — REWORK`

The rework is limited to finding F012.

This authority permits design correction only.

It does not authorize implementation, source/test mutation, workspace provisioning, AgentRuntime invocation, Phase 3, real-project execution, or canonical promotion.

## Exact rework basis

```text
Repository:
cschrupp/relay

Canonical Slice 2.3 closed baseline:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

Slice 2.4 opening:
RLY-S24-OPEN-001 — OPEN

Revision 1:
913d65841fecb4cf8ed172531b4d22e9c45f92cc

Revision 2:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

Revision 3:
5370888cf9a8704d00f6b3beafa25f0becec86f8

Revision 4:
67af9f5e149cd9bf2f1bb620f79d510935eff1b0

Independent review 004:
RLY-S24-DESIGN-EVAL-004 — REWORK

Evaluation-004 record:
c13ac9d34679775048c3d6004197398460b1e806

Design branch:
design/2.4-execution-workspace-authority
```

All prior design records, rework authorities, and independent evaluations remain immutable.

## Authorized correction scope

Exactly:

```text
F012 WorkspacePlan full property-requirement transport
```

Do not redesign F001–F011.

## F012 required correction

The exact resolved WorkspacePlan must carry the complete workspace-property obligations from the exact WorkspacePolicyDefinition.

Freeze:

```python
WorkspacePlan(
    ...
    packet_required_property_keys:
        tuple[StableRequirementKey, ...],

    property_requirements:
        tuple[WorkspacePropertyRequirement, ...],
    ...
)
```

or an equivalent explicit dual representation.

The existing WorkPacket:

```text
required_workspace_property_keys
```

remains the packet-declared required subset.

The WorkspacePlan:

```text
property_requirements
```

must equal the complete exact:

```text
WorkspacePolicyDefinition.property_requirements
```

including policy-added requirements not named by the WorkPacket.

## Required exact semantics

Revision 5 must freeze:

1. exact packet subset validation;
2. exact policy-to-plan property-requirement equality;
3. provider preflight iteration over plan.property_requirements;
4. provider maximum-strength comparison against each plan requirement minimum;
5. final conformance join from exact WorkspacePropertyEvidence to exact plan requirement;
6. protected control_property_key resolution directly against plan.property_requirements;
7. extra/unknown evidence behavior;
8. missing evidence behavior;
9. exact canonical ordering/conflict rules;
10. WorkspacePlan digest mutation when requirement property/minimum strength changes;
11. fixed WorkspacePlan canonical vectors covering policy-added requirements.

## Explicit invariants

```text
WorkPacket required property keys
    ⊆ exact WorkspacePlan property requirements

WorkspacePlan property requirements
    == exact WorkspacePolicyDefinition property requirements

packet omission of a policy-added requirement
    != permission to drop that requirement

provider preflight
    must not require WorkspacePolicyDefinition lookup

final workspace conformance
    must not require WorkspacePolicyDefinition lookup

protected control_property_key
    must resolve directly in WorkspacePlan
```

## Required Revision 5 deliverable

Produce one additive amendment:

`docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV5_AMENDMENT.md`

Revision 5 is normative over Revision 1–4 only where explicitly stated.

Do not rewrite prior records.

The amendment must:

- close F012;
- enumerate superseded clauses;
- freeze corrected WorkspacePlan schema;
- freeze plan-resolution/preflight/conformance rules;
- freeze canonicality and conflict handling;
- add deterministic tests;
- update A01–A18 coverage.

## Explicitly not authorized

This authority does not permit:

- implementation source changes;
- test changes;
- modifications to accepted Slice 2.1 / 2.2 / 2.3 models;
- DB migration/persistence;
- operational DB mutation;
- real workspace provisioning;
- runtime/provider/model calls;
- network access;
- credential use;
- protected-asset mutation;
- AgentRuntime invocation;
- production WorkPacket wiring;
- Phase 3 work;
- real-project agent execution;
- canonical/main promotion.

## Required stop

After Revision 5 is published:

```text
STOP FOR SOL INDEPENDENT DESIGN REVIEW 005
```

No design acceptance may be self-issued.

## Authority boundary

```text
RLY-S24-DESIGN-REWORK-AUTH-004 — AUTHORIZED

Slice 2.4:
OPEN

Revision 5 rework:
AUTHORIZED — F012 ONLY

Design acceptance:
NOT AUTHORIZED BY THIS RECORD

Implementation:
NOT AUTHORIZED

Workspace provisioning:
NOT AUTHORIZED

AgentRuntime invocation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Rework authority != design acceptance. Design acceptance != implementation authority.**
