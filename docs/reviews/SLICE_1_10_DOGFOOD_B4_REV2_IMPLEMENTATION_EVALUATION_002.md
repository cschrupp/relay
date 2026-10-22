# Slice 1.10 Dogfood B4 Revision 2 — Independent Implementation Evaluation 002

**Document class:** Immutable independent implementation evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-S110-DOGFOOD-B4-R2-IMPL-EVAL-002`  
**Outcome:** `ACCEPT`

## Evaluated subject

Implementation authority: `RLY-S110-DOGFOOD-B4-R2-IMPL-AUTH-001 — AUTHORIZED`

Implementation branch: `implementation/1.10-dogfood-b4-rev2-runner`

Prior independent evaluation: `RLY-S110-DOGFOOD-B4-R2-IMPL-EVAL-001 — REWORK`

Rework parent: `b6a072135d372d526fa19b0f6b7d3e1bda25faa8`

Rework candidate: `9b6aa95ab366dcf99981adddc10d917ef15e1dc8`

Candidate relation to rework parent: 1 commit ahead / 0 behind.

Changed files relative to the rework parent:

- `scripts/b4_execution_runner.py`
- `tests/integration/test_b4_execution_runner.py`

The canonical B4 question contract is unchanged from the originally reviewed implementation candidate. The accepted read-only harness and accepted harness-test Git blobs are unchanged from the implementation-authority baseline.

## Independent re-evaluation summary

Rework 1 is bounded to F001 and F002 and does not reopen previously accepted implementation aspects.

### F001 — validation tri-state dependency semantics

**Disposition: CLOSED**

The runner now leaves `query_only_valid` and `relay_schema_version_valid` at their initialized `NOT_PERFORMED` state unless harness stdout has successfully decoded to a JSON object.

For empty stdout, the runner records:

- `stdout_nonempty = FAIL`
- `stdout_json_valid = FAIL`
- `query_only_valid = NOT_PERFORMED`
- `relay_schema_version_valid = NOT_PERFORMED`

For non-empty invalid JSON, the runner records:

- `stdout_nonempty = PASS`
- `stdout_json_valid = FAIL`
- `query_only_valid = NOT_PERFORMED`
- `relay_schema_version_valid = NOT_PERFORMED`

For decoded JSON objects, the protocol fields are actually inspected and independently recorded as PASS or FAIL.

The focused regression test now asserts the complete validation maps for the empty-output and invalid-JSON paths.

This satisfies the accepted tri-state invariant and no longer conflates “not checked” with “checked and failed.”

### F002 — wait-failure terminal capture custody

**Disposition: CLOSED**

After an initial `child.wait()` failure, the runner now enters a bounded child-finalization path.

The helper first checks whether the child is already terminal. If not, it attempts to kill the already-created child and performs one bounded wait using `CHILD_REAP_TIMEOUT_SECONDS = 5`.

If termination/reap is confirmed, capture durability and hashing occur only afterward. The existing wait-failure result remains a controlled `INVALID_HARNESS_EXIT / HARNESS_WAIT_FAILED`.

If termination cannot be confirmed, the runner:

- does not spawn another harness child;
- attempts to close the parent capture handles;
- records stdout/stderr size and SHA-256 as null;
- returns `INVALID_PREPARE_EVIDENCE`;
- records `failure_stage = wait`;
- records `failure_code = CHILD_TERMINATION_UNCONFIRMED`;
- does not claim terminal capture digests.

Focused tests prove both branches:

1. capture hashing is rejected unless the child has been reaped;
2. an unreapable child produces no capture hashes.

This closes the exact evidence-custody defect identified by F002.

## Scope and immutable identities

Independent Git comparison confirms the rework candidate is exactly one commit ahead of `b6a072135d372d526fa19b0f6b7d3e1bda25faa8` and changes only the runner and runner integration tests.

Verified unchanged identities:

- B4 question-contract blob: `17e788cd15961cd5609670292aea906c6e8de9f4` before/after Rework 1.
- Accepted read-only harness blob: `f98350ff14dbfb1bf6388de88fff366e67ec1afd` at authority baseline and Rework 1.
- Accepted harness-test blob: `6708eb8b1a3fcb8484a227a447ace678c3ec20d0` at authority baseline and Rework 1.

No question wording/dimensions, accepted harness semantics, product source, dependency, execution authority, B4 attempt authority, or Slice 2.2 authority changed.

## Validation evidence

Implementation handoff reports:

- focused runner tests: 59 passed;
- full test suite: 939 passed;
- repository-contract tests: 43 passed;
- Ruff lint: PASS;
- scoped Ruff format check for the touched implementation surface: PASS;
- Pyright: PASS;
- build: PASS.

The repository-wide `uv run ruff format --check .` was executed but does not pass because Ruff reports formatting in the immutable prior evaluation document’s fenced sample. That immutable evaluation record was correctly left unchanged. This is a repository-tooling / immutable-history interaction outside the Rework 1 Python change surface; it does not constitute an implementation defect in the candidate and must not be “fixed” by rewriting the immutable evaluation record.

No GitHub status checks are attached to the candidate SHA, so the reported local validation remains supporting evidence rather than independently reproduced CI evidence.

## Regression assessment

No new blocking defect was found in the bounded corrective delta.

The child-finalization helper has one terminality criterion: either `poll()` establishes a return code or the bounded `wait()` returns a code. If neither establishes termination, the runner declines to hash the captures. This preserves fail-closed evidence semantics.

The rework introduces no second process-spawn path and does not weaken the exact-once harness invocation boundary.

## Independent disposition

`RLY-S110-DOGFOOD-B4-R2-IMPL-EVAL-002 — ACCEPT`

- Candidate: `9b6aa95ab366dcf99981adddc10d917ef15e1dc8`
- Scope: PASS
- Architecture: PASS
- Question contract / accepted harness custody: PASS
- F001: CLOSED
- F002: CLOSED
- Deterministic evidence protocol: PASS
- Runner implementation: ACCEPTED FOR HUMAN DECISION

This independent acceptance does not itself authorize execution.

B4 attempt 006 remains **NOT AUTHORIZED**.

Slice 2.2 remains **NOT OPEN / NOT AUTHORIZED**.

The correct next governance step is Human acceptance or rejection of this exact implementation candidate. Only after a separate Human authority may any subsequent B4 execution be opened.
