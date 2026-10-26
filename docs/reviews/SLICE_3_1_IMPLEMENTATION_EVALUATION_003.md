# Relay — Slice 3.1 Coding Agent Execution — Independent Implementation Evaluation 003

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE / ACCEPT  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Evaluation ID:** `RLY-S31-IMPL-EVAL-003 — ACCEPT`  
**Evaluator:** Independent Implementation Reviewer — GPT-5.6 Sol  
**Exact corrective implementation subject:** `6dd4296440196b63078b13855b70dff60a386325`  
**Corrective parent:** `cdeebc9fdbb942a1a32092e3c3d5e2b62234b90e`  
**Prior evaluation:** `RLY-S31-IMPL-EVAL-002 — REWORK / NARROW`  
**Implementation authority:** `RLY-S31-IMPL-AUTH-001 — AUTHORIZED`  
**Implementation handoff:** `RLY-S31-IMPL-HANDOFF-001`  
**Accepted design:** `a28a9b88ddd85cd1a32932b30c4e0e668f23b557`  
**Exact-head CI:** `40265141596 — SUCCESS`

## 1. Decision

```text
RLY-S31-IMPL-EVAL-003 — ACCEPT
```

The exact Slice 3.1 corrective implementation candidate:

`6dd4296440196b63078b13855b70dff60a386325`

closes the remaining blocking finding `I31-F002`.

No blocking implementation defect remains within the authorized Slice 3.1 implementation scope.

This independent evaluation does not itself grant Human implementation acceptance, production execution authority, real-project execution authority, or canonical promotion authority.

## 2. Exact lineage and scope

PASS.

The corrective candidate is exactly one commit ahead of:

`cdeebc9fdbb942a1a32092e3c3d5e2b62234b90e`

which records `RLY-S31-IMPL-EVAL-002 — REWORK / NARROW`.

The corrective increment changes exactly:

```text
src/relay_engine/coding_execution/models.py
src/relay_engine/coding_execution/evaluation.py
tests/unit/test_coding_execution_evaluation.py
tests/unit/test_coding_execution_scenarios.py
```

No predecessor Slice implementation file changed.

Remote implementation branch points exactly to the evaluated subject.

Canonical `main` remains unchanged at:

`26e1ef9d19892b4585b828e8d92f7d9a55e9ba2f`.

## 3. Finding I31-F002 — CLOSED

Prior defect:

Slice 2.5 defines exact consumable identity as:

```text
ConsumableRef(
    consumable_key,
    scope_key
)
```

while Slice 3.1 canonicalized reservations using only `consumable_key`.

Corrective result: PASS.

### Base ExecutionSubject

`ExecutionSubject.reservations` now canonicalizes and deduplicates by:

```text
(consumable_key, scope_key)
```

rather than by `consumable_key` alone.

This correctly permits:

```text
("campaign-budget", "scope-a")
("campaign-budget", "scope-b")
```

as two distinct exact consumable identities.

It still rejects an actual duplicate exact pair.

### CorrectiveSubjectBinding

`CorrectiveSubjectBinding.reservations` now uses the same exact pair.

The required corrective reservation set is now represented as:

```text
tuple[ConsumableRef, ...]
```

and therefore preserves both:

- `consumable_key`;
- `scope_key`.

The exact-match validator reconstructs full `ConsumableRef` values from supplied reservation evidence and compares the complete ordered pair set to the complete required set.

### Evaluator REWORK path

`evaluate_evaluator_rework(...)` now derives required reservation refs directly from the corrective candidate's `ConsumptionRequirement.consumable` values and sorts them deterministically by:

```text
(consumable_key, scope_key)
```.

This preserves the accepted Slice 2.5 identity model through the A17 corrective lineage.

## 4. Focused reservation behavior

PASS.

The corrective tests prove:

- same consumable key under distinct scope keys is valid;
- both exact refs can coexist;
- duplicate exact pair is rejected;
- one missing scope-specific reservation remains fail-closed;
- wrong scope is rejected even when the consumable key matches;
- corrective binding preserves complete exact reservation refs;
- base ExecutionSubject accepts a valid multi-scope set;
- zero/single-reservation behavior remains compatible with the existing suite.

The existing `_reservation_reasons(...)` logic continues to match requirements and reservations by:

```text
(consumable_key, scope_key)
```

and therefore remains consistent with the corrected model boundaries.

## 5. Prior A17 finding remains closed

PASS.

The reservation correction does not regress `I31-F001`.

The implementation still preserves:

- exact evaluator REWORK record projection;
- exact reviewed terminal candidate/result/handoff lineage;
- finding IDs;
- permitted corrective scope;
- original authority scope;
- `IN_SCOPE_REWORK / NEW_AUTHORITY_REQUIRED / INDETERMINATE`;
- distinct new attempt identity / ExecutionId;
- exact fresh grant;
- exact fresh applicable reservation evidence;
- corrective binding carried into the next ExecutionSubject;
- no authority creation by evaluator REWORK.

Therefore:

```text
I31-F001 / A17:
CLOSED

I31-F002 / scoped reservation identity:
CLOSED
```

## 6. Overall implementation review

PASS.

Across the accepted candidate lineage, the implementation now substantively satisfies the frozen Slice 3.1 implementation authority:

- bounded `coding_execution` composition package;
- no predecessor rewrites;
- exact Human-grant verification;
- grant-time reservation verification;
- exact WorkPacket conformance before WorkPacketRef;
- WorkspacePlan resolution only from exact WorkPacketRef;
- exact intended-attempt / ExecutionId mapping;
- final fail-closed admission;
- injected AgentRuntime boundary;
- runtime/provider/model identity verification;
- runtime/workspace/evidence binding;
- protected-verification enforcement;
- terminal result independent of runtime self-claims;
- ProposedWorkObservation as evidence only;
- successor/backlog semantics reused from Slice 2.2;
- A17 corrective lineage;
- immutable evaluator handoff;
- implementer cannot self-accept;
- no live provider/model/runtime qualification in implementation tests.

No evidence requires reopening Slices 2.1–2.5.

## 7. Validation

PASS.

Exact-head GitHub Actions run:

`40265141596 — SUCCESS`

for exact subject:

`6dd4296440196b63078b13855b70dff60a386325`.

Observed CI quality steps all succeeded:

- environment synchronization;
- Ruff format;
- Ruff lint;
- Pyright;
- tests;
- build.

Executor-reported local validation additionally establishes:

```text
focused Slice 3.1 tests:
51 passed

full pytest suite:
1,195 passed

uv build:
PASS

git diff --check:
PASS

working tree:
CLEAN
```

No live runtime, OpenCode, provider, model, external service, real-project credential, or real-project execution occurred.

## 8. Remaining governance boundary

Independent implementation review is complete, but this record does not grant Human implementation acceptance.

Current state after this evaluation:

```text
Slice 3.1 design:
ACCEPTED

Slice 3.1 implementation candidate:
6dd4296440196b63078b13855b70dff60a386325

Independent implementation evaluation:
RLY-S31-IMPL-EVAL-003 — ACCEPT

Human implementation acceptance:
PENDING

Production execution:
NOT AUTHORIZED

Live AgentRuntime/provider/model execution:
NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED

Canonical promotion:
NOT AUTHORIZED
```

A separate Human acceptance/promotion decision is required before changing those states.

## 9. Final disposition

```text
Exact implementation subject:
6dd4296440196b63078b13855b70dff60a386325

Independent implementation evaluation:
RLY-S31-IMPL-EVAL-003 — ACCEPT

I31-F001:
CLOSED

I31-F002:
CLOSED

Lineage:
PASS

Authorized scope:
PASS

Predecessor freeze:
PASS

A01-A22:
SUBSTANTIVELY SATISFIED

Focused tests:
51 PASS

Full suite:
1,195 PASS

CI:
PASS

Implementation acceptance:
PENDING HUMAN DECISION

Execution:
NOT AUTHORIZED

Canonical promotion:
NOT AUTHORIZED
```

**ACCEPT — the Slice 3.1 implementation is technically ready for Human implementation acceptance and subsequent separately authorized canonicalization/execution gates.**
