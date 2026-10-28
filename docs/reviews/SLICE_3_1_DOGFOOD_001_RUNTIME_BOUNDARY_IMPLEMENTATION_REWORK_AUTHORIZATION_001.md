# Relay — Runtime Boundary Implementation Rework Authority 001

**Document class:** Immutable Human Authority record
**Status:** IMMUTABLE / AUTHORIZED
**Date:** 2026-10-27
**Record:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-REWORK-AUTH-001 — AUTHORIZED`

## Exact review basis

Reviewed implementation candidate:

`f1a20681dca90a933472314ab2d61ed5a772ed34`

Independent evaluation:

`RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-EVAL-001 — REWORK / NARROW`

Evaluation digest:

`sha256:d289f2cad05dd219c32e6fe0f33b1a060b2c1c72be4380086be3ffc089158c5e`

Human-accepted design remains Candidate 003:

`cb0ce54b94ac823a9327f557cc9968fffdd14e4d`

## Human decision

The Human authorizes one narrow corrective implementation cycle limited to I001, I002, and I003.

### I001 — launch ownership/composability

Correct the strong-boundary launch capability ownership so the Slice 2.4 `BoundaryScopedRuntimeLauncher` establishes and attests boundary-managed placement.

The Slice 2.1 runtime adapter must not be required to claim ownership of the workspace boundary launch merely to create the exact V2 prompt-free session.

The corrected implementation must preserve:

- exact boundary/placement verification before session preparation;
- V2 session binding;
- effective permission attestation;
- final prompt admission through `open_execution_v2()`;
- fail-closed behavior when a qualified launcher/attester is absent.

### I002 — provider-neutral V2 endpoint identity

Remove the local-only loopback/Unix restriction from the shared provider-neutral `RuntimeRequestV2` identity contract.

The shared schema must continue to require an exact, explicit, credential-free endpoint/control identity with no ambiguous discovery semantics.

Runtime/backend-specific restrictions remain owned by the exact adapter/provider policy. OpenCode may continue to require its accepted private/loopback control-channel constraint.

No remote backend implementation is authorized or required by this correction.

### I003 — positive coordinator validation

Add deterministic positive strong-boundary coordinator coverage using fakes or equivalent test doubles.

The test must demonstrate the accepted sequence:

```text
launch_runtime
→ create_session_v2
→ attest_permissions_v2
→ final freshness/admission
→ open_execution_v2
```

and verify at minimum:

- exactly one prompt-free session;
- no prompt if permission evidence is absent, incomplete, stale, or mismatched;
- a qualified workspace launcher composes with a runtime adapter that does not own boundary launch;
- exact placement/session/permission evidence reaches the final subject/evidence path;
- no replacement session or new attempt is created on failure.

## Frozen scope

Candidate 003 design, M001–M003 closure, and all implementation work outside I001–I003 remain frozen.

No redesign of Relay authority, WorkspacePlan, runtime lifecycle, admission lifecycle, V1 compatibility, attester trust, continuity/teardown, or LocalClone security semantics is authorized.

## Authorized work

The worker may modify only the implementation/test surfaces necessary for I001–I003, plus exact documentation/registry evidence for the corrective candidate.

Relevant existing surfaces include:

- `src/relay_engine/agent_runtime/`
- `src/relay_engine/execution_workspace/`
- `src/relay_engine/coding_execution/`
- corresponding unit/integration tests.

The worker may run repository validation and repair failures caused by this bounded correction.

## Explicit non-authority

This authority does not permit live Dogfood execution, fixture access, credential reads, provider/model calls, workspace provisioning for Dogfood, package installation, canonical promotion, or self-acceptance.

Dogfood 001 remains:

`AUTHORIZED / NOT ADMITTED / NOT CONSUMED`

## Required terminal

Successful terminal:

`RUNTIME_BOUNDARY_IMPLEMENTATION_REWORK_CANDIDATE_COMPLETE`

If the correction would require changing Human-accepted Candidate 003 semantics:

`ACCEPTED_DESIGN_CONTRADICTION`

If required provenance or safe correction is unavailable:

`FAIL_CLOSED`

On the successful terminal, proceed directly to independent implementation re-review.

**Disposition:** `AUTHORIZED`
