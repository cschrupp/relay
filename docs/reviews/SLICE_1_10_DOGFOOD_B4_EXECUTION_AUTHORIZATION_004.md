# Slice 1.10 Dogfood B4 — Cold-Start Execution Authorization 004

**Document class:** Immutable Human execution authority
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-AUTH-004`
**Decision:** `AUTHORIZED`
**Attempts authorized:** exactly one fresh-operator attempt

## Human decision

The Human authorizes one full B4 cold-start rerun as attempt 004.

Attempt 004 is not a correction session and is not a targeted retest. The operator must answer all ten frozen B4 questions from a fresh context and must not be told which questions, if any, failed in prior attempts.

Prior attempts remain immutable and consumed. This authority does not amend or reuse them.

## Scientific / product question

Can a new operator, with no prior Relay conversation or prior B4 answer/evaluation context, recover the same governed project state from Relay's accepted durable/read-only surfaces?

The rerun tests independent recoverability. It must not become coached reproduction.

## Exact execution pins

```text
Accepted B4 design:
9b274eda204dac30da51181f2c1de25cf7237010

Accepted read-only harness:
36a53179c9951375450a94c0283e68a9428143fb

Execution checkout:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Execution worktree:
/tmp/relay-b4-cold-start-pinned

Operational DB:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Required DB SHA-256:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

Project:
prj_018f47c1-7b2c-7abc-8def-123456789001

Current Slice:
slc_01a15754-1123-7535-9ded-6a564518e347
```

## Frozen checkout verification

Before any DB access, from `/tmp/relay-b4-cold-start-pinned`, execute exactly:

```bash
pwd
git rev-parse HEAD
git status --short
git rev-parse HEAD:scripts/b4_readonly_harness.py
git rev-parse HEAD:tests/integration/test_b4_readonly_harness.py
```

Required results:

```text
pwd:
/tmp/relay-b4-cold-start-pinned

HEAD:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

git status --short:
<empty>

scripts/b4_readonly_harness.py Git blob ID:
f98350ff14dbfb1bf6388de88fff366e67ec1afd

tests/integration/test_b4_readonly_harness.py Git blob ID:
6708eb8b1a3fcb8484a227a447ace678c3ec20d0
```

The two 40-hex harness values are Git blob object IDs. Verify them only with the exact `git rev-parse HEAD:<path>` commands above. Do not compare them to ordinary file SHA-256 digests.

Any mismatch consumes attempt 004 fail-closed.

## Cold-start custody

The operator must be a newly started Codex delegated session/run with no prior participation in Relay planning or prior B4 attempts.

Do not provide the operator:

- any prior Relay/ChatGPT conversation;
- assistant/project-history summaries;
- prior B4 operator answers;
- prior B4 evaluations or dispositions;
- information about which questions previously passed or failed;
- expected answers;
- evaluator source matrix or scoring guidance;
- evaluator coaching.

The operator may know only that it is executing one authorized B4 cold-start read-only run and must answer the ten supplied questions from allowed durable surfaces.

## Required declaration

Before inspection, record:

```text
I am executing B4 attempt 004 as a fresh read-only operator. I was not provided
the prior Relay/ChatGPT conversation, assistant summaries, prior B4 answers or
evaluations, information about prior question outcomes, evaluator answer key,
expected answers, or B4 evaluator source matrix. I will use only the allowed
information surfaces under RLY-S110-DOGFOOD-B4-EXEC-AUTH-004 and will seal my
answers before any evaluator comparison.
```

If false or unavailable, STOP INVALID.

## Allowed operator surfaces

The operator may inspect only:

1. `.relay/registry.json`;
2. current canonical documents resolved through that registry;
3. accepted immutable governance records normally discoverable from allowed canonical records;
4. repository code and CLI help solely to understand existing behavior;
5. the accepted read-only harness;
6. the harness-produced `project_board` and `slice_detail` JSON;
7. external evidence only where an allowed pinned record explicitly names its path and digest.

Ordinary repository search is permitted only to follow allowed references.

The execution authority/run card may be used for execution pins, safety limits, questions, and evidence instructions. It is not an answer source.

## Prohibited operator surfaces

Before sealing answers, do not inspect:

- any prior Relay/ChatGPT conversation;
- prior B4 operator evidence;
- prior B4 execution evaluations;
- assistant/Codex reconstruction summaries;
- evaluator notes, expected answers, source matrix, or scoring rubric;
- `docs/slices/SLICE_1_10_DOGFOOD_B4_RELAY_DOGFOOD_ACCEPTANCE_DESIGN.md`;
- `docs/reviews/SLICE_1_10_DOGFOOD_B4_DESIGN_EVALUATION_001.md`;
- any later governance branch or checkout beyond the pinned execution checkout.

If any prohibited surface is accessed before sealing, STOP INVALID.

## Live DB preflight

After checkout verification:

1. compute the operational DB SHA-256 and require the authorized digest;
2. inventory existing `-wal` and `-shm` metadata and hashes without mutation;
3. invoke the accepted harness exactly once;
4. require `query_only == 1`;
5. require schema version 8;
6. retain and hash the raw harness JSON output.

Harness command:

```bash
uv run python scripts/b4_readonly_harness.py \
  --database /home/user/projects/relay-local-state/relay-operational.sqlite3 \
  --project-id prj_018f47c1-7b2c-7abc-8def-123456789001 \
  --slice-id slc_01a15754-1123-7535-9ded-6a564518e347
```

No DB write, migration, checkpoint, vacuum, repair, normalization, sidecar cleanup, or repository mutation is authorized.

## Frozen operator questions

Answer all ten, in this exact order:

1. **What project is this?**
2. **What is the project objective?**
3. **What information is contextual or pre-T1 legacy rather than Relay lifecycle?**
4. **What is the current governed work frontier?**
5. **What exact Slice is current?**
6. **What lifecycle phase is it in?**
7. **What is blocked?**
8. **What happens next?**
9. **What Human decision, if any, is pending?**
10. **What work is only planned/proposed and therefore not authorized?**

For every question record:

```text
Answer:
Source class:
Source locator(s):
Relevant field/record:
Not determinable from durable state: yes/no
```

Do not guess. Do not score. Do not compare against prior answers.

## Evidence and sealing

Write exactly:

`/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-operator-evidence-attempt-004.json`

Include:

- cold-start declaration;
- session/runtime identity;
- model identity if exposed;
- full preflight;
- exact command/surface transcript;
- inspected-file/record inventory;
- raw harness-output SHA-256;
- verbatim Q1-Q10 answers and sources;
- answer-sealed timestamp.

Compute and report the evidence SHA-256.

After reporting the digest:

- do not modify the evidence packet;
- do not correct or supplement answers;
- do not inspect evaluator materials;
- do not self-evaluate.

Then close all DB connections, recompute the DB SHA-256, require equality with the pre-run digest, record final sidecar observations/hashes, and STOP for independent evaluation.

## Explicitly not authorized

- coaching or targeted correction of prior B4 failures;
- B4 self-scoring;
- answer correction after sealing;
- Human result acceptance;
- Axis B replay;
- repository or operational DB mutation;
- lifecycle/Slice mutation;
- Slice 2.2 design or implementation;
- Role Contracts implementation;
- AgentRuntime/OpenCode project execution;
- Phase 3;
- promotion;
- any fifth attempt.

## Required handoff

```text
Authority:
Execution checkout SHA:
Execution worktree:
Fresh operator/session identity:
Runtime:
Model identity:
Cold-start declaration: PASS/FAIL

Preflight: PASS/FAIL
Worktree clean:
Harness Git blob identity:
DB SHA before:
query_only:
schema version:
Raw harness output SHA-256:
Allowed sources inspected:
Prohibited sources inspected:

Q1
Answer:
Sources:

Q2
Answer:
Sources:

Q3
Answer:
Sources:

Q4
Answer:
Sources:

Q5
Answer:
Sources:

Q6
Answer:
Sources:

Q7
Answer:
Sources:

Q8
Answer:
Sources:

Q9
Answer:
Sources:

Q10
Answer:
Sources:

Operator evidence path:
Operator evidence SHA-256:
Answer sealed timestamp:

DB SHA after:
DB unchanged:
Sidecar observations:

B4 scoring performed: NO
B4 execution attempt count: 4
Slice 2.2 work performed: NO

Status:
STOP FOR INDEPENDENT B4 RESULT EVALUATION
```

## Authority status

```text
RLY-S110-DOGFOOD-B4-EXEC-AUTH-004 — AUTHORIZED

ATTEMPT 004:
AUTHORIZED / NOT YET RUN

B4 RESULT:
NOT ESTABLISHED BY THIS AUTHORITY

SLICE 2.2 DESIGN:
NOT OPEN / NOT AUTHORIZED
```
