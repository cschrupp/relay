# Relay — Slice 2.4 Execution Workspace Authority — Design Rework Authorization 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority:** `RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human explicitly authorizes one bounded Slice 2.4 design-rework pass responding only to:

`RLY-S24-DESIGN-EVAL-001 — REWORK`

The rework is limited to findings F001–F006.

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

Design Revision 1:
913d65841fecb4cf8ed172531b4d22e9c45f92cc

Independent design evaluation:
RLY-S24-DESIGN-EVAL-001 — REWORK

Evaluation record:
59a9f9dc6d9401245f3a927e85075a3b16d44bd0

Design branch:
design/2.4-execution-workspace-authority
```

Revision 1 and the independent evaluation record remain immutable.

## Authorized correction scope

Exactly:

```text
F001 exact-subject binding
F002 provider representability
F003 protected-verification permission semantics
F004 WorkspaceChangeManifest identity / exact type-state evidence
F005 no-WorkspacePolicyRef execution path
F006 local-clone control-strength / materialization claim
```

The overall provider-neutral architecture, ownership boundaries, non-authority invariants, filesystem/path model, shell-policy economy, network-versus-external-side-effect separation, credential secrecy, resource/runtime separation, retention model, Phase 3 boundary, no-DB posture, and preferred local-clone first backend are frozen unless a correction is strictly necessary to close F001–F006.

## F001 required correction

Revision 2 must make every positive conformance/evidence assertion bindable to the exact governed subject.

At minimum:

- a Slice 2.4 fact consuming WorkPacket conformance must carry the exact evaluated WorkPacketRef;
- workspace evidence that contributes to conformance must be bound to exact WorkspacePlanRef + WorkspaceInstanceRef, either directly or through an exact immutable subject-bound evidence envelope;
- evidence for another packet/plan/instance/provider cannot satisfy the current subject;
- an opaque evidence digest alone is insufficient unless its canonical digest domain includes the exact subject refs and schema/version.

Revision 2 must not modify accepted Slice 2.3 WorkPacketConformance.

## F002 required correction

Revision 2 must expand the provider capability schema enough for deterministic generic preflight to evaluate the semantic modes/dimensions used by schema v1.

At minimum the provider descriptor must represent, directly or equivalently:

- supported shell modes;
- supported network modes;
- supported external-side-effect modes;
- supported credential exposure modes;
- supported resource-limit dimensions;
- supported repository-metadata modes;
- required path/link-control capability semantics;
- provider-injected-file contract support where applicable.

Do not use arbitrary string capability bags.

Unknown or unrepresented semantic support must not yield SATISFIED preflight.

## F003 required correction

Revision 2 must remove all ordinal/narrower-than semantics from accepted `VerificationAssetPermission`.

The exact WorkPacket-required operation remains one semantic operation.

Physical workspace access/control is modeled separately.

If any set of semantic verification operations is modeled, it must be an explicitly canonical set/subset, never an ordered privilege lattice.

Filesystem writability must never imply semantic `MODIFY` authority.

## F004 required correction

Revision 2 must make WorkspaceChangeManifest digest identity independently recomputable with no self-reference.

Preferred pattern:

```text
WorkspaceChangeManifest
WorkspaceChangeManifestRef
digest_workspace_change_manifest(...)
```

Change entries must represent exact before/after type/mode state sufficiently to distinguish at least:

- regular file;
- symlink;
- executable-mode change;
- deletion/addition;
- type transition.

Symlink target identity must be exact where applicable.

## F005 required correction

Freeze the executable workspace rule:

```text
WorkPacket.workspace_policy_ref is None
    -> no WorkspacePlan may be resolved
    -> WORKSPACE_POLICY_REQUIRED
    -> UNSATISFIED
```

No implicit/default workspace policy may be manufactured.

## F006 required correction

Revision 2 must align local-clone capability claims with the frozen ControlStrength definitions.

A same-user local clone may positively inspect exact source baseline and clean initial state but must not call those facts BOUNDARY_ENFORCED unless a real preventing boundary exists.

If exact deterministic materialization is claimed, the local-clone contract must require independent object storage/no shared hardlink dependency rather than best-effort wording.

## Required Revision 2 deliverable

Produce one additive amendment:

`docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV2_AMENDMENT.md`

Revision 2 is normative over Revision 1 only where it explicitly differs.

Do not rewrite Revision 1.

The amendment must:

- restate the corrected conceptual schemas;
- restate affected evaluation rules;
- restate affected test obligations;
- update A01–A18 disposition/coverage for F001–F006;
- identify every Revision-1 clause superseded by the amendment.

## Explicitly not authorized

This authority does not permit:

- implementation source changes;
- test changes;
- modifications to accepted Slice 2.1 / 2.2 / 2.3 code or models;
- database migration/persistence;
- operational DB mutation;
- real workspace provisioning;
- Git clone/worktree execution against real project state;
- runtime/provider/model calls;
- network access;
- credentials;
- protected-asset mutation;
- AgentRuntime invocation;
- production WorkPacket wiring;
- Phase 3 work;
- real-project agent execution;
- canonical/main promotion.

## Required stop

After the Revision 2 amendment is published:

```text
STOP FOR SOL INDEPENDENT DESIGN REVIEW 002
```

No design acceptance may be self-issued.

## Authority boundary

```text
RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED

Slice 2.4:
OPEN

Revision 2 design rework:
AUTHORIZED — F001–F006 ONLY

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
