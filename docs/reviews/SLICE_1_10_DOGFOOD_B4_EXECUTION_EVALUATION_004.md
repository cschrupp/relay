# Slice 1.10 Dogfood B4 — Cold-Start Result Evaluation 004

**Document class:** Immutable independent result evaluation
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-EVAL-004`
**Outcome:** `INDETERMINATE / INVALID RUN — INCOMPLETE EVIDENCE`

## Evaluated subject

```text
Authority:
RLY-S110-DOGFOOD-B4-EXEC-AUTH-004 — AUTHORIZED

Execution checkout:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Execution worktree:
/tmp/relay-b4-cold-start-pinned
```

## Independent finding

Attempt 004 passed checkout and DB preflight. The accepted read-only harness ran exactly once with
`query_only = 1` and Relay schema version 8. The operational DB digest matched before and after,
and no Slice 2.2 work or B4 scoring occurred.

However, the operator did not preserve the raw harness JSON as required, did not compute its
SHA-256, did not create the canonical operator evidence packet, and did not seal Q1-Q10 answers.

Therefore the attempt cannot be independently scored under the accepted B4 evidence contract.

## Evidence-contract failure

Required but missing:

- raw harness-output SHA-256;
- canonical operator evidence packet;
- sealed verbatim Q1-Q10 answer set;
- evidence-packet SHA-256;
- answer-sealed timestamp.

The operator correctly did not rerun the harness or reconstruct the missing raw output after the
fact. That preserves custody integrity but leaves the attempt incomplete.

Draft answers are not scoreable evidence.

## Control state

```text
Checkout/preflight: PASS
Harness invocation count: 1
query_only: 1
schema version: 8
DB unchanged: YES
WAL: unchanged
SHM: same size and SHA-256; mtime advanced
Prohibited-source access: none reported
B4 self-scoring: NO
Slice 2.2 work: NO
```

A sidecar modification-time change alone does not invalidate B4; no sidecar cleanup or checkpoint
is required.

## Attempt accounting

```text
Attempt 004:
STARTED / HARNESS READ COMPLETED / EVIDENCE INCOMPLETE / CONSUMED

Answer phase:
DRAFTED BUT NOT SEALED

B4 semantic scoring:
NOT PERMITTED

B4 result:
NOT ESTABLISHED
```

## Important chronology correction

Attempt 003 is not awaiting evaluation. It was already independently evaluated under:

`RLY-S110-DOGFOOD-B4-EXEC-EVAL-003 — FAIL`

with Q6 and Q8 failing. Attempt 004 does not supersede or reopen that result.

## Rework boundary

No Relay product-state or read-only harness defect is established by attempt 004.

A future attempt requires a new Human authority. The execution protocol should make raw-output
capture atomic with harness invocation so the output cannot be lost before hashing. A fresh
operator still must not receive prior B4 answers, evaluations, or information about previous
question outcomes.

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-EXEC-EVAL-004
INDETERMINATE / INVALID RUN — INCOMPLETE EVIDENCE

Attempt 004:
CONSUMED

B4 design:
NO REWORK

B4 read-only harness:
NO REWORK

B4 acceptance:
NOT ESTABLISHED

Further attempt:
NOT AUTHORIZED

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED
```
