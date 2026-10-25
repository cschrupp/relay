# Slice 2.5 — Independent Design Evaluation 001

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE / REWORK  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Evaluation ID:** `RLY-S25-DESIGN-EVAL-001 — REWORK`  
**Evaluator:** Independent SOL — GPT-5.6 Sol  
**Exact subject:** `1e64b6b9b7c9e2e9e30e788607e9591f1eea456e`  
**Exact subject parent:** `029712fd31f79ee75f4b85e3cdfbc41a85d4770f`  
**Authority:** `RLY-S25-DESIGN-AUTH-001 — AUTHORIZED`  
**Exact-head CI:** `40143794167 — SUCCESS`

## 1. Disposition

```text
RLY-S25-DESIGN-EVAL-001 — REWORK
```

The candidate is architecturally strong and substantially satisfies the bounded Slice 2.5 design authority.

Two narrow findings block design acceptance:

1. the canonical-source model does not yet distinguish **current projection selection** from **authority-bearing provenance** strongly enough; and
2. the submitted living `CURRENT_BASELINE` contains a contradictory active frontier line that still says Slice 2.5 is `PROPOSED / NOT OPEN / NOT AUTHORIZED`.

No broad redesign is required.

No implementation authority is justified.

## 2. Lineage, scope, registry, and CI

PASS.

The candidate is exactly one commit above the authorized design-state parent:

```text
parent:
029712fd31f79ee75f4b85e3cdfbc41a85d4770f

candidate:
1e64b6b9b7c9e2e9e30e788607e9591f1eea456e
```

Changed paths are exactly:

```text
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_DESIGN.md
docs/CURRENT_BASELINE.md
.relay/registry.json
```

The normative design blob is:

`a93bbafafbd1a6e3f1b6cd6ab542ed6be955a73f`

The design is registered as:

```text
LOCKABLE_RECORD / REVIEW
revision 1
DESIGN CANDIDATE — UNACCEPTED / IMPLEMENTATION NOT AUTHORIZED
```

Registry ordering and canonical pointers pass.

Exact-head CI `40143794167` is green, including Ruff format, Ruff lint, Pyright, tests, and build.

## 3. Positive architectural findings

### P001 — Relay remains the only governance state machine

PASS.

The candidate explicitly keeps the project-state graph/projection derived and reconstructible, not independently authoritative.

It does not introduce a second task database, workflow engine, planner, graph authority, or orchestration queue.

### P002 — Human Authority boundary

PASS.

The candidate structurally preserves:

```text
READY != AUTHORIZED
authority candidate != authority
Qualification PASS != authority
evidence != authority
```

The resolver/compiler prepare a deterministic candidate; Human Authority remains the grant source.

### P003 — WorkPacket ownership

PASS.

Slice 2.3 WorkPacket / ContextManifest remain the external governed work unit and context transport.

Slice 2.5 gates/supplies the existing path and does not create a parallel task identity or sidecar authority format.

### P004 — Evidence applicability / invalidation

PASS.

The candidate cleanly separates:

```text
historical result
from
current applicability
```

with deterministic:

```text
APPLICABLE
NOT_APPLICABLE
INDETERMINATE
```

A historical PASS remains historical PASS when its exact executable/runtime/provider/environment/etc. envelope no longer matches.

This directly closes the stale-evidence failure mode that motivated the Slice.

### P005 — Requirement relations

PASS.

`REQUIRES`, `FORBIDS`, `CONSUMES`, and `PRODUCES` are bounded domain relations, not a generic workflow language.

Unknown relation kinds fail closed.

### P006 — Negative decisions

PASS.

`SUPERSEDED`, `REJECTED`, and `PROHIBITED_UNLESS_REAUTHORIZED` are materially distinct and carry exact scope/provenance/reauthorization semantics.

The design correctly avoids treating every superseded subject as a universal prohibition while preventing rejected/prohibited subjects from silently returning.

### P007 — Responsibility collision

PASS.

The candidate does not infer "no collision" from absence of a text match.

`NO_COLLISION` requires a complete normalized responsibility-key set and a complete accepted owner set.

Unresolved ownership is `INDETERMINATE`; a true competing owner blocks ordinary compilation pending architecture authority.

### P008 — Consumable semantics

PASS at design level.

The model distinguishes:

```text
AVAILABLE
RESERVED
CONSUMED
INDETERMINATE
```

and compilation itself does not reserve or consume.

The requirement for atomic reservation at Human grant is a legitimate future integration requirement needed to prevent concurrent double grant. It does not authorize implementation or operational mutation under this design authority.

### P009 — Resolver and compiler

PASS.

The deterministic aggregation rule is coherent:

```text
known hard blocker
    -> BLOCKED

otherwise unresolved required fact
    -> INDETERMINATE

otherwise
    -> READY
```

Known blockers do not erase unknowns from the trace.

Only `READY` produces a candidate eligible for Human review.

### P010 — Knowledge Delta

PASS.

Knowledge Delta is proposal-only and cannot self-promote from worker/evaluator/runtime output into accepted durable state.

### P011 — Reconstruction / persistence

PASS.

The normative initial model requires no durable project-state database.

Any future cache must be fully reconstructible from exact canonical inputs and cannot accept authoritative direct edits.

### P012 — Dogfood scenarios

PASS.

The design concretely represents the required failure modes:

- Wellplot environment qualification -> smoke -> independent smoke acceptance -> live confirmation;
- stale smoke applicability;
- second smoke-harness responsibility collision;
- rejected second semantic engine/fallback path;
- campaign namespace consumption;
- Tension/FEM one-shot/attempt/oracle applicability;
- Seneca backend/environment invalidation;
- Relay predecessor/closure/current-baseline reconstruction without chat history.

The scenarios are operational enough to become deterministic implementation tests.

## 4. F001 — living projection currentness is conflated with authority-bearing provenance

**Severity:** BLOCKING / NARROW ARCHITECTURAL CLARIFICATION

The candidate correctly says canonical records are pinned through exact registry pointers, but §4.2 currently states:

```text
Only these source classes can establish state:

1. Current canonical projections ...
```

and describes a non-pointer revision as not being "current authority."

That formulation is too broad.

Relay's accepted documentation governance distinguishes:

```text
historical authority
    immutable

current truth
    living projections
```

and separately freezes:

```text
documentation existence does not authorize engineering work
authorization remains an explicit Human Authority decision
```

A canonical pointer establishes **which projection revision is current**. It does not make every claim inside every living projection an authority-bearing fact.

This distinction matters because living canonical artifacts include both:

- genuinely normative living policies, whose owning accepted policy contract may make their exact current bytes normative; and
- summary/planning projections such as Current Baseline, Build Plan, and Product Proposal, which may describe accepted authority/acceptance/evidence but must not become the sole provenance for those authority-bearing facts.

Without an explicit rule here, Slice 2.5 could reintroduce the very failure it is designed to eliminate:

```text
CURRENT_BASELINE says "smoke accepted"
        ↓
resolver treats projection text as accepted state
        ↓
underlying immutable smoke acceptance missing
        ↓
authority candidate incorrectly becomes READY
```

### Required correction

Clarify the source model with semantics equivalent to:

```text
canonical pointer
    -> proves which registered revision is current
    -> does not by itself prove the authority semantics of each claim

living canonical policy
    -> may be normative only within the exact ownership/authority
       granted to that policy contract

living summary/planning projection
    -> may provide current selection/navigation/descriptive state
    -> may not be the sole provenance for Human authority,
       technical acceptance, independent evaluation result,
       qualification acceptance, prohibition,
       responsibility ownership, consumption,
       or another authority-bearing predicate

authority-bearing predicate
    -> must trace to the exact owning accepted/immutable/locked record,
       or to an explicitly authorized external fact whose accepted contract
       allows it

projection claim without required backing provenance
    -> INDETERMINATE
       or conflict if contradictory backing records exist
```

The design should also state that a summary projection can point to or summarize historical authority without replacing the exact historical authority record.

This is a clarification of §4.2 / §4.5 / §6 source resolution, not a new architecture.

It strengthens A01 and A02 and preserves the accepted repository/documentation contract.

## 5. F002 — CURRENT_BASELINE contains contradictory active Slice 2.5 state

**Severity:** BLOCKING / NARROW PROJECTION REWORK

The submitted `CURRENT_BASELINE.md` revision 159 correctly states near its top:

```text
Slice 2.5:
OPEN / DESIGN AUTHORIZED / IMPLEMENTATION NOT AUTHORIZED
```

and records the normative design candidate as produced / pending independent review.

However the same living projection later contains an active section titled:

```text
## Current planned frontier
```

whose `Then:` line still says:

```text
2.5 Project State Resolution & Authority Compilation
— PROPOSED / NOT OPEN / NOT AUTHORIZED
```

This is not labeled as historical state. It is an active current-frontier contradiction inside the canonical current-baseline projection.

The contradiction is particularly material for Slice 2.5 because the candidate itself proposes using current canonical projections as resolver inputs.

### Required correction

Update that active frontier statement to the exact current state, at minimum:

```text
2.5 Project State Resolution & Authority Compilation
— OPEN / DESIGN AUTHORIZED / DESIGN CANDIDATE UNDER REVIEW / IMPLEMENTATION NOT AUTHORIZED
```

After the rework evaluation is recorded, the wording may instead state that independent design evaluation is REWORK and corrective design is pending.

Do not rewrite clearly historical narrative merely because it contains old statuses.

## 6. Acceptance-criteria disposition

Current independent disposition:

```text
A01  REWORK — source authority/provenance distinction needs F001
A02  REWORK — projection/non-authority boundary needs F001

A03  PASS
A04  PASS
A05  PASS
A06  PASS
A07  PASS
A08  PASS
A09  PASS
A10  PASS
A11  PASS
A12  PASS
A13  PASS subject to F001 source correction
A14  PASS
A15  PASS
A16  PASS
A17  PASS
A18  PASS
A19  PASS
A20  PASS
A21  PASS
A22  PASS
A23  PASS
A24  PASS
A25  PASS
A26  PASS subject to F001 source correction
A27  PASS
A28  PASS
```

F002 is a candidate-package/current-projection defect rather than a defect in A03–A28 design semantics.

## 7. Required rework boundary

The existing Human design authority remains sufficient for this narrow corrective rework:

`RLY-S25-DESIGN-AUTH-001 — AUTHORIZED`

No new Human design authority is required because the correction does not expand the authorized objective or surface.

Preferred mutable surface:

```text
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_DESIGN.md
docs/CURRENT_BASELINE.md
.relay/registry.json
```

The immutable opening and design-authority records must not be rewritten.

No source code, tests, schema, database, runtime, WorkPacket, workspace, provider/model, Phase-3, or real-project execution changes are authorized.

The design should advance as a new REVIEW revision / new ArtifactId under the existing repository contract.

## 8. Re-review gate

After F001 and F002 are corrected:

1. produce one exact corrective design candidate;
2. validate registry transition/digests/pointers;
3. run full repository validation and exact-head CI;
4. STOP for independent SOL design re-review.

If the two findings are closed without collateral scope expansion, the design should become Human-design-acceptance eligible.

```text
Slice 2.5:
OPEN

Design authority:
AUTHORIZED

Design candidate:
REWORK REQUIRED — NARROW

Implementation:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED
```

**REWORK — TWO NARROW FINDINGS; NO BROAD REDESIGN REQUIRED.**
