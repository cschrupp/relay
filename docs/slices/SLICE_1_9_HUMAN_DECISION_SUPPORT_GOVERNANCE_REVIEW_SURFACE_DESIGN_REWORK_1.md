# Relay — Slice 1.9 Design Revision 1 — Rework 1 Addendum

**Document class:** Lockable design record  
**Status:** LOCKED / PROPOSED FOR INDEPENDENT DESIGN RE-REVIEW  
**Date:** 2026-10-11  
**Project:** Relay  
**Slice:** 1.9 — Human Decision Support and Governance Review Surface  
**Design authority:** RLY-S19-DESIGN-AUTH-001 — AUTHORIZED  
**Prior design:** 47af7b62a1d02f0224cc9a5c696898e8302bff56  
**Prior evaluation:** RLY-S19-DESIGN-EVAL-001 — REVISE  
**Precedence:** This addendum is normative where it changes Design Revision 1.

## 1. Rework scope

This addendum resolves exactly:

~~~text
F001 — exact basis_digest / CAS binding
F002 — pending versus already-recorded/revisable Human decisions
F003 — per-kind component applicability/completeness policy
~~~

No implementation authority is created.

## 2. RW1-D01 — Exact versioned DecisionBasisIdentityV1

Revision 1 D02 and D08 are amended.

The digest payload is an explicit non-authoritative read-model identity:

~~~text
DecisionBasisIdentityV1
    schema_version = 1
    decision_kind
    slice_id
    gate_ref
    target_phase
    human_action_basis
    decision_state
    expected_current_approval_decision_id
    expected_current_choice_decision_id
    expected_result_id
    expected_manual_evaluation_id
    eligible_choice_gate_refs
~~~

Fields not applicable to one decision kind are JSON null or the empty list as specified below. They are never silently omitted.

human_action_basis is the complete current HumanActionBasis serialized with Pydantic model_dump(mode="json"). It is required for all four Revision-1 Decision Card kinds because the existing AUTHORIZE, APPROVE/REJECT, CHOOSE_PATH, and TECHNICAL_ACCEPT/REJECT POST commands all ultimately bind to HumanActionBasis.

This explicitly corrects Revision 1 D08: ManualEvaluationActionBasis remains authoritative for the existing ATTACH_RESULT/EVALUATE manual-evaluation controls, but those controls do not produce Revision-1 Decision Cards. TECHNICAL_ACCEPTANCE uses HumanActionBasis plus its exact result/evaluation/current-approval expectations.

### Per-kind payload

GATE_AUTHORIZATION:

~~~text
gate_ref = exact gate_id + gate_revision
target_phase = exact target
human_action_basis = complete current HumanActionBasis
decision_state = PENDING_REQUIRED
expected_current_approval_decision_id = null
expected_current_choice_decision_id = null
expected_result_id = null
expected_manual_evaluation_id = null
eligible_choice_gate_refs = []
~~~

GATE_APPROVAL:

~~~text
gate_ref = exact gate_id + gate_revision
target_phase = exact target
human_action_basis = complete current HumanActionBasis
decision_state = derived under RW1-D02
expected_current_approval_decision_id =
    exact current approval/rejection decision for that gate, else null
expected_current_choice_decision_id = null
expected_result_id = null
expected_manual_evaluation_id = null
eligible_choice_gate_refs = []
~~~

GATE_PATH_CHOICE:

~~~text
gate_ref = null
target_phase = null
human_action_basis = complete current HumanActionBasis
decision_state = derived under RW1-D02
expected_current_approval_decision_id = null
expected_current_choice_decision_id =
    exact current choice decision projected on the current basis, else null
expected_result_id = null
expected_manual_evaluation_id = null
eligible_choice_gate_refs =
    sorted exact gate_id + revision refs for every current eligible HUMAN_CHOICE option
~~~

TECHNICAL_ACCEPTANCE:

~~~text
gate_ref = exact ACCEPTED-target gate_id + gate_revision
target_phase = ACCEPTED
human_action_basis = complete current HumanActionBasis
decision_state = derived under RW1-D02
expected_current_approval_decision_id =
    exact current Human approval/rejection decision for that technical gate, else null
expected_current_choice_decision_id = null
expected_result_id = exact current result_id
expected_manual_evaluation_id = exact current manual evaluation_id
eligible_choice_gate_refs = []
~~~

Any missing field required above means no actionable current Decision Card can be produced.

## 3. RW1-D02 — Canonical digest bytes

basis_digest is computed only from DecisionBasisIdentityV1.

Canonical bytes are:

~~~python
json.dumps(
    identity.model_dump(mode="json"),
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
~~~

Digest:

~~~python
"sha256:" + hashlib.sha256(canonical_bytes).hexdigest()
~~~

Normative serialization rules:

- enum values serialize as their string values;
- tuples serialize as JSON arrays through model_dump(mode="json");
- null remains JSON null;
- eligible_choice_gate_refs are sorted by (gate_id, gate_revision);
- no timestamps, labels, prose summaries, display order, source labels, or Q&A text outside the exact identity enter the digest;
- no random ID enters the digest.

Therefore:

~~~text
same exact actionable basis -> same digest
mutation-relevant CAS change -> different digest
presentation-only wording change -> same digest
~~~

The digest is navigation/freshness identity only. Existing POST validation remains authoritative.

## 4. RW1-D03 — Decision state is explicit

Add:

~~~text
DecisionCardState:
    PENDING_REQUIRED
    RECORDED_REVISABLE
~~~

Action availability does not establish pending state.

### GATE_AUTHORIZATION

An AUTHORIZE action exists only while current evaluation requires missing/stale authorization.

State:

~~~text
PENDING_REQUIRED
~~~

### GATE_APPROVAL

If HumanActionProjection.current_approval_decisions contains the exact current gate decision bound to the current HumanActionBasis:

~~~text
RECORDED_REVISABLE
~~~

otherwise:

~~~text
PENDING_REQUIRED
~~~

### GATE_PATH_CHOICE

If current_choice is represented in the current HumanActionBasis and its selected gate remains one of eligible_choice_gate_refs:

~~~text
RECORDED_REVISABLE
~~~

otherwise:

~~~text
PENDING_REQUIRED
~~~

### TECHNICAL_ACCEPTANCE

For the exact ACCEPTED-target gate, if current_approval_decisions contains the exact current technical Human decision bound to the current HumanActionBasis:

~~~text
RECORDED_REVISABLE
~~~

otherwise:

~~~text
PENDING_REQUIRED
~~~

The current recorded decision value and decision_id are displayed when state is RECORDED_REVISABLE.

A current REJECT is still a recorded decision. It is not presented as "missing approval."

## 5. RW1-D04 — UI terminology

Revision 1 D19 is amended.

The section heading is:

~~~text
Human Decisions
~~~

not universally "Pending Human Decisions."

Each card displays:

~~~text
Decision status: Human decision required
~~~

or:

~~~text
Decision status: Current decision recorded — change remains available
~~~

according to DecisionCardState.

why_required must describe the actual state:

- PENDING_REQUIRED: why the current policy requires a Human decision now;
- RECORDED_REVISABLE: why this decision remains revisable before the governed transition and what current decision is recorded.

The UI must never claim a decision is pending solely because an action control remains available.

## 6. RW1-D05 — Complete per-kind component requirement matrix

Revision 1 D05/D06 are amended by the following deterministic M0 matrix.

Legend:

~~~text
R = required by this Decision Card policy
D = dynamically required/inapplicable from exact existing gate semantics
O = optional presentation when authoritative current material exists
NA = not applicable to this decision kind in Revision 1
~~~

| Component | GATE_AUTHORIZATION | GATE_APPROVAL | GATE_PATH_CHOICE | TECHNICAL_ACCEPTANCE |
|---|---|---|---|---|
| DECISION_SUBJECT | R | R | R | R |
| CURRENT_STATE | R | R | R | R |
| PROPOSED_STATE | R | R | R | R |
| AUTHORITY_BASIS | R | O | O | R |
| POLICY_OR_GATE_BASIS | R | R | R | R |
| DESIGN_OR_SCOPE_BASIS | D | D | D | D |
| CHANGE_OR_RESULT_BASIS | NA | NA | NA | R |
| EVIDENCE | D | D | D | R |
| EVALUATION | R | R | R | R |
| RISKS_AND_BLOCKERS | R | R | R | R |
| GOVERNANCE_REQUIREMENTS | R | R | R | R |
| CONSEQUENCES | R | R | R | R |
| SOURCE_PROVENANCE | R | R | R | R |

## 7. RW1-D06 — Dynamic applicability rules

### DESIGN_OR_SCOPE_BASIS

For gate decisions:

- if the exact current HandoverGate has required_artifact_ids, the component is REQUIRED_PRESENT and source refs identify those exact artifact IDs;
- otherwise it is NOT_APPLICABLE unless another accepted current policy source explicitly requires design/scope material.

For technical acceptance:

- if the exact accepted result/evaluation or current gate requires artifacts, it is REQUIRED_PRESENT;
- otherwise NOT_APPLICABLE unless current policy explicitly requires it.

Missing required referenced artifact -> MISSING_REQUIRED.
Unresolved applicability -> UNKNOWN.

### EVIDENCE

For gate decisions:

- if the exact current gate has required_evidence_ids, EVIDENCE is REQUIRED_PRESENT;
- otherwise NOT_APPLICABLE unless another current accepted gate/policy condition explicitly requires evidence for that decision.

For TECHNICAL_ACCEPTANCE:

- EVIDENCE is REQUIRED_PRESENT because the current ManualEvaluationRecord requires and binds non-empty evidence_ids.

Missing required evidence -> MISSING_REQUIRED.
Evidence for another result/basis -> STALE or integrity error under existing semantics.

### AUTHORITY_BASIS

For GATE_AUTHORIZATION, the exact gate's authorization_required flag plus current gate evaluation reason is REQUIRED_PRESENT and explains why authority must be granted; a prior stale grant may be shown as source history but is not current authority.

For TECHNICAL_ACCEPTANCE, the exact ACCEPTED-target Human-approval gate requirement and current HumanActionBasis are REQUIRED_PRESENT.

For GATE_APPROVAL and GATE_PATH_CHOICE, prior/current Human decisions are optional current state, not prerequisites for the first decision.

### RISKS_AND_BLOCKERS

Required means Relay must present the exact current governed risk/blocker view available from gate evaluation, lifecycle blockage, and manual evaluation where applicable.

"No current blocking/risk reason is recorded in this exact governed basis" is permitted only as a scoped canonical fact. It must not be rewritten as a global risk = CLEAR unless an authoritative RiskStatus says CLEAR.

### GOVERNANCE_REQUIREMENTS

Required content comes only from current accepted HandoverGate / evaluation semantics:

- policy;
- hard_stop;
- authorization_required;
- required artifacts/evidence/dependencies/evaluation outcomes/quality checks;
- change-surface and risk review policy.

GovernanceProfile, profile level, Protected Verification Asset classification, or role-contract material is not required unless an authoritative current source exists and applicable accepted policy explicitly requires it.

Absent future profile/asset infrastructure therefore does not make every Revision-1 Decision Card incomplete.

## 8. RW1-D07 — Completeness precedence

DecisionBasisCompleteness is derived after component applicability/freshness is established:

~~~text
if any required component is STALE:
    STALE
elif any required applicability/freshness is UNKNOWN:
    UNKNOWN
elif any required component is MISSING_REQUIRED:
    INCOMPLETE
else:
    COMPLETE
~~~

A hard integrity contradiction remains an exception/error and is not converted into one of these four display states.

Optional material cannot make a card incomplete.

NOT_APPLICABLE material cannot make a card incomplete.

RECORDED_REVISABLE versus PENDING_REQUIRED does not by itself change completeness; it changes decision status and explanation.

## 9. RW1-D08 — Action binding and choice model

DecisionChoice is a discriminated read-model union, not a new command enum.

Conceptually:

~~~text
GateAuthorizationChoice
    command = AUTHORIZE
    gate_ref
    human_action_basis

GateApprovalChoice
    command = APPROVE | REJECT
    gate_ref
    human_action_basis
    expected_current_approval_decision_id

GatePathChoice
    command = CHOOSE_PATH
    selected_gate_ref
    human_action_basis
    expected_current_choice_decision_id

TechnicalAcceptanceChoice
    command = TECHNICAL_ACCEPT | TECHNICAL_REJECT
    gate_ref
    human_action_basis
    expected_result_id
    expected_manual_evaluation_id
    expected_current_approval_decision_id
~~~

The existing web POST routes and existing mutation services remain unchanged in authority semantics.

The Decision Support layer may prepare exact render data for those existing routes but may not invoke them.

## 10. RW1-D09 — Additional required tests

Add to Revision 1 D25:

### Digest contract

- canonical serialization matches sort_keys=True / compact UTF-8 definition;
- every HumanActionBasis field mutation rotates digest;
- approval current-decision ID mutation rotates GATE_APPROVAL digest;
- choice current-decision ID or eligible-gate-set mutation rotates GATE_PATH_CHOICE digest;
- result/evaluation/current-approval mutation rotates TECHNICAL_ACCEPTANCE digest;
- presentation-summary-only change does not rotate digest.

### Decision state

- no current decision -> PENDING_REQUIRED;
- current exact approval -> RECORDED_REVISABLE;
- current exact rejection -> RECORDED_REVISABLE;
- current exact path choice -> RECORDED_REVISABLE;
- current exact technical accept/reject -> RECORDED_REVISABLE;
- stale/non-current decision does not become RECORDED_REVISABLE;
- UI never labels a recorded revisable decision as missing/pending.

### Completeness policy

- each of four decision kinds exercises the frozen matrix;
- no required gate evidence -> EVIDENCE NOT_APPLICABLE for gate decision;
- required gate evidence missing -> MISSING_REQUIRED / INCOMPLETE;
- technical acceptance evidence is REQUIRED_PRESENT;
- absent GovernanceProfile infrastructure does not create false MISSING_REQUIRED;
- unresolved policy applicability -> UNKNOWN;
- required stale material -> STALE.

## 11. Finding disposition

~~~text
F001:
RESOLVED by RW1-D01, RW1-D02, RW1-D08, RW1-D09

F002:
RESOLVED by RW1-D03, RW1-D04, RW1-D09

F003:
RESOLVED by RW1-D05, RW1-D06, RW1-D07, RW1-D09
~~~

## 12. Preserved Revision-1 decisions

All other Revision-1 decisions remain normative, including:

- derived/read-only Decision Support;
- same-snapshot construction;
- existing mutation-service authority;
- explicit provenance;
- statement-class separation;
- risk non-invention;
- deterministic consequences;
- structured read-only Q&A;
- no provider/model execution;
- GovernanceProfile fail-honest presentation;
- clarity-feedback persistence deferral;
- telemetry collection deferral;
- server-rendered accessible UI;
- no migration or dependency change;
- bounded implementation surface;
- deterministic ordering;
- integrity-error preservation;
- downstream ownership and Phase 3 hard stops.

## 13. State after Rework 1

~~~text
Slice 1.9:
OPEN

Design subject:
Revision 1 + Rework 1 Addendum

Prior evaluation:
RLY-S19-DESIGN-EVAL-001 — REVISE

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
