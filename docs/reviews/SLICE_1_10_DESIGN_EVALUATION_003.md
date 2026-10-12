# Slice 1.10 — Independent Design Evaluation 003

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-12  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Evaluation ID:** `RLY-S110-DESIGN-EVAL-003`  
**Outcome:** `REVISE`  
**Design authority:** `RLY-S110-DESIGN-AUTH-001 — AUTHORIZED`  
**Composite design subject:** Revision 1 + Revision 2/Rework 1 + Revision 3/Rework 2  
**Revision 1:** `f9141f6f44927f2a13b85cce8ffd4501db0b183d`  
**Revision 2 / Rework 1:** `6b7f69d69da90879fd536b2edbbaad6d6f3da8c7`  
**Revision 3 / Rework 2:** `28e7f2d1e69a912ed98423e9ae78d932d2cda849`  
**Evaluator:** GPT-5.6 Sol — independent design reviewer

## 1. Decision

```text
REVISE
```

Revision 3 successfully resolves F005 and F006 from the prior evaluation and preserves the earlier fixes. One remaining composite-design contradiction prevents final acceptance: quarantine reconciliation can currently occur after a MANAGED -> MANAGED policy change, while the reconciliation predicates are evaluated under the **current** policy rather than the exact policy that governed the visible remote mutation.

That creates a post-hoc policy-weakening path inconsistent with the accepted Revision-1 invariant:

```text
No later profile downgrade retroactively legitimizes a prior promotion.
```

Exact-head CI for Revision 3:

```text
38260109649 — SUCCESS
```

Passing CI is engineering evidence only.

## 2. Prior findings disposition

```text
F001 — RESOLVED
F002 — RESOLVED
F003 — RESOLVED
F004 — RESOLVED
F005 — RESOLVED
F006 — RESOLVED
```

### F005 resolved

Revision 3 correctly replaces optional process configuration with an explicit durable binding chain:

```text
UNMANAGED
MANAGED(exact policy + digest)
derived UNKNOWN_OR_INVALID
```

Absence is `UNKNOWN_OR_INVALID`, never implicit `UNMANAGED`.

`RepositorySyncService` and `CanonicalPromotionService` both consume the same durable binding store, and MANAGED -> UNMANAGED requires exact Human repository-mutation authority.

This closes the previously conditional canonical-ref reservation.

### F006 resolved

`VISIBLE_UNVERIFIED` now creates durable-by-evidence quarantine.

While quarantined:

```text
ordinary promotion blocked
repository sync mutation blocked
MANAGED -> UNMANAGED downgrade blocked
force/backward recovery forbidden
```

Revision 3 also defines one explicit v1 exit:

```text
exact Human-authorized reconciliation of the already-visible target
```

with no Git mutation and immutable preservation of the original `VISIBLE_UNVERIFIED` result.

The quarantine model itself is accepted.

## 3. GitHub adapter assumptions — PASS

The independently checked GitHub API supports the Revision-3 adapter assumptions.

Current documentation confirms:

- `bypass_actors` is omitted unless the observer has write access to the ruleset;
- repository ruleset exact-version endpoints require Administration:write;
- exact-version response state contains ruleset conditions, rules, enforcement, and bypass actors;
- an `update` rule carries required boolean `update_allows_fetch_and_merge`;
- bypass modes include `always`, `pull_request`, and `exempt`;
- check-run reads require Checks:read and support exact check/app/latest filtering.

External references:

```text
https://docs.github.com/en/rest/repos/rules
https://docs.github.com/en/rest/checks/runs
```

RW8's stable-version observation algorithm and `update_allows_fetch_and_merge == false` requirement are therefore acceptable.

## 4. F007 — BLOCKING — quarantine reconciliation permits post-hoc policy weakening

Revision 1 freezes:

```text
No later profile downgrade retroactively legitimizes a prior promotion.
```

Revision 3 freezes both:

```text
A MANAGED -> MANAGED policy revision MAY be prepared during quarantine
only when needed to re-establish conformant controls for reconciliation.
```

and reconciliation requires:

```text
current binding == MANAGED
current binding/policy chain valid
required checks for target are current under current policy
full current source-control observation is conformant
```

The exact reconciliation subject similarly binds:

```text
current_binding_id
current_binding_revision
current_binding_digest
current_policy_digest
```

but does not require:

- current binding/policy == the exact binding/policy that governed the original promotion intent; or
- current policy to be provably non-weaker than the original policy; or
- every original promotion-critical requirement to remain satisfied.

Therefore this sequence is permitted by the text as written:

```text
1. Promotion intent I is created under strict policy P1.
2. GitHub ref visibly moves to target B.
3. Post-write control verification cannot prove P1 -> VISIBLE_UNVERIFIED.
4. Ref becomes QUARANTINED.
5. Human authorizes MANAGED(P1) -> MANAGED(P2).
6. P2 weakens a promotion-critical requirement that prevented clean verification.
7. B satisfies P2.
8. Human authorizes reconciliation under P2.
9. B becomes HEALTHY without ever satisfying P1.
```

Every individual record is exact and Human-authorized, but the combined outcome retroactively legitimizes the earlier visible mutation under a weaker policy.

This is precisely what the Revision-1 invariant forbids.

### Internal ambiguity

Revision 3 also contains a local tension:

```text
3.5 target MANAGED binding preparation:
  requires no unresolved canonical quarantine

versus

4.4 quarantine effects:
  MANAGED -> MANAGED policy revision MAY be prepared during quarantine
  when needed to re-establish conformant controls
```

The intended exception is not specified as a deterministic override and cannot be left for implementation to infer.

### Required rework

Revision 4 MUST freeze one unambiguous quarantine-policy rule.

### Recommended minimum — freeze Relay policy during quarantine

The cleanest v1 rule is:

```text
while canonical health == QUARANTINED or UNKNOWN:

  binding transition UNMANAGED -> *: not applicable to an already-managed quarantine
  MANAGED -> UNMANAGED: FORBIDDEN
  MANAGED(P1) -> MANAGED(P2): FORBIDDEN

  external GitHub rules/settings may be restored under separate repository-setting authority
  but the durable Relay binding/policy remains exact P1

  reconciliation MUST use:
    original intent binding_id
    original intent binding_revision
    original intent binding_digest
    original intent promotion_policy_digest
```

Then reconciliation may prove that current GitHub controls again conform to the exact original policy P1.

This requires no policy-ordering or 'non-weaker-than' calculus and is therefore minimum sufficient for v1.

### Alternative — explicit non-weakening relation

If MANAGED -> MANAGED policy revision during quarantine is retained, Revision 4 must define a deterministic machine-verifiable relation:

```text
P2 >= P1 for every promotion-critical requirement applicable to the original subject
```

and reconciliation must prove both:

```text
original P1 requirements remain satisfied
current P2 requirements are satisfied
```

No semantic partial order currently exists in Relay for arbitrary promotion policies, so this alternative would materially increase design complexity and is **not recommended** for Slice 1.10 v1.

### Reconciliation subject correction

Under the recommended rule, `CanonicalPromotionReconciliationSubjectV1` MUST bind both original and current observations but the policy basis remains the original exact policy:

```text
promotion_id
visible_unverified_result_digest
original_subject_digest
original_target_commit

original_binding_id
original_binding_revision
original_binding_digest
original_policy_digest

expected_visible_head
governance_basis_digest
required_check_observation_digest
current_source_control_observation_digest
```

The freshly observed controls/checks prove present conformance to the original frozen policy; they do not replace the governing policy.

## 5. Required Revision-4 scope

Revision 4 is deliberately narrow.

Preserve all Revision-1/2/3 decisions except where required to close F007.

Required amendments:

```text
RW9 — freeze the exact Relay promotion-policy binding while quarantine is unresolved
RW10 — reconciliation binds original policy/binding, current evidence only
RW11 — remove the contradictory quarantine-time MANAGED->MANAGED exception
```

Required tests:

```text
QUARANTINED blocks MANAGED->MANAGED policy revision
QUARANTINED blocks MANAGED->UNMANAGED downgrade
reconciliation subject uses original binding id/revision/digest
reconciliation subject uses original promotion policy digest
current weaker policy cannot be substituted
external ruleset restoration under same P1 can reconcile
original P1 violation -> reconciliation INELIGIBLE/UNKNOWN
accepted reconciliation never changes original binding/policy history
```

No new persistence table is required for this rework.

No implementation, ruleset mutation, credential mutation, or new Human Authority semantics are authorized by this evaluation.

## 6. Composite design status

The design is now one narrow correction away from acceptance.

Accepted directions to preserve:

- exact repository/ref/parent/target binding;
- reuse of `RepositoryMutationAuthorization`;
- durable MANAGED/UNMANAGED binding with absence fail-closed;
- source-control verifier capability separation;
- exact-version ruleset observation;
- exact check/app/SHA freshness;
- non-force canonical updates;
- exclusive canonical mutation boundary versus RepositorySyncService;
- append-only intent/result evidence;
- restart-first reconciliation after ambiguous/crashed ref update;
- per-property exact governance subjects and control continuity;
- quarantine derived from immutable evidence;
- exact Human reconciliation with zero Git writes;
- no force/backward recovery;
- no workflow/ruleset self-administration by the promotion executor.

## 7. Authority boundary

```text
Slice 1.10:
OPEN

Design authority:
RLY-S110-DESIGN-AUTH-001 — AUTHORIZED

Composite design:
Revision 1
+ Revision 2 / Rework 1
+ Revision 3 / Rework 2

Independent design evaluation:
RLY-S110-DESIGN-EVAL-003 — REVISE

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED

Repository-setting mutation:
NOT AUTHORIZED

Credential installation/permission mutation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

## 8. Next gate

The existing design authority permits the bounded Revision-4 repair.

After Revision 4 is frozen:

```text
RLY-S110-DESIGN-EVAL-004

Outcome:
ACCEPT | REVISE | ESCALATE
```

**REVISE — all previous blockers are closed, but quarantine recovery must remain bound to the exact original promotion policy so later policy changes cannot retroactively authorize what was not valid at the time of the visible mutation.**