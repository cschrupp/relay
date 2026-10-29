# Relay Slice 3.1 — Runtime-Native Execution Profile Amendment 001

**Document class:** Lockable design amendment candidate
**Status:** `DESIGN AMENDMENT CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED`
**Strategic authority:** `RLY-S31-RUNTIME-NATIVE-PROFILE-STRATEGIC-AMEND-001 — AUTHORIZED`
**Date:** 2026-10-28

## 1. Purpose

This amendment corrects an over-constraint introduced during Dogfood 001 runtime-boundary hardening.

The accepted runtime-boundary design correctly provides a strong-boundary execution path, but Dogfood 001 subsequently treated that path as mandatory for ordinary OpenCode execution. That is not the intended product architecture.

Relay governs and verifies coding-agent execution. OpenCode is the execution runtime. When the selected execution profile delegates sandboxing and tool permissions to OpenCode/runtime-native controls, Relay does not need to create a second OS/container sandbox around OpenCode.

The existing strong-boundary machinery is retained unchanged for executions that explicitly require it.

## 2. Execution profiles

### EP-01 — `RUNTIME_NATIVE_CONTROLLED`

This is the default intended profile for ordinary OpenCode coding-agent execution unless the exact authority or workspace policy requires stronger containment.

Relay responsibilities are:

1. Bind the exact authorized runtime, provider, model, workspace/source, WorkPacket and attempt.
2. Supply the exact runtime-native sandbox/permission/tool configuration required by the WorkPacket.
3. Verify before prompt admission that the selected OpenCode runtime matches the authorized identity and that the requested runtime-native configuration was accepted/applied.
4. Where the adapter exposes effective permission/tool state, obtain and bind that evidence to the exact session/attempt.
5. Do not infer controls that OpenCode cannot represent or that Relay cannot verify at the required strength.
6. After execution, inspect the repository/workspace and protected assets to validate authorized postconditions and detect unauthorized changes.
7. Preserve exact terminal evidence for independent review.

For this profile, the following are NOT inherently required:

- `BoundaryScopedRuntimeLauncher`;
- Relay-owned container/namespace/cgroup creation;
- `WorkspaceBoundaryRef`;
- OS process-tree placement attestation;
- independent placement-attester trust anchors;
- boundary continuity evidence;
- OS process-tree teardown evidence.

They become required only if another accepted requirement explicitly calls for `RELAY_MANAGED_STRONG_BOUNDARY` or an equivalent control strength.

### EP-02 — `RELAY_MANAGED_STRONG_BOUNDARY`

The previously accepted Candidate 003 runtime-boundary path remains valid and unchanged.

This profile is selected only when the exact authority-bearing work requires OS/container-level containment or an equivalent externally attested boundary.

Its existing requirements remain applicable, including:

```text
BoundaryScopedRuntimeLauncher
→ WorkspaceBoundaryRef
→ RuntimeLaunchSubject
→ RuntimePlacementAttestation
→ prompt-free runtime session
→ RuntimePermissionAttestation
→ final admission
→ continuity / teardown evidence
```

No part of this amendment downgrades this profile.

## 3. Runtime-native control mapping

For `RUNTIME_NATIVE_CONTROLLED`, Relay maps authorized constraints to runtime-native controls plus terminal verification.

Conceptually:

| Authorized concern | Runtime-native profile handling |
| --- | --- |
| allowed/denied tools | Configure OpenCode tool/permission policy; verify effective exposure where observable |
| shell access | Configure exact OpenCode shell permission policy |
| agent-facing network/web tools | Disable/deny through OpenCode permissions/tool configuration when supported; verify effective tool exposure where observable |
| workspace/file scope | Provide exact intended workspace and runtime instructions/configuration; verify terminal Git/filesystem evidence |
| protected oracle/assets | Keep them outside authorized mutation scope; verify pre/post digests and terminal state |
| Git remote mutation | Deny by runtime instructions/tool policy where supported and verify repository/remotes/effects afterward |
| dependency changes | Express as WorkPacket constraint and verify manifests/lockfiles/changes afterward |
| provider/model identity | Verify exact runtime-reported provider/model against authority |
| credentials | Provide only through the runtime's accepted credential path; do not place secret values in Relay evidence or prompts |
| duration/tool/output limits | Relay/runtime counters remain authoritative where already implemented |
| final mutation scope | Validate exact changeset against WorkPacket before result acceptance |

This is intentionally a mixed preventive/detective assurance model. Relay must label evidence according to what is actually enforced versus what is only inspected afterward.

## 4. Admission sequence for runtime-native OpenCode

The normal runtime-native path becomes:

```text
fresh AuthorityCandidate + exact Human execution authority
    ↓
materialize exact WorkPacket / Context / WorkspacePlan
    ↓
provision intended workspace using selected workspace provider
    ↓
verify exact fixture/source identity and durable reachability
    ↓
verify exact OpenCode runtime/API/version identity
    ↓
construct and supply exact OpenCode sandbox/permission/tool configuration
    ↓
create one prompt-free session
    ↓
verify effective permission/tool exposure where supported
    ↓
repeat candidate/grant/freshness/session binding checks
    ↓
ADMIT
    ↓
send exactly one authorized prompt / attempt
    ↓
collect runtime events + usage
    ↓
inspect Git/filesystem/protected assets/postconditions
    ↓
terminal evidence
    ↓
independent review / Human acceptance as applicable
```

Absence of Relay-owned process-placement evidence is not an admission defect under this profile.

If the OpenCode runtime cannot satisfy or evidence a constraint that the exact WorkPacket marks as mandatory before execution, admission remains fail-closed with a specific runtime-control gap.

## 5. Strong-boundary selection rule

A strong boundary is not inferred merely because a constraint concerns filesystem, network, credentials, or tools.

`RELAY_MANAGED_STRONG_BOUNDARY` is required only when an authority-bearing source explicitly requires OS/container-level enforcement, placement attestation, or a control strength that runtime-native OpenCode cannot satisfy.

Otherwise, `RUNTIME_NATIVE_CONTROLLED` is admissible when its runtime-native controls and evidence satisfy the exact accepted policy for the work.

This prevents accidental escalation from ordinary coding-agent governance into building a second agent sandbox platform.

## 6. Dogfood 001 re-baseline

Dogfood 001 currently has Execution Authorization 002 bound to AuthorityCandidate 002. That authority explicitly names a qualified `BoundaryScopedRuntimeLauncher` and placement-attester backend as mandatory admission prerequisites.

Those immutable records are not rewritten.

After this amendment is accepted and implemented as needed:

1. Dogfood 001 source coverage/current state must include the amendment and its acceptance/implementation records.
2. A fresh source snapshot must be created.
3. The production resolver/compiler must rerun.
4. Dogfood must select `RUNTIME_NATIVE_CONTROLLED` unless a remaining authority-bearing requirement independently requires the strong-boundary profile.
5. A fresh AuthorityCandidate must be produced.
6. A new exact Human execution authority is required.
7. Pre-admission then verifies runtime-native OpenCode configuration instead of requiring a Relay-owned OS sandbox.

Fixture commit durability remains a separate real blocker and must still be established.

The authorized OpenCode version/provider/model remain exact authority-bearing inputs unless deliberately revised and recompiled.

## 7. Implementation impact

This design amendment does not authorize implementation, but the expected implementation delta is narrow:

- add an explicit execution-profile selection/binding;
- allow the coordinator to take a runtime-native path without `BoundaryScopedRuntimeLauncher`;
- reuse existing OpenCode runtime identity and permission-attestation capabilities where applicable;
- add evidence that the requested runtime-native permission/tool configuration was supplied and, where observable, effective;
- preserve existing strong-boundary code and tests;
- add runtime-native positive and fail-closed tests;
- ensure post-run workspace/protected-asset checks remain part of terminal evaluation.

No new sandbox, OCI backend, namespace manager, cgroup manager, remote executor, parallel runtime framework, or workspace lifecycle is authorized or required by this amendment.

## 8. Invariants preserved

The amendment does not change:

- Human authority as the source of execution permission;
- exact candidate/grant/freshness binding;
- one-attempt semantics;
- WorkPacket authority and mutation scope;
- exact source/fixture identity;
- provider/model/runtime identity checks;
- independent evaluation separation;
- immutable historical records;
- fail-closed handling of unknown or mismatched evidence;
- no silent fallback or substitution.

## 9. Candidate disposition

This is a bounded design amendment candidate under the Human strategic direction above.

It requires independent design review and separate Human acceptance before implementation authority or Dogfood recompilation under the new profile.

**Disposition:** `READY FOR INDEPENDENT DESIGN REVIEW`
