# Slice 2.1 — Independent Design Evaluation — Revision 4

**Document class:** Immutable evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-05  
**Project:** Relay  
**Slice:** 2.1 — Agent Runtime Contract  
**Evaluation ID:** `RLY-S21-DESIGN-EVAL-004`  
**Outcome:** `ACCEPT`  
**Design authority:** `RLY-S21-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact accepted combined design head:** `fc55a50167e8c83d05bad9664c6b8e8fed59db42`  
**Revision chain:** Revision 1 + Revision 2 + Revision 3 + formatting-only correction  
**Prior evaluations:** `RLY-S21-DESIGN-EVAL-001 — REVISE`; `RLY-S21-DESIGN-EVAL-002 — REVISE`; `RLY-S21-DESIGN-EVAL-003 — ACCEPT`  
**Reviewer role:** Independent Slice 2.1 Design Evaluator — GPT-5.6 Sol

## Decision

```text
ACCEPT
```

The exact head `fc55a50167e8c83d05bad9664c6b8e8fed59db42` is accepted.

The only change after `RLY-S21-DESIGN-EVAL-003 — ACCEPT` was the formatter-required whitespace normalization inside one Python-like Markdown code block:

```text
state = ...
reason = ...
```

became:

```text
state=...
reason=...
```

No design meaning, field, invariant, contract, authority boundary, or implementation surface changed.

All findings remain resolved:

```text
F001 RESOLVED
F002 RESOLVED
F003 RESOLVED
F004 RESOLVED
F005 RESOLVED
```

The combined design remains implementation-grade and preserves:

- exact Relay authority outside the runtime;
- exact request/session binding;
- fail-closed retry/conflict behavior;
- pre-admission event observation for live-only OpenCode streams;
- exact-session event attribution;
- explicit event-gap semantics;
- runtime status separate from engineering result/acceptance;
- OpenCode HTTP adapter isolation;
- API-generation/version pinning;
- external credentials;
- no persistence/schema/lifecycle/governance expansion;
- separately authorized live sidecar;
- agent execution still unauthorized.

## Gate state

```text
Slice 2.1:
OPEN

Design authorization:
RLY-S21-DESIGN-AUTH-001 — AUTHORIZED

Exact independently accepted combined design head:
fc55a50167e8c83d05bad9664c6b8e8fed59db42

Independent design evaluation:
RLY-S21-DESIGN-EVAL-004 — ACCEPT

Human design acceptance:
NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Live OpenCode sidecar:
NOT AUTHORIZED

Relay agent execution:
NOT AUTHORIZED
```

**Independent design ACCEPT is evidence only.**
