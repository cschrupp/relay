# Slice 1.1 — GitHub App Integration Memory

**Status:** COMPLETE / ACCEPTED
**Record state:** LOCKED
**Phase:** 1
**Slice:** 1.1
**Accepted design head:** `0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b`
**Accepted technical implementation:** `ae79b15170c88e776af99944eab9b2fdd6872c2e`
**Human acceptance:** `RLY-S11-ACCEPT-001`

## Authority chain

```text
RLY-P0-PROTOCOL-ACCEPT-001
        ↓
RLY-P1-OPEN-001
        ↓
RLY-S11-DESIGN-AUTH-001
        ↓
Design Revision 1
d73daf2ab2a850a4762084e042fa496f7a377e99
        ↓
RLY-S11-DESIGN-EVAL-001 — REVISE
F001–F004
        ↓
Design Revision 2 amendment
0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b
        ↓
RLY-S11-DESIGN-EVAL-002 — ACCEPT
        ↓
RLY-S11-DESIGN-ACCEPT-001
        ↓
RLY-S11-AUTH-001
        ↓
Slice 1.1 implementation
```

## Design findings

```text
RLY-S11-DREV1-F001 — RESOLVED
webhook installation→project routing

RLY-S11-DREV1-F002 — RESOLVED
durable readiness / permission-policy state

RLY-S11-DREV1-F003 — RESOLVED
state revision / optimistic concurrency

RLY-S11-DREV1-F004 — RESOLVED
semantic delivery digest / idempotency
```

## Implementation summary

Implemented provider-specific package:

```text
src/relay_engine/integrations/github/
```

with:

```text
auth
client
errors
models
service
store
webhooks
```

Implemented behavior includes:

- RS256 GitHub App JWT creation with explicit time;
- short-lived, non-persisted installation tokens;
- pinned read-only GitHub REST calls through a narrow transport seam;
- strict external JSON typing/validation;
- project-scoped installation/repository state;
- status/readiness separation and fail-closed permission policy;
- explicit Relay `RepositoryId` → `RepositoryRef` conversion;
- migration v2 and schema verification;
- atomic full repository-set replacement;
- per-binding monotonic state revisions;
- stale-sync concurrency conflict;
- raw-body HMAC webhook verification;
- deterministic semantic delivery digests;
- project-scoped webhook idempotency;
- app-level webhook fanout to existing project bindings only;
- immutable integration events.

## Dependency change

Authorized new runtime dependency:

```text
PyJWT[crypto]
```

Frozen resolution at the technical checkpoint includes:

```text
PyJWT 2.15.0
cryptography 50.0.1
```

No full GitHub SDK or provider plugin framework was added.

## Quality evidence

Exact technical checkpoint:

```text
92a65728ab66ededed86d134a845a93fe58ad01d
```

GitHub Actions:

```text
Run:
36338324389

Environment sync:
PASS

Ruff format:
PASS

Ruff lint:
PASS

Pyright:
PASS — 0 errors

pytest:
PASS — 405 passed

build:
PASS
```

The final candidate SHA `ae79b15170c88e776af99944eab9b2fdd6872c2e` also passed GitHub Actions run `36338853536` on `slice/1.1-github-app-integration`; environment sync, Ruff format/lint, Pyright, tests, and build all succeeded.

## Scope boundaries preserved

Not implemented:

```text
Slice 1.2 repository registration/baseline resolution
Slice 1.3 remote .relay initialization/sync
GitHub contents writes
branch creation
commit creation
pull requests
user OAuth
generic provider framework
agent execution
```

## Accepted state and registry advancement

Acceptance finalization advances the registered `current-baseline` projection from `art_018f47c1-7b2c-7abc-8def-123456789117` revision 5 to `art_018f47c1-7b2c-7abc-8def-123456789119` revision 6. Its exact-byte digest is `sha256:8b84cc3880e6a86940a374cc62d93025b96ee24c92d78143b23b664eb887e9d6` (`updated_at: 2026-09-27T18:56:13Z`); the other four records and canonical pointers are unchanged.

## Accepted state

```text
Implementation:
COMPLETE / ACCEPTED

ADR-0007:
LOCKED / ACCEPTED

Memory:
LOCKED / ACCEPTED

Slice 1.2:
NOT OPEN / NOT AUTHORIZED
```

Human Authority accepted the exact Slice 1.1 result `ae79b15170c88e776af99944eab9b2fdd6872c2e` under `RLY-S11-ACCEPT-001`. This memory is now locked; future correction must follow Documentation Governance amendment or supersession rules.
