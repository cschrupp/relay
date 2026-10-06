# Slice 2.1 — Agent Runtime Contract — Design Revision 1

**Document class:** Lockable design record  
**Status:** PROPOSED FOR INDEPENDENT DESIGN REVIEW  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Document revision:** 1  
**Opening authority:** `RLY-S21-OPEN-001`  
**Design authority:** `RLY-S21-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact design subject baseline:** `2a02da12954a2ed54afdf088576e55dc19283a78`  
**Design-authority commit:** `ff72cd71cc6d2ff972b30345f02cf9d575296fcd`  
**Implementation authorization:** NOT GRANTED  
**Sidecar/runtime experiment authorization:** NOT GRANTED

---

# 1. Objective

Define the minimum Relay-owned contract through which a future governed execution may use an external coding-agent runtime without making that runtime authoritative for project state, lifecycle, Human Authority, evaluation, or acceptance.

The controlling boundary is:

```text
Relay deterministic governance
        ↓
authorized execution request
        ↓
AgentRuntime
        ↓
runtime adapter
        ↓
external coding-agent harness
        ↓
provider/model
```

The runtime may execute an already-authorized role. It may never decide that the role is authorized.

The Slice 2.1 design target is contract-level interoperability and provenance, not autonomous software development.

---

# 2. Existing accepted substrate

Slice 2.1 reuses the accepted Phase 1 foundation:

- immutable strict Pydantic domain values;
- exact repository / Baseline identity;
- typed `ExecutionId = exec_<uuid7>`;
- deterministic lifecycle and handover gates;
- durable Human Authority evidence;
- manual evaluator / Human technical-acceptance separation;
- accepted-result promotion;
- fail-closed stale-basis semantics;
- canonical documentation governance;
- repository quality profile.

No second lifecycle, authorization system, evaluation system, or accepted-result mechanism is introduced.

---

# 3. External evidence affecting the design

The current OpenCode documentation establishes several constraints that must not leak into Relay semantics:

1. OpenCode's documented client/SDK surface is JavaScript/TypeScript-oriented while the server exposes an HTTP API.
2. OpenCode sessions can be created for an explicit location/workspace.
3. the client exposes a live event subscription;
4. current event subscriptions are live-only, with no replay or automatic reconnection;
5. V1 and V2 permission configuration use different names and structure;
6. current V2 permission rules can allow, ask, or deny actions/resources;
7. session abort and session-diff/result-inspection surfaces exist;
8. local service/process management is a separate client concern.

Therefore the first Relay adapter is designed around an explicit HTTP/API-generation boundary rather than importing OpenCode JS/TS SDK object types into Relay.

The exact OpenCode transport/version remains subject to separately authorized sidecar evidence before live adapter acceptance.

---

# 4. S2.1-D01 — AgentRuntime is an execution boundary, not an authority boundary

`AgentRuntime` is called only after an upstream Relay service has validated the current exact Human/governance authority.

The runtime contract MUST NOT contain operations equivalent to:

```text
authorize_work()
approve_result()
advance_lifecycle()
accept_result()
promote_baseline()
decide_gate()
```

The runtime sees enough immutable provenance to execute and report what it did, but it does not own the truth of why execution was allowed.

Mandatory invariant:

```text
runtime permission
    !=
Relay authorization
```

---

# 5. S2.1-D02 — Reuse Relay ExecutionId

Relay's existing `ExecutionId` is the authoritative identity of one governed runtime execution attempt.

No competing Relay execution identifier is introduced.

Runtime-native identities are represented as opaque provenance:

```text
RuntimeSessionRef
    runtime_id
    session_id

RuntimeInvocationRef
    runtime_id
    session_id
    invocation_id | None
```

Rules:

- runtime IDs are strings validated for nonblank bounded length;
- they are namespaced by `runtime_id`;
- they never replace `ExecutionId`;
- they never become lifecycle/gate keys;
- an evaluator execution MUST use a distinct Relay `ExecutionId` and a distinct runtime session from the implementation execution;
- resume may continue only the same Relay `ExecutionId`;
- rework or a new governed attempt receives a new Relay `ExecutionId`.

---

# 6. S2.1-D03 — Runtime descriptor and capability discovery

Every adapter exposes a deterministic descriptor before execution:

```python
RuntimeDescriptor(
    runtime_id,
    adapter_version,
    runtime_version,
    api_generation,
    capabilities,
)
```

`runtime_id` is a Relay configuration key such as `opencode`, not a provider/model name.

Core capabilities:

```text
SESSION_CREATE
EXECUTE
EVENT_STREAM
CANCEL
RESULT_INSPECTION
```

These are mandatory for a runtime to satisfy the initial Relay AgentRuntime profile.

Optional capabilities:

```text
RESUME
STEER
PERMISSION_PROMPTS
DIFF_INSPECTION
USAGE_REPORTING
ACTUAL_PROVIDER_IDENTITY
ACTUAL_MODEL_IDENTITY
EVENT_REPLAY
NATIVE_WORKTREE
```

A caller supplies a required-capability set. Missing mandatory capability fails before session creation.

No adapter may silently emulate an unsupported capability in a way that changes semantics.

---

# 7. S2.1-D04 — Exact runtime/API version compatibility is explicit

Adapter compatibility is fail-closed.

An adapter declares:

```text
runtime_id
adapter_version
supported API generation(s)
supported runtime version range/predicate
```

At connection/capability discovery time, the adapter records the actual runtime/API version when exposed.

If the observed version is outside the accepted compatibility range:

```text
RuntimeFailureCategory.UNSUPPORTED_RUNTIME_VERSION
```

is returned before execution.

No silent V1↔V2 permission/event translation is permitted unless explicitly implemented and tested inside the adapter.

---

# 8. S2.1-D05 — Immutable execution request

The Relay-owned request is conceptually:

```python
RuntimeExecutionRequest(
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
    request_digest,
)
```

The request is frozen and extra-forbid, following existing Relay model conventions.

It contains no mutable lifecycle authority.

## workspace

```python
RuntimeWorkspaceAttachment(
    workspace_id,
    root,
    repository,
    source_commit,
)
```

The workspace is supplied by Relay/the future workspace layer.

The runtime MUST NOT:

- choose a different repository;
- replace the source commit;
- create a broader workspace on its own;
- add external directories merely because the harness supports them.

## input payload

Slice 2.1 does not own Context Builder or Work Packet semantics.

The runtime consumes a finalized adapter-facing payload:

```python
RuntimeInputPayload(
    text,
    payload_digest,
    attachment_refs=(),
)
```

A future Work Packet service constructs this payload. The runtime may not reinterpret it as permission to alter scope.

## permission_profile_ref

Slice 2.1 deliberately does not invent a generic cross-runtime permission language.

The request carries an immutable Relay permission-profile reference/digest for provenance. Runtime-specific materialization remains inside the adapter/integration layer and must be traceable to that ref.

## credential_refs

Only opaque external credential references cross the boundary.

Secret values must not appear in:

- repository files;
- Relay execution request serialization intended for durable project records;
- events;
- error messages;
- result summaries.

---

# 9. S2.1-D06 — Request digest and conflict semantics

`request_digest` is a SHA-256 digest over the canonical serialized execution request excluding fields that are intentionally runtime-generated.

It binds:

- execution identity;
- Slice/baseline identity;
- workspace identity/source commit;
- finalized input payload digest;
- runtime/provider/model request;
- permission-profile ref/digest;
- credential-ref identifiers;
- required capabilities;
- declared execution limits.

Retry rule:

```text
same ExecutionId + same request_digest
    = same logical execution request

same ExecutionId + different request_digest
    = REQUEST_CONFLICT / fail closed
```

A transport retry does not create new authority.

If Relay loses transport certainty after start, it MUST inspect the existing runtime/session binding before attempting another start. It must not blindly create a second session.

Durable mapping of ExecutionId to runtime session belongs to the future execution-orchestration/persistence slice; Slice 2.1 defines the contract and conflict rule only.

---

# 10. S2.1-D07 — Runtime/provider/model selection is provenance, not workflow semantics

```python
RuntimeSelection(
    runtime_id,
    requested_provider_id,
    requested_model_id,
)
```

Provider and model identifiers remain opaque strings.

The request records requested identity.

The result records actual identity when exposed:

```python
RuntimeProvenance(
    runtime_id,
    adapter_version,
    runtime_version,
    api_generation,
    requested_provider_id,
    requested_model_id,
    actual_provider_id,
    actual_model_id,
    identity_completeness,
)
```

`identity_completeness`:

```text
FULL
PARTIAL
UNKNOWN
```

If the runtime does not expose exact actual model/runtime variants, Relay records that fact. It must not fabricate exact identity.

Whether FULL identity is mandatory is an execution-profile decision, not an AgentRuntime default.

Changing provider/model does not change Relay lifecycle semantics.

---

# 11. S2.1-D08 — Session creation and execution start are separate

Conceptual protocol:

```python
class AgentRuntime(Protocol):
    async def describe() -> RuntimeDescriptor: ...
    async def create_session(
        request: RuntimeSessionRequest,
    ) -> RuntimeSessionRef: ...
    async def start(
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

Optional protocol extensions:

```python
class ResumableAgentRuntime(Protocol):
    async def resume(...) -> RuntimeExecutionHandle: ...

class SteerableAgentRuntime(Protocol):
    async def steer(...) -> RuntimeControlAck: ...
```

Optional behavior is capability-gated rather than every adapter returning `NotImplemented`.

This keeps the minimum contract honest.

---

# 12. S2.1-D09 — One active invocation per Relay execution

For one `ExecutionId`:

```text
CREATED
  ↓
RUNNING
  ↓
SUCCEEDED | FAILED | BLOCKED | CANCELLED
```

This is runtime observation only; it is NOT a second Relay lifecycle.

A runtime adapter must reject a second simultaneous start for the same execution/session binding.

The runtime-observation state may be reconstructed from inspection. It never authorizes a Relay lifecycle transition.

---

# 13. S2.1-D10 — Normalized events are observational

Normalized event types:

```text
EXECUTION_STARTED
PROGRESS
TOOL_REQUESTED
TOOL_COMPLETED
PERMISSION_REQUIRED
EXECUTION_BLOCKED
EXECUTION_IDLE
EXECUTION_COMPLETED
EXECUTION_FAILED
EXECUTION_CANCELLED
EVENT_GAP
```

Conceptual envelope:

```python
RuntimeEventEnvelope(
    execution_id,
    runtime_session,
    sequence,
    event_type,
    observed_at,
    runtime_event_id,
    raw_event_type,
    payload,
)
```

Rules:

- `sequence` is assigned monotonically by the adapter for one Relay ExecutionId;
- `observed_at` is Relay/adapter observation time;
- runtime-native event timestamp/ID may be retained when available;
- raw runtime payloads are not part of stable Relay semantics;
- sensitive material must be redacted or omitted;
- event order is evidence of observation order, not project authority.

Runtime events MUST NOT directly call lifecycle/governance mutation services.

---

# 14. S2.1-D11 — Event continuity is explicit

The contract does not assume event replay.

```python
EventContinuity(
    state = COMPLETE | LIVE_ONLY | INCOMPLETE,
    reason = ...,
)
```

For a runtime whose stream is live-only:

- initial subscription begins at the time the stream is consumed;
- after connection failure, a new subscription may miss events;
- the adapter must not invent replay;
- the next stream emits/records `EVENT_GAP` or inspection returns `INCOMPLETE` continuity.

A gap may make event evidence incomplete but does not itself decide the engineering result.

Terminal inspection is separate from event consumption.

---

# 15. S2.1-D12 — Cancellation is idempotent control, not lifecycle cancellation

```python
RuntimeCancelRequest(
    execution_id,
    runtime_session,
    reason,
)
```

`cancel()` is idempotent at the Relay contract boundary.

Acknowledgment states:

```text
REQUESTED
ALREADY_TERMINAL
NOT_FOUND
DENIED
```

Calling runtime cancel does not by itself transition the Relay Slice to `CANCELLED` or any other lifecycle phase.

The orchestration layer later decides what governance event follows.

---

# 16. S2.1-D13 — Resume is only same-authority continuation

Resume is optional.

If supported, resume may continue only:

```text
same ExecutionId
same request_digest
same workspace identity
same source baseline
same role/input payload
same permission-profile ref
```

Resume cannot widen scope or substitute a new work packet.

A new governed rework attempt uses a new `ExecutionId`; it is not modeled as resume.

An independent evaluator never resumes the implementer's session.

---

# 17. S2.1-D14 — Steering is optional and excluded from first implementation profile

Steering can easily become hidden authority expansion.

Therefore:

- `STEER` is optional;
- it is not required for initial AgentRuntime acceptance;
- the initial OpenCode profile MUST operate with steering disabled;
- a future steering design must bind every instruction to durable provenance and prove it cannot alter baseline, scope, role, permission profile, or acceptance criteria.

Slice 2.1 does not authorize a generic interactive steering channel.

---

# 18. S2.1-D15 — Runtime inspection is distinct from engineering-result verification

Conceptual inspection:

```python
RuntimeExecutionInspection(
    execution_id,
    runtime_session,
    runtime_status,
    terminal,
    summary,
    provenance,
    continuity,
    usage,
    runtime_output_refs,
    runtime_diff_hint,
)
```

Runtime statuses:

```text
RUNNING
SUCCEEDED
FAILED
BLOCKED
CANCELLED
UNKNOWN
```

Critical invariant:

```text
RuntimeExecutionInspection(SUCCEEDED)
    !=
SliceResultRecord
```

Even if OpenCode exposes session diff information, that diff is an observation/hint.

The future coding-execution layer must independently verify:

- repository identity;
- resulting commit;
- changed-file set;
- required quality evidence;

before constructing a Relay engineering result.

A runtime-reported commit or diff is never accepted on trust alone.

---

# 19. S2.1-D16 — Failure normalization

```text
UNSUPPORTED_CAPABILITY
UNSUPPORTED_RUNTIME_VERSION
REQUEST_CONFLICT
CONFIGURATION
AUTHENTICATION
PROVIDER_MODEL
RUNTIME_UNAVAILABLE
WORKSPACE_ACCESS
PERMISSION_DENIED
EVENT_CONTINUITY
TIMEOUT
RESOURCE_LIMIT
CANCELLED
AGENT_BLOCKED
RESULT_INSPECTION
TRANSPORT
INTERNAL
```

A `RuntimeFailure` contains:

```text
category
safe message
retryable advisory
runtime/provider diagnostic code if safe
execution/session refs when known
cause metadata only if sanitized
```

`retryable` is advisory only.

It never grants permission to create a new execution.

Unknown execution state after transport failure is fail-closed: inspect existing session/binding first.

---

# 20. S2.1-D17 — Permission enforcement is defense in depth

The Relay contract carries a permission-profile reference but does not claim that runtime permissions form a security boundary.

For OpenCode specifically, the adapter may translate a separately compiled policy into current OpenCode permission configuration.

The adapter must:

- pin the supported OpenCode API generation;
- test the exact mapping;
- fail if mandatory deny rules cannot be represented;
- never rely on runtime defaults for a mandatory Relay constraint;
- record the profile ref/digest used.

OpenCode permission behavior may narrow execution but cannot create Relay authority.

Production filesystem/process/network isolation remains the later Execution Workspace responsibility.

---

# 21. S2.1-D18 — Credentials stay external

`CredentialRef` is an opaque reference to externally managed credential material.

The runtime adapter receives a credential resolver/injected connection material at process/runtime boundary.

Rules:

- no token/password/key value in `.relay/`;
- no credential value in `RuntimeExecutionRequest` durable serialization;
- no credential value in normalized events;
- no credential value in failure details;
- no credential value in development memory.

Authentication failure is normalized as `AUTHENTICATION`, not solved by expanding access.

---

# 22. S2.1-D19 — OpenCode first adapter uses an explicit HTTP boundary

For Python Relay, the first accepted transport direction is:

```text
Relay Python
    ↓
OpenCodeRuntime
    ↓
HTTP transport
    ↓
explicit OpenCode server endpoint
```

Rationale:

- current OpenCode generated client/SDK is JS/TS;
- the server exposes a documented HTTP API;
- Relay already uses Python;
- using HTTP avoids embedding OpenCode JS types into Relay;
- it avoids adding Node/Bun as a Relay runtime dependency merely to reach the harness.

The adapter does not automatically install, discover, upgrade, or launch OpenCode in the base Slice 2.1 implementation.

Server/process lifecycle is separately governed.

The adapter accepts an explicit connection/endpoint reference supplied by configuration.

---

# 23. S2.1-D20 — OpenCode mapping

The adapter maps only behind its boundary:

```text
RuntimeWorkspaceAttachment.root
    → OpenCode session location/directory

RuntimeSessionRef
    ← OpenCode session ID

RuntimeExecutionRequest.input_payload
    → OpenCode session prompt/input

RuntimeSelection
    → OpenCode provider/model request where supported

events()
    ← OpenCode event stream

cancel()
    → OpenCode session abort

inspect()
    ← OpenCode session/status/diff/result surfaces

permission profile material
    → OpenCode permission config/policy
```

OpenCode-native objects do not leave the adapter.

Because current OpenCode event subscription is live-only, `EVENT_REPLAY` is not advertised for the first adapter unless separately proven by a later supported API.

Because OpenCode V1/V2 permission vocabulary differs, the adapter supports exactly the pinned generation tested by sidecar evidence.

---

# 24. S2.1-D21 — OpenCode sidecar evidence protocol

A live sidecar is REQUIRED before Human technical acceptance of a live `OpenCodeRuntime` adapter.

The sidecar is separately authorized and must use a disposable fixture repository/workspace, not Relay's canonical worktree.

Minimum protocol:

```text
1. record exact OpenCode version/API generation
2. start/connect to an explicit local test endpoint
3. bind an exact fixture repository commit/workspace
4. create one session programmatically
5. execute a benign bounded edit task
6. observe normalized events
7. prove external-directory denial
8. prove forbidden git push is denied
9. prove allowed read/edit operation succeeds
10. inspect session/result/diff
11. record requested and actual provider/model identity available
12. cancel a controlled long-running execution
13. test post-interruption inspection
14. test resume only if runtime advertises it
15. deliberately break event connection and record continuity behavior
16. normalize at least one provider/runtime failure
17. prove no credentials are written into fixture repository/Relay records
18. use a distinct session for a mock evaluator role
```

If current runtime behavior contradicts this design, the sidecar returns a design/implementation finding; it does not patch around the mismatch.

---

# 25. S2.1-D22 — Initial implementation boundary

A future base Slice 2.1 implementation is expected to add:

```text
src/relay_engine/agent_runtime/
    __init__.py
    errors.py
    models.py
    protocol.py
    opencode.py
```

Tests:

```text
tests/unit/test_agent_runtime_models.py
tests/unit/test_agent_runtime_contract.py
tests/unit/test_opencode_runtime.py
```

Expected bounded existing changes:

```text
src/relay_engine/domain/ids.py
    NO new execution ID; reuse ExecutionId
    only exports/typing changes if mechanically required

pyproject.toml
    httpx may move from dev-only to runtime dependency
    only if the implementation authority explicitly includes that dependency promotion

uv.lock
    only corresponding lock metadata change if required
```

No persistence schema is required in the base Slice 2.1 implementation.

No board/UI change is required.

No lifecycle/governance change is required.

No OpenCode process installation or Node/Bun dependency is required.

---

# 26. S2.1-D23 — OpenCode adapter implementation can exist without authorized agent execution

Implementing the adapter is not the same as using it to perform Relay engineering work.

Unit/contract tests use deterministic mocked HTTP/event transports.

A separately authorized sidecar may call a live disposable OpenCode service.

Production/dogfood Relay agent execution remains prohibited until later slices provide:

- accepted role contracts;
- runtime/provider/model routing;
- authoritative context/work packets;
- execution workspace policy;
- execution orchestration;
- explicit Human Authority.

---

# 27. S2.1-D24 — No persistence in this slice

Slice 2.1 defines value contracts and adapter semantics.

Durable execution/session/event storage is deferred to the execution-orchestration slice because persistence requirements depend on:

- work-packet identity;
- workspace identity;
- execution lifecycle;
- retries/recovery;
- M1 audit requirements.

Adding an `agent_runtime_sessions` or equivalent table during Slice 2.1 would be premature.

The design nevertheless fixes enough identity and idempotency semantics that later persistence cannot redefine authority.

---

# 28. Contract invariants

```text
AR-01 Relay authority is independent of runtime state.
AR-02 ExecutionId is the authoritative Relay execution-attempt identity.
AR-03 Runtime/session IDs are opaque provenance only.
AR-04 Same ExecutionId with different request digest fails closed.
AR-05 Runtime events are observational and cannot mutate lifecycle directly.
AR-06 Runtime success is not an engineering result.
AR-07 Runtime result is not evaluator judgment.
AR-08 Runtime result is not Human acceptance.
AR-09 Runtime result is not accepted-baseline promotion.
AR-10 Evaluator uses a separate ExecutionId and session.
AR-11 Resume never creates new authority.
AR-12 Steering is optional and disabled in the first profile.
AR-13 Permission policy can narrow but cannot create Relay authority.
AR-14 Workspace is supplied; runtime does not widen it.
AR-15 Credentials are external references.
AR-16 Requested and actual runtime/provider/model identity remain distinct.
AR-17 Missing actual identity is recorded, never fabricated.
AR-18 Unsupported runtime/API versions fail closed.
AR-19 Event gaps are explicit.
AR-20 OpenCode types never cross the adapter boundary.
```

---

# 29. Required tests for future implementation

## Models

```text
immutable / extra-forbid
nonblank bounded runtime/session/provider/model IDs
request digest deterministic
same request -> same digest
authority-relevant field change -> different digest
credential secret values cannot be serialized through contract types
```

## Capability/version

```text
missing mandatory capability -> fail before create_session
unsupported runtime/API version -> fail closed
optional capability absent -> typed unsupported failure
```

## Identity/conflict

```text
ExecutionId preserved end-to-end
runtime IDs do not replace ExecutionId
same ExecutionId + same digest retry is non-conflicting
same ExecutionId + different digest -> REQUEST_CONFLICT
second simultaneous start rejected
```

## Events

```text
normalized event vocabulary
monotonic adapter sequence
live-only stream represented honestly
disconnect -> EVENT_GAP / INCOMPLETE continuity
raw runtime event never mutates Relay governance
sensitive event fields sanitized
```

## Cancellation/inspection

```text
cancel idempotent
already-terminal cancel safe
inspection separate from events
runtime SUCCEEDED does not create SliceResultRecord
runtime diff remains non-authoritative hint
```

## OpenCode adapter

Using deterministic HTTP mock transport:

```text
session location mapping
prompt/input mapping
provider/model request mapping
event mapping
abort mapping
inspection/diff mapping
auth failure normalization
permission-denied normalization
transport failure normalization
version mismatch handling
no V1/V2 silent fallback
```

All existing Relay tests remain mandatory.

---

# 30. Quality gate

A future candidate must pass:

```text
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

and successful GitHub Actions CI on the exact candidate SHA.

Live sidecar evidence, if separately authorized, is additional evidence and not a substitute for deterministic tests.

---

# 31. Hard stops

Implementation must stop and escalate if it requires:

```text
new lifecycle semantics
new Human Authority semantics
new evaluator/acceptance semantics
new persistence schema
OpenCode SDK types in Relay domain contracts
Node/Bun as a Relay runtime dependency
automatic OpenCode install/upgrade/process discovery
runtime-created authority-expanding workspace
secret values in Relay durable data
event-driven direct lifecycle mutation
generic steering before separately designed authority
provider-specific workflow semantics
Phase 3 execution orchestration
unrelated Phase 1 hardening
```

A dependency promotion of existing `httpx` from dev to runtime is acceptable only if a later implementation authorization explicitly includes it.

---

# 32. Design acceptance matrix

An independent evaluator should require:

```text
[ ] runtime authority boundary is explicit
[ ] existing ExecutionId is reused
[ ] runtime/session IDs remain opaque
[ ] capability discovery is explicit
[ ] version/API compatibility fails closed
[ ] execution request is immutable and digest-bound
[ ] retry/conflict semantics are exact
[ ] workspace cannot be silently widened
[ ] context/work-packet construction remains outside Slice 2.1
[ ] permission profile is subordinate to Relay authority
[ ] credentials remain external
[ ] requested vs actual provider/model provenance is distinct
[ ] events are observational
[ ] event continuity/gaps are explicit
[ ] cancellation does not mutate Relay lifecycle
[ ] resume cannot widen authority
[ ] steering is not silently introduced
[ ] runtime inspection is not engineering-result acceptance
[ ] failure normalization is explicit
[ ] OpenCode types remain behind adapter
[ ] Python Relay does not require JS SDK coupling
[ ] OpenCode API generation is pinned
[ ] sidecar protocol is bounded and separately authorized
[ ] no new persistence is introduced prematurely
[ ] deterministic implementation/test surface is bounded
[ ] agent execution remains unauthorized
```

---

# 33. Resulting capability if implemented

After a future accepted Slice 2.1 implementation, Relay would have:

```text
a stable runtime-neutral AgentRuntime contract
        +
one OpenCode HTTP adapter implementation
        +
deterministic mocked contract tests
        +
explicit version/capability/provenance semantics
```

It would still NOT have authorization to run Relay engineering agents.

Later Phase 2/3 work must supply role contracts, routing, context/work packets, workspace policy, and execution orchestration.

---

# 34. Hard stop after Slice 2.1

Even after technical acceptance:

```text
Slice 2.2 Role Contracts:
separately opened/authorized

Slice 2.3 Runtime/Provider/Model Routing:
separately opened/authorized

Slice 2.4 Context/Work-Packet Inputs:
separately opened/authorized

Phase 3 execution:
separately authorized

Relay agent execution:
NOT implied
```

**Runtime capability ≠ Relay authority. Runtime completion ≠ engineering acceptance.**
