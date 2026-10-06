# Slice 2.1 — Agent Runtime Contract — Revision 2 Amendment

**Document class:** Lockable design record  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Document revision:** 2 Amendment  
**Design authority:** `RLY-S21-DESIGN-AUTH-001 — AUTHORIZED`  
**Revises:** Design Revision 1 at `c23f838f6de4a948b38020b2af66851e119e47a8`  
**Responds to:** `RLY-S21-DESIGN-EVAL-001 — REVISE`  
**Implementation authorization:** NOT GRANTED

Revision 2 is normative over Revision 1 where they differ.

---

# 1. Findings resolved

```text
F001 live-only event start/subscription race      RESOLVED
F002 OpenCode event scoping                       RESOLVED
F003 support objects / digest canonicalization    RESOLVED
F004 restart-recovery boundary                    RESOLVED
```

---

# 2. S2.1-D25 — Execution opening establishes observation before admission

Revision 1's caller-visible `start() -> events()` sequencing is replaced.

The stable contract is:

```python
class AgentRuntime(Protocol):
    async def describe() -> RuntimeDescriptor: ...

    async def create_session(
        request: RuntimeSessionRequest,
    ) -> RuntimeSessionRef: ...

    async def open_execution(
        request: RuntimeExecutionRequest,
        session: RuntimeSessionRef,
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

For a live-only event runtime, `open_execution()` MUST internally perform:

```text
validate request/session/capabilities
        ↓
establish runtime event subscription
        ↓
start bounded adapter-owned event pump
        ↓
prove pump ready
        ↓
admit prompt/execution to runtime
        ↓
return RuntimeExecutionHandle
```

If the adapter cannot establish observation before admission:

```text
RuntimeFailureCategory.EVENT_OBSERVATION_UNAVAILABLE
```

is returned and the execution prompt MUST NOT be admitted.

`events(handle)` consumes the already-active adapter buffer; it does not create the underlying OpenCode subscription.

For runtimes that later prove reliable replay semantics, an adapter may use replay instead, but only when it advertises `EVENT_REPLAY` and deterministic tests prove equivalent continuity.

---

# 3. S2.1-D26 — Adapter event pump is bounded and non-blocking

The adapter owns a bounded queue per active Relay `ExecutionId`.

The event pump:

- receives runtime events as quickly as practical;
- filters before normalization;
- assigns Relay observation sequence only to attributable execution events;
- places normalized events in the bounded queue;
- does not perform slow governance/database work in the runtime subscription callback.

If the queue overflows:

```text
continuity = INCOMPLETE
reason = BUFFER_OVERFLOW
```

and one `EVENT_GAP` observation is generated when possible.

Buffer overflow must not be hidden as complete evidence.

Exact queue size is configuration/implementation detail but must be bounded and deterministic in tests.

---

# 4. S2.1-D27 — OpenCode event attribution is exact

The OpenCode server/client event source may contain events outside the current Relay execution.

Before normalizing an event, `OpenCodeRuntime` must establish that the event belongs to the exact bound session.

Attribution inputs may include, depending on the pinned OpenCode API generation:

```text
session ID
location/directory
workspace identity
message/tool-call parent identity
```

Rules:

```text
explicit different session/location
    → ignore as unrelated

exact bound session
    → normalize

server-level marker with no execution subject
    → adapter diagnostic only, not RuntimeEventEnvelope

execution-relevant event whose subject is ambiguous
    → do not attribute;
      mark protocol/continuity incomplete;
      surface EVENT_ATTRIBUTION failure/diagnostic
```

An ambiguous event must never be assigned to a Relay `ExecutionId` merely because only one Relay execution is currently known to the caller.

The sidecar must prove attribution for the pinned OpenCode version.

---

# 5. S2.1-D28 — Runtime support value objects

## RuntimePermissionProfileRef

```python
RuntimePermissionProfileRef(
    profile_id: str,
    content_digest: ContentDigest,
)
```

- `profile_id` nonblank, bounded;
- digest uses existing Relay `ContentDigest`;
- this is provenance/reference only;
- runtime-specific policy material never becomes Relay domain semantics.

## CredentialRef

```python
CredentialRef(
    credential_id: str,
)
```

- nonblank bounded identifier;
- never contains credential material;
- adapters resolve it only through injected external configuration/resolver.

## RuntimeSessionRequest

```python
RuntimeSessionRequest(
    execution_id: ExecutionId,
    workspace: RuntimeWorkspaceAttachment,
    runtime_selection: RuntimeSelection,
    permission_profile_ref: RuntimePermissionProfileRef,
    credential_refs: tuple[CredentialRef, ...],
)
```

The tuple order is canonical and duplicate credential refs are rejected.

Session creation does not admit model execution.

## RuntimeExecutionHandle

```python
RuntimeExecutionHandle(
    execution_id: ExecutionId,
    runtime_session: RuntimeSessionRef,
    runtime_invocation: RuntimeInvocationRef | None,
    request_digest: ContentDigest,
    opened_at: datetime,
)
```

The handle contains no authority decision.

## RuntimeControlAck

```python
RuntimeControlAck(
    execution_id: ExecutionId,
    state: REQUESTED | ALREADY_TERMINAL | NOT_FOUND | DENIED,
    observed_runtime_status: RuntimeStatus | None,
)
```

## RuntimeCancelRequest

```python
RuntimeCancelRequest(
    execution_id: ExecutionId,
    runtime_session: RuntimeSessionRef,
    reason: str,
)
```

Reason is nonblank and is provenance, not runtime permission.

---

# 6. S2.1-D29 — Digest subject is a separate immutable value

Do not compute a request digest over an object containing its own digest.

Define:

```python
RuntimeExecutionBasis(
    schema_version,
    execution_id,
    slice_id,
    source_baseline_id,
    workspace,
    input_payload,
    runtime_selection,
    permission_profile_ref,
    credential_refs,
    required_capabilities,
    limits,
)
```

Then:

```python
RuntimeExecutionRequest(
    basis: RuntimeExecutionBasis,
    request_digest: ContentDigest,
)
```

The request is valid only when the supplied digest exactly matches the deterministic digest of `basis`.

## Canonical serialization

For schema v1:

1. Pydantic strict model -> JSON-compatible data;
2. include `schema_version`;
3. JSON object keys sorted lexically;
4. no insignificant whitespace: separators `(",", ":")`;
5. UTF-8;
6. `ensure_ascii=False`;
7. SHA-256 over exact bytes;
8. encode using Relay `ContentDigest` form: `sha256:<64 lowercase hex>`.

Ordered tuple/list values retain their declared order.

No floating-point field is permitted in the v1 digest basis. Execution limits use integers / explicit units.

The following ARE included because they materially change execution:

- workspace ID/root/repository/source commit;
- input payload digest and text/attachment references as represented by the basis;
- requested runtime/provider/model;
- permission-profile ID/digest;
- credential-reference IDs;
- required capabilities;
- declared limits.

Resolved secret material, runtime-generated session IDs, event IDs, timestamps generated after admission, and actual provider/model identity are NOT in the basis.

A future schema change that alters digest meaning must advance `schema_version`; it may not reinterpret a v1 digest.

---

# 7. S2.1-D30 — Process-lifetime session binding boundary

The base Slice 2.1 adapter may maintain:

```text
ExecutionId
    → RuntimeSessionRef
    → request digest
```

in process memory for conflict detection and event routing.

This does NOT provide restart-safe orchestration.

If the Relay process restarts:

```text
no durable binding supplied
    +
execution state may exist remotely
        ↓
FAIL CLOSED
SESSION_BINDING_REQUIRED
```

The adapter MUST NOT:

- list sessions and guess which one belongs to the execution;
- create a replacement session;
- infer identity from title, directory, newest timestamp, or model.

A later execution-persistence/orchestration slice may supply a previously persisted exact `RuntimeSessionRef` and request digest to reattach/inspect.

Until that layer is accepted:

```text
restart-safe governed agent execution:
NOT PROVIDED
```

Slice 2.1 technical acceptance must not claim otherwise.

---

# 8. S2.1-D31 — OpenCode first profile is non-interactive

The initial OpenCode execution profile does not support runtime permission prompts that require a Human reply during agent execution.

For the first profile:

```text
mandatory allowed operations
    → explicit allow

mandatory forbidden operations
    → explicit deny

would require ask
    → treated as blocked / unsupported for unattended execution
```

`PERMISSION_REQUIRED` may still be normalized as an observation when emitted, but Slice 2.1 does not provide a Human permission-reply control channel.

`PERMISSION_PROMPTS` therefore remains optional and is NOT required for the first accepted profile.

This avoids introducing hidden mid-execution Human Authority semantics.

---

# 9. S2.1-D32 — OpenCode prompt admission

For the pinned first adapter, session creation occurs before event-pump startup because attribution requires an exact session ID.

Then:

```text
create exact session at supplied workspace
        ↓
subscribe global/runtime event source
        ↓
activate exact-session filter
        ↓
mark pump ready
        ↓
admit one prompt/input for that session
```

Only one active prompt/invocation is allowed for the Relay ExecutionId.

The adapter must not use OpenCode steering delivery or mutable model/agent switching during the initial profile after `RuntimeExecutionBasis` is fixed.

Any runtime API that would alter provider/model/agent after execution basis creation is outside initial Slice 2.1 semantics.

---

# 10. S2.1-D33 — Mid-stream failure and reconnect

If the live event transport fails after execution admission:

```text
continuity = INCOMPLETE
EVENT_GAP(reason=STREAM_DISCONNECTED)
```

The adapter may re-subscribe for subsequent live events, but MUST NOT claim replayed continuity unless `EVENT_REPLAY` was advertised and proven.

The adapter then uses `inspect()` to determine current/terminal runtime state.

A transport disconnect does not automatically create a second prompt or session.

---

# 11. Additional deterministic tests

Revision 2 adds mandatory tests:

```text
event pump ready before prompt-admission call
prompt is not sent when event observation cannot be established
events emitted immediately on prompt admission are retained
unrelated session event is ignored
server-level unscoped marker is not attributed
ambiguous execution event marks continuity incomplete
bounded queue overflow marks EVENT_GAP
request digest matches exact canonical v1 serialization
request_digest field is not recursively included
basis field change changes digest
same basis produces identical digest
duplicate CredentialRef rejected
process restart without supplied binding -> SESSION_BINDING_REQUIRED
adapter does not discover/guess a replacement session
ASK-style permission requirement is not silently auto-approved
provider/model/agent switch after basis lock is rejected by initial profile
```

---

# 12. Updated failure vocabulary

Revision 2 adds:

```text
EVENT_OBSERVATION_UNAVAILABLE
EVENT_ATTRIBUTION
SESSION_BINDING_REQUIRED
```

to Revision 1's failure categories.

---

# 13. Updated initial implementation boundary

No additional production modules beyond Revision 1 are required.

The OpenCode adapter may use one small internal event-pump helper inside `opencode.py` or a private module only if clarity requires it.

No generic event bus is authorized.

No persistence is authorized.

No Human runtime-permission UI is authorized.

---

# 14. Result after Revision 2

The combined design now provides:

- exact pre-start event observation for live-only runtimes;
- session-scoped event provenance;
- precise support-value contracts;
- deterministic request digest identity;
- honest process-lifetime recovery semantics;
- non-interactive first permission profile;
- no hidden authority expansion.

All other Revision 1 decisions remain unchanged.

**Revision 2 remains design only. Implementation and live sidecar execution remain unauthorized.**
