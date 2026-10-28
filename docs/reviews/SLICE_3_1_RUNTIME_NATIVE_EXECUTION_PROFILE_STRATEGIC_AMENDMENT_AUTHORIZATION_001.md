# Relay Slice 3.1 — Runtime-Native Execution Profile Strategic Amendment Authorization 001

**Document class:** Immutable Human strategic amendment authority
**Status:** IMMUTABLE / AUTHORIZED
**Date:** 2026-10-28
**Record:** `RLY-S31-RUNTIME-NATIVE-PROFILE-STRATEGIC-AMEND-001 — AUTHORIZED`

## Human decision

Human Authority revises the intended Relay/OpenCode execution architecture for ordinary coding-agent execution.

Relay is the governance, authorization, orchestration, and evidence layer. OpenCode is the selected coding-agent execution runtime. Relay MUST NOT require a second Relay-owned OS/container sandbox around OpenCode merely to duplicate sandbox or permission controls that the selected runtime is already intended to provide.

For an execution profile that explicitly delegates execution containment to the selected runtime, Relay may satisfy admission by verifying the exact runtime identity and the exact runtime-native sandbox/permission configuration supplied to that runtime, observing the effective runtime permission/tool exposure where the adapter supports it, and validating terminal repository/workspace evidence and authorized postconditions.

This decision does not remove the previously accepted strong-boundary architecture. A Relay-managed strong boundary remains available as a separate higher-assurance execution profile when the exact WorkPacket, WorkspacePlan, policy, Human authority, or external requirement explicitly demands OS/container-level containment and placement attestation.

## Required architectural amendment

A bounded Slice 3.1 amendment shall distinguish at least these execution profiles:

```text
RUNTIME_NATIVE_CONTROLLED
    OpenCode/runtime-native sandbox and permission controls are the execution boundary.
    Relay verifies exact runtime identity, supplied configuration/instructions,
    effective permissions/tool exposure where observable, and post-run evidence.
    BoundaryScopedRuntimeLauncher and OS process-placement attestation are NOT
    admission prerequisites unless independently required by the exact work.

RELAY_MANAGED_STRONG_BOUNDARY
    Existing accepted strong-boundary path remains applicable.
    BoundaryScopedRuntimeLauncher, WorkspaceBoundaryRef, placement attestation,
    continuity and teardown evidence remain required at the accepted strength.
```

The amendment must preserve fail-closed behavior: if the selected profile requires a control that the selected runtime cannot represent, configure, verify, or evidence at the required strength, Relay must report the exact gap rather than silently weakening the control.

## Dogfood 001 consequence

The existing `RLY-S31-DOGFOOD-001-EXEC-AUTH-002` remains an immutable historical authority bound to AuthorityCandidate 002 and its explicit strong-boundary prerequisites. This strategic amendment does not rewrite or waive that record.

Dogfood 001 must be recompiled under the amended execution profile after the amendment is independently reviewed, Human-accepted, and implemented as necessary. Any changed AuthorityCandidate requires a fresh exact Human execution authority before admission.

The exact fixture/source durability requirement remains valid and is not waived. Exact runtime/provider/model identity also remains authority-bearing unless separately amended through the normal process.

## Scope boundary

This authority permits only the bounded design/documentation amendment needed to express the runtime-native execution profile and its relationship to the existing strong-boundary profile.

It does not authorize:
- live Dogfood execution or prompt admission;
- silent reuse or reinterpretation of Execution Authorization 002;
- weakening an exact WorkPacket constraint without recompilation;
- mutation of historical immutable records;
- implementation changes beyond those later authorized against the accepted amendment;
- canonical promotion of an unreviewed amendment.

**Disposition:** `AUTHORIZED — BOUNDED DESIGN AMENDMENT`
