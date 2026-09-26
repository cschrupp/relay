# Slice 1.1 — GitHub App Integration

**Document revision:** 1  
**Status:** REVIEW  
**Document class:** Lockable design record  
**Phase:** 1 — GitHub and Human-Controlled Project Workflow  
**Slice:** 1.1  
**Authorized baseline:** `cb9edc453442dc639a523ef301e4a258d0394daa`  
**Protocol review:** `RLY-P0-PROTOCOL-REVIEW-001` — ACCEPTED by Human Authority  
**Phase-1 opening:** `RLY-P1-OPEN-001`  
**Design authorization:** `RLY-S11-DESIGN-AUTH-001`  
**Reviewer next:** Independent Design Reviewer — GPT-5.6 Sol  
**Implementation:** NOT AUTHORIZED  
**Date:** 2026-09-26

---

# 1. Objective

Connect Relay securely to selected GitHub repositories through a GitHub App without weakening the provider-neutral Phase-0 contracts.

Slice 1.1 establishes only the provider-specific connection boundary needed to:

- authenticate Relay as a GitHub App;
- identify and synchronize an app installation;
- discover repositories currently accessible to that installation;
- inspect the installation permission grant;
- validate a selected repository is actually accessible;
- map current GitHub repository identity into an explicit provider-neutral `RepositoryRef`;
- detect installation suspension, deletion, repository-access changes, and relevant permission changes;
- persist non-secret installation/access state and immutable integration events;
- verify signed GitHub App webhooks;
- provide deterministic errors and auditable evidence.

Slice 1.1 does **not** register a repository as authoritative Relay project state, resolve refs to commit SHAs, initialize `.relay/`, mutate repositories, or execute agents.

---

# 2. Governing Phase-0 contracts

Slice 1.1 must preserve the following accepted behavior.

## 2.1 Provider-neutral repository identity

`RepositoryRef` remains:

```python
RepositoryRef(
    id: RepositoryId,
    host: str,
    path: str,
)
```

It remains credential-free and provider-neutral.

GitHub installation IDs, GitHub repository numeric IDs, node IDs, permission names, API URLs, and webhook payloads MUST NOT be added to `RepositoryRef` or other accepted generic domain values.

## 2.2 Explicit identity creation

Relay IDs remain explicit call-site values.

The GitHub adapter may observe GitHub's own stable numeric repository ID, but it MUST NOT silently derive a Relay `RepositoryId` from it.

## 2.3 Runtime secrets are not repository authority

`.relay/` is authoritative for repository artifact semantics and canonical pointers.

It is not a credential store.

GitHub App private keys, webhook secrets, app JWTs, and installation access tokens MUST NOT be written to:

- `.relay/`;
- project documents;
- SQLite engineering-state payloads;
- integration metadata tables;
- logs or audit event payloads.

## 2.4 Persistence behavior

Slice 0.5 migration checksums, contiguous history, atomic pending batches, and post-apply physical schema verification remain mandatory.

New GitHub integration tables use the existing persistence migration mechanism rather than introducing a second database framework.

## 2.5 Protocol-review amendments

P0-PR-01 through P0-PR-04 are in force.

In particular, registered living-projection changes require registry preflight, and design acceptance remains distinct from implementation authorization.

---

# 3. External GitHub facts used by this design

Current GitHub App behavior relevant to Slice 1.1:

1. GitHub Apps have no permissions by default; the app should request only the minimum permissions required.
2. App authentication uses an RS256-signed JWT.
3. The app JWT expires within at most ten minutes.
4. Installation access tokens are short-lived and currently expire after one hour.
5. Installation token permissions/repository access can be narrowed below the installation's grant.
6. GitHub Apps receive installation and installation-repository lifecycle signals.
7. Repository access can be limited to selected repositories.
8. User authorization of the GitHub App is separate from installation and is not required for the app to act as the installation.

Reference documentation:

- GitHub Docs — Generating a JSON Web Token (JWT) for a GitHub App
- GitHub Docs — REST API endpoints for GitHub Apps
- GitHub Docs — Choosing permissions for a GitHub App
- GitHub Docs — Webhook events and payloads
- GitHub Docs — Differences between GitHub Apps and OAuth apps

The implementation MUST treat provider response fields as external input and validate them before persistence.

---

# 4. Design decisions

## P1-D01 — Provider-specific package boundary

GitHub-specific behavior lives under:

```text
src/relay_engine/integrations/github/
```

Expected minimum package:

```text
__init__.py
auth.py
client.py
errors.py
models.py
service.py
store.py
webhooks.py
```

A smaller file split is acceptable if responsibilities remain obvious.

Do NOT add GitHub fields to `relay_engine.domain`.

Do NOT introduce a generic multi-provider repository-integration framework in Slice 1.1.

The first concrete provider should prove the required seam before generalization.

---

## P1-D02 — Core domain models remain unchanged

Slice 1.1 requires no semantic change to:

```text
Project
RepositoryRef
CommitRef
Artifact
Baseline
Slice
```

Narrow import/export changes are permitted only if implementation needs existing accepted types.

Any implementation discovery that appears to require changing provider-neutral repository semantics is an architecture escalation.

---

## P1-D03 — GitHub App, not PAT, is the primary architecture

Relay authenticates repository access through a GitHub App.

Personal access tokens are not a fallback architecture.

OAuth/user access tokens are out of scope for Slice 1.1.

A later product onboarding layer may introduce a user authorization flow if needed for user-specific installation discovery, but Slice 1.1 does not depend on it.

---

## P1-D04 — Required app permission policy is read-only

The Slice 1.1 GitHub App permission ceiling is:

```text
Repository metadata: read
Repository contents: read
```

No repository write permission is authorized.

No organization-level permission is authorized.

No account/user permission is authorized.

No Actions/workflows write permission is authorized.

No Issues/PR/checks/deployments permission is authorized.

If the observed installation grant contains a provider permission above the Slice 1.1 allowed ceiling, Relay classifies the connection as `PERMISSION_POLICY_VIOLATION` and does not use it.

A later slice that requires writes must explicitly redesign and obtain the additional permission.

---

## P1-D05 — Runtime app configuration

Non-secret operational configuration may include:

```text
GitHub App client ID / JWT issuer
GitHub API base URL
GitHub REST API version
user agent
request timeout
```

The default public GitHub API base is:

```text
https://api.github.com
```

The initial pinned REST API version is:

```text
2026-03-10
```

These values are operational configuration, not project engineering state.

---

## P1-D06 — Secret input boundary

Runtime credentials are represented only as ephemeral secret values supplied to the GitHub integration composition boundary.

Required secret values:

```text
GitHub App private key PEM
GitHub webhook secret
```

They MUST use masked secret types such as `pydantic.SecretStr` or an equivalent value that does not expose the secret through normal representation.

Slice 1.1 does not create an encrypted-secret database.

For local/test execution, secrets may be injected by process environment or test fixtures.

For deployed environments, the caller/deployment is responsible for supplying those values from an encrypted external secret store.

Relay MUST NOT persist the secret material after process startup.

---

## P1-D07 — App JWT generation

App JWT creation is deterministic given:

```text
client/issuer ID
private key
explicit current time
```

JWT requirements:

```text
algorithm: RS256
iat: explicit now minus 60 seconds
exp: no more than 10 minutes after now
iss: configured GitHub App client/issuer ID
```

JWT generation must accept an explicit/injected clock for tests.

The JWT itself is ephemeral and MUST NOT be persisted or logged.

---

## P1-D08 — JWT crypto dependency

Slice 1.1 may add:

```text
PyJWT[crypto]
```

as the single new runtime dependency required for standards-compliant RS256 signing.

The exact bounded compatible version is chosen during implementation and recorded in `pyproject.toml` / `uv.lock`.

Do NOT implement custom RSA/JWT cryptography.

Do NOT add a full GitHub SDK merely to avoid implementing the narrow REST calls required here.

---

## P1-D09 — HTTP transport seam

The GitHub package defines one small transport seam for deterministic tests.

Conceptually:

```python
class GitHubTransport(Protocol):
    def request(self, request: GitHubRequest) -> GitHubResponse: ...
```

The production implementation uses Python standard-library HTTPS facilities.

The seam exists only to:

- avoid live network calls in unit tests;
- make status/header/body behavior deterministic;
- keep authentication/client logic testable.

It is NOT a generic provider plugin framework.

---

## P1-D10 — Required request headers

Every GitHub REST call sends:

```text
Accept: application/vnd.github+json
X-GitHub-Api-Version: configured pinned version
User-Agent: configured Relay user agent
Authorization: Bearer <ephemeral credential>
```

JWT-authenticated app calls and installation-token calls use the credential appropriate to the endpoint.

Response request IDs and rate-limit headers may be captured as non-secret diagnostic evidence.

Authorization headers MUST be redacted from all logs/errors.

---

## P1-D11 — Installation access token lifecycle

Installation tokens are minted only after Relay has an explicit installation ID.

Installation tokens:

- are never stored in SQLite;
- are never written to `.relay/`;
- are never serialized into audit events;
- are never logged;
- are considered expired at or before the provider expiration;
- may be held in memory only for the duration of one high-level operation in Slice 1.1.

Slice 1.1 does not introduce a shared token cache.

For repository-specific reads, Relay requests the narrowest available token scope for the chosen repository and read-only permissions.

---

## P1-D12 — Installation state model

Provider-specific immutable values include the equivalent of:

```python
GitHubInstallationSnapshot(
    project_id: ProjectId,
    installation_id: int,
    app_id: int,
    account_id: int,
    account_login: str,
    account_type: GitHubAccountType,
    repository_selection: GitHubRepositorySelectionMode,
    status: GitHubInstallationStatus,
    permissions: tuple[GitHubPermissionGrant, ...],
    observed_at: datetime,
)
```

Statuses:

```text
ACTIVE
SUSPENDED
DELETED
```

`DELETED` is a retained tombstone state, not row deletion.

All provider strings/integers are validated and normalized only where GitHub semantics explicitly require it.

---

## P1-D13 — Permission snapshot model

Permissions are represented as sorted explicit entries, not an untyped dictionary:

```python
GitHubPermissionGrant(
    name: str,
    level: GitHubPermissionLevel,
)
```

Allowed levels reflect provider values needed by the integration:

```text
READ
WRITE
ADMIN
```

Unknown permission names may be retained as provider-specific strings so Relay can detect an unexpected/broader grant instead of silently discarding it.

Canonical ordering:

```text
permission name ASC
```

The permission-policy validator compares the observed grant to the exact Slice 1.1 allowed ceiling.

---

## P1-D14 — Repository access snapshot

Accessible repositories are represented with provider-specific identity:

```python
GitHubRepositorySnapshot(
    github_repository_id: int,
    node_id: str,
    full_name: str,
    owner_login: str,
    private: bool,
    archived: bool,
    default_branch: str,
    observed_at: datetime,
)
```

`full_name` must identify exactly:

```text
owner/repository
```

No credentials or clone URLs are persisted.

The GitHub numeric repository ID is provider identity only.

It does not replace Relay `RepositoryId`.

---

## P1-D15 — Project-scoped isolation

Until Relay has an Organization/Tenant model, the accepted `ProjectId` is the Slice 1.1 isolation boundary.

Every persisted installation and accessible-repository row is scoped by:

```text
project_id
+
installation_id
```

Store APIs always require `ProjectId`.

A repository/installation observed for project A must not become queryable through project B merely because the external installation ID is the same.

This is the minimum current isolation rule and does not claim to solve later organization tenancy.

---

## P1-D16 — Persistence migration v2

Slice 1.1 adds exactly one next migration through the accepted migration mechanism.

Required current-state tables are conceptually:

```text
github_installations

github_installation_repositories
```

Required immutable integration history:

```text
github_installation_events
```

The migration must:

- be version 2;
- have a deterministic checksum;
- extend `DEFAULT_MIGRATIONS`;
- extend physical schema verification;
- preserve contiguous applied migration history;
- be applied atomically with any later pending migration batch.

No ORM is introduced.

---

## P1-D17 — Installation current-state persistence

`github_installations` stores only non-secret provider state.

Logical key:

```text
(project_id, installation_id)
```

Payload includes the exact validated `GitHubInstallationSnapshot`.

Updates use semantic optimistic replacement inside a transaction.

A `DELETED` installation remains as a tombstone so a stale callback or repository selection cannot resurrect it implicitly.

Reactivation after deletion requires a newly observed valid installation state through explicit synchronization.

---

## P1-D18 — Repository-access persistence

`github_installation_repositories` stores the current complete accessible-repository set for one project-scoped installation.

A successful full synchronization replaces the current set transactionally.

Relay MUST NOT partially replace the set if pagination/API retrieval fails before completion.

For `SUSPENDED` installations, the last known set may remain stored but MUST be considered unavailable for authorization/use.

For `DELETED` installations, the current accessible set is removed in the same transaction that records deletion.

Historical access changes remain represented by immutable integration events.

---

## P1-D19 — Immutable GitHub integration events

State-changing observations produce immutable events equivalent to:

```python
GitHubInstallationEvent(
    event_id: str,
    project_id: ProjectId,
    installation_id: int,
    event_type: GitHubInstallationEventType,
    observed_at: datetime,
    delivery_id: str | None,
    prior_state_digest: str | None,
    resulting_state_digest: str,
)
```

Initial event vocabulary:

```text
INSTALLATION_SYNCED
PERMISSIONS_CHANGED
REPOSITORIES_CHANGED
SUSPENDED
UNSUSPENDED
DELETED
```

The event records provider state transition evidence, not credentials or full HTTP authorization material.

Event IDs are explicit inputs or explicitly generated by the integration call site; no hidden clock/ID generation occurs inside model validation.

---

## P1-D20 — Installation synchronization service

Primary command:

```python
synchronize_installation(
    *,
    project_id: ProjectId,
    installation_id: int,
    observed_at: datetime,
    ...
) -> GitHubInstallationSnapshot
```

Required sequence:

```text
create short-lived app JWT
        ↓
GET installation metadata
        ↓
validate app identity / installation state
        ↓
create short-lived installation token
        ↓
list all installation repositories with pagination
        ↓
validate exact permission policy
        ↓
validate repository payloads
        ↓
transactionally persist current state + event
```

No persistence change occurs until all required remote reads and validation succeed.

---

## P1-D21 — Repository selection and RepositoryRef conversion

Slice 1.1 supports selecting one currently accessible repository but does not yet register it as the project's authoritative repository.

Pure conversion/validation API:

```python
repository_ref_from_github(
    *,
    relay_repository_id: RepositoryId,
    installation: GitHubInstallationSnapshot,
    repository: GitHubRepositorySnapshot,
) -> RepositoryRef
```

Requirements:

- installation must be `ACTIVE`;
- repository must belong to the exact current accessible set for the same project/installation;
- host is exactly `github.com` for the public GitHub adapter;
- path is exactly the validated current GitHub `full_name`;
- Relay `RepositoryId` is explicit caller input.

Persisting project repository registration is deferred to Slice 1.2.

Resolving branch/tag/SHA is deferred to Slice 1.2.

---

## P1-D22 — Webhook signature verification

Webhook verification uses:

```text
X-Hub-Signature-256
```

and HMAC-SHA256 over the exact raw request body using the runtime webhook secret.

Verification uses constant-time comparison.

The webhook body is parsed only after signature verification succeeds.

Missing/invalid signature is rejected without persistence.

---

## P1-D23 — Webhook events in scope

Slice 1.1 handles only the installation/access events needed to keep connection state valid:

```text
installation
installation_repositories
```

Relevant actions include:

```text
created
new_permissions_accepted
suspend
unsuspend
deleted
added
removed
```

Provider payload actions not recognized by the accepted parser are rejected or explicitly ignored without state mutation according to the event contract.

No push, pull_request, issues, checks, workflow, or code-content webhook processing is implemented.

---

## P1-D24 — Webhook idempotency

`X-GitHub-Delivery` is treated as the provider delivery identity.

A successfully applied delivery ID is persisted with the immutable integration event.

Re-delivery of the same delivery ID with the same validated semantic event is idempotent.

The same delivery ID carrying conflicting semantic content is an integrity error.

No webhook event can bypass project scoping.

---

## P1-D25 — Webhook state behavior

A valid installation webhook may update local state without an immediate full resync only where the payload is sufficient to prove the state transition.

Examples:

```text
suspend   → mark SUSPENDED
unsuspend → mark ACTIVE, then require/trigger explicit resync before repository use
deleted   → mark DELETED and remove current repo-access rows
```

Repository added/removed events update access state only from validated payload identities and generate an immutable event.

Before an installation/repository is used after any ambiguous or stale condition, explicit synchronization is authoritative.

---

## P1-D26 — Revocation/staleness detection

Relay must detect loss of access through both:

1. validated GitHub installation webhooks; and
2. explicit synchronization/API failure.

Rules:

- a `DELETED` webhook creates a tombstone;
- a `SUSPENDED` webhook blocks use immediately;
- installation lookup `404` during explicit synchronization is classified as unavailable and may transition the known installation to `DELETED` only through the synchronization service's explicit classification path;
- authentication failures do not silently classify the installation as deleted;
- repository-specific `404` does not by itself delete the installation;
- insufficient permission is distinct from authentication failure;
- rate limiting is distinct from permission failure.

---

## P1-D27 — Failure taxonomy

Narrow provider-specific error family:

```text
GitHubIntegrationError
├── GitHubAuthenticationError
├── GitHubInstallationUnavailable
├── GitHubPermissionError
├── GitHubRepositoryAccessDenied
├── GitHubRateLimited
├── GitHubWebhookInvalid
├── GitHubRemoteError
└── GitHubIntegrationIntegrityError
```

Errors may carry non-secret context such as:

```text
HTTP status
GitHub request ID
installation ID
repository numeric ID
```

Errors MUST NOT carry:

```text
Authorization header
JWT
installation token
private key
webhook secret
```

---

## P1-D28 — Retry policy

Slice 1.1 implements no hidden automatic retry loop.

Callers receive typed failures.

This avoids introducing retry/backoff policy before Relay has an operational execution layer.

Pagination is part of one explicit synchronization operation and is not considered retry.

A later operational layer may add bounded retry policy.

---

## P1-D29 — Logging and redaction

Structured logs may include:

```text
project_id
installation_id
GitHub repository numeric ID
GitHub request ID
operation
result/error class
```

They MUST redact or omit:

```text
private key
webhook secret
JWT
installation access token
Authorization header
raw signed webhook signature
```

The implementation must include a regression proving secrets supplied to failure paths do not appear in exception text or captured logs.

---

## P1-D30 — No repository mutation

Slice 1.1 GitHub client exposes only the remote operations required for:

```text
app/installation identity reads
installation-token creation
installation repository listing
repository metadata/content reads needed to prove selected access
```

It MUST NOT expose or call:

```text
create/update/delete repository content
create branch/ref
delete ref
merge
create/update PR
create issue
push
workflow mutation
repository settings mutation
installation suspension/unsuspension
```

Even if GitHub's API supports those operations.

---

## P1-D31 — Content access boundary

`Contents: read` is authorized only so Slice 1.1 can prove selected repository read access and support subsequent Slice 1.2/1.3 designs.

Slice 1.1 does not clone repositories or interpret `.relay/` content through GitHub.

Repository contract validation remains filesystem/snapshot based until a later integration design explicitly connects these layers.

---

## P1-D32 — No user OAuth in the first installation path

The first accepted application service assumes the installation ID is supplied by an outer setup/callback boundary.

It then validates that installation using app authentication.

There is no persisted GitHub user token and no `github_app_authorization` state in Slice 1.1.

If product onboarding later requires "show installations accessible to this signed-in user," that capability receives its own design/authorization.

---

## P1-D33 — Testing strategy

Unit and persistence tests use a fake/in-memory GitHub transport.

CI MUST NOT require a real GitHub App, private key, webhook endpoint, or internet access.

Required deterministic tests include:

- JWT claims and no-secret representations;
- app-auth vs installation-auth header selection;
- exact API-version header;
- installation-token non-persistence;
- permission ceiling;
- pagination;
- atomic repository-set replacement;
- failure rollback;
- project isolation;
- suspended/deleted blocking;
- webhook HMAC verification;
- webhook delivery idempotency;
- repository add/remove;
- full `RepositoryRef` conversion;
- API error classification;
- log/error secret redaction;
- migration v1→v2 and fresh v2;
- migration tamper detection;
- restart reconstruction from persisted integration state.

Optional live GitHub integration tests are not part of Slice 1.1 acceptance.

---

## P1-D34 — Implementation change surface

Expected production change surface:

```text
src/relay_engine/integrations/
src/relay_engine/integrations/github/
src/relay_engine/persistence/migrations.py
src/relay_engine/settings.py               # non-secret operational settings/doc cleanup only if required
pyproject.toml
uv.lock
```

Expected tests:

```text
tests/unit/test_github_*.py
tests/unit/test_persistence*.py             # narrow migration/store additions
```

Required documentation:

```text
docs/architecture/GITHUB_APP_INTEGRATION.md
docs/decisions/ADR-0007-github-app-authentication.md
docs/slices/SLICE_1_1_GITHUB_APP_INTEGRATION_MEMORY.md
```

No change to accepted generic domain semantics is expected.

---

## P1-D35 — Stale settings docstring cleanup

`relay_engine/settings.py` still says the `.relay/` repository contract belongs to a later authorized slice.

That text is stale after accepted Slice 0.6.

Implementation of Slice 1.1 is authorized to correct that docstring while making any accepted non-secret GitHub operational-setting additions.

No behavior should be introduced solely to justify the cleanup.

---

## P1-D36 — Slice boundary with 1.2

Slice 1.1 ends when Relay can securely and durably answer:

> Which GitHub App installation is connected to this Relay project, which repositories can it currently read, what exact permissions were observed, and is the selected repository still accessible?

Slice 1.2 begins when Relay answers:

> Which provider-neutral repository is registered to the project, and what exact immutable Git commit is the authoritative baseline for work?

Do not merge those contracts.

---

## P1-D37 — Slice boundary with 1.3

Slice 1.1 does not write `.relay/registry.json` through GitHub.

Slice 1.3 owns initialization/synchronization of repository-side Relay artifacts.

Adding `Contents: write` for that work requires a separate accepted permission decision.

---

## P1-D38 — Implementation hard stop

After an independently accepted design, Human Authority may authorize Slice 1.1 implementation only.

Successful Slice 1.1 acceptance does not automatically authorize Slice 1.2.

**Unblocked ≠ authorized.**

---

# 5. Explicit out of scope

Slice 1.1 does not implement:

```text
GitHub user OAuth
GitHub Marketplace billing
GitHub Enterprise Server support
multiple Git providers
generic repository-provider plugin framework
repository registration as project authority
branch/tag/SHA resolution
Git clone/fetch/pull/push
baseline/worktree proof
.relay initialization or synchronization
contents writes
branch/ref creation
commit creation
pull-request creation/review
issues/checks/workflows/deployments
agent execution
model/provider execution
board/UI
REST product API
organization/tenant domain model
cloud secret manager
background workers
automatic retry/backoff workers
polling scheduler
```

GitHub Enterprise Server support requires later design because host/API-base/installation behavior introduces additional provider configuration and authority questions.

---

# 6. Acceptance matrix

## App configuration and authentication

```text
A01  no PAT is accepted as the primary GitHub credential
A02  user OAuth is absent from the Slice 1.1 runtime path
A03  app JWT uses RS256
A04  app JWT iat uses explicit clock with drift allowance
A05  app JWT exp never exceeds GitHub's accepted maximum
A06  JWT issuer uses explicit configured app identity
A07  private key never serializes into persisted state
A08  JWT never serializes into persisted state
A09  installation token never serializes into persisted state
A10  normal repr/logging masks secret values
A11  API base/version/user-agent are explicit non-secret config
A12  HTTP Authorization headers are never included in raised error text
```

## Permission and token scope

```text
A13  allowed provider permission ceiling is explicit and read-only
A14  contents read is required
A15  broader write/admin provider permission is rejected
A16  missing required read permission is rejected
A17  repository-specific token requests are narrowed to selected repo where applicable
A18  installation token expiration is represented explicitly
A19  expired token is never reused
A20  no shared persistent/in-memory token cache exists
```

## Installation identity/state

```text
A21  installation ID is positive and explicit
A22  app/account identity is validated
A23  installation state is ACTIVE/SUSPENDED/DELETED
A24  deleted state is retained as a tombstone
A25  suspended installation cannot be used for repository selection
A26  deleted installation cannot be used for repository selection
A27  project_id scopes every persisted installation lookup
A28  project A cannot read project B installation state
A29  installation snapshot has explicit observed_at
A30  provider permission entries have deterministic ordering
```

## Repository access

```text
A31  GitHub repository numeric ID is retained as provider identity
A32  repository full_name validates owner/repository shape
A33  repository token/clone credentials are not persisted
A34  complete paginated repository set is collected before replacement
A35  partial pagination failure leaves prior set unchanged
A36  successful sync atomically replaces the current repository set
A37  deleted installation removes current repository-access rows
A38  suspended installation repository rows are not considered usable
A39  selected repo must belong to exact project/installation current set
A40  RepositoryRef host is github.com
A41  RepositoryRef path is exact validated full_name
A42  Relay RepositoryId is explicit caller input
A43  no implicit provider-ID→Relay-ID derivation occurs
A44  project repository registration is not persisted in Slice 1.1
A45  branch/tag/SHA resolution is absent
```

## Persistence/audit

```text
A46  migration v2 uses accepted migration/checksum mechanism
A47  migration history remains contiguous
A48  fresh database reaches v2
A49  v1 database upgrades atomically to v2
A50  migration checksum tamper is detected
A51  physical schema verification includes new required tables/indexes
A52  integration state survives restart
A53  state-changing observation emits immutable event
A54  event contains no secret/token material
A55  duplicate conflicting delivery IDs are rejected
A56  identical redelivery is idempotent
A57  state/current rows and event append commit atomically
```

## Webhooks/revocation

```text
A58  missing webhook signature is rejected
A59  invalid HMAC is rejected
A60  raw body is verified before JSON parsing
A61  installation suspend blocks use
A62  installation unsuspend requires valid state before use
A63  installation delete tombstones state and removes current repo access
A64  installation_repositories add/remove updates provider access state
A65  unsupported webhook action cannot silently mutate state
A66  repository-specific 404 cannot silently delete installation
A67  app authentication failure is distinct from installation deletion
A68  permission failure is distinct from authentication failure
A69  rate-limit failure is distinct from permission failure
A70  explicit resync can repair missed/stale webhook state
```

## Scope and quality

```text
A71  no GitHub fields added to accepted core domain models
A72  no GitHub write API operation is implemented
A73  no .relay write/sync API is implemented
A74  no Git clone/fetch/push is implemented
A75  no UI/product HTTP server is introduced
A76  no model-provider/agent execution is introduced
A77  one narrow HTTP test seam; no generic provider framework
A78  PyJWT[crypto] is the only new runtime dependency unless escalated
A79  full existing quality suite remains green
A80  Slice 1.1 memory and ADR are produced
A81  implementation evidence names exact baseline/result SHAs
A82  current/next role+model are stated in substantive handovers
A83  registered living-projection changes include registry advancement
A84  Slice 1.2 remains separately unauthorized at Slice 1.1 acceptance
```

---

# 7. Required regression scenarios

At minimum:

```text
test_github_jwt_uses_rs256_and_explicit_clock
test_github_jwt_secret_not_repr_or_persisted
test_installation_token_not_persisted
test_installation_token_request_scopes_selected_repository
test_permission_policy_accepts_exact_read_only_grant
test_permission_policy_rejects_write_permission
test_permission_policy_rejects_missing_contents_read
test_installation_sync_paginates_before_commit
test_installation_sync_rolls_back_on_partial_pagination_failure
test_installation_state_is_project_scoped
test_suspended_installation_blocks_repository_selection
test_deleted_installation_blocks_repository_selection
test_deleted_installation_removes_current_repository_rows
test_repository_ref_requires_explicit_relay_repository_id
test_repository_ref_uses_exact_github_full_name
test_webhook_rejects_invalid_signature
test_webhook_verifies_raw_body_before_parse
test_webhook_redelivery_is_idempotent
test_webhook_conflicting_delivery_is_integrity_error
test_webhook_suspend_blocks_installation
test_webhook_delete_tombstones_installation
test_webhook_repository_added_and_removed
test_remote_401_is_authentication_error
test_remote_403_permission_is_permission_error
test_remote_rate_limit_is_rate_limited
test_repository_404_does_not_delete_installation
test_migration_v1_to_v2
test_migration_v2_tamper_detection
test_restart_recovers_github_installation_state
test_failure_and_logs_do_not_expose_credentials
```

---

# 8. Independent design-review questions

The independent reviewer should answer:

```text
Q1  Does the design preserve provider-neutral RepositoryRef semantics?
Q2  Is GitHub-specific state isolated tightly enough?
Q3  Is the read-only permission ceiling sufficient and minimal?
Q4  Are app JWT/private-key/token semantics safe and testable?
Q5  Is the secret boundary honest without prematurely building a secret manager?
Q6  Is project_id a sufficient Phase-1 isolation boundary without inventing tenancy?
Q7  Is migration v2 the right persistence boundary?
Q8  Are current-state + immutable-event semantics sufficient for revocation/audit?
Q9  Can webhook and explicit sync converge deterministically?
Q10 Are token/API failures classified without fabricating revocation?
Q11 Is repository selection useful without leaking Slice 1.2 registration/baseline work?
Q12 Does explicit RepositoryId input preserve Relay identity semantics?
Q13 Is the HTTP test seam minimal rather than speculative abstraction?
Q14 Is PyJWT[crypto] justified and narrower than a full GitHub SDK?
Q15 Are all repository-write capabilities genuinely absent?
Q16 Does the design satisfy P0-PR-01 ... P0-PR-04?
Q17 Is any requirement missing for revoked/suspended installation safety?
Q18 Is any part of this design better deferred to Slice 1.2 or 1.3?
```

Reviewer outcomes:

```text
ACCEPT
REVISE
ESCALATE
```

---

# 9. Implementation authorization state

```text
Phase 1:
OPEN

Slice 1.1:
DESIGN AUTHORIZED

Slice 1.1 Design Revision 1:
REVIEW

Slice 1.1 implementation:
NOT AUTHORIZED

Slice 1.2:
NOT OPEN / NOT AUTHORIZED
```

No implementation work may begin until:

1. this design is independently reviewed;
2. Human Authority accepts the reviewed design; and
3. Human Authority separately authorizes Slice 1.1 implementation.

STOP.
