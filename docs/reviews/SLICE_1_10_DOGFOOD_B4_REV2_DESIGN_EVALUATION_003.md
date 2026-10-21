# Slice 1.10 Dogfood B4 Revision 2 — Independent Design Evaluation 003

**Document class:** Immutable independent design evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Increment:** B4 Revision 2 — Protocol / Deterministic Evidence Runner  
**Record:** `RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-003`  
**Outcome:** `ACCEPT`

## Evaluated composite

```text
Design authority:
RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001 — AUTHORIZED

Revision 2 base:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da

Revision 2 Rework 1:
cfba7884c3fe927c31195ae0c1a10c9666c3bc9f

Prior evaluation:
RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-002 — REWORK

Revision 2 Rework 2:
0bb228c13d5f3ee4dce4167705cc0f444ece350a

Branch:
design/1.10-dogfood-b4-rev2-protocol-runner

Exact Rework-2 head CI:
PASS
```

## Independent conclusion

The complete Revision 2 + Rework 1 + Rework 2 composite is **ACCEPTED**.

The design now resolves the B4 defects established by attempts 001–005 without changing Relay product-state semantics or leaking expected factual answers to the fresh operator.

The architecture has a coherent separation of responsibility:

```text
deterministic runner
    -> execution and forensic protocol

fresh operator
    -> semantic interpretation

independent evaluator
    -> semantic correctness judgment

Human Authority
    -> result acceptance / successor authority
```

This is consistent with the stated Relay boundary that deterministic protocol correctness should not depend on LLM prompt compliance where code can enforce it.

## Finding closure

### F001 — CLOSED

The hidden-rubric defect is closed.

`B4QuestionContractV1` makes each operator-visible question a structured contract containing:

```text
question_id
question_text
required_dimensions[]
response_schema
```

The complete contract is hashed, supplied to the fresh operator, bound into `B4AnswerSetV1`, and bound again into independent evaluation.

The evaluator is explicitly prohibited from requiring a mandatory semantic dimension not present in the operator-visible contract.

Expected factual values remain absent.

### F002 — CLOSED

The deterministic evidence-custody defect is closed.

Before child launch:

- stdout capture is exclusively created;
- stderr capture is exclusively created.

After successful child creation:

- the accepted harness executes at most once;
- stdout/stderr are durable child destinations rather than LLM/session output;
- both streams are flushed/fsynced/closed and hashed;
- the runner produces a durable `B4PrepareResultV1` before success-only manifest/operator-input generation;
- child/output/protocol failure has an explicit terminal result and no retry path.

The design therefore removes the attempt-004 class of “harness ran successfully but evidence was never preserved.”

### O001 — CLOSED

`B4AnswerSetV1` is the single canonical operator declaration for inspected/prohibited sources.

Terminal evidence copies that declaration deterministically rather than recollecting it.

### F003 — CLOSED

Rework 2 completes the process-creation boundary.

If capture setup succeeds but process creation fails:

```text
execution_started = false
harness_invocation_count = 0
harness_exit_code = null

stdout/stderr preserved + hashed

B4PrepareResultV1:
  failure_stage = spawn
  prepare_outcome = INVALID_HARNESS_SPAWN

no success manifest
no operator envelope
no retry
STOP
```

This gives process spawn failure its own terminal state rather than misclassifying it as capture failure or child exit failure.

The prepare state machine is sufficiently total for implementation.

## Full design checklist

```text
Original B4 scientific objective preserved:
PASS

Authorized scope respected:
PASS

Question/evaluator contract one-to-one:
PASS

All evaluator mandatory dimensions operator-visible:
PASS

Expected factual answers hidden:
PASS

Question contract deterministically identified and hashed:
PASS

Answer set bound to exact question contract:
PASS

Evaluator bound to exact question contract:
PASS

Accepted read-only harness semantics unchanged:
PASS

Product read models unchanged:
PASS

Operational DB remains read-only:
PASS

Deterministic checkout qualification:
PASS

Deterministic Git-object qualification:
PASS

Exact-once harness boundary:
PASS

Raw stdout durable before interpretation:
PASS

Raw stderr durable before interpretation:
PASS

Spawn failure explicitly represented:
PASS

Post-launch terminal prepare evidence durable:
PASS

No-overwrite evidence semantics:
PASS

No automatic retry under same authority:
PASS

DB before/after proof:
PASS

WAL/SHM remain observational:
PASS

Semantic scoring excluded from runner:
PASS

Operator source declaration single-source:
PASS

Implementation footprint bounded:
PASS

Generic framework expansion deferred:
PASS

Attempt 006 separately governed:
PASS

Slice 2.2 remains closed:
PASS
```

## Non-blocking implementation observations

### O002 — partial capture-setup failure

`INVALID_CAPTURE_SETUP` is already a defined terminal outcome.

During implementation, if one capture file is created successfully and creation of the second fails, the runner should:

- close/fsync the file that was created where applicable;
- preserve it rather than delete/truncate it;
- record the capture-setup failure through the prepare-result path where the evidence filesystem permits;
- keep `execution_started=false` and invocation count 0;
- never spawn/retry.

This is an implementation detail within the accepted `INVALID_CAPTURE_SETUP` semantics, not a design blocker.

### O003 — NOT_PERFORMED vs failed validation

For pre-execution outcomes such as `INVALID_HARNESS_SPAWN`, implementation should prefer an explicit typed `NOT_PERFORMED` state for validations that could not occur, rather than using bare `false` if that would conflate “not checked” with “checked and failed.”

Rework 2 already requires those meanings not be conflated, so this is schema finalization rather than design rework.

## Implementation scope accepted

The preferred minimal implementation is proportionate:

```text
scripts/b4_execution_runner.py
scripts/b4_question_contract_v1.json
tests/integration/test_b4_execution_runner.py
```

The following should remain unchanged unless a separately reviewed blocker is discovered:

```text
scripts/b4_readonly_harness.py
src/relay_engine/board/*
src/relay_engine/lifecycle/*
src/relay_engine/persistence/*
operational database schema/state
```

A future generic `GovernedCommandRunner` / `EvidenceRun` abstraction remains explicitly outside this increment.

## Next governance boundary

This evaluation accepts the design only.

It does not authorize implementation.

Required sequence:

```text
R2 composite design
    -> INDEPENDENT ACCEPT      [this record]
    -> HUMAN DESIGN ACCEPTANCE
    -> separate implementation authority
    -> bounded runner implementation
    -> independent implementation evaluation
    -> Human implementation acceptance
    -> separately authorized B4 attempt 006
```

B4 attempt 006 must still run all ten Revision 2 questions under fresh cold-start custody.

B4 success would make Slice 2.2 design eligible to open; it would not itself authorize Slice 2.2.

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-003 — ACCEPT

Accepted composite:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da
+
cfba7884c3fe927c31195ae0c1a10c9666c3bc9f
+
0bb228c13d5f3ee4dce4167705cc0f444ece350a

F001:
CLOSED

F002:
CLOSED

O001:
CLOSED

F003:
CLOSED

B4 Revision 2 design:
INDEPENDENTLY ACCEPTED

Human design acceptance:
PENDING

Runner implementation:
NOT AUTHORIZED

B4 attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```
