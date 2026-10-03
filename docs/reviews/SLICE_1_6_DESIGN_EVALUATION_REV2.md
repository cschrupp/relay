# Slice 1.6 — Independent Design Evaluation — Revision 2

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-03  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Evaluation ID:** `RLY-S16-DESIGN-EVAL-002`  
**Outcome:** `REVISE`  
**Authority:** `RLY-S16-DESIGN-AUTH-001`  
**Revision 1:** `f3a0fa7d9cc5b344399c070406353e1107ec30ff`  
**Revision 2 Amendment:** `9a114b81f4347df10db7dfcb75677a606f18262e`  
**Prior evaluation:** `RLY-S16-DESIGN-EVAL-001 — REVISE`  
**Reviewer role:** Independent Slice 1.6 Design Reviewer — GPT-5.6 Sol

## Decision

```text
REVISE
```

Revision 2 resolves all six findings from `RLY-S16-DESIGN-EVAL-001`. The overall design is now close to acceptance. The remaining findings are narrow protocol corrections around the exact current authorization projection and the meaning of a Human Action Basis.

---

## F007 — BLOCKING — Exact-only authorization projection would suppress accepted AUTHORIZATION_STALE evidence

Revision 2 D02.1 defines current authorization projection only over grants that exactly match the current `(slice, baseline, gate, gate_revision)` basis.

The accepted Slice 0.4 engine intentionally distinguishes:

```text
no grant for this logical gate
    -> AUTHORIZATION_REQUIRED

same logical gate grant exists but baseline / gate revision no longer matches
    -> AUTHORIZATION_STALE
```

`HandoverContext` permits at most one grant per logical gate precisely so the current projection may contain that stale same-gate grant and the engine can explain why new authorization is required.

An exact-only projector would omit stale grants and collapse `AUTHORIZATION_STALE` into `AUTHORIZATION_REQUIRED`, losing accepted explanatory semantics.

### Required revision

For each **current logical gate ID**, construct one authorization projection as follows:

1. collect grants for the same Slice and logical gate ID;
2. if one or more grants exactly match current baseline + gate revision, select the earliest exact permission by `(granted_at, authorization_id)`;
3. otherwise, if stale same-gate grants exist, select one deterministic stale explanatory grant; the latest by `(granted_at, authorization_id)` is appropriate because no active current permission exists and the projection is explanatory only;
4. otherwise project no grant.

This preserves durable-permission semantics for exact grants while retaining the accepted stale-grant reason path.

The same projector must be used for action-basis comparison and successor evaluation contexts.

---

## F008 — MAJOR — AUTHORIZE no-op must not hide an unsynchronized durable grant

Revision 2 says an exact matching grant already present makes AUTHORIZE a no-op success.

That is correct only when the latest durable gate observation already contains the deterministic current grant projection and therefore reflects the required governance-revision advance.

An out-of-band/direct persistence write could leave:

```text
exact durable AuthorizationGrant exists
+
latest GateEvaluationRecord does not contain it
+
governance_revision was never advanced in durable observation history
```

Returning no-op success in that condition would leave the governance basis causally incomplete.

### Required revision

AUTHORIZE target-state idempotency applies only when the latest Human Action Basis already projects the exact active grant.

If an exact current grant exists but the latest observation is not synchronized to the deterministic authorization projection, the service must fail closed with `HumanActionBasisStale` / `HumanActionRequiresEvaluation`. It must not create a second grant and must not pretend the missing successor observation exists.

This preserves recovery visibility instead of silently normalizing out-of-band writes.

---

## F009 — MAJOR — “Full/current” action-basis wording must not overclaim external assessment freshness

Revision 2 sometimes calls the Human Action Basis a “full” or “current full” evaluation basis.

Accepted Slice 1.5 semantics deliberately distinguish durable structural matching from claims that every historical assessment input is freshly verified. Values such as risk, quality status, evaluation outcome, change-surface status, and toolchain-change status may exist only inside the latest durable `HandoverContext` observation.

Slice 1.6 can prove:

- the observation is the latest durable evaluation record;
- currently queryable lifecycle/gate/baseline state still matches;
- current durable human authority/decision evidence agrees with its projection.

It cannot independently prove an external assessment fact has not changed without another record.

### Required revision

Define Human Action Basis explicitly as:

> the latest durable gate-evaluation observation whose independently queryable durable structural facts and human-evidence projection still match current durable state.

It is the exact basis on which the human acts. It is **not** a claim that every assessment input has been freshly re-observed outside Relay.

A newer assessment must be recorded as a newer `GateEvaluationRecord`; `expected_evaluation_record_id` then prevents actions from silently using the older observation.

---

## Confirmed resolutions from Revision 2

The reviewer confirms Revision 2 correctly resolves:

- authorization-driven governance revision advancement;
- atomic successor gate observations for APPROVE / REJECT / CHOOSE_PATH;
- direct-cancellation bypass by routing CANCEL through a GREEN handover gate;
- optimistic concurrency for same-basis decision replacement;
- durable-permission rather than latest-wins semantics for exact matching grants;
- roadmap authorization-record field mapping and the M0 Human Authority principal boundary.

The reviewer also confirms no schema migration or new runtime dependency is required by the remaining corrections.

---

## Gate state

```text
Slice 1.6:
OPEN

Design authority:
RLY-S16-DESIGN-AUTH-001 — AUTHORIZED

Revision 1:
f3a0fa7d9cc5b344399c070406353e1107ec30ff

Revision 2 Amendment:
9a114b81f4347df10db7dfcb75677a606f18262e

Independent design evaluation:
RLY-S16-DESIGN-EVAL-002 — REVISE

Human design acceptance:
NOT YET ELIGIBLE

Implementation:
NOT AUTHORIZED

Slice 1.7:
NOT OPEN

Agent execution:
NOT AUTHORIZED
```

**Unblocked ≠ accepted.**
