# Slice 2.3 — Independent Design Evaluation 002

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Evaluation ID:** `RLY-S23-DESIGN-EVAL-002`  
**Outcome:** `ACCEPT`  
**Original design authority:** `RLY-S23-DESIGN-AUTH-001 — AUTHORIZED`  
**Rework authority:** `RLY-S23-DESIGN-REWORK-AUTH-001 — AUTHORIZED`  
**Revision 1 candidate:** `8e3cb2df658711cd3e18d364cf19fa5332b2ab2f`  
**Revision 1 blob:** `d11529c5fdf068a142e79171642cdb735dc290cd`  
**Revision 2 amendment candidate:** `699664be71e320e053127d7d7c7b2226911fe401`  
**Revision 2 amendment blob:** `c781a3de90cfd54156f3cce6009ac4baa46ce6af`  
**Prior evaluation:** `RLY-S23-DESIGN-EVAL-001 — REWORK`  
**Reviewer role:** Independent Slice 2.3 Design Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

Revision 2 closes all three blocking findings from `RLY-S23-DESIGN-EVAL-001` without expanding Slice 2.3 beyond its authorized design boundary.

The combined design:

- binds external conformance evidence to exact WorkPacket/control/context subjects;
- closes canonical identity recursively over normative packet/manifest collections;
- gives every required context entry a deterministic exact materialization contract;
- preserves WorkPacket != authority;
- preserves Human root authority outside the packet layer;
- preserves Slice 2.1 runtime ownership;
- preserves Slice 2.2 Role Contract ownership;
- preserves Slice 2.4 workspace-enforcement ownership;
- preserves Phase 3 orchestration ownership;
- adds no database, RAG system, runtime execution, workspace enforcement, lifecycle mutation, or provider call.

No blocking design finding remains.

Independent design ACCEPT does not itself grant Human design acceptance or implementation authority.

---

## 1. Exact evaluated subject

```text
Repository:
cschrupp/relay

Canonical opening baseline:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Slice 2.3 opening:
RLY-S23-OPEN-001 — OPEN

Opening commit:
bddc6a25ab31cfe7395b07135d7f05f5ac3c8e0f

Original design authority:
RLY-S23-DESIGN-AUTH-001 — AUTHORIZED

Original design-authority commit:
4bc054af24bbd19130d7474bab75433b056ef9e4

Revision 1:
8e3cb2df658711cd3e18d364cf19fa5332b2ab2f

Revision 1 blob:
d11529c5fdf068a142e79171642cdb735dc290cd

Prior independent evaluation:
RLY-S23-DESIGN-EVAL-001 — REWORK

Prior evaluation commit:
f0383fe624e99134586198cfcb9be77aae2fb014

Revision 2 rework authority:
RLY-S23-DESIGN-REWORK-AUTH-001 — AUTHORIZED

Rework-authority commit:
ff37525222215f2a64c833d77c5d2a8779ac7509

Revision 2 amendment:
699664be71e320e053127d7d7c7b2226911fe401

Revision 2 amendment blob:
c781a3de90cfd54156f3cce6009ac4baa46ce6af
```

Revision 2 is normative over Revision 1 where they differ.

The independent subject is the combined Revision 1 + Revision 2 design.

---

## 2. Rework lineage and scope

The Revision 2 candidate is exactly two commits after the immutable REWORK evaluation:

```text
f0383fe624e99134586198cfcb9be77aae2fb014
    |
    +-- ff37525222215f2a64c833d77c5d2a8779ac7509
    |   RLY-S23-DESIGN-REWORK-AUTH-001
    |
    +-- 699664be71e320e053127d7d7c7b2226911fe401
        Revision 2 amendment
```

The bounded rework delta adds only:

```text
docs/reviews/SLICE_2_3_DESIGN_REWORK_AUTHORIZATION_001.md
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN_REV2_AMENDMENT.md
```

No source, tests, dependencies, database, runtime, workspace, lifecycle, or canonical-main mutation occurred.

**Rework scope:** PASS.

---

# 3. F001 — exact-subject-bound conformance evidence

**Prior status:** BLOCKING  
**Revision 2 disposition:** CLOSED

Revision 2 replaces detached aggregate statuses with exact-subject-bound facts.

The combined design now requires `WorkPacketConformanceFacts` to bind:

```text
exact WorkPacketRef
exact ContextManifestRef
exact SliceDefinitionRef
exact SourceBaselineRef
exact AuthorityBasisRef tuple
exact PolicyBasisRef
exact GovernanceProfileRef or exact external not-required fact
exact RoleContractRef through RoleApplicabilityEvaluation
exact accepted-design Artifact tuple
exact protected-verification requirement/authority subjects
exact required ContextMaterialRef tuple
```

For every plural subject set, exact canonical tuple equality is required before status aggregation.

The evaluator must reject or fail closed when:

- Packet A facts are supplied for Packet B;
- authority-ref sets differ;
- policy/profile refs differ;
- source baseline differs;
- accepted design sets differ;
- ContextManifestRef differs;
- protected verification subject/operation/authority differs;
- materialization facts target another material set.

### Role applicability compatibility

Revision 2 reuses the actual accepted Slice 2.2 implementation type:

```text
RoleApplicabilityEvaluation
    role_contract_ref
    status
    reason
```

and requires:

```text
role_contract_applicability.role_contract_ref
    == packet.role_contract_ref

AND

role_contract_applicability.status
    == APPLICABLE
```

This is exactly compatible with the accepted Slice 2.2 role-applicability contract.

No near-equivalent role-selection system is introduced.

### Authority separation

Exact evidence binding does not turn evidence into authority.

The combined design still requires external Human/governance authority independently.

```text
exact authority fact
    !=
authority issuance

SATISFIED
    !=
AUTHORIZED
```

**F001:** CLOSED.

---

# 4. F002 — recursive canonical identity

**Prior status:** BLOCKING  
**Revision 2 disposition:** CLOSED

Revision 2 establishes a recursive rule:

> Every normative collection reachable from WorkPacket or ContextManifest must be explicitly order-semantic or canonical non-semantic.

For non-semantic collections:

- one deterministic ordering is mandatory;
- duplicates/conflicting stable identities are invalid;
- noncanonical input is rejected;
- evaluators/constructors do not silently sort.

The amendment explicitly covers:

```text
Baseline.artifact_ids
Baseline.decision_ids

NormalizedEngineeringIntent.source_refs
ScopeSpec.in_scope
ScopeSpec.out_of_scope
acceptance_criteria
dependency_slice_ids
quality_requirement_keys
standalone normalization issues

ContextManifest.entries

WorkPacket.authority_refs
accepted_design_artifacts
required_context_keys
evidence_requirements
deliverable_requirements
hard_stops
required_runtime_capabilities
credential_refs
required_workspace_property_keys
protected_verification_requirements

external conformance-fact tuples
```

### SourceBaselineRef

Replacing the embedded Baseline with:

```text
SourceBaselineRef
    baseline_id
    project_id
    commit
    content_digest
```

is a valid design refinement.

The content digest covers the exact canonical Baseline value, including the canonical artifact-id and decision-id tuples.

The existing Baseline domain object is not modified.

### Fixed digest vectors

Revision 2 requires literal canonical JSON / SHA-256 fixtures for:

- minimal ContextManifest;
- full material-variant ContextManifest;
- minimal WorkPacket;
- full normative-tuple WorkPacket;
- SourceBaselineRef source Baseline;
- amended WorkPacket.

This prevents tests from proving only self-consistency of one serializer implementation.

### Total-order implementation clarification

The accepted design's `unique/canonical` requirements mean implementations must reject two entries that share the same canonical stable identity/sort key while carrying conflicting normative content.

They must not invent an arbitrary tie order.

Examples include conflicting representations of the same Artifact identity or planning-source identity.

This clarification does not change the accepted architecture; it is a direct consequence of the design's unique/canonical invariant.

**F002:** CLOSED.

---

# 5. F003 — deterministic required-context materialization

**Prior status:** BLOCKING  
**Revision 2 disposition:** CLOSED

Revision 2 explicitly distinguishes:

```text
content hash identity
    !=
ability to materialize content
```

Every required ContextEntryRef now reaches an exact ContextMaterialRef.

The closed schema-v1 material mechanisms are:

```text
ArtifactMaterialRef
RepositoryContentMaterialRef
CapturedMaterialRef
```

There is no digest-only required-context variant.

## ArtifactMaterialRef

Binds an exact Relay Artifact and provenance digest.

Exact content is materialized from the Artifact path at its exact CommitRef.

Unavailable exact content -> INDETERMINATE.

Available but digest-mismatched content -> UNSATISFIED.

## RepositoryContentMaterialRef

Binds:

```text
RepositoryRef
CommitRef
repository-relative path
content digest
provenance digest
```

A branch, tag, current worktree, or path alone cannot satisfy required context.

## CapturedMaterialRef

Binds:

```text
resolver_key
resolver_version
material_key
material_version
content_digest
provenance_digest
```

The design normatively defines `resolver_key + resolver_version` as an exact immutable external materialization contract and `material_key + material_version` as one immutable capture under that contract.

Mutable aliases are forbidden as sufficient material identity.

If the exact resolver contract/version or material identity cannot be established, materialization is INDETERMINATE.

No resolver registry or implementation is introduced by Slice 2.3.

## Materialization evidence

Every required material receives an exact:

```text
ContextMaterializationFact
```

bound to the exact ContextMaterialRef.

SATISFIED requires both:

- observed content digest == expected;
- observed provenance digest == expected.

A fact for material A cannot satisfy material B.

## Provenance implementation clarification

The design requires exact provenance bytes/record to be available before materialization may be SATISFIED.

A later implementation must therefore make provenance verification deterministic for each material kind.

It may either:

- define a canonical provenance record derivable from the exact material ref; or
- consume an exact provenance record supplied by the external materialization contract.

A bare provenance digest with no obtainable/derivable exact provenance record must remain INDETERMINATE.

This is already the semantic requirement of Revision 2 and does not require another design amendment.

## Reproducibility

The combined design now correctly defines reproducibility as:

```text
exact packet/manifest identity
+ exact material refs
+ exact external materialization contract
+ exact material availability
+ matching content/provenance digests
```

not merely as possession of hashes.

**F003:** CLOSED.

---

# 6. IR clarification — mirrored control-plane context

**Disposition:** ADOPTED / PASS

Revision 2 introduces exact ControlMirrorBinding semantics for:

```text
AUTHORITY_BASIS
ROLE_CONTRACT
POLICY_BASIS
GOVERNANCE_PROFILE
ACCEPTED_DESIGN
SLICE_DEFINITION
SOURCE_BASELINE
```

WorkPacket control refs remain the machine-readable source of truth.

Mirrored ContextManifest material is renderable context only.

It cannot:

- override packet control refs;
- extend packet authority/scope;
- substitute another policy/role/design;
- present conflicting governing context to the model.

Mismatch is:

```text
CONTROL_MIRROR_CONFLICT
UNSATISFIED / STOP
```

This closes the non-blocking IR clarification without creating a prompt-policy system.

---

# 7. Preserved architecture assessment

## WorkPacket != authority

**PASS**

No packet model, digest, conformance result, materialization fact, role result, or context fact issues authority.

## Human root authority

**PASS**

Remains external to Slice 2.3.

## Planning normalization

**PASS**

Provider-neutral.

No Spec Kit/OpenSpec/BMAD implementation dependency is introduced.

Ambiguous/missing/conflicting source semantics remain fail-closed.

## Exact scope / acceptance contract

**PASS**

Objective, ScopeSpec, acceptance criteria, evidence, deliverables, and hard stops remain explicit and digest-bound.

## Slice 2.2 boundary

**PASS**

RoleInputRequirement / RoleOutputRequirement and RoleApplicabilityEvaluation are reused, not duplicated.

## Slice 2.1 runtime boundary

**PASS**

Runtime requirements remain declarations.

No AgentRuntime invocation or requested/actual identity fabrication is introduced.

## Slice 2.4 workspace boundary

**PASS**

Workspace policy/property requirements remain declarations.

No path/network/tool/credential/resource enforcement is designed into Slice 2.3.

## Protected verification

**PASS**

Exact requirement/ref-bound evidence does not collapse:

```text
permission
capability
authority
```

READ, MODIFY, APPROVE_MUTATION, and EVALUATE remain distinct.

## Amendment / authority renewal

**PASS**

Any normative WorkPacket/ContextManifest change changes identity/revision and requires renewed external authority applicability.

No context refresh-in-place exists.

## Successor semantics

**PASS**

Authorized successor reference:

- does not authorize successor execution;
- cannot be populated from PROPOSED_WORK;
- does not imply authority inheritance.

Empty successor ref still does not imply BACKLOG_EXHAUSTED.

Only externally established NO_AUTHORIZED_SUCCESSOR maps to BACKLOG_EXHAUSTED under Slice 2.2.

## Design economy

**PASS**

Revision 2 does not add:

```text
database
migration
content store
resolver registry
RAG
vector DB
network client
provider/model call
runtime invocation
workspace enforcement
lifecycle mutation
CLI
UI
Phase 3 orchestration
```

---

# 8. A01–A14 final disposition

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

WorkPacket/ContextManifest identity is recursively deterministic over all reachable normative collections, with literal canonical digest fixtures required.

### A02

PASS.

Exact Project/Slice/SourceBaselineRef identity remains bound.

### A03

PASS.

External authority/policy/profile/role evidence is exact-subject-bound and cannot manufacture authority.

### A04

PASS.

Required context now has exact material identity plus fail-closed deterministic materialization evidence.

### A05

PASS.

Planning normalization remains provider-neutral, exact-source-provenanced, and non-inventive.

### A06

PASS.

Objective/scope/non-scope/acceptance/evidence/deliverable/hard-stop contract remains explicit.

### A07

PASS.

Slice 2.2 semantic obligations are transported without duplicating role policy; exact RoleContract applicability is bound.

### A08

PASS.

Runtime requirements remain declarative and reuse Slice 2.1.

### A09

PASS.

Workspace/tool/network/credential/resource requirements remain declarative; Slice 2.4 enforcement is preserved.

### A10

PASS.

Protected-verification evidence remains exact requirement/ref-bound and cannot grant mutation/evaluation authority.

### A11

PASS.

Normative change -> new digest/revision -> renewed external authority applicability. No latest lookup.

### A12

PASS.

Successor/proposed-work/no-authority-inheritance/BACKLOG_EXHAUSTED semantics are preserved.

### A13

PASS.

Missing, stale, conflicting, unavailable, unsupported, or unverifiable required facts/material fail closed.

### A14

PASS.

No DB/RAG/orchestration/provider execution/Slice 2.4/Phase 3 scope leakage exists.

---

# 9. Exact-head quality evidence

Exact-head GitHub Actions:

```text
Run:
39793522379

Head:
699664be71e320e053127d7d7c7b2226911fe401

Branch:
design/2.3-context-work-packet-contract

Status:
COMPLETED

Conclusion:
SUCCESS
```

Observed quality steps:

```text
Sync environment:
SUCCESS

Ruff format:
SUCCESS

Ruff lint:
SUCCESS

Pyright:
SUCCESS

Tests:
SUCCESS

Build:
SUCCESS
```

CI is engineering evidence only; independent design acceptance is this separate evaluation.

---

# 10. Implementation handoff constraints

A later implementation authorization should preserve at minimum:

1. exact WorkPacketRef binding on every external fact set;
2. exact ContextManifestRef binding;
3. exact per-authority/design/protected/material fact binding;
4. accepted Slice 2.2 RoleApplicabilityEvaluation reuse;
5. SourceBaselineRef canonical baseline digest;
6. recursive canonical tuple validation;
7. rejection, not silent sorting, of noncanonical inputs;
8. literal canonical JSON/digest fixtures;
9. exact ContextMaterialRef closed union;
10. deterministic provenance verification;
11. exact materialization facts for every required context entry;
12. exact source-kind/material-kind compatibility;
13. control-mirror exact-match enforcement;
14. no resolver/storage implementation in Slice 2.3;
15. no DB migration;
16. no AgentRuntime invocation;
17. no workspace enforcement;
18. no lifecycle mutation;
19. no Human/work authority issuance;
20. no Slice 2.4 / Phase 3 implementation.

### Clarification — canonical sort-key collisions

If two candidate items share a canonical sort/stable identity while differing in normative content, implementation must reject the input as conflicting/invalid.

Do not resolve the collision by arbitrary secondary ordering.

### Clarification — exact resolver contract

For CapturedMaterialRef, `resolver_key + resolver_version` must be treated as an immutable externally established materialization-contract identity.

If its exact semantics cannot be established for that version, the material is INDETERMINATE.

No mutable resolver alias may silently satisfy a captured material ref.

These clarifications follow directly from the accepted Revision 2 semantics and do not expand implementation scope.

---

# 11. Independent disposition

```text
RLY-S23-DESIGN-EVAL-002 — ACCEPT

Revision 1:
8e3cb2df658711cd3e18d364cf19fa5332b2ab2f

Revision 2 Amendment:
699664be71e320e053127d7d7c7b2226911fe401

Revision 2 blob:
c781a3de90cfd54156f3cce6009ac4baa46ce6af

F001:
CLOSED

F002:
CLOSED

F003:
CLOSED

IR mirror clarification:
ADOPTED / PASS

A01-A14:
ALL PASS

Combined Slice 2.3 design:
INDEPENDENTLY ACCEPTED

Exact-head CI:
GREEN — 39793522379

Human design acceptance:
PENDING

Implementation:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Production WorkPacket creation/wiring:
NOT AUTHORIZED

Context materialization/storage:
NOT IMPLEMENTED / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

Independent design ACCEPT does not itself grant Human design acceptance or implementation authority.
