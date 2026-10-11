# Relay — Slice 1.9 Independent Implementation Evaluation 002

**Document class:** Immutable implementation evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Evaluation ID:** `RLY-S19-EVAL-002`  
**Outcome:** `REWORK`  
**Evaluator:** GPT-5.6 Sol

## Exact evaluated subject

```text
Repository: cschrupp/relay
Implementation authority: RLY-S19-IMPL-AUTH-001 — AUTHORIZED
Authorized implementation baseline: a3b489bb4682314a706f66c57ee0bc1bb917542c
Initial implementation candidate: becf1c80965d8c7c36cb081a3bfa1e66b074c13a
Prior evaluation: RLY-S19-EVAL-001 — REWORK
Rework start: 6b2565559223cee8f0b08e9299d26eba020feac4
Evaluated successor candidate: 707531ebea574a014cbb1c60f8d6714484a7205e
Accepted combined design subject: 03d6efecf9ad4aaec0c5967b9486650399d0a492
Ahead / behind authorized baseline: 3 / 0
Ahead / behind rework start: 1 / 0
Exact-head CI: 38169287770 — SUCCESS
```

The remote implementation branch was independently verified at the exact successor SHA. The successor is one commit above the required rework start, and the original candidate plus RLY-S19-EVAL-001 remain preserved in ancestry.

## Independent verification

```text
bounded rework changed files: 6
unauthorized migration/dependency/workflow/persistence changes: NONE
RLY-S19-EVAL-001 edited: NO
exact-head CI binding: PASS
Ruff format/lint: PASS
Pyright: PASS — 0 errors / 0 warnings / 0 informations
full pytest: PASS — 678 passed
build: PASS
```

## Prior finding disposition

### F001 — PARTIALLY RESOLVED

The successor correctly replaces representative-gate completeness with per-gate path-choice projection and merges all eligible gates' components, source refs, evidence statements, risks, blockers, unknowns, and governance requirements. Heterogeneous path requirements now affect completeness.

However, the complete Human-facing path-choice readout still has residual defects described below under F005-F007.

### F002 — RESOLVED IN PRODUCTION

Artifact source refs are now explicit, ordinary gate artifact applicability is projected, and technical acceptance receives the exact HandoverGate/current artifact basis. Required technical artifacts are no longer unconditionally marked NOT_APPLICABLE.

### F003 — RESOLVED IN PRODUCTION / REQUIRED PROOF INCOMPLETE

`SliceDetail.decision_support` is now required with no default, and `board.service.slice_detail()` explicitly supplies it.

The rework instruction also required a model-level test proving omission fails validation. No such test is present. This proof must be added before acceptance.

### F004 — RESOLVED IN PRODUCTION / REQUIRED PROOF INCOMPLETE

`_decision_why(...)` now distinguishes PENDING_REQUIRED from RECORDED_REVISABLE, requires the exact HUMAN_DECISION source for revisable state, identifies the current decision, and explains replacement availability.

Current REJECT, current path choice, and technical APPROVE are covered. The explicit rework proof requested current APPROVE and technical REJECT as well; those symmetric cases are not directly tested and must be added.

# New / residual findings

## F005 — BLOCKING — GATE_PATH_CHOICE consequence text is still the authorization consequence

`_build_gate_card(...)` constructs consequences as:

```text
if kind == GATE_APPROVAL:
    approval/rejection consequence
else:
    authorization-grant consequence
```

`GATE_PATH_CHOICE` therefore falls into the authorization branch. The merged path card keeps the first per-gate card's `consequences` unchanged.

The resulting Human Decision Card says, in substance, that a path choice records an authorization grant, which is false.

The accepted implementation contract requires:

```text
CHOOSE_PATH:
records exact selected gate choice and reevaluates;
does not execute handover by itself.
```

This is a Decision Support correctness defect: the UI presents incorrect consequences for the Human choice being considered.

### Required correction

Give GATE_PATH_CHOICE its own deterministic consequence statement matching existing CHOOSE_PATH semantics. Bind it to the complete path-choice source basis, not a representative gate only. Add an exact test that a path-choice card never contains the authorization-grant consequence and does contain the CHOOSE_PATH consequence.

## F006 — MAJOR — WHAT_EVIDENCE_EXISTS can hide missing path requirements when some evidence is present

`answer_decision_question(... WHAT_EVIDENCE_EXISTS ...)` uses:

```text
card.evidence or <EVIDENCE component summaries>
```

For a multi-path card where one eligible path has current required evidence and another eligible path has missing required evidence, `card.evidence` is non-empty. The answer therefore returns only the present evidence statements and omits the merged EVIDENCE component's MISSING_REQUIRED/applicability state.

The accepted Q&A contract requires WHAT_EVIDENCE_EXISTS to return the exact current required/available evidence **and applicability state**, and RLY-S19-EVAL-001 explicitly required this question to reflect the complete choice set.

### Required correction

Make WHAT_EVIDENCE_EXISTS include both current evidence statements and the EVIDENCE component applicability/summary when relevant. A mixed present/missing multi-path basis must disclose both the present evidence and the missing required evidence and must remain deterministic.

Add a test with at least two path gates where one required evidence ID is present and another required evidence ID is missing.

## F007 — MAJOR — Path-choice component merge collapses OPTIONAL_PRESENT into NOT_APPLICABLE

The accepted component matrix defines AUTHORITY_BASIS for GATE_PATH_CHOICE as optional (`O`), represented by the per-gate projector as `OPTIONAL_PRESENT` with `required=False`.

The merge logic currently says that when no merged component member is required:

```text
applicability = NOT_APPLICABLE
freshness = NOT_APPLICABLE
```

This converts a genuinely optional-present authority basis into NOT_APPLICABLE and loses an accepted semantic distinction.

### Required correction

Preserve optional applicability during merge. If no member is required but one or more current members are OPTIONAL_PRESENT, the merged component must remain OPTIONAL_PRESENT/CURRENT. Use NOT_APPLICABLE only when every constituent component is NOT_APPLICABLE.

Add a path-choice test asserting AUTHORITY_BASIS remains OPTIONAL_PRESENT and does not affect completeness.

## Required proof completion

Before the next re-review, add the tests explicitly required by RLY-S19-EVAL-001 but still absent:

```text
SliceDetail omission of decision_support -> validation failure
current APPROVE -> RECORDED_REVISABLE why_required exact decision source
current technical REJECT -> RECORDED_REVISABLE why_required exact decision source
```

Preserve the already-passing current REJECT, path-choice, and technical-APPROVE coverage.

## Rework boundary

This remains bounded implementation rework under RLY-S19-IMPL-AUTH-001. No new Human implementation authority or design revision is required.

Do not modify DecisionBasisIdentityV1/digest semantics, Human mutation CAS/services, persistence/schema, dependencies, workflows, lifecycle/governance semantics, Q&A architecture, or downstream Slice authority.

Preserve both evaluated implementation candidates and both evaluation records as immutable history.

## Decision

```text
RLY-S19-EVAL-002 — REWORK
```

Candidate `707531ebea574a014cbb1c60f8d6714484a7205e` is not yet eligible for Human technical acceptance. The remaining work is narrow and implementation-local.