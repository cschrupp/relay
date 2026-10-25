# Relay — Slice 2.5 Project State Resolution and Authority Compilation — Implementation Evaluation 001

**Document class:** Immutable independent SOL implementation evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Evaluation:** `RLY-S25-IMPL-EVAL-001 — REWORK / NARROW`

## Evaluated subject

```text
Repository:
cschrupp/relay

Implementation branch:
implementation/2.5-project-state-resolution-authority-compilation

Reviewed candidate:
4311912303cde089e165c9fa6bdd803d3b402918

Candidate parent / original authorized implementation baseline:
6203a693efb12ae22858d54b6e2edd46e95a52f4

Accepted normative design:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Original implementation authority:
RLY-S25-IMPL-AUTH-001 — AUTHORIZED

Implementation scope:
RLY-S25-CODEX-SCOPE-001
```

Candidate `4311912303cde089e165c9fa6bdd803d3b402918` is exactly one implementation commit ahead of the original authorized baseline and changes only the four authorized production modules and five authorized test files.

Exact-head GitHub Actions run `40153317897` completed successfully for the reviewed SHA.

Build/test success is evidence only and does not establish conformance.

## Disposition

```text
RLY-S25-IMPL-EVAL-001 — REWORK / NARROW
```

The implementation architecture is substantially correct and must not be broadly redesigned. Corrective work is limited to findings I001–I005 below.

## I001 — authority-bearing typed content is not cryptographically bound to backing value

**Severity:** BLOCKING

The implementation verifies that a `BackingProvenanceRef` names an accepted source assertion, but several authority-bearing typed objects can carry normative content that is not proven to be the exact content identified by the backing assertion's `value_digest`.

Affected semantic classes include, as applicable:

- `Invariant`;
- `QualificationFact`;
- `RequirementEdge`;
- `NegativeDecision`;
- `ResponsibilityClaim`;
- `ConsumableFact`;
- any equivalent authority-bearing typed fact entering resolved state.

The correction must establish an exact deterministic content binding between each authority-bearing typed value and the accepted backing predicate value used to authorize it.

A valid provenance reference accompanying altered normative content must fail closed.

Missing or mismatched binding must yield `INDETERMINATE`, not accepted state.

## I002 — qualification evidence and acceptance lineage are insufficiently verified

**Severity:** BLOCKING

A qualification may not be satisfied merely because referenced acceptance records exist.

The correction must prove, for required qualification evidence and acceptance:

1. each exact evidence reference is present in the pinned snapshot/materialized source set and is admissible for that qualification;
2. every required acceptance reference is exact, accepted, in scope, and explicitly accepts the exact qualification/evidence subject it is being used to satisfy;
3. unrelated Human/technical acceptance records cannot satisfy a qualification;
4. missing known acceptance is `BLOCKED` when absence is established;
5. unresolved evidence/acceptance lineage is `INDETERMINATE`.

Historical PASS remains evidence only.

## I003 — SUPERSEDED negative-decision semantics contradict accepted design

**Severity:** BLOCKING

`SUPERSEDED` means the exact prior subject is no longer current because an explicit successor replaced it.

It is **not** a universal prohibition and must not be treated identically to `REJECTED` or `PROHIBITED_UNLESS_REAUTHORIZED`.

The correction must preserve:

```text
SUPERSEDED:
exact prior subject cannot satisfy current predecessor/current-state use
use exact accepted successor where required
not a blanket prohibition of materially different successors

REJECTED:
matching request blocked absent exact reauthorization

PROHIBITED_UNLESS_REAUTHORIZED:
matching request blocked absent exact Human reauthorization
```

## I004 — unprovenanced ProducedExpectation ingress

**Severity:** BLOCKING

Caller-supplied `ProducedExpectation` values currently can enter `ResolvedProjectState` without exact accepted provenance.

That permits normative output/evidence expectations to affect a READY candidate without being derived from an accepted `PRODUCES` edge or another exact accepted source.

Correction must either:

- remove the direct unprovenanced ingress and derive produced expectations only from verified accepted `PRODUCES` edges; or
- require exact accepted provenance/content binding mechanically equivalent to all other authority-bearing state.

No arbitrary caller-provided normative expectation may enter resolved authority state.

## I005 — frozen dogfood acceptance matrix incomplete

**Severity:** BLOCKING

`tests/unit/test_project_state_dogfood.py` does not implement the frozen end-to-end resolver/compiler scenarios required by the accepted design and `RLY-S25-CODEX-SCOPE-001`.

Corrective coverage must deterministically exercise the required outcome classes, including at minimum:

### WellPlot

- missing environment qualification -> `BLOCKED`;
- missing accepted smoke -> `BLOCKED`;
- exact subject mismatch -> historical PASS retained + `NOT_APPLICABLE` + required request blocked;
- unknown required runtime identity -> `INDETERMINATE`;
- responsibility collision -> `BLOCKED`;
- rejected/prohibited fallback/semantic path -> `BLOCKED`;
- consumed namespace -> `BLOCKED`;
- incomplete namespace ledger -> `INDETERMINATE`.

### Tension/FEM

- exact scientific level / attempt / namespace consumption;
- consumed -> `BLOCKED`;
- different frozen oracle subject -> historical PASS retained + `NOT_APPLICABLE`;
- unknown ledger/subject -> `INDETERMINATE`.

### Seneca

- backend/GPU/runtime/environment qualification applicability;
- required identity mismatch -> historical PASS retained + `NOT_APPLICABLE` and required new qualification blocked;
- unknown required identity -> `INDETERMINATE`.

### Relay self-dogfood

- exact accepted predecessor/design/implementation/Human-acceptance/closure chain;
- inherited constraints;
- no chat-history reconstruction;
- `PROPOSED_WORK != authorized work`;
- no authorized successor preserves `BACKLOG_EXHAUSTED`;
- resolver/compiler does not invent a successor.

Equivalent deterministic fixture factoring is allowed. The frozen semantic families may not be reduced to isolated applicability-unit tests.

## Non-blocking governance finding G001

The original implementation authority decision existed but its immutable repository record was omitted.

This has been repaired by:

`RLY-S25-IMPL-AUTH-001 — AUTHORIZED`

recorded in:

`docs/reviews/SLICE_2_5_IMPLEMENTATION_AUTHORIZATION.md`

The repair does not accept the reviewed candidate and does not expand corrective implementation scope.

## Preserved accepted work

The corrective pass should preserve the candidate's already-sound architecture, including:

- pure four-module package boundary;
- immutable strict models;
- canonical ordering;
- canonical-pointer selection distinct from claim authority;
- historical result separate from current applicability;
- tri-state `RESOLVED/BLOCKED/INDETERMINATE` and `READY/BLOCKED/INDETERMINATE`;
- known blocker precedence while retaining unknown trace;
- responsibility-collision mechanics;
- consumable state model;
- Knowledge Delta proposal-only semantics;
- `READY != AUTHORIZED`;
- no persistence/network/runtime/provider/model/Human-authority side effects.

## Authority consequence

```text
Candidate 4311912303cde089e165c9fa6bdd803d3b402918:
REWORK REQUIRED / NOT ACCEPTED

Corrective implementation:
REQUIRES SEPARATE HUMAN AUTHORITY

Human technical acceptance:
NOT AUTHORIZED

Slice 2.5 closure:
NOT AUTHORIZED

Production wiring:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project execution:
NOT AUTHORIZED
```

**No broad redesign is authorized or required.**
