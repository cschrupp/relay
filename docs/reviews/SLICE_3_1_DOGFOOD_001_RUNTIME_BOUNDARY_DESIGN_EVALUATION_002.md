# Relay — Runtime Boundary Binding & Attestation Candidate 002 — Independent Review 002

**Document class:** Immutable independent design evaluation record
**Status:** IMMUTABLE / REWORK — NARROW
**Date:** 2026-10-27
**Project:** Relay
**Phase:** 3 — First Governed Autonomous Engineering Loop
**Workstream:** Dogfood 001 runtime-boundary contract closure
**Evaluation:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-002 — REWORK / NARROW`
**Exact reviewed subject:** `bb225507363b22c860e4d5082dd9494160afed77`
**Reviewed parent:** `c3a1e70a6cc43d0360842c79b07e77518562221b`

## 1. Decision

```text
RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-002
REWORK / NARROW
```

Candidate 002 successfully closes M001. The managed-launch architecture and all previously accepted substantive design decisions remain accepted in substance.

Two new exactness findings remain:

- M002 — authority provenance labels point to registry commits rather than authority-creation commits;
- M003 — RuntimePermissionAttestation is described as an immutable/content-digest-bound identity and later consumed by digest, but its own canonical digest/ref rule is not defined.

No architectural restart is warranted.

## 2. Exact repository subject

PASS.

The reviewed commit changes only:

- `.relay/registry.json`; and
- `docs/slices/SLICE_3_1_RUNTIME_BOUNDARY_BINDING_AND_ATTESTATION_DESIGN_CANDIDATE_002.md`.

Registered Candidate 002 artifact:

```text
artifact_id:
art_48af3cbc-7c42-4abb-837a-d2c7536b4742

content_digest:
sha256:90c2fa7dd803edee8971ad7378b52c8ed4ce35b16dc26e649b987e7c696e3aaf
```

Independent SHA-256 recomputation of the exact remote bytes matches the registered digest.

Registry state at the reviewed subject:

```text
artifacts:            391
canonical pointers:   5
ordering violations:  0
```

## 3. Exact-head CI

PASS.

Exact-head CI run `40569054922` is bound to the reviewed candidate SHA and completed `SUCCESS`.

## 4. M001 status

**CLOSED.**

Candidate 002 correctly separates placement evidence from runtime permission/exposure evidence.

`RuntimePlacementAttestation` now contains placement/boundary facts only. `RuntimePermissionAttestation` is separately owned by Slice 2.1 runtime integration and is produced for the exact prompt-free runtime session.

The lifecycle is corrected to:

```text
grant / reservation
→ WorkPacket / conformance
→ WorkspacePlan / workspace / boundary
→ RuntimeLaunchSubject
→ managed runtime-server launch
→ RuntimePlacementAttestation
→ RuntimeExecutionRequestV2
→ create exactly one runtime session
   NO PROMPT
→ RuntimeSessionBinding
→ RuntimePermissionAttestation
→ final ExecutionSubject
→ repeat freshness / reservation / binding / admission checks
→ open_execution()
→ exactly one prompt
```

This matches the accepted OpenCode separation between prompt-free session creation and prompt admission.

The digest graph is also corrected and acyclic:

```text
RuntimeLaunchSubject
→ RuntimePlacementAttestation
→ RuntimeExecutionRequestV2 / request_digest_v2
→ RuntimeSessionBinding
→ RuntimePermissionAttestation
→ final Slice 3.1 ExecutionSubject
```

The expected placement attester is now pinned through the provider/boundary trust binding. Unknown or substituted attesters fail closed.

## 5. Frozen architecture preservation

PASS.

Candidate 002 preserves the previously accepted substantive decisions:

- managed launch as the default for strong-boundary execution;
- external attach only with exact independent placement proof;
- WorkspaceBoundaryRef;
- RuntimeLaunchSubject;
- RuntimePlacementAttestation;
- RuntimeExecutionRequestV2;
- process-tree containment;
- anti-replay nonce/challenge semantics;
- network/provider-transport separation;
- credential separation;
- runtime-counter versus OS/process-tree resource distinction;
- continuity and teardown semantics;
- V1 compatibility / V2 strong-boundary semantics;
- LocalCloneWorkspaceProvider security ceiling;
- Slice 2.1 / 2.4 / 3.1 ownership split;
- Dogfood runtime/provider/model constraints and attempt semantics.

No parallel planner, workspace lifecycle, runtime framework, or authority system is introduced.

## 6. M002 — Authority provenance labels are incorrect

**Severity:** BLOCKING EXACTNESS / PROVENANCE
**Scope:** NARROW DOCUMENT CORRECTION

Candidate 002 states:

```text
Design authority commit:
6e177a68f57545d7ce7c4cc451430a35117f6e4c

Rework authority commit:
c3a1e70a6cc43d0360842c79b07e77518562221b
```

Those two commits are registry-only registration commits.

The actual authority artifact creation commits are:

```text
RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-AUTH-001
authority artifact creation commit:
0504263c41d6fa90c726ce0d3c6f2ee789068d6c

registry registration commit:
6e177a68f57545d7ce7c4cc451430a35117f6e4c

RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-REWORK-AUTH-001
authority artifact creation commit:
875520e59b790becec31058dc820da670aa63365

registry registration commit:
c3a1e70a6cc43d0360842c79b07e77518562221b
```

Candidate 001 correctly identified the original design-authority creation commit. Candidate 002 must not silently redefine the meaning of `authority commit`.

Required correction:

- either replace the two authority-commit values with the true artifact creation commits; or
- explicitly label both creation and registry-registration commits separately.

No authority semantics are reopened.

## 7. M003 — RuntimePermissionAttestation lacks an exact digest/ref rule

**Severity:** BLOCKING CONTRACT EXACTNESS
**Scope:** NARROW IDENTITY DEFINITION

Candidate 002 says:

```text
Use five distinct immutable identities.
Every reference is immutable or content-digest bound.
```

and later says Slice 3.1 includes the RuntimePermissionAttestation digest in the final ExecutionSubject.

However, the conceptual `RuntimePermissionAttestation` schema does not define:

- an attestation ID;
- an attestation content digest;
- a ref structure; or
- a canonical digest rule equivalent to the explicit launch-subject/request digest rules.

This leaves an implementation ambiguity at the exact point the final ExecutionSubject is supposed to bind immutable permission evidence.

### Required correction

Define one exact identity rule. A minimal acceptable direction is:

```text
RuntimePermissionAttestation
  attestation_id
  ... existing Candidate 002 fields ...

permission_attestation_digest =
  SHA256(canonical(RuntimePermissionAttestation payload excluding self-digest field))

RuntimePermissionAttestationRef
  attestation_id
  content_digest
```

or an equivalent repository-consistent immutable/content-digest-bound representation.

The exact naming may follow existing conventions, but the design must make these semantics explicit:

1. the attestation has one stable immutable identity;
2. exact canonical bytes determine its content digest;
3. Slice 3.1 binds the exact ref/digest in the final ExecutionSubject;
4. changed effective permissions, completeness, session, placement, request, adapter identity, or provenance change the attestation digest;
5. no latest/current lookup or endpoint-based substitution exists.

`request_digest_v2` must remain unchanged by this correction and must continue to exclude the later permission attestation, preserving acyclicity.

## 8. Rework boundary

The following are closed/frozen and must not be reopened:

- M001 permission/placement ownership correction;
- prompt-free session ordering;
- attester trust binding;
- managed-launch architecture;
- attach-mode fail-closed semantics;
- boundary/launch/placement/request identity model;
- process-tree containment;
- network, credential, resource, continuity and teardown design;
- V1/V2 versioning;
- LocalClone ceiling;
- Slice 2.1 / 2.4 / 3.1 ownership.

The remaining rework is limited to M002 and M003.

No new host probing, external research, implementation work, runtime launch, session creation, credential use, provider/model call, or Dogfood execution is required.

## 9. Final disposition

```text
Exact reviewed subject:
bb225507363b22c860e4d5082dd9494160afed77

Repository / registry:
PASS

Registered Candidate 002 digest:
PASS

Exact-head CI:
PASS

M001:
CLOSED

Frozen architecture preservation:
PASS

M002 authority provenance labels:
REWORK REQUIRED

M003 RuntimePermissionAttestation identity/digest:
REWORK REQUIRED

Disposition:
REWORK / NARROW

Implementation:
NOT AUTHORIZED

Dogfood 001:
AUTHORIZED / NOT ADMITTED / NOT CONSUMED
```

Candidate 002 requires only M002 and M003 correction. No architectural restart is warranted.
