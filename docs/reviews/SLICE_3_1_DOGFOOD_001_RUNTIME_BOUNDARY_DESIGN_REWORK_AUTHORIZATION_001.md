# Relay — Dogfood 001 Runtime Boundary Design M001 Rework Authority 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-27  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Workstream:** Dogfood 001 runtime-boundary contract design  
**Record:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-REWORK-AUTH-001 — AUTHORIZED`

## 1. Human decision

The Human authorizes one narrow design rework of Runtime Boundary Binding and Attestation Design Candidate 001 to close only finding M001 from the independent review.

Exact Candidate 001 subject:

`122a721c3b34827a24c5ff81cd5f059bcd649df2`

Candidate artifact digest:

`sha256:d120997f11e6dfba78b64da3eb1c6939997857c94a5da86ae611fd10d72494cb`

Independent evaluation:

`RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-001 — REWORK / NARROW`

Evaluation digest:

`sha256:efc3bb240b2bc3cbd7df2d356e5481b3c3c6e935e1b8fcfd4986eaff0f69fb55`

Dogfood 001 remains:

```text
AUTHORIZED
NOT ADMITTED
NOT CONSUMED
```

Implementation remains unauthorized.

## 2. Rework scope

The rework is limited to:

1. separating runtime placement attestation from actual effective runtime permission/tool/shell exposure evidence;
2. assigning actual effective runtime permission/exposure attestation to the accepted Slice 2.1 runtime-integration boundary;
3. moving effective-permission verification to after exact no-prompt runtime session creation and before prompt admission;
4. preserving digest acyclicity across launch subject, placement, request V2, runtime session, permission attestation, and final Slice 3.1 ExecutionSubject;
5. clarifying the expected placement-attester identity/trust basis so implementation cannot substitute an arbitrary attester.

No other design decision is reopened.

## 3. Required M001 correction

### C001 — Placement attestation remains placement evidence

`RuntimePlacementAttestation` must bind boundary/placement facts only, including the exact:

- launch-subject digest;
- WorkspaceBoundaryRef / boundary digest;
- runtime server identity;
- process-tree identity;
- endpoint identity;
- server/descendant boundary membership;
- enforcement evidence;
- boundary-provable credential-separation facts;
- attester identity;
- per-launch nonce or equivalent anti-replay identity;
- observation interval;
- completeness;
- authenticity/provenance.

Actual effective runtime tool/shell exposure must not be owned by the placement attester.

Expected permission-profile identity may remain in the launch subject and request.

### C002 — Slice 2.1 runtime permission attestation

The corrected design must define a distinct Relay-owned runtime-integration evidence concept equivalent to:

```text
RuntimePermissionAttestation
    execution_id
    request_digest_v2
    runtime_session_ref
    runtime_descriptor_ref
    launch_subject_digest
    placement_attestation_digest
    expected_permission_profile_ref
    observed_effective_profile_digest
    effective_tool_exposure
    effective_shell_exposure
    completeness
    observation_provenance
    observation_time_or_interval
```

Exact implementation names are not frozen by this authority.

Normative ownership is:

- produced/verified through Slice 2.1 runtime integration;
- consumed by Slice 3.1 final admission;
- never treated as Human authority;
- never inferred from provider capability or absence of runtime tool events.

### C003 — Correct pre-prompt ordering

The corrected design must use an ordering equivalent to:

```text
exact Human grant + reservation
    ↓
WorkPacket + conformance + exact WorkPacketRef
    ↓
WorkspacePlan + workspace instance + exact boundary
    ↓
RuntimeLaunchSubject
    ↓
managed runtime-server launch
    ↓
RuntimePlacementAttestation
    ↓
RuntimeExecutionRequestV2
    ↓
create exactly one runtime session
    NO PROMPT
    ↓
RuntimeSessionBinding(request_digest_v2)
    ↓
RuntimePermissionAttestation
    ↓
final Slice 3.1 ExecutionSubject
    ↓
repeat freshness / reservation / binding / admission checks
    ↓
open_execution
    ↓
admit exactly one prompt
```

Session creation is preparation inside the exact already-authorized attempt. It is not prompt admission and does not itself consume authority as successful agent execution.

If session creation or permission attestation fails, is absent, incomplete, stale, or mismatched:

```text
FAIL CLOSED
NO PROMPT
NO REPLACEMENT SESSION
NO NEW RUNTIME SERVER
NO RETRY UNDER A NEW IDENTITY
```

except where an already-accepted exact recovery rule for the same attempt/session applies.

### C004 — Preserve the acyclic identity graph

The design must preserve:

```text
RuntimeLaunchSubject
    ↓
RuntimePlacementAttestation
    ↓
RuntimeExecutionRequestV2 / request_digest_v2
    ↓
RuntimeSessionBinding
    ↓
RuntimePermissionAttestation
    ↓
final Slice 3.1 ExecutionSubject
```

`request_digest_v2` may bind:

- placement attestation;
- expected permission-profile identity.

It must not include the later session-scoped RuntimePermissionAttestation.

RuntimePermissionAttestation instead binds the already-final `request_digest_v2` and exact session.

The final Slice 3.1 ExecutionSubject binds all of them.

### C005 — OpenCode mapping

For strong-boundary OpenCode execution, the corrected design must state:

- Relay-managed launch establishes the exact OpenCode server inside the boundary;
- `create_session()` remains prompt-free;
- the exact session selects/binds the configured permission-bearing agent/profile;
- effective permission/tool/shell exposure evidence is obtained for that exact attested server/session;
- Slice 3.1 verifies that evidence before `open_execution()`;
- if the pinned Dogfood OpenCode version cannot expose trustworthy effective-permission evidence, admission remains blocked.

No requirement is weakened to accommodate OpenCode.

## 4. Placement-attester trust clarification

The corrected design must identify the expected placement-attester trust basis strongly enough to prevent arbitrary substitution.

The exact representation may be chosen during rework, but it must bind the expected attester identity or trust anchor into the exact provider/boundary contract or a content-digest-bound equivalent.

Normative rules:

```text
unexpected attester
    -> INDETERMINATE or UNSATISFIED / no admission

attester identity not exactly resolvable
    -> INDETERMINATE / no admission

runtime self-report alone
    -> not placement authority

endpoint owner alone
    -> not placement authority
```

This is a clarification of the accepted architecture, not authority to create a new trust infrastructure.

## 5. Decisions explicitly frozen

The rework must not reopen or materially change:

- Relay-managed launch as the default for strong-boundary executions;
- external attach requiring independent exact placement proof;
- `WorkspaceBoundaryRef`;
- `RuntimeLaunchSubject`;
- `RuntimePlacementAttestation` as the placement-proof concept;
- versioned `RuntimeExecutionRequestV2`;
- the two-stage launch/placement/request digest direction;
- process-tree containment;
- anti-replay nonce/challenge requirements;
- network/provider-transport separation;
- credential-separation requirements;
- runtime-counter versus OS/process-tree resource distinction;
- continuity and teardown semantics;
- V1 compatibility and V2 strong-boundary requirement;
- `LocalCloneWorkspaceProvider` security ceiling;
- Slice 2.1 / 2.4 / 3.1 ownership split;
- the accepted Dogfood runtime/provider/model constraints;
- Dogfood attempt identity, authority, reservation semantics, or consumption state.

## 6. Authorized artifact work

The worker may:

- revise Candidate 001 into a corrected Candidate 002, or create a tightly scoped additive correction artifact;
- update the registry for the corrected design artifact;
- run documentation/repository-contract validation;
- push the reviewable design candidate to the dedicated design branch.

The preferred result is a complete Candidate 002 whose text is internally coherent without requiring readers to synthesize Candidate 001 plus an informal correction.

## 7. Explicit non-authority

This authority does **not** permit:

- production source-code mutation;
- test implementation;
- runtime/provider/workspace implementation;
- package/dependency installation;
- host configuration changes;
- Dogfood fixture use;
- WorkPacket or WorkspacePlan materialization;
- workspace provisioning;
- OpenCode server launch;
- runtime session creation;
- credential access;
- provider/model calls;
- Dogfood prompt admission or consumption;
- implementation authorization;
- canonical promotion or merge.

## 8. Required terminal

The rework must terminate as:

### `RUNTIME_BOUNDARY_DESIGN_CANDIDATE_002_COMPLETE`

Use only when the exact M001 corrections are incorporated, Candidate 002 is internally coherent, registry/digest validation passes, and it is ready for independent re-review.

If M001 cannot be corrected without reopening frozen architecture:

### `ESCALATE_ARCHITECTURE_REOPEN_REQUIRED`

If required provenance is missing or contradictory:

### `FAIL_CLOSED`

## 9. Continuation rule

On `RUNTIME_BOUNDARY_DESIGN_CANDIDATE_002_COMPLETE`, proceed directly to independent design re-review.

Do not pause merely because the rework authority has reached its terminal.

Human design acceptance and implementation remain separate later gates.

**Disposition:** `AUTHORIZED`
