# Relay — Runtime Boundary Binding & Attestation Implementation Evaluation 002

**Document class:** Immutable independent implementation evaluation record
**Status:** IMMUTABLE / ACCEPT
**Date:** 2026-10-27
**Record:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-EVAL-002 — ACCEPT`
**Exact reviewed subject:** `e3b48c9c883d8e2983bbbca3e21f2bc0185f4a46`
**Reviewed parent:** `95584a91b7af4e90037535a2f63756aeddb056cd`

## 1. Decision

```text
RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-EVAL-002
ACCEPT
```

The bounded I001/I002/I003 corrective implementation is accepted.

The correction remains within the Human-accepted Candidate 003 design and does not reopen M001–M003 or any frozen architecture.

Implementation is ready for separate Human implementation acceptance.

## 2. Exact subject and validation

PASS.

Exact candidate:

`e3b48c9c883d8e2983bbbca3e21f2bc0185f4a46`

Exact parent is the implementation-rework authority registry tip:

`95584a91b7af4e90037535a2f63756aeddb056cd`

Exact-head CI:

`40608702388 — SUCCESS`

The candidate changes nine implementation/test files only. No accepted design record or registry entry is mutated by the candidate itself.

Reported validation includes Ruff format/lint, Pyright with zero errors, full test suite with 1,215 passing tests, build, and diff validation.

## 3. I001 — launch ownership and composability

PASS / CLOSED.

The runtime-level `BOUNDARY_MANAGED_LAUNCH` capability has been removed.

The coordinator no longer requires the Slice 2.1 runtime descriptor to claim boundary-managed launch before using the exact Slice 2.4 `BoundaryScopedRuntimeLauncher`.

`OpenCodeRuntime.create_session_v2()` likewise no longer requires OpenCode to claim ownership of boundary launch.

Strong-boundary placement remains established by:

```text
BoundaryScopedRuntimeLauncher
→ WorkspaceBoundaryRef
→ launch_runtime()
→ RuntimePlacementAttestation
→ exact trust/boundary/launch verification
```

The runtime still owns the behaviors assigned by Candidate 003: prompt-free V2 session binding, effective permission attestation, and prompt admission.

Missing launcher/attester evidence continues to fail closed.

## 4. I002 — provider-neutral V2 endpoint identity

PASS / CLOSED.

The shared `RuntimeRequestV2.endpoint_identity` no longer hardcodes loopback HTTP/HTTPS.

The shared contract now requires an explicit absolute authority, rejects embedded credentials, query/fragment ambiguity, whitespace, and malformed Unix identities, while allowing an exact remote executor control URI.

A deterministic test proves acceptance of:

`https://executor.example:8443/runtime/control`

OpenCode retains its own adapter-specific loopback HTTP(S) policy with explicit port and no credentials.

This restores the accepted provider-neutral ownership split:

```text
shared V2 identity:
provider-neutral exact endpoint identity

OpenCode adapter:
loopback/private control-channel policy
```

No remote backend is claimed or implemented.

## 5. I003 — positive coordinator composition validation

PASS / CLOSED.

The coordinator test suite now exercises a deterministic strong-boundary path through `execute_governed_attempt()`.

The positive scenario proves the exact ordering:

```text
launch_runtime
→ create_session_v2
→ attest_permissions_v2
→ final admission
→ final freshness
→ open_execution_v2
```

It also proves:

- exactly one V2 prompt-free session;
- exactly one permission attestation;
- exactly one V2 prompt admission;
- a workspace launcher composes with a runtime that does not own boundary launch;
- exact V2 request, placement attestation and permission-attestation ref reach the final subject;
- continuity and runtime teardown evidence reach the terminal evidence bundle;
- the provider-neutral remote endpoint is carried by the generic V2 request.

Negative coordinator scenarios cover permission evidence that is:

- missing;
- incomplete;
- stale;
- mismatched.

Each negative scenario creates exactly one prompt-free V2 session, performs no `open_execution_v2()`, performs no legacy prompt admission, invokes runtime teardown once, and retains exact session/teardown evidence in the boundary failure.

No replacement session or second attempt is created.

## 6. Additional stale-evidence guard

PASS.

The implementation now rejects a permission observation whose `observed_from` predates the exact session's `created_at`.

The same condition is represented in both preparation-time validation and final boundary evidence evaluation.

This is consistent with Candidate 003's requirement that permission evidence describe the exact prompt-free session rather than an earlier mutable observation.

## 7. Frozen implementation/design preservation

PASS.

The corrective diff does not alter the accepted semantics for:

- RuntimeLaunchSubject;
- RuntimePlacementAttestation and trust binding;
- RuntimePermissionAttestation identity/digest/ref;
- request/session/placement binding;
- prompt-free session ordering;
- final admission before prompt;
- continuity and teardown;
- V1 compatibility;
- LocalClone security ceiling;
- Slice 2.1 / 2.4 / 3.1 ownership;
- Dogfood runtime/provider/model constraints.

No parallel planner, authority system, runtime framework, or workspace lifecycle is introduced.

## 8. Concrete backend status

SEPARATE DOWNSTREAM GATE.

This acceptance does not assert that a concrete enforcing backend exists on the current host.

The implementation correctly remains fail-closed without a qualified `BoundaryScopedRuntimeLauncher` and trustworthy placement evidence.

The previously observed Bubblewrap/Docker host limitations therefore remain an environment/backend qualification matter rather than a contract-correctness defect.

## 9. Authority and execution state

This evaluation does not authorize:

- implementation acceptance on behalf of the Human;
- Dogfood WorkPacket or WorkspacePlan materialization;
- live workspace provisioning;
- OpenCode Dogfood launch/session/prompt;
- credential access;
- provider/model calls;
- Dogfood admission or consumption;
- canonical promotion.

Dogfood 001 remains:

`AUTHORIZED / NOT ADMITTED / NOT CONSUMED`

## 10. Final disposition

```text
Exact reviewed subject:
e3b48c9c883d8e2983bbbca3e21f2bc0185f4a46

Exact-head CI:
PASS

I001:
CLOSED

I002:
CLOSED

I003:
CLOSED

Accepted Candidate 003 preservation:
PASS

Implementation:
ACCEPT

Human implementation acceptance:
PENDING

Dogfood 001:
AUTHORIZED / NOT ADMITTED / NOT CONSUMED
```

**The corrected runtime-boundary implementation is independently accepted. The next gate is Human implementation acceptance of this exact candidate and EVAL-002.**
