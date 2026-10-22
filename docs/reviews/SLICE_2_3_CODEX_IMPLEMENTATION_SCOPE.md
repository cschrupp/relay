# Relay — Slice 2.3 Context / Work-Packet Contract — Codex Implementation Scope

**Document class:** Prepared implementation handoff / scope  
**Status:** IMPLEMENTATION SCOPE — HUMAN DESIGN ACCEPTED  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Record:** `RLY-S23-CODEX-SCOPE-001`

## 1. Governance status

```text
Slice opening:
RLY-S23-OPEN-001 — OPEN
bddc6a25ab31cfe7395b07135d7f05f5ac3c8e0f

Original design authority:
RLY-S23-DESIGN-AUTH-001 — AUTHORIZED
4bc054af24bbd19130d7474bab75433b056ef9e4

Revision 1:
8e3cb2df658711cd3e18d364cf19fa5332b2ab2f
blob d11529c5fdf068a142e79171642cdb735dc290cd

Independent design evaluation 1:
RLY-S23-DESIGN-EVAL-001 — REWORK
f0383fe624e99134586198cfcb9be77aae2fb014

Revision 2 rework authority:
RLY-S23-DESIGN-REWORK-AUTH-001 — AUTHORIZED
ff37525222215f2a64c833d77c5d2a8779ac7509

Revision 2 amendment:
699664be71e320e053127d7d7c7b2226911fe401
blob c781a3de90cfd54156f3cce6009ac4baa46ce6af

Independent design evaluation 2:
RLY-S23-DESIGN-EVAL-002 — ACCEPT
af163408b33d3b8fe3fe340aaa36b2be94c76c94

Human design acceptance:
RLY-S23-DESIGN-ACCEPT-001 — ACCEPTED
852da5033a51adfc1a9dde9383ffecdd81ac552c
```

Revision 2 is normative over Revision 1 where they differ.

The two implementation clarifications from `RLY-S23-DESIGN-EVAL-002` are binding:

```text
same canonical stable identity / sort key
+ conflicting normative content
    -> reject
    -> never create arbitrary tie ordering

CapturedMaterialRef resolver_key + resolver_version
    -> immutable external materialization-contract identity
    -> unresolved semantics = INDETERMINATE
```

If this scope conflicts semantically with the accepted design/evaluations, STOP and report the conflict. Do not reinterpret the accepted design.

---

## 2. Executor and objective

Planned executor:

```text
Codex / Luna implementation environment
```

Objective:

Implement the minimum **pure-domain** Slice 2.3 package that realizes the Human-accepted WorkPacket / ContextManifest contract.

The candidate must provide deterministic immutable models and pure evaluators for:

- WorkPacket identity / revision / digest;
- ContextManifest identity / revision / digest;
- canonical SourceBaselineRef derivation from existing Relay Baseline;
- provider-neutral NormalizedEngineeringIntent;
- exact planning source / adapter provenance values;
- exact context source/material references;
- exact materialization facts;
- exact subject-bound conformance facts;
- exact RoleContract applicability transport;
- explicit evidence / deliverable / hard-stop contracts;
- declarative runtime requirements;
- declarative workspace requirements;
- protected-verification requirement/authority transport;
- control-plane mirror exact-match checks;
- WorkPacket / ContextManifest identity-conflict detection;
- deterministic context conformance;
- deterministic WorkPacket conformance.

This is **contract implementation**, not orchestration or production wiring.

---

## 3. Governing design precedence

Codex must read in this order:

1. `docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT.md`
2. `docs/reviews/SLICE_2_3_OPENING.md`
3. `docs/reviews/SLICE_2_3_DESIGN_AUTHORIZATION.md`
4. `docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN.md`
5. `docs/reviews/SLICE_2_3_DESIGN_EVALUATION_001.md`
6. `docs/reviews/SLICE_2_3_DESIGN_REWORK_AUTHORIZATION_001.md`
7. `docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN_REV2_AMENDMENT.md`
8. `docs/reviews/SLICE_2_3_DESIGN_EVALUATION_002.md`
9. `docs/reviews/SLICE_2_3_DESIGN_ACCEPTANCE.md`
10. this scope record.

Evaluation 001 remains immutable evidence of the defects Revision 2 closes.

Evaluation 002 plus Human acceptance establish the accepted combined design.

---

## 4. Planned implementation branch and baseline

Implementation branch:

`implementation/2.3-context-work-packet-contract`

The implementation authority must pin the exact baseline to this scope commit.

The implementation branch must start from that exact baseline.

After authorization:

- verify local/remote implementation branch HEAD equals exact authorized baseline before edits;
- do not merge/rebase later `main`;
- do not rewrite design history;
- do not bring unrelated changes into the implementation branch.

---

## 5. Exact authorized file surface

Expected NEW production files only:

```text
src/relay_engine/work_packets/__init__.py
src/relay_engine/work_packets/models.py
src/relay_engine/work_packets/evaluation.py
```

Expected NEW tests only:

```text
tests/unit/test_work_packet_models.py
tests/unit/test_work_packet_evaluation.py
tests/unit/test_work_packet_architecture.py
```

Expected existing production files modified:

```text
NONE
```

Expected dependency / lock changes:

```text
NONE
```

If Codex concludes that any existing production file, database schema, migration, registry format, dependency, CI workflow, or persistence layer must change, STOP before editing it.

In particular, do not modify:

```text
src/relay_engine/domain/**
src/relay_engine/governance/**
src/relay_engine/role_contracts/**
src/relay_engine/agent_runtime/**
src/relay_engine/persistence/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/repository_sync/**
pyproject.toml
uv.lock
.github/workflows/**
.relay/registry.json
```

No new UUID prefix is authorized.

---

## 6. Existing primitives to reuse

Reuse existing Relay public values.

### Domain

```python
from relay_engine.domain import (
    AcceptanceCriterion,
    Artifact,
    ArtifactId,
    Baseline,
    BaselineId,
    CommitRef,
    ContentDigest,
    DecisionId,
    ProjectId,
    RepositoryRef,
    ScopeSpec,
    SliceId,
)
```

### Role Contracts

```python
from relay_engine.role_contracts import (
    RequirementStatus,
    RoleApplicabilityEvaluation,
    RoleContractApplicability,
    RoleContractRef,
    RoleInputRequirement,
    RoleOutputRequirement,
    VerificationAssetPermission,
)
```

### Runtime declarations

```python
from relay_engine.agent_runtime import (
    CredentialRef,
    RuntimeCapability,
    RuntimeExecutionLimits,
    RuntimePermissionProfileRef,
    RuntimeSelection,
)
```

Use Relay `DomainModel` semantics for stable serialized values:

```text
frozen=True
extra="forbid"
strict=True
validate_default=True
schema_version=1
```

Do not introduce competing ProjectId, SliceId, BaselineId, ArtifactId, ContentDigest, RepositoryRef, CommitRef, RoleContractRef, RuntimeCapability, CredentialRef, or RuntimeSelection types.

---

## 7. Package-local stable keys

Define bounded local string types/validators in `work_packets.models` for the Slice 2.3 concepts.

At minimum:

```text
WorkPacketKey
ContextManifestKey
ContextEntryKey
StableRequirementKey
StableContextSourceKey
StableResolverKey
```

Use a single mechanically consistent rule:

```text
lowercase
starts with ASCII letter
letters/digits
optional hyphen-separated segments
bounded length <= 64
no whitespace
```

Do not modify domain/governance modules merely to share a key helper.

Other non-key textual identity fields such as `material_key` / `material_version` may be bounded opaque nonblank strings when the design intentionally does not impose Relay-key syntax.

---

# 8. Stable enums / vocabularies

Implement exact stable values.

## AuthorityReferenceType

```text
SLICE_AUTHORIZATION_GRANT
REPOSITORY_MUTATION_AUTHORIZATION
HUMAN_GOVERNANCE_RECORD
```

## ContextClass

```text
STATIC
DYNAMIC
```

## ContextSourceKind

```text
RELAY_ARTIFACT
GOVERNANCE_RECORD
REPOSITORY_CONTENT
TOOL_DEFINITION
SKILL
RETRIEVAL_RESULT
RUNTIME_OBSERVATION
EXTERNAL_REFERENCE
SESSION_EXCERPT
```

## NormalizationStatus

```text
COMPLETE
INCOMPLETE
INDETERMINATE
```

## NormalizationIssueCode

At minimum:

```text
MISSING_REQUIRED_FIELD
AMBIGUOUS_FIELD
CONFLICTING_FIELD
UNSUPPORTED_SEMANTIC
SOURCE_UNVERIFIABLE
```

## Material kind discriminator

Exactly:

```text
RELAY_ARTIFACT
REPOSITORY_CONTENT
CAPTURED_MATERIAL
```

## ControlMirrorKind

```text
AUTHORITY_BASIS
ROLE_CONTRACT
POLICY_BASIS
GOVERNANCE_PROFILE
ACCEPTED_DESIGN
SLICE_DEFINITION
SOURCE_BASELINE
```

Do not add execution/lifecycle/authorization success enums.

---

# 9. Exact reference models

Implement immutable models equivalent to the accepted design.

## SliceDefinitionRef

```python
SliceDefinitionRef(
    slice_id: SliceId,
    definition_revision: int >= 1,
    content_digest: ContentDigest,
)
```

No latest/current resolver.

## SourceBaselineRef

```python
SourceBaselineRef(
    baseline_id: BaselineId,
    project_id: ProjectId,
    commit: CommitRef,
    content_digest: ContentDigest,
)
```

`content_digest` is the canonical digest of the exact existing `Baseline` object under Slice 2.3 canonical Baseline rules.

## AuthorityBasisRef

```python
AuthorityBasisRef(
    authority_type: AuthorityReferenceType,
    authority_key: StableRequirementKey,
    record_digest: ContentDigest,
    subject_digest: ContentDigest | None,
)
```

This is a reference only.

It must never create or validate Human root authority.

## PolicyBasisRef

Implement the accepted conceptual exact ref:

```python
PolicyBasisRef(
    policy_key: StableRequirementKey,
    policy_version: int >= 1,
    policy_digest: ContentDigest,
    effective_scope_digest: ContentDigest,
)
```

No policy engine.

## GovernanceProfileRef

```python
GovernanceProfileRef(
    profile_key: StableRequirementKey,
    profile_version: int >= 1,
    content_digest: ContentDigest,
    policy_basis_digest: ContentDigest,
)
```

No GovernanceProfile implementation/selection engine.

## WorkspacePolicyRef

```python
WorkspacePolicyRef(
    policy_key: StableRequirementKey,
    content_digest: ContentDigest,
)
```

No workspace enforcement.

---

# 10. Canonical existing Baseline handling

Implement pure helpers:

```python
canonical_baseline_json(baseline: Baseline) -> str
source_baseline_ref(baseline: Baseline) -> SourceBaselineRef
source_baseline_ref_matches(
    baseline: Baseline,
    ref: SourceBaselineRef,
) -> bool
```

Canonical Baseline rules:

```text
artifact_ids:
lexicographically ascending
unique

decision_ids:
lexicographically ascending
unique
```

The existing `Baseline` model already ensures uniqueness but not ordering.

Slice 2.3 must reject a noncanonical Baseline rather than silently sort it before identity derivation.

Canonical JSON:

```text
model JSON-compatible representation
sort_keys=True
separators=(",", ":")
ensure_ascii=False
allow_nan=False
UTF-8 SHA-256
no floating-point normative values
```

Hard-code at least one expected Baseline canonical JSON + SHA-256 vector in tests.

Do not modify `relay_engine.domain.Baseline`.

---

# 11. Planning source / adapter models

## PlanningArtifactSourceRef

```python
PlanningArtifactSourceRef(
    source_key: StableRequirementKey,
    source_type: StableRequirementKey,
    source_version: str | None,
    content_digest: ContentDigest,
    provenance_digest: ContentDigest,
    locator: str | None,
)
```

The source is non-authoritative.

All fields are normative.

`source_version` and `locator`, when present, must be bounded nonblank strings.

No external provider call.

## PlanningAdapterRef

```python
PlanningAdapterRef(
    adapter_key: StableRequirementKey,
    adapter_version: int >= 1,
    adapter_digest: ContentDigest,
    supported_source_type: StableRequirementKey,
)
```

The adapter is provenance only.

Do not implement adapters.

---

# 12. NormalizationIssue

Implement a small immutable value sufficient for the accepted canonical rule:

```python
NormalizationIssue(
    issue_code: NormalizationIssueCode,
    field_key: StableRequirementKey,
    source_key: StableRequirementKey | None,
)
```

No freeform issue text is required by Slice 2.3 v1.

Standalone non-COMPLETE intent issue ordering:

```text
(issue_code declaration/value, field_key, source_key-or-empty)
```

duplicate exact issues rejected.

---

# 13. NormalizedEngineeringIntent

Implement:

```python
NormalizedEngineeringIntent(
    schema_version: Literal[1],
    source_refs: tuple[PlanningArtifactSourceRef, ...],
    adapter_ref: PlanningAdapterRef | None,
    objective: str,
    scope: ScopeSpec,
    acceptance_criteria: tuple[AcceptanceCriterion, ...],
    dependency_slice_ids: tuple[SliceId, ...],
    quality_requirement_keys: tuple[StableRequirementKey, ...],
    status: NormalizationStatus,
    issues: tuple[NormalizationIssue, ...],
)
```

### Required canonical invariants

`source_refs`:

```text
canonical key:
(source_type, source_key, source_version-or-empty,
 content_digest, provenance_digest)

duplicate/conflicting stable identity rejected
noncanonical order rejected
```

`scope.in_scope` and `scope.out_of_scope`:

```text
lexicographic UTF-8
unique
noncanonical order rejected
same statement cannot exist in both tuples
```

`acceptance_criteria`:

```text
sort by criterion.key
key unique
noncanonical order rejected
```

`dependency_slice_ids`:

lexicographic, unique, canonical.

`quality_requirement_keys`:

lexicographic, unique, canonical.

`status == COMPLETE` requires:

```text
source_refs nonempty
issues == ()
objective nonblank
```

Only COMPLETE intent may appear in a WorkPacket.

INCOMPLETE/INDETERMINATE values may exist as standalone models but WorkPacket construction must reject them.

The model/evaluator must never synthesize missing scope/criteria or authority.

---

# 14. Context material models

Implement a closed discriminated union.

## ArtifactMaterialRef

```python
ArtifactMaterialRef(
    material_kind: Literal["RELAY_ARTIFACT"],
    artifact: Artifact,
    provenance_digest: ContentDigest,
)
```

## RepositoryContentMaterialRef

```python
RepositoryContentMaterialRef(
    material_kind: Literal["REPOSITORY_CONTENT"],
    repository: RepositoryRef,
    commit: CommitRef,
    path: str,
    content_digest: ContentDigest,
    provenance_digest: ContentDigest,
)
```

Validate:

- `commit.repository == repository`;
- `path` is canonical repository-relative;
- no branch/tag/current worktree alias exists in the model.

Reuse Relay repository-relative-path validation semantics locally; do not modify domain.

## CapturedMaterialRef

```python
CapturedMaterialRef(
    material_kind: Literal["CAPTURED_MATERIAL"],
    resolver_key: StableResolverKey,
    resolver_version: int >= 1,
    material_key: bounded nonblank str,
    material_version: bounded nonblank str,
    content_digest: ContentDigest,
    provenance_digest: ContentDigest,
)
```

Binding semantics:

```text
resolver_key + resolver_version
= exact immutable external materialization contract identity

material_key + material_version
= exact immutable captured material identity
```

No mutable `latest` fallback.

No resolver registry.

No resolver implementation.

If exact resolver semantics are not externally established, material conformance is INDETERMINATE.

## ContextMaterialRef

Use a strict discriminated union of exactly those three variants.

No digest-only variant.

---

# 15. ContextSourceRef

Implement:

```python
ContextSourceRef(
    source_kind: ContextSourceKind,
    source_key: StableContextSourceKey,
    source_version: str | None,
    material_ref: ContextMaterialRef,
    locator: str | None,
)
```

All fields are normative.

`locator` is descriptive only and never content identity.

A mutable URL/name/path in `locator` cannot replace the material ref.

### Source/material compatibility

Enforce exactly:

```text
RELAY_ARTIFACT
  -> ArtifactMaterialRef only

GOVERNANCE_RECORD
  -> ArtifactMaterialRef
  -> RepositoryContentMaterialRef

REPOSITORY_CONTENT
  -> RepositoryContentMaterialRef only

TOOL_DEFINITION
SKILL
RETRIEVAL_RESULT
RUNTIME_OBSERVATION
EXTERNAL_REFERENCE
SESSION_EXCERPT
  -> ArtifactMaterialRef
  -> CapturedMaterialRef
```

Invalid pair -> model validation failure.

Do not add network/retrieval behavior.

---

# 16. ControlMirrorBinding

Implement:

```python
ControlMirrorBinding(
    mirror_kind: ControlMirrorKind,
    control_subject_digest: ContentDigest,
)
```

The digest identifies the exact WorkPacket control subject being mirrored.

The package must provide deterministic internal/public helper behavior sufficient to derive the expected control-subject digest from exact packet refs.

No mirrored control object may override packet refs.

---

# 17. ContextEntryRef

Implement:

```python
ContextEntryRef(
    entry_key: ContextEntryKey,
    context_class: ContextClass,
    source: ContextSourceRef,
    control_mirror_binding: ControlMirrorBinding | None,
)
```

Entry key is unique in a manifest.

Supporting context may have no mirror binding.

If a ContextEntryRef is explicitly evaluated/rendered as governing authority/role/policy/profile/design/slice/baseline context, a matching ControlMirrorBinding is mandatory.

Do not introduce an additional "authoritative" bool.

---

# 18. ContextManifest / ContextManifestRef

Implement:

```python
ContextManifest(
    schema_version: Literal[1],
    project_id: ProjectId,
    slice_definition_ref: SliceDefinitionRef,
    manifest_key: ContextManifestKey,
    revision: int >= 1,
    entries: tuple[ContextEntryRef, ...],
)
```

```python
ContextManifestRef(
    project_id: ProjectId,
    slice_id: SliceId,
    manifest_key: ContextManifestKey,
    revision: int >= 1,
    content_digest: ContentDigest,
)
```

Manifest entry rules:

```text
ORDER-NON-SEMANTIC / CANONICAL
sort by entry_key
entry_key unique
noncanonical order rejected
same stable entry identity + conflicting content rejected
```

Provide:

```python
canonical_context_manifest_json(...)
digest_context_manifest(...)
context_manifest_ref(...)
context_manifest_ref_matches(...)
```

No filesystem/network/materialization occurs in these helpers.

Hard-code fixed manifest JSON/digest vectors.

---

# 19. Evidence / deliverable / hard-stop models

Implement:

```python
EvidenceRequirement(
    key: StableRequirementKey,
    statement: str,
    required: bool,
    role_output_requirement: RoleOutputRequirement | None,
)
```

```python
DeliverableRequirement(
    key: StableRequirementKey,
    statement: str,
    required: bool,
    role_output_requirement: RoleOutputRequirement | None,
)
```

```python
HardStopRequirement(
    key: StableRequirementKey,
    statement: str,
)
```

All statements bounded/nonblank.

Tuple ordering by `key`.

Duplicate keys rejected.

No result completion/acceptance state inside these models.

---

# 20. ProtectedVerificationRequirement

Implement:

```python
ProtectedVerificationRequirement(
    artifact: Artifact,
    required_operation: VerificationAssetPermission,
    separate_authority_ref: AuthorityBasisRef | None,
)
```

No path enforcement.

No mutation.

No assumption that permission implies authority.

Canonical tuple key:

```text
artifact.path
artifact.id
artifact.content_digest
required_operation
separate_authority_ref exact canonical identity or empty
```

Same protected stable identity + conflicting content -> reject.

---

# 21. ProtectedVerificationRequirementRef

Implement:

```python
ProtectedVerificationRequirementRef(
    artifact_id: ArtifactId,
    artifact_content_digest: ContentDigest,
    required_operation: VerificationAssetPermission,
    requirement_digest: ContentDigest,
)
```

Provide deterministic helper:

```python
protected_verification_requirement_ref(requirement)
```

`requirement_digest` covers the full canonical requirement including separate authority ref.

---

# 22. WorkPacket

Implement the combined accepted shape:

```python
WorkPacket(
    schema_version: Literal[1],
    packet_key: WorkPacketKey,
    revision: int >= 1,

    project_id: ProjectId,
    slice_definition_ref: SliceDefinitionRef,
    source_baseline_ref: SourceBaselineRef,

    authority_refs: tuple[AuthorityBasisRef, ...],
    policy_basis_ref: PolicyBasisRef,
    governance_profile_ref: GovernanceProfileRef | None,
    role_contract_ref: RoleContractRef,

    accepted_design_artifacts: tuple[Artifact, ...],

    normalized_intent: NormalizedEngineeringIntent,

    context_manifest_ref: ContextManifestRef,
    required_context_keys: tuple[ContextEntryKey, ...],

    evidence_requirements: tuple[EvidenceRequirement, ...],
    deliverable_requirements: tuple[DeliverableRequirement, ...],
    hard_stops: tuple[HardStopRequirement, ...],

    required_runtime_capabilities: tuple[RuntimeCapability, ...],
    runtime_selection_requirement: RuntimeSelection | None,
    runtime_limits: RuntimeExecutionLimits,
    runtime_permission_profile_ref: RuntimePermissionProfileRef | None,
    credential_refs: tuple[CredentialRef, ...],

    workspace_policy_ref: WorkspacePolicyRef | None,
    required_workspace_property_keys: tuple[StableRequirementKey, ...],

    protected_verification_requirements:
        tuple[ProtectedVerificationRequirement, ...],

    authorized_successor_ref: WorkPacketRef | None,
)
```

Implementation may rely on postponed annotations for the self-reference.

No authority status field.

No lifecycle state.

No ActorRef/execution state.

No material bytes.

No prompt.

No result.

---

# 23. WorkPacket structural invariants

Require at construction:

```text
source_baseline_ref.project_id == project_id

slice_definition_ref.slice_id
    == context_manifest_ref.slice_id
    == WorkPacketRef slice_id when derived

source_baseline_ref.commit.repository
    == repository identity bound inside the baseline ref

normalized_intent.status == COMPLETE
normalized_intent.issues == ()

authority_refs nonempty

authority_refs canonical + unique
accepted_design_artifacts canonical + unique
required_context_keys canonical + unique
evidence requirements canonical + unique keys
deliverable requirements canonical + unique keys
hard stops canonical + unique keys
runtime capabilities canonical + unique
credential refs canonical + unique
workspace property keys canonical + unique
protected verification requirements canonical + unique

all strings bounded/nonblank
no floating-point normative values
```

Do not silently reorder.

Construction fails on noncanonical tuples.

---

# 24. WorkPacket canonical ordering

Enforce:

## authority_refs

```text
(authority_type value,
 authority_key,
 record_digest,
 subject_digest-or-empty)
```

## accepted_design_artifacts

```text
(path, artifact_id, commit.sha, content_digest)
```

## required_context_keys

lexical.

## evidence / deliverable / hard stops

by `key`.

## RuntimeCapability

enum declaration order.

## CredentialRef

`credential_id`.

## workspace property keys

lexical.

## protected verification requirements

the exact key in §20.

## normalized intent

its own recursive rules.

If equal canonical stable identity / sort key is encountered with conflicting normative content, reject.

Never add an arbitrary tie-breaker solely to make serialization deterministic.

---

# 25. WorkPacketRef and digest helpers

Implement:

```python
WorkPacketRef(
    project_id: ProjectId,
    slice_id: SliceId,
    packet_key: WorkPacketKey,
    revision: int >= 1,
    content_digest: ContentDigest,
)
```

Provide:

```python
canonical_work_packet_json(...)
digest_work_packet(...)
work_packet_ref(...)
work_packet_ref_matches(...)
```

Canonical JSON uses the same strict style as Slice 2.1 / accepted design.

Tests require literal expected canonical JSON + SHA-256 for:

- minimal WorkPacket;
- full tuple WorkPacket;
- amended packet revision.

No latest packet lookup.

---

# 26. Identity-conflict models/evaluators

Implement pure values/evaluators for already-grouped exact governance bases.

At minimum:

```python
WorkPacketIdentityConflict(
    has_conflict: bool,
    packet_key: WorkPacketKey | None,
    revision: int | None,
)
```

```python
ContextManifestIdentityConflict(
    has_conflict: bool,
    manifest_key: ContextManifestKey | None,
    revision: int | None,
)
```

Pure evaluators:

```python
evaluate_work_packet_identity_conflicts(refs)
evaluate_context_manifest_identity_conflicts(refs)
```

Rules:

```text
same project/slice/key/revision
+ same digest
= no conflict

same project/slice/key/revision
+ different digest
= conflict
```

No latest/max/newest/best-match resolution.

---

# 27. Exact-subject fact models

Do not implement a generic authority system.

Implement the accepted external fact carriers.

## Exact ref facts

Use explicit models rather than forcing Pydantic generics if generics add complexity.

At minimum:

```python
SliceDefinitionFact(
    evaluated_ref: SliceDefinitionRef,
    status: RequirementStatus,
)

SourceBaselineFact(
    evaluated_ref: SourceBaselineRef,
    status: RequirementStatus,
)

AuthorityBasisFact(
    evaluated_ref: AuthorityBasisRef,
    status: RequirementStatus,
)

PolicyBasisFact(
    evaluated_ref: PolicyBasisRef,
    status: RequirementStatus,
)

ContextManifestFact(
    evaluated_ref: ContextManifestRef,
    status: RequirementStatus,
)
```

## GovernanceProfileFact

Implement the exact design semantics:

```python
GovernanceProfileFact(
    evaluated_policy_basis_ref: PolicyBasisRef,
    evaluated_profile_ref: GovernanceProfileRef | None,
    profile_requirement_status: RequirementStatus,
    profile_status: RequirementStatus,
)
```

Absence of profile ref does not mean not-required.

## AcceptedDesignFact

```python
AcceptedDesignFact(
    evaluated_artifact: Artifact,
    status: RequirementStatus,
)
```

## ProtectedVerificationAuthorityFact

```python
ProtectedVerificationAuthorityFact(
    evaluated_requirement_ref: ProtectedVerificationRequirementRef,
    evaluated_authority_ref: AuthorityBasisRef | None,
    status: RequirementStatus,
)
```

No fact issues authority.

---

# 28. ContextMaterializationFact

Implement:

```python
ContextMaterializationFact(
    evaluated_material_ref: ContextMaterialRef,
    material_status: RequirementStatus,
    observed_content_digest: ContentDigest | None,
    observed_provenance_digest: ContentDigest | None,
)
```

Structural/status invariants:

### SATISFIED

Requires both observed digests non-null and equal expected material digests.

### UNSATISFIED

Used for positively observed mismatches.

Observed digests may be present and mismatching.

### INDETERMINATE

Used when material/provenance/resolver/version cannot be established.

Do not infer SATISFIED from expected digests alone.

Do not perform materialization.

---

# 29. WorkPacketConformanceFacts

Implement exact subject-bound facts:

```python
WorkPacketConformanceFacts(
    evaluated_work_packet_ref: WorkPacketRef,
    evaluated_context_manifest_ref: ContextManifestRef,

    slice_definition_fact: SliceDefinitionFact,
    source_baseline_fact: SourceBaselineFact,

    authority_facts: tuple[AuthorityBasisFact, ...],
    policy_basis_fact: PolicyBasisFact,
    governance_profile_fact: GovernanceProfileFact,

    role_contract_applicability: RoleApplicabilityEvaluation,

    accepted_design_facts: tuple[AcceptedDesignFact, ...],
    context_manifest_fact: ContextManifestFact,

    protected_verification_authority_facts:
        tuple[ProtectedVerificationAuthorityFact, ...],

    materialization_facts:
        tuple[ContextMaterializationFact, ...],
)
```

Fact tuple order must exactly mirror packet/manifest subject order.

Noncanonical fact tuple order is invalid.

---

# 30. Conformance result models

Implement a small deterministic result.

Suggested:

```python
WorkPacketConformance(
    status: RequirementStatus,
    reasons: tuple[WorkPacketReason, ...],
)
```

```python
ContextConformance(
    status: RequirementStatus,
    reasons: tuple[WorkPacketReason, ...],
    missing_context_keys: tuple[ContextEntryKey, ...] = (),
)
```

Reasons canonical/unique by enum declaration order.

Do not add `AUTHORIZED`.

---

# 31. WorkPacketReason

Provide stable semantic reasons needed by the accepted design.

At minimum:

```text
WORK_PACKET_IDENTITY_CONFLICT
CONTEXT_MANIFEST_IDENTITY_CONFLICT
WORK_PACKET_REF_MISMATCH
CONTEXT_MANIFEST_REF_MISMATCH

WORK_PACKET_FACT_SUBJECT_MISMATCH
CONTEXT_MANIFEST_FACT_SUBJECT_MISMATCH
SLICE_DEFINITION_FACT_SUBJECT_MISMATCH
SOURCE_BASELINE_FACT_SUBJECT_MISMATCH
AUTHORITY_FACT_SET_MISMATCH
POLICY_FACT_SUBJECT_MISMATCH
GOVERNANCE_PROFILE_FACT_SUBJECT_MISMATCH
ROLE_APPLICABILITY_SUBJECT_MISMATCH
ACCEPTED_DESIGN_FACT_SET_MISMATCH
PROTECTED_VERIFICATION_FACT_SET_MISMATCH
MATERIALIZATION_FACT_SET_MISMATCH

SLICE_DEFINITION_MISSING
SLICE_DEFINITION_STALE
SLICE_DEFINITION_CONFLICT
SOURCE_BASELINE_MISSING
SOURCE_BASELINE_STALE
SOURCE_BASELINE_CONFLICT
SOURCE_BASELINE_REF_MISMATCH
SOURCE_BASELINE_NONCANONICAL

AUTHORITY_BASIS_MISSING
AUTHORITY_BASIS_STALE
AUTHORITY_BASIS_CONFLICT
POLICY_BASIS_MISSING
POLICY_BASIS_STALE
POLICY_BASIS_CONFLICT
GOVERNANCE_PROFILE_REQUIRED
GOVERNANCE_PROFILE_STALE
GOVERNANCE_PROFILE_CONFLICT
ROLE_CONTRACT_NOT_APPLICABLE
ROLE_CONTRACT_APPLICABILITY_UNKNOWN

NORMALIZED_INTENT_INCOMPLETE
NORMALIZED_INTENT_INDETERMINATE
PLANNING_SOURCE_UNVERIFIABLE
WORK_SCOPE_CONFLICT
WORK_SCOPE_INDETERMINATE

REQUIRED_CONTEXT_MISSING
REQUIRED_CONTEXT_INVALID
REQUIRED_CONTEXT_INDETERMINATE
CONTEXT_SOURCE_UNVERIFIABLE
MUTABLE_CONTEXT_ALIAS_UNRESOLVED

CONTEXT_MATERIAL_REF_REQUIRED
CONTEXT_MATERIAL_UNAVAILABLE
CONTEXT_MATERIAL_CONTENT_MISMATCH
CONTEXT_MATERIAL_PROVENANCE_MISMATCH
CONTEXT_MATERIAL_RESOLVER_UNSUPPORTED
CONTEXT_SOURCE_MATERIAL_KIND_INVALID

CONTROL_MIRROR_BINDING_REQUIRED
CONTROL_MIRROR_CONFLICT

ACCEPTED_DESIGN_BASIS_MISSING
ACCEPTED_DESIGN_BASIS_STALE
PROTECTED_VERIFICATION_AUTHORITY_REQUIRED
PROTECTED_VERIFICATION_AUTHORITY_INDETERMINATE

REQUIRED_EVIDENCE_CONTRACT_MISSING
REQUIRED_DELIVERABLE_CONTRACT_MISSING
SUCCESSOR_REFERENCE_NOT_AUTHORITY
NESTED_COLLECTION_NONCANONICAL
```

Exact internal grouping may be simplified, but known mismatch / missing-indeterminate distinctions must remain available.

No reason creates authority.

---

# 32. Context conformance evaluator

Implement pure:

```python
evaluate_context_conformance(
    packet: WorkPacket,
    manifest: ContextManifest,
    materialization_facts: tuple[ContextMaterializationFact, ...],
) -> ContextConformance
```

Required evaluation:

1. exact `context_manifest_ref(manifest) == packet.context_manifest_ref`;
2. exact `manifest.project_id == packet.project_id`;
3. exact `manifest.slice_definition_ref == packet.slice_definition_ref`;
4. every `required_context_key` exists exactly once;
5. source/material pair structurally valid;
6. exact material fact exists for each required context material ref;
7. material fact exact ref matches;
8. material status SATISFIED;
9. observed content/provenance digests exact-match material ref;
10. repository material, when applicable, is consistent with packet source-baseline repository/commit semantics;
11. control-mirror binding, when present/required, exact-matches packet control subject.

Precedence:

```text
known exact mismatch -> UNSATISFIED
else missing/unavailable/unverifiable -> INDETERMINATE
else -> SATISFIED
```

No filesystem/network reads.

---

# 33. Control-mirror matching

Implement deterministic pure mirror checks.

For each mirror kind, compute/compare the exact WorkPacket subject identity.

Expected subject:

```text
AUTHORITY_BASIS
  exact one authority ref
  OR canonical exact authority-ref-set digest only where explicitly represented that way

ROLE_CONTRACT
  packet.role_contract_ref

POLICY_BASIS
  packet.policy_basis_ref

GOVERNANCE_PROFILE
  packet.governance_profile_ref

ACCEPTED_DESIGN
  exact one packet accepted-design Artifact

SLICE_DEFINITION
  packet.slice_definition_ref

SOURCE_BASELINE
  packet.source_baseline_ref
```

If a mirror claims governing status but has no matching exact packet subject:

`CONTROL_MIRROR_CONFLICT / UNSATISFIED`

A supporting unbound entry may remain supporting context but cannot satisfy a governing mirror requirement.

Do not build a prompt renderer.

---

# 34. WorkPacket conformance evaluator

Implement pure:

```python
evaluate_work_packet_conformance(
    packet: WorkPacket,
    manifest: ContextManifest,
    facts: WorkPacketConformanceFacts,
) -> WorkPacketConformance
```

Mandatory evaluation order:

```text
1. packet structural/canonical validation already passed
2. derive exact WorkPacketRef
3. facts.evaluated_work_packet_ref exact match

4. manifest structural/canonical validation already passed
5. derive exact ContextManifestRef
6. packet/facts exact manifest refs match

7. exact subject bindings:
   SliceDefinitionRef
   SourceBaselineRef
   AuthorityBasisRef tuple
   PolicyBasisRef
   GovernanceProfileRef / exact not-required fact
   RoleApplicabilityEvaluation exact RoleContractRef
   accepted-design Artifact tuple
   protected-verification fact tuple
   materialization fact tuple

8. exact context/materialization conformance

9. evaluate supplied RequirementStatus values

10. aggregate:
    known incompatible/invalid -> UNSATISFIED
    else missing/stale/conflicting/unverifiable -> INDETERMINATE
    else -> SATISFIED
```

No later success can repair an earlier exact-subject mismatch.

Critical invariant:

```text
WorkPacketConformance.status == SATISFIED
    !=
AUTHORIZED
```

---

# 35. GovernanceProfileFact evaluator semantics

When packet has a profile:

```text
fact policy ref exact matches
fact profile ref exact matches
profile_requirement_status == SATISFIED
profile_status == SATISFIED
```

When packet has no profile:

```text
fact policy ref exact matches
fact evaluated_profile_ref is None
profile_requirement_status == SATISFIED
    means exact external policy positively established "not required"
```

Missing/unknown not-required basis -> INDETERMINATE.

Never infer "profile not required" from None alone.

---

# 36. Authority fact-set semantics

`authority_facts` must have exactly one fact for each packet `authority_ref`, same canonical order.

No missing facts.

No extra facts.

No substitution by semantically related/superseding authority.

Known fact for another exact ref -> UNSATISFIED.

Missing/stale/conflicting/unverifiable fact -> INDETERMINATE.

The package does not validate Human root authority.

---

# 37. Accepted-design fact semantics

`accepted_design_facts` must exactly correspond to `packet.accepted_design_artifacts`.

Comparison uses full Artifact identity:

```text
ArtifactId
path
CommitRef
ContentDigest
artifact_type
```

No path-only or latest-commit matching.

A fact for another artifact revision cannot satisfy the packet.

---

# 38. Protected-verification conformance

For each packet requirement that needs separate authority evaluation:

- derive exact ProtectedVerificationRequirementRef;
- require exactly one matching fact;
- if separate authority ref exists, fact must carry same exact authority ref;
- READ != MODIFY;
- MODIFY != APPROVE_MUTATION;
- EVALUATE does not imply mutation authority;
- workspace capability is irrelevant to this evaluator.

No protected asset mutation is performed.

---

# 39. Materialization fact semantics

Required context materials only.

For every required context key:

- derive exact material ref;
- require one exact fact.

SATISFIED only when observed content + provenance digests exactly match expected.

A bare expected digest is never evidence.

Optional ContextManifest entries need not have facts unless consumed elsewhere; Slice 2.3 does not decide renderer consumption.

---

# 40. Resolver/provenance boundary

No material resolver implementation.

No resolver registry.

For CapturedMaterialRef:

```text
resolver_key + resolver_version
must be treated as exact immutable externally established contract identity.
```

If an external caller cannot establish that resolver contract/version or material/provenance identity:

`INDETERMINATE`

Provenance SATISFIED requires exact provenance bytes/record to be obtainable or canonically derivable by the external materialization contract.

A bare provenance digest with no obtainable/derivable provenance remains INDETERMINATE.

Tests should model this through supplied facts only, not by implementing resolvers.

---

# 41. Public package exports

`src/relay_engine/work_packets/__init__.py` should export only stable Slice 2.3 contract models/evaluators.

Expected categories:

- reference/key enums/models;
- planning-normalization models;
- context material/source/manifest models;
- WorkPacket models;
- exact fact/conformance models;
- identity/digest helpers;
- pure conformance evaluators;
- identity-conflict evaluators.

No import-time side effects.

No mutable global registries.

No auto-discovery.

---

# 42. Architecture prohibitions

Production `relay_engine.work_packets` must not import/call mutation/execution APIs from:

```text
relay_engine.persistence
relay_engine.lifecycle
relay_engine.human_control
relay_engine.manual_evaluation
repository mutation/promotion executors
board/web UI mutation paths
bootstrap/adoption mutation paths
AgentRuntime protocol/adapters
network/http clients
vector DB / retrieval clients
```

Allowed imports:

- stable domain values;
- stable Role Contract values/evaluation result types;
- stable Agent Runtime declaration models/enums only.

A static architecture test must fail if forbidden dependencies appear.

---

# 43. No implementation wiring

Do not modify existing Relay callers to consume WorkPacket/ContextManifest.

Do not wire Slice 2.3 into:

- governance gates;
- lifecycle;
- Human approval;
- manual evaluation;
- canonical promotion;
- adoption/bootstrap;
- runtime request construction;
- workspace creation;
- board projections;
- CLI;
- UI;
- external planning systems.

The initial implementation succeeds by implementing the deterministic contract and negative tests.

---

# 44. Required model tests — identity and canonicality

At minimum:

```text
all models frozen / strict / extra-forbid
schema_version=1 where applicable
stable key validation
revisions >= 1

SliceDefinitionRef exact validation
SourceBaselineRef exact validation

noncanonical Baseline.artifact_ids -> rejected for source ref
noncanonical Baseline.decision_ids -> rejected for source ref
fixed Baseline JSON/digest vector

NormalizedEngineeringIntent:
  source_refs canonical/unique
  scope in/out canonical/unique/disjoint
  acceptance criteria canonical/unique
  dependencies canonical/unique
  quality keys canonical/unique
  COMPLETE requires issues == ()
  WorkPacket rejects non-COMPLETE intent

Context source/material compatibility
repository content commit repository match
repository path canonical

ContextManifest entries canonical/unique
fixed minimal manifest JSON/digest
fixed all-material-variants manifest JSON/digest
manifest field mutation changes digest
ContextManifestRef exact match/mismatch

WorkPacket all top-level tuple canonical rules
stable-identity collision + conflicting content rejected
fixed minimal packet JSON/digest
fixed full tuple packet JSON/digest
fixed amended packet JSON/digest
field mutation changes digest
WorkPacketRef exact match/mismatch
```

---

# 45. Required evaluation tests — F001 exact fact binding

Mandatory:

```text
facts for Packet A cannot satisfy Packet B
changed packet revision/digest invalidates facts
changed ContextManifestRef invalidates facts
changed SliceDefinitionRef invalidates facts
changed SourceBaselineRef invalidates facts

authority facts exact set match -> may proceed
missing authority fact -> INDETERMINATE
extra authority fact -> mismatch/fail closed
different authority ref -> UNSATISFIED

policy A fact cannot satisfy policy B
profile A fact cannot satisfy profile B
no profile + no exact not-required fact -> INDETERMINATE

RoleApplicabilityEvaluation for RoleContract A cannot satisfy B
RoleApplicabilityEvaluation NOT_APPLICABLE -> UNSATISFIED
RoleApplicabilityEvaluation INDETERMINATE -> INDETERMINATE

accepted-design set A cannot satisfy B
protected-verification fact A cannot satisfy requirement B
materialization fact set A cannot satisfy Manifest B
```

---

# 46. Required evaluation tests — F002 recursive canonicality

Mandatory:

```text
Baseline artifact/decision reorder rejected
planning source reorder rejected
scope reorder rejected
acceptance criteria reorder rejected
dependency reorder rejected
quality-key reorder rejected
manifest entry reorder rejected
authority-ref reorder rejected
accepted-artifact reorder rejected
required-context-key reorder rejected
evidence/deliverable/hard-stop reorder rejected
runtime-capability reorder rejected
credential reorder rejected
workspace-property reorder rejected
protected-verification reorder rejected
fact tuple reorder rejected

same stable sort identity + conflicting content rejected
semantically identical canonical objects -> identical digest
one normative scalar change -> different digest
```

Do not test canonicality only by comparing helper output to itself.

---

# 47. Required evaluation tests — F003 materialization

Mandatory:

```text
digest-only required context impossible structurally

ArtifactMaterialRef unavailable -> INDETERMINATE
RepositoryContentMaterialRef unavailable -> INDETERMINATE
CapturedMaterialRef unresolved resolver/version -> INDETERMINATE

material available + content mismatch -> UNSATISFIED
material available + provenance mismatch -> UNSATISFIED
exact material + exact provenance -> SATISFIED

mutable URL locator alone cannot satisfy context
branch name alone cannot satisfy repository material
current tool name alone cannot satisfy captured material
session name alone cannot satisfy captured material

required SESSION_EXCERPT carries exact material ref
required TOOL_DEFINITION carries exact material ref
required SKILL carries exact material ref
required EXTERNAL_REFERENCE carries exact material ref

provenance digest with no obtainable/derivable provenance -> INDETERMINATE
no prior chat state needed for exact context identity
```

---

# 48. Required control-mirror tests

Mandatory:

```text
mirrored RoleContract exact match -> allowed
mirrored RoleContract mismatch -> UNSATISFIED
mirrored PolicyBasis mismatch -> UNSATISFIED
mirrored GovernanceProfile mismatch -> UNSATISFIED
mirrored authority mismatch -> UNSATISFIED
mirrored accepted design mismatch -> UNSATISFIED
mirrored SliceDefinition mismatch -> UNSATISFIED
mirrored SourceBaseline mismatch -> UNSATISFIED

unbound supporting context remains supporting only
unbound supporting context cannot satisfy governing mirror semantics
mirror cannot override/extend packet control subject
```

---

# 49. Required non-authority tests

Explicitly prove:

```text
WorkPacket has no authority/authorized field
ContextManifest has no authority field
WorkPacketConformance has no AUTHORIZED state
SATISFIED != AUTHORIZED
AuthorityBasisRef is reference-only
AuthorityBasisFact is evidence-only
RoleApplicabilityEvaluation APPLICABLE != work authority
RuntimeCapability != authority
CredentialRef availability != authority
WorkspacePolicyRef != enforcement
ControlMirrorBinding != authority
materialization success != authority
accepted design fact != Human acceptance
authorized_successor_ref != successor execution authority
```

No function named/semantically equivalent to:

```text
authorize_work
accept_result
promote_result
execute_packet
invoke_agent
create_workspace
resolve_material
```

in the Slice 2.3 package.

---

# 50. Required boundary/static tests

`tests/unit/test_work_packet_architecture.py` must prove:

```text
no DB/persistence imports
no migration imports
no lifecycle mutation imports
no Human-control mutation imports
no manual-evaluation mutation imports
no promotion executor imports
no AgentRuntime protocol/adapter invocation
no network/http client imports
no vector DB / retrieval implementation
no filesystem materialization implementation
no resolver registry/global mutable resolver map
no workspace enforcement
no new UUID prefix
no latest/current/best-match resolver
no source/test edits outside authorized six files
```

Prefer AST/import inspection or direct module introspection over brittle whole-repository substring scanning.

---

# 51. A01–A14 implementation evidence mapping

Codex's candidate must demonstrate:

```text
A01 immutable exact packet identity/digest
    -> canonical model/digest tests + fixed vectors

A02 Project/Slice/Baseline binding
    -> structural + mismatch tests

A03 exact external authority/policy/profile/role refs
    -> exact fact binding tests + non-authority tests

A04 reproducible ContextManifest
    -> material ref + materialization fact tests

A05 provider-neutral normalized intent
    -> normalization canonical/fail-closed tests

A06 scope/non-scope/acceptance/evidence/deliverable
    -> model validation and tuple identity tests

A07 Slice 2.2 mapping
    -> exact RoleApplicabilityEvaluation reuse + RoleOutputRequirement refs

A08 runtime declaration only
    -> model reuse + architecture prohibition

A09 workspace declaration only
    -> WorkspacePolicyRef + architecture prohibition

A10 protected verification cannot grant authority
    -> exact requirement/ref fact tests

A11 amendment/new digest/no latest
    -> digest mutation + no resolver tests

A12 successor semantics preserved
    -> authorized_successor_ref remains pure ref/non-authority

A13 fail closed missing/stale/conflicting/unverifiable
    -> conformance precedence/negative tests

A14 no DB/RAG/orchestration/provider/2.4/Phase3 leakage
    -> architecture tests
```

---

# 52. Focused validation commands

Once authorized, Codex must run:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_work_packet_models.py
uv run pytest tests/unit/test_work_packet_evaluation.py
uv run pytest tests/unit/test_work_packet_architecture.py

uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

No network/provider/model/materialization execution is needed.

Exact-head GitHub Actions must also pass on the implementation candidate before independent implementation acceptance.

---

# 53. Scope verification

Before committing:

```bash
git status --short
git diff --name-only <AUTHORIZED_BASELINE>...HEAD
```

Expected changed paths exactly:

```text
src/relay_engine/work_packets/__init__.py
src/relay_engine/work_packets/models.py
src/relay_engine/work_packets/evaluation.py
tests/unit/test_work_packet_models.py
tests/unit/test_work_packet_evaluation.py
tests/unit/test_work_packet_architecture.py
```

If any other path appears, STOP unless separately authorized.

---

# 54. Candidate discipline

Codex must produce one coherent implementation candidate.

It must:

- start from exact authorized baseline;
- create only the six authorized files;
- keep the worktree clean outside those files;
- commit the candidate;
- push only `implementation/2.3-context-work-packet-contract`;
- not update `main`;
- not modify the design branch;
- not write its own evaluation or acceptance;
- not create follow-on authority;
- stop after returning exact candidate SHA/evidence.

No self-acceptance.

---

# 55. Required Codex return report

Return exactly enough evidence for independent review:

```text
SLICE 2.3 IMPLEMENTATION — READY FOR INDEPENDENT REVIEW

Implementation authority:
RLY-S23-IMPL-AUTH-001 — AUTHORIZED

Authorized baseline:
<exact SHA>

Implementation branch:
implementation/2.3-context-work-packet-contract

Candidate SHA:
<exact>

Parent:
<exact>

Remote branch:
<exact / verified>

Executor:
Codex

Actual model/runtime:
<exact if exposed>

Changed files:
<complete exact list>

A01-A14:
PASS/FAIL each

F001 exact-subject binding:
PASS/FAIL

F002 recursive canonical identity:
PASS/FAIL

F003 deterministic materialization contract:
PASS/FAIL

WorkPacket != authority invariant:
PASS/FAIL

Human root authority external:
PASS/FAIL

Focused model tests:
<count/result>

Focused evaluation tests:
<count/result>

Architecture tests:
<count/result>

Ruff format:
PASS/FAIL

Ruff lint:
PASS/FAIL

Pyright:
PASS/FAIL + diagnostics

Full pytest:
<count/result>

Build:
PASS/FAIL

git diff --check:
PASS/FAIL

Exact-head GitHub Actions:
<run ID/status>

Database/schema changes:
NONE

Dependency changes:
NONE

Network/provider/model calls:
NONE

Material resolver/storage implementation:
NONE

Operational DB/lifecycle mutations:
NONE

Workspace enforcement:
NONE

Deviations:
NONE or exact list

New work discovered:
NONE or exact non-authoritative proposals

Working tree:
CLEAN / DIRTY

Final disposition:
STOP FOR SOL INDEPENDENT IMPLEMENTATION REVIEW
```

---

# 56. Hard stop / authority boundary

Even after implementation authorization, Codex is not authorized to:

- issue or validate Human root authority;
- issue work authority;
- create production WorkPackets for real work;
- persist WorkPackets or ContextManifests;
- build a material resolver/content store;
- fetch external context;
- read implicit chat history;
- invoke AgentRuntime/provider/model endpoints;
- create/enforce workspaces;
- mutate operational DB/lifecycle;
- implement Slice 2.4;
- open or implement Phase 3;
- execute real-project agent work;
- accept/evaluate its own implementation;
- merge/promote to canonical main.

Stop after one implementation candidate and evidence report.

```text
Design accepted != implementation complete.
Implementation authorized != agent execution authorized.
Packet conforming != work authorized.
Unblocked != authorized.
```
