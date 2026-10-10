# Relay Roadmap / Governance-Assurance Re-baseline — Promotion Authority

**Document class:** Immutable Human promotion authority  
**Status:** IMMUTABLE  
**Record:** RLY-P2-ROADMAP-REBASE-PROMOTE-001  
**Decision:** AUTHORIZED  
**Date:** 2026-10-10

## 1. Human decision

Following:

~~~text
RLY-P2-ROADMAP-REBASE-001 — AUTHORIZED
RLY-P2-ROADMAP-REBASE-EVAL-001 — REWORK
RLY-P2-ROADMAP-REBASE-EVAL-002 — ACCEPT
RLY-P2-ROADMAP-REBASE-ACCEPT-001 — ACCEPTED
~~~

the Human authorizes canonical promotion of the accepted roadmap / governance-assurance redesign lineage to main.

## 2. Exact canonical precondition

Expected canonical main before promotion:

~~~text
ad0444337efcddb5694d14a57a99c22d18cdfb9c
~~~

Promotion must fail closed if canonical main has moved from that exact SHA.

## 3. Authorized promotion shape

Only an ancestry-preserving fast-forward of main is authorized.

The promoted head must be a descendant of:

~~~text
21412c5be287bc6a3ff64f354e576c04edc6fa0e
~~~

and may add only the governance records and registry update needed to:

- record RLY-P2-ROADMAP-REBASE-EVAL-002 — ACCEPT;
- clarify the established Sol/Luna role model;
- record this promotion authority.

No squash, rebase, history reconstruction, force update, or direct 38 -> 40 Product Proposal transition is authorized.

## 4. Mechanical promotion preconditions

Before moving main:

- final promotion head exact-head CI must be SUCCESS;
- final head must be strictly ahead of expected main with zero commits behind;
- merge base must equal expected main;
- living projection lineage must remain intact;
- no source/runtime/test/dependency/schema changes may be introduced after the accepted redesign;
- no future Slice may become opened or implementation-authorized.

## 5. Promotion operation

Authorized operation:

~~~text
main:
ad0444337efcddb5694d14a57a99c22d18cdfb9c
        |
        | fast-forward only
        v
final accepted governance head
~~~

The promotion executor is mechanical and does not make the acceptance decision.

## 6. Post-promotion authority boundary

Promotion of this roadmap redesign does not itself open Slice 1.8.

After promotion:

~~~text
Slice 1.8:
PLANNED — NEXT / NOT OPEN / NOT AUTHORIZED

Slice 1.9:
PLANNED / NOT OPEN / NOT AUTHORIZED

Slice 2.2–2.4:
PLANNED / NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~
