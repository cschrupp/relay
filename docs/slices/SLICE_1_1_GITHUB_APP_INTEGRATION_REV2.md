# Slice 1.1 — GitHub App Integration — Design Revision 2

**Document revision:** 2  
**Status:** REVIEW  
**Document class:** Lockable design amendment  
**Phase:** 1 — GitHub and Human-Controlled Project Workflow  
**Slice:** 1.1  
**Authorized baseline:** `cb9edc453442dc639a523ef301e4a258d0394daa`  
**Revision-1 design SHA:** `d73daf2ab2a850a4762084e042fa496f7a377e99`  
**Prior review:** `RLY-S11-DESIGN-EVAL-001 — REVISE`  
**Design authorization:** `RLY-S11-DESIGN-AUTH-001`  
**Implementation:** NOT AUTHORIZED  
**Reviewer next:** Independent Design Reviewer — GPT-5.6 Sol  
**Date:** 2026-09-26

---

# 1. Revision scope and precedence

Revision 2 is a bounded amendment to Slice 1.1 Design Revision 1.

The complete normative Slice 1.1 design is:

```text
Revision 1 at:
d73daf2ab2a850a4762084e042fa496f7a377e99

+

this Revision-2 amendment
```

All Revision-1 decisions remain normative except where this document explicitly replaces or tightens them.

Revision 2 resolves exactly:

```text
RLY-S11-DREV1-F001  webhook installation→project routing
RLY-S11-DREV1-F002  durable access readiness / permission drift
RLY-S11-DREV1-F003  synchronization/webhook concurrency
RLY-S11-DREV1-F004  webhook semantic idempotency evidence
```

No architecture redesign is introduced.

---

# 2. Design invariants added by Revision 2

## P1-D39 — Provider event routing is system-wide but state remains project-scoped

GitHub App webhooks identify an external installation but do not carry Relay `ProjectId`.

Therefore webhook dispatch uses an internal system-only reverse lookup equivalent to:

```python
project_bindings_for_installation(
    installation_id: int,
) -> tuple[ProjectId, ...]
```

This operation exists only to route a verified provider event to already-existing Relay project bindings.

Rules:

```text
verified webhook
      ↓
installation_id
      ↓
resolve existing Relay project bindings
      ↓
apply independently to every project-scoped binding
```

The reverse lookup:

- MUST NOT create a project;
- MUST NOT create a project↔installation binding;
- MUST NOT expose cross-project state through project-facing APIs;
- MUST return bindings in deterministic `ProjectId ASC` order;
- MAY return an empty tuple when Relay has no project bound to the installation.

If no binding exists, the verified webhook causes no project-state fabrication.

A later explicit setup/synchronization path establishes the binding.

Provider-wide negative signals such as `suspend` and `deleted` MUST fan out to every existing Relay project binding for that installation.

Project-facing reads remain strictly `ProjectId` scoped.

This resolves F001 without adding an Organization/Tenant abstraction.

---

## P1-D40 — Provider installation status and Relay access readiness are separate

Revision-1 `GitHubInstallationStatus` remains:

```text
ACTIVE
SUSPENDED
DELETED
```

Revision 2 adds durable Relay access readiness:

```text
GitHubAccessReadiness
    READY
    RESYNC_REQUIRED
    PERMISSION_POLICY_VIOLATION
```

Equivalent implementation names are acceptable if semantics remain exact.

A project-scoped GitHub repository is usable only when:

```text
installation.status == ACTIVE
AND
installation.readiness == READY
AND
current permission policy validates
```

Persisted repository rows alone never imply usability.

Required transitions:

```text
successful full synchronization
+ accepted permission policy
→ ACTIVE / READY

suspend webhook
→ SUSPENDED / RESYNC_REQUIRED

unsuspend webhook
→ ACTIVE / RESYNC_REQUIRED

new_permissions_accepted webhook
→ ACTIVE / RESYNC_REQUIRED
  unless the signed payload itself proves a policy violation,
  in which case → ACTIVE / PERMISSION_POLICY_VIOLATION

permission-policy violation found during explicit synchronization
→ persist ACTIVE / PERMISSION_POLICY_VIOLATION
→ emit immutable integration event
→ preserve or clear repository rows according to the atomic mutation contract,
  but rows are unusable in either case

deleted webhook
→ DELETED / RESYNC_REQUIRED
→ remove current repository-access rows
```

Fail-closed directionality is normative:

```text
negative/restrictive evidence
may block immediately

positive/broadening evidence
MUST NOT restore READY without authoritative full synchronization
```

Therefore:

```text
repository removed webhook
→ may remove/block immediately

repository added webhook
→ may record evidence and force RESYNC_REQUIRED
→ newly added repository is NOT usable until authoritative sync
```

`repository_ref_from_github(...)` MUST require `ACTIVE / READY`, not merely `ACTIVE`.

This resolves F002.

---

## P1-D41 — Project-scoped installation state has a monotonic local revision

Each persisted binding:

```text
(project_id, installation_id)
```

has:

```text
state_revision >= 1
```

Every successful mutation of installation/access state increments `state_revision` by exactly one.

The state revision is Relay-local concurrency provenance; it is not a GitHub revision and is not derived from timestamps.

The current-state payload persisted for the installation includes the exact revision or stores it as a verified indexed column that must agree with the typed payload.

---

## P1-D42 — Explicit synchronization uses optimistic concurrency across network work

`synchronize_installation(...)` operates conceptually as:

```text
1. read project-scoped current state_revision (or ABSENT)
2. remember expected revision
3. perform all remote reads and pagination
4. validate provider payloads and permission policy
5. begin one local write transaction
6. verify current state_revision still equals expected revision
7. if equal: commit complete new state atomically
8. if different: abort with concurrency conflict
```

If the binding was absent at step 1, the expected state is explicitly `ABSENT`; creation succeeds only if it is still absent at commit.

A mismatch raises:

```text
GitHubIntegrationConcurrencyConflict
```

under the provider-specific integration error family.

No hidden automatic retry occurs.

This prevents stale synchronization results from overwriting newer suspension, deletion, permission, or repository-access signals.

---

## P1-D43 — Webhooks mutate the same revisioned state atomically

Every supported project-scoped webhook application occurs in one local transaction.

The atomic mutation unit includes, as applicable:

```text
installation provider status
access readiness
repository-access rows
state_revision
immutable integration event
delivery idempotency evidence
```

A webhook reads the current state revision, applies one semantic mutation, and writes revision `N + 1`.

Provider fanout to multiple projects is **not** one cross-project transaction.

Each project binding is applied independently so one corrupt/unavailable project state cannot roll back a valid security restriction for another project.

The dispatcher returns an explicit per-project result set to the caller.

Security-sensitive negative events must not be silently skipped for one project because another project binding fails.

This resolves the mutation side of F003.

---

## P1-D44 — Typed webhook envelope and deterministic semantic digest

After HMAC verification and before state mutation, supported webhooks are normalized to a typed semantic envelope equivalent to:

```python
GitHubWebhookEnvelope(
    event_name: str,          # from X-GitHub-Event
    delivery_id: str,         # from X-GitHub-Delivery
    action: str,
    installation_id: int,
    semantic_payload: <validated event-specific fields>,
)
```

`X-GitHub-Event` and `X-GitHub-Delivery` are required for supported processing.

The semantic envelope excludes:

```text
signature header
webhook secret
raw authorization data
irrelevant provider fields
```

A deterministic delivery digest is:

```text
sha256(
    UTF-8 canonical JSON of the validated semantic webhook envelope
)
```

Canonical JSON uses the accepted Relay convention:

```python
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

The digest format is:

```text
sha256:<64 lowercase hex>
```

The digest fingerprints the provider semantic event, not the resulting local state.

---

## P1-D45 — Delivery idempotency is project-scoped and independent of later state

For every supported delivery applied to an existing project binding, persist:

```text
project_id
delivery_id
delivery_digest
```

with durable uniqueness on:

```text
(project_id, delivery_id)
```

This evidence may be represented directly on the immutable integration event when the schema guarantees the same uniqueness and retrieval semantics; a separate receipt table is not required merely for abstraction.

Rules:

```text
no existing (project_id, delivery_id)
→ apply semantic mutation or accepted semantic no-op
→ persist delivery evidence atomically

existing same delivery_id + same delivery_digest
→ idempotent NO-OP
→ do not advance state_revision again
→ do not append a duplicate integration event

existing same delivery_id + different delivery_digest
→ GitHubIntegrationIntegrityError
→ no state mutation
```

Idempotency is checked before evaluating the delivery against the current later state.

Therefore a redelivery remains idempotent even if unrelated later events changed installation state.

A verified webhook for an installation with no existing Relay project binding is not persisted as project-scoped delivery evidence because no project authority exists to attach it to.

This resolves F004.

---

## P1-D46 — State digests are normative if retained

If `prior_state_digest` and `resulting_state_digest` remain in `GitHubInstallationEvent`, they are defined as:

```text
sha256(canonical JSON of complete project-scoped persisted GitHub integration state)
```

Complete state includes at minimum:

```text
validated installation snapshot
provider status
Relay access readiness
state_revision
canonical ordered current repository-access set
```

The digest excludes secrets, tokens, signatures, and transient HTTP diagnostics.

Repository ordering for digest input is:

```text
github_repository_id ASC
```

If implementation determines these state digests provide no evidence beyond `state_revision` plus the exact persisted event payload, they MAY be omitted entirely.

They MUST NOT be left implementation-defined.

---

## P1-D47 — Permission-policy failure is a state transition, not only an exception

Revision-1 D20 is amended.

Remote/network/authentication failures before authoritative provider state is known still cause no persistence change.

However once a full synchronization has authoritatively established an installation's permission grant and that grant violates the accepted Slice-1.1 policy, Relay MUST persist that security state:

```text
status:
ACTIVE unless provider state says otherwise

readiness:
PERMISSION_POLICY_VIOLATION
```

and append a corresponding immutable event in the same concurrency-checked transaction.

The synchronization command may return/raise a typed permission-policy result after durable restriction is committed, but it MUST NOT leave previous `READY` state usable.

This is the exception to Revision-1's broad statement that no persistence occurs until all validation succeeds: provider payload structure must validate first, but a structurally valid authoritative permission grant that violates Relay policy is itself valid security evidence to persist.

---

## P1-D48 — Repository add/remove webhook convergence

Revision-1 D25 is tightened.

### Removed

A validated `installation_repositories` removal may immediately remove the exact matching provider repository identity from each bound project's current set and sets:

```text
readiness = RESYNC_REQUIRED
```

until a full synchronization confirms the complete set.

### Added

A validated `installation_repositories` addition MUST NOT make the repository immediately usable.

It records immutable evidence and sets:

```text
readiness = RESYNC_REQUIRED
```

The newly observed repository may be retained as unconfirmed provider evidence only if implementation clearly separates it from the usable current set; otherwise do not insert it into current access rows until resync.

The minimum implementation should prefer not inserting unconfirmed additions into the current usable repository table.

Full synchronization remains authoritative for restoring `READY` and the complete accessible set.

---

## P1-D49 — 403 failure-classification precedence

GitHub `403` is not mapped to `GitHubPermissionError` solely by status code.

Classification order must first inspect rate-limit evidence available from the response, including provider rate-limit headers or documented rate-limit response semantics.

Normative precedence:

```text
rate-limit evidence
→ GitHubRateLimited

otherwise authenticated 403 indicating insufficient permission
→ GitHubPermissionError

otherwise
→ GitHubRemoteError or a narrower justified provider error
```

No local installation deletion/suspension state may be fabricated from an ambiguous `403`.

---

# 3. Revised persistence shape

Revision-1 migration v2 remains the correct persistence boundary.

The same migration must now support the following semantics.

## github_installations

Logical identity:

```text
(project_id, installation_id)
```

Required current fields/typed payload semantics include:

```text
project_id
installation_id
state_revision
provider status
access readiness
validated installation snapshot
```

Required invariant:

```text
state_revision >= 1
```

## github_installation_repositories

Still represents the current **confirmed** full repository-access set for one project-scoped installation.

Rows are usable only when parent installation is `ACTIVE / READY`.

## github_installation_events

Immutable event history includes enough information to reconstruct:

```text
project_id
installation_id
event type
observed_at
state revision transition
delivery_id when webhook-derived
delivery_digest when webhook-derived
```

A schema may include explicit:

```text
prior_state_revision
resulting_state_revision
```

with:

```text
resulting = prior + 1
```

for state-changing events.

Webhook idempotent redelivery creates no second event.

Required durable uniqueness for webhook-derived events/receipts:

```text
(project_id, delivery_id)
```

where `delivery_id` is non-null.

## Reverse routing

The system-only installation→project lookup may use the indexed current-state table directly.

No separate global binding table is required unless implementation evidence demonstrates it is necessary.

Minimum sufficient query:

```sql
SELECT project_id
FROM github_installations
WHERE installation_id = ?
ORDER BY project_id
```

or equivalent typed store API.

---

# 4. Revised synchronization contract

Primary command remains conceptually:

```python
synchronize_installation(
    *,
    project_id: ProjectId,
    installation_id: int,
    observed_at: datetime,
    ...
) -> GitHubInstallationSnapshot
```

Revised sequence:

```text
read current binding + expected state_revision / ABSENT
        ↓
create short-lived app JWT
        ↓
GET installation metadata
        ↓
validate provider payload structure and app identity
        ↓
create short-lived installation token when installation permits it
        ↓
list complete installation repository set with pagination
        ↓
validate repository payloads
        ↓
classify exact permission policy
        ↓
begin local transaction
        ↓
compare current state_revision with expected value
        ↓
if mismatch: rollback / concurrency conflict
        ↓
if permission policy valid:
    persist provider state + READY + full repo set + event + revision
else:
    persist PERMISSION_POLICY_VIOLATION + event + revision
    repository rows remain unusable
        ↓
commit
```

If provider state is `SUSPENDED`, synchronization persists/retains blocked state and does not restore READY.

If provider state proves installation deletion/unavailability through the explicit accepted classification path, the mutation is concurrency-checked and fail-closed.

Authentication, rate-limit, malformed-response, or ambiguous remote failures do not fabricate a state transition.

---

# 5. Revised webhook contract

Required processing order:

```text
1. require X-GitHub-Event
2. require X-GitHub-Delivery
3. verify X-Hub-Signature-256 over exact raw body
4. parse JSON
5. validate supported typed semantic envelope
6. compute delivery_digest
7. resolve all existing Relay project bindings for installation_id
8. for each binding in ProjectId ASC order:
       begin independent transaction
       check delivery idempotency
       if duplicate/same digest → no-op
       if duplicate/conflicting digest → integrity failure for that binding
       otherwise apply fail-closed semantic transition
       advance state_revision if state changes
       persist integration event + delivery evidence atomically
9. return explicit per-project outcomes
```

An unsupported event/action:

```text
must not mutate project state
```

Whether it is returned as `IGNORED_UNSUPPORTED` or a typed unsupported-event result is an implementation detail, provided it is deterministic and not treated as a successfully applied supported delivery.

---

# 6. Revision-2 acceptance criteria

Revision-1 A01–A84 remain applicable except where tightened below.

Add:

```text
A85  verified webhook installation_id is routed to all and only existing project bindings
A86  webhook routing cannot create project↔installation bindings
A87  no-binding webhook fabricates no project state
A88  provider status and Relay access readiness are separate durable concepts
A89  repository use requires ACTIVE / READY
A90  unsuspend produces RESYNC_REQUIRED, not READY
A91  new_permissions_accepted cannot silently preserve READY
A92  authoritative permission-policy violation is persisted durably
A93  permission-policy violation blocks repository use
A94  each project-scoped installation binding has monotonic state_revision
A95  successful state mutation advances state_revision exactly once
A96  explicit synchronization compares expected state_revision before commit
A97  stale synchronization cannot overwrite newer webhook state
A98  concurrency conflict commits neither state nor event nor repo-set changes
A99  webhook mutation advances the same revisioned state
A100 cross-project webhook fanout uses independent project transactions
A101 X-GitHub-Event is required for supported webhook handling
A102 X-GitHub-Delivery is required for supported webhook handling
A103 delivery_digest uses canonical validated semantic-envelope JSON
A104 delivery idempotency uniqueness is (project_id, delivery_id)
A105 same delivery + same digest is no-op independent of later state
A106 same delivery + different digest is integrity error
A107 idempotent redelivery does not append duplicate event or advance revision
A108 repository removal can restrict immediately and forces RESYNC_REQUIRED
A109 repository addition cannot become usable before full resync
A110 state digests, if retained, have normative canonical representation
A111 403 classification checks rate-limit evidence before permission classification
A112 no F001–F004 correction introduces Slice 1.2 or 1.3 capability
```

---

# 7. Required Revision-2 regression scenarios

Add at minimum:

```text
test_webhook_routes_installation_to_all_existing_project_bindings
test_webhook_with_no_binding_creates_no_project_state
test_webhook_routing_cannot_create_project_binding
test_unsuspend_sets_resync_required_not_ready
test_repository_selection_requires_active_ready
test_new_permissions_accepted_blocks_until_resync
test_permission_policy_violation_is_persisted_and_blocks_use
test_stale_sync_cannot_overwrite_suspend_webhook
test_stale_sync_cannot_overwrite_delete_webhook
test_concurrent_repository_change_causes_sync_conflict
test_successful_sync_advances_state_revision
test_concurrency_conflict_rolls_back_state_event_and_repo_rows
test_webhook_requires_event_header
test_webhook_delivery_digest_is_deterministic
test_webhook_redelivery_same_digest_is_idempotent_after_later_state_changes
test_webhook_conflicting_delivery_digest_is_integrity_error
test_idempotent_redelivery_does_not_advance_revision
test_repository_removed_blocks_and_requires_resync
test_repository_added_not_usable_before_resync
test_403_rate_limit_precedes_permission_classification
```

Revision-1 regressions remain required.

---

# 8. Finding disposition

```text
RLY-S11-DREV1-F001
WEBHOOK_PROJECT_ROUTING_UNDEFINED
→ RESOLVED by P1-D39 and revised webhook routing contract

RLY-S11-DREV1-F002
LOCAL_ACCESS_READINESS_AND_PERMISSION_DRIFT_NOT_CLOSED
→ RESOLVED by P1-D40, P1-D47, P1-D48

RLY-S11-DREV1-F003
SYNC_WEBHOOK_CONCURRENCY_CAN_OVERWRITE_NEWER_SECURITY_STATE
→ RESOLVED by P1-D41, P1-D42, P1-D43

RLY-S11-DREV1-F004
WEBHOOK_IDEMPOTENCY_EVIDENCE_NOT_DETERMINISTIC
→ RESOLVED by P1-D44, P1-D45, P1-D46
```

No prior accepted Phase-0 semantics are changed.

---

# 9. Registered living-projection preflight

This Revision-2 correction changes only a new Slice 1.1 design amendment document.

It does NOT change bytes of any artifact currently registered in `.relay/registry.json`.

Therefore under P0-PR-01:

```text
.relay/registry.json advancement required:
NO
```

No living canonical projection is changed by this revision.

---

# 10. Scope and authority check

```text
production code changed:
NO

tests changed:
NO

runtime dependencies changed:
NO

migration implementation started:
NO

GitHub integration implementation started:
NO

Slice 1.2 started:
NO

Slice 1.3 started:
NO

Slice 1.1 implementation authorized:
NO
```

---

# 11. Independent design-review questions for Revision 2

The reviewer should determine:

```text
Q1  Does F001 routing preserve project isolation while handling app-level webhooks?
Q2  Does the reverse lookup remain minimum sufficient architecture?
Q3  Does access readiness close unsuspend/permission-drift fail-open paths?
Q4  Is ACTIVE / READY the correct sole usability condition?
Q5  Does durable PERMISSION_POLICY_VIOLATION preserve security evidence correctly?
Q6  Does state_revision fully prevent stale sync from overwriting newer webhook state?
Q7  Are per-project webhook transactions preferable to cross-project atomicity?
Q8  Is delivery_digest independent of later state and deterministic?
Q9  Is (project_id, delivery_id) the correct idempotency identity under fanout?
Q10 Are repository add/remove semantics fail-closed and convergent?
Q11 Is 403 classification precedence sufficient?
Q12 Do the additions remain within Slice 1.1 and Minimum Sufficient Architecture?
Q13 Are F001–F004 fully resolved without architecture escalation?
```

Allowed review outcomes:

```text
ACCEPT
REVISE
ESCALATE
```

---

# 12. Hard stop

```text
Slice 1.1 Design Revision 2:
COMPLETE / PENDING INDEPENDENT DESIGN REVIEW

Slice 1.1 implementation:
NOT AUTHORIZED

Slice 1.2:
NOT OPEN / NOT AUTHORIZED
```

STOP.
