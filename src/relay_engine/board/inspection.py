"""Read-only situation and canonical-governance projections for the board."""

import sqlite3

from relay_engine.board.models import (
    CanonicalGovernanceInspection,
    CanonicalTargetInspection,
    EvaluationBasisStatus,
    FrontierCardinality,
    LiveObservationStatus,
    ProjectGateReference,
    ProjectSituationProjection,
    ProjectSliceHierarchy,
    ProjectSliceIdentity,
    PromotionAttemptInspection,
    PromotionIntentAuthorityStatus,
    SituationBlocker,
    SituationBlockerSource,
    SituationNextWorkState,
    SliceCard,
    StaleSituationState,
    StaleStateKind,
)
from relay_engine.domain.models import Project
from relay_engine.governance.models import GateReasonKind
from relay_engine.lifecycle.models import BlockageStatus, LifecyclePhase, LifecycleValidity
from relay_engine.persistence import (
    PersistenceError,
    RelayDatabase,
    load_canonical_promotion_reconciliations,
    load_repository_promotion_intent,
    load_repository_promotion_result,
)
from relay_engine.promotion.bindings import (
    canonical_ref_health,
    promotion_intent_authority_is_valid,
    resolve_canonical_policy_binding,
)
from relay_engine.promotion.controls import (
    SourceControlConformance,
    SourceControlObservationV1,
    evaluate_source_control_conformance,
)
from relay_engine.promotion.models import (
    CanonicalPromotionPolicyBindingResolution,
    CanonicalPromotionPolicyBindingState,
    CanonicalRefHealth,
    PromotionAuthorizability,
    PromotionEligibilityState,
    PromotionPropertyOutcome,
    PromotionResultOutcome,
    ReconciliationPreparationState,
)

_CANONICAL_TABLES = (
    "canonical_promotion_policy_bindings",
    "repository_promotion_intents",
    "repository_promotion_results",
    "repository_promotion_reconciliations",
)


def _slice_identity(card: SliceCard) -> ProjectSliceIdentity:
    return ProjectSliceIdentity(
        slice_id=card.slice_id,
        title=card.title,
        definition_revision=card.definition_revision,
    )


def project_project_situation(cards: tuple[SliceCard, ...]) -> ProjectSituationProjection:
    """Classify current Slice facts and derive leaf active frontiers by hierarchy."""

    identities = {card.slice_id: _slice_identity(card) for card in cards}
    cards_by_id = {card.slice_id: card for card in cards}
    children: dict[str, list[str]] = {card.slice_id: [] for card in cards}
    for card in cards:
        if card.parent_slice_id is not None and card.parent_slice_id in children:
            children[card.parent_slice_id].append(card.slice_id)

    done: list[ProjectSliceIdentity] = []
    active: list[ProjectSliceIdentity] = []
    not_started: list[ProjectSliceIdentity] = []
    superseded: list[ProjectSliceIdentity] = []
    cancelled: list[ProjectSliceIdentity] = []
    active_ids: set[str] = set()
    blockers: list[SituationBlocker] = []
    stale_states: list[StaleSituationState] = []
    current_gates: list[ProjectGateReference] = []

    for card in cards:
        identity = identities[card.slice_id]
        lifecycle = card.lifecycle
        if lifecycle is None:
            not_started.append(identity)
        elif lifecycle.phase is LifecyclePhase.ACCEPTED:
            done.append(identity)
        elif lifecycle.phase is LifecyclePhase.SUPERSEDED:
            superseded.append(identity)
        elif lifecycle.phase is LifecyclePhase.CANCELLED:
            cancelled.append(identity)
        else:
            active.append(identity)
            active_ids.add(card.slice_id)

        if lifecycle is not None:
            if lifecycle.validity is LifecycleValidity.STALE:
                stale_states.append(
                    StaleSituationState(slice=identity, kind=StaleStateKind.LIFECYCLE)
                )
            if (
                lifecycle.validity is LifecycleValidity.CURRENT
                and lifecycle.blockage.status is BlockageStatus.BLOCKED
            ):
                if not lifecycle.blockage.reasons:
                    blockers.append(
                        SituationBlocker(
                            slice=identity,
                            source=SituationBlockerSource.LIFECYCLE,
                            code=BlockageStatus.BLOCKED.value,
                            summary=("Lifecycle blockage is recorded without reason details."),
                        )
                    )
                blockers.extend(
                    SituationBlocker(
                        slice=identity,
                        source=SituationBlockerSource.LIFECYCLE,
                        code=reason.code,
                        summary=reason.summary,
                    )
                    for reason in lifecycle.blockage.reasons
                )

        if card.evaluation_basis_status is EvaluationBasisStatus.STALE_DURABLE_BASIS:
            stale_states.append(
                StaleSituationState(slice=identity, kind=StaleStateKind.GATE_EVALUATION)
            )

        for gate in card.outgoing_gates:
            current_gates.append(ProjectGateReference(slice=identity, gate=gate))
            if gate.evaluation_basis_status is EvaluationBasisStatus.MATCHING_DURABLE_BASIS:
                if gate.evaluation_light is not None and gate.evaluation_light.value == "RED":
                    blockers.append(
                        SituationBlocker(
                            slice=identity,
                            source=SituationBlockerSource.GATE_EVALUATION,
                            code=gate.evaluation_light.value,
                            summary="Current durable gate evaluation is RED.",
                        )
                    )
                blockers.extend(
                    SituationBlocker(
                        slice=identity,
                        source=SituationBlockerSource.GATE_EVALUATION,
                        code=reason.code.value,
                        summary=reason.subject or reason.code.value,
                    )
                    for reason in gate.evaluation_reasons
                    if reason.kind is GateReasonKind.BLOCKING
                )

    active_descendants: set[str] = set()
    for descendant_id in active_ids:
        card = cards_by_id[descendant_id]
        parent_id = card.parent_slice_id
        visited: set[str] = set()
        while parent_id is not None and parent_id in cards_by_id and parent_id not in visited:
            visited.add(parent_id)
            if parent_id in active_ids:
                active_descendants.add(parent_id)
            parent_id = cards_by_id[parent_id].parent_slice_id

    done.sort(key=lambda item: item.slice_id)
    active.sort(key=lambda item: item.slice_id)
    not_started.sort(key=lambda item: item.slice_id)
    superseded.sort(key=lambda item: item.slice_id)
    cancelled.sort(key=lambda item: item.slice_id)
    frontiers = tuple(
        identity for identity in active if identity.slice_id not in active_descendants
    )
    cardinality = (
        FrontierCardinality.NONE
        if len(frontiers) == 0
        else FrontierCardinality.ONE
        if len(frontiers) == 1
        else FrontierCardinality.MULTIPLE
    )
    frontier_ids = {identity.slice_id for identity in frontiers}
    current_gates.sort(
        key=lambda item: (item.slice.slice_id, item.gate.gate_id, item.gate.gate_revision)
    )
    blockers.sort(
        key=lambda item: (item.slice.slice_id, item.source.value, item.code, item.summary)
    )
    stale_states.sort(key=lambda item: (item.slice.slice_id, item.kind.value))
    next_work = tuple(item for item in current_gates if item.slice.slice_id in frontier_ids)

    hierarchy = tuple(
        ProjectSliceHierarchy(
            slice_id=card.slice_id,
            parent_slice_id=card.parent_slice_id,
            child_slice_ids=tuple(sorted(children[card.slice_id])),
            dependency_ids=card.dependency_ids,
            superseded_by_slice_id=(
                None if card.lifecycle is None else card.lifecycle.superseded_by_slice_id
            ),
        )
        for card in sorted(cards, key=lambda item: item.slice_id)
    )

    return ProjectSituationProjection(
        done_slices=tuple(done),
        active_slices=tuple(active),
        not_started_slices=tuple(not_started),
        superseded_slices=tuple(superseded),
        cancelled_slices=tuple(cancelled),
        leaf_active_frontiers=frontiers,
        frontier_cardinality=cardinality,
        blockers=tuple(blockers),
        stale_states=tuple(stale_states),
        current_outgoing_gates=tuple(current_gates),
        hierarchy=hierarchy,
        next_governed_work=next_work,
        next_work_state=(
            SituationNextWorkState.CURRENT_FRONTIER_GATES
            if next_work
            else SituationNextWorkState.NOT_DETERMINABLE
        ),
    )


def _canonical_refs(connection: sqlite3.Connection, project: Project) -> tuple[str, ...]:
    values: set[str] = set()
    for table in _CANONICAL_TABLES:
        rows = connection.execute(
            f"SELECT DISTINCT canonical_ref FROM {table} "
            "WHERE project_id = ? AND repository_id = ?",
            (project.id, project.primary_repository.id),
        ).fetchall()
        values.update(str(row["canonical_ref"]) for row in rows)
    return tuple(sorted(values))


def _promotion_ids(
    connection: sqlite3.Connection, project: Project, canonical_ref: str
) -> tuple[str, ...]:
    values: set[str] = set()
    for table in (
        "repository_promotion_intents",
        "repository_promotion_results",
        "repository_promotion_reconciliations",
    ):
        rows = connection.execute(
            f"SELECT DISTINCT promotion_id FROM {table} "
            "WHERE project_id = ? AND repository_id = ? AND canonical_ref = ?",
            (project.id, project.primary_repository.id, canonical_ref),
        ).fetchall()
        values.update(str(row["promotion_id"]) for row in rows)
    return tuple(sorted(values))


def _promotion_attempts(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    project: Project,
    canonical_ref: str,
) -> tuple[tuple[PromotionAttemptInspection, ...], bool]:
    attempts: list[PromotionAttemptInspection] = []
    parsing_failed = False
    for promotion_id in _promotion_ids(connection, project, canonical_ref):
        try:
            intent = load_repository_promotion_intent(database, promotion_id)
            result = load_repository_promotion_result(database, promotion_id)
            reconciliations = load_canonical_promotion_reconciliations(database, promotion_id)
        except PersistenceError:
            parsing_failed = True
            attempts.append(
                PromotionAttemptInspection(
                    promotion_id=promotion_id,
                    intent=None,
                    original_authority_status=PromotionIntentAuthorityStatus.UNKNOWN,
                    result=None,
                    reconciliations=(),
                )
            )
            continue

        if intent is None:
            authority_status = (
                PromotionIntentAuthorityStatus.UNKNOWN
                if result is not None or reconciliations
                else PromotionIntentAuthorityStatus.NOT_APPLICABLE
            )
        else:
            authority_status = (
                PromotionIntentAuthorityStatus.VERIFIED
                if promotion_intent_authority_is_valid(database, intent)
                else PromotionIntentAuthorityStatus.UNKNOWN
            )
        attempts.append(
            PromotionAttemptInspection(
                promotion_id=promotion_id,
                intent=intent,
                original_authority_status=authority_status,
                result=result,
                reconciliations=reconciliations,
            )
        )
    return tuple(attempts), parsing_failed


def project_canonical_governance(
    database: RelayDatabase,
    connection: sqlite3.Connection,
    project: Project,
    *,
    live_source_control_observations: tuple[SourceControlObservationV1, ...] = (),
) -> CanonicalGovernanceInspection:
    """Project exact stored promotion state and explicitly supplied live observations."""

    targets: list[CanonicalTargetInspection] = []
    for canonical_ref in _canonical_refs(connection, project):
        binding = resolve_canonical_policy_binding(
            database,
            project_id=project.id,
            repository_id=project.primary_repository.id,
            canonical_ref=canonical_ref,
        )
        health = canonical_ref_health(
            database,
            project_id=project.id,
            repository_id=project.primary_repository.id,
            canonical_ref=canonical_ref,
        )
        attempts, attempt_parse_failed = _promotion_attempts(
            database, connection, project, canonical_ref
        )
        if attempt_parse_failed:
            health = CanonicalRefHealth.UNKNOWN

        matching_observations = tuple(
            observation
            for observation in live_source_control_observations
            if observation.canonical_ref == canonical_ref
        )
        live_observation: SourceControlObservationV1 | None = None
        observation_status = LiveObservationStatus.UNAVAILABLE
        conformance = SourceControlConformance.UNKNOWN
        if len(matching_observations) > 1:
            observation_status = LiveObservationStatus.AMBIGUOUS
        elif len(matching_observations) == 1:
            live_observation = matching_observations[0]
            if (
                live_observation.project_id != project.id
                or live_observation.repository != project.primary_repository
            ):
                observation_status = LiveObservationStatus.IDENTITY_MISMATCH
            else:
                observation_status = LiveObservationStatus.SUPPLIED
                current_binding = binding.current
                if (
                    binding.resolution is CanonicalPromotionPolicyBindingResolution.MANAGED
                    and current_binding is not None
                    and current_binding.state is CanonicalPromotionPolicyBindingState.MANAGED
                    and current_binding.policy is not None
                ):
                    conformance = evaluate_source_control_conformance(
                        live_observation,
                        policy=current_binding.policy,
                    )

        unresolved_visible_result = any(
            attempt.result is not None
            and attempt.result.outcome is PromotionResultOutcome.VISIBLE_UNVERIFIED
            and not attempt.reconciliations
            for attempt in attempts
        )
        reconciliation_state = (
            ReconciliationPreparationState.UNKNOWN
            if unresolved_visible_result and health is not CanonicalRefHealth.HEALTHY
            else None
        )
        targets.append(
            CanonicalTargetInspection(
                repository=project.primary_repository,
                canonical_ref=canonical_ref,
                binding_resolution=binding.resolution,
                current_binding=binding.current,
                health=health,
                current_authorizability=PromotionAuthorizability.UNKNOWN,
                current_eligibility=PromotionEligibilityState.UNKNOWN,
                reconciliation_preparation_state=reconciliation_state,
                live_observation_status=observation_status,
                live_source_control_observation=live_observation,
                live_source_control_conformance=PromotionPropertyOutcome(conformance.value),
                promotion_attempts=attempts,
            )
        )

    target_established = any(
        item.current_binding is not None
        and item.binding_resolution
        in {
            CanonicalPromotionPolicyBindingResolution.UNMANAGED,
            CanonicalPromotionPolicyBindingResolution.MANAGED,
        }
        for item in targets
    )
    return CanonicalGovernanceInspection(
        durable_target_established=target_established,
        targets=tuple(targets),
    )


__all__ = ["project_canonical_governance", "project_project_situation"]
