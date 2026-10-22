# Slice 2.2 — Independent Implementation Evaluation — Candidate 1

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Slice:** 2.2 — Role Contracts  
**Evaluation ID:** `RLY-S22-IMPL-EVAL-001`  
**Outcome:** `REWORK`  
**Implementation authority:** `RLY-S22-IMPL-AUTH-001 — AUTHORIZED`  
**Authorized implementation baseline:** `4cde30ef8b307e0483bcd94fe15a723b8003fbf2`  
**Exact evaluated candidate:** `e9433398af33ffd5c666105fcddaf2cb452d867a`  
**Reviewer role:** Independent Slice 2.2 Implementation Evaluator — GPT-5.6 Sol

## Decision

```text
REWORK
```

The candidate is correctly bounded, structurally clean, and implements most of the accepted Role Contracts design. However, two authority-critical semantic gaps remain:

1. applicability is not bound to an exact `RoleContractRef`;
2. protected-verification mutation/approval checks can report `SATISFIED` without any separate mutation-authority fact.

Both defects weaken design invariants that were explicitly introduced to close prior design-review findings. They must be resolved before technical acceptance.

No implementation acceptance, production wiring, lifecycle mutation, or downstream Slice authority is granted.

---

## 1. Exact subject / ancestry / scope

The candidate comparison is:

```text
base:
4cde30ef8b307e0483bcd94fe15a723b8003fbf2

candidate:
e9433398af33ffd5c666105fcddaf2cb452d867a

ahead:
1 commit

behind:
0

total commits:
1
```

Exactly the six authorized files were added:

```text
src/relay_engine/role_contracts/__init__.py
src/relay_engine/role_contracts/models.py
src/relay_engine/role_contracts/evaluation.py
tests/unit/test_role_contract_models.py
tests/unit/test_role_contract_evaluation.py
tests/unit/test_role_contract_architecture.py
```

No existing production file, dependency, schema, database, runtime adapter, lifecycle path, governance mutation path, Work Packet path, workspace-enforcement path, or Phase 3 path changed.

**Scope / ancestry:** PASS.

---

## 2. Positive implementation findings

The evaluator accepts the candidate implementation of:

- immutable strict `DomainModel`-based Role Contract values;
- bounded `RoleKey`;
- the four accepted `RoleClass` values;
- exact schema-v1 `RoleAction` vocabulary;
- complete per-schema action partition;
- disjoint allowed/prohibited actions;
- explicit `RoleInputRequirement` and `RoleOutputRequirement`;
- protected-verification permission vocabulary;
- stable assurance-property references without reimplementing the assurance engine;
- canonical JSON + SHA-256 `ContentDigest`;
- exact `RoleContractRef`;
- same-policy-group role-key/revision/digest conflict detection;
- `RoleActionBinding`;
- `PERMITTED_BY_ROLE != AUTHORIZED`;
- Human-authority actor-kind restriction;
- required-input/output tri-state evaluation;
- policy-selected role separation over actor/execution/session;
- reuse of Slice 2.1 `RuntimeCapability`, `RuntimeProvenance`, and `RuntimeSessionRef`;
- requested-versus-actual runtime identity separation;
- successor-resolution to bounded work-disposition mapping;
- no role UUID;
- no role database/catalog/global registry;
- no runtime/provider/network calls;
- no governance/lifecycle/Human-control mutation imports;
- no `PROPOSED_WORK` persistence subsystem;
- root Human Authority remaining external to the package.

The package direction remains small and consistent with the accepted design.

---

## 3. F001 — Applicability result is detached from the exact RoleContractRef

**Severity:** BLOCKING

The accepted design closed its prior F002 by requiring an exact prospective `ApplicableRoleContractBinding` containing, conceptually:

```text
exact governed subject
exact RoleContractRef
exact PolicyBasis
GovernanceProfile ref where applicable
authority basis refs
```

and requiring policy/profile or valid Human Authority to select the **exact RoleContractRef**.

The implementation instead defines:

```python
ApplicableRoleContractFacts(
    contract_identity_valid: RequirementStatus,
    governed_subject_bound: RequirementStatus,
    policy_basis_current: RequirementStatus,
    governance_profile_current: RequirementStatus,
    selection_source: SelectionSource | None,
    selection: ContractSelection,
    authority_basis_current: RequirementStatus,
    supersession_clear: RequirementStatus,
)
```

and:

```python
evaluate_role_contract_applicability(facts)
    -> RoleContractApplicability
```

The facts contain no `RoleContractRef`, no selected ref, and no exact subject/reference identity. `ContractSelection.SELECTS_THIS_CONTRACT` is therefore deictic: the evaluator has no contract object/ref to which “this contract” is bound.

### Failure mode

A caller can obtain:

```text
APPLICABLE
```

from a facts object that semantically described Contract A, then separately call:

```python
evaluate_role_action(contract_b, actor, action)
```

because no implementation object binds the applicability result to Contract A's exact ref.

The candidate therefore preserves:

```text
valid digest alone != applicability
```

but does **not** preserve the stronger accepted invariant:

```text
APPLICABLE
is a judgment about one exact RoleContractRef
for one exact governed subject/policy basis
```

The implementation scope explicitly required the pure applicability input to represent **exact contract content/ref identity** and the accepted design's applicability sequence is:

```text
exact RoleContractRef selected/bound
    -> role applicability evaluated
    -> role/action evaluation
```

### Required rework

Bind the applicability input/result to an exact `RoleContractRef`.

A minimal bounded correction is sufficient. For example:

```python
ApplicableRoleContractFacts(
    role_contract_ref: RoleContractRef,
    ...
    selected_role_contract_ref: RoleContractRef | None,
    ...
)
```

or a mechanically equivalent exact-reference structure.

The evaluator must prove that the authoritative selection, when present, selects the exact evaluated ref.

Required tests:

```text
facts for Contract A cannot make Contract B applicable
selected exact ref == evaluated exact ref -> may proceed
selected exact ref != evaluated exact ref -> NOT_APPLICABLE
missing/unresolved exact selected ref -> INDETERMINATE
conflicting exact selections -> INDETERMINATE
valid digest/status booleans without exact ref binding -> cannot produce APPLICABLE
```

Do not introduce PolicyBasis/GovernanceProfile persistence or a role registry.

---

## 4. F002 — Protected-verification mutation authority is not represented

**Severity:** BLOCKING

The accepted design requires protected-verification evaluation to combine:

```text
asset operation
+
RoleContract verification permission
+
applicable GovernanceProfile requirement
+
exact separate authority where mutation/approval is required
```

The authorized Codex scope further froze:

> Permission absence or unknown required classification/mutation authority must fail closed.

The implementation currently provides:

```python
evaluate_verification_asset_permission(
    granted,
    required,
    classification_known: bool,
) -> RequirementStatus
```

Its logic is effectively:

```text
classification unknown -> INDETERMINATE
required permission present -> SATISFIED
required permission absent -> UNSATISFIED
```

No mutation/approval authority fact is supplied or checked.

Therefore:

```text
required = MODIFY
granted includes MODIFY
classification_known = true
```

returns:

```text
SATISFIED
```

even when separate mutation authority is absent or unknown.

The same problem applies to `APPROVE_MUTATION` and any other operation whose applicable policy requires separate mutation authority.

This violates:

```text
role permission != mutation authority
evaluator role != mutation authority
repository write capability != protected-asset mutation authority
```

### Required rework

Keep concrete filesystem enforcement in Slice 2.4, but add the accepted **semantic authority fact** to the pure evaluator.

A bounded shape is sufficient, such as:

```python
evaluate_verification_asset_permission(
    granted,
    required,
    *,
    classification_status,
    separate_authority_status,
    separate_authority_required,
) -> RequirementStatus
```

or an equivalent immutable fact object.

Required behavior:

```text
classification unknown -> INDETERMINATE
role permission absent -> UNSATISFIED
required separate authority absent/invalid -> UNSATISFIED
required separate authority unknown/stale/conflicting -> INDETERMINATE
role permission present + required exact authority satisfied -> SATISFIED
operation with policy-established no separate-authority requirement -> evaluate permission normally
```

Required tests must explicitly cover `MODIFY` and `APPROVE_MUTATION`.

No governance mutation call or authority issuance belongs in this package; it consumes already-established authority facts only.

---

## 5. CI / quality-gate classification

Candidate GitHub Actions run:

```text
Run:
39705771811

Head:
e9433398af33ffd5c666105fcddaf2cb452d867a

Conclusion:
FAILURE

Failed step:
Ruff format

Later lint / Pyright / tests / build:
SKIPPED
```

This red CI is real, but the evaluator confirmed it is inherited from the authorized baseline rather than caused by the candidate:

- authorized-baseline CI runs `39704046658` and `39702495026` also fail at the same repository-wide Ruff-format step before later checks;
- the reported offending immutable file
  `docs/reviews/SLICE_1_10_DOGFOOD_B4_REV2_IMPLEMENTATION_EVALUATION_001.md`
  has Git blob
  `2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8`
  at both baseline and candidate;
- the candidate did not modify that file.

Disposition:

```text
candidate-introduced CI regression:
NO

exact-head CI green:
NO

baseline repository quality condition:
PRE-EXISTING / UNRESOLVED
```

This evaluation does not authorize modifying immutable historical evidence to make Ruff green.

The operator-reported local results—focused Role Contract tests, full pytest `970 passed`, Ruff lint, Pyright, build, changed-file formatting, and diff check—are consistent with the candidate structure but remain execution evidence reported by the implementer rather than a substitute for exact-head CI.

Because this implementation evaluation already returns REWORK on F001/F002, no CI waiver or exception decision is required here. The inherited CI condition must remain explicit at the next acceptance gate.

---

## 6. Accepted-design / implementation-scope disposition

```text
A01 identity separation:
PASS

A02 capability != authority:
PASS

A03 actions / required inputs / outputs / evidence:
PASS

A04 role separation / protected assets:
FAIL — F002 separate mutation-authority fact missing

A05 requested/actual runtime provenance:
PASS

A06 exact work authority cannot be inferred:
PASS

A07 bounded decomposition:
PASS at semantic boundary

A08 PROPOSED_WORK non-authority:
PASS at implemented semantic boundary / no persistence added

A09 BACKLOG_EXHAUSTED:
PASS

A10 fail-closed missing/stale/conflicting authority/evidence:
FAIL — F001 exact role binding and F002 mutation authority are incomplete

A11 downstream ownership preserved:
PASS
```

Prior design findings:

```text
Design F001 input/output semantics:
MATERIALIZED

Design F002 applicable/accepted RoleContract binding:
PARTIALLY MATERIALIZED / IMPLEMENTATION DEFECT -> current F001

Design F003 role key/revision/digest conflict:
MATERIALIZED
```

Human root-authority bootstrap invariant:

```text
PASS
```

---

## 7. Required rework boundary

Rework must remain within the existing six authorized files.

Expected production changes:

```text
src/relay_engine/role_contracts/models.py
src/relay_engine/role_contracts/evaluation.py
src/relay_engine/role_contracts/__init__.py
```

only as needed.

Expected tests:

```text
tests/unit/test_role_contract_evaluation.py
tests/unit/test_role_contract_models.py
tests/unit/test_role_contract_architecture.py
```

only as needed.

No new production file, dependency, ID prefix, persistence, schema, role catalog, governance engine, Work Packet, workspace enforcement, runtime call, or operational-state mutation is required.

If fixing F001/F002 appears to require any of those, STOP and escalate rather than expanding scope.

---

## 8. Independent disposition

```text
RLY-S22-IMPL-EVAL-001 — REWORK

Exact evaluated candidate:
e9433398af33ffd5c666105fcddaf2cb452d867a

F001:
OPEN — exact applicability not bound to exact RoleContractRef

F002:
OPEN — protected-verification mutation authority not represented

Candidate scope:
PASS

Candidate ancestry:
PASS

Candidate-introduced CI regression:
NO

Exact-head CI:
RED / inherited baseline Ruff-format condition

Human technical acceptance:
NOT ELIGIBLE YET

Implementation acceptance:
NOT GRANTED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

Produce a bounded successor candidate resolving F001/F002 and return it for independent implementation re-review.

**REWORK is evidence, not authority.**
