# Relay — Slice 3.1 Dogfood 001 Workspace-Provider Conformance Gap Investigation / Design Authority 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-26  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Slice 3.1 Dogfood 001 workspace-provider conformance gap  
**Record:** `RLY-S31-DOGFOOD-001-WORKSPACE-PROVIDER-GAP-AUTH-001 — AUTHORIZED`

## 1. Human decision

The Human authorizes the next Relay work item immediately: a bounded investigation and design of the workspace-provider conformance gap currently blocking Dogfood 001 admission.

This authority follows the independently accepted Slice 3.1 operational identity:

```text
SliceId:
slc_01a17b3e-1a64-7614-92d0-b2d6f79664b3

definition_revision:
1

content_digest:
sha256:1659a313cf123983b8a003d2804141ddeca69e4b83f96c272e96030a9cebf8be
```

Materialization evaluation:

`RLY-S31-OPERATIONAL-SLICE-IDENTITY-MATERIALIZATION-EVAL-001 — ACCEPT`

Dogfood 001 remains:

```text
AUTHORIZED
NOT ADMITTED
NOT CONSUMED
```

## 2. Exact problem

Dogfood 001 previously failed closed before admission because the available `LocalCloneWorkspaceProvider` is intentionally declared:

`SAME_USER_NO_SECURITY_BOUNDARY`

and cannot establish every required control at `BOUNDARY_ENFORCED` strength where such strength is required.

The accepted Slice 2.4 contract explicitly distinguishes:

```text
DETECTIVE < MEDIATED < BOUNDARY_ENFORCED

provider capability != instance enforcement evidence
same-user local clone != strong security boundary
workspace conformance != execution authority
```

The investigation must determine the smallest architecture that can satisfy the exact Dogfood 001 workspace requirements without weakening accepted policy or creating a parallel governance/runtime architecture.

## 3. Governing technical basis

The investigation/design is bound to the accepted Slice 2.4 Execution Workspace Authority contract, including:

- `RLY-S24-DESIGN-ACCEPT-001 — ACCEPTED`;
- accepted additive design revisions through Revision 6;
- provider-neutral `WorkspaceProvider` semantics;
- `WorkspaceProviderDescriptor`;
- `WorkspacePlan` / `WorkspacePlanRef`;
- `WorkspaceInstanceRef`;
- `WorkspaceConformance`;
- `RuntimeWorkspaceAttachment`;
- property capability versus exact-instance enforcement evidence;
- `DETECTIVE / MEDIATED / BOUNDARY_ENFORCED` strength semantics;
- the accepted local same-user security ceiling;
- Slice 3.1 ownership of final execution authority and orchestration.

Relevant accepted implementation behavior includes the existing `LocalCloneWorkspaceProvider` and `evaluate_workspace_preflight` fail-closed treatment of `BOUNDARY_ENFORCED` requirements under a same-user local-clone boundary.

## 4. Authorized investigation

The worker may inspect, without semantic mutation:

- all accepted Slice 2.1–2.5 design, implementation, evaluation, and acceptance artifacts relevant to workspace/runtime enforcement;
- Slice 3.1 accepted design and implementation;
- the exact Dogfood 001 request, authority candidate, Human grant, source coverage, snapshot, RoleContract, blocker evidence, and fixture identity;
- current workspace-provider implementation and tests;
- runtime/provider integration surfaces needed to determine whether the runtime actually executes inside the claimed workspace boundary;
- host/runtime capabilities relevant to isolation.

The worker must reconstruct the exact required workspace obligations from accepted authority/policy inputs rather than assuming that every workspace property requires the same control strength.

If an exact required strength cannot yet be determined because the authoritative WorkPacket/WorkspacePlan does not exist, the design must state that explicitly and distinguish:

- known minimum requirements already established by accepted inputs;
- requirements whose exact strength is deferred until WorkPacket/WorkspacePlan materialization.

No uncertainty may be silently converted into permission.

## 5. Authorized host capability probes

Read-only capability inspection is authorized, including checks such as:

- OS/kernel/WSL environment;
- namespaces/user namespaces;
- cgroup v2 availability and delegation;
- OCI/container runtime presence and version;
- rootless container capability;
- `bubblewrap` / `bwrap`, `unshare`, or equivalent sandbox primitives if already installed;
- filesystem/mount capabilities;
- network namespace / deny-network capability;
- process, memory, CPU, file-descriptor and disk/quota enforcement mechanisms;
- runtime executable availability and launch model.

No package installation or host configuration mutation is authorized by this record.

## 6. Authorized synthetic feasibility probes

To avoid a purely speculative design, the worker may run bounded throwaway feasibility probes using synthetic temporary fixtures only.

Such probes may:

- create temporary directories/files outside the Dogfood project;
- launch a disposable sandbox/container if the required software is already installed;
- test read-only versus writable mounts;
- test path-escape prevention;
- test denied network reachability;
- test process/resource limits;
- test environment provenance;
- test teardown and retention;
- test whether a synthetic runtime process can be forced to remain inside the same enforcement boundary.

Synthetic probes must:

- use no Dogfood fixture/source;
- use no credentials;
- use no external network access;
- create no persistent service;
- leave no durable host configuration;
- be torn down after the probe;
- not call an LLM/provider/model.

Probe evidence is investigation evidence only and does not establish Dogfood workspace conformance.

## 7. Required property analysis

The investigation must account for the complete Slice 2.4 workspace property vocabulary:

```text
EXACT_SOURCE_BASELINE
CLEAN_INITIAL_STATE
REPOSITORY_METADATA_ISOLATED
FILESYSTEM_SCOPE
PATH_ESCAPE_CONTROL
PROTECTED_ASSET_CONTROL
TOOL_EXPOSURE_CONTROL
NETWORK_REACHABILITY_CONTROL
EXTERNAL_SIDE_EFFECT_CONTROL
CREDENTIAL_EXPOSURE_CONTROL
RESOURCE_LIMIT_CONTROL
ENVIRONMENT_PROVENANCE
DIRTY_STATE_INSPECTION
CHANGESET_EXTRACTION
RETENTION_CONTROL
TEARDOWN_CONTROL
CONTROL_CONTINUITY
```

For each property, the result must state:

1. whether Dogfood 001 requires it;
2. exact or known-minimum required strength;
3. current `LocalCloneWorkspaceProvider` maximum strength;
4. why current capability is sufficient or insufficient;
5. proposed provider/control mechanism;
6. evidence required to prove actual instance enforcement;
7. ownership boundary for that evidence;
8. whether the accepted Slice 2.4 / Slice 2.1 / Slice 3.1 contracts can already represent it.

## 8. Provider-option analysis

The investigation must compare realistic minimal options supported by the actual host, which may include but are not limited to:

- current local disposable clone;
- local clone plus exact mediation;
- Linux namespace / bubblewrap-style sandbox;
- rootless OCI container;
- container with explicit mount/network/resource policy;
- other already-available local isolation primitive;
- a remote isolated sandbox only if local mechanisms cannot satisfy the contract.

The analysis must not assume "container" means `BOUNDARY_ENFORCED`. It must identify the declared threat/boundary model and the exact enforcement mechanism for each required property.

The preferred design is the smallest option that satisfies the accepted contract and can be evidenced deterministically.

## 9. Runtime-boundary requirement

A central design question is mandatory:

**Does the actual AgentRuntime process execute inside the same boundary whose controls are being claimed?**

The design must trace:

```text
WorkspacePlan
-> provider boundary
-> workspace instance
-> RuntimeWorkspaceAttachment
-> runtime process launch
-> tool/shell/network/credential exposure
-> evidence
```

If the current accepted interfaces cannot keep the runtime inside the provider boundary or cannot represent the required launch/enforcement identity, the result must report an exact contract gap.

Do not claim filesystem/network/tool enforcement from a sandboxed workspace if the executor itself can bypass that sandbox from the host.

## 10. Required design output

If feasible within accepted contracts, produce a concrete provider design sufficient for a later implementation authority. It must include:

- provider/backend identity;
- boundary class and threat model;
- exact capability declaration;
- provisioning sequence;
- source-baseline binding;
- filesystem and path controls;
- protected-asset controls;
- repository-metadata controls;
- tool/shell exposure;
- network policy;
- external-side-effect policy;
- credential exposure;
- resource limits;
- environment provenance;
- runtime launch/binding model;
- initial and terminal inspection;
- changeset extraction;
- retention/teardown;
- control-continuity evidence;
- failure modes and fail-closed behavior;
- exact code surfaces expected to change;
- exact test strategy;
- migration/compatibility impact;
- whether existing `LocalCloneWorkspaceProvider` remains supported;
- whether any accepted predecessor contract must change.

The design must preserve the existing provider-neutral Slice 2.4 architecture. It must not introduce a parallel workspace lifecycle, task system, runtime framework, or authority system.

## 11. Authorized durable artifacts

The worker may create and register the minimum documentation required for this work, including:

- one workspace-provider conformance gap investigation/result artifact;
- one design candidate if the investigation supports a concrete design;
- supporting bounded evidence files for synthetic probes, if necessary.

Registry updates must preserve exact repository ordering requirements.

A local commit and push to the dedicated documentation/design branch are permitted for reviewable investigation/design artifacts.

## 12. Explicit non-authority

This authority does **not** authorize:

- implementation of a new workspace provider;
- modification of production source code or tests;
- dependency/package installation;
- host configuration changes;
- production container/sandbox provisioning;
- Dogfood WorkPacket materialization;
- Dogfood WorkspacePlan materialization;
- provisioning a Dogfood workspace;
- using the Dogfood fixture in a sandbox probe;
- fixture/source repair;
- credential access;
- provider/model calls;
- AgentRuntime admission;
- Dogfood 001 consumption;
- weakening required control strengths;
- changing accepted Slice 2.4 semantics;
- changing accepted Slice 3.1 semantics;
- canonical promotion or merge.

## 13. Required terminals

The investigation/design must end in exactly one of:

### `PROVIDER_DESIGN_CANDIDATE_COMPLETE`

A concrete minimal provider design is available within accepted architecture and is ready for independent review.

### `EXISTING_PROVIDER_SUFFICIENT`

Use only if exact evidence proves the current provider can satisfy all known applicable requirements without weakening or false boundary claims.

### `RUNTIME_BOUNDARY_CONTRACT_GAP`

The workspace boundary cannot be made authoritative for execution because the accepted runtime/workspace interfaces cannot bind the runtime process into the required enforcement boundary.

### `HOST_CAPABILITY_GAP`

The current host lacks required isolation/enforcement primitives and the gap cannot be solved within this design task without new host tooling/configuration.

### `WORKSPACE_CONTRACT_GAP`

An accepted Slice 2.4 contract cannot represent or evidence a required control.

### `EXACT_PLAN_INPUT_REQUIRED`

The investigation reaches a point where the exact WorkPacket/WorkspacePlan is required before a valid provider decision can be made.

### `HUMAN_SEMANTIC_DECISION_REQUIRED`

Two or more materially different conforming architectures remain and selecting one is a Human product/operational choice rather than an engineering derivation.

### `FAIL_CLOSED`

Required provenance is missing/conflicting or the authorized investigation cannot safely determine the result.

## 14. Continuation rule

This authority is intended to keep Relay moving.

A `PROVIDER_DESIGN_CANDIDATE_COMPLETE` terminal should immediately hand off to independent design review. It does not require a conversational pause merely because this bounded authority terminates.

Implementation still requires separate exact Human authority after independent design acceptance.

**Disposition:** `AUTHORIZED`
