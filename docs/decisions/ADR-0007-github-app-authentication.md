# ADR-0007 — GitHub App Authentication and Installation State

**Status:** LOCKED / ACCEPTED
**Decision date:** 2026-09-27
**Authority:** Slice 1.1 Design Revision 1 plus accepted Revision 2 amendment
**Accepted design head:** `0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b`
**Independent design evaluation:** `RLY-S11-DESIGN-EVAL-002` — ACCEPT
**Human design acceptance:** `RLY-S11-DESIGN-ACCEPT-001`
**Implementation authorization:** `RLY-S11-AUTH-001`
**Accepted implementation result:** `ae79b15170c88e776af99944eab9b2fdd6872c2e`
**Human implementation acceptance:** `RLY-S11-ACCEPT-001`

## Context

Relay needs GitHub repository visibility without adding provider-specific fields to its accepted domain model, persisting credentials, or granting write authority before later slices need it. External installation lifecycle events also have to converge safely with explicit synchronization so stale cached authorization cannot become usable.

## Decision

1. Isolate GitHub behavior in `relay_engine.integrations.github`; leave accepted provider-neutral domain semantics unchanged.
2. Authenticate through a GitHub App, not a PAT fallback. Use RS256 app JWTs and short-lived installation access tokens.
3. Keep private keys, webhook secrets, JWTs, and installation tokens ephemeral. Persist only validated non-secret provider/access state.
4. Limit Slice 1.1 to repository metadata read and contents read. Persist a fail-closed policy-violation state for broader grants.
5. Use `ProjectId` as the current isolation boundary and `(project_id, installation_id)` as the durable binding key.
6. Separate provider installation status from Relay access readiness; repository use requires `ACTIVE / READY` plus valid policy.
7. Add SQLite migration v2 with installation state, current repository access, immutable events, and a monotonic state revision used for optimistic concurrency.
8. Verify GitHub webhook HMAC before parsing, normalize supported semantic events, and persist deterministic delivery evidence keyed by project and delivery ID.
9. Route app-level installation webhooks only to existing project bindings; webhooks never create projects or bindings.
10. Require an explicit Relay `RepositoryId` when converting current GitHub repository identity to `RepositoryRef`.
11. Add `PyJWT[crypto]` as the sole new runtime dependency required for standards-compliant RS256 signing; do not add a full GitHub SDK.

## Consequences

Relay can reason deterministically about which GitHub installation/repositories are currently safe for read use while keeping secrets outside repository/runtime engineering state and preserving the Phase-0 domain boundary. Revocation and restrictive provider evidence are fail-closed, and stale synchronization cannot overwrite newer security state.

Repository registration, ref resolution, immutable baseline proof, `.relay/` writes, repository mutation, user OAuth, and generic provider abstractions remain deferred.

## Acceptance state

```text
Accepted implementation result: ae79b15170c88e776af99944eab9b2fdd6872c2e
Human implementation acceptance: RLY-S11-ACCEPT-001
Decision state: LOCKED / ACCEPTED
```
