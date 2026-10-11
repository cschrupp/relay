# Relay — Slice 1.9 Design Revision 1 — Rework 2 Addendum

**Document class:** Lockable design record  
**Status:** LOCKED / PROPOSED FOR INDEPENDENT DESIGN RE-REVIEW  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Design authority:** RLY-S19-DESIGN-AUTH-001 — AUTHORIZED  
**Prior design:** 47af7b62a1d02f0224cc9a5c696898e8302bff56  
**Rework 1:** 731da541dbbae49ee890736eba9393e5d223b226  
**Prior evaluation:** RLY-S19-DESIGN-EVAL-002 — REVISE  
**Precedence:** This addendum is normative where it changes Revision 1 or Rework 1.

## 1. Rework scope

This addendum resolves only:

~~~text
F004 — one path-choice decision has multiple proposed outcomes,
       while Revision 1 modeled proposed_state as singular
~~~

No authority or implementation scope changes.

## 2. RW2-D01 — proposed_outcomes replaces singular proposed_state

Revision 1 D04 and D19 are amended.

DecisionCard now contains:

~~~text
DecisionCard
    decision: PendingDecisionRef
    title
    why_required
    current_state
    proposed_outcomes: tuple[DecisionProposedOutcome, ...]
    choices: tuple[DecisionChoice, ...]
    components
    evidence_summary
    evaluation_summary
    risks
    unknowns
    blocking_findings
    consequences
    governance_requirements
    source_refs
    completeness
    explicit_non_authority
    question_kinds
~~~

Define:

~~~text
DecisionProposedOutcome
    gate_ref
    target_phase
    label
~~~

proposed_outcomes is non-empty and deterministically ordered by:

~~~text
(gate_id, gate_revision, target_phase.value)
~~~

No singular DecisionCard.proposed_state remains in the implementation contract.

## 3. RW2-D02 — Per-kind cardinality

For:

~~~text
GATE_AUTHORIZATION
GATE_APPROVAL
TECHNICAL_ACCEPTANCE
~~~

proposed_outcomes contains exactly one item corresponding to the exact governed gate.

For:

~~~text
GATE_PATH_CHOICE
~~~

proposed_outcomes contains exactly one item for every exact current eligible HUMAN_CHOICE gate in eligible_choice_gate_refs.

Each proposed outcome carries that immutable gate revision's exact target_phase.

The outcome set and the eligible choice-ref set must identify the same gates exactly.

Mismatch is an integrity error, not a partial card.

## 4. RW2-D03 — PROPOSED_STATE component meaning

The component kind remains named:

~~~text
PROPOSED_STATE
~~~

for compatibility with Revision 1's component vocabulary.

Its semantic meaning is now:

~~~text
the complete exact set of governed outcome states
available under this Human decision
~~~

For single-outcome decisions, the set has one member.

For GATE_PATH_CHOICE, all eligible outcomes are required. Omitting one current eligible choice makes the component MISSING_REQUIRED / INCOMPLETE; unresolved target identity is UNKNOWN; stale gate revision is STALE or an integrity error under existing semantics.

## 5. RW2-D04 — Q&A and UI semantics

For single-outcome decisions:

~~~text
Current state -> proposed outcome
~~~

is valid.

For GATE_PATH_CHOICE, the interface must render:

~~~text
Current state -> choose one of:
    <exact gate / exact target>
    <exact gate / exact target>
    ...
~~~

WHAT_WOULD_CHANGE returns the complete ordered outcome set and does not imply that one outcome has already been selected.

WHAT_IF_APPROVED is not used to collapse a path-choice decision into a preselected route. Path-choice consequences are expressed per candidate choice, bound to the exact DecisionChoice.

If a current path choice is RECORDED_REVISABLE, the card identifies the currently recorded selected gate separately from the complete available outcome set.

## 6. RW2-D05 — Digest relationship

Rework 1's DecisionBasisIdentityV1 remains unchanged.

For GATE_PATH_CHOICE:

~~~text
target_phase = null
eligible_choice_gate_refs = complete sorted exact choice set
~~~

is intentional.

Because each HandoverGate revision is immutable and gate_id + gate_revision identifies its exact target_phase, the digest need not duplicate target phases.

The projector must verify each eligible_choice_gate_ref resolves to exactly one current HandoverGate with HUMAN_CHOICE policy before constructing proposed_outcomes.

## 7. RW2-D06 — Additional tests

Add:

- every single-outcome card has exactly one proposed_outcome;
- path-choice card has one proposed_outcome per exact eligible_choice_gate_ref;
- proposed_outcome ordering is deterministic;
- eligible choice refs and proposed outcome refs are identical sets;
- path-choice UI uses "choose one of" semantics;
- WHAT_WOULD_CHANGE lists all available exact outcomes;
- recorded current path choice is displayed separately from the available outcome set;
- no implementation field named singular proposed_state remains.

## 8. Finding disposition

~~~text
F004:
RESOLVED by RW2-D01 through RW2-D06
~~~

All Revision 1 + Rework 1 decisions not explicitly amended remain normative.

## 9. State

~~~text
Slice 1.9:
OPEN

Combined design subject:
Revision 1 + Rework 1 + Rework 2

Design:
REWORK COMPLETE / SUBMITTED FOR INDEPENDENT RE-REVIEW

Human design acceptance:
NOT GRANTED

Implementation:
NOT AUTHORIZED

Slice 1.10:
NOT OPEN / NOT AUTHORIZED

Phase 3:
NOT AUTHORIZED

Real-project agent execution:
NOT AUTHORIZED
~~~
