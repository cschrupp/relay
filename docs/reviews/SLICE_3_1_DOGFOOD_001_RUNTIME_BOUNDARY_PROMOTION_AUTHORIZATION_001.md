# Relay — Runtime Boundary Accepted Implementation Canonical Promotion Authority 001

**Document class:** Immutable Human Authority record
**Status:** IMMUTABLE / AUTHORIZED
**Date:** 2026-10-27
**Record:** `RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-PROMOTE-AUTH-001 — AUTHORIZED`

## Human decision

The Human authorizes canonical promotion of the Human-accepted runtime-boundary implementation lineage, with bounded living-projection reconciliation.

Exact accepted technical subject:

`e3b48c9c883d8e2983bbbca3e21f2bc0185f4a46`

Independent implementation evaluation:

`RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-EVAL-002 — ACCEPT`

Human implementation acceptance:

`RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-IMPL-ACCEPT-001 — ACCEPTED`

Human acceptance record commit:

`0b3a0cec71fea3902203dad332e1533c2540cbc0`

Acceptance registry tip:

`cfc09bf067a62fd222e61a0b3c5f7f34e00afc14`

## Canonical main lease

Promotion is authorized only while remote `main` remains exactly:

`6c0add5611e2e8eab942787e0d6a1afafaa4a2f4`

The canonical ref mutation is NON-FORCE FAST-FORWARD ONLY.

Force update, rebase, squash, cherry-pick recreation, backward movement, or history rewrite is prohibited.

If `main` moves from the exact lease before promotion, STOP and reconcile.

## Authorized promotion bookkeeping

After the Human implementation acceptance, the promotion lineage may change only governance/bookkeeping surfaces necessary to make current state truthful:

- record and register this promotion authority;
- update `docs/CURRENT_BASELINE.md`;
- update `docs/BUILD_PLAN_V0_6.md`;
- update `docs/TODO.md`;
- update `.relay/registry.json` revisions, digests, scopes and canonical pointers for those living projections;
- validate registry ordering/digests and repository contracts;
- obtain exact-head CI success.

No source, runtime, test, dependency, workflow, provider/model, or Dogfood execution semantics may change during promotion bookkeeping.

## Required current-state truth

Promotion-ready projections must state that:

- Slice 3.1 operational mapping for this bounded Dogfood exercise is accepted and materialized;
- runtime-boundary design Candidate 003 is Human-accepted;
- corrected runtime-boundary implementation `e3b48c9...` is independently accepted and Human-accepted;
- M001–M003 and I001–I003 are closed;
- no concrete enforcing backend is qualified on the current host;
- fixture/source durable reachability remains a separate unresolved admission condition;
- exact candidate/grant/source freshness must be recompiled/revalidated before WorkPacket materialization or admission;
- Dogfood 001 remains AUTHORIZED / NOT ADMITTED / NOT CONSUMED.

## Stale remote Dogfood branch boundary

Remote branch `dogfood/3.1-execution-001` currently contains an earlier frozen preparation lineage rooted at canonical base `6c0add...` and a different planned attempt identity.

That remote branch must NOT be force-moved, rebased, merged into `main`, registered as current Dogfood state, or treated as the later recovered Dogfood request/grant lineage under this authority.

The branch is preserved unchanged as historical/unreconciled evidence until the later exact Dogfood attempt lineage is durably available for a separate bounded reconciliation.

## Authorized canonical transition

After promotion bookkeeping validates and exact-head CI succeeds, authorize exactly one ref transition:

```text
branch: main
from: 6c0add5611e2e8eab942787e0d6a1afafaa4a2f4
to: exact validated promotion-bookkeeping descendant
mode: non-force fast-forward only
```

## Explicit non-authority

This authority does not permit:

- live Dogfood WorkPacket or WorkspacePlan materialization;
- fixture access;
- workspace provisioning;
- OpenCode launch/session/prompt;
- credential access;
- provider/model calls;
- Dogfood admission or consumption;
- mutation of the stale remote Dogfood branch;
- declaration that a concrete enforcing backend is qualified.

Dogfood 001 remains:

`AUTHORIZED / NOT ADMITTED / NOT CONSUMED`

**Disposition:** `AUTHORIZED`
