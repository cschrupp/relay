# Slice 2.4 — Execution Workspace Authority — Design Revision 1

**Document class:** Lockable Slice design record  
**Status:** DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Design authority:** RLY-S24-DESIGN-AUTH-001 — AUTHORIZED  
**Design-authority commit:** 7e96c34d97729daadc3606d6809d95f9e3145e51  
**Design branch:** design/2.4-execution-workspace-authority

---

# 1. Purpose

Slice 2.4 defines the deterministic Relay contract for one exact execution workspace.

It answers:

~~~text
What exact WorkPacket is this workspace for?
What exact source baseline is materialized?
What exact workspace policy applies?
What exact provider is being used?
What controls can that provider theoretically supply?
What controls were actually established for this instance?
What repository/filesystem paths may be read or written?
What protected verification assets may be read, executed, evaluated, or mutated?
What tools may be exposed?
What network reachability is permitted?
What credentials, if any, may be exposed inside the workspace?
What resource limits apply?
What environment was actually provisioned?
What changed?
Was the workspace clean at start?
Did required controls remain continuous?
Was teardown/retention completed as required?
~~~

The central invariant is:

~~~text
WorkspacePolicyDefinition
    + exact WorkPacket
    + exact RoleContract
    + exact provider
    + exact source baseline
    -> exact WorkspacePlan
    -> provider preflight
    -> exact WorkspaceInstance
    -> enforcement/provenance evidence
    -> WorkspaceConformance

WorkspacePlan != authority
WorkspaceConformance SATISFIED != execution authorized
~~~

Slice 2.4 supplies workspace enforcement contracts and evidence.

It does not decide whether work may execute.

---

# 2. Governing lineage

This design is governed by:

~~~text
Canonical Slice 2.3 closed baseline:
3ea0bcf626a28f85b9a8a2ba7ea59cb111cb77fc

Slice 2.3:
COMPLETE / ACCEPTED / CLOSED

Slice 2.3 closure:
RLY-S23-CLOSE-EVAL-001 — ACCEPT

Slice 2.4 opening:
RLY-S24-OPEN-001 — OPEN

Opening commit:
4a2a97b706c976d5d57680aadb3cdb8faa4474e9

Slice 2.4 design authority:
RLY-S24-DESIGN-AUTH-001 — AUTHORIZED

Design-authority commit:
7e96c34d97729daadc3606d6809d95f9e3145e51

Planning source:
docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY.md

Planning-source blob:
01edb5cf787280d68d9214b7c8b81abe6d7d5bf9

Accepted Slice 2.1 Agent Runtime implementation:
4f785f08576e465cd0aa278f927fa4b7253e3f49

Accepted Slice 2.2 Role Contracts implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Accepted Slice 2.3 Work-Packet implementation:
861ccb6bda528a98e1f570a32dcddc61358732e7
~~~

The planning source is design input only.

This design is normative where it refines that planning source.

---

# 3. Design problem

Relay now has:

- exact Project/Slice/Baseline identity;
- Human/governance authority mechanisms;
- accepted Role Contracts;
- exact WorkPackets and ContextManifests;
- runtime request/session/provenance contracts;
- GovernanceProfile and Protected Verification Asset semantics.

What remains missing is a deterministic enforcement boundary between:

~~~text
an exact governed WorkPacket
and
the mutable environment in which an executor may operate
~~~

Without Slice 2.4, a runtime could receive the correct WorkPacket yet still operate in an environment that:

- points at the wrong commit;
- includes stale or pre-existing changes;
- exposes writable paths outside scope;
- exposes protected verification assets too broadly;
- exposes tools stronger than policy allows;
- permits undeclared network access;
- leaks credentials;
- cannot establish resource boundaries;
- cannot prove what environment was used;
- cannot establish what changed;
- cannot prove teardown;
- silently degrades a required control because the selected backend cannot enforce it.

Slice 2.4 closes that gap.

---

# 4. Non-authority invariants

The following are normative:

~~~text
workspace capability != authority
workspace provider capability != control enforcement
workspace creation != work authorization
workspace plan != authority
workspace policy != Human authority
workspace conformance != execution authority
workspace conformance != engineering acceptance

filesystem visibility != write authority
filesystem write capability != permission for all visible paths
tool availability != permission to invoke a tool
shell availability != permission for arbitrary external side effects
network reachability != permission for external mutation
credential availability != permission to expose or use a credential
resource availability != permission to consume without policy

protected-asset visibility != mutation authority
protected-asset evaluation != mutation authority
evaluator role != mutation authority

exact checkout != authority
clean checkout != authority
successful execution != authority
successful teardown != acceptance
historical success != current waiver

WorkPacket conformance SATISFIED != execution authorized
RoleContract APPLICABLE != execution authorized
RuntimeCapability != workspace authority
PROPOSED_WORK != authorized work
BACKLOG_EXHAUSTED != permission to invent successor work
~~~

Human root authority and current work/execution authority remain external.

---

# 5. Ownership boundaries

## 5.1 Slice 2.4 owns

Slice 2.4 owns:

- WorkspacePolicyDefinition materialization for WorkspacePolicyRef;
- exact WorkspacePolicyDefinition digest;
- exact WorkspacePlan representation/ref/digest;
- exact workspace provider descriptor/ref/digest;
- provider capability representation;
- workspace property requirements;
- filesystem policy representation;
- tool exposure policy;
- shell exposure policy;
- network reachability policy;
- external-side-effect policy;
- workspace credential exposure policy;
- workspace resource policy;
- workspace retention policy;
- exact protected-asset workspace bindings;
- workspace provider preflight;
- workspace instance identity;
- exact source repository/commit/root binding;
- environment provenance;
- initial clean-state evidence;
- workspace property enforcement evidence;
- dirty-state inspection;
- exact change manifest;
- teardown/retention evidence;
- workspace conformance;
- derivation of RuntimeWorkspaceAttachment from a conforming instance.

## 5.2 Slice 2.3 remains owner of

Slice 2.3 remains owner of:

- WorkPacket / WorkPacketRef;
- SourceBaselineRef;
- WorkspacePolicyRef transport;
- required_workspace_property_keys;
- PolicyBasisRef;
- GovernanceProfileRef transport;
- RoleContractRef transport;
- credential_refs;
- runtime declarations;
- protected_verification_requirements;
- WorkPacket conformance.

Slice 2.4 consumes exact Slice 2.3 values.

It never creates or amends a WorkPacket.

## 5.3 Slice 2.2 remains owner of

Slice 2.2 remains owner of:

- RoleContract / RoleContractRef;
- RoleAction;
- VerificationAssetPermission;
- actor/action eligibility;
- protected-verification semantic permissions;
- role required assurance properties;
- role separation;
- successor / BACKLOG_EXHAUSTED semantics.

Slice 2.4 may enforce a narrower physical permission than the role permits.

It may never widen a RoleContract permission.

## 5.4 Slice 2.1 remains owner of

Slice 2.1 remains owner of:

- RuntimeCapability;
- RuntimeWorkspaceAttachment;
- RuntimePermissionProfileRef;
- CredentialRef;
- RuntimeExecutionLimits;
- runtime/provider/model selection/provenance;
- runtime request/session/events/results/cancellation.

Slice 2.4 may derive RuntimeWorkspaceAttachment.

Slice 2.4 does not invoke AgentRuntime.

## 5.5 Phase 3 remains owner of

Phase 3 remains owner of:

- selecting the exact currently authorized WorkPacket;
- binding actor and execution identity;
- establishing current execution authority;
- combining authority + RoleContract + WorkPacket + Workspace + Runtime predicates;
- final runtime input construction;
- AgentRuntime invocation;
- engineering-result collection;
- successor orchestration;
- real-project execution.

---

# 6. Threat and boundary model

Slice 2.4 must not collapse all workspace backends into one security claim.

Normative distinctions:

~~~text
local same-user directory
    != strong security boundary

local same-user Git worktree
    != strong security boundary

local same-user disposable clone
    != strong security boundary

container boundary
    != host/root/kernel boundary

remote isolated sandbox
    != universal proof of policy enforcement

post-execution detection
    != preventive enforcement

tool mediation
    != OS isolation

chmod/read-only mode under same privileged actor
    != unbypassable mutation prevention
~~~

Schema v1 evaluates controls relative to a declared provider boundary.

It does not claim protection from:

- compromised host kernel;
- host root/administrator;
- provider control plane compromise;
- malicious hardware/firmware;
- capabilities outside the declared provider boundary.

Those stronger threat models require separately designed controls.

---

# 7. Control-strength model

Provider capability and actual enforcement are distinct.

Use:

~~~text
ControlStrength:
  DETECTIVE
  MEDIATED
  BOUNDARY_ENFORCED
~~~

Meaning:

DETECTIVE
- Relay can observe/check a condition or violation;
- the environment does not necessarily prevent the violation.

MEDIATED
- all in-scope operations are intended to pass through an exact mediator;
- bypass outside that mediator may still be possible under the declared boundary.

BOUNDARY_ENFORCED
- the declared provider boundary prevents the prohibited operation for processes operating inside that boundary, subject to the stated threat model.

Strength ordering is normative:

~~~text
DETECTIVE < MEDIATED < BOUNDARY_ENFORCED
~~~

A provider descriptor may advertise a maximum strength.

Actual workspace evidence must independently establish the strength reached by the exact instance.

Provider capability alone never produces SATISFIED conformance.

---

# 8. Workspace property vocabulary

Schema v1 defines a bounded workspace property vocabulary:

~~~text
WorkspaceProperty:
  EXACT_SOURCE_BASELINE
  CLEAN_INITIAL_STATE
  REPOSITORY_METADATA_ISOLATED
  FILESYSTEM_SCOPE
  PATH_ESCAPE_CONTROL
  PROTECTED_ASSET_CONTROL
  TOOL_EXPOSURE_CONTROL
  NETWORK_REACHABILITY_CONTROL
  EXTERNAL_SIDE_EFFECT_CONTROL
  CREDENTIAL_EXPOSURE_CONTROL
  RESOURCE_LIMIT_CONTROL
  ENVIRONMENT_PROVENANCE
  DIRTY_STATE_INSPECTION
  CHANGESET_EXTRACTION
  RETENTION_CONTROL
  TEARDOWN_CONTROL
  CONTROL_CONTINUITY
~~~

A property is not an authority state.

---

# 9. WorkspacePropertyRequirement

Conceptual value:

~~~python
WorkspacePropertyRequirement(
    key: StableRequirementKey,
    property: WorkspaceProperty,
    minimum_strength: ControlStrength,
)
~~~

Rules:

- key is stable lowercase Slice 2.3-compatible key;
- keys are unique and canonical;
- a property may appear under more than one key only if policy intentionally defines separate obligations;
- same key with conflicting normative content is invalid;
- WorkPacket.required_workspace_property_keys must resolve to exact keys in WorkspacePolicyDefinition;
- an unknown required key is fail-closed;
- policy may require additional properties beyond WorkPacket.required_workspace_property_keys;
- the WorkPacket cannot weaken those additional policy requirements.

---

# 10. WorkspacePolicyDefinition

WorkspacePolicyRef in Slice 2.3 is reference-only.

Slice 2.4 defines the exact materialized content it references.

Conceptual schema:

~~~python
WorkspacePolicyDefinition(
    schema_version=1,

    policy_key,
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
    provider_requirements: WorkspaceProviderRequirements,
)
~~~

Identity:

~~~text
WorkspacePolicyRef.policy_key
    == WorkspacePolicyDefinition.policy_key

WorkspacePolicyRef.content_digest
    == SHA-256(canonical WorkspacePolicyDefinition bytes)
~~~

Provide pure helpers:

~~~python
canonical_workspace_policy_json(...)
digest_workspace_policy(...)
workspace_policy_ref_matches(...)
~~~

No latest/current policy lookup exists.

---

# 11. Policy/profile binding

WorkspacePolicyDefinition binds:

- exact PolicyBasisRef;
- exact GovernanceProfileRef or exact absence.

When used for a WorkPacket:

~~~text
definition.policy_basis_ref
    == packet.policy_basis_ref

definition.governance_profile_ref
    == packet.governance_profile_ref
~~~

A mismatch is known incompatible policy and is UNSATISFIED.

No provider, runtime, implementer, workflow, or agent may substitute a weaker profile/policy.

If policy/profile materialization cannot be established exactly:

INDETERMINATE / STOP.

---

# 12. Repository path model

Schema v1 uses repository-relative POSIX paths.

Canonical rules:

- no leading slash;
- no backslash;
- no NUL/control character;
- no empty interior segment;
- no "." segment;
- no ".." segment;
- no repeated slash;
- case is preserved and comparisons are case-sensitive at the Relay semantic layer;
- "." is reserved as the only root-prefix sentinel.

Path-prefix match is segment-aware:

~~~text
src
matches:
src
src/a.py
src/package/b.py

does not match:
src-old/x.py
~~~

Provider-specific filesystem case behavior must be represented in environment/provider evidence.

If the provider cannot preserve the semantic path model required by policy, conformance is fail-closed.

---

# 13. Filesystem policy

Use:

~~~text
FilesystemAccess:
  DENY
  READ_ONLY
  READ_WRITE
~~~

Conceptual:

~~~python
FilesystemPolicy(
    default_access: FilesystemAccess,
    writable_prefixes: tuple[RepositoryPathPrefix, ...],
    denied_prefixes: tuple[RepositoryPathPrefix, ...],
)
~~~

Rules:

1. denied prefixes always win;
2. protected-asset rules can only narrow ordinary filesystem access;
3. writable prefixes may widen READ_ONLY default to READ_WRITE;
4. writable prefixes cannot override DENY;
5. no implicit write access exists outside exact policy;
6. noncanonical/redundant/conflicting prefixes are rejected.

A provider must evaluate effective access after canonical path resolution.

---

# 14. Path escape and link semantics

A path string inside the repository is not enough.

For any provider claiming MEDIATED or BOUNDARY_ENFORCED filesystem scope:

- symbolic-link traversal must not escape the workspace root;
- mount/reparse/bind semantics must not silently escape the workspace boundary;
- writable hard-link aliases outside the intended boundary must be prevented or made impossible by the provider boundary;
- path resolution races must not create an unobserved escape;
- repository root identity must remain the exact provisioned root.

A local same-user clone may detect many path issues but cannot claim universal BOUNDARY_ENFORCED protection against a same-user process with arbitrary host filesystem access.

---

# 15. Repository metadata policy

Git metadata is distinct from working-tree content.

Use:

~~~text
RepositoryMetadataAccess:
  DENY
  READ_ONLY
  LOCAL_MUTATION
~~~

LOCAL_MUTATION means:

- mutation is limited to the isolated workspace repository metadata;
- canonical source repository refs are not the same mutable metadata store;
- remote repository writes remain governed separately by network/external-side-effect policy.

A same-repository Git worktree shares common Git metadata.

Therefore:

~~~text
local Git worktree
    cannot satisfy REPOSITORY_METADATA_ISOLATED
    at BOUNDARY_ENFORCED strength
~~~

A disposable clone with independent metadata can establish stronger repository-metadata isolation, although it still does not create general OS isolation.

---

# 16. Protected verification assets

WorkPacket.protected_verification_requirements is the exact per-work protected-asset input.

RoleContract.verification_asset_permissions is the role-level maximum semantic permission set.

For each required asset:

~~~python
ProtectedAssetWorkspaceBinding(
    requirement_ref: ProtectedVerificationRequirementRef,
    artifact: Artifact,
    requested_operation: VerificationAssetPermission,
    effective_operation: VerificationAssetPermission,
    separate_authority_ref: AuthorityBasisRef | None,
    workspace_path,
)
~~~

Rules:

- requested_operation must be permitted by exact accepted RoleContract;
- effective_operation must never exceed requested_operation;
- effective_operation must never exceed RoleContract permission;
- separate authority must be externally established where WorkPacket requires it;
- evaluator role/status alone never grants mutation authority;
- READ does not imply MODIFY;
- EXECUTE does not imply MODIFY;
- EVALUATE does not imply MODIFY;
- MODIFY does not imply APPROVE_MUTATION;
- a policy may narrow to less access than the role permits;
- a policy may not widen beyond role/work authority.

Protected bindings are exact and canonical.

---

# 17. Protected-asset physical enforcement

For a provider to claim PROTECTED_ASSET_CONTROL:

DETECTIVE
- before/after exact content digests can establish whether a protected asset changed.

MEDIATED
- exact tool mediation prevents mutation through the mediated path, but bypass may remain under the declared boundary.

BOUNDARY_ENFORCED
- the provider boundary prevents prohibited mutation, such as a read-only mount/overlay inaccessible for write from inside the execution boundary.

A same-user chmod/read-only bit alone is not BOUNDARY_ENFORCED.

Post-run unchanged digest is evidence that mutation was not observed.

It is not proof that mutation was physically impossible.

---

# 18. Tool policy

Tool identity must be exact.

Conceptual:

~~~python
WorkspaceToolRef(
    tool_key,
    tool_definition_digest,
)

ToolRule(
    tool_ref,
    decision: ALLOW | DENY,
)

ToolPolicy(
    default_decision,
    rules,
)
~~~

The ref identifies tool definition/provenance already captured elsewhere.

Slice 2.4 does not create a generic tool-definition registry.

Rules:

- exact tool identity/digest only;
- no "latest tool" alias;
- DENY wins on conflict;
- undeclared tools follow default policy;
- provider capability to expose a tool does not mean the tool is allowed;
- allowed tool does not authorize operations outside other workspace controls.

---

# 19. Shell policy

Schema v1 intentionally does not design a shell-language parser.

Use:

~~~text
ShellMode:
  DENY
  UNRESTRICTED_WITHIN_DECLARED_BOUNDARY
~~~

There is no schema-v1 "allow these shell strings" security claim.

Reason:

~~~text
shell text parsing
    != reliable capability enforcement
~~~

If shell is available:

- the provider must declare the actual boundary containing it;
- network/filesystem/credential/resource restrictions must be enforced independently;
- a provider cannot claim fine-grained command restriction merely because a prompt told the agent not to run a command.

Future command mediation may be added only through a separately designed exact tool interface.

---

# 20. Network policy

Use:

~~~text
NetworkMode:
  DENY_ALL
  ALLOWLIST
  UNRESTRICTED
~~~

Conceptual endpoint:

~~~python
NetworkEndpoint(
    scheme,
    host,
    port,
)
~~~

Rules:

- allowlist entries are canonical and exact;
- hostname matching is explicit;
- redirects do not implicitly widen an allowlist;
- DNS/IP behavior must be covered by provider enforcement evidence;
- network reachability and external mutation are separate concepts.

A local same-user process with normal host networking cannot honestly claim BOUNDARY_ENFORCED DENY_ALL merely because the task instructions say "do not use network".

---

# 21. External side-effect policy

Network reachability does not authorize mutating an external system.

Use:

~~~text
ExternalSideEffectMode:
  DENY_MUTATING_EFFECTS
  ALLOW_EXPLICIT_EFFECTS
  UNRESTRICTED
~~~

Conceptual exact effect key:

~~~python
ExternalEffectRef(
    effect_key,
    definition_digest,
)
~~~

This is reference-only.

It does not attempt to classify arbitrary shell commands.

If policy requires DENY_MUTATING_EFFECTS but the provider/runtime exposes an unmediated shell with unrestricted network, the provider cannot establish that control at MEDIATED or BOUNDARY_ENFORCED strength.

The result is fail-closed.

---

# 22. Credential policy

CredentialRef never contains secret material.

Slice 2.4 must preserve that boundary.

Use:

~~~text
CredentialExposureMode:
  NONE
  ENVIRONMENT
  FILE
  PROVIDER_NATIVE
~~~

Conceptual:

~~~python
WorkspaceCredentialGrant(
    credential_ref: CredentialRef,
    exposure_mode,
    exposure_key,
)
~~~

Rules:

- only CredentialRefs present in WorkPacket.credential_refs may be exposed;
- WorkspacePolicyDefinition selects which declared refs are workspace-visible;
- packet credential presence does not imply workspace exposure;
- runtime/provider credentials may remain outside the workspace entirely;
- no secret bytes, secret hashes, or secret values appear in Relay workspace models/evidence;
- extra credential exposure is UNSATISFIED;
- missing required credential provisioning is INDETERMINATE unless positively unavailable/incompatible;
- teardown evidence must indicate whether workspace-scoped credential exposure was revoked/removed when the provider can establish that fact.

---

# 23. Resource limits

Use integer-only deterministic values.

Conceptual:

~~~python
WorkspaceResourceLimits(
    max_memory_bytes: int | None,
    max_disk_bytes: int | None,
    max_processes: int | None,
    max_cpu_seconds: int | None,
    max_open_files: int | None,
)
~~~

No floats.

A None value means no requirement for that specific limit from this policy.

A provider that cannot enforce a required non-null limit cannot satisfy RESOURCE_LIMIT_CONTROL at the required strength.

RuntimeExecutionLimits from Slice 2.1 remain separate.

Workspace resource limits do not replace:

- runtime max duration;
- max tool calls;
- max runtime output bytes.

---

# 24. Retention policy

Use:

~~~text
WorkspaceRetentionMode:
  DELETE_ON_TERMINAL
  RETAIN_ON_FAILURE
  RETAIN_UNTIL_EXPLICIT_RELEASE
~~~

Conceptual:

~~~python
WorkspaceRetentionPolicy(
    mode,
    max_retention_seconds: int | None,
)
~~~

Rules:

- retention is exact policy;
- retained workspace is not authority to resume work;
- resume requires separate current work/execution authority;
- credential exposure must not persist merely because the workspace is retained unless exact policy permits it;
- terminal evidence records actual retained/deleted outcome.

---

# 25. Provider identity

Use content-addressed exact provider descriptors.

Conceptual:

~~~text
WorkspaceBackendKind:
  LOCAL_CLONE
  LOCAL_WORKTREE
  CONTAINER
  REMOTE_ISOLATED
  OTHER
~~~

~~~text
WorkspaceBoundaryClass:
  SAME_USER_NO_SECURITY_BOUNDARY
  MEDIATED_PROCESS_BOUNDARY
  CONTAINER_BOUNDARY
  REMOTE_ISOLATED_BOUNDARY
~~~

Conceptual:

~~~python
WorkspaceProviderDescriptor(
    schema_version=1,
    provider_id: RuntimeIdentifier,
    provider_version: RuntimeIdentifier,
    backend_kind: WorkspaceBackendKind,
    boundary_class: WorkspaceBoundaryClass,
    property_capabilities:
        tuple[WorkspaceProviderPropertyCapability, ...],
)

WorkspaceProviderPropertyCapability(
    property: WorkspaceProperty,
    maximum_strength: ControlStrength,
)
~~~

Provider ref:

~~~python
WorkspaceProviderRef(
    provider_id,
    provider_version,
    descriptor_digest,
)
~~~

No latest provider lookup.

---

# 26. Capability declaration is not enforcement evidence

This distinction is normative:

~~~text
ProviderDescriptor says:
"this implementation can enforce network denial"

does not establish:

"network denial was enforced for workspace X"
~~~

ProviderDescriptor supports preflight only.

Actual instance evidence is separately required.

A provider may overstate its descriptor due to defect.

Therefore conformance never uses descriptor capability alone as final positive evidence.

---

# 27. WorkspacePlan

WorkspacePlan is the immutable resolved contract for one intended workspace instance class.

Conceptual:

~~~python
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

    filesystem_policy,
    repository_metadata_policy,
    tool_policy,
    shell_policy,
    network_policy,
    external_side_effect_policy,
    resource_limits,
    retention_policy,
)
~~~

WorkspacePlanRef:

~~~python
WorkspacePlanRef(
    work_packet_ref,
    plan_key,
    revision,
    content_digest,
)
~~~

Plan is content-addressed.

No latest/max resolution.

---

# 28. WorkspacePlan resolution inputs

The pure resolver consumes exact already-materialized inputs:

- WorkPacket;
- WorkPacketRef;
- WorkPacketConformance;
- WorkspacePolicyDefinition;
- exact accepted RoleContract;
- exact provider descriptor;
- exact external facts required for protected-asset mutation authority where applicable.

The resolver must verify:

~~~text
work_packet_ref(packet) == supplied WorkPacketRef

WorkPacketConformance refers to same exact WorkPacketRef

WorkPacketConformance.status == SATISFIED

workspace policy ref matches exact policy definition

policy basis matches WorkPacket

governance profile matches WorkPacket

RoleContractRef matches exact RoleContract

all requested protected operations permitted by RoleContract

all separate mutation authority requirements established

all WorkPacket required_workspace_property_keys exist in policy

provider descriptor ref exact

provider advertised maximum strength is at least each required minimum strength

provider can represent required policy semantics
~~~

A successful resolution means:

~~~text
the plan is internally conforming and provider-compatible
~~~

It does not mean execution is authorized.

---

# 29. Policy narrowing and no weakening

The resolved plan is the least-privilege result.

Rules:

- policy may be stricter than WorkPacket requirements;
- provider may enforce stricter controls than plan;
- provider may not weaken required controls;
- RoleContract may permit more than this WorkPacket needs;
- plan grants only what this exact WorkPacket needs;
- WorkPacket cannot select a weaker WorkspacePolicyDefinition than its exact ref;
- provider cannot silently downgrade required ControlStrength;
- failure to satisfy a stricter policy is fail-closed.

No automatic "best effort" downgrade exists.

---

# 30. WorkspacePlan canonical identity

Canonical JSON:

~~~text
UTF-8
sort_keys=True
separators=(",", ":")
ensure_ascii=False
allow_nan=False
no floating-point normative values
~~~

All non-semantic collections must use explicit canonical ordering.

At minimum:

- property requirements by key;
- path prefixes lexicographically;
- protected bindings by artifact path/id/operation;
- tool rules by tool key/digest;
- network endpoints by scheme/host/port;
- effect refs by key/digest;
- credential grants by credential_id/exposure;
- provider capabilities by WorkspaceProperty enum declaration;
- change entries by path.

Stable sort identity collision with conflicting normative content is rejected.

Never add arbitrary secondary ordering merely to hide a conflict.

---

# 31. Provider preflight

Pure preflight:

~~~python
evaluate_workspace_preflight(
    plan,
    provider_descriptor,
) -> WorkspacePreflight
~~~

Result:

~~~python
WorkspacePreflight(
    status: RequirementStatus,
    reasons,
    unsupported_property_keys,
)
~~~

Semantics:

Known provider incompatibility:
UNSATISFIED

Provider descriptor missing/stale/unverifiable:
INDETERMINATE

All exact requirements theoretically supported:
SATISFIED

Important:

~~~text
preflight SATISFIED != actual control enforcement
preflight SATISFIED != execution authority
~~~

---

# 32. WorkspaceProvider protocol

Conceptual provider interface:

~~~python
class WorkspaceProvider(Protocol):
    def describe() -> WorkspaceProviderDescriptor: ...

    def provision(
        plan: WorkspacePlan,
    ) -> WorkspaceProvisionResult: ...

    def inspect(
        instance_ref: WorkspaceInstanceRef,
    ) -> WorkspaceInspection: ...

    def extract_changes(
        instance_ref: WorkspaceInstanceRef,
    ) -> WorkspaceChangeManifest: ...

    def teardown(
        instance_ref: WorkspaceInstanceRef,
    ) -> WorkspaceTeardownEvidence: ...
~~~

Production invocation of provision/teardown remains Phase 3/orchestration-controlled.

The protocol itself does not authorize calls.

---

# 33. Workspace instance identity

Conceptual:

~~~python
WorkspaceInstanceRef(
    workspace_id: RuntimeIdentifier,
    plan_ref: WorkspacePlanRef,
    provider_ref: WorkspaceProviderRef,
    repository: RepositoryRef,
    source_commit: CommitRef,
    root: absolute POSIX path,
)
~~~

Rules:

- source_commit.repository == repository;
- source_commit == plan.source_baseline_ref.commit;
- root is exact provider-created root;
- workspace_id is provider-issued opaque identity;
- instance ref is immutable;
- same workspace_id with conflicting plan/provider/source/root is identity conflict.

No workspace instance can float to another branch/commit.

---

# 34. WorkspaceProvisionResult

Conceptual:

~~~python
WorkspaceProvisionResult(
    instance_ref: WorkspaceInstanceRef,
    runtime_attachment: RuntimeWorkspaceAttachment,
    environment_provenance: WorkspaceEnvironmentProvenance,
    initial_inspection: WorkspaceInspection,
    property_evidence: tuple[WorkspacePropertyEvidence, ...],
)
~~~

Provision must establish exact source commit.

If the exact commit cannot be materialized, provisioning fails.

A branch name alone is never sufficient baseline identity.

---

# 35. RuntimeWorkspaceAttachment derivation

Slice 2.1 already owns:

~~~python
RuntimeWorkspaceAttachment(
    workspace_id,
    root,
    repository,
    source_commit,
)
~~~

Slice 2.4 must derive it from WorkspaceInstanceRef.

No separate workspace attachment model is introduced.

Derivation is pure and exact:

~~~text
attachment.workspace_id == instance.workspace_id
attachment.root         == instance.root
attachment.repository   == instance.repository
attachment.source_commit== instance.source_commit
~~~

Derivation does not invoke runtime.

Attachment existence does not authorize runtime use.

---

# 36. Environment provenance

Conceptual:

~~~python
WorkspaceEnvironmentProvenance(
    provider_ref,
    boundary_class,
    backend_kind,
    platform_key,
    platform_version,
    image_digest: ContentDigest | None,
    environment_digest: ContentDigest,
)
~~~

environment_digest covers an exact provider-defined, secret-free canonical environment record.

It must not contain:

- secrets;
- credential values;
- unnecessary personal/host identifiers.

The exact provider-defined provenance schema/version is part of provider descriptor identity.

If policy requires environment provenance and provider cannot produce it:

INDETERMINATE / STOP.

---

# 37. Initial clean-state requirement

Before execution, provider evidence must establish:

- exact source commit is checked out/materialized;
- no tracked modification exists;
- no unexpected untracked content exists unless exact policy explicitly allows provider-injected files;
- provider-injected files are separately identified and digest-bound;
- repository metadata state is consistent with provider policy.

Conceptual inspection:

~~~python
WorkspaceInspection(
    instance_ref,
    inspected_at,
    head_commit,
    tracked_changes,
    untracked_paths,
    provider_injected_paths,
    protected_asset_observations,
    property_evidence,
)
~~~

Time is evidence metadata, not identity ordering.

---

# 38. Provider-injected files

Some backends may need exact helper/configuration files.

Rules:

- every provider-injected path is declared in the provider/policy contract;
- content is exact/digest-bound;
- injected content cannot alter WorkPacket scope/authority;
- injected content is not source baseline content;
- result extraction distinguishes provider-injected files from engineering changes;
- an undeclared injected file makes initial state nonconforming.

---

# 39. Workspace property evidence

Conceptual:

~~~python
WorkspacePropertyEvidence(
    property_key,
    property,
    established_strength: ControlStrength,
    status: RequirementStatus,
    evidence_digest: ContentDigest,
)
~~~

Rules:

- evidence subject is exact WorkspaceInstanceRef + plan;
- exact key must correspond to policy requirement;
- established_strength must meet or exceed minimum strength;
- SATISFIED without exact evidence is invalid;
- provider capability descriptor cannot stand in for evidence;
- stale/other-instance evidence cannot satisfy current instance.

---

# 40. Control continuity

A control can be valid at provision time and lost later.

CONTROL_CONTINUITY therefore concerns the interval relevant to execution.

Conceptual:

~~~python
WorkspaceControlContinuityEvidence(
    instance_ref,
    plan_ref,
    start_evidence_digest,
    terminal_evidence_digest,
    status,
)
~~~

Schema v1 does not require full-trajectory recording.

It requires enough exact evidence under policy to establish that required controls were not known to be dropped.

If continuity is required but cannot be established:

INDETERMINATE.

A terminal clean result does not prove continuous enforcement.

---

# 41. Dirty-state inspection

After execution, Slice 2.4 must distinguish:

- tracked modified;
- tracked deleted;
- untracked added;
- type/symlink change where provider can establish it;
- provider-injected unchanged files;
- protected-asset change;
- out-of-scope change.

Dirty state is evidence.

Dirty state is not automatically failure: authorized implementation work is expected to create changes.

The exact policy determines whether each changed path is admissible.

---

# 42. WorkspaceChangeManifest

Conceptual:

~~~text
WorkspaceChangeKind:
  ADDED
  MODIFIED
  DELETED
  TYPE_CHANGED
~~~

~~~python
WorkspaceChangeEntry(
    path,
    change_kind,
    before_digest: ContentDigest | None,
    after_digest: ContentDigest | None,
)

WorkspaceChangeManifest(
    instance_ref,
    source_commit,
    entries: tuple[WorkspaceChangeEntry, ...],
    manifest_digest,
)
~~~

Rules:

- canonical by path;
- no duplicate path;
- deleted -> after_digest None;
- added -> before_digest None;
- modified/type-changed -> both expected where provider can establish content identity;
- exact provider-injected paths excluded or explicitly classified;
- manifest does not imply engineering acceptance.

---

# 43. Scope-conformance evaluation

Workspace filesystem scope uses the exact resolved plan.

For each changed path:

- canonicalize path;
- apply deny rules;
- apply protected binding;
- apply writable rule/default;
- classify allowed/forbidden/indeterminate.

Known forbidden change:
UNSATISFIED.

Unverifiable path identity:
INDETERMINATE.

No changed paths outside allowed mutation scope:
eligible for SATISFIED, subject to other controls.

This supports RELAY_SCOPE_CONFORMANCE evidence but does not independently define the broader assurance property.

---

# 44. Protected-asset terminal evaluation

For each protected binding:

- compare exact terminal content/digest where applicable;
- compare effective operation;
- compare separate authority status;
- compare actual mutation observation.

Examples:

READ-only requirement + unchanged:
may satisfy detective evidence.

READ-only requirement + changed:
UNSATISFIED.

MODIFY requirement + correct separate authority + changed:
not automatically accepted; physical permission may be conforming, engineering result still requires evaluation.

MODIFY requirement without separate required authority:
UNSATISFIED.

Unknown terminal asset identity:
INDETERMINATE.

---

# 45. Network/external-effect evidence

For BOUNDARY_ENFORCED network policy, evidence must come from the actual provider boundary mechanism.

Examples:

- container network namespace rule digest;
- exact proxy policy digest;
- remote sandbox network-policy attestation.

Instruction text is not enforcement evidence.

For DETECTIVE network evidence:

- logs may show observed connections;
- absence of logs is only sufficient if policy/provider establishes complete observation.

If observation completeness is unknown:

INDETERMINATE.

---

# 46. Credential evidence

Credential evidence contains only identifiers and exposure state.

Conceptual:

~~~python
WorkspaceCredentialEvidence(
    credential_ref,
    exposure_mode,
    status,
    revoked_or_removed: RequirementStatus | None,
)
~~~

No secret value.

No secret hash.

No environment variable value.

Unexpected exposed credential:
UNSATISFIED.

Required credential unavailable:
INDETERMINATE unless positively incompatible.

---

# 47. Resource evidence

Provider may emit:

~~~python
WorkspaceResourceEvidence(
    memory_limit_bytes,
    disk_limit_bytes,
    process_limit,
    cpu_seconds_limit,
    open_files_limit,
    status,
    evidence_digest,
)
~~~

Values are actual enforced limits, not requested limits.

Requested == actual is not inferred.

A provider descriptor saying "supports cgroups" is not enough.

---

# 48. Teardown evidence

Conceptual:

~~~text
WorkspaceTerminalDisposition:
  DELETED
  RETAINED_BY_POLICY
  RETAINED_PENDING_RELEASE
  TEARDOWN_FAILED
  UNKNOWN
~~~

~~~python
WorkspaceTeardownEvidence(
    instance_ref,
    disposition,
    credential_cleanup_status,
    workspace_absence_status,
    retained_until,
    evidence_digest,
)
~~~

Rules:

- DELETE_ON_TERMINAL requires positive deletion evidence;
- failure to establish deletion -> INDETERMINATE or UNSATISFIED depending observed state;
- RETAINED_BY_POLICY is not failure when exact policy requires it;
- retained workspace cannot be resumed without current external authority;
- teardown result is not Human acceptance.

---

# 49. Cancellation cleanup

Runtime cancellation is Slice 2.1.

Workspace cleanup after cancellation is Slice 2.4.

Cancellation does not automatically imply workspace deletion.

The exact retention policy applies.

Phase 3 may request cancellation then request workspace terminal handling.

Slice 2.4 returns evidence.

It does not decide result acceptance.

---

# 50. WorkspaceConformanceFacts

Conceptual:

~~~python
WorkspaceConformanceFacts(
    evaluated_plan_ref,
    evaluated_instance_ref,
    evaluated_provider_ref,

    work_packet_ref,
    work_packet_conformance_status,

    workspace_policy_status,
    role_contract_status,
    provider_descriptor_status,

    initial_inspection,
    property_evidence,
    protected_asset_evidence,
    credential_evidence,
    resource_evidence,

    terminal_inspection | None,
    change_manifest | None,
    continuity_evidence | None,
    teardown_evidence | None,
)
~~~

Exact subject equality is required.

Facts for another plan/instance/provider cannot satisfy current conformance.

---

# 51. WorkspaceConformance

Use accepted RequirementStatus:

~~~python
WorkspaceConformance(
    status: RequirementStatus,
    reasons: tuple[WorkspaceReason, ...],
    unsatisfied_property_keys: tuple[StableRequirementKey, ...],
    indeterminate_property_keys: tuple[StableRequirementKey, ...],
)
~~~

No AUTHORIZED status exists.

No ACCEPTED status exists.

---

# 52. Conformance aggregation

Normative precedence:

~~~text
known exact violation / incompatible subject / weaker-than-required control
    -> UNSATISFIED

else missing / stale / unavailable / unsupported / unverifiable required evidence
    -> INDETERMINATE

else
    -> SATISFIED
~~~

A later positive fact cannot repair an earlier exact-subject mismatch.

No majority/score/best-effort aggregation.

---

# 53. WorkspaceReason minimum vocabulary

At minimum:

~~~text
WORK_PACKET_REF_MISMATCH
WORK_PACKET_CONFORMANCE_REQUIRED

WORKSPACE_POLICY_REQUIRED
WORKSPACE_POLICY_REF_MISMATCH
WORKSPACE_POLICY_STALE
WORKSPACE_POLICY_CONFLICT

GOVERNANCE_PROFILE_MISMATCH
ROLE_CONTRACT_REF_MISMATCH
ROLE_PERMISSION_INSUFFICIENT

REQUIRED_WORKSPACE_PROPERTY_UNKNOWN
REQUIRED_WORKSPACE_PROPERTY_UNSUPPORTED
REQUIRED_WORKSPACE_PROPERTY_INDETERMINATE
REQUIRED_WORKSPACE_PROPERTY_UNSATISFIED
CONTROL_STRENGTH_INSUFFICIENT

PROVIDER_REF_MISMATCH
PROVIDER_DESCRIPTOR_UNAVAILABLE
PROVIDER_CAPABILITY_INSUFFICIENT
PROVIDER_BOUNDARY_INSUFFICIENT

SOURCE_BASELINE_MISMATCH
INITIAL_STATE_DIRTY
REPOSITORY_METADATA_NOT_ISOLATED

FILESYSTEM_SCOPE_VIOLATION
PATH_ESCAPE_UNCONTROLLED
PROTECTED_ASSET_PERMISSION_REQUIRED
PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED
PROTECTED_ASSET_MUTATED

TOOL_NOT_ALLOWED
SHELL_POLICY_UNSUPPORTED
NETWORK_POLICY_UNSUPPORTED
NETWORK_POLICY_VIOLATION
EXTERNAL_SIDE_EFFECT_POLICY_UNSUPPORTED
EXTERNAL_SIDE_EFFECT_VIOLATION

CREDENTIAL_NOT_DECLARED
CREDENTIAL_EXPOSURE_UNSUPPORTED
UNEXPECTED_CREDENTIAL_EXPOSURE

RESOURCE_LIMIT_UNSUPPORTED
RESOURCE_LIMIT_MISMATCH

ENVIRONMENT_PROVENANCE_INSUFFICIENT
CONTROL_CONTINUITY_INDETERMINATE

CHANGESET_UNAVAILABLE
CHANGE_OUT_OF_SCOPE

RETENTION_POLICY_VIOLATION
TEARDOWN_INDETERMINATE
TEARDOWN_FAILED
~~~

Reason vocabulary is deterministic evidence classification, not authority.

---

# 54. Pre-execution versus terminal conformance

Two explicit evaluation moments are useful:

~~~text
PRE_EXECUTION
TERMINAL
~~~

Pre-execution can evaluate:

- exact plan;
- exact policy;
- provider;
- source baseline;
- clean state;
- required property establishment;
- protected-asset setup;
- network/tool/credential/resource setup;
- environment provenance.

Terminal can additionally evaluate:

- changed paths;
- protected-asset outcome;
- continuity;
- credential cleanup;
- retention/teardown.

Pre-execution SATISFIED does not guarantee terminal SATISFIED.

Terminal SATISFIED does not imply engineering acceptance.

---

# 55. Assurance-property mapping

Slice 2.4 produces evidence usable by the broader accepted assurance model.

It does not redefine those properties.

## RELAY_SCOPE_CONFORMANCE

Relevant evidence:

- exact baseline;
- filesystem policy;
- WorkspaceChangeManifest;
- changed-path evaluation;
- protected asset evaluation.

## RELAY_EXECUTION_PROVENANCE_SUFFICIENT

Relevant evidence:

- exact provider ref;
- environment provenance;
- workspace instance ref;
- exact source commit;
- exact plan ref.

## RELAY_VERIFICATION_ASSETS_PROTECTED

Relevant evidence:

- protected asset bindings;
- physical control strength;
- before/after asset identity;
- mutation-authority facts.

## RELAY_FAIL_CLOSED

Relevant evidence:

- unsupported required property stops preflight;
- unverifiable exact subject remains INDETERMINATE;
- no silent control downgrade.

## RELAY_CONTROL_CONTINUITY_VERIFIED

Relevant evidence:

- pre/terminal control evidence;
- provider continuity evidence where required.

These mappings are evidence relationships only.

They do not self-certify broader assurance.

---

# 56. Backend model

Normative provider interface is provider-neutral.

Schema-v1 backend kinds include:

~~~text
LOCAL_CLONE
LOCAL_WORKTREE
CONTAINER
REMOTE_ISOLATED
OTHER
~~~

No backend kind is inherently trusted.

Exact descriptor + actual evidence determine what it can establish.

---

# 57. Local clone backend

The recommended first concrete provider is a disposable local clone.

Reason:

A disposable clone gives stronger repository isolation than a Git worktree because Git metadata is independent from the canonical checkout.

Minimum provision algorithm:

~~~text
1. require local source repository already available;
2. create fresh temporary workspace root;
3. local git clone with network disabled / no remote fetch;
4. avoid hardlinked source object dependency where implementation permits;
5. checkout exact source commit detached;
6. remove/disable unexpected remote mutation path where policy requires;
7. verify HEAD == exact source commit;
8. verify initial tracked state clean;
9. record exact provider-injected files, if any;
10. return WorkspaceInstanceRef + evidence.
~~~

This provider must never claim a strong same-user host filesystem/network boundary.

---

# 58. Local clone capability ceiling

A schema-v1 local same-user clone may reasonably support:

~~~text
EXACT_SOURCE_BASELINE:
BOUNDARY_ENFORCED relative to repository materialization operation

CLEAN_INITIAL_STATE:
DETECTIVE / positive exact inspection

REPOSITORY_METADATA_ISOLATED:
MEDIATED or stronger relative to separate clone metadata

DIRTY_STATE_INSPECTION:
DETECTIVE

CHANGESET_EXTRACTION:
DETECTIVE

RETENTION_CONTROL:
MEDIATED

TEARDOWN_CONTROL:
MEDIATED
~~~

It must not automatically claim:

~~~text
FILESYSTEM_SCOPE:
BOUNDARY_ENFORCED

PATH_ESCAPE_CONTROL:
BOUNDARY_ENFORCED

PROTECTED_ASSET_CONTROL:
BOUNDARY_ENFORCED

NETWORK_REACHABILITY_CONTROL:
BOUNDARY_ENFORCED

EXTERNAL_SIDE_EFFECT_CONTROL:
BOUNDARY_ENFORCED

CREDENTIAL_EXPOSURE_CONTROL:
BOUNDARY_ENFORCED

RESOURCE_LIMIT_CONTROL:
BOUNDARY_ENFORCED
~~~

unless an additional exact mechanism establishes those controls.

---

# 59. Local worktree backend

A local Git worktree may be useful for development.

However:

- it shares Git common metadata/object infrastructure;
- it is same-user;
- it is not a strong isolation boundary;
- it cannot claim REPOSITORY_METADATA_ISOLATED at strong strength;
- it cannot inherit trust merely from existing repository discipline.

Therefore LOCAL_WORKTREE is a supported provider kind but is not the recommended schema-v1 first provider for governed execution.

---

# 60. Container backend

A future container provider may establish stronger:

- filesystem mount isolation;
- read-only protected assets;
- network namespace/policy;
- resource/cgroup limits;
- credential injection/removal;
- environment/image provenance.

But:

~~~text
container provider name
    != proof controls were applied
~~~

Actual instance evidence remains mandatory.

No Docker/Kubernetes implementation is authorized by this design.

---

# 61. Remote isolated backend

A future remote provider may establish:

- ephemeral isolated filesystem;
- policy-controlled egress;
- secret injection;
- stronger tenant isolation;
- signed/environment attestations.

The provider-neutral contract does not assume any cloud vendor.

Remote attestation remains exact provider evidence, not Relay Human authority.

---

# 62. Workspace policy and provider compatibility

Pure compatibility evaluator:

~~~python
evaluate_workspace_policy_provider_compatibility(
    policy,
    provider_descriptor,
) -> WorkspacePreflight
~~~

Checks:

- every required property advertised;
- provider maximum strength >= required minimum;
- required boundary semantics representable;
- required tool/network/credential/resource modes representable.

Known unsupported:
UNSATISFIED.

Unknown descriptor:
INDETERMINATE.

Compatible:
SATISFIED.

Again:

preflight SATISFIED != actual control enforcement.

---

# 63. Runtime credential separation

Slice 2.3 WorkPacket.credential_refs is reused.

But schema v1 explicitly separates:

~~~text
credential declared for runtime/provider use
from
credential exposed inside workspace
~~~

WorkspacePolicyDefinition selects workspace-visible grants.

A runtime provider credential may be passed to AgentRuntime outside the workspace and never appear in workspace environment/files.

This prevents Slice 2.4 from accidentally turning every runtime credential into agent tool access.

---

# 64. Runtime permission profile separation

RuntimePermissionProfileRef remains Slice 2.1.

WorkspacePolicyDefinition remains Slice 2.4.

Both may constrain tools/permissions through different mechanisms.

Neither silently overrides the other.

Phase 3 later requires compatibility.

A workspace cannot claim tool restriction merely because RuntimePermissionProfileRef exists.

A runtime cannot claim filesystem isolation merely because WorkspacePolicyDefinition exists.

---

# 65. WorkPacket required_workspace_property_keys

WorkPacket required keys are an exact required subset.

Resolution:

~~~text
for every packet.required_workspace_property_key:
    exact matching WorkspacePropertyRequirement must exist
~~~

If key absent:
UNSATISFIED.

If matching requirement exists but provider cannot establish it:
UNSATISFIED or INDETERMINATE according to known capability/evidence.

Additional policy requirements remain mandatory.

No packet can omit a policy-required control merely because its key is absent from the packet tuple.

---

# 66. RoleContract required assurance properties

RoleContract.required_assurance_properties remains external assurance vocabulary.

Slice 2.4 does not duplicate it.

The workspace design may map workspace evidence to relevant assurance-property assessments externally.

If the applicable RoleContract requires an assurance property whose workspace contribution is mandatory but cannot be established, the wider execution gate remains fail-closed.

Phase 3 owns final cross-slice composition.

---

# 67. Role action and workspace mutation

RoleContract allowed_actions/prohibited_actions remains authoritative for role semantics.

Workspace physical write access cannot widen those actions.

Example:

~~~text
workspace path physically writable
+
RoleContract prohibits implementation mutation
=
actor still may not mutate implementation
~~~

The workspace should be provisioned least-privilege so physical capability matches the exact action where possible.

Physical capability is not semantic authority.

---

# 68. Workspace provider errors

Provider operational errors are separate from conformance.

Conceptual taxonomy:

~~~text
WorkspaceProviderErrorCode:
  INVALID_PLAN
  UNSUPPORTED_POLICY
  SOURCE_NOT_AVAILABLE
  SOURCE_COMMIT_NOT_AVAILABLE
  PROVISION_FAILED
  INSPECTION_FAILED
  CHANGESET_FAILED
  TEARDOWN_FAILED
  ENVIRONMENT_ERROR
~~~

Do not misclassify:

~~~text
provider operational failure
as
governance rejection
~~~

Conformance evaluator consumes normalized facts/status.

---

# 69. No persistence requirement in initial implementation

Initial Slice 2.4 implementation does not require a database migration.

Workspace objects are immutable values and provider-returned evidence.

Durable persistence/orchestration is not required to establish the contract.

If implementation later concludes a database migration is required, that is a scope expansion requiring separate design review/authority.

---

# 70. No new Relay lifecycle state

Workspace-local states do not become Project/Slice lifecycle states.

A provider may internally observe:

~~~text
PROVISIONED
ACTIVE
RETAINED
DELETED
FAILED
~~~

but those are workspace/provider observations only.

They do not move Relay Slice lifecycle.

---

# 71. First implementation architecture

If this design is accepted and implementation is separately authorized, the preferred minimum package is:

~~~text
src/relay_engine/execution_workspace/
    __init__.py
    models.py
    evaluation.py
    provider.py
    local_clone.py
~~~

Tests:

~~~text
tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
~~~

The exact implementation scope remains a later Human Authority record.

---

# 72. models.py responsibility

models.py should own pure immutable values only:

- enums;
- policy values;
- provider descriptor/ref;
- plan/ref;
- instance ref;
- inspection/evidence/change manifest;
- conformance facts/result;
- canonical JSON/digest helpers.

No filesystem or subprocess calls.

---

# 73. evaluation.py responsibility

evaluation.py should own pure deterministic functions:

- WorkspacePolicyRef match;
- RoleContract permission checks;
- required property mapping;
- provider-policy preflight;
- plan resolution/conformance;
- path effective-access evaluation;
- change-set scope evaluation;
- workspace conformance aggregation;
- RuntimeWorkspaceAttachment derivation.

No filesystem/network/subprocess calls.

---

# 74. provider.py responsibility

provider.py should define:

- WorkspaceProvider Protocol;
- normalized provider exceptions;
- no concrete side effects.

No global mutable provider registry is required in schema v1.

Provider selection is explicit by exact ref.

---

# 75. local_clone.py responsibility

local_clone.py may implement only the bounded local disposable clone provider.

Allowed operations:

- local filesystem temp directory creation;
- local Git clone/materialization from already available repository;
- exact checkout;
- local Git status/diff/inspection;
- exact change digesting;
- cleanup.

Not allowed as part of initial provider implementation:

- remote fetch/pull;
- push;
- package installation;
- arbitrary agent command execution;
- network access;
- secret retrieval;
- AgentRuntime invocation.

---

# 76. Local provider safety during tests

Integration tests must use disposable temporary repositories/workspaces only.

They must not mutate:

- the developer canonical checkout;
- Relay main refs;
- remote repositories;
- operational DB state.

Tests prove provider mechanics, not real-project execution.

---

# 77. Deterministic model tests

At minimum:

~~~text
WorkspacePolicyDefinition strict/frozen/extra-forbid
WorkspacePolicyRef exact digest match
policy/profile exact binding

canonical property requirement ordering
stable key collision rejection
path canonicalization
path-prefix segment semantics
filesystem deny precedence
protected rule narrowing

canonical tool rule ordering
network endpoint canonicality
credential grant subset rules
integer-only resource limits
retention invariants

ProviderDescriptor exact digest/ref
provider capability canonicality

WorkspacePlan fixed canonical JSON/SHA-256 vectors
plan mutation changes digest
no latest provider/policy resolution

WorkspaceInstance exact source/root/provider/plan binding
WorkspaceChangeManifest canonical entries
~~~

---

# 78. Provider compatibility tests

At minimum:

~~~text
required strength <= provider max
    -> preflight may SATISFY

required strength > provider max
    -> UNSATISFIED

required property missing from provider descriptor
    -> UNSATISFIED

descriptor unavailable/unverifiable
    -> INDETERMINATE

provider advertises capability
but no instance evidence
    -> final conformance INDETERMINATE
~~~

---

# 79. Filesystem negative tests

At minimum:

~~~text
../ escape rejected
absolute path rejected
backslash path rejected
duplicate slash rejected
symlink escape evidence missing -> INDETERMINATE when required
denied prefix write -> UNSATISFIED
read-only path changed -> UNSATISFIED
writable prefix changed -> potentially SATISFIED
out-of-scope path changed -> UNSATISFIED
unknown path identity -> INDETERMINATE
~~~

---

# 80. Protected asset tests

At minimum:

~~~text
RoleContract lacks requested permission
    -> UNSATISFIED

READ requirement + MODIFY physical plan
    -> reject widening

MODIFY requires separate authority + missing
    -> INDETERMINATE/UNSATISFIED per exact fact

READ protected asset changed
    -> UNSATISFIED

protected asset unchanged
    -> detective evidence may SATISFY applicable check

evaluator ACCEPT
without mutation authority
    -> cannot enable MODIFY
~~~

---

# 81. Tool/shell tests

At minimum:

~~~text
denied exact tool -> UNSATISFIED if exposed
unknown tool identity -> INDETERMINATE
shell DENY + shell exposed -> UNSATISFIED
fine-grained shell command allowlist attempted in schema v1 -> invalid model
unmediated shell cannot claim tool-level side-effect prevention
~~~

---

# 82. Network/external-effect tests

At minimum:

~~~text
DENY_ALL + provider no network control
    -> UNSATISFIED when boundary enforcement required

ALLOWLIST + exact supported endpoint policy
    -> preflight may SATISFY

redirect/destination widening not evidenced
    -> INDETERMINATE

network reachability allowed
but mutating external effects denied
and shell unmediated
    -> required effect control not SATISFIED
~~~

---

# 83. Credential tests

At minimum:

~~~text
credential not in WorkPacket
but workspace grant requested
    -> UNSATISFIED

packet credential exists
but policy does not expose it
    -> no workspace exposure

unexpected exposed credential
    -> UNSATISFIED

required exact credential exposure unavailable
    -> INDETERMINATE

secret value appears in model/evidence
    -> impossible by schema / architecture test
~~~

---

# 84. Resource tests

At minimum:

~~~text
required memory limit 1 GiB
provider actual 2 GiB
    -> UNSATISFIED if 1 GiB is maximum

provider says resource capability
but no actual limit evidence
    -> INDETERMINATE

no required resource limit
    -> no synthetic failure
~~~

---

# 85. Local clone integration tests

At minimum use disposable Git repos to prove:

~~~text
exact commit checkout
detached source identity
clean initial state
independent .git metadata from source checkout
untracked change detection
modified file detection
deleted file detection
change manifest digest stability
provider-injected path handling
teardown deletion
retention behavior
source repository remains unchanged
~~~

No network.

No remote.

No agent runtime.

---

# 86. Conformance tri-state tests

At minimum:

~~~text
known wrong provider ref
    -> UNSATISFIED

missing provider evidence
    -> INDETERMINATE

required property positively weaker than policy
    -> UNSATISFIED

required property evidence unavailable
    -> INDETERMINATE

known out-of-scope change
    -> UNSATISFIED

change manifest unavailable
    -> INDETERMINATE

all exact required facts satisfied
    -> SATISFIED
~~~

---

# 87. Non-authority tests

Explicitly prove:

~~~text
WorkspacePolicyDefinition has no authorized field
WorkspacePlan has no authorized field
WorkspaceConformance has no AUTHORIZED state
WorkspaceConformance SATISFIED != execution authority
provider capability != authority
workspace instance != authority
runtime attachment != authority
clean state != authority
RoleContract permission != work authority
credential exposure != authority
network reachability != authority
successful teardown != Human acceptance
~~~

No Slice 2.4 function may issue:

- Human acceptance;
- work authorization;
- implementation authorization;
- execution authorization;
- promotion authorization;
- successor authority.

---

# 88. Architecture tests

Static tests must prove initial Slice 2.4 production package does not import/call:

- persistence DB mutation;
- lifecycle mutation;
- Human control mutation;
- manual evaluation mutation;
- promotion executor;
- AgentRuntime adapter/session invocation;
- network/http clients;
- remote Git fetch/push;
- secret manager SDK;
- cloud/container SDK unless separately authorized for a later concrete provider.

The local clone provider may use local subprocess Git only inside its bounded provider module.

---

# 89. No production wiring in initial implementation

Initial implementation must not wire Slice 2.4 into:

- Phase 3;
- AgentRuntime execution;
- existing Human-control actions;
- lifecycle transitions;
- promotion;
- real WorkPacket execution;
- operational DB;
- board mutation.

It may export stable contract/provider APIs for later Phase 3 consumption.

---

# 90. Design acceptance matrix

A01 exact immutable WorkspacePolicyDefinition identity/digest matches WorkspacePolicyRef:
COVERED by sections 10, 30, 77.

A02 exact immutable WorkspacePlan identity/digest binds WorkPacketRef + baseline + provider:
COVERED by sections 27–30.

A03 plan/conformance cannot create authority:
COVERED by sections 4, 28, 51, 87.

A04 provider capability declaration separate from enforcement evidence:
COVERED by sections 7, 25–26, 39.

A05 source repository/commit/root and clean state:
COVERED by sections 33–38, 57.

A06 deterministic filesystem semantics and path escape:
COVERED by sections 12–14, 43.

A07 protected verification preserves role + separate mutation authority:
COVERED by sections 16–17, 44.

A08 tool/shell controls do not overclaim:
COVERED by sections 18–19.

A09 network/external-effect controls:
COVERED by sections 20–21, 45.

A10 exact credential allowlist; no secret bytes:
COVERED by sections 22, 46, 63.

A11 resource/retention/teardown/cancellation:
COVERED by sections 23–24, 47–49.

A12 environment/security-boundary provenance:
COVERED by sections 6–7, 25, 36.

A13 required workspace property mapping:
COVERED by sections 8–9, 65.

A14 instance/inspection/change manifest exact/content-bound:
COVERED by sections 33, 37, 41–42.

A15 RuntimeWorkspaceAttachment reuse/no invocation:
COVERED by sections 35, 64.

A16 local backend cannot claim stronger controls:
COVERED by sections 57–60.

A17 missing/stale/conflicting/unsupported/unverifiable fail closed:
COVERED by sections 31, 50–53, 86.

A18 no DB/orchestration/runtime/Phase3 leakage:
COVERED by sections 5, 69–75, 88–89.

---

# 91. Explicitly out of scope

This design does not authorize or implement:

- Phase 3 orchestration;
- actor/execution authority selection;
- AgentRuntime invocation;
- LLM/provider/model calls;
- real-project agent execution;
- production WorkPacket execution;
- generic secret storage;
- cloud credential brokering;
- generic IAM/RBAC;
- generic shell parsing;
- generic network proxy;
- generic container orchestration;
- Kubernetes;
- Docker integration;
- remote sandbox integration;
- database persistence;
- lifecycle changes;
- promotion;
- acceptance;
- new GovernanceProfile engine;
- new RoleContract semantics;
- new WorkPacket semantics.

---

# 92. Implementation stop rules

If later implementation discovers any of the following are necessary, STOP and return to design/authority:

- modifying accepted Slice 2.1 models;
- modifying accepted Slice 2.2 models;
- modifying accepted Slice 2.3 models;
- adding a database migration;
- adding a production runtime call;
- adding a cloud/container dependency;
- introducing a general command parser;
- introducing secret bytes into Relay models;
- adding a new authority state;
- weakening a required control because the local backend cannot enforce it.

---

# 93. Design disposition

~~~text
Slice 2.4:
OPEN

Design Revision 1:
COMPLETE CANDIDATE

Design authority:
RLY-S24-DESIGN-AUTH-001 — AUTHORIZED

Design acceptance:
PENDING INDEPENDENT REVIEW

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
~~~

# 94. Next gate

The exact next gate is:

~~~text
SOL independent Slice 2.4 design review
~~~

The independent evaluator must return:

~~~text
ACCEPT
REWORK
ESCALATE
~~~

No implementation authority may be inferred from design completion.

**Design candidate != design acceptance. Design acceptance != implementation authority.**
