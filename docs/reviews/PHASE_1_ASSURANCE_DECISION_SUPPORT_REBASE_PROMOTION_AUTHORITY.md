# Phase 1 Assurance / Decision Support Re-baseline — Promotion Authority

**Document class:** Immutable Human promotion authority  
**Status:** IMMUTABLE  
**Project:** Relay  
**Record:** `RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-PROMOTE-001`  
**Decision:** `AUTHORIZED`  
**Date:** 2026-10-10

## Human decision

Following:

```text
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-001 — AUTHORIZED
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-001 — AUTHORIZED
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-STRATEGIC-AMEND-EVAL-001 — ACCEPT
RLY-P1-ASSURANCE-DECISION-SUPPORT-REBASE-ACCEPT-001 — ACCEPTED
```

the Human authorizes canonical promotion of the complete accepted assurance / decision-support / strategic re-baseline lineage.

## Accepted subject

```text
Accepted architecture / roadmap subject:
2910736334241d93a248cc348d20c516e3ea8cc1

Independent evaluation recording commit:
ef19cef843d5ee0d18699032f6e4be7de29d90a4

Human acceptance recording commit:
ac3ef10a4f745b0aa417bf42eace167ef9f14dfe
```

## Exact canonical precondition

Expected canonical `main` before promotion:

```text
986b67f00958ef348fbf69ff677af630009881a7
```

Promotion must fail closed if canonical `main` has moved from that exact SHA.

## Authorized promotion shape

Only an ancestry-preserving fast-forward of `main` is authorized.

The final promotion head must be a descendant of:

```text
ac3ef10a4f745b0aa417bf42eace167ef9f14dfe
```

and may add only:

- this immutable promotion-authority record; and
- the corresponding registry update.

No source, runtime, test, dependency, schema, workflow, repository-setting, Slice-state, or design revision change is authorized by this record.

No squash, rebase, force update, history reconstruction, or branch-history replacement is authorized.

## Mechanical promotion preconditions

Before moving `main`:

- final promotion head exact-head CI must be SUCCESS;
- final head must be strictly ahead of expected `main` with zero commits behind;
- merge base must equal expected `main`;
- accepted architecture / roadmap subject must remain in the ancestry;
- Build Plan 84, Current Baseline 94, and Product Proposal 44 must remain the current living projections;
- registry transition must remain valid;
- no production source/runtime/test/dependency/schema/workflow/repository-setting changes may be introduced after Human acceptance;
- Slice 1.8 must remain paused;
- Slices 1.9 and 1.10 must remain unopened;
- Phase 3 and real-project agent execution must remain unauthorized.

## Promotion operation

Authorized operation:

```text
main:
986b67f00958ef348fbf69ff677af630009881a7
        |
        | ancestry-preserving fast-forward only
        v
final accepted governance head
```

The promotion executor acts mechanically. This record supplies the Human promotion decision; the executor cannot broaden it.

## Post-promotion authority boundary

Canonical promotion does not itself resume Slice 1.8.

After promotion:

```text
Slice 1.8:
OPEN / DESIGN AUTHORIZED / PAUSED

Slice 1.8 Design Revision 1:
PRESERVED / PRE-REBASELINE INPUT / NOT REVIEWED /
NOT HUMAN-ACCEPTED / NOT IMPLEMENTATION AUTHORITY

Slice 1.8 Design Revision 2:
NOT PRODUCED

Slice 1.8 implementation:
NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 1.10:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
```

A separate resume authority is required before Slice 1.8 design work continues.
