# Slice 2.1 — Live OpenCode Sidecar Evidence Evaluation — Run 008

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-07  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Record:** `RLY-S21-SIDECAR-EVAL-008`  
**Outcome:** `REWORK`

## Evaluated subject

```text
Human sidecar authority:
RLY-S21-SIDECAR-AUTH-002 — AUTHORIZED

Run-008 handoff:
RLY-S21-SIDECAR-HANDOFF-002

Canonical governance head:
ce45cf5141265b1d8aa6b1f427776128c0d1c67f

Candidate:
5df1add9ed829a62a99d7f25f561a0f492ff5c73

Independent implementation evaluation:
RLY-S21-EVAL-003 — ACCEPT

Requested provider/model:
openrouter / google/gemini-3.8-flash
```

## Live evidence summary

Run 008 passed all prerequisite environment, credential, isolation, runtime, and prompt-schema gates:

```text
.env ignored/untracked: PASS
OPENROUTER_API_KEY presence: PASS
protected V1 integrity: PASS
all V2 invocations through isolation wrapper: PASS
OpenCode version/hash: PASS
authenticated /api/health: PASS
candidate describe(): PASS
exact OpenRouter model availability: PASS
requested/actual provider-model identity: FULL
fixture/session binding: PASS
programmatic session creation: PASS
prompt HTTP admission: 200 PASS
observer-before-prompt: PASS
one-prompt guard: PASS
correct root-level prompt body: PASS
credential leak proof: PASS
```

The candidate admitted exactly one prompt. The live runtime then emitted only:

```text
session.inbox.enqueued
```

No fixture edit occurred, no provider turn completed, inspection remained nonterminal/UNKNOWN, and independent Git diff remained empty.

Evidence package:

```text
/tmp/relay-s21-sidecar/evidence-run-008/
```

Reported SHA-256 of `SHA256SUMS.txt`:

```text
7e4e7d8b3ef8df397e5fb51e891a4567d534e1cf199595779a4b12dab9618d6c
```

## F008-A — BLOCKING — open_execution requests admit-only behavior

The candidate sends:

```json
{
  "text": "<input>",
  "files": [],
  "agents": [],
  "skills": [],
  "metadata": {},
  "resume": false
}
```

The accepted Relay contract requires `open_execution()` to:

```text
establish observation
        ↓
admit prompt/execution
        ↓
runtime execution
```

Run 008 established that the prompt is now accepted by the exact pinned runtime, but no runtime execution follows.

This behavior is consistent with OpenCode V2's documented/current semantics:

```text
resume omitted/true:
durable admission + execution wake

resume false:
durable admit-only
```

Current OpenCode V2 implementation calls the execution wake only when `resume !== false`.

The live evidence therefore establishes that the candidate's explicit `resume: false` is incompatible with the accepted Relay `open_execution()` semantics.

### Required correction

Before editing, confirm the exact installed `0.0.0-beta-17823` semantics through its non-secret embedded/generated route contract.

Then use the minimum request mapping that both:

1. admits exactly one prompt; and
2. schedules the runtime execution loop.

If the pinned beta confirms omission is the normal execution-starting default, prefer omission over an unnecessary explicit value.

Do not add a second prompt, explicit resume operation, or retry loop to compensate for the current admit-only request.

## F008-B — BLOCKING — deterministic mock masks admit-only behavior

The deterministic mock currently asserts `"resume": false` and then manually emits execution-like events after the prompt POST.

That means the mock cannot detect that the real runtime interprets the same request as admit-only.

### Required correction

The deterministic runtime model must distinguish:

```text
admit-only request
    -> admitted/inbox event only
    -> no execution-start event

execution-starting request
    -> admission
    -> execution wake / execution events
```

Add a regression test proving that the adapter's normal `open_execution()` request uses the execution-starting semantics and cannot regress to `resume: false`.

Preserve observer-before-admission and exactly-one-prompt guarantees.

## F008-C — PROVENANCE CHECK REQUIRED — generic prompt-response id must not be fabricated as invocation identity

The candidate currently derives `RuntimeInvocationRef` using:

```text
invocationID
or invocationId
or generic id
```

The deterministic mock returns:

```json
{"data": {"id": "invocation-1"}}
```

and asserts that `runtime_invocation` is present.

Current OpenCode V2 defines prompt success as an admitted-input record whose generic `id` is a session-message/input identity, not a runtime invocation identity.

Relay's contract defines `RuntimeInvocationRef` as an opaque **runtime-native invocation identity, when exposed**. Relay must not fabricate that identity from an unrelated generic ID.

### Required correction

Before changing this mapping, inspect the exact pinned beta's non-secret prompt-success schema.

If the exact beta does not expose a true invocation identifier:

```text
RuntimeExecutionHandle.runtime_invocation = None
```

is the correct bounded representation.

Remove generic `id` fallback for invocation provenance unless the exact beta proves that field is an invocation identity.

Update deterministic mocks accordingly.

This correction remains inside the adapter boundary and does not alter Relay's public protocol.

## D21 disposition

```text
D21-01 PASS
D21-02 PASS
D21-03 PASS
D21-04 PASS
D21-05 FAIL — prompt admitted but bounded edit never executed
D21-06 PASS — normalized admission/progress observation; no terminal completion
D21-07 NOT_RUN
D21-08 NOT_RUN
D21-09 NOT_RUN
D21-10 FAIL — inspection available but requested edit absent
D21-11 PASS
D21-12 NOT_RUN
D21-13 NOT_RUN
D21-14 NOT_APPLICABLE
D21-15 NOT_RUN
D21-16 NOT_RUN
D21-17 PASS
D21-18 NOT_RUN
```

## Classification

```text
prompt request-schema compatibility:
PASS

live session creation:
PASS

live prompt admission:
PASS

runtime execution wake:
FAIL

candidate implementation defect:
ESTABLISHED

accepted Slice 2.1 design defect:
NOT ESTABLISHED

provider/model availability:
PASS

provider inference failure:
NOT ESTABLISHED — execution was not woken

Human technical acceptance:
NOT ELIGIBLE
```

## Governance decision

```text
Run 008:
STOPPED FAIL-CLOSED

Evaluation:
RLY-S21-SIDECAR-EVAL-008 — REWORK

Candidate:
PRESERVED
5df1add9ed829a62a99d7f25f561a0f492ff5c73

Prior deterministic evaluation:
RLY-S21-EVAL-003 — HISTORICAL ACCEPT FOR THE EVALUATED CANDIDATE,
BUT LIVE TECHNICAL ELIGIBILITY IS BLOCKED BY THIS FINDING
```

No Human technical acceptance, promotion, Slice closure, Slice 2.2, or Phase 3 authority is issued.
