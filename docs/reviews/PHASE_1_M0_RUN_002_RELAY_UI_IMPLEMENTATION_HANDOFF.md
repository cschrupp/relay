# Phase 1 M0 — Run 002 Relay UI Implementation Handoff

**Document class:** Immutable external-implementation handoff  
**Status:** IMPLEMENTATION AUTHORIZED / CANDIDATE PENDING  
**Date:** 2026-10-05  
**Authority:** `RLY-P1-M0-RUN-002-IMPL-AUTH-001 — AUTHORIZED`

## 1. Exact implementation basis

```text
Repository:
cschrupp/relay

Frozen product baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

Implementation branch:
implementation/m0-run-002-governance-status-summary

Implementation authority record commit:
fec580e06848286a919091be5d2fb8b1400f21f3

Accepted design:
RLY-P1-M0-RUN-002-DESIGN-001
65bda5393fe74ab5c5b1fda03be80b81bbc4fe30

Independent design review:
RLY-P1-M0-RUN-002-DESIGN-EVAL-001 — ACCEPT
75ec3d36d8e15d4d1050c0c2e73b6e4fc62e2a2c

Human design acceptance:
RLY-P1-M0-RUN-002-DESIGN-ACCEPT-001 — ACCEPTED
a0671a4fed7be1361727d4cd2f55f0accb1535c9
```

The implementation branch was created from the exact frozen product baseline. The implementer must verify this before editing.

## 2. Bootstrap contract

Use the existing authorized branch. Do not create a different product basis.

```bash
git fetch origin
git checkout implementation/m0-run-002-governance-status-summary
git rev-parse HEAD
git merge-base --is-ancestor d14fa79fd13f8f70745d8ed47feafdf2d4892a19 HEAD
```

Before implementation starts, `git rev-parse HEAD` must return exactly:

```text
d14fa79fd13f8f70745d8ed47feafdf2d4892a19
```

If not, STOP and report the mismatch.

Do not merge/rebase/cherry-pick later `main` into this branch.

## 3. Objective

Implement a compact, read-only **Governance status** section near the top of existing Slice detail rendering.

The summary is a presentation view over already projected `SliceDetail` facts. It must not compute new canonical governance truth or alter governing behavior.

Target placement:

```text
Slice identity header
-> Governance status
-> Definition
-> Lifecycle
-> evaluation observation
-> Human actions
-> manual evaluation/result
-> Execution
```

## 4. Authorized file surface

Production:

```text
src/relay_engine/board/render.py
```

Focused tests:

```text
tests/unit/test_board_render.py
```

No other file is authorized by default.

If another file is genuinely required, STOP and request scope review before modifying it.

## 5. Preferred rendering structure

Preferred implementation:

```python
def _governance_status_section(detail: SliceDetail) -> str:
    ...
```

Small private helpers in `board/render.py` are acceptable, e.g. lifecycle, gate, Human-evidence, manual-evaluation, and development-memory subrenderers.

Call the summary from `render_slice_detail(...)` before `_definition_section(detail)`.

Do not introduce a new presentation/domain model.

## 6. Lifecycle summary

Always render lifecycle truth from `detail.lifecycle`.

If no lifecycle exists:

```text
Lifecycle: NOT_STARTED — no lifecycle record.
```

If present, render at least:

- phase;
- validity;
- blockage status;
- lifecycle revision;
- existing blockage reasons when blocked.

For READY, render explicit wording equivalent to:

```text
READY is a lifecycle phase; it does not grant execution authorization.
```

Never infer “ready to execute” from lifecycle READY.

## 7. Current outgoing gates

Render each `detail.outgoing_gates` independently.

For each gate show:

- gate id;
- gate revision;
- target phase;
- whether authorization is required;
- evaluation-basis status.

### Matching durable basis

Only when:

```text
EvaluationBasisStatus.MATCHING_DURABLE_BASIS
```

may the current traffic light be shown.

Display textual `GREEN`, `YELLOW`, or `RED` plus existing color class if useful.

Render typed current reasons without inventing additional semantics.

### Stale durable basis

Render explicit stale wording and do not show historical traffic light as current.

### NOT_EVALUATED / NOT_APPLICABLE

Keep these as separate textual states.

Do not synthesize an overall/global traffic light.

## 8. Human evidence

Use only `detail.human_actions`.

### Authorization grants

For each current authorization grant, render sufficient exact provenance already available on the model, including:

- authorization id;
- gate id/revision;
- actor/display name when available;
- granted-at timestamp.

If none:

```text
Current authorization grants: none projected.
```

Do not turn absence into an inferred `NOT AUTHORIZED` state.

### Approval decisions

Render each current approval decision separately from authorization grants, including decision id/value and gate id/revision.

### Choice decision

If present, render selected gate id/revision and decision id.

### Human hold

Render existing hold code/summary if projected.

Include compact explanatory wording equivalent to:

```text
Unblocked, READY, authorization grants, and approval decisions are distinct governance facts.
```

## 9. Manual evaluation and accepted-result provenance

Use only `detail.manual_evaluation`.

Render current result independently:

- result id;
- result baseline id;
- exact result commit if `current_result_baseline` is available.

Render current evaluator decision independently:

- evaluation id;
- outcome;
- evaluator identity/display name;
- result id evaluated.

Render current Human technical decision independently:

- decision id;
- decision value;
- gate id/revision.

Render accepted-result promotion independently when present:

- accepted result id;
- exact accepted commit;
- manual evaluation id;
- Human approval decision id;
- accepted execution id.

Include compact explanatory wording equivalent to:

```text
Engineering result, evaluator decision, Human technical decision, and accepted-result promotion are distinct records.
```

Never collapse these into a single “accepted” badge/status.

## 10. Development memory

If `detail.manual_evaluation.development_memory` exists, render compact provenance availability:

- source baseline id;
- count of result history;
- count of evaluation history;
- count of Evidence items;
- count of accepted results.

Do not introduce or persist any new memory representation.

If absent, either omit or state that no development-memory projection is currently available. Do not infer that no engineering history exists.

## 11. Escaping / accessibility

Every externally influenced field must continue through existing `_e(...)` escaping.

This includes reason text, display names, identifiers, summaries, repository/baseline content, and any user/model-owned text.

Use semantic headings/lists.

Traffic-light meaning must be textual; color is only supplemental.

Keep existing accessible focus behavior and existing detailed sections intact.

## 12. Styling

Prefer existing styles.

A very small presentation-only CSS addition in `board/render.py` is acceptable if necessary for compact grouping.

Forbidden:

```text
JavaScript
new frontend framework
external assets
CSS framework
new dependency
new build tool
```

## 13. Verification contract

The candidate must demonstrate all accepted design checks:

```text
V002-01 Governance status appears before Definition.
V002-02 READY explicitly does not grant execution authorization.
V002-03 Matching durable gate basis renders current textual traffic light/reasons.
V002-04 Stale basis suppresses current-light claim and renders stale warning.
V002-05 NOT_EVALUATED and NOT_APPLICABLE remain distinct.
V002-06 Authorization grants render exact provenance; absence says none projected.
V002-07 Approval and choice evidence remain distinct from authorization grants.
V002-08 Result/evaluator/technical/promotion layers remain separate.
V002-09 Current result commit and accepted commit render independently when available.
V002-10 Development-memory source/counts render when projected.
V002-11 Adversarial externally influenced strings are escaped in the new summary.
V002-12 Existing detailed provenance sections remain present.
V002-13 Candidate diff is limited to accepted production/test files.
V002-14 Repository quality gates pass.
```

Add focused deterministic tests in `tests/unit/test_board_render.py` rather than weakening or replacing existing assertions.

## 14. Anti-circularity hard stop

Do not modify:

```text
src/relay_engine/governance/**
src/relay_engine/lifecycle/**
src/relay_engine/human_control/**
src/relay_engine/manual_evaluation/**
src/relay_engine/persistence/**
src/relay_engine/repository_baseline/**
src/relay_engine/repository_contract/**
src/relay_engine/repository_sync/**
src/relay_engine/board/models.py
src/relay_engine/board/service.py
```

Do not modify `board/web.py` for semantic reasons.

Do not change action availability, lifecycle, gate rules, manual-evaluation rules, acceptance/promotion semantics, storage/schema, or agent execution.

If any of those becomes necessary, STOP.

## 15. Required quality commands

The frozen baseline CI uses exactly:

```bash
uv sync --frozen --group dev
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
git diff --check
```

Also run focused board-render tests before the full suite:

```bash
uv run pytest tests/unit/test_board_render.py
```

If repository-contract/frozen-sync checks are separate from the full suite in the local repository, run the repository-owned commands/scripts as found at the frozen baseline and report them exactly. Do not create new tooling to satisfy this handoff.

GitHub Actions CI exists and runs on push. After pushing the exact candidate, report the workflow run ID/status bound to the candidate SHA when available.

## 16. Candidate branch / push boundary

Push implementation only to:

```text
implementation/m0-run-002-governance-status-summary
```

Do not merge to `main`.

Do not modify `validation/phase-1-m0`.

Do not write an acceptance/closure record.

## 17. Final external-implementer report

Return exactly enough evidence for independent evaluation:

```text
authorized baseline:
d14fa79fd13f8f70745d8ed47feafdf2d4892a19

branch:
implementation/m0-run-002-governance-status-summary

candidate SHA:
<exact SHA>

executor:
<tool>

actual model:
<exact value if exposed>

model provenance deviation:
NONE or exact description

changed files:
<complete list>

V002-01..V002-14:
PASS/FAIL + concise evidence per item

focused board-render tests:
<exact result>

ruff format:
PASS/FAIL

ruff lint:
PASS/FAIL

pyright:
PASS/FAIL + error/warning counts

full pytest:
<exact counts>

build:
PASS/FAIL

git diff --check:
PASS/FAIL

repository-contract/frozen-sync checks:
<exact result or included in full suite>

GitHub Actions:
<run id + exact candidate SHA + status, or pending/unavailable>

dependencies/toolchain:
UNCHANGED or exact deviation

deviations:
NONE or exact list

new work discovered:
NONE or exact list
```

## 18. Authority boundary after implementation

The candidate remains only an implementation result.

Codex/external implementer is not authorized to:

- independently accept/evaluate its own candidate as the M0 evaluator;
- grant Human technical acceptance;
- promote the result;
- merge to `main`;
- declare Run 002/M0/Phase 1 complete;
- open Phase 2;
- execute Relay agents.

Stop after pushing the candidate and returning evidence.
