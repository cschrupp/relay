# Slice 2.1 — Independent Design Evaluation — Revision 2

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Evaluation ID:** `RLY-S21-DESIGN-EVAL-002`  
**Outcome:** `REVISE`  
**Design authority:** `RLY-S21-DESIGN-AUTH-001 — AUTHORIZED`  
**Combined design head evaluated:** `3f67c919a06a6ba6681605a6dac63d188f5de766`  
**Prior evaluation:** `RLY-S21-DESIGN-EVAL-001 — REVISE`  
**Reviewer role:** Independent Slice 2.1 Design Evaluator — GPT-5.6 Sol

## Decision

```text
REVISE
```

Revision 2 resolves F001–F004. One remaining binding ambiguity must be removed before acceptance.

## F005 — Session creation basis can drift from execution basis

**Severity:** MAJOR

Revision 2 defines a separate `RuntimeSessionRequest` containing a subset of the fields later carried by `RuntimeExecutionBasis`.

That permits two logically distinct values to exist:

```text
session created for:
workspace A / model A / permission profile A

open_execution request:
workspace B / model B / permission profile B
```

The design says `open_execution()` validates request/session/capabilities, but does not make the exact binding representation normative.

That leaves an implementation-significant authority/provenance seam open.

### Required revision

Bind session creation to the exact immutable execution request/basis rather than a separately reconstructable subset.

Preferred minimum design:

```text
create_session(RuntimeExecutionRequest)
    -> RuntimeSessionBinding

RuntimeSessionBinding:
    ExecutionId
    RuntimeSessionRef
    exact request_digest
    workspace identity
    created_at

open_execution(
    same RuntimeExecutionRequest,
    exact RuntimeSessionBinding
)
```

`open_execution` must reject any ExecutionId/request-digest/session-binding mismatch as `REQUEST_CONFLICT`.

The session binding must not duplicate mutable provider/workspace/profile truth that could diverge from the request basis.

This also strengthens retry/idempotency semantics without adding persistence.

## Revision 2 findings confirmed resolved

```text
F001 live-only event start/subscription race      RESOLVED
F002 OpenCode event scoping                       RESOLVED
F003 support objects / digest canonicalization    RESOLVED
F004 restart-recovery boundary                    RESOLVED
```

## Positive assessment

Apart from F005, the combined design is now implementation-grade:

- pre-start event observation is correct for a live-only stream;
- event attribution is exact-session scoped;
- queue overflow/disconnect produce explicit incomplete continuity;
- request digest semantics are deterministic;
- process-restart limitations are honest;
- permission prompts do not create hidden Human Authority;
- runtime/provider/model switching after basis lock is prohibited;
- no persistence, lifecycle, governance, or agent-execution scope has leaked into Slice 2.1.

## Required next state

Produce a narrow Revision 3 amendment resolving F005, then independently review the combined Revision 1 + Revision 2 + Revision 3 design.

Human design acceptance remains pending.

**REVISE is evidence, not implementation authority.**
