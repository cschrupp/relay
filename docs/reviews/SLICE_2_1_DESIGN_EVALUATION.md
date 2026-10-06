# Slice 2.1 — Independent Design Evaluation — Revision 1

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Evaluation ID:** `RLY-S21-DESIGN-EVAL-001`  
**Outcome:** `REVISE`  
**Design authority:** `RLY-S21-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact evaluated design commit:** `c23f838f6de4a948b38020b2af66851e119e47a8`  
**Reviewer role:** Independent Slice 2.1 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REVISE
```

The design has the correct architectural direction and preserves Relay's authority boundary, but four implementation-significant ambiguities remain. They must be resolved before Human design acceptance.

No implementation is authorized.

---

## F001 — Live-only event stream creates a start/subscription race

**Severity:** BLOCKING DESIGN FINDING

Revision 1 defines:

```text
create_session()
start()
events()
```

as separate caller operations.

Current OpenCode documentation states that its event subscription is live-only with no replay or automatic reconnection. Therefore an OpenCode adapter that starts a prompt and only then lets the caller begin consuming events can lose events emitted between start and subscription.

That would make the first runtime adapter unable to satisfy its own continuity semantics.

### Required revision

The design must make event observation active before execution admission for live-only runtimes.

Acceptable architecture:

```text
adapter prepares/binds session
        ↓
adapter starts event pump and bounded buffer
        ↓
adapter admits prompt/execution
        ↓
caller receives handle
        ↓
events(handle) drains already-active adapter stream
```

or an equivalent atomic `open/start-and-observe` contract.

The design must state what happens when event observation cannot be established before start.

---

## F002 — OpenCode event scoping is under-specified

**Severity:** MAJOR

OpenCode event subscription is server/client scoped rather than a Relay ExecutionId-native stream.

Revision 1 does not specify how the adapter proves that an incoming event belongs to the exact bound session/location before converting it into a Relay event.

Without this, unrelated session events could contaminate execution provenance.

### Required revision

The OpenCode adapter must filter/map every normalized event against the exact runtime session and, where necessary, location/workspace identity.

Unattributable or ambiguous events must not be attributed to the Relay ExecutionId.

The design must define whether such events are ignored, retained only as raw diagnostics, or treated as continuity/protocol errors.

---

## F003 — Several protocol support objects are referenced but not sufficiently defined

**Severity:** MAJOR

Revision 1 gives a useful top-level request and inspection shape but leaves implementer-significant values implicit:

```text
RuntimeSessionRequest
RuntimeExecutionHandle
RuntimePermissionProfileRef
CredentialRef
RuntimeControlAck
request-digest canonicalization
```

The exact digest basis is especially important because the design makes it a conflict/idempotency invariant.

### Required revision

Define the minimum immutable fields and validation rules for these values.

For request digest, define:

- the exact digest subject value;
- canonical serialization;
- exclusion of `request_digest` itself;
- UTF-8 / SHA-256 rule;
- which path/runtime-local fields are included;
- how future schema versions avoid accidental digest reinterpretation.

---

## F004 — Restart recovery is stronger than the accepted persistence boundary can support

**Severity:** MAJOR

Revision 1 correctly defers durable ExecutionId→runtime-session persistence, but also requires Relay to inspect the existing session before retrying after uncertain transport state.

After a Relay process restart, the base Slice 2.1 adapter may not possess the runtime-session binding needed to perform that inspection.

### Required revision

Make the boundary explicit:

```text
Slice 2.1 contract/adapter:
process-lifetime binding only unless supplied an existing RuntimeSessionRef

restart-safe governed execution:
NOT PROVIDED until later durable execution orchestration/persistence
```

If process state is lost and no durable binding is supplied, the adapter must fail closed rather than create a replacement session.

Live Slice 2.1 sidecar evidence may exercise process-local recovery, but technical acceptance must not imply restart-safe autonomous execution.

---

## Positive findings

The evaluator specifically accepts the direction of:

- reusing `ExecutionId`;
- keeping OpenCode IDs opaque;
- runtime success distinct from engineering result;
- no direct lifecycle mutation from events;
- requested/actual provider/model provenance;
- external credential references;
- no new persistence schema in Slice 2.1;
- HTTP boundary for Python Relay instead of embedding JS/TS SDK types;
- API-generation/version pinning;
- steering excluded from the first profile;
- separately authorized sidecar;
- runtime permissions subordinate to Relay authority.

---

## Required next state

Produce a bounded Revision 2 amendment resolving F001–F004.

The evaluator should then review the combined design:

```text
Revision 1
+
Revision 2 Amendment
```

Human design acceptance remains pending.

**REVISE is not implementation authority.**
