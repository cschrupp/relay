# Slice 1.10 Dogfood B4 — Cold-Start Execution Authorization 005

**Document class:** Immutable Human execution authority
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-AUTH-005`
**Decision:** `AUTHORIZED`
**Attempts authorized:** exactly one fresh-operator attempt

## Human decision

The Human authorizes B4 cold-start execution attempt 005.

Attempt 005 is a full independent cold-start run. It is not a correction session and the operator must not receive prior B4 answers, evaluations, or question outcomes.

The accepted B4 design and accepted read-only harness remain unchanged.

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

Raw harness capture path:
/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-harness-attempt-005.json

Operator evidence path:
/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-operator-evidence-attempt-005.json
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

Require exactly:

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

The 40-hex harness values are Git blob object IDs. Verify them only with the exact `git rev-parse HEAD:<path>` commands above.

Any mismatch consumes attempt 005 fail-closed.

## Cold-start custody

Use one newly started Codex delegated operator session with no prior participation in Relay planning or prior B4 runs.

Do not provide:

- prior Relay/ChatGPT conversation;
- assistant/project-history summaries;
- prior B4 answers or evidence packets;
- prior B4 evaluations or dispositions;
- information about which prior questions passed or failed;
- evaluator answer key, expected answers, source matrix, or scoring guidance.

The operator must answer all ten questions independently from allowed durable surfaces.

## Required declaration

Before inspection, record:

```text
I am executing B4 attempt 005 as a fresh read-only operator. I was not provided
the prior Relay/ChatGPT conversation, assistant summaries, prior B4 answers or
evaluations, information about prior question outcomes, evaluator answer key,
expected answers, or B4 evaluator source matrix. I will use only the allowed
information surfaces under RLY-S110-DOGFOOD-B4-EXEC-AUTH-005 and will seal my
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
6. the single captured harness `project_board` and `slice_detail` JSON;
7. external evidence only where an allowed pinned record explicitly names its exact path and digest.

The execution authority/run card is for pins, safety limits, questions, and evidence instructions only; it is not an answer source.

## Prohibited operator surfaces

Before sealing answers, do not inspect:

- prior Relay/ChatGPT conversations;
- prior B4 answer/evidence packets;
- prior B4 execution evaluations;
- assistant/Codex reconstruction summaries;
- evaluator notes, expected answers, source matrix, or scoring rubric;
- `docs/slices/SLICE_1_10_DOGFOOD_B4_RELAY_DOGFOOD_ACCEPTANCE_DESIGN.md`;
- `docs/reviews/SLICE_1_10_DOGFOOD_B4_DESIGN_EVALUATION_001.md`;
- any later governance checkout or branch beyond the pinned execution checkout.

If any prohibited surface is accessed, STOP INVALID.

## Live DB preflight

Before harness invocation:

1. compute the operational DB SHA-256 and require the authorized digest;
2. inventory existing `-wal` and `-shm` metadata and hashes without mutation;
3. require that the raw-output capture path does not already exist.

No DB write, migration, checkpoint, vacuum, repair, normalization, or sidecar cleanup is authorized.

## Atomic raw-output capture

The single authorized harness invocation must be coupled directly to file capture.

Execute exactly:

```bash
set -euo pipefail

RAW=/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-harness-attempt-005.json

test ! -e "$RAW"

uv run python scripts/b4_readonly_harness.py \
  --database /home/user/projects/relay-local-state/relay-operational.sqlite3 \
  --project-id prj_018f47c1-7b2c-7abc-8def-123456789001 \
  --slice-id slc_01a15754-1123-7535-9ded-6a564518e347 \
  > "$RAW"

test -s "$RAW"
python -m json.tool "$RAW" >/dev/null
sha256sum "$RAW"
```

The harness must not be invoked before, after, or outside that exact capture command.

The operator must then read the captured JSON file, require:

```text
query_only = 1
schema_version = 8
```

and record the exact SHA-256 emitted by `sha256sum`.

If capture, non-empty check, JSON validation, or hashing fails, STOP. Do not rerun or reconstruct the harness output.

## Frozen operator questions

Answer all ten, in exact order:

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

For each record:

```text
Answer:
Source class:
Source locator(s):
Relevant field/record:
Not determinable from durable state: yes/no
```

Do not guess, self-score, compare with previous answers, or inspect evaluator material.

## Evidence and sealing

Write exactly:

`/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-operator-evidence-attempt-005.json`

The packet must include:

- authority and attempt;
- cold-start declaration;
- session/runtime/model identity as available;
- checkout and harness-pin preflight;
- DB digest and sidecar observations before;
- exact atomic harness command;
- raw harness capture path and SHA-256;
- `query_only` and schema version;
- inspected-source inventory;
- verbatim Q1-Q10 answers and source records;
- answer-sealed timestamp.

After writing the packet:

```bash
EVIDENCE=/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-operator-evidence-attempt-005.json
test -s "$EVIDENCE"
python -m json.tool "$EVIDENCE" >/dev/null
sha256sum "$EVIDENCE"
```

The SHA-256 reported by that command seals the packet.

After sealing:

- do not modify the packet;
- do not correct or supplement answers;
- do not inspect evaluator material;
- do not self-evaluate.

## Post-run read-only proof

After sealing:

1. close all DB connections;
2. recompute the operational DB SHA-256;
3. require equality with the pre-run digest;
4. record final `-wal` and `-shm` metadata/hashes;
5. do not modify sidecars.

A sidecar modification-time change alone is observational evidence.

## Explicitly not authorized

No repository mutation, DB mutation, lifecycle/Slice change, Axis B replay, B4 scoring, answer correction, Human result acceptance, Slice 2.2 design or implementation, Role Contracts implementation, Phase 3, promotion, or sixth attempt.

## Required handoff

Return:

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
Raw harness capture path:
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
B4 execution attempt count: 5
Slice 2.2 work performed: NO

Status:
STOP FOR INDEPENDENT B4 RESULT EVALUATION
```

## Authority status

```text
RLY-S110-DOGFOOD-B4-EXEC-AUTH-005 — AUTHORIZED

ATTEMPT 005:
AUTHORIZED / NOT YET RUN

B4 RESULT:
NOT ESTABLISHED BY THIS AUTHORITY

SLICE 2.2 DESIGN:
NOT OPEN / NOT AUTHORIZED
```
