# Relay — Slice 1.10 Canonical Source and Promotion Enforcement — Implementation Evaluation 001

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE / ACCEPT  
**Date:** 2026-10-25  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Evaluation ID:** `RLY-S110-IMPL-EVAL-001 — ACCEPT`  
**Evaluator:** Independent Slice 1.10 Implementation Evaluator — GPT-5.6 Sol  
**Exact historical implementation subject:** `8003170f56120640ab29eb776cc1b2ba53c66a5f`  
**Implementation authority:** `RLY-S110-IMPL-AUTH-001 — AUTHORIZED`  
**Accepted composite design:** Revisions 1–4 under `RLY-S110-DESIGN-EVAL-004 — ACCEPT` and `RLY-S110-DESIGN-ACCEPT-001 — ACCEPTED`  
**Historical exact-head CI:** `38307308578 — SUCCESS`  
**Compatibility frontier reviewed:** canonical `main` `da966f67676a227488ef216d388d405b5e383d93`  
**Current exact-head/post-promotion CI:** `40165012106 — SUCCESS`

## 1. Decision

```text
RLY-S110-IMPL-EVAL-001 — ACCEPT
```

The exact historical Slice 1.10 implementation candidate:

`8003170f56120640ab29eb776cc1b2ba53c66a5f`

conforms to the Human-accepted Slice 1.10 composite design and the bounded implementation authority `RLY-S110-IMPL-AUTH-001`.

No blocking implementation defect was found.

The later shared-file evolution reviewed at canonical `main` does not invalidate the accepted historical implementation subject.

## 2. Exact lineage and authorized surface

PASS.

The candidate is a true descendant of the Human-accepted design/implementation start:

```text
accepted design / implementation start:
bf0094aff8dfb380b24b8e15be1bc2286948dda6

historical implementation candidate:
8003170f56120640ab29eb776cc1b2ba53c66a5f

ahead:
5 commits

behind:
0

merge base:
bf0094aff8dfb380b24b8e15be1bc2286948dda6
```

The production changes are confined to the exact production surface authorized by `RLY-S110-IMPL-AUTH-001`:

```text
src/relay_engine/promotion/**
src/relay_engine/integrations/github/ruleset_verifier.py
src/relay_engine/domain/ids.py
src/relay_engine/repository_sync/models.py
src/relay_engine/repository_sync/errors.py
src/relay_engine/repository_sync/service.py
src/relay_engine/integrations/github/__init__.py
src/relay_engine/integrations/github/models.py
src/relay_engine/integrations/github/client.py
src/relay_engine/integrations/github/service.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
```

Tests changed only under the authorized `tests/unit/` and `tests/integration/` surface.

The only governance/documentation changes in the implementation lineage are the authorized implementation authority/handoff records and corresponding registry update.

No dependency, toolchain, workflow, AgentRuntime, Phase-3, or unrelated production surface was introduced by the candidate.

## 3. Exact repository-mutation authority model

PASS.

The implementation introduces explicit typed subject discriminators for:

- the existing RepositorySync subject;
- CanonicalPromotionSubjectV1;
- CanonicalPolicyBindingSubjectV1;
- CanonicalPromotionReconciliationSubjectV1.

`RepositoryMutationAuthorization` remains the single repository-mutation authority mechanism.

It requires:

- exact supported discriminated subject type;
- exact project identity;
- exact subject schema version;
- exact deterministic subject digest;
- Human actor.

Legacy RepositorySync payload compatibility is narrowly preserved only for the exact pre-discriminator RepositorySync wire shape.

Unknown or missing promotion discriminators fail validation.

This satisfies the accepted design requirement that promotion execution reuse Human repository-mutation authority rather than create a second authority system.

## 4. Canonical policy binding and quarantine semantics

PASS.

The implementation provides append-only exact binding revisions with deterministic CAS semantics.

Binding preparation:

- requires exact `HEALTHY` canonical-ref health;
- returns UNKNOWN when health/history cannot be established;
- blocks all transitions under `QUARANTINED`;
- requires exact source-control conformance before a MANAGED binding is authorizable.

Binding execution rechecks:

- health;
- exact prior binding identity/revision/digest;
- exact Human authorization.

Missing, corrupt, absent, or unreadable binding history resolves fail-closed to `UNKNOWN_OR_INVALID`, not implicit unmanaged state.

No policy-strength ordering or policy substitution algorithm is introduced.

## 5. RepositorySync fencing and canonical writer boundary

PASS.

A MANAGED canonical ref is reserved to `CanonicalPromotionService`.

RepositorySync remote mutation requires:

```text
explicit UNMANAGED binding
+
HEALTHY canonical-ref state
```

Unknown/invalid binding, quarantine, or other non-healthy state fails closed.

The static production contract proves exactly two `update_git_ref(...)` callsites:

```text
CanonicalPromotionService
RepositorySyncService
```

and both use:

```text
force=False
```

The accepted writer separation is therefore encoded rather than left as convention.

## 6. Promotion preparation and exact execution authority

PASS.

Promotion preparation distinguishes:

```text
AUTHORIZABLE
INELIGIBLE
UNKNOWN
```

from execution-time eligibility.

Preparation alone cannot mutate the repository.

Human authorization is bound to the exact promotion subject, including:

- project/repository/provider identity;
- installation state revision;
- canonical ref;
- expected parent;
- exact target commit;
- exact binding identity/revision/digest;
- promotion policy digest;
- governance-basis digest;
- exact required-check specification.

Execution reloads and revalidates the exact Human authority and all current predicates before any ref mutation.

`READY/AUTHORIZABLE != AUTHORIZED` is preserved.

## 7. Required-check and source-control verification

PASS.

Required checks are evaluated against:

- exact target SHA;
- exact check name;
- exact GitHub App identity;
- latest matching run;
- completed state;
- successful conclusion.

Missing or ambiguous check identity becomes UNKNOWN; known non-success becomes FAIL.

The Control Verifier is isolated behind a provider-neutral port.

The GitHub adapter performs GET-only requests and uses stable ruleset-version reads:

```text
history version
-> exact version read
-> current ruleset identity read
-> second history version
```

Version drift is rejected.

Conformance validates the exact accepted integrity/writer ruleset requirements, including:

- active enforcement;
- no integrity bypass;
- exactly one writer bypass actor;
- exact Promotion App identity;
- exact canonical branch conditions;
- deletion/non-fast-forward protection;
- exact required-status-check configuration;
- strict status checks;
- `update_allows_fetch_and_merge == false`.

No ruleset mutation capability is present.

## 8. Durable promotion intent, result, crash recovery, and quarantine

PASS.

Migration v6 creates exactly the four authorized append-only tables:

```text
canonical_promotion_policy_bindings
repository_promotion_intents
repository_promotion_results
repository_promotion_reconciliations
```

There is no quarantine table.

All four histories are protected against UPDATE and DELETE.

Promotion execution commits immutable intent before the non-force ref update.

Terminal outcomes are bounded to the accepted model, including:

```text
SUCCEEDED
NOT_APPLIED
CONFLICT
VISIBLE_UNVERIFIED
```

Restart handling is intent-first.

If a prior intent exists, the implementation observes current ref state before attempting any successor write and:

- returns/reconstructs exact terminal state when already terminal;
- reconciles a visible target;
- records conflict on a third head;
- records stale intent when the basis changed;
- permits only the bounded accepted retry path when the exact parent and basis remain unchanged.

A visible target that cannot be proven against the original exact basis becomes `VISIBLE_UNVERIFIED`.

Canonical health is derived only from immutable intent/result/reconciliation history.

Unresolved `VISIBLE_UNVERIFIED` history yields `QUARANTINED`.

No mutable quarantine flag exists.

## 9. Exact reconciliation

PASS.

Reconciliation:

- is available only for an exact unresolved `VISIBLE_UNVERIFIED` result;
- requires current quarantine;
- reconstructs the original binding and policy exactly;
- rejects successor-policy substitution;
- re-observes evidence against the original frozen policy/binding;
- requires exact Human reconciliation authority;
- appends one immutable reconciliation record;
- performs zero Git ref writes.

The original intent/result/authorization/binding history remains unchanged.

## 10. Historical validation

PASS.

Exact historical candidate:

`8003170f56120640ab29eb776cc1b2ba53c66a5f`

has exact-head GitHub Actions run:

`38307308578 — SUCCESS`

Observed CI steps all succeeded:

- environment synchronization;
- Ruff format;
- Ruff lint;
- Pyright;
- tests;
- build.

The historical regression suite includes explicit coverage for:

- exact writer-callsite allowlist and non-force mutation;
- GET-only Control Verifier;
- deterministic promotion subject digest;
- strict typed mutation authority;
- quarantine/unknown binding freeze;
- missing-binding fail-closed behavior;
- MANAGED RepositorySync fencing;
- competing binding CAS;
- exact ruleset conformance;
- exact required-check identity;
- intent-before-write ordering;
- restart-first recovery;
- bounded retry;
- stale basis;
- visible-unverified behavior;
- binding revision drift;
- structured Human/evaluator continuity;
- exact zero-write reconciliation;
- successor-policy substitution rejection;
- invalid original authority;
- migration-v6 exact four-table append-only contract.

Green CI is evidence; the ACCEPT disposition additionally depends on the independent semantic review above.

## 11. Compatibility review against later shared-file evolution

PASS.

The historical candidate is a true Git ancestor of current canonical main.

The dedicated Slice 1.10 production modules remain byte-identical at current `main`, including:

```text
src/relay_engine/promotion/__init__.py
src/relay_engine/promotion/errors.py
src/relay_engine/promotion/models.py
src/relay_engine/promotion/service.py
src/relay_engine/promotion/controls.py
src/relay_engine/promotion/bindings.py
src/relay_engine/promotion/reconciliation.py
src/relay_engine/integrations/github/ruleset_verifier.py
```

The promotion-facing RepositorySync and GitHub integration modules reviewed are also unchanged.

Later shared-file evolution is compatible:

### Domain IDs

The original Slice 1.10 identifiers remain unchanged. Later operational-history/adoption identifiers are additive.

### Migration v6

The complete `CANONICAL_PROMOTION_MIGRATION` definition is byte-for-byte identical between the historical candidate and current main.

Later migrations append new tables/indexes/triggers rather than rewriting the Slice 1.10 migration.

### Persistence store

All promotion-specific persistence functions reviewed are text-identical between the historical candidate and current main, including authorization, binding, intent, result, unresolved-intent, and reconciliation operations.

### Persistence exports

The Slice 1.10 persistence exports remain present; later operational-history APIs are additive.

### Regression preservation

Every original test function in the changed promotion-binding, promotion-service, promotion-persistence, and RepositorySync regression files remains present at current main.

Current canonical main at:

`da966f67676a227488ef216d388d405b5e383d93`

also passes post-promotion CI:

`40165012106 — SUCCESS`.

This compatibility review does **not** redefine the implementation subject. The accepted technical subject remains exact historical candidate `8003170f...`.

It establishes only that later accepted shared-file evolution has not invalidated the Slice 1.10 implementation contract.

## 12. Final disposition

```text
RLY-S110-IMPL-EVAL-001 — ACCEPT

Exact Slice 1.10 implementation subject:
8003170f56120640ab29eb776cc1b2ba53c66a5f

Historical implementation:
INDEPENDENTLY ACCEPTED

Compatibility with current canonical main:
PASS

Human top-level Slice 1.10 technical acceptance:
ELIGIBLE / NOT YET GRANTED

Slice 1.10 closure authority:
NOT YET ELIGIBLE UNTIL HUMAN TECHNICAL ACCEPTANCE

Slice 1.10:
OPEN

Phase 3:
OPEN

Slice 3.1:
NOT OPEN / NOT AUTHORIZED

Phase 3 execution:
GATED

Real-project execution:
NOT AUTHORIZED
```

## 13. Next legitimate gate

The next legitimate gate is explicit Human technical acceptance of exact historical implementation subject:

`8003170f56120640ab29eb776cc1b2ba53c66a5f`

under this independent evaluation.

Only after that Human acceptance is durably recorded should top-level Slice 1.10 finalization/closure authority be considered.

**ACCEPT — SLICE 1.10 IMPLEMENTATION IS TECHNICALLY ELIGIBLE FOR HUMAN ACCEPTANCE.**
