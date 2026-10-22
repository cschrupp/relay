# Slice 1.10 Dogfood B4 — Relay Dogfood Acceptance Design Revision 2 Rework 2

**Authority:** `RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001`  
**Rework basis:** `RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-002 — REWORK`  
**Amends composite:** Revision 2 base `ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da` + Rework 1 `cfba7884c3fe927c31195ae0c1a10c9666c3bc9f`  
**Status:** REWORK CANDIDATE — NOT ACCEPTED; DOES NOT AUTHORIZE IMPLEMENTATION OR EXECUTION

## 1. Rework decision

This amendment closes only:

`F003 — explicit harness-spawn failure state missing`

All Revision 2 and Rework 1 provisions remain normative except where explicitly amended below.

No product, read-model, lifecycle, persistence, operational-DB, question-contract, evaluator-contract, or accepted read-only harness semantic change is introduced.

## 2. Invocation terminology

For B4 Revision 2:

`harness_invocation_count` means the number of harness child processes successfully created.

Therefore:

- before process creation succeeds: `harness_invocation_count = 0`;
- after one child process is successfully created: `harness_invocation_count = 1`;
- no authority permits a second child process.

An attempted but failed process creation does not increment the invocation count.

`execution_started` becomes `true` only after child creation succeeds.

## 3. New prepare outcome

Add:

`INVALID_HARNESS_SPAWN`

to the allowed `B4PrepareResultV1.prepare_outcome` values.

The complete relevant prepare outcomes are now:

```text
PREPARED
INVALID_PRECHECK
INVALID_CAPTURE_SETUP
INVALID_HARNESS_SPAWN
INVALID_HARNESS_EXIT
INVALID_HARNESS_OUTPUT
INVALID_HARNESS_PROTOCOL
INVALID_PREPARE_EVIDENCE
```

## 4. Normative spawn-failure transition

The runner enters the spawn boundary only after:

1. deterministic preflight has passed;
2. the stdout capture path has been exclusively created and opened;
3. the stderr capture path has been exclusively created and opened.

The runner then attempts to create exactly one accepted harness child process.

If process creation itself fails before a child exists, for example due to an executable/interpreter launch `OSError`, the runner MUST:

```text
execution_started = false
harness_invocation_count = 0
harness_exit_code = null
```

and MUST then:

1. flush both capture file handles if applicable;
2. fsync both capture files where supported;
3. close both capture files;
4. compute size and SHA-256 over both exact files;
5. write `B4PrepareResultV1` using exclusive-create semantics;
6. record:
   - `failure_stage = "spawn"`;
   - a stable runner-owned failure classification;
   - `prepare_outcome = "INVALID_HARNESS_SPAWN"`;
7. fsync and hash the prepare-result artifact;
8. create no `B4PrepareManifestV1`;
9. create no operator-input envelope;
10. perform no retry under the same authority;
11. STOP.

The runner MUST NOT delete the empty or partially initialized stdout/stderr capture files merely because no child was created. Their existence and digests are evidence of the attempted execution boundary.

## 5. Stable failure classification

The runner MUST NOT persist raw Python exception representations as the only failure classification.

For spawn failure it records a stable runner-owned code, for example:

`HARNESS_PROCESS_CREATION_FAILED`

It MAY additionally record a bounded diagnostic message/class name for debugging, provided that:

- the stable code remains authoritative for protocol classification;
- the diagnostic does not alter protocol semantics;
- no secret/environment dump is required.

The exact stable code name may be finalized during implementation if the same semantics are preserved and tests pin it.

## 6. Revised prepare state machine

The prepare state machine is now total across the intended deterministic boundaries:

```text
START
  |
  +-- deterministic preflight
  |      failure
  |        -> INVALID_PRECHECK
  |        -> execution_started=false
  |        -> invocation_count=0
  |        -> STOP
  |
  +-- establish stdout + stderr exclusive captures
  |      failure
  |        -> INVALID_CAPTURE_SETUP
  |        -> execution_started=false
  |        -> invocation_count=0
  |        -> STOP
  |
  +-- spawn accepted harness
  |      spawn failure
  |        -> preserve/hash stdout + stderr
  |        -> durable B4PrepareResultV1
  |        -> INVALID_HARNESS_SPAWN
  |        -> execution_started=false
  |        -> invocation_count=0
  |        -> STOP
  |
  +-- child successfully created
  |        -> execution_started=true
  |        -> invocation_count=1
  |
  +-- wait for child
  |
  +-- fsync/close/hash stdout + stderr
  |
  +-- child-exit / output / protocol validation
  |      failure
  |        -> durable B4PrepareResultV1(failure)
  |        -> invocation_count=1
  |        -> STOP
  |
  +-- durable B4PrepareResultV1(PREPARED)
  |
  +-- B4PrepareManifestV1
  |
  +-- operator-input envelope
  |
  v
READY_FOR_FRESH_OPERATOR
```

There is no designed path from any terminal failure state back to spawn.

## 7. B4PrepareResultV1 clarification

For `INVALID_HARNESS_SPAWN`, `B4PrepareResultV1` MUST contain at least:

```text
schema_version
authority_id
run_id
attempt_number

execution_started = false
harness_invocation_count = 0
harness_exit_code = null

stdout.path
stdout.size
stdout.sha256

stderr.path
stderr.size
stderr.sha256

validation.stdout_nonempty = false or observed value
validation.stdout_json_valid = false
validation.query_only_valid = false
validation.relay_schema_version_valid = false

failure_stage = "spawn"
failure_code = stable runner-owned spawn-failure code
prepare_outcome = "INVALID_HARNESS_SPAWN"
recorded_at
```

Validation fields that cannot logically have succeeded because no child ran MUST have explicit false/not-performed semantics as frozen by implementation schema; they MUST NOT be omitted ambiguously.

Implementation may choose a typed `NOT_PERFORMED` representation instead of false if that representation is defined consistently across the prepare-result schema. It must not conflate “checked and failed” with “could not be checked because execution never began.”

## 8. Failure of the spawn-failure evidence write itself

Rework 1 already establishes the evidence-filesystem limit.

If stdout/stderr capture exists but the runner cannot persist the required `B4PrepareResultV1` after spawn failure:

- externally report `INVALID_PREPARE_EVIDENCE`;
- do not create success manifest/operator envelope;
- do not retry;
- preserve stdout/stderr capture files where possible.

The design does not claim to make a durable prepare-result artifact possible when its target filesystem cannot accept the artifact.

## 9. Additional acceptance criterion

Add:

**AC22 — total spawn boundary**

If capture setup succeeds but process creation fails, the runner:

- creates no child;
- records `execution_started=false`;
- records `harness_invocation_count=0`;
- records `harness_exit_code=null`;
- preserves and hashes stdout/stderr capture files;
- writes `B4PrepareResultV1` with `INVALID_HARNESS_SPAWN`;
- creates no success manifest/operator envelope;
- does not retry.

## 10. Additional required focused tests

Implementation MUST add at least:

```text
capture setup succeeds + subprocess spawn forced to fail
  -> child never starts
  -> execution_started=false
  -> invocation_count=0
  -> exit_code=null
  -> stdout capture preserved
  -> stderr capture preserved
  -> stdout/stderr digests recorded
  -> B4PrepareResultV1 outcome INVALID_HARNESS_SPAWN
  -> failure_stage spawn
  -> no B4PrepareManifestV1
  -> no operator-input envelope
  -> no second spawn attempt
```

A second test SHOULD force prepare-result persistence failure after a simulated spawn failure and verify the external `INVALID_PREPARE_EVIDENCE` fail-closed path without retry.

## 11. Rework scope audit

This amendment does not:

- modify the B4 question contract;
- expose expected factual answers;
- change evaluator semantics;
- change the read-only harness;
- change Relay product code;
- expand into generic runner architecture;
- authorize implementation;
- authorize B4 attempt 006;
- authorize Slice 2.2.

## 12. Composite design after Rework 2

The Revision 2 composite becomes:

```text
Revision 2 base:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da

Revision 2 Rework 1:
cfba7884c3fe927c31195ae0c1a10c9666c3bc9f

Revision 2 Rework 2:
this amendment
```

Finding disposition:

```text
F001:
CLOSED BY REWORK 1

F002:
CLOSED BY REWORK 1

O001:
CLOSED BY REWORK 1

F003:
DESIGN REWORKED BY REWORK 2
```

## 13. Current gate

```text
RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001 — AUTHORIZED

B4 Revision 2 composite:
READY FOR INDEPENDENT RE-REVIEW

Runner implementation:
NOT AUTHORIZED

B4 attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```
