# Slice 2.2 — Role Contracts — Design Revision 2 Amendment

**Document class:** Lockable design amendment  
**Status:** REWORK COMPLETE — READY FOR INDEPENDENT RE-REVIEW  
**Date:** 2026-10-21  
**Project:** Relay  
**Slice:** 2.2 — Role Contracts  
**Document revision:** 2 Amendment  
**Design authority:** `RLY-S22-DESIGN-AUTH-001 — AUTHORIZED`  
**Revises:** Design Revision 1 at `63895f87e8f47a0e22a192e6cdbd002e6d51e45d`  
**Responds to:** `RLY-S22-DESIGN-EVAL-001 — REWORK`  
**Evaluation commit:** `ee2d03b6c4cab767381dae2fc9576ade2ef2ec02`  
**Implementation authorization:** NOT GRANTED

Revision 2 is normative over Revision 1 where they differ. All Revision 1 decisions not changed here remain in force.

---

## 1. Rework disposition

```text
F001 required input/output contract semantics      RESOLVED
F002 applicable/accepted RoleContract binding      RESOLVED
F003 role key/revision/digest conflict semantics   RESOLVED

IR clarification: complete action classification  ADOPTED
```

The rework preserves Revision 1's architecture:

- no new authority system;
- no role-contract database;
- no generic IAM/RBAC platform;
- no Work Packet implementation;
- no workspace enforcement;
- no runtime/provider execution;
- no operational database or lifecycle mutation.

---

## 2. F001 resolution — Role Contracts explicitly own required input/output semantics

Revision 1's `RoleContract` is amended to include exact semantic requirements for the inputs a role must receive and the outputs it must produce.

The combined conceptual object becomes:

```python
RoleContract(
    schema_version: int,
    role_key: str,
    revision: int,
    role_class: RoleClass,
    allowed_actor_kinds: tuple[ActorKind, ...],
    allowed_actions: tuple[RoleAction, ...],
    prohibited_actions: tuple[RoleAction, ...],
    required_inputs: tuple[RoleInputRequirement, ...],
    required_outputs: tuple[RoleOutputRequirement, ...],
    verification_asset_permissions: tuple[VerificationAssetPermission, ...],
    required_runtime_capabilities: tuple[RuntimeCapability, ...],
    required_assurance_properties: tuple[str, ...],
)
```

`required_inputs` and `required_outputs` are normative, digest-bound Role Contract fields.

They define **semantic contract obligations**, not the full transport/payload schema.

Slice 2.3 owns how exact values/references satisfying those obligations are carried in a Work Packet or ContextManifest. Slice 2.2 owns what the role requires.

---

## 3. S2.2-D19 — Minimum RoleInputRequirement vocabulary

The initial stable semantic input-requirement vocabulary is:

```text
ACTOR_IDENTITY_BINDING
APPLICABLE_ROLE_CONTRACT_BINDING
GOVERNANCE_PROFILE_BINDING
AUTHORIZED_WORK_BASIS
SOURCE_BASELINE
ACCEPTED_DESIGN_BASIS
EVALUATION_SUBJECT
EVIDENCE_BASIS
DECISION_BASIS
PROMOTION_BASIS
RUNTIME_EXECUTION_BASIS
```

These values are deliberately semantic and provider/workflow neutral.

Meaning:

| Input requirement | Required semantic basis |
| --- | --- |
| `ACTOR_IDENTITY_BINDING` | Exact actor identity and policy-required independent binding evidence. |
| `APPLICABLE_ROLE_CONTRACT_BINDING` | Exact RoleContractRef plus the valid applicability basis defined by this amendment. |
| `GOVERNANCE_PROFILE_BINDING` | Exact applicable GovernanceProfile/policy binding where policy requires one. |
| `AUTHORIZED_WORK_BASIS` | Exact governed work identity plus current authority required for the requested action. |
| `SOURCE_BASELINE` | Exact source Baseline/repository state required for the governed action. |
| `ACCEPTED_DESIGN_BASIS` | Exact accepted design reference when implementation/execution policy requires one. |
| `EVALUATION_SUBJECT` | Exact result/change/subject that an evaluator is asked to judge. |
| `EVIDENCE_BASIS` | Exact evidence references required by the applicable evaluation/decision policy. |
| `DECISION_BASIS` | Exact current Decision Basis required for a Human authority/acceptance decision. |
| `PROMOTION_BASIS` | Exact accepted subject, required acceptance/evaluation, current canonical parent/policy, and promotion authority inputs required for mechanical promotion. |
| `RUNTIME_EXECUTION_BASIS` | Exact Slice 2.1 RuntimeExecutionRequest/basis when the role action is runtime-backed. |

The vocabulary does not freeze Slice 2.3's packet shape and does not duplicate the underlying domain objects. It names which semantic contract must be satisfied.

A Role Contract includes only the requirements applicable to that role contract.

---

## 4. S2.2-D20 — Minimum RoleOutputRequirement vocabulary

The initial stable semantic output-requirement vocabulary is:

```text
ENGINEERING_RESULT
EXECUTION_EVIDENCE
EVALUATION_JUDGMENT
HUMAN_DECISION
PROMOTION_EVIDENCE
WORK_DISPOSITION
```

Meaning:

| Output requirement | Required semantic output |
| --- | --- |
| `ENGINEERING_RESULT` | Exact resulting engineering subject/result reference and required change/evidence facts; runtime success alone is insufficient. |
| `EXECUTION_EVIDENCE` | Evidence/provenance required by the applicable policy for the role's executed action. |
| `EVALUATION_JUDGMENT` | Exact-subject evaluation outcome/findings under an exact policy basis. |
| `HUMAN_DECISION` | Explicit Human authority/acceptance/choice record for the exact subject and decision type. |
| `PROMOTION_EVIDENCE` | Evidence of the already-authorized exact mechanical promotion and resulting canonical state. |
| `WORK_DISPOSITION` | Bounded disposition of the current authorized assignment, including successor available, `BACKLOG_EXHAUSTED`, or escalation-required semantics where applicable. |

`PROPOSED_WORK` observations are permitted outputs of `PROPOSE_FUTURE_WORK`, but they are not globally required outputs of an executor role. If an exact Role Contract requires such an observation, it is carried as part of `EXECUTION_EVIDENCE` or the later packet/result contract without acquiring authority.

---

## 5. S2.2-D21 — Input/output conformance is deterministic and fail-closed

Role Contract conformance gains an independent requirement result:

```text
SATISFIED
UNSATISFIED
INDETERMINATE
```

Conceptually:

```python
evaluate_required_inputs(
    contract: RoleContract,
    supplied_facts: RoleInputFacts,
) -> RoleRequirementEvaluation

evaluate_required_outputs(
    contract: RoleContract,
    produced_facts: RoleOutputFacts,
) -> RoleRequirementEvaluation
```

This does not require a universal `RoleInputFacts` or `RoleOutputFacts` persisted schema in Slice 2.2. The future packet/orchestration layer may adapt exact typed domain references into the pure evaluator.

Rules:

1. every requirement named in the Role Contract must be accounted for;
2. exact current fact present and attributable -> requirement may be `SATISFIED`;
3. positively incompatible/wrong subject/wrong binding -> `UNSATISFIED`;
4. missing, stale, conflicting, unverifiable, or applicability-unknown required fact -> `INDETERMINATE`;
5. neither `UNSATISFIED` nor `INDETERMINATE` permits the governed action/result to advance;
6. `NOT_APPLICABLE` is valid only when the applicable exact policy deterministically establishes non-applicability; callers may not omit a requirement and label it non-applicable themselves.

The role layer must report which requirement keys failed or remain indeterminate.

This resolves B3 A03 without importing Slice 2.3's Work Packet.

---

## 6. S2.2-D22 — Required input/output references are minimum requirements, not an allowlist of all fields

`required_inputs` and `required_outputs` express minimum semantic obligations.

They do not prohibit a Work Packet/result from carrying additional fields that are:

- permitted by the downstream schema;
- inside current authority;
- non-conflicting with the exact Role Contract and GovernanceProfile.

A caller must not infer authority from an extra field merely because it is present.

```text
required semantic input present != broader authority
extra context present != authority
required output produced != Human acceptance
```

---

## 7. F002 resolution — ApplicableRoleContractBinding

A syntactically valid or correctly hashed RoleContract is not applicable merely because a caller possesses it.

Before a governed action, Relay must have an exact **ApplicableRoleContractBinding**.

Conceptually:

```python
ApplicableRoleContractBinding(
    subject: AssuranceSubjectRef,
    role_contract_ref: RoleContractRef,
    policy_basis: PolicyBasis,
    governance_profile_ref: ExactPolicyArtifactRef | None,
    authority_basis_refs: tuple[str, ...],
)
```

This is a conceptual policy/authority binding, not a new authorization class or persistence table.

The exact serialized types for `AssuranceSubjectRef`, `PolicyBasis`, and profile/authority references remain owned by the Governance Assurance / Work-Packet design boundaries. Slice 2.2 freezes only the semantic predicate below.

---

## 8. S2.2-D23 — Applicability predicate

A Role Contract is `APPLICABLE` only when all applicable conditions are established:

```text
exact RoleContractRef content identity validates
AND exact governed subject is identified
AND exact current PolicyBasis is established
AND required GovernanceProfile binding is exact/current
AND that policy/profile or explicit current Human Authority selects the exact RoleContractRef
AND required authority basis is current for the subject/action
AND no conflicting/superseding role-contract selection exists
```

Applicability result:

```text
APPLICABLE
NOT_APPLICABLE
INDETERMINATE
```

Meanings:

- `APPLICABLE`: exact current policy/authority basis selects the exact contract for the exact governed subject/action;
- `NOT_APPLICABLE`: exact current policy positively establishes another contract/role basis or establishes that this role contract does not apply;
- `INDETERMINATE`: policy/profile/authority/currentness/supersession/identity cannot be established uniquely.

Only `APPLICABLE` may proceed to `evaluate_role_action()`.

A correctly hashed contract with unresolved applicability must not return an executable `PERMITTED_BY_ROLE` result.

---

## 9. S2.2-D24 — Who may select the applicable Role Contract

Role Contract selection is a **Control/Governance-plane fact**.

It may be established only by:

1. exact Relay policy/GovernanceProfile semantics that already have authority to select the role requirement for the governed subject; or
2. an explicit Human Authority decision that validly selects/overrides the exact RoleContractRef for the exact subject/action under the governing policy.

It may **not** be established by:

- the executor;
- the evaluator merely by evaluating;
- the runtime;
- the provider/model;
- prompt text;
- branch name;
- workspace access;
- a RoleContract's own fields;
- "latest role contract" discovery;
- document presence.

An executor/model/runtime may report that a Role Contract was supplied. It cannot establish its applicability.

This directly reuses the Governance Assurance rule:

```text
policy artifact/reference != authority by serialization
role name != authority
execution cannot manufacture authority
```

---

## 10. S2.2-D25 — Applicability must be established before the governed action

The ApplicableRoleContractBinding is prospective.

For an execution/evaluation/promotion action:

```text
applicable policy + exact subject
        ↓
exact RoleContractRef selected/bound
        ↓
role applicability evaluated
        ↓
role/action/input requirements evaluated
        ↓
separate work/action authority evaluated
        ↓
governed action may be admitted
```

A later Role Contract selection cannot retroactively validate an action performed under missing, stale, conflicting, or wrong role policy.

```text
execute first -> select permissive role later -> claim conformance
    = invalid
```

Historical actions remain judged under the exact role/policy basis applicable when they occurred.

---

## 11. S2.2-D26 — Slice 2.3 transports, but does not manufacture, the role binding

Future Slice 2.3 must carry exact references sufficient to reconstruct the already-established binding:

```text
RoleContractRef
exact governed subject/work ref
PolicyBasis ref/version/digest
GovernanceProfile ref/digest where applicable
authority-basis refs where required
```

The Work Packet builder must fail closed if the applicable binding cannot be established before packet finalization.

It may not:

- search for the "most recent" Role Contract;
- select a contract by role name alone;
- downgrade to a permissive contract;
- infer applicability from an executor's capabilities;
- synthesize missing authority.

Slice 2.3 therefore transports an accepted/current binding; it does not create role-policy authority.

---

## 12. F003 resolution — role key/revision/digest identity rule

Revision 1's RoleContract identity is retained:

```text
role_key
revision
content_digest
```

The semantic relationship is now frozen.

Within one exact applicable `PolicyBasis`:

```text
(role_key, revision) -> exactly one content_digest
```

Therefore:

```text
same PolicyBasis
+ same role_key
+ same revision
+ different content_digest
    ->
ROLE_CONTRACT_IDENTITY_CONFLICT
INDETERMINATE / FAIL CLOSED
```

A successor contract under the same `role_key` must increment `revision`.

A different exact PolicyBasis may intentionally select a different contract lineage or different content for the same human-readable/stable role key, but the policy basis must remain explicit in the applicability binding. No cross-policy "latest" resolution is permitted.

The `content_digest` remains the exact byte/content identity.

The `revision` remains the semantic version sequence inside the role-key lineage selected by one exact policy basis.

---

## 13. S2.2-D27 — No latest/best-match Role Contract resolution

Consumers must receive an exact `RoleContractRef`.

Forbidden resolution behavior:

```text
role_key -> max(revision)
role_key -> newest timestamp
role_class -> arbitrary matching contract
missing digest -> look up latest
digest mismatch -> choose closest
```

There is no "best match".

If the exact selected RoleContractRef is unavailable or conflicts with another current selection:

```text
ROLE_CONTRACT_NOT_RESOLVED
or
ROLE_CONTRACT_IDENTITY_CONFLICT
    ->
INDETERMINATE / STOP
```

This rule applies even if another available contract would be more permissive or technically executable.

---

## 14. IR clarification adopted — complete action coverage per schema version

Revision 1's `allowed_actions` and `prohibited_actions` remain disjoint.

Revision 2 adds:

```text
for every RoleAction defined by the RoleContract schema version:
allowed_actions U prohibited_actions
    == complete RoleAction set for that schema version
```

Therefore a valid v1 Role Contract explicitly classifies every v1 action.

An action introduced by a future Role Contract schema version cannot be silently interpreted by an older contract.

If an older contract is evaluated against an action it does not know:

```text
ROLE_ACTION_UNKNOWN_TO_CONTRACT_SCHEMA
    ->
INDETERMINATE / FAIL CLOSED
```

Changing the normative RoleAction vocabulary requires a Role Contract schema-version change when compatibility would otherwise be ambiguous.

This preserves forward fail-closed behavior while making each accepted contract complete for its own action vocabulary.

---

## 15. S2.2-D28 — Revised evaluation composition

Revision 1 D23 is replaced by the following composition:

```text
exact RoleContract bytes/digest validate
AND exact ApplicableRoleContractBinding = APPLICABLE
AND actor identity/binding is sufficient
AND requested action is known to contract schema
AND requested action = PERMITTED_BY_ROLE
AND required role inputs = SATISFIED
AND required separation holds
AND required protected-asset permission/authority holds
AND required assurance/provenance is sufficient
AND separate exact work/action authority independently passes
AND future Work Packet is exact/current
AND future workspace policy can enforce required constraints
        ->
eligible for governed action admission
```

For completion/result progression:

```text
required role outputs = SATISFIED
AND applicable result/evaluation/acceptance/promotion predicates pass
        ->
downstream governance may consider its own transition
```

No Role Contract result directly mutates lifecycle or grants acceptance/promotion.

---

## 16. S2.2-D29 — Revised refusal/escalation vocabulary

Revision 1 D17 remains in force and adds these mandatory semantic reasons:

```text
ROLE_CONTRACT_NOT_APPLICABLE
ROLE_CONTRACT_APPLICABILITY_UNKNOWN
ROLE_CONTRACT_IDENTITY_CONFLICT
ROLE_ACTION_UNKNOWN_TO_CONTRACT_SCHEMA
REQUIRED_ROLE_INPUT_MISSING
REQUIRED_ROLE_INPUT_INVALID
REQUIRED_ROLE_INPUT_INDETERMINATE
REQUIRED_ROLE_OUTPUT_MISSING
REQUIRED_ROLE_OUTPUT_INVALID
REQUIRED_ROLE_OUTPUT_INDETERMINATE
```

Known prohibited/incompatible fact -> deny/fail.

Unknown/missing/stale/conflicting applicability or required fact -> indeterminate/escalate/stop.

No refusal code creates authority.

---

## 17. Role-class input/output examples

These examples demonstrate semantics; they are not global hard-coded profiles. Exact RoleContract instances and applicable GovernanceProfile/policy decide the final tuples.

### IMPLEMENTER example

Typical required inputs:

```text
ACTOR_IDENTITY_BINDING
APPLICABLE_ROLE_CONTRACT_BINDING
GOVERNANCE_PROFILE_BINDING
AUTHORIZED_WORK_BASIS
SOURCE_BASELINE
ACCEPTED_DESIGN_BASIS
RUNTIME_EXECUTION_BASIS   # when runtime-backed
```

Typical required outputs:

```text
ENGINEERING_RESULT
EXECUTION_EVIDENCE
WORK_DISPOSITION
```

### INDEPENDENT_EVALUATOR example

Typical required inputs:

```text
ACTOR_IDENTITY_BINDING
APPLICABLE_ROLE_CONTRACT_BINDING
GOVERNANCE_PROFILE_BINDING
EVALUATION_SUBJECT
EVIDENCE_BASIS
```

Typical required output:

```text
EVALUATION_JUDGMENT
```

### HUMAN_AUTHORITY example

Typical required inputs:

```text
ACTOR_IDENTITY_BINDING
APPLICABLE_ROLE_CONTRACT_BINDING
DECISION_BASIS
```

Typical required output:

```text
HUMAN_DECISION
```

### PROMOTION_EXECUTOR example

Typical required inputs:

```text
ACTOR_IDENTITY_BINDING
APPLICABLE_ROLE_CONTRACT_BINDING
PROMOTION_BASIS
```

Typical required output:

```text
PROMOTION_EVIDENCE
```

These examples do not replace exact policy or authority.

---

## 18. Revised deterministic test requirements

Revision 1 §26 remains required and adds:

### F001 input/output contract tests

```text
required input tuple is digest-bound
required output tuple is digest-bound
duplicate input/output requirement rejected
missing required input -> INDETERMINATE/UNSATISFIED as exact case dictates
wrong-subject required input -> UNSATISFIED
stale/conflicting input -> INDETERMINATE
missing required output blocks downstream result progression
NOT_APPLICABLE accepted only when exact policy establishes it
Slice 2.3 transport cannot silently omit a RoleContract-required input
```

### F002 applicability tests

```text
valid digest + no policy/authority selection -> INDETERMINATE
executor-selected permissive contract -> rejected/not applicable
exact policy-selected contract -> APPLICABLE
exact Human-authorized selection where policy permits -> APPLICABLE
stale/superseded selection -> INDETERMINATE or NOT_APPLICABLE per exact established state
conflicting current selections -> INDETERMINATE
later role selection does not retroactively validate prior action
```

### F003 identity tests

```text
same PolicyBasis + same role_key/revision + same digest -> same contract identity
same PolicyBasis + same role_key/revision + different digest -> ROLE_CONTRACT_IDENTITY_CONFLICT
same role_key successor contract requires revision increment
exact ref required; no latest/max-revision fallback
different PolicyBasis remains explicitly distinct
```

### Action completeness tests

```text
all schema-v1 actions classified exactly once
allowed/prohibited overlap rejected
missing known v1 action classification rejected as invalid contract
future unknown action against old schema -> INDETERMINATE
```

---

## 19. Updated implementation boundary

The minimum implementation architecture remains:

```text
src/relay_engine/role_contracts/
  __init__.py
  models.py
  evaluation.py
```

Revision 2 adds only pure-domain/evaluation concepts needed for:

- `RoleInputRequirement`;
- `RoleOutputRequirement`;
- required-input/output conformance;
- `ApplicableRoleContractBinding` semantic evaluation;
- role identity-conflict detection;
- complete action coverage validation.

No database migration/table is required.

No role catalog is required.

No policy/profile engine is authorized.

No Work Packet implementation is authorized.

No operational-state mutation is authorized.

If implementation cannot resolve exact applicability without introducing a new persistence/authority subsystem, it must stop and escalate rather than inventing one.

---

## 20. B3 A01–A11 traceability after rework

```text
A01 PASS — Revision 1 D01/D05/D06/D11
A02 PASS — Revision 1 D04/D11/D12
A03 PASS — Revision 1 D03/D04/D10/D17 plus Revision 2 D19–D22/D29
A04 PASS — Revision 1 D07–D09/D22 plus Revision 2 D23–D26
A05 PASS — Revision 1 D11
A06 PASS — Revision 1 D12/D23 plus Revision 2 D23–D28
A07 PASS — Revision 1 D13
A08 PASS — Revision 1 D14
A09 PASS — Revision 1 D15/D16
A10 PASS — Revision 1 D17 plus Revision 2 D21/D23/D29
A11 PASS — Revision 1 D18/D25 plus unchanged implementation boundary
```

This is a design claim for independent re-review, not self-acceptance.

---

## 21. Review checklist additions

Independent re-review must additionally verify:

- Role Contract explicitly owns required semantic inputs and outputs;
- those requirements are normative digest-bound fields;
- Slice 2.3 transports, rather than invents, role requirements;
- valid digest alone cannot make a Role Contract applicable;
- exact policy/profile/Human-authority basis selects the applicable RoleContractRef before action;
- executor/runtime/model cannot self-select or downgrade the contract;
- applicability has APPLICABLE / NOT_APPLICABLE / INDETERMINATE semantics;
- within one PolicyBasis, one role_key/revision maps to exactly one digest;
- no latest/best-match fallback exists;
- all actions known to the contract schema are explicitly classified;
- unknown future actions fail closed;
- no new role-policy persistence or authority system was introduced.

---

## 22. Combined-design disposition

```text
RLY-S22-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
63895f87e8f47a0e22a192e6cdbd002e6d51e45d

Independent evaluation:
RLY-S22-DESIGN-EVAL-001 — REWORK

Revision 2 Amendment:
REWORK COMPLETE
READY FOR INDEPENDENT RE-REVIEW

F001:
RESOLVED BY DESIGN

F002:
RESOLVED BY DESIGN

F003:
RESOLVED BY DESIGN

Slice 2.2 implementation:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

**Rework complete != design accepted. Design accepted != implementation authorized.**
