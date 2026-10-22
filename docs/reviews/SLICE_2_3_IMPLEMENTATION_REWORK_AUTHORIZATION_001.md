# Relay — Slice 2.3 Implementation Rework Authorization 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-22  
**Project:** Relay  
**Slice:** 2.3 — Context / Work-Packet Contract  
**Authority:** `RLY-S23-IMPL-REWORK-AUTH-001 — AUTHORIZED`

## Human Authority decision

The Human authorizes one bounded corrective implementation pass responding only to:

`RLY-S23-IMPL-EVAL-001 — REWORK`

This authority is limited to defects I001–I003.

## Exact rework basis

```text
Repository:
cschrupp/relay

Original implementation authority:
RLY-S23-IMPL-AUTH-001 — AUTHORIZED

Authorized implementation baseline:
f0996a1909bff8dda76a455d6d88d027b4b736f2

Rejected candidate:
1e978355f1fd4c5981786112f4df3a77ec89802e

Independent implementation evaluation:
RLY-S23-IMPL-EVAL-001 — REWORK

Evaluation record commit:
b9ffc43eb0f67b3b5a808df7b6709befd872cb80

Implementation branch:
implementation/2.3-context-work-packet-contract
```

The corrective implementation must preserve the rejected candidate's already-passing contract behavior except where I001–I003 require correction.

## Authorized mutable files

Exactly:

```text
src/relay_engine/work_packets/evaluation.py
tests/unit/test_work_packet_evaluation.py
```

No other production, test, documentation, configuration, dependency, registry, CI, database, lifecycle, runtime, workspace, or governance file may be modified by the corrective implementation.

If a correction appears to require any other file, STOP and report the exact reason.

## I001 — missing plural fact tri-state

Correct the evaluator so missing expected facts are classified by set/ordered-subsequence semantics, not prefix position.

For each plural fact family:

- authority facts;
- accepted-design facts;
- protected-verification authority facts;
- materialization facts;

the required behavior is:

```text
exact canonical tuple equality
    -> evaluate statuses

supplied subjects are an ordered subsequence of expected subjects
with no unexpected, duplicate, conflicting, or reordered subjects
    -> missing evidence
    -> INDETERMINATE

unexpected subject
duplicate/conflicting subject
noncanonical/reordered subject
wrong exact ref
    -> UNSATISFIED
```

Required regression coverage includes missing first, middle, and last subjects where the family supports multiple expected values.

Do not weaken exact-subject binding.

## I002 — repeated exact material refs

Correct context conformance so two different required context keys may reference the same exact `ContextMaterialRef`.

The evaluator must reason in required-context-key order.

A valid implementation may compare the ordered material-ref sequence derived from:

`packet.required_context_keys -> manifest entries`

against the ordered materialization-fact subject sequence.

Required behavior:

```text
two required keys -> same exact material
two matching positional facts
    -> SATISFIED

one required positional fact missing
    -> INDETERMINATE

wrong material fact
    -> UNSATISFIED
```

Do not introduce a new uniqueness requirement for ContextMaterialRef.

Do not change models.

## I003 — GovernanceProfileRef absent path

Correct GovernanceProfileFact evaluation exactly as accepted:

### Packet contains GovernanceProfileRef

Require:

```text
exact policy ref
exact profile ref
profile_requirement_status == SATISFIED
profile_status == SATISFIED
```

### Packet contains no GovernanceProfileRef

Require:

```text
exact policy ref
evaluated_profile_ref is None
profile_requirement_status == SATISFIED
```

That exact positive requirement fact establishes "profile not required."

For the no-profile path, `profile_status` must not independently force INDETERMINATE/UNSATISFIED for a nonexistent profile.

Unknown/missing `profile_requirement_status` remains INDETERMINATE.

## Preservation requirements

The corrective candidate must preserve:

- F002 recursive canonical identity;
- all fixed canonical JSON / SHA-256 vectors;
- exact WorkPacket / ContextManifest identity;
- WorkPacket != authority;
- Human root authority external;
- exact RoleApplicabilityEvaluation reuse;
- no DB/persistence;
- no material resolver/storage;
- no network/provider/runtime calls;
- no workspace enforcement;
- no lifecycle mutation;
- no Slice 2.4 work;
- no Phase 3 work;
- no production WorkPacket wiring.

## Validation

Run at minimum:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_work_packet_evaluation.py
uv run pytest tests/unit/test_work_packet_models.py
uv run pytest tests/unit/test_work_packet_architecture.py

uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Exact-head GitHub Actions must pass.

## Candidate discipline

Codex must:

- continue from the existing implementation lineage;
- modify exactly the two authorized files;
- create one corrective implementation candidate;
- push only `implementation/2.3-context-work-packet-contract`;
- verify the remote branch exact SHA;
- report focused I001/I002/I003 regression evidence;
- STOP FOR SOL INDEPENDENT IMPLEMENTATION RE-REVIEW.

No self-acceptance.

## Authority boundary

```text
RLY-S23-IMPL-REWORK-AUTH-001 — AUTHORIZED

Corrective implementation:
AUTHORIZED — I001 / I002 / I003 ONLY

Human technical acceptance:
NOT AUTHORIZED BY THIS RECORD

Production wiring:
NOT AUTHORIZED

Operational DB / lifecycle:
NOT AUTHORIZED

Context resolver/storage:
NOT AUTHORIZED

Runtime/provider/model execution:
NOT AUTHORIZED

Workspace enforcement:
NOT AUTHORIZED

Slice 2.4:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED

Canonical/main promotion:
NOT AUTHORIZED
```

**Bounded rework authority != acceptance.**
