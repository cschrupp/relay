# Slice 2.4 — Execution Workspace Authority — Design Revision 2 Amendment

**Document class:** Lockable Slice design amendment  
**Status:** DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Revision 1 subject:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Independent review:** `RLY-S24-DESIGN-EVAL-001 — REWORK`  
**Evaluation record:** `59a9f9dc6d9401245f3a927e85075a3b16d44bd0`  
**Rework authority:** `RLY-S24-DESIGN-REWORK-AUTH-001 — AUTHORIZED`  
**Rework-authority commit:** `38aa99e11f1bbc41196fce4f3e1053e8b9ee96ed`  
**Design branch:** `design/2.4-execution-workspace-authority`

---

# 1. Amendment scope

This amendment corrects only the six blocking findings from `RLY-S24-DESIGN-EVAL-001`:

```text
F001 exact-subject binding
F002 provider representability
F003 protected-verification permission semantics
F004 WorkspaceChangeManifest identity / exact type-state evidence
F005 no-WorkspacePolicyRef path
F006 local-clone control-strength / materialization claim
```

Revision 1 remains normative everywhere this amendment does not explicitly differ.

No implementation is authorized.

---

# 2. Supersession map

This amendment supersedes the following Revision-1 clauses only where described below.

| Revision-1 area | Revision-2 disposition |
|---|---|
| §16 ProtectedAssetWorkspaceBinding `requested_operation/effective_operation` ordering | Replaced by exact semantic operation + separate physical access/control |
| §25 WorkspaceProviderDescriptor capability shape | Expanded with finite exact semantic-mode/dimension capability declarations |
| §28 bare `WorkPacketConformance` input / "refers to same exact WorkPacketRef" | Replaced by exact subject-bound `WorkPacketConformanceFact` |
| §34–§50 evidence schemas where exact subject was prose-only | Amended to require exact `WorkspaceEvidenceSubject` or an object already containing exact instance ref |
| §42 `WorkspaceChangeManifest(..., manifest_digest)` | Replaced by separate immutable manifest + manifest ref/digest helper |
| §42 TYPE_CHANGED content-only representation | Replaced by exact before/after entry state |
| §50 bare status fields for policy/role/provider | Replaced by exact subject-bound fact wrappers |
| implicit no-policy behavior across §§10, 28, 53, 65 | Frozen as known UNSATISFIED / no plan |
| §58 local-clone `EXACT_SOURCE_BASELINE: BOUNDARY_ENFORCED` | Replaced by DETECTIVE exact-state evidence |
| §57 "avoid hardlinks where implementation permits" | Replaced by mandatory independent object storage / no alternates |

No other Revision-1 architecture is reopened.

---

# 3. F001 correction — exact subject-bound facts

Revision 1 correctly required exact-subject equality but did not make every positive assertion structurally bindable.

Revision 2 freezes explicit exact subject facts.

## 3.1 WorkPacketConformanceFact

Accepted Slice 2.3 `WorkPacketConformance` remains unchanged.

Slice 2.4 introduces only a subject-binding fact wrapper:

```python
WorkPacketConformanceFact(
    evaluated_work_packet_ref: WorkPacketRef,
    conformance: WorkPacketConformance,
)
```

Normative rules:

- `evaluated_work_packet_ref == work_packet_ref(packet)` is mandatory;
- `conformance.status == SATISFIED` is mandatory for WorkspacePlan resolution;
- wrong exact WorkPacketRef is known mismatch -> UNSATISFIED;
- exact ref with INDETERMINATE conformance -> INDETERMINATE;
- exact ref with UNSATISFIED conformance -> UNSATISFIED;
- Slice 2.4 does not reinterpret Slice 2.3 reasons;
- this wrapper does not create authority.

The fact is externally established from the accepted Slice 2.3 evaluator result and exact subject.

It does not modify `WorkPacketConformance`.

## 3.2 Exact policy/role/provider facts

Replace bare status fields with exact-subject facts:

```python
WorkspacePolicyFact(
    evaluated_ref: WorkspacePolicyRef,
    status: RequirementStatus,
)

RoleContractFact(
    evaluated_ref: RoleContractRef,
    status: RequirementStatus,
)

WorkspaceProviderDescriptorFact(
    evaluated_ref: WorkspaceProviderRef,
    status: RequirementStatus,
)
```

Exact ref mismatch is UNSATISFIED.

INDETERMINATE status on the exact subject remains INDETERMINATE.

## 3.3 WorkspaceEvidenceSubject

Freeze one reusable exact evidence subject:

```python
WorkspaceEvidenceSubject(
    plan_ref: WorkspacePlanRef,
    instance_ref: WorkspaceInstanceRef,
    provider_ref: WorkspaceProviderRef,
)
```

Validator invariants:

```text
instance_ref.plan_ref == plan_ref
instance_ref.provider_ref == provider_ref
```

Any mismatch is invalid construction.

## 3.4 Evidence objects requiring WorkspaceEvidenceSubject

The following evidence classes must carry exact `subject: WorkspaceEvidenceSubject`:

```text
WorkspacePropertyEvidence
WorkspaceEnvironmentProvenance
WorkspaceCredentialEvidence
WorkspaceResourceEvidence
WorkspaceControlContinuityEvidence
WorkspaceTeardownEvidence
```

Conceptual corrected forms:

```python
WorkspacePropertyEvidence(
    subject: WorkspaceEvidenceSubject,
    property_key,
    property,
    established_strength,
    status,
    evidence_payload_digest,
)

WorkspaceCredentialEvidence(
    subject: WorkspaceEvidenceSubject,
    credential_ref,
    exposure_mode,
    status,
    revoked_or_removed,
)

WorkspaceResourceEvidence(
    subject: WorkspaceEvidenceSubject,
    memory_limit_bytes,
    disk_limit_bytes,
    process_limit,
    cpu_seconds_limit,
    open_files_limit,
    status,
    evidence_payload_digest,
)

WorkspaceEnvironmentProvenance(
    subject: WorkspaceEvidenceSubject,
    boundary_class,
    backend_kind,
    platform_key,
    platform_version,
    image_digest,
    environment_payload_digest,
)

WorkspaceControlContinuityEvidence(
    subject: WorkspaceEvidenceSubject,
    start_evidence_digest,
    terminal_evidence_digest,
    status,
)

WorkspaceTeardownEvidence(
    subject: WorkspaceEvidenceSubject,
    disposition,
    credential_cleanup_status,
    workspace_absence_status,
    retained_until,
    evidence_payload_digest,
)
```

The `*_payload_digest` values identify provider-specific evidence payloads.

They are not substitutes for subject refs.

## 3.5 Evidence classes already structurally subject-bound

`WorkspaceInspection` and `WorkspaceChangeManifest` carry exact `WorkspaceInstanceRef`.

Because `WorkspaceInstanceRef` itself contains exact `WorkspacePlanRef` and `WorkspaceProviderRef`, they are structurally subject-bound.

No second subject field is required on those objects.

## 3.6 Corrected WorkspaceConformanceFacts

```python
WorkspaceConformanceFacts(
    evaluated_plan_ref: WorkspacePlanRef,
    evaluated_instance_ref: WorkspaceInstanceRef,
    evaluated_provider_ref: WorkspaceProviderRef,

    work_packet_conformance_fact: WorkPacketConformanceFact,
    workspace_policy_fact: WorkspacePolicyFact,
    role_contract_fact: RoleContractFact,
    provider_descriptor_fact: WorkspaceProviderDescriptorFact,

    initial_inspection: WorkspaceInspection,
    property_evidence: tuple[WorkspacePropertyEvidence, ...],
    protected_asset_evidence: tuple[ProtectedAssetEvidence, ...],
    credential_evidence: tuple[WorkspaceCredentialEvidence, ...],
    resource_evidence: tuple[WorkspaceResourceEvidence, ...],
    environment_provenance: WorkspaceEnvironmentProvenance,

    terminal_inspection: WorkspaceInspection | None,
    change_manifest: WorkspaceChangeManifest | None,
    continuity_evidence: WorkspaceControlContinuityEvidence | None,
    teardown_evidence: WorkspaceTeardownEvidence | None,
)
```

Every nested evidence item must resolve to the exact same plan/instance/provider subject.

A fact for another subject is UNSATISFIED, never reusable positive evidence.

## 3.7 F001 required tests

Freeze tests proving:

```text
SATISFIED packet-A fact + packet B
    -> UNSATISFIED / WORK_PACKET_REF_MISMATCH

policy fact for another WorkspacePolicyRef
    -> UNSATISFIED

role fact for another RoleContractRef
    -> UNSATISFIED

provider fact for another WorkspaceProviderRef
    -> UNSATISFIED

property evidence for instance A + facts for instance B
    -> UNSATISFIED

credential/resource/environment evidence for plan A + plan B
    -> UNSATISFIED
```

**F001: CLOSED BY DESIGN.**

---

# 4. F002 correction — exact provider representability

Revision 1's `WorkspaceProperty + maximum_strength` remains useful but is insufficient for generic semantic-mode preflight.

Revision 2 adds a finite schema-v1 capability profile.

## 4.1 Resource-limit dimensions

```text
WorkspaceResourceDimension:
  MEMORY_BYTES
  DISK_BYTES
  PROCESS_COUNT
  CPU_SECONDS
  OPEN_FILES
```

## 4.2 Path-control capabilities

```text
WorkspacePathControlCapability:
  CANONICAL_REPOSITORY_PATHS
  SYMLINK_ESCAPE_DETECTION
  SYMLINK_ESCAPE_PREVENTION
  HARDLINK_ESCAPE_DETECTION
  HARDLINK_ESCAPE_PREVENTION
  MOUNT_OR_REPARSE_ESCAPE_DETECTION
  MOUNT_OR_REPARSE_ESCAPE_PREVENTION
```

The provider descriptor declares exact supported values.

Presence means the provider implementation can represent that mechanism.

Actual establishment for an instance still requires evidence.

## 4.3 Corrected WorkspaceProviderDescriptor

```python
WorkspaceProviderDescriptor(
    schema_version=1,

    provider_id: RuntimeIdentifier,
    provider_version: RuntimeIdentifier,
    backend_kind: WorkspaceBackendKind,
    boundary_class: WorkspaceBoundaryClass,

    property_capabilities:
        tuple[WorkspaceProviderPropertyCapability, ...],

    supported_shell_modes:
        tuple[ShellMode, ...],

    supported_network_modes:
        tuple[NetworkMode, ...],

    supported_external_side_effect_modes:
        tuple[ExternalSideEffectMode, ...],

    supported_credential_exposure_modes:
        tuple[CredentialExposureMode, ...],

    supported_resource_dimensions:
        tuple[WorkspaceResourceDimension, ...],

    supported_repository_metadata_modes:
        tuple[RepositoryMetadataAccess, ...],

    path_control_capabilities:
        tuple[WorkspacePathControlCapability, ...],

    supports_provider_injected_file_contract: bool,
)
```

All enum tuples are:

- unique;
- enum-declaration ordered;
- canonical.

No arbitrary strings.

Provider descriptor identity includes every field above.

## 4.4 Provider capability meaning

The descriptor means:

```text
this provider implementation can represent / attempt this control
```

It does not mean:

```text
the exact workspace instance established this control
```

That distinction from Revision 1 remains frozen.

## 4.5 Exact preflight

Generic preflight must evaluate both:

1. required property + minimum strength; and
2. exact semantic mode/dimension representability.

Examples:

```text
policy.network_mode == ALLOWLIST
and ALLOWLIST not in descriptor.supported_network_modes
    -> UNSATISFIED

policy.shell_mode == DENY
and DENY not in descriptor.supported_shell_modes
    -> UNSATISFIED

credential grant exposure_mode == FILE
and FILE not supported
    -> UNSATISFIED

resource max_processes != None
and PROCESS_COUNT not supported
    -> UNSATISFIED

repository metadata mode LOCAL_MUTATION
not in supported_repository_metadata_modes
    -> UNSATISFIED
```

If the exact descriptor cannot be established or its identity is stale/unverifiable:

INDETERMINATE.

If a required semantic dimension is absent from the schema/provider declaration:

never SATISFIED.

## 4.6 Provider-injected file contract

Revision 2 freezes exact support semantics.

`supports_provider_injected_file_contract=True` only means the provider can enforce the contract shape.

Actual policy/plan must carry exact provider-injected-file declarations if used.

Add:

```python
ProviderInjectedFileRequirement(
    path: RepositoryPath,
    content_digest: ContentDigest,
)
```

to `WorkspacePolicyDefinition`:

```python
provider_injected_files:
    tuple[ProviderInjectedFileRequirement, ...]
```

Canonical order: path.

Duplicate/conflicting path is invalid.

If the tuple is non-empty and provider capability is false:

UNSATISFIED at preflight.

An undeclared injected file at initial inspection:

UNSATISFIED.

## 4.7 F002 required tests

Freeze:

```text
property capability says network control exists
but ALLOWLIST mode unsupported
    -> UNSATISFIED

credential control exists
but FILE exposure unsupported
    -> UNSATISFIED

resource control exists
but PROCESS_COUNT unsupported
    -> UNSATISFIED

metadata control exists
but LOCAL_MUTATION unsupported
    -> UNSATISFIED

required symlink-prevention property
without SYMLINK_ESCAPE_PREVENTION
    -> UNSATISFIED

provider-injected files required
but contract unsupported
    -> UNSATISFIED

descriptor unavailable/unverifiable
    -> INDETERMINATE

descriptor compatible
but instance enforcement evidence absent
    -> final conformance INDETERMINATE
```

**F002: CLOSED BY DESIGN.**

---

# 5. F003 correction — protected permissions are not ordinal

Revision 2 removes `effective_operation` and all "narrower than" comparison between `VerificationAssetPermission` enum values.

Accepted Slice 2.2 values remain orthogonal semantics:

```text
READ
CREATE
PROPOSE_MUTATION
MODIFY
APPROVE_MUTATION
EXECUTE
EVALUATE
```

No ordering exists.

## 5.1 Corrected ProtectedAssetWorkspaceBinding

```python
ProtectedAssetWorkspaceBinding(
    requirement_ref: ProtectedVerificationRequirementRef,
    artifact: Artifact,
    required_operation: VerificationAssetPermission,
    separate_authority_ref: AuthorityBasisRef | None,
    workspace_path: RepositoryPath,

    physical_access: FilesystemAccess,
    minimum_control_strength: ControlStrength,
)
```

Normative rules:

- `required_operation` must equal the exact WorkPacket protected-verification requirement operation;
- `required_operation in RoleContract.verification_asset_permissions` is mandatory;
- separate authority ref must exactly equal WorkPacket requirement where present;
- external authority fact must establish required mutation authority;
- `physical_access` is workspace capability, not semantic permission;
- physical READ_WRITE does not grant semantic MODIFY;
- physical READ_ONLY does not imply semantic READ/EXECUTE/EVALUATE authority;
- semantic permission and physical access are evaluated independently.

## 5.2 Physical-access compatibility

The plan may require physical access necessary to carry out an already-permitted semantic operation.

That relationship is explicit and operation-specific, not ordinal.

Schema-v1 minimum compatibility:

```text
READ:
  physical access must permit reading

EXECUTE:
  physical access must permit reading/executing under provider/tool policy

EVALUATE:
  physical access must permit the evidence access required by policy

MODIFY:
  physical access must be READ_WRITE

CREATE:
  destination scope must be READ_WRITE

PROPOSE_MUTATION:
  does not require mutation access merely to propose

APPROVE_MUTATION:
  approval semantics alone do not require mutation access
```

These rules describe physical prerequisites only.

They do not manufacture semantic authority.

## 5.3 No inferred permission

Freeze:

```text
filesystem READ_WRITE
    != semantic MODIFY

semantic MODIFY
    != APPROVE_MUTATION

semantic EVALUATE
    != MODIFY

semantic EXECUTE
    != MODIFY

evaluator ACCEPT
    != mutation authority
```

## 5.4 F003 required tests

```text
exact required operation absent from RoleContract
    -> UNSATISFIED

READ_WRITE filesystem + RoleContract lacks MODIFY
    -> semantic MODIFY remains prohibited

EVALUATE present, MODIFY absent
    -> cannot resolve MODIFY requirement

MODIFY requirement + physical READ_ONLY
    -> UNSATISFIED physical compatibility

MODIFY requirement + separate authority required but unavailable
    -> INDETERMINATE or UNSATISFIED according to exact authority fact

no ordinal enum comparison exists
    -> architecture/model test
```

**F003: CLOSED BY DESIGN.**

---

# 6. F004 correction — exact change-manifest identity

Revision 2 removes `manifest_digest` from `WorkspaceChangeManifest`.

Use established Relay pattern: immutable object + separately derived ref.

## 6.1 WorkspaceEntryKind

```text
WorkspaceEntryKind:
  REGULAR_FILE
  SYMLINK
```

Schema v1 result extraction does not treat directories as content-bearing change entries.

Directory creation/removal is represented by contained entries.

If a provider must represent another filesystem node kind:

unsupported / INDETERMINATE rather than silent coercion.

## 6.2 WorkspaceEntryState

```python
WorkspaceEntryState(
    kind: WorkspaceEntryKind,

    content_digest: ContentDigest | None,
    symlink_target_digest: ContentDigest | None,

    executable: bool | None,
)
```

Validation:

For REGULAR_FILE:

```text
content_digest required
symlink_target_digest == None
executable required
```

For SYMLINK:

```text
content_digest == None
symlink_target_digest required
executable == None
```

`symlink_target_digest` is SHA-256 of the exact raw symlink target bytes using the provider's canonical byte acquisition contract.

It does not resolve/follow the target.

## 6.3 Corrected WorkspaceChangeEntry

```python
WorkspaceChangeEntry(
    path: RepositoryPath,
    before: WorkspaceEntryState | None,
    after: WorkspaceEntryState | None,
)
```

Rules:

- before and after cannot both be None;
- before == after is invalid/no-op;
- before None -> addition;
- after None -> deletion;
- same kind with changed identity/mode -> modification;
- different kind -> type change;
- executable-bit-only change changes exact entry state even when content digest is unchanged.

`WorkspaceChangeKind` may be a pure derived helper.

It is not required in canonical identity.

## 6.4 Corrected WorkspaceChangeManifest

```python
WorkspaceChangeManifest(
    instance_ref: WorkspaceInstanceRef,
    source_commit: CommitRef,
    entries: tuple[WorkspaceChangeEntry, ...],
)
```

Canonical:

- entries unique by path;
- lexical path order;
- source_commit exactly matches instance source;
- no provider-injected entry may be silently dropped unless exact policy marks it as provider-injected and unchanged;
- any excluded provider artifact must remain accountable through initial/terminal inspection.

## 6.5 WorkspaceChangeManifestRef

```python
WorkspaceChangeManifestRef(
    instance_ref: WorkspaceInstanceRef,
    content_digest: ContentDigest,
)
```

Helpers:

```python
canonical_workspace_change_manifest_json(...)
digest_workspace_change_manifest(...)
workspace_change_manifest_ref(...)
workspace_change_manifest_ref_matches(...)
```

Digest domain is exact canonical `WorkspaceChangeManifest` bytes only.

No self-reference exists.

## 6.6 F004 required tests

```text
same bytes + executable false -> true
    -> different manifest digest

REGULAR_FILE -> SYMLINK
    -> exact before/after kinds preserved

symlink target A -> B
    -> different target digest / manifest identity

addition/deletion exact state
    -> deterministic

manifest ref independently recomputable
    -> PASS

entry reorder
    -> rejected as noncanonical

duplicate path
    -> rejected
```

**F004: CLOSED BY DESIGN.**

---

# 7. F005 correction — WorkspacePolicyRef is mandatory for executable workspace planning

Accepted Slice 2.3 intentionally permits:

```python
workspace_policy_ref: WorkspacePolicyRef | None
```

That means a WorkPacket may exist without a workspace policy because Slice 2.3 is not itself an execution/workspace gate.

Slice 2.4 freezes the execution boundary:

```text
Any WorkPacket used to resolve a WorkspacePlan
MUST contain an exact WorkspacePolicyRef.
```

Therefore:

```text
packet.workspace_policy_ref is None
    -> no WorkspacePlan
    -> WORKSPACE_POLICY_REQUIRED
    -> UNSATISFIED
```

This is a known missing mandatory workspace contract for this operation.

It is not an INDETERMINATE provider fact.

No implicit policy.

No default local policy.

No "safe fallback" policy.

No provider-generated policy.

## 7.1 Resolver order

Before resolving provider compatibility:

```text
1. exact WorkPacketRef
2. exact WorkPacketConformanceFact
3. packet.workspace_policy_ref present
4. exact WorkspacePolicyDefinition digest match
5. exact policy/profile binding
6. exact RoleContract binding
7. protected authority facts
8. exact provider descriptor
9. provider compatibility
10. produce WorkspacePlan
```

If step 3 fails, stop with UNSATISFIED.

## 7.2 F005 required tests

```text
workspace_policy_ref None
    -> UNSATISFIED / WORKSPACE_POLICY_REQUIRED

no implicit WorkspacePolicyDefinition created
    -> architecture test

exact ref + wrong policy digest
    -> UNSATISFIED

exact ref + unavailable exact definition
    -> INDETERMINATE
```

**F005: CLOSED BY DESIGN.**

---

# 8. F006 correction — local-clone strength and materialization

Revision 1's same-user boundary model remains correct.

The one inconsistent capability label is replaced.

## 8.1 Correct local-clone ceiling

For a plain same-user local disposable clone with no additional isolation mechanism:

```text
boundary_class:
SAME_USER_NO_SECURITY_BOUNDARY

EXACT_SOURCE_BASELINE:
DETECTIVE

CLEAN_INITIAL_STATE:
DETECTIVE

REPOSITORY_METADATA_ISOLATED:
DETECTIVE

DIRTY_STATE_INSPECTION:
DETECTIVE

CHANGESET_EXTRACTION:
DETECTIVE

RETENTION_CONTROL:
MEDIATED

TEARDOWN_CONTROL:
MEDIATED
```

The provider may advertise no stronger value merely because it successfully performed the initial clone.

If later implementation adds an exact independent mediator/boundary, that is separately represented in the exact provider descriptor/version.

## 8.2 Meaning of exact-source evidence

`EXACT_SOURCE_BASELINE: DETECTIVE` means:

```text
the provider positively observed and recorded
that the exact WorkspaceInstance materialized the exact source commit
at the evidence point
```

It does not mean:

```text
a same-user executor was physically prevented
from changing repository state later
```

Continuity is evaluated separately.

## 8.3 Exact local-clone object isolation

The local clone provider contract is strengthened.

For a provider that claims independent repository metadata/object storage:

- no Git alternates;
- no shared object-store dependency;
- no `--shared`;
- no local hardlinked object reuse;
- exact clone/materialization mechanism must force independent object storage;
- provider must verify `.git/objects/info/alternates` is absent/empty;
- source repository remains unchanged;
- exact commit must already be locally available; no remote fetch is allowed.

The implementation may use an equivalent to:

```text
local clone with hardlinks disabled
```

but the normative property is independent storage, not a specific command-line spelling.

"Where implementation permits" is removed.

If independent object storage cannot be established:

`REPOSITORY_METADATA_ISOLATED` is not SATISFIED.

## 8.4 No accidental boundary upgrade

Freeze:

```text
successful clone
    != BOUNDARY_ENFORCED

detached HEAD
    != BOUNDARY_ENFORCED

clean git status
    != BOUNDARY_ENFORCED

separate .git directory
    != general filesystem boundary
```

## 8.5 F006 required tests

```text
plain local clone descriptor advertises
EXACT_SOURCE_BASELINE > DETECTIVE
    -> invalid descriptor for schema-v1 local provider

plain local clone advertises generic filesystem/network boundary enforcement
    -> invalid or unsupported

clone uses alternates/shared objects
when metadata isolation required
    -> UNSATISFIED

source repository object store and refs remain unchanged
    -> verified

exact commit observed initially
    -> exact baseline evidence SATISFIED at DETECTIVE strength

later continuity unavailable
    -> CONTROL_CONTINUITY INDETERMINATE when required
```

**F006: CLOSED BY DESIGN.**

---

# 9. Corrected WorkspacePlan resolution contract

Revision 2 freezes the exact resolver inputs:

```python
resolve_workspace_plan(
    packet: WorkPacket,
    packet_ref: WorkPacketRef,
    packet_conformance_fact: WorkPacketConformanceFact,

    workspace_policy: WorkspacePolicyDefinition,
    role_contract: RoleContract,

    protected_authority_facts:
        tuple[ProtectedVerificationAuthorityFact, ...],

    provider_descriptor: WorkspaceProviderDescriptor,
) -> WorkspacePlanResolution
```

No authority is created.

## 9.1 Required exact checks

```text
work_packet_ref(packet) == packet_ref

packet_conformance_fact.evaluated_work_packet_ref == packet_ref

packet_conformance_fact.conformance.status == SATISFIED

packet.workspace_policy_ref is not None

workspace_policy_ref_matches(
    workspace_policy,
    packet.workspace_policy_ref
)

workspace_policy.policy_basis_ref
    == packet.policy_basis_ref

workspace_policy.governance_profile_ref
    == packet.governance_profile_ref

role_contract_ref(role_contract)
    == packet.role_contract_ref

every packet.required_workspace_property_key
    exists exactly in workspace_policy

every protected requirement operation
    is present exactly in RoleContract.verification_asset_permissions

every required separate authority
    is exact-subject bound and established

workspace provider descriptor ref
    exactly recomputes from descriptor

provider semantic capabilities
    can represent every policy mode/dimension

provider maximum property strengths
    meet every minimum policy requirement
```

## 9.2 Resolution result

Use:

```python
WorkspacePlanResolution(
    status: RequirementStatus,
    reasons: tuple[WorkspaceReason, ...],
    plan: WorkspacePlan | None,
)
```

Rules:

- plan exists only when status == SATISFIED;
- known mismatch/incompatibility -> UNSATISFIED / plan None;
- missing/unverifiable exact fact -> INDETERMINATE / plan None;
- SATISFIED means deterministic plan resolution only;
- SATISFIED != execution authority.

---

# 10. Corrected WorkspaceConformance evaluation

The exact subject is:

```text
WorkspacePlanRef
+
WorkspaceInstanceRef
+
WorkspaceProviderRef
```

The evaluator first validates all outer subject refs.

Then every nested evidence object must bind to that exact subject through:

- `WorkspaceEvidenceSubject`; or
- exact `WorkspaceInstanceRef` containing exact plan/provider refs.

Known subject mismatch:

UNSATISFIED.

Missing exact evidence:

INDETERMINATE.

Only after subject binding succeeds may property/evidence status contribute.

This ordering is mandatory.

---

# 11. Corrected preflight versus final evidence rule

The following remains normative:

```text
ProviderDescriptor
    -> can this provider represent/attempt the required control?

WorkspacePropertyEvidence
    -> was the required control actually established for this exact instance?
```

Therefore:

```text
descriptor compatibility SATISFIED
+
missing exact instance evidence
=
WorkspaceConformance INDETERMINATE
```

Never SATISFIED.

---

# 12. Corrected local-provider security statement

The first local provider is a **development/dogfood evidence provider**, not a generic sandbox.

It is suitable only when the exact WorkspacePolicyDefinition can be satisfied using the control strengths it honestly provides.

Typical local-clone strengths:

```text
exact baseline observation
clean initial state observation
independent Git metadata/object observation
dirty-state inspection
change extraction
provider-mediated retention/teardown
```

It is not sufficient when policy requires strong:

```text
filesystem mutation prevention
path-escape prevention
protected-asset write prevention
network denial/allowlist enforcement
external side-effect prevention
credential isolation
resource isolation
```

unless an additional exact provider mechanism establishes those controls.

No automatic downgrade exists.

---

# 13. Updated deterministic test obligations

Revision 1 tests remain required except where superseded.

Add or replace with the following.

## 13.1 Exact-subject tests

```text
packet-A conformance fact + packet B -> UNSATISFIED
policy-A fact + policy B -> UNSATISFIED
role-A fact + role B -> UNSATISFIED
provider-A fact + provider B -> UNSATISFIED
instance-A evidence + instance B -> UNSATISFIED
plan-A credential/resource/environment evidence + plan B -> UNSATISFIED
```

## 13.2 Provider semantic-mode tests

```text
network property present but ALLOWLIST mode absent -> UNSATISFIED
shell control present but DENY mode absent -> UNSATISFIED
credential property present but FILE mode absent -> UNSATISFIED
resource property present but PROCESS_COUNT absent -> UNSATISFIED
metadata property present but LOCAL_MUTATION absent -> UNSATISFIED
path prevention required but exact path capability absent -> UNSATISFIED
provider injected files required but capability false -> UNSATISFIED
```

## 13.3 Protected-permission tests

```text
no ordinal enum comparison
required operation must be exact RoleContract member
filesystem write does not grant semantic MODIFY
EVALUATE does not grant MODIFY
MODIFY does not grant APPROVE_MUTATION
physical access compatibility tested separately
```

## 13.4 Change-manifest tests

```text
manifest digest recomputable without self-reference
regular -> symlink exact transition
symlink target identity change
executable-bit-only change
addition
deletion
noncanonical order rejected
duplicate path rejected
```

## 13.5 Workspace-policy-required tests

```text
None ref -> UNSATISFIED
wrong digest -> UNSATISFIED
unavailable exact policy -> INDETERMINATE
no implicit/default policy path exists
```

## 13.6 Local-clone tests

```text
plain local provider cannot advertise BOUNDARY_ENFORCED baseline control
no alternates
no shared hardlinked object dependency
source repo unchanged
exact commit initial observation
clean initial observation
continuity remains separate
```

---

# 14. Updated A01–A18 coverage

With Revision 1 + this amendment:

```text
A01 PASS BY DESIGN
A02 PASS BY DESIGN
A03 PASS BY DESIGN
A04 PASS BY DESIGN
A05 PASS BY DESIGN
A06 PASS BY DESIGN
A07 PASS BY DESIGN
A08 PASS BY DESIGN
A09 PASS BY DESIGN
A10 PASS BY DESIGN
A11 PASS BY DESIGN
A12 PASS BY DESIGN
A13 PASS BY DESIGN
A14 PASS BY DESIGN
A15 PASS BY DESIGN
A16 PASS BY DESIGN
A17 PASS BY DESIGN
A18 PASS BY DESIGN
```

## A01

Exact immutable WorkspacePolicyDefinition identity/digest remains Revision 1 §10.

Revision 2 adds the explicit rule that a workspace plan cannot exist without an exact WorkspacePolicyRef.

## A02

WorkspacePlan exact identity remains Revision 1 §§27–30.

Revision 2 adds exact subject-bound WorkPacketConformanceFact.

## A03

Non-authority architecture unchanged.

## A04

Provider capability remains separate from enforcement evidence.

Revision 2 makes both descriptor semantics and evidence subject binding representable.

## A05

Exact source/root/clean state retained.

Local same-user claims now use correct DETECTIVE strength.

## A06

Filesystem/path-escape design unchanged.

Provider descriptor now represents exact path-control support.

## A07

Protected verification now uses exact orthogonal semantic permission plus separate physical control.

## A08

Shell design unchanged.

Provider descriptor now represents exact supported ShellMode values.

## A09

Network/external-effect design unchanged.

Provider descriptor now represents exact supported modes.

## A10

Credential secrecy unchanged.

Provider descriptor now represents exact exposure modes.

## A11

Resource/retention/teardown semantics unchanged.

Provider descriptor now represents exact resource dimensions.

## A12

Environment/security provenance now carries exact WorkspaceEvidenceSubject.

## A13

required_workspace_property_keys mapping retained.

WorkspacePolicyRef absence now explicitly fails closed.

## A14

WorkspaceChangeManifest now has independent digest identity and exact entry type/mode state.

## A15

RuntimeWorkspaceAttachment derivation remains unchanged.

## A16

Local backend remains supported but cannot overclaim boundary strength.

## A17

Exact-subject facts, exact provider-mode support, mandatory policy ref, and fail-closed precedence are now representable.

## A18

No DB/orchestration/runtime invocation/Phase 3 leakage introduced.

---

# 15. Implementation architecture impact

Revision 1's proposed package remains unchanged:

```text
src/relay_engine/execution_workspace/
    __init__.py
    models.py
    evaluation.py
    provider.py
    local_clone.py

tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
```

No accepted Slice 2.1, 2.2, or 2.3 model must change.

The subject-binding wrappers defined here live inside Slice 2.4.

No database migration is introduced.

---

# 16. Preserved non-authority boundary

Revision 2 preserves:

```text
WorkspacePolicyDefinition != authority
WorkspacePlan != authority
WorkspacePlanResolution SATISFIED != authority
WorkspacePreflight SATISFIED != authority
WorkspaceInstanceRef != authority
WorkspacePropertyEvidence != authority
WorkspaceConformance SATISFIED != authority
RuntimeWorkspaceAttachment != authority
successful teardown != Human acceptance
```

Phase 3 remains responsible for execution authority and orchestration.

---

# 17. Revision 2 disposition

```text
Slice 2.4:
OPEN

Revision 1:
REWORKED BY ADDITIVE REVISION 2 AMENDMENT

RLY-S24-DESIGN-EVAL-001:
REWORK — HISTORICAL / PRESERVED

F001:
CLOSED BY DESIGN

F002:
CLOSED BY DESIGN

F003:
CLOSED BY DESIGN

F004:
CLOSED BY DESIGN

F005:
CLOSED BY DESIGN

F006:
CLOSED BY DESIGN

Design acceptance:
PENDING INDEPENDENT REVIEW 002

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

# 18. Next gate

```text
STOP FOR SOL INDEPENDENT DESIGN REVIEW 002
```

The independent evaluator must review the combined design:

```text
Revision 1
+
Revision 2 Amendment
```

and return exactly:

```text
ACCEPT
REWORK
ESCALATE
```

No implementation authority is implied.

**Design amendment != design acceptance. Design acceptance != implementation authority.**
