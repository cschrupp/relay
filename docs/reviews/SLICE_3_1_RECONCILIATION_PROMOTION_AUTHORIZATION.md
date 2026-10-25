# Relay — Slice 3.1 Opening / Design-Authority Reconciliation — Promotion Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Authority:** `RLY-S31-RECON-PROMOTE-AUTH-001 — AUTHORIZED`

## 1. Human Authority decision

The Human explicitly authorizes canonical promotion of the independently accepted Slice 3.1 opening/design-authority reconciliation, subject to the exact lease and bounded bookkeeping requirements below.

This authority is limited to promotion of the accepted reconciliation state.

It does **not** authorize Slice 3.1 design acceptance, implementation, production wiring, AgentRuntime/provider/model execution, real-project autonomous execution, or any new engineering work.

## 2. Exact accepted subject

```text
Accepted reconciliation subject:
f8779306cee446b5ec319ab87ee44de3e0f0e9f7

Independent acceptance:
RLY-S31-RECON-EVAL-002 — ACCEPT

Acceptance record commit:
5d7183c72d0696caf940fba9b8784602cd34858f

Prior reconciliation evaluation:
RLY-S31-RECON-EVAL-001 — REWORK / NARROW

Canonical main lease:
f441e49f2d16e1f0149aca8cadd924f9617c7dfa

Promotion branch:
reconciliation/3.1-opening-design-authority
```

## 3. Authorized promotion-bookkeeping descendant

The exact accepted technical/documentation subject remains:

`f8779306cee446b5ec319ab87ee44de3e0f0e9f7`.

This authority permits an exact descendant used **only** to preserve and register immutable governance evidence required for canonical promotion.

Authorized bookkeeping is limited to:

- preserving `RLY-S31-RECON-EVAL-001` byte-for-byte;
- preserving `RLY-S31-RECON-EVAL-002` byte-for-byte;
- preserving this promotion authority byte-for-byte;
- registering those immutable records in `.relay/registry.json`;
- maintaining registry ordering and canonical-pointer validity;
- validating the resulting exact promotion candidate.

No living projection revision is required merely because promotion authority is recorded, because the accepted current-state truth is unchanged.

No source or test changes are authorized.

## 4. Expected promotion-ready registry state

The independently accepted reconciliation subject has:

```text
registry artifacts:
357

canonical pointers:
5
```

Promotion bookkeeping adds exactly three immutable records:

```text
docs/reviews/SLICE_3_1_RECONCILIATION_EVALUATION_001.md
docs/reviews/SLICE_3_1_RECONCILIATION_EVALUATION_002.md
docs/reviews/SLICE_3_1_RECONCILIATION_PROMOTION_AUTHORIZATION.md
```

Therefore the promotion-ready registry target is:

```text
artifact count:
360

canonical pointers:
5

Build Plan:
revision 152

Current Baseline:
revision 169

Product Proposal:
revision 68

TODO:
revision 60
```

Do not duplicate previously registered Slice 3.1 opening/design authority records.

## 5. Promotion conditions

Canonical promotion is authorized only if all of the following remain true:

```text
remote main == f441e49f2d16e1f0149aca8cadd924f9617c7dfa

promotion candidate is a true descendant of:
f441e49f2d16e1f0149aca8cadd924f9617c7dfa

promotion candidate is a true descendant of:
f8779306cee446b5ec319ab87ee44de3e0f0e9f7

promotion candidate is a true descendant of:
5d7183c72d0696caf940fba9b8784602cd34858f

only authorized promotion-bookkeeping changes occur after the accepted subject

registry artifact count == 360
registry canonical pointers == 5
registry paths/order/digests valid

Build Plan revision == 152
Current Baseline revision == 169
Product Proposal revision == 68
TODO revision == 60

Slice 3.1 remains OPEN
Slice 3.1 design remains AUTHORIZED / ACCEPTANCE PENDING
Slice 3.1 implementation remains NOT AUTHORIZED
Phase 3 execution remains NOT AUTHORIZED
real-project execution remains NOT AUTHORIZED

exact-head CI == SUCCESS
```

## 6. Canonical ref mutation authority

If all promotion conditions pass, authorize exactly one canonical ref transition:

```text
branch:
main

from:
f441e49f2d16e1f0149aca8cadd924f9617c7dfa

to:
the exact validated promotion-bookkeeping descendant of
f8779306cee446b5ec319ab87ee44de3e0f0e9f7

mode:
NON-FORCE FAST-FORWARD ONLY
```

The update must use the exact expected main lease.

No force update, rebase, squash, cherry-pick recreation, merge commit, or history rewrite is authorized.

If `main` moves from the exact lease before promotion, STOP and reconcile.

## 7. Post-promotion verification

After the fast-forward, verify:

- remote `main` points exactly to the promoted candidate;
- the reconciliation branch points to the same candidate or remains an ancestor as intended;
- the promoted candidate remains descendant of the accepted subject;
- post-promotion `main` CI succeeds.

A post-promotion CI failure does not authorize rollback or force mutation; it requires separate governance handling.

## 8. Preserved non-authority

After promotion, the controlling state remains:

```text
Phase 3:
OPEN

Slice 3.1:
OPEN

Slice 3.1 design:
AUTHORIZED

Design acceptance:
PENDING

Slice 3.1 implementation:
NOT AUTHORIZED

Production wiring:
NOT AUTHORIZED

AgentRuntime / provider / model execution:
NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

Promotion of governance projections does not grant engineering execution authority.

## 9. Disposition

```text
RLY-S31-RECON-PROMOTE-AUTH-001 — AUTHORIZED

Accepted reconciliation:
f8779306cee446b5ec319ab87ee44de3e0f0e9f7

Independent evaluation:
RLY-S31-RECON-EVAL-002 — ACCEPT

Promotion bookkeeping:
AUTHORIZED / BOUNDED

Canonical promotion:
AUTHORIZED CONDITIONALLY

Main lease:
f441e49f2d16e1f0149aca8cadd924f9617c7dfa

Force:
PROHIBITED
```

**Promotion authority is limited to canonicalizing the already-accepted Slice 3.1 opening/design-authority reconciliation. It does not authorize design acceptance, implementation, or execution.**
