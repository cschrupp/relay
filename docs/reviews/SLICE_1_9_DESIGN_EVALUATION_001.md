# Slice 1.9 — Independent Design Evaluation 001

**Document class:** Immutable design evaluation record  
**Status:** IMMUTABLE  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Evaluation ID:** RLY-S19-DESIGN-EVAL-001  
**Outcome:** REVISE  
**Evaluator:** GPT-5.6 Sol — independent design reviewer / governance gatekeeper

## Exact evaluated subject

~~~text
Opening:
RLY-S19-OPEN-001 — OPEN
commit 5bf25378b15955b6e21252ec3f9cc91dcf7192d7

Design authority:
RLY-S19-DESIGN-AUTH-001 — AUTHORIZED
commit 8ea33bb01c94dd0fc7d24185702ad4f98ed1b687

Design Revision 1:
47af7b62a1d02f0224cc9a5c696898e8302bff56

Canonical parent:
7e690f9fe22b34226fff2d3364d1ed94b91dc9f7

Exact-head CI:
38150799304 — SUCCESS
~~~

## Overall assessment

Revision 1 has the correct architecture direction: Decision Support remains a derived read model over existing Relay authority, uses the existing same-snapshot board seam, preserves current Human/manual-evaluation mutation services, avoids new persistence and dependencies, keeps Q&A deterministic/read-only, and respects Slice 1.8 / 1.10 / 2.2–2.4 ownership.

Three bounded contract defects remain before Human design acceptance eligibility.

## F001 — basis_digest is not bound to an exact frozen CAS payload

**Outcome:** REVISE

D02 says basis_digest is derived from deterministic canonical serialization of the exact decision-basis identity and must change whenever the exact basis changes, but Revision 1 does not freeze:

- the complete hashed field set;
- the canonical serialization algorithm;
- how heterogeneous HumanActionBasis versus ManualEvaluationActionBasis inputs are represented;
- current approval / current choice identities required by existing mutation routes.

Existing Relay mutation semantics are stricter than the listed PendingDecisionRef fields. HumanActionBasis includes evaluation_record_id, lifecycle_revision, governance_revision, gate refs, current approval IDs, current choice ID, result identity, and manual-evaluation identity. Technical-decision forms additionally bind the exact current approval decision identity.

A digest that omits any actionable CAS component may remain unchanged while the mutation basis changes.

Required correction:

1. define an explicit versioned DecisionBasisIdentity payload;
2. include decision kind plus the complete exact underlying action CAS and decision-specific selector/current-decision identity;
3. define canonical JSON bytes exactly;
4. SHA-256 those bytes;
5. test that every mutation-relevant basis change rotates the digest while non-basis presentation changes do not.

The digest remains navigation/freshness identity only and does not replace existing POST CAS validation.

## F002 — action availability is not equivalent to a pending Human decision

**Outcome:** REVISE

D03 derives Decision Cards from existing actions and calls the section Pending Human Decisions.

Current accepted services intentionally keep some decision controls available after a current decision exists:

- APPROVE / REJECT remain projected for an exact gate when a current HumanApprovalDecision exists, enabling revision of that decision;
- CHOOSE_PATH can remain available for alternate paths after a current choice exists;
- TECHNICAL_ACCEPT / TECHNICAL_REJECT remain available while an accepted evaluation is current, including when a current technical Human decision exists before promotion.

Therefore:

~~~text
action exists != decision is pending
~~~

Required correction:

- define explicit decision state, at minimum PENDING_REQUIRED versus RECORDED_REVISABLE;
- bind and display the current recorded Human decision when present;
- ensure why_required does not falsely state a Human decision is missing when the card actually represents a revisable current decision;
- define whether the UI section is Human Decisions rather than always Pending Human Decisions, or filter pending cards and separately expose revisable current decisions;
- preserve current decision identity in digest/freshness semantics.

## F003 — completeness has no frozen per-kind required-component policy

**Outcome:** REVISE

D05 defines component vocabulary and D06 defines COMPLETE / INCOMPLETE / UNKNOWN / STALE, but no rule maps each supported decision kind to its required, optional, or inapplicable components.

Without that matrix, implementation would have to invent policy while computing RELAY_DECISION_BASIS_COMPLETE.

Required correction:

Freeze a deterministic component-requirement matrix for:

~~~text
GATE_AUTHORIZATION
GATE_APPROVAL
GATE_PATH_CHOICE
TECHNICAL_ACCEPTANCE
~~~

For each component, specify the default requirement state and the exact existing governed condition that can alter applicability.

The matrix must not require GovernanceProfile or Protected Verification Asset data that the current product does not authoritatively possess. Those remain UNKNOWN or explicitly unavailable where applicable and must not make every current M0 decision permanently incomplete unless current accepted policy actually requires them.

## Passed areas

~~~text
authority boundary: PASS
Slice 1.8 semantic consumption: PASS
Decision Support non-authority: PASS
same-snapshot direction: PASS
existing mutation CAS preserved: PASS
no parallel state machine: PASS
typed source/provenance direction: PASS
fact vs evaluator judgment separation: PASS
risk non-invention: PASS
deterministic consequence boundary: PASS
structured Q&A / no LLM: PASS
Q&A read-only boundary: PASS
CSRF / HUMAN actor preservation: PASS
GovernanceProfile fail-honest boundary: PASS
clarity persistence deferral: PASS
telemetry collection deferral: PASS
server-rendered accessibility direction: PASS
no migration: PASS
no dependency change: PASS
bounded implementation surface: PASS
integrity-error preservation: PASS
Slice 1.10 / 2.2 / 2.3 / 2.4 ownership: PASS
Phase 3 non-authority: PASS
exact-head CI: PASS
~~~

## Decision

~~~text
RLY-S19-DESIGN-EVAL-001 — REVISE
~~~

The findings are bounded design-contract corrections. No new Human Authority is required under RLY-S19-DESIGN-AUTH-001. Implementation remains unauthorized.
