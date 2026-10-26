# Relay — Slice 3.1 Coding Agent Execution — Independent Implementation Evaluation 001

**Document class:** Immutable independent implementation evaluation record  
**Status:** IMMUTABLE / REWORK — NARROW  
**Date:** 2026-10-25  
**Project:** Relay  
**Phase:** 3 — First Governed Autonomous Engineering Loop  
**Slice:** 3.1 — Coding Agent Execution  
**Evaluation ID:** `RLY-S31-IMPL-EVAL-001 — REWORK / NARROW`  
**Evaluator:** Independent Implementation Reviewer — GPT-5.6 Sol  
**Exact implementation subject:** `7aadaf5b8c8e9ff856f4fb8275184b22f363f029`  
**Authorized parent:** `7c59e0df114ff85afc4c8ea3c041b410da62fe1c`  
**Implementation authority:** `RLY-S31-IMPL-AUTH-001 — AUTHORIZED`  
**Accepted design:** `a28a9b88ddd85cd1a32932b30c4e0e668f23b557`  
**Exact-head CI:** `40260415262 — SUCCESS`

## 1. Decision

```text
RLY-S31-IMPL-EVAL-001 — REWORK / NARROW
```

The implementation is strong and substantially satisfies the accepted Slice 3.1 design and bounded implementation authority.

One blocking implementation gap remains: accepted scenario **A17** is not represented or proven.

No broad redesign, predecessor-contract change, runtime/provider change, or new Human implementation authority is required. The missing behavior is already inside `RLY-S31-IMPL-AUTH-001`.

## 2. Exact lineage and scope

PASS.

The candidate:

`7aadaf5b8c8e9ff856f4fb8275184b22f363f029`

is exactly one commit ahead of authorized parent:

`7c59e0df114ff85afc4c8ea3c041b410da62fe1c`.

The implementation increment changes exactly eight new files:

```text
src/relay_engine/coding_execution/__init__.py
src/relay_engine/coding_execution/models.py
src/relay_engine/coding_execution/evaluation.py
src/relay_engine/coding_execution/coordinator.py
tests/unit/test_coding_execution_models.py
tests/unit/test_coding_execution_evaluation.py
tests/unit/test_coding_execution_coordinator.py
tests/unit/test_coding_execution_scenarios.py
```

No predecessor Slice implementation file changed.

Canonical `main` remains unchanged.

The remote implementation branch points exactly to the evaluated candidate.

## 3. Validation

PASS.

Exact-head GitHub Actions run:

`40260415262 — SUCCESS`

for exact subject:

`7aadaf5b8c8e9ff856f4fb8275184b22f363f029`.

Observed CI quality steps all succeeded:

- environment synchronization;
- Ruff format;
- Ruff lint;
- Pyright;
- tests;
- build.

Executor-reported local validation additionally establishes:

```text
focused coding-execution tests:
42 passed

full pytest suite:
1,186 passed

uv build:
PASS

git diff --check:
PASS

working tree:
CLEAN
```

No real AgentRuntime/OpenCode/provider/model/network/credential execution occurred.

## 4. Architecture review

PASS except for Finding I31-F001.

The implementation correctly provides a small Slice 3.1 composition package rather than a second governance architecture.

Verified strengths include:

- exact intended-attempt / `ExecutionId` reversible mapping;
- read-only Human-grant and reservation evidence;
- no reservation creation/release/consumption mutation;
- exact candidate/grant/attempt binding;
- WorkPacket materialization/conformance before exact WorkPacketRef;
- WorkspacePlan resolution only after exact WorkPacketRef exists;
- workspace preflight/conformance before runtime prompt admission;
- final candidate/grant/reservation/freshness revalidation;
- injected `AgentRuntime` boundary;
- exact runtime session/handle binding;
- runtime/provider/model identity checks;
- effective permission/tool/shell evidence checks;
- runtime event continuity checks;
- fail-closed ambiguous/unknown evidence handling;
- protected-verification mutation enforcement through accepted workspace semantics;
- dirty workspace and local commit evidence;
- budget/usage handling;
- `ProposedWorkObservation` as evidence rather than terminal status;
- existing Slice 2.2 successor disposition reuse;
- immutable terminal result/evaluator handoff;
- explicit prevention of implementation self-acceptance;
- contract-gap evidence rather than predecessor mutation.

No evidence supports reopening Slices 2.1–2.5.

## 5. Finding I31-F001 — A17 evaluator-REWORK corrective lineage is missing

**Severity:** blocking but narrow  
**Disposition:** REWORK REQUIRED

The accepted Slice 3.1 design requires:

```text
An evaluator REWORK creates a corrective subject linked to:
- exact reviewed candidate;
- exact evaluation record;
- finding IDs;
- authority;
- permitted files or behaviors.

The same Human authority may cover correction only when the correction
remains inside the exact accepted authority/scope.

A genuinely new governed runtime attempt gets a new exact attempt identity
and ExecutionId and the applicable fresh grant/reservation decision.
```

The implementation authority also makes A17 mandatory:

```text
A17:
in-scope correction remains bounded;
new runtime attempt has new exact attempt identity where applicable.
```

and explicitly requires deterministic A01–A22 coverage.

The current implementation contains:

- immutable terminal result;
- immutable evaluator-handoff digest;
- implementer self-acceptance prohibition.

It does **not** contain any typed representation or deterministic evaluation for:

- an evaluator `REWORK` judgment;
- the exact evaluation-record identity/digest;
- finding IDs;
- corrective permitted-file / permitted-behavior scope;
- linkage from reviewed terminal candidate to corrective subject;
- determination that corrective work remains inside the original authority;
- distinction between a correction that may reuse the same authority scope and one requiring new Human authority;
- enforcement that a genuinely new runtime attempt receives a new intended-attempt / `ExecutionId` pair and applicable new grant/reservation.

Repository-wide inspection of the new Slice 3.1 package and focused tests found no `REWORK`, finding-ID, corrective-subject, reviewed-candidate, or equivalent implementation path.

Therefore A17 is not merely under-tested; its required orchestration contract is absent.

## 6. Why the existing evaluator handoff is insufficient

The current `TerminalExecutionResult` correctly prevents self-acceptance and produces a digest-bound evaluator handoff.

That satisfies the **outbound** evaluator handoff portion of A16.

A17 is the **return path after independent evaluation**.

An immutable handoff alone cannot establish whether a later corrective execution:

- is actually responding to the exact reviewed candidate;
- is bound to exact evaluator findings;
- remains within original authority;
- attempts work outside permitted correction scope;
- is a continuation versus a genuinely new governed attempt.

Without an explicit bound corrective subject/evaluation input, the coordinator would have to infer those facts from prose or caller convention, which the accepted design prohibits.

## 7. Required narrow correction

Remain inside:

```text
src/relay_engine/coding_execution/**
tests/unit/test_coding_execution_*.py
```

No predecessor changes are justified.

Add the minimum immutable/evaluation semantics necessary to represent and validate A17.

A minimal solution may use concepts equivalent to:

### `EvaluatorReworkBinding`

Bind at least:

- exact reviewed `TerminalExecutionResult` / evaluator handoff digest;
- exact independent evaluation record identity/digest;
- evaluator disposition exactly `REWORK`;
- canonical non-empty finding IDs;
- exact corrective authority reference/basis;
- exact permitted corrective files and/or behavior keys;
- whether the evaluator finding is asserted to remain inside the original authority boundary.

This object is evidence/binding only. It must not issue Human authority.

### `CorrectiveExecutionSubject` or equivalent

Bind at least:

- exact prior execution/candidate/handoff;
- exact `EvaluatorReworkBinding`;
- exact original authority/candidate basis;
- exact corrective scope;
- exact new intended-attempt identity / `ExecutionId` when a new runtime attempt is required;
- exact grant/reservation binding for that new attempt as applicable.

Do not create a new lifecycle engine.

### Deterministic evaluation

Provide a pure check that distinguishes at least:

```text
IN_SCOPE_REWORK
NEW_AUTHORITY_REQUIRED
INDETERMINATE
```

or an equivalent non-lifecycle vocabulary.

Known scope excess -> new authority required / stop.

Missing or conflicting evaluator finding/scope provenance -> indeterminate / stop.

An evaluator `REWORK` judgment by itself must never create execution authority.

## 8. Mandatory corrective tests

At minimum add deterministic tests proving:

1. exact reviewed terminal candidate + exact REWORK record + exact finding IDs + bounded corrective scope -> accepted as an in-scope corrective basis;
2. mismatched reviewed candidate/handoff digest -> fail closed;
3. evaluation record without `REWORK` disposition -> cannot create corrective basis;
4. missing/duplicate/conflicting finding IDs -> fail closed;
5. corrective file/behavior outside evaluator-permitted scope -> requires new authority / stop;
6. correction outside original WorkPacket/Human authority -> requires new authority / stop;
7. new runtime corrective attempt cannot reuse the prior intended-attempt / `ExecutionId`;
8. new runtime corrective attempt requires the applicable fresh grant/reservation binding;
9. evaluator REWORK alone cannot create a WorkPacket, grant, reservation, runtime session, or runtime admission;
10. exact prior candidate, evaluation, finding IDs, corrective subject, and new terminal candidate remain linkable in immutable evidence.

Map these tests explicitly to A17.

A18 should continue to prove the scope/new-authority stop boundary.

## 9. Final-admission ordering review

PASS / no additional finding.

The frozen scope describes:

```text
derive ExecutionSubject
-> final freshness/reservation/identity checks
-> ADMIT
-> runtime session/prompt
```

The implementation computes its pure final `AdmissionEvidence` immediately before constructing the immutable `ExecutionSubject`, then constructs/validates that subject before any call to:

- `runtime.create_session()`;
- `runtime.open_execution()`.

This does not create an authority bypass: all steps before runtime session creation are pure/read-only or workspace preparation, and subject validation can still fail before runtime admission.

No separate blocking finding is warranted here.

## 10. Reporting correction

The completion report cites:

`RLY-S31-CODEX-SCOPE-001`.

No durable repository record with that identifier exists on the evaluated lineage.

The governing implementation records are:

- `RLY-S31-IMPL-AUTH-001 — AUTHORIZED`;
- `RLY-S31-IMPL-HANDOFF-001`.

This is a completion-report naming issue, not a code defect and not a second blocker. The corrective report should use the durable record IDs.

## 11. Existing authority is sufficient for correction

The required A17 behavior was explicitly included in the existing accepted design and implementation authority.

Therefore:

```text
new Human implementation authority:
NOT REQUIRED

predecessor contract reopening:
NOT REQUIRED

broad Slice 3.1 redesign:
NOT REQUIRED

bounded corrective implementation:
AUTHORIZED under RLY-S31-IMPL-AUTH-001
```

Codex may perform this narrow correction on the existing implementation branch without another Human gate.

## 12. Final disposition

```text
Exact implementation subject:
7aadaf5b8c8e9ff856f4fb8275184b22f363f029

Independent implementation evaluation:
RLY-S31-IMPL-EVAL-001 — REWORK / NARROW

Lineage:
PASS

Authorized file scope:
PASS

Predecessor freeze:
PASS

Core admission/orchestration:
PASS

Grant/reservation semantics:
PASS

WorkPacket -> WorkspacePlan ordering:
PASS

Runtime/workspace evidence:
PASS

A01-A16:
substantively covered

A17:
REWORK REQUIRED

A18-A22:
substantively covered

CI:
PASS

Implementation acceptance:
NOT GRANTED

Execution:
NOT AUTHORIZED

Canonical promotion:
NOT AUTHORIZED
```

**REWORK — add the minimum exact evaluator-REWORK/corrective-subject lineage required by A17, prove it deterministically, rerun the focused/full suite and CI, then return one exact corrective implementation candidate for independent re-review.**
