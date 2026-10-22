# Slice 2.4 — Independent Design Evaluation 001

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Evaluation ID:** `RLY-S24-DESIGN-EVAL-001`  
**Outcome:** `REWORK`  
**Design authority:** `RLY-S24-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact evaluated candidate:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Reviewer role:** Independent Slice 2.4 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

The design direction is sound and materially stronger than the original Slice 2.4 proposal. In particular, it correctly separates provider capability from actual enforcement evidence, refuses to treat a local same-user workspace as a strong generic security boundary, preserves Slice 2.1 / 2.2 / 2.3 ownership, and keeps workspace conformance non-authoritative.

However, six blocking design defects remain. Each is a case where the prose requires a deterministic security or exact-subject property that the proposed schema cannot yet represent or prove.

No implementation should begin from Revision 1.

---

# 1. Exact reviewed lineage

```text
Repository:
cschrupp/relay

Canonical Slice 2.3 closed baseline:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

Slice 2.4 opening:
RLY-S24-OPEN-001 — OPEN
4a2a97b706c976d5d57680aadb3cdb8faa4474e9

Slice 2.4 design authority:
RLY-S24-DESIGN-AUTH-001 — AUTHORIZED
7e96c34d97729daadc3606d6809d95f9e3145e51

Evaluated design:
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN.md

Exact candidate:
913d65841fecb4cf8ed172531b4d22e9c45f92cc
```

The design branch is exactly at the evaluated candidate.

Relative to canonical Slice 2.3 closed main, only the following three documentation files exist on the Slice 2.4 design lineage:

```text
docs/reviews/SLICE_2_4_OPENING.md
docs/reviews/SLICE_2_4_DESIGN_AUTHORIZATION.md
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN.md
```

No implementation/source/test change is part of the evaluated design candidate.

**Lineage / design-only boundary:** PASS.

---

# 2. Exact-head quality evidence

Exact-head GitHub Actions independently verified:

```text
Run:
39844220879

Head:
913d65841fecb4cf8ed172531b4d22e9c45f92cc

Branch:
design/2.4-execution-workspace-authority

Conclusion:
SUCCESS
```

Observed quality steps:

```text
Sync environment   SUCCESS
Ruff format        SUCCESS
Ruff lint          SUCCESS
Pyright            SUCCESS
Tests              SUCCESS
Build              SUCCESS
```

This is repository-health evidence only. It does not override design defects.

---

# 3. Finding F001 — exact-subject binding is required by prose but missing from proposed fact schemas

**Severity:** BLOCKING  
**Affected criteria:** A02, A04, A12, A17  
**Disposition:** REWORK REQUIRED

Revision 1 correctly requires exact subject binding.

For example, Section 28 states:

```text
WorkPacketConformance refers to same exact WorkPacketRef
```

and Section 39 states:

```text
evidence subject is exact WorkspaceInstanceRef + plan
```

Section 50 further says:

```text
Exact subject equality is required.
Facts for another plan/instance/provider cannot satisfy current conformance.
```

Those are correct requirements.

The proposed schemas, however, do not carry enough subject identity to prove them.

## F001-A — accepted WorkPacketConformance is not subject-bound

The accepted Slice 2.3 model is:

```python
class WorkPacketConformance(DomainModel):
    status: RequirementStatus
    reasons: tuple[WorkPacketReason, ...]
```

It carries no `WorkPacketRef`.

Revision 1 proposes the WorkspacePlan resolver consume:

```text
WorkPacket
WorkPacketRef
WorkPacketConformance
...
```

and verify:

```text
WorkPacketConformance refers to same exact WorkPacketRef
```

That verification is impossible using the accepted WorkPacketConformance object alone.

A SATISFIED result from packet A can be paired with packet B unless Slice 2.4 consumes or constructs an exact subject-bound fact.

## F001-B — several workspace evidence objects are also not subject-bound

Examples include the conceptual:

```python
WorkspacePropertyEvidence(
    property_key,
    property,
    established_strength,
    status,
    evidence_digest,
)

WorkspaceCredentialEvidence(
    credential_ref,
    exposure_mode,
    status,
    revoked_or_removed,
)

WorkspaceResourceEvidence(
    ...,
    status,
    evidence_digest,
)
```

The prose requires each item to refer to the exact current `WorkspaceInstanceRef` + `WorkspacePlanRef`, but those subject refs are absent.

The outer `WorkspaceConformanceFacts` carrying one evaluated plan/instance does not prove that arbitrary nested evidence was produced for those exact subjects.

An opaque `evidence_digest` is not sufficient unless the exact evidence schema and subject-binding digest semantics are themselves defined and verifiable.

## Required bounded correction

Revision 2 must make subject binding representable.

Acceptable patterns include either:

### Pattern A — explicit exact-subject facts

For example:

```python
WorkPacketConformanceFact(
    evaluated_work_packet_ref: WorkPacketRef,
    status: RequirementStatus,
    reasons: tuple[WorkPacketReason, ...],
)

WorkspacePropertyEvidence(
    evaluated_plan_ref: WorkspacePlanRef,
    evaluated_instance_ref: WorkspaceInstanceRef,
    ...
)
```

and equivalent exact subject refs on credential/resource/environment evidence.

### Pattern B — exact subject-bound envelope

A single immutable evidence envelope may bind:

```text
exact plan ref
exact instance ref
exact provider ref
exact evidence payload digest
exact evidence schema/version
```

with nested facts deterministically covered by that envelope.

But the design must define the digest domain and exact mapping.

### Pattern C — recompute accepted Slice 2.3 conformance

Instead of trusting a bare WorkPacketConformance result, Slice 2.4 may receive the exact accepted Slice 2.3 conformance inputs and call the accepted pure evaluator, then independently bind the exact WorkPacketRef.

That is allowed only if it does not duplicate or redefine Slice 2.3 semantics.

## Required tests

The future design must require negative tests proving:

```text
SATISFIED conformance for packet A
cannot satisfy packet B

property evidence for instance A
cannot satisfy instance B

credential/resource/environment evidence for plan A
cannot satisfy plan B
```

**F001:** OPEN / BLOCKING.

---

# 4. Finding F002 — provider descriptor is too weak for the preflight semantics Revision 1 requires

**Severity:** BLOCKING  
**Affected criteria:** A04, A08, A09, A10, A11, A16, A17  
**Disposition:** REWORK REQUIRED

Revision 1 defines:

```python
WorkspaceProviderDescriptor(
    ...
    property_capabilities:
        tuple[WorkspaceProviderPropertyCapability, ...],
)

WorkspaceProviderPropertyCapability(
    property: WorkspaceProperty,
    maximum_strength: ControlStrength,
)
```

But Section 62 requires generic preflight to verify:

```text
required boundary semantics representable
required tool/network/credential/resource modes representable
```

Those facts cannot be derived from `WorkspaceProperty + maximum_strength`.

Examples:

- a provider may support `NETWORK_REACHABILITY_CONTROL` at BOUNDARY_ENFORCED strength but support only DENY_ALL, not ALLOWLIST;
- a provider may support credential exposure via PROVIDER_NATIVE but not FILE;
- a provider may enforce memory limits but not process-count limits;
- a provider may expose tools but have no shell-disable mechanism;
- a provider may support local filesystem restriction but not the required path/symlink semantics;
- a provider may support repository metadata isolation but not the selected metadata-access mode.

Revision 1 also requires provider-injected files to be exact and declared in the provider/policy contract, yet neither the conceptual WorkspaceProviderDescriptor nor WorkspacePolicyDefinition shown in Revision 1 contains an exact provider-injected-file declaration.

Therefore the proposed pure generic preflight cannot deterministically establish all the compatibility claims assigned to it.

## Required bounded correction

Revision 2 must make provider representability exact.

This can be done with a bounded provider capability schema, for example by adding exact supported mode/dimension declarations such as:

```text
supported_shell_modes
supported_network_modes
supported_external_side_effect_modes
supported_credential_exposure_modes
supported_resource_limit_dimensions
supported_repository_metadata_modes
path-resolution/link-control capabilities
provider-injected-file contract support
```

or an equivalent closed schema of exact provider features.

Do not replace this with arbitrary string capability bags.

The representation must remain deterministic, canonical, finite for schema v1, and independently digest-bound.

If a semantic mode is not represented in the descriptor, generic preflight must not claim it is supported.

## Required tests

At minimum:

```text
provider supports NETWORK control but not ALLOWLIST
+ policy requires ALLOWLIST
    -> UNSATISFIED

provider supports credentials but not FILE exposure
+ policy requires FILE
    -> UNSATISFIED

provider supports memory limit only
+ policy requires max_processes
    -> UNSATISFIED

descriptor lacks exact support information
    -> INDETERMINATE, not SATISFIED
```

**F002:** OPEN / BLOCKING.

---

# 5. Finding F003 — VerificationAssetPermission is treated as an ordered permission level, but the accepted enum is orthogonal

**Severity:** BLOCKING  
**Affected criterion:** A07  
**Disposition:** REWORK REQUIRED

Revision 1 proposes:

```python
ProtectedAssetWorkspaceBinding(
    ...
    requested_operation: VerificationAssetPermission,
    effective_operation: VerificationAssetPermission,
    ...
)
```

and requires:

```text
effective_operation must never exceed requested_operation
effective_operation must never exceed RoleContract permission
policy may narrow to less access
```

But accepted Slice 2.2 `VerificationAssetPermission` is:

```text
READ
CREATE
PROPOSE_MUTATION
MODIFY
APPROVE_MUTATION
EXECUTE
EVALUATE
```

This enum is intentionally not a linear privilege lattice.

Revision 1 itself correctly says:

```text
READ does not imply MODIFY
EXECUTE does not imply MODIFY
EVALUATE does not imply MODIFY
MODIFY does not imply APPROVE_MUTATION
```

Therefore "effective_operation <= requested_operation" has no deterministic meaning.

Examples:

```text
Is READ narrower than EXECUTE?
Is EVALUATE narrower than MODIFY?
Does MODIFY imply READ?
Does CREATE imply MODIFY?
```

The accepted contract does not answer those questions, and Slice 2.4 must not invent that ordering.

## Required bounded correction

Do not order VerificationAssetPermission values.

A clean design is:

```python
ProtectedAssetWorkspaceBinding(
    requirement_ref,
    artifact,
    required_operation,        # exact operation from WorkPacket
    separate_authority_ref,
    workspace_path,
)
```

Then separately model **physical workspace access/control** using Slice 2.4 filesystem/protected-asset control values.

Alternatively, if Slice 2.4 needs a set of semantic operations, use an explicitly canonical subset of exact `VerificationAssetPermission` values and require:

```text
granted_operations ⊆ RoleContract.verification_asset_permissions
required WorkPacket operation ∈ granted_operations
```

but do not define an implicit order among enum members.

The future implementation must not infer semantic permission from filesystem writability.

## Required tests

At minimum prove there is no ordinal permission comparison and that:

```text
RoleContract lacks exact required operation
    -> UNSATISFIED

required operation present
    -> may proceed to physical-control evaluation

filesystem writable
    != semantic MODIFY permission

evaluator role / EVALUATE
    != MODIFY or APPROVE_MUTATION
```

**F003:** OPEN / BLOCKING.

---

# 6. Finding F004 — WorkspaceChangeManifest identity is self-referential and TYPE_CHANGED evidence is not exact enough

**Severity:** BLOCKING  
**Affected criterion:** A14  
**Disposition:** REWORK REQUIRED

Revision 1 proposes:

```python
WorkspaceChangeManifest(
    instance_ref,
    source_commit,
    entries,
    manifest_digest,
)
```

while also describing the manifest as canonical/content-bound.

If `manifest_digest` is part of the canonical serialized manifest, the digest is self-referential.

The design does not state that `manifest_digest` is excluded from the digest domain, nor does it introduce a separate ref model.

This is under-specified for deterministic identity.

## F004-B — TYPE_CHANGED is not fully described

The proposed entry is:

```python
WorkspaceChangeEntry(
    path,
    change_kind,
    before_digest,
    after_digest,
)
```

with:

```text
TYPE_CHANGED
```

But content digests alone do not identify a type/mode transition.

Examples:

- regular file -> symlink;
- symlink -> regular file;
- executable mode bit change where bytes are unchanged.

A `TYPE_CHANGED` marker says a transition occurred but does not identify the exact before/after type/mode state.

That is weaker than A14's exact/content-bound result-extraction requirement.

## Required bounded correction

Use either:

### Separate ref

```python
WorkspaceChangeManifest(
    instance_ref,
    source_commit,
    entries,
)

WorkspaceChangeManifestRef(
    instance_ref,
    content_digest,
)
```

with `digest_workspace_change_manifest(...)`;

or explicitly define the canonical digest domain as every normative field **except** `manifest_digest`.

The separate-ref pattern is preferred because it matches established Relay identity practice.

For entry identity, include sufficient exact state, e.g.:

```python
before_kind
after_kind
before_mode
after_mode
before_digest
after_digest
```

with fields applicable by kind.

Do not require a content digest where no ordinary file content exists; define exact symlink-target identity where needed.

## Required tests

At minimum:

```text
same bytes + executable-bit change
    -> distinct manifest identity

regular -> symlink
    -> exact before/after kinds preserved

manifest digest is independently recomputable
    -> no self-reference

entry reorder
    -> rejected or canonicalized only according to frozen rules
```

**F004:** OPEN / BLOCKING.

---

# 7. Finding F005 — the executable no-WorkspacePolicyRef case is undefined

**Severity:** BLOCKING  
**Affected criteria:** A01, A13, A17  
**Disposition:** REWORK REQUIRED

Accepted Slice 2.3 permits:

```python
workspace_policy_ref: WorkspacePolicyRef | None
```

Revision 1 WorkspacePlan requires:

```python
workspace_policy_ref: WorkspacePolicyRef
```

and the reason vocabulary includes:

```text
WORKSPACE_POLICY_REQUIRED
```

but Revision 1 never freezes the exact transition from:

```text
packet.workspace_policy_ref is None
```

to workspace planning/conformance.

This matters because Slice 2.4 must not silently create a default workspace policy; doing so would manufacture policy semantics outside the WorkPacket's exact references.

## Required bounded correction

Freeze one explicit rule.

Recommended:

```text
Any WorkPacket intended for Slice 2.4 workspace provisioning
MUST contain an exact WorkspacePolicyRef.

packet.workspace_policy_ref is None
    -> WorkspacePlan cannot be resolved
    -> WORKSPACE_POLICY_REQUIRED
    -> UNSATISFIED
```

This is a known absence of a required execution-workspace contract, not missing provider evidence.

If the design instead intends an explicit no-policy execution mode, it must define that mode as an exact externally selected policy state. It must not be an implicit default.

## Required tests

```text
workspace_policy_ref None
    -> plan resolution fails closed

no implicit default WorkspacePolicyDefinition
    -> proven

exact ref + wrong definition digest
    -> UNSATISFIED
```

**F005:** OPEN / BLOCKING.

---

# 8. Finding F006 — the local-clone capability ceiling overstates BOUNDARY_ENFORCED baseline control

**Severity:** BLOCKING  
**Affected criteria:** A05, A16  
**Disposition:** REWORK REQUIRED

Revision 1 defines BOUNDARY_ENFORCED as:

```text
the declared provider boundary prevents the prohibited operation
for processes operating inside that boundary
```

It also correctly declares:

```text
local same-user disposable clone
    != strong security boundary
```

and gives the local provider boundary class:

```text
SAME_USER_NO_SECURITY_BOUNDARY
```

However, Section 58 then states that a local same-user clone may support:

```text
EXACT_SOURCE_BASELINE:
BOUNDARY_ENFORCED relative to repository materialization operation
```

That is inconsistent with the design's own ControlStrength definition.

A local-clone provisioner can positively establish:

```text
HEAD == exact source commit at provision/inspection time
```

but a same-user process with unrestricted repository/filesystem capability can subsequently change HEAD, refs, index, working tree, or Git metadata.

That is strong **exact-state evidence**, not a general boundary preventing mutation by processes inside the declared workspace boundary.

Control continuity can later detect or establish more, but it does not make the initial same-user clone a BOUNDARY_ENFORCED security boundary.

## Required bounded correction

Do not use BOUNDARY_ENFORCED for the local same-user baseline claim unless an actual boundary prevents the relevant mutation.

Recommended schema-v1 ceiling:

```text
EXACT_SOURCE_BASELINE:
DETECTIVE
(or another explicitly non-boundary strength if Revision 2 introduces one)

CLEAN_INITIAL_STATE:
DETECTIVE

REPOSITORY_METADATA_ISOLATED:
MEDIATED only when exact local-provider mechanics justify the mediation claim

DIRTY_STATE_INSPECTION:
DETECTIVE

CHANGESET_EXTRACTION:
DETECTIVE

RETENTION_CONTROL:
MEDIATED

TEARDOWN_CONTROL:
MEDIATED
```

If Relay needs to represent "the provisioner deterministically selected the exact commit" separately from security enforcement strength, add a distinct exact provisioning property/evidence concept rather than overloading BOUNDARY_ENFORCED.

Also strengthen local clone materialization so independent Git object storage is deterministic. If source preservation is part of the provider claim, the future implementation contract should require the equivalent of local clone without shared hardlinked object mutation risk, rather than "avoid hardlinks where implementation permits."

## Required tests

The design must require tests showing a same-user local clone cannot advertise a BOUNDARY_ENFORCED property unless an actual enforcing boundary is present.

**F006:** OPEN / BLOCKING.

---

# 9. Positive design findings

The following parts of Revision 1 are accepted in direction and should be preserved through rework.

## P01 — ownership boundaries

PASS.

The design correctly preserves Slice 2.1, 2.2, 2.3, and Phase 3 ownership.

## P02 — non-authority architecture

PASS.

The design consistently preserves:

```text
WorkspacePlan != authority
WorkspaceConformance != authority
provider capability != authority
workspace creation != authority
```

## P03 — provider capability versus enforcement evidence

PASS IN PRINCIPLE.

This is one of the strongest parts of the design.

F002 concerns representability of provider capability detail, not the separation principle.

## P04 — local backend honesty

PASS IN PRINCIPLE.

The design correctly refuses to classify local same-user workspaces as generic strong isolation.

F006 is a narrow inconsistency in one capability label, not a rejection of the backend strategy.

## P05 — shell policy economy

PASS.

Avoiding a generic shell-command parser in schema v1 is appropriate.

## P06 — network versus external side effects

PASS.

The design correctly separates reachability from authority to mutate external systems.

## P07 — credential secrecy boundary

PASS.

CredentialRef-only modeling and prohibition on secret values/hashes in workspace models is correct.

## P08 — resource/runtime separation

PASS.

Workspace resource limits remain distinct from Slice 2.1 RuntimeExecutionLimits.

## P09 — no new lifecycle state

PASS.

Provider-local workspace states do not mutate Relay Slice lifecycle.

## P10 — local-clone first implementation

PASS IN PRINCIPLE.

A disposable local clone is a better first bounded backend than a same-repository worktree for exact baseline/change inspection.

## P11 — no DB migration requirement

PASS.

The initial contract can be implemented without persistence.

## P12 — Phase 3 boundary

PASS.

No real execution/orchestration authority is imported into Slice 2.4.

---

# 10. A01–A18 disposition

```text
A01 REWORK — F005
A02 REWORK — F001
A03 PASS
A04 REWORK — F001 / F002
A05 REWORK — F006
A06 PASS
A07 REWORK — F003
A08 REWORK — F002
A09 REWORK — F002
A10 REWORK — F002
A11 REWORK — F002
A12 REWORK — F001
A13 PASS subject to F005 exact no-policy rule
A14 REWORK — F004
A15 PASS
A16 REWORK — F002 / F006
A17 REWORK — F001 / F002 / F005
A18 PASS
```

### A01

REWORK.

Policy identity/digest design is strong, but the accepted WorkPacket allows `WorkspacePolicyRef | None` and the no-policy path is undefined.

### A02

REWORK.

WorkspacePlan binds WorkPacketRef structurally, but the claimed WorkPacketConformance exact-subject check cannot be implemented with the accepted bare WorkPacketConformance result.

### A03

PASS.

No workspace structure issues authority.

### A04

REWORK.

Capability/enforcement separation is conceptually correct, but evidence subject binding and provider representability need schema correction.

### A05

REWORK.

Exact baseline/root/clean-state concepts are present, but local BOUNDARY_ENFORCED baseline labeling contradicts the declared same-user boundary.

### A06

PASS.

Filesystem/path semantics are detailed and appropriately fail-closed.

### A07

REWORK.

Protected verification semantics need a non-ordinal permission model.

### A08

REWORK.

Shell design itself is good; provider descriptor needs exact shell-mode representability.

### A09

REWORK.

Network/external-effect semantics are good; generic preflight cannot currently prove provider mode support.

### A10

REWORK.

Credential secrecy is good; provider descriptor must encode exact supported exposure modes.

### A11

REWORK.

Resource/retention semantics are good; provider descriptor needs exact enforceable resource dimensions/modes.

### A12

REWORK.

Environment provenance is conceptually strong but evidence must be exact-subject bound.

### A13

PASS in direction.

Required property key mapping is correct. Revision 2 must integrate the explicit WorkspacePolicyRef-required rule.

### A14

REWORK.

Change-manifest identity and exact type/mode transitions are under-specified.

### A15

PASS.

RuntimeWorkspaceAttachment reuse is correct and no runtime invocation is included.

### A16

REWORK.

The design generally respects local-backend limits but one BOUNDARY_ENFORCED claim is inconsistent, and provider representability is under-specified.

### A17

REWORK.

Tri-state precedence is correct in principle; exact facts and no-policy/provider semantics must be representable before fail-closed evaluation is deterministic.

### A18

PASS.

No DB/orchestration/runtime invocation/Phase 3 scope leakage is present.

---

# 11. Required bounded Revision 2 scope

A corrective design amendment should be narrowly limited to F001–F006.

It should not redesign:

- the overall provider-neutral architecture;
- the three-level control-strength concept except where required by F006;
- filesystem policy;
- shell policy;
- network/external-effect separation;
- credential secrecy;
- resource values;
- retention model;
- Phase 3 boundary;
- initial package layout.

Revision 2 should specifically:

1. make every conformance/evidence subject exactly bindable to the correct WorkPacket/plan/instance/provider;
2. expand provider capability representation enough for deterministic semantic-mode preflight;
3. remove ordinal/narrower-than semantics from VerificationAssetPermission;
4. make WorkspaceChangeManifest digest identity independently recomputable and capture exact type/mode transitions;
5. freeze `WorkspacePolicyRef is None` behavior for executable workspace planning;
6. correct the local-clone capability ceiling and hardlink/materialization wording.

No implementation is required or authorized to correct these design findings.

---

# 12. Independent disposition

```text
RLY-S24-DESIGN-EVAL-001 — REWORK

Exact design candidate:
913d65841fecb4cf8ed172531b4d22e9c45f92cc

Exact-head CI:
39844220879 — SUCCESS

Design-only scope:
PASS

F001 exact-subject binding:
OPEN / BLOCKING

F002 provider representability:
OPEN / BLOCKING

F003 protected-permission ordering:
OPEN / BLOCKING

F004 change-manifest identity:
OPEN / BLOCKING

F005 no-WorkspacePolicyRef path:
OPEN / BLOCKING

F006 local-clone boundary strength:
OPEN / BLOCKING

A01–A18:
PARTIAL / REWORK REQUIRED

Implementation:
NOT AUTHORIZED

Workspace provisioning:
NOT AUTHORIZED

AgentRuntime invocation:
NOT AUTHORIZED

Production WorkPacket wiring:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

This evaluation is evidence only.

It does not authorize Revision 2 mutation.

A separate bounded Human design-rework authority is required before the design candidate may be amended.
