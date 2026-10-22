# Slice 1.10 Dogfood B4 — Cold-Start Execution Authorization 003

**Document class:** Immutable Human execution authority
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-AUTH-003`
**Decision:** `AUTHORIZED`
**Attempts authorized:** exactly one fresh-operator attempt

## Human decision

The Human authorizes B4 cold-start execution attempt 003.

Prior attempts remain consumed:

- attempt 001: `RLY-S110-DOGFOOD-B4-EXEC-EVAL-001 — FAIL_CLOSED / NO ANSWER PHASE`
- attempt 002: `RLY-S110-DOGFOOD-B4-EXEC-EVAL-002 — FAIL_CLOSED / NO DB ACCESS / NO ANSWER PHASE`

This authority does not amend or reuse either prior attempt.

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

Before any DB access, the fresh operator must execute these exact commands from
`/tmp/relay-b4-cold-start-pinned`:

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

The two 40-hex harness values are **Git blob object IDs**, not SHA-256 file digests.
Do not compute or compare ordinary file SHA-256 values for this pin check.

Any mismatch consumes attempt 003 fail-closed.

## Fresh-operator custody

Use one newly started operator session with no prior Relay/ChatGPT conversation, project-history summary, evaluator answer key, expected answers, or B4 evaluator source matrix.

The operator is read-only and must not self-score.

Before answer sealing the operator must not inspect:

- prior Relay/ChatGPT conversation material;
- assistant/Codex reconstruction summaries;
- evaluator notes or expected answers;
- prior B4 answer packets;
- `docs/slices/SLICE_1_10_DOGFOOD_B4_RELAY_DOGFOOD_ACCEPTANCE_DESIGN.md`;
- `docs/reviews/SLICE_1_10_DOGFOOD_B4_DESIGN_EVALUATION_001.md`.

## Cold-start declaration

The operator must record:

```text
I am executing B4 attempt 003 as a fresh read-only operator. I was not provided
the prior Relay/ChatGPT conversation, assistant summaries, evaluator answer key,
expected answers, or B4 evaluator source matrix. I will use only the allowed
information surfaces under RLY-S110-DOGFOOD-B4-EXEC-AUTH-003 and will seal my
answers before any evaluator comparison.
```

If false or unavailable, STOP INVALID.

## Allowed operator surfaces

The operator may inspect:

- `.relay/registry.json`;
- registry-resolved current canonical documents;
- accepted immutable governance records normally discoverable from allowed records;
- repository code/CLI help solely to understand existing behavior;
- the accepted read-only harness;
- harness-produced `project_board` and `slice_detail` JSON.

Ordinary repository search may be used to follow allowed references.

## Live DB preflight

After checkout verification:

1. compute the live DB SHA-256 and require the exact authorized digest;
2. record existing `-wal` and `-shm` metadata/hashes without mutation;
3. invoke the accepted harness exactly once;
4. require `query_only == 1`;
5. require Relay schema version 8;
6. retain and hash the raw harness JSON output.

Harness command:

```bash
uv run python scripts/b4_readonly_harness.py \
  --database /home/user/projects/relay-local-state/relay-operational.sqlite3 \
  --project-id prj_018f47c1-7b2c-7abc-8def-123456789001 \
  --slice-id slc_01a15754-1123-7535-9ded-6a564518e347
```

No DB write, migration, checkpoint, vacuum, repair, normalization, or sidecar cleanup is authorized.

## Frozen questions

Answer in exact order:

1. What project is this?
2. What is the project objective?
3. What information is contextual or pre-T1 legacy rather than Relay lifecycle?
4. What is the current governed work frontier?
5. What exact Slice is current?
6. What lifecycle phase is it in?
7. What is blocked?
8. What happens next?
9. What Human decision, if any, is pending?
10. What work is only planned/proposed and therefore not authorized?

For every answer record:

- answer;
- source class;
- exact source locator(s);
- relevant field/record identity;
- whether any part is `NOT DETERMINABLE FROM CURRENT DURABLE STATE`.

Do not score answers.

## Evidence and sealing

Write exactly:

`/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-operator-evidence-attempt-003.json`

Include the cold-start declaration, runtime/session/model identity as exposed, preflight, inspected-source inventory, raw harness-output SHA-256, Q1-Q10 answers and sources, and answer-sealed timestamp.

Compute and report the evidence SHA-256. Do not modify or correct the packet after reporting that digest.

Then close all DB connections, recompute the live DB SHA-256, require equality with the pre-run digest, record sidecar observations, and STOP for independent evaluation.

## Explicitly not authorized

No self-scoring, post-seal answer correction, B4 Human result acceptance, Axis B replay, DB/repository mutation, lifecycle/Slice mutation, Slice 2.2 design or implementation, Role Contracts implementation, Phase 3, promotion, or fourth attempt.

## Status

```text
RLY-S110-DOGFOOD-B4-EXEC-AUTH-003 — AUTHORIZED

Attempt 001:
CONSUMED / FAIL_CLOSED

Attempt 002:
CONSUMED / FAIL_CLOSED

Attempt 003:
AUTHORIZED / NOT YET RUN

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED
```
