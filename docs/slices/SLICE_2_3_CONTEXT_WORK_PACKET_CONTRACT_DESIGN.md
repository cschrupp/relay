# Slice 2.3 — Context / Work-Packet Contract — Design Revision 1

**Document class:** Lockable Slice design record  
**Status:** DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Design authority:** `RLY-S23-DESIGN-AUTH-001 — AUTHORIZED`  
**Design branch:** `design/2.3-context-work-packet-contract`

---

## 1. Purpose

Slice 2.3 defines the deterministic Relay contract that transports one exact bounded unit of governed work and the exact effective context required to perform it.

The design connects already-established governance and runtime concepts without creating a second authority system, a second artifact registry, a workflow engine, or workspace enforcement.

The central invariant is:

```text
WorkPacket
  = exact bounded work description
  + exact external authority references
  + exact accepted role reference
  + exact source baseline
  + exact normalized intent
  + exact context manifest
  + exact evidence/deliverable contract
  + declarative runtime/workspace requirements

WorkPacket != authority
ContextManifest != authority
NormalizedEngineeringIntent != authority
packet conformance != execution authority
```

An executor may act only when a separate governance/orchestration layer establishes current authority and all other execution predicates.

---

## 2. Governing lineage

This design is governed by:

```text
Canonical design baseline:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Slice 2.3 opening:
RLY-S23-OPEN-001 — OPEN

Opening commit:
bddc6a25ab31cfe7395b07135d7f05f5ac3c8e0f

Design authority:
RLY-S23-DESIGN-AUTH-001 — AUTHORIZED

Design-authority commit:
4bc054af24bbd19130d7474bab75433b056ef9e4

Existing Slice 2.3 proposal:
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT.md

Proposal blob:
575f3ae1bca0752f0bd5840559d4dea0010352f4

Slice 2.2 accepted implementation:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Slice 2.2 closure:
RLY-S22-CLOSE-EVAL-001 — ACCEPT
```

The existing proposal is design input. This document is normative where it refines that proposal.

---

## 3. Design problem

Relay now has:

- deterministic project/slice/baseline/artifact identity;
- Human/governance authorization mechanisms;
- accepted Role Contracts;
- runtime capability and requested/actual runtime provenance;
- accepted governance-assurance semantics.

What is still missing is an exact immutable work envelope answering:

```text
What exact work?
Against what exact project/slice definition?
Against what exact source baseline?
Under what exact external authority?
Under what exact RoleContract?
Using what exact accepted design/policy/profile basis?
With what exact effective context?
With what exact scope/non-scope?
With what acceptance criteria?
With what required evidence?
With what deliverable/result contract?
With what declarative runtime/workspace requirements?
Under what hard-stop/escalation conditions?
```

Without that envelope, orchestration can drift even if role/runtime/workspace components are individually correct.

---

## 4. Non-authority invariants

The following are normative:

```text
packet presence != authority
packet digest != authority
packet conformance != authority
context presence != authority
context digest != authority
prompt text != context authority
planning source != authority
normalization != authority
adapter output != authority
role contract != work authority
runtime capability != work authority
workspace capability != work authority
credential availability != work authority
successful previous packet != successor authority
PROPOSED_WORK != authorized work
roadmap order != authority
```

Human root authority remains external to Slice 2.3.

No WorkPacket constructor/evaluator may issue, renew, infer, or bootstrap authority.

---

## 5. Ownership boundaries

### Slice 2.3 owns

- exact WorkPacket representation;
- exact WorkPacket reference/digest;
- exact ContextManifest representation;
- exact ContextManifest reference/digest;
- provider-neutral normalized intent representation;
- planning-source and normalization-adapter provenance;
- exact transport of authority/policy/profile/design/role references;
- exact work scope/non-scope and acceptance criteria;
- required evidence and deliverable/result contract;
- declarative runtime requirements;
- declarative workspace-policy requirements;
- fail-closed packet/context conformance;
- packet/context revision and identity-conflict semantics;
- successor WorkPacket reference transport where authority already exists.

### Slice 2.2 owns

- RoleContract;
- RoleContractRef;
- role/action eligibility;
- role input/output obligation vocabulary;
- RoleContract applicability;
- role separation;
- protected-verification semantic permissions;
- PROPOSED_WORK non-authority;
- successor tri-state;
- BACKLOG_EXHAUSTED semantics.

Slice 2.3 transports Slice 2.2 values. It does not redefine them.

### Slice 2.1 owns

- runtime capabilities;
- runtime/provider/model requested/actual provenance;
- runtime sessions;
- RuntimeExecutionBasis/Request;
- runtime permissions/credentials at execution;
- runtime events/cancel/result inspection.

Slice 2.3 may declare requirements using accepted Slice 2.1 values. It does not invoke AgentRuntime.

### Slice 2.4 owns

- concrete workspace creation;
- filesystem/path allow/deny enforcement;
- tool restrictions;
- network restrictions;
- credential access enforcement;
- resource enforcement;
- protected-asset concrete mutation controls;
- workspace/environment evidence.

Slice 2.3 transports exact declarative workspace-policy requirements only.

### Phase 3 owns

- resolving an exact current WorkPacket for execution;
- binding an exact actor/execution;
- combining role + authority + packet + workspace + runtime predicates;
- rendering/finalizing runtime input;
- invoking AgentRuntime;
- collecting result/evidence;
- successor handoff/orchestration.

---

## 6. Identity strategy

No new UUID prefix is required for WorkPacket or ContextManifest.

Both are immutable stable-key/revision/content-digest identities.

Normative concept:

```python
type WorkPacketKey = bounded stable lowercase key
type ContextManifestKey = bounded stable lowercase key

WorkPacketRef(
    project_id,
    slice_id,
    packet_key,
    revision,
    content_digest,
)

ContextManifestRef(
    project_id,
    slice_id,
    manifest_key,
    revision,
    content_digest,
)
```

Rules:

- stable keys are lowercase, start with a letter, and use optional hyphen-separated alphanumeric segments;
- revision starts at 1;
- digest is SHA-256 of exact canonical schema bytes;
- exact ref is always required;
- no "latest", max revision, newest timestamp, branch tip, or best-match resolution is permitted;
- same key/revision with different digest under one exact governed basis is an identity conflict;
- an amended normative object receives a new revision and a new digest;
- no-op revision increments are forbidden when prior exact identity is supplied;
- prior immutable versions remain valid historical subjects.

---

## 7. Exact Slice-definition reference

The existing `Slice` domain value intentionally has no workflow state or revision.

Slice 2.3 therefore introduces a reference-only exact definition identity:

```python
SliceDefinitionRef(
    slice_id: SliceId,
    definition_revision: int >= 1,
    content_digest: ContentDigest,
)
```

This does not replace `Slice`.

The digest identifies the exact normalized Slice-definition bytes established elsewhere.

The WorkPacket must bind the exact SliceDefinitionRef used to establish its objective/scope/acceptance contract.

No packet may resolve a Slice definition by "current" or roadmap position.

---

## 8. Exact authority reference transport

Slice 2.3 must carry exact authority references but must not model authority issuance.

Reference-only vocabulary:

```text
AuthorityReferenceType:
  SLICE_AUTHORIZATION_GRANT
  REPOSITORY_MUTATION_AUTHORIZATION
  HUMAN_GOVERNANCE_RECORD
```

Conceptual value:

```python
AuthorityBasisRef(
    authority_type,
    authority_key,
    record_digest,
    subject_digest | None,
)
```

Semantics:

- `authority_key` identifies the external authority record;
- `record_digest` binds exact authority-record content;
- `subject_digest` is required when the authority mechanism is subject-digest bound;
- the reference itself does not prove currentness, applicability, or validity;
- external governance supplies currentness/applicability facts;
- no authority type may be added merely to make a packet pass;
- opaque prose without exact record identity/digest is insufficient.

A packet with an authority reference can still be unauthorized.

---

## 9. Exact policy/profile references

Slice 2.3 uses reference-only policy/profile values.

Conceptually:

```python
PolicyBasisRef(
    policy_key,
    policy_version,
    policy_digest,
    effective_scope_digest,
)

GovernanceProfileRef(
    profile_key,
    profile_version,
    content_digest,
    policy_basis_digest,
)
```

Rules:

- policy/profile selection occurs outside Slice 2.3;
- WorkPacket transports the exact externally selected values;
- WorkPacket cannot select a weaker profile;
- missing required profile is fail-closed;
- stale/conflicting profile/policy is fail-closed;
- packet digest does not establish policy/profile applicability.

---

## 10. Exact accepted-artifact references

For accepted design/architecture/governance inputs already represented as Relay `Artifact` values, reuse the existing `Artifact` model rather than inventing a second document reference type.

A packet may include exact accepted artifacts whose identity includes:

- ArtifactId;
- repository-relative path;
- CommitRef;
- ContentDigest;
- artifact type.

Presence of an Artifact does not establish acceptance; external governance currentness/acceptance facts remain separate.

---

## 11. Context classes

Every effective context entry is explicitly classified:

```text
STATIC
DYNAMIC
```

### STATIC

Examples:

- repository/system rules;
- accepted architecture;
- accepted design;
- policy references;
- RoleContract reference;
- authority/non-authority guardrails;
- stable project conventions.

### DYNAMIC

Examples:

- selected repository files/content;
- retrieved documents;
- skills;
- tool definitions;
- runtime observations;
- external references;
- bounded session excerpts.

The class indicates change cadence/provenance expectations only.

STATIC does not imply authoritative.

DYNAMIC does not imply untrusted.

---

## 12. Context source vocabulary

The minimum source kinds are:

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

Conceptual source reference:

```python
ContextSourceRef(
    source_kind,
    source_key,
    content_digest,
    provenance_digest,
    source_version | None,
    locator | None,
    repository_commit | None,
)
```

Normative rules:

- `content_digest` identifies exact content;
- `provenance_digest` binds exact source/retrieval/capture metadata;
- `source_key` is stable and secret-free;
- `locator` is descriptive/retrieval provenance, not content identity;
- repository content requires exact CommitRef;
- a mutable branch, URL, file path, tool name, skill name, or session name without exact content digest is insufficient;
- secret material must never appear in a locator/reference;
- credentials are referenced only by existing opaque credential IDs;
- if required exact content cannot be reconstructed/verified, conformance is INDETERMINATE.

No source kind grants authority.

---

## 13. Context entries

Conceptual value:

```python
ContextEntryRef(
    entry_key,
    context_class,
    source: ContextSourceRef,
)
```

Rules:

- entry keys are stable and unique within a manifest;
- entries are canonical-order by `entry_key`;
- the same entry key cannot point to multiple digests in one manifest;
- content is identified by source content digest;
- no duplicate content source identity with conflicting provenance is permitted;
- a context entry is a reference, not mutable embedded session state.

---

## 14. ContextManifest

Normative shape:

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

The ContextManifest represents the exact effective governed context available to the packet.

It does not contain authority status.

It does not contain implicit chat history.

It does not contain "all repository files" unless exact selected file identities are explicitly enumerated or a separately digest-bound repository snapshot manifest is referenced.

It does not fetch content.

It does not execute retrieval.

It does not own context-window truncation.

---

## 15. Required context is packet-owned

A WorkPacket carries:

```python
required_context_keys: tuple[ContextEntryKey, ...]
```

The referenced ContextManifest may contain additional optional/supporting entries, but every required key must:

- exist exactly once;
- have exact content digest;
- have sufficient provenance;
- be compatible with the packet's exact project/slice/baseline where applicable.

Missing required key:

`INDETERMINATE / STOP`

Known wrong content/source:

`UNSATISFIED / STOP`

Optional content never silently becomes required authority.

---

## 16. Mutable context aliases are prohibited

Required governed context may not be represented only as:

```text
latest
current
HEAD
main
the current file
the current tool schema
the latest web page
the current chat
the previous answer
whatever the retriever returns
```

If such a mutable source matters, it must be frozen into an exact snapshot/reference and digest before it can satisfy a required context key.

This is the reproducibility boundary.

---

## 17. Session-history treatment

Conversation/session history is not implicitly part of a WorkPacket.

If a bounded session excerpt is required:

- the excerpt must be explicitly selected;
- the exact selected bytes must be content-digested;
- provenance must identify the source session/sequence/window without embedding secrets;
- the excerpt becomes a DYNAMIC `SESSION_EXCERPT` context entry;
- later turns outside the snapshot cannot silently change packet meaning.

A model's latent memory is never governed context.

---

## 18. Tool and skill treatment

Required tool/skill semantics must be exact.

A tool definition or skill reference used as governed input requires:

- stable key;
- version if available;
- exact content digest;
- provenance digest.

A tool merely being installed/available is capability, not authority.

If the exact required tool/skill contract changes, the ContextManifest digest changes.

---

## 19. External/retrieved content treatment

Required external content must be captured as an exact snapshot or exact content-addressed reference.

The WorkPacket/ContextManifest must not claim reproducibility from a mutable external URL alone.

Required retrieval provenance includes enough exact facts to explain:

- what source was selected;
- what content was selected;
- which exact digest was consumed;
- which retrieval/capture basis produced it.

General-purpose RAG is out of scope.

---

## 20. Planning-source interoperability

Relay planning may originate from:

- Relay-native design/governance;
- another deterministic planning system;
- Spec Kit;
- OpenSpec;
- BMAD;
- an enterprise workflow;
- a future provider.

Named systems are examples, not dependencies.

The WorkPacket contract must remain provider-neutral.

---

## 21. PlanningArtifactSourceRef

Conceptual value:

```python
PlanningArtifactSourceRef(
    source_key,
    source_type,
    source_version | None,
    content_digest,
    provenance_digest,
    locator | None,
)
```

This identifies exact planning source content.

It is non-authoritative.

A source may contain proposals, design, scope, or acceptance statements, but Relay does not infer Human authority from their presence.

---

## 22. PlanningAdapterRef

Conceptual value:

```python
PlanningAdapterRef(
    adapter_key,
    adapter_version,
    adapter_digest,
    supported_source_type,
)
```

An adapter is a normalization mechanism, not a governance actor.

Adapter code/version/digest must be exact when adapter transformation affects normalized intent.

Relay-native already-normalized input may omit an adapter ref when no transformation occurred.

No adapter implementation is authorized by this Slice design.

---

## 23. Normalization status

Stable status:

```text
COMPLETE
INCOMPLETE
INDETERMINATE
```

Minimum issue vocabulary:

```text
MISSING_REQUIRED_FIELD
AMBIGUOUS_FIELD
CONFLICTING_FIELD
UNSUPPORTED_SEMANTIC
SOURCE_UNVERIFIABLE
```

Semantics:

- COMPLETE: every required normalized field is exact and source-supported;
- INCOMPLETE: a required field is positively absent;
- INDETERMINATE: ambiguity/conflict/verifiability prevents establishing exact meaning.

Only COMPLETE normalized intent may appear in a conforming WorkPacket.

---

## 24. NormalizedEngineeringIntent

Reuse existing domain values where possible.

Conceptual shape:

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

Rules:

- objective nonblank;
- in-scope/out-of-scope statements explicit;
- acceptance criterion keys unique;
- dependencies unique/canonical;
- source refs nonempty;
- COMPLETE requires zero issues;
- INCOMPLETE/INDETERMINATE cannot be admitted into a conforming WorkPacket;
- no field may be invented from ambiguous prose merely to achieve COMPLETE.

---

## 25. Human clarification

A Human may clarify normalized intent.

Clarification becomes governed only when represented through an external durable Human decision/authority and exact source reference.

A chat answer by itself does not silently mutate an existing normalized intent or WorkPacket.

If Human clarification changes objective/scope/acceptance:

- normalized intent changes;
- WorkPacket digest changes;
- WorkPacket revision changes;
- prior authority binding cannot be reused unless external governance explicitly establishes applicability to the new exact subject.

---

## 26. Work objective/scope contract

The WorkPacket includes exact normalized intent rather than duplicating objective/scope/acceptance text separately.

This prevents drift between:

- planning source;
- normalized intent;
- packet scope.

Packet conformance requires:

```text
packet.slice_definition_ref
compatible with
normalized intent scope/acceptance
compatible with
external exact current authority subject
```

Compatibility is supplied/evaluated deterministically from external facts; Slice 2.3 does not broaden authority.

---

## 27. Evidence requirement

Conceptual value:

```python
EvidenceRequirement(
    key,
    statement,
    required: bool,
    role_output_requirement: RoleOutputRequirement | None,
)
```

Rules:

- key stable/unique;
- statement nonblank;
- required evidence is explicit;
- mapping to a Slice 2.2 RoleOutputRequirement is optional when the evidence has a direct role-output semantic;
- packet does not claim that evidence exists merely because the requirement is present.

Examples:

- test results;
- diff/change-surface evidence;
- evaluation judgment;
- execution provenance;
- exact artifact hashes;
- repository-state evidence.

---

## 28. Deliverable contract

Conceptual value:

```python
DeliverableRequirement(
    key,
    statement,
    required: bool,
    role_output_requirement: RoleOutputRequirement | None,
)
```

This describes what result must be produced.

It does not accept the result.

It does not promote the result.

It does not mutate lifecycle.

---

## 29. Hard stops and escalation

Conceptual value:

```python
HardStopRequirement(
    key,
    statement,
)
```

Hard stops are declarative packet constraints.

Examples:

- stop on scope expansion;
- stop on missing authority;
- stop on baseline mismatch;
- stop on required context mismatch;
- stop if a workspace capability would exceed the packet;
- stop if protected verification authority is missing.

Hard-stop presence is not itself enforcement; Phase 3/2.4 enforce applicable constraints.

---

## 30. Declarative runtime requirements

Reuse accepted Slice 2.1 values.

A WorkPacket may carry:

```text
required_runtime_capabilities: tuple[RuntimeCapability, ...]
runtime_selection_requirement: RuntimeSelection | None
runtime_limits: RuntimeExecutionLimits
runtime_permission_profile_ref: RuntimePermissionProfileRef | None
credential_refs: tuple[CredentialRef, ...]
```

Semantics:

- these are requirements/refs only;
- no runtime session is created;
- no provider/model call occurs;
- requested provider/model does not establish actual provider/model;
- actual runtime provenance remains Slice 2.1 execution evidence;
- credential refs never contain secrets;
- availability of a credential does not grant permission to use it.

---

## 31. Declarative workspace requirements

Slice 2.3 must not define filesystem enforcement.

Minimum reference-only value:

```python
WorkspacePolicyRef(
    policy_key,
    content_digest,
)
```

A WorkPacket may also carry stable required workspace-property keys.

Examples of future properties:

- exact repository source;
- bounded write surface;
- network policy;
- tool policy;
- protected-asset policy;
- resource constraints.

Slice 2.4 gives these properties executable meaning and enforcement.

Slice 2.3 only binds the exact requirement set.

---

## 32. Protected verification transport

Protected verification semantics remain policy/RoleContract owned.

Slice 2.3 may transport:

```python
ProtectedVerificationRequirement(
    artifact: Artifact,
    required_operation: VerificationAssetPermission,
    separate_authority_ref: AuthorityBasisRef | None,
)
```

Rules:

- READ does not imply MODIFY;
- MODIFY does not imply APPROVE_MUTATION;
- EVALUATE does not imply mutation authority;
- presence of `separate_authority_ref` does not prove it current/valid;
- required mutation/approval authority status is evaluated externally;
- Slice 2.4 later enforces concrete paths/tools.

---

## 33. WorkPacket normative shape

Conceptual schema-v1:

```python
WorkPacket(
    schema_version: Literal[1],
    packet_key: WorkPacketKey,
    revision: int >= 1,

    project_id: ProjectId,
    slice_definition_ref: SliceDefinitionRef,
    source_baseline: Baseline,

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

Exact implementation may factor small shared reference values into a separate module, but must preserve this semantic boundary.

---

## 34. WorkPacket structural invariants

A schema-v1 WorkPacket must satisfy:

- source_baseline.project_id == project_id;
- source_baseline commit repository is the governed project repository established externally;
- slice_definition_ref.slice_id is the packet's exact Slice;
- normalized intent is COMPLETE;
- normalized intent issues are empty;
- authority_refs nonempty for governed executable work;
- authority refs unique/canonical;
- accepted design artifact refs unique/canonical;
- required context keys unique/canonical;
- evidence keys unique;
- deliverable keys unique;
- hard-stop keys unique;
- runtime capabilities unique/canonical by enum declaration order;
- credential IDs unique;
- workspace property keys unique/canonical;
- protected-verification requirements unique by exact artifact/operation;
- governance_profile_ref required only when external policy says required;
- no floating-point normative fields;
- all strings bounded and nonblank;
- no secret-bearing field.

Structural validity still does not establish authority.

---

## 35. Canonical serialization

ContextManifest and WorkPacket use the accepted Relay deterministic JSON style:

```text
UTF-8
JSON object
sort_keys = true
separators = (",", ":")
ensure_ascii = false
allow_nan = false
no floating-point normative values
schema_version = 1
```

Digest:

`sha256:<64 lowercase hex>`

Every normative field is included.

Display-only commentary, if ever added, must be explicitly non-normative and excluded by design; schema-v1 should avoid display-only fields entirely.

---

## 36. ContextManifest canonicality

Schema-v1 requires:

- entries sorted by entry_key;
- unique entry keys;
- stable source-kind enum order where tuples use enums;
- no duplicate exact source identity under conflicting digests;
- no duplicate source locator/version with conflicting provenance;
- project/slice definition exact identity embedded;
- manifest canonical digest recomputable without network access.

Any canonicality failure is invalid, not auto-reordered.

---

## 37. WorkPacket canonicality

Schema-v1 requires canonical tuple ordering.

Implementation must reject noncanonical input rather than silently sort it.

Canonical ordering keys:

```text
authority refs: authority_type + authority_key
accepted artifacts: path + artifact_id
required context keys: lexical
evidence requirements: key
deliverable requirements: key
hard stops: key
runtime capabilities: enum declaration order
credential refs: credential_id
workspace property keys: lexical
protected verification requirements:
  artifact.path + artifact.id + required_operation
```

This preserves stable identity and makes accidental reordering visible at construction time.

---

## 38. WorkPacketRef

```python
WorkPacketRef(
    project_id,
    slice_id,
    packet_key,
    revision,
    content_digest,
)
```

A ref proves only exact packet content identity.

It does not prove:

- packet authority;
- packet currentness;
- packet acceptance;
- actor binding;
- runtime suitability;
- workspace enforceability;
- lifecycle state.

---

## 39. ContextManifestRef

```python
ContextManifestRef(
    project_id,
    slice_id,
    manifest_key,
    revision,
    content_digest,
)
```

A WorkPacket's ContextManifestRef must match the exact manifest supplied to evaluation.

Manifest A cannot satisfy Packet B merely because keys/revisions are similar.

---

## 40. Identity conflict semantics

Within one exact external governed authority/policy basis:

```text
(project_id, slice_id, packet_key, revision)
    -> exactly one WorkPacket digest

(project_id, slice_id, manifest_key, revision)
    -> exactly one ContextManifest digest
```

Different digests for the same identity tuple:

```text
WORK_PACKET_IDENTITY_CONFLICT
CONTEXT_MANIFEST_IDENTITY_CONFLICT
INDETERMINATE / STOP
```

No latest/newest fallback.

---

## 41. Amendment semantics

Changing any normative WorkPacket field requires:

- new packet revision;
- new packet digest;
- new exact WorkPacketRef;
- new/external authority applicability decision for the new exact subject.

Changing ContextManifest normative content requires:

- new manifest revision;
- new manifest digest;
- WorkPacket amendment if the packet is to consume that new manifest.

An old authority binding may not be silently reused for a changed packet.

---

## 42. External conformance facts

Slice 2.3 evaluates supplied facts; it does not fetch governance state.

Conceptual:

```python
WorkPacketConformanceFacts(
    slice_definition_status: RequirementStatus,
    source_baseline_status: RequirementStatus,
    authority_basis_status: RequirementStatus,
    policy_basis_status: RequirementStatus,
    governance_profile_status: RequirementStatus,
    role_contract_applicability: RoleContractApplicability,
    accepted_design_basis_status: RequirementStatus,
    context_manifest_status: RequirementStatus,
    protected_verification_authority_status: RequirementStatus,
)
```

Facts are established by the appropriate external governance/control layer.

No boolean in this fact object is a grant of authority; it is evidence consumed by conformance evaluation.

---

## 43. Conformance status

Reuse Slice 2.2 `RequirementStatus`:

```text
SATISFIED
UNSATISFIED
INDETERMINATE
```

Rules:

- positively incompatible exact fact -> UNSATISFIED;
- missing/stale/conflicting/unverifiable required fact -> INDETERMINATE;
- all required structural and supplied facts established -> SATISFIED.

Normative statement:

```text
WorkPacket conformance SATISFIED != AUTHORIZED
```

Execution admission remains a Phase 3 conjunction.

---

## 44. Context conformance

Context evaluation compares exact WorkPacket requirements with the exact supplied ContextManifest.

Minimum checks:

- exact ContextManifestRef digest match;
- exact project match;
- exact SliceDefinitionRef match;
- every required context key present once;
- every required entry content/provenance exact;
- repository entries use the expected source baseline where the requirement says they must;
- no identity conflict;
- no unresolved mutable alias;
- no required unverifiable source.

Missing required entry -> INDETERMINATE.

Known wrong digest/ref -> UNSATISFIED.

---

## 45. Normalized-intent conformance

A WorkPacket is structurally conforming only with:

```text
NormalizationStatus.COMPLETE
issues == ()
```

INCOMPLETE/INDETERMINATE intent cannot be promoted to packet conformance by adding authority refs.

Authority does not repair ambiguous content.

A Human clarification must produce a new exact normalized intent before packet creation/amendment.

---

## 46. Scope conflict semantics

Known contradiction among:

- exact Slice definition;
- normalized intent;
- external authority subject;
- WorkPacket declarative constraints;

is:

```text
WORK_SCOPE_CONFLICT
UNSATISFIED / STOP
```

Missing ability to determine compatibility is:

```text
WORK_SCOPE_INDETERMINATE
INDETERMINATE / STOP
```

No model/runtime may choose the broader interpretation.

---

## 47. Slice 2.2 input-requirement mapping

Slice 2.3 transports existing RoleInputRequirement semantics as follows.

| RoleInputRequirement | Slice 2.3 transport / boundary |
| --- | --- |
| ACTOR_IDENTITY_BINDING | execution-time external fact; not satisfied by packet |
| APPLICABLE_ROLE_CONTRACT_BINDING | exact RoleContractRef + external RoleContractApplicability |
| GOVERNANCE_PROFILE_BINDING | exact GovernanceProfileRef + external currentness/applicability |
| AUTHORIZED_WORK_BASIS | exact AuthorityBasisRef tuple + external validity/currentness |
| SOURCE_BASELINE | exact embedded Baseline |
| ACCEPTED_DESIGN_BASIS | exact accepted Artifact refs + external acceptance/currentness |
| EVALUATION_SUBJECT | evaluator WorkPacket normalized intent / subject refs; actor/evaluation binding external |
| EVIDENCE_BASIS | ContextManifest/evidence/artifact refs |
| DECISION_BASIS | exact governance/Human-decision refs when required |
| PROMOTION_BASIS | exact promotion/authority/design/evidence refs when required |
| RUNTIME_EXECUTION_BASIS | not satisfied until Phase 3 creates exact RuntimeExecutionBasis |

Slice 2.3 does not mark an execution-time requirement SATISFIED merely because it can transport related references.

---

## 48. Slice 2.2 output-requirement mapping

| RoleOutputRequirement | Packet contract |
| --- | --- |
| ENGINEERING_RESULT | deliverable requirement |
| EXECUTION_EVIDENCE | evidence requirement |
| EVALUATION_JUDGMENT | deliverable/evidence requirement for evaluator packets |
| HUMAN_DECISION | external Human decision deliverable/reference only; packet cannot create it |
| PROMOTION_EVIDENCE | evidence requirement for promotion packets |
| WORK_DISPOSITION | deliverable/evidence requirement using accepted Slice 2.2 disposition vocabulary |

Output requirement presence does not establish output completion.

---

## 49. Protected verification conformance

Packet conformance must never infer mutation authority from:

- RoleContract permission alone;
- asset presence;
- evaluator role;
- workspace write access;
- credential availability.

For protected MODIFY/APPROVE_MUTATION, a required separate authority ref/status remains mandatory when policy requires it.

Unknown/stale/conflicting authority -> INDETERMINATE.

Known absent required authority -> UNSATISFIED.

---

## 50. Runtime requirement boundary

A conforming WorkPacket can declare runtime requirements.

It cannot prove a runtime satisfies them.

Phase 3/Slice 2.1 later compare:

- required RuntimeCapability;
- requested RuntimeSelection;
- runtime permission profile;
- credential refs;
- limits;

against actual runtime capability/provenance.

Actual provider/model identity remains observed evidence, never packet inference.

---

## 51. Workspace requirement boundary

A conforming WorkPacket can declare exact workspace policy/property refs.

It cannot prove they are enforceable.

Slice 2.4 later resolves/enforces those requirements.

If Slice 2.4 cannot establish enforcement for a required property:

`STOP`

No fallback to "best effort" workspace access.

---

## 52. Runtime input / prompt boundary

A runtime prompt/input is a projection of an exact WorkPacket + exact ContextManifest.

It is not the governed source of truth.

Phase 3 may later define a deterministic rendering/materialization function that produces `RuntimeInputPayload`.

Normative relationship:

```text
WorkPacketRef
+ ContextManifestRef
+ exact renderer/version/policy
    -> RuntimeInputPayload

RuntimeInputPayload
    != WorkPacket
    != authority
```

Prompt/provider formatting cannot add scope, acceptance criteria, authority, or hidden context.

---

## 53. Authorized successor transport

Slice 2.3 may carry:

```python
authorized_successor_ref: WorkPacketRef | None
```

This field is valid only when external governance has already established the successor under Slice 2.2 `AUTHORIZED_SUCCESSOR_ESTABLISHED`.

Rules:

- current execution still stops;
- successor gets a separate WorkPacket/execution;
- current actor does not inherit authority;
- successor ref alone does not authorize successor execution;
- absent successor ref does not prove NO_AUTHORIZED_SUCCESSOR.

---

## 54. BACKLOG_EXHAUSTED preservation

Slice 2.3 does not derive BACKLOG_EXHAUSTED from an empty successor field.

Only external durable governance may establish:

`NO_AUTHORIZED_SUCCESSOR`

which Slice 2.2 maps to:

`BACKLOG_EXHAUSTED`

If successor state cannot be determined:

`ESCALATION_REQUIRED / STOP`

No WorkPacket field changes this rule.

---

## 55. PROPOSED_WORK preservation

Planning normalization may reveal future work.

That future work remains:

`PROPOSED_WORK`

until separately accepted/authorized by governance.

It must not appear as `authorized_successor_ref` unless independent authority already exists.

The packet layer does not maintain a backlog.

---

## 56. Refusal / reason vocabulary

Minimum Slice 2.3 reasons:

```text
WORK_PACKET_IDENTITY_CONFLICT
CONTEXT_MANIFEST_IDENTITY_CONFLICT
WORK_PACKET_REF_MISMATCH
CONTEXT_MANIFEST_REF_MISMATCH

SLICE_DEFINITION_MISSING
SLICE_DEFINITION_STALE
SLICE_DEFINITION_CONFLICT
SOURCE_BASELINE_MISSING
SOURCE_BASELINE_STALE
SOURCE_BASELINE_CONFLICT

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

ACCEPTED_DESIGN_BASIS_MISSING
ACCEPTED_DESIGN_BASIS_STALE
PROTECTED_VERIFICATION_AUTHORITY_REQUIRED
PROTECTED_VERIFICATION_AUTHORITY_INDETERMINATE

REQUIRED_EVIDENCE_CONTRACT_MISSING
REQUIRED_DELIVERABLE_CONTRACT_MISSING
SUCCESSOR_REFERENCE_NOT_AUTHORITY
```

Exact naming may be refined during implementation review, but semantic distinctions are normative.

---

## 57. Evaluation precedence

Overall conformance:

```text
known incompatible/invalid required condition
    -> UNSATISFIED

else any missing/stale/conflicting/unverifiable/unknown required condition
    -> INDETERMINATE

else
    -> SATISFIED
```

SATISFIED means the packet contract is conforming to supplied facts.

It does not mean executable.

---

## 58. Execution-admission composition

Future Phase 3 admission is conjunctive:

```text
exact WorkPacket ref resolves
AND WorkPacket conformance == SATISFIED
AND exact ContextManifest ref resolves
AND RoleContract applicability == APPLICABLE
AND role action eligibility == PERMITTED_BY_ROLE
AND actor binding is established
AND exact current work authority passes
AND required role separation passes
AND Slice 2.4 workspace policy is enforceable/enforced
AND Slice 2.1 runtime capabilities/provenance satisfy requirements
AND protected-verification constraints pass
    -> orchestration may admit execution
```

No individual predicate implies another.

---

## 59. No implicit repository context

The entire repository is not implicitly governed context merely because a workspace exists.

The packet/context contract distinguishes:

- source baseline: exact repository commit;
- selected effective context: exact referenced content;
- workspace visibility: later execution capability.

An agent may physically see more files than the ContextManifest enumerates.

Physical visibility does not broaden governed decision context or authority.

Slice 2.4/Phase 3 may later restrict visibility further.

---

## 60. Context minimization

A WorkPacket should include the minimum sufficient context needed for the authorized work.

This is both a reproducibility and quality requirement.

Do not treat "include everything" as a deterministic solution.

Context selection must remain:

- explicit;
- reviewable;
- digest-bound;
- source-provenanced.

General semantic retrieval systems may be added later only with separately accepted requirements.

---

## 61. Reproducibility definition

A WorkPacket is reproducible when an independent consumer can establish:

- exact WorkPacket bytes/digest;
- exact ContextManifest bytes/digest;
- exact source baseline;
- exact selected context content/provenance;
- exact normalized planning source/provenance;
- exact role/policy/profile/authority refs;
- exact declarative requirements;

without relying on prior conversation state or mutable aliases.

Reproducibility does not require that an external URL remain live if the exact consumed content snapshot/digest is preserved.

---

## 62. Initial implementation architecture

A later implementation authority should prefer one bounded package:

```text
src/relay_engine/work_packets/
  __init__.py
  models.py
  evaluation.py
```

No initial persistence layer.

No CLI.

No UI.

No network adapter.

No provider adapter.

No runtime invocation.

No workspace enforcement.

---

## 63. Expected models.py responsibility

Likely schema-v1 values:

```text
WorkPacketKey
ContextManifestKey
ContextEntryKey
StableRequirementKey

SliceDefinitionRef
AuthorityReferenceType
AuthorityBasisRef
PolicyBasisRef
GovernanceProfileRef

ContextClass
ContextSourceKind
ContextSourceRef
ContextEntryRef
ContextManifest
ContextManifestRef

PlanningArtifactSourceRef
PlanningAdapterRef
NormalizationStatus
NormalizationIssueCode
NormalizationIssue
NormalizedEngineeringIntent

EvidenceRequirement
DeliverableRequirement
HardStopRequirement
WorkspacePolicyRef
ProtectedVerificationRequirement

WorkPacket
WorkPacketRef

WorkPacketReason
WorkPacketConformance
WorkPacketConformanceFacts
IdentityConflict results
```

Exact implementation may reduce the number of named models if semantics remain explicit and testable.

---

## 64. Expected evaluation.py responsibility

Pure deterministic functions only:

```text
canonical_context_manifest_json
digest_context_manifest
context_manifest_ref
context_manifest_ref_matches

canonical_work_packet_json
digest_work_packet
work_packet_ref
work_packet_ref_matches

evaluate_context_manifest_identity_conflicts
evaluate_work_packet_identity_conflicts

evaluate_context_conformance
evaluate_work_packet_conformance
```

No database access.

No filesystem reads.

No network.

No AgentRuntime calls.

No workspace mutation.

No authority issuance.

---

## 65. Existing production modules not modified by default

Initial implementation should not require changes to:

```text
src/relay_engine/domain/ids.py
src/relay_engine/domain/models.py
src/relay_engine/domain/references.py
src/relay_engine/governance/**
src/relay_engine/role_contracts/**
src/relay_engine/agent_runtime/**
src/relay_engine/persistence/**
src/relay_engine/lifecycle/**
src/relay_engine/promotion/**
src/relay_engine/repository_sync/**
```

If implementation appears to require such changes, STOP and return the need for explicit scope review.

A behavior-preserving shared stable-key helper extraction is not assumed.

---

## 66. No migration / persistence requirement

Revision 1 requires no new database table.

Reason:

- WorkPacket/ContextManifest semantics can be proven as immutable domain values first;
- no production orchestrator consumes them yet;
- persistence design should follow an actual consumer rather than speculative schema.

Future persistence requires separate authority if/when Phase 3 or operational planning requires it.

---

## 67. Deterministic model tests

Later implementation must test at least:

### WorkPacket identity

- same packet -> same digest;
- normative change -> different digest;
- noncanonical tuples rejected;
- duplicate keys rejected;
- packet ref exact match/mismatch;
- same key/revision different digest conflict;
- no latest resolver.

### ContextManifest identity

- same manifest -> same digest;
- changed entry digest/provenance -> changed manifest digest;
- entries canonical/unique;
- manifest ref exact match/mismatch;
- same key/revision different digest conflict;
- no latest resolver.

---

## 68. Context tests

Required:

- required static entry present/exact -> SATISFIED;
- required dynamic entry present/exact -> SATISFIED;
- missing required context -> INDETERMINATE;
- known wrong digest -> UNSATISFIED;
- unverified mutable URL/branch/current-tool alias -> INDETERMINATE;
- optional context absence does not fail packet;
- session excerpt must be exact snapshot;
- repository context must bind exact CommitRef where required;
- context from another project/slice rejected.

---

## 69. Planning-normalization tests

Required:

- Relay-native exact normalized input can be COMPLETE without adapter;
- transformed external source requires exact adapter ref;
- COMPLETE with issues rejected;
- INCOMPLETE intent cannot yield conforming packet;
- ambiguous/conflicting/unverifiable source -> INDETERMINATE;
- adapter output cannot add authority;
- missing source-supported acceptance criterion cannot be invented;
- source/provenance change changes packet digest.

---

## 70. Authority tests

Required:

- packet with exact authority ref but external authority status missing -> INDETERMINATE;
- stale authority -> INDETERMINATE;
- conflicting authority -> INDETERMINATE;
- known incompatible authority subject -> UNSATISFIED;
- packet digest alone never yields authorization;
- WorkPacket constructor cannot issue authority;
- Human root authority is external.

---

## 71. Role-contract mapping tests

Required:

- exact RoleContractRef transported;
- role applicability missing/unknown -> packet conformance INDETERMINATE;
- NOT_APPLICABLE -> UNSATISFIED;
- APPLICABLE can satisfy packet role-reference conformance only;
- ACTOR_IDENTITY_BINDING remains execution-time external;
- RUNTIME_EXECUTION_BASIS remains unsatisfied until Phase 3 creates exact basis;
- output requirements remain requirements, not completed outputs.

---

## 72. Runtime/workspace tests

Required:

- required RuntimeCapability tuple canonical/unique;
- requested provider/model requirement remains declarative;
- packet cannot report actual provider/model;
- credential refs contain identifiers only;
- runtime requirement presence does not invoke runtime;
- workspace policy ref does not enforce paths;
- no filesystem/network/tool permission check is implemented by 2.3;
- no 2.4 capability is imported as execution machinery.

---

## 73. Protected-verification tests

Required:

- protected asset READ requirement does not imply MODIFY;
- MODIFY/APPROVE reference requires separate authority when policy facts say required;
- authority ref presence without external currentness is insufficient;
- evaluator role does not grant mutation authority;
- workspace write capability does not grant protected mutation authority.

---

## 74. Amendment tests

Required:

- changing normative packet content requires new digest;
- same packet key/revision with changed digest -> identity conflict;
- new packet revision cannot automatically reuse old authority applicability;
- context-manifest amendment changes packet digest when packet points to new ref;
- no-op revision under supplied previous ref is rejected;
- no latest/newest fallback.

---

## 75. Successor tests

Required:

- authorized successor ref transport does not authorize current or successor execution;
- successor ref allowed only with externally established authorized-successor fact;
- empty successor ref does not imply BACKLOG_EXHAUSTED;
- NO_AUTHORIZED_SUCCESSOR external fact maps using Slice 2.2 semantics;
- SUCCESSOR_NOT_DETERMINABLE remains escalation;
- PROPOSED_WORK cannot populate authorized successor ref.

---

## 76. Static architecture tests

Later implementation must prove:

- no new DB migration/table;
- no new UUID prefix;
- no network calls;
- no provider/model calls;
- no AgentRuntime invocation;
- no workspace mutation;
- no lifecycle mutation;
- no Human authority creation;
- no repository promotion;
- no generic RAG/vector DB;
- no external-planning adapter implementation;
- no Slice 2.4 implementation;
- no Phase 3 orchestration.

---

## 77. Acceptance-criteria traceability

| Criterion | Design coverage |
| --- | --- |
| A01 exact immutable WorkPacket identity/revision/digest | §§6, 33–41, 67 |
| A02 exact Project/Slice/baseline binding | §§7, 33–34 |
| A03 external authority/policy/profile/role refs; no authority creation | §§8–10, 42–43, 70 |
| A04 reproducible ContextManifest | §§11–19, 44, 61, 68 |
| A05 normalized intent/provenance/no invention | §§20–25, 45, 69 |
| A06 objective/scope/non-scope/acceptance/deliverable/evidence | §§24, 26–29, 33 |
| A07 Slice 2.2 input/output mapping | §§47–49, 71 |
| A08 runtime requirements declarative / Slice 2.1 reuse | §§30, 50, 72 |
| A09 workspace requirements declarative / Slice 2.4 preserved | §§31, 51, 72 |
| A10 protected verification transport cannot grant authority | §§32, 49, 73 |
| A11 amendment/new digest/renewed authority/no latest | §§40–41, 74 |
| A12 successor/proposed-work/exhaustion preserved | §§53–55, 75 |
| A13 fail closed missing/stale/conflicting/unverifiable | §§42–46, 56–57 |
| A14 no DB/RAG/orchestration/provider/2.4/Phase3 leakage | §§60, 62–66, 76 |

All fourteen authorized design criteria are covered.

---

## 78. Design risks and mitigations

### R1 — WorkPacket becomes a hidden authority token

Mitigation:

- external authority reference/currentness mandatory;
- conformance status deliberately named SATISFIED/UNSATISFIED/INDETERMINATE;
- no AUTHORIZED state;
- negative tests.

### R2 — ContextManifest becomes a general RAG system

Mitigation:

- exact refs/digests only;
- no retrieval engine;
- no vector DB;
- no ranking policy;
- no network.

### R3 — Planning normalization invents scope

Mitigation:

- explicit COMPLETE/INCOMPLETE/INDETERMINATE;
- source-supported fields only;
- ambiguity/conflict fail closed;
- Human clarification through governed decision.

### R4 — Packet duplicates RoleContract policy

Mitigation:

- exact RoleContractRef transport;
- fixed mapping to existing RoleInput/Output vocabulary;
- RoleContract remains authority-independent policy.

### R5 — Packet absorbs workspace enforcement

Mitigation:

- WorkspacePolicyRef only;
- 2.4 owns enforcement;
- static architecture tests.

### R6 — Packet absorbs runtime execution

Mitigation:

- reuse runtime requirement values only;
- no AgentRuntime import for invocation;
- Phase 3 owns execution.

### R7 — Mutable chat/tool/web context silently changes work

Mitigation:

- exact snapshot/digest required;
- no implicit chat history;
- mutable aliases fail closed.

### R8 — successor reference becomes backlog authority

Mitigation:

- externally established successor fact required;
- separate WorkPacket execution required;
- no authority inheritance;
- empty ref does not imply exhaustion.

### R9 — over-modeling creates governance overhead

Mitigation:

- content-addressed keys/revisions instead of new UUID/persistence;
- initial pure-domain package only;
- existing domain/runtime/role values reused;
- no database until a real consumer requires it.

---

## 79. Independent design-review checklist

Independent review must answer YES to all:

- WorkPacket is immutable/content-addressed;
- ContextManifest is immutable/content-addressed;
- no latest/best-match lookup exists;
- packet cannot manufacture authority;
- Human root authority remains external;
- exact Project/Slice/baseline identity is bound;
- exact RoleContractRef is transported;
- policy/profile selection remains external;
- ContextManifest represents exact effective context rather than prompt text;
- required context is fail-closed;
- mutable aliases cannot satisfy required context;
- session/chat context must be explicitly snapshotted;
- planning normalization is provider-neutral;
- adapter output cannot invent authority/scope/acceptance;
- incomplete/ambiguous normalization fails closed;
- scope/non-scope/acceptance are explicit;
- evidence/deliverable requirements are explicit;
- Slice 2.2 input/output semantics are transported, not duplicated;
- runtime requirements reuse Slice 2.1;
- workspace enforcement remains 2.4;
- protected-verification authority remains separate;
- changed packet/context requires new digest/revision;
- changed packet requires renewed external authority applicability;
- successor ref does not inherit authority;
- empty successor ref does not imply BACKLOG_EXHAUSTED;
- no DB migration/persistence required initially;
- no RAG/provider/runtime/workspace/orchestration scope leakage;
- implementation architecture is small and deterministic.

Any NO requires REWORK or ESCALATE.

---

## 80. Design disposition

```text
RLY-S23-DESIGN-AUTH-001 — AUTHORIZED

Slice 2.3:
OPEN

Design Revision 1:
COMPLETE / READY FOR INDEPENDENT DESIGN REVIEW

Implementation:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Production WorkPacket creation/wiring:
NOT AUTHORIZED

Runtime/provider/model execution:
NOT AUTHORIZED

Workspace enforcement:
NOT AUTHORIZED — Slice 2.4

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

**Design complete != design accepted. Design accepted != implementation authorized.**
