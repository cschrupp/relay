# Slice 2.5 — Independent Design Evaluation 002

**Document class:** Immutable independent design evaluation record  
**Status:** IMMUTABLE / ACCEPT  
**Date:** 2026-10-24  
**Project:** Relay  
**Slice:** 2.5 — Project State Resolution and Authority Compilation  
**Evaluation ID:** `RLY-S25-DESIGN-EVAL-002 — ACCEPT`  
**Evaluator:** Independent SOL — GPT-5.6 Sol  
**Exact corrective subject:** `b2f566d3f8ed616e3e901795858b7046aa3fa6c6`  
**Exact corrective parent:** `d46ab2ecde9f7a987feeea9937db3f36f72ba48b`  
**Design authority:** `RLY-S25-DESIGN-AUTH-001 — AUTHORIZED`  
**Prior evaluation:** `RLY-S25-DESIGN-EVAL-001 — REWORK`  
**Exact-head CI:** `40146740040 — SUCCESS`

## 1. Decision

```text
RLY-S25-DESIGN-EVAL-002 — ACCEPT
```

The exact corrective design candidate closes both findings from `RLY-S25-DESIGN-EVAL-001 — REWORK` without collateral architecture or scope expansion.

The Slice 2.5 normative design is independently accepted and is eligible for Human design acceptance.

Implementation remains unauthorized.

## 2. Exact corrective scope

PASS.

The corrective candidate is exactly one commit above the registered evaluation/governance base:

```text
base:
d46ab2ecde9f7a987feeea9937db3f36f72ba48b

candidate:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6
```

Only the three authorized paths changed:

```text
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_DESIGN.md
docs/CURRENT_BASELINE.md
.relay/registry.json
```

No production source, tests, schema, database, runtime, WorkPacket, workspace, provider/model, Phase-3, or real-project execution surface changed.

## 3. F001 — projection currentness versus authority-bearing provenance

**Disposition:** CLOSED.

Revision 2 now freezes the required distinction:

```text
canonical pointer
    -> selects the exact current registered projection
    -> does not confer authority on every claim inside it
```

The design now separates source roles precisely:

### Living summary / planning projections

They may provide:

- current navigation;
- current selection;
- descriptive state;
- references to underlying governed records.

They may not, by themselves, establish:

- Human authority;
- independent or technical acceptance;
- qualification acceptance;
- prohibition;
- responsibility ownership;
- consumption;
- another authority-bearing predicate.

### Living canonical policy

A living policy may be normative only within the exact ownership, scope, and authority granted by its accepted policy contract.

Canonical status or self-description as a policy is insufficient by itself.

### Authority-bearing predicate

An authority-bearing predicate must trace to:

```text
exact owning accepted / immutable / locked record
or
explicitly authorized external fact whose accepted contract permits it
```

A projection may summarize or point to that source but does not replace it.

The fail-closed rules are now explicit:

```text
required backing provenance absent
    -> INDETERMINATE

summary claim conflicts with exact backing record
    -> INDETERMINATE
       with contradiction retained in provenance trace

living policy claim outside accepted policy ownership/scope
    -> cannot establish predicate
    -> INDETERMINATE when predicate is required and no valid source exists
```

The exact resolution snapshot also now requires backing provenance for authority-bearing predicates summarized by a living projection.

This closes the summary-as-authority failure mode identified in EVAL-001.

## 4. F002 — active CURRENT_BASELINE contradiction

**Disposition:** CLOSED.

The active `Current planned frontier` no longer states that Slice 2.5 is proposed or unopened.

It now records, in substance:

```text
Slice 2.5:
OPEN
DESIGN AUTHORIZED
DESIGN EVAL-001 REWORK
CORRECTIVE DESIGN CANDIDATE pending disposition
IMPLEMENTATION NOT AUTHORIZED
```

This is consistent with the candidate's pre-re-review state.

The wording does not create authority or acceptance and no longer contradicts the Human opening/design authorities.

This evaluation supersedes that pending-review status in current governance state; the living baseline should now advance to reflect `RLY-S25-DESIGN-EVAL-002 — ACCEPT`.

## 5. Architecture retained unchanged

The correction does not alter the accepted architectural substance from the first review.

The following remain PASS:

- Relay is the only governance state machine;
- Human Authority is the sole authority source;
- derived project state is reconstructible and non-authoritative;
- Project State Resolver is deterministic, provenance-bearing, and fail-closed;
- Authority Compiler returns `READY / BLOCKED / INDETERMINATE` and never grants authority;
- `READY != AUTHORIZED`;
- historical evidence and current applicability remain separate;
- `REQUIRES / FORBIDS / CONSUMES / PRODUCES` remain bounded relations rather than a workflow language;
- `SUPERSEDED / REJECTED / PROHIBITED_UNLESS_REAUTHORIZED` remain distinct;
- responsibility collision is fail-closed and non-authorizing;
- Knowledge Delta remains proposal-only until accepted/promoted;
- WorkPacket remains the external governed work unit;
- RoleContract, ContextManifest, Execution Workspace, AgentRuntime, and Phase-3 ownership remain intact;
- consumption semantics prevent silent one-shot reuse;
- no independent project-state database is introduced;
- cache/projection persistence, if later implemented, must remain fully reconstructible;
- Wellplot, Tension/FEM, Seneca, and Relay dogfood scenarios remain deterministic and representable;
- no chat-history dependency is required.

## 6. Acceptance criteria A01–A28

Final independent disposition:

```text
A01  PASS
A02  PASS
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
A13  PASS
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
A26  PASS
A27  PASS
A28  PASS
```

No residual design blocker was found.

## 7. Registry and exact-head validation

PASS.

The corrective design is registered as:

```text
path:
docs/slices/SLICE_2_5_PROJECT_STATE_RESOLUTION_AND_AUTHORITY_COMPILATION_DESIGN.md

artifact class/state:
LOCKABLE_RECORD / REVIEW

revision:
2

ArtifactId:
art_d4e439de-1838-4c85-b448-a30f8d25fc31

Git blob:
d14812812374424bbff0e692ed9eca8ebd55196c

content digest:
sha256:78e97cdba7510fb6f21fe358488f1ce4900a93cddbdc32839d6650184a817afc
```

The corrective baseline is revision 160 with a new ArtifactId and valid canonical pointer.

Registry cardinality is 336 with valid ordering and canonical pointers.

Exact-head CI:

`40146740040 — SUCCESS`

All workflow quality steps succeeded, including environment sync, Ruff format, Ruff lint, Pyright, tests, and build.

The GitHub Actions Node.js / Ubuntu migration notices are runner/platform notices and do not affect the design disposition.

## 8. Final design disposition

```text
F001:
CLOSED

F002:
CLOSED

Slice 2.5 normative design:
INDEPENDENTLY ACCEPTED

Exact accepted design subject:
b2f566d3f8ed616e3e901795858b7046aa3fa6c6

Human design acceptance:
ELIGIBLE / NOT YET GRANTED

Implementation:
NOT AUTHORIZED

Production ProjectStateResolver:
NOT AUTHORIZED

Production AuthorityCompiler:
NOT AUTHORIZED

Phase 3:
NOT OPEN / NOT AUTHORIZED

Real-project autonomous execution:
NOT AUTHORIZED
```

## 9. Next legitimate gate

The next legitimate governance gate is Human design acceptance of exact design subject:

`b2f566d3f8ed616e3e901795858b7046aa3fa6c6`

Human design acceptance does not itself authorize implementation.

Any later implementation must receive separate Human implementation authority with a cohesive WorkPacket/authority boundary consistent with `RLY-GOV-AUTHWORK-GRANULARITY-001`.

**ACCEPT — SLICE 2.5 DESIGN IS ELIGIBLE FOR HUMAN DESIGN ACCEPTANCE.**
