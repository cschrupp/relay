# Relay Slice 3.1 — Trusted Local Execution Profile Implementation Acceptance 001

**Document class:** Immutable Human implementation acceptance record  
**Status:** IMMUTABLE / ACCEPTED  
**Date:** 2026-10-28  
**Record:** `RLY-S31-RUNTIME-NATIVE-PROFILE-IMPL-ACCEPT-001 — ACCEPTED`

## Human decision

Human Authority accepts the exact implementation candidate for the trusted-local execution profile after independent technical review and successful exact-head CI.

This acceptance binds only the following exact subject:

```text
implementation authority:
RLY-S31-RUNTIME-NATIVE-PROFILE-IMPL-AUTH-001 — AUTHORIZED

implementation candidate:
3f6ab5d02ae7cc8e8698e6d99457b72934772fc2

branch at acceptance decision:
implementation/3.1-trusted-local-execution-profile

authorized implementation base:
39bbf7fbbc9873f285efd6305cd7c5a27080be00

independent implementation review:
ACCEPT

review findings:
F001 CLOSED
F002 CLOSED
F003 CLOSED
F004 CLOSED

exact-head CI:
40802597511 — SUCCESS

CI exact candidate:
3f6ab5d02ae7cc8e8698e6d99457b72934772fc2

pull request:
#3 — OPEN / NOT MERGED
```

## Accepted implementation outcome

Human Authority accepts the bounded implementation of:

- authority-bound execution-profile selection for `TRUSTED_LOCAL_EXECUTION` and preserved `RELAY_MANAGED_STRONG_BOUNDARY`;
- exact OpenCode configuration qualification, observer binding, and permission evidence;
- truthful workspace-provider/runtime evidence ownership;
- prompt-free-session failure and cleanup handling;
- immutable/stable candidate capture for independent evaluation;
- fail-closed trusted-local handling of unsupported network/external-effect evidence;
- regression preservation of the existing strong-boundary path.

The accepted implementation contains no new Relay sandbox backend.

## Explicit non-authority

This Human implementation acceptance does **not** authorize:

- merging PR #3;
- canonical promotion to `main`;
- rewriting or rebinding historical Dogfood Execution Authorization 002;
- Dogfood 001 workspace launch or execution;
- OpenCode prompt admission for Dogfood;
- Dogfood credential access;
- Dogfood provider/model calls;
- fixture substitution;
- runtime/provider/model substitution;
- bypassing the fresh Dogfood resolver/compiler/authority sequence required by the accepted design.

Dogfood remains:

`NOT ADMITTED / NOT CONSUMED`

A separate canonical promotion/merge decision is required before this implementation becomes canonical. After canonical promotion, Dogfood must still receive a fresh source snapshot, fresh authority compilation, exact trusted-local qualification/runtime binding, and new Human execution authority before any live execution.

**Disposition:** `IMPLEMENTATION ACCEPTED / PROMOTION NOT AUTHORIZED / DOGFOOD NOT AUTHORIZED`
