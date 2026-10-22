# Slice 2.2 — Role Contracts — Design Revision 1

**Document class:** Lockable design record  
**Status:** DESIGN CANDIDATE — READY FOR INDEPENDENT REVIEW  
**Date:** 2026-10-21  
**Project:** Relay  
**Slice:** 2.2 — Role Contracts  
**Document revision:** 1  
**Opening authority:** `RLY-S22-OPEN-001 — OPEN`  
**Design authority:** `RLY-S22-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact design subject baseline:** `00214852ba7d603ce06121707f3e79606345b07f`  
**Design-authority commit:** `e7d3ab657f72f551fd046daa668bc646c6e2b389`  
**Design branch:** `design/2.2-role-contracts`  
**Implementation authorization:** NOT GRANTED

---

## 1. Objective

Define the minimum Relay-owned Role Contract semantics required to say what an engineering actor **may and must do** inside an already-established Relay authority boundary.

Slice 2.2 does not create a second authority system. It defines a deterministic role-policy contract that can be bound to an exact actor and exact governed work by later Work-Packet/execution layers.

The controlling separation is:

```text
role != actor identity != runtime identity != model identity
identity != capability != authority

role permits/forbids classes of action
authority permits exact governed work
runtime/workspace capability makes an action technically possible

all required conditions must hold
none may manufacture another
```

The design must also make executor authority exhaustion explicit:

```text
current authorized work
        ↓
bounded internal decomposition only
        ↓
discovered future work => PROPOSED_WORK (non-authoritative)
        ↓
exact authorized successor established?
        ├─ yes -> current execution stops; later governed handoff may use successor
        ├─ no  -> BACKLOG_EXHAUSTED / successful STOP
        └─ unknown/conflicting -> ESCALATE / fail closed
```

---

## 2. Frozen design basis

This design consumes, and does not redefine:

1. the accepted Phase 1 governance substrate and immutable `ActorRef`;
2. the Governance Assurance Reference Model, including GovernanceProfile semantics and Protected Verification Assets;
3. Human Decision Support / Human acceptance separation;
4. canonical promotion separation;
5. the Human-accepted Slice 2.1 Agent Runtime Contract;
6. B3's exact Slice 2.2 definition and A01–A11 acceptance contract;
7. B4's Human-accepted demonstration that current Relay state must be recoverable from durable state and that `NOT_DETERMINABLE` must remain distinct from established absence.

B3 fixes the current Slice identity:

`slc_01a15754-1123-7535-9ded-6a564518e347 — Slice 2.2 — Role Contracts`

and fixes these authority-exhaustion semantics:

- authorized work is an exact work reference with current explicit authority;
- internal decomposition stays inside that work;
- `PROPOSED_WORK` is non-authoritative;
- successor work requires separate authorized establishment;
- `BACKLOG_EXHAUSTED` is successful stop, not lifecycle state or permission to invent work.

---

## 3. Non-goals

Slice 2.2 does **not** design or implement:

- Work-Packet construction, planning normalization, or ContextManifest — Slice 2.3;
- filesystem/tool/network/credential enforcement — Slice 2.4;
- AgentRuntime transport/session/event mechanics — Slice 2.1;
- autonomous orchestration — Phase 3;
- a general IAM/RBAC platform;
- a GovernanceProfile policy engine or profile taxonomy;
- lifecycle redesign;
- a new backlog database;
- Human acceptance automation;
- promotion policy/execution;
- operational DB mutation under this design authority.

---

## 4. S2.2-D01 — Role Contract is immutable, content-addressed policy

The stable domain object is conceptually:

```python
RoleContract(
    schema_version: int,
    role_key: str,
    revision: int,
    role_class: RoleClass,
    allowed_actor_kinds: tuple[ActorKind, ...],
    allowed_actions: tuple[RoleAction, ...],
    prohibited_actions: tuple[RoleAction, ...],
    verification_asset_permissions: tuple[VerificationAssetPermission, ...],
    required_runtime_capabilities: tuple[RuntimeCapability, ...],
    required_assurance_properties: tuple[str, ...],
)
```

Its exact identity is:

```python
RoleContractRef(
    role_key: str,
    revision: int,
    content_digest: ContentDigest,
)
```

Rules:

- `role_key` is a bounded stable key, not a display label;
- `revision >= 1`;
- the contract serializes canonically and is SHA-256 content-addressed;
- ordered enum/property tuples are unique and canonical-order validated;
- `allowed_actions` and `prohibited_actions` are disjoint;
- omitted actions are not silently allowed;
- a digest proves byte/content identity, not authority or acceptance.

No new `role_` UUID identifier is required. Stable key + revision + digest is sufficient and avoids a new identity/persistence subsystem.

### Persistence decision

Slice 2.2 introduces **no role-contract database table**.

Role Contracts are immutable domain values. A later Work Packet binds an exact `RoleContractRef`; how accepted role-contract material is transported/materialized belongs to Slice 2.3. If a future requirement proves that Relay needs an operational role catalog, that is a separate design decision rather than an implicit Slice 2.2 schema expansion.

---

## 5. S2.2-D02 — Initial role classes are intentionally small

The initial stable classes are:

```text
IMPLEMENTER
INDEPENDENT_EVALUATOR
HUMAN_AUTHORITY
PROMOTION_EXECUTOR
```

These are governance classes, not product personas and not model/provider identities.

They cover the separation required by the accepted roadmap:

```text
implementation actor
    !=
independent evaluator
    !=
Human Authority
    !=
promotion executor
```

The design does not freeze `architect`, `planner`, `researcher`, `reviewer`, or vendor-specific agent types into the initial product schema. Such behaviors can be represented by exact allowed actions under an applicable role contract until a later accepted requirement proves another stable class is needed.

---

## 6. S2.2-D03 — Minimal RoleAction vocabulary

The initial semantic action vocabulary is:

```text
CONTEXT_READ
IMPLEMENTATION_MUTATE
IMPLEMENTATION_TEST_MUTATE
VERIFICATION_EXECUTE
EVALUATE_RESULT
AUTHORIZE_WORK
ACCEPT_RESULT
PROMOTE_RESULT
DECOMPOSE_AUTHORIZED_WORK
PROPOSE_FUTURE_WORK
```

Protected-verification operations use a separate bounded vocabulary because they apply to policy-designated assets rather than all project actions:

```text
READ
CREATE
PROPOSE_MUTATION
MODIFY
APPROVE_MUTATION
EXECUTE
EVALUATE
```

The split is deliberate:

- `RoleAction` answers what category of governed action the role may perform;
- `VerificationAssetPermission` answers what the role may do to an asset already classified as a Protected Verification Asset by applicable policy/profile.

No path glob, filesystem rule, tool permission, network rule, or credential rule is stored here. Those are Slice 2.4 enforcement concerns.

---

## 7. S2.2-D04 — Role eligibility is not authorization

Role evaluation returns only:

```text
PERMITTED_BY_ROLE
PROHIBITED_BY_ROLE
INDETERMINATE
```

Conceptually:

```python
evaluate_role_action(contract, actor, action) -> RoleEligibility
```

Rules:

1. actor kind not allowed by the contract -> `PROHIBITED_BY_ROLE`;
2. action explicitly prohibited -> `PROHIBITED_BY_ROLE`;
3. action explicitly allowed -> `PERMITTED_BY_ROLE`;
4. action absent from both sets -> `INDETERMINATE`;
5. malformed/conflicting contract -> invalid contract / fail closed.

Critical invariant:

```text
PERMITTED_BY_ROLE != AUTHORIZED
```

A caller may proceed only after a **separate** authority mechanism establishes that the exact action is authorized for the exact current work/baseline/subject.

Role Contract code MUST NOT expose operations such as:

```text
authorize_work()
accept_result()
promote_baseline()
create_successor()
advance_lifecycle()
```

It may determine whether a role is eligible to request/perform one of those semantic action classes after separate authority exists.

---

## 8. S2.2-D05 — Actor identity is reused, never inferred

Relay already owns:

```python
ActorRef(
    id: ActorId,
    kind: HUMAN | SYSTEM | AGENT,
    display_name: str | None,
)
```

Slice 2.2 reuses it.

A role binding never derives actor identity from:

- role name;
- model name;
- provider;
- runtime/session ID;
- prompt text;
- HTTP header;
- workspace user;
- Git author string.

Where policy requires `RELAY_ACTOR_IDENTITY_BOUND`, the exact ActorRef and its applicable binding evidence must be present.

Mandatory class rule:

```text
HUMAN_AUTHORITY -> ActorKind.HUMAN only
```

Other classes may be bound to HUMAN, SYSTEM, or AGENT only when their exact Role Contract and applicable GovernanceProfile allow it.

A model or runtime may participate in an actor's execution provenance, but it is never the actor authority by itself.

---

## 9. S2.2-D06 — Role binding is action-scoped, not permanent privilege

Conceptually, Relay evaluates a role for one exact governed action through:

```python
RoleActionBinding(
    role_contract_ref,
    actor,
    action,
    execution_id | None,
)
```

This is evidence/binding, not an ACL grant.

Rules:

- runtime-backed actions bind the applicable Relay `ExecutionId`;
- Human decisions need not fabricate an ExecutionId;
- one actor may hold more than one role only when each role binding is explicit and applicable policy permits the combination;
- one role binding does not imply another role;
- binding an actor to `INDEPENDENT_EVALUATOR` does not grant verification-asset mutation authority;
- binding an actor to `PROMOTION_EXECUTOR` does not grant promotion authority.

The exact work/authority reference is intentionally **not** embedded into RoleContract itself. Slice 2.3 must bind RoleContractRef + exact accepted work + current authority into the Work Packet.

---

## 10. S2.2-D07 — Separation rules are policy inputs with deterministic checks

Conceptually:

```python
RoleSeparationRequirement(
    left_role_class,
    right_role_class,
    distinct_actor: bool,
    distinct_execution: bool,
    distinct_runtime_session: bool,
)
```

The applicable GovernanceProfile/policy supplies the required separation rules.

Minimum Relay semantics:

### Implementer vs independent evaluator

When independent evaluation is required:

```text
implementer ActorRef != evaluator ActorRef
```

For runtime-backed work:

```text
implementer ExecutionId != evaluator ExecutionId
implementer runtime session != evaluator runtime session
```

This preserves the accepted Slice 2.1 rule.

### Human Authority

`HUMAN_AUTHORITY` must be a HUMAN actor and must produce the separate durable Human authority/acceptance decision required by the applicable gate.

No implementation/evaluation role implies Human Authority.

### Promotion executor

The promotion executor performs an already-authorized mechanical operation. It may not supply Human acceptance or decide promotion policy.

### Multi-role physical actors

A single underlying person/system may hold multiple role bindings only where policy permits it and every required role/capability is explicit.

Example:

```text
evaluator review != verification-asset mutation approval
```

The same physical actor may perform both only if it separately holds the explicit mutation-approval role/capability and applicable authority.

No global rule requires `designer != evaluator`; the existing Relay clarification remains in force unless an exact GovernanceProfile or later authority requires stronger separation.

---

## 11. S2.2-D08 — Protected Verification Assets use explicit operation permissions

Protected Verification Assets are policy/profile-classified assets. Role Contracts do not classify repository paths themselves.

For an already-classified protected asset, evaluate:

```text
asset operation
        +
RoleContract.verification_asset_permissions
        +
applicable GovernanceProfile requirement
        +
exact separate authority where mutation/approval is required
```

Rules:

- READ does not imply MODIFY;
- CREATE does not imply approval;
- PROPOSE_MUTATION does not mutate;
- MODIFY does not imply APPROVE_MUTATION;
- EVALUATE does not imply mutation authority;
- evaluator PASS/ACCEPT never manufactures mutation authority;
- verification execution does not imply authority to change the verification basis;
- an implementer may change ordinary implementation tests when policy allows, but may not weaken a profile-protected acceptance/evaluation asset merely because repository writes are technically possible;
- unknown required asset classification or mutation authority -> `INDETERMINATE` / fail closed.

Slice 2.4 later maps these semantic permissions to concrete filesystem/tool restrictions and records enforcement evidence.

---

## 12. S2.2-D09 — GovernanceProfile constrains Role Contracts; Role Contracts do not select profiles

The applicable GovernanceProfile may require:

- specific role classes;
- specific separation rules;
- actor-identity strength/binding;
- protected-verification treatment;
- evaluator independence;
- required assurance properties;
- execution provenance completeness;
- stronger evidence obligations.

Slice 2.2 does not implement profile selection or scoring.

Role conformance consumes an already-resolved profile reference/requirements from the governance/work-packet layer.

If a profile is required but is:

```text
missing
unknown
stale
conflicting
not attributable to the current work
```

then Role Contract conformance is not silently downgraded. The result is `INDETERMINATE` and requires escalation/current authority resolution.

```text
implementer cannot self-downgrade governance
runtime capability cannot self-downgrade governance
model output cannot self-downgrade governance
```

---

## 13. S2.2-D10 — Assurance obligations are references, not duplicated governance logic

`RoleContract.required_assurance_properties` contains stable references to assurance properties already defined by the Governance Assurance model.

Typical applicable properties include:

```text
RELAY_ACTOR_IDENTITY_BOUND
RELAY_IMPLEMENTER_EVALUATOR_SEPARATION
RELAY_INDEPENDENT_EVALUATION
RELAY_RUNTIME_IDENTITY_RECORDED
RELAY_EXECUTION_PROVENANCE_SUFFICIENT
RELAY_GOVERNANCE_PROFILE_BOUND
RELAY_VERIFICATION_ASSETS_PROTECTED
```

Role Contract implementation must not reimplement the entire assurance engine.

It answers:

- what evidence/property obligations this role requires;
- whether the necessary role facts are present and non-conflicting.

The existing/future assurance/evaluation layer answers whether the complete engineering subject satisfies the property under the applicable policy.

---

## 14. S2.2-D11 — Reuse Slice 2.1 runtime provenance

Role Contracts do not duplicate runtime/provider/model fields.

Runtime-backed execution reuses Slice 2.1:

- `RuntimeExecutionRequest`;
- `RuntimeExecutionBasis`;
- `RuntimeDescriptor`;
- `RuntimeCapability`;
- `RuntimeProvenance`;
- `ExecutionId`;
- runtime/session bindings.

The Role Contract may require exact `RuntimeCapability` values.

Requested-versus-actual provider/model identity is evaluated from `RuntimeProvenance`.

Rules:

- requested identity and actual identity remain distinct;
- mismatch is evidence, not automatically authorization failure;
- applicable profile determines whether exact actual identity is required;
- if required provenance is unavailable or incomplete, report insufficient/indeterminate provenance rather than fabricate an identity;
- runtime permission is defense in depth and may narrow behavior, but never creates Relay authority.

---

## 15. S2.2-D12 — Work authority is an external exact prerequisite

Role Contract semantics require the caller to supply an exact current work/authority basis.

Slice 2.3 must eventually bind at least:

```text
exact Project/Slice identity
exact Slice definition revision
exact accepted baseline/design references required by policy
exact current authority reference(s)
exact RoleContractRef
exact applicable GovernanceProfile reference
exact input/context references
```

Slice 2.2 does not freeze the Work-Packet schema.

The following are never sufficient authority:

```text
roadmap order
PROPOSED lifecycle phase
unblocked state
role eligibility
runtime capability
workspace write access
successful prior execution
model recommendation
internal decomposition
document presence
```

If exact current authority is missing, stale, conflicting, or invalid, execution must stop/escalate. The role layer must not guess scope.

---

## 16. S2.2-D13 — Internal decomposition is bounded child planning, not backlog mutation

An IMPLEMENTER may have `DECOMPOSE_AUTHORIZED_WORK` only when the current exact authority permits implementation/execution.

Internal decomposition:

- may create ephemeral/subordinate steps;
- may order or split the current authorized work;
- may choose an implementation sequence inside current scope;
- must remain within the exact authorized work objective/scope/acceptance contract;
- cannot alter acceptance criteria;
- cannot add authoritative dependencies;
- cannot widen repository/workspace authority;
- cannot create a successor Slice;
- cannot change the authoritative backlog.

Internal tasks do not receive independent authoritative work identity merely because an agent names them.

If decomposition reveals that required work is outside scope, the executor stops that path and emits a non-authoritative proposal/escalation.

---

## 17. S2.2-D14 — PROPOSED_WORK is content/evidence, never runnable authority

A discovered future item may be represented conceptually as:

```python
ProposedWorkObservation(
    source_slice_id,
    source_execution_id | None,
    summary,
    rationale,
    evidence_refs,
    proposal_digest,
)
```

The exact implementation may simplify this further.

Mandatory negative properties:

`PROPOSED_WORK` contains **no**:

- authorization;
- lifecycle phase;
- executable status;
- successor authority;
- implicit Slice creation;
- automatic priority;
- runtime/workspace permission.

It is non-authoritative evidence for later Human/governance consideration.

Promotion from a proposal into governed successor work requires a separate accepted definition and applicable Human/governance authority through existing/future project/Slice mechanisms.

```text
proposal != backlog item
proposal != Slice
proposal != authority
proposal != executable work
```

Slice 2.2 implementation does not require a proposal database table. Persistence/UX may be designed later when an actual consumer requires it.

---

## 18. S2.2-D15 — Successor resolution is tri-state

A future orchestration layer must resolve successor state using durable Relay governance, never model inference.

Conceptually:

```text
AUTHORIZED_SUCCESSOR_ESTABLISHED
NO_AUTHORIZED_SUCCESSOR
SUCCESSOR_NOT_DETERMINABLE
```

Rules:

### AUTHORIZED_SUCCESSOR_ESTABLISHED

An exact successor identity and applicable authority are established.

The current execution still stops. A new governed Work Packet/execution is required to act on the successor.

The current executor does not inherit authority into the next item.

### NO_AUTHORIZED_SUCCESSOR

Durable state positively establishes that no authorized successor exists.

Result:

```text
BACKLOG_EXHAUSTED
```

This is successful termination of the current executor assignment.

### SUCCESSOR_NOT_DETERMINABLE

Durable state is missing, stale, conflicting, or cannot establish whether an authorized successor exists.

Result:

```text
ESCALATION_REQUIRED / STOP
```

Do **not** convert this into `BACKLOG_EXHAUSTED`.

This distinction is mandatory. B4 demonstrated that an empty projected next-work list can coexist with `NOT_DETERMINABLE`; absence of evidence is not proof of authoritative backlog exhaustion.

---

## 19. S2.2-D16 — BACKLOG_EXHAUSTED is a successful work disposition, not lifecycle

The bounded semantic disposition is:

```text
AUTHORIZED_SUCCESSOR_AVAILABLE
BACKLOG_EXHAUSTED
ESCALATION_REQUIRED
```

It is not:

- a Slice lifecycle phase;
- a HandoverGate result;
- an evaluation outcome;
- Human acceptance;
- promotion;
- permission to invent work.

`BACKLOG_EXHAUSTED` means only:

> the current authorized assignment is complete and durable Relay governance positively establishes no authorized successor available to this executor.

A caller may record this in execution/result evidence, but must not mutate lifecycle merely because exhaustion was reported.

---

## 20. S2.2-D17 — Fail-closed refusal and escalation taxonomy

The design requires stable role-level reasons sufficient for deterministic tests and downstream explanation.

Minimum conceptual reasons:

```text
ROLE_ACTION_PROHIBITED
ROLE_ACTION_UNSPECIFIED
ACTOR_KIND_NOT_ALLOWED
ACTOR_IDENTITY_NOT_BOUND
ROLE_SEPARATION_VIOLATION
GOVERNANCE_PROFILE_REQUIRED
GOVERNANCE_PROFILE_CONFLICT
PROTECTED_ASSET_PERMISSION_REQUIRED
PROTECTED_ASSET_MUTATION_AUTHORITY_REQUIRED
REQUIRED_ASSURANCE_EVIDENCE_MISSING
EXECUTION_PROVENANCE_INSUFFICIENT
WORK_AUTHORITY_MISSING
WORK_AUTHORITY_STALE
WORK_AUTHORITY_CONFLICT
WORK_SCOPE_EXCEEDED
SUCCESSOR_NOT_DETERMINABLE
```

Known prohibition -> deny/stop.

Missing/unknown/conflicting prerequisite -> indeterminate/escalate/stop.

No category grants authority.

Exact naming may be refined during implementation if needed to align existing error vocabularies, but the semantic distinctions above are normative.

---

## 21. S2.2-D18 — Required input/output contract boundary

Slice 2.2 owns these stable concepts:

```text
RoleClass
RoleAction
VerificationAssetPermission
RoleContract
RoleContractRef
RoleActionBinding
RoleEligibility
RoleSeparationRequirement
role-level conformance/refusal reasons
PROPOSED_WORK semantics
authorized-successor tri-state semantics
BACKLOG_EXHAUSTED semantics
```

Slice 2.2 does **not** own a full execution input/output envelope.

### Slice 2.3 owns

- exact Work Packet;
- ContextManifest;
- planning normalization;
- authority/baseline/design/policy/role references inside the packet;
- accepted work reference transport;
- successor-work reference transport where applicable.

### Slice 2.4 owns

- filesystem/path enforcement;
- allowed/denied writes;
- tool restrictions;
- network access;
- credentials;
- resource limits;
- protected-asset concrete enforcement;
- workspace/environment evidence.

### Slice 2.1 owns

- runtime capability discovery;
- runtime/provider/model requested/actual provenance;
- sessions/events/cancel/inspection.

### Phase 3 owns

- orchestration of an authorized Work Packet through role + runtime + workspace enforcement;
- producing execution/result evidence;
- successor handoff behavior.

---

## 22. Role-class baseline responsibilities

The following matrix is a **semantic baseline**, not a substitute for exact RoleContract instances or applicable GovernanceProfile constraints.

| Role class | May typically do | Must not gain merely from role |
| --- | --- | --- |
| `IMPLEMENTER` | read context, mutate implementation, mutate ordinary implementation tests when policy permits, run verification, decompose authorized work, propose future work | authorize work, Human-accept, independently evaluate its own result where separation is required, promote, mutate protected verification basis without separate permission/authority |
| `INDEPENDENT_EVALUATOR` | read subject/evidence, execute allowed verification, evaluate result, report findings | implementation authority, Human acceptance, promotion authority, protected-asset mutation authority |
| `HUMAN_AUTHORITY` | issue exact Human decisions/authorities allowed by governance policy | automatic repository/runtime capability; technical execution is separate |
| `PROMOTION_EXECUTOR` | mechanically execute an already-authorized exact promotion when predicates pass | policy choice, Human acceptance, implementation authority, authority to relax predicates |

The exact allowed/prohibited sets are contract data; this matrix prevents semantic drift during implementation.

---

## 23. Deterministic conformance composition

A governed action is eligible to execute only when all applicable layers pass:

```text
exact RoleContract resolves
AND actor identity/binding is sufficient
AND role action = PERMITTED_BY_ROLE
AND required separation holds
AND required protected-asset permission holds
AND required assurance/provenance is sufficient
AND exact work authority independently passes
AND future Work Packet is exact/current
AND future workspace policy can enforce the required constraints
```

Any required unknown is fail-closed.

This is deliberately conjunction, not privilege inheritance.

```text
role eligibility
    AND authority
    AND context/work packet
    AND workspace enforcement
    AND runtime capability
        -> executable governed action

no single term implies another
```

---

## 24. Canonical serialization and digest

If implemented, `RoleContract` canonical identity should follow the same deterministic style already used by `RuntimeExecutionBasis`:

```text
UTF-8
JSON object
sort_keys = true
separators = (",", ":")
ensure_ascii = false
no floating-point policy values
one schema version
```

The SHA-256 is represented as Relay `ContentDigest`:

`sha256:<64 lowercase hex>`

Digest inputs include every normative RoleContract field.

Display labels/comments, if ever added, must either be explicitly normative and hashed or explicitly excluded by design; implementation must not silently mix the two.

---

## 25. Minimal implementation architecture

A later implementation authority should prefer one bounded package, conceptually:

```text
src/relay_engine/role_contracts/
  __init__.py
  models.py
  evaluation.py
```

Expected responsibilities:

### `models.py`

- RoleClass;
- RoleAction;
- VerificationAssetPermission;
- RoleContract / RoleContractRef;
- RoleActionBinding;
- RoleEligibility;
- RoleSeparationRequirement;
- bounded work-exhaustion/proposal semantic values where required.

### `evaluation.py`

Pure deterministic functions for:

- contract validation/canonical digest;
- role/action eligibility;
- actor-kind validation;
- separation evaluation;
- protected-verification permission evaluation;
- required-provenance/assurance-presence checks;
- successor tri-state -> bounded disposition mapping.

Initial implementation should require **no**:

- database migration;
- new operational table;
- runtime adapter modification;
- workspace enforcement;
- CLI;
- UI;
- network/provider calls.

A mechanical extraction/reuse of an existing stable-key helper is permissible only if needed and behavior-preserving.

---

## 26. Required implementation tests

A later implementation authority must require deterministic tests at least for:

### Identity / canonicality

- same RoleContract -> same digest;
- changed normative field -> changed digest;
- duplicate/noncanonical tuples rejected;
- allowed/prohibited action overlap rejected;
- role key/revision validation;
- no new role UUID identity required.

### Role vs authority

- allowed role action returns `PERMITTED_BY_ROLE`, never `AUTHORIZED`;
- prohibited action fails deterministically;
- unspecified action returns `INDETERMINATE`;
- role label/model/runtime name cannot substitute actor identity or authority.

### Actor / separation

- HUMAN_AUTHORITY rejects non-HUMAN actor;
- required implementer/evaluator actor separation enforced;
- required runtime-backed execution/session separation enforced;
- same physical actor with two capabilities is accepted only where policy explicitly permits both bindings.

### Protected assets

- READ does not imply MODIFY;
- MODIFY does not imply APPROVE_MUTATION;
- EVALUATE does not imply mutation authority;
- unknown required asset classification fails closed;
- implementer ordinary-test permission does not imply protected-asset mutation.

### Runtime provenance

- required RuntimeCapability missing -> fail/indeterminate before execution;
- requested vs actual identity retained separately;
- missing required actual identity is insufficient rather than fabricated.

### Work authority / decomposition

- decomposition may not alter current work scope/acceptance;
- proposal cannot be consumed as authority;
- proposal has no implicit Slice/lifecycle/executable status;
- executor cannot establish successor authority.

### Exhaustion

- exact authorized successor -> `AUTHORIZED_SUCCESSOR_AVAILABLE`, current execution still stops;
- positively established no successor -> `BACKLOG_EXHAUSTED`;
- successor not determinable -> `ESCALATION_REQUIRED`, never `BACKLOG_EXHAUSTED`;
- exhaustion never mutates lifecycle.

### Static architecture checks

- no DB migration/table added by initial role-contract implementation;
- no writable operational DB path in role evaluation;
- no AgentRuntime authority method;
- no automatic Human acceptance/promotion;
- no Slice 2.3/2.4/Phase 3 implementation smuggled into package.

---

## 27. Acceptance-criteria traceability

| B3 criterion | Slice 2.2 design disposition |
| --- | --- |
| A01 identities distinct | D01, D05, D06, D11 |
| A02 capability != authority | D04, D11, D12 |
| A03 actions/contracts/evidence explicit | D03, D04, D10, D17, D18 |
| A04 role separation/protected assets | D07, D08, D09, D22 |
| A05 requested/actual provenance | D11 |
| A06 exact work authority | D12, D23 |
| A07 bounded decomposition | D13 |
| A08 PROPOSED_WORK non-authority | D14 |
| A09 BACKLOG_EXHAUSTED | D15, D16 |
| A10 fail-closed escalation | D17 |
| A11 downstream boundaries preserved | D18, D25 |

All eleven frozen B3 acceptance criteria are covered without introducing a second lifecycle/backlog/workspace/runtime mechanism.

---

## 28. Resolved design questions

1. **What is a Role Contract?**  
   An immutable, content-addressed role-policy value describing role class, eligible actor kinds, allowed/prohibited semantic actions, protected-verification permissions, runtime capability requirements, and assurance obligations.

2. **How is it identified?**  
   Stable role key + revision + exact content digest; no new UUID domain is required.

3. **How are role/actor/runtime/model/authority/capability separated?**  
   RoleContract describes role policy; ActorRef identifies actor; Slice 2.1 owns runtime/model provenance; future Work Packet binds authority; capability never implies authority.

4. **What action vocabulary is necessary?**  
   The bounded D03 RoleAction vocabulary plus protected-verification operations.

5. **How are allow/prohibit decisions represented?**  
   Explicit disjoint tuples; unlisted action is `INDETERMINATE`.

6. **How does policy require separation?**  
   Through explicit RoleSeparationRequirement values resolved by the applicable GovernanceProfile.

7. **How is evaluator independence checked?**  
   Required distinct ActorRef and, for runtime-backed execution, distinct ExecutionId/session.

8. **How are protected verification assets represented?**  
   Asset classification is policy/profile-owned; RoleContract carries semantic operation permissions only.

9. **Who may mutate/approve/evaluate protected assets?**  
   Only an actor whose exact RoleContract, policy/profile, and separate mutation/approval authority permit that operation. Evaluation alone confers no mutation authority.

10. **How is runtime/provider/model provenance used?**  
    Reuse Slice 2.1 requested/actual provenance; applicable policy determines sufficiency; provenance is not authority.

11. **What conformance evidence is required?**  
    Exact contract ref, actor/binding, action, separation result, applicable profile/properties, protected-asset decision where relevant, runtime provenance where relevant, and separate exact work-authority evidence.

12. **What happens when authority is missing/ambiguous?**  
    Stop and escalate; never infer scope or permission.

13. **How is PROPOSED_WORK represented?**  
    As non-authoritative content/evidence with source provenance and digest, with no executable/lifecycle/authority semantics.

14. **How does authorized-work exhaustion work?**  
    Governance supplies tri-state successor resolution; established none -> `BACKLOG_EXHAUSTED`; indeterminate -> escalation; established successor still requires new governed handoff.

15. **What belongs to Slice 2.3?**  
    Work Packet, ContextManifest, exact work/authority/role/profile reference transport, planning normalization.

16. **What belongs to Slice 2.4?**  
    Concrete workspace/tool/path/network/credential enforcement and enforcement evidence.

17. **What minimal implementation changes are expected?**  
    A small role-contract domain/evaluation package and tests, with no initial DB migration.

18. **What proves the design?**  
    The deterministic and negative test matrix in §26 plus independent design review against A01–A11.

---

## 29. Risks and mitigations

### R1 — Role Contract becomes hidden RBAC

**Mitigation:** role eligibility is tri-state and explicitly non-authoritative; no users/groups/inheritance/ACL database.

### R2 — Capability is mistaken for authority

**Mitigation:** `PERMITTED_BY_ROLE` naming, separate authority prerequisite, negative tests.

### R3 — Protected verification policy leaks into filesystem mechanics

**Mitigation:** Slice 2.2 defines semantic operations only; Slice 2.4 owns path/tool enforcement.

### R4 — GovernanceProfile is accidentally reimplemented

**Mitigation:** consume profile requirements/references; do not select/score profiles.

### R5 — Runtime/provider details leak into role domain

**Mitigation:** reuse Slice 2.1 RuntimeCapability/RuntimeProvenance; no provider-specific role types.

### R6 — PROPOSED_WORK becomes a shadow backlog

**Mitigation:** no Slice/lifecycle/authorization/executable fields and no initial proposal table.

### R7 — Empty next-work projection is mislabeled BACKLOG_EXHAUSTED

**Mitigation:** exact tri-state successor semantics; only positively established absence maps to exhaustion.

### R8 — Design absorbs Slice 2.3/2.4

**Mitigation:** explicit ownership boundary in D18 and static implementation checks.

---

## 30. Independent design-review checklist

Independent review must answer YES to all:

- all B3 A01–A11 criteria are covered;
- role identity/version/class are explicit;
- ActorRef is reused rather than reinvented;
- role/action eligibility cannot manufacture authority;
- implementer/evaluator/Human/promotion separation is explicit;
- stronger separation remains GovernanceProfile/policy-selected;
- protected verification mutation/approval/evaluation are distinct;
- evaluator outcome does not create mutation authority;
- runtime/provider/model provenance reuses Slice 2.1;
- no runtime/provider-specific role semantics leak into Relay domain;
- exact work authority remains external and mandatory;
- decomposition cannot extend authoritative work;
- PROPOSED_WORK is structurally non-authoritative;
- successor resolution distinguishes NONE from NOT_DETERMINABLE;
- BACKLOG_EXHAUSTED is successful stop, not lifecycle;
- no new backlog/lifecycle/role database is introduced;
- Slice 2.3, 2.4, and Phase 3 ownership remains intact;
- implementation scope is small and deterministically testable.

Any NO requires REWORK or ESCALATE.

---

## 31. Design disposition

```text
RLY-S22-DESIGN-AUTH-001 — AUTHORIZED

Slice 2.2:
OPEN

Role Contracts design:
REVISION 1 COMPLETE
READY FOR INDEPENDENT DESIGN REVIEW

Implementation:
NOT AUTHORIZED

Operational DB / lifecycle mutation:
NOT AUTHORIZED

Slice 2.3:
NOT OPEN / NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

**Design complete != design accepted. Design accepted != implementation authorized.**
