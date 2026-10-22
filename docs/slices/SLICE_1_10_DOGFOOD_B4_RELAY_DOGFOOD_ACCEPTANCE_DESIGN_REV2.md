# Slice 1.10 Dogfood B4 — Relay Dogfood Acceptance Design Revision 2

**Authority:** RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001  
**Status:** DESIGN CANDIDATE — NOT ACCEPTED; DOES NOT AUTHORIZE IMPLEMENTATION OR EXECUTION  
**Parent B4 design:** 9b274eda204dac30da51181f2c1de25cf7237010  
**Rework basis:** RLY-S110-DOGFOOD-B4-EXEC-EVAL-005 — FAIL — PROTOCOL/DESIGN AMBIGUITY ESTABLISHED  
**Starting branch parent:** 0d74d594486c7b5471feed4a15d5a1cad70840c9

## 1. Revision 2 decision

Revision 2 preserves the original B4 scientific objective: prove that a fresh operator can recover Relay's adopted and current project state from accepted durable/read-only surfaces without prior conversation reconstruction.

Revision 2 changes how that experiment is specified and executed, not the Relay project state being inspected.

Two defects are in scope:

1. operator/evaluator contract mismatch — visible questions Q6, Q8 and Q10 did not state all dimensions or scope later required by evaluation;
2. deterministic protocol delegated to prompt compliance — capture, hashing, sealing and binary execution obligations depended on a language model remembering procedural instructions.

Revision 2 resolves these by:

- freezing a visible question contract whose wording is one-to-one with evaluator boundaries;
- introducing a deterministic B4 execution/evidence runner above the accepted read-only harness;
- reducing the fresh operator's responsibility to semantic interpretation and structured answer production;
- keeping semantic evaluation and Human acceptance outside both operator and runner.

Revision 2 does not change project_board, slice_detail, lifecycle, Human-control, persistence, operational-DB, or accepted read-only harness semantics.

## 2. Architectural principle

Deterministic protocol and probabilistic reasoning MUST be separated.

```text
Deterministic B4 runner
  -> qualify checkout / DB / harness
  -> invoke harness exactly once
  -> durably capture and hash exact stdout
  -> generate exact operator input

Fresh operator
  -> inspect allowed durable state
  -> reason about Q1-Q10
  -> produce B4AnswerSetV1

Deterministic B4 runner
  -> validate structure/completeness
  -> prove DB before/after state
  -> construct and seal terminal evidence

Independent evaluator
  -> judge semantic correctness

Human Authority
  -> accept or reject result
```

Normative rule:

> If failure to perform an operation invalidates the evidence, and the operation can be performed deterministically, that operation MUST NOT depend on LLM prompt compliance.

The LLM owns meaning. The runner owns protocol correctness.

## 3. Scope

### 3.1 In scope

- exact revised B4 operator questions;
- deterministic question-set identity and digest;
- checkout, harness and DB preflight;
- exact-once harness execution through a runner;
- byte-preserving raw-output capture;
- no-overwrite evidence paths;
- JSON validation and hashing;
- deterministic operator-input envelope;
- B4AnswerSetV1;
- structural answer validation;
- canonical terminal evidence construction and sealing;
- DB before/after equality verification;
- sidecar observation semantics;
- failure-state evidence;
- focused implementation tests;
- attempt-006 entry criteria.

### 3.2 Out of scope

- changes to existing read-model semantics;
- changes to scripts/b4_readonly_harness.py unless implementation proves a blocker;
- changes to project_board or slice_detail;
- lifecycle, gate, Human-action, adoption, origin or persistence changes;
- automated semantic scoring by the runner;
- model-specific answer coaching;
- B4 attempt 006;
- Axis B replay;
- Slice 2.2 / Role Contracts;
- Phase 3;
- promotion.

## 4. Prior attempts as design evidence

| Attempt | Observation | Revision 2 response |
| --- | --- | --- |
| 001 | exact checkout not operationally established in operator venue | runner verifies exact HEAD and clean tree before DB access |
| 002 | Git blob IDs compared to file SHA-256 | runner performs Git-object verification itself |
| 003 | valid run; Q6/Q8 interpretation mismatch | visible contract review triggered |
| 004 | harness succeeded but raw stdout was not durably preserved | runner owns capture before child execution starts |
| 005 | deterministic capture worked; independent Q6/Q8 recurrence and Q10 omission | visible question contract revised; deterministic capture becomes code responsibility |

Repeated Q6/Q8 failures are not future answer hints. They are only evidence that the observable contract was misaligned.

## 5. Existing read-only harness remains a leaf component

The accepted harness retains one responsibility:

```text
pinned operational SQLite DB
  -> existing Relay read models
  -> project_board + slice_detail
  -> deterministic JSON stdout
```

The harness MUST NOT add B4 question interpretation, authority inference, answer generation, evaluator scoring, or evidence-envelope orchestration.

Revision 2 wraps the harness rather than expanding it.

## 6. New deterministic component: B4ExecutionRunner

### 6.1 Placement

Preferred implementation path: scripts/b4_execution_runner.py

Focused tests: tests/integration/test_b4_execution_runner.py

Rationale: B4 remains dogfood/evaluation tooling. Keep the initial fix under scripts rather than widening src/relay_engine into a generic framework. Generalization is a later design decision.

No production-source change is expected.

### 6.2 Runner modes

The runner exposes three CLI subcommands:

```text
prepare
validate-answers
seal
```

### 6.3 prepare

prepare deterministically:

1. verifies execution root;
2. verifies exact HEAD;
3. verifies clean worktree;
4. verifies accepted harness and harness-test Git blob IDs;
5. verifies DB path and exact pre-run SHA-256;
6. inventories WAL/SHM without mutation;
7. verifies all pinned output targets are absent;
8. opens the raw-output target using exclusive-create semantics;
9. invokes the accepted harness exactly once;
10. streams child stdout directly into that already-open raw-output file;
11. flushes/fsyncs/closes the raw capture;
12. records exit status and stderr evidence;
13. validates non-empty JSON;
14. requires query_only == 1;
15. requires Relay schema version 8;
16. computes SHA-256 over exact captured stdout bytes;
17. resolves and records registry/canonical artifact identities;
18. writes an immutable preparation manifest;
19. writes the deterministic operator-input envelope.

If steps 1-7 fail, the harness MUST NOT run.

Once raw capture is opened and the child execution begins, any later failure is terminal for that authority. There is no automatic retry.

### 6.4 validate-answers

validate-answers reads an unsealed B4AnswerSetV1 and performs structural validation only.

It MAY be invoked repeatedly before sealing.

It verifies:

- schema version;
- question-set ID and digest;
- exactly ten unique question IDs;
- exact Q1-Q10 membership;
- exact visible question text;
- required answer/source fields;
- boolean and enum validity;
- absence of evaluator result/score fields.

It MUST NOT judge semantics, compare against expected answers, reveal evaluator criteria, infer authority, or modify the answer file.

Structural or formatting errors may be corrected before seal while no evaluator feedback has been exposed.

### 6.5 seal

seal requires successful prepare state and structurally valid answers.

It deterministically:

1. hashes exact answer-set bytes;
2. records final inspected-source and prohibited-source declarations;
3. recomputes DB SHA-256;
4. inventories WAL/SHM after;
5. compares DB before/after;
6. constructs terminal evidence from runner facts plus the exact operator answer set;
7. writes terminal evidence using exclusive-create semantics;
8. fsyncs;
9. computes terminal-evidence SHA-256;
10. emits the terminal handoff.

If DB after differs, seal still writes terminal evidence with protocol status INVALID_DB_MUTATION. Evidence of invalidation must not disappear because a postcondition failed.

The runner never performs semantic B4 scoring.

## 7. Exact-once raw capture invariant

Hard invariant:

> There MUST be no successful harness execution path in which the harness stdout bytes are unavailable for validation and hashing.

Preferred mechanics:

```text
os.open(raw_path, O_WRONLY | O_CREAT | O_EXCL, 0o600)
  -> subprocess harness stdout is that file descriptor
  -> flush + fsync + close
  -> read exact bytes
  -> validate JSON
  -> SHA-256 exact bytes
```

Equivalent primitives are acceptable only if tests prove the invariant.

A child non-zero exit, partial JSON, invalid JSON or downstream processing failure does not permit rerun. Preserved bytes/error evidence remain part of the failed attempt.

## 8. No-overwrite evidence semantics

Every execution authority pins unique paths for:

- raw harness output;
- preparation manifest;
- operator-input envelope;
- answer set;
- terminal evidence.

Runner-created evidence uses exclusive-create semantics.

Existing target => fail closed before the relevant operation.

The runner MUST NOT truncate, replace, auto-number, rename around collisions, delete failed evidence, or normalize prior evidence.

A new attempt requires new Human authority and new paths.

## 9. Question contract Revision 2

### 9.1 Deterministic question-set identity

Question set ID: B4-R2-QSET-001

The runner-generated operator input contains:

- question-set ID;
- exact visible question text;
- exact response-field schema;
- allowed/prohibited source rules;
- question-contract SHA-256.

The evaluator records and checks the same identity/digest.

The runner MUST NOT contain expected factual answers.

### 9.2 Exact questions and answer dimensions

#### Q1

**What project is this?**

Visible required dimensions: Project identity and repository identity.

#### Q2

**What is the project objective?**

Visible required dimensions: represented Project objective and its record/time scope where material.

#### Q3

**What information is contextual or pre-T1 legacy rather than Relay lifecycle?**

Visible required dimensions: what pre-T1 existence is established, where Relay lifecycle/history begins, and no fabricated pre-T1 Relay lifecycle.

#### Q4

**What is the current governed work frontier?**

Visible required dimensions: exact current frontier Slice set, represented cardinality/completeness, and any relevant durable not-determinable state.

#### Q5

**What exact Slice is current?**

Visible required dimensions: Slice ID, title, definition revision, and parent/dependencies where material.

#### Q6 — REVISED

**What is the current Slice lifecycle state? State its phase, lifecycle revision, validity, blockage status, and any recorded blockage reasons.**

Those five dimensions are exactly what the evaluator may require.

Lifecycle state alone never establishes design or implementation authority.

#### Q7

**What is blocked?**

Visible required dimensions: explicit current blockers, with current Slice/project blockers distinguished from historical or separate blockers.

#### Q8 — REVISED

**According to Relay's durable project and governance state at this pinned checkout, what is the next governed project action or Human governance decision? Do not describe the next procedural step of this B4 operator run. If no exact next governed action or decision is established, say NOT DETERMINABLE FROM CURRENT DURABLE STATE.**

Visible required dimensions: operational next-work projection; applicable canonical governance action/decision; distinction between authorized action, needed Human authorization/decision, and merely planned work.

Execution-run instructions are explicitly outside the semantic answer scope.

#### Q9

**What Human decision, if any, is pending?**

Visible required dimensions: only explicit durable pending Human decisions; distinguish none recorded from not determinable; available controls are not pending decisions by themselves.

#### Q10 — REVISED

**What current or future work is only proposed/planned and therefore not authorized? For the current Slice, distinguish whether design/opening authority exists from whether implementation authority exists, then identify later roadmap work that remains not open/not authorized.**

Visible required dimensions: current Slice planned/lifecycle status; design/opening authority boundary; implementation authority boundary; later roadmap work.

### 9.3 Anti-coaching boundary

Question wording MAY name dimensions that are scored.

It MUST NOT reveal factual values expected for those dimensions.

Allowed example: State phase, revision, validity and blockage.

Prohibited example: The answer should be PROPOSED, revision 0, CURRENT and CLEAR.

The former defines the contract. The latter supplies the answer.

## 10. Evaluator contract Revision 2

The evaluator MUST score only dimensions visible in the operator contract. No hidden mandatory dimensions remain.

| Q | Primary source | PASS boundary |
| --- | --- | --- |
| Q1 | operational Project/adoption | correct Project + repository |
| Q2 | immutable adoption objective | faithful represented objective |
| Q3 | adoption/T1 + origin | correct context/lifecycle boundary |
| Q4 | board situation | exact frontier + represented completeness/not-determinable state |
| Q5 | Slice detail/card | exact Slice identity/revision |
| Q6 | slice_detail.lifecycle | every lifecycle dimension explicitly requested |
| Q7 | board blockers + lifecycle blockage + gate basis | correctly scoped explicit blockers |
| Q8 | board next-work + registry-resolved canonical governance | correct next governed action/decision or correct NOT_DETERMINABLE; no operator-procedure substitution |
| Q9 | HumanActionProjection + durable decisions | only explicit pending Human decision |
| Q10 | lifecycle + exact authority + canonical roadmap | correct design/opening vs implementation boundary plus later planned work |

Scoring remains:

```text
any mandatory FAIL -> overall FAIL
else any INDETERMINATE -> overall INDETERMINATE
all PASS + valid controls -> overall PASS
custody/control violation -> INDETERMINATE / INVALID RUN
```

No weighted score.

## 11. B4AnswerSetV1

The semantic operator produces one structured answer artifact.

Conceptual schema:

```text
B4AnswerSetV1
  schema_version: 1
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
    question_id: Q1..Q10
    question_text
    answer
    source_class[]
    source_locators[]
    relevant_fields_or_records[]
    not_determinable: bool
  completed_at
```

Rules:

- exactly Q1-Q10 once each;
- question text byte-matches generated contract;
- answer is nonblank;
- no semantic score/evaluator fields;
- no post-seal correction.

## 12. B4PrepareManifestV1

Runner-created immutable preparation evidence contains at minimum:

```text
authority/run/question-set identity
execution root
expected + observed HEAD
worktree cleanliness
expected + observed harness Git blob IDs
DB path
expected + observed DB SHA before
sidecars before
raw-output path
exclusive-create status
harness command
harness invocation count
harness exit code
stderr digest
raw-output SHA/size/JSON validity
query_only
Relay schema version
registry SHA
canonical artifact identities/digests
prepare status
prepared_at
```

prepare manifest is immutable after successful prepare.

## 13. B4TerminalEvidenceV2

The canonical evidence artifact is runner-generated, not manually assembled by the operator.

Conceptual fields:

```text
schema/authority/run/attempt identity
prepare manifest + SHA
raw harness path + SHA + size
question contract ID + SHA
answer-set path + SHA + exact structured answers
DB expected/before/after/unchanged
sidecars before/after
cold-start/operator/runtime/model custody
allowed/prohibited source inventories
protocol_result
sealed_at
```

Allowed protocol_result values:

```text
PREPARED
SEALED_READY_FOR_INDEPENDENT_EVALUATION
INVALID_PRECHECK
INVALID_HARNESS
INVALID_EVIDENCE
INVALID_DB_MUTATION
```

protocol_result is procedural only. It is not B4 semantic scoring.

## 14. Operator-input envelope

After successful prepare, the runner generates the material handed to the fresh operator.

It contains only:

- authority/run identity;
- cold-start declaration;
- allowed/prohibited source rules;
- source precedence;
- pinned checkout identity;
- raw read-model path and digest;
- registry/canonical references;
- exact B4-R2-QSET-001 contract;
- B4AnswerSetV1 schema and answer destination.

It MUST NOT contain expected factual answers, prior B4 answers/evaluations/outcomes, hidden evaluator scoring hints, or later repository state.

## 15. Source precedence

Revision 2 preserves:

1. pinned operational DB/read models for current runtime truth;
2. accepted immutable governance records for authority/history;
3. registry-resolved canonical projections for roadmap/governance context;
4. code/help for behavior and field meaning only;
5. conversation memory, assistant summaries and unsourced chronology prohibited.

Execution authority is protocol metadata. Unless a future question explicitly asks about the execution attempt, it MUST NOT be factual evidence for Q1-Q10.

## 16. Cold-start custody

The fresh operator must not receive:

- prior Relay conversation;
- prior B4 answers or evidence packets;
- prior B4 result evaluations;
- previous pass/fail question outcomes;
- evaluator factual answer key;
- private evaluator notes.

The runner cannot prove private memory. It records the declaration, generated-input digest, source inventories and timestamps. A known custody breach invalidates the run.

## 17. Failure semantics

### 17.1 Pre-harness failure

Wrong root/HEAD, dirty tree, wrong blobs, wrong DB digest, or pre-existing output target => INVALID_PRECHECK; harness invocation count stays 0; no automatic correction/retry.

### 17.2 Harness/capture failure

Child non-zero, empty output, invalid JSON, wrong query_only, wrong schema, or capture/fsync failure => INVALID_HARNESS or INVALID_EVIDENCE; invocation count 1; preserve available bytes/errors; no rerun.

### 17.3 Answer structural failure

Before seal, validate-answers may report structural defects and the operator may correct the unsealed answer file without evaluator feedback. This is not semantic scoring.

After successful seal, answers are immutable.

### 17.4 Post-run DB mutation

If DB after differs, runner still seals terminal evidence with INVALID_DB_MUTATION. No repair/checkpoint.

### 17.5 Sidecars

WAL/SHM are observational. Zero-byte WAL is acceptable. SHM presence is acceptable. mtime-only change does not invalidate. Never checkpoint/delete/normalize.

## 18. Runner is not an authority engine

The runner MUST NOT:

- decide whether Slice 2.2 is authorized;
- determine CURRENT/NEXT/LATER/BLOCKED semantics;
- synthesize Q answers;
- mark semantic answers correct;
- infer Human intent;
- mutate lifecycle/Slices/governance DB records;
- create successor work;
- promote code.

It validates procedure and structure only.

## 19. Canonical serialization

Runner-generated JSON uses one repository-owned deterministic serializer:

```text
UTF-8
sorted keys
compact separators
newline terminated
UTC RFC3339 timestamps
SHA-256 over exact bytes
```

Raw harness stdout is hashed before any reserialization.

RFC 8785/JCS is not required unless implementation review demonstrates a concrete need.

## 20. Implementation acceptance criteria

AC01 — wrong HEAD/dirty tree/wrong blob/wrong DB hash/pre-existing evidence prevents harness invocation.

AC02 — successful prepare invokes accepted harness exactly once; no failure path invokes it twice.

AC03 — stdout is directed to exclusively created durable capture as part of invocation.

AC04 — raw-output size and SHA-256 cover exact captured bytes.

AC05 — runner requires query_only == 1 and schema version 8.

AC06 — operator input contains exact B4-R2-QSET-001 text and digest.

AC07 — evaluator has no hidden mandatory answer dimensions.

AC08 — exactly Q1-Q10 once each are required before seal.

AC09 — runner contains no expected factual answer or semantic PASS/FAIL logic.

AC10 — existing evidence target always fails closed; no overwrite.

AC11 — before/after DB hashes are recorded and mismatch detected.

AC12 — post-invocation failure preserves deterministic failure evidence.

AC13 — runner never checkpoints/deletes/normalizes sidecars.

AC14 — successful seal writes terminal evidence once and hashes it.

AC15 — existing Relay read-model semantics remain unchanged.

## 21. Required focused tests

Implementation MUST cover at least:

```text
wrong HEAD
dirty worktree
wrong harness script blob
wrong harness-test blob
wrong DB SHA
pre-existing raw path
pre-existing manifest path
pre-existing terminal evidence path
harness non-zero
empty harness stdout
invalid harness JSON
query_only != 1
schema version != 8
successful prepare invokes harness exactly once
successful prepare preserves exact stdout bytes
successful prepare hashes exact stdout bytes
operator input carries exact question contract
answer set missing Q
answer set duplicate Q
answer set mismatched question text
answer set contains forbidden score field
valid answer-set structure
seal detects DB hash change
mtime-only sidecar change is observational
seal is immutable/no-overwrite
runner contains no expected factual answer strings
runner never calls writable open_database
runner does not modify operational DB
```

Normal full pytest, Ruff, Pyright, build and repository-contract validation also remain required under later implementation authority.

## 22. Attempt 006 entry criteria

Attempt 006 MUST NOT be authorized until:

1. Revision 2 design receives independent ACCEPT;
2. Human accepts Revision 2 design;
3. runner implementation receives separate authority;
4. implementation receives independent ACCEPT;
5. Human accepts implementation;
6. exact runner/harness/question-set identities are pinned;
7. clean execution checkout is qualified;
8. unique evidence paths are pinned;
9. live DB digest is pinned;
10. fresh-operator custody plan is frozen.

Attempt 006 must run all ten Revision 2 questions. It is not a targeted Q6/Q8/Q10 retest.

## 23. B4 success and Slice 2.2 boundary

B4 passes only after a valid run has all ten questions independently PASS, followed by explicit Human result acceptance.

Only then does Slice 2.2 design become eligible to open.

B4 success never directly authorizes Slice 2.2 design or implementation.

## 24. Future generalization

The runner is intentionally B4-specific.

If proven useful, a later design may extract a generic GovernedCommandRunner or EvidenceRun primitive for preconditions, exact command execution, capture, provenance, hashing, before/after proof and sealing.

That generalization is outside Revision 2. Do not turn this bounded B4 fix into a framework project.

## 25. Risks and mitigations

R1 — overfitting questions. Mitigation: expose dimensions, never factual values.

R2 — runner becomes a second control plane. Mitigation: procedure only; no authority/semantic decisions.

R3 — duplicate harness semantics. Mitigation: existing harness remains sole read-model producer.

R4 — evidence machinery expands scope. Mitigation: one B4-specific script and focused tests.

R5 — structural validation becomes coaching. Mitigation: schema/completeness only, no answer values.

R6 — later governance differs from pinned checkout. Mitigation: answers are scoped to exact pinned checkout; execution authority is protocol metadata, not answer evidence.

## 26. Independent design-review checklist

Independent review must answer YES to all:

- original B4 scientific objective preserved;
- visible questions align one-to-one with evaluator mandatory dimensions;
- factual expected answers remain hidden;
- deterministic evidence custody removed from LLM memory/compliance;
- successful harness execution implies preserved raw bytes or deterministic failure evidence;
- accepted harness semantics remain unchanged;
- live DB remains read-only;
- semantic scoring excluded from runner;
- failed attempts preserved rather than repaired/retried;
- implementation scope remains minimal/testable;
- attempt 006 remains separately governed;
- Slice 2.2 remains closed.

## 27. Design disposition

```text
RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001 — AUTHORIZED

B4 Revision 2 design:
CANDIDATE READY FOR INDEPENDENT REVIEW

B4 read-only harness:
SEMANTICS UNCHANGED

B4 deterministic execution/evidence runner:
DESIGNED / NOT IMPLEMENTED / NOT AUTHORIZED

B4 Revision 2 question contract:
DESIGNED / NOT ACCEPTED

B4 attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```