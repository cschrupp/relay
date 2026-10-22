# Slice 1.10 Dogfood B4 — Cold-Start Result Evaluation 003

**Document class:** Immutable independent result evaluation
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-EVAL-003`
**Outcome:** `FAIL`

## Evaluated subject

```text
Authority:
RLY-S110-DOGFOOD-B4-EXEC-AUTH-003 — AUTHORIZED

Execution checkout:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Execution worktree:
/tmp/relay-b4-cold-start-pinned

Operator evidence:
b4-cold-start-operator-evidence-attempt-003.json

Operator evidence SHA-256:
062e715377e187276d8d0e0be00f280e14abf375e6982ce5f12683a26e12685b

Raw harness output SHA-256:
7ba9e613a7536277c6d6472a3eb2a53891312774a38e79dc60ed67f64330b148

DB SHA before:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

DB SHA after:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e
```

## Control validity

The execution controls are valid.

- fresh-operator declaration: PASS;
- exact execution checkout: PASS;
- clean worktree: PASS;
- accepted harness Git blob identities: PASS;
- DB pre-run digest: PASS;
- `query_only == 1`: PASS;
- schema version 8: PASS;
- prohibited-source access: NONE reported;
- harness invocation count: one;
- DB before/after digest equality: PASS;
- B4 self-scoring: not performed;
- Slice 2.2 work: not performed.

The run is therefore a valid B4 execution and is scored normally.

## Mandatory question scoring

### Q1 — PASS

The operator correctly identified Project Relay and repository
`github.com/cschrupp/relay` from the operational Project/adoption projection.

### Q2 — PASS

The operator faithfully summarized the immutable adoption
`project_objective`: Relay is a governance control plane for agentic software
engineering preserving Human authority, exact baselines, bounded work, evidence,
independent evaluation, rework, acceptance, and promotion while delegating coding
execution to external runtimes.

### Q3 — PASS

The answer correctly distinguished pre-T1 project existence/context from
Relay-governed lifecycle beginning at T1 and did not fabricate pre-T1 Relay
history.

### Q4 — PASS

The operator recovered the exact active leaf frontier as one complete frontier:

`slc_01a15754-1123-7535-9ded-6a564518e347` —
`Slice 2.2 — Role Contracts`, definition revision 2.

### Q5 — PASS

The exact current Slice identity, title, ID, and definition revision were correct.

### Q6 — FAIL

Question:

`What lifecycle phase is it in?`

The frozen B4 source matrix requires the answer to state the represented lifecycle
**phase, revision, validity, and blockage**.

The sealed answer stated only:

`PROPOSED`

The durable/read-model state exposes a `SliceLifecycle` containing phase,
revision, validity, and blockage. The accepted B4 baseline establishes lifecycle
revision 0 / `PROPOSED`; the operator's own Q7 source establishes blockage
`CLEAR`. The operator did not report lifecycle revision or validity and did not
include blockage in Q6.

This is materially incomplete under the frozen answer boundary. The information
was available through the inspected allowed `slice_detail.lifecycle` projection,
so this is an operator-answer deficiency rather than missing durable state or an
unavailable product surface.

Result: `FAIL`.

### Q7 — PASS

The operator correctly reported that no explicit current blockers are projected:
the Project situation blocker list is empty and the current Slice blockage is
`CLEAR` with no reasons. The answer appropriately limited the claim to recorded
state.

### Q8 — FAIL

Question:

`What happens next?`

The operational board correctly yielded:

```text
next_governed_work = empty
next_work_state = NOT_DETERMINABLE
```

However, the sealed answer then stated that the canonical Build Plan
“identifies one exact B4 cold-start execution as the next gate; this attempt
executed that gate.”

At the exact pinned execution checkout
`63dd5071295fe2cd78f346b3a401a9030b6bb4c3`, the registry-resolved canonical
Build Plan states:

```text
next gate  Authorize one exact B4 cold-start dogfood execution
```

and the canonical Current Baseline states that B4 cold-start execution is
eligible for separate authority while B4 execution remains unauthorized at that
pinned state.

The operator therefore collapsed two distinct governance actions:

1. **authorize** one exact B4 execution; and
2. **execute** an already authorized B4 attempt.

Relay's B4 matrix explicitly requires NEXT to distinguish an exact authorized
action from a governance decision and prohibits upgrading planning/order into
authority. The phrase “this attempt executed that gate” is not what the pinned
canonical projection says and materially loses the authorization/execution
boundary.

The correct pinned-state orientation is that the operational board itself does
not determine next governed work, while the canonical governance projection says
the next governance gate is Human authorization of one exact B4 cold-start
execution. The separate attempt-003 execution authority is run custody, not a
basis for rewriting the pinned canonical answer.

Result: `FAIL`.

### Q9 — PASS

The operator correctly reported that the current Slice's
`HumanActionProjection` contains no explicit pending Human decision. It did not
mistake available Human controls for an already pending decision.

### Q10 — PASS

The operator correctly identified Slice 2.2 as `PROPOSED` rather than
authorized and correctly classified Slices 2.2–2.4 / Phase 3 as planned future
work lacking the necessary opening/implementation authority.

## Overall result

The accepted B4 scoring rule is:

- any mandatory FAIL => overall `FAIL`;
- otherwise any INDETERMINATE => overall `INDETERMINATE`;
- PASS only if all ten mandatory questions PASS and controls are valid.

Results:

```text
Q1   PASS
Q2   PASS
Q3   PASS
Q4   PASS
Q5   PASS
Q6   FAIL
Q7   PASS
Q8   FAIL
Q9   PASS
Q10  PASS

Controls  VALID
Overall   FAIL
```

## Finding classification

The two failures are not custody failures and do not establish a defect in the
accepted read-only harness or operational database.

```text
Q6:
OPERATOR ERROR / MATERIAL INCOMPLETENESS
Available lifecycle fields were not fully reported.

Q8:
OPERATOR ERROR / GOVERNANCE-BOUNDARY COLLAPSE
Authorization and execution were conflated despite the pinned canonical
projection distinguishing them.
```

The product surfaces exposed the material facts needed to answer both questions.
No product or harness rework is justified from this run alone.

## Rework / rerun boundary

Under the accepted B4 design, B4 is not accepted.

A future rerun requires a separate Human authority and must remain cold-start and
sealed. Do not repair the sealed attempt-003 answers.

Any rerun should target the failed mandatory questions without exposing the
evaluator source matrix or expected answers to the fresh operator. The purpose is
still to test independent recovery, not coached reproduction.

No Slice 2.2 design or implementation authority follows from this result.

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-EXEC-EVAL-003 — FAIL

B4 attempt 001:
CONSUMED / FAIL_CLOSED

B4 attempt 002:
CONSUMED / FAIL_CLOSED

B4 attempt 003:
VALID RUN / FAIL

B4 design:
NO REWORK

B4 read-only harness:
NO REWORK

B4 product-state recovery:
8 / 10 MANDATORY QUESTIONS PASS
Q6 FAIL
Q8 FAIL

B4 Human result acceptance:
NOT ELIGIBLE

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED

Further B4 rerun:
NOT AUTHORIZED
```
