# Slice 1.10 — Canonical Source and Promotion Enforcement — Design Revision 3 / Rework 2

**Document class:** Lockable design rework record  
**Status:** PROPOSED FOR INDEPENDENT DESIGN RE-REVIEW  
**Date:** 2026-10-12  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Opening:** `RLY-S110-OPEN-001 — OPEN`  
**Design authority:** `RLY-S110-DESIGN-AUTH-001 — AUTHORIZED`  
**Revision 1:** `f9141f6f44927f2a13b85cce8ffd4501db0b183d`  
**Revision 2 / Rework 1:** `6b7f69d69da90879fd536b2edbbaad6d6f3da8c7`  
**Round-2 review:** `RLY-S110-DESIGN-EVAL-002 — REVISE`  
**Round-2 evaluation record:** `9881d72911d2ce2e5aad66c90881ecba3255b8b7`  
**Implementation authorization:** NOT GRANTED

---

## 1. Rework contract

This document is a bounded successor/addendum to Revision 1 and Revision 2.

Revision 1 + Revision 2 remain authoritative wherever this document does not explicitly amend them.

Where this document conflicts with an earlier design statement, Revision 3 controls.

Revision 3 resolves:

```text
F005 — canonical policy activation/reservation was not durably fail-closed
F006 — VISIBLE_UNVERIFIED lacked a governed quarantine/recovery contract
```

and freezes the required ruleset-observation clarification:

```text
RW8 — version-consistent exact ruleset observation
      + update.update_allows_fetch_and_merge == false
```

No implementation or repository-setting mutation is authorized.

---

## 2. Revision-3 summary

Revision 3 adds three bounded contracts:

```text
RW6  Durable canonical-policy binding state
RW7  Durable canonical divergence/quarantine + exact Human reconciliation
RW8  Version-consistent source-control observation
```

The core resulting safety rule is:

```text
unknown binding != unmanaged
visible but unverifiable canonical movement != successful promotion
quarantine cannot be escaped by policy removal or repository sync
```

---

## 3. RW6 — Durable canonical-policy binding resolves F005

### 3.1 Process configuration is no longer authority

Revision 2's optional provider:

```text
policy_for(...) -> CanonicalPromotionPolicyV1 | None
```

is superseded.

`None` MUST NOT mean 'unmanaged'.

Canonical-ref governance state becomes durable Relay control-plane state.

### 3.2 Binding state vocabulary

Add:

```text
CanonicalPromotionPolicyBindingState

UNMANAGED
MANAGED
```

`UNKNOWN_OR_INVALID` is a derived resolution state, not a persisted Human choice.

Resolution vocabulary:

```text
CanonicalPromotionPolicyBindingResolution

UNMANAGED
MANAGED
UNKNOWN_OR_INVALID
```

Meanings:

```text
UNMANAGED:
  an explicit current durable binding revision says this exact repository/ref
  is intentionally outside canonical-promotion enforcement

MANAGED:
  an explicit current durable binding revision binds this exact repository/ref
  to an exact CanonicalPromotionPolicyV1 and digest

UNKNOWN_OR_INVALID:
  no durable binding exists, or the binding chain/payload/digest is invalid,
  ambiguous, unreadable, or cannot be proved current
```

**Absence is UNKNOWN_OR_INVALID, never UNMANAGED.**

### 3.3 Durable binding record

Add immutable append-only:

```text
CanonicalPromotionPolicyBindingV1

binding_id
schema_version = 1
project_id
repository: RepositoryRef
canonical_ref
revision >= 1
state: UNMANAGED | MANAGED
policy: CanonicalPromotionPolicyV1 | null
policy_digest: sha256 | null
authorization_id
supersedes_binding_id | null
bound_at
```

Validation:

```text
UNMANAGED:
  policy == null
  policy_digest == null

MANAGED:
  policy present
  policy_digest == canonical digest(policy)
  policy canonical branch matches canonical_ref

revision == 1:
  supersedes_binding_id == null

revision > 1:
  supersedes_binding_id references exact prior current binding
```

Binding rows are immutable and linearly revisioned per exact:

```text
(project_id, repository, canonical_ref)
```

### 3.4 Exact Human authority for binding transitions

Reuse the existing exact HUMAN `RepositoryMutationAuthorization` envelope.

Its subject union becomes:

```text
RepositorySyncSubjectV1
CanonicalPromotionSubjectV1
CanonicalPolicyBindingSubjectV1
CanonicalPromotionReconciliationSubjectV1
```

No new Human Authority semantics are introduced.

`CanonicalPolicyBindingSubjectV1`:

```text
schema_version = 1
project_id
repository
canonical_ref

expected_current_binding_id | null
expected_current_revision
expected_current_binding_digest | null

target_revision
target_state: UNMANAGED | MANAGED
target_policy | null
target_policy_digest | null
```

Canonical subject digest uses sorted compact JSON as with other exact repository-mutation subjects.

Rules:

- first binding requires `expected_current_revision == 0` and null expected binding identity;
- later transitions bind the exact current binding ID/revision/digest;
- `target_revision == expected_current_revision + 1`;
- HUMAN actor required;
- binding authorization mutates Relay control-plane persistence only;
- it does not mutate GitHub, rulesets, refs, or workflow settings.

### 3.5 Binding transition service

`prepare_policy_binding_transition(...)` is read-only.

It returns:

```text
AUTHORIZABLE
INELIGIBLE
UNKNOWN
```

For target `MANAGED`, preparation MUST additionally prove:

- exact repository/ref identity;
- exact target policy digest;
- Control Verifier can observe the required rulesets;
- current source-control posture is conformant to the target policy;
- no unresolved canonical quarantine exists.

For target `UNMANAGED`, preparation MUST prove:

- exact current binding chain is valid;
- no unresolved canonical quarantine exists.

An explicit MANAGED -> UNMANAGED downgrade is therefore a separate exact Human decision; it cannot occur through process/config omission.

`authorize_policy_binding_transition(...)` persists exact Human `RepositoryMutationAuthorization<CanonicalPolicyBindingSubjectV1>`.

`execute_policy_binding_transition(...)`:

```text
BEGIN IMMEDIATE
load exact current binding
require exact expected current identity/revision/digest
load exact binding authorization
require target subject exact
insert immutable next binding row
COMMIT
```

No remote call occurs inside the transaction.

### 3.6 Durable store and provider

Replace the optional configuration provider with:

```text
CanonicalPromotionPolicyBindingStore

resolve(project_id, repository, ref_name)
  -> CanonicalPromotionPolicyBindingResolution
```

`CanonicalPromotionService` and `RepositorySyncService` MUST both read this durable store.

Neither service accepts caller-supplied policy state.

No constructor may default `UNKNOWN_OR_INVALID` to `UNMANAGED`.

### 3.7 RepositorySync behavior

For a remote repository mutation request:

```text
binding == MANAGED:
  canonical ref mutation RESERVED
  raise RepositorySyncCanonicalRefReserved

binding == UNKNOWN_OR_INVALID:
  mutation BLOCKED
  raise RepositorySyncCanonicalPolicyUnknown

binding == UNMANAGED:
  legacy repository-sync mutation behavior allowed
```

Read-only CURRENT/no-op recognition MAY remain available in all three states because it performs no remote mutation.

### 3.8 Promotion behavior

```text
binding == MANAGED:
  policy is the exact durable bound policy
  promotion subject includes binding_id + binding_revision + binding_digest + policy_digest

binding == UNMANAGED:
  CanonicalPromotionService returns INELIGIBLE(CANONICAL_REF_UNMANAGED)

binding == UNKNOWN_OR_INVALID:
  returns UNKNOWN
  no Human promotion authority may be issued
```

Changing the binding or policy revision stales any previously issued exact promotion authority.

### 3.9 Bootstrap / legacy projects

Revision 3 intentionally tightens backward compatibility.

After Slice 1.10 implementation is active:

```text
no binding record
  != legacy-unmanaged
  == UNKNOWN_OR_INVALID
```

Remote repository-sync mutation is blocked until the Human explicitly classifies the exact repository/ref as:

```text
UNMANAGED
or
MANAGED(exact policy)
```

This one-time explicit classification is required because silent legacy fallback would recreate F005.

### 3.10 F005 disposition

F005 is resolved because policy removal/configuration loss can no longer silently unreserve a canonical ref.

---

## 4. RW7 — Canonical divergence/quarantine resolves F006

### 4.1 Canonical health vocabulary

Add derived:

```text
CanonicalRefHealth

HEALTHY
QUARANTINED
UNKNOWN
```

`QUARANTINED` is durable-by-evidence: it is derived from immutable promotion result/reconciliation history, not from an in-memory flag.

### 4.2 Quarantine trigger

An exact:

```text
RepositoryPromotionResultV1.outcome == VISIBLE_UNVERIFIED
```

for `(project_id, repository, canonical_ref)` creates unresolved quarantine unless an accepted reconciliation record exists for that exact promotion result.

Additionally, a promotion result whose reason proves an unexpected third canonical head MAY also quarantine the ref under the same mechanism; implementation must not weaken the mandatory `VISIBLE_UNVERIFIED` trigger.

### 4.3 Quarantine derivation

```text
QUARANTINED:
  exists VISIBLE_UNVERIFIED result R
  and no accepted CanonicalPromotionReconciliationV1 references R

HEALTHY:
  no unresolved quarantine result exists

UNKNOWN:
  result/reconciliation history is unreadable, ambiguous, or integrity-invalid
```

`UNKNOWN` is fail-closed.

### 4.4 Quarantine effects

When health is `QUARANTINED` or `UNKNOWN`:

```text
ordinary canonical promotion: BLOCKED
RepositorySync remote mutation: BLOCKED
MANAGED -> UNMANAGED binding downgrade: BLOCKED
automatic retry of prior promotion: BLOCKED
force/backward ref recovery: FORBIDDEN
```

A MANAGED -> MANAGED policy revision MAY be prepared during quarantine only when needed to re-establish conformant controls for reconciliation; it does not clear quarantine.

### 4.5 V1 recovery choice

Slice 1.10 v1 supports **Recovery A only**:

```text
exact Human reconciliation of the already-visible target
```

V1 does not support automatic forward corrective promotion while quarantined.

If the already-visible target cannot be reconciled under current valid policy/controls/governance basis, the ref remains quarantined and requires a separately designed future break-glass or corrective-history authority path.

No destructive rollback or force update is introduced.

### 4.6 Read-only reconciliation preparation

Add:

```text
prepare_canonical_reconciliation(...)
```

It accepts one exact unresolved `VISIBLE_UNVERIFIED` promotion result and returns:

```text
RECONCILABLE
INELIGIBLE
UNKNOWN
```

`RECONCILABLE` requires all of:

```text
exact unresolved VISIBLE_UNVERIFIED result exists
current canonical head == original promotion target
current binding == MANAGED
current binding/policy chain valid
original promotion intent + authorization + result integrity valid
target commit exists exactly
required checks for target are current under current policy
structured governance/control-continuity basis is current
full current source-control observation is conformant
no conflicting reconciliation exists
```

Preparation computes:

```text
CanonicalPromotionReconciliationSubjectV1
```

### 4.7 Exact reconciliation subject

`CanonicalPromotionReconciliationSubjectV1`:

```text
schema_version = 1
project_id
repository
canonical_ref
promotion_id
visible_unverified_result_digest
original_subject_digest
original_target_commit
expected_visible_head
current_binding_id
current_binding_revision
current_binding_digest
current_policy_digest
governance_basis_digest
required_check_observation_digest
source_control_observation_digest
```

`expected_visible_head` MUST equal the original target.

### 4.8 Human reconciliation authority

`authorize_canonical_reconciliation(...)`:

- accepts only exact `RECONCILABLE` preparation;
- requires HUMAN actor;
- persists immutable `RepositoryMutationAuthorization<CanonicalPromotionReconciliationSubjectV1>`;
- performs no Git mutation;
- does not rewrite the original result.

### 4.9 Reconciliation execution

`execute_canonical_reconciliation(...)` re-runs every live reconciliation predicate.

Required sequence:

```text
1. load unresolved quarantine result + original intent
2. load exact reconciliation authority
3. re-resolve current MANAGED binding
4. require current head == original target
5. reverify governance basis and target checks
6. obtain stable version-consistent source-control observation
7. require freshly recomputed reconciliation subject == authorized subject
8. BEGIN IMMEDIATE
9. require no reconciliation already exists
10. append immutable CanonicalPromotionReconciliationV1
11. COMMIT
```

No Git ref update occurs.

### 4.10 Reconciliation record

Add append-only:

```text
CanonicalPromotionReconciliationV1

reconciliation_id
schema_version = 1
project_id
repository
canonical_ref
promotion_id
original_visible_unverified_result_digest
target_commit
authorization_id
reconciliation_subject_digest
binding_id
binding_revision
policy_digest
governance_basis_digest
source_control_observation_digest
reconciled_at
reconciled_by
outcome = RECONCILED
```

The original `VISIBLE_UNVERIFIED` result remains immutable.

Effective canonical promotion evidence becomes:

```text
SUCCEEDED RepositoryPromotionResultV1

OR

VISIBLE_UNVERIFIED RepositoryPromotionResultV1
+
accepted CanonicalPromotionReconciliationV1
```

This pair proves that the already-visible exact target was later reconciled under explicit Human authority without pretending the original attempt succeeded cleanly.

### 4.11 Future promotion after reconciliation

After accepted reconciliation:

```text
health -> HEALTHY
current canonical head == reconciled target
future exact promotions may use that target as expected_parent
```

No no-op re-promotion of the same target is required.

### 4.12 Idempotency

```text
one accepted reconciliation per promotion_id
same reconciliation_id + stored record -> return exact record
same promotion_id + existing accepted reconciliation -> return existing reconciliation
no second authority execution mutates Git
```

### 4.13 F006 disposition

F006 is resolved because provider-visible but unverified canonical movement becomes a durable quarantine state with one explicit v1 exit: exact Human-authorized reconciliation of the already-visible target.

---

## 5. RW8 — Version-consistent ruleset observation

### 5.1 Required invariant

A promotion-critical source-control observation MUST correspond to stable exact ruleset versions.

Relay MUST NOT combine fields from multiple concurrent ruleset versions into one apparent observation.

### 5.2 Stable-version read algorithm

For each required or additional applicable ruleset ID:

```text
1. GET ruleset history; capture current/latest version_id V1
2. GET exact ruleset version V1
3. GET current ruleset metadata
4. GET ruleset history again; capture current/latest version_id V2
5. require V1 == V2
6. require exact-version state.id == expected ruleset_id
7. require current ruleset identity/source/target agrees with exact-version state
8. normalize only the exact-version state for conditions/rules/bypass actors
```

If any request fails, version changes, identity disagrees, or fields required for conformance are unavailable:

```text
observation = UNKNOWN
```

The caller may perform another bounded read-only observation attempt; it MUST NOT synthesize stability.

### 5.3 Observation fingerprint

`GitHubSourceControlObservationV1` fingerprint includes exact:

```text
ruleset_id
version_id
updated_at
enforcement
normalized conditions
normalized rules
normalized bypass actors
```

for every policy-required/applicable ruleset.

Pre-write intent stores that exact fingerprint.

Post-write verification requires the same fingerprint for a clean `SUCCEEDED` result.

### 5.4 Exact writer update rule

Ruleset B conformance additionally requires:

```text
rule.type == update
rule.parameters.update_allows_fetch_and_merge == false
```

Any missing/true/ambiguous value is nonconformant or UNKNOWN according to whether a violation is positively established.

This prevents an alternate fetch-and-merge update permission from weakening the exact writer contract.

### 5.5 Ruleset A remains non-bypassable

Revision 2 remains unchanged:

```text
Ruleset A bypass_actors == ()
```

Ruleset B remains:

```text
exact one Integration actor
actor_id == Relay Promotion App ID
bypass_mode == always
update_allows_fetch_and_merge == false
```

---

## 6. Migration v6 — revised exact scope

Revision 1/2 migration-v6 scope is superseded.

One deterministic migration v6 is still sufficient, now with exactly four append-only tables:

```text
canonical_promotion_policy_bindings
repository_promotion_intents
repository_promotion_results
repository_promotion_reconciliations
```

### 6.1 `canonical_promotion_policy_bindings`

```text
binding_id TEXT PRIMARY KEY
project_id TEXT NOT NULL
repository_id TEXT NOT NULL
canonical_ref TEXT NOT NULL
revision INTEGER NOT NULL CHECK (revision >= 1)
state TEXT NOT NULL CHECK state IN ('UNMANAGED','MANAGED')
policy_digest TEXT NULL
authorization_id TEXT NOT NULL
supersedes_binding_id TEXT NULL
bound_at TEXT NOT NULL
payload_json TEXT NOT NULL

UNIQUE(project_id, repository_id, canonical_ref, revision)
UNIQUE(supersedes_binding_id) WHERE supersedes_binding_id IS NOT NULL
```

Indexes support latest binding lookup by exact project/repository/ref.

UPDATE and DELETE triggers reject mutation.

### 6.2 `repository_promotion_intents`

Revision 2 constraints preserved.

### 6.3 `repository_promotion_results`

Revision 2 constraints preserved.

### 6.4 `repository_promotion_reconciliations`

```text
reconciliation_id TEXT PRIMARY KEY
promotion_id TEXT NOT NULL
project_id TEXT NOT NULL
repository_id TEXT NOT NULL
canonical_ref TEXT NOT NULL
target_sha TEXT NOT NULL
authorization_id TEXT NOT NULL
reconciled_at TEXT NOT NULL
payload_json TEXT NOT NULL

UNIQUE(promotion_id)
```

UPDATE and DELETE triggers reject mutation.

No mutable quarantine table is added.

Quarantine is derived from immutable result + reconciliation history.

---

## 7. Revised authority subject union

Revision 3 freezes the complete v1 exact subject union consumed by `RepositoryMutationAuthorization`:

```text
RepositorySyncSubjectV1
CanonicalPromotionSubjectV1
CanonicalPolicyBindingSubjectV1
CanonicalPromotionReconciliationSubjectV1
```

Each subject has its own schema tag/type discriminator in persisted payload JSON.

Loaders MUST reject unknown/missing/ambiguous subject type rather than guessing from fields.

Old `RepositorySyncSubjectV1` authorizations remain readable.

---

## 8. Revised promotion subject

`CanonicalPromotionSubjectV1` now binds:

```text
schema_version
project/repository/provider identity
installation_id / provider IDs / expected state_revision
canonical_ref
expected_parent
target_commit

binding_id
binding_revision
binding_digest
promotion_policy_digest
governance_basis_digest
required_check_specs
```

Binding revision/digest change invalidates authority even when policy contents happen to serialize identically.

---

## 9. Revised runtime decision table

### RepositorySyncService remote mutation

```text
binding UNMANAGED + health HEALTHY:
  allowed under existing exact sync authority

binding MANAGED:
  blocked for canonical ref

binding UNKNOWN_OR_INVALID:
  blocked

health QUARANTINED or UNKNOWN:
  blocked regardless of binding
```

### CanonicalPromotionService

```text
binding MANAGED + health HEALTHY:
  authorizability/promotion path available

binding UNMANAGED:
  INELIGIBLE

binding UNKNOWN_OR_INVALID:
  UNKNOWN / blocked

health QUARANTINED or UNKNOWN:
  ordinary promotion blocked
```

### Policy-binding transition

```text
health HEALTHY:
  exact Human-authorized UNMANAGED<->MANAGED or MANAGED policy revision allowed

health QUARANTINED:
  MANAGED->UNMANAGED forbidden
  MANAGED->MANAGED allowed only through exact authority and only to support restored conformance
```

### Reconciliation

```text
health QUARANTINED:
  exact Human reconciliation path only

health HEALTHY:
  no reconciliation needed
```

---

## 10. Revised implementation change surface

Revision 1/2 implementation surfaces remain bounded with these additions:

```text
src/relay_engine/promotion/
    bindings.py        # durable binding models/service/store port
    reconciliation.py  # quarantine/reconciliation models/service
```

Existing bounded changes additionally include:

```text
src/relay_engine/domain/ids.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
src/relay_engine/repository_sync/errors.py
src/relay_engine/repository_sync/service.py
src/relay_engine/integrations/github/ruleset_verifier.py
```

No workflow mutation, ruleset mutation endpoint, background worker, queue, or generic SCM abstraction is added.

Materially broader production scope requires escalation.

---

## 11. Required Revision-3 tests

### RW6 — policy binding

```text
no binding -> UNKNOWN_OR_INVALID
no binding -> sync remote mutation blocked
explicit UNMANAGED -> legacy sync mutation allowed
explicit MANAGED -> sync canonical mutation blocked
MANAGED promotion subject binds exact binding id/revision/digest
binding revision change stales promotion authority
MANAGED -> UNMANAGED requires exact Human binding authority
config omission cannot unmanage ref
binding-chain corruption -> UNKNOWN_OR_INVALID
binding transition CAS race -> one winner / one conflict
old sync RepositoryMutationAuthorization payload remains loadable
subject union unknown discriminator -> integrity error
```

### RW7 — quarantine/reconciliation

```text
VISIBLE_UNVERIFIED -> QUARANTINED
QUARANTINED blocks ordinary promotion
QUARANTINED blocks RepositorySync mutation
QUARANTINED blocks MANAGED->UNMANAGED downgrade
reconciliation prep requires current head == original target
reconciliation prep requires MANAGED current binding
reconciliation requires current checks + stable conformant controls
reconciliation authority exact subject required
reconciliation execution performs zero Git writes
original VISIBLE_UNVERIFIED remains immutable
accepted reconciliation -> HEALTHY
reconciled target may be expected_parent of future promotion
duplicate reconciliation returns exact stored record
unreconcilable target stays quarantined
```

### RW8 — stable rulesets

```text
history V1 == history V2 -> exact-version observation accepted
history V1 != V2 -> UNKNOWN
exact-version/current identity mismatch -> UNKNOWN
missing bypass actors -> UNKNOWN
writer update_allows_fetch_and_merge true -> nonconformant
writer update_allows_fetch_and_merge false -> eligible for conformance
pre/post exact ruleset fingerprint drift -> VISIBLE_UNVERIFIED
```

---

## 12. Revised dogfood sequence

Slice 1.10 closure on `cschrupp/relay` must prove the complete lifecycle:

```text
1. exact Control Verifier capability available and separated
2. Ruleset A and Ruleset B configured under separate authority
3. create exact MANAGED binding for refs/heads/main under Human binding authority
4. durable binding resolves MANAGED with exact policy digest
5. RepositorySyncService cannot mutate main
6. stable ruleset observation PASS
7. target without exact successful quality check blocked
8. stale parent blocked
9. exact promotion becomes AUTHORIZABLE
10. exact HUMAN promotion authority persisted
11. execution ELIGIBLE
12. immutable intent persisted
13. non-force Promotion-App ref update succeeds
14. post-write stable control fingerprint matches
15. SUCCEEDED result durable
16. exact retry idempotent
```

Separate fault-injection dogfood must demonstrate:

```text
visible target + post-write control-version drift
  -> VISIBLE_UNVERIFIED
  -> QUARANTINED
  -> sync/promotion blocked
  -> exact Human reconciliation
  -> HEALTHY
  -> no additional Git ref update during reconciliation
```

Repository-setting, credential, and live dogfood mutations remain subject to separate authority.

---

## 13. Explicit non-authority preserved

Revision 3 does not authorize:

- implementation;
- schema migration execution;
- creation or installation of Promotion App / Control Verifier credentials;
- permission changes;
- ruleset creation/update/delete;
- workflow changes;
- policy-binding execution on a live project;
- canonical promotion execution;
- quarantine reconciliation execution;
- force push / history rewrite;
- break-glass recovery;
- Role Contracts / Slice 2.2;
- Context/Work Packets / Slice 2.3;
- Workspace Authority / Slice 2.4;
- Phase 3;
- real-project agent execution.

---

## 14. Composite Revision-3 acceptance matrix

Independent re-review must require:

```text
[ ] F001 remains resolved: full bypass posture observable through isolated verifier
[ ] F002 remains resolved: crash/restart reconciliation before stale-parent rejection
[ ] F003 remains resolved: exact Human acceptance subjects + control continuity
[ ] F004 remains resolved: RepositorySync cannot serve as canonical mutation path
[ ] F005 resolved: missing policy binding is UNKNOWN, never implicit UNMANAGED
[ ] MANAGED->UNMANAGED requires exact Human authority
[ ] policy/binding revision is exact promotion-authority basis
[ ] F006 resolved: VISIBLE_UNVERIFIED creates durable quarantine
[ ] quarantine blocks sync + ordinary promotion + downgrade escape
[ ] exact Human reconciliation clears quarantine without Git rewrite
[ ] original VISIBLE_UNVERIFIED evidence remains immutable
[ ] no force/backward-ref recovery introduced
[ ] ruleset observation is exact-version stable
[ ] writer rule requires update_allows_fetch_and_merge == false
[ ] no SQLite transaction spans remote GitHub I/O
[ ] migration remains bounded and append-only
[ ] no new Human Authority semantics introduced
[ ] old repository-sync authorizations remain readable
[ ] implementation/ruleset/workflow/credential mutations remain unauthorized
[ ] Slice 2.2–2.4 and Phase 3 remain unauthorized
```

---

## 15. Resulting composite design

If Revision 3 is accepted, the complete implementation contract is:

```text
Revision 1
+ Revision 2 / Rework 1
+ Revision 3 / Rework 2
```

with the newest addendum controlling on conflict.

Resulting canonical-source chain:

```text
durable explicit MANAGED policy binding
  -> stable exact control observation
  -> read-only AUTHORIZABLE promotion subject
  -> exact HUMAN RepositoryMutationAuthorization
  -> execution-time ELIGIBLE
  -> immutable intent
  -> exact non-force canonical ref update
  -> stable post-write observation
  -> SUCCEEDED

or, if provider visibility cannot be verified cleanly:

  -> VISIBLE_UNVERIFIED
  -> QUARANTINED
  -> exact HUMAN reconciliation
  -> HEALTHY
```

At no point can absence of configuration, repository-sync authority, executor capability, CI success, or provider visibility manufacture promotion authority.

---

## 16. Hard stop

Revision 3 is design only.

Required next gate:

```text
RLY-S110-DESIGN-EVAL-003

Outcome:
ACCEPT | REVISE | ESCALATE
```

Human design acceptance remains a separate authority event.

Implementation authorization remains separate.

**Revision 3 complete != design accepted. Design accepted != implementation authorized.**