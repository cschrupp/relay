# Slice 2.1 — Independent Design Evaluation — Revision 3

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Evaluation ID:** `RLY-S21-DESIGN-EVAL-003`  
**Outcome:** `ACCEPT`  
**Design authority:** `RLY-S21-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact accepted combined design head:** `db2ef143430d1fa0d9746f579e0ed0e3e472e053`  
**Revision chain:** Revision 1 + Revision 2 + Revision 3  
**Prior evaluations:** `RLY-S21-DESIGN-EVAL-001 — REVISE`; `RLY-S21-DESIGN-EVAL-002 — REVISE`  
**Reviewer role:** Independent Slice 2.1 Design Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The combined Revision 1 + Revision 2 + Revision 3 design satisfies `RLY-S21-DESIGN-AUTH-001`.

No blocking or major design findings remain.

---

# 1. Findings resolution

```text
F001 live-only event start/subscription race      RESOLVED
F002 OpenCode event scoping                       RESOLVED
F003 support objects / digest canonicalization    RESOLVED
F004 restart-recovery boundary                    RESOLVED
F005 session creation / execution basis drift     RESOLVED
```

Revision 3 is normative over Revision 2 where they differ; Revision 2 is normative over Revision 1.

---

# 2. Accepted architectural result

The accepted contract keeps Relay authority outside the runtime:

```text
exact authorized Relay execution basis
        ↓
RuntimeExecutionRequest + deterministic digest
        ↓
create_session(exact request)
        ↓
RuntimeSessionBinding(exact digest)
        ↓
event observer active before prompt admission
        ↓
open_execution(exact request + exact binding)
        ↓
external runtime
        ↓
normalized observational events + inspection
```

The following remain intentionally separate:

```text
runtime permission
    != Relay authorization

runtime status
    != Relay lifecycle

runtime success
    != engineering result

engineering result
    != evaluator decision
    != Human technical acceptance
    != accepted-result promotion
```

---

# 3. Accepted identity and retry semantics

The evaluator accepts:

- existing Relay `ExecutionId` as the governed attempt identity;
- opaque runtime/session IDs as provenance only;
- exact request-digest binding;
- same ExecutionId + different digest -> fail closed;
- one active runtime invocation per execution binding;
- evaluator execution requires a distinct ExecutionId/session;
- rework is a new governed execution, not resume;
- resume, if later enabled, is same-authority continuation only.

The combined design no longer contains a separate session-request reconstruction seam.

---

# 4. Accepted event semantics

The design correctly accounts for a live-only OpenCode stream.

For the first adapter:

```text
create exact session
    ↓
subscribe / event pump ready
    ↓
exact-session filtering
    ↓
prompt admission
```

Events are:

- observational;
- session/location attributed before normalization;
- monotonically sequenced at the adapter boundary;
- bounded-buffered;
- explicitly incomplete after overflow/disconnect/gap;
- prohibited from directly mutating Relay lifecycle/governance.

This is materially safer than assuming replay semantics the runtime does not provide.

---

# 5. Accepted OpenCode boundary

The design appropriately chooses an explicit HTTP boundary for Python Relay rather than making the JS/TS OpenCode SDK part of Relay's domain/runtime dependency surface.

Accepted constraints include:

- exact API-generation/version compatibility;
- no silent V1/V2 fallback;
- no OpenCode-native type crossing the adapter;
- explicit endpoint/connection configuration;
- no automatic install/upgrade/process discovery in base Slice 2.1;
- OpenCode workspace location supplied by Relay;
- runtime worktree creation not treated as Relay workspace authority;
- session permissions as defense in depth only;
- non-interactive first permission profile;
- optional steering disabled initially.

A live OpenCode sidecar remains separately authorized and required before Human technical acceptance of the live adapter.

---

# 6. Accepted recovery limitation

The evaluator accepts the deliberate absence of persistence in Slice 2.1.

The contract is honest that:

```text
process-lifetime exact binding:
SUPPORTED

restart-safe governed execution:
NOT PROVIDED
```

After process-state loss, no session may be guessed or recreated. A later orchestration/persistence slice must provide exact durable binding before restart-safe execution can exist.

This is minimum sufficient architecture rather than a deficiency to patch in Slice 2.1.

---

# 7. Accepted provenance

The contract distinguishes requested from actual:

```text
runtime
provider
model
version/API generation
```

Missing actual identity is recorded as partial/unknown rather than fabricated.

Credential values remain outside durable Relay data.

The request digest binds credential-reference identities but not secret material.

---

# 8. Accepted implementation boundary

Expected production surface:

```text
src/relay_engine/agent_runtime/
    __init__.py
    errors.py
    models.py
    protocol.py
    opencode.py
```

Expected tests:

```text
tests/unit/test_agent_runtime_models.py
tests/unit/test_agent_runtime_contract.py
tests/unit/test_opencode_runtime.py
```

Expected existing-file changes are narrowly bounded.

No schema migration, board change, lifecycle change, governance change, Node/Bun dependency, runtime process installer, or agent-execution orchestration is accepted by this design.

A later implementation authorization may explicitly permit promotion of the already-present `httpx` package from dev-only to runtime dependency for the Python HTTP adapter. Design acceptance alone does not authorize that dependency change.

---

# 9. Sidecar hard boundary

The live OpenCode sidecar protocol is well bounded and remains separately unauthorized.

Sidecar success is evidence only.

It cannot:

- authorize implementation;
- authorize agent execution;
- establish Human acceptance;
- open Phase 3;
- replace deterministic contract tests.

If sidecar behavior contradicts the accepted design, the conflict returns to design/rework rather than being silently adapted.

---

# 10. Acceptance matrix

```text
[x] runtime authority boundary explicit
[x] ExecutionId reused
[x] runtime/session IDs opaque
[x] capability discovery explicit
[x] runtime/API compatibility fail closed
[x] execution request immutable and digest-bound
[x] exact canonical digest defined
[x] session creation bound to exact request
[x] retry/conflict semantics exact
[x] event observer active before live execution
[x] event attribution exact-session scoped
[x] event gaps explicit
[x] cancellation does not mutate lifecycle
[x] resume cannot widen authority
[x] steering excluded from initial profile
[x] workspace cannot be silently widened
[x] permission profile subordinate to Relay authority
[x] credentials external
[x] requested/actual model provenance distinct
[x] runtime inspection not engineering-result acceptance
[x] failure normalization explicit
[x] OpenCode types behind adapter
[x] Python Relay not coupled to JS SDK
[x] OpenCode API generation pinned
[x] sidecar bounded and separately authorized
[x] no premature persistence
[x] bounded implementation/test surface
[x] agent execution remains unauthorized
```

---

# 11. Gate state

```text
Slice 2.1:
OPEN

Design authorization:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

Exact independently accepted combined design head:
db2ef143430d1fa0d9746f579e0ed0e3e472e053

Independent design evaluation:
RLY-S21-DESIGN-EVAL-003 — ACCEPT

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Live OpenCode sidecar:
NOT AUTHORIZED

Relay agent execution:
NOT AUTHORIZED
```

**Independent design ACCEPT is evidence. It does not grant Human design acceptance, implementation authority, sidecar authority, or agent-execution authority.**
