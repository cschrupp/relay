# Slice 1.1 — GitHub App Integration Memory

**Status:** IMPLEMENTATION COMPLETE / PENDING INDEPENDENT EVALUATION  
**Record state:** WORKING / NOT LOCKED  
**Phase:** 1  
**Slice:** 1.1  
**Accepted design head:** `0cf5436021eeef45f5e6d9fc20fe6dcf76e0a19b`  
**Technical implementation checkpoint:** `92a65728ab66ededed86d134a845a93fe58ad01d`

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

## Candidate state

```text
Implementation:
COMPLETE / PENDING INDEPENDENT EVALUATION

ADR-0007:
PROPOSED / VALIDATED / PENDING ACCEPTANCE

Memory:
WORKING / NOT LOCKED

Slice 1.2:
NOT OPEN / NOT AUTHORIZED
```

This record must not be locked until Human Authority accepts an independently evaluated Slice 1.1 implementation result.
