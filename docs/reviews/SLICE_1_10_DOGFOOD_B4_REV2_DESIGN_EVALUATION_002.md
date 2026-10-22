# Slice 1.10 Dogfood B4 Revision 2 — Independent Design Evaluation 002

**Document class:** Immutable independent design evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Project:** Relay  
**Increment:** B4 Revision 2 — Protocol / Deterministic Evidence Runner  
**Record:** `RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-002`  
**Outcome:** `REWORK`

## Evaluated composite

```text
Design authority:
RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001 — AUTHORIZED

Base Revision 2:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da

Prior independent evaluation:
RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-001 — REWORK

Rework 1:
cfba7884c3fe927c31195ae0c1a10c9666c3bc9f

Branch:
design/1.10-dogfood-b4-rev2-protocol-runner

Rework delta from prior evaluation:
1 commit ahead / 0 behind

Exact-head CI:
PASS
```

## Independent summary

The composite is materially improved and the original blocking findings are closed.

### F001 — CLOSED

Rework 1 defines `B4QuestionContractV1` with:

```text
question_id
question_text
required_dimensions[]
response_schema
```

and requires:

- the complete operator-visible contract to be delivered to the fresh operator;
- `required_dimensions[]` to be included in the question-contract digest;
- `B4AnswerSetV1` to bind to the same question-set ID/digest;
- the evaluator to bind to the same contract;
- the evaluator to score no mandatory dimension absent from that visible contract.

This closes the hidden-rubric defect without exposing expected factual values.

### F002 — CLOSED

Rework 1 makes both harness output streams durable before child launch:

- stdout exclusive-create file;
- stderr exclusive-create file;
- both passed directly to the child;
- both flushed/fsynced/closed after termination;
- both hashed over exact bytes.

It also introduces `B4PrepareResultV1` as a durable prepare-phase result and requires it to be written before any success-only preparation manifest or operator-input envelope.

A post-launch harness/validation failure no longer depends on success-path manifest creation to preserve its forensic evidence.

### O001 — CLOSED

`B4AnswerSetV1` is now the single canonical operator declaration for:

- `inspected_sources[]`;
- `prohibited_sources_accessed[]`.

Terminal evidence copies those fields deterministically rather than recollecting them.

Runner-observed access, if implemented, is explicitly distinct evidence.

## F003 — Spawn-failure state is not defined

**Severity:** BLOCKING  
**Class:** deterministic prepare-state totality

A narrow gap remains between capture setup and successful child execution.

The reworked state machine is:

```text
establish stdout/stderr captures
    ->
invoke harness EXACTLY ONCE
    ->
child exit / validation
```

The design defines:

- capture-setup failure before spawn: `INVALID_CAPTURE_SETUP`, invocation count 0;
- child non-zero / output / protocol failures after spawn;
- durable post-launch `B4PrepareResultV1`.

But it does not define the state where:

1. stdout and stderr files were successfully opened;
2. the runner attempts to spawn the harness;
3. process creation itself fails before a child starts, e.g. an `OSError` / executable-launch failure.

In that state:

- capture setup succeeded, so `INVALID_CAPTURE_SETUP` is inaccurate;
- no child existed, so `INVALID_HARNESS_EXIT` is inaccurate;
- there is no exit code;
- `execution_started` should be false;
- harness invocation count should remain 0;
- the design does not say whether/how `B4PrepareResultV1` is written.

This leaves one deterministic prepare outcome without an explicit terminal transition.

For a design whose purpose is to make the execution protocol deterministic and auditable, the prepare state machine should be total.

## Required correction

Add an explicit spawn-failure outcome, recommended:

`INVALID_HARNESS_SPAWN`

or equivalently named `INVALID_EXEC_START`.

Normative behavior when capture files exist but child creation fails:

```text
execution_started = false
harness_invocation_count = 0
harness_exit_code = null

flush/fsync/close stdout + stderr
hash both capture files
write + fsync B4PrepareResultV1
failure_stage = "spawn"
failure_code = stable runner classification
prepare_outcome = INVALID_HARNESS_SPAWN

do not create B4PrepareManifestV1
do not create operator-input envelope
do not retry under the same authority
STOP
```

Add a focused test proving:

```text
capture setup succeeds
child spawn is forced to fail
harness invocation count remains 0
stdout/stderr files remain preserved
B4PrepareResultV1 records INVALID_HARNESS_SPAWN
no success manifest/operator envelope exists
```

No product or harness semantic change is required.

## Scope review

The composite remains within the authorized B4 Revision 2 scope.

No unauthorized expansion was found into:

- product read-model semantics;
- lifecycle/persistence;
- generic execution framework work;
- B4 attempt 006;
- Slice 2.2;
- Phase 3.

The preferred implementation footprint remains proportionate:

```text
scripts/b4_execution_runner.py
scripts/b4_question_contract_v1.json
tests/integration/test_b4_execution_runner.py
```

## Checklist

```text
Original B4 scientific objective preserved:
YES

F001 question-contract visibility:
CLOSED

F002 stdout/stderr + post-launch durability:
CLOSED

O001 source inventory:
CLOSED

Expected factual answers hidden:
YES

Accepted read-only harness semantics unchanged:
YES

Operational DB read-only:
YES

Semantic scoring excluded from runner:
YES

No-overwrite / no automatic retry:
YES

Prepare state machine total:
NO — F003

Implementation scope bounded:
YES

Attempt 006 separately governed:
YES

Slice 2.2 closed:
YES
```

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-002 — REWORK

Composite:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da
+
cfba7884c3fe927c31195ae0c1a10c9666c3bc9f

F001:
CLOSED

F002:
CLOSED

O001:
CLOSED

Blocking finding:
F003 — explicit harness-spawn failure state missing

B4 Revision 2 direction:
SOUND

Runner implementation:
NOT AUTHORIZED

B4 attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```
