# Slice 1.6 — Independent Design Evaluation — Revision 3

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Evaluation ID:** `RLY-S16-DESIGN-EVAL-003`  
**Outcome:** `ACCEPT`  
**Authority:** `RLY-S16-DESIGN-AUTH-001`  
**Human-authorized design subject baseline:** `e9c6e3a5cc7592764bf0ac4932a2ae2659644027`  
**Authority-recording design parent:** `e4923c837f20de35eb96cd1caf615b86860d9222`  
**Revision 1:** `f3a0fa7d9cc5b344399c070406353e1107ec30ff`  
**Revision 2 Amendment:** `9a114b81f4347df10db7dfcb75677a606f18262e`  
**Revision 3 Amendment / exact accepted design head:** `c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb`  
**Prior evaluations:** `RLY-S16-DESIGN-EVAL-001 — REVISE`, `RLY-S16-DESIGN-EVAL-002 — REVISE`  
**Reviewer role:** Independent Slice 1.6 Design Reviewer — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The combined Slice 1.6 Revision 1 + Revision 2 + Revision 3 design satisfies `RLY-S16-DESIGN-AUTH-001` and preserves the accepted Relay lifecycle, governance, persistence, board-projection, and Human Authority boundaries.

Revision 3 is normative wherever it replaces or qualifies Revision 2; Revision 2 is normative wherever it replaces or qualifies Revision 1.

---

# 1. Authority and scope verification

The design remains bounded to:

> Human Authorization and Decision Gates

It does not authorize or design implementation of:

- Slice 1.7 manual evaluation / technical acceptance / accepted-baseline promotion;
- agent execution;
- AgentRuntime/OpenCode execution;
- repository/provider mutation;
- a general workflow engine;
- React/Node/new frontend build tooling;
- broad authentication/organization/RBAC infrastructure.

The design uses the accepted local server-rendered board and request-scoped SQLite architecture.

---

# 2. Accepted governance composition

The design correctly preserves:

```text
Human durable decision / permission
        !=
governed lifecycle execution
```

and:

```text
requested lifecycle movement
        -> exact HandoverGate
        -> deterministic evaluation
        -> selected + GREEN
        -> accepted lifecycle engine
```

APPROVE, REJECT, CHOOSE_PATH, and AUTHORIZE create durable human evidence. ADVANCE and CANCEL execute only exact current GREEN gates. CANCEL no longer bypasses gate governance.

Transition to `ACCEPTED` remains excluded from Slice 1.6 product execution and reserved for Slice 1.7.

---

# 3. Governance-revision causality

The final design correctly applies the accepted rule that authorization projection changes are non-human-decision governance-fact changes.

A new AUTHORIZE action atomically records:

```text
AuthorizationGrant
+
governance_revision N -> N+1
+
successor HandoverContext
+
deterministic complete gate evaluation
+
successor GateEvaluationRecord
```

Human approvals/choices do not advance `governance_revision`; they atomically append their decision plus a successor evaluation at the same governance revision.

This preserves causal human-decision staleness and gives Slice 1.5 a truthful latest stored observation after gate-affecting Human Authority action.

---

# 4. Current durable human-evidence projection

The final authorization projector is compatible with accepted Slice 0.4 semantics:

- exact matching grant exists -> earliest exact grant expresses the durable current permission;
- no exact grant but same-logical-gate stale grant exists -> deterministic latest stale grant remains explanatory evidence;
- no same-gate grant -> no grant projected.

This preserves both:

```text
AUTHORIZATION_REQUIRED
AUTHORIZATION_STALE
```

without inventing revocation semantics.

Approval and choice histories use deterministic latest relevant selection, while stale basis remains visible to the accepted gate engine.

---

# 5. Concurrency and stale-view safety

The final design binds consequential actions to:

```text
expected_evaluation_record_id
```

and binds replaceable approval/choice actions to exact expected current decision identity.

Therefore:

- a newer assessment invalidates an older form;
- a stale browser view cannot silently reverse a decision it did not observe;
- an out-of-band grant lacking its successor governance observation is surfaced as stale/incomplete rather than silently normalized;
- execution proves the supplied current human evidence is the deterministic latest durable projection inside the write transaction.

No hidden rebase or optimistic retry is permitted.

---

# 6. Human lifecycle controls

The design correctly avoids new `PAUSED` / `DEFERRED` lifecycle phases.

```text
BLOCK
PAUSE
DEFER
```

reuse accepted orthogonal `Blockage` with reserved Human Authority reason codes.

`CLEAR_HOLD` removes only those reserved Human-control blockers and never clears unrelated blockers.

PAUSE and DEFER are explicitly indefinite holds in Slice 1.6; no scheduler or automatic-resume subsystem is introduced.

Blockage actions remain constrained by accepted blockable phases.

---

# 7. Observation semantics

The design preserves the accepted Slice 1.5 rule:

> gate lights shown by the board are durable stored observations, not unrecorded live truth.

Gate-affecting Human Authority mutations append successor evaluation records atomically, so normal POST-Redirect-GET returns a projection backed by durable observation evidence.

The Human Action Basis is correctly defined as the latest durable evaluation observation plus currently queryable durable structural/human-evidence agreement. It explicitly does not claim that external assessment facts were freshly re-observed at POST time.

---

# 8. Product-security boundary

For the current M0 local product stage, the design truthfully defines one configured:

```text
ActorRef(kind=HUMAN)
```

as the Human Authority principal.

The form cannot override actor identity. SYSTEM/AGENT actors are rejected for Human Authority commands.

Mutation routes require anti-CSRF protection, remain loopback-local by default, use request-scoped database ownership, and introduce no unsupported claim of multi-user authentication or organization RBAC.

---

# 9. Persistence and architecture sufficiency

The reviewer agrees that the accepted design requires:

```text
new runtime dependencies: NONE
new schema migration: NONE
```

Existing tables already persist grants, human decisions, gate evaluation records, lifecycle events/current state, and executions.

The proposed `human_control` application package plus narrow caller-owned-transaction persistence helpers is Minimum Sufficient Architecture.

No generic command bus, workflow framework, ORM, event bus, or speculative abstraction is justified.

---

# 10. Expected implementation boundary accepted for later authorization

Expected new production package:

```text
src/relay_engine/human_control/
    __init__.py
    errors.py
    models.py
    service.py
```

Expected bounded existing-file changes:

```text
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/render.py
src/relay_engine/board/web.py
src/relay_engine/persistence/store.py
src/relay_engine/persistence/__init__.py
```

A tiny persistence record/export adjustment is acceptable only when mechanically required by the accepted transaction contract.

Material expansion beyond this surface must be escalated during any later implementation authorization.

---

# 11. Review findings

```text
RLY-S16-DESIGN-EVAL-001
F001-F006 -> RESOLVED by Revision 2

RLY-S16-DESIGN-EVAL-002
F007-F009 -> RESOLVED by Revision 3

Revision 3 review:
NO BLOCKING FINDINGS
NO MAJOR FINDINGS
```

---

# 12. Gate state

```text
Slice 1.6:
OPEN

Design authorization:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Exact accepted design head:
c0fe5d7d2c2bba5b1d9e0011e194005268b6f9fb

Independent design evaluation:
RLY-S16-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
NOT YET GRANTED

Implementation authorization:
NOT GRANTED

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

This independent evaluation does not itself grant Human design acceptance or implementation authority.

**Unblocked ≠ authorized.**
