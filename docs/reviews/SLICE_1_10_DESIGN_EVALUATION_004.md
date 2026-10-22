# Slice 1.10 — Independent Design Evaluation 004

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-12  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Evaluation ID:** `RLY-S110-DESIGN-EVAL-004`  
**Outcome:** `ACCEPT`  
**Design authority:** `RLY-S110-DESIGN-AUTH-001 — AUTHORIZED`  
**Composite design subject:** Revision 1 + Revision 2/Rework 1 + Revision 3/Rework 2 + Revision 4/Rework 3  
**Revision 1:** `f9141f6f44927f2a13b85cce8ffd4501db0b183d`  
**Revision 2 / Rework 1:** `6b7f69d69da90879fd536b2edbbaad6d6f3da8c7`  
**Revision 3 / Rework 2:** `28e7f2d1e69a912ed98423e9ae78d932d2cda849`  
**Revision 4 / Rework 3:** `60dced8e88ae8d0d8e69e2916e465374a6b931db`  
**Evaluator:** GPT-5.6 Sol — independent design reviewer

## 1. Decision

```text
ACCEPT
```

The four-part composite design satisfies the exact Slice 1.10 design authority and closes all findings from `RLY-S110-DESIGN-EVAL-001`, `-002`, and `-003` without introducing a new authority gap, alternate canonical-write path, mutable recovery shortcut, policy-substitution path, or unbounded implementation surface.

Exact-head CI for Revision 4:

```text
38272141516 — SUCCESS
```

Passing CI is engineering evidence only. This evaluation is independent design evidence, not Human design acceptance and not implementation authorization.

## 2. Exact subject and repository-state verification

Independent verification established:

```text
design branch head:
60dced8e88ae8d0d8e69e2916e465374a6b931db

starting evaluation baseline:
e51f73e151aa0c454a612575e95f59fee88fddb0

Revision-4 diff:
.relay/registry.json
docs/slices/SLICE_1_10_CANONICAL_SOURCE_PROMOTION_ENFORCEMENT_DESIGN_REWORK_3.md

candidate relation:
ahead by 1 / behind by 0

canonical main:
0a0b415ceafd78401e6fa2cae24c208e0fe82a75
unchanged

registry:
205 artifacts before this evaluation record
unique paths PASS
unique artifact IDs PASS
normative ordering PASS
malformed artifact IDs NONE
canonical keys exactly 5 and unchanged
```

Revision 4's registered artifact is a `LOCKABLE_RECORD / REVIEW` with exact digest and does not rewrite prior design/evaluation history.

## 3. Findings disposition

```text
F001 — RESOLVED
F002 — RESOLVED
F003 — RESOLVED
F004 — RESOLVED
F005 — RESOLVED
F006 — RESOLVED
F007 — RESOLVED
```

## 4. F007 resolution — PASS

Revision 4 closes the final policy-substitution defect by freezing the exact durable Relay policy/binding throughout unresolved quarantine.

Normative composite behavior is now unambiguous:

```text
health == HEALTHY:
  exact Human-authorized binding transitions may be considered

health == QUARANTINED:
  all binding transitions for that exact canonical ref are forbidden

health == UNKNOWN:
  all binding transitions for that exact canonical ref are forbidden
```

The removed Revision-3 MANAGED -> MANAGED quarantine exception has no remaining normative force.

Revision 4 also avoids introducing a policy-strength calculus. A weaker or stronger successor policy is equally unusable for reconciliation because the binding is frozen rather than compared.

## 5. Reconciliation policy continuity — PASS

`CanonicalPromotionReconciliationSubjectV1` now binds the original promotion basis:

```text
original_binding_id
original_binding_revision
original_binding_digest
original_policy_digest
original_governance_basis_digest
```

Fresh required-check and source-control observations remain current evidence only.

They do not replace or supersede the governing policy.

Reconciliation therefore proves:

```text
the already-visible exact target satisfies the exact original promotion policy/binding
using fresh evidence
under exact new Human reconciliation authority
```

and does not mean that a later policy retrospectively accepted the earlier mutation.

## 6. Canonical quarantine/recovery — PASS

The accepted composite contract preserves:

```text
VISIBLE_UNVERIFIED
  -> QUARANTINED

QUARANTINED:
  ordinary promotion blocked
  RepositorySync mutation blocked
  automatic retry blocked
  binding changes blocked
  force/backward recovery forbidden
```

The v1 recovery remains exactly one bounded path:

```text
exact Human reconciliation of the already-visible target
```

Reconciliation performs no Git ref write and never rewrites the original promotion result, intent, authority, binding history, or policy history.

Accepted reconciliation only changes the derived canonical health from `QUARANTINED` to `HEALTHY`.

## 7. Durable policy activation and exclusive writer — PASS

The composite design retains the resolved F004/F005 controls:

- canonical governance binding is durable Relay state, not optional process configuration;
- absence/corruption is `UNKNOWN_OR_INVALID`, never implicit `UNMANAGED`;
- explicit UNMANAGED/MANAGED classification is Human-authorized;
- active MANAGED canonical refs are reserved against `RepositorySyncService` mutation;
- unknown binding state blocks remote sync mutation;
- `RepositorySyncSubjectV1` authority cannot substitute for `CanonicalPromotionSubjectV1` authority;
- production low-level ref-update callsites are statically bounded;
- GitHub Ruleset B actor restriction is reinforced by Relay application-level call-path separation.

## 8. Authority and verification separation — PASS

The complete design continues to preserve:

```text
CI success != Human Authority
evaluation ACCEPT != Human design acceptance
Human technical acceptance != promotion
write credential != promotion authority
repository administrator capability != Relay authority
source-control control evidence != authority
promotion receipt != authority
```

`RepositoryMutationAuthorization` remains the one reused exact HUMAN repository-mutation authority envelope for the bounded subject union. No second Human Authority system is invented.

## 9. Source-control enforcement — PASS

The composite design preserves:

- exact repository/ref/parent/target binding;
- exact target-SHA and CI-App check binding;
- required check conclusion `success` for Relay's own predicate;
- stable exact-version ruleset observation;
- isolated Control Verifier capability;
- no ruleset-administration capability in the Promotion App;
- Ruleset A with no bypass actors;
- Ruleset B with exact Promotion App `Integration / always` bypass;
- `update_allows_fetch_and_merge == false`;
- force push and deletion prohibition;
- non-force canonical ref updates only;
- no PR/merge-queue dependency;
- no rebase/squash/cherry-pick recreation during promotion.

Provider controls remain enforcement/evidence adapters, not Relay semantic authority.

## 10. Persistence and crash semantics — PASS

The composite design's migration remains bounded to exactly four append-only v6 tables:

```text
canonical_promotion_policy_bindings
repository_promotion_intents
repository_promotion_results
repository_promotion_reconciliations
```

No mutable quarantine table, worker queue, lease state, generic event store, or policy-strength table is introduced.

The pre-write intent remains durable before the remote side effect, restart reconciliation precedes stale-parent rejection, terminal attempt outcomes remain explicit, and no SQLite write transaction spans GitHub network I/O.

## 11. Design-scope conformance — PASS

The accepted design remains inside `RLY-S110-DESIGN-AUTH-001`.

It does not absorb:

```text
Role Contracts / Slice 2.2
Context / Work Packets / Slice 2.3
Workspace Authority / Slice 2.4
generic SCM abstraction
GitLab/Bitbucket adapters
provider execution
agent execution
Phase 3
formal SLSA certification
cryptographic attestation framework
```

## 12. Accepted composite design

The exact accepted design subject is:

```text
Revision 1:
f9141f6f44927f2a13b85cce8ffd4501db0b183d

+ Revision 2 / Rework 1:
6b7f69d69da90879fd536b2edbbaad6d6f3da8c7

+ Revision 3 / Rework 2:
28e7f2d1e69a912ed98423e9ae78d932d2cda849

+ Revision 4 / Rework 3:
60dced8e88ae8d0d8e69e2916e465374a6b931db
```

Later addenda control only where they explicitly amend earlier text.

## 13. Evaluation result

```text
RLY-S110-DESIGN-EVAL-004 — ACCEPT
```

No blocking or major design finding remains within the authorized Slice 1.10 design scope.

Implementation risks remain to be proven by future implementation/evaluation, particularly:

- exact GitHub ruleset API parsing and version stabilization;
- real credential/capability separation;
- migration/store integrity;
- static ref-update callsite enforcement;
- race/crash fixtures;
- live Relay dogfood of rulesets, policy binding, promotion, quarantine, and reconciliation.

Those are implementation/evidence obligations already required by the accepted design; they are not unresolved design defects.

## 14. Authority boundary after ACCEPT

```text
Slice 1.10:
OPEN

Design authority:
RLY-S110-DESIGN-AUTH-001 — AUTHORIZED

Independent design evaluation:
RLY-S110-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Repository-setting mutation:
NOT AUTHORIZED

Credential / App-permission mutation:
NOT AUTHORIZED

Workflow mutation:
NOT AUTHORIZED

Canonical promotion:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

## 15. Next gate

Independent design ACCEPT is evidence only.

The next required authority event is separate Human design acceptance of this exact composite design subject.

Only after Human design acceptance may a separate implementation authorization be considered.

**ACCEPT — design evidence complete; Human design acceptance remains required.**