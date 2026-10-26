# Relay Slice 3.1 — Dogfood 001 — Execution Preparation Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-26  
**Record:** `RLY-S31-DOGFOOD-001-PREP-AUTH-001 — AUTHORIZED`  
**Canonical Relay base:** `6c0add5611e2e8eab942787e0d6a1afafaa4a2f4`  
**Preparation branch:** `dogfood/3.1-execution-001`

## 1. Human decision

The Human authorizes one bounded **pre-execution preparation** for Relay Slice 3.1 Dogfood 001.

This authority exists because the accepted Slice 2.5 -> Slice 3.1 ordering requires:

```text
requested outcome
  -> Project State Resolver
  -> READY AuthorityCandidate
  -> Human grant of exact AuthorityCandidate digest
  -> authority-linked WorkPacket materialization
  -> exact WorkPacketRef
  -> WorkspacePlan
  -> final admission
  -> runtime execution
```

Therefore an exact WorkPacketRef must not be fabricated before the exact Human grant exists.

This preparation authority permits Codex to establish every exact input required for the later one-shot execution grant **without invoking AgentRuntime or a provider/model**.

## 2. Frozen task

Task record:

`RLY-S31-DOGFOOD-001-TASK-001`

Task artifact:

`docs/reviews/SLICE_3_1_DOGFOOD_001_TASK_SCOPE.md`

Task Git blob:

`c476cb2b941f6ca869911c26b64290425cd56350`

Task SHA-256:

`8290fede3692ee3bfcfd07863080de99b10bacc25f1aa8d5976d026930119940`

Protected oracle source:

`docs/reviews/SLICE_3_1_DOGFOOD_001_PROTECTED_ORACLE.py`

Oracle Git blob:

`c8030c1fcdbce0b02694e25f295e6fb6cf38dc40`

Oracle SHA-256:

`5e7bb4ffcaa07b67be440d722fcd18b64cef638ae78b045f6f9a9f46b123d36d`

The preparation operator must not reinterpret or expand the frozen task.

## 3. Planned governed attempt identity

The exact planned attempt identity is frozen now:

```text
intended_attempt_id:
exec-019a2f5e-7c11-7a31-8a42-2d5e6f708901

ExecutionId:
exec_019a2f5e-7c11-7a31-8a42-2d5e6f708901
```

Preparation must fail if any generated candidate or later runtime basis substitutes another attempt identity.

## 4. Runtime selection reserved for the later execution grant

The requested live route for Dogfood 001 is:

```text
AgentRuntime:
accepted Slice 2.1 OpenCode V2 adapter

accepted adapter implementation:
4f785f08576e465cd0aa278f927fa4b7253e3f49

OpenCode version:
0.0.0-beta-17823

OpenCode binary SHA-256:
e3b94f9545c77b98bd830435dc89ce1942ef425b6c6adf77bc798809473d4fa7

provider:
openrouter

model:
google/gemini-3.8-flash

provider package:
aisdk:@openrouter/ai-sdk-provider

credential reference:
openrouter-api-key
```

This preparation authority does **not** permit starting OpenCode, calling `AgentRuntime.describe()`, querying provider/model endpoints, reading credentials, or making any network call.

The later execution authority will permit exactly one live attempt only if this exact route passes fresh preflight. No fallback provider/model is allowed.

## 5. Planned execution limits

The later WorkPacket/runtime basis must use no broader limits than:

```text
max governed attempts:
1

max runtime sessions for implementation:
1

max duration:
600 seconds

max tool calls:
20

max runtime output:
200000 bytes

maximum changed source files:
1

authorized mutable source:
src/dogfood/execution_order.py

dependency changes:
0

configuration changes:
0

package installation:
prohibited

remote Git writes:
prohibited

push:
prohibited

merge:
prohibited

PR creation:
prohibited

tag/release:
prohibited
```

If the exact accepted models cannot represent a required bound, report the contract gap and STOP rather than weakening the bound.

## 6. Fixture preparation

Preparation may create one disposable local Git repository solely for Dogfood 001 beneath:

`/tmp/relay-s31-dogfood-001/source`

and one later execution workspace beneath:

`/tmp/relay-s31-dogfood-001/workspace`.

The preparation repository must contain exactly:

```text
src/dogfood/__init__.py
src/dogfood/execution_order.py
tests/__init__.py
tests/test_execution_order.py
```

The initial source stub is exactly the stub frozen in `RLY-S31-DOGFOOD-001-TASK-001`.

Both `__init__.py` files are zero bytes.

`tests/test_execution_order.py` must be copied byte-for-byte from the protected-oracle artifact pinned above.

Preparation may initialize and commit this fixture locally. It must report:

- repository identity used for Relay models;
- exact clean source commit SHA;
- Git blob SHA for all four files;
- SHA-256 for all four files;
- clean status.

No remote repository is required and no remote may be configured.

## 7. Protected verification semantics

For the later governed attempt:

```text
tests/test_execution_order.py:
READ + EXECUTE allowed
WRITE prohibited

src/dogfood/execution_order.py:
READ + WRITE allowed

src/dogfood/__init__.py:
READ only

tests/__init__.py:
READ only

.git/**:
no implementation-agent mutation
```

The preparation operator may write the oracle only while creating the frozen initial fixture before the source baseline commit.

After the baseline commit exists, any mutation of the oracle consumes the preparation as invalid and makes the later execution ineligible.

## 8. Project-state request preparation

Feed the frozen task through the accepted Slice 2.5 resolver/compiler using an exact request whose semantic keys are:

```text
request_key:
dogfood-execution-001

outcome_key:
implement-deterministic-execution-order

scope_key:
slice-3-1-dogfood-001

action_key:
governed-coding-execution

intended_attempt_id:
exec-019a2f5e-7c11-7a31-8a42-2d5e6f708901
```

The exact subject must include at least:

- Relay canonical controller base `6c0add5611e2e8eab942787e0d6a1afafaa4a2f4`;
- frozen task SHA-256;
- protected oracle SHA-256;
- exact fixture source commit;
- requested runtime/provider/model identity;
- one-file mutable surface;
- no-push/no-merge boundary.

Use accepted resolver/compiler semantics. Do not special-case Dogfood 001 inside production code.

## 9. Required compilation result

Preparation succeeds only if Slice 2.5 returns:

```text
CompilationStatus:
READY

AuthorityCandidate:
present

candidate intended_attempt_id:
exec-019a2f5e-7c11-7a31-8a42-2d5e6f708901
```

Retain and report:

- exact AuthorityCandidate canonical JSON;
- exact AuthorityCandidate content digest;
- exact source snapshot digest;
- exact role-contract ref;
- all inherited constraints/prohibitions;
- all qualification facts;
- all evidence/deliverable expectations;
- exact consumption requirements.

### Consumable rule

For Dogfood 001, the expected applicable consumable set is:

`()`

If the accepted resolver/compiler establishes any applicable `CONSUMES` requirement, do **not** fabricate or bypass it. Report the exact requirement and STOP for Human decision.

If the set is empty, later grant-time reservation evidence is exactly empty; Slice 3.1 must not fabricate a reservation.

## 10. Proposed WorkPacket inputs

Preparation may assemble the complete **post-grant WorkPacket materialization inputs**, but must not claim a WorkPacket has been authorized or materialized before Human grant.

The proposed packet contract must preserve:

```text
packet_key:
dogfood-execution-001

revision:
1

normalized outcome:
implement resolve_execution_order according to RLY-S31-DOGFOOD-001-TASK-001

authorized mutable path:
src/dogfood/execution_order.py

protected verification:
tests/test_execution_order.py — READ/EXECUTE only

oracle command:
PYTHONPATH=src python -m unittest -v tests.test_execution_order

runtime:
OpenCode V2 / openrouter / google/gemini-3.8-flash

credential ref:
openrouter-api-key

limits:
600 sec / 20 tool calls / 200000 output bytes

hard stops:
scope expansion
protected-oracle mutation
dependency/configuration change
provider/model substitution
credential leakage
unauthorized network/external effect
runtime continuity loss requiring blind retry
budget exhaustion
push/merge/remote mutation
```

## 11. Workspace policy preparation

Prepare an exact WorkspacePolicy/plan input that can enforce:

- exact fixture source commit;
- writable path only `src/dogfood/execution_order.py`;
- oracle readable/executable but non-writable;
- repository metadata not writable by the implementation actor;
- shell only as required to inspect/edit the allowed source and run the exact oracle;
- network denied except the separately mediated AgentRuntime/provider transport;
- no arbitrary external mutating effects;
- credential value never exposed to workspace files or prompt;
- deletion/teardown of the disposable workspace after terminal evidence is captured.

Do not provision a live execution workspace under this preparation authority if provisioning would invoke runtime/provider/network behavior. Static/local fixture preparation is permitted.

## 12. Recovery rule

Preparation is not a model attempt and does not consume the governed execution attempt.

If preparation fails before a Human grant:

- preserve evidence;
- do not invoke AgentRuntime;
- do not silently change task, runtime/provider/model, attempt ID, source baseline, or permissions;
- repair only ordinary preparation mechanics that do not change the governed subject;
- if the governed subject would change, STOP for Human review.

## 13. Explicitly prohibited

This authority does not permit:

- Human grant issuance on behalf of the Human;
- consumable reservation/consumption mutation;
- WorkPacket execution;
- AgentRuntime session creation;
- OpenCode invocation;
- provider/model query or inference;
- credential access;
- network access for the dogfood attempt;
- implementation of `resolve_execution_order`;
- source mutation after fixture baseline creation;
- test/oracle mutation after fixture baseline creation;
- push/merge/PR/tag/release;
- canonical Relay mutation;
- independent evaluation or Human acceptance.

## 14. Required preparation handoff

Return exactly enough evidence for the Human to issue the final one-shot execution authority:

```text
Authority:
RLY-S31-DOGFOOD-001-PREP-AUTH-001 — AUTHORIZED

Relay canonical base:
6c0add5611e2e8eab942787e0d6a1afafaa4a2f4

task record / blob / SHA-256:
<exact>

protected oracle blob / SHA-256:
<exact>

fixture root:
<exact>

fixture repository identity:
<exact>

fixture baseline commit:
<exact>

fixture clean:
PASS/FAIL

fixture file blobs:
<exact>

fixture file SHA-256:
<exact>

ProjectStateRequest:
<exact canonical JSON>

CompilationStatus:
READY/BLOCKED/INDETERMINATE

AuthorityCandidate:
<exact canonical JSON or unavailable>

AuthorityCandidate content digest:
<exact or unavailable>

intended_attempt_id:
<exact>

ExecutionId:
<exact>

consumption requirements:
<exact>

expected reservation set:
EMPTY or <exact refs>

role-contract ref:
<exact>

proposed post-grant WorkPacket materialization inputs:
<exact>

proposed ContextManifest:
<exact>

proposed workspace policy/plan inputs:
<exact>

requested runtime/provider/model:
<exact>

runtime limits:
<exact>

credential values accessed:
NO

AgentRuntime calls:
0

provider/model calls:
0

network calls for governed execution:
0

implementation source changes:
0

protected oracle changed after fixture baseline:
NO

remote Git writes:
0

Status:
STOP FOR HUMAN DOGFOOD EXECUTION GRANT
```

## 15. Final preparation disposition

```text
RLY-S31-DOGFOOD-001-PREP-AUTH-001 — AUTHORIZED

Execution preparation:
AUTHORIZED / BOUNDED

Human execution grant:
NOT YET ISSUED

WorkPacket runtime admission:
NOT AUTHORIZED

Live AgentRuntime/provider/model execution:
NOT AUTHORIZED

Dogfood implementation attempt:
NOT STARTED
```
