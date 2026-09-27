# GitHub App Integration — Slice 1.1

**Status:** IMPLEMENTED / PENDING INDEPENDENT EVALUATION  
**Authority:** Slice 1.1 Design Revision 1 plus accepted Revision 2 amendment  
**Accepted design head:** `0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b`  
**Scope:** Read-only GitHub App authentication, installation discovery, project-scoped access state, and signed installation webhooks

## Purpose

Slice 1.1 gives Relay a provider-specific GitHub connection boundary without changing the accepted provider-neutral domain model. The integration can authenticate as a GitHub App, synchronize one installation, discover its current readable repositories, enforce Relay's read-only permission policy, process signed installation lifecycle webhooks, and convert a currently usable GitHub repository into an explicit `RepositoryRef` when the caller supplies the Relay `RepositoryId`.

It does not register the repository as project authority, resolve refs or baselines, write `.relay/`, mutate GitHub repositories, or execute agents.

## Package boundary

GitHub-specific behavior lives under:

```text
src/relay_engine/integrations/github/
    __init__.py
    auth.py
    client.py
    errors.py
    models.py
    service.py
    store.py
    webhooks.py
```

The accepted generic `Project`, `RepositoryRef`, `CommitRef`, `Artifact`, `Baseline`, and `Slice` semantics are unchanged.

## Authentication and secrets

`create_app_jwt` signs RS256 GitHub App JWTs using an explicit current time. Private-key material, webhook secrets, app JWTs, and installation access tokens remain ephemeral masked values and are never written to SQLite, `.relay/`, integration events, or normal error text.

Installation tokens are minted for a high-level operation only. Repository-specific token requests use the selected provider repository ID and read-only contents permission.

The implementation adds the accepted `PyJWT[crypto]` runtime dependency and uses Python's standard-library HTTP stack behind one small deterministic transport protocol.

## Provider validation

Remote JSON is treated as untrusted `object` data. The GitHub client and webhook parser establish explicit typed mapping/list boundaries and validate provider integers, strings, booleans, enums, permissions, repository identities, and supported webhook actions before constructing typed values or persisting state.

Every REST request uses the configured public API base, pinned API version, Relay user agent, and appropriate ephemeral bearer credential. HTTP `403` rate-limit evidence is classified before ordinary permission denial.

## Durable state

SQLite migration v2 adds:

```text
github_installations
github_installation_repositories
github_installation_events
```

Each installation binding is scoped by:

```text
(project_id, installation_id)
```

and carries a monotonic `state_revision`.

Provider status and Relay authorization readiness are distinct:

```text
provider status:
ACTIVE / SUSPENDED / DELETED

Relay readiness:
READY / RESYNC_REQUIRED / PERMISSION_POLICY_VIOLATION
```

Repository use requires the binding to be `ACTIVE`, `READY`, and within the accepted permission policy.

A successful full synchronization atomically advances current installation state, replaces the complete repository-access set, advances `state_revision`, and records an immutable integration event. A stale synchronization cannot overwrite a newer webhook mutation because its expected revision no longer matches.

## Permission policy

Slice 1.1 is read-only. The allowed ceiling is repository metadata read and repository contents read. A structurally valid broader observed grant becomes durable `PERMISSION_POLICY_VIOLATION` evidence rather than leaving an older `READY` state usable.

Suspension/deletion and repository-removal evidence may restrict access immediately. Unsuspension, repository additions, and other positive/broadening signals never restore `READY` without authoritative synchronization.

## Webhooks

Webhook processing verifies `X-Hub-Signature-256` against the exact raw request bytes before JSON parsing. Supported events require both `X-GitHub-Event` and `X-GitHub-Delivery`.

The validated semantic envelope is deterministically hashed using canonical JSON. Durable idempotency is project-scoped:

```text
(project_id, delivery_id)
```

Same delivery ID plus same digest is an idempotent no-op. Reuse of the same project/delivery ID with different semantic content is an integrity error.

GitHub's app-level installation webhook is routed by provider installation ID to all existing Relay project bindings. The dispatcher cannot fabricate a project or create a new project-installation binding.

## RepositoryRef conversion

GitHub repository identity remains provider-specific metadata. Conversion requires an explicit caller-supplied Relay `RepositoryId`; no Relay identity is derived from GitHub numeric IDs.

The conversion is usable only for a repository in the binding's confirmed current access set while the installation is `ACTIVE / READY`. The public adapter emits:

```text
host = github.com
path = owner/repository
```

Actual project repository registration and immutable baseline resolution remain Slice 1.2 work.

## Error contract

The package exposes a narrow GitHub integration error family covering authentication, permission denial, policy violation, rate limiting, remote/protocol failure, unavailable installations, repository access denial, webhook validation, durable integrity failure, and optimistic-concurrency conflict.

Provider error details are bounded so credentials are not reflected into normal errors.

## Deliberate exclusions

Slice 1.1 contains no user OAuth flow, GitHub write permission, repository registration, Git ref/baseline resolution, `.relay/` remote sync, branch/commit/PR mutation, generic provider framework, background worker system, UI, or agent execution.
