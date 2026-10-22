# Slice 2.4 — Execution Workspace Authority — Design Revision 4 Amendment

**Document class:** Lockable Slice design amendment  
**Status:** DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Revision 1:** `913d65841fecb4cf8ed172531b4d22e9c45f92cc`  
**Revision 2:** `3671e6ca7470f0b74c49ffa856e60474f22a5a92`  
**Revision 3:** `5370888cf9a8704d00f6b3beafa25f0becec86f8`  
**Independent review 003:** `RLY-S24-DESIGN-EVAL-003 — REWORK`  
**Evaluation-003 record:** `4e3b065ad0a40027cd551a3e99faf861f27da14c`  
**Revision-4 authority:** `RLY-S24-DESIGN-REWORK-AUTH-003 — AUTHORIZED`  
**Authority commit:** `58a0b9dd012c6ddbc51c67da93e6f59360337d56`  
**Design branch:** `design/2.4-execution-workspace-authority`

---

# 1. Amendment scope

This amendment corrects only:

```text
F009 protected-authority fact consumption
F010 provider-injected-file plan/provision transport
F011 remaining digest-bound policy-container schemas
```

Revision 1 + Revision 2 + Revision 3 remain normative everywhere this amendment does not explicitly differ.

No implementation is authorized.

---

# 2. Supersession map

This amendment supersedes only:

| Prior clause | Revision-4 disposition |
|---|---|
| Revision 3 §7.1 requiring an exact authority fact for `separate_authority_ref=None` | Replaced: no fact exists/is consumed; prerequisite is NOT_APPLICABLE |
| Revision 3 §12 unconditional `protected_authority_facts` interpretation | Replaced by exact filtered expected-fact sequence |
| Revision 2 §4.6 `ProviderInjectedFileRequirement(path, content_digest)` | Replaced by keyed exact provider-owned injected-file requirement |
| Revision 2 §4.3 boolean `supports_provider_injected_file_contract` | Replaced by exact provider injected-file capabilities |
| Revision 3 §18 `provider_injected_files` policy field | Retained with corrected requirement schema |
| Revision 3 §22 leaving provider-injected files outside WorkspacePlan | Replaced: exact tuple is embedded in WorkspacePlan |
| Revision 1 §18 informal `ALLOW | DENY` | Replaced by exact `ToolDecision` enum |
| Revision 1 §§19–21 prose-only Shell/Network/ExternalSideEffect containers | Replaced by exact schemas and validators |
| Revision 3 §18 complete WorkspacePolicyDefinition claim | Retained, now with fully frozen nested policy container schemas |

No other prior clause is reopened.

---

# 3. F009 correction — accepted Slice 2.3 authority-fact semantics

Accepted Slice 2.3 defines protected authority facts only for protected requirements whose:

```text
separate_authority_ref is not None
```

Slice 2.4 must preserve that contract exactly.

## 3.1 No-authority case

For a `ProtectedAssetWorkspaceBinding` with:

```text
binding.separate_authority_ref is None
```

the rule is:

```text
separate-authority prerequisite:
NOT_APPLICABLE

ProtectedVerificationAuthorityFact required:
NO

ProtectedVerificationAuthorityFact consumed:
NO
```

No synthetic fact is created.

No `ProtectedVerificationAuthorityFact(..., evaluated_authority_ref=None)` is expected.

No absence of such a fact contributes INDETERMINATE.

This is not a grant of authority.

It means only that this exact WorkPacket requirement did not declare a separate-authority prerequisite.

## 3.2 Authority-required case

For a binding with:

```text
binding.separate_authority_ref is not None
```

exactly one matching accepted Slice 2.3 fact is required:

```python
ProtectedVerificationAuthorityFact(
    evaluated_requirement_ref
        == binding.requirement_ref,

    evaluated_authority_ref
        == binding.separate_authority_ref,

    status=...
)
```

Status semantics:

```text
SATISFIED
    -> separate-authority prerequisite satisfied

INDETERMINATE
    -> workspace protected-authority contribution INDETERMINATE

UNSATISFIED
    -> workspace protected-authority contribution UNSATISFIED
```

## 3.3 Exact expected authority-fact sequence

Let:

```text
expected_authority_bindings :=
    plan.protected_asset_bindings
    filtered to
    separate_authority_ref is not None
```

The filter preserves the exact canonical binding order.

Let:

```text
expected_authority_subjects :=
    tuple(
      (
        binding.requirement_ref,
        binding.separate_authority_ref
      )
      for binding in expected_authority_bindings
    )
```

The supplied `WorkspaceConformanceFacts.protected_authority_facts` must obey the same missing-versus-mismatch semantics established by accepted Slice 2.3:

- supplied exact subjects in canonical expected order, with one or more expected subjects absent -> missing evidence / INDETERMINATE;
- unexpected subject -> UNSATISFIED;
- duplicate subject -> UNSATISFIED;
- reordered subject -> UNSATISFIED;
- correct requirement ref with wrong authority ref -> UNSATISFIED;
- extra fact when expected sequence is empty -> UNSATISFIED.

A binding with `separate_authority_ref=None` never appears in this sequence.

## 3.4 Revision-3 protected evaluation ordering correction

Revision 3 §11 step 3 becomes:

```text
3. if separate_authority_ref is non-None:
       exact separate-authority fact
   else:
       authority prerequisite NOT_APPLICABLE
       consume no authority fact
```

Everything else in the protected-asset derivation remains unchanged.

## 3.5 F009 tests

Freeze:

```text
binding authority None
+ zero authority facts
    -> no authority-related reason

binding authority None
+ extraneous fact
    -> UNSATISFIED

two bindings:
A authority None
B authority required
+ exact fact for B
    -> authority sequence valid

required fact missing first/middle/last
    -> INDETERMINATE

wrong authority ref
    -> UNSATISFIED

wrong requirement ref
    -> UNSATISFIED

duplicate fact
    -> UNSATISFIED

reordered facts
    -> UNSATISFIED
```

**F009 is closed by exact alignment with accepted Slice 2.3.**

---

# 4. F010 correction — provider-injected files are exact provider-owned materials

A path + digest alone is insufficient for `WorkspaceProvider.provision(plan)` to materialize bytes.

Revision 4 freezes a self-contained provider contract.

The exact provider descriptor/version owns the deterministic materialization implementation for named injected-file keys.

No external policy/content resolver is introduced.

---

# 5. ProviderInjectedFileCapability

Replace Revision-2 boolean support with exact capabilities:

```python
ProviderInjectedFileCapability(
    file_key: StableRequirementKey,
    content_digest: ContentDigest,
)
```

Meaning:

```text
For this exact WorkspaceProviderDescriptor identity,
the provider implementation can deterministically materialize
the exact bytes identified by file_key,
and the resulting bytes MUST hash to content_digest.
```

The capability contains no bytes.

The exact provider implementation/version is the byte source.

The content digest is the required independent verification.

## 5.1 Capability canonicality

`WorkspaceProviderDescriptor.provider_injected_file_capabilities` is:

```python
tuple[ProviderInjectedFileCapability, ...]
```

Canonical order:

```text
file_key
```

Rules:

- file_key unique;
- duplicate file_key invalid;
- same file_key with conflicting digest invalid;
- descriptor digest covers every capability.

The Revision-2 field:

```text
supports_provider_injected_file_contract: bool
```

is removed.

Capability tuple empty means no provider-owned injected files are supported.

---

# 6. Corrected ProviderInjectedFileRequirement

Freeze:

```python
ProviderInjectedFileRequirement(
    path: RepositoryPath,
    provider_file_key: StableRequirementKey,
    content_digest: ContentDigest,
)
```

The exact policy states:

```text
this provider-owned material
must appear at this exact workspace path
with this exact content digest
```

No source baseline or WorkPacket authority is modified by the injected content.

## 6.1 Requirement canonicality

Inside WorkspacePolicyDefinition:

canonical order:

```text
path
```

Rules:

- path unique;
- provider_file_key unique within one policy in schema v1;
- duplicate path invalid;
- duplicate provider_file_key invalid;
- same stable path/key with conflicting digest invalid.

The one-key/one-path rule avoids aliasing the same provider-owned helper into multiple paths in schema v1.

A later schema revision may explicitly permit aliases.

---

# 7. Provider injected-file preflight

For every policy requirement:

```python
ProviderInjectedFileRequirement(
    path=P,
    provider_file_key=K,
    content_digest=D,
)
```

the exact provider descriptor must contain:

```python
ProviderInjectedFileCapability(
    file_key=K,
    content_digest=D,
)
```

Exact key + digest required.

Rules:

```text
key absent
    -> UNSATISFIED

key present but digest differs
    -> UNSATISFIED

descriptor unavailable/unverifiable
    -> INDETERMINATE
```

No capability wildcard.

No latest provider file.

---

# 8. Corrected WorkspacePlan

Revision 1 WorkspacePlan is amended to include:

```python
WorkspacePlan(
    schema_version=1,
    plan_key,
    revision,

    work_packet_ref: WorkPacketRef,
    source_baseline_ref: SourceBaselineRef,
    role_contract_ref: RoleContractRef,

    workspace_policy_ref: WorkspacePolicyRef,
    governance_profile_ref: GovernanceProfileRef | None,

    provider_ref: WorkspaceProviderRef,

    required_property_keys:
        tuple[StableRequirementKey, ...],

    protected_asset_bindings:
        tuple[ProtectedAssetWorkspaceBinding, ...],

    workspace_credential_grants:
        tuple[WorkspaceCredentialGrant, ...],

    provider_injected_files:
        tuple[ProviderInjectedFileRequirement, ...],

    filesystem_policy: FilesystemPolicy,
    repository_metadata_policy: RepositoryMetadataPolicy,
    tool_policy: ToolPolicy,
    shell_policy: ShellPolicy,
    network_policy: NetworkPolicy,
    external_side_effect_policy: ExternalSideEffectPolicy,
    resource_limits: WorkspaceResourceLimits,
    retention_policy: WorkspaceRetentionPolicy,
)
```

No implicit policy lookup is required by the provider.

## 8.1 Exact mapping

Plan resolution requires:

```text
plan.provider_injected_files
    == workspace_policy.provider_injected_files
```

exactly.

No provider/runtime/resolver may add another planned injected file.

The tuple participates in canonical WorkspacePlan identity.

Mutation of:

- path;
- provider_file_key;
- content_digest;

changes WorkspacePlan digest.

---

# 9. Provider protocol remains self-contained

The provider protocol remains:

```python
class WorkspaceProvider(Protocol):
    def provision(
        plan: WorkspacePlan,
    ) -> WorkspaceProvisionResult: ...
```

The provider now receives every exact injected-file requirement directly from `plan.provider_injected_files`.

For each item it must:

1. resolve exact `provider_file_key` through its own exact provider implementation/version;
2. materialize bytes at exact `path`;
3. hash actual bytes;
4. require actual digest == planned `content_digest`;
5. report the injected path in initial WorkspaceInspection.

No external content store.

No WorkspacePolicyDefinition lookup.

No network fetch.

No arbitrary caller-provided bytes.

---

# 10. Provider-injected file inspection semantics

Initial inspection must classify every provider-injected file exactly.

For each planned injected file:

```text
exact path present
+
actual content digest == planned content_digest
    -> injected-file requirement SATISFIED

path missing
    -> UNSATISFIED

wrong content digest
    -> UNSATISFIED
```

Any provider-injected path not present in `plan.provider_injected_files`:

UNSATISFIED.

Provider-injected files are not baseline source content.

They are excluded from engineering change output only when:

- path is exactly declared;
- initial digest matches;
- terminal state remains exactly unchanged.

If a provider-injected file changes during execution, that change must appear in terminal change accounting and is evaluated against filesystem/scope policy.

---

# 11. F010 tests

Freeze:

```text
policy injected tuple == plan injected tuple
    -> required

policy tuple mutation
    -> plan digest changes

provider descriptor exact key+digest supported
    -> preflight eligible

provider key absent
    -> UNSATISFIED

provider key present / digest mismatch
    -> UNSATISFIED

planned file missing after provision
    -> UNSATISFIED

planned file wrong bytes/digest
    -> UNSATISFIED

undeclared injected path
    -> UNSATISFIED

declared injected file unchanged
    -> excluded from engineering changes with exact accounting

declared injected file changed
    -> appears in change accounting

provider protocol receives exact requirements through plan
    -> architecture test

no policy/content resolver used by provider
    -> architecture test
```

**F010 is closed by a self-contained WorkspacePlan/provider contract.**

---

# 12. F011 correction — ToolDecision

Freeze:

```text
ToolDecision:
  ALLOW
  DENY
```

No boolean substitute.

No third/default/unknown enum member.

Correct:

```python
WorkspaceToolRef(
    tool_key: StableRequirementKey,
    tool_definition_digest: ContentDigest,
)

ToolRule(
    tool_ref: WorkspaceToolRef,
    decision: ToolDecision,
)

ToolPolicy(
    default_decision: ToolDecision,
    rules: tuple[ToolRule, ...],
)
```

## 12.1 Tool policy canonicality

Canonical order:

```text
tool_ref.tool_key
```

Rules:

- one rule per tool_key;
- duplicate tool_key invalid;
- same tool_key with differing definition digest is stable-identity conflict;
- exact rule decision participates in policy digest;
- undeclared tool uses exact default_decision;
- a DENY rule is not overridden by another rule because duplicates are invalid.

No "best match" behavior.

---

# 13. ShellPolicy

Freeze:

```python
ShellPolicy(
    mode: ShellMode,
)
```

with existing exact enum:

```text
ShellMode:
  DENY
  UNRESTRICTED_WITHIN_DECLARED_BOUNDARY
```

No command allowlist.

No command regex.

No hidden shell settings.

The exact mode participates in WorkspacePolicyDefinition digest.

Provider preflight requires:

```text
shell_policy.mode
    in provider_descriptor.supported_shell_modes
```

---

# 14. NetworkEndpoint

Freeze exact schema-v1 endpoint identity:

```python
NetworkEndpoint(
    scheme: BoundedText,
    host: BoundedText,
    port: int,
)
```

Validators:

```text
scheme:
- nonblank
- ASCII
- lowercase
- pattern: [a-z][a-z0-9+.-]*

host:
- nonblank
- ASCII
- lowercase
- no whitespace
- no wildcard '*'
- no trailing '.'

port:
- integer
- 1 <= port <= 65535
```

The `host` value is an exact policy identity string.

Relay does not resolve DNS as part of policy identity.

Provider enforcement evidence owns DNS/IP behavior.

Canonical endpoint key:

```text
(scheme, host, port)
```

Duplicate exact endpoint invalid.

Same scheme+host+port is the complete stable identity; therefore conflicting duplicates cannot exist.

---

# 15. NetworkPolicy

Freeze:

```python
NetworkPolicy(
    mode: NetworkMode,
    allowed_endpoints: tuple[NetworkEndpoint, ...],
)
```

Existing enum:

```text
NetworkMode:
  DENY_ALL
  ALLOWLIST
  UNRESTRICTED
```

## 15.1 Mode invariants

```text
DENY_ALL
    -> allowed_endpoints == ()

UNRESTRICTED
    -> allowed_endpoints == ()

ALLOWLIST
    -> allowed_endpoints must be non-empty
```

This prevents multiple policy spellings for equivalent "no endpoints" semantics.

An empty allowlist must be expressed as `DENY_ALL`.

## 15.2 Canonicality

For ALLOWLIST:

- exact endpoint tuple sorted by `(scheme, host, port)`;
- unique;
- noncanonical order rejected;
- duplicates rejected.

Redirects do not add endpoint authority.

A redirected destination must itself be allowed by provider enforcement semantics or the request must be blocked.

The policy object itself does not perform DNS resolution.

---

# 16. ExternalEffectRef

Freeze:

```python
ExternalEffectRef(
    effect_key: StableRequirementKey,
    definition_digest: ContentDigest,
)
```

The ref identifies an externally defined exact mutating-effect class/operation contract.

Slice 2.4 does not define arbitrary effect detection from shell text.

Canonical identity:

```text
effect_key
```

Within one policy:

- one ref per effect_key;
- same effect_key with another digest is conflict/invalid.

---

# 17. ExternalSideEffectPolicy

Freeze:

```python
ExternalSideEffectPolicy(
    mode: ExternalSideEffectMode,
    allowed_effects: tuple[ExternalEffectRef, ...],
)
```

Existing enum:

```text
ExternalSideEffectMode:
  DENY_MUTATING_EFFECTS
  ALLOW_EXPLICIT_EFFECTS
  UNRESTRICTED
```

## 17.1 Mode invariants

```text
DENY_MUTATING_EFFECTS
    -> allowed_effects == ()

UNRESTRICTED
    -> allowed_effects == ()

ALLOW_EXPLICIT_EFFECTS
    -> allowed_effects must be non-empty
```

An empty explicit-effect list must be expressed as `DENY_MUTATING_EFFECTS`.

## 17.2 Canonicality

For ALLOW_EXPLICIT_EFFECTS:

- sort by effect_key;
- unique effect_key;
- conflict if same effect_key differs in definition_digest;
- noncanonical order rejected.

Provider/runtime mediation must be able to identify exact effect refs for positive enforcement.

If unmediated shell/network makes the required effect policy unenforceable at the requested ControlStrength:

UNSATISFIED preflight or conformance according to the exact known condition.

---

# 18. Corrected complete WorkspacePolicyDefinition

The complete schema-v1 policy is now:

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

Every named nested normative type is now frozen by Revision 1–4.

No opaque extension bag.

No `WorkspaceProviderRequirements`.

Unknown fields forbidden.

---

# 19. Corrected WorkspaceProviderDescriptor injected-file field

Revision 2 WorkspaceProviderDescriptor is amended only for F010:

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

    provider_injected_file_capabilities:
        tuple[ProviderInjectedFileCapability, ...],
)
```

The removed boolean field must not exist.

All existing canonical enum-order rules remain.

Injected-file capabilities sort by file_key and are unique.

---

# 20. WorkspacePolicyDefinition canonical identity completion

Canonical JSON/digest rules remain:

```text
UTF-8
sort_keys=True
separators=(",", ":")
ensure_ascii=False
allow_nan=False
no float normative values
SHA-256 over exact canonical bytes
```

Revision 4 freezes the remaining nested collection keys:

```text
tool_policy.rules:
    tool_ref.tool_key

network_policy.allowed_endpoints:
    scheme / host / port

external_side_effect_policy.allowed_effects:
    effect_key

provider_injected_files:
    path

provider descriptor injected-file capabilities:
    file_key
```

Stable identity collision with conflicting normative content:
reject.

No arbitrary secondary sorting to hide conflicts.

---

# 21. Fixed canonical vectors

Implementation must freeze literal canonical JSON and SHA-256 vectors for at least:

## Minimal policy

```text
- no governance profile
- empty property requirements where legal for the fixture
- explicit filesystem policy
- explicit RepositoryMetadataPolicy
- explicit ToolPolicy with default
- explicit ShellPolicy
- NetworkPolicy DENY_ALL / empty endpoints
- ExternalSideEffectPolicy DENY_MUTATING_EFFECTS / empty effects
- empty credential policy
- no optional resource limits
- exact retention policy
- no provider-injected files
```

## Full policy

```text
- governance profile
- non-empty properties
- repository metadata access
- non-empty tool rules
- shell mode
- ALLOWLIST with canonical endpoints
- ALLOW_EXPLICIT_EFFECTS with canonical effect refs
- credential grants
- resource limits
- retention
- provider-injected file requirements
```

Any nested normative mutation changes policy digest.

---

# 22. WorkspacePlan canonical identity completion

WorkspacePlan canonical identity now explicitly includes:

```text
provider_injected_files
```

with canonical order by path and the same uniqueness/conflict rules as policy.

Existing canonical rules remain for:

- protected bindings;
- credential grants;
- other nested policy values.

Fixed plan vectors must include:

- no injected files;
- one or more injected files.

Changing provider_file_key, injected path, or digest must change plan digest.

---

# 23. F011 deterministic tests

Freeze:

```text
ToolDecision only ALLOW/DENY

tool rule decision mutation
    -> policy digest changes

tool duplicate key
    -> invalid

tool stable key + conflicting definition digest
    -> invalid

ShellPolicy.mode mutation
    -> policy digest changes

NetworkPolicy DENY_ALL + endpoint
    -> invalid

NetworkPolicy UNRESTRICTED + endpoint
    -> invalid

NetworkPolicy ALLOWLIST + empty tuple
    -> invalid

endpoint noncanonical scheme/host
    -> invalid

endpoint port outside 1..65535
    -> invalid

endpoint reorder
    -> invalid

endpoint duplicate
    -> invalid

ExternalSideEffectPolicy DENY_MUTATING_EFFECTS + effect
    -> invalid

UNRESTRICTED + effect
    -> invalid

ALLOW_EXPLICIT_EFFECTS + empty tuple
    -> invalid

effect reorder
    -> invalid

duplicate effect_key
    -> invalid

same effect_key + conflicting digest
    -> invalid

minimal fixed policy vector
    -> exact SHA-256

full fixed policy vector
    -> exact SHA-256
```

**F011 is closed by complete policy-container schemas.**

---

# 24. Updated exact plan-resolution order

The Revision-2 resolver order is retained and extended only where needed:

```text
1. exact WorkPacketRef
2. exact WorkPacketConformanceFact
3. exact WorkspacePolicyRef present
4. exact WorkspacePolicyDefinition digest match
5. exact policy/profile binding
6. exact RoleContract binding
7. exact protected semantic permissions
8. exact protected authority facts only for non-None authority requirements
9. exact provider descriptor
10. exact semantic provider compatibility
11. exact provider-injected file key/digest capability compatibility
12. exact credential subset mapping
13. produce self-contained WorkspacePlan
```

Plan exists only on SATISFIED resolution.

SATISFIED != execution authority.

---

# 25. Updated A01–A18 coverage

Combined Revision 1 + Revision 2 + Revision 3 + Revision 4:

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

All WorkspacePolicyDefinition nested normative types are frozen and digestable.

## A02

WorkspacePlan is self-contained and now includes provider-injected-file requirements.

## A03

No authority creation introduced.

## A04

Provider descriptor and instance evidence remain separate; provider material capabilities are exact.

## A05

Exact source/initial state plus exact provider-injected material accounting are representable.

## A06

Filesystem/path semantics unchanged.

## A07

Protected authority consumption now exactly matches accepted Slice 2.3.

## A08

ToolDecision and ShellPolicy are fully frozen.

## A09

NetworkPolicy and ExternalSideEffectPolicy are fully frozen.

## A10

Credential policy remains frozen from Revision 3.

## A11

Resource/retention unchanged.

## A12

Environment provenance unchanged.

## A13

Workspace property mapping unchanged.

## A14

Exact change/inspection state unchanged.

## A15

RuntimeWorkspaceAttachment unchanged.

## A16

Local-provider ceiling unchanged.

## A17

No remaining known undefined/mismatched schema path in F001–F011.

## A18

No DB/orchestration/runtime/Phase 3 leakage introduced.

---

# 26. Revision 4 implementation impact

The proposed implementation package remains:

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

No accepted Slice 2.1 / 2.2 / 2.3 source model changes are required.

No DB migration.

No policy resolver/content store.

No runtime invocation.

---

# 27. Preserved authority boundary

```text
no ProtectedVerificationAuthorityFact for None
    != authority grant

provider injected-file capability
    != authority

provider-owned injected bytes
    != source baseline

ToolPolicy ALLOW
    != work authority

NetworkPolicy reachability
    != external mutation authority

ExternalSideEffectPolicy allowance
    != Human authority

WorkspacePlan
    != execution authority

WorkspaceConformance SATISFIED
    != execution authority

successful provider provisioning
    != engineering acceptance
```

Phase 3 remains the future orchestration/execution-authority composition owner.

---

# 28. Revision 4 disposition

```text
Slice 2.4:
OPEN

RLY-S24-DESIGN-EVAL-001:
REWORK — HISTORICAL

RLY-S24-DESIGN-EVAL-002:
REWORK — HISTORICAL

RLY-S24-DESIGN-EVAL-003:
REWORK — HISTORICAL

F001–F008:
CLOSED BY PRIOR REVISIONS

F009:
CLOSED BY REVISION 4

F010:
CLOSED BY REVISION 4

F011:
CLOSED BY REVISION 4

Design acceptance:
PENDING INDEPENDENT REVIEW 004

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

# 29. Next gate

```text
STOP FOR SOL INDEPENDENT DESIGN REVIEW 004
```

The independent evaluator must review:

```text
Revision 1
+
Revision 2
+
Revision 3
+
Revision 4
```

and return exactly:

```text
ACCEPT
REWORK
ESCALATE
```

No implementation authority is implied.

**Revision 4 design cleanup != design acceptance. Design acceptance != implementation authority.**
