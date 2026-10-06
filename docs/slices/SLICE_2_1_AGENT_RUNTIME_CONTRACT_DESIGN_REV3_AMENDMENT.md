# Slice 2.1 — Agent Runtime Contract — Revision 3 Amendment

**Document class:** Lockable design record  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Document revision:** 3 Amendment  
**Design authority:** `RLY-S21-DESIGN-AUTH-001 — AUTHORIZED`  
**Revises:** Revision 1 + Revision 2  
**Responds to:** `RLY-S21-DESIGN-EVAL-002 — REVISE`  
**Implementation authorization:** NOT GRANTED

Revision 3 is normative over Revision 2 where they differ.

---

# 1. F005 resolution

```text
F005 session creation basis can drift from execution basis
RESOLVED
```

Revision 2's standalone `RuntimeSessionRequest` is removed from the stable contract.

---

# 2. S2.1-D34 — Session creation is bound to the exact execution request

The normative protocol becomes:

```python
class AgentRuntime(Protocol):
    async def describe() -> RuntimeDescriptor: ...

    async def create_session(
        request: RuntimeExecutionRequest,
    ) -> RuntimeSessionBinding: ...

    async def open_execution(
        request: RuntimeExecutionRequest,
        binding: RuntimeSessionBinding,
    ) -> RuntimeExecutionHandle: ...

    def events(
        handle: RuntimeExecutionHandle,
    ) -> AsyncIterator[RuntimeEventEnvelope]: ...

    async def cancel(
        request: RuntimeCancelRequest,
    ) -> RuntimeControlAck: ...

    async def inspect(
        handle: RuntimeExecutionHandle,
    ) -> RuntimeExecutionInspection: ...
```

Session creation receives the same exact immutable request that will later be admitted.

It may use only the fields required to create the runtime session, but the full request digest is bound at creation time.

Session creation MUST NOT send the execution prompt/input.

---

# 3. S2.1-D35 — RuntimeSessionBinding

```python
RuntimeSessionBinding(
    execution_id: ExecutionId,
    runtime_session: RuntimeSessionRef,
    request_digest: ContentDigest,
    workspace_id: str,
    created_at: datetime,
)
```

The binding deliberately does not duplicate:

- provider/model;
- source baseline;
- permission profile;
- credential refs;
- prompt/input;
- full workspace description.

Those remain authoritative in the exact digest-bound `RuntimeExecutionRequest`.

`workspace_id` is retained only as a local invariant check against accidental binding to another caller-supplied workspace.

The binding is runtime provenance, not Human authority.

---

# 4. S2.1-D36 — Exact binding validation

Before starting the event pump or admitting execution, `open_execution()` requires:

```text
binding.execution_id
    == request.basis.execution_id

binding.request_digest
    == request.request_digest

binding.workspace_id
    == request.basis.workspace.workspace_id

recomputed_digest(request.basis)
    == request.request_digest

binding.runtime_session.runtime_id
    == request.basis.runtime_selection.runtime_id
```

Any mismatch returns:

```text
RuntimeFailureCategory.REQUEST_CONFLICT
```

and no prompt is admitted.

There is no "best match" behavior.

---

# 5. S2.1-D37 — Session-create retry semantics

Within one live adapter process:

```text
same ExecutionId + same request digest
    + known existing binding
        → return/reuse exact binding

same ExecutionId + different request digest
        → REQUEST_CONFLICT
```

After process restart, Revision 2's `SESSION_BINDING_REQUIRED` rule controls.

The adapter may accept an exact previously persisted `RuntimeSessionBinding` from a future orchestration layer, but it may not discover one heuristically.

---

# 6. S2.1-D38 — OpenCode session creation mapping

For the first OpenCode adapter:

```text
request.basis.workspace.root
    → exact OpenCode session location/directory

request.basis.runtime_selection provider/model
    → session provider/model selection where supported

returned OpenCode session ID
    → RuntimeSessionRef

request.request_digest
    → RuntimeSessionBinding.request_digest
```

The prompt/input is admitted only later by `open_execution()`, after the event pump is ready.

This preserves the Revision 2 live-only event guarantee.

---

# 7. Additional tests

```text
create_session binds exact request digest
create_session does not send prompt
same request retry reuses known binding
same ExecutionId + changed request -> REQUEST_CONFLICT
binding/request digest mismatch -> no event pump / no prompt
binding/workspace mismatch -> no prompt
binding/runtime mismatch -> no prompt
open_execution recomputes digest before admission
session binding contains no duplicated mutable provider/profile/input truth
```

---

# 8. Combined-design result

Revision 3 removes the last separate reconstruction seam between session creation and execution admission.

The authoritative chain is now:

```text
exact RuntimeExecutionBasis
        ↓ deterministic digest
RuntimeExecutionRequest
        ↓
create_session(exact same request)
        ↓
RuntimeSessionBinding(exact digest)
        ↓
pre-start event observation
        ↓ exact binding validation
open_execution(exact same request)
        ↓
runtime execution
```

All Revision 1 and Revision 2 decisions not changed here remain in force.

**Implementation, live sidecar execution, and Relay agent execution remain unauthorized.**
