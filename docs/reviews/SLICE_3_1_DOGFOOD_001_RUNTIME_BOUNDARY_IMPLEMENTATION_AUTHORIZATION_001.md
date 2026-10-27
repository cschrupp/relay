# Relay — Runtime Boundary Binding & Attestation Implementation Authority 001

**Document class:** Immutable Human Authority record
**Status:** IMMUTABLE / AUTHORIZED
**Date:** 2026-10-27
**Record:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-AUTH-001 — AUTHORIZED`

## Exact accepted design basis

Candidate 003 commit:

`cb0ce54b94ac823a9327f557cc9968fffdd14e4d`

Candidate 003 digest:

`sha256:9483f7672c9ff1d92652103aa3e63e608ebd5c4bb4bbd9726e6420b3adb1f6a8`

Independent design evaluation:

`RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-003 — ACCEPT`

Evaluation digest:

`sha256:827a49952cb753f1df5766931c8d369614b7e4462e9eadae3339509a182f31d1`

Human design acceptance:

`RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-ACCEPT-001 — ACCEPTED`

Acceptance digest:

`sha256:d6bbb910431e6b083f1d4b30e2af0e9d09f6d4d14462a00a6f10eaaecd1070c2`

M001, M002, and M003 are closed.

## Human decision

The Human authorizes implementation of the accepted Candidate 003 contract as one cohesive bounded worker task.

The worker may plan, implement, validate, repair, and self-review internally without additional Human gates, provided all work remains inside this authority.

Implementation should occur on a dedicated implementation branch based on the exact authority lineage.

## Authorized implementation scope

### Slice 2.4 workspace layer

Implement the accepted additive workspace-boundary contract needed by Candidate 003, including as applicable:

- exact boundary reference and immutable evidence identities;
- provider-bound expected placement-attester identity/trust binding;
- boundary-scoped runtime launch capability/protocol;
- placement-attestation representation and validation;
- continuity and teardown evidence hooks;
- conformance evaluation for boundary-sensitive properties;
- preservation of the current LocalClone security ceiling.

No existing LocalClone capability may be upgraded by assertion.

### Slice 2.1 runtime layer

Implement the accepted additive runtime contract, including as applicable:

- versioned runtime request V2;
- RuntimeLaunchSubject and canonical digest;
- placement-attestation binding/verification;
- prompt-free exact session preparation;
- RuntimePermissionAttestation;
- stable permission-attestation identity;
- canonical SHA-256 digest and exact immutable ref;
- session/request/placement/profile binding;
- fail-closed permission completeness semantics;
- OpenCode adapter integration points required by the accepted design without performing a live Dogfood run.

The existing V1 contract must remain compatible for lower-strength use cases and must not silently claim V2 assurance.

### Slice 3.1 coding-execution layer

Implement the accepted coordinator composition needed to:

- bind exact workspace boundary and placement evidence;
- bind request V2 and exact RuntimeSessionBinding;
- bind exact RuntimePermissionAttestationRef;
- repeat final freshness/binding checks before prompt admission;
- keep `open_execution()` as the prompt-admission boundary;
- retain boundary/placement/permission/continuity/teardown evidence in the existing result/evidence path;
- preserve one-attempt / one-session semantics and existing authority ownership.

No second admission state machine, planner, runtime framework, or workspace lifecycle may be introduced.

## Concrete backend allowance

The worker may add the smallest provider/backend or launcher implementation needed to exercise the accepted contract if it can be built with existing repository dependencies and already available host primitives.

Any such backend must:

- implement the accepted provider-neutral contract rather than introducing backend-specific governance semantics;
- declare only controls it can actually establish;
- produce exact instance evidence;
- fail closed when a required control is unsupported or unobservable;
- remain testable without Dogfood credentials, provider/model calls, or a live Dogfood OpenCode session.

If a full strong-boundary backend cannot be implemented safely under these constraints, the contract implementation may still complete and the result must identify the exact remaining backend capability gap. Do not fake or overstate conformance.

## Authorized source and test surfaces

The worker may modify existing implementation and tests under:

- `src/relay_engine/execution_workspace/`
- `src/relay_engine/agent_runtime/`
- `src/relay_engine/coding_execution/`
- corresponding package exports
- `tests/unit/`
- `tests/integration/`

Small adjacent changes are permitted only when mechanically required by the accepted contract, imports, typing, serialization, persistence compatibility, or architecture checks.

Documentation and registry updates necessary to record the implementation candidate and evidence are authorized.

No dependency/package installation is authorized. If an unavailable dependency is required, stop with the appropriate blocked terminal rather than installing it.

## Mandatory validation

The implementation candidate must include deterministic tests covering at least:

- canonical launch/request/permission digests;
- permission-attestation stable identity/ref semantics;
- digest mutation on material permission-evidence changes;
- stale/tampered/mismatched placement and permission evidence;
- expected-attester mismatch;
- request/session/placement substitution;
- exactly one prompt-free session before final admission;
- no prompt when permission evidence is missing/incomplete/mismatched;
- V1 compatibility and no silent V1-to-V2 assurance upgrade;
- LocalClone security ceiling;
- process-tree/continuity evidence contract behavior using deterministic fakes;
- coordinator final binding/admission ordering;
- one-attempt / one-session recovery and retry invariants.

Run the relevant focused suites and the full repository test suite or the repository's accepted equivalent validation.

## Explicit non-authority

This authority does not permit:

- Human authority issuance or mutation beyond this record;
- Dogfood WorkPacket or WorkspacePlan materialization;
- Dogfood fixture access;
- live Dogfood workspace provisioning;
- live OpenCode Dogfood server/session/prompt execution;
- credential reads or secret material use;
- provider/model calls;
- external network execution for Dogfood;
- Dogfood admission or consumption;
- weakening accepted controls;
- changing the accepted Dogfood runtime/provider/model constraints;
- canonical promotion, merge, or canonical-pointer mutation;
- accepting or promoting the worker's own implementation.

Dogfood 001 remains:

`AUTHORIZED / NOT ADMITTED / NOT CONSUMED`

## Required implementation terminals

Use exactly one:

### `RUNTIME_BOUNDARY_IMPLEMENTATION_CANDIDATE_COMPLETE`

The accepted contract is implemented, deterministic validation passes, and the exact implementation candidate is ready for independent review. Any remaining live backend/runtime qualification is explicitly separated from contract correctness.

### `RUNTIME_BOUNDARY_BACKEND_CAPABILITY_BLOCKED`

The contract implementation is materially complete but a required concrete backend capability cannot be implemented or established under the authorized environment. Record the exact missing capability without weakening semantics.

### `ACCEPTED_DESIGN_CONTRADICTION`

Implementation reveals a contradiction in the Human-accepted Candidate 003 that cannot be resolved without changing accepted semantics.

### `FAIL_CLOSED`

Required provenance is missing/conflicting or safe implementation cannot proceed inside this authority.

## Continuation

On `RUNTIME_BOUNDARY_IMPLEMENTATION_CANDIDATE_COMPLETE`, proceed directly to independent implementation review.

Implementation review/acceptance is separate from Dogfood execution admission.

**Disposition:** `AUTHORIZED`
