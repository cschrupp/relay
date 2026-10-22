# Slice 2.3 — Independent Implementation Evaluation 001

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Evaluation ID:** `RLY-S23-IMPL-EVAL-001`  
**Outcome:** `REWORK`  
**Implementation authority:** `RLY-S23-IMPL-AUTH-001 — AUTHORIZED`  
**Authorized baseline:** `f0996a1909bff8dda76a455d6d88d027b4b736f2`  
**Exact evaluated candidate:** `1e978355f1fd4c5981786112f4df3a77ec89802e`  
**Reviewer role:** Independent Slice 2.3 Implementation Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

The candidate is well bounded, has green exact-head CI, preserves the non-authority architecture, and implements the majority of the accepted Slice 2.3 contract correctly.

However, three implementation defects prevent acceptance:

1. missing exact facts in plural fact tuples are classified by a prefix heuristic, so a missing middle fact becomes `UNSATISFIED` instead of the accepted `INDETERMINATE`;
2. context conformance cannot satisfy two different required context keys that intentionally reference the same exact ContextMaterialRef, even though the accepted contract is keyed by required context entries and does not forbid material reuse;
3. when a packet has no GovernanceProfileRef and external policy positively establishes "profile not required", the evaluator still requires an independent `profile_status == SATISFIED`, adding a stronger requirement than the accepted design.

These are bounded evaluator defects. They do not require model redesign, persistence, new files, or scope expansion.

The architecture-test change made for shallow GitHub checkouts is accepted as non-blocking because independent remote comparison directly establishes the exact six-file implementation surface.

---

## 1. Exact subject and ancestry

```text
Repository:
cschrupp/relay

Implementation authority:
RLY-S23-IMPL-AUTH-001 — AUTHORIZED

Authorized baseline:
f0996a1909bff8dda76a455d6d88d027b4b736f2

Implementation branch:
implementation/2.3-context-work-packet-contract

Initial implementation commit:
9141e48df80160308ece9b66bd8c67bdd72400d7

Evaluated candidate:
1e978355f1fd4c5981786112f4df3a77ec89802e
```

Exact ancestry:

```text
f0996a1909bff8dda76a455d6d88d027b4b736f2
    |
    +-- 9141e48df80160308ece9b66bd8c67bdd72400d7
    |   Implement Slice 2.3 work packet contracts
    |
    +-- 1e978355f1fd4c5981786112f4df3a77ec89802e
        Make Slice 2.3 architecture test shallow-clone safe
```

The remote implementation branch resolves exactly to the candidate.

**Ancestry:** PASS.

---

## 2. Authorized change surface

Independent comparison from the exact authorized baseline shows exactly six changed files:

```text
src/relay_engine/work_packets/__init__.py
src/relay_engine/work_packets/models.py
src/relay_engine/work_packets/evaluation.py
tests/unit/test_work_packet_models.py
tests/unit/test_work_packet_evaluation.py
tests/unit/test_work_packet_architecture.py
```

No existing production file changed.

No dependency, lockfile, CI, registry, database, migration, documentation, runtime, lifecycle, workspace, or persistence file changed.

**Scope boundary:** PASS.

---

# 3. Finding I001 — missing plural facts are misclassified by prefix position

**Severity:** BLOCKING  
**Affected design findings/criteria:** F001, A13  
**Disposition:** REWORK REQUIRED

The accepted contract distinguishes:

```text
known wrong / incompatible exact fact
    -> UNSATISFIED

missing / stale / conflicting / unverifiable required fact
    -> INDETERMINATE
```

and explicitly requires plural authority/design/protected/material fact tuples to exact-match the packet/manifest subjects.

The implementation currently detects "missing" only when the supplied tuple is a **prefix** of the expected tuple.

For authority facts:

```python
if authority_refs != packet.authority_refs:
    if authority_refs == packet.authority_refs[: len(authority_refs)]:
        AUTHORITY_BASIS_MISSING
    else:
        AUTHORITY_FACT_SET_MISMATCH
        failed = True
```

The same prefix pattern is used for:

- `accepted_design_facts`;
- `protected_verification_authority_facts`;
- `materialization_facts`.

Therefore:

```text
expected: A, B, C
actual:   A, C
```

is treated as an exact-set mismatch / known failure rather than missing fact B.

But A and C are both exact expected subjects and B is merely absent.

Under the accepted design that is:

```text
missing required evidence
-> INDETERMINATE
```

not:

```text
known incompatible evidence
-> UNSATISFIED
```

This is not just a reason-label issue: it changes the top-level conformance status.

### Required bounded correction

For every plural exact-subject fact collection, distinguish:

1. exact tuple equality -> evaluate statuses;
2. supplied subjects are an ordered subset/subsequence of expected exact subjects, with no unexpected/duplicate/reordered subject -> missing evidence -> `INDETERMINATE`;
3. any unexpected subject, duplicate/conflicting subject, or noncanonical/reordered subject -> exact-set mismatch -> `UNSATISFIED`.

This must apply to:

- authority facts;
- accepted-design facts;
- protected-verification authority facts;
- materialization facts.

Do not weaken exact-ref binding.

### Required tests

At minimum use three expected subjects and prove:

```text
missing first  -> INDETERMINATE
missing middle -> INDETERMINATE
missing last   -> INDETERMINATE

reordered      -> UNSATISFIED
unexpected     -> UNSATISFIED
extra          -> UNSATISFIED
wrong ref      -> UNSATISFIED
```

for the plural fact families above where applicable.

**I001:** OPEN / BLOCKING.

---

# 4. Finding I002 — repeated exact material refs across required context keys cannot conform

**Severity:** BLOCKING  
**Affected design findings/criteria:** F003, A04, A13  
**Disposition:** REWORK REQUIRED

The accepted contract is defined per required context key:

```text
for every WorkPacket required_context_key
    resolve exact ContextEntryRef
    derive exact ContextMaterialRef
    require exactly one matching ContextMaterializationFact
```

The design does **not** forbid two distinct ContextEntryRef values from pointing to the same exact ContextMaterialRef.

That is a legitimate representation: two governed context entries can have distinct semantic keys/classes while using the same immutable material bytes.

The implementation currently builds:

```python
facts_by_material[canonical(material_ref)] -> list[facts]
```

and then treats:

```python
len(matches) > 1
```

as:

```text
MATERIALIZATION_FACT_SET_MISMATCH
UNSATISFIED
```

Later, it also compares:

```text
fact_material_refs
==
required_material_refs
```

This creates an impossible case when two required entry keys reuse one material:

- supplying two positional facts creates `len(matches) > 1` and fails;
- supplying one fact makes the exact fact tuple shorter than the required-entry-derived material tuple and remains incomplete.

So a manifest allowed by the accepted model cannot reach SATISFIED context conformance.

### Required bounded correction

Materialization-fact matching must respect **required context entry order**, not impose global uniqueness of ContextMaterialRef.

A simple acceptable implementation is positional exact comparison:

```text
required_context_keys
    -> ordered ContextEntryRef tuple
    -> ordered ContextMaterialRef tuple

materialization_facts
    -> ordered evaluated_material_ref tuple

exact equality:
    evaluate each position

ordered-subsequence missing facts:
    INDETERMINATE

unexpected/reordered/extra facts:
    UNSATISFIED
```

Identical material refs may repeat when different required context keys point to the same exact material.

Do not add a new prohibition on material reuse; that would be a design change outside the accepted contract.

### Required tests

At minimum:

```text
two required context keys -> same exact material
two matching positional facts
    -> SATISFIED

same setup with one fact missing
    -> INDETERMINATE

same setup with one wrong material fact
    -> UNSATISFIED

same setup with fact order inconsistent with required key order
    -> UNSATISFIED when the refs differ enough to establish reordering
```

**I002:** OPEN / BLOCKING.

---

# 5. Finding I003 — no-profile case is stronger than the accepted GovernanceProfileFact semantics

**Severity:** BLOCKING  
**Affected criteria:** A03, A13  
**Disposition:** REWORK REQUIRED

The accepted scope explicitly states:

### When packet carries a GovernanceProfileRef

```text
fact policy ref exact matches
fact profile ref exact matches
profile_requirement_status == SATISFIED
profile_status == SATISFIED
```

### When packet carries no GovernanceProfileRef

```text
fact policy ref exact matches
fact evaluated_profile_ref is None
profile_requirement_status == SATISFIED
    means exact external policy positively established "not required"
```

and:

```text
missing/unknown not-required basis
-> INDETERMINATE
```

The candidate evaluates `profile_status` unconditionally:

```python
if profile_fact.profile_status is UNSATISFIED:
    GOVERNANCE_PROFILE_CONFLICT
    failed = True
elif profile_fact.profile_status is INDETERMINATE:
    GOVERNANCE_PROFILE_STALE
```

Therefore a packet with:

```text
governance_profile_ref = None

evaluated_profile_ref = None

profile_requirement_status = SATISFIED
    # external policy positively establishes no profile is required

profile_status = INDETERMINATE
    # there is no profile whose currentness can be evaluated
```

becomes INDETERMINATE.

That adds an unnecessary external fact requirement after the exact "profile not required" fact has already been positively established.

This is stronger governance than the accepted design.

### Required bounded correction

Branch evaluation by packet profile presence.

If packet has a GovernanceProfileRef:

- exact profile subject match required;
- `profile_requirement_status == SATISFIED`;
- `profile_status == SATISFIED`.

If packet has no GovernanceProfileRef:

- exact policy ref required;
- `evaluated_profile_ref is None`;
- `profile_requirement_status == SATISFIED` is sufficient to establish "not required";
- do not require a separate positive profile-status fact for a nonexistent profile.

A missing/unknown `profile_requirement_status` remains INDETERMINATE.

### Required tests

```text
no packet profile
+ evaluated_profile_ref None
+ requirement SATISFIED
+ profile_status INDETERMINATE
    -> profile condition does not make packet INDETERMINATE

no packet profile
+ requirement INDETERMINATE
    -> INDETERMINATE

packet has profile
+ profile_status INDETERMINATE
    -> INDETERMINATE

packet has profile
+ profile_status UNSATISFIED
    -> UNSATISFIED
```

**I003:** OPEN / BLOCKING.

---

# 6. Shallow-checkout architecture-test adjustment

**Disposition:** NON-BLOCKING / EXTERNAL EVIDENCE CLOSES CHANGE-SURFACE CLAIM

The first candidate commit used a test that ran:

```text
git diff <authorized-baseline>...HEAD
```

inside the test suite.

GitHub's shallow checkout did not contain the required history object, so that test was environment-dependent.

The follow-up commit replaces it with a static assertion that:

- the Slice 2.3 package contains only its three expected files;
- the Slice 2.3 unit-test family contains only its three expected tests.

That replacement does **not**, by itself, prove that an unrelated pre-existing repository file was not modified.

However, independent GitHub comparison from the exact authorized baseline directly proves the complete candidate delta contains only the six authorized files.

Therefore:

- the candidate's actual scope is valid;
- the shallow-clone repair is not a scope violation;
- no implementation rejection is required solely for this test change.

For future work, repository-change-surface proof should remain a governance/CI/review comparison against the exact candidate rather than relying on a unit test that assumes ancestor objects are locally present.

---

# 7. Positive implementation findings

## Exact authorized surface

**PASS**

Exactly six authorized files.

## WorkPacket / ContextManifest immutability and identity

**PASS**

Canonical JSON and SHA-256 helpers exist with literal fixed vectors.

## F002 recursive canonical identity

**PASS**

The candidate correctly rejects noncanonical ordering for the accepted nested/top-level normative collections and rejects stable-identity conflicts.

No silent sorting is used to accept noncanonical input.

## SourceBaselineRef

**PASS**

Existing Baseline is reused and canonicalized externally without modifying the domain model.

## Planning normalization

**PASS**

Provider-neutral, exact-source-provenanced, COMPLETE/INCOMPLETE/INDETERMINATE model is implemented.

## Context material closed union

**PASS**

Exactly:

```text
ArtifactMaterialRef
RepositoryContentMaterialRef
CapturedMaterialRef
```

No digest-only material variant.

## Materialization boundary

**PASS**, except I002 tuple matching.

No storage/resolver/network/filesystem materialization is implemented.

## Slice 2.2 reuse

**PASS**

Actual accepted `RoleApplicabilityEvaluation`, `RoleContractRef`, `RequirementStatus`, `RoleOutputRequirement`, and `VerificationAssetPermission` are reused.

## Slice 2.1 reuse

**PASS**

Runtime values are declarations only.

No AgentRuntime protocol/invocation.

## WorkPacket != authority

**PASS**

No authorization state/function is introduced.

## Control mirrors

**PASS**

Exact WorkPacket subject digest binding and content-digest checks are implemented.

## Protected verification

**PASS**, except missing-fact position handling in I001.

Permission/reference semantics do not issue mutation authority.

## Identity conflict evaluators

**PASS**

No latest/max/best-match resolution.

## DB / lifecycle / runtime / workspace boundaries

**PASS**

No unauthorized integration or mutation detected.

---

# 8. A01–A14 disposition

```text
A01 PASS
A02 PASS
A03 REWORK — I003
A04 REWORK — I002
A05 PASS
A06 PASS
A07 PASS
A08 PASS
A09 PASS
A10 PASS subject to I001 missing-fact correction
A11 PASS
A12 PASS
A13 REWORK — I001 / I002 / I003
A14 PASS
```

### A01

PASS.

Canonical packet/manifest identity and fixed digest vectors are implemented.

### A02

PASS.

Project/Slice/Baseline exact bindings are implemented and conformance checks exact manifest/project/slice identity.

### A03

REWORK.

Exact authority/policy/profile/role refs are implemented, but the no-profile path adds a stronger requirement than accepted.

### A04

REWORK.

Exact material refs/materialization facts are implemented, but valid reuse of the same exact material across multiple required context entries cannot conform.

### A05

PASS.

Provider-neutral normalized intent.

### A06

PASS.

Scope/acceptance/evidence/deliverable/hard-stop values are explicit and digest-bound.

### A07

PASS.

Accepted Slice 2.2 types are reused.

### A08

PASS.

Runtime declarations only.

### A09

PASS.

Workspace declarations only.

### A10

PASS semantically, subject to I001 so missing protected facts retain the required INDETERMINATE distinction.

### A11

PASS.

Normative changes alter digests/revisions; no latest lookup.

### A12

PASS.

Successor ref remains non-authoritative.

### A13

REWORK.

Fail-closed exists, but the accepted UNSATISFIED-vs-INDETERMINATE taxonomy is not preserved in the three identified edge cases.

### A14

PASS.

No forbidden scope leakage.

---

# 9. Exact-head quality evidence

Exact-head GitHub Actions independently verified:

```text
Run:
39806862801

Branch:
implementation/2.3-context-work-packet-contract

Head:
1e978355f1fd4c5981786112f4df3a77ec89802e

Status:
COMPLETED

Conclusion:
SUCCESS
```

Observed CI steps:

```text
Sync environment      SUCCESS
Ruff format           SUCCESS
Ruff lint             SUCCESS
Pyright               SUCCESS
Tests                 SUCCESS
Build                 SUCCESS
```

The executor additionally reports:

```text
full pytest:
1019 passed

git diff --check:
PASS

working tree:
CLEAN
```

Green tests/CI are engineering evidence; they do not override the contract defects above.

---

# 10. Required bounded rework

A corrective implementation should remain inside the existing six-file surface.

Expected files likely requiring changes:

```text
src/relay_engine/work_packets/evaluation.py
tests/unit/test_work_packet_evaluation.py
```

Changes to models should not be necessary unless the implementer identifies an exact accepted-contract reason.

The rework should:

1. replace prefix-only missing-fact detection with exact ordered-subsequence/set semantics preserving missing vs mismatch;
2. make materialization facts correspond to required context entries positionally without globally forbidding repeated exact material refs;
3. make no-profile evaluation depend on the exact positive "profile not required" fact, not a redundant profile-status fact;
4. add focused regression tests for all three findings;
5. preserve F002 canonicality and every existing architecture boundary.

No DB, runtime, workspace, resolver/storage, lifecycle, or downstream change is needed.

---

# 11. Independent disposition

```text
RLY-S23-IMPL-EVAL-001 — REWORK

Exact candidate:
1e978355f1fd4c5981786112f4df3a77ec89802e

Authorized baseline:
f0996a1909bff8dda76a455d6d88d027b4b736f2

Authorized six-file scope:
PASS

Exact-head CI:
GREEN — 39806862801

F001 exact-subject binding:
PARTIAL — exact refs correct; missing-fact tri-state defect remains

F002 recursive canonical identity:
PASS

F003 deterministic materialization contract:
PARTIAL — exact material model correct; repeated-material required-entry handling defective

WorkPacket != authority:
PASS

Human root authority external:
PASS

I001 missing plural fact tri-state:
OPEN / BLOCKING

I002 repeated required material refs:
OPEN / BLOCKING

I003 no-profile stronger-than-design condition:
OPEN / BLOCKING

Human technical acceptance:
NOT ELIGIBLE

Implementation closure:
NOT ELIGIBLE

Production wiring:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Context storage / resolver:
NOT AUTHORIZED

Workspace enforcement:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

This REWORK evaluation is evidence only. It does not authorize corrective mutation.

A bounded corrective implementation authorization remains a Human Authority action.
