# Slice 1.6 — Human Authorization and Decision Gates — Revision 3 Amendment

**Status:** DESIGN REVISION 3 — PENDING INDEPENDENT REVIEW  
**Document class:** Lockable design record  
**Human version:** Revision 3 Amendment  
**Project:** Relay  
**Slice:** 1.6 — Human Authorization and Decision Gates  
**Design authority:** `RLY-S16-DESIGN-AUTH-001`  
**Human-authorized design subject baseline:** `e9c6e3a5cc7592764bf0ac4932a2ae2659644027`  
**Revision 1:** `f3a0fa7d9cc5b344399c070406353e1107ec30ff`  
**Revision 2 Amendment:** `9a114b81f4347df10db7dfcb75677a606f18262e`  
**Independent Revision-2 review:** `RLY-S16-DESIGN-EVAL-002 — REVISE`  
**Review record commit:** `ed68bc0c9716704f1cd8f54c2004869d38259b21`  
**Architect / Contract Designer:** GPT-5.6 Sol  
**Date:** 2026-10-03

Revision 1 and Revision 2 remain historical design evidence. This amendment is normative wherever it replaces or qualifies them.

---

# 1. Purpose

Resolve the three narrow findings from `RLY-S16-DESIGN-EVAL-002` without changing the accepted Revision-2 architecture or implementation boundary.

---

# 2. R3-D01 — Authorization projection preserves both current permission and stale evidence

This replaces Revision 2 D02.1 and resolves `RLY-S16-DESIGN-EVAL-002/F007`.

For each current logical gate, Slice 1.6 constructs **at most one** `AuthorizationGrant` in `HandoverContext`, preserving the accepted projection-unambiguity rule.

Given current gate:

```text
gate.slice_id
gate.gate_id
gate.revision
gate.baseline_id
```

load durable grants for the same:

```text
slice_id
gate_id
```

Then select deterministically:

## Exact current permission exists

If one or more grants match both:

```text
baseline_id == current gate baseline
gate_revision == current gate revision
```

project the earliest established exact permission:

```text
least granted_at
then least authorization_id
```

All later exact duplicates are redundant immutable evidence and do not replace or delay the permission.

## No exact permission, but stale same-gate permission exists

If no exact current grant exists but one or more grants for the same Slice/logical gate exist on another baseline and/or gate revision, project one stale explanatory grant:

```text
greatest granted_at
then greatest authorization_id
```

This grant does not authorize the current gate. It exists in the current context only so the accepted engine can return:

```text
AUTHORIZATION_STALE
```

rather than collapsing the condition into `AUTHORIZATION_REQUIRED`.

## No same-gate grant

Project no grant for that logical gate.

This exact projector is used consistently for:

- Human Action Basis comparison;
- successor GateEvaluationRecord contexts;
- governed execution current-evidence verification;
- Slice-detail Human Action projection.

Revocation/expiry remain out of scope.

---

# 3. R3-D02 — AUTHORIZE idempotency requires synchronized authority observation

This qualifies Revision 2 D03 and resolves `RLY-S16-DESIGN-EVAL-002/F008`.

AUTHORIZE has three cases.

## Case A — exact current grant exists and latest observation already projects it

If:

- an exact current grant exists;
- the deterministic authorization projector selects that grant; and
- the latest Human Action Basis context already contains that selected grant with all other Human Action Basis checks satisfied;

then the requested authorization target state already exists.

Result:

```text
no-op success
no new grant
no governance_revision increment
no new GateEvaluationRecord
```

This is safe retry/idempotency.

## Case B — exact current grant exists but latest observation does not project it

This means durable authority and durable evaluation chronology are not synchronized—for example, an out-of-band persistence write created a grant without the required successor observation.

Result:

```text
HumanActionBasisStale / HumanActionRequiresEvaluation
NO WRITE
```

The service must not:

- create a second grant;
- invent the missing prior governance revision transition;
- claim target-state success;
- silently repair history.

Explicit recovery/reconciliation is separate governed work.

## Case C — no exact current grant exists

Apply Revision 2 D03 normally:

```text
validate latest Human Action Basis
insert grant
increment governance_revision exactly once
build successor context with R3-D01 projector
evaluate complete gate set
append successor GateEvaluationRecord
commit atomically
```

A stale same-gate grant may be present in the pre-action context. The new exact grant replaces it **in the current projection only**; the stale grant remains immutable history.

---

# 4. R3-D03 — Human Action Basis is a latest durable observation, not omniscient freshness

This replaces over-broad “full/current basis” wording in Revision 2 and resolves `RLY-S16-DESIGN-EVAL-002/F009`.

Normative definition:

> **Human Action Basis** is the latest durable gate-evaluation observation whose independently queryable durable structural facts and deterministic durable human-evidence projection still agree with current Relay state.

The service proves at minimum:

```text
latest GateEvaluationRecord identity by durable sequence
current lifecycle equality / revision
current outgoing gate refs and revisions
current gate baseline
current deterministic authorization projection
current deterministic approval projection
current deterministic choice projection
submitted expected decision identities
```

The latest evaluation record remains the source observation for assessment facts that do not yet have another accepted current durable authority source, including as applicable:

```text
evaluation_outcome
quality_checks
change_surface_status
risk_status
toolchain_change_status
available artifacts / evidence where not independently re-derived by this service
```

Therefore Human Action Basis means:

```text
latest recorded observation
+
verified currently queryable durable facts
```

It does **not** mean:

```text
all external assessment facts were freshly re-observed at POST time
```

If a newer assessment exists, it must first become a newer durable `GateEvaluationRecord`. Every consequential gate action carries `expected_evaluation_record_id`, so a newly recorded assessment invalidates stale forms deterministically.

The UI wording must not describe Human Action Basis as “freshly verified current truth.” It may say, for example:

```text
Acting on latest recorded gate evaluation and current durable authority state.
```

---

# 5. R3-D04 — Consequential action projection rules

For one Slice-detail projection:

1. load the latest durable gate evaluation by persistence sequence;
2. verify Slice 1.5 structural basis status;
3. build R3-D01 current authorization projection;
4. build Revision-2 latest relevant approval/choice projections;
5. compare those human projections to the latest evaluation context;
6. expose gate-affecting actions only when the resulting Human Action Basis is valid for that action.

A stale explanatory authorization/decision may be displayed, but it does not become current authority merely because it is visible.

AUTHORIZE may be exposed when the latest observation is valid and the current gate reports an authorization requirement/staleness. APPROVE/REJECT/CHOOSE_PATH remain tied to the latest observed current action reasons. ADVANCE/CANCEL remain tied to exact latest observation identity and current GREEN re-evaluation inside the write transaction.

---

# 6. R3-D05 — Additional deterministic tests

Implementation must additionally prove:

## Stale authorization projection

- stale same-gate grant is projected when no exact current grant exists;
- accepted gate engine returns `AUTHORIZATION_STALE` for that projection;
- exact current grant takes projection precedence over stale grants;
- earliest exact grant is selected when redundant exact grants exist;
- latest stale grant is selected deterministically only when no exact current grant exists.

## AUTHORIZE synchronization

- synchronized exact grant -> no-op success;
- exact durable grant missing from latest observation -> fail closed, no write;
- stale grant + no exact grant -> new exact grant + one governance revision increment + successor evaluation;
- successor evaluation projects new exact grant, not stale grant.

## Human Action Basis semantics

- newer evaluation record invalidates older submitted `expected_evaluation_record_id` even when lifecycle/gate refs are unchanged;
- external assessment freshness is never inferred from wall-clock age;
- action projection does not claim assessment facts are independently reverified when they are only present in the latest durable observation.

---

# 7. Resolution matrix

```text
F007 stale authorization evidence
    -> RESOLVED by R3-D01, D04, D05

F008 unsynchronized grant idempotency
    -> RESOLVED by R3-D02, D05

F009 overclaiming observation freshness
    -> RESOLVED by R3-D03, D04, D05
```

All Revision-2 resolutions for `RLY-S16-DESIGN-EVAL-001` remain in force.

---

# 8. Preserved boundaries

Unchanged:

```text
new runtime dependencies: NONE
schema migration: NONE
server-rendered FastAPI board: PRESERVED
request-scoped SQLite ownership: PRESERVED
Slice 1.7: NOT OPEN
manual technical acceptance/baseline promotion: NOT AUTHORIZED
AgentRuntime/OpenCode implementation: NOT AUTHORIZED
agent execution: NOT AUTHORIZED
```

Revision 3 introduces no additional production package beyond the Revision-1/2 expected change surface.

---

# 9. Review handoff

```text
Combined design subject:
Revision 1
f3a0fa7d9cc5b344399c070406353e1107ec30ff
+
Revision 2 Amendment
9a114b81f4347df10db7dfcb75677a606f18262e
+
Revision 3 Amendment
<this amendment commit>

Next role:
Independent Slice 1.6 Design Reviewer

Outcome vocabulary:
ACCEPT / REVISE / ESCALATE
```

Human design acceptance and implementation authorization remain separate later gates.

**Unblocked ≠ authorized.**
