# Relay — Slice 2.1 Agent Runtime Contract — Implementation Handoff

**Document class:** Immutable implementation handoff  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-S21-IMPL-HANDOFF-001`

## 1. Authority

```text
Implementation authority:
RLY-S21-IMPL-AUTH-001 — AUTHORIZED

Authority record commit:
4626e64c5187f7f68af488ee5e42d169872463f2

Authorized implementation baseline:
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22

Implementation branch:
implementation/2.1-agent-runtime-contract

Exact accepted design head:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Independent design evaluation:
RLY-S21-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
RLY-S21-DESIGN-ACCEPT-001 — ACCEPTED
```

The implementation candidate must begin from the exact authorized baseline. Do not merge or rebase later `main`.

## 2. Executor role

The external implementation role is Codex.

Codex may produce and push one implementation candidate only.

Codex must report the actual executing model/runtime identity if exposed. Model identity is provenance, not authority.

## 3. Bootstrap

```bash
git fetch origin
git checkout implementation/2.1-agent-runtime-contract
git rev-parse HEAD
```

The exact pre-edit HEAD MUST be:

```text
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22
```

If not, STOP.

Also verify:

```bash
git status --short
```

Do not begin with unrelated tracked or untracked changes that could contaminate evidence.

## 4. Governing design precedence

Read these in order:

1. `docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT_DESIGN.md`
2. `docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT_DESIGN_REV2_AMENDMENT.md`
3. `docs/slices/SLICE_2_1_AGENT_RUNTIME_CONTRACT_DESIGN_REV3_AMENDMENT.md`
4. `docs/reviews/SLICE_2_1_DESIGN_EVALUATION_REV4.md`
5. `docs/reviews/SLICE_2_1_DESIGN_ACCEPTANCE.md`

Revision 3 is normative over Revision 2 where they differ; Revision 2 is normative over Revision 1.

Do not infer semantics from the older roadmap proposal when it conflicts with the accepted combined design.

## 5. Objective

Implement the minimum runtime-neutral `AgentRuntime` package and one OpenCode-over-HTTP adapter while preserving Relay authority outside the runtime.

The candidate MUST NOT perform real agent work.

The implementation target is:

```text
Relay-owned immutable runtime contracts
        +
AgentRuntime protocol
        +
OpenCode HTTP adapter
        +
deterministic mocked transport/event tests
```

## 6. Authorized files

Expected NEW:

```text
src/relay_engine/agent_runtime/__init__.py
src/relay_engine/agent_runtime/errors.py
src/relay_engine/agent_runtime/models.py
src/relay_engine/agent_runtime/protocol.py
src/relay_engine/agent_runtime/opencode.py

tests/unit/test_agent_runtime_models.py
tests/unit/test_agent_runtime_contract.py
tests/unit/test_opencode_runtime.py
```

One small private helper module beneath `src/relay_engine/agent_runtime/` is allowed only if the event-pump/transport code is materially clearer.

Expected MODIFY:

```text
pyproject.toml
uv.lock
```

Permitted only if mechanically necessary:

```text
src/relay_engine/agent_runtime/__init__.py exports
src/relay_engine/domain/ids.py
src/relay_engine/domain/__init__.py
```

Do NOT add a new execution ID prefix/type. Reuse existing `ExecutionId`.

No other production file is authorized by default.

## 7. Existing Relay primitives to reuse

Use:

```python
from relay_engine.domain import ContentDigest, ExecutionId, RepositoryRef
from relay_engine.domain.references import CommitRef
from relay_engine.domain._base import DomainModel, require_nonblank
```

or equivalent existing public imports.

Relay `DomainModel` is:

```text
frozen
extra="forbid"
strict
schema_version=1
```

New stable value objects should follow that convention.

Do not introduce a competing digest type.

`ContentDigest` remains:

```text
sha256:<64 lowercase hex>
```

## 8. Runtime models

Implement accepted types/enums with explicit bounded validation.

Names may differ only when repository conventions make a mechanically clearer equivalent, but semantics must remain exact.

Expected core enums/value objects include:

```text
RuntimeCapability
RuntimeStatus
RuntimeEventType
RuntimeContinuityState
RuntimeFailureCategory
RuntimeControlAckState
RuntimeIdentityCompleteness

RuntimeDescriptor
RuntimeSessionRef
RuntimeInvocationRef
RuntimeSelection
RuntimeProvenance

RuntimeWorkspaceAttachment
RuntimeInputPayload
RuntimePermissionProfileRef
CredentialRef
RuntimeExecutionLimits

RuntimeExecutionBasis
RuntimeExecutionRequest
RuntimeSessionBinding
RuntimeExecutionHandle

RuntimeEventEnvelope
EventContinuity
RuntimeUsage
RuntimeExecutionInspection

RuntimeCancelRequest
RuntimeControlAck
RuntimeFailure
```

Requirements:

- external/runtime identifiers: nonblank and bounded;
- duplicate credential refs rejected;
- duplicate capabilities rejected or normalized deterministically only if the accepted model explicitly permits;
- timestamps: timezone-aware and UTC-normalized;
- paths/workspace root: explicit values, no automatic widening;
- no secret field exists in `CredentialRef`;
- event payload/diagnostics must not require retaining raw secrets.

Do not put Relay authorization/lifecycle decisions inside runtime models.

## 9. Exact request digest

Implement a single deterministic helper for schema-v1 digest creation.

Normative algorithm:

```text
RuntimeExecutionBasis
    ↓ model JSON-compatible form
keys sorted lexically
separators=(",", ":")
ensure_ascii=False
UTF-8
SHA-256
    ↓
ContentDigest = sha256:<lowercase hex>
```

The digest subject includes `schema_version`.

Ordered lists/tuples retain declared order.

The v1 basis must contain no floating-point values.

`RuntimeExecutionRequest` is valid only when:

```text
supplied request_digest
==
recomputed exact basis digest
```

The digest does not recursively contain itself.

Tests must include a fixed known canonical JSON vector and expected digest, not only round-trip helper tests.

## 10. RuntimeExecutionBasis

The basis binds at minimum:

```text
execution_id
slice_id
source_baseline_id
workspace
input_payload
runtime_selection
permission_profile_ref
credential_refs
required_capabilities
limits
schema_version
```

Workspace must bind:

```text
workspace_id
root
repository identity
source commit
```

Input payload must bind:

```text
text
payload_digest
attachment refs
```

Runtime selection binds:

```text
runtime_id
requested_provider_id
requested_model_id
```

No actual runtime-generated session/model identity belongs in the basis.

## 11. Protocol

Normative minimum:

```python
class AgentRuntime(Protocol):
    async def describe(self) -> RuntimeDescriptor: ...

    async def create_session(
        self,
        request: RuntimeExecutionRequest,
    ) -> RuntimeSessionBinding: ...

    async def open_execution(
        self,
        request: RuntimeExecutionRequest,
        binding: RuntimeSessionBinding,
    ) -> RuntimeExecutionHandle: ...

    def events(
        self,
        handle: RuntimeExecutionHandle,
    ) -> AsyncIterator[RuntimeEventEnvelope]: ...

    async def cancel(
        self,
        request: RuntimeCancelRequest,
    ) -> RuntimeControlAck: ...

    async def inspect(
        self,
        handle: RuntimeExecutionHandle,
    ) -> RuntimeExecutionInspection: ...
```

Optional resume should be represented by a separate capability/protocol extension.

Do not implement steering in the initial profile.

Do not implement a generic orchestration service.

## 12. Exact session binding

`create_session(request)` receives the exact execution request.

It must not admit the prompt.

Return a binding equivalent to:

```text
ExecutionId
RuntimeSessionRef
exact request_digest
workspace_id
created_at
```

Do not duplicate provider/model/profile/input truth in the binding.

Before any event-pump start or prompt admission, `open_execution` must check:

```text
binding.execution_id == request.basis.execution_id
binding.request_digest == request.request_digest
binding.workspace_id == request.basis.workspace.workspace_id
recompute(request.basis) == request.request_digest
binding.runtime_session.runtime_id == request.basis.runtime_selection.runtime_id
```

Mismatch:

```text
REQUEST_CONFLICT
```

No event pump/prompt admission on mismatch.

## 13. Process-local idempotency

Within one `OpenCodeRuntime` instance/process:

```text
same ExecutionId + same digest + known binding
    -> return/reuse exact binding

same ExecutionId + different digest
    -> REQUEST_CONFLICT
```

Only one active invocation is allowed per execution binding.

Do not add persistent storage.

Do not discover/guess a remote session after process-state loss.

Expose/return:

```text
SESSION_BINDING_REQUIRED
```

when exact prior binding is required but unavailable.

## 14. httpx dependency

Move:

```text
httpx>=0.28,<1
```

from dev-only dependencies to `[project].dependencies`.

Update `uv.lock` only as required by that promotion.

No additional package is authorized.

Use `httpx.AsyncClient` or a mechanically equivalent httpx async transport.

The adapter should accept an injectable/preconfigured client or transport boundary so deterministic tests can use `httpx.MockTransport` or an equivalent in-process mock.

## 15. OpenCode connection model

The adapter receives an explicit endpoint/base URL and compatibility configuration.

It must NOT:

- install OpenCode;
- spawn OpenCode;
- search PATH for OpenCode;
- upgrade OpenCode;
- auto-discover a local server;
- start Node/Bun;
- read user auth files;
- acquire provider credentials itself.

The first accepted API profile is one explicitly pinned OpenCode API generation. Do not silently fall back across generations.

If runtime/API version information is absent or incompatible where the configured profile requires it, fail closed.

Keep endpoint/path parsing/mapping private to `OpenCodeRuntime`.

OpenCode response types must not become Relay public types.

## 16. OpenCode execution sequence

For the initial live-only profile, implementation semantics are:

```text
create_session(exact request)
    ↓
exact RuntimeSessionBinding
    ↓
open_execution(request, binding)
    ↓
validate request + binding + capability/version
    ↓
establish event stream
    ↓
activate exact-session/location filter
    ↓
start bounded event pump
    ↓
prove event pump ready
    ↓
admit exactly one prompt/input
    ↓
return RuntimeExecutionHandle
```

If event observation cannot be established before prompt admission:

```text
EVENT_OBSERVATION_UNAVAILABLE
```

and prompt admission MUST NOT occur.

## 17. Event pump

Use a bounded per-execution queue.

Requirements:

- exact attributable events only;
- unrelated session events ignored;
- server-level unscoped diagnostics not attributed to an ExecutionId;
- execution-relevant ambiguous event -> continuity incomplete / EVENT_ATTRIBUTION;
- adapter-assigned monotonic sequence for normalized attributable events;
- sensitive raw fields redacted/omitted;
- event callback/pump does not call Relay persistence/governance/lifecycle;
- no generic event bus.

If queue overflows:

```text
continuity = INCOMPLETE
reason = BUFFER_OVERFLOW
EVENT_GAP when representable
```

If live stream disconnects:

```text
continuity = INCOMPLETE
reason = STREAM_DISCONNECTED
EVENT_GAP
```

Re-subscription may observe future live events but must not claim replay.

## 18. Event normalization

Support the accepted stable vocabulary:

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

Preserve raw event type/id only as bounded provenance when safe.

Runtime events never mutate Relay project state.

## 19. Permissions

Initial OpenCode profile is non-interactive:

```text
required allow -> explicit allow
required deny  -> explicit deny
would require ask -> blocked/unsupported
```

Do not automatically approve an `ask` permission.

Do not build a Human permission-response UI or channel.

Runtime permission narrowing is defense in depth only.

## 20. Credentials

`CredentialRef` carries identifier only.

No secret value may appear in:

```text
models
request JSON intended for durable use
normalized events
safe failure messages
inspection summaries
tests/fixtures committed to repo
```

If tests need an auth header, use an obvious non-secret sentinel and assert it never appears in normalized outputs.

## 21. Provider/model provenance

Request records:

```text
requested_provider_id
requested_model_id
```

Inspection/result provenance records actual provider/model only when exposed.

Use:

```text
FULL
PARTIAL
UNKNOWN
```

or exact accepted equivalent.

Never infer an exact actual model from the requested model.

Do not change provider/model/agent after basis lock in the first profile.

## 22. Cancel

`cancel()` is idempotent at the Relay boundary.

Supported acknowledgment states:

```text
REQUESTED
ALREADY_TERMINAL
NOT_FOUND
DENIED
```

Cancel does not mutate Relay lifecycle.

## 23. Inspect

`inspect()` returns runtime observation only:

```text
runtime status
terminal flag
safe summary
runtime provenance
event continuity
usage when exposed
runtime output refs/hints
runtime diff hint when exposed
```

Critical assertion:

```text
RuntimeStatus.SUCCEEDED
!=
SliceResultRecord
```

Do not import/call manual-evaluation, baseline-promotion, or governance services from `agent_runtime`.

## 24. Failure categories

Implement the accepted normalized failure vocabulary, including:

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
EVENT_OBSERVATION_UNAVAILABLE
EVENT_ATTRIBUTION
SESSION_BINDING_REQUIRED
TIMEOUT
RESOURCE_LIMIT
CANCELLED
AGENT_BLOCKED
RESULT_INSPECTION
TRANSPORT
INTERNAL
```

Safe messages must not expose secrets.

`retryable` is advisory only and never authorizes a new execution/session.

## 25. Required deterministic tests

At minimum prove:

### Models / digest

```text
strict/frozen/extra-forbid
nonblank/bounded IDs
aware UTC timestamps
duplicate credential refs rejected
fixed canonical JSON digest vector
same basis -> same digest
authority-relevant basis change -> different digest
request rejects wrong digest
no secret-bearing CredentialRef surface
```

### Capability / version

```text
missing required capability -> fail before session creation
unsupported API/runtime compatibility -> fail closed
optional capability absent -> typed unsupported behavior
```

### Session binding / idempotency

```text
create_session binds exact digest
create_session does not send prompt
same request retry reuses exact known binding
same ExecutionId + changed digest -> REQUEST_CONFLICT
binding/digest mismatch -> no event pump / no prompt
binding/workspace mismatch -> no prompt
binding/runtime mismatch -> no prompt
second active invocation rejected
process-loss/no supplied binding -> SESSION_BINDING_REQUIRED
adapter does not list/guess replacement session
```

### Event sequencing

```text
event pump ready before prompt call
immediate post-prompt event retained
unrelated session event ignored
unscoped server diagnostic not attributed
ambiguous event -> incomplete continuity
monotonic adapter sequence
queue overflow -> EVENT_GAP / INCOMPLETE
stream disconnect -> EVENT_GAP / INCOMPLETE
no replay claimed
no event calls Relay governance/lifecycle
```

### Permission / security

```text
ASK requirement never auto-approved
forbidden operation maps to deny/block
credential sentinel not leaked into events/errors/inspection
external directory/session mismatch rejected or not attributed
```

### Cancellation / inspection

```text
cancel idempotent
already-terminal cancel safe
inspect independent of event consumption
runtime SUCCEEDED creates no Relay engineering result
runtime diff remains a non-authoritative hint
requested-vs-actual model identity remains distinct
```

### OpenCode mocked HTTP mapping

```text
explicit endpoint used
session created at supplied workspace
prompt admitted only after event pump ready
provider/model request mapping
exact session event filtering
abort/cancel mapping
inspection/status/diff mapping
auth failure normalization
permission-denied normalization
transport failure normalization
malformed response normalization
version/API mismatch fail closed
no V1/V2 silent fallback
```

## 26. Forbidden imports / coupling

Production `agent_runtime` must not depend on or call:

```text
relay_engine.governance mutation services
relay_engine.lifecycle mutation services
relay_engine.human_control mutation services
relay_engine.manual_evaluation mutation services
relay_engine.persistence write APIs
board/UI controls
```

Domain identity/value types may be imported.

## 27. No live sidecar in this candidate

Do not execute:

```text
opencode ...
npx ...
bun ...
provider API requests
real model inference
real OpenCode HTTP endpoints
```

Do not require local OpenCode installation for unit tests or CI.

If the implementation cannot be meaningfully completed without a live call, STOP and report the exact missing evidence rather than making the call.

## 28. Quality gates

Run:

```bash
uv sync --frozen --group dev

uv run pytest tests/unit/test_agent_runtime_models.py
uv run pytest tests/unit/test_agent_runtime_contract.py
uv run pytest tests/unit/test_opencode_runtime.py

uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

If you run `ruff format` to repair formatting, inspect the resulting diff and keep it within authorized files.

## 29. Scope verification

Before committing:

```bash
git status --short
git diff --name-only aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22...HEAD
```

Expected production/test paths are only the authorized agent-runtime package, tests, `pyproject.toml`, and `uv.lock`, plus the narrowly permitted domain export/type file only if genuinely necessary.

If unrelated files appear, remove them or STOP.

## 30. Candidate / push

Commit one coherent implementation candidate.

Push only to:

```text
implementation/2.1-agent-runtime-contract
```

Do NOT update `main`.

Do NOT update the design branch.

Do NOT create acceptance/closure records.

After push, obtain exact candidate SHA and check GitHub Actions for that exact SHA.

## 31. Required Codex report

Return exactly enough evidence to independently evaluate:

```text
authorized baseline:
aaec399b7d8cd1c4f39b7171f664cb85aa4ecf22

implementation authority:
RLY-S21-IMPL-AUTH-001

branch:
implementation/2.1-agent-runtime-contract

candidate SHA:
<exact>

executor:
Codex

actual model:
<exact if exposed>

model provenance deviation:
NONE or exact deviation

changed files:
<complete list>

accepted design coverage:
S2.1-D01..D38 — PASS/FAIL with concise mapping

dependency change:
httpx promoted dev -> runtime: PASS/FAIL
other dependency changes: NONE / exact deviation

focused tests:
<exact counts>

ruff format:
PASS/FAIL

ruff lint:
PASS/FAIL

pyright:
PASS/FAIL + exact errors/warnings

full pytest:
<exact counts>

build:
PASS/FAIL

git diff --check:
PASS/FAIL

GitHub Actions:
<run ID, candidate SHA, status>

live OpenCode/provider calls:
NONE

deviations:
NONE or exact list

new work discovered:
NONE or exact list
```

## 32. Stop boundary

This is an implementation candidate only.

Codex is NOT authorized to:

- independently accept its own implementation;
- run the live OpenCode sidecar;
- use real credentials;
- call a provider/model;
- use the adapter for real Relay engineering;
- grant Human technical acceptance;
- promote/merge the result;
- close Slice 2.1;
- open Slice 2.2;
- begin Phase 3;
- execute Relay agents.

Stop after pushing the candidate and returning the evidence report.

**Implementation authorized ≠ runtime execution authorized.**
