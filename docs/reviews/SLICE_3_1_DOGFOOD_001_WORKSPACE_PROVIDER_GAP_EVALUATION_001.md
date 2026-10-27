# Relay — Dogfood 001 Workspace-Provider Conformance Gap Investigation — Independent Review 001

**Document class:** Immutable independent evaluation record  
**Status:** IMMUTABLE / ACCEPT  
**Date:** 2026-10-27  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Dogfood 001 workspace-provider conformance gap investigation  
**Evaluation:** `RLY-S31-DOGFOOD-001-WORKSPACE-PROVIDER-GAP-EVAL-001 — ACCEPT`  
**Exact reviewed subject:** `f19304a3f7fb8b3316fdba99a4227597538066ca`  
**Reviewed parent:** `1bc909a7e25bbc19f55280d2059dcbc5e939d843`

## 1. Decision

```text
RLY-S31-DOGFOOD-001-WORKSPACE-PROVIDER-GAP-EVAL-001
ACCEPT
```

The investigation terminal:

`RUNTIME_BOUNDARY_CONTRACT_GAP`

is justified and is the correct fail-closed result under the authorized investigation.

No provider design candidate should be accepted from the current evidence because the missing capability is not merely a stronger filesystem provider. Relay lacks an accepted exact contract/evidence path binding the actual runtime server and tool processes to the workspace enforcement boundary whose controls would be claimed.

## 2. Exact reviewed footprint

PASS.

The exact subject changes only:

- `.relay/registry.json`; and
- `docs/reviews/SLICE_3_1_DOGFOOD_001_WORKSPACE_PROVIDER_GAP_INVESTIGATION_001.md`.

No production source, test, dependency, CI definition, operational database, Dogfood fixture, WorkPacket, WorkspacePlan, workspace instance, runtime session, credential, provider/model request, or Dogfood implementation artifact is changed by the reviewed commit.

The result artifact is registered as an immutable record with digest:

`sha256:e2a1777ac90c7ec7565223289c954931c6145e2f62ab12ce13622eed201cd7a1`

Independent SHA-256 recomputation of the exact remote bytes matches the registered digest.

Registry state at the reviewed subject:

```text
artifacts:            385
canonical pointers:   5
ordering violations:  0
```

## 3. CI and repository validation

PASS.

Exact-head CI run `40449955501` is bound to the reviewed commit and completed with:

`SUCCESS`.

The investigation reports repository-contract validation:

`43 passed`.

No contrary repository evidence was found.

## 4. Core contract-gap finding

PASS.

The finding is established by Relay's accepted interfaces themselves.

### 4.1 RuntimeWorkspaceAttachment does not identify runtime placement

The accepted `RuntimeWorkspaceAttachment` binds:

- workspace ID;
- absolute workspace root;
- repository identity;
- exact source commit.

It does not bind:

- runtime server process identity;
- PID/process-tree identity;
- mount namespace;
- network namespace;
- user namespace;
- cgroup;
- OCI/container identity;
- sandbox identity;
- process-launch provenance.

Binding a workspace path into an execution request proves which workspace Relay requested. It does not prove where the runtime server or its tool descendants execute.

### 4.2 RuntimeSessionBinding does not close the gap

The accepted `RuntimeSessionBinding` binds:

- execution ID;
- runtime session;
- request digest;
- workspace ID;
- creation timestamp.

Its accepted design deliberately avoids duplicating the wider execution basis.

That correctly protects request/session identity but does not establish process placement or containment.

### 4.3 OpenCodeRuntime is transport-only with respect to server placement

The accepted `OpenCodeRuntime` adapter explicitly documents:

```text
No server discovery, process management, credential lookup,
or API-generation fallback occurs here.
```

It connects to an explicit HTTP endpoint.

Session creation sends the requested workspace root as an OpenCode session location and verifies the returned directory, but that confirms a logical working directory only. It does not prove that the HTTP server or tool children are executing inside the workspace provider's mount/network/resource boundary.

Therefore the current adapter cannot truthfully convert workspace provider capability into runtime process-placement evidence.

## 5. External corroboration

PASS as supplementary evidence.

Current official OpenCode documentation describes:

- `opencode serve` as a separately running headless HTTP server; and
- the shell tool as running with the host user's filesystem, process, and network authority.

Current OCI runtime documentation separately models mount/network/PID/user/cgroup namespaces and cgroup resource controls as explicit runtime configuration.

These sources support the investigation's threat model.

They do not establish behavior of the exact historical Dogfood OpenCode version `0.0.0-beta-17823`; the investigation correctly avoids using current documentation to qualify that version.

The Relay contract gap is independently established without relying on that version-specific inference.

## 6. Host feasibility result

ACCEPTED as bounded investigation evidence.

The synthetic probes establish that this host can construct useful isolation primitives:

- user/mount/PID/network namespace creation;
- Bubblewrap mount isolation;
- one explicitly writable bound directory;
- read-only host paths;
- path/symlink escape suppression under the synthetic mount shape;
- network namespace with no ordinary routes;
- bounded tmpfs;
- selected per-process rlimits.

The probes do **not** establish a Dogfood-conforming provider.

The reported constraints are material:

- no delegated writable cgroup v2 hierarchy;
- Docker daemon unavailable to the user;
- no established usable rootless OCI service;
- direct Bubblewrap network setup constrained on this host;
- current installed OpenCode version does not match the authorized Dogfood runtime version.

These facts support the conclusion that choosing a specific provider implementation now would be premature.

## 7. Property matrix

PASS.

The investigation correctly separates:

```text
known Dogfood obligation
!=
exact ControlStrength already established
```

because the exact WorkPacket and WorkspacePlan have not yet been materialized.

It does not lower unknown future minimum strengths to fit the current provider.

The matrix covers the complete accepted Slice 2.4 property vocabulary and distinguishes:

- current LocalClone maximum capability;
- known gap;
- potential enforcement mechanism;
- exact-instance evidence requirement;
- current contract representability.

This is the correct fail-closed treatment.

## 8. LocalClone disposition

PASS.

The current `LocalCloneWorkspaceProvider` remains useful for:

- exact source checkout evidence;
- clean-state detection;
- repository metadata separation;
- dirty-state inspection;
- changeset extraction;
- mediated retention/teardown.

It is correctly **not** reclassified as a strong boundary.

Its explicit `SAME_USER_NO_SECURITY_BOUNDARY` semantics remain intact.

No provider strength is widened by assertion.

## 9. Why this is not PROVIDER_DESIGN_CANDIDATE_COMPLETE

PASS.

A stronger provider alone would not close the central evidence gap.

For runtime-sensitive controls, a future conforming architecture must be able to establish a chain equivalent to:

```text
exact WorkspacePlan / workspace instance
        ->
exact enforcement-boundary identity
        ->
exact runtime server launch/placement identity
        ->
exact runtime process tree / tool descendants
        ->
mount/network/resource/credential/tool controls
        ->
continuous exact-instance evidence
        ->
terminal teardown/effect evidence
```

The currently accepted interfaces do not carry the necessary runtime-placement/attestation identity.

Therefore producing an OCI/Bubblewrap provider design as if it were independently sufficient would be architecturally false.

## 10. Ownership of the next design problem

The smallest correct next problem is a **runtime-boundary binding and attestation contract**, not a new Relay architecture.

The design must preserve the existing ownership split:

- Slice 2.4 owns workspace policy, provider boundary, workspace instance, enforcement requirements and workspace evidence;
- Slice 2.1/runtime integration owns runtime descriptor/session/request/provenance and runtime-specific behavior;
- Slice 3.1 owns exact composition, final ExecutionSubject, admission, and orchestration.

The design should determine the minimum accepted identity/evidence needed to bind:

1. exact workspace instance/provider boundary;
2. exact runtime server process or container/sandbox launch identity;
3. exact process-tree descendants used for tools;
4. namespace/mount/network/resource boundary identities;
5. exact runtime permission/effective exposure evidence;
6. credential-delivery separation;
7. continuity and teardown evidence;
8. all of the above to the exact execution/request digest.

The design should first test whether this can be added as a narrow runtime-integration/workspace-boundary extension.

It must not create:

- a second runtime framework;
- a second workspace lifecycle;
- a new authority system;
- a generic process supervisor unrelated to Relay's existing contracts.

## 11. Remaining independent blockers

This ACCEPT closes only the investigation gate.

It does not close:

- runtime-boundary contract design;
- implementation of that design;
- exact OpenCode historical-version qualification;
- workspace-provider implementation/conformance;
- fixture/source durable reachability;
- exact WorkPacket/WorkspacePlan construction;
- final freshness/admission predicates.

Dogfood 001 remains:

```text
AUTHORIZED
NOT ADMITTED
NOT CONSUMED
```

## 12. Final disposition

```text
Exact investigation subject:
f19304a3f7fb8b3316fdba99a4227597538066ca

Investigation authority compliance:
PASS

Registry / digest:
PASS

Exact-head CI:
PASS

Host synthetic evidence:
ACCEPTED AS BOUNDED EVIDENCE

Current LocalClone boundary:
INSUFFICIENT FOR STRONG RUNTIME-SENSITIVE CLAIMS

Runtime-placement / process-attestation contract:
MISSING

Terminal:
RUNTIME_BOUNDARY_CONTRACT_GAP — ACCEPT

Provider design candidate:
NOT PRODUCED / CORRECT

Dogfood 001:
AUTHORIZED / NOT ADMITTED / NOT CONSUMED
```

**The investigation is independently accepted. The next Human gate is a bounded runtime-boundary binding and attestation contract design authority.**
