# Slice 2.3 — Independent Design Evaluation 001

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Evaluation ID:** `RLY-S23-DESIGN-EVAL-001`  
**Outcome:** `REWORK`  
**Design authority:** `RLY-S23-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact evaluated candidate:** `8e3cb2df658711cd3e18d364cf19fa5332b2ab2f`  
**Exact design blob:** `d11529c5fdf068a142e79171642cdb735dc290cd`  
**Reviewer role:** Independent Slice 2.3 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

Revision 1 establishes the correct overall Slice 2.3 architecture and preserves the accepted Slice 2.1 / Slice 2.2 / Slice 2.4 / Phase 3 boundaries.

However, three design defects prevent independent acceptance:

1. externally supplied conformance statuses are not bound to the exact WorkPacket/ref subjects they attest;
2. canonical identity is not closed over every nested normative sequence included in the WorkPacket digest;
3. ContextManifest references prove content hashes/provenance but do not yet guarantee deterministic materialization/reproduction of every required context entry.

All three are bounded contract-integrity issues. None requires expanding Slice 2.3 into persistence, RAG, runtime execution, workspace enforcement, or a second authority system.

---

## 1. Exact review subject

```text
Repository:
cschrupp/relay

Canonical design baseline:
408237a34e8acdf14eba7ee873f26d1f10ff5a6c

Opening:
RLY-S23-OPEN-001 — OPEN

Opening commit:
bddc6a25ab31cfe7395b07135d7f05f5ac3c8e0f

Design authority:
RLY-S23-DESIGN-AUTH-001 — AUTHORIZED

Design-authority commit:
4bc054af24bbd19130d7474bab75433b056ef9e4

Evaluated design candidate:
8e3cb2df658711cd3e18d364cf19fa5332b2ab2f

Design blob:
d11529c5fdf068a142e79171642cdb735dc290cd
```

Candidate ancestry is exact:

```text
ahead of authorized canonical baseline:
3 commits

behind:
0
```

The candidate adds exactly:

```text
docs/reviews/SLICE_2_3_OPENING.md
docs/reviews/SLICE_2_3_DESIGN_AUTHORIZATION.md
docs/slices/SLICE_2_3_CONTEXT_WORK_PACKET_CONTRACT_DESIGN.md
```

No implementation/source/test/runtime/database/workspace mutation is part of the design candidate.

**Scope / ancestry:** PASS.

---

# 2. Finding F001 — external conformance facts are detached from exact subjects

**Severity:** BLOCKING  
**Affected criteria:** A03, A07, A10, A13  
**Disposition:** REWORK REQUIRED

Revision 1 defines:

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

The statuses are not bound to the exact references they attest.

There is no required field such as:

```text
evaluated_work_packet_ref
evaluated_context_manifest_ref
evaluated_slice_definition_ref
evaluated_source_baseline identity
evaluated authority-ref set
evaluated policy/profile refs
evaluated RoleContractRef
evaluated accepted-design refs
evaluated protected-verification requirement/authority refs
```

Therefore the design does not yet prevent:

```text
facts evaluated for Packet A
    +
Packet B with different exact references
    ->
same aggregate SATISFIED statuses being consumed
```

This is structurally the same detached-evidence failure class that Slice 2.2 previously repaired for RoleContract applicability.

The design correctly says supplied facts are external evidence and that packet conformance is not authority. That is necessary but not sufficient: the evidence must also be exact-subject-bound.

## Required bounded correction

Revision 2 must require every externally supplied conformance fact/result to bind the exact subject it evaluates.

At minimum, the conformance input/evaluation must bind:

```text
exact WorkPacketRef
exact ContextManifestRef
exact SliceDefinitionRef
exact source-baseline identity
exact authority-ref set
exact PolicyBasisRef
exact GovernanceProfileRef or exact externally-established not-required fact
exact RoleContractRef through RoleApplicabilityEvaluation
exact accepted-design artifact set
exact protected-verification requirements and separate authority refs/statuses
```

For plural requirements, a single unkeyed aggregate status is insufficient.

Use exact per-ref facts/evaluations or an exact digest-bound set plus status whose identity can be checked deterministically.

The evaluator must reject or return INDETERMINATE when:

- facts are for another WorkPacketRef;
- a supplied authority/ref set differs from the packet;
- a policy/profile fact is for another exact ref;
- RoleApplicabilityEvaluation is for another RoleContractRef;
- accepted-design evidence is for another artifact/ref set;
- protected-verification authority evidence is for another exact requirement/asset/ref;
- any required subject binding is missing or conflicting.

## Required negative tests

At minimum:

- Packet A conformance facts cannot satisfy Packet B;
- changing one authority ref invalidates old facts;
- changing ContextManifestRef invalidates old facts;
- facts for another source baseline cannot satisfy the packet;
- applicability for RoleContract A cannot satisfy packet RoleContract B;
- accepted-design status for artifact set A cannot satisfy set B;
- protected-verification authority for asset/operation A cannot satisfy B.

**F001 status:** OPEN / BLOCKING.

---

# 3. Finding F002 — canonical digest is not closed over nested normative collections

**Severity:** BLOCKING  
**Affected criterion:** A01  
**Disposition:** REWORK REQUIRED

Revision 1 correctly requires:

```text
UTF-8
sort_keys = true
compact JSON separators
ensure_ascii = false
allow_nan = false
no floating-point normative values
canonical tuple ordering
reject noncanonical input rather than silently sort
```

It also freezes top-level ordering for:

- authority refs;
- accepted artifacts;
- required context keys;
- evidence requirements;
- deliverables;
- hard stops;
- runtime capabilities;
- credential refs;
- workspace property keys;
- protected-verification requirements.

But the WorkPacket digest recursively includes normative objects whose collection order is not fully frozen by the design.

Examples include:

### Existing embedded Baseline

The existing Relay `Baseline` contains:

```text
artifact_ids
decision_ids
```

The accepted domain model requires uniqueness but does not require canonical ordering.

Revision 1 embeds the complete `Baseline` in WorkPacket and does not add packet-level canonicality rules for those nested tuples.

### NormalizedEngineeringIntent

Revision 1 includes:

```python
source_refs
scope.in_scope
scope.out_of_scope
acceptance_criteria
dependency_slice_ids
quality_requirement_keys
issues
```

It explicitly freezes dependency canonicality and acceptance-key uniqueness, but does not fully define the ordering/semantic-order rule for all other normative collections.

Because JSON object-key sorting does not canonicalize array order, callers can construct semantically equivalent normative data with different tuple ordering and therefore different WorkPacket digests unless every nested sequence is either:

1. explicitly declared order-semantic; or
2. explicitly required to use one deterministic canonical order.

That leaves A01 incompletely specified.

## Required bounded correction

Revision 2 must close canonicality over **every normative collection reachable from WorkPacket and ContextManifest**.

For each nested collection, explicitly choose exactly one rule:

```text
ORDER IS NORMATIVE
or
ORDER IS NOT SEMANTIC -> exact canonical ordering is mandatory
```

If ordering is non-semantic, define deterministic ordering keys and reject noncanonical input.

The review expects this to cover at minimum:

- Baseline.artifact_ids;
- Baseline.decision_ids;
- NormalizedEngineeringIntent.source_refs;
- ScopeSpec.in_scope;
- ScopeSpec.out_of_scope;
- NormalizedEngineeringIntent.acceptance_criteria;
- dependency_slice_ids;
- quality_requirement_keys;
- normalization issues for non-COMPLETE values if those values are digestible;
- all nested source/ref tuples introduced by Revision 2.

No production-domain change is required merely to close this design.

The WorkPacket model may validate canonical nested values itself, or the design may replace embedded objects with exact digest-bound refs where that is simpler and preserves existing ownership.

## Required tests

At minimum:

- reordered non-semantic source refs are rejected;
- reordered non-semantic scope statements are rejected or explicitly produce different semantics because order is normatively declared;
- reordered acceptance criteria are rejected unless order is explicitly normative;
- Baseline artifact/decision tuple noncanonicality cannot silently produce alternate packet identities;
- hard-coded canonical JSON/digest vectors exist for WorkPacket and ContextManifest;
- semantically identical canonical inputs produce the same digest.

**F002 status:** OPEN / BLOCKING.

---

# 4. Finding F003 — required context is hash-verifiable but not yet deterministically reproducible

**Severity:** BLOCKING  
**Affected criteria:** A04, A13  
**Disposition:** REWORK REQUIRED

Revision 1 defines:

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

and correctly requires exact digests and fail-closed behavior if content cannot be reconstructed/verified.

It also states:

```text
A WorkPacket is reproducible when an independent consumer can establish:
- exact selected context content/provenance
...
without relying on prior conversation state or mutable aliases.
```

However, the design does not yet define the deterministic materialization boundary that makes this statement true.

A `content_digest` allows a consumer to verify bytes **after bytes are supplied**.

A digest by itself does not provide the bytes.

Likewise:

- `provenance_digest` proves only the identity of supplied provenance bytes;
- `locator` is explicitly optional and non-identity;
- no durable snapshot/artifact/content object is required for TOOL_DEFINITION, SKILL, RETRIEVAL_RESULT, RUNTIME_OBSERVATION, EXTERNAL_REFERENCE, or SESSION_EXCERPT;
- no source-kind-specific exact resolver/materialization contract is frozen.

Therefore a manifest can theoretically remain structurally valid while referring to exact hashes whose underlying bytes are no longer deterministically obtainable from durable Relay state or an explicitly bound material bundle.

That falls short of A04's reproducibility requirement.

## Required bounded correction

Revision 2 must define how every **required** context entry reaches exact bytes/provenance deterministically.

This does not require Slice 2.3 to implement storage, RAG, network retrieval, or persistence.

Acceptable architecture is reference-only, but the reference must bind a materializable exact object.

Prefer reuse of existing Relay identities:

### RELAY_ARTIFACT / accepted repository artifact

Use exact `Artifact` identity where applicable.

### REPOSITORY_CONTENT

Require at least:

```text
exact RepositoryRef / CommitRef
exact repository-relative path or exact snapshot-manifest entry
exact content_digest
```

### TOOL_DEFINITION / SKILL / EXTERNAL_REFERENCE / RETRIEVAL_RESULT / SESSION_EXCERPT / RUNTIME_OBSERVATION

Require an exact captured snapshot/material reference whose bytes can be supplied deterministically by an external content/materialization layer, for example:

```text
exact durable Artifact
or
exact content-addressed material ref + source/provenance identity
or
an exact material bundle reference supplied with the packet
```

The storage/resolver implementation remains out of scope; the **contract** for exact materialization cannot remain implicit.

For a required entry:

```text
digest known
but no exact material source/resolver/bundle binding
    ->
INDETERMINATE / STOP
```

The design should also require that any control-plane material mirrored into ContextManifest for rendering—authority, RoleContract, policy/profile, accepted design—matches the packet's exact control references. A conflicting mirrored context entry must not be allowed to mislead the execution prompt.

## Required tests

At minimum:

- digest-only required external context without material ref -> INDETERMINATE;
- repository content without exact commit+path/material identity -> INDETERMINATE;
- exact material bytes whose digest mismatches source ref -> UNSATISFIED;
- exact material source/ref + matching bytes/provenance -> SATISFIED;
- mutable URL alone cannot satisfy required context;
- session excerpt requires an exact captured material reference;
- exact context can be reconstructed without prior chat state;
- mirrored RoleContract/policy/authority/design context cannot conflict with exact WorkPacket refs.

**F003 status:** OPEN / BLOCKING.

---

# 5. Architecture assessment

## WorkPacket != authority

**PASS**

Revision 1 repeatedly and correctly preserves:

```text
packet presence != authority
packet digest != authority
packet conformance != authority
```

No packet constructor/evaluator creates Human/work authority.

## Human root authority

**PASS**

Human root authority remains external.

No packet field bootstraps it.

## Exact Project/Slice/baseline intent

**PASS**, subject to F002 canonical closure.

The design binds exact ProjectId, SliceDefinitionRef, and source Baseline and forbids "current/latest" Slice resolution.

## Context model

**REWORK**, due F003.

The STATIC/DYNAMIC distinction and source/provenance semantics are appropriate, but required-content materialization must be explicit.

## Planning normalization

**PASS**

The design is provider-neutral and does not implement Spec Kit/OpenSpec/BMAD adapters.

Normalization has explicit COMPLETE / INCOMPLETE / INDETERMINATE semantics and forbids invention from ambiguous prose.

## Scope / acceptance contract

**PASS**

Objective, ScopeSpec, AcceptanceCriterion, dependencies, evidence, deliverables, and hard stops are explicit.

## Slice 2.2 input/output mapping

**PASS**, subject to F001 exact fact binding.

The mapping correctly distinguishes transportable references from execution-time facts and does not incorrectly mark ACTOR_IDENTITY_BINDING or RUNTIME_EXECUTION_BASIS satisfied merely from packet presence.

## Runtime boundary

**PASS**

Runtime requirements reuse Slice 2.1 values and remain declarative.

No AgentRuntime invocation is designed into Slice 2.3.

## Workspace boundary

**PASS**

WorkspacePolicyRef / property requirements are declarations only.

Concrete enforcement remains Slice 2.4.

## Protected Verification Assets

**PASS**, subject to F001 exact authority-evidence binding.

The design correctly preserves permission != authority and workspace write != protected mutation authority.

## Amendment semantics

**PASS**

Changed normative WorkPacket/ContextManifest content requires a new digest/revision and new external authority applicability.

No latest/newest fallback is allowed.

## Successor / PROPOSED_WORK / BACKLOG_EXHAUSTED

**PASS**

The design preserves:

- no successor authority inheritance;
- current execution stops;
- empty successor ref != no successor;
- PROPOSED_WORK != authority;
- only externally established NO_AUTHORIZED_SUCCESSOR maps to BACKLOG_EXHAUSTED.

## Design economy

**PASS**

Initial implementation remains a bounded pure-domain package with:

```text
no database
no migration
no RAG
no vector DB
no provider calls
no runtime execution
no workspace enforcement
no lifecycle mutation
no external-planning adapter implementation
no Phase 3 orchestration
```

---

# 6. A01–A14 disposition

```text
A01  FAIL — F002
A02  PASS
A03  FAIL — F001
A04  FAIL — F003
A05  PASS
A06  PASS
A07  PASS subject to F001 exact-fact binding
A08  PASS
A09  PASS
A10  PASS subject to F001 exact protected-authority binding
A11  PASS
A12  PASS
A13  FAIL — F001 / F003
A14  PASS
```

### A01 — exact immutable WorkPacket identity/revision/digest

FAIL because canonical ordering is not closed over every nested normative collection included in the digest.

### A02 — exact Project/Slice/baseline binding

PASS. Exact identity and stale/conflict semantics are explicitly designed.

### A03 — exact external authority/policy/profile/role refs; packet cannot create authority

FAIL because supplied conformance statuses are not exact-ref-bound even though the packet refs themselves are exact.

### A04 — reproducible ContextManifest

FAIL because required context has exact hashes/provenance but no mandatory deterministic materialization reference/bundle contract.

### A05 — provider-neutral normalized intent

PASS.

### A06 — objective/scope/non-scope/acceptance/deliverable/evidence

PASS.

### A07 — Slice 2.2 required input/output mapping

PASS semantically, but implementation eligibility depends on closing F001 so external facts cannot be consumed against the wrong packet/ref.

### A08 — runtime requirements declarative / Slice 2.1 reuse

PASS.

### A09 — workspace/tool/network/credential requirements declarative / Slice 2.4 preserved

PASS.

### A10 — protected-verification transport cannot grant authority

PASS semantically, but exact authority evidence must be bound per F001.

### A11 — amendments/revisions / renewed authority / no latest

PASS.

### A12 — successor/proposed-work/exhaustion semantics

PASS.

### A13 — missing/stale/conflicting/unverifiable fail closed

FAIL at the exact-subject/evidence boundary because F001 allows detached statuses and F003 does not yet guarantee required material resolution.

### A14 — no scope leakage

PASS.

---

# 7. Required Revision 2 scope

Revision 2 should be a bounded design amendment/rework, not a replacement architecture.

It must close exactly:

```text
F001 exact-subject-bound conformance evidence
F002 recursive canonicality of every normative collection
F003 deterministic required-context materialization/reproduction contract
```

It should preserve the accepted Revision 1 architecture for:

- provider-neutral normalized planning intent;
- WorkPacket/ContextManifest content-addressed identities;
- external authority ownership;
- RoleContract mapping;
- runtime declarations;
- workspace declarations;
- protected verification separation;
- amendments;
- successor semantics;
- design economy.

No implementation is authorized by this evaluation.

---

# 8. Non-blocking clarification for Revision 2

Where WorkPacket control-plane values are mirrored into ContextManifest for model/prompt visibility—such as:

- authority/non-authority;
- RoleContract;
- policy/profile;
- accepted design;

the mirrored context should be explicitly derived from or exact-match the packet's control references.

A ContextManifest should not be able to carry a stale/conflicting control-plane instruction that is non-authoritative but still misleading to the execution model.

This can be closed naturally as part of F003 context conformance.

---

# 9. Independent disposition

```text
RLY-S23-DESIGN-EVAL-001 — REWORK

Exact evaluated design candidate:
8e3cb2df658711cd3e18d364cf19fa5332b2ab2f

Exact design blob:
d11529c5fdf068a142e79171642cdb735dc290cd

F001 exact-subject-bound conformance evidence:
OPEN / BLOCKING

F002 recursive canonical identity:
OPEN / BLOCKING

F003 deterministic required-context materialization:
OPEN / BLOCKING

A01:
FAIL

A02:
PASS

A03:
FAIL

A04:
FAIL

A05:
PASS

A06:
PASS

A07:
PASS subject to F001

A08:
PASS

A09:
PASS

A10:
PASS subject to F001

A11:
PASS

A12:
PASS

A13:
FAIL

A14:
PASS

Overall architecture:
SOUND / BOUNDED REWORK REQUIRED

Human design acceptance:
NOT ELIGIBLE

Implementation:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Production WorkPacket creation/wiring:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**REWORK is an independent evaluation outcome, not implementation or mutation authority.**
