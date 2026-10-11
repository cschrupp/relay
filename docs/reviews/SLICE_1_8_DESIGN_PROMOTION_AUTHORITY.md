# Relay — Slice 1.8 Design Promotion Authority

**Document class:** Immutable Human promotion authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-10  
**Record:** RLY-S18-DESIGN-PROMOTE-001  
**Decision:** AUTHORIZED

## Human decision

The Human explicitly authorizes canonical promotion of the Human-accepted Slice 1.8 combined design lineage.

## Exact authority basis

~~~text
Canonical main before promotion:
b80f7e5401540468bbbd42445e53c01b6a565b56

Human-accepted design head:
7be4fdf117849abef2f3fe9eb9b9f41c70c4a1d3

Independent design evaluation:
RLY-S18-DESIGN-EVAL-002 — ACCEPT
c41f47089e9d8bf311a3f8c4b39ca803665888cc

Human design acceptance:
RLY-S18-DESIGN-ACCEPT-001 — ACCEPTED
7be4fdf117849abef2f3fe9eb9b9f41c70c4a1d3
~~~

## Authorized promotion shape

Only an ancestry-preserving fast-forward of main is authorized.

The final promotion head must be a descendant of the exact Human-accepted design head and may add only this immutable promotion-authority record plus its registry update.

No squash, rebase, force update, history reconstruction, or branch-history replacement is authorized.

## Mechanical promotion preconditions

- canonical main must still equal b80f7e5401540468bbbd42445e53c01b6a565b56;
- the final promotion head must be ahead of main with zero commits behind;
- the merge base must equal the expected canonical main;
- the Human-accepted combined design lineage must remain in ancestry;
- all three accepted design artifacts must remain LOCKED;
- Build Plan 86, Current Baseline 96, and Product Proposal 46 must remain current;
- registry transition must remain valid;
- exact-head CI on the final promotion head must succeed;
- no production source/runtime/test/dependency/schema/workflow/repository-setting change may be introduced after Human design acceptance;
- Slice 1.8 implementation must remain unauthorized;
- Slices 1.9 and 1.10 must remain unopened and unauthorized;
- Phase 3 and real-project agent execution must remain unauthorized.

## Post-promotion authority boundary

Canonical promotion establishes the accepted Slice 1.8 design as canonical project design state.

It does not authorize implementation.

~~~text
Slice 1.8:
OPEN / DESIGN ACCEPTED / IMPLEMENTATION NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 1.10:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
~~~

A separate Human implementation authorization is required before any Slice 1.8 implementation begins.
