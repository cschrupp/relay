# Slice 2.4 — I003-R1 Human Decision and Corrective Implementation Authorization 001

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE / AUTHORIZED  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.4 — Execution Workspace Authority  
**Authority ID:** `RLY-S24-I003-R1-REWORK-AUTH-001 — AUTHORIZED`  
**Human decision:** Option 1 accepted — final conformance independently validates protected semantic-operation / physical-access compatibility  
**Subject candidate:** `aa9d71fb749137b60ba8ad620cd43ef7155ad310`  
**Subject evaluation:** `RLY-S24-IMPL-EVAL-002 — ESCALATE`  
**Evaluation record:** `docs/reviews/SLICE_2_4_IMPLEMENTATION_EVALUATION_002.md`  
**Corrective branch:** `implementation/2.4-execution-workspace-authority-rework-001`

## 1. Human decision

The Human Authority accepts the recommended Option 1 for I003-R1.

Relay retains both validation layers:

```text
resolve_workspace_plan()
    prevents semantically/physically incompatible protected bindings
    from being produced by the normal resolver

evaluate_workspace_conformance()
    independently rejects an incompatible protected binding if an
    already-materialized WorkspacePlan reaches final conformance
```

The final evaluator must not rely solely on the resolver having created the plan correctly.

This decision does not reopen the Slice 2.4 schema or architecture.

## 2. Exact corrective requirement

Within final conformance, validate the existing Revision-2 / Revision-3 protected physical-access compatibility rules.

At minimum:

```text
required_operation = MODIFY
physical_access = READ_ONLY
    -> UNSATISFIED

required_operation = MODIFY
physical_access = DENY
    -> UNSATISFIED

required_operation = CREATE
physical_access != READ_WRITE
    -> UNSATISFIED
```

For existing-material operations requiring physical read/evidence access:

```text
READ / EXECUTE / EVALUATE
physical_access = DENY
    -> UNSATISFIED
```

Physical access remains capability only. It never creates semantic authority.

```text
READ_WRITE physical access
    != semantic MODIFY authority
```

`PROPOSE_MUTATION` and `APPROVE_MUTATION` remain governed by their already-accepted semantic rules; this correction must not invent a physical mutation requirement for those operations.

The correction must return a deterministic existing Slice 2.4 failure outcome/reason. Do not introduce a new schema solely for this fix unless the existing reason vocabulary proves structurally insufficient; if that occurs, STOP and report the blocker rather than expanding scope.

## 3. Authorized mutable surface

Only these files may be modified by the corrective implementation:

```text
src/relay_engine/execution_workspace/evaluation.py
tests/unit/test_execution_workspace_evaluation.py
```

Any required change outside those two files is out of scope and requires STOP / separate authority.

No changes are authorized to:

```text
models.py
local_clone.py
provider.py
__init__.py
other tests
documentation
registry
dependencies
CI/workflows
database/lifecycle
WorkPacket
RoleContract
AgentRuntime
runtime/provider/model integration
Phase 3
promotion/closure state
```

## 4. Required regression evidence

The corrective tests must prove at minimum:

```text
manually materialized otherwise-valid WorkspacePlan
+
protected binding required_operation = MODIFY
+
physical_access = READ_ONLY
    -> final conformance UNSATISFIED
```

The implementation should also cover the directly equivalent CREATE / denied-access compatibility cases when they can be expressed within the same invariant without widening architecture.

Existing passing Slice 2.4 behavior must remain unchanged.

## 5. I003-R2 remains unresolved and unauthorized

This authority does not resolve or modify I003-R2.

Specifically, no implementation is authorized for:

```text
observed exact tool exposure
unknown runtime tool identity
actual shell exposure
tool-exposure evidence
shell-exposure evidence
new runtime evidence schemas
AgentRuntime integration
```

I003-R2 remains:

```text
OPEN / BLOCKING / HUMAN DESIGN DECISION PENDING
```

The worker must not infer that authorization of I003-R1 authorizes Path A or Path B for I003-R2.

## 6. Execution discipline

The implementer may internally plan, implement, test, repair, and self-review this bounded correction without stopping at routine internal milestones.

The implementer must STOP if:

- the two-file mutable surface is insufficient;
- the existing evaluator reason vocabulary cannot express the failure without schema change;
- a design amendment becomes necessary;
- I003-R2 would need to be touched;
- another unrelated defect is discovered that requires mutation.

The resulting candidate must remain on:

`implementation/2.4-execution-workspace-authority-rework-001`

and must be submitted for independent SOL re-review.

## 7. Validation

Required validation:

```text
uv sync --frozen --group dev

uv run pytest tests/unit/test_execution_workspace_evaluation.py
uv run pytest tests/unit/test_execution_workspace_models.py
uv run pytest tests/unit/test_execution_workspace_provider_contract.py
uv run pytest tests/integration/test_local_clone_workspace_provider.py
uv run pytest tests/unit/test_execution_workspace_architecture.py

uv run pytest tests/unit/test_repository_contract.py
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Push the exact candidate to the corrective branch, verify the remote SHA, and require exact-head GitHub Actions success before independent re-review.

## 8. Authority boundary

This record authorizes only the I003-R1 corrective implementation above.

It does not grant:

```text
implementation acceptance
Human technical acceptance
Slice 2.4 closure
I003-R2 design clarification
production workspace provisioning
production WorkPacket wiring
AgentRuntime/model execution
Phase 3
real-project agent execution
canonical/main promotion
```

**AUTHORIZED: I003-R1 ONLY. I003-R2 REMAINS STOPPED.**
