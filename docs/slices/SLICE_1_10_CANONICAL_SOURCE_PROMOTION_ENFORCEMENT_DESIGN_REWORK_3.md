# Slice 1.10 — Canonical Source and Promotion Enforcement
## Design Revision 4 / Rework 3

- **Document class:** Lockable design rework record
- **Status:** PROPOSED FOR INDEPENDENT DESIGN RE-REVIEW
- **Date:** 2026-10-12
- **Project:** Relay
- **Slice:** 1.10 — Canonical Source and Promotion Enforcement
- **Opening:** `RLY-S110-OPEN-001 — OPEN`
- **Design authority:** `RLY-S110-DESIGN-AUTH-001 — AUTHORIZED`
- **Rework basis:** `RLY-S110-DESIGN-EVAL-003 — REVISE`
- **Revision 1:** `f9141f6f44927f2a13b85cce8ffd4501db0b183d`
- **Revision 2 / Rework 1:** `6b7f69d69da90879fd536b2edbbaad6d6f3da8c7`
- **Revision 3 / Rework 2:** `28e7f2d1e69a912ed98423e9ae78d932d2cda849`
**Implementation authorization:** NOT GRANTED

---

## 1. Rework contract and precedence

The composite Slice 1.10 design is:

```text
Revision 1
+ Revision 2 / Rework 1
+ Revision 3 / Rework 2
+ Revision 4 / Rework 3
```

Revision 4 controls only where it explicitly amends prior revisions. All other accepted design decisions remain unchanged. This addendum resolves only `F007 — quarantine reconciliation permits post-hoc policy weakening` from `RLY-S110-DESIGN-EVAL-003 — REVISE`.

Revision 4 adds:

```text
RW9 — freeze the Relay policy binding for the full lifetime of quarantine
RW10 — bind reconciliation to the original intent's exact policy and binding
RW11 — remove Revision 3's quarantine-time MANAGED -> MANAGED exception
```

Revisions 1, 2, 3, and all prior evaluation records remain unchanged and byte-preserved.

---

## 2. F007 and governing invariant

Revision 3 allowed a `MANAGED(P1) -> MANAGED(P2)` binding transition during quarantine, while its reconciliation checks used the current policy. That combination could let a later, weaker `P2` legitimize a visible canonical mutation that was not verifiably valid under original policy `P1`.

The governing invariant is:

```text
A later policy change must never retroactively legitimize a canonical
mutation that was not verifiably valid under the exact policy governing
the original promotion attempt.
```

```text
QUARANTINE FREEZES POLICY.

Fresh evidence may change.
External enforcement may be repaired under separate authority.
Human reconciliation authority may be newly issued.

The Relay policy and durable binding governing the original visible
promotion attempt do not change until that quarantine is resolved.
```

Reconciliation proves the original attempt under its original policy. It does not re-judge that attempt under a later policy.

---

## 3. RW9 — Freeze Relay policy and binding during quarantine

### 3.1 Binding-transition eligibility

Policy-binding transition preparation is eligible only for a healthy exact canonical ref:

```text
prepare_policy_binding_transition(...):
  resolve exact canonical-ref health

  if HEALTHY:
    continue ordinary exact Human-authorized binding-transition checks

  if QUARANTINED:
    return INELIGIBLE

  if UNKNOWN:
    return UNKNOWN
```

No canonical-policy binding transition for that exact ref may be prepared, authorized, or executed while health is `QUARANTINED` or `UNKNOWN`. This prohibition includes:

```text
MANAGED -> UNMANAGED
MANAGED(P1) -> MANAGED(P2)
UNMANAGED -> MANAGED
```

There is no quarantine-time policy-revision exception in v1. Revision 3's sentence that allowed a `MANAGED -> MANAGED` policy revision during quarantine is withdrawn and has no normative force. It must not be used as an implementation option or inferred exception. The general no-binding-transition-during-quarantine rule controls.

The rule does not add a policy-strength ordering or comparison algorithm. `P2 >= P1` semantics are out of scope for Slice 1.10 v1.

### 3.2 Health table

```text
CanonicalRefHealth == HEALTHY:
  ordinary exact Human-authorized binding transitions may be considered

CanonicalRefHealth == QUARANTINED:
  every canonical-policy binding transition for the exact ref is forbidden

CanonicalRefHealth == UNKNOWN:
  every canonical-policy binding transition for the exact ref is forbidden
```

`UNKNOWN` fails closed; it is not treated as healthy or unmanaged.

### 3.3 External-control repair is a separate boundary

Relay's durable promotion policy/binding is distinct from external GitHub enforcement configuration:

```text
During unresolved quarantine:
  Relay MANAGED binding: FROZEN
  Relay promotion policy: FROZEN
  GitHub rulesets/settings: may be restored or corrected only under
                            separate explicit repository-setting authority
```

For example, if the original binding is `P1`, GitHub control drift caused `VISIBLE_UNVERIFIED`, and a separately authorized operator restores GitHub controls so they again conform to `P1`, reconciliation may become eligible after fresh verification. The durable Relay binding remains the exact original `P1`. Changing Relay to a weaker `P2` to make reconciliation easier is forbidden. This design grants no repository-setting mutation authority.

---

## 4. RW10 — Reconciliation is bound to the original promotion

### 4.1 Exact reconciliation subject

Amend `CanonicalPromotionReconciliationSubjectV1`. Its governing policy identity is taken from the original promotion intent and exact original promotion subject, not from a later mutable binding.

The subject contains at minimum:

```text
schema_version = 1

project_id
repository: RepositoryRef
canonical_ref

promotion_id
visible_unverified_result_digest

original_subject_digest
original_target_commit

original_binding_id
original_binding_revision
original_binding_digest
original_policy_digest

expected_visible_head

original_governance_basis_digest

current_required_check_observation_digest
current_source_control_observation_digest
```

`expected_visible_head` must equal `original_target_commit`. The exact current binding is checked against the original identity; it does not replace it in the subject. `original_policy_digest` is the sole governing policy digest. Do not add an ambiguous `current_policy_digest` field.

The two `current_*_observation_digest` values bind fresh evidence gathered for this reconciliation. They do not change or supersede the original policy basis.

### 4.2 Reconciliation preparation

`prepare_canonical_reconciliation(...)` is read-only and returns `RECONCILABLE`, `INELIGIBLE`, or `UNKNOWN`. It requires all of the following:

1. The exact unresolved `VISIBLE_UNVERIFIED` result exists.
2. The current canonical head equals the original promotion target.
3. Current canonical health is `QUARANTINED`.
4. The current durable binding exists and its full chain/payload/digest is valid.
5. The current binding is exactly the original `binding_id`, `binding_revision`, and `binding_digest` recorded in the original intent/subject.
6. The current bound policy digest equals `original_policy_digest`.
7. Original promotion intent, authorization, and result integrity are valid and mutually consistent.
8. The exact target commit exists.
9. The original governance basis remains structurally valid and current as required by the original promotion policy.
10. Fresh required-check observations satisfy the exact original policy.
11. A fresh, version-consistent source-control observation satisfies the exact original policy.
12. No accepted reconciliation already exists for the exact promotion.

Classification is fail-closed:

```text
current binding differs from original binding:
  RECONCILABLE = false; return INELIGIBLE

original binding/policy cannot be reconstructed exactly:
  return UNKNOWN; quarantine remains

original policy requirement is positively violated:
  return INELIGIBLE; quarantine remains

required observation or integrity evidence is unavailable/ambiguous:
  return UNKNOWN; quarantine remains
```

Do not adapt the authorized subject to a successor binding or policy. A weaker or stronger successor policy cannot be substituted. The binding is frozen, not compared by strength.

### 4.3 Reconciliation execution

`execute_canonical_reconciliation(...)` performs zero Git writes. It revalidates the original basis and fresh evidence before appending only the immutable local reconciliation record:

```text
1. load exact unresolved quarantine result
2. load original promotion intent
3. load exact reconciliation authority
4. resolve current durable binding
5. require current binding == original frozen binding
6. require current head == original target
7. reverify original governance basis
8. reverify target checks against original policy
9. obtain fresh stable source-control observation
10. evaluate observation against original policy
11. recompute exact reconciliation subject
12. require exact equality with Human-authorized subject
13. BEGIN IMMEDIATE
14. require quarantine still unresolved
15. require no reconciliation record exists
16. append immutable reconciliation record
17. COMMIT
```

No `PATCH` ref update, force update, new commit, policy update, binding update, or ruleset update occurs in reconciliation execution. SQLite transactions do not span GitHub I/O; all remote observations precede the local transaction.

### 4.4 Reconciliation record

Amend `CanonicalPromotionReconciliationV1` to preserve the frozen original policy/binding basis and current evidence provenance:

```text
reconciliation_id
promotion_id

project_id
repository: RepositoryRef
canonical_ref

original_visible_unverified_result_digest
target_commit

authorization_id
reconciliation_subject_digest

original_binding_id
original_binding_revision
original_binding_digest
original_policy_digest

original_governance_basis_digest

current_required_check_observation_digest
current_source_control_observation_digest

reconciled_at
reconciled_by

outcome = RECONCILED
```

The record means:

```text
The already-visible exact target was subsequently proven valid under
the exact original promotion policy and exact original durable binding,
using fresh evidence and explicit Human reconciliation authority.
```

It does not mean that a later policy decided the earlier mutation was acceptable. The original `VISIBLE_UNVERIFIED` result, original intent, original authorization, and original binding history remain immutable. An accepted reconciliation changes only derived health from `QUARANTINED` to `HEALTHY`; it does not alter or rewrite policy-binding history or the original result.

---

## 5. RW11 — Quarantine semantics and removed exception

Preserve Revision 3's quarantine state model and all other quarantine behavior:

```text
VISIBLE_UNVERIFIED
    -> QUARANTINED

QUARANTINED:
    ordinary promotion blocked
    repository sync mutation blocked
    automatic retry blocked
    force/backward recovery forbidden
```

An accepted exact reconciliation may derive:

```text
QUARANTINED -> HEALTHY
```

The original `VISIBLE_UNVERIFIED` evidence remains immutable. No mutable quarantine table, force reset, destructive rollback, or forward corrective-history path is added by Revision 4.

Revision 3 contains two incompatible statements: binding transition preparation generally requires no unresolved quarantine, while its quarantine-effects section permits a `MANAGED -> MANAGED` transition during quarantine. Revision 4 explicitly removes the latter exception. The general rule is unambiguous: no binding transition while the exact canonical ref is `QUARANTINED` or `UNKNOWN`.

---

## 6. Persistence boundary

Migration v6 remains exactly the Revision-3 four-table design:

```text
canonical_promotion_policy_bindings
repository_promotion_intents
repository_promotion_results
repository_promotion_reconciliations
```

No fifth table is needed. Revision 4 adds no policy-order table, quarantine table, recovery queue, worker lease, or policy-comparison state. Quarantine remains derived from immutable result and reconciliation history.

---

## 7. Required future implementation tests

Add these exact requirements to the Revision-3 implementation test matrix; retain all prior Revision-1/2/3 test requirements:

```text
QUARANTINED blocks MANAGED(P1) -> MANAGED(P2)
QUARANTINED blocks MANAGED -> UNMANAGED
UNKNOWN health blocks every binding transition

reconciliation subject binds original_binding_id
reconciliation subject binds original_binding_revision
reconciliation subject binds original_binding_digest
reconciliation subject binds original_policy_digest

current binding mismatch -> reconciliation non-executable
current policy digest mismatch -> reconciliation non-executable
weaker successor policy cannot be substituted for original policy
stronger successor policy cannot be substituted either; binding is frozen

fresh GitHub controls restored to original P1 -> reconciliation may be RECONCILABLE
current controls violating original P1 -> INELIGIBLE
unverifiable original P1 -> UNKNOWN

accepted reconciliation does not alter policy-binding history
accepted reconciliation does not alter original VISIBLE_UNVERIFIED result
reconciliation execution performs zero Git ref writes
```

---

## 8. Composite design and remaining authority gates

If Revision 4 is accepted, the complete design subject is Revision 1 + Revision 2/Rework 1 + Revision 3/Rework 2 + Revision 4/Rework 3, with each later addendum controlling only where it explicitly amends prior text. Revision 4 resolves only F007. Prior findings F001–F006 and every other accepted design decision remain unchanged.

```text
Slice 1.10:
OPEN

Independent design evaluation 003:
RLY-S110-DESIGN-EVAL-003 — REVISE

Independent design evaluation 004:
PENDING

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED

Repository-setting mutation:
NOT AUTHORIZED

Credential / App-permission mutation:
NOT AUTHORIZED

Workflow mutation:
NOT AUTHORIZED

Schema migration execution:
NOT AUTHORIZED

Canonical promotion:
NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED
```

This addendum is design only. The next gate is `RLY-S110-DESIGN-EVAL-004` with outcome `ACCEPT | REVISE | ESCALATE`. Design rework authority is not implementation authority.
