# Slice 1.10 Dogfood B4 — Cold-Start Execution Authorization 002

**Document class:** Immutable Human execution authority
**Status:** IMMUTABLE
**Date:** 2026-10-21
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-AUTH-002`
**Decision:** `AUTHORIZED`
**Attempts authorized:** exactly one corrected fresh-operator attempt

## Human decision

The Human authorizes B4 cold-start execution attempt 002.

Attempt 001 remains consumed under
`RLY-S110-DOGFOOD-B4-EXEC-EVAL-001 — FAIL_CLOSED / NO ANSWER PHASE`.
This authority does not amend or reuse attempt 001.

## Exact pins

```text
Accepted design:
9b274eda204dac30da51181f2c1de25cf7237010

Accepted harness:
36a53179c9951375450a94c0283e68a9428143fb

Execution checkout:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Execution worktree:
/tmp/relay-b4-cold-start-pinned

Harness blobs:
scripts/b4_readonly_harness.py
f98350ff14dbfb1bf6388de88fff366e67ec1afd

tests/integration/test_b4_readonly_harness.py
6708eb8b1a3fcb8484a227a447ace678c3ec20d0

Operational DB:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Required DB SHA-256:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

Project:
prj_018f47c1-7b2c-7abc-8def-123456789001

Slice:
slc_01a15754-1123-7535-9ded-6a564518e347
```

The operator must run from the pinned worktree and verify exact HEAD plus clean status before DB access.
Any pin mismatch consumes this authority fail-closed.

## Fresh-operator custody

Use one newly started operator session with no prior Relay/ChatGPT conversation, assistant summary, evaluator answer key, expected answers, or B4 evaluator source matrix.

The operator may inspect only registry-resolved current canonical documents, normally discoverable accepted immutable records, repository code/help for behavior, and the accepted read-only harness/output.

Before answer sealing, the operator must not inspect:

- prior Relay/ChatGPT conversation material;
- evaluator notes or expected answers;
- prior B4 answer packets;
- `docs/slices/SLICE_1_10_DOGFOOD_B4_RELAY_DOGFOOD_ACCEPTANCE_DESIGN.md`;
- `docs/reviews/SLICE_1_10_DOGFOOD_B4_DESIGN_EVALUATION_001.md`.

The operator must record that it is a fresh read-only operator and will seal answers before evaluator comparison.

## Preflight

Before Q1-Q10:

1. working directory = `/tmp/relay-b4-cold-start-pinned`;
2. HEAD = `63dd5071295fe2cd78f346b3a401a9030b6bb4c3`;
3. worktree clean;
4. harness blobs equal the pins above;
5. live DB digest equals the authorized digest;
6. record WAL/SHM observations without mutation;
7. invoke the accepted harness exactly once;
8. require `query_only == 1`;
9. require schema version 8;
10. hash and retain raw harness JSON.

Harness command:

```bash
uv run python scripts/b4_readonly_harness.py \
  --database /home/user/projects/relay-local-state/relay-operational.sqlite3 \
  --project-id prj_018f47c1-7b2c-7abc-8def-123456789001 \
  --slice-id slc_01a15754-1123-7535-9ded-6a564518e347
```

No DB migration, write, checkpoint, vacuum, repair, or sidecar cleanup is authorized.

## Frozen questions

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

For each: record answer, source class, exact source locator/record, and any
`NOT DETERMINABLE FROM CURRENT DURABLE STATE`.
Do not score the answers.

## Evidence and sealing

Write exactly:

`/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-operator-evidence-attempt-002.json`

Include declaration, runtime/session/model identity as exposed, preflight, inspected sources, raw harness-output digest, Q1-Q10 answers/sources, and sealed timestamp.

Report the evidence SHA-256 and do not modify the packet afterward.

Then close DB connections, recompute the live DB SHA-256, require equality, record sidecar observations, and STOP for independent evaluation.

## Not authorized

No self-scoring, answer correction after sealing, Human result acceptance, Axis B replay, repository/DB mutation, lifecycle/Slice mutation, Slice 2.2 work, Role Contract implementation, Phase 3, promotion, or third attempt.

## Status

```text
RLY-S110-DOGFOOD-B4-EXEC-AUTH-002 — AUTHORIZED

Attempt 001:
CONSUMED / FAIL_CLOSED

Attempt 002:
AUTHORIZED / NOT YET RUN

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED
```
