# Slice 1.10 — Independent Design Evaluation 001

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Evaluation ID:** `RLY-S110-DESIGN-EVAL-001`  
**Outcome:** `REVISE`  
**Design authority:** `RLY-S110-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact evaluated design subject:** `f9141f6f44927f2a13b85cce8ffd4501db0b183d`  
**Exact design-baseline authority head:** `dac1557adeca9a1928d442a6f4aea809d8b33a10`  
**Evaluator:** GPT-5.6 Sol — independent design reviewer

## 1. Decision

```text
REVISE
```

Revision 1 contains a strong minimum-scope architecture and preserves Relay's core authority separation, but four blocking gaps prevent design acceptance. They are design-contract defects, not implementation defects.

Exact-head CI for the evaluated design subject:

```text
38197601396 — SUCCESS
```

Passing CI is engineering evidence only and does not cure the findings below.

## 2. Passing design properties

The independent review accepts the following architectural directions as sound and they SHOULD be preserved in rework:

- canonical registry pointers remain distinct from the canonical Git ref;
- exact repository/ref/parent/target subject binding;
- full-SHA target and expected-parent identity;
- reuse of existing `RepositoryMutationAuthorization` rather than creating a second Human-authority system;
- automated executor refusal to infer executable authority from prose;
- exact required-check identity and target-SHA binding;
- non-force ref updates only;
- no rebase/squash/cherry-pick recreation during promotion;
- no self-administering promotion executor;
- GitHub adapter separated from provider-neutral promotion semantics;
- no generic property engine or generic SCM abstraction;
- one bounded migration for append-only promotion intent/result evidence is reasonable in principle;
- rollback by new forward history rather than destructive ref rewind;
- live Relay dogfood before closure.

## 3. F001 — BLOCKING — required ruleset bypass posture is not observable with the permitted App capability

Revision 1 requires:

```text
Ruleset A:
  no bypass actors

Ruleset B:
  exact Relay GitHub App is the sole bypass actor
  no Human/team/admin-role bypass entries

RELAY_SOURCE_CONTROL_ENFORCED:
  FAIL/UNKNOWN if either bypass posture cannot be proved
```

At the same time D08/D10 deliberately deny the Relay App repository-rules / administration mutation capability.

Current GitHub REST semantics create a contradiction:

- active branch rules and repository-ruleset metadata can be read with Metadata:read;
- however GitHub documents that the `bypass_actors` property is returned only when the caller has **write access to the ruleset**.

Therefore the proposed least-privileged promotion App cannot prove the exact bypass list required by D09/D19. Absence of a returned bypass list is ambiguous, not proof of an empty list.

Under Revision 1's own fail-closed semantics:

```text
bypass posture unverifiable
    -> RELAY_SOURCE_CONTROL_ENFORCED = UNKNOWN
    -> promotion blocked
```

Thus the design as written cannot reach ELIGIBLE while preserving its stated permission boundary.

### Required rework

Revision 2 MUST define a machine-verifiable bypass-posture evidence path without giving the promotion executor authority to mutate its own guardrails.

Acceptable solution classes include:

1. a separately isolated control-verifier credential/actor with sufficient GitHub access to observe `bypass_actors`, used by code that exposes no mutation endpoint; or
2. a separately authorized exact source-control configuration attestation produced by an administrative verifier and consumed with exact ruleset IDs/versions/digests/freshness; or
3. another concrete mechanism that can unambiguously prove the required bypass posture.

The rework MUST NOT:

- silently drop bypass verification;
- treat redacted/missing `bypass_actors` as empty;
- give the promotion executor ruleset-administration mutation power merely for convenience.

External platform evidence:

```text
https://docs.github.com/en/rest/repos/rules
```

## 4. F002 — BLOCKING — persisted intent does not provide restart recovery after a successful remote write

D14 justifies `repository_promotion_intents` specifically for crash/reconciliation safety.

But D15 begins execution by:

```text
1. load intent
2. re-run promotion preparation
3. require same subject digest and ELIGIBLE
...
7. require canonical ref == expected parent
```

Consider the required failure window:

```text
intent persisted
remote PATCH succeeds
canonical ref == target
process crashes before repository_promotion_results insert
```

On restart there is no success result. A normal fresh preparation sees that the canonical ref no longer equals `expected_parent`; Revision 1 therefore classifies the subject stale before it defines a durable success-recovery path.

The same-call `GitHubRefUpdateIndeterminate` reconciliation in D16 does not solve a process crash/restart after the remote side effect.

### Required rework

Define explicit restart reconciliation before ordinary stale-parent rejection for an existing persisted intent with no result.

At minimum:

```text
head == target:
  reverify target identity, authorization subject, applicable controls/check evidence,
  and exact intent;
  append one reconciled immutable success result;
  do not issue a second ref mutation

head == expected parent:
  resume ordinary fresh eligibility/revalidation path

head == third commit:
  conflict/indeterminate;
  no success result;
  no blind retry
```

Specify uniqueness/idempotency constraints and add a crash-after-visible-PATCH-before-result test.

## 5. F003 — BLOCKING — exact Human-acceptance continuity to a later finalization/promotion target is underspecified

Revision 1 makes `RELAY_HUMAN_ACCEPTED` mandatory for v1 promotion.

The accepted Slice 1.8 semantics define:

```text
RELAY_HUMAN_ACCEPTED:
an explicit Human acceptance authority record binds to the exact accepted subject
```

Revision 1 also correctly states that:

```text
accepted technical candidate != necessarily the final promotion target
```

because finalization/closure can produce a later exact commit.

However D22 only says the service consumes accepted structured evaluation/Human-acceptance records. It does not define the causal contract that allows an exact Human acceptance of technical candidate A to contribute to promotion eligibility for later closure/finalization target B without falsely pretending that the Human accepted B directly.

This is not hypothetical. Relay's established closure pattern preserves:

```text
Human technical acceptance -> accepted technical candidate
closure evaluation -> closure-ready candidate
authorized closed-state bookkeeping -> later final canonical target
```

Those statement classes are intentionally distinct.

Without an explicit causal model, implementation is forced into one of two invalid choices:

- mark `RELAY_HUMAN_ACCEPTED` PASS for the later target without an exact acceptance record for that target; or
- make ordinary finalization-derived targets permanently ineligible.

### Required rework

Define the exact structured promotion-basis chain.

Revision 2 MUST state, for each required property, which exact subject it binds and how continuity to the promotion target is proven.

A likely valid model is:

```text
technical Human acceptance
  -> exact accepted technical subject

closure/finalization evaluation + authority
  -> exact authorized transformation/lineage to promotion target

RELAY_CONTROL_CONTINUITY_VERIFIED
  -> proves no authority gap from accepted subject to target

RELAY_PROMOTION_AUTHORIZED
  -> exact current mutation authority for the final target
```

`RELAY_HUMAN_ACCEPTED` must remain truthful about the subject actually accepted. Do not redefine it to mean promotion authorization.

If automated v1 cannot consume the current closure/finalization record representation without parsing prose, Revision 2 must define the minimum structured adapter/input required or explicitly require a new exact Human decision at the appropriate statement-class boundary. It must not infer semantics from Markdown.

## 6. F004 — BLOCKING — canonical writer exclusivity conflicts with the existing RepositorySyncService write path

Revision 1 states:

```text
Ruleset B makes the Relay App the only canonical-ref writer
```

and the acceptance matrix expects canonical-source enforcement rather than convention.

However accepted Slice 1.3 production behavior already uses the same Relay GitHub App to:

```text
mint a repository-scoped contents:write token
create a commit
PATCH the provider default branch with force=false
```

`RepositorySyncService.execute_repository_sync()` therefore remains a second production code path capable of attempting mutation of the same default/canonical branch using the same App identity.

Ruleset B distinguishes actor identity, not which Relay service method is calling through that App.

Ruleset A's required check may cause ordinary repository-sync commits to be rejected, but relying on incidental status-check failure is not an explicit canonical-writer boundary, and it conflicts with D32's statement that repository synchronization behavior remains unchanged.

### Required rework

Revision 2 MUST explicitly define the interaction between repository synchronization and an enforced canonical ref.

At minimum, when a canonical-promotion policy applies to a repository/ref:

```text
RepositorySyncService must not be an alternate canonical-ref mutation path
```

Valid approaches include a deterministic fail-closed guard that rejects sync mutation of the governed canonical ref while preserving noncanonical/uncontrolled sync semantics.

The design must then correct D32: canonical-ref sync behavior is intentionally narrowed by Slice 1.10; only unaffected repository-sync semantics remain backward compatible.

Add negative tests proving:

- a repository-sync authorization cannot mutate an enforced canonical ref;
- a repository-sync authorization cannot be reused as promotion authority;
- only the promotion service's exact subject/authority path may request canonical promotion.

## 7. Nonblocking review observations

These are not independent blockers once F001–F004 are corrected:

1. D07 should define deterministic selection of the current check run when reruns produce multiple check records, preferably by a provider operation with explicit latest semantics plus exact app/name/SHA filtering.
2. D09 should use exact GitHub API vocabulary for ruleset bypass mode in the adapter contract rather than the prose phrase `direct update permitted`.
3. The migration design should freeze uniqueness/index constraints for one intent/result per `promotion_id` and the exact idempotency lookup key during rework.

## 8. Required Revision-2 scope

Revision 2 is bounded to the design defects above.

Preserve Revision 1 wherever not amended.

Required amendments:

```text
RW1 — observable source-control bypass posture without self-administering executor
RW2 — restart reconciliation after visible remote success and pre-result crash
RW3 — exact acceptance/control-continuity model from accepted subject to final target
RW4 — exclusive canonical mutation boundary versus RepositorySyncService
RW5 — deterministic check-rerun selection and promotion-intent/result idempotency details
```

No implementation, ruleset mutation, workflow mutation, or new Human Authority semantics are authorized by this evaluation.

## 9. Authority boundary

```text
Slice 1.10:
OPEN

Design authority:
RLY-S110-DESIGN-AUTH-001 — AUTHORIZED

Design Revision 1:
f9141f6f44927f2a13b85cce8ffd4501db0b183d

Independent design evaluation:
RLY-S110-DESIGN-EVAL-001 — REVISE

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED

Repository-setting mutation:
NOT AUTHORIZED

Slice 2.2–2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

## 10. Next gate

The existing design authority permits bounded design rework addressing this evaluation.

After Revision 2 is frozen, stop for a new independent design evaluation:

```text
RLY-S110-DESIGN-EVAL-002

Outcome:
ACCEPT | REVISE | ESCALATE
```

**REVISE — the architecture is promising, but canonical promotion is not yet provably closed under the actual GitHub observation and Relay write-path model.**