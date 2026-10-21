# Slice 1.10 Dogfood B4 — Relay Dogfood Acceptance Design Revision 2 Rework 1

**Authority:** `RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001`  
**Rework basis:** `RLY-S110-DOGFOOD-B4-R2-DESIGN-EVAL-001 — REWORK`  
**Amends:** `SLICE_1_10_DOGFOOD_B4_RELAY_DOGFOOD_ACCEPTANCE_DESIGN_REV2.md` at `ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da`  
**Status:** REWORK CANDIDATE — NOT ACCEPTED; DOES NOT AUTHORIZE IMPLEMENTATION OR EXECUTION

## 1. Rework decision

This amendment closes only the two blocking findings and one non-blocking observation from the first independent Revision 2 design review:

- `F001` — operator-visible mandatory dimensions were not normatively part of the generated question contract;
- `F002` — stderr and post-launch terminal prepare disposition were not guaranteed durable independently of success-path manifest creation;
- `O001` — operator source inventory needed one canonical source of truth.

All Revision 2 provisions remain normative except where explicitly amended here.

No product read-model, lifecycle, persistence, operational-DB, or accepted read-only harness semantic change is introduced.

## 2. F001 closure — canonical operator-visible question contract

### 2.1 New normative artifact: B4QuestionContractV1

`B4-R2-QSET-001` is no longer defined only by prose/question text. It is a canonical structured artifact.

Conceptual schema:

```text
B4QuestionContractV1
  schema_version: 1
  question_set_id: B4-R2-QSET-001
  questions[10]
    question_id: Q1..Q10
    question_text
    required_dimensions[]
    response_schema
```

Normative requirements:

- exactly ten entries, Q1 through Q10, once each;
- question order is Q1..Q10;
- every `required_dimensions[]` entry is operator-visible;
- every evaluator-mandatory semantic dimension MUST appear in the corresponding `required_dimensions[]`;
- evaluator review MUST NOT fail an answer for a mandatory semantic dimension absent from the exact accepted question contract;
- no expected factual value may appear in `question_text`, `required_dimensions[]`, or `response_schema`;
- the contract is canonical JSON using the Revision 2 serialization rules;
- `question_contract_sha256` is SHA-256 over the exact canonical contract bytes.

### 2.2 Preferred repository representation

Preferred implementation adds one data artifact:

`scripts/b4_question_contract_v1.json`

The runner MUST read this artifact rather than maintain an independent handwritten duplicate of Q1-Q10.

The later implementation authority/review MUST pin both:

- runner Git blob identity;
- question-contract Git blob identity and SHA-256 of its canonical bytes.

Equivalent generated-in-code representation is acceptable only if there is still exactly one normative question source and tests prove byte identity between what the operator receives and what the evaluator binds to. A separate JSON artifact is preferred for legibility and diffability.

### 2.3 Exact canonical entries

The accepted Revision 2 question text and required dimensions become:

#### Q1

`question_text`: **What project is this?**

`required_dimensions[]`:

- Project identity;
- repository identity.

#### Q2

`question_text`: **What is the project objective?**

`required_dimensions[]`:

- represented Project objective;
- source/record time scope where material.

#### Q3

`question_text`: **What information is contextual or pre-T1 legacy rather than Relay lifecycle?**

`required_dimensions[]`:

- what the adoption record establishes about pre-T1 software-project existence;
- where Relay-governed lifecycle/history begins;
- explicit avoidance of fabricated pre-T1 Relay lifecycle/history.

#### Q4

`question_text`: **What is the current governed work frontier?**

`required_dimensions[]`:

- exact current frontier Slice set;
- represented frontier cardinality/completeness;
- relevant durable incomplete/not-determinable state.

#### Q5

`question_text`: **What exact Slice is current?**

`required_dimensions[]`:

- Slice ID;
- title;
- definition revision;
- parent/dependencies where material.

#### Q6

`question_text`: **What is the current Slice lifecycle state? State its phase, lifecycle revision, validity, blockage status, and any recorded blockage reasons.**

`required_dimensions[]`:

- lifecycle phase;
- lifecycle revision;
- lifecycle validity;
- blockage status;
- recorded blockage reasons.

#### Q7

`question_text`: **What is blocked?**

`required_dimensions[]`:

- explicit current blockers;
- distinction between current Slice/project blockers and historical/separate blockers;
- qualification that absence of projected blockers does not prove absence of undocumented external impediments.

#### Q8

`question_text`: **According to Relay's durable project and governance state at this pinned checkout, what is the next governed project action or Human governance decision? Do not describe the next procedural step of this B4 operator run. If no exact next governed action or decision is established, say NOT DETERMINABLE FROM CURRENT DURABLE STATE.**

`required_dimensions[]`:

- operational next-work projection;
- applicable registry-resolved canonical governance action/decision;
- distinction among currently authorized action, needed Human authorization/decision, and merely planned work;
- exclusion of B4 operator-procedure steps as the project answer.

#### Q9

`question_text`: **What Human decision, if any, is pending?**

`required_dimensions[]`:

- only explicit durable pending Human decision;
- distinction between none recorded and not determinable;
- available controls/actions are not pending decisions by themselves.

#### Q10

`question_text`: **What current or future work is only proposed/planned and therefore not authorized? For the current Slice, distinguish whether design/opening authority exists from whether implementation authority exists, then identify later roadmap work that remains not open/not authorized.**

`required_dimensions[]`:

- current Slice lifecycle/planned status;
- current Slice design/opening authority boundary;
- current Slice implementation authority boundary;
- later roadmap work remaining not open/not authorized;
- no authority inference from roadmap order, capability, `PROPOSED`, or document presence.

### 2.4 Operator-input binding

The deterministic operator-input envelope MUST embed or byte-identically reference the complete `B4QuestionContractV1`, including `required_dimensions[]` for all questions.

The envelope MUST carry:

- `question_set_id`;
- `question_contract_sha256`;
- exact canonical contract path/content identity;
- B4AnswerSetV1 destination.

The operator MUST be able to read every mandatory evaluated dimension before answering.

### 2.5 Answer-set binding

`B4AnswerSetV1` MUST contain:

- `question_set_id`;
- `question_contract_sha256`;
- for each answer, exact `question_id` and `question_text`.

`validate-answers` MUST reject:

- wrong question-set ID;
- wrong contract digest;
- question text differing from the canonical contract;
- missing/duplicate Q IDs.

The answer set does not need to duplicate `required_dimensions[]`; it is bound to them by the immutable contract digest.

### 2.6 Evaluator binding

Independent evaluation MUST record the same `question_set_id` and `question_contract_sha256` from terminal evidence.

Evaluator rule:

> A mandatory semantic dimension is scoreable only if it is present in the accepted operator-visible `required_dimensions[]` for that question.

This closes F001.

## 3. F002 closure — durable post-launch evidence

### 3.1 New evidence paths

Every future B4 execution authority MUST pin unique paths for at least:

- raw stdout capture;
- raw stderr capture;
- prepare-result artifact;
- successful prepare manifest;
- operator-input envelope;
- operator answer set;
- terminal evidence.

All runner-owned output targets use no-overwrite / exclusive-create semantics.

### 3.2 Pre-spawn capture establishment

Before spawning the harness, the runner MUST successfully establish both child output destinations:

```text
stdout_path -> exclusive-create file
stderr_path -> exclusive-create file
```

Preferred mechanics:

```text
os.open(stdout_path, O_WRONLY | O_CREAT | O_EXCL, 0o600)
os.open(stderr_path, O_WRONLY | O_CREAT | O_EXCL, 0o600)
```

The child MUST receive those durable file descriptors directly as stdout/stderr.

No material harness stdout or stderr may exist only in terminal UI, model context, or an in-memory `PIPE` as the designed path.

If either capture destination cannot be established before spawn:

- harness invocation count remains 0;
- disposition is pre-launch failure;
- do not spawn the harness;
- do not retry under the same authority.

### 3.3 Child execution

After both capture files are established:

```text
spawn accepted harness once
stdout -> durable stdout file
stderr -> durable stderr file
wait for child
flush/fsync/close stdout
flush/fsync/close stderr
hash exact stdout bytes
hash exact stderr bytes
```

Both byte streams are preserved regardless of child exit code.

### 3.4 New normative artifact: B4PrepareResultV1

A runner-owned `B4PrepareResultV1` is the durable terminal record for the `prepare` phase.

It is distinct from the success-only `B4PrepareManifestV1`.

Conceptual schema:

```text
B4PrepareResultV1
  schema_version: 1
  authority_id
  run_id
  attempt_number
  execution_started: bool
  harness_invocation_count
  harness_exit_code | null
  stdout
    path
    size
    sha256
  stderr
    path
    size
    sha256
  validation
    stdout_nonempty
    stdout_json_valid
    query_only_valid
    relay_schema_version_valid
  failure_stage | null
  failure_code | null
  prepare_outcome
  recorded_at
```

Allowed `prepare_outcome` values:

```text
PREPARED
INVALID_PRECHECK
INVALID_CAPTURE_SETUP
INVALID_HARNESS_EXIT
INVALID_HARNESS_OUTPUT
INVALID_HARNESS_PROTOCOL
INVALID_PREPARE_EVIDENCE
```

`B4PrepareResultV1` is procedural evidence only and contains no semantic B4 score.

### 3.5 Ordering invariant

After child execution begins, the runner MUST establish the durable prepare-result basis before creating any success-only preparation manifest or operator-input envelope.

Normative success ordering:

```text
child exits
  -> fsync/close stdout + stderr
  -> hash both streams
  -> validate harness output/protocol
  -> write + fsync B4PrepareResultV1 with PREPARED
  -> hash B4PrepareResultV1
  -> only then write B4PrepareManifestV1
  -> only then write operator-input envelope
```

Normative failure ordering after spawn:

```text
child exits or validation fails
  -> preserve/fsync stdout + stderr
  -> hash available exact bytes
  -> write + fsync B4PrepareResultV1 with exact failure stage/code
  -> STOP
```

No success-only manifest or operator envelope is generated after a failed prepare result.

If the filesystem itself prevents `B4PrepareResultV1` from being written, the runner reports `INVALID_PREPARE_EVIDENCE` externally and stops; stdout/stderr remain preserved where possible. The design does not claim to make evidence durable when the evidence filesystem itself is unavailable.

### 3.6 B4PrepareManifestV1 amendment

`B4PrepareManifestV1` now exists only for a successful `PREPARED` result.

It MUST reference:

- `prepare_result_path`;
- `prepare_result_sha256`;
- stdout path/digest;
- stderr path/digest;
- exact question-contract path/digest;
- registry/canonical identities.

It MUST NOT be the sole record of child exit, stderr, or prepare failure.

### 3.7 Terminal evidence amendment

`B4TerminalEvidenceV2` MUST reference the immutable prepare-result path/digest in addition to the successful prepare manifest when present.

For a valid semantic run:

```text
prepare_result.prepare_outcome = PREPARED
prepare manifest present
operator envelope present
answer set structurally valid
seal succeeds
```

For prepare-phase failure, no semantic evaluation occurs.

This closes F002.

## 4. O001 closure — one canonical source-inventory declaration

The canonical operator declaration of inspected/prohibited sources is `B4AnswerSetV1`.

`B4AnswerSetV1` owns exactly:

```text
inspected_sources[]
prohibited_sources_accessed[]
```

`seal` MUST NOT request or accept a second independently editable source inventory.

`B4TerminalEvidenceV2` copies these fields deterministically from the sealed answer set and records the answer-set digest from which they came.

If a separate deterministic runner-observed command/file access log exists, it MUST be named distinctly, for example:

`runner_observed_accesses[]`

and MUST NOT be presented as another operator declaration.

Any discrepancy between operator declaration and deterministic runner observation is preserved for independent evaluation; the runner does not silently reconcile them.

This closes O001.

## 5. Revised prepare state machine

```text
START
  |
  +-- deterministic preflight
  |      failure -> INVALID_PRECHECK / invocation_count=0 / STOP
  |
  +-- establish stdout + stderr exclusive captures
  |      failure -> INVALID_CAPTURE_SETUP / invocation_count=0 / STOP
  |
  +-- invoke harness EXACTLY ONCE
  |
  +-- fsync/close/hash stdout + stderr
  |
  +-- child exit / JSON / query_only / schema validation
  |      failure
  |        -> durable B4PrepareResultV1(failure)
  |        -> STOP
  |
  +-- durable B4PrepareResultV1(PREPARED)
  |
  +-- B4PrepareManifestV1
  |
  +-- operator-input envelope + B4QuestionContractV1 digest
  |
  v
READY_FOR_FRESH_OPERATOR
```

The model is not responsible for any transition in this state machine.

## 6. Revised implementation footprint

Preferred minimal implementation becomes:

```text
scripts/b4_execution_runner.py
scripts/b4_question_contract_v1.json
tests/integration/test_b4_execution_runner.py
```

`scripts/b4_readonly_harness.py` remains unchanged unless implementation proves a separately reviewed blocker.

No `src/relay_engine/` product-source change is expected.

## 7. Additional implementation acceptance criteria

The Revision 2 AC set is amended with:

**AC16 — complete operator-visible contract**  
Every evaluator-mandatory dimension is present in canonical `required_dimensions[]`, included in the question-contract digest, and supplied to the operator.

**AC17 — evaluator contract identity**  
Terminal evidence binds independent evaluation to the exact question-set ID and digest supplied to the operator.

**AC18 — durable stderr**  
Harness stderr is redirected to an exclusive durable file before spawn and hashed after child termination.

**AC19 — durable prepare outcome**  
Every normal post-launch terminal prepare path writes `B4PrepareResultV1` before any success-only manifest/envelope step.

**AC20 — prepare ordering**  
`B4PrepareManifestV1` and operator input cannot be created unless the immutable prepare result already records `PREPARED`.

**AC21 — single source inventory**  
Operator source declarations originate only in `B4AnswerSetV1`; terminal evidence copies rather than recollects them.

## 8. Additional required focused tests

Implementation tests MUST additionally cover:

```text
canonical question contract contains required_dimensions[] for Q1-Q10
question-contract digest changes if any required dimension changes
operator envelope contains exact canonical question contract/digest
evaluator/terminal evidence binds same question-contract digest
answer set with wrong question-contract digest rejected

stderr target pre-exists -> no harness invocation
stderr capture setup failure -> no harness invocation
harness non-zero -> stdout and stderr preserved + hashed
harness invalid JSON -> stdout and stderr preserved + prepare-result failure
query_only mismatch -> durable prepare-result failure
schema mismatch -> durable prepare-result failure
success -> PREPARED result exists before manifest/envelope generation
manifest-generation failure after PREPARED does not lose child/capture outcome
operator-envelope generation failure after PREPARED does not lose child/capture outcome

seal accepts exactly one operator source declaration
terminal evidence copies source inventory from answer-set bytes/digest
```

## 9. Rework scope audit

This amendment does not:

- alter Q1-Q10 factual answers;
- expose expected state values;
- change the B4 scientific objective;
- change read-model semantics;
- change the accepted read-only harness;
- create a generic execution framework;
- authorize implementation;
- authorize attempt 006;
- open Slice 2.2.

## 10. Composite design disposition

The Revision 2 design candidate is now the composite:

```text
Revision 2 base:
ebc05e22d921ea8a4ac55b0c5c0006a86fe0d2da

Revision 2 Rework 1:
this amendment
```

Required next gate:

independent review of the composite Revision 2 + Rework 1 design.

Status:

```text
RLY-S110-DOGFOOD-B4-R2-DESIGN-AUTH-001 — AUTHORIZED

F001:
DESIGN REWORKED

F002:
DESIGN REWORKED

O001:
CLARIFIED

B4 Revision 2 composite:
READY FOR INDEPENDENT RE-REVIEW

Runner implementation:
NOT AUTHORIZED

B4 attempt 006:
NOT AUTHORIZED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```