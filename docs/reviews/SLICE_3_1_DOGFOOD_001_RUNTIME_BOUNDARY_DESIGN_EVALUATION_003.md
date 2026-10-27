# Relay — Runtime Boundary Binding & Attestation Candidate 003 — Independent Review 003

**Document class:** Immutable independent design evaluation record
**Status:** IMMUTABLE / ACCEPT
**Date:** 2026-10-27
**Project:** Relay
**Phase:** 3 — First Governed Autonomous Engineering Loop
**Workstream:** Dogfood 001 runtime-boundary contract closure
**Evaluation:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-003 — ACCEPT`
**Exact reviewed subject:** `cb0ce54b94ac823a9327f557cc9968fffdd14e4d`
**Reviewed parent:** `c9e422d41244db96ad4b6e34b87423ff2b60527a`

## 1. Decision

```text
RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-003
ACCEPT
```

Candidate 003 closes M002 and M003 without reopening M001 or drifting any frozen architecture.

The runtime-boundary binding and attestation design is accepted for Human design acceptance.

Implementation remains unauthorized.

## 2. Exact repository subject

PASS.

The exact candidate commit changes only:

- `.relay/registry.json`; and
- `docs/slices/SLICE_3_1_RUNTIME_BOUNDARY_BINDING_AND_ATTESTATION_DESIGN_CANDIDATE_003.md`.

Registered Candidate 003:

```text
artifact_id:
art_b80eba8d-20a5-4672-915c-da19e32ef4e6

content_digest:
sha256:9483f7672c9ff1d92652103aa3e63e608ebd5c4bb4bbd9726e6420b3adb1f6a8
```

The exact-head CI run `40575292913` is bound to the reviewed SHA and completed `SUCCESS`.

Registry at the reviewed subject:

```text
artifacts:            394
canonical pointers:   5
ordering violations:  0
```

## 3. M002 — authority provenance

PASS / CLOSED.

Candidate 003 now distinguishes authority-artifact creation commits from registry-registration commits.

Original runtime-boundary design authority:

```text
artifact creation:
0504263c41d6fa90c726ce0d3c6f2ee789068d6c

registry registration:
6e177a68f57545d7ce7c4cc451430a35117f6e4c
```

M001 rework authority:

```text
artifact creation:
875520e59b790becec31058dc820da670aa63365

registry registration:
c3a1e70a6cc43d0360842c79b07e77518562221b
```

The M002/M003 authority itself is also recorded consistently:

```text
artifact creation:
3d252a7f8d6fb820f72cb1671f97b69b2210c501

registry registration:
c9e422d41244db96ad4b6e34b87423ff2b60527a
```

No authority semantics are changed.

## 4. M003 — RuntimePermissionAttestation identity

PASS / CLOSED.

Candidate 003 now defines:

- a stable Relay-owned `attestation_id`;
- explicit `schema_version`;
- the exact session/request/placement/runtime/permission/provenance payload;
- canonical UTF-8 JSON serialization with sorted keys, compact separators, non-finite values forbidden, and deterministic ordering rules;
- `permission_attestation_digest = sha256(canonical(payload))`;
- exact immutable `RuntimePermissionAttestationRef(attestation_id, content_digest)`;
- exact resolution by both identity and digest;
- no latest/current/endpoint substitution;
- Slice 3.1 binding of the exact ref into the final `ExecutionSubject`;
- exclusion of the later permission attestation from `request_digest_v2`.

Material changes to the attestation payload therefore change the content digest.

The identity chain remains acyclic:

```text
RuntimeLaunchSubject
    ->
RuntimePlacementAttestation
    ->
RuntimeExecutionRequestV2 / request_digest_v2
    ->
RuntimeSessionBinding
    ->
RuntimePermissionAttestationRef
    ->
final Slice 3.1 ExecutionSubject
```

## 5. M001 preservation

PASS / REMAINS CLOSED.

Candidate 003 preserves:

- placement attestation separate from runtime permission/exposure evidence;
- Slice 2.1 ownership of runtime permission attestation;
- prompt-free exact session creation before permission attestation;
- final admission before `open_execution()`;
- expected placement-attester trust binding.

No M001 regression is present.

## 6. Frozen architecture preservation

PASS.

A direct Candidate 002 -> Candidate 003 comparison shows the substantive changes are limited to M002/M003 and corresponding exact-ref wording/tests/terminal metadata.

The following remain unchanged in substance:

- Relay-managed launch for strong-boundary execution;
- independent exact placement proof for external attach;
- WorkspaceBoundaryRef;
- RuntimeLaunchSubject;
- RuntimePlacementAttestation;
- RuntimeExecutionRequestV2;
- process-tree containment;
- nonce/replay protection;
- network/provider-transport separation;
- credential separation;
- runtime-counter versus OS/process-tree resource distinction;
- continuity and teardown;
- V1/V2 versioning;
- LocalCloneWorkspaceProvider security ceiling;
- Slice 2.1 / 2.4 / 3.1 ownership;
- Dogfood runtime/provider/model and attempt constraints.

No parallel planner, authority system, runtime framework, or workspace lifecycle is introduced.

## 7. Design completeness

PASS.

The accepted design now gives a coherent, implementation-ready contract direction for closing the previously accepted `RUNTIME_BOUNDARY_CONTRACT_GAP`.

This ACCEPT is design acceptance evidence only. It does not establish that the current host, a particular sandbox backend, or the pinned OpenCode beta can satisfy the contract. Those remain later implementation/qualification obligations.

## 8. Remaining gates

This review does not authorize:

- source/test implementation;
- provider/runtime/workspace implementation;
- Dogfood workspace provisioning;
- OpenCode runtime launch;
- runtime session creation;
- credential access;
- provider/model calls;
- prompt admission;
- Dogfood consumption;
- canonical promotion.

Fixture/source durable reachability and exact pinned-runtime qualification also remain unresolved downstream gates.

## 9. Final disposition

```text
Exact reviewed subject:
cb0ce54b94ac823a9327f557cc9968fffdd14e4d

Repository / registry:
PASS

Exact-head CI:
PASS

M001:
CLOSED

M002:
CLOSED

M003:
CLOSED

Frozen architecture:
PASS

Design:
ACCEPT

Implementation:
NOT AUTHORIZED

Dogfood 001:
AUTHORIZED / NOT ADMITTED / NOT CONSUMED
```

**Candidate 003 is independently accepted. The next Human gate is exact design acceptance before any implementation authority is issued.**
