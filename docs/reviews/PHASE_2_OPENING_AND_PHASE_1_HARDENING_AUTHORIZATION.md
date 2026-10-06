# Relay — Phase 2 Opening and Phase 1 Accepted-Baseline / Active-Hardening Authorization

**Document class:** Immutable Human Authority record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Record:** `RLY-P2-OPEN-001`  
**Decision:** `AUTHORIZED`

## 1. Human authority

The Human explicitly authorized:

> Authorize Phase 2 opening under the accepted-baseline / active-hardening model.  
> Record Phase 1 as ACCEPTED BASELINE / HARDENING ACTIVE, not CLOSED.

## 2. Exact basis

```text
Canonical Relay engineering baseline before this documentation transition:
cf8aae9d44bfef5019500bac37ae6baf3cdb5235

Phase 1 M0 evaluation:
RLY-P1-M0-EVAL-001 — ACCEPT
validation record commit:
33e3d9c8c6342f8b7a5ac688630395c2f2a66a9c

Human M0 acceptance:
RLY-P1-M0-ACCEPT-001 — ACCEPTED
validation record commit:
6c0bca5dcf851bc3f7544d86197a62acdce68b9f
```

M0 established that Relay's deterministic-governance thesis is viable enough to justify continued investment. It was not a production-readiness gate for every Phase 1 product surface.

## 3. Authorized phase model

```text
Phase 1:
ACCEPTED BASELINE / HARDENING ACTIVE

Phase 1 M0:
PASSED / HUMAN-ACCEPTED

Phase 1 production maturity:
NOT CLAIMED

Phase 2:
OPEN

Slice 2.1:
NOT OPEN / NOT AUTHORIZED

Relay agent execution:
NOT AUTHORIZED
```

Phase 1 remains the governing deterministic substrate. Hardening may continue in parallel with Phase 2 through separately authorized work.

## 4. Blocking relationship

Phase 2 may proceed on the accepted Phase 1 baseline.

However, any Phase 1 deficiency that threatens:

- authority integrity;
- deterministic state transitions;
- provenance;
- Human control;
- evaluator independence;
- accepted-result promotion;
- fail-closed behavior;

is a blocking dependency for affected Phase 2 work.

Non-blocking maturity work may continue in parallel, including:

- UI/UX and information hierarchy;
- progressive disclosure and board ergonomics;
- terminology and governance clarity;
- canon practicality;
- development-memory presentation;
- operator workflow improvements.

## 5. Canonical documentation authority

This authority permits the documentation-only canonical transition required to represent the decision:

- advance the canonical Build Plan;
- advance the canonical Current Baseline;
- advance the corresponding registry pointers/digests;
- update non-authoritative presentation text that would otherwise incorrectly say Phase 2 is closed.

No runtime/source implementation is authorized by this record.

## 6. Explicit non-authority

This record does **not** authorize:

- opening Slice 2.1;
- Slice 2.1 design;
- any Phase 2 implementation;
- OpenCode or other runtime integration implementation;
- provider/model execution;
- Relay coding-agent execution;
- Phase 3;
- autonomous acceptance;
- closing Phase 1.

The governing distinctions remain:

```text
Phase open ≠ Slice open
Slice open ≠ design authorized
Design accepted ≠ implementation authorized
READY ≠ AUTHORIZED
Unblocked ≠ authorized
```
