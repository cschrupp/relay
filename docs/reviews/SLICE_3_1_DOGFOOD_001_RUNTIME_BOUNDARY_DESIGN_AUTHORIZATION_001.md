# Relay — Dogfood 001 Runtime Boundary Binding & Attestation Contract Design Authority 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-27  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Dogfood 001 runtime-boundary contract closure  
**Record:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-AUTH-001 — AUTHORIZED`

## 1. Human decision

The Human authorizes a bounded design task to resolve the independently accepted:

`RUNTIME_BOUNDARY_CONTRACT_GAP`

for Dogfood 001.

Accepted gap investigation:

`RLY-S31-DOGFOOD-001-WORKSPACE-PROVIDER-GAP-INVESTIGATION-001`

Exact investigation subject:

`f19304a3f7fb8b3316fdba99a4227597538066ca`

Accepted independent evaluation:

`RLY-S31-DOGFOOD-001-WORKSPACE-PROVIDER-GAP-EVAL-001 — ACCEPT`

Evaluation digest:

`sha256:1a3895447d2a6f78b5121f4537f841115b9a49abb9bb598d8801793e36fadca3`

Qualified Slice 3.1 identity:

```text
SliceId:
slc_01a17b3e-1a64-7614-92d0-b2d6f79664b3

definition_revision:
1

content_digest:
sha256:1659a313cf123983b8a003d2804141ddeca69e4b83f96c272e96030a9cebf8be
```

Dogfood 001 remains:

```text
AUTHORIZED
NOT ADMITTED
NOT CONSUMED
```

## 2. Design objective

Design the smallest Relay-native contract extension that can truthfully establish, before and through execution, that the exact AgentRuntime server and its tool/process descendants operate inside the same enforcement boundary whose workspace controls Relay evaluates.

The design must close the missing evidence chain:

```text
exact WorkspacePlan / WorkspaceInstance
        ↓
exact enforcement-boundary identity
        ↓
exact runtime launch or placement identity
        ↓
exact runtime server + descendant process tree
        ↓
mount / filesystem / network / resource / credential boundary
        ↓
effective runtime permissions and exposure
        ↓
continuous exact-instance evidence
        ↓
terminal process-tree / teardown evidence
        ↓
exact execution/request binding
```

The design must not claim that a workspace path, runtime endpoint, working directory, container name, or provider declaration alone establishes process containment.

## 3. Existing ownership boundaries are normative

The design must preserve the accepted ownership split.

### Slice 2.4 — Execution Workspace Authority

Slice 2.4 continues to own:

- workspace policy;
- WorkspacePlan and WorkspacePlanRef;
- WorkspaceProvider identity/capability;
- WorkspaceInstance identity;
- declared provider boundary and threat model;
- filesystem/path/protected-asset/network/credential/resource/retention controls;
- workspace property evidence;
- WorkspaceConformance;
- RuntimeWorkspaceAttachment derivation.

Slice 2.4 does not become execution authority.

### Slice 2.1 — Agent Runtime

Slice 2.1/runtime integration continues to own:

- runtime identity and descriptor;
- RuntimeExecutionRequest and digest;
- RuntimeSessionBinding;
- runtime session/invocation lifecycle;
- runtime-specific adapter behavior;
- runtime events and inspection;
- actual provider/model identity;
- effective runtime permission/exposure evidence.

The design may add the minimum runtime-boundary launch/placement/attestation contract necessary to prove where the runtime actually executes.

### Slice 3.1 — Coding Agent Execution

Slice 3.1 continues to own:

- exact composition of authority + WorkPacket + workspace + runtime predicates;
- final immutable ExecutionSubject;
- final admit / deny / indeterminate decision;
- orchestration of one authorized attempt;
- consumption and terminal execution evidence.

Slice 3.1 may consume new exact boundary/attestation evidence but must not recreate the provider or runtime lifecycle.

## 4. Authorized design work

The worker may inspect all accepted design, implementation, evaluation and acceptance artifacts necessary to trace:

- Slice 2.1 runtime contracts and OpenCode adapter behavior;
- Slice 2.4 workspace-provider and conformance contracts;
- Slice 3.1 execution/admission contracts;
- Dogfood 001 exact runtime/workspace requirements;
- accepted OpenCode sidecar/provisioning history;
- provider/runtime permission-profile evidence direction;
- existing runtime/workspace models, protocols, tests and architecture checks.

The worker may produce additive design amendments or a consolidated design candidate that modifies the conceptual contracts of Slices 2.1, 2.4 and 3.1 only where necessary to close this exact gap.

Existing accepted artifacts must remain immutable historical records.

## 5. Required design questions

The design must answer, precisely:

1. **Who creates the runtime process?**  
   Is the process launched by the workspace provider, a narrow runtime launcher owned by runtime integration, or another existing Relay boundary?

2. **What exact identity represents the enforcement boundary?**  
   Define the stable identity required to refer to the mount/network/resource/process boundary without binding Relay to one Linux mechanism.

3. **What exact identity represents runtime placement?**  
   Define how the runtime server is bound to the boundary and how descendant tool processes remain within it.

4. **Who attests placement?**  
   Identify the component capable of observing and signing/producing the exact evidence, without letting the runtime self-authorize.

5. **What must be known before admission?**  
   Separate pre-admission evidence from terminal/continuity evidence.

6. **What happens if placement identity is unknown or mismatched?**  
   Required result must be `INDETERMINATE` or `UNSATISFIED`, never inferred permission.

7. **How are namespaces/containers abstracted?**  
   The schema must support Bubblewrap/namespaces, OCI/container, or future remote sandbox implementations without claiming equivalence among them.

8. **How is the process tree covered?**  
   The runtime server and all tool descendants must be within the claimed boundary, or the execution cannot claim boundary enforcement.

9. **How are resource controls represented?**  
   Distinguish runtime counters from OS/process-tree memory/CPU/PID/file/disk controls.

10. **How is network separation represented?**  
    Distinguish agent/tool egress from any separately authorized runtime/provider inference transport.

11. **How is credential separation represented?**  
    The design must permit the runtime/provider path to use an authorized credential while proving agent/tool processes cannot read secret material where that is required.

12. **How is effective tool/shell exposure bound?**  
    Integrate the accepted Slice 2.4 Revision 6 direction for runtime permission/exposure evidence.

13. **How is continuity established?**  
    Define evidence sufficient to show that the relevant boundary did not change or disappear during the governed execution.

14. **How is teardown established?**  
    Define how Relay proves the runtime/process tree has terminated and the boundary/workspace lifecycle reached its required terminal state.

15. **How does all evidence bind to the exact ExecutionId/request digest?**  
    No floating or latest-instance evidence is permitted.

## 6. Preferred minimal architecture

The design should prefer an architecture equivalent in spirit to:

```text
WorkspaceProvider
    establishes exact workspace + boundary
             ↓
BoundaryRef / exact immutable boundary evidence
             ↓
Runtime integration
    launches or obtains an exact runtime placement
    inside that boundary
             ↓
RuntimePlacementAttestation
    binds runtime process/server identity
    + boundary identity
    + exact execution/request subject
             ↓
Slice 3.1
    verifies all exact bindings
             ↓
ADMIT only if all required predicates pass
```

Names above are conceptual and not pre-authorized schema names.

The design may choose a narrower representation if it closes the same proof obligation.

## 7. Launch versus attach decision

The design must explicitly compare at least:

### Relay-managed launch

A Relay-controlled integration component launches the exact runtime server inside the workspace/provider boundary and records launch/placement evidence.

### Externally launched runtime + attestation

Relay connects to an already-running runtime only if an independently verifiable attestation can prove that exact server/process tree is inside the exact required boundary.

If attach-mode cannot be made trustworthy without fragile host assumptions, the design should reject attach-mode for strong-boundary executions rather than preserving it for convenience.

The existing externally reachable HTTP adapter may remain valid for weaker/non-boundary use cases if the accepted contracts support such use.

## 8. Boundary identity and evidence requirements

The design must define enough identity/evidence to prevent substitution between:

- different workspace instances;
- different provider instances;
- different sandboxes/containers/namespaces;
- different runtime server processes;
- different process trees;
- stale runtime placements;
- different ExecutionIds;
- different request digests.

A boundary/placement attestation must be immutable or content-digest bound.

At minimum, the design must determine whether evidence needs:

- provider ref;
- workspace instance ref;
- boundary type/class;
- boundary instance ID;
- launch/placement ID;
- runtime descriptor/ref;
- runtime server/process identity;
- process start identity robust to PID reuse;
- process-tree identity/evidence;
- mount/network/user/PID namespace identities where applicable;
- cgroup/resource-domain identity where applicable;
- runtime endpoint;
- execution ID;
- request digest;
- creation/observation timestamps;
- attester identity;
- evidence completeness state.

The design must avoid host-specific fields unless necessary for evidence and keep a provider-neutral semantic layer.

## 9. Admission semantics

The design must state exact fail-closed outcomes.

At minimum:

```text
required boundary attestation absent
    -> INDETERMINATE / no admission

attestation subject != exact workspace/runtime/execution subject
    -> UNSATISFIED / no admission

runtime endpoint reachable but placement unproven
    -> INDETERMINATE / no admission

runtime process outside claimed boundary
    -> UNSATISFIED / no admission

runtime placement changes after authorization/admission predicate evaluation
    -> stop / fail closed

process-tree continuity becomes unknown during execution
    -> terminal evidence marks continuity incomplete;
       do not claim conforming execution
```

The design must specify how these outcomes integrate with existing Slice 3.1 admission without inventing a second admission state machine.

## 10. OpenCode-specific mapping

The design must include a concrete first-runtime mapping for OpenCode while keeping the contract runtime-neutral.

It must determine:

- whether Relay must launch `opencode serve` itself for strong-boundary execution;
- how the exact authorized runtime version is pinned and observed;
- how the endpoint is derived from the launched instance;
- how session `location.directory` relates to the bounded workspace;
- how runtime permission configuration is materialized and attested;
- how provider credentials are supplied without exposing them to tool/shell processes where prohibited;
- how server/tool descendants inherit the boundary;
- what exact evidence proves those statements.

Current documentation for newer OpenCode versions may inform threat analysis but must not be treated as qualification evidence for Dogfood's pinned historical version.

## 11. Host feasibility boundary

This design may use the accepted synthetic host findings as feasibility input:

- user/mount/PID/network namespaces are available;
- Bubblewrap-style mount isolation is partially feasible;
- composed unshare + Bubblewrap synthetic isolation worked;
- cgroup v2 is visible but not delegated writable;
- Docker daemon is unavailable to the current user;
- no usable rootless OCI service was established.

The design must not choose a host-specific implementation merely because one probe succeeded.

If the exact contract can be designed provider-neutrally while implementation feasibility differs by backend, that is preferred.

## 12. Required outputs

The worker must produce a reviewable design package containing:

1. problem statement and accepted-gap lineage;
2. exact ownership analysis;
3. proposed contract changes by Slice owner;
4. conceptual and, where appropriate, concrete schema;
5. stable identity and digest rules;
6. lifecycle/order of operations;
7. pre-admission and terminal evidence requirements;
8. fail-closed semantics;
9. OpenCode mapping;
10. provider-neutral mapping;
11. backward compatibility impact;
12. effect on existing LocalCloneWorkspaceProvider;
13. effect on existing OpenCodeRuntime attach behavior;
14. exact implementation surfaces expected to change;
15. exact tests required;
16. migration/versioning strategy, if any;
17. explicit non-goals;
18. unresolved questions, if any.

The worker must also identify whether the design is:

- purely additive to existing accepted schemas/protocols; or
- requires a versioned contract amendment.

## 13. Explicit non-authority

This authority does **not** authorize:

- production source/test mutation;
- implementation of new models/protocols/providers/launchers;
- package installation;
- host configuration changes;
- starting the Dogfood OpenCode server;
- using the Dogfood fixture;
- WorkPacket/WorkspacePlan materialization;
- Dogfood workspace provisioning;
- credential access;
- provider/model calls;
- AgentRuntime execution;
- Dogfood admission or consumption;
- changing the accepted Dogfood runtime version;
- weakening workspace or runtime controls;
- rewriting historical accepted design records;
- creating a second planner, runtime framework, workspace lifecycle, or authority system;
- canonical promotion or merge.

## 14. Authorized durable artifacts

The worker may create and register:

- one runtime-boundary contract design candidate;
- additive design-amendment artifacts for affected existing Slice contracts if useful;
- one bounded decision matrix or schema appendix if necessary.

Documentation/design commits and push to the dedicated design branch are authorized for independent review.

Registry ordering and digest invariants remain mandatory.

## 15. Required terminals

Exactly one terminal must be produced:

### `RUNTIME_BOUNDARY_DESIGN_CANDIDATE_COMPLETE`

A concrete contract design closes the accepted gap and is ready for independent design review.

### `PREDECESSOR_CONTRACT_REDESIGN_REQUIRED`

The gap cannot be closed additively without materially redesigning an accepted predecessor contract.

### `HOST_SPECIFIC_SEMANTICS_REQUIRED`

A provider-neutral contract cannot express the necessary proof without hard-coding a host isolation mechanism.

### `HUMAN_SEMANTIC_DECISION_REQUIRED`

Two or more materially different valid contract architectures remain and selection is a Human product/architecture choice.

### `FAIL_CLOSED`

Required lineage/provenance is missing or contradictory, or no safe design can be derived under this authority.

## 16. Continuation rule

This is a Relay workflow step, not a conversational stopping point.

A `RUNTIME_BOUNDARY_DESIGN_CANDIDATE_COMPLETE` terminal should proceed directly to independent design review.

If independently accepted, the next gate is Human design acceptance followed by a separate exact implementation authority.

Dogfood 001 remains unadmitted and unconsumed throughout this design task.

**Disposition:** `AUTHORIZED`
