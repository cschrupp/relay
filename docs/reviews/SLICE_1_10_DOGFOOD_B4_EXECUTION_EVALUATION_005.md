# Slice 1.10 Dogfood B4 — Cold-Start Result Evaluation 005

**Document class:** Immutable independent result evaluation
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-EVAL-005`
**Outcome:** `FAIL — PROTOCOL/DESIGN AMBIGUITY ESTABLISHED`

## Evaluated subject

```text
Authority:
RLY-S110-DOGFOOD-B4-EXEC-AUTH-005 — AUTHORIZED

Execution checkout:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Execution worktree:
/tmp/relay-b4-cold-start-pinned

Raw harness capture:
b4-cold-start-harness-attempt-005.json

Raw harness SHA-256:
7ba9e613a7536277c6d6472a3eb2a53891312774a38e79dc60ed67f64330b148

Operator evidence:
b4-cold-start-operator-evidence-attempt-005.json

Operator evidence SHA-256:
ba48e959b49405421266a7b250e7b71038c94f63e7449962286aafd37af24500

DB SHA before:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

DB SHA after:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e
```

## Control validity

Attempt 005 satisfies the B4 custody and evidence controls.

- cold-start declaration: PASS;
- exact checkout/worktree: PASS;
- worktree clean: PASS;
- accepted harness Git blob identities: PASS;
- DB pre-run digest: PASS;
- single harness invocation: PASS;
- atomic raw-output capture: PASS;
- raw-output JSON validation: PASS;
- raw-output SHA-256: PRESENT;
- `query_only == 1`: PASS;
- schema version 8: PASS;
- canonical operator evidence packet: PRESENT;
- operator evidence SHA-256: PRESENT / SEALED;
- prohibited-source access: NONE reported;
- DB before/after equality: PASS;
- B4 self-scoring: not performed;
- Slice 2.2 work: not performed.

This is a valid run and is scored normally.

## Mandatory question scoring

### Q1 — PASS

Relay and repository identity were correctly recovered from the operational read model.

### Q2 — PASS

The immutable adoption objective was faithfully recovered.

### Q3 — PASS

The operator correctly distinguished pre-T1 software-project context from Relay-governed lifecycle/history beginning at T1, and correctly separated PRE_GENESIS project origin from the NATIVE_RELAY current Slice.

### Q4 — PASS

The operator recovered the exact complete active leaf frontier as Slice 2.2 — Role Contracts, while correctly refusing to treat frontier presence or PROPOSED lifecycle as authority.

### Q5 — PASS

The exact current Slice ID, title, and definition revision were correctly recovered.

### Q6 — FAIL

Frozen question:

`What lifecycle phase is it in?`

Sealed answer:

`PROPOSED.`

The accepted B4 evaluator boundary requires the answer to report lifecycle **phase, revision, validity, and blockage**. The operational `slice_detail.lifecycle` surface exposes these fields, and the accepted starting state establishes revision 0 / PROPOSED.

The sealed answer is therefore materially incomplete under the frozen scoring contract.

However, this is now the second independent cold-start operator to answer the literal question with the phase alone. Attempt 003 produced the same pattern.

Finding classification:

```text
FORMAL RESULT:
FAIL

PRIMARY CAUSE:
B4 QUESTION / ANSWER-BOUNDARY MISMATCH

OBSERVATION:
The literal operator question asks only for lifecycle phase while the hidden
evaluator contract requires four lifecycle dimensions.
```

This repeated result is evidence that the B4 protocol itself induces a predictable interpretation and should be revised before another scientific rerun.

### Q7 — PASS

The answer correctly separates the historical strict-B0 blocker from the current Slice state and reports no explicit current Slice blocker: situation blockers empty; blockage CLEAR with no reasons.

### Q8 — FAIL

Frozen question:

`What happens next?`

The answer correctly reports the operational projection:

```text
next_work_state = NOT_DETERMINABLE
next_governed_work = empty
```

It then states that the attempt authority directs evidence sealing and independent B4 evaluation, citing the task authority.

That is not an allowed answer source. Attempt-005 authority explicitly states that the execution authority/run card is for pins, safety limits, questions, and evidence instructions only and **is not an answer source**.

At the pinned checkout, the registry-resolved canonical Build Plan states:

```text
next gate  Authorize one exact B4 cold-start dogfood execution
```

while the operational projection itself does not determine a next governed work item.

The sealed answer therefore substitutes the operator-run procedural next step for the governed-project next action.

Formal result: `FAIL`.

As with Q6, this is now a repeated independent failure. Attempt 003 also conflated B4 run progression with the intended governance-next interpretation, though in a different form.

Finding classification:

```text
FORMAL RESULT:
FAIL

PRIMARY CAUSE:
B4 QUESTION-SCOPE AMBIGUITY

OBSERVATION:
"What happens next?" is naturally interpretable as the next step in the current
operator task, while the hidden evaluator contract means the next governed
project action/decision.
```

### Q9 — PASS

No explicit pending Human decision is represented in the current Slice HumanActionProjection. The operator correctly distinguishes the external B4 evaluation handoff from a durable pending Human decision.

### Q10 — FAIL

The operator correctly identifies Slice 2.2 as PROPOSED and correctly states that implementation is not authorized. It also correctly marks Slices 2.3, 2.4, Phase 3, and real-project agent execution as future / planned / not authorized.

However, the immediate missing authority boundary for the current frontier is incomplete.

At the pinned canonical checkout:

```text
CURRENT_BASELINE:
B4 execution and Slice 2.2 design remain unauthorized

TODO:
Keep B4 execution and Slice 2.2 design/implementation closed until separate authorities.

BUILD_PLAN:
Slice 2.2 — Role Contracts:
PLANNED / NOT OPEN / NOT AUTHORIZED
```

The sealed answer states only that Slice 2.2 **implementation** is not authorized. It does not state that Slice 2.2 **design itself is not open / not authorized**, which is the immediate authority boundary B4 is intended to preserve.

Formal result: `FAIL`.

Finding classification:

```text
FORMAL RESULT:
FAIL

PRIMARY CAUSE:
MATERIAL AUTHORITY-BOUNDARY INCOMPLETENESS
```

## Overall result

The frozen scoring rule requires every mandatory question to PASS.

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
Q10  FAIL

Controls  VALID
Overall   FAIL
```

## Cross-attempt diagnosis

Attempt 005 is materially more informative than a simple operator failure.

Two independent valid cold-start runs now show repeated interpretation failures on Q6 and Q8:

```text
Attempt 003:
Q6 FAIL
Q8 FAIL

Attempt 005:
Q6 FAIL
Q8 FAIL
Q10 FAIL
```

Because the operators were independently cold-started and were not told prior outcomes, recurrence is evidence against the hypothesis that these were isolated slips.

### Q6 protocol defect

The visible question asks only for a lifecycle phase while the hidden scoring boundary requires phase + revision + validity + blockage.

### Q8 protocol defect

The visible question `What happens next?` does not explicitly scope “next” to Relay-governed project state, while the scoring contract does.

These are evaluator/operator contract mismatches. Continuing to rerun unchanged would mostly measure whether a model happens to infer hidden evaluator expectations.

### Deterministic evidence-custody finding

Attempt 005 also confirms that atomic raw-output capture and deterministic hashing eliminate the evidence-loss failure seen in attempt 004.

That strengthens the architectural conclusion that deterministic evidence custody belongs in an execution wrapper rather than prompt compliance.

This finding is not a defect in `project_board`, `slice_detail`, or the accepted read-only harness semantics.

## Required next action

Do **not** authorize attempt 006 under the existing B4 question contract.

Open a bounded B4 protocol/design rework to align visible questions with evaluator expectations and to formalize deterministic evidence custody.

At minimum the rework should:

1. make Q6 ask for exactly the lifecycle dimensions that will be scored;
2. scope Q8 explicitly to Relay-governed project next-action / next-decision state, excluding operator-run procedural steps;
3. make Q10 require the exact missing authority boundary for current Slice design vs implementation;
4. preserve the same source-precedence rules and cold-start custody;
5. specify deterministic evidence capture/sealing as runner responsibility rather than model memory.

The rework must not encode the factual expected answers; it should only make the observable question contract match the evaluator contract.

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-EXEC-EVAL-005
FAIL — PROTOCOL/DESIGN AMBIGUITY ESTABLISHED

B4 attempt 005:
VALID RUN / FAIL

B4 read-only harness semantics:
NO REWORK INDICATED

B4 evidence execution wrapper:
DETERMINISTIC HARDENING INDICATED

B4 question/evaluator contract:
REWORK REQUIRED

B4 acceptance:
NOT ELIGIBLE

Attempt 006:
DO NOT AUTHORIZE UNDER CURRENT DESIGN

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED
```
