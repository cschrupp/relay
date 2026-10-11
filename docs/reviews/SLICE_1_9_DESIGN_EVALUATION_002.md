# Slice 1.9 — Independent Design Evaluation 002

**Document class:** Immutable design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Evaluation ID:** RLY-S19-DESIGN-EVAL-002  
**Outcome:** REVISE  
**Evaluator:** GPT-5.6 Sol — independent design reviewer / governance gatekeeper

## Exact evaluated subject

~~~text
Design Revision 1:
47af7b62a1d02f0224cc9a5c696898e8302bff56

Prior evaluation:
RLY-S19-DESIGN-EVAL-001 — REVISE
commit d2a0889d35b3cc06e7dcf5375a691b57fb5f185a

Rework 1:
731da541dbbae49ee890736eba9393e5d223b226

Exact-head CI:
38151512256 — SUCCESS
~~~

The evaluated design subject is Revision 1 plus Rework 1, with Rework 1 normative where explicit.

## Prior findings

~~~text
F001 exact digest/CAS binding: RESOLVED
F002 pending vs recorded/revisable decision: RESOLVED
F003 per-kind completeness policy: RESOLVED
~~~

## F004 — path-choice decision has multiple proposed outcomes but the card contract remains singular

**Outcome:** REVISE

Revision 1 D04 defines:

~~~text
DecisionCard
    current_state
    proposed_state
~~~

Rework 1 correctly defines GATE_PATH_CHOICE as one decision spanning multiple eligible exact gate paths and sets the top-level target_phase in its basis identity to null.

At the same time, Rework 1's component matrix requires PROPOSED_STATE for GATE_PATH_CHOICE.

A Human path choice therefore has no single truthful proposed state before the choice is made.

Required correction:

- replace or normatively override the singular proposed_state field with an exact collection of proposed outcomes;
- for non-choice decisions, the collection has exactly one outcome;
- for GATE_PATH_CHOICE, the collection contains one outcome for each exact eligible gate ref and its target phase;
- deterministic ordering is required;
- Q&A and UI must say "one of these outcomes" rather than imply one already-selected proposed state;
- the PROPOSED_STATE component remains required but is satisfied by the complete exact outcome set.

## Passed areas

All authority boundaries and all other Revision 1 + Rework 1 decisions pass re-review, including exact CAS digest semantics, decision-state semantics, component applicability, deterministic Q&A, no model/provider execution, no persistence migration, no dependency changes, and downstream Slice ownership.

## Decision

~~~text
RLY-S19-DESIGN-EVAL-002 — REVISE
~~~

This is a single bounded design correction. No new Human Authority is required. Implementation remains unauthorized.
