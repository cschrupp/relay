# Slice 2.3 — Independent Implementation Evaluation 002

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Evaluation ID:** `RLY-S23-IMPL-EVAL-002`  
**Outcome:** `ACCEPT`  
**Original implementation authority:** `RLY-S23-IMPL-AUTH-001 — AUTHORIZED`  
**Corrective authority:** `RLY-S23-IMPL-REWORK-AUTH-001 — AUTHORIZED`  
**Original candidate:** `1e978355f1fd4c5981786112f4df3a77ec89802e`  
**Prior evaluation:** `RLY-S23-IMPL-EVAL-001 — REWORK`  
**Prior evaluation commit:** `b9ffc43eb0f67b3b5a808df7b6709befd872cb80`  
**Exact corrective candidate:** `861ccb6bda528a98e1f570a32dcddc61358732e7`  
**Reviewer role:** Independent Slice 2.3 Implementation Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The bounded corrective candidate closes all three blocking findings from `RLY-S23-IMPL-EVAL-001` without widening implementation scope.

The accepted implementation now:

- preserves exact-subject binding;
- distinguishes missing evidence from known mismatch independent of tuple position;
- permits distinct required context keys to reuse the same exact immutable material reference;
- implements the accepted no-profile GovernanceProfile semantics;
- preserves recursive canonical identity;
- preserves WorkPacket != authority;
- preserves Human root authority outside Slice 2.3;
- preserves the no-persistence / no-resolver / no-runtime / no-workspace-enforcement architecture boundary.

No blocking implementation finding remains.

Independent implementation ACCEPT does not itself grant Human technical acceptance, closure, production wiring, Slice 2.4 authority, or Phase 3 authority.

---

## 1. Exact reviewed lineage

```text
Repository:
cschrupp/relay

Authorized implementation baseline:
f0996a1909bff8dda76a455d6d88d027b4b736f2

Original implementation candidate:
1e978355f1fd4c5981786112f4df3a77ec89802e

Independent evaluation 001:
RLY-S23-IMPL-EVAL-001 — REWORK

Evaluation-001 commit:
b9ffc43eb0f67b3b5a808df7b6709befd872cb80

Corrective authority:
RLY-S23-IMPL-REWORK-AUTH-001 — AUTHORIZED
68022bbf41f5ca203f88dbbcfe9d2afc75c9b807
(external governance fact on design lineage)

Corrective candidate:
861ccb6bda528a98e1f570a32dcddc61358732e7

Implementation branch:
implementation/2.3-context-work-packet-contract
```

Corrective ancestry:

```text
b9ffc43eb0f67b3b5a808df7b6709befd872cb80
    |
    +-- 861ccb6bda528a98e1f570a32dcddc61358732e7
```

Before this evaluation record was written, the remote implementation branch resolved exactly to the corrective candidate.

**Lineage:** PASS.

---

## 2. Corrective change surface

Independent comparison from the REWORK evaluation commit to the corrective candidate shows exactly two changed files:

```text
src/relay_engine/work_packets/evaluation.py
tests/unit/test_work_packet_evaluation.py
```

This exactly matches `RLY-S23-IMPL-REWORK-AUTH-001`.

No model file changed.

No canonical JSON/digest implementation changed.

No package exports changed.

No dependency, lockfile, CI, documentation, registry, DB, migration, lifecycle, runtime, workspace, resolver/storage, or downstream file changed.

**Corrective scope:** PASS.

---

# 3. I001 — missing plural facts tri-state

**Prior status:** OPEN / BLOCKING  
**Disposition:** CLOSED

The rejected candidate used prefix-only logic to distinguish missing facts from mismatches.

The corrective implementation introduces a pure ordered-subsequence matcher:

```python
_ordered_subsequence_indices(actual, expected)
```

Normative behavior now matches the corrective authority:

```text
actual == expected
    -> evaluate exact statuses

actual is an ordered subsequence of expected
    -> missing evidence
    -> INDETERMINATE

actual contains unexpected / duplicate / conflicting / reordered subject
    -> no ordered-subsequence match
    -> UNSATISFIED
```

This behavior is applied to:

- authority facts;
- accepted-design facts;
- protected-verification authority facts;
- materialization facts.

### Authority facts

`authority_refs` are mapped against `packet.authority_refs`.

A missing first/middle/last authority is now `AUTHORITY_BASIS_MISSING` without setting the known-failure flag.

Unexpected/reordered/duplicate subjects remain `AUTHORITY_FACT_SET_MISMATCH` and UNSATISFIED.

### Accepted-design facts

Accepted Artifact subjects use the same ordered-subsequence semantics.

Missing expected artifacts are `ACCEPTED_DESIGN_BASIS_MISSING` / INDETERMINATE.

Wrong exact Artifact subjects remain a set mismatch / UNSATISFIED.

### Protected-verification facts

Facts are first bound to exact `ProtectedVerificationRequirementRef` subjects.

Missing subjects are `PROTECTED_VERIFICATION_AUTHORITY_INDETERMINATE`.

Exact unexpected/reordered/wrong subjects remain `PROTECTED_VERIFICATION_FACT_SET_MISMATCH`.

For supplied valid subjects, the implementation correctly maps each fact back to its original expected requirement position before comparing `evaluated_authority_ref` and status.

### Materialization facts

Materialization facts now use the same ordered-subsequence mechanism in required-context-key order.

Missing material evidence remains unavailable/indeterminate.

Unexpected/wrong/reordered exact material subjects remain `MATERIALIZATION_FACT_SET_MISMATCH` / UNSATISFIED.

### Regression coverage

The corrective tests create three expected subjects for all four plural families and parameterize:

```text
missing first
missing middle
missing last
```

Each is verified as `INDETERMINATE`.

Existing negative tests continue to prove wrong/extra/reordered exact subjects remain `UNSATISFIED`.

The shared exact-subject matcher is small, deterministic, and does not weaken F001.

**I001:** CLOSED.

---

# 4. I002 — repeated exact material refs across required context keys

**Prior status:** OPEN / BLOCKING  
**Disposition:** CLOSED

The accepted design permits:

```text
ContextEntryRef key A
    -> ContextMaterialRef X

ContextEntryRef key B
    -> ContextMaterialRef X
```

because entry semantic identity and material byte identity are separate concepts.

The rejected candidate grouped materialization facts globally by material identity, which made repeated exact material refs impossible to satisfy.

The corrective implementation now derives:

```text
packet.required_context_keys
    -> ordered required ContextEntryRef sequence
    -> ordered required ContextMaterialRef sequence
```

and compares the supplied materialization-fact subject sequence using positional ordered-subsequence semantics.

It then evaluates each required position independently.

Therefore:

```text
required key A -> material X
required key B -> material X

fact position A -> material X
fact position B -> material X
    -> valid
```

The same exact material ref may legitimately appear at multiple required positions.

### Missing repeated position

One fact for two required positions is an ordered subsequence.

The missing required position receives unavailable/indeterminate treatment.

### Wrong material

A supplied material ref that cannot match the expected ordered subject sequence remains an exact subject mismatch and UNSATISFIED.

### Regression coverage

The new test explicitly constructs two required context entries with distinct keys and the same exact material ref and verifies:

```text
two matching positional materialization facts
    -> SATISFIED

one positional fact missing
    -> INDETERMINATE
```

Existing wrong-material tests remain UNSATISFIED.

No new material uniqueness restriction was introduced.

No models changed.

**I002:** CLOSED.

---

# 5. I003 — absent GovernanceProfileRef semantics

**Prior status:** OPEN / BLOCKING  
**Disposition:** CLOSED

The accepted contract distinguishes two paths.

## Packet has GovernanceProfileRef

The evaluator still requires:

- exact PolicyBasisRef subject;
- exact GovernanceProfileRef subject;
- `profile_requirement_status == SATISFIED`;
- `profile_status == SATISFIED`.

An INDETERMINATE or UNSATISFIED profile status remains fail-closed.

## Packet has no GovernanceProfileRef

The evaluator now requires:

- exact PolicyBasisRef subject;
- `evaluated_profile_ref is None`;
- `profile_requirement_status == SATISFIED`.

Once the exact external policy fact positively establishes that no profile is required, `profile_status` is no longer evaluated as a separate requirement for a nonexistent profile.

This exactly matches the Human-accepted scope.

### Regression coverage

The new test parameterizes absent-profile facts with:

```text
profile_requirement_status = SATISFIED

profile_status = INDETERMINATE
or
profile_status = UNSATISFIED
```

and verifies that neither nonexistent-profile status changes an otherwise conforming packet from SATISFIED.

The prior test still proves:

```text
no profile
+ profile requirement INDETERMINATE
    -> INDETERMINATE
```

Existing-profile subject mismatch and status behavior remain fail-closed.

**I003:** CLOSED.

---

# 6. Preservation of prior accepted implementation behavior

## F001 exact-subject binding

**PASS**

The corrective ordered-subsequence mechanism does not allow a wrong subject to satisfy another subject.

It only distinguishes absence from known mismatch.

Packet A facts still cannot satisfy Packet B.

## F002 recursive canonical identity

**PASS / UNCHANGED**

No model or canonicalization file changed in the corrective candidate.

The previously reviewed implementation remains intact:

- canonical Baseline tuples;
- canonical NormalizedEngineeringIntent tuples;
- canonical ContextManifest entries;
- canonical WorkPacket tuples;
- fixed literal JSON/SHA-256 vectors;
- stable-identity collision rejection;
- no silent sorting.

## F003 deterministic materialization contract

**PASS**

Materialization remains exact-ref-bound and externally supplied.

The I002 correction changes only positional fact association; it does not weaken:

- exact material refs;
- content digest verification;
- provenance digest verification;
- source/material compatibility;
- resolver/version semantics;
- unavailable -> INDETERMINATE;
- mismatch -> UNSATISFIED.

## WorkPacket != authority

**PASS / UNCHANGED**

No authority state or issuance path exists.

```text
SATISFIED != AUTHORIZED
```

remains true.

## Human root authority

**PASS / EXTERNAL**

No root-authority creation or validation is implemented.

## Slice 2.1 / 2.2 / 2.4 / Phase 3 boundaries

**PASS**

No corrective change touches those boundaries.

---

# 7. A01–A14 final implementation disposition

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

PASS — deterministic canonical packet/manifest identity remains intact.

### A02

PASS — exact Project/Slice/Baseline binding remains intact.

### A03

PASS — exact authority/policy/profile/role binding now matches the accepted no-profile semantics.

### A04

PASS — deterministic materialization supports valid repeated-material context entries.

### A05

PASS — normalized intent unchanged.

### A06

PASS — scope/evidence/deliverable/hard-stop contract unchanged.

### A07

PASS — exact Slice 2.2 RoleApplicabilityEvaluation reuse unchanged.

### A08

PASS — runtime declarations only.

### A09

PASS — workspace declarations only.

### A10

PASS — missing protected-verification evidence preserves INDETERMINATE; wrong exact subjects remain UNSATISFIED.

### A11

PASS — amendment/digest/no-latest behavior unchanged.

### A12

PASS — successor non-authority semantics unchanged.

### A13

PASS — missing/stale/unverifiable evidence is now consistently INDETERMINATE, while known mismatches remain UNSATISFIED.

### A14

PASS — no DB/RAG/runtime/workspace/2.4/Phase3 scope leakage.

---

# 8. Exact-head validation evidence

Exact-head GitHub Actions independently verified:

```text
Run:
39815430841

Branch:
implementation/2.3-context-work-packet-contract

Head:
861ccb6bda528a98e1f570a32dcddc61358732e7

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

Executor-reported local evidence:

```text
focused model tests:
PASS

focused evaluation tests:
PASS

focused architecture tests:
PASS

full pytest:
1034 passed

git diff --check:
PASS

worktree:
CLEAN
```

The exact-head CI and independent source review agree.

---

# 9. No remaining implementation blockers

```text
I001:
CLOSED

I002:
CLOSED

I003:
CLOSED

F001:
PASS

F002:
PASS

F003:
PASS

A01-A14:
ALL PASS
```

No further implementation rework is required for the accepted Slice 2.3 contract.

---

# 10. Independent disposition

```text
RLY-S23-IMPL-EVAL-002 — ACCEPT

Exact corrective candidate:
861ccb6bda528a98e1f570a32dcddc61358732e7

Original implementation authority:
RLY-S23-IMPL-AUTH-001 — AUTHORIZED

Corrective authority:
RLY-S23-IMPL-REWORK-AUTH-001 — AUTHORIZED

Authorized corrective file surface:
PASS

Exact-head CI:
GREEN — 39815430841

I001:
CLOSED

I002:
CLOSED

I003:
CLOSED

F001 exact-subject binding:
PASS

F002 recursive canonical identity:
PASS

F003 deterministic materialization contract:
PASS

WorkPacket != authority:
PASS

Human root authority external:
PASS

A01-A14:
ALL PASS

Implementation:
INDEPENDENTLY ACCEPTED

Human technical acceptance:
PENDING

Slice 2.3 closure:
NOT AUTHORIZED / NOT COMPLETE

Production WorkPacket wiring:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Context storage / material resolver:
NOT AUTHORIZED

Runtime/provider/model execution:
NOT AUTHORIZED

Workspace enforcement:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

Independent implementation ACCEPT does not itself grant Human technical acceptance, closure, downstream authority, or canonical promotion.
