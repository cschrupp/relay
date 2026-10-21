# Slice 1.10 Dogfood B4 Revision 2 — Independent Implementation Evaluation 001

**Document class:** Immutable independent implementation evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-S110-DOGFOOD-B4-R2-IMPL-EVAL-001`  
**Outcome:** `REWORK`

## Evaluated subject

```text
Implementation authority:
RLY-S110-DOGFOOD-B4-R2-IMPL-AUTH-001 — AUTHORIZED

Authority commit:
47f7a818871426bb5576175c6f6a529353938ff3

Implementation branch:
implementation/1.10-dogfood-b4-rev2-runner

Candidate:
1937309db82f1d1cc03a542c5fc074116c00d3fc

Candidate relation to authority commit:
1 commit ahead / 0 behind

Changed files:
scripts/b4_execution_runner.py
scripts/b4_question_contract_v1.json
tests/integration/test_b4_execution_runner.py
```

Remote candidate publication and three-file scope were independently verified.

No GitHub workflow run is attached to the candidate SHA. The implementation handoff reports the following local validation:

```text
focused tests: 57 passed
full pytest: 937 passed
ruff format: PASS
ruff lint: PASS
pyright: 0 errors / 0 warnings
uv build: PASS
repository-contract checks: 43 passed
```

These reported results are supporting evidence; this evaluation is based on independent inspection of the published candidate.

## Independent summary

The candidate implements the accepted architecture substantially correctly:

- only the three authorized files changed;
- the accepted read-only harness and its tests remain outside the candidate delta;
- the runner exposes `prepare`, `validate-answers`, and `seal`;
- Git blob identity is used rather than confusing blob IDs with SHA-256;
- evidence/output paths are fail-closed and no-overwrite;
- stdout and stderr are exclusive durable captures established before child creation;
- spawn failure is explicitly classified;
- a successful child is created at most once;
- raw capture bytes are hashed without reserialization;
- `B4PrepareResultV1(PREPARED)` precedes manifest and operator envelope;
- the canonical question contract contains Q1-Q10 with the accepted visible required dimensions;
- answer validation is structural and does not rewrite answer bytes;
- seal re-verifies the prepare-result digest and exact stdout/stderr capture digests;
- DB mutation produces terminal evidence with `INVALID_DB_MUTATION`;
- the runner contains no Relay product mutation imports and no semantic B4 scoring.

Two blocking implementation defects remain in the evidence-state semantics.

---

## F001 — Downstream validation states incorrectly record FAIL when the check was not performed

**Severity:** BLOCKING  
**Class:** evidence semantic integrity

The accepted implementation authority requires typed validation states:

```text
PASS
FAIL
NOT_PERFORMED
```

and explicitly states:

> Do not conflate “not checked” with “checked and failed.”

The candidate initializes all validation fields to `NOT_PERFORMED`, which is correct.

However, after attempting to decode harness stdout, it computes:

```python
query_only_ok = (
    isinstance(decoded, dict)
    and ...
)
schema_ok = (
    isinstance(decoded, dict)
    and ...
)

result["validation"]["query_only_valid"] = "PASS" if query_only_ok else "FAIL"
result["validation"]["relay_schema_version_valid"] = "PASS" if schema_ok else "FAIL"
```

When stdout is empty or invalid JSON, `decoded` is not a dictionary. Therefore neither `query_only` nor `schema_version` can actually be inspected.

The candidate nevertheless records both downstream validations as `FAIL`.

That makes the evidence claim that those checks were performed and failed, when in fact they were impossible to perform.

The current failure tests verify the high-level outcome (`INVALID_HARNESS_OUTPUT`) but do not verify the required tri-state semantics for that path.

### Required correction

Validation must be dependency-aware.

Minimum behavior:

```text
empty stdout:
  stdout_nonempty = FAIL
  stdout_json_valid = NOT_PERFORMED or FAIL only if parsing was intentionally attempted
  query_only_valid = NOT_PERFORMED
  relay_schema_version_valid = NOT_PERFORMED

non-empty invalid JSON:
  stdout_nonempty = PASS
  stdout_json_valid = FAIL
  query_only_valid = NOT_PERFORMED
  relay_schema_version_valid = NOT_PERFORMED

valid JSON without/with invalid query_only:
  stdout_json_valid = PASS
  query_only_valid = FAIL
  schema validation may be independently PASS/FAIL if the field is inspectable

valid JSON without/with invalid schema_version:
  stdout_json_valid = PASS
  relay_schema_version_valid = FAIL
```

The exact empty-stdout treatment for `stdout_json_valid` may be frozen consistently, but downstream field validations MUST remain `NOT_PERFORMED` when JSON structure is unavailable.

Add focused assertions for the complete validation map on empty-stdout and invalid-JSON paths.

---

## F002 — wait-failure path hashes captures without proving the child is terminal

**Severity:** BLOCKING  
**Class:** exact evidence custody

After successful process creation the candidate correctly sets:

```text
execution_started = true
harness_invocation_count = 1
```

It then executes:

```python
try:
    result["harness_exit_code"] = child.wait()
except OSError:
    wait_error = True

captures_durable = _close_capture_pair(stdout_handle, stderr_handle)
...
hash/read captures
...
if wait_error:
    return _fail_prepare(... "INVALID_HARNESS_EXIT", "wait", "HARNESS_WAIT_FAILED")
```

The problem is ordering.

If `child.wait()` raises `OSError`, the implementation has not established that the child process has terminated. The parent then closes and hashes the capture files and emits a durable prepare result as if those hashes represented terminal child output.

A still-running child may retain its inherited stdout/stderr file descriptors and write additional bytes after the parent hashes them. In that case the hashes recorded in `B4PrepareResultV1` would not describe the final capture files.

That violates the core Revision 2 evidence invariant: deterministic captured evidence must not become mutable after its terminal digest is recorded.

The current test suite does not force a wait failure and contains no kill/terminate/reap handling for this path.

### Required correction

The runner must not claim terminal capture digests until child termination is established.

A bounded acceptable design is:

1. if the initial `wait()` fails, enter a deterministic child-finalization path;
2. attempt to establish termination/reap state without spawning another child;
3. if necessary, terminate/kill the already-created child using a documented bounded sequence;
4. only after termination is established:
   - fsync/close captures;
   - hash exact bytes;
   - write terminal prepare failure evidence;
5. if termination cannot be established, classify as `INVALID_PREPARE_EVIDENCE` or another accepted fail-closed procedural state and do not represent the capture hashes as terminal evidence.

No second harness invocation is permitted.

Add a focused test that simulates a wait failure and proves capture hashing occurs only after the child is terminal/reaped, or proves a fail-closed evidence outcome that does not falsely claim terminal capture bytes.

---

## Question-contract review

The published `scripts/b4_question_contract_v1.json` correctly carries:

- `B4-R2-QSET-001`;
- Q1-Q10 in order;
- exact accepted question text;
- the accepted `required_dimensions[]`;
- structural response-schema fields only;
- no expected factual B4 answers.

No question-contract rework is indicated.

## Scope review

No scope violation was found.

The candidate changes only:

```text
scripts/b4_execution_runner.py
scripts/b4_question_contract_v1.json
tests/integration/test_b4_execution_runner.py
```

No product source, dependency, registry, governance-document, or accepted-harness change is present in the candidate.

## Accepted implementation aspects

The following do not require redesign:

```text
Git/checkout preflight
DB pre-hash and sidecar observation
output-path collision/no-overwrite checks
canonical question contract
exclusive stdout/stderr creation
spawn-failure state
exact-once child creation
PREPARED ordering before manifest/envelope
registry current-living-projection recording
B4AnswerSetV1 structural validation
single source inventory
seal-time capture/result verification
DB before/after terminal evidence
terminal digest emitted externally
```

## Required Rework 1 scope

Rework is bounded to the existing authorized files.

Required changes:

```text
F001:
Correct validation tri-state dependency semantics.
Add focused empty-output/invalid-JSON validation-state tests.

F002:
Make wait-failure handling establish child termination before terminal capture hashing,
or fail closed without claiming mutable hashes as terminal evidence.
Add focused wait-failure regression coverage.
```

Do not change:

- B4 question wording or dimensions;
- accepted read-only harness;
- product source;
- dependencies;
- implementation architecture;
- execution authority;
- B4 attempt 006;
- Slice 2.2.

The existing implementation authority is sufficient for this bounded corrective rework; no authority expansion is required.

## Independent disposition

```text
RLY-S110-DOGFOOD-B4-R2-IMPL-EVAL-001 — REWORK

Candidate:
1937309db82f1d1cc03a542c5fc074116c00d3fc

Scope:
PASS

Architecture:
PASS

Question contract:
PASS

Deterministic evidence protocol:
REWORK — F001 / F002

F001:
validation tri-state dependency semantics incorrect

F002:
wait-failure path does not prove child termination before capture hashing

Runner implementation:
NOT ACCEPTED

B4 attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```
