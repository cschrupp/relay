# Slice 2.3 — Context / Work-Packet Contract — Design Revision 2 Amendment

**Document class:** Lockable design amendment  
**Status:** REWORK COMPLETE — READY FOR INDEPENDENT RE-REVIEW  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Document revision:** 2 Amendment  
**Original design authority:** `RLY-S23-DESIGN-AUTH-001 — AUTHORIZED`  
**Rework authority:** `RLY-S23-DESIGN-REWORK-AUTH-001 — AUTHORIZED`  
**Rework-authority commit:** `ff37525222215f2a64c833d77c5d2a8779ac7509`  
**Revises:** Design Revision 1 at `8e3cb2df658711cd3e18d364cf19fa5332b2ab2f`  
**Responds to:** `RLY-S23-DESIGN-EVAL-001 — REWORK`  
**Evaluation commit:** `f0383fe624e99134586198cfcb9be77aae2fb014`  
**Implementation authorization:** NOT GRANTED

Revision 2 is normative over Revision 1 where they differ. All Revision 1 decisions not changed here remain in force.

---

## 1. Rework disposition

```text
F001 exact-subject-bound conformance evidence          RESOLVED
F002 recursive canonical identity                     RESOLVED
F003 deterministic required-context materialization   RESOLVED

IR clarification:
mirrored control-plane context must exact-match packet control refs
                                                      ADOPTED
```

The amendment preserves Revision 1's architecture:

- WorkPacket != authority;
- ContextManifest != authority;
- Human root authority remains external;
- provider-neutral planning normalization;
- Slice 2.2 RoleContract semantics are reused;
- Slice 2.1 runtime ownership remains intact;
- Slice 2.4 workspace enforcement remains intact;
- Phase 3 orchestration remains intact;
- no DB migration or persistence;
- no RAG/vector DB;
- no provider/runtime calls;
- no workspace mutation;
- no lifecycle mutation;
- no new WorkPacket/ContextManifest UUID prefix.

---

# Part I — F001: Exact-subject-bound conformance evidence

## 2. Design principle

External conformance evidence is valid only for the exact subject it attests.

The following is now a normative invariant:

```text
fact/evaluation for subject A
    !=
fact/evaluation for subject B
```

A status value such as `SATISFIED`, `UNSATISFIED`, `INDETERMINATE`, or `APPLICABLE` is never sufficient by itself.

Every externally supplied fact consumed by Slice 2.3 must carry an exact subject binding.

This mirrors the accepted Slice 2.2 rule:

```text
RoleApplicabilityEvaluation
must bind the exact RoleContractRef it evaluates.
```

---

## 3. SourceBaselineRef replaces embedded Baseline in WorkPacket

Revision 1 embedded the complete existing `Baseline` object in WorkPacket.

Revision 2 replaces that field with an exact digest-bound reference:

```python
SourceBaselineRef(
    baseline_id: BaselineId,
    project_id: ProjectId,
    commit: CommitRef,
    content_digest: ContentDigest,
)
```

`content_digest` is the digest of the exact canonical existing `Baseline` value after the canonicality rules in Part II are applied.

The ref therefore binds:

- exact BaselineId;
- exact ProjectId;
- exact repository/commit;
- exact authoritative artifact-id tuple;
- exact authoritative decision-id tuple.

The WorkPacket field becomes:

```python
source_baseline_ref: SourceBaselineRef
```

This is a reference-only correction. It does not create a second baseline identity system or alter the existing `Baseline` model.

---

## 4. ExactRefRequirementFact

Revision 2 introduces a conceptual reusable fact shape:

```python
ExactRefRequirementFact[T](
    evaluated_ref: T,
    status: RequirementStatus,
)
```

The exact implementation does not need Python generics if a small explicit model is clearer.

Normative semantics:

- `evaluated_ref` identifies the exact subject;
- `status` reports only that subject;
- known wrong subject/ref -> `UNSATISFIED`;
- missing/stale/conflicting/unverifiable currentness -> `INDETERMINATE`;
- callers may not substitute a fact for a different exact ref.

---

## 5. AuthorityBasisFact

Authority facts are per exact authority reference:

```python
AuthorityBasisFact(
    evaluated_ref: AuthorityBasisRef,
    status: RequirementStatus,
)
```

The fact tuple must contain exactly one fact for every WorkPacket `authority_ref`, in the same canonical order.

No missing fact.

No extra fact.

No fact for a semantically similar or superseding authority unless the WorkPacket itself is amended to that exact authority ref.

```text
authority set A status
    cannot satisfy
authority set B
```

---

## 6. PolicyBasisFact

```python
PolicyBasisFact(
    evaluated_ref: PolicyBasisRef,
    status: RequirementStatus,
)
```

The exact ref must equal the WorkPacket's `policy_basis_ref`.

Different policy key/version/digest/effective-scope digest invalidates the fact for that packet.

---

## 7. GovernanceProfileFact

Profile applicability is bound to the exact PolicyBasisRef.

Conceptually:

```python
GovernanceProfileFact(
    evaluated_policy_basis_ref: PolicyBasisRef,
    evaluated_profile_ref: GovernanceProfileRef | None,
    profile_requirement_status: RequirementStatus,
    profile_status: RequirementStatus,
)
```

Rules:

### Packet carries GovernanceProfileRef

Then:

- `evaluated_policy_basis_ref == packet.policy_basis_ref`;
- `evaluated_profile_ref == packet.governance_profile_ref`;
- profile requirement must be positively established;
- profile status must be `SATISFIED`.

### Packet carries no GovernanceProfileRef

Then:

- exact PolicyBasisRef still must match;
- `evaluated_profile_ref is None`;
- `profile_requirement_status == SATISFIED` means external policy positively established that no profile is required;
- missing/unknown requirement status -> `INDETERMINATE`.

Absence of a profile ref never means "not required" by default.

---

## 8. Role applicability uses the accepted exact-ref-bound Slice 2.2 result

Revision 1's raw:

```text
role_contract_applicability: RoleContractApplicability
```

is replaced.

Revision 2 requires the accepted Slice 2.2 exact result:

```python
role_contract_applicability: RoleApplicabilityEvaluation
```

Conformance requires:

```text
role_contract_applicability.role_contract_ref
    == packet.role_contract_ref
```

and:

```text
role_contract_applicability.status == APPLICABLE
```

A result for RoleContract A cannot satisfy a packet carrying RoleContract B.

---

## 9. AcceptedDesignFact

Accepted design evidence is per exact Artifact.

```python
AcceptedDesignFact(
    evaluated_artifact: Artifact,
    status: RequirementStatus,
)
```

The fact tuple must match the WorkPacket's canonical `accepted_design_artifacts` tuple exactly by:

- ArtifactId;
- path;
- CommitRef;
- ContentDigest;
- artifact type.

A status for another revision/path/commit/digest cannot satisfy the packet.

---

## 10. ContextManifestFact

```python
ContextManifestFact(
    evaluated_ref: ContextManifestRef,
    status: RequirementStatus,
)
```

The exact evaluated ref must equal:

`packet.context_manifest_ref`

and the separately supplied exact ContextManifest must itself resolve to that ref.

A fact for Manifest A cannot satisfy Packet B pointing to Manifest B.

---

## 11. ProtectedVerificationAuthorityFact

Protected-verification authority evidence becomes exact per packet requirement.

First define a stable exact requirement identity:

```python
ProtectedVerificationRequirementRef(
    artifact_id: ArtifactId,
    artifact_content_digest: ContentDigest,
    required_operation: VerificationAssetPermission,
    requirement_digest: ContentDigest,
)
```

The `requirement_digest` covers the complete canonical `ProtectedVerificationRequirement`, including any required separate authority ref.

External fact:

```python
ProtectedVerificationAuthorityFact(
    evaluated_requirement_ref: ProtectedVerificationRequirementRef,
    evaluated_authority_ref: AuthorityBasisRef | None,
    status: RequirementStatus,
)
```

Rules:

- exact requirement ref must match one packet requirement;
- if packet requirement names a separate authority ref, fact must name the same exact authority ref;
- authority for another asset or another operation cannot satisfy the requirement;
- READ authority cannot satisfy MODIFY;
- MODIFY cannot satisfy APPROVE_MUTATION;
- evaluator identity/capability cannot substitute the fact.

---

## 12. WorkPacketConformanceFacts Revision 2

Revision 1 §42 is replaced by:

```python
WorkPacketConformanceFacts(
    evaluated_work_packet_ref: WorkPacketRef,
    evaluated_context_manifest_ref: ContextManifestRef,

    slice_definition_fact:
        ExactRefRequirementFact[SliceDefinitionRef],

    source_baseline_fact:
        ExactRefRequirementFact[SourceBaselineRef],

    authority_facts:
        tuple[AuthorityBasisFact, ...],

    policy_basis_fact:
        PolicyBasisFact,

    governance_profile_fact:
        GovernanceProfileFact,

    role_contract_applicability:
        RoleApplicabilityEvaluation,

    accepted_design_facts:
        tuple[AcceptedDesignFact, ...],

    context_manifest_fact:
        ContextManifestFact,

    protected_verification_authority_facts:
        tuple[ProtectedVerificationAuthorityFact, ...],

    materialization_facts:
        tuple[ContextMaterializationFact, ...],
)
```

No aggregate status may stand in for an exact plural subject set.

---

## 13. Exact-set equality rules

Before evaluating statuses, `evaluate_work_packet_conformance()` must establish exact subject equality.

Normative preconditions:

```text
facts.evaluated_work_packet_ref
    == exact WorkPacketRef(packet)

facts.evaluated_context_manifest_ref
    == packet.context_manifest_ref

facts.slice_definition_fact.evaluated_ref
    == packet.slice_definition_ref

facts.source_baseline_fact.evaluated_ref
    == packet.source_baseline_ref

facts.authority_facts refs
    == packet.authority_refs

facts.policy_basis_fact.evaluated_ref
    == packet.policy_basis_ref

facts governance-profile subject
    == exact packet policy/profile subject

facts.role_contract_applicability.role_contract_ref
    == packet.role_contract_ref

facts.accepted_design_facts artifacts
    == packet.accepted_design_artifacts

facts.protected-verification facts
    == exact packet protected-verification requirements
       that require separate authority evaluation

facts.materialization_facts
    == exact required material refs from the supplied ContextManifest
```

All plural comparisons are exact canonical tuple equality after validation.

Mismatch is not "close enough".

---

## 14. F001 status semantics

If exact subject/ref equality fails because the supplied fact is positively for another subject:

```text
UNSATISFIED
```

If a required exact fact is absent, stale, conflicting, or cannot be established:

```text
INDETERMINATE
```

No mismatched exact fact can return `SATISFIED`.

---

## 15. F001 refusal reasons

Revision 2 adds:

```text
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
```

Exact implementation naming may be tightened, but the distinctions are normative.

---

## 16. F001 required tests

Implementation authorization must require:

```text
facts for Packet A cannot satisfy Packet B
changing packet revision/digest invalidates old facts
changing ContextManifestRef invalidates old facts
changing SliceDefinitionRef invalidates old facts
changing SourceBaselineRef invalidates old facts
changing one authority ref invalidates old authority fact set
missing one authority fact -> INDETERMINATE
extra authority fact -> mismatch / fail closed
policy fact for policy A cannot satisfy policy B
profile fact for profile A cannot satisfy profile B
no profile ref + no exact not-required fact -> INDETERMINATE
RoleApplicabilityEvaluation for RoleContract A cannot satisfy B
accepted-design fact set A cannot satisfy set B
protected-verification authority for asset/operation A cannot satisfy B
materialization facts for Manifest A cannot satisfy Manifest B
```

**F001: RESOLVED BY DESIGN.**

---

# Part II — F002: Recursive canonical identity

## 17. Canonicality rule is recursive

Revision 1's canonical JSON rules remain in force.

Revision 2 adds:

> Every normative collection reachable from a WorkPacket or ContextManifest must have an explicit ordering semantic.

For each collection exactly one of these applies:

```text
ORDER-NORMATIVE
or
ORDER-NON-SEMANTIC / CANONICAL
```

### ORDER-NORMATIVE

Order changes meaning.

Different order intentionally changes the canonical bytes/digest.

### ORDER-NON-SEMANTIC / CANONICAL

Order does not change meaning.

One exact canonical order is mandatory.

Noncanonical input is rejected; constructors/evaluators do not silently sort.

---

## 18. Baseline canonicality

The existing `Baseline` model remains unchanged.

For purposes of `SourceBaselineRef.content_digest`, Slice 2.3 defines canonical baseline validation:

```text
Baseline.artifact_ids:
ORDER-NON-SEMANTIC / CANONICAL
lexicographically ascending by ArtifactId
unique

Baseline.decision_ids:
ORDER-NON-SEMANTIC / CANONICAL
lexicographically ascending by DecisionId
unique
```

The remaining Baseline object fields are scalar/object fields.

Canonical baseline serialization uses the same schema-v1 JSON rules as WorkPacket.

If a supplied Baseline has noncanonical artifact/decision tuples, Slice 2.3 refuses to compute an admissible `SourceBaselineRef`.

This does not modify `relay_engine.domain.Baseline`.

---

## 19. NormalizedEngineeringIntent canonicality

Revision 1 §24 is amended.

### source_refs

```text
ORDER-NON-SEMANTIC / CANONICAL
sort key:
(source_type, source_key, source_version-or-empty,
 content_digest, provenance_digest)
unique exact source identity
```

### ScopeSpec.in_scope

```text
ORDER-NON-SEMANTIC / CANONICAL
lexicographic UTF-8 order
unique exact strings
```

### ScopeSpec.out_of_scope

Same rule as `in_scope`.

A statement cannot appear in both in-scope and out-of-scope.

### acceptance_criteria

```text
ORDER-NON-SEMANTIC / CANONICAL
sort by AcceptanceCriterion.key
keys unique
```

Criterion statement/required flag are normative content.

### dependency_slice_ids

```text
ORDER-NON-SEMANTIC / CANONICAL
lexicographic SliceId order
unique
```

### quality_requirement_keys

```text
ORDER-NON-SEMANTIC / CANONICAL
lexicographic stable-key order
unique
```

### issues

A WorkPacket-admissible `NormalizedEngineeringIntent` must have:

```text
status == COMPLETE
issues == ()
```

Therefore issues are not reachable in a conforming WorkPacket digest.

If the implementation exposes standalone canonical serialization for incomplete/indeterminate intent, issue tuples must be canonical by:

```text
(issue_code, field_key, source_key-or-empty)
```

with exact duplicate issue tuples rejected.

---

## 20. PlanningArtifactSourceRef canonical fields

All normative fields are scalar.

If a source reference later gains a collection field, that schema change must explicitly classify its ordering before it can enter a WorkPacket digest.

This prevents hidden future array nondeterminism.

---

## 21. ContextMaterialRef canonicality

Revision 2 adds material refs in Part III.

All material-ref variants use scalar fields plus exact nested objects without unordered collections.

Where a material-bundle reference later contains an entry tuple, entries must be canonical by material key/ref identity.

No implementation may introduce an unordered normative map/list into a digest path without an explicit rule.

---

## 22. ContextManifest canonicality

Revision 1 remains:

```text
entries:
ORDER-NON-SEMANTIC / CANONICAL
sort by entry_key
entry_key unique
```

Revision 2 adds:

- source/material-ref fields are fully normative;
- `control_mirror_binding`, when present, is normative;
- exact material ref changes manifest digest;
- exact control-mirror binding changes manifest digest.

There is no hidden mutable material source outside the manifest identity.

---

## 23. WorkPacket top-level canonicality

Revision 1 §37 remains and is clarified:

### authority_refs

Canonical:

```text
(authority_type, authority_key, record_digest, subject_digest-or-empty)
```

### accepted_design_artifacts

Canonical:

```text
(path, artifact_id, commit.sha, content_digest)
```

### required_context_keys

Lexical.

### evidence_requirements

By key.

### deliverable_requirements

By key.

### hard_stops

By key.

### runtime capabilities

Enum declaration order.

### credential refs

By credential_id.

### required workspace property keys

Lexical.

### protected verification requirements

Canonical:

```text
(artifact.path, artifact.id, artifact.content_digest,
 required_operation,
 separate_authority_ref canonical identity or empty)
```

### authorized_successor_ref

Scalar nested exact ref, optional.

---

## 24. Conformance-fact canonicality

Although `WorkPacketConformanceFacts` is external to the packet digest, deterministic evaluation requires its plural tuples to be canonical.

Rules:

```text
authority_facts:
same order as packet.authority_refs

accepted_design_facts:
same order as packet.accepted_design_artifacts

protected_verification_authority_facts:
same order as packet protected-verification requirements requiring facts

materialization_facts:
same order as required ContextManifest entry keys
```

Noncanonical fact tuples are invalid.

No evaluator silently sorts facts before comparison.

---

## 25. Canonical JSON vectors are mandatory

Implementation tests must contain hard-coded expected canonical JSON and SHA-256 digest vectors for at least:

1. one minimal ContextManifest;
2. one ContextManifest containing all context source/material variants;
3. one minimal WorkPacket;
4. one WorkPacket exercising every normative tuple;
5. one canonical SourceBaselineRef source Baseline;
6. one amended WorkPacket revision.

The expected bytes/digests must be literal fixtures, not generated and then compared to themselves.

---

## 26. F002 negative tests

At minimum:

```text
Baseline.artifact_ids reordered -> rejected
Baseline.decision_ids reordered -> rejected
planning source refs reordered -> rejected
scope.in_scope reordered -> rejected
scope.out_of_scope reordered -> rejected
acceptance criteria reordered -> rejected
dependencies reordered -> rejected
quality keys reordered -> rejected
ContextManifest entries reordered -> rejected
authority refs reordered -> rejected
accepted artifacts reordered -> rejected
required context keys reordered -> rejected
evidence/deliverable/hard-stop tuples reordered -> rejected
credentials reordered -> rejected
workspace property keys reordered -> rejected
protected verification requirements reordered -> rejected
external fact tuples reordered -> rejected
semantically identical canonical objects -> same digest
one normative scalar change -> different digest
```

**F002: RESOLVED BY DESIGN.**

---

# Part III — F003: Deterministic required-context materialization

## 27. Hash identity is not materialization

Revision 2 makes explicit:

```text
known content_digest
    !=
ability to obtain exact content bytes
```

A required context entry is admissible only when it carries an exact `ContextMaterialRef` identifying a deterministic materialization path.

Slice 2.3 does not perform materialization.

It defines the contract an external materialization layer must satisfy.

---

## 28. ContextMaterialRef

Revision 1's `ContextSourceRef` is amended to carry:

```python
material_ref: ContextMaterialRef
```

`ContextMaterialRef` is a closed schema-v1 discriminated union of exactly three source mechanisms:

```text
ArtifactMaterialRef
RepositoryContentMaterialRef
CapturedMaterialRef
```

No digest-only fourth case exists.

---

## 29. ArtifactMaterialRef

Use when exact bytes are already represented by a Relay Artifact.

```python
ArtifactMaterialRef(
    material_kind: Literal["RELAY_ARTIFACT"],
    artifact: Artifact,
    provenance_digest: ContentDigest,
)
```

Materialization semantics:

- read exact artifact path at exact Artifact.commit;
- verify exact Artifact.content_digest;
- verify supplied provenance bytes/record against `provenance_digest`.

If exact artifact bytes are unavailable:

`INDETERMINATE / STOP`

If supplied bytes are available but digest mismatches:

`UNSATISFIED / STOP`

---

## 30. RepositoryContentMaterialRef

Use for exact repository content that is not necessarily a registered Relay Artifact.

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

Rules:

- `commit.repository == repository`;
- `path` is repository-relative and canonical;
- branch/tag/current working-tree names are forbidden;
- materialization reads exactly `path` from exactly `commit`;
- exact bytes must hash to `content_digest`.

Repository path alone is insufficient.

Repository commit alone is insufficient.

---

## 31. CapturedMaterialRef

Use for tool definitions, skills, retrieved content, runtime observations, external references, and session excerpts when they are not materialized as Relay Artifact/repository content.

```python
CapturedMaterialRef(
    material_kind: Literal["CAPTURED_MATERIAL"],
    resolver_key: StableKey,
    resolver_version: int >= 1,
    material_key: str,
    material_version: str,
    content_digest: ContentDigest,
    provenance_digest: ContentDigest,
)
```

Normative semantics:

- `resolver_key + resolver_version` identifies an exact external materialization contract;
- `material_key + material_version` identifies one immutable captured material object under that resolver;
- the resolver must return exact bytes and provenance corresponding to those identities;
- the caller verifies returned bytes/provenance against the two digests;
- a mutable URL, "latest", current tool name, current skill name, session name, or query string is not an admissible material key/version pair by itself;
- if resolver/material identity cannot deterministically reproduce the exact capture, the reference is invalid for required context.

Slice 2.3 does not implement or register resolvers.

No generic adapter framework is authorized.

---

## 32. ContextSourceRef Revision 2

Revision 1's shape is replaced by:

```python
ContextSourceRef(
    source_kind: ContextSourceKind,
    source_key: StableContextSourceKey,
    source_version: str | None,
    material_ref: ContextMaterialRef,
    locator: str | None,
)
```

The exact content/provenance identity is owned by `material_ref`.

`locator` remains descriptive only.

A locator may help a human understand origin, but it cannot satisfy materialization.

---

## 33. Source-kind/material-kind compatibility

Schema-v1 freezes these allowed relationships.

### RELAY_ARTIFACT

Allowed:

`ArtifactMaterialRef`

### GOVERNANCE_RECORD

Preferred:

`ArtifactMaterialRef`

Allowed only if not registered as an Artifact:

`RepositoryContentMaterialRef`

### REPOSITORY_CONTENT

Required:

`RepositoryContentMaterialRef`

### TOOL_DEFINITION

Allowed:

`ArtifactMaterialRef`
or
`CapturedMaterialRef`

### SKILL

Allowed:

`ArtifactMaterialRef`
or
`CapturedMaterialRef`

### RETRIEVAL_RESULT

Allowed:

`ArtifactMaterialRef`
or
`CapturedMaterialRef`

### RUNTIME_OBSERVATION

Allowed:

`ArtifactMaterialRef`
or
`CapturedMaterialRef`

### EXTERNAL_REFERENCE

Allowed:

`ArtifactMaterialRef`
or
`CapturedMaterialRef`

### SESSION_EXCERPT

Allowed:

`ArtifactMaterialRef`
or
`CapturedMaterialRef`

An incompatible source/material pair is structurally invalid.

---

## 34. Required context always has material identity

Every `ContextEntryRef` already points to a `ContextSourceRef`.

After Revision 2 every source contains an exact material ref.

Therefore:

```text
required context key
    -> exact ContextEntryRef
    -> exact ContextSourceRef
    -> exact ContextMaterialRef
    -> deterministic external materialization contract
```

There is no valid required context entry whose only content identity is a hash.

---

## 35. ContextMaterializationFact

The external materialization layer supplies per-material evidence:

```python
ContextMaterializationFact(
    evaluated_material_ref: ContextMaterialRef,
    material_status: RequirementStatus,
    observed_content_digest: ContentDigest | None,
    observed_provenance_digest: ContentDigest | None,
)
```

Rules:

### SATISFIED

Allowed only when:

- exact material ref resolved;
- exact material bytes were available;
- exact provenance bytes/record were available;
- observed content digest equals expected;
- observed provenance digest equals expected.

### UNSATISFIED

Use when material resolves but supplied exact bytes/provenance positively mismatch the expected identity.

### INDETERMINATE

Use when:

- material cannot be obtained;
- resolver unavailable;
- exact version unsupported;
- provenance cannot be obtained;
- availability/currentness cannot be established;
- supplied material fact is absent.

No status grants authority.

---

## 36. Materialization fact exact-set rule

For every WorkPacket `required_context_key`:

- resolve exact ContextEntryRef in the exact ContextManifest;
- derive exact ContextMaterialRef;
- require exactly one matching ContextMaterializationFact.

Optional manifest entries need not have materialization facts unless the renderer/orchestrator chooses to consume them.

A fact for another material ref cannot satisfy the entry.

---

## 37. Context conformance Revision 2

Revision 1 §44 is replaced/extended.

A required entry is `SATISFIED` only when:

```text
exact ContextManifestRef matches
AND exact project matches
AND exact SliceDefinitionRef matches
AND exact required key exists once
AND source/material pair is schema-valid
AND exact materialization fact is present
AND material_status == SATISFIED
AND observed content digest == material expected content digest
AND observed provenance digest == material expected provenance digest
AND repository material, where applicable, matches required source baseline semantics
AND control-mirror binding, where applicable, exact-matches packet control refs
```

Known wrong digest/ref/material/control mirror:

`UNSATISFIED / STOP`

Missing/unavailable/unverifiable material:

`INDETERMINATE / STOP`

---

## 38. Reproducibility definition Revision 2

Revision 1 §61 is clarified.

A WorkPacket is reproducible only when an independent consumer can establish:

- exact WorkPacket bytes/digest;
- exact ContextManifest bytes/digest;
- exact SourceBaselineRef;
- exact required ContextMaterialRefs;
- an external materialization contract capable of supplying exact bytes/provenance for every required material ref;
- exact observed bytes/provenance matching expected digests;
- exact normalized planning source/provenance;
- exact role/policy/profile/authority refs;
- exact declarative requirements;

without prior conversation state or mutable aliases.

Reproducibility is a property of the contract plus exact material availability, not of a hash alone.

---

# Part IV — Mirrored control-plane context

## 39. ControlMirrorKind

Revision 2 adopts the IR clarification.

When control-plane material is included in ContextManifest for model/runtime visibility, the entry must carry a binding:

```text
AUTHORITY_BASIS
ROLE_CONTRACT
POLICY_BASIS
GOVERNANCE_PROFILE
ACCEPTED_DESIGN
SLICE_DEFINITION
SOURCE_BASELINE
```

Conceptual:

```python
ControlMirrorBinding(
    mirror_kind: ControlMirrorKind,
    control_subject_digest: ContentDigest,
)
```

The digest is the canonical identity/digest of the exact WorkPacket control subject being mirrored.

---

## 40. ContextEntryRef Revision 2

```python
ContextEntryRef(
    entry_key,
    context_class,
    source: ContextSourceRef,
    control_mirror_binding: ControlMirrorBinding | None,
)
```

If the entry is intended to present a WorkPacket control-plane object as authoritative/governing context, `control_mirror_binding` is mandatory.

Without it, the entry may be supporting context but cannot be rendered/labeled as the packet's governing authority/policy/role/design/baseline instruction.

---

## 41. Exact mirror rules

### AUTHORITY_BASIS

`control_subject_digest` must identify exactly one WorkPacket AuthorityBasisRef or the canonical authority-ref set digest, as specified by the renderer contract.

### ROLE_CONTRACT

Must equal the exact packet RoleContractRef identity digest.

### POLICY_BASIS

Must equal packet PolicyBasisRef identity digest.

### GOVERNANCE_PROFILE

Must equal packet GovernanceProfileRef identity digest.

### ACCEPTED_DESIGN

Must equal one exact packet accepted-design Artifact identity digest.

### SLICE_DEFINITION

Must equal packet SliceDefinitionRef identity digest.

### SOURCE_BASELINE

Must equal packet SourceBaselineRef identity digest.

Any mismatch:

```text
CONTROL_MIRROR_CONFLICT
UNSATISFIED / STOP
```

A model must not receive conflicting "governing" context merely because the conflict is non-authoritative.

---

## 42. Control-plane source of truth

Normative precedence:

```text
WorkPacket exact control refs
    are the governing machine-readable subjects.

ContextManifest mirrored material
    is a renderable/materialized representation only.

mirror cannot override packet
mirror cannot extend packet
mirror cannot substitute another authority/policy/role/design
```

Phase 3 rendering must prefer derivation from exact packet refs when possible.

---

# Part V — Revised WorkPacket / ContextManifest shapes

## 43. ContextManifest combined Revision 2 shape

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

Revision 1 shape is retained.

Revision 2 changes the nested `ContextSourceRef` / `ContextEntryRef` semantics through material refs and control-mirror bindings.

---

## 44. WorkPacket combined Revision 2 shape

Revision 1 §33 is amended only where shown:

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

No authority status is embedded.

No material bytes are embedded.

No resolver executes inside the WorkPacket model.

---

# Part VI — Amendment / authority semantics

## 45. Revision changes remain authority-sensitive

Revision 1 amendment semantics remain.

Revision 2 clarifies:

Changing any of these changes WorkPacket identity and requires a new external authority applicability decision:

- SourceBaselineRef;
- authority refs;
- policy/profile refs;
- RoleContractRef;
- accepted design artifacts;
- normalized intent;
- ContextManifestRef;
- required context keys;
- evidence/deliverable/hard-stop contract;
- runtime declarations;
- workspace declarations;
- protected-verification requirements;
- successor ref.

Changing only external conformance facts does not change WorkPacket digest, but facts must bind the exact unchanged WorkPacketRef.

---

## 46. Context material updates require new manifest identity

If any ContextMaterialRef changes:

- ContextSourceRef changes;
- ContextEntryRef changes;
- ContextManifest digest changes;
- ContextManifest revision increments;
- consuming WorkPacket must amend its ContextManifestRef;
- WorkPacket digest/revision changes;
- external authority applicability must be re-established for the new packet.

There is no "refresh context in place."

---

# Part VII — Deterministic evaluation composition

## 47. Revised packet conformance order

Evaluation is intentionally ordered:

```text
1. validate WorkPacket structure/canonicality
2. compute exact WorkPacketRef
3. verify facts.evaluated_work_packet_ref exact match

4. resolve exact ContextManifest
5. validate ContextManifest structure/canonicality
6. compute exact ContextManifestRef
7. verify packet/facts exact manifest refs match

8. verify exact subject bindings for:
   Slice definition
   source baseline
   authority refs
   policy/profile
   RoleContract applicability
   accepted design
   protected verification
   materialization facts

9. evaluate exact materialization/context conformance

10. evaluate supplied requirement statuses

11. aggregate:
    known incompatible/invalid -> UNSATISFIED
    else missing/stale/conflicting/unverifiable -> INDETERMINATE
    else -> SATISFIED
```

No later successful fact repairs an earlier exact-subject mismatch.

---

## 48. Conformance still does not authorize execution

Even after Revision 2:

```text
WorkPacketConformance == SATISFIED
    !=
AUTHORIZED
```

Future Phase 3 still requires independently:

- exact current authority;
- actor binding;
- RoleAction eligibility;
- separation;
- Slice 2.4 workspace enforcement;
- Slice 2.1 runtime capability/provenance;
- protected-verification controls;
- all applicable execution predicates.

---

# Part VIII — Revised refusal vocabulary

## 49. Additional mandatory reasons

Revision 1 reason vocabulary remains and adds:

```text
WORK_PACKET_FACT_SUBJECT_MISMATCH
AUTHORITY_FACT_SET_MISMATCH
ACCEPTED_DESIGN_FACT_SET_MISMATCH
PROTECTED_VERIFICATION_FACT_SET_MISMATCH
MATERIALIZATION_FACT_SET_MISMATCH

SOURCE_BASELINE_REF_MISMATCH
SOURCE_BASELINE_NONCANONICAL

CONTEXT_MATERIAL_REF_REQUIRED
CONTEXT_MATERIAL_UNAVAILABLE
CONTEXT_MATERIAL_CONTENT_MISMATCH
CONTEXT_MATERIAL_PROVENANCE_MISMATCH
CONTEXT_MATERIAL_RESOLVER_UNSUPPORTED
CONTEXT_SOURCE_MATERIAL_KIND_INVALID

CONTROL_MIRROR_BINDING_REQUIRED
CONTROL_MIRROR_CONFLICT

NESTED_COLLECTION_NONCANONICAL
```

Known mismatch -> `UNSATISFIED`.

Missing/unavailable/stale/conflicting/unverifiable -> `INDETERMINATE`.

No reason grants authority.

---

# Part IX — Revised implementation boundary

## 50. Minimal package remains unchanged

A later implementation authority should still prefer:

```text
src/relay_engine/work_packets/
  __init__.py
  models.py
  evaluation.py
```

Revision 2 does not justify:

- database;
- content store;
- retrieval engine;
- resolver registry;
- network client;
- runtime adapter;
- workspace implementation;
- CLI;
- UI.

---

## 51. Materialization implementation remains external

Initial Slice 2.3 code may define:

- material-ref models;
- materialization-fact models;
- pure validation/evaluation.

It must not implement:

```text
resolve_material(...)
fetch_url(...)
read_external_skill(...)
call_tool_registry(...)
query_vector_store(...)
read_chat_history(...)
invoke_runtime(...)
```

Actual material supply belongs to a later integration/orchestration boundary.

---

# Part X — Revised test obligations

## 52. F001 exact-subject tests

All tests from §16 are required.

Additionally:

- `evaluated_work_packet_ref` must be exact;
- no fact object may be accepted without its exact evaluated subject;
- plural fact tuples must exact-match packet/manifest subject tuples;
- exact set mismatch fails before status aggregation.

---

## 53. F002 recursive canonicality tests

All tests from §26 are required.

Hard-coded canonical JSON/digest vectors are mandatory.

Implementation must include at least one regression test proving two semantically identical but differently ordered noncanonical inputs cannot yield two valid WorkPacket identities.

---

## 54. F003 materialization tests

Mandatory:

```text
required digest-only source with no material ref -> structurally invalid
repository material without exact commit/path -> invalid
ArtifactMaterialRef unavailable -> INDETERMINATE
RepositoryContentMaterialRef unavailable -> INDETERMINATE
CapturedMaterialRef resolver/version unavailable -> INDETERMINATE

material available + wrong content digest -> UNSATISFIED
material available + wrong provenance digest -> UNSATISFIED
exact material + exact provenance -> SATISFIED

mutable URL alone cannot satisfy required context
mutable branch name alone cannot satisfy required context
current tool name alone cannot satisfy required context
session name alone cannot satisfy required context

required SESSION_EXCERPT has exact material ref
required TOOL_DEFINITION has exact material ref
required SKILL has exact material ref
required EXTERNAL_REFERENCE has exact material ref

context is reproducible without prior chat state
```

---

## 55. Control-mirror tests

Mandatory:

```text
mirrored RoleContract exact match -> allowed
mirrored RoleContract mismatch -> UNSATISFIED
mirrored policy mismatch -> UNSATISFIED
mirrored authority mismatch -> UNSATISFIED
mirrored accepted design mismatch -> UNSATISFIED
mirrored baseline mismatch -> UNSATISFIED

unbound supporting context cannot be presented as governing control context
```

---

# Part XI — A01–A14 closure

## 56. Acceptance criteria disposition after Revision 2

```text
A01 PASS
A02 PASS
A03 PASS
A04 PASS
A05 PASS
A06 PASS
A07 PASS
A08 PASS
A09 PASS
A10 PASS
A11 PASS
A12 PASS
A13 PASS
A14 PASS
```

### A01

PASS.

WorkPacket/ContextManifest identity now closes recursively over every normative collection reachable from canonical bytes, with explicit order semantics and fixed test vectors.

### A02

PASS.

Exact Project/Slice/SourceBaselineRef binding remains explicit.

### A03

PASS.

External authority/policy/profile/role facts are exact-ref-bound; no detached aggregate status may satisfy another packet.

### A04

PASS.

Every required ContextEntryRef now binds an exact deterministic materialization contract and fail-closed materialization evidence.

### A05

PASS.

Provider-neutral normalized intent remains exact/source-provenanced and no semantic invention is permitted.

### A06

PASS.

Objective/scope/non-scope/acceptance/evidence/deliverable/hard-stop contract remains explicit.

### A07

PASS.

Slice 2.2 input/output semantics are transported without duplication, and exact applicability is bound through RoleApplicabilityEvaluation.

### A08

PASS.

Runtime requirements remain declarative and reuse Slice 2.1.

### A09

PASS.

Workspace requirements remain declarative; Slice 2.4 enforcement remains untouched.

### A10

PASS.

Protected-verification authority evidence is exact requirement/ref-bound and cannot be inferred from role/workspace capability.

### A11

PASS.

Changed normative packet/context content changes digest/revision and requires renewed external authority applicability; no latest lookup exists.

### A12

PASS.

Successor ref remains non-inherited authority; PROPOSED_WORK and BACKLOG_EXHAUSTED semantics are preserved.

### A13

PASS.

Missing/stale/conflicting/unverifiable exact facts or required material fail closed.

### A14

PASS.

No DB/RAG/orchestration/provider execution/Slice 2.4/Phase 3 scope leakage is introduced.

---

# Part XII — Independent re-review checklist

## 57. Revision 2 review questions

Independent re-review must answer YES to all:

### F001

- Does every external conformance status bind an exact subject/ref?
- Does WorkPacketConformanceFacts bind the exact WorkPacketRef?
- Do plural authority/design/protected/material fact sets exact-match packet subjects?
- Does RoleApplicabilityEvaluation bind the packet's exact RoleContractRef?
- Can facts for Packet A ever satisfy Packet B? Expected: NO.

### F002

- Is every normative sequence reachable from WorkPacket/ContextManifest explicitly classified as order-semantic or canonical non-semantic?
- Are nested Baseline and NormalizedEngineeringIntent collections covered?
- Are noncanonical inputs rejected rather than silently sorted?
- Are fixed canonical JSON/digest vectors required?

### F003

- Does every required context entry carry an exact ContextMaterialRef?
- Is digest-only required context impossible?
- Can an external materialization layer obtain exact bytes/provenance from the material ref contract?
- Do unavailable materials fail INDETERMINATE?
- Do mismatched supplied bytes fail UNSATISFIED?
- Is materialization implementation still outside Slice 2.3?
- Are mirrored control-plane entries exact-bound to packet control refs?

### Preserved boundaries

- WorkPacket != authority?
- Human root authority external?
- no DB/persistence?
- no RAG/vector DB?
- no provider/runtime execution?
- no workspace enforcement?
- no Slice 2.4 opening?
- no Phase 3 opening?

Any NO requires REWORK or ESCALATE.

---

# Part XIII — Rework disposition

## 58. Final Revision 2 state

```text
RLY-S23-DESIGN-REWORK-AUTH-001 — AUTHORIZED

Slice 2.3:
OPEN

Design Revision 1:
RLY-S23-DESIGN-EVAL-001 — REWORK

Design Revision 2 Amendment:
REWORK COMPLETE / READY FOR INDEPENDENT RE-REVIEW

F001:
RESOLVED BY DESIGN

F002:
RESOLVED BY DESIGN

F003:
RESOLVED BY DESIGN

A01-A14:
ALL PASS BY DESIGN CLAIM — REQUIRES INDEPENDENT RE-REVIEW

Human design acceptance:
NOT ELIGIBLE UNTIL INDEPENDENT ACCEPT

Implementation:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Production WorkPacket creation/wiring:
NOT AUTHORIZED

Context materialization/storage:
NOT IMPLEMENTED / NOT AUTHORIZED

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

**Revision 2 rework complete != independent design acceptance.**
