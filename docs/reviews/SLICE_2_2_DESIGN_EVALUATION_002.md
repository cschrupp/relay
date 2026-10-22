# Slice 2.2 — Independent Design Evaluation — Revision 2 Re-review

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Slice:** 2.2 — Role Contracts  
**Evaluation ID:** `RLY-S22-DESIGN-EVAL-002`  
**Outcome:** `ACCEPT`  
**Design authority:** `RLY-S22-DESIGN-AUTH-001 — AUTHORIZED`  
**Revision 1 commit:** `63895f87e8f47a0e22a192e6cdbd002e6d51e45d`  
**Revision 1 blob:** `04d3b0bb3691779b395262a7aff54727a8f43896`  
**Revision 2 amendment commit:** `f95b26d7123152627418f50b01cb99f9eb3ca0a3`  
**Revision 2 amendment blob:** `a3244554e6cc78c0ac4dce18ab01f04e20d35115`  
**Prior evaluation:** `RLY-S22-DESIGN-EVAL-001 — REWORK`  
**Reviewer role:** Slice 2.2 Design Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The combined design:

```text
Revision 1
+
Revision 2 Amendment
```

satisfies the authorized Slice 2.2 Role Contracts design scope and the B3-frozen A01–A11 acceptance contract.

All blocking and major findings from `RLY-S22-DESIGN-EVAL-001` are closed.

This evaluation is evidence only. Human design acceptance and implementation authorization remain separate gates.

---

## Review basis

The re-review checks the combined design against:

- `RLY-S22-DESIGN-AUTH-001`;
- `RLY-S22-DESIGN-EVAL-001 — REWORK`;
- the B3-frozen Slice 2.2 definition and A01–A11 criteria;
- the accepted Governance Assurance Reference Model;
- the accepted Slice 2.1 Agent Runtime Contract;
- the established Relay role-separation clarification.

The Revision 2 rework diff from evaluation commit `ee2d03b6c4cab767381dae2fc9576ade2ef2ec02` to candidate `f95b26d7123152627418f50b01cb99f9eb3ca0a3` is exactly one new design-amendment file:

`docs/slices/SLICE_2_2_ROLE_CONTRACTS_DESIGN_REV2_AMENDMENT.md`

No production source, schema, database, lifecycle, runtime, Work Packet, workspace-enforcement, Slice 2.3/2.4, Phase 3, or promotion change is present.

---

## F001 — Required input/output contract semantics

**Prior status:** BLOCKING  
**Disposition:** CLOSED

Revision 2 adds normative, digest-bound:

```text
required_inputs: tuple[RoleInputRequirement, ...]
required_outputs: tuple[RoleOutputRequirement, ...]
```

to the Role Contract.

The design now clearly separates ownership:

```text
Slice 2.2:
defines what semantic inputs/outputs a role requires

Slice 2.3:
transports exact references/values satisfying those requirements
```

The initial bounded input vocabulary covers actor identity, applicable role binding, GovernanceProfile, authorized work, source baseline, accepted design, evaluation/evidence/decision/promotion bases, and runtime execution basis.

The output vocabulary covers engineering result, execution evidence, evaluation judgment, Human decision, promotion evidence, and work disposition.

Conformance is deterministic:

```text
SATISFIED
UNSATISFIED
INDETERMINATE
```

with missing/stale/conflicting/unverifiable required facts fail-closed.

The design also correctly makes these **minimum semantic requirements**, not a complete packet-field allowlist.

B3 A03 is now satisfied without importing Slice 2.3 Work Packet design.

---

## F002 — Applicable/accepted Role Contract binding

**Prior status:** BLOCKING  
**Disposition:** CLOSED

Revision 2 introduces the semantic `ApplicableRoleContractBinding` and freezes an applicability predicate requiring:

- exact RoleContractRef content identity;
- exact governed subject;
- exact current PolicyBasis;
- exact/current GovernanceProfile where required;
- policy/profile or valid explicit Human Authority selection of the exact RoleContractRef;
- current required authority basis;
- no conflicting/superseding selection.

Applicability is explicitly:

```text
APPLICABLE
NOT_APPLICABLE
INDETERMINATE
```

Only `APPLICABLE` may proceed to role-action evaluation.

This closes the prior permissive-self-authorship failure mode:

```text
valid RoleContract bytes/digest
    !=
applicable RoleContract policy
```

The design correctly places selection in the Control/Governance plane and explicitly forbids selection by:

- executor;
- evaluator merely by evaluating;
- runtime;
- provider/model;
- prompt text;
- branch name;
- workspace capability;
- RoleContract self-description;
- latest/best-match discovery.

It also establishes prospective binding and forbids retroactive role-policy repair.

Slice 2.3 is limited to transporting an already-established exact binding rather than manufacturing role-policy authority.

No second authority system or role-policy database is introduced.

---

## F003 — Role key/revision/digest conflict semantics

**Prior status:** MAJOR  
**Disposition:** CLOSED

Revision 2 freezes:

```text
within one exact applicable PolicyBasis:

(role_key, revision) -> exactly one content_digest
```

and:

```text
same PolicyBasis
+ same role_key
+ same revision
+ different digest
    ->
ROLE_CONTRACT_IDENTITY_CONFLICT
INDETERMINATE / FAIL CLOSED
```

A successor contract in the same policy/role-key lineage increments revision.

Different PolicyBasis values remain explicit and may select distinct lineages/content without being silently merged.

Consumers require an exact RoleContractRef. Latest/max-revision/newest/best-match fallback is explicitly forbidden.

The identity/version requirement is therefore implementation-significant and deterministic.

---

## Prior non-blocking clarification — action coverage

**Disposition:** CLOSED / ADOPTED

Revision 2 requires:

```text
for every RoleAction known to the RoleContract schema version:

allowed_actions U prohibited_actions
    == complete action set
```

with disjoint membership.

A future action unknown to an older contract becomes:

```text
ROLE_ACTION_UNKNOWN_TO_CONTRACT_SCHEMA
-> INDETERMINATE / FAIL CLOSED
```

This gives complete explicit classification for each known contract schema while preserving forward fail-closed behavior.

---

## Combined-design architecture assessment

### Role / identity / capability / authority separation — PASS

The combined design preserves:

```text
role != actor identity != runtime identity != model identity
identity != capability != authority
PERMITTED_BY_ROLE != AUTHORIZED
```

`ActorRef` is reused rather than replaced.

Runtime/provider/model identity remains Slice 2.1 provenance.

Role evaluation cannot issue Human authority, accept results, promote baselines, create successor work, or mutate lifecycle.

### Role classes — PASS

The initial classes remain bounded:

```text
IMPLEMENTER
INDEPENDENT_EVALUATOR
HUMAN_AUTHORITY
PROMOTION_EXECUTOR
```

The design avoids prematurely turning architect/planner/researcher/vendor agent labels into permanent domain classes.

### Evaluator independence — PASS

Policy-selected separation is explicit.

When independent evaluation is required:

```text
implementer ActorRef != evaluator ActorRef
```

and runtime-backed evaluation additionally requires distinct execution/session identity as defined by the accepted Slice 2.1 contract.

The design does not invent a global designer != evaluator rule and remains consistent with the established Relay clarification.

### Protected Verification Assets — PASS

READ, CREATE, PROPOSE_MUTATION, MODIFY, APPROVE_MUTATION, EXECUTE, and EVALUATE remain separate semantic permissions.

The combined design preserves:

```text
evaluator review != mutation authority
evaluation outcome != mutation authority
repository write capability != protected-asset mutation authority
```

Concrete path/tool enforcement remains correctly deferred to Slice 2.4.

### GovernanceProfile boundary — PASS

Role Contracts consume applicable GovernanceProfile/policy requirements and do not select, score, or redesign GovernanceProfile.

Unknown/stale/conflicting profile applicability fails closed.

### Runtime boundary — PASS

The design reuses Slice 2.1:

- ExecutionId;
- RuntimeExecutionRequest/Basis;
- RuntimeCapability;
- RuntimeProvenance;
- runtime/session bindings.

No OpenCode/provider-specific types leak into Role Contract semantics.

Runtime permission/capability remains subordinate to Relay authority.

### Work-authority boundary — PASS

Exact current work authority remains a separate prerequisite.

The combined design correctly refuses to infer authority from:

- roadmap placement;
- PROPOSED lifecycle;
- role eligibility;
- runtime capability;
- workspace write capability;
- model recommendation;
- internal decomposition;
- document presence.

### Internal decomposition — PASS

Internal decomposition remains subordinate planning inside the current exact work boundary and cannot alter acceptance criteria, widen workspace, add authoritative dependencies, create successor Slice identity, or extend the authoritative backlog.

### PROPOSED_WORK — PASS

`PROPOSED_WORK` remains non-authoritative evidence/content with no:

- authorization;
- lifecycle phase;
- runnable status;
- successor authority;
- implicit Slice creation;
- automatic priority.

No proposal/backlog persistence subsystem is introduced.

### Successor resolution / BACKLOG_EXHAUSTED — PASS

The design preserves the essential tri-state distinction:

```text
AUTHORIZED_SUCCESSOR_ESTABLISHED
NO_AUTHORIZED_SUCCESSOR
SUCCESSOR_NOT_DETERMINABLE
```

Only positively established `NO_AUTHORIZED_SUCCESSOR` maps to successful `BACKLOG_EXHAUSTED`.

Unknown/conflicting state maps to escalation/stop.

An available successor still requires a fresh governed Work Packet/execution; authority does not flow implicitly from the current executor.

`BACKLOG_EXHAUSTED` remains a work disposition, not lifecycle, evaluation, acceptance, or promotion.

### Design economy — PASS

The proposed implementation remains a small pure-domain package:

```text
src/relay_engine/role_contracts/
  __init__.py
  models.py
  evaluation.py
```

No initial database migration/table, CLI, UI, runtime adapter change, workspace enforcement, provider call, or new authority store is required.

---

## B3 A01–A11 final disposition

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
```

### A01

Role identity/version/class, actor identity, runtime identity, and model identity are distinct with binding/provenance semantics.

### A02

Capability and role eligibility remain distinct from authority.

### A03

Allowed/prohibited actions, required inputs, required outputs, and evidence/assurance obligations are now explicit and deterministically testable.

### A04

Implementer/evaluator/Human/promotion responsibilities and protected-verification controls are explicit and policy-bound.

### A05

Requested/actual runtime-provider-model provenance reuses the accepted Slice 2.1 model.

### A06

Work authority resolves separately to exact governed work/current authority and cannot be inferred from role/capability/state.

### A07

Decomposition cannot extend authoritative work.

### A08

Discovered future work remains non-authoritative `PROPOSED_WORK`.

### A09

Positively established lack of successor maps to successful `BACKLOG_EXHAUSTED`.

### A10

Missing/stale/conflicting/invalid policy, authority, identity, provenance, input/output, or successor state fails closed and escalates.

### A11

Work Packet, workspace enforcement, lifecycle/backlog persistence, and Phase 3 ownership remain outside Slice 2.2.

---

## Non-blocking implementation clarification — root Human Authority bootstrap

The combined design says applicable Role Contract selection may be established by existing Relay policy/GovernanceProfile semantics or by valid explicit Human Authority.

Implementation must preserve the pre-existing governance invariant:

```text
Human root authority
    exists independently of RoleContract
```

A RoleContract may describe/check the `HUMAN_AUTHORITY` role for downstream policy conformance. It must never become the source of, or a bootstrap prerequisite for, the Human's root authority to issue the policy/authority decision that selects a Role Contract.

In other words:

```text
RoleContract constrains/records role conformance
RoleContract does not create Human Authority
```

The current combined design is already compatible with this rule because Role Contract selection is defined as an external Control/Governance-plane fact. This clarification is therefore non-blocking and should be retained explicitly in the implementation handoff/tests.

---

## Required implementation handoff constraints

A later implementation authorization should preserve at minimum:

1. pure immutable Role Contract/domain models;
2. canonical deterministic digest;
3. exact `RoleContractRef`;
4. exact applicability evaluation;
5. complete schema-version action classification;
6. required input/output evaluation;
7. actor-kind and separation checks;
8. protected-verification permission checks;
9. Slice 2.1 provenance/capability reuse;
10. exact role-key/revision/digest conflict handling;
11. no latest/best-match contract resolution;
12. no Role Contract self-selection;
13. no Role Contract creation of Human/work authority;
14. bounded `PROPOSED_WORK` semantics;
15. successor tri-state and `BACKLOG_EXHAUSTED`;
16. no DB migration/role catalog;
17. no Slice 2.3/2.4/Phase 3 implementation.

The deterministic and negative tests specified by Revision 1 + Revision 2 are part of the accepted design obligations.

---

## Independent disposition

```text
RLY-S22-DESIGN-EVAL-002 — ACCEPT

Revision 1:
63895f87e8f47a0e22a192e6cdbd002e6d51e45d

Revision 2 Amendment:
f95b26d7123152627418f50b01cb99f9eb3ca0a3

F001:
CLOSED

F002:
CLOSED

F003:
CLOSED

B3 A01-A11:
ALL PASS

Combined Slice 2.2 design:
INDEPENDENTLY ACCEPTED

Human design acceptance:
PENDING

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
```

Independent design ACCEPT does not itself grant implementation authority.
