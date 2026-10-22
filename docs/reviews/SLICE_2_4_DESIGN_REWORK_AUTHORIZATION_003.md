# Relay — Slice 2.4 Execution Workspace Authority — Design Rework Authorization 003

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority:** `RLY-S24-DESIGN-REWORK-AUTH-003 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes one bounded Slice 2.4 Design Revision 4 integration-cleanup pass responding only to:

`RLY-S24-DESIGN-EVAL-003 — REWORK`

The rework is limited to findings F009–F011.

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
4a2a97b706c976d5d57680aadb3cdb8faa4474e9

Original design authority:
RLY-S24-DESIGN-AUTH-001 — AUTHORIZED
7e96c34d97729daadc3606d6809d95f9e3145e51

Revision 1:
913d65841fecb4cf8ed172531b4d22e9c45f92cc

Revision 2:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

Revision 3:
5370888cf9a8704d00f6b3beafa25f0becec86f8

Independent review 003:
RLY-S24-DESIGN-EVAL-003 — REWORK
4e3b065ad0a40027cd551a3e99faf861f27da14c

Design branch:
design/2.4-execution-workspace-authority
```

All prior design records, rework authorities, and independent evaluations remain immutable.

## Authorized correction scope

Exactly:

```text
F009 protected-authority fact consumption for no-authority requirements
F010 provider-injected-file transport into provider provisioning
F011 remaining digest-bound policy container schemas
```

Everything else is frozen.

Do not redesign F001–F008.

## F009 required correction

Align Slice 2.4 with accepted Slice 2.3 semantics:

```text
binding.separate_authority_ref is None
    -> no ProtectedVerificationAuthorityFact is required
    -> no ProtectedVerificationAuthorityFact is consumed
    -> separate-authority prerequisite is NOT_APPLICABLE
```

Only bindings with non-None separate authority refs participate in the exact protected-authority fact sequence.

Freeze deterministic missing/extra/wrong/reordered fact behavior consistent with accepted Slice 2.3 exact-subject semantics.

## F010 required correction

Make provider-injected-file requirements available to the exact provider protocol without an implicit policy lookup.

Preferred correction:

```python
WorkspacePlan(
    ...
    provider_injected_files:
        tuple[ProviderInjectedFileRequirement, ...],
)
```

with exact mapping:

```text
plan.provider_injected_files
    == workspace_policy.provider_injected_files
```

The tuple participates in WorkspacePlan canonical identity.

`WorkspaceProvider.provision(plan)` must therefore receive all exact injected-file path/digest requirements directly.

No policy resolver/content store may be invented.

## F011 required correction

Freeze complete schema-v1 containers for all remaining digest-bound policy fields.

At minimum:

```python
ToolDecision:
    ALLOW
    DENY

ShellPolicy(
    mode: ShellMode,
)

NetworkPolicy(
    mode: NetworkMode,
    allowed_endpoints: tuple[NetworkEndpoint, ...],
)

ExternalSideEffectPolicy(
    mode: ExternalSideEffectMode,
    allowed_effects: tuple[ExternalEffectRef, ...],
)
```

Also freeze:

- exact mode/list consistency;
- canonical ordering;
- duplicate/conflict rejection;
- exact leaf identity rules required for deterministic hashing;
- WorkspacePolicyDefinition fixed canonical vectors including these containers.

Do not invent a generic policy language.

## Required Revision 4 deliverable

Produce one additive amendment:

`docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV4_AMENDMENT.md`

Revision 4 is normative over Revision 1 + Revision 2 + Revision 3 only where explicitly stated.

Do not rewrite prior records.

The amendment must:

- close F009–F011;
- enumerate superseded prior clauses;
- freeze corrected schemas/evaluation rules;
- freeze exact canonicality/conflict rules;
- add deterministic tests;
- update A01–A18 coverage.

## Explicitly not authorized

This authority does not permit:

- implementation source changes;
- test changes;
- modifications to accepted Slice 2.1 / 2.2 / 2.3 code/models;
- DB migration/persistence;
- operational DB mutation;
- real workspace provisioning;
- Git clone/worktree execution against real project state;
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

After Revision 4 is published:

```text
STOP FOR SOL INDEPENDENT DESIGN REVIEW 004
```

No design acceptance may be self-issued.

## Authority boundary

```text
RLY-S24-DESIGN-REWORK-AUTH-003 — AUTHORIZED

Slice 2.4:
OPEN

Revision 4 integration cleanup:
AUTHORIZED — F009–F011 ONLY

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
