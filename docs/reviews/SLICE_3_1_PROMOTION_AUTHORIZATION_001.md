# Relay — Slice 3.1 Coding Agent Execution — Canonical Promotion Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-26  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Authority:** `RLY-S31-PROMOTE-AUTH-001 — AUTHORIZED`

## 1. Human Authority decision

The Human authorizes canonical promotion of the independently accepted and Human-accepted Slice 3.1 implementation lineage, subject to the exact lease and bookkeeping constraints below.

This authority canonicalizes already-accepted design/implementation state. It does **not** authorize live execution, production Human-grant issuance, consumable mutation, provider/model calls, credentials, real-project autonomous execution, or automatic successor execution.

## 2. Exact accepted technical subject

```text
Accepted implementation:
6dd4296440196b63078b13855b70dff60a386325

Independent implementation acceptance:
RLY-S31-IMPL-EVAL-003 — ACCEPT

Independent evaluation record commit:
0f53703af6530543da89fc3b3eb157a391efa995

Human implementation acceptance:
RLY-S31-IMPL-ACCEPT-001 — ACCEPTED

Human acceptance record commit:
36fa1766dc80d88c4e54ddaacd5f8bc3f5b45c2a

Accepted design:
a28a9b88ddd85cd1a32932b30c4e0e668f23b557

Human design acceptance:
RLY-S31-DESIGN-ACCEPT-001 — ACCEPTED
```

## 3. Canonical main lease

Promotion is authorized only while remote `main` remains exactly:

`26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f`.

If `main` moves before the promotion ref update, STOP and reconcile. Force update, rebase, squash, cherry-pick recreation, history rewrite, or backward ref movement is prohibited.

## 4. Authorized promotion bookkeeping

After the Human acceptance record, an exact descendant may be created solely to:

- record this promotion authority;
- register the Slice 3.1 design/implementation evaluation, acceptance, authorization and handoff records;
- update living current-state projections so they truthfully show design and implementation accepted;
- update `.relay/registry.json` ordering, revisions, metadata and digests;
- run repository validation and exact-head CI.

No production/runtime/test/source semantics may change after the exact accepted implementation subject except governance projection/registry bookkeeping.

The already accepted Slice 3.1 source/test implementation contained in the lineage is the technical subject being promoted.

## 5. Current-state projection truth

The promotion-ready lineage must state, without ambiguity:

```text
Phase 3:
OPEN

Slice 3.1:
OPEN

Slice 3.1 design:
ACCEPTED

Accepted design:
a28a9b88ddd85cd1a32932b30c4e0e668f23b557

Slice 3.1 implementation:
ACCEPTED

Accepted implementation:
6dd4296440196b63078b13855b70dff60a386325

Independent implementation evaluation:
RLY-S31-IMPL-EVAL-003 — ACCEPT

Human implementation acceptance:
RLY-S31-IMPL-ACCEPT-001 — ACCEPTED

Canonical promotion:
AUTHORIZED under RLY-S31-PROMOTE-AUTH-001

Live AgentRuntime/provider/model execution:
NOT AUTHORIZED

Production Human-grant/reservation mutation:
NOT AUTHORIZED

Operational persistence:
NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

Historical snapshots may remain only where clearly historical.

## 6. Promotion condition

Before changing `main`, verify:

- exact promotion candidate descends from `26e1ef9d...`;
- exact promotion candidate descends from accepted implementation `6dd4296...`;
- exact promotion candidate descends from Human acceptance `36fa176...`;
- post-acceptance changes are promotion bookkeeping only;
- registry ordering, pointers and digests validate;
- current projections reflect accepted design/implementation;
- exact-head CI is SUCCESS;
- remote implementation branch points to the exact promotion candidate;
- remote `main` still equals the lease.

## 7. Authorized canonical transition

If all conditions pass, authorize exactly one ref mutation:

```text
branch:
main

from:
26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f

to:
the exact validated Slice 3.1 promotion-bookkeeping descendant

mode:
NON-FORCE FAST-FORWARD ONLY
```

Use the exact expected main SHA as a lease.

## 8. Post-promotion state

After successful promotion, verify remote `main` equals the promoted candidate and post-promotion CI succeeds.

Promotion does not close Slice 3.1 and does not authorize live execution. Any later production execution/dogfood/real-project attempt requires its own exact Human authority.

## 9. Disposition

```text
RLY-S31-PROMOTE-AUTH-001 — AUTHORIZED

Accepted implementation:
6dd4296440196b63078b13855b70dff60a386325

Promotion bookkeeping:
AUTHORIZED / BOUNDED

Canonical promotion:
AUTHORIZED CONDITIONALLY

Live execution:
NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

**Canonicalize the accepted Slice 3.1 implementation lineage only. Do not interpret promotion as execution authority.**
