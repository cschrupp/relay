# Relay — Runtime Boundary Binding & Attestation Implementation Evaluation 001

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE / REWORK — NARROW  
**Date:** 2026-10-27  
**Record:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-EVAL-001 — REWORK / NARROW`  
**Exact reviewed subject:** `f1a20681dca90a933472314ab2d61ed5a772ed34`  
**Reviewed parent:** `3e8c64d31d94d038ebc2041c45661fae69e72d96`

## 1. Decision

```text
RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-EVAL-001
REWORK / NARROW
```

The implementation is strong in substance and remains within the accepted Slice 2.1 / 2.4 / 3.1 architecture, but three bounded implementation defects prevent acceptance.

No design reopen is required.

## 2. Exact subject and validation

PASS.

Exact candidate branch head:

`f1a20681dca90a933472314ab2d61ed5a772ed34`

Exact-head CI:

`40593965777 — SUCCESS`

The candidate changes only the authorized runtime-boundary implementation surfaces and tests:

- agent_runtime
- execution_workspace
- coding_execution
- runtime-boundary unit tests.

The reported full test/build/static validation is consistent with the exact-head CI quality job.

No Dogfood execution evidence or authority mutation is present.

## 3. Implementation areas that pass

### I000-A — Contract identities

PASS.

The candidate implements:

- RuntimeLaunchSubject;
- RuntimeRequestV2;
- WorkspaceBoundaryRef;
- RuntimePlacementAttestation and exact ref;
- RuntimePermissionAttestation and exact immutable ref;
- canonical digests;
- request/session/placement/permission binding;
- continuity and teardown evidence types.

M001–M003 design closure is preserved.

### I000-B — Permission ordering

PASS in structure.

The coordinator prepares:

```text
boundary launch
→ placement attestation
→ RuntimeRequestV2
→ prompt-free session
→ continuity evidence
→ RuntimePermissionAttestation
→ final revalidation
→ prompt admission
```

The prompt remains behind `open_execution_v2()`.

### I000-C — Fail-closed semantics

PASS in principle.

Missing/mismatched placement, session, permission, continuity, provider/model identity, or trust binding blocks admission.

OpenCode does not pretend that the current host/runtime is already strongly isolated.

### I000-D — No unauthorized live execution

PASS.

No Dogfood fixture, prompt, provider/model call, credential read, or authority consumption was performed.

## 4. I001 — Boundary-launch capability is assigned to the wrong owner

**Severity:** BLOCKING  
**Scope:** NARROW IMPLEMENTATION CORRECTION

Candidate 003 assigns managed runtime launch to the Slice 2.4 workspace/provider boundary capability.

The implementation correctly introduces:

`BoundaryScopedRuntimeLauncher`

on the workspace-provider side.

However, the coordinator additionally requires:

```text
RuntimeCapability.BOUNDARY_MANAGED_LAUNCH
```

on the Slice 2.1 runtime descriptor before it will call the workspace launcher.

`OpenCodeRuntime.create_session_v2()` independently enforces the same runtime capability.

At the same time, `OpenCodeRuntime.describe()` intentionally never advertises that capability.

The result is a structural dead end:

```text
qualified workspace launcher exists
        ↓
coordinator checks runtime descriptor
        ↓
OpenCode lacks BOUNDARY_MANAGED_LAUNCH
        ↓
strong-boundary execution always blocks
```

This contradicts the accepted design, which allows the OpenCode adapter to remain the transport/session adapter behind an independently qualified workspace-boundary launcher.

### Required correction

Launch qualification must be owned by the exact `BoundaryScopedRuntimeLauncher` / workspace boundary contract.

The runtime adapter should be required only to support the Slice 2.1 behaviors it actually owns, such as:

- V2 prompt-free session binding;
- effective permission attestation;
- V2 prompt admission.

Do not require OpenCode itself to claim that it created or owns the workspace boundary.

The `BOUNDARY_MANAGED_LAUNCH` runtime capability should be removed from this admission dependency, or redefined so it does not duplicate Slice 2.4 launch ownership.

## 5. I002 — Generic RuntimeRequestV2 hardcodes a local endpoint policy

**Severity:** BLOCKING CONTRACT DRIFT  
**Scope:** NARROW SCHEMA CORRECTION

The accepted Candidate 003 contract is provider-neutral and explicitly allows future remote isolated executors.

The generic `RuntimeRequestV2.endpoint_identity` validator currently permits only:

- loopback HTTP/HTTPS with an explicit port; or
- absolute Unix sockets.

That is an OpenCode/local-control-channel policy embedded in the provider-neutral request schema.

A legitimate future remote isolated executor cannot be represented by the accepted generic V2 model.

### Required correction

Keep the shared V2 identity contract provider-neutral.

The generic endpoint identity should enforce only the shared invariants required by the design, such as:

- explicit exact identity;
- no embedded credentials;
- no ambiguous mutable discovery.

Backend/runtime-specific endpoint constraints belong in the exact adapter/provider/WorkspacePlan policy.

For OpenCode strong-boundary execution, the adapter may continue to enforce loopback/private-control-channel requirements.

No remote backend needs to be implemented in this rework; only remove the schema-level contradiction.

## 6. I003 — Mandatory positive coordinator-path validation is missing

**Severity:** BLOCKING VALIDATION GAP  
**Scope:** TEST-ONLY AFTER I001/I002 CORRECTION

The implementation authority explicitly required deterministic validation of coordinator final binding/admission ordering and one-session strong-boundary composition.

The new runtime-boundary test file contains model/evaluator tests and an OpenCode negative capability test, but no positive test of:

`execute_governed_attempt()`

with a deterministic fake `BoundaryScopedRuntimeLauncher` and V2 runtime.

The existing coordinator/scenario/OpenCode/workspace tests also do not reference:

- `boundary_runtime_launcher`;
- `RuntimeRequestV2`;
- `create_session_v2`.

Therefore the exact defect in I001 is invisible to the current test suite.

### Required test

Add at least one deterministic positive strong-boundary coordinator scenario proving ordering equivalent to:

```text
launch_runtime
< create_session_v2
< attest_permissions_v2
< final admission/freshness
< open_execution_v2
```

and prove:

- exactly one prompt-free session is created;
- no prompt is admitted when permission evidence is missing/incomplete/mismatched;
- a qualified workspace launcher can compose with a runtime adapter that does not itself own boundary launch;
- exact placement/session/permission refs reach the final ExecutionSubject/evidence bundle;
- no second session/attempt is created on failure.

This may use fakes only; no live backend or provider call is required.

## 7. Concrete backend status

NONBLOCKING FOR THIS REVIEW.

The candidate correctly fails closed without a concrete qualified boundary launcher/attester.

The reported Bubblewrap/Docker host limitations do not justify weakening the contract and are not required to be solved in this correction.

A concrete production backend remains a downstream capability/qualification gate.

## 8. Rework boundary

The following are accepted in substance and must not be reopened:

- Candidate 003 design;
- M001/M002/M003 design closure;
- versioned request/digest direction;
- exact placement and permission evidence identities;
- prompt-free session before permission attestation;
- final prompt admission through `open_execution_v2()`;
- placement-attester trust binding;
- continuity/teardown evidence model;
- LocalClone security ceiling;
- V1 compatibility;
- Slice 2.1 / 2.4 / 3.1 ownership.

The rework is limited to I001, I002, and I003.

No live Dogfood work is required or authorized.

## 9. Final disposition

```text
Exact reviewed subject:
f1a20681dca90a933472314ab2d61ed5a772ed34

Exact-head CI:
PASS

Core contract models:
PASS

M001–M003 preservation:
PASS

I001 launch ownership/composability:
REWORK REQUIRED

I002 provider-neutral endpoint schema:
REWORK REQUIRED

I003 positive coordinator validation:
REWORK REQUIRED

Disposition:
REWORK / NARROW

Implementation acceptance:
NOT GRANTED

Dogfood 001:
AUTHORIZED / NOT ADMITTED / NOT CONSUMED
```

**The implementation does not require architectural redesign. Correct the capability ownership, restore provider-neutral V2 endpoint semantics, and add the missing positive coordinator composition test.**
