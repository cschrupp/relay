# Slice 1.10 — Independent Design Evaluation 002

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-12  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Evaluation ID:** `RLY-S110-DESIGN-EVAL-002`  
**Outcome:** `REVISE`  
**Design authority:** `RLY-S110-DESIGN-AUTH-001 — AUTHORIZED`  
**Composite design subject:** Revision 1 + Revision 2/Rework 1  
**Revision 1:** `f9141f6f44927f2a13b85cce8ffd4501db0b183d`  
**Revision 2 / Rework 1:** `6b7f69d69da90879fd536b2edbbaad6d6f3da8c7`  
**Evaluator:** GPT-5.6 Sol — independent design reviewer

## 1. Decision

```text
REVISE
```

Revision 2 successfully resolves the four blocking findings from `RLY-S110-DESIGN-EVAL-001` and materially improves the architecture. Two remaining design gaps prevent final design acceptance because they affect the claimed fail-closed exclusive-canonical-write contract and the governed state after an externally visible but unverifiable mutation.

Exact-head CI for Revision 2:

```text
38202434815 — SUCCESS
```

Passing CI is engineering evidence only.

## 2. Prior findings disposition

### F001 — RESOLVED

The separate `SourceControlVerifierPort` / `GitHubRulesetVerifier` design gives the promotion path a machine-verifiable source for ruleset bypass posture without placing repository-administration capability in the promotion executor.

Current GitHub documentation confirms:

- `GET /repos/{owner}/{repo}/rulesets/{ruleset_id}` requires only Metadata:read for ordinary visibility;
- `bypass_actors` is returned only when the caller has write access to the ruleset;
- repository ruleset history/version endpoints require Administration:write;
- ruleset bypass actors support `Integration` and bypass modes `always`, `pull_request`, and `exempt`.

External evidence:

```text
https://docs.github.com/en/rest/repos/rules
```

Revision 2's capability separation is acceptable:

```text
Promotion App:
  no administration permission

Control Verifier:
  separate credential
  administration:write only because GitHub requires it for the needed observation
  no contents:write
  GET-only adapter surface
```

The privileged verifier credential remains a high-value secret, but that is an operational security concern rather than a design blocker because it is separated from the canonical mutation executor and no mutation surface is exposed by the designed verifier adapter.

### F002 — RESOLVED

Restart-first reconciliation now occurs before ordinary stale-parent rejection.

The persisted intent supports the required crash window:

```text
remote ref == target + no result
  -> observe/reconcile
  -> zero second PATCH
```

The design also correctly removes the long SQLite transaction across remote network I/O and persists exact pre-write evidence before the side effect.

### F003 — RESOLVED

The composite design no longer relabels ancestor Human acceptance as acceptance of the final target.

Per-property exact subjects plus `PromotionGovernanceBasisV1`, `governance_basis_digest`, and `RELAY_CONTROL_CONTINUITY_VERIFIED` preserve statement-class separation.

The pre-authorization `AUTHORIZABLE` state also removes Revision 1's circular dependency in which promotion authority was required before the exact subject existed to authorize.

### F004 — PARTIALLY RESOLVED / superseded by F005

Revision 2 correctly introduces an application-level canonical-ref reservation and explicitly prevents a `RepositorySyncSubjectV1` authorization from becoming promotion authority.

The static `update_git_ref` callsite allowlist is also a sound preservation control.

However the reservation is still conditional on a policy-provider response whose absence is not itself governed or fail-closed. F005 below is therefore the remaining closure of this boundary.

## 3. Platform assumptions independently re-verified

GitHub's current public contract supports the main adapter assumptions in the composite design:

```text
ruleset update rule:
  only bypass actors may update matching refs

required status check rule:
  exact context
  optional integration_id
  strict_required_status_checks_policy

non_fast_forward rule:
  blocks force pushes

check-run listing:
  exact ref/SHA
  check_name filter
  app_id filter
  filter=latest
  Checks:read
```

External evidence:

```text
https://docs.github.com/en/rest/repos/rules
https://docs.github.com/en/rest/checks/runs
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
```

These assumptions are not blockers.

## 4. F005 — BLOCKING — active canonical policy/reservation is not durably bound or fail-closed

Revision 2 defines:

```text
CanonicalPromotionPolicyProvider

policy_for(project_id, repository, ref_name)
  -> CanonicalPromotionPolicyV1 | None
```

and uses the same provider/configuration in both:

```text
CanonicalPromotionService
RepositorySyncService
```

The RepositorySync canonical guard applies only:

```text
when policy_for(...) returns an active policy
```

while `None` means ordinary/uncontrolled repository-sync behavior remains available.

This overloads two materially different states:

```text
A. intentionally unmanaged ref
B. ref that is supposed to be governed but whose policy binding/configuration is missing, stale, unloaded, or accidentally removed
```

Those states cannot safely have the same behavior.

Why this remains blocking:

- Ruleset B identifies the **Relay Promotion App actor**, not the Python service method using that actor.
- `RepositorySyncService` uses the same contents-write GitHub App capability.
- Therefore the application-level reservation is the control that distinguishes legitimate promotion from another Relay code path using the same actor.
- If a previously governed canonical ref silently becomes `policy_for(...) == None`, the designed application-level exclusive-writer guard disappears rather than failing closed.

This violates the accepted design requirements:

```text
no implicit policy weakening
unknown/stale policy basis blocks promotion-critical behavior
RepositorySyncService must not be an alternate canonical mutation path
```

### Required rework

Revision 3 MUST introduce an explicit durable/governed canonical-policy binding state that distinguishes at least:

```text
UNMANAGED
MANAGED(exact CanonicalPromotionPolicyV1 / exact digest)
UNKNOWN_OR_INVALID
```

Acceptable minimum designs include:

1. a durable project/repository/ref policy-binding record in Relay persistence; or
2. another immutable authoritative binding whose presence/absence is itself machine-verifiable and cannot silently degrade from MANAGED to UNMANAGED through ordinary process configuration.

Required semantics:

```text
MANAGED:
  RepositorySyncService mutation of canonical ref always reserved

UNKNOWN_OR_INVALID:
  RepositorySyncService mutation of canonical/default ref fails closed
  promotion fails closed

UNMANAGED:
  repository sync retains legacy behavior
  only when the ref has been explicitly classified UNMANAGED by the governing binding mechanism
```

Removing/downgrading a MANAGED binding MUST itself require an explicit governed operation; process restart/config omission cannot implicitly unmanage the canonical ref.

The exact policy digest used by `CanonicalPromotionSubjectV1` must derive from this authoritative binding.

## 5. F006 — BLOCKING — VISIBLE_UNVERIFIED creates canonical divergence without a governed recovery contract

Revision 2 correctly refuses to write `SUCCEEDED` when:

```text
canonical ref became visible at target
but post-write control fingerprint/version no longer matches the frozen pre-write control posture
```

It records terminal:

```text
VISIBLE_UNVERIFIED
```

and says:

```text
Human reconciliation required
```

That is fail-closed as far as declaring promotion success, but the provider canonical ref has already moved.

The resulting state is materially different from an ordinary failed promotion:

```text
GitHub canonical ref -> target B
Relay promotion result -> NOT SUCCEEDED / VISIBLE_UNVERIFIED
```

Revision 2 does not define:

- whether the project/ref enters a durable quarantined/divergent state;
- whether new promotions may use B as their expected parent;
- whether repository sync remains reserved while divergence exists;
- whether a Human may later validate B without another Git mutation;
- whether recovery must instead create a new forward corrective commit;
- what exact Human authority and evidence clears the divergence;
- how an append-only audit trail represents that reconciliation.

The current relational contract makes this especially important:

```text
repository_promotion_results:
  one terminal result per promotion_id

CanonicalPromotionSubjectV1:
  expected_parent != target
```

So a terminal `VISIBLE_UNVERIFIED` cannot simply be upgraded later to `SUCCEEDED`, and the same target cannot be re-promoted as a no-op.

### Required rework

Revision 3 MUST define a deterministic quarantine/reconciliation contract.

Minimum acceptable semantics:

```text
VISIBLE_UNVERIFIED:
  marks exact project/repository/canonical_ref as DIVERGENT / QUARANTINED
  blocks ordinary promotion execution
  blocks RepositorySync mutation
  remains append-only evidence
```

Then choose and freeze one or both governed recovery paths:

### Recovery A — exact Human reconciliation of the already-visible target

Define a separate exact reconciliation subject and Human authority that:

- binds the original promotion intent/result;
- binds current canonical head == original target;
- re-verifies target identity, governance basis, required checks, current control posture, and any policy-required evidence;
- produces an append-only reconciliation record;
- clears quarantine without issuing another ref update;
- never rewrites the original `VISIBLE_UNVERIFIED` result.

### Recovery B — forward corrective history

Require a separately governed new descendant target from the current visible head, for example an authorized revert/corrective commit, and promote that exact descendant after quarantine-specific Human authority permits recovery.

If only Recovery B is supported, state that explicitly and define when quarantine is cleared.

Do not introduce force-push/backward-ref recovery.

## 6. Required clarification — exact version-consistent control observation

This is not a separate blocker if addressed with F005/F006 rework.

`GitHubSourceControlObservationV1` carries `version_id`, rules, conditions, and bypass actors. GitHub exposes current ruleset, history, and exact-version endpoints through separate requests.

Revision 3 SHOULD freeze a stable observation algorithm so a concurrent administrator edit cannot produce a hybrid snapshot.

Recommended contract:

```text
1. read ruleset history -> current version_id
2. read exact ruleset version(version_id)
3. read history again
4. require current version_id unchanged
5. normalize only exact-version payload
```

Any version drift during observation -> `UNKNOWN`; retry read-only observation or block.

Also explicitly require:

```text
Ruleset B update.update_allows_fetch_and_merge == false
```

unless implementation evidence proves that provider option cannot create an alternate update path for the governed canonical ref.

## 7. Required Revision-3 scope

Revision 3 is bounded.

Preserve all accepted directions from Revision 1 and Revision 2 except where amended.

Required amendments:

```text
RW6 — durable MANAGED / UNMANAGED / UNKNOWN canonical policy binding
RW7 — durable canonical divergence/quarantine + governed reconciliation
RW8 — version-consistent ruleset observation and exact update-rule parameters
```

No implementation, repository-setting mutation, workflow mutation, credential installation, or new Human Authority execution is authorized by this evaluation.

## 8. Authority boundary

```text
Slice 1.10:
OPEN

Design authority:
RLY-S110-DESIGN-AUTH-001 — AUTHORIZED

Composite design:
Revision 1 + Revision 2/Rework 1

Independent design evaluation:
RLY-S110-DESIGN-EVAL-002 — REVISE

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED

Repository-setting mutation:
NOT AUTHORIZED

Credential installation/permission changes:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

## 9. Next gate

The existing design authority permits this bounded design rework.

After Revision 3 is frozen:

```text
RLY-S110-DESIGN-EVAL-003

Outcome:
ACCEPT | REVISE | ESCALATE
```

**REVISE — Revision 2 resolves the original architecture defects, but canonical-policy activation and provider-visible divergence still need explicit fail-closed governance contracts before implementation may be authorized.**