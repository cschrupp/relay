# Relay — Slice 2.4 Execution Workspace Authority — Design Rework Authorization 002

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority:** `RLY-S24-DESIGN-REWORK-AUTH-002 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes one bounded Slice 2.4 Design Revision 3 rework pass responding only to:

`RLY-S24-DESIGN-EVAL-002 — REWORK`

The rework is limited to findings F007–F008.

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

Independent review 001:
RLY-S24-DESIGN-EVAL-001 — REWORK
59a9f9dc6d9401245f3a927e85075a3b16d44bd0

Design rework authority 001:
RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED
38aa99e11f1bbc41196fce4f3e1053e8b9ee96ed

Revision 2 amendment:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

Independent review 002:
RLY-S24-DESIGN-EVAL-002 — REWORK
8165a241b8a146142ea2dcb199147946367fdb60

Design branch:
design/2.4-execution-workspace-authority
```

Revision 1, Revision 2, and both independent evaluations remain immutable.

## Authorized correction scope

Exactly:

```text
F007 ProtectedAssetEvidence schema / derivation
F008 nested WorkspacePolicyDefinition schemas
```

Everything else is frozen.

In particular, do not redesign:

- WorkPacketConformanceFact;
- WorkspaceEvidenceSubject;
- provider capability schema;
- ControlStrength;
- protected permission non-ordinal semantics;
- WorkspaceChangeManifest;
- mandatory WorkspacePolicyRef rule;
- local-clone security ceiling;
- filesystem/path model;
- shell/network/external-effect model;
- credential secrecy boundary;
- Phase 3 boundary.

## F007 required correction

Revision 3 must eliminate the undefined normative `ProtectedAssetEvidence` placeholder.

Preferred correction:

Do not create a new redundant protected-asset evidence model.

Instead, define protected-asset conformance as a deterministic derivation from exact existing subjects:

```text
ProtectedAssetWorkspaceBinding
+
ProtectedVerificationAuthorityFact
+
initial WorkspaceInspection
+
terminal WorkspaceInspection when applicable
+
WorkspaceChangeManifest when applicable
+
WorkspacePropertyEvidence(PROTECTED_ASSET_CONTROL)
```

The design must freeze:

- exact subject joins;
- exact requirement-ref joins;
- exact artifact/path identity joins;
- mutation-observed semantics;
- missing-evidence semantics;
- separate authority handling;
- physical control-strength evaluation;
- canonical ordering/conflict rules;
- pre-execution versus terminal behavior.

No duplicate authority representation may be introduced.

If Revision 3 instead keeps `ProtectedAssetEvidence`, it must define its complete exact schema and show why duplication is necessary.

## F008 required correction

Revision 3 must freeze or remove all currently undefined submodels inside exact `WorkspacePolicyDefinition`.

At minimum:

```python
RepositoryMetadataPolicy(
    access: RepositoryMetadataAccess,
)

WorkspaceCredentialPolicy(
    grants: tuple[WorkspaceCredentialGrant, ...],
)
```

Credential-policy rules must include:

- every grant CredentialRef must be present in exact WorkPacket.credential_refs;
- canonical ordering;
- duplicate/conflicting credential grant rejection;
- exact mapping into WorkspacePlan.workspace_credential_grants;
- no secret bytes/hashes/values.

`WorkspaceProviderRequirements` must either:

1. be removed from WorkspacePolicyDefinition if Revision 2's property requirements + exact semantic-mode provider compatibility fully cover it; or
2. be defined as a finite exact schema-v1 model with a non-duplicative purpose.

Preferred correction: **remove it** unless a unique requirement remains.

Revision 3 must update the canonical WorkspacePolicyDefinition schema and explicitly state that its digest covers the corrected nested structures.

## Required Revision 3 deliverable

Produce one additive amendment:

`docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV3_AMENDMENT.md`

Revision 3 is normative over Revision 1 + Revision 2 only where explicitly stated.

Do not rewrite prior design records.

The amendment must:

- close F007 and F008;
- freeze corrected schemas and evaluator rules;
- freeze canonical ordering/conflict behavior;
- add exact deterministic test obligations;
- update A01–A18 coverage;
- enumerate superseded Revision-1/Revision-2 clauses.

## Explicitly not authorized

This authority does not permit:

- implementation source changes;
- test changes;
- modifications to accepted Slice 2.1 / 2.2 / 2.3 code/models;
- database migration or persistence;
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

After Revision 3 is published:

```text
STOP FOR SOL INDEPENDENT DESIGN REVIEW 003
```

No design acceptance may be self-issued.

## Authority boundary

```text
RLY-S24-DESIGN-REWORK-AUTH-002 — AUTHORIZED

Slice 2.4:
OPEN

Revision 3 rework:
AUTHORIZED — F007–F008 ONLY

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
