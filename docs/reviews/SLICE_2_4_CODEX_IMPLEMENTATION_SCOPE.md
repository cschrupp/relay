# Relay — Slice 2.4 Execution Workspace Authority — Codex Implementation Scope

**Document class:** Prepared implementation handoff / scope  
**Status:** IMPLEMENTATION SCOPE — HUMAN DESIGN ACCEPTED / IMPLEMENTATION NOT AUTHORIZED  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Record:** `RLY-S24-CODEX-SCOPE-001`

## 1. Governance status

```text
Slice opening:
RLY-S24-OPEN-001 — OPEN
4a2a97b706c976d5d57680aadb3cdb8faa4474e9

Design authorization:
RLY-S24-DESIGN-AUTH-001 — AUTHORIZED
7e96c34d97729daadc3606d6809d95f9e3145e51

Revision 1:
913d65841fecb4cf8ed172531b4d22e9c45f92cc

Revision 2:
3671e6ca7470f0b74c49ffa856e60474f22a5a92

Revision 3:
5370888cf9a8704d00f6b3beafa25f0becec86f8

Revision 4:
67af9f5e149cd9bf2f1bb620f79d510935eff1b0

Revision 5:
910449b2c984f7f2d14281f573e46fc46ebce399

Independent design evaluation:
RLY-S24-DESIGN-EVAL-005 — ACCEPT
f4aaf4cd0590af7c7aeaddb9f01f15ede5dac46a

Human design acceptance:
RLY-S24-DESIGN-ACCEPT-001 — ACCEPTED
103e27bb48e775f42601dea45822c34896feb730
```

Revisions 2–5 are normative over earlier revisions only where they explicitly differ.

All findings F001–F012 are closed.

All A01–A18 design criteria pass.

The two binding implementation clarifications from `RLY-S24-DESIGN-EVAL-005` are mandatory:

```text
C01 WorkspacePlan stable identity:
(work_packet_ref, plan_key, revision)
same stable identity + different digest -> conflict / fail closed

C02 provider property capabilities:
unique by WorkspaceProperty
canonical in WorkspaceProperty enum order
duplicates/conflicting maximum_strength -> invalid descriptor
```

If this scope conflicts with the accepted combined design or IR5, STOP and report the conflict. Do not reinterpret the design.

---

## 2. Executor and objective

Planned executor:

```text
Codex / Luna implementation environment
```

Objective:

Implement the minimum Slice 2.4 contract package plus one bounded **local disposable-clone provider**.

The candidate must realize:

- immutable WorkspacePolicyDefinition identity/digest;
- immutable WorkspaceProviderDescriptor / WorkspaceProviderRef identity;
- immutable WorkspacePlan / WorkspacePlanRef identity;
- exact WorkPacket/RoleContract/policy/profile/provider plan resolution;
- complete WorkPacket-subset + policy-property transport into WorkspacePlan;
- deterministic provider-policy preflight;
- deterministic path/filesystem access evaluation;
- exact protected-verification binding and conformance derivation;
- exact credential/resource/environment/property evidence models;
- exact WorkspaceInstanceRef / WorkspaceInspection models;
- exact WorkspaceChangeManifest / ref/digest;
- exact pre-execution and terminal WorkspaceConformance;
- exact RuntimeWorkspaceAttachment derivation;
- provider-neutral WorkspaceProvider Protocol;
- one bounded local disposable-clone implementation;
- deterministic architecture/negative/integration tests.

This is **workspace contract implementation and local-provider mechanics**.

It is not production orchestration or real-project execution.

---

## 3. Governing design precedence

Codex must read in this order:

1. `docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY.md`
2. `docs/reviews/SLICE_2_4_OPENING.md`
3. `docs/reviews/SLICE_2_4_DESIGN_AUTHORIZATION.md`
4. `docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN.md`
5. `docs/reviews/SLICE_2_4_DESIGN_EVALUATION_001.md`
6. `docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV2_AMENDMENT.md`
7. `docs/reviews/SLICE_2_4_DESIGN_EVALUATION_002.md`
8. `docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV3_AMENDMENT.md`
9. `docs/reviews/SLICE_2_4_DESIGN_EVALUATION_003.md`
10. `docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV4_AMENDMENT.md`
11. `docs/reviews/SLICE_2_4_DESIGN_EVALUATION_004.md`
12. `docs/slices/SLICE_2_4_EXECUTION_WORKSPACE_AUTHORITY_DESIGN_REV5_AMENDMENT.md`
13. `docs/reviews/SLICE_2_4_DESIGN_EVALUATION_005.md`
14. `docs/reviews/SLICE_2_4_DESIGN_ACCEPTANCE.md`
15. this scope record.

Earlier REWORK evaluations remain immutable evidence of defects later revisions close.

---

## 4. Planned implementation branch and baseline

Planned implementation branch:

`implementation/2.4-execution-workspace-authority`

The later implementation authorization must pin the exact baseline to the commit containing this scope record.

The implementation branch must start from that exact authorized baseline.

After authorization:

- verify local/remote implementation branch HEAD equals the exact authorized baseline before edits;
- do not merge/rebase later `main`;
- do not rewrite design history;
- do not cherry-pick unrelated work;
- do not widen the file surface.

---

## 5. Exact planned file surface

Expected NEW production files only:

```text
src/relay_engine/execution_workspace/__init__.py
src/relay_engine/execution_workspace/models.py
src/relay_engine/execution_workspace/evaluation.py
src/relay_engine/execution_workspace/provider.py
src/relay_engine/execution_workspace/local_clone.py
```

Expected NEW tests only:

```text
tests/unit/test_execution_workspace_models.py
tests/unit/test_execution_workspace_evaluation.py
tests/unit/test_execution_workspace_provider_contract.py
tests/integration/test_local_clone_workspace_provider.py
tests/unit/test_execution_workspace_architecture.py
```

Expected existing production files modified:

```text
NONE
```

Expected dependency / lock changes:

```text
NONE
```

If implementation requires any other file, STOP before editing it.

---

## 6. Existing contracts to reuse unchanged

Reuse accepted Relay types rather than introducing competitors.

### Work packets / Slice 2.3

At minimum reuse:

```text
WorkPacket
WorkPacketRef
WorkPacketConformance
WorkPacketReason
SourceBaselineRef
PolicyBasisRef
GovernanceProfileRef
WorkspacePolicyRef
AuthorityBasisRef
ProtectedVerificationRequirement
ProtectedVerificationRequirementRef
ProtectedVerificationAuthorityFact
StableRequirementKey
```

### Role contracts / Slice 2.2

At minimum reuse:

```text
RequirementStatus
RoleContract
RoleContractRef
VerificationAssetPermission
```

### Agent runtime / Slice 2.1

At minimum reuse:

```text
CredentialRef
RuntimeIdentifier
RuntimeWorkspaceAttachment
```

### Domain

Reuse existing exact Relay primitives including:

```text
Artifact
CommitRef
ContentDigest
RepositoryRef
```

Do not modify accepted Slice 2.1 / 2.2 / 2.3 models to make Slice 2.4 easier.

Use package-local subject-binding wrappers where accepted design requires them.

---

## 7. models.py responsibility

`models.py` owns strict immutable schema-v1 values and canonical/digest helpers.

Implement the accepted exact concepts, including:

```text
ControlStrength
WorkspaceProperty
WorkspacePropertyRequirement

FilesystemAccess
FilesystemPolicy
RepositoryMetadataAccess
RepositoryMetadataPolicy

ToolDecision
WorkspaceToolRef
ToolRule
ToolPolicy

ShellMode
ShellPolicy

NetworkMode
NetworkEndpoint
NetworkPolicy

ExternalSideEffectMode
ExternalEffectRef
ExternalSideEffectPolicy

CredentialExposureMode
WorkspaceCredentialGrant
WorkspaceCredentialPolicy

WorkspaceResourceDimension
WorkspaceResourceLimits

WorkspaceRetentionMode
WorkspaceRetentionPolicy

WorkspaceBackendKind
WorkspaceBoundaryClass
WorkspacePathControlCapability

WorkspaceProviderPropertyCapability
ProviderInjectedFileCapability
WorkspaceProviderDescriptor
WorkspaceProviderRef

ProviderInjectedFileRequirement

WorkspacePolicyDefinition

ProtectedAssetWorkspaceBinding
ProtectedAssetObservation

WorkspacePlan
WorkspacePlanRef
WorkspacePlanResolution

WorkspaceEvidenceSubject
WorkspacePropertyEvidence
WorkspaceCredentialEvidence
WorkspaceResourceEvidence
WorkspaceEnvironmentProvenance
WorkspaceControlContinuityEvidence

WorkspaceInstanceRef
WorkspaceInspection

WorkspaceEntryKind
WorkspaceEntryState
WorkspaceChangeEntry
WorkspaceChangeManifest
WorkspaceChangeManifestRef

WorkspaceTerminalDisposition
WorkspaceTeardownEvidence

WorkPacketConformanceFact
WorkspacePolicyFact
RoleContractFact
WorkspaceProviderDescriptorFact

WorkspacePreflight
WorkspaceConformanceFacts
WorkspaceConformance
WorkspaceReason
```

Exact names may vary only where Python typing requires a mechanically equivalent representation. Semantics may not vary.

Use existing Relay `DomainModel` behavior:

```text
frozen
strict
extra forbid
validate defaults
```

No side effects in `models.py`.

---

## 8. Canonical identity requirements

Implement pure canonical JSON / SHA-256 helpers for all accepted content-addressed values.

At minimum:

```text
WorkspacePolicyDefinition
WorkspaceProviderDescriptor
WorkspacePlan
WorkspaceChangeManifest
```

Provide exact ref-match helpers.

Canonical JSON:

```text
UTF-8
sort_keys=True
separators=(",", ":")
ensure_ascii=False
allow_nan=False
no normative floats
```

Every order-non-semantic collection must enforce its frozen canonical order before digesting.

Do not silently sort invalid input.

Stable-key collision with conflicting normative content:
reject.

Freeze literal canonical JSON + SHA-256 vectors required by the accepted design.

---

## 9. WorkspacePolicyDefinition implementation

Implement the complete accepted schema:

```text
policy key
policy basis ref
optional governance profile ref
complete property requirements

filesystem policy
repository metadata policy
tool policy
shell policy
network policy
external side-effect policy
credential policy
resource limits
retention policy
provider-injected-file requirements
```

No:

- opaque extension bag;
- WorkspaceProviderRequirements;
- default/implicit policy;
- latest/current policy lookup.

`WorkspacePolicyRef` must match exact canonical policy digest.

A WorkPacket with `workspace_policy_ref is None` cannot resolve a WorkspacePlan:

```text
WORKSPACE_POLICY_REQUIRED
UNSATISFIED
```

---

## 10. WorkspacePlan implementation

Implement the final accepted self-contained plan.

It must carry:

```text
plan_key: StableRequirementKey
revision: int >= 1

exact WorkPacketRef
exact SourceBaselineRef
exact RoleContractRef
exact WorkspacePolicyRef
exact optional GovernanceProfileRef
exact WorkspaceProviderRef

packet_required_property_keys
complete property_requirements

protected_asset_bindings
workspace_credential_grants
provider_injected_files

filesystem policy
repository metadata policy
tool policy
shell policy
network policy
external side-effect policy
resource limits
retention policy
```

Freeze C01:

```text
stable plan identity:
(work_packet_ref, plan_key, revision)

same stable identity + different digest
    -> identity conflict / fail closed
```

No latest/max revision selection.

Plan digest includes every normative field.

---

## 11. Plan resolution

`evaluation.py` must provide a pure deterministic plan resolver.

Inputs must include exact already-materialized:

```text
WorkPacket
WorkPacketRef
WorkPacketConformanceFact
WorkspacePolicyDefinition
RoleContract
protected authority facts
WorkspaceProviderDescriptor
```

Required sequence:

```text
exact packet ref
exact packet conformance subject/status
workspace policy ref present
exact policy digest match
exact policy/profile binding
exact RoleContract binding

validate packet required property keys
copy packet subset trace
copy complete policy property requirements

validate exact protected semantic permissions
validate protected authority facts only for non-None requirements

validate exact provider descriptor/ref
provider property strength compatibility
semantic mode/dimension compatibility
provider-injected-file key/digest compatibility
credential subset compatibility

produce plan only on SATISFIED
```

No partially resolved plan escapes.

Plan resolution SATISFIED != execution authority.

---

## 12. Provider descriptor implementation

Implement exact provider descriptor semantics.

Freeze C02:

```text
property_capabilities:
unique by WorkspaceProperty
WorkspaceProperty enum declaration order
duplicate property invalid
same property + differing max strength invalid
```

Implement exact finite capability collections for:

- shell modes;
- network modes;
- external-side-effect modes;
- credential exposure modes;
- resource dimensions;
- repository metadata modes;
- path-control capabilities;
- provider-injected-file capabilities.

No arbitrary string capability bag.

Descriptor capability != instance enforcement evidence.

---

## 13. Provider preflight

Implement pure:

```python
evaluate_workspace_preflight(
    plan,
    provider_descriptor,
) -> WorkspacePreflight
```

It must use the self-contained plan only.

It must iterate all:

```text
plan.property_requirements
```

including policy-added requirements not named by the WorkPacket.

For each:

```text
provider property capability present
maximum_strength >= minimum_strength
```

and all exact semantic modes/dimensions must be representable.

Known incompatibility:
UNSATISFIED.

Unavailable/stale/unverifiable exact descriptor:
INDETERMINATE.

Compatibility:
SATISFIED preflight only.

Preflight SATISFIED != actual enforcement and != execution authority.

---

## 14. Protected verification implementation

Do not create a standalone `ProtectedAssetEvidence`.

Implement deterministic protected conformance from:

```text
ProtectedAssetWorkspaceBinding
ProtectedVerificationAuthorityFact where applicable
ProtectedAssetObservation
WorkspacePropertyRequirement(PROTECTED_ASSET_CONTROL)
WorkspacePropertyEvidence
WorkspaceChangeManifest where applicable
```

Semantic `VerificationAssetPermission` is non-ordinal.

Physical access is separate.

Never infer:

```text
READ_WRITE filesystem -> semantic MODIFY
EVALUATE -> MODIFY
MODIFY -> APPROVE_MUTATION
```

For `separate_authority_ref is None`:

```text
no authority fact expected
no authority fact consumed
prerequisite NOT_APPLICABLE
```

For non-None authority requirements, exact facts only.

---

## 15. Filesystem/path implementation

Implement exact repository-relative POSIX path validation.

Freeze:

- no absolute paths;
- no backslashes;
- no empty/"."/".." segments;
- no repeated slash;
- case preserved;
- segment-aware prefix matching;
- DENY precedence;
- protected rule can only narrow ordinary filesystem access.

Do not claim OS-level prevention from pure path evaluation.

Provider enforcement strength remains separately evidenced.

---

## 16. Property evidence / final conformance

Implement exact subject-bound property evidence against:

```text
plan.property_requirements
```

Expected population semantics:

```text
missing expected item:
INDETERMINATE

unexpected property key:
UNSATISFIED

duplicate key:
UNSATISFIED

reordered evidence:
UNSATISFIED

correct key + wrong WorkspaceProperty:
UNSATISFIED

established strength below minimum:
UNSATISFIED
```

Wrong plan/instance/provider subject:
UNSATISFIED.

Final aggregation precedence:

```text
known violation/mismatch
    -> UNSATISFIED

else missing/unavailable/unverifiable required fact
    -> INDETERMINATE

else
    -> SATISFIED
```

No scoring/majority/best effort.

WorkspaceConformance has no AUTHORIZED state.

---

## 17. Workspace change implementation

Implement exact:

```text
WorkspaceEntryKind
WorkspaceEntryState
WorkspaceChangeEntry
WorkspaceChangeManifest
WorkspaceChangeManifestRef
```

Schema v1 exact entry kinds:

```text
REGULAR_FILE
SYMLINK
```

Unsupported node kinds fail closed.

Represent exact:

- additions;
- deletions;
- regular/symlink type changes;
- executable-bit changes;
- content digests;
- raw symlink-target digests.

Manifest ref digest must be independently recomputable.

No self-referential digest field.

---

## 18. WorkspaceProvider Protocol

`provider.py` defines only:

- `WorkspaceProvider` Protocol;
- provider operation result/error values required by accepted design;
- no concrete provisioning logic.

Protocol:

```text
describe
provision(plan)
inspect(instance_ref)
extract_changes(instance_ref)
teardown(instance_ref)
```

Protocol existence != authorization to invoke it.

No global mutable provider registry.

---

## 19. local_clone.py bounded provider

Implement exactly one concrete provider:

```text
LOCAL_CLONE
SAME_USER_NO_SECURITY_BOUNDARY
```

It is a development/dogfood evidence provider, not a production security sandbox.

Allowed local mechanics:

- create disposable local temporary workspace root;
- clone from an already available local source repository;
- force independent object storage / no shared hardlink dependency;
- no Git alternates;
- checkout exact source commit detached;
- inspect HEAD/status;
- compute exact file/symlink states;
- materialize exact provider-owned injected files from provider-version-owned keyed bytes;
- compute change manifest;
- cleanup/retain according to exact policy.

Forbidden:

- remote fetch;
- pull;
- push;
- network;
- package installation;
- arbitrary agent command execution;
- secret retrieval;
- AgentRuntime invocation;
- mutation of canonical source repository.

The provider must verify:

```text
exact source commit
clean initial state
no alternates/shared object dependency
source repository unchanged
exact injected-file path/digest
```

The plain provider must not advertise BOUNDARY_ENFORCED generic filesystem/network/credential/resource controls.

---

## 20. Local-provider injected materials

Any provider-owned helper bytes must be static/deterministic assets owned by the exact local provider implementation/version.

The provider descriptor exposes:

```text
provider_file_key
content_digest
```

The plan exposes:

```text
path
provider_file_key
content_digest
```

Provision must:

- resolve the exact local keyed material;
- write exact bytes;
- verify digest;
- report injected path in initial inspection.

Do not add a file store/resolver.

Do not fetch injected material.

---

## 21. RuntimeWorkspaceAttachment derivation

Implement a pure exact helper from `WorkspaceInstanceRef` to accepted Slice 2.1:

```text
RuntimeWorkspaceAttachment
```

Exact equality:

```text
workspace_id
root
repository
source_commit
```

No AgentRuntime invocation.

Attachment existence != execution authority.

---

## 22. Architecture tests

The architecture tests must prove the Slice 2.4 package does not import/call:

- persistence mutation;
- lifecycle mutation;
- Human control mutation;
- manual evaluation mutation;
- promotion;
- AgentRuntime invocation/adapters;
- network/http clients;
- remote Git operations;
- secret manager SDK;
- cloud/container SDK;
- policy resolver/store;
- WorkspacePolicyDefinition lookup after plan resolution.

`local_clone.py` may use local subprocess Git only for its bounded local provider.

No network-facing library is needed.

---

## 23. Integration-test safety

`tests/integration/test_local_clone_workspace_provider.py` must use only disposable temporary Git repositories and temporary workspace roots created by the test.

It must not mutate:

- the current Relay checkout;
- canonical Git refs;
- user repositories;
- remote repositories;
- operational DB state.

No network.

No credentials.

No real agent execution.

---

## 24. Required test coverage

At minimum cover the accepted tests from Revisions 1–5, including:

- policy/plan/provider fixed canonical JSON/SHA-256 vectors;
- all canonical-order/duplicate/conflict rejection;
- WorkspacePlan C01 identity conflict;
- provider C02 property-capability uniqueness;
- packet subset vs policy-added property requirements;
- provider strength compatibility;
- unsupported semantic modes/dimensions;
- path escape/prefix rules;
- non-ordinal protected permissions;
- no-authority protected-fact case;
- exact protected observations/mutation;
- provider-injected-file capability/plan/inspection;
- credential subset/exposure rules;
- network/effect policy invariants;
- WorkspaceChangeManifest exact state transitions;
- property evidence population tri-state;
- RuntimeWorkspaceAttachment derivation;
- local-clone exact commit/clean state/independent object storage/source unchanged;
- teardown/retention;
- non-authority tests.

Do not weaken or skip a frozen design test because the local provider cannot satisfy the corresponding strong policy. The expected result may be fail-closed.

---

## 25. Exact forbidden implementation changes

Do not modify:

```text
src/relay_engine/domain/**
src/relay_engine/governance/**
src/relay_engine/role_contracts/**
src/relay_engine/agent_runtime/**
src/relay_engine/work_packets/**
src/relay_engine/persistence/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/promotion/**
src/relay_engine/repository_sync/**
src/relay_engine/integrations/**
pyproject.toml
uv.lock
.github/workflows/**
.relay/registry.json
docs/**
```

Do not add a dependency.

Do not add a DB migration.

Do not add production wiring.

If any accepted requirement appears impossible inside the ten-file surface, STOP and report the exact conflict.

---

## 26. Required validation

Codex must run:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_execution_workspace_models.py
uv run pytest tests/unit/test_execution_workspace_evaluation.py
uv run pytest tests/unit/test_execution_workspace_provider_contract.py
uv run pytest tests/integration/test_local_clone_workspace_provider.py
uv run pytest tests/unit/test_execution_workspace_architecture.py

uv run ruff format --check .
uv run ruff check .
uv run pyright

uv run pytest tests/unit/test_repository_contract.py
uv run pytest

uv build
git diff --check
```

Exact-head GitHub Actions must be allowed to run on the pushed implementation candidate.

Tests/CI are evidence only.

---

## 27. Candidate discipline

After separate implementation authorization, Codex must:

- begin from the exact authorized scope baseline;
- create only the ten authorized files;
- create a coherent implementation candidate;
- use branch `implementation/2.4-execution-workspace-authority`;
- push only that branch;
- verify remote candidate SHA;
- report changed-file list and validation evidence;
- report zero network/provider/model/AgentRuntime calls;
- report that integration tests used disposable local repositories only;
- STOP for SOL independent implementation review.

Do not self-evaluate or self-accept.

---

## 28. Explicitly out of implementation scope

Not authorized by this scope:

- production workspace provisioning;
- real-project workspace creation;
- production WorkPacket wiring;
- operational DB/persistence;
- lifecycle mutation;
- Human authority creation/validation;
- secret retrieval;
- real credential exposure;
- network access;
- remote Git operations;
- Docker/Kubernetes/cloud provider implementation;
- remote isolated provider implementation;
- AgentRuntime/provider/model calls;
- prompt rendering/execution;
- Phase 3 orchestration;
- real-project agent execution;
- canonical/main promotion.

---

## 29. Governance disposition

```text
RLY-S24-CODEX-SCOPE-001 — PREPARED

Human design acceptance:
RLY-S24-DESIGN-ACCEPT-001 — ACCEPTED

Implementation scope:
PREPARED / EXACT

Implementation authorization:
NOT YET GRANTED

Planned implementation branch:
implementation/2.4-execution-workspace-authority

Production workspace provisioning:
NOT AUTHORIZED

AgentRuntime invocation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

The next legitimate gate is a separate Human implementation authorization that pins the exact commit containing this scope.

**Prepared scope != implementation authority.**
