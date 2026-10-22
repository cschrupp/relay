# Slice 1.10 Dogfood B4 — Cold-Start Dogfood Execution Authorization 001

**Document class:** Immutable Human execution authority  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B4 — Relay Dogfood Acceptance  
**Record:** `RLY-S110-DOGFOOD-B4-EXEC-AUTH-001`  
**Decision:** `AUTHORIZED`  
**Attempts authorized:** exactly one fresh-operator attempt

## Human Authority decision

The Human explicitly authorizes one exact B4 cold-start dogfood execution under the Human-accepted B4 design and Human-accepted read-only harness.

This authority permits the operator session and sealed answer collection only. It does not authorize self-scoring, Human acceptance, Slice 2.2 design, or any mutation of the real operational database.

## Exact execution basis

```text
B4 design:
9b274eda204dac30da51181f2c1de25cf7237010
RLY-S110-DOGFOOD-B4-DESIGN-EVAL-001 — ACCEPT
RLY-S110-DOGFOOD-B4-DESIGN-ACCEPT-001 — ACCEPTED

Accepted read-only harness:
36a53179c9951375450a94c0283e68a9428143fb
RLY-S110-DOGFOOD-B4-HARNESS-IMPL-EVAL-001 — ACCEPT
RLY-S110-DOGFOOD-B4-HARNESS-IMPL-ACCEPT-001 — ACCEPTED

Execution checkout:
63dd5071295fe2cd78f346b3a401a9030b6bb4c3

Operational DB:
/home/user/projects/relay-local-state/relay-operational.sqlite3

Required pre-run DB SHA-256:
6bcef5dc6383a75772948fd82bdbc881b05b169f22fb107720f2a3dc53a14a5e

Project:
prj_018f47c1-7b2c-7abc-8def-123456789001

Current Slice:
slc_01a15754-1123-7535-9ded-6a564518e347

Harness command:
uv run python scripts/b4_readonly_harness.py \
  --database /home/user/projects/relay-local-state/relay-operational.sqlite3 \
  --project-id prj_018f47c1-7b2c-7abc-8def-123456789001 \
  --slice-id slc_01a15754-1123-7535-9ded-6a564518e347
```

If the checkout, cleanliness, harness bytes, DB path, or DB pre-run digest differs from these pins, STOP before the answer phase. This authority is not transferable to a corrected or second attempt.

## Externally administered B4 roles

B4 role assignment is externally administered by Human Authority and test custody. It is not evidence that Relay implements Role Contracts or agent-role binding.

### Fresh operator

The operator must be a newly started Codex session/run that:

- did not participate in the prior Relay/ChatGPT planning conversation;
- is not given any ChatGPT transcript, assistant summary, evaluator answer key, or prior B4 expected answers;
- receives only this run card, the pinned checkout/database, and the allowed information surfaces below;
- records its runtime/session identity and, where exposed by the runtime, actual model identity;
- performs read-only inspection and answers Q1–Q10;
- seals its answers before any independent evaluator comparison;
- does not score its own answers.

The operator is not an architect, implementer, or authority for this run. Its B4 function is read-only orientation only.

### Independent evaluator

Independent scoring occurs only after the operator answer packet is sealed.

The evaluator may use the Human-accepted B4 design/source matrix and the full allowed authoritative state. The evaluator must not coach or correct the operator before sealing.

### Human Authority

The Human alone may accept or reject the independently evaluated B4 result.

## Operator cold-start declaration

Before inspecting Relay state, the fresh operator must include this declaration in its evidence packet:

```text
I am executing B4 as a fresh read-only operator. I was not provided the prior
Relay/ChatGPT conversation, assistant summaries, evaluator answer key, expected
answers, or B4 evaluator source matrix. I will use only the allowed information
surfaces under RLY-S110-DOGFOOD-B4-EXEC-AUTH-001 and will seal my answers
before any evaluator comparison.
```

If that declaration is false or cannot be made, the run is INVALID and must stop.

## Allowed operator information surfaces

The operator may use:

1. the exact pinned checkout at `63dd5071295fe2cd78f346b3a401a9030b6bb4c3`;
2. `.relay/registry.json`;
3. registry-resolved current canonical documents;
4. accepted immutable governance records discovered normally through the registry or references from allowed canonical/accepted records;
5. repository code and CLI help solely to understand product/read-model behavior;
6. the accepted read-only harness;
7. harness-produced `project_board` and `slice_detail` JSON from the pinned live DB;
8. exact external evidence files only when an allowed pinned repository record or this authority names their path and digest.

The operator may use ordinary repository search to follow allowed references.

## Prohibited operator information surfaces

During the answer phase the operator must not inspect or receive:

- this conversation or any prior ChatGPT/Codex conversation reconstructing Relay history;
- assistant-generated project summaries;
- evaluator notes or expected answers;
- the B4 evaluator source matrix or scoring analysis;
- `docs/slices/SLICE_1_10_DOGFOOD_B4_RELAY_DOGFOOD_ACCEPTANCE_DESIGN.md`;
- `docs/reviews/SLICE_1_10_DOGFOOD_B4_DESIGN_EVALUATION_001.md`;
- any external B4 answer key, draft answer sheet, or prior B4 operator answer packet.

This execution authority may be read only for run pins, safety limits, exact questions, and custody instructions. It is not an answer source.

If a prohibited source is inspected before answer sealing, the run is INVALID. Do not continue and do not retry under this authority.

## Read-only preflight

Before Q1–Q10:

1. confirm exact checkout HEAD `63dd5071295fe2cd78f346b3a401a9030b6bb4c3`;
2. confirm clean worktree;
3. confirm the harness files match accepted harness candidate `36a53179c9951375450a94c0283e68a9428143fb`;
4. compute the operational DB SHA-256 and require the exact authorized digest;
5. inventory existing `-wal` / `-shm` sidecars without changing them;
6. invoke the accepted harness exactly once for the live inspection;
7. require `query_only == 1` and schema version 8;
8. retain/hash the raw harness JSON output;
9. do not checkpoint, delete, normalize, migrate, vacuum, or modify the DB or sidecars.

If any mandatory preflight condition fails, STOP and return a fail-closed evidence packet. Do not collect Q1–Q10 answers.

## Frozen operator questions

After successful preflight, answer these questions verbatim and in this exact order:

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

For every answer, record:

- the verbatim answer;
- source class;
- exact source locator(s);
- relevant field/record identity;
- whether any part is `NOT DETERMINABLE FROM CURRENT DURABLE STATE`.

Do not assign PASS / FAIL / INDETERMINATE. That belongs to independent evaluation.

## Answer sealing

After Q10:

1. write one immutable-style external operator evidence packet to:

`/home/user/projects/relay-local-state/adoption-evidence/b4-cold-start-operator-evidence-attempt-001.json`

2. include the cold-start declaration, session/runtime identity, model identity if exposed, preflight facts, command/surface transcript, inspected-file/record inventory, raw harness-output digest, Q1–Q10 answers and sources, and answer-sealed timestamp;
3. compute and report the operator evidence SHA-256;
4. do not modify the packet after reporting its digest;
5. do not inspect the B4 evaluator design/matrix after sealing;
6. STOP for independent result evaluation.

No self-correction after sealing is permitted under this attempt.

## Post-run read-only proof

After sealing answers:

- close all DB connections;
- compute the live DB SHA-256 again;
- require equality with the pre-run digest;
- record sidecar inventory/hashes;
- do not remove/checkpoint sidecars.

If the DB digest differs, the run is INVALID and must not be scored as PASS.

## Explicitly not authorized

- B4 self-evaluation or scoring;
- operator answer correction after sealing;
- B4 Human result acceptance;
- Axis B B0-F/B1/B2 replay;
- repository or live DB mutation as part of the operator run;
- lifecycle transition;
- Slice definition change;
- new Slice creation;
- Slice 2.2 design or implementation;
- Role Contract implementation;
- OpenCode/AgentRuntime project execution;
- Phase 3;
- promotion;
- a second B4 attempt.

## Required handoff

Return:

```text
Authority
Execution checkout SHA
Fresh operator/session identity
Runtime and model identity (model if exposed)
Cold-start declaration: PASS/FAIL

Preflight: PASS/FAIL
Worktree clean: yes/no
Harness identity: PASS/FAIL
DB SHA before
query_only
schema version
Raw harness output SHA-256
Allowed sources inspected
Prohibited sources inspected: NONE or exact list

Q1 answer + sources
Q2 answer + sources
Q3 answer + sources
Q4 answer + sources
Q5 answer + sources
Q6 answer + sources
Q7 answer + sources
Q8 answer + sources
Q9 answer + sources
Q10 answer + sources

Operator evidence path
Operator evidence SHA-256
Answer sealed timestamp

DB SHA after
DB unchanged: yes/no
Sidecar observations

B4 scoring performed: NO
B4 execution attempt count: 1
Slice 2.2 work performed: NO

Status:
STOP FOR INDEPENDENT B4 RESULT EVALUATION
```

## Authority status

```text
RLY-S110-DOGFOOD-B4-EXEC-AUTH-001 — AUTHORIZED

ONE FRESH-OPERATOR B4 ATTEMPT:
AUTHORIZED

B4 INDEPENDENT RESULT EVALUATION:
PENDING SEALED OPERATOR EVIDENCE

SLICE 2.2 DESIGN:
NOT OPEN / NOT AUTHORIZED
```
