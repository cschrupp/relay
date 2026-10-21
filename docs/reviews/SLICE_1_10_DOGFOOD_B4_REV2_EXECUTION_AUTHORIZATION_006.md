# Slice 1.10 Dogfood B4 Revision 2 — Cold-Start Execution Authorization 006

**Document class:** Immutable Human execution authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-21  
**Record:** `RLY-S110-DOGFOOD-B4-R2-EXEC-AUTH-006`  
**Decision:** `AUTHORIZED`  
**Attempts authorized:** exactly one B4 Revision 2 fresh-operator attempt

## 1. Human decision

The Human authorizes B4 Revision 2 cold-start execution Attempt 006.

This is the first execution of the Human-accepted Revision 2 deterministic runner/question contract. It is a full ten-question independent cold-start run, not a targeted retest of prior failures.

This authority permits only the bounded B4 Attempt 006 execution described below. It does not authorize B4 semantic acceptance, repository promotion, Slice 2.2 opening, Slice 2.2 design, Slice 2.2 implementation, or any other downstream work.

## 2. Accepted basis

```text
B4 Revision 2 design:
RLY-S110-DOGFOOD-B4-R2-DESIGN-ACCEPT-001 — ACCEPTED

Runner implementation:
RLY-S110-DOGFOOD-B4-R2-IMPL-ACCEPT-001 — ACCEPTED

Exact accepted implementation candidate:
9b6aa95ab366dcf99981adddc10d917ef15e1dc8

Independent implementation evaluation:
RLY-S110-DOGFOOD-B4-R2-IMPL-EVAL-002 — ACCEPT

Implementation Human acceptance:
commit 2774889f43fff0e22fc94e7d6f7b5a4b04d6a3bb
```

Later evaluation/acceptance commits are governance evidence for authorizing the run. They are not part of the operator's factual answer surface.

## 3. Exact execution checkout and identities

```text
Execution checkout:
9b6aa95ab366dcf99981adddc10d917ef15e1dc8

Execution worktree:
/tmp/relay-b4-r2-attempt-006-pinned

Runner path:
scripts/b4_execution_runner.py

Runner Git blob:
301545a7f4b26be23a764a69a6d2ba3f3007a418

Runner test Git blob:
7dba00d586d53a5360a3929442c75a4add74e152

Accepted read-only harness path:
scripts/b4_readonly_harness.py

Accepted harness Git blob:
f98350ff14dbfb1bf6388de88fff366e67ec1afd

Accepted harness-test path:
tests/integration/test_b4_readonly_harness.py

Accepted harness-test Git blob:
6708eb8b1a3fcb8484a227a447ace678c3ec20d0

Question-contract path:
scripts/b4_question_contract_v1.json

Question-contract Git blob:
17e788cd15961cd5609670292aea906c6e8de9f4

Question-contract SHA-256:
59d9a0a8e005eb81fd577c476fdc9be37248105d6d194aa2e16ed27bbc0da0b6

Question set:
B4-R2-QSET-001
```

The checkout is intentionally pinned to the exact Human-accepted implementation subject, not to the later evaluation/acceptance/authority commits. The fresh operator must not inspect later repository state.

## 4. Operational state pins

The last valid B4 run established the operational DB digest below both before and after its read-only execution. Revision 2 implementation work explicitly did not access the real operational DB. Attempt 006 therefore uses the same expected digest and MUST independently verify it before harness spawn.

```text
Operational DB:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Required DB SHA-256:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

Project ID:
prj_018f47c1-7b2c-7abc-8def-123456789001

Current Slice ID:
slc_01a15754-1123-7535-9ded-6a564518e347
```

Any DB digest mismatch is a preflight failure. Do not derive or authorize a replacement digest during this attempt.

## 5. Attempt identity

```text
Authority ID:
RLY-S110-DOGFOOD-B4-R2-EXEC-AUTH-006

Run ID:
B4-R2-ATTEMPT-006

Attempt number:
6
```

Exactly one harness child invocation is authorized, solely through the accepted runner.

No direct manual invocation of `scripts/b4_readonly_harness.py` is authorized.

## 6. Unique evidence paths

All Attempt 006 evidence paths are unique and outside the repository:

```text
stdout:
/home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.stdout.json

stderr:
/home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.stderr.txt

prepare result:
/home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.prepare-result.json

prepare manifest:
/home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.prepare-manifest.json

operator input:
/home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.operator-input.json

operator answer set:
/home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.answer-set.json

terminal evidence:
/home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.terminal-evidence.json
```

The evidence directory must already exist.

Every target above MUST be absent before `prepare`. Do not delete, truncate, overwrite, auto-number, or substitute paths to recover from a failure. A failed attempt is preserved and consumed.

## 7. Checkout qualification

Before any runner invocation or DB access, create/use the pinned worktree and require:

```bash
cd /tmp/relay-b4-r2-attempt-006-pinned
pwd
git rev-parse HEAD
git status --porcelain
git rev-parse HEAD:scripts/b4_execution_runner.py
git rev-parse HEAD:tests/integration/test_b4_execution_runner.py
git rev-parse HEAD:scripts/b4_question_contract_v1.json
git rev-parse HEAD:scripts/b4_readonly_harness.py
git rev-parse HEAD:tests/integration/test_b4_readonly_harness.py
```

Require:

```text
pwd:
/tmp/relay-b4-r2-attempt-006-pinned

HEAD:
9b6aa95ab366dcf99981adddc10d917ef15e1dc8

git status --porcelain:
<empty>

runner blob:
301545a7f4b26be23a764a69a6d2ba3f3007a418

runner-test blob:
7dba00d586d53a5360a3929442c75a4add74e152

question-contract blob:
17e788cd15961cd5609670292aea906c6e8de9f4

harness blob:
f98350ff14dbfb1bf6388de88fff366e67ec1afd

harness-test blob:
6708eb8b1a3fcb8484a227a447ace678c3ec20d0
```

Any mismatch consumes Attempt 006 fail-closed. Do not repair the pinned checkout under this authority.

## 8. Authorized prepare command

After checkout qualification, execute exactly one runner `prepare`:

```bash
uv run python scripts/b4_execution_runner.py prepare \
  --authority-id RLY-S110-DOGFOOD-B4-R2-EXEC-AUTH-006 \
  --run-id B4-R2-ATTEMPT-006 \
  --attempt-number 6 \
  --execution-root /tmp/relay-b4-r2-attempt-006-pinned \
  --expected-head 9b6aa95ab366dcf99981adddc10d917ef15e1dc8 \
  --harness-path scripts/b4_readonly_harness.py \
  --expected-harness-blob f98350ff14dbfb1bf6388de88fff366e67ec1afd \
  --harness-test-path tests/integration/test_b4_readonly_harness.py \
  --expected-harness-test-blob 6708eb8b1a3fcb8484a227a447ace678c3ec20d0 \
  --database-path /home/user/projects/relay-local-state/relay-operational.sqlite3 \
  --expected-db-sha256 6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e \
  --project-id prj_018f47c1-7b2c-7abc-8def-123456789001 \
  --slice-id slc_01a15754-1123-7535-9ded-6a564518e347 \
  --question-contract-path scripts/b4_question_contract_v1.json \
  --expected-question-contract-sha256 59d9a0a8e005eb81fd577c476fdc9be37248105d6d194aa2e16ed27bbc0da0b6 \
  --stdout-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.stdout.json \
  --stderr-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.stderr.txt \
  --prepare-result-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.prepare-result.json \
  --prepare-manifest-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.prepare-manifest.json \
  --operator-input-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.operator-input.json \
  --answer-set-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.answer-set.json \
  --terminal-evidence-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.terminal-evidence.json
```

This command is the sole authorized route to the harness child.

If `prepare` does not produce `PREPARED`, STOP. Attempt 006 is consumed. Do not rerun.

## 9. Fresh-operator custody

Only after successful `PREPARED`, start one fresh operator session that has not participated in:

- Relay planning/design;
- prior B4 attempts;
- B4 Revision 2 design/review;
- B4 runner implementation/review;
- this conversation.

Provide the fresh operator only:

1. the exact pinned checkout at `9b6aa95ab366dcf99981adddc10d917ef15e1dc8`;
2. the runner-generated Attempt 006 operator-input envelope;
3. permission to inspect only the sources allowed by that envelope.

Do not provide:

- prior Relay/ChatGPT conversation;
- project bootstrap summaries;
- prior B4 answers/evidence;
- prior B4 evaluations or outcomes;
- B4 Revision 2 evaluator records;
- this execution authority as factual answer evidence;
- expected factual answers;
- evaluator scoring notes or source matrix;
- repository state later than the pinned execution checkout.

The operator must use the exact cold-start declaration emitted by the runner.

If fresh-session custody cannot be established, STOP INVALID. Do not substitute a previously involved agent.

## 10. Answer production

The operator must answer all ten questions in `B4-R2-QSET-001` and write exactly one `B4AnswerSetV1` to:

`/home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.answer-set.json`

The visible `question_text` and `required_dimensions[]` in the runner-generated envelope are the complete operator contract.

The operator must not:

- self-score;
- compare with prior runs;
- seek evaluator material;
- infer expected factual answers from this authority;
- inspect later commits/branches;
- mutate Relay repository state or the operational DB.

Structural corrections before seal are permitted only in the same fresh operator session and only from runner structural validation output. No semantic/evaluator feedback may be supplied.

## 11. Structural validation

After the operator writes the answer set, run:

```bash
uv run python scripts/b4_execution_runner.py validate-answers \
  --prepare-manifest-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.prepare-manifest.json \
  --answer-set-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.answer-set.json
```

If structural validation fails, only structural correction in the same fresh operator session is permitted before seal. Do not provide semantic hints or evaluator information.

## 12. Seal

Once structurally valid, execute exactly:

```bash
uv run python scripts/b4_execution_runner.py seal \
  --prepare-manifest-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.prepare-manifest.json \
  --answer-set-path /home/user/projects/relay-local-state/adoption-evidence/b4-r2-attempt-006.answer-set.json
```

Require terminal evidence to report:

`SEALED_READY_FOR_INDEPENDENT_EVALUATION`

If it reports `INVALID_DB_MUTATION` or any other invalid outcome, STOP. Semantic B4 evaluation is not eligible.

After terminal evidence exists, the answer set and evidence are sealed and must not be corrected or supplemented.

## 13. Independent result evaluation boundary

Only after successful seal may the Attempt 006 terminal evidence be handed to an independent evaluator.

The evaluator, not the runner and not the operator, performs semantic scoring.

B4 succeeds only if:

- protocol/custody is valid;
- DB is unchanged;
- all ten mandatory questions independently PASS.

A semantic PASS still requires separate Human result acceptance before B4 is complete.

## 14. Explicitly not authorized

This authority does not permit:

- a second Attempt 006 harness invocation;
- Attempt 007;
- deletion/reconstruction of failed Attempt 006 evidence;
- modification of the pinned checkout;
- direct harness invocation outside the runner;
- DB write/migration/checkpoint/vacuum/repair/normalization;
- B4 semantic scoring by the operator or runner;
- rewriting prior B4 records;
- promotion/merge;
- Slice 2.2 opening;
- Slice 2.2 design;
- Slice 2.2 implementation;
- Phase 3 execution.

## 15. Required execution handoff

Return:

```text
Authority:
RLY-S110-DOGFOOD-B4-R2-EXEC-AUTH-006

Execution checkout:
Execution worktree:
Worktree clean:

Runner Git blob:
Runner-test Git blob:
Question-contract Git blob:
Question-contract SHA-256:
Harness Git blob:
Harness-test Git blob:

DB SHA before:
Prepare result:
Harness invocation count:
Harness exit code:
stdout SHA-256:
stderr SHA-256:
query_only validation:
schema validation:

Fresh operator/session identity:
Runtime identity:
Model identity:
Cold-start declaration:
Inspected sources:
Prohibited sources accessed:

Answer validation:
Answer-set path:
Answer-set SHA-256:

Terminal protocol result:
Terminal-evidence path:
Terminal-evidence SHA-256:
DB SHA after:
DB unchanged:
Sidecar observations:

B4 semantic scoring performed by operator/runner:
NO

Attempt 006 harness invocation count:
1

Slice 2.2 work performed:
NO

Status:
STOP FOR INDEPENDENT B4 RESULT EVALUATION
```

## 16. Authority status

```text
RLY-S110-DOGFOOD-B4-R2-EXEC-AUTH-006 — AUTHORIZED

B4 Revision 2 design:
COMPLETE / HUMAN ACCEPTED

B4 Revision 2 runner implementation:
COMPLETE / HUMAN ACCEPTED

B4 Attempt 006:
AUTHORIZED / NOT YET EXECUTED

B4 result:
NOT ESTABLISHED

Slice 2.2:
NOT OPEN / NOT AUTHORIZED
```
