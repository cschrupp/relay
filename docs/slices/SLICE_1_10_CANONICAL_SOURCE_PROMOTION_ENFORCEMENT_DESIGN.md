# Slice 1.10 — Canonical Source and Promotion Enforcement — Design Revision 1

**Document class:** Lockable design record  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Opening:** `RLY-S110-OPEN-001 — OPEN`  
**Design authority:** `RLY-S110-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact design baseline:** `dac1557adeca9a1928d442a6f4aea809d8b33a10`  
**Implementation authorization:** NOT GRANTED

---

## 1. Purpose

Slice 1.10 closes the gap between Relay's semantic promotion governance and the technical Git ref that represents canonical source.

The design adds no second lifecycle and no second authority system.

```text
Relay semantic authority
    -> exact promotion subject
    -> deterministic promotion predicates
    -> exact Human repository-mutation authority
    -> trusted promotion executor
    -> non-force canonical-ref update
    -> durable promotion intent/result evidence
```

Core invariant:

```text
promotion executor != promotion decision maker
```

---

## 2. Current verified repository facts

Read-only design inspection at the exact design baseline established:

```text
canonical repository: github.com/cschrupp/relay
default branch: main
main protected flag: false
repository rulesets: []
merge commits allowed: true
squash merges allowed: true
rebase merges allowed: true

CI workflow: .github/workflows/ci.yml
workflow name: CI
quality job: quality

GitHub integration:
existing read/write installation-token profiles
existing exact Git ref reads
existing commit/tree/blob reads
existing commit/tree/blob creation
existing non-force branch-ref update
force=True explicitly forbidden by GitHubClient
ambiguous ref-update outcome explicitly reconciled rather than blindly retried
```

The current Relay repository is therefore **not source-control-conformant** for Slice 1.10 promotion enforcement. Opening/design authority does not permit changing those settings.

---

## 3. Existing accepted contracts reused

Slice 1.10 MUST reuse rather than replace:

1. `Project.primary_repository` as durable repository identity authority.
2. `RepositoryRef` and full canonical commit SHA values.
3. schema-v1 `.relay/registry.json` as the canonical document/artifact registry.
4. `RepositoryMutationAuthorization` as the durable exact HUMAN authority primitive for repository mutation.
5. `GitHubRepositoryAccessSelection` and installation `state_revision` as provider/access freshness.
6. repository-scoped GitHub App tokens.
7. `GitHubClient.get_git_ref()` and `update_git_ref(..., force=False)` behavior.
8. Slice 1.8 statement-class separation and native verified-property meanings.
9. Slice 1.7 Human technical acceptance and accepted-result semantics where they are applicable evidence.

Slice 1.10 does not reinterpret lifecycle `AuthorizationGrant` as repository mutation authority.

---

## 4. D01 — Two canonical concepts remain distinct

Relay has two different canonical concepts:

```text
repository registry canonical pointer
    = exact current canonical document/artifact revision

canonical source ref
    = exact provider Git ref whose current target is Relay's promoted source lineage
```

`CanonicalPointer` remains unchanged.

Slice 1.10 does not place branch/ref identity into `.relay/registry.json` and does not make the registry self-describe its own Git commit.

---

## 5. D02 — Canonical source identity

Provider-neutral conceptual value:

```text
CanonicalSourceRefV1
  project_id
  repository: full RepositoryRef
  ref_name: refs/heads/<branch>
  expected_parent: exact CommitRef
```

For GitHub v1, the canonical ref is the provider-reported default branch captured during promotion preparation. It MUST equal the branch named by the promotion policy.

The ref name identifies the mutation target. It is not sufficient authority by itself.

The expected parent SHA is promotion-critical. A moving branch name without exact parent binding cannot satisfy `RELAY_CANONICAL_PARENT_CURRENT`.

Default-branch identity changes after preparation stale the promotion subject.

---

## 6. D03 — Exact promotion subject

Add a strict immutable `CanonicalPromotionSubjectV1`:

```text
schema_version = 1
project_id
repository: RepositoryRef
installation_id
github_repository_id
github_node_id
expected_state_revision
canonical_ref
expected_parent: CommitRef
target_commit: CommitRef
promotion_policy_digest
required_check_specs
```

Constraints:

- repository identities must agree everywhere;
- parent and target use full canonical lowercase SHA;
- parent != target;
- canonical ref is a safe full heads ref;
- required check specs are unique and canonically ordered;
- subject serialization is canonical JSON with sorted keys and compact separators;
- subject digest is SHA-256 over those exact bytes.

The target commit is the exact commit that will become canonical. An accepted technical candidate is not automatically the promotion target; closure/finalization may produce a later exact target.

---

## 7. D04 — Reuse existing repository mutation authority

`RepositoryMutationAuthorization` becomes the common exact HUMAN authority envelope for two repository-mutation subject variants:

```text
RepositorySyncSubjectV1
CanonicalPromotionSubjectV1
```

The existing persistence table remains usable because it already stores:

```text
authorization_id
project_id
subject_digest
payload_json
```

No new promotion-authority table is required.

The authorization still requires a HUMAN actor and exact subject digest.

This is an evolution of the accepted repository-mutation authority mechanism, not a new authority system.

### Automated-v1 authority boundary

The v1 promotion executor MUST accept only an exact machine-verifiable `RepositoryMutationAuthorization` whose subject is the exact `CanonicalPromotionSubjectV1` being executed.

A prose-only finalization/closure authority MUST NOT be parsed, inferred, summarized, or converted into executable promotion authority.

Existing Human-governed workflows may semantically rely on a prior conditional finalization/closure authority, as Relay canon already permits. Automated v1 simply refuses to mechanize that authority unless it has been represented through an accepted structured authority mechanism.

This conservative boundary preserves:

```text
authority cannot be manufactured from prose
unknown structured authority -> promotion blocked
```

---

## 8. D05 — Promotion policy

Add immutable `CanonicalPromotionPolicyV1` with a deterministic digest.

It contains only promotion-enforcement policy, not Human authority:

```text
policy_id
schema_version = 1
canonical_branch
required_checks
require_source_control_enforcement = true
require_exact_parent = true
allow_force = false
allow_delete = false
allowed_update_actor = Relay GitHub App identity
promotion_property_requirements
```

Profile-selected requirements MAY add stricter predicates when an authoritative GovernanceProfile binding exists.

Slice 1.10 does not implement profile selection.

If a required profile/policy basis is unresolved, the applicable promotion property is `UNKNOWN` and promotion fails closed.

No later profile downgrade retroactively legitimizes a prior promotion.

---

## 9. D06 — Required promotion properties

Promotion preparation derives a bounded `PromotionEligibilityV1` using Slice 1.8 semantics.

Mandatory v1 properties:

```text
RELAY_EVIDENCE_SUBJECT_EXACT
RELAY_INDEPENDENT_EVALUATION
RELAY_HUMAN_ACCEPTED
RELAY_PROMOTION_AUTHORIZED
RELAY_CANONICAL_PARENT_CURRENT
RELAY_REQUIRED_CHECKS_CURRENT
RELAY_SOURCE_CONTROL_ENFORCED
RELAY_FAIL_CLOSED
```

`RELAY_EXACT_AUTHORIZED_BASELINE`, `RELAY_GOVERNANCE_PROFILE_BOUND`, and `RELAY_VERIFICATION_ASSETS_PROTECTED` are included when the accepted policy marks them applicable to the promotion subject.

Required `FAIL` or `UNKNOWN` blocks execution.

Slice 1.10 MUST NOT implement a generic property engine. The promotion service computes only the exact bounded promotion properties it owns or can derive from accepted upstream records.

---

## 10. D07 — Required-check identity and freshness

Required check specification:

```text
GitHubRequiredCheckV1
  name
  expected_app_id
```

For Relay dogfood, the required check name is `quality`.

The exact GitHub App ID producing that check MUST be observed and frozen during implementation/dogfood validation rather than guessed in design.

Relay requires the latest applicable check run for the exact target SHA and exact expected app to be:

```text
status = completed
conclusion = success
```

GitHub's broader merge semantics may treat neutral or skipped as acceptable in some configurations; Relay v1 intentionally requires `success` for its own predicate.

Target-SHA check evidence is stale if it belongs to another SHA, another check name, another source app, or a superseded/rerun state whose latest exact check is not successful.

---

## 11. D08 — GitHub App permission evolution

Promotion eligibility needs authenticated check-run reads for private as well as public repositories.

Therefore the accepted installation permission policy must be evolved, under this separately reviewed design, to allow exactly:

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

No `checks:write`, `administration`, `actions:write`, `workflows`, pull-request, or repository-rules write permission is authorized by this design.

Ordinary baseline/repository reads remain read-scoped. A write token remains repository-scoped and is minted only after exact mutation authority is proven.

---

## 12. D09 — GitHub source-control enforcement profile

GitHub v1 uses repository **rulesets** as the normative enforcement adapter.

### Ruleset A — canonical integrity

Targets the canonical branch and MUST enforce:

```text
restrict deletions
block force pushes
require status check: quality
required check source pinned to the expected GitHub App
no bypass actors
```

Strict/up-to-date required-check semantics MUST be enabled where represented by the GitHub ruleset API.

Ruleset A MUST NOT list the Relay App as a bypass actor.

### Ruleset B — canonical writer

Targets the canonical branch and MUST enforce:

```text
restrict updates
bypass actor: exact Relay GitHub App only
bypass mode: direct update permitted for the App
no Human/team/admin-role bypass entries
```

The split is intentional:

- Ruleset B allows only Relay's trusted App to update canonical source.
- The App still remains subject to Ruleset A, so it cannot bypass required CI, force-push blocking, or deletion blocking.

### Explicitly not required

```text
require pull request before merging: NO
require merge queue: NO
require linear history: NO
```

Relay canonical promotion is a governed direct ref update, not a PR merge.

Linear-history enforcement is not required because valid Relay finalization ancestry may include true merge commits that must remain preserved.

Legacy branch protection may coexist as stricter defense in depth, but it is not Relay's normative GitHub mapping and cannot substitute for the two required rulesets.

---

## 13. D10 — Repository-setting ownership

Relay's GitHub App MUST NOT receive administration permission merely to configure its own guardrails.

Slice 1.10 implementation may:

- model the desired ruleset contract;
- read active repository/branch rulesets;
- evaluate conformance;
- block promotion when controls are absent/ambiguous/nonconformant.

Slice 1.10 implementation MUST NOT automatically create/update/delete repository rulesets.

Applying the required GitHub rulesets is a separate Human/operator repository-setting mutation and requires explicit implementation/finalization authority when performed.

This prevents the promotion executor from weakening the controls that constrain it.

---

## 14. D11 — GitHub read adapter additions

Extend the existing GitHub integration minimally with read-only methods/models for:

```text
list active repository rulesets / exact rule details
get active rules applying to the canonical branch
list check runs for an exact target SHA
compare exact commits / ancestry evidence
```

Existing exact ref/commit/tree reads are reused.

No generic SCM provider framework is introduced.

Provider-neutral promotion models live outside `integrations/github`; GitHub mapping remains a concrete adapter.

---

## 15. D12 — Preparation is read-only

`CanonicalPromotionService.prepare(...)` performs no mutation.

It must re-resolve:

```text
Project.primary_repository
GitHub access selection
installation state_revision
provider repository ID/node ID/default branch
canonical branch ref
exact expected parent
target commit existence
target ancestry from expected parent
required target check runs
active ruleset conformance
app permission profile
app identity
upstream evaluation / Human-acceptance evidence supplied by accepted Relay stores
```

Preparation returns exactly one state:

```text
ELIGIBLE
INELIGIBLE
UNKNOWN
```

Only `ELIGIBLE` carries an exact `CanonicalPromotionSubjectV1` and subject digest that can receive Human repository-mutation authority.

`UNKNOWN` is non-executable.

---

## 16. D13 — Authority issuance

`authorize_canonical_promotion(...)` reuses the existing repository mutation authorization persistence seam.

It MUST:

- accept only an `ELIGIBLE` exact preparation;
- require `ActorKind.HUMAN`;
- bind the exact promotion subject and digest;
- use caller-owned authorization ID/time/reason;
- persist immutably;
- not mutate GitHub;
- not mark anything promoted.

Authorization durability does not make stale predicates current.

---

## 17. D14 — Durable promotion intent and result

Remote Git ref mutation and SQLite cannot be one atomic transaction.

To make crash/reconciliation behavior auditable, migration v6 is justified and limited to two append-only tables:

```text
repository_promotion_intents
repository_promotion_results
```

### `RepositoryPromotionIntentV1`

Inserted before the remote side effect and binds:

```text
promotion_id
project_id
exact CanonicalPromotionSubjectV1 + digest
authorization_id
authorization subject digest
prepared control/evidence digest
created_at
executor ActorRef
```

### `RepositoryPromotionResultV1`

Inserted only after exact observation proves successful canonical visibility:

```text
promotion_id
prior canonical CommitRef
resulting canonical CommitRef
target CommitRef
promoted_at
reconciled_after_indeterminate: bool
provider observation metadata
```

Both tables are append-only. No mutable attempt-state machine, queue, worker, lease table, or token cache is introduced.

---

## 18. D15 — Execution algorithm

`execute_canonical_promotion(...)` operates on one previously persisted intent.

Required sequence:

```text
1. load exact intent + exact RepositoryMutationAuthorization
2. re-run promotion preparation against live state
3. require same exact subject digest and ELIGIBLE
4. enter SQLite BEGIN IMMEDIATE execution critical section
5. recheck no success result already exists
6. recheck installation/access state and exact authorization
7. re-read canonical ref and require exact expected parent
8. mint repository-scoped WRITE token
9. PATCH canonical ref to exact target with force=false
10. reconcile ambiguous provider outcome by observation only
11. re-read canonical ref and exact target commit
12. require visible head == exact target
13. append immutable promotion result
14. commit SQLite transaction
```

The critical section serializes Relay promotion execution for the SQLite authority store. GitHub Ruleset B makes the Relay App the only canonical-ref writer; together these close the stale-parent race without pretending GitHub and SQLite are a distributed transaction.

---

## 19. D16 — Race and conflict semantics

Before the update, live canonical head MUST equal `expected_parent.sha` exactly.

Any different head is `STALE_CANONICAL_PARENT`; do not attempt promotion.

The provider update MUST use `force=false`.

Provider rejection is non-success and does not create a promotion result.

If the update response is indeterminate:

```text
head == target:
  verify exact target + controls + authority, then append reconciled success

head == expected parent:
  no success result; caller may retry the same exact intent after full revalidation

head == any third commit:
  INDETERMINATE/CONFLICT; do not write a success result and do not retry blindly
```

An exact retry after a persisted success returns the existing result without another ref mutation.

---

## 20. D17 — Ancestry policy

Target MUST be a descendant of the exact expected parent.

For GitHub, use exact compare/ancestry evidence plus the provider's non-force ref-update guarantee.

Relay does NOT require target to be a direct child.

This preserves accepted finalization lineages containing multiple commits and ancestry-preserving merge commits.

Forbidden:

```text
force update
rebase during promotion
squash during promotion
cherry-pick recreation during promotion
history rewrite
automatic merge conflict resolution
```

---

## 21. D18 — Rollback

Moving the canonical branch backward is not a valid promotion operation.

`force=true` remains forbidden.

A rollback must be represented as new forward history, for example an authorized revert commit or other new descendant, then promoted as a new exact subject.

Emergency destructive history rewrite is outside Slice 1.10 v1 and requires separate design/authority.

---

## 22. D19 — Source-control enforcement property

`RELAY_SOURCE_CONTROL_ENFORCED = PASS` only when the exact live GitHub control observation proves both required rulesets and exact canonical branch targeting.

Any of the following yields `FAIL` or `UNKNOWN` and blocks promotion:

- no rulesets;
- disabled/evaluate-only ruleset where active enforcement is required;
- branch not targeted;
- force pushes permitted;
- deletion permitted;
- required check absent;
- required check source not pinned;
- integrity-ruleset bypass exists;
- writer ruleset allows a Human/team/admin-role bypass;
- Relay App is not the sole allowed writer;
- ruleset state cannot be read or parsed unambiguously.

Repository admin capability is not accepted as a substitute.

---

## 23. D20 — Required-check property

`RELAY_REQUIRED_CHECKS_CURRENT = PASS` only when every required exact check specification has one current successful exact-target result from its required app identity.

Missing, queued, in-progress, cancelled, timed-out, neutral, skipped, stale-SHA, wrong-app, or ambiguous latest result does not PASS.

GitHub ruleset enforcement remains a second independent technical barrier; Relay does not rely only on its own check observation.

---

## 24. D21 — Promotion authorization property

`RELAY_PROMOTION_AUTHORIZED = PASS` only when:

```text
an immutable RepositoryMutationAuthorization exists
actor.kind == HUMAN
project matches
subject is CanonicalPromotionSubjectV1
subject digest is exact
subject equals the freshly re-prepared promotion subject
```

An authorization for repository sync, another target SHA, another parent, another branch, another policy digest, or another provider state revision is stale/nonmatching.

---

## 25. D22 — Human acceptance and evaluation inputs

Slice 1.10 does not create a second evaluation or Human-acceptance system.

Where promotion policy requires `RELAY_INDEPENDENT_EVALUATION` or `RELAY_HUMAN_ACCEPTED`, the service consumes accepted structured Relay records available to the project.

If the required upstream acceptance/evaluation exists only as unstructured prose and no accepted adapter can prove it, automated promotion returns `UNKNOWN` and fails closed.

This is intentional. Machine automation does not infer authority or verification from Markdown prose.

---

## 26. D23 — GovernanceProfile and Protected Verification Assets

Slice 1.10 consumes but does not implement these future mechanisms.

If an applicable accepted policy/profile requires:

```text
RELAY_GOVERNANCE_PROFILE_BOUND
RELAY_VERIFICATION_ASSETS_PROTECTED
```

the promotion request must carry exact authoritative inputs sufficient to evaluate those properties.

Absent authoritative inputs -> `UNKNOWN` -> promotion blocked.

No profile taxonomy, scoring engine, role system, workspace enforcement, or verification-asset mutation system is added.

---

## 27. D24 — GitHub ruleset configuration is not self-modifying

The implementation may expose a deterministic expected-control projection suitable for Human/operator configuration and review.

It must not call GitHub administration/ruleset mutation endpoints.

Reason:

```text
the executor must not be able to weaken the rules that constrain the executor
```

A later separately authorized administrative adapter could be designed, but is not required for Slice 1.10.

---

## 28. D25 — Implementation change surface

Expected new production package:

```text
src/relay_engine/promotion/
    __init__.py
    errors.py
    models.py
    service.py
```

Bounded existing changes:

```text
src/relay_engine/domain/ids.py
src/relay_engine/repository_sync/models.py
src/relay_engine/repository_sync/service.py       # shared authority helpers only
src/relay_engine/integrations/github/models.py
src/relay_engine/integrations/github/client.py
src/relay_engine/integrations/github/service.py
src/relay_engine/persistence/migrations.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
```

Tests may add dedicated unit/integration files.

Documentation may add one consolidated architecture/reference document and update living status projections during finalization.

Materially broader production changes require escalation.

---

## 29. D26 — Migration v6

One deterministic SQLite migration is allowed:

```text
version 6
name: repository canonical promotion evidence

tables:
  repository_promotion_intents
  repository_promotion_results

indexes:
  promotion intents by project/ref/subject
  promotion results by project/ref/result

append-only triggers:
  intents UPDATE/DELETE forbidden
  results UPDATE/DELETE forbidden
```

No lifecycle table, Human-decision table, gate table, generic event store, queue, or worker schema is added.

---

## 30. D27 — No workflow mutation in Slice 1.10 v1

The current CI workflow already provides the `quality` job used by the Relay repository.

Slice 1.10 does not require changing `.github/workflows/ci.yml` merely to enforce promotion.

If implementation discovers that GitHub cannot bind the existing check deterministically as designed, STOP and escalate rather than silently changing workflow semantics.

---

## 31. D28 — Current Relay repository must dogfood the control

Closure of Slice 1.10 requires live proof on `cschrupp/relay`, not only mocks.

Required live sequence after separately authorized repository-setting configuration:

```text
1. ruleset verifier reports PASS for main
2. unauthorized Human/direct canonical update is technically blocked or independently proven blocked
3. exact target without required successful quality check is blocked
4. stale-parent promotion is blocked
5. authorized exact target with successful quality check promotes via non-force Relay App update
6. resulting main head is exact target
7. promotion result record is durable
8. retry is idempotent
```

Live configuration authority is separate from design acceptance and implementation authorization.

---

## 32. D29 — Failure taxonomy

Minimum typed failure classes:

```text
PromotionNotEligible
PromotionBasisUnknown
PromotionAuthorizationRequired
PromotionAuthorizationStale
PromotionAccessChanged
PromotionCanonicalRefChanged
PromotionTargetInvalid
PromotionAncestryInvalid
PromotionRequiredCheckMissing
PromotionRequiredCheckFailed
PromotionSourceControlNonconformant
PromotionRefUpdateRejected
PromotionRefUpdateIndeterminate
PromotionPostWriteVerificationError
PromotionAlreadyCompletedConflict
```

Provider/network errors never degrade into authority or PASS.

---

## 33. D30 — Positive tests

Implementation must prove at minimum:

```text
promotion subject canonical digest stable
exact Human mutation authority accepted
target descendant of expected parent accepted
exact required check success accepted
two-ruleset control posture accepted
non-force exact ref update success
promotion intent persisted before remote side effect
promotion result persisted after verified visibility
exact retry returns prior success without second write
indeterminate response + target visible reconciles to success
```

---

## 34. D31 — Negative and stale tests

Required negative cases:

```text
wrong repository / provider ID / node ID
changed installation state_revision
default branch changed
canonical ref changed
expected parent stale
target not descendant
target SHA abbreviated/invalid
missing Human promotion authorization
sync authorization reused as promotion authority
authorization for wrong parent/target/policy
missing independent evaluation when required
missing Human acceptance when required
required check absent
required check queued/in-progress
required check neutral/skipped/cancelled/failure
required check from wrong app
integrity ruleset absent
integrity ruleset bypass nonempty
force push not blocked
deletion not restricted
writer ruleset absent
Human/team/admin writer bypass present
Relay App not sole update bypass
ruleset observation unavailable
force=True attempt rejected locally
provider non-fast-forward rejection
third-head observation after indeterminate update
post-write head not target
duplicate promotion result conflict
```

---

## 35. D32 — Preservation tests

All existing Slice 1.1–1.9 tests remain mandatory.

Specifically prove:

- repository synchronization behavior remains unchanged;
- old persisted `RepositoryMutationAuthorization` payloads for sync still load;
- existing READ/WRITE GitHub permission tests are intentionally updated only for `checks:read`; no broader permission is accepted;
- repository-contract schema v1 is unchanged;
- Baseline resolution semantics are unchanged;
- manual evaluation / Human acceptance semantics are unchanged;
- generic lifecycle handover execution is unchanged;
- Decision Support remains non-authoritative.

---

## 36. D33 — Repository settings and merge methods

The current repository permits merge, squash, and rebase merge methods. Slice 1.10 does not need to disable them globally.

Once Ruleset B restricts updates to `main`, ordinary Human merge actions into `main` are blocked regardless of those repository-level merge-method toggles unless separately authorized/bypassed.

Feature/design branches remain outside the canonical ruleset target unless policy explicitly says otherwise.

---

## 37. D34 — Security boundary

Promotion credentials are capability, not authority.

```text
write token != promotion authority
GitHub App identity != Human Authority
admin capability != bypass permission under Relay policy
successful PATCH != valid promotion unless post-write proof + durable intent/authority exist
```

Tokens are never persisted.

The App receives no ruleset-administration permission.

---

## 38. D35 — No cryptographic-signing requirement

Slice 1.10 does not add signed-commit, Sigstore, in-toto, or transparency-log requirements.

Those may be mapped later, but canonical-source enforcement does not depend on claiming a formal SLSA level or cryptographic attestation.

---

## 39. D36 — External control mapping

GitHub rulesets and Checks are enforcement/evidence mechanisms, not Relay semantic authority.

The GitHub mapping relies on currently documented platform capabilities:

- branch/tag rulesets can restrict updates/deletions and block force pushes;
- rulesets can require status checks;
- bypass actors can include GitHub Apps;
- Git reference updates with `force=false` preserve fast-forward semantics;
- reading check runs through a GitHub App requires Checks:read.

External platform behavior is version-sensitive and must be covered by live dogfood evidence before closure.

---

## 40. D37 — Deliberate exclusions

Slice 1.10 v1 does not implement:

```text
generic SCM abstraction
GitLab/Bitbucket adapters
PR creation or merge automation
merge queue
branch creation strategy
repository ruleset administration
automatic policy/profile selection
Role Contracts
ContextManifest / Work Packets
workspace enforcement
agent execution
autonomous evaluation
automatic Human acceptance
automatic authority derivation from prose
force-push break glass
destructive rollback
cryptographic attestation framework
formal SLSA level certification
```

---

## 41. D38 — Implementation stop conditions

A future implementation must STOP and escalate if it requires:

```text
force ref update
ruleset-administration permission in the Relay App
workflow-file mutation to make the core design viable
new lifecycle transition semantics
new Human Authority semantics
parsing prose to infer promotion authority
generic provider-write abstraction
mutable promotion evidence
background worker / queue
automatic policy weakening
automatic bypass of source-control controls
material production surface beyond D25
```

---

## 42. D39 — Quality gate

A future authorized implementation candidate must pass:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest tests/unit/test_repository_contract.py
uv run pytest
uv build
git diff --check
```

plus exact-head GitHub Actions CI.

Passing engineering checks is evidence, not Human acceptance.

---

## 43. D40 — Design acceptance matrix

Independent design review must require all of:

```text
[ ] canonical document pointer and canonical Git ref remain distinct
[ ] promotion subject binds exact repository/ref/parent/target/policy/provider state
[ ] existing RepositoryMutationAuthorization is reused rather than duplicated
[ ] automated executor cannot infer authority from prose
[ ] required checks are exact-SHA and exact-app bound
[ ] source-control enforcement has no integrity bypass for Relay App
[ ] only Relay App can update canonical branch
[ ] App cannot administer/relax its own rulesets
[ ] force and deletion paths are blocked
[ ] non-force promotion preserves accepted ancestry
[ ] stale canonical parent fails closed
[ ] crash/indeterminate update has durable reconciliation basis
[ ] promotion result evidence is append-only
[ ] ruleset absence/ambiguity blocks promotion
[ ] no generic property engine is introduced
[ ] GovernanceProfile/PVA ownership remains downstream/consumed only
[ ] repository sync/backward compatibility preserved
[ ] implementation surface is minimum sufficient
[ ] live Relay dogfood is required before closure
[ ] Slice 2.2–2.4 and Phase 3 remain unauthorized
```

---

## 44. Resulting capability if implemented and accepted

Relay will be able to say, with technical enforcement rather than convention:

```text
this exact commit may become canonical
because this exact Human mutation authority exists,
the exact accepted evidence/checks are current,
the expected canonical parent is still current,
the repository controls prevent unauthorized writers and destructive updates,
and the trusted executor moved only the exact canonical ref by non-force update.
```

The canonical Git ref becomes an enforced output of Relay governance rather than a manually trusted convention.

---

## 45. Hard stop

This design authorizes no implementation and no repository-setting mutation.

Required next gate:

```text
independent design evaluation:
ACCEPT | REVISE | ESCALATE
```

Only after independent design acceptance evidence and separate Human design acceptance may implementation authorization be considered.

**Design complete != design accepted. Design accepted != implementation authorized.**