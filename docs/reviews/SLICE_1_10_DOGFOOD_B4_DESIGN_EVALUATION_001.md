# Slice 1.10 Dogfood B4 — Relay Dogfood Acceptance — Design Evaluation 001

**Document class:** Immutable independent design evaluation  
**Status:** IMMUTABLE  
**Date:** 2026-10-20  
**Project:** Relay  
**Increment:** B4 — Relay Dogfood Acceptance  
**Record:** `RLY-S110-DOGFOOD-B4-DESIGN-EVAL-001`  
**Outcome:** `ACCEPT`

## Evaluated subject

```text
B4 design authority:
RLY-S110-DOGFOOD-B4-DESIGN-AUTH-001 — AUTHORIZED

Starting SHA:
ed74c7118d6bdf6587bbcfe6598da307103ad154

Design candidate:
9b274eda204dac30da51181f2c1de25cf7237010

Changed path:
docs/slices/SLICE_1_10_DOGFOOD_B4_RELAY_DOGFOOD_ACCEPTANCE_DESIGN.md

Exact-head CI:
PASS
```

## Independent review

The candidate satisfies the B4 design authority and preserves the accepted B3
state/authority boundaries.

### Cold-start contract

The design freezes a reviewable fresh-operator boundary:

- no ChatGPT conversation history or assistant summaries;
- no hidden answer key or evaluator coaching;
- clean pinned checkout;
- explicit read-only operational DB;
- normal repository/product/read-model surfaces only;
- sealed operator answers before evaluator comparison;
- transcript and inspected-source inventory sufficient to review custody.

The design does not claim to prove private memory; it instead makes prohibited
context access an explicit run-invalidating condition and records observable
session custody.

### Axis decision

Axis A — current-state recovery — is correctly normative.

Axis B — disposable B0-F/B1/B2 replay — is supporting evidence only and remains
separately authorized if ever run.

This is aligned with B4's actual success claim: Relay must recover its accepted
current state without conversation reconstruction, not redundantly prove the
already accepted B0-F/B1/B2 implementation chain.

### Ten-question source matrix

The exact Q1–Q10 contract is sufficiently deterministic.

It correctly separates:

- operational DB truth for current Project/Slice/lifecycle/situation;
- accepted immutable governance records for authority/decision history;
- registry-resolved canonical living projections for roadmap/current governance;
- code/help as interpretation of product behavior only;
- prohibited conversation context.

The matrix also correctly distinguishes:

- adoption/T1 context from post-T1 current state;
- lifecycle from authority;
- planned/proposed work from authorized work;
- explicit blockers from absence of recorded blockers;
- explicit pending Human decisions from merely available Human controls.

All ten questions are mandatory.

### CURRENT / NEXT / LATER / BLOCKED

The candidate uses the existing read models and canonical repository records
without creating a new persisted four-column roadmap.

The truth rules are appropriately conservative:

- CURRENT comes from the pinned operational state;
- NEXT requires exact current authority or is reported not determinable;
- LATER comes from current canonical roadmap context and remains non-authority;
- BLOCKED requires explicit current lifecycle/gate evidence.

Historical T1 orientation cannot overwrite the post-B3 projection.

### Read-only operator surface

The design correctly identifies a real current product limitation:

- `relay-board` is not suitable for direct B4 use against the live DB because
  the normal database opener is writable/WAL-configuring and the web app exposes
  mutation routes;
- `relay-bootstrap` is not a current-state inspection surface.

The proposed tiny read-only harness is technically viable and remains within the
design authority because it adds no semantics or authority.

The existing `project_board` and `slice_detail` services accept a
caller-owned `RelayDatabase` connection. A separately pinned wrapper can
construct that connection from a SQLite URI opened `mode=ro`, set
`query_only`, and invoke the existing read models without using Relay's
writable `open_database` setup.

This must be separately prepared/reviewed if used; it is not authorized by the
design acceptance itself.

### Deterministic scoring

The PASS / FAIL / INDETERMINATE rules are objective and fail closed.

Overall B4:

- PASS only if all ten mandatory questions pass and custody/read-only controls
  are valid;
- FAIL if any mandatory question fails;
- INDETERMINATE if no question fails but at least one remains indeterminate;
- custody/control violation invalidates the run and cannot produce PASS.

The design appropriately treats missing durable truth differently from operator
guessing or a product surface hiding existing durable truth.

### Evidence and mutation boundary

The evidence contract is sufficient for independent result review and includes
the exact operator answers, sources, commands/surfaces, transcript/custody,
registry references, DB before/after digest, and derived orientation.

The real operational DB remains read-only throughout B4.

No lifecycle transition, Slice mutation, B4 state, successor Slice, 2.2 design
state, execution/evaluation/promotion state, or repair is permitted inside the
run.

### Closeout

A successful B4 run still requires:

1. independent result review;
2. explicit Human result acceptance.

Only then does Slice 2.2 design become eligible to open.

B4 acceptance itself does not authorize Slice 2.2 design or implementation.

## Non-blocking observation

The need for a tiny read-only projection harness reflects a product-surface
ergonomics gap: the existing public `relay-board` launcher is not appropriate
for this read-only live-state acceptance run.

That is not a B4 design defect because the design authority explicitly allowed
a minimal read-only harness exposing existing semantics. B4 execution may itself
determine whether this gap is acceptable for the product success criterion or
requires a bounded product-surface correction.

## Independent disposition

No blocking discrepancy was found against
`RLY-S110-DOGFOOD-B4-DESIGN-AUTH-001`.

```text
RLY-S110-DOGFOOD-B4-DESIGN-EVAL-001 — ACCEPT

B4 design:
INDEPENDENTLY ACCEPTED
HUMAN DESIGN ACCEPTANCE PENDING

B4 execution:
NOT AUTHORIZED

Slice 2.2 design:
NOT OPEN / NOT AUTHORIZED
```
