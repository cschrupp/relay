# Slice 1.10 Dogfood B4 — Cold-Start Execution Evaluation 002

**Document class:** Immutable independent execution evaluation
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-EVAL-002`
**Outcome:** `FAIL_CLOSED / NO DB ACCESS / NO ANSWER PHASE`

## Evaluated subject

```text
Authority:
RLY-S110-DOGFOOD-B4-EXEC-AUTH-002 — AUTHORIZED

Execution worktree:
/tmp/relay-b4-cold-start-pinned

Required HEAD:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Observed HEAD:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Worktree:
CLEAN
```

## Independent finding

Attempt 002 stopped during preflight before operational DB access and before harness invocation.

The fresh operator correctly verified the worktree path, exact pinned HEAD, and clean status. It then attempted to verify the harness content pins by computing SHA-256 file digests and comparing those values to the supplied 40-hex Git blob object IDs. Those are different hash domains and are not directly comparable.

The operator therefore reported a false pin mismatch and stopped fail-closed.

No operational DB access occurred. No harness invocation occurred. Q1–Q10 were not entered. No operator evidence packet was created. No B4 scoring was performed. No Slice 2.2 work occurred.

## Root-cause classification

```text
Class:
EXECUTION-CUSTODY / RUN-CARD VERIFICATION AMBIGUITY

Accepted harness Git blob IDs:
scripts/b4_readonly_harness.py
f98350ff14dbfb1bf6388de88fff366e67ec1afd

tests/integration/test_b4_readonly_harness.py
6708eb8b1a3fcb8484a227a447ace678c3ec20d0

Incorrect operator comparison:
SHA-256(file bytes) == Git blob object ID

Correct verification:
git rev-parse HEAD:scripts/b4_readonly_harness.py
git rev-parse HEAD:tests/integration/test_b4_readonly_harness.py
```

The prior independent preparation had already established that the pinned checkout contains those exact Git blob IDs.

The attempt-002 authority/run card named the blob values but did not freeze the exact Git-object verification command. A fresh operator could therefore choose an incompatible digest method. This is a test-custody/protocol defect, not a Relay product-state defect.

## Attempt accounting

```text
B4 execution attempt 002:
STARTED / PRECHECK FAIL_CLOSED / CONSUMED

DB access:
NONE

Harness invocation:
NONE

Answer phase:
NOT ENTERED

B4 semantic result:
NOT ESTABLISHED
```

## Rework boundary

No B4 design rework is indicated.

No read-only harness rework is indicated.

Before any further execution attempt, the operator run card must freeze the harness-pin verification command itself, for example:

```bash
git rev-parse HEAD:scripts/b4_readonly_harness.py
git rev-parse HEAD:tests/integration/test_b4_readonly_harness.py
```

and compare the returned Git object IDs byte-for-byte with the accepted blob IDs.

A future attempt requires a new Human execution authority. Attempt 002 cannot be reused.

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-EXEC-EVAL-002 — FAIL_CLOSED / NO DB ACCESS / NO ANSWER PHASE

B4 attempt 001:
CONSUMED / FAIL_CLOSED

B4 attempt 002:
CONSUMED / FAIL_CLOSED

B4 design:
NO REWORK

B4 read-only harness:
NO REWORK

B4 acceptance:
NOT ESTABLISHED

Further attempt:
NOT AUTHORIZED
```

This evaluation does not authorize another B4 execution attempt, Slice 2.2 design, or any downstream work.
