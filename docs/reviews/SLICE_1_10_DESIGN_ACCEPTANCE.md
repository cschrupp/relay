# Relay — Slice 1.10 Canonical Source and Promotion Enforcement — Human Design Acceptance

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-12  
**Project:** Relay  
**Slice:** 1.10 — Canonical Source and Promotion Enforcement  
**Record:** `RLY-S110-DESIGN-ACCEPT-001`  
**Decision:** `ACCEPTED`

## 1. Human Authority decision

The Human stated:

> accepted

At the current governance gate, this is recorded as Human acceptance of the exact four-part Slice 1.10 composite design independently accepted by `RLY-S110-DESIGN-EVAL-004`.

This is design acceptance only. It is not implementation authorization.

## 2. Accepted design lineage

```text
Canonical parent:
0a0b415ceafd78401e6fa2cae24c208e0fe82a75

Opening:
RLY-S110-OPEN-001 — OPEN
f02e32d1ca1fbcb751ba6a5d630f33e50bf34a56

Design authority:
RLY-S110-DESIGN-AUTH-001 — AUTHORIZED
dac1557adeca9a1928d442a6f4aea809d8b33a10

Design Revision 1:
f9141f6f44927f2a13b85cce8ffd4501db0b183d

Independent evaluation 001:
RLY-S110-DESIGN-EVAL-001 — REVISE
bc085c53b080ea197afc7ba4409b10c1658f2f40

Design Revision 2 / Rework 1:
6b7f69d69da90879fd536b2edbbaad6d6f3da8c7

Independent evaluation 002:
RLY-S110-DESIGN-EVAL-002 — REVISE
9881d72911d2ce2e5aad66c90881ecba3255b8b7

Design Revision 3 / Rework 2:
28e7f2d1e69a912ed98423e9ae78d932d2cda849

Independent evaluation 003:
RLY-S110-DESIGN-EVAL-003 — REVISE
e51f73e151aa0c454a612575e95f59fee88fddb0

Design Revision 4 / Rework 3:
60dced8e88ae8d0d8e69e2916e465374a6b931db

Independent evaluation 004:
RLY-S110-DESIGN-EVAL-004 — ACCEPT
d3f4f7807cca47289595a59a90a49bd7cb4f5907

Exact-head CI on evaluation-record lineage:
38272577350 — SUCCESS
```

## 3. Accepted composite design

The Human accepts:

```text
Revision 1
+ Revision 2 / Rework 1
+ Revision 3 / Rework 2
+ Revision 4 / Rework 3
= ACCEPTED
```

Revision 4 is normative where it amends Revision 3 or earlier text.
Revision 3 is normative where it amends Revision 2 or Revision 1.
Revision 2 is normative where it amends Revision 1.
Revision 1 remains normative where later addenda are silent.

## 4. Accepted architecture boundary

The accepted design establishes:

- exact canonical repository/ref/parent/target binding;
- durable explicit canonical-policy binding with `UNMANAGED`, `MANAGED`, and fail-closed `UNKNOWN_OR_INVALID` resolution;
- exact HUMAN `RepositoryMutationAuthorization` reuse across the bounded repository-control subject union;
- pre-authorization `AUTHORIZABLE` versus execution-time `ELIGIBLE` separation;
- exact promotion policy and governance-basis digests;
- exact check-name/App/SHA freshness with successful completion required;
- isolated source-control verifier capability for full GitHub ruleset observation;
- exact-version ruleset stabilization and deterministic conformance evaluation;
- canonical integrity rules with no bypass actors;
- canonical writer restriction to the exact Relay Promotion App;
- `update_allows_fetch_and_merge == false`;
- non-force canonical Git-ref mutation only;
- explicit fencing of `RepositorySyncService` from a MANAGED canonical ref;
- append-only promotion intent and result evidence;
- restart-first reconciliation for ambiguous/crashed provider ref updates;
- per-property exact governance subjects and explicit control continuity;
- `VISIBLE_UNVERIFIED` canonical quarantine derived from immutable evidence;
- frozen Relay policy/binding for the full unresolved-quarantine lifetime;
- exact Human reconciliation of the already-visible target under the original policy/binding with zero Git writes;
- no destructive rollback, force-update, policy substitution, or silent policy weakening;
- live Relay dogfood before Slice 1.10 closure.

## 5. Preserved non-substitutability

```text
CI success != Human Authority
evaluation ACCEPT != Human Authority
technical acceptance != promotion
write credential != promotion authority
repository-admin capability != Relay authority
ruleset state != Relay authority
promotion receipt != promotion authority
visible Git mutation != valid Relay promotion

promotion executor != promotion decision maker
```

## 6. Explicit implementation boundary

This record accepts the design only.

It does not authorize:

- production implementation;
- production/runtime/test changes;
- migration v6 execution;
- creation or mutation of the four designed persistence tables;
- GitHub App installation or permission changes;
- Control Verifier credential installation/use;
- branch protection or ruleset creation/update/deletion;
- repository-setting changes;
- workflow changes;
- canonical promotion execution;
- policy-binding execution on a live project;
- quarantine reconciliation execution;
- force push/history rewrite;
- break-glass recovery;
- Role Contracts / Slice 2.2;
- Context/Work Packets / Slice 2.3;
- Workspace Authority / Slice 2.4;
- Phase 3;
- real-project agent execution.

A separate Human implementation authorization is required.

Repository-setting and credential mutations remain separately governed even after implementation authorization unless explicitly included in an exact later authority.

## 7. Resulting state

```text
Slice 1.10:
OPEN

Composite design:
RLY-S110-DESIGN-ACCEPT-001 — ACCEPTED

Independent design evaluation:
RLY-S110-DESIGN-EVAL-004 — ACCEPT

Implementation:
NOT AUTHORIZED

Repository-setting mutation:
NOT AUTHORIZED

Credential / App-permission mutation:
NOT AUTHORIZED

Canonical promotion:
NOT AUTHORIZED

Slice 2.2–2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

## 8. Next gate

The next possible gate is a separate exact Human implementation authorization for the accepted Slice 1.10 composite design.

Suggested identifier:

```text
RLY-S110-IMPL-AUTH-001
```

Implementation authorization must define the exact accepted design baseline, implementation branch/start SHA, allowed production/schema/test/documentation surface, explicit non-authority, validation requirements, and any separate treatment of live GitHub ruleset/credential configuration.

**Design accepted != implementation authorized.**