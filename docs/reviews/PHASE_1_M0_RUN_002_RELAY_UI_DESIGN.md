# Phase 1 M0 — Run 002 Relay UI Governance Status Summary Design

**Document class:** Reviewable design artifact  
**Status:** DESIGN COMPLETE / NOT YET HUMAN-ACCEPTED  
**Date:** 2026-10-05  
**Record:** `RLY-P1-M0-RUN-002-DESIGN-001`

## 1. Authority and exact basis

```text
Phase 1 M0 authority:
RLY-P1-M0-AUTH-001 — AUTHORIZED

Run:
RLY-P1-M0-RUN-002 — OPENED

Task-selection commit:
45221e6337699f4ae6592b928d76530ac1b10d63

Design authority:
RLY-P1-M0-RUN-002-DESIGN-AUTH-001 — AUTHORIZED

Design-authority commit:
6c29b3dadc07ba9e97e3e1121a676eab50320655

Target repository:
cschrupp/relay

Exact frozen product baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Task:
Relay Slice Detail — Governance Status Summary
```

Later movement of `main` does not silently change this design basis.

## 2. Design objective

Add one compact, read-only **Governance status** section near the top of the existing Slice detail page so a Human can understand the current governed state without reconstructing it from several lower sections.

The summary is strictly a presentation of facts already carried by `SliceDetail`.

It must not:

- calculate a new canonical governance state;
- alter action eligibility;
- persist new state;
- add a new aggregate traffic light;
- reinterpret absence of evidence;
- replace the detailed sections that remain the full provenance presentation.

## 3. Core presentation rule

The summary is a **view**, not a governance decision.

Every displayed statement must be directly derivable from one of these existing projections:

```text
SliceDetail.lifecycle
SliceDetail.outgoing_gates
SliceDetail.human_actions
SliceDetail.manual_evaluation
```

No database access, service call, or new domain calculation is allowed inside the renderer.

## 4. Placement and structure

`render_slice_detail(...)` should render the new section immediately after the existing project/Slice identity header and before `Definition`.

Recommended semantic structure:

```html
<section aria-labelledby="governance-status-heading">
  <h2 id="governance-status-heading">Governance status</h2>
  ...compact current-state groups...
</section>
```

The detailed existing sections remain below it:

```text
Definition
Lifecycle
Gate/evaluation observation
Human actions
Manual evaluation and result
Execution
```

The summary therefore improves scanability without becoming a substitute for provenance.

## 5. Lifecycle group

Always display the current lifecycle truth.

### No lifecycle record

Display approximately:

```text
Lifecycle: NOT_STARTED — no lifecycle record.
```

### Existing lifecycle

Display:

- phase;
- validity;
- blockage status;
- lifecycle revision;
- existing blockage reasons if blocked.

If the phase is `READY`, include an explicit nearby warning:

```text
READY is a lifecycle phase; it does not grant execution authorization.
```

The summary must never emit wording equivalent to “ready to execute” merely from the lifecycle phase.

## 6. Current gate status group

Render each `detail.outgoing_gates` independently. Do not synthesize a global gate result.

For each current gate show:

- gate id;
- gate revision;
- target phase;
- whether authorization is required;
- evaluation-basis status.

### Matching durable basis

Only when:

```text
evaluation_basis_status == MATCHING_DURABLE_BASIS
```

may the summary show the gate's current traffic light.

Display the textual light (`GREEN`, `YELLOW`, or `RED`) in addition to any existing color styling.

If current reasons are present, show them as the existing typed reason code/kind/subject projection permits.

### Stale durable basis

Display approximately:

```text
Evaluation: stale durable basis — historical traffic lights are not current.
```

Do **not** display the historical light as current.

### Not evaluated

Display:

```text
Evaluation: not evaluated.
```

### Not applicable

Display:

```text
Evaluation: not applicable.
```

This preserves the existing board invariant that traffic-light color is observational evidence only when bound to the current durable basis.

## 7. Human authority/evidence group

The summary must present Human evidence, not infer a synthetic authorization status.

### Authorization grants

For each item in:

```text
detail.human_actions.current_authorizations
```

show enough exact provenance to identify the current grant, including the gate identity/revision and grant identity/time/actor fields already available on the model.

If none are projected, display:

```text
Current authorization grants: none projected.
```

Do not rewrite this as a new governance decision such as “NOT AUTHORIZED” unless that exact negative state is canonically represented elsewhere.

### Approval decisions

For current approval decisions, show their exact decision (`APPROVED`/`REJECTED` as represented), gate identity/revision, and decision identity.

### Choice decision

If present, show the selected gate identity/revision and decision identity.

### Human hold

If current Human holds exist, summarize the existing hold codes/summaries.

### Required invariant wording

The summary should include a compact explanatory line:

```text
Unblocked, READY, authorization grants, and approval decisions are distinct governance facts.
```

This is explanatory UI wording, not a state transition rule.

## 8. Manual evaluation / result group

Use only `detail.manual_evaluation`.

Show current facts independently.

### Current result

If present, show:

- result id;
- result baseline id;
- exact result commit when `current_result_baseline` is available.

If a current result exists but its baseline is not resolvable, say that the exact result commit is not currently resolvable rather than inventing one.

### Current evaluator decision

If `current_evaluation` exists, show:

- evaluation id;
- outcome;
- evaluator identity/display name;
- result id it evaluates.

Do not label this as Human technical acceptance.

### Current Human technical decision

If `current_technical_decision` exists, show separately:

- decision id;
- decision value;
- gate identity/revision.

### Accepted result

If `accepted_result` exists, show separately:

- accepted result id;
- exact accepted commit;
- manual evaluation id;
- Human approval decision id;
- accepted execution id.

### Required invariant wording

Render a compact explanatory statement near this group:

```text
Engineering result, evaluator decision, Human technical decision, and accepted-result promotion are distinct records.
```

The summary must not collapse them into a single “accepted” badge.

## 9. Development-memory group

If `detail.manual_evaluation.development_memory` exists, show that durable development history is available plus compact counts already derivable from the projection:

```text
results: <n>
evaluations: <n>
evidence items: <n>
accepted results: <n>
```

Also show the source baseline identity.

Do not introduce a new materialized memory or duplicate the full history.

If no development-memory projection exists, the summary may omit this group or state that no development-memory projection is available. It must not infer that engineering history does not exist outside the projection.

## 10. Rendering architecture

Preferred implementation:

```python

def _governance_status_section(detail: SliceDetail) -> str:
    ...
```

called from `render_slice_detail(...)` before `_definition_section(detail)`.

Small private helpers are acceptable if they remain in `board/render.py`, for example:

```text
_governance_lifecycle_summary(...)
_governance_gate_summary(...)
_governance_human_summary(...)
_governance_manual_summary(...)
```

Do not introduce a new presentation model unless implementation demonstrates that the renderer becomes materially unsafe/unmaintainable without one. That would be a design-review stop rather than automatic scope expansion.

## 11. Escaping and accessibility

All externally influenced fields must continue through the existing `_e(...)` escaping path.

This includes:

- Slice/project labels;
- blockage summaries;
- gate reason subjects;
- Human reason text/display names;
- result/evaluation identifiers;
- repository paths;
- development-memory identities.

Do not embed raw model/user text as HTML.

Use semantic headings/lists. Traffic-light meaning must always be textual; color may supplement it but must never be the only signal.

## 12. Styling

Use the existing CSS and `.gate-light` / `.green` / `.yellow` / `.red` classes where appropriate.

At most a very small presentation-only CSS addition inside `board/render.py` is permitted if needed for compact grouping.

No JavaScript, external assets, CSS framework, frontend framework, or dependency changes.

## 13. Expected implementation surface

Expected production change:

```text
src/relay_engine/board/render.py
```

Expected test change:

```text
tests/unit/test_board_render.py
```

Not expected and therefore design-stop surfaces:

```text
src/relay_engine/board/models.py
src/relay_engine/board/service.py
src/relay_engine/board/web.py
```

Anything under the frozen governance/domain/persistence surfaces is forbidden under Run 002.

## 14. Deterministic verification contract

Implementation evaluation must prove at minimum:

### V002-01 Placement

`Governance status` appears before the `Definition` section on Slice detail.

### V002-02 READY distinction

A READY lifecycle renders the explicit statement that READY does not grant execution authorization.

### V002-03 Matching traffic light

A gate on matching durable basis renders its current textual traffic light and relevant current reasons.

### V002-04 Stale traffic light suppression

A stale durable basis renders the stale warning and does not present the historical traffic light as current.

### V002-05 Unevaluated states

`NOT_EVALUATED` and `NOT_APPLICABLE` remain distinct textual states.

### V002-06 Human authorization evidence

Current authorization grants render as evidence with exact identifying provenance. Absence renders as “none projected,” not as an inferred negative Human decision.

### V002-07 Approval/choice distinction

Current approval and choice decisions, when present, remain distinguishable from authorization grants.

### V002-08 Result/evaluation/technical/promotion distinction

Fixtures containing all four layers prove that the summary renders them as separate records.

### V002-09 Exact commit provenance

When the current result baseline and accepted result exist, the exact result commit and exact accepted commit render independently.

### V002-10 Development memory

When development memory exists, source baseline and compact history counts render.

### V002-11 Escaping

Adversarial externally influenced strings continue to be escaped in the new summary.

### V002-12 Detailed sections preserved

Existing Lifecycle, evaluation observation, Human actions, manual evaluation/result, and execution sections remain present.

### V002-13 Change surface

Candidate diff contains only the accepted presentation/test files unless separately re-authorized.

### V002-14 Quality gates

Repository-owned formatting, lint, typing, tests, build, and repository-contract checks required by the current Relay baseline pass on the candidate.

## 15. Explicit non-goals

Not authorized by this design:

- new actions/buttons;
- new route/endpoint;
- new stored status;
- new global traffic light;
- new projection/service field;
- board index redesign;
- board lane redesign;
- dashboard metrics;
- persistence/schema work;
- governance semantics;
- Phase 2 work;
- autonomous agent integration;
- dependency/toolchain changes.

## 16. Design stop conditions

Stop and return to design/Human Authority if implementation would require:

- changing `SliceDetail` to add missing governance truth;
- touching `board/service.py` or `board/web.py` for semantic reasons;
- touching governance/lifecycle/human-control/manual-evaluation/persistence/repository semantics;
- adding a dependency;
- defining a new aggregate status/traffic-light rule;
- changing action availability;
- deleting or materially changing existing detailed provenance sections.

## 17. Conclusion

The implementation should be a small presentation-only change:

```text
existing SliceDetail truth
-> compact read-only Governance status summary
-> existing detailed provenance unchanged
```

This gives M0 a genuine UI usability improvement while keeping the governance engine under validation frozen.

## 18. State after design

```text
Phase 1 M0: AUTHORIZED / IN PROGRESS
Run 002: OPEN
Run 002 target: Relay
Frozen product baseline: d14fa79fd13f8f70745d8ed47feafdf2d4892a19
Design authority: AUTHORIZED
Design: COMPLETE
Design review: PENDING
Human design acceptance: NOT GRANTED
Implementation: NOT AUTHORIZED
Phase 2: NOT OPEN
Relay agent execution: NOT AUTHORIZED
```
