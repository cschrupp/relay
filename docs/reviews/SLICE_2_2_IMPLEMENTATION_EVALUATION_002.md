# Slice 2.2 — Independent Implementation Evaluation — Rework 1

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Slice:** 2.2 — Role Contracts  
**Evaluation ID:** `RLY-S22-IMPL-EVAL-002`  
**Outcome:** `ESCALATE`  
**Implementation authority:** `RLY-S22-IMPL-AUTH-001 — AUTHORIZED`  
**Authorized implementation baseline:** `4cde30ef8b307e0483bcd94fe15a723b8003fbf2`  
**Prior implementation candidate:** `e9433398af33ffd5c666105fcddaf2cb452d867a`  
**Prior evaluation:** `RLY-S22-IMPL-EVAL-001 — REWORK`  
**Exact rework candidate:** `4400bd1da0db04e41077c3a6ed1c16d258104ba5`  
**Reviewer role:** Independent Slice 2.2 Implementation Evaluator — GPT-5.6 Sol

## Decision

```text
ESCALATE
```

The bounded rework closes both implementation defects from `RLY-S22-IMPL-EVAL-001`.

No remaining Role Contracts implementation defect was found in the reviewed rework.

However, `RLY-S22-IMPL-AUTH-001` explicitly requires GitHub Actions CI to pass on the exact candidate SHA when the branch workflow runs. The exact rework head remains red at repository-wide Ruff format because of a pre-existing unchanged immutable historical document outside the authorized implementation scope.

The independent evaluator cannot silently waive an explicit Human quality contract. Therefore the code is **technically ready**, but overall implementation acceptance must escalate for a Human decision on the inherited CI condition.

No Human technical acceptance or implementation acceptance is granted by this record.

---

## 1. Exact subject / ancestry / rework scope

Rework comparison:

```text
parent:
2bbe9541e41fa4cbfcd5cc2a4c66556a7944a42e

rework candidate:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

ahead:
1 commit

behind:
0

total commits:
1
```

The rework modifies only five previously authorized files:

```text
src/relay_engine/role_contracts/__init__.py
src/relay_engine/role_contracts/evaluation.py
src/relay_engine/role_contracts/models.py
tests/unit/test_role_contract_architecture.py
tests/unit/test_role_contract_evaluation.py
```

The sixth planned unit-test file is unchanged.

No existing non-Role-Contract production file, dependency, schema, database, runtime adapter, lifecycle/governance mutation path, Work Packet path, workspace-enforcement path, or Phase 3 path changed.

Remote branch `implementation/2.2-role-contracts` resolves exactly to:

`4400bd1da0db04e41077c3a6ed1c16d258104ba5`

at review time.

**Scope / ancestry:** PASS.

---

## 2. F001 closure — applicability is now bound to exact RoleContractRef

**Prior status:** BLOCKING  
**Disposition:** CLOSED

The rework changes `ApplicableRoleContractFacts` to carry:

```python
evaluated_role_contract_ref: RoleContractRef
selected_role_contract_refs: tuple[RoleContractRef, ...]
```

and changes applicability evaluation to return:

```python
RoleApplicabilityEvaluation(
    role_contract_ref=<exact evaluated ref>,
    status=<APPLICABLE | NOT_APPLICABLE | INDETERMINATE>,
    reason=...
)
```

The evaluator now establishes exact-reference semantics:

- zero selected refs -> `INDETERMINATE`;
- multiple/conflicting selected refs -> `INDETERMINATE`;
- exactly one selected ref different from the evaluated ref -> `NOT_APPLICABLE`;
- exact matching selected/evaluated ref with otherwise satisfied current facts -> `APPLICABLE`;
- contradictory selection label/ref facts remain fail-closed.

Most importantly, `evaluate_role_action()` now requires a `RoleApplicabilityEvaluation` and independently checks:

```text
applicability.role_contract_ref
    ==
role_contract_ref(contract)

AND

applicability.status == APPLICABLE
```

Otherwise it returns `INDETERMINATE`.

Therefore an applicability result for Contract A cannot authorize role evaluation against Contract B.

This restores the accepted design sequence:

```text
exact RoleContractRef selected/bound
    -> exact-ref applicability evaluation
    -> role action evaluation for that same exact contract
```

No PolicyBasis/GovernanceProfile persistence, role registry, or new authority system was introduced.

**F001:** CLOSED.

---

## 3. F002 closure — protected mutation/approval requires external authority fact

**Prior status:** BLOCKING  
**Disposition:** CLOSED

The rework extends the pure protected-verification evaluator with:

```python
separate_authority_status: RequirementStatus | None
```

For:

```text
MODIFY
APPROVE_MUTATION
```

the result now requires both:

1. the Role Contract semantic permission; and
2. an externally established separate-authority status.

Behavior is now:

```text
classification unknown
    -> INDETERMINATE

role permission absent
    -> UNSATISFIED

MODIFY / APPROVE_MUTATION
+ separate authority missing
    -> INDETERMINATE

MODIFY / APPROVE_MUTATION
+ authority UNSATISFIED
    -> UNSATISFIED

MODIFY / APPROVE_MUTATION
+ authority INDETERMINATE
    -> INDETERMINATE

MODIFY / APPROVE_MUTATION
+ authority SATISFIED
    -> SATISFIED
```

Non-mutating operations such as READ do not require a fabricated mutation-authority fact.

This preserves:

```text
role permission != mutation authority
evaluator role != mutation authority
repository write capability != protected-asset mutation authority
```

The package only consumes already-established authority status. It does not issue authority or call governance/Human-control mutation paths.

**F002:** CLOSED.

---

## 4. Rework regression / architecture assessment

The rework preserves the previously accepted properties:

- immutable digest-bound `RoleContract`;
- complete schema-v1 action classification;
- exact `RoleContractRef`;
- role-key/revision/digest conflict detection;
- `PERMITTED_BY_ROLE != AUTHORIZED`;
- Human root authority external to Role Contracts;
- tri-state required input/output checks;
- policy-selected actor/execution/session separation;
- requested-versus-actual runtime provenance separation;
- no actual provider/model inference;
- no role catalog/database;
- no persistence;
- no lifecycle mutation;
- no runtime calls;
- no latest/max/best-match contract resolver;
- no `PROPOSED_WORK` persistence;
- successor tri-state and bounded `BACKLOG_EXHAUSTED`;
- no downstream Slice 2.3/2.4 or Phase 3 implementation.

No new implementation finding is opened.

---

## 5. Accepted-design / authority criteria after rework

```text
A01 identity separation:
PASS

A02 capability != authority:
PASS

A03 actions / required inputs / outputs / evidence:
PASS

A04 role separation / protected assets:
PASS

A05 requested/actual runtime provenance:
PASS

A06 exact work authority cannot be inferred:
PASS

A07 bounded decomposition:
PASS at semantic boundary

A08 PROPOSED_WORK non-authority:
PASS at implemented semantic boundary

A09 BACKLOG_EXHAUSTED:
PASS

A10 fail-closed missing/stale/conflicting authority/evidence:
PASS

A11 downstream ownership preserved:
PASS
```

Prior implementation findings:

```text
RLY-S22-IMPL-EVAL-001 F001:
CLOSED

RLY-S22-IMPL-EVAL-001 F002:
CLOSED
```

Human root-authority bootstrap invariant:

```text
PASS
```

Semantic implementation disposition:

```text
TECHNICALLY READY
NO OPEN CODE FINDING
```

---

## 6. Reported deterministic validation

The implementation handoff reports:

```text
focused model tests:
13 passed

focused evaluation tests:
18 passed

focused architecture tests:
4 passed

full pytest:
974 passed

Ruff lint:
PASS

Pyright:
PASS

build:
PASS

changed-file format check:
PASS

diff check:
PASS
```

These results are consistent with the reviewed code and bounded diff.

They are implementation evidence reported by the executor. The independent evaluator did not recreate those local executions through GitHub Actions because the exact-head workflow stops earlier at the inherited repository-wide format condition described below.

---

## 7. Exact-head CI condition

Exact rework CI:

```text
Run:
39708475492

Head:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Workflow:
CI

Conclusion:
FAILURE

Failed step:
Ruff format

Ruff lint:
SKIPPED

Pyright:
SKIPPED

Tests:
SKIPPED

Build:
SKIPPED
```

The evaluator reconfirmed this is inherited from the authorized implementation baseline:

```text
baseline:
4cde30ef8b307e0483bcd94fe15a723b8003fbf2

baseline CI runs:
39704046658 — FAILURE at Ruff format
39702495026 — FAILURE at Ruff format
```

The reported offending immutable historical document remains byte-identical by Git blob:

```text
docs/reviews/SLICE_1_10_DOGFOOD_B4_REV2_IMPLEMENTATION_EVALUATION_001.md

baseline blob:
2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8

rework-candidate blob:
2bddc7ede8dc23f1fa11d6494f3d3f25f7fda0b8
```

Therefore:

```text
candidate-introduced CI regression:
NO

Role Contracts changed-file format:
reported PASS

repository-wide exact-head CI:
RED

cause:
PRE-EXISTING / OUTSIDE AUTHORIZED IMPLEMENTATION SCOPE
```

---

## 8. Why the overall outcome is ESCALATE rather than ACCEPT

`RLY-S22-IMPL-AUTH-001` explicitly states:

```text
and GitHub Actions CI on the exact candidate SHA if the branch workflow runs.
```

The workflow ran and is not green.

The accepted cross-cutting quality policy also makes declared quality checks part of the engineering contract and requires the evaluator to assess failed declared checks.

The evaluator has established that the failure is not caused by the Slice 2.2 candidate and cannot be corrected within the authorized six-file implementation surface.

That creates a governance conflict:

```text
candidate code conforms
AND
candidate did not introduce CI failure
AND
exact-head required CI is still red
AND
implementer lacks authority to repair/alter the failing historical artifact or quality contract
```

The independent evaluator has no Human authority to waive that explicit quality requirement.

Therefore:

```text
REWORK
```

would be incorrect because there is no remaining authorized implementation defect to rework.

```text
ACCEPT
```

would silently waive an explicit Human implementation condition.

The correct outcome is:

```text
ESCALATE
```

for a separate Human decision.

---

## 9. Required Human decision

The implementation is eligible for one of the following separately explicit paths:

### Path A — bounded quality-gate exception for this exact candidate

Human Authority may explicitly accept the inherited CI failure for:

`4400bd1da0db04e41077c3a6ed1c16d258104ba5`

based on the established facts that:

- the failing file predates the implementation baseline;
- its blob is unchanged;
- the candidate touches only authorized Role Contract files;
- changed-file formatting is reported green;
- semantic implementation review has no open finding;
- local lint/type/test/build evidence is reported green.

Such an exception must be durable and exact-candidate-bound. It must not become a general waiver of repository quality policy.

### Path B — separately authorize correction of the repository-wide CI baseline

If policy/document-governance permits a non-history-rewriting correction to the quality baseline/tooling, issue separate authority for that work.

This Slice 2.2 implementation authority does not permit it.

After a valid correction, rerun exact-head-equivalent CI/evidence as required by the new authority.

The evaluator does not choose between these paths.

---

## 10. Independent disposition

```text
RLY-S22-IMPL-EVAL-002 — ESCALATE

Exact rework candidate:
4400bd1da0db04e41077c3a6ed1c16d258104ba5

Code findings:
NONE OPEN

Prior F001:
CLOSED

Prior F002:
CLOSED

A01-A11:
ALL PASS

Candidate scope:
PASS

Candidate ancestry:
PASS

Candidate-introduced CI regression:
NO

Exact-head CI:
RED / inherited baseline condition

Semantic implementation:
TECHNICALLY READY

Independent implementation ACCEPT:
NOT GRANTED because exact-head required CI is not green

Human decision required:
EXACT-CANDIDATE QUALITY-GATE EXCEPTION
or
SEPARATELY AUTHORIZED BASELINE QUALITY REPAIR

Human technical acceptance:
PENDING / NOT YET ELIGIBLE UNDER CURRENT UNAMENDED QUALITY CONTRACT

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

**ESCALATE identifies a governance/quality-contract conflict, not a remaining Role Contracts code defect.**
