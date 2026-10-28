# Relay Dogfood 001 — Source Coverage 004 Human Acceptance

**Document class:** Immutable Human acceptance record  
**Status:** IMMUTABLE / ACCEPTED  
**Date:** 2026-10-28  
**Record:** `RLY-S31-DOGFOOD-001-SOURCE-COVERAGE-ACCEPT-001 — ACCEPTED`

## Human decision

The Human accepts only the exact Dogfood 001 source-coverage declaration
identified below. This acceptance records the bounded completeness assertion
for the exact requested outcome and scope. It does not accept a global
inventory of Relay history.

```text
source_key: dogfood-001-source-coverage-004
logical_digest: sha256:3974a5c6516ef2d26cd0b6a13f9331712751ca719b911e29499fcd6f7cfd1a9d
registered_file_digest: sha256:f2c6d519ea45c06125f5a835e319551d50e12f355249aa288bdb480d08ae181d
outcome: deterministic-dependency-resolution
scope: dogfood-001
```

The accepted declaration's completeness assertions mean complete for deciding
authority eligibility for the exact Dogfood 001 requested outcome and scope.
They do not claim a complete inventory of all Relay history.

## Scope and non-authority

This decision accepts the exact source-coverage declaration above. It does
not issue or refresh an execution grant, authorize reservation mutation or
consumption, materialize a WorkPacket or WorkspacePlan, provision a workspace,
qualify a concrete backend, establish fixture reachability, admit a runtime or
prompt, authorize credential access or provider/model calls, or authorize
Dogfood execution.

The historical AuthorityCandidate remains bound to its historical snapshot
and is not made current by this acceptance. The historical execution grant is
not rebound or refreshed. A fresh post-acceptance source snapshot and actual
resolver/compiler evaluation are required. Any resulting AuthorityCandidate
requires a separate exact Human execution-authority decision before any
admission.

**Disposition:** `ACCEPTED`
