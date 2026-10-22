# Slice 2.4 — Execution Workspace Authority — Design Revision 3 Amendment

**Document class:** Lockable Slice design amendment  
**Status:** DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Revision 1:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Revision 2 amendment:** `3671e6ca7470f0b74c49ffa856e60474f22a5a92`  
**Independent review 002:** `RLY-S24-DESIGN-EVAL-002 — REWORK`  
**Evaluation-002 record:** `8165a241b8a146142ea2dcb199147946367fdb60`  
**Revision-3 authority:** `RLY-S24-DESIGN-REWORK-AUTH-002 — AUTHORIZED`  
**Authority commit:** `cfcc55eaae6ceb594345078df90ea3164176b50d`  
**Design branch:** `design/2.4-execution-workspace-authority`

---

# 1. Amendment scope

This amendment corrects only:

```text
F007 ProtectedAssetEvidence schema / deterministic derivation
F008 nested WorkspacePolicyDefinition schemas
```

Revision 1 + Revision 2 remain normative everywhere this amendment does not explicitly differ.

No implementation is authorized.

---

# 2. Supersession map

This amendment supersedes only:

| Prior clause | Revision-3 disposition |
|---|---|
| Revision 2 §3.6 `protected_asset_evidence: tuple[ProtectedAssetEvidence, ...]` | Removed; no standalone ProtectedAssetEvidence model exists |
| Revision 1 §37 `protected_asset_observations` prose-only field | Replaced by exact `ProtectedAssetObservation` schema |
| Revision 2 §5.1 `minimum_control_strength` inside ProtectedAssetWorkspaceBinding | Replaced by exact `control_property_key` reference to policy strength |
| Revision 1 §10 undefined `RepositoryMetadataPolicy` | Defined |
| Revision 1 §10 undefined `WorkspaceCredentialPolicy` | Defined |
| Revision 1 §10 undefined `WorkspaceProviderRequirements` | Removed |
| Revision 1 §22 incomplete `WorkspaceCredentialGrant` shape | Frozen completely |
| Revision 2 §4.6 addition of `provider_injected_files` | Retained and incorporated into corrected complete WorkspacePolicyDefinition |

No other clause is reopened.

---

# 3. F007 correction — remove ProtectedAssetEvidence

There is no `ProtectedAssetEvidence` model in schema v1.

Protected-asset conformance is deterministically derived from existing exact evidence.

The exact derivation basis is:

```text
ProtectedAssetWorkspaceBinding
+
ProtectedVerificationAuthorityFact
+
WorkspacePropertyRequirement(PROTECTED_ASSET_CONTROL)
+
WorkspacePropertyEvidence(PROTECTED_ASSET_CONTROL)
+
initial WorkspaceInspection / ProtectedAssetObservation
+
terminal WorkspaceInspection / ProtectedAssetObservation
+
WorkspaceChangeManifest when terminal changes are evaluated
```

This avoids duplicating authority state, mutation state, and change identity.

---

# 4. Corrected ProtectedAssetWorkspaceBinding

Revision 2's separation between semantic permission and physical access remains frozen.

The corrected binding is:

```python
ProtectedAssetWorkspaceBinding(
    requirement_ref: ProtectedVerificationRequirementRef,
    artifact: Artifact,
    required_operation: VerificationAssetPermission,
    separate_authority_ref: AuthorityBasisRef | None,
    workspace_path: RepositoryPath,

    physical_access: FilesystemAccess,
    control_property_key: StableRequirementKey,
)
```

`minimum_control_strength` is removed from the binding.

The required strength is owned by the exact policy requirement selected by `control_property_key`.

## 4.1 Binding invariants

The binding must satisfy:

```text
requirement_ref.artifact_id
    == artifact.id

requirement_ref.artifact_content_digest
    == artifact.content_digest

requirement_ref.required_operation
    == required_operation
```

and `requirement_ref` must exactly correspond to one WorkPacket protected-verification requirement.

The exact `separate_authority_ref` must equal the WorkPacket requirement's authority ref.

`control_property_key` must resolve to exactly one `WorkspacePropertyRequirement` in the selected WorkspacePolicyDefinition such that:

```text
requirement.property
    == PROTECTED_ASSET_CONTROL
```

Unknown key:
UNSATISFIED.

Key resolving to another WorkspaceProperty:
UNSATISFIED.

The physical access compatibility rules from Revision 2 remain unchanged.

Semantic permission remains exact and non-ordinal.

---

# 5. ProtectedAssetObservation

Freeze:

```python
ProtectedAssetObservation(
    requirement_ref: ProtectedVerificationRequirementRef,
    workspace_path: RepositoryPath,
    state: WorkspaceEntryState | None,
)
```

Meaning:

- `state is None` means the exact protected path is absent at this inspection point;
- non-None state uses the exact Revision-2 WorkspaceEntryState;
- no authority status is stored;
- no semantic permission is stored;
- no duplicate content digest is added outside WorkspaceEntryState.

## 5.1 Observation canonicality

Inside each WorkspaceInspection:

- observations are unique by exact `requirement_ref`;
- observations are ordered by the canonical key:

```text
(
  artifact_id,
  artifact_content_digest,
  required_operation enum declaration order,
  requirement_digest,
  workspace_path
)
```

- same requirement ref with conflicting path/state is invalid;
- duplicate requirement ref is invalid.

## 5.2 Observation-to-binding join

For every ProtectedAssetWorkspaceBinding, the relevant observation must match exactly:

```text
observation.requirement_ref == binding.requirement_ref
observation.workspace_path   == binding.workspace_path
```

A different requirement ref or path never substitutes.

Missing required observation:
INDETERMINATE.

Conflicting observation:
UNSATISFIED.

---

# 6. Corrected WorkspaceInspection protected observations

Revision 1's WorkspaceInspection is amended to use:

```python
WorkspaceInspection(
    instance_ref: WorkspaceInstanceRef,
    inspected_at,
    head_commit: CommitRef,
    tracked_changes,
    untracked_paths,
    provider_injected_paths,
    protected_asset_observations:
        tuple[ProtectedAssetObservation, ...],
    property_evidence:
        tuple[WorkspacePropertyEvidence, ...],
)
```

WorkspaceInspection remains structurally subject-bound through exact `instance_ref`.

The inspection's protected observations therefore inherit the exact plan/provider subject from the instance plus their exact protected requirement/path subjects.

---

# 7. Exact protected-asset authority join

For each binding, use the accepted Slice 2.3 fact:

```python
ProtectedVerificationAuthorityFact(
    evaluated_requirement_ref,
    evaluated_authority_ref,
    status,
)
```

Exact join requires:

```text
fact.evaluated_requirement_ref
    == binding.requirement_ref

fact.evaluated_authority_ref
    == binding.separate_authority_ref
```

No authority is copied into a new evidence object.

## 7.1 Authority status semantics

When `binding.separate_authority_ref is None`:

- the exact fact for requirement + None must establish the applicable no-separate-authority condition according to accepted Slice 2.3 semantics;
- Slice 2.4 does not invent another authority predicate.

When an authority ref is required:

```text
exact fact SATISFIED
    -> authority prerequisite satisfied for workspace planning/evaluation

exact fact UNSATISFIED
    -> UNSATISFIED

exact fact INDETERMINATE or missing
    -> INDETERMINATE
```

A fact for another requirement or another authority ref:
UNSATISFIED.

---

# 8. Exact protected physical-control join

For each binding:

1. resolve `binding.control_property_key`;
2. require the corresponding WorkspacePropertyRequirement property to be `PROTECTED_ASSET_CONTROL`;
3. obtain exact WorkspacePropertyEvidence with:
   - same exact WorkspaceEvidenceSubject;
   - same exact property key;
   - property == PROTECTED_ASSET_CONTROL;
4. require:
   - evidence.status == SATISFIED;
   - established_strength >= policy minimum strength.

Known lower strength:
UNSATISFIED.

Missing/unverifiable evidence:
INDETERMINATE.

Provider descriptor capability alone never satisfies this check.

---

# 9. Pre-execution protected-asset conformance

For each protected binding before execution:

Required exact inputs:

```text
binding
authority fact
initial protected observation
PROTECTED_ASSET_CONTROL property requirement
exact property evidence
```

Checks:

- exact subject joins;
- exact semantic operation permitted by RoleContract;
- exact separate authority condition;
- physical access compatible with exact semantic operation;
- exact policy control property exists;
- actual established control strength meets policy minimum;
- initial observation matches exact requirement/path;
- initial state is verifiable where the protected requirement requires existing material.

Known mismatch/violation:
UNSATISFIED.

Missing/unverifiable required fact:
INDETERMINATE.

All checks satisfied:
protected-asset pre-execution contribution SATISFIED.

This result is not execution authority.

---

# 10. Terminal protected-asset mutation derivation

For each binding with both initial and terminal observations:

```text
mutation_observed :=
    initial_observation.state
    != terminal_observation.state
```

No independent mutation boolean is stored.

## 10.1 Manifest consistency

When terminal WorkspaceChangeManifest is required/available:

If `mutation_observed == True`:

- exactly one manifest entry for `binding.workspace_path` must exist;
- manifest entry before == initial observation state;
- manifest entry after == terminal observation state.

If `mutation_observed == False`:

- no manifest entry for that protected path may claim a change.

Contradiction:
UNSATISFIED.

Required manifest unavailable:
INDETERMINATE.

## 10.2 Non-mutating semantic operations

For:

```text
READ
EXECUTE
EVALUATE
PROPOSE_MUTATION
APPROVE_MUTATION
```

a mutation observed through this protected binding is:

`PROTECTED_ASSET_MUTATED -> UNSATISFIED`

These semantic operations do not themselves authorize physical mutation.

## 10.3 Mutating semantic operations

For:

```text
CREATE
MODIFY
```

mutation is not automatically a conformance failure.

It is eligible only when:

- exact RoleContract semantic permission is present;
- exact WorkPacket required operation matches;
- any required separate authority fact is SATISFIED;
- physical access is compatible;
- required PROTECTED_ASSET_CONTROL evidence is SATISFIED;
- path/scope evaluation permits the change.

Mutation eligibility is not engineering acceptance.

No mutation is required merely because CREATE or MODIFY is permitted.

---

# 11. Protected-asset aggregation ordering

For each binding evaluate in this order:

```text
1. exact binding identity
2. exact RoleContract required operation
3. exact separate authority fact
4. exact control_property_key
5. exact WorkspacePropertyEvidence subject/key/property
6. exact initial observation
7. terminal observation if terminal evaluation
8. manifest consistency if terminal change evaluation
9. mutation compatibility with semantic operation
10. broader path/scope conformance
```

Precedence:

```text
known exact mismatch / forbidden mutation / insufficient control
    -> UNSATISFIED

else missing / unavailable / unverifiable required evidence
    -> INDETERMINATE

else
    -> SATISFIED
```

A later positive fact cannot repair an earlier exact-subject mismatch.

---

# 12. Corrected WorkspaceConformanceFacts

Revision 2 §3.6 is amended to remove the undefined field:

```text
protected_asset_evidence:
    tuple[ProtectedAssetEvidence, ...]
```

Corrected conceptual shape:

```python
WorkspaceConformanceFacts(
    evaluated_plan_ref: WorkspacePlanRef,
    evaluated_instance_ref: WorkspaceInstanceRef,
    evaluated_provider_ref: WorkspaceProviderRef,

    work_packet_conformance_fact: WorkPacketConformanceFact,
    workspace_policy_fact: WorkspacePolicyFact,
    role_contract_fact: RoleContractFact,
    provider_descriptor_fact: WorkspaceProviderDescriptorFact,

    protected_authority_facts:
        tuple[ProtectedVerificationAuthorityFact, ...],

    initial_inspection: WorkspaceInspection,
    property_evidence: tuple[WorkspacePropertyEvidence, ...],
    credential_evidence: tuple[WorkspaceCredentialEvidence, ...],
    resource_evidence: tuple[WorkspaceResourceEvidence, ...],
    environment_provenance: WorkspaceEnvironmentProvenance,

    terminal_inspection: WorkspaceInspection | None,
    change_manifest: WorkspaceChangeManifest | None,
    continuity_evidence: WorkspaceControlContinuityEvidence | None,
    teardown_evidence: WorkspaceTeardownEvidence | None,
)
```

The exact ProtectedAssetWorkspaceBindings come from the exact WorkspacePlan being evaluated.

There is no duplicate protected-asset evidence collection.

**F007 is closed by deterministic derivation.**

---

# 13. F007 deterministic tests

Freeze at minimum:

```text
observation requirement A used for binding B
    -> UNSATISFIED

observation correct requirement but wrong path
    -> UNSATISFIED

required initial observation missing
    -> INDETERMINATE

authority fact for another requirement
    -> UNSATISFIED

authority fact for another authority ref
    -> UNSATISFIED

PROTECTED_ASSET_CONTROL evidence for another instance
    -> UNSATISFIED

PROTECTED_ASSET_CONTROL established below required strength
    -> UNSATISFIED

READ protected asset initial != terminal
    -> UNSATISFIED

EVALUATE protected asset initial != terminal
    -> UNSATISFIED

MODIFY protected asset changed with required authority/control
    -> eligible for SATISFIED protected-asset conformance

MODIFY protected asset changed but required authority missing
    -> INDETERMINATE or UNSATISFIED according to exact authority fact

initial/terminal state changed but manifest disagrees
    -> UNSATISFIED

required terminal observation missing
    -> INDETERMINATE
```

---

# 14. F008 correction — define RepositoryMetadataPolicy

Freeze:

```python
RepositoryMetadataPolicy(
    access: RepositoryMetadataAccess,
)
```

No additional implicit fields.

The exact `access` value participates in WorkspacePolicyDefinition canonical identity.

Provider compatibility must require:

```text
repository_metadata_policy.access
    in provider_descriptor.supported_repository_metadata_modes
```

Known unsupported:
UNSATISFIED.

Unknown descriptor:
INDETERMINATE.

---

# 15. Corrected WorkspaceCredentialGrant

Freeze the complete schema:

```python
WorkspaceCredentialGrant(
    credential_ref: CredentialRef,
    exposure_mode: CredentialExposureMode,
    exposure_key: BoundedText | None,
)
```

`exposure_key` is a secret-free exact locator/name interpreted under the exact exposure mode and provider contract.

It is never secret material.

## 15.1 Exposure-key invariants

```text
exposure_mode == NONE
    -> exposure_key must be None

exposure_mode in {ENVIRONMENT, FILE, PROVIDER_NATIVE}
    -> exposure_key must be non-None and nonblank
```

Examples of meaning:

- ENVIRONMENT: exact environment-variable name;
- FILE: exact provider-managed workspace credential-file locator;
- PROVIDER_NATIVE: exact provider-native injection slot/key.

The value is an identity/locator only.

No secret bytes, secret hash, or secret value may appear.

---

# 16. WorkspaceCredentialPolicy

Freeze:

```python
WorkspaceCredentialPolicy(
    grants: tuple[WorkspaceCredentialGrant, ...],
)
```

Default semantics:

```text
credential not present in grants
    -> not exposed to workspace
```

## 16.1 Canonical ordering

Canonical key:

```text
(
  credential_ref.credential_id,
  exposure_mode enum declaration order,
  exposure_key-or-empty
)
```

The tuple must be in canonical order.

## 16.2 Uniqueness/conflict rule

At most one grant may exist for each `credential_id`.

Therefore:

```text
same credential_id repeated
    -> invalid
```

even if exposure modes/keys differ.

This rejects ambiguous multi-exposure policy in schema v1.

A future multiple-exposure feature requires a later schema revision.

## 16.3 WorkPacket subset rule

During WorkspacePlan resolution:

For every policy grant:

```text
grant.credential_ref
    must exactly equal one CredentialRef
    in packet.credential_refs
```

Grant not declared in exact WorkPacket:
UNSATISFIED / CREDENTIAL_NOT_DECLARED.

A packet CredentialRef absent from policy grants:
no workspace exposure.

## 16.4 Plan mapping

```text
WorkspacePlan.workspace_credential_grants
    == WorkspacePolicyDefinition.credential_policy.grants
```

exactly, after the WorkPacket subset check.

No provider, runtime, or resolver adds another workspace credential grant.

Provider preflight then checks exact `exposure_mode` support.

Actual exposure still requires exact instance credential evidence.

---

# 17. Remove WorkspaceProviderRequirements

`WorkspaceProviderRequirements` is removed from schema v1.

Reason:

Revision 2 already expresses provider requirements through:

```text
WorkspacePropertyRequirement
+
minimum ControlStrength
+
exact policy modes
+
exact resource dimensions
+
exact repository metadata mode
+
path-control semantics
+
provider-injected-file contract
+
WorkspaceProviderDescriptor compatibility
```

A separate `WorkspaceProviderRequirements` container would create a second overlapping requirement channel and could conflict with the policy fields above.

No unique normative requirement remains for that type.

Therefore it is deleted rather than defined.

---

# 18. Corrected complete WorkspacePolicyDefinition

Revision 1 §10 + Revision 2 §4.6 are superseded by this complete schema:

```python
WorkspacePolicyDefinition(
    schema_version=1,

    policy_key: StableRequirementKey,
    policy_basis_ref: PolicyBasisRef,
    governance_profile_ref: GovernanceProfileRef | None,

    property_requirements:
        tuple[WorkspacePropertyRequirement, ...],

    filesystem_policy: FilesystemPolicy,
    repository_metadata_policy: RepositoryMetadataPolicy,
    tool_policy: ToolPolicy,
    shell_policy: ShellPolicy,
    network_policy: NetworkPolicy,
    external_side_effect_policy: ExternalSideEffectPolicy,
    credential_policy: WorkspaceCredentialPolicy,
    resource_limits: WorkspaceResourceLimits,
    retention_policy: WorkspaceRetentionPolicy,

    provider_injected_files:
        tuple[ProviderInjectedFileRequirement, ...],
)
```

There is no `provider_requirements` field.

No unspecified extension bag exists.

Unknown fields are forbidden.

---

# 19. WorkspacePolicyDefinition canonical identity

Canonical digest remains:

```text
SHA-256(
  UTF-8 canonical JSON of the complete
  WorkspacePolicyDefinition
)
```

with:

```text
sort_keys=True
separators=(",", ":")
ensure_ascii=False
allow_nan=False
no floating-point normative values
```

The digest covers every nested policy field defined in §18, including:

- RepositoryMetadataPolicy.access;
- every WorkspaceCredentialGrant field;
- provider-injected file requirements;
- all Revision-1/Revision-2 policy fields.

No nested opaque policy object exists.

## 19.1 Nested collection canonicality

At minimum:

```text
property_requirements:
    by requirement key

filesystem prefixes:
    Revision-1 canonical path ordering

tool rules:
    by exact tool ref identity

network endpoints:
    scheme / host / port

external effect refs:
    effect key / definition digest

credential grants:
    credential_id / exposure-mode enum order / exposure-key-or-empty

provider_injected_files:
    path
```

Same stable canonical identity with conflicting normative content:
reject.

No arbitrary tie ordering.

---

# 20. Fixed canonical vectors

Implementation scope must include literal fixed canonical JSON/SHA-256 vectors for at least:

```text
minimal WorkspacePolicyDefinition:
- no governance profile
- no credentials
- no injected files
- no optional limits

full WorkspacePolicyDefinition:
- governance profile
- non-empty property requirements
- repository metadata mode
- tool/shell/network/effect policy
- credential grants
- resource limits
- retention policy
- provider-injected files
```

Mutation of any nested normative field must change the policy digest.

Reordering a noncanonical collection must be rejected before digest identity is accepted.

---

# 21. F008 deterministic tests

Freeze at minimum:

```text
RepositoryMetadataPolicy.access changes
    -> policy digest changes

credential grant not declared in WorkPacket
    -> UNSATISFIED plan resolution

packet credential absent from policy grants
    -> no workspace exposure

same credential_id repeated
    -> invalid

credential grants reordered
    -> invalid noncanonical input

NONE + non-None exposure_key
    -> invalid

ENVIRONMENT/FILE/PROVIDER_NATIVE + None exposure_key
    -> invalid

secret bytes/value field
    -> impossible by schema

credential grant mutation
    -> policy digest changes

provider_injected_files mutation
    -> policy digest changes

unknown WorkspacePolicyDefinition field
    -> rejected

WorkspaceProviderRequirements
    -> absent from schema

minimal fixed canonical vector
    -> exact expected SHA-256

full fixed canonical vector
    -> exact expected SHA-256
```

**F008 is closed by exact schema.**

---

# 22. Corrected WorkspacePlan policy mapping

Revision 1 WorkspacePlan remains structurally unchanged except its resolved nested values now derive from the corrected complete policy.

At plan resolution:

```text
plan.filesystem_policy
    == workspace_policy.filesystem_policy

plan.repository_metadata_policy
    == workspace_policy.repository_metadata_policy

plan.tool_policy
    == workspace_policy.tool_policy

plan.shell_policy
    == workspace_policy.shell_policy

plan.network_policy
    == workspace_policy.network_policy

plan.external_side_effect_policy
    == workspace_policy.external_side_effect_policy

plan.workspace_credential_grants
    == workspace_policy.credential_policy.grants

plan.resource_limits
    == workspace_policy.resource_limits

plan.retention_policy
    == workspace_policy.retention_policy
```

Provider-injected file requirements remain exact plan/provisioning requirements even if not redundantly copied into WorkspacePlan; the exact WorkspacePolicyRef is inside the plan identity and provider provisioning consumes the exact policy definition during authorized orchestration.

If implementation requires them embedded in WorkspacePlan for pure provider use, that exact duplication must be frozen in implementation scope before coding; it may not be invented silently.

---

# 23. F007/F008 reason handling

No new authority states are introduced.

Existing reason vocabulary is sufficient except implementation may need exact deterministic reasons for observation/policy structural mismatch.

At minimum existing:

```text
PROTECTED_ASSET_PERMISSION_REQUIRED
PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED
PROTECTED_ASSET_MUTATED
REQUIRED_WORKSPACE_PROPERTY_UNKNOWN
REQUIRED_WORKSPACE_PROPERTY_UNSATISFIED
CREDENTIAL_NOT_DECLARED
CREDENTIAL_EXPOSURE_UNSUPPORTED
UNEXPECTED_CREDENTIAL_EXPOSURE
WORKSPACE_POLICY_REF_MISMATCH
WORKSPACE_POLICY_CONFLICT
```

must be used where applicable.

If a new reason enum is required solely to distinguish:

```text
PROTECTED_ASSET_OBSERVATION_MISMATCH
PROTECTED_ASSET_OBSERVATION_MISSING
```

that is within Slice 2.4 implementation scope provided it does not alter aggregation precedence.

---

# 24. Updated A01–A18 coverage

Combined Revision 1 + Revision 2 + Revision 3:

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

WorkspacePolicyDefinition is now complete: no undefined nested normative policy types remain.

## A02

Unchanged from accepted Revision-2 correction.

## A03

Non-authority boundary unchanged.

## A04

Protected conformance now derives from exact subject-bound existing evidence; no opaque protected evidence placeholder remains.

## A05

Unchanged from Revision 2.

## A06

Unchanged.

## A07

Exact semantic protected permission + physical access + exact authority fact + exact observation/control derivation are now complete.

## A08

Tool/shell policy unchanged; complete policy identity now includes the exact nested policy.

## A09

Network/external-effect policy unchanged.

## A10

WorkspaceCredentialPolicy and exact WorkPacket-to-plan mapping are now frozen.

## A11

Repository metadata/resource/retention policy identity is complete.

## A12

Exact protected observations are structurally attached to exact WorkspaceInspection instance.

## A13

All required workspace policy keys continue to resolve against exact complete policy definition.

## A14

Exact WorkspaceEntryState from Revision 2 is reused for protected observations and change-manifest consistency.

## A15

RuntimeWorkspaceAttachment boundary unchanged.

## A16

Local-clone ceiling unchanged from Revision 2.

## A17

No undefined protected evidence or nested policy container remains in the corrected areas.

## A18

No DB/orchestration/runtime/Phase3 leakage introduced.

---

# 25. Implementation architecture impact

The proposed package/file architecture remains unchanged:

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

No accepted Slice 2.1 / 2.2 / 2.3 model change is required.

No DB migration is introduced.

---

# 26. Preserved authority boundary

```text
WorkspacePolicyDefinition != authority
WorkspaceCredentialPolicy != authority
ProtectedAssetObservation != authority
ProtectedVerificationAuthorityFact != authority creation
WorkspacePlan != authority
WorkspacePlanResolution SATISFIED != authority
WorkspaceConformance SATISFIED != authority
RuntimeWorkspaceAttachment != authority
successful local clone != authority
successful teardown != Human acceptance
```

Phase 3 remains responsible for current execution authority and orchestration.

---

# 27. Revision 3 disposition

```text
Slice 2.4:
OPEN

Revision 1:
PRESERVED

Revision 2:
PRESERVED

RLY-S24-DESIGN-EVAL-001:
REWORK — HISTORICAL

RLY-S24-DESIGN-EVAL-002:
REWORK — HISTORICAL

F001–F006:
CLOSED BY REVISION 2

F007:
CLOSED BY REVISION 3

F008:
CLOSED BY REVISION 3

Design acceptance:
PENDING INDEPENDENT REVIEW 003

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

# 28. Next gate

```text
STOP FOR SOL INDEPENDENT DESIGN REVIEW 003
```

The independent evaluator must review the combined normative design:

```text
Revision 1
+
Revision 2 Amendment
+
Revision 3 Amendment
```

and return exactly:

```text
ACCEPT
REWORK
ESCALATE
```

No implementation authority is implied.

**Design amendment != design acceptance. Design acceptance != implementation authority.**
