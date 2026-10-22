# Slice 1.10 Dogfood B4 Revision 2 — Deterministic Runner Implementation Authorization

**Document class:** Immutable Human implementation authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-S110-DOGFOOD-B4-R2-IMPL-AUTH-001`  
**Decision:** `AUTHORIZED`

## 1. Human decision

The Human authorizes bounded implementation of the Human-accepted B4 Revision 2 deterministic execution/evidence runner and canonical question contract.

This authority implements only the accepted B4 Revision 2 composite.

## 2. Exact accepted design basis

```text
Revision 2 base:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da

Revision 2 Rework 1:
cfba7884c3fe927c31195ae0c1a10c9666c3bc9f

Revision 2 Rework 2:
0bb228c13d5f3ee4dce4167705cc0f444ece350a

Independent design evaluation:
RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-003 — ACCEPT
commit f82c8c8f4030e4abeab8b3910388aeb34f513261

Human design acceptance:
RLY-S110-DOGFOOD-B4-R2-DESIGN-ACCEPT-001 — ACCEPTED
commit 529c9a642d6ed6e6c6cd6caa487676d045c062b7
```

Implementation branch:

`implementation/1.10-dogfood-b4-rev2-runner`

Authorized implementation parent:

`529c9a642d6ed6e6c6cd6caa487676d045c062b7`

## 3. Authorized implementation files

Codex may create/modify only:

```text
scripts/b4_execution_runner.py
scripts/b4_question_contract_v1.json
tests/integration/test_b4_execution_runner.py
```

No other implementation file is authorized.

The governance authority record itself is not an implementation file and must not be edited by Codex.

If implementation proves that another production/test/config file is strictly required, STOP and report the blocker. Do not widen scope autonomously.

## 4. Explicitly frozen / out of scope

Do not modify:

```text
scripts/b4_readonly_harness.py
tests/integration/test_b4_readonly_harness.py
src/relay_engine/**
pyproject.toml
uv.lock
.relay/registry.json
docs/**
.github/**
```

except that this already-created immutable implementation-authority document exists on the branch.

Also prohibited:

- operational DB mutation;
- new schema/migration;
- product board/lifecycle/persistence changes;
- semantic B4 answer generation;
- semantic B4 scoring;
- expected factual answer keys;
- B4 attempt 006;
- Slice 2.2 / Role Contracts;
- generic GovernedCommandRunner/EvidenceRun extraction;
- promotion;
- dependency additions.

## 5. Implementation principle

The code boundary is:

```text
runner = deterministic protocol
operator = semantic reasoning
evaluator = semantic correctness
Human = acceptance / authority
```

If an operation is deterministic and its omission would invalidate B4 evidence, the runner owns it.

The runner MUST NOT infer Relay governance meaning.

## 6. Runtime/dependency constraint

Use Python 3.14 and existing dependencies only.

Prefer Python standard library for the new runner.

No new package dependency and no project configuration change is authorized.

The runner MUST invoke the accepted harness using the current interpreter, conceptually:

```text
sys.executable scripts/b4_readonly_harness.py ...
```

Do not invoke a different semantic read path and do not duplicate `project_board` / `slice_detail` logic.

Do not use `shell=True`.

## 7. Canonical question contract artifact

Create:

`scripts/b4_question_contract_v1.json`

It is the single normative source for `B4QuestionContractV1`.

The file MUST itself be canonical JSON:

- UTF-8;
- sorted object keys;
- compact separators;
- one trailing newline;
- no comments;
- no duplicate JSON keys.

Top-level shape:

```text
{
  "schema_version": 1,
  "question_set_id": "B4-R2-QSET-001",
  "questions": [Q1..Q10]
}
```

Each question entry MUST contain exactly:

```text
question_id
question_text
required_dimensions
response_schema
```

The exact question text and required dimensions MUST match the Human-accepted Revision 2 + Rework 1 contract. Do not paraphrase them.

`response_schema` MUST expose the operator answer fields required by `B4AnswerSetV1`:

```text
answer
source_class
source_locators
relevant_fields_or_records
not_determinable
```

It may express these as deterministic field/type/required metadata; it MUST NOT contain factual expected answers.

The runner computes SHA-256 over the exact contract-file bytes and requires its caller-supplied expected digest to match.

The runner MUST also parse and reserialize the contract with its canonical serializer and require byte identity with the on-disk file.

## 8. CLI contract

Create:

`scripts/b4_execution_runner.py`

It MUST expose exactly these top-level subcommands:

```text
prepare
validate-answers
seal
```

Argument spelling may follow normal argparse conventions, but the functionality below is mandatory.

### 8.1 prepare required inputs

`prepare` must receive:

```text
authority_id
run_id
attempt_number

execution_root
expected_head

harness_path
expected_harness_blob
harness_test_path
expected_harness_test_blob

database_path
expected_db_sha256
project_id
slice_id

question_contract_path
expected_question_contract_sha256

stdout_path
stderr_path
prepare_result_path
prepare_manifest_path
operator_input_path
answer_set_path
terminal_evidence_path
```

All run-specific values come from a later execution authority. Do not hardcode B4 attempt-006 values into the implementation.

### 8.2 validate-answers required inputs

`validate-answers` must receive at minimum:

```text
prepare_manifest_path
answer_set_path
```

It must require that the answer-set path matches the path pinned by the successful prepare manifest.

### 8.3 seal required inputs

`seal` must receive at minimum:

```text
prepare_manifest_path
answer_set_path
```

The terminal-evidence target and DB identity are taken from the successful pinned prepare manifest; do not permit seal-time substitution with different paths.

## 9. Deterministic JSON serializer

Implement one runner-owned serializer for runner-generated JSON artifacts.

Required bytes:

```text
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
+ "\n"
```

encoded UTF-8.

Use this for:

- question-contract canonicality validation;
- `B4PrepareResultV1`;
- `B4PrepareManifestV1`;
- operator-input envelope;
- `B4TerminalEvidenceV2`;
- CLI machine-readable success/failure summaries where JSON is emitted.

Hashes are SHA-256 of exact bytes.

The operator-authored answer set is hashed over its exact supplied bytes; it need not be rewritten into canonical form.

## 10. Path and no-overwrite rules

Before harness spawn, `prepare` MUST validate:

- execution root resolves to the exact Git top-level;
- all runner output paths are absolute or deterministically resolved;
- stdout, stderr, prepare-result, prepare-manifest, operator-input, answer-set and terminal-evidence paths are pairwise distinct;
- evidence/output paths are outside the execution repository;
- evidence/output paths do not equal the DB or DB sidecar paths;
- every required parent directory already exists;
- runner does not auto-create missing evidence directories;
- every pinned output path is absent.

Runner-created files use exclusive-create semantics.

Never:

- truncate;
- overwrite;
- auto-number;
- choose alternate filenames;
- delete failed evidence to retry;
- retry under the same authority.

## 11. Git preflight

`prepare` MUST deterministically verify:

1. `git rev-parse --show-toplevel` resolves to `execution_root`;
2. `git rev-parse HEAD == expected_head`;
3. `git status --porcelain` is empty;
4. `git rev-parse HEAD:<harness_path> == expected_harness_blob`;
5. `git rev-parse HEAD:<harness_test_path> == expected_harness_test_blob`.

Harness/test paths must resolve inside the execution root and be representable as repository-relative Git paths.

Do not compare Git blob IDs to ordinary SHA-256 file digests.

Any mismatch is `INVALID_PRECHECK`; no harness child may start.

## 12. DB and sidecar preflight

Before harness spawn:

- database must already exist as a file;
- compute SHA-256 and require exact equality with `expected_db_sha256`;
- inventory `<database>-wal` and `<database>-shm` without mutation.

For each sidecar record where present:

```text
path
exists
size
mtime_ns
sha256
```

If absent, record absence explicitly.

Never checkpoint, remove, truncate, normalize, chmod, or otherwise mutate the DB or sidecars.

## 13. Registry/canonical-source recording

For successful preparation, compute SHA-256 of:

`.relay/registry.json`

Parse it as JSON.

Record all entries where:

```text
artifact_class == "LIVING_PROJECTION"
artifact_state == "CURRENT"
```

At minimum retain for each:

```text
artifact_id
path
revision
content_digest
title
```

This is identity/provenance recording only.

Do not infer which canonical artifact answers any B4 question and do not infer authority from these records.

## 14. Question-contract preflight

Before harness spawn:

- question-contract file must exist under the execution root;
- exact file SHA-256 must match `expected_question_contract_sha256`;
- parse JSON rejecting duplicate keys;
- require schema version 1;
- require question-set ID `B4-R2-QSET-001`;
- require exactly ordered Q1..Q10;
- require exact accepted question text;
- require non-empty `required_dimensions[]`;
- require valid `response_schema`;
- require canonical reserialization byte-equal to the source bytes.

Mismatch => `INVALID_PRECHECK`; no harness child starts.

The runner contains no separate duplicate list of factual expected answers.

It MAY contain structural constants needed to validate the accepted contract shape, but the JSON artifact remains the normative question content.

## 15. Prepare state machine

The implemented prepare state machine MUST be total.

### 15.1 INVALID_PRECHECK

Any deterministic preflight failure before capture setup:

```text
execution_started = false
harness_invocation_count = 0
harness_exit_code = null
prepare_outcome = INVALID_PRECHECK
```

Write `B4PrepareResultV1` when its own target is available and safe to create.

If the prepare-result target itself cannot be created, emit fail-closed stderr/exit status and do not create alternate evidence.

### 15.2 INVALID_CAPTURE_SETUP

Open stdout first and stderr second using exclusive creation.

If capture setup fails:

- no harness child starts;
- `execution_started=false`;
- invocation count 0;
- preserve any capture file already created;
- flush/fsync/close what was created where applicable;
- do not delete/truncate the partial evidence;
- write `B4PrepareResultV1` when possible;
- no retry.

### 15.3 INVALID_HARNESS_SPAWN

After both captures are open, attempt one child creation.

If process creation fails before a child exists:

```text
execution_started = false
harness_invocation_count = 0
harness_exit_code = null
failure_stage = "spawn"
prepare_outcome = INVALID_HARNESS_SPAWN
```

Then:

- flush/fsync/close both capture files;
- hash both exact byte streams;
- preserve both files;
- write/fsync/hash `B4PrepareResultV1`;
- no success manifest;
- no operator envelope;
- no retry.

Use a stable runner-owned failure code such as `HARNESS_PROCESS_CREATION_FAILED`; raw exception text is diagnostic only.

### 15.4 Child started

Once child creation succeeds:

```text
execution_started = true
harness_invocation_count = 1
```

There is no code path to spawn a second harness child.

Invoke the existing harness with exactly the pinned:

```text
--database
--project-id
--slice-id
```

arguments.

Child stdout/stderr are the already-open durable capture files.

### 15.5 After child termination

Always:

- flush/fsync/close stdout;
- flush/fsync/close stderr;
- hash exact stdout bytes;
- hash exact stderr bytes.

Then classify:

- non-zero child => `INVALID_HARNESS_EXIT`;
- zero child + empty stdout => `INVALID_HARNESS_OUTPUT`;
- zero child + invalid JSON => `INVALID_HARNESS_OUTPUT`;
- valid JSON but `query_only != 1` => `INVALID_HARNESS_PROTOCOL`;
- valid JSON but `schema_version != 8` => `INVALID_HARNESS_PROTOCOL`;
- otherwise continue toward `PREPARED`.

Any failure writes durable `B4PrepareResultV1`, then STOP.

No success manifest/operator input may be generated.

## 16. B4PrepareResultV1

The prepare result is the procedural terminal record of prepare when it can be persisted.

Required conceptual fields:

```text
schema_version = 1
authority_id
run_id
attempt_number

execution_root
expected_head
observed_head
worktree_clean

harness_path
expected_harness_blob
observed_harness_blob
harness_test_path
expected_harness_test_blob
observed_harness_test_blob

database_path
expected_db_sha256
db_sha256_before
sidecars_before

question_contract_path
question_set_id
expected_question_contract_sha256
question_contract_sha256

execution_started
harness_invocation_count
harness_exit_code

stdout: {path, exists, size, sha256}
stderr: {path, exists, size, sha256}

validation:
  stdout_nonempty
  stdout_json_valid
  query_only_valid
  relay_schema_version_valid

failure_stage
failure_code
prepare_outcome
recorded_at
```

Validation values MUST use a typed tri-state representation:

```text
PASS
FAIL
NOT_PERFORMED
```

Do not conflate “not checked” with “checked and failed.”

Allowed `prepare_outcome` values exactly:

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

No semantic B4 PASS/FAIL fields.

## 17. Successful prepare ordering

Only after the child/protocol checks succeed:

1. create/fsync `B4PrepareResultV1` with `PREPARED`;
2. hash exact prepare-result bytes;
3. only then create `B4PrepareManifestV1`;
4. only then create operator-input envelope.

If prepare-result persistence fails, report `INVALID_PREPARE_EVIDENCE`; do not create success artifacts.

If manifest or operator-input creation fails after PREPARED:

- preserve prepare result and captures;
- fail closed;
- do not rerun harness;
- do not overwrite/reconstruct prior artifacts.

## 18. B4PrepareManifestV1

Success-only manifest.

Must include/reference at least:

```text
schema_version = 1
authority_id
run_id
attempt_number

prepare_result_path
prepare_result_sha256

stdout_path
stdout_sha256
stderr_path
stderr_sha256

database_path
expected_db_sha256
db_sha256_before
sidecars_before

project_id
slice_id

question_contract_path
question_set_id
question_contract_sha256

registry_path
registry_sha256
current_living_projections[]

operator_input_path
answer_set_path
terminal_evidence_path

prepared_at
```

It is immutable/no-overwrite.

## 19. Operator-input envelope

Runner-generated and canonical JSON.

Must include:

- authority/run/attempt identity;
- exact cold-start declaration text;
- source precedence;
- allowed source classes;
- prohibited source classes;
- execution checkout identity;
- raw harness capture path + SHA-256;
- registry path + SHA-256;
- current living-projection identities;
- full `B4QuestionContractV1` including `required_dimensions[]`;
- `question_contract_sha256`;
- `B4AnswerSetV1` structural schema/instructions;
- exact answer-set destination path.

Allowed-source rules must preserve the accepted B4 design:

1. registry;
2. registry-resolved canonical documents;
3. accepted immutable governance records discoverable from allowed canonical records;
4. repository code/help only for behavior/field meaning;
5. captured harness JSON;
6. explicitly pinned external evidence only where a permitted record names path+digest.

Prohibited before answer seal:

- prior Relay/ChatGPT conversation;
- prior B4 answer/evidence packets;
- prior B4 execution evaluations/outcomes;
- reconstructed project summaries;
- evaluator answer keys/expected factual answers/private notes;
- later repository state beyond the pinned checkout.

The execution authority is protocol/pin metadata, not factual Q1-Q10 answer evidence.

Do not include prior question pass/fail outcomes.

## 20. B4AnswerSetV1 structural validation

The operator-authored answer file uses:

```text
schema_version = 1
authority_id
run_id
question_set_id
question_contract_sha256
cold_start_declaration
operator_identity
runtime_identity
model_identity | null
inspected_sources[]
prohibited_sources_accessed[]
answers[10]
completed_at
```

Each answer contains exactly:

```text
question_id
question_text
answer
source_class[]
source_locators[]
relevant_fields_or_records[]
not_determinable
```

`validate-answers` MUST:

- parse JSON and reject duplicate keys;
- require exact allowed top-level keys;
- require exact allowed answer keys;
- bind authority/run/question-set/digest to the successful manifest;
- require exact Q1..Q10 once each;
- require exact canonical question text;
- require nonblank answer text;
- require `not_determinable` boolean;
- require list/string types;
- require `inspected_sources[]` non-empty;
- require `prohibited_sources_accessed[]` be a list;
- when `not_determinable=false`, require non-empty source class + locator evidence;
- reject semantic/evaluator score fields by exact-schema enforcement;
- make no semantic correctness judgment;
- never modify the answer file.

It may be called repeatedly before seal.

## 21. Single source inventory

The only operator-owned declarations are in `B4AnswerSetV1`:

```text
inspected_sources[]
prohibited_sources_accessed[]
```

`seal` must not recollect a second operator inventory.

Terminal evidence copies these fields from the exact hashed answer set.

If runner-observed access is ever included, call it something distinct such as `runner_observed_accesses`; it must not masquerade as the operator declaration.

## 22. Seal behavior

`seal` requires:

- successful immutable prepare manifest;
- prepare result outcome PREPARED;
- structurally valid answer set;
- answer-set path equal to the manifest-pinned path;
- terminal-evidence target absent.

Then:

1. hash exact answer-set bytes;
2. inventory DB sidecars after;
3. recompute DB SHA-256;
4. compare before/after;
5. construct canonical `B4TerminalEvidenceV2`;
6. exclusive-create/fsync terminal evidence;
7. compute SHA-256 over exact terminal-evidence bytes;
8. emit terminal digest/summary.

Do not embed the terminal file's own SHA-256 inside itself. Report that digest externally after write.

If DB SHA differs:

- still create terminal evidence;
- `protocol_result = INVALID_DB_MUTATION`;
- return controlled non-zero status;
- do not repair/checkpoint DB;
- semantic B4 evaluation is not eligible.

If unchanged:

`protocol_result = SEALED_READY_FOR_INDEPENDENT_EVALUATION`

The runner never assigns Q-level or overall B4 semantic scores.

## 23. B4TerminalEvidenceV2 minimum contents

```text
schema_version
authority_id
run_id
attempt_number

prepare_result_path
prepare_result_sha256
prepare_manifest_path
prepare_manifest_sha256

raw_harness:
  stdout path/sha256/size
  stderr path/sha256/size

question_contract:
  question_set_id
  path
  sha256

operator_answer_set:
  path
  sha256
  parsed exact structured data

database:
  path
  expected_sha256
  before_sha256
  after_sha256
  unchanged

sidecars:
  before
  after

custody:
  cold_start_declaration
  operator_identity
  runtime_identity
  model_identity
  inspected_sources
  prohibited_sources_accessed

protocol_result
sealed_at
```

## 24. CLI output and exit behavior

Normal successful subcommands return exit code 0.

Controlled fail-closed protocol/validation outcomes return a stable non-zero code (2 is recommended).

Output should be concise and machine-readable where practical.

Never print semantic expected answers.

Unhandled programming errors must not be converted into a false successful protocol result.

## 25. Required focused tests

At minimum implement deterministic tests for:

### Preflight

- wrong HEAD => no child;
- dirty worktree => no child;
- wrong harness blob => no child;
- wrong harness-test blob => no child;
- wrong DB SHA => no child;
- wrong question-contract SHA => no child;
- non-canonical/invalid question contract => no child;
- output path inside repo => no child;
- duplicate output paths => no child;
- pre-existing stdout target => no child;
- pre-existing stderr target => no child;
- pre-existing prepare-result target => no overwrite/no child;
- pre-existing manifest/operator-input/answer/terminal target => no child.

### Capture/spawn

- stdout capture setup failure => no child;
- stderr capture setup failure after stdout exists => preserve stdout/no child;
- forced process-spawn failure after both captures =>:
  - execution_started false;
  - invocation count 0;
  - exit code null;
  - both captures preserved/hashed;
  - `INVALID_HARNESS_SPAWN`;
  - no manifest/envelope;
  - no retry.

### Child/harness protocol

- non-zero harness => stdout/stderr preserved + `INVALID_HARNESS_EXIT`;
- empty stdout => `INVALID_HARNESS_OUTPUT`;
- invalid JSON => `INVALID_HARNESS_OUTPUT`;
- `query_only != 1` => `INVALID_HARNESS_PROTOCOL`;
- schema != 8 => `INVALID_HARNESS_PROTOCOL`;
- each failure invokes harness at most once;
- success invokes harness exactly once.

### Success evidence

- exact stdout bytes preserved and hash matches;
- exact stderr bytes preserved and hash matches;
- PREPARED result exists before success manifest/envelope;
- manifest binds prepare-result digest;
- operator envelope contains exact complete question contract/digest;
- registry current-living-projection identities recorded;
- no expected factual answer key emitted.

### Answer validation

- missing Q rejected;
- duplicate Q rejected;
- wrong Q order/identity rejected as required by schema;
- mismatched question text rejected;
- wrong question-set ID rejected;
- wrong contract digest rejected;
- wrong authority/run rejected;
- extra semantic score field rejected;
- missing required field rejected;
- structurally valid answer set accepted;
- validator does not rewrite answer bytes.

### Seal

- seal refuses non-PREPARED manifest/result;
- seal refuses invalid answer structure;
- terminal path collision refuses overwrite;
- DB unchanged => `SEALED_READY_FOR_INDEPENDENT_EVALUATION`;
- DB changed => terminal evidence still written with `INVALID_DB_MUTATION`;
- sidecar mtime-only change recorded but does not by itself invalidate;
- terminal evidence copies source inventory from answer set;
- terminal SHA reported externally;
- no DB checkpoint/delete/normalization.

### Static/invariant checks

- existing B4 harness bytes unchanged;
- existing harness test bytes unchanged;
- runner does not call Relay writable `open_database`;
- runner does not import board/lifecycle mutation services;
- no product source changes;
- no second harness spawn path.

Tests MUST use disposable DBs/worktrees/evidence paths. Never point tests at the real operational DB.

## 26. Validation commands

Before handoff Codex must run and report:

```bash
uv run pytest tests/integration/test_b4_execution_runner.py -q
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv build
```

Also run repository-contract checks if they are a distinct repository command in this checkout; discover and report the exact command rather than inventing one.

The worktree must be clean after the candidate commit.

## 27. Candidate construction rules

Codex may iterate locally and fix failures within the authorized files.

It may create one final implementation candidate commit or a small ancestry-preserving implementation series.

Do not:

- merge;
- rebase onto unrelated later state;
- promote;
- update main;
- modify governance records;
- open B4 attempt 006;
- execute against the real operational DB.

## 28. Required implementation handoff

Return exactly enough evidence for independent review:

```text
Authority:
RLY-S110-DOGFOOD-B4-R2-IMPL-AUTH-001

Implementation branch:
Implementation parent:
Candidate SHA:
Candidate ancestry from parent:
Worktree clean:

Changed files:
- ...

Question-contract Git blob:
Question-contract SHA-256:
Runner Git blob:
Runner test Git blob:

Existing accepted harness blob before/after:
Existing accepted harness-test blob before/after:

Focused tests:
Full pytest:
Ruff format:
Ruff lint:
Pyright:
Build:
Repository-contract checks:

Implementation notes:
- prepare state machine
- exact-once child boundary
- capture/sealing behavior
- answer validation behavior

Product source changes:
NO

Existing harness semantic changes:
NO

Real operational DB accessed:
NO

B4 semantic scoring performed:
NO

B4 attempt 006 performed:
NO

Slice 2.2 work performed:
NO

Status:
STOP FOR INDEPENDENT IMPLEMENTATION REVIEW
```

Do not self-accept the implementation.

## 29. Governance status

```text
RLY-S110-DOGFOOD-B4-R2-IMPL-AUTH-001 — AUTHORIZED

B4 Revision 2 design:
COMPLETE / HUMAN ACCEPTED

Deterministic runner implementation:
AUTHORIZED / OPEN

B4 attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```
