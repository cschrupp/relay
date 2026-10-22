# Slice 1.10 — Canonical Source and Promotion Enforcement — Design Revision 2 / Rework 1

**Document class:** Lockable design rework record  
**Status:** PROPOSED FOR INDEPENDENT DESIGN RE-REVIEW  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Opening:** `RLY-S110-OPEN-001 — OPEN`  
**Design authority:** `RLY-S110-DESIGN-AUTH-001 — AUTHORIZED`  
**Revision 1:** `f9141f6f44927f2a13b85cce8ffd4501db0b183d`  
**Independent review:** `RLY-S110-DESIGN-EVAL-001 — REVISE`  
**Evaluation record:** `bc085c53b080ea197afc7ba4409b10c1658f2f40`  
**Implementation authorization:** NOT GRANTED

---

## 1. Rework contract

This document is a bounded successor/addendum to Design Revision 1.

Revision 1 remains authoritative wherever this document does not explicitly amend it.

The combined Revision-2 design subject is:

```text
Revision 1:
f9141f6f44927f2a13b85cce8ffd4501db0b183d

+

Design Revision 2 / Rework 1:
this exact frozen addendum
```

This rework resolves:

```text
F001 — ruleset bypass posture was not observable under the proposed App capability
F002 — restart recovery after visible remote success was incomplete
F003 — Human acceptance/evaluation continuity to a later promotion target was underspecified
F004 — RepositorySyncService remained an alternate canonical-ref mutation path
```

and incorporates the three nonblocking review clarifications:

```text
deterministic check-rerun selection
exact GitHub bypass-mode vocabulary
promotion intent/result uniqueness and idempotency
```

---

## 2. Rework summary

Revision 2 introduces five bounded corrections:

```text
RW1  Separate source-control verifier capability
RW2  Durable pre-write intent + restart reconciliation state machine
RW3  Exact per-property governance subjects + control-continuity chain
RW4  Canonical-ref reservation that fences RepositorySyncService
RW5  Deterministic check selection + explicit idempotency constraints
```

It also corrects one Revision-1 internal circularity:

```text
Human promotion authority cannot be required before Relay has produced
the exact subject that the Human must authorize.
```

Therefore Revision 2 separates pre-authorization **AUTHORIZABLE** state from post-authorization **ELIGIBLE** execution state.

---

## 3. RW1 — Source-control verifier capability resolves F001

### 3.1 Provider limitation accepted as a design fact

GitHub documents two relevant facts:

```text
GET repository ruleset:
  Metadata:read is sufficient to read ordinary ruleset state

bypass_actors:
  returned only when the caller has write access to the ruleset

ruleset history/version endpoints:
  require Administration:write
```

Authoritative platform references:

```text
https://docs.github.com/en/rest/repos/rules
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
```

Revision 1's single least-privileged App therefore cannot prove the bypass posture it requires.

### 3.2 Capability separation

Revision 2 defines two distinct GitHub credentials/capability domains:

```text
A. Relay Promotion App
   metadata:read
   contents:read/write
   checks:read
   administration: NONE

B. Relay Control Verifier
   metadata:read
   administration:write   # provider-required to observe full ruleset state/history
   contents:write: NONE
   checks:write: NONE
```

The provider unfortunately couples ruleset-bypass visibility to an administration-write-capable credential. Relay compensates by strict capability separation rather than granting that capability to the promotion executor.

Mandatory isolation rules:

- the promotion executor MUST NOT receive the Control Verifier credential/private key/token;
- the repository-sync service MUST NOT receive the Control Verifier credential;
- the Control Verifier implementation exposes GET-only ruleset observation methods;
- the Control Verifier code surface MUST contain no create/update/delete ruleset method and no generic caller-supplied HTTP method/path escape hatch;
- the Control Verifier MUST NOT receive contents-write capability;
- production composition MUST use a distinct credential/config object from the Promotion App;
- the Control Verifier is evidence-producing capability, never promotion authority;
- possession of its credential is not Human Authority.

Revision 2 still forbids the promotion executor from administering or weakening its own guardrails.

### 3.3 New provider-neutral port

Add provider-neutral protocol:

```text
SourceControlVerifierPort

observe_canonical_controls(
  project_id,
  repository,
  canonical_ref,
  policy
) -> SourceControlObservationV1
```

The promotion service depends on this narrow port, not on an administrative GitHub client.

GitHub provides one concrete adapter:

```text
GitHubRulesetVerifier
```

whose transport surface is GET-only.

### 3.4 Exact control observation

`GitHubSourceControlObservationV1` contains:

```text
schema_version = 1
project_id
repository
github_repository_id
github_node_id
canonical_ref
verifier_app_id
observed_at

integrity_ruleset:
  ruleset_id
  version_id
  updated_at
  source_type
  source
  target
  enforcement
  normalized_conditions
  normalized_rules
  normalized_bypass_actors

writer_ruleset:
  same fields

additional_applicable_rulesets:
  normalized tuple

observation_digest
```

`observation_digest` is SHA-256 over canonical JSON of the complete normalized observation excluding the digest field itself.

Normalization is deterministic:

- rulesets ordered by `(source_type, source, ruleset_id)`;
- rules ordered by stable rule type plus canonical parameter JSON;
- bypass actors ordered by `(actor_type, actor_id-or--1, bypass_mode)`;
- conditions serialized with sorted keys and canonical list order where GitHub semantics are order-insensitive.

### 3.5 Exact bypass contract

GitHub API vocabulary is now frozen exactly.

Ruleset A — canonical integrity:

```text
enforcement == active
bypass_actors == ()
restrict deletions == enabled
block force pushes == enabled
required status check == exact policy check
required check source == exact expected CI App
```

Ruleset B — canonical writer:

```text
enforcement == active
restrict updates == enabled
bypass_actors == exactly one actor

actor_type  == Integration
actor_id    == exact Relay Promotion App ID
bypass_mode == always
```

`pull_request` and `exempt` are nonconformant for the writer bypass.

`exempt` is explicitly forbidden because GitHub documents that exempt actors do not have rules run for them.

Additional applicable rulesets are allowed only if explicitly allowlisted by exact ID in the promotion policy and fully observed by the verifier. Unknown/unexpected applicable rulesets yield `UNKNOWN`.

### 3.6 Observation timing

Source-control observation occurs:

```text
prepare/authorizability:
  observe current control posture

execution preflight:
  observe again immediately before durable intent creation

post-write verification:
  observe again after canonical-ref visibility
```

Execution preflight MUST be conformant.

The exact pre-write observation is persisted inside the immutable promotion intent.

A successful result requires the post-write observation to identify the same exact integrity/writer ruleset versions as the persisted pre-write observation.

If ruleset versions/fingerprints changed between intent and post-write observation:

```text
remote visibility may have occurred
but Relay cannot prove execution under the frozen control posture
-> no SUCCEEDED result
-> terminal VISIBLE_UNVERIFIED result / Human reconciliation required
```

This is deliberately conservative.

### 3.7 F001 disposition

F001 is resolved because bypass posture is now observed by an isolated capability that can see the provider-sensitive field, while the promotion executor still cannot mutate rulesets.

---

## 4. RW2 — Durable intent and restart reconciliation resolves F002

### 4.1 Do not hold SQLite transaction across GitHub network I/O

Revision 1 D15 is replaced.

Relay MUST NOT keep `BEGIN IMMEDIATE` open across a remote GitHub request.

The immutable intent is the durable pre-write boundary.

### 4.2 Promotion attempt records

Migration v6 still uses exactly two append-only tables:

```text
repository_promotion_intents
repository_promotion_results
```

but Revision 2 clarifies that a result records the terminal observed outcome of one promotion attempt, not only successful promotions.

`RepositoryPromotionIntentV1`:

```text
promotion_id
project_id
repository
canonical_ref
subject
subject_digest
authorization_id
authorization_subject_digest
policy_digest
governance_basis_digest
expected_parent
target_commit
prewrite_execution_eligibility
prewrite_required_check_observations
prewrite_source_control_observation
prewrite_basis_digest
created_at
executor
```

The intent is inserted and COMMITTED only after full live execution eligibility has passed and immediately before the remote ref update.

`RepositoryPromotionResultV1`:

```text
promotion_id
project_id
repository
canonical_ref
expected_parent
target_commit
outcome
observed_head
observed_at
postwrite_source_control_observation | null
reconciled_after_restart: bool
reason_code | null
provider_request_id | null
```

Outcome vocabulary:

```text
SUCCEEDED
NOT_APPLIED
CONFLICT
VISIBLE_UNVERIFIED
```

Only `SUCCEEDED` is a Relay promotion record.

`NOT_APPLIED`, `CONFLICT`, and `VISIBLE_UNVERIFIED` are immutable attempt evidence and MUST NOT be projected as successful promotion.

### 4.3 Normal execution algorithm

Replace Revision 1 D15 with:

```text
1. resolve exact promotion request and policy
2. compute fresh pre-authorization/authorizability basis
3. load exact RepositoryMutationAuthorization
4. compute full execution eligibility including promotion authority
5. require ELIGIBLE
6. obtain fresh required-check observations
7. obtain fresh SourceControlVerifier observation
8. re-read canonical ref == exact expected parent
9. inside short BEGIN IMMEDIATE:
     a. recheck no terminal SUCCEEDED result already proves this target
     b. allocate/check promotion_id
     c. insert immutable intent with exact pre-write basis
     d. COMMIT
10. mint repository-scoped Promotion-App contents:write token
11. PATCH exact canonical ref to exact target with force=false
12. reconcile ambiguous transport response by observation only
13. re-read exact canonical ref and target commit
14. re-observe source-control controls
15. append exactly one terminal immutable result
```

No blind retry exists.

### 4.4 Restart-first reconciliation

When `execute_canonical_promotion(promotion_id)` finds an existing intent with no result, it MUST reconcile the remote ref **before ordinary stale-parent rejection**.

```text
head == target:
  verify exact intent/authorization/target identity;
  verify target commit exists and subject digest is intact;
  obtain current source-control observation;
  require current integrity/writer ruleset version fingerprint
    == intent.prewrite_source_control_observation fingerprint;
  if equal -> append SUCCEEDED with reconciled_after_restart=true;
  if not equal -> append VISIBLE_UNVERIFIED; require Human reconciliation;
  never PATCH again.

head == expected_parent:
  no remote effect is visible;
  recompute full execution eligibility;
  if the current basis digest exactly equals the intent prewrite_basis_digest:
      the same promotion_id may retry the one PATCH;
  else:
      append NOT_APPLIED with STALE_INTENT;
      a fresh promotion_id is required after fresh preparation;

head == any third commit:
  append CONFLICT;
  no success result;
  no PATCH;
  no blind retry.
```

### 4.5 Ambiguous-response reconciliation

Same-process indeterminate response follows the same three-way observation and terminal-result rules.

### 4.6 Crash test

Implementation MUST include a deterministic crash fixture:

```text
intent committed
PATCH provider effect succeeds
process stops before result insert
restart
head == target
same control fingerprint
-> one reconciled SUCCEEDED result
-> zero additional PATCH calls
```

### 4.7 F002 disposition

F002 is resolved because a visible remote success is recoverable from the persisted exact pre-write intent without first invalidating itself as a stale-parent request.

---

## 5. RW3 — Exact governance subjects and control continuity resolves F003

### 5.1 No statement-class collapse

Revision 2 preserves:

```text
Human acceptance of commit A
!= independent evaluation of commit C
!= promotion authorization for commit B
!= promotion execution of B
```

Those exact subjects may differ.

### 5.2 Promotion governance basis

Add `PromotionGovernanceBasisV1`:

```text
schema_version = 1
project_id
slice_id | null

accepted_result_ref:
  result_id
  result_baseline_id
  accepted_commit
  manual_evaluation_id
  human_approval_decision_id
  accepted_execution_id
  accepted_at

independent_evaluation_refs:
  exact structured verification references

continuity_anchor_commit
target_commit
governance_basis_digest
```

The accepted-result portion MUST reconstruct from the existing structured `AcceptedSliceResult` chain.

Each independent-evaluation reference MUST be a structured exact-subject judgment. Existing `ManualEvaluationRecord` is an accepted source. A future exact typed mirror of repository-governance evaluation is allowed.

Markdown prose is never parsed to manufacture a judgment.

If the required evaluation exists only as prose and no accepted structured adapter exists:

```text
required evaluation basis = UNKNOWN
promotion blocked
```

### 5.3 Promotion subject amendment

`CanonicalPromotionSubjectV1` from Revision 1 is amended to include:

```text
governance_basis_digest
```

The exact Human `RepositoryMutationAuthorization` therefore binds:

- exact repository/ref/parent/target;
- exact promotion policy;
- exact required-check specifications;
- exact structured governance basis used for control continuity.

### 5.4 Per-property exact subject

Add `PromotionPropertyResultV1`:

```text
property_name
outcome: PASS | FAIL | UNKNOWN
exact_subject_ref
basis_refs
reason_codes
```

Mandatory subject mapping:

```text
RELAY_HUMAN_ACCEPTED
  subject = accepted_result_ref.accepted_commit

RELAY_INDEPENDENT_EVALUATION
  subject = the exact subject of the policy-selected structured evaluation ref

RELAY_CANONICAL_PARENT_CURRENT
  subject = exact repository/ref/expected-parent basis

RELAY_REQUIRED_CHECKS_CURRENT
  subject = exact target_commit

RELAY_SOURCE_CONTROL_ENFORCED
  subject = exact repository/ref + policy basis

RELAY_PROMOTION_AUTHORIZED
  subject = exact CanonicalPromotionSubjectV1

RELAY_CONTROL_CONTINUITY_VERIFIED
  subject = exact governance-chain digest from accepted/evaluated subject(s) through target
```

Thus Relay never claims that a Human accepted target B when the Human actually accepted A.

### 5.5 Continuity rules

`RELAY_CONTROL_CONTINUITY_VERIFIED = PASS` only after exact promotion authority exists and all required links are reconstructable:

```text
accepted result A is durable and current under existing acceptance semantics
required independent evaluation E is durable, ACCEPT, and exact for E
A and E satisfy policy-required ancestry/order
continuity_anchor is an ancestor of target B
target B is the exact promotion subject target
RepositoryMutationAuthorization binds B + governance_basis_digest
no required current record is superseded/rejected/stale
canonical expected parent remains current
```

Policy may require the independent evaluation or Human acceptance to bind the target itself.

If policy requires target-bound acceptance/evaluation and only an ancestor-bound record exists, result is `UNKNOWN`, not PASS.

Default v1 policy MAY allow:

```text
Human technical acceptance bound to exact accepted result A
+ structured independent evaluation bound to exact applicable ancestor/closure subject E
+ exact Git ancestry A/E -> B
+ exact Human repository-mutation authorization bound to B
+ RELAY_CONTROL_CONTINUITY_VERIFIED
```

This is control continuity; it is not retroactive Human acceptance of B.

### 5.6 Two-stage state model removes authorization circularity

Revision 1 used `ELIGIBLE` before authority issuance while also listing `RELAY_PROMOTION_AUTHORIZED` as mandatory. That is circular and is corrected here.

Pre-authorization preparation returns:

```text
AUTHORIZABLE
INELIGIBLE
UNKNOWN
```

`AUTHORIZABLE` requires all pre-authority predicates and carries the exact promotion subject + digest that may receive Human repository-mutation authority.

It does **not** claim `RELAY_PROMOTION_AUTHORIZED = PASS`.

After exact authority exists, execution-time re-evaluation returns:

```text
ELIGIBLE
INELIGIBLE
UNKNOWN
```

`ELIGIBLE` requires the complete mandatory property set including:

```text
RELAY_PROMOTION_AUTHORIZED = PASS
RELAY_CONTROL_CONTINUITY_VERIFIED = PASS
```

Only execution-time `ELIGIBLE` can create a durable intent.

### 5.7 F003 disposition

F003 is resolved because every property remains truthful about its exact subject and the final target is connected through an explicit, machine-verifiable control-continuity chain rather than by reinterpreting earlier acceptance.

---

## 6. RW4 — Canonical-ref reservation resolves F004

### 6.1 Shared policy provider

Add mandatory provider-neutral dependency:

```text
CanonicalPromotionPolicyProvider

policy_for(project_id, repository, ref_name)
  -> CanonicalPromotionPolicyV1 | None
```

The provider is application composition/configuration, not caller-controlled request data.

The same provider instance/configuration is injected into:

```text
CanonicalPromotionService
RepositorySyncService
```

No production constructor may silently default to an allow-all/no-guard implementation.

An exact policy digest is included in every promotion subject.

Changing the policy changes the digest and stales existing exact promotion authority.

### 6.2 RepositorySyncService canonical guard

Existing repository synchronization remains unchanged only for repositories/refs without an active canonical-promotion policy.

When sync preparation discovers that its provider default branch is the active canonical ref under `CanonicalPromotionPolicyProvider`:

```text
if repository contract state == CURRENT:
  read-only/no-op recognition may return CURRENT

if a remote mutation would be required:
  raise RepositorySyncCanonicalRefReserved
  before minting a write token
  before creating any blob/tree/commit
  before calling update_git_ref
```

Repository-sync mutation authority cannot override this reservation.

`RepositoryMutationAuthorization<RepositorySyncSubjectV1>` is not valid promotion authority.

### 6.3 Canonical mutation callsite allowlist

Add a repository-contract/static test over production Python sources:

```text
GitHubClient.update_git_ref(...) callsites allowed only in:
  src/relay_engine/repository_sync/service.py
  src/relay_engine/promotion/service.py
```

and separately prove:

```text
repository_sync/service.py:
  active canonical ref -> mutation path unreachable

promotion/service.py:
  active canonical ref -> exact promotion subject/authority required
```

Any new production ref-mutating callsite fails repository-contract tests.

### 6.4 Backward compatibility statement corrected

Revision 1 D32 is amended:

```text
uncontrolled/noncanonical RepositorySyncService behavior remains backward compatible;
mutation of an actively governed canonical ref is intentionally narrowed and must fail closed.
```

### 6.5 F004 disposition

F004 is resolved because actor-level GitHub bypass is no longer the only boundary; Relay code also reserves the active canonical ref exclusively for `CanonicalPromotionService`.

---

## 7. RW5 — Deterministic check selection

Revision 1 D07/D20 are amended.

GitHub adapter MUST query the exact target SHA using:

```text
GET /repos/{owner}/{repo}/commits/{target_sha}/check-runs
  ?check_name=<exact name>
  &app_id=<exact app id>
  &filter=latest
  &per_page=100
```

GitHub documents `filter=latest`, `check_name`, and `app_id` for this endpoint and requires Checks:read for GitHub App installation tokens:

```text
https://docs.github.com/en/rest/checks/runs
```

For one required check specification, Relay v1 requires exactly one unambiguous returned latest check run after exact SHA/name/app filtering.

```text
0 matches -> UNKNOWN / missing
>1 matches -> UNKNOWN / ambiguous check identity
1 match:
  head_sha == target
  name == required name
  app.id == expected_app_id
  status == completed
  conclusion == success
  -> PASS
```

Any other status/conclusion fails or remains unknown according to whether violation versus insufficient/current evidence is positively known.

Repository-contract tests MUST ensure the Relay dogfood required job name `quality` is unique across workflows because GitHub warns duplicate job names can create ambiguous required checks.

---

## 8. RW5 — Promotion intent/result uniqueness and idempotency

Migration v6 exact relational constraints are now frozen.

### `repository_promotion_intents`

```text
promotion_id TEXT PRIMARY KEY
project_id TEXT NOT NULL
canonical_ref TEXT NOT NULL
subject_digest TEXT NOT NULL
expected_parent_sha TEXT NOT NULL
target_sha TEXT NOT NULL
created_at TEXT NOT NULL
payload_json TEXT NOT NULL

INDEX by (project_id, canonical_ref, subject_digest)
INDEX by (project_id, canonical_ref, expected_parent_sha, target_sha)
```

Subject digest is intentionally **not UNIQUE** because a terminal NOT_APPLIED attempt may be followed by a fresh attempt under a newly observed dynamic evidence basis while the exact Human-authorized subject remains unchanged.

### `repository_promotion_results`

```text
promotion_id TEXT PRIMARY KEY
  REFERENCES repository_promotion_intents(promotion_id)
project_id TEXT NOT NULL
canonical_ref TEXT NOT NULL
outcome TEXT NOT NULL
target_sha TEXT NOT NULL
observed_at TEXT NOT NULL
payload_json TEXT NOT NULL

CHECK outcome IN ('SUCCEEDED','NOT_APPLIED','CONFLICT','VISIBLE_UNVERIFIED')
```

Add partial unique index:

```text
one successful canonical target:
UNIQUE(project_id, canonical_ref, target_sha)
WHERE outcome = 'SUCCEEDED'
```

Both tables receive UPDATE and DELETE rejection triggers.

### Idempotency

```text
same promotion_id + existing result:
  return exact stored result; no provider write

same promotion_id + unresolved intent:
  run restart-first reconciliation

new promotion_id + exact subject:
  allowed only after any older unresolved exact-subject intent has been reconciled to a terminal result

canonical head already == target + matching prior SUCCEEDED result:
  return existing success; no new PATCH
```

This makes idempotency explicit without mutable attempt state.

---

## 9. Revised promotion preparation/execution model

Revision 1 D12–D16 are superseded by this two-phase model.

### Phase A — authorizability

`prepare_canonical_promotion(...)` is read-only.

It resolves:

```text
project/repository identity
active canonical promotion policy
provider identity/state revision/default branch
exact canonical ref/head
exact target commit + ancestry
structured governance basis
required exact check runs
full SourceControlVerifier observation
pre-authority property results
```

Returns:

```text
AUTHORIZABLE -> exact CanonicalPromotionSubjectV1 + digest
INELIGIBLE   -> positively violated required condition(s)
UNKNOWN      -> unresolved/ambiguous required basis
```

### Phase B — Human exact authority

`authorize_canonical_promotion(...)`:

```text
accept AUTHORIZABLE preparation only
require HUMAN actor
persist exact RepositoryMutationAuthorization<CanonicalPromotionSubjectV1>
no GitHub mutation
```

### Phase C — execution eligibility

`evaluate_execution_eligibility(...)` re-runs all live facts and adds:

```text
RELAY_PROMOTION_AUTHORIZED
RELAY_CONTROL_CONTINUITY_VERIFIED
```

Only exact `ELIGIBLE` may insert a promotion intent.

### Phase D — durable intent / remote effect / result

Use RW2 algorithm.

---

## 10. Revised source-control policy fields

`CanonicalPromotionPolicyV1` is amended to include exact GitHub control expectations where GitHub is the provider:

```text
canonical_branch
promotion_app_id
control_verifier_app_id
integrity_ruleset_id
writer_ruleset_id
allowed_additional_ruleset_ids = ()
required_checks
require_source_control_enforcement = true
require_exact_parent = true
allow_force = false
allow_delete = false
human_acceptance_must_bind_target: bool
independent_evaluation_must_bind_target: bool
promotion_property_requirements
```

Provider-neutral model may hold a provider-control policy union; GitHub IDs remain in the GitHub-specific control portion rather than generic semantics.

---

## 11. Revised GitHub permission boundary

Promotion App exact installation profiles become:

```text
READ:
  contents:read
  metadata:read
  checks:read

WRITE:
  contents:write
  metadata:read
  checks:read
```

The existing GitHub integration accepts only those exact profiles.

Control Verifier uses a **separate** configuration/client path and is not accepted by `permission_profile()` for ordinary project repository access.

Verifier capability:

```text
metadata:read
administration:write
contents:write absent
```

because GitHub requires write access to see `bypass_actors` and Administration:write for ruleset version history.

No implementation authorization or credential installation is granted by this design.

---

## 12. Revised implementation change surface

Preserve Revision 1 D25 with these bounded amendments.

Expected promotion package:

```text
src/relay_engine/promotion/
    __init__.py
    errors.py
    models.py
    service.py
    controls.py          # provider-neutral control-verifier protocol
```

GitHub adapter additions:

```text
src/relay_engine/integrations/github/models.py
src/relay_engine/integrations/github/client.py      # checks/compare + low-priv reads
src/relay_engine/integrations/github/service.py

new narrow GET-only verifier adapter, exact location to follow existing integration layout:
src/relay_engine/integrations/github/ruleset_verifier.py
```

Repository-sync bounded changes:

```text
src/relay_engine/repository_sync/errors.py
src/relay_engine/repository_sync/service.py
```

Persistence remains migration v6 + store/export changes from Revision 1.

No workflow mutation is added.

Materially broader production scope requires escalation.

---

## 13. Required new tests from rework

### F001 / control verifier

```text
metadata-only promotion client cannot claim bypass posture
verifier full observation includes exact bypass actors
Ruleset A bypass nonempty -> nonconformant
Ruleset B actor_type != Integration -> nonconformant
Ruleset B wrong app ID -> nonconformant
Ruleset B bypass_mode pull_request -> nonconformant
Ruleset B bypass_mode exempt -> nonconformant
Ruleset B bypass_mode always + exact app -> conformant
verifier unavailable -> UNKNOWN
verifier adapter exposes only GET requests
promotion executor configuration contains no verifier credential
post-write ruleset version drift -> VISIBLE_UNVERIFIED
```

### F002 / restart

```text
crash after visible PATCH before result -> reconciled SUCCEEDED
restart target + control fingerprint changed -> VISIBLE_UNVERIFIED
restart parent + exact same basis -> one retry allowed
restart parent + changed basis -> NOT_APPLIED(STALE_INTENT)
restart third head -> CONFLICT
same promotion_id never issues second PATCH after terminal result
```

### F003 / subject continuity

```text
Human acceptance PASS binds only exact accepted commit
ancestor acceptance is not relabeled as target acceptance
target-bound policy rejects ancestor-only acceptance
ancestor acceptance + allowed continuity + exact target promotion authority -> continuity PASS
missing structured evaluation adapter -> UNKNOWN
prose-only evaluation cannot be parsed into PASS
governance_basis_digest mismatch -> promotion authority stale
pre-authorization preparation can be AUTHORIZABLE without promotion authority
execution cannot be ELIGIBLE without exact promotion authority
```

### F004 / exclusive writer

```text
RepositorySyncService CURRENT no-op on canonical ref allowed
RepositorySyncService mutation on active canonical ref rejected before write token
sync authorization cannot authorize canonical promotion
promotion service remains allowed exact canonical mutation path
production update_git_ref callsite allowlist exact
noncanonical/uncontrolled repository sync behavior preserved
```

### Check/idempotency

```text
latest check query uses exact SHA/name/app/filter=latest
zero check matches -> UNKNOWN
multiple exact latest matches -> UNKNOWN
one completed success -> PASS
one neutral/skipped/failure/in-progress -> non-PASS
duplicate quality job-name repository contract test
intent/result append-only triggers
one SUCCEEDED result per project/ref/target
terminal non-success permits later fresh promotion_id
```

---

## 14. Revised dogfood prerequisites

Before Slice 1.10 can close on `cschrupp/relay`, separate authorized operator/configuration work must establish:

```text
Relay Promotion App exact permission profile
Relay Control Verifier separate credential/configuration
Ruleset A exact integrity posture
Ruleset B exact Integration/always writer bypass
active CanonicalPromotionPolicyV1 for main
unique required quality check identity and exact source app
```

Dogfood proof must show both capability domains are distinct.

Live test must additionally prove `RepositorySyncService` cannot mutate `main` once the canonical policy is active.

---

## 15. Explicit non-authority preserved

This rework does not authorize:

- implementation;
- installation or permission change of either GitHub App;
- creation/update/deletion of rulesets;
- repository settings mutation;
- workflow mutation;
- canonical promotion execution;
- schema migration execution;
- automatic evaluator/Human decision;
- parsing Markdown to infer authority or evaluation;
- Role Contracts / Slice 2.2;
- Context/Work Packets / Slice 2.3;
- Workspace Authority / Slice 2.4;
- Phase 3;
- real-project agent execution.

The privileged Control Verifier credential is a proposed implementation dependency only. Its existence in design is not authority to create/install/use it.

---

## 16. Revision-2 acceptance matrix

Independent re-review must require:

```text
[ ] F001 resolved: bypass posture is machine-observable without giving promotion executor ruleset mutation capability
[ ] verifier credential and promotion credential are capability-separated
[ ] exact GitHub bypass_mode = always for sole Promotion App writer
[ ] F002 resolved: persisted-intent restart recovers visible success before stale-parent rejection
[ ] no SQLite write transaction spans GitHub network I/O
[ ] terminal non-success outcomes are durable and not misreported as promotion
[ ] F003 resolved: Human acceptance remains bound to exact accepted subject
[ ] per-property exact subjects are explicit
[ ] control continuity bridges accepted/evaluated subject(s) to exact target without statement-class collapse
[ ] authorizability and execution eligibility are distinct; no authority circularity
[ ] F004 resolved: RepositorySyncService cannot mutate an actively governed canonical ref
[ ] low-level ref update callsites are statically bounded
[ ] check rerun selection is deterministic and ambiguous duplicates fail closed
[ ] intent/result uniqueness/idempotency constraints are exact
[ ] Revision-1 non-force, exact-parent, no-self-admin, no-prose-authority invariants remain preserved
[ ] no new Human Authority semantics are invented
[ ] no workflow/ruleset mutation is authorized by design
[ ] Slice 2.2–2.4 and Phase 3 remain unauthorized
```

---

## 17. Resulting composite design

If Revision 2 is accepted, the implementation contract is Revision 1 plus this addendum.

Where they conflict, this addendum controls.

Core resulting chain:

```text
read-only authorizability
  -> exact promotion subject + governance basis digest
  -> exact HUMAN RepositoryMutationAuthorization
  -> execution-time full eligibility
  -> isolated full source-control observation
  -> immutable pre-write intent
  -> exact non-force canonical ref update
  -> restart-safe observation/reconciliation
  -> immutable terminal result
```

Canonical source now has two independent enforcement layers:

```text
GitHub layer:
  only Relay Promotion App is permitted to update canonical ref
  integrity rules still constrain that App

Relay application layer:
  RepositorySyncService is fenced from an active canonical ref
  only CanonicalPromotionService can request the governed mutation
```

---

## 18. Hard stop

Revision 2 is design only.

Required next gate:

```text
RLY-S110-DESIGN-EVAL-002

Outcome:
ACCEPT | REVISE | ESCALATE
```

Human design acceptance remains separate.

Implementation authorization remains separate.

**Rework complete != design accepted. Design accepted != implementation authorized.**