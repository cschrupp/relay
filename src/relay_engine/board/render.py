"""Accessible server-rendered HTML for immutable board projections."""

import json
from html import escape
from urllib.parse import quote

from relay_engine.board.models import (
    BoardProjection,
    DependencyProjection,
    EvaluationBasisStatus,
    GateProjection,
    ProjectBoard,
    SliceCard,
    SliceDetail,
)
from relay_engine.domain.models import Baseline
from relay_engine.governance.models import (
    ChangeSurfaceStatus,
    EvaluationOutcome,
    GateReason,
    GateReasonKind,
    RiskStatus,
    ToolchainChangeStatus,
)
from relay_engine.human_control.models import (
    HumanAction,
    HumanActionKind,
    HumanActionProjection,
)
from relay_engine.lifecycle.models import BlockageStatus
from relay_engine.manual_evaluation.models import (
    ManualEvaluationActionKind,
    ManualEvaluationProjection,
)

_STYLE = """
body {
  color: #17202a;
  font: 1rem/1.5 system-ui, sans-serif;
  margin: 0 auto;
  max-width: 76rem;
  padding: 1rem;
}
a { color: #0645ad; }
a:focus-visible, input:focus-visible, button:focus-visible {
  outline: 3px solid #d2691e;
  outline-offset: 2px;
}
nav, form, section, article { margin-block: 1rem; }
.lanes { display: grid; gap: 1rem; grid-template-columns: repeat(3, minmax(16rem, 1fr)); }
.lane, article { border: 1px solid #78838f; border-radius: .35rem; padding: .8rem; }
.gate-light { border-left: .45rem solid; padding-left: .6rem; }
.green { border-color: #16803c; } .yellow { border-color: #9a6b00; } .red { border-color: #b42318; }
.muted { color: #4b5563; }
pre { overflow-wrap: anywhere; white-space: pre-wrap; }
@media (max-width: 48rem) { .lanes { grid-template-columns: 1fr; } }
"""


def _e(value: object) -> str:
    return escape(str(value), quote=True)


def _page(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{_e(title)}</title><style>{_STYLE}</style></head>"
        f"<body><main><h1>{_e(title)}</h1>{body}</main></body></html>"
    )


def _slice_url(project_id: str, slice_id: str) -> str:
    return f"/projects/{quote(project_id, safe='')}/slices/{quote(slice_id, safe='')}"


def _project_url(project_id: str) -> str:
    return f"/projects/{quote(project_id, safe='')}"


def _reason_list(reasons: tuple[GateReason, ...]) -> str:
    if not reasons:
        return ""
    items = "".join(
        f"<li>{_e(reason.kind.value)}: {_e(reason.code.value)}"
        f"{'' if reason.subject is None else f' — {_e(reason.subject)}'}</li>"
        for reason in reasons
    )
    return f"<ul>{items}</ul>"


def _evaluation_status(status: EvaluationBasisStatus) -> str:
    labels = {
        EvaluationBasisStatus.MATCHING_DURABLE_BASIS: "matching durable basis",
        EvaluationBasisStatus.STALE_DURABLE_BASIS: "stale durable basis",
        EvaluationBasisStatus.NOT_EVALUATED: "not evaluated",
        EvaluationBasisStatus.NOT_APPLICABLE: "not applicable",
    }
    return labels[status]


def _dependency_item(dependency: DependencyProjection, project_id: str) -> str:
    title = "no current definition" if dependency.title is None else _e(dependency.title)
    state = (
        "no lifecycle"
        if dependency.lifecycle_phase is None
        else _e(dependency.lifecycle_phase.value)
    )
    if dependency.lifecycle_validity is not None:
        state += f"; lifecycle validity {_e(dependency.lifecycle_validity.value)}"
    return (
        f'<li><a href="{_slice_url(project_id, dependency.slice_id)}">'
        f"{_e(dependency.slice_id)}</a> — {title}; {state}</li>"
    )


def _gate_status(gate: GateProjection) -> str:
    if gate.evaluation_basis_status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS:
        if gate.evaluation_light is None:
            return "<p>Integrity error: matching observation has no gate result.</p>"
        color = gate.evaluation_light.value.lower()
        result = (
            f'<p class="gate-light {_e(color)}">Latest recorded evaluation on current '
            f"durable basis: <strong>{_e(gate.evaluation_light.value)}</strong></p>"
        )
        return result + _reason_list(gate.evaluation_reasons)
    if gate.evaluation_basis_status is EvaluationBasisStatus.STALE_DURABLE_BASIS:
        return "<p>Evaluation: stale durable basis. Historical lights are not current.</p>"
    if gate.evaluation_basis_status is EvaluationBasisStatus.NOT_EVALUATED:
        return "<p>Evaluation: not evaluated.</p>"
    return "<p>Evaluation: not applicable.</p>"


def _gate_item(gate: GateProjection) -> str:
    blocking_count = sum(
        reason.kind is GateReasonKind.BLOCKING for reason in gate.evaluation_reasons
    )
    human_action_count = sum(
        reason.kind is GateReasonKind.HUMAN_ACTION for reason in gate.evaluation_reasons
    )
    reason_counts = ""
    if gate.evaluation_basis_status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS:
        reason_counts = (
            f"<p>Recorded reason counts: {blocking_count} blocking; "
            f"{human_action_count} human action.</p>"
        )
    return (
        "<li>"
        f"<h4>Gate {_e(gate.gate_id)} revision {_e(gate.gate_revision)}</h4>"
        f"<p>Target phase: {_e(gate.target_phase.value)}; policy: {_e(gate.policy.value)}; "
        f"hard stop: {_e(gate.hard_stop)}; authorization required: "
        f"{_e(gate.authorization_required)}; baseline: {_e(gate.baseline_id)}</p>"
        f"{reason_counts}"
        f"{_gate_status(gate)}</li>"
    )


def _blockage(card: SliceCard) -> str:
    if card.lifecycle is None:
        return ""
    blockage = card.lifecycle.blockage
    if blockage.status is not BlockageStatus.BLOCKED:
        return ""
    reasons = "".join(
        f"<li>{_e(reason.code)}: {_e(reason.summary)}</li>" for reason in blockage.reasons
    )
    return f"<p><strong>BLOCKED</strong></p><ul>{reasons}</ul>"


def _card(card: SliceCard, project_id: str) -> str:
    phase = "NOT_STARTED" if card.lifecycle is None else card.lifecycle.phase.value
    validity = ""
    if card.lifecycle is not None and card.lifecycle.validity.value == "STALE":
        validity = "<p>Lifecycle validity: STALE</p>"
    parent = (
        "" if card.parent_slice_id is None else f"<p>Parent Slice: {_e(card.parent_slice_id)}</p>"
    )
    dependency_count = len(card.dependencies)
    dependencies = (
        "<p>No declared dependencies.</p>"
        if not card.dependencies
        else f"<p>Declared dependencies: {dependency_count}</p><ul>"
        + "".join(_dependency_item(item, project_id) for item in card.dependencies)
        + "</ul>"
    )
    gates = (
        "<p>No current outgoing gates.</p>"
        if not card.outgoing_gates
        else "<h4>Outgoing gates</h4><ul>"
        + "".join(_gate_item(item) for item in card.outgoing_gates)
        + "</ul>"
    )
    evaluation = f"<p>Evaluation basis: {_e(_evaluation_status(card.evaluation_basis_status))}</p>"
    if card.latest_evaluation_record_id is not None:
        evaluation += (
            f"<p>Latest recorded observation: {_e(card.latest_evaluation_record_id)} "
            f"({_e(card.latest_evaluation_recorded_at)})</p>"
        )
    detail = _slice_url(project_id, card.slice_id)
    return (
        f'<article><h3><a href="{detail}">{_e(card.title)}</a></h3>'
        f"<p>Slice ID: <code>{_e(card.slice_id)}</code></p>"
        f"<p>Lifecycle: <strong>{_e(phase)}</strong></p>{validity}{_blockage(card)}"
        f"{parent}{dependencies}{evaluation}{gates}</article>"
    )


def render_project_index(projection: BoardProjection) -> str:
    """Render the verified current Project index."""

    if not projection.projects:
        return _page("Relay board", "<p>No Projects are defined.</p>")
    items = "".join(
        "<li>"
        f'<h2><a href="{_project_url(item.project.id)}">{_e(item.project.name)}</a></h2>'
        f"<p>Project ID: <code>{_e(item.project.id)}</code></p>"
        f"<p>Primary repository: {_e(item.project.primary_repository.path)}</p>"
        f"<p>Current Slices: {_e(item.slice_count)}</p></li>"
        for item in projection.projects
    )
    return _page("Relay board", f"<ul>{items}</ul>")


def render_project_board(board: ProjectBoard, query: str = "") -> str:
    """Render a Project's complete projection, optionally filtering displayed cards."""

    needle = query.casefold()
    body = (
        f'<nav aria-label="Primary"><a href="/">All Projects</a></nav>'
        f"<p>Project ID: <code>{_e(board.project.id)}</code></p>"
        f"<p>Primary repository: {_e(board.project.primary_repository.path)}</p>"
        '<form method="get"><label for="q">Search Slice title or exact ID</label> '
        f'<input id="q" name="q" value="{_e(query)}">'
        '<button type="submit">Search</button></form>'
    )
    if not board.cards:
        body += "<p>This Project has no Slices.</p>"

    rendered_count = 0
    body += '<div class="lanes">'
    for lane in board.lanes:
        cards = tuple(
            card
            for card in board.cards
            if card.lane is lane
            and (
                not needle or needle in card.title.casefold() or needle in card.slice_id.casefold()
            )
        )
        rendered_count += len(cards)
        content = "".join(_card(card, board.project.id) for card in cards)
        body += (
            f'<section class="lane"><h2>{_e(lane.value)}</h2>'
            f"{content if content else '<p>No Slices in this lane.</p>'}</section>"
        )
    body += "</div>"
    if needle and rendered_count == 0:
        body += "<p>No Slices match this search.</p>"
    return _page(f"{board.project.name} — board", body)


def _governance_lifecycle_summary(detail: SliceDetail) -> str:
    lifecycle = detail.lifecycle
    if lifecycle is None:
        return "<p>Lifecycle: NOT_STARTED — no lifecycle record.</p>"

    body = (
        f"<p>Lifecycle: <strong>{_e(lifecycle.phase.value)}</strong>; validity "
        f"{_e(lifecycle.validity.value)}; blockage "
        f"{_e(lifecycle.blockage.status.value)}; revision {_e(lifecycle.revision)}.</p>"
    )
    if lifecycle.blockage.status is BlockageStatus.BLOCKED:
        reasons = "".join(
            f"<li>{_e(reason.code)}: {_e(reason.summary)}</li>"
            for reason in lifecycle.blockage.reasons
        )
        body += f"<h4>Blockage reasons</h4><ul>{reasons}</ul>"
    if lifecycle.phase.value == "READY":
        body += "<p>READY is a lifecycle phase; it does not grant execution authorization.</p>"
    return body


def _governance_gate_evaluation(gate: GateProjection) -> str:
    status = gate.evaluation_basis_status
    if status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS:
        if gate.evaluation_light is None:
            evaluation = "<p>No current traffic light is projected for the matching basis.</p>"
        else:
            color = gate.evaluation_light.value.lower()
            evaluation = (
                f'<p class="gate-light {_e(color)}">Current traffic light: '
                f"<strong>{_e(gate.evaluation_light.value)}</strong></p>"
            )
        return (
            "<p>Evaluation-basis status: matching durable basis.</p>"
            f"{evaluation}{_reason_list(gate.evaluation_reasons)}"
        )
    if status is EvaluationBasisStatus.STALE_DURABLE_BASIS:
        return "<p>Evaluation: stale durable basis — historical traffic lights are not current.</p>"
    if status is EvaluationBasisStatus.NOT_EVALUATED:
        return "<p>Evaluation: not evaluated.</p>"
    return "<p>Evaluation: not applicable.</p>"


def _governance_gate_summary(detail: SliceDetail) -> str:
    if not detail.outgoing_gates:
        return "<p>No current outgoing gates projected.</p>"

    gates = "".join(
        "<li>"
        f"<h4>Gate <code>{_e(gate.gate_id)}</code> revision "
        f"{_e(gate.gate_revision)}</h4>"
        f"<p>Target lifecycle phase: {_e(gate.target_phase.value)}; "
        f"authorization required: {_e('yes' if gate.authorization_required else 'no')}.</p>"
        f"{_governance_gate_evaluation(gate)}</li>"
        for gate in detail.outgoing_gates
    )
    return f"<ul>{gates}</ul>"


def _governance_human_summary(detail: SliceDetail) -> str:
    projection = detail.human_actions
    parts: list[str] = ["<h4>Authorization grants</h4>"]
    if projection.current_authorizations:
        grants = "".join(
            "<li>Authorization <code>"
            f"{_e(grant.authorization_id)}</code>; gate <code>{_e(grant.gate_id)}</code> "
            f"revision {_e(grant.gate_revision)}; actor "
            f"{_e(grant.actor.display_name or grant.actor.id)}; granted "
            f"{_e(grant.granted_at)}.</li>"
            for grant in projection.current_authorizations
        )
        parts.append(f"<ul>{grants}</ul>")
    else:
        parts.append("<p>Current authorization grants: none projected.</p>")

    parts.append("<h4>Approval decisions</h4>")
    if projection.current_approval_decisions:
        decisions = "".join(
            "<li>Approval decision <code>"
            f"{_e(decision.decision_id)}</code>: {_e(decision.decision.value)}; gate "
            f"<code>{_e(decision.gate_id)}</code> revision "
            f"{_e(decision.gate_revision)}.</li>"
            for decision in projection.current_approval_decisions
        )
        parts.append(f"<ul>{decisions}</ul>")
    else:
        parts.append("<p>No current approval decisions projected.</p>")

    parts.append("<h4>Choice decision</h4>")
    if projection.current_choice is None:
        parts.append("<p>No current choice decision projected.</p>")
    else:
        choice = projection.current_choice
        parts.append(
            "<p>Choice decision <code>"
            f"{_e(choice.decision_id)}</code> selected gate "
            f"<code>{_e(choice.selected_gate_id)}</code> revision "
            f"{_e(choice.selected_gate_revision)}.</p>"
        )

    parts.append("<h4>Human holds</h4>")
    if projection.human_hold:
        holds = "".join(
            f"<li>{_e(hold.code)}: {_e(hold.summary)}</li>" for hold in projection.human_hold
        )
        parts.append(f"<ul>{holds}</ul>")
    else:
        parts.append("<p>No current Human holds projected.</p>")

    parts.append(
        "<p>Unblocked, READY, authorization grants, and approval decisions are distinct "
        "governance facts.</p>"
    )
    return "".join(parts)


def _governance_manual_evaluation_summary(detail: SliceDetail) -> str:
    projection: ManualEvaluationProjection = detail.manual_evaluation
    parts: list[str] = []

    parts.append("<h4>Engineering result</h4>")
    result = projection.current_result
    if result is None:
        parts.append("<p>No current engineering result projected.</p>")
    else:
        parts.append(
            f"<p>Result <code>{_e(result.result_id)}</code>; result baseline "
            f"<code>{_e(result.result_baseline_id)}</code>.</p>"
        )
        baseline = projection.current_result_baseline
        if baseline is None:
            parts.append("<p>Exact result commit is not currently resolvable.</p>")
        else:
            parts.append(
                f"<p>Exact result commit: <code>{_e(baseline.commit.sha)}</code> in "
                f"{_e(baseline.commit.repository.path)}.</p>"
            )

    parts.append("<h4>Evaluator decision</h4>")
    evaluation = projection.current_evaluation
    if evaluation is None:
        parts.append("<p>No current evaluator decision projected.</p>")
    else:
        parts.append(
            f"<p>Evaluation <code>{_e(evaluation.evaluation_id)}</code>; outcome "
            f"{_e(evaluation.outcome.value)}; evaluator "
            f"{_e(evaluation.evaluator.display_name or evaluation.evaluator.id)}; "
            f"result <code>{_e(evaluation.result_id)}</code>.</p>"
        )

    parts.append("<h4>Human technical decision</h4>")
    decision = projection.current_technical_decision
    if decision is None:
        parts.append("<p>No current Human technical decision projected.</p>")
    else:
        parts.append(
            f"<p>Decision <code>{_e(decision.decision_id)}</code>: "
            f"{_e(decision.decision.value)}; gate <code>{_e(decision.gate_id)}</code> "
            f"revision {_e(decision.gate_revision)}.</p>"
        )

    parts.append("<h4>Accepted-result promotion</h4>")
    accepted = projection.accepted_result
    if accepted is None:
        parts.append("<p>No accepted-result promotion projected.</p>")
    else:
        parts.append(
            f"<p>Accepted result <code>{_e(accepted.result_id)}</code>; exact accepted "
            f"commit <code>{_e(accepted.commit)}</code>; manual evaluation "
            f"<code>{_e(accepted.manual_evaluation_id)}</code>; Human approval decision "
            f"<code>{_e(accepted.human_approval_decision_id)}</code>; accepted execution "
            f"<code>{_e(accepted.accepted_execution_id)}</code>.</p>"
        )

    parts.append(
        "<p>Engineering result, evaluator decision, Human technical decision, and "
        "accepted-result promotion are distinct records.</p>"
    )

    memory = projection.development_memory
    if memory is not None:
        parts.append(
            f"<p>Development memory source baseline: "
            f"<code>{_e(memory.source_baseline.id)}</code>. Result records: "
            f"{len(memory.result_history)}; evaluation records: "
            f"{len(memory.evaluation_history)}; Evidence items: {len(memory.evidence)}; "
            f"accepted results: {len(memory.accepted_results)}.</p>"
        )
    return "".join(parts)


def _governance_status_section(detail: SliceDetail) -> str:
    """Render a compact read-only summary from current SliceDetail projections."""

    return (
        '<section aria-labelledby="governance-status-heading">'
        '<h2 id="governance-status-heading">Governance status</h2>'
        "<h3>Lifecycle</h3>"
        f"{_governance_lifecycle_summary(detail)}"
        "<h3>Outgoing gates</h3>"
        f"{_governance_gate_summary(detail)}"
        "<h3>Human authority evidence</h3>"
        f"{_governance_human_summary(detail)}"
        "<h3>Manual evaluation and result provenance</h3>"
        f"{_governance_manual_evaluation_summary(detail)}"
        "</section>"
    )


def _definition_section(detail: SliceDetail) -> str:
    value = detail.slice_definition.value
    in_scope = "".join(f"<li>{_e(item)}</li>" for item in value.scope.in_scope)
    out_scope = "".join(f"<li>{_e(item)}</li>" for item in value.scope.out_of_scope)
    criteria = "".join(
        f"<li><strong>{_e(item.key)}</strong> ({'required' if item.required else 'optional'}): "
        f"{_e(item.statement)}</li>"
        for item in value.acceptance_criteria
    )
    parent = (
        "<p>No parent Slice.</p>"
        if detail.parent is None
        else "<p>Parent Slice:</p><ul>"
        + _dependency_item(detail.parent, detail.project.id)
        + "</ul>"
    )
    children = (
        "<p>No child Slices.</p>"
        if not detail.children
        else "<ul>"
        + "".join(_dependency_item(item, detail.project.id) for item in detail.children)
        + "</ul>"
    )
    dependencies = (
        "<p>No declared dependencies.</p>"
        if not detail.dependencies
        else "<ul>"
        + "".join(_dependency_item(item, detail.project.id) for item in detail.dependencies)
        + "</ul>"
    )
    return (
        "<section><h2>Definition</h2>"
        f"<p>Definition revision: {_e(detail.slice_definition.definition_revision)}</p>"
        f"<h3>In scope</h3><ul>{in_scope}</ul>"
        f"<h3>Out of scope</h3><ul>{out_scope}</ul>"
        f"<h3>Acceptance criteria</h3><ul>{criteria}</ul>"
        f"<h3>Parent and children</h3>{parent}{children}"
        f"<h3>Dependencies</h3>{dependencies}</section>"
    )


def _lifecycle_section(detail: SliceDetail) -> str:
    lifecycle = detail.lifecycle
    if lifecycle is None:
        return "<section><h2>Lifecycle</h2><p>NOT_STARTED; no lifecycle record.</p></section>"
    reasons = "".join(
        f"<li>{_e(reason.code)}: {_e(reason.summary)}</li>" for reason in lifecycle.blockage.reasons
    )
    successor = (
        ""
        if lifecycle.superseded_by_slice_id is None
        else f"<p>Superseded by Slice: {_e(lifecycle.superseded_by_slice_id)}</p>"
    )
    return (
        "<section><h2>Lifecycle</h2>"
        f"<p>Phase: <strong>{_e(lifecycle.phase.value)}</strong></p>"
        f"<p>Validity: {_e(lifecycle.validity.value)}</p>"
        f"<p>Blockage: {_e(lifecycle.blockage.status.value)}</p>"
        f"<p>Revision: {_e(lifecycle.revision)}; updated: {_e(lifecycle.updated_at)}</p>"
        f"<ul>{reasons}</ul>"
        f"{successor}"
        "<p>Lifecycle READY is a phase and does not grant execution authorization.</p>"
        "</section>"
    )


def _baseline_text(label: str, baseline: Baseline | None) -> str:
    if baseline is None:
        return f"<p>{_e(label)}: no resolvable baseline.</p>"
    return (
        f"<p>{_e(label)}: <code>{_e(baseline.id)}</code>; commit "
        f"<code>{_e(baseline.commit.sha)}</code> in {_e(baseline.commit.repository.path)}.</p>"
    )


def _observation_section(detail: SliceDetail) -> str:
    status = _evaluation_status(detail.evaluation_basis_status)
    body = f"<p>Evaluation basis: {_e(status)}</p>"
    body += _baseline_text("Current outgoing-gate baseline", detail.baseline)
    record = detail.latest_evaluation_observation
    if record is None:
        body += "<p>No durable evaluation observation is recorded.</p>"
    else:
        body += (
            f"<p>Latest recorded observation: <code>{_e(record.id)}</code>; "
            f"recorded at {_e(record.recorded_at)}.</p>"
        )
        body += _baseline_text("Recorded evaluation baseline", detail.evaluation_baseline)
        if detail.evaluation_basis_status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS:
            body += "<p>Latest recorded evaluation on current durable basis.</p>"
        else:
            body += "<p>Older evaluation evidence; stored lights are historical.</p>"
        evaluations = "".join(
            f"<li>Gate {_e(item.gate_id)} revision {_e(item.gate_revision)}: "
            f"{_e(item.light.value)}{_reason_list(item.reasons)}</li>"
            for item in record.evaluations
        )
        refs = "".join(
            f"<li>Gate {_e(item.gate_id)} revision {_e(item.gate_revision)}</li>"
            for item in record.gate_refs
        )
        body += f"<h3>Recorded gate outputs</h3><ul>{evaluations}</ul>"
        body += f"<h3>Recorded gate references</h3><ul>{refs}</ul>"
        body += (
            "<h3>Full recorded HandoverContext</h3>"
            f"<pre><code>{_e(record.context.model_dump_json(indent=2))}</code></pre>"
        )
    gates = (
        "<p>No current outgoing gate definitions.</p>"
        if not detail.outgoing_gates
        else "<h3>Current outgoing gates</h3><ul>"
        + "".join(_gate_item(item) for item in detail.outgoing_gates)
        + "</ul>"
    )
    return f"<section><h2>Evaluation and gates</h2>{body}{gates}</section>"


def _execution_section(detail: SliceDetail) -> str:
    if not detail.relevant_execution_records:
        return "<section><h2>Execution evidence</h2><p>No execution records.</p></section>"
    items = "".join(
        "<li>"
        f"<p>Execution <code>{_e(record.execution_id)}</code>; evaluation record "
        f"<code>{_e(record.gate_evaluation_record_id)}</code>; selected gate "
        f"<code>{_e(record.selected_gate_id)}</code> revision "
        f"{_e(record.selected_gate_revision)}.</p>"
        f"<p>Lifecycle revision {_e(record.source_lifecycle_revision)} → "
        f"{_e(record.resulting_lifecycle_revision)}; event "
        f"<code>{_e(record.event_id)}</code>.</p>"
        f"<p>Actor: {_e(record.actor.kind.value)} "
        f"{_e(record.actor.display_name or record.actor.id)}; "
        f"time: {_e(record.occurred_at)}; reason: {_e(record.reason)}</p>"
        "</li>"
        for record in detail.relevant_execution_records
    )
    return f"<section><h2>Execution evidence</h2><ol>{items}</ol></section>"


def _human_evidence(projection: HumanActionProjection) -> str:
    evidence: list[str] = []
    for grant in projection.current_authorizations:
        actor = grant.actor.display_name or grant.actor.id
        evidence.append(
            "<li>Authorization <code>"
            f"{_e(grant.authorization_id)}</code> for gate <code>{_e(grant.gate_id)}</code> "
            f"revision {_e(grant.gate_revision)}; baseline <code>{_e(grant.baseline_id)}</code>; "
            f"actor {_e(actor)}; granted {_e(grant.granted_at)}; "
            f"reason: {_e(grant.reason)}</li>"
        )
    for decision in projection.current_approval_decisions:
        actor = decision.actor.display_name or decision.actor.id
        evidence.append(
            "<li>Approval decision <code>"
            f"{_e(decision.decision_id)}</code> for gate <code>{_e(decision.gate_id)}</code> "
            f"revision {_e(decision.gate_revision)}: "
            f"<strong>{_e(decision.decision.value)}</strong>; "
            f"lifecycle revision {_e(decision.lifecycle_revision)}; governance revision "
            f"{_e(decision.governance_revision)}; actor "
            f"{_e(actor)}; time {_e(decision.occurred_at)}; "
            f"reason: {_e(decision.reason)}</li>"
        )
    if projection.current_choice is not None:
        choice = projection.current_choice
        actor = choice.actor.display_name or choice.actor.id
        evidence.append(
            "<li>Choice decision <code>"
            f"{_e(choice.decision_id)}</code> selected gate <code>"
            f"{_e(choice.selected_gate_id)}</code> revision {_e(choice.selected_gate_revision)}; "
            f"lifecycle revision {_e(choice.lifecycle_revision)}; governance revision "
            f"{_e(choice.governance_revision)}; actor {_e(actor)}; "
            f"time {_e(choice.occurred_at)}; reason: {_e(choice.reason)}</li>"
        )
    for hold in projection.human_hold:
        evidence.append(f"<li>Human hold {_e(hold.code)}: {_e(hold.summary)}</li>")
    if not evidence:
        return "<p>No current Human evidence is projected.</p>"
    return "<ul>" + "".join(evidence) + "</ul>"


def _hidden(name: str, value: object) -> str:
    return f'<input type="hidden" name="{_e(name)}" value="{_e(value)}">'


def _reason_field() -> str:
    return '<label>Reason <textarea name="reason" required maxlength="2000"></textarea></label>'


def _action_form(
    path: str,
    label: str,
    csrf_token: str,
    hidden_fields: tuple[tuple[str, object], ...],
    *,
    reason: bool = True,
    extra: str = "",
) -> str:
    hidden = _hidden("csrf_token", csrf_token) + "".join(
        _hidden(name, value) for name, value in hidden_fields
    )
    reason_control = _reason_field() if reason else ""
    return (
        f'<form method="post" action="{_e(path)}"><fieldset><legend>{_e(label)}</legend>'
        f'{hidden}{extra}{reason_control}<button type="submit">{_e(label)}</button>'
        "</fieldset></form>"
    )


def _human_action_form(
    action: HumanAction,
    detail: SliceDetail,
    csrf_token: str,
    basis_json: str,
) -> str:
    value = detail.slice_definition.value
    prefix = _slice_url(detail.project.id, value.id)
    gate_id = action.gate_id or ""
    route = action.kind.value.lower()
    fields: list[tuple[str, object]] = [("basis", basis_json)]
    if action.gate_id is not None:
        fields.append(("gate_id", action.gate_id))
    if action.gate_revision is not None:
        fields.append(("gate_revision", action.gate_revision))
    if action.kind in {HumanActionKind.APPROVE, HumanActionKind.REJECT}:
        decision = next(
            (
                item
                for item in detail.human_actions.current_approval_decisions
                if item.gate_id == action.gate_id
            ),
            None,
        )
        fields.append(
            (
                "expected_current_approval_decision_id",
                "" if decision is None else decision.decision_id,
            )
        )
    extra = ""
    label = action.kind.value.replace("_", " ").title()
    if action.kind is HumanActionKind.CHOOSE_PATH:
        current_choice = detail.human_actions.current_choice
        fields.append(
            (
                "expected_current_choice_decision_id",
                "" if current_choice is None else current_choice.decision_id,
            )
        )
        basis = detail.human_actions.basis
        current_refs: set[tuple[str, int]] = (
            set()
            if basis is None
            else {(reference.gate_id, reference.gate_revision) for reference in basis.gate_refs}
        )
        options = "".join(
            f'<option value="{_e(gate.gate_id)}">{_e(gate.key)} — '
            f"{_e(gate.gate_id)} revision {_e(gate.revision)}; target "
            f"{_e(gate.target_phase.value)}</option>"
            for gate in detail.outgoing_gate_definitions
            if gate.policy.value == "HUMAN_CHOICE" and (gate.gate_id, gate.revision) in current_refs
        )
        extra = (
            '<label>Chosen path <select name="selected_gate_id" required>'
            '<option value="" disabled selected>Select a path</option>'
            f"{options}</select></label>"
        )
    if action.kind is HumanActionKind.CANCEL:
        route = "cancel"
    if action.kind is HumanActionKind.ADVANCE:
        route = "advance"
    if action.kind is HumanActionKind.CHOOSE_PATH:
        route = "choose"
    if action.kind in {HumanActionKind.APPROVE, HumanActionKind.REJECT}:
        route = action.kind.value.lower()
    provenance = ""
    if action.gate_id is not None:
        basis = detail.human_actions.basis
        baseline_id = "" if basis is None else basis.baseline_id
        provenance = (
            f"<p>Gate <code>{_e(gate_id)}</code> revision {_e(action.gate_revision)}; "
            f"target {_e(action.target_phase.value if action.target_phase else '')}; "
            f"baseline <code>{_e(baseline_id)}</code>.</p>"
            f"{_reason_list(action.reasons)}"
        )
    return provenance + _action_form(
        f"{prefix}/actions/{route}",
        label,
        csrf_token,
        tuple(fields),
        extra=extra,
    )


def _human_action_section(detail: SliceDetail, csrf_token: str | None) -> str:
    projection = detail.human_actions
    basis = projection.basis
    provenance = (
        "<p>No current Human Action Basis is available. Gate controls are hidden until a matching "
        "durable evaluation and Human-evidence projection exist.</p>"
        if basis is None
        else "<p>Human Action Basis: evaluation <code>"
        f"{_e(basis.evaluation_record_id)}</code>; baseline <code>{_e(basis.baseline_id)}</code>; "
        f"lifecycle revision {_e(basis.lifecycle_revision)}; governance revision "
        f"{_e(basis.governance_revision)}.</p>"
    )
    body = f"<h3>Current Human evidence</h3>{_human_evidence(projection)}{provenance}"
    if csrf_token is not None:
        if basis is not None:
            basis_json = basis.model_dump_json()
            seen: set[HumanActionKind] = set()
            for action in projection.actions:
                if action.kind in {
                    HumanActionKind.BLOCK,
                    HumanActionKind.PAUSE,
                    HumanActionKind.DEFER,
                    HumanActionKind.CLEAR_HOLD,
                }:
                    continue
                if action.kind is HumanActionKind.CHOOSE_PATH:
                    if action.kind in seen:
                        continue
                    seen.add(action.kind)
                body += _human_action_form(action, detail, csrf_token, basis_json)
        lifecycle = detail.lifecycle
        if lifecycle is not None:
            slice_url = _slice_url(detail.project.id, detail.slice_definition.value.id)
            for kind in (HumanActionKind.BLOCK, HumanActionKind.PAUSE, HumanActionKind.DEFER):
                if any(action.kind is kind for action in projection.actions):
                    body += _action_form(
                        f"{slice_url}/actions/hold",
                        kind.value.title(),
                        csrf_token,
                        (
                            ("hold_kind", kind.value),
                            ("expected_lifecycle_revision", lifecycle.revision),
                        ),
                    )
            if any(action.kind is HumanActionKind.CLEAR_HOLD for action in projection.actions):
                body += _action_form(
                    f"{slice_url}/actions/resume",
                    "Resume",
                    csrf_token,
                    (("expected_lifecycle_revision", lifecycle.revision),),
                )
    return (
        '<section aria-labelledby="human-actions-heading">'
        f'<h2 id="human-actions-heading">Human actions</h2>{body}</section>'
    )


def _manual_evaluation_form(
    path: str,
    label: str,
    csrf_token: str,
    fields: tuple[tuple[str, object], ...],
    controls: str,
) -> str:
    hidden = _hidden("csrf_token", csrf_token) + "".join(
        _hidden(name, value) for name, value in fields
    )
    return (
        f'<form method="post" action="{_e(path)}"><fieldset><legend>{_e(label)}</legend>'
        f'{hidden}{controls}<button type="submit">{_e(label)}</button></fieldset></form>'
    )


def _manual_evaluation_section(detail: SliceDetail, csrf_token: str | None) -> str:
    projection: ManualEvaluationProjection = detail.manual_evaluation
    parts = ['<section aria-labelledby="manual-evaluation-heading">']
    parts.append('<h2 id="manual-evaluation-heading">Manual evaluation and result</h2>')
    if projection.current_result is None:
        parts.append("<p>No result is attached to the current EVALUATING attempt.</p>")
    else:
        result = projection.current_result
        baseline = projection.current_result_baseline
        parts.append(
            f"<p>Current result <code>{_e(result.result_id)}</code>; result Baseline "
            f"<code>{_e(result.result_baseline_id)}</code>; source Baseline "
            f"<code>{_e(result.source_baseline_id)}</code>; lifecycle revision "
            f"{_e(result.lifecycle_revision)}.</p>"
        )
        if baseline is not None:
            parts.append(
                f"<p>Exact result commit: <code>{_e(baseline.commit.sha)}</code> in "
                f"{_e(baseline.commit.repository.path)}.</p>"
            )
        if projection.current_evaluation is None:
            parts.append("<p>Awaiting authored manual evaluation.</p>")
        else:
            evaluation = projection.current_evaluation
            parts.append(
                f"<p>Current evaluator decision <code>{_e(evaluation.evaluation_id)}</code>: "
                f"<strong>{_e(evaluation.outcome.value)}</strong>; evaluator "
                f"{_e(evaluation.evaluator.display_name or evaluation.evaluator.id)}; "
                f"evaluated {_e(evaluation.evaluated_at)}.</p>"
            )
            parts.append(
                "<p>Evidence IDs: "
                + ", ".join(f"<code>{_e(item)}</code>" for item in evaluation.evidence_ids)
                + "</p>"
            )
            findings = "".join(f"<li>{_e(item)}</li>" for item in evaluation.findings)
            findings_section = f"<ul>{findings}</ul>" if findings else "<p>No findings.</p>"
            parts.append(
                f"<h3>Findings</h3>{findings_section}<p>Summary: {_e(evaluation.summary)}</p>"
            )
    if projection.result_history:
        result_items = "".join(
            "<li>"
            f"<code>{_e(item.result_id)}</code>; Baseline <code>"
            f"{_e(item.result_baseline_id)}</code>; lifecycle revision "
            f"{_e(item.lifecycle_revision)}; supersedes "
            f"{_e(item.supersedes_result_id or 'none')}.</li>"
            for item in projection.result_history
        )
        parts.append(f"<details><summary>Result history</summary><ol>{result_items}</ol></details>")
    if projection.evaluation_history:
        evaluation_items = "".join(
            "<li>"
            f"<code>{_e(item.evaluation_id)}</code>; result <code>{_e(item.result_id)}</code>; "
            f"{_e(item.outcome.value)}; supersedes "
            f"{_e(item.supersedes_evaluation_id or 'none')}.</li>"
            for item in projection.evaluation_history
        )
        parts.append(
            f"<details><summary>Evaluation history</summary><ol>{evaluation_items}</ol></details>"
        )
    if projection.current_technical_decision is not None:
        decision = projection.current_technical_decision
        parts.append(
            f"<p>Human technical decision <code>{_e(decision.decision_id)}</code>: "
            f"<strong>{_e(decision.decision.value)}</strong> for gate "
            f"<code>{_e(decision.gate_id)}</code> revision {_e(decision.gate_revision)}; "
            f"lifecycle revision {_e(decision.lifecycle_revision)}, governance revision "
            f"{_e(decision.governance_revision)}.</p>"
        )
    if projection.accepted_result is not None:
        accepted = projection.accepted_result
        parts.append(
            f"<p>Accepted result <code>{_e(accepted.result_id)}</code>; exact Baseline "
            f"<code>{_e(accepted.result_baseline_id)}</code>; commit "
            f"<code>{_e(accepted.commit)}</code>; evaluation "
            f"<code>{_e(accepted.manual_evaluation_id)}</code>; Human decision "
            f"<code>{_e(accepted.human_approval_decision_id)}</code>; execution "
            f"<code>{_e(accepted.accepted_execution_id)}</code> at {_e(accepted.accepted_at)}.</p>"
        )
    memory = projection.development_memory
    if memory is not None:
        parts.append(
            f"<details><summary>Development memory projection</summary>"
            f"<p>Source Baseline <code>{_e(memory.source_baseline.id)}</code>; "
            f"{len(memory.result_history)} result records, "
            f"{len(memory.evaluation_history)} evaluations, {len(memory.evidence)} Evidence items, "
            f"{len(memory.accepted_results)} accepted result executions.</p></details>"
        )

    basis = projection.action_basis
    if csrf_token is not None and basis is not None:
        root = _slice_url(detail.project.id, detail.slice_definition.value.id)
        base_fields = (
            ("expected_lifecycle_revision", basis.lifecycle_revision),
            ("expected_slice_definition_revision", basis.slice_definition_revision),
            ("expected_current_result_id", basis.current_result_id or ""),
            (
                "expected_current_evaluation_id",
                basis.current_manual_evaluation_id or "",
            ),
            (
                "expected_latest_gate_evaluation_record_id",
                basis.latest_gate_evaluation_record_id or "",
            ),
            (
                "expected_gate_refs",
                json.dumps([item.model_dump(mode="json") for item in basis.gate_refs]),
            ),
        )
        actions = set(projection.actions)
        if ManualEvaluationActionKind.ATTACH_RESULT in actions:
            controls = (
                '<label>Revision selector kind <select name="revision_kind">'
                '<option value="COMMIT_SHA">Exact commit SHA</option>'
                '<option value="BRANCH">Branch</option><option value="TAG">Tag</option>'
                "</select></label>"
                '<label>Commit or ref <input name="revision_value" required '
                'maxlength="128"></label>'
                '<label>Reason <textarea name="reason" required '
                'maxlength="2000"></textarea></label>'
            )
            parts.append(
                _manual_evaluation_form(
                    f"{root}/actions/attach-result",
                    "Attach verified result",
                    csrf_token,
                    base_fields,
                    controls,
                )
            )
        if ManualEvaluationActionKind.EVALUATE in actions:
            outcome_options = "".join(
                f'<option value="{_e(item.value)}">{_e(item.value)}</option>'
                for item in EvaluationOutcome
            )
            surface_options = "".join(
                f'<option value="{_e(item.value)}">{_e(item.value)}</option>'
                for item in ChangeSurfaceStatus
            )
            risk_options = "".join(
                f'<option value="{_e(item.value)}">{_e(item.value)}</option>' for item in RiskStatus
            )
            toolchain_options = "".join(
                f'<option value="{_e(item.value)}">{_e(item.value)}</option>'
                for item in ToolchainChangeStatus
            )
            controls = (
                f'<label>Outcome <select name="outcome" required>'
                f"{outcome_options}</select></label>"
                "<label>New Evidence claims, one per line "
                '<textarea name="evidence_claims" required></textarea></label>'
                "<label>Existing Evidence IDs, comma separated "
                '<input name="existing_evidence_ids"></label>'
                "<label>Quality checks, one key=STATUS per line "
                '<textarea name="quality_checks"></textarea></label>'
                f'<label>Change surface <select name="change_surface_status" required>'
                f"{surface_options}</select></label>"
                f'<label>Risk <select name="risk_status" required>{risk_options}</select></label>'
                f'<label>Toolchain <select name="toolchain_change_status" required>'
                f"{toolchain_options}</select></label>"
                '<label>Findings, one per line <textarea name="findings"></textarea></label>'
                '<label>Summary <textarea name="summary" required '
                'maxlength="4000"></textarea></label>'
            )
            parts.append(
                _manual_evaluation_form(
                    f"{root}/actions/evaluate",
                    "Record manual evaluation",
                    csrf_token,
                    base_fields,
                    controls,
                )
            )

        human_basis = detail.human_actions.basis
        approval = next(
            (
                item
                for item in detail.human_actions.current_approval_decisions
                if any(ref.gate_id == item.gate_id for ref in projection.technical_gate_refs)
            ),
            None,
        )
        if (
            human_basis is not None
            and projection.current_result is not None
            and projection.current_evaluation is not None
        ):
            for reference in projection.technical_gate_refs:
                expected = (
                    ""
                    if approval is None or approval.gate_id != reference.gate_id
                    else approval.decision_id
                )
                technical_fields = (
                    ("basis", human_basis.model_dump_json()),
                    ("expected_result_id", projection.current_result.result_id),
                    ("expected_manual_evaluation_id", projection.current_evaluation.evaluation_id),
                    ("gate_id", reference.gate_id),
                    ("gate_revision", reference.gate_revision),
                    ("expected_current_approval_decision_id", expected),
                )
                for kind, label in (
                    (ManualEvaluationActionKind.TECHNICAL_ACCEPT, "Technical accept"),
                    (ManualEvaluationActionKind.TECHNICAL_REJECT, "Technical reject"),
                ):
                    if kind in actions:
                        route = (
                            "technical-accept"
                            if kind is ManualEvaluationActionKind.TECHNICAL_ACCEPT
                            else "technical-reject"
                        )
                        parts.append(
                            _manual_evaluation_form(
                                f"{root}/actions/{route}",
                                f"{label} gate {reference.gate_id}",
                                csrf_token,
                                technical_fields,
                                '<label>Reason <textarea name="reason" required '
                                'maxlength="2000"></textarea></label>',
                            )
                        )
            for reference in projection.promotable_gate_refs:
                expected = (
                    ""
                    if approval is None or approval.gate_id != reference.gate_id
                    else approval.decision_id
                )
                parts.append(
                    _manual_evaluation_form(
                        f"{root}/actions/promote-accepted",
                        f"Promote accepted gate {reference.gate_id}",
                        csrf_token,
                        (
                            ("basis", human_basis.model_dump_json()),
                            ("expected_result_id", projection.current_result.result_id),
                            (
                                "expected_manual_evaluation_id",
                                projection.current_evaluation.evaluation_id,
                            ),
                            ("expected_current_approval_decision_id", expected),
                            ("gate_id", reference.gate_id),
                            ("gate_revision", reference.gate_revision),
                        ),
                        '<label>Reason <textarea name="reason" required '
                        'maxlength="2000"></textarea></label>',
                    )
                )
    parts.append("</section>")
    return "".join(parts)


def render_slice_detail(detail: SliceDetail, csrf_token: str | None = None) -> str:
    """Render one complete Slice projection without database access."""

    value = detail.slice_definition.value
    body = (
        f'<nav aria-label="Primary"><a href="/">All Projects</a> · '
        f'<a href="{_project_url(detail.project.id)}">Project board</a></nav>'
        f"<p>Project: {_e(detail.project.name)} (<code>{_e(detail.project.id)}</code>); "
        f"definition revision {_e(detail.project_definition_revision)}.</p>"
        f"<p>Slice ID: <code>{_e(value.id)}</code></p>"
        f"{_governance_status_section(detail)}{_definition_section(detail)}"
        f"{_lifecycle_section(detail)}"
        f"{_observation_section(detail)}{_human_action_section(detail, csrf_token)}"
        f"{_manual_evaluation_section(detail, csrf_token)}"
        f"{_execution_section(detail)}"
    )
    return _page(f"{value.title} — Slice detail", body)


def render_error_page(kind: str) -> str:
    """Render a non-partial, non-sensitive presentation-boundary failure."""

    messages = {
        "NOT_FOUND": "The requested Project or Slice does not exist.",
        "UNAVAILABLE": "Durable state is temporarily unavailable.",
        "INTEGRITY_ERROR": "Durable state failed integrity checks; no partial projection is shown.",
    }
    message = messages.get(kind, "The request could not be completed.")
    return _page(kind, f"<p>{_e(message)}</p>")


__all__ = [
    "render_error_page",
    "render_project_board",
    "render_project_index",
    "render_slice_detail",
]
